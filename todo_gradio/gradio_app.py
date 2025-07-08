import os
import pandas as pd
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
import gradio as gr
from agents import Agent, function_tool, RunContextWrapper, WebSearchTool, Runner
from phoenix.otel import register
import weave

# Add parent directory to path for local imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.todo_agent import create_agent
from agent.storage import InMemoryTodoStorage, TodoStatus

def initialize_tracing():
    """Initializes Phoenix and Weave tracing for the application."""
    project_name = "todo-agent-gradio"

    os.environ["OPENAI_TRACING_ENABLED"] = "1"
    os.environ["WEAVE_PRINT_CALL_LINK"] = "false"

    # Prevent re-initialization on hot-reload
    if not weave.get_client():
        try:
            register(project_name=project_name, auto_instrument=True)
            weave.init(project_name=project_name)
            print(f"Tracing initialized for project: '{project_name}'")
        except Exception as e:
            print(
                f"Warning: Tracing initialization failed. The app will work, but traces will not be captured. Error: {e}"
            )

initialize_tracing()

def format_todos_for_display(todos: list) -> pd.DataFrame:
    """
    Formats the to-do list for display in the Gradio DataFrame.
    This is a "ViewModel" transformation, adapting the data model for the UI.
    """
    if not todos:
        return pd.DataFrame(columns=["ID", "Status", "Task", "Details", "Project", "Created"])
    
    df = pd.DataFrame([t.model_dump() for t in todos])
    
    # Rename for user-friendly headers
    df.rename(columns={
        'id': 'ID',
        'name': 'Task',
        'description': 'Details',
        'project': 'Project',
        'status': 'Status',
        'created_at': 'Created'
    }, inplace=True)
    
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d %H:%M')
    df['Project'] = df['Project'].fillna('')
    
    display_df = df[['ID', 'Status', 'Task', 'Details', 'Project', 'Created']]
    
    return display_df

async def agent_chat(user_input: str, chat_history: list, storage_instance: InMemoryTodoStorage):
    """Handles chat interaction between user and agent."""
    chat_history.append({"role": "user", "content": user_input})
    
    agent = create_agent(
        storage=storage_instance,
        agent_name="To-Do Agent (Gradio)"
    )

    result = await Runner.run(agent, input=chat_history)
    full_history = result.to_input_list()
    
    # Hide raw tool calls in display
    display_history = []
    for msg in full_history:
        role = msg.get("role")
        content = msg.get("content")
        
        if role == "user":
            display_history.append(msg)
        elif role == "assistant":
            if content:
                display_content = ""
                # Handle streaming response chunks
                if isinstance(content, list):
                    display_content = "".join(chunk.get('text', '') for chunk in content if isinstance(chunk, dict))
                elif isinstance(content, dict) and 'text' in content:
                    display_content = content['text']
                else:
                    display_content = str(content)
                
                if display_content:
                    display_history.append({"role": "assistant", "content": display_content})
            elif msg.get("tool_calls"):
                display_history.append({"role": "assistant", "content": "🛠️ Thinking..."})
    
    todos = storage_instance.read_all()
    df = format_todos_for_display(todos)
        
    return "", display_history, full_history, storage_instance, df

async def refresh_todos_df(storage_instance: InMemoryTodoStorage):
    """Callback to manually refresh the to-do list display."""
    todos = storage_instance.read_all()
    return format_todos_for_display(todos)

with gr.Blocks(theme=gr.themes.Soft(), title="To-Do Agent") as demo:
    gr.Markdown("# To-Do Agent")
    gr.Markdown("Manage your to-do list with an AI assistant. The agent can create, read, update, and delete tasks. It can also use web search to help you flesh out your ideas.")
    
    storage_state = gr.State(InMemoryTodoStorage)
    chat_history_state = gr.State([])
    
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

    send_button.click(
        agent_chat,
        inputs=[user_input_box, chat_history_state, storage_state],
        outputs=[user_input_box, chatbot, chat_history_state, storage_state, todo_df]
    )
    user_input_box.submit(
        agent_chat,
        inputs=[user_input_box, chat_history_state, storage_state],
        outputs=[user_input_box, chatbot, chat_history_state, storage_state, todo_df]
    )
    refresh_button.click(
        refresh_todos_df,
        inputs=[storage_state],
        outputs=[todo_df]
    )
    
    def initial_load():
        """Returns the initial state for the UI components."""
        return format_todos_for_display([]), [], InMemoryTodoStorage()
    
    demo.load(initial_load, None, [todo_df, chatbot, storage_state])


if __name__ == "__main__":
    demo.launch()