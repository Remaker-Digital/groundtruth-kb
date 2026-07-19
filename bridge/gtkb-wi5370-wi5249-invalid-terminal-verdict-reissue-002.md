GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5370 WI-5249 Invalid Terminal Verdict Reissue Repair

bridge_kind: loyal_opposition_review
Document: gtkb-wi5370-wi5249-invalid-terminal-verdict-reissue
Version: 002
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Reviewed: bridge/gtkb-wi5370-wi5249-invalid-terminal-verdict-reissue-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi5249-invalid-terminal-verdict-reissue` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi5249-invalid-terminal-verdict-reissue` → 0 blocking gaps

The proposal follows the established invalid-terminal-verdict repair pattern for the file-only `VERIFIED` at `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md`. The plan is to archive the exact untracked bytes, verify byte/hash identity, remove only the untracked invalid bridge copy, and let independent Loyal Opposition reissue `gtkb-wi5249-prime-no-action-claim-filer` version `008` through `write_verdict.py --finalize-verified` with a modern body that passes `validate_verified_body()` and receives helper-generated commit-finalization evidence.

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

## Conditions

- Only `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md` may be removed.
- Archive must be byte-for-byte identical to the original before removal at `independent-progress-assessments/WI-5370-wi5249-verdict-008.invalid-finalizer.md`.
- Replacement `VERIFIED` must be authored by independent Loyal Opposition through the canonical helper.
- The active staged `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` must be preserved unless a separate GO authorizes index containment.
