NO-GO
::init gtkb lo
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fbc0b-871e-7ab0-aa0b-1024c767b883
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; owner-designated Loyal Opposition session
author_metadata_source: explicit_owner_direction

bridge_kind: lo_verdict
Document: gtkb-wi5879-wi5617-invalid-terminal-chain-repair
Version: 004
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-003.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5879
Related Work Items: WI-5617, WI-5825, WI-5858, WI-5881
target_paths: []

# Loyal Opposition Verdict — WI-5879 durable invalid-terminal repair

## Verdict

NO-GO. v003 correctly rejects v001's expiring-draft theory and preserves the invalid v013 as forward-only in-root evidence, but its proposed reservation does not fence the actual claim takeover required for recovery. A foreign Prime Builder may replace the recovery worker's non-GO victim claim immediately after the move exposes v012 `GO`, before `claim-no-action` can reclassify it. Its seven targets omit the claim registry, CLI, and regression surface that control that race. In addition, current WI-5881 is the explicit generic cross-process reservation successor and states that WI-5879 must wait for that contract plus WI-5825 recovery.

## First-Line Eligibility And Review Independence

- Owner-directed role is Loyal Opposition; `NO-GO` is authorized.
- v003 author context `019fb19b-7814-73c1-8707-204e432cbf00` differs from reviewer context `019fbc0b-871e-7ab0-aa0b-1024c767b883`. No harness label, dispatcher choice, durable role mapping, or prompt label was used as an eligibility restriction.
- Canonical reviewed artifact: strict `REVISED` v003, SHA-256 `1F8A9222B1E42799D46C8EBD66186C80FC09E1B57AB6E2FE578E384F63C5C96E`; the review claim was null before this exact lease.

## Confirmed Baseline

- The complete WI-5879 v001–v003 chain is strict-valid: `NEW` v001, independent `NO-GO` v002, and PB `REVISED` v003 responding to v002. v003 is the current review artifact.
- The victim `gtkb-dispatcher-next-foundation-spike` still has invalid untracked v013 SHA-256 `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`; v011/v012 retain `2A3AAE14FA671D7D3FBFF8E6F8F01EF017723F6457091B13563C30D93C84EEDD` and `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`. Strict resolution fails `WRONG_STATUS_AUTHOR_ROLE` because v013 is Prime-authored `VERIFIED`. Victim and WI-5879 claims were null before this review.
- The cleanup target is absent. The victim v012 GO has a consumed capability/receipt; no v013 capability exists. Registry inspection is coherent with identity current.
- Direct active project membership and list-free PAUTH v2 apply to the declared classes. This allows a properly reviewed future repair; it does not cure the recovery race or replace GO/claim/start/verification gates.
- WI-5825 remains latest `GO` v006, not independently VERIFIED. Its four shared source/test paths remain foreign-dirty or otherwise must be re-read after its own landing; v003 correctly must not start on them now.

## Findings

### F1 — P0: immediate claim takeover defeats the promised fresh-session exclusive recovery

**Evidence.** `scripts/bridge_work_intent_registry.py::_can_preempt_lingering_draft` (lines 923–928) returns true whenever an incoming `go_implementation` claim meets any existing non-GO claim. `_claim_operation` applies that rule for another session at lines 960–965. The repository's current regression `test_claim_go_implementation_preempts_lingering_draft_claim` passed (1 passed): a draft holder is replaced after a GO file appears, with no TTL expiry.

The proposed sequence must acquire the victim claim before moving invalid v013. While v013 is physical head, `claim-no-action` is unavailable because it requires latest `GO` or `NO-GO`; the victim claim is consequently non-GO. After the move, v012 is head `GO`. Any eligible foreign Prime session calling ordinary `claim` now receives `go_implementation` and immediately preempts that non-GO holder. v003 then requires the recovery-aware writer to validate current exact claims and requires the original/fresh recovery session to obtain an exact victim claim before its `NO-ACTION` replacement. The reservation described in v003 fences ordinary capability mint, but neither changes nor binds `work_intent_claims`; it cannot reacquire the victim claim from the foreign GO holder or guarantee the stated fresh-session route.

**Impact.** The evidence move can leave an immutable reservation but no exclusive, recoverable claimant capable of meeting the proposal's own publication precondition. This is an immediate interleaving, not a timer/TTL-expiry issue. A reservation that only fences mint is insufficient where the canonical writer also requires the exact claim.

**Required correction.** Do not implement an incident-specific partial reservation. The generic contract must atomically or fail-closed bind reservation and claim eligibility before the move, deny ordinary GO takeover for a reserved exact replacement slot, define the authorized fresh-session resume/takeover operation, and prove both denial and resume using separate worker sessions. It necessarily reaches `scripts/bridge_work_intent_registry.py`, `scripts/bridge_claim_cli.py` if the CLI exposes the operation, and focused claim-registry/CLI tests; omitting those paths cannot truthfully satisfy v003's exclusive-recovery invariant.

### F2 — P0: v003 duplicates the canonical generic successor and violates its ordering

**Evidence.** WI-5791 is marked resolved by the bridge VERIFIED backlog reconciler, but `TEST-11758` has no test file/function or result, and the work item has no target-bearing implementation proposal/report/independent implementation verification. It is historical superseded evidence, not a landed contract.

Current open P0 WI-5881 was created as its forward-only successor specifically because that terminal reconciliation was false. Its canonical description owns a generic exact-generation recovery reservation across the work-intent registry and CLI, registry control plane, writer, durable store, and integration tests; it explicitly fences ordinary claim takeover and publication mint, survives process/session/claim expiry, and says WI-5879 is an incident-specific consumer that must wait for the generic contract and WI-5825 receipt recovery. v003 proposes the same generic surfaces but omits the claim layer and does not cite or sequence behind WI-5881.

**Impact.** Parallel implementation would create two competing contracts for the same generation/claim semantics and risks an incident-only exception that leaves other recovery paths vulnerable.

**Required correction.** WI-5879 must not implement the generic reservation primitive. Reconcile its scope as an incident consumer behind independently implemented and VERIFIED WI-5881 and WI-5825, with re-read clean shared targets and no overlapping claim/registry/writer ownership. Preserve WI-5791/TEST-11758 as superseded evidence; do not treat their reconciler closure as implementation approval.

### F3 — P1: the stated TEST-11807 route does not test the decisive race

**Evidence.** All four v003 named test nodes are absent today (`pytest --collect-only` found zero; all four node paths reported no match), as expected pre-implementation. More importantly, their named registry/writer locations do not exercise the existing CLI behavior that passed the takeover regression. No planned test holds a pre-move non-GO victim claim, moves v013 to expose v012 GO, attempts a foreign ordinary claim before `claim-no-action`, and then proves that only the immutable-bound recovery session may resume.

**Required correction.** The generic WI-5881 test plan must include this exact preemption interleaving plus foreign-worker resume/denial. A later WI-5879 consumer test may verify its specific v013 archive/predecessor tuple, but must use the generic claim/reservation interface rather than reimplement it.

## Applicability Preflight

- packet_hash: `sha256:4fc0db22ef967156146dc4727160376409265e65032cb93160b2d646b111c797`
- candidate_evidence_hash: `sha256:50c2f9096c7412d81a40e02221f6395a2c452535bceb9f0de04c93a58235a8ee`
- bridge_document_name: `gtkb-wi5879-wi5617-invalid-terminal-chain-repair`
- content_file: `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-003.md`
- operative_file: `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

Four must-apply and one may-apply clause were re-evaluated with zero mandatory evidence gaps and zero blocking gaps. Mechanical passage is a floor; it does not prove that the declared seven paths cover the recovery protocol's required claim fence.

## Deliberation And Authority Evidence

- `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` supports exact-record CAS rather than a global worker leader; it does not permit an unfenced claim handoff.
- `DELIB-202667724` / `DELIB-202667732` support the active Bridge Protocol Reliability repair authority.
- `DELIB-202667722` and WI-5858 retain timer/TTL centralization; this finding is a non-TTL immediate-preemption defect and adds no timer change.
- WI-5881 is the current, non-approval backlog carrier for the generic repair; it does not itself authorize implementation.

## Non-Impairment Disposition

This append-only verdict grants no implementation authority. It preserves all WI-5879 and victim chain bytes, the invalid v013 incident evidence, WI-5617's open state, WI-5791/TEST-11758 history, existing claims other than this review lease, source/tests/DB/registry/dispatcher/TAFE/Git state, and the foreign index lock. It does not treat NO-ACTION as closure and does not move, archive, delete, or rewrite any file.

## Commands

- `gt bridge show gtkb-wi5879-wi5617-invalid-terminal-chain-repair --json --compact`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5879-wi5617-invalid-terminal-chain-repair`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5879-wi5617-invalid-terminal-chain-repair`
- strict lifecycle, victim capability/receipt, target-hash, claim, PAUTH/project/WI, registry, and deliberation reads
- `python -m pytest platform_tests/scripts/test_bridge_claim_cli.py::test_claim_go_implementation_preempts_lingering_draft_claim -q --tb=short` — 1 passed
- four v003 proposed TEST-11807 node collection — 0 collected / no matching nodes

## Skills Applied

- gtkb-bridge
- gtkb-proposal-review
