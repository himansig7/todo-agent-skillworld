# todo-agent

A minimal OpenAI Agents SDK to-do list app with a full CRUD toolset and built-in web search. This project includes tracing/observation integrations for:
- OpenAI Platform Tracing
- Arize Phoenix Cloud
- Weights & Biases Weave

This project demonstrates a 101-level AI engineering workflow: building a modular agent, observing traces, and following best practices for Python project management.

---

## Project Structure

```
todo-agent/
├── main.py                  # Entry point, tracing, & CLI loop
├── manage.py                # CLI for managing data (reset, seed)
├── agent/
│   ├── __init__.py
│   ├── todo_agent.py        # Defines the agent, its tools, and prompt
│   └── storage.py           # Data access layer for todos.json
├── data/
│   ├── todos.json           # User-specific to-do items (auto-created, gitignored)
│   ├── session_default.json # Conversation history (auto-created, gitignored)
│   └── seed_todos.json      # Example data for the `manage.py seed` command
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Agent Capabilities

The agent has access to a suite of tools to be a proactive assistant:

- **`create_todo`**: Adds a new task to the list.
- **`read_todos`**: Lists all tasks or filters by project.
- **`update_todo`**: Modifies an existing task (e.g., renames it or marks it as complete).
- **`delete_todo`**: Removes a task.
- **`web_search`**: Searches the web to find information and clarify tasks. For example, if you ask it to "plan a trip," it will offer to research destinations for you.

---

## Setup

1. **Install [uv](https://github.com/astral-sh/uv)**
2. **Install dependencies:**
   ```sh
   uv pip install
   ```
3. **Environment variables:**
   - Copy `.env.example` to `.env` and fill in your API keys and secrets. All required and optional variables are documented in `.env.example`.

---

## Environment Variables

All required and optional environment variables are documented in the `.env.example` file. Copy this file to `.env` and update the values as needed for your environment and integrations.

---

## Running the App

```sh
python main.py
```

- Interact with the agent in natural language.
- To see the new project features, try requests like:
  - "I need to plan a vacation."
  - "Add 'buy a new laptop' to my list." (The agent might ask if you want help researching models).
  - "Show me my 'House Chores' project tasks."
- Type `exit` or `quit` to end the session.
- Traces are sent to OpenAI, Weave (W&B), and Phoenix Cloud (Arize web UI).

---

## Managing Data for Testing

This project includes a `manage.py` script with commands to help you reset or seed your data, which is useful for testing or running evaluations.

-   **Resetting Data**: To clear all to-do items and conversation history, run:
    ```sh
    python manage.py reset --yes
    ```
-   **Seeding Data**: To load a specific set of to-dos for a test, run:
    ```sh
    python manage.py seed
    ```
    This command uses `data/seed_todos.json` by default, but you can provide a path to a different file.

---

## Data Files

The `data/` directory holds both user-generated data and example data:

- **`todos.json` & `session_default.json`**: These files are created automatically when you first run the app. They are listed in the `.gitignore` file, so your local conversation history and to-do items will not be committed to the repository.
- **`seed_todos.json`**: This file is included in the repository and provides a default set of to-dos that you can load using the `python manage.py seed` command. It serves as a good starting point for testing.

---

## Tracing Integrations

All tracing integrations are enabled by default in `main.py`:
- **OpenAI Platform**: Native support, see [OpenAI docs](https://platform.openai.com/docs/observability/overview)
- **Arize Phoenix Cloud**: See [Phoenix Otel Python SDK](https://arize.com/docs/phoenix/sdk-api-reference/python-pacakges/arize-phoenix-otel)
- **Weights & Biases Weave**: See [W&B Weave docs](https://docs.wandb.ai/guides/weave)

You can view traces in each provider's dashboard after running the agent.

---

## any.cursor Rules

- Use Python 3.12+
- Use `uv` for all dependency and environment management
- Only add dependencies with `uv add ...` or `uv pip install ...`
- Never edit `pyproject.toml` directly
- Use `python-dotenv` for environment variables
- Follow PEP 8 and use type hints
- Modular, reusable, and well-documented code
- Comment complex logic and include Google-style docstrings
- Implement proper error handling
- Focus on security and performance

---

## License

MIT
