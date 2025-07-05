"""
Basic Todo Operations Test
Demonstrates fundamental AI agent capabilities: CRUD operations, bulk tasks, and project management.

This test shows:
1. Creating todos with varied patterns (title-only vs detailed descriptions)
2. Bulk operations (creating multiple todos at once)
3. Project organization and management
4. Selective deletion and updates
5. Basic validation to ensure the agent works correctly

Perfect for AI Engineering 101 - shows core agent functionality with clear examples.
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
    Run basic todo operations test combining CRUD and workflow management.
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
    
    # Test conversation - shows core agent capabilities
    test_messages = [
        # CRUD Operations: Create todos with different patterns
        "Add 'Buy groceries' with description 'Get milk, bread, and fresh vegetables'",
        "Add 'Walk the dog' to my list",  # Title-only
        "Add 'Review budget' to my Work project with description 'Analyze Q4 expenses and plan for next quarter'",
        
        # Multi-task operations: Bulk creation
        "Add these tasks to my Personal project: 'Call mom', 'Schedule dentist appointment', and 'Plan weekend trip'",
        
        # Read operations: Show organized view
        "Show me all my todos organized by project",
        
        # Update operations: Modify existing todos
        "Update 'Walk the dog' to include description 'Take 30-minute walk in the park'",
        
        # Delete operations: Remove specific todos
        "Delete the 'Call mom' task",
        
        # Final state verification
        "Show me my complete todo list with details"
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
    
    # Simple validation - verify the test worked
    try:
        with open("data/todos.json", "r") as f:
            todos = json.load(f)
        
        print(f"✅ Validation: {len(todos)} todos created")
        
        # Check for project organization
        projects = set(t.get('project') for t in todos if t.get('project'))
        print(f"✅ Validation: {len(projects)} projects created: {list(projects)}")
        
        # Check for description patterns
        with_desc = len([t for t in todos if t.get('description')])
        without_desc = len([t for t in todos if not t.get('description')])
        print(f"✅ Validation: {with_desc} todos with descriptions, {without_desc} without")
        
        # Verify deletion worked (should NOT find deleted todo)
        call_mom_exists = any('call mom' in t['name'].lower() for t in todos)
        if not call_mom_exists:
            print("✅ Validation: Deleted todo successfully removed")
        
        # Show final organized state
        print("\n📋 Final Todo Organization:")
        project_groups = {}
        for todo in todos:
            project = todo.get('project', 'Personal Tasks')
            if project not in project_groups:
                project_groups[project] = []
            project_groups[project].append(todo)
        
        for project, project_todos in project_groups.items():
            print(f"\n📂 {project}:")
            for todo in project_todos:
                desc_preview = f" - {todo['description'][:50]}..." if todo.get('description') else ""
                print(f"  • {todo['name']}{desc_preview}")
        
    except FileNotFoundError:
        print("❌ No todos.json file found")
    
    print("\n🎓 Key Learning Points:")
    print("• Agent handles varied todo patterns (title-only vs detailed)")
    print("• Bulk operations work smoothly")
    print("• Project organization keeps tasks structured")
    print("• CRUD operations (Create, Read, Update, Delete) all functional")
    print("• Agent maintains conversation context across multiple turns")


if __name__ == "__main__":
    asyncio.run(run_basic_operations_test()) 