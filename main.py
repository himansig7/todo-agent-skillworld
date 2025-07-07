"""
Entry point for the command-line interface (CLI) of the todo-agent.

This script demonstrates a typical setup for a stateful, conversational agent:
- Loads environment variables for API keys and configuration.
- Initializes tracing and observability integrations (Phoenix, Weave).
- Manages conversation history by saving and loading it from a JSON file.
- Creates an agent with a file-based storage backend (`JsonTodoStorage`).
- Runs a loop to interact with the user via the command line.
"""

# Standard library imports
import os
import asyncio
import json

# Third-party imports
from dotenv import load_dotenv
from phoenix.otel import register
import weave
from agents import Runner, Agent

# Local application imports
from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage

# --- Initial Setup ---
# Load environment variables from a .env file. This is a best practice for
# managing secrets and configuration without hardcoding them in the source code.
load_dotenv()

# --- Tracing & Observation Setup ---
# Initialize integrations to observe and debug the agent's behavior.
# This is crucial for understanding the agent's decision-making process.
os.environ["OPENAI_TRACING_ENABLED"] = "1"
os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
register(
    # The project name groups all traces from this CLI application.
    project_name="todo-agent-cli",
    auto_instrument=True
)
weave.init("todo-agent-cli")

# -----------------------------------------------------------------------------
# Session Management
#
# To create a stateful conversation, we save/load the message history
# to a JSON file, allowing the agent to "remember" past interactions.
# -----------------------------------------------------------------------------
SESSION_FILE = "data/session_default.json"
MAX_TURNS = 12 # Max *user* turns to keep in history to prevent token overflow.

def load_session() -> list:
    """Loads the message history from the session file."""
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        # Return the history if it exists, otherwise an empty list.
        return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/corrupt, start a new session.
        return []

def save_session(history: list):
    """Saves the message history to the session file."""
    # Ensure the 'data' directory exists.
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        # Save the history in a structured format.
        json.dump({"history": history}, f, indent=2)

async def main():
    # Load the previous conversation history to maintain context.
    history = load_session()
    
    # Create the agent instance using the central factory,
    # providing it with the file-based storage system.
    agent = create_agent(
        storage=JsonTodoStorage(),
        agent_name="To-Do Agent (CLI)"
    )
    print("To-Do Agent (CLI) is ready. Tracing is enabled. Type 'exit' to quit.")
    
    # Start the main interaction loop.
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        
        # Add the new user message to the history.
        history.append({"role": "user", "content": user_input})

        # --- Context Window Management ---
        # To prevent token overflow, we trim the history to the last `MAX_TURNS`.
        user_message_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
        if len(user_message_indices) > MAX_TURNS:
            # Find the index of the oldest user message to keep.
            start_index = user_message_indices[-MAX_TURNS]
            print(f"(Trimming conversation history to the last {MAX_TURNS} turns...)")
            history = history[start_index:]

        # --- Agent Execution ---
        # The Runner handles the conversation turn, calling tools and the LLM.
        result = await Runner.run(
            agent,
            input=history,
        )
        print("----"*10)
        print(f"Agent: {result.final_output}")
        print("===="*10)
        
        # The agent's result contains the full, updated history (user, assistant, tools).
        # We replace our local history with this to prepare for the next turn.
        history = result.to_input_list()
        
        # Save the updated history to disk to maintain state for the next session.
        save_session(history)

if __name__ == "__main__":
    # Run the asynchronous main function.
    asyncio.run(main()) 