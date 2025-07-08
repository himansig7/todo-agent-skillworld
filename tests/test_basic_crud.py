"""
Basic CRUD Operations Test
Tutorial: Learn core todo app operations while planning an observability article.
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
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"tutorial.name={project_name},tutorial.type=basic_crud,environment=test,app.name=todo-agent"
    
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


async def run_basic_crud_test():
    """Tutorial: Set up article structure while learning essential todo operations."""
    start_time = datetime.now()
    test_details = {
        "turns": 0,
        "validation_results": {},
        "errors": []
    }
    
    try:
        reset_test_data()
        
        load_dotenv()
        
        initialize_tracing("writing-article-foundation")
        
        agent = create_agent(storage=JsonTodoStorage(), agent_name="To-Do Agent (Article Planning)")

        print("🧪 Starting Basic CRUD Tutorial")
        print("=" * 50)
        print("🎯 Learn: Essential todo operations while planning an article")
        print("📚 Foundation: Set up observability platforms comparison article")
        
        test_messages = [
            # === Article Structure Setup ===
            "Add 'Write introduction to agent observability' to my Writing project with description 'Explain why observability matters for AI agents'",
            
            # === Platform Sections ===
            "Add these platform sections to Writing project: 'Create OpenAI platform overview', 'Write Arize Phoenix analysis', and 'Add Weights & Biases Weave section'",
            
            # === Progress Check ===
            "Show me my Writing project tasks",
            
            # === Status Updates ===
            "Mark 'Create OpenAI platform overview' as in progress since I'm starting research on that section",
            
            # === Description Enhancement ===
            "Update the description for 'Write Arize Phoenix analysis' to include 'Focus on cloud deployment benefits and trace visualization features'",
            
            # === Final Completion ===
            "Mark 'Write introduction to agent observability' as completed and add note 'Finished 300-word intro explaining the importance of observability'"
        ]
        
        history = []
        
        # Weave: Add minimal context attributes for this tutorial session  
        with weave.attributes({'tutorial_type': 'basic_crud', 'environment': 'test', 'app_name': 'todo-agent', 'tutorial_name': 'writing-article-foundation'}):
            for i, message in enumerate(test_messages, 1):
                print(f"\n--- Tutorial Step {i} ---")
                print(f"User: {message}")
                
                history.append({"role": "user", "content": message})
                result = await Runner.run(agent, input=history)
                
                print(f"Agent: {result.final_output}")
                history = result.to_input_list()
                
                await asyncio.sleep(0.5)
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🎓 Basic CRUD Tutorial Complete")
        
        validation_success = True
        
        try:
            with open("data/todos.json", "r") as f:
                todos = json.load(f)
            
            total_todos = len(todos)
            completed_todos = len([t for t in todos if t and t.get('status') == 'Completed'])
            in_progress_todos = len([t for t in todos if t and t.get('status') == 'In Progress'])
            test_details["validation_results"]["total_todos"] = total_todos
            test_details["validation_results"]["completed_todos"] = completed_todos
            test_details["validation_results"]["in_progress_todos"] = in_progress_todos
            
            print(f"\n📊 Article Foundation: {total_todos} sections planned, {completed_todos} completed, {in_progress_todos} in progress")
            
            for todo in todos:
                if not todo or not isinstance(todo, dict):
                    continue
                    
                status = todo.get('status', 'Not Started')
                name = todo.get('name', 'Unnamed Task')
                
                if status == 'Completed':
                    status_emoji = "✅"
                elif status == 'In Progress':
                    status_emoji = "🚧"
                else:
                    status_emoji = "📝"
                    
                print(f"  {status_emoji} {name}")
                if todo.get('project'):
                    print(f"    Project: {todo['project']}")
                if todo.get('description'):
                    desc = todo['description']
                    print(f"    Description: {desc[:60]}{'...' if len(desc) > 60 else ''}")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 What You Learned:")
        print("• Create structured writing tasks with clear descriptions")
        print("• Organize tasks by project for better workflow")
        print("• Update task status (Not Started → In Progress → Completed)")
        print("• Enhance descriptions and add progress notes")
        print("• Comprehensive CRUD operations on all todo fields")
        print("🚀 Next: Try the web search tutorial to research platform details!")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if overall_success:
            print(f"\n✅ TUTORIAL PASSED: Article foundation ready! ({duration:.1f}s)")
        else:
            print(f"\n❌ TUTORIAL FAILED: Check setup and try again ({duration:.1f}s)")
        
        return overall_success
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n❌ TUTORIAL FAILED: {str(e)} ({duration:.1f}s)")
        return False




if __name__ == "__main__":
    success = asyncio.run(run_basic_crud_test())
    exit(0 if success else 1) 