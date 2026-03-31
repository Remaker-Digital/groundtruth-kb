"""Test fixtures for the Task Tracker API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from task_tracker.app import app, store


@pytest.fixture(autouse=True)
def _reset_store():
    """Reset the in-memory store before each test."""
    store._tasks.clear()
    store._counter = 0
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
