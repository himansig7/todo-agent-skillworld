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
import asyncio
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from phoenix.otel import register
import weave
from agents import Runner, Agent

# Setup imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.todo_agent import create_agent
from agent.storage import JsonTodoStorage


def reset_test_data():
    """Reset todos and session data for clean test runs."""
    os.makedirs("data", exist_ok=True)
    
    # Reset todos.json
    with open("data/todos.json", "w") as f:
        json.dump([], f)
    
    # Reset session history
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
    
    # Append to log file
    log_file = "tests/logs/test_results.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")
    
    print(f"📊 Test result logged to {log_file}")


async def run_web_search_demo():
    """
    Run web search demo showing agent's multi-turn research capabilities.
    """
    start_time = datetime.now()
    test_details = {
        "turns": 0,
        "validation_results": {},
        "errors": []
    }
    
    try:
        # Reset data for clean test
        reset_test_data()
        
        # Setup tracing (same as main.py)
        load_dotenv()
        
        os.environ["OPENAI_TRACING_ENABLED"] = "1"
        os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
        register(project_name="todo-agent-test-websearch", auto_instrument=True)
        weave.init("todo-agent-test-websearch")

        # Instantiate the agent using the central factory
        agent = create_agent(agent_name="To-Do Agent (Web Search Test)")
        
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
        for turn, message in enumerate(test_messages):
            print(f"\n--- Turn {turn + 1} ---")
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
        
        test_details["turns"] = len(test_messages)
        
        print("\n" + "=" * 50)
        print("🧪 Web Search Demo Complete")
        
        # Comprehensive validation - verify the agent used multi-tool workflow effectively
        validation_success = True
        
        try:
            with open("data/todos.json", "r") as f:
                todos = json.load(f)
            
            travel_todos = [t for t in todos if t.get('project') == 'Travel']
            total_travel_todos = len(travel_todos)
            test_details["validation_results"]["total_travel_todos"] = total_travel_todos
            print(f"✅ Validation: {total_travel_todos} travel todos created")
            
            # Check for research-driven specificity
            detailed_todos = [
                t for t in travel_todos 
                if t.get('description') and len(t['description']) > 40
            ]
            test_details["validation_results"]["detailed_todos"] = len(detailed_todos)
            print(f"✅ Validation: {len(detailed_todos)} todos with detailed descriptions (research-driven)")
            
            # Check for destination-specific tasks
            destination_tasks = [
                t for t in travel_todos 
                if any(keyword in t['name'].lower() for keyword in ['hotel', 'restaurant', 'flight', 'airport'])
            ]
            test_details["validation_results"]["destination_tasks"] = len(destination_tasks)
            print(f"✅ Validation: {len(destination_tasks)} destination-specific tasks")
            
            # Check for comparison/planning tasks
            planning_tasks = [
                t for t in travel_todos 
                if any(keyword in t['name'].lower() for keyword in ['compare', 'research', 'book'])
            ]
            test_details["validation_results"]["planning_tasks"] = len(planning_tasks)
            print(f"✅ Validation: {len(planning_tasks)} planning and comparison tasks")
            
            # Minimum thresholds for success
            if total_travel_todos < 5:
                validation_success = False
                test_details["errors"].append(f"Expected at least 5 travel todos, got {total_travel_todos}")
            
            if len(detailed_todos) < 2:
                validation_success = False
                test_details["errors"].append(f"Expected at least 2 detailed todos (research-driven), got {len(detailed_todos)}")
            
            if len(destination_tasks) < 1:
                validation_success = False
                test_details["errors"].append(f"Expected at least 1 destination-specific task, got {len(destination_tasks)}")
            
            if len(planning_tasks) < 1:
                validation_success = False
                test_details["errors"].append(f"Expected at least 1 planning/comparison task, got {len(planning_tasks)}")
            
            # Store final todo list for inspection
            test_details["validation_results"]["final_todos"] = [
                {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "project": t.get("project", ""),
                    "status": t.get("status", "Unknown")
                } for t in travel_todos
            ]
            
            # Show organized results
            print(f"\n🗺️  Complete Travel Plan:")
            for i, todo in enumerate(travel_todos, 1):
                status_map = {"Completed": "✅", "In Progress": "⏳", "Not Started": "⬜️"}
                status_icon = status_map.get(todo.get('status'), '❓')
                desc_preview = f"\n   📝 {todo['description'][:80]}..." if todo.get('description') else ""
                print(f"{i}. {status_icon} {todo['name']}{desc_preview}")
            
        except FileNotFoundError:
            validation_success = False
            error_msg = "No todos.json file found"
            test_details["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        # Success determination
        overall_success = validation_success and len(test_details["errors"]) == 0
        
        print(f"\n🎓 Key Learning Points:")
        print("• Agent handles multi-turn research workflow")
        print("• Web search → detailed research → todo creation pipeline")
        print("• Transforms vague requests into specific, actionable tasks")
        print("• Multi-tool coordination: research then organize")
        print("• Agent maintains context across complex research sessions")
        print("🔍 Check your tracing dashboard to see the web search + todo creation workflow!")
        
        # Log test results
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
        # Log exception
        end_time = datetime.now()
        test_details["errors"].append(str(e))
        log_test_result("web_search_demo", start_time, end_time, False, test_details)
        print(f"\n❌ TEST FAILED: Web Search Demo - {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_web_search_demo())
    exit(0 if success else 1) 