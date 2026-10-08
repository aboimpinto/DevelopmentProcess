# Client-executed feature lifecycle

DevCycle is a recipe server. A successful MCP call delivers operations; it does
not implement, test or complete a feature, and it does not enqueue a background
job. `pending_execution` is expected. The calling coding agent must execute the
procedure using its local tools.

Start Feature and Continue Implementation have one shared execution loop in
`DevCycleManager/client_execution.py`. Start initializes the feature, then joins
the loop; Continue resumes the recorded task. Accept Phase consumes the same
mode and completion boundary. The server still performs no repository mutations.

| Mode | Client completion boundary |
| --- | --- |
| autonomous (default) | All remaining phases accepted and complete-feature executed successfully. |
| single_phase | The selected incomplete phase accepted; no next-phase activation. |

Partial commits and progress reports are interim results. Pending tasks and
failed gates prevent acceptance and require continued work. An early final answer
requires a documented inability to proceed, cancellation or explicit user pause.
Do not invent a new product requirement or waive a real gate to finish.

After every commit or evidence update, the client checks the current task's
remaining deliverables. It continues unfinished work on that task, or records
completion and immediately starts the next pending task in declared order in the
same session. When no tasks remain, it runs the phase gates and acceptance.
Before returning a final answer it checks the selected completion boundary;
ordinary pending work requires another tool operation, not a partial final report.

Execution is incremental: the remaining feature need not fit in a single response
or context window. Neither synchronous execution nor a large remaining workload
establishes an execution budget. A resource-limit stop must identify an actual
user/runtime constraint or observed failure, any known remaining allowance,
permitted recovery attempted and why the next required operation cannot proceed.
Real limits and cancellation remain authoritative; the recipe never overrides
them. Context compaction/recovery belongs to the client harness. Durable resume
notes support that recovery but are not themselves a reason to stop.

The response puts execution ownership, mode, completion boundary and the client
directive before the long instructions. Text JSON and structuredContent contain
the same contract for compatibility. Existing fields and expected-artifact lists
are retained; these lists are not claims that the artifacts were produced.

## Regression investigation

- Commit `9228dcc` (2026-03-03) already returned client-owned, pending recipes.
  The recent changes did not convert a background executor into a recipe server.
- Commit `b51fbb6` (2026-03-26) introduced autonomous lifecycle instructions but
  classified failing quality gates as stopping conditions. Later local text still
  allowed stopping for an unresolved task/gate and made continuation optional.
- The workspace-boundary update left those clauses unchanged. It addressed Git
  entry/recovery/handoff rules, not autonomous execution termination.
- Both a Pi run and a direct Codex run returned normally with an unfinished task.
  The direct client received autonomous mode and the execution-owner contract;
  its final answer incorrectly used client-side execution as an explanation for
  returning partial work. No recorded runtime cutoff establishes causality.
- Conflicting stop clauses and legacy interactive-default text are removed.
  One shared client loop now states the required continuation and stop boundaries.
- A fresh Pi session on 2026-09-24 received that contract but still returned
  `stopReason: stop` after partial Task 2.1 commit `b6c9610aa`, with passing checks
  and no reported blocker. It never reached code review or phase acceptance.
  The task-to-task handoff and pre-final completion check are now explicit in both
  the leading directive and the procedure. This is an instruction improvement,
  not proof that a client will obey it or a server-side continuation mechanism.
- The next Pi attempt accepted Phase 2 and activated Phase 3, then returned a
  normal final response at 21:04:17Z claiming the substantial remaining phases
  exceeded a synchronous execution budget. It made no Phase 3 product edits.
  The visible log contains no corresponding resource-limit error or user cap;
  the last response reports 208,493 total tokens and `stopReason: stop`, with no
  recorded compaction. These facts do not establish the model's internal reason.
  The shared contract now requires concrete evidence for budget-related stops,
  separates remaining workload from runtime limits and preserves client-owned
  context recovery. Phase activation alone does not demonstrate implementation.

The tests exercise actual JSON-RPC calls for both entry points, both modes,
acceptance handoff, invalid modes and equivalent response representations. They
verify the served contract, not model obedience. A fresh client run is still
needed to verify autonomous behaviour end to end.
