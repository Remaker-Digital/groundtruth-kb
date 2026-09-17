"""Shared fixtures for the native application (adopter) test suite.

Each fixture initializes an explicitly registered application through the
native scaffold against real native HTTP on the disposable database. The
retired SQLite-era sandbox under the checkout's own ``applications/`` directory,
its literal host-root binding and its local ``groundtruth.db`` are gone: the
disposable host is the fixture's own Git repository with registered slots.
"""

from __future__ import annotations

import types
from collections.abc import Iterator
from pathlib import Path

import pytest

from groundtruth_kb.project import chroma as chroma_module


class FakeChromaCollection:
    def __init__(self) -> None:
        self.rows: dict[str, dict] = {}

    def upsert(self, *, ids, documents, metadatas):
        for ident, document, metadata in zip(ids, documents, metadatas, strict=True):
            self.rows[ident] = {"document": document, "metadata": metadata}


class FakeChromaClient:
    """Persistent-client stand-in: records what a rebuild would store, without the dependency."""

    instances: list[FakeChromaClient] = []

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.collection = FakeChromaCollection()
        self.closed = False
        FakeChromaClient.instances.append(self)
        (self.path / "chroma.sqlite3").write_bytes(b"fake persistent store")

    def get_or_create_collection(self, name, metadata=None):
        assert name == chroma_module.COLLECTION_NAME
        return self.collection

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def fake_chromadb(monkeypatch):
    """Exercise the rebuild path without the optional dependency installed."""
    module = types.SimpleNamespace(PersistentClient=FakeChromaClient, instances=FakeChromaClient.instances)
    monkeypatch.setattr(chroma_module._db_module, "HAS_CHROMADB", True)
    monkeypatch.setattr(chroma_module._db_module, "_load_chromadb", lambda: module)
    FakeChromaClient.instances.clear()
    return module


@pytest.fixture
def clean_adopter(native_application) -> Iterator[tuple[Path, Path]]:
    """Yield ``(application_root, host_root)`` for a freshly initialized dual-agent application."""
    target = native_application.scaffold("Alpha", profile="dual-agent")
    yield target, native_application.host


@pytest.fixture
def clean_adopter_local_only(native_application) -> Iterator[tuple[Path, Path]]:
    """Local-only profile variant for tests that do not need bridge-tier CI."""
    target = native_application.scaffold("Alpha", profile="local-only")
    yield target, native_application.host
