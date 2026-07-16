import pathlib
import sys
import traceback

sys.path.insert(0, str(pathlib.Path("E:/GT-KB")))
sys.path.insert(0, str(pathlib.Path("E:/GT-KB/groundtruth-kb/src")))

import scripts.gtkb_bridge_writer as w

body_path = pathlib.Path("E:/GT-KB/.claude/skills/verify/helpers/final-verdict-5171.md")
print("reading", body_path, file=sys.stderr)
body = body_path.read_text(encoding="utf-8")
print("body len", len(body), file=sys.stderr)

try:
    path = w.write_bridge_file(
        "gtkb-wi5171-document-authoritative-backlog-writer",
        2,
        body,
        pathlib.Path("E:/GT-KB"),
    )
    print("WROTE", path)
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
