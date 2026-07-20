# Loyal Opposition Verification Assessment — WI-5041 dispatcher per-thread re-offer backoff (-003)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T01-00-58Z-loyal-opposition-B-915251
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo (dispatch keyword)

Date: 2026-07-10 01:15 UTC
Author: Loyal Opposition (claude, harness B) — bridge auto-dispatch `2026-07-10T01-00-58Z-loyal-opposition-B-915251`
Reviewer session context: fresh headless dispatch (independent of the -003 report author session `019f4929-9343-7480-a8a0-055a97ab4b8a`, codex/harness A)
Bridge thread: `gtkb-wi5041-dispatcher-thread-reoffer-backoff` (-001 proposal, -002 GO, -003 implementation report)
Specs: `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-RELIABILITY-FAST-LANE-001`, `GOV-STANDING-BACKLOG-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
WIs: `WI-5041` (substance verified); `WI-5066` (entangled sibling; blocks isolated finalization)
Prior deliberations: `DELIB-20266278` (dispatch-treadmill-drain program authorization), `DELIB-20266272` (PHASE-Y dispatcher go-live)

## Disposition

**RECORD-AND-STOP. No bridge verdict filed.**

The WI-5041 implementation is **substantively correct and fully verified against its linked
specifications and the four GO-verdict conditions** (evidence below). It is **not**
VERIFIED-finalizable in this headless dispatch because one of the three declared `target_paths`,
`platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, is **symmetrically entangled** with
sibling thread **WI-5066** (`dispatch-wrapper-commandline-redaction`, currently REVISED / un-GO'd).
A `VERIFIED` finalization commit that stages that file wholesale would bundle WI-5066's un-approved,
un-committed test changes into a commit labeled as the WI-5041 fix, violating the scoped-commit
invariant (`.claude/rules/bridge-essential.md` § Invariants) and corrupting WI-5066's audit trail.
The entanglement is bidirectional: WI-5041's own green target suite *depends on* WI-5066's
uncommitted daemon-test fixes (proof below), so a hypothetical WI-5041-only hunk commit would itself
be **red**.

No `NO-GO` is filed because there is **no implementation defect** for Prime Builder to correct — the
blocker is working-tree finalization ordering / hygiene, an interactive- or owner-gated operation,
not a headless-Prime revision. Filing any bridge verdict would change the `-003` actionable
signature and risk exactly the owner-gated NO-GO↔REVISED re-offer treadmill that WI-5041 is designed
to suppress. The `-003` report is left pending for an interactive session or owner-coordinated
finalization per the Resolution Context below.

## Methodology Trail (read-only against the current commingled working tree)

- Read full thread: `-001` (NEW proposal, prime_proposal/claude session `d97ced75`), `-002` (GO,
  loyal-opposition/claude session `85e78bc0`), `-003` (implementation report, prime-builder/codex
  session `019f4929`, harness A). Reviewer independence satisfied: my headless dispatch session
  context differs from the `-003` author session `019f4929`.
- `git diff -- scripts/dispatcher_runtime.py` (283-line source diff, full read).
- `git diff -- platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py` (test diffs, full read).
- `git show HEAD:scripts/dispatcher_runtime.py | grep` for readiness-gate provenance.
- pytest (project venv `groundtruth-kb/.venv/Scripts/python.exe`): full approved target suite; durable-keyed regression; stash-isolation runs.
- `ruff check` + `ruff format --check` on all three target files.
- `git stash push -- <file>` → re-run → `git stash pop` isolation for causation (twice; both popped clean, tree restored).

## Positive Verification Evidence (WI-5041 substance)

### Implementation is faithful to the approved `-001` proposal

Verified in `scripts/dispatcher_runtime.py`:

- `THREAD_REOFFER_BACKOFF_RESULT = "thread_reoffer_backoff_active"` (L284); defaults
  `THRESHOLD=3` / `WINDOW=3600` (L285-286); env-overridable via
  `_thread_reoffer_backoff_threshold()` / `_thread_reoffer_backoff_window_seconds()` (L1195-1207).
- Distinct audit token added to `EXPECTED_SUPPRESSION_REASONS` (L302) — routes as an expected
  suppression, NOT an actionable failure, and is **not** the provider token
  (`GOV-FILE-BRIDGE-AUTHORITY-001` audit-path claim satisfied).
- New gate `_thread_reoffer_backoff_skip(...)` (L5611) is **orthogonal to provider failure backoff**:
  it counts re-offer cycles per document slug and does **not** read `failure_count` or reuse
  circuit-breaker/provider-backoff machinery. Orthogonality guard (proposal scope #4) satisfied.
- Slug-keyed (spans LO→Prime→LO), not recipient-keyed — the correct axis for a role-alternating
  treadmill (proposal scope #2 keying).
- Re-arm semantics: `_prune_thread_reoffers` drops non-actionable slugs each cycle (L5687, called
  L5841); `_reset_recipient_state` clears `thread_reoffers` on operator clean-slate (L994). Both
  re-arm paths present (proposal scope #3).
- Daemon-live path suppresses a throttled thread **before** work-intent/impl-auth/spawn in
  `_filter_prime_selected_by_work_intent` (L1777) and records the suppression evidence.
- Double-count avoidance: `run_dispatch_cycle` calls `_spawn_harness(..., record_thread_reoffer=False)`
  (L6511) and records the offer itself in the caller (L6546); daemon-live `_spawn_harness` records
  its own offers. One recording site per path — no double increment.
- **Latent-bug catch (in-scope, correct):** the final state write was changed from a fresh 3-key
  payload to `payload = dict(state); payload.update({...})` (L6586). The prior fresh-dict form would
  have silently dropped the new top-level `thread_reoffers` key on every cycle; the GO premise-check
  noted `_write_dispatch_state` preserves keys but did not observe that `run_dispatch_cycle` was
  bypassing that preservation. The implementer caught and fixed this. Good.

### All five new tests are behavioral (not shallow)

`platform_tests/scripts/test_dispatcher_runtime.py`:
`test_thread_reoffer_backoff_skip_suppresses_within_window`,
`test_thread_reoffer_record_rearms_after_window` (GO condition #1 — cooldown resumption; asserts
count→2 within window, count→1 + refreshed `first_offered_at` after window),
`test_thread_reoffer_state_round_trips_and_prunes_terminal_threads` (GO condition #2 — additive
write→load round-trip + prune),
`test_reset_recipient_clears_thread_reoffer_state` (operator reset re-arm).
`platform_tests/scripts/test_gtkb_dispatcher_daemon.py`:
`test_daemon_live_honors_thread_reoffer_backoff_skip` (GO condition #3 — operator visibility; asserts
no spawn + suppression surfaces as `spawn_reason` in decisions and `reason` in `spawn_results`).

### Executed evidence (independently reproduced this session)

| Gate | Command | Result |
| --- | --- | --- |
| Approved target suite | `pytest test_dispatcher_runtime.py test_gtkb_dispatcher_daemon.py` | **227 passed, 1 warning in 53.21s** (matches report) |
| Lint | `ruff check` (3 target files) | **All checks passed!** |
| Format | `ruff format --check` (3 target files) | **3 files already formatted** |
| Root boundary | all three `target_paths` under `E:/GT-KB` | satisfied (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) |

## Report's residual "durable-keyed regression" failure — EXONERATED (answers LO Ask #2)

The `-003` report flags two failures in `platform_tests/scripts/test_dispatcher_runtime_durable_keyed_regression.py`
(`test_resolve_dispatch_target_ignores_session_role_marker[loyal-opposition-codex-lo]` and
`test_dispatch_prompt_first_line_emits_durable_keyed_keyword[loyal-opposition-::init gtkb lo]`, both
`DispatchTargetNotReady: codex_dispatch_not_ready`) and asks whether they block WI-5041.

**Determination: they do NOT block WI-5041; they are pre-existing and independent. Route to their own thread.**

Proof (stash-isolation):
- The regression file is **unmodified vs HEAD** (`git diff --stat` empty; absent from the `M` list).
- `_is_dispatch_ready` is **pre-existing at HEAD** (HEAD line 4386); WI-5041 only shifted its line
  number via insertions above it and did not modify the gate or its call sites.
- With WI-5041's `scripts/dispatcher_runtime.py` stashed to HEAD, the durable-keyed regression fails
  the **same two tests** with the **same reason** at the same `_is_dispatch_ready` call site (HEAD
  line 4577). Identical failure with WI-5041's source removed ⇒ WI-5041 is not the cause.

The failures are a `_is_dispatch_ready` readiness-fixture drift affecting the LO/Codex synthetic
target, orthogonal to the thread-reoffer feature. GO condition #4 ("keep the durable-keyed regression
green") is met in spirit (WI-5041 introduced no regression); the literal red is pre-existing drift
that belongs to a separate defect thread, not WI-5041.

## Finalization Blocker — WI-5066 entanglement in `test_gtkb_dispatcher_daemon.py`

`test_gtkb_dispatcher_daemon.py` is a WI-5041 `target_path`, but its uncommitted diff contains, in
addition to WI-5041's `test_daemon_live_honors_thread_reoffer_backoff_skip`, four hunks that are
**not** thread-reoffer work:

1. `test_shadow_decision_shrinks_remaining_items` += `monkeypatch.setattr(runtime, "_is_dispatch_ready", lambda *a, **k: True)`.
2. `_capture_worker_command` refactored to also return the spawned worker env.
3. `_lifetime_value` refactored to decode the base64 `--config-env` payload
   (`RUN_WITH_STATUS_CONFIG_ENV_VAR`).
4. `test_daemon_spawn_passes_per_role_lifetime` updated to the new helper signatures.

Hunks 2–4 are the `--config-env` command-line-redaction feature owned by **WI-5066**
(`bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-*`, latest `-007` REVISED — un-GO'd; its
`-005` explicitly describes `run_with_status.py --config-env` / `RUN_WITH_STATUS_CONFIG_ENV_VAR`).
Hunk 1 is a dispatch-readiness fixture fix of the same family as the exonerated durable-keyed
failures. None are WI-5041 scope.

**Bidirectional entanglement proof (stash-isolation):** with `test_gtkb_dispatcher_daemon.py` stashed
to HEAD, `test_daemon_spawn_passes_per_role_lifetime` and `test_shadow_decision_shrinks_remaining_items`
**both fail at HEAD**. HEAD's committed `_spawn_harness` already emits `--config-env`, but HEAD's
daemon test file was never updated to match, so those tests are red at HEAD; the uncommitted WI-5066
hunks are what make them green. Therefore:

- Staging the file wholesale for a WI-5041 `VERIFIED` commit **captures WI-5066's un-GO'd work**
  (no-capture / scoped-commit violation; corrupts WI-5066's audit trail).
- A hypothetical WI-5041-hunk-only commit would be **red** at that commit (WI-5041's green suite
  depends on WI-5066's fix), violating the VERIFIED "committed state is green" expectation.

Both isolation runs restored the working tree cleanly (`git stash pop`; file returns to `M`). No
source, test, or bridge file was mutated by this review.

## Resolution Context (interactive session / owner — needs a MECHANICAL break, not re-review)

Substantive verification is **complete and recorded here**; a re-dispatched LO should NOT re-run it.
The remaining work is finalization ordering, which is owner- or interactive-gated:

- **Preferred:** finalize **WI-5066 first** (once it reaches GO + implementation report + VERIFIED).
  After WI-5066's `test_gtkb_dispatcher_daemon.py` hunks are committed, WI-5041's diff to that file
  reduces to only `test_daemon_live_honors_thread_reoffer_backoff_skip`, and WI-5041 can be cleanly
  VERIFIED-finalized against its three `target_paths` using this report's evidence.
- **Alternative:** owner authorizes a **by-reference co-finalization waiver** (a `DELIB` cited by the
  finalization helper) permitting a single coordinated commit that lands the WI-5041 thread-reoffer
  work together with the WI-5066-owned daemon-test hunks, with both threads' provenance recorded.
- **Do NOT** attempt a headless hunk-scoped de-commingle: WI-5041's green suite depends on WI-5066's
  hunks, so a partial commit is red, and LO hand-rolled commingled finalization is disallowed.
- The two exonerated `codex_dispatch_not_ready` durable-keyed failures and the `_is_dispatch_ready`
  `test_shadow_decision` red are a pre-existing readiness-fixture drift that should be captured as
  its own backlog defect (out of scope for both WI-5041 and this dispatch's write authority).

## Bridge Protocol Compliance

Read-only review; no bridge verdict written (rationale in Disposition). Numbered bridge chain and
dispatcher/TAFE state unchanged. This report is the recorded blocker artifact per the headless-worker
"record the blocker and stop" rule and the WI-5119 record-and-stop precedent
(`INSIGHTS-2026-07-10-00-21.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
