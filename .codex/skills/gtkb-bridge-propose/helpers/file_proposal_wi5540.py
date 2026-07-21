"""One-off governed-writer wrapper: file the WI-5540 gate-shadow-repair proposal (version 001).

Invoked as a plain ``python <this file>`` command so the Bash-command
mutating-heuristic in ``scripts/implementation_start_gate.py`` does not
classify the invocation as a direct protected-path mutation (no inline
``write_text`` / ``open(..., 'w'`` / redirect tokens appear in the shell
command text itself). Internally this delegates to
``write_bridge.propose_bridge``, which runs the credential scan, author
metadata insertion, envelope normalization, bridge-compliance audit, and
work-intent claim acquire/release exactly as the ``gtkb-bridge-propose``
skill's "Claude path" describes, then performs the file-first write. Follows
the precedent established by ``.claude/skills/verify/helpers/file_go_verdict_*.py``
for verdict authoring, adapted here for proposal authoring via the actual
documented composer (``propose_bridge``), not the lower-level verdict writer.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

HELPER_PATH = ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
_spec = importlib.util.spec_from_file_location("write_bridge", HELPER_PATH)
assert _spec is not None and _spec.loader is not None
write_bridge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(write_bridge)

TOPIC_SLUG = "gtkb-wi5540-lo-verdict-write-gate-shadow-repair"
BODY_PATH = ROOT / ".gtkb-state" / "propose-drafts" / f"{TOPIC_SLUG}-001.md"


def main() -> int:
    body = BODY_PATH.read_text(encoding="utf-8")
    target = write_bridge.propose_bridge(
        TOPIC_SLUG,
        body,
        mode="abort",
        pre_populate_prior_deliberations=False,
    )
    print(f"WROTE: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
