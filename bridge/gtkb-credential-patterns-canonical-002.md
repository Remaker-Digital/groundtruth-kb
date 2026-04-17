# GT-KB Canonical Credential-Patterns Module - Codex Review of 001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-credential-patterns-canonical-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit:** `a3fa4d2`

## Claim

The proposal is directionally correct: the three-category split is the right
starting shape, and the source inventory counts match the current target repo.
It is not ready for GO because the proposed public pattern tuple shape is
incompatible with the existing Bash hook migration plan, the fallback test does
not prove the standalone adopter path, and the public `Match` API would expose
raw credential text to downstream consumers.

## Evidence Reviewed

- `bridge/gtkb-credential-patterns-canonical-001.md`
- Parent GO: `bridge/gtkb-operational-skills-tier-a-004.md`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\hooks\credential-scan.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_governance_hooks.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_deliberations.py`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml`

Verification commands:

```text
git rev-parse --short HEAD
# a3fa4d2

python -m pytest tests/test_deliberations.py::TestRedaction -q --tb=short -p no:cacheprovider
# 20 passed, 1 warning

python -m pytest tests/test_governance_hooks.py::test_credential_scan_self_test_exit_zero tests/test_governance_hooks.py::test_credential_scan_stdin_blocks -q --tb=short -p no:cacheprovider
# 2 passed, 1 warning

python -m groundtruth_kb deliberations search "credential patterns canonical module redaction governance"
# No deliberations match 'credential patterns canonical module redaction governance'.
```

Pattern inventory was also inspected directly from source. Current counts match
the proposal: DB redaction has 18 entries at
`src/groundtruth_kb/db.py:4158-4189`; the Bash hook has 13 credential entries
and 2 output detectors at `templates/hooks/credential-scan.py:21-51`.

## Findings

### 1. High - Proposed canonical tuple shape breaks the Bash hook import path

**Evidence:**

- The proposal defines `CREDENTIAL_PATTERNS`, `PII_PATTERNS`,
  `REDACTION_PATTERNS`, and `BASH_EXTRAS` as
  `list[tuple[str, re.Pattern[str]]]`:
  `bridge/gtkb-credential-patterns-canonical-001.md:68-81`.
- The same proposal says `templates/hooks/credential-scan.py` should replace
  its inline `CREDENTIAL_PATTERNS` with a re-export from the canonical module,
  replace `OUTPUT_PATTERNS` with `BASH_EXTRAS`, and leave `_check_command()`
  unchanged: `bridge/gtkb-credential-patterns-canonical-001.md:156-164`.
- The current hook iterates `for pattern, description in CREDENTIAL_PATTERNS`
  and immediately calls `pattern.search(command)`, then returns the
  description: `templates/hooks/credential-scan.py:62-69`.

**Risk/impact:**

With the proposed import and unchanged `_check_command()`, `pattern` becomes a
string name, not a compiled regex. The hook would raise `AttributeError:
'str' object has no attribute 'search'` on the canonical import path, or would
produce unstable denial reasons if the tuple order were changed ad hoc. This is
a direct regression in the PreToolUse credential gate.

**Required action:**

Revise the migration contract so the canonical module exposes an adapter that
matches the hook contract, or revise the hook body and tests explicitly. Acceptable
shapes include:

- a single `PatternSpec` dataclass with `name`, `pattern`, `scope`, and optional
  `bash_description`, plus exported adapters such as
  `BASH_CREDENTIAL_PATTERNS: list[tuple[re.Pattern[str], str]]`; or
- keep `(name, pattern)` as the canonical storage shape, but update
  `_check_command()` to consume that shape and map names to stable user-facing
  descriptions.

The revised proposal must include a test that exercises the canonical import
path, not only the fallback path.

### 2. High - Fallback parity test does not prove standalone adopter behavior

**Evidence:**

- The proposal requires an inlined fallback when
  `groundtruth_kb.governance.credential_patterns` is not importable:
  `bridge/gtkb-credential-patterns-canonical-001.md:189-201`.
- The proposed fallback-equivalence test only compares structural tuples of
  `(name, pattern.pattern, pattern.flags)`:
  `bridge/gtkb-credential-patterns-canonical-001.md:244-248`.
- Current tests execute the hook but do not isolate the no-package adopter
  scenario: `tests/test_governance_hooks.py:167-188`.
- The existing hook already has an `ImportError` fallback for output helpers,
  proving standalone behavior is an established requirement:
  `templates/hooks/credential-scan.py:73-89`.

**Risk/impact:**

A structural comparison can pass while the copied hook still fails when run
outside the repository or without `groundtruth_kb` on `PYTHONPATH`. It also
does not check the hook's actual denial behavior, first-match ordering, or
description/reason output. That leaves the exact drift risk from the parent GO
partially open.

**Required action:**

Keep the fallback unless the project explicitly drops standalone hook
portability and documents that as a breaking behavior change. If the fallback
stays, add runtime coverage:

- run `credential-scan.py --self-test` in an environment where the package
  import is blocked or absent;
- run stdin blocking in the same fallback-only mode;
- compare canonical-import and fallback behavior against a fixture set that
  covers all Bash credential and output detector entries, including first
  matched pattern identity and denial reason.

The structural tuple parity test is useful, but it is not sufficient by itself.

### 3. Medium - Public `Match.matched_text` creates a new credential exposure surface

**Evidence:**

- The proposed public `Match` dataclass includes `matched_text`:
  `bridge/gtkb-credential-patterns-canonical-001.md:97-103`.
- Downstream consumers will include the future Write/Edit hook and skills:
  `bridge/gtkb-credential-patterns-canonical-001.md:120-125`.

**Risk/impact:**

Returning raw credential values in a public scan result makes it easy for hooks,
skills, debug logs, or bridge reports to accidentally persist the secret that
the scanner detected. This conflicts with the purpose of the module and raises
the blast radius for the downstream Phase A consumers.

**Required action:**

Remove `matched_text` from the public `Match` API or replace it with safe
metadata such as `matched_length`, `redaction`, and optional bounded context
with the match already redacted. If raw text is needed internally for
`redact()`, keep it private to the redaction implementation.

### 4. Medium - Test floor is lower than the stated coverage rule

**Evidence:**

- The proposal says new tests should include one positive and one negative per
  `CREDENTIAL_PATTERNS` and `PII_PATTERNS` entry:
  `bridge/gtkb-credential-patterns-canonical-001.md:210-211`.
- The same proposal sets the file-level floor at only `>=15` tests:
  `bridge/gtkb-credential-patterns-canonical-001.md:208` and
  `bridge/gtkb-credential-patterns-canonical-001.md:337`.
- The source inventory implies more than 15 tests are needed: 15 DB credential
  patterns plus 3 PII patterns, before preserving Bash-only patterns:
  `src/groundtruth_kb/db.py:4158-4189` and
  `templates/hooks/credential-scan.py:21-51`.

**Risk/impact:**

An implementation could satisfy the numeric exit criterion while leaving some
patterns without positive or negative coverage. That weakens the proposed parity
gate and makes future catalog edits easier to regress.

**Required action:**

Replace the fixed `>=15` floor with a generated or parameterized rule:

```text
at least one positive and one negative fixture for every canonical credential
and PII pattern, plus Bash-specific fixtures for BASH_EXTRAS and any hook-only
credential shapes
```

The test count should scale with `len(CREDENTIAL_PATTERNS + PII_PATTERNS)` and
with the hook adapter list.

## Responses to GO-Request Questions

1. The CREDENTIAL / PII / BASH_EXTRAS split is the right high-level shape. Do
   not collapse to a flat undifferentiated `PATTERNS` list. The implementation
   still needs a stable adapter for the Bash hook contract.
2. Fallback structural parity is not enough. Add fallback-only runtime tests and
   compare behavior across representative fixtures.
3. The inlined fallback remains necessary unless GT-KB intentionally abandons
   standalone copied-hook behavior. The current hook already treats missing
   package imports as a supported scenario.
4. Regex-equivalence review: only the AWS `AKIA[0-9A-Z]{16}` pattern appears
   exactly equivalent between DB and hook. The Anthropic patterns differ
   (`\d+` with 20+ token chars in DB versus exactly two digits and no minimum
   token length in the hook). Stripe/service key patterns overlap but differ
   on accepted prefixes and minimum lengths. Connection string and Azure key
   patterns are not equivalent. Keep distinct entries unless fixture-based
   proof shows equivalence.
5. The `>=15` test floor is not sufficient. Use per-pattern positive and
   negative coverage as the exit criterion.

## Required Revision

Submit `gtkb-credential-patterns-canonical-003.md` with:

1. A corrected canonical API and Bash hook adapter plan that cannot invert
   `(pattern, description)` and `(name, pattern)`.
2. Runtime tests for both canonical-import and fallback-only hook execution.
3. A public scan result shape that does not expose raw credential text.
4. A scalable per-pattern test requirement, not a fixed `>=15` floor.
5. Updated exit criteria reflecting the current 20-test `TestRedaction` class
   and the hook adapter/fallback behavior gates.

## Decision Needed From Owner

None. This is a technical NO-GO for revision by Prime.
