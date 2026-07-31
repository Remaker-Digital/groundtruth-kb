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

# WI-5441 Owner-Liveness Specification Amendments

bridge_kind: governance_review
Document: gtkb-wi5441-owner-liveness-spec-amendments
Version: 001
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".groundtruth/formal-artifact-approvals/2026-07-26-DCL-ARTIFACT-APPROVAL-HOOK-001-v5.json",".groundtruth/formal-artifact-approvals/2026-07-26-DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001-v2.json",".groundtruth/formal-artifact-approvals/2026-07-26-DCL-SOT-REGISTRY-PROJECTION-PARITY-001-v3.json",".groundtruth/formal-artifact-approvals/2026-07-26-DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v4.json",".groundtruth/formal-artifact-approvals/2026-07-26-GOV-ARTIFACT-APPROVAL-001-v4.json",".groundtruth/formal-artifact-approvals/2026-07-26-GOV-PLATFORM-SOT-REGISTRY-001-v3.json"]
approval_evidence_scope: six concrete formal-artifact approval packet targets for the six complete specification versions displayed below; no source, configuration, test, registry-declaration, or other packet work is proposed

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This governance-review thread is the requirement-capture split required by
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md` F1. The
parent implementation proposal correctly declared a genuine requirement gap,
but a `prime_proposal` carrying protected implementation paths cannot exercise a
GO while that gap remains. This thread carries only the six formal-artifact
approval packet paths and the six corresponding MemBase specification updates.

The amendments make the owner's no-notation direct-edit and governance-liveness
rules explicit while preserving the registry as the sole membership authority.
They do not authorize any source, hook, configuration, test, registry
declaration, filesystem identity, dispatcher, migration, deletion, commit,
release, or deployment change. After these exact versions land, the parent
thread may be refiled as `prime_proposal` with `Existing requirements
sufficient` and the accepted v005 implementation design unchanged.

## Subject Boundary

This is requirement capture only. It resolves the subject expansion that began
when WI-5441 grew from reverse-coverage reconciliation into a platform-wide
membership, content-audit, and operational-liveness repair. The six amended
specifications define that expanded subject. The parent thread remains the sole
place for implementation and tests.

The TAFE dispatcher remains deliberately disabled. No dispatcher activation or
reconfiguration is part of this proposal. WI-5640 Stage B remains paused and all
90 obsolete migration sources remain retained.

## Owner Decisions / Input

The owner directed on 2026-07-26 that:

1. A registered artifact may be edited in an ordinary editor such as Notepad
   without any notation, marker, mode, packet, filename convention, editor
   integration, or other signal.
2. Workers should leave attributable records automatically through the easiest
   normal tool path, but a missing audit record or bypassed GOV is preferable to
   platform failure.
3. Governance is a path-of-least-resistance coordination system, not a
   filesystem security boundary.
4. Obsolete, unfinished, unavailable, or broken governance must not recursively
   block work that corrects that governance.
5. Functional syntax, schema, and behavior checks may still reject malformed
   content on its merits.
6. Registered move, rename, delete, locator, coverage, lifecycle, membership
   removal, destructive cleanup, release, and deployment remain separately
   governed identity or irreversible-effect operations.

These decisions are captured in WI-5441 version 11 and project authorization
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
version 2. No new owner decision is required.

## Requirement Sufficiency

New or revised requirement required before implementation.

This state is deliberate and mechanically usable because this thread is a
`governance_review` whose `target_paths` contain only the six approval packets.
The exact proposed versions follow. A GO authorizes requirement capture only;
it does not authorize the parent WI-5441 implementation.

## Exact Specification Amendments

The following full descriptions are the proposed canonical content. Existing
identifiers, titles, types, and non-description metadata remain unchanged except
for the normal new-version provenance fields written by the governed spec
service.

### `GOV-PLATFORM-SOT-REGISTRY-001` v3

**Title:** Platform-wide Artifact Membership Registry

`config/registry/sot-artifacts.toml` is the sole authority for whether a GT-KB
platform artifact belongs to the platform. The MemBase `sot_artifacts` table is
its exact declaration projection; projections, observed-revision records, Git
state, inventories, caches, loading graphs, manifests, and filesystem presence
cannot independently grant membership.

Every load-bearing platform file, directory, glob-expanded member, opaque
service container, MemBase authority, and declared external runtime identity
MUST be covered by one active registry declaration. An unregistered
load-bearing artifact is a release-blocking and sweep-blocking defect. Creation
of a load-bearing artifact MUST establish registry coverage in the same
governed work transaction.

Registry declaration and lifecycle operations MUST use the deterministic
`gt registry` CLI. Direct TOML editing and direct projection-table mutation are
prohibited. Registering a new artifact is a routine OPS operation when the
authority specification, locator, ownership, and mutation API validate.
Removing membership, or deleting, moving, or renaming a registered artifact,
requires a digest-bound transition authorization with owner evidence and
independent bridge `GO`.

An in-place content edit at an unchanged registered locator is not a membership
or filesystem-identity transition. The owner MAY edit a registered artifact in
an ordinary editor without a governance notation, marker, mode, packet, or
editor integration, and the resulting bytes remain immediately usable.
Governed worker tools SHOULD append attributable observed-revision evidence
automatically on their normal path. Actor-blind or later observation MAY append
honest unattributed evidence. Missing, stale, or failed content-observation
evidence is visible audit debt; by itself it MUST NOT reject, revert,
quarantine, delay, or invalidate content or block ordinary local edit, read,
build, or test work.

Functional syntax, schema, integrity, and behavior checks remain authoritative
on their merits. A missing registered path, object-kind change, ambiguous
locator, path escape, declaration/projection drift, coverage collision, or
unregistered load-bearing artifact remains a membership or identity defect.
Content-observation completeness is reported separately and cannot grant or
remove membership.

When a governance observation or approval mechanism is unavailable, obsolete,
or itself under repair, minimal corrective local work proceeds repair-forward.
The platform records the audit gap afterward when possible rather than
discarding corrective bytes or entering a recursive authorization loop. This
does not waive the separate authorization required for identity transitions or
irreversible external effects.

After a complete reconciliation reaches zero true unknown and zero
unregistered-load-bearing paths, in-scope unregistered filesystem objects are
disposable by the governed hygiene sweep only through quarantine and the fixed
retention/expiry contract. Immediate permanent deletion is prohibited.

The platform-root registry does not govern immediate child directories under
`applications/`; each hosted application MUST own and enforce its own registry
SoT. Files directly inside `applications/` that are not within an application
child directory remain in platform sweep scope.

Registry declaration/projection drift, invalid locators, missing registered
objects, and reverse-coverage defects are ERROR severity and block membership
closure, release, retention planning, and destructive sweep as applicable.
Content-observation gaps remain visible audit debt and do not become membership
errors. The registry self-declaration remains mandatory.

### `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2

All registry declaration mutation MUST pass through `gt registry` under a
registry lock and recoverable transaction journal. Direct TOML, direct
`sot_artifacts`, direct revision-ledger, and raw registered-path identity
mutation are prohibited worker surfaces.

`register` requires an OPS envelope, unique id and locator, existing authority
specification, valid ownership and mutation API, valid coverage mode, no unsafe
overlap, and a successful declaration/projection transaction. It does not
require removal oversight.

`amend` may change non-identity declaration fields under OPS authority but may
not disguise a move, rename, deletion, narrowing, or removal. Any change to
locator, coverage mode, lifecycle effect, or membership set is an identity
transition.

An in-place content edit at an unchanged registered locator is not a registry
declaration or identity mutation. The owner may perform it directly with no
governance notation, packet, mode, or editor integration. Governed worker tools
SHOULD invoke `observe` automatically after successful content mutation when
trustworthy worker context exists. Passive, commit-time, inspection-time, or
periodic observation MAY append honest unattributed evidence when actor context
is unavailable.

Failed, missing, or stale content observation produces visible, retryable audit
debt. It MUST NOT by itself reject, revert, quarantine, delay, or invalidate the
bytes or block ordinary local edit, read, build, or test work. Functional
validation may still fail invalid content on its merits. A successful revision
append remains locked, journaled, append-only, and projection-consistent; an
observation row cannot grant membership or authorize an identity transition.

`transition request` binds entry id, source locator, current revision digest,
operation, destination when applicable, owner evidence, intended membership
result, and expiry. `transition apply` requires an OPS envelope, matching active
request, matching independent bridge `GO`, and fresh operation-time
revalidation. A worker cannot authorize deletion by deleting first or editing
the registry afterward.

Move or rename MUST update filesystem identity, declaration, projection,
revision history, journal, and receipt as one recoverable transaction. Delete
first moves the registered artifact into governed quarantine and records its
membership transition; permanent deletion remains subject to the 30-day DCL.
Membership removal without a present file requires the same oversight.

Hooks, commit gates, release gates, and migration tools MUST call the shared
registry resolver and identity-authorization service. Unsupported or failed
content-observation paths leave a visible audit gap and ordinary local work
continues. Unsupported or failed identity-transition authorization does not
silently authorize that transition.

When the normal governance mechanism is unavailable or is itself the broken
target, the minimal corrective content change may proceed repair-forward and
its evidence may be appended afterward. This liveness exception does not grant
delete, move, rename, locator, coverage, lifecycle, membership-removal,
destructive-sweep, release, deployment, or external-effect authority.

### `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4

Every declaration retains the existing required identity, domain, lifecycle,
storage path, authority, mutation API, versioning, backup, health-check, and
owner-role fields. Every declaration MUST additionally carry an explicit
`coverage_mode` with one of these values:

- `exact`: registers one filesystem object at the normalized relative locator.
  It does not implicitly register descendants.
- `recursive`: registers the directory and all non-service descendants reached
  without following symbolic links, junctions, or reparse points.
- `glob`: registers the deterministic in-root match set produced by the declared
  pattern. Empty and changed match sets remain visible evidence.
- `opaque_container`: registers a service-owned file or directory container
  while its payload lifecycle is governed by a dedicated service ledger.
  Payloads do not become independent members merely because they reside in the
  container. Use requires an explicit authority specification and service
  mutation API.
- `virtual`: registers a non-filesystem authority such as `membase:<table>` or a
  declared external runtime identity and has no filesystem-retention effect.

Coverage mode MUST NOT be inferred from trailing separators, wildcard
punctuation, current object type, or current existence. Filesystem locators MUST
be project-relative, case-normalized for collision detection,
path-escape-free, and compatible with Windows path semantics. `recursive`
locators MUST name directories. An `opaque_container` locator MAY name a file
or directory only when its authority and mutation API establish the internal
payload lifecycle. `glob` patterns MUST remain within the root. `virtual`
locators MUST use a registered virtual scheme. A locator may not ambiguously
overlap another active declaration unless the overlap is explicitly validated
as identical authority and semantics.

The migration to v3 MUST assign and review a coverage mode for every existing
declaration. No default may silently turn a broad directory row into recursive
retention.

Concrete members resolved by `exact`, `recursive`, or `glob` receive
append-only observed revisions. An `opaque_container` receives container-state
revisions plus dedicated payload receipts. `virtual` currentness is checked by
its declared health function or mutation API.

Each observed revision MUST identify the registry entry, canonical relative
member path or virtual identity, object kind, digest when applicable, logical
size when applicable, operation, observation time, predecessor revision, and
an `evidence_view`. Supported evidence views include `working_tree`,
`git_index`, `governed_tool`, `registry_transaction`, `bridge_publication`, and
`recovery`. A revision MAY include an evidence source reference such as a
capability id, receipt id, source path, or Git blob OID. Actor and session fields
MAY use an explicit unattributed value when no trustworthy provenance exists;
they MUST NOT invent human or worker identity.

Revision evidence is audit state, not membership authority. A missing or stale
content revision MUST remain visible but does not invalidate otherwise valid
artifact bytes or block ordinary local edit, read, build, or test work.

Unknown fields, invalid enum values, unsafe paths, case-fold collisions,
unsupported virtual schemes, ambiguous overlaps, or prohibited opaque-container
use fail registry loading.

### `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3

TOML declarations and current MemBase `sot_artifacts` declarations MUST match
exactly for all declaration fields, including `coverage_mode`. Declaration
drift is ERROR severity and blocks registry identity mutation, membership
closure, release, retention-manifest generation, and sweep execution.

The append-only `sot_artifact_revisions` history is content-currentness and
audit evidence, not a second membership authority and not a TOML declaration-
parity surface. A revision row cannot create or remove membership. Each revision
identifies the registry entry, canonical relative member path or virtual
identity, object kind, digest and logical size where applicable, operation,
actor and session or explicit unattributed provenance, observation time,
predecessor revision, `evidence_view`, and optional evidence source reference.

Successful declaration, projection, journal, receipt, and revision writes MUST
preserve reader-visible parity through the locked recoverable transaction. A
journaled incomplete identity transaction fails closed and MUST be recovered
before further registry identity mutation or destructive sweep planning.

A failed, missing, or stale content-observation append leaves visible,
retryable audit debt. It MUST NOT roll back artifact bytes, corrupt declaration
parity, or by itself reject ordinary local edit, read, build, test, or
content-only commit work. A later observer may append accurate attributable or
unattributed evidence for the relevant working-tree, staged, governed-tool, or
recovery view.

The existing public workflow `edit TOML then run gt registry sync` is retired.
`sync` may remain only as an internal transaction step or a read-only repair-
plan command; it cannot legitimize direct declaration edits. The registry self-
row is validated through a normalized non-recursive declaration digest.

When the registry observation or approval mechanism is unavailable or is
itself under repair, minimal corrective content work proceeds repair-forward
and the audit gap is captured afterward when possible. This does not weaken
atomic declaration/projection transitions or authorize identity changes.

### `GOV-ARTIFACT-APPROVAL-001` v4

GroundTruth-KB must bias toward owner visibility when AI workers manage formal
artifacts. When an AI worker proposes to create, update, promote, or retire a
GOV, SPEC, PB, ADR, DCL, Deliberation Archive entry, or narrative artifact based
on user conversation, the normal governed tool path MUST present the full
proposed artifact in its native review format before treating it as canonical
project truth.

The review packet includes the artifact type, proposed identifier, lifecycle
status or outcome, title, summary, full content, metadata, links, assertions or
constraints where applicable, changed_by, change_reason, and source reference.
For an AI-authored narrative artifact, it includes the full proposed file
content, or the fully rewritten content for a partial edit, plus the proposed
blob SHA-256. Tool-context approval hooks validate the packet against the
proposed content when that governed path is functioning.

The artifact must not become canonical through the governed AI-authoring path
until the owner approves or explicitly acknowledges the proposed entry, unless
the owner previously activated a scoped auto-approval state for that exact
class. Auto-approval does not remove the display or transcript-capture
requirement from that governed path.

An ordinary owner edit made directly in an editor such as Notepad requires no
packet, notation, marker, mode, filename convention, editor integration, or
other signal. The resulting bytes remain usable immediately. Because an
actor-blind filesystem or commit observer cannot reliably distinguish an owner
edit from an unmediated worker write, missing approval or attribution evidence
alone MUST NOT reject, revert, quarantine, delay, or invalidate a registered
content-only change or block ordinary local edit, read, build, or test work.

Governed workers SHOULD leave attributable approval and revision evidence
automatically because the governed path is the path of least resistance. An
actor-blind or later observer MAY record explicit unattributed evidence and a
visible audit gap; it MUST NOT invent provenance. Functional syntax, schema,
integrity, and behavior checks remain valid on their merits.

If the approval mechanism is unavailable, obsolete, or itself under repair,
minimal corrective content work proceeds repair-forward and the missing audit
record is repaired afterward when possible. This liveness rule does not waive
separate authorization for registered move, rename, delete, locator, coverage,
lifecycle, membership removal, destructive cleanup, release, deployment, or
other irreversible effects.

The narrative-artifact extension is implemented by
GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 Slice A.1 plus Slice C. The
canonical path-pattern set remains at
`config/governance/narrative-artifact-approval.toml`; its gates guide governed
AI tools and collect evidence, but actor-blind absence of evidence is not a
content-validity decision.

Rationale: the owner's interaction with GT-KB is an artifact-generation and
management activity, so AI-authored formalization should be visible and easy to
review. The mechanism exists to reduce drift and preserve owner control, not to
turn incomplete governance into a security boundary that prevents correct work
or prevents the owner from editing the platform directly.

### `DCL-ARTIFACT-APPROVAL-HOOK-001` v5

Any hook, skill, CLI flow, or harness integration that converts user input into
AI-authored formal GT-KB artifacts SHOULD render the complete proposed artifact
before canonical persistence. The renderer must not summarize away required
metadata or omit content that will be stored.

The governed approval event captures proposed artifact ID and type, source
conversation or source artifact, full proposed content hash, approval mode,
and the explicit change request statement. When available, the normal worker
path persists a transcript record of the display-and-acknowledge moment for
downstream audit.

The constraint applies to these implementation surfaces:

1. Bash-mediated formal KB mutations: the formal-artifact approval hook
   intercepts recognized AI tool commands such as `gt spec record`,
   `gt spec update`, and Deliberation Archive mutation commands and requires a
   matching packet through the normal governed path. Deterministic packet
   auto-discovery may be used when artifact id and full-content hash match.
2. Narrative-artifact writes made through a worker tool with proposal content:
   the narrative-artifact approval hook compares protected path and proposed
   content with an explicit or auto-discovered packet. A trustworthy tool
   context may deny or redirect that worker operation to the easier governed
   path while the mechanism is available.
3. Actor-blind filesystem, staging, and commit checks: these validate and record
   packet or revision evidence when present. Absence of a packet or attributable
   observation alone MUST NOT reject a registered content-only change, because
   the observer cannot infer whether an ordinary owner editor or an unmediated
   worker produced the bytes. It emits visible audit debt and may append honest
   staged-view or unattributed evidence. Functional validation remains valid on
   its merits.

An ordinary owner editor change requires no packet, notation, marker, mode,
filename convention, editor integration, or environment variable. The bytes
remain immediately usable. No hook may infer owner or worker identity from the
mere absence or presence of approval evidence.

Path-pattern exemptions remain enumerated in
`config/governance/narrative-artifact-approval.toml`. Future implementation
surfaces extend the governed worker path additively without turning actor-blind
checks into content-permission gates.

When the approval hook, packet writer, bridge, claim, observation service, or
related governance mechanism is unavailable, obsolete, or itself under repair,
minimal corrective content work proceeds repair-forward. The platform emits a
visible diagnostic and captures missing evidence afterward when possible rather
than discarding the correction or entering recursive denial. This does not
authorize identity transitions, destructive cleanup, release, deployment, or
other irreversible effects.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v2, proposed v3: sole membership authority;
  content audit is made nonblocking without weakening identity boundaries.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1, proposed v2:
  declaration and identity mutation remain governed; content observation becomes
  best-effort and repair-forward.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3, proposed v4: revision evidence views,
  honest unattributed provenance, and file-shaped opaque service containers.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2, proposed v3: declaration parity
  remains atomic; audit evidence is separate and nonblocking.
- `GOV-ARTIFACT-APPROVAL-001` v3, proposed v4: owner direct edits need no packet
  or notation; AI tool paths retain full-artifact review.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v4, proposed v5: tool-context guidance is
  separated from actor-blind observation and commit checks.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: this NEW thread receives independent review
  before any packet or specification mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: the governance-review submode
  carries only formal approval packet targets while requirement sufficiency is
  `gap`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: all six exact
  amendments and their governing relationship are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: verification maps each
  amended specification to packet and read-back evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: owner decisions become durable
  specifications without treating missing audit evidence as content failure.

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: the owner decisions cross the
  requirement threshold and are captured as governed specification versions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: each amendment is an append-only new
  version; no current specification is silently rewritten or retired.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all packet paths and specification
  operations remain in the GT-KB root, while hosted application boundaries stay
  outside the platform registry's ownership.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`: establishes
  the registry as membership authority, makes additions routine, and keeps
  removal and destructive sweep under oversight.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`: all 90 migration sources stay
  present until repeated deterministic closure scans support separately
  authorized deletion.
- WI-5441 versions 10 and 11: durable owner wording for notation-free direct
  editing and governance liveness.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-005.md`: carries
  the accepted implementation design and first displays these six amendments.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md`: requires
  this governance-review split because a genuine requirement gap cannot share a
  source implementation authorization.
- `bridge/gtkb-file-move-rename-canonicalization-v4-020.md`: verifies WI-5640
  Stage A; Stage B remains paused pending registry membership closure.

No seeded intake candidate was relevant; those generic intake records were
removed rather than cited as false precedent.

## Spec-Derived Verification Plan

| Requirement | Executable evidence | Expected result |
| --- | --- | --- |
| Six exact owner-approved artifacts | Validate each declared JSON packet with the canonical formal-artifact packet helper against the exact full content above | Six valid packets; artifact ids and next versions exact; no seventh packet |
| Sole registry membership authority | Read back `GOV-PLATFORM-SOT-REGISTRY-001` v3 through `gt spec show --json` | Membership authority and identity boundaries preserved; audit gaps explicitly nonblocking |
| Identity mutation oversight | Read back `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2 | Move, rename, delete, locator, coverage, lifecycle, and removal still require governed transition authorization |
| Revision and opaque-container schema | Read back `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4 | `evidence_view`, optional evidence source, honest unattributed provenance, and file-shaped opaque container semantics present |
| Declaration/projection atomicity | Read back `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3 | Declaration parity remains atomic and blocking; content-audit debt is separate and nonblocking |
| Owner direct edit | Read back `GOV-ARTIFACT-APPROVAL-001` v4 | Plain editor changes require no packet, notation, marker, or mode and remain usable |
| Worker versus actor-blind hooks | Read back `DCL-ARTIFACT-APPROVAL-HOOK-001` v5 | Governed worker route remains easiest; actor-blind absence of evidence cannot invalidate content |
| Exact content | Independently SHA-256 the normalized proposed description for each packet and compare with the current MemBase version description after update | Six byte-identical normalized contents and six expected next versions |
| Scope ceiling | `git diff --name-only` plus packet-directory inventory before and after | Only the six declared packet paths are created; no source, config, test, bridge-existing-file, or registry declaration is modified by implementation |
| Parent sequencing | `gt bridge show` for both threads and `gt spec show` for all six ids | This thread is GO before updates; all six versions land before the parent is refiled as requirements sufficient |
| Bridge preflights | Applicability and mandatory clause preflights against exact filed bytes | Exit 0; no missing required or advisory specs; no blocking clause gap |

## Acceptance Criteria

1. Exactly six approval packet files are created at the six declared paths, and
   each validates against the exact proposed full content and next version.
2. The six MemBase specifications advance to versions v3, v2, v4, v3, v4, and
   v5 respectively through the canonical governed spec service.
3. The owner no-notation, nonblocking-audit, honest-unattributed-provenance, and
   repair-forward rules appear in all applicable specifications without
   weakening the registry's sole membership authority.
4. Registered move, rename, delete, locator, coverage, lifecycle, membership
   removal, destructive cleanup, release, deployment, and other irreversible
   effects remain separately governed.
5. No source, configuration, hook, test, registry declaration, filesystem
   identity, migration file, dispatcher setting, or unrelated worktree path is
   mutated.
6. No WI-5640 Stage B apply, source deletion, commit, push, release, deployment,
   credential action, destructive cleanup, or history rewrite occurs.
7. The parent WI-5441 proposal is not refiled as `Existing requirements
   sufficient` until all six current specification records reproduce these
   approved versions exactly.


## Specification-Derived Verification Command Evidence

The post-amendment report MUST execute and record the observed result of:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py platform_tests/hooks/test_narrative_artifact_approval.py -q --no-header
```

Those tests are non-implementation regression evidence only: the six amended
specifications must not silently break the current formal-artifact read and
packet-validation surfaces before the separately reviewed parent implementation
changes their behavior. Exact packet validation and six-spec read-back remain
the authoritative verification for this requirement-capture slice.

## Risk / Rollback

The primary risk is weakening identity governance while repairing content-edit
liveness. The complete replacement text repeatedly distinguishes content-only
edits from membership and identity transitions, and read-back verification
checks both halves.

The second risk is proposal-to-packet drift. Packet hashes bind the exact full
content displayed here, and implementation must compare normalized content
before each update and read it back afterward.

Specification versions are append-only. If a packet or update fails, stop
before later updates where practical and report the exact partial state; do not
rewrite history. Any correction is a new reviewed version. No source rollback is
needed because this thread changes no implementation file.

## Governance Detector Disposition

The parent v003 detector defect used a JSON Unicode escape that prevented the
approval-evidence detector from seeing one path. That suppression is retired.
This proposal uses six literal `.groundtruth/formal-artifact-approvals/` paths,
contains zero escaped path spellings, and expects the detector to fire and pass
on the merits. The full raw-byte limitation remains recorded here as historical
control-plane evidence and is not used as a bypass.

## Requested Loyal Opposition Action

Verify that this thread is executable in `governance_review` mode with zero
forbidden source/config/test targets; compare all six full proposed descriptions
with the owner contract; confirm identity and irreversible-effect oversight is
preserved; and file GO only for the six packet-backed specification updates.
The parent implementation thread remains unauthorized until these amendments
land and it is independently refiled and reviewed.

## Recommended Commit Type

`docs:` - six append-only governance specification versions and their approval
packets; no implementation behavior changes in this thread.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
