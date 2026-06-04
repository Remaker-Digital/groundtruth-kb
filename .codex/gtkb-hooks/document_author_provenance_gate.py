#!/usr/bin/env python3
"""Codex parity wrapper for document_author_provenance_gate.

Delegates to the canonical Claude hook at
``.claude/hooks/document_author_provenance_gate.py``, which already handles
both Write and apply_patch payload shapes. Forwarding stdin and stdout
byte-for-byte guarantees Claude+Codex parity by construction; no patch
reconstruction is needed because the canonical hook extracts new-file content
from ``*** Add File:`` hunks itself.

Source authority: GOV-DOCUMENT-AUTHOR-PROVENANCE-001 (WI-3399); GO verdict
at bridge/gtkb-document-author-provenance-contract-004.md.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_HOOK = PROJECT_ROOT / ".claude" / "hooks" / "document_author_provenance_gate.py"


def main() -> int:
    if not CANONICAL_HOOK.is_file():
        # Fail open: if the canonical hook is missing, do not block writes.
        # An audit run via scripts/check_document_author_metadata.py is the
        # backstop for surfaces not gated at write-time.
        print("{}")
        return 0
    stdin_data = sys.stdin.read()
    result = subprocess.run(
        [sys.executable, str(CANONICAL_HOOK)],
        input=stdin_data,
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
