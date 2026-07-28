REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5441 Global Registry Membership And Liveness Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 007
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md
Prior proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-005.md
Supplemental advisory: bridge/gtkb-wi5441-reconciliation-supplemental-findings-advisory-001.md
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["config/governance/narrative-artifact-approval.toml","config/hooks/gtkb-formal-artifact-approval-gate.py","config/hooks/gtkb-narrative-artifact-approval-gate.py","config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/bridge/taxonomy.py","groundtruth-kb/src/groundtruth_kb/cli.py","groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml","groundtruth-kb/src/groundtruth_kb/db.py","groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py","groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py","groundtruth-kb/src/groundtruth_kb/project/doctor.py","groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py","groundtruth-kb/src/groundtruth_kb/project/sot_audit.py","groundtruth-kb/src/groundtruth_kb/project/sot_registry.py","groundtruth-kb/tests/test_artifact_membership_reconciliation.py","groundtruth-kb/tests/test_db.py","groundtruth-kb/tests/test_doctor.py","groundtruth-kb/tests/test_registry_control_plane.py","groundtruth-kb/tests/test_sot_duplicate_audit.py","groundtruth-kb/tests/test_sot_registry.py","groundtruth.db","platform_tests/hooks/test_formal_artifact_approval_gate.py","platform_tests/hooks/test_narrative_artifact_approval.py","platform_tests/scripts/test_bridge_kind_taxonomy.py","platform_tests/scripts/test_check_harness_parity.py","platform_tests/scripts/test_check_narrative_artifact_evidence.py","platform_tests/scripts/test_check_protected_commit_authorization.py","platform_tests/scripts/test_check_sot_registry_completeness.py","platform_tests/scripts/test_gtkb_file_reference_migration.py","platform_tests/scripts/test_hygiene_sweep_cli.py","platform_tests/scripts/test_implementation_start_gate.py","platform_tests/scripts/test_registry_observation_hook.py","platform_tests/scripts/test_release_candidate_gate.py","scripts/check_harness_parity.py","scripts/check_narrative_artifact_evidence.py","scripts/check_protected_commit_authorization.py","scripts/gtkb_file_reference_migration.py","scripts/implementation_start_gate.py","scripts/migrate_bridge_kind_taxonomy.py","scripts/registry_observation_hook.py","scripts/release_candidate_gate.py"]
registry_admission_policy: {"allowed_operations":["add_exact_member","add_recursive_service_container","append_content_observation"],"bind_before_mutation":["sorted_exact_candidate_manifest","candidate_manifest_sha256","observer_input_digests","registry_generation_digest","dry_run_receipt"],"forbidden_operations":["delete_member","move_member","rename_member","retire_member","shrink_coverage","replace_exact_set_with_broad_glob"],"mode":"deterministic_additive_only","observer_classes":["capability_inventory","governed_knowledge","package_and_entrypoint","registered_dependency_closure","physical_census"],"scope":"present in-root load-bearing candidates proven by all successful typed observers"}
approval_evidence_scope: no formal-artifact approval-evidence or approval-packet work in this parent; the child thread owns the six packet targets
specification_dependency: {"child_thread":"gtkb-wi5441-owner-liveness-spec-amendments","readback_bytes":20460,"readback_sha256":"sha256:27c07974b72264dba355290bc253e55088d2be1df3eb2b59c8cccab93e8ba36d","required_versions":["GOV-PLATFORM-SOT-REGISTRY-001:v3","DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001:v2","DCL-SOT-REGISTRY-RECORD-SCHEMA-001:v4","DCL-SOT-REGISTRY-PROJECTION-PARITY-001:v3","GOV-ARTIFACT-APPROVAL-001:v4","DCL-ARTIFACT-APPROVAL-HOOK-001:v5"],"status":"satisfied","terminal_commit":"9c22e02c28b1347503abeab228e27c36f6d0e947","terminal_verdict":"bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md"}
taxonomy_dependency: {"absorbed_scope":["governance_review enum","governance_review migration preservation","focused taxonomy regression"],"source_work_item":"WI-5479","remaining_scope":"role/domain-neutral advisory-report taxonomy plus missing authority specification and all adapters","status":"bounded_dependency_absorption"}
commit_clearance_dependency: {"implementation_report":"bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md","overlapping_targets":["scripts/check_protected_commit_authorization.py","platform_tests/scripts/test_check_protected_commit_authorization.py"],"status":"terminal_verified","terminal_commit":"1c82158e82b517a531ffa343c38cc2b1e71507b3","terminal_verdict":"bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md","thread":"gtkb-wi5441-bridge-publication-capability-commit-clearance"}

## Revision Claim

Complete the registry before WI-5640 Stage B while preserving the owner's
operational-liveness rule. The registry remains the sole authority for artifact
membership and identity. It is not a file-permission security boundary, and its
audit ledger does not decide whether the current bytes of a registered artifact
are usable.

This revision replaces three unsafe assumptions in v003:

1. The fixed 128-path capability admission was not global completeness. A
   canonical governed-knowledge scan found another 107 present, unregistered
   paths before package, entrypoint, audit-trail, and hook-root expansion.
2. Direct content observation cannot be a mandatory precondition for ordinary
   editing, build, or test work. A Notepad save carries no governance notation
   and must remain immediately effective.
3. A governance mechanism that is obsolete, unavailable, or under repair must
   not recursively require itself to authorize its own correction when no
   functioning compliant route exists.

The implementation will create one typed reconciliation service, admit every
present load-bearing gap it proves through a deterministic additive-only batch,
and make worker audit capture automatic on the normal path. Missing audit
capture remains visible audit debt but never invalidates content or blocks
ordinary local work.

No file move, rename, reference rewrite, quarantine, deletion, push, release,
deployment, dispatcher mutation, harness-role mutation, or WI-5640 Stage B apply
is authorized. This parent also makes one already-proven bridge dependency
durable: preserve `governance_review` as its own canonical enum and migration
value with a focused regression test. That bounded slice is absorbed from
WI-5479 because this child/parent chain currently depends on the uncommitted
repair. WI-5479 remains open for the separate role/domain-neutral advisory
taxonomy, missing authority specification, adapters, and broader acceptance.

## Requirement Sufficiency

Existing requirements sufficient, contingent on the child evidence named below
being replaced with exact filed and read-back identifiers before publication.

The six owner-liveness amendments are no longer implementation work in this
parent thread. They are owned by
`gtkb-wi5441-owner-liveness-spec-amendments`, whose bounded governance-review
scope is not parent packet work; the child contains six formal-artifact approval
records. This parent may be filed only after that child is independently GO'd,
implemented, independently
VERIFIED, and all six current MemBase descriptions reproduce the approved
versions exactly.

Required pre-filing evidence:

- child terminal verdict:
  `bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md`, finalized in
  commit `9c22e02c28b1347503abeab228e27c36f6d0e947`;
- six-spec normalized read-back digest:
  `sha256:27c07974b72264dba355290bc253e55088d2be1df3eb2b59c8cccab93e8ba36d`;
- digest schema: sort the six records by `artifact_id`, normalize CRLF and CR
  within each `description` to LF, serialize the JSON array containing
  `artifact_id`, `description`, `status`, and `version` as UTF-8 with sorted
  object keys, `ensure_ascii=false`, separators `(',', ':')`, and no trailing
  newline, then SHA-256 the resulting 20,460 bytes;
- current versions: `GOV-PLATFORM-SOT-REGISTRY-001` v3,
  `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2,
  `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4,
  `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3,
  `GOV-ARTIFACT-APPROVAL-001` v4, and
  `DCL-ARTIFACT-APPROVAL-HOOK-001` v5.

Until every placeholder above is replaced from live state, this file is a
non-dispatchable draft and cannot be published as `REVISED`.

## Owner Liveness And Hand-Edit Contract

WI-5441 version 11 records the controlling owner requirements from 2026-07-26.
They are acceptance requirements, not implementation suggestions:

1. A registered artifact may be edited directly in an ordinary editor such as
   Notepad. The bytes become the current artifact bytes immediately.
2. The edit requires no notation, marker, comment, command, filename convention,
   begin/end mode, editor integration, environment variable, or other signal.
3. Missing or failed audit capture, a bypassed GOV, or unknown actor identity is
   audit debt. None may cause the platform to reject, revert, quarantine, delay,
   or invalidate the content or block ordinary local edit, build, or test work.
4. Governed worker tools should leave attributable records automatically because
   that is the path of least resistance. When no trustworthy actor evidence is
   available, the platform may record `unattributed_external` and
   `direct_in_place_content_change`; it must not invent human or AI provenance.
5. Passive observation is best-effort recovery evidence. Failure to observe
   emits a visible diagnostic and remains retryable; it is not a denial.
6. Functional syntax, schema, and behavior checks remain valid. A malformed edit
   may fail a parser or test on its merits, but missing governance evidence alone
   cannot make it fail.
7. If the normal governance route is unavailable or the target is the broken
   governance mechanism itself, corrective local work proceeds repair-forward.
   The worker records the gap afterward when possible rather than losing the
   work or entering a recursive authorization loop.
8. The existing owner rules for registered move, rename, delete, locator,
   coverage, lifecycle, membership removal, destructive cleanup, and external
   release remain separately governed identity or irreversible-effect
   boundaries. A bypass discovered after the fact is repaired forward; this
   proposal does not claim filesystem security can make bypass impossible.

## Membership, Audit, And Liveness Are Separate

The shared service exposes three independent states:

- `membership_complete`: every operative in-root load-bearing artifact resolves
  to an active registry declaration; there are zero true
  `unregistered_load_bearing` and zero true `invalid_unknown` results after every
  required typed observer succeeds.
- `audit_complete`: all currently known content revisions have attributable or
  explicitly unattributed observation evidence. This is diagnostic and may be
  false without changing membership or ordinary operational liveness.
- `operational_liveness`: local edit, read, build, and test paths do not depend
  on audit completeness or an observation service being available.

`membership_complete` remains the owner-required WI-5640 Stage B precondition.
It also remains a destructive sweep and release precondition. It does not become
a universal source-edit permission gate. `audit_complete` is never a Stage B,
build, test, or content-validity precondition.

Registered content-digest drift is therefore an audit observation state, not a
membership failure. A missing registered path, object-kind change, ambiguous
locator, path escape, or coverage collision remains an identity failure and
keeps `membership_complete`, sweep, and release false.

## Direct-Edit And Worker Audit Flow

The control plane will implement the following ordered behavior:

1. A filesystem content edit at an existing registered locator is accepted.
2. A governed worker helper that knows the worker context appends an attributable
   revision automatically in the same normal workflow.
3. A hook, commit checker, inspection command, or periodic auditor may observe
   otherwise-unrecorded bytes and append best-effort evidence. When actor
   evidence is absent it uses honest unattributed provenance.
4. Observation failure reports `audit_gap` with path and reason, preserves the
   bytes, and returns success to ordinary local edit/build/test callers.
5. The commit checker hashes the staged blob. A matching governed or passive
   observation is useful evidence; absence of one cannot reject a registered
   content-only staged change. It may append staged-view evidence or report
   audit debt.
6. A later unstaged edit does not invalidate an earlier staged blob. Revision
   rows carry an `evidence_view` such as `working_tree`, `git_index`,
   `governed_tool`, `registry_transaction`, `bridge_publication`, or `recovery`,
   plus an optional source reference or Git blob OID.
7. Tool-context approval hooks may continue to make the governed worker route
   easiest when that route is functioning. An actor-blind file or pre-commit
   gate may not infer that missing packet evidence means an owner edit is
   forbidden.
8. Governance-repair targets use the same bytes-first rule. When the governed
   helper is unavailable, the corrective change survives and the missing record
   is repaired afterward.

No background observer may rewrite artifact bytes, infer actor identity, or
silently convert a content edit into a path or lifecycle transition.

## Satisfied Specification Dependency

The six owner-liveness specification amendments are a predecessor, not a target
of this parent implementation. They land through the independently reviewed
child thread `gtkb-wi5441-owner-liveness-spec-amendments` before this revision
is filed. This parent creates no formal-artifact packet and performs no
specification mutation.

The parent start gate must read the six exact current versions listed under
`## Requirement Sufficiency`, compare their normalized descriptions with the
child report, and fail before source mutation on any version, description, or
approval-evidence drift. The implementation report must repeat that read-back.

The amended specifications preserve registry membership and identity authority
while making content observation best-effort and nonblocking. Registered move,
rename, delete, locator, coverage, lifecycle, membership removal, destructive
cleanup, release, and deployment remain separately governed. No requirement is
weakened implicitly by this parent proposal.

## Registry Self-Reference And Audit-Trail Admission

`groundtruth.db` is load-bearing but currently unregistered. Exact payload
hashing cannot make the database its own stable registry member because appending
the database revision mutates the same database bytes. The schema amendment will
permit `groundtruth.db` to be registered as a service-owned opaque file
container. The registry protects its path, object kind, and service identity;
MemBase owns the internal payload lifecycle.

This parent creates no formal approval packet. The existing packet directory
and active hook roots are nevertheless load-bearing. The deterministic batch
must register their proven canonical
contents or a narrowly justified service-container declaration. Broad recursive
or glob coverage is forbidden for mixed canonical/scratch trees.

The implementation report must use a section titled exactly
`## By-Reference Finalization Waiver`. It must contain `by-reference`, `waiver`,
and the owner/DELIB citation. `groundtruth.db` must not appear in
`## Files Changed`, a finalizer include set, Git staging, or a commit.

## Typed Observer Set And Admission Policy

The service exposes adapters for all five observer classes. An adapter may prove
load-bearing status but cannot itself grant membership:

1. **Capability inventory:** every canonical source and present typed
   native/adapter surface, retaining the parity checker's rule that a waiver only
   changes a missing result.
2. **Governed knowledge:** current MemBase specification source paths, governed
   test implementation paths, project authorization paths, and other canonical
   in-root path fields through existing KnowledgeDB readers.
3. **Package and entrypoint:** root and package build metadata, package source
   trees selected by build configuration, console entrypoints, packaged context
   manifests/resources, root platform testpaths, and package tests.
4. **Registered dependency closure:** registry dependencies, managed-generator
   manifests, and deterministic in-root references emitted by registered text
   artifacts through the canonical inventory service.
5. **Physical census:** no-follow root traversal plus the canonical registry
   resolver, excluding hosted application ownership boundaries and explicitly
   non-authoritative runtime/scratch surfaces from load-bearing inference.

All five adapters must successfully build the ancestor map before a subtree is
prunable. Any unavailable, ambiguous, or failed required adapter leaves a true
`invalid_unknown` and prevents `membership_complete`; it does not block ordinary
local editing, build, or test work.

The prior fixed 128-path ceiling is retired because it was only the capability
difference. The replacement is the machine-readable `registry_admission_policy`
above. It authorizes only deterministic additions selected by the five typed
observers. Before registry mutation, the implementation must materialize an
exact sorted candidate manifest, its SHA-256 digest, all observer input digests,
the starting registry generation, and a dry-run receipt. Those exact bytes bind
the apply and must be included in the report.

The batch may add exact members and narrowly justified recursive service
containers. It may append content observations. It may not remove, move, rename,
retire, shrink coverage, or replace exact declarations with a broad glob. Any
candidate whose class or metadata is ambiguous remains blocking rather than
being admitted speculatively.

## Deterministic Evidence That Invalidates The Fixed Ceiling

The current capability join remains useful historical evidence: 226
observations, 156 unique operative paths, and 128 present unregistered paths on
the 313-record WI-5640 postimage. The prior
`sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`
is retained only as historical v003 evidence. It is not an authorization bound
because v004 correctly found its row vocabulary undefined and the observer set
is now broader.

A separate read-only scan using canonical KnowledgeDB readers and the canonical
registry resolver produced 340 governed-knowledge observations, 163 unique
present paths, 56 registered present paths, and 107 present unregistered paths.
It also found historical missing-path references and two hosted-application
paths; neither class is auto-admitted. Examples of the 107 include active hook,
workflow, config, source, script, and test files. Explicit runtime/scratch paths
such as session envelopes, `.gtkb-state` evidence copies, and memory notepads are
not admitted merely because stale knowledge metadata cites them.

Package metadata further establishes that the GroundTruth package source and
test trees and the root platform testpaths are operative build/test inputs.
`groundtruth.db`, `.githooks/`, and the formal approval audit trail are additional
current gaps. Therefore an exact 128-addition acceptance criterion would remain
false completeness and is removed.

The implementation produces a new `reconciliation_evidence_digest` over exact
normalized rows with a fully specified schema emitted by the service. A focused
test independently serializes the rows using sorted keys, compact separators,
UTF-8, and no trailing newline. No opaque hard-coded digest is claimed before
the exact candidate set exists.

## Classification And Pruning

Every inspected physical object receives one of four membership classes:

1. `registered`.
2. `unregistered_load_bearing`.
3. `unregistered_disposable`.
4. `invalid_unknown`.

Structural ancestors and `pruned_uninspected_subtree` are traversal states, not
additional membership classes. Hosted application roots and `.git` remain owned
service boundaries. Git tracked, ignored, and untracked status is evidence only
and never grants membership.

An unregistered directory may be represented as a pruned envelope only after
all five successful observer ancestor maps and the registry structural-ancestor
map prove it contains no known operative path. The walker `lstat`s the boundary,
never follows symlinks, junctions, or reparse nodes, records
`descendants_inspected: false`, and does not descend. A boundary exception,
uncertain type, observer failure, path escape, collision, or exception on a path
the selected traversal must inspect remains `invalid_unknown`.

The previous 441 unreadable observations and their root distribution are
historical, volatile evidence. Immediately before implementation mutation, the
service reruns the unknown census, emits the current count and normalized
root-attribution table, and binds that table into the candidate manifest. Tests
bind the attribution procedure, not obsolete literal counts. Every legacy path
still present must map to a current inspected result or explicit pruned envelope;
any unmapped or newly encountered true unknown keeps `membership_complete`
false.

Predicate definitions are exact:

- `membership_complete`: coherent membership declarations, all five required
  observers successful, zero `unregistered_load_bearing`, zero true
  `invalid_unknown`, and every in-scope physical object represented directly or
  by one explicit pruned envelope.
- `sweep_eligible`: membership complete, registry currentness true, zero
  pruned/uninspected envelopes, no nonterminal registry transaction, current
  Git-root readiness, an immutable reclaim run and plan hash, exact item and
  identity hashes, batch-bound owner and apply evidence, fresh quiescence
  evidence, exact actuator authorization, and operation-time revalidation of
  root identity, candidate state, destination safety, registry matches, Git
  roots, and quiescence.
- `release_eligible`: membership complete, zero pruned/uninspected envelopes,
  and all existing release/currentness requirements.
- `audit_complete`: no pending known content-observation gap; advisory only.

## CLI And Consumer Integration

Add `gt registry reconcile --json` as the canonical report. It emits membership
classes, traversal states, observer provenance, counts, digests, exact admission
candidates, audit gaps, and closure flags.

`gt registry inspect` displays reverse coverage and the reconciliation summary.
Doctor, `gt registry validate`, release preflight, WI-5640 migration preflight,
and hygiene sweep consume the same typed result and may not reimplement
classification.

Hot-path publication/currentness checks must not hash the entire 13.7k-file
registered inventory on every call. Membership resolution uses the declaration
projection. Worker tools observe paths they touch, commit checks hash staged
blobs, and a read-only periodic/deep audit may hash the full set. Cache or
observation failure produces audit debt, not local platform failure.

Release, destructive sweep, and WI-5640 Stage B remain false on membership
gaps. Ordinary local edit/build/test work remains available on audit gaps or
observation-service failure. Migration preflight consumes
`membership_complete` only; it does not infer sweep or deletion authority.

## One-Time Bootstrap Repair Disclosure

Before this revision could be published, an owner direct edit to
`.claude/rules/project-root-boundary.md` made its registered content observation
stale. The existing implementation-start and bridge writer path would therefore
block the proposal that repairs this behavior.

Prime used the canonical registry-control-plane module under its registry file
lock to append one metadata-only observation:

- revision: `SOTREV-DD6F0FCB877B40E8B0E0C3F5E30539DB`;
- registry entry: `wi5640-source-066`;
- path: `.claude/rules/project-root-boundary.md`;
- digest: `sha256:69df9f861d419b1e849a168955469793d3ce3b0b765ed1755f3df18003ebaa41`;
- operation: `direct_in_place_content_change`;
- actor/session: `registry-observer/unattributed`, `external-direct-edit`;
- capability and journal: null.

No artifact bytes or path were changed. The registry remained 313 records with
generation digest
`sha256:a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7`
and returned current. This is a disclosed repair-forward bootstrap, not a claim
that the current product already implements passive observation. The required
after-action chain is terminal at
`bridge/gtkb-wi5441-registry-observation-bootstrap-after-action-002.md`
(`WITHDRAWN`), and retroactive owner approval is recorded as
`DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`.

## Responses To v004 And v006

### F1 - detector suppression

Resolved with v004 Option A. The escaped admission list was removed rather
than cosmetically re-spelled. The child governance-review thread uses six
literal formal-artifact packet target paths, contains no JSON Unicode escape,
and makes the approval detector fire and pass on the merits. This parent owns no
packet target. The historical raw-byte detector limitation is retained in the
dedicated Governance Detector Disposition section below and is not used as a
bypass.

### F2 - target ceiling expansion

The parent target ceiling expands from 19 to 41 paths as an explicit Prime
and owner-directed scope decision. It includes the missing hygiene source,
direct-edit and audit enforcement consumers, registry schema and projection
files, and paired tests. The six approval packets moved to the separate child
governance-review thread and are absent from this parent's target set. This
conflicts with v002's earlier carry-forward instruction because later owner
requirements and deterministic evidence proved the narrower scope incomplete.

The subject also expands explicitly from registry membership reconciliation to
registry membership plus platform-wide content-audit liveness. That includes the
implementation-start and protected-commit consumers that authorize this work.
The owner-approved PAUTH covers that subject expansion; the proposal does not
hide it behind path arithmetic.

WI-5640 Stage A is terminal VERIFIED at v4-020 and finalized in commit
`fd1068587c75c7f53816e4110ccde1f0df01dd04`. Stage B is paused. WI-5441 owns
shared registry/migration paths only after a fresh claim and exact start packet;
no concurrent WI-5640 claim or mutation is permitted. WI-5640 regains those
paths only after WI-5441 releases its claim and reaches independent VERIFIED.

### F3 - volatile unknown attribution

Resolved. The pre-mutation trip-wire includes the current unknown count and
normalized root-attribution table. Acceptance binds the procedure and manifest
digest, not literal historical counts.

### F4 - observer coverage for pruning

Resolved. Prunability requires successful ancestor maps from all five observer
classes. Unavailable, failed, or ambiguous observer evidence leaves
`invalid_unknown`; only ordinary local work remains fail-open on the audit or
observer-service problem.

### F5 - missing closure criterion

Resolved in Acceptance Criterion 3: zero unregistered load-bearing and zero true
invalid unknown are explicit requirements for membership completion.

### F6 - contradictory census counts

Resolved. Historical counts are labeled historical and are not acceptance
constants. The implementation reruns and timestamps one current census and
binds its manifest before mutation.

### F7 - finalizer waiver heading

Resolved. The exact recognized heading and token contract are named under
Registry Self-Reference. The deliberate correction to the advisory is explicit:
`groundtruth.db` is excluded from `## Files Changed` and staging.

### F8 - hygiene source asymmetry

Resolved. `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` and its focused
test are both in `target_paths`.

### F9 - unnamed verifier

Resolved. This proposal claims only the two canonical bridge preflights and the
named executable verification commands in the test plan. No private
proposal-specific verifier is cited.

### F10 - residual imprecision

Resolved. The predicates use `in-scope physical object`, remove the
incorrect iff statement, and name both registry currentness and the exact
hygiene actuator preconditions. `sweep_eligible` requires a current coherent
registry, current Git-root readiness, an immutable run plan hash, exact item and
identity hashes, batch-bound owner and apply evidence, fresh quiescence evidence,
exact actuator authorization, and operation-time revalidation of root,
candidate, destination, registry, Git, and quiescence state.
No approval-packet scope is claimed in this parent; that work moved to the child.

### v006 F1 - requirement-capture split

Resolved through the child governance-review thread. This parent has 41 targets,
no approval-packet targets, and declares existing requirements sufficient only
after the six amended specifications are terminally verified and read back.

### v006 F2 - detector disclosure retention

Resolved. The Governance Detector Disposition section below records the exact
escaped-byte defect, the literal child fix, and the absence of packet scope in
this parent.

### v006 F3 - emergency-bootstrap closure

Resolved. The terminal after-action entry and retroactive owner decision are
cited in the bootstrap disclosure and prior-deliberation section.

### v006 F4 - subject expansion

Resolved in the F2 response: the proposal now names membership plus
platform-wide content-audit liveness and identifies the self-authorizing gate
consumers explicitly.

### v006 F5 - residual precision

Resolved. `sweep_eligible` names registry currentness and every hygiene actuator
precondition. The vacuous literal-spelling claim is removed; the actual fix was
deleting the escaped admission list and moving six literal packet targets into
the child thread.

### Carried capability digest vocabulary

The fixed v003 digest is historical only. The replacement service defines and
emits the complete row vocabulary and a new digest after the full observer set
materializes. The independent serializer test makes it reproducible.

## Governance Detector Disposition

The v003 proposal embedded a JSON Unicode escape in an approval-path string, so
the raw-byte approval-evidence detector did not see the literal governed path.
That suppression is historical evidence only. It is neither retained nor relied
upon.

The child uses `.groundtruth/formal-artifact-approvals/`; this parent does not
update that directory. The child contains zero escaped path spellings and was
confirmed to make the detector fire and pass on the merits.
Those six targets are absent from this parent. This parent therefore neither
requests packet work nor claims an approval-evidence scope it does not own.

Two declared implementation filenames contain the literal
`formal-artifact-approval` token. The raw detector may therefore surface its
no-scope checkpoint when inspected in isolation, even though no packet target is
declared. The metadata header answers that checkpoint explicitly. The governed
Codex writer's actual audit-only path passes these exact draft bytes; no path
escape or encoded spelling is used.

## Cross-Thread Coordination

The child specification thread is terminally VERIFIED at
`bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md`, finalized in
commit `9c22e02c28b1347503abeab228e27c36f6d0e947`. WI-5640 Stage A is
VERIFIED. Stage B remains paused until this parent thread is GO'd, implemented,
and independently VERIFIED with `membership_complete: true`.
Obsolete migration sources remain present under
`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`; no deletion occurs here.

The commit-clearance repair overlaps this parent's checker and focused test
targets. Its final implementation report is
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md`; the
independent terminal verdict is
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`,
finalized with the exact five-file postimage and bridge chain in commit
`1c82158e82b517a531ffa343c38cc2b1e71507b3`. The post-commit registry readback
is coherent and current at 313 records. Global reverse coverage remains
incomplete, which is this parent's unresolved subject rather than a defect in
the child finalization. Parent implementation must carry that exact verified
postimage forward and may extend it only without regressing per-path
consumed-publication clearance.

WI-5424 has a separate uncommitted implementation report at
`bridge/gtkb-wi5424-auto-finalization-import-repair-v2-003.md`. Its two source
changes and bridge artifacts are excluded from this proposal and must not be
staged, reverted, or included in WI-5441 finalization.

The owner and another session have unrelated edits to
`.claude/rules/project-root-boundary.md` and `memory/MEMORY.md`. They remain
untouched and excluded.

The TAFE dispatcher remains deliberately disabled. This proposal does not
activate or reconfigure it. Loyal Opposition review remains manually driven by
the owner in a separate interactive session; no LO sub-agent is authorized.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v3.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2.
- `GOV-ARTIFACT-APPROVAL-001` v4.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v5.
- `SPEC-INTAKE-97538b` v2.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.
- `GOV-WORK-TREE-HYGIENE-001`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- `ADR-CROSS-HARNESS-PARITY-001`.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Prior Deliberations And Related Work

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`: registry is
  membership authority; additions are easy; removal and destructive sweep need
  oversight; unregistered artifacts are disposable only after classification.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`: retain all 90 obsolete source
  files until repeated deterministic closure scans support a separately
  authorized deletion.
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`: downstream work uses
  the registry rather than Git as artifact authority.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` and
  v4-008 VERIFIED: bounded control-plane foundation, not global membership
  closure.
- `bridge/gtkb-sot-singleton-coverage-audit-007.md` and v008 VERIFIED: prior
  count-only `coverage_complete`, redefined here.
- `bridge/gtkb-file-move-rename-canonicalization-v4-020.md`: terminal Stage A
  verification.
- WI-5479 v2: broader bridge-kind taxonomy correction. This parent absorbs only
  the `governance_review` enum/migration/test release blocker needed by the
  live requirement-capture chain; advisory-report neutralization remains open.
- WI-5441 versions 10 and 11: exact no-notation and governance-liveness owner
  requirements.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-001.md` through
  `bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md`, finalized in
  `9c22e02c28b1347503abeab228e27c36f6d0e947`: independently reviewed
  requirement capture and exact six-spec read-back.
- `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-009.md` and
  `bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md`,
  finalized in `1c82158e82b517a531ffa343c38cc2b1e71507b3`: overlapping
  exact-path commit-clearance implementation that is terminally verified and
  must be preserved by this parent.
- `bridge/gtkb-wi5441-registry-observation-bootstrap-after-action-002.md` and
  `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`: terminal
  repair-forward audit record and bounded retroactive owner approval.

## Specification-Derived Verification Plan

| Requirement | Executable evidence | Expected result |
| --- | --- | --- |
| No-notation direct edit | Registry control-plane and hook fixtures that modify a registered file with plain filesystem I/O and no packet, marker, mode, or actor | Bytes remain; local edit/build/test callers pass; audit row is attributable when known or unattributed when not |
| Audit gap liveness | Fault-inject observation service unavailable, stale projection, missing capability, and journal failure | Visible `audit_gap`; no content revert/reject/quarantine; ordinary local work continues |
| Worker path of least resistance | Governed tool fixture with session/capability evidence | Attributable revision appended automatically without extra worker ceremony |
| Governance self-repair | Disable or break the approval/observation dependency while editing its own scoped source | Corrective bytes survive; repair-forward diagnostic emitted; no recursive denial |
| Actor-blind commit path | Stage a registered content-only blob with no packet or prior observation | Narrative and protected commit checks do not reject solely for missing evidence; staged digest can be observed or warned |
| Functional validation separation | Make syntactically invalid and valid direct edits | Syntax/test failure is reported only for invalid content, independent of governance evidence |
| Registry schema | `groundtruth-kb/tests/test_db.py`, `test_sot_registry.py`, and `test_registry_control_plane.py` | Evidence views round-trip; opaque service-owned file identity valid; projection parity current |
| Exact additive admission | `gt registry reconcile --json`, deterministic manifest test, `gt registry register --batch-file` dry-run/apply/retry | All proven present load-bearing gaps added; zero removal/move/rename/coverage shrink; one receipt; retry idempotent |
| Observer semantics | Unit fixtures for all five adapters | Provenance exact; missing/historical/scratch evidence not auto-admitted; observer cannot grant membership |
| Classification | Synthetic root matrix for four classes, ancestors, apps, `.git`, virtual, opaque, symlink, reparse, and unreadable nodes | Every required object classified once; true ambiguity remains unknown |
| Pruning safety | Registered/observer descendant, failed-observer, boundary-error, and large disposable subtree fixtures | No hidden operative path; all five ancestor maps required; sweep/release false on every pruned envelope |
| Closure | Current-root `gt registry reconcile --json` after apply | Zero `unregistered_load_bearing`; zero true `invalid_unknown`; `membership_complete: true`; audit state reported separately |
| Performance | Cold and warm current-root reconcile plus publication/currentness focused tests | Reconcile under 30 seconds; no unconditional 13.7k-file digest on every hot-path check |
| Consumer parity | Doctor, validate, release, migration, hygiene, and inspect focused suites | One result/digest; membership gaps block irreversible consumers; audit gaps do not block ordinary local work |
| Satisfied spec dependency | Read back the six exact current spec versions and normalized descriptions through KnowledgeDB before start and in the report | Child-approved owner semantics remain exact; any drift blocks parent start before source mutation |
| Governance-review taxonomy durability | Enum/migration unit test plus clean-process bridge taxonomy parse of the child and parent | `governance_review` remains distinct and is never collapsed into an advisory kind; WI-5479 broader scope remains open |
| Quality | Ruff check/format on changed Python, `git diff --check`, target-path audit | Clean; no unrelated WI-5424 or owner files included |
| Bridge preflights | Applicability and mandatory clause preflights against exact filed content | No missing required/advisory specs or blocking clause gap |

## Acceptance Criteria

1. Every registered artifact remains directly editable in a plain text editor
   without notation, packet, marker, mode, or editor integration. Missing audit
   evidence alone cannot reject, revert, quarantine, delay, or invalidate its
   content or block ordinary local edit, build, or test work.
2. Governed worker paths automatically leave attributable evidence when their
   context is trustworthy. Unknown provenance is recorded honestly when
   observed; failed observation remains visible, retryable, non-blocking audit
   debt.
3. Reconciliation reports zero `unregistered_load_bearing` and zero true
   `invalid_unknown` before `membership_complete: true`. Audit completeness is
   reported separately and is not required for membership or local liveness.
4. The exact additive candidate manifest, manifest digest, observer input
   digests, starting registry generation, and dry-run receipt are bound before
   mutation and reproduced in the implementation report.
5. The registry transaction performs additions and observation appends only.
   It performs zero delete, move, rename, retirement, coverage shrink, or broad
   glob substitution, and exact retry is idempotent.
6. All five observer classes are typed, provenance-bearing, deterministic, and
   unable to grant membership. All five ancestor maps must succeed before any
   prune decision.
7. `coverage_complete` remains a public key and doctor gate, redefined as the
   shared exact `membership_complete`; the count-only predicate is impossible.
8. A pruned root reports `descendants_inspected: false` and cannot hide a
   registered or observed descendant, erase an encountered exception, or permit
   sweep/release eligibility.
9. Doctor, validate, release, migration, hygiene, inspect, observation, and
   commit checks consume the shared registry/reconciliation semantics. No hot
   path unconditionally hashes the entire registered inventory.
10. The six current amended specification versions exactly reproduce the
    terminal child report and encode the owner liveness and direct-edit contract;
    this parent creates no approval packet or specification version.
11. `groundtruth.db` is registered as an opaque service-owned file identity,
    is named only under `## By-Reference Finalization Waiver` in the report, and
    never enters `## Files Changed`, staging, a finalizer include set, or commit.
12. No target outside `target_paths` is mutated except additive registry member
    rows selected by the declared policy and their canonical projection. The
    report lists the exact added members and proves the policy selected each.
13. No WI-5640 Stage B apply, obsolete-source deletion, dispatcher activation,
    harness-role mutation, unrelated WI-5424 change, push, release, deployment,
    credential action, destructive cleanup, or history rewrite occurs.
14. `groundtruth_kb.bridge.taxonomy.BridgeKind`, the migration map, and the
    focused taxonomy test preserve `governance_review` as a distinct value.
    This parent does not close WI-5479 or rename the advisory-report kind.

## Risks And Rollback

The largest correctness risk is false load-bearing classification. The service
therefore separates observer evidence from membership grant, materializes the
exact additive plan before mutation, and blocks membership completion on any
true ambiguity. It does not block ordinary local work on observer or audit
failure.

The largest liveness risk is recreating a universal gate that treats missing
evidence as invalid content. The direct-edit, actor-blind commit, service-failure,
and self-repair fixtures are mandatory negatives against that regression.

A separate durability risk is that the active requirement-capture chain currently
parses only because the `governance_review` taxonomy repair is dirty in this
worktree. The bounded three-file absorption makes that exact dependency durable
without claiming to complete WI-5479's broader advisory-taxonomy work.

Subtree pruning can hide evidence if any observer ancestor map is omitted. All
five maps are required, and pruned envelopes always block destructive sweep and
release.

Registry apply uses the existing journal/recovery transaction. A pre-commit
failure retains the old coherent generation. An indeterminate transaction uses
the recovery-forward path. Source bytes are not deleted as rollback.

If the six-spec dependency is missing or drifts, implementation start fails
before source mutation and the parent is revised; this thread does not repair
specifications in-band. If additive admission cannot reach membership closure,
the report states the remaining exact gaps and files NO-ACTION for further
review; it does not erase work or fabricate completeness.

## Owner Decisions / Input

The owner explicitly directed on 2026-07-26 that:

- plain Notepad edits require no notation and must not be rejected;
- workers should leave records through the easiest governed path;
- governance is assistance and path-of-least-resistance, not filesystem
  security or an impermeable barrier;
- an audit gap or bypassed GOV is preferable to platform failure;
- obsolete or unfinished governance must not block the work correcting it; and
- the primary objective is completing correct work without drift, not obtaining
  perfect audit evidence at the cost of doing no work.

These directions are durably captured in WI-5441 version 11 and the cited
project authorization. No new owner decision is required.

## Pre-Filing Preflight

Before publication Prime must confirm that the latest parent state is v006
NO-GO, the child is terminally VERIFIED at
`bridge/gtkb-wi5441-owner-liveness-spec-amendments-012.md` in commit
`9c22e02c28b1347503abeab228e27c36f6d0e947`, the overlapping commit-clearance
repair is terminally VERIFIED at
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-010.md` in
commit `1c82158e82b517a531ffa343c38cc2b1e71507b3`, all six current spec versions
and normalized descriptions match
`sha256:27c07974b72264dba355290bc253e55088d2be1df3eb2b59c8cccab93e8ba36d`, WI-5441 version 11 still
carries the owner requirements, WI-5640 Stage A remains terminal VERIFIED, and
unrelated worktree changes remain excluded.

The canonical applicability preflight and mandatory clause preflight are run
against these exact candidate bytes by the governed revision helper. Filing is
permitted only when both exit zero with no missing required/advisory
specification and no blocking clause gap.

## Requested Loyal Opposition Action

Confirm first that the child governance-review thread is terminally VERIFIED
and the six current specifications match the declared versions and normalized
read-back digest. Then review this parent against the owner liveness rule, not as
a security-boundary design. Confirm ordinary direct content edits cannot fail
for missing governance evidence; worker audit capture remains automatic on the
normal path; identity and irreversible boundaries remain narrow; all five
observer classes control pruning; the additive-only admission policy can reach
honest membership closure; and v004 plus v006 findings are answered. File GO
only if the implementation can make the registry complete without making
governance a prerequisite for ordinary work.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
