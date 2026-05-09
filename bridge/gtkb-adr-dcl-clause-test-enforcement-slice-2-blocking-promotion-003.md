REVISED

# Implementation Proposal — GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT Slice 2 (Blocking Promotion, Revised-1)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-002.md` (F1 test-plan/regression contradiction; F2 underspecified `--advisory` bypass).
**Predecessors:** `-001` NEW; `-002` Codex NO-GO.
**Source advisory:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`
**Owner directive:** S336 "Band 3: Governance tightening" routes Slice 2 for pickup; standing "work independently on the bridge NO-GO items" scope authorizes this revision.

## Claim

This `-003` revises the Slice 2 implementation plan to address both Codex NO-GO findings:

- **F1 (test-plan/regression contradiction)**: the live regression at `tests/scripts/test_adr_dcl_clause_preflight.py:79-81` asserts every parsed clause has `enforcement_mode == "advisory_only_in_slice_1"`. The Slice-2 TOML flip will fail that assertion. The revised test plan explicitly **modifies** the existing schema regression to assert the new post-promotion state and adds positive coverage for the registry's mixed-mode capability (so future advisory-mode fixtures can coexist with the promoted blocking-mode fixtures during Slice-4 ratchet adoption).

- **F2 (`--advisory` bypass tightening)**: the flag is renamed to `--report-only` to remove the misleading "this is the advisory mode" framing, and its semantics are tightened: it produces diagnostic output ONLY and explicitly cannot satisfy GO/VERIFIED gates. The CLI's stdout under `--report-only` carries an unconditional banner declaring non-authorization. The rule update and codex-review-gate update both restate this constraint.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the test plan below maps tests to acceptance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this proposal touches platform code only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers; the registry transitions from `advisory_only_in_slice_1` to `blocking`.
- `GOV-STANDING-BACKLOG-001` — backlog as cross-session work authority; this slice consumes the top-priority Band 3 entry.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract; the "Clause-Test Preflight (Advisory; Slice 1)" subsection is rewritten by this slice.
- `.claude/rules/codex-review-gate.md` — review-gate constraints; Loyal Opposition's review obligations expand.
- `.claude/rules/canonical-terminology.md` — glossary alignment.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/deliberation-protocol.md` — Deliberation Archive protocol.
- `config/governance/adr-dcl-clauses.toml` — clause registry; modified.
- `scripts/adr_dcl_clause_preflight.py` — preflight CLI; modified.
- `tests/scripts/test_adr_dcl_clause_preflight.py` — focused test suite; **modified** (F1 fix) AND extended.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` — Slice 1 NEW with the slice plan that schedules Slice 2.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-002.md` — Codex GO on Slice 1.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-003.md` — Slice 1 post-impl report.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-004.md` — Codex VERIFIED on Slice 1.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-001.md` — superseded `-001` NEW.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-002.md` — Codex NO-GO addressed by this revision.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md` — source advisory.

## Owner Decisions / Input

The 2026-05-06 owner directive elevated `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` to top-priority Band 3. The S336 session directive ("Band 3: Governance tightening") routes Slice 2 pickup. No new owner-AUQ is requested; both Codex findings are mechanical implementation-plan defects that this revision corrects without requiring owner input.

The advisory's acceptance model (per `ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`) is preserved unchanged: blocking clauses must pass OR each gap must carry an explicit owner waiver. This revision tightens the implementation surface to make that contract enforceable.

## Findings Addressed

### F1 — Test-plan/regression contradiction

**Addressed by explicitly updating the existing schema regression and adding positive coverage for the promoted state plus mixed-mode coexistence.**

The current schema regression (`tests/scripts/test_adr_dcl_clause_preflight.py:79-81`) is:

```python
assert c.enforcement_mode == "advisory_only_in_slice_1", (
    f"Slice 1 contract violation: clause {c.clause_id} has enforcement_mode={c.enforcement_mode}"
)
```

This assertion is part of `test_clauses_load_with_required_schema` (the schema-regression test). It encodes Slice 1's contract literally, and the Slice 2 flip will fail it. The revised plan addresses this in three explicit steps:

1. **Replace** the literal-equality assertion with a value-set assertion that codifies the post-promotion state:

   ```python
   VALID_ENFORCEMENT_MODES = {"blocking", "advisory"}
   for c in clauses:
       assert c.enforcement_mode in VALID_ENFORCEMENT_MODES, (
           f"clause {c.clause_id} has invalid enforcement_mode={c.enforcement_mode!r}"
       )
   ```

   This change is explicit. The test plan now declares **1 existing test modified** (no longer "0 existing tests modified") and the modification is bounded to those three lines plus the import-line constant addition.

2. **Add** a new test `test_all_slice_1_fixtures_promoted_to_blocking` that asserts every fixture spec_id from the Slice 1 set has `enforcement_mode == "blocking"` after promotion. This is the post-state regression.

3. **Add** a new test `test_mixed_enforcement_modes_supported` that constructs a fixture clause with `enforcement_mode == "advisory"` (lowercase, no `_only_in_slice_1` suffix) and asserts the loader accepts it. This proves the registry can carry both modes simultaneously, which is required for Slice 4's ratchet adoption (new fixtures begin in advisory before promotion).

### F2 — `--advisory` bypass underspecified

**Addressed by renaming the flag, tightening its semantics, and making non-authorization explicit in CLI output, the rule, and the codex-review-gate.**

Original `-001` plan had `--advisory` as an always-exit-0 override under "owner-discretion" or "operator-discretion." That framing was too broad. The revised plan:

1. **Renames** the flag to `--report-only`. The new name signals diagnostic intent and avoids confusion with the registry's `enforcement_mode = "advisory"` value.

2. **Tightens semantics**: `--report-only` produces the existing markdown output but emits an additional unconditional banner at the top:

   ```text
   ⚠ --report-only mode: this output IS DIAGNOSTIC ONLY and CANNOT satisfy GO/VERIFIED.
   ⚠ Mandatory gate runs require the default (no-flag) invocation. Cite an explicit
   ⚠ owner-waiver line per blocking gap if a real bypass is required:
   ⚠   Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>
   ```

   The CLI exit code under `--report-only` is the same exit code the default invocation would produce (so operators can see "what would happen" without authorizing). This eliminates the "exit 0 even though there's a real gap" silent-bypass concern Codex flagged.

3. **Rule update tightening** in `.claude/rules/file-bridge-protocol.md`: the new "Clause-Test Preflight (Mandatory; Slice 2)" section explicitly states:
   - The mandatory gate runs without flags. Exit 5 = blocking gap; exit 0 = pass.
   - `--report-only` is for diagnostic inspection ONLY.
   - The only valid bypass is an explicit owner-waiver line in the bridge content, not a CLI flag.
   - GO/VERIFIED verdicts must cite the unflagged invocation's output.

4. **Codex-review-gate update tightening** in `.claude/rules/codex-review-gate.md`: the bullet now reads:
   - "Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>` (no `--report-only`). Treat exit 5 as a NO-GO blocker unless the proposal carries an explicit owner-waiver line per blocking gap. The `--report-only` flag is diagnostic only and cannot stand in for the mandatory check."

## Slice 2 Scope (revised)

### Change 1 — Promote `enforcement_mode` from advisory to blocking (unchanged from `-001`)

`config/governance/adr-dcl-clauses.toml`: change `enforcement_mode = "advisory_only_in_slice_1"` to `enforcement_mode = "blocking"` for each of the 5 currently-registered clauses. The `severity = "blocking"` field remains. Future Slice-4 ratchet additions begin with `enforcement_mode = "advisory"` (lowercase, no slice-tag suffix).

### Change 2 — CLI exit-code semantics (revised)

`scripts/adr_dcl_clause_preflight.py`:

- Default invocation: iterate `ClauseResult` list. For each `must_apply` clause whose `enforcement_mode == "blocking"` AND whose `evidence_found` is False AND whose bridge content does NOT include an explicit owner-waiver line citing the clause_id, accumulate as a gap. Exit 5 if gaps non-empty; exit 0 if empty.
- Markdown output emits a "Blocking Gaps" subsection enumerating the offending clauses and their `evidence_required` text.
- `--report-only` flag (renamed from `--advisory`): same evaluation logic, same exit code as the default invocation, BUT prepends the unconditional 4-line non-authorization banner shown in F2 above. The flag does not change the exit code; it is a diagnostic-output-only flag.
- Clauses with `enforcement_mode == "advisory"` (lowercase, post-Slice-4-ratchet pattern) are evaluated and reported but never contribute to the gap accumulator regardless of evidence_found state.

### Change 3 — Tests (revised; F1 fix)

`tests/scripts/test_adr_dcl_clause_preflight.py`:

**Modified** (1 test):
- `test_clauses_load_with_required_schema` — replace the literal-equality assertion (`enforcement_mode == "advisory_only_in_slice_1"`) with a value-set assertion (`enforcement_mode in {"blocking", "advisory"}`). 3 lines changed plus a constant addition.

**Added** (7 tests):
- `test_all_slice_1_fixtures_promoted_to_blocking` — F1 positive coverage: assert every fixture has `enforcement_mode == "blocking"` post-promotion.
- `test_mixed_enforcement_modes_supported` — F1 mixed-mode coexistence: loader accepts both `blocking` and `advisory` values.
- `test_blocking_evidence_gap_exits_nonzero` — Change-2 positive: exit 5 when must_apply blocking has no evidence.
- `test_blocking_evidence_present_exits_zero` — Change-2 positive: exit 0 when evidence found.
- `test_report_only_flag_does_not_change_exit_code` — F2: `--report-only` returns the same exit code as the default invocation (i.e., exit 5 with gap, exit 0 without).
- `test_report_only_emits_non_authorization_banner` — F2: markdown stdout under `--report-only` contains the non-authorization banner text.
- `test_explicit_owner_waiver_clears_blocking_gap` — Change-2: owner-waiver line in bridge content makes a must_apply gap non-blocking.

**Total Slice 2 test delta:** 1 modified + 7 added = 8 changes. (Previous claim of "6 added; 0 modified" was incorrect; this revised count is honest.)

### Change 4 — Rule update (revised; F2 fix)

`.claude/rules/file-bridge-protocol.md`: replace the existing `## Clause-Test Preflight (Advisory; Slice 1)` section with `## Clause-Test Preflight (Mandatory; Slice 2)`. New section content includes:

- The default invocation is the mandatory gate. Exit 5 = blocking gap; exit 0 = pass.
- `--report-only` is diagnostic-output-only and cannot satisfy GO/VERIFIED.
- The only valid bypass for a real blocking gap is an explicit owner-waiver line:

  ```text
  Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>
  ```

- GO/VERIFIED verdicts must cite the **default-invocation** output, not `--report-only` output.
- Future Slice 3 (LO-verdict template integration) and Slice 4 (ratchet adoption) build on this gate.
- Cites `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` as the originating bridge thread (post-VERIFIED).

### Change 5 — Loyal Opposition obligation (revised; F2 fix)

`.claude/rules/codex-review-gate.md`: add a single bullet to the existing "If Loyal Opposition is reviewing an implementation proposal" enumeration:

- "Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>` (no `--report-only`). Treat exit 5 as a NO-GO blocker unless the proposal carries an explicit owner-waiver line per blocking gap. The `--report-only` flag is diagnostic-only and cannot stand in for the mandatory check. Include the resulting `Clause Applicability` section (and `Blocking Gaps` subsection if non-empty) in any `GO`/`VERIFIED` verdict."

### Files Changed (revised count)

- `config/governance/adr-dcl-clauses.toml` — 5 single-field flips (`enforcement_mode`).
- `scripts/adr_dcl_clause_preflight.py` — exit-code logic + `--report-only` flag + non-authorization banner.
- `tests/scripts/test_adr_dcl_clause_preflight.py` — **1 modified test (F1 fix)** + 7 new tests.
- `.claude/rules/file-bridge-protocol.md` — section header rename + content rewrite (F2 tightening).
- `.claude/rules/codex-review-gate.md` — single bullet addition (F2 tightening).
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-{NNN}.md` (this thread).
- `bridge/INDEX.md` — REVISED line for `-003` added at top of this entry.

## Out Of Scope (unchanged from `-001`)

- Slice 3: clause-test matrix integration into Loyal Opposition verdict templates and Prime Builder proposal templates.
- Slice 4: ratchet adoption — backfill more ADR/DCL records into the registry beyond the current 5.
- Slice 5: optional semantic-search/LLM-assist for candidate discovery.
- New clauses or clause-schema changes (Slice 2 promotes existing clauses only).
- Wiring the preflight into the `bridge-compliance-gate.py` PreToolUse hook.
- Modifying the `bridge_applicability_preflight.py` exit-code semantics.

## Specification-Derived Test Plan (revised)

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX entry | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` | preflight_passed: true |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-impl report carries spec-to-test mapping + executed evidence | section present |
| **T-promotion-1** | Change 1 | `grep -c 'enforcement_mode = "blocking"' config/governance/adr-dcl-clauses.toml` | returns 5 |
| **T-promotion-2** | Change 1 (regression) | `grep -c 'advisory_only_in_slice_1' config/governance/adr-dcl-clauses.toml` | returns 0 |
| **T-schema-mixed-modes** | F1 fix | `test_clauses_load_with_required_schema` modified to assert `enforcement_mode in {"blocking", "advisory"}`; `test_mixed_enforcement_modes_supported` covers loader acceptance of both | PASS |
| **T-schema-promoted** | F1 positive coverage | `test_all_slice_1_fixtures_promoted_to_blocking` asserts every Slice-1 fixture has `enforcement_mode == "blocking"` | PASS |
| **T-cli-blocking-gap** | Change 2 | `test_blocking_evidence_gap_exits_nonzero` | PASS (exit 5) |
| **T-cli-evidence-present** | Change 2 | `test_blocking_evidence_present_exits_zero` | PASS (exit 0) |
| **T-cli-report-only-exit-code** | F2 fix | `test_report_only_flag_does_not_change_exit_code` | PASS (exit 5 with gap; exit 0 without) |
| **T-cli-report-only-banner** | F2 fix | `test_report_only_emits_non_authorization_banner` | PASS (banner text present in stdout) |
| **T-cli-waiver** | Change 2 | `test_explicit_owner_waiver_clears_blocking_gap` | PASS (exit 0; waiver cited) |
| **T-classification-regression** | Change 3 (regression) | `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q` | All 13 tests pass (5 from Slice 1 unchanged + 1 modified + 7 new) |
| **T-self-blocking** | Change 1 dogfood | After implementation: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` | exit 0 (this proposal satisfies all 5 promoted blocking clauses) |
| **T-rule-update** | Change 4 (F2) | `grep "## Clause-Test Preflight (Mandatory; Slice 2)" .claude/rules/file-bridge-protocol.md` AND `grep "report-only" .claude/rules/file-bridge-protocol.md` | both match present after impl |
| **T-codex-gate-update** | Change 5 (F2) | `grep "adr_dcl_clause_preflight" .claude/rules/codex-review-gate.md` AND `grep "report-only" .claude/rules/codex-review-gate.md` | both match present after impl |
| **T-isolation-1** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All Slice-2 changes touch only `config/`, `scripts/`, `tests/scripts/`, `.claude/rules/` | `git diff --stat` confirms |
| **T-secrets-1** | Credential safety | `python -m groundtruth_kb secrets scan --paths <changed files> --json --fail-on=` returns `finding_count: 0` | True |

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Five-clause `enforcement_mode = "blocking"` promotion accepted
- [ ] Modified `test_clauses_load_with_required_schema` (F1 fix) accepted
- [ ] `--report-only` rename + non-authorization banner + same-exit-code semantics (F2 fix) accepted
- [ ] Owner-waiver line format accepted (`Owner waiver: <clause_id> — <DELIB-ID> — <reason>`)
- [ ] Rule and codex-review-gate updates accepted

VERIFIED when:

- [ ] All test IDs pass
- [ ] CLI dogfood self-check (T-self-blocking) passes against this very bridge thread
- [ ] Codex VERIFIED on the post-impl report

## Risk and Rollback (revised)

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Promotion creates false-positive blocks for legitimate proposals | Medium | Medium | Slice-4 ratchet adoption can downgrade specific clauses to `enforcement_mode = "advisory"`. Owner-waiver line provides per-bridge bypass without code change. |
| Operator runs `--report-only` and mistakes diagnostic output for an authorizing pass | Low | High | The non-authorization banner is unconditional and prefixed to every `--report-only` invocation's stdout. The codex-review-gate rule explicitly states `--report-only` cannot satisfy the mandatory check. |
| Slice-2 implementation itself fails the post-promotion clause preflight | Low | Low | T-self-blocking dogfood test runs the CLI against this bridge thread; advisory-mode self-check at filing time already shows 0 gaps. |
| `enforcement_mode` field semantics drift between TOML, CLI, and tests | Low | Low | F1 fix introduces a `VALID_ENFORCEMENT_MODES` set used by the CLI loader, the schema regression, and the test fixture; single source of truth. |

Rollback: `git revert` of the Slice 2 commit reverts (a) the 5 `enforcement_mode` field flips, (b) the CLI exit-code logic, (c) the `--report-only` flag and non-authorization banner, (d) the modified schema test, (e) the rule-section rename, and (f) the codex-review-gate bullet. Slice 1 behavior is fully restored.

## Pre-Filing Preflight

This `-003` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

This `-003` will also be evaluated by `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` (Slice 1 advisory-mode CLI). Expected: 5 must_apply clauses, evidence found for all 5 (this proposal cites bridge/INDEX.md, declares in-root paths, includes a Specification Links section, includes a Specification-Derived Test Plan section, and addresses the standing-backlog visibility clause via the explicit Band-3-priority citation).

## Provenance

| Source | Reference |
|---|---|
| Codex NO-GO triggering this revision | `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-002.md` (F1 test-plan/regression contradiction; F2 underspecified `--advisory` bypass) |
| Source advisory | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md` |
| Slice 1 closure | `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` through `-004` |
| Owner top-priority directive (2026-05-06) | `memory/work_list.md` §"TOP — Active workstreams" |
| Owner directive (S336) | "Band 3: Governance tightening" |
| Slice 1 clause registry (current) | `config/governance/adr-dcl-clauses.toml` (5 clauses, all `enforcement_mode = "advisory_only_in_slice_1"`) |
| Slice 1 preflight CLI (current) | `scripts/adr_dcl_clause_preflight.py` (exits 0 unconditionally per Slice-1 contract) |
| Slice 1 schema regression (target of F1 fix) | `tests/scripts/test_adr_dcl_clause_preflight.py:79-81` |
| Companion future bridges | Slice 3 LO-verdict-template integration; Slice 4 ratchet adoption; Slice 5 semantic discovery |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
