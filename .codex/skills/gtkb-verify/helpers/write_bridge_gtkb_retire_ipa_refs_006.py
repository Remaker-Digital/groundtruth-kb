"""One-off writer for bridge/gtkb-retire-ipa-refs-rules-skills-006.md.

Mirrors the precedent pattern in writer_script.py / write_bridge_5171.py:
calls scripts.gtkb_bridge_writer.write_bridge_file directly, since the raw
Write tool is hard-blocked for bridge/<slug>-NNN.md (GTKB-CONTROLLED-ARTIFACT-
DIRECT-MUTATION / PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001).
"""

from pathlib import Path

import scripts.gtkb_bridge_writer as w

body_path = Path("E:/GT-KB/.claude/skills/verify/helpers/draft-gtkb-retire-ipa-refs-rules-skills-006-body.md")
body = body_path.read_text(encoding="utf-8")

result = w.write_bridge_file(
    "gtkb-retire-ipa-refs-rules-skills",
    6,
    body,
    Path("E:/GT-KB"),
)
print(f"WROTE: {result}")
