#!/usr/bin/env python3
"""Audit skill discoverability and effectiveness by activity.

This read-only helper maps activity-envelope skill requirements to the harness
capability registry and generated skill adapter manifests. It classifies each
active harness/activity pair with evidence so Phase 3 harness-equivalence work
can distinguish true coverage, weak evidence, typed waivers, and follow-on
gaps.

GO: bridge/gtkb-wi4965-skill-effectiveness-by-activity-002.md
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))

try:
    from groundtruth_kb.activity.profiles import ActivityProfile, load_activity_profiles
except ModuleNotFoundError:  # pragma: no cover - direct import contract is validated by tests.
    ActivityProfile = Any  # type: ignore[misc,assignment]
    load_activity_profiles = None  # type: ignore[assignment]


BRIDGE_ID = "gtkb-wi4965-skill-effectiveness-by-activity"
WORK_ITEM_ID = "WI-4965"
PROJECT_ID = "PROJECT-HARNESS-EQUIVALENCE-PHASE-3"
PAUTH_ID = "PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI4965-BATCH-C-20260705"
CAPABILITY_REGISTRY = Path("config") / "agent-control" / "harness-capability-registry.toml"
HARNESS_REGISTRY = Path("harness-state") / "harness-registry.json"
ACTIVITY_PROFILES = Path("config") / "agent-control" / "activity-disposition-profiles.toml"
REPORT_DIR = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
REPORT_NAME_PREFIX = "HARNESS-EQUIVALENCE-PHASE-3-SKILL-EFFECTIVENESS-"

STATUS_COVERED = "covered"
STATUS_WEAK = "weakly-evidenced"
STATUS_MISSING = "missing"
STATUS_NOT_APPLICABLE = "not-applicable"
STATUS_TYPED_WAIVED = "typed-waived"
VALID_STATUSES = {
    STATUS_COVERED,
    STATUS_WEAK,
    STATUS_MISSING,
    STATUS_NOT_APPLICABLE,
    STATUS_TYPED_WAIVED,
}

STRONG_SURFACE_STATUSES = {"native", "adapter"}
WEAK_SURFACE_STATUSES = {"fallback"}
WAIVED_SURFACE_STATUSES = {"unsupported", "owner-action-required"}
WAIVER_REASON_CLASSES = {"hard-limitation", "harness-surface-difference", "deliberate-deferral"}
STRONG_ENVELOPE_MODES = {"native", "adapter", "generated-adapter"}
WEAK_ENVELOPE_MODES = {"optimized-startup", "fallback", "compact-provider", "documented-limitation"}
WAIVED_ENVELOPE_MODES = {"typed-waiver"}
ACTIVITY_ALIASES = {
    "proposal": "build",
    "implementation": "build",
    "review": "test",
    "verification": "test",
    "bridge": "build",
    "bridge-reconciliation": "ops",
    "backlog": "project",
    "project-backlog": "project",
    "sot-query": "ops",
    "session-wrap": "project",
    "harness-parity": "ops",
}


@dataclass(frozen=True)
class SkillEvidence:
    skill_name: str
    capability_id: str | None
    status: str
    evidence: str
    disposition: str
    waiver_ref: str | None = None


@dataclass(frozen=True)
class ActivityRow:
    harness: str
    harness_id: str
    activity: str
    headless_eligibility: str
    status: str
    evidence: tuple[SkillEvidence, ...]
    missing_skills: tuple[str, ...]
    weak_skills: tuple[str, ...]
    typed_waivers: tuple[str, ...]
    follow_on_disposition: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = [asdict(item) for item in self.evidence]
        return payload


@dataclass(frozen=True)
class AuditReport:
    generated_at: str
    project_root: str
    bridge_id: str
    work_item_id: str
    project_id: str
    project_authorization: str
    rows: tuple[ActivityRow, ...]
    summary: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "project_root": self.project_root,
            "bridge_id": self.bridge_id,
            "work_item_id": self.work_item_id,
            "project_id": self.project_id,
            "project_authorization": self.project_authorization,
            "summary": self.summary,
            "rows": [row.as_dict() for row in self.rows],
        }


def now_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _as_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def normalize_skill_name(name: str) -> str:
    normalized = name.strip()
    aliases = {
        "open-items": "projects",
        "codex-report": "loyal-opposition-report",
        "verify": "gtkb-verify",
    }
    return aliases.get(normalized, normalized)


def capability_ids_for_skill(skill_name: str) -> tuple[str, ...]:
    normalized = normalize_skill_name(skill_name)
    candidates = {f"skill.{skill_name}", f"skill.{normalized}"}
    if normalized.startswith("gtkb-"):
        candidates.add(f"skill.{normalized.removeprefix('gtkb-')}")
    if normalized == "loyal-opposition-report":
        candidates.add("skill.codex-report")
    return tuple(sorted(candidates))


def load_active_harnesses(project_root: Path) -> tuple[dict[str, Any], ...]:
    registry = _load_json(project_root / HARNESS_REGISTRY)
    harnesses: list[dict[str, Any]] = []
    for record in registry.get("harnesses", []):
        if not isinstance(record, dict) or record.get("status") != "active":
            continue
        harness_name = str(record.get("harness_name") or "").strip().lower()
        if not harness_name:
            continue
        harnesses.append(record)
    return tuple(sorted(harnesses, key=lambda record: str(record.get("harness_name") or "")))


def load_capability_registry(project_root: Path) -> dict[str, Any]:
    return _load_toml(project_root / CAPABILITY_REGISTRY)


def _capability_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    capabilities = registry.get("capabilities", [])
    return {
        str(item.get("id")): item
        for item in capabilities
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    }


def _skill_capability_lookup(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for capability in _capability_by_id(registry).values():
        if capability.get("kind") != "skill":
            continue
        cap_id = str(capability.get("id") or "")
        canonical_name = str(capability.get("canonical_name") or "")
        canonical_source = Path(str(capability.get("canonical_source") or ""))
        keys = {cap_id, cap_id.removeprefix("skill."), canonical_name}
        if canonical_source.name == "SKILL.md":
            keys.add(canonical_source.parent.name)
        for key in keys:
            if key:
                lookup.setdefault(key, capability)
    return lookup


def _waiver_lookup(registry: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    waivers = registry.get("parity_waivers", [])
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    if not isinstance(waivers, list):
        return lookup
    for waiver in waivers:
        if not isinstance(waiver, dict):
            continue
        cap_id = str(waiver.get("capability_id") or "").strip()
        harness = str(waiver.get("harness") or "").strip().lower()
        reason_class = str(waiver.get("reason_class") or "").strip()
        owner_ref = str(waiver.get("owner_approval_ref") or "").strip()
        rationale = str(waiver.get("rationale") or "").strip()
        if not cap_id or not harness or reason_class not in WAIVER_REASON_CLASSES or not owner_ref or not rationale:
            continue
        lookup[(cap_id, harness)] = waiver
    return lookup


def _manifest_capability_ids(project_root: Path, manifest_path: str) -> set[str]:
    if not manifest_path:
        return set()
    path = project_root / manifest_path
    if not path.is_file():
        return set()
    try:
        manifest = _load_json(path)
    except json.JSONDecodeError:
        return set()
    ids: set[str] = set()
    for entry in manifest.get("adapters", []):
        if isinstance(entry, dict) and entry.get("capability_id"):
            ids.add(str(entry["capability_id"]))
    return ids


def _harness_manifest_ids(project_root: Path, registry: dict[str, Any], harness_name: str) -> set[str]:
    harnesses = registry.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return set()
    floor = harnesses.get(harness_name, {})
    if not isinstance(floor, dict):
        return set()
    manifest_path = str(floor.get("skill_adapter_manifest") or "").strip()
    return _manifest_capability_ids(project_root, manifest_path)


def _harness_floor(registry: dict[str, Any], harness_name: str) -> dict[str, Any]:
    harnesses = registry.get("harnesses", {})
    if not isinstance(harnesses, dict):
        return {}
    floor = harnesses.get(harness_name, {})
    return floor if isinstance(floor, dict) else {}


def _activity_projection_evidence(registry: dict[str, Any], harness_name: str) -> SkillEvidence | None:
    floor = _harness_floor(registry, harness_name)
    mode = str(floor.get("activity_envelope_projection_mode") or "").strip()
    if not mode:
        return None
    manifest = str(floor.get("activity_envelope_manifest_source") or ACTIVITY_PROFILES.as_posix())
    limitations = str(floor.get("result_envelope_limitations") or "").strip()
    evidence = f"config/agent-control/harness-capability-registry.toml::[harnesses.{harness_name}]"
    if mode in STRONG_ENVELOPE_MODES:
        status = STATUS_COVERED
        disposition = f"Activity-envelope mode `{mode}` references `{manifest}`."
    elif mode in WEAK_ENVELOPE_MODES:
        status = STATUS_WEAK
        disposition = f"Activity-envelope mode `{mode}` requires compact/fallback evidence. {limitations}".strip()
    elif mode in WAIVED_ENVELOPE_MODES:
        status = STATUS_TYPED_WAIVED
        disposition = f"Activity-envelope mode `{mode}` is explicitly waived. {limitations}".strip()
    else:
        status = STATUS_MISSING
        disposition = f"Unknown activity-envelope projection mode `{mode}`; update registry evidence."
    return SkillEvidence(
        skill_name="activity-envelope-projection",
        capability_id="activity-envelope.projection-mode",
        status=status,
        evidence=evidence,
        disposition=disposition,
    )


def _surface_exists(project_root: Path, surface: str) -> bool:
    return bool(surface and (project_root / surface).is_file())


def _resolve_skill_capability(
    skill_name: str,
    skill_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    for candidate in capability_ids_for_skill(skill_name):
        if candidate in skill_lookup:
            return skill_lookup[candidate]
    return skill_lookup.get(normalize_skill_name(skill_name))


def _skill_evidence(
    project_root: Path,
    *,
    skill_name: str,
    capability: dict[str, Any] | None,
    harness_name: str,
    manifest_ids: set[str],
    waivers: dict[tuple[str, str], dict[str, Any]],
) -> SkillEvidence:
    if capability is None:
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=None,
            status=STATUS_MISSING,
            evidence="no matching skill capability in harness capability registry",
            disposition="Follow-on: register this activity skill or update the activity profile to the canonical skill name.",
        )

    cap_id = str(capability.get("id") or "")
    harness_surface = capability.get(harness_name)
    if not isinstance(harness_surface, dict) and cap_id in manifest_ids:
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=cap_id,
            status=STATUS_COVERED,
            evidence="generated skill manifest",
            disposition="No new work; generated skill adapter manifest exposes this skill.",
        )

    if not isinstance(harness_surface, dict):
        waiver = waivers.get((cap_id, harness_name))
        if waiver:
            return _waived_skill_evidence(skill_name, cap_id, waiver)
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=cap_id,
            status=STATUS_MISSING,
            evidence="registry lacks harness-specific skill surface",
            disposition="Follow-on: add a harness skill surface, manifest projection, or typed waiver.",
        )

    configured_status = str(harness_surface.get("status") or "").strip().lower()
    surface = str(harness_surface.get("surface") or "").strip()
    waiver = waivers.get((cap_id, harness_name))

    if configured_status in STRONG_SURFACE_STATUSES and _surface_exists(project_root, surface):
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=cap_id,
            status=STATUS_COVERED,
            evidence=surface,
            disposition="No new work; discoverable skill surface exists.",
        )
    if configured_status in WEAK_SURFACE_STATUSES and _surface_exists(project_root, surface):
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=cap_id,
            status=STATUS_WEAK,
            evidence=surface,
            disposition=str(
                harness_surface.get("fallback") or "Fallback surface exists; runtime use still needs evidence."
            ),
        )
    if configured_status in WAIVED_SURFACE_STATUSES:
        if waiver:
            return _waived_skill_evidence(skill_name, cap_id, waiver)
        return SkillEvidence(
            skill_name=skill_name,
            capability_id=cap_id,
            status=STATUS_NOT_APPLICABLE,
            evidence=f"registry status: {configured_status}",
            disposition=str(harness_surface.get("reason") or "Registered as unsupported for this harness."),
        )
    if waiver:
        return _waived_skill_evidence(skill_name, cap_id, waiver)
    return SkillEvidence(
        skill_name=skill_name,
        capability_id=cap_id,
        status=STATUS_MISSING,
        evidence=surface or "no surface declared",
        disposition="Follow-on: repair missing or stale skill surface evidence.",
    )


def _waived_skill_evidence(skill_name: str, cap_id: str, waiver: dict[str, Any]) -> SkillEvidence:
    owner_ref = str(waiver.get("owner_approval_ref") or "").strip()
    reason_class = str(waiver.get("reason_class") or "").strip()
    rationale = str(waiver.get("rationale") or "").strip()
    return SkillEvidence(
        skill_name=skill_name,
        capability_id=cap_id,
        status=STATUS_TYPED_WAIVED,
        evidence=owner_ref,
        disposition=f"Typed waiver ({reason_class}): {rationale}",
        waiver_ref=owner_ref,
    )


def _row_status(evidence: tuple[SkillEvidence, ...]) -> str:
    statuses = {item.status for item in evidence}
    if STATUS_MISSING in statuses:
        return STATUS_MISSING
    if STATUS_WEAK in statuses:
        return STATUS_WEAK
    if statuses and statuses <= {STATUS_TYPED_WAIVED, STATUS_NOT_APPLICABLE}:
        return STATUS_TYPED_WAIVED if STATUS_TYPED_WAIVED in statuses else STATUS_NOT_APPLICABLE
    if STATUS_TYPED_WAIVED in statuses:
        return STATUS_WEAK
    return STATUS_COVERED


def _row_disposition(status: str, evidence: tuple[SkillEvidence, ...]) -> str:
    if status == STATUS_COVERED:
        return "No new work; all activity skills are discoverable for this harness."
    if status == STATUS_WEAK:
        return (
            "Follow-on: strengthen fallback or typed-waiver evidence before treating this activity as fully equivalent."
        )
    if status == STATUS_TYPED_WAIVED:
        return "No implementation in this slice; typed waivers explain each non-equivalent skill surface."
    if status == STATUS_NOT_APPLICABLE:
        return "No implementation in this slice; registered harness status marks the skill surface not applicable."
    missing = [item.skill_name for item in evidence if item.status == STATUS_MISSING]
    return f"Follow-on: add skill projection evidence or typed waivers for {', '.join(missing)}."


def evaluate(project_root: Path = PROJECT_ROOT, *, generated_at: str | None = None) -> AuditReport:
    project_root = project_root.resolve()
    if load_activity_profiles is None:
        raise RuntimeError("groundtruth_kb.activity.profiles is not importable")

    profiles: dict[str, ActivityProfile] = load_activity_profiles(project_root / ACTIVITY_PROFILES)
    capability_registry = load_capability_registry(project_root)
    skill_lookup = _skill_capability_lookup(capability_registry)
    waivers = _waiver_lookup(capability_registry)
    rows: list[ActivityRow] = []

    for harness in load_active_harnesses(project_root):
        harness_name = str(harness.get("harness_name") or "").strip().lower()
        harness_id = str(harness.get("id") or "")
        manifest_ids = _harness_manifest_ids(project_root, capability_registry, harness_name)
        projection_evidence = _activity_projection_evidence(capability_registry, harness_name)
        for activity_name in sorted(profiles):
            profile = profiles[activity_name]
            skill_evidence = tuple(
                _skill_evidence(
                    project_root,
                    skill_name=skill_name,
                    capability=_resolve_skill_capability(skill_name, skill_lookup),
                    harness_name=harness_name,
                    manifest_ids=manifest_ids,
                    waivers=waivers,
                )
                for skill_name in profile.skills
            )
            evidence = skill_evidence + ((projection_evidence,) if projection_evidence else ())
            status = _row_status(evidence)
            rows.append(
                ActivityRow(
                    harness=harness_name,
                    harness_id=harness_id,
                    activity=activity_name,
                    headless_eligibility=profile.headless_eligibility,
                    status=status,
                    evidence=evidence,
                    missing_skills=tuple(item.skill_name for item in skill_evidence if item.status == STATUS_MISSING),
                    weak_skills=tuple(item.skill_name for item in skill_evidence if item.status == STATUS_WEAK),
                    typed_waivers=tuple(
                        item.waiver_ref or item.skill_name
                        for item in skill_evidence
                        if item.status == STATUS_TYPED_WAIVED
                    ),
                    follow_on_disposition=_row_disposition(status, evidence),
                )
            )

    summary = Counter(row.status for row in rows)
    for status in sorted(VALID_STATUSES):
        summary.setdefault(status, 0)
    return AuditReport(
        generated_at=generated_at or now_stamp(),
        project_root=str(project_root),
        bridge_id=BRIDGE_ID,
        work_item_id=WORK_ITEM_ID,
        project_id=PROJECT_ID,
        project_authorization=PAUTH_ID,
        rows=tuple(rows),
        summary={status: summary[status] for status in sorted(summary) if summary[status]},
    )


def render_markdown_report(report: AuditReport) -> str:
    lines = [
        "# Harness Equivalence Phase 3 Skill Effectiveness Audit",
        "",
        f"Generated: `{report.generated_at}`",
        f"Bridge: `{report.bridge_id}`",
        f"Project: `{report.project_id}`",
        f"Work Item: `{report.work_item_id}`",
        f"Project Authorization: `{report.project_authorization}`",
        "",
        "This read-only audit maps activity-envelope skill requirements to each active harness's skill projection evidence.",
        "",
        "## Summary",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(report.summary.items()):
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## Activity Matrix",
            "",
            "| Harness | Activity | Eligibility | Status | Skills | Evidence | Follow-on disposition |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.rows:
        skills = ", ".join(f"`{item.skill_name}`:{item.status}" for item in row.evidence)
        evidence = "<br>".join(_escape_table(f"{item.skill_name}: {item.evidence}") for item in row.evidence)
        lines.append(
            "| "
            f"`{row.harness}` (`{row.harness_id}`) | "
            f"`{row.activity}` | "
            f"`{row.headless_eligibility}` | "
            f"`{row.status}` | "
            f"{_escape_table(skills)} | "
            f"{evidence} | "
            f"{_escape_table(row.follow_on_disposition)} |"
        )

    missing_rows = [row for row in report.rows if row.status == STATUS_MISSING]
    weak_rows = [row for row in report.rows if row.status == STATUS_WEAK]
    waived_rows = [row for row in report.rows if row.typed_waivers]

    if missing_rows:
        lines.extend(["", "## Gaps"])
        for row in missing_rows:
            lines.extend(
                [
                    "",
                    f"### `{row.harness}` / `{row.activity}`",
                    "",
                    f"- Missing skills: {', '.join(f'`{skill}`' for skill in row.missing_skills)}",
                    f"- Follow-on disposition: {row.follow_on_disposition}",
                ]
            )

    if weak_rows:
        lines.extend(["", "## Weak Evidence"])
        for row in weak_rows:
            weak = tuple(item.skill_name for item in row.evidence if item.status in {STATUS_WEAK, STATUS_TYPED_WAIVED})
            lines.append(f"- `{row.harness}` / `{row.activity}`: {', '.join(f'`{skill}`' for skill in weak)}")

    if waived_rows:
        lines.extend(["", "## Typed Waivers"])
        seen: set[tuple[str, str]] = set()
        for row in waived_rows:
            for item in row.evidence:
                if item.status != STATUS_TYPED_WAIVED:
                    continue
                key = (item.capability_id or item.skill_name, item.waiver_ref or "")
                if key in seen:
                    continue
                seen.add(key)
                lines.append(f"- `{row.harness}` `{item.skill_name}`: {item.disposition} Evidence: `{item.evidence}`.")

    lines.extend(
        [
            "",
            "## Verification Notes",
            "",
            "- `covered` means the harness has a native or generated adapter skill surface for every skill in the activity profile.",
            "- `weakly-evidenced` means the activity depends on at least one fallback surface or typed waiver and should not be treated as full semantic equivalence without follow-on evidence.",
            "- `missing` means the activity has at least one required skill with no registry, manifest, or typed-waiver evidence.",
            "- This helper does not mutate harness skills, capability registry entries, MemBase, bridge state, dispatcher state, or generated runtime state.",
        ]
    )
    return "\n".join(lines) + "\n"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|")


def write_report(markdown: str, path: Path, *, project_root: Path = PROJECT_ROOT) -> Path:
    project_root = project_root.resolve()
    resolved = path.resolve()
    expected_dir = (project_root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX").resolve()
    if resolved.parent != expected_dir:
        raise ValueError("report path must be inside independent-progress-assessments/CODEX-INSIGHT-DROPBOX")
    if not resolved.name.startswith(REPORT_NAME_PREFIX) or resolved.suffix != ".md":
        raise ValueError(f"report filename must start with {REPORT_NAME_PREFIX!r} and end with .md")
    expected_dir.mkdir(parents=True, exist_ok=True)
    resolved.write_text(markdown, encoding="utf-8", newline="\n")
    return resolved


def _json_default(value: Any) -> Any:
    if isinstance(value, AuditReport):
        return value.as_dict()
    if isinstance(value, ActivityRow):
        return value.as_dict()
    if isinstance(value, SkillEvidence):
        return asdict(value)
    raise TypeError(f"{type(value).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit structured JSON instead of markdown.")
    parser.add_argument("--write-report", action="store_true", help="Write the markdown report to the insight dropbox.")
    parser.add_argument("--output", type=Path, help="Explicit report path. Must stay under CODEX-INSIGHT-DROPBOX.")
    args = parser.parse_args(argv)

    report = evaluate(args.project_root)
    if args.json:
        print(json.dumps(report, default=_json_default, indent=2, sort_keys=True))
        return 0

    markdown = render_markdown_report(report)
    if args.write_report:
        output = args.output
        if output is None:
            output = REPORT_DIR / f"{REPORT_NAME_PREFIX}{report.generated_at}.md"
        written = write_report(markdown, output, project_root=args.project_root)
        print(_rel(args.project_root, written))
        return 0

    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
