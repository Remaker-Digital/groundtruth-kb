#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook -- Poller Freshness Indicator.

Reads the Claude and Codex scan-status JSON files written by the Windows
scheduled-task pollers (independent-progress-assessments/bridge-automation/),
computes the age of the most-recent update for each, and emits a systemMessage
that instructs Claude to prepend a one-line poller freshness block to the top
of every response.

The goal is silent-failure detection: if the Windows scheduler stops firing
(PS1 syntax error, OAuth expiry, task disabled, worktree confusion), the age
counter will visibly grow with every owner interaction, making the outage
obvious without having to check logs.

DESIGN INVARIANTS (do not violate — read .claude/rules/bridge-essential.md):

1. WORKTREE-SAFE. The hook resolves the repo root via a fallback chain so it
   works identically whether Claude is started from the main checkout, a git
   worktree under .claude/worktrees/, or any other mount point. It never
   assumes CLAUDE_PROJECT_DIR points at the main checkout.

2. FAIL LOUD. The hook MUST emit a systemMessage on every invocation, even if
   status files are missing, git is broken, Python crashes during status parse,
   or any other error occurs. Silent failure is the exact bug this hook exists
   to prevent. Any exit path that produces no systemMessage is a bug.

3. NEVER BLOCK. The hook exits 0 unconditionally. A hook that errors is worse
   than a hook that reports ALARM, because a failing hook is invisible.

Stdin:  JSON {"user_prompt": "...", "session_id": "...", ...}
Stdout: JSON {"systemMessage": "..."}
Exit:   Always 0.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Thresholds for freshness markers (seconds)
FRESH_SEC = 240  # <4 min: healthy (3-min cadence + 1 min grace)
STALE_SEC = 600  # <10 min: warning
# >=10 min: alarm

# Last-resort fallback — used only if git and CLAUDE_PROJECT_DIR both fail
# to resolve a valid repo containing the scan-status files.
#
# Per S307 hardcoded-path directive (no machine-local literals in active code):
# this fallback is supplied via the GTKB_PROJECT_ROOT environment variable,
# not hardcoded. If the env var is unset and every other resolution method
# in _resolve_repo_root() fails, the hook returns ALARM with an explanatory
# message rather than silently using a workstation-specific path.
#
# Setup:
#   PowerShell user profile:  $env:GTKB_PROJECT_ROOT = "E:\path\to\your\GT-KB"
#   Bash shell profile:        export GTKB_PROJECT_ROOT="/c/path/to/your/GT-KB"
#   Documented in:             independent-progress-assessments/bridge-automation/README-ENV-SETUP.md
_env_fallback = os.environ.get("GTKB_PROJECT_ROOT")
HARDCODED_FALLBACK_ROOT: Path | None = (
    Path(_env_fallback) if _env_fallback else None
)

STATUS_REL_PATHS = (
    Path("independent-progress-assessments") / "bridge-automation" / "logs" / "claude-scan-status.json",
    Path("independent-progress-assessments") / "bridge-automation" / "logs" / "codex-scan-status.json",
)


def _resolve_repo_root() -> tuple[Path | None, str]:
    """
    Return (repo_root, method) where method is a short string describing how
    the root was resolved. Returns (None, reason) if nothing worked.

    Fallback chain:
      1. git rev-parse --show-superproject-working-tree (for submodules, rare)
      2. git rev-parse --git-common-dir + parent (main checkout of a worktree)
      3. git rev-parse --show-toplevel (current checkout, may be a worktree)
      4. CLAUDE_PROJECT_DIR env var
      5. HARDCODED_FALLBACK_ROOT

    At each step, verify the candidate contains the status files before
    accepting it. A path that doesn't contain the status files is useless.
    """
    cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    def _has_status_files(root: Path) -> bool:
        return all((root / rel).exists() for rel in STATUS_REL_PATHS)

    # Step 1/2/3: try git
    try:
        # --git-common-dir resolves to the .git directory of the MAIN checkout
        # even when called from a worktree. For a main checkout it returns
        # ".git"; for a worktree it returns an absolute path into the main
        # checkout's .git/worktrees/<name>. The parent of .git is the main
        # repo root.
        proc = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0:
            gcd = Path(proc.stdout.strip())
            if not gcd.is_absolute():
                gcd = (Path(cwd) / gcd).resolve()
            candidate = gcd.parent
            if _has_status_files(candidate):
                return candidate, "git-common-dir"
    except (OSError, subprocess.TimeoutExpired):
        pass

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0:
            candidate = Path(proc.stdout.strip())
            if _has_status_files(candidate):
                return candidate, "git-toplevel"
    except (OSError, subprocess.TimeoutExpired):
        pass

    # Step 4: CLAUDE_PROJECT_DIR
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        candidate = Path(env_dir)
        if _has_status_files(candidate):
            return candidate, "CLAUDE_PROJECT_DIR"

    # Step 5: env-var fallback (set via GTKB_PROJECT_ROOT, not hardcoded).
    # If the env var is unset, HARDCODED_FALLBACK_ROOT is None and we skip.
    if HARDCODED_FALLBACK_ROOT is not None and _has_status_files(HARDCODED_FALLBACK_ROOT):
        return HARDCODED_FALLBACK_ROOT, "env-fallback (GTKB_PROJECT_ROOT)"

    return None, "no-path-contains-status-files"


def _read_status(path: Path) -> dict | None:
    """Read a BOM-safe UTF-8 JSON status file. Returns None on any failure."""
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _age_str(sec: float) -> str:
    """Format an age in seconds as a short human string."""
    s = int(sec)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m{s % 60:02d}s"
    h = s // 3600
    m = (s % 3600) // 60
    return f"{h}h{m:02d}m"


def _marker(sec: float) -> str:
    """Return a leading visual marker based on freshness band."""
    if sec < FRESH_SEC:
        return "OK"
    if sec < STALE_SEC:
        return "WARN"
    return "ALARM"


def _summarize(label: str, status: dict | None) -> tuple[str, str]:
    """Return (one_line_summary, marker). marker is OK/WARN/ALARM/ALARM."""
    if status is None:
        return f"{label}=FILE-MISSING", "ALARM"

    updated = status.get("updatedAtUtc") or ""
    try:
        updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        age_sec = (datetime.now(timezone.utc) - updated_dt).total_seconds()
    except (ValueError, TypeError):
        return f"{label}=UNREADABLE-TIMESTAMP", "ALARM"

    state = status.get("state", "?")
    marker = _marker(age_sec)
    age = _age_str(age_sec)
    # Truncate message to keep the prelude compact
    msg = (status.get("message", "") or "")[:60]
    return f"{label}={marker} {age} ago ({state}) {msg}".rstrip(), marker


def _emit(overall: str, body_lines: list[str]) -> None:
    """
    Emit the systemMessage instructing Claude to prepend the POLLER block.
    Always called exactly once per invocation via a try/except wrapper in main().
    """
    now = datetime.now(timezone.utc).strftime("%H:%M:%SZ")
    block_lines = [f"{overall} @ {now}"] + [f"  {line}" for line in body_lines]
    block = "\n".join(block_lines)
    instruction = (
        f"MANDATORY: Begin your response with a fenced code block containing "
        f"exactly these lines (no additional commentary inside the block):\n"
        f"```\n"
        f"{block}\n"
        f"```\n"
        f"Then proceed with your normal response. This prelude is required on "
        f"every response so the owner can see at a glance whether the bridge "
        f"poller is still firing. Do not omit it and do not apologize for "
        f"including it. Per .claude/rules/bridge-essential.md, bridge uptime "
        f"is the top-priority task; if this block shows WARN or ALARM, stop "
        f"and repair before any other work."
    )
    try:
        json.dump({"systemMessage": instruction}, sys.stdout)
    except Exception:
        pass


def main() -> None:
    # Consume stdin (contents unused)
    try:
        sys.stdin.read()
    except Exception:
        pass

    # Wrap the entire flow in a top-level try/except so a crash still emits a
    # visible ALARM systemMessage. Silent failure is the bug this hook exists
    # to prevent.
    try:
        repo_root, method = _resolve_repo_root()
        if repo_root is None:
            _emit(
                "POLLER ALARM",
                [
                    f"path-resolution={method}",
                    "status files not found via git, CLAUDE_PROJECT_DIR, or fallback",
                ],
            )
            return

        claude_path = repo_root / STATUS_REL_PATHS[0]
        codex_path = repo_root / STATUS_REL_PATHS[1]
        claude = _read_status(claude_path)
        codex = _read_status(codex_path)

        claude_line, claude_marker = _summarize("claude", claude)
        codex_line, codex_marker = _summarize("codex", codex)

        markers = (claude_marker, codex_marker)
        if "ALARM" in markers:
            overall = "POLLER ALARM"
        elif "WARN" in markers:
            overall = "POLLER WARN"
        else:
            overall = "POLLER OK"

        _emit(overall, [claude_line, codex_line])
    except Exception as exc:
        # Last-resort: emit an ALARM with the exception traceback hash so the
        # owner sees that the hook itself is broken instead of silently
        # disappearing. Truncate the traceback to keep the message compact.
        tb = traceback.format_exc().splitlines()[-1][:120]
        _emit(
            "POLLER ALARM",
            [
                f"hook-crashed exc={type(exc).__name__}",
                f"last-tb-line={tb}",
            ],
        )


if __name__ == "__main__":
    main()
