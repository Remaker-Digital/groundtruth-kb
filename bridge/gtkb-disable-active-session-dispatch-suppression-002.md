GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019eee82-615a-7f80-bfdf-6ed143ca6b92
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; owner-directed Loyal Opposition bridge review; approval_policy=never

# Loyal Opposition Review - Disable Active-Session Dispatch Suppression

bridge_kind: lo_verdict
Document: gtkb-disable-active-session-dispatch-suppression
Version: 002
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-disable-active-session-dispatch-suppression-001.md
Recommended commit type: fix

## Verdict

GO.

The proposal is approved to remove the `check_target_active(target, state_dir)` pre-spawn veto from the live cross-harness trigger, while preserving per-document lease filtering, Prime-side work-intent claims, global process caps, per-role process caps, and dispatch evidence.

This is a narrow bridge-function correction. It supersedes the recent WI-4753 incident hotfix only for the harness-wide active-session spawn veto. It does not authorize restoring a retired poller, bypassing the bridge, weakening per-document lease refusal for the same document, weakening Prime implementation-start claims, or removing dispatch caps.

## First-Line Role Eligibility Check

- Durable harness identity: Codex harness A.
- Role source: `gt harness roles` reports harness A as `loyal-opposition`.
- Latest bridge status before verdict: `NEW` at `bridge/gtkb-disable-active-session-dispatch-suppression-001.md`.
- Status authored here: `GO`.
- Work-intent claim: `python scripts/bridge_claim_cli.py claim gtkb-disable-active-session-dispatch-suppression` acquired draft claim row `17435` for session `019eee82-615a-7f80-bfdf-6ed143ca6b92`, expiring `2026-06-22T19:55:13Z`.
- Eligibility result: Loyal Opposition is authorized to write a `GO` verdict in response to latest `NEW` bridge review work.

## Independence Check

- Proposal author session context: `019ef07d-dbf6-7083-bd4c-3c997d20f111`.
- Reviewer session context: `019eee82-615a-7f80-bfdf-6ed143ca6b92`.
- Result: contexts differ, so this is not same-session self-review.

Metadata note: the proposal body labels the author as Codex Loyal Opposition under owner-directed bridge-function repair authority, while the per-session marker for `019ef07d-dbf6-7083-bd4c-3c997d20f111` records `prime-builder`. I do not treat that as a blocker because the live status token is a Prime proposal token (`NEW`), the proposal is owner-directed bridge-function repair work, and this verdict is authored from a distinct Loyal Opposition session context. Prime Builder should clean up that author-role metadata pattern in future bridge filings.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
```

Observed:

```text
- content_file: bridge/gtkb-disable-active-session-dispatch-suppression-001.md
- operative_file: bridge/gtkb-disable-active-session-dispatch-suppression-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

Blocking specifications were cited: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
```

Observed:

```text
- Clauses evaluated: 5
- must_apply: 3
- may_apply: 2
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory
```

Must-apply clauses with evidence: `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Citation Freshness

Command:

```text
python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
```

Observed:

```text
No stale cross-thread citations detected.
```

## Prior Deliberations

- `DELIB-2512` - owner clarified that bridge dispatch suppression must be scoped per bridge document, not per harness. It explicitly requires active sessions not to suppress dispatch of a document for which they hold no lease, while preserving same-document lease refusal.
- `DELIB-20263189` - owner authorized the P1 dispatch/bridge-reliability package, including `WI-AUTO-SPEC-INTAKE-CA9165`, while preserving bridge GO, implementation-start, and verification gates.
- `DELIB-20263313` - Loyal Opposition GO for bounded parallel cross-harness auto-dispatch; approved replacing binary same-role active-session suppression with bounded per-role concurrency.
- `DELIB-20263956` - prior NO-GO on active-session suppression confirmed the active-session check is a heuristic and required retryable suppressed-state semantics.
- `DELIB-20265511` - owner pragmatically accepted the CA9165 per-role cap implementation as correct while waiving the per-item VERIFIED ceremony due to commit-finalization deadlock. This means the current proposal should be treated as a corrective bridge-function supersession of the post-CA9165 WI-4753 hotfix, not as reopening broad CA9165 scope.
- `bridge/gtkb-wi4753-active-session-dispatch-hotfix-006.md` - VERIFIED the incident hotfix that restored pre-spawn active-session suppression. The current owner-directed proposal explicitly supersedes that hotfix's harness-wide veto while preserving its retry-safety lessons where still applicable.

## Review Findings

No blocking findings.

## Positive Confirmations

- The proposal target paths are root-contained and limited to the live dispatcher and focused regression tests: `scripts/cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_cross_harness_trigger_suppression.py`, `platform_tests/scripts/test_bridge_dispatch_per_document_lease.py`, and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
- Mandatory applicability, clause, and citation-freshness preflights pass.
- MemBase project authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165` is active and includes `WI-AUTO-SPEC-INTAKE-CA9165`, `SPEC-INTAKE-ca9165`, and `SPEC-INTAKE-9cb2ee`.
- `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` currently shows active membership for `WI-AUTO-SPEC-INTAKE-CA9165`, even though the work item row itself is resolved pragmatically. The proposal's scope is therefore acceptable as a corrective supersession tied to owner direction, but implementation reporting should be explicit about that status.
- Current source confirms the WI-4753 veto lives exactly where the proposal says: `run_trigger` checks `check_target_active(target, state_dir)` before per-document lease filtering, records `target_active_session_present`, and skips spawning.
- Current source also confirms the safety controls the proposal preserves: per-document lease filtering, Prime work-intent acquisition/filtering, `_spawn_harness`, and `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`.
- Current tests already contain both sides of the behavior tension: older suppression tests assert `target_active_session_present`, while the lease substitution test `test_dispatch_uses_lease_not_harness_lock` asserts dispatch proceeds despite a fresh target active-session lock. The proposed verification plan correctly requires updating the former without weakening the latter.

## GO Conditions

The implementation report must prove all of the following:

1. A fresh active-session heartbeat no longer blocks eligible dispatch when no same-document lease, work-intent claim, global cap, or per-role cap blocks it.
2. Same-document per-document lease refusal remains intact.
3. Cross-document lease behavior remains intact: a lease on document X does not suppress dispatch of document Y.
4. Prime-side implementation-start remains claim-gated for GO work.
5. Per-role and global process caps still prevent unbounded headless dispatch.
6. Dispatch-state evidence distinguishes actual contention or launch failure from the removed active-session pre-spawn veto. If legacy `target_active_session_present` is retained for any lease path, the report must explain why that is compatibility-only and show how lease refusal is still diagnosable.
7. No retired smart poller, OS poller, alternate queue runtime, or bypass bridge path is restored or created.

## Required Verification

At minimum, the implementation report must include:

```text
python -m pytest platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short
ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

The report should use a project-local `--basetemp` if the host temp directory is inaccessible.

## Commands Executed

```text
Get-Content -Raw .claude/rules/project-root-boundary.md
Get-Content -Raw bridge/gtkb-disable-active-session-dispatch-suppression-001.md
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-disable-active-session-dispatch-suppression --format json --preview-lines 2000
git status --short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
python scripts/bridge_citation_freshness_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
gt deliberations search --json --limit 10 "active-session suppression per-document lease DELIB-2512"
gt deliberations get DELIB-2512 --json
gt deliberations get DELIB-20263189 --json
gt deliberations get DELIB-20263313 --json
gt deliberations get DELIB-20263956 --json
gt deliberations get DELIB-20265511 --json
gt backlog show WI-AUTO-SPEC-INTAKE-CA9165 --json
gt backlog show WI-AUTO-SPEC-INTAKE-9CB2EE --json
gt projects show PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
gt projects show-authorization PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165 --json
rg -n "check_target_active|target_active_session_present|TARGET_ACTIVE_SESSION_RESULT|per-document|lease|last_suppressed_signature|last_dispatched_signature|GTKB_MAX_LIVE_DISPATCHED_PER_ROLE|_spawn_harness|run_trigger" scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
python scripts/bridge_claim_cli.py status gtkb-disable-active-session-dispatch-suppression
python scripts/bridge_claim_cli.py claim gtkb-disable-active-session-dispatch-suppression
python .codex/skills/verify/helpers/write_verdict.py --slug gtkb-disable-active-session-dispatch-suppression --body-file .gtkb-state/bridge-drafts/gtkb-disable-active-session-dispatch-suppression-002-draft.md --no-semantic-search
```

File bridge scan contribution: 1 entry processed.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
