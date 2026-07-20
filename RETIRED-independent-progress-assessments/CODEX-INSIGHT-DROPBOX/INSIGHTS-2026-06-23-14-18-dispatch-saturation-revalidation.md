Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001
WIs: WI-4670, WI-4739, WI-4770, WI-4760, WI-4757

# LO Dispatch Saturation Revalidation

Generated: 2026-06-23 14:18 UTC
Reviewer: Codex Loyal Opposition automation, harness A
Work mode: Read-only fallback investigation of dispatch-health failure. This report does not assert a harness-identity review blocker; authoritative GT-KB review independence is session-context based.

## Claim

Live bridge dispatch remains operationally failed, but the observed failure modes are already covered by existing backlog work rather than needing a duplicate hygiene item. Direct bridge scanning works. During the 14:18 UTC revalidation, the headless LO dispatch lane was saturated by live long-running wrapper processes and rejected new work with `per_role_concurrency_cap_reached`; after the required 10-minute idle wait, dispatch health still failed but the live health surface reported LO `launch_failed` / `unchanged` states instead of the cap-saturation tail.

## Evidence

- Live LO bridge scan returned eight `NEW`/`REVISED` leaves: `agent-red-wi3193-intent-categories-diagram`, `agent-red-wi3194-knowledge-retrieval-technical-detail`, `gtkb-bridge-compliance-gate-test-hygiene-pending-scan-hang-fix`, `gtkb-bridge-gate-detectors-magic-content-phrases`, `gtkb-perrole-concurrency-cap-dispatch`, `gtkb-reconcile-included-work-item-ids-semantics`, `gtkb-wi4692-application-subject-dispatch-drain-suspend`, and `gtkb-wi4767-dispatch-config-file-edit-guard`.
- Author metadata on those latest leaves was inspected for session-context review independence. Matching harness identity alone is not a review blocker under the authoritative bridge rules.
- `python -m groundtruth_kb.cli bridge dispatch health --json` returned `health_status: FAIL`. Findings included LO failures for C/D/F and Prime Builder subprocess failures for A/B.
- `python -m groundtruth_kb.cli bridge dispatch status --json` selected active LO targets F, D, and C from `E:\GT-KB\config\dispatcher\rules.toml`, so the failure is runtime delivery, not missing dispatcher topology.
- `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-failures.jsonl` tail repeatedly records `per_role_concurrency_cap_reached` with `per_role_cap: 8` and `per_role_live: 8` for `loyal-opposition:C` and `loyal-opposition:D`.
- Recent in-root runtime logs show provider/tool failures still present:
  - `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-runs\2026-06-23T14-09-12Z-loyal-opposition-C-bbecd2.stderr.log` reports Gemini CLI `IneligibleTierError` and directs migration to Antigravity.
  - `E:\GT-KB\.gtkb-state\bridge-poller\dispatch-runs\2026-06-23T14-05-41Z-loyal-opposition-D-75792f.stderr.log` reports `ollama_harness: Ollama chat request failed: HTTP Error 502: Bad Gateway`.
- A live process census found eight recent dispatch wrapper PID files still alive, matching the cap symptom: D pids `27492`, `35316`, `42524`, `36140`; F pids `33448`, `45660`, `41436`, `34360`.
- `E:\GT-KB\scripts\run_with_status.py` starts the child process with `subprocess.Popen(...)` and then calls bare `p.wait()` with no worker lifetime timeout, matching the current `WI-4670` status-detail note about immortal hung workers saturating the per-role cap.
- Environment kill-switch check returned blank at process, User, and Machine scope for `GTKB_NO_CROSS_HARNESS_TRIGGER`; this run did not reproduce `WI-4760`'s silent kill-switch mode.
- Post-wait recheck at 2026-06-23 14:34 UTC found nine LO-actionable leaves. `python -m groundtruth_kb.cli bridge dispatch health --json` still returned `health_status: FAIL`, now with `loyal-opposition` and `loyal-opposition:C/F` `launch_failed` findings plus `loyal-opposition:D` `unchanged`.

## Finding P0-001: LO dispatch is saturated by live long-running worker wrappers

### Observation

The 14:18 UTC failure stream was no longer just individual provider errors. It showed repeated launch denial because the LO lane saw eight live dispatched processes. The process census confirmed those PIDs were alive, and the active dispatcher wrapper has no maximum lifetime around the child process. The post-wait health surface remained red, which means the immediate symptom shifted but the dispatch lane was still not delivering LO verdict work.

### Deficiency Rationale

When the dispatcher counts all eight wrappers as live, no additional LO dispatch can start. That strands actionable `NEW`/`REVISED` bridge work even though direct bridge scanning remains available. Provider-specific fixes for Gemini, Ollama, or OpenRouter will not be enough if a worker can remain alive indefinitely and consume the role cap.

### Proposed Solution / Enhancement

Implement `WI-4670` with the worker-lifetime timeout as a first-class acceptance condition. The minimal-risk path is:

1. Add a configurable maximum runtime to `scripts/run_with_status.py` or to the caller's wrapper contract.
2. On timeout, terminate the child process tree, write a non-zero exit code, and include a structured timeout reason in stderr or a sidecar status field.
3. Teach dispatch health to distinguish provider failure, wrapper timeout, spawn-rate limit, and per-role-cap saturation.
4. Add regression coverage that launches a deliberately hanging worker and proves the cap is released after timeout.

### Option Rationale

Terminating known live PIDs would clear the immediate queue but would not fix the recurrence. Disabling C/D/F would reduce noise but leave the same wrapper-lifetime defect for any future headless target. A bounded wrapper lifetime is the smallest reusable control that prevents hung workers from becoming permanent capacity loss.

## Duplicate / Precedence Check

No new hygiene work item was added. `WI-4670` already names the current cross-cutting defect: `run_with_status.py` uses bare `p.wait()` with no worker-lifetime timeout, allowing hung workers to saturate the per-role cap. Related rows remain distinct:

- `WI-4739`: multi-LO same-version verdict races.
- `WI-4770`: Prime Builder per-item authorization quarantine.
- `WI-4760`: persistent kill-switch visibility.
- `WI-4757`: git-status permission warnings for temp dirs.

## Prime Builder Implementation Context

| Element | Detail |
|---|---|
| Objective | Make headless LO dispatch recover from hung workers, failed launches, and provider failures while exposing precise runtime failure classes. |
| Preconditions | Treat `WI-4670` as the owning P0 item; do not create a duplicate hygiene item for per-role-cap saturation. |
| Evidence paths | `scripts/run_with_status.py`; `.gtkb-state/bridge-poller/dispatch-failures.jsonl`; `.gtkb-state/bridge-poller/dispatch-runs/*loyal-opposition*.{pid,stderr.log,exit_code}`. |
| File touchpoints | Likely `scripts/run_with_status.py`, `scripts/cross_harness_bridge_trigger.py`, and focused tests under `platform_tests/scripts/`. |
| Implementation sequence | Add timeout contract; terminate process tree on timeout; emit structured failure reason; update health classification; add focused regression tests. |
| Verification steps | Force a hanging worker, confirm exit/status file is written, confirm live process count drops, and confirm `gt bridge dispatch health --json` reports timeout or launch/provider failure precisely instead of silent cap saturation or generic launch failure. |
| Rollback notes | Wrapper timeout can be feature-flagged or defaulted conservatively; rollback restores prior wrapper behavior without changing bridge artifacts. |
| Open decisions | None surfaced by this LO pass. |

## Commands Executed

- `python .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
- `rg -n "^(Document:|Version:|Status:|Author:|Date:|Work Item:|author_harness_id:|author_session_context_id:|author_role:|author_harness:|session_context_id:)" <eight latest bridge files>`
- `python -m groundtruth_kb.cli backlog list --json`
- `python -m groundtruth_kb.cli backlog list --json --id WI-4670 --id WI-4739 --id WI-4770 --id WI-4760 --id WI-4757`
- `python -m groundtruth_kb.cli bridge dispatch config`
- `python -m groundtruth_kb.cli bridge dispatch status --json`
- `python -m groundtruth_kb.cli bridge dispatch health --json`
- `Get-Content .gtkb-state\bridge-poller\dispatch-failures.jsonl -Tail 40`
- `Get-ChildItem .gtkb-state\bridge-poller\dispatch-runs -File | Sort-Object LastWriteTime -Descending | Select-Object -First 40`
- `Get-CimInstance Win32_Process ...`
- `rg -n "wait\(|timeout|Popen|subprocess" scripts/run_with_status.py scripts/cross_harness_bridge_trigger.py scripts/ollama_harness.py scripts/openrouter_harness.py`

## Owner Decision Needed

None. This report preserves live evidence and recommends executing the existing P0 work item.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
