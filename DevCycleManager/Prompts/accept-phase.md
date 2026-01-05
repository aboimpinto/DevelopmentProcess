# Accept Phase - MCP Procedure

You are executing the **Accept Phase** procedure for the DevCycleManager. This procedure formalizes user acceptance of a completed phase, updates all documentation with final metrics, and previews the next phase.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Phase Number**: {{phase_number}}
- **Feature Path** (if provided): {{feature_path}}

---

## Procedure Overview

This procedure handles **USER-CENTRIC** phase acceptance:

1. **Validates checkpoint was filled** (not NotStarted)
2. **Validates phase is awaiting acceptance** (status = AWAITING_USER_ACCEPTANCE)
3. **Validates technical requirements** (build, tests, code review)
4. **Handles incomplete tasks** (with user justification)
5. **Marks phase as COMPLETED** in all files
6. **Updates time tracking** with actual vs estimated
7. **Creates git commit** with achievements
8. **Previews next phase** (without starting it)

**IMPORTANT**: This procedure does NOT automatically start the next phase. The user must explicitly run `continue-implementation` to proceed.

---

## Step 0: Locate and Validate the Feature

### Find the Feature
Search for the feature folder in `MemoryBank/Features/03_IN_PROGRESS/`:

1. Look for `{{feature_id}}*` folders in `03_IN_PROGRESS/`
2. If not found: Stop and report error

### Find the Phase File
Locate the phase file:
- `Phases/phase-{{phase_number}}-*.md`

**If phase file not found**: Stop and report available phases.

### Read Required Files
1. **Phase file**: `Phases/phase-{{phase_number}}-*.md`
2. **FeatureTasks.md**: For Phase Summary table
3. **FeatureDescription.md**: For feature context
4. **start-feature-report-*.md**: For validation report

---

## Step 1: Validate Checkpoint Was Filled

**Read the checkpoint section** in the phase file and check for checkpoint status:

```markdown
### Phase Checkpoint

**Checkpoint Status**: {NotStarted | InProgress | Complete}
```

### If Checkpoint Status is "NotStarted" or Missing

```markdown
❌ Cannot Accept Phase {{phase_number}}

**Checkpoint Status**: NotStarted

The checkpoint has not been filled. This typically happens when:
- Phase completion (build/test/review) was not run
- The continue-implementation procedure was not completed

**Required Before Acceptance**:
- Build verification results
- Test coverage metrics
- Code review status (if required)
- Time tracking summary

**Next Steps**:
Run `continue-implementation` to complete phase requirements first.
```

**STOP** - Do not proceed with acceptance.

### If Checkpoint Status is "InProgress" or "Complete"

Proceed to Step 2.

---

## Step 2: Validate Phase Is Awaiting Acceptance

**Read the phase file header** and check status:

```markdown
**Status**: {status}
```

### If Status is NOT "AWAITING_USER_ACCEPTANCE"

```markdown
❌ Cannot Accept Phase {{phase_number}}

**Current Status**: {current_status}
**Expected Status**: AWAITING_USER_ACCEPTANCE

**Reason**: Phase must complete all technical requirements first.

**What's Missing** (check checkpoint section):
- [ ] All tasks completed
- [ ] Build passing (0 errors, 0 warnings)
- [ ] All tests passing (100%)
- [ ] Code review APPROVED (if required)
- [ ] Checkpoint section filled

**Next Steps**:
Run `continue-implementation` to complete phase requirements.
```

**STOP** - Do not proceed with acceptance.

### If Status IS "AWAITING_USER_ACCEPTANCE"

Proceed to Step 3.

---

## Step 3: Validate Technical Requirements (COMPREHENSIVE)

**Read checkpoint section** and verify ALL of the following:

### 3.1 All Tasks Completed
**Check ALL tasks in the phase file:**
- Count tasks with status `[COMPLETED]`
- Count tasks with status `[PENDING]`, `[IN_PROGRESS]`, `[BLOCKED]`

**Validation**:
- ✅ All tasks are `[COMPLETED]` or `[SKIPPED]` (with justification)
- ❌ Any task is still `[PENDING]`, `[IN_PROGRESS]`, or `[BLOCKED]`

### 3.2 Git Commits Tracked (CRITICAL)

**Check each task's Git Commits table:**
```markdown
**Git Commits:**
| Commit Hash | Message | Date |
|-------------|---------|------|
| abc1234 | feat(FEAT-001): ... | 2024-01-15 |
```

**Validation**:
- ✅ Every task with code changes has at least one commit in its table
- ❌ Any task has an empty Git Commits table (except Phase 0, 1, 8 or documentation-only tasks)

**Check the Phase Checkpoint's Git Commits (Phase Summary):**
```markdown
### Git Commits (Phase Summary)

| # | Commit Hash | Message | Task | Date |
|---|-------------|---------|------|------|
| 1 | abc1234 | ... | Task 2.1 | 2024-01-15 |

**Total Commits in Phase**: 4
```

**Validation**:
- ✅ Git Commits (Phase Summary) table exists with entries
- ✅ Total Commits in Phase is greater than 0 (for code phases)
- ❌ Table is missing or empty for code-relevant phases

### 3.3 Build Verification
```markdown
- [x] Build succeeds with 0 errors, 0 warnings
```
- ✅ Build passing with 0 errors, 0 warnings
- ❌ Build has errors or warnings

### 3.4 Lint Verification (If Configured)

**Check if lint is configured** (read FeatureTasks.md Lint Configuration):
- If **Lint Enabled: Yes** and **Lint Blocks Checkpoint: Yes**:
  ```markdown
  - [x] Lint passes with 0 errors, 0 warnings
  ```
  - ✅ Lint passing
  - ❌ Lint has errors or warnings

### 3.5 Test Coverage
```markdown
- [x] All tests passing (100%)
```
- ✅ All tests passing
- ❌ Any test failures or skipped tests without justification

### 3.6 Code Review (CRITICAL for Code-Relevant Phases)

**Determine if code review is required:**

**Code review REQUIRED for:**
- Phase 2 (Data Layer) - If contains business logic
- Phase 3 (Business Logic) - **ALWAYS**
- Phase 4 (Presentation Logic) - **ALWAYS**
- Phase 5 (User Interface) - **ALWAYS**
- Phase 6 (Integration) - If contains significant code
- Phase 7 (Testing & Polish) - If contains new code

**Code review may be SKIPPED for:**
- Phase 0 (Health Check)
- Phase 1 (Planning & Analysis)
- Phase 8 (Final Checkpoint)
- Phases with ONLY DTOs, config, or documentation

**If code review IS required, verify Code Review History:**

```markdown
#### Code Review History

| # | Date | Status | Report | Notes |
|---|------|--------|--------|-------|
| 1 | 2024-01-15 | NEEDS_CHANGES | ... | 3 issues |
| 2 | 2024-01-16 | APPROVED | ... | All fixed |

**Current Code Review Status**: APPROVED
**Latest Review Result**: APPROVED
**Reviews Required to Pass**: 2
```

**Validation**:
- ✅ Code Review History table exists with at least one entry
- ✅ **Latest Review Result** is `APPROVED` or `APPROVED_WITH_NOTES`
- ❌ Code Review History is empty or missing
- ❌ Latest Review Result is `NEEDS_CHANGES`
- ❌ No Code Review History for a code-relevant phase

### 3.7 Generate Validation Report

```markdown
## Phase {{phase_number}} Acceptance Validation

### Requirements Checklist

| Requirement | Status | Details |
|-------------|--------|---------|
| All Tasks Completed | ✅/❌ | {X}/{Y} tasks completed |
| Git Commits Tracked (Tasks) | ✅/❌ | {X} tasks have commits tracked |
| Git Commits Summary | ✅/❌ | {X} commits in Phase Summary |
| Build Clean | ✅/❌ | 0 errors, 0 warnings |
| Lint Clean | ✅/❌/N/A | {status or "Not configured"} |
| Tests Passing | ✅/❌ | {X}/{Y} tests passing |
| Code Review | ✅/❌/N/A | {status} |

**Overall Validation**: ✅ PASSED / ❌ FAILED
```

### If Any Requirement Fails

```markdown
❌ Cannot Accept Phase {{phase_number}} - Requirements Not Met

**Failed Requirements**:

{For each failed requirement:}
### {Requirement Name}
**Status**: ❌ FAILED
**Expected**: {what was expected}
**Found**: {what was found}
**How to Fix**: {specific steps}

---

**Summary of Issues**:
1. {Issue 1}
2. {Issue 2}
3. {Issue 3}

**Next Steps**:
1. Address all failed requirements listed above
2. Run `continue-implementation` to complete missing items
3. Re-run `accept-phase` when all requirements are met
```

**STOP** - Do not proceed with acceptance.

### If All Requirements Pass

Proceed to Step 4.

---

## Step 4: Check for Incomplete Tasks

**Scan all tasks** in the phase file and count by status:
- `[COMPLETED]` - Done
- `[IN_PROGRESS]` - Not done
- `[PENDING]` - Not done
- `[BLOCKED]` - Not done
- `[SKIPPED]` - Already handled

### If ALL Tasks are COMPLETED or SKIPPED

Proceed to Step 6 (Mark Phase as COMPLETED).

### If ANY Tasks are Incomplete

Present options to user:

```markdown
⚠️ Phase {{phase_number}} Has Incomplete Tasks

**Incomplete Tasks** ({count}):
{List each incomplete task with status}

**Options**:
1. **Continue working** - Return to implementation to complete tasks
   - Run `continue-implementation` to resume
   - Phase remains in AWAITING_USER_ACCEPTANCE status

2. **Accept anyway** - Mark tasks as SKIPPED and complete phase
   - Requires justification for each skipped task
   - Tasks will be marked [SKIPPED]
   - Justification documented in checkpoint

**Your choice**: Please specify 1 or 2
```

**STOP** - Wait for user response.

---

## Step 5: Handle Skipped Tasks (If User Chooses Option 2)

### Request Justification

```markdown
**Justification Required**

Please provide a reason for skipping these tasks:
{List incomplete tasks}

Example justifications:
- "Requirements changed - feature no longer needed"
- "Task moved to next phase for better workflow"
- "Discovered task was duplicate of existing work"
- "Will be addressed in future iteration"

Your justification:
```

**STOP** - Wait for user justification.

### After Receiving Justification

1. **Update each incomplete task** to `[SKIPPED]`:
   ```markdown
   ### Task {N}.{M}: {Task Name}
   **Status**: `[SKIPPED]`
   **Skip Reason**: {User's justification}
   **Skipped On**: {timestamp}
   ```

2. **Add to checkpoint section**:
   ```markdown
   ### Skipped Tasks

   **Tasks Skipped**: {count}
   **Justification**: {User's justification}

   | Task | Original Status | Skip Reason |
   |------|----------------|-------------|
   | {task} | {status} | {justification} |
   ```

3. Proceed to Step 6.

---

## Step 6: Mark Phase as COMPLETED

### 6.1: Get Completion Timestamp

Record the current date/time for all updates.

### 6.2: Calculate Time Metrics

From the phase file and tasks, calculate:

1. **Phase Started**: (from phase header)
2. **Phase Completed**: (current timestamp)
3. **Total Elapsed Time**: Completed - Started
4. **Total Active Work Time**: Sum of all task durations
5. **Estimated Time**: (from phase header)
6. **Variance**: ((Estimated - Actual) / Estimated) × 100%

**Time Tracking Format**:
```markdown
**Time Summary**:
- Estimated: {X}h
- Actual: {Y}h
- Variance: {+/-Z}% ({ahead of/behind} schedule)
```

### 6.3: Update Phase File Header

```markdown
OLD:
**Status**: AWAITING_USER_ACCEPTANCE
**Phase Completed (Elapsed)**: -

NEW:
**Status**: COMPLETED
**Phase Completed (Elapsed)**: {timestamp}
**Total Elapsed Time**: {elapsed}
**Total Active Work Time**: {active_work}
```

### 6.4: Update Checkpoint Status

```markdown
OLD:
**Checkpoint Status**: InProgress

NEW:
**Checkpoint Status**: Complete
```

### 6.5: Add Phase Completion Details to Checkpoint

```markdown
### Phase Status Update

**Checkpoint Status**: Complete
**Phase Status**: COMPLETED
**User Acceptance**: [x] Accepted by user on {timestamp}
**Phase Completion Date**: {timestamp}

**Phase Achievements**:
- {Key accomplishment 1}
- {Key accomplishment 2}
- {Key accomplishment 3}

**Quality Metrics**:
- Build: {status}
- Tests: {passed}/{total} passing ({percentage}%)
- Code Review: {status}

**Time Metrics**:
- Estimated: {estimated}
- Actual: {actual}
- Variance: {variance}
```

### 6.6: Save Phase File

---

## Step 7: Update FeatureTasks.md

### 7.1: Update Phase Summary Table

Find the row for Phase {{phase_number}} and update:

```markdown
OLD:
| {{phase_number}} | {Phase Name} | {Est Man} | {Est AI} | AWAITING_USER_ACCEPTANCE | {Actual Man} | {Actual AI} | {phase file} |

NEW:
| {{phase_number}} | {Phase Name} | {Est Man} | {Est AI} | COMPLETED | {Actual Man} | {Actual AI} | {phase file} |
```

### 7.2: Update Overall Progress (If Section Exists)

```markdown
**Phases Completed**: {X}/{Total} ({percentage}%)
**Total Time Spent**: {sum of actual times}
**Overall Variance**: {percentage vs total estimated}
```

### 7.3: Save FeatureTasks.md

---

## Step 8: Update start-feature-report

If `start-feature-report-*.md` exists, update the phase status:

```markdown
### Phase Status

| Phase | Status | Completed |
|-------|--------|-----------|
| Phase 0 | COMPLETED | {date} |
| Phase 1 | COMPLETED | {date} |
| ...
| Phase {{phase_number}} | COMPLETED | {timestamp} |
| Phase {N+1} | PENDING | - |
```

---

## Step 9: Create Git Commit

### 9.1: Stage All Changes

```bash
git add -A
```

### 9.2: Create Comprehensive Commit Message

```
feat({{feature_id}}): Complete Phase {{phase_number}} - {Phase Name}

Phase {{phase_number}} Achievements:
- {Key accomplishment 1}
- {Key accomplishment 2}
- {Key accomplishment 3}

Implementation Summary:
- Tasks Completed: {count}
- Tasks Skipped: {count} (if any)
- Build: {status}
- Tests: {passed}/{total} passing
- Code Review: {status}

Time Metrics:
- Estimated: {estimated}
- Actual: {actual}
- Variance: {variance}

{If tasks skipped:}
Skipped Tasks:
- {Task}: {Justification}

Generated with Claude Code
```

### 9.3: Commit

```bash
git commit -m "{commit message}"
```

### 9.4: Get Commit Hash

Record the commit hash for the summary.

---

## Step 10: Push to Remote (If Git Connected)

### 10.1: Push Changes

```bash
git push origin {branch-name}
```

### 10.2: Handle Push Failures

If push fails:
```bash
git pull --rebase origin {branch-name}
# Resolve conflicts if any
git push origin {branch-name}
```

### 10.3: Record Push Status

- If successful: Record "Pushed to Remote: Yes"
- If failed: Record "Pushed to Remote: No - {reason}"

---

## Step 11: Preview Next Phase

### 11.1: Find Next Phase

- Next phase number: {{phase_number}} + 1
- Read next phase file: `Phases/phase-{N+1}-*.md`

### 11.2: Extract Next Phase Information

- Phase name and description
- Estimated time (Man/Hour and AI/Hour)
- List of tasks (first 5)
- Prerequisites status

### 11.3: Check If Feature Is Complete

If there is no next phase (all phases completed):
- This is the final phase
- Skip next phase preview
- Proceed to Feature Completion (Step 12)

### 11.4: Generate Next Phase Preview

```markdown
## Next Phase Preview: Phase {N+1} - {Phase Name}

**Phase Number**: {N+1}
**Description**: {Description from phase file}

**Estimated Time**:
- Man/Hour: {estimate}
- AI/Hour: {estimate}
- Total: {total}

**Key Tasks** (showing first 5):
1. Task {N+1}.1: {Description}
2. Task {N+1}.2: {Description}
3. Task {N+1}.3: {Description}
4. Task {N+1}.4: {Description}
5. Task {N+1}.5: {Description}

**Prerequisites**:
- [x] Phase {{phase_number}} completed
- {List other prerequisites}

**Phase {N+1} Status**: PENDING (ready to start)

---

## To Start Phase {N+1}

**Run the MCP command**:
```
continue-implementation (feature_id: {{feature_id}})
```

This will:
1. Mark Phase {N+1} as IN_PROGRESS
2. Start with Task {N+1}.1
3. Follow project coding standards
4. Run code review at phase completion
5. Wait for your acceptance when ready

**Remember**: Phase transition is **USER-CONTROLLED**. Phase {N+1} will NOT start automatically.
```

**IMPORTANT**: Do NOT:
- Change next phase status to IN_PROGRESS
- Start implementing next phase tasks
- Modify next phase file

---

## Step 12: Feature Completion (If Final Phase)

If Phase {{phase_number}} was the last phase:

### 12.1: Update FeatureTasks.md

Mark feature as complete:
```markdown
**Feature Status**: COMPLETED
**Feature Completed**: {timestamp}
**Total Time**: {sum of all phases}
```

### 12.2: Move Feature Folder

```
Move from: MemoryBank/Features/03_IN_PROGRESS/{{feature_id}}-{name}/
Move to:   MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}/
```

### 12.3: Create Feature Completion Summary

Save as `feature-completion-report.md`:

```markdown
# Feature Completion Report: {{feature_id}}

**Feature**: {Feature Title}
**Status**: COMPLETED
**Completed**: {timestamp}

## Summary
{Feature description and what was achieved}

## Phases Completed

| Phase | Name | Estimated | Actual | Variance |
|-------|------|-----------|--------|----------|
| 0 | Health Check | {est} | {actual} | {var} |
| 1 | Planning | {est} | {actual} | {var} |
| ... | ... | ... | ... | ... |
| {{phase_number}} | {Name} | {est} | {actual} | {var} |

## Total Time
- Estimated: {total_estimated}
- Actual: {total_actual}
- Variance: {variance}

## Key Deliverables
- {Deliverable 1}
- {Deliverable 2}
- {Deliverable 3}

## LessonsLearned Documents
- Phase 1: MemoryBank/LessonsLearned/{{feature_id}}/Phase-1-*.md
- Phase 2: MemoryBank/LessonsLearned/{{feature_id}}/Phase-2-*.md
- ...
```

### 12.4: Final Git Commit

```
feat({{feature_id}}): Complete Feature - {Feature Title}

Feature fully implemented across {N} phases.

Total Time:
- Estimated: {total_estimated}
- Actual: {total_actual}
- Variance: {variance}

Generated with Claude Code
```

---

## Step 13: Final Output Summary

### For Phase Acceptance (Not Final Phase)

```markdown
## Phase {{phase_number}} Accepted - COMPLETED ✅

**Feature**: {{feature_id}} - {Feature Title}
**Phase**: Phase {{phase_number}} - {Phase Name}
**Status**: COMPLETED
**Completion Time**: {timestamp}

**Time Metrics**:
- Estimated: {estimated}
- Actual: {actual}
- Variance: {variance}

**Quality Metrics**:
- Build: {status}
- Tests: {passed}/{total} passing ({percentage}%)
- Code Review: {status}

**Git Commit**: `{hash}` - "{commit message}"
**Pushed to Remote**: {Yes/No}

**Skipped Tasks**: {None or count with justification}

---

**Files Updated**:
- [x] Phase file: Phases/phase-{{phase_number}}-*.md
- [x] FeatureTasks.md: Phase Summary table
- [x] start-feature-report-*.md (if exists)
- [x] Checkpoint section: Complete

---

{Next Phase Preview from Step 11}

---

✅ Phase {{phase_number}} Acceptance Complete

**To continue**: Run `continue-implementation` MCP command
```

### For Feature Completion (Final Phase)

```markdown
## Feature {{feature_id}} COMPLETED ✅

**Feature**: {Feature Title}
**Status**: COMPLETED
**Completion Time**: {timestamp}

**Total Phases**: {count}
**Total Time**: {actual} (estimated: {estimated})
**Overall Variance**: {variance}

**Git Commit**: `{hash}` - "{commit message}"
**Pushed to Remote**: {Yes/No}

**Feature moved to**: MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}/

**Completion Report**: feature-completion-report.md

---

🎉 Congratulations! Feature implementation complete.
```

---

## Error Handling

### Feature Not Found
```
❌ Error: Feature not found

Feature ID: {{feature_id}}
Searched in: MemoryBank/Features/03_IN_PROGRESS/

Please verify the feature ID is correct and the feature is in IN_PROGRESS status.
```

### Phase Not Found
```
❌ Error: Phase not found

Feature: {{feature_id}}
Phase: {{phase_number}}

Available phases in this feature:
{List available phases}

Please verify the phase number.
```

### Git Push Failed
```
⚠️ Git push failed

Error: {error message}

Phase {{phase_number}} is marked as COMPLETED locally but not pushed to remote.

To resolve:
1. Run: git pull --rebase origin {branch}
2. Resolve any conflicts
3. Run: git push origin {branch}
```

---

## Validation Checklist

Before completing phase acceptance, verify:

### Pre-Conditions (Must Pass)
- [ ] Checkpoint status was NOT "NotStarted"
- [ ] Phase status was "AWAITING_USER_ACCEPTANCE"

### Quality Gates (Must Pass)
- [ ] **All Tasks Completed**: Every task is `[COMPLETED]` or `[SKIPPED]` with justification
- [ ] **Git Commits Tracked (Tasks)**: Every task with code has commits in its Git Commits table
- [ ] **Git Commits Summary**: Phase checkpoint has complete Git Commits (Phase Summary) table
- [ ] **Build Clean**: 0 errors, 0 warnings
- [ ] **Lint Clean**: 0 errors, 0 warnings (if lint is configured and blocking)
- [ ] **Tests Passing**: 100% pass rate
- [ ] **Code Review APPROVED**: Latest review is APPROVED or APPROVED_WITH_NOTES (if required for phase type)
- [ ] **Code Review History**: All reviews documented in Code Review History table (if required)

### Post-Acceptance Updates
- [ ] Phase file updated to COMPLETED
- [ ] Checkpoint status updated to Complete
- [ ] FeatureTasks.md updated to COMPLETED
- [ ] start-feature-report updated (if exists)
- [ ] Time metrics calculated and recorded
- [ ] Git commit created
- [ ] Git push successful (or documented if failed)
- [ ] Next phase preview provided (or feature completion if final)

---

## Key Rules

1. **USER-CENTRIC**: Never auto-start next phase
2. **Validate First**: Check ALL requirements before accepting - no shortcuts
3. **Git Commits Required**: Phase MUST have tracked commits in both task tables AND Phase Summary
4. **Code Review Required**: Code-relevant phases MUST have APPROVED code review in history
5. **Handle Incomplete Tasks**: Prompt user, get justification for any SKIPPED tasks
6. **Update ALL Files**: Phase file, FeatureTasks.md, start-feature-report, checkpoint
7. **Calculate Time Metrics**: Actual vs Estimated with variance
8. **Git Commit**: Comprehensive commit with achievements
9. **Clear Communication**: Show next phase preview without starting it
10. **Respect User Control**: User decides when to continue

## Rejection Scenarios

The `accept-phase` command will **REJECT** the phase if:

| Scenario | Reason | Fix |
|----------|--------|-----|
| Tasks incomplete | Not all tasks are `[COMPLETED]` or `[SKIPPED]` | Complete tasks or provide skip justification |
| Git commits missing (tasks) | Task Git Commits tables are empty | Track commits in each task |
| Git commits missing (summary) | Phase Git Commits Summary is empty | Update Phase Checkpoint with all commits |
| Build fails | Build has errors or warnings | Fix build issues |
| Lint fails | Lint has errors (if configured as blocking) | Fix lint issues |
| Tests fail | Tests are not 100% passing | Fix failing tests |
| Code review missing | Code-relevant phase has no Code Review History | Run `code-review` MCP command |
| Code review NEEDS_CHANGES | Latest review status is NEEDS_CHANGES | Fix issues and re-run `code-review` |

> 🔴 **All validations must pass before a phase can be accepted. There are no exceptions.**
