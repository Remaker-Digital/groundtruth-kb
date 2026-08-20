"""Cursor SessionStart hook dispatcher (thin delegating wrapper)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import session_start_dispatch_core as _core  # noqa: E402

for _name, _value in vars(_core).items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value

HARNESS_NAME = "cursor"
OUT_DIR = PROJECT_ROOT / ".cursor" / "gtkb-hooks"

for _name, _value in list(globals().items()):
    if isinstance(_value, types.FunctionType) and getattr(_value, "__module__", None) == _core.__name__:
        _rebound = types.FunctionType(
            _value.__code__, globals(), _value.__name__, _value.__defaults__, _value.__closure__
        )
        _rebound.__kwdefaults__ = _value.__kwdefaults__
        _rebound.__annotations__ = _value.__annotations__
        _rebound.__qualname__ = _value.__qualname__
        _rebound.__doc__ = _value.__doc__
        _rebound.__dict__.update(_value.__dict__)
        globals()[_name] = _rebound

if __name__ == "__main__":
    raise SystemExit(globals()["main"]())
