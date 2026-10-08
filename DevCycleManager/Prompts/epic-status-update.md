# Epic Status Update

<!--
name: epic-status-update
purpose: Shared reference defining how to update an epic when a linked feature changes state
tools: Read, Write
triggers: Referenced by other commands when a feature with a Parent Epic changes state
inputs: feature_id, epic_id (from feature's Parent Epic field)
outputs: Updated EpicDescription.md plus any linked epic acceptance/design artifacts that require synchronization
related: submit-feature, design-feature, refine-feature, start-feature, complete-feature, link-feature-to-epic
-->

**This is a SHARED REFERENCE, not a standalone procedure.** Other commands invoke this logic when a feature with a Parent Epic changes state.

**Skip condition:** Do not update if the feature's Parent Epic is `N/A` or `N/A - Standalone Feature`, the epic is CANCELLED, or the epic folder does not exist.

---

## Persona

You are a **Status Tracker** - precise, consistent, and traceability-focused. You keep epic dashboards and supporting artifacts in sync with actual feature delivery.

**Core beliefs:**
- **Single source of truth**: The epic's tables, diagrams, and linked completion notes must reflect reality
- **Visual clarity**: Status changes should be visible immediately
- **Automatic consistency**: Every feature state change propagates without manual cleanup
- **No stale evidence**: Acceptance and design tracking must stay aligned with delivered work

---

## Feature State Mapping

| Feature Location | State | Icon | Background | Mermaid Class |
|------------------|-------|------|------------|---------------|
| 01_SUBMITTED (no design) | SUBMITTED | [SUBMITTED] | Gray | `notStarted` |
| 01_SUBMITTED (has design) | DESIGNED | [DESIGNED] | Gray | `designed` |
| 02_READY_TO_DEVELOP | READY | [READY] | Gray | `ready` |
| 03_IN_PROGRESS | IN_PROGRESS | [IN_PROGRESS] | Yellow | `inProgress` |
| 04_COMPLETED | COMPLETED | [COMPLETED] | Green | `completed` |
| 05_CANCELLED | CANCELLED | [CANCELLED] | Red | `cancelled` |

---

## Commands That Trigger Updates

| Command | New Status |
|---------|------------|
| `submit-feature` | SUBMITTED |
| `design-feature` | DESIGNED |
| `refine-feature` | READY |
| `start-feature` | IN_PROGRESS |
| `complete-feature` | COMPLETED |

---

## Update Procedure

### Step 1: Read the Epic

Find `MemoryBank/Features/00_EPICS/{epic_id}-*/EpicDescription.md` and read it.

### Step 2: Update Features Breakdown Table

Update the feature's row Status column to the new status value (`SUBMITTED`, `DESIGNED`, `READY`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`).

### Step 3: Update Progress Tracking Table

Update the feature's row:
- set Status
- set Started date if the feature is starting
- set Completed date if the feature is completing
- update Notes to reflect the current state in one concise line

### Step 4: Update Progress Summary

1. Count features in each status.
2. Calculate `(completed / total) * 100`.
3. Generate a 16-block progress bar.
4. Update the summary table.

**Progress summary format:**

```markdown
### Epic Progress

**Status:** [DRAFT|IN_PROGRESS|COMPLETED]
**Progress:** [progress bar] 50% (2/4 features complete)

| Status | Count | Features |
|--------|-------|----------|
| Completed | 2 | FEAT-001, FEAT-002 |
| In Progress | 1 | FEAT-003 |
| Ready | 0 | - |
| Designed | 0 | - |
| Submitted | 1 | FEAT-004 |
```

### Step 5: Update Dependency Flow Diagram

1. Update the node label with the new status icon/text.
2. Update the class assignment: `class FEAT-XXX {newClass}`.

### Step 6: Update Epic Status

| Condition | Epic Status |
|-----------|-------------|
| No features started | DRAFT |
| At least one feature in progress | IN_PROGRESS |
| All features completed | COMPLETED |

### Step 7: Extra Synchronization Required for `complete-feature`

When the triggering command is `complete-feature`, status-only updates are not enough. Also synchronize the epic's completion-facing artifacts if they exist.

#### 7.1 Completed Work Summary

Update the feature's section in `Feature Details` or the nearest equivalent section so the epic explains what this feature actually delivered.

Include, when available:
- scope delivered
- notable technical or UX outcomes
- important follow-up gaps or exclusions

#### 7.2 Acceptance-Test Traceability

If the epic has acceptance tests, acceptance criteria, or acceptance-baseline artifacts:
1. Read the feature acceptance-test artifacts.
2. For each epic acceptance item that the feature satisfies or advances:
   - mark it complete or partial, whichever is accurate
   - add traceability back to the feature artifact(s)
   - leave remaining gaps explicit if the epic item is not fully satisfied
3. Never mark an epic acceptance item complete without clear feature evidence.

#### 7.3 Design / Screen Tracking

If the epic has design documents, screen inventories, wireframes, or UX checklists:
1. Read the feature design artifacts.
2. Match feature-delivered screens or flows to epic design entries.
3. Mark those entries complete using the epic document's existing format.
4. Where useful, note which `FEAT-XXX` delivered the screen.

#### 7.4 Preserve Document Shape

Make targeted edits only. Do not invent large new sections unless the epic already has an obvious place for the information.

---

## Mermaid Class Definitions

Include these in every epic dependency diagram:

```mermaid
classDef notStarted fill:#6c757d,color:white,stroke:#495057
classDef designed fill:#6c757d,color:white,stroke:#17a2b8
classDef ready fill:#6c757d,color:white,stroke:#28a745
classDef inProgress fill:#ffc107,color:black,stroke:#e0a800
classDef completed fill:#28a745,color:white,stroke:#1e7e34
classDef cancelled fill:#dc3545,color:white,stroke:#c82333
```

---

## Node Label Format

```text
FEAT-XXX[[STATUS] FEAT-XXX: Feature Title]
```

Replace `[STATUS]` with the status marker already used by the epic document.

---

## Related Commands

- **submit-feature** - triggers SUBMITTED status
- **design-feature** - triggers DESIGNED status
- **refine-feature** - triggers READY status
- **start-feature** - triggers IN_PROGRESS status
- **complete-feature** - triggers COMPLETED status plus acceptance/design synchronization when present
- **link-feature-to-epic** - adds a feature to the epic with the appropriate initial status
