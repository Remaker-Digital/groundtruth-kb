"""Deterministic sweep-commit batch planning for protected hook-config edits.

WI-4528 (P3, ``tooling``, origin=improvement). The inventory-drift gate
(``scripts/check_dev_environment_inventory_drift.py``, run by
``.githooks/pre-commit --staged --allow-review-evidence``) accepts a protected
hook-config change such as ``.codex/hooks.json`` only when a numbered bridge
evidence file is CO-STAGED in the same commit (``review_evidence_present``).
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

from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

__all__ = [
    "CommitBatch",
    "INVENTORY_DRIFT_TOML_RELATIVE_PATH",
    "BRIDGE_EVIDENCE_PATTERNS",
    "NONTERMINAL_BRIDGE_STATUSES",
    "load_protected_path_globs",
    "is_protected_path",
    "is_bridge_evidence_path",
    "partition_staged",
    "bridge_files_citing",
    "unverified_bridge_evidence_threads_citing",
    "active_nonterminal_bridge_threads_citing",
    "plan_commit_batches",
]

# Authoritative protected-paths config consumed by the inventory-drift gate.
INVENTORY_DRIFT_TOML_RELATIVE_PATH = Path("config/governance/protected-artifact-inventory-drift.toml")

# Bridge review-evidence patterns, byte-identical to BRIDGE_REVIEW_EVIDENCE_PATTERNS
# in scripts/check_dev_environment_inventory_drift.py. A staged path matching any
# of these satisfies the gate's review_evidence_present condition.
BRIDGE_EVIDENCE_PATTERNS = ("bridge/*-[0-9][0-9][0-9].md",)
NONTERMINAL_BRIDGE_STATUSES = frozenset({"NEW", "REVISED", "GO", "NO-GO"})


@dataclass(frozen=True)
class CommitBatch:
    """One planned commit: a set of paths committed together, with rationale.

    ``kind`` is one of:
      - ``"protected-with-evidence"``: protected hook-config path(s) grouped with
        at least one co-staged bridge-evidence file (the gate-friendly batch).
      - ``"protected-missing-evidence"``: protected path(s) with NO co-stageable
        bridge evidence in the staged set; committing this batch will be blocked
        by the inventory-drift gate. The ``rationale`` flags the diagnostic.
      - ``"protected-unverified-thread"``: protected path(s) whose co-staged
        bridge evidence belongs to a thread that is not at ``VERIFIED`` or whose
        status cannot be read; committing would bypass finalization.
      - ``"protected-active-thread-nonterminal"``: protected path(s) cited by a
        live non-terminal bridge thread; committing before VERIFIED would bypass
        the bridge commit-finalization gate.
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


def _body_cites_protected_path(body: str, protected_path: str) -> bool:
    """Return True when ``body`` mentions the protected path or its basename."""
    norm_protected = _posix(protected_path)
    protected_basename = Path(norm_protected).name
    return norm_protected in body or protected_basename in body


def partition_staged(paths: list[str], protected_globs: list[str]) -> dict[str, list[str]]:
    """Split staged paths into ``protected`` / ``bridge`` / ``other`` buckets.

    Pure, no I/O. ``bridge`` includes candidate numbered review-evidence files.
    A path that is both bridge-shaped and protected (none exist in the current
    registry, but defensively) is classified as ``protected`` first.
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

    Bridge files that cannot be read are skipped (fail-soft); a protected path
    with no citing bridge file maps to an empty list (the missing-evidence case).
    """
    root = Path(project_root)

    # Pre-read bridge file bodies once.
    bodies: dict[str, str] = {}
    for bridge_file in staged_bridge_files:
        try:
            bodies[bridge_file] = (root / bridge_file).read_text(encoding="utf-8", errors="replace")
        except (FileNotFoundError, OSError):
            continue

    citing: dict[str, list[str]] = {}
    for protected in staged_protected:
        norm_protected = _posix(protected)
        matches: list[str] = []
        for bridge_file, body in bodies.items():
            if _body_cites_protected_path(body, norm_protected):
                matches.append(bridge_file)
        citing[norm_protected] = matches
    return citing


def _bridge_slug_from_evidence_path(path: str) -> str | None:
    """Return the bridge thread slug for ``bridge/<slug>-NNN.md`` evidence paths."""
    candidate = _posix(path)
    if not is_bridge_evidence_path(candidate):
        return None
    name = Path(candidate).name
    stem = name.removesuffix(".md")
    slug, sep, version = stem.rpartition("-")
    if sep != "-" or not slug or not version.isdigit():
        return None
    return slug


def unverified_bridge_evidence_threads_citing(
    protected_to_evidence: dict[str, list[str]],
    project_root: Path | str,
) -> dict[str, list[str]]:
    """Map protected paths to co-staged evidence threads that are not VERIFIED.

    ``protected-with-evidence`` is commit-safe only when the citing bridge
    evidence belongs to a thread whose latest status token is ``VERIFIED``. If
    the thread cannot be resolved or its status cannot be read, the evidence is
    treated conservatively as unverified so sweep planning withholds the
    protected path instead of front-running the finalization gate.
    """
    root = Path(project_root)
    result: dict[str, list[str]] = {protected: [] for protected in protected_to_evidence}

    try:
        expected_documents = scan_expected_documents(root)
    except OSError:
        for protected, evidence_files in protected_to_evidence.items():
            result[protected] = [f"{evidence}@unreadable" for evidence in evidence_files]
        return result

    for protected, evidence_files in protected_to_evidence.items():
        for evidence in evidence_files:
            slug = _bridge_slug_from_evidence_path(evidence)
            if slug is None:
                result[protected].append(f"{evidence}@unresolved")
                continue

            document = expected_documents.get(slug)
            if document is not None and document.files:
                latest_path = root / document.files[-1]
                status = status_from_bridge_file(latest_path)
            else:
                status = status_from_bridge_file(root / evidence)

            if status != "VERIFIED":
                result[protected].append(f"{slug}@{status or 'unreadable'}")

    return result


def active_nonterminal_bridge_threads_citing(
    staged_protected: list[str],
    project_root: Path | str,
) -> dict[str, list[str]]:
    """Map protected paths to active non-terminal bridge threads that cite them.

    The live bridge thread status is the latest versioned bridge file's canonical
    status token. Threads at ``VERIFIED`` or another terminal token do not gate
    commit planning. Any bridge scan/read problem fails soft and returns no
    active-thread matches, preserving the helper's planning-only contract.
    """
    protected_norm = [_posix(path) for path in staged_protected]
    empty = {path: [] for path in protected_norm}
    if not protected_norm:
        return empty

    root = Path(project_root)
    try:
        expected_documents = scan_expected_documents(root)
    except OSError:
        return empty

    citing: dict[str, list[str]] = {path: [] for path in protected_norm}
    for slug, document in sorted(expected_documents.items()):
        if not document.files:
            continue

        latest_path = root / document.files[-1]
        status = status_from_bridge_file(latest_path)
        if status not in NONTERMINAL_BRIDGE_STATUSES:
            continue

        try:
            bodies = [
                (root / bridge_file).read_text(encoding="utf-8", errors="replace") for bridge_file in document.files
            ]
        except (FileNotFoundError, OSError):
            return empty

        for protected in protected_norm:
            if any(_body_cites_protected_path(body, protected) for body in bodies):
                citing[protected].append(f"{slug}@{status}")

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
      - a protected path whose co-staged bridge evidence resolves to anything
        other than latest ``VERIFIED`` is surfaced in a held
        ``protected-unverified-thread`` batch;
      - a protected path cited by a live non-terminal bridge thread is surfaced
        in a held ``protected-active-thread-nonterminal`` batch before evidence
        co-staging is considered, so sweep automation cannot commit ahead of
        VERIFIED;
      - bridge-only files not tied to a protected path get their own
        ``bridge-only`` batch (preserving the existing swarm bridge-filing
        pattern);
      - other files get an ``unconstrained`` batch.

    Order: staged unverified-evidence holds first, then active non-terminal
    holds, protected-with-evidence, protected-missing-evidence, bridge-only, and
    unconstrained.

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
    unverified_evidence_threads = unverified_bridge_evidence_threads_citing(citing, project_root)
    active_threads = active_nonterminal_bridge_threads_citing(protected_paths, project_root)

    batches: list[CommitBatch] = []
    consumed_bridge: set[str] = set()

    # 1) Protected unverified-thread holds, active-thread holds, protected-with-evidence,
    # and missing-evidence batches.
    for protected in protected_paths:
        unverified_threads = unverified_evidence_threads.get(protected, [])
        if unverified_threads:
            evidence = citing.get(protected, [])
            batches.append(
                CommitBatch(
                    paths=[protected],
                    kind="protected-unverified-thread",
                    rationale=(
                        f"Protected path {protected!r} has co-staged bridge evidence "
                        f"{evidence!r}, but citing thread(s) {unverified_threads!r} "
                        "are not VERIFIED; exclude the protected path from sweep "
                        "until the bridge thread reaches VERIFIED."
                    ),
                    evidence=list(evidence),
                )
            )
            continue

        nonterminal_threads = active_threads.get(protected, [])
        if nonterminal_threads:
            batches.append(
                CommitBatch(
                    paths=[protected],
                    kind="protected-active-thread-nonterminal",
                    rationale=(
                        f"Protected path {protected!r} is cited by active non-terminal "
                        f"bridge thread(s) {nonterminal_threads!r}; hold until the "
                        "thread reaches VERIFIED before commit finalization."
                    ),
                )
            )
            continue

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
                        "numbered bridge evidence file citing it before committing."
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
