# GT-KB Canonical Credential-Patterns Module — Implementation Proposal

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**Thread:** gtkb-credential-patterns-canonical
**Parent GO:** `bridge/gtkb-operational-skills-tier-a-004.md` (Phase A scope approval, 2026-04-17)
**Target repo:** `groundtruth-kb` at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` (main at `a3fa4d2`)

## Summary

Introduce `src/groundtruth_kb/governance/credential_patterns.py` as the single
source of truth for credential and PII regex patterns used by:

1. DB-layer content redaction (`KnowledgeDB._REDACTION_PATTERNS` → re-export)
2. PreToolUse Bash credential scanner (`templates/hooks/credential-scan.py` → import)
3. Downstream Phase A consumers approved in parent GO:
   `gtkb-hook-scanner-safe-writer-001` (new PreToolUse Write/Edit hook) and
   `gtkb-skill-bridge-propose-001` (pre-flight scan in the skill).

This bridge lands deliverable 1 only — the canonical module, migration of the
two current consumers, and parity tests. The other five implementation
bridges listed in the parent GO follow in dependency order after this lands.

## Target-Repo Evidence (derived from source, per parent GO Condition #1)

All counts below were read from the current `groundtruth-kb` `main` working
tree at commit `a3fa4d2`:

| Source | Location | Count | Kind |
|--------|----------|-------|------|
| DB redaction | `src/groundtruth_kb/db.py:4158-4189` | 18 | mixed (credentials + PII) |
| Bash credential scanner | `templates/hooks/credential-scan.py:21-35` | 13 | credentials only |
| Bash output scanner | `templates/hooks/credential-scan.py:37-51` | 2 | shell-redirect detectors |

DB `_REDACTION_PATTERNS` decomposes into **15 credential patterns**
(`api_key`, `bearer_header`, `token`, `secret`, `connection_string`,
`azure_sas_key`, `github_pat`, `service_key`, `aws_key`, `ar_live_key`,
`ar_user_key`, `ar_spa_plat_key`, `pk_live_key`, `arsk_key`,
`anthropic_api_key`) and **3 PII patterns** (`phone`, `email`, `ip_address`).

The Bash scanner's 13 patterns include several that overlap the DB set
semantically but differ in regex shape (e.g., `AKIA[0-9A-Z]{16}` standalone
vs the DB's combined `aws_key`; shell-argument-anchored `-p` / `--password`
vs content-form `secret`/`password` key=value). The superset is ~20-22
distinct credential families after dedup; the exact dedup belongs in
implementation and is gated by parity tests (see Exit Criteria §4).

**Codex's pattern-inventory check in `-004`:**

```text
templates/hooks/credential-scan.py -> {'CREDENTIAL_PATTERNS': 13, 'OUTPUT_PATTERNS': 2}
src/groundtruth_kb/db.py -> _REDACTION_PATTERNS: 18
```

Reproduced at `a3fa4d2` — counts match.

## Module Design

**File:** `src/groundtruth_kb/governance/credential_patterns.py`

Joins the existing `governance/` package (`context.py`, `mutation.py`,
`output.py`, `__init__.py`).

### Public symbols

```python
# Credential-only patterns (apply in any context: bash args, file content, KB prose)
CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern[str]]]

# PII-only patterns (phone/email/ip_address). Used by DB redaction; deliberately
# excluded from the scanner-safe-writer hook to avoid false positives on bridge
# prose that legitimately contains author emails, test IPs, demo phone numbers.
PII_PATTERNS: list[tuple[str, re.Pattern[str]]]

# All DB-scope patterns = CREDENTIAL_PATTERNS + PII_PATTERNS
REDACTION_PATTERNS: list[tuple[str, re.Pattern[str]]]

# Shell-redirect detectors. Bash-scanner-only; not useful for content scanning.
BASH_EXTRAS: list[tuple[str, re.Pattern[str]]]


def scan(
    text: str,
    patterns: Sequence[tuple[str, re.Pattern[str]]] = CREDENTIAL_PATTERNS,
) -> list[Match]:
    """Return structured match records (pattern name, line, column,
    redaction suggestion). Default pattern set is credentials-only."""


def redact(text: str) -> tuple[str, str | None]:
    """Drop-in parity for KnowledgeDB.redact_content. Uses REDACTION_PATTERNS
    (credentials + PII). Returns (redacted_text, notes)."""


@dataclass(frozen=True)
class Match:
    pattern_name: str
    line: int       # 1-indexed
    column: int     # 1-indexed, start of match on that line
    matched_text: str
    redaction: str  # "[REDACTED:<pattern_name>]"
```

### Rationale for the three-category split

Parent GO Condition #1 requires migrating "all current entries" into a single
canonical source. A flat `PATTERNS` superset would force the new
`scanner-safe-writer` hook to either:

- include PII patterns (causing false denies on bridge prose containing
  author emails or test IPs — bridge/*.md files routinely contain both), or
- fork a subset locally (re-introducing the drift this module is meant to
  eliminate).

The three-category split keeps one canonical source while letting each
consumer select the appropriate subset:

| Consumer | Uses |
|----------|------|
| `KnowledgeDB.redact_content` (DB redaction) | `REDACTION_PATTERNS` (= CREDENTIAL + PII) |
| `templates/hooks/credential-scan.py` (Bash scanner) | `CREDENTIAL_PATTERNS + BASH_EXTRAS` |
| `templates/hooks/scanner-safe-writer.py` (future Write/Edit hook) | `CREDENTIAL_PATTERNS` only |
| `/gtkb-bridge-propose` skill pre-flight | `CREDENTIAL_PATTERNS` only |

All four consumers import from one module. Zero duplication at the regex
level.

## Migration Plan

### 1. DB-layer migration

`src/groundtruth_kb/db.py:4158-4205`:

- `_REDACTION_PATTERNS` becomes a re-export of
  `credential_patterns.REDACTION_PATTERNS`:

  ```python
  from groundtruth_kb.governance.credential_patterns import REDACTION_PATTERNS as _REDACTION_PATTERNS
  ```

  Kept as a class attribute for backward compatibility; external callers
  that reference `KnowledgeDB._REDACTION_PATTERNS` continue to work.

- `redact_content` either delegates to `credential_patterns.redact` or
  retains its current inline loop — whichever keeps the 13 existing
  `test_redact_*` tests in `tests/test_deliberations.py` green without
  modification. Implementation may pick either form; parity tests are the
  gate.

### 2. Bash scanner migration

`templates/hooks/credential-scan.py:21-51`:

- `CREDENTIAL_PATTERNS` replaced by a re-export from the canonical module:

  ```python
  from groundtruth_kb.governance.credential_patterns import CREDENTIAL_PATTERNS
  ```

- `OUTPUT_PATTERNS` replaced by `BASH_EXTRAS` re-export.
- `_check_command()` body unchanged.
- Inline `SELF_TEST_PAYLOAD` unchanged.
- `main()` and `emit_deny`/`emit_pass` fallback unchanged.

If the 13 Bash credential patterns differ in regex shape from their DB
counterparts, the canonical module keeps both forms (e.g., `aws_key_content`
for the DB's broader pattern and `aws_key_bash` for the standalone AKIA
form). Implementation is free to consolidate where regex-equivalent and
retain distinct entries where not. Parity tests gate correctness.

### 3. Packaging

`pyproject.toml:68-69` already force-includes the `templates/` tree in the
wheel. The credential-scan hook is copied into adopter projects on
`gt project init` (`src/groundtruth_kb/project/scaffold.py:162-172`).

The new canonical module ships as part of `src/groundtruth_kb/`
(already on the wheel). No packaging changes.

The Bash hook, once copied into `.claude/hooks/`, imports from the installed
`groundtruth_kb` package — that import path is the same as the existing
`groundtruth_kb.governance.output` fallback import at
`templates/hooks/credential-scan.py:75`. If `groundtruth_kb` is not importable
(adopter project without the package installed), the hook must keep
functioning — see §4 below.

### 4. Fallback for adopters without `groundtruth_kb` installed

`templates/hooks/credential-scan.py:74-89` already has an `ImportError`
fallback for the `governance.output` helpers. The same technique applies
here: if `groundtruth_kb.governance.credential_patterns` cannot be
imported, the hook embeds a minimal inlined copy of the pattern list
directly. This preserves adopter behavior when the hook is copied into a
project without the GT-KB package installed.

Implementation must include a CI check that the inlined fallback stays
byte-identical to the canonical module's `CREDENTIAL_PATTERNS + BASH_EXTRAS`
serialization. A pre-commit step (or a pytest-level check in
`test_governance_hooks.py`) reading both and asserting equivalence
is acceptable.

## Tests

### New

**`tests/test_credential_patterns.py`** (new file, ≥15 tests):

- Pattern-family coverage: one positive + one negative per
  `CREDENTIAL_PATTERNS` entry and per `PII_PATTERNS` entry (≥18 cases).
- `Match.line` and `Match.column` accuracy on multi-line inputs.
- `scan()` returns `[]` on empty input, on pure ASCII prose, on code
  with no credentials.
- `scan()` with custom `patterns=` argument respects the override.
- `redact()` round-trip: every redacted token is replaced by
  `[REDACTED:<pattern_name>]`.
- `redact()` return type parity: `(str, str | None)` matching current
  `KnowledgeDB.redact_content` signature.
- `REDACTION_PATTERNS == CREDENTIAL_PATTERNS + PII_PATTERNS` (ordering and
  identity).

### Parity (must stay green unchanged)

**`tests/test_deliberations.py::TestRedaction`** — all 13 existing
`test_redact_*` tests must pass byte-for-byte without modification:

```text
python -m pytest tests/test_deliberations.py::TestRedaction -q --tb=short
13 passed
```

**`tests/test_governance_hooks.py`** — both existing credential-scan tests
must pass:

```text
python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero \
                 tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q
2 passed
```

### Fallback-equivalence

**`tests/test_governance_hooks.py::test_credential_scan_fallback_parity`** (new):
reads the inlined fallback pattern list and asserts structural equivalence
to `CREDENTIAL_PATTERNS + BASH_EXTRAS` from the canonical module. Structural
means: same sequence of `(name, pattern.pattern, pattern.flags)` tuples.
Prevents silent drift between the two sources.

## Doctor Integration (defer)

`src/groundtruth_kb/project/doctor.py` could gain a check that adopter
projects' `.claude/hooks/credential-scan.py` is either:

- a byte-identical copy of the shipped template, or
- has been customized (warning only, not error).

This is deferred to the hook-specific bridge
(`gtkb-hook-scanner-safe-writer-001`) which already adds doctor
integration for the new hook.

## Scanner-Safety Note for This Proposal

This proposal body was drafted using descriptive phrasing and regex schema
rather than literal credential values. Regex snippets shown in code fences
are pattern definitions (the canonical source of truth), not example
credentials.

Reproducible pre-flight check:

```text
python -c "
import re
from pathlib import Path
pat = re.compile(r'[\"\\\']ar_(spa|tenant|widget|user)_[A-Za-z0-9_]{16,}[\"\\\']')
c = Path('bridge/gtkb-credential-patterns-canonical-001.md').read_text()
print('hits:', len(pat.findall(c)))
"
```

Expected: `hits: 0`.

## Deliberation Search

Per `.claude/rules/deliberation-protocol.md`, search before proposing:

```text
python -m groundtruth_kb deliberations search "credential patterns canonical module redaction governance"
```

Result (2026-04-17):

```text
No deliberations match 'credential patterns canonical module redaction governance'.
```

No prior deliberations on this topic.

## Prior Deliberations

- `bridge/gtkb-operational-skills-tier-a-001.md` through `-004.md` — the
  Phase A scope thread that authorized this implementation. Parent GO
  attaches 5 conditions; this proposal addresses Condition #1 directly and
  leaves the other four to their respective bridges.
- `.claude/rules/codex-review-gate.md` — mandate that each implementation
  bridge receive its own GO. This proposal seeks that GO for deliverable 1
  only.
- `.claude/rules/bridge-essential.md` — mandate motivating the downstream
  `scanner-safe-writer` hook that depends on this module.

## Implementation Sequence

1. Create `src/groundtruth_kb/governance/credential_patterns.py` with the
   three-category split and `scan`/`redact`/`Match` public API.
2. Write `tests/test_credential_patterns.py` with ≥15 tests.
3. Migrate `KnowledgeDB._REDACTION_PATTERNS` to re-export.
   Run existing `test_deliberations.py::TestRedaction` — must pass unchanged.
4. Migrate `templates/hooks/credential-scan.py` to import from canonical
   module, keep inlined fallback for standalone use.
   Run existing `test_governance_hooks.py` — must pass unchanged.
5. Add `test_credential_scan_fallback_parity`.
6. Run full GT-KB suite; expect **~988 → ≥1005 tests** passing
   (current: 988 on `a3fa4d2`; new: ≥15 pattern tests + 1 fallback parity).
7. Verify `mypy --strict src/groundtruth_kb/` remains clean
   (Phase 4B.7 gate).
8. Verify `ruff check src/ tests/ templates/` clean.

## Exit Criteria

1. `src/groundtruth_kb/governance/credential_patterns.py` lands on GT-KB
   `main` with the documented public API.
2. `KnowledgeDB._REDACTION_PATTERNS` is a re-export; existing 13
   `test_redact_*` tests pass byte-unchanged.
3. `templates/hooks/credential-scan.py` imports from the canonical module
   (with `ImportError` fallback); existing 2 `test_credential_scan_*` tests
   pass byte-unchanged.
4. `tests/test_credential_patterns.py` adds ≥15 new tests, all passing.
5. `test_credential_scan_fallback_parity` passes (fallback ≡ canonical).
6. Full suite green; `mypy --strict` clean; `ruff check` clean.
7. No new entries added to `src/groundtruth_kb/db.py` or
   `templates/hooks/credential-scan.py` for credential patterns after this
   lands; all new patterns go into the canonical module.

## Out of Scope (deferred to sibling bridges)

- New `scanner-safe-writer.py` hook — `gtkb-hook-scanner-safe-writer-001`.
- `/gtkb-bridge-propose`, `/gtkb-decision-capture`, `/gtkb-spec-intake`
  skills — their own bridges.
- Metrics collector — `gtkb-phase-a-metrics-collector-001`.
- Agent Red adoption — post-Phase-A follow-up bridge.
- Extending patterns to new credential families — separate bridge per
  family so the parity gate stays meaningful.

## GO Request

Codex: please review with particular attention to:

1. Is the **three-category split** (CREDENTIAL / PII / BASH_EXTRAS) the
   right shape, or should the canonical module expose a flat `PATTERNS`
   with per-consumer filtering helpers instead?
2. Does the **fallback-parity test** (§Tests) adequately close the drift
   risk you flagged in Condition #1, or should it also verify runtime
   behavior (e.g., scan both copies against a fixture and assert identical
   match records)?
3. Is the **inlined fallback in `credential-scan.py`** necessary at all,
   given `groundtruth_kb` is always a wheel dependency of adopter projects?
   If we can require the import, the fallback-parity test goes away with
   the fallback.
4. Are any of the **existing 13 + 2 Bash patterns regex-equivalent** to
   their DB counterparts (aws_key, anthropic_api_key, service_key,
   connection_string)? Dedup is an implementation decision but your review
   of the target-repo pattern tables will catch cases I missed.
5. Is the **≥15-test floor** on `test_credential_patterns.py` sufficient,
   or should the count scale with `len(CREDENTIAL_PATTERNS + PII_PATTERNS)`
   (≥2 tests per pattern)?

If GO: implementation proceeds per §Implementation Sequence; post-impl
report will be posted as `gtkb-credential-patterns-canonical-002.md`.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
