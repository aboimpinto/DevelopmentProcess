"""Merged recipe boundaries: policy delivery, not certification of client work."""
import json
import unittest

from main import JsonRpcRequest, json_rpc_handler


class ConsolidatedContractTests(unittest.IsolatedAsyncioTestCase):
    async def recipe(self, tool, **arguments):
        response = await json_rpc_handler(JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": {
                "feature_id": "FEAT-MERGE", "file_path": "/memory/target.md",
                **arguments,
            }},
        ))
        self.assertIsNone(response.error)
        self.assertFalse(response.result["isError"])
        payload = response.result["structuredContent"]
        self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
        return payload

    async def test_epic_reconciliation_retains_single_target_and_manifest_boundaries(self):
        for mode in ("adaptive_interview", "question_manifest"):
            payload = await self.recipe("deep-dive", response_mode=mode)
            self.assertEqual(payload["deep_dive_scope"]["mutation_scope"],
                             [] if mode == "question_manifest" else ["/memory/target.md"])
            text = " ".join(payload["instructions"].split())
            self.assertIn("target itself is an epic", text)
            self.assertIn("question_manifest mode, return questions without any mutation", text)
            self.assertIn("never update that linked file", text)
            self.assertIn("do not create or modify a separate history file", text)
            self.assertIn("Interview completion never certifies feature or epic delivery", text)
            self.assertIn("## Required Dependency Order", text)

    async def test_hosted_stages_do_not_receive_interactive_lifecycle_procedures(self):
        for stage in ("opening", "follow_up", "clarify", "apply_answers"):
            payload = await self.recipe("deep-dive", response_mode="host_stage", stage=stage)
            self.assertEqual(payload["deep_dive_host_contract"]["mutation_scope"], [])
            for unrelated in ("## Required Dependency Order", "## Shared Phase Quality Policy",
                              "## Shared Feature Readiness Gate", "### 5.3 Reconcile"):
                self.assertNotIn(unrelated, payload["instructions"])
            self.assertNotIn("acceptance_policy_version", payload)

    async def test_readiness_and_independent_phase_gates_coexist(self):
        for tool in ("refine-feature", "start-feature"):
            payload = await self.recipe(tool)
            text = " ".join(payload["instructions"].split())
            for rule in ("## Shared Feature Readiness Gate", "## Required Dependency Order",
                         "## Shared Phase Quality Policy", "## Acceptance Responsibility Policy",
                         "No unresolved required command placeholders",
                         "declare each gate independently"):
                self.assertIn(rule, text)
            self.assertNotIn("Every implementation task gets a unit test task", text)
        refinement = (await self.recipe("refine-feature"))["instructions"]
        self.assertIn("Resolve routine technical choices locally", refinement)
        self.assertIn("Refine Feature is a documentation-only planning action", refinement)
        self.assertNotIn("If any unresolved marker exists", refinement)

    async def test_completion_preserves_pr_inventory_and_epic_acceptance(self):
        text = " ".join((await self.recipe("complete-feature"))["instructions"].split())
        for rule in ("every associated PR", "Do not infer merge from a closed PR",
                     "never replace this inventory with just the final PR",
                     "all required features and epic-level acceptance/delivery gates",
                     "### 7.3 Link Feature Acceptance Tests to Epic Acceptance Tests",
                     "### 7.4 Mark Completed Screens in Epic Design Artifacts",
                     "Before committing, execute the readback in 9.4",
                     "without copying it into the source repository",
                     "Reuse passing evidence for unchanged inputs"):
            self.assertIn(rule, text)
        self.assertNotIn("If all epic features are now completed, set Epic Status", text)
