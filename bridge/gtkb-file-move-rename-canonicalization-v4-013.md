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
Version: 013
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-012.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640
target_paths: ["scripts/gtkb_file_reference_migration.py", "config/file-reference-migration/wi5640.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "groundtruth.db", ".gtkb-state/file-reference-migration/wi5640/**"]
input_authority_paths: ["gtkb-file-move-and-rename-list.csv", "config/file-reference-migration/wi5640.toml"]
kb_mutation_in_scope: true

# WI-5640 v4 Registry Membership Closure

## Revision Trigger

Prime Builder implemented and tested the authorized lifecycle-repair and Stage A
support changes under v4-012, then stopped before the registry transaction when a
deterministic registry-membership audit found one load-bearing tracked input that
the approved admission count omitted:

- `config/file-reference-migration/wi5640.toml` is loaded by
  `scripts/gtkb_file_reference_migration.py` through `DEFAULT_POLICY` for
  analyze, preflight, recover, and plan generation.
- `git ls-files --error-unmatch` confirms the policy is tracked.
- The canonical registry resolver returns no record for the policy.
- The same resolver confirms that every other tracked source, configuration, and
  test path changed under v4-012 is already registered.

The owner has established that the registry is the ultimate SoT for artifact
membership and that failure to register a new load-bearing artifact is a
catastrophic failure. Leaving this policy unregistered is therefore forbidden.
The v4-012 GO, however, authorizes exactly 167 admissions and a final record count
of 312. Adding a 168th record under that GO would exceed its scope ceiling.

No registry declaration, packaged mirror, registry projection, consumer
reference, obsolete source, or migration destination was mutated. The first
governed publication attempt then failed closed because the authorized edits had
made ten registered source/test revisions stale. Their exact postimages were
parked under `.gtkb-state/file-reference-migration/wi5640/`, and the live paths
were restored byte-for-byte to their last registry-observed digests. Registry
currentness returned to `true` with no stale or missing revision before this
publication retry. This REVISED successor makes the prior implementation-start
packet inert and requests the minimum membership correction.

## Implementation State Disclosure

The following authorized work already occurred before the stop:

1. WI-5640 was reopened once through the governed CLI at work-item version 3.
   It is `open` / `implementing`, has the exact eight canonical related bridge
   paths, and has one new `wi_reopened` event. Continuation must verify this state
   and MUST NOT append a second reopen version or event.
2. The exact terminal-reopen DB/CLI and test postimages are durably parked with
   their verified digests. Before parking, the focused lifecycle suite passed 145
   tests.
3. The exact registry recovery, public inventory, migration, F5, and test
   postimages are durably parked with their verified digests. Before parking, the
   focused registry and inventory suites passed 26 and 9 tests.
4. The ten registered live source/test paths were restored to their prior
   registry-observed bytes solely to recover bridge publication. Continuation
   must reapply the parked postimages through one exact, capability-observed
   mutation before additional implementation or verification.
5. No registry admission transaction has run. Canonical and packaged registry
   declarations remain at 145 records.
6. `groundtruth.db` remains runtime evidence only and is excluded from Files
   Changed and every finalizer include list.

## Exact Scope Correction

The 15 declared `target_paths` are unchanged from v4-011/v4-012. No new source
or configuration target is requested. The correction is only to the exact
membership set written through the already-authorized registry transaction:

- Preserve the reviewed 167 manifest-locator records exactly as specified by
  v4-009. Their sorted LF path-set digest remains
  `sha256:92baca678bd277f8b0aa3c76576b1bcae48e07d83cefdcc64e58b9aa16ae31b4`.
- Add exactly one separately bound declaration for the load-bearing policy.
- Execute one 168-record `gt registry register --batch-file` transaction.
- Require the final coherent/current registry generation to contain 313 records.
- Require all 180 manifest locators and the policy locator to resolve exactly.

The singleton declaration is:

```json
{
  "id": "wi5640-config-file-reference-migration-wi5640-toml",
  "domain": "control_surface",
  "lifecycle": "active",
  "storage_path": "config/file-reference-migration/wi5640.toml",
  "coverage_mode": "exact",
  "authority_spec_id": "GOV-PLATFORM-SOT-REGISTRY-001",
  "mutation_api": "Governed bridge-authorized source edit",
  "versioning_policy": "git_tracked",
  "backup_policy": "git_tracked",
  "restore_action": "git_restore",
  "health_check_function": "",
  "owner_role": "shared",
  "depends_on": [],
  "forbidden_substitutes": [],
  "notes": "WI-5640 load-bearing deterministic migration policy; exact registration required because DEFAULT_POLICY loads this file for analyze, preflight, recover, and plan generation."
}
```

The LF-terminated, sorted-key, compact JSON encoding of this declaration has
SHA-256
`6274a9af4ded39d66445f30bb0ebbbebd32a700fc03ef4db3e6a4fddc645521b`.
The batch builder must independently reproduce both the reviewed 167-path digest
and this singleton declaration digest before requesting a mutation capability.

## Conditions Carried Forward

All v4-009 implementation details and all v4-010/v4-012 GO conditions remain in
force except the mechanically corrected admission count and final record count.

1. The implementation report must disclose that the DB primitive now validates
   authorization shape while terminal-reopen subject authorization is supplied
   by the governed caller. It must prove `cli_backlog_update.py` remains the sole
   production caller and include the empty-policy negative test.
2. `groundtruth.db` is by-reference evidence only. It may not appear under Files
   Changed or in any VERIFIED-finalizer `--include` argument.
3. WI-5441 reopen behavior remains unchanged, including its PAUTH, v007/v008
   strict evidence, controlling v008 GO, metadata checks, and subset semantics.
4. The scope ceiling remains lifecycle repair, exact registry admission, public
   inventory API, one journal-proven recovery branch, and two read-only
   preflights only.
5. No consumer reference rewrite, Stage B apply, obsolete-source deletion,
   registry-member removal or conversion, terminal resolution or verification,
   exact-plan child, commit, push, release, deployment, dispatcher mutation, raw
   SQL, or history rewrite is authorized.
6. Any further target or membership spillover stops implementation and requires
   another revision.

## Mechanical Continuation Procedure

1. After independent GO, acquire a fresh claim and implementation-start packet
   for the unchanged 15 target paths.
2. Verify the existing WI-5640 version-3 open/implementing row and sole
   `wi_reopened` event. Do not invoke the reopen apply path again.
3. Verify every parked postimage against its recorded digest, mint one exact
   observation capability under the fresh packet, atomically reapply the ten
   postimages, consume the capability, and require registry currentness to remain
   green. Any preimage, postimage, packet, PAUTH, or target drift stops.
4. Rerun the focused lifecycle, registry recovery, inventory, migration, Ruff,
   adapter, generator, and exact governance suites required by v4-009/v4-012.
5. Parse the reviewed CSV structurally and derive the unchanged 180-locator
   union, 13 existing manifest members, and 167 missing manifest members.
6. Build the reviewed 167 exact records plus the exact singleton policy record.
   Require a unique 168-record batch with no ID, path, normalization, case-fold,
   resolver, or current-generation collision.
7. Execute one canonical `gt registry register --batch-file` transaction through
   the WI-5441 control plane. Do not use direct TOML, mirror, or SQLite writes.
8. Verify canonical/packaged byte equality, projection parity, receipt binding,
   record count 313, resolver hits for all 180 manifest locators plus the policy,
   and zero stale or missing revisions.
9. Run two sequential clean-process read-only preflights. Require identical
   manifest, policy, scanner, registry generation, receipt, plan hash, and
   closure fingerprint bindings.
10. File a NEW implementation report. Do not run Stage B or any excluded action.

## Specification-Derived Verification Plan

| Requirement | Exact evidence | Required result |
| --- | --- | --- |
| Load-bearing membership completeness | canonical resolver audit over every tracked implementation input | the policy was the sole missing input before admission; zero missing inputs after |
| Exact manifest admission | structured CSV, path-set digest, generated batch audit | unchanged 13 existing plus 167 admitted; 180/180 manifest locators resolve |
| Exact singleton admission | canonical JSON digest and resolver lookup | exactly one policy record with digest `6274a9af...521b`; exact policy path resolves |
| Registry generation integrity | transaction receipt and `gt registry inspect --no-census --json` | 313 records, coherent/current, canonical/packaged/projection parity, no stale or missing revision |
| Lifecycle idempotence | work-item history and event audit | existing version 3 and one reopen event retained; no second append |
| DB authorization posture | source call-site scan and direct negative test | sole production caller; empty required-path policy rejected |
| WI-5441 non-regression | focused CLI/DB regression suite | original PAUTH, v007/v008, controlling GO, metadata, and subset behavior unchanged |
| Registry recovery | fault matrix and unknown/tampered-state tests | only journal-proven known state completes forward; unknown remains blocked |
| Public inventory authority | inventory and migration tests | public API only; one coherent snapshot; opaque boundaries preserved |
| F5 evidence correction | exact governance suite | stale WI-5648 allowance absent; WI-5178 residuals explicit and non-waiving |
| Deterministic continuation | two clean-process preflights | identical hashes, generation, receipt, status, and zero unauthorized writes |
| Source retention | existence and byte audit | all 90 old sources and all 90 destinations remain |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "v4-009 design, v4-012 GO, owner registry-authority rule, and deterministic post-implementation registry resolver audit",
  "canonical_authority": "config/registry/sot-artifacts.toml through groundtruth_kb.project.registry_control_plane",
  "primary_route": "preserve the completed lifecycle repair, atomically admit the reviewed 167 manifest records plus one exact load-bearing policy record, then run two read-only preflights",
  "before_behavior": "the migration policy is a tracked runtime dependency but is absent from the authoritative registry",
  "after_behavior": "the policy and all 180 manifest locators resolve in one coherent 313-record generation",
  "self_descriptive_naming": "the singleton ID and notes identify the exact WI-5640 migration policy and why it is load-bearing",
  "obsolete_guidance_disposition": "no consumer guidance or obsolete source is rewritten in this slice",
  "history_preservation": "bridge, Git, MemBase history, all 90 sources, and all 90 destinations remain present",
  "baseline": "145 registry records; 13 existing and 167 missing manifest locators; one separately missing load-bearing policy",
  "expected_result": "one coherent 313-record generation resolving 180 of 180 manifest locators plus the policy",
  "rollback": "abort before transaction or use only journal-proven recovery; no retained file is removed",
  "hard_invariants": [
    "no second WI-5640 lifecycle append",
    "no consumer reference rewrite or Stage B apply",
    "no obsolete-source deletion",
    "no registry-member removal or conversion",
    "no commit, push, release, deployment, dispatcher mutation, or history rewrite"
  ],
  "fail_closed_conditions": [
    "bridge, PAUTH, work-item-version, CSV, path-set, singleton-record, generation, or receipt drift",
    "registry collision, ambiguity, missing load-bearing member, or mixed generation",
    "unknown recovery combination",
    "preflight nondeterminism or permission failure"
  ],
  "essential_context_preservation": "authoritative membership, projection parity, retained sources, immutable audit trails, WI-5441 bindings, and WI-5178 residual status remain visible"
}
```

## Applicability Preflight

- packet_hash: `sha256:b45e793f68c2461c17c7c92336e26d3a88b2b1fdfda19a3722ffff665918ecc4`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- declared_target_paths: [".gtkb-state/file-reference-migration/wi5640/**", "config/file-reference-migration/wi5640.toml", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth.db", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "scripts/gtkb_file_reference_migration.py"]
- applicability_path_evidence: [".gtkb-state/file-reference-migration/wi5640/**", "bridge/gtkb-file-move-rename-canonicalization-v4-009.md`", "bridge/gtkb-file-move-rename-canonicalization-v4-010.md`", "bridge/gtkb-file-move-rename-canonicalization-v4-011.md`", "bridge/gtkb-file-move-rename-canonicalization-v4-012.md", "bridge/gtkb-file-move-rename-canonicalization-v4-012.md`", "bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`", "config/file-reference-migration/wi5640.toml", "config/file-reference-migration/wi5640.toml`", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth.db", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "scripts/gtkb_file_reference_migration.py", "scripts/gtkb_file_reference_migration.py`"]
- content_source: `pending_content`
- content_file: `.gtkb-state/propose-drafts/gtkb-file-move-rename-canonicalization-v4-013-recovery-assembly.md`
- operative_file: `bridge/gtkb-file-move-rename-canonicalization-v4-011.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-file-move-rename-canonicalization-v4`
- Operative file: `.gtkb-state\propose-drafts\gtkb-file-move-rename-canonicalization-v4-013-recovery-assembly.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

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

Existing requirements are sufficient. This revision corrects the admitted
membership set required to satisfy the owner's registry-authority invariant; it
does not introduce a new mechanism or broaden implementation behavior.

## Owner Decisions / Input

- The registry is the ultimate SoT for which artifacts are part of GT-KB.
- Every non-disposable load-bearing artifact must be registered.
- All obsolete sources remain through repeated deterministic verification under
  `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

No new owner decision is requested.

## Prior Deliberations And Evidence

- `bridge/gtkb-file-move-rename-canonicalization-v4-009.md`
- `bridge/gtkb-file-move-rename-canonicalization-v4-010.md`
- `bridge/gtkb-file-move-rename-canonicalization-v4-011.md`
- `bridge/gtkb-file-move-rename-canonicalization-v4-012.md`
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`

## Risk And Rollback

The principal risk is treating the reviewed manifest set as the complete
load-bearing membership set when the migration policy itself is outside that
manifest. Binding the unchanged 167-path digest and the separate singleton record
digest prevents silent set substitution. The single registry transaction keeps
all three readers on one generation. Unknown recovery states remain blocked.
No source or destination is deleted, and the completed append-only lifecycle
repair is preserved rather than replayed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
