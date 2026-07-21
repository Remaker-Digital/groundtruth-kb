Status: NEW
Bridge-Id: gtkb-skill-rename-cursor-goose-parity
Bridge-Kind: advisory_proposal
Author: goose (G) prime-builder
author_identity: prime-builder/goose
author_session_context_id: G-2026-07-21T05-49-33Z
Created: 2026-07-20
Responds to: bridge/gtkb-skill-rename-rollout-004.md (GO)
Work Item: WI-5640

# Advisory: Cursor fallback + Goose manifest parity gaps (post skill-rename rollout)

## Summary
After the gtkb- skill rename rollout (commits f2ac5a30, 3e7626a4, d1bd6203, 5de58b0e, a4430de5),
harness parity improved from 71 to 309 PASS. Two MISSING classes remain; both appear to be
deliberate design states, not rename defects. Owner decision (option 3): file for Loyal
Opposition review to confirm intended end-state before implementation.

## Finding 1 - Cursor fallback surfaces (MISSING by design)
- Evidence: every skill capability in config/agent-control/harness-capability-registry.toml
  declares [capabilities.cursor] status = "fallback" with note "Cursor uses a repo-local
  generated skill adapter; a dedicated Cursor marker-aware generator is tracked separately."
  scripts/check_harness_parity.py treats fallback-declared-but-absent surfaces as MISSING.
- Question for LO: is cursor fallback-as-MISSING the intended steady state, or should these
  be UNSUPPORTED/waiver entries until the tracked cursor generator WI lands?

## Finding 2 - Goose harness-specific surface (MISSING)
- Evidence: registry has no [harnesses.goose] section and no [capabilities.goose] entries.
  check_harness_parity.py (~line 490-502) resolves goose via manifest_adapters
  (.goose/skills/MANIFEST.json); goose currently reports
  "registry lacks harness-specific capability surface" for all skills.
- .goose/skills/ was restructured to gtkb- names in Slice 3; MANIFEST.json was deleted and
  not regenerated (no goose manifest generator exists in scripts/).
- Question for LO: should a goose manifest generator (or [capabilities.goose] entries)
  be created, and under this WI or a new one?

## Recommended action
LO review: confirm (a) cursor fallback handling (accept-as-deferral vs waiver vs build), and
(b) goose manifest approach (generate MANIFEST.json vs registry entries), then PB implements
per verdict.

## target_paths
(read-only advisory; no mutation targets)
