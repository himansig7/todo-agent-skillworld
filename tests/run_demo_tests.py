"""
Simple Test Runner for Todo Agent Demos

Runs the AI agent demonstration tests and manages data cleanup.
Perfect for AI Engineering 101 - simple and focused.
"""

import os
import json
import asyncio
import argparse
from test_basic_operations import run_basic_operations_test
from test_web_search_demo import run_web_search_demo


def reset_data():
    """Reset todos and session data for clean test runs."""
    os.makedirs("data", exist_ok=True)
    
    # Reset todos.json
    with open("data/todos.json", "w") as f:
        json.dump([], f)
    
    # Reset session history
    with open("data/session_default.json", "w") as f:
        json.dump({"history": []}, f)
    
    print("🔄 Data reset - starting with clean slate")


async def run_test(test_name):
    """Run a specific test."""
    if test_name == "basic":
        await run_basic_operations_test()
    elif test_name == "websearch":
        await run_web_search_demo()
    else:
        print(f"❌ Unknown test: {test_name}")
        print("Available tests: basic, websearch, all")
        return False
    
    return True


async def run_all_tests():
    """Run all demo tests in sequence."""
    print("🚀 Running All Demo Tests")
    print("=" * 60)
    print("🎓 These tests demonstrate core AI agent capabilities:")
    print("• Basic Operations: CRUD, bulk tasks, project organization")
    print("• Web Search Demo: Multi-tool workflow and proactive research")
    print("=" * 60)
    
    tests = [
        ("basic", "Basic Operations"),
        ("websearch", "Web Search Demo")
    ]
    
    results = []
    
    for test_name, test_description in tests:
        print(f"\n🔄 Starting {test_description}")
        print("-" * 40)
        
        # Reset data before each test
        reset_data()
        
        try:
            success = await run_test(test_name)
            results.append((test_description, success))
            if success:
                print(f"✅ {test_description} completed successfully")
            else:
                print(f"❌ {test_description} failed")
        except Exception as e:
            print(f"❌ {test_description} failed with error: {e}")
            results.append((test_description, False))
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Test Results")
    print("=" * 60)
    
    for test_description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_description}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n📈 Overall: {passed}/{total} demos completed successfully")
    
    if passed == total:
        print("\n🎉 All demos working! Your AI agent is ready for action.")
    else:
        print("\n🔧 Some demos had issues - check the output above for details.")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run todo-agent demo tests")
    parser.add_argument(
        "test", 
        nargs="?", 
        choices=["basic", "websearch", "all"], 
        default="all", 
        help="Demo to run: basic, websearch, or all (default: all)"
    )
    parser.add_argument(
        "--no-reset", 
        action="store_true", 
        help="Don't reset data before running"
    )
    
    args = parser.parse_args()
    
    # Reset data unless user specifically asks not to
    if not args.no_reset and args.test != "all":
        reset_data()
    
    # Run the requested test(s)
    if args.test == "all":
        await run_all_tests()
    else:
        await run_test(args.test)


if __name__ == "__main__":
    asyncio.run(main()) 