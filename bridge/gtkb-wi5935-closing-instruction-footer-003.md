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
Version: 003
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-5935
Responds to: bridge/gtkb-wi5935-closing-instruction-footer-002.md (LO GO)
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/wrap.py", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "scripts/gtkb_bridge_writer.py", "groundtruth.db"]

# WI-5935 Slice E — Post-Implementation Report (closing-instruction footer)

## Summary

Implemented the WI-5935 Slice E closing-instruction footer per the approved proposal at `-001` (LO GO `-002`), uniformly across interactive and bridge artifact surfaces.

- `render_wrap_summary` (in `session/wrap.py`) now emits `When you are finished working, close your session envelope by invoking ::wrap.`
- Startup-disclosure templates carry the closing instruction: `PRIME-BUILDER-STARTUP-OVERLAY.md`, `LOYAL-OPPOSITION-STARTUP-OVERLAY.md`, `SESSION-STARTUP-INDEX.md`.
- `scripts/gtkb_bridge_writer.py` appends the closing-instruction footer to every filed bridge artifact.

## Requirement Sufficiency

Existing requirements sufficient (approved proposal at -001, LO GO -002).

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/session/wrap.py`
- `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`
- `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `scripts/gtkb_bridge_writer.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` (Slice A) — closing-instruction clause.
- `SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001` v2 (Slice B) — closing-instruction contract.
- `GOV-SESSION-SELF-INITIALIZATION-001` (startup disclosure surface); `ADR-CROSS-HARNESS-PARITY-001` (uniform text).

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
## Specification-Derived Verification (spec-to-test mapping)

| Spec clause | Test |
| --- | --- |
| DCL closing-instruction (wrap summary surface) | `test_render_wrap_summary_includes_closing_instruction` |
| DCL closing-instruction (startup disclosure templates) | `test_startup_disclosure_surfaces_carry_closing_instruction` |
| DCL closing-instruction (bridge artifacts) | `test_write_bridge_file_appends_closing_instruction_footer` |

## Test Commands and Observed Results

- `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py::test_render_wrap_summary_includes_closing_instruction` → **1 passed**
- `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py::test_startup_disclosure_surfaces_carry_closing_instruction` → **1 passed**
- `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py::test_write_bridge_file_appends_closing_instruction_footer` → **1 passed**
- `python -m ruff check <changed files>` → **All checks passed**
- `python -m ruff format --check <changed files>` → **already formatted**

## Recommended Commit Type

feat: (new closing-instruction artifact surface)

## Owner Decisions / Input

- 2026-08-04: Owner directed implementation of WI-5935 across all six slices (A-F), each minting an implementation-start packet from its GO (transcript directive).
