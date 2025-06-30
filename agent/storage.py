"""
Handles reading and writing to the local todos.json file.
- Provides functions for CRUD operations on the JSON file
- Uses Pydantic for data validation
- Includes a factory for creating new TodoItem objects
"""

import os
import json
from typing import List, Any, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "todos.json")

class TodoItem(BaseModel):
    id: int
    content: str = Field(..., description="The text of the to-do item.")
    completed: bool = Field(default=False, description="Whether the to-do is completed.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp (UTC ISO 8601).")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp (UTC ISO 8601).")


def ensure_data_file():
    """Ensure the todos.json file exists."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w") as f:
            json.dump([], f)


def load_todos() -> List[TodoItem]:
    """Load all todos from the JSON file and validate with Pydantic."""
    ensure_data_file()
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return [TodoItem(**item) for item in data]


def save_todos(todos: List[TodoItem]):
    """Save all todos to the JSON file."""
    with open(DATA_PATH, "w") as f:
        json.dump([item.model_dump() for item in todos], f, indent=2)


def get_next_id(todos: List[TodoItem]) -> int:
    """Get the next available ID for a new to-do item."""
    return max([t.id for t in todos], default=0) + 1


def create_todo_item(todos: List[TodoItem], content: str) -> TodoItem:
    """Factory to create a new TodoItem with a unique id and timestamps."""
    now = datetime.now(timezone.utc).isoformat()
    return TodoItem(
        id=get_next_id(todos),
        content=content,
        completed=False,
        created_at=now,
        updated_at=now,
    ) 