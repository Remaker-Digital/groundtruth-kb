NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop-interactive
author_metadata_source: x-codex-turn-metadata

bridge_kind: implementation_report
Document: gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization
Version: 007
Date: 2026-08-12 UTC
Responds to: bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-006.md
Approved proposal: bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-005.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6075
Related Work Items: WI-6078
Recommended commit type: feat:
Recommended commit subject: feat(registry): admit WI-6075 load-bearing artifacts

target_paths: ["bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json", "bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-canonical-registry.patch", "bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-packaged-registry.patch", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]

# WI-6075 Implementation Report — Exact Two-Record Registry Admission

## Implementation Claim

Prime Builder completed the exact corrective slice approved by v005 and v006.
The canonical registry reconciliation surface generated one generation-bound
plan containing exactly the two reviewed load-bearing records. The governed
`gt registry register --batch-file` surface then completed one dry-run and one
live apply. The live call succeeded on its first and only invocation; it was
not an idempotent retry.

The registry moved from 1,445 to 1,447 declarations. Canonical and packaged
TOML bytes remain identical, the MemBase projection is coherent, both approved
IDs are present once, registry identity is current, validation has no errors,
and fresh reconciliation reports zero invalid-unknown and zero unregistered
load-bearing artifacts. The earlier six-identity removal remains intact.

The real Git index was not used for patch construction or finalization
preparation. Its physical and logical digests, only-staged-path set, and exact
foreign stage-0 blob entries remained byte-for-byte unchanged through the
registry transaction and disposable-index patch verification.

All generated plan, patch, and numbered bridge artifacts reside under the
mandatory project root `E:\GT-KB`; no live dependency, output, or verification
evidence for this implementation resolves outside that root.

## Authority And Start Evidence

- Latest reviewed proposal: v005, 19,521 bytes, SHA-256
  `B99E3D81A1EAAD442C2919392FE1F70335E88F9B137263C4CE73CDEF9C1BB4F1`.
  Governed publication row 2217 is `consumed`, with capability
  `sha256:b3d7eb507facdca5d638d7bd2966088652cb4a32aba3c4eda0bf3e2c1942207a`,
  result `sha256:7808b396dd01f2cca562c34d63de6d33d8271ddb7b4e01e35544371fbae08d04`,
  and revision `SOTREV-472774EA690B4515A999A96894098A5E`.
- Independent GO: v006, 16,107 bytes, SHA-256
  `B8ACCF50C07DF0BD987AC925C1E8E65C1440660A1B6448DACD40211753808255`.
  Governed publication row 2220 is `consumed`, with capability
  `sha256:5656d726145fdeb2dce6d6151acf6ddece109df30db101dc78e60f87eaf01bc4`,
  result `sha256:ad5f12732a1e898f16b6136609f335a79f425f64e1786c80bd834a01b256685c`,
  and revision `SOTREV-C77E28A2DB0A4EB8A6BFE513F62C873D`.
- Prime Builder work-intent claim: row 38101, kind `go_implementation`, session
  `019fe0e5-4e93-7280-9778-8d6738c9626d`, acquired
  `2026-08-12T08:10:13Z`. It was extended exactly once before report filing;
  the implementation deadline is `2026-08-12T09:10:13Z` and grace/TTL is
  `2026-08-12T09:20:13Z`.
- Finalized schema-v3 start packet:
  `sha256:a865b3d7164bd41dbc47b49f191a2b715bf1f845fe755bed5388d3647f297726`;
  pre-start packet:
  `sha256:b739b2ba7619f7d08921d660a14e084dde0066ffae125748c1a320b6b7398f3b`.
  The packet binds v005, v006, PAUTH v2, this Prime Builder session, and the
  exact six implementation targets; it expires `2026-08-12T10:12:00Z`.
- Operation-time evaluator:
  `project-authorization-operation-time-enforcement` v1,
  SHA-256 `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`;
  taxonomy v2 SHA-256
  `C0DA33114C9B3FD2B3DFD816043B458D8C0171143D014B79B812AA354F0EE450`.
  Both `implementation_packet_create` and `implementation_start` decisions
  were allowed for the exact target cohort.

## Exact Plan And Transaction Evidence

The canonical command
`gt registry reconcile --batch-output bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json`
created a 5,040-byte plan with SHA-256
`FCFB36D5779E3FD1EAC2596C08C6AB3CC2608D9F335A5F2931952F27CE4C8A42`.
It binds:

- starting generation
  `sha256:9fd3c371edd0bf6b42f23ff40b274d115be442e498487f81f7c55b3cc125d5e8`;
- candidate manifest
  `sha256:d294102fca66988c276bf07cb70d0e2089ba115d52fa2559d6b12fcc70ba37f5`;
- reconciliation evidence
  `sha256:b24a022bd006c622ac9eb1e6fcfb0fe10084e46f1b994a13fe3a0ad5f257b178`;
- all five observer-input digests; and
- exactly two `admission_candidates` and exactly two `records`, matching v005
  field-for-field.

The governed dry-run returned:

- receipt
  `sha256:0ad84cf3500b4ab14763ad42fa7ba5427ecfebea4cbcf7da73cec1c23a6d8a14`;
- desired record count `1447`;
- desired declaration digest
  `sha256:39f0ee3a14ab21a7181ec2e8118e2aca2d31c8182fc5761f0256cd7204e2a866`;
- desired projection digest
  `sha256:c43e4cb8e21f1e05002f8906f8a72469d907e221b40132f25416c0e601fa0266`.

The same public command was invoked once without `--dry-run`, with that exact
receipt. It returned:

- journal `SOTTXN-9DDE468409314F2F994BF113D392B12F`;
- receipt
  `sha256:39923fd21c020f5909f06e187a467a1f5eb37a0e7bc62abc4a7e78dc1cbcbb23`;
- `record_count: 1447`;
- `idempotent_retry: false`;
- declaration and projection digests exactly equal to the dry-run postimage.

Read-only journal inspection shows `journal_state=committed`,
`filesystem_result=canonical_and_packaged_replaced`, null error, the exact
bridge/session/start-packet/PAUTH bindings, old declaration/package digest
`sha256:12e824cf58780adf882f205b3550694595840139ff6784ade6f18c6e0076c0d4`,
old projection digest
`sha256:519ab805a4f76a7b849ebbdc8bdbd6cc994ac91405c9c64289760d99a95a184b`,
and `projection_transaction.changed_ids` containing only:

1. `wi5441-member-groundtruth-kb-src-groundtruth-kb-project-regist-6038d4298f`
2. `wi5441-member-scripts-batch-finalize-verified-py-e706bcfa32`

## Postimage Readback

- `gt registry inspect --json --no-census`: `coherent=true`, identity
  `current=true`, `missing=[]`, no object-kind mismatch, record count 1,447,
  canonical/package digest
  `sha256:39f0ee3a14ab21a7181ec2e8118e2aca2d31c8182fc5761f0256cd7204e2a866`,
  projection digest
  `sha256:c43e4cb8e21f1e05002f8906f8a72469d907e221b40132f25416c0e601fa0266`,
  and generation
  `sha256:3ad8027ce117dedcc6dd3bca0ddc8f8998f5a65fd01d2d3bdb6448a84bd5944c`.
- `gt registry validate --json`: `valid=true`, `errors=[]`,
  `membership_complete=true`, `invalid_unknown=0`,
  `unregistered_load_bearing=0`, and `gaps=[]`.
- Fresh `gt registry reconcile --json`: `admission_candidates=[]`,
  `batch_records=[]`, `membership_complete=true`, `invalid_unknown=0`, and
  `unregistered_load_bearing=0`.
- Both approved IDs return the exact v005 record fields through
  `gt registry show <id> --json`.
- All six identities retired in the consumed v001-v003 transition still return
  absent from the canonical `gt registry show` reader.
- Evidence-only backing files remain byte-exact:
  `registry_publication_diagnostics.py` is 8,210 bytes at
  `DB5F8D5B23EEDAFE4B4E60144A8A7DE62E51B1CAF67131B5A4724D6702EA51D0`;
  `batch_finalize_verified.py` is 46,069 bytes at
  `AC4FB63337C3C68C61555A8B9719B60BD9D2BECE297FE732E49C22B06E67C9B0`.

The periodic deep content audit was not performed. The resulting
`audit_not_performed` marker and `release_eligible=false` / `sweep_eligible=false`
are outside this admission slice and do not create a registry validity or
membership gap. No sweep, release, or destructive action was attempted.

## Disposable-Index Patch Evidence

Both singleton full-delta patches were generated from Git HEAD
`4f9c776104f30dda8d26a2bf7e24c173f1219555` with a disposable index initialized
by `git read-tree HEAD`. They include the already-consumed six-identity delta
plus this exact two-record admission, as required by v005.

| Patch | Bytes | SHA-256 | Only touched path | Strict result |
| --- | ---: | --- | --- | --- |
| `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-canonical-registry.patch` | 55,569 | `F0924B58E860EB037B7FDDC229C8EC0C4619717B601D244FAD7116FB6117E8C5` | `config/registry/sot-artifacts.toml` | `git apply --cached --check --whitespace=error-all` passed; postimage blob `df0f810c2d96921f4cc2f428a9e70db08140e393` |
| `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-packaged-registry.patch` | 55,793 | `E335FC83D9A310AFA8AB1F62A9403E4976DA5B18CCCE51F246B43993F190CE21` | `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` | `git apply --cached --check --whitespace=error-all` passed; postimage blob `df0f810c2d96921f4cc2f428a9e70db08140e393` |

Each strict apply began from HEAD, used no fuzz, three-way merge,
ignore-whitespace, or whole-worktree staging, changed exactly one named path,
and reproduced the current worktree blob. Each patch reports 1,258 insertions
and 102 deletions against HEAD.

The real index stayed unchanged at physical SHA-256
`5E67F7EA360EA7EE2D7CB68628478935F97F1239CB5F02975B4E08856287DBAF`
and logical `git ls-files -s` SHA-256
`69DEB298BBAD653B4C19AAD99360EF5799C9164018909FAB9C3ADB19274320C5`.
Its only staged paths remain the two registry mirrors, each stage 0, mode
100644, blob `d4a1aca0e15172acad63f218f32c9814b2055677`.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification Plan And Results

| Linked specification(s) | Executed evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001`; `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`; `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`; `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`; `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Canonical reconcile plan, governed batch dry-run/live receipt, committed journal, `inspect`, `show`, `validate`, and fresh `reconcile` | Exactly two schema-valid records admitted through the exclusive control plane; declarations/projection coherent; zero membership gaps. |
| `DCL-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Fresh pre-apply generation and candidate manifest checks; fresh post-apply validate/reconcile | Current generation was bound before effect; zero unknown/load-bearing gaps; no sweep performed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | v005/v006 receipts, claim row 38101, schema-v3 packet, target-by-target authorization validation, exact journal bindings | Live independent GO, current PAUTH v2, Prime claim/session, packet, project, WI, specs, and exact targets all matched before mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | 50 focused tests, Ruff/format/AST checks, strict singleton patch replay, registry readbacks, physical/logical real-index comparison, `git diff --check` | All gates passed; no backing-file, application, foreign-index, dispatcher, or out-of-root impairment. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Exact governed plan/patch artifacts, append-only report, and retained WI-6078 terminal dependency | Durable evidence is filed; WI-6078 remains unresolved until independent v008 terminal verification. |

## Commands Run

- `gt bridge show gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization --json --compact`
- `python scripts/implementation_authorization.py validate --target <each exact target>`
- `gt registry inspect --json --no-census`
- `gt registry validate --json`
- `gt registry reconcile --json`
- `gt registry reconcile --batch-output bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json`
- `gt registry register --batch-file bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json --dry-run --bridge-id gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization --session-id 019fe0e5-4e93-7280-9778-8d6738c9626d --start-packet-hash sha256:a865b3d7164bd41dbc47b49f191a2b715bf1f845fe755bed5388d3647f297726 --pauth-id PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730 --changed-by prime-builder/codex/A --change-reason <bounded WI-6075 reason>`
- The same `gt registry register --batch-file` command once without
  `--dry-run`, adding `--dry-run-receipt sha256:0ad84cf3500b4ab14763ad42fa7ba5427ecfebea4cbcf7da73cec1c23a6d8a14`.
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short -k "registry_transaction_updates_both_declaration_revisions or registration_preview_binds_generation_manifest_and_authority or registry_cli_register_amend_sync_and_direct_observe_denial"`
- `python -m pytest groundtruth-kb/tests/test_artifact_membership_reconciliation.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_registry_transition_slice1.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_batch_finalize_verified.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/registry_publication_diagnostics.py scripts/batch_finalize_verified.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/registry_publication_diagnostics.py scripts/batch_finalize_verified.py`
- Python `compile(..., mode="exec")` for both evidence-only backing files.
- Disposable-index `git read-tree HEAD`, singleton `git diff --binary --full-index`, and strict `git apply --cached --check --whitespace=error-all` for each patch.
- `git diff --check HEAD -- <two registry mirrors>` and
  `git diff --cached --check -- <two registry mirrors>`.

## Observed Test Results

- Registry control-plane registration/CLI slice: `3 passed, 58 deselected`.
- Artifact membership reconciliation suite: `14 passed`.
- Registry transition slice 1: `11 passed`.
- Batch finalizer suite: `22 passed`.
- Total focused tests: `50 passed`.
- Ruff lint: `All checks passed!`.
- Ruff format: `2 files already formatted`.
- AST compile: both backing files passed.
- Worktree and cached diff checks: passed with no output.
- Strict patch checks: both passed and reproduced the exact final blob.

## Files Changed

- `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json`
- `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-canonical-registry.patch`
- `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-packaged-registry.patch`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth.db` — service-owned registry projection/journal/revision mutation;
  intentionally excluded from Git finalization.

The report helper observed five Git-visible implementation paths and 1,162
foreign dirty paths. Every foreign path is excluded. The two backing Python
artifacts are evidence only and remain outside the changed/finalization set.

## Atomic Finalization Boundary

Independent v008 verification should use the approved two hunk patches in a
disposable index initialized from HEAD and include only:

- numbered bridge versions v001 through v007;
- the exact plan and two patch evidence artifacts;
- the two registry mirror postimages produced by the reviewed patches; and
- the generated v008 VERIFIED verdict.

`groundtruth.db` must remain outside Git. The finalizer must restore the real
index byte-for-byte to the physical/logical digests and exact `d4a1...` stage
entries recorded above. Whole-worktree staging, fuzz, three-way apply,
ignore-whitespace, foreign-path absorption, push, deployment, and release
remain prohibited.

## Acceptance Criteria Status

- [x] The exact two approved records are the only declarations added.
- [x] One governed dry-run and one first-attempt live registration moved the
  registry from 1,445 to 1,447 records.
- [x] Identity is current; declaration/package/projection state is coherent;
  validation and reconciliation have zero invalid/load-bearing gaps.
- [x] The consumed six-identity transition remains intact and was not replayed
  or reversed.
- [x] Both backing Python artifacts remain byte-exact and outside the patches
  and finalization cohort.
- [x] The shared real index retains only the exact foreign `d4a1...` pair.
- [x] Both singleton patches strictly reproduce the final registry postimage
  from HEAD without fuzz, three-way, or whitespace bypass.
- [ ] Independent v008 terminal verification and atomic commit remain pending;
  WI-6078 must remain unresolved until that succeeds.

## Owner Decisions / Input

This implementation executes the already-recorded owner disposition
`DELIB-20260808012018`, the earned-registration doctrine in
`DELIB-20260807012015`, and the current completion directive
`DELIB-20260808-WI6077-WI6081-LEAD-PRIME-COMPLETION-DIRECTIVE`. PAUTH v2 is
grounded in `DELIB-202667732`. No new owner choice, waiver, credential action,
external action, deployment, release, or destructive cleanup is requested by
this report.

## Prior Deliberations And Governed History

- `DELIB-20260808012018` — controlling six-identity retirement and registry
  correction disposition.
- `DELIB-20260807012015` — earned registration and closure-before-sweep.
- `DELIB-20260808012222` — governed authority evidence for
  `registry_publication_diagnostics.py`.
- `DELIB-202667732` — active whole-project PAUTH v2 repair and scope.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-001.md`
  through `-004.md` — original transition authorization, implementation
  report, and controlling reconciliation NO-GO.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-005.md`
  — exact two-record corrected proposal.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-006.md`
  — independent GO authorizing this implementation.

## Risk And Rollback

The material concurrent-drift risk was bounded by the generation, plan,
candidate manifest, observer digests, claim, packet, PAUTH, dry-run receipt,
and immediate operation-time readback. The live apply committed successfully
and must not be repeated. If later verification discovers an unexpected
registry defect, the only rollback route is a separately proposed, reviewed,
generation-bound registry transaction. Raw TOML, SQLite, projection, journal,
receipt, sidecar, or Git-index repair remains prohibited.

## Loyal Opposition Asks

1. Independently reproduce the exact authority, registry, journal, patch,
   index, and spec-derived test evidence above.
2. If every result holds, publish v008 VERIFIED through one atomic finalizer
   transaction using the exact include and hunk-patch boundaries above;
   otherwise issue NO-GO with concrete findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
