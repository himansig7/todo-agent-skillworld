"""
Entry point for the todo-agent project.
- Loads environment variables
- Initializes the agent
- Starts the CLI or API for CRUD operations
"""

import os
import weave
import phoenix as px
from agents import Runner
from agent.todo_agent import agent

# Enable all tracing integrations
os.environ["OPENAI_TRACING_ENABLED"] = "1"
weave.init("todo-agent-weave")
px.start_tracing()

def main():
    print("To-Do Agent (LLM-powered, all tracing enabled). Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        result = Runner.run(agent, user_input)
        print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    main() 