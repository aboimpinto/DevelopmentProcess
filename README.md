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

The HTTP `tools/call` boundary accepts standard MCP arguments under
`params.arguments`. The historical `params.input` shape remains supported for
older clients, but new clients and adapters should use the standard shape.

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

## Commands (16 total)

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
| `deep-dive` | Conduct a single-target comprehensive or targeted interview; linked documents remain read-only |
| `design-feature` | Create UX research report, wireframes, and design summary for a feature |

`deep-dive` accepts `file_path` plus optional `mode`, `focus`, and `response_mode` arguments:

- `mode="comprehensive"` (default) applies exactly one checklist for the target EPIC, FEAT, phase, or other spec.
- `mode="targeted"` requires a non-empty `focus` array and resolves only those questions plus necessary dependent follow-ups.
- `response_mode="adaptive_interview"` (default) conducts the normal conversational interview and may update only `file_path` after decision closure.
- `response_mode="question_manifest"` asks nothing interactively, modifies no files, and returns every currently identifiable question, its 3-4 options, and the recommended option in one versioned JSON manifest.
- In adaptive mode, only `file_path` may be modified. Linked EPICs, FEATs, and references are always read-only context.
- Completed Deep-Dive decisions are authoritative unless the user explicitly reopens them or the target contains an authoritative conflict.

```json
{
  "file_path": "MemoryBank/Features/01_SUBMITTED/FEAT-001-example/FeatureDescription.md",
  "mode": "targeted",
  "focus": ["Resolve the ownership decision discovered during refinement"],
  "response_mode": "question_manifest"
}
```

### Feature Planning and Implementation

| Command | Purpose |
|---------|---------|
| `refine-feature` | Transform a feature into a phased implementation plan using the full feature folder plus linked epic/dependency context (9 phases, tasks with Gherkin specs). Moves to `02_READY_TO_DEVELOP/` |
| `start-feature` | Validate documentation, create git branch, move to `03_IN_PROGRESS/`. Rejects if docs are incomplete or ambiguous. Supports `workflow_mode=autonomous` for official no-routine-prompt execution |
| `continue-implementation` | Orchestrate task-by-task implementation using feature history plus linked epic/dependency context; Phase 1 creates canonical `planning-analysis-report.md`, later phases reuse it; build, downstream-aware tests, commit tracking, code review, lessons learned. Supports `workflow_mode=autonomous` to continue through acceptance and completion |

### Quality and Completion

| Command | Purpose |
|---------|---------|
| `code-review` | Review a full phase, or one PR unit with optional `delivery_unit_id`, against CodeGuidelines. Returns APPROVED, APPROVED_WITH_NOTES, or NEEDS_CHANGES |
| `accept-phase` | Validate all quality gates (build, tests, lint, code review, git commits) and mark a phase COMPLETED. Supports `workflow_mode=autonomous` to continue automatically |
| `complete-feature` | Validate all phases done, compile lessons learned, retain every associated PR and available merge evidence, synchronize linked EPIC status and acceptance/design tracking, and move feature to `04_COMPLETED/`. Supports `workflow_mode=autonomous` to skip the extra lessons prompt |

Refinement, start and completion reconcile an existing epic against feature
records and evidence: statuses, counts, diagrams, delivery summaries and next
steps. Adaptive Deep-Dive reconciles only its target epic; linked epics remain
read-only and discrepancies are reported for a separately authorized action.
Question-manifest and hosted stages never mutate files. Obsolete progress snapshots
move to linked history (within the target for Deep-Dive) instead of leaving
conflicting status tables in the current epic. Deep-dive records decisions without
advancing implementation; refinement marks its target READY after its gate;
successful start marks it IN_PROGRESS; verified completion marks it COMPLETED.
Completed siblings are preserved. The epic completes only when all required
features and epic-level acceptance/delivery gates are complete. No linked epic
means N/A, not an instruction to create one.

## Project PR Delivery

This capability delivers instructions for the client to execute; the MCP server
neither reads client repositories nor watches/opens/merges PRs itself. The client
reads `<source repository>/.devcycle/PRPolicy.md`, or a policy path explicitly
provided by project instructions. An external MemoryBank is a separate location.
Existing explicit project conventions take precedence when no policy exists;
otherwise task-sized meaningful changes are the planning recommendation.

A minimal project policy can say:

```markdown
# PR Policy
- Default boundary: task.
- Evaluate grouping at the start of every phase from the actual tasks.
- Group only one cohesive independently working improvement with its tests/docs.
- Record no PR when work produces no source-repository diff.
- Branching mode: stacked. Continue from a verified predecessor's published head.
- Target the predecessor branch; track exact bases and restack after upstream fixes.
- Merge bottom-up to the final delivery branch, retargeting remaining PRs.
- Use this repository's publication command, review and validation requirements.
```

Refinement creates `PRDelivery.md` beside FeatureTasks.md: policy provenance,
task-to-unit coverage, safe dependencies, compatibility strategy and checks.
Before implementation, evaluate cohesion, scope, expected files/diff/commits,
contract/runtime risk and required validation. Record the chosen task, grouped,
phase or permitted feature boundary and rationale. No phase name/number selects
a PR boundary. Evidence-only work can use `PR Boundary: none` with a reason.

Delivery adds only `PR Boundary` and `PR Decision Basis` to phase records. Reuse
existing scope and gate decisions (`needCodeReview` / `needTestCoverage` when
present and the applicable scope policy). This capability leaves phase numbering
and phase-level gate selection in place. Task grouping does not waive required
commands or add production review to test-only work. Completed features need no
retrofit.

After each task, check its unit: continue remaining members, report READY_FOR_PR
and publish through the project workflow once gates pass, reuse an existing PR,
or continue on a new dependent branch under stacked policy while review is pending.
Missing prerequisite implementation/verification still blocks its consumer. Keep
base/predecessor/head and restack mappings; PR stamping and review diffs exclude
ancestor commits. Merge bottom-up, restacking/retargeting each child to the delivery
branch. Explicit merged-prerequisite project policies remain supported.
Track implementation and delivery separately.
`code-review(..., delivery_unit_id="PRU-01")` reviews only that unit and saves
under `code-reviews/delivery-units/PRU-01/`; omitting the argument retains full-phase
review. Unit approval never approves unfinished phase work. Review evidence names
the base/head/tree; changed content requires fresh validation/review.

Acceptance checks units due at its boundary; completion verifies all required
merges and retains all PRs in the feature and relevant epic references. Neither
creates a duplicate aggregate PR. Every PR explains why/before/after, scope,
dependencies and actual checks; broader context belongs in the linked feature
issue. Autonomous workflow does not authorize automatic merges.

## GitHub synchronization

Three MCP commands return instructions for the **local model**. The server does
not contact GitHub, read project files, store credentials or poll in the background.
They retain the normal pending_execution / client_llm response contract.

| Command | Arguments | Direction and scope |
| --- | --- | --- |
| `sync-epic` | `epic_id`, optional `epic_path`, `project_path` | Local → GitHub: create missing epic/feature issues and update their hierarchy; reuse existing links |
| `sync-feature` | `feature_id`, optional `feature_path`, `project_path` | Local → GitHub: update an existing feature issue with phases, predicted PRs and actual links; never create an issue |
| `refresh-delivery` | `feature_id`, optional `feature_path`, `project_path` | GitHub → local → issue: reconcile PR facts locally, then update the existing feature issue table; never merge Git branches |

A minimal project policy lives at the source repository's
`.devcycle/GitHubSync.md`, or an explicit path from its project instructions:

```markdown
# GitHub synchronization
Enabled: true
Provider: GitHub
Repository: example/project
Account: project-maintainer
MemoryBank: /local/path/to/MemoryBank
Delivery target: main
Automatic events: after epic feature definition; after refinement; after PR
publication; on resume/before completion; after local acceptance/completion
```

These are client-read instructions, not a machine-parsed configuration schema.
Use the actual project account and integration branch. Configuration stays local
if the project ignores .devcycle; no credentials belong in this file. Without
configuration, automatic synchronization is disabled. Explicit invocation may use
already established project settings; missing/conflicting identity is reported.
No project is automatically configured by installing/upgrading DevCycle.

After local epic/feature definition, the lifecycle calls sync-epic. After successful
refinement or PR publication, it calls sync-feature. Resume and delivery gates call
refresh-delivery, which saves observations and invokes sync-feature once to update
the issue table (also retrying a pending issue update). Final local acceptance
can synchronize feature and parent progress. Existing authorization applies; these
procedures do not add repeated permission prompts or authorize unrelated actions.
A failed issue update preserves locally verified delivery facts or local READY
refinement with SYNC_PENDING rather than
claiming the write worked or discarding the plan.

Refinement, even with GitHub disabled, produces `PRDelivery.md`. For delivery other
than one PR per feature it includes each phase's predicted count, stable unit IDs,
proposed PR titles, short descriptions, task membership and dependencies. A unit
spanning phases counts once; evidence-only work produces zero PRs. Record a feature
total, unopened remainder and uncertainty; revise with reasons at phase entry.
Feature-level delivery records one unit unless there is no repository change.

For example, a phase can have PRU-01 “Retain publication state” and PRU-02 “Publish
committed references”, followed by a no-diff checkpoint with zero PRs. The total is
two, not one per task/test and not one per phase by name. Each actual PR replaces
its planned display entry using the stable feature/unit identity; split or
superseded PRs keep their history and all links.

Issue updates use explicit managed-section markers and preserve human text and
attributes. Retries discover existing identities across open/closed issues before
creating anything. GitHubSync.md beside the feature/epic records readback and
partial failures. Closed-unmerged differs from merged; a child merged only into
an unmerged parent is not delivered to the final target. Refresh retains old stack
boundaries and flags restack/retarget work without executing it. Hosting facts
never automatically pass phase/feature acceptance or close issues.

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
      ├─ code-review               # Under existing phase review gates
      └─ accept-phase              # User accepts phase
   e. complete-feature             # Finalize & move to COMPLETED
```

Official autonomous workflow:
`start-feature(feature_id="FEAT-XXX", workflow_mode="autonomous")`
This hands off to `continue-implementation`, `accept-phase`, and `complete-feature` automatically unless a true blocker requires manual intervention.

## Quality Gates

### Shared phase-quality policy

`Prompts/phase-quality-policy.md` is injected into all six lifecycle recipe calls
(refine, start, continue, review, accept phase, complete feature). The MCP payload
exposes `quality_gate_policy_version: devcycle-phase-quality/v2` in both standard
structured output and the legacy JSON text response. Missing policy fails closed.

- Production-code and mixed phases require scoped production coverage using
  explicit project/phase thresholds; absent required policy must be resolved,
  not replaced with a guessed percentage.
- Test-only phases require executed, meaningful tests and assessment of their
  assertions, not production-code review or numerical coverage of test code. An explicitly assigned measurement of
  earlier production code still applies.
- Documentation-only phases retain deliverable validation; product tests,
  production coverage and code review can be Not Applicable with a reason.
- Required failed/missing/unexecuted verification and below-threshold or missing
  required coverage are CRITICAL acceptance blockers and yield NEEDS_CHANGES.
- Reviews record test counts, measured coverage, scope, thresholds, revision and
  evidence paths. Phase and feature acceptance reuse the same contract.

This server supplies recipes to the executing client LLM; it does not itself run
product tests or enforce a client application's state transitions. Updating it
does not retroactively validate historical reviews or rerun an active workflow.

Regression checks (inside an image with the server dependencies installed):

```bash
python -m unittest discover -s /app -p 'test*.py'
python -m compileall -q /app
```

Refinement and start share one readiness procedure,
[`feature-readiness.md`](DevCycleManager/Prompts/feature-readiness.md), included
in both MCP responses. Before declaring READY, the client must check scope,
persisted/public contracts, failure ordering, compatibility, acceptance-test
traceability, and execution prerequisites, then save `readiness-validation.md`
with evidence. Start verifies the same criteria against current inputs.
Routine technical choices are resolved within the agreed scope; only unresolved
material decisions require user input. These are client-executed checks, not
server-side validation of the project's files.

All lifecycle recipes also include the shared
[`dependency-order.md`](DevCycleManager/Prompts/dependency-order.md) policy.
Required prerequisites must be implemented and verified before consumer tasks
start. Refinement may schedule enabling tasks first inside the same feature;
unavailable prerequisites owned by later features block READY. Existing feature
IDs and green tests using separately provisioned services do not prove delivery.
Review checks required files missing from the diff, and completion requires the
supported startup/user workflow where applicable. Missing or empty dependency
policy causes recipe delivery to fail rather than silently omit the gate.
These instructions constrain client execution; the server does not independently
inspect project dependency evidence or certify its truth.

Run server regression tests with `python -m unittest discover -s tests -v` in an
environment with `DevCycleManager/requirements.txt` installed. Run both this suite
and `python -m unittest discover -s DevCycleManager -v`; neither directory's
standalone discovery includes the other. In the image, mount `tests/` at
`/app/tests` and run discovery separately for `/app` and `/app/tests`.

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
└── Prompts/             # Procedure templates and shared policies
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

## Explicit phase gates (policy v2)

Refinement declares Tests, workflow E2E, Code review, Build and Lint independently.
Implementation may revise applicability with a documented scope reason and a
synchronized task/gate contract. Documentation and health checkpoints need no
code review unless explicitly assigned. Data-only declarations may need no tests.
Frontend/backend TwinTests prove scoped phase acceptance; EPIC Gherkin/Playwright
E2E obligations and their phase/checkpoint ownership remain in the feature manifest.
The same policy is returned by refinement, implementation, review and acceptance.

The shared Acceptance Responsibility Policy (`acceptance-responsibility/v1`) is
injected into all twelve planning and delivery recipe boundaries, including EPIC
creation, feature slicing, Deep-Dive and refinement. It preserves EPIC -> FEAT ->
Phase -> Task ownership, many-to-many evidence links and independent gate flags.

## Acceptance and test workflow

For new features and bug repair, follow
[EPIC-to-Task acceptance and test traceability](docs/acceptance-test-traceability.md)
and the [shared responsibility policy](docs/acceptance-responsibility-policy.md).
Preserve test/criterion/code links at EPIC, FEAT, Phase and Task levels. Required
tests are executable quality gates; many-to-many coverage does not waive complete
workflow E2E proof. A bug is reproduced at the appropriate E2E/TwinTest boundary,
traced to focused coverage and code, then verified through the affected levels.


## Hosted Deep-Dive UI clients

Call `deep-dive` with `file_path`, `response_mode: "host_stage"`, and one stage:
`opening`, `follow_up`, `clarify`, or `apply_answers`. The response is a stateless
procedure under `deep_dive_host_contract.version: devcycle-deep-dive-host/v1`.
The model executes only that stage against the host-supplied context snapshot.

The host owns UI prompts, saved answers, validation, and target-file persistence.
Hosted stages have an empty mutation scope and do not invoke tools or another
recipe. Opening/follow-up return the existing question JSON shape; clarification
returns text; apply-answers returns a versioned `deep-dive.edits` JSON exchange
with exact, non-overlapping before/after excerpts from the current target. The
host preserves untouched content and refuses stale-source writes. The complete
edit schema is supplied once in the returned instructions. Missing stages or unknown
modes fail rather than entering the full interactive interview. Calls without
`response_mode` retain the existing interactive recipe. Standard MCP `arguments`
and legacy `input` tool-call payloads are supported.

Procedures live in `DevCycleManager/Prompts/deep-dive-host/`. Run
`python -m unittest discover -s DevCycleManager` with the project dependencies
installed, or mount that directory into the project's built image at `/app` and
run `python -m unittest discover` there. No paid model or production workflow is
required for these contract checks.
