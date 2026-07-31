GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5241 Invalid Terminal VERIFIED Verdict Reissue Repair

bridge_kind: loyal_opposition_review
Document: gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Reviewed: bridge/gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-wi5241-invalid-terminal-verdict-reissue` → 0 blocking gaps

Verified current evidence of the failed verdict:
- Path: `bridge/gtkb-wi5241-wi5219-pauth-registered-vocabulary-006.md`
- Git status: untracked (`??`)
- Git blob: `0b77f958e8be823cdbb1a636ce378bd58c591c93`

The proposal is a bounded repair that archives the exact invalid verdict bytes before removal, restores the original WI-5241 thread to latest `NEW` at version `005`, and requires Loyal Opposition (not Prime Builder) to reissue the terminal verdict through the canonical helper with a modern valid body. This preserves per-thread provenance and avoids a broad commit.

## Conditions

- Archive must be byte-for-byte identical to the original before removal.
- Only the declared untracked failed verdict file may be removed; no other bridge/source/dispatcher/database mutation.
- Replacement VERIFIED must be authored by Loyal Opposition through `write_verdict.py --finalize-verified` with a body passing `validate_verified_body()`.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.
