"""Instruction-only lifecycle handoff; this server never executes client work."""

LIFECYCLE_ENTRIES = {
    "start-feature": "initialize_feature_then_resume",
    "continue-implementation": "resume_recorded_task",
    "accept-phase": "validate_phase_then_continue",
}

# One execution loop for fresh starts and resumptions. Only the entry differs.
CLIENT_LOOP = """Execute the returned operations now using your local tools. This is an
instruction recipe, not a task result or a background job. The MCP call succeeded
in delivering instructions; it has not executed, tested or completed the feature.
You, the calling coding agent, own execution through the selected completion boundary.

1. Enter at the specified operation and resolve the current feature/phase/task
   from its artifacts. Start Feature performs setup and then joins the same
   implementation loop as Continue Implementation; setup is not the completion
   boundary. Preserve workspace authority and perform the declared entry checks.
2. Finish the current task and all remaining tasks in the phase. A partial commit,
   progress report, passing subset or IN_PROGRESS task is not a stopping point.
   After every commit and evidence update, read the current task's remaining
   deliverables. If unfinished, keep it IN_PROGRESS and execute its next operation.
   If finished and verified, record completion and immediately select the first
   pending task in declared order, mark it IN_PROGRESS and execute it in this same
   session. If no tasks remain, execute the phase gates. Do not end the turn or
   ask the user to send another continue command at a task boundary.
3. Execute the phase's declared checks and applicable review/coverage assessment.
   Unfinished tasks, missing evidence, failing tests and review findings block
   acceptance, not continued execution. Repair them within scope and rerun the
   affected checks; never waive a gate or invent additional acceptance criteria.
4. Once phase obligations pass, execute accept-phase and its returned operations.
   Preserve workflow_mode across handoffs. In autonomous mode you MUST continue
   to the next phase and, after the last phase, execute complete-feature.
   Activating the next phase or recording its resume point is not execution of
   that phase: immediately perform its next pending implementation/check operation.
5. Give interim progress updates while continuing tool execution. Return a final
   answer only at the selected completion boundary or a documented inability to
   proceed, cancellation or explicit user pause. An inability must name the exact
   obstacle, attempted repairs, preserved evidence and missing authority, resource
   or decision. Ordinary pending work and the absence of a background job do not
   establish an inability. Reassess repeated failures and stop safely at a genuine
   impasse rather than looping without progress. Do not retry this same MCP call
   instead of executing its recipe; invoke it again only for an explicit handoff.
   Before any final answer, compare the artifacts with the completion boundary.
   If ordinary work remains and there is no documented inability, cancellation or
   explicit pause, execute the next tool operation instead of returning a final
   summary. Saying "the autonomous procedure did not complete" does not establish
   a blocker. A passing check, clean worktree or successful commit is not one either.

Execution limits and context ownership:
- Continue one bounded task operation at a time. The remaining feature does not
  need to fit in one response or context window. Estimated hours, phase count,
  substantial remaining work and synchronous execution do not establish a limit.
- Do not invent a session, token, time or cost budget. A resource-limit stop must
  cite its actual source: an explicit user/runtime constraint or an observed
  provider/tool failure. State the limit/error, available allowance if known,
  recovery attempted where permitted, and why the next required operation cannot
  proceed within that constraint. Do not fabricate allowance or error evidence.
- Respect actual limits, cancellation and higher-priority instructions. Never
  bypass a quota, disable a safeguard or continue beyond an explicit user cap.
  When no such constraint prevents the next operation, execute it rather than
  stopping because the full remaining workload appears large.
- The client harness owns context management and compaction. Keep durable task
  and evidence records and let the harness compact/recover using its supported
  mechanisms, then resume the next operation from those records. Context growth
  alone is not a blocker; a real unrecoverable context failure must be evidenced.
  Do not assume a compaction tool exists or require the user to restart merely
  because compaction may eventually be needed.
- A resume note preserves state; it neither proves inability nor authorizes an
  early final answer. "This synchronous session cannot safely complete the
  remaining phases within its execution budget" is not a valid reason without
  the concrete constraint and evidence above. The absence of a background job
  does not change the calling client's obligation to continue executing locally.
"""


def bind_client_execution(result: dict, tool_name: str) -> dict:
    if result.get("status") != "pending_execution" or tool_name not in LIFECYCLE_ENTRIES:
        return result
    mode = result["workflow_mode"]
    if mode not in ("autonomous", "single_phase"):
        raise ValueError("Invalid client execution workflow mode")
    boundary = ("feature_completed" if mode == "autonomous" else "selected_phase_accepted")
    pacing = (
        "Autonomous: execute all remaining phases and feature completion before returning."
        if mode == "autonomous" else
        "Single phase: implement and accept exactly the selected incomplete phase, then stop; "
        "do not activate another phase or complete the feature in this action."
    )
    directive = (
        f"Workflow mode: {mode}. Entry: {LIFECYCLE_ENTRIES[tool_name]}.\n{pacing}\n"
        "This response supplies operations, not a task result or a background job. "
        "The server has not executed, tested or completed the feature. You must execute "
        "the Client execution loop in the instructions using local tools. Pending tasks "
        "and failed gates require continued work, not a partial final answer. Stop only "
        "at the selected completion boundary or a documented inability to proceed, "
        "cancellation or explicit user pause. After each commit, continue the unfinished "
        "task; after task completion, immediately execute the next pending task in the "
        "same session; after the last task, execute the declared phase gates. "
        "Do not ask for another continue command or return a final summary while "
        "ordinary work remains. Work one bounded operation at a time; the whole "
        "feature need not fit in one response or context window. Never infer an "
        "execution budget from remaining workload or synchronous execution. "
        "A resource-limit stop requires an explicit user/runtime constraint or "
        "observed failure preventing the next operation; respect real limits. "
        "The client harness owns context compaction and recovery."
    )
    result["client_directive"] = directive
    result["instructions"] += "\n\n## Client execution loop\n\n" + pacing + "\n\n" + CLIENT_LOOP
    # Place ownership and next action before the long policy/procedure in both
    # serialized representations. Keep their JSON bodies equivalent for clients.
    return {
        "status": result["status"],
        "action": result["action"],
        "execution_owner": "client_llm",
        "next_action": "execute_returned_procedure",
        "workflow_mode": mode,
        "completion_boundary": boundary,
        "client_directive": directive,
        **result,
    }
