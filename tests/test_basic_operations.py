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
            "Add 'Buy groceries' with description 'Get milk, bread, and fresh vegetables'",
            "Add 'Walk the dog' to my list",
            "Add these tasks to my Work project: 'Review budget' with description 'Analyze Q4 expenses', 'Schedule team meeting', and 'Update project timeline'",
            "Show me all my Work tasks, then update the 'Schedule team meeting' task to 'In Progress' and add description 'Book conference room and send invites'",
            "Add these personal tasks: 'Call mom', 'Schedule dentist appointment', and 'Plan weekend trip'",
            "Show me all my personal tasks, then mark 'Call mom' as completed and set 'Plan weekend trip' to 'In Progress' with description 'Research destinations and book hotel'",
            "Show me all completed tasks, then delete them to clean up my list",
            "Show me my complete todo list organized by project"
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
            test_details["validation_results"]["total_todos_remaining"] = total_todos
            print(f"✅ Validation: {total_todos} todos remaining after test")
            
            projects = set(t.get('project') for t in todos if t.get('project'))
            test_details["validation_results"]["projects"] = sorted(list(projects))
            print(f"✅ Validation: {len(projects)} projects created: {sorted(list(projects))}")
            
            status_counts = {
                "Not Started": len([t for t in todos if t.get('status') == 'Not Started']),
                "In Progress": len([t for t in todos if t.get('status') == 'In Progress']),
            }
            test_details["validation_results"]["status_counts"] = status_counts
            print(f"✅ Validation: Status counts - {status_counts}")
            
            with_desc = len([t for t in todos if t.get('description')])
            without_desc = len([t for t in todos if not t.get('description')])
            test_details["validation_results"]["todos_with_descriptions"] = with_desc
            test_details["validation_results"]["todos_without_descriptions"] = without_desc
            print(f"✅ Validation: {with_desc} with descriptions, {without_desc} without")
            
            # Validation thresholds
            if total_todos < 5:
                validation_success = False
                test_details["errors"].append(f"Expected at least 5 remaining todos, got {total_todos}")
            
            if len(projects) < 2:
                validation_success = False
                test_details["errors"].append(f"Expected at least 2 projects, got {len(projects)}")

            if status_counts["In Progress"] < 2:
                validation_success = False
                test_details["errors"].append(f"Expected at least 2 'In Progress' todos, got {status_counts['In Progress']}")
            
            print(f"\n📋 Final Todo Organization:")
            project_groups = {}
            for todo in todos:
                project = todo.get('project') or 'No Project'
                if project not in project_groups:
                    project_groups[project] = []
                project_groups[project].append(todo)
            
            for project, project_todos in sorted(project_groups.items()):
                print(f"\n📂 {project}:")
                for todo in project_todos:
                    status_map = {"Completed": "✅", "In Progress": "⏳", "Not Started": "⬜️"}
                    status_icon = status_map.get(todo.get('status'), '❓')
                    desc_preview = f" - {todo['description'][:50]}..." if todo.get('description') else ""
                    print(f"  {status_icon} {todo['name']}{desc_preview}")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 Key Learning Points:")
        print("• Agent handles varied tool usage patterns (single vs multi-tool operations)")
        print("• Multi-tool workflows: Read → Update, Read → Delete")
        print("• Bulk operations with different complexity levels")
        print("• Project organization and task management")
        print("• Agent maintains context across multi-turn operations")
        print("🔍 Check your tracing dashboard to see the varied tool call patterns!")
        
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