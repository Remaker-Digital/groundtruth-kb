#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Deterministic hygiene guard for `.claude/settings.local.json`.

GTKB-STARTUP-REFRACTOR-001 Slice B (WI-4269), advisory finding F3. The
machine-local Claude settings file is part of the effective startup/runtime
environment but is not credential- or root-boundary-governed by the normal
write gates. This read-only guard scans its `permissions.allow` / `deny` entries
for forbidden pattern classes and exits non-zero (with a redacted report) when
any are present, so the cleaned-up state cannot be silently re-introduced.

Forbidden pattern classes (per `.claude/rules/project-root-boundary.md` and the
credential-safety discipline of `GOV-ARTIFACT-APPROVAL-001`):

- legacy-archive path references (the out-of-root `Claude-Playground` archive),
- credential-shaped literals (access keys, connection strings, secrets/passwords).

The guard NEVER prints a matched value verbatim; it reports the offending
pattern class plus a short redacted fingerprint, so running it is safe in logs.

Exit codes: 0 = clean (or file absent), 1 = violations found, 2 = unreadable.

Authority: `bridge/gtkb-startup-refractor-slice-b-local-settings-hygiene-002.md`
(GO); `GOV-SESSION-SELF-INITIALIZATION-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

# Forbidden pattern classes. Each is (class_name, compiled_regex). Patterns are
# case-insensitive and matched against each allow/deny entry string.
FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("legacy-archive-path", re.compile(r"claude-playground", re.IGNORECASE)),
    ("credential-access-key", re.compile(r"access[_-]?key", re.IGNORECASE)),
    ("credential-connection-string", re.compile(r"connection[_-]?string", re.IGNORECASE)),
    ("credential-secret", re.compile(r"\b(secret|password)\s*=", re.IGNORECASE)),
)

_DEFAULT_REL_PATH = Path(".claude") / "settings.local.json"


def _redacted(value: str) -> str:
    """A non-reversible fingerprint of a matched entry (never the raw value)."""
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    return f"<redacted len={len(value)} sha8={digest}>"


def _entries(settings: dict) -> list[str]:
    """Collect all permission allow/deny entry strings from a settings dict."""
    perms = settings.get("permissions")
    if not isinstance(perms, dict):
        return []
    out: list[str] = []
    for key in ("allow", "deny"):
        seq = perms.get(key)
        if isinstance(seq, list):
            out.extend(str(item) for item in seq)
    return out


def find_violations(settings: dict) -> list[str]:
    """Return redacted violation descriptions for forbidden entries.

    Pure function over a parsed settings dict; the returned strings carry the
    offending pattern class and a redacted fingerprint only.
    """
    violations: list[str] = []
    for entry in _entries(settings):
        for class_name, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(entry):
                violations.append(f"{class_name}: {_redacted(entry)}")
                break
    return violations


def _resolve_path(project_root: Path, override: str | None) -> Path:
    if override:
        return Path(override)
    return project_root / _DEFAULT_REL_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan .claude/settings.local.json for forbidden hygiene patterns.")
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd).")
    parser.add_argument("--path", default=None, help="Explicit settings file path (overrides default).")
    args = parser.parse_args(argv)

    target = _resolve_path(Path(args.project_root), args.path)
    if not target.is_file():
        print(f"local-settings-hygiene: OK (no file at {target})")
        return 0
    try:
        settings = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"local-settings-hygiene: UNREADABLE {target}: {exc}")
        return 2

    violations = find_violations(settings)
    if violations:
        print(f"local-settings-hygiene: {len(violations)} violation(s) in {target}:")
        for v in violations:
            print(f"  - {v}")
        return 1
    print(f"local-settings-hygiene: OK ({target} clean)")
    return 0


if __name__ == "__main__":  # pragma: no cover - command-line entry
    raise SystemExit(main())
