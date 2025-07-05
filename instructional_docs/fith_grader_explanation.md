# AI Engineering 101: How to Train Your Executive Assistant

Welcome, Manager! Your department has just been assigned a new **Executive Assistant**. Our job isn't just to see if they can do the work, but to train them, measure their performance, and ensure they meet our company's standards.

Many people think of LLMs as new employees: full of potential but needing clear direction. You can't expect them to understand your workflow without clear instructions and the right tools. A detailed memo is a great start, but they need the right office supplies to do their job efficiently. Let's review our new assistant.

## Part 1: The Executive Assistant - Our To-Do Agent

Before we can delegate tasks, we need to understand our assistant's capabilities. Here are the core components they come with:
*   **The Brain**: A fast, low-cost AI model (`gpt-4.1-mini`) representing their fundamental intelligence and ability to follow instructions.
*   **The Instruction Memo**: A `prompt` that outlines their role and how they should operate.
*   **A set of "Office Supplies"**: `Tools` to create, read, update, and delete items on a to-do list.
*   **A Filing Cabinet**: `Storage` which holds two important documents: the official **To-Do List File** and the **Conversation Log** (our chat history).

Now that we know their setup, let's move to the performance review.

---

## Part 2: The Performance Review - Measuring with Tracing

As a manager, your most important tool is the **Performance Review Sheet**, which in AI Engineering is called **tracing**. Tracing allows you to assign a task and get a detailed report on every single action the assistant took to complete it.

### The Task Report: A Trace

When we give our assistant a task, we are running one full **work cycle**. The output is a complete **Task Report**, which we call a **trace**. This report documents every step of the assistant's performance for that single task.

### A Single Action Item: A Span

A **Task Report** is made up of several **action items**. Each action item is a **span**, which measures one specific, isolated step. For a simple task, our report would have a few key action items:
1.  **Action 1: Reading the Memo.** The assistant processes your instructions.
2.  **Action 2: Using a Tool.** The assistant uses one of their "Office Supplies" (a tool).
3.  **Action 3: Filing the Update.** The assistant saves the result to the correct file in the Filing Cabinet.

### The Performance Metrics: Metadata

This is where the real management happens! Every action item (span) in the report comes with a set of precise **measurements**, which we call **metadata**. This is the data that tells us if our assistant is meeting performance standards:
*   **Time (Latency)**: How long did this specific step take, in milliseconds? Is the assistant spending too much time thinking about simple tasks?
*   **Effort (Tokens)**: How much mental energy did they use? Is the task too complex for this assistant, leading to burnout (high cost)?
*   **Task Details (Input/Output)**: What were the exact instructions for this step, and what was the result? Did they follow the memo precisely?
*   **Outcome (Status)**: Did this step succeed (`SUCCESS`) or fail (`ERROR`)? This immediately shows us where mistakes were made.

### Why This Is The Core of Management

By analyzing these task reports, we can make data-driven decisions. If the assistant is too slow (high latency) or inefficient (high token cost), we might need to assign the task to a more senior assistant (a different model). If they're making mistakes (error status), we might need to write a clearer Instruction Memo (the prompt).

This cycle of **assigning, measuring, and coaching** is the heart of AI Engineering. Understanding how to read these reports is the first step to becoming a great manager of AI systems.