author_identity: prime-builder
author_harness_id: B
author_session_context_id: 67ed84c1-5adb-44f8-ae29-3d0f8fd286b6
author_model: claude-fable-5
author_model_version: 5
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

# 2026-06-10 (S430, Claude Fable 5, harness B): Hygiene investigation + Fable Investigation chartering

**Investigation (read-only, multi-agent):** 16 subagents / 4 workflow rounds (~3.4M subagent tokens), dry-loop decay 65→17→13→7. Report: `independent-progress-assessments/GT-KB-ARCHITECTURE-HYGIENE-INVESTIGATION-2026-06-10.md` — 60 ranked findings **HYG-001..060 (frozen IDs)**, 14 adversarially re-verified (all upheld), 28 absorbed merges, 14 demoted, all 15 prompt seeds adjudicated (S14 refuted codex-side). Systemic stories: bridge dispatch dead end-to-end (WinError 2 on every active target), regression-signal system dead (1,630/2,541 assertions failing, ~93% on pre-isolation Agent-Red paths; session-start sweep dead since 2026-05-13), Agent-Red residue saturation (root config identity, pyproject, CI, templates), enforcement theater (destructive/credential gates only in git-ignored settings.local.json), no retention/backup anywhere (MemBase zero durable backup; 4.76GB orphan LFS in .git; .gtkb-state 3.6GB).

**v2 report** (`...-v2.md`) = parallel investigation by **Antigravity (harness C)**, 45 findings under its own colliding HYG numbering. Verified-merge admitted **HYG-061..068** (antigravity adapters 22 stale/14 missing live; goose registration gaps; GOV-SOT-FRESHNESS ↔ startup-relay-DCL direct contradiction; ~1,004 open WIs vs 162 PAUTH-covered; 76 unwired skill-health findings; AUQ-coverage FAIL = tracker false-positive pollution; doctor isolation suite miscalibrated for platform root). 8 v2 claims refuted with live evidence — list in the advisory; do not re-chase.

**Chartering (grill-me, 7 AUQs):** `DELIB-FABLE-GRILL-20260610-Q1..Q7` (note: their session_id field says "S429-fable-grill" — written before discovering the parallel Antigravity session had claimed S429; this session is S430). Decisions: verified-merge; full milestone with internal waves; hybrid cluster WIs; cluster-level AUQ batches supersede per-finding Tier-1; layered repeatability (deterministic CLI core + `gtkb-hygiene-investigation` skill + delta mode, ≤400K full / ≤150K delta tokens); owner-directed ADVISORY packaging; same-session creation.

**Artifacts created:** `bridge/gtkb-fable-investigation-advisory-001.md` (ADVISORY, bridge_kind governance_advisory) + INDEX entry; `PROJECT-FABLE-INVESTIGATION` + **WI-4413..WI-4435** (FAB-01..23, three waves; FAB-02 tfstate secrets = P0); memberships verified clean (no doubled-prefix); advisory bridge-linked to the project. WIs carry source-owner-directive + DELIB evidence so the deterministic approval-state backfill classifies them `auq_resolved`.

**Reusable gate lessons (new this session):**
- `bridge_kind` is a closed enum per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`: {governance_advisory, implementation_report, index_reconciliation, lo_verdict, operational_state_change, prime_proposal}; custom kinds hard-blocked at Write.
- ADVISORY bridge files must match a mandated template: first line `ADVISORY`; headers bridge_kind/Document/Version/Author/Date; sections `## Source`, `## Claim`, `## Owner Decision Needed`, `## Recommended Prime Action`, `## Classification Slot`.
- The Write tool is blocked for ALL paths under `C:\Users` (root-boundary gate) — including the harness auto-memory store the harness itself designates; in-root `memory/` is the compliant store (this is HYG-016's duality, now with a live enforcement specimen).
- Governed markdown documents under `memory/` require the 6-field author-provenance metadata block at Write time.
- Large repo files can't be generated via one piped command (Windows ~32K command-line limit → ENAMETOOLONG) — chunk python-via-stdin appends at <25KB per call.
- `gt session wrap --harness-name claude --harness-id B` is the `::wrap` deterministic service (defaults to codex — must pass claude/B explicitly).
- decision-capture helper is a library, not a CLI — pipe python importing `.claude/skills/decision-capture/helpers/record_decision.py`.

**Open at session end (uncommitted, deliberate — no commit requested):** advisory + INDEX edit + both reports + this memory file + envelope archives; investigation self-residue `$null` file at root is flagged for deletion in FAB-23.
