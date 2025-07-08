"""
Basic Todo Operations Test
Demonstrates fundamental AI agent capabilities: CRUD operations, bulk tasks, and project management.
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


async def run_basic_operations_test():
    """Run basic todo operations test with varied tool usage patterns."""
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
        register(project_name="todo-agent-test-basic", auto_instrument=True)
        weave.init("todo-agent-test-basic")
        
        agent = create_agent(agent_name="To-Do Agent (Basic Ops Test)")

        print("🧪 Starting Basic Operations Test")
        print("=" * 50)
        
        test_messages = [
            # === Natural Planning Phase ===
            "add 'write ai article' to my content project with description 'tutorial about building ai agents for developers'",
            "i need to add some more stuff to content project: 'research agent patterns' with description 'look at different ways to build agents', 'document our tools' with description 'explain how the crud tools work', and 'make some diagrams' with description 'update mermaid diagrams with new flows'",
            
            # === Status Updates (Natural Language) ===
            "i finished researching the agent patterns and took good notes on tool design. mark that task as completed. also started working on diagrams yesterday so set that to in progress and add note 'got basic flow done, working on tool interactions'",
            "show me what i have in content project right now",
            
            # === Writing Phase ===
            "add these to Writing project: 'draft intro' with description 'hook readers and explain what they will learn', 'write tools section' with description 'explain function decorators and schemas', and 'cover observability' with description 'openai tracing, phoenix, and weave setup'",
            "just finished the intro and it turned out good. mark 'draft intro' as done and update description to 'finished 400 word intro with clear examples'",
            
            # === Publication Phase ===
            "add Publication project with these: 'review everything' with description 'check code examples and make sure it all works', 'prep code samples' with description 'clean up github repo and readme', and 'submit article' with description 'format for publication and schedule'",
            "finished reviewing everthing and fixed some code bugs. mark that task complete and start working on code samples",
            
            # === Cleanup ===
            "show me completed tasks and delete them to clean up my list",
            "show me current workload by project"
        ]
        
        history = []
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Turn {i} ---")
            print(f"User: {message}")
            
            history.append({"role": "user", "content": message})
            result = await Runner.run(agent, input=history)
            
            print(f"Agent: {result.final_output}")
            history = result.to_input_list()
            
            await asyncio.sleep(0.5)
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🧪 Basic Operations Test Complete")
        
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
            
            print(f"\n📋 Article Creation Project Portfolio:")
            project_groups = {}
            for todo in todos:
                project = todo.get('project') or 'No Project'
                if project not in project_groups:
                    project_groups[project] = []
                project_groups[project].append(todo)
            
            for project, project_todos in sorted(project_groups.items()):
                print(f"\n📂 {project} ({len(project_todos)} tasks):")
                for todo in project_todos:
                    status_map = {"Completed": "✅", "In Progress": "⏳", "Not Started": "⬜️"}
                    status_icon = status_map.get(todo.get('status'), '❓')
                    desc_preview = f" - {todo['description'][:60]}..." if todo.get('description') else ""
                    print(f"  {status_icon} {todo['name']}{desc_preview}")
            
            print(f"\n📊 Final Results: {total_todos} todos across {len(projects)} projects")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 Key Learning Points:")
        print("• Demonstrates natural language processing with casual, unstructured input")
        print("• Agent handles typos, misspellings, and informal language gracefully")
        print("• Shows Content → Writing → Publication workflow with realistic task progression")
        print("• Concise task names and descriptions mirror real human productivity patterns")
        print("• Agent maintains context across informal, multi-turn conversations")
        print("• **Observability over validation**: Use tracing dashboards to evaluate quality, not hardcoded checks")
        print("🔍 Check your tracing dashboards - that's where the real evaluation happens!")
        
        end_time = datetime.now()
        log_test_result("basic_operations", start_time, end_time, overall_success, test_details)
        
        if overall_success:
            print(f"\n✅ TEST PASSED: Basic Operations Test")
        else:
            print(f"\n❌ TEST FAILED: Basic Operations Test")
            for error in test_details["errors"]:
                print(f"   • {error}")
        
        return overall_success
        
    except Exception as e:
        end_time = datetime.now()
        test_details["errors"].append(str(e))
        log_test_result("basic_operations", start_time, end_time, False, test_details)
        print(f"\n❌ TEST FAILED: Basic Operations Test - {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_basic_operations_test())
    exit(0 if success else 1) 