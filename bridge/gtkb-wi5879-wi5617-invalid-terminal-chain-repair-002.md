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

# Loyal Opposition Review Verdict — NO-GO — WI-5879

bridge_kind: lo_verdict
Document: gtkb-wi5879-wi5617-invalid-terminal-chain-repair
Version: 002
Responds to: bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-001.md
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5879
Related Work Items: WI-5617
Recommended commit type: N/A (review verdict only)

target_paths: ["bridge/gtkb-dispatcher-next-foundation-spike-013.md", "bridge/cleanup-evidence/wi5617-invalid-pb-verified-013-20260801/gtkb-dispatcher-next-foundation-spike-013.md.invalid-pb-verified", "groundtruth.db"]

## Verdict

NO-GO. The exact preservation move and subsequent receipt-backed replacement are lawful in principle, but the proposed recovery protocol is not durable across its critical crash window. It must be revised before any target mutation.

## First-Line Role Eligibility and Review Independence

- Status writer: owner-designated Loyal Opposition; `NO-GO` is role-authorized.
- Reviewed proposal author session: `019f9b59-52a0-75b2-9973-bd5601f98e9f`.
- Reviewer session: `019fbc0b-871e-7ab0-aa0b-1024c767b883`.
- Independence: PASS; session contexts differ. No harness, dispatcher, or role-map condition was used as a review-eligibility criterion.

## Applicability Preflight

- packet_hash: `sha256:66e1c6b79ed607214a0e513962238edeb2ca6bc301ccda428646c09082100139`
- bridge_document_name: `gtkb-wi5879-wi5617-invalid-terminal-chain-repair`
- content_file: `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-001.md`
- operative_file: `bridge/gtkb-wi5879-wi5617-invalid-terminal-chain-repair-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:c672ca379fa5e9cfd2dfacebfa34aee5c12ff10858233e116beaa76b3cf443ce`

## Clause Applicability

- Mandatory clause gate: PASS.
- Clauses evaluated: 5; must-apply: 4; blocking gaps: 0.

## Evidence Confirmed

- v001 is canonically `NEW`, SHA-256 `0216FCEB05F25ED62C36AAC6285638F68342E82F2C87F621E58E7630C376D951`, and had no filing claim before review.
- Full victim v001–v013 chain was read. Strict resolution fails `WRONG_STATUS_AUTHOR_ROLE`: PB-authored v013 `VERIFIED`, SHA-256 `ECDF08766CA2FE930A4869E71F946D59BA535D3CB5CC87D5A5F2DC249E42870D`. v011/v012 retain `2A3AAE14FA671D7D3FBFF8E6F8F01EF017723F6457091B13563C30D93C84EEDD` and `70848E8C8F97781AA9906681589E6FA20322DDD753447EF9838AB86DB042ED12`.
- Active list-free PAUTH v2 applies and operation-time evaluation allows exactly the two bridge paths plus `groundtruth.db`. The cleanup destination is absent; v013 has no receipt, v012 has a consumed `GO` receipt; victim claim is null; no bridge-publication capability is minted; registry journal is terminal.
- The archive destination is an in-root opaque bridge operation path. `bridge-versioned-files` is the aggregate identity, and canonical `gt registry observe --artifact bridge-versioned-files` can truthfully record post-move content. `groundtruth.db` is therefore the correct service-owned metadata target; raw SQLite is not justified.
- An ordinary victim draft claim can precede the move; after the physical head reverts to v012 `GO`, its same holder can reclassify using `claim-no-action`; `GO → NO-ACTION` is legal. This does not protect the crash window.
- Focused regression passed: `platform_tests/scripts/test_bridge_claim_cli.py`, `platform_tests/scripts/test_bridge_lifecycle_resolver.py`, and `platform_tests/groundtruth_kb/cli/test_registry_observe_cli.py`: 76 passed. The foreign `.git/index.lock` exists and was untouched.

## Blocking Finding

### P0 — The post-move recovery is protected only by an expiring draft lease

The victim claim is an ordinary `draft` claim: default 600 seconds, no durable move-recovery reservation, and no draft recovery/extension path. v001 moves v013 before claim reclassification and before a replacement publication capability can be minted.

After a crash in that interval, bytes remain archived but the live physical head is v012 `GO`. Once the draft lease expires, another worker can claim the victim thread and proceed from that `GO`; it need not know the archived repair bytes. Registry observation restores aggregate currentness but does not bind or reserve recovery. The later short-lived replacement capability is too late to close this gap. A competing valid v013 can therefore occupy the intended path before resumption, contradicting the proposal's single-replacement, collision, and crash-resume acceptance claims.

## Required Revision

Provide an executable, receipt-backed recovery protocol that survives loss or expiry of the initial worker session. Before or atomically with the move, durably bind the exact archived hash, archive path, intended replacement path, and victim ownership; prevent recovery or reclassification by any fresh worker until that binding is validated and consumed; and add a focused crash-after-move/after-lease-expiry collision test. If current mechanisms cannot supply this invariant, expand scope to the minimal claim/writer/control-plane change and tests. Do not replace it with a global-leader rule or raw database edits.

Also identify an executable/recordable route for TEST-11807, which currently has no bound test file or result, so a later terminal verification can substantiate its required pass.

## Non-Blocking Clarification

Registry writes and minted publication capabilities are internally serialized contention points, not a global worker-leader authorization; exact-thread claims plus canonical re-read/retry remain the correct coordination basis. The hard-coded 10-second claim-write retry is already tracked by WI-5858, so no duplicate timer WI was filed.

## Disposition

No target was modified by this review. Preserve v001 and the victim chain. A revised proposal must resolve the P0 recovery invariant before any evidence move, registry observation, claim reclassification, or replacement v013 publication. No owner decision is required.
