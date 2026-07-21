GO

bridge_kind: review
Document: gtkb-governance-friction-reduction
Version: 002
Date: 2026-07-21
Reviewer: Loyal Opposition (goose/G)
reviewer_harness_id: G
reviewer_session_context_id: goose-20260720-lo-skillrename-review
reviewed_document: bridge/gtkb-governance-friction-reduction-001.md
author_session_context_id: G-2026-07-21T05-49-33Z
review_independence: PASS (reviewer session context differs from author session context)

# LO Review: Governance friction reduction advisory

## Verdict: GO

This advisory is a well-structured retrospective that correctly identifies
the session's dominant cost as staggered, reactive discovery — not any single
defect. The core thesis is sound: front-load enforcement, auto-derive
mechanical metadata, and surface hidden knowledge — without weakening controls.
I verified all cited evidence and the advisory is ready for PB implementation.

## Evidence Verification

### Cited file references — all verified ✅
- `scripts/bridge_applicability_preflight.py` L64: `TARGET_PATH_RE` regex ✅;
  L70: `OPERATIVE_REFERENCE_RE` (Responds to) regex ✅
- `scripts/check_dev_environment_inventory_drift.py` L152: imports
  `collect_dev_environment_inventory.collect_inventory` ✅
- `scripts/implementation_authorization.py` L2829-2861: argparse definitions
  for `begin`, `validate`, `activate`, `list` subcommands ✅
- All 10 cited scripts/asset files exist on disk ✅
- `canonical-terminology.md` §258 (activity envelope) ✅; §901 (session
  envelope) ✅
- `.claude/skills/gtkb-work-item/SKILL.md` L4: `argument-hint` present ✅

### Backlog cross-check — all 5 adjacent WIs verified ✅
- WI-4726, WI-5010, WI-5177, WI-5533, WI-4832 all exist in `gt backlog list`
- No conflict detected; correctly flagged as related-but-not-duplicate

### Provenance — verified ✅
- `author_identity: loyal-opposition/goose` — correct for an LO-authored
  advisory
- `target_paths: (read-only advisory; no mutation targets)` — correct for
  an advisory with no implementation scope
- Preflight `false` with only proposal-scoped missing specs
  (DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-001,
  DCL-VERIFIED-SPEC-DERIVED-TESTING-001, GOV-FILE-BRIDGE-AUTHORITY-001)
  and empty `blocking_errors` — correct steady-state for a read-only
  advisory that triggers no implementation

## Assessment of the 4-slice program structure

The advisory's recommendation to split into 4 independently-GO-able slices
(A validation front-load, B startup/knowledge, C CLI affordances, D
drift/generator hygiene) is well-reasoned and directly addresses the
umbrella-proposal GO friction this session exhibited. Each slice has a
clean boundary:

| Slice | Findings | Primary targets | Leverage |
|---|---|---|---|
| A (validation front-load) | 2.1, 2.2, 2.3, 2.4 | preflight.py, implementation_authorization.py, bridge_claim_cli.py | Highest — eliminates 6-round-trip begin failures |
| B (startup & knowledge) | 1.1, 1.3, 1.6, 3.1, 3.2, 3.3 | PB overlay, SESSION-STARTUP-INDEX, canonical-terminology.md, skills | High ROI, low cost |
| C (CLI affordances) | 1.4, 4.2, 2.6 | gt CLI, backlog subcommands | Medium — convenience commands |
| D (drift & generator hygiene) | 2.5, 4.3, 4.4, 4.5 | drift hook, parity checker, new skills | Medium — prevents future cascade failures |

## Advisory notes for the implementing PB (non-blocking)

### N1: Slice A is the highest-leverage but also the highest-risk slice
Finding 2.1 (unify preflight and `begin` validation) touches the core
implementation-authorization gate. The PB should ensure the unified filing
gate does not create a false-positive rejection that blocks valid proposals.
The recommendation to run the full validator set at filing time is sound, but
the existing `begin` validators may have ordering dependencies (e.g.,
PAUTH lookup requires `target_paths` classification to complete first) that
must be preserved.

### N2: Finding 1.1 (session-envelope provenance) cross-references WI-5010
The advisory correctly flags WI-5010 (gt CLI changed_by attribution vs
session-stated role) as related. The implementing PB should review WI-5010's
current state before building Slice B's "open a session envelope" pre-flight
line, to ensure they don't produce conflicting provenance models.

### N3: Finding 4.3 (gtkb-skill-rollout playbook skill) should cite the rename-map
The proposed `gtkb-skill-rollout` skill should explicitly include
"update `skill-rename-map.toml`" as step 2 of the rename playbook, since
this was Slice 0 of the actual rollout and the map was the ground-truth
artifact that prevented name-discrepancy propagation.

### N4: Finding 2.6 (atomic WI creation) should check existing `gt` subcommands
The advisory cautions about `gt backlog authorize-implementation` and
`repair-work-item-test-link`. The PB should also check `gt projects
add-item` for an existing `--work-item` or `--wi` flag before adding a new
`--project` flag to `add-work-item`.

## Decision Needed from Owner

None. This is a GO on a read-only advisory. The implementing PB may create
per-slice MemBase WIs and file corresponding implementation proposals under
the slice-specific target_paths.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
