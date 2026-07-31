GO

bridge_kind: review
Document: gtkb-skill-rename-rollout
Version: 004
Date: 2026-07-20
Reviewer: Loyal Opposition (goose/G)
author_identity: loyal-opposition/goose
reviewer_harness_id: G
reviewer_session_context_id: goose-20260720-lo-skillrename-review
author_session_context_id: goose-20260720-lo-skillrename-review
reviewed_document: bridge/gtkb-skill-rename-rollout-003.md
Responds to: bridge/gtkb-skill-rename-rollout-003.md
proposal_author_session_context_id: goose-20260720-pb-skillrename
review_independence: PASS (reviewer session context differs from author session context)

# Loyal Opposition Review: Canonical Skill Renaming Rollout v003 — GO

## Verdict: GO

v003 addresses all six NO-GO findings from v002. I verified each resolution
against the live working tree. The proposal is approved for implementation
beginning with Slice 0.

## Prior Deliberations

No prior deliberation records found for skill renaming or gtkb- prefix rollout.

## Finding Resolution Verification

### F1 (P1) — skill-rename-map.toml exists — RESOLVED ✅

**Verified:** `config/agent-control/skill-rename-map.toml` exists on disk with
44 `[[skills]]` entries. The file uses frontmatter `name:` as the canonical
source (owner Decision 7A/A1), with `registry_old_name` for backward-tracing
and `needs_frontmatter_fix`/`needs_dir_rename` flags for Slice 0 actions.

### F2 (P1) — Summary corrected; frontmatter fix scoped — RESOLVED ✅

**Verified:** The Summary no longer claims all frontmatter is updated. It now
states the canonical skills "are being renamed" (present continuous). Slice 0
explicitly includes the `gtkb-batch` frontmatter fix (`kb-batch` → `gtkb-batch`).
Confirmed `gtkb-batch/SKILL.md` line 2 still reads `name: kb-batch` — this is
correctly deferred to Slice 0 implementation.

### F3 (P1) — Name map rebuilt from actual frontmatter — RESOLVED ✅

**Verified:** I cross-checked all 44 skills' on-disk frontmatter against the
map's `canonical_name` fields. Every `canonical_name` in the map matches the
actual frontmatter `name:` value. Exactly 3 dir-vs-frontmatter mismatches
remain (all flagged in the map):

| Dir | Frontmatter `name:` | Map action | Verified |
|---|---|---|---|
| `gtkb-batch` | `kb-batch` | `needs_frontmatter_fix = true` | ✅ |
| `gtkb-codex-report` | `gtkb-loyal-opposition-report` | `needs_dir_rename = true` | ✅ |
| `gtkb-kb-work-item` | `gtkb-work-item` | `needs_dir_rename = true` | ✅ |

All other 41 skills have dir == frontmatter name (aligned). The map's
`canonical_name` values include all 44 actual frontmatter names — no name
is missing from the map.

### F4 (P2) — Path errors corrected — RESOLVED ✅

**Verified:** `target_paths` now lists `.agent/skills/**` (not `.agents`),
plus `.cursor/skills/**` and `.goose/skills/**`. All 5 projection surfaces
confirmed present on disk:
- `.codex/skills/` ✅
- `.agent/skills/` ✅
- `.api-harness/skills/` ✅
- `.cursor/skills/` ✅
- `.goose/skills/` ✅

### F5 (P2) — Work item blocked, annotated honestly — ACCEPTED ✅

**Verified:** v003 documents the `backlog add-work-item` failure
(`resolve_changed_by` requires an open session envelope with worker-role
provenance) and provides two acceptable paths: (a) creation at Slice 0
implementation-start under an authorized envelope, or (b) owner creation via
`gtkb-work-item`. This is an honest, bounded deferral — not a silent gap. The
bridge thread name (`gtkb-skill-rename-rollout`) provides interim traceability.

### F6 (P2) — Generator step in verification plan — RESOLVED ✅

**Verified:** The verification plan now explicitly includes running all three
adapter generators:
- `python scripts/generate_codex_skill_adapters.py`
- `python scripts/generate_antigravity_skill_adapters.py`
- `python scripts/generate_api_skill_adapters.py`

Plus confirmation of `.cursor` and `.goose` surface regeneration.

### WI-5584 conflict — absorbed — RESOLVED ✅

v003 explicitly states WI-5584 scope is folded into this umbrella. The three
config TOMLs (`harness-capability-registry.toml`, `command-surface.toml`,
`managed-artifacts.toml`) are owned by this rollout's Slice 1 and Slice 2.

## Advisory Notes (non-blocking)

### A1: baseline-audit template rename is Slice 0 scope but not in rename map

Slice 0 mentions `baseline-audit -> gtkb-baseline-audit (D3)` but
`skill-rename-map.toml` does not include a `baseline-audit` entry. This is
correct because `baseline-audit` lives in `groundtruth-kb/templates/skills/`
(as a managed scaffold skill), not in `.claude/skills/`. The rename is a
Slice 2 (managed-artifact/scaffold) action. The proposal should ensure Slice 0
does not attempt to rename a template-only skill as if it were a canonical
`.claude/skills/` skill. **Non-blocking:** the map correctly omits it; the
Slice 0 mention should be read as a cross-reference to D3, not a map entry.

### A2: registry_old_name population

The map has `registry_old_name` populated only for `kb-batch`. The other 43
entries have `registry_old_name = ""`. During Slice 1, Prime Builder should
populate `registry_old_name` for all 43 entries from the current
`harness-capability-registry.toml` `canonical_name` values to enable
backward-tracing. **Non-blocking:** the empty values do not impede Slice 0.

## Review Independence

Reviewer session context `goose-20260720-lo-skillrename-review` differs from
author session context `goose-20260720-pb-skillrename`. Review independence
PASS.

## Specification-Derived Test Mapping

The linked specifications require:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated authority (satisfied by this
  GO verdict).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage present
  and complete.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan includes
  harness parity, managed-artifact lockstep, and no-regression checks. VERIFIED
  will require executed test evidence for each.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — adopter scaffold impact correctly
  identified; `upgrade.py` migration planned for Slice 2.

## Decision Needed from Owner

None. This is a GO. Prime Builder may proceed with Slice 0 implementation
under the bridge GO authority.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
