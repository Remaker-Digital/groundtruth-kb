NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# gtkb-wi4856-daemon-status-liveness-accurate — Post-implementation report: liveness-accurate daemon status + substrate-derived mode

Document: gtkb-wi4856-daemon-status-liveness-accurate
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4856
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4856-LIVENESS-ACCURATE-STATUS
Responds to: bridge/gtkb-wi4856-daemon-status-liveness-accurate-002.md (GO)
Recommended commit type: fix

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (`-002`) liveness-accurate daemon status fix. `collect_daemon_status` now derives `running` from process liveness + heartbeat freshness (not lock presence alone) and derives `mode`/`active_substrate` from the active substrate selection (not a hardcoded `"shadow"`), reusing the daemon's own `daemon_process_alive`, `_active_substrate`, and heartbeat-age helpers.

## Implemented Changes

`scripts/gtkb_dispatcher_daemon.py`:
- Added module constant `HEARTBEAT_STALE_DEFAULT_SECONDS = 180` + env var `GTKB_DISPATCHER_DAEMON_HEARTBEAT_STALE_SECONDS`, and helper `_heartbeat_stale_seconds()` (env-overridable, fail-soft to default).
- `collect_daemon_status`: `mode = "live" if active_substrate == DAEMON_SUBSTRATE else "shadow"` with `active_substrate` added to the payload (mirrors `run_tick`); `running = pid_alive or (lock_present and heartbeat_fresh)` where `pid_alive = daemon_process_alive(state_dir)` and `heartbeat_fresh = heartbeat_age is not None and heartbeat_age <= _heartbeat_stale_seconds()`. The `lock` payload and `heartbeat_age_seconds` remain for diagnostics.

`groundtruth-kb/src/groundtruth_kb/cli.py`:
- `bridge_dispatch_daemon_status_cmd`: added one human-readable line `Active substrate: {payload.get('active_substrate')}` after the (already-present, now-correct) mode line. The `--json` path already surfaces the full payload.

`platform_tests/scripts/test_gtkb_dispatcher_daemon.py`:
- Added 5 spec-derived tests (stale-lock-dead-daemon / live-PID / lock+fresh-heartbeat / mode-live / mode-shadow).

## Specification Links

Carried forward from `-001`:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-17` — Automation script modification approval gate; modifies the daemon automation script + CLI surface; owner-authorized (DELIB-20266203, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — daemon operability contract (status accuracy).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs cited; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4856 + project + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — behavior maps to derived tests, executed below.
- `GOV-STANDING-BACKLOG-001` — WI-4856 authorized standing-backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| WI-4856(1): stale lock + dead daemon does not report running | `test_status_running_false_on_stale_lock_dead_daemon` | PASS |
| WI-4856(1): live PID reports running | `test_status_running_true_when_pid_alive` | PASS |
| WI-4856(1): lock + fresh heartbeat reports running (no PID file) | `test_status_running_true_when_lock_and_heartbeat_fresh` | PASS |
| WI-4856(2): mode=live + active_substrate when substrate=dispatcher_daemon | `test_status_mode_live_when_substrate_daemon` | PASS |
| WI-4856(2): mode=shadow when substrate=cross_harness_trigger | `test_status_mode_shadow_when_substrate_cross_harness` | PASS |
| Non-regression: clean-stop reports not-running | existing `test_..._stop...` (lock released) | PASS |
| Non-regression: CLI status default mode | existing `test_daemon_control_cli_status_reports_state` | PASS |

## Verification Evidence

Repo venv `groundtruth-kb/.venv/Scripts/python.exe`:
- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q` → `26 passed in 4.72s` (21 existing + 5 new).
- `python -m ruff check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py` → `All checks passed!`.
- `python -m ruff format --check` on all 3 changed files → `3 files already formatted`.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py` reports 2 pre-existing `E501` violations at the ChromaDB error messages (~lines 6223/6661), confirmed present in committed `HEAD` (`git show HEAD:...cli.py | ruff check --select E501 -` → 2 errors). These predate WI-4856 and are out of scope; the WI-4856 one-line `cli.py` edit introduces no new violations.
- Live smoke: `gt bridge dispatch daemon status` on the live tree → `mode: shadow`, `Active substrate: cross_harness_trigger`, `Running: False` despite a ~25,230s-old (stale) heartbeat. Pre-fix, this stale-lock state reported `Running: True`; the fix correctly reports `False`.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement (WI-4856 acceptance) is that daemon status report `running` from heartbeat freshness / process liveness rather than lock presence alone, and that mode / active substrate derive from the active substrate selection. DELIB-20266203 Q2 authorizes the fix. No new requirement.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4856-LIVENESS-ACCURATE-STATUS` (active; includes WI-4856 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266203`). The owner approved the full Phase X daemon fix-chain (DELIB-20266203 Q2), of which WI-4856 is step X4. No additional owner decision is required for this report.

## Prior Deliberations

- `DELIB-20266203` — owner grilled plan; Q2 authorizes the full daemon fix-chain including WI-4856 (X4).
- `bridge/gtkb-wi4856-daemon-status-liveness-accurate-001.md` (NEW proposal), `-002.md` (Cursor LO GO).
- WI-4855 — provided the `daemon_process_alive` / `_pid_is_running` liveness primitives reused here.

## Risk / Rollback

- A freshly-crashed daemon (stale lock + dead PID + heartbeat within `HEARTBEAT_STALE_SECONDS`) reports `running=True` transiently until the heartbeat ages out (≤180s). Acceptable per the GO; self-clears. Prior behavior reported `running=True` indefinitely off a stale lock.
- `start`'s single-instance guard now treats a stale-lock-only state as not-running, so restart-after-crash is no longer blocked by a stale lock (improvement, consistent with WI-4855).
- Rollback: single-commit revert restores lock-presence `running` and hardcoded `mode`. No KB mutation.

## Recommended Commit Type

`fix` — repairs stale daemon-status reporting; reuses existing liveness/substrate helpers. No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
