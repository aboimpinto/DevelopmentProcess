"""Verify delivered planning contracts; not generated client document quality."""
import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main


class SpecificationLevelTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool, **arguments):
        return await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": {
                "feature_id": "FEAT-901", "epic_id": "EPIC-901",
                "file_path": "/synthetic/EpicDescription.md",
                "feature_path": "/synthetic/feature", "phase_number": 2,
                "description": "Synthetic document processing", **arguments,
            }},
        ))

    def payload(self, response):
        self.assertIsNone(response.error)
        self.assertFalse(response.result["isError"])
        payload = response.result["structuredContent"]
        self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
        return payload

    async def test_all_authoring_and_update_boundaries_deliver_one_canonical_policy(self):
        policy = (main.PROMPTS_DIR / "specification-level-policy.md").read_text()
        expected_tools = {
            "submit-epic", "submit-feature", "create-epic-features",
            "link-feature-to-epic", "design-feature", "deep-dive", "refine-feature",
            "start-feature", "continue-implementation", "code-review",
            "accept-phase", "complete-feature", "sync-epic", "sync-feature",
            "refresh-delivery",
        }
        self.assertEqual(main.SPECIFICATION_POLICY_TOOLS, expected_tools)
        for tool in sorted(expected_tools):
            with self.subTest(tool=tool):
                payload = self.payload(await self.call(tool))
                self.assertEqual(payload["status"], "pending_execution")
                self.assertEqual(payload["execution_owner"], "client_llm")
                self.assertEqual(payload["specification_level_policy_version"],
                                 "devcycle-specification-levels/v1")
                self.assertEqual(payload["instructions"].count(policy), 1)

    async def test_interview_modes_preserve_their_existing_mutation_scope(self):
        for mode in ("adaptive_interview", "question_manifest"):
            for target in ("EpicDescription.md", "FeatureDescription.md"):
                with self.subTest(mode=mode, target=target):
                    path = "/synthetic/" + target
                    payload = self.payload(await self.call(
                        "deep-dive", file_path=path, response_mode=mode))
                    self.assertEqual(payload["deep_dive_scope"]["mutation_scope"],
                                     [path] if mode == "adaptive_interview" else [])
                    text = " ".join(payload["instructions"].split())
                    self.assertIn("An EPIC may complete its interview", text)
                    self.assertIn("For a FEAT or phase", text)
                    self.assertNotIn("Deep-Dive must resolve every in-scope product", text)
                    self.assertIn("Only update", text)

    async def test_host_stages_receive_guidance_without_new_authority_or_schema(self):
        for stage in main.HOST_STAGES:
            with self.subTest(stage=stage):
                original = main.hosted_deep_dive_recipe(
                    main.PROMPTS_DIR, "/synthetic/EpicDescription.md", stage)
                payload = self.payload(await self.call(
                    "deep-dive", response_mode="host_stage", stage=stage))
                self.assertEqual(payload["deep_dive_host_contract"],
                                 original["deep_dive_host_contract"])
                self.assertEqual(payload["deep_dive_host_contract"]["mutation_scope"], [])
                self.assertTrue(payload["instructions"].startswith(original["instructions"]))
                self.assertIn("specification_level_policy_version", payload)
                self.assertNotIn("acceptance_policy_version", payload)
                self.assertNotIn("### 5.3 Reconcile", payload["instructions"])

    async def test_missing_empty_or_incompatible_policy_never_serves_partial_recipe(self):
        for content in (None, "", "Policy version: obsolete/v0"):
            with self.subTest(content=content), TemporaryDirectory() as directory:
                prompts = Path(directory) / "Prompts"
                shutil.copytree(main.PROMPTS_DIR, prompts)
                policy = prompts / "specification-level-policy.md"
                if content is None:
                    policy.unlink()
                else:
                    policy.write_text(content)
                with patch.object(main, "PROMPTS_DIR", prompts):
                    for tool, arguments in (
                        ("submit-epic", {}), ("sync-epic", {}),
                        ("deep-dive", {"response_mode": "host_stage", "stage": "opening"}),
                    ):
                        response = await self.call(tool, **arguments)
                        self.assertTrue(response.error or response.result.get("isError"))
                        if response.result:
                            self.assertNotIn("instructions", response.result.get("structuredContent", {}))

    async def test_epic_submission_marks_uncreated_features_as_proposals(self):
        payload = self.payload(await self.call("submit-epic"))
        text = payload["instructions"]
        self.assertIn("| {Suggested feature 1} | PROPOSED |", text)
        self.assertNotIn("| {Suggested feature 1} | SUBMITTED |", text)
        self.assertIn("## Design Work for Feature Refinement", text)

    async def test_feature_creation_and_refinement_retain_parent_decisions(self):
        creation = " ".join(self.payload(await self.call("create-epic-features"))["instructions"].split())
        self.assertIn("stable parent criterion IDs", creation)
        self.assertIn("named design work assigned to this feature", creation)
        refinement = " ".join(self.payload(await self.call("refine-feature"))["instructions"].split())
        self.assertIn("Resolve design work assigned to this feature", refinement)
        self.assertIn("do not silently promote proposals to constraints", refinement)
        self.assertIn("do not delete, relocate or automatically simplify", refinement)
        self.assertIn("EPIC acceptance requires its complete workflow E2E evidence", refinement)

    async def test_initialize_reports_new_release(self):
        response = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="initialize", params={}))
        self.assertEqual(response.result["serverInfo"]["version"], "0.3.1-remote")


if __name__ == "__main__":
    unittest.main()
