#!/usr/bin/env python3
"""Seed Cursor harness SessionStart relay caches and lifecycle guard."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

OUT_DIR = PROJECT_ROOT / ".cursor" / "gtkb-hooks"
GUARD_PATH = PROJECT_ROOT / "harness-state" / "cursor" / "session-lifecycle-guard.json"
DISPATCH = PROJECT_ROOT / ".cursor" / "gtkb-hooks" / "session_start_dispatch.py"
PYTHON = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
CODEX_LO = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "last-user-visible-startup-lo.md"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_lifecycle_guard() -> None:
    GUARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = _now_iso()
    payload = {
        "armed_at": now,
        "armed_reason": "startup_first_owner_prompt_must_be_discarded",
        "current_subject": "gtkb_infrastructure",
        "discard_next_user_prompt": True,
        "first_wrapup_suppressed": False,
        "startup_guard_id": now,
        "startup_response_pending": False,
    }
    GUARD_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote lifecycle guard: {GUARD_PATH}")


def _write_lo_relay_cache_fallback() -> None:
    """Copy codex LO cache as interim seed when SessionStart dispatch is slow."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CODEX_LO.is_file():
        raise FileNotFoundError(f"missing codex LO cache seed: {CODEX_LO}")
    dst = OUT_DIR / "last-user-visible-startup-lo.md"
    shutil.copy2(CODEX_LO, dst)
    body = dst.read_bytes()
    now = _now_iso()
    meta = {
        "harness_name": "cursor",
        "harness_id": "E",
        "role_mode": "lo",
        "role_profile": "loyal-opposition",
        "role_authority": {
            "interactive_resolved_role": "loyal-opposition",
            "interactive_role_source": "startup disclosure cache role mode lo; authoritative only when selected by the owner transcript/init-keyword path",
            "durable_registry_roles": ["loyal-opposition"],
            "durable_registry_authority": "headless dispatch routing and interactive fallback only; non-overriding when a transcript-defined interactive role is present",
            "authority_mode": "cache_only_pending_init_keyword",
        },
        "generated_at": now,
        "byte_length": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    (OUT_DIR / "last-user-visible-startup-lo.meta.json").write_text(
        json.dumps(meta, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"seeded LO relay cache: {dst}")


def _run_session_start_dispatch() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [str(PYTHON), str(DISPATCH)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    if completed.stdout.strip():
        print(completed.stdout.strip()[:500])
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return completed.returncode


def _verify() -> int:
    required = [
        OUT_DIR / "last-user-visible-startup-lo.md",
        OUT_DIR / "last-user-visible-startup-lo.meta.json",
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        print("missing after bootstrap:")
        for path in missing:
            print(f"  - {path}")
        return 1
    meta = json.loads((OUT_DIR / "last-user-visible-startup-lo.meta.json").read_text(encoding="utf-8"))
    body = (OUT_DIR / "last-user-visible-startup-lo.md").read_bytes()
    ok = meta.get("sha256") == hashlib.sha256(body).hexdigest()
    print("cursor LO cache meta:", json.dumps(meta, indent=2))
    print("sha256 consistent:", ok)
    return 0 if ok else 1


def main() -> int:
    _ensure_lifecycle_guard()
    _write_lo_relay_cache_fallback()
    code = _run_session_start_dispatch()
    if code != 0:
        print(f"session_start_dispatch exited {code} (fallback cache remains)", file=sys.stderr)
    return _verify()


if __name__ == "__main__":
    raise SystemExit(main())
