
# Out-of-the-Box Observability: OpenAI, Phoenix, and Weave Compared

Hey fellow MLOps practitioners, here's the reality: when you're working with foundation models, you're essentially flying blind unless you have proper observability. The catch? Most teams think they need to build complex custom tracking from scratch. **Plot twist: you don't.**

Three major platforms—OpenAI's native tracing, Arize Phoenix, and W&B Weave—give you powerful observability capabilities right out of the box. With just a few lines of setup code, you get detailed traces, spans, and metrics that would take weeks to build yourself. But here's the question: which platform gives you the best default experience?

I spent time testing all three with a simple multi-tool agent, and the results surprised me. Each platform has a distinct personality when it comes to out-of-the-box observability—from OpenAI's clean simplicity to Phoenix's analytics depth to Weave's collaboration focus. In this post, I'll show you exactly what each platform gives you by default, so you can pick the right one for your workflow without reinventing the wheel.

Let's dive into what you actually get for free (or nearly free) when it comes to foundation model observability.

---

## Part 1: Test Case - Multi-Tool Agent Architecture

I built this simple CRUD to-do agent to mimic the kind of multi-tool workflows we see in production—like an overworked intern juggling database ops and quick web searches. It's powered by `gpt-4.1-mini`, with a detailed prompt for reasoning, tools for task management, and persistent storage.

### Quick-Start: Run the Agent

Get it running locally in minutes:

```bash
git clone https://github.com/leowalker89/todo-agent.git
cd todo-agent
uv sync # Install deps with uv
cp .env.example .env # Add your API keys
uv run main.py
```

Now you're ready to test commands like 'Add a task to research MLOps tools.'

### Why This Makes a Good Test Case

This agent combines LLM reasoning, tool selection, and multi-step execution—perfect for evaluating what each platform shows you by default. In production terms, it's like a lightweight RAG system: vague user input → tool calls → refined output.

### Core Components

- **Model**: `gpt-4.1-mini` for cost-effective intelligence.
- **Prompt**: Guides proactive task management.
- **Tools**:
  - `create_todo`: Add tasks.
  - `read_todos`: List or filter tasks.
  - `update_todo`: Modify tasks (e.g., mark complete).
  - `delete_todo`: Remove tasks.
  - `web_search`: Research to clarify vague requests.

### Execution Flow

The agent interprets your request, selects tools, executes them, and responds—mirroring real MLOps pipelines where observability becomes crucial for understanding what's happening under the hood.

---

## Part 2: Traces & Spans: The Building Blocks

Before we dive into what each platform gives you, let's quickly cover the fundamentals. Understanding traces and spans is key to appreciating what these platforms deliver out-of-the-box.

### What is a Trace?

A trace is the full execution record of a single workflow, documenting every step from input to output. Think of it as your AI's 'flight recorder'—essential for understanding what happened when things go sideways.

### Breaking It Down: Spans

Each trace consists of spans, which are isolated steps in the process. For our agent, a typical trace might include:
1. **Input Processing**: The LLM interprets the user's request.
2. **Tool Selection & Execution**: Calling tools like `web_search` or `update_todo`.
3. **Output Generation**: Formulating the final response.

### Key Metadata You Get For Free

Here's what all three platforms capture automatically:
- **Latency**: Time per step (in ms)—crucial for spotting bottlenecks.
- **Tokens**: Usage and cost—helps with budget tracking.
- **Input/Output**: Exact data flowing through—perfect for debugging.
- **Status**: Success or error—basic but expandable.
- **Tool Calls**: Which tools were selected and their parameters.

The beauty? You don't have to manually instrument any of this. These platforms capture it all with minimal setup.

---

## Part 3: Platform Comparison - What You Get Out of the Box

To test these platforms, I ran the agent's built-in demos—things like article planning and web research—that simulate real MLOps workflows. Here's what each platform delivered with minimal configuration:

### OpenAI Platform

- **Out-of-Box Strengths:** Native integration with OpenAI Agent SDK with zero dependencies. Clean UI optimized for tool call debugging. Real-time trace streaming.
- **Default Metadata:** Latency, tool calls (input/output), model, tokens (input/output/total), timestamps, request IDs.
- **Parent/Child Structure:** Clickable trace hierarchy shows agent → tool sequences with clear flow visualization.
- **Setup:** ~1 line of code

### Arize Phoenix

- **Out-of-Box Strengths:** Model-agnostic platform with waterfall timeline views and automatic bottleneck detection. Built-in cost analytics and session grouping.
- **Default Metadata:** Workflow names, detailed timings, token counts, cost calculations, span relationships, LLM parameters.
- **Parent/Child Structure:** Hierarchical waterfall view with automatic parent/child span linking and performance insights.
- **Setup:** ~2 lines of code

### W&B Weave

- **Out-of-Box Strengths:** Framework-agnostic platform with trace trees and built-in feedback collection systems. Automatic experiment grouping and versioning.
- **Default Metadata:** Full inputs/outputs, execution status, automatic run grouping, model versions, experiment metadata.
- **Parent/Child Structure:** Interactive tree view tracking complete workflow → operation → sub-call hierarchies.
- **Setup:** ~2 lines of code

### Comparison Summary

| Platform | Default Visualization | Key Auto-Captured Metadata | Built-in Collaboration | Setup Lines |
| --- | --- | --- | --- | --- |
| OpenAI | Chronological span log | Latency, cost, tool calls | No | ~1 line |
| Phoenix | Waterfall timeline | Latency, tokens, cost, analytics | No | ~2 lines |
| W&B Weave | Hierarchical tree view | Inputs, outputs, feedback, experiments | Yes | ~2 lines |

**The Bottom Line:** All three capture core metadata automatically. The differences lie in visualization style, analytics depth, and collaboration features.

---

## Part 4: When to Use What - Out-of-the-Box Recommendations

Based on my experiments, here's when each platform's default capabilities shine:

### For Quick Debugging: OpenAI Platform

- **Why:** Requires no additional dependencies if you're already using the OpenAI Python SDK.
- **Best Default Feature:** Clean, readable tool call traces.
- **Trade-off:** Limited analytics depth, but sometimes simple is better.
- **Perfect When:** You need to quickly verify your agent is working correctly.

### For Rich Analytics: Arize Phoenix

- **Why:** Gives you professional-grade analytics dashboards with minimal configuration.
- **Best Default Feature:** Automatic waterfall charts that immediately show performance bottlenecks.
- **Trade-off:** Slightly more setup, but the payoff in insights is immediate.
- **Perfect When:** You want to understand performance patterns without building custom dashboards.

### For Team Collaboration: W&B Weave

- **Why:** Built-in experiment tracking and team features from day one.
- **Best Default Feature:** Automatic experiment organization and sharing capabilities.
- **Trade-off:** More complex interface, but scales with team needs.
- **Perfect When:** Multiple people need to review and compare agent performance.

### The Hybrid Approach

Here's what I actually do in practice:
1. **Start with OpenAI** for immediate validation
2. **Add Phoenix** when I need deeper performance analysis
3. **Layer in Weave** when working with a team or running experiments

The beauty is that all three have generous free tiers, so you can test their default capabilities without commitment.

---

## When You Outgrow the Defaults

While these out-of-the-box capabilities are impressive, there are scenarios where you'll need custom instrumentation:

- **Custom Metrics**: Domain-specific KPIs like task completion rates or user satisfaction scores
- **Advanced Analytics**: Complex performance analysis, A/B testing, or custom dashboards  
- **Specialized Workflows**: Multi-model pipelines, custom evaluation frameworks, or integration with existing monitoring systems
- **Compliance Requirements**: Specific logging formats, data retention policies, or audit trails

The good news? Starting with these default capabilities gives you a solid foundation to build upon. You'll understand your observability needs better before investing in custom solutions.

---

## Conclusion: The Power of Defaults

Here's the key insight: **you don't need to build observability from scratch**. These platforms give you professional-grade tracing capabilities with just a few lines of setup code. The question isn't whether you should instrument your foundation models—it's which platform's defaults best match your workflow.

Key takeaways:
- **Start Simple**: OpenAI's built-in tracing gets you 80% of what you need with zero overhead.
- **Scale Smart**: Phoenix and Weave offer more sophisticated defaults when you need deeper insights.
- **Mix and Match**: There's no rule saying you can't use multiple platforms—they complement each other well.

The real power here is speed to insight. Instead of spending weeks building custom observability, you can have professional-grade tracing running in minutes. That's time better spent on what actually matters: building better AI.

What's your experience with out-of-the-box observability? Have you found any hidden gems in these platforms' default features? 