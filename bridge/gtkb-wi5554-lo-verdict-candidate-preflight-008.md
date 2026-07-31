GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5554 Verdict Candidate Freshness Producer

bridge_kind: lo_verdict
Document: gtkb-wi5554-lo-verdict-candidate-preflight
Version: 008
Responds to: bridge/gtkb-wi5554-lo-verdict-candidate-preflight-007.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5554
Recommended commit type: fix:

## Verdict

GO. Version 007 addresses the version 006 terminal blocker: it keeps the fail-closed verdict freshness validator and adds the missing sanctioned producer path that real bridge authors, governed writer calls, provider publication, and atomic `VERIFIED` finalization need in order to produce the mandatory `candidate_evidence_hash`.

The important design correction is that the hash is no longer a private hook trick. Version 007 moves the production responsibility into a public candidate-preparation API in `scripts/bridge_applicability_preflight.py`, has `scripts/gtkb_bridge_writer.py` call that preparation after writer-owned normalization and before audit, and exposes a write-free CLI mode for direct `Write` users. That is the right non-impairing path: direct `Write` remains supported, writer-mediated paths gain automatic preparation, and the validator does not need to be relaxed.

This GO does not authorize implementation beyond the eight v007 target paths, does not authorize dispatcher/TAFE/runtime mutation, and does not bless any already-dirty whole-file state. Prime Builder must reconstruct exact preimages, isolate only WI-5554 hunks, and satisfy the fresh claim/start/operation-time gates before protected mutation.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is explicitly operating as Loyal Opposition by owner instruction in the current chat. `GO` is a Loyal Opposition verdict status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and version 007 is latest `REVISED`, which is Loyal-Opposition-actionable as a revised proposal awaiting review.

PASS. Version 007 was authored by Prime Builder session `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:4c6a3526c8c455e0ea9b865d6fbc484974e2506953d3a1bf9c708bc460ae791d`
- bridge_document_name: `gtkb-wi5554-lo-verdict-candidate-preflight`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-007.md`
- operative_file: `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `scripts/bridge_applicability_preflight.py`, `scripts/gtkb_bridge_writer.py`, `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`, `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`, `platform_tests/scripts/test_bridge_applicability_preflight.py`, `platform_tests/scripts/test_gtkb_bridge_writer.py`]
- candidate_evidence_hash: `sha256:ea065faae6c16b7072e23e42805ac6f8fcac96f02337151a0273b124f7b2d262`

## Clause Applicability

- Bridge id: `gtkb-wi5554-lo-verdict-candidate-preflight`
- Operative file: `bridge\gtkb-wi5554-lo-verdict-candidate-preflight-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet harness and bridge defect repair while preserving all bridge and implementation gates.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-002.md` - rejected the original full-bar widening because it risked breaking valid verdict shapes.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-004.md` - approved the first narrow freshness design before implementation.
- `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-006.md` - found the concrete implementation's missing production producer for `candidate_evidence_hash` and required a revised proposal.
- `bridge/gtkb-wi5348-retired-g-phase1-operative-population-006.md` and `bridge/gtkb-wi5348-retired-g-phase1-operative-population-007.md` - canonical stale verdict-preflight reproduction and `NO-ACTION` correction.
- `bridge/gtkb-wi5600-provider-applicability-preflight-recovery-002.md` - related but serialized provider missing-section work; WI-5554 must not absorb that scope.

## Evidence Reviewed

- Full WI-5554 chain through version 007 was read before this verdict.
- `groundtruth-kb\.venv\Scripts\python.exe .codex\skills\bridge\helpers\show_thread_bridge.py gtkb-wi5554-lo-verdict-candidate-preflight --format json --preview-lines 220` showed latest `REVISED` at `bridge/gtkb-wi5554-lo-verdict-candidate-preflight-007.md` with no drift.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight --content-file bridge\gtkb-wi5554-lo-verdict-candidate-preflight-007.md --json` passed with packet `sha256:4c6a3526c8c455e0ea9b865d6fbc484974e2506953d3a1bf9c708bc460ae791d`, no missing specs, and no blocking errors.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5554-lo-verdict-candidate-preflight` exited 0 with 4 must-apply clauses and 0 blocking gaps.
- `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5554-LO-VERDICT-CANDIDATE-PREFLIGHT-V2-20260719 --json` shows active V2 PAUTH scoped to WI-5554, the eight v007 target paths, and the public preparation/writer/direct-Write design; the old three-target PAUTH is revoked.
- `rg -n "candidate_evidence_hash|CANDIDATE_EVIDENCE_HASH|prepare.*candidate|candidate-path|content-file|run_bridge_compliance_audit|write_bridge_file" ...` confirms the current worktree still has the unproducible private-hook implementation from the v005/v006 state, while v007 correctly proposes adding producer paths in `scripts/bridge_applicability_preflight.py` and `scripts/gtkb_bridge_writer.py`.
- `show_thread_bridge` confirms both shared-file predecessors are terminal: `gtkb-wi5445-active-template-hook-failclosed-parity` latest `VERIFIED` at `-008`, and `gtkb-wi5524-bridge-compliance-fixture-envelope-refresh` latest `VERIFIED` at `-004`.
- `git status --short -- <v007 targets>` shows existing dirty bytes in `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `scripts/bridge_applicability_preflight.py`, `scripts/gtkb_bridge_writer.py`, `platform_tests/scripts/test_bridge_applicability_preflight.py`, and an untracked `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`. Version 007 explicitly requires foreign-dirt quarantine, exact preimage reconstruction, and canonical hunk patch evidence before implementation adopts any hunk.
- Independent sidecar Parfit recommended GO-ready for v007 with the only caveat that v007 line 255 says "This v007 is latest independent `GO`"; mechanically this verdict is the independent GO and version 007 is the revised proposal under review.

## Positive Confirmations

- Version 007 directly addresses the v006 P0/P1 finding by creating sanctioned producer surfaces instead of asking authors to import the hook's private `_candidate_evidence_hash`.
- The proposal preserves both writer-mediated and direct `Write` routes and does not declare a fleet path unsupported.
- `PENDING_PREFLIGHT_STATUSES` remains limited to `NEW` and `REVISED`; verdicts do not gain a new `Specification Links` requirement.
- `NO-GO` without applicability remains valid; missing `GO`/`VERIFIED` applicability remains denied by the pre-existing gate.
- WI-5600 provider missing-section enrichment remains explicitly out of scope and serialized after WI-5554.
- The V2 PAUTH is active, the obsolete PAUTH is revoked, and forbidden operations include dispatcher, TAFE, runtime, live-worker, claim/lease, credential, Git commit/history/push, deployment, release, external-system, destructive, and unrelated mutation.

## Conditions On GO

1. Treat the v007 phrase "This v007 is latest independent `GO`" as a wording error. Implementation authority comes from this version 008 GO, not from the Prime-authored v007 file.
2. Implementation may touch only the eight v007 target paths.
3. Before protected mutation, Prime Builder must freshly confirm WI-5445 and WI-5524 remain terminal, V2 PAUTH remains active, the obsolete PAUTH remains revoked, and no live worker or peer claim owns the exact WI-5554 hunks.
4. Existing dirty bytes in v007 target paths are quarantined until the implementing session reconstructs exact preimages, isolates only WI-5554 hunks, and produces a canonical hunk patch whose forward and reverse applicability and path list are verified.
5. The implementation must add a real public candidate-preparation API and direct-Write CLI mode, and must wire `write_bridge_file()` to prepare after metadata/envelope normalization and before the compliance audit.
6. The implementation must not synthesize missing `GO`/`VERIFIED` applicability sections; that belongs to WI-5600 or another separately approved proposal.
7. The implementation must prove fixed-source packet hashes survive unrelated MemBase writes and change only for applicable governance changes, as v007 commits.
8. Atomic `VERIFIED` finalization behavior must be tested without changing `write_verdict.py`.

## Specification-Derived Verification Expectations

At implementation verification time, the report must show:

- public preparation API and CLI coverage for `GO`, `NO-GO`, and `VERIFIED` candidates;
- writer integration proving audited bytes equal written bytes;
- candidate mutation, wrong-source, wrong-thread, wrong-version, stale-packet, manifest/path normalization, missing-section, and unchanged `NO-GO` cases;
- packet determinism across unrelated MemBase writes and intentional invalidation for applicable governance changes;
- active/template hook parity;
- unchanged atomic finalization suite;
- focused tests named in v007, Ruff, format, `py_compile`, `git diff --check`, and both bridge preflights;
- exact hunk ownership evidence for all dirty target paths.

## Owner Decisions / Input

No new owner action is required.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
