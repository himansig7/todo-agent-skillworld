"""
Test Runner for Todo Agent Demos
Runs the AI agent demonstration tests with structured logging and reporting.
"""

import os
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from test_basic_operations import run_basic_operations_test
from test_web_search_demo import run_web_search_demo
from opentelemetry import trace


def reset_data():
    """Reset todos and session data for clean test runs."""
    os.makedirs("data", exist_ok=True)
    
    with open("data/todos.json", "w") as f:
        json.dump([], f)
    
    with open("data/session_default.json", "w") as f:
        json.dump({"history": []}, f)
    
    print("🔄 Data reset - starting with clean slate")


def log_test_suite_result(suite_name, start_time, end_time, results, summary):
    """Log overall test suite results."""
    os.makedirs("tests/logs", exist_ok=True)
    
    result = {
        "suite_name": suite_name,
        "timestamp": datetime.now().isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "test_results": results,
        "summary": summary
    }
    
    log_file = "tests/logs/test_suite_results.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(result) + "\n")
    
    print(f"📊 Test suite result logged to {log_file}")


def generate_test_report():
    """Generate a markdown test report from the logs."""
    log_file = "tests/logs/test_results.jsonl"
    suite_log_file = "tests/logs/test_suite_results.jsonl"
    
    if not os.path.exists(log_file):
        print("❌ No test results found")
        return
    
    report_content = []
    report_content.append("# Todo Agent Test Report\n")
    report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    with open(log_file, "r") as f:
        test_results = [json.loads(line) for line in f]
    
    # Get latest results for each test
    latest_results = {}
    for result in test_results:
        test_name = result["test_name"]
        if test_name not in latest_results or result["timestamp"] > latest_results[test_name]["timestamp"]:
            latest_results[test_name] = result
    
    report_content.append("## Test Results Summary\n")
    
    passed = 0
    failed = 0
    
    for test_name, result in latest_results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        duration = f"{result['duration_seconds']:.2f}s"
        
        report_content.append(f"### {test_name.replace('_', ' ').title()}\n")
        report_content.append(f"- **Status**: {status}\n")
        report_content.append(f"- **Duration**: {duration}\n")
        report_content.append(f"- **Turns**: {result['details']['turns']}\n")
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
            report_content.append(f"- **Errors**: {', '.join(result['details']['errors'])}\n")
        
        if result["details"]["validation_results"]:
            report_content.append("- **Validation Results**:\n")
            for key, value in result["details"]["validation_results"].items():
                report_content.append(f"  - {key.replace('_', ' ').title()}: {value}\n")
        
        report_content.append("\n")
    
    total = passed + failed
    report_content.append(f"## Overall Summary\n")
    report_content.append(f"- **Total Tests**: {total}\n")
    report_content.append(f"- **Passed**: {passed}\n")
    report_content.append(f"- **Failed**: {failed}\n")
    report_content.append(f"- **Success Rate**: {(passed/total*100):.1f}%\n")
    
    if os.path.exists(suite_log_file):
        with open(suite_log_file, "r") as f:
            suite_results = [json.loads(line) for line in f]
        
        if suite_results:
            latest_suite = suite_results[-1]
            report_content.append(f"\n## Latest Test Suite Run\n")
            report_content.append(f"- **Suite**: {latest_suite['suite_name']}\n")
            report_content.append(f"- **Duration**: {latest_suite['duration_seconds']:.2f}s\n")
            report_content.append(f"- **Summary**: {latest_suite['summary']}\n")
    
    report_file = "tests/logs/test_report.md"
    with open(report_file, "w") as f:
        f.write("".join(report_content))
    
    print(f"📋 Test report generated: {report_file}")


async def run_test(test_name):
    """Run a specific test."""
    print(f"\n🔄 Starting {test_name.replace('_', ' ').title()}")
    print("-" * 40)
    
    try:
        if test_name == "basic":
            return await run_basic_operations_test()
        elif test_name == "websearch":
            return await run_web_search_demo()
        else:
            print(f"❌ Unknown test: {test_name}")
            print("Available tests: basic, websearch, all")
            return False
    except Exception as e:
        print(f"❌ {test_name.replace('_', ' ').title()} failed with error: {e}")
        return False


async def run_all_tests():
    """Run all demo tests in sequence with comprehensive reporting."""
    suite_start_time = datetime.now()
    
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
        try:
            success = await run_test(test_name)
            results.append({
                "test_name": test_name,
                "description": test_description,
                "success": success
            })
            
            if success:
                print(f"✅ {test_description} completed successfully")
            else:
                print(f"❌ {test_description} failed")
                
        except Exception as e:
            print(f"❌ {test_description} failed with error: {e}")
            results.append({
                "test_name": test_name,
                "description": test_description,
                "success": False,
                "error": str(e)
            })
        
        # Shutdown tracer for re-initialization
        trace.get_tracer_provider().shutdown()
        await asyncio.sleep(1)
    
    suite_end_time = datetime.now()
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    suite_summary = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": (passed / total * 100) if total > 0 else 0
    }
    
    print("\n" + "=" * 60)
    print("📊 Demo Test Results")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        error_info = f" ({result.get('error', '')})" if not result["success"] and result.get('error') else ""
        print(f"{status} {result['description']}{error_info}")
    
    print(f"\n📈 Overall: {passed}/{total} demos completed successfully")
    print(f"🎯 Success Rate: {suite_summary['success_rate']:.1f}%")
    
    log_test_suite_result("all_demos", suite_start_time, suite_end_time, results, suite_summary)
    
    if passed == total:
        print("\n🎉 All demos working! Your AI agent is ready for action.")
    else:
        print("\n🔧 Some demos had issues - check the logs for details.")
        
    generate_test_report()
    
    return passed == total


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
        help="Don't reset data before running (only affects individual tests)"
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate test report from existing logs"
    )
    
    args = parser.parse_args()
    
    if args.report:
        generate_test_report()
        return
    
    if args.test == "all":
        success = await run_all_tests()
    else:
        success = await run_test(args.test)
    
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 