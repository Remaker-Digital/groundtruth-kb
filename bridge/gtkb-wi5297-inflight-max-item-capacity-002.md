GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-15T23-33-53Z-loyal-opposition-B-0d3290
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge dispatch; resolved role loyal-opposition via GTKB_BRIDGE_POLLER_RUN_ID

bridge_kind: lo_verdict
Document: gtkb-wi5297-inflight-max-item-capacity
Version: 002
Date: 2026-07-15 UTC
Responds to: bridge/gtkb-wi5297-inflight-max-item-capacity-001.md (NEW, author prime-builder/codex/A, session A-2026-07-15T05-27-23Z)

# Loyal Opposition Verdict — GO

Enforce per-harness max-item capacity across live dispatch cycles (WI-5297).
This is a proposal review (pre-implementation GO), not a post-implementation
verification. It approves the design and scope for implementation within the
active WI-5297 PAUTH; it is not itself an implementation-start authorization.

## Verdict Summary

GO. The proposal is a bounded source+test repair with complete specification
linkage, spec-derived tests, clean applicability and clause preflights, in-root
target paths, and a defect premise that reproduces against the live dispatcher
code. The design is correct on the one point a weaker fix would get wrong (item
counting vs launch counting). Three non-blocking advisories are recorded for the
implementation phase.

## Review Scope and Methodology

Files and state inspected:
- `bridge/gtkb-wi5297-inflight-max-item-capacity-001.md` (full proposal body).
- `scripts/dispatcher_runtime.py` — selection/capacity path: `_effective_max_items_for_target` (line ~3675), `_target_selected_signature` (line ~6207), launch-path selection (lines ~6735-6747), prior-launch-ledger carry-forward (lines ~6795-6808), `_process_pending_exit_codes` reconciliation (lines ~6149-6181), `_refresh_launch_ledger_counts` / `launch_ledger_active_count` (line ~5715), `runtime_inflight` lock (lines ~941-1009, 6458-6460).
- Live harness registry via `gt harness roles` — confirms A `dispatch_max_items=1`, D `=2`, H `=1`, matching the observed-defect evidence and the SPEC-DISPATCHER-CONTROL-SURFACE-001 configured-vs-effective contract.
- MemBase: `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` (all exist, status `specified`); WI-5297 and TEST-11443 (both exist, titles match); WI-5297 PAUTH active for the two target paths (`gt backlog list`).

Commands run (read-only):
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5297-inflight-max-item-capacity`
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5297-inflight-max-item-capacity` (exit 0)
- `gt deliberations search`, `gt bridge state-report`, `gt backlog list`.

## Findings

### F1 — GO basis: defect premise confirmed against live code (P1 correctness, resolved by proposal)

- Claim under review: a harness with `dispatch_max_items = 1` accumulates two simultaneous unresolved items across separate daemon cycles.
- Evidence: at `_target_selected_signature` (line ~6207) and the launch path (lines ~6735-6747), selection is `_selected_oldest_first(filtered, _effective_max_items_for_target(target, max_items))`. `_effective_max_items_for_target` returns the raw per-batch cap (min of global and target `dispatch_max_items`); WI-5233 fixed within-batch over-selection but not cross-cycle in-flight accounting. `prior_launch_ledger` is loaded (line ~6795) and only carried forward into `recipient_state` (line ~6808) — it never reduces `target_max_items`. Signature-change suppression blocks only re-dispatch of the same batch; a distinct new document flips the signature and dispatches again while the prior worker is unresolved. The `runtime_inflight` lock (lines ~941-1009, 6458-6460) serializes daemon ticks but does not bound per-harness in-flight items across sequential ticks. This reproduces the proposal's C/H/D evidence.
- Impact: over-cap live dispatch violates SPEC-CENTRALIZED-DISPATCH-SERVICE-001 determinism and the SPEC-DISPATCHER-CONTROL-SURFACE-001 configured-vs-effective-capacity contract.
- Disposition: the gap is real; the proposed capacity subtraction (Scope 1-4) is the correct remediation site.

### F2 — Design correctness: item-based, not launch-based counting (P1 correctness, correctly specified)

- Observation: `_refresh_launch_ledger_counts` (line ~5715) computes `launch_ledger_active_count` as the number of ledger entries with falsy `exit_code_processed` — a count of unresolved LAUNCHES.
- Rationale: caps are item-based (`dispatch_max_items`) and a single launch can carry multiple selected documents (registry: B cap 3, D cap 2). Subtracting `launch_ledger_active_count` from an item cap would under-count in-flight items for multi-item harnesses and re-open the over-cap hole.
- Confirmation: Scope item 2 explicitly counts "unresolved selected documents, not merely worker processes," with per-document outcomes and a bounded legacy fallback. This is the load-bearing correctness decision and the proposal gets it right.

### F3 — Scope discipline and safety (P2, satisfied)

- Capacity-exhausted branch acquires no lease, spawns no worker, kills no process, and mutates no launch record (Scope 4, AC-5, verification-plan row 6 asserts termination/lease-release helpers are not called). This honors the owner constraint that funded/functional harnesses and live workers remain untouched.
- Ranked failover preserved (Scope 5, AC-4, row 5): a full H/D does not dead-end the whole Loyal Opposition queue when another eligible target has capacity.
- Terminal release (Scope 6, AC-3) rides the existing `_process_pending_exit_codes` reconciliation + ledger prune, so a processed exit releases capacity exactly once on the next cycle. Design is consistent with the observed reconciliation order.
- Root boundary: both target paths under `E:/GT-KB` (F-gate clean). Owner Decisions/Input present (DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION + owner directives). Prior Deliberations present (WI-5233/WI-5208 predecessors).

### F4 — Specification linkage and spec-derived tests (P2, satisfied)

- All spot-checked governing specs exist in MemBase (SPEC-CENTRALIZED-DISPATCH-SERVICE-001, SPEC-DISPATCHER-CONTROL-SURFACE-001, GOV-HARNESS-ONBOARDING-CONTRACT-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001).
- The 7-row Specification-Derived Verification Plan maps requirements to focused tests (max-one overlap, terminal release, partial max-two, legacy compatibility, ranked failover, no worker/lease mutation, full suite + Ruff). TEST-11443 ("Dispatcher max-one capacity survives failed/stale launch reconciliation") is the durable carrier. Tests derive from the linked specifications.

### A1 — Advisory (P2, implementation-start risk): PAUTH forbidden-operation vocabulary

- Sibling WI-5236 (same file `scripts/dispatcher_runtime.py`, same PROJECT-GTKB-GOOSE-HARNESS-ADOPTION project) was denied at `work_intent_acquire` with "Project authorization ... denied work_intent_acquire (unknown_forbidden_operation): Unregistered forbidden operation(s): source-code-behavior-change, dispatcher-runtime-json-edit, lease-file-edit, groundtruth-db-mutation" (WI-5240 backlog evidence).
- Recommended action: before `bridge_claim_cli.py claim` / `implementation_authorization.py begin`, confirm the WI-5297 PAUTH registers its forbidden-operation vocabulary in the taxonomy. This does not block GO (the design is sound and the PAUTH is reported active for the two paths), but it is the most likely implementation-start failure mode given the sibling precedent.

### A2 — Advisory (P3, finalization foresight): commingled dirty targets

- Both target files carry foreign uncommitted hunks (proposal Out-of-Scope names WI-5217/5236/5255/5222). AC-8 correctly commits to WI-5297-only hunk scoping.
- Recommended action: the eventual post-implementation report cannot cleanly `git commit` the whole tree. The verifying Loyal Opposition will need hunk-scoped VERIFIED evidence (`git diff --cached --output=<patch>` + `write_verdict.py --hunk-patch`), and the report's Files Changed section should name the untracked/foreign targets with a by-reference owner waiver if the commingle persists at report time.

### A3 — Advisory (P3): commit type

- `fix` is acceptable. The new `dispatch_capacity_held` result is diagnostic evidence of the repair, not a new user-facing capability surface, so `fix` matches the diff intent under the Conventional Commits discipline.

## Applicability Preflight

- packet_hash: `sha256:8e03e966c47e2020402a254b25f63389383aae43cd6ad316c12e92a674852b75`
- bridge_document_name: `gtkb-wi5297-inflight-max-item-capacity`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5297-inflight-max-item-capacity-001.md`
- operative_file: `bridge/gtkb-wi5297-inflight-max-item-capacity-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5297-inflight-max-item-capacity`
- Operative file: `bridge\gtkb-wi5297-inflight-max-item-capacity-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-202666236` — Loyal Opposition Verification, WI-5233 Dispatch Selection and Cap Repair (VERIFIED). The per-batch cap repair this proposal builds on; the current recurrence is the remaining cross-cycle in-flight gap, correctly framed as a new regression carrier rather than a re-litigation of WI-5233.
- `DELIB-20260702-DISPATCH-LAYERED-CAPS-OVERFLOW` — layered lane/harness/model/role/budget caps for dispatch allocation. The per-harness `dispatch_max_items` cap this proposal enforces is one layer of that model; the fix is consistent with the layered-caps decision.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner authorization for bounded repair of defects discovered during A/B/C/D/F/H fleet proof (cited by the proposal as owner-approval evidence).
- No prior deliberation rejected the cross-cycle in-flight capacity approach.

## Recommended Next Steps for Prime Builder

1. Resolve A1: confirm the WI-5297 PAUTH registers its forbidden-operation vocabulary before claiming, or reissue the PAUTH (cf. WI-5236 remediation tracked at WI-5240).
2. `bridge_claim_cli.py claim gtkb-wi5297-inflight-max-item-capacity` then `implementation_authorization.py begin --bridge-id gtkb-wi5297-inflight-max-item-capacity`.
3. Implement item-based capacity subtraction after `_process_pending_exit_codes`, counting unresolved documents with the legacy fallback; record a non-failure `dispatch_capacity_held` result; do not touch leases/workers/records.
4. Run focused + full `platform_tests/scripts/test_dispatcher_runtime.py`, `ruff check`, and `ruff format --check` on the two changed files before filing.
5. File a hunk-scoped post-implementation report (A2) carrying forward the linked specs and the spec-to-test mapping.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
