"""Contract tests for recipe delivery, not simulated execution of GitHub writes."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "DevCycleManager"))
import main


COMMANDS = {
    "sync-epic": {"epic_id": "EPIC-123", "epic_path": "/client/epic"},
    "sync-feature": {"feature_id": "FEAT-456", "feature_path": "/client/feature"},
    "refresh-delivery": {"feature_id": "FEAT-456", "feature_path": "/client/feature"},
}
HOOKS = {
    "create-epic-features": {"epic_id": "EPIC-123"},
    "refine-feature": {"feature_id": "FEAT-456"},
    "start-feature": {"feature_id": "FEAT-456"},
    "continue-implementation": {"feature_id": "FEAT-456"},
    "accept-phase": {"feature_id": "FEAT-456", "phase_number": 42},
    "complete-feature": {"feature_id": "FEAT-456"},
}


class GitHubSyncTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, tool, args, field="arguments"):
        response = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": tool, field: args},
        ))
        self.assertIsNone(response.error)
        result = response.result
        payload = result["structuredContent"]
        self.assertEqual(payload, json.loads(result["content"][0]["text"]))
        return result, payload

    async def test_discovery_and_both_call_shapes_preserve_client_execution(self):
        discovery = await main.json_rpc_handler(main.JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/list", params={},
        ))
        tools = discovery.result["tools"]
        self.assertEqual(16, len(tools))
        self.assertEqual(16, len({tool["name"] for tool in tools}))
        for name, args in COMMANDS.items():
            schema = next(t["inputSchema"] for t in tools if t["name"] == name)
            id_key = "epic_id" if name == "sync-epic" else "feature_id"
            self.assertEqual([id_key], schema["required"])
            self.assertIn("project_path", schema["properties"])
            for field in ("arguments", "input"):
                with self.subTest(name=name, field=field):
                    result, payload = await self.call(name, dict(args, project_path="/client/repo"), field)
                    self.assertFalse(result["isError"])
                    self.assertEqual("pending_execution", payload["status"])
                    self.assertEqual("client_llm", payload["execution_owner"])
                    self.assertEqual("execute_returned_procedure", payload["next_action"])
                    self.assertFalse(payload["retry_same_tool"])
                    direction = "github_to_local_then_issue" if name == "refresh-delivery" else "local_to_github"
                    self.assertEqual(direction, payload["sync_direction"])
                    self.assertIn(args[id_key], payload["instructions"])
                    self.assertIn("/client/repo", payload["instructions"])
                    self.assertNotIn("{{", payload["instructions"])

    async def test_optional_paths_are_not_required_or_read_by_server(self):
        # Only prompt files may be read; nonexistent client paths must remain data.
        original = Path.read_text
        def read(path, *args, **kwargs):
            self.assertEqual(main.PROMPTS_DIR, path.parent)
            return original(path, *args, **kwargs)
        with patch.object(Path, "read_text", read), patch("subprocess.run", side_effect=AssertionError("No commands on server")):
            for name, args in COMMANDS.items():
                id_key = "epic_id" if name == "sync-epic" else "feature_id"
                result, _ = await self.call(name, {id_key: args[id_key]})
                self.assertFalse(result["isError"])
                result, payload = await self.call(name, dict(args, project_path="/not/mounted/{{feature_id}}"))
                self.assertFalse(result["isError"])
                self.assertIn("/not/mounted/{{feature_id}}", payload["instructions"])

    async def test_invalid_identity_or_paths_never_return_an_executable_recipe(self):
        for name, args in COMMANDS.items():
            id_key = "epic_id" if name == "sync-epic" else "feature_id"
            for value in (None, "", "../FEAT-1", "FEAT-1\n", "wrong-1", 4, True, {}, []):
                with self.subTest(name=name, value=value):
                    result, payload = await self.call(name, dict(args, **{id_key: value}))
                    self.assertTrue(result["isError"])
                    self.assertFalse(payload["tool_call_success"])
                    self.assertNotIn("instructions", payload)
            for key in (id_key.replace("_id", "_path"), "project_path"):
                for value in ("", " \t", "x\ny", "x\0y", 4, {}, []):
                    result, payload = await self.call(name, dict(args, **{key: value}))
                    self.assertTrue(result["isError"])
                    self.assertIn(key, payload["message"])

    async def test_required_shared_policy_reaches_commands_and_lifecycle_hooks_once(self):
        policy = (main.PROMPTS_DIR / "github-sync.md").read_text()
        for name, args in (COMMANDS | HOOKS).items():
            result, payload = await self.call(name, args)
            self.assertFalse(result["isError"])
            self.assertEqual(1, payload["instructions"].count(policy))
        _, payload = await self.call("submit-feature", {"description": "Synthetic"})
        self.assertNotIn(policy, payload["instructions"])

    async def test_missing_empty_policy_fails_closed_and_live_updates_are_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            with patch.object(main, "PROMPTS_DIR", root):
                path = root / "github-sync.md"
                for content in (None, "", " \n"):
                    if content is None:
                        path.unlink()
                    else:
                        path.write_text(content)
                    for name, args in (COMMANDS | HOOKS).items():
                        result, payload = await self.call(name, args)
                        self.assertTrue(result["isError"])
                        self.assertIn("github-sync.md", payload["message"])
                        self.assertNotIn("instructions", payload)
                for revision in ("SYNC_FIRST", "SYNC_SECOND"):
                    path.write_text(revision)
                    for name, args in (COMMANDS | HOOKS).items():
                        result, payload = await self.call(name, args)
                        self.assertFalse(result["isError"])
                        self.assertEqual(1, payload["instructions"].count(revision))
                        if revision == "SYNC_SECOND":
                            self.assertNotIn("SYNC_FIRST", payload["instructions"])

    async def test_missing_or_empty_individual_recipe_is_not_success(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "Prompts"
            shutil.copytree(main.PROMPTS_DIR, root)
            with patch.object(main, "PROMPTS_DIR", root):
                for name, args in COMMANDS.items():
                    path = root / f"{name}.md"
                    for content in (None, " \n"):
                        if content is None:
                            path.unlink()
                        else:
                            path.write_text(content)
                        result, payload = await self.call(name, args)
                        self.assertTrue(result["isError"])
                        self.assertIn(f"{name}.md", payload["message"])
                        self.assertNotIn("instructions", payload)

    async def test_refresh_updates_local_records_then_issue_without_recursive_sync(self):
        _, payload = await self.call("refresh-delivery", COMMANDS["refresh-delivery"])
        self.assertIn("Existing feature issue delivery table", payload["outputs"])
        self.assertIn("After successfully saving verified local observations, invoke sync-feature once", payload["instructions"])
        self.assertIn("previous issue write is SYNC_PENDING", payload["instructions"])
        self.assertIn("failed remote write preserves the verified", payload["instructions"])
        self.assertIn("sync-feature cannot call back", payload["instructions"])

    async def test_publication_updates_issue_table_before_merge(self):
        _, payload = await self.call("sync-feature", COMMANDS["sync-feature"])
        self.assertIn("| Phase | Unit / tasks | Proposed PR title and short description | Depends on | Actual PR | Delivery status |", payload["instructions"])
        self.assertIn("Do not wait for merge, review completion", payload["instructions"])
        self.assertIn("same issue-table row, before continuing to the next unit", payload["instructions"])

    async def test_refinement_delivers_forecast_before_sync_even_without_config(self):
        result, payload = await self.call("refine-feature", {"feature_id": "FEAT-456"})
        self.assertFalse(result["isError"])
        instructions = payload["instructions"]
        self.assertIn("### PR forecast produced by refinement", instructions)
        self.assertIn("independent of whether\nGitHub synchronization is enabled", instructions)
        self.assertIn("proposed PR title", instructions)
        self.assertIn("short\nreviewer-facing description", instructions)
        self.assertIn("The feature total counts distinct active units exactly once", instructions)
        self.assertIn("unknown scope is unknown, not zero", instructions)
        self.assertIn("R6 includes the PR forecast", instructions)
        self.assertTrue(any("per-phase forecast" in item for item in payload["outputs"]))


if __name__ == "__main__":
    unittest.main()
