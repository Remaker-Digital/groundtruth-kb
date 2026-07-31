NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5
author_model_version: 2026-07-15 Codex Desktop
author_model_configuration: danger-full-access filesystem; network enabled; approval policy never

bridge_kind: governance_advisory
Document: gtkb-modernization-rc-blocker-repair
Version: 001
Date: 2026-07-15
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5165
target_paths: []

# GT-KB Modernization RC Blocker Repair Governance Proposal

## Claim

The modernization release candidate is not ready because current acceptance evidence shows live RC blockers that cannot be repaired by direct mutation from this session. This governance proposal records the blocker set and asks for the next governed implementation authority path. It does not authorize source, test, configuration, runtime-state, MemBase, dispatcher, bridge-routing, semantic-evidence, Git, release, deployment, credential, or harness-contact mutation.

## Owner Decisions / Input

- 2026-07-15 transcript directive: `AUTHORIZED: file RC blocker repair proposal only`.
- Boundary retained from owner directives: no harness may directly interact with another harness without explicit per-access approval; all harness, TAFE, and bridge interaction must remain via TAFE/bridge/skills+CLI; no direct mutation of change-controlled harness, TAFE, bridge implementation artifacts, or SoT without explicit per-access approval; bridge routing must remain deterministic and must not be manually steered by Prime Builder.

## Evidence

- `python scripts\check_modernization_release_candidate.py validate` passed: frozen manifest has 8 capabilities and 94 handles.
- `python scripts\check_modernization_release_candidate.py digest` returned `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
- `python scripts\check_modernization_release_candidate.py status` returned NOT READY because the worktree is not clean, zero independently attested clean passing runs exist at current HEAD, and the independent modernization audit JSON is missing.
- `python scripts\check_modernization_scope_semantics.py run --phase clean-suite --json` returned FAIL with 90 assertions evaluated and 27 failing.
- `MSA-MOD-P01`, `MSA-MOD-P03`, and `MSA-MOD-P05` fail because `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE` is active with `parent_project_id = NULL`; the frozen checker requires all seven child projects under `PROJECT-GTKB-PLATFORM-MODERNIZATION`.
- `MSA-MOD-HP09` fails because current bridge health/parity evidence shows no active dispatchable Loyal Opposition target. This proposal does not change dispatch eligibility, weights, or routing.
- `python scripts\collect_modernization_semantic_evidence.py --json status` reported `INVALID=14` and `BLOCKED=12`; invalid receipts are stale against current HEAD and/or canonical session provenance, and blocked receipts have no valid collected issue.
- `MSA-MOD-GL13` lacks `.gtkb-state\modernization-release-candidate\semantic-evidence\git-lifecycle-modernization-pilot.json`.
- `python -m groundtruth_kb bridge file-implementation-proposal --wi WI-5165 --slug gtkb-modernization-rc-blocker-repair --project PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE ... --dry-run --json` failed before writing: `No active project authorization covers WI-5165 in PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE; pass --create-missing-state with --owner-decision to create a bounded PAUTH.`

## Proposed Next Governance Action

Create or approve a bounded implementation PAUTH for `WI-5165` under `PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE`, then file a normal implementation proposal for the smallest repair slice that can make the RC blocker set strictly smaller.

The follow-on implementation proposal should cover only the minimum necessary repair classes:

1. Append-only project metadata repair for the Assurance project parent link, using governed project CLI/API, not raw SQL.
2. Deterministic bridge-health or dispatchability repair sufficient for the frozen HP09 parity assertion, without Prime Builder manual routing or direct harness contact.
3. Collector provenance repair or valid collector-context launch so new semantic receipts bind to the correct current session authority.
4. Current-HEAD replacement receipts for stale receipt-backed assertions, and honest BLOCKED results for receipts whose prerequisites are not yet satisfied.
5. The real-pilot receipt path for `MSA-MOD-GL13`, only after the real lifecycle pilot and independent verification evidence exist.
6. Release-candidate evidence sequencing: clean worktree, two independently attested clean passing runs at current HEAD, independent modernization audit JSON, then exact full RC gate.

## Out Of Scope

- No implementation is authorized by this governance proposal.
- No creation of missing PAUTH or MemBase authorization state is performed by this filing.
- No direct dispatcher eligibility, weight, target-selection, routing, or harness-budget mutation is authorized.
- No harness contact, sub-agent launch, direct LO routing, or bridge bypass is authorized.
- No git staging, commit, push, release, deployment, destructive cleanup, or credential lifecycle action is authorized.
- No change to WI-5138 finalization commit `08cbc0172ad77d6b4395f34498e5cb0abbe7465f` is authorized.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
- DCL-PROJECT-DEPENDENCY-ORDERING-001
- GOV-SESSION-ROLE-AUTHORITY-001
- DCL-SESSION-ROLE-RESOLUTION-001
- DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001
- DCL-GIT-BRANCH-BINDING-PROMOTION-001

## Prior Deliberations

- 2026-07-15 transcript directive authorizing this filing only: `AUTHORIZED: file RC blocker repair proposal only`.
- DELIB-20260710-GTKB-MODERNIZATION-GATE-1-READINESS-AUTHORIZATION, cited by active Assurance work-item memberships for WI-5152 through WI-5165.
- DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY, cited by the existing WI-5138 root PAUTH and preserved as separate from this WI-5165 repair scope.

## Specification-Derived Verification

This governance advisory does not implement code or mutate SoT. The current observed verification state is intentionally blocking:

- `python scripts\check_modernization_release_candidate.py validate` observed PASS.
- `python scripts\check_modernization_release_candidate.py digest` observed `AD70C6D61C01500DBDF11BA8AFD5C1A42AD8C00D4EB63BDBF0EEC2423D1EB240`.
- `python scripts\check_modernization_release_candidate.py status` observed NOT READY.
- `python scripts\check_modernization_scope_semantics.py run --phase clean-suite --json` observed FAIL with 27 failing assertions.
- `python scripts\collect_modernization_semantic_evidence.py --json status` observed INVALID and BLOCKED receipt states.
- Targeted regression evidence retained for future implementation proposals includes `python -m pytest platform_tests/scripts/test_modernization_release_candidate.py -q --tb=short` and targeted `test_modernization_*` nodeids for each repaired assertion.

A future implementation proposal must replace this advisory state with concrete spec-to-test mapping for the exact target_paths it requests.

## Verification Plan For Follow-On Implementation

A future implementation proposal should require at minimum:

- `python scripts\check_modernization_release_candidate.py validate`
- `python scripts\check_modernization_release_candidate.py digest`
- `python scripts\check_modernization_release_candidate.py status`
- `python scripts\check_modernization_scope_semantics.py run --phase clean-suite --json`
- `python scripts\collect_modernization_semantic_evidence.py --json status`
- Targeted assertion reruns for each repaired `MSA-MOD-*` blocker.
- The exact frozen full RC gate only after clean-worktree prerequisites are satisfied: `python scripts\release_candidate_gate.py --modernization-scope --include-frontend`.

## Risk And Rollback

Risk is governance confusion if this proposal is mistaken for implementation authority. The mitigation is explicit: target_paths is empty, this file uses `bridge_kind: governance_advisory`, and the dry-run evidence proves missing PAUTH for `WI-5165`. Rollback is not deletion or rewrite; any correction must be an append-only follow-up bridge entry.
