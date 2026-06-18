NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T12-10Z
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation session; Prime Builder; automation_id=keep-working

# Align Startup MemBase Scope Filter Naming

bridge_kind: prime_proposal
Document: gtkb-startup-membase-scope-filter-naming
Version: 001
Author: Codex Prime Builder automation
Date: 2026-06-18T12:10:00Z

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-3466

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_disclosure_shape.py"]

implementation_scope: source_and_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-3466 captures naming drift in the startup MemBase/dashboard-scope metric path. `scripts/session_self_initialization.py` currently renders the active work subject label as `GT-KB` for GT-KB infrastructure sessions, but the metrics feeding that label are stored in variables named `agent_red_specs`, `agent_red_work_items`, `agent_red_tests`, and `agent_red_deliberations`, using `_is_agent_red_scope()` plus `AGENT_RED_SCOPE_INCLUDED` constants.

The live classifier already distinguishes GT-KB framework/upstream rows from Agent Red product/release/operations rows. The defect is that the helper and local names still imply Agent Red ownership on a generic GT-KB startup/dashboard surface, which conflicts with the post-isolation operating model and makes future metric defects harder to reason about.

This proposal requests a narrow source/test cleanup: rename the scope helper/constants/locals to subject/dashboard-scope terminology while preserving current classification behavior, then add regression coverage proving the rendered `GT-KB open MemBase work items` line is backed by GT-KB-scoped rows and not by Agent Red-specific naming assumptions.

## Evidence

- `scripts/session_self_initialization.py:964` defines `classify_dashboard_scope()` as the current classifier.
- `scripts/session_self_initialization.py:1030` defines `_is_agent_red_scope()`, even though `classify_dashboard_scope()` returns GT-KB framework/upstream scopes as well as Agent Red scopes.
- `scripts/session_self_initialization.py:1147-1154` filters current metrics through `agent_red_*` locals before setting `membase.open_work_items`.
- `scripts/session_self_initialization.py:4489` renders the active subject label as `<subject_label> open MemBase work items`, so a GT-KB session can display `GT-KB open MemBase work items` while the backing names still say Agent Red.
- `scripts/session_self_initialization.py:516-527` defines Agent Red-named included-scope constants and a `GTKB_SCOPE_EXCLUDED` constant. The implementation should rename the inclusion constants around their current dashboard-subject purpose without silently changing the current scope sets.
- `DELIB-1084` states that startup/dashboard lifecycle behavior is GT-KB-scoped and should apply to all projects, not be preserved as Agent Red-specific behavior.

## Proposed Scope

1. Rename the misleading `_is_agent_red_scope()` helper and `AGENT_RED_*_SCOPE_INCLUDED` constants to neutral dashboard-subject names that reflect their current use.
2. Rename local variables in `_database_metrics()` and `_historical_snapshot_rows()` from `agent_red_*` to neutral scoped/visible/current-dashboard names.
3. Preserve current scope behavior unless focused tests reveal an obvious mismatch with the existing subject-label contract. This proposal is naming/clarity first, not a dashboard-scope model redesign.
4. Add or update focused tests in `platform_tests/scripts/test_session_self_initialization.py` proving GT-KB-scoped rows count under GT-KB startup labels and Agent Red product rows do not silently drive GT-KB infrastructure metrics.
5. Update disclosure-shape tests only if they reference the renamed constants/helper directly.

## Out of Scope

- No formal GOV/SPEC/ADR/DCL mutation.
- No MemBase mutation beyond the existing work item and project authorization records.
- No dashboard UI redesign, time-series storage redesign, or new scope taxonomy.
- No Agent Red application-source change.
- No change to bridge queue routing or startup focus selection.

## Files Expected To Change

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization_disclosure_shape.py` only if direct references require a rename.

All target paths are under `E:/GT-KB`. The bridge proposal, implementation report, and LO verdict files for this thread remain under `E:/GT-KB/bridge/`.

## Requirement Sufficiency

Existing requirements sufficient.

WI-3466 states the defect and options. Live code inspection shows option (a) is the least-risk repair: the filter is not genuinely Agent Red-only; it is a dashboard-scope inclusion helper whose names are vestigial. `DELIB-1084`, `GOV-SESSION-SELF-INITIALIZATION-001`, and the Agent Red conformance/isolation records already require startup/dashboard behavior to be GT-KB-scoped rather than Agent Red-unique. No new owner decision is required to rename the misleading helper/constants and add tests while preserving behavior.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not introduce credential-shaped fixture data or environment values. | Bridge helper credential scan plus diff review. | |
| CQ-PATHS-001 | Yes | Keep all changed paths inside `E:/GT-KB` and within declared target paths. | Implementation-start packet target-path validation and `git diff --name-only`. | |
| CQ-COMPLEXITY-001 | Yes | Limit changes to renames and focused test coverage; no classifier redesign. | Diff review and focused pytest. | |
| CQ-CONSTANTS-001 | Yes | Rename constants for clarity without broadening or shrinking included scope sets unless tests prove current behavior wrong. | Focused tests asserting current GT-KB/Agent Red scope behavior. | |
| CQ-SECURITY-001 | N/A | | | No auth, secret, deployment, external-service, or credential handling surface changes. |
| CQ-DOCS-001 | Yes | Bridge proposal/report carry the durable explanation; no docs-only target file planned. | LO review of proposal/report. | |
| CQ-TESTS-001 | Yes | Add focused regression coverage for GT-KB startup-label scope and Agent Red exclusion from GT-KB infrastructure metrics. | `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "scope or open MemBase or membase"` plus full focused module if selector is unstable. | |
| CQ-LOGGING-001 | N/A | | | No logging behavior is changed. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest and Ruff lint/format checks before implementation report. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal uses the governed numbered-file bridge chain and implementation waits for LO GO plus implementation-start authorization.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup disclosure and reports must present current operating state accurately for the active work subject.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - Prime Builder startup disclosure must be understandable and must not preserve misleading role/work-subject labels.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` - startup/dashboard KPI surfaces must remain tied to the live project dashboard contract.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - the repair should preserve compact startup payload behavior and avoid expensive new metric paths.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red remains a conformant adopter application, not the owner of generic GT-KB startup/dashboard mechanics.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and tests stay inside the GT-KB root and do not route unqualified GT-KB tooling evidence to Agent Red external surfaces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active May29 Hygiene PAUTH authorizes Prime Builder to advance unimplemented May29 work through bridge proposals.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass LO GO, implementation-start authorization, or verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites relevant governing specs and maps proposed tests before requesting GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward the spec-to-test mapping and observed results.
- `GOV-STANDING-BACKLOG-001` - WI-3466 is governed backlog work under the active May29 Hygiene project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the discovered naming drift is preserved as a work item and proposal rather than being corrected silently.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change maintains traceability from work item to bridge proposal, tests, report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this bridge thread is the implementation-proposal lifecycle state for WI-3466.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorized all unimplemented May29 Hygiene work items for implementation proposals.
- `DELIB-1084` - prior LO finding that startup/dashboard behavior is GT-KB-scoped and should not remain Agent Red-unique.
- `DELIB-0834` - owner decision that Agent Red is a fully conformant GT-KB-supported adopter application, not an ad hoc exception.
- `DELIB-20260618` - verified bridge history for Agent Red reference-adopter framing restoration; relevant to preserving Agent Red as adopter framing while removing vestigial owner-of-platform naming.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` is active and cites `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`.
- The current automation instruction authorizes autonomous Prime Builder work on incomplete HYGIENE project items while respecting bridge and governance gates.
- No new owner decision is required because this proposal chooses the behavior-preserving naming cleanup supported by live code evidence and prior owner decisions.

## Spec-Derived Verification Plan

| Specification / governing surface | Verification command or evidence | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge applicability preflight and numbered bridge thread inspection. | Proposal/report/verdict remain in the canonical numbered bridge chain. |
| `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Focused pytest in `platform_tests/scripts/test_session_self_initialization.py` covering rendered startup metric label and scoped MemBase count. | GT-KB startup label uses GT-KB-scoped rows after the rename; behavior remains understandable and current. |
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` | Existing dashboard/startup metric tests in the same module. | Dashboard metric payload shape remains compatible. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Diff review confirms no new subprocess, semantic search, or full-database pass beyond existing scoped-client payload processing. | Startup cost surface is unchanged. |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Regression asserts Agent Red product/release rows are not counted as GT-KB infrastructure metrics unless the existing active subject is application-scoped. | Agent Red remains an adopter/application scope, not the implicit source of GT-KB infrastructure metrics. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before implementation, `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-membase-scope-filter-naming` must succeed from the live GO. | Protected source/test edits happen only under a current packet. |
| Python quality gates | `python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py`; `python -m ruff format --check ...` | Lint and format pass for changed Python target paths. |

Expected focused verification after implementation:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short -k "scope or open MemBase or membase"
python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_self_initialization_disclosure_shape.py
```

If the pytest selector collects no tests after implementation, run the full focused module:

```text
python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short
```

## Acceptance Criteria

- GT-KB startup MemBase work-item metrics no longer use Agent Red-specific helper, constant, or local variable names for generic dashboard-scope filtering.
- Current scope classification behavior is preserved unless tests expose an existing mismatch.
- Focused tests prove GT-KB-scoped rows drive the GT-KB infrastructure metric and Agent Red rows do not silently back the GT-KB label.
- No formal artifact, MemBase, deployment, external-service, or Agent Red application mutation occurs in this slice.
- Focused pytest plus Ruff lint and format checks pass before the implementation report is filed.

## Risk / Rollback

Risk is low to moderate. The highest risk is accidentally changing the classifier semantics while performing what should be a naming cleanup. The implementation should favor alias-preserving or mechanically local renames and focused before/after tests.

Rollback is a normal git revert of the implementation commit plus a follow-up bridge report if LO identifies an unintended behavior change. Do not delete or rewrite prior bridge versions.

## Bridge Filing

This proposal is filed as `bridge/gtkb-startup-membase-scope-filter-naming-001.md`. Implementation must wait for a Loyal Opposition GO and a live implementation-start packet.

## Recommended Commit Type

refactor: the primary implementation is behavior-preserving naming cleanup with regression tests guarding the existing startup metric semantics.
