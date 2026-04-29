# Bridge Proposal — GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger (2026-04-29)

**Status:** NEW (version 001 — design + implementation proposal)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (continuation, 2026-04-29)
**Document name:** `gtkb-bridge-poller-p3-notify-2026-04-29`
**Authority:** Owner architectural clarification archived as `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` (S319 2026-04-29). Owner verbatim: *"The objective of the poller is to ask the LO or Prime agent to check the INDEX.md when there was an updated entry that is directly relevant to the respective agent's role."* Three concrete owner decisions captured: (1) filesystem-coordination notification mechanism; (2) routing rules NEW/REVISED→Codex, GO/NO-GO/VERIFIED→Prime; (3) 15s default timer, variable, filesystem-handles-contention.

**Replaces in scope:** the spawn-based P3 invoker design implied by umbrella `bridge/gtkb-bridge-poller-001-smart-poller-007.md`. The spawn variant's binding negative result is captured in `bridge/gtkb-bridge-poller-p2-5-spike-report-2026-04-29-004.md` (VERIFIED). This proposal is the redirect: notify-based trigger using existing agent sessions, no spawning.

---

## 1. Scope

### 1.1 In scope

1. **Add 1 source module:** `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` (~120 LOC)
   - `NotificationArtifact` dataclass (recipient, transition list, written_at, etc.)
   - `write_notification(state_dir, recipient, transitions)` — atomic JSON+markdown write per recipient
   - `read_notification(state_dir, recipient)` — agent-side read; returns the most recent notification or None
   - `clear_notification(state_dir, recipient)` — agent-side acknowledgment after action
2. **Add 1 runner script:** `groundtruth-kb/scripts/bridge_poller_runner.py` (~150 LOC)
   - `argparse main()`: `--once` (single iteration; default loop-forever), `--interval` (seconds; default 15), `--state-dir`, `--quiet`, `--max-iterations` (safety cap for testing)
   - Long-running loop: parse INDEX → diff against checkpoint → route transitions → write notifications → sleep
   - Uses P1 detector + P1 checkpoint + P1 routing modules already shipped
   - Logs to `<state_dir>/poller-runs/<iso8601>.log` (JSONL)
   - SIGINT/SIGTERM-clean shutdown
3. **Add 2 test modules:** `groundtruth-kb/tests/`
   - `test_bridge_notify.py` (~10 tests; notification artifact lifecycle)
   - `test_bridge_poller_runner.py` (~10 tests; loop iteration, --once mode, INDEX-change detection, recipient filtering, log emission)
4. **Update `bridge/__init__.py`** to export the public notify API.

### 1.2 Out of scope (explicit)

- **Spawning agent sessions.** The poller never invokes `claude -p`, `codex exec`, or any agent CLI. The `_run_command_live()` adapter in `scripts/bridge_poller_verification_spike.py` is preserved as historical-evidence dead-code; this work item does NOT extend it.
- **Hook integration on the agent side.** Hooks that READ notification artifacts and surface them to the agent are a separate slice (let's call it P3.1 if filed). This proposal ships the WRITER (poller) only.
- **OS scheduled-task registration.** The poller runs as a long-running process in this proposal. Owner explicitly retired OS-scheduled-task pollers in S308 (`DELIB-1121`); this proposal does NOT re-introduce them.
- **Backfill of notifications for historical INDEX entries.** First poller run is bootstrap mode (per P1 checkpoint contract): writes baseline checkpoint, emits zero notifications. Subsequent runs notify only on transitions detected since the prior checkpoint.
- **Autonomous bridge dispatch / autonomous implementation work.** Per the owner objective, the poller's job ends at "notify the agent." The agent does the actual bridge work in its existing session.

### 1.3 No-touch boundary

- P1 detector / checkpoint / routing / audit modules: unchanged.
- P2 registry: unchanged. (The notify path uses `routing.BridgeAgent.PRIME` / `BridgeAgent.CODEX` enum directly; doesn't need registry lookups in P3 — all sessions know their own role from their durable role record.)
- P2.5 spike machinery: unchanged. Stays as historical evidence.
- Legacy `bridge/poller.py`, `bridge/worker.py`, etc.: unchanged.

## 2. Architecture

### 2.1 Notification artifact format

One notification file per recipient at `<state_dir>/notifications/pending-bridge-action-{role}.json`:

```json
{
  "schema_version": 1,
  "recipient": "prime",
  "written_at": "2026-04-29T05:30:00+00:00",
  "poller_run_id": "2026-04-29T05-29-45Z-abcdef",
  "pending_transitions": [
    {
      "document_name": "gtkb-isolation-completion-plan-2026-04-28",
      "from_status": "NEW",
      "from_file": "bridge/gtkb-isolation-completion-plan-2026-04-28-001.md",
      "to_status": "GO",
      "to_file": "bridge/gtkb-isolation-completion-plan-2026-04-28-010.md"
    }
  ],
  "summary": "1 GO awaits Prime action: gtkb-isolation-completion-plan-2026-04-28 (REVISED → GO)"
}
```

A companion `pending-bridge-action-{role}.md` markdown file holds a human-readable rendering for any tool/hook that prefers markdown over JSON parse. Agent sessions can choose either form.

### 2.2 Atomic write semantics

Per P1 `checkpoint._atomic_write`: `path.with_suffix(suffix + ".tmp")` write, then `Path.replace(target)`. POSIX rename-over guarantees that any reader sees either the full prior content or the full new content — never a partial. Owner explicitly asked the filesystem to handle contention; this delivers it.

### 2.3 Polling loop algorithm (bootstrap-safe)

```python
def main_loop(*, interval_s=15, max_iterations=None):
    state_dir = get_state_dir()  # P1 paths.get_state_dir()
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        index_text = (resolve_project_root() / "bridge" / "INDEX.md").read_text(encoding="utf-8")
        parse_result = parse_index(index_text, project_root=resolve_project_root())
        cp_load = load_checkpoint(state_dir)
        transitions = diff_against_checkpoint(
            parse_result.documents, cp_load.checkpoint, is_bootstrap=cp_load.is_bootstrap
        )
        # Always write a fresh checkpoint after each successful parse
        write_checkpoint(state_dir, parse_result.documents)
        if cp_load.is_bootstrap:
            emit_audit_event(state_dir, "bootstrap", {...})
            log_iteration(iteration, "bootstrap", documents_seen=len(parse_result.documents))
        else:
            routed = route_transitions(transitions, project_root=resolve_project_root())
            for_prime = [r for r in routed if r.outcome == ROUTABLE and r.recipient == BridgeAgent.PRIME]
            for_codex = [r for r in routed if r.outcome == ROUTABLE and r.recipient == BridgeAgent.CODEX]
            if for_prime:
                write_notification(state_dir, "prime", for_prime)
            if for_codex:
                write_notification(state_dir, "codex", for_codex)
            log_iteration(iteration, "scan", routed_count=len(routed), prime_count=len(for_prime), codex_count=len(for_codex))
        iteration += 1
        if max_iterations is None or iteration < max_iterations:
            time.sleep(interval_s)
```

Bootstrap behavior preserves the P1 contract: first run on a fresh state_dir emits zero notifications and writes a baseline checkpoint. Subsequent runs notify on actual transitions only.

### 2.4 No-spawn invariant

The poller's only outputs are:
- Filesystem writes under `<state_dir>/notifications/` and `<state_dir>/poller-runs/`
- Stdout/stderr logging
- Process exit code on shutdown

The poller does NOT:
- Invoke `subprocess.run` against `claude` or `codex`
- Send any HTTP requests
- Use any `anthropic` / `openai` / similar API client
- Modify any file outside `<state_dir>/`

Test contract enforces this: `test_bridge_poller_runner_does_not_invoke_claude_or_codex` monkeypatches `subprocess.run` to raise on any call; the loop runs and the test passes.

### 2.5 Agent-side hook (NOT in this proposal's scope)

Once notifications are being written, an agent-side hook reads them. That hook is a separate slice — possibly P3.1 — and lives in the project's `.claude/hooks/` and `.codex/hooks/` directories, NOT in the package. This proposal SHIPS the writer; the reader is filed separately.

The notification format is designed so the reader hook is trivial: read the JSON, check `pending_transitions` count, emit a `systemMessage` like "Bridge: 1 GO awaits Prime action" + the summary string. After the agent processes the transition (via existing manual `Bridge` flow in this proposal's scope), the hook can call `clear_notification(state_dir, recipient)` to remove the file. Or the next poller iteration overwrites it with the current transition state, which naturally clears stale entries.

## 3. Execution Plan (Commit Sequence)

| # | Commit | Files |
|---|---|---|
| 1 | "smart-poller P3-notify: add notify module + tests" | `notify.py` + `test_bridge_notify.py` |
| 2 | "smart-poller P3-notify: add poller runner script + tests" | `bridge_poller_runner.py` + `test_bridge_poller_runner.py` |
| 3 | "smart-poller P3-notify: wire __init__ exports + post-impl verification" | `__init__.py` (modified) + post-implementation report at `-002` of this thread |

Per-commit acceptance: each commit's tests pass before continuing. Final commit runs the full bridge test suite.

## 4. Acceptance Criteria

1. `notify.write_notification(state_dir, recipient, transitions)` produces atomic in-root JSON+markdown files at `<state_dir>/notifications/pending-bridge-action-{recipient}.{json,md}`.
2. `notify.read_notification(state_dir, recipient)` returns the parsed `NotificationArtifact` or `None` if no notification.
3. `notify.clear_notification(state_dir, recipient)` removes the notification atomically.
4. `bridge_poller_runner.py --once` runs one iteration and exits cleanly (for testability and one-shot operation).
5. `bridge_poller_runner.py --interval N --max-iterations M` runs M iterations spaced by N seconds and exits cleanly.
6. First-iteration-on-fresh-state emits ZERO notifications (bootstrap mode per P1 contract).
7. Subsequent iterations emit notifications only on detected transitions.
8. Routing: `NEW`/`REVISED` transitions route to `pending-bridge-action-codex.{json,md}`; `GO`/`NO-GO`/`VERIFIED` to `pending-bridge-action-prime.{json,md}`. (Confirmed by P1 routing.py.)
9. `subprocess.run` is NEVER invoked against `claude`/`codex` by the poller (test asserts via `monkeypatch.setattr(subprocess, "run", lambda *_, **__: assert_never())`).
10. `pending-bridge-action-{role}.json` is valid JSON; passes round-trip via `notify.read_notification`.
11. Filesystem contention is handled by atomic write semantics — no lock files, no IPC.
12. SIGINT clean shutdown: poller exits with code 0 and writes a final log entry.
13. Package-native verification passes: `cd groundtruth-kb && python -m pytest -q --tb=short` reports green.

## 5. Risks and Reversibility

### 5.1 Risk: Poller running forever consumes IO/CPU

**Mitigation:** Loop iteration is cheap (one INDEX read, one checkpoint diff, one file write). At 15s interval that's 4 iterations/minute, 240/hour, 5760/day. Each iteration: ~2KB INDEX read + ~5KB checkpoint write + maybe ~1KB notification write. ~50KB/day of state-dir writes. Negligible.

### 5.2 Risk: Stale notifications after agent acts

**Mitigation:** Each poller iteration OVERWRITES the notification file with the current pending state. If the agent has already acted on a transition and the next iteration sees no new transitions, the file gets overwritten with `pending_transitions: []` (or removed via `clear_notification`). Stale notifications self-heal within one polling interval. No race between agent action and poller; agent reads whatever current state is.

### 5.3 Risk: First-run on existing populated INDEX emits zero notifications (bootstrap suppression)

**Mitigation:** This is intended per P1 checkpoint contract. If the owner wants to "replay" all current top statuses as transitions, they invoke `--replay-existing` (deferred to umbrella P5 per `-007 §3.7`; not implemented here but the framework supports it). For now, bootstrap-and-only-detect-changes-going-forward is the safe default.

### 5.4 Risk: S308 OS-poller halt directive

**Mitigation:** S308 halted OS-scheduled-task pollers because they spawned new claude/codex sessions and consumed ~12.5M tokens/day. THIS poller has zero spawn cost (zero LLM invocations per iteration). The S308 directive is implementation-specific to the spawn pollers; per `bridge/halt-os-pollers-token-regression-002.md` the protocol itself is unaffected. The notify poller is opt-in (owner manually starts it; no OS scheduled-task registration in this proposal). Owner can stop it anytime with SIGINT.

### 5.5 Reversibility

Each of the 3 commits is independently revertable. P3-notify reverts cleanly; P1+P2 keep working without it. The poller's state-dir contents are append-only logs + overwritable notification files; reverting the code doesn't corrupt anything.

## 6. Codex Review Asks

1. **No-spawn invariant test soundness.** Confirm acceptance criterion #9 (test asserts `subprocess.run` is never invoked against `claude`/`codex`) is sufficient to mechanically prove the poller doesn't drift back into the spawn variant.

2. **Bootstrap behavior on existing populated INDEX.** Confirm the bootstrap suppression (zero notifications on first run; only detect changes going forward) is the right default for an owner who already has a populated bridge thread set. If the owner wants "first run = notify on all current top statuses," that's a `--replay-existing` follow-on.

3. **Notification file format adequacy.** Confirm the JSON schema (`schema_version`, `pending_transitions[]` with from/to status+file, `summary`) is sufficient for an eventual reader hook to surface to the agent. Flag if a different shape would be easier to consume.

4. **Per-recipient single-file vs. per-transition multiple-files.** This proposal uses one file per recipient containing all current pending transitions (overwritten each iteration). Alternative: one file per transition, accumulated over time. Single-file is simpler and self-cleans; multi-file gives history. I'd default to single-file; flag if multi-file is preferred.

5. **No-OS-scheduled-task discipline.** Confirm the proposal's exclusion of OS scheduled-task registration (per S308) is correct, and that owner-manual-start of the long-running poller is the right pattern.

6. **Reuse of P1 + P2 modules.** Confirm reusing `parse_index`, `diff_against_checkpoint`, `route_transitions`, `paths.get_state_dir`, etc. without modification is correct. No P1/P2 changes are proposed.

A NO-GO with specific findings remains more valuable than a fast GO. The notify variant is dramatically smaller scope than the spawn variant; getting the design right at proposal time should be cheap.

## 7. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. The 3 commits in §3 occur only after Codex GO.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
