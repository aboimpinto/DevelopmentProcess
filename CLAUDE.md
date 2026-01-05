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

The DevCycle MCP Server provides 9 commands that guide features through a complete development lifecycle.

### Feature Lifecycle Overview

```
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
- Creates `Features/` with state folders (01_SUBMITTED, 02_READY_TO_DEVELOP, etc.)
- Creates `Overview/`, `Architecture/`, `CodeGuidelines/`, `LessonsLearned/` folders
- Adds README files with guidance

**Example**:
```
User: "Initialize a new project"
LLM: Invokes init-project MCP command
```

---

### 2. `submit-feature`

**Purpose**: Submit a new feature idea for development.

**When to Use**: When you have a new feature request or idea to track.

**Parameters**:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `description` | Yes | The feature description from the user |
| `title` | No | Optional title (LLM generates if not provided) |
| `external_id` | No | External reference (ticket number, user story ID) |

**What It Does**:
- Creates a new feature folder in `01_SUBMITTED/`
- Generates a unique Feature ID (e.g., FEAT-001)
- Creates `FeatureDescription.md` with the requirements
- Returns procedure for LLM to execute

**Example**:
```
User: "I need a feature to allow users to reset their password via email"
LLM: Invokes submit-feature with description="Allow users to reset their password via email"
```

**Output**: Feature folder created at `MemoryBank/Features/01_SUBMITTED/FEAT-XXX-feature-name/`

---

### 3. `design-feature`

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

### 4. `refine-feature`

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

### 5. `start-feature`

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

### 6. `continue-implementation`

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

### 7. `code-review`

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

### 8. `accept-phase`

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

### 9. `complete-feature`

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

## Typical Workflow

```
1. init-project          # First time only
2. submit-feature        # Create new feature
3. design-feature        # UX research & wireframes
4. refine-feature        # Break into phases & tasks
5. start-feature         # Validate & create branch

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
