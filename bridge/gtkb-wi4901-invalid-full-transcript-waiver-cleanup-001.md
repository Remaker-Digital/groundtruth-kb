NEW

# WI-4901 — Retire invalid full-transcript Phase 2 waivers

bridge_kind: prime_proposal
Document: gtkb-wi4901-invalid-full-transcript-waiver-cleanup
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d4b-288e-7ef0-9904-0264a4880d24
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; filesystem unrestricted; network enabled

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4901

target_paths: ["config/harness-parity/phase2-waivers.toml"]

implementation_scope: config
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal authorizes a narrow defect repair to the Phase 2 harness parity waiver registry: retire or remove the two active waiver records that use the invalid dimension `full_transcript_archive` for Ollama and OpenRouter. The current Phase 2 evaluator does not define `full_transcript_archive` as a valid waiver dimension, so these entries fail validation as `invalid_waiver` and keep the parity lane red for a configuration-schema defect rather than a real runtime capability gap.

The implementation must not alter dispatcher eligibility, harness roles, provider credentials, source code, tests, or unrelated Phase 2 waiver records. The expected change is limited to `config/harness-parity/phase2-waivers.toml`, preserving the valid `event_source` provider waivers and leaving unrelated Phase 2 gaps visible.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this protected config mutation must enter the numbered bridge chain and wait for Loyal Opposition review before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal cites the governance and parity specifications that constrain the waiver cleanup.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries the active Phase 2 project authorization, project id, work item id, and inline-JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map the waiver cleanup to executed Phase 2 parity checks.
- `GOV-STANDING-BACKLOG-001` — the repair is linked to WI-4901, whose acceptance summary requires malformed or invalid waivers to fail closed.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation must validate against the active Phase 2 PAUTH and the single approved target path before editing.
- `ADR-CROSS-HARNESS-PARITY-001` — waiver registry changes must keep cross-harness parity accounting truthful rather than masking unsupported capabilities.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — the parity evaluator must distinguish valid waivers from real missing/blocked gaps.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness capability and waiver surfaces must remain explicit and auditable across harnesses.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the owner direction, active project authorization, work item, proposal, and future verification report remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the cleanup preserves traceability from defect observation to proposal, implementation evidence, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the invalid-waiver finding is converted into a governed proposal rather than an untracked direct config edit.

## Prior Deliberations

- `bridge/gtkb-wi4901-phase2-waiver-registry-001.md` — established the typed waiver-registry schema and fail-closed handling for malformed waivers.
- `bridge/gtkb-wi4901-phase2-release-waiver-closure-003.md` and `bridge/gtkb-wi4901-phase2-release-waiver-closure-006.md` — recorded and verified the Phase 2 release-waiver closure, including valid provider `event_source` waivers.
- `bridge/gtkb-envelope-sharding-harness-projection-parity-004.md` — documented the envelope/sharding parity state and `full_transcript_archive_required = false` posture used by the provider-harness lanes.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-07-12-09-harness-parity-bridge-status.md` — Loyal Opposition report identifying `WAIVER-P2-OLLAMA-FULL-TRANSCRIPT-ARCHIVE` and `WAIVER-P2-OPENROUTER-FULL-TRANSCRIPT-ARCHIVE` as invalid Phase 2 waiver records.
- Deliberation search for `WI-4901 phase2 waivers full_transcript_archive invalid waiver` returned mostly unrelated historical waiver/verdict records, so the operative prior context for this narrow repair is the bridge chain and LO insight report above.

## Owner Decisions / Input

- Mike directed Prime Builder in this session to file the waiver cleanup proposal after the implementation authorization validator rejected direct edits to `config/harness-parity/phase2-waivers.toml` as outside the active WI-5032/WI-4842 implementation scopes.
- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` remains active for `PROJECT-HARNESS-PARITY-PHASE-2` and covers WI-4901 Phase 2 waiver-registry work.
- This proposal requests review authorization only; it is not an implementation-start packet and does not authorize direct edits until a latest `GO` exists and `scripts/implementation_authorization.py begin --bridge-id gtkb-wi4901-invalid-full-transcript-waiver-cleanup` succeeds.

## Requirement Sufficiency

Existing requirements sufficient. WI-4901's acceptance summary already requires invalid or malformed typed waivers to fail closed, and the Phase 2 evaluator currently reports two concrete invalid waiver records. No new or revised requirement is needed to remove or retire those invalid entries while preserving valid provider waivers.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | After `GO`, run `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi4901-invalid-full-transcript-waiver-cleanup` and confirm the packet covers only `config/harness-parity/phase2-waivers.toml`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, `ADR-CROSS-HARNESS-PARITY-001` | Run `groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --project-root . --format markdown`; expected result: `invalid_waiver` count is 0 and the two `full_transcript_archive` waiver findings are gone. Overall status may still fail on unrelated dispatcher receive or event-source gaps that this proposal does not target. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-STANDING-BACKLOG-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --no-header`; expected result: pass, proving the waiver schema/evaluator contract remains intact. |
| Configuration syntax floor | Parse `config/harness-parity/phase2-waivers.toml` with Python `tomllib`; expected result: parse succeeds after the cleanup. |

## Risk / Rollback

Risk is low but real: removing the invalid transcript waivers could expose a future evaluator enhancement if `full_transcript_archive` becomes a valid Phase 2 dimension later. That is acceptable because the current evaluator does not measure that dimension, provider harness transcript limitations are already represented elsewhere, and invalid waiver records should not be left active as pseudo-documentation.

Rollback is a focused revert of `config/harness-parity/phase2-waivers.toml` plus the associated implementation report if verification has not completed. The rollback would restore the two invalid waiver records and the Phase 2 evaluator would again report `invalid_waiver` for Ollama and OpenRouter.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4901-invalid-full-transcript-waiver-cleanup`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the eventual implementation repairs invalid Phase 2 waiver configuration without adding a new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
