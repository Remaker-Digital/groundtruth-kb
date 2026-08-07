NEW
::init gtkb pb
::open build
author_identity: Goose Prime Builder
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: manual interactive desktop session

bridge_kind: prime_proposal
Document: gtkb-wi5935-closing-instruction-footer
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Work Item: WI-5935
Project: PROJECT-GTKB-SESSION-ENVELOPE

# WI-5935 Slice E - Closing-instruction footer, uniform across interactive + bridge artifacts

## Summary

Delivers the WI-5935 closing-instruction requirement: every interactive-session and bridge artifact carries a closing instruction (`When you are finished working, close your session envelope by invoking ::wrap.`). Adds the footer to the wrap-summary surface and the startup-disclosure / artifact templates, uniformly across harnesses.

## Requirement Sufficiency

Existing requirements sufficient (once Slice A DCL and Slice B spec v2 closing-instruction clause are GO).

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/wrap.py", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "scripts/gtkb_bridge_writer.py", "groundtruth.db"]

## Implementation Plan

1. Add the closing-instruction line to the wrap summary output (`render_wrap_summary`).
2. Add the closing instruction to the startup-disclosure templates (PB + LO overlays + startup index).
3. Add the closing instruction to the bridge-writer envelope head so filed bridge artifacts carry it.
4. Uniform wording across all surfaces (no per-harness text).

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A) - closing-instruction clause; `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B) - closing-instruction contract.
- `GOV-SESSION-SELF-INITIALIZATION-001` (startup disclosure surface); `ADR-CROSS-HARNESS-PARITY-001` (uniform across harnesses).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- Grep-based assertion per linked spec: each target surface contains the closing-instruction token (`::wrap`). `python -m pytest` template/disclosure tests; `ruff check` on wrap.py / gtkb_bridge_writer.py.

## Prior Deliberations

- `DELIB-20265897` - mechanical wrap/harvest model.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 34536 and this is thread id 20700.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04: Owner selected Option 1 - file all slices now, staged by dependency. Depends on Slice A GO.

## Cross-Harness Disposition

Uniform footer text across all harnesses; no per-harness variant and no waiver requested (per `ADR-CROSS-HARNESS-PARITY-001` Q8).

## Recommended Commit Type

feat: (new closing-instruction artifact surface).
