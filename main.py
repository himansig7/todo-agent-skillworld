"""
Entry point for the todo-agent project.
- Loads environment variables
- Initializes the agent
- Starts the CLI or API for CRUD operations
"""

import os
from dotenv import load_dotenv
load_dotenv()

from phoenix.otel import register
register(
    project_name="todo-agent",
    auto_instrument=True
)

import weave
import asyncio
import json
from agents import Runner
from agent.todo_agent import agent

# Enable all tracing integrations
os.environ["OPENAI_TRACING_ENABLED"] = "1"
weave.init("todo-agent-weave")

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

        # Trim history to the last MAX_TURNS to avoid token overflow.
        user_message_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
        if len(user_message_indices) > MAX_TURNS:
            start_index = user_message_indices[-MAX_TURNS]
            history = history[start_index:]

        # Run the agent with the managed history
        result = await Runner.run(
            agent,
            input=history,
        )
        print(f"Agent: {result.final_output}")
        # Update history for next turn
        history = result.to_input_list()
        save_session(history)

if __name__ == "__main__":
    asyncio.run(main()) 