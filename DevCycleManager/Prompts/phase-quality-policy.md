## Shared Phase Quality Policy

Policy version: `devcycle-phase-quality/v2`.
This policy governs refinement, implementation, code review, phase acceptance,
and feature completion. It takes precedence over generic checkpoint boilerplate
about running every command or skipping review for a numbered phase. It does not
grant additional execution authority or change the selected workflow mode.

### Workspace entry, recovery and clean handoffs

Apply this repository lifecycle contract before workflow mutations and at every
handoff. It is independent of phase numbers and test/review flags. During
refinement, declare these obligations without executing them or claiming a clean
workspace; start/resume/accept operations gather the actual evidence.

Resolve the authorized code repository, feature branch and worktree first. Record
its absolute path, branch, HEAD and `git status --porcelain=v1 --untracked-files=all`
in the existing feature/phase evidence. Inspect staged, unstaged and untracked
paths, including conflicts and unfinished merge/rebase operations. Never mistake
a nested directory inheriting a shared parent's Git root for the code checkout.
External MemoryBank documents retain their lifecycle write authority, but their
shared owner repository is outside code Git authority: do not stage, commit,
push, stash, clean or require cleanliness there. Apply Git steps only inside the
resolved code checkout; follow the project's configured push remote, never assume
`origin` is an authorized publishing destination. Respect explicit non-Git project
policy and record N/A; a failed Git command in an expected Git checkout is an error.

- **Fresh start:** require a clean entry before setup writes, branch creation or
  moving the feature to IN_PROGRESS. An explicitly authorized isolated worktree
  may provide that clean entry without disturbing another checkout. Do not reuse
  an arbitrary feature branch. Recheck the selected feature worktree after setup:
  account for every generated path, commit authorized setup changes when required,
  save the startup report, and verify cleanliness before implementation handoff.
- **Initial checkpoint:** verify the recorded checkout identity and clean entry,
  run only its declared health checks, and reconcile check-generated files before
  a clean exit. Preserve real evidence in its declared location; remove only
  disposable outputs owned by those checks. Report-producing writes must precede
  the final cleanliness check. Do not defer workspace readiness to a later phase.
- **Resume:** before phase activation, task execution or acceptance handoff,
  compare current files with task ownership and prior evidence. Dirty files from
  the current interrupted task are resumable work, not an automatic rejection:
  preserve them, document their ownership and resume repair/validation. Unknown,
  unrelated or later-phase changes require a recovery plan before advancement;
  do not stage them into the current phase or silently erase them. A moved task
  must carry its files, failed evidence and recovery instructions with it. Record
  the owning phase/task, source revision, exact saved paths, backup/stash commit
  identity and restoration point in the phase document before retrying. Inspect
  recorded backups and `git stash list` before reconstructing missing work. Restore
  only the verified feature-owned snapshot in the intended worktree when its task
  begins, without overwriting new edits; retain the backup until recovery is
  verified. Never automatically stash, reset or clean unknown/user changes just
  to pass a gate. A blocked recovery leaves the phase unaccepted, naming the paths
  and authority needed; it does not invent missing product acceptance criteria.
- **Acceptance:** applicable task/check/review evidence must pass, all code-checkout
  changes must have accounted ownership, and required commits must be recorded.
  Save final reports and lifecycle documents before the final Git check. For
  tracked lifecycle documents, prepare completion updates while finalizing; they
  are provisional until commit and the clean handoff succeed. On failure, retain
  an incomplete/finalization-pending status in phase and feature projections.
  Require a clean code checkout after commits before publishing completion or
  advancing. If a later write dirties it, reconcile and recheck before handoff.
  This exit gate remains mandatory; it is not the first workspace inspection.

A clean checkpoint is evidence of repository state, not proof of test success.
Do not fabricate an empty commit just to satisfy a documentation-only phase whose
changes live outside code Git authority. Record the unchanged code HEAD, clean
status and external document updates separately. Any specifically required push
must target the authorized remote; failure retains pending delivery status.

### One gate protocol for every phase

Every phase uses the same completion reducer. Publish the supplied phase.gates
JSON exchange beside the phase document as <phase-document>.gates.json. The
needCodeReview and needTestCoverage booleans are independent: false/false,
false/true, true/false and true/true are all valid. Predict them during refinement
from actual deliverables and acceptance criteria, with pending results. Do not
set outcomes to passed during refinement. Documentation, DTO and checkpoint names
are examples of scope, never exceptions in the gate engine. A phase identity is
an opaque binding reference; its number, letter or title never selects gates.

Preserve criteria, configured checks, actual execution evidence, meaningful
assertion mappings and review outcome. Keep FeatureDescription.md's test manifest
linked to these records. Build, lint and running existing tests are independent
configured obligations even with both flags false. Developers may revise flags
with before/after values, implemented scope, reason and evidence references; they
must not disable gates to hide failures. Update task/phase projections together.
HEPHA supplies a host observation ledger for execution evidence. Use original
execution references, not a shell command that only reads a report. The supplied
schema governs machine exchanges; Markdown is the readable projection. In
coverage.criteria, checkIds reference executable checks only: keep review evidence
in the independent review gate, never add CW-REVIEW as a required test execution.
Audit
runId and timestamps remain optional. Do not invent evidence to satisfy a field.

Missing tests, inadequate meaningful coverage, failing tests and review findings
prevent phase acceptance but remain same-phase repair work. Continue the
implementation/test/review loop automatically within the agreed scope. Do not
activate the next phase until the flags and configured checks are satisfied.
A session boundary is not a reason to abandon repair. When the same failure
persists, reassess infrastructure, architectural assumptions and the attempted
fixes. Report rewrites, timestamps and new invocation IDs are not progress.
Escalate only when a concrete architectural/intent/authority impasse or repeated
lack of a meaningful repair path needs user help. State the exact cause, attempted
repairs, evidence and decision or capability needed. Honor cancellation and
execution authority. Never ask for another Continue click merely for failed tests.

### Acceptance coverage and numeric measurement are different

needTestCoverage asks whether the implemented scope needs meaningful test
assessment against observable behavior and acceptance criteria. It never asks
whether a percentage threshold or instrumentation exists. Do not copy numeric N/A into needTestCoverage. During legacy reconciliation, derive the flag from the
accepted scope and behavioral obligations, preserving existing criterion mappings.
An absent numeric policy or unavailable instrumentation does not remove these
obligations. Do not delete acceptance mappings merely to validate a false flag.
If the record contains an active assessment while disabling it, reconcile that
contradiction before acceptance; this is same-phase repair, not a failed test.
Use the provided schema as convention authority. Older features and transcripts
may supply scope/evidence; they do not replace the current contract definition.

| Declaration | Meaning |
| --- | --- |
| Acceptance coverage | Meaningful assertions prove the applicable acceptance behavior; controlled by needTestCoverage. |
| Numeric coverage measurement | Instrumented line/branch/function/statement metrics under a separately explicit project policy. Absence of such policy does not disable acceptance coverage. |

Refinement predicts the two booleans independently. A phase with no applicable
acceptance-coverage assessment can retain false with a scope justification and
an empty coverage.criteria assessment. Its declared build/lint/test health checks
remain required. Existing test-manifest links remain in FeatureDescription.md.
When the assessment is required, publish true and assess important behavior,
missing assertions and execution evidence without inventing a percentage target.

### Explicit phase gates are the decision authority

Do not exempt a phase by its number or name. Work class and changed-file lists
inform refinement; they do not themselves enable tests, review or browser gates.
During refinement declare each gate independently as REQUIRED or NOT_APPLICABLE
with a scope reason. During development the developer may revise that declaration
when the actual deliverable has nothing applicable to test or review. Record the
old decision, new decision and scope reason; synchronize the phase gate contract,
task list, evidence projection and native execution contract when present.
Do not require a new user confirmation just to record justified applicability.
A failed test or unresolved review finding is not a reason for non-applicability.

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

### Phase integration acceptance and EPIC workflow coverage

A frontend TwinTest or backend TwinTest can prove phase acceptance for its scoped
behavior. Gherkin/Playwright E2E integration tests prove the complete frontend-to-
backend workflow defined by the EPIC's horizontal implementation slices. Neither
layer replaces the other. A UI phase may own frontend TwinTests AND changes to the
EPIC E2E scenarios. Trace EPIC and FEAT acceptance IDs to phase tasks, test identities,
commands and evidence in FeatureDescription.md's test manifest. Assign required
E2E updates to the phases that change the workflow, and explicitly assign where the
full E2E suite must execute and pass (that phase or a later checkpoint). Preserve
that obligation through phase acceptance and feature completion; a green TwinTest
must not waive it. Do not require a full browser run merely because a UI file is
present, and do not infer that UI-only work needs no E2E changes.

Acceptance is traced through EPIC, FEAT, Phase and Task. Preserve those identities and
scope in the test manifest. TwinTests isolate the frontend or backend so many
behavioral alternatives can be exercised efficiently. E2E tests cover selected
complete workflows. Coverage mappings are many-to-many: several TwinTests may
support one workflow and one E2E scenario may cover several acceptance criteria.
There is no one-to-one E2E requirement per TwinTest or per Phase acceptance test.
Require sufficient evidence for every assigned criterion, not matching test counts.

### Refinement records obligations, not successful outcomes

Publish a `## Phase Quality Gate Contract` in each phase: policy version, work
class, output scope, and a gate table with applicability (REQUIRED or
NOT_APPLICABLE), rationale, owner phase, exact configured command, production
coverage includes/excludes and thresholds for lines, branches, functions and
statements where required. Distinguish scenario/requirements coverage from
instrumented code coverage. A suite-presence or traceability checker is not an
instrumented coverage measurement.

Use the same gate labels in the contract and evidence tables: Tests (unit and
scoped integration/TwinTests), Gherkin/Playwright E2E (complete workflow), Code
review, Build, Lint, Acceptance coverage, and Numeric coverage measurement. Keep REQUIRED/NOT_APPLICABLE applicability
separate from PASSED/FAILED execution. Required E2E work owned by another checkpoint
must name that checkpoint and remain in the feature manifest; never drop it.
The explicit table wins over generic task/checkpoint examples in a recipe. Omit
non-applicable execution/review tasks and replace their boilerplate with the reason.

Reuse explicit project standards. Do not invent a percentage or silently promote
an advisory target to a mandatory threshold. If a required coverage scope or
threshold is absent, record `COVERAGE_POLICY_UNDEFINED` and resolve it through
Deep-Dive before publishing implementation-ready refinement. For legacy plans,
reconstruct applicability from recorded scope/standards and stop at an unresolved
policy decision; do not reset completed work or invent historic measurements.
Refinement remains documentation-only and must not run coverage commands.

### Evidence and outcomes

For each required gate record the command, working repository, tested revision
(and dirty-diff identity if applicable), phase/task scope, exit code,
discovered/executed/passed/failed/skipped counts and a durable raw report path.
Record runId and execution timestamp when available; missing audit metadata alone
is not an acceptance blocker. Use distinct outcomes: PASSED, FAILED, ZERO_TESTS_DISCOVERED, NOT_EXECUTED,
UNVERIFIED, or NOT_APPLICABLE with a reason. Exit zero with "No test matches"
or zero discovered tests is ZERO_TESTS_DISCOVERED, never PASSED. A listed test
file, generated report or agent assertion does not prove successful execution.
Missing required measurements are not zero percent: report NOT_MEASURED and block
the required coverage gate until verified. Show measured numerator/denominator and
percentage per metric, coverage scope, exclusions, configured threshold, tested
revision and report path. Reject measurements for a different revision/scope or
unsupported metrics; do not substitute whole-repository coverage for scoped data.

Preserve the complete evidence in the phase checkpoint and review report. Also
project a `## Quality Gate Evidence` table with `Gate | Decision | Evidence / Justification`:
Tests, Gherkin/Playwright E2E, Code review, Acceptance coverage and Numeric coverage measurement. Use satisfied only
for verified success; missing for required unresolved evidence; unknown for
ambiguous/conflicting/stale evidence; not applicable only with a scope-based
reason. Include report paths and the contract reference. Do not infer zero actual
tests from zero paths recognised by a consumer's Markdown parser.

### Blocking severity and acceptance

Missing required test scenarios, failed required tests, zero discovery,
unexecuted required integration/browser tests, missing required coverage
measurements, and measured coverage below the recorded threshold are
CRITICAL (Must Fix) acceptance blockers. Record an explicit finding code and
remediation. Code review must return NEEDS_CHANGES, never APPROVED or
APPROVED_WITH_NOTES with those findings downgraded to STANDARD. An unsupported
or ambiguous evidence claim is also blocking pending verification; explain that
it is not necessarily a product defect. A legitimate Not Applicable decision is
neither a waiver nor a low-coverage finding. Advisory targets remain advisory.

Phase acceptance must consume the same contract, measurements, scope and revision
as code review. Do not mark the phase accepted or dispatch the next phase while
any applicable required gate is unresolved. After fixes rerun affected configured
commands and obtain a new review covering the changed scope; a narrow diagnostic
rerun never replaces a failing required full suite.

Feature completion reuses the same phase decisions and evidence. Do not reclassify
an accepted documentation/test-only phase as requiring production coverage merely
because the feature contains production code. Separately evaluate explicitly
assigned feature-wide integration/regression gates. Revalidate phase evidence
when a relevant revision, scope or contract change invalidates it, and report the
specific reason rather than silently contradicting earlier acceptance.
Keep previously declared manual qualification and external release dependencies
in release readiness; never relabel an executed failing in-scope gate as external.
Historical approvals are not retroactively rewritten as measured coverage.
