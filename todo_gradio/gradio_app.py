# 1. Imports
import os
import asyncio
import uuid
import pandas as pd
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
import gradio as gr

# Third-party for agent
from agents import Agent, function_tool, RunContextWrapper, WebSearchTool, Runner

# Tracing imports
from phoenix.otel import register
import weave

# Local application imports
# We need to adjust sys.path to import from the parent directory,
# which is a common pattern in Python applications to resolve modules.
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.todo_agent import AGENT_PROMPT, get_tools
from agent.storage import InMemoryTodoStorage, TodoStatus

# 2. Tracing Setup
# For educational purposes, this shows how to set up tracing for a web application.
# Each session gets a unique Phoenix trace to avoid mixing data, while all
# sessions are logged to a single, static Weave project for easier aggregation.
def initialize_tracing():
    """Initializes Phoenix and Weave tracing for the application."""
    # Phoenix can handle dynamic project names better for session isolation.
    # Weave will use a single project to avoid auth/creation issues in a serverless context.
    session_id = str(uuid.uuid4())[:8]
    project_name_phoenix = f"todo-gradio-phoenix-{session_id}"
    project_name_weave = "todo-agent-gradio"  # Static project name for Weave

    os.environ["OPENAI_TRACING_ENABLED"] = "1"
    os.environ["WEAVE_PRINT_CALL_LINK"] = "false" # Keep the console clean
    
    # Check if tracing is already initialized to prevent errors on hot-reload
    if not weave.get_client():
        try:
            register(project_name=project_name_phoenix, auto_instrument=True)
            weave.init(project_name=project_name_weave)
            print(f"Tracing initialized for Weave project '{project_name_weave}' and Phoenix session '{session_id}'")
        except Exception as e:
            print(f"Warning: Tracing initialization failed. The app will work, but traces will not be captured. Error: {e}")

initialize_tracing()

# 3. Data Formatting Helper
def format_todos_for_display(todos: list) -> pd.DataFrame:
    """
    Formats the to-do list for display in the Gradio DataFrame.
    This is a "ViewModel" transformation, adapting the data model for the UI.
    """
    if not todos:
        # Define columns even for an empty DataFrame to ensure consistent UI.
        return pd.DataFrame(columns=["ID", "Status", "Task", "Details", "Project", "Created"])
    
    # Convert list of Pydantic models to a Pandas DataFrame
    df = pd.DataFrame([t.model_dump() for t in todos])
    
    # --- Data Transformations for Readability ---
    # 1. Rename columns for a more user-friendly header
    df.rename(columns={
        'id': 'ID',
        'name': 'Task',
        'description': 'Details',
        'project': 'Project',
        'status': 'Status',
        'created_at': 'Created'
    }, inplace=True)
    
    # 2. Format the 'Created At' timestamp for better readability
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d %H:%M')
    
    # 3. Fill missing 'Project' values with an empty string for a cleaner look
    df['Project'] = df['Project'].fillna('')

    # 4. Select and reorder columns for the final display
    display_df = df[['ID', 'Status', 'Task', 'Details', 'Project', 'Created']]
    
    return display_df

# 4. Gradio App Logic
async def agent_chat(user_input: str, chat_history: list, storage_instance: InMemoryTodoStorage):
    """
    Core function that handles the chat interaction between the user and the agent.
    This function is called every time the user sends a message.
    """
    # Append the new user message to the conversation history
    chat_history.append({"role": "user", "content": user_input})
    
    # Create a new, stateless agent for each turn, configured with the session's storage.
    agent = Agent(
        name="To-Do Agent (Gradio)",
        model="gpt-4.1-mini",
        instructions=AGENT_PROMPT,
        tools=get_tools(storage_instance), # Critically, we pass the session's in-memory storage
    )

    # Use the Runner to execute the agent with the latest chat history
    result = await Runner.run(agent, input=chat_history)
    
    # The result contains the full history, which we use to update our session state.
    full_history = result.to_input_list()
    
    # Create a clean "display history" for the UI, hiding raw tool calls.
    display_history = []
    for msg in full_history:
        role = msg.get("role")
        content = msg.get("content")
        
        if role == "user":
            display_history.append(msg)
        elif role == "assistant":
            # If the assistant message is a text response, add it directly.
            if content:
                display_content = ""
                # Handle the case where the content is a list of response chunks from streaming
                if isinstance(content, list):
                    display_content = "".join(chunk.get('text', '') for chunk in content if isinstance(chunk, dict))
                # Handle a single response chunk
                elif isinstance(content, dict) and 'text' in content:
                    display_content = content['text']
                else: # Fallback for simple string content
                    display_content = str(content)
                
                if display_content:
                    display_history.append({"role": "assistant", "content": display_content})
            # For tool calls, show a user-friendly placeholder instead of the raw JSON.
            elif msg.get("tool_calls"):
                display_history.append({"role": "assistant", "content": "🛠️ Thinking..."})
    
    # Refresh the to-do list DataFrame with the latest data from storage
    todos = storage_instance.read_all()
    df = format_todos_for_display(todos)
        
    # Return all updated state variables to Gradio
    return "", display_history, full_history, storage_instance, df

async def refresh_todos_df(storage_instance: InMemoryTodoStorage):
    """Callback to manually refresh the to-do list display."""
    todos = storage_instance.read_all()
    return format_todos_for_display(todos)

# 5. Gradio UI Layout
# `gr.Blocks` allows for more complex and custom UI layouts.
with gr.Blocks(theme=gr.themes.Soft(), title="To-Do Agent") as demo:
    gr.Markdown("# To-Do Agent")
    gr.Markdown("Manage your to-do list with an AI assistant. The agent can create, read, update, and delete tasks. It can also use web search to help you flesh out your ideas.")
    
    # `gr.State` holds non-visible, session-specific data (storage and history).
    storage_state = gr.State(InMemoryTodoStorage) # Each user gets their own in-memory storage
    chat_history_state = gr.State([]) # Each user gets their own chat history
    
    # --- UI Components ---
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### To-Do List")
            todo_df = gr.DataFrame(
                interactive=False, 
                wrap=True,
                column_widths=["5%", "15%", "25%", "30%", "10%", "15%"]
            )
            refresh_button = gr.Button("Refresh List")
        
        with gr.Column(scale=1):
            gr.Markdown("### Chat")
            chatbot = gr.Chatbot(label="To-Do Agent Chat", type="messages", height=500)
            with gr.Row():
                user_input_box = gr.Textbox(placeholder="Type your message here...", show_label=False, scale=4)
                send_button = gr.Button("Send", variant="primary", scale=1)

    # --- Event Handlers ---
    # Connect the UI components to our Python logic.
    
    # Handle the "Send" button click
    send_button.click(
        agent_chat,
        inputs=[user_input_box, chat_history_state, storage_state],
        outputs=[user_input_box, chatbot, chat_history_state, storage_state, todo_df]
    )
    # Handle submitting text with the Enter key
    user_input_box.submit(
        agent_chat,
        inputs=[user_input_box, chat_history_state, storage_state],
        outputs=[user_input_box, chatbot, chat_history_state, storage_state, todo_df]
    )
    # Handle the "Refresh" button click
    refresh_button.click(
        refresh_todos_df,
        inputs=[storage_state],
        outputs=[todo_df]
    )
    
    # The `demo.load` event runs on page load to initialize the UI.
    def initial_load():
        """Returns the initial state for the UI components."""
        return format_todos_for_display([]), [], InMemoryTodoStorage()
    
    demo.load(initial_load, None, [todo_df, chatbot, storage_state])


if __name__ == "__main__":
    # Launch the Gradio app. `share=True` would create a public link.
    demo.launch()