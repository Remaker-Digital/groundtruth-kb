"""Validate that a dispatched worker's behavior role matches its session document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROLE_BOOTSTRAP_CONTRACT = {
    "phase": "role-bootstrap",
    "ordering": "before-activity",
    "gate": "protected-work",
    "behavior_role_source": "envelope-role",
    "source_classification": "source-classified",
    "registry_read_policy": "registry-read-classification",
    "registry_read_classification": "no-dispatcher-config-read",
    "mismatch_policy": "mismatch-audit",
    "substitution_policy": "no-role-substitution",
    "activity_policy": "cannot-alter-role",
    "scope": "applicable-harnesses",
    "interactive_authority": "interactive-transcript",
    "interactive_persistence": "persists-boundaries",
    "subject_init_policy": "subject-only",
    "fallback_policy": "resolver-fallback",
    "marker_policy": "session-matched-marker",
    "registry_mutation_policy": "no-registry-mutation",
    "registry_authority_policy": "registry-not-behavior-authority",
}


def _failure_class(message: str) -> str:
    lowered = message.lower()
    if "missing" in lowered or "does not exist" in lowered:
        return "missing"
    if "malformed" in lowered or "unsupported" in lowered or "must be" in lowered:
        return "malformed"
    if "conflict" in lowered or "ambiguous" in lowered or "does not match" in lowered:
        return "conflict"
    return "invalid"


def _denied(reason: str, *, failure_class: str) -> dict[str, object]:
    return {
        "ok": False,
        "decision": "deny",
        "failure_class": failure_class,
        "reason": reason,
        "recovery": "refresh the explicit worker session envelope before work",
        "authority_contract": ROLE_BOOTSTRAP_CONTRACT,
    }


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
        reason = str(exc)
        return _denied(reason, failure_class=_failure_class(reason))
    if not provenance["dispatch_run_id"]:
        return _denied(
            "Worker role provenance is missing dispatch run evidence.",
            failure_class="missing",
        )
    if provenance["role_resolution_source"] != "dispatcher_composition":
        return _denied(
            "Worker role provenance is malformed: dispatched work requires dispatcher_composition source evidence.",
            failure_class="malformed",
        )

    # Registry-selected dispatcher intent is an audit comparison only. A mismatch
    # must never substitute or block the explicit worker behavior role.
    audit_status = "match" if provenance["role"] == dispatch_role else "warning"
    return {
        "ok": True,
        "decision": "allow",
        "resolved_role": provenance["role"],
        "role": provenance["role"],
        "harness_name": provenance["harness_name"],
        "session_id": provenance["session_id"],
        "run_id": provenance["dispatch_run_id"],
        "role_resolution_source": provenance["role_resolution_source"],
        "source_classified": "dispatcher-envelope",
        "mismatch_audit": {
            "status": audit_status,
            "dispatch_role": dispatch_role,
            "worker_role": provenance["role"],
        },
        "authority_contract": ROLE_BOOTSTRAP_CONTRACT,
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
