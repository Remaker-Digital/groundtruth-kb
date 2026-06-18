ADVISORY

bridge_kind: lo_advisory
Document: gtkb-dispatch-malformed-status-token-packet-gap-advisory
Version: 001
Author: Loyal Opposition (Codex, session envelope ::init gtkb lo)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Related Thread: bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md
Related Work Item: WI-4658

# Loyal Opposition Advisory - Malformed Status Quarantine Does Not Cover Implementation-Authorization Packet Creation

## Summary

Live dispatcher evidence after `gtkb-dispatch-malformed-status-token-quarantine-004.md` shows a remaining bridge-dispatch failure mode: Prime Builder dispatch no longer fails only at work-intent acquire, but still fails when creating implementation-start authorization packets.

This is not a reversal of the WI-4658 verification evidence. WI-4658 verified the work-intent registry quarantine path, the persisted `quarantined_threads` state, and the dispatch-health WARN finding. The new evidence shows an adjacent parser path in `scripts/implementation_authorization.py` still scans the malformed `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` file and raises `AuthorizationError`, preventing dispatch of an otherwise selected GO thread.

## Live Evidence

- `gt bridge dispatch health --json` reports `health_status: FAIL`.
- `.gtkb-state/bridge-poller/dispatch-state.json` shows `prime-builder` / `prime-builder:A` at `last_result: launch_failed` with:
  - `reason: implementation_authorization_packet_failed`
  - `failed_slug: gtkb-wi4616-covered-by-dispatch-reliability-reconciliation`
  - `error_message: Bridge file has unrecognized status line: bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md: 'GO test'`
- `.gtkb-state/bridge-poller/dispatch-failures.jsonl` continues to append repeated `implementation_authorization_packet_failed` rows for `gtkb-wi4616-covered-by-dispatch-reliability-reconciliation` while also recording `bridge_file_malformed_status_quarantined` rows for `gtkb-wi4232-bridge-index-drift-pb-classification`.
- Latest `gtkb-wi4616-covered-by-dispatch-reliability-reconciliation` status is `GO` at `bridge/gtkb-wi4616-covered-by-dispatch-reliability-reconciliation-006.md`, so Prime dispatch has a legitimate GO thread to process but cannot issue the worker packet.

## Source Evidence

- `scripts/cross_harness_bridge_trigger.py::_create_dispatch_authorization_packets` calls `issue_dispatch_authorization_packets(project_root, bridge_ids, dispatch_id=dispatch_id)` before spawning Prime workers. On `AuthorizationError`, it records `implementation_authorization_packet_failed` and prevents launch.
- `scripts/implementation_authorization.py::_bridge_file_status` has a separate status parser from `scripts/bridge_work_intent_registry.py::_bridge_file_status`. It still raises `AuthorizationError(f"Bridge file has unrecognized status line: {rel_path}: {line!r}")` for `GO test`.
- WI-4658 introduced `MalformedBridgeStatusError` and quarantine behavior in `scripts/bridge_work_intent_registry.py` and the dispatch batch-acquire path, but did not update `scripts/implementation_authorization.py`.

## Recommended Prime Builder Action

File a focused follow-up implementation proposal. The smallest likely repair is to make implementation-authorization packet creation honor the same malformed-status quarantine semantics before packet issuance:

1. Do not treat `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md` as a valid GO.
2. Do not let that malformed thread poison packet creation for unrelated GO threads selected in the same dispatch batch.
3. Preserve fail-closed packet creation for the selected GO thread itself if its own latest bridge status is malformed or non-substantive.
4. Add tests proving:
   - a malformed unrelated GO-status thread is quarantined or skipped before packet creation;
   - packet creation still succeeds for the legitimate selected GO thread;
   - malformed status on the selected thread still prevents packet creation;
   - dispatch failure logs distinguish quarantine from real authorization failure.

Likely target paths:

- `scripts/implementation_authorization.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- optionally `platform_tests/scripts/test_worker_packet_authorization_envelope.py`

## Role / Authority Note

This advisory is filed from the current Loyal Opposition session envelope. I am not taking Prime Builder mutation from this session. The live failure is Prime Builder-actionable as a bridge-dispatch reliability follow-up.

## Commands Executed

```text
gt bridge dispatch status --json
gt bridge dispatch health --json
Get-Content -Raw .gtkb-state/bridge-poller/dispatch-state.json
Get-ChildItem bridge -Filter 'gtkb-wi4616-covered-by-dispatch-reliability-reconciliation-*.md'
rg -n "implementation_authorization_packet_failed|MalformedBridgeStatusError|malformed status|quarantined_threads|quarantined_slugs" scripts groundtruth-kb/src platform_tests -g "*.py"
Get-Content -Tail 20 .gtkb-state/bridge-poller/dispatch-failures.jsonl
Get-Content scripts/cross_harness_bridge_trigger.py | Select-Object -Skip 990 -First 45
Get-Content scripts/implementation_authorization.py | Select-Object -Skip 1 -First 120
rg -n "bridge_file_status|_bridge_file_status|MalformedBridgeStatus|WorkIntentRegistryError|GO test|unrecognized status" scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/bridge_work_intent_registry.py
```

## Bridge Filing

Filed as `bridge/gtkb-dispatch-malformed-status-token-packet-gap-advisory-001.md`; no prior bridge file was modified.
