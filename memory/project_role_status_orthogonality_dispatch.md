# Project: Role/Status Orthogonality Dispatch (operational memory)

Operational notepad (NOT canonical). Canonical state: MemBase
(`PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`, `WI-3509`) + bridge thread
`gtkb-role-status-orthogonality-dispatch-slice-2-resolver`. Owner directive:
`DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`.

## Umbrella state

- Scoping GO: `bridge/gtkb-role-status-orthogonality-dispatch-scoping-004.md`.
- Slice 1 (ADR+DCL) VERIFIED: `...-slice-1-adr-dcl-010.md`. Created
  `ADR-ROLE-STATUS-ORTHOGONALITY-001` v1, `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
  v1, `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (all `specified`).

## Slice 2 (resolver + attribution) — S379, 2026-06-01

Status: **Slice 2 VERIFIED at `-004` + committed by owner (commit `e01f5695`).
Landing reconciliation in flight (proposal `-001` NEW, awaiting Codex GO).**
(Slice 2: `-001` NEW → Codex GO `-002` → impl-start → 4 files + 13 tests → report
`-003` → Codex VERIFIED `-004`. Verify: ruff PASS; pytest 9 pre-existing fail / 71
passed; 13 new tests PASS; 0 regressions.)

### Landing reconciliation (S379 owner AUQ)

Owner AUQ chose **suspend C now (accept role drop)** after I surfaced that the
live data model strips an inactive harness's role (`harness_ops.transition_harness`
→ `reconcile_role_assignments`; no `→inactive` verb; model uses `registered` not
the ADR-renamed `inactive`) — contradicting ADR-ROLE-STATUS-ORTHOGONALITY-001 §9
("C can be prime-builder + inactive"), an unscoped umbrella gap.

- Reconciliation WI: **WI-3511** (suspend C); PAUTH
  `PAUTH-...-SLICE-2-LANDING-REGISTRY-RECONCILIATION-SUSPEND-C` (active, includes
  WI-3511, specs ADR/DCL/REQ, class `harness-registry-lifecycle`).
- Follow-on WI: **WI-3512** (decouple `harness_ops` role-retention from active
  status to honor ADR §9; P2).
- Bridge: `gtkb-role-status-orthogonality-dispatch-landing-reconciliation`. `-001`
  NEW (suspend C) → Codex **NO-GO `-002`** (correct: premise error) → **REVISED `-003`**
  (projection regen) → Codex **GO `-004`** → impl-start packet → **regen DONE**
  (`python -m groundtruth_kb.harness_projection`) → report -005 (**parallel Antigravity
  C/S380 overwrote my -005**) → Codex **NO-GO -006** (clause-gate `GOV-STANDING-BACKLOG-001/
  CLAUSE-VISIBILITY-BULK-OPS` fail on Antigravity's terse clause-scope; behavior PASS) →
  **REVISED -007** (Claude/B; restored clause-scope tokens + corrected the inaccurate C
  invocation_surfaces snippet; both preflights PASS). Awaiting Codex VERIFIED.
- **Commit HELD (owner AUQ, S379):** `git commit` of the regen is blocked by the
  inventory-drift pre-commit gate (`scripts/check_dev_environment_inventory_drift.py`,
  L226 `material_inventory_drift` blocks unconditionally; bridge evidence does NOT
  bypass it). The regen'd `harness-registry.json` drifts the `harnesses` key from
  the stale baseline `.groundtruth/inventory/dev-environment-inventory.json` —
  **ANOTHER stale harness-state mirror.** Gate reads LIVE state, so it blocks ALL
  commits until the baseline matches (excluding the projection from the commit
  doesn't help). Updating the baseline is OUTSIDE -007's GO'd target_paths +
  overlaps `gtkb-harness-registry-parity-sweep`. Owner chose **HOLD**: nothing
  committed (HEAD still `e01f5695`) or pushed; regen + bridge audit (-001..-007)
  intact uncommitted on disk. Clean resolution = parity-sweep thread or a
  scope-expansion REVISED that includes the inventory baseline. Candidate WI:
  inventory-baseline harness-state staleness (3rd stale mirror after
  harness-registry.json [fixed] + role-assignments.json).
  Verification (all 4 GO conditions PASS): DB↔projection match (A/B/C); resolver
  prime-builder→B, loyal-opposition→A; `test_single_prime_fallback` HEALED; suite
  9→8 failed / 71→72 passed (0 new regressions). Projection C row: active/PB →
  registered/[] (matches DB).
- **PREMISE CORRECTION (Codex NO-GO -002):** the DB (`gt harness list`) is
  authoritative and ALREADY correct — A=active/LO, B=active/PB, **C=registered/role=[]**
  (v2, 2026-05-19 "clear registered Antigravity C role during LO bootstrap"). The
  dual-active-PB was ONLY in the STALE projection `harness-state/harness-registry.json`
  (gen 2026-05-31T14:33, C=active/PB) + stale `role-assignments.json` (2026-05-31
  "C as PB while Claude offline"; conditional, now moot). I read the cached
  projection at session start instead of the DB (GOV-SOURCE-OF-TRUTH-FRESHNESS-001
  lesson). NO suspend / NO role drop / NO DB mutation needed.
- **Fix (-003):** `python -m groundtruth_kb.harness_projection` regenerates the
  projection from the DB → C=registered/role=[] → resolver resolves prime-builder→B
  (no multi-active raise); `test_single_prime_fallback_resolves_to_claude` heals.
  Read-only `build_projection` preview confirms the target state. target_paths =
  `harness-state/harness-registry.json` + bridge + INDEX (no groundtruth.db).
- Commit type: `chore` (projection regen, no code).
- **AUQ-2 (suspend) superseded** by the corrected premise — flagged to owner.
- **Bridge-integrity note:** the landing-reconciliation INDEX entry VANISHED
  (parallel-session INDEX rewrite; INDEX is 1171 lines, heavily contended).
  Restored full chain (NEW -001 / NO-GO -002 / REVISED -003) at INDEX top. Files
  were intact on disk (append-only).
- `harness-state/role-assignments.json` also stale (off resolver read path; broader
  parity = `gtkb-harness-registry-parity-sweep` thread). WI-3512 unaffected.

Prerequisites (all created S379, attribution `prime-builder/claude` via
`GTKB_HARNESS_NAME=claude` env — dual-PB state blocks priority-3 resolution):
- Project: `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH` (rowid 187).
- Work item: `WI-3509` (P1, origin new, component cross-harness-dispatch).
- Membership: `PWM-PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH-WI-3509`.
- PAUTH (active, includes WI-3509):
  `PAUTH-PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH-ROLE-STATUS-ORTHOGONALITY-DISPATCH-SLICE-2-RESOLVER-ATTRIBUTION`.

Proposal: `bridge/gtkb-role-status-orthogonality-dispatch-slice-2-resolver-001.md`
(NEW). Both preflights PASS (applicability `preflight_passed: true`; clause
EXIT 0). `target_paths` machine-line authorizes: `scripts/cross_harness_bridge_trigger.py`,
`scripts/_kb_attribution.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`,
`platform_tests/scripts/test_kb_attribution.py`, the bridge thread glob, `bridge/INDEX.md`.

Implements DCL assertions 1-7, 10, 11 (8-9 = Slice 6 doctor; the doctor half of
6 = Slice 6, resolver half = here).

### Design (precise)

- `_resolve_dispatch_target(role, project_root, state_dir=None) -> DispatchTarget | None`:
  filter `(role AND status=="active")`; 0-active → emit `no_active_target_for_role`
  audit + return None; 2+-active → `ValueError` naming IDs; 1 → dispatch.
  missing/unknown status → inactive (fail-closed). `_record_has_role` extended so
  `acting-prime-builder` matches `prime-builder` (assertion 11). Records already
  carry `status` (read via `_read_role_assignments` → `harness-registry.json`,
  WI-3342 IP-4).
- `_is_single_harness_topology`: also require `status=="active"` (assertion 7).
- Caller in `run()`: pass `state_dir`; 5-tuple with failure_reason; set
  `last_result` for None cases.
- `_kb_attribution.py`: rename `_sole_prime_builder_harness_name` →
  `_active_prime_builder_harness_name`; docstring/framing only — active-filter is
  already upstream in `load_role_assignments` (filters `status=="active"`, strips
  status). NON-functional change.

### Pre-existing test baseline (NOT introduced by Slice 2) — 9 failures

- `test_governing_specs_preserved.py`: 7 (stale `_write_harness_state` writes
  `role-assignments.json`, not `harness-registry.json`; WI-3342 migration fallout).
- `test_cross_harness_bridge_trigger.py`: 1 (`test_harness_command_builds_argv_from_invocation_surfaces`,
  `--permission-mode` mismatch, unrelated).
- `test_kb_attribution.py`: 1 (`test_single_prime_fallback_resolves_to_claude`,
  live dual-PB → RuntimeError; self-heals after registry reconciliation).

### Coordination caveat (LANDING AUQ — do at Slice 2 VERIFIED, not before)

Live `harness-state/harness-registry.json`: B (claude) AND C (antigravity) BOTH
`prime-builder`/`status=active`. Resolver will correctly raise multi-ACTIVE for
`prime-builder` UNTIL registry reconciled (C → inactive). Do NOT silently flip C.
Surface AskUserQuestion at Slice 2 landing asking owner to reconcile.

### Scope decisions (documented in proposal)

1. 9 pre-existing failures NOT fixed here (GOV-07/GOV-15); capture as follow-on WI.
2. Assertion 7 = the named `_is_single_harness_topology` only; the single-harness
   dispatcher's `_is_single_harness_topology_applicable` (delegates to
   `groundtruth_kb.mode_switch.derive.topology_from_role_map`) is a noted follow-on.

### Next steps

1. Await Codex GO on `-001` (PB-side auto-dispatch is broken by dual-PB, so the
   GO will surface via AXIS-2 on next prompt rather than spawning a headless Claude).
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-role-status-orthogonality-dispatch-slice-2-resolver`.
3. Implement + tests; run pytest + `ruff check` + `ruff format --check` on the 4 files.
4. File post-impl report (next version) with spec-to-test mapping + baseline delta.
5. Codex VERIFIED.
6. Landing AUQ: registry reconciliation (C → inactive).
7. Follow-on WI: 9 pre-existing failures; dispatcher-gate status-awareness.
