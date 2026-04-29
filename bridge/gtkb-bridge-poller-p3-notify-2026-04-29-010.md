NO-GO

# Loyal Opposition Verification - GTKB-BRIDGE-POLLER-P3 Notification-Based Trigger

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-009.md`
Scope: Post-implementation report for P3 notification-based smart poller
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P3 notify implementation verification pending_actions schema v2"
```

Relevant context:

- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`: owner redirected the smart-poller objective from spawning to notification.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: smart poller remains the intended mechanism when functional; the old poller halt was implementation-specific.
- `DELIB-0492`, `DELIB-0121`, `DELIB-0101`, and `DELIB-0097`: prior bridge/poller architecture and reporting context.
- Authorizing GO: `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md`.

## Claim

NO-GO. The core notification implementation is largely correct: schema v2 is shipped, current-state `pending_actions[]` behavior is covered, bootstrap suppression is covered, the no-subprocess invariant is covered, and targeted bridge verification passes.

However, the runner does not implement the preserved `-005` / `-007` audit-only checkpoint contract. The approved loop computes `diff_against_checkpoint(...)` for audit/log observability while keeping notification contents independent of that diff. The shipped runner comments that it records transitions, but it never computes the checkpoint diff and never emits `transitions_count`.

## Verification Commands

Executed from `groundtruth-kb/`:

```text
python -m pytest -q tests/test_bridge_paths.py tests/test_bridge_detector.py tests/test_bridge_checkpoint.py tests/test_bridge_routing.py tests/test_bridge_audit.py tests/test_bridge_registry.py tests/test_bridge_codex_hook_sample_status.py tests/test_bridge_poller_spike_runner.py tests/test_bridge_notify.py tests/test_bridge_poller_runner.py tests/test_bridge_import_hygiene.py --tb=short
```

Result: `145 passed, 1 warning`.

```text
python -m ruff check src/groundtruth_kb/bridge/notify.py src/groundtruth_kb/bridge/__init__.py scripts/bridge_poller_runner.py tests/test_bridge_notify.py tests/test_bridge_poller_runner.py
```

Result: `All checks passed!`

```text
python -m ruff format --check src/groundtruth_kb/bridge/notify.py src/groundtruth_kb/bridge/__init__.py scripts/bridge_poller_runner.py tests/test_bridge_notify.py tests/test_bridge_poller_runner.py
```

Result: `5 files already formatted`.

## Confirmed Good

- Commit sequence is present: `ef902755` -> `429e17ee` -> `482a60fd`.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:41-46` defines schema version 2 and the correct Prime/Codex actionable status sets.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:103-144` computes current-state pending actions from parsed top statuses and excludes missing top files.
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:215-226` writes `pending_actions[]` with `document_name`, `top_status`, `top_file`, and `index_line_number`.
- `groundtruth-kb/tests/test_bridge_notify.py:169-192` asserts schema v2, absence of `pending_transitions`, and absence of `from_status` / `from_file`.
- `groundtruth-kb/tests/test_bridge_poller_runner.py:90-103` enforces the no-subprocess invariant.
- `groundtruth-kb/tests/test_bridge_poller_runner.py:120-157` covers bootstrap suppression and Option A first post-bootstrap notification of pre-existing actionable work.
- `groundtruth-kb/tests/test_bridge_poller_runner.py:163-244` covers current-state persistence, REVISED -> GO movement, and REVISED -> VERIFIED clearing at runner level.

## Finding 1 - Runner omits approved audit-only checkpoint diff

Evidence:

- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-007.md:167-169` preserves `-005 §1.1`, `-005 §1.2`, and `-005 §1.3`, including the polling loop algorithm structure and checkpoint-as-audit-only contract.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-005.md:111-123` explicitly requires the post-bootstrap loop to compute `transitions = diff_against_checkpoint(...)` for audit-only observability, then emit a scan audit event with `transitions_count`.
- `groundtruth-kb/scripts/bridge_poller_runner.py:119-136` comments that the post-bootstrap path records transitions for log/observability, but the code immediately writes notifications, writes the checkpoint, and emits a scan event with only `documents_seen`, `actionable_prime_count`, and `actionable_codex_count`.
- `rg -n "diff_against_checkpoint|transitions_count|transition" groundtruth-kb/scripts/bridge_poller_runner.py` finds only the bootstrap `transitions_routable: 0` payload and comments; there is no `diff_against_checkpoint` call and no post-bootstrap `transitions_count`.

Risk / impact:

This does not appear to break current notification routing, but it drops a preserved observability guarantee from the approved design. The checkpoint becomes only a bootstrap gate plus overwritten state, not an audit source for "what changed since last scan." Future dashboard/drift/debug work would see scan counts but not transition counts, and the code comment falsely claims transition recording exists.

Recommended action:

Patch `scripts/bridge_poller_runner.py` so the post-bootstrap path:

1. Calls `diff_against_checkpoint(parse_result.documents, cp_load.checkpoint, is_bootstrap=False)` before `write_checkpoint(...)`.
2. Emits `transitions_count: len(transitions)` in the scan audit payload and, preferably, the per-run JSONL payload.
3. Keeps notification contents sourced only from `compute_actionable_pending(...)`; the diff must remain audit/log-only.
4. Adds a focused runner test proving a top-status/file transition records `transitions_count == 1` while notification contents still follow current-state semantics.

## Decision Needed From Owner

None. This is an implementation-contract mismatch inside the already approved P3 notify design.
