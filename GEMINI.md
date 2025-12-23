# Project Overview

This project is focused on learning how to create a **MCP (Centralized Development Process) server**. The goal is to define a standardized development process that can be used by Gemini to manage a feature development lifecycle.

The MCP server will run as a self-contained application inside a Docker container, either locally or in the cloud.

For a detailed explanation of the architecture and technical implementation, see the documents in the `MemoryBank/Overview` directory.

# Development Workflow

The core of this project is the feature development workflow, which is managed by the MCP server. Features are represented as folders containing Markdown files and their state is determined by their location within the `MemoryBank/Features` directory.

## Feature States

*   `01_SUBMITTED`: New feature ideas.
*   `02_READY_TO_DEVELOP`: Designed and approved features.
*   `03_IN_PROGRESS`: Features currently under development.
*   `04_COMPLETED`: Completed features.

## MCP Commands

The MCP server will provide commands to move features through the development workflow, such as `SubmitFeature`, `DesignFeature`, `StartImplementation`, and `ImplementationCompleted`.

# Directory Structure

*   **`GEMINI.md`**: This file, providing a high-level overview of the project.
*   **`MemoryBank/`**: The knowledge base for the project.
    *   **`Overview/`**: Contains detailed documentation about the project's architecture and design.
        *   `Architecture.md`: Explains the core concepts, feature management, and MCP commands.
        *   `MCP_Containerization.md`: Details the technical plan for building and running the MCP server in Docker, including LLM integration via the Sampling Protocol.
        *   `Sampling_Protocol.md`: Describes the "MCP Sampling Protocol" for integrating the MCP server with the host's LLM context.
        *   `Remote_Process_Model.md`: Defines the interaction model where the Server acts as the "Recipe Book" and the Client as the "Hands" to manage local files from a remote context.
        *   `Prompt_Management.md`: Details the strategy for storing and using external Markdown templates for LLM prompts.
    *   **`Features/`**: Contains the feature folders, organized by their current state.
        *   `01_SUBMITTED/`
        *   `02_READY_TO_DEVELOP/`
        *   `03_IN_PROGRESS/`
        *   `04_COMPLETED/`
        *   `05_CANCELLED/`
    *   **`CodeGuidelines/`**: Coding standards and style guides.
    *   **`Architecture/`**: High-level system design documents.
    *   **`LessonsLearned/`**: Retrospectives and knowledge sharing.
    *   **`Tools/`**: Scripts and utility configurations.

# LLM Integration

The integration with the host's LLM is a key aspect of this project. The chosen approach is the **MCP Sampling Protocol**, where the client application (e.g., the Gemini CLI) is responsible for all communication with the LLM. The MCP server will request LLM actions via `ctx.session.sample()`, but it will not have direct access to the LLM or require its own `GEMINI_API_KEY`.

This pattern is secure, flexible, and preserves the rich context of the calling environment. For a detailed explanation, see the [Sampling Protocol](./MemoryBank/Overview/Sampling_Protocol.md) document.
