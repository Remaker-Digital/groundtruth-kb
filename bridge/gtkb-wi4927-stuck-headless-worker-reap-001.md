NEW

# Cross-harness stuck headless dispatch worker detection and reap (desktop-hosted agents)

bridge_kind: prime_proposal
Document: gtkb-wi4927-stuck-headless-worker-reap
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-30 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-30T01-00-00Z-prime-builder-E-s514
author_model: composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive; ::init gtkb pb; cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4927-STUCK-HEADLESS-WORKER-REAP
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4927

target_paths: ["scripts/dispatcher_runtime.py", "scripts/cursor_harness.py", "scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py", "platform_tests/scripts/test_harness_storm_watchdog.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source, tests, dispatcher-runtime, storm-watchdog
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-confirmed S514 evidence: two stuck Cursor headless agent sessions remained inside the Cursor IDE process tree after dispatch completed, consuming CPU and RAM until manual exit. WI-4857 (VERIFIED) reaps orphaned workers via `dispatch-runs` `.pid` / `.exit_code` sidecars at daemon startup/shutdown; WI-4845 bounds worker lifetime through `run_with_status.py`; WI-4894 repaired storm-watchdog decider output. The remaining gap is **desktop-hosted agent children** that outlive the shim PID the dispatcher tracks — especially Cursor harness E, where `cursor_harness.py` uses `subprocess.run(agent ...)` and the long-lived `agent` process may attach under `Cursor.exe` rather than the python shim recorded in sidecars.

This proposal authorizes a bounded slice to:

1. **Inventory** spawn argv, tracked PID, and Windows process-tree semantics for each headless dispatch harness (A–F).
2. **Detect** stuck headless workers when sidecars say complete but desktop-hosted agents persist, or when lease progress stalls beyond lifetime with no exit_code.
3. **Reap** safely with provenance gating — preserve WI-4828 interactive-session safety (never reap owner interactive Codex/Cursor sessions).
4. **Test** with Cursor agent orphan simulation plus at least one non-Cursor harness path.

Explicitly **out of scope**: reducing Cursor IDE idle baseline RAM (~2.3 GB structural cost); that is product architecture, not dispatch orphan reap.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected dispatcher/storm-watchdog scripts require bridge GO before mutation.
- `GOV-17` — automation script modification approval gate; this slice modifies dispatcher health and storm-watchdog automation.
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher owns worker lifecycle; orphaned headless agents violate operability contract.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — centralized dispatch must not leak stuck workers across harness topologies.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal carries WI/project/PAUTH and target_paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable linkage block present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification table below is the LO review contract.
- `GOV-STANDING-BACKLOG-001` — WI-4927 is the governing backlog item.
- `GOV-AUTOMATION-VALUE-VS-COST-001` — stuck workers waste CPU/RAM and block re-dispatch; detection must be low-noise.

## Prior Deliberations

- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` — harden-first posture for Claude and Cursor headless collaboration; PAUTH owner-decision evidence for WI-4927 authorization.
- `DELIB-20266104` — WI-4670 storm remediation surgical watchdog liveness-awareness (WI-4828 safety boundary).
- `DELIB-20266203` — Phase X daemon fix-chain owner authorization context (WI-4857 reap slice).
- `bridge/gtkb-wi4857-reap-orphaned-dispatched-workers-004.md` — VERIFIED sidecar-based reap; defines what this slice extends.
- `bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-003.md` — VERIFIED cursor_harness.py in storm-watchdog NONCODEX list; insufficient for desktop `agent` children.

## Owner Decisions / Input

Implementation authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4927-STUCK-HEADLESS-WORKER-REAP` (minted 2026-06-30; includes WI-4927, WI-4857, WI-4845, WI-4894; cites `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626`). Owner reply **Proceed** (S514) authorized filing this proposal after manual cleanup of two stuck Cursor headless sessions confirmed the defect class. No additional owner decision is required before Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. WI-4927 acceptance criteria (inventory, detection, reap, regression tests) plus the cited PAUTH scope and prior reap/watchdog slices define the implementation boundary. No new SPEC/GOV/ADR required before implementation.

## Proposed Scope (phased within one implementation report)

### Phase A — Cursor desktop-hosted orphan path (primary defect)

- Extend `cursor_harness.py` to record dispatch correlation metadata (dispatch_id + agent child PID or process-tree snapshot) in `dispatch-runs` or a sibling provenance file when spawned under dispatcher control.
- Extend `storm_watchdog_reap.py` / `harness_storm_watchdog.ps1` process gather to classify standalone `agent` / `cursor-agent` processes that correlate to completed dispatch sidecars but remain alive beyond grace/lifetime as reap candidates.
- Preserve WI-4828: processes without dispatched-root provenance or matching interactive Cursor owner sessions are never reaped.

### Phase B — Cross-harness inventory docstring + health surface

- Add `dispatcher_runtime.list_stuck_headless_workers()` (or extend existing health JSON) returning per-harness stuck-worker counts for doctor/`gt bridge dispatch health` consumers.
- Document spawn/tree semantics inline for Codex, Claude, Antigravity, Ollama, OpenRouter harness entrypoints (comments + health output fields only; no behavior change where sidecar reap already suffices).

### Phase C — Regression tests

- `test_cursor_harness_records_agent_child_provenance` — simulated dispatch records child PID metadata.
- `test_storm_watchdog_reap_desktop_agent_orphan` — completed sidecar + live agent child => reap decision.
- `test_storm_watchdog_reap_skips_interactive_cursor` — interactive session fixture => no reap.
- Non-regression: existing `test_storm_watchdog_reap.py`, `test_harness_storm_watchdog.py`, `test_gtkb_dispatcher_daemon.py` suites PASS.

## Specification-Derived Verification Plan

| Spec / clause | Test / command | Expected result |
|---|---|---|
| WI-4927: detect desktop-hosted orphan | `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short -k desktop_agent` | Orphan agent with completed dispatch sidecar is selected for reap; interactive Cursor fixture skipped. |
| WI-4927: Cursor provenance recording | `python -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short -k provenance` | Harness writes dispatch correlation metadata under dispatcher-controlled spawn. |
| ADR-DISPATCHER-ARCHITECTURE-001 | `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` | Daemon startup/shutdown reap non-regression; health surface exposes stuck-worker count when present. |
| WI-4828 safety boundary | `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short -k interactive` | Interactive codex/cursor processes never selected for reap. |
| GOV-17 automation gate | `python -m ruff check scripts/dispatcher_runtime.py scripts/cursor_harness.py scripts/ops/storm_watchdog_reap.py` | Clean. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Implementation report quotes exact pytest/ruff outputs above. | LO can verify without re-running exploratory diagnostics. |

```text
python -m ruff format --check scripts/dispatcher_runtime.py scripts/cursor_harness.py scripts/ops/storm_watchdog_reap.py scripts/ops/harness_storm_watchdog.ps1
python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py platform_tests/scripts/test_harness_storm_watchdog.py platform_tests/scripts/test_cursor_harness.py -q --tb=short
```

## Risks / Rollback

- **Risk:** reaping a legitimate long-running interactive Cursor agent session. **Mitigation:** WI-4828 dispatched-root + lease + provenance gates; add explicit interactive-session detector for `agent` argv patterns tied to owner workspace without dispatch_id sidecar.
- **Risk:** false positives on healthy in-flight dispatches. **Mitigation:** reuse lease registry + max_lifetime from `storm_watchdog_reap.py`; only reap when exit_code sidecar is present (dispatch complete) but agent child remains.
- **Risk:** Windows process-tree enumeration cost. **Mitigation:** run only inside existing storm-watchdog cadence and dispatcher health on-demand paths.
- **Rollback:** single-commit revert removes provenance recording and extended reap classification; sidecar-based WI-4857 behavior unchanged.

## Recommended Commit Type

`fix` — repairs cross-harness stuck headless worker leakage discovered in production Cursor dispatch topology; extends existing reap/watchdog machinery rather than introducing a parallel runtime.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
