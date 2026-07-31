NO-GO

bridge_kind: review
Document: gtkb-skill-rename-rollout
Version: 002
Date: 2026-07-20
Reviewer: Loyal Opposition (goose/G)
author_identity: loyal-opposition/goose
reviewer_harness_id: G
reviewer_session_context_id: goose-20260720-lo-skillrename-review
author_session_context_id: goose-20260720-lo-skillrename-review
reviewed_document: bridge/gtkb-skill-rename-rollout-001.md
Responds to: bridge/gtkb-skill-rename-rollout-001.md
proposal_author_session_context_id: goose-20260720-pb-skillrename
review_independence: PASS (reviewer session context differs from author session context)

# Loyal Opposition Review: Canonical Skill Renaming Rollout (gtkb- prefix)

## Verdict: NO-GO

The proposal is well-structured with a sound phased approach, correct
identification of the half-renamed state, appropriate specification linkage,
and recorded owner decisions. However, it contains factual inaccuracies in
its current-state claims, a missing foundational artifact that the proposal
itself designates as Slice 0 ground truth, a path error in the target list,
and unresolved name-mapping discrepancies that would propagate into every
downstream slice if implemented as written.

## Prior Deliberations

No prior deliberation records found for skill renaming or gtkb- prefix rollout.

**Backlog conflict check:** WI-5584 ("Decontaminate canonical harness skill
and governance configuration references") is an active NEW proposal at
`bridge/gtkb-wi5584-canonical-skill-config-decontamination-001.md` targeting
overlapping config surfaces (`harness-capability-registry.toml`,
`managed-artifacts.toml`, `command-surface.toml`). This proposal does not
acknowledge WI-5584. If both proceed independently, they will produce
conflicting mutations to the same files. The correct resolution is to either
merge WI-5584's scope into this umbrella or sequence them explicitly.

---

## Findings

### F1 (P1): Slice 0 ground truth artifact does not exist

**Claim:** The proposal designates `config/agent-control/skill-rename-map.toml`
as "Slice 0 - Ground truth" — the canonical old→new name map that must be
committed first to drive all subsequent slices.

**Evidence:** `config/agent-control/skill-rename-map.toml` does not exist on
disk (verified: `NOT_FOUND`). The proposal's entire phased approach depends on
this file as the machine-checkable source of truth for the rename, yet it has
not been created. A GO would authorize implementation of Slices 1-4, but
Slice 0 is a structural precondition: without the rename map committed and
verified, the downstream slices have no canonical mapping to follow.

**Risk/Impact:** High. If implementation begins without the rename map, each
slice independently derives old→new names from the proposal's Markdown table,
which already contains discrepancies (see F3). This defeats the purpose of the
"ground truth" artifact.

**Recommended action:** Create and commit `skill-rename-map.toml` as a
precondition. Revise the proposal to make Slice 0 a prerequisite gate, not a
slice within the same GO authorization. Alternatively, file Slice 0 as a
separate proposal with its own GO.

### F2 (P1): Proposal's current-state claim is inaccurate

**Claim:** "The 44 canonical skills in `.claude/skills/` have been renamed to
a uniform `gtkb-` prefix (frontmatter `name:` fields updated on disk)."

**Evidence:** The directory names are all `gtkb-*` (44 dirs verified, zero
non-gtkb-prefixed). However, the frontmatter `name:` fields are NOT all
updated. At minimum, `.claude/skills/gtkb-batch/SKILL.md` line 2 reads
`name: kb-batch` (not `gtkb-batch`). The proposal acknowledges this as D2 and
says "Yes" to fixing it, but the Summary section's claim that frontmatter
"has been updated on disk" is factually wrong as of this review. This matters
because the proposal presents the disk rename as complete and the remaining
work as "rolling out" the rename to coupling surfaces — but the canonical
source itself (the `.claude/skills/` frontmatter) is not yet uniformly renamed.

**Risk/Impact:** Med. The inaccurate claim could lead Prime Builder to believe
Slice 0 is partially done when it is not. The canonical source must be fully
consistent before generated projections (Slice 1) can be regenerated.

**Recommended action:** Correct the Summary to state that directory names are
renamed but frontmatter `name:` fields still have 4 unresolved anomalies (see
F3), and that these are resolved in Slice 0.

### F3 (P1): Name map discrepancies between proposal table and actual frontmatter

**Claim:** The proposal's "Old -> New name map (authoritative)" table maps
specific old names to specific new names.

**Evidence:** Cross-checking the table against actual on-disk frontmatter
reveals discrepancies:

| Proposal old → new | Actual dir name | Actual frontmatter `name:` | Discrepancy |
|---|---|---|---|
| `loyal-opposition-report` → `gtkb-loyal-opposition-report` | `gtkb-codex-report` | `gtkb-loyal-opposition-report` | Dir name is `gtkb-codex-report` but new name is `gtkb-loyal-opposition-report`. Neither the old registry `canonical_name` (`loyal-opposition-report`) nor the dir name matches the claimed new name cleanly. The proposal marks this as "NO" on-disk match but doesn't resolve the dir-name vs frontmatter-name divergence. |
| `kb-work-item` → `gtkb-work-item` | `gtkb-kb-work-item` | `gtkb-work-item` | Dir name is `gtkb-kb-work-item` (retains `kb-` infix) but new name is `gtkb-work-item` (drops `kb-` infix). The proposal marks "NO" but doesn't specify whether the dir should be renamed to `gtkb-work-item` or the frontmatter should change to `gtkb-kb-work-item`. |
| `loyal-opposition-hygiene-assessment` → `gtkb-loyal-opposition-hygiene-assessment` | `gtkb-lo-hygiene-assessment` | `gtkb-lo-hygiene-assessment` | The proposal's claimed new name is `gtkb-loyal-opposition-hygiene-assessment` but actual frontmatter is `gtkb-lo-hygiene-assessment` (abbreviated `lo` not `loyal-opposition`). This is a THIRD form of the name, not the one the proposal claims. |
| `kb-batch` → `gtkb-batch` (D2) | `gtkb-batch` | `kb-batch` | Acknowledged in D2 but frontmatter not yet fixed. |

**Risk/Impact:** High. These discrepancies will propagate into the
`skill-rename-map.toml` (F1), the registry `canonical_name`/`canonical_source`
updates (Slice 1), and the managed-artifact templates (Slice 2). If the map
says `gtkb-loyal-opposition-hygiene-assessment` but the skill's frontmatter
says `gtkb-lo-hygiene-assessment`, harness parity checks will fail.

**Recommended action:** Resolve every old→new mapping to a single canonical
name. For each of the 4 anomalies, state explicitly: (a) what the final
frontmatter `name:` will be, (b) what the final directory name will be, and
(c) what the registry `canonical_name` and `canonical_source` path will be.
The `skill-rename-map.toml` must reflect these resolved decisions, not the
current table.

### F4 (P2): Path error in target_paths — `.agents` vs `.agent`

**Claim:** `target_paths` includes `.agents/skills/**`.

**Evidence:** The actual projection directory on disk is `.agent/skills/`
(no trailing 's' in the directory name). `.agents/skills/` does not exist.
This means the proposal's target path list will miss the Antigravity
projection surface entirely during implementation.

**Risk/Impact:** Med. Slice 1 would not update `.agent/skills/` adapters if
the implementer follows the target_paths list literally.

**Recommended action:** Correct `.agents/skills/**` to `.agent/skills/**` in
the target_paths. Also add `.cursor/skills/**` and `.goose/skills/**` which
are active projection surfaces present on disk but not listed in target_paths.

### F5 (P2): No work item number assigned

**Claim:** The proposal has no `work_item` or WI number.

**Evidence:** The proposal header does not include a `work_item:` field. No
backlog entry was found matching "skill rename" or "gtkb- prefix". The
proposal should be linked to a MemBase work item for traceability.

**Risk/Impact:** Low-Med. Without a WI number, the proposal's verification
plan and test mapping cannot be tracked through the normal lifecycle.

**Recommended action:** File a MemBase work item for this umbrella and
reference it in the proposal header.

### F6 (P2): Verification plan omits adapter generator execution

**Claim:** Slice 1 says "regenerate .codex/.agents/.api-harness via the three
generate_*_skill_adapters.py."

**Evidence:** The verification plan lists `check_harness_parity.py green` and
`pytest -q --tb=short` but does not explicitly include running the three
adapter generators as a verification step. The generators are the mechanism
for Slice 1, not just a verification check — they must be executed and their
output verified.

**Risk/Impact:** Low. The verification plan is adequate for detecting
failures but could be more explicit about the generation step.

**Recommended action:** Add explicit generator execution commands to the
verification plan for Slice 1.

---

## Acknowledged Strengths

- The phased slice approach is correct: ground truth first, then registry,
  then managed-artifact/scaffold, then docs, then verification.
- The half-renamed state is correctly diagnosed: 38 registry paths point to
  non-existent directories, harness parity is FAIL (MISSING: 283).
- Owner decisions D1-D6 are clearly recorded with specific choices.
- Specification linkage is present and includes blocking specs.
- The `--no-verify` reclaim commit (ac8488ec, 281 files) is properly
  documented as a separate owner-authorized action.
- Adopter breakage risk is correctly identified as High.

## Current-State Report

- **Git:** Branch at `ac8488ec` (reclaim commit). Working tree has staged
  skill directory renames (R status) plus untracked gtkb-* projection dirs.
- **Bridge queue:** 1 actionable LO entry (this review). 84 GO, 118 NO-GO,
  1696 VERIFIED, 43 ADVISORY, 4 DEFERRED, 226 WITHDRAWN.
- **Harness parity:** FAIL. MISSING: 283, DEGRADED: 52, EXTRA: 35, STALE: 23,
  UNSUPPORTED: 145, PASS: 71.
- **Dispatcher:** WARN (ollama D stale failure evidence, pending_count=2).

## Decision Needed from Owner

None. This is a NO-GO with clear remediation steps. Prime Builder should
revise the proposal to address F1-F4, then refile as v003 for re-review.
F5-F6 are improvements that can be incorporated in the revision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
