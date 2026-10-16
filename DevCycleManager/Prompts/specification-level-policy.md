# Shared Specification Level Policy

Policy version: `devcycle-specification-levels/v1`.

Apply this policy when authoring, interviewing, decomposing, refining or updating
planning records. It defines the level of detail; it grants no extra mutation
authority, tools, approvals or changes to a host's output schema. In a hosted
interview, use only the supplied snapshot and saved decisions.

## EPIC: intent and decomposition readiness

An EPIC explains the problem, users, desired outcomes, observable workflow,
business rules, scope/exclusions, measurable success and relevant failure
outcomes. Its feature outline assigns bounded outcomes, acceptance ownership,
real prerequisites and cross-feature dependencies. Each feature must be
independently verifiable at its boundary; prerequisites do not make it invalid.
Avoid component-only slices without a demonstrable contract or outcome, catch-all
operations/testing features, and duplicated responsibility. A shared contract
feature is legitimate when its deliverable, consumers and validation are clear.

An EPIC is ready for decomposition when these boundaries are clear enough to
create meaningful features. It need not settle internal APIs, storage schemas,
algorithms, provider adapters, retry implementation or task-level test mechanics.
Include such details when already approved or necessary to state a genuine shared
constraint; explain why and retain the source decision. Do not invent technical
requirements merely to fill a template. Observable behavior and a mandated
integration/security/compatibility boundary can be EPIC requirements even when
technical in subject matter.

Distinguish unresolved EPIC intent from planned FEAT design work. Unclear product
behavior or a shared contract that changes feature boundaries must be resolved
at EPIC level. A bounded implementation choice may remain open: record the named
owning feature (a proposed name is enough), question, known constraints and the
milestone before which it must be resolved. This is planned refinement, not a
future human approval gate. Do not declare a new FEAT submitted before its record
exists or manufacture identifiers for proposed slices.

## FEAT and phases: design and implementation readiness

Carry parent intent, stable criterion IDs, business rules, approved constraints,
decision rationale and source links into the feature. Resolve assigned design
work during feature refinement and before dependent implementation. Specify the
owned contracts, relevant data/lifecycle/error behavior, dependencies, technical
approach and independently executable acceptance needed for the actual scope.
Phases/tasks make that design actionable and supply concrete validation evidence.
Do not require every EPIC to supply a full design, or infer missing product
requirements. Use repository evidence and explicitly delegated engineering
judgment within recorded constraints; ask about remaining product ambiguities.
Required implementation decisions cannot be replaced with later owner attestation
or human sign-off tasks. New shared-boundary conflicts require explicit
reconciliation within authorized scope, never a silent change to parent intent.

## Preserve context through updates

Keep approved decisions distinct from assumptions and proposals. Preserve stable
IDs, rationale, references, dependencies and EPIC -> FEAT -> Phase -> Task links.
The Acceptance Responsibility Policy still governs many-to-many coverage: feature
checks prove their boundary; EPIC acceptance requires its complete workflow E2E
evidence. Planning/interview completion does not certify delivery or acceptance.

For new technical detail, prefer the owning FEAT/phase or an existing linked design
record; summarize only the outcome or changed shared constraint in the EPIC.
Do not duplicate implementation plans during status reconciliation or GitHub
synchronization. Existing rich EPICs remain valid: do not delete, relocate or
automatically simplify their technical sections. Any later authorized migration
must preserve decision context and repair all references and criterion mappings.
Single-target interviews may only edit their target; report linked conflicts for
the appropriate lifecycle action rather than editing sibling documents.
