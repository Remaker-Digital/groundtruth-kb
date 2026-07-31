NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user

# GT-KB Artifact Registry Authority And Quarantine Sweep Governance Review

bridge_kind: governance_advisory
Document: gtkb-artifact-registry-authoritative-hygiene-sweep
Version: 001 (NEW)
Date: 2026-07-22 UTC
Related Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Related Work Item: WI-5441
Implementation authorization: Not requested by this governance-review proposal.
target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**", "config/registry/sot-artifacts.toml", "config/governance/spec-applicability.toml", "config/governance/adr-dcl-clauses.toml", "config/agent-control/harness-capability-registry.toml", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/project/artifact_registry.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/hygiene/registry_sweep.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "scripts/check_protected_commit_authorization.py", ".claude/hooks/scanner-safe-writer.py", ".claude/hooks/destructive-gate.py", ".codex/gtkb-hooks/destructive-gate.cmd", ".claude/skills/gtkb-artifact-registry/SKILL.md", ".codex/skills/gtkb-artifact-registry/SKILL.md", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_artifact_registry.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "platform_tests/skills/test_gtkb_artifact_registry_skill.py", "platform_tests/scripts/test_artifact_registry_cli.py", "platform_tests/hooks/test_artifact_registry_mutation_gate.py"]

## Claim

GT-KB should replace its descriptive, manually edited SoT-class inventory with a deterministic artifact-membership control plane. `config/registry/sot-artifacts.toml` remains the sole authority for whether a platform artifact belongs to GT-KB. A CLI becomes the only registry mutation surface; an OPS-envelope managed skill becomes the only worker-facing orchestration surface. Registered artifact mutation is observed automatically, registered delete/move/rename is denied without a hash-bound authorization, and a root hygiene sweep quarantines every in-scope unregistered path for exactly 30 days before operation-time-revalidated automatic deletion.

This document requests independent review of the governance family and implementation decomposition only. It does not authorize source, configuration, hook, skill, database-spec, quarantine, purge, Git, release, deployment, credential, dispatcher, or external-system mutation.

## Owner Decision And Supersession

The governing owner decision is `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`.

It establishes all of the following:

1. `config/registry/sot-artifacts.toml` is the ultimate membership source of truth.
2. Registry identity/lifecycle operations are shielded behind a deterministic CLI and an OPS-only managed skill.
3. Registered artifact changes update registry state automatically.
4. Registered delete/move/rename requires mechanical authorization and an atomic registry transition.
5. Adding a load-bearing artifact must establish registry coverage; omission is catastrophic because unregistered artifacts are sweep-eligible.
6. The first sweep follows a complete reconciliation, not an assumption that Git tracking implies membership.
7. The platform sweep covers `E:\GT-KB` but skips each `applications/<child>/` directory because each hosted application owns a separate registry SoT.
8. In-scope unregistered artifacts are quarantined.
9. Quarantine retention is exactly 30 days, cannot be shortened by workers, and ends in automatic permanent deletion only after fresh revalidation.
10. Re-registration blocks expiry deletion and surfaces deterministic restoration.
11. Necessary formal governance changes are owner-authorized.

The decision supersedes prior GOV/DCL/ADR/procedure/skill language only where it conflicts with this registry authority, sweep, reclaim, quarantine, retention, or deletion model. It does not revoke unrelated role separation, independent review, project authorization, credentials, release, deployment, or root-boundary governance.

## Current-State Evidence

Read-only reconciliation on 2026-07-22 found:

- TOML and MemBase projection currently agree: 50 rows in each, no field divergence.
- The repository has 19,093 Git-tracked files.
- Existing registry expansion covers 13,484 tracked files and leaves 5,609 tracked files uncovered.
- There are 128 non-ignored untracked paths, of which 104 are uncovered.
- The active 90-row file-reference migration manifest has only 7 registered source paths and no registered destination paths.
- `_check_sot_registry_completeness` currently checks TOML/projection parity plus existence of active concrete paths; it does not perform reverse filesystem coverage or fail on unregistered load-bearing paths.
- `scripts/gtkb_file_reference_migration.py` already treats the registry as exclusive scan authority and blocks unregistered destinations. The incomplete registry therefore creates a concrete false-negative and migration-block risk.
- `gt registry` currently exposes `list`, `show`, `validate`, `sync`, `diff`, and `audit-duplicates`; it has no governed register/amend/transition authorization, full-root reconciliation, revision observation, retention-manifest, quarantine, restore, or expiry surface.
- `gt hygiene reclaim` already provides receipted plan/trash/purge/restore mechanics and fresh registry/Git checks, but its candidate model is selective and its `deep-clean` path can purge immediately. That is not the owner-approved full-root, 30-day registry-authoritative model.
- Existing hygiene-sweep text scanning and artifact-lifecycle loading-graph discovery remain useful evidence sources, but neither is membership authority.

These counts are diagnostic only. No current unregistered path is declared disposable by this proposal.

## Requirement Sufficiency

Existing requirements are not sufficient without revision.

- `GOV-PLATFORM-SOT-REGISTRY-001` currently governs SoT classes, calls TOML a human edit-surface, permits direct edit plus sync, and sets WARN severity. It does not make every platform artifact a membership decision or require reverse coverage.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` cannot unambiguously distinguish exact files, recursive directories, globs, opaque service containers, MemBase tables, or external runtime identities.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` currently prescribes manual TOML edit followed by `gt registry sync`; that conflicts with CLI-only mutation and automatic observed revision updates.
- `GOV-WORK-TREE-HYGIENE-001` requires batch-specific owner apply evidence and treats destructive behavior as separately approved. The new owner decision pre-authorizes the fixed 30-day expiry policy after a governed sweep while retaining fail-closed operation-time checks.
- `SPEC-INTAKE-97538b` correctly rejects Git as essentiality authority but needs the stronger consequence that every in-scope unregistered path becomes quarantine-eligible only after reconciliation closes all unknowns.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` says “No unbounded purge.” The new decision supersedes that phrase only for the complete, registry-derived, hash-bound root sweep with 30-day quarantine and expiry revalidation.
- The current `gtkb-hygiene-reclaim` skill states that absence from the registry is not trash authority. That statement is superseded for this exact registry-authoritative sweep after reconciliation is closed.

## Proposed Governance Family

The implementation proposal that follows this review should generate owner-authorized formal-artifact packets and append new versions of:

1. `GOV-PLATFORM-SOT-REGISTRY-001` v2: registry is exclusive platform artifact-membership authority; direct mutation prohibited; reverse coverage is release-blocking; addition is routine, removal requires oversight.
2. `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v3: add unambiguous locator/coverage semantics and mutation-observation metadata contracts.
3. `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` v2: stable declarations remain TOML-authoritative; MemBase projection parity covers declarations; append-only observed revisions are automatically maintained state and cannot grant membership.
4. `GOV-WORK-TREE-HYGIENE-001` v2: define the complete registry-authoritative platform sweep, 30-day quarantine, automatic expiry authority, and restoration block.
5. `SPEC-INTAKE-97538b` v2: clarify that Git status is evidence only and registry classification is the sole retention decision.
6. New `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`: choose the compound declaration/revision-ledger architecture and reject direct TOML edits, Git-derived membership, immediate purge, and ad hoc exclusion lists.
7. New `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`: specify register/amend/observe/move/rename/delete/remove authorization and transaction invariants.
8. New `DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001`: specify inventory closure, retention-manifest derivation, application-child exclusions, no-follow filesystem traversal, quiescence, and apply revalidation.
9. New `DCL-QUARANTINE-RETENTION-EXPIRY-001`: fix retention at 30 days and specify automatic deletion, re-registration blocking, restoration visibility, and immutable receipts.

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, and unrelated governance remain cited constraints unless the formal diff proves a narrow conflicting clause requires a successor version.

## Registry Data Model

### Membership declaration

TOML remains the sole membership authority. Each filesystem locator must declare one coverage mode:

- `exact`: one file, directory entry, symlink, or reparse-point object only.
- `recursive`: a directory and all non-service descendants are registered artifacts.
- `glob`: the deterministic set matched under the root, with no path escape.
- `opaque_container`: the container is registered, while payload lifecycle is controlled by its dedicated service ledger. This is intended for quarantine payload storage and similar service-owned data, not as a general bypass.
- `virtual`: a MemBase table or external runtime identity with no filesystem retention effect.

Existing rows must be migrated explicitly; no locator type may be inferred permanently from punctuation or current disk state.

### Automatic currentness

The registry control plane consists of:

- TOML declarations: canonical membership, ownership, mutation API, lifecycle, coverage mode, and authority.
- MemBase `sot_artifacts`: exact projection of declaration fields.
- Append-only MemBase `sot_artifact_revisions`: observed digest/state history for concrete registry members. Revision rows include entry id, canonical relative path, object kind, content or Merkle digest, size, observation time, actor/session, operation, and predecessor revision.

Observed revision rows do not create membership and do not weaken TOML authority. This avoids recursively rewriting the TOML file whenever a registered artifact changes while still making every governed content alteration mechanically current and auditable.

### Registry transaction journal

Every mutating CLI command writes an intent journal before touching TOML, the projection, a registered path, or a quarantine payload. Completion records the declaration digest, prior/current observed revision, filesystem result, projection transaction, and receipt digest. Recovery is deterministic after partial failure. A registry lock serializes declaration and identity transitions.

## CLI Boundary

All registry operations must be available only through `gt registry`; direct TOML mutation and direct projection writes become gate failures.

Proposed command contract:

| Command | Mutation | Minimum authority |
|---|---:|---|
| `gt registry inspect` | no | any role; full-root report |
| `gt registry validate` | no | any role; declaration, projection, revision freshness, and reverse coverage |
| `gt registry reconcile plan` | no | OPS envelope for worker orchestration |
| `gt registry register` | yes | OPS envelope, valid authority spec, no removal oversight |
| `gt registry amend` | yes | OPS envelope; non-identity field changes only |
| `gt registry observe` | yes | automated-only service/hook path after governed content mutation |
| `gt registry transition request` | journal only | OPS envelope; exact digest-bound move/rename/delete/remove proposal |
| `gt registry transition apply` | yes | OPS envelope plus owner evidence and independent GO matching the request digest |
| `gt registry retention-manifest` | evidence only | OPS envelope; hash-bound allow/exclusion set derived from a closed reconciliation |
| `gt registry sweep plan` | evidence only | OPS envelope; full-root candidate manifest |
| `gt registry sweep quarantine` | yes | OPS envelope, matching plan/registry/inventory hashes, quiescence, owner sweep evidence |
| `gt registry quarantine list` | no | OPS envelope |
| `gt registry quarantine restore` | yes | OPS envelope; requires registered destination or explicit owner evidence |
| `gt registry quarantine expire` | yes | automated-only scheduled path; no worker-supplied age override |

The current free-standing `sync` command becomes an internal transaction step or a read-only repair plan. It must not remain a route for direct TOML edits.

## Registered Mutation Enforcement

### Content edits

Before a worker write, the gate resolves the target against registry membership and enforces the row's owner role, mutation API, active project authorization, bridge GO, matching claim, and implementation-start evidence. After a successful write, the hook calls `gt registry observe` to append the new revision. A stale observed revision blocks commit, release, retention-manifest generation, and sweep.

Hook gaps cannot silently authorize mutation. Native or unsupported harness paths use the same deterministic CLI from Codex/Claude adapters, and the commit gate performs a complete freshness check as a backstop. External/manual changes are detected by `inspect`/doctor and reported as stale registry state until reconciled; they do not silently rewrite membership.

### Delete, move, rename, and registry removal

The protected operation is bound to entry id, source locator, current digest, intended operation, destination when applicable, owner evidence, independent bridge verdict, and expiry. Apply revalidates all fields immediately before mutation.

- Move/rename updates filesystem identity, TOML declaration, MemBase projection, observed revision, and receipt as one recoverable transaction.
- Delete first transitions the artifact into quarantine; permanent deletion follows only the fixed expiry contract.
- Removing membership requires the same oversight even if the file no longer exists.
- A worker cannot turn an unauthorized delete into an authorized operation by first deleting and then editing the registry.

## First-Sweep Reconciliation

The first sweep is fail-closed and proceeds in distinct stages.

### Stage 1: deterministic census

Walk `E:\GT-KB` without following symlinks, junctions, or reparse points. Record each object by normalized relative path, object kind, size, timestamps used only as evidence, and content/Merkle digest. Skip each immediate child directory under `applications/`; do not skip files placed directly in `applications/` or unrelated siblings. Detect case-fold collisions and paths that cannot be represented safely.

### Stage 2: evidence overlay

For every census object, calculate independent evidence from:

- current registry expansion;
- Git tracked/ignored/untracked status, as non-authoritative evidence;
- effective worker loading graph and startup/hook/entry-point/config discovery;
- Python imports, package data, console scripts, CI/workflow inputs, generated-adapter manifests, managed-skill registries, test collection, service restore registries, and active runtime configuration;
- existing artifact-lifecycle, inventory, and file-reference migration outputs.

### Stage 3: classification closure

Classify every in-scope object as `registered`, `structural_ancestor`, `quarantine_service_payload`, `unregistered_load_bearing`, or `unregistered_disposable`. `unknown` is permitted in reports but blocks an executable plan. Git tracking alone can never select either retained or disposable.

Newly discovered load-bearing artifacts are registered through the CLI. Duplicate, obsolete, generated, cache, residue, and unexplained paths require explicit evidence-backed classification. Registry removal is never used merely to make a candidate disappear.

### Stage 4: hash-bound retention manifest

Generate a canonical manifest containing root identity, registry declaration digest, projection revision, complete inventory digest, application-child exclusions, exact retained paths, recursive/glob expansions, structural ancestors, opaque service containers, disposable candidates, and the final plan digest. The manifest is the sweep exclusion/retention list. Handwritten exclusion files are invalid.

### Stage 5: dry-run and independent review

The first complete manifest receives independent LO review. Any registry change, inventory change, candidate byte change, application-boundary change, or newly discovered unknown invalidates it.

### Stage 6: quarantine apply

With a matching approved plan, quiescence, and OPS envelope, atomically move each candidate into the registered opaque quarantine service container. Preserve relative path, path kind, content digest, source stat evidence, plan digest, registry digest, and a per-item receipt. The sweep never permanently deletes directly.

## Thirty-Day Quarantine And Automatic Expiry

Each quarantined item receives immutable `quarantined_at` and `expires_at = quarantined_at + 30 days` values. No CLI flag or worker input can reduce retention. The automated expiry service processes only exact receipted payloads and, at operation time, revalidates:

1. current time is at or after the recorded expiry;
2. the receipt and payload path are intact and under the quarantine container;
3. payload bytes still match the receipt;
4. the original source path and artifact identity remain unregistered;
5. no current registry entry, transition request, restoration request, or active plan claims the payload;
6. the applications boundary and root identity are unchanged;
7. no symlink/reparse/path-escape condition exists.

If re-registration is detected, expiry is blocked, the item becomes `restore_pending`, and `gt registry quarantine list` plus doctor/session visibility surface the required restoration. Automatic expiry authority derives from the owner decision and fixed DCL; no new per-item owner prompt is required after all checks pass.

## OPS Managed Skill

Create canonical `.claude/skills/gtkb-artifact-registry/SKILL.md`, generated Codex adapter, capability-registry row, and contract tests.

The skill must:

- declare `allowed_activities: [ops]` and fail closed outside an open OPS envelope;
- orchestrate only `gt registry` commands, never edit TOML/SQLite/quarantine paths directly;
- distinguish read-only inspect/reconcile from mutating register/transition/quarantine/restore/expire operations;
- require exact command receipts and expose blockers without suggesting raw filesystem commands;
- generate retention manifests through the CLI and never hand-author exclusions;
- forbid direct `Remove-Item`, `Move-Item`, `rm`, `mv`, `git clean`, wildcard deletion, direct TOML edits, direct SQLite updates, retention shortening, application-child traversal, and manual quarantine payload deletion;
- state that the first sweep remains blocked until reconciliation has zero unknown and zero unregistered-load-bearing paths.

The current `gtkb-hygiene-sweep` remains the orchestrator for deterministic text/inventory scans. The current `gtkb-hygiene-reclaim` becomes a lower-level compatibility/recovery surface or is revised to delegate registry-authoritative platform sweep operations to the new skill/CLI. It must no longer state that absence from the registry is never trash authority for a closed, approved registry sweep.

## Implementation Decomposition

After governance review, file separate implementation proposals under `PROJECT-GTKB-HOUSEKEEPING-HARDENING` / `WI-5441` with a new active PAUTH that names the exact work items/specs and mutation classes.

1. Governance and schema: approval packets; append spec versions; DB migrations for locator semantics, observed revisions, transition journals, quarantine receipts.
2. Registry CLI: lock, transactions, register/amend/observe/transition, strict direct-edit deprecation, deterministic receipts.
3. Coverage and currentness: reverse inventory, load-bearing discovery adapters, doctor/release ERROR gates, hook/commit integration.
4. Managed skill: canonical OPS skill, generated adapters, registry/manifest/scenario updates, structural tests.
5. Sweep planner: full-root no-follow census, application-child exclusion, classification closure, hash-bound retention manifest.
6. Quarantine actuator: same-volume atomic moves, receipts, restore, 30-day expiry service, expiry revalidation.
7. Initial reconciliation: report-only inventory, owner/LO review of unresolved classifications, registry additions, repeat until closed.
8. First live sweep: separately approved exact plan, quarantine apply, post-apply verification. No expiry can occur before 30 elapsed days.

No phase may bundle the first live sweep with implementation of the actuator that performs it.

## Specification Links

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - direct owner authority and scoped supersession.
- `GOV-PLATFORM-SOT-REGISTRY-001` - current registry authority to be revised.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` - current row schema to be revised.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - current TOML/MemBase parity contract to be revised.
- `GOV-WORK-TREE-HYGIENE-001` - current report-first/apply-evidence contract to be revised narrowly.
- `SPEC-INTAKE-97538b` - Git is not cleanup-essentiality authority.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - named-artifact classification and audited quarantine precedent.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - hosted application boundary and in-root placement.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - cross-cutting requirements need deterministic enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent bridge review and numbered-file authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires an active bounded PAUTH.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time project authorization must be fresh.
- `GOV-ARTIFACT-APPROVAL-001` - formal GOV/DCL/ADR updates require approval packets.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - later implementation proposals must carry concrete links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map each clause to executable evidence.
- `ADR-REGISTRY-DISCOVERY-001` - managed command/check registration and incremental modularity.
- `SPEC-1853` - stable managed-skill/tool identity.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - capability registration and harness projection.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - decision-to-spec-to-work-to-test traceability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable lifecycle artifacts and explicit states.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - revisions, supersession, quarantine, and removal are lifecycle events.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - controlling owner decision for this proposal.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - registry-first cleanup guardrails after loss of an essential ignored artifact; explicitly rejects Git as essentiality authority.
- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - prior bounded cleanup charter; superseded only where its “No unbounded purge” language conflicts with this exact closed-registry sweep.
- `DELIB-0724` - historical VERIFIED managed artifact registry thread; useful precedent, not current platform membership authority.
- `DELIB-1204` - later archival view of the same historical thread as ORPHAN; confirms it is not live authority.
- `DELIB-20263459` - prior hygiene sweep scope regression caused by scanning copied worktrees/historical surfaces; motivates strict traversal and application boundaries.
- `DELIB-202666366` - WI-5142 hygiene-reclaim review; confirms managed-skill linkage, registry checks, byte accounting, quiescence, and finalization-scope expectations.
- `DELIB-202666274` - active Artifact Decontamination PAUTH precedent; it forbids destructive cleanup and therefore is not used as authority for this new sweep.

## Spec-Derived Verification Plan

| Requirement | Planned mechanical evidence |
|---|---|
| TOML is sole membership authority | tests prove projection/revision rows cannot add membership and direct TOML/projection edits fail gates |
| Every locator is unambiguous | schema migration tests cover exact/recursive/glob/opaque/virtual and reject implicit or escaping forms |
| Add is easy; removal has oversight | CLI tests register in one OPS transaction; removal/move/delete fail without matching owner evidence plus independent GO |
| Registered content stays current | write-hook/CLI tests prove successful edits append observed revisions; stale revisions block commit/release/sweep |
| Full-root coverage | synthetic and live report-only tests classify every in-scope object exactly once and fail on unknown/load-bearing gaps |
| Application isolation | tests skip only immediate `applications/<child>/` directories, retain direct `applications/` files in scope, and never follow links |
| Hash-bound retention manifest | canonical serialization tests prove registry/inventory/path/byte changes invalidate apply |
| No direct permanent deletion | quarantine tests prove sweep only moves payloads and writes immutable receipts |
| Fixed 30-day retention | boundary tests at 29d23h59m59s refuse; 30d permits only after all fresh checks; no override flag exists |
| Re-registration blocks expiry | tests register original path after quarantine, verify `restore_pending`, refuse deletion, and restore without overwrite |
| Recovery after interruption | fault injection at every transaction phase converges through journal recovery without lost membership or payload |
| OPS-only skill | skill catalog and activity-envelope tests deny build/project/deliberation/no-envelope use and forbid raw mutation commands |
| Existing behavior preserved | focused registry, doctor, file-migration, hygiene reclaim/sweep, hook, capability-registry, and adapter suites remain green |

The implementation proposal must replace these planned checks with exact test nodes and commands before requesting GO.

## Acceptance Criteria For This Governance Review

1. LO confirms or corrects the scoped supersession interpretation.
2. LO confirms the compound TOML-declaration plus append-only observed-revision model preserves TOML as sole membership authority.
3. LO confirms the proposed governance family is complete and does not create competing SoTs.
4. LO confirms `PROJECT-GTKB-HOUSEKEEPING-HARDENING` / `WI-5441` is the correct lineage and identifies any necessary sibling WIs rather than duplicate work.
5. LO confirms the application-child exclusion is faithful to the hosted-application isolation contract.
6. LO confirms 30-day automatic expiry can derive standing authority from the owner decision while still requiring operation-time revalidation.
7. LO confirms no current unregistered path is treated as disposable until classification closure.
8. LO confirms implementation, initial reconciliation, first live sweep, and expiry remain separately reviewable stages.

## Risk And Rollback

- **False-negative registry coverage:** catastrophic data loss risk. Mitigation: unknown/load-bearing gaps block executable manifests; first sweep requires independent review and fresh hashes.
- **Overbroad recursive rows:** can preserve residue and defeat the sweep. Mitigation: explicit coverage modes, reverse expansion reports, and reviewer-visible row-by-row reconciliation.
- **Overbroad classification of tracked files:** can turn Git into de facto authority. Mitigation: Git is evidence only; each retained path must resolve through registry coverage.
- **Hook bypass or concurrency:** can leave revisions stale. Mitigation: registry lock, journal recovery, complete commit/release/sweep freshness gates, and quiescence.
- **Application boundary escape:** can sweep adopter data. Mitigation: root identity, immediate-child exclusion, no-follow traversal, reparse detection, and synthetic Windows tests.
- **Quarantine state loss:** can strand or prematurely delete payloads. Mitigation: opaque registered container, immutable receipt hash, payload digest, recovery journal, and expiry fail-closed.
- **Automatic expiry misclassification:** irreversible loss. Mitigation: fixed age, no override, re-registration/claim checks, exact payload identity, and refusal on any uncertainty.

Rollback before any live sweep is append-only governance supersession plus code/config rollback through the normal bridge path. After quarantine apply, rollback is `gt registry quarantine restore` against exact receipts. After a correctly expired permanent deletion, rollback is available only from the artifact's declared backup policy; this is why reconciliation closure and 30-day restoration visibility are hard prerequisites.

## Owner Input

No owner decision remains open for this review. Mike selected quarantine and fixed retention at 30 days, authorized all necessary formal governance changes, and declared the scoped plan to supersede conflicting prior artifact-registry/hygiene governance.

## Requested Loyal Opposition Action

Review this governance design and return `GO` or `NO-GO` for formalization into approval packets and bounded implementation proposals. In particular, challenge:

1. whether any prior governance outside the stated scoped supersession would be unintentionally impaired;
2. whether the locator modes and declaration/revision split are sufficient for an ultimate membership SoT;
3. whether the first-sweep closure rule can mechanically prevent an unregistered load-bearing artifact from entering quarantine;
4. whether transition authorization and 30-day expiry are fail-closed under interruption, concurrency, and re-registration;
5. whether existing WI-5142/WI-5573 work should be dependencies or separate compatibility slices rather than folded into WI-5441.

## Preflight

Applicability and ADR/DCL clause preflights will be run against this exact draft before helper-mediated filing. Their packet hashes and outcomes will be reported in the filing result; no preflight result is claimed in advance.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
