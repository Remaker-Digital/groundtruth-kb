"""Validate that a dispatched worker's behavior role matches its session document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def evaluate(
    project_root: Path,
    *,
    session_id: str,
    harness_name: str,
    dispatch_role: str,
) -> dict[str, object]:
    """Validate explicit worker evidence without consulting dispatcher configuration."""
    from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance

    try:
        provenance = resolve_worker_role_provenance(
            project_root,
            current_session_id=session_id,
            harness_name=harness_name,
        )
    except EnvelopeError as exc:
        return {"ok": False, "reason": str(exc), "recovery": "refresh the explicit worker session envelope before work"}
    if not provenance["dispatch_run_id"]:
        return {
            "ok": False,
            "reason": "Worker role provenance is missing dispatch run evidence.",
            "recovery": "refresh the explicit worker session envelope before work",
        }

    # Registry-selected dispatcher intent is an audit comparison only. A mismatch
    # must never substitute or block the explicit worker behavior role.
    audit_status = "match" if provenance["role"] == dispatch_role else "warning"
    return {
        "ok": True,
        "role": provenance["role"],
        "harness_name": provenance["harness_name"],
        "dispatch_audit": {
            "status": audit_status,
            "dispatch_role": dispatch_role,
            "worker_role": provenance["role"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--harness-name", required=True)
    parser.add_argument("--dispatch-role", required=True, choices=("prime-builder", "loyal-opposition"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = evaluate(
        args.project_root.resolve(),
        session_id=args.session_id,
        harness_name=args.harness_name,
        dispatch_role=args.dispatch_role,
    )
    if args.json:
        print(json.dumps(result, sort_keys=True))
    elif result["ok"]:
        print(f"dispatched worker role verified: {result['role']}/{result['harness_name']}")
    else:
        print(f"dispatched worker role bootstrap failed: {result['reason']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
