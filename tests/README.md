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

### Run Without Data Reset
```bash
# Keep existing todos (build on current data)
python tests/run_demo_tests.py --no-reset
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