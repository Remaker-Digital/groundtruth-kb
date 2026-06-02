NEW

# Implementation Proposal - Background Auto-Push Investigation (GTKB-AUTO-PUSH-INVESTIGATION-001)

bridge_kind: implementation_proposal
Document: gtkb-auto-push-investigation-001-prop
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-AUTO-PUSH-INVESTIGATION-001

target_paths: [".gtkb-state/git-audit/", "scripts/git_audit_observer.py", "tests/scripts/test_git_audit_observer.py"]

This NEW proposal investigates and instruments the source of background auto-push of local commits to `origin/develop` observed at S344 (commit 5611dc44 pushed between local commit creation and subsequent reset --soft, with no human-visible push command in transcript).

## Claim

Add a passive git observer that logs every push event to `.gtkb-state/git-audit/pushes.jsonl`. Cross-reference against expected push points (manual `gh pr` invocations, owner-directed pushes). Surface unexpected pushes via UserPromptSubmit additionalContext.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `GOV-ARTIFACT-APPROVAL-001` - push to remote is a high-blast-radius mutation.
- `PB-ARTIFACT-APPROVAL-001` - protected behavior.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - this WI tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-GOVERNANCE-HARDENING authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI description + S344 incident form the operative scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-GOVERNANCE-HARDENING per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (observer) + IP-2 (audit hook) + IP-3 (tests) single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Git post-push hook (or wrapper)

Local-only git hook at `.git/hooks/post-receive` is server-side. Need a client-side intercept. Approach: monkey-patch via `git config alias.push 'push'` is ineffective. Better: a wrapper script in `scripts/git_audit_observer.py` that polls `git reflog --since` periodically + on UserPromptSubmit, writes new push events to `.gtkb-state/git-audit/pushes.jsonl`.

### IP-2: Unexpected-push surfacing

UserPromptSubmit hook reads `pushes.jsonl`, cross-references against an in-session push intent registry (`.gtkb-state/git-audit/intent-<session>.json`, written when owner or Prime explicitly intends a push). Pushes without matching intent are surfaced in additionalContext.

### IP-3: Tests + diagnosis script

Tests verify push detection, intent matching, and unexpected-push flagging.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Push event logged to jsonl | `test_observer_logs_push_to_jsonl` |
| Multiple pushes recorded | `test_observer_logs_multiple_pushes` |
| Intent-matched push not flagged | `test_intent_matched_push_not_flagged` |
| Unmatched push flagged | `test_unmatched_push_flagged` |
| JSONL format parseable | `test_pushes_jsonl_parseable` |
| Session-scoped intent registry | `test_intent_registry_per_session` |

Run: `python -m pytest tests/scripts/test_git_audit_observer.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 6 tests PASS.
- Both preflights PASS.
- Real-world: S344-style auto-push scenario is detected in post-impl smoke test.

## Risks / Rollback

- Risk: observer adds I/O on every UserPromptSubmit; latency concern. Mitigation: cache + only re-scan when reflog mtime changes.
- Risk: false-flag on legitimate pushes from git aliases. Mitigation: intent registry surfaces them.
- Rollback: remove the observer script + hook registration.

## Recommended Commit Type

`feat` - new audit instrumentation. ~70 LOC.
