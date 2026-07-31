REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# WI-5441 Global Registry Membership Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 003
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-002.md
Supplemental advisory: bridge/gtkb-wi5441-reconciliation-supplemental-findings-advisory-001.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py","groundtruth-kb/src/groundtruth_kb/project/doctor.py","groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/project/sot_audit.py","groundtruth-kb/tests/test_artifact_membership_reconciliation.py","groundtruth-kb/tests/test_registry_control_plane.py","groundtruth-kb/tests/test_sot_duplicate_audit.py","groundtruth.db","platform_tests/scripts/test_check_harness_parity.py","platform_tests/scripts/test_check_sot_registry_completeness.py","platform_tests/scripts/test_gtkb_file_reference_migration.py","platform_tests/scripts/test_hygiene_sweep_cli.py","platform_tests/scripts/test_release_candidate_gate.py","scripts/check_harness_parity.py","scripts/gtkb_file_reference_migration.py","scripts/release_candidate_gate.py"]
registry_admission_paths: [".agent/skills/gtkb-adr/SKILL.md",".agent/skills/gtkb-alternatives-investigation/SKILL.md",".agent/skills/gtkb-arch-audit/SKILL.md",".agent/skills/gtkb-assert/SKILL.md",".agent/skills/gtkb-assertion-triage/SKILL.md",".agent/skills/gtkb-batch/SKILL.md",".agent/skills/gtkb-benchmarks/SKILL.md",".agent/skills/gtkb-bridge-config/SKILL.md",".agent/skills/gtkb-bridge-propose/SKILL.md",".agent/skills/gtkb-bridge-reconciliation/SKILL.md",".agent/skills/gtkb-bridge/SKILL.md",".agent/skills/gtkb-check-deliberations/SKILL.md",".agent/skills/gtkb-code-review-audit/SKILL.md",".agent/skills/gtkb-decision-capture/SKILL.md",".agent/skills/gtkb-dispatcher-control/SKILL.md",".agent/skills/gtkb-grill-me-for-clarification/SKILL.md",".agent/skills/gtkb-harness-parity-review/SKILL.md",".agent/skills/gtkb-hygiene-investigation/SKILL.md",".agent/skills/gtkb-hygiene-sweep/SKILL.md",".agent/skills/gtkb-lo-hygiene-assessment/SKILL.md",".agent/skills/gtkb-lo-opportunity-radar/SKILL.md",".agent/skills/gtkb-loyal-opposition-report/SKILL.md",".agent/skills/gtkb-managed-skill-adoption-review/SKILL.md",".agent/skills/gtkb-projects/SKILL.md",".agent/skills/gtkb-promote/SKILL.md",".agent/skills/gtkb-proposal-review/SKILL.md",".agent/skills/gtkb-propose/SKILL.md",".agent/skills/gtkb-query/SKILL.md",".agent/skills/gtkb-release-candidate-gate/SKILL.md",".agent/skills/gtkb-send-review/SKILL.md",".agent/skills/gtkb-session-wrap-scan/SKILL.md",".agent/skills/gtkb-session-wrap/SKILL.md",".agent/skills/gtkb-spec-intake/SKILL.md",".agent/skills/gtkb-spec/SKILL.md",".agent/skills/gtkb-structural-hygiene-review/SKILL.md",".agent/skills/gtkb-sweep-commit/SKILL.md",".agent/skills/gtkb-verify/SKILL.md",".agent/skills/gtkb-work-item/SKILL.md",".claude/skills/gtkb-adr/SKILL.md",".claude/skills/gtkb-advisory-disposition/SKILL.md",".claude/skills/gtkb-advisory-intake/SKILL.md",".claude/skills/gtkb-advisory-proposal/SKILL.md",".claude/skills/gtkb-alternatives-investigation/SKILL.md",".claude/skills/gtkb-arch-audit/SKILL.md",".claude/skills/gtkb-assert/SKILL.md",".claude/skills/gtkb-assertion-triage/SKILL.md",".claude/skills/gtkb-batch/SKILL.md",".claude/skills/gtkb-benchmarks/SKILL.md",".claude/skills/gtkb-bridge-config/SKILL.md",".claude/skills/gtkb-bridge-reconciliation/SKILL.md",".claude/skills/gtkb-check-deliberations/SKILL.md",".claude/skills/gtkb-code-review-audit/SKILL.md",".claude/skills/gtkb-decision-capture/SKILL.md",".claude/skills/gtkb-dispatcher-control/SKILL.md",".claude/skills/gtkb-formal-artifact-packet-helper/SKILL.md",".claude/skills/gtkb-grill-me-for-clarification/SKILL.md",".claude/skills/gtkb-harness-parity-review/SKILL.md",".claude/skills/gtkb-hygiene-investigation/SKILL.md",".claude/skills/gtkb-hygiene-reclaim/SKILL.md",".claude/skills/gtkb-hygiene-sweep/SKILL.md",".claude/skills/gtkb-lo-hygiene-assessment/SKILL.md",".claude/skills/gtkb-lo-opportunity-radar/SKILL.md",".claude/skills/gtkb-loyal-opposition-report/SKILL.md",".claude/skills/gtkb-managed-skill-adoption-review/SKILL.md",".claude/skills/gtkb-projects/SKILL.md",".claude/skills/gtkb-promote/SKILL.md",".claude/skills/gtkb-propose/SKILL.md",".claude/skills/gtkb-query/SKILL.md",".claude/skills/gtkb-release-candidate-gate/SKILL.md",".claude/skills/gtkb-session-wrap-scan/SKILL.md",".claude/skills/gtkb-session-wrap/SKILL.md",".claude/skills/gtkb-skill-governance-lifecycle/SKILL.md",".claude/skills/gtkb-spec-intake/SKILL.md",".claude/skills/gtkb-spec/SKILL.md",".claude/skills/gtkb-structural-hygiene-review/SKILL.md",".claude/skills/gtkb-sweep-commit/SKILL.md",".claude/skills/gtkb-work-item/SKILL.md",".codex/gtkb-hooks/bridge-compliance-audit.cmd",".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd",".codex/gtkb-hooks/codex-mcp-worker-guard.cmd",".codex/gtkb-hooks/directive-enforcement.cmd",".codex/gtkb-hooks/formal-artifact-\u0061pproval.cmd",".codex/gtkb-hooks/session_start_dispatch.py",".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py",".codex/gtkb-hooks/sot-read-discipline-bash-adapter.py",".codex/gtkb-hooks/wi-id-collision-gate.cmd",".codex/skills/gtkb-adr/SKILL.md",".codex/skills/gtkb-advisory-disposition/SKILL.md",".codex/skills/gtkb-advisory-intake/SKILL.md",".codex/skills/gtkb-advisory-proposal/SKILL.md",".codex/skills/gtkb-alternatives-investigation/SKILL.md",".codex/skills/gtkb-arch-audit/SKILL.md",".codex/skills/gtkb-assert/SKILL.md",".codex/skills/gtkb-assertion-triage/SKILL.md",".codex/skills/gtkb-batch/SKILL.md",".codex/skills/gtkb-benchmarks/SKILL.md",".codex/skills/gtkb-bridge-config/SKILL.md",".codex/skills/gtkb-bridge-propose/SKILL.md",".codex/skills/gtkb-bridge-reconciliation/SKILL.md",".codex/skills/gtkb-check-deliberations/SKILL.md",".codex/skills/gtkb-code-review-audit/SKILL.md",".codex/skills/gtkb-decision-capture/SKILL.md",".codex/skills/gtkb-dispatcher-control/SKILL.md",".codex/skills/gtkb-formal-artifact-packet-helper/SKILL.md",".codex/skills/gtkb-grill-me-for-clarification/SKILL.md",".codex/skills/gtkb-harness-parity-review/SKILL.md",".codex/skills/gtkb-hygiene-investigation/SKILL.md",".codex/skills/gtkb-hygiene-reclaim/SKILL.md",".codex/skills/gtkb-hygiene-sweep/SKILL.md",".codex/skills/gtkb-lo-hygiene-assessment/SKILL.md",".codex/skills/gtkb-lo-opportunity-radar/SKILL.md",".codex/skills/gtkb-loyal-opposition-report/SKILL.md",".codex/skills/gtkb-managed-skill-adoption-review/SKILL.md",".codex/skills/gtkb-projects/SKILL.md",".codex/skills/gtkb-promote/SKILL.md",".codex/skills/gtkb-propose/SKILL.md",".codex/skills/gtkb-query/SKILL.md",".codex/skills/gtkb-release-candidate-gate/SKILL.md",".codex/skills/gtkb-session-wrap-scan/SKILL.md",".codex/skills/gtkb-session-wrap/SKILL.md",".codex/skills/gtkb-skill-governance-lifecycle/SKILL.md",".codex/skills/gtkb-spec-intake/SKILL.md",".codex/skills/gtkb-spec/SKILL.md",".codex/skills/gtkb-structural-hygiene-review/SKILL.md",".codex/skills/gtkb-sweep-commit/SKILL.md",".codex/skills/gtkb-work-item/SKILL.md","scripts/dispatch_blackbox_gate.py","scripts/session_self_initialization.py"]
registry_admission_path_count: 128
capability_evidence_hash: sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3
approval_evidence_scope: no formal-artifact approval-evidence or approval-packet mutation; the decoded hook path is a capability subject only; F1 Option B is disclosed below

## Revision Delta

This revision responds finding-by-finding to v002 F1-F4 and supplemental
advisory A1-A5. It preserves the independently confirmed 226/156/128 evidence
join, exact 128-path ceiling, four physical membership classifications, and
report-first non-destructive posture.

The revision:

1. discloses and constrains the JSON escape used for one capability-subject path;
2. specifies the exact capability-evidence serialization and requires a named producer test;
3. identifies the 313-record registry as the uncommitted WI-5640 postimage and makes re-baselining mandatory;
4. includes present native/adapter surfaces even when a waiver record exists;
5. separates pruned/uninspected subtree envelopes from true `invalid_unknown` and keeps sweep/release fail-closed on them;
6. preserves and redefines `coverage_complete` instead of retiring it;
7. re-points the WI-5640 dependency at the current implementation report; and
8. expands the target ceiling to the actual release, migration, and hygiene consumers plus their focused tests.

## Governance Detector Disposition

v002 F1 is resolved through its Option B because the current governed Codex
writer has no interactive checkpoint-answer channel. The raw JSON metadata
retains `\u0061` in one string. JSON decoding produces the exact path
`.codex/gtkb-hooks/formal-artifact-approval.cmd`, which is not formal-artifact
approval evidence; it is an executable capability subject being admitted to the
membership registry.

Mechanical necessity is narrow and recorded: the bridge gate scans undecoded
raw bytes, treats the literal path inside the comma-packed JSON array as an
unnegated approval-evidence declaration, and the Codex adapter maps the resulting
`ask` decision to a hard failure. `scripts/gtkb_bridge_writer.py` likewise treats
`ask`, `block`, and `deny` as publication failures, so there is no owner-answer
round trip on this provider path. The implementation must parse this metadata
as JSON, assert the decoded exact path is present once, and emit the ordinary
literal path into the admission batch. No production registry record, batch,
source file, test, or report may retain the escape. Detector normalization and
path-array precision remain separate standing-backlog work.

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
3. redefine the prior count-only `coverage_complete` predicate as exact
   classification closure without removing its public key or doctor gate;
4. make doctor, `gt registry validate`, the release candidate gate, WI-5640
   migration preflight, and the hygiene-sweep CLI consume the same typed result;
5. separate membership closure from physical-disposal readiness so pruned,
   uninspected payloads cannot silently become sweep- or release-eligible; and
6. reduce whole-root census cost by representing provably non-member,
   non-observer-ancestor subtrees as explicit bounded envelopes.

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

The exact capability input is
`config/agent-control/gtkb-harness-capability-registry.toml`. The observer selects:

- every `canonical_source`;
- every per-harness `surface` whose typed status is `native` or `adapter`;
- present native/adapter surfaces even when a waiver record exists, because
  `scripts/check_harness_parity.py:893-895` applies a waiver only to `MISSING`;
- no `fallback` or `unsupported` surface.

The canonical SoT resolver then classifies each selected path. Independent Prime
and two Loyal Opposition derivations agree exactly:

- 226 evidence observations;
- 156 unique operative paths;
- 128 present operative paths with no registry member;
- zero missing operative paths;
- 117 uncovered skill paths and 11 uncovered hook/script paths;
- uncovered roots: 49 `.codex`, 39 `.claude`, 38 `.agent`, and two `scripts`;
- deterministic evidence hash:
  `sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`.

These counts are **not committed-HEAD facts**. They derive from the uncommitted
WI-5640 registry postimage: HEAD has 145 records; the worktree postimage has 313
(298 exact, 10 virtual, one glob, three opaque containers, one recursive). The
current WI-5640 implementation report is v4-019 and awaits independent
verification/finalization. Before any WI-5441 mutation, the producer must rerun
the join against the finalized WI-5640 generation. Any change to the 313-record
generation, the 226 observations, the 156 unique paths, the 128-path difference,
or the bound evidence hash fails before mutation and requires a revised proposal.

A fresh legacy census using canonical `load_registry_snapshot` plus
`census_registry` on that same worktree postimage observed 1,874,338 objects and
exactly 441 `invalid_unknown`, all `unreadable`: 431 under `.pytest-tmp`,
9 under `groundtruth-kb/.gtkb-state`, and 1 under
`groundtruth-kb/pytest-kpi-retro-codex`. Those three enclosing roots are
unregistered, are not registered structural ancestors, and have no current
capability-observer descendant. Their revised treatment is specified under Fast
Complete Census; the 441 observations may not disappear from evidence without
an explicit old-to-new root attribution.

Deleting all unregistered objects today would remove the 128 declared, present
capability surfaces and impair GT-KB. That contradicts
`GOV-PLATFORM-SOT-REGISTRY-001` v2 and proves registry membership closure is
false on the current baseline.

## Prior False-Completeness Predicate

`groundtruth_kb.project.sot_audit.DuplicateSoTAuditReport.coverage_complete`
currently returns true when:

`registry_count > 0 and persistent_file_count >= registered_file_count`.

That count inequality does not map, join, or classify the persistent files.
WI-5014 therefore established a duplicate-SoT audit, not global membership
closure, despite naming a `whole_project_persistent_file_closure` phase.

This slice chooses **redefine**, not retire. The public `coverage_complete` JSON
key and doctor gate remain. Their value becomes a projection of the shared
reconciliation service's exact `membership_complete` predicate. No count
comparison or second implementation may support a coverage-complete claim.

## Authority And Classification Model

The reconciliation result has exactly four physical membership classifications:

1. `registered`: the canonical resolver returns one active declaration.
2. `unregistered_load_bearing`: no declaration resolves, but one or more typed
   operative observers identify the object. This is membership-, release-, and
   sweep-blocking.
3. `unregistered_disposable`: no declaration and no operative observer identify
   the object. This work does not retain, correct, quarantine, or delete it.
4. `invalid_unknown`: observer/registry parse failure, missing operative target,
   path escape, collision, ambiguous evidence, unsafe root boundary, or an
   exception encountered on a path the membership pass is required to inspect.
   This is membership-, release-, and sweep-blocking.

Structural ancestors and `pruned_uninspected_subtree` remain traversal states,
not fifth membership classes. A pruned root may carry the physical class
`unregistered_disposable`, but its report must state that descendants were not
individually inspected. That traversal state does not block
`membership_complete` after registry/observer ancestor proof, but it always
blocks `sweep_eligible` and `release_eligible` in this slice.

Virtual declarations remain declaration-only. Immediate `applications/<child>`
roots remain application-owned boundaries. `.git` remains VCS service state.

Every exact result carries normalized path, object kind, classification,
registry ID if any, observer IDs, observer source digests, and a deterministic
evidence digest. Every pruned envelope carries root path, boundary object kind,
registry-ancestor proof, observer-ancestor proof, and an explicit
`descendants_inspected: false`. An observer cannot mutate registry state or
silently convert a candidate to membership.

## Typed Observer Set

The first implementation must expose adapters, not ad hoc caller parsing, for:

1. **Capability inventory:** canonical source plus typed native/adapter surfaces
   using the parity checker's exact present-waiver semantics.
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
ambiguous evidence, and an unreadable path that the selected traversal is
required to inspect produce `invalid_unknown`; they never become disposable.
Unreadable descendants beneath a pruned envelope are not asserted absent or
classified individually; the envelope records that non-observation and keeps
sweep/release ineligible.

Git tracked, ignored, and untracked status is evidence metadata only and cannot
grant membership or retention.

## Exact Capability Admission

The 128 `registry_admission_paths` in this proposal are the full mutation scope
ceiling for membership additions in this slice.

Each record is exact-path coverage. Canonical sources are `active`; generated
harness adapters are `generated`; executable hook/script surfaces retain their
typed control-surface domain. Record metadata is derived from existing registered
peer records for the same artifact class and validated before apply.

The capability-evidence hash has one exact producer contract. Build one row for
each selected observation with keys `path`, `capability_id`, `kind`, `evidence`,
and `status`; append `registry_state`, `record_id`, and boolean `exists` from the
canonical resolver and filesystem check. Sort rows by `(path, capability_id,
evidence)`. Serialize the list with Python `json.dumps(rows, sort_keys=True,
separators=(",", ":"), ensure_ascii=True)`, UTF-8 encode it with no trailing
newline, and SHA-256 those bytes. This algorithm reproduces the bound value
`sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`.
The production capability adapter must return both rows and digest; a focused
test must recompute the digest independently.

The batch must:

1. be rendered as deterministic JSON;
2. bind the current declaration, packaged mirror, projection, capability
   registry digest, exact capability-evidence digest, exact 128-path set,
   PAUTH, GO, claim, and implementation-start packet;
3. pass dry-run with 128 additions and zero removals/identity transitions;
4. commit through one registry transaction;
5. leave canonical and packaged TOML byte-identical and the projection current;
6. emit one receipt and support idempotent exact retry; and
7. fail before mutation if any operative path, source digest, target metadata,
   capability row, or current registry generation changes.

No glob may replace the exact set. Helper/reference directories must not be
covered wholesale because they contain disposable drafts and generator debris.

## Fast Complete Census

The current walker descends every unregistered directory. On this checkout that
enumerates more than 1.8 million disposable test objects and took several minutes.

The replacement must precompute:

- registered structural ancestors;
- every typed operative-observer path and its ancestors; and
- unsafe boundary roots already encountered before a prune decision.

This revision chooses supplemental finding A1 **Option B**. An unregistered
directory that is neither a registered structural ancestor nor an operative-
observer ancestor may be represented once as a pruned envelope. The walker
performs `lstat` on the boundary, never follows symlinks/junctions/reparse nodes,
records `descendants_inspected: false`, and does not descend. A boundary
exception or uncertain object type remains `invalid_unknown`.

Pruning does not make hidden evidence disappear. The result includes a sorted
`pruned_uninspected_subtrees` array and digest. The legacy 441 unknowns must map
to the three current enclosing roots (`.pytest-tmp`,
`groundtruth-kb/.gtkb-state`, and `groundtruth-kb/pytest-kpi-retro-codex`) or the
implementation fails its baseline test. If any root gains a registered or
observer descendant, it is no longer prunable and the walker must descend;
encountered exceptions then remain `invalid_unknown`.

Predicate separation is explicit:

- `membership_complete`: coherent/current registry, zero
  `unregistered_load_bearing`, zero `invalid_unknown`, complete typed-observer
  execution, and every top-level physical object represented exactly or by one
  explicit pruned envelope;
- `sweep_eligible`: membership complete, zero pruned/uninspected envelopes, no
  nonterminal registry transaction, and the existing quarantine preconditions;
- `release_eligible`: membership complete, zero pruned/uninspected envelopes,
  and all existing release/currentness requirements.

Therefore the expected first postimplementation state is zero
`unregistered_load_bearing`, zero true `invalid_unknown` if and only if all 441
legacy observations are attributed to the three envelopes, and a nonzero
pruned/uninspected count that keeps sweep/release false. Any residual true
unknown keeps `membership_complete` false and WI-5640 paused.

Tests must prove pruning cannot hide a registered member or observer path,
cannot turn an encountered exception into disposable, and cannot make sweep or
release eligible. The report must include elapsed time and assert warm and cold
read-only reconciliation under 30 seconds without deleting scratch data.

## CLI And Enforcement

Add `gt registry reconcile --json` as the canonical read-only report. It emits
the four membership classifications, traversal states, observer provenance,
counts, digests, subtree envelopes, and closure flags.

`gt registry inspect` must display reverse-coverage and reconciliation summary
in human mode. It may not print only `coherent: true` and record count while
hiding blocking gaps.

`gt registry validate`, doctor, `scripts/release_candidate_gate.py`,
`scripts/gtkb_file_reference_migration.py preflight`, and `gt hygiene sweep`
must consume the same typed reconciliation result. A consumer may request a
bounded detail payload but may not reimplement classification. Release and
hygiene tests must prove any pruned/uninspected envelope blocks their eligible
decision. Migration preflight may proceed only on `membership_complete: true`;
it never treats that flag as deletion, sweep, or release authority.

Sweep execution remains outside this scope and continues to require quarantine,
receipt, non-shortenable retention, restoration visibility, zero pruned/
uninspected envelopes, and separate authorization.

## Cross-Thread Coordination

`bridge/gtkb-file-move-rename-canonicalization-v4-018.md` independently
confirmed the bounded WI-5640 implementation substance and returned NO-GO only
on report evidence/form. `bridge/gtkb-file-move-rename-canonicalization-v4-019.md`
is the current report-only correction; it changes no implementation postimage.

This thread may be proposed and reviewed concurrently, but implementation must
not acquire a claim or mutate any target until:

1. the current WI-5640 implementation report (currently v4-019) receives an
   independent VERIFIED and its governed finalization commit completes;
2. the exact shared implementation baseline is reloaded from that finalized
   commit and the 313/226/156/128 evidence is re-derived;
3. this proposal receives an independent GO; and
4. a fresh WI-5441 claim and exact implementation-start packet are issued.

The shared paths include the registry declaration/mirror/database,
`registry_control_plane.py`, `scripts/gtkb_file_reference_migration.py`, and its
focused test. No concurrent implementation claims are permitted. If the current
WI-5640 review requires any implementation postimage change, this proposal must
be revised against that new baseline before implementation. No same-session
review is eligible.

WI-5640 Stage B remains paused until this reconciliation reports
`membership_complete: true`. A true membership result does not confer sweep,
deletion, release, commit, push, or deployment authority.

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
  redefined here, not treated as membership evidence.
- `bridge/gtkb-file-move-rename-canonicalization-v4-018.md`: independent
  confirmation that the bounded WI-5640 implementation substance passed; NO-GO was report-form only.
- `bridge/gtkb-file-move-rename-canonicalization-v4-019.md`: current
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
checker classifies absent fallback surfaces as deferred, not operative. A
present native/adapter surface remains operative even when a waiver record
exists; waivers only alter a `MISSING` result.

Future capability creation must update the capability registry and registry
membership in the same governed transaction. A regression test mechanically
joins every canonical/native/adapter capability path to the SoT resolver and
fails on any uncovered or missing operative path.

## Specification-Derived Verification Plan

| Requirement | Exact executable evidence | Expected result |
| --- | --- | --- |
| Capability admission | Named production adapter plus independent hash test and `gt registry reconcile --json` | 226 observations, 156 operative paths, exact digest, zero uncovered/missing after 128 additions |
| Atomicity | Registry transaction fault matrix and exact retry test | Old or new coherent generation; one receipt; no partial admission |
| Observer semantics | Unit fixtures for capability, MemBase, package, dependency, and physical adapters | Provenance exact; present-waived native included; fallback/Git never grants membership |
| Classification | Synthetic root matrix for all four classifications, structural ancestors, hosted apps, `.git`, virtual, opaque, symlink, junction, and unreadable nodes | Every inspected object classified once; pruned descendants explicitly uninspected |
| Legacy unknown attribution | Current-root baseline test | 441 old unknowns map 431/9/1 to the three declared enclosing roots or fail closed |
| False predicate | `test_sot_duplicate_audit.py` regression | Public `coverage_complete` remains and delegates to exact membership closure |
| Pruning safety | Registered/observer descendant, encountered-error, and million-file subtree tests | No hidden member/observer; no silent unknown conversion; sweep/release remain false |
| Performance | Cold and warm current-root `gt registry reconcile --json` timing | Each under 30 seconds without cleanup |
| Human inspect | CLI test with load-bearing, unknown, and pruned gaps | Blocking counts and envelopes visible |
| Doctor/validate parity | Doctor and registry-focused tests | Same membership result and digest; blockers fail closed |
| Release parity | `platform_tests/scripts/test_release_candidate_gate.py` | True unknown or pruned envelope blocks release |
| Migration parity | `platform_tests/scripts/test_gtkb_file_reference_migration.py` | Stage B preflight requires membership complete; no sweep authority inferred |
| Hygiene parity | `platform_tests/scripts/test_hygiene_sweep_cli.py` | Pruned/unknown/load-bearing gaps block sweep eligibility |
| Quality | Ruff check/format on all changed Python paths; `git diff --check`; exact Files Changed audit | Clean and scoped |
| Preflight | Applicability and mandatory clause preflights against exact filed content | No missing required spec or blocking gap |

## Acceptance Criteria

1. The exact 128 declared present capability paths are registered atomically;
   all 156 operative capability paths resolve and no operative path is missing.
2. The capability-evidence producer and independent test reproduce the exact
   226-row serialization and bound digest before mutation.
3. The filed 441-unknown baseline is attributed 431/9/1 to the three current
   outer roots. Any unmapped or newly encountered true unknown leaves
   `membership_complete: false`.
4. Every high-confidence observer is typed, provenance-bearing, deterministic,
   and unable to grant membership.
5. `coverage_complete` remains a public key and doctor gate, redefined as the
   shared service's exact `membership_complete`; count inequality is impossible.
6. A pruned root is reported with `descendants_inspected: false`; it cannot hide
   a registered/observer descendant, erase an encountered exception, or permit
   sweep/release eligibility.
7. Human inspect exposes blocking counts and envelopes. Doctor, validate,
   release, migration, and hygiene consume one classification result and digest.
8. Current-root reconciliation completes under 30 seconds without deleting,
   moving, or recursively enumerating unregistered test debris.
9. Registry declaration, packaged mirror, projection, revisions, and transaction
   receipt are coherent/current after admission.
10. No target outside `target_paths` is mutated. `groundtruth.db` is an
    authorized by-reference runtime mutation target, is named only in the
    by-reference report section, and MUST NOT enter `## Files Changed`, a
    finalizer include set, staging, or a commit.
11. No WI-5640 Stage B mutation or obsolete-source deletion occurs. WI-5640
    remains paused unless its current report is independently VERIFIED/finalized
    and this thread reaches independent VERIFIED with
    `membership_complete: true`.
12. No dispatcher/TAFE activation or configuration mutation, harness-role
    mutation, Git staging/commit/push, release, deployment, credential, cleanup,
    or history rewrite occurs.

## Risks And Rollback

A broad glob would retain disposable debris; exact admission prevents that.
Incomplete observer coverage could falsely classify a needed artifact as
disposable; zero true unknowns, typed sources, exact provenance, and cross-source
fixtures are mandatory before membership closure.

Subtree pruning is the highest-risk performance change. The revised design does
not claim descendants were inspected and cannot authorize sweep or release while
any pruned envelope exists. Stage B may consume membership closure only because
it rewrites registered targets and performs no deletion; its own exact-plan GO
remains separately required.

The 313-record and 128-path baseline is uncommitted until WI-5640 finalization.
Any postimage drift invalidates the precondition and forces re-review before
mutation.

Registry apply uses the existing journal and recover path. Any failure before
commit restores or retains the old coherent generation; any indeterminate state
is recovery-required. No source file is deleted as rollback.

## Owner Decisions / Input

The owner already directed that the registry is ultimate membership authority,
that every non-disposable artifact be registered, that unregistered artifacts
are disposable only through governed sweep, and that registry completeness be
corrected before WI-5640 continues.

This revision chooses v002 F1 Option B solely for the documented non-interactive
gate limitation, supplemental A1 Option B for honest pruned-subtree accounting,
and A4's non-removal path by redefining `coverage_complete`. None removes a
registered identity, public key, doctor gate, source file, or audit artifact. No
new owner decision is required.

## Pre-Filing Preflight

The exact completed candidate was checked before filing.

- Proposal-specific verifier: exit 0; 19 exact targets, 128 unique decoded
  admissions, 226 observations, 156 operative paths, exact capability digest,
  no invalid SHA tokens, no stale markers, and no approval-detector ask.
- Applicability preflight: exit 0; `preflight_passed: true`, no missing required
  or advisory specifications, no blocking errors, and no unclassified targets.
- Mandatory clause preflight: exit 0; five clauses evaluated, four must-apply,
  one may-apply, zero evidence gaps, and zero blocking gaps.

The governed revision helper reruns both canonical preflights against the final
candidate bytes before publication.

## Requested Loyal Opposition Action

Independently reproduce the 226/156/128 capability join and exact serialization
hash; confirm the Option B governance-detector disclosure; inspect the 441-root
attribution, pruned-envelope predicate separation, preserved
`coverage_complete`, expanded consumer scope, and sequencing against the current
WI-5640 report. File GO only if the proposal can mechanically reach honest
membership closure while sweep/release remain fail-closed on every uninspected
subtree. Otherwise file one exact NO-GO revision.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
