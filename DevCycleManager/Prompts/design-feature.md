# Design Feature - MCP Procedure

You are executing the **Design Feature** procedure for the DevCycleManager. This procedure creates comprehensive UX documentation for a feature through three sequential phases.

## Input Provided
- **Feature ID**: {{feature_id}}
- **Feature Path** (if provided): {{feature_path}}

---

## Phase Overview

This procedure generates three documents in sequence:
1. **UX-research-report.md** - User research, personas, and workflows
2. **Wireframes-design.md** - Visual specifications and component layouts
3. **design-summary.md** - Consolidated design documentation

**IMPORTANT**: Complete each phase fully before moving to the next. Each phase builds on the previous one.

---

## Step 0: Locate and Analyze the Feature

### Find the Feature
Search for the feature folder in `MemoryBank/Features/`:
1. First check `01_SUBMITTED/` for `{{feature_id}}*` folders
2. If not found, check `02_READY_TO_DEVELOP/`
3. If not found, check `03_IN_PROGRESS/`

**If the feature is not found:** Stop and report: "Feature {{feature_id}} not found in any state folder."

### Read Feature Context
Once found, read these files:
1. **FeatureDescription.md** in the feature folder - This is your primary input
2. **MemoryBank/Overview/** - Project vision and goals
3. **MemoryBank/Architecture/** - Existing components and patterns
4. **MemoryBank/CodeGuidelines/** - Standards and technologies

### Check for Backend-Only Features
Look for indicators in FeatureDescription.md:
- Keywords: "backend", "API only", "no UI", "service", "data processing"
- If the feature is explicitly backend-only: Skip to the **Backend Feature Shortcut** section at the end

### Look for Existing Design Assets
Search the feature folder and `MemoryBank/` for:
- Screenshots (*.png, *.jpg, *.jpeg)
- Mockups or wireframes
- UI specifications
- Application wireframe maps
- Design guidelines documents

**Note what you find** - these will inform the design process.

---

## PHASE 1: UX Research Report

### Purpose
Understand the users, their needs, and how they will interact with this feature.

### Research Steps

1. **Identify User Personas**
   - Who will use this feature?
   - What is their experience level?
   - What are their goals and pain points?
   - What context are they in when using this feature?

2. **Map User Journeys**
   - How do users discover this feature?
   - What triggers them to use it?
   - What steps do they take?
   - What decisions do they make along the way?
   - How do they know they succeeded?

3. **Analyze Information Architecture**
   - Where does this feature fit in the application structure?
   - How is it accessed (navigation, shortcuts, links)?
   - What information needs to be displayed?
   - What is the hierarchy of importance?

4. **Define Interaction Patterns**
   - How do users enter the feature? (button, menu, link, etc.)
   - How do users exit? (save, cancel, close, back)
   - What confirmation or feedback is needed?
   - What errors might occur and how to handle them?

5. **Consider Accessibility**
   - Keyboard navigation requirements
   - Screen reader compatibility
   - Color contrast and visual accessibility
   - Touch/mobile considerations (if applicable)

### Create: UX-research-report.md

Save to the feature folder with this structure:

```markdown
# UX Research Report: [Feature Title]

**Feature ID**: {{feature_id}}
**Date**: [Today's date]
**Status**: Design Phase

## Executive Summary
[2-3 sentences summarizing the key findings and recommendations]

## User Personas

### Primary Persona: [Name]
- **Role**: [Job title or user type]
- **Experience**: [Novice/Intermediate/Expert]
- **Goals**: [What they want to achieve]
- **Pain Points**: [Current frustrations]
- **Context**: [When/where they use the app]

### Secondary Persona: [Name]
[Same structure as above]

## User Journey Map

### Entry Points
- [How users discover/access this feature]

### Core Flow
1. [Step 1]: User action → System response
2. [Step 2]: User action → System response
3. [Step 3]: User action → System response

### Exit Points
- **Success Path**: [How users complete the task]
- **Cancel/Abort**: [How users exit without completing]
- **Error Recovery**: [How users recover from errors]

## Information Architecture

### Navigation Location
[Where this feature lives in the app structure]

### Information Hierarchy
1. **Primary** (always visible): [Most important elements]
2. **Secondary** (visible on demand): [Supporting information]
3. **Tertiary** (available but hidden): [Advanced options]

## Interaction Patterns

### Input Methods
- [Mouse/Touch interactions]
- [Keyboard shortcuts]
- [Voice/accessibility inputs]

### Feedback & Confirmation
- [Loading states]
- [Success indicators]
- [Error messages]

### Decision Points
| Decision | Options | Default | Impact |
|----------|---------|---------|--------|
| [Decision 1] | [A, B, C] | [Default] | [What happens] |

## Accessibility Requirements
- [ ] Keyboard navigation: [Specific requirements]
- [ ] Screen reader: [Specific requirements]
- [ ] Color/contrast: [Specific requirements]
- [ ] Motor accessibility: [Specific requirements]

## Research Sources
- [List any existing documentation, mockups, or user feedback used]

## Open Questions
- [Questions that need stakeholder input]
```

**CHECKPOINT**: Confirm UX-research-report.md is saved before proceeding to Phase 2.

---

## PHASE 2: Wireframes Design

### Purpose
Translate the UX research into visual specifications and component layouts.

### Read First
Before creating wireframes, read:
1. The UX-research-report.md you just created
2. Any existing design system or component library documentation in `MemoryBank/`
3. Screenshots or mockups found in Step 0

### Design Steps

1. **Define Screen/View Structure**
   - How many screens/views does this feature need?
   - What is the layout for each?
   - How do screens connect/flow?

2. **Create ASCII Wireframes**
   - Use ASCII art to show component layouts
   - Show different states (empty, loading, populated, error)
   - Indicate interactive elements

3. **Specify Components**
   - List the UI components needed
   - Define their properties and behaviors
   - Note any custom components required

4. **Map Navigation Flow**
   - Show how users move between screens
   - Indicate back/forward navigation
   - Show modal/dialog relationships

5. **Define Responsive Behavior** (if applicable)
   - How does the layout adapt to different sizes?
   - What elements hide/show at breakpoints?

### Create: Wireframes-design.md

Save to the feature folder with this structure:

```markdown
# Wireframes Design: [Feature Title]

**Feature ID**: {{feature_id}}
**Date**: [Today's date]
**Based on**: UX-research-report.md

## Screen Inventory

| Screen | Purpose | Entry Point | Exit Points |
|--------|---------|-------------|-------------|
| [Screen 1] | [Purpose] | [How accessed] | [Where it leads] |

## Wireframes

### Screen 1: [Name]

**Purpose**: [What this screen does]
**State**: [Default / Empty / Loading / Error]

```
┌─────────────────────────────────────────────┐
│  [Header / Title Bar]                    [X]│
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │     [Main Content Area]             │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Action Button 1]    [Action Button 2]     │
└─────────────────────────────────────────────┘
```

**Component Specifications**:
| Element | Component Type | Properties | Behavior |
|---------|---------------|------------|----------|
| [Header] | [Type] | [Props] | [Behavior] |

**State Variations**:
- **Empty State**: [Description or mini-wireframe]
- **Loading State**: [Description or mini-wireframe]
- **Error State**: [Description or mini-wireframe]

### Screen 2: [Name]
[Same structure as Screen 1]

## Navigation Flow

```
[Entry Point]
      │
      ▼
┌─────────────┐     ┌─────────────┐
│  Screen 1   │────▶│  Screen 2   │
└─────────────┘     └─────────────┘
      │                   │
      ▼                   ▼
  [Cancel]           [Complete]
```

## Component Library

### Components Used
| Component | Usage | Notes |
|-----------|-------|-------|
| [Button] | [Where used] | [Variations needed] |
| [Input Field] | [Where used] | [Validation rules] |

### Custom Components Needed
| Component | Purpose | Specification |
|-----------|---------|---------------|
| [Custom 1] | [Why needed] | [Basic spec] |

## Interaction Specifications

### Keyboard Navigation
| Key | Action | Context |
|-----|--------|---------|
| Tab | Move to next element | All screens |
| Enter | Confirm/Submit | Forms, dialogs |
| Escape | Cancel/Close | Dialogs, modals |

### Micro-interactions
| Trigger | Animation | Duration |
|---------|-----------|----------|
| [Button hover] | [Effect] | [Time] |

## Responsive Considerations
[If applicable - breakpoints, layout changes, etc.]

## Design Tokens
[Colors, spacing, typography used - reference design system if available]
```

**CHECKPOINT**: Confirm Wireframes-design.md is saved before proceeding to Phase 3.

---

## PHASE 3: Design Summary

### Purpose
Consolidate the UX research and wireframes into an actionable design document.

### Read First
1. FeatureDescription.md
2. UX-research-report.md
3. Wireframes-design.md

### Create: design-summary.md

Save to the feature folder with this structure:

```markdown
# Design Summary: [Feature Title]

**Feature ID**: {{feature_id}}
**Date**: [Today's date]
**Status**: Ready for Implementation

## Overview
[1-2 paragraphs summarizing what this feature does and why it matters]

## Design Decisions

### Key UX Decisions
| Decision | Choice Made | Rationale |
|----------|-------------|-----------|
| [Navigation pattern] | [Choice] | [Why] |
| [Layout approach] | [Choice] | [Why] |
| [Interaction model] | [Choice] | [Why] |

### Trade-offs Accepted
- [Trade-off 1]: [What we gained vs. what we gave up]
- [Trade-off 2]: [What we gained vs. what we gave up]

## Implementation Checklist

### Screens to Build
- [ ] [Screen 1]: [Brief description]
- [ ] [Screen 2]: [Brief description]

### Components to Create/Modify
- [ ] [Component 1]: [New/Modify] - [Notes]
- [ ] [Component 2]: [New/Modify] - [Notes]

### Data Requirements
- [ ] [Data source 1]: [What's needed]
- [ ] [Data source 2]: [What's needed]

## Design Files
- [UX Research Report](./UX-research-report.md)
- [Wireframes & Specifications](./Wireframes-design.md)

## User Testing Recommendations
1. [Test scenario 1]: [What to validate]
2. [Test scenario 2]: [What to validate]

## Open Items
- [ ] [Item needing stakeholder decision]
- [ ] [Item needing technical validation]

## Next Steps
1. Review designs with stakeholders
2. Create development tasks based on implementation checklist
3. Build UI components
4. Integrate with backend services
5. Conduct user testing
```

---

## Step Final: Confirm Completion

After all three documents are created, provide this summary:

```
✅ Design Documentation Generated for {{feature_id}}

📁 Feature folder: [path to feature folder]

📄 Documents created:
   • UX-research-report.md - User research and personas
   • Wireframes-design.md - Visual specifications
   • design-summary.md - Consolidated design documentation

📋 Next Steps:
   1. Review the design documents with stakeholders
   2. Address any open questions in the design summary
   3. Move feature to 02_READY_TO_DEVELOP (if in 01_SUBMITTED)
   4. Create implementation tasks from the design summary
```

---

## Backend Feature Shortcut

**If the feature is explicitly backend-only (no UI):**

Create a single file: `design-summary.md` with this content:

```markdown
# Design Summary: [Feature Title]

**Feature ID**: {{feature_id}}
**Date**: [Today's date]
**Type**: Backend / No UI

## Overview
[Description of the backend feature]

## API/Interface Design
[Describe the API endpoints, data structures, or interfaces]

## Integration Points
[How other parts of the system will interact with this]

## Implementation Notes
[Technical considerations]

## Why No UI
[Explanation of why this is a backend-only feature]
```

Then report:
```
✅ Backend Feature Design Summary Generated for {{feature_id}}

📁 Feature folder: [path]
📄 Document created: design-summary.md (Backend feature - no UI wireframes needed)
```

---

## Error Handling

- **Feature not found**: Report clearly and stop
- **FeatureDescription.md missing**: Cannot proceed without requirements - stop and report
- **Unable to write files**: Report the specific error and which phase failed
- **Ambiguous requirements**: Note in UX-research-report.md under "Open Questions" and continue
