"""Optional derived search cache for one application, rebuilt from current canonical records.

The cache is a disposable derivation of the native authority's current records for
the selected application scope. It grants nothing, is never read as authority, and
its absence never blocks application work. Regeneration derives from the
configured authority only; no local database is opened or created.

The only directory regeneration may delete is the cache the application declares
in its artifact registry (``.gtkb-app-isolation.json``): the top-level
``.groundtruth-chroma`` entry classified ``generated_output``, or a path inside
it. Every other target is refused before any record is read or any byte removed.
"""

from __future__ import annotations

import gc
import shutil
import tomllib
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb import db as _db_module
from groundtruth_kb.authority_client import AuthorityClient
from groundtruth_kb.config import GTConfig
from groundtruth_kb.isolation.app_root_minimization import (
    REGISTRY_FILENAME,
    AppRootFinding,
    _load_registry,
    _normalize_registry_entries,
)

CHROMA_DIRNAME = ".groundtruth-chroma"
CHROMA_CLASSIFICATION = "generated_output"
COLLECTION_NAME = "gtkb_canonical_records"


class CacheTargetError(ValueError):
    """The configured cache path is not the application's declared disposable cache; nothing was read or removed."""

    code = "cache_target_refused"


@dataclass(frozen=True)
class ChromaRegenerationResult:
    """Result for previewing or rebuilding an application's disposable search cache."""

    target: Path
    authority_url: str
    application_scope: str
    chroma_path: Path
    dry_run: bool
    status: str
    indexed: int = 0
    chunks: int = 0
    errors: tuple[str, ...] = ()
    removed_paths: tuple[str, ...] = ()
    record_counts: dict[str, int] | None = None

    def to_json_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return {
            "target": str(self.target),
            "authority_url": self.authority_url,
            "application_scope": self.application_scope,
            "chroma_path": str(self.chroma_path),
            "dry_run": self.dry_run,
            "status": self.status,
            "indexed": self.indexed,
            "chunks": self.chunks,
            "errors": list(self.errors),
            "removed_paths": list(self.removed_paths),
            "record_counts": dict(self.record_counts or {}),
            "canonical_writes": 0,
        }


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _confine_cache_target(target: Path, chroma_path: Path) -> None:
    """Refuse every cache target other than the application's declared disposable cache.

    ``target`` and ``chroma_path`` are resolved. The accepted target is the top-level
    ``.groundtruth-chroma`` entry the registry declares as a ``generated_output`` DIR, or a
    path inside it. The application root, its Git metadata, authoritative inputs, runtime
    data, undeclared entries and every other generated output (hooks, harness projections)
    are never cache targets. Without a registry only the default child is accepted. A
    registry that is present but invalid cannot classify anything and refuses. Runs before
    any record is read and before any byte is removed.
    """
    if chroma_path == target:
        raise CacheTargetError(
            f"ChromaDB path {chroma_path} is the application root itself; the cache target must be the declared "
            f"disposable cache directory {CHROMA_DIRNAME}"
        )
    if not _is_relative_to(chroma_path, target):
        raise CacheTargetError(f"ChromaDB path {chroma_path} is outside application target {target}")
    top = chroma_path.relative_to(target).parts[0]
    if top.casefold() == ".git":
        raise CacheTargetError(
            f"ChromaDB path {chroma_path} is inside the application's Git metadata {target / top}; "
            "Git metadata is never a cache target"
        )
    registry_path = target / REGISTRY_FILENAME
    findings: list[AppRootFinding] = []
    payload = _load_registry(registry_path, target, findings)
    if payload is None and any(finding.code == "registry_missing" for finding in findings):
        if top != CHROMA_DIRNAME:
            raise CacheTargetError(
                f"ChromaDB path {chroma_path} is not the default cache {target / CHROMA_DIRNAME} and {target} has "
                f"no {REGISTRY_FILENAME} declaring a disposable cache; only the default cache is accepted without "
                "a registry"
            )
        return
    entries = _normalize_registry_entries(payload, target, registry_path, findings)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        head = "; ".join(f"{finding.code}: {finding.message}" for finding in errors[:3])
        raise CacheTargetError(
            f"ChromaDB path {chroma_path} cannot be classified: {REGISTRY_FILENAME} in {target} is invalid ({head})"
        )
    declared = next((entry for entry in entries if entry["name"] == top), None)
    if declared is None:
        raise CacheTargetError(
            f"ChromaDB path {chroma_path}: top-level entry {top!r} is not declared in {REGISTRY_FILENAME}; only the "
            f"declared disposable cache {CHROMA_DIRNAME} ({CHROMA_CLASSIFICATION} DIR) is a cache target"
        )
    classification = declared.get("classification")
    if top != CHROMA_DIRNAME:
        if classification == CHROMA_CLASSIFICATION:
            raise CacheTargetError(
                f"ChromaDB path {chroma_path}: top-level entry {top!r} is declared {classification} but is not "
                f"the declared search cache {CHROMA_DIRNAME}; other generated outputs are not disposable by "
                "cache regeneration"
            )
        raise CacheTargetError(
            f"ChromaDB path {chroma_path}: top-level entry {top!r} is declared {classification} in "
            f"{REGISTRY_FILENAME}, not the disposable search cache"
        )
    if declared.get("type") != "DIR" or classification != CHROMA_CLASSIFICATION:
        raise CacheTargetError(
            f"ChromaDB path {chroma_path}: {CHROMA_DIRNAME} is declared {declared.get('type')} {classification} in "
            f"{REGISTRY_FILENAME}, not a {CHROMA_CLASSIFICATION} DIR; the cache is not disposable as declared"
        )


def _application_scope(target: Path, explicit: str | None) -> str:
    if explicit is not None:
        if explicit != "gtkb_platform" and not explicit.startswith("application:"):
            raise ValueError("application_scope must be gtkb_platform or application:<catalog name>")
        return explicit
    marker = target / "application.toml"
    if not marker.is_file():
        raise ValueError(f"{target} has no application.toml marker; select the application scope explicitly")
    payload = tomllib.loads(marker.read_text(encoding="utf-8"))
    nested = payload.get("application", {})
    name = nested.get("name") if isinstance(nested, dict) else None
    if not isinstance(name, str) or not name:
        raise ValueError("application.toml must name the registered application")
    return "application:" + name


def _validate_target(target: Path) -> tuple[Path, GTConfig]:
    resolved = target.resolve()
    config_path = resolved / "groundtruth.toml"
    if not config_path.is_file():
        raise ValueError(f"application target {resolved} does not contain groundtruth.toml")
    config = GTConfig.load(config_path=config_path, discover=False)
    if not config.authority_url:
        raise ValueError(
            "The search cache derives from the configured native authority; set authority_url in groundtruth.toml. "
            "No local database is read or created."
        )
    return resolved, config


def _pages(client: AuthorityClient, domain: str, **filters: Any) -> Iterator[dict[str, Any]]:
    after = None
    while True:
        page = client.request("GET", f"/v1/{domain}", query={**filters, "limit": 1000, "after": after})
        yield from page["records"]
        following = page["next_after"]
        if following is None:
            return
        if following == after:
            raise ValueError(f"The {domain} cursor did not advance")
        after = following


def canonical_documents(client: AuthorityClient, scope: str) -> list[dict[str, Any]]:
    """Read the application's current records; each becomes one indexed document."""
    documents: list[dict[str, Any]] = []
    for record in _pages(client, "specifications", application_scope=scope):
        if record.get("status") != "active":
            continue
        documents.append(
            {
                "id": "specifications/" + str(record["id"]),
                "domain": "specifications",
                "record_id": str(record["id"]),
                "version": int(record["version"]),
                "text": "\n".join(part for part in (record.get("title"), record.get("description")) if part),
            }
        )
    for record in _pages(client, "tests", application_scope=scope):
        documents.append(
            {
                "id": "tests/" + str(record["id"]),
                "domain": "tests",
                "record_id": str(record["id"]),
                "version": int(record["version"]),
                "text": "\n".join(
                    str(part)
                    for part in (record.get("title"), record.get("description"), record.get("expected_outcome"))
                    if part
                ),
            }
        )
    if scope.startswith("application:"):
        for project in _pages(client, "projects", repository_ref=scope):
            shown = client.request("GET", "/v1/projects/" + quote(str(project["id"]), safe=""))
            for membership in shown.get("memberships", []):
                work_id = str(membership["work_item_id"])
                work = client.request("GET", "/v1/work-items/" + quote(work_id, safe=""))
                row = work.get("work_item", work)
                documents.append(
                    {
                        "id": "work-items/" + work_id,
                        "domain": "work-items",
                        "record_id": work_id,
                        "version": int(row["version"]),
                        "text": "\n".join(str(part) for part in (row.get("title"), row.get("description")) if part),
                    }
                )
    return documents


def _removed_paths(chroma_path: Path) -> tuple[str, ...]:
    if not chroma_path.exists():
        return ()
    return tuple(sorted(str(path.relative_to(chroma_path)) for path in chroma_path.rglob("*") if path.is_file()))


def _counts(documents: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        counts[document["domain"]] = counts.get(document["domain"], 0) + 1
    return counts


def _close(client: Any) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        close()
    gc.collect()


def regenerate(
    target: Path,
    *,
    dry_run: bool = False,
    application_scope: str | None = None,
    client: AuthorityClient | None = None,
) -> ChromaRegenerationResult:
    """Preview or rebuild the disposable cache from the authority's current records.

    A preview reads canonical records and reports what would be replaced without
    writing. Without the optional ChromaDB dependency the result is an explicit
    ``skipped`` outcome and existing cache bytes are preserved. A rebuild replaces
    the cache directory only after the current records were read completely, and
    only when that directory is the application's declared disposable cache
    (``_confine_cache_target``); any other target raises ``CacheTargetError``
    before a record is read.
    """
    target, config = _validate_target(target)
    scope = _application_scope(target, application_scope)
    chroma_path = (config.chroma_path or target / CHROMA_DIRNAME).resolve()
    _confine_cache_target(target, chroma_path)
    reader = client or AuthorityClient(str(config.authority_url))
    documents = canonical_documents(reader, scope)
    removed = _removed_paths(chroma_path)

    def outcome(
        status: str, *, dry_run: bool, indexed: int = 0, errors: tuple[str, ...] = ()
    ) -> ChromaRegenerationResult:
        return ChromaRegenerationResult(
            target=target,
            authority_url=str(config.authority_url),
            application_scope=scope,
            chroma_path=chroma_path,
            dry_run=dry_run,
            status=status,
            indexed=indexed,
            chunks=indexed,
            errors=errors,
            removed_paths=removed,
            record_counts=_counts(documents),
        )

    if dry_run:
        return outcome("would-regenerate", dry_run=True)
    if not _db_module.HAS_CHROMADB:
        return outcome("skipped", dry_run=False, errors=("ChromaDB not installed",))
    chromadb = _db_module._load_chromadb()
    if chromadb is None:
        return outcome("skipped", dry_run=False, errors=("ChromaDB import failed",))
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
    chroma_path.mkdir(parents=True)
    store = chromadb.PersistentClient(path=str(chroma_path))
    errors: list[str] = []
    indexed = 0
    try:
        collection = store.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "l2"})
        for document in documents:
            try:
                collection.upsert(
                    ids=[document["id"]],
                    documents=[document["text"] or document["record_id"]],
                    metadatas=[
                        {
                            "domain": document["domain"],
                            "record_id": document["record_id"],
                            "version": document["version"],
                            "application_scope": scope,
                        }
                    ],
                )
                indexed += 1
            except Exception as error:  # intentional-catch: per-record error tracking, rebuild continues
                errors.append(f"{document['id']}: {error}")
    finally:
        _close(store)
    return outcome("error" if errors else "regenerated", dry_run=False, indexed=indexed, errors=tuple(errors))
