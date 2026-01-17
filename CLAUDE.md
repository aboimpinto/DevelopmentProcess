# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server for managing a feature development lifecycle. The server runs in Docker and follows a "Recipe Book" (Server) vs "Hands and Eyes" (Client) architecture - the server defines the process, while the client (Gemini CLI, Claude Code) executes file operations and LLM calls.

## Local Environment Setup

### Build and Run the MCP Server

```bash
# Build the Docker image
docker build -t devcycle-mcp .

# Run the container
docker run -d -p 8080:8000 -v "$(pwd)/MemoryBank:/app/MemoryBank" --name devcycle-mcp-local devcycle-mcp

# Verify it's running
curl -X POST http://localhost:8080/ -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Connect Claude Code to the MCP Server

```bash
claude mcp add --transport http devcycle-mcp http://localhost:8080/
```

Verify connection:
```bash
claude mcp list
```

Expected output:
```
devcycle-mcp: http://localhost:8080/ (HTTP) - ✓ Connected
```

Restart Claude Code and run `/mcp` to confirm the tools are available.

To remove:
```bash
claude mcp remove devcycle-mcp
```

### Container Management

```bash
# Stop and remove
docker rm -f devcycle-mcp-local

# View logs
docker logs -f devcycle-mcp-local

# Rebuild after code changes
docker rm -f devcycle-mcp-local && docker build -t devcycle-mcp . && docker run -d -p 8080:8000 -v "$(pwd)/MemoryBank:/app/MemoryBank" --name devcycle-mcp-local devcycle-mcp
```

## Architecture

### Remote Process Model
- **Server**: Stateless "Recipe Book" that holds process knowledge. Returns structured instructions (JSON) telling the client what actions to perform.
- **Client**: Local "Hands and Eyes" that executes file I/O, provides context, and handles LLM calls via the MCP Sampling Protocol.

### MCP Sampling Protocol
The server requests LLM actions via `ctx.session.sample()` rather than directly calling LLM APIs. This means:
- No API keys needed on the server
- LLM calls use the client's existing session and quota
- The client handles all authentication

### Feature State Machine
Features are folders in `MemoryBank/Features/` and their state is determined by location:
- `01_SUBMITTED` → `02_READY_TO_DEVELOP` → `03_IN_PROGRESS` → `04_COMPLETED`
- Also: `05_CANCELLED` for abandoned features

### Key Directories
- `DevCycleManager/` - MCP server Python code (FastAPI + JSON-RPC)
- `DevCycleManager/Prompts/` - External prompt templates and config files
- `MemoryBank/` - Knowledge base and feature storage
- `MemoryBank/Overview/` - Architecture and design documentation

The server exposes a single JSON-RPC endpoint at `/` that handles `initialize`, `tools/list`, and `tools/call` methods.

---

## MCP Commands Reference

The DevCycle MCP Server provides 13 commands that guide features through a complete development lifecycle.

### Feature Lifecycle Overview

```
┌─────────────┐
│  00_EPICS   │ ◄── submit-epic (strategic initiatives)
│             │     └── deep-dive (refine epic details)
│             │     └── create-epic-features (batch create)
└──────┬──────┘
       │ (features linked via epic_id or link-feature-to-epic)
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 01_SUBMITTED │ ──► │ 02_READY_TO │ ──► │ 03_IN_      │ ──► │ 04_COMPLETED│
│              │     │   _DEVELOP  │     │   PROGRESS  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
  submit-feature      refine-feature     start-feature      complete-feature
  design-feature                         continue-implementation
                                         code-review
                                         accept-phase
```

---

### 1. `init-project`

**Purpose**: Initialize the MemoryBank folder structure for a new project.

**When to Use**: First time setup, before any features can be created.

**Parameters**: None

**What It Does**:
- Creates `MemoryBank/` folder structure
- Creates `Features/` with state folders (00_EPICS, 01_SUBMITTED, 02_READY_TO_DEVELOP, etc.)
- Creates `Overview/`, `Architecture/`, `CodeGuidelines/`, `LessonsLearned/` folders
- Adds README files with guidance

**Example**:
```
User: "Initialize a new project"
LLM: Invokes init-project MCP command
```

---

### 2. `submit-epic`

**Purpose**: Submit a new epic (large body of work containing multiple features).

**When to Use**: When you have a strategic initiative or major capability that will require multiple features to implement.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | The epic description - what strategic goal is being achieved |
| `title` | No | Optional title (LLM generates if not provided) |
| `external_id` | No | External reference (initiative ID, roadmap item) |

**What It Does**:
- Creates a new epic folder in `00_EPICS/`
- Generates a unique Epic ID (e.g., EPIC-001)
- Creates `EpicDescription.md` with:
  - Executive summary and problem statement
  - Success criteria
  - Features breakdown table (placeholder)
  - Dependency flow diagram (Mermaid)
  - Risks and mitigations
  - Progress tracking
- Returns procedure for LLM to execute

**Example**:
```
User: "I need a reporting dashboard that allows users to track metrics and export reports"
LLM: Invokes submit-epic with description="Reporting dashboard with metrics tracking and report exports"
```

**Output**: Epic folder created at `MemoryBank/Features/00_EPICS/EPIC-XXX-epic-name/`

**Next Steps After Creating Epic**:
1. Run `deep-dive` on the EpicDescription.md to gather comprehensive details
2. Create features using `submit-feature` with `epic_id` parameter
3. Update the epic's Features Breakdown and Dependency Diagram as features are created

---

### 3. `submit-feature`

**Purpose**: Submit a new feature idea for development.

**When to Use**: When you have a new feature request or idea to track.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | The feature description from the user |
| `title` | No | Optional title (LLM generates if not provided) |
| `external_id` | No | External reference (ticket number, user story ID) |
| `epic_id` | No | Parent epic ID (e.g., EPIC-001) to link this feature to an epic |

**What It Does**:
- Creates a new feature folder in `01_SUBMITTED/`
- Generates a unique Feature ID (e.g., FEAT-001)
- Creates `FeatureDescription.md` with the requirements
- If `epic_id` is provided, validates the epic exists and links the feature
- Returns procedure for LLM to execute

**Example**:
```
User: "I need a feature to allow users to reset their password via email"
LLM: Invokes submit-feature with description="Allow users to reset their password via email"

User: "Add a data visualization feature to the reporting epic"
LLM: Invokes submit-feature with description="Data visualization with charts", epic_id="EPIC-001"
```

**Output**: Feature folder created at `MemoryBank/Features/01_SUBMITTED/FEAT-XXX-feature-name/`

---

### 4. `create-epic-features`

**Purpose**: Batch-create all features defined in an epic's Features Breakdown table.

**When to Use**: After an epic has been refined with `deep-dive` and you want to create all its features at once.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `epic_id` | Yes | The epic ID (e.g., EPIC-001) containing features to create |
| `epic_path` | No | Direct path to epic folder if known |

**What It Does**:
- Reads the epic's Features Breakdown table
- Identifies features with "TBD" IDs (not yet created)
- Asks for user confirmation before creating
- Creates features in dependency order
- Updates epic with actual FEAT-XXX IDs
- Updates Progress Tracking and Dependency Diagram

**Example**:
```
User: "Create all features for the reporting dashboard epic"
LLM: Invokes create-epic-features with epic_id="EPIC-001"
```

**Output**: All TBD features created and epic updated with FEAT-XXX IDs

---

### 5. `link-feature-to-epic`

**Purpose**: Link an existing feature to an epic.

**When to Use**: When you have a standalone feature that should be part of an epic, or when moving a feature between epics.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) to link |
| `epic_id` | Yes | The epic ID (e.g., EPIC-001) to link to |
| `feature_path` | No | Direct path to feature folder if known |
| `epic_path` | No | Direct path to epic folder if known |

**What It Does**:
- Updates feature's `FeatureDescription.md` (Parent Epic field)
- Updates epic's `EpicDescription.md`:
  - Adds to Features Breakdown table
  - Adds to Progress Tracking table
  - Adds to Feature Details section
  - Updates Dependency Flow Diagram
- If re-linking: Removes from previous epic

**Example**:
```
User: "Link the export feature to the reporting epic"
LLM: Invokes link-feature-to-epic with feature_id="FEAT-005", epic_id="EPIC-001"
```

**Output**: Bidirectional link established between feature and epic

---

### 6. `design-feature`

**Purpose**: Design a feature with UX research, wireframes, and design summary.

**When to Use**: After submitting a feature, before refining into tasks.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- Reads the FeatureDescription.md
- Creates 3 design documents:
  - `UX-research-report.md` - User needs, workflows, pain points
  - `Wireframes-design.md` - Visual specifications (ASCII/Mermaid)
  - `design-summary.md` - Consolidated design decisions

**Example**:
```
User: "Design the password reset feature"
LLM: Invokes design-feature with feature_id="FEAT-001"
```

---

### 7. `refine-feature`

**Purpose**: Transform a feature into a detailed, phased implementation plan with tasks.

**When to Use**: After design is complete, before starting implementation.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- Analyzes all feature documents
- Detects project technology stack (framework, lint, tests)
- Creates phased implementation plan (Phases 0-8)
- Breaks down each phase into independent, testable tasks
- Creates `FeatureTasks.md` summary
- Creates individual phase files in `Phases/` folder
- Adds Git Commits tracking tables and Code Review History sections
- Moves feature from `01_SUBMITTED` to `02_READY_TO_DEVELOP`

**Phase Structure**:
| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Health Check | Verify build/tests before starting |
| 1 | Planning & Analysis | Finalize technical approach |
| 2 | Data Layer | Models, DTOs, schemas |
| 3 | Business Logic | Services, domain rules |
| 4 | Presentation Logic | Controllers, handlers |
| 5 | User Interface | Views, components |
| 6 | Integration | Wire everything together |
| 7 | Testing & Polish | End-to-end tests |
| 8 | Final Checkpoint | Complete verification |

**Example**:
```
User: "Refine the password reset feature into tasks"
LLM: Invokes refine-feature with feature_id="FEAT-001"
```

---

### 8. `start-feature`

**Purpose**: Validate and start implementing a feature.

**When to Use**: After refinement, when ready to begin coding.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- **Pre-Validation** (strict, will reject if fails):
  - Documentation consistency check
  - Completeness check
  - Ambiguity detection (no vague tasks allowed)
  - Technology-agnostic check (no code in task files)
  - Build/test commands configured
- **Post-Validation** (auto-fixes where possible):
  - Time tracking fields present
  - Git Commits tables present
  - Code Review History sections present
  - Lint configuration documented
- Creates git branch: `feat/FEAT-XXX-feature-name`
- Moves feature from `02_READY_TO_DEVELOP` to `03_IN_PROGRESS`
- Creates `start-feature-report-*.md`

**Example**:
```
User: "Start working on the password reset feature"
LLM: Invokes start-feature with feature_id="FEAT-001"
```

**Rejection Reasons**:
- Ambiguous task descriptions
- Missing design documents
- Code snippets in task files
- Build/test commands not configured

---

### 9. `continue-implementation`

**Purpose**: Continue implementing an in-progress feature, task by task.

**When to Use**: After starting a feature, or to resume work on an existing feature.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- Identifies current state (which phase, which task)
- For each task:
  - Gathers task context and requirements
  - Guides implementation following Gherkin specs
  - Runs build and tests
  - **Tracks git commits** in task and phase tables
  - Marks task as COMPLETED
- At phase completion:
  - Validates all git commits are tracked
  - Runs build, tests, and lint
  - **Invokes `code-review` MCP command** (for code-relevant phases)
  - Creates LessonsLearned document
  - Sets phase to AWAITING_USER_ACCEPTANCE

**Git Commit Tracking** (CRITICAL):
After every commit, the LLM must update:
1. Task's **Git Commits** table
2. Phase Checkpoint's **Git Commits (Phase Summary)** table

**Example**:
```
User: "Continue working on the password reset feature"
LLM: Invokes continue-implementation with feature_id="FEAT-001"
```

---

### 10. `code-review`

**Purpose**: Perform comprehensive code review of a phase against CodeGuidelines.

**When to Use**: At phase checkpoint, before accepting a phase.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `phase_number` | Yes | The phase number to review (e.g., 3) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- Reads Git Commits (Phase Summary) to identify changed files
- Reviews each file against `MemoryBank/CodeGuidelines/`
- Validates test quality (meaningful assertions)
- Generates detailed report with status:
  - **APPROVED**: No issues, ready to proceed
  - **APPROVED_WITH_NOTES**: Minor issues, can proceed
  - **NEEDS_CHANGES**: Critical issues, must fix
- Saves report to `code-reviews/phase-{N}/Code-Review-{timestamp}-{STATUS}.md`
- Updates **Code Review History** table in phase checkpoint

**Phases Requiring Code Review**:
- Phase 3 (Business Logic) - ALWAYS
- Phase 4 (Presentation Logic) - ALWAYS
- Phase 5 (User Interface) - ALWAYS
- Phase 2, 6, 7 - If contains significant code

**Phases That Skip Code Review**:
- Phase 0, 1, 8 (no code changes)
- Phases with only DTOs, config, or documentation

**Example**:
```
User: "Run code review for phase 3"
LLM: Invokes code-review with feature_id="FEAT-001", phase_number=3
```

**If NEEDS_CHANGES**:
1. Fix the issues
2. Commit fixes (track in Git Commits tables!)
3. Re-run `code-review`
4. Repeat until APPROVED

---

### 11. `accept-phase`

**Purpose**: Accept a completed phase and mark it as COMPLETED.

**When to Use**: After all phase tasks are done and code review is approved.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `phase_number` | Yes | The phase number to accept (e.g., 3) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- **Validates ALL requirements** (will reject if any fail):
  - All tasks COMPLETED or SKIPPED (with justification)
  - Git Commits tracked in all task tables
  - Git Commits (Phase Summary) has all commits
  - Build clean (0 errors, 0 warnings)
  - Lint clean (if configured)
  - Tests passing (100%)
  - Code Review APPROVED (for code-relevant phases)
  - Code Review History documented
- Updates phase status to COMPLETED
- Updates FeatureTasks.md with actual times
- Creates git commit with phase achievements
- Previews next phase (does NOT auto-start)

**Example**:
```
User: "Accept phase 3"
LLM: Invokes accept-phase with feature_id="FEAT-001", phase_number=3
```

**Rejection Scenarios**:
| Scenario | How to Fix |
|----------|------------|
| Tasks incomplete | Complete tasks or provide skip justification |
| Git commits missing | Track commits in task and phase tables |
| Build/lint/tests fail | Fix the issues |
| Code review missing | Run `code-review` MCP command |
| Code review NEEDS_CHANGES | Fix issues and re-run code review |

---

### 12. `complete-feature`

**Purpose**: Complete a feature and move it to COMPLETED state.

**When to Use**: After ALL phases are completed.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `feature_id` | Yes | The feature ID (e.g., FEAT-001) |
| `feature_path` | No | Direct path to feature folder if known |

**What It Does**:
- Validates all phases are COMPLETED or SKIPPED (with justification)
- Verifies git is clean, build and tests pass
- Compiles Lessons Learned from all phases
- **Asks user** for additional lessons to highlight
- Creates `feature-completion-report.md`
- Moves feature folder from `03_IN_PROGRESS` to `04_COMPLETED`
- Creates final git commit

**Example**:
```
User: "Complete the password reset feature"
LLM: Invokes complete-feature with feature_id="FEAT-001"
```

---

### 13. `deep-dive`

**Purpose**: Conduct an intensive interview about a spec file to gather comprehensive details.

**When to Use**: When a spec file (EpicDescription, FeatureDescription, Phase, Overview, etc.) needs more detail before proceeding. Use this to fill in gaps, resolve ambiguities, and capture decisions.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `file_path` | Yes | Path to the spec file to deep-dive into |

**What It Does**:
- Reads the spec file and identifies its type (EpicDescription, FeatureDescription, Phase, Overview, etc.)
- Conducts an intensive interview using `AskUserQuestion` tool
- Uses context-dependent checklists to ensure comprehensive coverage
- Probes deeply on vague or incomplete answers
- Reads and incorporates any referenced documents
- Appends new sections to the spec file with gathered information
- Marks uncertain items with `[NEEDS VALIDATION]`

**Coverage by File Type**:
| File Type | Topics Covered |
|-----------|---------------|
| EpicDescription | Strategic context, business goals, feature breakdown, dependencies, risks, success criteria, scope boundaries |
| FeatureDescription | Users/personas, requirements, UX flows, error states, technical constraints, tradeoffs, success metrics |
| Phase | Scope clarity, technical approach, testing strategy, error handling, quality criteria |
| Overview/Architecture | Component purposes, design decisions, operational concerns, evolution path |

**Interview Style**:
- **Adaptive questioning**: Starts with batches of 2-3 related questions, switches to one-at-a-time for complex topics
- **Free-flowing conversation**: Follows threads naturally rather than rigidly following a checklist
- **Always probes deeper**: Vague answers like "standard approach" are not accepted - asks for specifics
- **Handles uncertainty**: Helps users think through options, marks uncertain decisions for validation

**Example**:
```
User: "I need more details about the password reset feature"
LLM: Invokes deep-dive with file_path="MemoryBank/Features/01_SUBMITTED/FEAT-001-password-reset/FeatureDescription.md"
```

---

## Typical Workflow

### For Strategic Initiatives (Epics)

```
1. init-project              # First time only
2. submit-epic               # Create strategic initiative
   └─ deep-dive              # Gather comprehensive epic details
3. create-epic-features      # Batch-create all features from epic
   OR
   submit-feature (×N)       # Create features one at a time with epic_id
4. For each feature:
   └─ (follow feature workflow below)
5. Epic auto-updates as features progress

# To add existing features to epic:
link-feature-to-epic         # Link standalone feature to epic
```

### For Individual Features

```
1. init-project           # First time only
2. submit-feature         # Create new feature (with optional epic_id)
   └─ deep-dive           # (Optional) Gather comprehensive details
3. design-feature         # UX research & wireframes
4. refine-feature         # Break into phases & tasks
   └─ deep-dive           # (Optional) Clarify any phase details
5. start-feature          # Validate & create branch

# For each phase:
6. continue-implementation   # Implement tasks
   - Track git commits after each commit
   - Build & test continuously
7. code-review              # Review code at checkpoint
   - Fix issues if NEEDS_CHANGES
   - Re-run until APPROVED
8. accept-phase             # User accepts phase

# After all phases:
9. complete-feature      # Finalize & move to COMPLETED
```

**Note**: `deep-dive` can be used at any point when a spec file needs more detail. It's particularly useful after `submit-epic` to define features, after `submit-feature` to flesh out requirements, or after `refine-feature` to clarify phase tasks.

---

## Epic Progress Visualization

When features are linked to an epic, the epic's Dependency Flow Diagram serves as a **live dashboard** showing progress.

### Visual Status Scheme

| Background | Icon | Status | Meaning |
|------------|------|--------|---------|
| Gray | 📋 | SUBMITTED | Feature submitted, not designed |
| Gray | 📐 | DESIGNED | Design complete, not refined |
| Gray | 📝 | READY | Refined, ready to start |
| Yellow | 🔨 | IN_PROGRESS | Implementation in progress |
| Green | ✅ | COMPLETED | Feature complete |
| Red | ❌ | CANCELLED | Feature cancelled |

### Progress Bar

Epics display a visual progress bar:
```
Progress: ████████░░░░░░░░ 50% (2/4 features complete)
```

### Automatic Updates

The epic is automatically updated when features change state:

| Command | Updates Epic Status To |
|---------|----------------------|
| `submit-feature` (with epic_id) | 📋 SUBMITTED |
| `design-feature` | 📐 DESIGNED |
| `refine-feature` | 📝 READY |
| `start-feature` | 🔨 IN_PROGRESS |
| `complete-feature` | ✅ COMPLETED |

### Mermaid Diagram Classes

```mermaid
classDef notStarted fill:#6c757d,color:white,stroke:#495057
classDef designed fill:#6c757d,color:white,stroke:#17a2b8
classDef ready fill:#6c757d,color:white,stroke:#28a745
classDef inProgress fill:#ffc107,color:black,stroke:#e0a800
classDef completed fill:#28a745,color:white,stroke:#1e7e34
classDef cancelled fill:#dc3545,color:white,stroke:#c82333
```

**Note:** Features without a parent epic (standalone features) do not trigger epic updates.

---

## Quality Gates Summary

Every phase must pass these gates before acceptance:

| Gate | Requirement |
|------|-------------|
| Tasks | All COMPLETED or SKIPPED with justification |
| Git Commits (Tasks) | Every task has commits in its table |
| Git Commits (Summary) | Phase checkpoint has all commits listed |
| Build | 0 errors, 0 warnings |
| Lint | 0 errors, 0 warnings (if configured) |
| Tests | 100% passing |
| Code Review | APPROVED or APPROVED_WITH_NOTES (for code phases) |
| Code Review History | All reviews documented |

---

## Connecting to the MCP Server

### Claude Code
```bash
claude mcp add --transport http devcycle-mcp http://localhost:8080/
```

### Gemini CLI
Add to `~/.gemini/settings.json` or `.gemini/settings.json`:
```json
{
  "mcpServers": {
    "devcycle-mcp": {
      "url": "http://localhost:8080/"
    }
  }
}
```
