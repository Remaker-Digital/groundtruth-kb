GO

bridge_kind: review
Document: gtkb-skill-rename-cursor-goose-parity
Version: 002
Date: 2026-07-20
Reviewer: Loyal Opposition (goose/G)
reviewer_harness_id: G
reviewer_session_context_id: goose-20260720-lo-skillrename-review
reviewed_document: bridge/gtkb-skill-rename-cursor-goose-parity-001.md
author_session_context_id: G-2026-07-21T05-49-33Z
review_independence: PASS (reviewer session context differs from author session context)

# LO Review: Cursor fallback + Goose manifest parity gaps

## Verdict: GO

The advisory correctly identifies the two remaining MISSING classes after the
skill-rename rollout. Both are pre-existing design states exposed by the
rename, not defects introduced by it. The advisory asks the right questions.
My disposition on each:

## Finding 1 — Cursor fallback surfaces: DEFER (accept-as-deferral)

**Claim:** Every skill capability declares `[capabilities.cursor]` with
`status = "fallback"` and a note about a dedicated Cursor marker-aware
generator tracked separately. The parity checker reports MISSING because
the fallback surface files don't exist at the declared gtkb-* paths.

**Evidence verified:**
- Registry `[capabilities.cursor]` entries declare `surface =
  ".cursor/skills/gtkb-<name>/SKILL.md"` with `fallback = "Cursor uses a
  repo-local generated skill adapter; a dedicated Cursor marker-aware
  generator is tracked separately."`
- Only 5 cursor skill dirs exist on disk (`gtkb-benchmarks`,
  `gtkb-hygiene-investigation`, `gtkb-hygiene-sweep`, `gtkb-propose`,
  `gtkb-sweep-commit`). These are pre-existing repo-local adapters, not
  generated projections.
- The parity checker reports these as `MISSING | Fallback surface is declared
  but absent.` — which is technically correct but misleading, since the
  design intent is that cursor surfaces are deferred pending a dedicated
  generator.

**Disposition:** Accept as deferral. The cursor fallback design is intentional
and pre-dates the rename rollout. The MISSING status is a checker semantics
issue, not a rename defect.

**Recommendation for Prime Builder:** Do NOT create placeholder cursor surface
files to suppress the MISSING count. Instead, consider a parity-checker
enhancement (separate work item) to report fallback-declared-but-absent as
`DEFERRED` or `WAIVED` instead of `MISSING`. That would make the 100 cursor
MISSING entries disappear from the failure count without masking real gaps.

## Finding 2 — Goose manifest: ADOPT (regenerate MANIFEST.json)

**Claim:** The registry has no `[harnesses.goose]` section and no
`[capabilities.goose]` entries. The parity checker resolves goose via
`manifest_adapters` (`.goose/skills/MANIFEST.json`), which was deleted during
the reclaim sweep and never regenerated. No goose manifest generator exists in
`scripts/`.

**Evidence verified:**
- No `[harnesses.goose]` or `capabilities.goose` entries in
  `harness-capability-registry.toml`.
- `.goose/skills/MANIFEST.json` does not exist (confirmed deleted).
- All 44 `.goose/skills/gtkb-*` directories exist on disk with SKILL.md files,
  but there is no manifest indexing them.
- `scripts/goose_harness.py` exists but is not a manifest generator; no
  `generate_goose_*` script exists.
- Parity checker reports goose as `MISSING | registry lacks harness-specific
  capability surface` for all capabilities.

**Disposition:** Adopt — regenerate `.goose/skills/MANIFEST.json`. The goose
harness resolves via manifest, not via registry capability entries. The fix is
to create a manifest generator (or extend an existing generator) that produces
MANIFEST.json from the canonical `.claude/skills/` source, then run it.

**Recommendation for Prime Builder:**
1. Create `scripts/generate_goose_manifest.py` (or extend
   `scripts/generate_api_skill_adapters.py` to also produce goose manifest)
   that reads `.claude/skills/gtkb-*/SKILL.md` and emits
   `.goose/skills/MANIFEST.json` with skill name, path, and SHA-256 entries.
2. Add goose manifest regeneration to the adapter generator verification
   step in the rename rollout's Slice 4.
3. File as a new work item (not WI-5640) — this is a goose-harness gap, not a
   rename-rollout gap. The rename rollout's scope was the 44 canonical skills;
   the goose manifest is a harness-infrastructure gap that predates and is
   independent of the rename.

## Summary of LO disposition

| Finding | Disposition | Action needed | Scope |
|---|---|---|---|
| Cursor fallback MISSING | DEFER | Parity checker enhancement (separate WI) to report as DEFERRED/WAIVED | New WI |
| Goose manifest MISSING | ADOPT | Create goose manifest generator; regenerate MANIFEST.json | New WI |

Neither finding blocks the skill-rename rollout. The rollout is complete;
these are pre-existing harness-infrastructure gaps surfaced by the rollout's
verification step. File two new work items and proceed.

## Decision Needed from Owner

None. This is a GO on the advisory. Prime Builder should file the two new
work items and implement per the recommendations above.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
