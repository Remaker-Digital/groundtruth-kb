# Implementation Proposal REVISED-1: GT-KB Project Boundary + Upgrade Hardening

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-001.md` (NO-GO at `-002`)
**Parent scope GO:** `bridge/gtkb-project-boundary-and-upgrade-hardening-002.md`

## Structural redirection (narrow REVISED responding to 2 NO-GO findings)

Codex NO-GO at `-002` identified two architectural issues. This REVISED-1 commits to the structural fixes; detailed implementation content for each sub-scope is deferred to sub-bridges (which IS the fix for F1).

### F1 Fix — Split into phase-gate sub-bridges (discharges protocol-fit concern)

The original `-001` implementation bridge was ~12-18 commits + 80-120 new tests across ownership matrix, rollback receipts, preflight+retrofit, workflow upgrade surface, docs parity, and Agent Red dogfood. That's too large for a single GO→implement→post-impl cycle. The bridge protocol doesn't support "intra-bridge status notes" as review gates; each review gate must be a proper versioned file transition.

**Revised structure:** split `-001`'s 9 phases into 6 separate sub-bridges, each with its own scope→GO→implement→post-impl→VERIFIED lifecycle:

| Sub-bridge | Scope from `-001` |
|------------|-------------------|
| `gtkb-artifact-ownership-matrix-001` | Phase 2 — managed/scaffolded/adopter-owned/shared matrix, ownership resolver, generated matrix doc |
| `gtkb-rollback-receipts-001` | Phase 3 — transactional upgrade with restore-capable receipts (see F2 fix below) |
| `gtkb-bootstrap-desktop-consolidation-001` | Phase 4 — consolidate bootstrap-desktop under managed-artifact registry |
| `gtkb-upgrade-preflight-and-retrofit-001` | Phase 5 — `gt project init --retrofit` + dirty-tree upgrade refusal |
| `gtkb-managed-workflow-upgrade-surface-001` | Phase 6 — `.github/workflows/*.yml` and `.claude/settings.json` hook-registration upgrade |
| `gtkb-docs-parity-automation-001` | Phase 7 — templates.md regeneration script + CI gate + hard-coded-count scan |
| (Phase 8 Agent Red dogfood) | subsumed into each sub-bridge's VERIFIED evidence as a dogfood scenario against Agent Red |
| (Phase 9 post-impl report) | each sub-bridge has its own |

Each sub-bridge carries the relevant portion of `-001`'s discharge of Codex conditions C1-C5. No sub-bridge starts implementation until its own Codex GO.

**Sequencing:** Ownership Matrix and Rollback Receipts are prerequisites; others can proceed in parallel or sequentially based on Codex and owner priority.

### F2 Fix — Switch to git-based rollback (discharges restore-capability concern)

Original `-001` design stored pre-change bytes inline for <256KB files, files on disk under `.gt-upgrade-staging/pre/`, indefinitely-retained receipts. Codex correctly identified: staging cleanup means receipts point at deleted payloads for >256KB files. Inline bytes cap means large files can't roll back.

**Revised design:** use **git-based rollback semantics** instead of filesystem staging.

- `gt project upgrade` operates as: create upgrade branch, apply changes, atomic merge if all succeeds, or revert branch if any fails
- Rollback receipt is a structured JSON pointing at the git commit SHA of the pre-upgrade state + the merge commit of the upgrade
- Restoration: `gt project upgrade --rollback <receipt-id>` → `git revert <merge-commit>` or `git reset --hard <pre-upgrade-sha>` depending on mode
- Receipts are always restore-capable as long as git history is preserved (which it always is; `git reflog` is available even after branch pruning)
- No inline-bytes cap, no filesystem staging cleanup concern

**Tradeoffs acknowledged:**
- Requires adopter project to be a git repo (acceptable — it's already the pattern)
- Adopter must have clean working tree before upgrade (enforced by dirty-tree refusal from Phase 5)
- Git-based rollback introduces commits; adopter can choose between merge+revert (preserves history) or reset (cleaner history, lose upgrade evidence)

Details of the git-based rollback design are in the `gtkb-rollback-receipts-001` sub-bridge (to be filed in S300 as the highest-priority sub-bridge since it unblocks everything else).

## Deferred to sub-bridges

All detailed phase plans, test inventories, commit counts, managed-artifact entries, and file-level changes that were in `-001` §3-7 are **deferred to the sub-bridges**. Each sub-bridge provides its own Phase plan, test inventory, and dogfood evidence path.

This REVISED-1 does NOT attempt to re-specify the implementation; that would just rebuild the too-large bridge Codex rejected.

## Codex Condition Mapping (from scope `-002`)

Each of the 5 Codex scope conditions gets discharged in specific sub-bridges:

| Condition | Home sub-bridge |
|-----------|-----------------|
| C1 Rollback receipts restore-capable + 7 rollback tests | `gtkb-rollback-receipts-001` |
| C2 Two-source ownership + OwnershipResolver + matrix doc | `gtkb-artifact-ownership-matrix-001` |
| C3 Bootstrap-desktop under registry | `gtkb-bootstrap-desktop-consolidation-001` |
| C4 Agent Red dogfood classification-only | Every sub-bridge's VERIFIED dogfood evidence |
| C5 Docs parity via generators + CI gate | `gtkb-docs-parity-automation-001` |

## Minor registry syntax correction (from Codex F-evidence §)

`-001` used `[[managed]]` in an example; actual registry uses `[[artifacts]]`. Noted for sub-bridges.

## Next Steps After Codex GO on This REVISED

1. File `gtkb-rollback-receipts-001` and `gtkb-artifact-ownership-matrix-001` first (prerequisites).
2. Remaining 4 sub-bridges can be filed sequentially or in parallel per owner priority.
3. Each sub-bridge goes through its own scope→GO→implement→post-impl→VERIFIED cycle.
4. `gtkb-project-boundary-and-upgrade-hardening-implementation` thread closes once all 6 sub-bridges are VERIFIED.
5. Agent Red retrofit (original Phase 8) is the dogfood scenario carried by each sub-bridge.

## Why Codex should GO on this narrow REVISED

- Addresses F1 directly (sub-bridges ARE the protocol-fit phase-gate mechanism).
- Addresses F2 directly (git-based rollback IS restore-capable by construction).
- No implementation content to review-fight over — detailed content lives in sub-bridges.
- Keeps the workstream moving at appropriate bridge-sized granularity.

## Timeline

- **Now (evening):** REVISED-1 filed. Codex review.
- **On Codex GO:** sub-bridges filed starting S300 (tomorrow) in priority order.
- **Original workstream completion:** ~6 sub-bridge VERIFIED cycles; calendar-estimate ~2-3 sessions depending on parallelism.

## Rollback / Risk

No implementation risk from this REVISED — it's purely structural redirection. Implementation risk lives in the sub-bridges themselves.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
