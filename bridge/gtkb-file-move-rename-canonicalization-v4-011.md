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


bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v4
Version: 011
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-010.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640
target_paths: ["scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "groundtruth.db", ".gtkb-state/file-reference-migration/wi5640/**"]
kb_mutation_in_scope: true

# WI-5640 v4 Lifecycle Repair And Registry Admission - Executability Correction

## Revision Trigger

The v4-010 GO was verified live and an exact implementation-start packet was
successfully minted. Before any protected source edit, Prime Builder inspected
the terminal-reopen call chain and found a second enforcement layer outside the
declared target set.

`groundtruth_kb.cli_backlog_update` delegates the write to
`KnowledgeDB.reopen_terminal_work_item`. The latter independently requires the
WI-5441 v007 and v008 bridge paths at `groundtruth-kb/src/groundtruth_kb/db.py`
lines 5028-5033. A WI-5640 request carrying the approved exact eight-thread
reverse index therefore fails inside the database service even after the CLI
policy accepts it. Adding the WI-5441 paths to the WI-5640 stored link set would
violate v4-009's exact-set requirement and would record false evidence.

`db.py` was not declared by v4-009. v4-010 condition 4 says any required
spillover stops implementation and requires a revision. Prime Builder released
the unused implementation claim without editing protected source. The current
packet is inert once this REVISED successor becomes current because the latest
bridge state is no longer GO.

## Scope Correction

All v4-009 implementation details and all v4-010 conditions remain in force.
This revision adds exactly two target paths:

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/tests/test_db.py`

The database primitive will accept an explicit, already-live-validated terminal
reopen policy binding from the canonical CLI service. It will continue to repeat
the structural authorization floor before one atomic append:

- owner approval is required;
- bridge evidence must have been validated by the caller;
- the reason must identify the work item, owner-approved terminal repair, and an
  active PAUTH;
- resolution status and stage must be nonterminal;
- related bridge evidence must be a non-empty JSON string array;
- the caller must provide a non-empty required path set; and
- the supplied paths must satisfy the requested subset or exact-set policy.

The CLI remains the authority for PAUTH lookup, strict lifecycle resolution,
Work Item metadata, controlling verdict, and reverse-index discovery. It passes
the existing WI-5441 two-path subset policy unchanged. It passes WI-5640's eight
current latest paths as an exact-set policy. The DB primitive does not infer a
work item or widen eligibility.

## GO Condition Carry-Forward

### F1 - `groundtruth.db` is evidence-only

`groundtruth.db` remains an authorized runtime mutation target for the one
append-only lifecycle repair and registry projection. The implementation report
will cite its digests, journal IDs, receipts, event evidence, and read-only
reproduction commands by reference. It will not list `groundtruth.db` under
`Files Changed`, and no VERIFIED-finalizer `--include` argument may name it.

### F2 - WI-5441 behavior remains provably unchanged

Regression coverage will execute the existing WI-5441 happy path, dry run, and
incomplete-request cases. New tests will prove its exact PAUTH, v007/v008 strict
evidence, controlling v008 GO, metadata checks, and subset semantics still bind.
Additional negative tests will prove an unrelated work item is rejected and the
database primitive cannot be invoked without an explicit required path policy.

## Mechanical Implementation Procedure

1. After independent GO, acquire a fresh claim and implementation-start packet
   for exactly the revised target set.
2. Replace the single-WI CLI constants with a data-defined policy table for only
   WI-5441 and WI-5640. Preserve all WI-5441 values and behavior.
3. Extend the DB primitive to require explicit validated path policy input,
   preserving its atomic version/event append and all existing structural checks.
4. Recompute WI-5640's canonical reverse index and strict v4 lifecycle. Require
   v009 REVISED, its immediate independent GO successor as controlling state,
   exact `Work Item: WI-5640` metadata, the active project PAUTH, and exact
   equality with all eight current latest bridge paths.
5. Run the CLI once in dry-run mode and once in apply mode. Append one open / 
   implementing work-item version and one `wi_reopened` event with no unrelated
   field change.
6. Add only the journal-proven canonical-new / packaged-old / projection-old
   registry forward-completion branch. Unknown digest combinations remain
   `repair_required`.
7. Parse the reviewed CSV structurally, derive the 180-locator union, require the
   reviewed 13/167 partition and missing-set digest, and build deterministic exact
   records.
8. Execute one canonical `gt registry register --batch-file` transaction. Verify
   canonical/packaged byte equality, projection parity, receipt binding, record
   count 312, all 180 resolver hits, and zero stale/missing revisions.
9. Publish `registered_artifact_inventory` from
   `groundtruth_kb.inventory.string_scan`; retain any private alias only for
   compatibility. Make the migration engine consume the public API and its
   already-loaded coherent snapshot.
10. Remove the obsolete 41-failure WI-5648 allowance and record the current four
    separately owned WI-5178 failures without granting a Stage B waiver.
11. Run the approved unit, fault, governance, Ruff, adapter, and generator gates.
12. Run two sequential clean-process read-only preflights. They must bind the same
    manifest, policy, scanner, registry generation, receipt, plan hash, and closure
    fingerprint.
13. File a NEW implementation report. Do not run Stage B, create an exact-plan
    child, commit, delete old sources, push, release, deploy, mutate dispatcher
    state, or rewrite history.

## Specification-Derived Verification Plan

| Requirement | Exact evidence | Required result |
| --- | --- | --- |
| Database-layer executability | `test_db.py` direct primitive tests | explicit path policy required; subset/exact semantics enforced atomically |
| WI-5441 non-regression | existing and expanded `test_backlog_update_cli.py` cases | original PAUTH, v007/v008, metadata, GO, and mutation behavior unchanged |
| WI-5640 false-terminal repair | CLI dry-run/apply plus history/event audit | one open/implementing version, one event, exact eight links, no other field drift |
| Registry recovery | fault matrix plus tampered/unknown-state tests | after-prepare yields old; every later reviewed durable phase yields new; unknown stays blocked |
| Exact registry admission | structured CSV and resolver audit | 90 rows, 33/38/19, 13 existing plus 167 admitted, 180/180 resolved |
| Registry generation integrity | `gt registry inspect --no-census --json` | 312 records, coherent/current, no stale/missing revision, exact receipt |
| Public inventory authority | inventory and migration tests | public API only, opaque boundaries preserved, missing registered members reported |
| F5 evidence correction | exact eight-module governance suite | stale WI-5648 allowance absent; WI-5178 residuals explicit; no Stage B waiver |
| Reproducible preflight | two clean processes | identical hashes, generation, receipt, status, and zero unauthorized writes |
| Source retention | manifest existence and byte audit | all 90 old sources and 90 destinations remain |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "v4-009 approved proposal, v4-010 GO conditions, and pre-mutation inspection of the live DB enforcement layer",
  "canonical_authority": "config/registry/sot-artifacts.toml through groundtruth_kb.project.registry_control_plane; gt backlog update through its DB primitive",
  "primary_route": "reopen only WI-5640 through two-layer policy validation, atomically admit exactly 167 locators, publish the registered inventory API, then run two read-only preflights",
  "before_behavior": "the approved CLI repair is rejected by a DB primitive hard-coded to WI-5441 evidence",
  "after_behavior": "the DB primitive enforces an explicit caller-bound subset or exact path policy while the CLI owns live governance evidence",
  "self_descriptive_naming": "terminal reopen policy, required bridge paths, and exact related paths name the enforcement contract",
  "obsolete_guidance_disposition": "no consumer guidance or obsolete source is rewritten in this slice",
  "history_preservation": "bridge, Git, MemBase history, all 90 sources, and all 90 destinations remain present",
  "baseline": "v4-010 GO with 13 declared path globs and a DB-layer hard-coded WI-5441 path check outside scope",
  "expected_result": "one executable two-layer WI-5640 reopen path plus the unchanged registry-admission and preflight results",
  "rollback": "abort before the append or registry transaction; use only journal-proven registry recovery; no retained file is removed",
  "hard_invariants": [
    "no direct SQL or bypass of the DB primitive",
    "no consumer reference rewrite or Stage B apply",
    "no obsolete-source deletion",
    "no registry-member removal or conversion",
    "no commit, push, release, deployment, dispatcher mutation, or history rewrite"
  ],
  "fail_closed_conditions": [
    "required target spillover",
    "bridge, PAUTH, reverse-index, work-item-version, CSV, digest, generation, or receipt drift",
    "unknown registry recovery combination",
    "preflight nondeterminism or permission failure"
  ],
  "essential_context_preservation": "registered authority, projection parity, retained sources, immutable audit trails, WI-5441 bindings, and WI-5178 residual status remain visible"
}
```

## Applicability Preflight

- packet_hash: `sha256:8ca84fafd2fe3965aeb104814a96e1855e62561287214481983a69df2dd5ad0b`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- content_source: `pending_content`
- content_file: `.gtkb-state/propose-drafts/gtkb-file-move-rename-canonicalization-v4-011.md`
- preflight_passed: `true`
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-file-move-rename-canonicalization-v4`
- Operative file: `.gtkb-state/propose-drafts/gtkb-file-move-rename-canonicalization-v4-011.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory mode observed exit: 0

The three must-apply clauses were
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

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

The linked lifecycle, registry, project-authorization, nonimpairment, and
mechanical-enforcement specifications already require the corrected two-layer
behavior. This revision adds only the missing executable target and tests.

## Owner Decisions / Input

- The owner's `Repair forward` direction authorizes the reviewed append-only
  correction of false control-plane state.
- The registry is the ultimate SoT for GT-KB artifact membership.
- All obsolete sources remain through repeated deterministic verification under
  `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

No new owner decision is requested.

## Prior Deliberations And Evidence

- `bridge/gtkb-file-move-rename-canonicalization-v4-009.md`
- `bridge/gtkb-file-move-rename-canonicalization-v4-010.md`
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`

## Risk And Rollback

The principal risk is accidentally weakening the database primitive while
generalizing its hard-coded WI-5441 paths. The explicit non-empty required path
contract, exact/subset policy flag, direct primitive tests, and unchanged CLI
live-validation responsibilities prevent that widening. No source mutation,
MemBase append, or registry transaction occurs before an independent GO on this
revision and a fresh exact implementation-start packet.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
