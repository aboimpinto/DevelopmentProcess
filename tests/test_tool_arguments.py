import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "DevCycleManager"))

from main import JsonRpcRequest, json_rpc_handler


class ToolArgumentsTests(unittest.IsolatedAsyncioTestCase):
    async def call_submit_feature(self, **payload):
        response = await json_rpc_handler(JsonRpcRequest(
            jsonrpc="2.0", id=1, method="tools/call",
            params={"name": "submit-feature", **payload},
        ))
        self.assertIsNone(response.error)
        self.assertFalse(response.result["isError"])
        return response.result["structuredContent"]["instructions"]

    async def test_standard_arguments_reach_procedure(self):
        instructions = await self.call_submit_feature(
            arguments={"description": "STANDARD_ARGUMENT_SENTINEL"},
        )
        self.assertIn("STANDARD_ARGUMENT_SENTINEL", instructions)

    async def test_legacy_input_still_reaches_procedure(self):
        instructions = await self.call_submit_feature(
            input={"description": "LEGACY_INPUT_SENTINEL"},
        )
        self.assertIn("LEGACY_INPUT_SENTINEL", instructions)

    async def test_standard_arguments_take_precedence(self):
        instructions = await self.call_submit_feature(
            arguments={"description": "STANDARD_ARGUMENT_SENTINEL"},
            input={"description": "LEGACY_INPUT_SENTINEL"},
        )
        self.assertIn("STANDARD_ARGUMENT_SENTINEL", instructions)
        self.assertNotIn("LEGACY_INPUT_SENTINEL", instructions)
