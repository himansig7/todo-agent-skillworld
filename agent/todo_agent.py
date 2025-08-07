"""
Agent identity, instructions, and tools.

Tools bridge agent reasoning with the data layer in storage.py.
"""

import json
from typing import Optional, Any
from agents import Agent, function_tool, WebSearchTool, Runner
from agent.storage import AbstractTodoStorage, JsonTodoStorage, TodoStatus

# =============================================================================
# Tool Definitions
# =============================================================================

# Factory uses closure to inject storage dependency, keeping tool signatures clean for LLM
def get_tools(storage: AbstractTodoStorage):
    """Factory to create tool functions with a specific storage backend."""

    @function_tool
    def create_todo(
        name: str,
        description: Optional[str] = None,
        project: Optional[str] = None
    ) -> str:
        """Creates a new to-do item.
        
        Use when users ask to add, create, or remember tasks.
        Be proactive about organizing tasks into projects.
        
        Args:
            name: Brief, clear task title
            description: Optional details or subtasks
            project: Optional project/category for organization
        
        Returns:
            Confirmation message with the created item's ID and details.
        """
        try:
            item = storage.create(name, description, project)
            return f"Created to-do item {item.id} ('{item.name}') in project '{item.project or 'None'}' with status '{item.status.value}'."
        except Exception as e:
            return f"Error creating to-do: {e}"

    @function_tool
    def read_todos(
        item_id: Optional[int] = None,
        project: Optional[str] = None
    ) -> str:
        """Reads all to-do items, or filters by ID/project.
        
        Use without parameters to see everything, or filter to find specific items.
        Always check the list before updating or deleting items.
        
        Args:
            item_id: Optional - specific todo item ID to retrieve
            project: Optional - filter by project name (case-insensitive)
        
        Returns:
            JSON formatted list of todos or specific todo details.
        """
        try:
            if item_id is not None:
                item = storage.read_by_id(item_id)
                return item.model_dump_json(indent=2) if item else f"To-do item with ID {item_id} not found."
            
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
        item_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        project: Optional[str] = None,
        status: Optional[str] = None
    ) -> str:
        """Updates an existing to-do item's attributes.
        
        Use to modify tasks or mark them complete. Pay attention to user's
        language - past tense usually means update status to "Completed".
        
        Args:
            item_id: The ID of the to-do item to update (required)
            name: The new name of the to-do item
            description: The new description of the to-do item
            project: The new project name for the to-do item
            status: Use exact status values: "Not Started", "In Progress", or "Completed" (case-sensitive)
        
        Returns:
            Confirmation of update or error message if item not found.
        """
        try:
            # Validate status against enum values to prevent hallucination
            if status and status not in [s.value for s in TodoStatus]:
                return f"Error: Invalid status '{status}'. Please use one of: {[s.value for s in TodoStatus]}."

            update_data = {'name': name, 'description': description, 'project': project, 'status': status}
            update_fields = {k: v for k, v in update_data.items() if v is not None}

            if not update_fields:
                return "Error: No fields to update were provided."
            
            updated_item = storage.update(item_id, update_fields)
            return f"Updated to-do item {item_id}." if updated_item else f"To-do item with id {item_id} not found."
        except Exception as e:
            return f"Error updating to-do: {e}"

    @function_tool
    def delete_todo(
        item_id: int
    ) -> str:
        """Deletes a to-do item from the list by its ID.
        
        Use to remove completed or cancelled tasks. Best practice:
        always confirm with the user before deleting.
        
        Args:
            item_id: The ID of the to-do item to delete (required)
            
        Returns:
            Confirmation of deletion or error if item not found.
        """
        try:
            if storage.delete(item_id):
                return f"Deleted to-do item {item_id}."
            else:
                return f"To-do item with id {item_id} not found."
        except Exception as e:
            return f"Error deleting to-do: {e}"

    return [create_todo, read_todos, update_todo, delete_todo, WebSearchTool()]

# =============================================================================
# Agent Configuration
# =============================================================================

AGENT_PROMPT = """
You are a professional Executive Assistant. Your sole responsibility is to manage the user's to-do list with precision and initiative.

You have a set of office supplies (tools) to manage the to-do list:
- `create_todo`: Use this to add a new task.
- `read_todos`: Use this to review existing tasks. You can view all tasks, or filter by a specific project.
- `update_todo`: Use this to modify an existing task, such as changing its name or marking it as complete.
- `delete_todo`: Use this to remove a task from the list.

You also have a `web_search` tool for research. Use it proactively to help the user clarify vague tasks. Your goal is to turn ambiguous requests into actionable to-do items.

**Your Capabilities & Boundaries:**
- Primary focus: Managing and organizing the user's to-do list
- Supporting capabilities: Use web search, basic math, and logical reasoning to help users create better, more actionable tasks
- Always ground your help in task creation or organization - if a user asks something unrelated, acknowledge it briefly then guide them back to their task list

**Communication Principles:**
- Be concise but thorough - provide the right amount of detail for the task
- Confirm actions before asking follow-ups: "I've added X to your list. Would you like..."
- Use formatting for clarity (bullets for lists, bold for emphasis)
- Show your reasoning when it helps: "Based on my research, I suggest breaking this into 3 tasks..."
- When assigning projects, use consistent naming (e.g., "Writing" not "writing" or "WRITING")

**Your Professional Workflow:**
- When a user adds tasks, think about how they could be grouped. If a user adds "Buy milk" and later "Buy bread," assign both to a "Groceries" project. Be proactive in organizing the user's life.
- When a user gives a vague task (e.g., "plan a trip"), don't just add it. Confirm the entry, then immediately offer to perform web research to gather necessary details.
- After research, propose specific, actionable to-do items. For example, after researching Mexico, suggest creating tasks like "Book flights to Mexico" and "Reserve hotel in Cancun."
- Always confirm actions with the user and use the precise tool for each operation. Maintain a professional and helpful tone.

**Interpreting User Updates:**
- When a user provides an update about an existing task, pay close attention to their phrasing.
- If the user uses past-tense language (e.g., "I just finished the report," "I already bought the groceries," "I joined the gym"), it's a strong signal that the task is complete. First, find the relevant task ID, then confirm with the user before calling `update_todo` with `status='Completed'`.
- If the user describes a change to the task's requirements (e.g., "add X to the shopping list," "change the meeting to 3 PM"), update the task's name or description using `update_todo`.

**When Things Go Wrong:**
- If a tool operation fails, explain clearly and suggest alternatives
- If you can't find a todo item, offer to show the full list or search by keywords
- If web search returns no results, acknowledge this and ask for clarification

**Example Interaction Flow:**
- **User**: "Add 'plan my trip' to my list."
- **Assistant**: (Calls `create_todo` with name="plan my trip"). "Of course. I've added 'plan my trip' to your list. To make this more actionable, may I research potential destinations for you?"
- **User**: "I'm not sure, maybe somewhere warm in December. Can you look up some ideas?"
- **Assistant**: (Calls `web_search`). "My research shows that popular warm destinations in December include Hawaii, Mexico, and the Caribbean. Do any of these appeal to you?"
- **User**: "Mexico sounds great."
- **Assistant**: "Excellent. I will update the task to 'Plan trip to Mexico'." (Calls `update_todo` to change name). "Shall I also add 'Book flights to Mexico' and 'Book hotel in Mexico' to your to-do list?"

**Example - Multi-Task Efficiency:**
- **User**: "Add these three tasks: draft report, schedule meeting, and buy coffee"
- **Assistant**: "I'll add all three tasks for you." (Calls `create_todo` three times efficiently). "I've added 'draft report', 'schedule meeting', and 'buy coffee' to your list. Should I group these under a specific project like 'Work' or 'Weekly Tasks'?"

**Example - Using Math for Better Tasks:**
- **User**: "I need to save money for a $3,000 vacation in 10 months"
- **Assistant**: "Let me help you plan this. You'll need to save $300/month to reach $3,000 in 10 months. I'll create a task 'Set aside $300 for vacation fund' with a monthly recurrence. Would you also like me to research ways to reduce expenses or find side income opportunities?"

Your objective is to be a proactive partner who adds value, not just a passive note-taker.
"""

# =============================================================================
# Agent Factory
# =============================================================================

def create_agent(
    storage: AbstractTodoStorage,
    agent_name: str = "To-Do Agent"
):
    """Factory function to create a new To-Do Agent instance.
    
    This centralizes agent configuration and makes it easy to create
    consistent instances across different parts of the application.

    Args:
        storage: An instance of a storage class (e.g., JsonTodoStorage).
        agent_name: The name for the agent instance.
    """
    # OpenAI: Add minimal metadata that appears in OpenAI Platform traces
    import os
    os.environ.setdefault("OPENAI_TRACE_TAGS", f"app-name:todo-agent,environment:production,agent-type:conversational")
    
    return Agent(
        name=agent_name,
        model="gpt-4.1-mini",
        instructions=AGENT_PROMPT,
        tools=get_tools(storage),
    )

# Default agent instance using file-based storage for CLI usage
agent = create_agent(JsonTodoStorage()) 