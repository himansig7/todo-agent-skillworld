# todo-agent

A minimal OpenAI Agents SDK to-do list app with full CRUD operations and built-in tracing/observation integrations for:
- OpenAI Platform Tracing
- Arize Phoenix
- Weights & Biases Weave

This project demonstrates a 101-level AI engineering workflow: building a to-do app agent, observing traces in multiple platforms, and following best practices for Python project management.

---

## Project Structure

```
todo-agent/
│
├── main.py                # Unified entry point for the agent and all tracing
├── agent/                 # Agent logic and tools
│   ├── __init__.py
│   ├── todo_agent.py      # Core agent logic (OpenAI SDK, CRUD)
│   └── storage.py         # JSON storage logic
├── data/
│   └── todos.json         # Local JSON file for to-do items
├── .cursor/
│   └── rules/
│       └── project-standards.mdc
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
   - Create a `.env` file for your API keys and secrets. See below for required and optional variables.

---

## Environment Variables

Create a `.env` file in your project root with at least:

```
OPENAI_API_KEY=sk-...
```

Optional (for tracing integrations):
```
# Enable OpenAI Platform tracing
OPENAI_TRACING_ENABLED=1

# Weights & Biases Weave
WANDB_API_KEY=your-wandb-api-key

# Arize Phoenix
PHOENIX_API_KEY=your-arize-api-key
PHOENIX_PROJECT=your-arize-project
PHOENIX_CLIENT_HEADERS=...
PHOENIX_COLLECTOR_ENDPOINT=...
```

---

## Running the App

```sh
python main.py
```

- Interact with the agent in natural language (e.g., "Add a to-do: Buy groceries.", "Show my to-do list.").
- Type `exit` or `quit` to end the session.

---

## Tracing Integrations

All tracing integrations are enabled by default in `main.py`:
- **OpenAI Platform**: Native support, see [OpenAI docs](https://platform.openai.com/docs/observability/overview)
- **Arize Phoenix**: See [Arize Phoenix docs](https://docs.arize.com/phoenix/)
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
