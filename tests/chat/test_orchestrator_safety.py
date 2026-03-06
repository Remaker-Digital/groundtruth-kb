"""Tests for ChatPipeline async safety mechanisms.

Covers:
    - _create_background_task: GC-safe fire-and-forget with exception logging
    - _get_http_client: asyncio.Lock prevents race condition on lazy init
    - _background_tasks set lifecycle (add, discard on completion)
    - endpoints._background_tasks module-level set

Module under test: src/chat/pipeline/orchestrator.py, src/chat/endpoints.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers to build a minimal ChatPipeline without full dependency graph
# ---------------------------------------------------------------------------

def _make_pipeline():
    """Create a ChatPipeline with minimal mocked dependencies."""
    from src.chat.pipeline.orchestrator import ChatPipeline

    with patch.object(ChatPipeline, "_init_agents"):
        pipeline = ChatPipeline(
            session=MagicMock(),
            prompt_builder=MagicMock(),
            profile_service=MagicMock(),
        )
    return pipeline


# ---------------------------------------------------------------------------
# _create_background_task tests
# ---------------------------------------------------------------------------

class TestCreateBackgroundTask:
    """Verify fire-and-forget task lifecycle management."""

    @pytest.mark.asyncio
    async def test_task_added_to_background_set(self):
        """Task reference must be stored in _background_tasks to prevent GC."""
        pipeline = _make_pipeline()

        async def noop():
            pass

        task = pipeline._create_background_task(noop(), name="test-noop")
        assert task in pipeline._background_tasks

        await task
        # Give the done callback a chance to fire
        await asyncio.sleep(0)
        assert task not in pipeline._background_tasks

    @pytest.mark.asyncio
    async def test_task_discarded_after_completion(self):
        """Completed tasks must be removed from the set automatically."""
        pipeline = _make_pipeline()
        event = asyncio.Event()

        async def wait_for_event():
            await event.wait()

        task = pipeline._create_background_task(wait_for_event(), name="test-wait")
        assert len(pipeline._background_tasks) == 1

        event.set()
        await task
        await asyncio.sleep(0)
        assert len(pipeline._background_tasks) == 0

    @pytest.mark.asyncio
    async def test_task_exception_logged_not_raised(self):
        """Exceptions in background tasks must be logged, not propagated."""
        pipeline = _make_pipeline()

        async def fail():
            raise ValueError("test error")

        with patch("src.chat.pipeline.orchestrator.logger") as mock_logger:
            task = pipeline._create_background_task(fail(), name="test-fail")
            # Wait for the task to complete (it will fail internally)
            await asyncio.sleep(0.05)
            # The done callback should have logged the warning
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args
            assert "test-fail" in str(call_args)
            # Task should still be removed from the set
            assert task not in pipeline._background_tasks

    @pytest.mark.asyncio
    async def test_task_name_set(self):
        """Task should have the custom name for identification in logs."""
        pipeline = _make_pipeline()

        async def noop():
            pass

        task = pipeline._create_background_task(noop(), name="analytics-conv123")
        assert task.get_name() == "analytics-conv123"
        await task

    @pytest.mark.asyncio
    async def test_multiple_concurrent_tasks(self):
        """Multiple background tasks can run simultaneously."""
        pipeline = _make_pipeline()
        results = []

        async def append(val):
            results.append(val)

        t1 = pipeline._create_background_task(append(1), name="t1")
        t2 = pipeline._create_background_task(append(2), name="t2")
        t3 = pipeline._create_background_task(append(3), name="t3")
        assert len(pipeline._background_tasks) == 3

        await asyncio.gather(t1, t2, t3)
        await asyncio.sleep(0)
        assert sorted(results) == [1, 2, 3]
        assert len(pipeline._background_tasks) == 0


# ---------------------------------------------------------------------------
# _get_http_client lock tests
# ---------------------------------------------------------------------------

class TestGetHttpClientLock:
    """Verify HTTP client lazy init is race-condition-safe."""

    @pytest.mark.asyncio
    async def test_single_client_created(self):
        """Only one httpx.AsyncClient should be created even with concurrent calls."""
        pipeline = _make_pipeline()

        # Call _get_http_client multiple times concurrently
        clients = await asyncio.gather(
            pipeline._get_http_client(),
            pipeline._get_http_client(),
            pipeline._get_http_client(),
        )
        # All should return the same client instance
        assert clients[0] is clients[1]
        assert clients[1] is clients[2]
        assert clients[0] is not None

        # Clean up
        await pipeline.close()

    @pytest.mark.asyncio
    async def test_client_recreated_after_close(self):
        """If the client is closed, a new one should be created."""
        pipeline = _make_pipeline()

        client1 = await pipeline._get_http_client()
        await client1.aclose()

        client2 = await pipeline._get_http_client()
        assert client2 is not client1
        assert not client2.is_closed

        # Clean up
        await pipeline.close()

    @pytest.mark.asyncio
    async def test_lock_prevents_double_creation(self):
        """Under contention, the lock should prevent duplicate clients."""
        pipeline = _make_pipeline()
        creation_count = 0
        original_init = pipeline._http_client

        # Patch to track how many times a client is actually created
        import httpx

        original_async_client = httpx.AsyncClient

        def counting_client(**kwargs):
            nonlocal creation_count
            creation_count += 1
            return original_async_client(**kwargs)

        with patch("src.chat.pipeline.orchestrator.httpx.AsyncClient", side_effect=counting_client):
            clients = await asyncio.gather(
                pipeline._get_http_client(),
                pipeline._get_http_client(),
                pipeline._get_http_client(),
                pipeline._get_http_client(),
                pipeline._get_http_client(),
            )

        # Only 1 client should have been created
        assert creation_count == 1
        # All references should be the same
        assert all(c is clients[0] for c in clients)

        # Clean up
        await pipeline.close()


# ---------------------------------------------------------------------------
# Pipeline __init__ attribute tests
# ---------------------------------------------------------------------------

class TestPipelineInitAttributes:
    """Verify new safety attributes are initialized correctly."""

    def test_http_lock_initialized(self):
        """_http_lock must be an asyncio.Lock."""
        pipeline = _make_pipeline()
        assert isinstance(pipeline._http_lock, asyncio.Lock)

    def test_background_tasks_initialized_as_empty_set(self):
        """_background_tasks must start as an empty set."""
        pipeline = _make_pipeline()
        assert isinstance(pipeline._background_tasks, set)
        assert len(pipeline._background_tasks) == 0


# ---------------------------------------------------------------------------
# endpoints._background_tasks tests
# ---------------------------------------------------------------------------

class TestEndpointsBackgroundTasks:
    """Verify module-level _background_tasks in endpoints.py."""

    def test_module_level_set_exists(self):
        """endpoints._background_tasks must be a set."""
        from src.chat.endpoints import _background_tasks
        assert isinstance(_background_tasks, set)
