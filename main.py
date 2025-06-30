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

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("history", []), data.get("last_response_id", None)
    except FileNotFoundError:
        return [], None

def save_session(history, last_response_id):
    with open(SESSION_FILE, "w") as f:
        json.dump({"history": history, "last_response_id": last_response_id}, f)

async def main():
    history, last_response_id = load_session()
    print("To-Do Agent (LLM-powered, all tracing enabled). Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        # Add the new user message to history
        history.append({"role": "user", "content": user_input})
        # Run the agent with full history and chaining
        result = await Runner.run(
            agent,
            input=history,
            previous_response_id=last_response_id,
        )
        print(f"Agent: {result.final_output}")
        # Update history and last_response_id for next turn
        history = result.to_input_list()
        # Try to get the response ID from possible attributes
        last_response_id = getattr(result, "openai_response_id", None)
        if last_response_id is None and hasattr(result, "metadata"):
            last_response_id = getattr(result.metadata, "openai_response_id", None)
        # Optionally, print available attributes for debugging
        # print(dir(result))
        save_session(history, last_response_id)

if __name__ == "__main__":
    asyncio.run(main()) 