NEW

# WI-5393 - Finalize pytest recursion exclusions with compatibility evidence

bridge_kind: prime_proposal
Document: gtkb-wi5393-pytest-recursion-exclusions
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5393

target_paths: ["pyproject.toml", "platform_tests/governance/test_platform_tests_rename.py"]

implementation_scope: pytest recursion configuration and one regression test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Independently review and finalize the current root pytest configuration
candidate that adds `norecursedirs = [".*", "pytest-tmp-*"]`. This prevents
default recursive collection from entering in-root hidden/runtime evidence and
pytest temporary trees while retaining `platform_tests` as the canonical test
root. Add one parsed-configuration regression beside the existing testpaths
contract so future edits cannot silently hide the platform suite or re-enable
runtime-tree recursion.

The release-candidate gate currently stops at the protected project-config
`docs_review` route. Documentation review disposition: no public behavior,
command syntax, API, or user workflow changes; no documentation edit is
required. Compatibility evidence and independent review are required before an
exact mechanical finalization can make the tree clean. No unrelated dirty or
staged path may be absorbed.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - protected configuration dirt must have exact
  ownership, review, testing, and finalization rather than aggregate capture.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - collection optimization must not
  hide platform tests or weaken release evidence.
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` - platform-owned tests remain the
  independent GT-KB acceptance surface.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the configuration and its
  effect require deterministic, executable evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does
  not waive GO, claim, start, verification, or Git gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority
  is rechecked before protected edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requirements are
  explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  and exact targets are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - review maps config
  behavior to executable compatibility evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5393 durably owns the discovered RC blocker.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - candidate, work item, proposal,
  test, report, verdict, and finalization remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - VERIFIED and physical finalization
  are separate required lifecycle states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - docs-review disposition and
  compatibility evidence are preserved as durable artifacts.

## Prior Deliberations

- `DELIB-202666274` - supplies project-scoped modernization Assurance authority
  while retaining bridge and mechanical Git gates.
- Owner directive, 2026-07-16 - inventory ownership for all worktree dirt and
  finalize only independently verified scopes with exact authority.
- WI-5365 - separately owns duplicate nested Git metadata work; WI-5393 changes
  only pytest recursive collection and must not absorb WI-5365 behavior.

## Owner Decisions / Input

No new owner decision is required. The project PAUTH covers the bounded config
and test review. Git staging, commit, push, release, deployment, cleanup,
credentials, dispatcher, TAFE, harness routing, roles, and eligibility remain
excluded until their own exact authority exists.

## Requirement Sufficiency

Existing requirements are sufficient. The inventory policy already prescribes
documentation review and compatibility testing for this config class; this
proposal supplies both without changing that policy.

## Proposed Scope

1. Preserve the current two `norecursedirs` patterns and normalize only the
   existing terminal blank-line artifact if formatting requires it.
2. Add one focused test asserting the parsed root config retains
   `platform_tests`, excludes hidden trees, and excludes pytest runtime trees.
3. Run the existing governance module and a representative collect-only probe.
4. Record that user documentation is unaffected.
5. Finalize only these exact reviewed hunks under separate mechanical authority.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` | Run the governance config test module and a representative platform collect-only probe. | The platform suite remains discoverable and the new recursion assertion passes. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Parse the root TOML and inspect the configured testpaths and norecursedirs values. | `platform_tests` is retained; hidden and pytest runtime trees are excluded exactly. |
| `GOV-WORK-TREE-HYGIENE-001` | Inspect exact two-path diff and diff-check output, then rerun the release inventory-drift check after separate finalization. | No foreign hunk is present; the protected-config blocker disappears only after governed physical closure. |
| Documentation review | Compare changed behavior with public command, API, and workflow documentation surfaces. | No public documentation is affected; the no-doc-change disposition is independently accepted. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5393; current root pytest config diff; release-candidate docs_review failure on 2026-07-16","canonical_authority":"GOV-WORK-TREE-HYGIENE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"root pytest recursion exclusions plus parsed-config regression","before_behavior":"Default collection can recurse into hidden/runtime pytest trees, while the unowned config candidate blocks the release gate at docs_review.","after_behavior":"Runtime trees are excluded, platform tests remain discoverable, docs impact is explicitly none, and only independently verified hunks are eligible for finalization.","self_descriptive_naming":"test_pyproject_norecursedirs_preserves_platform_collection names both the optimization and its safety condition.","obsolete_guidance_disposition":"No public guidance changes; the review record states that this is internal test discovery configuration.","history_preservation":"The original diff, WI-5393, compatibility test, docs disposition, report, verdict, and exact finalization remain traceable.","baseline":{"release_gate":"fails because pyproject.toml requires docs_review","candidate":"adds hidden and pytest-tmp recursion exclusions"},"expected_result":{"config":"platform_tests retained with exact runtime recursion exclusions","release_gate":"protected config no longer dirty after separately authorized finalization"},"rollback":{"instructions":"revert only the WI-5393 config and test hunks through a governed successor","verification":"rerun config regression, collect-only probe, and release inventory check"},"hard_invariants":["platform_tests remains canonical","no runtime evidence tree is collected by default","no foreign dirt is staged or committed","no harness or dispatcher change","no Git effect without separate authority"],"fail_closed_conditions":["platform tests disappear from collection","patterns broaden beyond hidden/runtime pytest trees","docs impact is omitted","foreign hunks enter scope","GO, claim, start, or independent VERIFIED is absent"],"essential_context_preservation":"Retain exact config values, independent platform test scope, docs-review disposition, worktree ownership, and physical-finalization boundary."}
```

## Acceptance Criteria

1. Root pytest config retains `platform_tests` and the exact two recursion
   exclusions.
2. Focused config and representative collection tests pass.
3. Independent review accepts the no-doc-change disposition.
4. Exact diff contains no unrelated path or hunk.
5. Independent VERIFIED and separate mechanical authority precede finalization.

## Risk / Rollback

The risk is overbroad exclusion hiding real tests. Exact patterns, parsed-config
assertions, and representative collection evidence constrain that risk.
Rollback is the two-path hunk through a governed successor; no broad reset,
unstage, clean, or aggregate commit is permitted.

## Bridge Filing

File through the governed Codex non-bypass helper. The numbered bridge file
chain is append-only. Deterministic TAFE routing remains external; this filing
does not contact or configure any harness.

## Recommended Commit Type

`test` - bound pytest recursion without weakening platform collection.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
