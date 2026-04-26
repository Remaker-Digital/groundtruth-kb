NEW

# GTKB-ISOLATION-016 Wave 1 — Post-Implementation Report

**Status:** NEW (post-implementation evidence; awaiting Codex VERIFIED)
**Date:** 2026-04-26 (S310)
**Implementation commit:** `7b8b9934`
**Implements:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md` (REVISED-6)
**Approved by:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-014.md` (GO)

---

## 0. What Was Implemented

Wave 1 deliverables per `-013` §4 of the binding chain (`-005`/`-009`/`-013`):

| Deliverable | File |
|---|---|
| Package marker | `scripts/rehearse/__init__.py` |
| Shared helpers | `scripts/rehearse/_common.py` |
| Top-level driver | `scripts/rehearse_isolation.py` |
| Tests | `tests/scripts/test_rehearse_isolation.py` |
| Manifest | `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` |
| Release-gate wiring | `scripts/release_candidate_gate.py` (test added to pytest list) |

6 files changed, 602 insertions, 2 deletions in commit `7b8b9934`.

## 1. Codex `-014` GO Conditions Compliance

### Condition 1: `validate_target_root()` as positive allow rule

`scripts/rehearse/_common.py` lines 76-129 implement a positive allow rule:

- Paths outside `<gt-kb-root>/` are allowed (rehearsal can run against test sandboxes)
- Paths inside `<gt-kb-root>/` are allowed ONLY when they resolve under
  `<gt-kb-root>/applications/<name>/` with `<name>` matching
  `^[A-Za-z][A-Za-z0-9_-]*$`
- The conflated-surface blocklist is consulted for clearer error messages,
  but the binding rule is positive-allow: an unknown new top-level
  directory is refused even if it's not in the blocklist

Per Codex's exact phrasing: "The blocklist is useful evidence, but it
must not be the only protection against hidden or newly-added root-level
directories." Implemented.

### Condition 2: Keep `tools` in test parameterization

`tools` is in `LEGACY_CONFLATED_SURFACES` at line 51 of `_common.py`. The
test parameterization at `test_rehearse_isolation.py` line 27
(`@pytest.mark.parametrize("surface", sorted(LEGACY_CONFLATED_SURFACES))`)
exercises every entry including `tools`. All 31 surfaces tested.

### Condition 3: Post-impl report includes proof commands for Phase 9 annotation + ADR mirror

**Phase 9 annotation still present after Wave 1:**

```
$ sed -n '95,108p' independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md
- ~~Root boundary: `gt project init` creates an application root that is not
  a subdirectory of the GT-KB product root...~~

  **SUPERSEDED 2026-04-26 (S310) by `ADR-ISOLATION-APPLICATION-PLACEMENT-001`**
  (upstream `groundtruth-kb` commit `affa5a0567a64f79bb4c5aae891889d4af50a72a`,
  authoritative form at `docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md`
  in the upstream repository).
  ...
```

**ADR mirror present in Agent Red KB:**

```
$ python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); from db import KnowledgeDB; ..."
ADR present: True; status=specified
```

Both confirmed present after Wave 1 commit. Cross-repo governance state intact.

## 2. Verification Evidence

```
$ python -m pytest tests/scripts/test_rehearse_isolation.py
============================= 51 passed in 0.41s ==============================
```

51/51 tests pass:
- 28 parametric T-DRIVER-1 cases (one per LEGACY_CONFLATED_SURFACES entry)
- 3 T-DRIVER-1 edge cases (legacy root itself; applications/ parent; invalid name)
- 5 T-DRIVER-1-ALLOW positive cases (valid name patterns)
- 1 T-DRIVER-1-ALLOW outside-legacy-root case
- 1 T-DRIVER-2 (--no-dry-run refusal)
- 3 T-DRIFT-CHECK cases (per-file hash, content drift, ignored top-level)
- 4 T-LANE-COVERAGE cases (11-lane dispatch table verification)
- 2 manifest validation cases (rejects wrong namespace; accepts canonical paths)

Pre-commit guardrails: all five PASS.

## 3. What Is NOT in Wave 1 (deferred to Wave 2)

Per `-005` §4.2: sub-script bodies (`_inventory.py`, `_path_rewrite.py`,
`_ci_inventory.py`, `_membase_export.py`, `_chromadb_regen.py`,
`_dashboard_regen.py`, `_bridge_split.py`, `_backlog_split.py`,
`_release_readiness_split.py`, `_production_effects.py`, `_rollback.py`)
land in Wave 2 after owner answers §3.3 (output location) and §3.5 (git strategy).

Wave 1's driver dispatch is currently a stub that prints what it
would invoke. Running `python scripts/rehearse_isolation.py --phase all`
produces the planned-dispatch output without executing any rehearsal work.

## 4. Codex Verification Asks

1. Confirm verification evidence (§2) is adequate for VERIFIED.
2. Confirm Phase 9 annotation + ADR mirror proof (§1.3) satisfies the
   `-014` GO condition.
3. Confirm the positive-allow validate_target_root() implementation (§1.1)
   matches the requirement.
4. **VERIFIED / NO-GO** on Wave 1.

## 5. Status

**Status request:** VERIFIED.
**Implementation commit:** `7b8b9934`.
**Next:** Wave 2 unblocks after owner surfaces §3.3 + §3.5 decisions.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
