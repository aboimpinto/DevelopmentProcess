"""Verify delivered planning contracts; these tests do not certify client execution."""
import json
import shutil
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import main


BOUNDARIES = (
    "refine-feature", "start-feature", "continue-implementation",
    "code-review", "accept-phase", "complete-feature",
)


class AdaptivePhasePlanningTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, name, **arguments):
        return await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": name, "arguments": {
                "feature_id": "FEAT-901", "phase_number": 37, **arguments,
            }},
        ))

    async def payload(self, name, **arguments):
        response = await self.call(name, **arguments)
        self.assertIsNone(response.error)
        self.assertFalse(response.result["isError"])
        payload = response.result["structuredContent"]
        self.assertEqual(payload, json.loads(response.result["content"][0]["text"]))
        return payload

    async def test_same_required_roles_policy_reaches_every_lifecycle_boundary(self):
        policy = (main.PROMPTS_DIR / "feature-phase-planning-policy.md").read_text()
        for name in BOUNDARIES:
            with self.subTest(tool=name):
                payload = await self.payload(name)
                self.assertEqual("devcycle-feature-phases/v1", payload["feature_phase_policy_version"])
                self.assertEqual(1, payload["instructions"].count(policy))
                self.assertEqual("pending_execution", payload["status"])
                self.assertEqual("client_llm", payload["execution_owner"])
                # Role metadata must not break existing strict host exchanges.
                schema = payload["phase_gate_exchange_schema"]["properties"]["payload"]
                self.assertNotIn("phaseRole", schema["properties"])

    async def test_refinement_discovery_outputs_and_templates_do_not_force_nine_layers(self):
        listing = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=2, method="tools/list",
        ))
        description = next(t["description"] for t in listing.result["tools"]
                           if t["name"] == "refine-feature")
        payload = await self.payload("refine-feature")
        for text in (description, " ".join(payload["outputs"]), payload["instructions"]):
            with self.subTest(surface=text[:70]):
                for role in ("Initial Checkpoint", "Planning", "Final Checkpoint"):
                    self.assertIn(role, text)
                for stale in ("phase-0 through phase-8", "phase-5-user-interface.md",
                              "phase-8-final-checkpoint.md", "0/9", "9 phases"):
                    self.assertNotIn(stale, text)
        self.assertIn("[actual phase count]", payload["instructions"])
        self.assertIn("**Phase Role**:", payload["instructions"])
        self.assertIn("Structure Rationale", payload["instructions"])

    async def test_checkpoint_and_planning_obligations_are_served_without_claiming_a_pass(self):
        payload = await self.payload("refine-feature")
        text = " ".join(payload["instructions"].split())
        for rule in (
            "A failed baseline blocks progression to Planning and feature implementation",
            "build must have zero errors and zero warnings",
            "all required tests must pass",
            "Files/modules to create, modify, move or delete",
            "Relevant lessons learned, previous traps",
            "Declare fresh execution",
            "Baseline results and focused development runs cannot replace this final verification",
            "Feature completion can reuse this verified final-checkpoint evidence",
            "Required checkpoint commands remain required even when both flags are false",
            "Refine Feature is a documentation-only planning action",
            "Refinement only plans these checks; it must not run them or mark their outcomes PASSED",
        ):
            with self.subTest(rule=rule):
                self.assertIn(rule, text)
        self.assertEqual("execute_returned_procedure", payload["next_action"])

    async def test_missing_empty_or_incompatible_policy_never_returns_partial_lifecycle_recipe(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(main.PROMPTS_DIR, root, dirs_exist_ok=True)
            policy = root / "feature-phase-planning-policy.md"
            with patch.object(main, "PROMPTS_DIR", root):
                for contents in (None, "", " \n", "Policy version: incompatible/v9"):
                    if contents is None:
                        policy.unlink()
                    else:
                        policy.write_text(contents)
                    for name in BOUNDARIES:
                        with self.subTest(contents=contents, tool=name):
                            response = await self.call(name)
                            self.assertIsNotNone(response.error)
                            self.assertIsNone(response.result)
                    # Bounded hosted interviews do not depend on lifecycle planning.
                    hosted = await self.payload("deep-dive", file_path="/synthetic/spec.md",
                                                response_mode="host_stage", stage="opening")
                    self.assertNotIn("feature_phase_policy_version", hosted)

    async def test_policy_is_reloaded_without_restart(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copytree(main.PROMPTS_DIR, root, dirs_exist_ok=True)
            policy = root / "feature-phase-planning-policy.md"
            with patch.object(main, "PROMPTS_DIR", root):
                for revision in ("FIRST_POLICY_REVISION", "SECOND_POLICY_REVISION"):
                    policy.write_text("Policy version: devcycle-feature-phases/v1\n" + revision)
                    for name in BOUNDARIES:
                        with self.subTest(revision=revision, tool=name):
                            payload = await self.payload(name)
                            self.assertEqual(1, payload["instructions"].count(revision))
                            if revision == "SECOND_POLICY_REVISION":
                                self.assertNotIn("FIRST_POLICY_REVISION", payload["instructions"])

    async def test_existing_plans_preserve_history_and_both_execution_modes(self):
        for mode in ("autonomous", "single_phase"):
            for name in ("start-feature", "continue-implementation", "accept-phase"):
                with self.subTest(mode=mode, tool=name):
                    payload = await self.payload(name, workflow_mode=mode)
                    self.assertEqual("selected_phase_accepted" if mode == "single_phase"
                                     else "feature_completed", payload["completion_boundary"])
                    text = " ".join(payload["instructions"].split())
                    self.assertIn("Never fabricate a pre-change baseline after coding has begun", text)
                    self.assertIn("Do not reopen completed features solely to retrofit", text)
                    self.assertIn("never use a fixed denominator", text)
                    self.assertIn("not new fields in that strict JSON envelope", text)


if __name__ == "__main__":
    unittest.main()
