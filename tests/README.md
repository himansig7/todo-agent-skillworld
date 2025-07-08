# Todo-Agent Demo Tests

Simple demonstration tests for the todo-agent project.

## 🧪 Demo Tests

| Test | Description | What It Shows |
|------|-------------|---------------|
| `test_basic_operations.py` | Natural language article creation workflow | Casual input processing, typo handling, concise task management, Content → Writing → Publication phases |
| `test_web_search_demo.py` | AI brainstorming & idea generation | Web search for inspiration, collaborative planning, idea suggestions → structured tasks |

## 🚀 Running the Demos

### Run All Demos
```bash
python tests/run_demo_tests.py
```

### Run Individual Demos
```bash
# Basic CRUD and workflow operations
python tests/run_demo_tests.py basic

# Web search integration demo
python tests/run_demo_tests.py websearch
```

### Additional Options
```bash
# Generate test report from existing logs
python tests/run_demo_tests.py --report
```

### Direct Test Execution
```bash
python tests/test_basic_operations.py
python tests/test_web_search_demo.py
```

## 📋 What Each Demo Shows

### Basic Operations Demo
- Natural language processing with casual, unstructured input
- Agent handles typos, misspellings, and informal language gracefully
- Content → Writing → Publication workflow with realistic task progression
- Concise task names and descriptions mirror real human productivity patterns

### Web Search Demo  
- Collaborative brainstorming and idea generation workflow
- Web search → idea suggestions → structured task creation pipeline
- Agent suggests and supports rather than taking over completely
- Transforms writer's block into actionable planning tasks

## 📊 Test Logging & Reporting

Each test automatically logs structured results with:
- Test execution time and duration
- Turn-by-turn conversation tracking
- Comprehensive validation results
- Pass/fail status with detailed error reporting
- Automatic test report generation

### Test Logs Location
- `tests/logs/test_results.jsonl` - Individual test results
- `tests/logs/test_suite_results.jsonl` - Test suite summaries
- `tests/logs/test_report.md` - Human-readable test report

### Understanding Test Results
Each test includes minimal validation (just basic sanity checks):
- Both tests: Simply verify that some todos were created during the conversation
- **Real evaluation happens in your tracing dashboards** - use the observability tools to assess quality and performance

## 🔄 Data Management

### When Data Gets Reset
- All tests: Each test automatically resets data before running for clean results
- Individual tests: Run with fresh data every time
- Test suite: Each test in the suite gets fresh data

### Data Persistence
- During tests: Data accumulates naturally through the test conversation
- After tests: Data persists in `data/` directory for inspection
- Logs: Test results and reports are preserved in `tests/logs/`

### Manual Data Control
```bash
python -c "
import os, json
os.makedirs('data', exist_ok=True)
with open('data/todos.json', 'w') as f: json.dump([], f)
with open('data/session_default.json', 'w') as f: json.dump({'history': []}, f)
"
```

## 🔍 Observability & Tracing

Each demo uses the same tracing setup as the main application:
- OpenAI Platform: Native tracing enabled
- Arize Phoenix Cloud: Project names `todo-agent-test-basic` and `todo-agent-test-websearch`
- W&B Weave: Individual tracking for each demo

Check your tracing dashboards to see:
- Agent decision-making process
- Tool usage patterns
- Web search API calls
- Performance metrics

## 🎓 Learning Objectives

These demos teach core AI engineering concepts:

1. Agent Architecture: How to build conversational AI for technical content creation
2. Tool Design Patterns: CRUD operations, web search integration, and schema validation
3. **Observability First**: Use tracing dashboards to evaluate agent quality, not hardcoded validation
4. Workflow Management: Multi-project organization and status progression patterns
5. Natural Language Processing: Handling casual input, typos, and collaborative interactions

## 💡 Key Takeaways

- **Observability Over Validation**: Use tracing dashboards to evaluate agent quality, not rigid programmatic checks
- Natural Language Robustness: Agents handle casual input, typos, and informal language gracefully  
- Collaborative Intelligence: Best agents suggest and support rather than take over completely
- Practical Workflows: Status progression and project organization mirror real-world productivity patterns
- Educational Value: Simple demos that showcase complex AI engineering concepts clearly 