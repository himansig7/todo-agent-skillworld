"""
Web Search Demo Test
Demonstrates how AI agents use web search to turn vague requests into actionable tasks.

This test shows:
1. Agent takes a general request ("plan vacation")
2. Agent proactively offers to research destinations
3. Agent uses web search to gather information
4. Agent converts research into specific, actionable todos
5. Multi-tool workflow (web search + todo management)

Perfect example of real AI agent value - transforming ambiguous requests into structured plans.
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


async def run_web_search_demo():
    """
    Run web search demo showing agent's proactive research capabilities.
    """
    # Setup tracing (same as main.py)
    load_dotenv()
    warnings.filterwarnings("ignore", category=PydanticJsonSchemaWarning)
    
    os.environ["OPENAI_TRACING_ENABLED"] = "1"
    os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
    register(project_name="todo-agent-websearch-demo", auto_instrument=True)
    weave.init("todo-agent-websearch-demo")
    
    print("🧪 Starting Web Search Demo")
    print("=" * 50)
    print("🎯 Goal: Watch the agent turn vague vacation ideas into actionable plans")
    print("=" * 50)
    
    # Test conversation - demonstrates multi-tool agent workflow
    test_messages = [
        # Start with vague request
        "Add 'Plan summer vacation' to my Travel project",
        
        # Express uncertainty - trigger agent research
        "I want to go somewhere warm with beaches but I'm not sure where. Can you help me research destinations?",
        
        # Ask agent to create actionable tasks from research
        "Based on your research, add specific planning tasks for beach vacation destinations",
        
        # Show the organized results
        "Show me my Travel project with all the tasks you've created"
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
    print("🧪 Web Search Demo Complete")
    
    # Simple validation - verify the agent used web search effectively
    try:
        with open("data/todos.json", "r") as f:
            todos = json.load(f)
        
        travel_todos = [t for t in todos if t.get('project') == 'Travel']
        print(f"✅ Validation: {len(travel_todos)} travel todos created")
        
        # Check for research-driven specificity
        detailed_todos = [
            t for t in travel_todos 
            if t.get('description') and len(t['description']) > 30
        ]
        
        if detailed_todos:
            print(f"✅ Validation: {len(detailed_todos)} todos with detailed descriptions (research-driven)")
        else:
            print("ℹ️  Note: Agent may not have used web search in this run")
        
        # Show what the agent created
        print(f"\n🗺️  Travel Plan Created:")
        for i, todo in enumerate(travel_todos, 1):
            desc_preview = f"\n   📝 {todo['description']}" if todo.get('description') else ""
            print(f"{i}. {todo['name']}{desc_preview}")
        
    except FileNotFoundError:
        print("❌ No todos.json file found")
    
    print(f"\n🎓 Key Learning Points:")
    print("• Agent proactively offers to research when given vague requests")
    print("• Multi-tool workflow: web search → todo creation")
    print("• Transforms general ideas into specific, actionable tasks")
    print("• Shows real AI agent value beyond simple task management")
    print("🔍 Check your tracing dashboard to see the web search API calls!")


if __name__ == "__main__":
    asyncio.run(run_web_search_demo()) 