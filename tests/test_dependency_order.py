"""Test recipe delivery, not the client's semantic evaluation of dependencies."""
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
    "submit-epic": {"description": "Synthetic dependency example"},
    "submit-feature": {"description": "Synthetic dependency example"},
    "create-epic-features": {"epic_id": "EPIC-123"},
    "link-feature-to-epic": {"feature_id": "FEAT-123", "epic_id": "EPIC-123"},
    "design-feature": {"feature_id": "FEAT-123"},
    "deep-dive": {"file_path": "/external/example.md"},
    "refine-feature": {"feature_id": "FEAT-123"},
    "start-feature": {"feature_id": "FEAT-123", "workflow_mode": "autonomous"},
    "continue-implementation": {"feature_id": "FEAT-123", "workflow_mode": "autonomous"},
    "code-review": {"feature_id": "FEAT-123", "phase_number": 3},
    "accept-phase": {"feature_id": "FEAT-123", "phase_number": 3, "workflow_mode": "autonomous"},
    "complete-feature": {"feature_id": "FEAT-123", "workflow_mode": "autonomous"},
}


class DependencyOrderTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool):
        return await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": TOOLS[tool]},
        ))

    async def test_every_lifecycle_tool_delivers_policy_in_both_payloads(self):
        policy = (main.PROMPTS_DIR / "dependency-order.md").read_text()
        for tool in TOOLS:
            with self.subTest(tool=tool):
                response = await self.call(tool)
                self.assertIsNone(response.error)
                self.assertFalse(response.result["isError"])
                payload = response.result["structuredContent"]
                self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
                self.assertEqual("pending_execution", payload["status"])
                self.assertEqual("client_llm", payload["execution_owner"])
                self.assertEqual(1, payload["instructions"].count(policy))

    async def test_unavailable_policy_fails_closed_for_every_lifecycle_tool(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            policy = root / "dependency-order.md"
            with patch.object(main, "PROMPTS_DIR", root):
                for contents in (None, "", " \n\t"):
                    if contents is None:
                        policy.unlink()
                    else:
                        policy.write_text(contents)
                    for tool in TOOLS:
                        with self.subTest(tool=tool, contents=contents):
                            response = await self.call(tool)
                            self.assertIsNone(response.error)
                            self.assertTrue(response.result["isError"])
                            payload = response.result["structuredContent"]
                            self.assertEqual("error", payload["status"])
                            self.assertFalse(payload["tool_call_success"])
                            self.assertIn("dependency-order.md", payload["message"])
                            self.assertNotIn("instructions", payload)

    async def test_updated_policy_reaches_all_tools_without_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            with patch.object(main, "PROMPTS_DIR", root):
                for version in ("DEPENDENCIES_REVISION_ONE", "DEPENDENCIES_REVISION_TWO"):
                    (root / "dependency-order.md").write_text(version)
                    for tool in TOOLS:
                        with self.subTest(tool=tool, version=version):
                            response = await self.call(tool)
                            self.assertFalse(response.result["isError"])
                            text = response.result["structuredContent"]["instructions"]
                            self.assertEqual(1, text.count(version))
                            if version.endswith("TWO"):
                                self.assertNotIn("DEPENDENCIES_REVISION_ONE", text)


if __name__ == "__main__":
    unittest.main()
