"""Transient LO GO/NO-GO verdict writer (dropbox scratch; not an INSIGHTS report).

Usage: python _lo_verdict_runner.py <slug> <body-file>
Computes the next version for <slug>, then writes the verdict via the governed
gtkb_bridge_writer.write_bridge_file (VERIFIED helper is finalize-only; this
path handles GO/NO-GO proposal-review verdicts). Author metadata is read from
the body's embedded author_* block.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, "groundtruth-kb/src")
sys.path.insert(0, ".")

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

slug = sys.argv[1]
body_file = sys.argv[2]
root = Path(".").resolve()
body = Path(body_file).read_text(encoding="utf-8")

bridge_dir = root / "bridge"
pat = re.compile(re.escape(slug) + r"-(\d{3})\.md$")
versions = []
for p in bridge_dir.glob(slug + "-*.md"):
    m = pat.search(p.name)
    if m:
        versions.append(int(m.group(1)))
if not versions:
    raise SystemExit(f"no existing versions for slug {slug!r}")
next_v = max(versions) + 1

written = write_bridge_file(slug, next_v, body, root)
print(f"WROTE {written} (version {next_v:03d})")
