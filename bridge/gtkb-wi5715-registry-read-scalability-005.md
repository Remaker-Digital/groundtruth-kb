REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; report-only finalization recovery; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: current_interactive_session_context

bridge_kind: implementation_report
Document: gtkb-wi5715-registry-read-scalability
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5715-registry-read-scalability-004.md
Controlling GO: bridge/gtkb-wi5715-registry-read-scalability-002.md
Approved proposal: bridge/gtkb-wi5715-registry-read-scalability-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5715
Related Work Items: WI-5675, WI-5717, WI-5742, WI-5783, WI-5825, WI-5869

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py"]
verification_only_paths: ["groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py"]
implementation_scope: source_and_test_report_revision_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_packet_evidence_in_scope: false

This report performs no KB mutation. This report creates no approval-packet evidence.

# REVISED Implementation Report — WI-5715 Registry Read Scalability Finalization Recovery

## Revision Claim

No implementation byte changed after v003. Version 004 independently found the
three-target generation-bound read implementation technically sufficient for a
future VERIFIED verdict and blocked only because a foreign `.git/index.lock`
made atomic finalization unsafe. The lock is now absent without any action by
this session. The exact implementation and verification hashes remain identical
to v003/v004, and the complete 85-test matrix and static checks pass again.

This version responds forward to v004, declares the exact controlling GO, and
enumerates every required finalizer include path. It does not reimplement,
rebase, amend, stage, commit, or claim any source/test byte. Loyal Opposition
must independently reverify and may finalize only while the real index remains
available and the exact cohort is unchanged.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5715, proposal v001, controlling GO
v002, implementation report v003, independent v004 findings, the nineteen
linked specifications, TEST-11733, and the executed matrix below completely
specify the implementation and finalization outcome. No new requirement,
timer value, owner decision, or source scope is needed. A reappearing foreign
index lock or any byte drift is an operation-time hold, not permission to
weaken the finalizer.

## Version 004 Finding Addressed

### F1 — foreign real-index lock prevented the required atomic finalizer

Accepted. Version 004 did not reject the implementation. It found that the
canonical finalizer creates a disposable candidate index and then realigns the
real index, so removing or bypassing a foreign lock would be unsafe.

Fresh readback on 2026-08-01 found `.git/index.lock` absent. This session did
not delete, rename, truncate, replace, or otherwise act on the lock. Several
long-lived Git processes remain foreign and are not killed or adopted; absence
of the lock is rechecked immediately before live report filing and must be
rechecked again by the independent finalizer.

If the lock reappears, the correct outcome is another typed hold with exact
owner/process evidence. No `--no-verify`, shared-index cleanup, lock deletion,
manual staging, or partial finalization is authorized.

## Implementation Evidence Carried Forward

The v003 implementation remains the approved one-attempt, generation-bound
optimistic read path:

- terminal journal evidence and exact canonical/package/projection digests bind
  every accepted optimistic generation;
- marker change, nonterminal/incomplete state, or unprovable coherence invokes
  the unchanged exclusive path exactly once;
- stable typed body errors are preserved;
- optimistic SQLite handles are `mode=ro` and `query_only` and reject writes;
- custom/noncanonical registry layouts preserve the exclusive compatibility
  path; and
- writers, recovery, observation, publication, CAS, registration, amendment,
  and projection writes remain exclusively locked.

No cache, daemon, loop, timer, retry counter, sleep, throttle, threshold,
fan-out, queue capacity, or per-harness concurrency value was added.

## Exact Current Cohort

### Changed implementation paths

| Path | SHA-256 | Current state |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `A063E0CB057FACFC86D077360B02EB9805A1EB516C7CE16CCED0B472D06C3006` | Modified, exact v003/v004 WI-5715 cohort |
| `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py` | `A37C5738094802367DE4760638F7DF450B5F78085DC3F3E86CAC82A02B71437B` | Modified, exact v003/v004 WI-5715 cohort |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `FDA19AED075D4D397BF7A97556CB4395D6EA97324012DA08A8E39BE327349073` | Modified, exact v003/v004 WI-5715 cohort |

Exact diff remains 829 insertions and 53 deletions across only these three
implementation paths. No staged diff exists for this cohort.

### Unchanged verification-only paths

| Path | SHA-256 |
|---|---|
| `groundtruth-kb/tests/test_sot_registry.py` | `C6FCBA97DC582CAFD8A830CBC94BD4F90A997CA9F62D7490AFA9088BD87A19F8` |
| `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` | `55A029CD431C346D052076B99C1A514AF9BE51160EE7D073EEFD15F34A412780` |
| `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py` | `AD29B90ABAD02B8F16874A7327E40509AF82B01BCB9A8E1403ACD444373DA20A` |

These three files are finalizer includes and executed evidence, not WI-5715
mutations. They must remain byte-identical and produce no commit diff.

## Implementation Path Set

The independent VERIFIED finalizer must declare every path below with its
`--include` mechanism. Inclusion is transaction inventory, not authorization
to alter unchanged evidence:

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`
- `groundtruth-kb/tests/test_registry_control_plane.py`
- `groundtruth-kb/tests/test_sot_registry.py`
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py`
- `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py`
- `bridge/gtkb-wi5715-registry-read-scalability-001.md`
- `bridge/gtkb-wi5715-registry-read-scalability-002.md`
- `bridge/gtkb-wi5715-registry-read-scalability-003.md`
- `bridge/gtkb-wi5715-registry-read-scalability-004.md`
- `bridge/gtkb-wi5715-registry-read-scalability-005.md`

Versions v001 through v004 are currently untracked append-only predecessors,
so the final transaction must include them with this revised report and the
new independent VERIFIED verdict. The final commit must contain no unrelated
staged or working-tree path. Unchanged verification-only paths may appear in
the include set but must not appear as changed commit entries.

## Durable Operation-Time Authorization Evidence

No new implementation operation occurred. The controlling evidence remains:

- GO implementation claim row `36004`, acquired by the v003 implementation
  author session `019f9b59-52a0-75b2-9973-bd5601f98e9f`;
- final schema-v3 packet
  `sha256:bddb3ac66064e4c36df0f4a738b4aa9e96b005d2f74709b41500a60c23041e89`;
- proposal SHA-256
  `aa9c2e8126babf9750f0aff06a1fee2f9e052153dba28e73de7e3a14ddf03197`;
  and
- GO SHA-256
  `4d36192cedd48fe96a5ef457c29e683cf7c4fc8e91d38e988322b555599f65da`.

The historical claim and packet prove `live_at_implementation`; they are not
reused as live authority for new edits. This report filing uses only a fresh
draft claim. Independent review/finalization requires its own fresh LO review
claim and exact current preflight/finalizer evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only numbered chain and atomic
  terminal publication/finalization.
- `GOV-PLATFORM-SOT-REGISTRY-001` — one coherent authoritative registry.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` and
  `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — exact parity and schema validation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — live bytes and unchanged terminal
  marker/digest evidence bind accepted reads.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — exact disposable-index transaction,
  clean real-index reconciliation, and scoped commit.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` and
  `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — read-only mode, marker/digest
  equality, one fallback, and typed evidence are mechanical.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — historical
  implementation authority and current report/finalizer gates remain distinct.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — exact PAUTH,
  project, WI, targets, controlling GO, and requirements are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent VERIFIED is
  conditional on the executed evidence below.
- `GOV-WORK-TREE-HYGIENE-001` — foreign processes/index state and unrelated
  dirt remain excluded.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — writer/recovery/publication and
  public registry APIs remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — proposal/report/verdict and recovery
  evidence remain durable and forward-only.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths remain inside GT-KB.

## Prior Deliberations

- `DELIB-202667517` and
  `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT` — useful
  parallel readers without a platform-wide leader.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — generous runtime
  and exact re-observation under contention.
- `DELIB-20260801-GTKB-TIMER-CONCURRENCY-CONFIG-SOT-DIRECTIVE`,
  `DELIB-202667722`, and `DELIB-202667748` — hard-coded timer/concurrency
  policy is removed and centrally tuned from evidence; WI-5715 adds none.
- `DELIB-202667721` — list-free Housekeeping Hardening project authority.
- v001 through v004 — approved design, implementation evidence, and the exact
  finalization-only hold answered here.

## Owner Decisions / Input

No new owner decision is required. The owner-approved project PAUTH and prior
parallelism/timer decisions remain sufficient. The foreign lock cleared without
our intervention; this report does not infer permission to manipulate it if it
reappears.

## Specification-Derived Verification

Fresh execution in this PB session:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short --timeout=300
  PASS: 85 passed, 1 warning in 58.76s.

groundtruth-kb\.venv\Scripts\ruff.exe check <three implementation paths>
  PASS: All checks passed.

groundtruth-kb\.venv\Scripts\ruff.exe format --check <three implementation paths>
  PASS: 3 files already formatted.

git diff --check -- <three implementation paths>
  PASS; existing LF-to-CRLF working-copy advisory only.
```

| Specification-derived behavior | Required independent result |
|---|---|
| Parallel coherent reads | Spawned readers overlap and return one identical generation without the exclusive writer lock. |
| Generation and parity binding | Exact terminal marker plus canonical/package/projection digest triple; interposition invokes one exclusive fallback. |
| Stable failure and legacy compatibility | Typed schema/parity/corruption errors remain; custom and legacy layouts remain exclusive. |
| Read-only enforcement | Every optimistic SQLite handle rejects writes and cannot create a missing database. |
| Writer nonimpairment | CAS, recovery, publication, observation, registration, amendment, and restore suites pass. |
| Git lifecycle and hygiene | Exact include set, absent real-index lock, no unrelated staged paths, and one atomic commit containing the complete untracked chain. |
| Timer/concurrency policy | No new hard-coded production timer, retry, sleep, throttle, threshold, fan-out, or per-harness limit. |

The Pytest warning is the existing unknown `asyncio_mode` configuration warning;
it is disclosed and not treated as a passing assertion.

## Acceptance Criteria Status

1. All twelve implementation criteria from v003 remain met without byte drift.
2. V004's sole foreign-index-lock blocker is currently absent and was not
   manipulated by this session.
3. The complete six-file implementation/verification inventory and all five
   untracked predecessor/report files are explicit finalizer includes.
4. The 85-test matrix, Ruff check, Ruff format check, and diff check pass.
5. Independent review must recheck lock, hashes, current status, PAUTH, report
   claims, full include set, and staged-path closure immediately before finalization.
6. VERIFIED is withheld if any lock, path, hash, test, authority, claim,
   receipt, publication, or finalizer condition is ambiguous.

## Risk And Recovery

- The foreign Git processes may recreate the index lock. Preserve it and stop;
  never delete or race it.
- Registry marker payload size and lock contention remain observable costs.
  Route new measurements to WI-5715/WI-5869 and the central SoT-access advisory;
  do not hide them behind a local bound.
- If finalization fails after publication or commit preparation, preserve exact
  file/capability/receipt/claim evidence and follow the WI-5742/WI-5825/WI-5881
  forward-recovery contracts. Do not manually repair the numbered chain.
- Before a durable commit, rollback is no new action: keep the exact source
  cohort and append-only reports for another independent review. After commit,
  any reversal requires separate governed authority and a scoped revert.

## Candidate Pre-Filing Gates

Before live filing, reobserve v004 status/hash, v005 absence, exact Prime role,
null claim, project/PAUTH, six hashes, three-path diff, index-lock absence, and
no staged cohort path; run candidate applicability, clause, requirement,
credential, and bridge-compliance gates; publish only through the governed
revision writer. After filing, require exact live hash/status, released claim,
and no pending sidecar. Timeout is not failure; reobserve before retry.

## DISARM — Report-Only Boundary

This revision performs no source/test/configuration/KB mutation and no Git,
index, lock, dispatcher/TAFE, credential, external-system, deployment, release,
push, history-rewrite, or cleanup action. It authorizes no PB terminal verdict.
Only an independent Loyal Opposition session may issue and atomically finalize
VERIFIED after every condition above passes.

## Recommended Commit Type

`feat(registry): add generation-bound parallel reads`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
