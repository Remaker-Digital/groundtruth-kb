# OpenRouter/F Headless Dispatch Incident - 2026-07-07

## Claim

OpenRouter/F is correctly selected as the Loyal Opposition default dispatch target and can launch headlessly, but it cannot yet be trusted for regular unattended LO processing. Two controlled launches stalled silently with empty stdout/stderr and no exit-code sidecar; the second reproduced after adding an explicit `--timeout 60` to the OpenRouter/F headless invocation surface.

## Evidence

- Dispatcher topology: `gt bridge dispatch status --json` selects `loyal-opposition:F` and `prime-builder:A`; routing health was PASS after transient reset.
- Canonical LO-actionable repair proposals:
  - `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-001.md`
  - `bridge/gtkb-wi5065-codex-live-sandbox-readiness-001.md`
  - `bridge/gtkb-wi5066-openrouter-silent-stall-timeout-001.md`
- First controlled OpenRouter/F launch: `2026-07-07T20-33-28Z-loyal-opposition-F-25e69c`, selected `gtkb-wi5065-codex-live-sandbox-readiness`, stalled beyond the prior implicit 240-second request timeout with no stdout, no stderr, no exit-code sidecar, no CPU activity, and no observed TCP socket.
- Local no-token wrapper probes under `.gtkb-state/openrouter-local-probes/20260707T2044Z/` showed the basic status-wrapper envelope works:
  - `help.exit_code=0`, stdout captured.
  - `missing-key.exit_code=1`, stderr captured.
  - `closed-endpoint.exit_code=1`, stderr captured.
- Governed config transaction changed OpenRouter/F headless argv to include `--timeout 60`.
- Second controlled OpenRouter/F launch: `2026-07-07T20-46-50Z-loyal-opposition-F-9a0522`, selected `gtkb-wi5066-openrouter-silent-stall-timeout`, still stalled beyond 60 seconds with empty stdout/stderr and no exit-code sidecar.
- The second process tree showed nested `pythonw.exe` wrapper/shim processes and duplicate OpenRouter shim children, with no observed TCP socket.
- Both stalled runs required `gt bridge dispatch drain --timeout 10 --json` followed by `gt bridge dispatch reset --soft --json` to clear stale runtime state and document leases.
- Direct tiny OpenRouter bridge-review smoke succeeded outside dispatcher wrapping: `OPENROUTER_SMOKE_OK` in about 2.15 seconds.
- Direct tiny OpenRouter smoke through `run_with_status.py` plus `pythonw.exe` no-window wrapping succeeded: exit-code sidecar `0` and stdout `OPENROUTER_WRAPPER_OK` in about 2.06 seconds.
- Bounded real dispatcher launch `2026-07-07T20-55-13Z-loyal-opposition-F-2e0e6d` selected `gtkb-wi5066-openrouter-silent-stall-timeout`, used `GTKB_WORKER_LIFETIME_HARNESS_F_SECONDS=900`, and exited cleanly with exit code `1`; stderr captured `OpenRouter rate limited (HTTP 429 provider backpressure) after 3 attempt(s); retry_after_seconds=1`.
- Dispatcher health then suppressed `loyal-opposition:F` with `provider_failure_backoff_active`, while the active monitor counted the zero-stdout provider-rate-limit run as `corrupt_output` and placed the LO lane on hold.
- A direct tiny smoke using explicit route `--model deepseek-v4-flash` succeeded: `OPENROUTER_FLASH_OK` in about 2.49 seconds.
- Governed harness transaction updated OpenRouter/F headless argv to include `--model deepseek-v4-flash`; harness F version `37`.

## Risk / Impact

OpenRouter/F can be routed and spawned, and its basic no-window wrapper envelope is working. It is still not currently reliable enough for regular unattended LO processing because real bridge-review dispatch now fails under provider backpressure and the monitoring layer converts the clean provider-rate-limit exit into a lane-stopping `corrupt_output` hold.

Codex/A remains selected for Prime Builder but intentionally suppressed by `codex_dispatch_not_ready` because the live no-window shell smoke still fails with Windows sandbox setup `0xc0000142` and visible-window evidence.

## Recommended Action

1. Test the explicit `deepseek-v4-flash` route with one bounded real OpenRouter/F dispatch after preserving the provider-rate-limit evidence and clearing transient hold state.
2. Get LO review/GO for `gtkb-wi5066-openrouter-silent-stall-timeout` and implement the bounded timeout/stale-runtime hardening.
3. Get LO review/GO for `gtkb-wi5064-openrouter-ssl-retry-hardening` and implement transport retry/classification.
4. Add or fold a provider-rate-limit monitor-classification repair into the OpenRouter reliability proposal set so HTTP 429 provider backpressure does not masquerade as corrupt output.
5. Get LO review/GO for `gtkb-wi5065-codex-live-sandbox-readiness` and repair Codex/A live no-window readiness.

## Decision Needed From Owner

Choose the LO reviewer path for the repair proposals: spend limited Antigravity capacity, authorize a separate Codex LO context, wait for Claude/Ollama capacity, or accept another controlled OpenRouter/F attempt after WI-5066 scope changes.
