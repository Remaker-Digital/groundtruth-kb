#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import msvcrt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge_worker_context import (
    DEFAULT_MAX_DISPATCH_TARGETS,
    PROJECT_DIR,
    build_context_snapshot,
    build_contexts,
    build_prompt,
    context_requires_action,
    repair_terminal_thread_outputs,
    select_dispatch_batch,
)
from bridge_resident_worker import _maybe_clear_failed_residue

HOOKS_DIR = PROJECT_DIR / ".claude" / "hooks"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _append_log(message: str) -> None:
    _append_agent_log("codex", message)


def _agent_model(agent: str) -> str:
    return "opus" if agent == "prime" else "codex"


def _state_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake-state.json"


def _lock_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake.lock"


def _log_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake.log"


def _last_message_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake-last-message.txt"


def _last_stdout_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake-last-stdout.jsonl"


def _last_context_file(agent: str) -> Path:
    return HOOKS_DIR / f".{agent}-bridge-wake-last-context.json"


def _append_agent_log(agent: str, message: str) -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{_now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    with _log_file(agent).open("a", encoding="utf-8") as fh:
        fh.write(line)


def _load_state(agent: str) -> dict:
    try:
        return json.loads(_state_file(agent).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"last_wake_by_message": {}}


def _save_state(agent: str, state: dict) -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    _state_file(agent).write_text(json.dumps(state, indent=2), encoding="utf-8")


class _FileLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._fh = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            self.path.write_bytes(b"\x00")
        self._fh = open(self.path, "r+b")
        self._fh.seek(0)
        msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        return self

    def __exit__(self, *_args):
        if self._fh:
            try:
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            self._fh.close()
            self._fh = None


def _find_codex_exe() -> Path:
    candidate = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))) / "OpenAI" / "Codex" / "bin" / "codex.exe"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(
        f"Codex shim not found at {candidate}. Run scripts/install_codex_exec_shim.ps1 first."
    )


def _find_claude_exe() -> Path:
    resolved = shutil.which("claude")
    if resolved:
        return Path(resolved)
    fallback = Path.home() / ".local" / "bin" / "claude.exe"
    if fallback.exists():
        return fallback
    raise FileNotFoundError("Claude CLI not found on PATH. Install Claude Code CLI first.")


def _invoke_codex(codex_exe: Path, prompt: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(codex_exe),
        "-a",
        "never",
        "exec",
        "-C",
        str(PROJECT_DIR),
        "--sandbox",
        "danger-full-access",
        "--json",
        "--output-last-message",
        str(_last_message_file("codex")),
        prompt,
    ]
    _append_agent_log("codex", f"launching codex exec: {codex_exe}")
    popen_kwargs: dict[str, object] = {
        "cwd": str(PROJECT_DIR),
        "capture_output": True,
        "text": True,
        "timeout": timeout_seconds,
    }
    if os.name == "nt":
        # pythonw.exe runs without a console, but codex.exe is a console app.
        # Without CREATE_NO_WINDOW, Windows allocates a visible terminal host.
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = subprocess.run(
        cmd,
        **popen_kwargs,
    )
    _last_stdout_file("codex").write_text(completed.stdout or "", encoding="utf-8")
    if completed.stderr:
        _append_agent_log("codex", f"codex exec stderr: {completed.stderr.strip()}")
    return completed


def _invoke_prime(claude_exe: Path, prompt: str, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(claude_exe),
        "-p",
        "--model",
        _agent_model("prime"),
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "json",
        prompt,
    ]
    _append_agent_log("prime", f"launching claude print: {claude_exe}")
    popen_kwargs: dict[str, object] = {
        "cwd": str(PROJECT_DIR),
        "capture_output": True,
        "text": True,
        "timeout": timeout_seconds,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    completed = subprocess.run(
        cmd,
        **popen_kwargs,
    )
    _last_stdout_file("prime").write_text(completed.stdout or "", encoding="utf-8")
    _last_message_file("prime").write_text(completed.stdout or "", encoding="utf-8")
    if completed.stderr:
        _append_agent_log("prime", f"claude print stderr: {completed.stderr.strip()}")
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description="Wake a bridge worker via headless exec when bridge work is pending")
    parser.add_argument("--agent", choices=["codex", "prime"], default="codex")
    parser.add_argument("--cadence-minutes", type=int, default=9)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--trigger", default="scheduled")
    parser.add_argument("--message-id", action="append", default=[])
    parser.add_argument("--max-dispatch-targets", type=int, default=DEFAULT_MAX_DISPATCH_TARGETS)
    args = parser.parse_args()

    sys.path.insert(0, str(PROJECT_DIR))
    import prime_bridge_runtime as bridge

    try:
        with _FileLock(_lock_file(args.agent)):
            state = _load_state(args.agent)
            _maybe_clear_failed_residue(
                args.agent,
                bridge,
                state,
                log_fn=lambda message: _append_agent_log(args.agent, message),
            )
            new_items = bridge.list_inbox(agent=args.agent, status="pending", limit=100).get("items", [])
            contexts = build_contexts(
                bridge,
                agent=args.agent,
                explicit_refs=args.message_id,
                new_items=new_items,
                project_dir=PROJECT_DIR,
                log_fn=lambda message: _append_agent_log(args.agent, message),
                max_contexts=args.max_dispatch_targets,
            )
            pending_ids = {
                str(item.get("id") or "").strip()
                for item in new_items
                if str(item.get("id") or "").strip()
            }
            contexts = [
                context
                for context in contexts
                if str((context.get("canonical_message") or {}).get("id") or "").strip() in pending_ids
                or context_requires_action(args.agent, context)
            ]

            batch = select_dispatch_batch(
                contexts,
                new_items,
                max_targets=args.max_dispatch_targets,
            )
            batch_contexts = batch["contexts"]
            batch_new_items = batch["new_items"]
            wake_targets = set(batch["target_ids"])
            deferred_targets = batch["deferred_ids"]

            if not batch_new_items and not batch_contexts:
                _append_agent_log(args.agent, "no pending bridge work; exiting")
                return 0

            if deferred_targets:
                _append_agent_log(
                    args.agent,
                    f"wake batch capped at {args.max_dispatch_targets}; deferred_targets={','.join(deferred_targets)}",
                )

            pre_repair_count = repair_terminal_thread_outputs(
                bridge,
                agent=args.agent,
                target_refs=sorted(wake_targets),
                project_dir=PROJECT_DIR,
                log_fn=lambda message: _append_agent_log(args.agent, message),
            )
            if pre_repair_count > 0:
                _append_agent_log(
                    args.agent,
                    f"pre-dispatch terminal repair handled {pre_repair_count} target(s); re-evaluate bridge queue before heavy worker execution",
                )
                return 0

            payload = build_context_snapshot(
                trigger=args.trigger,
                contexts=batch_contexts,
                new_items=batch_new_items,
            )
            HOOKS_DIR.mkdir(parents=True, exist_ok=True)
            _last_context_file(args.agent).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            prompt = build_prompt(
                args.agent,
                _last_context_file(args.agent),
                batch_new_items,
                batch_contexts,
                project_dir=PROJECT_DIR,
            )
            for message_id in wake_targets:
                state.setdefault("last_wake_by_message", {})[message_id] = _now_iso()
            state["last_triggered_at"] = _now_iso()
            state["last_triggered_ids"] = sorted(wake_targets)
            state["last_trigger"] = args.trigger
            _save_state(args.agent, state)

            if args.agent == "codex":
                completed = _invoke_codex(_find_codex_exe(), prompt, args.timeout_seconds)
            else:
                completed = _invoke_prime(_find_claude_exe(), prompt, args.timeout_seconds)
            repair_terminal_thread_outputs(
                bridge,
                agent=args.agent,
                target_refs=sorted(wake_targets),
                project_dir=PROJECT_DIR,
                log_fn=lambda message: _append_agent_log(args.agent, message),
            )
            _append_agent_log(
                args.agent,
                f"{args.agent} wake exit={completed.returncode} trigger={args.trigger} new={len(batch_new_items)} contexts={len(batch_contexts)}",
            )
            if completed.returncode != 0:
                return completed.returncode
            return 0
    except OSError:
        _append_agent_log(args.agent, "wake lock busy; another run is active")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
