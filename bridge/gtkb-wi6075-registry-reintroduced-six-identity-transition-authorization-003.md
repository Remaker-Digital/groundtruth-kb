NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; exact governed six-identity registry transition
author_metadata_source: transcript init keyword and Codex runtime system metadata

# GT-KB Bridge Implementation Report - gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization - 003

bridge_kind: implementation_report
Document: gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization
Version: 003
Responds to: bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-002.md
Approved proposal: bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-001.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6075
target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: feat:

## Implementation Claim

Completed the independently approved, single-use `membership_set` transition for
exactly the six reintroduced pre-rename WI-5441 registry identities. The public
`gt registry transition request` / `apply` control plane consumed one fresh
generation-bound request and committed one receipt-bound journal transaction.
The canonical declaration, packaged declaration, and MemBase projection are now
coherent at 1,445 records; registry identity is current; validation is clean;
and membership reconciliation reports zero invalid-unknown and zero
unregistered-load-bearing artifacts.

No raw TOML, SQLite, projection, backing-file, Git-index, dispatcher, or TAFE
mutation was performed. The legacy TAFE dispatcher remained disabled.

## Specification Links

- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required. The transition is the exact operational
execution of `DELIB-20260808012018` under proposal `-001` and independent GO
`-002`; it does not widen or reinterpret that decision.

## Prior Deliberations

- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`; `GOV-PLATFORM-SOT-REGISTRY-001`; `ADR-REGISTRY-AUTHORITATIVE-ARTIFACT-LIFECYCLE-001` | One fresh request `REGTXNREQ-FE2EAF2761FA49EFBFA139E5A68F8AB4` was bound to the exact six removals and pre-generation, then consumed once by committed journal `SOTTXN-3258EA6AC7F240F98B36EB269115C54E`. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`; `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | `gt registry inspect --json --no-census` reports coherent declarations/projection, record count 1,445, identity current, `missing=[]`, and no object-kind mismatch. Canonical and packaged declaration SHA-256 values are identical. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The request bound live pre-generation `sha256:af78d18d997be53ffc44cca8b7620f9845c5fad66bd26b211256f7a84420e6c5`; post-readback reports generation `sha256:9fd3c371edd0bf6b42f23ff40b274d115be442e498487f81f7c55b3cc125d5e8`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Mutation used independent GO `-002`, claim row 37924, PAUTH v2, schema-v3 packet `sha256:c3d62be3025f62ff1ae5f2c1eec8902085e85959c8d3feeaa7cf4ab9680ea52b`, pre-start hash `sha256:1c8c9bdfeccf5efbb763fd680c9d423ba9fa0883c5d42aa63efa33f5e3f61f53`, and a fresh OPS envelope. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report preserves the approved project/work-item/spec links and records reproducible transaction, registry, and focused-test evidence for independent verification. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Exact target and receipt readbacks show the change is confined to the governed GT-KB registry transaction; backing artifacts and unrelated worktree/index state were not changed or absorbed. |

## Commands Run

- `gt registry inspect --json --no-census`
- `gt registry validate --json`
- `gt registry diff --json`
- `gt registry reconcile --json`
- Public `gt registry transition request` with operation `membership_set`, the
  six exact removal IDs, pre-generation `sha256:af78d18d...`, current PAUTH,
  claim/session/start-packet evidence, and `DELIB-20260808012018`.
- Public `gt registry transition apply` dry-run followed once by live apply for
  request `REGTXNREQ-FE2EAF2761FA49EFBFA139E5A68F8AB4`, with this thread's GO
  `-002` and the fresh OPS activity envelope.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_registry_transition_slice1.py -q --tb=short`

## Observed Results

- Preimage: declaration/package digest
  `sha256:8b1045403cca37495ad5871186c48925f0bee68c8ae5ebbccbfb090dc7033461`,
  projection digest
  `sha256:b1283a32a20db8df97d443f54456aa571ad6f2c1c623076670f83fc4bd8ee791`,
  generation
  `sha256:af78d18d997be53ffc44cca8b7620f9845c5fad66bd26b211256f7a84420e6c5`,
  and 1,451 records.
- Request `REGTXNREQ-FE2EAF2761FA49EFBFA139E5A68F8AB4`, digest
  `sha256:819593398cbfc95bfab0901c74580a6cb793f36448089e1e1946aa215bb7dcce`,
  was active before apply and consumed exactly once at `2026-08-10T22:17:23Z`.
- Committed journal: `SOTTXN-3258EA6AC7F240F98B36EB269115C54E`.
  Receipt digest:
  `sha256:3a7760d45b30c832fde2548876c4ec67a383dca6a06e5eba61b12a99e490cc14`.
  `idempotent_retry=false`.
- Postimage: canonical/package digest
  `sha256:12e824cf58780adf882f205b3550694595840139ff6784ade6f18c6e0076c0d4`,
  projection digest
  `sha256:519ab805a4f76a7b849ebbdc8bdbd6cc994ac91405c9c64289760d99a95a184b`,
  generation
  `sha256:9fd3c371edd0bf6b42f23ff40b274d115be442e498487f81f7c55b3cc125d5e8`,
  and 1,445 records.
- `gt registry validate --json`: `valid=true`, `errors=[]`.
- Identity/readback: `current=true`, `missing=[]`, and no object-kind mismatch.
- Reconciliation: `invalid_unknown=0`, `unregistered_load_bearing=0`,
  `membership_complete=true`, and no admission candidates.
- The reviewed admission-plan evidence remained byte-exact at
  `sha256:4edfe9958f787f3f55387c3c4adee30176768d51e26874161259ca93383edd01`
  (11,634 bytes).
- Focused registry-transition tests: `11 passed`; one ambient pytest config
  warning only.

## Files Changed

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth.db`

Excluded out-of-scope dirty paths: 1084.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The diff adds or changes skill, script, or platform capability surfaces.

```text
     config/registry/sot-artifacts.toml                 | 1326 ++++++++++++++++++--
     .../v1/config/registry/sot-artifacts.toml          | 1326 ++++++++++++++++++--
     2 files changed, 2448 insertions(+), 204 deletions(-)
```

## Acceptance Criteria Status

- [x] Exactly the six reviewed legacy identities were removed; no additions or
  coverage changes were requested.
- [x] Canonical and packaged declarations are byte-identical and projection
  coherent.
- [x] Identity is current, validation is clean, and membership is complete.
- [x] One request was consumed once and one journal committed with exact
  generation/session/authorization binding.
- [x] Legacy paths remained absent and renamed destinations remained present at
  the reviewed digests before request/apply.
- [x] No backing artifact, source, test, dispatcher, TAFE, Git index,
  credential, deployment, release, or external-system state changed.

## Requirement Sufficiency

Existing requirements are sufficient. The implementation executes the exact
reviewed six-identity retirement and introduces no new requirement.

## Risk And Rollback

The one-use request has been consumed and must never be replayed. If independent
readback finds an unexpected registry delta, recovery must use a new governed,
generation-bound reverse transition under current authority; raw TOML, SQLite,
projection, journal, or sidecar edits are prohibited. Bridge, request, journal,
and receipt history remains append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.

---

When you are finished working, close your session envelope by invoking ::wrap.
