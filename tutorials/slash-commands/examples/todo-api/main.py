"""Simple Todo API demonstrating slash command workflow."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="1.0.0")

DATABASE = "todos.db"


def init_db():
    """Initialize the database with the todos table."""
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)


@contextmanager
def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


class TodoCreate(BaseModel):
    """Schema for creating a todo."""

    title: str
    description: Optional[str] = None


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""

    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Todo(BaseModel):
    """Schema for a todo response."""

    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: str
    completed_at: Optional[str]


def row_to_todo(row: sqlite3.Row) -> Todo:
    """Convert a database row to a Todo."""
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
        created_at=row["created_at"],
        completed_at=row["completed_at"],
    )


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/todos", response_model=list[Todo])
def list_todos():
    """List all todos."""
    with get_db() as db:
        rows = db.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
        return [row_to_todo(row) for row in rows]


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    """Create a new todo."""
    created_at = datetime.utcnow().isoformat()
    with get_db() as db:
        cursor = db.execute(
            "INSERT INTO todos (title, description, created_at) VALUES (?, ?, ?)",
            (todo.title, todo.description, created_at),
        )
        todo_id = cursor.lastrowid
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return row_to_todo(row)


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    """Get a specific todo by ID."""
    with get_db() as db:
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        return row_to_todo(row)


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoUpdate):
    """Update a todo."""
    with get_db() as db:
        existing = db.execute(
            "SELECT * FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")

        updates = []
        values = []

        if todo.title is not None:
            updates.append("title = ?")
            values.append(todo.title)

        if todo.description is not None:
            updates.append("description = ?")
            values.append(todo.description)

        if todo.completed is not None:
            updates.append("completed = ?")
            values.append(int(todo.completed))
            if todo.completed and not existing["completed"]:
                updates.append("completed_at = ?")
                values.append(datetime.utcnow().isoformat())
            elif not todo.completed:
                updates.append("completed_at = ?")
                values.append(None)

        if updates:
            values.append(todo_id)
            db.execute(
                f"UPDATE todos SET {', '.join(updates)} WHERE id = ?",
                values,
            )

        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
        return row_to_todo(row)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a todo."""
    with get_db() as db:
        existing = db.execute(
            "SELECT * FROM todos WHERE id = ?", (todo_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")
        db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
