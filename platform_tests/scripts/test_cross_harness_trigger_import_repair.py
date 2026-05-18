# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-3360 regression: cross-harness trigger ``groundtruth_kb`` import bootstrap.

Per ``bridge/gtkb-cross-harness-trigger-import-repair-003.md`` (Codex GO at
``-004``), IP-3.

Defect: the PostToolUse/Stop hook registrations invoke
``python scripts/cross_harness_bridge_trigger.py`` with no ``PYTHONPATH`` set.
The trigger's lazy ``import groundtruth_kb`` calls then failed with
``ModuleNotFoundError: No module named 'groundtruth_kb'`` and the trigger
could not dispatch.

Fix (IP-1): a module-level ``sys.path`` bootstrap prepends ``groundtruth-kb/src``
alongside the pre-existing WI-3344 sibling-``scripts/`` bootstrap.

These tests load the trigger module the way the hooks invoke the script — with
``PYTHONPATH`` stripped from the environment — and assert the bootstrap makes
``groundtruth_kb`` importable while preserving the WI-3344 ``scripts/`` entry.
Reverting the IP-1 bootstrap fails both tests.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"
_PACKAGE_SRC = (_PROJECT_ROOT / "groundtruth-kb" / "src").resolve()
_SCRIPTS_DIR = (_PROJECT_ROOT / "scripts").resolve()

# Probe: load the trigger module so its module-level sys.path bootstrap runs,
# then report sys.path and (best-effort) the resolved groundtruth_kb location.
# Loading via importlib runs the module body (the IP-1 bootstrap) without the
# ``if __name__ == "__main__"`` dispatch path, so the probe has no side effects.
_PROBE_SNIPPET = "\n".join(
    [
        "import importlib.util, json, sys",
        f"spec = importlib.util.spec_from_file_location('cht', r'{_SCRIPT_PATH}')",
        "mod = importlib.util.module_from_spec(spec)",
        "sys.modules['cht'] = mod",
        "spec.loader.exec_module(mod)",
        "out = {'sys_path': list(sys.path)}",
        "try:",
        "    import groundtruth_kb",
        "    out['gtkb_file'] = groundtruth_kb.__file__",
        "except ModuleNotFoundError as exc:",
        "    out['gtkb_error'] = str(exc)",
        "print(json.dumps(out))",
    ]
)


def _probe_without_pythonpath() -> dict:
    """Load the trigger module in a subprocess with ``PYTHONPATH`` stripped —
    the bare invocation context of the PostToolUse/Stop hooks — and return the
    reported ``sys.path`` plus the resolved ``groundtruth_kb`` location."""
    assert _SCRIPT_PATH.is_file(), f"trigger script missing at {_SCRIPT_PATH}"
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", _PROBE_SNIPPET],
        env=env,
        capture_output=True,
        text=True,
        cwd=str(_PROJECT_ROOT),
    )
    assert result.returncode == 0, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_trigger_bootstrap_resolves_groundtruth_kb_without_pythonpath() -> None:
    """IP-1: with no ``PYTHONPATH`` set, loading the trigger module runs its
    bootstrap and ``import groundtruth_kb`` resolves from the bootstrapped
    ``groundtruth-kb/src`` rather than raising ModuleNotFoundError.
    """
    probe = _probe_without_pythonpath()
    assert "gtkb_error" not in probe, probe.get("gtkb_error")
    assert "gtkb_file" in probe, probe
    # Resolves from the bootstrapped package root, proving the IP-1 bootstrap
    # (not an unrelated site-packages install) is the resolver.
    gtkb_file = Path(probe["gtkb_file"]).resolve()
    assert gtkb_file.is_relative_to(_PACKAGE_SRC), gtkb_file


def test_trigger_bootstrap_preserves_wi3344_scripts_entry() -> None:
    """IP-1: the WI-3360 ``groundtruth-kb/src`` bootstrap is added alongside the
    pre-existing WI-3344 sibling-``scripts/`` bootstrap — both directories are
    on ``sys.path`` after the module loads, so neither import path regresses.
    """
    probe = _probe_without_pythonpath()
    on_path = {str(Path(p).resolve()) for p in probe["sys_path"] if p}
    assert str(_PACKAGE_SRC) in on_path, probe["sys_path"]
    assert str(_SCRIPTS_DIR) in on_path, probe["sys_path"]
