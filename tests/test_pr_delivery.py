"""Verify recipe delivery and scoped-review API; not client decision execution."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "DevCycleManager"))
import main


TOOLS = {
    "deep-dive": {"file_path": "/external/spec.md"},
    "refine-feature": {"feature_id": "FEAT-123"},
    "start-feature": {"feature_id": "FEAT-123"},
    "continue-implementation": {"feature_id": "FEAT-123"},
    "code-review": {"feature_id": "FEAT-123", "phase_number": 42},
    "accept-phase": {"feature_id": "FEAT-123", "phase_number": 42},
    "complete-feature": {"feature_id": "FEAT-123"},
}


class PRDeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool, arguments=None, field="arguments"):
        response = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, field: arguments if arguments is not None else TOOLS[tool]},
        ))
        self.assertIsNone(response.error)
        payload = response.result["structuredContent"]
        self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
        return response.result, payload

    async def test_policy_reaches_each_boundary_without_changing_execution_owner(self):
        policy = (main.PROMPTS_DIR / "pr-delivery.md").read_text()
        for tool in TOOLS:
            with self.subTest(tool=tool):
                result, payload = await self.call(tool)
                self.assertFalse(result["isError"])
                self.assertEqual("pending_execution", payload["status"])
                self.assertEqual("client_llm", payload["execution_owner"])
                self.assertFalse(payload["retry_same_tool"])
                self.assertEqual(1, payload["instructions"].count(policy))

    async def test_delivery_coexists_with_lifecycle_modes_and_acceptance_policies(self):
        for mode in ("autonomous", "single_phase"):
            for tool in ("start-feature", "continue-implementation", "accept-phase"):
                with self.subTest(mode=mode, tool=tool):
                    result, payload = await self.call(tool, {
                        **TOOLS[tool], "workflow_mode": mode,
                    })
                    self.assertFalse(result["isError"])
                    self.assertEqual(mode, payload["workflow_mode"])
                    self.assertEqual(
                        "feature_completed" if mode == "autonomous" else "selected_phase_accepted",
                        payload["completion_boundary"],
                    )
                    self.assertEqual("acceptance-responsibility/v1", payload["acceptance_policy_version"])
                    self.assertEqual("devcycle-phase-quality/v2", payload["quality_gate_policy_version"])
                    for policy in ("pr-delivery.md", "github-sync.md"):
                        self.assertEqual(1, payload["instructions"].count(
                            (main.PROMPTS_DIR / policy).read_text()
                        ))
                    self.assertIn("satisfy the project's PR boundary", payload["client_directive"])
                    self.assertIn("dependency-ready task", payload["client_directive"])

    async def test_missing_or_empty_policy_blocks_affected_recipes_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            policy = root / "pr-delivery.md"
            with patch.object(main, "PROMPTS_DIR", root):
                for contents in (None, "", " \n\t"):
                    if contents is None:
                        policy.unlink()
                    else:
                        policy.write_text(contents)
                    for tool in TOOLS:
                        with self.subTest(tool=tool, contents=contents):
                            result, payload = await self.call(tool)
                            self.assertTrue(result["isError"])
                            self.assertEqual("error", payload["status"])
                            self.assertFalse(payload["tool_call_success"])
                            self.assertIn("pr-delivery.md", payload["message"])
                            self.assertNotIn("instructions", payload)
                    result, _ = await self.call("submit-feature", {"description": "Synthetic"})
                    self.assertFalse(result["isError"])

    async def test_policy_updates_are_loaded_without_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            with patch.object(main, "PROMPTS_DIR", root):
                for revision in ("DELIVERY_FIRST", "DELIVERY_SECOND"):
                    (root / "pr-delivery.md").write_text(revision)
                    for tool in TOOLS:
                        with self.subTest(tool=tool, revision=revision):
                            result, payload = await self.call(tool)
                            self.assertFalse(result["isError"])
                            self.assertEqual(1, payload["instructions"].count(revision))
                            if revision == "DELIVERY_SECOND":
                                self.assertNotIn("DELIVERY_FIRST", payload["instructions"])

    async def test_scoped_review_arguments_and_output_do_not_claim_phase_approval(self):
        for field in ("arguments", "input"):
            with self.subTest(field=field):
                result, payload = await self.call("code-review", {
                    "feature_id": "FEAT-123", "phase_number": 42,
                    "feature_path": "/external/feature", "delivery_unit_id": "PRU-02",
                }, field=field)
                self.assertFalse(result["isError"])
                self.assertEqual({"kind": "delivery_unit", "delivery_unit_id": "PRU-02"}, payload["review_scope"])
                self.assertIn("**Delivery Unit**: PRU-02", payload["instructions"])
                self.assertIn("**Phase Number**: 42", payload["instructions"])
                self.assertIn("/external/feature", payload["instructions"])
                self.assertNotIn("{{delivery_unit_id}}", payload["instructions"])
                self.assertIn("delivery-units/PRU-02/", payload["outputs"][0])
                self.assertNotIn("Phase checkpoint updated with review results", payload["outputs"])

    async def test_omitted_unit_preserves_full_phase_review(self):
        result, payload = await self.call("code-review")
        self.assertFalse(result["isError"])
        self.assertEqual({"kind": "phase", "delivery_unit_id": None}, payload["review_scope"])
        self.assertIn("**Delivery Unit**: N/A - full phase review", payload["instructions"])
        self.assertIn("code-reviews/phase-{N}/", payload["outputs"][0])
        self.assertIn("Phase checkpoint updated with review results", payload["outputs"])

    async def test_invalid_unit_never_returns_executable_recipe(self):
        for value in ("", "../escape", "x/y", "x y", "x\n", "x" * 65, 5, True, [], {}):
            with self.subTest(value=value):
                result, payload = await self.call("code-review", {
                    **TOOLS["code-review"], "delivery_unit_id": value,
                })
                self.assertTrue(result["isError"])
                self.assertEqual("error", payload["status"])
                self.assertIn("delivery_unit_id", payload["message"])
                self.assertNotIn("instructions", payload)

    async def test_discovery_advertises_optional_scope_without_changing_required_arguments(self):
        response = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/list", params={},
        ))
        self.assertIsNone(response.error)
        tool = next(t for t in response.result["tools"] if t["name"] == "code-review")
        schema = tool["inputSchema"]
        self.assertEqual({"feature_id", "phase_number"}, set(schema["required"]))
        self.assertEqual("string", schema["properties"]["delivery_unit_id"]["type"])
        self.assertIn("pattern", schema["properties"]["delivery_unit_id"])


if __name__ == "__main__":
    unittest.main()
