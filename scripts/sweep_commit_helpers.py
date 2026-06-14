"""Deterministic sweep-commit batch planning for protected hook-config edits.

WI-4528 (P3, ``tooling``, origin=improvement). The inventory-drift gate
(``scripts/check_dev_environment_inventory_drift.py``, run by
``.githooks/pre-commit --staged --allow-review-evidence``) accepts a protected
hook-config change such as ``.codex/hooks.json`` only when a ``bridge/*.md`` or
``bridge/INDEX.md`` is CO-STAGED in the same commit (``review_evidence_present``).
The protected entries in ``config/governance/protected-artifact-inventory-drift.toml``
that carry ``accept_with_inventory_baseline_update = false`` are the ones that
require this co-staged bridge evidence.

On 2026-06-13 a sweep-commit committed bridge artifacts separately/first, leaving
the dependent ``.codex/hooks.json`` registration with no co-stageable bridge
evidence; the scoped commit was blocked and had to be split. This module computes
the correct co-staging plan so the inventory-drift gate sees
``review_evidence_present`` on the same commit.

The module is **pure planning**: it reads the inventory-drift TOML declaratively
and inspects bridge file bodies, but performs no git invocation, no file
mutation, no bridge writes, and no KB mutation. The orchestrator (the
``gtkb-sweep-commit`` skill, in a follow-on slice) is responsible for executing
``git commit -- <paths>`` per planned batch.

Governing specs: GOV-STANDING-BACKLOG-001 (WI-4528 backlog authority),
GOV-FILE-BRIDGE-AUTHORITY-001 (read-only with respect to bridge artifacts),
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (each behaviour has a test).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import fnmatch
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

__all__ = [
    "CommitBatch",
    "INVENTORY_DRIFT_TOML_RELATIVE_PATH",
    "BRIDGE_EVIDENCE_PATTERNS",
    "load_protected_path_globs",
    "is_protected_path",
    "is_bridge_evidence_path",
    "partition_staged",
    "bridge_files_citing",
    "plan_commit_batches",
]

# Authoritative protected-paths config consumed by the inventory-drift gate.
INVENTORY_DRIFT_TOML_RELATIVE_PATH = Path("config/governance/protected-artifact-inventory-drift.toml")

# Bridge review-evidence patterns, byte-identical to BRIDGE_REVIEW_EVIDENCE_PATTERNS
# in scripts/check_dev_environment_inventory_drift.py. A staged path matching any
# of these satisfies the gate's review_evidence_present condition.
BRIDGE_EVIDENCE_PATTERNS = ("bridge/INDEX.md", "bridge/*.md")


@dataclass(frozen=True)
class CommitBatch:
    """One planned commit: a set of paths committed together, with rationale.

    ``kind`` is one of:
      - ``"protected-with-evidence"``: protected hook-config path(s) grouped with
        at least one co-staged bridge-evidence file (the gate-friendly batch).
      - ``"protected-missing-evidence"``: protected path(s) with NO co-stageable
        bridge evidence in the staged set; committing this batch will be blocked
        by the inventory-drift gate. The ``rationale`` flags the diagnostic.
      - ``"bridge-only"``: bridge file(s) not tied to a specific protected path.
      - ``"unconstrained"``: source, tests, docs, and other non-protected paths.
    """

    paths: list[str]
    kind: str
    rationale: str = ""
    # Bridge-evidence files that justify a protected-with-evidence batch (subset
    # of ``paths``); empty for non-protected batch kinds.
    evidence: list[str] = field(default_factory=list)


def _posix(path: str) -> str:
    """Normalize a path to forward-slash form for cross-platform glob matching."""
    return str(path).replace("\\", "/").strip()


def load_protected_path_globs(project_root: Path | str) -> list[str]:
    """Return the union of protected-path globs that require co-staged bridge evidence.

    Reads ``config/governance/protected-artifact-inventory-drift.toml`` and unions
    the ``patterns`` of every ``[[protected_artifacts]]`` entry whose
    ``accept_with_inventory_baseline_update`` is ``false`` -- i.e. the entries the
    gate will only pass when bridge review evidence is co-staged. Reads
    declaratively so the helper inherits future protected-path additions.

    Returns an empty list (fail-soft) when the TOML is missing or unreadable, so
    callers can degrade to an unconstrained plan rather than blocking a commit.
    """
    toml_path = Path(project_root) / INVENTORY_DRIFT_TOML_RELATIVE_PATH
    try:
        with toml_path.open("rb") as handle:
            loaded = tomllib.load(handle)
    except (FileNotFoundError, OSError, tomllib.TOMLDecodeError):
        return []

    entries = loaded.get("protected_artifacts")
    if not isinstance(entries, list):
        return []

    globs: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        # Only entries that require co-staged bridge evidence are relevant.
        if entry.get("accept_with_inventory_baseline_update") is not False:
            continue
        patterns = entry.get("patterns")
        if not isinstance(patterns, list):
            continue
        for pattern in patterns:
            if not isinstance(pattern, str):
                continue
            norm = _posix(pattern)
            if norm and norm not in seen:
                seen.add(norm)
                globs.append(norm)
    return globs


def is_protected_path(path: str, protected_globs: list[str]) -> bool:
    """Return True if ``path`` matches any protected glob.

    Uses ``fnmatch.fnmatchcase`` on posix-normalized paths, identical to
    ``classify_changed_paths`` in the inventory-drift gate, so a path the helper
    treats as protected is exactly the set the gate treats as protected.
    """
    candidate = _posix(path)
    return any(fnmatch.fnmatchcase(candidate, _posix(glob)) for glob in protected_globs)


def is_bridge_evidence_path(path: str) -> bool:
    """Return True if ``path`` would satisfy the gate's bridge-review-evidence check."""
    candidate = _posix(path)
    return any(fnmatch.fnmatchcase(candidate, pattern) for pattern in BRIDGE_EVIDENCE_PATTERNS)


def partition_staged(paths: list[str], protected_globs: list[str]) -> dict[str, list[str]]:
    """Split staged paths into ``protected`` / ``bridge`` / ``other`` buckets.

    Pure, no I/O. ``bridge`` includes ``bridge/INDEX.md`` and any ``bridge/*.md``
    (the candidate review-evidence files). A path that is both bridge-shaped and
    protected (none exist in the current registry, but defensively) is classified
    as ``protected`` first.
    """
    protected: list[str] = []
    bridge: list[str] = []
    other: list[str] = []
    for raw in paths:
        candidate = _posix(raw)
        if is_protected_path(candidate, protected_globs):
            protected.append(candidate)
        elif is_bridge_evidence_path(candidate):
            bridge.append(candidate)
        else:
            other.append(candidate)
    return {"protected": protected, "bridge": bridge, "other": other}


def bridge_files_citing(
    staged_protected: list[str],
    staged_bridge_files: list[str],
    project_root: Path | str,
) -> dict[str, list[str]]:
    """Map each protected path to the staged bridge files that justify co-staging it.

    For each protected path, returns the list of staged bridge files whose body
    cites the protected path (path-token match or filename mention).
    ``bridge/INDEX.md``, when staged, is included as evidence for EVERY protected
    path: it is the universal gate-satisfier (the gate accepts any
    ``bridge/INDEX.md`` co-stage as review evidence regardless of content).

    Bridge files that cannot be read are skipped (fail-soft); a protected path
    with no citing bridge file maps to an empty list (the missing-evidence case).
    """
    root = Path(project_root)
    index_staged = [bf for bf in staged_bridge_files if _posix(bf) == "bridge/INDEX.md"]
    content_bridge_files = [bf for bf in staged_bridge_files if _posix(bf) != "bridge/INDEX.md"]

    # Pre-read bridge file bodies once.
    bodies: dict[str, str] = {}
    for bridge_file in content_bridge_files:
        try:
            bodies[bridge_file] = (root / bridge_file).read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, OSError):
            continue

    citing: dict[str, list[str]] = {}
    for protected in staged_protected:
        norm_protected = _posix(protected)
        protected_basename = Path(norm_protected).name
        matches: list[str] = []
        for bridge_file, body in bodies.items():
            if norm_protected in body or protected_basename in body:
                matches.append(bridge_file)
        # bridge/INDEX.md is universal evidence; append last so content-specific
        # citations are listed first.
        matches.extend(index_staged)
        citing[norm_protected] = matches
    return citing


def plan_commit_batches(staged: list[str], project_root: Path | str) -> list[CommitBatch]:
    """Compute the ordered list of commit batches for a staged set.

    Guarantees:
      - every protected path is in a batch that ALSO contains at least one
        bridge-evidence file (``kind="protected-with-evidence"``), so the
        inventory-drift gate sees ``review_evidence_present`` on that commit;
      - a protected path with no co-stageable bridge evidence is surfaced in a
        ``protected-missing-evidence`` batch whose rationale flags that the
        commit will be blocked by the gate (the 2026-06-13 incident diagnostic);
      - bridge-only files not tied to a protected path get their own
        ``bridge-only`` batch (preserving the existing swarm bridge-filing
        pattern);
      - other files get an ``unconstrained`` batch.

    Order: protected-with-evidence first (exercise the gate's friendly path
    early), then protected-missing-evidence, then bridge-only, then unconstrained.

    Fail-soft: when the inventory-drift TOML is missing/unreadable,
    ``load_protected_path_globs`` returns ``[]`` so no path is treated as
    protected; the whole staged set becomes one ``unconstrained`` batch with a
    WARN rationale, and the helper never raises.
    """
    staged_norm = [_posix(p) for p in staged if _posix(p)]
    protected_globs = load_protected_path_globs(project_root)

    if not protected_globs:
        return [
            CommitBatch(
                paths=list(staged_norm),
                kind="unconstrained",
                rationale=(
                    "WARN: protected-artifact-inventory-drift.toml missing, unreadable, "
                    "or declared no co-staged-evidence-required entries; no path treated "
                    "as protected. Staged set planned as a single unconstrained batch."
                ),
            )
        ]

    parts = partition_staged(staged_norm, protected_globs)
    protected_paths = parts["protected"]
    bridge_files = parts["bridge"]
    other_paths = parts["other"]

    citing = bridge_files_citing(protected_paths, bridge_files, project_root)

    batches: list[CommitBatch] = []
    consumed_bridge: set[str] = set()

    # 1) Protected-with-evidence and protected-missing-evidence batches.
    for protected in protected_paths:
        evidence = citing.get(protected, [])
        if evidence:
            consumed_bridge.update(evidence)
            batches.append(
                CommitBatch(
                    paths=[protected, *evidence],
                    kind="protected-with-evidence",
                    rationale=(
                        f"Protected path {protected!r} co-staged with bridge review "
                        f"evidence {evidence!r}; inventory-drift gate will accept "
                        "(review_evidence_present)."
                    ),
                    evidence=list(evidence),
                )
            )
        else:
            batches.append(
                CommitBatch(
                    paths=[protected],
                    kind="protected-missing-evidence",
                    rationale=(
                        f"Protected path {protected!r} has NO bridge evidence co-staged; "
                        "commit will be blocked by the inventory-drift gate. Stage a "
                        "bridge/*.md citing it, or bridge/INDEX.md, before committing."
                    ),
                )
            )

    # 2) Bridge-only batch for bridge files not consumed as protected evidence.
    leftover_bridge = [bf for bf in bridge_files if bf not in consumed_bridge]
    if leftover_bridge:
        batches.append(
            CommitBatch(
                paths=list(leftover_bridge),
                kind="bridge-only",
                rationale="Bridge files not tied to a staged protected path; committed on their own.",
            )
        )

    # 3) Unconstrained batch for everything else.
    if other_paths:
        batches.append(
            CommitBatch(
                paths=list(other_paths),
                kind="unconstrained",
                rationale="Non-protected, non-bridge paths; no co-staging constraint.",
            )
        )

    return batches
