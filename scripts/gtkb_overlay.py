#!/usr/bin/env python3
"""App-local session overlay baseline library (non-authoritative, copy-only).

This module is the Phase 6 first-slice implementation of GT-KB session overlays.
Overlays copy a fixed allowlist of already-generated dashboard/startup context
files into ``.groundtruth/session/overlays/<overlay_id>/files/`` alongside a
``manifest.json`` that explicitly marks the overlay and every entry
``authoritative: false``. Overlays are runtime context only: they must never
be consulted for canonical project state, promoted automatically, or trusted
when stale.

The library intentionally implements only:

- overlay id generation,
- manifest schema helpers,
- the allowlisted source inventory (four generated context files),
- a copy-only builder,
- stale-status evaluation against the live sources,
- manifest validation for the policy checker.

It does NOT implement promotion/apply, bridge-summary copies, deliberation
archive or MemBase copies, raw ``groundtruth.db``/``.groundtruth-chroma/``
copies, overlay-driven hook enforcement, control-plane refresh, or retention
cleanup. Those remain later slices per the Phase 6 plan.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OVERLAY_SCHEMA_VERSION = "1"
OVERLAY_ROOT_RELATIVE = Path(".groundtruth") / "session" / "overlays"
OVERLAY_CURRENT_POINTER_NAME = "current.json"
OVERLAY_MANIFEST_NAME = "manifest.json"
OVERLAY_FILES_DIRNAME = "files"
DEFAULT_OVERLAY_TTL = timedelta(hours=12)

# Fixed allowlist of generated app-local context artifacts. Every entry is
# an already-generated file whose canonical authority lives elsewhere (KB,
# MemBase, DA, source code). The overlay's copy is deliberately
# non-authoritative — kept here only so session startup can surface a
# stale-aware context view without re-reading large artifacts.
ALLOWLIST: tuple[tuple[str, str], ...] = (
    ("docs/gtkb-dashboard/dashboard-data.json", "dashboard-data.json"),
    ("docs/gtkb-dashboard/session-startup-report.md", "session-startup-report.md"),
    ("docs/gtkb-dashboard/session-wrapup-report.md", "session-wrapup-report.md"),
    ("memory/gtkb-dashboard-history.json", "gtkb-dashboard-history.json"),
)

# Denylist of content that must never be copied into an overlay even if a
# future caller accidentally passes it as a source. The allowlist check is
# the primary guard; this explicit denylist is defense in depth.
FORBIDDEN_NAME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(^|/)\.env(\..*)?$"),
    re.compile(r"(^|/)groundtruth\.db$"),
    re.compile(r"(^|/)\.groundtruth-chroma/"),
    re.compile(r"(^|/)bridge/"),
    re.compile(r"\.(py|ps1|sh|bat|cmd|exe|dll|so|dylib|vbs)$", re.IGNORECASE),
)

_OVERLAY_ID_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[a-z0-9][a-z0-9-]*[a-z0-9]$")


class OverlayPolicyError(RuntimeError):
    """Raised when an overlay manifest, entry, or layout violates policy."""


@dataclass(frozen=True)
class OverlayEntry:
    overlay_path: str
    source_kind: str
    source_uri: str
    source_hash: str
    authoritative: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "overlay_path": self.overlay_path,
            "source_kind": self.source_kind,
            "source_uri": self.source_uri,
            "source_hash": self.source_hash,
            "authoritative": self.authoritative,
        }


@dataclass(frozen=True)
class OverlayManifest:
    schema_version: str
    overlay_id: str
    authoritative: bool
    application_root: str
    subject: str
    role_slot: str
    harness_id: str
    created_at: str
    expires_at: str
    entries: tuple[OverlayEntry, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "overlay_id": self.overlay_id,
            "authoritative": self.authoritative,
            "application_root": self.application_root,
            "subject": self.subject,
            "role_slot": self.role_slot,
            "harness_id": self.harness_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class OverlayStalenessEntry:
    overlay_path: str
    source_uri: str
    recorded_hash: str
    current_hash: str | None
    stale: bool
    reason: str


@dataclass(frozen=True)
class OverlayStalenessReport:
    overlay_id: str
    overlay_dir: str
    authoritative: bool
    expired: bool
    entries_stale: int
    entries_total: int
    is_stale: bool
    entries: tuple[OverlayStalenessEntry, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overlay_id": self.overlay_id,
            "overlay_dir": self.overlay_dir,
            "authoritative": self.authoritative,
            "expired": self.expired,
            "entries_stale": self.entries_stale,
            "entries_total": self.entries_total,
            "is_stale": self.is_stale,
            "entries": [entry.__dict__ for entry in self.entries],
            "notes": list(self.notes),
        }


def overlay_root(project_root: Path = PROJECT_ROOT) -> Path:
    """Return the runtime overlay root for a given application root."""
    return project_root / OVERLAY_ROOT_RELATIVE


def generate_overlay_id(
    *,
    subject: str,
    harness_id: str,
    role_slot: str,
    now: datetime | None = None,
) -> str:
    """Return a deterministic ``<timestamp>-<slug>`` overlay id.

    The slug is derived from subject/harness/role so two overlays produced at
    the same second under different roles do not collide.
    """

    ts = (now or datetime.now(UTC)).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    slug_source = f"{subject}-{harness_id}-{role_slot}".strip("-")
    slug = re.sub(r"[^a-z0-9-]+", "-", slug_source.lower()).strip("-") or "overlay"
    return f"{ts}-{slug}"


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _assert_not_forbidden(source_uri: str) -> None:
    for pattern in FORBIDDEN_NAME_PATTERNS:
        if pattern.search(source_uri):
            raise OverlayPolicyError(
                f"refusing to copy forbidden source into overlay: {source_uri}"
            )


def _validate_allowlist_source(source_uri: str) -> str:
    normalized = source_uri.replace("\\", "/").lstrip("./")
    for allowed_uri, overlay_path in ALLOWLIST:
        if normalized == allowed_uri:
            _assert_not_forbidden(normalized)
            return overlay_path
    raise OverlayPolicyError(
        f"source not in overlay allowlist: {source_uri!r}; allowed={[uri for uri, _ in ALLOWLIST]}"
    )


def _resolve_inside_root(project_root: Path, source_uri: str) -> Path:
    candidate = (project_root / source_uri).resolve()
    root_resolved = project_root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise OverlayPolicyError(
            f"source path {source_uri!r} resolves outside application root {root_resolved}"
        ) from exc
    return candidate


def build_overlay(
    *,
    project_root: Path = PROJECT_ROOT,
    subject: str = "application",
    role_slot: str = "prime-builder",
    harness_id: str = "unknown-harness",
    now: datetime | None = None,
    ttl: timedelta = DEFAULT_OVERLAY_TTL,
    sources: tuple[tuple[str, str], ...] | None = None,
    overlay_root_path: Path | None = None,
    update_current_pointer: bool = True,
) -> OverlayManifest:
    """Build a non-authoritative overlay by copying allowlisted sources.

    Missing sources are silently skipped (no entry written) — they cannot be
    promoted to authoritative, and their absence is surfaced by the staleness
    report at startup. Every copy is hashed and recorded as
    ``authoritative: false``.
    """

    resolved_root = project_root.resolve()
    now = now or datetime.now(UTC)
    target_root = (overlay_root_path or overlay_root(resolved_root)).resolve()
    overlay_id = generate_overlay_id(subject=subject, harness_id=harness_id, role_slot=role_slot, now=now)
    overlay_dir = target_root / overlay_id
    files_dir = overlay_dir / OVERLAY_FILES_DIRNAME
    files_dir.mkdir(parents=True, exist_ok=True)

    allowlist = sources or ALLOWLIST
    entries: list[OverlayEntry] = []
    for source_uri, overlay_basename in allowlist:
        expected_overlay_path = _validate_allowlist_source(source_uri)
        # belt-and-braces: the allowlist binds source -> overlay name; the
        # caller does not get to rename.
        if expected_overlay_path != overlay_basename:
            raise OverlayPolicyError(
                f"allowlist entry mismatch: {source_uri} -> {overlay_basename!r}"
            )
        source_path = _resolve_inside_root(resolved_root, source_uri)
        if not source_path.is_file():
            # Skip missing sources; staleness evaluation will flag them.
            continue
        destination = files_dir / overlay_basename
        shutil.copy2(source_path, destination)
        entries.append(
            OverlayEntry(
                overlay_path=f"{OVERLAY_FILES_DIRNAME}/{overlay_basename}",
                source_kind="file",
                source_uri=source_uri,
                source_hash=_sha256(destination),
                authoritative=False,
            )
        )

    manifest = OverlayManifest(
        schema_version=OVERLAY_SCHEMA_VERSION,
        overlay_id=overlay_id,
        authoritative=False,
        application_root=str(resolved_root),
        subject=subject,
        role_slot=role_slot,
        harness_id=harness_id,
        created_at=now.astimezone(UTC).isoformat().replace("+00:00", "Z"),
        expires_at=(now + ttl).astimezone(UTC).isoformat().replace("+00:00", "Z"),
        entries=tuple(entries),
    )
    manifest_path = overlay_dir / OVERLAY_MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if update_current_pointer:
        pointer_path = target_root / OVERLAY_CURRENT_POINTER_NAME
        pointer_path.write_text(
            json.dumps(
                {
                    "authoritative": False,
                    "overlay_id": overlay_id,
                    "overlay_dir": str(overlay_dir.relative_to(resolved_root).as_posix()),
                    "manifest_path": str(manifest_path.relative_to(resolved_root).as_posix()),
                    "updated_at": manifest.created_at,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    return manifest


def load_manifest(overlay_dir: Path) -> OverlayManifest:
    manifest_path = overlay_dir / OVERLAY_MANIFEST_NAME
    if not manifest_path.is_file():
        raise OverlayPolicyError(f"overlay manifest missing: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OverlayPolicyError(f"overlay manifest is not valid JSON: {manifest_path}: {exc}") from exc
    return _manifest_from_dict(payload)


def _manifest_from_dict(payload: dict[str, Any]) -> OverlayManifest:
    required = {
        "schema_version",
        "overlay_id",
        "authoritative",
        "application_root",
        "subject",
        "role_slot",
        "harness_id",
        "created_at",
        "expires_at",
        "entries",
    }
    missing = required - payload.keys()
    if missing:
        raise OverlayPolicyError(f"overlay manifest missing required fields: {sorted(missing)}")
    if payload["schema_version"] != OVERLAY_SCHEMA_VERSION:
        raise OverlayPolicyError(
            f"overlay manifest schema_version must be {OVERLAY_SCHEMA_VERSION!r}; got {payload['schema_version']!r}"
        )
    entries_payload = payload["entries"]
    if not isinstance(entries_payload, list):
        raise OverlayPolicyError("overlay manifest entries must be a list")
    entries: list[OverlayEntry] = []
    for raw in entries_payload:
        if not isinstance(raw, dict):
            raise OverlayPolicyError("overlay manifest entry must be an object")
        entries.append(
            OverlayEntry(
                overlay_path=str(raw.get("overlay_path", "")),
                source_kind=str(raw.get("source_kind", "")),
                source_uri=str(raw.get("source_uri", "")),
                source_hash=str(raw.get("source_hash", "")),
                authoritative=bool(raw.get("authoritative", False)),
            )
        )
    return OverlayManifest(
        schema_version=str(payload["schema_version"]),
        overlay_id=str(payload["overlay_id"]),
        authoritative=bool(payload["authoritative"]),
        application_root=str(payload["application_root"]),
        subject=str(payload["subject"]),
        role_slot=str(payload["role_slot"]),
        harness_id=str(payload["harness_id"]),
        created_at=str(payload["created_at"]),
        expires_at=str(payload["expires_at"]),
        entries=tuple(entries),
    )


def load_current_pointer(project_root: Path = PROJECT_ROOT) -> dict[str, Any] | None:
    pointer = overlay_root(project_root) / OVERLAY_CURRENT_POINTER_NAME
    if not pointer.is_file():
        return None
    try:
        payload = json.loads(pointer.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def validate_manifest(manifest: OverlayManifest, *, project_root: Path) -> None:
    """Raise OverlayPolicyError if the manifest violates first-slice policy."""

    if manifest.authoritative:
        raise OverlayPolicyError(
            f"overlay {manifest.overlay_id} marks itself authoritative; first-slice policy forbids this"
        )
    if not _OVERLAY_ID_PATTERN.match(manifest.overlay_id):
        raise OverlayPolicyError(
            f"overlay_id {manifest.overlay_id!r} does not match required <timestampZ>-<slug> shape"
        )

    root_resolved = project_root.resolve()
    try:
        application_root = Path(manifest.application_root).resolve()
    except OSError as exc:
        raise OverlayPolicyError(
            f"overlay {manifest.overlay_id} has an unresolvable application_root: {manifest.application_root!r}"
        ) from exc
    if application_root != root_resolved:
        raise OverlayPolicyError(
            f"overlay {manifest.overlay_id} application_root {application_root} does not match current root {root_resolved}"
        )

    allowed_source_uris = {uri for uri, _ in ALLOWLIST}
    allowed_overlay_paths = {f"{OVERLAY_FILES_DIRNAME}/{name}" for _, name in ALLOWLIST}

    seen_sources: set[str] = set()
    for entry in manifest.entries:
        if entry.authoritative:
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} entry {entry.overlay_path!r} is authoritative; forbidden"
            )
        if entry.source_kind != "file":
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} entry {entry.overlay_path!r} has unsupported source_kind {entry.source_kind!r}"
            )
        if entry.source_uri not in allowed_source_uris:
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} entry source_uri {entry.source_uri!r} not in allowlist"
            )
        if entry.overlay_path not in allowed_overlay_paths:
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} entry overlay_path {entry.overlay_path!r} not in allowlist"
            )
        _assert_not_forbidden(entry.source_uri)
        if not re.fullmatch(r"[0-9a-f]{64}", entry.source_hash):
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} entry {entry.overlay_path!r} source_hash is not a sha256 hex digest"
            )
        if entry.source_uri in seen_sources:
            raise OverlayPolicyError(
                f"overlay {manifest.overlay_id} has duplicate source_uri {entry.source_uri!r}"
            )
        seen_sources.add(entry.source_uri)


def evaluate_staleness(
    overlay_dir: Path,
    *,
    project_root: Path = PROJECT_ROOT,
    now: datetime | None = None,
) -> OverlayStalenessReport:
    """Return a staleness report for the overlay rooted at ``overlay_dir``."""

    manifest = load_manifest(overlay_dir)
    now = now or datetime.now(UTC)
    try:
        expires_at = datetime.fromisoformat(manifest.expires_at.replace("Z", "+00:00"))
    except ValueError:
        expires_at = now  # treat unparseable expiry as expired
    expired = now >= expires_at

    entry_reports: list[OverlayStalenessEntry] = []
    stale_count = 0
    root_resolved = project_root.resolve()
    for entry in manifest.entries:
        source_path = root_resolved / entry.source_uri
        if not source_path.is_file():
            entry_reports.append(
                OverlayStalenessEntry(
                    overlay_path=entry.overlay_path,
                    source_uri=entry.source_uri,
                    recorded_hash=entry.source_hash,
                    current_hash=None,
                    stale=True,
                    reason="source_missing",
                )
            )
            stale_count += 1
            continue
        current_hash = _sha256(source_path)
        stale = current_hash != entry.source_hash
        if stale:
            stale_count += 1
        entry_reports.append(
            OverlayStalenessEntry(
                overlay_path=entry.overlay_path,
                source_uri=entry.source_uri,
                recorded_hash=entry.source_hash,
                current_hash=current_hash,
                stale=stale,
                reason="hash_changed" if stale else "fresh",
            )
        )

    notes: list[str] = ["overlay is non-authoritative; do not use as canonical state"]
    if expired:
        notes.append("overlay has passed its declared expiry")
    if stale_count:
        notes.append(f"{stale_count}/{len(manifest.entries)} entries diverge from current sources")

    return OverlayStalenessReport(
        overlay_id=manifest.overlay_id,
        overlay_dir=str(overlay_dir),
        authoritative=manifest.authoritative,
        expired=expired,
        entries_stale=stale_count,
        entries_total=len(manifest.entries),
        is_stale=expired or stale_count > 0,
        entries=tuple(entry_reports),
        notes=tuple(notes),
    )


def iter_overlay_dirs(project_root: Path = PROJECT_ROOT) -> list[Path]:
    root = overlay_root(project_root)
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and (path / OVERLAY_MANIFEST_NAME).is_file()
    )


def current_overlay_status(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Return a startup-facing snapshot of overlay state (non-authoritative)."""

    pointer = load_current_pointer(project_root)
    root = overlay_root(project_root)
    base: dict[str, Any] = {
        "authoritative": False,
        "overlay_root": str(root.relative_to(project_root.resolve()).as_posix())
        if root.is_dir()
        else OVERLAY_ROOT_RELATIVE.as_posix(),
        "overlay_present": False,
        "overlay_id": None,
        "expired": False,
        "entries_stale": 0,
        "entries_total": 0,
        "is_stale": False,
        "notes": ["no current session overlay; startup context is sourced from live files"],
    }

    if pointer is None:
        return base

    overlay_dir_rel = pointer.get("overlay_dir")
    if not isinstance(overlay_dir_rel, str):
        base["notes"] = ["current overlay pointer is malformed; treating as absent"]
        return base

    overlay_dir = (project_root / overlay_dir_rel).resolve()
    if not overlay_dir.is_dir():
        base["notes"] = [f"current overlay pointer references missing directory {overlay_dir_rel!r}"]
        return base

    try:
        report = evaluate_staleness(overlay_dir, project_root=project_root)
    except OverlayPolicyError as exc:
        base["notes"] = [f"current overlay failed validation and must not be trusted: {exc}"]
        return base

    return {
        "authoritative": False,
        "overlay_root": str(root.relative_to(project_root.resolve()).as_posix()),
        "overlay_present": True,
        "overlay_id": report.overlay_id,
        "expired": report.expired,
        "entries_stale": report.entries_stale,
        "entries_total": report.entries_total,
        "is_stale": report.is_stale,
        "notes": list(report.notes),
    }


__all__ = [
    "ALLOWLIST",
    "DEFAULT_OVERLAY_TTL",
    "FORBIDDEN_NAME_PATTERNS",
    "OVERLAY_CURRENT_POINTER_NAME",
    "OVERLAY_FILES_DIRNAME",
    "OVERLAY_MANIFEST_NAME",
    "OVERLAY_ROOT_RELATIVE",
    "OVERLAY_SCHEMA_VERSION",
    "OverlayEntry",
    "OverlayManifest",
    "OverlayPolicyError",
    "OverlayStalenessEntry",
    "OverlayStalenessReport",
    "build_overlay",
    "current_overlay_status",
    "evaluate_staleness",
    "generate_overlay_id",
    "iter_overlay_dirs",
    "load_current_pointer",
    "load_manifest",
    "overlay_root",
    "validate_manifest",
]
