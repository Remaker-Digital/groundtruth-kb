"""Build WI-4968 harness envelope-equivalence evidence.

The helper is read-only by default. It compares current harness registry
projection data, active typed waivers, and observed per-harness session-envelope
files against the retired WI-4950 baseline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASELINE_WORK_ITEM = "WI-4950"
BASELINE_TITLE = "Add cross-harness activity-envelope projection and result-envelope parity"
EVIDENCE_ID = "harness_envelope_equivalence"

ENVELOPE_FIELDS = {
    "activity": "activity_envelope_projection_mode",
    "result": "compact_result_envelope_mode",
    "session": "compact_session_envelope_mode",
}

VALID_MODES = {"native", "optimized-startup", "fallback", "compact-provider"}
LIMITED_MODES = {"optimized-startup", "fallback", "compact-provider"}
PROVIDER_LIMITED_MODES = {"compact-provider"}

STATUS_EQUIVALENT = "equivalent"
STATUS_LIMITED = "equivalent-with-limits"
STATUS_WAIVED = "typed-waived"
STATUS_MISSING = "missing-evidence"
STATUS_SUPERSEDED = "superseded"

STATUS_ORDER = {
    STATUS_MISSING: 4,
    STATUS_WAIVED: 3,
    STATUS_LIMITED: 2,
    STATUS_EQUIVALENT: 1,
    STATUS_SUPERSEDED: 0,
}

VERIFIED_SHARDING_REFERENCES = [
    "bridge/gtkb-session-activity-envelope-sharding-umbrella-004.md",
    "bridge/gtkb-envelope-sharding-taxonomy-baseline-006.md",
    "bridge/gtkb-envelope-sharding-harness-projection-parity-004.md",
    "bridge/gtkb-envelope-sharding-compact-query-modes-004.md",
]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _active_harnesses(registry: dict[str, Any]) -> list[dict[str, Any]]:
    raw = registry.get("harnesses")
    if not isinstance(raw, list):
        return []
    harnesses = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        if _clean_text(row.get("status") or "active") != "active":
            continue
        if not _clean_text(row.get("id")) or not _clean_text(row.get("harness_name")):
            continue
        harnesses.append(row)
    return sorted(harnesses, key=lambda row: _clean_text(row.get("id")))


def _capability_floor_by_harness(capability_registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = capability_registry.get("harnesses")
    if isinstance(raw, dict):
        return {str(name): value for name, value in raw.items() if isinstance(value, dict)}
    return {}


def _active_waivers_by_harness(waivers_payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    raw = waivers_payload.get("waivers")
    waivers = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    by_harness: dict[str, list[dict[str, str]]] = {}
    for waiver in waivers:
        if _clean_text(waiver.get("status")) != "active":
            continue
        harness_name = _clean_text(waiver.get("harness"))
        if not harness_name:
            continue
        by_harness.setdefault(harness_name, []).append({str(k): _clean_text(v) for k, v in waiver.items()})
    return by_harness


def _latest_session_envelope(root: Path, harness_name: str) -> dict[str, Any]:
    harness_dir = root / "harness-state" / harness_name
    current = harness_dir / "session-envelope.json"
    if current.is_file():
        payload = _read_json(current)
        return {
            "status": STATUS_EQUIVALENT if _valid_session_envelope(payload) else STATUS_MISSING,
            "path": current.relative_to(root).as_posix(),
            "session_id": _clean_text(payload.get("session_id")),
            "envelope_schema_version": payload.get("envelope_schema_version"),
            "observed_state": _clean_text(payload.get("status")),
        }

    archive_dir = harness_dir / "session-envelope-archive"
    archived = sorted(archive_dir.glob("*session-envelope.json")) if archive_dir.is_dir() else []
    if archived:
        latest = archived[-1]
        payload = _read_json(latest)
        return {
            "status": STATUS_EQUIVALENT if _valid_session_envelope(payload) else STATUS_MISSING,
            "path": latest.relative_to(root).as_posix(),
            "session_id": _clean_text(payload.get("session_id")),
            "envelope_schema_version": payload.get("envelope_schema_version"),
            "observed_state": _clean_text(payload.get("status")),
        }

    return {
        "status": STATUS_MISSING,
        "path": None,
        "session_id": None,
        "envelope_schema_version": None,
        "observed_state": None,
    }


def _valid_session_envelope(payload: dict[str, Any]) -> bool:
    return bool(
        payload.get("envelope_schema_version")
        and _clean_text(payload.get("harness_id"))
        and _clean_text(payload.get("harness_name"))
        and _clean_text(payload.get("session_id"))
        and _clean_text(payload.get("role_resolved"))
    )


def _classify_mode(mode: str) -> dict[str, str]:
    if not mode or mode not in VALID_MODES:
        return {
            "status": STATUS_MISSING,
            "mode": mode or "missing",
            "note": "Envelope mode is missing or outside the WI-4950 accepted vocabulary.",
        }
    if mode in LIMITED_MODES:
        return {
            "status": STATUS_LIMITED,
            "mode": mode,
            "note": f"`{mode}` is an accepted WI-4950 compact/limited envelope representation.",
        }
    return {"status": STATUS_EQUIVALENT, "mode": mode, "note": "`native` matches the WI-4950 baseline."}


def _full_transcript_classification(
    *,
    harness_name: str,
    merged_row: dict[str, Any],
    waivers: list[dict[str, str]],
) -> dict[str, Any]:
    waiver = next((item for item in waivers if item.get("dimension") == "full_transcript_archive"), None)
    if waiver is not None:
        return {
            "status": STATUS_WAIVED,
            "required": False,
            "waiver_id": waiver.get("id"),
            "evidence": waiver.get("evidence"),
            "note": waiver.get("rationale"),
        }
    required = merged_row.get("full_transcript_archive_required")
    if required is False:
        return {
            "status": STATUS_EQUIVALENT,
            "required": False,
            "waiver_id": None,
            "evidence": "harness-state/harness-registry.json",
            "note": "Harness is assessable through compact result/session envelopes without full transcript archives.",
        }
    return {
        "status": STATUS_MISSING,
        "required": required,
        "waiver_id": None,
        "evidence": None,
        "note": f"{harness_name} lacks full-transcript independence evidence or a typed waiver.",
    }


def _overall_classification(dimensions: dict[str, dict[str, Any]]) -> str:
    core_statuses = [
        str(row.get("status"))
        for name, row in dimensions.items()
        if name != "verified_sharding_boundary" and row.get("status")
    ]
    if not core_statuses:
        return STATUS_MISSING
    return max(core_statuses, key=lambda status: STATUS_ORDER.get(status, 99))


def _lane_record(
    *,
    root: Path,
    row: dict[str, Any],
    capability_floor: dict[str, Any],
    waivers: list[dict[str, str]],
) -> dict[str, Any]:
    harness_name = _clean_text(row.get("harness_name"))
    merged_row = {**capability_floor, **row}
    dimensions: dict[str, dict[str, Any]] = {}
    for dimension, field in ENVELOPE_FIELDS.items():
        dimensions[dimension] = _classify_mode(_clean_text(merged_row.get(field)))
    dimensions["full_transcript_archive"] = _full_transcript_classification(
        harness_name=harness_name,
        merged_row=merged_row,
        waivers=waivers,
    )
    dimensions["session_envelope_evidence"] = _latest_session_envelope(root, harness_name)
    dimensions["verified_sharding_boundary"] = {
        "status": STATUS_SUPERSEDED,
        "note": "Use verified envelope-sharding coverage as existing baseline evidence; do not reopen it here.",
        "references": VERIFIED_SHARDING_REFERENCES,
    }
    provider_limited = any(dimensions[name]["mode"] in PROVIDER_LIMITED_MODES for name in ENVELOPE_FIELDS)
    return {
        "harness_id": _clean_text(row.get("id")),
        "harness_name": harness_name,
        "roles": row.get("role") if isinstance(row.get("role"), list) else [],
        "status": _clean_text(row.get("status") or "active"),
        "overall_classification": _overall_classification(dimensions),
        "provider_limited": provider_limited,
        "typed_waivers": waivers,
        "result_envelope_limitations": _clean_text(merged_row.get("result_envelope_limitations")),
        "activity_envelope_manifest_source": _clean_text(merged_row.get("activity_envelope_manifest_source")),
        "dimensions": dimensions,
        "evidence_sources": {
            "registry_projection": "harness-state/harness-registry.json",
            "capability_registry": "config/agent-control/harness-capability-registry.toml"
            if capability_floor
            else None,
            "waiver_registry": "config/harness-parity/phase2-waivers.toml" if waivers else None,
        },
    }


def build_report(
    *,
    project_root: Path | str | None = None,
    registry_path: Path | str | None = None,
    capability_registry_path: Path | str | None = None,
    waivers_path: Path | str | None = None,
) -> dict[str, Any]:
    """Return structured WI-4968 envelope-equivalence evidence."""

    root = Path(project_root).resolve() if project_root is not None else _project_root()
    registry_file = (
        Path(registry_path) if registry_path is not None else root / "harness-state" / "harness-registry.json"
    )
    capability_file = (
        Path(capability_registry_path)
        if capability_registry_path is not None
        else root / "config" / "agent-control" / "harness-capability-registry.toml"
    )
    waivers_file = (
        Path(waivers_path) if waivers_path is not None else root / "config" / "harness-parity" / "phase2-waivers.toml"
    )

    registry = _read_json(registry_file)
    capability_floor = _capability_floor_by_harness(_read_toml(capability_file))
    waivers = _active_waivers_by_harness(_read_toml(waivers_file))

    lanes = [
        _lane_record(
            root=root,
            row=row,
            capability_floor=capability_floor.get(_clean_text(row.get("harness_name")), {}),
            waivers=waivers.get(_clean_text(row.get("harness_name")), []),
        )
        for row in _active_harnesses(registry)
    ]
    counts = Counter(lane["overall_classification"] for lane in lanes)
    issue_count = sum(1 for lane in lanes if lane["overall_classification"] == STATUS_MISSING)
    status = "FAIL" if not lanes else "WARN" if issue_count else "PASS"
    return {
        "schema_version": 1,
        "evidence_id": EVIDENCE_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "project_root": str(root),
        "baseline": {
            "work_item_id": BASELINE_WORK_ITEM,
            "title": BASELINE_TITLE,
            "accepted_modes": sorted(VALID_MODES),
            "verified_sharding_references": VERIFIED_SHARDING_REFERENCES,
        },
        "source_files": {
            "registry_projection": registry_file.relative_to(root).as_posix()
            if registry_file.is_relative_to(root)
            else str(registry_file),
            "capability_registry": capability_file.relative_to(root).as_posix()
            if capability_file.is_relative_to(root)
            else str(capability_file),
            "waiver_registry": waivers_file.relative_to(root).as_posix()
            if waivers_file.is_relative_to(root)
            else str(waivers_file),
        },
        "status": status,
        "summary": {
            "harness_count": len(lanes),
            "overall_classification_counts": dict(sorted(counts.items())),
            "missing_evidence_harnesses": [
                lane["harness_name"] for lane in lanes if lane["overall_classification"] == STATUS_MISSING
            ],
            "typed_waiver_count": sum(len(lane["typed_waivers"]) for lane in lanes),
        },
        "lanes": lanes,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact markdown evidence report."""

    baseline = report["baseline"]
    lines = [
        "# Harness Envelope Equivalence Evidence",
        "",
        f"- evidence_id: `{report['evidence_id']}`",
        f"- status: `{report['status']}`",
        f"- baseline: `{baseline['work_item_id']}` - {baseline['title']}",
        f"- generated_at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- harness_count: `{report['summary']['harness_count']}`",
        f"- typed_waiver_count: `{report['summary']['typed_waiver_count']}`",
        f"- missing_evidence_harnesses: `{', '.join(report['summary']['missing_evidence_harnesses']) or 'none'}`",
        "",
        "| Harness | Classification | Activity | Result | Session | Session evidence | Typed waivers |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for lane in report["lanes"]:
        dimensions = lane["dimensions"]
        waiver_ids = ", ".join(waiver["id"] for waiver in lane["typed_waivers"]) or "-"
        lines.append(
            f"| `{lane['harness_name']}` (`{lane['harness_id']}`) | `{lane['overall_classification']}` | "
            f"`{dimensions['activity']['status']}`/{dimensions['activity']['mode']} | "
            f"`{dimensions['result']['status']}`/{dimensions['result']['mode']} | "
            f"`{dimensions['session']['status']}`/{dimensions['session']['mode']} | "
            f"`{dimensions['session_envelope_evidence']['status']}` | {waiver_ids} |"
        )

    lines.extend(
        [
            "",
            "## Typed Waivers",
            "",
        ]
    )
    any_waiver = False
    for lane in report["lanes"]:
        for waiver in lane["typed_waivers"]:
            any_waiver = True
            lines.append(f"- `{lane['harness_name']}` `{waiver['id']}` ({waiver['dimension']}): {waiver['rationale']}")
    if not any_waiver:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Verified Sharding Boundary",
            "",
            "Existing envelope-sharding implementation is treated as verified coverage and is not reopened by WI-4968.",
        ]
    )
    for reference in baseline["verified_sharding_references"]:
        lines.append(f"- `{reference}`")

    missing = [
        lane
        for lane in report["lanes"]
        if lane["overall_classification"] == STATUS_MISSING
        or lane["dimensions"]["session_envelope_evidence"]["status"] == STATUS_MISSING
    ]
    if missing:
        lines.extend(["", "## Evidence Gaps", ""])
        for lane in missing:
            session_path = lane["dimensions"]["session_envelope_evidence"]["path"] or "no session-envelope file found"
            lines.append(
                f"- `{lane['harness_name']}`: `{lane['overall_classification']}`; session evidence: {session_path}"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of markdown.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path for the rendered payload.")
    args = parser.parse_args(argv)

    report = build_report(project_root=args.project_root)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n" if args.json else render_markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
