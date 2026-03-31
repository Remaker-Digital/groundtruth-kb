"""Task models and in-memory store.

Architecture decision ADR-001: We use an in-memory dict store instead of an
external database to keep the example focused on the GroundTruth method,
not on application database setup. Trade-off: data does not persist across
restarts. See the knowledge database for the full ADR.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

_VALID_TRANSITIONS: dict[str, set[str]] = {
    "created": {"in_progress"},
    "in_progress": {"done"},
    "done": set(),
}


class TaskStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    """Request body for creating a task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    assignee: str | None = None


class TaskUpdate(BaseModel):
    """Request body for updating a task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    assignee: str | None = None
    status: TaskStatus | None = None


class Task(BaseModel):
    """A task in the system."""

    id: str
    title: str
    description: str | None = None
    assignee: str | None = None
    status: TaskStatus = TaskStatus.created
    created_at: str = ""


class TaskStore:
    """In-memory task storage. No external database dependency (DCL-001)."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._counter: int = 0

    def create(self, data: TaskCreate) -> Task:
        """Create a new task and return it."""
        self._counter += 1
        task_id = f"TASK-{self._counter:04d}"
        task = Task(
            id=task_id,
            title=data.title,
            description=data.description,
            assignee=data.assignee,
            status=TaskStatus.created,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._tasks[task_id] = task.model_dump()
        return task

    def get(self, task_id: str) -> Task | None:
        """Get a task by ID, or None if not found."""
        data = self._tasks.get(task_id)
        return Task(**data) if data else None

    def list_all(self) -> list[Task]:
        """List all tasks in creation order."""
        return [Task(**d) for d in self._tasks.values()]

    def update(self, task_id: str, data: TaskUpdate) -> Task | None:
        """Update a task. Returns None if not found, raises ValueError on invalid transition."""
        existing = self._tasks.get(task_id)
        if existing is None:
            return None

        if data.status is not None:
            current = existing["status"]
            target = data.status.value
            if target not in _VALID_TRANSITIONS.get(current, set()):
                raise ValueError(
                    f"Invalid status transition: {current} → {target}. "
                    f"Valid transitions from '{current}': {sorted(_VALID_TRANSITIONS.get(current, set()))}"
                )
            existing["status"] = target

        if data.title is not None:
            existing["title"] = data.title
        if data.description is not None:
            existing["description"] = data.description
        if data.assignee is not None:
            existing["assignee"] = data.assignee

        return Task(**existing)

    def delete(self, task_id: str) -> bool:
        """Delete a task. Returns True if deleted, False if not found."""
        return self._tasks.pop(task_id, None) is not None
