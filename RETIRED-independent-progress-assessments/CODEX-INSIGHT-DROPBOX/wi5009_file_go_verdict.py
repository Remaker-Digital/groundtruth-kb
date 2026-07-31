# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot driver: file the WI-5009 GO verdict at -002 via the governed writer.

Headless LO-B cannot raw-Write bridge/<slug>-NNN.md (WI-4967 controlled-artifact
guard). This loads the governed helper and calls propose_bridge_codex_non_bypass,
which writes via write_bytes in-process (bypassing the PreToolUse Write hooks by
design) and runs its own bridge-compliance audit.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HELPER = ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
BODY = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5009-go-verdict-002-body.txt"
SLUG = "gtkb-wi5009-spec-before-code-structured-bridge-coverage"

spec = importlib.util.spec_from_file_location("gtkb_write_bridge_helper", HELPER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

body_text = BODY.read_text(encoding="utf-8")
out = mod.propose_bridge_codex_non_bypass(
    SLUG,
    body_text,
    version=2,
    status="GO",
    pre_populate_prior_deliberations=False,
    mode="abort",
)
print("WROTE:", out)
