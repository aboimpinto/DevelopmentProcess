# LLM Integration: The MCP Sampling Protocol

This document details the integration pattern for leveraging the host's Language Model (LLM) capabilities from within the MCP server, utilizing the **Sampling** feature of the MCP protocol. This approach avoids the need for the MCP server to directly manage LLM API keys or connections.

## What is MCP Sampling?

**Sampling** is a feature of the MCP protocol that allows the **Server** (our MCP server application) to ask the **Client** (e.g., Gemini CLI, Claude Code) to generate text on its behalf.

### Key Benefits:

*   **No Extra API Key:** Sampling uses the API key and quota already active in the client environment. The MCP server does not need its own LLM API key.
*   **No Double Cost:** LLM calls made via sampling count towards the client's session usage, avoiding duplicate billing.
*   **Model Alignment:** The sampling mechanism ensures that the text generation uses the same model "intelligence" that the user is currently interacting with via the client.

## Core Concept: Orchestration with Sampling

The fundamental idea is that the MCP server, when it requires LLM assistance, returns a "request for an LLM call" to the client that invoked it. The client then executes the LLM call using its own capabilities and returns the result back to the MCP server.

This creates a "callback" or "orchestration" style workflow where the MCP server defines the LLM task, but the client executes it.

## Technical Implementation (Server-Side)

On the server side (e.g., in a Python application using `uvicorn`):

1.  **Import `Context`**: The server will need to import `Context` to access session-specific functionalities.
2.  **`async` Functions**: Functions that interact with the client for sampling must be `async` as communication back to the client takes time.
3.  **`ctx.session.sample()`**: Instead of using a `genai.Client` or similar LLM client, the server will call `ctx.session.sample()` to initiate the LLM request to the client.

**Example Snippet (Conceptual `project_assistant.py`):**

```python
from fastapi import FastAPI, Depends
from your_mcp_library import Context # Assuming Context is provided by the environment

app = FastAPI()

# Placeholder for how Context might be passed or accessed
def get_context():
    # This would typically be provided by the MCP framework/runtime
    # For demonstration, assume it's available.
    pass

@app.post("/design-feature")
async def design_feature(feature_id: str, ctx: Context = Depends(get_context)):
    # ... MCP server logic to read feature description ...
    prompt = "Based on the following user story, please generate a detailed technical design for the 'new-login-flow' feature..."

    # Initiate sampling request to the client
    llm_response = await ctx.session.sample(prompt=prompt, temperature=0.7, max_tokens=1024)

    # ... MCP server logic to process llm_response and update feature files ...

    return {"status": "SUCCESS", "message": "Feature designed."}
```

## Important Caveat: Client Support

While **Sampling** is part of the official MCP protocol, **Client support varies**:

*   **Gemini CLI:** Generally supports sampling.
*   **Claude Desktop:** Supports sampling in recent versions.
*   **Claude Code (CLI):** Support is being rolled out. If an error like "Sampling not supported" or "Capability not found" occurs, the client might not support this feature, and an alternative (e.g., direct API key usage if permissible) might be necessary.

## How to Run

To run a server utilizing sampling, typically no special configuration for LLM API keys is needed within the server's environment. The `GEMINI_API_KEY` environment variable can often be removed from the server's `settings.json` if desired, as the client handles the LLM authentication.

The server would be run as usual (e.g., `uv run project_assistant.py` or `python your_server.py` after dependencies are installed).