REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fbf41-5d5e-74f3-b6f4-1ae7258c299c
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop Prime Builder worker; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: explicit delegated session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5806-operational-control-config-foundation
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5806-operational-control-config-foundation-004.md
Withdrawn historical GO: bridge/gtkb-wi5806-operational-control-config-foundation-002.md

Project Authorization: PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-TIMER-GOVERNANCE
Work Item: WI-5806
Related Work Items: WI-5441, WI-5510, WI-5596, WI-5610, WI-5611, WI-5696, WI-5700, WI-5804, WI-5805, WI-5819, WI-5849, WI-5909

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "config/governance/operational-controls.toml", "groundtruth-kb/tests/test_operational_control_config.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]
registry_admission_paths: ["groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py", "groundtruth-kb/tests/test_operational_control_config.py"]
implementation_scope: bounded_adoption_plus_governed_two_record_registry_admission
requires_review: true
requires_verification: true
kb_mutation_in_scope: true
dispatcher_or_tafe_mutation_in_scope: false
runtime_activation_in_scope: false

# WI-5806 REVISED Proposal — Typed Operational-Control Foundation With Atomic Registry Admission

## Revision Claim

Replace the withdrawn three-target contract with one exact six-target governed
transaction. Preserve the already-created source, catalog, and focused-test
postimages as evidence and adopt them only after a fresh independent GO. Admit
the source and test through the canonical `gt registry register` service in the
same governed implementation transaction. The catalog receives no redundant
exact record because active recursive record `governance-config-tree` already
covers it.

The typed operational-control design from v001 remains unchanged: a closed,
immutable Decimal-based schema; an initially empty production definition
catalog; no import-time reads; one root `.env.local` snapshot retaining only
declared names; rejection of empty, malformed, secret-class, stale, unbound, or
out-of-range present values; one-snapshot invariant closure; and zero meaning
disable for capacity, fan-out, and live-worker controls. No existing consumer,
timer configuration, environment file, dispatcher, or TAFE surface changes in
this foundation slice.

## Findings Addressed

### P0 — The original three-target registry contract was impossible

Accepted. V001 disclosed 22 `unregistered_load_bearing` paths and required
non-increase, while v002 prohibited registry-declaration work. Fresh canonical
validation still reports `coherent=true`, `valid=false`, and 24 load-bearing
gaps. The two additions are exactly:

1. `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`;
2. `groundtruth-kb/tests/test_operational_control_config.py`.

The catalog is not a third gap because `governance-config-tree` covers
`config/governance/operational-controls.toml` recursively. V005 therefore adds
both registry declaration projections and service-managed `groundtruth.db` to
the persistent target cohort, sets `kb_mutation_in_scope: true`, and binds the
registry batch to only the two exact candidates. Direct declaration edits and
raw SQLite writes remain prohibited.

### P2 — Existing implementation bytes are evidence, not terminal authority

Accepted. The three untracked postimages were created by prior Prime Builder
session `019fb19b-7814-73c1-8707-204e432cbf00` under the now-withdrawn v002
GO. They remain byte-identical and otherwise green, but neither their bytes nor
the expired start packet grant present implementation or verification
authority. V005 authorizes no mutation by itself. Future adoption or revision
requires a fresh independent GO, exact current claim, fresh schema-v3 packet,
OPS envelope for registry work, and exact preimage/currentness checks.

## Exact Scope And Current Preimages

| Path | Current state and SHA-256 | V005 disposition |
| --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py` | untracked postimage; `908C51A39BF3D62BA116C5E4EA8139B8FD7028C1CDBD999425B8BBE509343695` | Preserve and adopt after GO unless fresh review requires an explicit bounded correction. Exact registry record required. |
| `config/governance/operational-controls.toml` | untracked postimage; `1F6442E130D111A2C5AA298521D22E7DA75EC235BA4F2AEFE90FC97EE9288EDB` | Preserve. Already covered by `governance-config-tree`; no redundant exact record. |
| `groundtruth-kb/tests/test_operational_control_config.py` | untracked postimage; `906B09DF1B02FBE5D4F39DE7C59ECEE3EBAE91E8C3880751877DD21B25DF4E65` | Preserve and adopt after GO unless fresh review requires an explicit bounded correction. Exact registry record required. |
| `config/registry/sot-artifacts.toml` | clean; `8A45F90954CD0AF9F026A1A7884AC2E499EC54A768080FC4D04FF84AD853FB44` | Canonical CLI-managed declaration projection only. |
| `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` | clean and byte-identical; `8A45F90954CD0AF9F026A1A7884AC2E499EC54A768080FC4D04FF84AD853FB44` | Canonical CLI-managed packaged projection only. |
| `groundtruth.db` | dynamic service-managed SoT; 862,396,416 bytes at the latest candidate read | Registry projection/revision/journal/receipt row cohort only; never a Git include. A whole-file digest is deliberately not asserted as a fixed precondition because lawful concurrent writers and proposal publication change this SoT. |

The current draft claim is row 36252 under this author session. Governed
proposal publication is expected to release it. Before any future protected
mutation, every path, registry generation, candidate manifest, current claim,
project/PAUTH input, overlap, and foreign-dirty attribution is re-read. Drift
stops the implementation cycle and requires a reviewed revision or exact hunk
ledger; it is never silently adopted.

## Requirement Sufficiency

Existing requirements sufficient. V004 identifies the missing registry
transaction and exact six-target correction. The original operational-control
requirements, current Timer Governance project, TEST-11821, registry governance,
and active list-free PAUTH fully constrain this correction. No new owner choice,
production control value, dispatcher authority, or runtime migration is needed.

## Specification Links

- `GOV-ENV-LOCAL-AUTHORITY-001` and `ADR-ENV-SOT-TOPOLOGY-001` — root `.env.local` remains the sole live platform-value authority; checked-in TOML contains only schema, defaults, units, bounds, and invariants.
- `DCL-ENV-CLI-ENFORCEMENT-001` — future schema writes and consumer migrations remain governed by `gt env`; this foundation supplies only the bounded read model.
- `GOV-SOT-SINGLETON-001` — no raw process environment or second persistent live-value store is introduced.
- `GOV-PLATFORM-SOT-REGISTRY-001` v3 — new load-bearing source/test artifacts receive active registry membership in the same governed implementation transaction.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` v2 — registration uses the canonical CLI in an OPS envelope, with lock, journal, recovery, and receipt evidence; no direct TOML or raw database mutation.
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — both exact candidate records retain the closed canonical schema.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` — canonical declaration, packaged declaration, projection, journal, and receipt remain one coherent generation.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — one deterministic parser/resolver and one deterministic registration service replace local interpretation and manual registry edits.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — exact catalog, environment snapshot, claims, PAUTH, candidate manifest, generation, and receipt are read at their operation boundaries.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — every asserted behavior has executable evidence and failures remain visible.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — WI-5806 removes its two added registry gaps and admits no unrelated candidate.
- `GOV-STANDING-BACKLOG-001` — WI-5806 and TEST-11821 remain the durable work and verification carriers.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — preserve the withdrawn authority, correction, implementation, registry receipt, report, and later terminal evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH never replaces independent GO, exact claim, fresh start, or formal registry transaction evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — proposal, project authority, and executed evidence remain mechanically linked.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — role-correct append-only lifecycle, independent review, and exact implementation authority remain mandatory.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and authority evidence remain inside `E:/GT-KB`.
- `GOV-10`, `GOV-12`, `SPEC-1662`, and `GOV-15` — behavior is exercised through public interfaces with focused regression coverage, bounded side effects, and no dispatcher/TAFE or external-system action.

## Prior Deliberations

- `DELIB-202667722` — centralized, relaxed-first timer and throttle governance.
- `DELIB-202667748` — widened operational-control scope and recurring evidence-driven tuning.
- `DELIB-202667725` — current list-free Timer Governance whole-project authorization, preserving every per-WI lifecycle gate.
- `DELIB-202667517` — highly parallel Prime Builder operation with only short irreducible critical sections.
- V001 through v004 on this bridge are the exact proposal, withdrawn GO, PB authority correction, and corrected NO-GO evidence.

## Owner Decisions / Input

No new owner input is required. WI-5806 is an active member of
`PROJECT-GTKB-TIMER-GOVERNANCE` and inherits implementation approval through
current PAUTH `PAUTH-PROJECT-GTKB-TIMER-GOVERNANCE-WHOLE-PROJECT-20260730`
v2. Legacy `work_item.approval_state` is not operation-time authority. The
fresh GO, exact claim, schema-v3 start, OPS-envelope registry transaction,
implementation report, and independent verification gates remain mandatory.

## Preserved Operational-Control Contract

1. Production catalog schema is closed at v1 and starts with zero definitions.
   A later consumer adds its definition and switches its read in one separately
   governed cycle after a valid non-secret `gt env` schema binding exists.
2. Models and returned snapshots are immutable. Integer/Decimal parsing has
   explicit units, inclusive bounds, precision and magnitude bounds, closed
   zero semantics, and no Boolean/NaN/infinity/untyped-string acceptance.
3. Production loading reads exact root-bound regular files once. It never
   follows symlinks, imports a global catalog, reads raw `os.environ`, or
   accepts caller mappings as production authority.
4. The `.env.local` snapshot retains only declared control names. A present
   empty, whitespace, malformed, stale, secret-class, cross-scope, unbound, or
   out-of-range value fails closed and never falls back to a default.
5. All coupled controls resolve and validate from one catalog/environment
   snapshot using the closed relation vocabulary. Split snapshots, incompatible
   kinds/units, missing endpoints, invalid margins, and contradictory relations
   fail closed.
6. Capacity, fan-out, and live-worker definitions have `zero_semantics =
   "disable"`; absent applicable capacity is not treated as unlimited.
7. No existing consumer, `timer_config.py`, protected-commit configuration,
   dispatcher rules/runtime, environment file, TAFE state, or daemon state is
   changed by this foundation.

## Exact Registry Transaction

Fresh `gt registry reconcile --json` currently reports 24 admission candidates
against generation
`sha256:1648ec387957a95bc236f0e1e2f22c3cd10e16e032ffe7a2360d808d7e1e9ed1`,
candidate manifest
`sha256:00c0c05dbbbadd6fb1d2b4a3ad8fbd921d53c95f54a84028f14315b781f9cbf1`,
and reconciliation evidence
`sha256:d799782eaa32b4daf86508dc5cd7eda7d40748a343ee08482c2567dc8cf1daee`.
These are observation-only preimages and must be refreshed at start.

Select exactly these two candidate records and no third:

| Record ID | Storage path | Domain |
| --- | --- | --- |
| `wi5441-member-groundtruth-kb-src-groundtruth-kb-project-operat-c13eb20ed0` | `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py` | `control_surface` |
| `wi5441-member-groundtruth-kb-tests-test-operational-control-co-e67024a962` | `groundtruth-kb/tests/test_operational_control_config.py` | `governance_policy` |

An OPS-envelope Prime Builder performs only this sequence after all start gates:

1. Reconcile and bind the exact generation, two candidate records, candidate
   manifest, observer input digests, and reconciliation evidence digest.
2. Create an exact in-root two-record batch without writing either declaration.
3. Run `gt registry register --batch-file <batch> --dry-run` with the exact
   bridge, OPS session, current packet hash, active PAUTH, actor, and reason.
4. Apply the identical batch using the exact dry-run receipt and unchanged
   authority/preimage fields.
5. Canonically read back both records, both declarations, projection identity,
   journal/transaction receipt, and reverse coverage before any report.

Direct TOML edits, raw SQLite writes, broad reconcile application, unrelated
candidate cleanup, ad hoc projection sync, blind retry, or manual lock removal
are prohibited.

## Concurrency And Sequencing

WI-5909 is currently NEW v001 and not terminal. The preferred route waits for
independently VERIFIED WI-5909 row-cohort reservations so the registry operation
does not reserve all of `groundtruth.db`. If WI-5909 remains unavailable, a
future independent GO on these exact v005 bytes may explicitly accept the
current whole-database compatibility reservation only under this short-boundary
contract: finish every read-only candidate/test/preflight step first; acquire
the six-target claim at the last responsible moment; hold it only across exact
dry-run, apply, canonical readback, and report publication; and release it
immediately afterward. This is not global serialization or a MemBase leader.

`.git/index.lock` is absent on the current targeted read. Its state is checked
again before implementation and finalization. If a foreign lock exists, stop
and preserve it for WI-5819/WI-5849 or another governed owner; never delete,
rename, overwrite, or attribute it to WI-5806. No Git/index operation is
authorized during proposal filing or registry preparation.

An exact physical-latest `target_paths` scan currently finds 13 external
nonterminal chains overlapping the six-path cohort: five GO, three REVISED,
three NEW, one NO-ACTION, and one NO-GO. Twelve overlap only the current
whole-file `groundtruth.db` reservation; one overlaps `groundtruth.db` plus the
canonical declaration. No external chain declares either WI-5806 source/test
path or its catalog path. The canonical cross-claim collision function returns
`None` for this exact six-path cohort and author session. This is filing-time
evidence only. Every external head, valid packet, and active claim is re-read at
future start; any live collision waits or uses independently verified WI-5909
row-cohort semantics rather than being bypassed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5806, TEST-11821, v004 NO-GO, DELIB-202667722, DELIB-202667748, DELIB-202667725, and the active Timer Governance PAUTH",
  "canonical_authority": "Root .env.local owns live platform values; the checked-in operational-control catalog owns typed non-secret definitions; the SoT registry service owns membership and declaration projection",
  "primary_route": "load_operational_control_catalog plus load_platform_control_environment_snapshot plus resolve_operational_controls; gt registry reconcile/register for exact artifact admission",
  "before_behavior": "The three-target implementation is otherwise green but adds two unregistered load-bearing source/test artifacts and therefore cannot satisfy the withdrawn non-regression contract",
  "after_behavior": "The same typed foundation remains non-consuming while exactly its source and test gain active registry membership through one recoverable two-record transaction",
  "self_descriptive_naming": "operational_control_config names the full timer, retry, threshold, fan-out, and concurrency control class; both registry record IDs are deterministic path-derived identifiers",
  "obsolete_guidance_disposition": "The withdrawn three-target GO and no-registry-edit condition remain historical evidence and are not used as current authority",
  "history_preservation": "All numbered bridge versions, the withdrawn GO, registry journal and receipt, and later report/verdict remain append-only evidence",
  "baseline": {
    "production_control_definitions": 0,
    "existing_consumers_changed": 0,
    "unregistered_load_bearing": 24,
    "wi5806_added_gaps": 2,
    "registry_projection_sha256": "8A45F90954CD0AF9F026A1A7884AC2E499EC54A768080FC4D04FF84AD853FB44"
  },
  "expected_result": {
    "registry_records_added": 2,
    "wi5806_gaps_removed": 2,
    "unrelated_registry_candidates_added": 0,
    "catalog_exact_record_added": false,
    "dispatcher_or_tafe_mutation": false
  },
  "rollback": {
    "registry": "use the canonical recoverable registry journal to restore one coherent prior declaration and projection generation",
    "implementation": "revert only the exact source, catalog, and test adoption under separate reviewed authority",
    "history": "retain every bridge, journal, receipt, report, and verdict artifact"
  },
  "hard_invariants": [
    "root .env.local remains the only live platform-value authority",
    "the production catalog remains initially empty and no existing consumer changes",
    "exactly two registry records are admitted and both declaration projections stay byte-identical",
    "groundtruth.db is service-managed and excluded from Git",
    "no dispatcher, TAFE, environment, credential, deployment, release, or external-system mutation occurs"
  ],
  "fail_closed_conditions": [
    "target, claim, packet, project, PAUTH, bridge head, OPS envelope, candidate manifest, generation, receipt, or lock drift",
    "selection of any registry candidate other than the exact source and test records",
    "direct declaration or SQLite mutation",
    "mixed registry generation, projection mismatch, new unrelated gap, or nonzero invalid_unknown"
  ],
  "essential_context_preservation": "The foundation keeps all original typed parsing, bound, invariant, provenance, zero-disable, no-import-read, and non-consuming requirements while adding only the registry authority that v004 proved mandatory"
}
```

## Specification-Derived Verification Plan

| Requirement | Exact executable evidence |
| --- | --- |
| Typed catalog, parsing, bounds, one-snapshot invariants, path safety, and no import-time read | Run all 29 focused TEST-11821 tests against the exact preserved/reviewed source/catalog/test bytes. |
| Python quality | Run Ruff check, Ruff format check, and in-memory compile on source and test; all exit zero. |
| Registry candidate authority | Fresh reconcile; compare exact generation, manifest, observer digests, evidence digest, and two selected records; fail on any third record. |
| Dry-run/apply binding and recovery | Run the focused registration preview, generation/authority binding, dual-declaration transaction, fault-phase atomicity, idempotent retry, and CLI mutation-denial tests cited by v003/v004. |
| Exact registry membership | `gt registry show` both record IDs; verify exact storage paths, domains, coverage, authority, ownership, mutation API, backup/restore, and versioning fields. |
| Declaration/projection parity | Verify both declaration hashes equal; run `gt registry inspect --no-census --json`; require a coherent current identity and exactly two new records. |
| Nonimpairment | Compare immediate pre/post `gt registry validate --json`; remove both WI-5806 paths from the gap set, add no WI-5806 or unrelated gap, keep `invalid_unknown=0`, and disclose unrelated pre-existing debt. |
| Authority/currentness | Revalidate strict GO, exact claim, schema-v3 six-target packet, OPS session, PAUTH v2, target hashes, overlap heads, WI-5909 disposition, and lock state before mutation. |
| Finalization containment | Five Git-backed targets only in the later finalizer include set; `groundtruth.db` remains service-managed and excluded; no dispatcher/TAFE, environment, credential, deployment, release, or external mutation. |

Fresh pre-filing read-only evidence on the three implementation postimages is:

- focused tests: **29 passed** in 0.79 seconds;
- Ruff check: **All checks passed**;
- Ruff format: **2 files already formatted**;
- compile: passed.

These results support review but do not claim implementation verification.
They must be rerun after any future authorized delta and before the report.

## Acceptance Criteria

1. The three preserved postimages remain byte-identical or any necessary delta
   is separately visible, exact, GO-authorized, tested, and reported.
2. The production catalog remains schema-only with zero active definitions;
   no current control value, consumer, environment file, or runtime changes.
3. Exactly the two declared candidate records are registered through one
   canonical OPS-envelope transaction; no catalog record or unrelated candidate
   is added.
4. Canonical and packaged declaration files remain byte-identical and current;
   registry projection, journal, receipt, and generation are coherent.
5. The two WI-5806 paths leave `unregistered_load_bearing`; the post-minus-pre
   gap set is empty, `invalid_unknown` remains zero, and unrelated debt is
   disclosed rather than attributed or cleaned up.
6. Focused tests, registry atomicity/recovery tests, lint, format, compile,
   exact target/currentness checks, applicability, clause, collision, and
   independent verification gates all pass.
7. WI-5909 sequencing or the explicitly accepted short whole-database
   compatibility boundary is recorded before implementation start.
8. No direct registry declaration/SQLite mutation, Git/index manipulation,
   dispatcher/TAFE activation, credential action, deployment, release,
   destructive cleanup, or external-system mutation occurs.

## Pre-Filing Preflight Subsection

The completed candidate must pass immediately before filing:

- strict lifecycle currentness on exact v004 NO-GO and predecessor SHA;
- active project membership and list-free PAUTH v2 operation-time evaluation;
- exact target/currentness and six-path overlap/claim collision checks;
- applicability with no blocking errors or missing required/advisory specs;
- mandatory clause gate with no blocking gaps;
- proposal pattern lint and WI relationship/collision validation;
- role-correct author envelope, exact draft claim, credential/compliance gate,
  and governed writer publication with canonical readback.

## Risk And Rollback

The main residual risk is the multi-SoT registry transaction under contention.
Mitigations are the canonical OPS service, exact two-record batch, generation
and receipt binding, short critical section, old-or-new coherent fault contract,
and WI-5909 preference. Target, claim, packet, candidate, generation, lock, or
authority drift stops before mutation.

Proposal rollback never deletes append-only bridge history. After a future GO,
implementation rollback uses the registry service's recoverable journal to
restore a coherent prior declaration/projection generation and separately
reverts only the exact source/catalog/test adoption under new authority. It
must not touch unrelated registry entries, foreign changes, dispatcher/TAFE,
environment files, credentials, deployment, release, or the Git index lock.

## Files Expected To Change After Future GO

- `groundtruth-kb/src/groundtruth_kb/project/operational_control_config.py`
- `config/governance/operational-controls.toml`
- `groundtruth-kb/tests/test_operational_control_config.py`
- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth.db` (service-managed registry rows only; excluded from Git)

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
