# GT-KB Canonical Credential-Patterns Module (REVISED-3)

**Status:** REVISED (addresses NO-GO at `-006`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**NO-GO reference:** `bridge/gtkb-credential-patterns-canonical-006.md`
**Supersedes substantively:** `bridge/gtkb-credential-patterns-canonical-005.md`
**Target repo:** `groundtruth-kb` at HEAD `a3fa4d2`

## Summary of Revision

Narrow revision addressing the 2 findings in Codex `-006`. Architecture
from `-005` (PatternSpec dataclass + adapters, non-overloaded Scope,
`python -S` fallback isolation, source-derived floor of 32) is unchanged.
Two specific fixes:

1. **High Finding 1** (sidecar not in delivery paths): **inline the
   fallback catalog inside `credential-scan.py`**. No sidecar file;
   nothing new to add to `_MANAGED_HOOKS` or scaffold/upgrade/doctor.
   Chosen Option 1 from Codex `-006` § 1 Required action.
2. **Medium Finding 2** (mapping test tautology): **capture immutable
   pre-migration source fixture** at
   `tests/fixtures/credential_pattern_source_inventory_pre_migration.json`.
   Mapping assertion reads from fixture, not from post-migration
   `KnowledgeDB._REDACTION_PATTERNS`.

All other `-005` content (PatternSpec dataclass, adapter functions,
non-overloaded Scope API, `python -S` fallback test with
`FALLBACK_CATALOG_USED` marker, parameterized per-pattern tests) is
retained.

## Fix 1 — Inline Fallback (addresses `-006` Finding 1)

### Problem with sidecar design

`-005` used a sidecar `_standalone_fallback.py` adjacent to
`credential-scan.py`. Codex `-006` § 1 verified that:

- Scaffold glob-copies `templates/hooks/*.py` into new projects — sidecar
  would be delivered there ✓
- **Upgrade uses `_MANAGED_HOOKS` explicitly, not glob** — sidecar would
  NOT be delivered on `gt project upgrade` ✗
- **Doctor checks only `destructive-gate.py` and `credential-scan.py`** —
  missing sidecar would not be flagged ✗

Existing adopters upgrading could receive updated `credential-scan.py`
without the sidecar, triggering `ImportError` on the fallback path in
standalone environments.

### Fix: inline catalog inside credential-scan.py

Remove the sidecar entirely. The fallback catalog lives at module scope
inside `credential-scan.py` itself:

```python
# templates/hooks/credential-scan.py

from __future__ import annotations
import json, re, sys

# Attempt canonical import first
try:
    from groundtruth_kb.governance.credential_patterns import (
        bash_credential_pattern_list, bash_output_pattern_list,
    )
    CREDENTIAL_PATTERNS = bash_credential_pattern_list()
    OUTPUT_PATTERNS = bash_output_pattern_list()
    _catalog_source = "canonical"
except ImportError:
    # Inline standalone fallback.
    # Kept in sync with groundtruth_kb.governance.credential_patterns at test
    # time via TestInlineFallbackParity in tests/test_credential_patterns.py.
    # This catalog must not drift from the canonical module; the parity test
    # will fail if a pattern is added/removed/modified in one without the other.
    CREDENTIAL_PATTERNS = [
        (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key ID (AKIA...)"),
        (re.compile(r"\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+"), "Anthropic API key (sk-ant-api...)"),
        # ... full catalog (13 entries preserving current credential-scan.py list)
    ]
    OUTPUT_PATTERNS = [
        (re.compile(r"(echo|printf|cat)\s+.*(AKIA|sk-|sk_live|...)[>|]", re.DOTALL),
         "Credential value piped or redirected to output"),
        (re.compile(r"(export|set)\s+\w*(KEY|SECRET|TOKEN|...)\s*=\s*\S+", re.IGNORECASE),
         "Credential exported as environment variable with literal value"),
    ]
    _catalog_source = "fallback"

# ... rest of hook unchanged
```

### Consequences

**Delivery paths now cover the fallback automatically:**

- Scaffold copies `credential-scan.py` into new projects → fallback
  available by construction
- Upgrade includes `.claude/hooks/credential-scan.py` in `_MANAGED_HOOKS`
  (already) → fallback available by construction after upgrade
- Doctor checks `credential-scan.py` exists → fallback available by
  construction if hook exists
- No new files to track in `_MANAGED_HOOKS`, doctor required-hook list,
  or scaffold glob

**Trade-off**: `credential-scan.py` grows by ~30 lines (the inline
catalog). That's acceptable; the hook is already ~120 lines.

**Test**: parity test ensures the inline catalog matches the canonical
module's `bash_credential_pattern_list() + bash_output_pattern_list()`
output at test time. If either drifts, test fails:

```python
def test_inline_fallback_catalog_matches_canonical():
    """The inline fallback catalog in credential-scan.py must match the
    canonical module's Bash-scoped output. Drift fails the build."""
    import importlib.util

    # Load credential-scan.py as a module
    spec = importlib.util.spec_from_file_location(
        "credential_scan",
        "templates/hooks/credential-scan.py",
    )
    hook_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_module)

    # Load canonical module
    from groundtruth_kb.governance.credential_patterns import (
        bash_credential_pattern_list, bash_output_pattern_list,
    )

    # Compare — canonical path is active (import succeeded), so hook's
    # CREDENTIAL_PATTERNS comes from canonical. Parity is automatic.
    # But for defense-in-depth, inspect the inline catalog text.
    hook_source = Path("templates/hooks/credential-scan.py").read_text()
    # Assertion: parse the inline fallback catalog from source, compare
    # to what the canonical module produces
    inline_creds = _parse_inline_fallback_section(hook_source, "CREDENTIAL_PATTERNS")
    inline_outs = _parse_inline_fallback_section(hook_source, "OUTPUT_PATTERNS")
    canonical_creds = bash_credential_pattern_list()
    canonical_outs = bash_output_pattern_list()

    # Compare regex pattern strings + flags + descriptions
    assert _patterns_equivalent(inline_creds, canonical_creds), (
        "Inline CREDENTIAL_PATTERNS in credential-scan.py has drifted from "
        "groundtruth_kb.governance.credential_patterns.bash_credential_pattern_list(). "
        "Update both or the fallback behavior will diverge from canonical."
    )
    assert _patterns_equivalent(inline_outs, canonical_outs), (
        "Inline OUTPUT_PATTERNS in credential-scan.py has drifted from "
        "groundtruth_kb.governance.credential_patterns.bash_output_pattern_list()."
    )
```

### Removed from `-005`

- `_standalone_fallback.py` sidecar file
- `shutil.copy(fallback_path, isolated_dir / "_standalone_fallback.py")`
  in the fallback test
- Scaffold/upgrade/doctor delivery concerns for the sidecar (no longer
  exists)

### Retained from `-005`

- `python -S` fallback isolation technique
- `FALLBACK_CATALOG_USED` vs `CANONICAL_CATALOG_USED` stderr marker
- Parameterized `@pytest.mark.parametrize("mode", ["canonical", "fallback"])`
  stdin-blocking tests

The fallback test still copies `credential-scan.py` to an isolated dir,
runs with `-S`, and verifies the fallback marker. The only change:
doesn't need to copy a second file because the fallback catalog is inside
the single hook file.

## Fix 2 — Immutable Pre-Migration Source Fixture (addresses `-006` Finding 2)

### Problem with `-005`'s mapping test

`-005` proposed a test that iterates `KnowledgeDB._REDACTION_PATTERNS`
and `_bash_original_CREDENTIAL_PATTERNS` to verify the mapping covers
every source entry. But after migration, these structures become
derived views of the canonical module. The test would become
tautological — verifying the migration preserved what it migrated,
not what was in the pre-migration source.

### Fix: capture pre-migration source at fixture time, assert against fixture

Create a one-time fixture capturing the pre-migration source inventory:

**File**: `tests/fixtures/credential_pattern_source_inventory_pre_migration.json`

**Purpose**: Immutable snapshot of what `src/groundtruth_kb/db.py`
`_REDACTION_PATTERNS` and `templates/hooks/credential-scan.py`
`CREDENTIAL_PATTERNS` / `OUTPUT_PATTERNS` contained AT THE TIME OF
MIGRATION. Written once; never updated.

**Contents** (generated during implementation commit, from
pre-migration source):

```json
{
  "captured_at": "2026-04-17",
  "captured_from_commit": "a3fa4d2",
  "schema_version": 1,
  "db_redaction": [
    {"name": "api_key", "pattern": "(?:api[_-]?key|apikey)\\s*[:=]\\s*['\"]?[\\w\\-]{16,}['\"]?", "flags": "IGNORECASE"},
    {"name": "bearer_header", "pattern": "(?:Authorization\\s*:\\s*)?Bearer\\s+[\\w\\-\\.~+/]+=*", "flags": "IGNORECASE"},
    {"name": "token", "pattern": "(?:token|bearer)\\s*[:=]\\s*['\"]?[\\w\\-\\.]{20,}['\"]?", "flags": "IGNORECASE"},
    {"name": "secret", "pattern": "(?:secret|password|passwd)\\s*[:=]\\s*['\"]?[^\\s'\"]{8,}['\"]?", "flags": "IGNORECASE"},
    {"name": "connection_string", "pattern": "(?:mongodb|postgres|mysql|redis|amqp)://[^\\s\"']+", "flags": "IGNORECASE"},
    {"name": "azure_sas_key", "pattern": "SharedAccessKey=[A-Za-z0-9+/=]{20,}(?:;|$)", "flags": "IGNORECASE"},
    {"name": "github_pat", "pattern": "(?:ghp|gho|ghs|ghr)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}", "flags": "IGNORECASE"},
    {"name": "service_key", "pattern": "(?:sk|pk)[-_](?:live|test|prod)[-_][A-Za-z0-9]{20,}", "flags": "IGNORECASE"},
    {"name": "phone", "pattern": "\\+\\d{10,15}", "flags": ""},
    {"name": "email", "pattern": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "flags": ""},
    {"name": "ip_address", "pattern": "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", "flags": ""},
    {"name": "aws_key", "pattern": "AKIA[0-9A-Z]{16}", "flags": ""},
    {"name": "ar_live_key", "pattern": "\\bar_live_[A-Za-z0-9_-]{10,}", "flags": ""},
    {"name": "ar_user_key", "pattern": "\\bar_user_[A-Za-z0-9_-]{10,}", "flags": ""},
    {"name": "ar_spa_plat_key", "pattern": "\\bar_spa_plat_[A-Za-z0-9_-]{10,}", "flags": ""},
    {"name": "pk_live_key", "pattern": "\\bpk_live_[A-Za-z0-9_-]{10,}", "flags": ""},
    {"name": "arsk_key", "pattern": "\\barsk_[A-Za-z0-9_-]{10,}", "flags": ""},
    {"name": "anthropic_api_key", "pattern": "\\bsk-ant-api\\d+-[A-Za-z0-9_-]{20,}", "flags": ""}
  ],
  "bash_credential": [
    {"description": "AWS access key ID (AKIA...)", "pattern": "AKIA[0-9A-Z]{16}", "flags": ""},
    {"description": "Anthropic API key (sk-ant-api...)", "pattern": "\\bsk-ant-api[0-9]{2}-[a-zA-Z0-9_-]+", "flags": ""},
    {"description": "Secret key (sk-...)", "pattern": "\\bsk-[a-zA-Z0-9]{20,}", "flags": ""},
    {"description": "Stripe live secret key", "pattern": "\\bsk_live_[a-zA-Z0-9]+", "flags": ""},
    {"description": "Stripe test secret key", "pattern": "\\bsk_test_[a-zA-Z0-9]+", "flags": ""},
    {"description": "Stripe restricted key", "pattern": "\\brk_live_[a-zA-Z0-9]+", "flags": ""},
    {"description": "Private key block", "pattern": "-----BEGIN\\s+(RSA\\s+)?PRIVATE\\s+KEY-----", "flags": ""},
    {"description": "OpenSSH private key", "pattern": "-----BEGIN\\s+OPENSSH\\s+PRIVATE\\s+KEY-----", "flags": ""},
    {"description": "Connection string assignment", "pattern": "[Cc]onnection[Ss]tring\\s*=\\s*['\"]?[^\\s;]+", "flags": ""},
    {"description": "Azure Storage account key", "pattern": "AccountKey=[a-zA-Z0-9+/=]{20,}", "flags": ""},
    {"description": "JWT / bearer token", "pattern": "\\beyJ[a-zA-Z0-9_-]{50,}", "flags": ""},
    {"description": "Password passed as command argument", "pattern": "--password\\s*[=\\s]\\s*\\S+", "flags": ""},
    {"description": "Possible password flag (-p)", "pattern": "-p\\s+['\"]?[^\\s]+['\"]?\\s", "flags": ""}
  ],
  "bash_output": [
    {"description": "Credential value piped or redirected to output",
     "pattern": "(echo|printf|cat)\\s+.*(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey).*[>|]",
     "flags": "DOTALL"},
    {"description": "Credential exported as environment variable with literal value",
     "pattern": "(export|set)\\s+\\w*(KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)\\w*\\s*=\\s*\\S+",
     "flags": "IGNORECASE"}
  ]
}
```

**Fixture properties**:
- Written once during `gtkb-credential-patterns-canonical` implementation commit
- `captured_at` and `captured_from_commit` stamped for provenance
- `schema_version: 1` for future evolution
- **Never updated** — if the canonical module legitimately drops a pattern
  (e.g., full fixture-proven equivalence with another), that decision is
  recorded in a separate bridge and a new fixture version is created
- Contents reproduce exactly the current source from `db.py:4158-4189` and
  `credential-scan.py:21-51`

### Mapping-completeness test (refreshed)

```python
import json
from pathlib import Path


def test_all_source_entries_mapped_to_canonical():
    """Every pre-migration source entry must be represented in the
    canonical module via PatternSpec, either as migrated (distinct) or
    deduplicated (fixture-proven equivalent). No source entry may be
    silently dropped."""
    fixture_path = Path("tests/fixtures/credential_pattern_source_inventory_pre_migration.json")
    fixture = json.loads(fixture_path.read_text())
    assert fixture["schema_version"] == 1

    # Load post-migration canonical catalog + mapping report
    from groundtruth_kb.governance.credential_patterns import (
        CREDENTIAL_PATTERNS, PII_PATTERNS, BASH_EXTRAS,
    )
    mapping = parse_source_mapping_report()  # reads docs mapping artifact

    # DB redaction: 18 entries — every one must appear in mapping
    for entry in fixture["db_redaction"]:
        name = entry["name"]
        assert name in mapping.db_entries, (
            f"DB source entry {name!r} is absent from the source-to-canonical "
            f"mapping report. Either migrate it to a PatternSpec or document "
            f"the dedup target with fixture-proven equivalence."
        )
        resolution = mapping.db_entries[name]
        assert resolution in {"migrated", "deduplicated"}, (
            f"DB source entry {name!r} has unexpected resolution: {resolution!r}"
        )

    # Bash credential: 13 entries
    for entry in fixture["bash_credential"]:
        desc = entry["description"]
        assert desc in mapping.bash_credential_entries, (
            f"Bash credential source entry {desc!r} absent from mapping report."
        )

    # Bash output: 2 entries
    for entry in fixture["bash_output"]:
        desc = entry["description"]
        assert desc in mapping.bash_output_entries, (
            f"Bash output source entry {desc!r} absent from mapping report."
        )
```

**Test properties**:
- Reads from fixture (immutable post-migration)
- Validates mapping against pre-migration source, not post-migration
  canonical catalog
- Cannot pass if the migration silently drops an entry

### Documentation

The mapping report at `tests/credential_pattern_source_mapping.md`
(human-readable, sibling to the JSON fixture) gets updated as the
implementation migrates entries. The JSON fixture stays frozen.

## Updated Exit Criteria

Replaces `-005` § Updated Exit Criteria items 8 and 9:

8. `tests/test_credential_patterns.py` contains:
   - Parameterized per-pattern positive+negative tests with count
     `2 * len(actual_canonical_catalog)`
   - Scan-scope behavior tests (4 tests per `-005` Fix 2)
   - **Mapping-completeness test reading from
     `tests/fixtures/credential_pattern_source_inventory_pre_migration.json`**
     (per this revision Fix 2)
   - **Inline fallback parity test** (per this revision Fix 1) proving
     `credential-scan.py` inline catalog matches canonical module output
9. `tests/test_governance_hooks.py` extended with:
   - Canonical-mode self-test
   - Fallback-mode self-test using `python -S` + `FALLBACK_CATALOG_USED`
     stderr marker assertion
   - Parameterized `@pytest.mark.parametrize("mode", ["canonical", "fallback"])`
     stdin-blocking tests
   - First-match ordering parity between modes
   - **No sidecar file to copy**: fallback test stages only
     `credential-scan.py` in the isolated dir

New exit criteria items (added per this revision):

10. `tests/fixtures/credential_pattern_source_inventory_pre_migration.json`
    exists with `schema_version: 1`, captured from commit `a3fa4d2`,
    containing all 33 pre-migration source entries (18 DB + 13 Bash
    credential + 2 Bash output)
11. `credential-scan.py` inline fallback catalog is present (no sidecar
    file); parity test enforces sync with canonical module
12. `_MANAGED_HOOKS`, scaffold glob, and doctor required-hook list are
    unchanged by this implementation (no new delivery-surface entries)

## What's Retained from `-005`

- PatternSpec dataclass + `Scope` enum (without `Scope.ALL`)
- `db_pattern_list()`, `bash_credential_pattern_list()`,
  `bash_output_pattern_list()` adapters
- Public `Match` with no `matched_text` field; `_InternalMatch` private
- `scan(scope=None)` default = scan all patterns
- 4 scan-scope behavior tests
- `python -S` fallback isolation test
- `FALLBACK_CATALOG_USED` stderr marker assertion

## Responses to `-006` Findings

1. **Sidecar delivery gap**: resolved by choosing Option 1 (inline
   fallback). No sidecar exists; nothing to manage in `_MANAGED_HOOKS`,
   scaffold, upgrade, or doctor. Inline-parity test ensures catalog
   stays in sync with canonical.
2. **Mapping tautology**: resolved by immutable pre-migration fixture.
   Test asserts mapping covers fixture entries, not post-migration
   canonical views. Cannot pass if migration drops a source entry.

## GO Request

Codex: please confirm the 2 `-006` findings are addressed:

1. ✅ Inline fallback inside `credential-scan.py`; no sidecar file;
   `_MANAGED_HOOKS`/scaffold/upgrade/doctor unchanged; parity test
   enforces sync
2. ✅ Pre-migration source fixture at
   `tests/fixtures/credential_pattern_source_inventory_pre_migration.json`
   is immutable; mapping test reads from fixture, not from post-migration
   canonical catalog

If approved: I open implementation as a single GT-KB commit per parent
Tier A `-004` GO — module creation, DB migration, Bash hook migration
(inline fallback), fixture creation, all tests (parameterized per-pattern,
scope-behavior, inline-parity, mapping-completeness, `python -S` fallback
runtime).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
