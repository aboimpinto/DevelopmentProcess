from client_execution import bind_client_execution
import os
import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, List, Any, Dict, Tuple

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field
from deep_dive_host import HOST_STAGES, hosted_deep_dive_recipe

# --- Constants & Configuration ---
# Path to the directory containing prompt/config files
PROMPTS_DIR = Path(__file__).parent / "Prompts"

DEEP_DIVE_MODES = ("comprehensive", "targeted")
DEEP_DIVE_RESPONSE_MODES = ("adaptive_interview", "question_manifest")
FEATURE_WORKFLOW_MODES = ("autonomous", "single_phase")
ACCEPTANCE_POLICY_VERSION = "acceptance-responsibility/v1"
ACCEPTANCE_POLICY_TOOLS = frozenset(("submit-epic", "submit-feature", "create-epic-features", "link-feature-to-epic", "design-feature", "deep-dive", "refine-feature", "start-feature", "continue-implementation", "code-review", "accept-phase", "complete-feature"))
QUALITY_GATE_POLICY_VERSION = "devcycle-phase-quality/v2"
QUALITY_GATE_TOOLS = frozenset(("refine-feature", "start-feature", "continue-implementation",
                               "code-review", "accept-phase", "complete-feature"))


def normalize_feature_workflow_mode(workflow_mode: Optional[str]) -> str:
    """Validate execution pacing at the MCP boundary; omission means autonomous."""
    normalized = workflow_mode or "autonomous"
    if normalized not in FEATURE_WORKFLOW_MODES:
        raise ValueError(
            f"Unsupported workflow_mode: {normalized}. "
            f"Expected one of: {', '.join(FEATURE_WORKFLOW_MODES)}"
        )
    return normalized


@dataclass(frozen=True)
class DeepDiveRequest:
    """Validated immutable scope for one deep-dive recipe execution."""

    file_path: str
    mode: str
    focus: Tuple[str, ...]
    response_mode: str

    @classmethod
    def create(
        cls,
        file_path: str,
        mode: Optional[str] = None,
        focus: Optional[List[str]] = None,
        response_mode: Optional[str] = None,
    ) -> "DeepDiveRequest":
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("Deep-dive file_path is required")

        normalized_mode = mode or "comprehensive"
        if normalized_mode not in DEEP_DIVE_MODES:
            raise ValueError(
                f"Unsupported deep-dive mode: {normalized_mode}. "
                f"Expected one of: {', '.join(DEEP_DIVE_MODES)}"
            )

        normalized_response_mode = response_mode or "adaptive_interview"
        if normalized_response_mode not in DEEP_DIVE_RESPONSE_MODES:
            raise ValueError(
                f"Unsupported deep-dive response_mode: {normalized_response_mode}. "
                f"Expected one of: {', '.join(DEEP_DIVE_RESPONSE_MODES)}"
            )

        if focus is None:
            normalized_focus: Tuple[str, ...] = ()
        else:
            if not isinstance(focus, (list, tuple)):
                raise ValueError("Deep-dive focus must be an array of questions")
            if any(not isinstance(question, str) or not question.strip() for question in focus):
                raise ValueError("Deep-dive focus questions must be non-empty strings")
            normalized_focus = tuple(question.strip() for question in focus)

        if normalized_mode == "targeted" and not normalized_focus:
            raise ValueError("Targeted deep-dive requires at least one focus question")

        return cls(
            file_path=file_path.strip(),
            mode=normalized_mode,
            focus=normalized_focus,
            response_mode=normalized_response_mode,
        )


def load_procedure(name: str) -> str:
    """Include mandatory dependency ordering in every lifecycle recipe."""
    procedure = (PROMPTS_DIR / name).read_text(encoding="utf-8")
    dependencies = (PROMPTS_DIR / "dependency-order.md").read_text(encoding="utf-8")
    if not dependencies.strip():
        raise ValueError("Required dependency-order.md policy is empty")
    return procedure + "\n\n---\n\n" + dependencies


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

    return {
        "status": "pending_action",
        "action": "create_directories",
        "directories": required_folders,
        "context_files": ["CLAUDE.md"],
        "message": (
            "STEP 1: Read CLAUDE.md and find 'Memory Bank: <path>' under '## DevCycle Settings'. "
            "If not found, ask the user where to store the Memory Bank (suggest 'MemoryBank'), "
            "then write it to CLAUDE.md as:\n\n"
            "## DevCycle Settings\n"
            "Memory Bank: <chosen_path>\n\n"
            "STEP 2: Create the following directories UNDER the Memory Bank path:\n\n"
            + "".join(f"- {{memory_bank}}/{folder}\n" for folder in required_folders)
        )
    }

async def run_submit_epic(description: str, title: Optional[str] = None, external_id: Optional[str] = None) -> dict:
    """
    The Recipe for submitting an epic.
    Returns the step-by-step procedure prompt for the Client's LLM to execute.
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("submit-epic.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{description}}", description or "")
    procedure = procedure.replace("{{title}}", title or "[Not provided - LLM should generate]")
    procedure = procedure.replace("{{external_id}}", external_id or "[Not provided]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "submit-epic",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/"
        ],
        "context_files": [
            "CLAUDE.md",
            "{memory_bank}/Features/00_EPICS/NEXT_EPIC_ID.txt"
        ],
        "message": "Execute the submit-epic procedure. IMPORTANT: Start with Step 0 to read the project context before generating the epic description."
    }

async def run_submit_feature(description: str, title: Optional[str] = None, external_id: Optional[str] = None, epic_id: Optional[str] = None) -> dict:
    """
    The Recipe for submitting a feature.
    Returns the step-by-step procedure prompt for the Client's LLM to execute.
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("submit-feature.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{description}}", description or "")
    procedure = procedure.replace("{{title}}", title or "[Not provided - LLM should generate]")
    procedure = procedure.replace("{{external_id}}", external_id or "[Not provided]")
    procedure = procedure.replace("{{epic_id}}", epic_id or "[Not provided - standalone feature]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "submit-feature",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/",
            "{memory_bank}/Features/00_EPICS/"
        ],
        "context_files": [
            "CLAUDE.md",
            "{memory_bank}/Features/NEXT_FEATURE_ID.txt"
        ],
        "message": "Execute the submit-feature procedure. IMPORTANT: Start with Step 0 to read the project context before generating the feature description."
    }

async def run_create_epic_features(epic_id: str, epic_path: Optional[str] = None) -> dict:
    """
    The Recipe for batch-creating all features defined in an epic.
    Creates features from the epic's Features Breakdown table (TBD entries).
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("create-epic-features.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{epic_id}}", epic_id or "")
    procedure = procedure.replace("{{epic_path}}", epic_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/00_EPICS/ as defined in CLAUDE.md]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "create-epic-features",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/01_SUBMITTED/",
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/"
        ],
        "context_files": [
            "CLAUDE.md",
            "{memory_bank}/Features/NEXT_FEATURE_ID.txt"
        ],
        "message": "Execute the create-epic-features procedure. This will batch-create all TBD features from the epic's Features Breakdown table. User confirmation is required before creating."
    }

async def run_link_feature_to_epic(feature_id: str, epic_id: str, feature_path: Optional[str] = None, epic_path: Optional[str] = None) -> dict:
    """
    The Recipe for linking an existing feature to an epic.
    Updates both the feature and epic documents to establish the relationship.
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("link-feature-to-epic.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{epic_id}}", epic_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in all feature folders]")
    procedure = procedure.replace("{{epic_path}}", epic_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/00_EPICS/ as defined in CLAUDE.md]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "link-feature-to-epic",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/01_SUBMITTED/",
            "{memory_bank}/Features/02_READY_TO_DEVELOP/",
            "{memory_bank}/Features/03_IN_PROGRESS/",
            "{memory_bank}/Features/04_COMPLETED/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "message": "Execute the link-feature-to-epic procedure. This links an existing feature to an epic, updating both documents to maintain the relationship."
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
        procedure_template = load_procedure("design-feature.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "design-feature",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/01_SUBMITTED/",
            "{memory_bank}/Features/02_READY_TO_DEVELOP/"
        ],
        "context_files": [
            "CLAUDE.md"
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
    1. Analyzing all feature-folder documents plus linked epic/dependency context
    2. Creating phased implementation plan
    3. Breaking down into independent tasks with unit tests
    4. Adding checkpoints with quality gates
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("refine-feature.md")
        readiness = (PROMPTS_DIR / "feature-readiness.md").read_text(encoding="utf-8")
        procedure_template += "\n\n---\n\n" + readiness
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "refine-feature",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/01_SUBMITTED/",
            "{memory_bank}/Features/02_READY_TO_DEVELOP/",
            "{memory_bank}/Features/03_IN_PROGRESS/",
            "{memory_bank}/Features/04_COMPLETED/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "FeatureDescription.md",
            "FeatureTasks.md",
            "readiness-validation.md",
            "ImplementationContract.md (when applicable)",
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
        "message": "Execute the refine-feature procedure. Read the full feature folder plus any linked epic/dependency context, then create a phased implementation plan with tasks, unit tests, and quality checkpoints. Execute the included shared readiness gate and save readiness-validation.md before declaring READY or moving to 02_READY_TO_DEVELOP."
    }

async def run_start_feature(feature_id: str, feature_path: Optional[str] = None, workflow_mode: Optional[str] = None) -> dict:
    """
    The Recipe for starting a feature (moving to IN_PROGRESS).
    Validates the feature and transitions from 02_READY_TO_DEVELOP to 03_IN_PROGRESS:
    1. Pre-validation (consistency, completeness, ambiguity detection)
    2. Post-validation (time tracking, checkpoints, auto-fix)
    3. Git branch creation (if connected)
    4. Move to 03_IN_PROGRESS
    5. Git commit and push (if connected)
    6. Optionally hand off to autonomous end-to-end implementation workflow
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("start-feature.md")
        readiness = (PROMPTS_DIR / "feature-readiness.md").read_text(encoding="utf-8")
        procedure_template += "\n\n---\n\n" + readiness
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    resolved_workflow_mode = normalize_feature_workflow_mode(workflow_mode)
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")
    procedure = procedure.replace("{{workflow_mode}}", resolved_workflow_mode)

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "start-feature",
        "workflow_mode": resolved_workflow_mode,
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/02_READY_TO_DEVELOP/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "pre-validation-report-[STATUS]-[timestamp].md",
            "start-feature-report-[timestamp].md"
        ],
        "message": "Execute the start-feature procedure. This validates the feature, creates a git branch, and moves it to 03_IN_PROGRESS. workflow_mode defaults to autonomous; single_phase implements and accepts exactly the first incomplete phase, then stops. If pre-validation fails, the process STOPS with a rejection report."
    }

async def run_continue_implementation(feature_id: str, feature_path: Optional[str] = None, mode: Optional[str] = None, workflow_mode: Optional[str] = None) -> dict:
    """
    The Recipe for continuing feature implementation.
    Orchestrates the systematic implementation of an IN_PROGRESS feature:
    1. Discovers current state (feature, phase, task)
    2. Creates/refines the canonical Phase 1 planning document using feature, epic, and dependency context
    3. Executes tasks following specifications
    4. Manages quality (build, tests, code-review)
    5. Tracks progress (update phase files, FeatureTasks.md)
    6. Hands off phase acceptance (interactive or autonomous workflow)
    7. Creates LessonsLearned documents per phase
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("continue-implementation.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    resolved_workflow_mode = normalize_feature_workflow_mode(workflow_mode)
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")
    procedure = procedure.replace("{{mode}}", mode or "[Not provided - default auto-detect]")
    procedure = procedure.replace("{{workflow_mode}}", resolved_workflow_mode)

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "continue-implementation",
        "workflow_mode": resolved_workflow_mode,
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/01_SUBMITTED/",
            "{memory_bank}/Features/02_READY_TO_DEVELOP/",
            "{memory_bank}/Features/03_IN_PROGRESS/",
            "{memory_bank}/Features/04_COMPLETED/",
            "{memory_bank}/LessonsLearned/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "Phase updates in Phases/*.md",
            "FeatureTasks.md updates",
            "planning-analysis-report.md (canonical Phase 1 planning artifact)",
            "code-reviews/phase-{N}/*.md",
            "LessonsLearned/{feature_id}/Phase-{N}-{name}.md",
            "feature-completion-report.md (when all phases complete)"
        ],
        "message": "Execute the continue-implementation procedure locally. FIRST write operation when entering a PENDING phase: set phase status IN_PROGRESS in BOTH phase file and FeatureTasks.md. Keep statuses synchronized and enforce clean configured gates: zero build/lint warnings or errors and 100% tests, repairing pre-existing failures under the Boy Scout Rule. workflow_mode defaults to autonomous; single_phase implements and accepts exactly one phase, then stops."
    }

async def run_accept_phase(feature_id: str, phase_number: int, feature_path: Optional[str] = None, workflow_mode: Optional[str] = None) -> dict:
    """
    The Recipe for accepting a completed phase.
    Formalizes phase acceptance after all quality gates pass:
    1. Validates checkpoint was filled
    2. Validates phase is awaiting acceptance
    3. Validates technical requirements (build, tests, code review)
    4. Handles incomplete tasks (with user justification)
    5. Marks phase as COMPLETED in all files
    6. Updates time tracking with actual vs estimated
    7. Creates git commit with achievements
    8. Previews next phase (and optionally auto-continues in autonomous workflow mode)
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("accept-phase.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    resolved_workflow_mode = normalize_feature_workflow_mode(workflow_mode)
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{phase_number}}", str(phase_number) if phase_number is not None else "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")
    procedure = procedure.replace("{{workflow_mode}}", resolved_workflow_mode)

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "accept-phase",
        "workflow_mode": resolved_workflow_mode,
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/03_IN_PROGRESS/",
            "{memory_bank}/LessonsLearned/"
        ],
        "context_files": [
            "CLAUDE.md"
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
        "message": "Execute the accept-phase procedure. Accept only evidence from fully green configured build, lint, and test commands. workflow_mode defaults to autonomous; single_phase stops after this phase is accepted."
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
        procedure_template = load_procedure("code-review.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{phase_number}}", str(phase_number) if phase_number is not None else "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "code-review",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/LessonsLearned/",
            "{memory_bank}/Features/03_IN_PROGRESS/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "code-reviews/phase-{N}/Code-Review-{timestamp}-{STATUS}.md",
            "Phase checkpoint updated with review results"
        ],
        "message": "Execute the code-review procedure locally. `pending_execution` is expected and means the MCP call succeeded with a recipe to run. Do not retry the same code-review MCP call unless a procedure step explicitly requires it."
    }

async def run_complete_feature(feature_id: str, feature_path: Optional[str] = None, workflow_mode: Optional[str] = None) -> dict:
    """
    The Recipe for completing a feature.
    Validates all requirements and moves feature to COMPLETED state:
    1. Validates all phases are COMPLETED (or SKIPPED with justification)
    2. Verifies git repository is clean (no uncommitted/unpushed changes)
    3. Verifies build and tests pass (0 errors, 0 warnings, 100% tests)
    4. Compiles Lessons Learned from all phases into feature-level document
    5. Asks user for additional lessons they want to highlight (or skips the prompt in autonomous workflow mode)
    6. Updates feature and parent epic with completion status and available PR/merge evidence
    7. Synchronizes linked epic acceptance tests and design/screen tracking when present
    8. Creates completion reports (validation, metrics, lessons learned)
    9. Moves feature to 04_COMPLETED folder
    10. Creates completion git commit and pushes
    """
    # Load the procedure template
    try:
        procedure_template = load_procedure("complete-feature.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    # Replace placeholders with actual values
    procedure = procedure_template.replace("{{feature_id}}", feature_id or "")
    procedure = procedure.replace("{{feature_path}}", feature_path or "[Not provided - search in {MEMORY_BANK_PATH}/Features/ as defined in CLAUDE.md]")
    procedure = procedure.replace("{{workflow_mode}}", workflow_mode or "[Not provided - interactive default]")

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "complete-feature",
        "instructions": procedure,
        "context_folders": [
            "{memory_bank}/Features/00_EPICS/",
            "{memory_bank}/Features/03_IN_PROGRESS/",
            "{memory_bank}/LessonsLearned/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "feature-completion-report.md",
            "{memory_bank}/LessonsLearned/{feature_id}/Feature-Completion-LessonsLearned.md",
            "FeatureTasks.md updated with completion status",
            "FeatureDescription.md updated with every associated PR and available merge evidence",
            "Linked EpicDescription.md updated with completion and delivery references (if applicable)",
            "Feature folder moved to 04_COMPLETED/",
            "Git commit with completion details"
        ],
        "message": "Execute the complete-feature procedure. This validates all phases are complete, compiles Lessons Learned, synchronizes any linked epic documentation (including acceptance/design tracking when present), and moves the feature to 04_COMPLETED. In `workflow_mode=autonomous`, use auto-detected lessons only instead of pausing for extra user input. Running this command is confirmation to proceed (no extra yes/no gate)."
    }

async def run_deep_dive(
    file_path: str,
    mode: Optional[str] = None,
    focus: Optional[List[str]] = None,
    response_mode: Optional[str] = None,
    stage: Optional[str] = None,
) -> dict:
    """Return a single-target comprehensive or targeted deep-dive recipe."""
    if response_mode == "host_stage":
        return hosted_deep_dive_recipe(PROMPTS_DIR, file_path, stage)
    if stage is not None:
        raise ValueError("stage requires host_stage response mode")
    request = DeepDiveRequest.create(
        file_path=file_path,
        mode=mode,
        focus=focus,
        response_mode=response_mode,
    )

    try:
        procedure_template = load_procedure("deep-dive.md")
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "error",
            "message": f"Cannot load required procedure policy: {exc}"
        }

    focus_text = (
        "\n".join(f"- {question}" for question in request.focus)
        if request.focus
        else "- [No targeted focus supplied; use the selected file-type checklist]"
    )
    procedure = procedure_template.replace("{{file_path}}", request.file_path)
    procedure = procedure.replace("{{mode}}", request.mode)
    procedure = procedure.replace("{{focus}}", focus_text)
    procedure = procedure.replace("{{response_mode}}", request.response_mode)
    manifest_mode = request.response_mode == "question_manifest"

    return {
        "status": "pending_execution",
        "action": "execute_procedure",
        "procedure_name": "deep-dive",
        "instructions": procedure,
        "deep_dive_scope": {
            "target_file": request.file_path,
            "mode": request.mode,
            "focus": list(request.focus),
            "response_mode": request.response_mode,
            "mutation_scope": [] if manifest_mode else [request.file_path],
        },
        "context_folders": [
            "{memory_bank}/Overview/",
            "{memory_bank}/Architecture/",
            "{memory_bank}/CodeGuidelines/",
            "{memory_bank}/Features/"
        ],
        "context_files": [
            "CLAUDE.md"
        ],
        "outputs": [
            "DeepDiveQuestionManifestV1 JSON"
            if manifest_mode
            else f"{request.file_path} (the only file that may be updated)"
        ],
        "message": (
            f"Execute the {request.mode} deep-dive procedure for exactly one target file "
            f"using response mode {request.response_mode}. "
            "Linked EPICs, FEATs, and references are read-only context."
        )
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


def extract_tool_call(params: Optional[Union[Dict[str, Any], List[Any]]]) -> tuple[str, Dict[str, Any]]:
    """Accept standard MCP `arguments` while preserving the legacy `input` client shape."""
    if not isinstance(params, dict):
        raise ValueError("Invalid tools/call params: expected an object")

    tool_name = params.get("name")
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("Invalid tools/call params: name is required")

    raw_args = params.get("arguments", params.get("input", {}))
    if raw_args is None:
        raw_args = {}
    if not isinstance(raw_args, dict):
        raise ValueError("Invalid tools/call params: arguments must be an object")

    return tool_name, raw_args


def enrich_execution_contract(result: dict, tool_name: str) -> dict:
    """
    Add deterministic orchestration hints so any MCP client can act consistently.
    Keeps existing payload shape while adding machine-readable contract fields.
    """
    if not isinstance(result, dict):
        return result

    status_value = result.get("status")

    # Common metadata for all tool responses
    result.setdefault("contract_version", "1.0")
    result.setdefault("tool_name", tool_name)

    if status_value == "pending_execution":
        if tool_name in QUALITY_GATE_TOOLS:
            # Fail closed if the shared policy is missing; never serve a partial
            # quality recipe. Both MCP response representations carry this text.
            policy = (PROMPTS_DIR / "phase-quality-policy.md").read_text(encoding="utf-8")
            if QUALITY_GATE_POLICY_VERSION not in policy:
                raise ValueError("Shared phase quality policy version is missing or incompatible")
            command_policy = (PROMPTS_DIR / "project-test-plan-authoring-policy.md").read_text(encoding="utf-8")
            policy += "\n\n" + command_policy
            result["quality_gate_policy_version"] = QUALITY_GATE_POLICY_VERSION
            gate_schema = json.loads((PROMPTS_DIR / "phase-gates-exchange-v1.schema.json").read_text(encoding="utf-8"))
            result["phase_gate_exchange_schema"] = gate_schema
            policy += "\n\nExact phase gate JSON Schema (publish <phase-document>.gates.json; the phase document filename is its opaque phaseId):\n" + json.dumps(gate_schema, indent=2)
            result["instructions"] = policy + "\n\n---\n\n" + result["instructions"]
        if tool_name in ACCEPTANCE_POLICY_TOOLS and "deep_dive_host_contract" not in result:
            acceptance_policy = (PROMPTS_DIR / "acceptance-responsibility-policy.md").read_text(encoding="utf-8")
            if ACCEPTANCE_POLICY_VERSION not in acceptance_policy:
                raise ValueError("Acceptance responsibility policy version is missing or incompatible")
            result["acceptance_policy_version"] = ACCEPTANCE_POLICY_VERSION
            result["instructions"] = acceptance_policy + "\n\n---\n\n" + result["instructions"]
        # This is a successful tool call that returns a recipe for client-side execution.
        result.setdefault("tool_call_success", True)
        result.setdefault("execution_owner", "client_llm")
        result.setdefault("retry_same_tool", False)
        result.setdefault("next_action", "execute_returned_procedure")
        result.setdefault(
            "client_directive",
            "Execute the returned procedure locally. Do not retry this same MCP call unless a step explicitly requires it.",
        )
    elif status_value == "pending_action":
        result.setdefault("tool_call_success", True)
        result.setdefault("execution_owner", "client_llm")
        result.setdefault("retry_same_tool", False)
        result.setdefault("next_action", "perform_requested_action")
    elif status_value == "error":
        result.setdefault("tool_call_success", False)
    else:
        result.setdefault("tool_call_success", True)

    return bind_client_execution(result, tool_name)

@app.post("/", response_model=JsonRpcResponse, response_model_exclude_none=True)
async def json_rpc_handler(request: JsonRpcRequest):
    if request.id is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if request.method == "initialize":
        return JsonRpcResponse(id=request.id, result={
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "DevCycleManager", "version": "0.3.0-remote"},
            "capabilities": {"tools": {"listChanged": False}}
        })

    elif request.method == "tools/list":
        return JsonRpcResponse(id=request.id, result={
            "tools": [
                {
                    "name": "init-project",
                    "description": "Initialize the memory bank folder structure (path configured in CLAUDE.md).",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "submit-epic",
                    "description": "Submit a new epic (large body of work containing multiple features). Returns a step-by-step procedure that creates an epic in 00_EPICS with EpicDescription.md. Use deep-dive afterward to refine details.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "The epic description from the user - what strategic goal or major capability is being built"},
                            "title": {"type": "string", "description": "Optional: A title for the epic. If not provided, LLM will generate one."},
                            "external_id": {"type": "string", "description": "Optional: External reference ID (e.g., initiative ID, roadmap item)"}
                        },
                        "required": ["description"]
                    }
                },
                {
                    "name": "submit-feature",
                    "description": "Submit a new feature idea. Returns a step-by-step procedure for the LLM to execute.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "The feature description from the user"},
                            "title": {"type": "string", "description": "Optional: A title for the feature. If not provided, LLM will generate one."},
                            "external_id": {"type": "string", "description": "Optional: External reference ID (e.g., ticket number, user story ID)"},
                            "epic_id": {"type": "string", "description": "Optional: Parent epic ID (e.g., EPIC-001) to link this feature to an epic"}
                        },
                        "required": ["description"]
                    }
                },
                {
                    "name": "create-epic-features",
                    "description": "Batch-create all features defined in an epic's Features Breakdown table. Creates features with TBD IDs and updates the epic with actual FEAT-XXX IDs. Requires user confirmation.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "epic_id": {"type": "string", "description": "The epic ID (e.g., EPIC-001) containing the features to create"},
                            "epic_path": {"type": "string", "description": "Optional: Direct path to the epic folder if known"}
                        },
                        "required": ["epic_id"]
                    }
                },
                {
                    "name": "link-feature-to-epic",
                    "description": "Link an existing feature to an epic. Updates both the feature's Parent Epic field and the epic's Features Breakdown, Progress Tracking, and Dependency Diagram.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to link"},
                            "epic_id": {"type": "string", "description": "The epic ID (e.g., EPIC-001) to link the feature to"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"},
                            "epic_path": {"type": "string", "description": "Optional: Direct path to the epic folder if known"}
                        },
                        "required": ["feature_id", "epic_id"]
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
                    "description": "Refine a feature into implementable tasks using the full feature folder plus linked epic/dependency context. Creates a phased implementation plan with tasks, unit tests, and quality checkpoints, then moves the feature from 01_SUBMITTED to 02_READY_TO_DEVELOP.",
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
                    "description": "Returns operations for the calling coding agent to execute locally. Start implementing a feature. Validates (pre + post), creates a git branch, moves to 03_IN_PROGRESS, and by default continues autonomously. Set workflow_mode=single_phase to implement and accept only the next phase.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to start"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"},
                            "workflow_mode": {"type": "string", "enum": ["autonomous", "single_phase"], "default": "autonomous", "description": "Execution pacing. autonomous continues end-to-end (default); single_phase implements and accepts exactly the next phase, then stops."}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "continue-implementation",
                    "description": "Returns operations for the calling coding agent to execute locally. Continue implementing an IN_PROGRESS feature. Phase 1 creates or refreshes the canonical `planning-analysis-report.md` using feature, epic, and dependency context; later phases must read and reuse it instead of re-planning. Also orchestrates task execution, quality gates (build/test/review), downstream-aware test coverage, phase completion, and LessonsLearned documents. With `workflow_mode=autonomous`, it continues through code review, phase acceptance, next phases, and final completion without routine user interaction.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to continue implementing"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"},
                            "mode": {"type": "string", "description": "Optional: set to 'finalize_current_phase' to force validation + phase-finalization reconciliation when tasks are done but statuses are not synchronized"},
                            "workflow_mode": {"type": "string", "enum": ["autonomous", "single_phase"], "default": "autonomous", "description": "Execution pacing. autonomous continues end-to-end (default); single_phase implements and accepts exactly the current/next phase, then stops."}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "accept-phase",
                    "description": "Returns operations for the calling coding agent to execute locally. Accept a completed phase. Validates requirements, marks phase as COMPLETED in all files (phase file, FeatureTasks.md, start-feature-report), updates time tracking, creates git commit, and previews next phase. With `workflow_mode=autonomous`, it continues automatically to the next phase or feature completion when safe.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001)"},
                            "phase_number": {"type": "integer", "description": "The phase number to accept (e.g., 1, 2, 3)"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"},
                            "workflow_mode": {"type": "string", "enum": ["autonomous", "single_phase"], "default": "autonomous", "description": "Execution pacing. autonomous continues to the next phase (default); single_phase stops after this phase is accepted."}
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
                    "description": "Complete a feature and move to COMPLETED state. Validates all phases done, compiles Lessons Learned, synchronizes linked epic documentation (including acceptance tests and design/screen tracking when present), creates completion reports, and moves the feature to 04_COMPLETED. With `workflow_mode=autonomous`, it skips the extra lessons prompt and uses auto-detected lessons only. Invocation is treated as confirmation to proceed.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "feature_id": {"type": "string", "description": "The feature ID (e.g., FEAT-001) to complete"},
                            "feature_path": {"type": "string", "description": "Optional: Direct path to the feature folder if known"},
                            "workflow_mode": {"type": "string", "description": "Optional: set to 'autonomous' to finalize without pausing for extra lessons-learned input"}
                        },
                        "required": ["feature_id"]
                    }
                },
                {
                    "name": "deep-dive",
                    "description": "Conduct a single-target comprehensive or targeted interview about one spec file. Linked EPICs, FEATs, and references are read-only context; only the target file may be updated.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "minLength": 1, "description": "The sole spec file to deep-dive into (for example an EpicDescription.md or FeatureDescription.md)"},
                            "mode": {"type": "string", "enum": ["comprehensive", "targeted"], "default": "comprehensive", "description": "Use comprehensive for an initial full interview, or targeted to resolve supplied focus questions only"},
                            "focus": {"type": "array", "items": {"type": "string", "minLength": 1}, "description": "Questions or validation points to resolve. Required when mode is targeted."},
                            "response_mode": {"type": "string", "enum": ["adaptive_interview", "question_manifest", "host_stage"], "default": "adaptive_interview", "description": "Use adaptive_interview for a conversational interview, question_manifest for a complete question batch, or host_stage for one host-owned UI turn."},
                            "stage": {"type": "string", "enum": list(HOST_STAGES), "description": "Required with host_stage; no file mutation."}
                        },
                        "required": ["file_path"]
                    }
                }
            ]
        })

    elif request.method == "tools/call":
        try:
            tool_name, tool_args = extract_tool_call(request.params)
            if tool_name == "init-project":
                result = await run_init_project()
            elif tool_name == "submit-epic":
                result = await run_submit_epic(
                    description=tool_args.get("description"),
                    title=tool_args.get("title"),
                    external_id=tool_args.get("external_id")
                )
            elif tool_name == "submit-feature":
                result = await run_submit_feature(
                    description=tool_args.get("description"),
                    title=tool_args.get("title"),
                    external_id=tool_args.get("external_id"),
                    epic_id=tool_args.get("epic_id")
                )
            elif tool_name == "create-epic-features":
                result = await run_create_epic_features(
                    epic_id=tool_args.get("epic_id"),
                    epic_path=tool_args.get("epic_path")
                )
            elif tool_name == "link-feature-to-epic":
                result = await run_link_feature_to_epic(
                    feature_id=tool_args.get("feature_id"),
                    epic_id=tool_args.get("epic_id"),
                    feature_path=tool_args.get("feature_path"),
                    epic_path=tool_args.get("epic_path")
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
                    feature_path=tool_args.get("feature_path"),
                    workflow_mode=tool_args.get("workflow_mode")
                )
            elif tool_name == "continue-implementation":
                result = await run_continue_implementation(
                    feature_id=tool_args.get("feature_id"),
                    feature_path=tool_args.get("feature_path"),
                    mode=tool_args.get("mode"),
                    workflow_mode=tool_args.get("workflow_mode")
                )
            elif tool_name == "accept-phase":
                result = await run_accept_phase(
                    feature_id=tool_args.get("feature_id"),
                    phase_number=tool_args.get("phase_number"),
                    feature_path=tool_args.get("feature_path"),
                    workflow_mode=tool_args.get("workflow_mode")
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
                    feature_path=tool_args.get("feature_path"),
                    workflow_mode=tool_args.get("workflow_mode")
                )
            elif tool_name == "deep-dive":
                result = await run_deep_dive(
                    file_path=tool_args.get("file_path"),
                    mode=tool_args.get("mode"),
                    focus=tool_args.get("focus"),
                    response_mode=tool_args.get("response_mode"),
                    stage=tool_args.get("stage")
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            result = enrich_execution_contract(result, tool_name)

            # Backward compatible:
            # - `content[0].text` keeps existing clients working.
            # - `structuredContent` gives deterministic machine-readable data for robust orchestration.
            return JsonRpcResponse(
                id=request.id,
                result={
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}],
                    "structuredContent": result,
                    "isError": result.get("status") == "error"
                }
            )
        
        except Exception as e:
            return JsonRpcResponse(id=request.id, error={"code": -32603, "message": str(e)})

    return JsonRpcResponse(id=request.id, error={"code": -32601, "message": "Method not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
