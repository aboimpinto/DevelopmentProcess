"""JSON-RPC contracts must hand a procedure to the client, never a work result."""
import json
import unittest

from client_execution import CLIENT_LOOP
from main import JsonRpcRequest, json_rpc_handler


class ClientExecutionContractTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool, mode=None):
        arguments = {"feature_id": "FEAT-901", "feature_path": "/synthetic/feature", "phase_number": 17}
        if mode is not None:
            arguments["workflow_mode"] = mode
        return await json_rpc_handler(JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": arguments},
        ))

    async def test_start_and_continue_have_identical_loop_and_completion_boundary(self):
        for mode in (None, "autonomous", "single_phase"):
            records = []
            for tool in ("start-feature", "continue-implementation"):
                response = await self.call(tool, mode)
                self.assertIsNone(response.error)
                payload = response.result["structuredContent"]
                records.append(payload)
                self.assertIn(CLIENT_LOOP, payload["instructions"])
                self.assertEqual(payload["instructions"].count(CLIENT_LOOP), 1)
                self.assertEqual(payload["workflow_mode"], mode or "autonomous")
                self.assertEqual(payload["completion_boundary"],
                                 "selected_phase_accepted" if mode == "single_phase" else "feature_completed")
            self.assertEqual(records[0]["completion_boundary"], records[1]["completion_boundary"])
            self.assertIn("initialize_feature_then_resume", records[0]["client_directive"])
            self.assertIn("resume_recorded_task", records[1]["client_directive"])

    async def test_transport_success_is_not_work_completion_in_either_representation(self):
        for tool in ("start-feature", "continue-implementation", "accept-phase"):
            response = await self.call(tool)
            text = response.result["content"][0]["text"]
            payload = response.result["structuredContent"]
            self.assertEqual(json.loads(text), payload)
            self.assertEqual(payload["status"], "pending_execution")
            self.assertEqual(payload["action"], "execute_procedure")
            self.assertEqual(payload["execution_owner"], "client_llm")
            self.assertEqual(payload["next_action"], "execute_returned_procedure")
            self.assertFalse(payload["retry_same_tool"])
            self.assertIn("not a task result or a background job", payload["client_directive"])
            self.assertLess(text.index('"client_directive"'), text.index('"instructions"'))
            self.assertIn("not executed, tested or completed the feature", payload["client_directive"])

    async def test_incomplete_task_and_failed_gate_require_continued_execution(self):
        for tool in ("start-feature", "continue-implementation", "accept-phase"):
            payload = (await self.call(tool)).result["structuredContent"]
            text = " ".join(payload["instructions"].split())
            self.assertIn("block acceptance, not continued execution", text)
            self.assertIn("partial commit, progress report, passing subset or IN_PROGRESS task is not a stopping point", text)
            self.assertIn("obstacle, attempted repairs, preserved evidence", text)
            self.assertIn("cancellation or explicit user pause", text)
            self.assertNotIn("Stop early only for an unresolved in-scope task/gate", text)
            self.assertNotIn("`autonomous` may continue", text)
            self.assertNotIn("interactive or not provided", text)

    async def test_phase_acceptance_handoff_preserves_single_phase_boundary(self):
        for mode in ("autonomous", "single_phase"):
            payload = (await self.call("accept-phase", mode)).result["structuredContent"]
            self.assertIn("validate_phase_then_continue", payload["client_directive"])
            if mode == "single_phase":
                self.assertIn("do not activate another phase or complete the feature in this action", payload["client_directive"])
            else:
                self.assertIn("execute all remaining phases and feature completion before returning", payload["client_directive"])
            self.assertNotIn("Phase {N+1} will NOT start automatically", payload["instructions"])

    async def test_invalid_mode_remains_error_not_executable_recipe(self):
        for tool in ("start-feature", "continue-implementation", "accept-phase"):
            response = await self.call(tool, "interactive")
            self.assertIsNotNone(response.error)
            self.assertIsNone(response.result)

    async def test_listing_describes_client_execution_not_server_side_work(self):
        response = await json_rpc_handler(JsonRpcRequest(jsonrpc="2.0", id=2, method="tools/list"))
        for tool in response.result["tools"]:
            if tool['name'] in ("start-feature", "continue-implementation", "accept-phase"):
                self.assertTrue(tool['description'].startswith("Returns operations for the calling coding agent to execute locally. "))


if __name__ == "__main__":
    unittest.main()
