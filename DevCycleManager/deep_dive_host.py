"""Stateless procedures for a host-owned adaptive interview UI."""
import json
from pathlib import Path

HOST_STAGES = ("opening", "follow_up", "clarify", "apply_answers")
HOST_CONTRACT = "devcycle-deep-dive-host/v1"


def hosted_deep_dive_recipe(prompts_dir: Path, file_path: str, stage: str) -> dict:
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("Hosted Deep-Dive requires file_path")
    if stage not in HOST_STAGES:
        raise ValueError("Unsupported hosted Deep-Dive stage")
    directory = prompts_dir / "deep-dive-host"
    common = (directory / "common.md").read_text(encoding="utf-8")
    procedure = (directory / f"{stage}.md").read_text(encoding="utf-8")
    result = {
        "status": "pending_execution", "action": "execute_procedure",
        "execution_owner": "client_llm", "retry_same_tool": False,
        "procedure_name": "deep-dive",
        "instructions": common + "\n\n" + procedure,
        "deep_dive_host_contract": {
            "version": HOST_CONTRACT, "stage": stage,
            "target_file": file_path.strip(), "mutation_scope": [],
            "output": "questions_json" if stage in ("opening", "follow_up") else
                      "target_edits_json" if stage == "apply_answers" else "clarification_text",
        },
    }
    if stage in ("opening", "follow_up", "apply_answers"):
        schema_name = "edits-v1.schema.json" if stage == "apply_answers" else "questions-v1.schema.json"
        schema = json.loads((directory / schema_name).read_text(encoding="utf-8"))
        # Supply only the selected output schema. The host validates the same
        # versioned contract and enforces stage-specific cardinality/authority.
        result["instructions"] += "\n\nReturn JSON matching this schema:\n" + json.dumps(schema, indent=2)
    return result
