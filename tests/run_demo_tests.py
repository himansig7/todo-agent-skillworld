"""
Test Runner for Todo Agent Tutorials
Runs the progressive AI agent tutorial series with console-based reporting.
"""

import os
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from test_basic_crud import run_basic_crud_test
from test_web_search_brainstorming import run_web_search_test
from test_natural_language import run_natural_language_test
from opentelemetry import trace


def reset_data():
    """Reset todos and session data for clean test runs."""
    os.makedirs("data", exist_ok=True)
    
    with open("data/todos.json", "w") as f:
        json.dump([], f)
    
    with open("data/session_default.json", "w") as f:
        json.dump({"history": []}, f)
    
    print("🔄 Data reset - starting with clean slate")


async def run_tutorial(tutorial_name):
    """Run a specific tutorial with timing."""
    start_time = datetime.now()
    
    print(f"\n🔄 Starting {tutorial_name.replace('_', ' ').title()}")
    print("-" * 40)
    
    try:
        if tutorial_name == "basic":
            success = await run_basic_crud_test()
        elif tutorial_name == "research":
            success = await run_web_search_test()
        elif tutorial_name == "language":
            success = await run_natural_language_test()
        else:
            print(f"❌ Unknown tutorial: {tutorial_name}")
            print("Available tutorials: basic, research, language, all")
            return False
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {tutorial_name.replace('_', ' ').title()} ({duration:.1f}s)")
        
        return success
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"❌ {tutorial_name.replace('_', ' ').title()} failed with error: {e} ({duration:.1f}s)")
        return False


async def run_all_tutorials():
    """Run all tutorials in sequence with timing."""
    suite_start_time = datetime.now()
    
    print("🚀 Running All Todo Agent Tutorials")
    print("=" * 60)
    print("🎓 Progressive tutorial series for AI agent mastery:")
    print("• Writing Article Foundation: Essential CRUD operations")
    print("• Observability Platform Research: Web search workflow")
    print("• Finishing Article Project: Natural language conversation")
    print("=" * 60)
    
    tutorials = [
        ("basic", "Writing Article Foundation"),
        ("research", "Observability Platform Research"),
        ("language", "Finishing Article Project")
    ]
    
    results = []
    
    for tutorial_name, tutorial_description in tutorials:
        try:
            success = await run_tutorial(tutorial_name)
            results.append({"name": tutorial_name, "description": tutorial_description, "success": success})
                
        except Exception as e:
            print(f"❌ {tutorial_description} failed with error: {e}")
            results.append({"name": tutorial_name, "description": tutorial_description, "success": False})
        
        # Shutdown tracer for re-initialization
        trace.get_tracer_provider().shutdown()
        await asyncio.sleep(1)
    
    suite_end_time = datetime.now()
    suite_duration = (suite_end_time - suite_start_time).total_seconds()
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 Tutorial Series Results")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{status} {result['description']}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n📈 Overall: {passed}/{total} tutorials completed successfully")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    print(f"⏱️  Total Duration: {suite_duration:.1f}s")
    
    if passed == total:
        print("\n🎉 Tutorial series complete! You've mastered the todo agent!")
    else:
        print("\n🔧 Some tutorials had issues - check the output above for details.")
    
    return passed == total


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run todo-agent tutorial series")
    parser.add_argument(
        "tutorial", 
        nargs="?", 
        choices=["basic", "research", "language", "all"], 
        default="all", 
        help="Tutorial to run: basic, research, language, or all (default: all)"
    )
    
    args = parser.parse_args()
    
    if args.tutorial == "all":
        success = await run_all_tutorials()
    else:
        success = await run_tutorial(args.tutorial)
    
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 