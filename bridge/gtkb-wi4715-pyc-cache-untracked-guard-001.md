NEW

# gtkb-wi4715-pyc-cache-untracked-guard - pyc cache untracked guard

bridge_kind: prime_proposal
Document: gtkb-wi4715-pyc-cache-untracked-guard
Version: 001
Author: Codex Prime Builder
Date: 2026-06-23T03:30:49Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ef01a-73cf-7f82-ae71-a5acc321664f
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop interactive session; transcript role override ::init gtkb pb; bridge-propose + gtkb-propose skills

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4715

target_paths: [".gitignore", "platform_tests/scripts/test_no_tracked_pyc_artifacts.py"]

implementation_scope: test_addition | scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4715 was created after WI-4701 observed a tracked Python cache artifact under
the generated Codex bridge-skill adapter surface. The current checkout no
longer has any tracked `__pycache__` or `.pyc` artifact in `HEAD` or the git
index, and `.gitignore` already ignores representative helper-cache paths.

This proposal therefore treats the implementation as a closure guard rather
than a cleanup: add focused regression coverage that fails if generated helper
cache artifacts become tracked again, and assert that the policy surface keeps
`.pyc` / `__pycache__` files ignored. No bridge file, backlog record, formal
specification, or generated skill source should be rewritten merely to recreate
the stale symptom.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the append-only bridge proposal,
  Loyal Opposition review, and later implementation report / verification
  chain for this protected workspace change.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - binds this work to project
  authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23`,
  owner decision `DELIB-20265586`, and the snapshot member WI set that includes
  `WI-4715`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  proposal to identify the governing specifications before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the Project
  Authorization, Project, and Work Item metadata lines present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the
  post-implementation report to map verification evidence back to the cited
  specifications.
- `GOV-STANDING-BACKLOG-001` - governs closure of standing backlog work without
  adding unapproved new project WIs. This is a single-WI bridge review packet,
  not a bulk backlog operation; the owner-approval packet is `DELIB-20265586`
  plus the PAUTH cited above, and no formal-artifact-approval gate is triggered
  because no GOV/SPEC/ADR/DCL/PB/REQ artifact mutation is in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - applies because the proposal must
  preserve the hygiene finding and closure evidence as durable bridge/test
  artifacts instead of harness-local scratch.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - applies because the test, bridge
  report, and eventual verification verdict form the durable artifact graph for
  closing this stale adapter-cache defect.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - applies because WI-4715 should move
  through explicit `NEW` -> `GO` -> implementation report -> `VERIFIED`
  lifecycle states rather than being silently closed from a local observation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - applies because the defect came from
  generated Codex skill-adapter surfaces and should remain guarded in Codex's
  filesystem path as well as the template/source side.

## Prior Deliberations

- `DELIB-20265586` - owner authorization for the bounded
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` implementation batch, explicitly
  including `WI-4715` and excluding any newly added work items from this PAUTH.
- `DELIB-20265459` - owner authorization for the WI-4701 implementation batch
  that surfaced the adapter-generated bridge-skill hygiene issues from which
  WI-4715 was split.
- `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-003.md` - records the
  WI-4701 scope boundary and defers tracked-cache cleanup / hardening follow-up
  to successor work instead of broadening WI-4701.
- `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-009.md` - verifies the
  WI-4701 implementation while leaving the successor hygiene items to their
  own bridge cycles.

## Owner Decisions / Input

No new owner input is required for this proposal. `DELIB-20265586` authorizes
bounded implementation for the eight current open member work items in
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, including `WI-4715`, and the
proposed work stays inside the allowed mutation classes `test_addition` and
`scaffold_update`.

No new work item is added, no formal GOV/SPEC/ADR/DCL/PB/REQ artifact is
mutated, and no destructive cleanup is proposed.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4715`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
`GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` together define the required
behavior: the previously observed tracked cache artifact must not recur, the
proposal must stay bound to the authorized project member WI, and verification
must prove the cache-artifact guard works.

Current repo evidence also narrows the requirement: `git ls-files` and
`git ls-tree -r HEAD --name-only` find no tracked `__pycache__` or `.pyc`
artifact, while `git check-ignore -v` confirms representative helper-cache
paths are ignored by `.gitignore`. Therefore the implementation does not need a
new requirement, owner clarification, or cache deletion step before bridge
review.

## Spec-Derived Verification Plan

The implementation report will include spec-derived evidence equivalent to:

```text
python -m pytest platform_tests/scripts/test_no_tracked_pyc_artifacts.py -q --tb=short
python -m ruff check .gitignore platform_tests/scripts/test_no_tracked_pyc_artifacts.py
python -m ruff format --check platform_tests/scripts/test_no_tracked_pyc_artifacts.py
git ls-files | rg "(__pycache__|\\.pyc$)"
git check-ignore -v .codex/skills/bridge/helpers/__pycache__/protected_write.cpython-314.pyc
```

Expected results:

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - pytest fails if tracked
  `.pyc` or `__pycache__` artifacts appear in the index, and passes when none
  are tracked.
- `GOV-STANDING-BACKLOG-001` - pytest documents WI-4715 closure without adding
  successor WIs or broadening project scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the bridge proposal, regression test,
  post-implementation report, and LO verdict preserve an explicit lifecycle
  trail for the finding.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the representative Codex bridge helper
  cache path remains ignored, proving the adapter/cache surface is protected.
- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - bridge preflights,
  implementation-start authorization, and the post-implementation report prove
  that the work stayed inside the authorized WI and append-only bridge flow.

If the `git ls-files | rg ...` command exits non-zero because no tracked cache
artifacts exist, that non-match is the expected evidence; the report should
state the exit semantics explicitly.

## Risk / Rollback

Risk is low because the intended change is a focused regression test and, only
if LO requests it, a clarifying `.gitignore` assertion for already-effective
ignore policy. The main risk is over-broadening into repo-wide cleanup or
renormalization; this proposal explicitly excludes that work.

Rollback is a single commit revert of the added test / policy assertion. No
tracked cache artifact should be introduced as part of rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4715-pyc-cache-untracked-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

test - the expected implementation is regression coverage that proves generated
cache artifacts remain untracked and ignored.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
