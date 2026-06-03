"""Claude Code SessionStart hook dispatcher (thin delegating wrapper).

Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272;
bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md, Codex GO)
extracted the shared SessionStart dispatch logic into
``scripts/session_start_dispatch_core.py``. This wrapper sets the Claude-harness
configuration (``HARNESS_NAME``, ``OUT_DIR``) and rebinds the shared dispatch
functions onto this module's namespace so module-level names resolve against
this wrapper. The rebind preserves the SessionStart dispatcher tests'
``monkeypatch.setattr(module, ...)`` contract while the logic lives once in the
shared core. Behavior is identical to the Codex wrapper except ``HARNESS_NAME``
and ``OUT_DIR``.

The drift gate for the shared primitives lives in
``scripts/check_codex_hook_parity.py::_resolution_table_parity_errors``, which
asserts the primitives in the shared core plus per-wrapper delegation +
intentional-difference guards.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import session_start_dispatch_core as _core  # noqa: E402

# Seed this module's namespace with the shared surface (constants, the
# StartupDecision enum, stdlib re-exports, helper imports, and the dispatch
# functions) defined once in the core module.
for _name, _value in vars(_core).items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value

# Claude-harness configuration (the only real per-harness difference).
HARNESS_NAME = "claude"
OUT_DIR = PROJECT_ROOT / ".claude" / "hooks"

# Rebind every shared function onto THIS module's globals so module-level names
# (HARNESS_NAME, OUT_DIR, and test-monkeypatched helpers) resolve against this
# wrapper, preserving the existing SessionStart dispatcher tests'
# monkeypatch-on-module contract while the logic is defined once in the core.
for _name, _value in list(globals().items()):
    if isinstance(_value, types.FunctionType) and getattr(_value, "__module__", None) == _core.__name__:
        _rebound = types.FunctionType(
            _value.__code__, globals(), _value.__name__, _value.__defaults__, _value.__closure__
        )
        # FunctionType sets only __defaults__/__closure__; carry the rest so
        # keyword-only defaults, annotations, and metadata survive the rebind.
        _rebound.__kwdefaults__ = _value.__kwdefaults__
        _rebound.__annotations__ = _value.__annotations__
        _rebound.__qualname__ = _value.__qualname__
        _rebound.__doc__ = _value.__doc__
        _rebound.__dict__.update(_value.__dict__)
        globals()[_name] = _rebound

if __name__ == "__main__":
    raise SystemExit(globals()["main"]())
