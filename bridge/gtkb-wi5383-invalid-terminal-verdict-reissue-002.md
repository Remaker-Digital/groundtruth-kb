GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5383 Invalid Terminal Verdict Reissue Repair

bridge_kind: loyal_opposition_review
Document: gtkb-wi5383-invalid-terminal-verdict-reissue
Version: 002
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5383
Reviewed: bridge/gtkb-wi5383-invalid-terminal-verdict-reissue-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5383-invalid-terminal-verdict-reissue` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5383-invalid-terminal-verdict-reissue` → 0 blocking gaps

The proposal follows the established invalid-terminal-verdict repair pattern for the file-only `VERIFIED` at `bridge/gtkb-wi5383-verified-closure-evidence-008.md`. The plan is to archive the exact untracked bytes to a durable in-root diagnostic, verify byte/hash identity, remove only the untracked invalid bridge copy, and let independent Loyal Opposition reissue `gtkb-wi5383-verified-closure-evidence` version `008` through `write_verdict.py --finalize-verified` with a modern body that passes `validate_verified_body()` and includes the correct implementation-report reference and exact focused include set.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORITY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`

## Conditions

- Only `bridge/gtkb-wi5383-verified-closure-evidence-008.md` may be removed.
- Archive must be byte-for-byte identical to the original before removal at `independent-progress-assessments/WI-5383-invalid-terminal-verdict-008.finalization-diagnostic.md`.
- Replacement `VERIFIED` must be authored by independent Loyal Opposition through the canonical helper with the correct implementation-report reference.
- This proposal grants no backlog correction, source, dispatcher, TAFE, Git, or runtime mutation authority beyond the two named bridge/governance paths.
