NEW

# Implementation Proposal — GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT Slice 2 (Blocking Promotion)

**Author:** Prime Builder (Claude, harness B)
**Drafted:** 2026-05-08
**Type:** Net-additional implementation under the parent thread
`gtkb-adr-dcl-clause-test-enforcement` (Slice 1 VERIFIED at `-004`).
**Source advisory:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md`
**Owner directive:** 2026-05-06 top-priority directive added `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` to the standing backlog as Band 3 governance-tightening work; S336 owner directive ("Band 3: Governance tightening") routes this slice for pickup in this session.

## Claim

Slice 1 established the clause registry, the discovery CLI, and the advisory-mode reporting surface. Slice 2 promotes the registry-derived clause coverage to a **mandatory** gate per the Slice 1 plan ("block when blocking clauses lack evidence"). This proposal defines the promotion semantics, narrowly scopes the CLI exit-code change, updates the rule corpus to remove the "advisory only" disclaimer, and adds tests proving the gate blocks evidence-gap cases while preserving the must_apply / may_apply / not_applicable classification.

The five clauses currently in `config/governance/adr-dcl-clauses.toml` already carry `severity = "blocking"`. Slice 1 enforced none of them mechanically; the CLI always returned exit 0. Slice 2 makes those five clauses into hard blockers: when the CLI runs against a bridge file and a must_apply blocking clause has no evidence (and no explicit owner waiver), the CLI exits non-zero, and Loyal Opposition's review must NO-GO/refuse-VERIFIED unless the gap is closed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed through `bridge/INDEX.md`; this proposal is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every implementation proposal cites its governing specs; this section is the response.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the Specification-Derived Test Plan section maps tests to acceptance criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application files under `applications/`; this proposal touches platform code only (`scripts/`, `tests/scripts/`, `.claude/rules/`, `config/governance/`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact-oriented governance; the clause registry is a durable artifact promoted to enforcement.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifacts, lifecycle states, traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers; the clause registry transitions from `advisory_only_in_slice_1` to `blocking`.
- `GOV-STANDING-BACKLOG-001` — backlog as cross-session work authority; this slice consumes the top-priority entry per S332 directive Band 3.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract; the "Clause-Test Preflight (Advisory; Slice 1)" subsection is updated by this slice.
- `.claude/rules/codex-review-gate.md` — review-gate constraints; Loyal Opposition's review obligations expand to include the clause preflight.
- `.claude/rules/canonical-terminology.md` — glossary alignment.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `.claude/rules/deliberation-protocol.md` — Deliberation Archive protocol.
- `config/governance/adr-dcl-clauses.toml` — clause registry; modified by this slice (enforcement_mode promotion).
- `scripts/adr_dcl_clause_preflight.py` — preflight CLI; modified by this slice (exit-code semantics).
- `tests/scripts/test_adr_dcl_clause_preflight.py` — focused test suite; extended by this slice.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` — Slice 1 NEW filing with the slice plan that schedules Slice 2 as the blocking-promotion bridge thread.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-002.md` — Codex GO on Slice 1.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-003.md` — Slice 1 post-impl report.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-004.md` — Codex VERIFIED on Slice 1.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md` — source advisory authorizing the program.

## Owner Decisions / Input

The 2026-05-06 owner directive elevated `GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001` to top-priority Band 3 governance work in `memory/work_list.md` §"TOP — Active workstreams". The S336 session directive ("Band 3: Governance tightening") routes Slice 2 for pickup in this session under the standing "work independently" scope. No new owner-AUQ is requested; Slice 2 is a deterministic promotion of the existing Slice 1 fixtures (already at `severity = "blocking"`) from advisory to enforced.

If Codex review surfaces any of the five clauses as having Slice-1-feedback applicability/evidence-pattern issues (false positives, false negatives) that would make the promotion premature, Slice 2 should hold those clauses at advisory and ratchet only the clean ones. That decision is delegated to Codex's review of this proposal.

## Slice 2 Scope

### Change 1 — Promote `enforcement_mode` from advisory to blocking

`config/governance/adr-dcl-clauses.toml`: change `enforcement_mode = "advisory_only_in_slice_1"` to `enforcement_mode = "blocking"` for each of the 5 currently-registered clauses. The `severity = "blocking"` field already exists; the `enforcement_mode` flip is the single mechanical change that promotes from advisory to enforced. Preserve the schema for future per-clause hold-points (e.g., a `enforcement_mode = "advisory"` for newly-added clauses still being tuned).

### Change 2 — CLI exit-code semantics

`scripts/adr_dcl_clause_preflight.py`: replace the unconditional `return 0` paths with logic that:

- Iterates the evaluated `ClauseResult` list.
- For each `must_apply` clause whose `enforcement_mode == "blocking"` AND whose `evidence_found` is False AND whose bridge content does NOT include an explicit owner-waiver line citing the clause_id, accumulate it as a gap.
- After iteration, exit `0` when the gap list is empty; exit `5` (matches the `bridge_applicability_preflight.py` convention for "blocking applicability gap") when the gap list is non-empty.
- The CLI emits the existing "Clause Applicability" markdown section regardless of exit code, so the operator sees the same diagnostic plus a new "Blocking Gaps" subsection enumerating the offending clauses.
- Add an opt-out flag `--advisory` that restores Slice-1-era behavior (always exit 0). This is a safety hatch for transitional review packets and for Slice 4 ratchet-adoption work where new clauses begin in advisory mode.

The `--advisory` flag is owner-discretion and is documented in the rule update (Change 4).

### Change 3 — Tests

Extend `tests/scripts/test_adr_dcl_clause_preflight.py`:

- `test_blocking_evidence_gap_exits_nonzero` — fixture clause registry with a single `enforcement_mode = "blocking"` clause whose evidence pattern does not match the input bridge content; assert CLI exits 5.
- `test_blocking_evidence_present_exits_zero` — same fixture but bridge content includes the satisfying evidence pattern; assert CLI exits 0.
- `test_advisory_flag_overrides_blocking` — same evidence-gap fixture as the first test but invoke with `--advisory`; assert CLI exits 0 and the markdown output preserves the gap classification.
- `test_explicit_owner_waiver_clears_gap` — bridge content includes a line of the form `Owner waiver: <clause_id> — <DELIB-ID> — <reason>`; assert CLI exits 0 even though `evidence_found` is False.
- `test_advisory_clauses_do_not_block` — registry mixes `enforcement_mode = "advisory"` clauses with `enforcement_mode = "blocking"` clauses; only blocking-with-gap drives the exit code.
- `test_must_apply_classification_unchanged_after_promotion` — regression: the existing must_apply/may_apply/not_applicable classification logic is unchanged; only the exit code semantics differ. (Carries forward the 6 existing Slice-1 tests; they continue to pass.)

### Change 4 — Rule update

`.claude/rules/file-bridge-protocol.md`: replace the existing `## Clause-Test Preflight (Advisory; Slice 1)` section with `## Clause-Test Preflight (Mandatory; Slice 2)`. New section content:

- Describes the preflight as a hard gate for `must_apply` blocking-severity clauses.
- Documents the explicit owner-waiver line format: `Owner waiver: <clause_id> — <DELIB-ID> — <one-line reason>`.
- Documents the `--advisory` opt-out as a safety hatch (operator-discretion, not a permanent bypass).
- Cites `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` as the originating bridge thread (post-VERIFIED).
- Notes that future slice work (Slice 3 LO verdict template integration, Slice 4 ratchet adoption) is out of Slice 2's scope.

### Change 5 — Loyal Opposition obligation

`.claude/rules/codex-review-gate.md`: add a single bullet to the existing "If Loyal Opposition is reviewing an implementation proposal" enumeration: "Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>`. Treat exit 5 as a `NO-GO` blocker unless the proposal carries an explicit owner-waiver line for each gap. Include the resulting `Clause Applicability` section in any `GO`/`VERIFIED` verdict."

### Files Changed

- `config/governance/adr-dcl-clauses.toml` — 5 single-field flips (`enforcement_mode`).
- `scripts/adr_dcl_clause_preflight.py` — exit-code logic + `--advisory` flag.
- `tests/scripts/test_adr_dcl_clause_preflight.py` — 6 new tests; 0 existing tests modified.
- `.claude/rules/file-bridge-protocol.md` — section header rename + content rewrite.
- `.claude/rules/codex-review-gate.md` — single bullet addition.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-{NNN}.md` (this thread).
- `bridge/INDEX.md` — new thread entry.

## Out Of Scope

- Slice 3: clause-test matrix integration into Loyal Opposition verdict templates and Prime Builder proposal templates.
- Slice 4: ratchet adoption — backfill more ADR/DCL records into the registry beyond the current 5.
- Slice 5: optional semantic-search/LLM-assist for candidate discovery.
- New clauses or clause-schema changes (Slice 2 promotes existing clauses only; tighten/replace clauses in Slice 4).
- Wiring the preflight into the `bridge-compliance-gate.py` PreToolUse hook (separate future bridge if/when desired; current pattern keeps mechanical preflights as Loyal-Opposition-run rather than Write-time-blocked).
- Modifying the `bridge_applicability_preflight.py` exit-code semantics (which already uses 5 for blocking gaps; this slice harmonizes to that convention).

## Specification-Derived Test Plan

| Test ID | Spec Coverage | Procedure | Expected |
|---|---|---|---|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-impl report carries spec-to-test mapping + executed evidence | section present |
| **T-promotion-1** | Change 1 | `grep -c 'enforcement_mode = "blocking"' config/governance/adr-dcl-clauses.toml` | returns 5 |
| **T-promotion-2** | Change 1 (regression) | `grep -c 'advisory_only_in_slice_1' config/governance/adr-dcl-clauses.toml` | returns 0 |
| **T-cli-blocking-gap** | Change 2 | `tests/scripts/test_adr_dcl_clause_preflight.py::test_blocking_evidence_gap_exits_nonzero` | PASS (exit 5) |
| **T-cli-evidence-present** | Change 2 | `tests/scripts/test_adr_dcl_clause_preflight.py::test_blocking_evidence_present_exits_zero` | PASS (exit 0) |
| **T-cli-advisory-flag** | Change 2 | `tests/scripts/test_adr_dcl_clause_preflight.py::test_advisory_flag_overrides_blocking` | PASS (exit 0 even with gap) |
| **T-cli-waiver** | Change 2 | `tests/scripts/test_adr_dcl_clause_preflight.py::test_explicit_owner_waiver_clears_gap` | PASS (exit 0; waiver line cited) |
| **T-cli-mixed-modes** | Change 2 | `tests/scripts/test_adr_dcl_clause_preflight.py::test_advisory_clauses_do_not_block` | PASS |
| **T-classification-regression** | Change 3 (regression) | `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q` | All 12 tests pass (6 from Slice 1 + 6 new) |
| **T-self-blocking** | Change 1 dogfood | After implementation: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` | exit 0 (this proposal itself satisfies all applicable blocking clauses) |
| **T-rule-update** | Change 4 | `grep "## Clause-Test Preflight (Mandatory; Slice 2)" .claude/rules/file-bridge-protocol.md` | match present after impl; no `(Advisory; Slice 1)` heading remains |
| **T-codex-gate-update** | Change 5 | `grep "adr_dcl_clause_preflight" .claude/rules/codex-review-gate.md` | match present after impl |
| **T-isolation-1** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All Slice-2 changes touch only `config/`, `scripts/`, `tests/scripts/`, `.claude/rules/`; no `applications/Agent_Red/` content | `git diff --stat` confirms |
| **T-secrets-1** | Credential safety | `python -m groundtruth_kb secrets scan --paths <changed files> --json --fail-on=` returns `finding_count: 0` | True |

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Five-clause `enforcement_mode = "blocking"` promotion accepted (or partial promotion if Codex flags any clause as Slice-1-feedback-incomplete)
- [ ] CLI exit-code semantics accepted (exit 5 for blocking gap; `--advisory` opt-out honored)
- [ ] Owner-waiver line format accepted (`Owner waiver: <clause_id> — <DELIB-ID> — <reason>`)
- [ ] Rule update accepted (Mandatory ↔ Advisory section header swap; codex-review-gate bullet)
- [ ] Test plan accepted (12-test suite; 6 new + 6 existing regression)

VERIFIED when:

- [ ] All test IDs pass
- [ ] CLI dogfood self-check (T-self-blocking) passes against this very bridge thread
- [ ] Live `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` exits 0
- [ ] Codex VERIFIED on the post-impl report

## Risk and Rollback

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| Promotion creates false-positive blocks for legitimate proposals | Medium | Medium | `--advisory` opt-out flag; explicit owner-waiver line format; Slice-2 review can downgrade specific clauses to `enforcement_mode = "advisory"` if Slice-1-feedback identifies false-positive patterns. |
| Loyal Opposition obligation expansion adds friction to review cycle | Low | Low | Preflight runtime is negligible; existing `bridge_applicability_preflight.py` already runs in every Codex review per the file-bridge-protocol. |
| Slice-2 implementation itself fails clause preflight (dogfood deadlock) | Low | Low | T-self-blocking test runs the CLI against the Slice-2 thread; if any clause fires a blocking gap, the proposal must add the satisfying evidence before submission. |
| `enforcement_mode` field semantics drift between TOML and CLI | Low | Low | Test fixture verifies exact field name and values; rule update documents both modes; future clauses default to `advisory` until owner-promoted. |

Rollback: `git revert` of the Slice 2 commit reverts (a) the 5 `enforcement_mode` field flips, (b) the CLI exit-code logic, (c) the `--advisory` flag, (d) the rule-section rename, and (e) the codex-review-gate bullet. Slice 1 behavior is fully restored.

## Pre-Filing Preflight

This `-001` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` after INDEX update. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

This `-001` will also be evaluated by `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion` (Slice 1 advisory-mode CLI). Expected: 5 must_apply clauses, evidence found for all 5 (this proposal cites bridge/INDEX.md, declares in-root paths, includes a Specification Links section, includes a Specification-Derived Test Plan section, and addresses the standing-backlog visibility clause via the explicit Band-3-priority citation).

## Provenance

| Source | Reference |
|---|---|
| Source advisory | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/ADR-DCL-CLAUSE-TEST-ENFORCEMENT-ADVISORY-2026-05-06.md` |
| Slice 1 NEW (slice plan) | `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` §"Slice Plan" |
| Slice 1 GO | `bridge/gtkb-adr-dcl-clause-test-enforcement-002.md` |
| Slice 1 post-impl | `bridge/gtkb-adr-dcl-clause-test-enforcement-003.md` |
| Slice 1 VERIFIED | `bridge/gtkb-adr-dcl-clause-test-enforcement-004.md` |
| Owner top-priority directive (2026-05-06) | `memory/work_list.md` §"TOP — Active workstreams" |
| Owner directive (S336) | "Band 3: Governance tightening" routes Slice 2 pickup in this session |
| Slice 1 rule note (transitional) | `.claude/rules/file-bridge-protocol.md` §"Clause-Test Preflight (Advisory; Slice 1)" — replaced by Slice 2 |
| Slice 1 clause registry | `config/governance/adr-dcl-clauses.toml` (5 clauses, all `severity = "blocking"`, all `enforcement_mode = "advisory_only_in_slice_1"`) |
| Slice 1 preflight CLI | `scripts/adr_dcl_clause_preflight.py` (exits 0 unconditionally per Slice-1 contract) |
| Slice 1 tests | `tests/scripts/test_adr_dcl_clause_preflight.py` (6 tests pass) |
| Companion future bridges | Slice 3 LO-verdict-template integration; Slice 4 ratchet adoption; Slice 5 semantic discovery — all post-Slice-2 future threads |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
