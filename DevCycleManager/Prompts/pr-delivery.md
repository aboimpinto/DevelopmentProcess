# Project PR Delivery Policy

This is a client-executed procedure, not a server-side Git/hosting operation.
Apply it alongside Required Dependency Order. A configured PR boundary takes
precedence over generic instructions to continue directly to the next task,
reuse one feature branch, count one commit per task, or publish only at the end.
It never overrides compatibility, testing, review, account or merge requirements.

Apply the section for the invoked lifecycle stage. Deep-dive captures project
preferences, dependencies and questions in the current spec; it does not execute
implementation/publication or create a feature ledger for an epic-only interview.
Refinement creates the feature delivery plan; later tools consume and maintain it.

## Resolve the project policy

1. Locate the source repository from the user's project context, AGENTS.md,
   CLAUDE.md or MemoryBank project index. The feature's external MemoryBank is
   not necessarily the source repository. Read that repository's instructions.
2. Read the explicitly configured PR policy path if provided by those
   instructions; otherwise read `<repository>/.devcycle/PRPolicy.md` if present.
   Paths are resolved by the client, not inside the MCP container. Never use
   another project's policy or the MCP server's own repository settings.
3. Record the policy path, revision/content fingerprint and effective settings
   in the feature's `PRDelivery.md`. Re-read on resume and reconcile changes
   before starting a new unit. Do not silently regroup an already published PR.
4. If no policy exists, retain explicit repository/user conventions; record the
   resulting choice. If none exists, use task-sized meaningful changes as the
   planning recommendation; do not assume a feature-wide PR is required. A
   missing/unreadable explicitly configured policy or contradictory settings
   must be resolved before dependent work, not silently replaced by defaults.

Supported project preferences are a default boundary (`task`, `phase` or
`feature`), whether to evaluate grouping at phase start, grouping criteria,
branching mode (`stacked` or merged-prerequisite), dependency/merge rules, publication command, quality gates and reviewer context.
They are readable instructions, not a new machine-parsed settings API. Do not
invent mandatory numeric PR limits. Respect existing per-commit/file limits.
Use stacked delivery as the normal option for dependent improvements unless an
explicit project/user rule requires merged prerequisites. Earlier predicted PR
counts and approval of functional scope do not impose a maximum PR count. Preserve
an explicit user requirement that actually sets a hard limit; record its source,
exact limit and scope separately from the forecast. If safe units cannot fit that
limit, report the conflict rather than silently exceeding it or combining unsafe
scopes. A changed estimate alone needs no renewed scope approval.

## Delivery properties and existing gates

Keep `PR Boundary: undecided|task|grouped-task|phase|feature|none` and
`PR Decision Basis` in each phase document, linked to `PRDelivery.md`. Refinement
proposes candidate units; phase entry finalizes the boundary from actual work,
cohesion, dependencies, compatibility, validation and expected review size.
No phase name or number automatically selects a PR boundary.

PR grouping does not change phase numbering, lifecycle scope or gate selection.
Reuse existing `needCodeReview` and `needTestCoverage` declarations when present,
including phase.gates records and the applicable shared scope policy. Do not add
competing review flags or infer one flag from the other. When no declarations
exist, retain the project's existing applicable gates. Record the effective
checks/review for each unit; a no-production-review result still requires its
assigned test/assertion verification and declared commands. No phase-scope change
or merge of another workflow change is implied by choosing a PR boundary.
Completed historical phases need no retrofit to adopt delivery planning.

## Refinement: plan independently working changes

For each task, identify its required providers, affected consumers, data/schema
and public contract changes, runtime prerequisites, tests and documentation.
Record provider-before-consumer edges at task and PR-unit level, including
cross-phase dependencies. A unit is one independently reviewable improvement,
possibly including its separately tracked test/documentation tasks.
Prefer small task-level or coherent task-group PRs. Evaluate each phase's actual
work: it may produce zero, one or several PRs. Group across phases only for a
concrete compatibility or cohesion reason, recorded against the member tasks;
neither consecutive phase numbers nor an earlier PR estimate is such a reason.
For every proposed boundary, explain its purpose, included tasks, affected
consumers (or an evidenced none), dependencies, required tests/docs and why its
resulting tree is safe to merge after its prerequisites. A dependent unit can be
independently reviewed without being independent of its predecessor's code.

Do not force a breaking model change into a separately named phase merely because
of its label. Choose either a backward-compatible foundation followed by a
consumer switch and later cleanup, or move the breaking portion alongside its
production consumers, migration/compatibility work and tests in one bounded
unit. Update actual task/phase ownership and preserve traceability. Do not leave
an intermediate merge broken or postpone required tests to the Testing phase.
Resolve cycles by splitting/reordering work; never use feature-sized accumulation
to conceal an invalid dependency order. Unsupported scope changes need user input.

Create `PRDelivery.md` beside FeatureTasks.md during refinement and link it from
FeatureTasks.md and planning-analysis-report.md. Readiness requires every planned
source change to have an explicit unit or safe candidate grouping, dependencies,
compatibility rationale and validation. Documentation/verification-only tasks
with no source-repository changes record N/A; do not manufacture empty PRs.

### PR forecast produced by refinement

When delivery is not one PR per feature, produce a per-phase PR forecast as part
of refinement, before the READY gate. It is local planning, independent of whether
GitHub synchronization is enabled. Do not wait for implementation to define it.
For feature-level delivery, record the single feature unit (or zero if there is
no repository change), instead of inventing one PR for every phase.

Every candidate unit has a stable feature-scoped ID, proposed PR title, short
reviewer-facing description, member task IDs, owning/counting phase, cross-phase
references, grouping rationale, dependency/predecessor units, expected artifact
scope, compatibility and required validation. No real PR number, URL or branch
SHA exists until observed. Assign each source-changing task to exactly one active
unit (or explicitly split it into traceable sub-tasks); no-diff tasks have N/A.

Publish a phase summary in PRDelivery.md and FeatureTasks.md:

| Phase | Actual work / PR decision | Planned unit IDs and titles | Estimated PR count | Dependencies |
| --- | --- | --- | --- | --- |
| Actual phase ID | Property-based task/group/phase/none rationale | Stable IDs with short descriptions below | Distinct units owned by this phase | Predecessor units |

The feature total counts distinct active units exactly once, including units
already published/merged; superseded attempts remain in history and do not inflate
the current forecast. Show remaining unopened units separately. A unit spanning
phases is counted only in its owning phase, referenced elsewhere. Zero requires
an explicit no-repository-diff reason; unknown scope is unknown, not zero.

Record the forecast date, assumptions, confidence/uncertainties and reasons it
may change. It is an estimate, not a fixed delivery promise or a numeric cap.
Re-evaluate at phase entry and when scope/dependencies change. Preserve mappings
for published units; record replacements/splits explicitly rather than recycling
their IDs. The final refinement summary includes the per-phase and total estimate.
After successful refinement, configured sync-feature publishes this local plan
to the existing issue. Publication later replaces the planned entry with the real
PR link while preserving its unit ID, title/intent and history.

### Revised forecasts and commit feasibility

Keep PR grouping separate from commit feasibility. Splitting a PR does not waive
per-commit path/line/file-size limits, compiling intermediate commits or required
hooks. For a staging problem, record the exact blocked unit/task, violated limit,
evidence, proposed lawful staging and any unresolved authority. Check dependency
edges to identify which consumers are blocked and whether independent work can
proceed under the existing readiness/start gates. Do not use a unit-local staging
problem as a reason to combine unrelated scopes. If a feature-wide readiness gate
still blocks all implementation, name that gate and explain why; do not silently
waive it, mark READY or imply that every unit has the same technical problem.

When units split or regroup, reconcile phase records, FeatureTasks.md,
FeatureDescription.md, PRDelivery.md and parent EPIC delivery totals together.
Preserve task/criterion/test links, one counting owner per active unit and actual
PR identities. Record old-to-new unit mappings, date and reason; retain superseded
units as history, excluded from current totals. Recompute the parent total from
distinct feature/unit pairs, preserving unrelated sibling forecasts and states.
Show total, unopened remainder and actual PRs separately; do not count a superseded
aggregate as another unit. Reconcile configured GitHub synchronization for both
feature and parent forecasts, or record disabled/SYNC_PENDING with the exact reason.
Revised planning does not by itself change readiness or imply implementation.

## Phase entry: decide grouping from the actual work

Before task execution in each phase, evaluate the default boundary
against its actual tasks and the refined dependency plan. Record the chosen
task/grouped-task/phase boundary, member task IDs, rationale, expected files and
approximate diff/commit scope, compatibility evidence and checks. This is a
decision for this feature/phase, not a permanent exception for a phase number.

If tasks produce only verification evidence or external MemoryBank documents,
record `PR Boundary: none`, task evidence and N/A delivery. Do not manufacture
empty source PRs or commits for checkpoints, documentation or other no-diff work.
If versioned repository documentation/configuration changes, follow its delivery
rules even without executable code. Decide from actual artifacts, not phase labels.

A whole-phase PR is appropriate only when allowed by the project policy and
the work is one small coherent change with all required consumers/tests/docs
included. Otherwise keep task-sized units. A phase name does
not establish safety. Integration tests for one end-to-end behavior, including
their shared fixtures and assertions, may form one phase-end PR rather than one
PR per test. Unrelated test groups may need separate PRs. Evaluate the same
cohesion, dependencies, size and risk for every phase, not a list of named
exceptions. Do not defer tests required by an earlier production change into a
later integration-test PR. Make routine decisions under existing authorization;
explain them briefly without asking for another approval by default.

Re-evaluate if scope grows, a breaking change is found, or dependencies change.
Update the plan before more implementation; split unsubmitted work rather than
adding unrelated tasks to an open PR. A runtime grouping decision may refine
the plan but must not bypass readiness or dependency gates. If a unit would
span later phases, explicitly reorder the necessary work or use compatible
stages; do not create a phase-acceptance/dependency deadlock.

## Delivery record

Keep one row per unit, using stable IDs such as `PRU-01` (not invented GitHub IDs):

| Unit | Tasks / phase | Improvement and grouping rationale | Depends on | Compatibility and validation | Branch / base SHA / tested head | Review evidence | PR / state / merge evidence |
|---|---|---|---|---|---|---|---|
| PRU-01 | Actual task IDs | One observable improvement | Unit IDs or none | Required checks and actual results | Actual refs and exact base SHA when known | Report for tested revision | Actual URL/state or not opened |

For each proposed unit also retain this boundary explanation (link detailed
inventories rather than duplicating them):

| Boundary property | Required record |
| --- | --- |
| Purpose and scope | Proposed title/description, member task IDs and affected files/artifacts |
| Consumers and cohesion | Affected consumers, why these tasks belong together, concrete reason for any cross-phase grouping |
| Dependencies and safe tree | Predecessor units, inherited requirements, compatibility strategy and why the resulting tree is safe after prerequisites |
| Tests/docs and gates | Required tests, documentation and scoped review; execution owner and actual evidence when available |
| Publication and continuation | Publish at this unit's gates; next unit's separate branch and intended PR base |
| Commit feasibility | Applicable limits, staging plan or exact blocker, independent-work assessment and any feature-wide gate |

For stacks also record stack ID/order, predecessor unit/PR, current PR base branch
and SHA, intended final merge destination, last published head and restack status.
Save the old predecessor boundary before it is amended, stamped, rebased or deleted.
Review evidence covers the incremental base..head diff and verifies required
ancestor behavior in the complete consumer revision; it does not reassign ancestor
commits to the child's PR. Keep original-to-restacked/merged revision mappings.

Track implementation separately from delivery: `PLANNED`, `IMPLEMENTING`,
`READY_FOR_PR`, `PR_OPEN`, `AWAITING_MERGE`, `MERGED`, or `BLOCKED`; use N/A
with a reason for tasks without a repository diff. An implemented task is not
merged delivery. Keep closed-unmerged PRs as history with their replacement or
disposition. Each task must be covered exactly once by the current plan, or
explicitly split into traceable parts; preserve historical entries separately.

## Mandatory boundary check: after each task, before the next

Read the current unit and effective phase decision. After the final task in a
phase, satisfy its existing phase-end gates before publishing a due PR. Evaluate
in this order:

| Condition | Action |
|---|---|
| Prerequisite for the next task or currently due compatibility/test/review gate missing/failing | BLOCKED; repair it, no PR-ready claim |
| More tasks remain in the explicitly chosen unit | Continue only that unit's next dependency-ready task |
| No source-repository diff, with all work/evidence recorded | Record N/A; no empty commit or PR |
| Unit complete and required gates pass, no PR exists | READY_FOR_PR: report "This unit is ready for a PR" and publish through the project's required workflow within current authority |
| PR already exists for this unit/branch/head | Read it back; update only that unit, never create a duplicate |
| PR open, CI/review pending or changes requested | Record the condition; address fixes in this unit. With stacked policy, continue dependency-ready work on its own child branch; review failures that invalidate a prerequisite block that consumer |
| PR merged and merge verified | Record URL/base/head/merge/date; reconcile and restack existing descendants, update their PR bases and validation; update feature/issue inventory |

Before READY_FOR_PR, inspect the complete diff against the intended base for
scope creep, independently working behavior, compatibility and required tests.
Run project-required checks and the applicable review/verification of this exact
unit. Use `code-review` with `delivery_unit_id` only for required production review;
test-only work verifies assertions against its assigned behavior without adding a
production-code review. Existing phase-level review obligations still apply.
Small commits alone do not make the combined PR small. Use as few meaningful
commits/files as practical; do not squash past repository limits or fake evidence.

Use a distinct branch for each unit. The project/user branching policy determines
the next base. For **stacked PRs**, the root branches from the final delivery branch;
a dependent unit branches from its predecessor's published, PR-stamped head and
targets that predecessor branch. Continue while it is under review when required
code and verification are present in the consumer revision. An open PR alone is
neither a blocker nor proof of dependency availability. Independent work can form
another stack. Never pile the next unit onto the predecessor's review branch.

After upstream review fixes, rebases or publication stamping, reconcile every
descendant. Use each recorded old base SHA to replay only its own commits onto
the new predecessor, bottom-up (for Git: `git rebase --onto <new-base> <old-base-sha>
<child>`). Inspect conflicts and incremental diffs; rerun affected validation and
review, then publish with a lease on the observed remote head under existing
authority. Never silently overwrite another person's work or treat pre-restack
approvals/checks as current evidence. The server performs no rebase or push.

Merge in dependency order: merge the root to the final delivery branch, restack
its child onto that branch and retarget the existing child PR before merging it.
Repeat. Do not merge a child into an unmerged predecessor to declare it delivered.
Retain old boundaries until descendants are reconciled; verify hosting rather
than assuming retargeting after branch deletion. A rejected/closed-unmerged
prerequisite blocks dependent delivery until repaired or replanned. Publication
helpers must scope validation, descriptions and PR stamping to the selected base,
not the whole stack; predecessor commit identities/PR ownership remain intact.

If a project explicitly requires merged prerequisites instead, honor that rule;
planning and independent work may continue separately. Do not infer this rule
merely from task-sized PRs, worktree use, phase acceptance or default-branch names.
Never merge automatically merely because a unit is ready or the workflow is
autonomous. Respect the user's merge authority and branch protections.

On resume, reconcile branch, HEAD, PR metadata and the record before taking any
publication action. A failed create/push may already have published something;
check hosting first. Missing access is BLOCKED/unknown, not "no PR exists".
Record a precise restart point when waiting; this recipe installs no watcher.

## Reviewer context and lifecycle completion

Each PR explains the problem, why this change is needed, before/after behavior,
feature/phase/task IDs, grouping rationale, dependencies and actual validation.
Use the repository template and public issue/source links. Keep broader design
context and the task-to-PR sequence in the feature issue; a local MemoryBank link
is not reviewer-accessible context. Partial delivery uses reference links, not
closing keywords for unfinished features. Keep every associated PR in the
feature inventory, including supporting fixes, immediately upon publication.
Update remote issue text only within authorization; record pending updates if
access is unavailable. Never send unsolicited review messages.

At phase acceptance, verify all units due at its configured boundary have been
published and their required delivery conditions met. Under a stacked policy,
phase acceptance does not wait for all mainline merges unless that boundary
explicitly requires them; keep accepted implementation and pending delivery distinct.
An explicitly planned
later boundary may remain pending, clearly recorded; it is not merged delivery.
Final checkpoints reconcile integrated verification and existing delivery records.
Do not defer completed earlier units' publication to the final checkpoint or create
an extra aggregate PR. Keep fresh integrated checks and required final merges as
completion obligations; they do not impose a blanket publication wait on units
whose own applicable gates pass.
Do not open an additional aggregate phase PR over already delivered task PRs.
At feature completion, reconcile every unit and PR with hosting evidence and
verify all project-required merges through to the final delivery branch. A child
PR merged only into an unmerged predecessor is not final delivery. Do not archive a feature with required
delivery pending, create a duplicate feature PR, or reopen completed features
just to retrofit this plan. Update epic progress using existing consistency rules.
