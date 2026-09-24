import unittest
from main import JsonRpcRequest, json_rpc_handler, run_deep_dive
from deep_dive_host import HOST_STAGES, HOST_CONTRACT


class HostedDeepDiveTests(unittest.IsolatedAsyncioTestCase):
    async def test_discovery_and_standard_arguments_select_each_stage(self):
        catalog = await json_rpc_handler(JsonRpcRequest(jsonrpc="2.0", id=1, method="tools/list", params={}))
        tool = next(t for t in catalog.result["tools"] if t["name"] == "deep-dive")
        self.assertEqual(tool["inputSchema"]["properties"]["stage"]["enum"], list(HOST_STAGES))
        for stage in HOST_STAGES:
            with self.subTest(stage=stage):
                response = await json_rpc_handler(JsonRpcRequest(jsonrpc="2.0", id=2, method="tools/call", params={
                    "name": "deep-dive", "arguments": {"file_path": "/memory/target.md", "response_mode": "host_stage", "stage": stage}}))
                self.assertIsNone(response.error)
                recipe = response.result["structuredContent"]
                self.assertEqual(recipe["status"], "pending_execution")
                self.assertEqual(recipe["action"], "execute_procedure")
                self.assertEqual(recipe["execution_owner"], "client_llm")
                self.assertFalse(recipe["retry_same_tool"])
                self.assertEqual(recipe["deep_dive_host_contract"]["version"], HOST_CONTRACT)
                self.assertEqual(recipe["deep_dive_host_contract"]["stage"], stage)
                self.assertEqual(recipe["deep_dive_host_contract"]["mutation_scope"], [])
                expected = "target_edits_json" if stage == "apply_answers" else "clarification_text" if stage == "clarify" else "questions_json"
                self.assertEqual(recipe["deep_dive_host_contract"]["output"], expected)
                instructions = recipe["instructions"]
                self.assertIn("Only saved answers authorize product decisions", instructions)
                self.assertEqual(instructions.count("Contract: devcycle-deep-dive-host/v1"), 1)
                if stage in ("opening", "follow_up", "apply_answers"):
                    self.assertEqual(instructions.count('"$schema"'), 1)
                    if stage != "apply_answers":
                        self.assertNotIn("## Apply saved answers", instructions)
                else:
                    self.assertNotIn('"$schema"', instructions)

    async def test_invalid_host_requests_do_not_fall_back_to_interactive_execution(self):
        for fields in ({"stage": "unknown"}, {"stage": None}, {"stage": "opening", "file_path": " "}):
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    await run_deep_dive(**{"file_path": "/memory/target.md", "response_mode": "host_stage", **fields})
        with self.assertRaises(ValueError):
            await run_deep_dive("/memory/target.md", response_mode="unknown")

    async def test_legacy_call_retains_interactive_recipe(self):
        result = await run_deep_dive("/memory/target.md")
        self.assertEqual(result["status"], "pending_execution")
        self.assertNotIn("deep_dive_host_contract", result)
        self.assertIn("/memory/target.md", result["instructions"])

    async def test_legacy_input_and_standard_argument_precedence(self):
        legacy = {"file_path": "/memory/target.md", "response_mode": "host_stage", "stage": "clarify"}
        for params, stage in (({"input": legacy}, "clarify"),
                              ({"input": legacy, "arguments": {**legacy, "stage": "opening"}}, "opening")):
            response = await json_rpc_handler(JsonRpcRequest(jsonrpc="2.0", id=3, method="tools/call", params={"name": "deep-dive", **params}))
            self.assertIsNone(response.error)
            self.assertEqual(response.result["structuredContent"]["deep_dive_host_contract"]["stage"], stage)


if __name__ == "__main__":
    unittest.main()
