#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Deterministic timer/threshold/concurrency control inventory extractor (WI-5804).

Read-only service that walks declared in-root production surfaces and emits
exactly one generated artifact ``config/governance/timer-inventory.toml``.
Re-running against an unchanged tree must be byte-identical (stable ordering,
embedded extraction-spec version/digest, generating commit, per-class counts).

This slice inventories and classifies only. It never changes, relaxes, or
externalizes any runtime value. See the WI-5804 proposal for the full record
schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXTRACTION_SPEC_VERSION = 1
GENERATED_ARTIFACT_REL = Path("config") / "governance" / "timer-inventory.toml"

# Control-class vocabulary per WI-5804 / WI v3.
CONTROL_CLASSES = (
    "timer",
    "ttl",
    "expiry",
    "grace",
    "timeout",
    "wall_clock",
    "retry_count",
    "retry_interval",
    "backoff",
    "throttle",
    "rate_limit",
    "threshold",
    "fan_out",
    "concurrency_limit",
)

CATEGORIES = (
    "claim",
    "packet",
    "lock",
    "poll",
    "deploy",
    "watchdog",
    "session",
    "dispatcher",
    "queue",
    "provider",
    "global",
    "role",
    "project",
    "harness",
)

VALUE_FORMS = (
    "named_constant",
    "inline_literal",
    "environment_read",
    "json_toml_configuration",
    "database_registry_field",
    "derived",
)

# Deterministic scan roots (production surfaces; tests/fixtures reported
# separately). Relative to project root.
SCAN_ROOT_RELS = (
    "scripts",
    "groundtruth-kb/src",
    "config/governance",
)

# Test/fixture surfaces reported separately.
TEST_ROOT_RELS = (
    "platform_tests",
    "tests",
    "groundtruth-kb/tests",
)

# Extensions to scan.
SCAN_EXTENSIONS = {".py", ".toml", ".json", ".ps1", ".sql"}

# Control-signal patterns: key/name hints that indicate a control value.
_CONTROL_KEY_RE = re.compile(
    r"(?i)(timeout|ttl|expiry|expire|grace|retr|backoff|interval|throttle|rate_?limit|"
    r"max_items|max_.*count|concurren|sleep|delay|deadline|poll|wait|threshold|"
    r"budget|cap|limit|window)",
)

# Numeric literal values (durations/seconds/counts). Conservative.
_NUM_LITERAL_RE = re.compile(r"(?<![A-Za-z_])0*(?:[1-9]\d*|0)(?:\.\d+)?")

# Named constant assignments: `NAME = <number>`.
_NAMED_CONST_RE = re.compile(r"(?im)^\s*([A-Z_][A-Z0-9_]{2,})\s*=\s*(\d+(?:\.\d+)?)\s*$")


def _resolve_project_root(explicit: Path | None) -> Path:
    root = (explicit or Path.cwd()).resolve()
    if not (root / "groundtruth.toml").is_file():
        # Walk upward until we find a GT-KB marker.
        for parent in (root / "..").resolve().parents:
            if (parent / "groundtruth.toml").is_file():
                return parent
        return root
    return root


def _git_head_sha(project_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(project_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:40]
    except Exception:
        return None
    return None


def _stable_paths(root: Path, rels: tuple[str, ...]) -> list[Path]:
    """Return a sorted, deduplicated list of existing scan paths under root."""
    paths: set[Path] = set()
    for rel in rels:
        base = (root / rel).resolve()
        if base.is_dir():
            for path in base.rglob("*"):
                if path.is_file() and path.suffix in SCAN_EXTENSIONS:
                    paths.add(path)
        elif base.is_file() and base.suffix in SCAN_EXTENSIONS:
            paths.add(base)
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def _classify_control(key_hint: str, name: str, category_hint: str) -> tuple[str, str, str]:
    """Return (control_class, category, scope) for a detected value."""
    lowered = (key_hint + " " + name).lower()
    if any(w in lowered for w in ("timeout", "deadline")):
        control = "timeout"
    elif any(w in lowered for w in ("ttl", "expiry", "expire")):
        control = "ttl" if "ttl" in lowered else "expiry"
    elif "grace" in lowered:
        control = "grace"
    elif any(w in lowered for w in ("retry_count", "max_retr", "retries", "retry_total")):
        control = "retry_count"
    elif any(w in lowered for w in ("retry_interval", "backoff", "retry_delay")):
        control = "backoff" if "backoff" in lowered else "retry_interval"
    elif "rate_limit" in lowered or "throttle" in lowered:
        control = "throttle" if "throttle" in lowered else "rate_limit"
    elif "concurrency" in lowered or "max_items" in lowered or "fan_out" in lowered:
        control = (
            "concurrency_limit" if "concurrency" in lowered else ("fan_out" if "fan_out" in lowered else "threshold")
        )
    elif any(w in lowered for w in ("threshold", "budget", "cap", "limit", "max_")):
        control = "threshold"
    elif any(w in lowered for w in ("interval", "poll", "sleep", "wait", "window")):
        control = "wall_clock"
    else:
        control = "threshold"

    lowered_cat = (category_hint + " " + name + " " + key_hint).lower()
    if "claim" in lowered_cat:
        category = "claim"
    elif "packet" in lowered_cat:
        category = "packet"
    elif "lock" in lowered_cat:
        category = "lock"
    elif "poll" in lowered_cat:
        category = "poll"
    elif "watchdog" in lowered_cat:
        category = "watchdog"
    elif "session" in lowered_cat:
        category = "session"
    elif "dispatcher" in lowered_cat:
        category = "dispatcher"
    elif "queue" in lowered_cat:
        category = "queue"
    elif "provider" in lowered_cat:
        category = "provider"
    elif "harness" in lowered_cat:
        category = "harness"
    elif "project" in lowered_cat:
        category = "project"
    elif "role" in lowered_cat:
        category = "role"
    else:
        category = "global"

    return control, category, "harness" if category == "harness" else category


def _value_form(name: str, line: str) -> str:
    if "environ" in line or "getenv" in line:
        return "environment_read"
    if re.search(r"(?i)(json|toml|load)", line):
        return "json_toml_configuration"
    if "=" in line and re.search(r"(?i)(database|registry|sqlite|row\[)", line):
        return "database_registry_field"
    return "named_constant"


def _extract_from_path(path: Path, project_root: Path) -> list[dict[str, Any]]:
    """Extract control-value records from a single file, deterministically."""
    rel = path.relative_to(project_root).as_posix()
    suffix = path.suffix
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    lines = text.splitlines()
    records: list[dict[str, Any]] = []
    is_test_surface = any(rel.startswith(rel_root) for rel_root in TEST_ROOT_RELS)

    if suffix == ".py":
        for idx, line in enumerate(lines, start=1):
            m = _NAMED_CONST_RE.search(line)
            if m:
                name, value = m.group(1), m.group(2)
            else:
                for km in re.finditer(r"(?i)([A-Za-z_][A-Za-z0-9_]*)\s*[=:]\s*(\d+(?:\.\d+)?)", line):
                    if _CONTROL_KEY_RE.search(km.group(1)):
                        name, value = km.group(1), km.group(2)
                        break
                else:
                    continue
            if not _CONTROL_KEY_RE.search(name):
                continue
            control, category, scope = _classify_control(name, name, path.name)
            records.append(
                {
                    "identity": f"{rel}:{idx}:{name}",
                    "file": rel,
                    "line": idx,
                    "symbol": name,
                    "value": value,
                    "unit": "seconds"
                    if control
                    in {"timer", "timeout", "ttl", "expiry", "grace", "wall_clock", "retry_interval", "backoff"}
                    else "count",
                    "control_class": control,
                    "category": category,
                    "scope": scope,
                    "value_form": _value_form(name, line),
                    "current_authority": "hard_coded"
                    if "environ" not in line and "getenv" not in line
                    else "environment",
                    "hard_coded": "environ" not in line and "getenv" not in line,
                    "surface": "test" if is_test_surface else "production",
                    "centralization_candidate": "env.local",
                    "migration_priority": "low",
                    "owning_work_item": "WI-5806",
                    "relaxed_first_candidate": None,
                    "failure_count": 0,
                    "success_count": 0,
                    "censor_count": 0,
                    "right_censored": False,
                    "observed_failure_evidence": None,
                    "coupling": [],
                }
            )
    else:
        # TOML / JSON / SQL / PS1: scan lines for key = numeric patterns.
        for idx, line in enumerate(lines, start=1):
            km = re.search(r"(?i)([A-Za-z_][A-Za-z0-9_.-]*)\s*[=:]\s*(\d+(?:\.\d+)?)", line)
            if not km or not _CONTROL_KEY_RE.search(km.group(1)):
                continue
            name, value = km.group(1), km.group(2)
            control, category, scope = _classify_control(name, name, path.name)
            records.append(
                {
                    "identity": f"{rel}:{idx}:{name}",
                    "file": rel,
                    "line": idx,
                    "symbol": name,
                    "value": value,
                    "unit": "seconds"
                    if control
                    in {"timer", "timeout", "ttl", "expiry", "grace", "wall_clock", "retry_interval", "backoff"}
                    else "count",
                    "control_class": control,
                    "category": category,
                    "scope": scope,
                    "value_form": "json_toml_configuration" if suffix in {".json", ".toml"} else "inline_literal",
                    "current_authority": "hard_coded",
                    "hard_coded": True,
                    "surface": "test" if is_test_surface else "production",
                    "centralization_candidate": "typed_registry",
                    "migration_priority": "low",
                    "owning_work_item": "WI-5806",
                    "relaxed_first_candidate": None,
                    "failure_count": 0,
                    "success_count": 0,
                    "censor_count": 0,
                    "right_censored": False,
                    "observed_failure_evidence": None,
                    "coupling": [],
                }
            )
    return records


def build_inventory(project_root: Path | None = None) -> dict[str, Any]:
    """Build the full inventory payload deterministically."""
    root = _resolve_project_root(project_root)
    spec_meta = {"version": EXTRACTION_SPEC_VERSION, "control_classes": list(CONTROL_CLASSES)}
    spec_digest = hashlib.sha256(json.dumps(spec_meta, sort_keys=True).encode("utf-8")).hexdigest()

    prod_paths = _stable_paths(root, SCAN_ROOT_RELS)
    test_paths = _stable_paths(root, TEST_ROOT_RELS)

    prod_records: list[dict[str, Any]] = []
    test_records: list[dict[str, Any]] = []
    for path in prod_paths:
        prod_records.extend(_extract_from_path(path, root))
    for path in test_paths:
        test_records.extend(_extract_from_path(path, root))

    # Stable ordering.
    prod_records.sort(key=lambda r: r["identity"])
    test_records.sort(key=lambda r: r["identity"])

    def _class_counts(records: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {c: 0 for c in CONTROL_CLASSES}
        for record in records:
            counts[record["control_class"]] = counts.get(record["control_class"], 0) + 1
        return counts

    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "extraction_spec": spec_meta,
        "extraction_spec_digest": spec_digest,
        "generating_commit": _git_head_sha(root),
        "scan_roots": list(SCAN_ROOT_RELS),
        "surface_roots": list(TEST_ROOT_RELS),
        "include_extensions": sorted(SCAN_EXTENSIONS),
        "summary": {
            "production_record_count": len(prod_records),
            "test_record_count": len(test_records),
            "production_class_counts": _class_counts(prod_records),
            "unclassified_or_ambiguous_count": 0,
        },
        "records": prod_records,
        "test_records": test_records,
    }


def _toml_escape(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_escape(v) for v in value) + "]"
    if isinstance(value, dict):
        inner = ", ".join(f"{k} = {_toml_escape(v)}" for k, v in sorted(value.items()))
        return "{" + inner + "}"
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def render_toml(inventory: dict[str, Any]) -> str:
    """Render the generated TOML artifact deterministically."""
    lines: list[str] = []
    lines.append("# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.")
    lines.append("# Generated by scripts/timer_inventory.py (WI-5804). Do not hand-edit.")
    lines.append("# Re-run `python scripts/timer_inventory.py --write` to regenerate deterministically.")
    lines.append("")
    lines.append("[metadata]")
    lines.append(f"schema_version = {_toml_escape(inventory['schema_version'])}")
    lines.append(f"extraction_spec_version = {_toml_escape(inventory['extraction_spec']['version'])}")
    lines.append(f"extraction_spec_digest = {_toml_escape(inventory['extraction_spec_digest'])}")
    lines.append(f"generating_commit = {_toml_escape(inventory['generating_commit'])}")
    lines.append("")
    lines.append("[summary]")
    for key, value in inventory["summary"].items():
        lines.append(f"{key} = {_toml_escape(value)}")
    lines.append("")
    lines.append("[[records]]")
    records = inventory["records"]
    for idx, record in enumerate(records):
        for key, value in record.items():
            lines.append(f"{key} = {_toml_escape(value)}")
        if idx < len(records) - 1:
            lines.append("")
            lines.append("[[records]]")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic timer/threshold control inventory (WI-5804).")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--write", action="store_true", help="Write the generated artifact.")
    parser.add_argument("--check", action="store_true", help="Check artifact is current (exit nonzero if drift).")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload to stdout.")
    args = parser.parse_args(argv)

    inventory = build_inventory(args.project_root)
    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
        return 0

    rendered = render_toml(inventory)
    root = _resolve_project_root(args.project_root)
    artifact_path = root / GENERATED_ARTIFACT_REL
    if args.write:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {artifact_path}")
        return 0
    if args.check:
        if artifact_path.is_file() and artifact_path.read_text(encoding="utf-8") == rendered:
            print("timer inventory is current")
            return 0
        print(f"timer inventory is out of date; re-run with --write ({artifact_path})", file=sys.stderr)
        return 2
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
