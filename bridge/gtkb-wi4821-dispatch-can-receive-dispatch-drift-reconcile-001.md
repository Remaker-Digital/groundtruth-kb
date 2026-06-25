NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d40d99d8-b006-4dd8-8e9d-bce8371a1e4b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; mode=auto

# Reconcile dispatch `can_receive_dispatch` drift — regenerate stale projection + commit overlay (WI-4821)

bridge_kind: operational_state_change
target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json"]

Document: gtkb-wi4821-dispatch-can-receive-dispatch-drift-reconcile
Snapshot: 2026-06-25T~17:15Z

## Summary

Reconcile the `gt bridge dispatch health` WARN — `can_receive_dispatch` drift between
`config/dispatcher/rules.toml` (True) and `harness-state/harness-registry.json` (False)
for harnesses A, B, D, E, F — in the owner-approved **Honest-ON** direction. No source
logic changes; this is a dispatcher config/state reconciliation only:

1. **Regenerate** `harness-state/harness-registry.json` from canonical MemBase via the
   sanctioned generator `python -m groundtruth_kb.harness_projection`.
2. **Commit** the already-present working-tree `config/dispatcher/rules.toml` overlay
   (`can_receive_dispatch = true` for A, B, D, E, F) so the reconcile is durable.

This makes all three dispatch-eligibility surfaces agree at `True` for the active
dispatch-capable harnesses. **Runtime behavior is unchanged** — the overlay already wins
at selection time (`_apply_overlay`), so dispatch is already effectively armed; this only
makes the audit surfaces truthful and removes a misleading stale-False projection.

## Problem — three-surface drift (root cause)

| Surface | Value (A,B,D,E,F) | Authority |
| --- | --- | --- |
| MemBase `harnesses` table (base) | defaults **True** | canonical; `gt harness show --harness A` carries no explicit `can_receive_dispatch`, and codex/claude/cursor/ollama/openrouter are all in `_DISPATCH_RECEIVE_CAPABLE_TYPES` |
| `harness-state/harness-registry.json` (projection) | **False** (stale; generated 2026-06-25T05:05:13Z) | generated hot-path projection of the base |
| `config/dispatcher/rules.toml` (overlay) | **True** (uncommitted) | runtime dispatch overlay |

At selection time `apply_dispatch_config_to_record` overlays `rules.toml` onto the
registry record, and the candidate gate is `record.can_receive_dispatch is not True`
(`groundtruth_kb/bridge_dispatch_config.py`). The overlay (True) wins, so dispatch is
already effectively armed and `gt bridge dispatch health` reports `dispatchable=True` /
selects candidates. The WARN is purely the stale projection disagreeing with the overlay.

The staleness is temporal, not structural: `generate_harness_projection` already merges
the overlay (`load_bridge_dispatch_config` → `build_projection(..., dispatch_config=...)`),
so the projection only fell out of date because the overlay was edited to `true` *after*
the 05:05Z regeneration. A fresh regeneration resolves it deterministically.

## Empirical verification (read-only, pre-proposal)

Running the exact production generator path to a throwaway temp file
(`generate_harness_projection(db, project_root, projection_path=<temp>)`; canonical file
untouched) computed:

```
A codex        can_receive_dispatch=True  status=active
B claude       can_receive_dispatch=True  status=active
C antigravity  can_receive_dispatch=False status=retired
D ollama       can_receive_dispatch=True  status=active
E cursor       can_receive_dispatch=True  status=active
F openrouter   can_receive_dispatch=True  status=active
```

This proves a fresh regeneration clears the drift (projection → True, matching the
overlay) and additionally corrects a second staleness: C (antigravity) is `retired`
(gemini EOL) in canonical state but the on-disk projection predates that.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governs this
  proposal/review/verification cycle (always-blocking cross-cutting bridge governance).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state claims must derive from fresh canonical
  reads; this reconcile brings a stale derived projection back into agreement with its
  canonical MemBase source. Directly on-point: the fix is regenerating a stale projection
  from the authoritative table.
- `GOV-PLATFORM-SOT-REGISTRY-001` — `harness-state/harness-registry.json` is a registered
  platform SoT projection; reconciling it preserves SoT integrity.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — harness-state is the consolidated SoT for
  role/identity/dispatch projection; the projection must reflect the canonical table.
- `GOV-08` — Knowledge Database is the single source of truth; the generated projection
  must reflect the MemBase `harnesses` table.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — harness-state surfaces are read through
  the canonical reader entrypoints; regeneration uses the sanctioned generator, not a
  hand-edit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every
  relevant governing specification before requesting GO (the linkage gate this DCL
  mandates).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Verification plan below derives
  its checks from the linked specs (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` / `GOV-08`
  freshness assertion + the drift-detection test surface), satisfying the spec-derived
  testing requirement. Note: as an `operational_state_change` the thread is terminal-at-GO;
  the verification evidence is supplied in-line rather than via a separate VERIFIED cycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — treats the dispatch-eligibility
  projection as a durable artifact whose state must be reconciled, not left to drift.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the stale projection + retired-harness
  status are lifecycle-state changes that trigger reconciliation capture.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — artifact-oriented stance: the
  owner decision, spec linkage, and reconcile are preserved as durable governed records.

## Prior Deliberations

- `DELIB-20266107` (this session, owner_decision) — owner AUQ chose **Honest-ON**:
  regenerate projection + commit overlay so all three surfaces agree at True; no runtime
  change. Rejected the deliberate-quiesce (OFF) alternative.
- `DELIB-20265888` (owner directive) — harness/dispatch isolation architecture: dispatch
  is triggered by artifact deposit + explicit dispatcher state, not by harnesses
  themselves; reconciling the dispatch-eligibility projection is consistent with that
  isolation model.
- WI-4670 status note (2026-06-25 re-diagnosis) explicitly lists "(3) reconcile
  rules.toml-vs-registry can_receive_dispatch drift (separate candidate)" as remaining
  work; this proposal actions exactly that item under WI-4821.

## Owner Decisions / Input

- **AUQ-S20260625-dispatch-drift-direction** → owner answer: **Honest-ON** (regenerate
  projection + commit overlay so all three surfaces agree at True; no behavior change).
  Captured durably as `DELIB-20266107` (`source_type=owner_conversation`,
  `outcome=owner_decision`). The prior AUQ established the session focus ("Reconcile
  dispatch drift"); this AUQ established the direction.
- No further owner decision is blocking; the reconcile is scoped to the two cited target
  paths and changes no runtime behavior.

## Change Detail (post-GO execution)

1. `python -m groundtruth_kb.harness_projection` (PYTHONPATH=groundtruth-kb/src, project
   venv) — regenerates `harness-state/harness-registry.json` from MemBase, applying the
   working-tree overlay. Expected diff: `can_receive_dispatch` False→True for A,B,D,E,F;
   C status corrected to retired; `generated_at` refreshed.
2. Stage + commit `config/dispatcher/rules.toml` (overlay false→true, already on disk) and
   the regenerated `harness-state/harness-registry.json` in one scoped commit
   (`chore(dispatch): WI-4821 reconcile can_receive_dispatch drift to Honest-ON`).
3. Confirm `gt bridge dispatch health` no longer reports the `can_receive_dispatch` drift
   findings.

Both targets are git-tracked and not ignored. No source logic, no test, no hook, no KB
schema changes — dispatcher config + generated state only.

## Verification plan (spec-derived)

- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001 / GOV-08**: after regeneration, assert the on-disk
  `harness-state/harness-registry.json` `can_receive_dispatch` values equal the values
  computed by the canonical generator for the current MemBase table (True for A,B,D,E,F;
  False/retired for C). Evidence already captured by the read-only temp-file run above;
  re-confirmed on the real file post-commit.
- **WARN cleared**: `gt bridge dispatch health` output no longer contains
  `dispatch config drift warning: ... can_receive_dispatch ...` for A,B,D,E,F.
- **No behavior regression**: `gt bridge dispatch status` still selects the same
  candidates (PB: A,E,B; LO: D,F) — runtime selection unchanged (overlay already won).
- Targeted test surface: `platform_tests/scripts/test_bridge_dispatch_config.py` (drift
  detection) and the harness-projection projection tests remain green
  (`python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q`).

## Rollback

`git revert` the single reconcile commit restores the prior committed state
(`rules.toml` overlay=false, prior projection). Because runtime already reads True via
the uncommitted overlay, a revert would re-introduce the (cosmetic) drift WARN but not
change effective dispatch behavior. The change is fully reversible and low-risk.

## Bridge Protocol Compliance

This proposal is filed as the next numbered, append-only bridge file
(`bridge/gtkb-wi4821-dispatch-can-receive-dispatch-drift-reconcile-001.md`). Prior bridge
versions are never deleted or rewritten; the numbered/versioned bridge file chain remains
the canonical audit trail per `GOV-FILE-BRIDGE-AUTHORITY-001`, with TAFE-backed dispatcher
state as the workflow authority.

## Risk

Low. No source/test/hook/KB changes. The only behavioral surface — dispatch eligibility —
is unchanged (already True at runtime via the overlay). Residual storm posture is
unchanged and tracked separately under WI-4670 (controlled single-worker dispatch test)
and the WI-4787 shadow dispatcher daemon (`Running: False`); this proposal does not alter
that posture, it only makes the audit surfaces consistent with the already-effective
runtime.
