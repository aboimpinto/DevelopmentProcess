# Prompt Management Strategy

This document outlines the strategy for managing LLM prompts within the MCP Server. Instead of hardcoding prompt logic within the Python code, we utilize a **Prompt Library** stored as external Markdown files.

## Core Philosophy

*   **Separation of Concerns:** The Python code (`main.py`) handles the *mechanics* (routing, file I/O, API calls), while the Prompt files handle the *intelligence* (instructions, personas, templates).
*   **Maintainability:** Prompts can be edited, versioned, and reviewed without touching the core server code.
*   **Context-Awareness:** Prompts are designed as templates that accept dynamic variables (e.g., `{feature_title}`, `{user_description}`).

## Directory Structure

Prompts are stored in the `DevCycleManager/Prompts/` directory.

```text
DevCycleManager/
├── main.py
├── requirements.txt
└── Prompts/
    ├── submit_feature.md       # Instructions for generating a feature description
    ├── design_feature.md       # Instructions for generating a technical design
    ├── architecture_review.md  # Checklist for architectural compliance
    └── ...
```

## Prompt File Format

Prompt files are standard Markdown files. They can contain:
1.  **System Instructions:** "You are an expert Product Manager..."
2.  **Formatting Rules:** "Output must be valid Markdown..."
3.  **Placeholders:** Variables enclosed in curly braces (e.g., `{title}`) which are replaced by the server at runtime.

### Example: `submit_feature.md`

```markdown
You are a Senior Technical Product Manager.
Please convert the following raw idea into a structured Feature Description.

**Input Data:**
- Title: {title}
- Raw Description: {description}

**Requirements:**
1. Define clear Acceptance Criteria.
2. Identify potential risks.
3. Reference the project's 'CodeGuidelines' if applicable.

**Output:**
Return only the Markdown content for the file.
```

## Implementation Logic

The MCP Server (`main.py`) follows this pattern:

1.  **Load:** When a command is triggered (e.g., `submit-feature`), the server reads the corresponding file (`Prompts/submit_feature.md`).
2.  **Interpolate:** It replaces placeholders (like `{title}`) with the actual arguments provided by the user.
3.  **Execute:** The fully populated string is sent to the Client via the Sampling Protocol (`ctx.session.sample()`).
4.  **Result:** The LLM's response is used as the content for the next step in the workflow (e.g., writing a file).

## Updating Prompts

To update a prompt:
1.  Edit the `.md` file in `DevCycleManager/Prompts/`.
2.  Rebuild the Docker image (`docker build ...`) to include the changes in the container.
3.  Restart the container.
