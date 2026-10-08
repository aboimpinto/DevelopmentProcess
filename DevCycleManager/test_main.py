import unittest
from dataclasses import FrozenInstanceError

from main import (
    DeepDiveRequest,
    JsonRpcRequest,
    extract_tool_call,
    json_rpc_handler,
    run_accept_phase,
    run_complete_feature,
    run_continue_implementation,
    run_deep_dive,
    run_refine_feature,
    run_start_feature,
)


class ToolCallArgumentCompatibilityTests(unittest.TestCase):
    def test_accepts_standard_mcp_arguments(self):
        name, arguments = extract_tool_call({
            "name": "design-feature",
            "arguments": {"feature_id": "FEAT-123", "feature_path": "/memory/feature"},
        })

        self.assertEqual(name, "design-feature")
        self.assertEqual(arguments["feature_id"], "FEAT-123")
        self.assertEqual(arguments["feature_path"], "/memory/feature")

    def test_preserves_legacy_input_clients(self):
        name, arguments = extract_tool_call({
            "name": "refine-feature",
            "input": {"feature_id": "FEAT-456"},
        })

        self.assertEqual(name, "refine-feature")
        self.assertEqual(arguments, {"feature_id": "FEAT-456"})

    def test_standard_arguments_take_precedence_when_both_shapes_are_present(self):
        _, arguments = extract_tool_call({
            "name": "start-feature",
            "arguments": {"feature_id": "STANDARD"},
            "input": {"feature_id": "LEGACY"},
        })

        self.assertEqual(arguments, {"feature_id": "STANDARD"})

    def test_rejects_non_object_arguments(self):
        with self.assertRaisesRegex(ValueError, "arguments must be an object"):
            extract_tool_call({"name": "design-feature", "arguments": []})


class FeatureExecutionRecipeTests(unittest.IsolatedAsyncioTestCase):
    async def test_workflow_mode_defaults_to_autonomous(self):
        start = await run_start_feature("FEAT-001", "/memory/feature")
        continuation = await run_continue_implementation("FEAT-001", "/memory/feature")

        self.assertIn("**Workflow Mode**: autonomous", start["instructions"])
        self.assertIn("workflow_mode=autonomous", start["instructions"])
        self.assertIn("**Workflow Mode**: autonomous", continuation["instructions"])

    async def test_single_phase_mode_hands_off_from_start_and_stops_after_acceptance(self):
        start = await run_start_feature(
            "FEAT-001", "/memory/feature", workflow_mode="single_phase"
        )
        continuation = await run_continue_implementation(
            "FEAT-001", "/memory/feature", workflow_mode="single_phase"
        )
        acceptance = await run_accept_phase(
            "FEAT-001", 2, "/memory/feature", workflow_mode="single_phase"
        )

        self.assertIn("workflow_mode=single_phase", start["instructions"])
        self.assertIn("implement and accept exactly one phase", continuation["instructions"])
        self.assertIn("stop after this phase is accepted", acceptance["instructions"])

    async def test_quality_gates_forbid_preexisting_failure_waivers(self):
        continuation = await run_continue_implementation("FEAT-001", "/memory/feature")
        acceptance = await run_accept_phase("FEAT-001", 0, "/memory/feature")
        completion = await run_complete_feature("FEAT-001", "/memory/feature")

        for instructions in (
            continuation["instructions"],
            acceptance["instructions"],
            completion["instructions"],
        ):
            self.assertIn("A failed configured command remains RED", instructions)
            self.assertIn("Boy Scout Rule", instructions)
            self.assertIn("pre-existing", instructions)
            self.assertIn("focused rerun", instructions)

    async def test_refinement_and_autonomous_execution_never_defer_human_signoff(self):
        refinement = await run_refine_feature("FEAT-001", "/memory/feature")
        start = await run_start_feature("FEAT-001", "/memory/feature")
        continuation = await run_continue_implementation("FEAT-001", "/memory/feature")
        acceptance = await run_accept_phase("FEAT-001", 1, "/memory/feature")

        self.assertIn("must not create human-sign-off tasks", refinement["instructions"])
        self.assertIn("resolve it through Deep-Dive before refinement", refinement["instructions"])
        for instructions in (
            start["instructions"],
            continuation["instructions"],
            acceptance["instructions"],
        ):
            self.assertIn("never stop to request human sign-off", instructions)
            self.assertIn("delegated decision authority", instructions)

    async def test_external_release_findings_do_not_block_implementation_completion(self):
        refinement = await run_refine_feature("FEAT-001", "/memory/feature")
        continuation = await run_continue_implementation("FEAT-001", "/memory/feature")
        completion = await run_complete_feature("FEAT-001", "/memory/feature")

        self.assertIn("must not become implementation-completion gates", refinement["instructions"])
        for instructions in (continuation["instructions"], completion["instructions"]):
            self.assertIn("Implementation completion and release readiness are independent", instructions)
            self.assertIn("external release dependency", instructions)
            self.assertIn("Lessons Learned", instructions)
            self.assertIn("must not leave the phase or feature incomplete", instructions)

    async def test_manual_only_tests_are_skipped_and_traced_to_the_manual_test_pack(self):
        refinement = await run_refine_feature("FEAT-001", "/memory/feature")
        start = await run_start_feature("FEAT-001", "/memory/feature")
        continuation = await run_continue_implementation("FEAT-001", "/memory/feature")

        self.assertIn("MANUAL_TEST_REQUIRED", refinement["instructions"])
        self.assertIn("ManualTestObligations.json", refinement["instructions"])
        self.assertIn("This test cannot be automated and the user needs to test it manually.", refinement["instructions"])
        self.assertIn("[contract:<taskId>]", refinement["instructions"])
        self.assertIn("exact same `taskId`", refinement["instructions"])
        self.assertIn("matching `PENDING` entry", start["instructions"])
        self.assertIn("HEPHA_MANUAL_TEST_DEFERRAL_V1", continuation["instructions"])
        self.assertIn("Do not mark the task `COMPLETED`", continuation["instructions"])

    async def test_refinement_generates_cargo_serialization_only_for_cargo_build_scope(self):
        refinement = await run_refine_feature("FEAT-001", "/memory/feature")
        instructions = refinement["instructions"]

        self.assertIn("both conditions are proven", instructions)
        self.assertIn("`Cargo.toml` exists in the target product workspace", instructions)
        self.assertIn("will invoke Cargo", instructions)
        self.assertIn("Do not emit this profile merely because Rust is mentioned", instructions)
        self.assertIn("every generated phase file", instructions)
        self.assertIn("Sequential Cargo invocations are permitted", instructions)
        self.assertIn("Never background Cargo or emit concurrent Cargo tool calls", instructions)
        self.assertNotIn("exactly one Cargo invocation", instructions)

    async def test_tool_schema_exposes_validated_execution_modes_with_autonomous_default(self):
        response = await json_rpc_handler(
            JsonRpcRequest(jsonrpc="2.0", method="tools/list", id=3)
        )
        for tool_name in ("start-feature", "continue-implementation", "accept-phase"):
            tool = next(item for item in response.result["tools"] if item["name"] == tool_name)
            workflow_mode = tool["inputSchema"]["properties"]["workflow_mode"]
            self.assertEqual(workflow_mode["enum"], ["autonomous", "single_phase"])
            self.assertEqual(workflow_mode["default"], "autonomous")


class DeepDiveRequestTests(unittest.TestCase):
    def test_defaults_to_immutable_comprehensive_request(self):
        request = DeepDiveRequest.create("/memory/FeatureDescription.md")

        self.assertEqual(request.file_path, "/memory/FeatureDescription.md")
        self.assertEqual(request.mode, "comprehensive")
        self.assertEqual(request.focus, ())
        self.assertEqual(request.response_mode, "adaptive_interview")
        with self.assertRaises(FrozenInstanceError):
            request.mode = "targeted"

    def test_rejects_invalid_target_or_mode(self):
        with self.assertRaisesRegex(ValueError, "file_path is required"):
            DeepDiveRequest.create("  ")
        with self.assertRaisesRegex(ValueError, "Unsupported deep-dive mode"):
            DeepDiveRequest.create("/memory/spec.md", mode="everything")
        with self.assertRaisesRegex(ValueError, "Unsupported deep-dive response_mode"):
            DeepDiveRequest.create("/memory/spec.md", response_mode="stream_everything")

    def test_targeted_mode_requires_non_blank_focus_questions(self):
        with self.assertRaisesRegex(ValueError, "at least one focus question"):
            DeepDiveRequest.create("/memory/spec.md", mode="targeted")
        with self.assertRaisesRegex(ValueError, "focus questions must be non-empty"):
            DeepDiveRequest.create("/memory/spec.md", mode="targeted", focus=["  "])


class DeepDiveRecipeTests(unittest.IsolatedAsyncioTestCase):
    async def test_comprehensive_recipe_has_single_target_guards(self):
        result = await run_deep_dive("/memory/Features/00_EPICS/EPIC-001/EpicDescription.md")
        instructions = result["instructions"]

        self.assertIn("**Mode**: comprehensive", instructions)
        self.assertIn("sole Deep-Dive target", instructions)
        self.assertIn("Only the target file may be modified", instructions)
        self.assertIn("read-only evidence", instructions)
        self.assertIn("Select exactly one primary checklist", instructions)
        self.assertIn("[NEEDS_VALIDATION]", instructions)
        self.assertNotIn("{{mode}}", instructions)
        self.assertNotIn("{{focus}}", instructions)

    async def test_question_manifest_recipe_returns_all_options_without_mutation(self):
        result = await run_deep_dive(
            "/memory/Features/01_SUBMITTED/FEAT-002/FeatureDescription.md",
            response_mode="question_manifest",
        )
        instructions = result["instructions"]

        self.assertIn("**Response Mode**: question_manifest", instructions)
        self.assertIn("Return every currently identifiable question", instructions)
        self.assertIn('"schema_version": "devcycle-deep-dive-question-manifest/v1"', instructions)
        self.assertIn("Do not ask the user a question", instructions)
        self.assertEqual(result["deep_dive_scope"]["response_mode"], "question_manifest")
        self.assertEqual(result["deep_dive_scope"]["mutation_scope"], [])
        self.assertEqual(result["outputs"], ["DeepDiveQuestionManifestV1 JSON"])

    async def test_targeted_recipe_renders_focus_and_protects_completed_decisions(self):
        result = await run_deep_dive(
            "/memory/Features/01_SUBMITTED/FEAT-001/FeatureDescription.md",
            mode="targeted",
            focus=["Where should the canonical corpus live?"],
        )
        instructions = result["instructions"]

        self.assertIn("**Mode**: targeted", instructions)
        self.assertIn("Where should the canonical corpus live?", instructions)
        self.assertIn("Do not execute the full file-type checklist", instructions)
        self.assertIn("Completed decisions are authoritative", instructions)
        self.assertIn("must not defer an implementation decision", instructions)
        self.assertIn("Allowed statuses are `completed`, `already_resolved`", instructions)
        self.assertEqual(result["deep_dive_scope"]["mode"], "targeted")
        self.assertEqual(
            result["deep_dive_scope"]["focus"],
            ["Where should the canonical corpus live?"],
        )

    async def test_tools_list_exposes_backward_compatible_optional_scope(self):
        response = await json_rpc_handler(
            JsonRpcRequest(jsonrpc="2.0", method="tools/list", id=1)
        )
        tool = next(item for item in response.result["tools"] if item["name"] == "deep-dive")
        schema = tool["inputSchema"]

        self.assertEqual(schema["required"], ["file_path"])
        self.assertEqual(schema["properties"]["mode"]["enum"], ["comprehensive", "targeted"])
        self.assertEqual(schema["properties"]["focus"]["type"], "array")
        self.assertEqual(
            schema["properties"]["response_mode"]["enum"],
            ["adaptive_interview", "question_manifest", "host_stage"],
        )

    async def test_standard_mcp_arguments_reach_targeted_recipe(self):
        response = await json_rpc_handler(
            JsonRpcRequest(
                jsonrpc="2.0",
                method="tools/call",
                id=2,
                params={
                    "name": "deep-dive",
                    "arguments": {
                        "file_path": "/memory/FeatureDescription.md",
                        "mode": "targeted",
                        "focus": ["Resolve the ownership decision"],
                        "response_mode": "question_manifest",
                    },
                },
            )
        )
        result = response.result["structuredContent"]

        self.assertEqual(result["status"], "pending_execution")
        self.assertIn("**File Path**: /memory/FeatureDescription.md", result["instructions"])
        self.assertIn("Resolve the ownership decision", result["instructions"])
        self.assertEqual(result["deep_dive_scope"]["response_mode"], "question_manifest")
        self.assertFalse(result["retry_same_tool"])


if __name__ == "__main__":
    unittest.main()
