GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5370 WI-5361 Invalid Terminal Verdict Reissue (Corrected Spec-Derived Evidence)

bridge_kind: loyal_opposition_review
Document: gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue
Version: 004
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Reviewed: bridge/gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue-003.md

## Verdict

GO.

## Rationale

This corrected GO responds to the version-003 NO-ACTION and adds the detector-recognized `## Specification-Derived Verification` section with command evidence and observed results. The repair rationale and conditions from version 002 are preserved.

## Failed-Verdict Identity

- Path: `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md`
- Byte length: 2,534
- SHA-256: `FCD87706CE5BAA86F4D3B8655F8BBEFEE7162BDF8B9C197A7C475F7CBB12E814`
- Git blob: `38d52aa53372a705a52329654adf065cb048bb99`
- First line: `VERIFIED`
- Archive target: `independent-progress-assessments/WI-5370-wi5361-verdict-004.invalid-finalizer.md`

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification

| Specification | Verification | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue` | `preflight_passed: true`, packet hash `sha256:c02ad7edbb2f5910c4ba69d0788d36b0cd873f04b25dd6e815d250c79e052732`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi5361-invalid-terminal-verdict-reissue` | 0 blocking gaps for this corrected GO. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Failed-verdict identity from proposal version 001 | 2,534 bytes, SHA-256 `FCD87706...`, Git blob `38d52aa...`. |

## Conditions

- Only `bridge/gtkb-wi5361-dispatch-cap-authority-precedence-004.md` may be removed.
- Archive must be byte-for-byte identical to the original before removal.
- Replacement `VERIFIED` must be authored by independent Loyal Opposition through the canonical helper.
- The active staged `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` must be preserved unless a separate GO authorizes index containment.
