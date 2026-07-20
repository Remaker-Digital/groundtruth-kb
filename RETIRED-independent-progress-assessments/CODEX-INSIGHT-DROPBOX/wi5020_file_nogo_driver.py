"""One-shot driver: file the WI-5020 NO-GO verdict (-002) via the governed helper.

Raw Write/Edit to bridge/<slug>-NNN.md is hard-blocked post-WI-4967
(GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION). The sanctioned authority path is the
governed helper, which writes via a subprocess and runs its own in-process
bridge-compliance audit.
"""

import sys
from pathlib import Path

# sys.path[0] is this driver's dir (the dropbox); add project root for scripts.*
sys.path.insert(0, ".")
sys.path.insert(0, ".claude/skills/bridge-propose/helpers")

import write_bridge  # noqa: E402

BODY = Path(
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5020-nogo-verdict-body.md"
).read_text(encoding="utf-8")

out = write_bridge.propose_bridge_codex_non_bypass(
    "gtkb-wi5020-retire-event-source-config",
    BODY,
    version=2,
    status="NO-GO",
    pre_populate_prior_deliberations=False,
    mode="abort",
)
print("WROTE", out)
