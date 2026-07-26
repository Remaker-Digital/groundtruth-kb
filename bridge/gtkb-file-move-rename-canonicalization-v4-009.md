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

# Revised Proposal: Repair WI-5640 lifecycle, admit migration locators, and restore reproducible closure

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v4
Version: 009
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-008.md
Revises implementation report: bridge/gtkb-file-move-rename-canonicalization-v4-007.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "groundtruth.db", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | metadata | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
input_authority_paths: ["gtkb-file-move-and-rename-list.csv"]

## Revision Claim

This revision accepts all four findings in v4-008 and requests a bounded GO for
two prerequisite operations only. It first repairs WI-5640's mechanically false
terminal lifecycle through the canonical governed backlog service, then admits
the 167 currently unregistered manifest source/destination locators through the
WI-5441 registry transaction API. It also removes WI-5640's private
inventory-reader dependency, rebases the stale F5 allowance, and produces a
fresh deterministic preflight in two clean processes.

This revision does not rewrite any live consumer reference, delete or alter any
obsolete source, remove or relocate any existing registry record, resolve or
terminally verify WI-5640, run Stage B apply, stage or commit Git changes, push,
release, deploy, mutate the dispatcher, or contact an external system. The later
exact consumer-write plan remains a separate reviewed child operation.

## Dependency Gate

This draft MUST NOT be filed or implemented until
`gtkb-wi5441-registry-control-plane-reverse-coverage-v4` receives an independent
strict-chain `VERIFIED` verdict and its implementation bytes are committed.
That gate is now satisfied by
`bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` and commit
`f9731c41f5a3898fc86a3bffbc7c25f771c32f28`. Implementation must load that
committed registry generation through
`groundtruth_kb.project.registry_control_plane.load_registry_snapshot` and bind
the exact current transaction receipt before any registry mutation.

## Current Evidence

- The CSV SHA-256 is
  `02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`.
  Structured CSV parsing proves 90 unique rows, category counts 33 hooks / 38
  rules / 19 agent-control, 90 present tracked sources, 90 present tracked
  destinations, no no-op, duplicate source, duplicate destination, or known
  `conytol` / `gtbk-` typo.
- WI-5441 is independently `VERIFIED` at
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`.
  Commit `f9731c41f5a3898fc86a3bffbc7c25f771c32f28` contains all 73 paths in that
  verdict's finalization list with none missing, plus 23 previously dirty paths
  outside the list. The following commit, `e1762fe29bddeed1da440edefc5782bf11443266`,
  adds only the unregistered disposable path `.gtkb-index-ilk3djzq/index`.
  A fresh canonical inspection at current HEAD reports registry
  `coherent = true`, `current = true`, 145 records, and no missing or stale
  revisions. This proposal does not treat either out-of-scope commit addition as
  migration authority or request a history rewrite.
- The current coherent registry generation contains 145 records, but only 13
  of the 180 unique manifest locators resolve: 11 sources and 2 destinations.
  The sorted LF set of 167 missing locators has SHA-256
  `92baca678bd277f8b0aa3c76576b1bcae48e07d83cefdcc64e58b9aa16ae31b4`.
- MemBase currently reports WI-5640 version 2 as `resolution_status =
  "resolved"`, `stage = "resolved"`, with no `related_bridge_threads`. That
  version was written by `loyal-opposition/goose` on 2026-07-24 with reason
  `Bridge reconciliation: missing_implementation_commit_coverage - all linked
  threads terminal`. The canonical reverse bridge index instead finds eight
  WI-5640 threads, including current NO-GO threads. Invoking the reconciler's
  own strict classifier on the live row returns `action = "reopen"`, `reason =
  "overbroad_resolution_missing_implementation_commit_coverage"`. The built-in
  `--repair-overbroad` sweep cannot repair it because that sweep admits only
  rows whose `changed_by` is exactly `bridge-verified-backlog-reconciler`.
- An in-memory `RegistryResolver` simulation combines the current 145 records
  with the proposed 167 exact records without collision or ambiguity. The
  resulting 312-record resolver resolves all 180 manifest locators.
- The current registry inventory expands to 13,951 unique files with no
  blocking declaration finding. Of those, 13,803 are under the immutable
  `bridge/` audit boundary and 148 are non-bridge registered files. Adding the
  167 missing exact manifest locators produces a deterministic 315-file
  non-bridge authority scan; unregistered trees remain disposable and are not
  traversed as migration authority.
- The registry fault matrix currently returns old/new or blocks every reader,
  but an injected failure after only the canonical declaration replace leaves
  canonical-new / packaged-old / projection-old. `recover_registry` marks that
  exact known state `repair_required` and has no forward-completion branch.
  This draft therefore cannot claim automatic rollback for every fault.
- Current `preflight` fails closed before scanning with
  `ARTIFACT_REGISTRY_UNREGISTERED_TRANSITION` on
  `.claude/hooks/_delib_common.py`. No current reference-closure claim exists.
- Both WI-5659 commits, `f0b27999a` and `c0c4c40e4`, are ancestors of current
  research HEAD. The exact eight-module F5 suite now collects 475 tests and
  reports 471 passed / 4 failed. The former 37 strict-lifecycle fixture failures
  are gone; the four remaining tests are the separately disclosed WI-5178
  work-intent API/fixture cases.
- The three focused Stage A modules report 65 passed. Ruff check and format
  check pass on all six Stage A Python files named in v4-008.
- The July 24 `preflight.json` is historical only. It binds scanner SHA-256
  `6e091bb4...`, while current scanner SHA-256 is
  `2ed9e0d03729aed8bb2a319cf933d6dcf694512955a8308f999e76741723aabf`.
  Its blockers, proposed writes, plan hash, and closure fingerprint must not be
  reused as current evidence.

## Finding Responses

### Lifecycle precondition - false terminal WI-5640 row

Newly discovered after v4-008. The current MemBase row is terminal even though
the strict reverse index contains active NO-GO implementation threads. The
existing WI-5441 implementation introduces a canonical `gt backlog update
--reopen-terminal` service, but its approved implementation intentionally
accepts only WI-5441. Direct SQL, an ungoverned service call, or ordinary update
cannot repair WI-5640.

After WI-5441 is independently VERIFIED and finalized, this slice will preserve
its exact behavior and add one data-defined WI-5640 terminal-repair policy. The
policy must require all of the following before any write: explicit owner
approval already supplied by the owner's `Repair forward` directive; this
active project PAUTH; strict lifecycle validity for this v4 thread; this v009
REVISED proposal; its immediate independent GO successor as the controlling
strict state; exact `Work Item: WI-5640` metadata; and a canonical reverse-index
set containing all eight current WI-5640 thread slugs.

The command runs once in `--dry-run` mode and once in apply mode. It appends one
work-item version and one `wi_reopened` event; sets `resolution_status = "open"`
and `stage = "implementing"`; stores the eight current latest bridge paths; and
leaves title, description, priority, project, source links, and every other
field unchanged. A changed thread set, non-GO controlling verdict, invalid
chain, inactive PAUTH, missing owner evidence, or concurrent work-item version
change fails before mutation. No broad or arbitrary terminal-reopen authority
is requested.

### F1 - Ruff format gate

Resolved in the current checkout. The exact six-file lint and format commands
both pass. The implementation report will rerun and quote both commands after
all authorized changes.

### F2 - Registry-atomic migration scope

Accepted. The implementation will compute the 180-locator set only from the
reviewed CSV bytes, resolve the 13 existing members through the canonical
registry resolver, and require exact equality with the reviewed 167-path
missing-set digest. Any row, digest, existence, tracked-state, case-fold,
normalization, resolver, or generation drift stops before mutation.

The 167 missing paths will be added as 167 deterministic `coverage_mode =
"exact"` records in one control-plane transaction. Existing 13 records are
preserved byte-for-byte. No registry record is deleted, renamed, superseded, or
converted to recursive/glob coverage. Both old sources and canonical
destinations remain first-class registry members because the owner requires old
sources to remain available through repeated post-migration verification.

The transaction must atomically update:

1. `config/registry/sot-artifacts.toml`;
2. the packaged registry mirror;
3. the SQLite projection through the registered transaction API; and
4. exact revision/currentness evidence for the new generation.

No raw SQLite statement, direct TOML parser/writer, independent mirror copy, or
partial source/destination admission is permitted. Any fault before commit
must leave every reader seeing the old generation, the new generation, or an
explicit in-progress/recovery error; no reader may observe mixed membership.

Before the 167-record production transaction, the control plane will close its
one known deterministic recovery gap. When and only when the journal proves
canonical-new / packaged-old / projection-old, the canonical digest equals the
reviewed new digest, the packaged/projection digests equal the journal's old
digests, and the serialized journal payload reproduces the reviewed new digest,
`recover_registry` will complete forward: replace the packaged declaration from
that exact payload and commit the projection through `_commit_prepared_generation`.
Every unknown digest combination remains `repair_required`. The fault matrix
must then prove after-prepare recovery yields old and every later durable-phase
recovery yields new, with no raw/manual repair and no mixed reader-visible state.

### F3 - F5 terminal-verification gate

The WI-5648 strict-fixture blocker is resolved, but the policy still encodes the
obsolete 41-failure allowance. This revision removes that allowance and records
the current result without relabeling the four WI-5178 failures as WI-5648.

This slice reopens the false terminal WI-5640 row but does not request terminal
resolution, terminal verification, or an exact-plan child. The v4-008
requirement for a fully green frozen 460-node gate remains in force before any
of those later actions. The four WI-5178 residuals require their own completion
or an explicit owner-reviewed waiver; they are not silently grandfathered by
this proposal.

### F4 - Reproducible migration preflight

After registry admission, the scanner will obtain its file inventory from one
public canonical inventory API backed by the coherent registry snapshot. The
private `_artifact_inventory` import is removed. The public API must enumerate
only registered exact/recursive/glob members, preserve opaque-container
semantics, and report missing registered members without traversing disposable
unregistered trees.

Two fresh `preflight` processes will run sequentially in a quiescent runtime
directory. Each must exit normally, report the same manifest/policy/scanner and
registry-generation bindings, and produce identical plan and closure hashes.
Runtime evidence replacement uses unique temporary files and an atomic replace;
stale `.tmp-*` files are disposable and cannot become authority. A permission or
replace failure is a blocker, never a clean scan.

## Mechanical Implementation Procedure

1. Verify WI-5441 is strict-chain VERIFIED and finalized; acquire a fresh v4
   claim and exact implementation-start packet for only the declared targets.
2. Recompute the reverse WI-5640 bridge index and strict v4 lifecycle. Extend
   only the canonical terminal-reopen policy for the exact reviewed WI-5640
   evidence, run its focused tests, execute the CLI dry-run, then append exactly
   one open/implementing work-item version and one `wi_reopened` event.
3. Add the exact known canonical-new / packaged-old / projection-old recovery
   branch and fault test described above. Rerun the full registry fault matrix;
   no unknown state may be guessed or made readable.
4. Parse the CSV with `csv.DictReader(encoding="utf-8-sig", newline="")`;
   root-confine and NFC/case-fold validate all paths; require the fixed 90-row
   and 33/38/19 invariants.
5. Load one coherent registry snapshot and exact committed receipt. Derive the
   180-path union, 13 resolved set, and 167 missing set; verify the reviewed
   missing-set digest before preparing records.
6. Build deterministic exact records. Missing source IDs are
   `wi5640-source-NNN`; missing destination IDs are
   `wi5640-destination-NNN`, where `NNN` is the fixed CSV row number. Each uses
   `lifecycle = "active"`, `domain = "control_surface"`, Git version/backup
   policy, shared ownership, and a note identifying retained source versus
   canonical destination.
7. Execute one `register_artifacts` / `apply_registry_transaction` operation.
   Verify canonical/packaged byte equality, projection parity, receipt binding,
   record count 312, all 180 resolver hits, and zero stale/missing revisions.
8. Publish a public registered-artifact inventory function from
   `groundtruth_kb.inventory.string_scan`; keep any private compatibility alias
   internal. Change the migration engine to consume only the public API and the
   already-loaded snapshot.
9. Replace the stale 41-node WI-5648 baseline with current evidence while
   preserving the later 460/460 gate and explicit WI-5178 disposition.
10. Run unit/fault-injection tests, registry inspect, the 65-test focused suite,
   the 475-test governance suite, both Ruff gates, and adapter/generator checks.
11. Run two sequential clean-process preflights. Compare status, plan hash,
   closure fingerprint, registry generation, receipt, and all component hashes.
12. File a NEW implementation report for independent verification. Do not run
    Stage B, create an exact-plan child, commit, or delete old sources.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "owner registry-authority and obsolete-source-retention directives, WI-5640 CSV evidence, v4-008 findings, and WI-5441 v4-006 VERIFIED evidence",
  "canonical_authority": "config/registry/sot-artifacts.toml through groundtruth_kb.project.registry_control_plane; the reviewed CSV defines this slice's exact 180 locators",
  "primary_route": "reopen only WI-5640, atomically admit the exact 167 missing locators, publish the registered-artifact inventory API, then run two read-only preflights",
  "before_behavior": "WI-5640 is falsely terminal, 167 manifest locators are unregistered, migration imports a private inventory API, and preflight fails before scanning",
  "after_behavior": "WI-5640 is open and implementing, all 180 locators resolve in one coherent 312-record generation, migration uses the public registered inventory, and two preflights agree",
  "self_descriptive_naming": "wi5640-source-NNN and wi5640-destination-NNN preserve reviewed CSV row identity; registry_control_plane and registered inventory name their authority",
  "obsolete_guidance_disposition": "no consumer guidance is rewritten in this slice; obsolete references remain detected pending a separately reviewed exact-plan child",
  "history_preservation": "bridge, Git, and database audit history plus all 90 sources and 90 destinations remain present; no source is deleted or rewritten",
  "baseline": "90 CSV rows with 33 hooks, 38 rules, and 19 agent-control mappings; 145 registry records; 13 resolved and 167 missing manifest locators",
  "expected_result": "one coherent 312-record generation, 180 of 180 manifest locators resolved, public inventory use, and two identical clean-process preflights",
  "rollback": "abort before transaction or use only journal-proven registry recovery; append-only lifecycle repair remains auditable and no retained file is removed",
  "hard_invariants": [
    "no consumer reference rewrite or Stage B apply",
    "no obsolete-source deletion",
    "no registry-member removal or conversion",
    "no commit, push, release, deployment, dispatcher mutation, or history rewrite"
  ],
  "fail_closed_conditions": [
    "CSV, path-set, registry-generation, receipt, bridge, PAUTH, or work-item-version drift",
    "registry collision, ambiguity, missing member, or mixed generation",
    "unknown recovery digest combination",
    "preflight permission failure or nondeterministic closure evidence"
  ],
  "essential_context_preservation": "registered authority, generated projection parity, retained compatibility sources, immutable audit trails, and explicit WI-5178 residual status remain visible"
}
```

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Requirement Sufficiency

Existing requirements sufficient.

The linked registry authority, mutation-authorization, projection-parity,
bridge-lifecycle, project-authorization, nonimpairment, and mechanical-
enforcement specifications already define the behavior required by this bounded
repair. This proposal adds implementation and verification evidence for those
requirements; it does not introduce a new product or governance requirement.

## Owner Decisions / Input

- The registry is the ultimate SoT for GT-KB artifact membership.
- Every load-bearing artifact must be registered; unregistered artifacts are
  disposable and outside preservation/reference-closure scope.
- Adding a registry member is easy; removing one requires oversight.
- Every mutation of a registered artifact must update registry revision evidence
  automatically.
- The owner's `Repair forward` direction authorizes correction of false
  control-plane state through reviewed, append-only governed mechanisms.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` requires all obsolete sources
  to remain through repeated deterministic verification. Deletion is a separate
  owner-authorized phase.

No new owner decision is requested by this bounded admission proposal.

## Prior Deliberations And Evidence

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`
- `DELIB-202667192`
- `DELIB-202666274`
- `bridge/gtkb-file-move-rename-canonicalization-v4-001.md` through `-008.md`
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-005.md` and
  independent VERIFIED successor
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`

## Specification-Derived Verification Plan

| Requirement | Exact evidence | Required result |
| --- | --- | --- |
| False terminal repair | strict lifecycle/reverse-link probe, CLI dry-run/apply, work-item history/event audit | one new open/implementing version, one event, eight current links, no unrelated field change |
| Manifest integrity | Structured CSV audit plus fixed digest | 90 rows; 33/38/19; no duplicates/no-ops/typos |
| Exact admission set | Resolver audit and LF set digest | 13 existing + 167 missing before; 180/180 registered after |
| Reader-atomic three-store update | Registry transaction/fault-injection tests at every durable phase | readers see old/new or block; known one-replace state completes forward; unknown states stay repair-required |
| Automatic revision evidence | `gt registry inspect --no-census --json` and DB-backed currentness | coherent/current; no missing/stale; exact receipt |
| Canonical inventory API | public API unit tests and private-import ban | no migration import/use of `_artifact_inventory`; unregistered trees excluded |
| F5 correction | exact eight-module command | no former strict-fixture failures; later 460/460 gate preserved |
| Focused migration behavior | three Stage A test modules | all current and new tests pass |
| Determinism | two clean `preflight` processes | identical status, plan hash, closure fingerprint, and component bindings |
| Code quality | exact Ruff check and format commands | exit 0 |
| Retention/nonimpairment | source/destination existence and resolver audit | all 90 old sources and all 90 destinations remain present and registered |

## Acceptance Criteria

1. WI-5441 is independently VERIFIED and its implementation bytes are committed
   before this thread is filed or implemented; any broader commit scope is
   disclosed and excluded from migration authority.
2. The strict classifier continues to return `reopen` for WI-5640; the
   canonical terminal-reopen command appends exactly one nonterminal version
   and event, records all eight current bridge threads, and changes no unrelated
   field. No other work item becomes eligible for this exact repair policy.
3. The exact reviewed CSV and current registry generation derive a unique
   167-path addition set with digest
   `sha256:92baca678bd277f8b0aa3c76576b1bcae48e07d83cefdcc64e58b9aa16ae31b4`.
4. One transaction adds all 167 exact records and no other membership change;
   record count becomes 312 and all 180 manifest locators resolve.
5. Canonical TOML, packaged mirror, SQLite projection, receipt, and revision
   evidence are coherent/current after success. Fault recovery returns old or
   completes new for every known durable phase; readers block throughout, and
   unknown states remain repair-required rather than being guessed.
6. The migration engine uses a public canonical inventory API and never imports
   `_artifact_inventory` or independently parses registry TOML/SQLite.
7. The obsolete 41-failure WI-5648 allowance is removed. Former strict-fixture
   failures are zero; the later 460/460 gate remains explicit.
8. The focused 65-test baseline plus new lifecycle/admission/API/fault tests
   pass; exact
   Ruff lint and format checks pass.
9. Two sequential preflights complete without runtime replacement failure and
   produce identical current hashes and closure fingerprint.
10. Every old source and destination remains present. No consumer reference is
   rewritten and no source is deleted in this slice.
11. No intermediate commit, push, release, deployment, dispatcher mutation,
    raw database mutation, external-system mutation, or history rewrite occurs.

## Risk And Rollback

The primary risks are reopening the wrong terminal row, admitting an unintended
locator, or leaving the three stores on different generations. Exact bridge,
work-item-version, CSV/generation/set bindings and the WI-5441 journaled
transaction make those mechanically testable. The lifecycle repair is
append-only and touches one exact row; any policy/evidence drift blocks it. Any
registry fault blocks readers until registered recovery either proves the old
generation intact or completes the exact journal-bound new generation. Any
unknown post-crash digest combination remains repair-required and unreadable.

Recovery never deletes an old or destination file. It aborts an untouched old
generation or completes the exact journal-bound new generation; it never
silently invents a rollback after declaration replacement. Raw SQLite edits,
manual TOML/mirror restoration, broad Git restore, and destructive cleanup are
forbidden.

## Loyal Opposition Asks

1. Verify the false terminal diagnosis and that the exact WI-5640 reopen policy
   cannot authorize another row or survive bridge/PAUTH/version drift.
2. Verify the 167-path admission derivation and whether exact records are the
   least-ambiguous representation given existing exact coverage.
3. Verify three-store atomicity, public inventory API scope, F5 rebasing, and
   the two-process determinism gate.
4. Return GO only for this lifecycle-repair/registry-admission/preflight slice;
   do not authorize consumer rewrites, Stage B, source deletion, commit, push,
   or release.
