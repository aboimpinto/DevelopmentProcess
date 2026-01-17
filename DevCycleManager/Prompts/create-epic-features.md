# Create Epic Features - MCP Procedure

You are executing the **Create Epic Features** procedure for the DevCycleManager. This batch-creates all features defined in an epic's Features Breakdown table.

## Input Provided
- **Epic ID**: {{epic_id}}
- **Epic Path** (optional): {{epic_path}}

---

## Step 0: Locate and Read the Epic

1. **Find the epic folder:**
   - If `epic_path` is provided, use it directly
   - Otherwise, search in `MemoryBank/Features/00_EPICS/` for a folder starting with `{{epic_id}}`

2. **Read the EpicDescription.md file**

3. **Validate epic status:**
   - Epic must NOT be in CANCELLED status
   - If CANCELLED, report error and STOP

**If epic not found:** Report error "Epic {{epic_id}} not found" and STOP.

---

## Step 1: Parse Features Breakdown Table

Find the `## Features Breakdown` section and parse the table.

**Identify features to create:**
- Features with `TBD` in the Feature ID column need to be created
- Features that already have a `FEAT-XXX` ID are already created (skip these)

**Extract from each TBD row:**
- Title (from Title column)
- Dependencies (from Dependencies column)
- Priority (from Priority column)

**Example table:**
```markdown
| Feature ID | Title | Status | Dependencies | Priority |
|------------|-------|--------|--------------|----------|
| TBD | Dashboard Foundation | NOT_STARTED | None | P1 |
| TBD | Data Visualization | NOT_STARTED | Dashboard Foundation | P1 |
| FEAT-001 | Report Export | NOT_STARTED | Dashboard Foundation | P2 |
```

In this example:
- "Dashboard Foundation" and "Data Visualization" need to be created (TBD)
- "Report Export" already exists as FEAT-001 (skip)

---

## Step 2: Review Feature Details Section

For each TBD feature, find its corresponding section in `## Feature Details`:

**Extract additional information:**
- User Story
- Scope (what's included/excluded)
- Any additional context

This information will be used to create a rich feature description.

---

## Step 3: Confirm Features to Create

Before creating features, present a summary to the user:

```
Features to Create from {{epic_id}}

Epic: [Epic Title]
Features Found: [X] total, [Y] to create, [Z] already exist

Features to Create:
1. [Title 1] - Priority: P1, Dependencies: None
2. [Title 2] - Priority: P1, Dependencies: [Title 1]
3. [Title 3] - Priority: P2, Dependencies: [Title 1]

Already Created (will skip):
- FEAT-XXX: [Title]

Proceed with creating [Y] features?
```

**Use `AskUserQuestion` to confirm:**
- Option 1: "Yes, create all features"
- Option 2: "Let me select which features to create"
- Option 3: "Cancel"

**If user selects Option 2:**
- Present each feature and ask if it should be created
- Track which features to create

**If user selects Cancel:** STOP the procedure.

---

## Step 4: Create Features in Dependency Order

**IMPORTANT:** Create features in the correct order based on dependencies.

### 4.1: Build Dependency Graph

1. Identify features with no dependencies (can be created first)
2. For features with dependencies, ensure the dependency is created first
3. If a dependency refers to an already-created feature (FEAT-XXX), it's satisfied

### 4.2: Create Each Feature

For each feature to create (in dependency order):

1. **Compose the feature description** from:
   - User Story from Feature Details section
   - Scope items
   - Epic context (Problem Statement, Success Criteria)

2. **Call `submit-feature` MCP command** with:
   - `description`: Composed description
   - `title`: Feature title from table
   - `epic_id`: {{epic_id}}

3. **Track the created feature:**
   - Note the assigned FEAT-XXX ID
   - Map the title to the ID for dependency resolution

4. **Wait for completion** before creating dependent features

### 4.3: Handle Dependencies

When creating a feature with dependencies:
- Look up the FEAT-XXX ID of the dependency (created in this session or pre-existing)
- Include in the feature's Dependencies field

---

## Step 5: Update Epic with Dependency Mappings

After all features are created, verify the epic was updated:

1. **Re-read EpicDescription.md**

2. **Verify Features Breakdown table:**
   - All TBD entries should now have FEAT-XXX IDs
   - Dependencies should reference actual FEAT-XXX IDs

3. **Verify Dependency Flow Diagram:**
   - All placeholder nodes should be replaced with FEAT-XXX
   - Arrows should reflect actual dependencies

4. **Verify Progress Tracking:**
   - All features should be listed
   - Overall Progress should be accurate

**If any updates are missing:** Apply them now.

---

## Step 6: Confirm Completion

Provide a summary:

```
Epic Features Created Successfully

Epic: {{epic_id}} - [Epic Title]

Features Created: [X]
| Feature ID | Title | Dependencies |
|------------|-------|--------------|
| FEAT-XXX | [Title 1] | None |
| FEAT-YYY | [Title 2] | FEAT-XXX |
| FEAT-ZZZ | [Title 3] | FEAT-XXX |

Features Skipped (already existed): [Y]
| Feature ID | Title |
|------------|-------|
| FEAT-AAA | [Title] |

Epic Updated:
- Features Breakdown table: [X] features added
- Progress Tracking: Updated (0/[total] complete)
- Dependency Flow Diagram: Updated with FEAT-XXX nodes

Next Steps:
1. Run `deep-dive` on individual features to add more detail
2. Start with `design-feature` for each feature
3. Use `continue-implementation` once features are refined and started
```

---

## Error Handling

- **If epic not found:** Report error and STOP
- **If no TBD features found:** Report "All features in this epic have already been created" and STOP
- **If circular dependency detected:** Report the cycle and ask user to resolve in EpicDescription.md
- **If submit-feature fails:** Report error, note which features were created, and STOP
- **If user cancels:** Report which features (if any) were created before cancellation

---

## Important Notes

1. **Dependency Order Matters:** Always create features in dependency order to ensure proper linking
2. **Atomic Updates:** Each feature creation includes updating the epic
3. **Resume-Safe:** If interrupted, already-created features will have FEAT-XXX IDs and will be skipped on retry
4. **User Confirmation:** Always confirm before batch-creating to prevent unintended feature creation
