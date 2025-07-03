# A QA Engineer's Guide to Inspection Toolkits

Welcome, QA Engineer. You know how to read an `Inspection Report` (a trace) to measure your robot's performance. Now, which brand of inspection equipment should you use? Each toolkit has its own dashboard, features, and level of precision.

This guide compares the three different inspection toolkits we've hooked up to our robot: OpenAI, Arize Phoenix, and W&B Weave.

## 1. Quick Recap: What Are We Measuring?

Remember, a **trace** is the full Inspection Report for one test cycle, and a **span** is a single checkpoint or measurement within that report. All three platforms below will show you the same basic data. What makes them different is *how* they visualize the report and what extra diagnostic tools they provide.

---

## 2. The Inspection Toolkits: An Introduction

-   **OpenAI Native Tracing**: Think of this as the basic **multimeter** that comes with the robot's brain. It's simple, reliable, and gives you the core voltage and current readings with no extra setup.
-   **Arize Phoenix**: This is the **advanced diagnostics rig** for the serious R&D engineer. It's a powerful, open-source toolkit designed for deep, data-centric debugging, especially within a code notebook.
-   **W&B Weave**: This is the **enterprise-grade assembly line testing suite**. It's part of the larger Weights & Biases MLOps platform, designed for teams that need to run rigorous experiments, track product versions, and maintain professional, reproducible quality control.

---

## 3. The Test Bench: Comparing the User Experience

### a. Dashboard & Readouts (UI & First Impressions)

| Platform      | Dashboard Style                                                                                              |
| :------------ | :----------------------------------------------------------------------------------------------------------- |
| **OpenAI**    | **Clean & Basic**. The readouts are clear and integrated directly into the OpenAI dashboard. No frills.            |
| **Phoenix**   | **Data-Dense & Analytical**. This dashboard is for experts, packed with charts and data tables for deep analysis. |
| **W&B Weave** | **Polished & Professional**. A clean, modern interface that feels like part of a larger, integrated MLOps suite.  |

### b. Report Visualization (Trace Visualization)

This is how each toolkit displays the full Inspection Report for a single test.

| Platform      | Report Display Style                                                                                                                                     |
| :------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OpenAI**    | A simple, chronological log of all the checkpoints. Easy to read but less visual.                                                                        |
| **Phoenix**   | A classic "waterfall" chart. This is a powerful visualization that clearly shows how each checkpoint leads to the next and how long each one took.         |
| **W&B Weave** | Also a "waterfall" chart. It excels at showing the hierarchy of checkpoints, like when a major test is composed of several smaller sub-tests.               |

### c. Default Metrics Captured (Per Span)

This is the default set of measurements you get for a single checkpoint in your report.

| Platform      | Brain Checkpoint (LLM Call)                                                                      | Tool Checkpoint (Tool Call)                                                                 |
| :------------ | :----------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| **OpenAI**    | `model`, `prompt`, `completion`, `usage` (tokens), `latency`.                                      | `function_name`, `arguments`, `output`.                                                     |
| **Phoenix**   | Same as OpenAI, but sometimes enriches the data by automatically detecting the `prompt_template`. | `function_name`, `arguments`, `output`. The dashboard is great for inspecting complex data. |
| **W&B Weave** | `model`, `prompt`, `completion`, `usage`, `latency`. Very clear separation of inputs and outputs. | `op_name`, `inputs`, `output`.                                                              |

---

## 4. Advanced Diagnostics: A Look at Special Features

### a. Automated Testing (Evaluation & Scoring)

| Platform      | Automated QA Features                                                                                                                                                            |
| :------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OpenAI**    | **None built-in**. This toolkit only provides the raw measurements. You have to write your own scripts to score the results.                                                          |
| **Phoenix**   | **A Core Feature**. Phoenix provides a library of pre-built "evaluators" to automatically score your robot's performance on common tests like RAG relevance and hallucination detection. |
| **W&B Weave** | **Enterprise-Grade Evals**. Weave provides a formal system for creating rigorous, reproducible test suites and leaderboards to compare different prototype versions head-to-head.       |

### b. Querying Past Reports (Filtering & Querying)

| Platform      | "Search the Archives" Capabilities                                                                                  |
| :------------ | :------------------------------------------------------------------------------------------------------------------ |
| **OpenAI**    | Basic search by simple properties.                                                                                  |
| **Phoenix**   | Extremely powerful. You can load all your inspection reports into a code notebook and write complex queries to find specific results. |
| **W&B Weave** | A rich user interface for filtering, letting you find reports based on almost any measurement. You can save complex queries. |

### c. When to Use Each Toolkit (Key Strengths)

| Platform      | Unique Strength                                                                                                                                                               |
| :------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **OpenAI**    | **Simplicity & Zero Setup**. The fastest way to get basic measurements with no extra configuration. It just works.                                                                |
| **Phoenix**   | **Deep-Dive Diagnostics**. The best toolkit for the hands-on engineer who wants to run custom analytics and debug complex issues during the development phase.                  |
| **W&B Weave** | **Rigorous Experiment Tracking**. The best toolkit for teams that want to systematically track quality over time, compare prototype versions, and maintain a professional history of their testing. |
