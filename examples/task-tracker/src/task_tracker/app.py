"""Task Tracker API — FastAPI application.

A minimal REST API demonstrating the GroundTruth method. Each endpoint
is linked to a specification in the knowledge database.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from task_tracker.models import Task, TaskCreate, TaskStore, TaskUpdate

app = FastAPI(title="Task Tracker", version="0.1.0")
store = TaskStore()


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate) -> Task:
    """Create a new task with a title and optional description. (SPEC-001)"""
    return store.create(body)


@app.get("/tasks")
def list_tasks() -> list[Task]:
    """List all tasks in creation order. (SPEC-004)"""
    return store.list_all()


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> Task:
    """Get a task by ID. Returns 404 if not found. (SPEC-005)"""
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: str, body: TaskUpdate) -> Task:
    """Update a task's fields or transition its status. (SPEC-002, SPEC-003)"""
    try:
        task = store.update(task_id, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str) -> None:
    """Delete a task. Returns 204 on success, 404 if not found. (SPEC-005)"""
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
