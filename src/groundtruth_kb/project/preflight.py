# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Upgrade pre-flight checks — Area 5 (bridge ``gtkb-upgrade-pre-flight-checks``).

Implements the three Area-5 pre-flight checks scoped in
``bridge/gtkb-upgrade-pre-flight-checks-001.md`` and GO'd at ``-002`` / the
implementation bridge at ``-implementation-002``:

- **5.2 — Bridge in-flight awareness.** Scans ``bridge/INDEX.md`` for
  ``Document:`` entries whose latest (top) status line is non-terminal
  (``NEW``, ``REVISED``, or ``GO``). Emits one ``warning`` action per
  affected document. Silent when the latest status is ``VERIFIED`` or
  ``NO-GO``, regardless of what older lines say further down the entry
  (per C3).
- **5.3 — Malformed settings halt.** Inherited from
  ``plan_upgrade``'s existing malformed-JSON ``skip`` emission; the halt
  itself lives in :class:`groundtruth_kb.project.upgrade.MalformedSettingsError`
  and fires in ``execute_upgrade`` before any git or file work (C2).
- **5.6 — Scaffold coverage delta.** Reports paths the scaffold creates
  for the adopter's profile but the managed-artifact registry does not
  cover, so ``gt project upgrade`` cannot repair them. Uses the pure
  :func:`groundtruth_kb.project.scaffold.enumerate_scaffold_outputs`
  enumerator (C4) — never invokes ``scaffold_project`` against the
  adopter target.

All checks are read-only. Output is a list of non-mutating
:class:`~groundtruth_kb.project.upgrade.UpgradeAction` rows
(``action`` in ``"warning"`` / ``"informational"``); the CLI filters
these out of the list passed to ``execute_upgrade`` so apply behavior is
structurally unaffected (C1).

Authorizing chain:
- ``bridge/gtkb-upgrade-pre-flight-checks-002.md`` (scope GO + 5 conditions)
- ``bridge/gtkb-upgrade-pre-flight-checks-implementation-002.md`` (impl GO)
"""

from __future__ import annotations

import re
from pathlib import Path

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    GitignorePattern,
    SettingsHookRegistration,
    artifacts_for_upgrade,
)
from groundtruth_kb.project.manifest import read_manifest
from groundtruth_kb.project.scaffold import enumerate_scaffold_outputs
from groundtruth_kb.project.upgrade import UpgradeAction

# ---------------------------------------------------------------------------
# 5.2 — Bridge in-flight awareness
# ---------------------------------------------------------------------------

_DOCUMENT_HEADER_RE = re.compile(r"^Document:\s+(\S+)\s*$")
_STATUS_LINE_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s*bridge/")

# Non-terminal statuses: a document whose top line is one of these is still
# in an active review cycle. VERIFIED and NO-GO are terminal and silent.
_NON_TERMINAL_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "GO"})


def _check_bridge_inflight(target: Path, *, ignore: bool = False) -> list[UpgradeAction]:
    """Scan ``bridge/INDEX.md`` for un-terminated ``Document:`` entries.

    Parses by ``Document:`` block and inspects **only** the first status
    line after each block header. HTML comments (``<!-- ... -->``), blank
    lines, and narrative text between ``Document:`` blocks are skipped;
    they neither set nor clear the "waiting for first status" state.

    Silent when ``ignore=True`` (adopter opted out via
    ``--ignore-inflight-bridges``) or when ``bridge/INDEX.md`` does not
    exist (non-bridge projects).

    Per bridge ``gtkb-upgrade-pre-flight-checks-implementation-002.md`` C3.

    Args:
        target: Adopter project root.
        ignore: When True, skip the check entirely and return an empty
            list. Used by automation and CI that cannot be paused by
            in-flight bridge activity.

    Returns:
        One ``UpgradeAction(action="warning", ...)`` per document whose
        latest (top-of-block) status line is in
        :data:`_NON_TERMINAL_STATUSES`. Sorted deterministically by
        document name.
    """
    if ignore:
        return []

    index_path = target / "bridge" / "INDEX.md"
    if not index_path.exists():
        return []

    try:
        content = index_path.read_text(encoding="utf-8")
    except OSError:
        return []

    warnings: list[UpgradeAction] = []
    current_doc: str | None = None

    for raw_line in content.splitlines():
        line = raw_line.rstrip()

        doc_match = _DOCUMENT_HEADER_RE.match(line)
        if doc_match is not None:
            # A new ``Document:`` header resets our search regardless of
            # whether the previous block ever produced a status line.
            current_doc = doc_match.group(1)
            continue

        if current_doc is None:
            continue

        # HTML comments and blank lines are transparent — they neither
        # produce a status nor close the current document's search.
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue

        status_match = _STATUS_LINE_RE.match(line)
        if status_match is None:
            # Some other non-status content (table row, header text);
            # keep scanning for the real status line within this block.
            continue

        status = status_match.group(1)
        if status in _NON_TERMINAL_STATUSES:
            warnings.append(
                UpgradeAction(
                    file=f"bridge/{current_doc}",
                    action="warning",
                    reason=(
                        f"In-flight bridge: latest status is {status}. "
                        "Consider deferring upgrade until the thread is VERIFIED."
                    ),
                )
            )
        # Latest status seen — stop scanning this document (older status
        # lines below must not produce additional warnings; per C3).
        current_doc = None

    warnings.sort(key=lambda a: a.file)
    return warnings


# ---------------------------------------------------------------------------
# 5.6 — Scaffold coverage delta
# ---------------------------------------------------------------------------


def _managed_target_paths(profile_name: str) -> set[str]:
    """Return the set of target paths the managed-artifact registry covers for *profile_name*.

    File artifacts contribute their ``target_path`` directly.
    ``settings-hook-registration`` rows fold into ``.claude/settings.json``
    (the single file that hosts every registration), and
    ``gitignore-pattern`` rows fold into ``.gitignore``. This keeps the
    coverage check from false-positively flagging those two paths as
    uncovered when registry rows of non-file classes manage them.
    """
    managed: set[str] = set()
    for artifact in artifacts_for_upgrade(profile_name):
        if isinstance(artifact, FileArtifact):
            managed.add(artifact.target_path)
        elif isinstance(artifact, SettingsHookRegistration):
            managed.add(".claude/settings.json")
        elif isinstance(artifact, GitignorePattern):
            managed.add(".gitignore")
    return managed


def _check_scaffold_coverage(target: Path, profile_name: str) -> list[UpgradeAction]:
    """Report scaffold-created paths the managed registry cannot repair.

    Calls :func:`groundtruth_kb.project.scaffold.enumerate_scaffold_outputs`
    (pure, no writes) and subtracts the managed-artifact registry's covered
    paths. Each remaining path produces one ``informational`` action so
    the adopter sees — without alarm — the surface where manual repair is
    required if the scaffold-written file is deleted.

    Option-dependent paths (CI workflows, seed example, integrations,
    spec scaffold) are deliberately excluded by the enumerator to avoid
    false positives for projects initialized with non-default options.
    Per C4 of the implementation bridge.

    Args:
        target: Adopter project root. Read-only here; used only to
            resolve the manifest for ``cloud_provider`` context.
        profile_name: The adopter's profile (from manifest).

    Returns:
        Sorted list of ``UpgradeAction(action="informational", ...)`` rows,
        one per uncovered path.
    """
    manifest = read_manifest(target / "groundtruth.toml")
    cloud_provider = manifest.cloud_provider if manifest else "none"

    try:
        scaffold_paths = set(enumerate_scaffold_outputs(profile_name, cloud_provider=cloud_provider))
    except ValueError:
        # Unknown / unregistered profile — surface as a single info row
        # rather than crash the plan. Gives the adopter a clue to repair
        # the manifest rather than an opaque traceback.
        return [
            UpgradeAction(
                file="groundtruth.toml",
                action="informational",
                reason=f"Scaffold coverage skipped: unknown profile {profile_name!r} in manifest.",
            )
        ]

    managed = _managed_target_paths(profile_name)
    uncovered = sorted(scaffold_paths - managed)

    return [
        UpgradeAction(
            file=path,
            action="informational",
            reason=("Created by gt project init for this profile; upgrade cannot repair or update it if deleted."),
        )
        for path in uncovered
    ]
