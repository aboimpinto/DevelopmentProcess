# Start Feature - MCP Procedure

You are executing the **Start Feature** procedure for the DevCycleManager. This procedure validates a feature and transitions it from `02_READY_TO_DEVELOP` to `03_IN_PROGRESS`.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Feature Path** (if provided): {{feature_path}}

---

## Purpose

This procedure is the **quality gate before implementation begins**. It:
1. **Pre-validates** the feature for consistency and completeness
2. **Post-validates** the documentation for accuracy and format
3. Creates a **git branch** for the feature (if connected to git)
4. **Moves** the feature to `03_IN_PROGRESS`
5. **Commits and pushes** the changes (if connected to git)

**If any validation fails, the process STOPS with a detailed report.**

---

## Overview of Steps

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 0: Locate Feature in 02_READY_TO_DEVELOP                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: PRE-VALIDATION                                         │
│  - Consistency check                                            │
│  - Completeness check                                           │
│  - Ambiguity detection                                          │
│  → If FAIL: Generate rejection report, STOP                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                         ✅ PASS
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: POST-VALIDATION                                        │
│  - Time tracking fields present                                 │
│  - Calculations correct                                         │
│  - Checkpoints in place                                         │
│  - Git commit placeholders ready                                │
│  → If issues found: AUTO-FIX and document                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                         ✅ COMPLETE
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Git Branch Creation (if connected to git)              │
│  - Create feature branch: feat/[feature-name]                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Move Feature to 03_IN_PROGRESS                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Git Commit & Push (if connected to git)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Generate Success Report                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 0: Locate the Feature

Search for the feature folder in `MemoryBank/Features/02_READY_TO_DEVELOP/`:
1. Look for folders matching `{{feature_id}}*`
2. Verify `FeatureDescription.md` exists
3. Verify `FeatureTasks.md` exists
4. Verify `Phases/` folder exists with phase files

**If the feature is not found:** Stop and report: "Feature {{feature_id}} not found in 02_READY_TO_DEVELOP."

**Required files checklist:**
- [ ] `FeatureDescription.md`
- [ ] `FeatureTasks.md`
- [ ] `Phases/` folder with at least one phase file

---

## Step 1: PRE-VALIDATION (Consistency & Completeness)

**Mindset: ZERO TOLERANCE for ambiguity. If uncertain, REJECT.**

The pre-validation checks if the feature documentation is complete enough to implement without guessing.

### 1.1 Documentation Consistency Check

Read ALL documents and verify they are consistent:

| Check | Description | Action if Failed |
|-------|-------------|------------------|
| **Feature ID Match** | Feature ID is consistent across all documents | REJECT |
| **Title/Name Match** | Feature name is consistent | REJECT |
| **Scope Alignment** | FeatureDescription scope matches FeatureTasks scope | REJECT |
| **Phase Coverage** | All requirements have corresponding tasks | REJECT |

### 1.2 Completeness Check

Verify all necessary information is present:

**For Full-Stack Features (UI + Backend):**
- [ ] UI design documents exist (wireframes, mockups, or design-summary.md)
- [ ] All screens/views are documented
- [ ] All user interactions are defined
- [ ] All form validations are specified
- [ ] Backend contracts/APIs are documented
- [ ] Data models are defined

**For Backend-Only Features:**
- [ ] API contracts are documented
- [ ] Data models are defined
- [ ] Integration points are clear

**For Frontend-Only Features:**
- [ ] UI design documents exist
- [ ] All screens/views are documented
- [ ] All user interactions are defined
- [ ] Backend APIs it consumes are referenced

### 1.3 Ambiguity Detection (CRITICAL)

**Read every task in every phase file and ask: "Can I implement this without guessing?"**

Look for ambiguous language:
- ❌ "Handle errors appropriately" → HOW? What errors? What messages?
- ❌ "Add validation" → WHAT validation rules?
- ❌ "Display data" → WHAT data? In what format?
- ❌ "Similar to existing feature" → WHICH feature? WHAT aspects?
- ❌ "Support multiple formats" → WHICH formats specifically?

**If ANY task requires "creativity" or "interpretation" to implement, REJECT.**

### 1.4 Technology-Agnostic Documentation Check (CRITICAL)

**Phase and Task files MUST be readable by both business analysts and developers.**

#### Scan for Code in Phase/Task Files

Search ALL phase files for code patterns that should NOT be there:

**Code patterns to REJECT:**
- ❌ Code blocks with programming languages (```csharp, ```javascript, ```python, ```java, ```typescript, etc.)
- ❌ Class/interface definitions (`class`, `interface`, `struct`, `enum` keywords)
- ❌ Method signatures (`public`, `private`, `void`, `async`, `function`, `def`, `func`)
- ❌ Variable declarations with types (`int`, `string`, `bool`, `var`, `let`, `const`)
- ❌ Import/using statements (`import`, `using`, `require`, `from`)
- ❌ Framework-specific syntax (decorators like `@Injectable`, `[Attribute]`, etc.)

**Allowed formats:**
- ✅ Gherkin (Given/When/Then) for behavior specifications
- ✅ Mermaid flowcharts for logic flows
- ✅ Plain text descriptions of data structures
- ✅ JSON schemas (for data format, not implementation)
- ✅ References to auxiliary code files: `See: code-samples/phase-N-task-M-sample.md`

**If code is found inline:**

Option 1: **REJECT** with specific locations:
```markdown
❌ CODE DETECTED IN PHASE FILES

The following files contain implementation code that should be removed or moved to auxiliary files:

- Phases/phase-2-data-layer.md:
  - Line ~45: Contains C# class definition
  - Line ~78: Contains method implementation

Required Actions:
1. Move code to `Phases/code-samples/` folder
2. Replace with Gherkin behavior specification
3. Or replace with Mermaid flowchart
4. Reference the auxiliary file if code is truly necessary
```

Option 2: **AUTO-FIX** (if straightforward):
1. Create `Phases/code-samples/` folder
2. Move code blocks to appropriately named files
3. Replace inline code with reference: `See implementation example: [code-samples/phase-N-task-M-sample.md]`
4. Document the fix in the report

**Why This Matters:**
- Business analysts must be able to review and validate requirements
- QA can create test cases from Gherkin scenarios
- Developers decide HOW to implement (not told via code snippets)
- Documentation remains valid if technology changes

### 1.5 Project Build/Test Configuration Check

Verify the `FeatureTasks.md` has the **Project Build & Test Configuration** section filled in:

- [ ] Build command is documented (not `[PROJECT_BUILD_COMMAND]` placeholder)
- [ ] Test command is documented (not `[PROJECT_TEST_COMMAND]` placeholder)
- [ ] Success criteria are defined

**If missing:** REJECT with message: "Project build/test commands must be configured before starting implementation."

### 1.6 Pre-Validation Result

**If ALL checks pass:**
```markdown
## Pre-Validation Result: ✅ APPROVED

Feature {{feature_id}} has passed pre-validation:
- Documentation is consistent
- All required information is present
- No ambiguous tasks detected
- No code in phase/task files (technology-agnostic)
- Build/test configuration is complete

Proceeding to post-validation...
```

**If ANY check fails:**
```markdown
## Pre-Validation Result: ❌ REJECTED

Feature {{feature_id}} has FAILED pre-validation.

### Issues Found:

**Consistency Issues:**
- [List any inconsistencies]

**Missing Information:**
- [List missing documentation]

**Ambiguous Tasks:**
- Phase [X], Task [Y]: "[Task description]" - AMBIGUOUS because [reason]
- [List all ambiguous tasks]

**Code Detected in Phase/Task Files:**
- [File]: [Line/Location] - [Description of code found]
- Required action: Move to `Phases/code-samples/` or replace with Gherkin/Mermaid

**Missing Configuration:**
- [List missing build/test configuration]

### Required Actions:

1. [Specific action to fix issue 1]
2. [Specific action to fix issue 2]
3. [Continue for all issues]

### Recommendation:
Re-run `/refine-feature {{feature_id}}` after addressing all issues above.

---
**Status**: REJECTED
**Report saved to**: `02_READY_TO_DEVELOP/[feature-folder]/pre-validation-report-REJECTED-[timestamp].md`
```

**Save the rejection report and STOP. Do not proceed to post-validation.**

---

## Step 2: POST-VALIDATION (Documentation Quality)

**Only execute if pre-validation APPROVED.**

Post-validation ensures the documentation is properly formatted and ready for implementation tracking.

### 2.1 Time Tracking Fields Validation

Check ALL phase files for required time tracking fields:

**Phase Header (required):**
```markdown
**Status**: ⏸️ PENDING
**Estimated Time (Man/Hour)**: [X]h
**Estimated Time (AI/Hour)**: [Y]h
**Actual Time (Man/Hour)**: -
**Actual Time (AI/Hour)**: -
```

**Task Header (required):**
```markdown
**Status**: ⏸️ PENDING
**Estimated (Man/Hour)**: [X]h | **Estimated (AI/Hour)**: [Y]h
**Actual (Man/Hour)**: - | **Actual (AI/Hour)**: -
```

**If missing:** AUTO-FIX by adding the fields with default values.

### 2.2 Time Calculations Validation

Verify all sums are correct in `FeatureTasks.md`:

1. Sum of task estimates in each phase = Phase total
2. Sum of phase totals = Feature total
3. Man/Hour and AI/Hour calculated separately

**If incorrect:** AUTO-FIX by recalculating.

### 2.3 Checkpoint Validation

Verify each phase file has a checkpoint section with:

- [ ] Build verification section with `[PROJECT_BUILD_COMMAND]`
- [ ] Test verification section with `[PROJECT_TEST_COMMAND]`
- [ ] Lint verification section (if lint is configured)
- [ ] Git commits tracking table
- [ ] Code reviews history table
- [ ] Sign-off checklist

**If missing:** AUTO-FIX by adding the checkpoint template.

### 2.4 Git Commit Tracking Validation

Verify EACH task has a **Git Commits** table:

```markdown
**Git Commits:**
| Commit Hash | Message | Date |
|-------------|---------|------|
| - | - | - |
```

**If missing in any task:** AUTO-FIX by adding the Git Commits table after the Deliverables section.

Verify EACH phase checkpoint has a **Git Commits (Phase Summary)** section:

```markdown
### Git Commits (Phase Summary)

| # | Commit Hash | Message | Task | Date |
|---|-------------|---------|------|------|
| 1 | - | - | - | - |

**Total Commits in Phase**: 0
```

**If missing in any phase:** AUTO-FIX by adding the Git Commits summary section to the checkpoint.

### 2.5 Code Review History Validation

Verify EACH phase checkpoint (for code-relevant phases) has a **Code Review History** table:

```markdown
#### Code Review History

| # | Date | Status | Report | Notes |
|---|------|--------|--------|-------|
| 1 | - | ⏸️ NOT STARTED | - | - |

**Current Code Review Status**: ⏸️ NOT STARTED
**Latest Review Result**: -
**Reviews Required to Pass**: -
```

**Code-relevant phases that REQUIRE Code Review History:**
- Phase 2 (Data Layer) - If contains business logic
- Phase 3 (Business Logic) - **ALWAYS**
- Phase 4 (Presentation Logic) - **ALWAYS**
- Phase 5 (User Interface) - **ALWAYS**
- Phase 6 (Integration) - If contains significant code
- Phase 7 (Testing & Polish) - If contains new code

**Phases that may SKIP Code Review History:**
- Phase 0 (Health Check)
- Phase 1 (Planning & Analysis)
- Phase 8 (Final Checkpoint)

**If missing in any code-relevant phase:** AUTO-FIX by adding the Code Review History section to the checkpoint.

### 2.6 Technology Stack Validation (FeatureTasks.md)

Verify `FeatureTasks.md` has a **Project Technology Stack** section:

```markdown
## Project Technology Stack

**Detected/Confirmed**: [Date]

| Technology | Value | Source |
|------------|-------|--------|
| **Framework** | [e.g., Next.js 14] | [File/User] |
| **Language** | [e.g., TypeScript 5.x] | [File/User] |
| **Lint Tool** | [e.g., ESLint or "None"] | [File/User] |
| **Formatter** | [e.g., Prettier or "None"] | [File/User] |
| **Test Framework** | [e.g., Jest] | [File/User] |
| **Package Manager** | [e.g., npm] | [File/User] |
```

**If missing:** AUTO-FIX by adding the section with placeholder values and note: "⚠️ Technology stack needs confirmation from user."

### 2.7 Lint Configuration Validation (FeatureTasks.md)

Verify `FeatureTasks.md` has a **Lint Configuration** section:

```markdown
### Lint Configuration

**Lint Enabled**: [Yes/No]
**Lint Command**: `[e.g., npm run lint]`
**Lint Blocks Checkpoint**: [Yes/No]
```

**If missing:** AUTO-FIX by adding the section with:
- **Lint Enabled**: ⚠️ NOT CONFIGURED
- **Lint Command**: -
- **Lint Blocks Checkpoint**: No (until configured)

And add note: "⚠️ Lint configuration needs confirmation from user before Phase 0 completion."

### 2.8 Post-Validation Summary

Generate a summary of all validations and auto-fixes:

```markdown
## Post-Validation Result: ✅ COMPLETE

### Validations Performed:
- ✅ Time tracking fields: Present in all [X] phase files
- ✅ Time calculations: Verified (Total: [X]h Man + [Y]h AI)
- ✅ Checkpoints: Present in all [X] phases
- ✅ Git commit tracking (per task): Present in all [X] tasks
- ✅ Git commit summary (per phase): Present in all [X] phases
- ✅ Code review history: Present in [X] code-relevant phases
- ✅ Technology stack: Documented in FeatureTasks.md
- ✅ Lint configuration: Documented in FeatureTasks.md

### Auto-Fixes Applied:
- [List any auto-fixes, or "None required"]

**Example auto-fixes:**
- Added Git Commits table to Task 2.1, 2.3
- Added Git Commits (Phase Summary) to Phase 2, Phase 3
- Added Code Review History to Phase 3, Phase 4, Phase 5
- Added Technology Stack section to FeatureTasks.md
- Added Lint Configuration section to FeatureTasks.md

### Warnings (require user attention):
- [List any ⚠️ warnings that need user confirmation, or "None"]

### Feature Summary:
- **Total Phases**: [X]
- **Total Tasks**: [Y]
- **Total Estimated Time**: [Z]h (Man: [A]h, AI: [B]h)
```

---

## Step 3: Git Branch Creation

**Check if the project is connected to git:**

```bash
git status
```

**If connected to git:**

1. Check current branch:
   ```bash
   git branch --show-current
   ```

2. If on `main` or `master`, create feature branch:
   ```bash
   git checkout -b feat/{{feature_id}}-[feature-name-slug]
   ```

3. If already on a feature branch, continue using it.

**Branch naming convention:**
- Format: `feat/{{feature_id}}-[feature-name-slug]`
- Example: `feat/FEAT-001-user-authentication`

**If NOT connected to git:**
- Skip this step
- Note in report: "Not connected to git - branch creation skipped"

---

## Step 4: Move Feature to 03_IN_PROGRESS

Move the entire feature folder:

```
FROM: MemoryBank/Features/02_READY_TO_DEVELOP/[feature-folder]/
TO:   MemoryBank/Features/03_IN_PROGRESS/[feature-folder]/
```

**Update FeatureDescription.md** with state change:

```markdown
## Feature State Tracking

**Current State**: 03_IN_PROGRESS
**Last State Change**: [Today's date]
**Git Branch**: [branch-name or "N/A"]

### State History
| Date | From State | To State | Action |
|------|------------|----------|--------|
| [Original date] | - | 01_SUBMITTED | Initial submission |
| [Design date] | 01_SUBMITTED | 01_SUBMITTED | Design completed |
| [Refine date] | 01_SUBMITTED | 02_READY_TO_DEVELOP | Refinement completed |
| [Today] | 02_READY_TO_DEVELOP | 03_IN_PROGRESS | Implementation started |
```

---

## Step 5: Git Commit & Push

**If connected to git:**

1. Stage the changes:
   ```bash
   git add MemoryBank/Features/
   ```

2. Commit with descriptive message:
   ```bash
   git commit -m "feat({{feature_id}}): Start implementation - move to IN_PROGRESS

   - Pre-validation: APPROVED
   - Post-validation: COMPLETE
   - Branch: [branch-name]
   - Total estimated: [X]h"
   ```

3. Push to remote (if configured):
   ```bash
   git push -u origin [branch-name]
   ```

**If NOT connected to git:**
- Skip this step
- Note in report: "Not connected to git - commit/push skipped"

---

## Step 5.5: Update Parent Epic Status (If Linked)

**Check if the feature has a Parent Epic** by reading the `Parent Epic` field in `FeatureDescription.md`.

**If Parent Epic is NOT "N/A" or "N/A - Standalone Feature":**

1. **Find the epic folder**: `MemoryBank/Features/00_EPICS/{epic_id}-*/`

2. **Read `EpicDescription.md`**

3. **Update Features Breakdown table** - Change status to `IN_PROGRESS`:
   ```
   | FEAT-XXX | Title | IN_PROGRESS | ... | ... |
   ```

4. **Update Progress Tracking table** - Change status and set Started date:
   ```
   | FEAT-XXX | 🔨 IN_PROGRESS | [Today's date] | - | Implementation started |
   ```

5. **Update Epic Progress section**:
   - Recalculate counts in the status table
   - Move feature to 🔨 In Progress row
   - Recalculate progress bar

6. **Update Dependency Flow Diagram**:
   - Change node label: `FEAT-XXX[🔨 FEAT-XXX: Title]`
   - Change class: `class FEAT-XXX inProgress`

7. **Update Epic Status** (if not already IN_PROGRESS):
   - Change `Status` field in metadata to `IN_PROGRESS`

**If feature has no Parent Epic:** Skip this step.

---

## Step 6: Generate Success Report

Create the final report:

```markdown
# Start Feature Report: {{feature_id}}

**Status**: ✅ READY FOR IMPLEMENTATION
**Date**: [Today's date and time]

---

## Validation Summary

### Pre-Validation: ✅ APPROVED
- Documentation consistency: ✅ Passed
- Completeness check: ✅ Passed
- Ambiguity detection: ✅ No issues found
- Build/test configuration: ✅ Complete

### Post-Validation: ✅ COMPLETE
- Time tracking fields: ✅ Verified
- Time calculations: ✅ Correct
- Checkpoints: ✅ Present
- Git commit placeholders: ✅ Ready

---

## Feature Summary

| Item | Value |
|------|-------|
| **Feature ID** | {{feature_id}} |
| **Feature Name** | [Name] |
| **Current State** | 03_IN_PROGRESS |
| **Git Branch** | [branch-name or "N/A"] |
| **Total Phases** | [X] |
| **Total Tasks** | [Y] |
| **Estimated Time (Man)** | [A]h |
| **Estimated Time (AI)** | [B]h |
| **Total Estimated** | [C]h |

---

## Files Location

```
MemoryBank/Features/03_IN_PROGRESS/[feature-folder]/
├── FeatureDescription.md
├── FeatureTasks.md
├── UX-research-report.md (if exists)
├── Wireframes-design.md (if exists)
├── design-summary.md (if exists)
└── Phases/
    ├── phase-0-health-check.md
    ├── phase-1-planning-analysis.md
    ├── phase-2-data-layer.md
    ├── phase-3-business-logic.md
    ├── phase-4-presentation-logic.md
    ├── phase-5-user-interface.md
    ├── phase-6-integration.md
    ├── phase-7-testing-polish.md
    └── phase-8-final-checkpoint.md
```

---

## Epic Status (If Linked)

| Field | Value |
|-------|-------|
| **Parent Epic** | [EPIC-XXX or "N/A"] |
| **Epic Status** | [IN_PROGRESS or "N/A"] |
| **Epic Progress** | [X/Y features complete] |

**Diagram Updated**: [Yes/No/N/A]

---

## Next Steps

1. **Start with Phase 0**: Health Check
   - Verify build passes with 0 errors, 0 warnings
   - Verify all tests pass

2. **Work through phases sequentially**
   - Complete all tasks in a phase
   - Complete phase checkpoint before moving to next phase

3. **Track time as you work**
   - Update actual times in task and phase headers
   - Compare estimates vs actuals

4. **Commit after each significant task**
   - Use the git commit format from deliverables

---

## Reports Generated

- **Pre-validation report**: `03_IN_PROGRESS/[feature-folder]/pre-validation-report-APPROVED-[timestamp].md`
- **Start feature report**: `03_IN_PROGRESS/[feature-folder]/start-feature-report-[timestamp].md`
```

**Save this report to:**
`MemoryBank/Features/03_IN_PROGRESS/[feature-folder]/start-feature-report-[timestamp].md`

---

## Error Handling

### Pre-Validation Failure
- Generate detailed rejection report with specific issues
- Save report to `02_READY_TO_DEVELOP/[feature-folder]/pre-validation-report-REJECTED-[timestamp].md`
- **STOP immediately** - do not proceed to post-validation

### Post-Validation Issues
- Auto-fix where possible
- Document all fixes in the report
- If critical issues cannot be auto-fixed, generate warning but continue

### Git Operations Failure
- If branch creation fails: Continue without branch, note in report
- If commit fails: Continue without commit, note in report
- If push fails: Continue without push, note in report

### Move Operation Failure
- If move fails: Report error with details
- **STOP** - feature state is uncertain

---

## Report Naming Convention

All reports are timestamped:
- `pre-validation-report-[STATUS]-[YYYY-MM-DD-HH-MM].md`
- `start-feature-report-[YYYY-MM-DD-HH-MM].md`

Where STATUS is:
- **APPROVED** - Pre-validation passed
- **REJECTED** - Pre-validation failed

---

## Quick Reference

**Command Flow:**
1. Locate feature in `02_READY_TO_DEVELOP`
2. Run pre-validation → Must pass to continue
3. Run post-validation → Auto-fix issues
4. Create git branch (if git connected)
5. Move to `03_IN_PROGRESS`
6. Commit and push (if git connected)
7. Generate success report

**Key Files Generated:**
- Pre-validation report (always)
- Start feature report (if successful)

**Quality Gates:**
- Pre-validation is STRICT (reject on any ambiguity)
- Post-validation is HELPFUL (auto-fix where possible)
