# GT-KB Scanner-Safe-Writer PreToolUse Hook (Tier A #2)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Depends on VERIFIED:** `bridge/gtkb-credential-patterns-canonical-010.md` (Tier A #1 — canonical module landed at commit `862045d` on GT-KB main)
**Target repo:** `groundtruth-kb` at current main (`862045d`)

## Summary

New PreToolUse hook that scans content written to `bridge/*.md` files for
credential patterns **before** the write completes. Uses the canonical
credential-patterns module just shipped in Tier A #1. Emits a stable
deny-record JSONL log for downstream metrics collection (#6).

This closes the governance gap where bridge proposals/reviews could
contain leaked credentials that survive credential-scan (Bash hook) and
land on disk before any scan runs.

## Problem

The existing `templates/hooks/credential-scan.py` only guards **Bash**
tool commands. Content written directly via the **Write** tool — including
bridge proposal files, post-impl reports, and review findings — is not
scanned before landing. In practice, this means:

- A subagent or Prime pasting credential values into a bridge proposal
  could commit them to git before any gate catches it.
- Codex `-004` §Evidence Reviewed observed this risk indirectly when
  flagging "AR-key patterns" as sweep-out-of-scope for prose-only edits.
- The parent scope GO `gtkb-operational-skills-tier-a-004.md` condition
  G5 explicitly calls for this hook: "scanner-deny record schema must be
  a stable interface agreed between hook and collector."

## Solution

`templates/hooks/scanner-safe-writer.py` — a PreToolUse hook registered
for the Write tool. Path-scoped to `bridge/*.md` writes. Uses the
canonical scanner from Tier A #1. On credential detection: emits
`permissionDecision: deny` + writes a structured deny record to a log
file.

### Hook delivery (consistent with `credential-scan.py` pattern)

Per Tier A GO condition G2, skill/hook scaffold + adopter install is
explicit. This hook follows the same delivery pattern as
`credential-scan.py` (the scope GO's reference pattern):

1. **File creation**: `templates/hooks/scanner-safe-writer.py`
2. **Scaffold copy**: automatic via glob at
   `src/groundtruth_kb/project/scaffold.py:169-172` (copies
   `templates/hooks/*.py`). No scaffold code change needed.
3. **Upgrade management**: add
   `.claude/hooks/scanner-safe-writer.py` to `_MANAGED_HOOKS` at
   `src/groundtruth_kb/project/upgrade.py:27-34`.
4. **Doctor requirement**: add `scanner-safe-writer.py` to
   `required_hooks` for bridge profile at
   `src/groundtruth_kb/project/doctor.py:318-324`.
5. **Settings registration**: add to PreToolUse list in
   `src/groundtruth_kb/project/scaffold.py:334-339` — this becomes the
   6th PreToolUse hook.
6. **Gitignore entry**: add
   `.claude/hooks/scanner-safe-writer.log` to the scaffold's template
   `.gitignore` (prevents adopter projects from accidentally committing
   the deny-record log).

### Hook logic

```python
#!/usr/bin/env python3
"""PreToolUse hook: scanner-safe-writer.

Scans content passed to Write tool calls targeting bridge/*.md files for
credential patterns. Denies the write and records the deny event if a
pattern matches. Passes all other writes through unchanged.

Uses the canonical catalog from groundtruth_kb.governance.credential_patterns
when available; falls back to inline catalog mirrored from
credential-scan.py. Drift is caught by parity tests.

Emits CANONICAL_CATALOG_USED / FALLBACK_CATALOG_USED markers on stderr.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

try:
    from groundtruth_kb.governance.credential_patterns import (
        Match,
        Scope,
        scan as canonical_scan,
    )
    _catalog_source = "canonical"
    print("CANONICAL_CATALOG_USED", file=sys.stderr)
except ImportError:
    # Inline fallback — mirrored from credential-scan.py's fallback
    # catalog. Parity enforced by test_inline_fallback_parity_across_hooks.
    # ... catalog entries identical to credential-scan.py fallback ...
    _catalog_source = "fallback"
    print("FALLBACK_CATALOG_USED", file=sys.stderr)


BRIDGE_PATH_PATTERN = re.compile(r"(^|[/\\])bridge[/\\][^/\\]+\.md$")
DENY_LOG_PATH = Path(".claude/hooks/scanner-safe-writer.log")


def _is_in_scope(file_path: str) -> bool:
    """True if the Write target is a bridge/*.md file."""
    return bool(BRIDGE_PATH_PATTERN.search(file_path))


def _scan_content(content: str) -> list[dict]:
    """Return list of deny records (may be empty) for credential matches."""
    if _catalog_source == "canonical":
        matches = canonical_scan(content, scope=None)  # scan all scopes
        return [
            {"pattern_name": m.name, "pattern_description": m.description,
             "span": list(m.span)}
            for m in matches
        ]
    # Fallback: iterate inline catalog
    results = []
    for name, pattern, description in _INLINE_CATALOG:
        m = pattern.search(content)
        if m:
            results.append({
                "pattern_name": name,
                "pattern_description": description,
                "span": [m.start(), m.end()],
            })
    return results


def _write_deny_record(file_path: str, hits: list[dict], session_id: str | None) -> None:
    """Append a deny record to the JSONL log. Non-fatal if log write fails."""
    record = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "hook": "scanner-safe-writer",
        "event": "deny",
        "file_path": file_path,
        "catalog_source": _catalog_source,
        "hits": hits,
        "session_id": session_id,
    }
    try:
        DENY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DENY_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError:
        pass  # best-effort; never block the hook on log write failure


def main() -> None:
    # emit_deny/emit_pass helpers — same pattern as credential-scan.py
    try:
        from groundtruth_kb.governance.output import emit_deny, emit_pass
    except ImportError:
        def emit_deny(event: str, reason: str) -> None:  # type: ignore[misc]
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--self-test" in sys.argv:
        # Self-test asserts at least one fallback/canonical hit fires deny
        _self_test()
        return

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    if payload.get("tool_name") != "Write":
        emit_pass()
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    content = tool_input.get("content", "") or tool_input.get("text", "")

    if not file_path or not content:
        emit_pass()
        sys.exit(0)

    if not _is_in_scope(file_path):
        emit_pass()
        sys.exit(0)

    hits = _scan_content(content)
    if not hits:
        emit_pass()
        sys.exit(0)

    session_id = payload.get("session_id")
    _write_deny_record(file_path, hits, session_id)

    first_hit = hits[0]
    emit_deny(
        "PreToolUse",
        f"Credential pattern detected in {file_path}: "
        f"{first_hit['pattern_description']} (pattern={first_hit['pattern_name']}). "
        f"Remove the literal value or reference it by placeholder "
        f"(e.g., [REDACTED:{first_hit['pattern_name']}]) before writing.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
```

## Deny-Record Schema (stable interface per G5)

`schema_version: 1`. Each line in `.claude/hooks/scanner-safe-writer.log`
is a JSON object:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp_utc` | ISO 8601 string, Z-suffixed | When the deny fired |
| `hook` | string (constant) | `"scanner-safe-writer"` |
| `event` | string (constant) | `"deny"` |
| `file_path` | string | Write target (absolute or relative as received) |
| `catalog_source` | string enum | `"canonical"` or `"fallback"` |
| `hits` | list of objects | One per matched pattern |
| `hits[].pattern_name` | string | PatternSpec.name from canonical module |
| `hits[].pattern_description` | string | Human-readable pattern description |
| `hits[].span` | `[int, int]` | Match start, end offsets in content |
| `session_id` | string or null | Claude Code session ID if provided by hook payload |

**Stability contract**: schema is additive — new fields may be added in
future versions; existing fields MUST not be removed or change meaning
without a `schema_version` bump. `gtkb-phase-a-metrics-collector-001`
(#6) consumes this file by reading JSONL and parsing each record against
schema_version 1.

**Non-deny records**: this schema only defines `event: "deny"`. The
collector is not expected to read a pass-through record for every write;
that would be a privacy/performance issue.

## Tests (in `tests/test_scanner_safe_writer.py` — new file)

1. **Self-test**: `python templates/hooks/scanner-safe-writer.py --self-test`
   asserts exit code 0 and deny output for a known AR-key sample.
2. **Path-scope (in-scope)**: Write to `bridge/foo-001.md` with credential
   content → deny, deny record written.
3. **Path-scope (out-of-scope)**: Write to `docs/foo.md` or
   `src/bar.py` with credential content → pass-through (no scan, no
   deny record).
4. **Path-scope (edge cases)**: Write to `bridge/sub/foo.md` (nested) →
   in-scope. Write to `bridgelike/foo.md` → out-of-scope. Write to
   `BRIDGE/foo.md` (case) → in-scope on case-insensitive FS, decided per
   regex (`BRIDGE_PATH_PATTERN` is case-sensitive by default; explicit
   in docstring).
5. **Deny-record schema v1**: deny record is valid JSON with all
   required fields present; `schema_version` is implicit v1 (absent
   field = v1 per contract).
6. **Canonical-mode marker**: `CANONICAL_CATALOG_USED` stderr marker
   present when canonical import succeeds; hook denies correctly.
7. **Fallback-mode marker**: `python -S -I` isolation + inline fallback
   → `FALLBACK_CATALOG_USED` stderr marker present; hook denies
   equivalently.
8. **Cross-hook parity**: inline fallback catalog in
   `scanner-safe-writer.py` matches `credential-scan.py` inline fallback
   (both mirror canonical Bash adapters). Parity enforced by
   `test_inline_fallback_parity_across_hooks` — drift fails the build.
9. **Non-Write tool pass-through**: payload with `tool_name: "Bash"`
   → pass. Payload with `tool_name: "Edit"` → pass (Edit is out of
   scope for v1; future iteration may add).
10. **Log rotation/size**: deny log writes are append-only; no rotation
    in v1. Document this as an open item — collector (#6) reads the
    whole file each run.
11. **OSError tolerance**: if `.claude/hooks/` is read-only (adopter
    edge case), hook still emits deny correctly; log write failure is
    best-effort.

## Scaffold/Upgrade/Doctor Updates

### `src/groundtruth_kb/project/upgrade.py`

```diff
 _MANAGED_HOOKS = [
     ...
     ".claude/hooks/credential-scan.py",
+    ".claude/hooks/scanner-safe-writer.py",
     ...
 ]
```

### `src/groundtruth_kb/project/doctor.py`

```diff
 required_hooks = {"assertion-check.py", "spec-classifier.py"}
 if profile.includes_bridge:
-    required_hooks.update({"destructive-gate.py", "credential-scan.py"})
+    required_hooks.update({"destructive-gate.py", "credential-scan.py", "scanner-safe-writer.py"})
```

### `src/groundtruth_kb/project/scaffold.py`

In `_write_settings_json()` (line 307), extend the PreToolUse list:

```diff
 "PreToolUse": [
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/spec-before-code.py"}]},
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/bridge-compliance-gate.py"}]},
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/kb-not-markdown.py"}]},
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/destructive-gate.py"}]},
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/credential-scan.py"}]},
+    {"hooks": [{"type": "command", "command": f"python {hooks_dir}/scanner-safe-writer.py"}]},
 ],
```

### `.gitignore` template (scaffold-generated)

Add to the template `.gitignore` written by scaffold to adopter projects:

```
# Operational hook logs (do not commit)
.claude/hooks/*.log
```

This catches `scanner-safe-writer.log` and any future hook logs with a
single wildcard. Confirmed no existing tracked `.claude/hooks/*.log`
files.

## Exit Criteria

1. `templates/hooks/scanner-safe-writer.py` exists, executable, passes
   `--self-test`
2. Hook scans Write-tool payload `tool_input.content` against
   bridge/*.md paths; passes through non-bridge writes and non-Write
   tools
3. Uses `groundtruth_kb.governance.credential_patterns.scan()` from
   Tier A #1 as canonical path; inline fallback matches
   credential-scan.py parity
4. `CANONICAL_CATALOG_USED` / `FALLBACK_CATALOG_USED` stderr markers
   emitted on every run
5. Deny records written to `.claude/hooks/scanner-safe-writer.log` in
   stable JSONL schema v1 (see §Deny-Record Schema)
6. `_MANAGED_HOOKS` includes `scanner-safe-writer.py`; `doctor`
   requires it for bridge profile; `settings.json` registers it as
   PreToolUse #6
7. Scaffold `.gitignore` template excludes `.claude/hooks/*.log`
8. New test file `tests/test_scanner_safe_writer.py` with ≥11 tests
   (see §Tests); all pass
9. Full suite: 1074 → 1085+ tests (+11). Ruff clean. mypy --strict
   clean.
10. No modifications to `credential-scan.py`, `_REDACTION_PATTERNS`, or
    any existing Tier A #1 deliverable. This bridge is additive.

## GO Request Questions

1. **Path regex**: is `(^|[/\\])bridge[/\\][^/\\]+\.md$` the right
   scope? Should nested paths like `bridge/sub/foo.md` be in-scope
   (currently: NO — single-segment only)?
2. **Log location**: `.claude/hooks/scanner-safe-writer.log` — OK, or
   prefer a non-hook-colocated path? Gitignore handling is the main
   concern.
3. **Schema v1 completeness**: anything missing for #6 collector needs?
   Candidates: `pid`, `cwd`, `claude_model`, `git_branch`. I've kept v1
   minimal to reduce coupling; #6 can propose v2 extensions.
4. **Catalog scope for scan**: using `scan(scope=None)` (all scopes).
   Should this narrow to `scope=Scope.DB` since bridge content is text
   (not Bash commands)? `Scope.BASH_*` patterns may be redundant on
   prose content. Trade-off: narrower scope = fewer false positives but
   misses patterns like JWT/Azure keys that exist only in Bash scope.
5. **Case sensitivity**: `BRIDGE_PATH_PATTERN` is case-sensitive.
   Adopter projects on case-insensitive filesystems (macOS default,
   Windows) may have `Bridge/` directories. Recommend making pattern
   case-insensitive?

## Prior Deliberations

- `bridge/gtkb-operational-skills-tier-a-004.md` (Phase A scope GO,
  condition G5 mandates this bridge's deny-record schema)
- `bridge/gtkb-credential-patterns-canonical-010.md` (VERIFIED —
  canonical module that this hook imports from)
- `bridge/gtkb-credential-patterns-canonical-007.md` (approved
  proposal — PatternSpec + Scope + adapter design)
- No prior deliberations found for `scanner-safe-writer` specifically
  (this is a new hook)

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns. Sample values in the test section (e.g., `sk-ant-api03-*`)
are described, not instantiated as literals.

## Scope

**This bridge proposes only**: creation of the new hook file and the 4
infrastructure updates (upgrade.py / doctor.py / scaffold.py /
.gitignore template). **NOT in scope**: retroactive scanning of
existing bridge files, the metrics collector (#6), or the skill
bridges (#3-5).

Implementation target: single GT-KB commit touching:
- `templates/hooks/scanner-safe-writer.py` (new)
- `src/groundtruth_kb/project/upgrade.py` (_MANAGED_HOOKS extension)
- `src/groundtruth_kb/project/doctor.py` (required_hooks extension)
- `src/groundtruth_kb/project/scaffold.py` (PreToolUse registration
  + `.gitignore` template)
- `tests/test_scanner_safe_writer.py` (new)
- `tests/test_credential_patterns.py` (extend with cross-hook parity
  test, if that's where it belongs — alternative: extend
  `test_governance_hooks.py`)

## Downstream Unblocks

With this bridge VERIFIED, #3 `gtkb-skill-bridge-propose-001` can
build on the same hook infrastructure for skill-invoked bridge writes.
#5 `gtkb-skill-spec-intake-001` and #6
`gtkb-phase-a-metrics-collector-001` (which reads the deny-record log)
both depend on this bridge's deliverables.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
