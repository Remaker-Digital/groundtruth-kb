"""Generate the read-only review packet for the codex-backlog-cleanup window.

Consumes the inventory file produced by
``scripts/generate_codex_backlog_cleanup_inventory.py`` (asserts existence as a
Phase-1 dependency check) and emits an aggregated review packet to
``independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CODEX-BACKLOG-CLEANUP-2026-05-06-REVIEW-PACKET.md``.

Per ``bridge/gtkb-codex-backlog-cleanup-retroactive-review-003.md`` (GO at -004):
- counts by transition type (pre-state -> post-state);
- items flagged as potentially operationally consequential (title heuristic +
  recently-touched-in-bridge heuristic);
- summary statistics (total items, distinct titles, oldest/newest changed_at);
- explicit ``DECISION DEFERRED TO PHASE 2`` footer.

The Path A vs Path B owner choice is explicitly NOT made by this packet; it is
deferred to a future session per the GO conditions.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "groundtruth.db"
DEFAULT_INVENTORY_PATH = (
    PROJECT_ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "CODEX-BACKLOG-CLEANUP-2026-05-06-INVENTORY.md"
)
DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "CODEX-BACKLOG-CLEANUP-2026-05-06-REVIEW-PACKET.md"
)
BRIDGE_DIR = PROJECT_ROOT / "bridge"
CHANGED_BY = "codex-backlog-cleanup"
WINDOW_START = "2026-05-06T18:06:00Z"
WINDOW_END = "2026-05-06T18:10:00Z"
DEFERRED_MARKER = "DECISION DEFERRED TO PHASE 2"

CONSEQUENTIAL_KEYWORDS = (
    "release",
    "security",
    "blocker",
    "deploy",
    "credential",
    "secret",
    "auth",
    "production",
    "incident",
    "rollback",
    "isolation",
    "boundary",
    "approval",
    "verified",
)

BRIDGE_LOOKBACK_DAYS = 7
BRIDGE_WINDOW_END = "2026-05-06"


def _display_path(path: Path) -> str:
    """Render path relative to project root when possible, else absolute."""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def fetch_rows(db_path: Path) -> list[sqlite3.Row]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                cur.id AS wi_id,
                cur.title AS title,
                cur.resolution_status AS post_resolution_status,
                cur.stage AS post_stage,
                cur.changed_at AS changed_at,
                prev.resolution_status AS pre_resolution_status,
                prev.stage AS pre_stage,
                prev.version AS pre_version
            FROM work_items AS cur
            LEFT JOIN work_items AS prev
                ON prev.id = cur.id AND prev.version = cur.version - 1
            WHERE cur.changed_by = ?
              AND cur.changed_at >= ?
              AND cur.changed_at <  ?
            ORDER BY cur.changed_at ASC, cur.id ASC
            """,
            (CHANGED_BY, WINDOW_START, WINDOW_END),
        )
        return list(cur.fetchall())
    finally:
        conn.close()


def transition_label(row: sqlite3.Row) -> str:
    pre = (
        f"{row['pre_resolution_status']} / {row['pre_stage']}"
        if row["pre_version"] is not None
        else "(no prior version)"
    )
    post = f"{row['post_resolution_status']} / {row['post_stage']}"
    return f"{pre} -> {post}"


def title_consequential(title: str | None) -> tuple[bool, list[str]]:
    if not title:
        return (False, [])
    lower = title.lower()
    matched = [kw for kw in CONSEQUENTIAL_KEYWORDS if kw in lower]
    return (bool(matched), matched)


def recent_bridge_threads(bridge_dir: Path) -> set[str]:
    """Return bridge thread basenames touched within the lookback window.

    Heuristic uses filesystem mtime (not git log); this is a coarse signal
    intended only to surface attention candidates, not to make claims.
    """
    if not bridge_dir.exists():
        return set()
    cutoff_dt = datetime.fromisoformat(BRIDGE_WINDOW_END).replace(tzinfo=timezone.utc)
    cutoff = cutoff_dt.timestamp() - (BRIDGE_LOOKBACK_DAYS * 86400)
    threads: set[str] = set()
    for path in bridge_dir.glob("*.md"):
        try:
            if path.stat().st_mtime >= cutoff:
                stem = path.stem
                stem = re.sub(r"-\d{3}$", "", stem)
                threads.add(stem)
        except OSError:
            continue
    return threads


def bridge_touch_hits(wi_id: str, threads: set[str]) -> list[str]:
    """Return bridge thread names whose name contains the WI id substring."""
    if not wi_id:
        return []
    needle = wi_id.lower()
    return sorted(thread for thread in threads if needle in thread.lower())


def render(rows: list[sqlite3.Row], inventory_path: Path) -> str:
    transitions: Counter[str] = Counter()
    distinct_titles: set[str] = set()
    consequential: list[dict] = []
    bridge_threads = recent_bridge_threads(BRIDGE_DIR)
    timestamps: list[str] = []

    for row in rows:
        transitions[transition_label(row)] += 1
        if row["title"]:
            distinct_titles.add(row["title"])
        if row["changed_at"]:
            timestamps.append(row["changed_at"])
        title_hit, keywords = title_consequential(row["title"])
        bridge_hits = bridge_touch_hits(row["wi_id"], bridge_threads)
        if title_hit or bridge_hits:
            consequential.append(
                {
                    "wi_id": row["wi_id"],
                    "title": row["title"] or "",
                    "transition": transition_label(row),
                    "title_keywords": keywords,
                    "bridge_threads": bridge_hits,
                }
            )

    oldest = min(timestamps) if timestamps else "(none)"
    newest = max(timestamps) if timestamps else "(none)"

    lines: list[str] = [
        "# Codex Backlog Cleanup — 2026-05-06 Review Packet",
        "",
        "Generated by: `scripts/generate_codex_backlog_cleanup_review_packet.py`",
        f"Source attribution: `changed_by = '{CHANGED_BY}'`",
        f"Window: `{WINDOW_START}` <= `changed_at` < `{WINDOW_END}`",
        f"Inventory dependency: `{_display_path(inventory_path)}`",
        "",
        "Bridge thread: `bridge/gtkb-codex-backlog-cleanup-retroactive-review` "
        "(GO at -004; this artifact is the Phase-1 review-packet deliverable).",
        "",
        "Read-only review packet. No KB mutation occurred during generation.",
        "",
        "## Summary Statistics",
        "",
        f"- Total work_item changes: {len(rows)}",
        f"- Distinct titles: {len(distinct_titles)}",
        f"- Oldest changed_at: `{oldest}`",
        f"- Newest changed_at: `{newest}`",
        f"- Distinct transition types: {len(transitions)}",
        f"- Items flagged as potentially consequential: {len(consequential)}",
        "",
        "## Counts By Transition Type",
        "",
        "| Transition (pre-state -> post-state) | Count |",
        "|---|---|",
    ]
    for transition, count in sorted(transitions.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{transition}` | {count} |")

    lines.extend(
        [
            "",
            "## Potentially Consequential Items",
            "",
            "Heuristics:",
            "- Title contains one of: `"
            + "`, `".join(CONSEQUENTIAL_KEYWORDS)
            + "`.",
            f"- WI id appears as a substring in any `bridge/` thread filename "
            f"with mtime within {BRIDGE_LOOKBACK_DAYS} days of `{BRIDGE_WINDOW_END}`.",
            "",
            "These flags are advisory signals for owner review only; they do not",
            "assert that the change was wrong, nor do they pre-decide Path A or",
            "Path B.",
            "",
        ]
    )
    if consequential:
        lines.extend(
            [
                "| WI ID | Title | Transition | Title keyword hits | Bridge thread hits |",
                "|---|---|---|---|---|",
            ]
        )
        for item in consequential:
            kw = ", ".join(item["title_keywords"]) if item["title_keywords"] else "—"
            bt = ", ".join(item["bridge_threads"]) if item["bridge_threads"] else "—"
            title = item["title"].replace("|", "\\|")
            lines.append(
                f"| `{item['wi_id']}` | {title} | `{item['transition']}` | {kw} | {bt} |"
            )
    else:
        lines.append("(No items matched the heuristics.)")

    lines.extend(
        [
            "",
            "## Phase Boundary",
            "",
            f"**{DEFERRED_MARKER}.** This Phase-1 packet does NOT decide:",
            "",
            "- Path A (retroactive DELIB capture of the bulk operation as accepted), or",
            "- Path B (selective per-WI revert), or",
            "- Whether to file a forward-fix rule clause in `.claude/rules/operating-model.md`.",
            "",
            "Each of those is a separate bridge proposal filed AFTER owner review of",
            "this inventory + packet.",
            "",
            "---",
            "",
            "*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"ERROR: db not found: {args.db}", file=sys.stderr)
        return 2
    if not args.inventory.exists():
        print(
            f"ERROR: inventory dependency not found: {args.inventory}\n"
            "Run scripts/generate_codex_backlog_cleanup_inventory.py first.",
            file=sys.stderr,
        )
        return 3

    rows = fetch_rows(args.db)
    content = render(rows, args.inventory)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote review packet for {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
