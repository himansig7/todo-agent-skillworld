# Todo-Agent Tutorial Series

Progressive tutorial series for mastering AI agent workflows through realistic article planning.

## 🎓 Tutorial Series

| Tutorial | Description | What You Learn |
|----------|-------------|----------------|
| `test_basic_crud.py` | **Article Foundation Setup** | Essential CRUD operations while planning observability article structure |
| `test_web_search_brainstorming.py` | **Platform Research & Planning** | Web search integration for researching observability platforms |
| `test_natural_language.py` | **Project Completion Prep** | Natural language flexibility for finishing article tasks |

## 🚀 Running the Tutorials

### Complete Tutorial Series (Recommended)
```bash
uv run tests/run_demo_tests.py
```

### Individual Tutorials
```bash
# 1. Basic CRUD Tutorial - Learn essential operations
uv run tests/run_demo_tests.py basic

# 2. Platform Research Tutorial - Web search workflow
uv run tests/run_demo_tests.py research

# 3. Natural Language Tutorial - Casual conversation
uv run tests/run_demo_tests.py language
```

### Additional Options
```bash
# Generate tutorial report from existing logs
uv run tests/run_demo_tests.py --report
```

### Direct Tutorial Execution
```bash
uv run tests/test_basic_crud.py
uv run tests/test_web_search_brainstorming.py
uv run tests/test_natural_language.py
```

## 📚 Tutorial Learning Progression

### 1. Basic CRUD Tutorial (4 turns)
**Goal**: Learn essential todo operations while setting up article structure
- Create structured writing tasks with descriptions
- Organize tasks by project for better workflow  
- Update task status and add progress notes
- Build article foundations systematically

**Focus**: Observability platforms comparison article planning

### 2. Platform Research Tutorial (4 turns)
**Goal**: Research workflow → structured task creation
- **Turn 1**: Search "Arize Phoenix Cloud main benefits" → 2 paragraph summary
- **Turn 2**: Search "Weights & Biases Weave main benefits" → 2 paragraph summary  
- **Turn 3**: Search "OpenAI platform observability features" → 2 paragraph summary
- **Turn 4**: Convert research into structured writing tasks

**Focus**: Research stays in chat history, todos become actionable writing tasks

### 3. Natural Language Tutorial (4 turns)
**Goal**: Project completion with casual, natural conversation
- Handle typos gracefully ('everthing' → 'everything')
- Process casual language: 'hey', 'lemme see', 'gotta make sure'
- Context understanding: 'that proofreading task' references previous todo
- Natural conversation flow with task modifications

**Focus**: Finishing article with editing and publishing tasks

## 📊 Tutorial Logging & Reporting

Each tutorial automatically logs structured results with:
- Tutorial execution time and duration
- Turn-by-turn conversation tracking
- Learning objectives and outcomes
- Pass/fail status with detailed error reporting
- Automatic tutorial report generation

### Tutorial Logs Location
- `tests/logs/test_results.jsonl` - Individual tutorial results
- `tests/logs/test_suite_results.jsonl` - Tutorial series summaries
- `tests/logs/test_report.md` - Human-readable tutorial report

### Understanding Tutorial Results
Each tutorial includes minimal validation (basic sanity checks):
- All tutorials: Simply verify that some todos were created during the conversation
- **Real evaluation happens in your tracing dashboards** - use the observability tools to assess quality and performance

## 🔄 Data Management

### When Data Gets Reset
- All tutorials: Each tutorial automatically resets data before running for clean results
- Individual tutorials: Run with fresh data every time
- Tutorial series: Each tutorial in the series gets fresh data

### Data Persistence
- During tutorials: Data accumulates naturally through the tutorial conversation
- After tutorials: Data persists in `data/` directory for inspection
- Logs: Tutorial results and reports are preserved in `tests/logs/`

### Manual Data Control
```bash
uv run python -c "
import os, json
os.makedirs('data', exist_ok=True)
with open('data/todos.json', 'w') as f: json.dump([], f)
with open('data/session_default.json', 'w') as f: json.dump({'history': []}, f)
"
```

## 🔍 Observability & Tracing

Each tutorial uses separate tracing projects for clean observation:
- OpenAI Platform: Native tracing enabled
- Arize Phoenix Cloud: Projects `todo-agent-crud-tutorial`, `todo-agent-research-tutorial`, `todo-agent-language-tutorial`
- W&B Weave: Individual tracking for each tutorial

Check your tracing dashboards to see:
- Agent decision-making process and tool usage patterns
- Web search API calls and response processing
- Natural language interpretation and normalization
- Performance metrics across different conversation styles

## 🎯 Learning Objectives

This tutorial series teaches core AI engineering concepts through realistic workflows:

1. **Agent Architecture**: How to build conversational AI for content creation and project management
2. **Tool Design Patterns**: CRUD operations, web search integration, and schema validation
3. ****Observability First**: Use tracing dashboards to evaluate agent quality, not hardcoded validation
4. **Workflow Management**: Multi-project organization and realistic task progression patterns
5. **Natural Language Processing**: Handling casual input, typos, and collaborative interactions

## 💡 Key Takeaways

- **Progressive Learning**: Each tutorial builds on the previous, from basic operations to advanced workflows
- **Realistic Scenarios**: Actually plan an observability article while learning agent capabilities
- **Observability Over Validation**: Use tracing dashboards to evaluate agent quality, not rigid programmatic checks
- **Natural Language Robustness**: Agents handle casual input, typos, and informal language gracefully  
- **Research Integration**: Web search becomes structured task planning, not information dumping
- **Educational Value**: Learn AI engineering concepts through practical, hands-on tutorials

