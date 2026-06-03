"""``gt bridge revise`` — deterministic REVISED-filing CLI logic (WI-3429, Slice 1).

Replaces per-cycle AI-authored REVISED bridge filings with a deterministic
transform. Given a thread slug, a reason, and a mechanical fix-class, this
module:

1. Resolves the latest Prime-authored ``NEW``/``REVISED`` file for the thread
   (the carry-forward source — NOT a top-of-stack verdict).
2. Carries that content forward byte-identically.
3. Applies the named fix-class transform (a pure ``str -> str``).
4. Bumps the version to ``max(on-disk, INDEX) + 1``.
5. Updates the ``Version:`` / ``Responds to:`` provenance lines.
6. Writes the new bridge file through the scanner-safe credential path.
7. Updates ``bridge/INDEX.md`` atomically with a ``REVISED`` status line, via
   the serialized INDEX writer (``bridge_index_writer.atomic_index_update``).
8. Re-runs both bridge preflights and surfaces their results.

Slice 1 implements the three *mechanical* fix-classes
(``content_carryforward_only``, ``citation_add``, ``target_paths_add``). The
structural fix-classes (``target_paths_glob_widen``, ``partition_update``,
``pauth_swap``) are deferred to Slice 2 and fail closed.

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` and WI-3429. The INDEX-write
serialization satisfies ``GOV-FILE-BRIDGE-AUTHORITY-001``; byte-identical
carry-forward satisfies ``GOV-08``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

# --- Fix-class taxonomy -----------------------------------------------------

SLICE_1_FIX_CLASSES: tuple[str, ...] = (
    "content_carryforward_only",
    "citation_add",
    "target_paths_add",
)
SLICE_2_FIX_CLASSES: tuple[str, ...] = (
    "target_paths_glob_widen",
    "partition_update",
    "pauth_swap",
)
ALL_FIX_CLASSES: tuple[str, ...] = SLICE_1_FIX_CLASSES + SLICE_2_FIX_CLASSES

# Status tokens that mark a Prime-authored proposal version (a valid
# carry-forward source). Verdict tokens (GO/NO-GO/VERIFIED/ADVISORY/DEFERRED)
# are LO/owner-authored and never carried forward by a revise.
_PRIME_STATUS_TOKENS = ("NEW", "REVISED")
_VERSIONED_LINE_RE = re.compile(r"^(?P<status>[A-Z\-]+):\s*(?P<path>bridge/.+?-(?P<ver>\d{3})\.md)\s*$")
_VERSION_HEADER_RE = re.compile(r"^(?P<prefix>Version:\s*)(?P<ver>\d+)\s*$", re.MULTILINE)


class BridgeReviseError(RuntimeError):
    """Raised for any deterministic-revise precondition or transform failure."""


@dataclass
class ReviseResult:
    """Outcome of a revise (or dry-run preview)."""

    slug: str
    fix_class: str
    reason: str
    source_path: Path
    new_version: int
    new_path: Path
    new_content: str
    index_status_line: str
    dry_run: bool
    written: bool = False
    preflight_summaries: dict[str, str] = field(default_factory=dict)


# --- Helper-module loading (reuse-first; mirrors write_bridge's own pattern) -


def _discover_project_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / "scripts" / "bridge_index_writer.py").is_file():
            return parent
    # Package layout fallback: groundtruth-kb/src/groundtruth_kb/<this>
    return here.parents[3]


def _load_helpers(project_root: Path):
    """Import the reused write/index helpers via guarded sys.path.

    Returns a tuple ``(write_bridge_module, atomic_index_update)``. The same
    sys.path technique ``write_bridge`` uses internally; keeps a single
    canonical ``compose_index_update`` / credential-scan implementation rather
    than re-deriving them (avoids drift).
    """
    scripts_dir = project_root / "scripts"
    helper_dir = project_root / ".claude" / "skills" / "bridge-propose" / "helpers"
    for path in (str(project_root), str(scripts_dir), str(helper_dir)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        write_bridge = importlib.import_module("write_bridge")
    except Exception as exc:  # noqa: BLE001 - surface a clear precondition error
        raise BridgeReviseError(
            "write_bridge helper unavailable; expected "
            ".claude/skills/bridge-propose/helpers/write_bridge.py importable."
        ) from exc
    try:
        index_writer = importlib.import_module("bridge_index_writer")
    except Exception as exc:  # noqa: BLE001
        raise BridgeReviseError(
            "bridge_index_writer unavailable; expected scripts/bridge_index_writer.py importable."
        ) from exc
    return write_bridge, index_writer.atomic_index_update


# --- Thread / version resolution --------------------------------------------


def _index_block_lines(index_text: str, slug: str) -> list[str]:
    """Return the status lines of the ``Document: <slug>`` block in INDEX text."""
    lines = index_text.splitlines()
    block: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Document:"):
            in_block = stripped[len("Document:") :].strip() == slug
            continue
        if in_block:
            if not stripped:
                break
            block.append(stripped)
    return block


def find_carryforward_source(slug: str, index_text: str, bridge_dir: Path) -> Path:
    """Resolve the latest Prime-authored NEW/REVISED file to carry forward.

    Prefers the INDEX block (authoritative ordering, newest-first). Falls back
    to the highest-versioned on-disk file whose first non-blank line is a
    NEW/REVISED status token. Raises if no Prime-authored version exists.
    """
    for stripped in _index_block_lines(index_text, slug):
        m = _VERSIONED_LINE_RE.match(stripped)
        if m and m.group("status") in _PRIME_STATUS_TOKENS:
            candidate = bridge_dir.parent / m.group("path")
            if candidate.is_file():
                return candidate
    # Fallback: scan on-disk files newest-first.
    on_disk = sorted(
        bridge_dir.glob(f"{slug}-[0-9][0-9][0-9].md"),
        key=lambda p: p.name,
        reverse=True,
    )
    for path in on_disk:
        first = _first_status_token(path)
        if first in _PRIME_STATUS_TOKENS:
            return path
    raise BridgeReviseError(f"No Prime-authored NEW/REVISED version found for thread {slug!r}; cannot revise.")


def _first_status_token(path: Path) -> str | None:
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                return raw.strip().split()[0] if raw.strip() else None
    except OSError:
        return None
    return None


def _all_thread_versions(slug: str, index_text: str, bridge_dir: Path) -> set[int]:
    """Union of version numbers seen in the INDEX block and on disk."""
    versions: set[int] = set()
    for stripped in _index_block_lines(index_text, slug):
        m = _VERSIONED_LINE_RE.match(stripped)
        if m:
            versions.add(int(m.group("ver")))
    for path in bridge_dir.glob(f"{slug}-[0-9][0-9][0-9].md"):
        mm = re.search(r"-(\d{3})\.md$", path.name)
        if mm:
            versions.add(int(mm.group(1)))
    return versions


def next_version(slug: str, index_text: str, bridge_dir: Path) -> int:
    versions = _all_thread_versions(slug, index_text, bridge_dir)
    return (max(versions) + 1) if versions else 1


# --- Fix-class transforms (pure str -> str) ---------------------------------


def _apply_content_carryforward_only(body: str, **_: object) -> str:
    """No content change — pure carry-forward (version/provenance bumped later)."""
    return body


def _ensure_section(body: str, heading: str) -> str:
    """Append an empty ``## heading`` section if absent. Returns possibly-new body."""
    if any(ln.strip() == heading for ln in body.splitlines()):
        return body
    sep = "" if body.endswith("\n\n") else ("\n" if body.endswith("\n") else "\n\n")
    return body + sep + heading + "\n\n"


def _append_bullets_to_section(body: str, heading: str, new_bullets: list[str]) -> str:
    """Append ``- <bullet>`` lines to the end of a ``## heading`` section.

    Idempotent at the caller level (caller filters already-present items).
    """
    body = _ensure_section(body, heading)
    lines = body.splitlines(keepends=True)
    # locate heading, then the end of its section (next "## " or EOF).
    start = next(i for i, ln in enumerate(lines) if ln.strip() == heading)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j].strip()
        if s.startswith("## ") and not s.startswith("### "):
            end = j
            break
    # trim trailing blank lines inside the section, then insert bullets.
    insert_at = end
    while insert_at - 1 > start and not lines[insert_at - 1].strip():
        insert_at -= 1
    addition = "".join(f"- {b}\n" for b in new_bullets)
    new_lines = lines[:insert_at] + [addition] + lines[insert_at:]
    return "".join(new_lines)


def _apply_citation_add(body: str, *, add_citations: Sequence[str], **_: object) -> str:
    """Append spec IDs to ``## Specification Links`` (idempotent)."""
    if not add_citations:
        raise BridgeReviseError("citation_add requires at least one --add-citation SPEC-ID.")
    present = set(re.findall(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9-]+\b", body))
    fresh = [c for c in add_citations if c not in present]
    if not fresh:
        return body  # all already cited — no-op
    bullets = [f"`{c}` — added via `gt bridge revise` (citation_add)." for c in fresh]
    return _append_bullets_to_section(body, "## Specification Links", bullets)


def _apply_target_paths_add(body: str, *, add_target_paths: Sequence[str], **_: object) -> str:
    """Append concrete paths to the ``## target_paths`` section (idempotent)."""
    if not add_target_paths:
        raise BridgeReviseError("target_paths_add requires at least one --add-target-path <path>.")
    fresh = [p for p in add_target_paths if f"`{p}`" not in body and p not in body]
    if not fresh:
        return body
    bullets = [f"`{p}`" for p in fresh]
    return _append_bullets_to_section(body, "## target_paths", bullets)


_FIX_DISPATCH = {
    "content_carryforward_only": _apply_content_carryforward_only,
    "citation_add": _apply_citation_add,
    "target_paths_add": _apply_target_paths_add,
}


# --- Provenance ---------------------------------------------------------------


def _bump_version_and_provenance(body: str, new_version: int, source_path: Path, reason: str) -> str:
    """Set ``Version:`` to ``new_version`` and append a revise-provenance line."""
    if _VERSION_HEADER_RE.search(body):
        body = _VERSION_HEADER_RE.sub(rf"\g<prefix>{new_version:03d}", body, count=1)
    provenance = f"Responds to: {source_path.as_posix()} (revise: {reason})"
    if provenance in body:
        return body
    # Insert the provenance line immediately after the first status-token line.
    lines = body.splitlines(keepends=True)
    insert_at = 0
    for i, ln in enumerate(lines):
        if ln.strip():
            insert_at = i + 1
            break
    lines.insert(insert_at, provenance + "\n")
    return "".join(lines)


# --- Orchestration ------------------------------------------------------------


def _rerun_preflights(slug: str, project_root: Path) -> dict[str, str]:
    """Re-run both bridge preflights; return a compact pass/gap summary each."""
    summaries: dict[str, str] = {}
    venv_py = project_root / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
    interpreter = str(venv_py) if venv_py.is_file() else sys.executable
    checks = {
        "applicability": ("scripts/bridge_applicability_preflight.py", ("preflight_passed", "missing_required")),
        "clause": ("scripts/adr_dcl_clause_preflight.py", ("Blocking gaps", "Evidence gaps")),
    }
    for name, (script, needles) in checks.items():
        try:
            proc = subprocess.run(
                [interpreter, str(project_root / script), "--bridge-id", slug],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=False,
            )
            picked = [ln.strip() for ln in proc.stdout.splitlines() if any(n in ln for n in needles)]
            summaries[name] = " | ".join(picked) if picked else f"(exit {proc.returncode}; no summary line)"
        except Exception as exc:  # noqa: BLE001 - surface, don't crash the revise
            summaries[name] = f"(preflight invocation error: {exc})"
    return summaries


def revise(
    slug: str,
    reason: str,
    fix_class: str,
    *,
    add_citations: Sequence[str] = (),
    add_target_paths: Sequence[str] = (),
    dry_run: bool = False,
    project_root: Path | None = None,
) -> ReviseResult:
    """File a deterministic REVISED for ``slug`` applying ``fix_class``.

    Returns a :class:`ReviseResult`. With ``dry_run=True`` nothing is written
    and no INDEX mutation occurs; the preview content + INDEX line are computed.
    """
    if not reason or not reason.strip():
        raise BridgeReviseError("--reason is required and must be non-empty.")
    if fix_class in SLICE_2_FIX_CLASSES:
        raise BridgeReviseError(
            f"fix-class {fix_class!r} is a Slice-2 structural fix-class, deferred and not yet "
            f"implemented. Slice-1 supports: {', '.join(SLICE_1_FIX_CLASSES)}."
        )
    if fix_class not in SLICE_1_FIX_CLASSES:
        raise BridgeReviseError(f"unknown fix-class {fix_class!r}; expected one of {', '.join(SLICE_1_FIX_CLASSES)}.")

    project_root = (project_root or _discover_project_root()).resolve()
    bridge_dir = project_root / "bridge"
    index_path = bridge_dir / "INDEX.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""

    write_bridge, atomic_index_update = _load_helpers(project_root)

    source_path = find_carryforward_source(slug, index_text, bridge_dir)
    source_body = source_path.read_text(encoding="utf-8")  # byte-identical carry-forward
    new_ver = next_version(slug, index_text, bridge_dir)

    transform = _FIX_DISPATCH[fix_class]
    new_body = transform(source_body, add_citations=add_citations, add_target_paths=add_target_paths)
    new_body = _bump_version_and_provenance(new_body, new_ver, source_path, reason.strip())

    # Credential-safe gate (abort on hit — the revise never silently redacts).
    hits = write_bridge.scan_credential_hits(new_body)
    new_body = write_bridge.handle_hits_abort_or_redact(new_body, hits, mode="abort")

    new_path = bridge_dir / f"{slug}-{new_ver:03d}.md"
    index_status_line = f"REVISED: bridge/{slug}-{new_ver:03d}.md"

    result = ReviseResult(
        slug=slug,
        fix_class=fix_class,
        reason=reason.strip(),
        source_path=source_path,
        new_version=new_ver,
        new_path=new_path,
        new_content=new_body,
        index_status_line=index_status_line,
        dry_run=dry_run,
    )
    if dry_run:
        return result

    if new_path.exists():
        raise BridgeReviseError(f"{new_path} already exists; refusing to overwrite.")

    # Session + work-intent claim (reuse the canonical resolver — checks both
    # CLAUDE_SESSION_ID and CLAUDE_CODE_SESSION_ID; no new derivation path).
    session_id = write_bridge.resolve_work_intent_session_id()
    registry = write_bridge._acquire_bridge_work_intent(slug, session_id, project_root=project_root)
    try:
        new_path.write_bytes(new_body.encode("utf-8"))
        # Atomic, serialized INDEX REVISED-line insertion (GOV-FILE-BRIDGE-AUTHORITY-001).
        state_dir = project_root / ".gtkb-state" / "bridge-poller"
        atomic_index_update(
            index_path,
            lambda text: write_bridge.compose_index_update(slug, new_ver, "REVISED", text),
            state_dir=state_dir,
        )
    finally:
        write_bridge._release_bridge_work_intent(registry, slug, session_id, project_root=project_root)

    result.written = True
    result.preflight_summaries = _rerun_preflights(slug, project_root)
    return result
