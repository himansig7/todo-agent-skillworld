# todo-agent

A minimal OpenAI Agents SDK to-do list app with full CRUD operations and built-in tracing/observation integrations for:
- OpenAI Platform Tracing
- Arize Phoenix Cloud
- Weights & Biases Weave

This project demonstrates a 101-level AI engineering workflow: building a to-do app agent, observing traces in multiple platforms, and following best practices for Python project management.

---

## Project Structure

```
todo-agent/
├── main.py                  # Entry point, tracing, CLI loop
├── agent/
│   ├── __init__.py
│   ├── todo_agent.py        # Core agent logic (CRUD, OpenAI SDK)
│   └── storage.py           # JSON storage logic
├── data/
│   ├── todos.json           # (empty list on init)
│   └── session_default.json # (empty session on init)
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

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

- Interact with the agent in natural language (e.g., "Add a to-do: Buy groceries.", "Show my to-do list.").
- Type `exit` or `quit` to end the session.
- Traces are sent to OpenAI, Weave (W&B), and Phoenix Cloud (Arize web UI).

---

## Data Files

- `data/todos.json` and `data/session_default.json` are initialized as empty in the repo.
- These files are updated as you use the app, but are always reset to empty for a clean repo state.
- If you want to reset your app, simply clear these files to their initialized state.

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
