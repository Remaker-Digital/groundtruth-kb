NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T16-11Z
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation session; Prime Builder; automation_id=keep-working

# Implementation Report - Align Startup MemBase Scope Filter Naming

bridge_kind: implementation_report
Document: gtkb-startup-membase-scope-filter-naming
Version: 003
Responds-To: bridge/gtkb-startup-membase-scope-filter-naming-002.md
Proposal: bridge/gtkb-startup-membase-scope-filter-naming-001.md
GO: bridge/gtkb-startup-membase-scope-filter-naming-002.md

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3466

## Implementation Claim

Implemented WI-3466 by replacing the misleading Agent Red-named dashboard-scope selector in `scripts/session_self_initialization.py` with neutral, subject-aware dashboard-scope selectors.

The implementation now:

- uses `APPLICATION_DASHBOARD_SCOPE_INCLUDED` / `APPLICATION_DASHBOARD_PRIMARY_SCOPE_INCLUDED` for application-subject metrics;
- uses `GTKB_DASHBOARD_SCOPE_INCLUDED` / `GTKB_DASHBOARD_PRIMARY_SCOPE_INCLUDED` for GT-KB infrastructure metrics;
- routes `_database_metrics()`, `_backlog_metrics()`, `_bridge_metrics()`, and historical dashboard backfill through the subject-aware selector;
- reports `scope.included_scopes` instead of `scope.excluded_scopes` so the metric packet states what was counted;
- adds tests proving GT-KB subject metrics count GT-KB-scoped rows and application subject metrics count Agent Red-scoped rows;
- updates stale tests to use status-bearing numbered bridge files instead of `bridge/INDEX.md` as live authority.

No formal GOV/SPEC/ADR/DCL mutation, MemBase mutation, deployment, credential work, external service action, or Agent Red application-source change was performed.

## Files Changed

Scoped WI-3466 changes:

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`

The worktree also contains unrelated pre-existing dirty/staged/untracked files from other bridge threads, including WI-4639 verdict-seeding work and `bridge/gtkb-harness-hook-path-cwd-robustness-002.md`. Those files are not part of this implementation report and were not staged for this WI.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed through the governed numbered bridge chain.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup disclosure and reports must present current operating state accurately for the active work subject.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - Prime Builder startup disclosure must be understandable and must not preserve misleading role/work-subject labels.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - startup/dashboard KPI surfaces remain tied to the live project dashboard contract.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - the implementation avoids new subprocess, semantic search, or full-database passes.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red remains an adopter/application scope, not the owner of GT-KB infrastructure metrics.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - changed files are in-root under `E:/GT-KB` and within the approved target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation used the active May29 Hygiene project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation waited for LO GO plus a live implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation remains tied to the proposal's linked specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence below maps linked specifications to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-3466 is governed backlog work under the active May29 Hygiene project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item, proposal, implementation, tests, and report preserve the traceable artifact lifecycle.

## Spec-Derived Verification

| Specification / governing surface | Verification command or evidence | Observed result |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short` | PASS: 72 passed in 213.81s. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | New tests `test_database_metrics_gtkb_subject_counts_gtkb_scoped_rows` and `test_database_metrics_application_subject_counts_agent_red_rows` in `platform_tests/scripts/test_session_self_initialization.py`. | PASS as part of the 72-test module run; GT-KB subject counts `gtkb_framework` / `gtkb_upstream`, application subject counts Agent Red scopes. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Diff review of `scripts/session_self_initialization.py`. | PASS: selector changes reuse existing in-memory payload rows and do not add new subprocesses, semantic search, or database passes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The report is filed as `bridge/gtkb-startup-membase-scope-filter-naming-003.md` through the bridge helper. | Pending helper write at report filing time; numbered bridge chain preserved. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-membase-scope-filter-naming` | PASS: packet hash `sha256:eb34e67f70aba8e26e0a323fdc8c36f3992efbbe06471f625ad739eede497667`; targets match this implementation. |
| Python quality gates | `python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py` | PASS: All checks passed. |
| Python formatting gate | `python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py` | PASS: 3 files already formatted. |

Additional executed verification:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k database_metrics
```

Observed result: PASS, 2 passed and 70 deselected in 0.72s.

```text
python -m pytest platform_tests/scripts/test_session_self_initialization_disclosure_shape.py -q --tb=short
```

Observed result: PASS, 15 passed in 70.34s.

## Acceptance Criteria

- GT-KB startup MemBase work-item metrics no longer use Agent Red-specific helper, constant, or local variable names for generic dashboard-scope filtering.
- Startup metrics are subject-aware: GT-KB infrastructure subject counts GT-KB-scoped rows; application subject counts Agent Red rows.
- Agent Red remains an adopter/application scope and does not drive GT-KB infrastructure metrics.
- Current test fixtures use the live numbered bridge-file authority where they inspect bridge latest status.
- No out-of-scope formal artifact, MemBase, deployment, external-service, or application mutation occurred.

## Risk / Rollback

Risk is moderate because the implementation changes the selector from fixed Agent Red scopes to subject-aware scopes. Focused tests cover both subject modes, and the full startup module tests plus disclosure-shape tests passed.

Rollback is a normal git revert of the implementation commit and this implementation report. No data migration or external state change is involved.

## Recommended Commit Type

Recommended commit type: `refactor:`

refactor: the primary change is a behavior-preserving/subject-aligning naming cleanup for startup metric scope selection, with focused regression tests guarding the subject semantics.
