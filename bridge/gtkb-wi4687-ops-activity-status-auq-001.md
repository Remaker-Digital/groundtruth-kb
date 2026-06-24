NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eed3f-0ee1-7dc1-aa36-4241c0a96b37
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder session; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4687
bridge_kind: prime_proposal

# Implementation Proposal - WI-4687 Ops Activity Status And AUQ Option Surface

Document: gtkb-wi4687-ops-activity-status-auq
Version: 001
Date: 2026-06-24 UTC
Author Role: Prime Builder
Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4687
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/activity/ops.py", "groundtruth-kb/src/groundtruth_kb/session/topic_router.py", "platform_tests/scripts/test_ops_activity_context.py", "platform_tests/scripts/test_session_envelope_runtime.py"]

## First-Line Role Eligibility Check

Resolved session role: Prime Builder. Status authored by this file: `NEW`.
Prime Builder is authorized to author a `NEW` implementation proposal and is
not authoring a Loyal Opposition status token.

Required work-intent claim acquired before substantive drafting:

- `thread_slug`: `gtkb-wi4687-ops-activity-status-auq`
- `acting_role`: `prime-builder`
- `session_id`: `019eed3f-0ee1-7dc1-aa36-4241c0a96b37`
- `acquired_at`: `2026-06-24T00:30:05Z`
- `ttl_expires_at`: `2026-06-24T00:40:05Z`

## Summary

Implement the substantive `ops` activity surface that was deliberately left as
a stub by WI-4683. When `::open ops` is accepted, the topic context should
include a deterministic operations snapshot and a prioritized AUQ option list
covering the owner-approved choices: apply patch, increase scale threshold,
approve operational change, triage support, and evaluate feedback.

The implementation remains platform-side and report-only. It does not call
external deployment/support systems, does not ask the owner an AUQ directly,
and does not mutate application files. It reads known in-root operational
surfaces when present, reports unavailable/missing sources explicitly, and
emits the option list as operator context for the interactive owner or as a
headless report.

## Requirement Sufficiency

Existing requirements are sufficient for this source/test slice. WI-4687 states
the required behavior: `::open ops` acquires deployed-application status
signals (health, scale, support cases, user activity, ops feedback), applies
decision criteria, and emits prioritized AUQ options. `DCL-TOPIC-ENVELOPE-
ROUTING-001` v2 explicitly defers the substantive `ops` handler to WI-4687,
and `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` / `DCL-ACTIVITY-DISPOSITION-
PROFILE-001` define `ops` as an interactive-primary activity. No new owner
input, formal artifact mutation, project membership change, or adopter-specific
requirement is needed to implement the deterministic report surface.

## Scope

1. Add `groundtruth_kb.activity.ops` as the deterministic ops-activity
   renderer.
2. Have the renderer inspect only in-root, optional operational surfaces such
   as dashboard/session-startup data, release-readiness notes, bridge/dispatch
   health summaries if available, and existing ops feedback artifacts if
   present. Missing files become explicit "unavailable" evidence, not errors.
3. Derive a stable prioritized AUQ option list from the observed signals,
   always using the approved option vocabulary:
   - apply patch
   - increase scale threshold
   - approve operational change
   - triage support
   - evaluate feedback
4. Append the rendered ops activity section to `render_topic_context(...)` only
   for accepted `::open ops` commands.
5. Preserve the existing `::open ops` route target and preload stub from
   WI-4683; this proposal enriches the operator context, not the parser
   vocabulary.

## Non-Scope

- No changes to `config/agent-control/activity-disposition-profiles.toml`;
  WI-4730 owns the owner-refined per-activity profile details.
- No `applications/` mutation.
- No external API/network calls to hosting, support, analytics, or feedback
  systems.
- No real AskUserQuestion creation; the AUQ choices are emitted as report text
  for the operator to act on.
- No single-active/bare-close behavior; WI-4685 owns that reconciliation.
- No formal GOV/SPEC/ADR/DCL/PB/REQ mutation.
- No deployment, scaling action, support-ticket action, or release approval.

## Proposed Implementation

1. Create `groundtruth-kb/src/groundtruth_kb/activity/ops.py` with:
   - a small immutable snapshot model or plain dict shape,
   - fail-soft readers for known in-root operational files,
   - deterministic signal classification for health, scale, support, user
     activity, and ops feedback,
   - `render_ops_activity_context(project_root: Path) -> str`.
2. In `groundtruth-kb/src/groundtruth_kb/session/topic_router.py`, call the ops
   renderer from `render_topic_context(...)` only when `result["action"] ==
   "open"` and `result["topic_type"] == "ops"`. Exceptions render an
   unavailable section instead of blocking `::open ops`.
3. Add focused tests proving:
   - `::open ops` context includes the operations snapshot and option list,
   - missing operational files are reported explicitly and do not block open,
   - non-ops topic opens do not include the ops section,
   - close commands do not include the ops section,
   - the option vocabulary and order remain stable.

## Specification Links

- `DCL-TOPIC-ENVELOPE-ROUTING-001` v2: declares the `ops` route as operations
  status-and-decision surface and defers the substantive handler to WI-4687.
- `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2: defines the accepted `::open ops` /
  `::close ops` command surface that this proposal enriches without changing
  grammar.
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`: defines per-activity disposition
  profiles and identifies `ops` as situational awareness leading to prioritized
  action.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`: requires every activity, including
  `ops`, to carry the four-class profile and identifies `ops` as
  interactive-primary.
- `DCL-SESSION-ENVELOPE-DURABILITY-001`: topic-envelope context must remain
  session-envelope scoped and durable-file friendly.
- `ADR-ENVELOPE-META-MODEL-001` and `DCL-ENVELOPE-META-MODEL-001`: this
  enriches the topic/activity intent context without adding an envelope leg.
- `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001` and
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: implementation must remain
  platform-side and must not hardcode an adopter application.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: WI-4687 is within the
  snapshot-bound PAUTH cited above; future work items remain outside scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: implementation must wait for Loyal
  Opposition GO and implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: this proposal includes
  Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: concrete
  specification links are listed here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the post-implementation
  report must include executed spec-derived tests.
- `GOV-CODE-QUALITY-BASELINE-001`: implementation must satisfy scoped pytest,
  ruff check, and ruff format check.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: owner decisions and formal artifacts
  remain out of this source/test slice unless separately approved.

## Prior Deliberations

- `DELIB-20265586`: active owner decision authorizing snapshot-bound project
  implementation for the 13 open member WIs, including WI-4687.
- `DELIB-20265287`: program-level activity-envelope disposition and autonomous
  dispatch decision; F1 re-admits `ops` and defines the deployed-app status,
  decision-criteria, and prioritized AUQ option shape.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME`: DEC-4 locks the
  six-member activity set and provides the disposition-profile context model.
- `DELIB-20260638`: major-release envelope program context; superseded for the
  vocabulary count by the later six-member decision but still relevant to the
  envelope program.
- `bridge/gtkb-wi4683-router-runtime-six-member-vocabulary-004.md`: verifies
  the six-member runtime vocabulary and explicitly preserves WI-4687's handler
  boundary.
- `bridge/gtkb-wi4683-activity-vocabulary-reconcile-ops-006.md`: GO for the
  formal router vocabulary amendment, with `ops` handler deferred to WI-4687.

Deliberation searches run while drafting:

- `gt deliberations search "WI-4687 ops activity deployed application status AUQ decision criteria" --limit 10`
- `gt deliberations search "WI-4685 single-active activity envelope close open one active" --limit 10`

Search candidates were reviewed. The retained items above are the directly
relevant owner decisions and predecessor bridge records.

## Owner Decisions / Input

No new owner decision is required for this proposal. The implementation emits
prioritized AUQ option text, but it does not itself make an owner-only
operational decision, ask an AUQ, approve a deployment, increase capacity, or
triage a support case.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQB-1 Targeted scope | Yes | Keep changes to the ops renderer, topic context integration, and focused tests. | `git diff -- groundtruth-kb/src/groundtruth_kb/activity/ops.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py platform_tests/scripts/test_ops_activity_context.py platform_tests/scripts/test_session_envelope_runtime.py` | N/A |
| CQB-2 Spec-derived behavior | Yes | Tests derive from WI-4687, DCL routing v2, and the activity disposition DCL. | Focused pytest commands below. | N/A |
| CQB-3 Deterministic tests | Yes | Use temp project roots and in-root fixture files; no network or external services. | Focused pytest commands below. | N/A |
| CQB-4 Formatting and lint | Yes | Keep Python ruff-clean and formatted. | Ruff commands below. | N/A |
| CQB-5 No credentials/destructive actions | Yes | Read-only optional in-root files; no credentials, deletion, deployment, or external actions. | Code review plus tests. | N/A |
| CQB-6 Backward compatibility | Yes | Preserve non-ops topic rendering, close rendering, parser grammar, and WI-4685/WI-4730 boundaries. | Existing session-envelope tests plus new focused tests. | N/A |

## Spec-Derived Verification Plan

| Spec / requirement | Derived implementation check | Test / command |
| --- | --- | --- |
| WI-4687 / `DCL-TOPIC-ENVELOPE-ROUTING-001` v2 | `::open ops` renders operations status and decision surface, not just the route stub. | `python -m pytest platform_tests/scripts/test_ops_activity_context.py -q --tb=short` |
| DELIB-20265287 F1 | The emitted option vocabulary includes apply patch, increase scale threshold, approve operational change, triage support, and evaluate feedback in deterministic priority order. | `python -m pytest platform_tests/scripts/test_ops_activity_context.py -q --tb=short` |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | `ops` remains interactive-primary/report-only; implementation emits context, not a hard gate or automatic owner decision. | Focused tests plus code review. |
| `SPEC-TOPIC-ENVELOPE-ROUTER-001` v2 | Parser grammar and six-member vocabulary stay unchanged. | `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_wrapup_trigger_dispatch.py -q --tb=short` |
| Platform/application nonspecificity specs | No `applications/` files touched and no adopter names hardcoded in the ops renderer. | `rg -n "Agent Red|applications/" groundtruth-kb/src/groundtruth_kb/activity/ops.py groundtruth-kb/src/groundtruth_kb/session/topic_router.py` expected no adopter-specific implementation references. |
| `GOV-CODE-QUALITY-BASELINE-001` | Touched files are linted and format-checked. | `python -m ruff check ...`; `python -m ruff format --check ...` on target paths. |

## Implementation Start Gate

After Loyal Opposition GO, Prime Builder must run:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4687-ops-activity-status-auq
```

No protected source/test mutation will occur before GO and the implementation
start packet.

## Pre-Filing Preflight Subsection

Content-file preflights were run against this completed draft before live
filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4687-ops-activity-status-auq --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4687-ops-activity-status-auq-001.md --json`
- Result: `preflight_passed: true`, packet `sha256:9083a292822205ffca33e3be260be79e79017f8ea732d913c848aedbff5050fc`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4687-ops-activity-status-auq --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4687-ops-activity-status-auq-001.md`
- Result: clauses evaluated: 5, `must_apply: 3`, evidence gaps in must-apply clauses: 0, blocking gaps: 0.

The live bridge helper must also pass its credential, author-metadata,
bridge-compliance, and work-intent gates before writing
`bridge/gtkb-wi4687-ops-activity-status-auq-001.md`.

## Risk Notes

- The main behavioral risk is overstating operational knowledge. Mitigation:
  report source availability and missing data explicitly; do not infer live
  external service state from absent files.
- Another risk is accidentally creating an owner-decision path. Mitigation:
  emit AUQ option text only; do not call AskUserQuestion or mutate decision
  records.
- The `ops` profile details remain intentionally seed-level until WI-4730.
  Mitigation: do not modify profile config in this slice.
