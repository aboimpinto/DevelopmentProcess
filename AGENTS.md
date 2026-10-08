# DevCycle MCP working instructions

Use English and Linux/bash. This is the stateless workflow recipe server; clients
execute its returned instructions. Preserve existing uncommitted work.

Before changing planning, acceptance, tests or bug-repair recipes, read:
- [Acceptance responsibility](docs/acceptance-responsibility-policy.md)
- [EPIC-to-Task traceability and reverse bug tracing](docs/acceptance-test-traceability.md)

Phase and FEAT acceptance can use isolated frontend/backend tests, while EPIC
acceptance maps to full-workflow E2E tests. Preserve EPIC -> FEAT -> Phase -> Task
criterion/test/code links and many-to-many coverage. Passing TwinTests do not
replace EPIC E2E obligations. Tests prove implementation and act as quality gates;
failed required tests or missing required acceptance coverage block acceptance.

The shared policy in DevCycleManager/Prompts/acceptance-responsibility-policy.md
is injected into all planning/delivery recipe boundaries. Keep its documentation
and policy-injection tests aligned. Phase test/review applicability is independent
and explicit; developers may revise scope decisions with reasons, without erasing
failures or losing higher-level obligations.

Run the Python unittest suite in the built image when local dependencies are
unavailable. Replace a running MCP container only when authorized by the user;
preserve its endpoint/configuration and verify live JSON-RPC policy responses.

At every acceptance boundary, assess meaningful behavioral coverage against agreed
criteria: sufficient evidence, important behavior and remaining gaps. Inspect real
assertions and boundaries; percentages/counts are diagnostic signals, not proof.
Apply this during Task/Phase/FEAT/EPIC acceptance as well as bug repair.
