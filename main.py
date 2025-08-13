"""
Entry point for the command-line interface (CLI) of the todo-agent.

This script demonstrates a typical setup for a stateful, conversational agent:
- Loads environment variables for API keys and configuration.
- Initializes tracing and observability integrations (Phoenix, Weave).
- Manages conversation history by saving and loading it from a JSON file.
- Creates an agent with a file-based storage backend (`JsonTodoStorage`).
- Runs a loop to interact with the user via the command line.

Additions in this version:
- A tracing processor that writes each finished trace (WITH SPANS) to logs/*.json (if supported by your Agents SDK).
- A per-turn fallback log writer so you still get local JSON even if the processor API isn’t available.
- RunConfig with workflow name + metadata so traces are clearly labeled.
"""

# Standard library imports
import os
import asyncio
import json
import datetime
from typing import Any

# Third-party imports
from dotenv import load_dotenv

# Local application imports
from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage

# OpenAI Agents SDK
from agents import Runner
from agents.run import RunConfig

# Optional tracing imports (SDK versions may differ); we handle gracefully.
_native_tracing_supported = False
try:
    # Common newer naming
    from agents import add_trace_processor  # type: ignore
    from agents.tracing import TracingProcessor  # type: ignore
    _native_tracing_supported = True
except Exception:
    try:
        # Older/alternate naming some builds used
        from agents import add_tracing_processor as add_trace_processor  # type: ignore
        from agents.tracing import TracingProcessor  # type: ignore
        _native_tracing_supported = True
    except Exception:
        _native_tracing_supported = False

# --- Initial Setup ---
load_dotenv()

# Ensure directories exist
DATA_DIR = "data"
LOG_DIR = "logs"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- Tracing: Local JSON export with full spans (native processor if available) ---
if _native_tracing_supported:
    from collections import defaultdict

    class FullTraceToJsonProcessor(TracingProcessor):
        """
        Collects *all* span data and writes a single enriched JSON per trace:
        {
          "trace": {... trace header ...},
          "spans": [ {... span 1 ...}, {... span 2 ...}, ... ]
        }
        """

        def __init__(self, directory: str = LOG_DIR):
            self.directory = directory
            # trace_id -> list[dict]
            self._spans = defaultdict(list)

        def _span_to_dict(self, span):
            # Prefer the most informative method exposed by the SDK
            if hasattr(span, "export") and callable(getattr(span, "export")):
                return span.export()
            if hasattr(span, "to_dict") and callable(getattr(span, "to_dict")):
                return span.to_dict()
            return getattr(span, "__dict__", {"warning": "span has no export/to_dict"})

        def _trace_to_dict(self, trace):
            if hasattr(trace, "export") and callable(getattr(trace, "export")):
                return trace.export()
            if hasattr(trace, "to_dict") and callable(getattr(trace, "to_dict")):
                return trace.to_dict()
            return getattr(trace, "__dict__", {"warning": "trace has no export/to_dict"})

        # Required by interface; no-ops except on_span_end/on_trace_end
        def on_trace_start(self, trace) -> None:
            pass

        def on_span_start(self, span) -> None:
            pass

        def on_span_end(self, span) -> None:
            try:
                span_dict = self._span_to_dict(span)
                # Ensure convenience keys exist for linking/hierarchy
                span_dict.setdefault("span_id", getattr(span, "span_id", None))
                span_dict.setdefault("parent_span_id", getattr(span, "parent_span_id", None))
                span_dict.setdefault("trace_id", getattr(span, "trace_id", None))
                self._spans[span_dict.get("trace_id")].append(span_dict)
            except Exception as e:
                print(f"(warning) span export failed: {e}")

        def on_trace_end(self, trace) -> None:
            try:
                tdict = self._trace_to_dict(trace)
                trace_id = tdict.get("id") or getattr(trace, "trace_id", "trace")
                payload = {
                    "trace": tdict,
                    "spans": self._spans.pop(trace_id, []),
                }
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                out_path = os.path.join(self.directory, f"{trace_id}_{ts}.json")
                with open(out_path, "w") as f:
                    json.dump(payload, f, indent=2)
                print(f"(saved local trace w/ spans) -> {out_path}")
            except Exception as e:
                print(f"(warning) failed to write local trace: {e}")

        def shutdown(self) -> None:
            pass

        def force_flush(self) -> None:
            pass

    # Register our processor in addition to the default OpenAI exporter.
    try:
        add_trace_processor(FullTraceToJsonProcessor())
        print("(info) Trace processor enabled: saving OpenAI traces (with spans) to logs/*.json")
    except Exception as e:
        _native_tracing_supported = False
        print(f"(warning) Could not register full-span trace processor: {e}")

# -----------------------------------------------------------------------------
# Session Management
# -----------------------------------------------------------------------------
SESSION_FILE = os.path.join(DATA_DIR, "session_default.json")
MAX_TURNS = 12  # Max *user* turns to keep in history to prevent token overflow.

def load_session() -> list[dict[str, Any]]:
    """Loads the message history from the session file."""
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_session(history: list[dict[str, Any]]) -> None:
    """Saves the message history to the session file."""
    with open(SESSION_FILE, "w") as f:
        json.dump({"history": history}, f, indent=2)

# --- Fallback per-turn logger (always on) ---
def write_fallback_turn_log(user_input: str, result: Any) -> None:
    """
    Writes a compact per-turn JSON log so you always have something local,
    even if the native trace processor isn't available.
    """
    try:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = os.path.join(LOG_DIR, f"turn_{ts}.json")
        payload = {
            "timestamp": ts,
            "input": user_input,
            "final_output": getattr(result, "final_output", None),
            # Try to capture any structured bits if the result exposes them:
            "result_summary": {
                "tool_calls": getattr(result, "tool_calls", None),
                "messages_count": len(getattr(result, "messages", []) or []),
            },
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"(saved turn log) -> {path}")
    except Exception as e:
        print(f"(warning) failed to write fallback turn log: {e}")

async def main():
    # Load the previous conversation history to maintain context.
    history = load_session()

    # Create the agent instance using the central factory.
    agent = create_agent(
        storage=JsonTodoStorage(),
        agent_name="To-Do Agent (CLI)"
    )
    print("To-Do Agent (CLI) is ready. Tracing is enabled. Type 'exit' to quit.")
    if not _native_tracing_supported:
        print("(info) Native trace processor not available in this SDK version; using fallback per-turn logs.")

    # Start the main interaction loop.
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # Add the new user message to the history.
        history.append({"role": "user", "content": user_input})

        # --- Context Window Management ---
        user_message_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
        if len(user_message_indices) > MAX_TURNS:
            start_index = user_message_indices[-MAX_TURNS]
            print(f"(Trimming conversation history to the last {MAX_TURNS} turns...)")
            history = history[start_index:]

        # --- Agent Execution ---
        result = await Runner.run(
            agent,
            input=history,
            run_config=RunConfig(
                workflow_name="To‑Do Agent (CLI)",
                trace_metadata={
                    "surface": "cli",
                    "session_file": SESSION_FILE,
                },
                # Set False to avoid storing prompts/outputs in traces
                trace_include_sensitive_data=True,
            ),
        )

        print("----" * 10)
        print(f"Agent: {result.final_output}")
        print("====" * 10)

        # Always write the per-turn fallback log (small and dependable)
        write_fallback_turn_log(user_input, result)

        # Replace history with the agent's updated, full history for the next turn.
        history = result.to_input_list()
        save_session(history)

if __name__ == "__main__":
    asyncio.run(main())
