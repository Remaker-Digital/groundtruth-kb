GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5332 WI-5113 Invalid Terminal VERIFIED Verdict Reissue Repair

bridge_kind: loyal_opposition_review
Document: gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5332
Reviewed: bridge/gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5332-wi5113-invalid-terminal-verdict-reissue` → 0 blocking gaps

Failed-verdict identity evidence (verified independently):
- Path: `bridge/gtkb-wi5113-verified-finalizer-git-no-window-pauth-v2-006.md`
- Git status: untracked (`??`)
- Git blob: `8bc934d88727d2bbd24db2eea4dabe5ede66f33e`
- SHA-256: `097D7BEDEDA4CE255AB77EB39763C37F2FFF87E0DCE0F634DB9ACA9E6B89001D`

The proposal applies the established archive/remove/reissue pattern to one malformed file-only terminal VERIFIED artifact in the WI-5113 chain. It preserves the hunk-scoped owner waiver (`DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER`) and does not broaden it. Prime Builder does not author the replacement VERIFIED.

## Conditions

- Archive must be byte-for-byte identical to the original before removal.
- Only the declared untracked failed verdict file may be removed.
- Replacement VERIFIED must be authored by Loyal Opposition through `write_verdict.py --finalize-verified` with a body passing `validate_verified_body()`.
- Do not absorb the staged unrelated path `bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md` or any other foreign hunk.
- Do not touch the concurrent WI-5320/WI-5328/WI-5330 dispatcher-starvation program.
