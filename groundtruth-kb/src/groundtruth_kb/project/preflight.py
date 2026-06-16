# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Upgrade pre-flight checks — Area 5 (bridge ``gtkb-upgrade-pre-flight-checks``).

Implements the three Area-5 pre-flight checks scoped in
``bridge/gtkb-upgrade-pre-flight-checks-001.md`` and GO'd at ``-002`` / the
implementation bridge at ``-implementation-002``:

- **5.2 — Bridge in-flight awareness.** Scans status-bearing numbered bridge
  files whose latest status is non-terminal
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

_VERSIONED_BRIDGE_FILE_RE = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
_STATUS_TOKEN_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|ACCEPTED|BLOCKED)\b",
    re.IGNORECASE,
)

# Non-terminal statuses: a document whose top line is one of these is still
# in an active review cycle. VERIFIED/NO-GO are terminal and DEFERRED is parked,
# so all three are silent for this preflight.
_NON_TERMINAL_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "GO", "ADVISORY"})


def _check_bridge_inflight(target: Path, *, ignore: bool = False) -> list[UpgradeAction]:
    """Scan numbered bridge files for un-terminated bridge threads.

    Silent when ``ignore=True`` (adopter opted out via
    ``--ignore-inflight-bridges``) or when no bridge directory exists
    (non-bridge projects).

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

    bridge_dir = target / "bridge"
    if not bridge_dir.is_dir():
        return []

    latest: dict[str, tuple[int, str]] = {}
    for path in bridge_dir.glob("*.md"):
        name_match = _VERSIONED_BRIDGE_FILE_RE.match(path.name)
        if name_match is None:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        status: str | None = None
        for raw in lines:
            stripped = raw.strip()
            if not stripped:
                continue
            status_match = _STATUS_TOKEN_RE.match(stripped)
            status = status_match.group(1).upper() if status_match else None
            break
        if status is None:
            continue
        slug = name_match.group("slug")
        version = int(name_match.group("version"))
        prior = latest.get(slug)
        if prior is None or version > prior[0]:
            latest[slug] = (version, status)

    warnings: list[UpgradeAction] = []
    for current_doc, (_version, status) in latest.items():
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


def _check_isolation_state(target: Path, profile_name: str, product_root: Path | None = None) -> list[UpgradeAction]:
    """Slice 4: surface isolation-doctor failures as non-mutating diagnostic rows.

    Per bridge ``gtkb-isolation-017-slice4-upgrade-2026-05-02-007.md`` §"In-scope"
    and `-008` GO. Each failing isolation check (``status in {"fail", "warning"}``)
    produces one ``warning`` UpgradeAction row prefixed ``[ISOLATION]`` so dry-run
    output surfaces the gap. The CLI filters ``warning``/``informational`` rows
    out of the list passed to ``execute_upgrade`` so these never trigger git or
    file mutation. The actual gating + auto-fix invocation happens in
    ``execute_upgrade`` via ``_run_isolation_preflight`` + ``_run_isolation_fixers``.

    Args:
        target: Adopter project root.
        profile_name: Profile (e.g., ``"dual-agent"``) for ``run_isolation_checks``.
        product_root: GT-KB product root. Defaults to
            ``Path(__file__).resolve().parents[3]`` (matches ``doctor.py``).
    """
    from groundtruth_kb.project.doctor_isolation import run_isolation_checks

    if product_root is None:
        product_root = Path(__file__).resolve().parents[3]

    rows: list[UpgradeAction] = []
    try:
        checks = run_isolation_checks(target, profile_name, product_root=product_root)
    except Exception as exc:  # noqa: BLE001  # intentional-catch: graceful degradation; surface as info
        return [
            UpgradeAction(
                file="<isolation-preflight>",
                action="informational",
                reason=f"Isolation pre-flight skipped (exception: {exc}); execute_upgrade gating still applies.",
            )
        ]

    failing = [c for c in checks if c.status in ("fail", "warning")]
    if not failing:
        return [
            UpgradeAction(
                file="<isolation-preflight>",
                action="informational",
                reason="Isolation: all 9 checks pass.",
            )
        ]

    for check in failing:
        rows.append(
            UpgradeAction(
                file=f"<{check.name}>",
                action="warning",
                reason=f"[ISOLATION] {check.name}: {check.message}",
            )
        )
    return rows
