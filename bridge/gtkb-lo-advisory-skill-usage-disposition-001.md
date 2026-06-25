NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de8db3b1-a4a6-4be0-9f51-65b8d31e1299
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; WI-3330 advisory disposition

bridge_kind: governance_advisory
Document: gtkb-lo-advisory-skill-usage-disposition
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-24 UTC
Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3330
Source Advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md
target_paths: ["bridge/gtkb-lo-advisory-skill-usage-disposition-001.md"]
allowed_mutation_classes: ["scaffold_update"]
implementation_scope: advisory_disposition_monitor
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Prime Builder Disposition - Skill Usage / Activation Advisory (WI-3330)

## Summary

Prime Builder classifies WI-3330 as **`monitor`**.

The source advisory proposes a deterministic skill-usage router (a `skill_usage_router.py` / `gt skills suggest` surface with scenario-trigger registry metadata) plus bridge-shape preflights. The advisory's own "Owner Decision Needed" is `None`; it proposes a future implementation track and asks only that a later proposal choose an enforcement target. Honesty note: the advisory's headline deliverable (the router) is genuinely NOT built today (no spec, no script, no work item), so this is not an `adopted_covered` close. It is classified `monitor`: preserved as a future-work seed without committing the heavy router build into this routing WI. If the owner wants the router pursued, that belongs in a separate new project, not folded into this disposition.

This routing artifact performs no source, test, database, formal-artifact, project, work-item, release, deployment, or credential change. It asks Loyal Opposition to review only the classification and precedence evidence; `requires_verification` is false because the bridge GO is terminal for this advisory routing.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v2 (verified) - this disposition is filed through the bridge; Prime Builder requests review only and authors no Loyal Opposition verdict.
- `DCL-ADVISORY-ROUTING-001` - ADVISORY/LO-advisory input is routed to a Prime Builder disposition; this proposal records that classification.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - the source report is advisory input, not direct implementation approval.
- `GOV-STANDING-BACKLOG-001` - this is a governed backlog-routing item; the proposal performs no bulk backlog change and creates no new project work item.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - this proposal carries Project Authorization, Project, and Work Item metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) - the snapshot-bound PAUTH is cited for the project-retirement workflow; this disposition requests no protected implementation work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - any future implementation proposal derived from this advisory must carry concrete spec links and cannot treat this disposition as source authority.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - no implementation report is requested here; if future implementation occurs, verification must be spec-derived.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this routing artifact preserves the source advisory as durable prior art while avoiding duplicate work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) - all referenced live artifacts remain under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` and `.claude/rules/peer-solution-advisory-loop.md` - this follows the bridge lifecycle and the advisory disposition vocabulary.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`.
- Project: `PROJECT-GTKB-LO-ADVISORY-ROUTING`.
- Work item: `WI-3330`.
- Snapshot scope: WI-3330 is in the PAUTH's included work item IDs.
- Changes requested by this disposition: only this bridge routing artifact.
- Changes explicitly not requested: source, tests, hooks, CLI, generated dashboards, MemBase work-item resolution, formal artifacts, release/deployment, credential changes, and new project work items.

## Owner Decisions / Input

- `DELIB-20265586`: Owner authorized bounded implementation for the project's snapshot member work items while preserving the ACID-invariant for any future new project items.
- Owner AskUserQuestion (2026-06-24, this session): owner directed Prime Builder (Claude, harness B) to file dispositions for the un-owned advisory-routing work items.

No new owner decision is required for this monitor disposition. A future skill-router implementation would require fresh owner prioritization and its own bridge proposal/project.

## Requirement Sufficiency

Existing requirements sufficient.

The existing advisory-routing rules, the PAUTH, the source advisory, and the cited coverage/precedence evidence are sufficient to classify WI-3330 as `monitor`. No new or revised requirement is needed because this disposition declines new implementation under this routing WI and preserves, rather than expands, the source concern.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md` - source advisory; its own owner-decision is `None`.
- `.claude/rules/file-bridge-protocol.md` - records the already-shipped bridge-shape enforcement (preflights, claim CLI, implementation-start gate, compliance hook) that blunts the advisory's worst failure class.
- _No prior deliberation found on a skill-usage router itself; the router is genuinely unbuilt._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Coverage And Precedence Check

| Source advisory theme | Current routing conclusion |
|---|---|
| Bridge proposal-shape / target_paths / verdict-structure defects keep recurring. | Already mechanically gated: `scripts/bridge_applicability_preflight.py`, `scripts/bridge_claim_cli.py`, `scripts/implementation_authorization.py`, and `.claude/hooks/bridge-compliance-gate.py`. |
| Proposal/verdict helper skills should exist. | Present under `.claude/skills/`: `bridge-propose`, `gtkb-propose`, `send-review`, `verify`. |
| Core deliverable: a deterministic skill-usage router with trigger-scenario registry metadata. | NOT built (no spec, no `scripts/skill_usage_router.py`, no WI). Preserved as monitored future-work seed; out of scope for this routing WI. |

## Disposition

Prime Builder selects `monitor`.

- The advisory is preserved as prior art / a future-work seed for a possible skill-activation-enforcement project.
- No new implementation, spec, source, or formal-artifact change follows from WI-3330 under this routing disposition.
- The bridge-shape-defect class the advisory most worried about is already mechanically gated, so the residual urgency is low.
- Any future skill-router work must cite current evidence, obtain fresh owner prioritization, and file a narrow implementation proposal in a separate project.

## Target Path Rationale

The only target path is this bridge disposition file. It is the durable routing artifact requested by the advisory loop. The proposal intentionally avoids MemBase resolution or formal-artifact change until Loyal Opposition has reviewed the classification and the project-retirement workflow has an authorized terminal-state path.

## Spec-Derived Verification Plan

For this non-implementation routing disposition, verification is evidence-based rather than test-suite based:

- `gt bridge threads --wi WI-3330` confirms this is the WI's disposition thread through work-item metadata.
- The cited coverage/precedence artifacts (specs, bridge threads, projects, and rules above) are read-only confirmable in the live checkout.
- Applicability and clause preflights pass on the operative file before a GO is recorded.

No repo-native test or ruff command is appropriate because this disposition changes no source or tests.

## Pre-Filing Preflight

- The bridge-propose helper reruns its governed credential scan, author-metadata injection, and bridge-compliance audit before writing the dispatchable numbered bridge file.
- Applicability and clause preflights are run against this operative file after filing and recorded in the verdict.

## Requested Loyal Opposition Review

Please review whether `monitor` is the correct disposition for WI-3330 given that the advisory's headline router is genuinely unbuilt but its own owner-decision is `None` and its worst failure class is already mechanically gated. A `GO` should authorize no implementation work; it should only confirm the monitor classification and the explicit "router belongs in a separate project" boundary. A `NO-GO` should identify a specific uncovered source-advisory risk that requires a narrower follow-on proposal.
