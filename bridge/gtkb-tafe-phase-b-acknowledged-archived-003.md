NEW

bridge_kind: prime_impl_report
Document: gtkb-tafe-phase-b-acknowledged-archived
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-14 UTC
Responds to: bridge/gtkb-tafe-phase-b-acknowledged-archived-002.md (GO)
Recommended commit type: feat:
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T19-13-11Z-prime-builder-B-01a235
author_model: Claude Opus 4.8
author_model_version: 4.8
author_model_configuration: Claude Code headless bridge auto-dispatch worker (harness B); GTKB_BRIDGE_POLLER_RUN_ID set; workspace E:\GT-KB

# WI-4566 Phase B — Implementation Report: TAFE completeness oracle rules 2+3 + acknowledged-archived config

## Summary

Implemented the GO'd proposal's **core deliverable** — the DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001
v2 classification inputs (rule 2 implementation-sibling, rule 3 acknowledged-archived config) plus the
governed config listing the 68 owner-acknowledged slugs. Verified end-to-end: the live completeness
oracle now reports **`lost_blocks` 74 → 0** with `archived_blocks` correctly absorbing all 74 (562 → 636),
35 tests pass (10 new spec-derived), and both ruff gates are clean. The oracle's read-only contract is
preserved (AST guards intact).

Two operational steps in the proposal (Step 4 extra_block phantom-name fix; Step 5 stale-shadow
re-ingest) are reported as **residual** below: Step 4 is blocked by a real serialized-INDEX-writer
tooling gap (no rename/remove command; raw INDEX edit guarded), and Step 5 is a TAFE-shadow mutation
outside this packet's three authorized `target_paths`. Neither affects the completeness gate
(`IndexCompletenessReport.ok` gates on `lost_blocks` only, which is now 0). WI-4510 governed cutover
remains HELD and OUT OF SCOPE.

## Specification Links

(Carried forward from the GO'd proposal -001.)

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — landed governing requirement; rules 1→2→3
  precedence, gate-on-lost_blocks, read-only contract. **Implemented here.**
- `ADR-TAFE-SLICE-C-INGESTION-001` — the DCL derives from it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical; oracle stays read-only (no write
  surface added; verified by AST guards).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests + executed evidence (below).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the acknowledged-archived config is the auditable
  artifact-lifecycle disposition record.
- `GOV-STANDING-BACKLOG-001` — WI-4566; the 68-slug bulk acknowledgement is owner-approved (DELIB).
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — cutover is the dual-write program's terminal step.

## Spec-to-Test Mapping

All tests in `groundtruth-kb/tests/test_tafe_index_completeness.py` (35 passed). New tests derive from
`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2:

| Spec clause | Test(s) |
|---|---|
| Rule 2: non-terminal candidate WITH terminal `-implementation` sibling → archived | `test_rule2_non_terminal_candidate_with_terminal_impl_sibling_archived`, `test_rule2_sibling_latest_version_decides` |
| Rule 2: non-terminal sibling / no sibling → stays lost | `test_rule2_non_terminal_candidate_with_non_terminal_sibling_stays_lost`, `test_rule2_no_sibling_stays_lost` |
| Rule 3: slug in acknowledged config → archived | `test_rule3_acknowledged_slug_archived` |
| Rule 3: slug not listed → stays lost | `test_rule3_not_listed_stays_lost` |
| Rule 3: config-absent ⇒ graceful (no crash) | `test_rule3_config_absent_graceful` |
| Rule 3: malformed config ⇒ graceful | `test_rule3_malformed_config_graceful` |
| Precedence: rule 1 (terminal token) wins over config | `test_precedence_terminal_token_wins_over_config` |
| Precedence: rule 2 archives before config needed | `test_precedence_sibling_archives_before_config_needed` |
| DCL v2 assertions 1+2 (module references `-implementation` + config path) | `test_module_reads_acknowledged_config_path` |
| Read-only contract preserved (no open/write/subprocess/mutation; no canonical-INDEX literal) | `test_module_is_read_only`, `test_module_no_subprocess_no_mutation` (existing; still pass) |

## Commands Executed

```text
python -m pytest groundtruth-kb/tests/test_tafe_index_completeness.py -q
  => 35 passed in 2.77s

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py groundtruth-kb/tests/test_tafe_index_completeness.py
  => All checks passed!

python -m ruff format --check <same two files>
  => 2 files already formatted

python -m groundtruth_kb flow cutover-evidence --json   (live INDEX, read-only)
  => completeness.lost_blocks: 0   (was 74)
     completeness.archived_blocks: 636   (was 562; +74 reclassified)
     completeness.extra_blocks: 1  ['sp1-dispatch-reliability-prime-handoff']  (residual; see Step 4)
     parity.ok: true
     fidelity.ok: false   (pre-existing stale shadow; see Step 5)
```

## Requirement Sufficiency

(Carried forward.) **Existing requirements sufficient.** `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2
(landed, specified) defines rules 2+3 and the acknowledged-archived config input; this report implements
them. No further formal-artifact capture was required before implementation.

## Owner Decisions / Input

(Carried forward from the GO'd proposal; all owner approvals already captured as durable DELIBs — no new
owner decision is introduced by this report.)

- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614` — owner chose acknowledged-archived + sibling rule
  (AskUserQuestion).
- `DELIB-WI4546-DCL-COMPLETENESS-V2-APPROVE-20260614` — DCL v2 approval (AskUserQuestion).
- `DELIB-WI4546-PHASE-B-LANE-RECONCILIATION-20260614` — lane re-homed under WI-4566 (AskUserQuestion).
- WI-4510 cutover is NOT authorized by this work; it requires its own fresh owner AUQ
  (`DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614`).

## Prior Deliberations

- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614`; `DELIB-WI4546-DCL-COMPLETENESS-V2-APPROVE-20260614`;
  `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614`; `DELIB-WI4546-PAUTH-AUTHORIZE-20260614`.
- Phase A: `gtkb-tafe-shadow-index-reconciliation` VERIFIED@-006 (634 → 74).
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` (WI-4510 HOLD).

## Implemented Changes (Steps 1–3, complete + verified)

- **Step 1 — oracle rule 2 (sibling).** `groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py`:
  new `_candidate_is_archived()` evaluates a `<slug>-implementation` sibling (looked up in the on-disk
  `expected_docs` map); when the sibling's latest version is terminal (by the rule-1 `_classify_candidate`
  test), the candidate classifies `archived`. Read-only (`Path.read_text`).
- **Step 2 — oracle rule 3 (acknowledged config).** New `_load_acknowledged_slugs()` reads
  `config/governance/tafe-acknowledged-archived-bridges.toml` via `Path.read_text` + `tomllib.loads`
  (string parse — no `open()`, so the module's read-only AST guard is preserved). Precedence
  1 (terminal) → 2 (sibling) → 3 (acknowledged) → else `lost`. Config-absent / malformed ⇒ graceful
  (empty set, no crash). The classification loop in `index_completeness_report` now delegates to
  `_candidate_is_archived`.
- **Step 3 — config.** New `config/governance/tafe-acknowledged-archived-bridges.toml`:
  `schema_version = 1` + 68 `[[acknowledged]]` entries (the exact residual rule-3 slug set computed from
  the live oracle), each with a `reason` citing `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614`.

## Residual / Findings (Steps 4–5 NOT completed by this dispatched worker)

### F1 — Step 4 (extra_block phantom-name fix): blocked by a serialized-INDEX-writer tooling gap

Severity: P3 (non-gating). The proposal's Step 4 — correcting the phantom INDEX `Document:` entry
`sp1-dispatch-reliability-prime-handoff` (line 845; its version line + on-disk file are correctly
`gtkb-sp1-dispatch-reliability-prime-handoff`) — could not be performed with sanctioned tooling:

- `gt bridge index` exposes only `add-document` and `set-status`; **neither can rename or remove a
  Document name.** `add-document gtkb-sp1-...` would add the correct slug but leave the phantom
  `sp1-...` entry (still an extra_block).
- `gt bridge reconcile` is read-only (audit / index-chain / dry-run packet).
- Raw `bridge/INDEX.md` edits are blocked by GTKB-INDEX-WRITE-GUARD (WI-4481).

The extra_block does **not** gate `IndexCompletenessReport.ok` (the oracle gates on `lost_blocks`, now 0),
so this residual does not affect the DCL-v2 deliverable. **Recommended backlog capture (self-improvement
directive):** add a serialized-INDEX-writer command to correct/remove a phantom `Document:` name while
honoring GTKB-INDEX-WRITE-GUARD (e.g. `gt bridge index rename-document <old> <new>` or
`remove-document <slug>`), so phantom extra_blocks can be reconciled without a raw edit.

### F2 — Step 5 (stale-shadow re-ingest): deferred — outside authorized target_paths

Severity: P3 (non-gating, pre-existing). `gt flow ingest-bridge-index --apply` mutates the TAFE shadow
store (not one of this packet's three authorized `target_paths`), and the `fidelity.ok: false`
mismatches are pre-existing stale-shadow conditions, not introduced by this change. Deferred to avoid
authorization overreach by a headless worker. Full cutover-evidence `ok` (the WI-4510 precondition)
therefore remains False pending F1 + F2; WI-4510 cutover is HELD/OUT OF SCOPE regardless.

## Recommended Commit Type

`feat:` — adds the implementation-sibling + acknowledged-archived-config classification inputs to the
Slice B oracle plus the governed disposition config (new capability + governed data).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py` (M; +107 / −10) — rules 2+3.
- `config/governance/tafe-acknowledged-archived-bridges.toml` (new; 297 lines) — 68 acknowledged slugs.
- `groundtruth-kb/tests/test_tafe_index_completeness.py` (M) — 10 new spec-derived tests (35 total).

Source commit at implementation: `1913766fd` (changes uncommitted per dispatched-worker discipline).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
