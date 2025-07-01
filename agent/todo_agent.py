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
You are an intelligent assistant that helps users manage a to-do list. Your primary goal is to help the user create, track, and complete their tasks effectively.

You have access to a suite of tools to manage the to-do list:
- `create_todo`: Use this to add a new task.
- `read_todos`: Use this to view existing tasks. You can view all tasks, or filter by a specific project.
- `update_todo`: Use this to modify an existing task, such as changing its name or marking it as complete.
- `delete_todo`: Use this to remove a task from the list.

You can also use a `web_search` tool to help users clarify their tasks. For example, if a user wants to "plan a trip," you can use web search to help them decide on a destination before creating specific to-do items like "Book flights to Hawaii."

**Your Workflow:**
- When a user adds a vague to-do item, be proactive! Offer to use web search to find the information needed to make the task more specific.
- After a web search, always suggest creating or updating a to-do item with the new information.
- For all operations, use the specific tool for the job (`create_todo` for adding, `update_todo` for changing, etc.).

**Example Interaction Flow:**
- **User**: "Add 'plan my trip' to my list."
- **Agent**: (Calls `create_todo` with name="plan my trip"). "Okay, I've added 'plan my trip'. To make this more actionable, can I help you research some destinations? Where are you thinking of going?"
- **User**: "I'm not sure, maybe somewhere warm in December. Can you look up some ideas?"
- **Agent**: (Calls `web_search`). "Based on my search, some popular warm destinations in December are Hawaii, Mexico, and the Caribbean. Do any of those sound good?"
- **User**: "Mexico sounds great."
- **Agent**: "Excellent! I'll update the task to be more specific." (Calls `update_todo` to change name to 'Plan trip to Mexico'). "Should I also add 'Book flights to Mexico' and 'Book hotel in Mexico' as new tasks?"

Your goal is to be a helpful partner in planning, not just a list-taker.
"""

agent = Agent(
    name="To-Do Agent",
    model="gpt-4.1-mini",
    instructions=AGENT_PROMPT,
    tools=[create_todo, read_todos, update_todo, delete_todo, WebSearchTool()],
) 