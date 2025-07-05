"""
Web Search Demo Test
Demonstrates how AI agents use web search to turn vague requests into actionable tasks.

This test shows:
1. Agent takes a general request ("plan vacation")
2. Agent proactively offers to research destinations
3. Agent uses web search to gather information about multiple destinations
4. Agent does detailed research for each destination (hotels, restaurants, airports)
5. Agent converts research into specific, actionable todos
6. Multi-turn, multi-tool workflow (web search → todo creation → organization)

Perfect example of real AI agent value - transforming ambiguous requests into detailed, structured plans.
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
    Run web search demo showing agent's multi-turn research capabilities.
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
    print("🎯 Goal: Watch the agent research vacation details and create actionable plans")
    print("=" * 50)
    
    # Test conversation - demonstrates multi-turn, multi-tool agent workflow
    test_messages = [
        # Start with vague request
        "Add 'Plan summer vacation' to my Travel project",
        
        # Express uncertainty - trigger initial research
        "I want to go somewhere warm with beaches in July, but I'm not sure where. Can you research some good destinations for me?",
        
        # Guide agent to pick specific destinations for detailed research
        "Those sound great! Pick 2-3 of the most popular destinations and research specific details for each one: what hotels to stay at, good restaurants for dinner, and what airports to fly into",
        
        # Ask agent to create specific todos based on detailed research
        "Based on all your research, create specific planning tasks for each destination with all the details you found",
        
        # Create comparison tasks
        "Now add tasks to compare these destinations: 'Compare hotel prices across destinations', 'Compare flight costs', and 'Research best time to book'",
        
        # Final organization
        "Show me my complete Travel project with all the detailed tasks you've created"
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
    
    # Validation - verify the agent used multi-tool workflow effectively
    try:
        with open("data/todos.json", "r") as f:
            todos = json.load(f)
        
        travel_todos = [t for t in todos if t.get('project') == 'Travel']
        print(f"✅ Validation: {len(travel_todos)} travel todos created")
        
        # Check for research-driven specificity
        detailed_todos = [
            t for t in travel_todos 
            if t.get('description') and len(t['description']) > 40
        ]
        print(f"✅ Validation: {len(detailed_todos)} todos with detailed descriptions (research-driven)")
        
        # Check for destination-specific tasks
        destination_tasks = [
            t for t in travel_todos 
            if any(keyword in t['name'].lower() for keyword in ['hotel', 'restaurant', 'flight', 'airport'])
        ]
        print(f"✅ Validation: {len(destination_tasks)} destination-specific tasks")
        
        # Check for comparison/planning tasks
        planning_tasks = [
            t for t in travel_todos 
            if any(keyword in t['name'].lower() for keyword in ['compare', 'research', 'book'])
        ]
        print(f"✅ Validation: {len(planning_tasks)} planning and comparison tasks")
        
        # Show organized results
        print(f"\n🗺️  Complete Travel Plan:")
        for i, todo in enumerate(travel_todos, 1):
            status = "✅" if todo.get('completed') else "⏳"
            desc_preview = f"\n   📝 {todo['description'][:80]}..." if todo.get('description') else ""
            print(f"{i}. {status} {todo['name']}{desc_preview}")
        
    except FileNotFoundError:
        print("❌ No todos.json file found")
    
    print(f"\n🎓 Key Learning Points:")
    print("• Agent handles multi-turn research workflow")
    print("• Web search → detailed research → todo creation pipeline")
    print("• Transforms vague requests into specific, actionable tasks")
    print("• Multi-tool coordination: research then organize")
    print("• Agent maintains context across complex research sessions")
    print("🔍 Check your tracing dashboard to see the web search + todo creation workflow!")


if __name__ == "__main__":
    asyncio.run(run_web_search_demo()) 