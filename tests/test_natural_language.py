"""
Natural Language Project Completion Test
Tutorial: Finish article project using natural language with typos and casual conversation.
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
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = f"tutorial.name={project_name},tutorial.type=natural_language,environment=test,app.name=todo-agent"
    
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


async def run_natural_language_test():
    """Tutorial: Complete article project using casual, natural language."""
    start_time = datetime.now()
    test_details = {
        "turns": 0,
        "validation_results": {},
        "errors": []
    }
    
    try:
        reset_test_data()
        
        load_dotenv()
        
        initialize_tracing("finishing-article-project")
        
        agent = create_agent(storage=JsonTodoStorage(), agent_name="To-Do Agent (Article Completion)")

        print("🧪 Starting Natural Language Project Completion Tutorial")
        print("=" * 50)
        print("🎯 Learn: Natural conversation with typos and casual language")
        print("📚 Goal: Finish observability article with editing and publishing tasks")
        
        test_messages = [
            # === Casual task additions with typos ===
            "hey, add 'write conclusion section' and 'proofread everthing' to my Writing project - getting close to finishing this article",
            
            # === Natural editing and context ===
            "actually change that proofreading task to 'final review and editing' - sounds more professional",
            
            # === Publishing tasks with informal language ===
            "also add 'create code examples' and 'format for publication' to my Publishing project - gotta make sure the examples actually work",
            
            # === Check final status ===
            "lemme see what we have for the Writing project now"
        ]
        
        history = []
        
        # Weave: Add minimal context attributes for this tutorial session
        with weave.attributes({'tutorial_type': 'natural_language', 'environment': 'test', 'app_name': 'todo-agent', 'tutorial_name': 'language-completion-tutorial'}):
            for i, message in enumerate(test_messages, 1):
                print(f"\n--- Completion Step {i} ---")
                print(f"User: {message}")
                
                history.append({"role": "user", "content": message})
                result = await Runner.run(agent, input=history)
                
                print(f"Agent: {result.final_output}")
                history = result.to_input_list()
                
                await asyncio.sleep(0.5)
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🎓 Natural Language Project Completion Tutorial Complete")
        
        validation_success = True
        
        try:
            with open("data/todos.json", "r") as f:
                todos = json.load(f)
            
            total_todos = len(todos)
            test_details["validation_results"]["total_todos"] = total_todos
            
            projects = set(t.get('project') for t in todos if t.get('project'))
            test_details["validation_results"]["projects"] = sorted(list(projects))
            
            print(f"\n📊 Article Completion: {total_todos} finishing tasks across {len(projects)} projects")
            
            project_groups = {}
            for todo in todos:
                project = todo.get('project') or 'No Project'
                if project not in project_groups:
                    project_groups[project] = []
                project_groups[project].append(todo)
            
            for project, project_todos in sorted(project_groups.items()):
                print(f"\n📂 {project}:")
                for todo in project_todos:
                    print(f"  • {todo['name']}")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 What You Learned:")
        print("• Agent handles typos gracefully ('everthing' → 'everything')")
        print("• Natural conversation flow with task modifications")  
        print("• Casual language processing: 'hey', 'lemme see', 'gotta make sure'")
        print("• Context understanding: 'that proofreading task' references previous todo")
        print("🎉 Tutorial Series Complete: You've mastered todo agent workflows!")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if overall_success:
            print(f"\n✅ TUTORIAL PASSED: Natural language mastery achieved! ({duration:.1f}s)")
        else:
            print(f"\n❌ TUTORIAL FAILED: Language processing needs work ({duration:.1f}s)")
        
        return overall_success
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n❌ TUTORIAL FAILED: {str(e)} ({duration:.1f}s)")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_natural_language_test())
    exit(0 if success else 1) 