REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user

# WI-5441 Artifact Registry Governance Formalization

bridge_kind: prime_proposal
Document: gtkb-wi5441-artifact-registry-governance-formalization
Version: 003
Responds to: bridge/gtkb-wi5441-artifact-registry-governance-formalization-002.md
Revision reason: Correct the proposal Version metadata from `001 (NEW)` to the parser-valid exact numeric form. Normative content, target paths, PAUTH, acceptance criteria, and implementation scope are unchanged.
Date: 2026-07-22 UTC
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-GOVERNANCE-20260722
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-07-22-GOV-PLATFORM-SOT-REGISTRY-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-22-DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v3.json", ".groundtruth/formal-artifact-approvals/2026-07-22-DCL-SOT-REGISTRY-PROJECTION-PARITY-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-22-GOV-WORK-TREE-HYGIENE-001-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-22-SPEC-INTAKE-97538b-v2.json", ".groundtruth/formal-artifact-approvals/2026-07-22-ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001-v1.json", ".groundtruth/formal-artifact-approvals/2026-07-22-DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001-v1.json", ".groundtruth/formal-artifact-approvals/2026-07-22-DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001-v1.json", ".groundtruth/formal-artifact-approvals/2026-07-22-DCL-QUARANTINE-RETENTION-EXPIRY-001-v1.json"]

## Claim

Formalize the independently approved artifact-registry architecture as nine owner-approved, append-only MemBase specification records and nine corresponding formal-artifact approval packets. This slice changes governance authority only. It does not change database schema, Python source, tests, hooks, configuration, the TOML registry, managed skills, filesystem membership, quarantine contents, or sweep behavior.

The architecture review is `GO` at `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md`. The controlling owner decision is `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`. This proposal uses the real active bounded authorization `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-GOVERNANCE-20260722`; it does not rely on the nonexistent PAUTH string cited in the architecture verdict header.

## Exact Formal Artifact Set

| Artifact | Action | Resulting version | Status |
|---|---|---:|---|
| `GOV-PLATFORM-SOT-REGISTRY-001` | update | 2 | specified |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | update | 3 | specified |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | update | 2 | specified |
| `GOV-WORK-TREE-HYGIENE-001` | update | 2 | specified |
| `SPEC-INTAKE-97538b` | update | 2 | specified |
| `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` | create | 1 | specified |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | create | 1 | specified |
| `DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001` | create | 1 | specified |
| `DCL-QUARANTINE-RETENTION-EXPIRY-001` | create | 1 | specified |

All five predecessor records remain intact. None of these records is promoted to implemented or verified by this slice.

## Proposed Formal Content

The approval packets and inserted specification descriptions must use the following normative content. Formatting may add standard metadata headings, but implementation may not weaken, omit, or silently reinterpret any MUST/SHALL clause below.

### GOV-PLATFORM-SOT-REGISTRY-001 v2

**Title:** Platform-wide Artifact Membership Registry

`config/registry/sot-artifacts.toml` is the sole authority for whether a GT-KB platform artifact belongs to the platform. The MemBase `sot_artifacts` table is its exact declaration projection; projections, observed-revision records, Git state, inventories, caches, loading graphs, manifests, and filesystem presence cannot independently grant membership.

Every load-bearing platform file, directory, glob-expanded member, opaque service container, MemBase authority, and declared external runtime identity MUST be covered by one active registry declaration. An unregistered load-bearing artifact is a release-blocking and sweep-blocking defect. Creation of a load-bearing artifact MUST establish registry coverage in the same governed work transaction.

Registry declaration and lifecycle operations MUST use the deterministic `gt registry` CLI. Direct TOML editing and direct projection-table mutation are prohibited. Registering a new artifact is a routine OPS operation when the authority specification, locator, ownership, and mutation API validate. Removing membership, or deleting, moving, or renaming a registered artifact, requires a digest-bound transition authorization with owner evidence and independent bridge `GO`.

Successful governed content mutation of a concrete registered artifact MUST append current observed-revision evidence automatically. Stale observed state blocks commit, release, retention-manifest generation, and sweep execution.

After a complete reconciliation reaches zero unknown and zero unregistered-load-bearing paths, in-scope unregistered filesystem objects are disposable by the governed hygiene sweep only through quarantine and the fixed retention/expiry contract. Immediate permanent deletion is prohibited.

The platform-root registry does not govern immediate child directories under `applications/`; each hosted application MUST own and enforce its own registry SoT. Files directly inside `applications/` that are not within an application child directory remain in platform sweep scope.

Registry declaration/projection drift, invalid locators, stale observed revisions, and reverse-coverage defects are ERROR severity. The registry self-declaration remains mandatory.

### DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v3

Every declaration retains the existing required identity, domain, lifecycle, storage path, authority, mutation API, versioning, backup, health-check, and owner-role fields. Every declaration MUST additionally carry an explicit `coverage_mode` with one of these values:

- `exact`: registers one filesystem object at the normalized relative locator. It does not implicitly register descendants.
- `recursive`: registers the directory and all non-service descendants reached without following symbolic links, junctions, or reparse points.
- `glob`: registers the deterministic in-root match set produced by the declared pattern. Empty and changed match sets remain visible evidence.
- `opaque_container`: registers a service-owned container while its payload lifecycle is governed by a dedicated service ledger. Payloads do not become independent members merely because they reside in the container. Use requires an explicit authority specification and service mutation API.
- `virtual`: registers a non-filesystem authority such as `membase:<table>` or a declared external runtime identity and has no filesystem-retention effect.

Coverage mode MUST NOT be inferred from trailing separators, wildcard punctuation, current object type, or current existence. Filesystem locators MUST be project-relative, case-normalized for collision detection, path-escape-free, and compatible with Windows path semantics. `recursive` and `opaque_container` locators MUST name directories. `glob` patterns MUST remain within the root. `virtual` locators MUST use a registered virtual scheme. A locator may not ambiguously overlap another active declaration unless the overlap is explicitly validated as identical authority and semantics.

The migration to v3 MUST assign and review a coverage mode for every existing declaration. No default may silently turn a broad directory row into recursive retention.

Concrete members resolved by `exact`, `recursive`, or `glob` receive append-only observed revisions. `opaque_container` receives container-state revisions plus dedicated payload receipts. `virtual` currentness is checked by its declared health function or mutation API.

Unknown fields, invalid enum values, unsafe paths, case-fold collisions, unsupported virtual schemes, ambiguous overlaps, or prohibited opaque-container use fail registry loading.

### DCL-SOT-REGISTRY-PROJECTION-PARITY-001 v2

TOML declarations and current MemBase `sot_artifacts` declarations MUST match exactly for all declaration fields, including `coverage_mode`. Drift is ERROR severity and blocks registry mutation, commit, release, retention-manifest generation, and sweep execution.

The append-only `sot_artifact_revisions` history is currentness evidence, not a second membership authority and not a TOML-parity surface. A revision row cannot create membership. Each revision identifies the registry entry, canonical relative member path or virtual identity, object kind, content or Merkle digest, logical size where applicable, operation, actor/session, observation time, and predecessor revision.

The CLI MUST update declarations, projections, revision evidence, transaction journal, and receipts through one locked recoverable transaction. A journaled incomplete transaction fails closed and MUST be recovered before further registry mutation or sweep planning.

The existing public workflow “edit TOML then run `gt registry sync`” is retired. `sync` may remain only as an internal transaction step or a read-only repair-plan command; it cannot legitimize direct edits. The registry self-row is validated through a normalized non-recursive declaration digest.

### GOV-WORK-TREE-HYGIENE-001 v2

GT-KB retains deterministic report-first hygiene. Existing stray-work and text-scan diagnostics remain evidence surfaces and do not determine artifact membership.

A registry-authoritative platform hygiene sweep inventories the complete `E:\GT-KB` root without following symbolic links, junctions, or reparse points and skips each immediate child directory under `applications/`. It derives retention exclusively from current registry declarations plus structural ancestors required to reach registered paths and the governed quarantine service container.

An executable sweep requires zero unknown objects, zero unregistered-load-bearing objects, valid declaration/projection parity, fresh observed revisions, a hash-bound retention manifest, a matching current inventory, quiescence, an OPS envelope, and owner evidence for the exact sweep plan. Git tracked, ignored, and untracked classifications are evidence only.

The sweep moves unregistered-disposable objects into quarantine and writes immutable receipts. It never permanently deletes directly. Quarantine retention is exactly 30 days and cannot be shortened by workers. At expiry, an automated actuator may permanently delete an exact receipted payload without a new per-item owner prompt only after all operation-time checks in `DCL-QUARANTINE-RETENTION-EXPIRY-001` pass.

Re-registration, restoration claims, byte drift, path ambiguity, invalid receipts, root drift, or any check uncertainty blocks expiry deletion and surfaces the item. No proposal may both implement a sweep actuator and execute the first live sweep.

### SPEC-INTAKE-97538b v2

The phrase “tracked artifact list” means the platform artifact registry, not Git's tracked-file set. `config/registry/sot-artifacts.toml` is the sole cleanup-essentiality authority for platform artifacts.

Git tracked, ignored, and untracked status MUST NOT decide retention or disposal. A load-bearing artifact MUST be registered when created. A complete reconciliation MUST classify every in-scope object; any unknown or unregistered-load-bearing object blocks sweep execution.

After reconciliation closure, an in-scope object that is not covered by the registry is eligible for the governed quarantine sweep. Eligibility does not permit immediate deletion: the object receives a receipt, a non-shortenable 30-day quarantine, re-registration protection, restoration visibility, and operation-time expiry checks.

The platform rule excludes immediate application child directories under `applications/`, which are governed by each application's registry. No other platform path is excluded merely because it is ignored, generated, cached, historical, or untracked.

### ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001 v1

**Context.** The existing registry describes SoT classes and checks TOML/projection parity, but it does not establish complete reverse filesystem coverage, automatic revision currentness, safe identity transitions, or a deterministic retention boundary. Git cannot supply membership authority. Rewriting TOML after every content edit would create recursive self-hashing, high-contention churn, and broad-directory digest ambiguity.

**Decision.** Adopt a compound artifact-registry control plane:

1. TOML declarations are the sole membership authority.
2. `sot_artifacts` is the exact declaration projection.
3. append-only `sot_artifact_revisions` records automatic currentness evidence and cannot grant membership;
4. explicit coverage modes define filesystem and virtual locator semantics;
5. `gt registry` is the exclusive mutation surface;
6. digest-bound transition authorization governs registered delete/move/rename/removal;
7. a complete registry-derived retention manifest governs hygiene quarantine;
8. quarantine lasts exactly 30 days and expiry is an operation-time-revalidated automatic action;
9. immediate application child directories are delegated to their own registry SoTs.

**Rejected alternatives.** Git-derived membership is rejected because ignored and untracked artifacts may be essential. Manual TOML edit plus sync is rejected because it cannot guarantee atomic lifecycle transitions. Persisting every observed digest in TOML is rejected because it causes recursive registry rewrites and multi-worker contention. Handwritten exclusion lists are rejected because they can drift from authority. Immediate purge is rejected because it removes the restoration window. Treating every directory row as recursive is rejected because it can preserve arbitrary residue.

**Consequences.** Registry correctness becomes a release and sweep gate. Existing rows require explicit coverage-mode migration. Mutation gates and hooks must converge on the CLI. Initial reconciliation is substantial and the first live sweep remains separately approved. The revision ledger is authoritative evidence of currentness but never of membership.

### DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 v1

All declaration mutation MUST pass through `gt registry` under a registry lock and recoverable transaction journal. Direct TOML, direct `sot_artifacts`, direct revision-ledger, and raw registered-path identity mutation are prohibited worker surfaces.

`register` requires an OPS envelope, unique id/locator, existing authority specification, valid ownership/mutation API, valid coverage mode, no unsafe overlap, and successful declaration/projection transaction. It does not require removal oversight.

`amend` may change non-identity declaration fields under OPS authority but may not disguise a move, rename, deletion, narrowing, or removal. Any change to locator, coverage mode, lifecycle effect, or membership set is an identity transition.

`observe` is automated-only. After a successful governed content mutation it appends the exact current revision. Failed or missing observation leaves the artifact stale and blocks commit, release, retention planning, and sweep.

`transition request` binds entry id, source locator, current revision digest, operation, destination when applicable, owner evidence, intended membership result, and expiry. `transition apply` requires an OPS envelope, matching active request, matching independent bridge `GO`, and fresh operation-time revalidation. A worker cannot authorize deletion by deleting first or editing the registry afterward.

Move/rename MUST update filesystem identity, declaration, projection, revision history, journal, and receipt as one recoverable transaction. Delete first moves the registered artifact into governed quarantine and records its membership transition; permanent deletion remains subject to the 30-day DCL. Membership removal without a present file requires the same oversight.

Hooks, commit gates, release gates, and migration tools MUST call the shared registry resolver and authorization service. Unsupported hook paths fail closed or leave visible stale state; they do not silently authorize mutation.

### DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001 v1

The platform sweep MUST:

1. establish a normalized root identity for `E:\GT-KB`;
2. walk every in-scope object without following links or reparse points;
3. skip only immediate child directories under `applications/` and record each exclusion;
4. include files directly under `applications/` in platform scope;
5. resolve each object exactly once as registered, structural ancestor, opaque service payload, unregistered load-bearing, unregistered disposable, or unknown;
6. treat Git and discovery mechanisms as evidence, never membership authority;
7. block executable planning while unknown or unregistered-load-bearing counts are nonzero;
8. generate a canonical retention manifest bound to root, declarations, projection, observed revisions, complete inventory, application exclusions, retained expansions, ancestors, service containers, disposable candidates, and plan digest;
9. invalidate apply on any authority, path, byte, inventory, boundary, claim, or quiescence change;
10. move exact candidates into quarantine with immutable receipts and never permanently delete during sweep apply.

The initial reconciliation MUST overlay effective worker loading, startup, hook, command entry point, package/import, CI/workflow, generated-adapter, managed-skill, test-collection, service-restore, inventory, and file-reference-migration evidence. Each newly found load-bearing artifact is registered through the CLI. No existing unregistered object is presumed disposable solely from this specification.

The first complete retention manifest requires independent review. The sweep actuator implementation and first live sweep MUST be separate bridge threads. The first live sweep remains blocked until the initial reconciliation is closed and a fresh exact plan receives its own owner evidence and independent `GO`.

### DCL-QUARANTINE-RETENTION-EXPIRY-001 v1

Every sweep-quarantined item receives immutable `quarantined_at` and `expires_at`, with `expires_at` exactly 30 calendar days after `quarantined_at`. No worker, command option, environment variable, configuration value, or transition request may shorten the interval.

The receipt MUST bind original relative path, object kind, source stat evidence, payload path, content or Merkle digest, logical size, registry declaration digest, observed-revision cutoff, inventory digest, sweep plan digest, actor/session, and timestamps.

Automatic expiry may permanently delete only the exact receipted payload and only when all checks pass immediately before deletion:

1. current time is at or after immutable expiry;
2. root and quarantine-container identities match;
3. receipt and payload remain intact and path-confined;
4. payload bytes and object kind match the receipt;
5. original path and artifact identity remain unregistered;
6. no registry declaration, transition, restore request, active plan, or work claim owns the payload;
7. no link, reparse, collision, or path-escape condition exists;
8. the automated actor is using the canonical CLI expiry surface.

Any failure or uncertainty refuses deletion and appends a refusal event. Re-registration marks the item `restore_pending`, blocks expiry, and surfaces it through CLI, doctor, and session visibility. Restoration never overwrites an occupied destination and verifies the payload digest before and after move.

Successful expiry appends a permanent deletion receipt before payload removal intent and a completion event after deletion. Journal recovery MUST distinguish not-started, payload-present, and payload-absent states without repeating unsafe deletion. Restoration after correct expiry depends only on the artifact's declared backup policy.

## Implementation Procedure After GO

1. Generate nine formal-artifact approval packets with the exact full content above, normalized LF bytes, SHA-256, owner decision, architecture GO, PAUTH, and WI references.
2. Validate all nine packets before any spec write. A single failure aborts the batch.
3. Use governed `gt spec update` for the five existing IDs and governed `gt spec record` for the four new IDs, each with its matching approval packet.
4. Preserve predecessor versions and set every new row to `specified`.
5. Query each current record and predecessor history through `gt spec show`/governed spec APIs.
6. File a post-implementation report carrying packet hashes, row/version evidence, predecessor preservation, and unchanged registry parity evidence.
7. Request independent `VERIFIED`. Do not begin CLI/schema implementation from this thread.

## Specification Links

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - owner authority for all formal changes in this slice.
- `bridge/gtkb-artifact-registry-authoritative-hygiene-sweep-002.md` - independent architecture `GO` and phase directives.
- `GOV-PLATFORM-SOT-REGISTRY-001` - target governance family root.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - target declaration schema.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - target declaration projection/currentness boundary.
- `GOV-WORK-TREE-HYGIENE-001` - target hygiene authority.
- `SPEC-INTAKE-97538b` - target owner requirement.
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` - proposed architecture record.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - proposed mutation contract.
- `DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001` - proposed sweep contract.
- `DCL-QUARANTINE-RETENTION-EXPIRY-001` - proposed retention/expiry contract.
- `GOV-ARTIFACT-APPROVAL-001` - each formal artifact requires its own validated approval packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation proposal requires independent review.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active bounded PAUTH is mandatory.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH must be active at packet and insert time.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - normative content and evidence remain independently evaluable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing links are supplied.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived from each proposed clause.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application-child exclusion and root boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable graph traceability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision is promoted into formal authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only revision and creation states are explicit.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - controlling owner decision.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - registry-first preservation and rejection of Git essentiality.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - predecessor cleanup charter; superseded only in the scoped conflict.
- `DELIB-202666366` - prior independent review of hygiene reclaim and managed-skill linkage.
- `DELIB-20263459` - prior hygiene scanner scope regression and boundary evidence.

## Owner Decisions / Input

No owner decision remains open. Mike explicitly authorized all necessary formal GOV changes, fixed quarantine retention at 30 days, and declared the current registry/hygiene plan to supersede conflicting prior governance. The decision is durably captured in `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` and is the owner-decision source for the active PAUTH.

## Requirement Sufficiency

Requirements are sufficient for this governance-only slice. The architecture `GO` specifically directs these nine artifacts. The proposed text above resolves the conflicts identified in the review without choosing implementation details beyond the approved control-plane contracts. Exact SQL schema, Python APIs, CLI argument spelling beyond the approved command families, hook wiring, scheduler implementation, and first-sweep classifications remain implementation design for later bounded proposals.

## Specification-Derived Verification Plan

| Artifact requirement | Verification evidence |
|---|---|
| Five updates are append-only | `gt spec show <id> --json` returns the expected new version while governed history query retains the predecessor |
| Four IDs are created once | pre-insert collision check reports absent; post-insert `gt spec show` reports version 1 |
| All nine remain `specified` | current-row JSON for every ID has `status=specified`; none is implemented/verified |
| Exact owner-approved content | each row description SHA-256 equals its packet `full_content_sha256` |
| Packet completeness | formal packet validator passes action/id/version/content hash, owner evidence, architecture GO, PAUTH, and transcript capture |
| Scoped supersession | textual checks find the sole-membership, CLI-only, app-child exclusion, zero-unknown, quarantine-only, 30-day, no-shortening, and re-registration clauses in the intended records |
| No competing authority | TOML membership, projection, and revision-ledger roles are distinct in GOV/DCL/ADR text |
| No implementation mutation | `git diff --name-only` for this slice contains only exact packet paths and bridge files; semantic DB diff contains only the nine spec rows plus required audit metadata |
| Existing registry unchanged | `gt registry validate --json` remains in sync with the same declaration count and no field divergence |
| Root boundary | every file target is under `E:\GT-KB`; no application child is touched |
| Applicability | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-artifact-registry-governance-formalization --json` passes |
| Clause applicability | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-artifact-registry-governance-formalization` exits 0 with no blocking gaps |

## Acceptance Criteria

1. Nine validated formal-artifact approval packets exist at the exact declared paths.
2. Five target specifications advance by exactly one append-only version and preserve predecessors.
3. Four new specification IDs exist at version 1 with no collision or alias.
4. Every new current row is `specified` and contains the approved normative content.
5. Every row and packet cites the owner decision, architecture `GO`, active PAUTH, WI-5441, and this bridge thread.
6. No source, test, hook, configuration, TOML registry, skill, quarantine, sweep, Git, release, deployment, credential, dispatcher, or external mutation occurs.
7. Registry parity remains unchanged and valid.
8. A post-implementation report receives independent `VERIFIED` before any downstream proposal treats these records as formally implemented.

## Risk And Rollback

- **Semantic weakening across nine records:** mitigated by exact normative content in this proposal and per-record full-content hashes.
- **Partial batch:** all packets validate before writes; each append is auditable. A partial insert halts and is reported, never hidden.
- **Wrong version:** operation-time predecessor checks require 1→2, 2→3, 1→2, 1→2, and 1→2 exactly; four new IDs must remain absent until insert.
- **False implementation status:** all rows remain `specified`; promotion is a later independently verified lifecycle event.
- **PAUTH overreach:** allowed classes are bridge, metadata, and governance evidence only; all destructive and external operations are forbidden.

Formal records are append-only. Rollback never deletes or rewrites a row; it appends a successor version that explicitly supersedes the erroneous version and restores the prior semantics. Approval packets and bridge files remain audit evidence.

## Requested Loyal Opposition Action

Review this exact nine-artifact formalization for `GO` or `NO-GO`. Confirm:

1. the proposed full content faithfully implements the architecture verdict and owner decision;
2. scoped supersession does not impair unrelated governance;
3. the active PAUTH is real, bounded, and sufficient for packet/spec mutation only;
4. the locator modes, declaration/revision split, transition oversight, application boundary, zero-unknown gate, and 30-day expiry clauses are mutually coherent;
5. no implementation detail that belongs in later source/schema/skill proposals has been prematurely made irreversible here.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
