import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from main import JsonRpcRequest, json_rpc_handler


class SharedQualityGateRecipeTests(unittest.IsolatedAsyncioTestCase):
    async def recipe(self, name):
        response = await json_rpc_handler(JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": name, "arguments": {
                "feature_id": "FEAT-901", "phase_number": 11,
                "feature_path": "/synthetic/feature", "file_path": "/synthetic/feature/FeatureDescription.md", "epic_id": "EPIC-901",
                "description": "Synthetic bounded workflow", "title": "Synthetic workflow",
            }},
        ))
        self.assertIsNone(response.error)
        payload = response.result["structuredContent"]
        self.assertEqual(json.loads(response.result["content"][0]["text"]), payload)
        return payload

    async def test_project_command_policy_reaches_planning_development_and_acceptance(self):
        policy = (Path(__file__).parent / "Prompts/project-test-plan-authoring-policy.md").read_text()
        for name in ("refine-feature", "start-feature", "continue-implementation", "code-review", "accept-phase", "complete-feature"):
            with self.subTest(recipe=name):
                payload = await self.recipe(name)
                self.assertIn(policy, payload["instructions"])
                if name == "refine-feature":
                    self.assertIn("FeatureDescription.md", payload["outputs"])
                self.assertIn("## TestPlan", payload["instructions"])
                self.assertIn("## Verification References", payload["instructions"])

    async def test_shared_machine_gate_contract_reaches_all_consumers(self):
        schemas = []
        for name in ("refine-feature", "start-feature", "continue-implementation", "code-review", "accept-phase", "complete-feature"):
            payload = await self.recipe(name)
            schema = payload["phase_gate_exchange_schema"]
            schemas.append(schema)
            self.assertEqual(schema["properties"]["kind"], {"const": "phase.gates"})
            flags = schema["properties"]["payload"]["properties"]["flags"]
            self.assertEqual(set(flags["required"]), {"needCodeReview", "needTestCoverage"})
            self.assertNotIn("audit", schema["required"])
            self.assertIn("same-phase repair work", payload["instructions"])
            self.assertIn("report", payload["instructions"].lower())
        self.assertTrue(all(schema == schemas[0] for schema in schemas))

    async def test_refinement_and_acceptance_share_behavioral_coverage_semantics(self):
        for name in ("refine-feature", "continue-implementation", "accept-phase", "complete-feature"):
            with self.subTest(recipe=name):
                result = await self.recipe(name)
                flags = result["phase_gate_exchange_schema"]["properties"]["payload"]["properties"]["flags"]["properties"]
                description = flags["needTestCoverage"].get("description", "")
                self.assertIn("acceptance criteria", description)
                self.assertIn("absent percentage thresholds or instrumentation never disable this flag", description)
                instructions = " ".join(result["instructions"].split())
                self.assertIn("Acceptance coverage", instructions)
                self.assertIn("Numeric coverage measurement", instructions)
                self.assertIn("Do not copy numeric N/A into needTestCoverage", instructions)

    async def test_same_policy_reaches_every_phase_and_feature_boundary(self):
        policies = []
        for name in ("refine-feature", "start-feature", "continue-implementation",
                     "code-review", "accept-phase", "complete-feature"):
            with self.subTest(recipe=name):
                payload = await self.recipe(name)
                self.assertEqual(payload.get("quality_gate_policy_version"), "devcycle-phase-quality/v2")
                self.assertIn("## Shared Phase Quality Policy", payload["instructions"])
                self.assertIn("Feature completion reuses the same phase decisions", payload["instructions"])
                policies.append(payload["instructions"].split("\n\n---\n\n", 1)[0])
        self.assertEqual(len(set(policies)), 1)

    async def test_production_test_only_and_documentation_have_distinct_obligations(self):
        instructions = " ".join((await self.recipe("code-review"))["instructions"].split())
        for required in ("PRODUCTION_CODE", "TEST_ONLY", "DOCUMENTATION_ONLY", "MIXED",
                         "Do not measure coverage of test code", "Meaningful assertions",
                         "Do not exempt a phase by its number or name"):
            self.assertIn(required, instructions)
        self.assertNotIn("Phase 0 (Health Check) or Phase 1 (Planning & Analysis)", instructions)

    async def test_required_execution_and_coverage_failures_cannot_be_standard_notes(self):
        instructions = " ".join((await self.recipe("code-review"))["instructions"].split())
        for required in ("ZERO_TESTS_DISCOVERED", "NOT_EXECUTED", "UNVERIFIED",
                         "CRITICAL (Must Fix)", "NEEDS_CHANGES", "COVERAGE_POLICY_UNDEFINED",
                         "lines", "branches", "functions", "statements", "tested revision"):
            self.assertIn(required, instructions)
        self.assertIn("Missing required measurements are not zero percent", instructions)

    async def test_explicit_gates_and_epic_workflow_obligations_reach_all_consumers(self):
        for name in ("refine-feature", "continue-implementation", "code-review", "accept-phase", "complete-feature"):
            with self.subTest(recipe=name):
                payload = await self.recipe(name)
                instructions = " ".join(payload["instructions"].split())
                self.assertIn("declare each gate independently", instructions)
                self.assertIn("developer may revise that declaration", instructions)
                self.assertIn("frontend TwinTest or backend TwinTest", instructions)
                self.assertIn("full E2E suite must execute and pass", instructions)
                self.assertIn("a green TwinTest must not waive it", instructions)
                self.assertIn("Acceptance is traced through EPIC, FEAT, Phase and Task", instructions)
                self.assertIn("There is no one-to-one E2E requirement per TwinTest", instructions)
                self.assertIn("missing audit metadata alone is not an acceptance blocker", instructions)
                self.assertNotIn("Every implementation task has a corresponding unit test task", instructions)
                self.assertNotIn("Require review for production-code, test-only and mixed", instructions)

    async def test_acceptance_ownership_reaches_epic_feature_phase_and_task_creation(self):
        from main import ACCEPTANCE_POLICY_TOOLS
        policies = []
        for name in sorted(ACCEPTANCE_POLICY_TOOLS):
            with self.subTest(recipe=name):
                payload = await self.recipe(name)
                self.assertEqual(payload["acceptance_policy_version"], "acceptance-responsibility/v1")
                policy = payload["instructions"].split("\n\n---\n\n", 1)[0]
                policies.append(policy)
                for level in ("EPIC", "FEAT", "Phase", "Task"):
                    self.assertIn("| " + level + " |", policy)
                self.assertIn("Phase and FEAT acceptance can use isolated frontend/backend tests", policy)
                self.assertIn("A passing TwinTest does not replace that E2E obligation", policy)
                self.assertIn("many-to-many", policy)
                self.assertIn("Apply the same coverage assessment during Task, Phase, FEAT and EPIC acceptance", policy)
                self.assertIn("Explain what each test proves and whether an incorrect implementation would make it fail", policy)
                self.assertIn("Coverage percentages and test counts are diagnostic signals", policy)
                self.assertIn("missing required acceptance coverage block acceptance", policy)
                self.assertIn("stable criterion IDs and parent links", policy)
                self.assertIn("relevant implementation files", policy)
                self.assertIn("For a bug, first add or select an E2E or TwinTest that reproduces the failure", policy)
        self.assertEqual(len(set(policies)), 1)

    async def test_recipes_do_not_override_declarations_with_number_or_work_class_rules(self):
        forbidden = (
            "If current phase is Phase 1", "Phases 2-8 must read", "missing in Phase 2-8",
            "Every phase MUST pass before acceptance", "Every phase checkpoint requires",
            "ALWAYS for phases", "May skip for phases",
            "for code phases", "or N/A for non-code phases",
            "required for production-code, test-only and mixed changes",
            "For the first ordered phase and final ordered phase",
            "If still NEEDS_CHANGES after 3 cycles", "max 3 cycles",
        )
        for name in ("refine-feature", "start-feature", "continue-implementation", "accept-phase", "complete-feature"):
            instructions = (await self.recipe(name))["instructions"]
            for phrase in forbidden:
                with self.subTest(recipe=name, forbidden=phrase):
                    self.assertNotIn(phrase, instructions)

    async def test_completion_consumes_existing_evidence_before_requesting_execution(self):
        instructions = (await self.recipe("complete-feature"))["instructions"]
        self.assertIn("Reuse passing evidence for unchanged inputs", instructions)
        self.assertNotIn("This is the final ordered feature gate. Run the complete", instructions)

    async def test_missing_shared_policy_fails_closed_instead_of_serving_old_review(self):
        with TemporaryDirectory() as folder:
            from main import PROMPTS_DIR
            Path(folder, "code-review.md").write_text((PROMPTS_DIR / "code-review.md").read_text())
            with patch("main.PROMPTS_DIR", Path(folder)):
                response = await json_rpc_handler(JsonRpcRequest(
                    jsonrpc="2.0", id=2, method="tools/call",
                    params={"name": "code-review", "arguments": {"feature_id": "FEAT-901", "phase_number": 11}},
                ))
                self.assertIsNotNone(response.error)
                self.assertIsNone(response.result)

    async def test_test_only_exception_preserves_explicit_production_measurement_assignment(self):
        instructions = (await self.recipe("accept-phase"))["instructions"]
        self.assertIn("may explicitly own\nmeasuring earlier production code", instructions)
        self.assertIn("retain the assigned production scope and threshold", instructions)
        self.assertIn("phase number", instructions)


if __name__ == "__main__":
    unittest.main()
