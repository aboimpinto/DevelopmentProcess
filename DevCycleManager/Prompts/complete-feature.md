# Complete Feature - MCP Procedure

You are executing the **Complete Feature** procedure for the DevCycleManager. This procedure validates that a feature is truly complete, compiles Lessons Learned, and moves the feature to the COMPLETED state.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Feature Path** (if provided): {{feature_path}}

---

## Procedure Overview

This procedure performs **COMPREHENSIVE VALIDATION** before marking a feature complete:

1. **Validates all phases** are COMPLETED (or SKIPPED with justification)
2. **Verifies git repository** is clean (no uncommitted/unpushed changes)
3. **Verifies build and tests** pass (0 errors, 0 warnings, 100% tests)
4. **Compiles Lessons Learned** from all phases into feature-level document
5. **Asks user for additional lessons** they want to highlight
6. **Updates all documentation** with completion status
7. **Creates completion reports** (validation, metrics, lessons learned)
8. **Moves feature to 04_COMPLETED** folder
9. **Creates completion git commit** and pushes

**IMPORTANT**: This procedure requires explicit user confirmation before moving the feature.

---

## Step 0: Locate and Validate the Feature

### Find the Feature
Search for the feature folder in `MemoryBank/Features/03_IN_PROGRESS/`:

1. Look for `{{feature_id}}*` folders in `03_IN_PROGRESS/`
2. If not found: Stop and report error

**If feature not found**:
```
Feature {{feature_id}} not found in 03_IN_PROGRESS/.
Please verify the feature ID and ensure it has been started.
```

### Read Feature Documentation
Read these files:
1. `FeatureDescription.md` - Feature requirements and external IDs
2. `FeatureTasks.md` - Phase summary and task index
3. All phase files in `Phases/` folder
4. `start-feature-report-*.md` - Initial validation report
5. All code review reports in `code-reviews/`
6. All LessonsLearned documents created per phase

---

## Step 1: Phase Completion Verification

### 1.1: Check All Phases

For each phase in `Phases/`:

**Required for COMPLETED status**:
- Status must be `COMPLETED`
- All tasks must be `[COMPLETED]` or `[SKIPPED]` with justification
- Checkpoint section must show `Complete`
- Time tracking must be filled (no empty values)

**Allowed exceptions**:
- Tasks marked `[SKIPPED]` must have documented justification
- Phases marked `SKIPPED` must have documented justification

### 1.2: Create Phase Status Table

```markdown
## Phase Completion Status

| Phase | Name | Status | Tasks | Time (Est) | Time (Act) | Notes |
|-------|------|--------|-------|------------|------------|-------|
| 0 | Health Check | COMPLETED | 3/3 | 0.5h | 0.3h | - |
| 1 | Planning & Analysis | COMPLETED | 5/5 | 2h | 1.5h | - |
| 2 | Data Layer | COMPLETED | 8/8 | 3h | 3.5h | - |
| 3 | Business Logic | COMPLETED | 10/10 | 4h | 4h | - |
| 4 | Presentation Logic | COMPLETED | 6/6 | 2h | 2.2h | - |
| 5 | User Interface | SKIPPED | 0/4 | 2h | 0h | Backend-only feature |
| 6 | Integration | COMPLETED | 4/4 | 1.5h | 1.8h | - |
| 7 | Testing & Polish | COMPLETED | 5/5 | 1h | 1.2h | - |
| 8 | Final Checkpoint | COMPLETED | 2/2 | 0.5h | 0.4h | - |
```

### 1.3: Handle Incomplete Phases

**If ANY phase is not COMPLETED or SKIPPED**:

```markdown
Validation Failed: Incomplete Phases

The following phases are not completed:
- Phase {N}: {status} (expected: COMPLETED)
- Phase {M}: {status} (expected: COMPLETED)

**Action Required**: Complete all phases before moving to COMPLETED state.
Use `continue-implementation` MCP command to continue work.
```

**STOP** - Do not proceed with completion.

### 1.4: Validate Skipped Phases/Tasks

**For each SKIPPED phase or task**:
- Verify justification is documented
- Ensure justification is reasonable

**If justification is missing**:
```markdown
Validation Warning: Missing Justification

The following skipped items lack justification:
- Phase {N}: SKIPPED (no justification)
- Task {N}.{M}: SKIPPED (no justification)

**Action Required**: Provide justification for each skipped item.
```

Ask user for justification before proceeding.

---

## Step 2: Git Repository Verification

### 2.1: Check for Uncommitted Changes

```bash
git status --porcelain
```

**If there are uncommitted changes**:
```markdown
Validation Failed: Uncommitted Changes

The following files have uncommitted changes:
{list files}

**Action Required**: Commit and push all changes before completing feature.
```

**STOP** - Do not proceed.

### 2.2: Check for Unpushed Commits

```bash
git log origin/{branch}..HEAD --oneline
```

**If there are unpushed commits**:
```markdown
Validation Failed: Unpushed Commits

The following commits need to be pushed:
{list commits}

**Action Required**: Push all commits before completing feature.
```

**STOP** - Do not proceed.

### 2.3: Record Branch Information

Record:
- Current branch name
- Last commit hash
- Total commits for this feature

---

## Step 3: Build & Test Verification

### 3.1: Run Build

Execute the project's build command (from project documentation):
- **Required**: 0 errors, 0 warnings

**If build fails**:
```markdown
Validation Failed: Build Issues

Build errors: {count}
Build warnings: {count}

{error details}

**Action Required**: Fix all build errors and warnings before completing feature.
```

**STOP** - Do not proceed.

### 3.2: Run All Tests

Execute the project's test command:
- **Required**: 100% passing

**If tests fail**:
```markdown
Validation Failed: Test Failures

Tests passing: {passed}/{total} ({percentage}%)
Tests failing:
{list failed tests}

**Action Required**: Fix all failing tests before completing feature.
```

**STOP** - Do not proceed.

---

## Step 4: Compile Lessons Learned

### 4.1: Collect Phase-Level Lessons Learned

Read all LessonsLearned documents created during implementation:
- `MemoryBank/LessonsLearned/{{feature_id}}/Phase-*-*.md`

Extract from each:
- What went well
- Challenges encountered
- Technical decisions
- Patterns discovered
- Time analysis insights

### 4.2: Analyze Feature Metrics

Calculate overall metrics:
- Total estimated time vs actual time
- Phases with largest variance (over/under estimated)
- Most challenging phases
- Patterns that worked well

### 4.3: Ask User for Additional Lessons

**STOP and ask the user**:

```markdown
## Lessons Learned Collection

I've compiled the following lessons from phase documentation:

**Auto-Detected Lessons**:
1. {Lesson 1 from phase docs}
2. {Lesson 2 from phase docs}
3. {Lesson 3 from phase docs}

**Time Analysis**:
- Total Estimated: {X}h
- Total Actual: {Y}h
- Variance: {Z}% ({faster/slower} than estimated)
- Phases with largest variance: {list}

**Would you like to add any additional lessons learned?**

Examples of things you might want to highlight:
- Decisions that worked particularly well
- Decisions you would change in hindsight
- Tools or patterns that helped
- Problems that took longer than expected
- Recommendations for future similar features

Please provide any additional lessons you'd like documented, or type "none" to proceed with auto-detected lessons only.
```

**WAIT for user response**.

### 4.4: Create Feature-Level Lessons Learned Document

Save to `MemoryBank/LessonsLearned/{{feature_id}}/Feature-Completion-LessonsLearned.md`:

```markdown
# Lessons Learned: {{feature_id}} - {Feature Title}

**Feature**: {{feature_id}}
**Completed**: {timestamp}
**Total Development Time**: {actual}h (estimated: {estimated}h)

---

## Executive Summary

{2-3 paragraph summary of the feature implementation, key achievements, and overall lessons}

---

## Time Analysis

### Overall Metrics
| Metric | Estimated | Actual | Variance |
|--------|-----------|--------|----------|
| Total Time | {est}h | {actual}h | {var}% |
| Phases Completed | {total} | {completed} | - |
| Tasks Completed | {total} | {completed} | - |
| Code Reviews | - | {count} | - |

### Phase-by-Phase Analysis
| Phase | Estimated | Actual | Variance | Notes |
|-------|-----------|--------|----------|-------|
| 0 | {est} | {act} | {var}% | {notes} |
| 1 | {est} | {act} | {var}% | {notes} |
| ... | ... | ... | ... | ... |

### Variance Analysis
**Phases that took longer than estimated**:
- Phase {N}: +{X}% - {reason}

**Phases that were faster than estimated**:
- Phase {M}: -{Y}% - {reason}

---

## What Went Well

{Compiled from all phase lessons + user input}

1. **{Category}**: {Description}
2. **{Category}**: {Description}
3. **{Category}**: {Description}

---

## Challenges Encountered

{Compiled from all phase lessons + user input}

1. **{Challenge}**:
   - Impact: {description}
   - Resolution: {how it was resolved}
   - Prevention: {how to prevent in future}

2. **{Challenge}**:
   - Impact: {description}
   - Resolution: {how it was resolved}
   - Prevention: {how to prevent in future}

---

## Technical Decisions

| Decision | Choice Made | Rationale | Outcome |
|----------|-------------|-----------|---------|
| {Decision 1} | {Choice} | {Why} | {Result} |
| {Decision 2} | {Choice} | {Why} | {Result} |

---

## Patterns Discovered

### Reusable Patterns
{Patterns that should be reused in future features}

1. **{Pattern Name}**
   - Location: `{file path}`
   - Use Case: {when to use}
   - Example: {brief code or description}

### Anti-Patterns Identified
{Patterns that should be avoided}

1. **{Anti-Pattern Name}**
   - Problem: {why it's bad}
   - Alternative: {what to do instead}

---

## User-Highlighted Lessons

{Lessons specifically provided by the user during completion}

1. {User lesson 1}
2. {User lesson 2}
3. {User lesson 3}

---

## Recommendations for Future Features

Based on this feature implementation:

1. **Estimation**: {recommendations for time estimation}
2. **Architecture**: {architectural recommendations}
3. **Process**: {process improvements}
4. **Testing**: {testing recommendations}
5. **Documentation**: {documentation recommendations}

---

## Files Changed

### Summary
- Files Created: {count}
- Files Modified: {count}
- Total Lines Added: {count}
- Total Lines Removed: {count}

### Key Files
| File | Type | Purpose |
|------|------|---------|
| {file} | {New/Modified} | {purpose} |

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Build Status | 0 errors, 0 warnings |
| Test Status | {passed}/{total} passing (100%) |
| Code Reviews | {count} iterations |
| Final Review Status | APPROVED |

---

*Generated during feature completion on {timestamp}*
```

### 4.5: Update Global Lessons Learned Index

If `MemoryBank/LessonsLearned/README.md` or index exists, add entry for this feature.

---

## Step 5: Create Completion Reports

### 5.1: Create Feature Completion Report

Save to feature folder as `feature-completion-report.md`:

```markdown
# Feature Completion Report: {{feature_id}}

**Feature**: {Feature Title}
**Status**: COMPLETED
**Completed**: {timestamp}

---

## Summary

{Brief description of what was implemented}

---

## Validation Results

### Phase Completion
| Phase | Status | Tasks | Time |
|-------|--------|-------|------|
{phase status table}

**Total Phases**: {count}
**Phases Completed**: {count}
**Phases Skipped**: {count} (with justification)

### Git Repository
- Branch: {branch}
- Uncommitted Changes: None
- Unpushed Commits: None
- Final Commit: {hash}

### Build & Tests
- Build: 0 errors, 0 warnings
- Tests: {passed}/{total} passing (100%)

### Documentation
- FeatureDescription.md: Valid
- FeatureTasks.md: All phases COMPLETED
- Phase Files: All COMPLETED or SKIPPED with justification
- Code Reviews: All APPROVED
- Lessons Learned: Compiled

---

## Feature Metrics

| Metric | Estimated | Actual | Variance |
|--------|-----------|--------|----------|
| Total Time | {est}h | {actual}h | {var}% |
| Phases | {total} | {completed} | - |
| Tasks | {total} | {completed} | - |
| Code Reviews | - | {count} | - |
| Git Commits | - | {count} | - |

---

## Deliverables

### Code Deliverables
{List key files/components created}

### Documentation Deliverables
- Feature Completion Report (this file)
- Lessons Learned: `MemoryBank/LessonsLearned/{{feature_id}}/`
- Code Reviews: `code-reviews/`

---

## Skipped Items (If Any)

| Item | Type | Justification |
|------|------|---------------|
| {item} | {Phase/Task} | {justification} |

---

## Related Documents

- Feature Description: `FeatureDescription.md`
- Feature Tasks: `FeatureTasks.md`
- Design Summary: `design-summary.md`
- Lessons Learned: `MemoryBank/LessonsLearned/{{feature_id}}/`
- Code Reviews: `code-reviews/`

---

*Feature moved to 04_COMPLETED on {timestamp}*
```

### 5.2: Update FeatureTasks.md

Add completion section:

```markdown
---

## Feature Completion

**Status**: COMPLETED
**Completed**: {timestamp}
**Total Time**: {actual}h (estimated: {estimated}h, variance: {var}%)
**Final Commit**: {hash}
**Moved To**: `MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}/`
```

---

## Step 6: Present Validation Report

Present comprehensive validation report to user:

```markdown
# Feature Completion Validation Report

**Feature**: {{feature_id}} - {Feature Title}
**External ID**: {if provided in FeatureDescription}

---

## Phase Completion Status

{phase status table}

**Result**: {count}/{total} phases COMPLETED
{if skipped: "{count} phases SKIPPED with justification"}

---

## Git Repository Status

- Uncommitted Changes: None
- Unpushed Commits: None
- Branch: {branch}
- Total Commits: {count}

---

## Build & Test Status

- Build: 0 errors, 0 warnings
- Tests: {passed}/{total} passing (100%)

---

## Documentation Status

- FeatureDescription.md: Valid
- FeatureTasks.md: All phases COMPLETED
- Phase Files: All validated
- Code Reviews: All APPROVED
- Lessons Learned: Compiled ({count} documents)

---

## Feature Metrics

| Metric | Value |
|--------|-------|
| Total Phases | {count} |
| Total Tasks | {count} |
| Total Time (Estimated) | {est}h |
| Total Time (Actual) | {actual}h |
| Time Variance | {var}% |
| Code Reviews | {count} |
| Git Commits | {count} |

---

## Lessons Learned

{count} lessons compiled:
- What went well: {count} items
- Challenges: {count} items
- Technical decisions: {count} items
- User-highlighted: {count} items

Document: `MemoryBank/LessonsLearned/{{feature_id}}/Feature-Completion-LessonsLearned.md`

---

**Validation Result**: READY TO COMPLETE

All requirements met. Feature is ready to move to COMPLETED state.
```

---

## Step 7: Request User Confirmation

**CRITICAL**: Do not proceed without explicit user confirmation.

```markdown
---

## Confirm Feature Completion

This feature has passed all validation checks and is ready to complete.

**Actions that will be taken**:
1. Move feature folder to `MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}/`
2. Create completion git commit
3. Push to remote repository

**This action cannot be easily undone.**

**Do you want to proceed with completing this feature?**
- Reply "yes" or "complete" to proceed
- Reply "no" or "cancel" to abort
```

**WAIT for user response**.

**If user says no/cancel**:
```
Feature completion cancelled. Feature remains in 03_IN_PROGRESS.
```
**STOP** - Do not proceed.

---

## Step 8: Complete the Feature

### 8.1: Move Feature Folder

```bash
# Create COMPLETED folder if needed
mkdir -p "MemoryBank/Features/04_COMPLETED"

# Move feature folder
git mv "MemoryBank/Features/03_IN_PROGRESS/{{feature_id}}-{name}" "MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}"
```

### 8.2: Create Completion Commit

```
feat({{feature_id}}): Complete Feature - {Feature Title}

Feature moved to COMPLETED state after validation:
- All {count} phases completed successfully
- Total development time: {actual}h (estimated: {estimated}h, {var}% {faster/slower})
- Build: 0 errors, 0 warnings
- Tests: {passed}/{total} passing (100%)
- Code reviews: All APPROVED
- Lessons learned: Compiled and documented

Feature is production ready.

Generated with Claude Code
```

### 8.3: Push to Remote

```bash
git push origin {branch}
```

---

## Step 9: Final Completion Report

Present final report to user:

```markdown
# Feature Completion Success

**Feature**: {{feature_id}} - {Feature Title}
**Status**: COMPLETED
**Completed**: {timestamp}

---

## Actions Taken

- [x] Validated all phases completed
- [x] Verified git repository clean
- [x] Verified build and tests passing
- [x] Compiled Lessons Learned ({count} documents)
- [x] Created feature completion report
- [x] Moved feature to `04_COMPLETED/{{feature_id}}-{name}/`
- [x] Created completion commit ({hash})
- [x] Pushed to remote repository

---

## Commit Details

- **Hash**: {commit hash}
- **Message**: feat({{feature_id}}): Complete Feature - {Feature Title}
- **Branch**: {branch}
- **Remote**: Pushed

---

## Final Metrics

| Metric | Value |
|--------|-------|
| Total Phases | {completed}/{total} |
| Total Tasks | {completed}/{total} |
| Total Time | {actual}h (est: {estimated}h) |
| Time Efficiency | {var}% {faster/slower} |
| Code Reviews | {count} |
| Test Coverage | 100% |

---

## Documentation Created

- Feature Completion Report: `04_COMPLETED/{{feature_id}}-{name}/feature-completion-report.md`
- Lessons Learned: `MemoryBank/LessonsLearned/{{feature_id}}/`
  - Feature-Completion-LessonsLearned.md
  - Phase-*-*.md (per phase)

---

## Next Steps

- [ ] Close external ticket/story (if applicable)
- [ ] Update project documentation if needed
- [ ] Select next feature from `02_READY_TO_DEVELOP/`
- [ ] Review Lessons Learned for future features

---

**Feature {{feature_id}} is now archived in COMPLETED state!**

Congratulations on completing this feature!
```

---

## Error Handling

### Feature Not Found
```
Feature {{feature_id}} not found in MemoryBank/Features/03_IN_PROGRESS/.
Please verify the feature ID.
```

### Git Operations Fail
```
Git operation failed: {error}
Please resolve the issue and try again.
```

### Move Operation Fails
```
Failed to move feature folder: {error}
Feature remains in 03_IN_PROGRESS.
Please resolve the issue and try again.
```

---

## Important Rules

1. **NEVER skip validation steps** - All checks must pass
2. **ALWAYS compile Lessons Learned** - Both automatic and user-provided
3. **ALWAYS wait for user confirmation** before moving feature
4. **ALWAYS update all documentation** before moving
5. **NEVER proceed if any validation fails** - Report and stop
6. **Record everything** - Metrics, lessons, decisions

---

## Let's Begin!

When this procedure is invoked:
1. Start from **Step 0: Locate and Validate the Feature**
2. Proceed through all validation steps
3. Compile Lessons Learned (ask user for input)
4. Present validation report
5. Request user confirmation
6. Only after confirmation: Move feature and create commit
7. Present final completion report
