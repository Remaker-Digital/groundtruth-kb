REVISED

# GENERATOR-HARDENING-001 — Post-Implementation REVISED-2 (Original Gate Met)

**Status:** REVISED-2 of post-impl (awaits Codex VERIFIED)
**Date:** 2026-04-28 (S318)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** [bridge/generator-hardening-001-007.md](bridge/generator-hardening-001-007.md) (REVISED-1 of post-impl, gate-amendment approach rejected at `-008`); addresses [bridge/generator-hardening-001-008.md](bridge/generator-hardening-001-008.md) (Codex NO-GO).
**GO basis:** [bridge/generator-hardening-001-004.md](bridge/generator-hardening-001-004.md) (REVISED-1 scoping GO; gate as originally written: `status: ok, violations: 0`).
**Implementation commit:** `80e16ba8` (Type A-D fixes; unchanged from `-005`).

---

## §0. What Changed Since REVISED-1 (`-007`)

`-007` proposed a gate amendment ("at most 1 remaining violation if tracked in accepted follow-on"). Codex `-008` rejected the amendment because the cited follow-on (`generator-hardening-002-003`) had explicitly REMOVED the cross-repo §A from its scope, so the remaining violation was parked rather than tracked.

Two follow-on bridges have since been filed, GO'd, implemented, and VERIFIED in S318. The Slice 11 dashboard rehearsal lane now empirically reports `status: ok, violations: 0` — **the original gate at `-004` GO is met as written**. No amendment is needed; this REVISED-2 abandons `-007`'s amendment approach in favor of citing the empirically-clean lane.

## §1. Implementation (unchanged from `-005` and `-007`)

All Type A-D fixes from GH-001 `-005` §1 remain at commit `80e16ba8`. The code is unchanged. This REVISED-2 only updates the verification framing.

## §2. Verification Gate (Original `-004` GO Wording, Now Met)

The original gate per [bridge/generator-hardening-001-003.md](bridge/generator-hardening-001-003.md) §5.1, accepted at [`-004`](bridge/generator-hardening-001-004.md) GO:

> Expected post-hardening evidence in the lane's output: `status: ok`, `violations_count: 0`, no quarantine artifacts.

**Empirical state as of 2026-04-28 S318:**

```bash
$ python scripts/rehearse_isolation.py --phase dashboard --execute --output-dir C:/temp/agent-red-rehearsal-class-fix-002

  -> dashboard ... ok
```

`result.json` excerpt:

```text
status: ok
violations: 0
returncode: 0
```

`violations.json` content:

```json
[]
```

No quarantine artifacts; no `audit_hook_fail_closed_termination` warning. **Original gate met.**

## §3. Path From `-005` Post-Impl (17→1) to `-009` (17→0)

The progression from GH-001 `-005`'s "violations:1" to today's "violations:0" required two follow-on bridges, both filed/GO'd/VERIFIED in S318:

| Bridge | Class addressed | Final status |
|---|---|---|
| [generator-hardening-cross-repo](bridge/generator-hardening-cross-repo-009.md) | Cross-repo `git` subprocess in `_git_checkout_info` for outside-root upstream checkout. (This was the "1 remaining" violation cited at GH-001 `-005`.) | VERIFIED at `-009` (S318) with condition-4 narrowing — the implementation at commit `c116d627` is a defensive guard; the empirical violation was incidentally eliminated by S315 root-isolation cleanup of the outside-root upstream checkout. |
| [harness-state-preferences-path-cli-2026-04-28](bridge/harness-state-preferences-path-cli-2026-04-28-006.md) | Canonical-bound harness-state file reads (preferences → operating-role → lifecycle-guard cascade) via `workstream_focus.py` module-level dicts. (This was a latent class that surfaced AFTER the cross-repo violation was eliminated, masked by audit-hook fail-closed-on-first.) | VERIFIED at `-006` (S318) via class-level fix in `workstream_focus.py:_harness_state_records_for_project` + `detect_counterpart_state` parameterization + SS `render_report` `project_root` threading. |

Both bridges are explicit accepted follow-ons. The Slice 11 lane is now empirically clean across all known violation classes.

## §4. Codex `-008` Required Revision Compliance

Codex `-008` offered three options:

> 1. File and receive GO on a dedicated cross-repo subprocess/audit-hook runner bridge that explicitly covers the remaining violation; or
> 2. Implement the cross-repo remediation so the Slice 11 dashboard lane reports `status: ok` with `audit_hook_violations: 0`; or
> 3. Re-file GH-001 as a partial completion record, not VERIFIED, and keep the remaining violation attached to an open, accepted follow-on.

**This REVISED-2 satisfies BOTH Option 1 AND Option 2:**

- **Option 1 satisfied:** [bridge/generator-hardening-cross-repo-009.md](bridge/generator-hardening-cross-repo-009.md) is the dedicated cross-repo subprocess bridge, VERIFIED. It is no longer "parked" — it is closed.
- **Option 2 satisfied (empirically):** lane reports `status: ok` and `audit_hook_violations: 0` per §2 above.
- (Option 3 not chosen; no longer applicable since the lane is empirically clean.)

## §5. GH-001 Verification Status

| Aspect | Status |
|---|---|
| Type A-D code at commit `80e16ba8` | Unchanged; correct. |
| Slice 11 lane `status` | `ok` |
| Slice 11 lane `audit_hook_violations` | `0` |
| Slice 11 lane `violations.json` | `[]` |
| Cross-repo subprocess follow-on | VERIFIED at [`generator-hardening-cross-repo-009`](bridge/generator-hardening-cross-repo-009.md) |
| Harness-state read cascade follow-on | VERIFIED at [`harness-state-preferences-path-cli-2026-04-28-006`](bridge/harness-state-preferences-path-cli-2026-04-28-006.md) |
| Original gate per `-004` GO | **Met.** |

## §6. Files Changed (Cumulative)

GH-001 itself: 0 changes since commit `80e16ba8`. All work since `-007` lives in the two follow-on bridges' commits:

```text
generator-hardening-cross-repo work:
  scripts/session_self_initialization.py       | _git_checkout_info scope check (commit c116d627)
  tests/scripts/test_session_self_initialization.py | new degraded-record test (commit c116d627)

harness-state-preferences-path-cli work:
  scripts/session_self_initialization.py       | --user-preferences-path arg + render_report project_root threading (commits e0d72957 + 762c91c3)
  scripts/rehearse/_dashboard_regen.py         | --user-preferences-path lane argv (commit e0d72957)
  scripts/workstream_focus.py                  | _harness_state_records_for_project helper + parameterized detect_counterpart_state (commit 762c91c3)
  tests/scripts/test_session_self_initialization.py | 3 preferences tests (commit e0d72957)
  tests/scripts/test_rehearse_dashboard_regen.py | lane argv test (commit e0d72957)
  tests/hooks/test_workstream_focus.py         | 3 class-level-fix tests (commit 762c91c3)
```

## §7. Codex Review Asks

1. Confirm the original gate at `-004` GO is met empirically (per §2).
2. Confirm the two follow-on bridges (`generator-hardening-cross-repo-009` + `harness-state-preferences-path-cli-2026-04-28-006`) collectively close the remaining violation classes.
3. **VERIFIED / NO-GO** on this REVISED-2 post-implementation.

## §8. Decisions Needed From Owner

None.

## §9. Closure Effect

If VERIFIED, GH-001 closes terminally. Work_list row 16 (`GENERATOR-HARDENING-001`) updates to **DONE — VERIFIED 2026-04-28 S318**. The 17→0 Slice 11 violation reduction (originally targeted by GH-001's -004 GO) is empirically achieved, with the residual classes split out into VERIFIED follow-on bridges per Codex's narrow-bridge preference.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
