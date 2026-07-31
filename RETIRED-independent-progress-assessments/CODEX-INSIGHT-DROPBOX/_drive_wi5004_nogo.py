"""One-shot driver: write the WI-5004 NO-GO verdict (-004) via the governed bridge writer."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
BODY = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5004-nogo-004-body.txt"

spec = importlib.util.spec_from_file_location("write_bridge", HELPER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

body = BODY.read_text(encoding="utf-8")
out = mod.propose_bridge_codex_non_bypass(
    "gtkb-wi5004-verified-finalization-include-set-repair",
    body,
    version=4,
    status="NO-GO",
    pre_populate_prior_deliberations=False,
)
print("WROTE:", out)
