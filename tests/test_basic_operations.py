"""
Basic Todo Operations Test
Demonstrates fundamental AI agent capabilities: CRUD operations, bulk tasks, and project management.

This test shows:
1. Creating todos with varied patterns (title-only vs detailed descriptions)
2. Bulk operations (creating multiple todos at once)
3. Multi-tool workflows (read → update, read → delete)
4. Project organization and management
5. Basic validation to ensure the agent works correctly

Perfect for AI Engineering 101 - shows core agent functionality with varied tool usage patterns.
"""

import os
import sys
import warnings
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic.json_schema import PydanticJsonSchemaWarning
from phoenix.otel import register
import weave
from agents import Runner

# Setup imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.todo_agent import agent


async def run_basic_operations_test():
    """
    Run basic todo operations test with varied tool usage patterns.
    """
    # Setup tracing (same as main.py)
    load_dotenv()
    warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)
    
    os.environ["OPENAI_TRACING_ENABLED"] = "1"
    os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
    register(project_name="todo-agent-test-basic", auto_instrument=True)
    weave.init("todo-agent-test-basic")
    
    print("🧪 Starting Basic Operations Test")
    print("=" * 50)
    
    # Test conversation - varied tool usage patterns
    test_messages = [
        # Single-tool operations: Basic create
        "Add 'Buy groceries' with description 'Get milk, bread, and fresh vegetables'",
        "Add 'Walk the dog' to my list",  # Title-only
        
        # Multi-tool bulk operations: Create multiple todos with projects
        "Add these tasks to my Work project: 'Review budget' with description 'Analyze Q4 expenses', 'Schedule team meeting', and 'Update project timeline'",
        
        # Read then update workflow
        "Show me all my Work tasks, then update the 'Schedule team meeting' task to include description 'Book conference room and send invites'",
        
        # Create more variety for multi-tool operations
        "Add these personal tasks: 'Call mom', 'Schedule dentist appointment', and 'Plan weekend trip'",
        
        # Read then update multiple items
        "Show me all my personal tasks, then mark 'Call mom' as completed and update 'Plan weekend trip' to include description 'Research destinations and book hotel'",
        
        # Read then delete workflow
        "Show me all completed tasks, then delete them to clean up my list",
        
        # Final read to show organized results
        "Show me my complete todo list organized by project"
    ]
    
    history = []
    
    # Run conversation with agent
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {message}")
        
        # Add user message to history
        history.append({"role": "user", "content": message})
        
        # Run the agent
        result = await Runner.run(agent, input=history)
        
        print(f"Agent: {result.final_output}")
        
        # Update history with agent response
        history = result.to_input_list()
        
        # Small delay for readability
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 50)
    print("🧪 Basic Operations Test Complete")
    
    # Simple validation - verify varied tool usage worked
    try:
        with open("data/todos.json", "r") as f:
            todos = json.load(f)
        
        print(f"✅ Validation: {len(todos)} todos created")
        
        # Check for project organization
        projects = set(t.get('project') for t in todos if t.get('project'))
        print(f"✅ Validation: {len(projects)} projects created: {sorted(list(projects))}")
        
        # Check for completion status variety
        completed_count = len([t for t in todos if t.get('completed')])
        pending_count = len([t for t in todos if not t.get('completed')])
        print(f"✅ Validation: {completed_count} completed, {pending_count} pending tasks")
        
        # Check for description patterns
        with_desc = len([t for t in todos if t.get('description')])
        without_desc = len([t for t in todos if not t.get('description')])
        print(f"✅ Validation: {with_desc} todos with descriptions, {without_desc} without")
        
        # Show final organized state
        print(f"\n📋 Final Todo Organization:")
        project_groups = {}
        for todo in todos:
            project = todo.get('project', 'No Project')
            if project not in project_groups:
                project_groups[project] = []
            project_groups[project].append(todo)
        
        for project, project_todos in sorted(project_groups.items()):
            print(f"\n📂 {project}:")
            for todo in project_todos:
                status = "✅" if todo.get('completed') else "⏳"
                desc_preview = f" - {todo['description'][:50]}..." if todo.get('description') else ""
                print(f"  {status} {todo['name']}{desc_preview}")
        
    except FileNotFoundError:
        print("❌ No todos.json file found")
    
    print(f"\n🎓 Key Learning Points:")
    print("• Agent handles varied tool usage patterns (single vs multi-tool operations)")
    print("• Multi-tool workflows: Read → Update, Read → Delete")
    print("• Bulk operations with different complexity levels")
    print("• Project organization and task management")
    print("• Agent maintains context across multi-turn operations")
    print("🔍 Check your tracing dashboard to see the varied tool call patterns!")


if __name__ == "__main__":
    asyncio.run(run_basic_operations_test()) 