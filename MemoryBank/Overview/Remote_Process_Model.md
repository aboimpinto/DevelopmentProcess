# Remote Process Model: "Recipe Book" & "Hands"

This document defines the interaction model between the **MCP Server** (potentially remote) and the **Client** (local environment). This architecture addresses the "Context Gap" where the server defines the process but lacks direct access to the project files.

## Core Philosophy

*   **MCP Server as the "Recipe Book":** The server is stateless regarding the project's content. It holds the **Process Knowledge** (e.g., "To design a feature, one must read the Architecture doc and generate a Markdown file"). It acts as the Orchestrator.
*   **Client as the "Hands and Eyes":** The local client (CLI/Agent) holds the **Context** (files, git history). It is responsible for executing File I/O and providing the "brain" (LLM) with the necessary data.

## The Interaction Flow

The workflow relies on the MCP Server sending **Instructions** and **Prompts** to the Client, rather than performing direct file manipulations.

### Example: "Design a Feature"

1.  **Trigger:** User sends a command to the MCP: `DesignFeature(feature_id="123")`.
2.  **MCP "Recipe" Lookup:**
    *   The MCP identifies the process: "Design Phase".
    *   It knows this requires:
        *   Input: `MemoryBank/Overview/Architecture.md` and `MemoryBank/Overview/Sampling_Protocol.md`.
        *   Action: Generate a `Design.md` file.
3.  **MCP Request (Sampling):**
    *   The MCP uses `ctx.session.sample()` to send a request to the Client.
    *   **Prompt Instruction:** "I need to design feature 123. Please **read the local architecture documents**, and using that context, generate a technical design document."
4.  **Client Execution (The "Hands"):**
    *   The Client receives the request.
    *   It executes local tools (e.g., `read_file`) to fetch the requested context.
    *   It sends the context + prompt to the local LLM.
5.  **LLM Generation:** The LLM generates the design content.
6.  **Return to MCP:** The Client sends the generated content back to the MCP.
7.  **MCP Final Response:**
    *   The MCP wraps the content in a final response.
    *   **Instruction:** "Design generated. Please **write** this content to `MemoryBank/Features/02_READY_TO_DEVELOP/FEAT-123/Design.md`."
8.  **Client Final Action:** The Client (or User) confirms and saves the file locally.

## Benefits

*   **Remote-Ready:** The MCP Server can run in a Docker container in the cloud (AWS, Azure) without needing access to the user's local file system.
*   **Context-Aware:** The generation uses the full local context provided by the Client, ensuring high-quality outputs.
*   **Secure:** No API keys or source code are permanently stored on the MCP server.

## Architectural Implication

The MCP Server code (`main.py`) must be refactored to:
1.  **Remove** direct `os` and `open()` calls for project files.
2.  **Implement** `sample()` calls that instruct the client to fetch context.
3.  **Return** structured instructions (e.g., "Write this file") instead of performing the write itself.
