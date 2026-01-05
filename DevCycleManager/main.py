import os
import re
import json
from pathlib import Path
from typing import Optional, Union, List, Any, Dict

from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field

# --- Constants & Configuration ---
# Path to the directory containing prompt/config files
PROMPTS_DIR = Path(__file__).parent / "Prompts"

# --- Mocking the MCP Context/Sampling for the Prototype ---
async def mock_sample_llm(prompt: str, context: Optional[str] = None) -> str:
    """
    Simulates the MCP Sampling Protocol (`ctx.session.sample()`).
    In a real deployment, this sends the prompt to the Client's LLM.
    """
    print(f"\n[MCP SERVER] Sampling Request sent to Client:")
    print(f"--- Prompt ---\n{prompt}\n--------------")
    if context:
        print(f"--- Context requested ---\n{context}\n-------------------------")
    
    # Simulate a response for the prototype
    return f"[LLM Generated Content based on: {prompt[:30]}...]"

# --- Core Business Logic (The "Recipes") ---

async def run_init_project() -> dict:
    """
    The Recipe for initializing the project.
    It reads the required folder structure from a configuration file.
    """
    try:
        with open(PROMPTS_DIR / "init-project.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            required_folders = config.get("directories", [])
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="init-project.json not found in Prompts directory.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding init-project.json.")

    instructions = "Please initialize the project structure by creating the following directories:\n\n"
    for folder in required_folders:
        instructions += f"- {folder}\n"
    
    return {
        "status": "pending_action",
        "action": "create_directories",
        "directories": required_folders,
        "message": instructions
    }

async def run_submit_feature(description: str, title: Optional[str] = None, external_id: Optional[str] = None) -> dict:
    """
    The Recipe for submitting a feature.
    Returns the step-by-step procedure prompt for the Client's LLM to execute.
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "submit-feature.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "submit-feature.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{description}}", description or "")
    procedure = procedure.replace("{{title}}", title or "[Not provided - LLM should generate]")
    procedure = procedure.replace("{{external_id}}", external_id or "[Not provided]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "submit-feature",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Overview/",
            "MemoryBank/Architecture/",
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Features/"
        ],
        "context_files": [
            "MemoryBank/Features/NEXT_FEATURE_ID.txt"
        ],
        "message": "Execute the submit-feature procedure. IMPORTANT: Start with Step 0 to read the project context before generating the feature description."
    }

async def run_design_feature(feature_id: str, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for designing a feature.
    Returns a comprehensive 3-phase procedure that creates:
    1. UX-research-report.md
    2. Wireframes-design.md
    3. design-summary.md
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "design-feature.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "design-feature.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "design-feature",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Overview/",
            "MemoryBank/Architecture/",
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Features/01_SUBMITTED/",
            "MemoryBank/Features/02_READY_TO_DEVELOP/"
        ],
        "outputs": [
            "UX-research-report.md",
            "Wireframes-design.md",
            "design-summary.md"
        ],
        "message": "Execute the design-feature procedure. This is a 3-PHASE process: (1) UX Research, (2) Wireframes, (3) Design Summary. Complete each phase before moving to the next."
    }

async def run_refine_feature(feature_id: str, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for refining a feature into implementable tasks.
    Transforms a feature from 01_SUBMITTED to 02_READY_TO_DEVELOP by:
    1. Analyzing all feature documents
    2. Creating phased implementation plan
    3. Breaking down into independent tasks with unit tests
    4. Adding checkpoints with quality gates
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "refine-feature.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "refine-feature.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure_template.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "refine-feature",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Overview/",
            "MemoryBank/Architecture/",
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Features/01_SUBMITTED/",
            "MemoryBank/Features/02_READY_TO_DEVELOP/"
        ],
        "outputs": [
            "FeatureTasks.md",
            "Phases/phase-0-health-check.md",
            "Phases/phase-1-planning-analysis.md",
            "Phases/phase-2-data-layer.md",
            "Phases/phase-3-business-logic.md",
            "Phases/phase-4-presentation-logic.md",
            "Phases/phase-5-user-interface.md",
            "Phases/phase-6-integration.md",
            "Phases/phase-7-testing-polish.md",
            "Phases/phase-8-final-checkpoint.md"
        ],
        "message": "Execute the refine-feature procedure. This creates a phased implementation plan with tasks, unit tests, and quality checkpoints. The feature will be moved to 02_READY_TO_DEVELOP when complete."
    }

async def run_start_feature(feature_id: str, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for starting a feature (moving to IN_PROGRESS).
    Validates the feature and transitions from 02_READY_TO_DEVELOP to 03_IN_PROGRESS:
    1. Pre-validation (consistency, completeness, ambiguity detection)
    2. Post-validation (time tracking, checkpoints, auto-fix)
    3. Git branch creation (if connected)
    4. Move to 03_IN_PROGRESS
    5. Git commit and push (if connected)
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "start-feature.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "start-feature.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "start-feature",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Overview/",
            "MemoryBank/Architecture/",
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Features/02_READY_TO_DEVELOP/"
        ],
        "outputs": [
            "pre-validation-report-[STATUS]-[timestamp].md",
            "start-feature-report-[timestamp].md"
        ],
        "message": "Execute the start-feature procedure. This validates the feature (pre-validation + post-validation), creates a git branch, and moves the feature to 03_IN_PROGRESS. If pre-validation fails, the process STOPS with a rejection report."
    }

async def run_continue_implementation(feature_id: str, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for continuing feature implementation.
    Orchestrates the systematic implementation of an IN_PROGRESS feature:
    1. Discovers current state (feature, phase, task)
    2. Executes tasks following specifications
    3. Manages quality (build, tests, code-review)
    4. Tracks progress (update phase files, FeatureTasks.md)
    5. Requests user acceptance for phase completion
    6. Creates LessonsLearned documents per phase
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "continue-implementation.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "continue-implementation.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "continue-implementation",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Overview/",
            "MemoryBank/Architecture/",
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Features/03_IN_PROGRESS/",
            "MemoryBank/LessonsLearned/"
        ],
        "outputs": [
            "Phase updates in Phases/*.md",
            "FeatureTasks.md updates",
            "code-reviews/phase-{N}/*.md",
            "LessonsLearned/{feature_id}/Phase-{N}-{name}.md",
            "feature-completion-report.md (when all phases complete)"
        ],
        "message": "Execute the continue-implementation procedure. This orchestrates task execution, quality gates (build/test/review), phase completion with user acceptance, and LessonsLearned documentation. Resume from current state automatically."
    }

async def run_accept_phase(feature_id: str, phase_number: int, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for accepting a completed phase.
    Formalizes user acceptance of a phase that has passed all quality gates:
    1. Validates checkpoint was filled
    2. Validates phase is awaiting acceptance
    3. Validates technical requirements (build, tests, code review)
    4. Handles incomplete tasks (with user justification)
    5. Marks phase as COMPLETED in all files
    6. Updates time tracking with actual vs estimated
    7. Creates git commit with achievements
    8. Previews next phase (without starting it)
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "accept-phase.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "accept-phase.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{phase_number}}", str(phase_number) if phase_number is not None else "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "accept-phase",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Features/03_IN_PROGRESS/",
            "MemoryBank/LessonsLearned/"
        ],
        "outputs": [
            "Phase file updated to COMPLETED",
            "FeatureTasks.md updated with COMPLETED status and actual times",
            "start-feature-report-*.md updated",
            "Checkpoint section marked Complete",
            "Git commit with phase achievements",
            "Next phase preview (if not final phase)",
            "feature-completion-report.md (if final phase)"
        ],
        "message": "Execute the accept-phase procedure. This formalizes user acceptance, updates all documentation with COMPLETED status and time metrics, creates git commit, and previews next phase. Does NOT auto-start next phase - user must run continue-implementation."
    }

async def run_code_review(feature_id: str, phase_number: int, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for performing a comprehensive code review.
    Reviews all code changes in a phase against project CodeGuidelines:
    1. Determines if review is required (skip for non-code phases)
    2. Extracts phase context (commits, changed files)
    3. Reviews each file against CodeGuidelines
    4. Validates test quality (meaningful assertions, coverage)
    5. Generates detailed report with actionable feedback
    6. Updates phase checkpoint with review results
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "code-review.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "code-review.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{phase_number}}", str(phase_number) if phase_number is not None else "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "code-review",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/CodeGuidelines/",
            "MemoryBank/Architecture/",
            "MemoryBank/LessonsLearned/",
            "MemoryBank/Features/03_IN_PROGRESS/"
        ],
        "outputs": [
            "code-reviews/phase-{N}/Code-Review-{timestamp}-{STATUS}.md",
            "Phase checkpoint updated with review results"
        ],
        "message": "Execute the code-review procedure. This performs a comprehensive review of all phase changes against CodeGuidelines, generates a detailed report with APPROVED/APPROVED_WITH_NOTES/NEEDS_CHANGES status, and updates the phase checkpoint."
    }

async def run_complete_feature(feature_id: str, feature_path: Optional[str] = None) -> dict:
    """
    The Recipe for completing a feature.
    Validates all requirements and moves feature to COMPLETED state:
    1. Validates all phases are COMPLETED (or SKIPPED with justification)
    2. Verifies git repository is clean (no uncommitted/unpushed changes)
    3. Verifies build and tests pass (0 errors, 0 warnings, 100% tests)
    4. Compiles Lessons Learned from all phases into feature-level document
    5. Asks user for additional lessons they want to highlight
    6. Updates all documentation with completion status
    7. Creates completion reports (validation, metrics, lessons learned)
    8. Moves feature to 04_COMPLETED folder
    9. Creates completion git commit and pushes
    """
    # Load the procedure template
    try:
        with open(PROMPTS_DIR / "complete-feature.md", "r", encoding="utf-8") as f:
            procedure_template = f.read()
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "complete-feature.md prompt template not found in Prompts directory."
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in MemoryBank/Features/]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "complete-feature",
        "instructions": procedure,
        "context_folders": [
            "MemoryBank/Features/03_IN_PROGRESS/",
            "MemoryBank/LessonsLearned/"
        ],
        "outputs": [
            "feature-completion-report.md",
            "MemoryBank/LessonsLearned/{feature_id}/Feature-Completion-LessonsLearned.md",
            "FeatureTasks.md updated with completion status",
            "Feature folder moved to 04_COMPLETED/",
            "Git commit with completion details"
        ],
        "message": "Execute the complete-feature procedure. This validates all phases are complete, compiles Lessons Learned (asks user for additional input), creates completion reports, and moves the feature to 04_COMPLETED. REQUIRES USER CONFIRMATION before moving."
    }

# --- JSON-RPC Pydantic Models ---
class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(..., pattern=r"^2.0$")
    method: str
    id: Optional[Union[str, int]] = None
    params: Optional[Union[Dict[str, Any], List[Any]]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]]
    result: Optional[Any] = None
    error: Optional[Any] = None

# --- FastAPI App ---
app = FastAPI(title="DevCycleManager (Remote Process)")

@app.post("/", response_model=JsonRpcResponse, response_model_exclude_none=True)
async def json_rpc_handler(request: JsonRpcRequest):
    if request.id is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if request.method == "initialize":
        return JsonRpcResponse(id=request.id, result={
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "DevCycleManager", "version": "0.2.0-remote"},
            "capabilities": {"tools": {"listChanged": False}}
        })

    elif request.method == "tools/list":
        return JsonRpcResponse(id=request.id, result={
            "tools": [
                {
                    "name": "init-project",
                    "description": "Initialize the MemoryBank folder structure.",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "submit-feature",
                    "description": "Submit a new feature idea. Returns a step-by-step procedure for the LLM to execute.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "The feature description from the user"},
                            "title": {"type": "string", "description": "Optional: A title for the feature. If not provided, LLM will generate one."},
                            "external_id": {"type": "string", "description": "Optional: External reference ID (e.g., ticket number, user story ID)"}
                        },
                        "required": ["description"]
                    }
                },
                {
                    "name": "design-feature",
                    "description": "Design a feature with UX research, wireframes, and design summary. Returns a 3-phase procedure that creates UX-research-report.md, Wireframes-design.md, and design-summary.md.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to design"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "refine-feature",
                    "description": "Refine a feature into implementable tasks. Creates phased implementation plan with tasks, unit tests, and quality checkpoints. Moves feature from 01_SUBMITTED to 02_READY_TO_DEVELOP.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to refine"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "start-feature",
                    "description": "Start implementing a feature. Validates (pre + post), creates git branch, and moves from 02_READY_TO_DEVELOP to 03_IN_PROGRESS. Rejects if documentation is incomplete or ambiguous.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to start"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "continue-implementation",
                    "description": "Continue implementing an IN_PROGRESS feature. Orchestrates task execution, quality gates (build/test/review), phase completion with user acceptance, and creates LessonsLearned documents. Automatically resumes from current state.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to continue implementing"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "accept-phase",
                    "description": "Accept a completed phase. Validates requirements, marks phase as COMPLETED in all files (phase file, FeatureTasks.md, start-feature-report), updates time tracking, creates git commit, and previews next phase. Does NOT auto-start next phase.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001)"},
                            "phase_number": {"type": "integer", "description": "The phase number to accept (e.g., 1, 2, 3)"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id", "phase_number"]
                    }
                },
                {
                    "name": "code-review",
                    "description": "Perform comprehensive code review of a phase. Reviews all changed files against CodeGuidelines, validates test quality, generates detailed report with APPROVED/APPROVED_WITH_NOTES/NEEDS_CHANGES status, and updates phase checkpoint.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001)"},
                            "phase_number": {"type": "integer", "description": "The phase number to review (e.g., 2, 3, 4)"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id", "phase_number"]
                    }
                },
                {
                    "name": "complete-feature",
                    "description": "Complete a feature and move to COMPLETED state. Validates all phases done, compiles Lessons Learned (asks user for input), creates completion reports, and moves feature to 04_COMPLETED. REQUIRES USER CONFIRMATION.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to complete"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"}
                        },
                        "required": ["feature_id"]
                    }
                }
            ]
        })

    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        tool_args = request.params.get("input", {})

        try:
            if tool_name == "init-project":
                result = await run_init_project()
            elif tool_name == "submit-feature":
                result = await run_submit_feature(
                    description=tool_args.get("description"),
                    title=tool_args.get("title"),
                    external_id=tool_args.get("external_id")
                )
            elif tool_name == "design-feature":
                result = await run_design_feature(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "refine-feature":
                result = await run_refine_feature(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "start-feature":
                result = await run_start_feature(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "continue-implementation":
                result = await run_continue_implementation(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "accept-phase":
                result = await run_accept_phase(
                    feature_id=tool_args.get("feature_id"),
                    phase_number=tool_args.get("phase_number"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "code-review":
                result = await run_code_review(
                    feature_id=tool_args.get("feature_id"),
                    phase_number=tool_args.get("phase_number"),
                    feature_path=tool_args.get("feature_path")
                )
            elif tool_name == "complete-feature":
                result = await run_complete_feature(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path")
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # The result is now a DICTIONARY of instructions, not just a string
            return JsonRpcResponse(id=request.id, result={"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
        
        except Exception as e:
            return JsonRpcResponse(id=request.id, error={"code": -32603, "message": str(e)})

    return JsonRpcResponse(id=request.id, error={"code": -32601, "message": "Method not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)