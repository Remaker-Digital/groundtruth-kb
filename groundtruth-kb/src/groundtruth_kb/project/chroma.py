"""Adopter-facing ChromaDB cache regeneration helpers."""

from __future__ import annotations

import gc
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb import db as _db_module
from groundtruth_kb.config import GTConfig
from groundtruth_kb.project.scaffold import _GT_KB_HOST_ROOT, _is_installed_wheel_context

CHROMA_DIRNAME = ".groundtruth-chroma"


@dataclass(frozen=True)
class ChromaRegenerationResult:
    """Result for rebuilding an adopter's disposable ChromaDB cache."""

    target: Path
    db_path: Path
    chroma_path: Path
    dry_run: bool
    status: str
    indexed: int = 0
    chunks: int = 0
    errors: tuple[str, ...] = ()
    removed_paths: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return {
            "target": str(self.target),
            "db_path": str(self.db_path),
            "chroma_path": str(self.chroma_path),
            "dry_run": self.dry_run,
            "status": self.status,
            "indexed": self.indexed,
            "chunks": self.chunks,
            "errors": list(self.errors),
            "removed_paths": list(self.removed_paths),
        }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_adopter_target(target: Path) -> Path:
    resolved = target.resolve()
    if not (resolved / "groundtruth.toml").is_file():
        raise ValueError(f"adopter target {resolved} does not contain groundtruth.toml")

    if _is_installed_wheel_context():
        if resolved.parent.name != "applications":
            raise ValueError(
                f"adopter target {resolved} must live directly under an applications/ directory; "
                "per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopter applications are placed at "
                "<gt-kb-root>/applications/<name>/."
            )
        return resolved

    expected_parent = (_GT_KB_HOST_ROOT / "applications").resolve()
    if resolved.parent != expected_parent:
        raise ValueError(
            f"adopter target {resolved} must live directly under {expected_parent}; "
            "per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopter applications are placed at "
            "<gt-kb-root>/applications/<name>/."
        )
    return resolved


def _removed_paths(chroma_path: Path) -> tuple[str, ...]:
    if not chroma_path.exists():
        return ()
    return tuple(sorted(str(path.relative_to(chroma_path)) for path in chroma_path.rglob("*") if path.is_file()))


def _close_chroma_client(db: Any) -> None:
    client = getattr(db, "_chroma_client", None)
    close = getattr(client, "close", None)
    if callable(close):
        close()
    if hasattr(db, "_chroma_client"):
        delattr(db, "_chroma_client")
    gc.collect()


def regenerate(target: Path, *, dry_run: bool = False) -> ChromaRegenerationResult:
    """Regenerate the disposable ChromaDB cache for a scaffolded adopter.

    SQLite ``groundtruth.db`` remains the source of truth. The adopter target
    must be a direct child of the GT-KB host ``applications`` directory in a
    source checkout, or a direct child of an ``applications`` directory when
    GT-KB is installed from a wheel.
    """
    target = _validate_adopter_target(target)
    config = GTConfig.load(target / "groundtruth.toml")
    db_path = config.db_path.resolve()
    chroma_path = (config.chroma_path or target / CHROMA_DIRNAME).resolve()

    if not _is_relative_to(db_path, target):
        raise ValueError(f"groundtruth.db path {db_path} is outside adopter target {target}")
    if not _is_relative_to(chroma_path, target):
        raise ValueError(f"ChromaDB path {chroma_path} is outside adopter target {target}")
    if not db_path.is_file() or db_path.stat().st_size == 0:
        raise ValueError(f"groundtruth.db is missing or empty at {db_path}")

    removed = _removed_paths(chroma_path)
    if dry_run:
        return ChromaRegenerationResult(
            target=target,
            db_path=db_path,
            chroma_path=chroma_path,
            dry_run=True,
            status="would-regenerate",
            removed_paths=removed,
        )

    if not _db_module.HAS_CHROMADB:
        return ChromaRegenerationResult(
            target=target,
            db_path=db_path,
            chroma_path=chroma_path,
            dry_run=False,
            status="skipped",
            errors=("ChromaDB not installed",),
            removed_paths=removed,
        )

    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    db = _db_module.KnowledgeDB(db_path=db_path, chroma_path=chroma_path)
    try:
        rebuild = db.rebuild_deliberation_index()
    finally:
        db.close()
        _close_chroma_client(db)

    errors = tuple(str(error) for error in rebuild.get("errors", []))
    return ChromaRegenerationResult(
        target=target,
        db_path=db_path,
        chroma_path=chroma_path,
        dry_run=False,
        status="error" if errors else "regenerated",
        indexed=int(rebuild.get("indexed", 0)),
        chunks=int(rebuild.get("chunks", 0)),
        errors=errors,
        removed_paths=removed,
    )
