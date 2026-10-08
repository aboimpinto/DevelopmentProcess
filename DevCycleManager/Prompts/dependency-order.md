## Required Dependency Order

**Policy version: 1.** Apply this policy at the current workflow stage. It takes
precedence over generic phase order, optional-file rules, review exemptions, and
instructions to continue automatically. The client executes these checks; receipt
of this procedure is not evidence that a dependency has been satisfied.

### Non-negotiable rule

**Implement and verify the prerequisite before starting the task that depends
on it.** Never defer a required prerequisite to a later feature, phase, epic, or
follow-up while implementing its consumer. A feature ID, document, assigned
owner, open PR, or COMPLETED label alone does not establish availability.

A prerequisite is anything the intended behavior needs to build, start, run,
integrate, or be verified in a supported environment. Include code/contracts,
services, provisioning/startup commands, configuration, credentials availability,
schemas/migrations, shared data/storage and deployment wiring. Never record
credential values. Inspect related epics and actual code as well as declared
dependencies; a missing graph edge does not make a requirement optional.

Future enhancements are not prerequisites only when the current promised
behavior works and can be verified without them. Do not relabel a requirement
as optional, supply a production no-op, weaken acceptance, or use a test fixture
to hide a missing prerequisite.

### Record the dependency evidence

Keep one dependency table in the existing epic/feature plan and reference it
from readiness and implementation reports. Use one row per capability and
relevant environment (local development, CI, deployment); record justified N/A
for unsupported environments rather than expanding project scope.

| Required capability / environment | Provider feature or task | Consumer task | Status | Evidence and verification command |
|---|---|---|---|---|
| Concrete prerequisite | Owner and delivery location | First task requiring it | VERIFIED / PLANNED / BLOCKED | Actual revision/configuration, supported setup, dated result or explicitly pending verification |

VERIFIED means the needed implementation is present in the consumer's actual
working/integration revision and the applicable checks passed. For a runtime
service, distinguish implemented provisioning from current health; verify the
supported startup/configuration path and check health before dependent execution.
CI-provided services do not prove local startup. An external managed service may
satisfy a dependency through the agreed provisioning/configuration contract;
do not introduce local Docker as a universal requirement.

### Apply the gate at each stage

1. **Epic submission, deep-dive, feature creation and design:** discover and
   order prerequisites across epic boundaries, including transitive dependencies.
   Draw provider-to-consumer edges. Resolve cycles or future-provider inversions
   by splitting/reordering work under existing authority. Draft records may keep
   explicit BLOCKED dependencies; creating their IDs does not unblock execution.
2. **Refinement / READY:** every prerequisite must be VERIFIED, or a concrete
   PLANNED enabling task inside this feature, ordered before all its consumers
   with its own verification. An unavailable external/future-feature prerequisite
   blocks READY. Refine the plan while blocked, but do not move it to READY.
3. **Start:** recheck the table against the actual revision and environment.
   Same-feature PLANNED prerequisites permit starting their enabling tasks only;
   they do not authorize consumer implementation. A stale PASS is not evidence.
4. **Before each implementation task:** require VERIFIED prerequisites. If one
   is missing, pause the dependent task, implement and verify its authorized
   prerequisite first, update evidence, then resume. If outside current authority,
   report the specific blocker and required owner/action. Continue independent
   authorized work where possible. Never ask the user to repeat settled decisions.
5. **Review and phase acceptance:** verify dependency evidence for every task
   being accepted and inspect required-but-unchanged configuration, startup,
   migration, documentation and command-registration files. Runtime-affecting
   configuration requires review even in a config-only phase. A prerequisite
   cannot be SKIPPED merely to advance its consumer.
6. **Delivery / completion:** every prerequisite of delivered behavior must be
   VERIFIED. Where startup/provisioning changes, execute the supported user setup
   workflow in an isolated environment with task-owned services initially absent
   or stopped, then exercise the feature. Repeat setup to verify retained data
   and healthy-service reuse where promised. Use agreed provisioning for managed
   services; never stop/reset shared services. Record exact commands, revision,
   outcomes and any separate fixture setup. Green fixture-based tests alone
   cannot establish startup completeness. Missing required evidence blocks
   completion even when all phase checkboxes and unit tests pass.

### Required decisions in representative cases

- Consumer needs Redis; startup is assigned only to a future epic: BLOCKED.
  Move/split startup into a verified earlier delivery or the first enabling task
  of the current feature before implementing the consumer.
- Provider feature exists but its code/configuration is absent: BLOCKED; resolving
  its ID changes no implementation status.
- Same-feature startup task is fully specified but pending: the plan may be READY;
  execute and verify that task first. Consumer implementation remains blocked.
- Required provider is present and verified in the actual integration revision:
  proceed, retaining evidence and checking runtime readiness when needed.
- CI injects Redis but the promised local setup cannot start it: local delivery
  remains BLOCKED regardless of CI success.
