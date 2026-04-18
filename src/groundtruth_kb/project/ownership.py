# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Artifact Ownership Matrix — ``OwnershipResolver`` query API.

This module consumes the typed loader output from
:mod:`groundtruth_kb.project.managed_registry` (GO C2: no parallel raw-TOML
parser). Every :class:`~groundtruth_kb.project.managed_registry.ManagedArtifact`
loaded by ``_load_all_artifacts()`` carries an
:class:`~groundtruth_kb.project.managed_registry.OwnershipMeta` block (either
explicitly declared in TOML or class-default-derived per GO C1). The resolver
joins registry-class rows (keyed by ``target_path``) and ``ownership-glob``
rows (keyed by ``path_glob``) into a single query surface.

Design per ``bridge/gtkb-artifact-ownership-matrix-003.md`` §2.2.

**Owner-decision-pending heuristic (C3):** a row is flagged
``owner_decision_pending = "YES"`` iff its ownership enum equals
``legacy-exception``. This is the simplest deterministic rule and keeps the
initial report set to the rows mandated by GO C3 + the ``groundtruth.db``
row already defined in §1.4.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from groundtruth_kb.project.managed_registry import (
    DivergencePolicyEnum,
    FileArtifact,
    GitignorePattern,
    ManagedArtifact,
    OwnershipEnum,
    OwnershipGlobArtifact,
    SettingsHookRegistration,
    UpgradePolicyEnum,
    _load_all_artifacts,
)

# Cache for translated glob → regex (shared across resolver instances).
_GLOB_CACHE: dict[str, re.Pattern[str]] = {}

# The five ownership enum values, in the canonical report-ordering order.
_OWNERSHIP_SORT_ORDER: dict[str, int] = {
    "gt-kb-managed": 0,
    "gt-kb-scaffolded": 1,
    "shared-structured": 2,
    "adopter-owned": 3,
    "legacy-exception": 4,
}

# Default ignore globs when walking a tree for classification. Patterns use
# leading ``**/`` where the directory may appear at any depth (Agent Red has
# ``widget/node_modules/`` and similar nested vendor trees that would otherwise
# balloon the report). Includes common tool caches (pytest, hypothesis, codex
# pydeps, playwright) since those are never adopter content — they regenerate.
_DEFAULT_IGNORE_GLOBS: tuple[str, ...] = (
    ".git/**",
    "**/.git/**",
    ".venv/**",
    "**/.venv/**",
    "node_modules/**",
    "**/node_modules/**",
    "__pycache__/**",
    "**/__pycache__/**",
    ".pytest_cache/**",
    "**/.pytest_cache/**",
    ".mypy_cache/**",
    "**/.mypy_cache/**",
    ".ruff_cache/**",
    "**/.ruff_cache/**",
    ".groundtruth-chroma/**",
    "**/.groundtruth-chroma/**",
    ".hypothesis/**",
    "**/.hypothesis/**",
    ".codex_pydeps/**",
    "**/.codex_pydeps/**",
    ".playwright-mcp/**",
    "**/.playwright-mcp/**",
    "dist/**",
    "**/dist/**",
    "build/**",
    "**/build/**",
    ".next/**",
    "**/.next/**",
    "coverage/**",
    "**/coverage/**",
    # GT-KB upgrade staging.
    ".gt-upgrade-staging/**",
    # Log directories (operational, high-volume, non-adopter-content).
    "logs/**",
    "**/logs/**",
    # Compiled bytecode.
    "**/*.pyc",
    "**/*.pyo",
)

_SourceClass = Literal["file", "settings-hook-registration", "gitignore-pattern", "ownership-glob", "__fallback__"]


@dataclass(frozen=True)
class OwnershipRecord:
    """Unified ownership view across registry-class rows and ownership-glob rows.

    Exactly one of ``source`` / ``path_glob`` is set, discriminated by
    ``source_class``.
    """

    id: str
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None
    source_class: _SourceClass
    workflow_targets: tuple[str, ...] = ()
    notes: str = ""
    source: ManagedArtifact | None = None
    path_glob: str | None = None
    priority: int | None = None


@dataclass(frozen=True)
class ClassificationRow:
    """One path classified against the ownership map.

    Emitted by :meth:`OwnershipResolver.classify_tree` and rendered into the
    Agent Red classification report per §4 of the proposal.
    """

    path: str
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None
    notes: str
    owner_decision_pending: bool
    record_id: str


class OwnershipResolver:
    """Query API for the unified ownership map.

    Consumes the typed output of
    :func:`~groundtruth_kb.project.managed_registry._load_all_artifacts` — the
    resolver never re-parses TOML.

    ``classify_path`` applies the precedence documented in §2.2 of the
    proposal:

      1. Exact match against any FILE-class registry row's ``target_path``.
      2. Glob match against ``ownership-glob`` rows, ordered by ``priority``
         descending, tiebreak by longest literal prefix of ``path_glob``,
         then by lexical order of ``id``. First match wins.
      3. Fallback: synthetic record with ``ownership='adopter-owned'``,
         ``upgrade_policy='preserve'``, divergence policy ``None``, ``id``
         prefixed with ``__fallback__:``.

    Non-file-class registry rows (``settings-hook-registration``,
    ``gitignore-pattern``) are NOT returned by :meth:`classify_path` because
    their logical targets collide (the same ``.claude/settings.json`` hosts
    11 registrations). They are accessible only via :meth:`classify_by_id`
    and :meth:`all_records`.
    """

    def __init__(self) -> None:
        """Load the full typed artifact list once at construction time."""
        self._artifacts: list[ManagedArtifact] = _load_all_artifacts()
        # Pre-compute lookups for fast classify_path.
        self._by_id: dict[str, ManagedArtifact] = {a.id: a for a in self._artifacts}
        self._file_rows_by_target: dict[str, FileArtifact] = {}
        self._glob_rows: list[OwnershipGlobArtifact] = []
        for a in self._artifacts:
            if isinstance(a, FileArtifact):
                # target_path values are unique by construction (tested in
                # test_managed_registry); last-wins is fine.
                self._file_rows_by_target[a.target_path] = a
            elif isinstance(a, OwnershipGlobArtifact):
                self._glob_rows.append(a)
        # Order glob rows: priority desc, then longest literal prefix desc,
        # then lexical id asc. Applied once so classify_path is O(n).
        self._glob_rows.sort(key=lambda g: (-g.priority, -_literal_prefix_length(g.path_glob), g.id))

    # -- Query API -------------------------------------------------------

    def classify_by_id(self, record_id: str) -> OwnershipRecord:
        """Return the ownership record whose ``id`` matches *record_id*.

        Raises:
            KeyError: if no record has the given id.
        """
        artifact = self._by_id.get(record_id)
        if artifact is None:
            raise KeyError(f"no ownership record for id {record_id!r}")
        return _to_ownership_record(artifact)

    def classify_path(self, relpath: str) -> OwnershipRecord:
        """Classify a repository-relative POSIX-style path.

        Precedence: exact FILE-class match → glob match → synthetic fallback.

        The input should use forward slashes; Windows callers may pass a
        native path and it will be normalised.
        """
        norm = relpath.replace(os.sep, "/").lstrip("/")

        # 1. Exact match on any FILE-class row's target_path.
        file_row = self._file_rows_by_target.get(norm)
        if file_row is not None:
            return _to_ownership_record(file_row)

        # 2. Glob match (rows already sorted in __init__).
        for glob_row in self._glob_rows:
            if _match_glob(glob_row.path_glob, norm):
                return _to_ownership_record(glob_row)

        # 3. Fallback.
        return OwnershipRecord(
            id=f"__fallback__:{norm}",
            ownership="adopter-owned",
            upgrade_policy="preserve",
            adopter_divergence_policy=None,
            source_class="__fallback__",
            workflow_targets=(),
            notes="Unclassified path — no FILE-class or ownership-glob match.",
            source=None,
            path_glob=None,
            priority=None,
        )

    def all_records(self) -> list[OwnershipRecord]:
        """All ownership records in deterministic order by (ownership enum, id)."""
        records = [_to_ownership_record(a) for a in self._artifacts]
        records.sort(key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.id))
        return records

    # -- Tree walker -----------------------------------------------------

    def classify_tree(
        self,
        tree_root: Path,
        *,
        max_depth: int = 10,
        ignore_globs: tuple[str, ...] = _DEFAULT_IGNORE_GLOBS,
    ) -> list[ClassificationRow]:
        """Walk *tree_root* and classify every file.

        The walk is READ-ONLY — no filesystem writes are performed by this
        method or any of its helpers. Directories matched by *ignore_globs*
        are pruned from ``os.walk``. ``max_depth`` is measured relative to
        ``tree_root`` (0 = only files in the root).
        """
        tree_root = tree_root.resolve()
        rows: list[ClassificationRow] = []

        for dirpath, dirnames, filenames in os.walk(tree_root):
            # Depth relative to tree_root (rel may be "." for root).
            try:
                rel_dir = str(Path(dirpath).resolve().relative_to(tree_root)).replace(os.sep, "/")
            except ValueError:
                # Can happen on Windows with mixed drive resolution — skip.
                continue
            if rel_dir == ".":
                depth = 0
                rel_prefix = ""
            else:
                depth = rel_dir.count("/") + 1
                rel_prefix = rel_dir + "/"

            # Depth gate (inclusive): if we're already past max_depth, stop descending.
            if depth > max_depth:
                dirnames[:] = []
                continue

            # Prune ignored directories (before descent).
            pruned: list[str] = []
            for d in dirnames:
                cand = (rel_prefix + d).lstrip("/")
                if any(_match_glob(g, cand) or _match_glob(g, cand + "/") for g in ignore_globs):
                    continue
                pruned.append(d)
            dirnames[:] = pruned

            # Classify files at this level.
            for filename in filenames:
                rel_path = (rel_prefix + filename).lstrip("/")
                if any(_match_glob(g, rel_path) for g in ignore_globs):
                    continue
                record = self.classify_path(rel_path)
                rows.append(
                    ClassificationRow(
                        path=rel_path,
                        ownership=record.ownership,
                        upgrade_policy=record.upgrade_policy,
                        adopter_divergence_policy=record.adopter_divergence_policy,
                        notes=record.notes,
                        owner_decision_pending=(record.ownership == "legacy-exception"),
                        record_id=record.id,
                    )
                )

        rows.sort(key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.path))
        return rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _to_ownership_record(artifact: ManagedArtifact) -> OwnershipRecord:
    """Project a loader dataclass onto the unified :class:`OwnershipRecord`."""
    if isinstance(artifact, OwnershipGlobArtifact):
        glob_meta = artifact.ownership
        return OwnershipRecord(
            id=artifact.id,
            ownership=glob_meta.ownership,
            upgrade_policy=glob_meta.upgrade_policy,
            adopter_divergence_policy=glob_meta.adopter_divergence_policy,
            source_class="ownership-glob",
            workflow_targets=glob_meta.workflow_targets,
            notes=artifact.notes,
            source=artifact,
            path_glob=artifact.path_glob,
            priority=artifact.priority,
        )

    reg_meta = artifact.ownership
    if reg_meta is None:
        # Unreachable in current loader (every non-ownership-glob row receives
        # either an explicit or class-default OwnershipMeta), but the type
        # says it could be None. Raise rather than silently fall back.
        raise ValueError(f"artifact {artifact.id!r} has no ownership metadata (loader invariant violated)")

    if isinstance(artifact, FileArtifact):
        source_class: _SourceClass = "file"
    elif isinstance(artifact, SettingsHookRegistration):
        source_class = "settings-hook-registration"
    elif isinstance(artifact, GitignorePattern):
        source_class = "gitignore-pattern"
    else:  # pragma: no cover — exhausted by earlier isinstance checks
        raise TypeError(f"unknown artifact type {type(artifact).__name__}")

    return OwnershipRecord(
        id=artifact.id,
        ownership=reg_meta.ownership,
        upgrade_policy=reg_meta.upgrade_policy,
        adopter_divergence_policy=reg_meta.adopter_divergence_policy,
        source_class=source_class,
        workflow_targets=reg_meta.workflow_targets,
        notes="",
        source=artifact,
        path_glob=None,
        priority=None,
    )


def _match_glob(glob: str, path: str) -> bool:
    """Glob matcher supporting ``**`` recursive wildcards (POSIX-style).

    Translates *glob* to a regular expression where:

    - ``**`` matches any sequence of characters including ``/`` (zero or more
      path segments).
    - ``*`` matches any sequence NOT containing ``/`` (single-segment).
    - ``?`` matches a single character (not ``/``).
    - Literal characters are escaped.

    Additionally, a trailing ``/**`` is treated as matching everything under
    the prefix directory (any depth).
    """
    regex = _glob_to_regex(glob)
    return regex.fullmatch(path) is not None


def _glob_to_regex(glob: str) -> re.Pattern[str]:
    """Compile *glob* to an anchored regular expression. Cached by pattern.

    Conventions (POSIX / globstar):

    - ``**`` as an isolated path segment (``prefix/**/suffix``) matches zero
      or more path segments, including the separating ``/``. So
      ``bridge/**/*.md`` matches both ``bridge/foo.md`` and
      ``bridge/sub/foo.md``.
    - ``**`` at the end of a pattern (``prefix/**``) matches any content
      (including ``/``) under *prefix*. Also matches *prefix* with nothing
      after (the directory itself).
    - ``**`` at the start (``**/suffix``) matches *suffix* at any depth,
      including at the root.
    - ``*`` matches any sequence not containing ``/``.
    - ``?`` matches one character that is not ``/``.
    - ``[...]`` character classes pass through verbatim.
    """
    cached = _GLOB_CACHE.get(glob)
    if cached is not None:
        return cached

    # Pre-normalise well-known ``**`` segment patterns so the translator can
    # handle them as atomic tokens rather than greedy substrings.
    # ``/**/`` → a single placeholder that regex-translates to ``(?:/|/.*/)``
    # so "bridge/**/*.md" matches both "bridge/foo.md" and "bridge/sub/foo.md".
    DSTAR_SEG = "\x00DSTARSEG\x00"  # /**/
    DSTAR_PFX = "\x00DSTARPFX\x00"  # **/   (at start)
    DSTAR_SFX = "\x00DSTARSFX\x00"  # /**   (at end) or bare **
    working = glob
    working = working.replace("/**/", DSTAR_SEG)
    if working.startswith("**/"):
        working = DSTAR_PFX + working[3:]
    if working.endswith("/**"):
        working = working[:-3] + DSTAR_SFX
    if working == "**":
        working = DSTAR_SFX

    i = 0
    out: list[str] = []
    n = len(working)
    while i < n:
        # Multi-character placeholders first.
        if working.startswith(DSTAR_SEG, i):
            out.append("(?:/|/.*/)")
            i += len(DSTAR_SEG)
            continue
        if working.startswith(DSTAR_PFX, i):
            out.append("(?:|.*/)")
            i += len(DSTAR_PFX)
            continue
        if working.startswith(DSTAR_SFX, i):
            out.append("(?:|/.*)")
            i += len(DSTAR_SFX)
            continue

        ch = working[i]
        if ch == "*":
            # Bare * — count consecutive stars.
            stars = 1
            j = i + 1
            while j < n and working[j] == "*":
                stars += 1
                j += 1
            if stars >= 2:
                # Embedded ** that isn't a full segment — allow /-crossing match.
                out.append(".*")
            else:
                # single * = match any chars except /
                out.append("[^/]*")
            i = j
        elif ch == "?":
            out.append("[^/]")
            i += 1
        elif ch in ".+(){}|^$\\":
            out.append(re.escape(ch))
            i += 1
        elif ch == "[":
            # Pass through character class verbatim up to ].
            close = working.find("]", i + 1)
            if close < 0:
                out.append(re.escape(ch))
                i += 1
            else:
                out.append(working[i : close + 1])
                i = close + 1
        else:
            out.append(re.escape(ch))
            i += 1

    pattern = re.compile("^" + "".join(out) + "$")
    _GLOB_CACHE[glob] = pattern
    return pattern


def _literal_prefix_length(glob: str) -> int:
    """Return the length of the literal prefix before the first wildcard.

    Used to break ties among globs with the same priority (documented
    precedence: longer literal prefix wins).
    """
    for i, ch in enumerate(glob):
        if ch in "*?[":
            return i
    return len(glob)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def render_classification_report_markdown(
    rows: list[ClassificationRow],
    *,
    gt_kb_version: str,
    gt_kb_head: str,
    target_tree: str,
    target_head: str,
) -> str:
    """Render a classification row list as a Markdown report per §4.

    Ordering is by (ownership enum, path); ``classify_tree`` already does this,
    but the function re-sorts defensively so callers can pass rows from any
    source.
    """
    sorted_rows = sorted(rows, key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.path))
    decision_pending = [r for r in sorted_rows if r.owner_decision_pending]
    generated = datetime.now(UTC).isoformat(timespec="seconds")

    lines: list[str] = []
    lines.append("# Agent Red Classification Report")
    lines.append("")
    lines.append(f"- Generated: {generated}")
    lines.append(f"- GT-KB version: {gt_kb_version}")
    lines.append(f"- GT-KB HEAD: {gt_kb_head}")
    lines.append(f"- Target tree: {target_tree}")
    lines.append(f"- Target HEAD: {target_head}")
    lines.append(f"- Total paths classified: {len(sorted_rows)}")
    lines.append(f"- Owner-decision-pending rows: {len(decision_pending)}")
    lines.append("")
    lines.append("| path | ownership | upgrade_policy | divergence_policy | notes | owner_decision_pending |")
    lines.append("|---|---|---|---|---|---|")
    for r in sorted_rows:
        div = r.adopter_divergence_policy if r.adopter_divergence_policy is not None else "—"
        pend = "YES" if r.owner_decision_pending else ""
        notes = (r.notes or "").replace("|", "\\|").replace("\n", " ")
        path = r.path.replace("|", "\\|")
        lines.append(f"| {path} | {r.ownership} | {r.upgrade_policy} | {div} | {notes} | {pend} |")
    lines.append("")
    return "\n".join(lines)


def render_classification_report_json(
    rows: list[ClassificationRow],
    *,
    gt_kb_version: str,
    gt_kb_head: str,
    target_tree: str,
    target_head: str,
) -> str:
    """Render a classification row list as a JSON report."""
    import json

    sorted_rows = sorted(rows, key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.path))
    decision_pending_count = sum(1 for r in sorted_rows if r.owner_decision_pending)
    payload = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "gt_kb_version": gt_kb_version,
        "gt_kb_head": gt_kb_head,
        "target_tree": target_tree,
        "target_head": target_head,
        "total_paths_classified": len(sorted_rows),
        "owner_decision_pending_rows": decision_pending_count,
        "rows": [
            {
                "path": r.path,
                "ownership": r.ownership,
                "upgrade_policy": r.upgrade_policy,
                "adopter_divergence_policy": r.adopter_divergence_policy,
                "notes": r.notes,
                "owner_decision_pending": r.owner_decision_pending,
                "record_id": r.record_id,
            }
            for r in sorted_rows
        ],
    }
    return json.dumps(payload, indent=2)
