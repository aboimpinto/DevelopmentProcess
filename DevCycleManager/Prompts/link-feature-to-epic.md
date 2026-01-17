# Link Feature to Epic - MCP Procedure

You are executing the **Link Feature to Epic** procedure for the DevCycleManager. This links an existing feature to an epic, establishing the parent-child relationship.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Epic ID**: {{epic_id}}
- **Feature Path** (optional): {{feature_path}}
- **Epic Path** (optional): {{epic_path}}

---

## Step 0: Locate Both Documents

### 0.1: Find the Feature

1. **If `feature_path` is provided:** Use it directly
2. **Otherwise:** Search in all feature state folders:
   - `MemoryBank/Features/01_SUBMITTED/`
   - `MemoryBank/Features/02_READY_TO_DEVELOP/`
   - `MemoryBank/Features/03_IN_PROGRESS/`
   - `MemoryBank/Features/04_COMPLETED/`

3. **Look for folder starting with `{{feature_id}}`**

4. **Read `FeatureDescription.md`**

**If feature not found:** Report error "Feature {{feature_id}} not found" and STOP.

### 0.2: Find the Epic

1. **If `epic_path` is provided:** Use it directly
2. **Otherwise:** Search in `MemoryBank/Features/00_EPICS/` for folder starting with `{{epic_id}}`

3. **Read `EpicDescription.md`**

**If epic not found:** Report error "Epic {{epic_id}} not found" and STOP.

---

## Step 1: Validate the Link

### 1.1: Check Feature's Current Epic

Read the feature's `Parent Epic` field:

**If already linked to an epic:**
- If same epic: Report "Feature {{feature_id}} is already linked to {{epic_id}}" and STOP
- If different epic: Ask user to confirm re-linking

```
Feature {{feature_id}} is currently linked to [EXISTING_EPIC_ID].

Do you want to:
1. Move to {{epic_id}} (will update both epics)
2. Cancel
```

### 1.2: Check Epic Status

- Epic must NOT be in CANCELLED status
- If CANCELLED: Report error and STOP

### 1.3: Check for Duplicates

- Verify the feature is not already in the epic's Features Breakdown table
- If duplicate found: Report and STOP

---

## Step 2: Extract Feature Information

From the feature's `FeatureDescription.md`, extract:

| Field | Source |
|-------|--------|
| Feature ID | Metadata table |
| Title | Document title (after "# Feature:") |
| Status | Convert state folder to status (e.g., 01_SUBMITTED → NOT_STARTED) |
| Summary | Summary section |
| Requirements | Requirements section (key items) |
| Dependencies | Dependencies subsection |
| Priority | Priority field |

**Status Mapping:**
- `01_SUBMITTED` → `NOT_STARTED`
- `02_READY_TO_DEVELOP` → `NOT_STARTED`
- `03_IN_PROGRESS` → `IN_PROGRESS`
- `04_COMPLETED` → `COMPLETED`

---

## Step 3: Update Feature Document

Edit the feature's `FeatureDescription.md`:

### 3.1: Update Parent Epic Field

Find the metadata table and update:

```markdown
| **Parent Epic** | {{epic_id}} |
```

### 3.2: Add Epic Context (If Not Present)

If not already present, add a section after the metadata:

```markdown
## Epic Context

This feature is part of **{{epic_id}}: [Epic Title]**.

**Epic Goal:** [One-line summary from epic's Executive Summary]
```

---

## Step 4: Update Epic Document

Edit the epic's `EpicDescription.md`:

### 4.1: Update Features Breakdown Table

Find `## Features Breakdown` and add a new row:

```markdown
| {{feature_id}} | [Feature Title] | [Status] | [Dependencies] | [Priority] |
```

**Placement:**
- Add in logical order based on dependencies
- If no dependencies, add at the end of same-priority features

### 4.2: Update Progress Tracking Table

Find `## Progress Tracking` and add a new row:

```markdown
| {{feature_id}} | [Status] | [Started Date or -] | [Completed Date or -] | Linked from existing feature |
```

**Update Overall Progress:**
- Recalculate: `**Overall Progress:** X/Y features complete (Z%)`

### 4.3: Add Feature Details Section

Find `## Feature Details` and add:

```markdown
### {{feature_id}}: [Feature Title]
**User Story:** [Convert Summary to user story format: "As a [user], I want [X] so that [Y]"]

**Scope:**
- [Key requirement 1]
- [Key requirement 2]
- [Key requirement 3]

**Dependencies:** [From feature's Dependencies, or "None"]

**Note:** Linked from existing feature. See full details in feature folder.
```

### 4.4: Update Dependency Flow Diagram

Find the Mermaid diagram and:

1. **Add a new node:**
   ```
   {{feature_id}}[{{feature_id}}: Feature Title]
   ```

2. **Add dependency arrows** (if feature has dependencies on other features in this epic)

3. **Add the status class:**
   ```
   class {{feature_id}} [notStarted|inProgress|completed]
   ```

---

## Step 5: Handle Previous Epic (If Re-linking)

**If the feature was previously linked to a different epic:**

1. **Read the previous epic's `EpicDescription.md`**

2. **Remove feature from:**
   - Features Breakdown table (remove the row)
   - Progress Tracking table (remove the row)
   - Feature Details section (remove the subsection)
   - Dependency Flow Diagram (remove node and update arrows)

3. **Update Overall Progress** in the previous epic

4. **Add note to previous epic:**
   ```markdown
   > **Note:** {{feature_id}} was moved to {{epic_id}} on [date]
   ```

---

## Step 6: Confirm Completion

Provide a summary:

```
Feature Linked to Epic Successfully

Feature: {{feature_id}} - [Feature Title]
Epic: {{epic_id}} - [Epic Title]

Updates Made:

Feature (FeatureDescription.md):
- Parent Epic field: Updated to {{epic_id}}
- Epic Context section: [Added/Already present]

Epic (EpicDescription.md):
- Features Breakdown: Added {{feature_id}}
- Progress Tracking: Added {{feature_id}} ([Status])
- Feature Details: Added section for {{feature_id}}
- Dependency Diagram: Added node [with/without] dependencies

[If re-linked]
Previous Epic ([PREVIOUS_EPIC_ID]):
- Removed {{feature_id}} from all sections
- Updated progress tracking

Epic Progress: X/Y features complete (Z%)

Next Steps:
1. Review the epic's dependency diagram for accuracy
2. Continue with feature development workflow
```

---

## Error Handling

- **Feature not found:** Report error with search locations tried
- **Epic not found:** Report error
- **Feature already in epic:** Report and STOP (no action needed)
- **Epic is CANCELLED:** Report error - cannot link to cancelled epic
- **Circular dependency:** If linking creates a circular dependency, warn user
- **Write failure:** Report which file failed and what was successfully updated

---

## Important Notes

1. **Bidirectional Update:** Both feature AND epic are updated to maintain consistency
2. **Re-linking Support:** Features can be moved between epics (previous epic is cleaned up)
3. **Status Preservation:** Feature's current status is reflected in epic's tracking
4. **Dependency Awareness:** Feature's dependencies are added to epic's diagram
