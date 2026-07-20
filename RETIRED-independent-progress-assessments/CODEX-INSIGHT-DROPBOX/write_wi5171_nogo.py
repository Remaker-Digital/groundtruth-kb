"""Governed writer runner for the WI-5171 post-implementation NO-GO (version 008).

Loyal Opposition (harness B, auto-dispatched) publishes the verdict through the
canonical no-index bridge writer. The verdict body is authored separately and
carries a complete author-metadata block, so ``ensure_author_metadata`` validates
it without invoking the document-authoritative resolver.
"""

import pathlib
import sys
import traceback

ROOT = pathlib.Path("E:/GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

import scripts.gtkb_bridge_writer as w  # noqa: E402

body_path = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5171-nogo-008-body.txt"
body = body_path.read_text(encoding="utf-8")
print(f"body length: {len(body)}", file=sys.stderr)

try:
    written = w.write_bridge_file(
        "gtkb-wi5171-document-authoritative-backlog-writer",
        8,
        body,
        ROOT,
    )
    print(f"WROTE {written}")
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
