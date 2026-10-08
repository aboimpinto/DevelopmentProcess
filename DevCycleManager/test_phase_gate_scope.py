"""Recipe-boundary regression: non-production phases must not inherit code gates."""
import unittest
from main import JsonRpcRequest, json_rpc_handler


class PhaseGateScopeRecipeTests(unittest.IsolatedAsyncioTestCase):
    async def test_scope_matrix_reaches_every_delivery_boundary(self):
        expected_rows = (
            "| Planning/documentation only | false | false |",
            "| Initial checkpoint only | false | false |",
            "| Final checkpoint only | false | false |",
            "| Test-only work | false | Explicit assigned production-behavior assessment only |",
        )
        for tool in ("refine-feature", "start-feature", "continue-implementation",
                     "code-review", "accept-phase", "complete-feature"):
            for phase in (1, 17):
                with self.subTest(tool=tool, phase=phase):
                    response = await json_rpc_handler(JsonRpcRequest(
                        jsonrpc="2.0", id=1, method="tools/call",
                        params={"name": tool, "arguments": {
                            "feature_id": "FEAT-SCOPE", "feature_path": "/synthetic/feature",
                            "phase_number": phase,
                        }},
                    ))
                    self.assertIsNone(response.error)
                    instructions = response.result["structuredContent"]["instructions"]
                    for row in expected_rows:
                        self.assertIn(row, instructions)
                    for invariant in (
                        "Do not place executable fixture capture, test harness creation",
                        "A false coverage flag never cancels a declared test command",
                        "Preserve failed evidence and move unresolved obligations with the task",
                        "Do not run production-code review over test-only changes",
                        "Evaluate assertions against the assigned production behavior",
                    ):
                        self.assertIn(invariant, instructions)


if __name__ == "__main__":
    unittest.main()
