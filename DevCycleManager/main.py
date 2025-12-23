import os
import re
import json
from pathlib import Path
from typing import Optional, Union, List, Any, Dict

from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field

# --- Constants & Configuration ---
# Path to the directory containing prompt/config files
PROMPTS_DIR = Path(__file__).parent / "Prompts"

# --- Mocking the MCP Context/Sampling for the Prototype ---
async def mock_sample_llm(prompt: str, context: Optional[str] = None) -> str:
    """
    Simulates the MCP Sampling Protocol (`ctx.session.sample()`).
    In a real deployment, this sends the prompt to the Client's LLM.
    """
    print(f"\n[MCP SERVER] Sampling Request sent to Client:")
    print(f"--- Prompt ---\n{prompt}\n--------------")
    if context:
        print(f"--- Context requested ---\n{context}\n-------------------------")
    
    # Simulate a response for the prototype
    return f"[LLM Generated Content based on: {prompt[:30]}...]"

# --- Core Business Logic (The "Recipes") ---

async def run_init_project() -> dict:
    """
    The Recipe for initializing the project.
    It reads the required folder structure from a configuration file.
    """
    try:
        with open(PROMPTS_DIR / "init-project.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            required_folders = config.get("directories", [])
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="init-project.json not found in Prompts directory.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding init-project.json.")

    instructions = "Please initialize the project structure by creating the following directories:\n\n"
    for folder in required_folders:
        instructions += f"- {folder}\n"
    
    return {
        "status": "pending_action",
        "action": "create_directories",
        "directories": required_folders,
        "message": instructions
    }

async def run_submit_feature(description: str, title: Optional[str] = None, feature_id: Optional[str] = None) -> dict:
    """
    The Recipe for submitting a feature.
    1. Ask Client's LLM to generate a title (if missing).
    2. Ask Client's LLM to generate a description.
    3. Tell Client to save the file.
    """
    # Step 1: Generate Title if needed
    if not title:
        title_prompt = f"Create a concise (4-6 words) feature title for: '{description}'"
        # In a real app, we'd wait for this sample to return
        title = await mock_sample_llm(title_prompt)
        # Cleanup mock response for title to be usable as a slug
        title = "Generated Feature Title" 

    # Slugify for filename (logic stays here as it's a pure function)
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9- ]", "", slug)
    
    folder_name = f"FEAT-{slug}"
    if feature_id:
        folder_name = f"FEAT-{feature_id}-{slug}"
    
    # Step 2: Generate Description Content
    desc_prompt = f"Generate a markdown feature description for '{title}'. Requirement: {description}"
    # This instructs the client (implicitly) to use its LLM.
    # We might also ask the client to read 'MemoryBank/CodeGuidelines' first to match style.
    generated_content = await mock_sample_llm(
        prompt=desc_prompt, 
        context="MemoryBank/CodeGuidelines" # Example of requesting context
    )
    
    # Step 3: Return Instruction to Write
    target_path = f"MemoryBank/Features/01_SUBMITTED/{folder_name}/FeatureDescription.md"
    
    return {
        "status": "pending_action",
        "action": "write_file",
        "path": target_path,
        "content": generated_content,
        "message": f"Feature designed. Please save the description to '{target_path}'."
    }

# --- JSON-RPC Pydantic Models ---
class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(..., pattern=r"^2.0$")
    method: str
    id: Optional[Union[str, int]] = None
    params: Optional[Union[Dict[str, Any], List[Any]]] = None

class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]]
    result: Optional[Any] = None
    error: Optional[Any] = None

# --- FastAPI App ---
app = FastAPI(title="DevCycleManager (Remote Process)")

@app.post("/", response_model=JsonRpcResponse, response_model_exclude_none=True)
async def json_rpc_handler(request: JsonRpcRequest):
    if request.id is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if request.method == "initialize":
        return JsonRpcResponse(id=request.id, result={
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "DevCycleManager", "version": "0.2.0-remote"},
            "capabilities": {"tools": {"listChanged": False}}
        })

    elif request.method == "tools/list":
        return JsonRpcResponse(id=request.id, result={
            "tools": [
                {
                    "name": "init-project",
                    "description": "Initialize the MemoryBank folder structure.",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "submit-feature",
                    "description": "Submit a new feature idea.",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "description": {"type": "string"},
                            "title": {"type": "string"},
                            "feature_id": {"type": "string"}
                        },
                        "required": ["description"]
                    }
                }
            ]
        })

    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        tool_args = request.params.get("input", {})

        try:
            if tool_name == "init-project":
                result = await run_init_project()
            elif tool_name == "submit-feature":
                result = await run_submit_feature(
                    description=tool_args.get("description"),
                    title=tool_args.get("title"),
                    feature_id=tool_args.get("feature_id")
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # The result is now a DICTIONARY of instructions, not just a string
            return JsonRpcResponse(id=request.id, result={"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
        
        except Exception as e:
            return JsonRpcResponse(id=request.id, error={"code": -32603, "message": str(e)})

    return JsonRpcResponse(id=request.id, error={"code": -32601, "message": "Method not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)