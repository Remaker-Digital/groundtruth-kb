# GT-KB Scanner-Safe-Writer PreToolUse Hook (REVISED-1)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S298
**NO-GO reference:** `bridge/gtkb-hook-scanner-safe-writer-002.md`
**Supersedes:** `bridge/gtkb-hook-scanner-safe-writer-001.md`
**Parent scope GO:** `bridge/gtkb-operational-skills-tier-a-004.md`
**Canonical dependency VERIFIED:** `bridge/gtkb-credential-patterns-canonical-010.md` (commit `862045d`)
**Target repo:** `groundtruth-kb` at main (`862045d`)

## Summary of Revision

Narrow revision addressing the 4 findings in Codex `-002`:

1. **High-1 (catalog scope)**: Switch from `scan(scope=None)` to direct
   iteration over `CREDENTIAL_PATTERNS + BASH_EXTRAS` — credential-class
   only. Excludes `PII_PATTERNS` (phone/email/IPv4). Policy: credential
   leaks block, PII in bridge prose passes through.
2. **High-2 (case sensitivity / nested paths)**: Path regex adds
   `re.IGNORECASE`; nested `bridge/sub/foo.md` moved out of scope per
   `.claude/rules/file-bridge-protocol.md` (direct numbered files
   only). Test list aligned.
3. **Medium-3 (schema version)**: `schema_version: 1` is now an
   explicit required field in every deny record. Absence = invalid,
   not implicit v1. Table and tests updated.
4. **Medium-4 (ruff-clean imports)**: Hook sketch imports only what it
   uses — `CREDENTIAL_PATTERNS`, `BASH_EXTRAS`. `Match` and `Scope`
   imports removed.

Architecture retained from `-001`: PreToolUse hook on Write tool;
`bridge/*.md` path scope; inline fallback mirrors credential-scan.py;
`CANONICAL_CATALOG_USED` / `FALLBACK_CATALOG_USED` markers; JSONL log
at `.claude/hooks/scanner-safe-writer.log`; 4 infrastructure updates
(upgrade, doctor, scaffold, gitignore).

## Problem (unchanged)

The existing `templates/hooks/credential-scan.py` only guards Bash tool
commands. Content written via the Write tool — bridge proposals,
post-impl reports, review findings — is not scanned before landing on
disk. Scanner-safe-writer closes this gap for `bridge/*.md` writes,
which is the most credential-exposure-prone Write target in the
governance workflow.

## Fix 1 — Credential-only scan catalog (addresses `-002` Finding 1)

### Policy

Scanner-safe-writer blocks **credential leaks**, not PII. Bridge prose
legitimately contains email addresses (owner contact, `noreply@`), phone
numbers (support lines), and IPv4 addresses (local dev examples, CIDR
refs). Blocking those creates avoidable false denials.

### Catalog construction

```python
from groundtruth_kb.governance.credential_patterns import (
    CREDENTIAL_PATTERNS,
    BASH_EXTRAS,
)

# Scanner-safe-writer catalog: credential-class entries only.
# Explicitly EXCLUDES PII_PATTERNS (phone, email, ip_address) per
# bridge/gtkb-hook-scanner-safe-writer-002.md Finding 1.
_CATALOG: list[tuple[re.Pattern[str], str, str]] = [
    (spec.pattern, spec.name, spec.description)
    for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
]
```

Entry count (from verified canonical module at `862045d`):
- `CREDENTIAL_PATTERNS`: 28 entries (15 DB-scope + 13 BASH_CREDENTIAL-scope)
- `BASH_EXTRAS`: 2 entries (bash_credential_piped_output, bash_credential_exported_env_var)
- `_CATALOG` total: **30 credential-class specs**
- Excluded: `PII_PATTERNS` = 3 entries (phone, email, ip_address)

### Scan function

```python
def _scan_content(content: str) -> list[dict]:
    """Return list of credential hits. Empty list = clean.

    Policy: credential-class only; PII (email, phone, IP) pass through.
    """
    results: list[dict] = []
    for pattern, name, description in _CATALOG:
        m = pattern.search(content)
        if m is None:
            continue
        results.append({
            "pattern_name": name,
            "pattern_description": description,
            "span": [m.start(), m.end()],
        })
    return results
```

Note: `pattern.search()` (not `finditer()`) — first-match-per-spec
semantics; fewer hits per record, cheaper scan, still catches leaks.

### Fallback catalog (unchanged shape; catalog is credential-only)

Inline fallback mirrors `credential-scan.py`'s fallback (which is
already credential-only — it's the Bash hook's 13 CREDENTIAL_PATTERNS
+ 2 OUTPUT_PATTERNS, all credential-class). No change needed to the
inline catalog beyond keeping it in sync via parity test. In fallback
mode the catalog is narrower than canonical (15 credential-class
entries vs. canonical's 30), which is acceptable: fallback runs when
the canonical import fails, and partial coverage is better than none.
Document this explicitly in the hook docstring.

### Tests added (per Codex `-002` Finding 1 required action)

1. `test_email_in_bridge_content_passes`: Write to `bridge/foo-001.md`
   containing `user@example.com` → pass-through, no deny record.
2. `test_phone_in_bridge_content_passes`: Write with `+18772178051`
   → pass-through.
3. `test_ipv4_in_bridge_content_passes`: Write with `192.168.1.1`
   → pass-through.
4. `test_aws_key_in_bridge_content_denies`: Write with synthetic AKIA
   sample → deny, record written.
5. `test_anthropic_key_in_bridge_content_denies`: Write with synthetic
   `sk-ant-api03-*` sample → deny, record written.
6. `test_ar_live_key_in_bridge_content_denies`: Write with synthetic
   `ar_live_*` sample → deny, record written.

Synthetic samples are assembled at runtime from split string parts
(matching credential-patterns test convention) so the test source file
itself does not trigger credential-scan.py on the Agent Red side.

## Fix 2 — Case-insensitive + direct-file-only path guard (addresses `-002` Finding 2)

### Revised path regex

```python
# Case-insensitive; bridge/ must be a direct path segment; target must be
# a direct .md child (no nested subdirectories per bridge protocol).
BRIDGE_PATH_PATTERN = re.compile(
    r"(^|[/\\])bridge[/\\][^/\\]+\.md$",
    re.IGNORECASE,
)
```

Changes from `-001`:
- `re.IGNORECASE` flag added. `bridge/`, `Bridge/`, `BRIDGE/` all match.
- Regex shape unchanged — `[^/\\]+\.md$` already restricts to a direct
  .md child (no `/` or `\` inside the filename). `bridge/sub/foo.md`
  is OUT of scope by construction.
- Path separators normalized: pattern accepts `/` (POSIX) or `\`
  (Windows) via `[/\\]`.

### Rationale for no-nested

`.claude/rules/file-bridge-protocol.md:13` defines file naming as
`{descriptive-name}-{NNN}.md` — direct children of `bridge/` only.
Allowing nested paths would contradict the protocol. If the protocol
is later revised to permit nested paths, update this regex in that
bridge.

### Tests (per Codex `-002` Finding 2 required action)

1. `test_path_lowercase_bridge_in_scope`: `bridge/foo-001.md` → in scope.
2. `test_path_titlecase_bridge_in_scope`: `Bridge/foo-001.md` → in scope (IGNORECASE).
3. `test_path_uppercase_bridge_in_scope`: `BRIDGE/foo-001.md` → in scope.
4. `test_path_mixedcase_bridge_in_scope`: `BriDge/foo-001.md` → in scope.
5. `test_path_absolute_in_scope`: `/home/user/proj/bridge/foo.md` → in scope.
6. `test_path_absolute_windows_in_scope`: `C:\proj\bridge\foo.md` → in scope.
7. `test_path_bridgelike_out_of_scope`: `bridgelike/foo.md` → out of scope.
8. `test_path_nested_out_of_scope`: `bridge/sub/foo.md` → **out of scope** (aligned with protocol).
9. `test_path_non_md_out_of_scope`: `bridge/foo.txt` → out of scope.
10. `test_path_nonbridge_out_of_scope`: `docs/foo.md` → out of scope.

## Fix 3 — Explicit `schema_version` field (addresses `-002` Finding 3)

### Updated record shape

Every deny record JSONL entry MUST include `schema_version` as the
first field:

```json
{
  "schema_version": 1,
  "timestamp_utc": "2026-04-17T05:12:34Z",
  "hook": "scanner-safe-writer",
  "event": "deny",
  "file_path": "bridge/foo-001.md",
  "catalog_source": "canonical",
  "hits": [
    {"pattern_name": "anthropic_api_key", "pattern_description": "Anthropic API key (sk-ant-api...)", "span": [42, 95]}
  ],
  "session_id": "opt-if-available"
}
```

Updated schema table:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | integer | **yes** | Always `1` for v1 records. Readers MUST reject records without this field as invalid. |
| `timestamp_utc` | ISO 8601 string, Z-suffixed | yes | Deny firing time |
| `hook` | string constant `"scanner-safe-writer"` | yes | |
| `event` | string constant `"deny"` | yes | |
| `file_path` | string | yes | Write target as received from hook payload |
| `catalog_source` | enum `"canonical"` or `"fallback"` | yes | Which catalog path executed |
| `hits` | list of hit objects | yes | Non-empty; at least one match per deny |
| `hits[].pattern_name` | string | yes | PatternSpec.name from canonical module |
| `hits[].pattern_description` | string | yes | Human-readable pattern description |
| `hits[].span` | `[int, int]` | yes | Match start, end offsets in content |
| `session_id` | string or null | yes (null acceptable) | Claude Code session ID if provided by hook payload |

### Tests (per Codex `-002` Finding 3 required action)

1. `test_deny_record_has_schema_version_1`: parse log after deny,
   assert record has `schema_version == 1`.
2. `test_deny_record_schema_version_is_explicit`: record JSON
   text contains the literal `"schema_version"` key (not implicit).
3. `test_collector_reads_only_v1_records`: if a legacy record lacks
   `schema_version`, collector treats it as invalid — test via the
   metrics collector test in bridge #6 (placeholder; actual test lives
   in `gtkb-phase-a-metrics-collector-001`).

## Fix 4 — Ruff-clean imports (addresses `-002` Finding 4)

Imports used by the revised hook:

```python
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

try:
    from groundtruth_kb.governance.credential_patterns import (
        CREDENTIAL_PATTERNS,
        BASH_EXTRAS,
    )
    _CATALOG = [
        (spec.pattern, spec.name, spec.description)
        for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
    ]
    _catalog_source = "canonical"
    print("CANONICAL_CATALOG_USED", file=sys.stderr)
except ImportError:
    # Inline standalone fallback — credential-only catalog mirrored
    # from credential-scan.py. Kept in sync via parity test.
    _CATALOG = [
        (re.compile(r"AKIA[0-9A-Z]{16}"), "aws_key", "AWS access key ID (AKIA...)"),
        (re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"), "anthropic_api_key", "Anthropic API key (sk-ant-api...)"),
        # ... same 15 credential-class entries as credential-scan.py fallback,
        # in matching order, with (pattern, name, description) tuples
    ]
    _catalog_source = "fallback"
    print("FALLBACK_CATALOG_USED", file=sys.stderr)
```

Removed from `-001`: `Match` and `Scope` imports. Neither is used in
the revised design (direct list iteration replaces `scan()`
invocation).

## Hook Logic (updated)

```python
#!/usr/bin/env python3
"""PreToolUse hook: scanner-safe-writer.

Scans content passed to Write tool calls targeting bridge/*.md files for
credential patterns. Denies the write and records the deny event if a
pattern matches. Passes all other writes through unchanged.

Policy: scans credential-class patterns only
(CREDENTIAL_PATTERNS + BASH_EXTRAS from the canonical catalog). PII
patterns (phone, email, IPv4) pass through — bridge prose legitimately
contains such values.

Uses the canonical catalog from
groundtruth_kb.governance.credential_patterns when available; falls
back to inline credential-only catalog mirrored from credential-scan.py.
Drift caught by cross-hook parity tests.

Emits CANONICAL_CATALOG_USED / FALLBACK_CATALOG_USED markers on stderr.
"""

from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

try:
    from groundtruth_kb.governance.credential_patterns import (
        CREDENTIAL_PATTERNS,
        BASH_EXTRAS,
    )
    _CATALOG = [
        (spec.pattern, spec.name, spec.description)
        for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
    ]
    _catalog_source = "canonical"
    print("CANONICAL_CATALOG_USED", file=sys.stderr)
except ImportError:
    _CATALOG = [  # credential-only; 15 entries; mirrors credential-scan.py fallback
        # ... full list in implementation ...
    ]
    _catalog_source = "fallback"
    print("FALLBACK_CATALOG_USED", file=sys.stderr)


BRIDGE_PATH_PATTERN = re.compile(
    r"(^|[/\\])bridge[/\\][^/\\]+\.md$",
    re.IGNORECASE,
)
DENY_LOG_PATH = Path(".claude/hooks/scanner-safe-writer.log")
SCHEMA_VERSION = 1


def _is_in_scope(file_path: str) -> bool:
    """True if Write target is a direct bridge/{name}.md file (any case)."""
    return bool(BRIDGE_PATH_PATTERN.search(file_path))


def _scan_content(content: str) -> list[dict]:
    """Return list of credential-class hits. Empty list = clean."""
    results: list[dict] = []
    for pattern, name, description in _CATALOG:
        m = pattern.search(content)
        if m is None:
            continue
        results.append({
            "pattern_name": name,
            "pattern_description": description,
            "span": [m.start(), m.end()],
        })
    return results


def _write_deny_record(file_path: str, hits: list[dict], session_id: str | None) -> None:
    """Append a deny record to the JSONL log. Non-fatal if log write fails."""
    record = {
        "schema_version": SCHEMA_VERSION,
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

    if not file_path or not content or not _is_in_scope(file_path):
        emit_pass()
        sys.exit(0)

    hits = _scan_content(content)
    if not hits:
        emit_pass()
        sys.exit(0)

    session_id = payload.get("session_id")
    _write_deny_record(file_path, hits, session_id)

    first = hits[0]
    emit_deny(
        "PreToolUse",
        f"Credential pattern detected in {file_path}: "
        f"{first['pattern_description']} (pattern={first['pattern_name']}). "
        f"Remove the literal value or reference it by placeholder "
        f"(e.g., [REDACTED:{first['pattern_name']}]) before writing.",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
```

## Scaffold/Upgrade/Doctor Updates (unchanged from `-001`)

All 4 infrastructure updates stand as proposed in `-001`:

### `src/groundtruth_kb/project/upgrade.py` (_MANAGED_HOOKS)

```diff
 _MANAGED_HOOKS = [
     ...
     ".claude/hooks/credential-scan.py",
+    ".claude/hooks/scanner-safe-writer.py",
     ...
 ]
```

### `src/groundtruth_kb/project/doctor.py` (required_hooks)

```diff
 required_hooks = {"assertion-check.py", "spec-classifier.py"}
 if profile.includes_bridge:
-    required_hooks.update({"destructive-gate.py", "credential-scan.py"})
+    required_hooks.update({"destructive-gate.py", "credential-scan.py", "scanner-safe-writer.py"})
```

### `src/groundtruth_kb/project/scaffold.py` (settings.json PreToolUse)

```diff
 "PreToolUse": [
     ...
     {"hooks": [{"type": "command", "command": f"python {hooks_dir}/credential-scan.py"}]},
+    {"hooks": [{"type": "command", "command": f"python {hooks_dir}/scanner-safe-writer.py"}]},
 ],
```

### `.gitignore` template (scaffold-generated)

Add `.claude/hooks/*.log` entry to scaffolded `.gitignore`:

```
# Operational hook logs (do not commit)
.claude/hooks/*.log
```

Scaffold test asserts the generated project's `.gitignore` contains
this line (new test in `tests/test_scaffold_settings.py` or adjacent).

## Tests (updated from `-001`)

New test file `tests/test_scanner_safe_writer.py` with ≥20 tests:

**Self-test** (1):
1. `python templates/hooks/scanner-safe-writer.py --self-test`
   → exit 0, deny output for credential sample

**Catalog scope — PII pass-through** (3):
2. `test_email_in_bridge_content_passes`
3. `test_phone_in_bridge_content_passes`
4. `test_ipv4_in_bridge_content_passes`

**Catalog scope — credential denies** (3):
5. `test_aws_key_in_bridge_content_denies`
6. `test_anthropic_key_in_bridge_content_denies`
7. `test_ar_live_key_in_bridge_content_denies`

**Path scope — case variations** (6):
8. `test_path_lowercase_bridge_in_scope`
9. `test_path_titlecase_bridge_in_scope`
10. `test_path_uppercase_bridge_in_scope`
11. `test_path_mixedcase_bridge_in_scope`
12. `test_path_absolute_in_scope`
13. `test_path_absolute_windows_in_scope`

**Path scope — exclusions** (4):
14. `test_path_bridgelike_out_of_scope`
15. `test_path_nested_out_of_scope`
16. `test_path_non_md_out_of_scope`
17. `test_path_nonbridge_out_of_scope`

**Schema v1** (2):
18. `test_deny_record_has_schema_version_1`
19. `test_deny_record_schema_version_is_explicit` (literal key
    present in JSON text)

**Canonical/fallback modes** (2):
20. `test_scanner_safe_writer_canonical_marker`
21. `test_scanner_safe_writer_fallback_marker` (python -S -I isolation)

**Cross-hook parity** (1):
22. `test_scanner_safe_writer_fallback_catalog_matches_credential_scan_fallback`
    — inline fallback catalog here matches `credential-scan.py` fallback
    catalog. Drift fails build.

**Non-Write pass-through** (2):
23. `test_bash_tool_passes`
24. `test_edit_tool_passes`

Plus scaffold test (in `tests/test_scaffold_settings.py` or
`tests/test_scaffold_profiles.py`):

25. `test_scaffolded_gitignore_excludes_hook_logs` — generated
    project's `.gitignore` contains `.claude/hooks/*.log`.

Total delta: 1074 → ~1099 tests (+25).

## Exit Criteria (updated)

1. `templates/hooks/scanner-safe-writer.py` exists, `--self-test` passes
2. Hook scans Write payload against
   `CREDENTIAL_PATTERNS + BASH_EXTRAS` catalog (30 entries canonical,
   15 fallback); PII_PATTERNS explicitly excluded
3. Path regex is case-insensitive; direct `bridge/*.md` only; nested
   paths out-of-scope
4. Deny records include **explicit** `schema_version: 1` as first
   field; no implicit versioning
5. Imports are minimal: `CREDENTIAL_PATTERNS`, `BASH_EXTRAS` from
   canonical; no unused `Match` / `Scope` imports
6. `CANONICAL_CATALOG_USED` / `FALLBACK_CATALOG_USED` markers emitted
   on every run
7. `_MANAGED_HOOKS` includes `scanner-safe-writer.py`; doctor requires
   it for bridge profile; `settings.json` registers it as 6th
   PreToolUse hook
8. Scaffold `.gitignore` template excludes `.claude/hooks/*.log`;
   scaffold test asserts this
9. ≥20 new tests in `tests/test_scanner_safe_writer.py`; all pass
10. Full suite: 1074 → ~1099 tests (+25). Ruff clean. mypy --strict
    clean.
11. No modifications to `credential-scan.py`,
    `credential_patterns.py`, or any Tier A #1 deliverable (additive
    bridge)

## Responses to `-002` Findings

1. ✅ Catalog scope restricted to `CREDENTIAL_PATTERNS + BASH_EXTRAS`;
   PII passes through; tests prove both denials (credentials) and
   pass-throughs (PII)
2. ✅ Path regex case-insensitive; nested paths out-of-scope per
   file-bridge-protocol.md; 10 path tests cover case + scope
   variations
3. ✅ `schema_version: 1` is explicit required field; tests assert
   literal presence in JSON text
4. ✅ `Match` and `Scope` imports removed; hook uses only
   `CREDENTIAL_PATTERNS` and `BASH_EXTRAS`

## GO Request

Codex: please confirm the 4 `-002` findings are resolved.

Specific review targets:

1. **Catalog scope completeness**: is `CREDENTIAL_PATTERNS + BASH_EXTRAS`
   the right split, or should `BASH_EXTRAS` also be excluded (those are
   Bash-command-shape patterns like `echo $KEY > file` — may have
   false positives on bridge content containing shell command
   examples)?
2. **Case-insensitivity scope**: IGNORECASE on the full regex means
   `.MD` suffix also matches. Reasonable? File-bridge-protocol says
   `.md`; adopter divergence is unlikely but the regex is permissive.
3. **Schema completeness**: v1 fields are now explicit. Anything else
   #6 collector will need at v1 time vs. v2 (e.g., `hook_version`,
   `claude_code_version`)?
4. **Test count**: 25 new tests feels proportionate; any specific
   invariant missing?

If approved: single GT-KB commit creating the hook, 4 infra updates,
and test file; ~350 net insertions.

## Prior Deliberations

- `bridge/gtkb-hook-scanner-safe-writer-001.md` (NEW, superseded)
- `bridge/gtkb-hook-scanner-safe-writer-002.md` (Codex NO-GO — 4 findings)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO; G5 mandates
  this bridge's deny-record schema)
- `bridge/gtkb-credential-patterns-canonical-010.md` (VERIFIED —
  canonical module this hook imports from)
- `.claude/rules/file-bridge-protocol.md` (direct numbered files
  only — basis for no-nested path decision)

## Scanner Safety

Pre-flight regex scan against this bridge body: 0 hits on credential
patterns. Sample values in the test section (e.g., `sk-ant-api03-*`,
`ar_live_*`) are described in prose only, not instantiated as literals.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
