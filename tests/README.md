# Todo-Agent Demo Tests

Simple demonstration tests for the todo-agent project. Perfect for AI Engineering 101 - focused, educational, and easy to understand.

## 🧪 Demo Tests

| Test | Description | What It Shows |
|------|-------------|---------------|
| `test_basic_operations.py` | Core agent functionality | CRUD operations, bulk tasks, project organization, conversation context |
| `test_web_search_demo.py` | Multi-tool agent workflow | Web search integration, research → actionable todos, proactive behavior |

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
# Keep existing todos (build on current data)
python tests/run_demo_tests.py --no-reset

# Generate test report from existing logs
python tests/run_demo_tests.py --report
```

### Direct Test Execution
```bash
# Run tests directly (includes data reset and logging)
python tests/test_basic_operations.py
python tests/test_web_search_demo.py
```

## 📋 What Each Demo Shows

### Basic Operations Demo
- **Creates todos** with varied patterns (title-only vs detailed descriptions)
- **Bulk operations** (creating multiple todos at once)
- **Project organization** (Work, Personal, etc.)
- **CRUD lifecycle** (Create, Read, Update, Delete)
- **Conversation context** (agent remembers previous turns)

### Web Search Demo  
- **Proactive research** (agent offers to research vague requests)
- **Multi-tool workflow** (web search → todo creation)
- **Value transformation** (general idea → specific actionable tasks)
- **Real-world utility** (travel planning example)

## 📊 Test Logging & Reporting

Each test automatically logs structured results with:
- **Test execution time** and duration
- **Turn-by-turn conversation tracking**
- **Comprehensive validation results**
- **Pass/fail status with detailed error reporting**
- **Automatic test report generation**

### Test Logs Location
- `tests/logs/test_results.jsonl` - Individual test results
- `tests/logs/test_suite_results.jsonl` - Test suite summaries
- `tests/logs/test_report.md` - Human-readable test report

### Understanding Test Results
Each test includes validation thresholds:
- **Basic Operations**: Minimum 5 todos, 2 projects (completed tasks are deleted in test)
- **Web Search Demo**: Minimum 5 travel todos, 2 detailed todos, 1 destination task

## 🔄 Data Management

### When Data Gets Reset
- **All tests**: Each test automatically resets data before running for clean results
- **Individual tests**: Run with fresh data every time
- **Test suite**: Each test in the suite gets fresh data

### Data Persistence
- **During tests**: Data accumulates naturally through the test conversation
- **After tests**: Data persists in `data/` directory for inspection
- **Logs**: Test results and reports are preserved in `tests/logs/`

### Manual Data Control
```bash
# Reset data manually
python -c "
import os, json
os.makedirs('data', exist_ok=True)
with open('data/todos.json', 'w') as f: json.dump([], f)
with open('data/session_default.json', 'w') as f: json.dump({'history': []}, f)
"
```

## 🔍 Observability & Tracing

Each demo uses the same tracing setup as the main application:
- **OpenAI Platform**: Native tracing enabled
- **Arize Phoenix Cloud**: Project names `todo-agent-test-basic` and `todo-agent-websearch-demo`
- **W&B Weave**: Individual tracking for each demo

Check your tracing dashboards to see:
- Agent decision-making process
- Tool usage patterns
- Web search API calls
- Performance metrics

## 🎓 Learning Objectives

These demos teach core AI engineering concepts:

1. **Agent Design**: How to build conversational AI that maintains context
2. **Tool Integration**: Combining multiple capabilities (CRUD + web search)
3. **Observability**: Tracking agent behavior with tracing tools
4. **Validation**: Simple checks to ensure agent functionality
5. **Real-world Value**: Turning vague requests into actionable plans

## 💡 Key Takeaways

- **Simple is powerful**: Basic CRUD + web search = genuinely useful agent
- **Context matters**: Conversation history enables natural interactions
- **Proactivity adds value**: Agents that research and suggest are more helpful
- **Observability is crucial**: Tracing helps understand and debug agent behavior
- **Validation is essential**: Always verify your agent does what you expect

Perfect for understanding how AI agents work in practice! 