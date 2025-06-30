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
    """Arguments for the todo_crud tool."""
    action: Literal["create", "read", "update", "delete"]
    item_id: Optional[int]
    name: Optional[str]
    description: Optional[str]
    project: Optional[str]
    completed: Optional[bool]

# -----------------------------------------------------------------------------
# CRUD Function Tool
# -----------------------------------------------------------------------------
@function_tool
def todo_crud(
    ctx: RunContextWrapper[Any], 
    action: Literal["create", "read", "update", "delete"], 
    item_id: Optional[int] = None, 
    name: Optional[str] = None, 
    description: Optional[str] = None, 
    project: Optional[str] = None, 
    completed: Optional[bool] = None
) -> str:
    """
    Perform CRUD operations on the to-do list.

    Args:
        action: 'create', 'read', 'update', or 'delete'.
        item_id: ID of the to-do item (for update/delete/read).
        name: The name of the to-do item (for create/update).
        description: A detailed description of the to-do item (for create/update).
        project: A project name to group related tasks (for create/update).
        completed: The completion status of the to-do item (for update).
    Returns:
        str: Result message or data.
    """
    try:
        todos = load_todos()
        if action == "create":
            if not name:
                return "Error: 'name' is required for create."
            item = create_todo_item(todos, name, description, project)
            todos.append(item)
            save_todos(todos)
            return f"Created to-do item {item.id}: {name}"
        elif action == "read":
            if item_id is not None:
                for t in todos:
                    if t.id == item_id:
                        return t.model_dump_json(indent=2)
                return f"To-do item with id {item_id} not found."
            else:
                # Filter by project if provided
                if project:
                    project_todos = [t for t in todos if t.project == project]
                    if not project_todos:
                        return f"No to-do items found for project '{project}'."
                    return '[\n' + ',\n'.join([t.model_dump_json(indent=2) for t in project_todos]) + '\n]'
                return '[\n' + ',\n'.join([t.model_dump_json(indent=2) for t in todos]) + '\n]'
        elif action == "update":
            if item_id is None:
                return "Error: 'item_id' is required for update."
            
            item_updated = False
            for t in todos:
                if t.id == item_id:
                    if name is not None:
                        t.name = name
                        item_updated = True
                    if description is not None:
                        t.description = description
                        item_updated = True
                    if project is not None:
                        t.project = project
                        item_updated = True
                    if completed is not None:
                        t.completed = completed
                        item_updated = True
                    
                    if item_updated:
                        t.updated_at = datetime.now(timezone.utc).isoformat()
                        save_todos(todos)
                        return f"Updated to-do item {item_id}."
                    else:
                        return "Error: No fields to update were provided."
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
You are an intelligent assistant that manages a to-do list for the user.
You support creating, reading, updating, and deleting to-do items. Each to-do item has the following structure:
- `name`: A short, clear name for the task (required).
- `description`: An optional, more detailed description.
- `project`: An optional project name to group related tasks. This is great for tracking sub-tasks.
- `completed`: A flag to mark the task as done.

Use the 'todo_crud' tool for all operations.

Instructions:
- To add a new to-do, you must provide at least a `name`. You can also include a `description` and a `project`.
- To create sub-tasks, use the same `project` name for all related to-dos.
- To view all to-dos, ask to "list" or "show" items. You can also ask to see all tasks for a specific `project`.
- To update a to-do, specify the item `item_id` and the new `name`, `description`, `project`, or `completed` status.
- To mark a task as done, use the 'update' action with `item_id` and set `completed` to `True`.
- To delete a to-do, specify the `item_id`.

Example interactions:
- "I need to build a bookshelf." (You might ask if this is a project and suggest creating sub-tasks).
- "Create a project called 'Build Bookshelf' with these tasks: Design bookshelf, Buy materials, Assemble bookshelf."
- "Show my 'Build Bookshelf' project tasks."
- "Update item 3, set the description to 'Buy materials from Home Depot'."
- "Mark task 2 as completed."
- "Delete item 5."

Always confirm actions and provide clear feedback. Be proactive and help the user structure their tasks effectively.
"""

agent = Agent(
    name="To-Do Agent",
    model="gpt-4.1-mini",
    instructions=AGENT_PROMPT,
    tools=[todo_crud],
)

# TODO: Add tracing/observation integrations as needed 