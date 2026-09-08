#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project antigravity`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
"""Hook adapter for GT-KB workstream focus state and guards."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_runtime_import_paths() -> None:
    project_root = _repo_root()
    for path in (project_root / "scripts", project_root / "groundtruth-kb" / "src"):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def _load_shared_module():
    project_root = _repo_root()
    _ensure_runtime_import_paths()
    import workstream_focus  # noqa: PLC0415

    return workstream_focus, project_root


def _payload_prompt(payload: dict) -> str | None:
    prompt = payload.get("user_prompt")
    if not isinstance(prompt, str):
        prompt = payload.get("prompt")
    return prompt if isinstance(prompt, str) else None


def _persist_interactive_session_envelope(payload: dict, project_root: Path) -> bool:
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID"):
        return False
    prompt = _payload_prompt(payload)
    if prompt is None:
        return False

    _ensure_runtime_import_paths()
    from groundtruth_kb.session.envelope import (  # noqa: PLC0415
        EnvelopeError,
        ensure_worker_session,
        parse_canonical_init_keyword,
        resolve_harness_identity,
    )
    from gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id  # noqa: PLC0415

    parsed = parse_canonical_init_keyword(prompt)
    role = parsed.get("role") if parsed is not None else None
    if role is None:
        return False

    payload_session_id = payload.get("session_id")
    session_id = resolve_session_id(
        payload_session_id if isinstance(payload_session_id, str) else None,
        order=MARKER_CONTINUITY_ORDER,
    )
    if not session_id:
        return False

    harness_name = "claude"
    try:
        _, harness_id = resolve_harness_identity(project_root, harness_name=harness_name)
    except EnvelopeError:
        return False
    inherited_name = (os.environ.get("GTKB_HARNESS_NAME") or harness_name).strip().lower() or harness_name
    inherited_id = (os.environ.get("GTKB_HARNESS_ID") or harness_id).strip()
    if inherited_name != harness_name or inherited_id != harness_id:
        return False
    ensure_worker_session(
        project_root,
        harness_name=harness_name,
        harness_id=harness_id,
        session_id=session_id,
        role=role,
        role_source="transcript_init_keyword",
        init_keyword=prompt,
        dispatch_run_id=None,
    )
    return True


def main() -> None:
    try:
        os.environ.setdefault("GTKB_HARNESS_NAME", "claude")
        raw_stdin = sys.stdin.buffer.read()
        payload = json.loads(raw_stdin.decode("utf-8-sig") if raw_stdin else "{}")
        workstream_focus, project_root = _load_shared_module()
        _persist_interactive_session_envelope(payload, project_root)
        json.dump(workstream_focus.handle_hook_payload(payload, project_root), sys.stdout)
    except Exception as exc:  # noqa: BLE001 - hook failures must fail soft
        json.dump(
            {
                "systemMessage": (
                    f"GT-KB workstream focus hook error; default to GT-KB work until the hook is repaired. Error: {exc}"
                )
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()
