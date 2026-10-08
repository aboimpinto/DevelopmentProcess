## Shared Feature Readiness Gate

**Gate version: 2.** This gate is included by the server in both `refine-feature`
and `start-feature`. It is the authoritative readiness standard for both.
Apply it to the finished plan before declaring READY, and recheck it before
starting. A successful MCP call returns instructions; it does not certify that
the client has executed these checks.

### Resolve decisions using existing authority

Read project instructions, recorded user decisions, feature/epic scope, and the
relevant code and tests. Distinguish verified behavior, intended changes, and
unverified assumptions. Reuse answers from deep-dive and previous refinement.
Resolve ordinary technical choices within the agreed scope and document their
reasoning. Do not send the user back to deep-dive for those choices.

Ask only about unresolved decisions that change user-visible behavior or scope
and cannot be determined from existing authority, or about genuinely missing
external information. Internal naming, algorithms, and code organization need
not be frozen before development. Inspect unresolved markers in context:
historical superseded questions and unrelated future enhancements are not current
specification blockers. A future-feature TODO that supplies a required capability
is a dependency blocker; apply the included Required Dependency Order policy.
Pending results may remain planned at refinement, but required execution evidence
must exist before dependent work or acceptance.

### Contract and coverage checks

For each row record PASS with file/section evidence, justified N/A, or BLOCKED
with the exact missing capability, evidence, or decision. Keep detail proportional to the feature.

| ID | Check | Required evidence when applicable |
|----|-------|-----------------------------------|
| R1 | Scope and consistency | Feature, epic, dependencies, task plan, and acceptance scenarios agree; every requirement has an owner/task; historical claims and deliberate corrections are distinguished. Apply Required Dependency Order: record cross-epic prerequisites and actual availability; an unavailable external prerequisite blocks READY. Same-feature enabling tasks must precede consumers. |
| R2 | Persisted and public contracts | Exact relevant filenames/paths, field names/types, required/optional values, versions, identity/integrity rules, reader validation, and invalid/missing-data behavior. Define semantics in prose/tables or schemas; method bodies are unnecessary. |
| R3 | Ordering and failures | Ordered side effects, commit/eligibility boundary, partial-state retention/cleanup, retry/recovery ownership, and externally observable result at each meaningful failure boundary. Do not imply cross-system atomicity without evidence. |
| R4 | Compatibility | Existing supported inputs and consumers, legacy versions/readers, output shapes/status/exit behavior, and deliberate breaking changes. Check less prominent modes too, such as file versus directory input. |
| R5 | Acceptance traceability | Stable scenario IDs/tags link Given/When/Then acceptance scenarios to implementation tasks and planned integration tests. Cover happy paths, contract validation, failure boundaries, and preserved modes. Include reproducible manual steps and expected outcomes. Distinguish PLANNED, BOUND, and actually RUN evidence; partial feature coverage does not pass an entire epic. |
| R6 | Execution plan | Relevant phases/dependencies, repository-backed build/test/lint commands and prerequisites, time/status fields, checkpoint/commit/review tables. Record N/A with reasons. No unresolved required command placeholders. Include supported startup/configuration ownership and cold-start/repeat-start acceptance where applicable; test fixture setup is not user setup evidence. |

For applicable R2–R4 contracts, write or update `ImplementationContract.md` (or
link an existing authoritative design). Reconcile contradictory feature, task,
phase, acceptance, and manual-verification documents; an added appendix does
not silently override contradictory active requirements.

### Repair, then validate the final documents

1. Resolve technical omissions, document choices, and repair formatting or
   missing tracking templates within the existing scope.
2. Re-read the resulting documents and run every check above against the final
   plan, including the corresponding checks normally performed at start.
3. Save `readiness-validation.md` with date, gate version, repository revision
   and dirty-state observation, reviewed document paths/content hashes, all
   R1–R6 outcomes and evidence, the dependency table reference and stage-specific verdict, decisions/corrections, unresolved blockers, and
   final PASS/BLOCKED. Exclude the report itself from its input hashes. State
   explicitly which tests are only planned and which, if any, actually ran.
4. Only PASS permits a READY claim or progression to implementation. Otherwise
   retain the folder, mark current readiness BLOCKED in tracking, and report
   the concrete remaining blocker. Never erase prior rejection evidence.

`start-feature` reads this report and verifies the current documents, codebase,
and dependencies. It must not trust stale evidence or a READY folder name. If
the report is missing (including older features), generate it using this gate;
if inputs changed, revalidate affected checks and record the change. Do not
reject merely because a report is absent. Resolve routine omissions locally
and rerun the gate. An unavailable required prerequisite is a material blocker even when its design
is unambiguous. Stop dependent progression for that blocker; explain whether
it is new evidence, scope drift, or a gap missed in refinement. Never reject
solely because implementation still involves normal engineering judgment.
