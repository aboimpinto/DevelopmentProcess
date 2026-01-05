# Continue Implementation - MCP Procedure

You are executing the **Continue Implementation** procedure for the DevCycleManager. This procedure orchestrates the systematic implementation of a feature that is already in `03_IN_PROGRESS`.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Feature Path** (if provided): {{feature_path}}

---

## Procedure Overview

This procedure is the **PRIMARY ORCHESTRATOR** for feature implementation. It:

1. **Discovers context** (feature, phase, task)
2. **Executes tasks** (following task specifications)
3. **Manages quality** (build, tests, code-review)
4. **Tracks progress** (update phase files, FeatureTasks.md)
5. **Requests acceptance** (user approval for phase completion)
6. **Creates LessonsLearned** (per-phase documentation)

**IMPORTANT**: This procedure ORCHESTRATES but NEVER implements code directly. All code implementation is done by you (the LLM) following the task specifications.

---

## Step 0: Locate and Validate the Feature

### Find the Feature
Search for the feature folder in `MemoryBank/Features/03_IN_PROGRESS/`:

1. Look for `{{feature_id}}*` folders in `03_IN_PROGRESS/`
2. If not found, check `02_READY_TO_DEVELOP/` (feature may need to be started first)
3. If in `02_READY_TO_DEVELOP/`, inform user: "Feature {{feature_id}} is in READY_TO_DEVELOP. Use the start-feature command first."

**If the feature is not found in any expected location:** Stop and report: "Feature {{feature_id}} not found. Please verify the feature ID."

### Validate Feature Structure
Once found, verify these files exist:
1. `FeatureDescription.md` - Feature requirements
2. `FeatureTasks.md` - Phase summary and task index
3. `Phases/` folder with phase files
4. `start-feature-report-*.md` - Validation report from start-feature

**If validation report is missing:** This feature may not have been properly started. Inform user.

### Read Project Context
Read these context files to understand the project:
1. `MemoryBank/Overview/` - Project vision and goals
2. `MemoryBank/Architecture/` - Existing components and patterns
3. `MemoryBank/CodeGuidelines/` - Standards and technologies

### Extract Build/Test Commands
From the project documentation, identify:
- **Build Command**: How to compile/build the project
- **Test Command**: How to run the test suite
- **Lint Command**: How to run code quality checks (if applicable)

**If build/test commands not found:** Ask user for the commands before proceeding.

---

## Step 1: Identify Current State

### Read FeatureTasks.md
Extract the Phase Summary table to identify:
- Current phase (Status = `IN_PROGRESS`)
- Completed phases (Status = `COMPLETED`)
- Pending phases (Status = `PENDING`)

### Read Current Phase File
Find the phase file in `Phases/` that matches the current `IN_PROGRESS` phase:
- `Phases/phase-{N}-{name}.md`

### Identify Entry Point

Determine where to resume based on current state:

#### Entry Point A: After start-feature (Fresh Start)
**Detection**: Phase status is `IN_PROGRESS`, no tasks have `[IN_PROGRESS]` or `[COMPLETED]`
**Action**: Start with the first task of the phase

#### Entry Point B: Mid-Phase (Task Continuation)
**Detection**: Some tasks are `[COMPLETED]`, one task is `[IN_PROGRESS]`
**Action**: Continue with the `[IN_PROGRESS]` task

#### Entry Point C: All Tasks Complete (Checkpoint Pending)
**Detection**: All tasks are `[COMPLETED]`, but phase checkpoint is not filled
**Action**: Go to Step 4 (Phase Completion)

#### Entry Point D: Checkpoint Incomplete (Validation Failed)
**Detection**: Checkpoint status is `InProgress` with failures recorded
**Action**: Fix issues (build errors, test failures, code review issues) then re-validate

#### Entry Point E: Awaiting User Acceptance
**Detection**: Phase status is `AWAITING_USER_ACCEPTANCE`
**Action**: Present phase summary, wait for user acceptance

---

## Step 1.5: Phase 1 - Planning & Analysis (Special Handling)

**IMPORTANT**: If the current phase is **Phase 1 (Planning & Analysis)**, this step provides a detailed recipe for analyzing the implementation approach BEFORE any coding begins.

### Purpose of Phase 1

Phase 1 is NOT about writing code. It's about:
1. **Understanding** what kind of implementation this feature requires
2. **Researching** existing patterns in the codebase
3. **Enriching** task specifications with concrete implementation guidance
4. **Preparing** code samples for subsequent phases

### Step 1.5.1: Classify Implementation Types

For each task in the feature, determine the implementation type(s):

| Type | Description | Look For |
|------|-------------|----------|
| **UI/Presentation** | User interface components, views, screens | "display", "show", "screen", "dialog", "form" |
| **Data Layer** | Database access, data models, repositories | "store", "save", "retrieve", "database", "entity" |
| **Service/API** | External service calls, API integration | "API", "service", "endpoint", "request", "response" |
| **Business Logic** | Core algorithms, rules, calculations | "calculate", "validate", "process", "rule" |
| **State Management** | Application state, caching, events | "state", "cache", "event", "notify", "subscribe" |
| **Integration** | Connecting components, orchestration | "connect", "integrate", "orchestrate", "coordinate" |
| **Infrastructure** | Configuration, logging, error handling | "config", "log", "error", "setup" |

**Output**: Create a classification table in the phase file:

```markdown
### Implementation Type Analysis

| Task | Primary Type | Secondary Types | Complexity |
|------|--------------|-----------------|------------|
| 2.1 | Data Layer | Business Logic | Medium |
| 3.1 | Service/API | Error Handling | High |
| 5.1 | UI/Presentation | State Management | Medium |
```

### Step 1.5.2: Study Project Guidelines

Read and analyze the following documents thoroughly:

#### 1. CodeGuidelines Analysis
Read all files in `MemoryBank/CodeGuidelines/`:

**Extract and document**:
- Naming conventions (files, classes, methods, variables)
- Code structure patterns (folder organization, module structure)
- Error handling patterns
- Testing requirements and patterns
- Documentation standards
- Technology-specific guidelines

**Create Summary**:
```markdown
### CodeGuidelines Summary for This Feature

**Naming Conventions**:
- {Convention 1}: {Example}
- {Convention 2}: {Example}

**Required Patterns**:
- {Pattern 1}: Used for {scenario}
- {Pattern 2}: Used for {scenario}

**Testing Requirements**:
- {Requirement 1}
- {Requirement 2}

**Technology Stack**:
- Language: {language}
- Framework: {framework}
- Testing: {test framework}
```

#### 2. Architecture Analysis
Read all files in `MemoryBank/Architecture/`:

**Extract and document**:
- Layer structure (presentation, business, data)
- Component relationships
- Dependency injection patterns
- Communication patterns (events, callbacks, direct calls)
- Module boundaries

**Create Summary**:
```markdown
### Architecture Patterns for This Feature

**Layer This Feature Touches**:
- [ ] Presentation Layer
- [ ] Business Logic Layer
- [ ] Data Access Layer
- [ ] Infrastructure Layer

**Components to Create/Modify**:
| Component | Layer | Action | Depends On |
|-----------|-------|--------|------------|
| {Component 1} | {Layer} | Create | {Dependencies} |
| {Component 2} | {Layer} | Modify | {Dependencies} |

**Integration Points**:
- {Integration point 1}: {How to integrate}
- {Integration point 2}: {How to integrate}
```

#### 3. LessonsLearned Analysis
Read all files in `MemoryBank/LessonsLearned/`:

**Extract and document**:
- Past mistakes to avoid
- Successful patterns to reuse
- Performance considerations
- Edge cases discovered
- Time estimation insights

**Create Summary**:
```markdown
### Lessons Learned Applicable to This Feature

**Patterns to Reuse**:
- {Pattern from FEAT-XXX}: {Description and when to apply}
- {Pattern from FEAT-YYY}: {Description and when to apply}

**Pitfalls to Avoid**:
- {Pitfall 1}: {How to avoid}
- {Pitfall 2}: {How to avoid}

**Time Estimation Adjustments**:
- {Type of task}: Typically takes {X}% longer than estimated because {reason}
```

### Step 1.5.3: Search for Existing Patterns in Codebase

**Search the actual codebase** for patterns that match the implementation types identified:

#### For UI/Presentation Tasks:
```
Search for:
- Existing views/screens similar to what's needed
- Form handling patterns
- Validation display patterns
- Navigation patterns
- Component reuse opportunities
```

#### For Data Layer Tasks:
```
Search for:
- Existing repository/DAO patterns
- Data model structures
- Query patterns
- Transaction handling
- Caching implementations
```

#### For Service/API Tasks:
```
Search for:
- Existing API client patterns
- Error handling for external calls
- Retry logic implementations
- Response mapping patterns
- Authentication handling
```

#### For Business Logic Tasks:
```
Search for:
- Similar calculation/validation logic
- Rule engine patterns
- State machine implementations
- Event handling patterns
```

**Document Findings**:
```markdown
### Existing Patterns Found

#### Pattern: {Pattern Name}
**Location**: `{file path}`
**Used For**: {Description}
**Applicable To Tasks**: {Task numbers}
**How To Apply**:
```{language}
// Key code snippet showing the pattern
```

#### Pattern: {Pattern Name 2}
...
```

### Step 1.5.4: Enrich Task Specifications

For each task in subsequent phases, add implementation guidance:

#### Option A: Add Directly to Task
Update the task in the phase file with:

```markdown
### Task {N}.{M}: {Task Name}

[... existing task content ...]

---
#### Implementation Guidance (Added in Phase 1)

**Implementation Type**: {Primary Type} + {Secondary Types}

**Recommended Approach**:
1. {Step 1}
2. {Step 2}
3. {Step 3}

**Pattern Reference**:
- Use pattern from `{file path}` as template
- Key method: `{method name}`

**Files to Create/Modify**:
| File | Action | Based On |
|------|--------|----------|
| `{path/to/file}` | Create | `{template file}` |
| `{path/to/file}` | Modify | Add {what} |

**Dependencies**:
- Requires: {dependency 1}
- Requires: {dependency 2}

**Testing Approach**:
- Unit test: {what to test}
- Integration test: {what to test}
```

#### Option B: Create Code Sample Reference
For complex implementations, create a code sample file:

**Location**: `Phases/code-samples/task-{N}-{M}-{name}.md`

**Template**:
```markdown
# Code Sample: Task {N}.{M} - {Task Name}

## Overview
{Brief description of what this code sample demonstrates}

## Implementation Pattern

### Step 1: {Step Name}
```{language}
// Code example with comments explaining the pattern
```

### Step 2: {Step Name}
```{language}
// Code example
```

## Adaptation Notes
- Replace `{placeholder}` with {actual value}
- Modify {section} to handle {specific requirement}

## Test Pattern
```{language}
// Example test structure
```

## References
- Based on: `{source file path}`
- Related pattern: `{related file path}`
```

**Then add reference to the task**:
```markdown
**Code Sample**: See `Phases/code-samples/task-{N}-{M}-{name}.md`
```

### Step 1.5.5: Create Planning Analysis Report

Save to the feature folder as `planning-analysis-report.md`:

```markdown
# Planning & Analysis Report: {{feature_id}}

**Feature**: {Feature Title}
**Date**: {timestamp}
**Phase**: 1 - Planning & Analysis

## Executive Summary
{2-3 sentences summarizing the implementation approach}

## Implementation Type Distribution

| Type | Task Count | Complexity |
|------|------------|------------|
| UI/Presentation | {count} | {avg complexity} |
| Data Layer | {count} | {avg complexity} |
| Service/API | {count} | {avg complexity} |
| Business Logic | {count} | {avg complexity} |
| Other | {count} | {avg complexity} |

## Key Patterns Identified

### Pattern 1: {Name}
- **Source**: `{file path}`
- **Used In Tasks**: {list}
- **Why**: {rationale}

### Pattern 2: {Name}
...

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {Risk 1} | {H/M/L} | {H/M/L} | {Strategy} |
| {Risk 2} | {H/M/L} | {H/M/L} | {Strategy} |

## Dependencies Identified

| Dependency | Required By | Status |
|------------|-------------|--------|
| {Dependency 1} | Tasks {list} | {Available/Needs Setup} |
| {Dependency 2} | Tasks {list} | {Available/Needs Setup} |

## Tasks Enriched

| Task | Enrichment Added | Code Sample Created |
|------|------------------|---------------------|
| 2.1 | Implementation guidance | Yes - `code-samples/task-2-1-*.md` |
| 2.2 | Pattern reference | No |
| 3.1 | Implementation guidance | Yes - `code-samples/task-3-1-*.md` |

## Estimated Impact on Timeline

Based on LessonsLearned and complexity analysis:
- Original Estimate: {X hours}
- Adjusted Estimate: {Y hours}
- Adjustment Reason: {explanation}

## Ready for Implementation

- [x] All tasks classified by implementation type
- [x] CodeGuidelines reviewed and summarized
- [x] Architecture patterns documented
- [x] LessonsLearned applied
- [x] Existing codebase patterns identified
- [x] Tasks enriched with implementation guidance
- [x] Code samples created where needed
- [x] Risks identified and mitigation planned

**Recommendation**: Proceed to Phase 2 - {Next Phase Name}
```

### Step 1.5.6: Phase 1 Completion Checklist

Before marking Phase 1 as complete, verify:

- [ ] **Implementation types classified** for ALL tasks in ALL phases
- [ ] **CodeGuidelines summary** created with applicable patterns
- [ ] **Architecture analysis** completed with component mapping
- [ ] **LessonsLearned** reviewed and applicable patterns noted
- [ ] **Codebase search** performed for reusable patterns
- [ ] **Tasks enriched** with implementation guidance OR code sample references
- [ ] **Code samples created** for complex tasks (in `Phases/code-samples/`)
- [ ] **Planning Analysis Report** created
- [ ] **No code written** - Phase 1 is analysis only

**If any item is incomplete**: Address before proceeding.

**When all items complete**: Proceed to Phase Completion (Step 3).

---

## Step 2: Task Execution Loop

For each task in the current phase:

### Step 2.1: Mark Task as IN_PROGRESS

Update the task in the phase file:
```markdown
**Status**: `[IN_PROGRESS]`
**Work Started**: {current timestamp}
```

Update FeatureTasks.md if this is the first task starting in this phase.

### Step 2.2: Gather Task Context

Collect all information needed to implement the task:

1. **Task Requirements**:
   - User Story (As a... I want... So that...)
   - Behavior Specification (Gherkin scenarios)
   - Data Requirements (if any)
   - Business Rules
   - Critical Requirements

2. **Design Context**:
   - Read `design-summary.md` for implementation guidance
   - Read `UX-research-report.md` for user flow context
   - Check `Phases/code-samples/` for any reference code

3. **Project Standards**:
   - Read `MemoryBank/CodeGuidelines/` for coding standards
   - Follow project-specific patterns

### Step 2.3: Implement the Task

**You (the LLM) implement the task** following:
- The Gherkin behavior specifications (Given/When/Then)
- The project's coding standards
- The architectural patterns from MemoryBank

**For each implementation**:
1. Write the code following the behavior spec
2. Write corresponding unit tests
3. Run the build command
4. Run the test command
5. Fix any errors (see Step 2.4)
6. Commit the changes

**Commit Message Format**:
```
feat({feature_id}): {task description}

- {change 1}
- {change 2}

Generated with Claude Code
```

### Step 2.3.1: Track Git Commit in Task

**CRITICAL**: After EVERY git commit, you MUST update the task's Git Commits table:

1. **Get the commit hash**:
   ```bash
   git log -1 --format="%h"
   ```

2. **Update the task's Git Commits table** in the phase file:
   ```markdown
   **Git Commits:**
   | Commit Hash | Message | Date |
   |-------------|---------|------|
   | abc1234 | feat(FEAT-001): Implement user validation | 2024-01-15 |
   ```

3. **Also update the Phase Checkpoint's Git Commits (Phase Summary)** table:
   ```markdown
   ### Git Commits (Phase Summary)

   | # | Commit Hash | Message | Task | Date |
   |---|-------------|---------|------|------|
   | 1 | abc1234 | feat(FEAT-001): Implement user validation | Task 2.1 | 2024-01-15 |

   **Total Commits in Phase**: 1
   ```

> 🔴 **IMPORTANT**: Failing to track commits will block phase acceptance. The `accept-phase` command validates that all commits are properly documented.

### Step 2.4: Handle Build/Test Errors

**If Build Errors Occur**:
1. Analyze the error messages
2. Identify root cause
3. Fix the issues
4. Re-run build
5. If still failing after 3 attempts, inform user and request help

**If Test Failures Occur**:
1. Determine if it's a test issue or implementation issue
2. If test issue: Fix the test
3. If implementation issue: Fix the implementation
4. Re-run tests
5. If still failing after 3 attempts, inform user and request help

**Boy Scout Rule**: Fix ALL warnings before proceeding. Do not leave warnings unaddressed.

### Step 2.5: Mark Task as COMPLETED

Update the task in the phase file:
```markdown
**Status**: `[COMPLETED]`
**Work Completed**: {current timestamp}
**Actual Duration**: {calculated duration}
```

**Verify Git Commits are Tracked**:
Before marking as complete, verify the task's Git Commits table has entries:
```markdown
**Git Commits:**
| Commit Hash | Message | Date |
|-------------|---------|------|
| abc1234 | feat(FEAT-001): Implement user validation | 2024-01-15 |
| def5678 | test(FEAT-001): Add user validation tests | 2024-01-15 |
```

> ⚠️ **WARNING**: If the Git Commits table is empty, the task is NOT properly completed. Every task with code changes MUST have at least one commit tracked.

### Step 2.6: Continue to Next Task

- If more tasks remain: Loop back to Step 2.1 with next `[PENDING]` task
- If all tasks complete: Proceed to Step 3 (Phase Completion)

---

## Step 3: Phase Completion

When all tasks in a phase are `[COMPLETED]`:

### Step 3.0: Validate Git Commits are Tracked (CRITICAL)

**Before proceeding with phase completion, verify ALL commits are documented:**

1. **Check each task's Git Commits table**:
   - Every task with code changes MUST have at least one commit
   - If any task has an empty Git Commits table, go back and fill it

2. **Check the Phase Checkpoint's Git Commits (Phase Summary)**:
   - Should contain ALL commits from ALL tasks in this phase
   - Update the "Total Commits in Phase" count

3. **Verify commit count is reasonable**:
   - A phase with 5 tasks should typically have 5+ commits
   - If the count seems low, verify no commits were missed

**Example Phase Git Commits Summary**:
```markdown
### Git Commits (Phase Summary)

| # | Commit Hash | Message | Task | Date |
|---|-------------|---------|------|------|
| 1 | abc1234 | feat(FEAT-001): Add user model | Task 2.1 | 2024-01-15 |
| 2 | def5678 | test(FEAT-001): Add user model tests | Task 2.2 | 2024-01-15 |
| 3 | ghi9012 | feat(FEAT-001): Add validation service | Task 2.3 | 2024-01-15 |
| 4 | jkl3456 | test(FEAT-001): Add validation tests | Task 2.4 | 2024-01-15 |

**Total Commits in Phase**: 4
```

> 🔴 **BLOCKING**: If git commits are not properly tracked, the `accept-phase` command will REJECT the phase.

### Step 3.1: Run Full Build

Execute the project's build command:
- **Expected**: 0 errors, 0 warnings
- **If errors/warnings exist**: Fix them before proceeding

### Step 3.2: Run ALL Tests

Execute the project's test command:
- **Expected**: 100% passing
- **If failures exist**: Fix them before proceeding

### Step 3.2.1: Run Lint (If Configured)

If the project has lint configured (check FeatureTasks.md Lint Configuration):
- Execute the lint command
- **Expected**: 0 errors, 0 warnings
- **If errors/warnings exist**: Fix them before proceeding

> ⚠️ **BLOCKING**: If lint is configured as blocking, lint errors MUST be fixed before proceeding.

### Step 3.3: Code Review (REQUIRED for Code-Relevant Phases)

**Determine if code-review is needed**:

**SKIP code-review for**:
- Phase 0: Health Check
- Phase 1: Planning & Analysis
- Phase 8: Final Checkpoint (verification only)
- Phases with only configuration/documentation
- Phases with only data models/DTOs (no business logic)

**REQUIRE code-review for**:
- Phase 2 (Data Layer) - If contains business logic
- Phase 3 (Business Logic) - **ALWAYS**
- Phase 4 (Presentation Logic) - **ALWAYS**
- Phase 5 (User Interface) - **ALWAYS**
- Phase 6 (Integration) - If contains significant code
- Phase 7 (Testing & Polish) - If contains new code beyond tests

**If code-review IS required**:

### 🔴 IMPORTANT: Use the `code-review` MCP Command

**DO NOT perform the code review manually.** Instead, invoke the `code-review` MCP command:

```
MCP Command: code-review
Parameters:
  - feature_id: {{feature_id}}
  - phase_number: {current_phase_number}
```

The `code-review` MCP command will:
1. **Read the Git Commits (Phase Summary)** to identify all commits in this phase
2. Extract all changed files from those commits
3. Review each file against `MemoryBank/CodeGuidelines/`
4. Validate test quality (meaningful assertions, coverage)
5. Generate a detailed report with status:
   - **APPROVED**: No issues, ready to proceed
   - **APPROVED_WITH_NOTES**: Minor issues, can proceed with notes
   - **NEEDS_CHANGES**: Critical issues, must fix before proceeding
6. Save report to `code-reviews/phase-{N}/Code-Review-{timestamp}-{STATUS}.md`
7. Update phase checkpoint's **Code Review History** table

### Step 3.3.1: Update Code Review History Table

After EACH code review (including re-reviews), update the **Code Review History** table in the Phase Checkpoint:

```markdown
#### Code Review History

| # | Date | Status | Report | Notes |
|---|------|--------|--------|-------|
| 1 | 2024-01-15 | NEEDS_CHANGES | [Code-Review-2024-01-15-NEEDS_CHANGES.md](code-reviews/phase-3/...) | 3 critical issues |
| 2 | 2024-01-16 | APPROVED_WITH_NOTES | [Code-Review-2024-01-16-APPROVED_WITH_NOTES.md](code-reviews/phase-3/...) | 1 minor note |

**Current Code Review Status**: APPROVED_WITH_NOTES
**Latest Review Result**: APPROVED_WITH_NOTES
**Reviews Required to Pass**: 2
```

> 📝 **All reviews are tracked**: This history shows how issues were identified and resolved, providing valuable documentation for future reference.

### After Code Review Completes

**If review status is APPROVED or APPROVED_WITH_NOTES**:
- Update the Code Review History table with the result
- Proceed to Step 3.4 (Fill Checkpoint Section)

**If review status is NEEDS_CHANGES**:
1. Update the Code Review History table with the result
2. Read the code review report for specific issues
3. Fix all CRITICAL issues (mandatory)
4. Address HIGH PRIORITY issues (recommended)
5. Create git commit with fixes
6. **Track the fix commit** in both task and Phase Summary tables
7. Re-run build (must pass with 0 errors, 0 warnings)
8. Re-run tests (must pass 100%)
9. Re-run lint (if configured)
10. **Re-invoke `code-review` MCP command** for re-review
11. **Add new row to Code Review History** with new result
12. Repeat until review status is APPROVED or APPROVED_WITH_NOTES

### Auto-Fix Loop for Code Review

```
review_count = 0
While review_status == NEEDS_CHANGES:
    review_count += 1
    1. Add review to Code Review History table
    2. Read review report issues
    3. Fix CRITICAL issues
    4. Fix HIGH PRIORITY issues
    5. Commit fixes (track in Git Commits tables!)
    6. Run build (verify clean)
    7. Run tests (verify passing)
    8. Run lint (verify clean, if configured)
    9. Re-invoke code-review MCP command
    10. Check new review status
    11. Add new row to Code Review History
```

**Maximum Iterations**: 3 review cycles
- If still NEEDS_CHANGES after 3 cycles, inform user and request manual intervention

> 🔴 **BLOCKING**: The `accept-phase` command will REJECT a phase if:
> - Code review is required but no reviews exist in Code Review History
> - The latest review status is NEEDS_CHANGES

### Step 3.4: Fill Checkpoint Section

Update the phase file's checkpoint section with:
- Build Verification status
- Test Coverage status
- Standards Compliance status
- Time Tracking Summary
- All code review iterations

### Step 3.5: Calculate Phase Times

1. **Phase Started**: (from phase header)
2. **Phase Completed**: (current timestamp)
3. **Total Elapsed Time**: Completed - Started
4. **Total Active Work Time**: Sum of all task durations
5. **Variance**: Compare estimated vs actual

### Step 3.6: Update Phase Status

Set phase status to `AWAITING_USER_ACCEPTANCE`:
```markdown
**Status**: AWAITING_USER_ACCEPTANCE
**Phase Completed**: {timestamp}
**Total Elapsed Time**: {elapsed}
**Total Active Work Time**: {active_work}
```

Update FeatureTasks.md Phase Summary with new status.

---

## Step 4: Create LessonsLearned Document

**After each phase completion (before user acceptance)**, create a LessonsLearned document:

### Location
`MemoryBank/LessonsLearned/{{feature_id}}/Phase-{N}-{name}.md`

### Template
```markdown
# Lessons Learned: Phase {N} - {Phase Name}

**Feature ID**: {{feature_id}}
**Phase**: {N} - {Name}
**Date**: {timestamp}

## Summary
{1-2 paragraph summary of what was implemented in this phase}

## What Went Well
- {Positive outcome 1}
- {Positive outcome 2}
- {Positive outcome 3}

## Challenges Encountered
- {Challenge 1}: {How it was resolved}
- {Challenge 2}: {How it was resolved}

## Technical Decisions
| Decision | Choice Made | Rationale |
|----------|-------------|-----------|
| {Decision 1} | {Choice} | {Why} |
| {Decision 2} | {Choice} | {Why} |

## Patterns Discovered
{Any reusable patterns or solutions discovered during implementation}

## Recommendations for Future
- {Recommendation 1}
- {Recommendation 2}

## Time Analysis
- Estimated: {estimated_time}
- Actual: {actual_time}
- Variance: {variance}
- Reason for variance: {explanation}

## Files Changed
| File | Type | Changes |
|------|------|---------|
| {file1} | {New/Modified} | {Brief description} |
| {file2} | {New/Modified} | {Brief description} |
```

---

## Step 5: Request User Acceptance

Present a comprehensive phase completion summary:

```markdown
## Phase {N} Complete - Awaiting User Acceptance

**All Technical Requirements Met:**
- All tasks completed: {task_count} tasks
- Build: {build_status}
- Tests: {test_status}
- Code Review: {review_status}
- Git commits recorded: {commit_count} commits

**Phase Achievements:**
- {Achievement 1}
- {Achievement 2}
- {Achievement 3}

**Time Summary:**
- Estimated: {estimated}
- Actual: {actual}
- Variance: {variance}

**LessonsLearned Document:** Created at {path}

**Ready for User Review:**
Please review the implementation and provide acceptance to proceed to Phase {N+1}.

**To Accept**: Reply "I accept Phase {N}" or "Phase {N} looks good"
**To Reject**: Provide specific feedback on what needs adjustment
```

**WAIT for user response** - Do not proceed without explicit user acceptance.

---

## Step 6: Handle User Response

### If User Accepts

1. **Update Phase Status to COMPLETED**:
   ```markdown
   **Status**: COMPLETED
   ```

2. **Update FeatureTasks.md**:
   - Phase row status → `COMPLETED`
   - Actual times filled in

3. **Create Phase Completion Git Commit**:
   ```
   feat({feature_id}): Complete Phase {N} - {Phase Name}

   Phase {N} Achievements:
   - {achievement 1}
   - {achievement 2}
   - {achievement 3}

   Implementation Summary:
   - Tasks completed: {count}
   - Build: {status}
   - Tests: {status}

   Time: {actual} (estimated: {estimated})

   Generated with Claude Code
   ```

4. **Push to Remote** (if git connected)

5. **Present Next Phase Preview**:
   ```markdown
   Phase {N} Marked as COMPLETED

   Next Phase: Phase {N+1} - {Name}
   Status: PENDING
   Estimated Time: {estimate}

   Ready to start Phase {N+1}?
   ```

### If User Rejects

1. Document feedback in phase notes
2. Update phase status back to `IN_PROGRESS`
3. Address the feedback
4. Re-run validation when fixes complete
5. Request acceptance again

---

## Step 7: Feature Completion

When ALL phases are `COMPLETED`:

1. **Update FeatureTasks.md**:
   - All phases should show `COMPLETED`
   - Calculate total feature time

2. **Move Feature Folder**:
   ```
   Move from: MemoryBank/Features/03_IN_PROGRESS/{{feature_id}}-{name}/
   Move to:   MemoryBank/Features/04_COMPLETED/{{feature_id}}-{name}/
   ```

3. **Create Feature Completion Summary**:
   Save to feature folder as `feature-completion-report.md`:
   ```markdown
   # Feature Completion Report: {{feature_id}}

   **Feature**: {Feature Title}
   **Completed**: {timestamp}

   ## Summary
   {Feature description and what was achieved}

   ## Phases Completed
   | Phase | Name | Estimated | Actual | Variance |
   |-------|------|-----------|--------|----------|
   | 1 | ... | ... | ... | ... |

   ## Total Time
   - Estimated: {total_estimated}
   - Actual: {total_actual}
   - Variance: {variance}

   ## Key Deliverables
   - {Deliverable 1}
   - {Deliverable 2}

   ## LessonsLearned Documents
   - Phase 1: {path}
   - Phase 2: {path}
   ...
   ```

4. **Final Git Commit**:
   ```
   feat({feature_id}): Complete Feature - {Feature Title}

   Feature fully implemented across {N} phases.
   Total time: {actual} (estimated: {estimated})

   Generated with Claude Code
   ```

5. **Report Completion**:
   ```markdown
   Feature {{feature_id}} COMPLETED

   Feature has been moved to 04_COMPLETED.
   All {N} phases implemented successfully.
   Total time: {actual}

   Completion report: {path}
   ```

---

## Error Handling

### Feature Not Found
```
Feature {{feature_id}} not found in MemoryBank/Features/.
Please verify the feature ID and current status.
```

### Phase Files Missing
```
Required phase file not found: Phases/phase-{N}-{name}.md
Feature may not have been properly refined. Run refine-feature first.
```

### Build Command Not Configured
```
Build command not found in project documentation.
Please provide the build command for this project.
```

### Test Command Not Configured
```
Test command not found in project documentation.
Please provide the test command for this project.
```

### Maximum Retry Exceeded
```
Maximum retry attempts (3) exceeded for {build/test}.
Manual intervention required.

Last error:
{error_details}

Please fix the issue and run continue-implementation again.
```

---

## Quality Gates

Every phase MUST pass these gates before completion:

1. **All Tasks COMPLETED**: Every task in the phase must be `[COMPLETED]`
2. **Git Commits Tracked**: Every task must have its commits documented in the Git Commits table
3. **Git Commits Summary**: Phase checkpoint must have complete Git Commits (Phase Summary) table
4. **Build Clean**: 0 errors, 0 warnings
5. **Lint Clean**: 0 errors, 0 warnings (if lint is configured)
6. **Tests Passing**: 100% pass rate
7. **Code Review APPROVED**: If required for the phase type (latest review must be APPROVED or APPROVED_WITH_NOTES)
8. **Code Review History**: All reviews documented in Code Review History table
9. **LessonsLearned Created**: Document created for the phase
10. **User Acceptance**: Explicit approval from user via `accept-phase` command

**No shortcuts allowed** - All gates must pass before moving to next phase.

> 🔴 **The `accept-phase` command validates ALL of these requirements**. If any are missing, the phase will be REJECTED.

---

## Status Icons Reference

- `PENDING` - Not yet started
- `IN_PROGRESS` - Currently being worked on
- `AWAITING_USER_ACCEPTANCE` - Complete, awaiting approval
- `COMPLETED` - Finished and approved
- `BLOCKED` - Cannot proceed due to external issue

---

## Let's Begin!

When this procedure is invoked, start from **Step 0: Locate and Validate the Feature** and proceed through the workflow based on the detected entry point.

Remember:
- Quality over speed
- Every task completed according to its specification
- Every phase reviewed and approved
- Every lesson captured for future reference
