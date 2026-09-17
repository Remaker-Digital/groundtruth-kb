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

import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

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

_SourceClass = Literal[
    "file", "settings-hook-registration", "gitignore-pattern", "ownership-glob", "registry", "__fallback__"
]


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
    """One path classified against the selected root's declarations or, when it carries none, the template map.

    Emitted by :meth:`OwnershipResolver.classify_tree` and rendered by the tree classification report. ``finding``
    names a diagnostic the classification cannot resolve: ``undeclared`` (no current declaration of the selected root
    covers the path; without a declaration source, no template row does) or ``unreadable`` (the walk could not read
    it). A finding grants no ownership or authorization. ``template_hint`` names the packaged template record that
    knows an undeclared path: orientation only, never coverage — a packaged copy cannot independently grant
    membership (GOV-PLATFORM-SOT-REGISTRY-001).
    """

    path: str
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None
    notes: str
    record_id: str
    finding: str | None = None
    template_hint: str | None = None


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
        declared: DeclarationLookup | None = None,
    ) -> list[ClassificationRow]:
        """Walk *tree_root* and classify every file.

        The walk is READ-ONLY — no filesystem writes are performed by this
        method or any of its helpers. Directories matched by *ignore_globs*
        are pruned from ``os.walk``. ``max_depth`` is measured relative to
        ``tree_root`` (0 = only files in the root). When *declared* is given
        (see :func:`load_target_declarations`) the selected root's current
        declarations are the sole coverage: a path it covers takes that
        declaration and every other path is an ``undeclared`` finding whose
        template match, if any, is reported as a hint. Without *declared* the
        template map classifies (a target that carries no declaration file).
        """
        tree_root = tree_root.resolve()
        rows: list[ClassificationRow] = []
        unreadable: list[str] = []

        def _record_unreadable(error: OSError) -> None:
            failed = Path(str(error.filename or tree_root))
            try:
                relative = str(failed.resolve().relative_to(tree_root)).replace(os.sep, "/")
            except (OSError, ValueError):
                relative = str(failed)
            unreadable.append(relative if relative != "." else "")

        for dirpath, dirnames, filenames in os.walk(tree_root, onerror=_record_unreadable):
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
                rows.append(self._classify_row(rel_path, declared))
        for rel_path in sorted(set(unreadable)):
            rows.append(
                ClassificationRow(
                    path=rel_path,
                    ownership="adopter-owned",
                    upgrade_policy="preserve",
                    adopter_divergence_policy=None,
                    notes="The walk could not read this path.",
                    record_id=f"__fallback__:{rel_path}",
                    finding="unreadable",
                )
            )

        rows.sort(key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.path))
        return rows

    def _classify_row(self, rel_path: str, declared: DeclarationLookup | None) -> ClassificationRow:
        """Classify one walked file; the selected root's declarations, when consulted, are the sole coverage."""
        template_hint: str | None = None
        if declared is None:
            record = self.classify_path(rel_path)
        else:
            declared_record = declared(rel_path)
            if declared_record is not None:
                record = declared_record
            else:
                template = self.classify_path(rel_path)
                if template.source_class != "__fallback__":
                    template_hint = template.id
                record = _undeclared_record(rel_path, template)
        return ClassificationRow(
            path=rel_path,
            ownership=record.ownership,
            upgrade_policy=record.upgrade_policy,
            adopter_divergence_policy=record.adopter_divergence_policy,
            notes=record.notes,
            record_id=record.id,
            finding="undeclared" if record.source_class == "__fallback__" else None,
            template_hint=template_hint,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _undeclared_record(norm: str, template: OwnershipRecord) -> OwnershipRecord:
    """The finding record for a path no current declaration of the selected root covers.

    *template* is the packaged template map's answer for the same path; a match is reported in the notes as a hint.
    It grants nothing: the row stays adopter-owned/preserve with an ``undeclared`` finding.
    """
    notes = "No current declaration of the selected root covers this path."
    if template.source_class != "__fallback__":
        notes += (
            f" Template hint: {template.id} ({template.ownership}, {template.upgrade_policy});"
            " a packaged template grants no membership."
        )
    return OwnershipRecord(
        id=f"__fallback__:{norm}",
        ownership="adopter-owned",
        upgrade_policy="preserve",
        adopter_divergence_policy=None,
        source_class="__fallback__",
        workflow_targets=(),
        notes=notes,
        source=None,
        path_glob=None,
        priority=None,
    )


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
        notes=reg_meta.notes,
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
# The selected target's current declarations
# ---------------------------------------------------------------------------

PLATFORM_DECLARATION = "config/registry/sot-artifacts.toml"
APPLICATION_DECLARATION = ".gtkb-app-isolation.json"
DeclarationLookup = Callable[[str], "OwnershipRecord | None"]


@dataclass(frozen=True)
class DeclarationSource:
    """Which current declaration the classification consulted for the selected target.

    ``kind`` is ``platform-registry`` (the target's SoT artifact registry through the registry resolver),
    ``application-registry`` (the application's artifact-boundary registry, validated by the application-boundary
    validator), ``none`` (neither file exists at the target: template classifications only) or ``unavailable`` (a
    declaration file exists but cannot be read or validated; its cause is in ``detail`` and ``findings``, nothing is
    covered and every walked path is an ``undeclared`` finding — the packaged templates infer nothing). ``findings``
    carries the validator's structured findings (``code``, ``message``, ``severity`` and, where known, ``path``).
    """

    kind: Literal["platform-registry", "application-registry", "none", "unavailable"]
    path: str | None
    declarations: int
    detail: str
    findings: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": self.path,
            "declarations": self.declarations,
            "detail": self.detail,
            "findings": [dict(finding) for finding in self.findings],
        }


def _platform_declaration_record(record: Any) -> OwnershipRecord:
    generated = record.lifecycle == "generated"
    return OwnershipRecord(
        id=record.id,
        ownership="gt-kb-managed",
        upgrade_policy="overwrite" if generated else "preserve",
        adopter_divergence_policy=None,
        source_class="registry",
        workflow_targets=(),
        notes=(
            f"Declared by the platform registry: domain {record.domain}, lifecycle {record.lifecycle}, "
            f"coverage {record.coverage_mode}, owner role {record.owner_role}."
        ),
        source=None,
        path_glob=None,
        priority=None,
    )


# One row per classification the application-boundary validator allows (``ALLOWED_CLASSIFICATIONS`` in
# ``groundtruth_kb.isolation.app_root_minimization``); the validator rejects any other value before lookup, so the
# map is indexed directly and never defaults.
_APPLICATION_CLASSIFICATIONS: dict[str, tuple[OwnershipEnum, UpgradePolicyEnum]] = {
    "authoritative_input": ("adopter-owned", "preserve"),
    "generated_output": ("gt-kb-managed", "overwrite"),
    "runtime_data": ("adopter-owned", "transient"),
    "bounded_temporary_output": ("adopter-owned", "transient"),
}


def _uncovered(_relative: str) -> OwnershipRecord | None:
    """The lookup of an unavailable declaration source: nothing is covered and nothing is inferred."""
    return None


def _load_platform_declarations(platform_path: Path) -> tuple[DeclarationSource, DeclarationLookup]:
    from groundtruth_kb.project.registry_control_plane import RegistryCoverageError, RegistryResolver
    from groundtruth_kb.project.sot_registry import InvalidSoTRecord, load_toml

    try:
        records = load_toml(platform_path)
        resolver = RegistryResolver(records)
    except (InvalidSoTRecord, RegistryCoverageError, OSError, ValueError) as error:
        finding = {
            "code": "registry_invalid",
            "message": f"{type(error).__name__}: {error}",
            "severity": "error",
            "path": PLATFORM_DECLARATION,
        }
        return (
            DeclarationSource("unavailable", PLATFORM_DECLARATION, 0, f"{PLATFORM_DECLARATION}: {error}", (finding,)),
            _uncovered,
        )
    usable = sum(1 for record in records if record.lifecycle != "archive" and record.coverage_mode != "virtual")

    def platform_lookup(relative: str) -> OwnershipRecord | None:
        try:
            record = resolver.resolve(relative)
        except RegistryCoverageError:
            return None
        if record is None or record.coverage_mode == "virtual":
            return None
        return _platform_declaration_record(record)

    return (
        DeclarationSource(
            "platform-registry",
            PLATFORM_DECLARATION,
            usable,
            f"{usable} current declaration(s) with filesystem coverage; archived declarations excluded",
        ),
        platform_lookup,
    )


def _load_application_declarations(target: Path, application_path: Path) -> tuple[DeclarationSource, DeclarationLookup]:
    from groundtruth_kb.isolation.app_root_minimization import (
        AppRootFinding,
        _load_registry,
        _normalize_registry_entries,
    )

    findings: list[AppRootFinding] = []
    payload = _load_registry(application_path, target, findings)
    entries = _normalize_registry_entries(payload, target, application_path, findings)
    errors = [finding for finding in findings if finding.severity == "error"]
    if errors:
        summary = "; ".join(f"{finding.code}: {finding.message}" for finding in errors[:3])
        if len(errors) > 3:
            summary += f"; +{len(errors) - 3} more"
        return (
            DeclarationSource(
                "unavailable",
                APPLICATION_DECLARATION,
                0,
                f"{APPLICATION_DECLARATION}: {len(errors)} declaration finding(s): {summary}",
                tuple(finding.to_dict() for finding in findings),
            ),
            _uncovered,
        )
    by_key: dict[tuple[str, str], dict[str, Any]] = {
        (str(entry["name"]), str(entry["type"])): entry for entry in entries
    }

    def application_lookup(relative: str) -> OwnershipRecord | None:
        top, _, rest = relative.partition("/")
        entry = by_key.get((top, "DIR" if rest else "FILE"))
        if entry is None:
            return None
        classification = str(entry["classification"])
        ownership, upgrade = _APPLICATION_CLASSIFICATIONS[classification]
        return OwnershipRecord(
            id=f"application-registry:{top}",
            ownership=ownership,
            upgrade_policy=upgrade,
            adopter_divergence_policy=None,
            source_class="registry",
            workflow_targets=(),
            notes=f"Declared by the application registry as {classification}: {str(entry['purpose']).strip()}",
            source=None,
            path_glob=None,
            priority=None,
        )

    return (
        DeclarationSource(
            "application-registry",
            APPLICATION_DECLARATION,
            len(entries),
            f"{len(entries)} validated top-level artifact entr{'y' if len(entries) == 1 else 'ies'}",
        ),
        application_lookup,
    )


def load_target_declarations(target: Path) -> tuple[DeclarationSource, DeclarationLookup | None]:
    """Return the selected target's current declaration source and a path lookup over it.

    The platform registry is consulted through the existing registry resolver so exact, recursive, glob and
    opaque-container coverage and the archived-declaration exclusion match every other reader of that file. An
    application root's ``.gtkb-app-isolation.json`` is read and validated by the application-boundary validator
    (:mod:`groundtruth_kb.isolation.app_root_minimization`: schema version, application identity, entry names, types,
    classifications, purposes, duplicate entries and duplicate JSON keys); a validated ``FILE`` entry covers that
    top-level file and a ``DIR`` entry covers its descendants. A source that cannot be read or validated is
    ``unavailable`` with the findings listed, and its lookup covers nothing, so every path stays a finding. The lookup
    is ``None`` only when neither file exists (``none``): the one case in which the caller classifies from the
    packaged templates. Declarations are never inferred from the templates.
    """
    platform_path = target / PLATFORM_DECLARATION
    if platform_path.is_file():
        return _load_platform_declarations(platform_path)
    application_path = target / APPLICATION_DECLARATION
    if application_path.is_file():
        return _load_application_declarations(target, application_path)
    return (
        DeclarationSource(
            "none",
            None,
            0,
            f"neither {PLATFORM_DECLARATION} nor {APPLICATION_DECLARATION} exists at the target; "
            "template classifications only",
        ),
        None,
    )


@dataclass(frozen=True)
class TreeClassification:
    """The classification of one selected target: its declaration source and the classified rows."""

    target: str
    declaration_source: DeclarationSource
    rows: list[ClassificationRow]


def classify_target(
    target: Path,
    *,
    max_depth: int = 10,
    ignore_globs: tuple[str, ...] = _DEFAULT_IGNORE_GLOBS,
    resolver: OwnershipResolver | None = None,
) -> TreeClassification:
    """Classify a selected target against its own current declarations.

    The template map classifies only a target that carries no declaration file; otherwise it supplies hints for
    the paths the declarations do not cover, which remain findings.
    """
    target = target.resolve()
    source, lookup = load_target_declarations(target)
    rows = (resolver or OwnershipResolver()).classify_tree(
        target, max_depth=max_depth, ignore_globs=ignore_globs, declared=lookup
    )
    return TreeClassification(str(target), source, rows)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def _report_payload(
    rows: list[ClassificationRow],
    *,
    gt_kb_version: str,
    target_tree: str,
    declaration_source: DeclarationSource | None = None,
) -> dict[str, Any]:
    sorted_rows = sorted(rows, key=lambda r: (_OWNERSHIP_SORT_ORDER[r.ownership], r.path))
    findings = [r for r in sorted_rows if r.finding]
    source = declaration_source or DeclarationSource("none", None, 0, "no declaration source was consulted")
    return {
        "report": "tree-classification",
        "gt_kb_version": gt_kb_version,
        "target_tree": target_tree,
        "declaration_source": source.to_dict(),
        "total_paths_classified": len(sorted_rows),
        "findings": {
            "undeclared": sum(1 for r in findings if r.finding == "undeclared"),
            "unreadable": sum(1 for r in findings if r.finding == "unreadable"),
        },
        "rows": [
            {
                "path": r.path,
                "ownership": r.ownership,
                "upgrade_policy": r.upgrade_policy,
                "adopter_divergence_policy": r.adopter_divergence_policy,
                "notes": r.notes,
                "record_id": r.record_id,
                "finding": r.finding,
                "template_hint": r.template_hint,
            }
            for r in sorted_rows
        ],
    }


def _describe_source(source: dict[str, Any]) -> str:
    if source["kind"] in ("platform-registry", "application-registry"):
        return f"{source['kind']} ({source['path']}; {source['detail']})"
    return f"{source['kind']} ({source['detail']})"


def render_classification_report_markdown(
    rows: list[ClassificationRow],
    *,
    gt_kb_version: str,
    target_tree: str,
    declaration_source: DeclarationSource | None = None,
) -> str:
    """Render a classification row list as a deterministic Markdown report.

    Ordering is by (ownership enum, path); ``classify_tree`` already does this, but the function re-sorts
    defensively so callers can pass rows from any source. Findings (undeclared, unreadable) are diagnostics: they
    grant no ownership or authorization. The header names the declaration source the classification consulted. Two
    optional sections follow the table: the template hints for undeclared paths (not coverage) and the declaration
    findings of an unavailable source.
    """
    payload = _report_payload(
        rows, gt_kb_version=gt_kb_version, target_tree=target_tree, declaration_source=declaration_source
    )
    lines: list[str] = []
    lines.append("# Tree classification report")
    lines.append("")
    lines.append(f"- GT-KB version: {gt_kb_version}")
    lines.append(f"- Target tree: {target_tree}")
    lines.append(f"- Declaration source: {_describe_source(payload['declaration_source'])}")
    lines.append(f"- Total paths classified: {payload['total_paths_classified']}")
    lines.append(
        f"- Findings: {payload['findings']['undeclared']} undeclared, {payload['findings']['unreadable']} unreadable"
    )
    lines.append("")
    lines.append("| path | ownership | upgrade_policy | divergence_policy | record | finding |")
    lines.append("|---|---|---|---|---|---|")
    for r in payload["rows"]:
        div = r["adopter_divergence_policy"] if r["adopter_divergence_policy"] is not None else "—"
        path = str(r["path"]).replace("|", "\\|")
        record = str(r["record_id"]).replace("|", "\\|")
        lines.append(f"| {path} | {r['ownership']} | {r['upgrade_policy']} | {div} | {record} | {r['finding'] or ''} |")
    hinted = [r for r in payload["rows"] if r["template_hint"]]
    if hinted:
        lines.append("")
        lines.append("## Template hints")
        lines.append("")
        lines.append("Packaged template records that know an undeclared path. A hint is not coverage.")
        lines.append("")
        for r in hinted:
            path = str(r["path"]).replace("|", "\\|")
            lines.append(f"- {path}: {r['template_hint']}")
    source_findings = payload["declaration_source"]["findings"]
    if source_findings:
        lines.append("")
        lines.append("## Declaration findings")
        lines.append("")
        lines.append("The declaration source is unavailable; nothing was inferred and every path is a finding.")
        lines.append("")
        for finding in source_findings:
            location = f" ({finding['path']})" if finding.get("path") else ""
            lines.append(f"- {finding['code']}: {finding['message']}{location}")
    lines.append("")
    return "\n".join(lines)


def render_classification_report_json(
    rows: list[ClassificationRow],
    *,
    gt_kb_version: str,
    target_tree: str,
    declaration_source: DeclarationSource | None = None,
) -> str:
    """Render a classification row list as a deterministic JSON report."""
    return (
        json.dumps(
            _report_payload(
                rows, gt_kb_version=gt_kb_version, target_tree=target_tree, declaration_source=declaration_source
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
