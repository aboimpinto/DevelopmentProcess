## Adaptive Feature Phase Planning

Policy version: devcycle-feature-phases/v1.

### Required structure, flexible implementation

Every newly refined feature includes exactly one Initial Checkpoint, one Planning
phase, and one Final Checkpoint. The order is Initial Checkpoint -> Planning ->
feature-specific implementation phases -> Final Checkpoint. Choose the intervening
phases from concrete deliverables, dependencies, risks and useful verification
boundaries. There is no fixed phase count or required data/business/UI layer split.
Omit a UI or other implementation phase with no work; do not generate an empty
phase just to mark it NOT_APPLICABLE or SKIPPED. A small change can use one
implementation phase; larger work may use several. Do not invent implementation
work when the accepted deliverable is itself a planning document.

Record `Phase Role` in each phase document and a matching `Role` column in
FeatureTasks.md: `initial_checkpoint`, `planning`, `implementation`, or
`final_checkpoint`. Roles describe required planning responsibilities; they do not
select a different executor or override needCodeReview/needTestCoverage. Keep the
existing phase.gates exchange unchanged: roles belong to the phase documents and
feature summary, not new fields in that strict JSON envelope. Phase identifiers
and filenames remain stable references, not rules for choosing work or gates.
Number phases for navigation if useful; never assume particular numbers for roles.

Refinement declares executable tasks, independent gate flags, dependencies and
verification references for these responsibilities. All phases run through the
same task execution and acceptance loop. Required checkpoint commands remain
required even when both flags are false. A feature cannot waive the three required
roles by marking them SKIPPED. Document why the chosen implementation structure
fits this feature and map every acceptance obligation to an owner.

### Initial Checkpoint: establish the baseline

Declare the project's build, lint when configured, and all project-required test
suites in TestPlan, with exact commands, working directories, setup and success
criteria. Include all configured baseline suites, not only tests touched by the
feature. Resolve wrappers and suite selection so a focused subset, discovery-only
run, zero selected tests or skipped required suite cannot impersonate a green run.
For a project without an applicable compiler/build or test suite, record explicit
repository-backed non-applicability and the applicable verification alternative;
missing configuration or unavailable infrastructure is not non-applicability.

Execute the baseline before feature implementation: build must have zero errors
and zero warnings, configured lint must be clean, and all required tests must pass.
Record commands, actual outcomes, source revision/tree, relevant environment and
durable reports. Refinement only plans these checks; it must not run them or mark
their outcomes PASSED. Start Feature hands off to this declared work through the
common execution loop; a READY plan is not evidence of a green baseline.

A failed baseline blocks progression to Planning and feature implementation.
Diagnose and repair within existing authority, then rerun affected checks and
establish a fully green baseline. Record prerequisite repairs as owned tasks at
this boundary with their applicable review/coverage obligations; revise the scope
and flags if production or test changes are needed. Do not defer baseline repair
to an implementation phase that itself depends on this checkpoint. Preserve failed
evidence and repair results. If repair needs unavailable resources or wider
authority, retain the blocker rather than proceeding or claiming a pass.
Pre-existing failures and warnings are never an acceptance waiver. A later failure
requires investigation of code, tests and environment, not an unsupported claim
that it existed before the feature.

### Planning: decide how to implement

After the baseline passes, inspect current implementation and produce the canonical
`planning-analysis-report.md`. Go beyond restating requirements. Record:
- Files/modules to create, modify, move or delete, including old/new paths for moves.
- Existing architecture, coding guidelines and concrete pattern examples to follow.
- Relevant lessons learned, previous traps and how this approach avoids them.
- Technical approach, dependency order, compatibility risks and integration points.
- Tests and checks proving preserved behavior and the new acceptance criteria.
- Changes needed to the proposed implementation phases, tasks and PR delivery units.

Planning validates and details refinement's proposed structure. Update affected
phase documents, FeatureTasks.md, TestPlan/criterion links, gate declarations and
PRDelivery.md together when repository findings change the approach. Preserve
accepted intent, stable identities, completed evidence and actual PR links. Record
old/new ownership and reasons; do not reset completed work or add a human-sign-off
task. Material unresolved product/scope/authority decisions follow the existing
escalation rules. Planning is document work, not an opportunity to start coding.
Dependent tasks read this report; they update material decisions in place instead
of creating separate planning processes for each numbered phase.

### Final Checkpoint: verify the integrated result

Publish completed delivery units when their own applicable gates pass; do not
hold them for this checkpoint. Dependent implementation normally continues on
separate stacked branches from published, PR-stamped predecessor heads while
review proceeds, subject to explicit project policy and verified prerequisites.
This checkpoint reconciles existing delivery records and creates no extra
aggregate PR. Evidence-only work has zero PRs because it has no repository diff,
not because of its phase name. Commit limits and readiness gates still apply.

Declare fresh execution of the project's build, configured lint and all
project-required test suites against the final integrated source after implementation
and applicable required merges. Build has zero errors and warnings; configured
lint is clean; all required tests pass. Include feature acceptance and integration
checks at their declared boundary and retain linked EPIC E2E ownership. Baseline
results and focused development runs cannot replace this final verification.

Record the final revision/tree, relevant environment, commands and report evidence.
Relevant source, tests, configuration, dependency or environment changes invalidate
affected results and require rerunning those checks before completion. A timestamp
or report rewrite alone is not fresh execution. Preserve valid independent results.
Reuse valid reviews and coverage assessments for unchanged scope; do not create
duplicate authoring/review loops merely because this is the final checkpoint.
Feature completion can reuse this verified final-checkpoint evidence for unchanged
inputs instead of automatically running everything yet again. Missing, failed or
invalidated required evidence blocks completion and returns to the responsible
repair task. Neither an empty diff nor both flags false waives these obligations.

### Readiness, progress and existing features

Before READY, Start Feature, phase acceptance and feature completion, reconcile
role assignments, dependencies, declared checks and criterion ownership. Initial
Checkpoint is first, Planning follows it before feature implementation, and Final
Checkpoint depends on every required implementation deliverable. Compute phase
counts, current/next phase, progress and PR forecasts from the actual phase list;
never use a fixed denominator or assume the final phase has a specific number.
Validate planned obligations at refinement/start; require actual evidence at their
execution and acceptance boundaries. Planning and checkpoints cannot be omitted
or skipped merely because the feature is small or has no UI.

For existing READY or IN_PROGRESS features, reconcile at the next authorized
refinement/start/resume boundary, not by rewriting historical artifacts at server
deployment. Map existing responsibilities and evidence to roles based on actual
content, never names/numbers alone; retain IDs and valid work. Remove obsolete
empty implementation placeholders from the active plan with a recorded rationale
and preserved history. If required work is missing, add explicitly owned tasks or
phases and update references. Never fabricate a pre-change baseline after coding
has begun: record that historical gap, establish the current baseline before further
work, and retain the limitation in final evidence. Do not reopen completed features
solely to retrofit the new structure. This server delivers planning instructions;
the client verifies artifacts and executes them locally.
