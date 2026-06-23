NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef0d4-5474-7af3-af31-4c8ab4cf4f7a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop heartbeat continuation; approval_policy=never
author_metadata_source: explicit heartbeat proposal metadata

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4690

# Implementation Proposal - WI-4690 Application Work-Subject Advisory Boundary

bridge_kind: prime_proposal
Document: gtkb-wi4690-application-work-subject-advisory-boundary
Version: 001 (NEW)
Date: 2026-06-23 UTC

target_paths: ["scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", ".codex/gtkb-hooks/workstream-focus.cmd", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_workstream_focus_hook_parity.py", "platform_tests/scripts/test_advisory_backlog_router.py", "scripts/advisory_backlog_router.py"]

Recommended commit type: fix

## Claim

Tighten the existing work-subject guard so an `application` work subject treats GT-KB product and ordinary GT-KB governance/rule/source mutation as read-only, while preserving the intentionally allowed cross-scope output path: a bridge `ADVISORY` entry and the existing advisory-router candidate staging flow.

The current verified work-subject implementation already blocks `application` sessions from writing GT-KB product paths, but it still allows broad `current_repo_bridge_or_governance` writes in application mode, including `.claude/rules/**`. WI-4690 narrows that allowance to the advisory/control-plane path the project work item names: application sessions may emit cross-scope platform concerns as bridge ADVISORY, then the advisory router stages them for later GT-KB disposition. Application sessions must not directly mutate GT-KB rules, platform source, formal artifacts, MemBase, or ordinary bridge implementation proposals.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-RUFF-CHECK | Yes | Keep touched Python files lint-clean. | `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_advisory_backlog_router.py scripts/advisory_backlog_router.py` | N/A |
| CQ-RUFF-FORMAT | Yes | Preserve repository formatting on touched Python files. | `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_advisory_backlog_router.py scripts/advisory_backlog_router.py` | N/A |
| CQ-FOCUSED-PYTEST | Yes | Run focused work-subject/advisory-router regression tests. | `python -m pytest platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_advisory_backlog_router.py -q --tb=short` | N/A |
| CQ-SCOPE-LIMIT | Yes | Mutate only target_paths after GO and implementation-start authorization. | `git diff --name-only` plus implementation report target-path inventory. | N/A |
| CQ-NO-FORMAL-ARTIFACT | Yes | Do not mutate GOV/SPEC/ADR/DCL/PB/REQ or groundtruth.db in this source slice. | `git status --short -- <target_paths>` and formal-artifact path absence in report. | N/A |

## First-Line Role Eligibility Check

- Resolved session role: Prime Builder, harness A, per `gt harness roles` during this heartbeat continuation.
- Status authored here: NEW.
- Eligibility result: Prime Builder is authorized to write NEW bridge proposals for snapshot-bound implementation work items.
- Pre-drafting claim: `scripts/bridge_claim_cli.py claim gtkb-wi4690-application-work-subject-advisory-boundary` succeeded for session `019ef0d4-5474-7af3-af31-4c8ab4cf4f7a`, refreshed at `2026-06-23T12:14:22Z` and expiring at `2026-06-23T12:24:22Z`.

## Project Authorization

- Project Authorization: `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23`
- Owner decision: `DELIB-20265586`
- Project: `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`
- Work Item: `WI-4690`
- Snapshot scope: WI-4690 is one of the 13 open member work items included in the 2026-06-23 snapshot authorization.
- Allowed mutation classes used by this proposal: `source`, `test_addition`, `hook_upgrade` only.
- Out of scope: formal artifact mutation, MemBase mutation, application source mutation, deployment, credential change, and new work-item creation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4690 gives the missing runtime rule directly: under `::init application`, GT-KB artifacts are read-only and the only GT-KB-directed output is a bridge ADVISORY routed later into a GT-KB candidate work item plus Deliberation Archive record. The existing work-subject foundation and advisory router provide enough specified substrate for a narrow enforcement slice. No new ADR, DCL, GOV, SPEC, PB, or REQ mutation is proposed here.

## Current Behavior

- `scripts/workstream_focus.py` classifies `.claude/rules/**`, `.claude/hooks/**`, `.codex/**`, `bridge/**`, `memory/**`, `groundtruth.db`, and related surfaces as `current_repo_bridge_or_governance`.
- `guard_tool_use()` currently blocks cross-product writes only for `application -> gtkb_product` and `gtkb_infrastructure -> application_product`.
- The existing test `platform_tests/hooks/test_workstream_focus.py::test_application_subject_allows_current_repo_bridge_or_governance_write` explicitly asserts that `application` subject may write `.claude/rules/new-rule.md`.
- `scripts/advisory_backlog_router.py` already scans latest-status `ADVISORY` bridge threads and stages advisory candidates without directly creating open work items.

## Proposed Change

1. Add a narrow application-subject allowance for cross-scope advisory/control-plane output:
   - allow a status-bearing `bridge/*.md` write only when the candidate content is an `ADVISORY` bridge entry;
   - allow read-only operations under all current classifications;
   - allow advisory-router candidate/runtime state writes needed to stage the ADVISORY for later GT-KB handling.
2. Block application-subject writes to ordinary GT-KB governance/control-plane targets that are not the advisory channel, including `.claude/rules/**`, `.claude/hooks/**`, `.codex/**`, `groundtruth.db`, `memory/**`, and non-ADVISORY bridge implementation/review/report files.
3. Preserve GT-KB-subject behavior: GT-KB sessions continue to use bridge/governance surfaces normally and continue to block application-product mutations unless the work subject is switched to application.
4. Preserve the existing advisory router; only add tests or small parser hardening if the current router lacks coverage for bridge ADVISORY staging.
5. Keep application-specific naming parameterized. Do not hardcode Agent Red beyond existing compatibility aliases already present in work-subject command handling.

## Specification Links

- `DELIB-20265586` - owner approval for the snapshot-bound project implementation authorization used by this proposal.
- `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23` - active bounded authorization including WI-4690 and allowing source/test/hook updates.
- `WI-4690` - requires application write-isolation under `::init application` plus cross-scope advisory channel.
- `bridge/gtkb-envelope-disposition-autonomous-dispatch-advisory-001.md` - program advisory naming WI-4690 as application write-isolation plus cross-scope advisory channel.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - applications are isolated execution contexts with separate lifecycle authority from GT-KB platform artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - adopter application boundary is under the GT-KB root's applications directory; proposal keeps all active GT-KB files in-root and avoids application source mutation.
- `ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001` - workspace identity is default GT-KB platform with explicit hosted-application/application exception; the guard must honor the binary subject boundary rather than infer from paths alone.
- `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` - platform guard behavior must remain adopter-agnostic and parameterized.
- `DCL-ADVISORY-ROUTING-001` - ADVISORY entries route via Axis 2/advisory surfaces rather than ordinary dispatch actionability; this proposal preserves ADVISORY as the cross-scope platform output path.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - activity disposition profiles declare which objects the session manipulates; application mode must not manipulate GT-KB platform artifacts directly.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` - activity routing stays on existing GT-KB service surfaces; this proposal does not add a new service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state must remain status-bearing and governed; this proposal does not create alternate queues.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant implementation constraints and project metadata.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - required `Project Authorization`, `Project`, and `Work Item` metadata lines are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute spec-derived tests mapped below.
- `GOV-CODE-QUALITY-BASELINE-001` - touched Python and hook surfaces must pass repo-native ruff and format checks.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - cross-scope platform concerns raised during application work are preserved as governed advisory candidates, not silent direct mutations.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved from work item to proposal to implementation report and tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory candidate lifecycle state remains staged/promoted/rejected rather than bypassed.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test or command | Expected evidence |
|---|---|---|
| WI-4690 application write-isolation | New/updated `platform_tests/hooks/test_workstream_focus.py` tests for application subject blocking `.claude/rules/**`, `.claude/hooks/**`, `.codex/**`, `groundtruth.db`, and non-ADVISORY `bridge/*.md` writes | Guard returns `decision=block` with application-subject reason and points to bridge ADVISORY or GT-KB work-subject switch |
| WI-4690 cross-scope advisory channel | New/updated `platform_tests/hooks/test_workstream_focus.py` test allowing `bridge/<slug>-001.md` only when the Write payload content starts with `ADVISORY` and contains `bridge_kind: loyal_opposition_advisory` or equivalent advisory metadata | Guard returns `{}` for ADVISORY-shaped bridge output in application mode |
| `DCL-ADVISORY-ROUTING-001` | `platform_tests/scripts/test_advisory_backlog_router.py` bridge-source regression, if not already present, proving latest `ADVISORY` bridge thread is staged as a candidate and not auto-promoted to a work item | Router result has staged candidate with `source='bridge'`; work-item count remains zero |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` + `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Existing and updated `platform_tests/hooks/test_workstream_focus.py` root-classification and cross-product guard tests | Application product writes remain allowed under application subject; GT-KB product writes remain blocked |
| `ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001` + `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` | Existing `test_startup_gate_init_keyword_sets_app_scope` plus guard tests avoiding hardcoded adopter-specific behavior | `::init agent_red` compatibility still sets application subject, but guard logic is subject/category based |
| Hook parity | `platform_tests/scripts/test_workstream_focus_hook_parity.py` and existing hook wrapper smoke tests | Claude/Codex workstream-focus wrappers still delegate to the shared module |
| Code quality | `python -m ruff check <touched files>` and `python -m ruff format --check <touched files>` | No lint or formatting regressions |

Minimum verification commands after implementation:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_advisory_backlog_router.py -q --tb=short --basetemp .gtkb-state\pytest-tmp-wi4690-application-advisory-boundary
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\workstream_focus.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_advisory_backlog_router.py scripts\advisory_backlog_router.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\workstream_focus.py platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_advisory_backlog_router.py scripts\advisory_backlog_router.py
```

## Applicability And Clause Preflight Self-Check

- Read `config/governance/spec-applicability.toml` before filing.
- Expected required trigger coverage: `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` are cited above.
- Expected advisory trigger coverage: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` are cited above.
- Clause evidence: all target paths are in-root; the proposal has concrete spec links; the verification plan maps specs to tests; bridge authority remains the canonical state surface.

## Prior Deliberations

- `DELIB-20265586` - owner selected the snapshot-bound project implementation authorization used by this proposal.
- `DELIB-20265287` - owner decision set for the envelope disposition and autonomous dispatch program, including application write-isolation/advisory-channel work.
- `DELIB-20260621` - activity disposition profile framing: profile direction declares which objects the session manipulates.
- `DELIB-20265219`, `DELIB-20265220`, `DELIB-20265227` - Agent Red readiness/application-isolation governance foundation leading to `ADR-APPLICATION-ISOLATION-CONTRACT-001`.
- `bridge/gtkb-work-subject-root-enforcement-implementation-020.md` - VERIFIED work-subject/root enforcement foundation; this proposal narrows the remaining application-mode governance allowance rather than reopening the foundation.
- `bridge/agent-disposition-wi4589-external-mutation-gate-slice1-006.md` - related external-mutation gate recovery thread; content evidence is useful, but finalization remains separately NO-GO and this proposal does not depend on that thread reaching VERIFIED.
- `bridge/gtkb-envelope-disposition-autonomous-dispatch-advisory-001.md` - program advisory listing WI-4690 and its intended boundary.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner input required. The proposal stays within the active snapshot PAUTH and does not mutate formal artifacts. If Loyal Opposition concludes the phrase "only GT-KB-directed output is a bridge ADVISORY" should permit more than ADVISORY/control-plane staging, that would be a requirement-disambiguation NO-GO rather than an implementation change under this proposal.

## Risks And Mitigations

- Risk: blocking too much control-plane output could impair bridge protocol use during application sessions. Mitigation: explicitly allow ADVISORY-shaped bridge output and advisory candidate staging, and keep GT-KB-subject bridge/governance behavior unchanged.
- Risk: bridge Write payloads from different harnesses may expose content under different keys. Mitigation: tests should cover the hook payload shapes used by current Write/Bash adapters and fail closed for mutating shell commands where candidate content cannot be inspected.
- Risk: broad `.codex/**` or `.claude/**` blocking could interfere with harmless cache writes. Mitigation: only mutating tool writes are guarded; read-only startup relay cache reads remain separately permitted by the startup relay cache logic.
