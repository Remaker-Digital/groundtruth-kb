"""Measure session/activity envelope load from the sharding taxonomy.

The report is deterministic and read-only. It estimates surface size, rough
token load, activity auto-load payloads, and failure conditions that would blur
the global session envelope with activity-specific shards.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tomllib
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

BENCHMARK_ID = "activity_envelope_load"
REQUIRED_CLASSES = {"global_baseline", "activity_only", "explicit_query", "never_startup"}
REQUIRED_NEVER_STARTUP_PAYLOADS = {
    "raw_bridge_archival_json",
    "full_session_transcripts",
    "generated_runtime_cache_directories",
    "unbounded_database_dumps",
}

DEFAULT_THRESHOLDS = {
    "global_surface_warning_tokens": 60000,
    "global_surface_failure_tokens": 120000,
    "activity_auto_warning_tokens": 1200,
    "activity_auto_failure_tokens": 2400,
}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def _status_from_issues(issues: list[dict[str, str]]) -> str:
    severities = {issue["severity"] for issue in issues}
    if "FAIL" in severities:
        return "FAIL"
    if "WARN" in severities:
        return "WARN"
    return "PASS"


def _thresholds(taxonomy: dict[str, Any]) -> dict[str, int]:
    configured = taxonomy.get("measurement", {}).get("thresholds", {})
    thresholds = dict(DEFAULT_THRESHOLDS)
    for key in thresholds:
        if key in configured:
            thresholds[key] = int(configured[key])
    return thresholds


def _surface_stats(root: Path, paths: list[str]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    total_bytes = 0
    total_tokens = 0
    missing: list[str] = []
    for raw_path in paths:
        path = root / raw_path
        exists = path.is_file()
        size = path.stat().st_size if exists else 0
        tokens = math.ceil(size / 4) if size else 0
        total_bytes += size
        total_tokens += tokens
        if not exists:
            missing.append(raw_path)
        entries.append(
            {
                "path": raw_path,
                "exists": exists,
                "bytes": size,
                "estimated_tokens": tokens,
            }
        )
    return {
        "surface_count": len(paths),
        "existing_surface_count": len(paths) - len(missing),
        "missing_surfaces": missing,
        "surface_bytes": total_bytes,
        "surface_token_estimate": total_tokens,
        "surfaces": entries,
    }


def _payload_text(values: list[Any]) -> str:
    parts: list[str] = []
    for value in values:
        if isinstance(value, dict):
            for nested in value.values():
                if isinstance(nested, list):
                    parts.extend(str(item) for item in nested)
                else:
                    parts.append(str(nested))
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))
    return "\n".join(parts)


def _activity_report(name: str, entry: dict[str, Any]) -> dict[str, Any]:
    direction = entry.get("direction", {})
    history_state = entry.get("history_state", {})
    classification = {key: str(value) for key, value in entry.get("classification", {}).items()}
    auto_payload_text = _payload_text(
        [
            entry.get("skills", []),
            entry.get("terminology", []),
            direction.get("stance", ""),
            direction.get("guardrails", []),
            direction.get("manipulates", []),
        ]
    )
    return {
        "headless_eligibility": entry.get("headless_eligibility"),
        "classification": classification,
        "auto_payload_token_estimate": _estimate_tokens(auto_payload_text),
        "auto_payload_item_count": (
            len(entry.get("skills", []))
            + len(entry.get("terminology", []))
            + len(direction.get("guardrails", []))
            + len(direction.get("manipulates", []))
            + (1 if direction.get("stance") else 0)
        ),
        "explicit_query_source_count": len(history_state.get("sources", [])),
        "skills_count": len(entry.get("skills", [])),
        "terminology_count": len(entry.get("terminology", [])),
    }


def build_report(
    *,
    project_root: Path | None = None,
    taxonomy_path: Path | None = None,
    profiles_path: Path | None = None,
) -> dict[str, Any]:
    """Build a compact session/activity envelope load report."""
    root = (project_root or _project_root()).resolve()
    taxonomy_file = taxonomy_path or root / "config" / "agent-control" / "activity-envelope-sharding.toml"
    profiles_file = profiles_path or root / "config" / "agent-control" / "activity-disposition-profiles.toml"
    taxonomy = _load_toml(taxonomy_file)
    profiles = _load_toml(profiles_file)
    thresholds = _thresholds(taxonomy)
    issues: list[dict[str, str]] = []

    classes = taxonomy.get("classes", {})
    declared_classes = set(taxonomy.get("taxonomy", {}).get("required_classes", []))
    missing_classes = sorted(REQUIRED_CLASSES - declared_classes)
    if missing_classes:
        issues.append(
            {
                "severity": "FAIL",
                "code": "missing_required_class",
                "message": f"Missing sharding classes: {missing_classes}",
            }
        )

    global_class = classes.get("global_baseline", {})
    global_surfaces = _surface_stats(root, list(global_class.get("allowed_surfaces", [])))
    if global_surfaces["surface_token_estimate"] > thresholds["global_surface_failure_tokens"]:
        issues.append(
            {
                "severity": "FAIL",
                "code": "global_surface_token_estimate_exceeds_failure_threshold",
                "message": "Global baseline allowed surfaces exceed failure threshold.",
            }
        )
    elif global_surfaces["surface_token_estimate"] > thresholds["global_surface_warning_tokens"]:
        issues.append(
            {
                "severity": "WARN",
                "code": "global_surface_token_estimate_exceeds_warning_threshold",
                "message": "Global baseline allowed surfaces exceed warning threshold.",
            }
        )
    for missing in global_surfaces["missing_surfaces"]:
        issues.append(
            {
                "severity": "WARN",
                "code": "global_surface_missing",
                "message": f"Global baseline surface is missing: {missing}",
            }
        )

    explicit_query = classes.get("explicit_query", {})
    if explicit_query.get("compact_surface_required") is not True:
        issues.append(
            {
                "severity": "WARN",
                "code": "explicit_query_compact_surface_not_required",
                "message": "explicit_query class should require compact query/read surfaces.",
            }
        )

    never_startup = classes.get("never_startup", {})
    forbidden_payloads = set(never_startup.get("forbidden_payloads", []))
    missing_forbidden = sorted(REQUIRED_NEVER_STARTUP_PAYLOADS - forbidden_payloads)
    if missing_forbidden:
        issues.append(
            {
                "severity": "FAIL",
                "code": "missing_never_startup_payload",
                "message": f"never_startup is missing required forbidden payload(s): {missing_forbidden}",
            }
        )

    activities: dict[str, Any] = {}
    for name, entry in sorted(profiles.get("activities", {}).items()):
        activity = _activity_report(name, entry)
        classification = activity["classification"]
        global_leaks = [
            key
            for key in ("skills", "terminology", "history_state", "direction")
            if classification.get(key) == "global_baseline"
        ]
        if global_leaks:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": "activity_payload_in_global_baseline",
                    "message": f"Activity {name} classifies activity payload(s) as global_baseline: {global_leaks}",
                }
            )
        if classification.get("history_state") != "explicit_query":
            issues.append(
                {
                    "severity": "FAIL",
                    "code": "history_state_not_explicit_query",
                    "message": f"Activity {name} history_state must remain explicit_query.",
                }
            )
        if activity["auto_payload_token_estimate"] > thresholds["activity_auto_failure_tokens"]:
            issues.append(
                {
                    "severity": "FAIL",
                    "code": "activity_auto_payload_exceeds_failure_threshold",
                    "message": f"Activity {name} auto payload exceeds failure threshold.",
                }
            )
        elif activity["auto_payload_token_estimate"] > thresholds["activity_auto_warning_tokens"]:
            issues.append(
                {
                    "severity": "WARN",
                    "code": "activity_auto_payload_exceeds_warning_threshold",
                    "message": f"Activity {name} auto payload exceeds warning threshold.",
                }
            )
        activities[name] = activity

    auto_tokens = sum(activity["auto_payload_token_estimate"] for activity in activities.values())
    payload = {
        "schema_version": 1,
        "benchmark_id": BENCHMARK_ID,
        "status": _status_from_issues(issues),
        "project_root": str(root),
        "thresholds": thresholds,
        "global_baseline": {
            **global_surfaces,
            "required_payload_count": len(global_class.get("required_payloads", [])),
            "excluded_payloads": list(global_class.get("excludes_payloads", [])),
        },
        "activities": activities,
        "never_startup": {
            "forbidden_payloads": sorted(forbidden_payloads),
            "missing_required_forbidden_payloads": missing_forbidden,
            "required_alternative": never_startup.get("required_alternative"),
        },
        "summary": {
            "activity_count": len(activities),
            "activity_auto_payload_token_estimate_total": auto_tokens,
            "global_surface_token_estimate": global_surfaces["surface_token_estimate"],
            "issue_count": len(issues),
        },
        "issues": issues,
    }
    return payload


def render_markdown(report: dict[str, Any]) -> str:
    """Render a compact human-readable summary."""
    lines = [
        "# Activity Envelope Load Benchmark",
        "",
        f"- status: {report['status']}",
        f"- global surface token estimate: {report['summary']['global_surface_token_estimate']}",
        f"- activity auto payload token estimate total: {report['summary']['activity_auto_payload_token_estimate_total']}",
        f"- issues: {report['summary']['issue_count']}",
        "",
        "| Activity | Auto tokens | Explicit-query sources | Skills | Terms |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, activity in report["activities"].items():
        lines.append(
            f"| {name} | {activity['auto_payload_token_estimate']} | "
            f"{activity['explicit_query_source_count']} | {activity['skills_count']} | "
            f"{activity['terminology_count']} |"
        )
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- {issue['severity']} `{issue['code']}`: {issue['message']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)
    report = build_report(project_root=args.project_root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0 if report["status"] in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
