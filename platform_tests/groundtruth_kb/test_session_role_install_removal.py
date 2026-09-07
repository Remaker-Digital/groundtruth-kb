"""TEST-12660 — no route defers or installs a session role for a later session.

Linked acceptance test for WI-7823 (PROJECT-GTKB-WI7823-ROLE-INSTALLATION-REMOVAL),
spec ``DCL-SESSION-ROLE-RESOLUTION-001``.

Canon s0.1 makes the owner's literal ``::init gtkb <pb|lo>`` line, or the init line of a
dispatchable bridge item, the ONLY source of a session role, and forbids inferring role
from "a harness name, model, registry, dispatcher configuration, projection, prior
session, or memory". Canon s4 makes the role immutable for the session context.

SCOPE, per the owner postimage decision recorded on WI-7823 v4 and GO v004: this file
asserts the NARROW postimage, the deferral half of the ROLE axis only.

Deliberately NOT asserted, and preserved:

* ``mode_switch.transaction.apply_role_switch``, the immediate branch of
  ``gt mode set-role``, and the sibling route ``gt harness set-role``. All three write a
  harness-registry routing label under ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` v2
  and are not session-role mutation.
* The whole ``bridge_substrate`` axis. It has its own writer
  ``defer_bridge_substrate_switch``, its own identically-named
  ``--defer-to-next-session`` option on ``gt mode set-bridge-substrate``, and it carries
  no role. ``list_pending``, ``apply_pending`` and the two operator subcommands are
  retained to serve it; removing them would strand a path the GO preserves.
* The ``.gtkb-state`` root under which that preserved queue writes, carried by WI-7172.

All five tests are expected to FAIL before the removal; that red preimage is the point.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SRC = REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb"
CLI = SRC / "cli.py"
PENDING = SRC / "mode_switch" / "pending.py"
WAY_OF_WORKING = REPO_ROOT / ".harness-baseline-configuration" / "rules" / "way-of-working.md"

STARTUP_PATHS = (
    REPO_ROOT / "scripts" / "session_self_initialization.py",
    REPO_ROOT / "scripts" / "session_start_dispatch_core.py",
    REPO_ROOT / "scripts" / "dispatcher_runtime.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _command_block(source: str, command: str) -> str:
    """Return the decorator-and-body slice for one ``mode_group`` subcommand."""
    marker = f'@mode_group.command("{command}")'
    start = source.find(marker)
    assert start != -1, f"mode_group subcommand {command!r} not found in cli.py"
    nxt = source.find("@mode_group.command(", start + len(marker))
    return source[start:] if nxt == -1 else source[start:nxt]


def test_no_cli_option_defers_a_role_change_to_a_later_session() -> None:
    """Condition 1: the set-role command queues no role change for a future session."""
    source = _read(CLI)
    set_role = _command_block(source, "set-role")
    assert "--defer-to-next-session" not in set_role, "gt mode set-role still exposes a defer-to-next-session option"
    assert "defer_role_switch" not in source, "cli.py still imports or calls the deferred role-switch writer"


def test_no_role_switch_record_can_be_created() -> None:
    """Condition 2: the role-switch pending writer is gone from the package."""
    if PENDING.exists():
        assert "def defer_role_switch(" not in _read(PENDING), (
            "defer_role_switch still writes a role-switch record for a later session"
        )


def test_no_session_startup_path_applies_pending_switches() -> None:
    """Condition 3: no startup path drains the pending queue into a new session."""
    offenders = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in STARTUP_PATHS
        if path.exists() and "mode_switch.pending import apply_pending" in _read(path)
    ]
    assert offenders == [], f"session-startup paths still apply pending mode switches: {offenders}"


def test_no_rule_directs_prose_to_toggle_a_next_session_role() -> None:
    """Condition 4: no canonical rule teaches a prose next-session role toggle."""
    text = _read(WAY_OF_WORKING).lower()
    assert "next-session role" not in text, "way-of-working.md still teaches a durable next-session role toggle"
    assert "switch mode next session" not in text


def test_pending_queue_retains_no_role_axis_but_keeps_bridge_substrate() -> None:
    """Condition 5: the shared queue applies no role, and the preserved axis survives."""
    pending = _read(PENDING)
    # Structural, not textual: the module may legitimately name the applier in prose
    # while neither importing nor calling it.
    tree = ast.parse(pending)
    imported = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    assert "apply_role_switch" not in imported, (
        "pending.py still imports the role-switch applier; the queue must carry no role axis"
    )
    called = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "apply_role_switch" not in called, (
        "pending.py still calls the role-switch applier; the queue must carry no role axis"
    )
    # The preserved bridge-substrate operator surface must NOT be collaterally removed.
    for kept in ("def list_pending(", "def apply_pending("):
        assert kept in pending, f"{kept} was removed; the bridge_substrate axis needs it"
    cli = _read(CLI)
    for kept in ('@mode_group.command("list-pending")', '@mode_group.command("apply-pending")'):
        assert kept in cli, f"{kept} was removed; it serves the preserved bridge_substrate axis"
