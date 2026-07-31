NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# WI-5441 Global Registry Membership Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 001
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["config/registry/sot-artifacts.toml","groundtruth.db","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py","groundtruth-kb/src/groundtruth_kb/project/doctor.py","groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/project/sot_audit.py","groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/tests/test_artifact_membership_reconciliation.py","groundtruth-kb/tests/test_registry_control_plane.py","groundtruth-kb/tests/test_sot_duplicate_audit.py","platform_tests/scripts/test_check_harness_parity.py","platform_tests/scripts/test_check_sot_registry_completeness.py","scripts/check_harness_parity.py"]
registry_admission_paths: [".agent/skills/gtkb-adr/SKILL.md",".agent/skills/gtkb-alternatives-investigation/SKILL.md",".agent/skills/gtkb-arch-audit/SKILL.md",".agent/skills/gtkb-assert/SKILL.md",".agent/skills/gtkb-assertion-triage/SKILL.md",".agent/skills/gtkb-batch/SKILL.md",".agent/skills/gtkb-benchmarks/SKILL.md",".agent/skills/gtkb-bridge-config/SKILL.md",".agent/skills/gtkb-bridge-propose/SKILL.md",".agent/skills/gtkb-bridge-reconciliation/SKILL.md",".agent/skills/gtkb-bridge/SKILL.md",".agent/skills/gtkb-check-deliberations/SKILL.md",".agent/skills/gtkb-code-review-audit/SKILL.md",".agent/skills/gtkb-decision-capture/SKILL.md",".agent/skills/gtkb-dispatcher-control/SKILL.md",".agent/skills/gtkb-grill-me-for-clarification/SKILL.md",".agent/skills/gtkb-harness-parity-review/SKILL.md",".agent/skills/gtkb-hygiene-investigation/SKILL.md",".agent/skills/gtkb-hygiene-sweep/SKILL.md",".agent/skills/gtkb-lo-hygiene-assessment/SKILL.md",".agent/skills/gtkb-lo-opportunity-radar/SKILL.md",".agent/skills/gtkb-loyal-opposition-report/SKILL.md",".agent/skills/gtkb-managed-skill-adoption-review/SKILL.md",".agent/skills/gtkb-projects/SKILL.md",".agent/skills/gtkb-promote/SKILL.md",".agent/skills/gtkb-proposal-review/SKILL.md",".agent/skills/gtkb-propose/SKILL.md",".agent/skills/gtkb-query/SKILL.md",".agent/skills/gtkb-release-candidate-gate/SKILL.md",".agent/skills/gtkb-send-review/SKILL.md",".agent/skills/gtkb-session-wrap-scan/SKILL.md",".agent/skills/gtkb-session-wrap/SKILL.md",".agent/skills/gtkb-spec-intake/SKILL.md",".agent/skills/gtkb-spec/SKILL.md",".agent/skills/gtkb-structural-hygiene-review/SKILL.md",".agent/skills/gtkb-sweep-commit/SKILL.md",".agent/skills/gtkb-verify/SKILL.md",".agent/skills/gtkb-work-item/SKILL.md",".claude/skills/gtkb-adr/SKILL.md",".claude/skills/gtkb-advisory-disposition/SKILL.md",".claude/skills/gtkb-advisory-intake/SKILL.md",".claude/skills/gtkb-advisory-proposal/SKILL.md",".claude/skills/gtkb-alternatives-investigation/SKILL.md",".claude/skills/gtkb-arch-audit/SKILL.md",".claude/skills/gtkb-assert/SKILL.md",".claude/skills/gtkb-assertion-triage/SKILL.md",".claude/skills/gtkb-batch/SKILL.md",".claude/skills/gtkb-benchmarks/SKILL.md",".claude/skills/gtkb-bridge-config/SKILL.md",".claude/skills/gtkb-bridge-reconciliation/SKILL.md",".claude/skills/gtkb-check-deliberations/SKILL.md",".claude/skills/gtkb-code-review-audit/SKILL.md",".claude/skills/gtkb-decision-capture/SKILL.md",".claude/skills/gtkb-dispatcher-control/SKILL.md",".claude/skills/gtkb-formal-artifact-packet-helper/SKILL.md",".claude/skills/gtkb-grill-me-for-clarification/SKILL.md",".claude/skills/gtkb-harness-parity-review/SKILL.md",".claude/skills/gtkb-hygiene-investigation/SKILL.md",".claude/skills/gtkb-hygiene-reclaim/SKILL.md",".claude/skills/gtkb-hygiene-sweep/SKILL.md",".claude/skills/gtkb-lo-hygiene-assessment/SKILL.md",".claude/skills/gtkb-lo-opportunity-radar/SKILL.md",".claude/skills/gtkb-loyal-opposition-report/SKILL.md",".claude/skills/gtkb-managed-skill-adoption-review/SKILL.md",".claude/skills/gtkb-projects/SKILL.md",".claude/skills/gtkb-promote/SKILL.md",".claude/skills/gtkb-propose/SKILL.md",".claude/skills/gtkb-query/SKILL.md",".claude/skills/gtkb-release-candidate-gate/SKILL.md",".claude/skills/gtkb-session-wrap-scan/SKILL.md",".claude/skills/gtkb-session-wrap/SKILL.md",".claude/skills/gtkb-skill-governance-lifecycle/SKILL.md",".claude/skills/gtkb-spec-intake/SKILL.md",".claude/skills/gtkb-spec/SKILL.md",".claude/skills/gtkb-structural-hygiene-review/SKILL.md",".claude/skills/gtkb-sweep-commit/SKILL.md",".claude/skills/gtkb-work-item/SKILL.md",".codex/gtkb-hooks/bridge-compliance-audit.cmd",".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd",".codex/gtkb-hooks/codex-mcp-worker-guard.cmd",".codex/gtkb-hooks/directive-enforcement.cmd",".codex/gtkb-hooks/formal-artifact-\u0061pproval.cmd",".codex/gtkb-hooks/session_start_dispatch.py",".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py",".codex/gtkb-hooks/sot-read-discipline-bash-adapter.py",".codex/gtkb-hooks/wi-id-collision-gate.cmd",".codex/skills/gtkb-adr/SKILL.md",".codex/skills/gtkb-advisory-disposition/SKILL.md",".codex/skills/gtkb-advisory-intake/SKILL.md",".codex/skills/gtkb-advisory-proposal/SKILL.md",".codex/skills/gtkb-alternatives-investigation/SKILL.md",".codex/skills/gtkb-arch-audit/SKILL.md",".codex/skills/gtkb-assert/SKILL.md",".codex/skills/gtkb-assertion-triage/SKILL.md",".codex/skills/gtkb-batch/SKILL.md",".codex/skills/gtkb-benchmarks/SKILL.md",".codex/skills/gtkb-bridge-config/SKILL.md",".codex/skills/gtkb-bridge-propose/SKILL.md",".codex/skills/gtkb-bridge-reconciliation/SKILL.md",".codex/skills/gtkb-check-deliberations/SKILL.md",".codex/skills/gtkb-code-review-audit/SKILL.md",".codex/skills/gtkb-decision-capture/SKILL.md",".codex/skills/gtkb-dispatcher-control/SKILL.md",".codex/skills/gtkb-formal-artifact-packet-helper/SKILL.md",".codex/skills/gtkb-grill-me-for-clarification/SKILL.md",".codex/skills/gtkb-harness-parity-review/SKILL.md",".codex/skills/gtkb-hygiene-investigation/SKILL.md",".codex/skills/gtkb-hygiene-reclaim/SKILL.md",".codex/skills/gtkb-hygiene-sweep/SKILL.md",".codex/skills/gtkb-lo-hygiene-assessment/SKILL.md",".codex/skills/gtkb-lo-opportunity-radar/SKILL.md",".codex/skills/gtkb-loyal-opposition-report/SKILL.md",".codex/skills/gtkb-managed-skill-adoption-review/SKILL.md",".codex/skills/gtkb-projects/SKILL.md",".codex/skills/gtkb-promote/SKILL.md",".codex/skills/gtkb-propose/SKILL.md",".codex/skills/gtkb-query/SKILL.md",".codex/skills/gtkb-release-candidate-gate/SKILL.md",".codex/skills/gtkb-session-wrap-scan/SKILL.md",".codex/skills/gtkb-session-wrap/SKILL.md",".codex/skills/gtkb-skill-governance-lifecycle/SKILL.md",".codex/skills/gtkb-spec-intake/SKILL.md",".codex/skills/gtkb-spec/SKILL.md",".codex/skills/gtkb-structural-hygiene-review/SKILL.md",".codex/skills/gtkb-sweep-commit/SKILL.md",".codex/skills/gtkb-work-item/SKILL.md","scripts/dispatch_blackbox_gate.py","scripts/session_self_initialization.py"]
registry_admission_path_count: 128
capability_evidence_hash: sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3
approval_evidence_scope: no formal-artifact approval-evidence or approval-packet work; names in registry_admission_paths are capability subjects only

## Claim

Finish the registry-completeness acceptance work that the terminal v4 control-plane
thread intentionally left to a subsequent reviewed reconciliation.

The platform registry remains the sole membership authority. Observation
sources may prove that an unregistered artifact is load-bearing, but they never
grant membership. This slice will:

1. admit the exact 128 present native, adapter, and canonical capability paths
   bound above through one atomic `gt registry register --batch-file`
   transaction;
2. implement a typed, provenance-bearing membership reconciliation service;
3. replace the prior count-only `coverage_complete` predicate with exact
   classification closure;
4. make doctor, `gt registry validate`, and release fail on unknown or
   unregistered-load-bearing paths while leaving unregistered-disposable
   objects eligible only for later governed quarantine;
5. reduce whole-root census cost by classifying provably disposable,
   non-structural-ancestor subtrees without recursively enumerating their
   payload.

No file move, rename, reference rewrite, quarantine, deletion, commit, push,
release, deployment, dispatcher mutation, harness-role mutation, or Stage B
migration apply is authorized.

## Why The Verified v4 Slice Is Not Closure

The v4 proposal's Acceptance Criterion 6 required only that "all touched
load-bearing publication chokepoints are registered." Its terminal v4-006
verification used `gt registry inspect --no-census --json`, proving
declaration/projection/currentness coherence for 145 records but not global
membership completeness.

After the bounded WI-5640 registry transaction, the live registry has 313
records: 298 exact, 10 virtual, one glob, three opaque containers, and one
recursive declaration.

A canonical whole-root census observed:

- 1,864,241 objects;
- 1,863,842 unregistered or invalid gaps;
- 1,726,203 objects under `.pytest-tmp`;
- approximately six minutes elapsed for both CLI inspection and direct census.

Most of those objects are disposable under the owner's membership rule. Their
quantity does not prove a registry defect. The load-bearing observer join does.

## Deterministic P0 Evidence

The exact input is
`config/agent-control/gtkb-harness-capability-registry.toml`. For every
capability, the observer selects:

- every `canonical_source`;
- every per-harness `surface` whose typed status is `native` or `adapter`;
- no `fallback`, `unsupported`, or waived surface.

This mirrors `scripts/check_harness_parity.py`: an absent fallback is
`DEFERRED`, while native and adapter surfaces are operative and existence
checked.

The canonical SoT resolver then classified the selected paths:

- 226 evidence observations;
- 156 unique operative paths;
- 128 present operative paths with no registry member;
- zero missing operative paths;
- 117 uncovered skill paths and 11 uncovered hook/script paths;
- uncovered roots: 49 `.codex`, 39 `.claude`, 38 `.agent`, and two `scripts`;
- deterministic evidence hash: `sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`.

Deleting all unregistered objects today would remove those 128 declared,
present capability surfaces and impair GT-KB. That contradicts
`GOV-PLATFORM-SOT-REGISTRY-001` v2 and proves registry completeness is false.

## Prior False-Completeness Predicate

`groundtruth_kb.project.sot_audit.DuplicateSoTAuditReport.coverage_complete`
currently returns true when:

`registry_count > 0 and persistent_file_count >= registered_file_count`.

That count inequality does not map, join, or classify the persistent files.
WI-5014 therefore established a duplicate-SoT audit, not global membership
closure, despite naming a "whole_project_persistent_file_closure" phase.

This slice must either retire that predicate in favor of the new reconciliation
result or redefine it as exact set closure. No count comparison may support a
coverage-complete claim.

## Authority And Classification Model

The reconciliation result has exactly four physical classifications:

1. `registered`: the canonical resolver returns one active declaration.
2. `unregistered_load_bearing`: no declaration resolves, but one or more typed
   operative observers identify the object. This is release- and sweep-blocking.
3. `unregistered_disposable`: no declaration and no operative observer identify
   the object. This is not retained or corrected by this work; it may only enter
   a separately authorized quarantine sweep after closure.
4. `invalid_unknown`: unreadable, ambiguous, unsafe, conflicting, or
   unsupported object/evidence. This is release- and sweep-blocking.

Structural ancestors remain a traversal class, not membership. Virtual
declarations remain declaration-only. Immediate `applications/<child>` roots
remain application-owned boundaries. `.git` remains VCS service state.

Every result carries normalized path, object kind, classification, registry ID
if any, observer IDs, observer source digests, and a deterministic evidence
digest. An observer cannot mutate registry state or silently convert a candidate
to membership.

## Typed Observer Set

The first implementation must expose adapters, not ad hoc caller parsing, for:

1. **Capability inventory:** canonical source plus typed native/adapter surfaces
   using the same status semantics as the parity checker.
2. **Governed knowledge paths:** current MemBase specification `source_paths`,
   governed test implementation paths, and other canonical in-root path fields
   exposed through existing KnowledgeDB readers.
3. **Package and entrypoint paths:** in-root package/build metadata, console
   entrypoints, packaged context manifests, and declared package resources.
4. **Registered dependency closure:** registry `depends_on`, managed generator
   manifests, and deterministic in-root path references emitted by registered
   text artifacts through the canonical inventory service.
5. **Physical census:** the no-follow root walker and canonical resolver.

Observer parse failure, missing operative target, path escape, collision,
ambiguous evidence, unreadable object, and junction/reparse uncertainty produce
`invalid_unknown`; they never become disposable by default.

Git tracked, ignored, and untracked status is evidence metadata only and cannot
grant membership or retention.

## Exact Capability Admission

The 128 `registry_admission_paths` in this proposal are the full mutation scope
ceiling for membership additions in this slice.

Each record is exact-path coverage. Canonical sources are `active`; generated
harness adapters are `generated`; executable hook/script surfaces retain their
typed control-surface domain. Record metadata is derived from the existing
registered peer records for the same artifact class and validated before apply.

The batch must:

1. be rendered as deterministic JSON;
2. bind the current declaration, packaged mirror, projection, capability
   registry digest, `sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`, exact 128-path set, PAUTH, GO, claim, and
   implementation-start packet;
3. pass dry-run with 128 additions and zero removals/identity transitions;
4. commit through one registry transaction;
5. leave canonical and packaged TOML byte-identical and the projection current;
6. emit one receipt and support idempotent exact retry;
7. fail before mutation if any operative path, source digest, target metadata,
   or current registry generation changes.

No glob may replace the exact set. In particular, helper/reference directories
must not be covered wholesale because they contain disposable drafts and
generator debris.

## Fast Complete Census

The current walker descends every unregistered directory. On this checkout that
enumerates more than 1.7 million disposable pytest objects and makes routine
inspection take minutes.

The replacement must precompute:

- registered structural ancestors;
- exact operative observer paths and their ancestors;
- unsafe or unreadable boundaries.

An unregistered directory that is neither a registered structural ancestor nor
an operative-observer ancestor may be classified once as an
`unregistered_disposable_subtree` covering its descendants. The walker does not
descend it. Junctions, symlinks, and reparse nodes are never followed and cannot
receive subtree disposition when their target or type is uncertain.

Tests must prove this pruning cannot hide a registered member or observer path.
The report must include elapsed time and assert a warm and cold read-only
reconciliation under 30 seconds on the current root without relying on Git
status or deleting scratch data.

## CLI And Enforcement

Add `gt registry reconcile --json` as the canonical read-only report. It emits
the four classifications, observer provenance, counts, digests, subtree
summaries, and closure flags:

- `membership_complete`: zero `unregistered_load_bearing` and zero
  `invalid_unknown`;
- `sweep_eligible`: membership complete, coherent/current registry, and no
  nonterminal transaction;
- `release_eligible`: membership complete plus existing release/currentness
  requirements.

`gt registry inspect` must display reverse-coverage and reconciliation summary
in human mode. It may not print only `coherent: true` and record count while
hiding blocking gaps.

`gt registry validate`, doctor, release, migration preflight, and hygiene sweep
must consume the same typed reconciliation result. A consumer may request a
bounded detail payload but may not reimplement classification.

Sweep execution remains outside this scope and continues to require quarantine,
receipt, non-shortenable retention, restoration visibility, and separate
authorization.

## Cross-Thread Coordination

`bridge/gtkb-file-move-rename-canonicalization-v4-016.md` independently
re-executed the bounded WI-5640 implementation evidence and found it correct.
Its NO-GO was confined to a finalizer path-harvest defect in report form.
`bridge/gtkb-file-move-rename-canonicalization-v4-017.md` is the current
report-only correction; it changes no implementation postimage.

This thread may be proposed and reviewed concurrently, but implementation must
not acquire a claim or mutate any target until:

1. v4-017 receives an independent VERIFIED and its governed finalization commit completes;
2. the exact shared implementation baseline is retained;
3. this proposal receives an independent GO;
4. a fresh WI-5441 claim and exact implementation-start packet are issued.

If v4-017 or a later review requires any implementation postimage change, this
proposal must be revised against that new baseline before implementation. No
same-session review is eligible.

WI-5640 Stage B remains paused until this reconciliation reports
`membership_complete: true`.

## Requirement Sufficiency

Existing requirements sufficient.

`GOV-PLATFORM-SOT-REGISTRY-001` v2 and `SPEC-INTAKE-97538b` v2 already
require sole registry authority, registration of every load-bearing artifact,
zero unknown and zero unregistered-load-bearing closure, and quarantine-only
disposal. This proposal supplies implementation and tests; it does not create a
competing membership rule.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v2: sole membership authority, every
  load-bearing artifact registered, unregistered-load-bearing release/sweep
  blocker, and zero-unknown reconciliation.
- `SPEC-INTAKE-97538b` v2: Git status is not essentiality authority; every
  in-scope object is classified before quarantine eligibility.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`: exact locators and explicit coverage.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`: declaration, mirror, projection,
  journal, and revision parity.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`: CLI-only authorized
  mutation and no identity removal.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`: one mechanical
  service consumed by doctor, release, migration, and sweep.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`: typed operative surface semantics.
- `GOV-WORK-TREE-HYGIENE-001`: report-first, non-destructive closure.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: preserve the proven defect,
  reconciliation plan, and terminal evidence as governed artifacts.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Prior Deliberations And Related Work

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`: controlling
  owner directive for membership, automatic observation, and quarantine-only
  disposal.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-003.md` and
  v4-006 VERIFIED: control-plane foundation; explicitly bounded to touched
  chokepoints and no census verification.
- `.gtkb-state/bridge-revisions/drafts/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md`:
  non-authoritative historical draft explicitly deferred load-bearing versus
  disposable reconciliation to this subsequent reviewed step.
- `bridge/gtkb-sot-singleton-coverage-audit-007.md` and v008 VERIFIED:
  WI-5014 duplicate-SoT audit; its count-only `coverage_complete` predicate is
  corrected or retired here, not treated as membership evidence.
- `bridge/gtkb-file-move-rename-canonicalization-v4-016.md`: independent
  confirmation that the bounded WI-5640 implementation evidence passed; NO-GO was report-form only.
- `bridge/gtkb-file-move-rename-canonicalization-v4-017.md`: current
  report-only correction and shared baseline awaiting independent VERIFIED.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`: old migration sources stay
  present; no deletion is performed here.
- Required search found no open work item that already owns global
  unregistered-load-bearing reconciliation.

## Cross-Harness Disposition

This proposal does not create or change a harness role.

Claude canonical skill sources, generated Codex adapters, generated Antigravity
adapters, and operative hooks are admitted exactly as declared. Cursor fallback
surfaces are excluded from automatic admission because the canonical parity
checker classifies absent fallback surfaces as deferred, not operative.

Future capability creation must update the capability registry and registry
membership in the same governed transaction. A regression test mechanically
joins every canonical/native/adapter capability path to the SoT resolver and
fails on any uncovered or missing operative path.

## Specification-Derived Verification Plan

| Requirement | Exact executable evidence | Expected result |
| --- | --- | --- |
| Capability admission | New cross-registry test plus `gt registry reconcile --json` | 156 operative paths, zero uncovered/missing; exact 128 additions |
| Atomicity | Registry transaction fault matrix and exact retry test | Old or new coherent generation; one receipt; no partial admission |
| Observer semantics | Unit fixtures for capability, MemBase, package, dependency, and physical adapters | Provenance exact; fallback/Git never grants membership |
| Classification | Synthetic root matrix for all four classifications, structural ancestors, hosted apps, `.git`, virtual, opaque, symlink, junction, and unreadable nodes | Every in-scope object or subtree classified once |
| False predicate | `test_sot_duplicate_audit.py` regression | Count inequality cannot produce coverage complete |
| Pruning safety | Registered/observer descendant tests plus a million-file synthetic disposable subtree | Descendants cannot be hidden; bounded traversal |
| Performance | Cold and warm current-root `gt registry reconcile --json` timing | Each under 30 seconds without cleanup |
| Human inspect | CLI test with load-bearing and unknown gaps | Blocking counts visible in human output |
| Enforcement parity | doctor, release, migration-preflight, and hygiene-sweep focused tests | Same typed closure decision and digest |
| Quality | Ruff check/format on all changed Python paths; `git diff --check`; exact Files Changed audit | Clean and scoped |
| Preflight | applicability and mandatory clause preflights against exact filed content | No missing required spec or blocking gap |

## Acceptance Criteria

1. The exact 128 declared present capability paths are registered atomically;
   all 156 operative capability paths resolve and no operative path is missing.
2. Reconciliation reports zero `unregistered_load_bearing` and zero
   `invalid_unknown` before any `membership_complete` claim.
3. Every high-confidence observer is typed, provenance-bearing, deterministic,
   and unable to grant membership.
4. `coverage_complete` is exact set/classification closure; the prior count-only
   predicate is impossible.
5. Disposable subtrees are pruned only when neither registry nor observer has a
   descendant and no unsafe filesystem boundary is present.
6. Human inspect exposes blocking counts. Doctor, validate, release, migration,
   and sweep consume one classification result and fail closed on blockers.
7. Current-root reconciliation completes under 30 seconds without deleting,
   moving, or ignoring unregistered data.
8. Registry declaration, packaged mirror, projection, revisions, and transaction
   receipt are coherent/current after admission.
9. No target outside `target_paths` is mutated. `groundtruth.db` remains
   by-reference in Files Changed and finalizer include lists.
10. No WI-5640 Stage B mutation or obsolete-source deletion occurs. WI-5640
    remains paused unless v4-017 is independently VERIFIED and finalized and this
    thread reaches independent VERIFIED with `membership_complete: true`.
11. No dispatcher/TAFE activation or configuration mutation, harness-role
    mutation, Git staging/commit/push, release, deployment, credential, cleanup,
    or history rewrite occurs.

## Risks And Rollback

A broad glob would retain disposable debris; exact admission prevents that.
Incomplete observer coverage could falsely classify a needed artifact as
disposable; zero-unknown closure, typed sources, exact provenance, and
cross-source fixtures are mandatory before sweep eligibility.

Subtree pruning is the highest-risk performance change. It is allowed only after
registered and observer ancestor sets are fixed and must fail closed on
reparse/unreadable boundaries.

Registry apply uses the existing journal and recover path. Any failure before
commit restores or retains the old coherent generation; any indeterminate state
is recovery-required. No source file is deleted as rollback.

## Owner Decisions / Input

The owner already directed that the registry is ultimate membership authority,
that every non-disposable artifact be registered, that unregistered artifacts
are disposable only through governed sweep, and that registry completeness be
corrected before WI-5640 continues. No new owner decision is required.

## Pre-Filing Preflight

Run `bridge_applicability_preflight.py` and
`adr_dcl_clause_preflight.py` against this exact candidate. File only when
applicability passes with no missing required specification and the mandatory
clause preflight exits zero.

## Requested Loyal Opposition Action

Independently reproduce the 156/128 operative capability join and inspect the
four-class authority model, exact admission ceiling, false WI-5014 predicate,
subtree-pruning safety, shared-path sequencing with v4-015, and enforcement
consumers. File GO only if the scope can mechanically reach zero unknown and
zero unregistered-load-bearing without retaining disposable debris or
authorizing cleanup. Otherwise file one exact NO-GO revision.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
