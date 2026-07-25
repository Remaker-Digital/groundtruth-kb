NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata


# Stage A Implementation Report: Registry and F5 gates remain fail-closed

bridge_kind: implementation_report
Document: gtkb-file-move-rename-canonicalization-v4
Version: 007
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-006.md
Approved proposal: bridge/gtkb-file-move-rename-canonicalization-v4-005.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["scripts/gtkb_file_reference_migration.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_cursor_skill_adapters.py", "config/file-reference-migration/wi5640.toml", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_generate_rule_compatibility_projections.py", "platform_tests/scripts/test_generate_cursor_skill_adapters.py", "platform_tests/fixtures/file_reference_migration/**", ".gtkb-state/file-reference-migration/wi5640/**"]

implementation_scope: source | test | configuration | runtime_state | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Implementation Claim

The bounded Stage A pass remains intentionally fail-closed. It produced a
registry-scoped deterministic observation and focused migration tests, but it
did not produce an authorized migration apply candidate. Two independently
blocking facts now control the program:

1. The owner confirmed that `config/registry/sot-artifacts.toml` is the ultimate
   GT-KB membership authority. Its MemBase `sot_artifacts` table is a projection
   of that same registry, not a second authority. Every load-bearing artifact
   must be registered; unregistered artifacts are sweep-disposable. A
   registered move or rename must be mechanically authorized and update the
   registry atomically. Registry removal requires oversight.
2. A clean re-baseline at research HEAD `c0c4c40e4` reproduced the exact frozen
   F5 baseline: 41 failures and 419 passes across the 460-node governance suite.
   WI-5659 repaired governed VERIFIED commit finalization, but it did not repair
   these strict-chain fixtures.

The current GO does not authorize `config/registry/sot-artifacts.toml`,
`groundtruth.db`, the 90 destination paths, or live consumers. It therefore
cannot authorize the owner's required atomic destination-registration
transaction. General registry completeness and enforcement belong to P0
`WI-5441` in a parallel Prime Builder session. WI-5640 will not edit or seed the
registry ahead of that owner.

No migration `apply`, registry mutation, MemBase sync, live consumer rewrite,
database mutation, old-source deletion, Git staging, commit, push, release,
deployment, or dispatcher mutation occurred in this pass. Loyal Opposition
should return a finding-specific `NO-GO`; this report is not a request for
`VERIFIED`.

## First-Line Role Eligibility Check

PASS. This is a Prime Builder-authored `NEW` implementation report responding
to the latest independent Loyal Opposition `GO` at v4-006. Prime Builder is
authorized to file `NEW` implementation reports. No Loyal Opposition verdict
token is authored here.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`

## Owner Decisions / Input

- Owner directive, 2026-07-22/24: the SoT artifact registry is the ultimate
  membership authority. New load-bearing artifacts must be registered
  atomically; registered delete/move/rename operations require mechanical
  authorization; path transitions update the registry automatically; removals
  require oversight; unregistered artifacts are disposable.
- Owner sequencing, 2026-07-24: WI-5441 owns general registry seeding,
  completeness, and fail-closed enforcement. WI-5640 must stand down on general
  registry edits and retain only its own atomic 90-destination registration and
  path-transition step.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` remains controlling for this
  migration: all 90 obsolete sources stay in place through apply and repeated
  verification; deletion requires a later separately authorized operation.

No new owner decision is required for Loyal Opposition review of this report.

## Prior Deliberations And Dependencies

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - old-source retention and separately authorized deletion.
- `bridge/gtkb-file-move-rename-canonicalization-v4-005.md` - approved bounded Stage A correction proposal.
- `bridge/gtkb-file-move-rename-canonicalization-v4-006.md` - independent GO limited to nine Stage A paths.
- `WI-5441` - P0 owner of registry completeness, canonical-reader enforcement, and fail-closed registered path mutation.
- `WI-5659`; commits `f0b27999a` and `c0c4c40e4` - repaired governed VERIFIED commit finalization and audit-scratch scope.
- `WI-5648` - the separately owned 41-node strict-chain/governance dependency remains open in this exact suite.

## Registry Authority And Sequencing Evidence

The canonical authority is one registry:

- Human-edit source: `config/registry/sot-artifacts.toml`.
- Canonical API: `groundtruth_kb.project.sot_registry.load_toml` and
  `groundtruth_kb.project.sot_registry.load_projection`.
- Derived view: MemBase `sot_artifacts`, regenerated through
  `gt registry sync` under `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`.

The Stage A implementation currently imports the private
`groundtruth_kb.inventory.string_scan._artifact_inventory` helper. That is not
the canonical registry API and must be replaced in a separately authorized
correction. The migration must not re-parse the TOML itself.

The last registry-scoped preflight observed 13,512 registered files and 13,548
registered files/directories with zero inventory read errors. Its observation
hash was
`sha256:6cb360e78ff33c24823acad7a0f9bb2694b56d5ff78a56006219844f7afa43dc`.
It correctly blocked because all 90 proposed destination paths were
unregistered.

The migration preflight remained blocked with:

- 377 total blockers.
- 90 `MANIFEST_DESTINATION_UNREGISTERED` blockers.
- 135 `UNRESOLVED_LIVE_REFERENCE` blockers.
- 90 downstream `MAPPING_FILE_NOT_SCANNED` blockers.
- 43 `ALIAS_OCCURRENCE_NOT_MATERIALIZED` blockers.
- 10 `ALIAS_CANDIDATE_UNDISPOSITIONED` blockers.
- 3 `GENERATOR_CHECK_FAILED` and 2 `GENERATOR_CHECK_BLOCKED` blockers.
- 2 `PHYSICAL_ALIAS_SOURCE_MISSING` blockers.
- 1 `GENERATED_OUTPUT_NOT_MATERIALIZED` blocker.
- 1 `LIVE_SQLITE_REFERENCE_REQUIRES_DOMAIN_API` blocker.

Plan hash:
`sha256:a0109c89fa500d3b82c99dfe7989b5824777dcc08a420e80c6658fe6d7d563c3`.
Closure fingerprint:
`sha256:0f7745b1d6f012b7401b5755778b40d12d682a3b19d99d1233d05a159e064745`.

The earlier physical full-root approach enumerated more than 1.5 million
entries and roughly 245.6 GB, overwhelmingly runtime/non-SoT material. It was
discarded after the owner clarified registry authority. Unregistered physical
artifacts do not enter migration closure or preservation requirements.

## WI-5659 / F5 Re-Baseline

Prime Builder verified that both WI-5659 commits are ancestors of the current
research HEAD:

- `f0b27999a2a39d8465fbb7e9fb5c3dda07d635eb`
- `c0c4c40e4347e4462c3eaf7b4f3b8ac6881b920a`

Because the shared checkout contains concurrent uncommitted work, the exact
`c0c4c40e4` tree was checked out in an isolated runtime clone at
`.gtkb-state/file-reference-migration/wi5640/rebaseline-c0c4c40e4-20260723`.
The canonical eight-module governance command collected exactly 460 nodes and
completed in 93.55 seconds:

```powershell
python -m pytest groundtruth-kb/tests/test_governance_mutation.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_project_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short
```

Observed result: `41 failed, 419 passed, 1 warning in 93.55s`.

All 41 failures remain in
`platform_tests/scripts/test_implementation_start_gate.py`; their sorted LF
node-list hash is exactly
`sha256:31cd76c57a3d6070965aebda83e31ea66a4a0d2a0e9454ffd36f51db6ced3338`.
The repeated signature is missing required `Version` metadata in synthetic
bridge fixtures. This proves the WI-5659 finalizer repair is real but does not
clear the separate F5 fixture dependency.

The dirty integrated checkout collected 462 nodes because concurrent
uncommitted tests add two nodes. Its default run timed out while repeatedly
enumerating the very large dirty worktree. That diagnostic is not substituted
for the clean research-HEAD result above.

## Focused Stage A Verification

```powershell
python -m ruff check scripts/gtkb_file_reference_migration.py platform_tests/scripts/test_gtkb_file_reference_migration.py
python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py -q --tb=short
```

- Ruff: `All checks passed!`.
- Focused migration suite: `52 passed in 10.75s`.
- These focused passes validate the current fail-closed registry observation;
  they do not authorize apply or override the registry and F5 blockers.

## Files In The Approved Stage A Scope

The shared checkout currently contains untracked Stage A candidates at:

- `scripts/gtkb_file_reference_migration.py`
- `scripts/generate_rule_compatibility_projections.py`
- `scripts/generate_cursor_skill_adapters.py`
- `config/file-reference-migration/wi5640.toml`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_generate_rule_compatibility_projections.py`
- `platform_tests/scripts/test_generate_cursor_skill_adapters.py`
- `platform_tests/fixtures/file_reference_migration/**`

Runtime evidence is under `.gtkb-state/file-reference-migration/wi5640/**`.
No claim is made that these candidates are terminal or commit-ready.

## Specification-Derived Verification

| Governing surface | Executed evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Canonical registry identity and API inspected; registry-scoped migration preflight run | FAIL-CLOSED: all 90 destinations require atomic registration |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | TOML authority and MemBase projection relationship verified | PASS as architecture; no sync or mutation attempted |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Current Stage A reader path inspected | NO-GO correction: consume canonical API, do not use private inventory helper |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Clean research-HEAD eight-module governance suite | FAIL: 41 historical F5 nodes remain |
| Cross-harness and bridge authority specs | Exact v4 chain, nine-path GO, and no-apply boundary inspected | PASS for fail-closed reporting only |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ruff and 52-node focused suite executed; full governance suite executed | Evidence complete for this NO-GO request; terminal verification prohibited |

## Acceptance Status

- [x] No live migration apply or old-source deletion occurred.
- [x] Registry authority is treated as the only GT-KB membership source.
- [x] Unregistered physical artifacts are excluded from correctness closure.
- [x] General registry seeding and enforcement are left to WI-5441.
- [x] The 90 destination-registration step remains assigned to WI-5640.
- [x] Clean research HEAD reproduces the exact historical F5 hash.
- [ ] WI-5441 has not yet delivered a verified-complete registry baseline.
- [ ] The migration does not yet consume the canonical registry API.
- [ ] The 90 destinations are not atomically registered by the plan.
- [ ] The MemBase registry projection is not included in the transaction.
- [ ] F5 has not reached 460/460.
- [ ] The remaining migration blockers are not zero.
- [ ] No exact Stage B plan is authorized.

## Risk And Rollback

No live migration transaction occurred, so there is no consumer rollback to
perform. Stage A candidates and runtime evidence remain uncommitted. The
isolated research-HEAD clone is disposable runtime evidence and does not alter
the main repository index.

The principal risk is false progress: treating WI-5659 as clearing F5, or
registering destinations separately from their creation/path transition, would
violate the observed evidence and the owner's atomicity rule. Stage B remains
paused.

## Loyal Opposition Request

1. Return `NO-GO`, not `VERIFIED`, because the current GO cannot authorize the
   registry transaction and the exact F5 suite still fails 41 nodes.
2. Require a revised proposal only after WI-5441 supplies a verified-complete
   registry baseline and fail-closed registered-path enforcement.
3. Require the revised WI-5640 scope to include the exact atomic transaction:
   90 destination creations/path transitions, corresponding registry
   additions or `storage_path` updates in
   `config/registry/sot-artifacts.toml`, canonical API consumption, derived
   `gt registry sync`/MemBase projection effects, exact consumer rewrites, and
   transaction/fault-injection tests. General registry seeding remains excluded.
4. Preserve all 90 old sources. Their deletion remains a later, separately
   authorized operation after repeated clean verification.
5. Preserve the 460/460 governance requirement; WI-5659 must be credited for
   finalizer repair without being misreported as a repair of the 41 fixtures.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
