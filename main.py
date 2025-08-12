import os
import asyncio
import json
from typing import Any, Dict, List

from dotenv import load_dotenv

from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow, task  # ← use task, not step
from opentelemetry import trace

SESSION_FILE = "data/session_default.json"
MAX_TURNS = 12

# ------------------ helpers ------------------
def load_session() -> list:
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("history", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_session(history: list):
    os.makedirs(os.path.dirname(SESSION_FILE), exist_ok=True)
    with open(SESSION_FILE, "w") as f:
        json.dump({"history": history}, f, indent=2)

def trim_history(history: List[Dict[str, Any]], max_user_turns: int) -> List[Dict[str, Any]]:
    user_ix = [i for i, m in enumerate(history) if m.get("role") == "user"]
    if len(user_ix) > max_user_turns:
        start = user_ix[-max_user_turns]
        print(f"(Trimming conversation history to the last {max_user_turns} turns...)")
        return history[start:]
    return history

def _as_text(x: Any) -> str:
    if isinstance(x, str):
        return x
    try:
        return json.dumps(x, ensure_ascii=False)
    except Exception:
        return str(x)

def flatten_for_logging(history: List[Dict[str, Any]], limit: int = 20) -> List[str]:
    recent = history[-limit:]
    return [f"{m.get('role','?')}: {_as_text(m.get('content',''))}" for m in recent]

def annotate_span(attrs: Dict[str, Any]):
    span = trace.get_current_span()
    if not span or not hasattr(span, "set_attribute"):
        return
    for k, v in attrs.items():
        if isinstance(v, (str, bool, int, float, bytes)) or v is None:
            span.set_attribute(k, v)
        elif isinstance(v, (list, tuple)):
            span.set_attribute(k, [v2 if isinstance(v2, (str, bool, int, float, bytes)) or v2 is None else _as_text(v2) for v2 in v])
        else:
            span.set_attribute(k, _as_text(v))

# ------------------ traced tasks/workflows ------------------
@task(name="agent_turn")
async def run_agent_turn(agent, history: list):
    from agents import Runner
    result = await Runner.run(agent, input=history)

    # attach optional metrics/usage if your Runner sets them
    metrics = getattr(result, "metrics", {}) if hasattr(result, "metrics") else {}
    annotate_span({
        "todo_agent.result.summary": _as_text(getattr(result, "final_output", "")[:500]),
        "todo_agent.result.metrics": metrics,
    })
    return result

@workflow(name="todo_agent_execution")
async def agent_run_workflow(agent, history: list, user_input: str, prompt_preview: List[str]):
    annotate_span({
        "gen_ai.last_user_message": user_input,
        "gen_ai.prompt_preview": prompt_preview,       # list[str] → OTel-safe
        "gen_ai.prompt_preview_size": len(prompt_preview),
    })
    result = await run_agent_turn(agent, history)

    # If your result has token usage, attach here:
    usage = getattr(result, "usage", None)
    if usage is not None:
        annotate_span({"gen_ai.usage": usage})

    return result

# ------------------ main ------------------
async def main():
    load_dotenv()  # ← ensure env vars (TRACELOOP_API_KEY, etc.) are loaded
    Traceloop.init(app_name="todo-agent-cli", disable_batch=True)  # export to Traceloop

    history = load_session()
    agent = create_agent(storage=JsonTodoStorage(), agent_name="To-Do Agent (CLI)")

    print("To-Do Agent (CLI) is ready. Tracing is enabled. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        history.append({"role": "user", "content": user_input})
        history = trim_history(history, MAX_TURNS)

        # Make a SAFE, string-only preview for telemetry
        prompt_preview = flatten_for_logging(history, limit=20)

        result = await agent_run_workflow(
            agent=agent,
            history=history,          # original objects go to your agent
            user_input=user_input,
            prompt_preview=prompt_preview,  # strings-only for span attrs
        )

        print("----" * 10)
        print(f"Agent: {getattr(result, 'final_output', '')}")
        print("====" * 10)

        if hasattr(result, "to_input_list"):
            history = result.to_input_list()
        else:
            history.append({"role": "assistant", "content": getattr(result, "final_output", "")})

        save_session(history)

if __name__ == "__main__":
    asyncio.run(main())
