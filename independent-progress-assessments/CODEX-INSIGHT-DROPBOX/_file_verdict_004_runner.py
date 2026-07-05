import importlib.util
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
helper_path = ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
spec = importlib.util.spec_from_file_location("gtkb_write_bridge", helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

draft = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "gtkb-sot-singleton-coverage-audit-004-verdict-draft.md"
)
body = draft.read_text(encoding="utf-8")

path = mod.propose_bridge_codex_non_bypass(
    "gtkb-sot-singleton-coverage-audit",
    body,
    version=4,
    status="NO-GO",
    mode="abort",
    bridge_dir=ROOT / "bridge",
    pre_populate_prior_deliberations=False,
)
print("WROTE:", path)
