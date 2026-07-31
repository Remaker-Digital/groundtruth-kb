ADVISORY
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019fac54-c55c-75c0-8332-d7fdaf03b20a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; transcript-resolved Loyal Opposition role
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory — WI-5665 clean-index NO-GO requires independent correction

bridge_kind: governance_advisory
Document: gtkb-lo-wi5665-premature-nogo-clean-index-correction-advisory
Version: 001
Author: Loyal Opposition (Codex A)
Date: 2026-07-29 UTC

## Source

This session filed `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-012.md` as NO-GO after observing six unrelated files in the shared real Git index. Subsequent direct inspection of the governed finalizer found that `finalize_verified_commit` builds a disposable index from `HEAD`, stages and validates the exact reviewed set there, and explicitly tolerates unrelated real-index staging (`.codex/skills/gtkb-verify/helpers/write_verdict.py:1116-1123`, `:1196-1229`).

The same session context authored v012 and cannot formally issue its replacement verdict under session-context review independence.

## Claim

The nonempty shared real index was not, by itself, a valid terminal-finalization blocker for WI-5665. The current NO-GO must be independently reassessed against v011's exact include set and current PAUTH/claim state. This is a review-correction obligation only; it does not establish that WI-5665 is otherwise ready for VERIFIED.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`

## Owner Decision Needed

None. Independent Loyal Opposition review can determine the corrected disposition from the existing governed evidence; no implementation scope or approval is inferred.

## Recommended Prime Action

Route `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-011.md` to a different Loyal Opposition session for a complete fresh review. That reviewer must re-run applicability and clause preflights, verify author-session independence, validate the current operation-time PAUTH and exact finalizer cohort, and then file the appropriate governed verdict. It must not rely on shared-index non-emptiness as a blocker unless the exact staged candidate itself is contaminated or the finalizer's disposable-index checks fail.

## Prior Deliberations And Related Evidence

- `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-011.md` — the reviewed implementation report.
- `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-012.md` — the same-session NO-GO needing independent correction.
- `bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md` — the established finalizer design rationale for preserving unrelated staging.
- `DELIB-20260729-WI5665-NARROW-FINALIZATION-PAUTH-APPROVAL` — existing owner authorization evidence; its currentness and exact reach remain for the independent reviewer to validate.

## Classification Slot

`adapt`.

This is a deterministic bridge-review correction using existing governed finalizer behavior, not a request for a new capability.

## Non-Approval Semantics

This advisory authorizes no source change, staging, commit, terminal verification, or PAUTH expansion. It only preserves the need for an independent correction of the review disposition.
