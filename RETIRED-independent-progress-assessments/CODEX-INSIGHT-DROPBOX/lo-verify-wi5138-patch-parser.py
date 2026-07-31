import sys
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "write_verdict_under_test", ".claude/skills/verify/helpers/write_verdict.py"
)
wv = importlib.util.module_from_spec(spec)
sys.modules["write_verdict_under_test"] = wv
spec.loader.exec_module(wv)

root = Path("E:/GT-KB")
text = Path(
    ".gtkb-state/modernization-db-reconstruction-001/wi5138-pauth-groundtruth.patch"
).read_text(encoding="utf-8")
touched = wv._patch_paths_from_text(text, root)
print("touched paths:", touched)
