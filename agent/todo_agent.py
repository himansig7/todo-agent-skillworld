"""
This file defines the agent's identity, instructions, and available tools.

The tools defined here act as the bridge between the agent's reasoning
and the application's data layer in `storage.py`.
"""

import json
from typing import Optional, Any
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime, timezone
from agents import Agent, function_tool, RunContextWrapper, WebSearchTool
from agent.storage import TodoStorage

# -----------------------------------------------------------------------------
# Tool Definitions
# -----------------------------------------------------------------------------
# Note: The `ctx: RunContextWrapper[Any]` parameter is a placeholder for passing
# run-specific context to tools, such as user IDs or database connections.
# We don't use it in this simple app, but it's a best practice to include it.

@function_tool
def create_todo(
    ctx: RunContextWrapper[Any],
    name: str = Field(..., description="The name of the to-do item."),
    description: Optional[str] = Field(default=None, description="A detailed description of the to-do item."),
    project: Optional[str] = Field(default=None, description="A project name to group related tasks.")
) -> str:
    """Creates a new to-do item and adds it to the list."""
    try:
        storage = TodoStorage()
        item = storage.create(name, description, project)
        return f"Created to-do item {item.id}: {item.name}"
    except Exception as e:
        return f"Error creating to-do: {e}"

@function_tool
def read_todos(
    ctx: RunContextWrapper[Any],
    item_id: Optional[int] = Field(default=None, description="ID of a specific to-do item to read."),
    project: Optional[str] = Field(default=None, description="Filter to-do items by a specific project.")
) -> str:
    """Reads all to-do items, or a specific item/project if an ID or project name is provided."""
    try:
        storage = TodoStorage()
        if item_id is not None:
            item = storage.read_by_id(item_id)
            return item.model_dump_json(indent=2) if item else f"To-do item with id {item_id} not found."
        
        if project:
            project_todos = storage.read_by_project(project)
            if not project_todos:
                return f"No to-do items found for project '{project}'."
            return '[\n' + ',\n'.join([t.model_dump_json(indent=2) for t in project_todos]) + '\n]'
        
        all_todos = storage.read_all()
        return '[\n' + ',\n'.join([t.model_dump_json(indent=2) for t in all_todos]) + '\n]'
    except Exception as e:
        return f"Error reading to-dos: {e}"

@function_tool
def update_todo(
    ctx: RunContextWrapper[Any],
    item_id: int = Field(..., description="The ID of the to-do item to update."),
    name: Optional[str] = Field(default=None, description="The new name of the to-do item."),
    description: Optional[str] = Field(default=None, description="The new description of the to-do item."),
    project: Optional[str] = Field(default=None, description="The new project name for the to-do item."),
    completed: Optional[bool] = Field(default=None, description="The new completion status of the to-do item.")
) -> str:
    """Updates an existing to-do item's attributes."""
    try:
        storage = TodoStorage()
        update_data = {'name': name, 'description': description, 'project': project, 'completed': completed}
        update_fields = {k: v for k, v in update_data.items() if v is not None}

        if not update_fields:
            return "Error: No fields to update were provided."
        
        updated_item = storage.update(item_id, update_fields)
        return f"Updated to-do item {item_id}." if updated_item else f"To-do item with id {item_id} not found."
    except Exception as e:
        return f"Error updating to-do: {e}"

@function_tool
def delete_todo(
    ctx: RunContextWrapper[Any],
    item_id: int = Field(..., description="The ID of the to-do item to delete.")
) -> str:
    """Deletes a to-do item from the list by its ID."""
    try:
        storage = TodoStorage()
        if storage.delete(item_id):
            return f"Deleted to-do item {item_id}."
        else:
            return f"To-do item with id {item_id} not found."
    except Exception as e:
        return f"Error deleting to-do: {e}"

# -----------------------------------------------------------------------------
# Agent Prompt & Setup
# -----------------------------------------------------------------------------
AGENT_PROMPT = """
You are a professional Executive Assistant. Your sole responsibility is to manage the user's to-do list with precision and initiative.

You have a set of office supplies (tools) to manage the to-do list:
- `create_todo`: Use this to add a new task.
- `read_todos`: Use this to review existing tasks. You can view all tasks, or filter by a specific project.
- `update_todo`: Use this to modify an existing task, such as changing its name or marking it as complete.
- `delete_todo`: Use this to remove a task from the list.

You also have a `web_search` tool for research. Use it proactively to help the user clarify vague tasks. Your goal is to turn ambiguous requests into actionable to-do items.

**Your Professional Workflow:**
- When a user gives a vague task (e.g., "plan a trip"), don't just add it. Confirm the entry, then immediately offer to perform web research to gather necessary details.
- After research, propose specific, actionable to-do items. For example, after researching Mexico, suggest creating tasks like "Book flights to Mexico" and "Reserve hotel in Cancun."
- Always confirm actions with the user and use the precise tool for each operation. Maintain a professional and helpful tone.

**Example Interaction Flow:**
- **User**: "Add 'plan my trip' to my list."
- **Assistant**: (Calls `create_todo` with name="plan my trip"). "Of course. I've added 'plan my trip' to your list. To make this more actionable, may I research potential destinations for you?"
- **User**: "I'm not sure, maybe somewhere warm in December. Can you look up some ideas?"
- **Assistant**: (Calls `web_search`). "My research shows that popular warm destinations in December include Hawaii, Mexico, and the Caribbean. Do any of these appeal to you?"
- **User**: "Mexico sounds great."
- **Assistant**: "Excellent. I will update the task to 'Plan trip to Mexico'." (Calls `update_todo` to change name). "Shall I also add 'Book flights to Mexico' and 'Book hotel in Mexico' to your to-do list?"

Your objective is to be a proactive partner who adds value, not just a passive note-taker.
"""

agent = Agent(
    name="To-Do Agent",
    model="gpt-4.1-mini",
    instructions=AGENT_PROMPT,
    tools=[create_todo, read_todos, update_todo, delete_todo, WebSearchTool()],
) 