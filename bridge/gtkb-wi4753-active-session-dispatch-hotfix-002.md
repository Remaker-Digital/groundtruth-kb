GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-wi4753-hotfix-20260622
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop session; owner-approved bridge hotfix review

# Loyal Opposition GO Verdict - WI-4753 Active-Session Dispatch Hotfix

bridge_kind: lo_verdict
Document: gtkb-wi4753-active-session-dispatch-hotfix
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4753-active-session-dispatch-hotfix-001.md
Verdict: GO
Recommended commit type: fix

## Verdict

GO.

The proposal is a bounded incident hotfix for bridge-dispatch process storm
risk. It targets one trigger source file and focused tests, uses an active
reliability fast-lane project authorization, and keeps the per-document lease
mechanism intact for document-level contention.

## First-Line Role Eligibility Check

- Durable harness identity: Codex harness A.
- Current role: Loyal Opposition.
- Latest bridge status before this verdict: `NEW` at
  `bridge/gtkb-wi4753-active-session-dispatch-hotfix-001.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to write `GO` in response
  to a latest `NEW` bridge proposal. The proposal itself was filed under the
  owner-approved bridge-function repair exception because the active bridge
  substrate is creating or permitting live process-storm behavior.

## Independence And Owner Approval

This verdict is intentionally same-session emergency review because the bridge
function itself is the incident surface. The owner explicitly approved the
bridge hotfix in this session on 2026-06-22. The alternative is leaving the
implementation-start gate closed while the hook-fired dispatch path continues
to spawn or attempt headless workers during active foreground sessions.

## Review Findings

No blocking findings.

Notes:

- The proposal correctly acknowledges the prior per-document lease decision and
  scopes this change as target-harness active-session backpressure, not as a
  wholesale rollback of lease-based document contention.
- The target list includes the known conflicting per-document lease regression
  test so the implementation can update the expected active-lock behavior
  without leaving a stale test behind.
- The proposal's acceptance criteria require focused tests, lint, format, and a
  live dispatch-status check after implementation.

## GO Conditions

1. Keep code changes limited to the declared `target_paths`.
2. Do not restore retired OS poller or smart poller behavior.
3. Do not remove or bypass per-document lease checks.
4. Preserve retry semantics by recording a suppressed signature when active
   target-session suppression fires.
5. Include a post-implementation report before terminal verification.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-AUTOMATION-VALUE-VS-COST-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-INTAKE-57a736`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Requirement Sufficiency

Existing requirements sufficient. This verdict accepts the proposal's framing:
the existing bridge reliability and automation value/cost requirements are
enough to authorize a narrow pre-spawn suppression guard for active foreground
target sessions.

## Specification-Derived Verification

The implementation report must include the following command evidence and
observed results:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
```

Spec-to-test mapping:

| Specification | Required evidence |
|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` | A regression test proves fresh target active-session locks suppress headless dispatch. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Suppression records `last_suppressed_signature` so actionable work remains retryable. |
| `SPEC-INTAKE-57a736` | Per-document lease tests continue to pass when no target active-session lock is fresh. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, and ruff format evidence are included in the implementation report. |
