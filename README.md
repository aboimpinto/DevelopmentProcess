# DevCycle MCP Server

A Model Context Protocol (MCP) server that guides AI assistants through a structured feature development lifecycle. The server acts as a stateless "Recipe Book" — it holds process knowledge and returns step-by-step procedures for the client (Claude Code, Gemini CLI) to execute.

## Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│   MCP Client (LLM)   │  HTTP   │   DevCycle MCP Server │
│  Claude Code / Gemini │◄──────►│  FastAPI + JSON-RPC   │
│                       │        │  (Docker container)   │
│  - Executes file I/O  │        │  - Returns procedures │
│  - Runs git/build/test│        │  - Holds process docs │
│  - Handles LLM calls  │        │  - Manages templates  │
└──────────────────────┘         └──────────────────────┘
```

- **Server**: Stateless recipe book. Returns structured JSON instructions telling the client what to do.
- **Client**: Local hands and eyes. Executes file operations, git commands, builds, tests, and LLM calls.

## Universal Client Contract (All LLMs)

`tools/call` is a successful MCP call even when it returns a procedure to execute.

- The server returns:
  - `result.structuredContent` (machine-readable, preferred)
  - `result.content[0].text` (JSON string, backward-compatible)
- For recipe tools (`submit-feature`, `continue-implementation`, `accept-phase`, etc.), expect:
  - `status: "pending_execution"`
  - `action: "execute_procedure"`
  - `execution_owner: "client_llm"`
  - `retry_same_tool: false`
  - `next_action: "execute_returned_procedure"`

### Required Client Behavior

1. Call the MCP tool once.
2. Read `structuredContent` first (fallback: parse `content[0].text` as JSON).
3. If `status == "pending_execution"` and `action == "execute_procedure"`:
   - execute the returned procedure locally (files, git, build/test, etc.)
   - do not retry the same MCP call unless a procedure step explicitly asks for it
4. If `status == "pending_action"`, perform the requested action.
5. If `status == "error"`, treat as failure.

### Minimal Decision Logic

```text
if status == "error": fail
elif status == "pending_execution" and action == "execute_procedure": execute instructions locally
elif status == "pending_action": perform requested action
else: handle as standard success payload
```

## Quick Start

### Build and Run

```bash
# Build the Docker image
docker build -t devcycle-mcp .

# Run the container
docker run -d -p 8080:8000 -v "$(pwd)/MemoryBank:/app/MemoryBank" --name devcycle-mcp-local devcycle-mcp

# Verify it's running
curl -X POST http://localhost:8080/ -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Connect Claude Code

```bash
claude mcp add --transport http devcycle-mcp http://localhost:8080/
```

### Connect Gemini CLI

Add to `~/.gemini/settings.json`:
```json
{
  "mcpServers": {
    "devcycle-mcp": {
      "url": "http://localhost:8080/"
    }
  }
}
```

### Container Management

```bash
# Stop and remove
docker rm -f devcycle-mcp-local

# View logs
docker logs -f devcycle-mcp-local

# Rebuild after code changes
docker rm -f devcycle-mcp-local && docker build -t devcycle-mcp . && \
  docker run -d -p 8080:8000 -v "$(pwd)/MemoryBank:/app/MemoryBank" --name devcycle-mcp-local devcycle-mcp
```

## Feature Lifecycle

Features flow through state folders in `MemoryBank/Features/`:

```
00_EPICS ──► 01_SUBMITTED ──► 02_READY_TO_DEVELOP ──► 03_IN_PROGRESS ──► 04_COMPLETED
```

## Commands (13 total)

### Project Setup

| Command | Purpose |
|---------|---------|
| `init-project` | Create the MemoryBank folder structure for a new project |

### Epic Management

| Command | Purpose |
|---------|---------|
| `submit-epic` | Create a new epic (strategic initiative with multiple features) in `00_EPICS/` |
| `create-epic-features` | Batch-create all features from an epic's Features Breakdown table |
| `link-feature-to-epic` | Link an existing standalone feature to an epic (bidirectional update) |

### Feature Submission and Design

| Command | Purpose |
|---------|---------|
| `submit-feature` | Submit a new feature idea into `01_SUBMITTED/` with FeatureDescription.md |
| `deep-dive` | Conduct an intensive interview on any spec file to gather comprehensive details |
| `design-feature` | Create UX research report, wireframes, and design summary for a feature |

### Feature Planning and Implementation

| Command | Purpose |
|---------|---------|
| `refine-feature` | Transform a feature into a phased implementation plan using the full feature folder plus linked epic/dependency context (9 phases, tasks with Gherkin specs). Moves to `02_READY_TO_DEVELOP/` |
| `start-feature` | Validate documentation, create git branch, move to `03_IN_PROGRESS/`. Rejects if docs are incomplete or ambiguous. Supports `workflow_mode=autonomous` for official no-routine-prompt execution |
| `continue-implementation` | Orchestrate task-by-task implementation using feature history plus linked epic/dependency context; Phase 1 creates canonical `planning-analysis-report.md`, later phases reuse it; build, downstream-aware tests, commit tracking, code review, lessons learned. Supports `workflow_mode=autonomous` to continue through acceptance and completion |

### Quality and Completion

| Command | Purpose |
|---------|---------|
| `code-review` | Review all phase changes against CodeGuidelines. Returns APPROVED, APPROVED_WITH_NOTES, or NEEDS_CHANGES |
| `accept-phase` | Validate all quality gates (build, tests, lint, code review, git commits) and mark a phase COMPLETED. Supports `workflow_mode=autonomous` to continue automatically |
| `complete-feature` | Validate all phases done, compile lessons learned, move feature to `04_COMPLETED/`. Supports `workflow_mode=autonomous` to skip the extra lessons prompt |

## Typical Workflow

```
1. init-project                    # First time only
2. submit-epic                     # Create strategic initiative
   └─ deep-dive                    # Gather epic details
3. create-epic-features            # Batch-create features from epic
4. For each feature:
   a. design-feature               # UX research & wireframes
   b. refine-feature               # Break into phases & tasks
   c. start-feature                # Validate & create branch
   d. For each phase:
      ├─ continue-implementation   # Implement tasks
      ├─ code-review               # Review code
      └─ accept-phase              # User accepts phase
   e. complete-feature             # Finalize & move to COMPLETED
```

Official autonomous workflow:
`start-feature(feature_id="FEAT-XXX", workflow_mode="autonomous")`
This hands off to `continue-implementation`, `accept-phase`, and `complete-feature` automatically unless a true blocker requires manual intervention.

## Quality Gates

Every phase must pass before acceptance:

| Gate | Requirement |
|------|-------------|
| Tasks | All COMPLETED or SKIPPED with justification |
| Git Commits | Tracked in both task-level and phase-level tables |
| Build | 0 errors, 0 warnings |
| Lint | 0 errors, 0 warnings (if configured) |
| Tests | 100% passing |
| Code Review | APPROVED or APPROVED_WITH_NOTES (for code phases) |

## Project Structure

```
DevCycleManager/
├── main.py              # FastAPI JSON-RPC server (single endpoint at /)
├── requirements.txt     # Python dependencies (fastapi, uvicorn)
└── Prompts/             # Procedure templates (13 prompt files)
    ├── init-project.json
    ├── submit-epic.md
    ├── submit-feature.md
    ├── create-epic-features.md
    ├── link-feature-to-epic.md
    ├── design-feature.md
    ├── refine-feature.md
    ├── start-feature.md
    ├── continue-implementation.md
    ├── code-review.md
    ├── accept-phase.md
    ├── complete-feature.md
    ├── deep-dive.md
    └── epic-status-update.md

MemoryBank/              # Knowledge base (volume-mounted)
├── Overview/            # Project vision, goals
├── Architecture/        # Components, patterns
├── CodeGuidelines/      # Standards, technologies
├── LessonsLearned/      # Phase-level insights
└── Features/
    ├── 00_EPICS/        # Strategic initiatives
    ├── 01_SUBMITTED/    # New feature ideas
    ├── 02_READY_TO_DEVELOP/  # Refined, ready to start
    ├── 03_IN_PROGRESS/  # Currently being implemented
    ├── 04_COMPLETED/    # Done
    └── 05_CANCELLED/    # Abandoned
```

## Acknowledgements

The prompt template structure was inspired by the patterns found in [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents). Key patterns adopted include HTML comment frontmatter, persona definitions with core beliefs, completion checklists, and structured error recovery tables.

## Prompt Template Structure

All prompt templates follow a consistent structure:

```markdown
# Command Name

<!-- HTML comment frontmatter: name, purpose, tools, triggers, I/O, related -->

## Inputs          — Template variables ({{feature_id}}, etc.)
## Persona         — Role title + 4 core beliefs
## Completion Checklist — "Done when..." checkboxes
## Phase 1-N       — Numbered execution phases
## Rules           — Concise one-liners
## Error Recovery  — Scenario/action table
## Related Commands
```
