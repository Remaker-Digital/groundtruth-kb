#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project cursor`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Exact-init session binding (UserPromptSubmit).

Writes the session-init binding at the only point where the literal canonical
init line exists: the owner's prompt. The binding carries the role; there is no
separate attestation. WI-6940 removed that surface because the retirement of
``ADR-SESSION-ROLE-ATTESTATION-SERVICE-001`` forbids retaining it, and
``DCL-SESSION-ROLE-RESOLUTION-001`` v9 resolves role from the immutable binding
alone.

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

Hook transport remains non-blocking, and silence is reserved for prompts that
are not init attempts at all. A recognized exact init that cannot be bound emits
a visible ``systemMessage``, and so does a near-canonical init that binds
nothing, so a session is never left believing it declared a role it does not
hold. A binding that already exists is the normal re-entry case, not a fault.
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

# Deliberately looser than the pre-filter above, and used for nothing except
# deciding whether a rejected prompt deserves an explanation. Matching this and
# not `_INIT_PREFILTER` is the definition of a near miss.
_NEAR_INIT_RE = re.compile(r"^[ \t]*::init\b", re.MULTILINE)


def near_miss_disclosure(prompt: object) -> dict:
    """Explain a near-canonical init that created nothing (WI-6499).

    A prompt that resembles the canonical init but does not match it exactly is
    rejected by ``_INIT_PREFILTER`` and previously returned an empty payload.
    Nothing was wrong with the rejection; the silence was the defect. A session
    that types the init line with anything else in the same message proceeds
    believing it declared a role, and learns otherwise only later, when an
    unrelated governed CLI refuses with a typed ``no_session_binding``. By then
    the cause is several steps behind the symptom.

    This names the miss where it happens. It binds nothing, writes nothing, and
    relaxes no parse: ``_INIT_PREFILTER`` and ``bind_exact_init`` stay strict,
    so a near miss still creates no binding, no session id, and no role.
    """
    if not isinstance(prompt, str) or _NEAR_INIT_RE.search(prompt) is None:
        return {}
    return {
        "systemMessage": (
            "GT-KB saw text resembling the canonical init but not matching it exactly, so no "
            "session binding was created and governed role-sensitive work remains unavailable "
            "for this session. The binding requires the complete message "
            "'::init <gtkb|application> <pb|lo>' and nothing else: no leading or trailing "
            "whitespace, no trailing text, and no additional lines. Send that line as its own "
            "message to establish the binding."
        )
    }


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


def main() -> int:
    """Hook entry point."""
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:  # noqa: BLE001 - malformed payload is not our failure
        return 0

    try:
        prompt = payload.get("prompt") or payload.get("user_prompt") or ""
        if not isinstance(prompt, str) or _INIT_PREFILTER.fullmatch(prompt) is None:
            # Silent for an ordinary prompt, explanatory for a near miss. The
            # rejection itself is unchanged either way.
            print(json.dumps(near_miss_disclosure(prompt)))
            return 0
        init_command = prompt

        project_root = discover_project_root()
        if project_root is not None and str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        try:
            from scripts.gtkb_session_id import (  # noqa: PLC0415
                BRIDGE_WORK_INTENT_ORDER,
                resolve_session_id,
            )

            resolved = resolve_session_id(order=BRIDGE_WORK_INTENT_ORDER)
        except Exception:
            resolved = ""
        # WI-6499 bound the hook-transport id; every consumer resolves the
        # harness env id. Bind what consumers read, so they agree by construction.
        session_id = (resolved or payload.get("session_id") or "").strip()
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
