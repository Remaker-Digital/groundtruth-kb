GO-PENDING: Loyal Opposition review required before any file mutation.

# WI-5640 — Secret-scanner fixture placeholder sweep (A+B): annotate all remaining flagged test-fixture lines

- **Work Item:** WI-5640
- **Type:** Implementation Proposal (Prime Builder -> Loyal Opposition)
- **Status:** NEW
- **Date:** 2026-07-20
- **Author role:** Prime Builder
- **Bridge thread:** gtkb-wi5640-scanner-fixture-placeholder-sweep
- **Precedent:** WI-4880 (bridge/gtkb-wi4880-intake-test-scanner-fp-suppression-002.md, GO) + owner deliberation DELIB-20266274 — the `# placeholder` trailing comment is the codebase-standard suppression mechanism that `scripts/scan_secrets.py` honors for documentation/example fixtures.
- **Companion:** WI-5410 (bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md) already proposes the `test_cli_deliberations.py:181` fix; this sweep covers that line **plus** the remaining MEDIUM fixtures and the doc-quote lines, per owner directive "A + B".

## 1. Problem statement

The local pre-commit hook (`.githooks/pre-commit` -> `scripts/scan_secrets.py --staged`) blocks `git commit` whenever a staged change touches any of four files containing pre-existing **test fixtures** that match secret patterns. None of the matches are real credentials. Re-running the actual scanner against the four files yields exactly **10 findings**:

| # | File | Line | Sev | Pattern | Fixture |
|---|------|------|-----|---------|---------|
| 1 | groundtruth-kb/tests/test_cli_deliberations.py | 181 | HIGH | AWS Access Key | `AKIAIOSFODNN7EXAMPLE` (AWS canonical doc example) |
| 2 | groundtruth-kb/tests/test_cli_deliberations.py | 181 | MEDIUM | Secret Key Assignment | (same line, 2nd pattern) |
| 3 | applications/Agent_Red/tests/test_host/test_build_contract.py | 634 | MEDIUM | Secret Key Assignment | `AGENT_RED_TEST_SECRET=super-secret-value` |
| 4 | applications/Agent_Red/tests/test_host/test_build_contract.py | 661 | MEDIUM | Secret Key Assignment | (assert of same fixture) |
| 5 | platform_tests/scripts/test_cloud_harness_base.py | 447 | MEDIUM | Secret Key Assignment | `api_key=abcdefghijklmnop` sentinel |
| 6 | platform_tests/scripts/test_cloud_harness_base.py | 449 | MEDIUM | Bearer Token | `Bearer ignored-authorization-sentinel` |
| 7 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 72 | HIGH | AWS Access Key | doc **quote** of the flagged line |
| 8 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 72 | MEDIUM | Secret Key Assignment | (same line, 2nd pattern) |
| 9 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 103 | HIGH | AWS Access Key | doc **quote** (diff "- " line) |
| 10 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 103 | MEDIUM | Secret Key Assignment | (same line, 2nd pattern) |

(The .md's line 104 — the proposed "+ " fixed line — already carries `# placeholder` and is correctly skipped.)

## 2. Root cause

All ten are intentional, non-secret **test fixtures / documentation quotes**, not credentials:

- `AKIAIOSFODNN7EXAMPLE` is AWS's own published documentation example key (see the extensive comment at test_cli_deliberations.py:176-180).
- `AGENT_RED_TEST_SECRET=super-secret-value` is a self-evidently fake env fixture used to assert the sync script does **not** print secrets (test_build_contract.py:653 asserts it is absent from output).
- `api_key=abcdefghijklmnop` / `Bearer ignored-authorization-sentinel` are explicit "sentinel"/"ignored" fixtures in a harness test double.
- The two .md lines are **quotations** of the flagged source line inside a bridge document describing the fix.

The scanner's skip list (scan_file, ~L220-240) skips any line whose lowercased stripped text contains a marker such as `placeholder`. These fixture lines pre-date the scanner and carry no marker, so the first staged touch of each file trips the hook.

## 3. Proposed change (minimal, additive, non-breaking)

Append the codebase-standard `# placeholder` marker. For Python source lines this is a **trailing comment** (does not alter the string value, so `in`-based substring assertions and the env-file content written by the fixture are unchanged). For the two .md documentation-quote lines, append a parenthetical `(placeholder)` so the marker substring is present without altering the quoted code semantics.

### 3.1 groundtruth-kb/tests/test_cli_deliberations.py — line 181
```text
-        secret = "AKIAIOSFODNN7EXAMPLE"
+        secret = "AKIAIOSFODNN7EXAMPLE"  # placeholder
```
*(Identical to the WI-5410 proposal; included here so the sweep is self-contained. If WI-5410 lands first, this becomes a no-op / already-applied.)*

### 3.2 applications/Agent_Red/tests/test_host/test_build_contract.py — lines 634, 661
```text
-        source.write_text("VITE_API_BASE=/api\nAGENT_RED_TEST_SECRET=super-secret-value\n", encoding="utf-8")
+        source.write_text("VITE_API_BASE=/api\nAGENT_RED_TEST_SECRET=super-secret-value\n", encoding="utf-8")  # placeholder
```
```text
-            assert "AGENT_RED_TEST_SECRET=super-secret-value" in target.read_text(encoding="utf-8")
+            assert "AGENT_RED_TEST_SECRET=super-secret-value" in target.read_text(encoding="utf-8")  # placeholder
```
The `# placeholder` is a Python comment **outside** the string literal; the env content written to `.env.local` and the asserted substring are byte-for-byte unchanged.

### 3.3 platform_tests/scripts/test_cloud_harness_base.py — lines 447, 449
```text
-            "message": "named selector rejected; api_key=abcdefghijklmnop" + " x" * 400,
+            "message": "named selector rejected; api_key=abcdefghijklmnop" + " x" * 400,  # placeholder
```
```text
-            "authorization": "Bearer ignored-authorization-sentinel",
+            "authorization": "Bearer ignored-authorization-sentinel",  # placeholder
```
Trailing comments after dict-literal entries; the JSON body under test is unchanged.

### 3.4 bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md — lines 72, 103
```text
-   secret = "AKIAIOSFODNN7EXAMPLE" inside test_add_content_file_redaction,
+   secret = "AKIAIOSFODNN7EXAMPLE" inside test_add_content_file_redaction, (placeholder)
```
```text
--        secret = "AKIAIOSFODNN7EXAMPLE"
+-        secret = "AKIAIOSFODNN7EXAMPLE"   # (placeholder)
```
These are documentation quotes; appending the marker text keeps the quote legible while satisfying the scanner's substring skip.

## 4. Why annotation (not rotation / removal / scanner change)

- **No real credentials exist** — there is nothing to rotate. The fixtures are load-bearing test inputs.
- **Removal breaks tests** — the assertions depend on these exact fixture strings.
- **Scanner change is out of scope** — modifying `scan_secrets.py` would weaken detection for real secrets and require its own review; the marker mechanism already exists precisely for this case.
- **Annotation is the established precedent** — WI-4880 + DELIB-20266274 explicitly designate `# placeholder` as the codebase-standard mechanism.

## 5. Verification plan (post-GO)

1. Apply the four edits.
2. `python scripts/_tmp_real_scan.py` -> expect **0 findings** across the four files (re-runs the real `scan_file`).
3. `python -m pytest groundtruth-kb/tests/test_cli_deliberations.py applications/Agent_Red/tests/test_host/test_build_contract.py platform_tests/scripts/test_cloud_harness_base.py -q --tb=short` -> confirm no regressions. (Agent Red suite may still hit the pre-existing `jwt` ModuleNotFoundError environment issue noted in WI-5381; that is external to this change.)
4. `ruff check` / `ruff format --check` on the three touched .py files.
5. Stage the files and run `python scripts/scan_secrets.py --staged` -> expect clean (unblocks `git commit`).
6. File implementation-report bridge entry (WI-5640-002).

## 6. Files touched (all PROTECTED — mutation gated on this GO)

- `groundtruth-kb/tests/test_cli_deliberations.py`
- `applications/Agent_Red/tests/test_host/test_build_contract.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md`

## 7. Risk / impact

- **Severity: low.** Pure additive comment/doc-text annotations; no runtime behavior change.
- **Reversibility:** trivially revertible (comment removal).
- **Blast radius:** none beyond the four files; no API, schema, or dependency change.

## 8. Decision requested

**GO / NO-GO** on applying the four placeholder-annotation edits above.
