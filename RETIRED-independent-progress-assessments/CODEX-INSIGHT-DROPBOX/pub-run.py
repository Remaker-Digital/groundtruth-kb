import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.gtkb_bridge_writer import write_bridge_file

DROP = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"

jobs = [
    ("gtkb-wi5179-harness-diagnostic-mode", 4, "pub-wi5179-004.txt"),
    ("gtkb-wi5180-default-dispatch-metrics-snapshot", 2, "pub-wi5180-002.txt"),
    ("gtkb-wi5186-lo-startup-gate-dcl-reconciliation", 4, "pub-wi5186dcl-004.txt"),
]

for slug, ver, fname in jobs:
    try:
        body = (DROP / fname).read_text(encoding="utf-8")
        target = write_bridge_file(slug, ver, body, ROOT)
        print(f"OK   {slug} -> {target}")
    except Exception as e:
        print(f"FAIL {slug} v{ver}: {type(e).__name__}: {e}")

# peer wi5185-002 disposition
p = ROOT / "bridge" / "gtkb-wi5185-dispatcher-identity-runtime-kind-002.md"
if p.exists():
    first = next((ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()), "")
    ctx = next((ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if "author_session_context_id" in ln), "")
    print(f"wi5185-002 peer verdict: {first} | {ctx}")
