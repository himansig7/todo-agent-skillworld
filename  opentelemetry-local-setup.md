# OpenTelemetry Local Install & Setup Guide (with Traceloop / OpenLLMetry)

This guide explains how to install and run **OpenTelemetry** locally, integrate with **Traceloop** (OpenLLMetry), and verify traces.

---

## 1. Prerequisites

Before installing:

- **Python** ≥ 3.9 installed
- **pip** available
- **virtualenv** (optional but recommended)
- (Optional) **Homebrew** (macOS) if installing tools globally

---

## 2. Create a Virtual Environment

```bash
# Create and activate a Python venv
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

3. Install Required Packages

    #Install the OpenTelemetry SDK and exporters:

    pip install opentelemetry-api \
                opentelemetry-sdk \
                opentelemetry-exporter-otlp \
                opentelemetry-exporter-otlp-proto-http

    #If using Traceloop / OpenLLMetry:
        pip install traceloop-sdk

    #If using OpenAI or LangChain:
        pip install openai langchain

4. Get Your Traceloop API Key

    Go to https://app.traceloop.com/ and log in.
    In the left sidebar, click Settings → API Keys.
    Choose the correct Environment (Development).
    Click Create API Key.
    Copy the generated key — keep it secure.

5. Environment Variables

Set your API key in a .env file in the project root:

TRACELOOP_API_KEY=your_api_key_here
TRACELOOP_TRACE_CONTENT=false  # optional: disable raw prompt logging

If you’re sending to a generic OTLP collector:

OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
OTEL_SERVICE_NAME=my-service

6. Minimal Test Script

Create otel_test.py:

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("test-span"):
    print("Hello from OpenTelemetry!")

print("Tracing complete.")

Run:

python otel_test.py

You should see a JSON-like span output in your console.
7. Sending Data to Traceloop (OpenLLMetry)

Example integration:

from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

Traceloop.init(app_name="my-app", disable_batch=True)

@workflow(name="demo_workflow")
def my_flow():
    print("Workflow executed!")

my_flow()

Check traces at:
https://app.traceloop.com/ → Traces