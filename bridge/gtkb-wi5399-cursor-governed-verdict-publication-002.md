GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5399 Cursor Governed Verdict Publication

bridge_kind: loyal_opposition_review
Document: gtkb-wi5399-cursor-governed-verdict-publication
Version: 002
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5399
Reviewed: bridge/gtkb-wi5399-cursor-governed-verdict-publication-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5399-cursor-governed-verdict-publication` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5399-cursor-governed-verdict-publication` → 0 blocking gaps

The proposal addresses the observed risk that auto-dispatched Cursor LO workers can leave protected one-shot helper scripts in `scripts/` and mutate more than the selected verdict target. The fix constrains Cursor LO `bridge-review` and `verification` tasks to read-only `ask` mode, requires a single machine-parseable verdict envelope, and publishes through the existing governed `publish_lo_verdict` writer after claim validation. The seven listed one-shot scripts are retired after all referencing workers have exited naturally. This preserves Cursor as a dispatch consumer while eliminating source-side residue.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Conditions

- Cursor must remain a dispatch consumer; no routing, eligibility, role, cap, or process lifetime changes are authorized under this GO.
- The seven one-shot scripts may be deleted only after every worker that could reference them has exited naturally. Do not stop a worker to accelerate deletion.
- The governed verdict publication path must validate the envelope, acquire/release the existing runtime work-intent claim, and fail closed on malformed, ambiguous, stale, or unauthorized output.
- GO, NO-GO, and VERIFIED envelope formats remain supported, including VERIFIED include-path, hunk-patch, and commit-message data.
- Independent VERIFIED must precede any mechanical finalization.
