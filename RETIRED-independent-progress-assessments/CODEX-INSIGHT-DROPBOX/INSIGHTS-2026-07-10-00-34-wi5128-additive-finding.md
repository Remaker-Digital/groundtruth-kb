author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T00-17-29Z-loyal-opposition-B-92de58
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition

# Loyal Opposition Advisory — Additive finding for WI-5128 startup-relay REVISED

Specs: SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001, GOV-FILE-BRIDGE-AUTHORITY-001, ADR-CODEX-HOOK-PARITY-FALLBACK-001
WIs: WI-5128
Thread: bridge/gtkb-wi5128-startup-relay-cache-refresh (latest: -002 NO-GO)
Date: 2026-07-10 UTC

## Why this report exists (concurrence + stand-down)

The dispatcher fanned the same `-001` NEW to two Loyal Opposition sessions. An
independent interactive LO session (session `bacf82bb-dbf0-45d5-b833-8b0862487e78`)
filed **NO-GO at `-002`** while this headless session was still investigating.
I **concur with that NO-GO** and stand down rather than stack a competing `-003`
verdict — the thread is already Prime-actionable. The `-002` findings (boilerplate
verification plan; spec over-linking) are correct and sufficient to move the thread
forward.

This report preserves **one material finding the `-002` verdict did not surface**,
because acting on `-002` as written risks a duplicate-test, near-no-op REVISED that
leaves the owner's actual incident unfixed.

## Finding [P1] — Acceptance criteria are already satisfied by committed tests; the real residual defect is uncharacterized

- **Claim.** The bounded startup-relay refresh WI-5128 proposes to "restore"
  already ships in committed code, and both of the proposal's acceptance criteria
  are already covered by existing committed regression tests. The `-002` verdict's
  "required correction" asks Codex to add a test that a stale-but-integrity-valid
  cache "is refreshed within the bounded hook budget" — but that test already
  exists. Following `-002` literally would produce a duplicate test.
- **Evidence.**
  - Bounded refresh already shipped: `_refresh_startup_relay_cache_bounded`
    (`scripts/workstream_focus.py:1605`) and the refresh-then-revalidate branch in
    `_startup_relay_pointer` (`scripts/workstream_focus.py:1727`); 2.0s budget at
    `scripts/workstream_focus.py:114`. `git log -S "_refresh_startup_relay_cache_bounded"`
    attributes the symbol to committed commit `8de3bcf6` ("WI-4738 bounded startup
    relay refresh timeout"). All four `target_paths` are clean in `git status` —
    committed canonical state.
  - Acceptance criterion 1 (recover a stale integrity-valid cache within the
    bounded refresh) is already tested by
    `platform_tests/hooks/test_workstream_focus.py:1674`
    (`test_startup_gate_self_heals_freshness_stale_cache`).
  - Acceptance criterion 2 (bounded / fail-visibly on timeout) is already tested by
    `platform_tests/hooks/test_workstream_focus.py:1762`
    (`test_startup_gate_refresh_timeout_fails_visibly_without_late_cache_write`).
  - The **actual** defect exists only in the cited owner decision
    `DELIB-202665935`, not in the proposal's problem framing: the Codex PB cache
    and sidecar had matching hashes but a `generated_at` outside the freshness
    window, and the bounded refresh **did not complete**, so the relay failed
    closed via `_startup_relay_failure_context` (`scripts/workstream_focus.py:1836`).
    The proposal cites this DELIB only as authorization evidence; its Summary /
    Proposed Scope / Acceptance Criteria never name the observed failure or explain
    why the current committed refresh-then-revalidate path is insufficient for it.
- **Impact.** A REVISED that only fixes the verification plan (per `-002`) but does
  not characterize the residual defect will either (a) add a test duplicating
  `test_startup_gate_self_heals_freshness_stale_cache`, or (b) implement a no-op
  against acceptance criteria that already pass — consuming a full bridge cycle and
  a commit while the owner's 2026-07-09 incident stays unfixed. At verification, an
  LO cannot distinguish "fixed" from "already worked," forcing a later NO-GO.
- **Recommended action for the REVISED.** Beyond the `-002` corrections, the
  REVISED must add a concrete **Problem Statement** that (i) cites the
  `DELIB-202665935` observed failure, and (ii) chooses and justifies the fix layer:
  either make the 2.0s bounded refresh reliably complete for the Codex PB
  stale-but-integrity-valid case (budget vs. `_render_role_startup_report` cost), or
  improve the fail-closed branch so it yields a recoverable/diagnosable result
  without owner intervention. Then state the **net-new** behavior and **net-new**
  test that differ from the two existing tests above.
- **Owner decision needed.** No. Codex can revise autonomously; owner authorization
  (`DELIB-202665935` + active `PAUTH-...-STARTUP-RELAY-REPAIR`) is already on record.

## Prior deliberations (evidence that most of the described behavior already shipped)

- `DELIB-20264935` — GO: Startup Relay Cache TTL Self-Heal.
- `DELIB-20265679` — VERIFIED: WI-3460 Workstream-Focus Stale Relay Fixtures.
- `DELIB-20266279` — Owner: "Startup relay is degraded — how should I proceed" (the 2026-07-09 incident precursor).
- `DELIB-202665935` — Owner decision authorizing this derived repair.

## Disposition

Headless LO review target (`-001` NEW) is already dispositioned to NO-GO by an
independent LO session; no further bridge action from this session. This advisory
is additive context for whoever revises WI-5128.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
