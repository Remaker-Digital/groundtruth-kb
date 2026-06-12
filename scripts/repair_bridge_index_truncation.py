#!/usr/bin/env python3
"""One-shot repair for catastrophic bridge/INDEX.md truncation (fbfda62c).

Restores bridge/INDEX.md from the last known-good git revision and prepends
post-truncation document blocks that are not already present in that baseline.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASELINE_REF = "0b3ae25f"
REPAIR_COMMENT = (
    "<!-- LO bridge repair 2026-06-08: restored INDEX from "
    f"{BASELINE_REF} after catastrophic truncation in fbfda62c; "
    "prepended post-truncation NEW threads only. -->"
)

NEW_THREAD_ORDER = [
    "gtkb-platform-observability-hygiene",
    "gtkb-bridge-kind-taxonomy-stabilization",
    "gtkb-workstream-focus-marker-race-fix",
    "gtkb-mcp-stable-harness-surface-implementation",
    "gtkb-bridge-advisory-message-type-implementation",
    "gtkb-ecosystem-scout-policy-implementation",
    "gtkb-smart-poller-p1-p2-implementation",
    "gtkb-directive-enforcement-p1-p2-combined",
    "gtkb-isolation-phase3-implementation",
    "gtkb-p0-secrets-purge-enforcement",
    "gtkb-ollama-lo-prompt-hardening",
    "gtkb-ollama-dispatch-state-recovery",
    "gtkb-isolation-phase3-occupancy-detection",
    "gtkb-directive-enforcement-p1-p2",
    "gtkb-smart-bridge-trigger-foundation-spike",
]

_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN|ACCEPTED|BLOCKED):\s+(bridge/\S+\.md)\s*$"
)


def _git_show(ref: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{ref}:{path}"],
        cwd=PROJECT_ROOT,
        text=True,
        errors="replace",
    )


def _parse_document_blocks(text: str) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    lines: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("Document: "):
            if current is not None:
                blocks[current] = lines
            current = raw.split(": ", 1)[1].strip()
            lines = [raw]
            continue
        if current is None:
            continue
        if raw.strip() == "":
            lines.append(raw)
            continue
        if raw.startswith("Document: "):
            continue
        if _STATUS_LINE_RE.match(raw.strip()) or raw.startswith("<!--"):
            lines.append(raw)
            continue
        if raw.strip():
            lines.append(raw)
    if current is not None:
        blocks[current] = lines
    return blocks


def _baseline_documents(text: str) -> set[str]:
    return {line.split(": ", 1)[1].strip() for line in text.splitlines() if line.startswith("Document: ")}


def build_repaired_index(*, baseline_text: str, current_text: str) -> str:
    baseline_docs = _baseline_documents(baseline_text)
    current_blocks = _parse_document_blocks(current_text)

    prepend_blocks: list[str] = []
    for slug in NEW_THREAD_ORDER:
        if slug in baseline_docs:
            continue
        block = current_blocks.get(slug)
        if not block:
            raise RuntimeError(f"missing current INDEX block for new thread: {slug}")
        prepend_blocks.append("\n".join(block).rstrip())

    baseline_lines = baseline_text.splitlines()
    header_end = 0
    for idx, line in enumerate(baseline_lines):
        if line.startswith("Document: "):
            header_end = idx
            break
    header = "\n".join(baseline_lines[:header_end]).rstrip()
    body = "\n".join(baseline_lines[header_end:]).strip()

    parts = [header, REPAIR_COMMENT, ""]
    if prepend_blocks:
        parts.append("\n\n".join(prepend_blocks))
        parts.append("")
    parts.append(body)
    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write repaired INDEX to disk.")
    parser.add_argument(
        "--index-path",
        type=Path,
        default=PROJECT_ROOT / "bridge" / "INDEX.md",
        help="Path to bridge/INDEX.md",
    )
    args = parser.parse_args()

    baseline_text = _git_show(BASELINE_REF, "bridge/INDEX.md")
    current_text = args.index_path.read_text(encoding="utf-8")
    repaired = build_repaired_index(baseline_text=baseline_text, current_text=current_text)

    baseline_count = len(_baseline_documents(baseline_text))
    repaired_count = len(_baseline_documents(repaired))
    print(f"baseline_documents={baseline_count}")
    print(f"repaired_documents={repaired_count}")
    print(f"prepended_new_threads={repaired_count - baseline_count}")
    print(f"repaired_lines={len(repaired.splitlines())}")

    if args.apply:
        args.index_path.write_text(repaired, encoding="utf-8", newline="\n")
        print(f"wrote {args.index_path}")
    else:
        print("dry-run only; pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
