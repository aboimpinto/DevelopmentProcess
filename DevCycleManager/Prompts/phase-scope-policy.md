# Phase scope and gate applicability

This shared policy takes precedence over generic recipe boilerplate that calls for
code review or coverage at every phase or exempts a numbered phase. Reconcile
explicit needCodeReview and needTestCoverage declarations against intended scope
before executing a recipe; synchronize Markdown and machine gate records with
old/new flags, scope reasons and evidence. Do not fabricate acceptance, drop
agreed requirements or mark failing evidence passed.

### Scope boundaries and final gate selection

Determine the intended deliverables before selecting gates. Keep the scope the
human assigned to a phase; do not expand a planning/checkpoint phase into mixed
implementation just to fit executable work into it. These are scope conditions,
not phase-number exceptions. The same conditions apply to any phase identifier.

| Declared deliverables | needCodeReview | needTestCoverage | Required completion work |
| --- | --- | --- | --- |
| Planning/documentation only | false | false | Validate the required documents, decisions, references and task/criterion ownership. No invented test or code-review loop. |
| Initial checkpoint only | false | false | Execute the explicitly declared baseline health checks; record observed results without authoring tests or production changes. |
| Final checkpoint only | false | false | Execute or reuse the declared final checks and reconcile earlier acceptance evidence. Do not reopen production review or create another coverage-authoring loop for unchanged work. |
| Test-only work | false | Explicit assigned production-behavior assessment only | Execute the declared tests and evaluate their meaningful assertions. No coverage of test code or production-code review of test files. |
| Production or explicitly mixed implementation | Independent scope decision | Independent scope decision | Name the production review scope and the behavior that needs testing; do not infer one flag from the other. |

Do not place executable fixture capture, test harness creation, test implementation
or production edits inside a planning/documentation-only phase. Plan that work
there, then assign its execution to a named implementation or test-only owner
before any change that depends on it. Keep checkpoint repairs in the responsible
implementation/test task; a real failure must be repaired, not relabelled N/A.
If accepted scope intentionally adds production changes, first revise the phase's
deliverables, task ownership and independent flags with a recorded reason.

Do not run production-code review over test-only changes. Evaluate assertions against the assigned production behavior
as part of test verification: scenario alignment, isolation, alternatives and
defect detection remain required. Do not measure coverage of test code or
recursively require tests of the test harness. A TEST_ONLY phase may explicitly own
measuring earlier production code; retain the assigned production scope and threshold.
That is the reason for a true needTestCoverage flag, not the presence of test files.
If tests expose a production defect, repair it under an identified production
scope with its applicable review gate; test-only status cannot exempt that repair.

A false coverage flag never cancels a declared test command. Initial and final
checkpoints still run their explicitly assigned tests/build/lint (or reuse valid
unchanged-input evidence where allowed), and failed required checks prevent
acceptance. Final evidence reconciliation must identify missing or invalidated
proof and route it to its existing owner. It does not require a duplicate review
or assessment of unchanged, already accepted work.

When correcting a previously mixed plan, document the user-authorized scope
correction, old/new flags, stable task/criterion IDs, new owner and dependencies.
Preserve failed evidence and move unresolved obligations with the task; never
turn a failed run into a pass. Synchronize Markdown, phase.gates, task ledgers,
TestPlan/FeatureDescription mappings and evidence references. A task move is not
completion and does not justify removing a feature-level acceptance obligation.
