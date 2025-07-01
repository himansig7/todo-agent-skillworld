"""
This file defines the data access layer for the to-do list.

It provides a TodoStorage class that encapsulates all persistence logic,
making the agent's tool code cleaner and easier to understand.
"""

import os
import json
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "todos.json")

class TodoItem(BaseModel):
    """Represents a single to-do item in the list."""
    id: int
    name: str = Field(..., description="A short, clear name for the to-do item.")
    description: Optional[str] = Field(default=None, description="An optional, more detailed description of the to-do item.")
    project: Optional[str] = Field(default=None, description="An optional project name to group related tasks.")
    completed: bool = Field(default=False, description="Whether the to-do is completed.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp (UTC ISO 8601).")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp (UTC ISO 8601).")


class TodoStorage:
    """Handles all persistence logic for the to-do list."""
    def __init__(self, path: str = DATA_PATH):
        self._path = path
        self._ensure_data_file()

    # -------------------------------------------------------------------------
    # "Private" Helper Methods
    #
    # These methods, prefixed with an underscore, are intended for internal
    # use within this class only. They handle the low-level details of
    # reading from and writing to the JSON file.
    # -------------------------------------------------------------------------
    def _ensure_data_file(self):
        """Ensure the todos.json file exists."""
        if not os.path.exists(self._path):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, "w") as f:
                json.dump([], f)

    def _load_todos(self) -> List[TodoItem]:
        """Load all todos from the JSON file and validate with Pydantic."""
        with open(self._path, "r") as f:
            data = json.load(f)
        return [TodoItem(**item) for item in data]

    def _save_todos(self, todos: List[TodoItem]):
        """Save all todos to the JSON file."""
        with open(self._path, "w") as f:
            json.dump([item.model_dump() for item in todos], f, indent=2)

    def get_next_id(self, todos: List[TodoItem]) -> int:
        """Get the next available ID for a new to-do item."""
        return max([t.id for t in todos], default=0) + 1

    # -------------------------------------------------------------------------
    # Public CRUD Methods
    #
    # These methods provide the public interface for the agent's tools to
    # interact with the to-do list. They handle the core logic for creating,
    # reading, updating, and deleting items.
    # -------------------------------------------------------------------------
    def create(self, name: str, description: Optional[str], project: Optional[str]) -> TodoItem:
        """Creates a new to-do item and saves it."""
        todos = self._load_todos()
        now = datetime.now(timezone.utc).isoformat()
        item = TodoItem(
            id=self.get_next_id(todos),
            name=name,
            description=description,
            project=project,
            completed=False,
            created_at=now,
            updated_at=now,
        )
        todos.append(item)
        self._save_todos(todos)
        return item

    def read_all(self) -> List[TodoItem]:
        """Returns all to-do items."""
        return self._load_todos()

    def read_by_id(self, item_id: int) -> Optional[TodoItem]:
        """Finds a single to-do item by its ID."""
        todos = self.read_all()
        return next((t for t in todos if t.id == item_id), None)

    def read_by_project(self, project: str) -> List[TodoItem]:
        """Finds all to-do items belonging to a specific project."""
        todos = self.read_all()
        return [t for t in todos if t.project == project]

    def update(self, item_id: int, update_data: dict) -> Optional[TodoItem]:
        """Updates an existing to-do item and saves the list."""
        todos = self.read_all()
        item_to_update = next((t for t in todos if t.id == item_id), None)
        if not item_to_update:
            return None

        for key, value in update_data.items():
            if value is not None:
                setattr(item_to_update, key, value)
        
        item_to_update.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_todos(todos)
        return item_to_update

    def delete(self, item_id: int) -> bool:
        """Deletes a to-do item by its ID and saves the list."""
        todos = self._load_todos()
        original_count = len(todos)
        new_todos = [t for t in todos if t.id != item_id]
        
        if len(new_todos) == original_count:
            return False
        
        self._save_todos(new_todos)
        return True 