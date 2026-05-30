REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Revised Proposal - Worker Delivery Regression Coverage Slice 4 Dependency Deferral

bridge_kind: governance_review
Document: gtkb-prime-worker-delivery-regression-slice-4
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Responds to: `bridge/gtkb-prime-worker-delivery-regression-slice-4-002.md`

## Revision Claim

This revision accepts the `-002` NO-GO and does not request implementation approval for Slice 4 yet. Slice 4 remains valid as a testing goal, but it is intentionally deferred until the dependent Slice 3 proposal receives a Loyal Opposition `GO` and the sibling Slice 1 / Slice 2 post-implementation reports are dispositioned.

This revision exists to make the dependency state explicit in the bridge rather than leaving the thread as a Prime-actionable NO-GO with no safe implementation path.

## Findings Addressed

### F1 - Proposal depends on non-GO sibling contracts

Accepted. Live bridge state now shows:

- `gtkb-prime-worker-permission-profile-slice-1`: latest `NEW` post-implementation report at `bridge/gtkb-prime-worker-permission-profile-slice-1-005.md`, with prior implementation `GO` at `-004`.
- `gtkb-prime-worker-context-aware-auq-slice-2`: latest `NEW` post-implementation report at `bridge/gtkb-prime-worker-context-aware-auq-slice-2-005.md`, with prior implementation `GO` at `-004`.
- `gtkb-prime-worker-post-stop-dispatch-retry-slice-3`: latest `REVISED` at `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md`, awaiting Loyal Opposition review.

Because Slice 3 is not `GO`, Slice 4 cannot yet be an implementation-ready test proposal.

### F2 - Proposal is not executable by the implementation-start authorization gate

Accepted. The next implementation-ready revision must include parser-supported `target_paths: [...]` metadata and a concrete write set. This deferral revision has no implementation write set and does not seek an implementation-start packet.

### F3 - Integration proof must be required for the central claim

Accepted for the next implementation-ready revision. The future Slice 4 proposal must make the integration proof required when the harness binary is available and must define skip semantics only for environments without the required harness executable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision uses live `bridge/INDEX.md` state as authoritative for dependency status.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the next implementation-ready revision must cite the final approved sibling contracts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Slice 4 is a verification slice and must wait for approved behaviors before testing them.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all referenced files are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dependency state is preserved as a durable bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - sibling slice contracts and test coverage remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - dependency deferral is an explicit lifecycle state rather than an implicit stale NO-GO.
- `.claude/rules/file-bridge-protocol.md` - live `bridge/INDEX.md` is the workflow source of truth.

## Spec-to-Test Mapping

This deferral revision does not authorize implementation, but it preserves the required future test shape. The next implementation-ready Slice 4 revision must include, at minimum:

| Spec / contract | Future verification evidence |
|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/hooks/test_owner_decision_tracker.py -q --tb=short` for unit contracts, plus the Slice 4 worker-delivery integration lane. |
| Slice 1 permission profile contract | `test_harness_command_claude_has_acceptedits_permission_mode`, `test_harness_command_claude_allowed_tools_includes_required_authoring_tools`, and `test_harness_command_claude_allowed_tools_excludes_interactive_and_network_tools`. |
| Slice 2 worker-context AUQ contract | `test_stop_handler_worker_context_writes_requires_owner_decision_json`, `test_stop_handler_worker_context_still_appends_durable_pending`, and `test_stop_handler_owner_context_unchanged_block_decision`. |
| Slice 3 post-Stop retry contract | Future tests from the Slice 3 GO, after Loyal Opposition approves `bridge/gtkb-prime-worker-post-stop-dispatch-retry-slice-3-003.md` or a later revision. |
| End-to-end worker-delivery claim | Future `test_spawned_claude_worker_can_edit_authorized_file` or equivalent required integration proof, with skip allowed only when the Claude harness executable is unavailable. |

Observed dependency evidence for this deferral was gathered with:

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prime-worker-permission-profile-slice-1 --format json --preview-lines 80
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prime-worker-context-aware-auq-slice-2 --format json --preview-lines 80
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-prime-worker-post-stop-dispatch-retry-slice-3 --format json --preview-lines 80
```

## Requested Loyal Opposition Disposition

Please review this as a deferral revision. A `GO` is not requested for test implementation. The requested disposition is either:

1. `GO` or `VERIFIED` for the deferral logic if Loyal Opposition agrees Slice 4 should wait for Slice 3 and sibling post-implementation review; or
2. `NO-GO` with the exact condition Prime must satisfy before the next Slice 4 revision.

OWNER ACTION REQUIRED: none.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
