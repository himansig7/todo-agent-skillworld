import os
import json
import asyncio
import datetime
from typing import Any
from collections import defaultdict
from dotenv import load_dotenv

from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage

from agents import Runner
from agents.run import RunConfig

# Load environment variables (including OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI SDK for enriching response spans
from openai import OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Paths
DATA_DIR = "data"
LOG_DIR = "logs"
SESSION_FILE = os.path.join(DATA_DIR, "session_default.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Register tracing processor if supported
try:
    from agents import add_trace_processor
    from agents.tracing import TracingProcessor

    class EnrichedTraceProcessor(TracingProcessor):
        def __init__(self, directory: str = LOG_DIR):
            self.directory = directory
            self._spans = defaultdict(list)

        def on_span_end(self, span):
            try:
                span_dict = span.export() if hasattr(span, "export") else span.to_dict()
                data = span_dict.get("span_data", {})

                # If it's a response span, enrich it
                if data.get("type") == "response" and "response_id" in data:
                    try:
                        response = openai_client.responses.retrieve(data["response_id"])
                        data["model"] = response.model
                        data["model"] = response.model

                        # Convert usage to plain dict (fixes serialization crash)
                        raw_usage = getattr(response, "usage", None)
                        if raw_usage:
                            data["usage"] = {
                                "input_tokens": getattr(raw_usage, "prompt_tokens", None),
                                "output_tokens": getattr(raw_usage, "completion_tokens", None),
                                "total_tokens": getattr(raw_usage, "total_tokens", None),
                            }

                        span_dict["span_data"] = data
                    except Exception as e:
                        data["enrich_error"] = str(e)

                self._spans[span_dict.get("trace_id")].append(span_dict)
            except Exception as e:
                print(f"(warning) span export failed: {e}")

        def on_trace_end(self, trace):
            try:
                trace_dict = trace.export() if hasattr(trace, "export") else trace.to_dict()
                trace_id = trace_dict.get("id") or getattr(trace, "trace_id", "trace")
                payload = {
                    "trace": trace_dict,
                    "spans": self._spans.pop(trace_id, []),
                }
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                out_path = os.path.join(self.directory, f"{trace_id}_{ts}.json")
                with open(out_path, "w") as f:
                    json.dump(payload, f, indent=2)
                print(f"(saved enriched trace) -> {out_path}")
            except Exception as e:
                print(f"(warning) failed to write enriched trace: {e}")

        def on_trace_start(self, trace): pass
        def on_span_start(self, span): pass
        def shutdown(self): pass
        def force_flush(self): pass

    add_trace_processor(EnrichedTraceProcessor())
except Exception as e:
    print(f"(warning) could not enable enriched tracing: {e}")

# Session helpers
MAX_TURNS = 12

def load_session() -> list[dict[str, Any]]:
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f).get("history", [])
    except Exception:
        return []

def save_session(history: list[dict[str, Any]]):
    with open(SESSION_FILE, "w") as f:
        json.dump({"history": history}, f, indent=2)

async def main():
    history = load_session()

    agent = create_agent(JsonTodoStorage(), agent_name="To-Do Agent (CLI)")
    print("To-Do Agent (CLI) is ready. Tracing is enabled. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        history.append({"role": "user", "content": user_input})

        user_indices = [i for i, msg in enumerate(history) if msg.get("role") == "user"]
        if len(user_indices) > MAX_TURNS:
            history = history[user_indices[-MAX_TURNS]:]
            print(f"(Trimming to last {MAX_TURNS} turns...)")

        result = await Runner.run(
            agent,
            input=history,
            run_config=RunConfig(
                workflow_name="To‑Do Agent (CLI)",
                trace_metadata={"surface": "cli", "session_file": SESSION_FILE},
                trace_include_sensitive_data=True,
            ),
        )

        print("----" * 10)
        print(f"Agent: {result.final_output}")
        print("====" * 10)

        history = result.to_input_list()
        save_session(history)

if __name__ == "__main__":
    asyncio.run(main())
