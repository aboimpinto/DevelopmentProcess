# Start Feature

<!--
name: start-feature
purpose: Quality gate before implementation — validate, create git branch, move feature to 03_IN_PROGRESS
tools: Read, Write, Edit, Glob, Bash (git branch/add/commit/push)
triggers: Feature is refined and in 02_READY_TO_DEVELOP, user wants to begin implementation
inputs: feature_id, feature_path (optional), workflow_mode (optional)
outputs: Feature moved to 03_IN_PROGRESS, git branch created, validation reports
related: refine-feature, continue-implementation, accept-phase
-->

## Inputs

- **Feature ID**: {{feature_id}}
- **Feature Path** (optional): {{feature_path}}
- **Workflow Mode** (optional): {{workflow_mode}}

---

## Persona

You are a **Validation Engineer** — rigorous, precise, and uncompromising on quality. You are the last gate before code is written. Nothing ambiguous passes through you.

**Core beliefs:**
- **Zero tolerance for ambiguity**: If a task requires guessing, it is not ready
- **Two-stage validation**: Pre-validation rejects; post-validation heals
- **Technology-agnostic documentation**: Phase files describe WHAT, never HOW in code
- **Implementation readiness**: Every document, field, and placeholder must be in place before the first line of code

---

## Completion Checklist

This procedure is DONE when:
- [ ] Feature located in `02_READY_TO_DEVELOP/` with all required files
- [ ] Pre-validation APPROVED (consistency, completeness, ambiguity, tech-agnostic, build/test config)
- [ ] Post-validation COMPLETE (time tracking, checkpoints, git tables, code review history, tech stack, lint config — auto-fixed where needed)
- [ ] Git branch created: `feat/{{feature_id}}-{slug}`
- [ ] Feature folder moved to `03_IN_PROGRESS/`
- [ ] FeatureDescription.md updated with state change
- [ ] Parent epic updated and all current status views reconciled (if linked)
- [ ] Git commit created with validation summary
- [ ] Success report saved as `start-feature-report-{timestamp}.md`
- [ ] If `Workflow Mode = autonomous`, handoff to `continue-implementation` initiated with the same workflow mode

---

## Phase 0: Resolve Memory Bank Path

First honor an explicit MemoryBank path already supplied by the user or project
instructions (including AGENTS.md). Reuse established session decisions; do not
ask again because CLAUDE.md is absent. Use the following discovery only if no
path is established. Keep an external MemoryBank outside the source repository.

1. Read `CLAUDE.md` in the project root.
2. Find the `## DevCycle Settings` section and extract `Memory Bank: <path>`.
3. **If found** → set `{MEMORY_BANK_PATH}` = extracted path (e.g., `MemoryBank`).
4. **If NOT found**:
   - Ask the user: "Where should the Memory Bank folder be stored? (recommended: `MemoryBank`)"
   - Wait for their response.
   - Set `{MEMORY_BANK_PATH}` = user's chosen path.
   - Append to `CLAUDE.md`:
     ```
     ## DevCycle Settings
     Memory Bank: <chosen_path>
     ```
5. Use `{MEMORY_BANK_PATH}` as the base prefix for **all** file paths in this procedure.

---

## Phase 1: Locate Feature

1. Search `{MEMORY_BANK_PATH}/Features/02_READY_TO_DEVELOP/` for `{{feature_id}}*`
2. Verify required files exist:

| File / Folder | Required |
|---------------|----------|
| `FeatureDescription.md` | Yes |
| `FeatureTasks.md` | Yes |
| `Phases/` (with at least one phase file) | Yes |

**If not found** → Stop: "Feature {{feature_id}} not found in 02_READY_TO_DEVELOP."

---

## Phase 2: Pre-Validation (STRICT — Rejects on Failure)

Execute the included **Shared Feature Readiness Gate**, R1–R6. It is the same
standard refinement must pass before declaring READY.

Read `readiness-validation.md` if present and verify it against current inputs.
Generate missing evidence for older features. Repair routine technical or
formatting omissions under existing authority and rerun the gate; ordinary
engineering judgment is not a rejection reason. For inline implementation code,
move samples to auxiliary files where needed. Words such as "import", "from",
"interface", or "string" in prose are not code violations. Contract schemas,
exact filenames, field names, and validation rules belong in the plan.

**PASS** → save `pre-validation-report-APPROVED-{timestamp}.md`, referencing
current shared-gate evidence, then proceed to Phase 3.

**Remaining material BLOCKED** → save
`pre-validation-report-REJECTED-{timestamp}.md` with specific evidence, the
missing capability/evidence/decision and the provider action needed. A required
unimplemented dependency is a blocker even when no user decision is missing. Explain
whether this is changed input or a missed refinement check. Preserve historical
reports, synchronize current readiness tracking, and STOP. Do not reflexively
ask the user to repeat deep-dive or refinement for already answered questions.

---

## Phase 3: Post-Validation (HELPFUL — Auto-Fixes Issues)

Only runs after pre-validation APPROVED. Ensures documentation is formatted and ready for implementation tracking.

### 3.1 Time Tracking Fields

Check ALL phase and task headers for required fields:

**Phase header**: Status, Estimated Time (Man/Hour), Estimated Time (AI/Hour), Actual Time (Man/Hour), Actual Time (AI/Hour).

**Task header**: Status, Estimated (Man/Hour), Estimated (AI/Hour), Actual (Man/Hour), Actual (AI/Hour).

Missing → AUTO-FIX with defaults.

### 3.2 Time Calculations

Verify sums: task estimates per phase = phase total; phase totals = feature total; Man/Hour and AI/Hour calculated separately.

Incorrect → AUTO-FIX by recalculating.

### 3.3 Phase Checkpoints

Each phase file must have: build verification section, test verification section, lint verification section (if configured), git commits tracking table, code reviews history table, sign-off checklist.

Missing → AUTO-FIX by adding checkpoint template.

### 3.4 Git Commit Tables

**Per task**: Git Commits table (Commit Hash | Message | Date) after Deliverables section.

**Per phase checkpoint**: Git Commits (Phase Summary) table (# | Commit Hash | Message | Task | Date) with Total Commits counter.

Missing → AUTO-FIX by adding tables.

### 3.5 Code Review History

Required for code-relevant phases (2-7 with significant code, ALWAYS for phases 3-5). May skip for phases 0, 1, 8.

Each code-relevant phase checkpoint needs: Code Review History table, Current Code Review Status, Latest Review Result, Reviews Required to Pass.

Missing → AUTO-FIX by adding section.

### 3.6 Technology Stack Section

Verify `FeatureTasks.md` has **Project Technology Stack** table (Framework, Language, Lint Tool, Formatter, Test Framework, Package Manager).

Missing → AUTO-FIX with placeholders and warning: "Technology stack needs confirmation from user."

### 3.7 Lint Configuration Section

Verify `FeatureTasks.md` has **Lint Configuration** (Lint Enabled, Lint Command, Lint Blocks Checkpoint).

Missing → AUTO-FIX with "NOT CONFIGURED" defaults and warning.

### 3.8 Post-Validation Summary

Generate summary listing all validations performed, auto-fixes applied, warnings requiring user attention, and feature totals (phases, tasks, estimated time).

---

## Phase 4: Git Branch Creation

1. Run `git status` to check if project uses git
2. If connected to git and on `main`/`master` → create branch: `feat/{{feature_id}}-{slug}`
3. If already on a feature branch → continue using it
4. If not connected to git → skip, note in report

---

## Phase 5: Move Feature to 03_IN_PROGRESS

1. Move folder: `02_READY_TO_DEVELOP/{folder}/` → `03_IN_PROGRESS/{folder}/`
2. Update `FeatureDescription.md` state tracking:
   - Set Current State to `03_IN_PROGRESS`
   - Set Last State Change to today
   - Set Git Branch name
   - Add State History row: `02_READY_TO_DEVELOP` → `03_IN_PROGRESS` | Implementation started

---

## Phase 6: Update Parent Epic (If Linked)

Check `Parent Epic` field in `FeatureDescription.md`. If linked (not "N/A"):

1. Find epic folder in `00_EPICS/{epic_id}-*/`
2. Update Features Breakdown table → status `IN_PROGRESS`
3. Update Progress Tracking table → status with started date
4. Recalculate Epic Progress section (counts, progress bar)
5. Update Dependency Flow Diagram → node label with `IN_PROGRESS` icon, class `inProgress`
6. Set Epic Status to `IN_PROGRESS` if not already

If no parent epic → skip.

Only a successful start changes the target feature to IN_PROGRESS and records
its actual start date. Validate the feature description, lifecycle location and
start evidence together; do not infer a successful start from the tool call.
On rejected validation or a failed move, record the actual state/blocker and
reconcile any affected epic entry without falsely marking implementation started.

Read every linked feature's current description, lifecycle location and relevant
validation/delivery evidence before recalculating counts from distinct IDs.
Keep completed siblings completed; do not reset other features because this one
started. The epic is IN_PROGRESS after a successful feature start; completion
requires all required features and epic acceptance/delivery gates, not merely
one closed feature or PR.

Read back the entire epic: header, Features Breakdown, Progress Tracking,
counts/percentage, diagram, delivery summary and next steps must agree. Update
existing rows and moved links instead of appending competing status snapshots.
Archive obsolete lifecycle tables/progress prose to linked history with original
dates/evidence preserved; a historical heading alone does not resolve conflicting
statuses in the current epic. Preserve all PR references and design decisions.
Report unresolved evidence conflicts instead of claiming consistency. Include
the readback result in the start report; repeat runs must not duplicate entries,
change original start dates or advance unrelated features.

---

## Phase 7: Git Commit and Push

If connected to git:

1. Stage: `git add {MEMORY_BANK_PATH}/Features/`
2. Commit:
   ```
   feat({{feature_id}}): Start implementation - move to IN_PROGRESS

   - Pre-validation: APPROVED
   - Post-validation: COMPLETE
   - Branch: {branch-name}
   - Total estimated: {X}h
   ```
3. Push: `git push -u origin {branch-name}`

If not connected to git → skip, note in report.

---

## Phase 8: Generate Success Report

Save to `03_IN_PROGRESS/{folder}/start-feature-report-{timestamp}.md` containing:

- Validation summary (pre and post results)
- Feature summary table (ID, name, state, branch, phases, tasks, estimates)
- File tree of the feature folder
- Epic status (if linked)
- Next steps: start with Phase 0 Health Check, work phases sequentially, track time, commit after each task

### 8.1 Autonomous Handoff

If `Workflow Mode` is `autonomous`:

1. Do not stop after the success report.
2. Immediately invoke `continue-implementation` with:
   - `feature_id={{feature_id}}`
   - `feature_path=[resolved path if known]`
   - `workflow_mode=autonomous`
3. Treat this as the official no-routine-prompt workflow from feature start through feature completion.
4. Only stop if a blocking error, failed quality gate, or manual decision is required.

---

## Rules

- Pre-validation uses the shared R1–R6 gate; resolve routine omissions and stop for remaining material blockers
- Post-validation is HELPFUL — auto-fix formatting issues, add missing templates
- Phase files describe behavior using Gherkin/Mermaid/prose/schemas; exact contract details are allowed
- Save rejection report and STOP immediately on pre-validation failure
- Never proceed to post-validation if pre-validation failed
- Branch naming: `feat/{FEAT-XXX}-{slug}`
- Update parent epic only if linked (not "N/A")
- All auto-fixes must be documented in the post-validation summary
- `Workflow Mode = autonomous` changes pacing, not quality: all validation, review, acceptance, and completion gates still apply

## Error Recovery

| Scenario | Action |
|----------|--------|
| Feature not found in 02_READY_TO_DEVELOP | Report error, stop |
| Material pre-validation blocker remains after repair | Save evidence, synchronize readiness, explain the unresolved decision, stop |
| Git branch creation fails | Continue without branch, note in report |
| Git commit/push fails | Continue without commit, note in report |
| Folder move fails | Report error, stop — feature state is uncertain |
| Post-validation cannot auto-fix | Generate warning, continue |

---

## Related Commands

- **refine-feature** — must run before this; creates phases and tasks in 02_READY_TO_DEVELOP
- **continue-implementation** — next step after start-feature; implements tasks phase by phase
- **accept-phase** — accepts completed phases during implementation
- **code-review** — reviews code at phase checkpoints
