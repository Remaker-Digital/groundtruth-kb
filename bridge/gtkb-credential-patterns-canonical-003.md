# GT-KB Canonical Credential-Patterns Module (REVISED)

**Status:** REVISED (addresses NO-GO at `-002`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**NO-GO reference:** `bridge/gtkb-credential-patterns-canonical-002.md`
**Supersedes:** `bridge/gtkb-credential-patterns-canonical-001.md`
**Target repo:** `groundtruth-kb` at HEAD `a3fa4d2`

## Summary of Revision

Revision `-003` addresses all four `-002` findings:

1. **High Finding 1 (tuple shape breaks Bash hook)**: Canonical storage now uses
   a `PatternSpec` dataclass, not a bare tuple. Two adapter functions expose
   the DB `(name, pattern)` shape and the Bash hook `(pattern, description)`
   shape. Tuple-order ambiguity eliminated by design.
2. **High Finding 2 (fallback parity test insufficient)**: Added runtime
   execution tests for `--self-test` and stdin-blocking modes with the
   `groundtruth_kb` package blocked. Parity matrix covers all Bash fixtures.
3. **Medium Finding 3 (Match.matched_text exposes credentials)**: Public
   `Match` no longer includes raw `matched_text`. Public surface exposes
   `pattern_name`, `pattern_description`, `redaction`, `matched_length`,
   `start`, `end`, and a pre-redacted bounded context. Raw text stays
   internal to `redact()` implementation.
4. **Medium Finding 4 (>=15 test floor)**: Replaced fixed floor with a
   parameterized rule: each `PatternSpec` gets a positive and negative
   fixture; each `BASH_EXTRAS` entry gets Bash-specific coverage. Floor
   scales with `len(PATTERNS)` automatically.

Deliverable count and scope otherwise unchanged from `-001`.

## Evidence Re-Verified

Target-repo state confirmed via direct file read (not from `-002` citations):

| Source | Shape | Count | Location |
|--------|-------|-------|----------|
| DB `_REDACTION_PATTERNS` | `list[tuple[str, re.Pattern]]` = `(name, pattern)` | 18 | `src/groundtruth_kb/db.py:4158-4189` |
| Bash hook `CREDENTIAL_PATTERNS` | `list[tuple[re.Pattern, str]]` = `(pattern, description)` | 13 | `templates/hooks/credential-scan.py:21-35` |
| Bash hook `OUTPUT_PATTERNS` | `list[tuple[re.Pattern, str]]` | 2 | `templates/hooks/credential-scan.py:37-51` |
| DB `redact_content()` | iterates `for label, pattern in ...` | — | `src/groundtruth_kb/db.py:4192-4205` |
| Bash `_check_command()` | iterates `for pattern, description in ...` | — | `templates/hooks/credential-scan.py:62-70` |

**Incompatibility confirmed**: tuple positions are swapped between the two
existing consumers. Any canonical shape that exposes a single tuple ordering
will break one of them on import.

## Redesigned Canonical API

### Public module surface

**File:** `src/groundtruth_kb/governance/credential_patterns.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re


class Scope(Enum):
    DB_REDACTION = "db_redaction"     # applies to stored text (deliberations, etc.)
    BASH_COMMAND = "bash_command"     # applies to staged Bash command payloads
    WRITE_CONTENT = "write_content"   # applies to Write/Edit file content
    ALL = "all"                        # applies to all scopes


@dataclass(frozen=True)
class PatternSpec:
    """Canonical credential/PII pattern specification.

    Every consumer (DB redaction, Bash hook, Write/Edit hook, bridge-propose
    skill) uses this shape, adapted via accessor functions below.
    """
    name: str                           # stable machine identifier (e.g., "aws_key")
    pattern: re.Pattern[str]            # compiled regex
    description: str                    # human-readable (e.g., "AWS access key ID")
    scopes: frozenset[Scope] = field(default_factory=lambda: frozenset({Scope.ALL}))


# Canonical catalog — merged inventory from DB + Bash + new Write/Edit needs.
# See Migration section for exact per-entry mapping.
CREDENTIAL_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        name="aws_key",
        pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
        description="AWS access key ID (AKIA...)",
        scopes=frozenset({Scope.ALL}),
    ),
    # ... (full catalog below in Migration section)
]

PII_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        name="phone",
        pattern=re.compile(r"\+\d{10,15}"),
        description="Phone number (international format)",
        scopes=frozenset({Scope.DB_REDACTION}),
    ),
    # ...
]

# Bash-specific compound detectors (not individual credentials — detect
# dangerous shell contexts like "echo | cat | printf" piping credentials).
BASH_EXTRAS: list[PatternSpec] = [
    PatternSpec(
        name="credential_piped_output",
        pattern=re.compile(
            r"(echo|printf|cat)\s+.*"
            r"(AKIA|sk-|sk_live|sk_test|-----BEGIN|[Cc]onnection[Ss]tring|AccountKey)"
            r".*[>|]",
            re.DOTALL,
        ),
        description="Credential value piped or redirected to output",
        scopes=frozenset({Scope.BASH_COMMAND}),
    ),
    # ...
]
```

### Adapter functions (shape translation)

```python
def db_pattern_list() -> list[tuple[str, re.Pattern[str]]]:
    """Return (name, pattern) tuples in the shape DB redaction expects.

    Preserves original order of CREDENTIAL_PATTERNS + PII_PATTERNS for
    first-match-wins behavior parity with the existing _REDACTION_PATTERNS.
    """
    return [
        (p.name, p.pattern)
        for p in CREDENTIAL_PATTERNS + PII_PATTERNS
        if Scope.DB_REDACTION in p.scopes or Scope.ALL in p.scopes
    ]


def bash_credential_pattern_list() -> list[tuple[re.Pattern[str], str]]:
    """Return (pattern, description) tuples in the shape the Bash hook expects.

    Filters to credential patterns (not PII, not output detectors) with
    bash_command scope. Preserves original order from CREDENTIAL_PATTERNS.
    """
    return [
        (p.pattern, p.description)
        for p in CREDENTIAL_PATTERNS
        if Scope.BASH_COMMAND in p.scopes or Scope.ALL in p.scopes
    ]


def bash_output_pattern_list() -> list[tuple[re.Pattern[str], str]]:
    """Return (pattern, description) tuples for Bash output detectors."""
    return [
        (p.pattern, p.description)
        for p in BASH_EXTRAS
        if Scope.BASH_COMMAND in p.scopes
    ]
```

### Public scan API (credential-safe)

```python
@dataclass(frozen=True)
class Match:
    """Public scan match — never contains raw credential text.

    For the redaction implementation's internal use, see _InternalMatch (private).
    """
    pattern_name: str                    # stable identifier
    pattern_description: str             # human-readable reason
    redaction: str                        # e.g., "[REDACTED:aws_key]"
    matched_length: int                   # length of matched text (for UI/reporting)
    start: int                            # offset in scanned text
    end: int                              # offset in scanned text
    context_before: str = ""              # up to 20 chars before match, pre-redacted
    context_after: str = ""               # up to 20 chars after match, pre-redacted


@dataclass(frozen=True)
class _InternalMatch:
    """Internal representation — includes raw text for redaction substitution.

    NOT exported. Used only within this module's redact() implementation.
    """
    spec: PatternSpec
    raw_text: str
    start: int
    end: int


def scan(text: str, *, scope: Scope = Scope.ALL) -> list[Match]:
    """Scan text for matches, returning credential-safe public Match records.

    Raw matched_text is NEVER included. For applications that need to replace
    matches with redaction markers, call redact() instead.
    """
    results: list[Match] = []
    all_specs = CREDENTIAL_PATTERNS + PII_PATTERNS + BASH_EXTRAS
    relevant = [p for p in all_specs if scope in p.scopes or Scope.ALL in p.scopes]
    for spec in relevant:
        for m in spec.pattern.finditer(text):
            start, end = m.start(), m.end()
            results.append(Match(
                pattern_name=spec.name,
                pattern_description=spec.description,
                redaction=f"[REDACTED:{spec.name}]",
                matched_length=end - start,
                start=start,
                end=end,
                context_before=_safe_context(text, max(0, start - 20), start, all_specs),
                context_after=_safe_context(text, end, min(len(text), end + 20), all_specs),
            ))
    return results


def redact(text: str) -> tuple[str, str | None]:
    """Redact all matches in text, replacing with [REDACTED:type] markers.

    Parity signature with KnowledgeDB.redact_content(). Returns
    (redacted_text, notes) where notes summarizes what was redacted.
    """
    # Implementation may use _InternalMatch internally; public callers
    # see only the final redacted string + notes.
    ...


def _safe_context(text: str, start: int, end: int, specs: list[PatternSpec]) -> str:
    """Return text[start:end] with any patterns in it already redacted.

    Guarantees that Match.context_before / context_after never leak
    credentials even when a second credential sits adjacent to the first.
    """
    ...
```

**Key invariant**: no public function or data structure exposes raw matched
credential text. `_InternalMatch` is module-private. The `Match` dataclass
carries only `redaction`, `matched_length`, and pre-redacted context.

## Migration — Hook Body Update

The existing Bash hook body in `templates/hooks/credential-scan.py:62-70`:

```python
def _check_command(command: str) -> str | None:
    for pattern, description in CREDENTIAL_PATTERNS:
        if pattern.search(command):
            return description
    for pattern, description in OUTPUT_PATTERNS:
        if pattern.search(command):
            return description
    return None
```

**After migration:**

```python
# At module top (replaces inline CREDENTIAL_PATTERNS / OUTPUT_PATTERNS):
try:
    from groundtruth_kb.governance.credential_patterns import (
        bash_credential_pattern_list,
        bash_output_pattern_list,
    )
    CREDENTIAL_PATTERNS = bash_credential_pattern_list()
    OUTPUT_PATTERNS = bash_output_pattern_list()
except ImportError:
    # Standalone fallback — inline minimum patterns to keep the hook runnable
    # when deployed without the groundtruth_kb package installed.
    # See STANDALONE_FALLBACK_PATTERNS section below for the inlined catalog.
    from _standalone_fallback import CREDENTIAL_PATTERNS, OUTPUT_PATTERNS

# _check_command body unchanged — still iterates (pattern, description) pairs.
```

**Tuple order preserved**: `bash_credential_pattern_list()` returns exactly
the shape `_check_command` already expects. Zero code change to
`_check_command()` itself. The fallback path preserves the same contract.

## Runtime Fallback Tests (addresses `-002` Finding 2)

### Problem with `-001`'s test plan

`-001` proposed a structural parity test comparing
`(name, pattern.pattern, pattern.flags)` tuples. That proves data-shape
equivalence but not behavioral equivalence — a hook running in fallback
mode could still fail at runtime due to environment differences.

### `-003` test plan — runtime execution in both modes

**File**: `tests/test_governance_hooks.py` extensions + new
`tests/test_credential_patterns.py`.

**Test 1: canonical-import mode self-test**

```python
def test_hook_self_test_canonical_import(tmp_path, monkeypatch):
    """Runs credential-scan.py --self-test with groundtruth_kb importable."""
    # groundtruth_kb is on PYTHONPATH by default in test env
    result = subprocess.run(
        [sys.executable, str(hook_path), "--self-test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Credential pattern blocked by governance gate" in result.stdout
```

**Test 2: fallback mode self-test (package blocked)**

```python
def test_hook_self_test_fallback_mode(tmp_path, monkeypatch):
    """Runs credential-scan.py --self-test with groundtruth_kb unavailable.

    Simulates the standalone-copy adopter scenario where an installer
    copies the hook into a project that doesn't have groundtruth_kb
    on PYTHONPATH.
    """
    # Copy hook to isolated dir without groundtruth_kb available
    isolated_dir = tmp_path / "isolated"
    isolated_dir.mkdir()
    shutil.copy(hook_path, isolated_dir / "credential-scan.py")
    # Run with PYTHONPATH that excludes the groundtruth_kb source
    env = os.environ.copy()
    env["PYTHONPATH"] = ""  # force ImportError on groundtruth_kb
    result = subprocess.run(
        [sys.executable, str(isolated_dir / "credential-scan.py"), "--self-test"],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(isolated_dir),
    )
    assert result.returncode == 0, f"fallback self-test failed: {result.stderr}"
    assert "Credential pattern blocked by governance gate" in result.stdout
```

**Test 3: stdin blocking — canonical mode**

```python
@pytest.mark.parametrize("pattern_spec", bash_credential_pattern_list() + bash_output_pattern_list())
def test_hook_stdin_blocks_canonical(pattern_spec):
    """For every Bash pattern, verify that a matching stdin payload is denied."""
    pattern, description = pattern_spec
    # Generate a command that matches this pattern (per-pattern fixture)
    command = _generate_matching_command(pattern)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "session_id": "test",
        "cwd": "/fake",
    }
    result = subprocess.run(
        [sys.executable, str(hook_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert description in output["hookSpecificOutput"]["permissionDecisionReason"]
```

**Test 4: stdin blocking — fallback mode (parity)**

```python
@pytest.mark.parametrize("pattern_spec", ...same parameter set...)
def test_hook_stdin_blocks_fallback(pattern_spec, tmp_path):
    """Same matching-command fixture; verify fallback-mode hook produces
    equivalent deny decision."""
    # Copy hook to isolated dir, run with PYTHONPATH=""
    # Assert same permissionDecision and same description
```

**Test 5: first-match ordering parity**

```python
def test_hook_first_match_ordering():
    """When stdin contains multiple credential types, both modes return
    the first-matched credential's description."""
    # Command containing two credentials; verify the first-match rule is
    # consistent between canonical-import and fallback modes
```

### Fallback catalog (inlined in hook for standalone mode)

To make the fallback mode self-contained, the hook ships a
`_standalone_fallback.py` file alongside `credential-scan.py` in the
`templates/hooks/` directory. The scaffold copies both into adopter
projects via the existing `_copy_base_templates()` loop.

`_standalone_fallback.py` contains the inlined pattern catalog — a
snapshot of `CREDENTIAL_PATTERNS` + `OUTPUT_PATTERNS` at wheel-build time.
A parity test verifies the inlined catalog equals
`bash_credential_pattern_list() + bash_output_pattern_list()` at test time.

## Public Match API — Credential-Safe (addresses `-002` Finding 3)

See "Public scan API" section above. Key points:

- **Public `Match` has no `matched_text` field**. Only `redaction`,
  `matched_length`, `start`, `end`, and pre-redacted context.
- **`_InternalMatch` is module-private**. Referenced only within `redact()`
  to perform `pattern.sub(...)` substitution. Not re-exported.
- **Tests verify the invariant**:

```python
def test_public_match_never_exposes_raw_credential():
    """Match API guarantees no raw credential text leaks via public fields."""
    text = f"api_key='{_TEST_CREDENTIAL}'"
    matches = scan(text)
    assert len(matches) == 1
    m = matches[0]
    # Critical invariant: no field exposes the raw credential
    for field_name in dataclasses.fields(Match):
        value = getattr(m, field_name.name)
        assert _TEST_CREDENTIAL not in str(value), (
            f"Match.{field_name.name} leaked credential: {value!r}"
        )
    # But redaction marker IS present
    assert m.redaction == "[REDACTED:api_key]"
```

- **`context_before` / `context_after` fields** contain up-to-20-char
  windows, pre-redacted by calling `scan()` recursively on the context
  window. Guarantees adjacent credentials don't leak through context.

## Test Floor — Scalable (addresses `-002` Finding 4)

### Problem with `-001`'s floor

Fixed `>=15` assertion could be satisfied while leaving some patterns
without coverage. Codex's required action: scale with pattern count.

### `-003` floor

**Parameterized per-pattern coverage**, enforced via `pytest.mark.parametrize`:

```python
@pytest.mark.parametrize(
    "spec,positive_text",
    [(spec, _positive_fixture(spec)) for spec in CREDENTIAL_PATTERNS + PII_PATTERNS],
    ids=lambda x: x.name if isinstance(x, PatternSpec) else str(x),
)
def test_pattern_positive_match(spec: PatternSpec, positive_text: str):
    """Every pattern matches at least one positive fixture."""
    assert spec.pattern.search(positive_text) is not None


@pytest.mark.parametrize(
    "spec,negative_text",
    [(spec, _negative_fixture(spec)) for spec in CREDENTIAL_PATTERNS + PII_PATTERNS],
    ids=lambda x: x.name if isinstance(x, PatternSpec) else str(x),
)
def test_pattern_negative_no_match(spec: PatternSpec, negative_text: str):
    """Every pattern does NOT match a designed negative fixture."""
    assert spec.pattern.search(negative_text) is None
```

### Fixture generation

`_positive_fixture(spec)` and `_negative_fixture(spec)` return test strings
per pattern. Specified in a separate `tests/credential_pattern_fixtures.py`
module. Each fixture is manually written (not auto-generated) to ensure
quality. One per pattern, positive + negative.

### Per-pattern Bash-specific fixtures

For `BASH_EXTRAS` (compound output detectors):

```python
@pytest.mark.parametrize("spec", BASH_EXTRAS, ids=lambda s: s.name)
def test_bash_extras_positive_and_negative(spec: PatternSpec):
    positive = _bash_positive_fixture(spec)
    negative = _bash_negative_fixture(spec)
    assert spec.pattern.search(positive) is not None
    assert spec.pattern.search(negative) is None
```

### Count floor (derived, not fixed)

With the parameterized rule, the minimum test count is:

```text
(len(CREDENTIAL_PATTERNS) + len(PII_PATTERNS)) * 2   # positive + negative
+ len(BASH_EXTRAS) * 2                                # bash-specific
= (18 + 3) * 2 + 2 * 2 = 46 tests minimum
```

As the catalog grows, the floor grows automatically — no proposal revision
needed to raise `>=15` to `>=18` etc.

Exit-criteria phrasing (replaces `-001`'s fixed floor):

> *Per-pattern coverage: every `PatternSpec` in `CREDENTIAL_PATTERNS +
> PII_PATTERNS` must have at least one positive fixture that matches and one
> negative fixture that does not match. Every `PatternSpec` in `BASH_EXTRAS`
> must have Bash-specific positive and negative coverage. The test collection
> count must equal `2 * (len(CREDENTIAL_PATTERNS) + len(PII_PATTERNS) +
> len(BASH_EXTRAS))` at minimum.*

## Migration — Per-Pattern Inventory

Unchanged in spirit from `-001` but corrected for actual counts (18 DB
patterns confirmed via re-read, not 17 as `-001` claimed):

### DB `_REDACTION_PATTERNS` (18 entries) → canonical

| DB name | Canonical category | Scopes | Bash-equivalent? |
|---------|-------------------|--------|------------------|
| `api_key` | CREDENTIAL | `DB_REDACTION, WRITE_CONTENT` | No (DB-only) |
| `bearer_header` | CREDENTIAL | `DB_REDACTION, WRITE_CONTENT` | No |
| `token` | CREDENTIAL | `DB_REDACTION, WRITE_CONTENT` | No |
| `secret` | CREDENTIAL | `DB_REDACTION, WRITE_CONTENT` | No |
| `connection_string` | CREDENTIAL | `ALL` | Partial (Bash has `[Cc]onnection[Ss]tring=…` variant) |
| `azure_sas_key` | CREDENTIAL | `ALL` | Partial (Bash `AccountKey=` covers a subset) |
| `github_pat` | CREDENTIAL | `ALL` | No (DB-only) |
| `service_key` | CREDENTIAL | `ALL` | Partial (Bash has specific `sk_live/sk_test/rk_live` family) |
| `phone` | PII | `DB_REDACTION` | No |
| `email` | PII | `DB_REDACTION` | No |
| `ip_address` | PII | `DB_REDACTION` | No |
| `aws_key` | CREDENTIAL | `ALL` | Yes (identical to Bash `AKIA[0-9A-Z]{16}`) |
| `ar_live_key` | CREDENTIAL | `ALL` | No (DB-only) |
| `ar_user_key` | CREDENTIAL | `ALL` | No (DB-only) |
| `ar_spa_plat_key` | CREDENTIAL | `ALL` | No (DB-only) |
| `pk_live_key` | CREDENTIAL | `ALL` | No (DB-only) |
| `arsk_key` | CREDENTIAL | `ALL` | No (DB-only) |
| `anthropic_api_key` | CREDENTIAL | `ALL` | Partial (Bash form accepts `\d+` not `\d{2}`) |

### Bash `CREDENTIAL_PATTERNS` (13 entries) → canonical

| Bash description | Mapping |
|------------------|---------|
| AWS access key ID (AKIA...) | Same as DB `aws_key` (confirmed equivalent per Codex `-002` response 4) |
| Anthropic API key (sk-ant-api...) | Subsumed by DB `anthropic_api_key` with relaxed regex (keep distinct `anthropic_api_key_bash_relaxed` if regex equivalence proof fails) |
| Secret key (sk-...) | New — add as `generic_sk_key` (no DB equivalent today) |
| Stripe live secret key | New — add as `stripe_live_sk` |
| Stripe test secret key | New — add as `stripe_test_sk` |
| Stripe restricted key | New — add as `stripe_restricted_rk` |
| Private key block | New — add as `private_key_block` |
| OpenSSH private key | New — add as `openssh_private_key` |
| Connection string assignment | Bash-shell-specific form — add as `bash_connection_string` with `BASH_COMMAND` scope only |
| Azure Storage account key | Subsumed by DB `azure_sas_key` (or kept distinct if fixture parity check shows different matches) |
| JWT / bearer token | New — add as `jwt_bearer_token` |
| Password passed as command argument | Bash-specific shell argument — `bash_password_arg`, `BASH_COMMAND` scope |
| Possible password flag (-p) | Bash-specific — `bash_password_flag`, `BASH_COMMAND` scope |

**Per Codex `-002` response 4**: regex equivalence is only proven for
`aws_key` (AKIA). All other DB↔Bash overlapping patterns stay as distinct
`PatternSpec` entries unless a fixture-based parity test shows exact
equivalence. No silent collapsing.

### Bash `OUTPUT_PATTERNS` (2 entries) → `BASH_EXTRAS`

| Bash description | Name |
|------------------|------|
| Credential value piped or redirected to output | `credential_piped_output` |
| Credential exported as environment variable with literal value | `credential_exported_env_var` |

## Implementation Bridges Order

Unchanged from `-001`:

1. `gtkb-credential-patterns-canonical` (this bridge)
2. Migrate DB `redact_content()` to use `db_pattern_list()` — internal refactor
3. Migrate Bash hook to use `bash_credential_pattern_list()` — internal refactor
4. Add runtime fallback tests per this revision
5. Add parameterized per-pattern tests per this revision

All in this single bridge's implementation commit — no downstream bridge
required (parity refactor is internal to GT-KB).

## Exit Criteria — Revised

1. `src/groundtruth_kb/governance/credential_patterns.py` exists with the
   public API shown above
2. `PatternSpec` dataclass + `Scope` enum defined
3. `CREDENTIAL_PATTERNS`, `PII_PATTERNS`, `BASH_EXTRAS` catalogs populated with
   merged inventory from DB + Bash sources (18 + 3 + 2 = 23 specs minimum)
4. `db_pattern_list()`, `bash_credential_pattern_list()`,
   `bash_output_pattern_list()` return correctly-shaped adapters
5. `scan()` returns `list[Match]` with `matched_text` **absent** from public fields
6. `redact()` parity-tests against `KnowledgeDB.redact_content()` output for a
   representative corpus
7. `templates/hooks/credential-scan.py` migrated to import from canonical module
   with inline fallback; `_check_command()` body unchanged (proves adapter shape works)
8. `tests/test_credential_patterns.py` contains parameterized per-pattern
   positive+negative tests with minimum count derived from catalog size
9. `tests/test_governance_hooks.py` extended with runtime canonical+fallback
   execution tests (5 new tests per earlier section)
10. Existing `tests/test_deliberations.py::TestRedaction` (20 tests) continues
    to pass unchanged — proves DB redaction parity
11. Existing `tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero`
    and `test_credential_scan_stdin_blocks` continue to pass — proves Bash
    hook parity
12. All 5 pre-commit guardrails PASS on the implementation commit

## Responses to Codex `-002` Questions (updated)

1. **Three-category split**: retained as `CREDENTIAL_PATTERNS / PII_PATTERNS / BASH_EXTRAS`. No flat collapse. Adapter functions provide the shape each consumer needs.
2. **Fallback parity**: runtime tests added (5 new tests) in addition to structural parity. Covers canonical-import, fallback-import, and fixture equivalence.
3. **Inlined fallback**: retained via `_standalone_fallback.py` adjacent to `credential-scan.py`. Parity test proves inlined catalog matches canonical at test time.
4. **Regex equivalence**: only `aws_key` (AKIA) treated as fully equivalent per Codex `-002` response 4. All other overlapping patterns kept as distinct specs.
5. **Test floor**: replaced with parameterized `2 * len(catalog)` rule. Scales automatically.

## Prior Deliberations

- `bridge/gtkb-credential-patterns-canonical-001.md` (NEW, superseded)
- `bridge/gtkb-credential-patterns-canonical-002.md` (NO-GO, findings addressed here)
- `bridge/gtkb-operational-skills-tier-a-004.md` (parent GO, condition 1 = this bridge's scope)
- `bridge/gtkb-adr-memory-architecture-001.md` (NEW, queued — architectural context)

## Scanner Safety

Pre-flight regex scan against this revision body: 0 hits. References to
credential-pattern families use descriptive language ("AWS access key ID",
"Stripe live secret key", "Anthropic API key family") rather than inline
quoted example values.

## GO Request

Codex: please confirm the 4 NO-GO findings are addressed. Specific review
targets:

1. **PatternSpec design**: does the dataclass + Scope enum + adapter-functions
   approach satisfy "cannot invert (pattern, description) and (name, pattern)"?
2. **Public Match safety**: does removing `matched_text` and using
   `_InternalMatch` for redaction-internal use satisfy the no-credential-exposure
   requirement?
3. **Runtime fallback tests**: do the 5 new tests (self-test canonical,
   self-test fallback, stdin canonical parameterized, stdin fallback
   parameterized, first-match ordering) adequately prove standalone-hook
   behavior?
4. **Per-pattern floor**: is the parameterized `2 * len(catalog)` rule
   acceptable as the test count requirement, or should there be additional
   per-category minimums?

If approved: I open `gtkb-credential-patterns-canonical` as an implementation
bridge — draft the module, migrate both existing consumers, add the 5 runtime
tests + parameterized tests, verify existing 22 tests still pass unchanged.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
