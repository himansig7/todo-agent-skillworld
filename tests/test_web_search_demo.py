"""
Web Search Demo Test
Demonstrates how AI agents use web search to turn vague requests into actionable tasks.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from phoenix.otel import register
import weave
from agents import Runner, Agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage


def reset_test_data():
    """Reset todos and session data for clean test runs."""
    os.makedirs("data", exist_ok=True)
    
    with open("data/todos.json", "w") as f:
        json.dump([], f)
    
    with open("data/session_default.json", "w") as f:
        json.dump({"history": []}, f)
    
    print("🔄 Data reset - starting with clean slate")


def log_test_result(test_name, start_time, end_time, success, details):
    """Log structured test results to file."""
    os.makedirs("tests/logs", exist_ok=True)
    
    result = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "success": success,
        "details": details
    }
    
    log_file = "tests/logs/test_results.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")
    
    print(f"📊 Test result logged to {log_file}")


async def run_web_search_demo():
    """Run web search demo showing agent's multi-turn research capabilities."""
    start_time = datetime.now()
    test_details = {
        "turns": 0,
        "validation_results": {},
        "errors": []
    }
    
    try:
        reset_test_data()
        
        load_dotenv()
        
        os.environ["OPENAI_TRACING_ENABLED"] = "1"
        os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
        register(project_name="todo-agent-test-websearch", auto_instrument=True)
        weave.init("todo-agent-test-websearch")

        agent = create_agent(agent_name="To-Do Agent (AI Research Test)")
        
        print("🧪 Starting Web Search Demo")
        print("=" * 50)
        print("🎯 Goal: Watch the agent research AI engineering practices and create technical writing tasks")
        print("=" * 50)
        
        test_messages = [
            # === Initial Brainstorming Request ===
            "Add 'Plan AI agents article' to my Writing project with description 'Write tutorial article about building AI agents - need ideas for structure and key topics'",
            "I'm writing an article about AI agents but I'm stuck on what to cover. Can you help me brainstorm the main topics I should include? Maybe search for what people are asking about AI agents lately",
            
            # === Idea Generation and Suggestions ===
            "Those are good ideas! Can you look up what specific challenges developers face when building their first AI agent? I want to make sure I'm addressing real pain points",
            "Based on what you found, can you suggest some specific sections I should write? Like what would be the most helpful topics to cover first",
            
            # === Content Structure Help ===
            "I'm thinking about covering observability tools but I'm not sure which ones are worth mentioning. Can you research what tracing tools are popular with AI developers right now?",
            "That's helpful! Can you suggest how I should organize these topics? Should I create separate tasks for each tool or group them somehow?",
            
            # === Implementation Examples ===
            "I want to include some practical examples but I'm not sure what would be most useful. Can you look up what kind of code examples developers find most helpful in AI tutorials?",
            "Show me what tasks you've suggested so far - I want to see if we're covering the right topics for my article"
        ]
        
        history = []
        
        for turn, message in enumerate(test_messages):
            print(f"\n--- Turn {turn + 1} ---")
            print(f"User: {message}")
            
            history.append({"role": "user", "content": message})
            result = await Runner.run(agent, input=history)
            
            print(f"Agent: {result.final_output}")
            history = result.to_input_list()
            
            await asyncio.sleep(0.5)
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🧪 Web Search Demo Complete")
        
        validation_success = True
        
        try:
            with open("data/todos.json", "r") as f:
                todos = json.load(f)
            
            total_todos = len(todos)
            test_details["validation_results"]["total_todos"] = total_todos
            
            projects = set(t.get('project') for t in todos if t.get('project'))
            test_details["validation_results"]["projects"] = sorted(list(projects))
            
            # Basic sanity check - did the agent create any todos?
            if total_todos == 0:
                validation_success = False
                test_details["errors"].append("No todos were created during the test")
            
            print(f"\n📝 Complete Article Planning & Ideas:")
            for i, todo in enumerate(todos, 1):
                status_map = {"Completed": "✅", "In Progress": "⏳", "Not Started": "⬜️"}
                status_icon = status_map.get(todo.get('status'), '❓')
                project_tag = f"[{todo.get('project', 'No Project')}]" if todo.get('project') else ""
                desc_preview = f"\n   💡 {todo['description'][:60]}..." if todo.get('description') else ""
                print(f"{i}. {status_icon} {todo['name']} {project_tag}{desc_preview}")
            
            print(f"\n📊 Final Results: {total_todos} todos across {len(projects)} projects")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 Key Learning Points:")
        print("• Agent helps with brainstorming and idea generation rather than doing all the work")
        print("• Web search → idea suggestions → task creation pipeline")
        print("• Transforms vague writing blocks into specific, actionable planning tasks")
        print("• Multi-tool coordination: research for inspiration then suggest structure")
        print("• Agent maintains context across brainstorming sessions while staying collaborative")
        print("• **Observability over validation**: Quality evaluation happens in your tracing dashboards")
        print("🔍 Check your tracing dashboards - that's where you analyze the web search + brainstorming workflow!")
        
        end_time = datetime.now()
        log_test_result("web_search_demo", start_time, end_time, overall_success, test_details)
        
        if overall_success:
            print(f"\n✅ TEST PASSED: Web Search Demo")
        else:
            print(f"\n❌ TEST FAILED: Web Search Demo")
            for error in test_details["errors"]:
                print(f"   • {error}")
        
        return overall_success
        
    except Exception as e:
        end_time = datetime.now()
        test_details["errors"].append(str(e))
        log_test_result("web_search_demo", start_time, end_time, False, test_details)
        print(f"\n❌ TEST FAILED: Web Search Demo - {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_web_search_demo())
    exit(0 if success else 1) 