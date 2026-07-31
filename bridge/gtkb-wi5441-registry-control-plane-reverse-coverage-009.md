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

# GT-KB Bridge Implementation Report - WI-5441 Registry Control Plane - 009

bridge_kind: implementation_report
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 009 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-008.md
Approved proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
Recommended commit type: feat:

## Implementation Claim

WI-5441 is implemented for independent verification. The canonical TOML,
packaged mirror, and MemBase projection now form one locked, journaled,
reader-coherent registry generation. Every record has an explicit coverage
mode, registry membership mutations use governed transaction APIs and receipts,
and the named read, migration, commit, release, doctor, reclaim,
decontamination, freshness, inventory, and hook consumers fail closed on mixed,
stale, incomplete, or unregistered authority state.

The reviewed bootstrap committed 54 records: the exact reviewed 50-record
legacy map plus the four WI-5441 implementation artifacts. The final bounded
inspection reports canonical/package/projection parity and current revision
evidence for all 54 records. The exhaustive whole-root census completed and
correctly leaves reverse closure red; it did not silently exclude disposable,
cache, virtual-environment, temporary, or untracked content. WI-5640 therefore
remains paused for the separately reviewed reconciliation required by v007.

WI-5441's false terminal state was repaired through the dedicated governed
reopen service. The work item is now version 6, stage `implementing`, and
resolution status `in_progress`; all five prior bridge links plus v007/v008 are
preserved. A dedicated append-only backlog snapshot was added through
`KnowledgeDB` because the ordinary structural guard correctly refused an
implementing transition until backlog membership existed.

No source commit, push, deletion, move, rename, WI-5640 registration batch, or
WI-5640 migration was performed.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-CROSS-HARNESS-PARITY-001`

## Owner Decisions / Input

- Carry forward the owner's registry rule: registered membership is the
  ultimate SoT; unregistered artifacts are disposable; registered artifacts
  cannot be moved, renamed, or deleted without mechanical authorization; and
  every admitted load-bearing artifact must be registered.
- Carry forward the owner's sequencing: WI-5441 must be independently VERIFIED
  before WI-5640 resumes, and WI-5640's old sources remain in place until
  repeated reference verification supports separate deletion authority.
- Carry forward the owner's worker direction: this Codex session performs Prime
  Builder work; the owner drives the independent interactive Loyal Opposition
  review. No LO sub-agents were created.
- No new owner decision is required by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-006.md` - F8
  overlap/citation NO-GO addressed by v007.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` - preserved overlap
  finding, consolidated by v007/v008.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md` - approved
  implementation proposal and exact verification contract.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-008.md` -
  independent GO authorizing the exact 50 target paths.

## Registry Transaction Evidence

- Bootstrap journal: `SOTTXN-22BD0427D3664729BB260F5328B55283`.
- Record count: 54.
- Declaration/package digest:
  `sha256:393005366742b720435da47e0b8ec47d03df6cd9de8ce577ca773bea8bcfda0f`.
- Projection digest:
  `sha256:bd9d4c4f70cc086f0d6fc2ee15e61aca0d3024123caa920608504d4f53b7f7b3`.
- Receipt digest:
  `sha256:39e1109c3d552c667cea34f5ae731bb16ce89958a9bfac7a9d16dec91f2c6e59`.
- Final registered-test observation revision:
  `SOTREV-AA78224C89AA48C49EE2DAE5D13D74E2`.
- Final `gt registry inspect --no-census --json`: coherent true, current true,
  missing revisions 0, stale revisions 0, record count 54.

## Reverse-Coverage Census

The deterministic whole-root census classified 1,761,624 objects:

| Classification | Count |
| --- | ---: |
| registered member | 56 |
| registered structural ancestor | 27 |
| opaque container | 3 |
| virtual declaration | 10 |
| unregistered | 1,761,087 |
| invalid/unknown | 441 |

The blocking gap list contains 1,761,526 objects after the two named
`vcs_service_state` / `hosted_application_root` boundary nodes are excluded from
the gap list. This is an expected fail-closed census result, not a completeness
claim. It proves the reconciliation workload still exists. In particular, the
live decontamination audit exposes two unregistered worker-loaded files:
`config/agent-control/gtkb-harness-capability-registry.toml` and
`config/agent-control/skill-rename-map.toml`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | 54-record bootstrap receipt; final coherent/current inspection; exhaustive census counts above. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | `test_sot_registry.py` 19 passed; `test_registry_control_plane.py` 17 passed; explicit map/mode, unsafe path, collision, and overlap tests. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Canonical and packaged SHA-256 values are byte-identical; final projection digest and parity inspection pass. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Fault/recovery tests, five commit-boundary nodes, seven observer tests, and five migration refusal classes pass. |
| `GOV-WORK-TREE-HYGIENE-001` | Census completed without cache/temp/venv exclusions; reclaim, inventory, doctor, and decontamination consumers executed. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Commit, release, migration, implementation-start, doctor, hooks, and direct-reader scan executed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live v008 GO claim and exact start packet bound bootstrap and observation receipts; no commit performed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | v007/v008 linkage carried forward unchanged and helper plan resolved all 12 linked specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact named test commands, pass/fail nodes, census counts, digests, and residual ownership are reported below. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Prime authored only REVISED/NEW artifacts; v008 GO remains independently authored. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Census treats immediate application children as the only hosted-application traversal boundary. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bootstrap receipt, revision evidence, WI versions, reopen event, backlog snapshot, and v009 report preserve durable evidence. |
| `ADR-CROSS-HARNESS-PARITY-001` | Claude hook registration, both read-hook mirrors, Codex post-tool adapter wiring, and observer tests pass. |

## Commands And Observed Results

- `python -m py_compile <all 32 changed Python paths>` - pass.
- `python -m json.tool .claude/settings.json` - pass.
- `git diff --no-index -- .claude/hooks/sot-read-discipline.py config/hooks/gtkb-sot-read-discipline.py` - byte-identical, exit 0.
- `ruff check <all 32 changed Python paths> --output-format concise` - all checks passed.
- `ruff format --check <all 32 changed Python paths>` - 32 already formatted.
- `git diff --check` - pass; only line-ending conversion warnings.
- Core pre-bootstrap run (`test_registry_control_plane.py`,
  `test_registry_observation_hook.py`, and
  `test_gtkb_file_reference_migration.py`) - 76 passed.
- Post-bootstrap freshness/read-hook/controlled-path/decontamination/doctor run
  - 83 passed, 1 expected fail-closed live-root decontamination node exposing
  the two unregistered worker-loaded files listed above.
- Exact commit, release, and terminal-reopen nodes - 14 passed.
- Exact implementation-start registry nodes - 5 passed.
- Full `test_implementation_start_gate.py` - 206 passed, 4 failed. The four
  residual nodes are:
  `test_work_intent_acquire_denial_creates_no_claim`,
  `test_work_intent_extension_denial_leaves_claim_unchanged`,
  `test_work_intent_renew_denial_leaves_go_claim_unchanged`, and
  `test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`.
  All four depend on the out-of-scope WI-5178
  `scripts/bridge_work_intent_registry.py` surface. The proposal estimated five;
  the exact current baseline is four, and no production workaround was added.
- Broad registry/mirror/reclaim/inventory/commit/release run - 239 passed,
  1 skipped, 2 failed. The WI-5441 repeatable-bootstrap failure was repaired and
  the complete control-plane module then passed 17/17. The remaining failure is
  the pre-disclosed unrelated activity-profile packaged-mirror drift at
  `test_context_manifest.py::test_packaged_v1_snapshot_matches_source_checkout_registry_inputs`.
- Final direct-reader scan found no named enforcement consumer reading raw
  `current_sot_artifacts` outside the canonical schema/reader. Remaining
  `load_toml` calls in `hygiene/auto_resolve.py`, `hygiene/strays.py`, and
  `project/sot_audit.py` use the public barrier API and are outside v008's exact
  targets; canonical module internals and path constants remain expected.

## Shared-File Hunk Inventory

`platform_tests/scripts/test_implementation_start_gate.py` is the only file
shared with the unresolved WI-5279 thread. WI-5279 v2 remains latest NO-GO and
was unclaimed at pre-mutation check. WI-5441 owns these test-only hunk starts in
the current diff: old/new lines 14/15, 22/28, 42/49, 43/51, 47/56, 81/91,
82/93, 95/110, 97/114, 121/138, 133/147, 135/167, 309/339, 583/682,
717/833, 866/982, 890/1009, 1225/1344, 1233/1352, and 2272/2394.

The hunks repair strict bridge fixture metadata and stale messages absorbed from
WI-5279, add the five registry integration tests, and update two assertions to
the new registry-authoritative classifications. No production hunk from
WI-5279 was changed; `scripts/bridge_work_intent_registry.py` remains untouched.

## Files Changed

- `.claude/hooks/sot-read-discipline.py`
- `.claude/settings.json`
- `.codex/gtkb-hooks/run_py_no_window.py`
- `config/hooks/gtkb-sot-read-discipline.py`
- `config/registry/sot-artifacts.toml`
- `groundtruth.db` (projection, journal, revisions, WI/event/backlog evidence)
- `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py`
- `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` (new)
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`
- `groundtruth-kb/tests/test_backlog_update_cli.py`
- `groundtruth-kb/tests/test_db.py`
- `groundtruth-kb/tests/test_hygiene_reclaim.py`
- `groundtruth-kb/tests/test_inventory_string_scan.py`
- `groundtruth-kb/tests/test_registry_control_plane.py` (new)
- `groundtruth-kb/tests/test_sot_registry.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_sot_registry_completeness.py`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_modernization_artifact_decontamination.py`
- `platform_tests/scripts/test_registry_observation_hook.py` (new)
- `platform_tests/scripts/test_release_candidate_gate.py`
- `scripts/check_protected_commit_authorization.py`
- `scripts/controlled_artifact_paths.py`
- `scripts/evidence_freshness_boundary.py`
- `scripts/gtkb_file_reference_migration.py`
- `scripts/implementation_start_gate.py`
- `scripts/registry_observation_hook.py` (new)
- `scripts/release_candidate_gate.py`

## Acceptance Criteria Status

- [x] Explicit reviewed coverage mode exists for every canonical record.
- [x] Canonical TOML, packaged mirror, and MemBase projection change under one
  journaled transaction with deterministic recovery and receipt evidence.
- [x] Public register/amend/recover/inspect/validate APIs exist; public sync is
  diagnostic-only; direct observe without a capability is denied.
- [x] Named enforcement consumers use one coherent snapshot and fail closed.
- [x] Registered mutation observation is single-use and bound to path, preimage,
  session, tool event, bridge, start packet, PAUTH decision, and result.
- [x] Commit, migration, and release boundaries reject stale, incomplete,
  unregistered, identity-changing, or reverse-open state as applicable.
- [x] WI-5441 terminal lifecycle is repaired without rewriting history.
- [x] Full-root reverse census is deterministic and reports every gap.
- [ ] Reverse coverage is closed. This was explicitly deferred by v007 to a
  subsequent reviewed reconciliation; 1,761,526 blocking gaps remain.
- [ ] WI-5640 may resume. It remains paused until reconciliation reaches zero
  unknown and zero unregistered load-bearing objects and WI-5441 is VERIFIED.

## Risk And Rollback

- Reverse coverage is intentionally fail-closed and very large. Release and
  WI-5640 migration must remain blocked; do not reinterpret the census as a
  request to register or preserve every disposable object.
- Full census output can be hundreds of megabytes because every gap is explicit.
  Bounded `inspect --no-census` remains the routine coherence/currentness path;
  the full census is the deliberate reconciliation input.
- The desktop Codex execution surface used here did not automatically run the
  new pre/post observer around a late registered test edit. That edit was
  restored to its recorded preimage, reapplied under an exact minted capability,
  and consumed as revision `SOTREV-AA78224C89AA48C49EE2DAE5D13D74E2`.
- Rollback before commit is the exact working-tree diff plus transaction
  recovery API. Bridge versions and MemBase audit history are append-only and
  must not be rewritten. No rollback or cleanup should occur before LO review.

## Loyal Opposition Asks

1. Verify journal/receipt coherence, final 54-record currentness, observer
   binding, exact consumer behavior, and WI version/event history.
2. Treat the four WI-5178 failures, one activity-profile mirror failure, and
   fail-closed reverse/decontamination results according to the explicit scope
   distinctions above; do not accept a broad green summary in their place.
3. Return VERIFIED only if every linked specification and v008 condition is
   satisfied. Otherwise return NO-GO with exact findings.

No commit is authorized until an independent VERIFIED verdict is filed.
