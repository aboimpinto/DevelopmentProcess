# Submit Feature - MCP Procedure

You are executing the **Submit Feature** procedure for the DevCycleManager. Follow these steps exactly to create a new feature in the `01_SUBMITTED` state.

## Input Provided
- **User Description**: {{description}}
- **Title** (optional): {{title}}
- **External ID** (optional): {{external_id}}
- **Parent Epic** (optional): {{epic_id}}

---

## Step 0: Gather Project Context (CRITICAL)

Before generating any content, you MUST read and understand the project context. This ensures the feature aligns with what is being built.

**Read these files/folders in order:**

1. **Project Overview** - `MemoryBank/Overview/`
   - Read ALL `.md` files in this folder
   - Understand: What is this project? What problem does it solve? What is the vision?

2. **Architecture** - `MemoryBank/Architecture/`
   - Read ALL `.md` files in this folder
   - Understand: What components exist? How do they interact? What patterns are used?

3. **Code Guidelines** - `MemoryBank/CodeGuidelines/`
   - Read ALL `.md` files in this folder
   - Understand: What standards must be followed? What technologies are used?

4. **Existing Features** - `MemoryBank/Features/`
   - List the folders in `02_READY_TO_DEVELOP/`, `03_IN_PROGRESS/`, and `04_COMPLETED/`
   - Skim the `FeatureDescription.md` of recent features to understand what's already planned or built

**If any of these folders are empty or don't exist:** Note this in the feature description under "Technical Considerations" as the project may be in early stages.

**Use this context to:**
- Understand where this feature fits in the overall system
- Identify which existing components it might interact with
- Ensure the feature aligns with established patterns and guidelines
- Avoid proposing something that duplicates existing functionality

---

## Step 0.5: Validate Parent Epic (If Provided)

**If a Parent Epic ID was provided:**

1. Search for the epic folder in `MemoryBank/Features/00_EPICS/`
   - Look for a folder starting with the epic ID (e.g., `EPIC-001-*`)

2. **If the epic folder EXISTS:**
   - Read the `EpicDescription.md` file
   - Verify the epic is not in CANCELLED status
   - Note the epic's strategic goal to ensure this feature aligns
   - This feature will be listed in the epic's Features Breakdown table

3. **If the epic folder DOES NOT EXIST:**
   - Report an error: "Parent epic {epic_id} not found. Please create the epic first using submit-epic or remove the epic_id parameter."
   - STOP the procedure - do not create the feature

**If NO Parent Epic was provided:** Continue to Step 1 (standalone feature).

---

## Step 1: Manage Feature ID Counter

First, check if `MemoryBank/Features/NEXT_FEATURE_ID.txt` exists.

**If it does NOT exist:**
1. Create the file `MemoryBank/Features/NEXT_FEATURE_ID.txt`
2. Write the number `1` to it
3. Use `1` as the current feature ID

**If it EXISTS:**
1. Read the current number from the file
2. Use that number as the current feature ID
3. Increment the number by 1
4. Write the new number back to the file

Format the Feature ID as: `FEAT-XXX` (zero-padded to 3 digits)
- Example: `1` becomes `FEAT-001`, `42` becomes `FEAT-042`

---

## Step 2: Generate Feature Title

**If a title was provided:** Use it as-is.

**If NO title was provided:** Generate a concise title (4-6 words) that captures the essence of the feature description.

Requirements for the title:
- Clear and descriptive
- Action-oriented (starts with verb when possible)
- No special characters

---

## Step 3: Create Folder Name

Create a slug from the title:
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters (keep only a-z, 0-9, hyphens)
4. Limit to 50 characters

Folder name format: `FEAT-XXX-slug`
- Example: `FEAT-001-user-authentication-module`

If an external ID was provided, include it: `FEAT-XXX-EXT-YYY-slug`
- Example: `FEAT-001-EXT-12345-user-authentication-module`

---

## Step 4: Generate Feature Description Document

Create `FeatureDescription.md` with the following structure:

```markdown
# Feature: [Generated or Provided Title]

| Field | Value |
|-------|-------|
| **Feature ID** | FEAT-XXX |
| **Parent Epic** | [Epic ID if provided, otherwise "N/A - Standalone Feature"] |
| **External Reference** | [External ID if provided, otherwise "N/A"] |
| **Date Submitted** | [Today's date: YYYY-MM-DD] |
| **Status** | 01_SUBMITTED |

## Summary
[Write 2-3 sentences summarizing what this feature will accomplish based on the user's description]

## Problem Statement
[Expand on the problem this feature is intended to solve. Why is this needed? What pain point does it address?]

## Proposed Solution
[Provide a high-level overview of how this feature will solve the problem. Keep it conceptual, not implementation details]

## Requirements
- [ ] [Requirement 1 - derived from the description]
- [ ] [Requirement 2 - derived from the description]
- [ ] [Requirement 3 - derived from the description]
[Add more requirements as needed]

## Acceptance Criteria
- [ ] [Criterion 1 - how do we know this feature is complete?]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Out of Scope
- [What this feature explicitly will NOT include]
- [Boundaries and limitations]

## Integration Context
Based on the project's current state (from Step 0):

### Affected Components
[List which existing components/modules this feature will touch or extend. Use "None - new component" if it's entirely new]

### Dependencies
[List any existing features or components this feature depends on. Use "None" if standalone]

### Related Features
[Reference any features in 02_READY_TO_DEVELOP, 03_IN_PROGRESS, or 04_COMPLETED that relate to this one]

## Technical Considerations
[Any technical notes, constraints, or considerations for implementation based on the project's architecture and guidelines. Leave as "To be defined during design phase" if unknown]

## Priority
[Suggest: High / Medium / Low - based on the urgency implied in the description]

## Estimated Complexity
[Suggest: Small / Medium / Large - based on the scope of the requirements]
```

---

## Step 5: Create the Files

Execute these actions in order:

1. **Create the feature folder:**
   ```
   MemoryBank/Features/01_SUBMITTED/[folder-name]/
   ```

2. **Write the FeatureDescription.md file:**
   ```
   MemoryBank/Features/01_SUBMITTED/[folder-name]/FeatureDescription.md
   ```

3. **Update NEXT_FEATURE_ID.txt** (if not already done in Step 1)

---

## Step 5.5: Update Parent Epic (If Linked)

**If this feature is linked to an epic (`epic_id` was provided):**

You MUST update the epic's `EpicDescription.md` to maintain the Epic-Feature relationship.

### 5.5.1: Update Features Breakdown Table

Find the `## Features Breakdown` section and update the table:

**If there's a TBD row that matches this feature's description:**
- Replace the TBD row with the actual feature data

**If no matching TBD row exists:**
- Add a new row to the table

Table row format:
```markdown
| FEAT-XXX | [Feature Title] | NOT_STARTED | [Dependencies or "None"] | [P1/P2/P3] |
```

### 5.5.2: Update Progress Tracking Table

Find the `## Progress Tracking` section and update:

**If there's a TBD row:**
- Replace it with the actual feature data

**If no TBD row exists:**
- Add a new row

Table row format:
```markdown
| FEAT-XXX | NOT_STARTED | - | - | [Notes if any] |
```

Also update the **Overall Progress** line:
- Count total features and completed features
- Update: `**Overall Progress:** X/Y features complete (Z%)`

### 5.5.3: Update Feature Details Section

Find the `## Feature Details` section:

**If there's a placeholder section for this feature:**
- Replace the placeholder title with: `### FEAT-XXX: [Feature Title]`
- Update the User Story, Scope, and Dependencies based on the FeatureDescription.md

**If no placeholder exists:**
- Add a new feature details subsection:

```markdown
### FEAT-XXX: [Feature Title]
**User Story:** [From FeatureDescription.md Summary - convert to "As a [user], I want [X] so that [Y]" format]

**Scope:**
- [Key items from Requirements]

**Dependencies:** [From FeatureDescription.md Dependencies, or "None"]
```

### 5.5.4: Update Dependency Flow Diagram (If Applicable)

Find the Mermaid diagram in `## Dependency Flow Diagram`:

**If there are placeholder nodes (F1, F2, etc.):**
- Replace with actual FEAT-XXX identifiers
- Update node labels with feature titles

**If adding a new feature:**
- Add a new node: `FEAT-XXX[FEAT-XXX: Feature Title]`
- Add dependency arrows if this feature depends on others
- Update the class assignment: `class FEAT-XXX notStarted`

---

## Step 6: Confirm Submission

After completing all steps, provide a summary:

```
Feature Submitted Successfully

- Feature ID: FEAT-XXX
- Title: [Feature Title]
- Parent Epic: [Epic ID or "None - Standalone Feature"]
- External Reference: [ID or "None"]
- Location: MemoryBank/Features/01_SUBMITTED/[folder-name]/
- Files Created/Updated:
  - FeatureDescription.md (created)
  - NEXT_FEATURE_ID.txt updated to [next number]
  - [If linked to epic] EpicDescription.md updated:
    - Features Breakdown table: Added FEAT-XXX
    - Progress Tracking table: Added FEAT-XXX
    - Feature Details section: Added/updated
    - Dependency Flow Diagram: Updated (if applicable)

Next Steps:
1. Review the feature and run `deep-dive` to gather more details if needed
2. Move to design-feature when ready for UX research and wireframes
```

---

## Error Handling

- **If the feature folder already exists:** Report the conflict and do NOT overwrite. Suggest using a different title or checking for duplicates.
- **If unable to write files:** Report the specific error and which step failed.
- **If the description is too vague:** Generate the feature anyway but add a note in the Summary section: "⚠️ Original description was brief. Please expand the requirements before moving to development."
