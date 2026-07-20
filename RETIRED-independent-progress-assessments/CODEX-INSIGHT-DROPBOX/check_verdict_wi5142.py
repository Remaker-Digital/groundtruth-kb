"""Dry-run anchor + compliance validation for the WI-5142 NO-GO verdict draft."""

from pathlib import Path

from scripts.gtkb_bridge_writer import (
    run_bridge_compliance_audit,
    validate_verdict_evidence_anchors,
    violation_summary,
)

ROOT = Path("E:/GT-KB")
DRAFT = ROOT / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/verdict-body-gtkb-wi5142-hygiene-reclaim-cli-skill-002.md"
TARGET = ROOT / "bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-002.md"

content = DRAFT.read_text(encoding="utf-8")

violations = validate_verdict_evidence_anchors(content, project_root=ROOT)
if violations:
    print("ANCHOR VIOLATIONS:")
    print(violation_summary(violations))
else:
    print("ANCHOR: clean")

try:
    run_bridge_compliance_audit(file_path=TARGET, content=content, project_root=ROOT)
    print("COMPLIANCE: clean")
except Exception as exc:  # noqa: BLE001
    print(f"COMPLIANCE FAIL: {type(exc).__name__}: {exc}")
