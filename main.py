"""
Entry point for the todo-agent project.
- Loads environment variables
- Initializes the agent
- Starts the CLI or API for CRUD operations
"""

# Standard library imports
import os
import warnings
import asyncio
import json

# Third-party imports
from dotenv import load_dotenv
from pydantic.json_schema import PydanticJsonSchemaWarning
from phoenix.otel import register
import weave
from agents import Runner

# Local application imports
from agent.todo_agent import agent

# --- Initial Setup ---
load_dotenv()

# Suppress harmless Pydantic warnings for a cleaner console experience.
warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)

# --- Tracing & Observation Setup ---
# Initialize integrations for OpenAI, Arize Phoenix, and Weave to observe agent behavior.
os.environ["OPENAI_TRACING_ENABLED"] = "1"
os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
register(
    project_name="todo-agent",
    auto_instrument=True
)
weave.init("todo-agent-weave")

# -----------------------------------------------------------------------------
# Session Management
#
# To maintain a continuous conversation, we save the message history to a local
# JSON file. This allows the agent to "remember" previous turns of the
# conversation even if the application is restarted.
# -----------------------------------------------------------------------------
SESSION_FILE = "data/session_default.json"
MAX_TURNS = 12 # Max conversation turns to keep in history

def load_session() -> list:
    """Load message history from the session file."""
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_session(history: list):
    """Save message history to the session file."""
    with open(SESSION_FILE, "w") as f:
        json.dump({"history": history}, f, indent=2)

async def main():
    history = load_session()
    print("To-Do Agent (LLM-powered, all tracing enabled). Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        # Add the new user message to history
        history.append({"role": "user", "content": user_input})

        # Trim the history to the last MAX_TURNS to prevent token overflow.
        user_message_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
        if len(user_message_indices) > MAX_TURNS:
            start_index = user_message_indices[-MAX_TURNS]
            history = history[start_index:]

        # Run the agent with the managed history
        result = await Runner.run(
            agent,
            input=history,
        )
        print("----"*10)
        print(f"Agent: {result.final_output}")
        print("===="*10)
        # The agent's result contains the full updated history (user, agent, tools).
        # We replace our local history with this to prepare for the next turn.
        history = result.to_input_list()
        save_session(history)

if __name__ == "__main__":
    asyncio.run(main()) 