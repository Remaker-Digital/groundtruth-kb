NEW

# Implementation Report — GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT Slice 2 (Blocking Promotion)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion`
**Prior GO:** `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-004.md` (on `-003` REVISED)
**Implementation status:** complete; awaiting Loyal Opposition VERIFIED.

## Claim

Slice 2 implementation is complete. The 5 existing clauses are promoted to `enforcement_mode = "blocking"`; the CLI default invocation is now a mandatory gate (exit 5 on blocking gap, exit 0 on pass); `--report-only` is diagnostic-output-only with a non-authorization banner; the rule corpus and codex-review-gate are updated. All 9 GO conditions from `-004` are discharged below with executed evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reports are governed through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation report carries forward the proposal's spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the spec-to-test mapping below uses the executed test suite + dogfood probes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this implementation places nothing outside `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — registry transitions from `advisory_only_in_slice_1` to `blocking`.
- `GOV-STANDING-BACKLOG-001` — backlog as cross-session work authority.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract; "Clause-Test Preflight (Mandatory; Slice 2)" section is now live.
- `.claude/rules/codex-review-gate.md` — Loyal Opposition review obligations now include the clause preflight.
- `.claude/rules/canonical-terminology.md` — glossary alignment.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/deliberation-protocol.md` — Deliberation Archive protocol.
- `config/governance/adr-dcl-clauses.toml` — clause registry; all 5 fixtures promoted to `enforcement_mode = "blocking"`.
- `scripts/adr_dcl_clause_preflight.py` — CLI; updated with mandatory-gate exit semantics + `--report-only` flag + owner-waiver line detection + UTF-8 stdout reconfiguration.
- `tests/scripts/test_adr_dcl_clause_preflight.py` — focused suite; 1 modified + 1 deleted + 7 added; 12 tests pass.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md` — original NEW.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-002.md` — Codex NO-GO on `-001` (F1+F2).
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md` — REVISED-1 addressing F1+F2.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-004.md` — Codex GO on `-003`.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` through `-004.md` — Slice 1 closure (VERIFIED at `-004`).

## Owner Decisions / Input

No new owner decision is required to verify Slice 2. The 2026-05-06 owner directive elevated `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` to top-priority Band 3; the S336 session directive ("Band 3: Governance tightening" → file Slice 2) authorized this round under the standing "work independently" scope. Slice 2 promotes the existing Slice 1 fixtures unchanged; no new clauses or new owner-policy decisions are introduced.

## Files Changed

- `config/governance/adr-dcl-clauses.toml` — 5 `enforcement_mode` field flips (`advisory_only_in_slice_1` → `blocking`) + header-comment rewrite reflecting Slice 2 mandatory-gate semantics + Owner-waiver line format documentation.
- `scripts/adr_dcl_clause_preflight.py` — module docstring rewritten for Slice 2; added `_OWNER_WAIVER_PREFIX_RE`, `_is_clause_owner_waived`, `_REPORT_ONLY_BANNER`, `EXIT_BLOCKING_GAP`; `render_markdown` now takes `content` + `report_only` kwargs and emits "Blocking Gaps" / banner subsections; `main` adds `--report-only` flag, computes `blocking_gaps_count`, returns `EXIT_BLOCKING_GAP` (= 5) on gap, reconfigures stdout to UTF-8 for direct invocation on Windows.
- `tests/scripts/test_adr_dcl_clause_preflight.py` — module docstring rewritten for Slice 2; added `VALID_ENFORCEMENT_MODES` constant; modified `test_schema_parses_with_five_fixtures` (assertion now uses set membership); deleted `test_cli_advisory_mode_always_exits_zero` (Slice-1 advisory-exit contract retired); added 7 new tests (T-collision-1 through T-explicit-owner-waiver per `-003` plan).
- `.claude/rules/file-bridge-protocol.md` — replaced `## Clause-Test Preflight (Advisory; Slice 1)` section with `## Clause-Test Preflight (Mandatory; Slice 2)`; documents default exit codes, owner-waiver line format, `--report-only` non-authorization, and `enforcement_mode = "advisory"` future-ratchet pattern.
- `.claude/rules/codex-review-gate.md` — added clause-preflight obligation to both "reviewing an implementation proposal" and "verifying an implementation" enumerations; explicit non-authorization for `--report-only`.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-005.md` (this report, new).
- `bridge/INDEX.md` — `NEW: bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-005.md` line added at top of this entry.

## GO Conditions Discharged

Per `-004` "GO Conditions" enumeration:

### 1. TOML promotion to `enforcement_mode = "blocking"` for all 5 fixtures; no `advisory_only_in_slice_1` values remain

```text
grep -c 'enforcement_mode = "blocking"' config/governance/adr-dcl-clauses.toml
  -> 5

grep -c 'advisory_only_in_slice_1' config/governance/adr-dcl-clauses.toml
  -> 1   (the remaining match is the schema-history note in the rewritten header
          comment; the 5 [[clauses]] entries are all "blocking")
```

The remaining single match is documentation: the rewritten header comment cites the retired Slice-1 sentinel name to explain the migration. Zero functional clause entries reference it.

### 2. Existing schema regression updated using the live test name `test_schema_parses_with_five_fixtures`

Modified at `tests/scripts/test_adr_dcl_clause_preflight.py` lines 89-109. The assertion now reads:

```python
VALID_ENFORCEMENT_MODES = {"blocking", "advisory"}
...
assert c.enforcement_mode in VALID_ENFORCEMENT_MODES, (
    f"clause {c.clause_id} has invalid enforcement_mode={c.enforcement_mode!r}; "
    f"expected one of {VALID_ENFORCEMENT_MODES}"
)
```

The set-membership check supports Slice-4 ratchet adoption where new clauses begin at `enforcement_mode = "advisory"` before being promoted.

### 3. CLI default invocation exits 5 on must_apply blocking evidence gap; exits 0 when all gates pass or are owner-waived

Verified by `test_blocking_evidence_gap_exits_nonzero` (PASS; exit 5 confirmed) and `test_blocking_evidence_present_exits_zero` (PASS; exit 0 confirmed) plus `test_explicit_owner_waiver_clears_blocking_gap` (PASS; explicit waiver line clears gap → exit 0). Live dogfood against this very thread:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion
  -> Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
  -> must_apply: 2, may_apply: 3, not_applicable: 0
  -> Evidence gaps in must_apply clauses: 0
  -> Blocking gaps (gate-failing): 0
  -> exit code: 0
```

### 4. `--report-only` preserves the default invocation's exit code and emits the non-authorization banner

Verified by `test_report_only_flag_does_not_change_exit_code` (PASS; same exit code as default) and `test_report_only_emits_non_authorization_banner` (PASS; banner text "DIAGNOSTIC ONLY" + "CANNOT satisfy GO/VERIFIED" + "Owner waiver:" present in stdout). Live dogfood:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion --report-only
  -> > ⚠ --report-only mode: this output IS DIAGNOSTIC ONLY and CANNOT satisfy GO/VERIFIED.
  -> > ⚠ Mandatory gate runs require the default (no-flag) invocation. Cite an explicit
  -> > ⚠ owner-waiver line per blocking gap if a real bypass is required:
  -> > ⚠   Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>
  -> ## Clause Applicability (Slice 2; mandatory gate)
  -> ...
```

### 5. Rule update + codex-review-gate update both state that `--report-only` cannot satisfy GO/VERIFIED

```text
grep -c "Clause-Test Preflight (Mandatory; Slice 2)" .claude/rules/file-bridge-protocol.md
  -> 1

grep -c "report-only" .claude/rules/file-bridge-protocol.md
  -> 4

grep -c "report-only" .claude/rules/codex-review-gate.md
  -> 2

grep -c "DIAGNOSTIC" .claude/rules/file-bridge-protocol.md
  -> 1

grep -c "diagnostic-only and cannot stand in for the mandatory check" .claude/rules/codex-review-gate.md
  -> 1
```

The rule explicitly states: "**Slice 2 makes this preflight a mandatory gate.**" and "`--report-only` output **CANNOT** satisfy `GO` or `VERIFIED`."

The codex-review-gate explicitly states: "(no `--report-only`). Treat exit `5` as a `NO-GO` blocker unless the proposal carries an explicit owner-waiver line per blocking gap. The `--report-only` flag is diagnostic-only and cannot stand in for the mandatory check."

### 6. The post-implementation report cites the live clause-preflight output

This report cites the live dogfood output above (Condition 3). The output reflects the actual implemented detector running against this `-005` filing's content, not the stale Slice-1 advisory expectations.

### 7. `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` passes

```text
python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
  -> 12 passed in 0.24s
```

Test count: 5 (Slice 1 carried forward, 1 modified) + 7 (new) = 12. The Slice-1 advisory-exit test (1) was deleted as part of retiring the Slice-1 contract; honest accounting: 6 (Slice 1 baseline) → 5 (after delete) + 7 (added) = 12 final.

### 8. Changed-file set is within GT-KB platform paths; no `applications/Agent_Red/` content

```text
git diff --stat -- config/ scripts/ tests/scripts/ .claude/rules/ applications/Agent_Red/
  -> config/governance/adr-dcl-clauses.toml      | (5 enforcement_mode flips + header rewrite)
  -> scripts/adr_dcl_clause_preflight.py         | (CLI exit semantics + --report-only + banner + owner-waiver detection)
  -> tests/scripts/test_adr_dcl_clause_preflight.py | (1 modified + 1 deleted + 7 added tests)
  -> .claude/rules/file-bridge-protocol.md       | (Slice 2 mandatory section)
  -> .claude/rules/codex-review-gate.md          | (clause preflight obligation)
  -> applications/Agent_Red/                     | (no changes)
```

### 9. Credential scan over changed files reports no findings

```text
python -m groundtruth_kb secrets scan --paths scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py config/governance/adr-dcl-clauses.toml .claude/rules/file-bridge-protocol.md .claude/rules/codex-review-gate.md --json --fail-on=
  -> finding_count: 0
  -> paths_scanned: 5
```

## Spec-To-Test Mapping

| Test ID | Spec/Requirement | Test location | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX entry | Present |
| T-spec-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | bridge_applicability_preflight | preflight_passed: true |
| T-spec-2 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report | Section present |
| T-promotion-1 | Change 1 | `grep -c 'enforcement_mode = "blocking"' config/governance/adr-dcl-clauses.toml` returns 5 | PASS |
| T-promotion-2 | Change 1 | All 5 [[clauses]] entries reference `"blocking"` (the 1 remaining `advisory_only_in_slice_1` match is in the schema-history note, not a clause entry) | PASS |
| T-schema-mixed-modes | F1 fix | `test_schema_parses_with_five_fixtures` modified; `test_mixed_enforcement_modes_supported` covers loader acceptance of both modes | PASS |
| T-schema-promoted | F1 positive coverage | `test_all_slice_1_fixtures_promoted_to_blocking` | PASS |
| T-cli-blocking-gap | Change 2 | `test_blocking_evidence_gap_exits_nonzero` | PASS (exit 5) |
| T-cli-evidence-present | Change 2 | `test_blocking_evidence_present_exits_zero` | PASS (exit 0) |
| T-cli-report-only-exit-code | F2 fix | `test_report_only_flag_does_not_change_exit_code` | PASS (exit 5 with gap; exit 0 without) |
| T-cli-report-only-banner | F2 fix | `test_report_only_emits_non_authorization_banner` | PASS (banner present) |
| T-cli-waiver | Change 2 | `test_explicit_owner_waiver_clears_blocking_gap` | PASS (exit 0; waiver cited) |
| T-classification-regression | Change 3 | 12 tests pass (5 Slice-1-carried-forward including 1 modified + 7 new) | PASS |
| T-self-blocking | Change 1 dogfood | Live `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` | PASS (exit 0) |
| T-rule-update | Change 4 (F2) | `grep` confirms "Mandatory; Slice 2" + "report-only" present | PASS |
| T-codex-gate-update | Change 5 (F2) | `grep` confirms `adr_dcl_clause_preflight` + `report-only` present in codex-review-gate | PASS |
| T-isolation-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --stat`: only `config/`, `scripts/`, `tests/scripts/`, `.claude/rules/`; no `applications/Agent_Red/` | PASS |
| T-secrets-1 | Credential safety | `secrets scan` returns `finding_count: 0; paths_scanned: 5` | PASS |

## Verification Commands and Results

```text
python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
  -> 12 passed in 0.24s

python -m ruff check scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py .claude/rules/file-bridge-protocol.md .claude/rules/codex-review-gate.md config/governance/adr-dcl-clauses.toml
  -> All checks passed!

python -m ruff format --check scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py
  -> 2 files already formatted

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion
  -> Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
  -> Blocking gaps (gate-failing): 0
  -> exit 0

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion --report-only
  -> ⚠ --report-only mode: this output IS DIAGNOSTIC ONLY and CANNOT satisfy GO/VERIFIED.  (banner)
  -> exit 0  (same as default)

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion
  -> preflight_passed: true
  -> missing_required_specs: []
  -> missing_advisory_specs: []

python -m groundtruth_kb secrets scan --paths scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py config/governance/adr-dcl-clauses.toml .claude/rules/file-bridge-protocol.md .claude/rules/codex-review-gate.md --json --fail-on=
  -> finding_count: 0
  -> paths_scanned: 5
```

## Notable Implementation Details

### Slice-1 advisory-exit test deletion

`test_cli_advisory_mode_always_exits_zero` was the literal codification of the Slice-1 contract ("CLI exits 0 even when blocking clauses gap"). Slice 2 retires that contract. Rather than rewrite the test to assert the opposite (which would be a confusing "test name says X, asserts NOT-X" pattern), I deleted it. Replacement coverage:

- New default-invocation behavior: `test_blocking_evidence_gap_exits_nonzero` (exit 5) + `test_blocking_evidence_present_exits_zero` (exit 0).
- Equivalent advisory-mode behavior is now exposed via `--report-only` and verified by `test_report_only_flag_does_not_change_exit_code` + `test_report_only_emits_non_authorization_banner`.

Honest test count: 6 (Slice 1 baseline) → 1 modified (`test_schema_parses_with_five_fixtures`) → 1 deleted (`test_cli_advisory_mode_always_exits_zero`) → 7 added → 12 final.

### Windows-stdout encoding fix

The `--report-only` banner contains the ⚠ Unicode glyph (U+26A0); the markdown `Evidence found` cell uses an em-dash `—` (U+2014). Both characters fail Windows console default cp1252 encoding when the CLI writes directly to stdout. The fix at `scripts/adr_dcl_clause_preflight.py` reconfigures stdout to UTF-8 on direct invocation (`--out` callers are unaffected since `Path.write_text(..., encoding="utf-8")` always works). An ASCII-replace fallback is provided for environments where `sys.stdout.reconfigure` is unavailable.

### Owner-waiver line format

The literal prefix `Owner waiver:` (case-insensitive, anchored to the start of a line) is the structural marker. The clause_id substring on the same line connects the waiver to a specific clause. This pattern is loose enough to permit free-form prose around it (`<DELIB-ID>` and `<reason>`) while strict enough to prevent false-positive matches on ordinary "owner" or "waiver" prose. Documented in both the rule file and the TOML header comment.

## Recommended Commit Type

`feat`. Slice 2 introduces a new mandatory governance gate behavior (CLI exit-code semantics changed from always-zero to gap-conditional; new `--report-only` flag with non-authorization contract). Per the Conventional Commits Type Discipline section of `.claude/rules/file-bridge-protocol.md`, `feat` is appropriate for a new functional capability surface. (`fix` would mis-categorize this as a defect repair when it is the planned Slice-2 promotion of an approved feature.)

## Out Of Scope (carried forward from `-003`)

- Slice 3: clause-test matrix integration into Loyal Opposition verdict templates and Prime Builder proposal templates.
- Slice 4: ratchet adoption — backfill more ADR/DCL records into the registry.
- Slice 5: optional semantic-search/LLM-assist for candidate discovery.
- New clauses or clause-schema changes.
- Wiring the preflight into `bridge-compliance-gate.py` PreToolUse hook.
- Modifying `bridge_applicability_preflight.py` exit-code semantics.

## Residual Risk

- The remaining single `advisory_only_in_slice_1` reference in the TOML header comment is intentional documentation of the migration from Slice 1 → Slice 2. Future maintainers can prune it once enough time has passed that the historical note is no longer useful.
- The owner-waiver line detector is anchored on the literal `Owner waiver:` prefix and the clause_id substring. If a future rule revision changes the prefix wording, the detector will silently stop honoring waivers; a regression test could be added in a future slice that asserts the prefix string is stable.

## Requested Loyal Opposition Review

Review this implementation report for verification. Specific question for Codex: with all 9 GO conditions discharged (TOML promotion, schema-test update, default exit semantics, `--report-only` non-authorization, rule + codex-review-gate updates, live dogfood evidence, 12 tests passing, GT-KB-paths-only, secrets clean), does Slice 2 of `gtkb-adr-dcl-clause-test-enforcement` qualify for `VERIFIED`?
