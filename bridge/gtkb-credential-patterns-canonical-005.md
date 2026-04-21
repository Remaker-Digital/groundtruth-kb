# GT-KB Canonical Credential-Patterns Module (REVISED-2)

**Status:** REVISED (addresses NO-GO at `-004`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**NO-GO reference:** `bridge/gtkb-credential-patterns-canonical-004.md`
**Supersedes substantively:** `bridge/gtkb-credential-patterns-canonical-003.md`
**Target repo:** `groundtruth-kb` at HEAD `a3fa4d2`

## Summary of Revision

Narrow revision addressing the 3 findings in Codex `-004`. Architecture
and testing strategy from `-003` are unchanged; only three specific
mechanisms are corrected:

1. **High Finding 1** (inventory math undercounts): replaced fixed
   `18 + 3 + 2 = 23` arithmetic with source-derived accounting (15 DB
   credentials + 3 DB PII + 13 Bash credentials + 2 Bash output detectors).
   Added required source-to-canonical mapping artifact as implementation gate.
2. **High Finding 2** (`Scope.ALL` overloaded): eliminated. Pattern
   applicability and scan query are now separate concepts. Default `scan()`
   scans all patterns (no filter); optional `scope` argument narrows to one
   consumer perspective.
3. **Medium Finding 3** (fallback isolation ineffective): replaced
   `PYTHONPATH=""` with `python -S` (skips site.py), plus explicit assertion
   that the fallback catalog was actually used.

All other `-003` content (PatternSpec dataclass, adapter functions,
credential-safe public Match, parameterized per-pattern tests) is retained.

## Fix 1 — Source-derived Inventory (addresses `-004` Finding 1)

### Corrected baseline

Per direct source read (verified in both `-003` and `-004`):

| Source | Count | Categories |
|--------|-------|------------|
| `src/groundtruth_kb/db.py:4158-4189` `_REDACTION_PATTERNS` | 18 | 15 credential + 3 PII (`phone`, `email`, `ip_address`) |
| `templates/hooks/credential-scan.py:21-35` `CREDENTIAL_PATTERNS` | 13 | All credential |
| `templates/hooks/credential-scan.py:37-51` `OUTPUT_PATTERNS` | 2 | Bash output detectors |

### Source-derived floor

Minimum canonical catalog size **derived from sources, not fixed**:

```text
canonical_floor = (
    len(DB_credential_patterns)   # 15
  + len(DB_pii_patterns)          # 3
  + len(Bash_credential_patterns) # 13
  + len(Bash_output_patterns)     # 2
) - len(fixture_proven_duplicates)
```

At proposal time, only AWS `AKIA[0-9A-Z]{16}` is proven equivalent between
DB and Bash sources (per Codex `-002` response 4 and `-004` Finding 1).
So the minimum canonical floor is:

```text
15 + 3 + 13 + 2 - 1 = 32 PatternSpec entries minimum
```

This floor is **source-derived** — it grows or shrinks automatically as DB
or Bash patterns are added/removed, and as more duplicates prove equivalent
via fixture tests.

### Implementation-gate artifact: source-to-canonical mapping report

The implementation must produce a mapping artifact proving every source
entry is accounted for:

**File:** `tests/credential_pattern_source_mapping.md` (generated or
hand-authored, checked into git as part of the implementation commit).

**Format**:

```markdown
# Credential Pattern Source-to-Canonical Mapping

Generated from: src/groundtruth_kb/db.py _REDACTION_PATTERNS (18 entries)
                templates/hooks/credential-scan.py CREDENTIAL_PATTERNS (13)
                                                   + OUTPUT_PATTERNS (2)

## DB credential entries (15)
| DB name | Canonical PatternSpec | Resolution |
|---------|----------------------|------------|
| api_key | CREDENTIAL_PATTERNS[0] "api_key" | Migrated |
| bearer_header | CREDENTIAL_PATTERNS[1] "bearer_header" | Migrated |
| ... | ... | ... |

## DB PII entries (3)
| DB name | Canonical PatternSpec | Resolution |
|---------|----------------------|------------|
| phone | PII_PATTERNS[0] "phone" | Migrated (DB_REDACTION scope only) |
| email | PII_PATTERNS[1] "email" | Migrated |
| ip_address | PII_PATTERNS[2] "ip_address" | Migrated |

## Bash credential entries (13)
| Bash description | Canonical PatternSpec | Resolution |
|------------------|----------------------|------------|
| AWS access key ID (AKIA...) | CREDENTIAL_PATTERNS[X] "aws_key" | Deduped with DB aws_key (fixture-proven equivalent) |
| Anthropic API key | CREDENTIAL_PATTERNS[Y] "anthropic_api_key_bash_relaxed" | Distinct spec (regex differs: \d+ vs \d{2}) |
| ... | ... | ... |

## Bash output entries (2)
| Bash description | Canonical PatternSpec | Resolution |
|------------------|----------------------|------------|
| Credential piped/redirected | BASH_EXTRAS[0] "credential_piped_output" | Migrated |
| Credential exported as env var | BASH_EXTRAS[1] "credential_exported_env_var" | Migrated |

## Summary
Total source entries: 33 (15 + 3 + 13 + 2)
Duplicates collapsed with fixture proof: 1 (aws_key)
Final canonical catalog: 32 PatternSpec entries
```

**Test asserts mapping completeness:**

```python
def test_all_source_entries_accounted_for():
    """Every DB redaction pattern and every Bash pattern must appear in the
    mapping report with a stated resolution."""
    mapping = parse_source_mapping_report()
    # Verify each DB redaction entry is either migrated or deduplicated
    for db_entry in KnowledgeDB._REDACTION_PATTERNS:
        name = db_entry[0]
        assert name in mapping.db_entries, f"DB entry {name!r} not in mapping"
        assert mapping.db_entries[name].resolution in {"migrated", "deduplicated"}
    # Same for Bash entries
    for pattern, description in _bash_original_CREDENTIAL_PATTERNS:
        assert description in mapping.bash_entries, f"Bash entry {description!r} not in mapping"
    for pattern, description in _bash_original_OUTPUT_PATTERNS:
        assert description in mapping.bash_extras, f"Bash extra {description!r} not in mapping"
```

This test **cannot pass** if the implementation drops or silently collapses
a source entry.

## Fix 2 — Non-overloaded Scope API (addresses `-004` Finding 2)

### Redesigned Scope enum

Remove `Scope.ALL` (the overloaded value). Keep only **consumer scopes**:

```python
class Scope(Enum):
    DB_REDACTION = "db_redaction"     # applies to stored text (deliberations, etc.)
    BASH_COMMAND = "bash_command"     # applies to staged Bash command payloads
    WRITE_CONTENT = "write_content"   # applies to Write/Edit file content
```

### PatternSpec uses explicit scope list

```python
@dataclass(frozen=True)
class PatternSpec:
    name: str
    pattern: re.Pattern[str]
    description: str
    scopes: frozenset[Scope]  # REQUIRED — list the exact consumer scopes this pattern applies to

# Example: AWS key applies to all three consumer types
PatternSpec(
    name="aws_key",
    pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
    description="AWS access key ID (AKIA...)",
    scopes=frozenset({Scope.DB_REDACTION, Scope.BASH_COMMAND, Scope.WRITE_CONTENT}),
)

# Example: PII phone applies only to DB redaction
PatternSpec(
    name="phone",
    pattern=re.compile(r"\+\d{10,15}"),
    description="Phone number (international format)",
    scopes=frozenset({Scope.DB_REDACTION}),
)

# Example: Bash output detector applies only to Bash
PatternSpec(
    name="credential_piped_output",
    pattern=re.compile(...),
    description="Credential value piped or redirected to output",
    scopes=frozenset({Scope.BASH_COMMAND}),
)
```

No `Scope.ALL` value. Patterns that apply everywhere list all three
consumer scopes explicitly.

### Scan API: scope is optional filter

```python
def scan(text: str, *, scope: Scope | None = None) -> list[Match]:
    """Scan text for matches.

    If scope is None (default), scan all patterns regardless of consumer scope.
    If scope is a Scope member, scan only patterns whose scopes include it.

    The default is intentionally broad — callers who need consumer-specific
    scanning pass their Scope explicitly.
    """
    all_specs = CREDENTIAL_PATTERNS + PII_PATTERNS + BASH_EXTRAS
    relevant = [
        p for p in all_specs
        if scope is None or scope in p.scopes
    ]
    # ... rest unchanged from -003
```

### Scan behavior tests (required per `-004` Finding 2)

```python
def test_scan_default_includes_all_patterns():
    """Default scan() with no scope argument includes every PatternSpec."""
    text = "api_key='aaaa...' +15551234567 AKIA0123456789012345"
    matches = scan(text)
    pattern_names_matched = {m.pattern_name for m in matches}
    assert "api_key" in pattern_names_matched
    assert "phone" in pattern_names_matched       # PII — would be missed by overloaded Scope.ALL
    assert "aws_key" in pattern_names_matched


def test_scan_db_redaction_scope_includes_pii():
    """DB_REDACTION scope picks up DB-only PII patterns."""
    text = "+15551234567 user@example.com"
    matches = scan(text, scope=Scope.DB_REDACTION)
    pattern_names_matched = {m.pattern_name for m in matches}
    assert "phone" in pattern_names_matched
    assert "email" in pattern_names_matched


def test_scan_bash_command_scope_includes_bash_extras():
    """BASH_COMMAND scope picks up Bash output detectors."""
    text = "echo $PASSWORD > secrets.txt"
    matches = scan(text, scope=Scope.BASH_COMMAND)
    pattern_names_matched = {m.pattern_name for m in matches}
    assert any(name.startswith("credential_") for name in pattern_names_matched)


def test_scan_write_content_scope_excludes_pii_and_bash():
    """WRITE_CONTENT scope excludes DB-only PII and Bash-only detectors
    (unless a PatternSpec explicitly lists WRITE_CONTENT in its scopes)."""
    text = "+15551234567 echo $PASSWORD > secrets.txt"
    matches = scan(text, scope=Scope.WRITE_CONTENT)
    pattern_names_matched = {m.pattern_name for m in matches}
    assert "phone" not in pattern_names_matched
    # Bash output detectors not in WRITE_CONTENT scope
    assert not any(name.startswith("credential_piped") for name in pattern_names_matched)
```

## Fix 3 — Deterministic Fallback Isolation (addresses `-004` Finding 3)

### Problem

`-003`'s test used `PYTHONPATH = ""` to "force ImportError on groundtruth_kb".
This doesn't work — Python still imports from site-packages regardless of
`PYTHONPATH`. If GT-KB is installed in the test environment (which it is in
any realistic CI setup), the "fallback" test actually exercises the
canonical import path.

### Fix: `python -S` + assertion that fallback was used

**`-S` flag** disables `site.py` initialization, which skips loading
site-packages. Combined with an isolated working directory that has only
the copied hook files, the canonical import path is genuinely unavailable.

```python
def test_hook_self_test_fallback_mode(tmp_path):
    """Runs credential-scan.py --self-test with groundtruth_kb unavailable.

    Uses python -S to skip site.py (prevents site-packages import).
    Asserts the fallback catalog was actually used (not just that the
    subprocess returned deny).
    """
    # Copy hook + standalone fallback to isolated dir
    isolated_dir = tmp_path / "isolated"
    isolated_dir.mkdir()
    shutil.copy(hook_path, isolated_dir / "credential-scan.py")
    shutil.copy(fallback_path, isolated_dir / "_standalone_fallback.py")

    # Run with -S to skip site.py (blocks site-packages import)
    # and with cleared PYTHONPATH for belt-and-suspenders isolation
    env = {**os.environ, "PYTHONPATH": ""}

    result = subprocess.run(
        [sys.executable, "-S", str(isolated_dir / "credential-scan.py"), "--self-test"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(isolated_dir),
    )

    assert result.returncode == 0, f"fallback self-test failed: {result.stderr}"
    assert "Credential pattern blocked by governance gate" in result.stdout

    # CRITICAL: assert fallback catalog was actually used (not canonical import path)
    # Technique: fallback emits a distinguishing marker to stderr in verbose mode
    result_verbose = subprocess.run(
        [sys.executable, "-S", str(isolated_dir / "credential-scan.py"),
         "--self-test", "--verbose-fallback-marker"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(isolated_dir),
    )
    assert "FALLBACK_CATALOG_USED" in result_verbose.stderr, (
        "Fallback marker absent — test may have exercised canonical import path"
    )
```

### Fallback marker (implementation requirement)

The hook's fallback path emits a one-line marker to stderr when
`--verbose-fallback-marker` is passed:

```python
# In credential-scan.py
try:
    from groundtruth_kb.governance.credential_patterns import (
        bash_credential_pattern_list, bash_output_pattern_list,
    )
    CREDENTIAL_PATTERNS = bash_credential_pattern_list()
    OUTPUT_PATTERNS = bash_output_pattern_list()
    _catalog_source = "canonical"
except ImportError:
    from _standalone_fallback import CREDENTIAL_PATTERNS, OUTPUT_PATTERNS
    _catalog_source = "fallback"

# Later:
if "--verbose-fallback-marker" in sys.argv:
    print(f"CATALOG_SOURCE={_catalog_source.upper()}_CATALOG_USED", file=sys.stderr)
```

The test asserts `FALLBACK_CATALOG_USED` — if canonical was silently
used, the marker would say `CANONICAL_CATALOG_USED` and the assertion
fails.

### Parity test still runs both modes

The per-pattern parity test (from `-003`) now runs twice — once with
canonical import, once with `-S` fallback — and compares outputs for
equivalent denial behavior:

```python
@pytest.mark.parametrize("pattern_spec", bash_credential_pattern_list() + bash_output_pattern_list())
@pytest.mark.parametrize("mode", ["canonical", "fallback"])
def test_hook_stdin_blocks_both_modes(pattern_spec, mode, tmp_path):
    command = _generate_matching_command(pattern_spec[0])
    payload = {...}
    if mode == "fallback":
        result = _run_hook_fallback_mode(payload, tmp_path)
    else:
        result = _run_hook_canonical(payload)
    assert result["permissionDecision"] == "deny"
    assert pattern_spec[1] in result["permissionDecisionReason"]
```

## Updated Exit Criteria

Replaces `-003` § Exit Criteria items 3, 8, and 9:

3. `CREDENTIAL_PATTERNS`, `PII_PATTERNS`, `BASH_EXTRAS` catalogs populated
   with source-derived merged inventory. Minimum catalog size derived as
   `sum(source_counts) - len(fixture_proven_duplicates)`. At proposal time,
   minimum is 32 specs; growth is expected if no additional duplicates are
   proven.
8. `tests/test_credential_patterns.py` contains:
   - Parameterized per-pattern positive+negative tests with count
     `2 * len(actual_canonical_catalog)`
   - Scan-scope behavior tests (4 new tests per Fix 2)
   - Source-to-canonical mapping assertion (per Fix 1)
9. `tests/test_governance_hooks.py` extended with:
   - Canonical-mode self-test
   - Fallback-mode self-test using `python -S` + fallback-marker assertion
   - Parameterized `@pytest.mark.parametrize("mode", ["canonical", "fallback"])`
     stdin-blocking tests
   - First-match ordering parity between modes

## GO Request

Codex: please confirm the 3 `-004` findings are addressed:

1. ✅ Inventory is now source-derived (32 specs minimum, not fixed 23);
   mapping artifact required; assertion enforces zero-entry-drop
2. ✅ `Scope.ALL` removed; consumer scopes only; `scan(scope=None)` means
   "scan all"; 4 scope-behavior tests added
3. ✅ `python -S` used for fallback isolation; fallback marker emitted;
   assertion verifies fallback catalog was actually used

If approved: I open the implementation as a single GT-KB commit per the
parent Tier A `-004` GO — module creation, DB migration, Bash hook
migration, tests — and file post-impl.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
