"""GT-KB MCP server scaffold + proof-of-pattern read-only tool.

Slice 1 registers exactly one tool, ``gt_status_summary``, which returns a
boundary-safe, authority-labelled snapshot of GT-KB workflow state (bridge
INDEX status counts, MemBase row counts, project root, working-tree-clean
flag, and current harness role).

The server is not registered with any harness in this slice; that lands in
Slice 3 along with the ``.mcp.json`` / Codex config wiring.
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from mcp.server.lowlevel import Server
from mcp import types

from groundtruth_kb.mcp_surface.authority import AuthorityLabel, build_envelope
from groundtruth_kb.mcp_surface.boundary import resolve_safe_path
from groundtruth_kb.mcp_surface.roles import current_role

SERVER_NAME = "gt-kb-mcp"

_BRIDGE_STATUS_RE = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|WITHDRAWN):\s+")


def _bridge_status_counts(project_root: Path) -> dict[str, int]:
    """Return latest-status-per-thread counts from ``bridge/INDEX.md``."""

    index_path = resolve_safe_path("bridge/INDEX.md", root=project_root)
    text = index_path.read_text(encoding="utf-8")
    latest_status_per_thread: dict[str, str] = {}
    current_doc: str | None = None
    for line in text.splitlines():
        if line.startswith("Document: "):
            current_doc = line.split(": ", 1)[1].strip()
            continue
        if not current_doc:
            continue
        match = _BRIDGE_STATUS_RE.match(line)
        if match and current_doc not in latest_status_per_thread:
            latest_status_per_thread[current_doc] = match.group(1)
            current_doc = None
    return dict(Counter(latest_status_per_thread.values()))


def _membase_row_counts(project_root: Path) -> dict[str, int | None]:
    """Return current-state row counts for the canonical MemBase views.

    MemBase tables (``work_items``, ``specifications``, ``deliberations``) are
    append-only and contain all historical versions. The summary surface
    reports current state, which lives in the ``current_*`` views (the canonical
    "latest version per id" projection). Base-table counts overstate current
    workflow state by including historical versions and must not be used here.
    """

    db_path = resolve_safe_path("groundtruth.db", root=project_root)
    keys = ("current_work_items", "current_specifications", "current_deliberations")
    if not db_path.is_file():
        return {key: None for key in keys}
    counts: dict[str, int | None] = {}
    connection = sqlite3.connect(db_path)
    try:
        for view in keys:
            try:
                row = connection.execute(f"SELECT count(*) FROM {view}").fetchone()
                counts[view] = int(row[0]) if row else None
            except sqlite3.OperationalError:
                counts[view] = None
    finally:
        connection.close()
    return counts


def _working_tree_clean(project_root: Path) -> bool | None:
    """Return True if the working tree is clean, False if dirty, None on error."""

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() == ""


def gt_status_summary_payload(project_root: Path) -> dict[str, Any]:
    """Build the ``gt_status_summary`` payload (without the envelope wrap)."""

    return {
        "bridge_status_counts": _bridge_status_counts(project_root),
        "membase_row_counts": _membase_row_counts(project_root),
        "project_root": str(project_root),
        "working_tree_clean": _working_tree_clean(project_root),
        "current_role": current_role(),
    }


def build_status_summary_envelope(project_root: Path) -> dict[str, Any]:
    """Build the full envelope-wrapped ``gt_status_summary`` response."""

    payload = gt_status_summary_payload(project_root)
    return build_envelope(
        authority=AuthorityLabel.GENERATED_SUMMARY,
        payload=payload,
        source_ref="bridge/INDEX.md+groundtruth.db",
    )


def build_server() -> Server:
    """Construct the GT-KB MCP server with the Slice 1 tool registered."""

    server: Server = Server(SERVER_NAME)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="gt_status_summary",
                description=(
                    "Read-only summary of GT-KB workflow state: bridge INDEX "
                    "status counts, MemBase row counts, project root, "
                    "working-tree-clean flag, and current harness role. Returns "
                    "a generated-summary envelope; not authoritative."
                ),
                inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        if name != "gt_status_summary":
            raise ValueError(f"Unknown tool: {name}")
        from groundtruth_kb.mcp_surface.boundary import _resolve_root

        envelope = build_status_summary_envelope(_resolve_root())
        return [types.TextContent(type="text", text=json.dumps(envelope, indent=2))]

    return server


SERVER = build_server()
