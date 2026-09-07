#!/usr/bin/env python3
"""Cross-harness parity discovery-diff (Slice 3 of PROJECT-GTKB-CROSS-HARNESS-PARITY).

Discovers the *actual* hook surfaces wired on each harness (the hook arrays in
``.claude/settings.json`` and ``.codex/hooks.json``), maps each discovered
surface to a capability key, diffs the keys across the applicability-scoped
active population, and reports any **unwaived** asymmetry.

Realizes ``DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`` assertions
**PARITY-DIFF-EXISTS** (this module enumerates + diffs actual surfaces) and
**PARITY-DIFF-WIRED** (consumed by the ``_check_parity_discovery_diff`` doctor
check at WARN; the FAIL ramp + CI gate land in Slice 6). The applicability rule
(**PARITY-APPLICABILITY-RULE**) is consumed from the Slice-2 reader
(``resolve_applicability``); the typed waiver store is consumed via
``load_parity_waivers`` + ``validate_parity_waiver``.

Design contract (per ``DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY`` §3, Q5):
the registry is **not** the existence authority — the diff *discovers* existence
from the live config files. The registry supplies only the canonical
per-harness surface map (to upgrade a discovered basename to a real capability
id) and the owner-approved waiver store (to suppress legitimate asymmetry).

Slice-3 scope (per the advisory §7 risk note): the hook-surface axis only. The
diff compares harnesses that declare a hook-config file (``claude`` via
``.claude/settings.json``, ``codex`` via ``.codex/hooks.json``); cloud-shim and
inactive harnesses that declare no hook-config file are **surface-not-applicable**
(excluded by applicability, not suppressed by a waiver). Command / MCP / startup
surface classes are a Slice-6 coverage-audit expansion.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Package-qualified imports only (WI-6583). The former bare-name fallback loaded
# these modules a second time under their unqualified names, so each ``scripts/x.py``
# resolved to two distinct module objects and tripped the dual-identity guard in
# ``scripts/verify_antigravity_dispatch.py``.
from scripts.check_harness_parity import (  # noqa: E402
    build_surface_map,
    load_parity_waivers,
    load_registry,
    resolve_applicability,
    validate_parity_waiver,
)
from scripts.harness_projection_reader import load_harness_projection  # noqa: E402

# Harnesses that declare a hook-config file, and the file each declares. A
# harness participates in the hook-surface diff iff it is active AND its config
# file exists on disk. Other harnesses are surface-not-applicable for this axis.
HOOK_CONFIG_FILES: dict[str, str] = {
    "claude": ".claude/settings.json",
    "codex": ".codex/hooks.json",
}
SCOPE_NOTE = (
    "Hook-config discovery only: Claude `.claude/settings.json` and Codex `.codex/hooks.json` when present. "
    "API/provider and non-hook startup/command surfaces require phase-2 readiness or later coverage-audit evidence."
)

# The five hook event arrays both config schemas share.
HOOK_EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart", "Stop")

# Matches script/wrapper paths referenced inside a hook command string. Both
# harness schemas embed the path inside the `command` value (Claude uses
# forward-slash relative paths under `$CLAUDE_PROJECT_DIR`; Codex uses absolute
# back-slash paths and `cmd /d /s /c <wrapper>.cmd`).
_SURFACE_TOKEN_RE = re.compile(r"[A-Za-z0-9_./\\:$-]+\.(?:py|cmd)")
_BATCH_ARG_RE = re.compile(r"(?:^|\s)--batch(?:\s+|=)([A-Za-z0-9_.-]+)")


@dataclass(frozen=True)
class AsymmetryFinding:
    """One unwaived cross-harness asymmetry."""

    capability_key: str
    registered: bool
    present_on: list[str]
    absent_on: list[str]
    applicable_population: list[str]
    waived_harnesses: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DiffReport:
    overall_status: str  # "PASS" | "ASYMMETRY"
    project_root: str
    population: list[str]
    findings: list[AsymmetryFinding]
    errors: list[str] = field(default_factory=list)


def _surface_stem(token: str) -> str:
    """Normalize a discovered path token to its basename without extension.

    ``E:\\GT-KB\\.codex\\gtkb-hooks\\session_wrapup_trigger_dispatch.py`` and
    ``.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py`` both reduce to
    ``session_wrapup_trigger_dispatch``. A ``.cmd`` wrapper fronting a canonical
    ``.py`` (``workstream-focus.cmd`` ↔ ``workstream-focus.py``) reduces to the
    same stem, so the two harnesses' surfaces key together.
    """
    normalized = token.replace("\\", "/")
    return Path(normalized).stem


def _batch_surfaces(project_root: Path, batch_name: str) -> set[str]:
    """Return hook stems referenced by a Codex ``run_py_no_window`` batch.

    Codex registers one no-window wrapper per hook event and fans out to the
    actual hook scripts through the wrapper's declarative ``BATCHES`` table.
    The parity scanner reads that table as data so discovery reflects actual
    execution without requiring duplicate hook commands in ``.codex/hooks.json``.
    """
    runner = project_root / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
    try:
        tree = ast.parse(runner.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()

    for node in tree.body:
        is_batches_assign = isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "BATCHES" for target in node.targets
        )
        is_batches_annassign = (
            isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "BATCHES"
        )
        value_node = getattr(node, "value", None) if is_batches_assign or is_batches_annassign else None
        if value_node is None:
            continue
        try:
            batches = ast.literal_eval(value_node)
        except (ValueError, SyntaxError):
            return set()
        entries = batches.get(batch_name) if isinstance(batches, dict) else None
        if not isinstance(entries, tuple):
            return set()
        stems: set[str] = set()
        for entry in entries:
            if not isinstance(entry, tuple):
                continue
            for value in entry:
                if not isinstance(value, str):
                    continue
                for token in _SURFACE_TOKEN_RE.findall(value):
                    stem = _surface_stem(token)
                    if stem:
                        stems.add(stem)
        return stems
    return set()


def enumerate_hook_surfaces(config_data: dict[str, Any], *, project_root: Path | None = None) -> set[str]:
    """Return the set of hook surface stems referenced anywhere in a config.

    Parses the shared ``hooks[event] -> [ {hooks: [{command}]} ]`` structure of
    both ``.claude/settings.json`` and ``.codex/hooks.json``, extracts every
    ``.py``/``.cmd`` path token from each command, and reduces it to a stem.
    Presence is harness-level (collapsed across events): a capability "exists on
    harness X" if it appears in any of X's event arrays.
    """
    stems: set[str] = set()
    hooks = config_data.get("hooks") or {}
    for event in HOOK_EVENTS:
        for group in hooks.get(event) or []:
            if not isinstance(group, dict):
                continue
            for hook in group.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                command = str(hook.get("command") or "")
                for token in _SURFACE_TOKEN_RE.findall(command):
                    stem = _surface_stem(token)
                    if stem:
                        stems.add(stem)
                if project_root is not None:
                    for match in _BATCH_ARG_RE.finditer(command):
                        stems.update(_batch_surfaces(project_root, match.group(1)))
    return stems


def discover_surfaces_by_harness(
    project_root: Path,
    *,
    config_files: dict[str, str] | None = None,
) -> tuple[dict[str, set[str]], list[str]]:
    """Discover hook-surface stems for every harness with a present config file.

    Returns ``(surfaces_by_harness, errors)``. A harness whose config file is
    absent is simply omitted (surface-not-applicable); a malformed config file
    is recorded as an error and that harness omitted.
    """
    config_map = HOOK_CONFIG_FILES if config_files is None else config_files
    surfaces: dict[str, set[str]] = {}
    errors: list[str] = []
    for harness, rel in config_map.items():
        path = project_root / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: unreadable hook config ({exc})")
            continue
        surfaces[harness] = enumerate_hook_surfaces(data, project_root=project_root)
    return surfaces, errors


def _registered_surface_index(registry: dict[str, Any]) -> dict[tuple[str, str], str]:
    """Map ``(harness, surface_stem) -> capability id`` from the registry surface map.

    Lets a discovered ``(harness, stem)`` be upgraded from an unregistered
    ``hook:<stem>`` key to the canonical capability id when the registry
    declares that harness surface.
    """
    index: dict[tuple[str, str], str] = {}
    for cap_id, harness_surfaces in build_surface_map(registry).items():
        for harness, entry in harness_surfaces.items():
            surface = entry.get("surface")
            if not surface:
                continue
            index[(harness, _surface_stem(str(surface)))] = cap_id
    return index


def _active_harnesses(projection: dict[str, Any]) -> dict[str, list[str]]:
    """Return ``{harness_name: role_list}`` for active harnesses only (Q4: active-only)."""
    active: dict[str, list[str]] = {}
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict):
            continue
        name = record.get("harness_name")
        if not name or record.get("status") != "active":
            continue
        role = record.get("role")
        active[str(name)] = [str(r) for r in role] if isinstance(role, list) else []
    return active


def _waived(waivers: list[dict[str, Any]], capability_id: str, harness: str) -> bool:
    """True when a *valid* typed waiver covers ``(capability_id, harness)``."""
    for waiver in waivers:
        if (
            str(waiver.get("capability_id") or "") == capability_id
            and str(waiver.get("harness") or "") == harness
            and not validate_parity_waiver(waiver)
        ):
            return True
    return False


def compute_diff(
    surfaces_by_harness: dict[str, set[str]],
    registry: dict[str, Any],
    projection: dict[str, Any],
    *,
    errors: list[str] | None = None,
) -> DiffReport:
    """Diff discovered surfaces across the applicability-scoped active population.

    The hook-surface population is the set of harnesses that are active AND
    declared a discovered surface set (i.e. have a hook-config file). For each
    discovered capability key present on at least one population member, every
    other *applicable* population member must declare the surface or carry a
    valid typed waiver; otherwise the absence is an asymmetry finding.
    """
    errors = list(errors or [])
    active = _active_harnesses(projection)
    # Population = active harnesses that contributed a discovered surface set.
    population = sorted(h for h in surfaces_by_harness if h in active)

    cap_by_id: dict[str, dict[str, Any]] = {}
    raw_caps = registry.get("capabilities")
    if isinstance(raw_caps, list):
        for cap in raw_caps:
            if isinstance(cap, dict) and cap.get("id"):
                cap_by_id[str(cap["id"])] = cap
    surface_index = _registered_surface_index(registry)
    waivers = load_parity_waivers(registry)

    # Build capability-key presence: key -> {harness} (population only).
    # A discovered (harness, stem) upgrades to its registry capability id when
    # registered; otherwise keys as "hook:<stem>". Raw same-stem aliases are
    # retained only when at least one population member exposes that stem as an
    # unregistered surface. This preserves genuinely unregistered asymmetry
    # detection while avoiding false positives where another harness has the
    # same stem registered as a fallback for a broader canonical capability.
    presence: dict[str, set[str]] = {}
    key_is_registered: dict[str, bool] = {}
    key_capability_id: dict[str, str] = {}
    raw_presence: dict[str, set[str]] = {}
    raw_unregistered_keys: set[str] = set()
    for harness in population:
        for stem in surfaces_by_harness.get(harness, set()):
            raw_key = f"hook:{stem}"
            raw_presence.setdefault(raw_key, set()).add(harness)
            cap_id = surface_index.get((harness, stem))
            if cap_id is not None:
                key = cap_id
                key_is_registered[key] = True
                key_capability_id[key] = cap_id
            else:
                key = raw_key
                raw_unregistered_keys.add(raw_key)
                key_is_registered.setdefault(key, False)
            presence.setdefault(key, set()).add(harness)
    for raw_key in raw_unregistered_keys:
        presence[raw_key] = set(raw_presence.get(raw_key, set()))
        key_is_registered[raw_key] = False

    findings: list[AsymmetryFinding] = []
    for key, present_on in presence.items():
        registered = key_is_registered.get(key, False)
        # Resolve the applicable population for this capability key.
        if registered:
            capability = cap_by_id.get(key_capability_id[key], {})
            applicability = resolve_applicability(capability)
            if applicability == "role-relative":
                required = {
                    str(r).strip().lower() for r in capability.get("required_for_roles") or [] if str(r).strip()
                }
                applicable = {h for h in population if required & {role.lower() for role in active.get(h, [])}}
            else:  # universal
                applicable = set(population)
        else:
            # Unregistered hook surfaces are universal over the population.
            applicable = set(population)

        absent_on = sorted(applicable - present_on)
        if not absent_on:
            continue
        waived: list[str] = []
        unwaived: list[str] = []
        for harness in absent_on:
            if registered and _waived(waivers, key_capability_id[key], harness):
                waived.append(harness)
            else:
                unwaived.append(harness)
        if not unwaived:
            continue
        findings.append(
            AsymmetryFinding(
                capability_key=key,
                registered=registered,
                present_on=sorted(present_on),
                absent_on=unwaived,
                applicable_population=sorted(applicable),
                waived_harnesses=sorted(waived),
            )
        )

    findings.sort(key=lambda f: f.capability_key)
    status = "ASYMMETRY" if findings else "PASS"
    return DiffReport(
        overall_status=status,
        project_root=str(Path.cwd()),
        population=population,
        findings=findings,
        errors=errors,
    )


def run_discovery_diff(
    project_root: Path = PROJECT_ROOT,
    *,
    config_files: dict[str, str] | None = None,
    registry: dict[str, Any] | None = None,
    projection: dict[str, Any] | None = None,
) -> DiffReport:
    """Enumerate live harness surfaces and diff them. The doctor + tests entrypoint.

    ``registry`` / ``projection`` / ``config_files`` may be injected for tests;
    when omitted they are read from the live tree.
    """
    project_root = project_root.resolve()
    errors: list[str] = []
    if registry is None:
        try:
            registry, _ = load_registry(project_root)
        except FileNotFoundError:
            registry = {}
            errors.append("missing harness-capability registry")
        except Exception as exc:  # noqa: BLE001 - surface a malformed registry as an error row
            registry = {}
            errors.append(f"invalid harness-capability registry: {exc}")
    if projection is None:
        projection = load_harness_projection(project_root)
    surfaces, discover_errors = discover_surfaces_by_harness(project_root, config_files=config_files)
    errors.extend(discover_errors)
    report = compute_diff(surfaces, registry, projection, errors=errors)
    # Re-stamp project_root with the resolved value (compute_diff uses cwd default).
    return DiffReport(
        overall_status=report.overall_status,
        project_root=str(project_root),
        population=report.population,
        findings=report.findings,
        errors=report.errors,
    )


def format_markdown(report: DiffReport) -> str:
    lines = [
        "# Cross-Harness Parity Discovery-Diff",
        "",
        f"- Overall status: {report.overall_status}",
        f"- Project root: {report.project_root}",
        f"- Hook-surface population: {', '.join(report.population) or 'none'}",
        f"- Scope note: {SCOPE_NOTE}",
        f"- Unwaived asymmetries: {len(report.findings)}",
    ]
    if report.errors:
        lines.extend(["", "## Errors"])
        lines.extend(f"- {error}" for error in report.errors)
    if report.findings:
        lines.extend(
            [
                "",
                "## Unwaived Asymmetries",
                "",
                "| Capability key | Registered | Present on | Absent on | Applicable |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for finding in report.findings:
            lines.append(
                f"| {finding.capability_key} | {finding.registered} | "
                f"{', '.join(finding.present_on)} | {', '.join(finding.absent_on)} | "
                f"{', '.join(finding.applicable_population)} |"
            )
    else:
        lines.extend(["", "No unwaived cross-harness asymmetry in the selected scope."])
    return "\n".join(lines) + "\n"


def _json_default(value: Any) -> Any:
    if isinstance(value, DiffReport):
        payload = asdict(value)
        return payload
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown (default).")
    args = parser.parse_args(argv)

    report = run_discovery_diff(args.project_root)
    if args.json:
        print(json.dumps(report, default=_json_default, indent=2, sort_keys=True))
    else:
        print(format_markdown(report), end="")
    # Slice 3: the CLI exits non-zero on asymmetry so the Slice-6 release/CI gate
    # can adopt it directly. The *doctor* wrapper maps asymmetry to WARN (Q6 ramp).
    return 1 if report.overall_status == "ASYMMETRY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
