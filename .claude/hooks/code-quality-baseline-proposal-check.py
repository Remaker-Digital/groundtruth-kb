# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project claude`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
"""Baseline code-quality proposal check (delegating shim).

WI-7289: the baseline manifest now declares ``shell_exec`` for this hook, so it
receives shell-command payloads whose shape the delegated implementation does
not understand. The shim expands each recognized shell write into a native
payload and feeds them to the unchanged implementation one at a time, so the
delegate's verdicts and reasons are untouched.
"""

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
HOOKS = Path(__file__).resolve().parent
if str(HOOKS) not in sys.path:
    sys.path.insert(0, str(HOOKS))

from groundtruth_kb.hooks.code_quality_baseline_proposal_check import main as _delegate  # noqa: E402


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.stdin = io.StringIO(raw)
        return _delegate() or 0

    try:
        from _shell_payload import expand_shell_payload

        candidates = expand_shell_payload(payload, ROOT)
    except Exception:
        candidates = [payload]

    if not candidates:
        # Unrecognized shell command: allow, exactly as before registration.
        print("{}")
        return 0

    for candidate in candidates:
        sys.stdin = io.StringIO(json.dumps(candidate))
        rc = _delegate() or 0
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
