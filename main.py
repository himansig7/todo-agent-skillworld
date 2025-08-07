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
import time

# Third-party imports
from dotenv import load_dotenv

# Local application imports
from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage

from agents import Agent, Runner


# --- OpenTelemetry Tracing Setup ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode
from otel_file_exporter import FileSpanExporter

# Load environment variables from .env file
load_dotenv()

# Set up OpenTelemetry to write traces to a file
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace_log_path = os.path.join(os.path.dirname(__file__), 'otel_traces.log')
file_exporter = FileSpanExporter(trace_log_path)
span_processor = SimpleSpanProcessor(file_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)


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
        start_time = time.time()
        
        # Estimate input tokens (rough approximation)
        def count_tokens_in_content(content):
            if isinstance(content, str):
                return len(content.split())
            elif isinstance(content, list):
                # Handle streaming response chunks
                return sum(len(chunk.get('text', '').split()) for chunk in content if isinstance(chunk, dict))
            else:
                return 0
        
        input_tokens = len(user_input.split()) + sum(count_tokens_in_content(msg.get("content", "")) for msg in history)
        
        with tracer.start_as_current_span("agent_run") as span:
            span.set_attribute("user_input", user_input)
            span.set_attribute("num_turns", len(history))
            span.set_attribute("session_file", SESSION_FILE)
            span.set_attribute("estimated_input_tokens", input_tokens)
            span.set_attribute("start_time", start_time)

            try:
                result = await Runner.run(agent, input=history)
                
                # Calculate timing and token metrics
                end_time = time.time()
                response_time = end_time - start_time
                output_tokens = len(result.final_output.split())
                total_tokens = input_tokens + output_tokens
                
                # Set span attributes for metrics
                span.set_attribute("agent_output", result.final_output[:200])  # Avoid logging huge output
                span.set_attribute("response_time_seconds", response_time)
                span.set_attribute("estimated_input_tokens", input_tokens)
                span.set_attribute("output_tokens", output_tokens)
                span.set_attribute("total_tokens", total_tokens)
                span.set_attribute("tokens_per_second", total_tokens / response_time if response_time > 0 else 0)
                span.set_status(Status(StatusCode.OK))
                
                print(f"[Metrics] Response time: {response_time:.2f}s, Input tokens: ~{input_tokens}, Output tokens: {output_tokens}, Total: {total_tokens}")
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                span.set_attribute("response_time_seconds", response_time)
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                print(f"Agent error: {e}")
                return

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