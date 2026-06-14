NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: c2f8c28a-bc49-4158-a509-1ae540eec86d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (harness B); owner-authorized Phase B; explanatory output style

# WI-4546 Phase B — TAFE completeness oracle: implementation-sibling rule + acknowledged-archived config (dispose residual 74 lost_blocks)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-7-RECONCILIATION-WI-4546
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4546
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py", "config/governance/tafe-acknowledged-archived-bridges.toml", "groundtruth-kb/tests/test_tafe_index_completeness.py"]

## Summary

WI-4546 Phase A (oracle terminal-token refinement) is VERIFIED (`gtkb-tafe-shadow-index-reconciliation`
@-006; live `lost_blocks` 634 -> 74). Phase B disposes the residual 74 (all historical/abandoned, none
live) per owner strategy `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614` and the landed
`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2, reaching a clean cutover-evidence run:

- **Rule 2 (implementation-sibling):** classify a non-terminal orphan whose `<slug>-implementation`
  sibling's latest on-disk version is terminal as `archived` (clears the 6 bucket-A slugs; general for
  future split proposal/impl threads).
- **Rule 3 (acknowledged-archived config):** classify a candidate whose slug is listed in the new
  governed `config/governance/tafe-acknowledged-archived-bridges.toml` as `archived` (clears the 68
  bucket-B+C slugs).
- Create that config with the 68 owner-acknowledged slugs (each with a `reason`).
- Fix the 1 `extra_block` (the phantom INDEX `Document:` entry `sp1-dispatch-reliability-prime-handoff`
  whose on-disk file is `gtkb-sp1-dispatch-reliability-prime-handoff`) via the serialized INDEX writer.
- Re-ingest the stale shadow (`gt flow ingest-bridge-index --apply`) and re-run `gt flow cutover-evidence`
  until clean.

Expected result: `lost_blocks` 74 -> 0, `extra_blocks` 1 -> 0, parity ok, contention-zero, fidelity ok
=> cutover-evidence `ok` (the WI-4510 precondition). WI-4510 governed cutover remains HELD and OUT OF
SCOPE (needs a fresh owner AUQ per `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614`).

## Specification Links

- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) — landed governing requirement defining rules 2+3.
- `ADR-TAFE-SLICE-C-INGESTION-001` — the DCL derives from it.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical; oracle stays read-only; the `extra_block`
  fix uses the serialized INDEX writer (`gt bridge index ...`), never a raw edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived tests + executed evidence (below).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the acknowledged-archived config is the auditable
  artifact-lifecycle disposition record for the historical/abandoned threads.
- `GOV-STANDING-BACKLOG-001` — WI-4546; the 68-slug bulk acknowledgement is owner-approved (DELIB).
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — cutover is the dual-write program's terminal step.

## Prior Deliberations

- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614` — owner chose acknowledged-archived + sibling rule.
- `DELIB-WI4546-DCL-COMPLETENESS-V2-APPROVE-20260614` — owner approved DCL v2 (rules 2+3).
- `DELIB-WI4546-DCL-COMPLETENESS-APPROVE-20260614` — DCL v1 (terminal-token rule).
- `DELIB-WI4546-RECONCILE-STRATEGY-REFINE-ORACLE-20260614`; `DELIB-WI4546-PAUTH-AUTHORIZE-20260614`.
- `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614` (WI-4510 HOLD); `DELIB-20263195` (cutover sequence).
- Phase A: `gtkb-tafe-shadow-index-reconciliation` VERIFIED@-006.

## Owner Decisions / Input

- `DELIB-WI4546-PHASE-B-DISPOSITION-STRATEGY-20260614` — strategy (AskUserQuestion: "Acknowledged-archived
  record + sibling rule").
- `DELIB-WI4546-DCL-COMPLETENESS-V2-APPROVE-20260614` — DCL v2 approval (AskUserQuestion: "Approve & insert
  v2 as shown").
- WI-4510 cutover is NOT authorized by this proposal; it requires its own fresh owner AUQ.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2 (landed, specified)
defines rules 2+3 and the acknowledged-archived config input; this proposal implements them. No further
formal-artifact capture is required before implementation.

## Proposed Change

- **Step 1 — oracle rule 2 (sibling).** In `tafe_index_completeness.py`, when a candidate's latest version
  is non-terminal, look up the `<slug>-implementation` expected document; if its latest on-disk version is
  terminal (by the v1 terminal-token test), classify the candidate `archived`. Read-only.
- **Step 2 — oracle rule 3 (acknowledged config).** Load `config/governance/tafe-acknowledged-archived-bridges.toml`
  (read-only, `tomllib`); a candidate slug in the acknowledged set classifies `archived`. Precedence:
  rule 1 (terminal token) -> rule 2 (sibling) -> rule 3 (acknowledged) -> else `lost`. Config-absent =>
  graceful (no acknowledged entries; no crash).
- **Step 3 — config.** Create `config/governance/tafe-acknowledged-archived-bridges.toml` with the 68
  owner-acknowledged slugs (each `slug` + `reason`), plus `schema_version`.
- **Step 4 — extra_block fix.** Correct the phantom INDEX `Document:` entry
  `sp1-dispatch-reliability-prime-handoff` -> `gtkb-sp1-dispatch-reliability-prime-handoff` via the
  serialized INDEX writer (`gt bridge index ...`); never a raw `bridge/INDEX.md` edit.
- **Step 5 — re-ingest + re-verify.** `gt flow ingest-bridge-index --apply` to clear the stale-shadow
  fidelity_mismatches + contention; re-run `gt flow cutover-evidence --json` until `ok`
  (`lost_blocks == [] && extra_blocks == [] && parity.ok && contention_zero && fidelity.ok`).

## Spec-Derived Verification Plan

Derived from `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` v2:

- `test_tafe_index_completeness.py`:
  - rule 2: non-terminal candidate WITH a terminal `<slug>-implementation` sibling => `archived_blocks`;
    WITH a non-terminal sibling => stays `lost_blocks`.
  - rule 3: candidate slug listed in the acknowledged config => `archived_blocks`; not listed (and
    non-terminal, no sibling) => `lost_blocks`.
  - precedence: terminal-token still wins (rule 1); config-absent => graceful (all such => lost).
  - read-only AST guards preserved (Path.read_text/tomllib, no `open()` write, no `bridge/INDEX.md`
    code literal, no subprocess, no mutators).
- Integration: `gt flow cutover-evidence --json` over the live INDEX => `lost_blocks == []`,
  `extra_blocks == []`, archived reflects the 74 reclassified.
- `ruff check` + `ruff format --check` on changed Python.

## Risk / Rollback

- **Risk:** acknowledging a genuinely-live slug would hide a real completeness defect. **Mitigation:** the
  68 are owner-reviewed (read-only characterization found all historical/abandoned, none live); the config
  is reversible (remove an entry -> slug re-surfaces as `lost_block`).
- **Risk:** sibling-rule false-archive if a `-implementation` sibling is terminal but the proposal thread
  is genuinely still open. **Mitigation:** a terminal impl sibling means the work completed; the
  conservative default (lost) applies whenever no terminal evidence exists.
- **Rollback:** additive — revert `tafe_index_completeness.py`, remove the config, and revert the INDEX
  `Document:` correction. No schema change (kb_schema_change is PAUTH-forbidden); no canonical-INDEX
  content mutation beyond the single serialized-writer name correction.

## Recommended Commit Type

`feat:` — adds the implementation-sibling + acknowledged-archived-config classification inputs to the
Slice B oracle plus the governed disposition config (new capability + governed data).
