import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "DevCycleManager"))

import main


class FeatureReadinessTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool):
        return await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": {
                "feature_id": "FEAT-123", "feature_path": "/external/feature",
                **({"workflow_mode": "autonomous"} if tool == "start-feature" else {}),
            }},
        ))

    async def test_both_tools_deliver_same_gate_and_preserve_client_contract(self):
        gate = (main.PROMPTS_DIR / "feature-readiness.md").read_text()
        for tool in ("refine-feature", "start-feature"):
            with self.subTest(tool=tool):
                response = await self.call(tool)
                self.assertIsNone(response.error)
                self.assertFalse(response.result["isError"])
                payload = response.result["structuredContent"]
                self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
                self.assertEqual("pending_execution", payload["status"])
                self.assertEqual("client_llm", payload["execution_owner"])
                self.assertFalse(payload["retry_same_tool"])
                self.assertEqual(1, payload["instructions"].count(gate))
                self.assertIn("FEAT-123", payload["instructions"])
                self.assertIn("/external/feature", payload["instructions"])
                self.assertNotIn("{{feature_id}}", payload["instructions"])

    async def test_gate_changes_reach_both_tools_without_server_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(main.PROMPTS_DIR, root, dirs_exist_ok=True)
            with patch.object(main, "PROMPTS_DIR", root):
                for revision in ("GATE_FIRST_REVISION", "GATE_SECOND_REVISION"):
                    (root / "feature-readiness.md").write_text(revision)
                    for tool in ("refine-feature", "start-feature"):
                        response = await self.call(tool)
                        self.assertIsNone(response.error)
                        self.assertFalse(response.result["isError"])
                        payload = response.result["structuredContent"]
                        self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
                        text = payload["instructions"]
                        self.assertEqual(1, text.count(revision))
                        if revision == "GATE_SECOND_REVISION":
                            self.assertNotIn("GATE_FIRST_REVISION", text)
                        self.assertEqual("devcycle-phase-quality/v2", payload["quality_gate_policy_version"])
                        self.assertEqual("acceptance-responsibility/v1", payload["acceptance_policy_version"])

    async def test_missing_shared_gate_cannot_silently_bypass_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "dependency-order.md").write_text("DEPENDENCY_POLICY")
            for name in ("refine-feature.md", "start-feature.md"):
                (root / name).write_text((main.PROMPTS_DIR / name).read_text())
            with patch.object(main, "PROMPTS_DIR", root):
                for tool in ("refine-feature", "start-feature"):
                    response = await self.call(tool)
                    self.assertTrue(response.result["isError"])
                    payload = response.result["structuredContent"]
                    self.assertEqual("error", payload["status"])
                    self.assertIn("feature-readiness.md", payload["message"])
                    self.assertNotIn("instructions", payload)
