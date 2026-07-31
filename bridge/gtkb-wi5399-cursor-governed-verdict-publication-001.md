NEW

# WI-5399 - Contain Cursor LO effects to governed verdict publication

bridge_kind: prime_proposal
Document: gtkb-wi5399-cursor-governed-verdict-publication
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5399

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py", "scripts/verify_cursor_dispatch.py", "platform_tests/scripts/test_verify_cursor_dispatch.py", "scripts/_dispatch_wi5211_002_verdict.py", "scripts/_dispatch_wi5241_006_verdict.py", "scripts/_dispatch_wi5307_018_verdict.py", "scripts/_dispatch_wi5318_wi5316_006_verdicts.py", "scripts/_dispatch_wi5341_002_verdict.py", "scripts/_dispatch_wi5343_002_verdict.py", "scripts/_dispatch_lo_verdicts_20260717_envelope_authority.py"]

implementation_scope: Cursor LO read-only execution, governed verdict publication, and exact one-shot helper retirement
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

An auto-dispatched Cursor E Loyal Opposition worker created
`scripts/_dispatch_lo_verdicts_20260717_envelope_authority.py` while processing
bridge work. The protected helper hard-codes verdict versions and author
metadata, reads operative bridge files, and calls the low-level writer. Six
earlier one-shot verdict scripts are already tracked. This leaves protected
source residue and allows a review worker to mutate more than its selected
verdict target.

For `bridge-review` and `verification` only, run Cursor in its existing
read-only `ask` mode and require one machine-parseable verdict envelope as the
final output. The shim validates that envelope, acquires/releases the existing
runtime work-intent claim, and publishes through `publish_lo_verdict`; malformed,
ambiguous, stale, or unauthorized output fails closed without a bridge write.
GO, NO-GO, and VERIFIED remain supported, including VERIFIED include-path,
hunk-patch, and commit-message data. Ordinary Cursor routes, dispatcher
selection, eligibility, roles, caps, and process lifetimes are unchanged.

After every worker that could reference the observed helper has exited
naturally, delete the exact seven one-shot scripts listed in `target_paths`.
Do not stop a worker, disable or deprioritize Cursor, rewrite prior bridge
artifacts, or clean any unrelated path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - only the role-authorized next verdict may be published through the governed writer.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Cursor remains a dispatch consumer; the daemon retains all routing and lifecycle authority.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the existing daemon-selected prompt and audit flow remain intact.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001` - the harness cannot route, suspend, or interact with another harness.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - containment must preserve dispatchability and successful LO review behavior.
- `GOV-WORK-TREE-HYGIENE-001` - headless review must not leave protected source-side one-shot residue.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - publisher metadata comes from the validated worker session, not model-authored constants.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the observed defect, proposal, implementation report, tests, and verdict remain a traceable artifact graph.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the detected risk is preserved as WI-5399/TEST-11511 before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - filing, implementation, verification, and retirement remain distinct lifecycle transitions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every applicable governing requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, work item, and exact targets are machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent VERIFIED requires the mapped tests below.

## Prior Deliberations

- `DELIB-20265888` - harnesses are consumers of the dispatcher and do not control routing or other harnesses.
- `DELIB-20266276` - resilience work must preserve degraded continuity and dispatchability.
- `INTAKE-9d534667` - GO publication retains the required LO authority fields.
- `INTAKE-9314e628` - VERIFIED publication retains required verification and finalization fields.
- WI-5210 - provider-backed LO routes already established `PublishBridgeVerdict` as the governed publication pattern; this applies equivalent behavior to Cursor E.
- WI-4871 - Cursor VERIFIED publication must continue to use the mandatory finalization gate rather than leave terminal residue.
- WI-4778 - Cursor headless review remains a supported dispatch target; this proposal constrains effects without retiring that capability.

## Owner Decisions / Input

The owner directed that harnesses never interact directly, that all
harness/TAFE/bridge interaction use TAFE, bridge, skills, and CLI, that no
harness be disabled because of window/process defects, and that every detected
modernization defect be recorded as an `origin=hygiene` work item. The owner
also authorized the full modernization program at project scope. This proposal
does not request a routing, eligibility, role, process, credential, deployment,
release, staging, or commit change.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001`,
`DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`, and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` jointly require role-correct
governed publication without giving the review worker a broader mutation or
control-plane surface. No new formal artifact is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "Owner harness-isolation and non-dispatchability-impairment directives; WI-5399; TEST-11511; observed 2026-07-17 Cursor E source-side helper residue",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-FILE-BRIDGE-AUTHORITY-001; DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001",
  "primary_route": "TAFE-selected Cursor E review in read-only ask mode, followed by shim-owned work-intent claim and publish_lo_verdict publication through the governed bridge service",
  "before_behavior": "Cursor LO launches trusted workspace-write mode and can leave one-shot protected source helpers that hard-code and publish verdicts outside the selected bridge target.",
  "after_behavior": "Cursor LO reads and reviews without workspace source mutation, emits one strict verdict envelope, and the shim alone publishes the authorized next verdict through the canonical publisher.",
  "self_descriptive_naming": "The verdict envelope, parser, claim lifecycle, and publisher adapter use bridge-verdict publication terminology and the WI-5399 Cursor scope is explicit.",
  "obsolete_guidance_disposition": "Delete only the exact seven one-shot verdict helpers after applicable workers exit naturally; preserve their Git history and every numbered bridge artifact.",
  "history_preservation": "Prior commits, bridge chains, dispatch/session evidence, MemBase history, and worker provenance remain unchanged and queryable.",
  "baseline": {
    "tracked_one_shot_helpers": 6,
    "untracked_one_shot_helpers": 1,
    "cursor_lo_mode": "trusted default workspace-write",
    "publication_boundary": "model-created helper may call low-level bridge writer"
  },
  "expected_result": {
    "tracked_one_shot_helpers": 0,
    "untracked_one_shot_helpers": 0,
    "cursor_lo_mode": "read-only ask",
    "publication_boundary": "strict envelope plus publish_lo_verdict"
  },
  "rollback": {
    "instructions": "Revert only the exact Cursor shim/readiness/test hunks and exact seven reviewed deletions in one governed transaction.",
    "verification": "Rerun focused Cursor and publisher tests and confirm dispatcher eligibility, roles, caps, and ordinary Cursor command construction are unchanged."
  },
  "hard_invariants": [
    "Cursor E remains dispatchable and is never disabled or deprioritized.",
    "The harness never selects, routes, spawns, suspends, or observes another harness.",
    "Only a role-authorized next verdict is published through publish_lo_verdict.",
    "Malformed, ambiguous, stale, unclaimed, or provenance-conflicting output creates no bridge file.",
    "No live worker is stopped for rollout or helper retirement.",
    "No source, test, configuration, runtime, or bridge path outside target_paths is mutated."
  ],
  "fail_closed_conditions": [
    "Independent GO, matching claim/start authority, or post-implementation VERIFIED is absent.",
    "Cursor read-only mode cannot complete the required review evidence.",
    "The final output does not contain exactly one valid verdict envelope.",
    "The governed publisher rejects the claim, transition, provenance, version, evidence, or finalization scope.",
    "Any worker that may reference a deletion target remains live.",
    "A proposed change would alter routing, eligibility, role, cap, process lifetime, or another harness."
  ],
  "essential_context_preservation": "Preserve substantive LO review capability, preflight command evidence, GO/NO-GO/VERIFIED semantics, VERIFIED hunk and commit scoping, dispatcher audit correlation, and the complete append-only bridge and Git histories."
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py -q --tb=short` | LO routes force read-only mode, parse exactly one envelope, bind session-derived metadata, acquire/release the claim, and call only `publish_lo_verdict`; invalid/stale output produces no publication. |
| `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | same focused suite plus static command-construction assertions | No routing, target selection, role, eligibility, cap, or other-harness operation is exposed to Cursor. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_cursor_dispatch.py -q --tb=short` | readiness remains green and validates the governed read-only publication route; ordinary routes retain current command behavior. |
| `GOV-WORK-TREE-HYGIENE-001` | `git ls-files "scripts/_dispatch*.py"` and `git ls-files --others --exclude-standard "scripts/_dispatch*.py"` | Neither command reports any of the seven retired one-shot helpers; no unrelated file is removed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog list --all --id WI-5399 --json` | WI-5399 remains linked to TEST-11511 and the filed proposal; implementation/report/verdict evidence is appended rather than inferred from cleanup. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short` | Physical residue cannot be treated as retired merely because review metadata is terminal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cursor_harness.py platform_tests/scripts/test_verify_cursor_dispatch.py platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` | All focused harness, readiness, and publisher tests pass before an independent LO verdict. |

The implementation report must record the naturally exited worker check before
deleting the untracked helper and must provide before/after Git status proving
that only the exact reviewed targets changed.

## Risk / Rollback

The main risk is making Cursor unable to complete a substantive review if its
read-only mode cannot execute required read-only preflights, or parsing a model
response as a verdict when it is not one. Tests therefore require exact
single-envelope framing, fail-closed parsing, no publication on ambiguity, and
preservation of the existing readiness contract. VERIFIED metadata receives
separate coverage because it can invoke Git finalization. Rollback is one
scoped commit restoring the shim/tests and the seven helpers; no dispatcher,
harness registry, role, eligibility, runtime history, or bridge history is
rewritten.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5399-cursor-governed-verdict-publication`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix`: this closes an observed unauthorized effect boundary and removes its
exact protected-source residue while preserving the supported feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
