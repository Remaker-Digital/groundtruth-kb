# Canonical Backlog Writer Document-Role Authority Audit

Date: 2026-07-10
Role: Prime Builder / Codex
Program impact: Harness Observability and Dispatcher Workflow Reporting goal

## Findings

### F1 - P0: Backlog mutation role is inferred from dispatcher/default state instead of the explicit session document

Claim: The canonical backlog mutation path violates `GOV-SESSION-ROLE-AUTHORITY-001` v5 and `DCL-SESSION-ROLE-RESOLUTION-001` v6.

Evidence:

- `scripts/_kb_attribution.py:304-330` resolves a harness, requires a role from `harness-registry.json`, and then optionally substitutes a marker role. The explicit session envelope's `role_resolved` is not the role authority.
- `scripts/_kb_attribution.py:260-278` calls `resolve_interactive_session_role(..., current_session_id=None)` and accepts `marker_session_id_unverified`.
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add.py:142-157,194-200`, `cli_backlog_update.py:57-61,147-152`, and `cli_backlog_add_work_item.py:90-99,185-191` all use that resolver before mutation and expose no explicit role-document input.
- The current Codex session envelope records `role_resolved=prime-builder`, but a peer session's shared marker recorded `loyal-opposition`. The WI-5118 source-spec linkage was consequently written as `changed_by=loyal-opposition/codex`.
- `DELIB-20260710-GTKB-INTERACTIVE-KB-ATTRIBUTION-GLOBAL-MARKER-COLLISION` records the same fresh defect on WI-5148.

Risk/impact: A peer session or dispatcher/default role can silently relabel MemBase mutations. This corrupts governance provenance and lets worker behavior depend on dispatcher configuration after delivery.

Required correction:

1. The writer must consume one canonical session/dispatch document carrying explicit resolved role plus run/session provenance.
2. The role segment of `changed_by` must derive exclusively from that document.
3. A dispatch event may confirm dispatcher intent but must never supply or substitute worker role.
4. Missing, malformed, conflicting, or session-mismatched document evidence must fail before mutation with a recovery route.
5. Registry, target-map, ranking, shared-marker, and `GTKB_BRIDGE_POLLER_RUN_ID` state must not be behavior-role authority inside the writer.

### F2 - P1: Regression tests preserve behavior prohibited by the current GOV/DCL

Evidence:

- `platform_tests/scripts/test_kb_attribution_session_role.py:109-113` explicitly treats `marker_session_id_unverified` as an accepted role source.
- The same file at `150-160` requires dispatched attribution to keep the durable role.
- The same file at `222-247` requires durable Prime fallback when the envelope is absent, skipped under headless dispatch, or ambiguous.
- `DCL-SESSION-ROLE-RESOLUTION-001` v6 now requires explicit worker-document role evidence, prohibits dispatcher-configuration reads for worker behavior, and rejects unverified shared-marker authority.

Risk/impact: The focused suite can remain green while the formal role-authority contract fails, and a correct implementation would be rejected by stale tests.

Required correction: Replace these cases with document-authority, mismatch-audit-without-substitution, missing/conflicting-evidence failure, cross-session isolation, interactive/dispatched parity, and all-writer-surface integration tests.

### F3 - P1: The corrective test artifact was created through a now-rejected authority workaround

Evidence: `TEST-11340` was created after setting `GTKB_BRIDGE_POLLER_RUN_ID` to suppress the peer marker and force the durable PB label. The resulting label is correct, but the authority source is not.

Risk/impact: The append-only artifact history contains a mutation whose provenance mechanism contradicts the owner's document-only role requirement.

Required correction: Preserve version 1 as audit evidence. After the writer fix is independently VERIFIED, write a new `TEST-11340` version through the corrected document-authoritative path and cite this audit. Do not delete or rewrite history.

## Work-Item Disposition

No duplicate work item is needed.

- `WI-5171` is the P0 implementation carrier for explicit session-role envelopes, worker bootstrap, and marker/attribution isolation.
- `WI-5086` preserves the marker-write failure and cross-surface role-fragmentation regression.
- `WI-5010` preserves the interactive `changed_by` authority investigation and can close only after the resolved contract is implemented and verified.
- `WI-4463` remains historical recurrence evidence; do not reopen it while the live correction is carried by WI-5171/WI-5086.

These three open items are added to the active Harness Observability and Dispatcher Workflow Reporting goal's terminal-state audit.

## Recommended First Slice

Authorize a bounded source-and-test slice under `PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES` for WI-5171 and WI-5086. Limit it to the canonical backlog writer and its role-document consumer. Exclude dispatcher selection/ranking changes, formal-artifact mutation, rules/hooks registration, release/deploy, credentials, and unrelated modernization work.

## Owner Decision Needed

One bounded PAUTH decision is required before a bridge proposal or protected implementation can begin.
