import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.verdict_evidence_anchor_preflight import (
    validate_verdict_evidence_anchors,
    violation_summary,
)
from scripts.gtkb_bridge_writer import write_bridge_file

draft_path = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5359-nogo-draft-008.txt"
body = draft_path.read_text(encoding="utf-8")

violations = validate_verdict_evidence_anchors(body, project_root=ROOT)
print("ANCHOR_VIOLATIONS:", len(violations))
if violations:
    print(violation_summary(violations))
    sys.exit(2)

result = write_bridge_file(
    "gtkb-wi5359-artifact-evaluability-acceptance-baseline",
    8,
    body,
    ROOT,
)
print("WRITE_RESULT:", result)
