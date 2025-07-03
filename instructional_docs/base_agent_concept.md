# The To-Do Robot: Product Schematics

Welcome, QA Engineer. This document is the official technical blueprint for our To-Do Robot prototype. Use this as your reference guide when you're analyzing inspection reports (traces) to understand how the product is built.

## High-Level Overview

-   **Goal**: To build a simple, effective AI agent prototype.
-   **Core Components**: The robot is built from a few key parts:
    1.  **Command Center (`main.py`)**: Where the test process is initiated.
    2.  **Brain & Rulebook (`agent/todo_agent.py`)**: The core logic and operating instructions.
    3.  **Backpack (`agent/storage.py`)**: The robot's memory storage unit.
-   **Core Technologies**: The schematics call for OpenAI's Agents SDK, Pydantic for data validation, and our three inspection toolkits (tracing libraries).

---

## Component Deep-Dive

### 1. `main.py`: The Robot's Power Switch & Command Center

This script is where the engineer initiates a test cycle.

-   **Responsibilities**:
    -   **Power On**: Loads environment variables from `.env`.
    -   **Connect Inspection Tools (Tracing Setup)**: This is the critical step where we initialize our observability toolkits. This ensures every action is measured.
    -   **The Command Line**: Manages the interactive session where we run our tests.
    -   **Short-Term Memory**: Handles saving and loading conversation history.

-   **Inspector's Note**: The `Runner.run()` call in this file is the start of every Inspection Report. When you view a trace, this will be the top-level "root" span that all other measurements are nested under.

### 2. `agent/todo_agent.py`: The Robot's Brain & Rulebook

This is where the robot's core processing logic lives.

-   **The Brain (`Agent` Object)**: This object bundles the robot's `model`, its `instructions` (the Rulebook), and its `tools`.
-   **The Rulebook (`AGENT_PROMPT`)**: This is the primary specification for the robot's behavior. It's a detailed set of instructions we give the AI to guide its decisions.
-   **Inspector's Note**: The Rulebook is the most important specification to check. If the robot fails a test by using the wrong tool or giving a bad response, the first step is to see if it's correctly following its own operating manual.

### 3. `agent/todo_agent.py`: The Robot's Hands & Toolbox

These are the functions that the robot can execute to perform actions.

-   **The `@function_tool` Decorator**: A special tag identifying a Python function as a standard tool in the robot's toolbox.
-   **Tool Manuals (Pydantic Arguments)**: The arguments for each tool function (e.g., `name: str`) act as a user manual for the Brain, telling it exactly what information it needs to operate the tool.
-   **Inspector's Note**: Every time the robot uses a tool, it appears as a "tool call" checkpoint (span) in the inspection report. This is a critical measurement point. You can inspect the `inputs` and `outputs` to verify the robot is operating its tools correctly.

### 4. `agent/storage.py`: The Robot's Backpack

This script handles the robot's long-term memory.

-   **The `TodoStorage` Class**: A dedicated class to handle all read/write operations for the to-do list file (`data/todos.json`).
-   **Decoupling from the Brain**: The Brain doesn't need to know *how* the Backpack works, just that it can store and retrieve things. This is a great engineering practice for creating modular and testable systems.
-   **Inspector's Note**: While the Backpack functions aren't "tools" the robot chooses, they are part of the overall process. A slow file system or a bug in saving data would cause high latency in the parent tool's checkpoint, helping us isolate performance issues beyond the AI's logic.

---

## Data & Execution Flow

The following diagram illustrates the lifecycle of a single user request. This flow is what our inspection reports (traces) will capture and allow us to measure.

See the [Agent Execution Flow Diagram](./agent_mermaid_diagram.md).
