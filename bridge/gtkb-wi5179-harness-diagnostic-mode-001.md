NEW

# Harness diagnostic mode - privacy-bounded cross-harness evidence for WI-5179

bridge_kind: prime_proposal
Document: gtkb-wi5179-harness-diagnostic-mode
Version: 001
Author: Prime Builder / Codex
Date: 2026-07-11 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated session document
author_metadata_source: validated harness-state/codex/session-envelopes session document plus Codex runtime context

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5179-HARNESS-DIAGNOSTIC-20260711
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5179

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "scripts/cloud_harness_base.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py", "platform_tests/groundtruth_kb/test_harness_diagnostic.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: source | test_addition | cli_extension | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the owner-approved, read-only `gt harness diagnostic --harness-id <ID> --json` v1 surface for every active registered GT-KB harness. The diagnostic projection will collect only bounded local, cached, or explicitly unavailable evidence; it will not call a provider, alter a dispatcher decision, mutate a claim, or create a competing report command.

The projection will use the active registry as the parity inventory, read the role solely from the harness's validated session document, and treat dispatch as confirmation of dispatch intent rather than role authority. It will expose at most 50 recent privacy-safe records, including the allowed WI-5173 telemetry fields when present, while preserving `null` and coverage/unavailable reasons when evidence is missing or partial.

## Specification Links

- `SPEC-HARNESS-DIAGNOSTIC-MODE-001` - defines the v1 contract, parity inventory, WI-5173 integration, null semantics, bounded event output, and privacy exclusions.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - governs the safe telemetry fields that may be projected without re-serializing unsafe runtime data.
- `ADR-CROSS-HARNESS-PARITY-001` - requires registry-driven behavioral parity or a declared owner-approved typed waiver.
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` - require document-derived worker role provenance; dispatcher configuration and selection cannot supply a role.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - require PAUTH, a live independent GO, a matching claim, and an implementation-start packet before protected edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived automated verification before an independent VERIFIED verdict.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the approved requirement, authorization, proposal, test, report, and verification lineage without treating capture as implementation approval.

## Prior Deliberations

- `DELIB-20260710-WI5175-DIAGNOSTIC-MODE-SPEC-APPROVAL` - owner approval of the diagnostic-mode child specification.
- `DELIB-20260711-WI5179-PAUTH-APPROVAL` - owner approval of the bounded WI-5179 implementation authorization.
- `DELIB-20260710-CANONICAL-BACKLOG-WRITER-DOCUMENT-ROLE-AUTHORITY` - confirms the governing rule applied here: role is derived exclusively from the document artifact; dispatch confirms intent only.

## Owner Decisions / Input

- `DELIB-20260710-WI5175-DIAGNOSTIC-MODE-SPEC-APPROVAL` approved `SPEC-HARNESS-DIAGNOSTIC-MODE-001`.
- `DELIB-20260711-WI5179-PAUTH-APPROVAL` authorized `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5179-HARNESS-DIAGNOSTIC-20260711`.
- The authorization permits filing this proposal only. Protected implementation remains blocked until an independent Loyal Opposition GO, a matching work-intent claim, and an implementation-start packet are live.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-HARNESS-DIAGNOSTIC-MODE-001` specifies the diagnostic interface, semantics, privacy boundary, telemetry projection, and acceptance matrix. The active PAUTH constrains implementation to the listed targets and explicitly excludes provider requests, credentials/secrets/environment values, prompt/message/tool/provider-body capture, dispatcher configuration or selection changes, claims or production-state mutation, metrics enrichment, automatic tuning, deployments, and a competing report command.

## Spec-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Registry parity and typed waiver | Enumerate active registry harnesses; assert each has the diagnostic contract or an owner-approved typed waiver, and test cloud-template inheritance. |
| Document-only role provenance | Supply a session document role that conflicts with dispatcher metadata; assert document role and source survive while invalid/missing documents report unavailable rather than infer a role. |
| Privacy and read-only operation | Assert local invocation makes no provider request and serialized output contains none of prompts/messages/generated text/tool arguments/results/credentials/secrets/environment values/raw provider bodies. |
| Bounded evidence and null semantics | Assert no more than 50 recent records, unknown values are `null`, and every unavailable field has freshness/coverage/unavailable-reason evidence. |
| WI-5173 projection | Assert successful, partial, absent, and provider-unavailable telemetry produce only safe correlation, timing, turn, tool, outcome, usage, and cost projections without failing the diagnostic. |
| CLI compatibility | Exercise `gt harness diagnostic --harness-id <ID> --json`; keep the existing `gt harness telemetry` and dispatcher-report contracts unchanged. |

Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_harness_cli.py platform_tests/groundtruth_kb/test_harness_diagnostic.py platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short`, then broaden to the affected harness and CLI suites. Run `groundtruth-kb/.venv/Scripts/python.exe -m ruff check` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check` over the changed Python targets.

## Risk / Rollback

- Risk: a diagnostic convenience path could expose unsafe runtime payloads. Mitigation: construct output from a narrow allowlist of primitives and assert prohibited-content exclusions.
- Risk: role could drift to dispatcher metadata. Mitigation: resolve role provenance only through the validated session document and test conflicting metadata.
- Risk: a local command could trigger provider traffic or operational mutation. Mitigation: isolate local/cached collection and assert no provider call, claim mutation, configuration write, or dispatcher selection change.
- Risk: telemetry absence could become a false zero. Mitigation: retain `null`, coverage, freshness, and unavailable reasons through every projection path.
- Rollback: revert the single implementation commit; no dispatch, role, configuration, claim, or production-state transition is introduced by this work.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5179-harness-diagnostic-mode`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat` - adds the approved read-only diagnostic CLI surface and its bounded projection module.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
