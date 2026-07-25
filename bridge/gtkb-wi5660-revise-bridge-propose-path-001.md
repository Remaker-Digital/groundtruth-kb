NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c58a8564-bed2-41d4-851b-075b84e86797
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5660-revise-bridge-propose-path
Version: 001
bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5660
target_paths: [".claude/skills/gtkb-bridge/helpers/revise_bridge.py", "platform_tests/skills/test_bridge_revise_helper.py"]

# WI-5660 — Fix revise_bridge.py stale bridge-propose helper path (fast-lane reliability fix)

## Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

All four eligibility criteria hold:

1. Origin is defect (WI-5660 origin=defect). Yes.
2. No new public API, CLI surface, or behavior beyond removing the defect — the change only makes an existing path constant resolve the renamed skill directory. Yes.
3. No new or revised requirement or specification. Yes.
4. Small, single-concern: 2 files, ~20 net lines (one resolver function, one test-path correction, one regression test). Yes.

Covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through WI-5660's active `PROJECT-GTKB-RELIABILITY-FIXES` membership (linked 2026-07-24 via `gt projects add-item`; WI-5660 additionally retains its `PROJECT-GTKB-HOUSEKEEPING-HARDENING` context).

## Problem

`.claude/skills/gtkb-bridge/helpers/revise_bridge.py:27` hardcoded
`BRIDGE_PROPOSE_HELPER = PROJECT_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"`,
but the skill directory was renamed to `gtkb-bridge-propose` during the WI-5651 skill-rename canonicalization.
`file_revision()` therefore raised `FileNotFoundError` at `_load_bridge_propose_helper()`, breaking the governed
REVISED-filing path for Prime Builder. The sibling `impl_report_bridge.py:31-41` already uses the correct
fallback-tuple resolver (`("gtkb-bridge-propose", "bridge-propose")`); revise's constant was missed by the WI-5651
sweep. WI-5659 worked around the same defect with an untracked runtime-patch wrapper
(`.gtkb-state/_wi5659-revised/run_revise.py`) and deferred the permanent fix to WI-5660.

Additionally, the helper's own test `platform_tests/skills/test_bridge_revise_helper.py:12` points `HELPER_PATH` at
the pre-rename `.claude/skills/bridge/helpers/` (should be `gtkb-bridge`), so the entire test module currently errors
on load. That line must be corrected for any test in the module (including the new regression test) to run.

## Proposed Change

1. `revise_bridge.py`: replace the single hardcoded `BRIDGE_PROPOSE_HELPER` line with a
   `_resolve_bridge_propose_helper(root)` fallback-tuple resolver, matching the proven `impl_report_bridge.py:31-41`
   pattern (prefer `gtkb-bridge-propose`, fall back to `bridge-propose`).
2. `test_bridge_revise_helper.py`: correct `HELPER_PATH` line 12 from `"bridge"` to `"gtkb-bridge"`.
3. `test_bridge_revise_helper.py`: add a regression test asserting `BRIDGE_PROPOSE_HELPER.is_file()` and that
   `_load_bridge_propose_helper()` loads a module exposing `scan_credential_hits`.

## Implementation Status Disclosure (early application under bridge-repair urgency)

Change 1 (the `revise_bridge.py` resolver) was applied ahead of this GO during session
`c58a8564-bed2-41d4-851b-075b84e86797` under owner AUQ 2026-07-24, as a minimal bridge-function repair to unblock the
WI-5441 Phase 1B REVISED filing (`bridge/gtkb-wi5441-registry-db-schema-008.md`), which was blocked by this exact
defect. The fix is validated end-to-end: v008 filed successfully through the repaired path (revise helper exit 0).
This proposal seeks GO for that applied change plus the still-pending protected-path test edits (changes 2 and 3),
which have NOT been applied — they require the implementation-start packet derived from this GO because
`platform_tests/` is a protected path. No commit has been made; `revise_bridge.py` is modified-and-clean in the
worktree.

## Cross-Harness Disposition

`revise_bridge.py` is a Claude-canonical helper with generated per-harness adapters (Codex, Goose) and a scaffold template. Per-harness disposition for this fast-lane fix:

| Harness / surface | Path | Disposition |
| --- | --- | --- |
| Claude (canonical) | `.claude/skills/gtkb-bridge/helpers/revise_bridge.py` | FIXED by change 1 — the canonical source from which adapters are generated. |
| Codex (generated adapter) | `.codex/skills/gtkb-bridge/helpers/revise_bridge.py` | Parity DEFERRED — restored by regenerating adapters from the fixed canonical via `scripts/generate_codex_skill_adapters.py`, not per-file editing. |
| Goose (generated adapter) | `.goose/skills/gtkb-bridge/helpers/revise_bridge.py` | Parity DEFERRED — same regeneration path. |
| Scaffold template | `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` | Scaffold-hygiene fix DEFERRED — affects only new adopter-project scaffolding, not any live REVISED-filing path. |

The deferred non-Claude surfaces are non-blocking for the Claude REVISED-filing path this fast-lane fix repairs, and the correct fix for generated adapters is regeneration (a distinct operation with in-flight-worktree entanglement risk) rather than hand-editing. The deferral scope is the broader skill-rename stale-path debt the owner authorized capturing as a follow-on backlog item on 2026-07-24.

Owner waiver: DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001/PARITY-DISPOSITION-GATE — owner AUQ 2026-07-24 (session c58a8564-bed2-41d4-851b-075b84e86797) — non-Claude harness-surface parity for `revise_bridge.py` is deferred to the broader stale-path-debt follow-on WI per owner direction; the Claude canonical is fixed in this proposal and the adapters regenerate from it.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — the fast-lane governance path this proposal uses.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority; the broken REVISED-filing path this repairs.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation-proposal specification linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scoped implementation authorization (standing PAUTH coverage).
- `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification for the regression test.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement is needed; this only repairs path resolution so it
matches the completed WI-5651 skill rename.

## Owner Decisions / Input

- Owner AUQ 2026-07-24 (session `c58a8564-bed2-41d4-851b-075b84e86797`): after WI-5441 v008 filing was blocked by
  this defect, the owner selected "Fast-lane fix, then file v008" (authorizing the early bridge-repair application of
  change 1) and then "Proper fast-lane cycle" (authorizing this governed fast-lane proposal → Loyal Opposition GO →
  implement the test edits → Loyal Opposition VERIFIED → commit, rather than an ungoverned edit).

## Prior Deliberations

- `WI-5651` skill-rename path-canonicalization threads (commits `d8926a8fb`, `2e32daac2`) — the sweep that added the
  fallback resolver to `impl_report_bridge.py` but missed `revise_bridge.py:27`.
- `WI-5659` — restored governed commit-finalization; worked around this defect with an untracked runtime-patch
  wrapper and explicitly deferred the permanent line-27 fix to WI-5660.
- `bridge/gtkb-wi5441-registry-db-schema-008.md` — the WI-5441 REVISED whose filing this defect blocked (now unblocked
  by the applied change 1).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the owner decision establishing the reliability fast-lane path.

## Verification Plan (Spec-to-Test Mapping)

| Governing concern | Test / command | Expected |
| --- | --- | --- |
| Defect removed (propose-helper resolves) | New `test_bridge_propose_helper_resolves_to_existing_file`: asserts `BRIDGE_PROPOSE_HELPER.is_file()` and `_load_bridge_propose_helper()` exposes `scan_credential_hits` | PASS |
| Regression coverage restored | `python -m pytest platform_tests/skills/test_bridge_revise_helper.py -q` | all pass (module previously errored on load) |
| Integration proof (already observed) | `revise_bridge.py file gtkb-wi5441-registry-db-schema` filed `-008.md` | exit 0 (observed 2026-07-24) |
| Code quality | `ruff check` and `ruff format --check` on both changed files | pass |

## Risk And Rollback

Risk: minimal. Change 1 mirrors an in-repo proven pattern and is validated live. Changes 2 and 3 are test-only.
Rollback: revert the two files; no data, behavior, or runtime-state change beyond path resolution.

## Recommended Commit Type

`fix:` — repairs broken path resolution; no new capability surface.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
