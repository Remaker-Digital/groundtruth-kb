"""Diagnostic + governed write for the WI-5217 finalization-scoped NO-GO (-008).

Run WITHOUT arguments for diagnostics + anchor-guard dry-run only.
Run WITH `--write` to perform the governed write_bridge_file call.
"""

import os
import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402
from scripts.verdict_evidence_anchor_preflight import (  # noqa: E402
    validate_verdict_evidence_anchors,
    violation_summary,
)

SLUG = "gtkb-wi5217-antigravity-prompt-transport"
REPORT_AUTHOR_SESSION = "019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5217"
BODY_PATH = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5217-nogo-008-body.txt"

body = BODY_PATH.read_text(encoding="utf-8")

# --- next version ---
bridge_dir = ROOT / "bridge"
existing = sorted(bridge_dir.glob(f"{SLUG}-*.md"))
versions = []
for p in existing:
    stem = p.stem
    tail = stem.rsplit("-", 1)[-1]
    if tail.isdigit():
        versions.append(int(tail))
next_version = (max(versions) + 1) if versions else 1
print(f"existing versions: {sorted(versions)}")
print(f"next_version: {next_version}")

# --- session context / independence ---
run_id = os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID")
print(f"GTKB_BRIDGE_POLLER_RUN_ID: {run_id!r}")
print(f"report(007) author session: {REPORT_AUTHOR_SESSION!r}")
print(f"independence ok (differs): {run_id != REPORT_AUTHOR_SESSION and bool(run_id)}")

# --- anchor guard dry-run (raw body, before author injection) ---
violations = validate_verdict_evidence_anchors(body, project_root=ROOT)
print(f"anchor violations: {len(violations)}")
if violations:
    print(violation_summary(violations))

author_metadata = {
    "author_identity": "loyal-opposition/claude/B",
    "author_harness_id": "B",
    "author_session_context_id": run_id,
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": (
        "Claude Code dispatcher-spawned headless Loyal Opposition; resolved_role=loyal-opposition"
    ),
}

if "--write" not in sys.argv:
    print("DRY-RUN ONLY (pass --write to perform the governed write).")
    sys.exit(0)

if violations:
    print("REFUSING to write: anchor violations present.")
    sys.exit(1)
if not run_id or run_id == REPORT_AUTHOR_SESSION:
    print("REFUSING to write: session context missing or non-independent.")
    sys.exit(1)

target = write_bridge_file(
    SLUG,
    next_version,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print(f"WROTE: {target}")
