# Planning at the right level

The canonical rule is the [Shared Specification Level Policy](../DevCycleManager/Prompts/specification-level-policy.md),
version `devcycle-specification-levels/v1`. Maintain the normative text there.
DevCycle delivers it in planning, delivery and synchronization recipes, including
hosted Deep-Dive stages. Projects should reference it in AGENTS.md and add only
project-specific constraints.

The policy distinguishes an EPIC ready for feature decomposition from a FEAT
ready for implementation. Existing technical context remains authoritative;
adopting the policy does not authorize rewriting existing EPICs.

Examples for reviewing client output:

| Situation | Expected treatment |
| --- | --- |
| Reprocessing a retained source must reuse its results | EPIC business rule with workflow acceptance |
| Importing the same external document again creates a new source with fresh provider calls | EPIC behavior and source-identity boundary |
| Choosing the internal storage schema for recovery | Named design work for the owning FEAT unless already mandated |
| A shared source-identity contract changes acquisition dependencies | Resolve the shared boundary before finalizing decomposition |
| An existing EPIC records an approved execution design | Preserve it and carry its constraints/references into FEATs |
| A feature finishes its isolated tests | Update traceability; do not claim unrun integrated EPIC E2E tests passed |

Automated tests verify policy delivery, missing-policy failures, preservation of
host contracts and the explicit recipe boundaries. They do not evaluate a client
model's generated EPIC quality. Review actual future EPIC/FEAT output against the
examples above and the canonical rule before claiming that behavioral outcome.
