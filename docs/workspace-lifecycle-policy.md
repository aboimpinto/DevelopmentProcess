# Workspace lifecycle and recovery

The shared [phase quality policy](../DevCycleManager/Prompts/phase-quality-policy.md)
owns the repository contract served by MCP. HEPHA supplies checkout authority;
Pi executes the procedure and records real Git evidence. No phase number or
review/coverage flag selects repository safety rules.

| Boundary | Required behavior |
| --- | --- |
| Fresh start | Resolve the authorized checkout and require clean entry before setup writes or the lifecycle move. |
| Startup handoff | Reconcile setup-generated files, save reports, finalize applicable commits/publishing, then verify cleanliness. |
| Initial checkpoint | Verify identity and clean entry; execute declared checks; reconcile their outputs and verify clean exit. |
| Resume | Inspect before activation or acceptance; preserve current-task changes and resolve unknown/deferred ownership. |
| Acceptance | Validate declared gates, finalize owned changes, verify clean exit, and only then advance. |

External shared documentation repositories are outside code Git authority. Their
unrelated changes do not block the feature. External documentation updates are
reported separately; they do not require an empty product commit. A failed commit
or required push leaves finalization pending. Cleanliness never certifies tests.

Interrupted work needs a durable handoff: record the task owner, source revision,
paths, saved snapshot identity and restoration point in the owning phase before
retrying. Check recorded backups and the stash list before recreating missing
files. Restore only verified feature-owned work without overwriting new edits.
Keep failed evidence and backups until recovery is verified. A stash is preservation,
not completion or permission to discard an unresolved obligation.

## Acceptance scenarios

```gherkin
Scenario: Dirty checkout before startup
  Given the selected code checkout contains unaccounted changes
  When start-feature inspects workspace entry
  Then it preserves those files and resolves recovery before setup writes
  And it does not move the feature into progress or start a phase

Scenario: Startup creates a tracked report
  Given startup began in a clean authorized checkout
  When setup and report generation create authorized tracked changes
  Then those changes are finalized before the final clean check
  And implementation starts only after the clean handoff succeeds

Scenario: Initial checkpoint produces generated files
  Given the initial checkpoint has declared health checks
  When those checks produce files
  Then the checkpoint retains declared evidence and reconciles its own outputs
  And it verifies clean exit without inventing review or coverage obligations

Scenario: Resume interrupted work from the current task
  Given dirty files belong to the current interrupted task
  When continue-implementation resolves ownership before activation
  Then it preserves and resumes that work
  And dirty status alone does not reject the resume

Scenario: Task ownership moved while files were saved
  Given a task moved to a later phase with unresolved failed evidence
  And its files were preserved in a named snapshot
  When the owner task resumes
  Then its phase supplies the snapshot identity and restoration point
  And recovery checks the backup before recreating files
  And unresolved evidence remains unresolved until verification passes

Scenario: Documentation-only acceptance with an external MemoryBank
  Given documentation criteria pass and no executable checks are declared
  And the authorized code checkout is clean with no changes to commit
  When accept-phase finalizes the phase
  Then it records the unchanged code HEAD and external document updates
  And it does not require an empty commit or shared-parent Git cleanliness

Scenario: Commit or required publishing fails
  Given applicable task gates passed
  When required finalization fails
  Then phase and feature retain an incomplete finalization status
  And no next phase is activated
```

`test_workspace_lifecycle.py` verifies that these instructions reach the actual
JSON-RPC recipe boundaries, in the correct order and without contradictory legacy
commands. This stateless server test does not certify that a model obeys the
instructions; live runs must still supply the Git and phase-artifact evidence.
