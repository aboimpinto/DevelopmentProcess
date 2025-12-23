# Project Architecture

This document outlines the architecture of the **MCP (Centralized Development Process) server**.

## Core Concept

The MCP server is a self-contained application, running in a Docker container, that exposes a set of commands to manage a standardized feature development lifecycle. It acts as a state machine, moving features through a predefined workflow.

## Remote Process Model

The architecture follows a **"Recipe Book" (Server) vs. "Hands and Eyes" (Client)** model to handle the separation between the process logic and the local project files.

*   **The Server** defines the *process* (what steps to take, what docs to read).
*   **The Client** executes the *actions* (reading files, calling the LLM, writing results).

For a detailed explanation of this interaction, see [Remote_Process_Model.md](./Remote_Process_Model.md).

## Prompt Engineering

The project utilizes a **Prompt Library** pattern to decouple LLM instructions from server code. Prompts are stored as external Markdown templates in the `DevCycleManager/Prompts/` directory.

For details on the prompt strategy and file format, see [Prompt_Management.md](./Prompt_Management.md).

## Containerization

The server will be packaged as a Docker image. This allows it to be run consistently in any environment, either locally for development or deployed to a cloud provider.

## Feature Management

The core of the MCP is the management of "features".

*   **Representation:** A feature is represented as a folder containing Markdown files that describe the feature in detail.
*   **Storage:** All features are stored within the `MemoryBank/Features` directory.
*   **State:** A feature's current state in the development lifecycle is determined by its location within the subdirectories of `MemoryBank/Features`.

### Feature States

The development process is divided into the following states. A feature, represented by its folder, will be moved between these state directories.

1.  **`01_SUBMITTED`**: A new feature idea is submitted. It contains an initial description.
2.  **`02_READY_TO_DEVELOP`**: The feature has been designed and refined and is ready for implementation.
3.  **`03_IN_PROGRESS`**: A developer has started working on the feature.
4.  **`04_COMPLETED`**: The implementation is complete.
5.  **`05_CANCELLED`**: The feature was abandoned or rejected.

## MCP Commands

The MCP server will expose an API with the following commands to manipulate the state of a feature:

*   **`SubmitFeature`**: Creates a new feature folder in the `01_SUBMITTED` directory.
*   **`DesignFeature`**: Adds design details to the feature's Markdown files.
*   **`RefineFeature`**: Allows for updates and refinements to the feature's design. This might not move the folder but will modify its content.
*   **`StartImplementation`**: Moves the feature folder from `02_READY_TO_DEVELOP` to `03_IN_PROGRESS`.
*   **`ContinueImplementation`**: Used to add implementation notes or updates while the feature is `03_IN_PROGRESS`.
*   **`ImplementationCompleted`**: Moves the feature folder from `03_IN_PROGRESS` to `04_COMPLETED`.