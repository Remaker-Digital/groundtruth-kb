#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Inventory project-authorization exposure for non-terminal bridge threads.

The sweep is read-only. It indexes the bridge directory once, selects the
latest implementation-bearing artifact for each non-terminal exact thread,
projects the terminal cohort, and delegates PAUTH evaluation to the same
canonical operation-time path used by ``bridge_applicability_preflight.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

try:
    from scripts import bridge_applicability_preflight as preflight
    from scripts.bridge_thread_files import index_bridge_thread_files, status_from_bridge_file
except ImportError:  # pragma: no cover - direct script execution path
    import bridge_applicability_preflight as preflight  # type: ignore[no-redef]
    from bridge_thread_files import index_bridge_thread_files, status_from_bridge_file  # type: ignore[no-redef]

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
OUTPUT_ROOT_RELATIVE: Final[Path] = Path(".gtkb-state/pauth-exposure")
TERMINAL_STATUSES: Final[frozenset[str]] = frozenset(
    {"VERIFIED", "WITHDRAWN", "DEFERRED", "RETIRED", "SUPERSEDED", "ACCEPTED", "ADVISORY"}
)
IMPLEMENTATION_KINDS: Final[frozenset[str]] = preflight.PROPOSAL_BRIDGE_KINDS | preflight.FINALIZATION_BRIDGE_KINDS


def _relative(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _latest_status(files: list[Any]) -> tuple[str | None, Path | None]:
    if not files:
        return None, None
    latest = files[-1]
    return status_from_bridge_file(latest.path), latest.path


def _latest_implementation_content(files: list[Any]) -> tuple[Path, str, str] | None:
    selected: tuple[Path, str, str] | None = None
    for item in files:
        try:
            content = item.path.read_text(encoding="utf-8")
        except OSError:
            continue
        kind = preflight._bridge_kind(content)
        if kind in IMPLEMENTATION_KINDS:
            selected = (item.path, content, str(kind))
    return selected


def _preflight_versions(root: Path, slug: str, files: list[Any]) -> list[preflight.BridgeVersion]:
    versions: list[preflight.BridgeVersion] = []
    for item in files:
        versions.append(
            preflight.BridgeVersion(
                status=status_from_bridge_file(item.path) or "UNKNOWN",
                rel_path=_relative(root, item.path),
                abs_path=item.path,
                version_number=item.version,
            )
        )
    return versions


def _classification(pauth: dict[str, Any], errors: list[str]) -> str:
    if pauth.get("allowed") is True:
        return "authorized"
    if pauth.get("decisions"):
        codes = {str(decision.get("reason_code") or "") for decision in pauth["decisions"]}
        if "target_mutation_class_not_allowed" in codes:
            return "mutation_class_denied"
        if "forbidden_operation" in codes or "unknown_forbidden_operation" in codes:
            return "operation_denied"
        return "authorization_denied"
    error = str(pauth.get("error") or " ".join(errors)).lower()
    if "does not cite project authorization" in error:
        return "missing_pauth"
    if "evaluator" in error or "taxonomy" in error:
        return "pauth_load_or_evaluator_failure"
    return "pauth_load_or_evaluator_failure"


def _source_fingerprint(root: Path, file_index: dict[str, list[Any]]) -> str:
    bridge_files: list[tuple[str, int, int]] = []
    for files in file_index.values():
        for item in files:
            stat = item.path.stat()
            bridge_files.append((_relative(root, item.path), stat.st_size, stat.st_mtime_ns))
    database_files: list[tuple[str, int | None, int | None]] = []
    for suffix in ("", "-wal", "-shm"):
        path = root / f"groundtruth.db{suffix}"
        try:
            stat = path.stat()
            database_files.append((path.name, stat.st_size, stat.st_mtime_ns))
        except FileNotFoundError:
            database_files.append((path.name, None, None))
    material = json.dumps(
        {
            "bridge_files": sorted(bridge_files),
            "database_files": database_files,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def build_inventory(
    project_root: Path = PROJECT_ROOT,
    *,
    decision_time: datetime | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    effective_decision_time = (decision_time or datetime.now(UTC)).astimezone(UTC).replace(microsecond=0)
    file_index = index_bridge_thread_files(root)
    start_fingerprint = _source_fingerprint(root, file_index)
    rows: list[dict[str, Any]] = []
    nonterminal_count = 0
    skipped_nonimplementation = 0

    for slug in sorted(file_index):
        files = file_index[slug]
        latest_status, latest_path = _latest_status(files)
        if latest_status in TERMINAL_STATUSES:
            continue
        nonterminal_count += 1
        if latest_status is None:
            rows.append(
                {
                    "bridge_id": slug,
                    "latest_status": None,
                    "latest_path": _relative(root, latest_path) if latest_path else None,
                    "classification": "unknown_latest_status",
                    "blocking_errors": ["Latest numbered bridge file has no recognized status token."],
                }
            )
            continue

        selected = _latest_implementation_content(files)
        if selected is None:
            skipped_nonimplementation += 1
            continue
        scope_path, scope_content, scope_kind = selected
        declared_targets = preflight.extract_declared_target_paths(scope_content)
        versions = _preflight_versions(root, slug, files)
        authorization_content = scope_content
        authorization_source = _relative(root, scope_path)
        authorization_specs = set(preflight.extract_spec_links(scope_content))
        approved_content: str | None = None
        if scope_kind in preflight.FINALIZATION_BRIDGE_KINDS:
            approved_content, approved_path, proposal_error = preflight._approved_proposal_for_report(
                bridge_id=slug,
                report_content=scope_content,
                versions=versions,
            )
            if proposal_error is not None:
                rows.append(
                    {
                        "bridge_id": slug,
                        "latest_status": latest_status,
                        "latest_path": _relative(root, latest_path) if latest_path else None,
                        "scope_path": _relative(root, scope_path),
                        "scope_kind": scope_kind,
                        "classification": "lifecycle_resolution_failure",
                        "authorization_id": None,
                        "authorization_version": None,
                        "project_id": None,
                        "cohort": [],
                        "requested_operations": list(preflight.PAUTH_PHASE_OPERATIONS["finalization"]),
                        "target_classifications": [],
                        "decisions": [],
                        "blocking_errors": [proposal_error],
                    }
                )
                continue
            if approved_content is not None:
                authorization_content = approved_content
                authorization_source = approved_path or authorization_source
                authorization_specs.update(preflight.extract_spec_links(approved_content))
        cohort = preflight._pauth_phase_cohort(
            phase="finalization",
            bridge_id=slug,
            content=scope_content,
            declared_target_paths=declared_targets,
            versions=versions,
            approved_proposal_content=approved_content,
        )
        pauth, errors = preflight._evaluate_pauth_phase(
            content=authorization_content,
            project_root=root,
            phase="finalization",
            cohort=cohort,
            cited_specs=authorization_specs,
            authorization_source=authorization_source,
            decision_time=effective_decision_time,
        )
        rows.append(
            {
                "bridge_id": slug,
                "latest_status": latest_status,
                "latest_path": _relative(root, latest_path) if latest_path else None,
                "scope_path": _relative(root, scope_path),
                "scope_kind": scope_kind,
                "classification": _classification(pauth, errors),
                "authorization_id": pauth.get("authorization_id"),
                "authorization_version": pauth.get("authorization_version"),
                "project_id": pauth.get("project_id"),
                "authorization_source": pauth.get("authorization_source"),
                "cohort": cohort,
                "requested_operations": pauth.get("requested_operations", []),
                "target_classifications": pauth.get("target_classifications", []),
                "decisions": pauth.get("decisions", []),
                "blocking_errors": errors,
            }
        )

    end_index = index_bridge_thread_files(root)
    end_fingerprint = _source_fingerprint(root, end_index)
    scan_consistent = start_fingerprint == end_fingerprint
    if not scan_consistent:
        rows = []
    counts = Counter(str(row["classification"]) for row in rows)
    if not scan_consistent:
        counts["concurrent_source_change"] += 1
    return {
        "schema_version": 1,
        "project_root": root.as_posix(),
        "decision_time": effective_decision_time.isoformat().replace("+00:00", "Z"),
        "scan_consistent": scan_consistent,
        "source_fingerprint": start_fingerprint if scan_consistent else None,
        "blocking_errors": (
            []
            if scan_consistent
            else ["Bridge or PAUTH source state changed during the sweep; mixed-snapshot results were discarded."]
        ),
        "thread_count": len(file_index),
        "nonterminal_thread_count": nonterminal_count,
        "evaluated_thread_count": len(rows),
        "skipped_nonimplementation_count": skipped_nonimplementation,
        "classification_counts": dict(sorted(counts.items())),
        "has_exposure": (not scan_consistent) or any(row["classification"] != "authorized" for row in rows),
        "rows": rows,
    }


def format_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# PAUTH Finalization Exposure Sweep",
        "",
        f"- Decision time: `{inventory['decision_time']}`",
        f"- Source snapshot consistent: `{str(inventory['scan_consistent']).lower()}`",
        f"- Source fingerprint: `{inventory['source_fingerprint']}`",
        f"- Thread count: `{inventory['thread_count']}`",
        f"- Non-terminal threads: `{inventory['nonterminal_thread_count']}`",
        f"- Evaluated implementation-bearing threads: `{inventory['evaluated_thread_count']}`",
        f"- Skipped non-implementation threads: `{inventory['skipped_nonimplementation_count']}`",
        f"- Exposure present: `{str(inventory['has_exposure']).lower()}`",
        f"- Classification counts: `{json.dumps(inventory['classification_counts'], sort_keys=True)}`",
        "",
        "| Bridge | Latest | Scope | Classification | Authorization |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in inventory["rows"]:
        lines.append(
            f"| `{row['bridge_id']}` | `{row.get('latest_status')}` | "
            f"`{row.get('scope_path')}` | `{row['classification']}` | "
            f"`{row.get('authorization_id')}` |"
        )
    return "\n".join(lines) + "\n"


def _validated_output_path(root: Path, output: Path) -> Path:
    candidate = output if output.is_absolute() else root / output
    resolved = candidate.resolve()
    allowed_root = (root / OUTPUT_ROOT_RELATIVE).resolve()
    if resolved != allowed_root and allowed_root not in resolved.parents:
        raise ValueError(f"output must remain under {OUTPUT_ROOT_RELATIVE.as_posix()}/")
    return resolved


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument(
        "--decision-time",
        default=None,
        help="UTC-aware ISO-8601 operation-time instant; defaults to the current UTC second.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output path; must remain under .gtkb-state/pauth-exposure/.",
    )
    return parser


def _parse_decision_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("decision time must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("decision time must include a UTC offset")
    return parsed.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.project_root.resolve()
    try:
        decision_time = _parse_decision_time(args.decision_time)
        inventory = build_inventory(root, decision_time=decision_time)
    except (OSError, RuntimeError, ValueError) as exc:
        sys.stderr.write(f"error: sweep failed closed: {exc}\n")
        return 3
    rendered = json.dumps(inventory, indent=2, sort_keys=True) + "\n" if args.json else format_markdown(inventory)
    if args.output is not None:
        try:
            output = _validated_output_path(root, args.output)
        except ValueError as exc:
            sys.stderr.write(f"error: {exc}\n")
            return 2
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(rendered)
    return 0 if inventory["scan_consistent"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
