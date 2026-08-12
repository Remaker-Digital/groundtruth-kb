REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop-interactive
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization
Version: 005
Date: 2026-08-12 UTC
Responds to: bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-004.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6075
Related Work Items: WI-6078

target_paths: ["bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json", "bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-canonical-registry.patch", "bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-packaged-registry.patch", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]
implementation_scope: exact_two_record_registry_admission_and_terminal_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false

# WI-6075 REVISED — exact two-record registry admission after the consumed six-identity transition

## Revision Claim

Version 005 accepts the findings in NO-GO v004 and replaces its now-stale
one-gap observation with a fresh, generation-bound correction for the exact two
load-bearing membership gaps reported by the live registry control plane. The
six-identity removal described by v001-v003 is already consumed and remains
correct; this revision does not replay, reverse, or widen it.

The new work is one governed exact-batch admission of two records through
`gt registry register --batch-file`. It is a fresh operation against the live
1,445-record generation, not a continuation of request
`REGTXNREQ-FE2EAF2761FA49EFBFA139E5A68F8AB4` and not a raw edit of either
registry declaration or MemBase. After independent GO and a fresh
implementation-start packet, Prime Builder may materialize one exact plan,
perform one dry-run and one live registration, produce two reviewed singleton
patch artifacts, report the result, and route it to independent atomic
verification.

## Requirement Sufficiency

Existing requirements are sufficient. NO-GO v004 established a factual
postcondition failure, not an ambiguous product requirement. The current
registry control plane now supplies the exact admission candidates and the
transactional batch-registration API needed to close it without source changes
or an owner design choice.

## Response To V004 Findings

### F1 — reconciliation must be truthful at verification time

Accepted. The v003 claim that membership was complete is historical evidence
from its immediate post-operation readback, not the current postcondition. A
fresh live census now reports identity state current, `missing=[]`,
`invalid_unknown=0`, and exactly two unregistered load-bearing paths. Version
005 binds those two records exactly and makes zero-gap reconciliation an
operation-time and terminal-verification requirement.

### F2 — concurrent registry state must be explicitly bounded

Accepted. Both registry declarations are currently identical at SHA-256
`12E824CF58780ADF882F205B3550694595840139FF6784ADE6F18C6E0076C0D4`,
934,972 bytes, 1,445 records, generation
`sha256:9fd3c371edd0bf6b42f23ff40b274d115be442e498487f81f7c55b3cc125d5e8`.
They are `MM` in the shared worktree: the real index contains a foreign
stage-0 blob `d4a1aca0e15172acad63f218f32c9814b2055677`, while the worktree contains
the consumed six-identity postimage. The implementation and finalizer must
preserve that real-index entry byte-for-byte and may operate only through an
explicit disposable index for patch and commit verification.

Registered/disposable census counts can vary as unrelated in-root artifacts
arrive. They are observation evidence, not a scope-expansion mechanism. The
operation is bound instead to the exact two load-bearing candidate records,
the live generation, the two registry preimages, the candidate manifest, and a
fresh dry-run receipt. Any third load-bearing candidate or any change to either
record stops the operation and requires review.

## Exact Admission Scope

The only authorized new registry records are:

```json
[
  {
    "authority_spec_id": "GOV-PLATFORM-SOT-REGISTRY-001",
    "backup_policy": "git_tracked",
    "coverage_mode": "exact",
    "depends_on": [],
    "domain": "control_surface",
    "forbidden_substitutes": [],
    "health_check_function": "",
    "id": "wi5441-member-groundtruth-kb-src-groundtruth-kb-project-regist-6038d4298f",
    "lifecycle": "active",
    "mutation_api": "Governed bridge-authorized source edit; direct owner in-place content edit remains valid",
    "notes": "Deterministically admitted by WI-5441 observers: package_and_entrypoint, registered_dependency_closure.",
    "owner_role": "shared",
    "restore_action": "git_restore",
    "storage_path": "groundtruth-kb/src/groundtruth_kb/project/registry_publication_diagnostics.py",
    "versioning_policy": "git_tracked"
  },
  {
    "authority_spec_id": "GOV-PLATFORM-SOT-REGISTRY-001",
    "backup_policy": "git_tracked",
    "coverage_mode": "exact",
    "depends_on": [],
    "domain": "control_surface",
    "forbidden_substitutes": [],
    "health_check_function": "",
    "id": "wi5441-member-scripts-batch-finalize-verified-py-e706bcfa32",
    "lifecycle": "active",
    "mutation_api": "Governed bridge-authorized source edit; direct owner in-place content edit remains valid",
    "notes": "Deterministically admitted by WI-5441 observers: registered_dependency_closure.",
    "owner_role": "shared",
    "restore_action": "git_restore",
    "storage_path": "scripts/batch_finalize_verified.py",
    "versioning_policy": "git_tracked"
  }
]
```

Current evidence-only backing-file identities are:

| Path | Bytes | SHA-256 | Mutation status |
| --- | ---: | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/project/registry_publication_diagnostics.py` | 8,210 | `DB5F8D5B23EEDAFE4B4E60144A8A7DE62E51B1CAF67131B5A4724D6702EA51D0` | evidence only; no edit |
| `scripts/batch_finalize_verified.py` | 46,069 | `AC4FB63337C3C68C61555A8B9719B60BD9D2BECE297FE732E49C22B06E67C9B0` | evidence only; no edit |

The current candidate manifest is
`sha256:d294102fca66988c276bf07cb70d0e2089ba115d52fa2559d6b12fcc70ba37f5`.
Both paths must remain present and byte-exact at operation time. They are not
implementation targets, must not be staged or committed by this thread, and
must not be absorbed into either patch artifact.

## Authorized Implementation Sequence

No protected or registry mutation may begin until an unrelated Loyal
Opposition session files GO on this v005, Prime Builder acquires a fresh exact
`go_implementation` claim, and one fresh schema-v3 packet binds v005, that GO,
PAUTH v2, and all six declared targets.

1. Re-read v001-v005 and every consumed receipt. Prove the six-identity request
   and journal remain consumed and are not replayed.
2. Re-run `gt registry inspect --json --no-census`, `validate --json`, and
   `reconcile --json`. Require coherent identical declarations, current
   identity, no missing identity, `invalid_unknown=0`, and exactly the two
   records above as the complete load-bearing admission set.
3. Capture HEAD, physical and logical real-index digests, stage entries, both
   registry hashes, the database schema digest, current registry generation,
   record count, and relevant transaction/journal counts. Require the only
   staged paths to remain the two registry mirrors at the exact foreign
   stage-0 blob `d4a1aca0e15172acad63f218f32c9814b2055677`.
4. Materialize
   `bridge/cleanup-evidence/gtkb-wi6075-two-load-bearing-admission-plan.json`
   from the fresh control-plane `batch_records`. The file must contain exactly
   the two JSON records above plus the current candidate manifest, observer
   input digests, generation, registry preimage hashes, and backing-file
   hashes. It must contain no third record or placeholder.
5. Invoke `gt registry register --batch-file <plan> --dry-run` with the exact
   bridge, session, start-packet, PAUTH, actor, and reason bindings. Capture the
   canonical dry-run receipt. Abort on any drift, widened record set, duplicate
   conflict, or currentness error.
6. Invoke the same public register surface once, and only once, with the exact
   dry-run receipt. Never edit TOML, SQLite, projection, journal, or registry
   revision rows directly. If it raises, do not retry; publish a truthful
   failed-implementation report.
7. Require a 1,447-record coherent postimage, both new IDs present once,
   `valid=true`, `membership_complete=true`, zero invalid identities, zero
   unregistered load-bearing paths, identical canonical/package bytes, one
   receipt-bound registry transaction, and no unrelated registry delta.
8. From a disposable index initialized from the exact current HEAD, generate
   and validate two singleton full-delta patches from HEAD to the final
   registry postimage. Each patch must touch only its named registry file,
   apply strictly with no fuzz/three-way/whitespace bypass, and reproduce the
   exact worktree blob. The patches must include the earlier consumed
   six-identity delta plus these two admissions so the child carrier can close
   without losing history.
9. Re-run registry transition/control-plane tests, registry inspect/validate/
   reconcile, strict patch tests, Ruff/format where applicable, compile checks,
   and `git diff --check`. File v007 as the truthful implementation report.
10. Route v007 to a fresh unrelated Loyal Opposition session for one atomic
    v008 VERIFIED transaction. The finalizer must apply only the two reviewed
    hunk patches in a disposable index, include the numbered v001-v007 chain
    plus the plan and patch evidence, auto-create v008, exclude
    `groundtruth.db` from Git, and restore the real index byte-for-byte with the
    same two foreign `d4a1...` stage entries.

## Explicit Non-Authority

This revision does not authorize:

- replay, reversal, or amendment of the consumed six-identity transition;
- admission of any record other than the exact two above;
- edits to either backing file or any source/test path;
- raw TOML, SQLite, registry-projection, journal, receipt, or sidecar edits;
- dispatcher or legacy TAFE mutation;
- replacing or clearing the foreign real-index stage entries;
- an ignore-whitespace, fuzz, three-way, or whole-worktree staging bypass;
- push, deploy, release, history rewrite, destructive cleanup, or credential work;
- resolution of WI-6078 before this carrier reaches terminal VERIFIED and a
  fresh registry validation reports zero gaps.

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

## Prior Deliberations And Governed Evidence

- `DELIB-20260808012018` — original owner disposition and six-identity retirement authority; already consumed, preserved by reference.
- `DELIB-20260807012015` — earned registration and closure-before-sweep doctrine.
- `DELIB-20260808012222` — current in-root reference evidence for `registry_publication_diagnostics.py`.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-001.md` — original exact-six proposal.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-002.md` — original GO.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-003.md` — consumed implementation report.
- `bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-004.md` — controlling NO-GO and required reconciliation correction.
- `bridge/gtkb-wi6075-registry-membership-closure-010.md` — stale parent GO whose six-ID preimage must not be replayed.

## Specification-Derived Verification Plan

| Requirement | Verification | Required result |
| --- | --- | --- |
| Exact admission scope | Compare fresh reconcile `batch_records`, plan JSON, dry-run receipt, and applied receipt | exactly two records; exact IDs and fields; no third record |
| Transactional registry mutation | Inspect public register receipt, registry journal/revision, row counts, and postimage | one dry-run plus one live apply; no raw mutation; 1,445 to 1,447 |
| Registry correctness | `gt registry inspect`, `validate`, and `reconcile` | coherent/current/valid; missing and invalid empty; zero load-bearing gaps |
| Projection parity | Hash canonical and packaged declarations and inspect MemBase projection | declarations byte-identical; projection coherent |
| Backing-file preservation | Hash both evidence-only paths before and after | exact bytes unchanged; absent from patches and commit |
| Historical six-ID preservation | Inspect consumed request/journal and registry diff | six removals remain consumed; no replay/reversal |
| Shared-index isolation | Compare physical/logical index and stage entries before/after apply and finalizer | exact foreign d4a1 pair preserved; no new real-index entry |
| Patch containment | Inspect patch touched paths and strict disposable-HEAD apply | two singleton patches reproduce exact postimage; no fuzz/bypass |
| Regression safety | Focused registry transition/control-plane tests, Ruff/format/compile, diff check | all pass; no new warning attributable to this work |
| Terminal closure | Independent atomic v008 readback | exact cohort committed; receipt complete; registry zero-gap state remains current |

## Acceptance Criteria

1. The exact two records above are the only new registry declarations.
2. The registry moves from 1,445 to 1,447 records through one governed live
   registration after a matching dry-run receipt.
3. Identity remains current, declarations and projection remain coherent, and
   reconciliation reaches zero invalid and zero unregistered load-bearing
   paths.
4. The consumed six-identity transition remains intact and is never replayed.
5. Both backing files remain byte-exact and outside every mutation/commit
   cohort.
6. The shared real index retains exactly the foreign d4a1 registry pair.
7. The two patch artifacts reproduce only the intended registry postimage from
   HEAD and pass strict disposable-index checks.
8. Independent v008 terminal verification succeeds before WI-6078 is resolved.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "bridge/gtkb-wi6075-registry-reintroduced-six-identity-transition-authorization-004.md and the fresh registry reconcile candidate manifest",
  "canonical_authority": "the governed registry control plane, PAUTH v2, the fresh GO/start packet, and the numbered bridge chain",
  "primary_route": "exact two-record plan, transactional dry-run and apply, strict patch evidence, implementation report, independent atomic verification",
  "before_behavior": "the six stale identities are correctly removed, but two current load-bearing artifacts are outside the registry and terminal verification truthfully fails",
  "after_behavior": "both load-bearing artifacts are registered once, registry validation and reconciliation are gap-free, and the consumed six-identity history is terminalized without absorbing foreign work",
  "self_descriptive_naming": "the plan and patch filenames identify WI-6075 and the exact two-load-bearing admission purpose",
  "obsolete_guidance_disposition": "v003 zero-gap evidence is retained as historical immediate readback; v004 and v005 govern current reconciliation truth",
  "history_preservation": "all earlier requests, journals, receipts, numbered bridge files, and real-index entries remain append-only and intact",
  "baseline": {
    "registry_records": 1445,
    "missing_identities": 0,
    "invalid_unknown": 0,
    "unregistered_load_bearing": 2,
    "candidate_manifest": "sha256:d294102fca66988c276bf07cb70d0e2089ba115d52fa2559d6b12fcc70ba37f5"
  },
  "expected_result": {
    "registry_records": 1447,
    "records_added": 2,
    "unregistered_load_bearing": 0,
    "invalid_unknown": 0,
    "foreign_index_entries_preserved": 2
  },
  "rollback": {
    "instructions": "if the dry-run or live call fails, do not retry; preserve the receipt and file a failed report. After a committed but invalid postimage, use only a separately governed generation-bound reverse transaction.",
    "verification": "re-read declarations, projection, journal, plan, receipt, target hashes, HEAD, and real index; never repair by raw file or DB edits"
  },
  "hard_invariants": [
    "no third registry record is admitted",
    "the six consumed removals are not replayed or reversed",
    "evidence-only backing files are never edited or committed",
    "the foreign real-index pair remains byte-exact",
    "groundtruth.db is a governed operation target but not a Git include",
    "dispatcher and legacy TAFE state remain untouched"
  ],
  "fail_closed_conditions": [
    "new or changed load-bearing candidate",
    "registry generation or preimage drift after dry-run",
    "claim, GO, packet, PAUTH, or activity-envelope mismatch",
    "duplicate or widened batch record",
    "raw mutation or patch containment failure",
    "test, registry, index, or projection regression"
  ],
  "essential_context_preservation": "the revision preserves the successful six-identity transition, v004 truthfulness finding, exact current two-record gap, transactional API boundary, foreign index ownership, and terminal dependency for WI-6078"
}
```

## Risk And Rollback

The primary risk is concurrent registry drift between census, dry-run, and
apply. Every phase is generation-bound and must stop on drift. The live register
call is one-shot. No retry is authorized after an exception. If the call
commits but a postcondition fails, preserve all evidence and obtain a new
reviewed reverse-transaction carrier; never edit declarations or MemBase
directly.

## Owner Action Required

None. This revision is the exact corrective execution demanded by v004 under
the active whole-project PAUTH and the owner's standing instruction to carry
WI-6078 through genuine completion. It introduces no product choice or scope
tradeoff.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
