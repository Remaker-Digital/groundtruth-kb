#!/usr/bin/env python3
"""One-shot Prime Builder dispatch executor for 2026-07-01 auto-dispatch.

Bridge entries (oldest-first):
- gtkb-gov-004-dangling-membership-repair-slice-3 (GO -002)
- gtkb-envelope-sharding-initial-shard-migration (GO -002)

Run from repo root:
  groundtruth-kb\\.venv\\Scripts\\python.exe .gtkb-state\\dispatch\\execute-pb-go-entries-20260701.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GT = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
PYTHON = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
IMPL_HELPER = PROJECT_ROOT / ".cursor" / "skills" / "bridge" / "helpers" / "impl_report_bridge.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.project.lifecycle import ProjectLifecycleService  # noqa: E402


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print(f"\n>>> {' '.join(str(c) for c in cmd)}")
    completed = subprocess.run(
        cmd,
        cwd=str(cwd or PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n", file=sys.stderr)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed


def execute_gov004_slice3() -> dict[str, object]:
    """MemBase membership repair via ProjectLifecycleService."""
    db = KnowledgeDB(PROJECT_ROOT / "groundtruth.db")
    svc = ProjectLifecycleService(db)
    reason_prefix = "GTKB-GOV-004 slice 3 (bridge/gtkb-gov-004-dangling-membership-repair-slice-3)"
    ops = [
        ("remove", "PROJECT-GTKB-DASHBOARD", "GTKB-DASHBOARD-RETENTION"),
        ("remove", "PROJECT-GTKB-DASHBOARD-RETENTION-POLICY", "GTKB-DASHBOARD-RETENTION"),
        ("add", "PROJECT-GTKB-DASHBOARD-OBSERVABILITY", "GTKB-DASHBOARD-RETENTION"),
        ("remove", "PROJECT-GTKB-MASS-001", "GTKB-MASS-001"),
        ("add", "GTKB-V1-RELEASE-STRATEGY-001", "GTKB-MASS-001"),
    ]
    results: list[dict[str, str]] = []
    for op, project_id, work_item_id in ops:
        change_reason = f"{reason_prefix}: {op} {work_item_id} on {project_id}"
        if op == "remove":
            membership = svc.remove_project_item(project_id, work_item_id, change_reason=change_reason)
        else:
            membership = svc.add_project_item(project_id, work_item_id, change_reason=change_reason)
        results.append(
            {
                "op": op,
                "project_id": project_id,
                "work_item_id": work_item_id,
                "membership_status": str(membership.get("status", "")),
            }
        )
    _run(
        [
            str(GT),
            "backlog",
            "update",
            "GTKB-GOV-004",
            "--related-bridge-threads",
            '["gtkb-project-membership-reconciliation-slice-1-inventory-tool","gtkb-deferred-backlog-metadata-refresh","gtkb-gov-004-inventory-evidence-slice-2","gtkb-gov-004-dangling-membership-repair-slice-3"]',
            "--status-detail",
            "Inventory 2026-07-01: total_non_terminal=186; dangling_or_terminal_project_membership=5 (slice 3 repairs 2 unambiguous: GTKB-DASHBOARD-RETENTION, GTKB-MASS-001). Remaining dangling: WI-4851 + 2 WORKLIST rows. Evidence: .gtkb-state/governance-hardening/inventory-20260701.json.",
            "--owner-approved",
            "--change-reason",
            "GTKB-GOV-004 slice 3 dangling membership repair (dispatch execute-pb-go-entries-20260701).",
        ]
    )
    inv_out = PROJECT_ROOT / ".gtkb-state" / "governance-hardening" / "inventory-post-slice3-20260701.json"
    inv_out.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            str(PYTHON),
            str(PROJECT_ROOT / "scripts" / "inventory_project_membership_reconciliation.py"),
            "--format",
            "json",
            "--output-json",
            str(inv_out),
        ]
    )
    pytest = _run(
        [
            str(PYTHON),
            "-m",
            "pytest",
            "platform_tests/scripts/test_inventory_project_membership_reconciliation.py",
            "-q",
            "--tb=short",
        ]
    )
    show_obs = _run([str(GT), "projects", "show", "PROJECT-GTKB-DASHBOARD-OBSERVABILITY", "--json"])
    show_v1 = _run([str(GT), "projects", "show", "GTKB-V1-RELEASE-STRATEGY-001", "--json"])
    show_gov = _run([str(GT), "backlog", "show", "GTKB-GOV-004", "--json"])
    return {
        "membership_ops": results,
        "inventory_path": str(inv_out),
        "pytest_stdout": pytest.stdout.strip(),
        "projects_show_observability": json.loads(show_obs.stdout),
        "projects_show_v1": json.loads(show_v1.stdout),
        "backlog_show_gov004": json.loads(show_gov.stdout),
    }


def verify_wi4949() -> dict[str, str]:
    """Run WI-4949 verification commands (implementation already in tree)."""
    pytest1 = _run(
        [
            str(PYTHON),
            "-m",
            "pytest",
            "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py",
            "platform_tests/scripts/test_activity_disposition_profiles.py",
            "-q",
            "--tb=short",
        ]
    )
    adapter = _run(
        [
            str(PYTHON),
            str(PROJECT_ROOT / "scripts" / "generate_codex_skill_adapters.py"),
            "--check",
            "--update-registry",
        ]
    )
    return {
        "pytest_stdout": pytest1.stdout.strip(),
        "adapter_check_stdout": adapter.stdout.strip(),
    }


def main() -> int:
    print("=== GOV-004 dangling membership repair slice 3 ===")
    gov_evidence = execute_gov004_slice3()
    evidence_path = PROJECT_ROOT / ".gtkb-state" / "dispatch" / "gov004-slice3-evidence.json"
    evidence_path.write_text(json.dumps(gov_evidence, indent=2), encoding="utf-8")
    print(f"Wrote {evidence_path}")

    print("\n=== WI-4949 envelope sharding verification ===")
    wi4949_evidence = verify_wi4949()
    wi4949_path = PROJECT_ROOT / ".gtkb-state" / "dispatch" / "wi4949-verification-evidence.json"
    wi4949_path.write_text(json.dumps(wi4949_evidence, indent=2), encoding="utf-8")
    print(f"Wrote {wi4949_path}")

    print("\n=== Filing implementation reports (draft scaffold; complete content separately) ===")
    for slug in (
        "gtkb-gov-004-dangling-membership-repair-slice-3",
        "gtkb-envelope-sharding-initial-shard-migration",
    ):
        _run([str(PYTHON), str(IMPL_HELPER), "plan", slug])
    print(
        "\nNext: complete impl report bodies under .gtkb-state/bridge-impl-reports/drafts/ "
        "and file with impl_report_bridge.py file <slug> --content-file <path>"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
