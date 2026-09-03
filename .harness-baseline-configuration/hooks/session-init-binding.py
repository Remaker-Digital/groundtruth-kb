#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Exact-init role attestation binding (UserPromptSubmit).

Writes the session-init binding and its initial role attestation at the only
point where the literal canonical init line exists: the owner's prompt.

Why this hook exists (WI-6499). ``bind_exact_init`` is the sole writer of the
``session_init_bindings`` table, and its only prior production caller was
``scripts/session_self_initialization.py`` on the SessionStart path. SessionStart
fires *before* the owner types anything, so ``init_command`` is necessarily
empty there and that caller's own guard correctly returns without binding. The
literal ``::init <subject> <role>`` line arrives on the first UserPromptSubmit.
The result was that no code path in a live interactive harness ever wrote a
binding, and every gate requiring one - the work-intent claim, the
implementation-start packet, and verdict filing - failed closed for every
session.

This hook closes that gap without relaxing any check. It passes the owner's
complete prompt straight through to ``bind_exact_init``, which applies the
canonical ``^::init (gtkb|application) (pb|lo)$`` match itself. It never extracts
a valid first line from a larger prompt and never synthesizes a command from
subject, role, registry, environment, or cache.

Note on vocabulary: ``bind_exact_init`` mints its own ``SENV-<uuid>`` surrogate
key for the ``envelope_id`` column. No envelope object is created, read, or
required. The column name is legacy vocabulary only, so this hook does not
depend on the envelope-as-object model.

Hook transport remains non-blocking, but a recognized exact init that cannot be
bound emits a visible ``systemMessage``. A binding that already exists is the
normal re-entry case, not a fault.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Mirrors groundtruth_kb.session.attestation.service._EXACT_INIT_RE. Used only
# as a cheap pre-filter so the common non-init prompt costs no import; the
# service applies the authoritative match.
_INIT_PREFILTER = re.compile(r"^::init (gtkb|application) (pb|lo)$")


def discover_project_root(start: Path | None = None) -> Path | None:
    """Walk upward for the repository marker.

    Depth-independent, unlike a bare ``parents[N]`` index: correct whether this
    module is read from the neutral baseline or from a projected harness tree,
    which sit at different depths (WI-6444).
    """
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / "groundtruth.db").is_file():
            return parent
    return None


def _log_bind_failure(project_root: Path, session_id: str, code: str) -> None:
    """Record an unexpected binding failure without breaking the turn."""
    try:
        log_dir = project_root / ".gtkb-state" / "session-attestation"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "bind-failures.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"session_id": session_id, "code": code, "issuer": "hook:init"}) + "\n")
    except Exception:  # noqa: BLE001 - logging must never break the turn
        pass


def main() -> int:
    """Hook entry point."""
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:  # noqa: BLE001 - malformed payload is not our failure
        return 0

    try:
        prompt = payload.get("prompt") or payload.get("user_prompt") or ""
        if not isinstance(prompt, str) or _INIT_PREFILTER.fullmatch(prompt) is None:
            print(json.dumps({}))
            return 0
        init_command = prompt

        session_id = (payload.get("session_id") or "").strip()
        project_root = discover_project_root()
        if not session_id or project_root is None:
            print(
                json.dumps(
                    {
                        "systemMessage": (
                            "GT-KB recognized the exact init command but could not create its immutable "
                            "session binding because the harness session id or project root is unavailable. "
                            "Governed role-sensitive work remains unavailable for this session."
                        )
                    }
                )
            )
            return 0

        src = project_root / "groundtruth-kb" / "src"
        if src.is_dir() and str(src) not in sys.path:
            sys.path.insert(0, str(src))

        from groundtruth_kb.session.attestation import (  # noqa: PLC0415
            RoleAttestationError,
            bind_exact_init,
        )

        try:
            bind_exact_init(
                project_root / "groundtruth.db",
                native_context_id=session_id,
                init_command=init_command,
            )
        except RoleAttestationError as exc:
            # An already-bound context is the expected re-entry case: the binding
            # is immutable by design, so a second init is a no-op, not a fault.
            if exc.code != "session_already_initialized":
                _log_bind_failure(project_root, session_id, exc.code)
                print(
                    json.dumps(
                        {
                            "systemMessage": (
                                "GT-KB exact-init binding failed with typed result "
                                f"{exc.code!r}; governed role-sensitive work remains unavailable "
                                "for this session."
                            )
                        }
                    )
                )
                return 0
            print(json.dumps({}))
            return 0
    except Exception:  # noqa: BLE001 - transport stays non-blocking, failure stays visible
        print(
            json.dumps(
                {
                    "systemMessage": (
                        "GT-KB exact-init binding failed unexpectedly; governed role-sensitive work "
                        "remains unavailable for this session."
                    )
                }
            )
        )
        return 0

    print(json.dumps({"systemMessage": "GT-KB exact-init session binding established."}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
