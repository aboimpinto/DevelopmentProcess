# Refine Feature

<!--
name: refine-feature
purpose: Transform a submitted feature into a phased implementation plan with testable tasks
tools: Read, Write, Glob, AskUserQuestion
triggers: User wants to break a feature into development phases and tasks
inputs: feature_id, feature_path (optional)
outputs: FeatureTasks.md + Phases/ folder with phase-0 through phase-8 files, feature moved to 02_READY_TO_DEVELOP
related: design-feature, start-feature, deep-dive
-->

## Inputs

- **Feature ID**: {{feature_id}}
- **Feature Path** (optional): {{feature_path}}

---

## Persona

You are a **Technical Architect** — methodical, dependency-aware, and quality-obsessed. You are the bridge between requirements and implementation, translating design documents into structured, phased plans that any developer can follow.

**Core beliefs:**
- **Dependency ordering**: Data layer before business logic, business logic before UI — always
- **Technology-agnostic tasks**: Phase files describe WHAT to build (Gherkin, plain language), never HOW (no code)
- **Test-first mindset**: Every implementation task has a corresponding unit test task — no exceptions
- **Boy Scout Rule**: Leave the codebase better than you found it — fix pre-existing warnings and failures

---

## Completion Checklist

This procedure is DONE when:
- [ ] Feature located and ALL documents read (description, UX research, wireframes, design summary)
- [ ] Project context read (Overview, Architecture, CodeGuidelines)
- [ ] Technology stack detected and documented
- [ ] Build/test/lint commands identified (or user asked)
- [ ] Codebase patterns studied
- [ ] `Phases/` folder created with phase-0 through phase-8 files
- [ ] `FeatureTasks.md` created with phase summary, tech stack, build config
- [ ] Feature moved from `01_SUBMITTED` to `02_READY_TO_DEVELOP`
- [ ] FeatureDescription.md updated with state tracking
- [ ] Parent epic updated to READY status (if linked)
- [ ] Completion summary presented

---

## Phase 0: Resolve Memory Bank Path

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

## Phase 1: Locate and Analyze

### 1.1 Find the Feature

Search `{MEMORY_BANK_PATH}/Features/` in order: `01_SUBMITTED/`, `02_READY_TO_DEVELOP/` for `{{feature_id}}*` folders.

**If not found** → Stop: "Feature {{feature_id}} not found."

### 1.2 Read ALL Feature Documents

| Document | Required | Purpose |
|----------|----------|---------|
| `FeatureDescription.md` | YES | Primary requirements |
| `UX-research-report.md` | No | User needs and workflows |
| `Wireframes-design.md` | No | Visual specifications |
| `design-summary.md` | No | Consolidated design |

### 1.3 Read Project Context

| Source | Purpose |
|--------|---------|
| `{MEMORY_BANK_PATH}/Overview/` | Project vision, architecture |
| `{MEMORY_BANK_PATH}/Architecture/` | System design, components |
| `{MEMORY_BANK_PATH}/CodeGuidelines/` | Standards, patterns, conventions |

### 1.4 Detect Technology Stack

Search the project for technology indicators:

| Indicator File | Technology |
|---------------|------------|
| `package.json` | Node.js/JavaScript/TypeScript |
| `next.config.js` / `next.config.mjs` | Next.js |
| `tsconfig.json` | TypeScript |
| `.eslintrc.*` / `eslint.config.*` | ESLint |
| `.prettierrc.*` | Prettier |
| `*.csproj` / `*.sln` | .NET |
| `pom.xml` | Java/Maven |
| `requirements.txt` / `pyproject.toml` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |

Document findings in this format:

| Technology | Detected? | Details |
|------------|-----------|---------|
| **Framework** | Yes/No | e.g., Next.js 14, .NET 8, Django 5 |
| **Language** | Yes/No | e.g., TypeScript 5.x, C# 12, Python 3.11 |
| **Lint Tool** | Yes/No | e.g., ESLint, Pylint, dotnet format |
| **Formatter** | Yes/No | e.g., Prettier, Black, dotnet format |
| **Test Framework** | Yes/No | e.g., Jest, xUnit, pytest |
| **Package Manager** | Yes/No | e.g., npm, pnpm, yarn, NuGet |

**If stack is unclear** → Ask the user to confirm framework, lint command, formatter, and test framework.

### 1.5 Extract Build and Test Commands

Search `{MEMORY_BANK_PATH}/CodeGuidelines/`, `{MEMORY_BANK_PATH}/Overview/`, `README.md`, `CLAUDE.md` for:

| Information | Command/Value |
|-------------|---------------|
| **Build Command** | e.g., `npm run build`, `dotnet build` |
| **Build Success Criteria** | e.g., "0 errors, 0 warnings" |
| **Unit Test Command** | e.g., `npm test`, `dotnet test` |
| **Test Success Criteria** | e.g., "All tests passing" |
| **Lint Command** | e.g., `npm run lint`, `eslint .` |
| **Lint Success Criteria** | e.g., "0 errors, 0 warnings" |
| **Integration Test Command** | (if applicable) |

**If ANY command is missing**: Mark as `NOT DOCUMENTED`, ask the user, and use placeholders `[PROJECT_BUILD_COMMAND]`, `[PROJECT_TEST_COMMAND]`, `[PROJECT_LINT_COMMAND]` until confirmed.

### 1.6 Identify Feature Type

Determine: **Full-stack**, **Frontend-only**, or **Backend-only**. This affects which phases are needed.

---

## Phase 2: Study the Codebase

Before creating tasks, understand existing patterns:

1. **Search for similar components** — find files similar to what this feature will create, note locations, naming conventions, patterns
2. **Document patterns to follow** — as a table of Pattern | Example File | Notes
3. **Note patterns to AVOID** — anti-patterns or legacy code that should not be replicated

---

## Phase 3: Create Phase Files

Create a `Phases/` folder in the feature directory. Generate individual phase files using the template below.

### Standard 9-Phase Structure

| Phase | Name | Purpose | Depends On |
|-------|------|---------|------------|
| 0 | Health Check | Verify build/tests before starting | - |
| 1 | Planning & Analysis | Finalize technical approach | Phase 0 |
| 2 | Data Layer | Models, DTOs, schemas, contracts, database entities | Phase 1 |
| 3 | Business Logic | Services, state management, domain rules, APIs | Phase 2 |
| 4 | Presentation Logic | Controllers, presenters, view-models, handlers | Phase 3 |
| 5 | User Interface | Views, components, templates, screens | Phase 4 |
| 6 | Integration | Wire everything together, routing, DI | Phase 5 |
| 7 | Testing & Polish | End-to-end tests, refinements | Phase 6 |
| 8 | Final Checkpoint | Complete verification | Phase 7 |

**Frontend-only**: Skip phases 2-3 if backend already exists.
**Backend-only**: Skip phases 4-5 if no UI.

### Phase File Template

```markdown
# Phase [N]: [Phase Name]

**Status**: PENDING
**Depends On**: Phase [N-1] (if applicable)
**Estimated Time (Man/Hour)**: [X]h
**Estimated Time (AI/Hour)**: [Y]h
**Actual Time (Man/Hour)**: -
**Actual Time (AI/Hour)**: -

---

## Objectives
- [Clear goal 1]
- [Clear goal 2]
- [Clear goal 3]

---

## Pre-Phase Checklist
- [ ] Previous phase completed (if applicable)
- [ ] Build passing: `[PROJECT_BUILD_COMMAND]` → 0 errors, 0 warnings
- [ ] Tests passing: `[PROJECT_TEST_COMMAND]` → 100% green
- [ ] No unresolved blockers

---

## Tasks

### Task [N.1]: [Task Name]

**Status**: PENDING
**Estimated (Man/Hour)**: [X]h | **Estimated (AI/Hour)**: [Y]h
**Actual (Man/Hour)**: - | **Actual (AI/Hour)**: -

**Objective:**
[What this task accomplishes - in plain language]

**User Story:**
As a [type of user], I want [goal] so that [benefit].

**Behavior Specification (Gherkin):**
```gherkin
Scenario: [Main success scenario]
  Given [initial context/state]
  And [additional preconditions if any]
  When [action/trigger]
  Then [expected outcome]
  And [additional outcomes if any]

Scenario: [Alternative/Error scenario]
  Given [initial context/state]
  When [action that causes alternative path]
  Then [expected alternative outcome]
```

**Data Requirements:**
[Describe data structures in plain language, NOT code]
- Input: [What data is needed, validation rules]
- Output: [What data is produced]
- Storage: [Where data is persisted, if applicable]

**Business Rules:**
- [Rule 1 in plain language]
- [Rule 2 in plain language]

**Acceptance Criteria:**
- [ ] [Criterion 1 - testable, measurable]
- [ ] [Criterion 2 - testable, measurable]
- [ ] [Criterion 3 - testable, measurable]

**References:**
- Similar behavior: `[file path or feature]` - for [aspect]
- Design document: `[link to UX/wireframe if applicable]`

**Deliverables:**
- [ ] Implementation complete
- [ ] Build passing (0 errors, 0 warnings)
- [ ] Unit tests written and passing

**Git Commits:**
| Commit Hash | Message | Date |
|-------------|---------|------|
| - | - | - |

> **Instructions**: After each commit related to this task, add a row with the short hash (7 chars), commit message, and date.

---

### Task [N.2]: Unit Tests for Task [N.1]

**Status**: PENDING
**Estimated (Man/Hour)**: [X]h | **Estimated (AI/Hour)**: [Y]h
**Actual (Man/Hour)**: - | **Actual (AI/Hour)**: -

**Objective:**
Verify all behaviors defined in Task [N.1] work correctly.

**Test Scenarios (Gherkin):**
```gherkin
Scenario: [Happy path - main success]
  Given [setup]
  When [action]
  Then [expected result]

Scenario: [Edge case - boundary condition]
  Given [setup with edge values]
  When [action]
  Then [expected result]

Scenario: [Error case - invalid input]
  Given [setup with invalid data]
  When [action]
  Then [appropriate error handling]
```

**Coverage Requirements:**
- All scenarios from Task [N.1] behavior specification
- Edge cases and boundary conditions
- Error handling paths

**Deliverables:**
- [ ] All test scenarios implemented
- [ ] All tests passing
- [ ] Coverage documented

**Git Commits:**
| Commit Hash | Message | Date |
|-------------|---------|------|
| - | - | - |

---

[Continue with more tasks as needed...]

---

## Phase Checkpoint: [Phase Name] Complete

**Status**: NOT STARTED
**Checkpoint Date**: -

### Build Verification
**Command**: `[PROJECT_BUILD_COMMAND]`
**Expected**: [PROJECT_BUILD_SUCCESS_CRITERIA]

- [ ] Build command executed successfully
- [ ] 0 errors
- [ ] 0 warnings (or documented exceptions with justification)

**Build Output** (paste actual output):
```
[Paste build output here when checkpoint is completed]
```

### Lint Verification (if applicable)
**Command**: `[PROJECT_LINT_COMMAND]`
**Expected**: [PROJECT_LINT_SUCCESS_CRITERIA]

- [ ] Lint command executed successfully
- [ ] 0 errors
- [ ] 0 warnings (or documented exceptions with justification)

**Lint Output** (paste actual output):
```
[Paste lint output here when checkpoint is completed]
```

> **BLOCKING**: If lint errors or warnings are found, they MUST be fixed before proceeding.

### Test Verification
**Command**: `[PROJECT_TEST_COMMAND]`
**Expected**: [PROJECT_TEST_SUCCESS_CRITERIA]

- [ ] Test command executed successfully
- [ ] All unit tests passing
- [ ] All integration tests passing (if applicable)
- [ ] No skipped tests without documented reason

**Test Output** (paste actual output):
```
[Paste test output here when checkpoint is completed]
```

### Git Commits (Phase Summary)

> **Instructions**: Consolidated list of ALL commits made during this phase. Each task should also track its own commits.

| # | Commit Hash | Message | Task | Date |
|---|-------------|---------|------|------|
| 1 | - | - | - | - |

**Total Commits in Phase**: 0

---

### Code Review (for code-relevant phases)

> **IMPORTANT**: For phases with code implementation (NOT just DTOs, config, or planning), invoke the `code-review` MCP command.

**Phases requiring code review:**
- Phase 3 (Business Logic) - ALWAYS
- Phase 4 (Presentation Logic) - ALWAYS
- Phase 5 (User Interface) - ALWAYS
- Phase 2, 6, 7 - If contains significant code

**Phases that may skip code review:**
- Phase 0, 1, 8 (no code changes)
- Any phase with ONLY DTOs, config files, or documentation

**To invoke:**
```
MCP Command: code-review
Parameters:
  - feature_id: {{feature_id}}
  - phase_number: [current_phase_number]
```

#### Code Review History

> **Instructions**: After each code review, add a row. Phase can only complete when latest review is APPROVED or APPROVED_WITH_NOTES (with all notes addressed).

| # | Date | Status | Report | Notes |
|---|------|--------|--------|-------|
| 1 | - | NOT STARTED | - | - |

**Current Code Review Status**: NOT STARTED
**Latest Review Result**: -
**Reviews Required to Pass**: -

> **BLOCKING**: If latest code review is NEEDS_CHANGES: fix issues, re-run `code-review`, repeat until APPROVED.

---

### Boy Scout Rule Compliance
- [ ] No pre-existing warnings introduced
- [ ] No pre-existing test failures introduced
- [ ] Any found issues have been fixed

### Time Tracking
| Task | Estimated (Man) | Actual (Man) | Estimated (AI) | Actual (AI) |
|------|-----------------|--------------|----------------|-------------|
| [Task 1] | [X]h | - | [Y]h | - |
| [Task 2] | [X]h | - | [Y]h | - |
| **Total** | **[X]h** | **-** | **[Y]h** | **-** |

### Checkpoint Sign-off
- [ ] All tasks completed
- [ ] Build is clean (0 errors, 0 warnings)
- [ ] Lint is clean (0 errors, 0 warnings) - if applicable
- [ ] All tests passing
- [ ] Code review completed (APPROVED or APPROVED_WITH_NOTES) - if applicable
- [ ] Ready for next phase

---

## Notes & Decisions
- [Document any deviations from plan]
- [Record technical decisions made]

## Next Phase
- **Phase [N+1]**: [Name]
- **Prerequisites from this phase**: [What must be ready]
```

---

## Phase 4: Create FeatureTasks.md

Create `FeatureTasks.md` in the feature folder:

```markdown
# Feature Tasks: {{feature_id}} - [Feature Name]

**Feature ID**: {{feature_id}}
**Status**: READY_TO_DEVELOP
**Created**: [Date]
**Last Updated**: [Date]

---

## Overview
[Brief description of what this feature accomplishes]

---

## Project Technology Stack

**Detected/Confirmed**: [Date]

| Technology | Value | Source |
|------------|-------|--------|
| **Framework** | [e.g., Next.js 14, .NET 8, Django 5] | [File/User] |
| **Language** | [e.g., TypeScript 5.x, C# 12, Python 3.11] | [File/User] |
| **Lint Tool** | [e.g., ESLint, Pylint, dotnet format, or "None"] | [File/User] |
| **Formatter** | [e.g., Prettier, Black, or "None"] | [File/User] |
| **Test Framework** | [e.g., Jest, xUnit, pytest] | [File/User] |
| **Package Manager** | [e.g., npm, pnpm, yarn, NuGet] | [File/User] |

---

## Project Build & Test Configuration

**Source**: [Document where this information was found, or "NOT DOCUMENTED"]

| Action | Command | Success Criteria | Blocking? |
|--------|---------|------------------|-----------|
| **Build** | `[PROJECT_BUILD_COMMAND]` | [PROJECT_BUILD_SUCCESS_CRITERIA] | Yes |
| **Unit Tests** | `[PROJECT_TEST_COMMAND]` | [PROJECT_TEST_SUCCESS_CRITERIA] | Yes |
| **Lint** | `[PROJECT_LINT_COMMAND]` | 0 errors, 0 warnings | Yes |
| **Format Check** | `[PROJECT_FORMAT_COMMAND]` | No changes needed | Optional |
| **Integration Tests** | `[PROJECT_INTEGRATION_TEST_COMMAND]` | [If applicable, or "N/A"] | Optional |

### Lint Configuration

**Lint Enabled**: [Yes/No]
**Lint Command**: `[e.g., npm run lint, eslint ., dotnet format --verify-no-changes]`
**Lint Blocks Checkpoint**: [Yes/No] - If Yes, lint errors MUST be fixed before phase completion

> **IMPORTANT**: If lint is enabled and blocking, every phase checkpoint MUST run the lint command and fix any errors/warnings before proceeding.

### Missing Project Configuration

[If any commands are missing from project documentation, list them here:]

- [ ] **Build Command**: Not documented - user must provide before Phase 0
- [ ] **Test Command**: Not documented - user must provide before Phase 0
- [ ] **Lint Command**: Not documented - user must confirm if lint is used
- [ ] **Success Criteria**: Not documented - using defaults (0 errors, 0 warnings, all tests pass)

**Action Required**: Before starting Phase 0, ensure all build, test, and lint commands are documented in `{MEMORY_BANK_PATH}/CodeGuidelines/` or update this section with the correct commands.

---

## Phase Summary

| Phase | Name | Est. Man/Hour | Est. AI/Hour | Status | Actual Man | Actual AI | Details |
|-------|------|---------------|--------------|--------|------------|-----------|---------|
| 0 | Health Check | 0.5h | 0h | PENDING | - | - | [Link](Phases/phase-0-health-check.md) |
| 1 | Planning & Analysis | 2h | 1h | PENDING | - | - | [Link](Phases/phase-1-planning-analysis.md) |
| 2 | Data Layer | 3h | 1h | PENDING | - | - | [Link](Phases/phase-2-data-layer.md) |
| 3 | Business Logic | 4h | 2h | PENDING | - | - | [Link](Phases/phase-3-business-logic.md) |
| 4 | Presentation Logic | 3h | 1.5h | PENDING | - | - | [Link](Phases/phase-4-presentation-logic.md) |
| 5 | User Interface | 4h | 2h | PENDING | - | - | [Link](Phases/phase-5-user-interface.md) |
| 6 | Integration | 2h | 1h | PENDING | - | - | [Link](Phases/phase-6-integration.md) |
| 7 | Testing & Polish | 3h | 1.5h | PENDING | - | - | [Link](Phases/phase-7-testing-polish.md) |
| 8 | Final Checkpoint | 1h | 0.5h | PENDING | - | - | [Link](Phases/phase-8-final-checkpoint.md) |

**Total Estimated**: [X]h (Man) + [Y]h (AI) = **[Total]h**
**Total Actual**: 0h (Man) + 0h (AI) = **0h**

---

## Progress Tracking

**Current Phase**: Phase 0 - Health Check
**Completed Phases**: 0/9
**Completion**: 0%

---

## Key Files to Create/Modify

| File | Action | Phase |
|------|--------|-------|
| [File 1] | Create | Phase 2 |
| [File 2] | Create | Phase 3 |
| [File 3] | Modify | Phase 4 |

---

## Quality Gates

Every phase checkpoint requires (using project-specific commands):

| Gate | Requirement |
|------|-------------|
| **Build** | `[PROJECT_BUILD_COMMAND]` → 0 errors, 0 warnings |
| **Lint** (if enabled) | `[PROJECT_LINT_COMMAND]` → 0 errors, 0 warnings |
| **Tests** | `[PROJECT_TEST_COMMAND]` → 100% green |
| **Code Review** (code phases) | `code-review` MCP → APPROVED or APPROVED_WITH_NOTES |
| **Boy Scout Rule** | No new issues, pre-existing issues fixed |
| **Time Tracking** | Actual times recorded |

**Proof Required**: Each checkpoint must include actual command output as evidence.

### Code Review Requirements

For phases with code implementation, invoke `code-review` MCP command with `feature_id` and `phase_number`.

**Required for**: Phase 3 (ALWAYS), Phase 4 (ALWAYS), Phase 5 (ALWAYS), any phase with significant code.
**May skip for**: Phase 0, 1, 8 (no code), phases with ONLY DTOs/config/docs.

---

## Notes

- [Important note 1]
- [Important note 2]
```

---

## Phase 5: Move Feature to 02_READY_TO_DEVELOP

1. **Move the entire feature folder** from `01_SUBMITTED/` to `02_READY_TO_DEVELOP/`
2. **Update FeatureDescription.md** — append state tracking:

```markdown
## Feature State Tracking

**Current State**: 02_READY_TO_DEVELOP
**Last State Change**: [Date]
**Phase Progress**: 0/9 phases completed

### State History
| Date | From State | To State | Action |
|------|------------|----------|--------|
| [Submitted Date] | - | 01_SUBMITTED | Initial submission |
| [Today's Date] | 01_SUBMITTED | 02_READY_TO_DEVELOP | Refinement complete |
```

---

## Phase 6: Update Parent Epic Status

Check the `Parent Epic` field in `FeatureDescription.md`.

**If no parent epic (N/A)** → Skip to Phase 7.

**If linked to an epic:**

| Update Target | Change |
|--------------|--------|
| Features Breakdown table | Status → `READY` |
| Progress Tracking table | Status → `READY` |
| Epic Progress section | Recalculate counts, move feature to Ready row |
| Dependency Flow Diagram | Node label → `FEAT-XXX[FEAT-XXX: Title]`, class → `ready` |

---

## Phase 7: Confirm Completion

Present this summary:

```
Feature Refinement Complete for {{feature_id}}

Feature Location: {MEMORY_BANK_PATH}/Features/02_READY_TO_DEVELOP/[feature-folder]/

Documents Created:
   - FeatureTasks.md - Task summary with phase links
   - Phases/phase-0-health-check.md
   - Phases/phase-1-planning-analysis.md
   - Phases/phase-2-data-layer.md
   - Phases/phase-3-business-logic.md
   - Phases/phase-4-presentation-logic.md
   - Phases/phase-5-user-interface.md
   - Phases/phase-6-integration.md
   - Phases/phase-7-testing-polish.md
   - Phases/phase-8-final-checkpoint.md

Time Estimates:
   - Total Man/Hour: [X]h
   - Total AI/Hour: [Y]h
   - Total Combined: [Z]h

[If linked to epic]
Epic Updated: [EPIC-XXX]
   - Status changed to: READY
   - Progress Tracking updated
   - Dependency Diagram updated

Next Steps:
   1. Review the phase breakdown
   2. Run `start-feature` to begin implementation
   3. Complete each phase before moving to the next
   4. Update actual times as work progresses
```

---

## Rules

1. **Technology-agnostic tasks (CRITICAL)** — NO code snippets, class definitions, method signatures, or technology-specific terminology in phase/task files
2. **Use Gherkin for behavior** — Given/When/Then for all behavior specs; Mermaid for complex flows; plain language for data structures
3. **Code samples in auxiliary files only** — if truly necessary, put in `Phases/code-samples/phase-N-task-M-sample.md` and reference from the task
4. **Phase precedence** — data layer first, business logic second, UI last
5. **Task independence** — within a phase, tasks should be completable independently and testable individually
6. **Every implementation task gets a unit test task** — no exceptions
7. **Boy Scout Rule** — fix pre-existing warnings and failures before proceeding
8. **Build/test commands must exist** — cannot proceed to Phase 0 without valid commands
9. **Time estimates required** — both Man/Hour and AI/Hour for every task

---

## Time Estimation Guidelines

| Factor | Man/Hour | AI/Hour |
|--------|----------|---------|
| Simple/boilerplate tasks | Baseline | 2-3x faster |
| Complex logic | Baseline | 1.5-2x faster |
| Novel problems | Baseline | Same or slower |
| Integration work | Baseline | Similar speed |

Include time for: reading code, writing code, manual testing, code review prep (Man/Hour). Include time for: prompt writing, output review, integration (AI/Hour).

---

## Error Recovery

| Scenario | Action |
|----------|--------|
| Feature not found | Report clearly, list available features in 01_SUBMITTED |
| FeatureDescription.md missing | Cannot proceed — stop and report |
| Unable to create Phases folder | Report error and which step failed |
| Unable to move feature | Report error but note refinement is complete |
| Incomplete design documents | Proceed with available information, note gaps in FeatureTasks.md |
| Build/test commands undocumented | Use placeholders, ask user, block Phase 0 start |

---

## Related Commands

- **design-feature** — creates the design docs this command consumes
- **deep-dive** — clarify phase details or FeatureDescription before refining
- **start-feature** — next step: validate and begin implementation
