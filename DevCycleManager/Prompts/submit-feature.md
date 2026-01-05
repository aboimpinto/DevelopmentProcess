# Submit Feature - MCP Procedure

You are executing the **Submit Feature** procedure for the DevCycleManager. Follow these steps exactly to create a new feature in the `01_SUBMITTED` state.

## Input Provided
- **User Description**: {{description}}
- **Title** (optional): {{title}}
- **External ID** (optional): {{external_id}}

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

## Step 6: Confirm Submission

After completing all steps, provide a summary:

```
✅ Feature Submitted Successfully

- Feature ID: FEAT-XXX
- Title: [Feature Title]
- External Reference: [ID or "None"]
- Location: MemoryBank/Features/01_SUBMITTED/[folder-name]/
- Files Created:
  - FeatureDescription.md
  - NEXT_FEATURE_ID.txt updated to [next number]

📋 Next Step: Review the feature and move to 02_READY_TO_DEVELOP when ready for design and planning.
```

---

## Error Handling

- **If the feature folder already exists:** Report the conflict and do NOT overwrite. Suggest using a different title or checking for duplicates.
- **If unable to write files:** Report the specific error and which step failed.
- **If the description is too vague:** Generate the feature anyway but add a note in the Summary section: "⚠️ Original description was brief. Please expand the requirements before moving to development."
