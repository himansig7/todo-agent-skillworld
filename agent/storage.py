"""
This file defines the data access layer for the to-do list.

It provides an abstract base class for storage and two concrete implementations:
- `JsonTodoStorage`: Persists to-do items to a local JSON file.
- `InMemoryTodoStorage`: Stores to-do items in memory for transient sessions.

This separation of concerns makes the agent's tool code cleaner and allows
different application entry points (CLI, web app, tests) to use the storage
mechanism best suited to their needs.
"""

import os
import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# Define the path to the JSON data file relative to the project root.
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "todos.json")

class TodoStatus(str, Enum):
    """
    Enumeration for the status of a to-do item.
    Inherits from `str` to be easily JSON-serializable.
    """
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class TodoItem(BaseModel):
    """Represents a single to-do item in the list."""
    id: int
    name: str = Field(..., description="A short, clear name for the to-do item.")
    description: Optional[str] = Field(default=None, description="An optional, more detailed description of the to-do item.")
    project: Optional[str] = Field(default=None, description="An optional project name to group related tasks.")
    status: TodoStatus = Field(default=TodoStatus.NOT_STARTED, description="The current status of the to-do item.")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp (UTC ISO 8601).")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Last update timestamp (UTC ISO 8601).")


class AbstractTodoStorage(ABC):
    """Abstract base class defining the contract for to-do storage."""

    @abstractmethod
    def create(self, name: str, description: Optional[str], project: Optional[str]) -> TodoItem:
        """Creates a new to-do item and saves it."""
        pass

    @abstractmethod
    def read_all(self) -> List[TodoItem]:
        """Returns all to-do items."""
        pass

    @abstractmethod
    def read_by_id(self, item_id: int) -> Optional[TodoItem]:
        """Finds a single to-do item by its ID."""
        pass

    @abstractmethod
    def read_by_project(self, project: str) -> List[TodoItem]:
        """Finds all to-do items belonging to a specific project."""
        pass

    @abstractmethod
    def update(self, item_id: int, update_data: Dict[str, Any]) -> Optional[TodoItem]:
        """Updates an existing to-do item and saves the list."""
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        """Deletes a to-do item by its ID and saves the list."""
        pass


class JsonTodoStorage(AbstractTodoStorage):
    """Handles all persistence logic for the to-do list using a JSON file."""
    def __init__(self, path: str = DATA_PATH):
        self._path = path
        self._ensure_data_file()

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

    def _get_next_id(self, todos: List[TodoItem]) -> int:
        """Get the next available ID for a new to-do item."""
        return max([t.id for t in todos], default=0) + 1

    def create(self, name: str, description: Optional[str], project: Optional[str]) -> TodoItem:
        """Creates a new to-do item and saves it."""
        todos = self._load_todos()
        now = datetime.now(timezone.utc).isoformat()
        new_item = TodoItem(
            id=self._get_next_id(todos),
            name=name,
            description=description,
            project=project,
            created_at=now,
            updated_at=now,
        )
        todos.append(new_item)
        self._save_todos(todos)
        return new_item

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
        # Ensure case-insensitive matching for project names
        return [t for t in todos if t.project and t.project.lower() == project.lower()]

    def update(self, item_id: int, update_data: Dict[str, Any]) -> Optional[TodoItem]:
        """Updates an existing to-do item and saves the list."""
        todos = self.read_all()
        
        # Find the item by its unique ID
        for i, item in enumerate(todos):
            if item.id == item_id:
                # Explicitly convert status string to TodoStatus enum
                if "status" in update_data and isinstance(update_data["status"], str):
                    try:
                        update_data["status"] = TodoStatus(update_data["status"])
                    except ValueError:
                        pass  # Let Pydantic handle validation errors for invalid strings
                
                # Automatically update the timestamp
                update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

                updated_item = todos[i].model_copy(update=update_data)
                todos[i] = updated_item
                self._save_todos(todos)
                return updated_item
        
        return None  # Return None if the item_id was not found

    def delete(self, item_id: int) -> bool:
        """Deletes a to-do item by its ID and saves the list."""
        todos = self._load_todos()
        original_count = len(todos)
        new_todos = [t for t in todos if t.id != item_id]
        
        if len(new_todos) == original_count:
            return False
        
        self._save_todos(new_todos)
        return True


class InMemoryTodoStorage(AbstractTodoStorage):
    """Handles all persistence logic for the to-do list in memory."""
    def __init__(self):
        self._todos: List[TodoItem] = []
        self._next_id = 1

    def _get_next_id(self) -> int:
        """Get the next available ID for a new to-do item."""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def create(self, name: str, description: Optional[str], project: Optional[str]) -> TodoItem:
        now = datetime.now(timezone.utc).isoformat()
        new_item = TodoItem(
            id=self._get_next_id(),
            name=name,
            description=description,
            project=project,
            created_at=now,
            updated_at=now,
        )
        self._todos.append(new_item)
        return new_item

    def read_all(self) -> List[TodoItem]:
        return self._todos

    def read_by_id(self, item_id: int) -> Optional[TodoItem]:
        return next((t for t in self._todos if t.id == item_id), None)

    def read_by_project(self, project: str) -> List[TodoItem]:
        # Ensure case-insensitive matching for project names
        return [t for t in self._todos if t.project and t.project.lower() == project.lower()]

    def update(self, item_id: int, update_data: dict) -> Optional[TodoItem]:
        item_to_update = self.read_by_id(item_id)
        if not item_to_update:
            return None

        # Explicitly convert status string to TodoStatus enum
        if "status" in update_data and isinstance(update_data["status"], str):
            try:
                update_data["status"] = TodoStatus(update_data["status"])
            except ValueError:
                pass  # Let Pydantic handle validation errors

        # Update fields from the provided data
        for key, value in update_data.items():
            if hasattr(item_to_update, key):
                setattr(item_to_update, key, value)
        
        # Automatically update the timestamp
        item_to_update.updated_at = datetime.now(timezone.utc).isoformat()
        return item_to_update

    def delete(self, item_id: int) -> bool:
        original_count = len(self._todos)
        self._todos = [t for t in self._todos if t.id != item_id]
        return len(self._todos) < original_count 