"""
Core agent logic for the todo-agent project.
- Integrates with OpenAI Agents SDK
- Handles CRUD operations for to-do items via a single function tool
- Connects to tracing/observation libraries
"""

import json
from typing import Optional, Any, TypedDict, Literal
from pydantic import ValidationError
from datetime import datetime, timezone
from agents import Agent, function_tool, RunContextWrapper
from agent.storage import TodoItem, load_todos, save_todos, get_next_id, create_todo_item

# -----------------------------------------------------------------------------
# Tool Argument Schema
# -----------------------------------------------------------------------------
class TodoCrudArgs(TypedDict, total=False):
    action: Literal["create", "read", "update", "delete"]
    item_id: Optional[int]
    content: Optional[str]
    completed: Optional[bool]

# -----------------------------------------------------------------------------
# CRUD Function Tool
# -----------------------------------------------------------------------------
@function_tool
def todo_crud(ctx: RunContextWrapper[Any], action: Literal["create", "read", "update", "delete"], item_id: Optional[int] = None, content: Optional[str] = None, completed: Optional[bool] = None) -> str:
    """
    Perform CRUD operations on the to-do list.

    Args:
        action: 'create', 'read', 'update', or 'delete'
        item_id: ID of the to-do item (for update/delete/read)
        content: Content for create/update
        completed: Completed status for update
    Returns:
        str: Result message or data
    """
    try:
        todos = load_todos()
        if action == "create":
            if not content:
                return "Error: 'content' is required for create."
            item = create_todo_item(todos, content)
            todos.append(item)
            save_todos(todos)
            return f"Created to-do item {item.id}: {content}"
        elif action == "read":
            if item_id is not None:
                for t in todos:
                    if t.id == item_id:
                        return t.model_dump_json(indent=2)
                return f"To-do item with id {item_id} not found."
            else:
                return '[\n' + ',\n'.join([t.model_dump_json(indent=2) for t in todos]) + '\n]'
        elif action == "update":
            if item_id is None:
                return "Error: 'item_id' is required for update."
            for t in todos:
                if t.id == item_id:
                    if content is not None:
                        t.content = content
                    if completed is not None:
                        t.completed = completed
                    t.updated_at = datetime.now(timezone.utc).isoformat()
                    save_todos(todos)
                    return f"Updated to-do item {item_id}."
            return f"To-do item with id {item_id} not found."
        elif action == "delete":
            if item_id is None:
                return "Error: 'item_id' is required for delete."
            new_todos = [t for t in todos if t.id != item_id]
            if len(new_todos) == len(todos):
                return f"To-do item with id {item_id} not found."
            save_todos(new_todos)
            return f"Deleted to-do item {item_id}."
        else:
            return "Error: Unknown action. Use 'create', 'read', 'update', or 'delete'."
    except ValidationError as ve:
        return f"Validation error: {ve}"
    except Exception as e:
        return f"Unexpected error: {e}"

# -----------------------------------------------------------------------------
# Agent Prompt & Setup
# -----------------------------------------------------------------------------
AGENT_PROMPT = """
You are a helpful assistant that manages a to-do list for the user.
You support the following actions: create, read, update, and delete to-do items.
Use the 'todo_crud' tool for all operations.

Instructions:
- To add a new to-do, specify the content.
- To view all to-dos, ask to list or show items.
- To update a to-do, specify the item ID and new content.
- To delete a to-do, specify the item ID.

Example interactions:
- 'Add a to-do: Buy groceries.'
- 'Show my to-do list.'
- 'Update to-do 2 to: Buy groceries and milk.'
- 'Delete to-do 3.'

Always confirm actions and provide clear feedback.
"""

agent = Agent(
    name="To-Do Agent",
    model="gpt-4.1-mini"
    instructions=AGENT_PROMPT,
    tools=[todo_crud],
)

# TODO: Add tracing/observation integrations as needed 