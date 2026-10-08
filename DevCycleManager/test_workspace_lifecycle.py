"""Exercise the served recipe contract, not an assumed LLM execution outcome."""
import unittest
from main import JsonRpcRequest, json_rpc_handler


class WorkspaceLifecycleRecipeTests(unittest.IsolatedAsyncioTestCase):
    async def recipe(self, tool, mode="autonomous"):
        response = await json_rpc_handler(JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, "arguments": {
                "feature_id": "FEAT-901", "feature_path": "/synthetic/feature",
                "phase_number": 17, "workflow_mode": mode,
            }},
        ))
        self.assertIsNone(response.error)
        payload = response.result["structuredContent"]
        self.assertEqual(payload["status"], "pending_execution")
        self.assertEqual(payload["execution_owner"], "client_llm")
        return payload["instructions"]

    async def test_workspace_contract_reaches_every_gate_consumer(self):
        for tool in ("refine-feature", "start-feature", "continue-implementation",
                     "accept-phase", "code-review", "complete-feature"):
            with self.subTest(tool=tool):
                text = " ".join((await self.recipe(tool)).split())
                for rule in (
                    "### Workspace entry, recovery and clean handoffs",
                    "git status --porcelain=v1 --untracked-files=all",
                    "shared owner repository is outside code Git authority",
                    "unfinished merge/rebase operations",
                    "Require a clean code checkout after commits before publishing completion",
                    "A clean checkpoint is evidence of repository state, not proof of test success",
                ):
                    self.assertIn(rule, text)

    async def test_dirty_fresh_start_is_checked_before_any_setup_mutation(self):
        for mode in ("autonomous", "single_phase"):
            with self.subTest(mode=mode):
                text = await self.recipe("start-feature", mode)
                self.assertLess(text.index("## Workspace Preflight (before any write)"),
                                text.index("## Phase 0: Resolve Memory Bank Path"))
                self.assertIn("Keep the feature out of IN_PROGRESS until this entry check succeeds", text)
                self.assertNotIn("If already on a feature branch → continue using it", text)
                self.assertNotIn("git push -u origin", text)

    async def test_startup_generated_reports_are_finalized_before_handoff(self):
        text = await self.recipe("start-feature")
        self.assertLess(text.index("## Phase 8: Generate Success Report"),
                        text.index("### 8.1 Clean Startup Handoff"))
        self.assertLess(text.index("### 8.1 Clean Startup Handoff"),
                        text.index("### 8.2 Implementation Handoff"))
        self.assertIn("record startup-finalization pending and do not invoke", text)
        self.assertIn("without repeating\nthe lifecycle move", text)

    async def test_current_task_dirty_resume_is_recoverable_before_activation(self):
        text = await self.recipe("continue-implementation")
        flat = " ".join(text.split())
        self.assertLess(text.index("## Workspace Preflight (before any write)"),
                        text.index("## Phase 2: State Detection"))
        self.assertIn("current interrupted task are resumable work, not an automatic rejection", flat)
        self.assertIn("After read-only workspace preflight and ownership resolution succeed", text)
        self.assertIn("No table entry bypasses that check", text)

    async def test_deferred_work_requires_discoverable_recovery_without_erasing_failures(self):
        for tool in ("continue-implementation", "accept-phase"):
            with self.subTest(tool=tool):
                text = " ".join((await self.recipe(tool)).split())
                for rule in (
                    "A moved task must carry its files, failed evidence and recovery instructions",
                    "backup/stash commit identity and restoration point in the phase document before retrying",
                    "git stash list",
                    "without overwriting new edits; retain the backup until recovery is verified",
                    "Never automatically stash, reset or clean unknown/user changes",
                ):
                    self.assertIn(rule, text)

    async def test_acceptance_requires_clean_exit_and_preserves_failure_status(self):
        text = await self.recipe("accept-phase")
        flat = " ".join(text.split())
        self.assertLess(text.index("## Workspace Preflight (before any write)"),
                        text.index("## Phase 4: Prepare Completion Records"))
        self.assertLess(text.index("### 5.4 Verify Clean Handoff"),
                        text.index("## Phase 6: Next Phase Preview"))
        self.assertIn("required push failure retains finalization-pending status, not COMPLETED", flat)
        self.assertIn("external documentation-only work does not require an empty code commit", flat)
        self.assertNotIn("### 5.1 Stage All Uncommitted Files (MANDATORY)", text)
        self.assertNotIn("attempt `git pull --rebase` then retry", text)

    async def test_initial_checkpoint_declares_readiness_without_refinement_execution(self):
        text = " ".join((await self.recipe("refine-feature")).split())
        self.assertIn("Assign clean entry and clean exit verification to the initial checkpoint", text)
        self.assertIn("Refinement records pending obligations only", text)
        self.assertIn("it must not run Git cleanup or claim the checkout is clean", text)
        self.assertIn("do not create a circular dependency", text)
        self.assertIn("It is independent of phase numbers and test/review flags", text)


if __name__ == "__main__":
    unittest.main()
