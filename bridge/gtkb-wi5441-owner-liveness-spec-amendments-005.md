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

# WI-5441 Owner-Liveness Specification Amendments

bridge_kind: governance_review
Document: gtkb-wi5441-owner-liveness-spec-amendments
Version: 005
Responds to: bridge/gtkb-wi5441-owner-liveness-spec-amendments-004.md
Prior proposal: bridge/gtkb-wi5441-owner-liveness-spec-amendments-003.md
Prior verdict: bridge/gtkb-wi5441-owner-liveness-spec-amendments-004.md
Date: 2026-07-27 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".groundtruth/formal-artifact-approvals/**","groundtruth.db"]
approval_evidence_scope: the date-independent formal-artifact approval packet envelope; exactly six governed-service-emitted packets are bound below by artifact id, version suffix, and full-content SHA-256; groundtruth.db carries the six append-only MemBase versions

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
requirement_sufficiency_state: gap
spec_status_overrides: {"DCL-ARTIFACT-APPROVAL-HOOK-001":"specified","GOV-ARTIFACT-APPROVAL-001":"specified"}
metadata_enforcement_note: requirement_sufficiency_state and spec_status_overrides are documentary summaries only; machine authority is the Requirement Sufficiency section, acceptance criterion 3, and the explicit command flags below

---

## Revision Claim

This v005 preserves the complete v003 design and all six exact amendment bodies
while answering the two blocking and four non-blocking findings in
`bridge/gtkb-wi5441-owner-liveness-spec-amendments-004.md`. All eight v002
findings remain closed and are not re-litigated.

| v004 finding | Disposition in this revision |
| --- | --- |
| F1 | Replace the synthetic AUQ label with real owner-conversation record `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`, whose exact readback approves this policy and all six amendment bodies. |
| F2 | Cite that same owner decision as the provenance for platform-wide actor-blind non-rejection, including `AGENTS.md`, `CLAUDE.md`, and registered rule files. |
| F3 | Disclose the scope-ceiling refinement: transient unregistered content inputs are required by `gt spec update`; only governed artifacts are constrained to the six packets plus `groundtruth.db`. |
| F4 | Declare the exact transient content directory, generation source, retention, disposal, and finalization exclusion; reconcile the scope-verification row. |
| F5 | Mark `requirement_sufficiency_state` and `spec_status_overrides` as documentary summaries, not machine bindings. |
| F6 | Add six explicit canonical commands; the two lifecycle overrides carry `--status specified`. |

No amendment content, content hash, target envelope, requirement subject,
governance-review split, or parent-implementation boundary changes.

## Summary

This governance-review thread is the requirement-capture split required by
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-006.md` F1. The
parent implementation proposal correctly declared a genuine requirement gap,
but a `prime_proposal` carrying protected implementation paths cannot exercise a
GO while that gap remains. This thread carries the date-independent formal-artifact packet envelope,
`groundtruth.db`, and exactly six corresponding MemBase specification updates.
The governed service emits each packet as part of its update; no packet is
pre-created.

The amendments make the owner's no-notation direct-edit and governance-liveness
rules explicit while preserving the registry as the sole membership authority.
The owner ratified the platform-wide policy and all six exact amendment bodies in
`DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`.
They do not authorize any source, hook, configuration, test, registry
declaration, filesystem identity, dispatcher, migration, deletion, push,
release, or deployment change. One bounded local finalization commit may
contain only the six emitted packets and `groundtruth.db` after independent
VERIFIED. After these exact versions land, the parent
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
7. Because every load-bearing artifact must be registered, actor-blind
   missing-evidence non-rejection is intentionally platform-wide for
   registered content-only edits, including `AGENTS.md`, `CLAUDE.md`, and
   registered rule files. Trustworthy AI tool context still routes workers
   through the easier governed approval path.

Directives 1 through 6 are recorded in WI-5441 version 11 and project
authorization
`PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726`
version 2. Directive 7 and the six exact amendment bodies were then presented
to and approved by the owner and are durably captured as owner-conversation
decision `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` version 1, content hash
`4220c8118974035d1c81bef5c5a7843b90158022b378cf7d01a558c95befeac5`.

The six governed updates will pass that real identifier through the CLI's
legacy-named `--auq-id` field and the concise answer: "Approved as stated:
platform-wide registered content-edit liveness and six exact amendments."
The parameter name does not change the cited record's actual
`source_type=owner_conversation` and `outcome=owner_decision`. No synthetic
evidence identifier remains, and no new owner policy decision is required.

The decision-capture helper persisted that prerequisite owner-conversation row
in `groundtruth.db` before this child revision was filed. That completed
evidence write is the pre-GO baseline, not one of the six proposed
specification mutations. The implementation scope comparison begins after the
decision row exists and must attribute only the six post-GO updates and their
six emitted packets to this child.

## Requirement Sufficiency

New or revised requirement required before implementation.

This state is deliberate and mechanically usable because this thread is a
`governance_review` whose `target_paths` contain only the packet envelope and
`groundtruth.db`; the forbidden-target set remains empty. The exact proposed
versions follow. A GO authorizes requirement capture only;
it does not authorize the parent WI-5441 implementation.

## Exact Specification Amendments

The following full descriptions are the proposed canonical content. Existing
identifiers, titles, types, and non-description metadata remain unchanged except
for normal new-version provenance and two deliberate lifecycle overrides:
`GOV-ARTIFACT-APPROVAL-001` v4 and `DCL-ARTIFACT-APPROVAL-HOOK-001` v5
land as `specified` until the parent implementation is independently verified.

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

The completed v3 migration assigned and reviewed a coverage mode for every
existing declaration. No default may silently turn a broad directory row into
recursive retention.

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
closure, release, retention-manifest generation, and sweep execution. It does
not by itself block an unrelated content-only commit. A commit or operation
that mutates registry declarations, projections, locators, coverage, lifecycle,
or membership remains blocked until exact parity is restored.

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
This applies platform-wide to registered content-only artifacts, including
`AGENTS.md`, `CLAUDE.md`, and registered rule files; registration cannot turn
actor-blind missing evidence into a permission failure. Trustworthy AI tool
context may still deny or redirect an unapproved worker write to the normal
governed path while that mechanism is functioning.

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
   staged-view or unattributed evidence. This platform-wide rule includes
   registered `AGENTS.md`, `CLAUDE.md`, and rule files. It intentionally narrows
   the actor-blind commit floor for missing evidence while preserving
   trustworthy write-time worker routing. Functional validation remains valid
   on its merits.

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

## Date-Independent Packet Bindings

The governed service chooses the UTC filename date at execution. Exactness is
therefore bound to these date-independent values:

| Artifact | Version suffix | Full-content SHA-256 |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `-v3.json` | `sha256:fab2376a2912f4a062c9b40ed34129cb8e85e36ae61179dc1d6a7b8fb0138fd4` |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | `-v2.json` | `sha256:d3abfb9f1a35e6db497c79b96a11ea8dc0649e3a8d6d334a1a595d001b8656f6` |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `-v4.json` | `sha256:5d57291198539b2d98e7b0e140e144c1b8db81022988d8c8718ae7fd5d97e4f3` |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `-v3.json` | `sha256:d571012bdaa5f44a41c4d3e5587fc0c5445c09cfb9470515f02720f17bc3bd8c` |
| `GOV-ARTIFACT-APPROVAL-001` | `-v4.json` | `sha256:a6e47fe8abb8682f62f7b208359277a41195db7ee04e064ba95c048dd53878db` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `-v5.json` | `sha256:3e33c1023764597661e20638fe2213f3561dbc502170290e9ec47c984d9dcf3c` |

Pre-creation is prohibited. Each packet is emitted by its matching governed update and validated afterward.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001` v2, proposed v3: sole membership authority;
  content audit is made nonblocking without weakening identity boundaries.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v1, proposed v2:
  declaration and identity mutation remain governed; content observation becomes
  best-effort and repair-forward.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3, proposed v4: revision evidence views,
  honest unattributed provenance, and file-shaped opaque service containers.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2, proposed v3: declaration parity
  remains atomic and blocks identity work; unrelated content-only commits are
  intentionally not blocked by separate declaration drift.
- `GOV-ARTIFACT-APPROVAL-001` v3, proposed v4: owner direct edits need no packet
  or notation; AI tool paths retain full-artifact review.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v4, proposed v5: tool-context guidance is
  separated from actor-blind observation and commit checks.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: the harness-agnostic commit floor
  remains load-bearing for functional checks and evidence validation, but its
  actor-blind missing-packet branch becomes non-rejecting for registered
  content-only changes.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`: trustworthy
  write-time worker routing remains the mechanical path of least resistance;
  review/commit-time actor-blind absence records debt rather than blocking.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: this versioned thread receives independent review
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

- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`: owner-conversation decision that ratifies the
  platform-wide actor-blind content-edit liveness rule and approves all six exact
  amendment bodies.
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-004.md`: closes all
  v002 findings and requires the real owner identifier plus four execution
  clarifications carried in this revision.
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
- `bridge/gtkb-wi5441-owner-liveness-spec-amendments-002.md`: preserves the
  split and requires date-independent targets, canonical packet order, complete
  governing-spec linkage, and the F4-F8 precision corrections carried here.
- `bridge/gtkb-file-move-rename-canonicalization-v4-020.md`: verifies WI-5640
  Stage A; Stage B remains paused pending registry membership closure.

No seeded intake candidate was relevant; those generic intake records were
removed rather than cited as false precedent.

## Canonical Execution Plan

The six content inputs are generated mechanically from the unchanged
`## Exact Specification Amendments` bodies into
`.gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/`. They are
unregistered, non-canonical scratch inputs; they are not approval packets,
governed artifacts, or finalization members. Keep them only through packet and
MemBase exact readback, after which they are disposable.

Before mutation, run these exact commands with `--dry-run`. After independent
GO, rerun the same six commands with only `--dry-run` removed. Each governed
update emits its own packet; no packet is pre-created.

```text
gt spec update --id GOV-PLATFORM-SOT-REGISTRY-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/GOV-PLATFORM-SOT-REGISTRY-001-v3.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --dry-run --json
gt spec update --id DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001-v2.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --dry-run --json
gt spec update --id DCL-SOT-REGISTRY-RECORD-SCHEMA-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v4.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --dry-run --json
gt spec update --id DCL-SOT-REGISTRY-PROJECTION-PARITY-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/DCL-SOT-REGISTRY-PROJECTION-PARITY-001-v3.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --dry-run --json
gt spec update --id GOV-ARTIFACT-APPROVAL-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/GOV-ARTIFACT-APPROVAL-001-v4.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --status specified --dry-run --json
gt spec update --id DCL-ARTIFACT-APPROVAL-HOOK-001 --content-file .gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/DCL-ARTIFACT-APPROVAL-HOOK-001-v5.md --change-reason "WI-5441 owner-liveness exact specification amendment" --auq-id DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS --auq-answer "Approved as stated: platform-wide registered content-edit liveness and six exact amendments." --owner-presented --status specified --dry-run --json
```

The header fields `requirement_sufficiency_state` and
`spec_status_overrides` are documentary summaries only. Machine authority for
the gap is the `## Requirement Sufficiency` section. Machine authority for the
two lifecycle overrides is the explicit `--status specified` flags above,
acceptance criterion 3, emitted packet content, and final MemBase readback.

## Spec-Derived Verification Plan

| Requirement | Executable evidence | Expected result |
| --- | --- | --- |
| Six date-independent packets | For each exact content file, run `gt spec update --dry-run --json`; after GO, run the same governed update without `--dry-run`, then validate the service-emitted packet | Exactly six packets under the declared envelope; each artifact id, `-v<N>` suffix, and full-content SHA-256 matches the binding table; no packet is pre-created |
| Sole registry membership authority | Read back `GOV-PLATFORM-SOT-REGISTRY-001` v3 | Membership authority and identity boundaries remain blocking; content audit gaps are nonblocking |
| Identity mutation oversight | Read back `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2 | Move, rename, delete, locator, coverage, lifecycle, and removal still require governed transition authorization |
| Revision and opaque-container schema | Read back `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v4 | Evidence views, honest unattributed provenance, file-shaped opaque containers, and past-tense v3 migration are present |
| Declaration/projection atomicity | Read back `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v3 | Identity operations remain parity-blocked; unrelated content-only commit liveness is explicit |
| Platform-wide owner direct edit | Read back `GOV-ARTIFACT-APPROVAL-001` v4 and `DCL-ARTIFACT-APPROVAL-HOOK-001` v5 | Registered content-only edits, including AGENTS/CLAUDE/rules, are not rejected by actor-blind missing evidence; trustworthy worker routing remains governed |
| Lifecycle accuracy | Inspect the two updated rows | Approval GOV v4 and hook DCL v5 are `specified`, not `verified` |
| Cross-cutting floor | Run the formal/narrative approval tests and inspect the parent test plan | Existing implementation remains unchanged in this child; parent must test write-time routing plus nonblocking actor-blind absence |
| Exact content | Independently SHA-256 each normalized proposal description and compare with packet and MemBase readback | Six byte-identical normalized descriptions and expected versions |
| Scope ceiling | Compare governed target inventory and the full worktree before/after | Governed mutations are exactly six service-emitted packets plus `groundtruth.db`; six transient inputs under `.gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/` are generated from the displayed bodies, excluded from finalization, and disposable after exact readback; no source/config/test/registry declaration changes |
| Parent sequencing | Show both bridge threads and all six current specs | Child GO precedes updates; child VERIFIED precedes parent refile |
| Bridge preflights | Applicability and mandatory clause preflights against exact filed bytes | Exit 0; no missing required/advisory specs or blocking clause gap |

## Acceptance Criteria

1. Each of the six canonical `gt spec update` operations emits its own packet;
   no packet target is created before the corresponding update.
2. Exactly six emitted packets exist under
   `.groundtruth/formal-artifact-approvals/**`; each matches its artifact id,
   `-v<N>` suffix, and replacement-content SHA-256 from the binding table.
3. The six specifications advance to v3, v2, v4, v3, v4, and v5. The first
   four retain their current status; `GOV-ARTIFACT-APPROVAL-001` v4 and
   `DCL-ARTIFACT-APPROVAL-HOOK-001` v5 land as `specified`.
4. The owner no-notation, nonblocking-audit, honest-unattributed-provenance,
   repair-forward, and intentionally platform-wide registered-content rules
   appear exactly without weakening registry identity or irreversible-effect
   governance.
5. Declaration/projection drift blocks identity and membership work but does
   not independently block an unrelated content-only commit.
6. No source, configuration, hook, test, registry declaration, filesystem
   identity, migration file, or dispatcher setting changes. The only governed
   artifacts mutated are the six emitted packets and `groundtruth.db`. Six
   transient content inputs may be generated under
   `.gtkb-state/propose-drafts/wi5441-owner-liveness-v005-contents/`; they are
   unregistered non-canonical scratch, excluded from finalization, and disposable
   after exact packet and MemBase readback.
7. No WI-5640 Stage B apply, source deletion, push, release, deployment,
   credential action, destructive cleanup, or history rewrite occurs. One
   bounded local finalization commit of the six packets plus `groundtruth.db`
   is permitted only through terminal independent VERIFIED.
8. The parent WI-5441 proposal is not refiled as `Existing requirements
   sufficient` until all six current specification records and packet hashes
   reproduce these approved versions exactly.

## Specification-Derived Verification Command Evidence

Before mutation, Prime runs all six canonical updates with `--dry-run --json`
and asserts predecessor version, proposed version, artifact type, content hash,
dynamic packet target, and zero mutation. After GO, Prime reruns each command
without `--dry-run`; that operation emits the packet and appends the spec
version. Prime then validates each emitted packet with:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/validate_formal_artifact_packet.py <emitted-packet>
```

The post-amendment report MUST also execute and record:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py platform_tests/hooks/test_narrative_artifact_approval.py -q --no-header
```

Those tests are non-implementation regression evidence only. Exact packet
validation, statuses, versions, content hashes, and six-spec readback are the
authoritative evidence for this requirement-capture slice. Parent implementation
remains separately reviewed.

## Risk / Rollback

The primary risk is weakening identity governance while repairing content-edit
liveness. The complete text distinguishes unchanged-locator content edits from
registry declaration, locator, coverage, lifecycle, membership, and irreversible
transitions. The platform-wide actor-blind narrowing is intentional; trustworthy
worker-tool routing remains the path of least resistance.

The second risk is date and packet-order drift. The packet envelope is date
independent, while artifact id, version suffix, and replacement-content hash
bind exactness. `gt spec update` must emit the packet; pre-creating a target is a
hard error and is prohibited by the plan.

The third risk is partial append-only progress. Before mutation, all six dry
runs must pass against the same predecessor versions. After GO, execute and
validate one governed update at a time. On any failure, stop and report the
exact partial state; never rewrite spec history or fabricate an absent packet.

No source rollback exists in this child. A content correction requires a new
reviewed specification version. The bounded local finalization set contains
only the six emitted packets and `groundtruth.db`.

## Governance Detector Disposition

The parent v003 JSON-escape suppression remains retired. This revision uses a
literal packet-envelope path and no escaped spelling. Mechanically, the
`governance_review` metadata exemption short-circuits the approval-evidence ask
check before target-path merits evaluation; this proposal does not claim that
the merits branch executed. Independent review must still confirm the target
set is allowed and the forbidden governance-review target set is empty.

## Requested Loyal Opposition Action

Confirm that v002 F1-F8 remain closed and that v004 F1-F6 are resolved without changing the correct split. Verify
the dynamic packet envelope plus `groundtruth.db` remain allowed in
`governance_review`; reproduce all six content hashes and predecessor versions;
confirm the canonical emit-then-validate order, the two `specified` overrides,
the platform-wide owner intent, complete specification linkage, and zero
authorization for parent implementation or WI-5640 Stage B.

## Recommended Commit Type

`docs:` - six append-only governance specification versions and their approval
packets; no implementation behavior changes in this thread.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
