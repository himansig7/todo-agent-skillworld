# Main entry point for data management tasks.

"""
Management script for the todo-agent project.

Provides CLI commands for common administrative tasks like resetting data,
seeding the database, and running evaluations.
"""

import typer
import json
import os

app = typer.Typer(
    help="A CLI for managing the to-do agent application.",
    add_completion=False
)

TODOS_PATH = os.path.join("data", "todos.json")
SESSION_PATH = os.path.join("data", "session_default.json")
DEFAULT_SEED_PATH = os.path.join("data", "seed_todos.json")

@app.command()
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt.")
):
    """
    Resets the to-do list and session history to a clean state.
    """
    if not yes:
        confirm = typer.confirm("Are you sure you want to delete all to-dos and session history?")
        if not confirm:
            print("Aborting.")
            raise typer.Abort()
    
    # Reset todos.json to an empty list
    with open(TODOS_PATH, "w") as f:
        json.dump([], f)
    
    # Reset session_default.json to an empty history
    with open(SESSION_PATH, "w") as f:
        json.dump({"history": []}, f)
        
    print("✅ To-do list and session history have been reset.")


@app.command()
def seed(
    file_path: str = typer.Argument(DEFAULT_SEED_PATH, help="Path to the seed JSON file.")
):
    """
    Seeds the to-do list with data from a JSON file.
    
    This command will overwrite the current to-do list.
    """
    # If a filename is provided without a directory, assume it's in the data/ directory.
    if not os.path.dirname(file_path):
        file_path = os.path.join("data", file_path)

    if not os.path.exists(file_path):
        print(f"Error: Seed file not found at '{file_path}'")
        raise typer.Exit(code=1)
        
    with open(file_path, "r") as f:
        seed_data = json.load(f)
    
    with open(TODOS_PATH, "w") as f:
        json.dump(seed_data, f, indent=2)
    
    print(f"✅ To-do list has been seeded from '{file_path}'.")


if __name__ == "__main__":
    app() 