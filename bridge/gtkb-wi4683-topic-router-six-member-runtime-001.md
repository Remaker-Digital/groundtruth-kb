NEW

# WI-4683 Runtime Reconciliation: Six-Member Topic-Envelope Vocabulary

bridge_kind: prime_proposal
Document: gtkb-wi4683-topic-router-six-member-runtime
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eed3f-0ee1-7dc1-aa36-4241c0a96b37
author_model: GPT-5 Codex
author_model_version: codex-session
author_model_configuration: Codex desktop; approval_policy=never; workspace=E:\GT-KB; active role=prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4683

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_wrapup_trigger_dispatch.py"]

implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the source/test follow-on for `WI-4683` after the formal router amendments landed. `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 now define the closed six-member vocabulary `{ops, deliberation, build, test, spec, project}`, but the strict runtime parser and session envelope maps still carry the older five-member set.

This proposal changes only the runtime vocabulary surface and focused regression tests: add `ops` to `TOPIC_TYPES`, `TOPIC_COMMAND_RE`, `ROUTE_TARGETS`, and `PRELOAD_STATES`; assert `::open ops` and `::close ops` are accepted while unsupported topic types remain rejected; and assert the hook-side parser recognizes the same command surface. The substantive `ops` handler remains deferred to `WI-4687`; this slice routes `ops` to the existing operations/status surface as the v2 DCL stub requires.

## Specification Links

- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 - defines `::open <type>` and typed `::close <type>` over the closed six-member vocabulary including `ops`.
- `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 - requires the router dispatch map and typed-close grammar to include `ops`, with the substantive per-type `ops` handler deferred to `WI-4687`.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - already defines the canonical six activities and makes `ops` one of the profile-bearing activity names.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` - records the closed-but-extensible six-member activity vocabulary and the disposition-profile framing this runtime must align with.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization is owner evidence but does not replace bridge GO, target-path scoping, implementation-start authorization, implementation reporting, or Loyal Opposition verification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal uses an append-only status-bearing bridge thread and requires Loyal Opposition `GO` before source/test mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal links the source/test change to concrete governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries `Project Authorization`, `Project`, and `Work Item` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map the change to spec-derived tests and observed command results.
- `GOV-STANDING-BACKLOG-001` - `WI-4683` remains a MemBase project work item in the active project backlog and is driven through the project/WI loop.
- Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` shape the evidence and follow-on handling but do not add source targets.

## Prior Deliberations

- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - DEC-4 locks the six-member activity vocabulary including `ops`.
- `DELIB-20265287` - D10 classifies the activity-vocabulary drift as a defect and F1 re-admits `ops` while deferring the substantive `ops` activity handler to `WI-4687`.
- `DELIB-20260638` - earlier five-member topic-envelope content goal, now superseded for vocabulary count by `DELIB-20260621` DEC-4 and the v2 router specs.
- `DELIB-20260698` and `DELIB-20261272` - prior Loyal Opposition NO-GO reviews that correctly blocked source/test reconciliation before the formal router specs were amended.
- `DELIB-20260697`, `DELIB-20261271`, and `DELIB-20261797` - prior GO records for the original topic-envelope router spec/DCL lineage.
- `bridge/gtkb-wi4683-activity-vocabulary-reconcile-ops-006.md` - GO for the governance-review predecessor, limited to drafting and downstream owner-ratified formal amendments; it explicitly required a separate source/test bridge after v2 rows were live.

## Owner Decisions / Input

No new owner decision is required for this source/test bridge. The substantive vocabulary decision is already owner-ratified by `DELIB-20260621` DEC-4 and `DELIB-20265287` F1, the project-wide implementation authorization is `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23` (`DELIB-20265586`), and the two formal router amendments were owner-ratified on 2026-06-22 with approval packets:

- `.groundtruth/formal-artifact-approvals/2026-06-22-SPEC-TOPIC-ENVELOPE-ROUTER-001-v2.json`
- `.groundtruth/formal-artifact-approvals/2026-06-22-DCL-TOPIC-ENVELOPE-ROUTING-001-v2.json`

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 and `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 are live in MemBase, both at `status=specified`, and they explicitly require the six-member vocabulary and typed-close grammar. This bridge performs the source/test reconciliation those specs intentionally left expected-failing until the code follow-on landed. No formal artifact, MemBase mutation, project mutation, production deployment, credential lifecycle change, destructive cleanup, or out-of-root work is in scope.

## Preflight Evidence

Applicability preflight on the pending draft passed:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4683-topic-router-six-member-runtime --content-file .gtkb-state/propose-drafts/gtkb-wi4683-topic-router-six-member-runtime-001.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:6c4da30473a3d7a43947602ea989c3b239daebc76d5407e2378d0f793635e483
```

Clause preflight on the pending draft passed:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4683-topic-router-six-member-runtime --content-file .gtkb-state/propose-drafts/gtkb-wi4683-topic-router-six-member-runtime-001.md
must_apply: 4
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

Phantom-spec sweep checked 13 cited formal artifact ids against `gt spec show ... --json`; all resolved: `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ACTIVITY-DISPOSITION-PROFILE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-TOPIC-ENVELOPE-ROUTING-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-STANDING-BACKLOG-001`, and `SPEC-TOPIC-ENVELOPE-ROUTER-001`.

## Spec-Derived Verification Plan

| Specification | Source/test obligation | Verification command | Expected result |
|---|---|---|---|
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 | `parse_topic_command` accepts `::open ops` and `::close ops`; unsupported/bare/malformed commands remain rejected. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --no-header` | Focused tests pass, including new `ops` parser assertions. |
| `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 | `TOPIC_TYPES`, route targets, preload states, and typed-close regex expose exactly the six-member set with an `ops` stub route to the existing operations/status surface. | Same focused pytest command plus source inspection in the implementation report. | Tests prove `open_topic(..., "ops")` records route/preload data and `close_topic(..., "ops")` closes it; source inspection shows the six-member regex. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Runtime topic vocabulary aligns with the profile vocabulary that already includes `ops`. | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_activity_disposition_profiles.py platform_tests/scripts/test_session_envelope_runtime.py -q --no-header` | Existing profile tests remain green and the session runtime accepts the same activity name. |
| Bridge/governance specs | Proposal, implementation start, target paths, implementation report, and LO verification remain append-only and target-scoped. | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4683-topic-router-six-member-runtime`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4683-topic-router-six-member-runtime`; implementation-start packet after GO. | Preflights pass with no missing required specs or blocking gaps; impl-start packet authorizes only the listed target paths. |
| Repo quality floor | Touched Python files are formatted/linted. | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/topic_router.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py`; `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check ...same files...` | Ruff check and format check pass for touched files. |

## Risk / Rollback

Risk is low and localized to strict topic command parsing and session-envelope topic metadata. The main behavioral change is that `::open ops` and `::close ops` move from rejected to accepted with a stub route; `WI-4687` still owns the real operations activity behavior. Rollback is a single git revert of the implementation commit, restoring the five-member runtime set while leaving the already-approved v2 specs as evidence of the desired state.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4683-topic-router-six-member-runtime`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - this corrects source/spec drift by reconciling the runtime topic-envelope vocabulary to the already-approved six-member specification.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
