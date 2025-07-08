"""
Web Search Platform Research Test
Tutorial: Research observability platforms and convert findings into writing tasks.
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




def initialize_tracing(project_name: str):
    """Initialize tracing with graceful error handling."""
    os.environ["OPENAI_TRACING_ENABLED"] = "1"
    os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
    
    # Phoenix: Add minimal custom resource attributes via environment variable
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"tutorial.name={project_name},tutorial.type=web_search,environment=test,app.name=todo-agent"
    
    try:
        register(project_name=project_name, auto_instrument=True)
        print(f"✅ Phoenix tracing initialized for: {project_name}")
    except Exception as e:
        print(f"⚠️  Phoenix tracing failed: {e}")
    
    if not weave.get_client():
        try:
            weave.init(project_name)
            print(f"✅ Weave tracing initialized for: {project_name}")
        except Exception as e:
            print(f"⚠️  Weave tracing failed (continuing without Weave): {e}")


async def run_web_search_test():
    """Tutorial: Research platforms and create structured writing tasks."""
    start_time = datetime.now()
    test_details = {
        "turns": 0,
        "validation_results": {},
        "errors": []
    }
    
    try:
        reset_test_data()
        
        load_dotenv()
        
        initialize_tracing("observability-platform-research")
        
        agent = create_agent(storage=JsonTodoStorage(), agent_name="To-Do Agent (Platform Research)")

        print("🧪 Starting Web Search Platform Research Tutorial")
        print("=" * 50)
        print("🎯 Learn: Research workflow → structured task creation")
        print("📚 Goal: Compare observability platforms for AI agents")
        
        test_messages = [
            # === Platform Research (3 searches with guided responses) ===
            "Search for 'Arize Phoenix Cloud main benefits agent observability' and give me a brief 2 paragraph summary",
            
            "Search for 'Weights & Biases Weave main benefits agent tracing' and give me a brief 2 paragraph summary",
            
            "Search for 'OpenAI platform observability features benefits' and give me a brief 2 paragraph summary",
            
            # === Convert Research to Tasks ===
            "Based on this research, please add writing tasks to my 'Platform Comparison' project for comparing these platforms - I need specific tasks I can work on"
        ]
        
        history = []
        
        # Weave: Add minimal context attributes for this tutorial session
        with weave.attributes({'tutorial_type': 'web_search', 'environment': 'test', 'app_name': 'todo-agent', 'tutorial_name': 'platform-research-tutorial'}):
            for i, message in enumerate(test_messages, 1):
                print(f"\n--- Research Step {i} ---")
                print(f"User: {message}")
                
                history.append({"role": "user", "content": message})
                result = await Runner.run(agent, input=history)
                
                print(f"Agent: {result.final_output}")
                history = result.to_input_list()
                
                await asyncio.sleep(0.5)
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🎓 Platform Research Tutorial Complete")
        
        validation_success = True
        
        try:
            with open("data/todos.json", "r") as f:
                todos = json.load(f)
            
            total_todos = len(todos)
            test_details["validation_results"]["total_todos"] = total_todos
            
            # Research tutorial should create at least 3 writing tasks
            if total_todos < 3:
                validation_success = False
                error_msg = f"Expected at least 3 writing tasks from research, got {total_todos}"
                test_details["errors"].append(error_msg)
                print(f"❌ {error_msg}")
            
            print(f"\n📊 Research Results: {total_todos} writing tasks created from platform research")
            
            for i, todo in enumerate(todos, 1):
                if not todo or not isinstance(todo, dict):
                    continue
                name = todo.get('name', 'Unnamed Task')
                print(f"{i}. {name}")
                if todo.get('description'):
                    print(f"   Description: {todo['description']}")
                if todo.get('project'):
                    print(f"   Project: {todo['project']}")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 What You Learned:")
        print("• Web search integration for research workflows")  
        print("• Converting research findings into structured writing tasks")
        print("• Multi-platform comparison methodology")
        print("• Research stays in chat history, todos are actionable tasks")
        print("🚀 Next: Try the natural language tutorial for project finishing touches!")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if overall_success:
            print(f"\n✅ TUTORIAL PASSED: Platform research complete! ({duration:.1f}s)")
        else:
            print(f"\n❌ TUTORIAL FAILED: Research workflow needs attention ({duration:.1f}s)")
        
        return overall_success
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n❌ TUTORIAL FAILED: {str(e)} ({duration:.1f}s)")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_web_search_test())
    exit(0 if success else 1) 