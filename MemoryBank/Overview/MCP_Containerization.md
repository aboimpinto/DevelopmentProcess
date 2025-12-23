# MCP Server Containerization

This document provides a technical overview of how the MCP (Centralized Development Process) server will be built, containerized, and run.

## 1. Recommended Programming Language

**Python** is the recommended language for creating the MCP server. It has a strong ecosystem of libraries for web development and is well-suited for the file manipulation tasks required by the MCP.

A lightweight web framework like **Flask** or **FastAPI** is recommended to expose the MCP commands as a REST API.

## 2. Container Software Requirements

The Docker container will need the following software:

*   **Base Image:** A standard Python base image (e.g., `python:3.10-slim`).
*   **Python Libraries:**
    *   `Flask` or `FastAPI` to create the web server and API endpoints.
    *   Any other libraries needed for interacting with the filesystem or handling requests.
*   **Application Code:** The MCP server's Python source code.

## 3. Exposed Ports

The container will need to expose a port to make the MCP API accessible. The specific port can be configured, but a common choice is:

*   **`8000`** (if using FastAPI) or **`5000`** (if using Flask).

This port will be mapped to a port on the host machine when the container is run.

## 4. MCP SDK

There is no special "MCP SDK" to be installed. We will be creating the MCP server application from scratch.

## 5. Build and Run Commands

Here are example commands for building and running the MCP container.

### Building the Docker Image

A `Dockerfile` will be created in the root of the project. The command to build the image would be:

```bash
docker build -t mcp-server .
```

### Running the Docker Container

The `docker run` command needs to do two important things:
1.  Map the container's exposed port to a port on the host machine.
2.  Mount the `MemoryBank` directory on the host into the container so the MCP server can access and modify the feature folders.

```bash
docker run -d -p 8080:8000 \
  -v /path/to/your/DevelopmentProcess/MemoryBank:/app/MemoryBank \
  --name mcp-server-instance \
  mcp-server
```

*   `-p 8080:8000`: Maps port `8080` on the host to port `8000` in the container.
*   `-v /path/to/your/DevelopmentProcess/MemoryBank:/app/MemoryBank`: Mounts the local `MemoryBank` directory as a volume inside the container at `/app/MemoryBank`. **You must replace the path with the absolute path to your `MemoryBank` directory.**

## 6. First Steps to Create the MCP Software

1.  **Initialize a Python Project:** Create a `src` directory for the Python code and a `requirements.txt` file to list dependencies.
2.  **Choose a Web Framework:** Decide between Flask or FastAPI and set up a basic "Hello World" application.
3.  **Implement File System Logic:** Create Python functions to handle the core logic of the MCP:
    *   Creating new feature folders in `01_SUBMITTED`.
    *   Moving feature folders between the state directories (`01_SUBMITTED`, `02_READY_TO_DEVELOP`, etc.).
    *   Reading and writing to the Markdown files within a feature folder.
4.  **Create API Endpoints:** Create an API endpoint for each of the MCP commands (`SubmitFeature`, `StartImplementation`, etc.).
5.  **Create the `Dockerfile`:** Write a Dockerfile that builds the container image with all the necessary software and the application code.

## 7. LLM Integration

The integration with the host's LLM (e.g., the one used by the Gemini CLI) is a critical part of the architecture. The recommended approach is to leverage the **MCP Sampling Protocol**, where the client application (e.g., Gemini CLI) is responsible for all communication with the LLM. The MCP server will request LLM actions via `ctx.session.sample()`, but it will not have direct access to the LLM or require its own `GEMINI_API_KEY`.

This pattern is explained in detail in the [Sampling Protocol](./Sampling_Protocol.md) document.
