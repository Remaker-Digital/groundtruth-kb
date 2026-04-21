# NO-GO: WI-3142 Credential Scan Narrowing Re-Review

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Source reviewed:** `bridge/credential-scan-narrowing-009.md`
**Prior reviews:** `bridge/credential-scan-narrowing-002.md`, `bridge/credential-scan-narrowing-004.md`, `bridge/credential-scan-narrowing-006.md`, `bridge/credential-scan-narrowing-008.md`
**Verdict:** NO-GO

## Claim

The v5 proposal fixes important prior issues: quoted keys can include hyphens,
bare Edit payloads are now considered, the source example set is corrected to
five values, and the third-party deploy-secret claim is narrowed.

It is still not ready for GO because the newly hyphen-aware scope exposes an
unclassified Agent Red key-shaped value in `scripts/archive/`, the proposed
detector still misses key values followed by common punctuation, and the
reviewed fixture inventory still has path/count errors.

## Evidence

- `bridge/credential-scan-narrowing-009.md` proposes `_KEY_CHARS =
  [A-Za-z0-9_-]`, so the reviewed blast radius must include hyphen-containing
  key-shaped values.
- Verification command:
  `rg -n -o --pcre2 "(ar_user|ar_live|ar_spa_plat|ar_spa|ar_tenant|ar_widget|pk_live|arsk)_[A-Za-z0-9_-]{10,}" scripts -g "!scripts/deploy/**"`
  returned:
  - `scripts/archive/s157_kb_update.py:143`:
    `ar_spa_plat_mdbq-Sm3vE5Qj3d4H2Dk82juVsB42wg3`
  - `scripts/test_e2e_conversation_flows.py:46`:
    `pk_live_invalid_key_00000000`
- `scripts/archive/s157_kb_update.py:141-143` describes SPA platform admin
  credentials and includes the staging key in prose.
- Regex probe using the v5 proposed patterns returned:
  - quoted hyphen key: matched
  - bare Edit key: matched
  - env assignment: matched
  - YAML assignment: matched
  - `Staging key: ar_spa_plat_mdbq-Sm3vE5Qj3d4H2Dk82juVsB42wg3.`: no match
  - `KEY=ar_user_rema_yZR6wMz-VDlVJhbdRPW1Vh01TkytKcQ3;`: no match
- `tests/conftest.py:169-180` contains six key-shaped values, not seven.
  `arsk_completely_invalid_key` is not in `tests/conftest.py`; it appears in
  `tests/multi_tenant/test_middleware_pipeline.py:193`,
  `tests/test_conftest_smoke.py:94`, and `tests/test_error_handling.py:66`.
- Inventory probe with the v5 hyphen-aware family regex found:
  - old excluded files: 9 unique values / 12 matches
  - other tests: 43 unique values / 97 matches
  - `scripts/test_*`: 1 unique value
  After deduping the one shared `arsk_completely_invalid_key`, the fixture set
  is 52 unique values, not the 51 stated in
  `bridge/credential-scan-narrowing-009.md`.

## Findings

### P1 - Hyphen-aware audit misses an archive staging key

The proposal changed the key character class to include hyphens but did not
rerun the full audit with that character class. That misses an existing
hyphen-containing `ar_spa_plat_` value in `scripts/archive/s157_kb_update.py`.
The file text identifies it as a staging key, not merely a generic format
example.

**Risk/impact:** Prime can implement the proposed audit and remediation plan
while leaving a known Agent Red key-shaped value unclassified and potentially
undetected. This is the same class of blind spot this work item is trying to
close.

**Required action:** Add `scripts/archive/s157_kb_update.py:143` to the audit
and disposition it explicitly: remediate, path-and-value allow as historical
archive material, or open an owner-visible risk item. The implementation tests
or dry-run inventory should use the final hyphen-aware detector, not the older
underscore-only scan.

### P1 - Proposed detector misses keys followed by punctuation

The v5 pattern requires the character after a bare or assignment-form key to be
a quote, end of string, whitespace, or comma. Real prose and config can end a
key with punctuation such as `.` or `;`. The existing archive key is followed by
a period, and the proposed detector did not match it.

**Risk/impact:** The scanner can pass realistic leaks in Markdown/prose,
Python string text, shell/env fragments, or documentation comments even after
the "bare Edit" fix.

**Required action:** Replace the trailing delimiter with a boundary that means
"next character is not a valid key character", for example a negative lookahead
against `[A-Za-z0-9_-]`. Add hook-entrypoint tests for bare and assignment-form
keys followed by `.`, `;`, `)`, `]`, and newline.

### P2 - Fixture inventory metadata is still inconsistent

The proposal says `tests/conftest.py` has seven values and that the deduped
fixture set has 51 unique values. Current repo evidence shows six values in
`tests/conftest.py`, nine unique values across the old excluded files, 43
unique values in other tests with one shared value, and one approved
`scripts/test_*` value. That yields a 52-value fixture set.

**Risk/impact:** If implementation follows the stated 51-value count, one
reviewed fixture can be omitted. If it follows the table instead, the code will
not match the reviewed totals, defeating the purpose of the inventory coverage
test.

**Required action:** Regenerate the final inventory from the final detector and
make the proposal internally consistent: exact path-to-values table, exact
deduped fixture count, and coverage tests that assert the same scopes and
counts.

## Required Conditions For GO

1. Re-run the full audit with the final hyphen-aware detector and classify the
   `scripts/archive/s157_kb_update.py` key-shaped value.
2. Fix trailing-boundary detection so punctuation-suffixed bare/assignment keys
   are blocked.
3. Correct the fixture inventory paths and deduped value count, then align the
   inventory coverage test with that exact inventory.
4. Keep all prior requirements: remove the two blanket exclusions, use
   path-and-value scoped suppression, block real-looking keys in approved
   fixture paths, prevent global suppression, preserve FQDN/connection-string
   detection, remediate the evaluation defaults and Agent Red deploy value, and
   keep the third-party deploy-secret follow-up visible.

## Decision Needed From Owner

Owner decision is needed only if the archive staging key is intentionally
retained as an accepted historical artifact. Otherwise Prime should revise the
audit, detector boundary, and inventory count before implementation.
