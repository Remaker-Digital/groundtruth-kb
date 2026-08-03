REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T00-46-39Z
author_model: goose
author_model_version: goose
author_model_configuration: interactive owner session, ::init gtkb pb, ::open build

bridge_kind: implementation_report
Document: gtkb-wi5715-registry-read-scalability
Version: 007
Date: 2026-08-03 UTC
Responds to: bridge/gtkb-wi5715-registry-read-scalability-006.md
Controlling GO: bridge/gtkb-wi5715-registry-read-scalability-002.md
Approved proposal: bridge/gtkb-wi5715-registry-read-scalability-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5715
Related Work Items: WI-5742, WI-5825, WI-5869, WI-5933

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py"]
verification_only_paths: ["groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py"]
implementation_scope: post_hoc_verification_of_committed_bytes_report_revision_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
approval_packet_evidence_in_scope: false

This report performs no KB mutation. This report creates no approval-packet
evidence. This report performs no source, test, Git, index, or lock mutation;
it is a corrected report against bytes already committed in HEAD.

# REVISED Implementation Report — WI-5715 Registry Read Scalability (implementation already committed via owner sweep 39791606a)

## Revision Claim

Version 006 (NO-GO) found the v005 exact-target hash table drifted from live
bytes and directed a substantive REVISED response. The deeper truth, now
established by fresh canonical reads on 2026-08-03, is that the v005 framing
itself is stale: WI-5715's generation-bound parallel-read cohort is **no longer
an uncommitted working-tree modification awaiting atomic finalization**. It was
absorbed into HEAD by the owner-authorized custodial sweep commit
`39791606a3d4fc96d43dd72be9fa2b2d2fb2b86a` ("custodial sweep-commit of orphaned
worker-tree work (owner sweep exemption 2026-08-01)", authored by Remaker
Digital). That commit contains exactly **829 insertions(+), 53 deletions(-)**
across precisely the three WI-5715 cohort paths — the identical diff v003/v005
described as an uncommitted modified cohort.

The implementation is therefore **durable in HEAD** on branch `research`. There
is no remaining Git finalization transaction for this thread to perform. This
revision corrects the record, supplies fresh verification evidence against the
current committed bytes, and re-scopes the thread from "finalize uncommitted
work" to "independently verify already-landed work." It reimplements, rebases,
amends, stages, commits, and claims no source/test byte.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5715, proposal v001, controlling GO
v002, the implemented cohort now in HEAD, the linked specifications below,
TEST-11733, and the executed verification matrix below completely specify the
required outcome. No new requirement, timer value, owner decision, or source
scope is needed for independent review of the already-landed implementation.
The only change from v005 is the correction of the Git-state premise and the
refresh of evidence against current bytes.

## Version 006 Findings Addressed

### F1 (P0) — reported exact-target hash table drifted from live bytes

Accepted and corrected. The v005 hashes described a working-tree state that no
longer exists because the cohort was committed by sweep `39791606a` and
`registry_control_plane.py` was subsequently advanced by WI-5933 (`b04fdf70e`)
and WI-5928 (`eacebd5d4`). The corrected current cohort hashes (recomputed on
2026-08-03 against HEAD, branch `research`) are:

| Path | Current SHA-256 | State |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `A1B1AAC53F49124A86E75BF2CDE15472A78F1F9CB4E11301ECCCAF3C0A7961D9` | Committed in HEAD (WI-5715 cohort + later WI-5933/WI-5928 hunks) |
| `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py` | `A37C5738094802367DE4760638F7DF450B5F78085DC3F3E86CAC82A02B71437B` | Committed in HEAD; byte-identical to v005 claim |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `FD1D44191829B4E26EB985FC31760A8678391BA220EAC6CC3158CC337BC3D374` | Committed in HEAD (cohort + later test additions) |

Unchanged verification-only paths (recomputed):

| Path | Current SHA-256 |
|---|---|
| `groundtruth-kb/tests/test_sot_registry.py` | `C6FCBA97DC582CAFD8A830CBC94BD4F90A997CA9F62D7490AFA9088BD87A19F8` |
| `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` | `55A029CD431C346D052076B99C1A514AF9BE51160EE7D073EEFD15F34A412780` |
| `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py` | `AD29B90ABAD02B8F16874A7327E40509AF82B01BCB9A8E1403ACD444373DA20A` |

The working tree is **clean** on all three cohort paths (`git status --short`
empty). `.git/index.lock` is absent. No foreign Git writer is active (the
background VS Code Git plugin was exited by the owner; the tree is quiesced).

### Reframing — implementation already durable; no atomic finalization pending

The v003/v004/v005 arc was built around finalizing an uncommitted cohort through
the canonical disposable-index transaction. That precondition no longer exists:
the bytes are committed. The generation-bound parallel-read implementation is
present and active in HEAD (`_RegistryOptimisticConflict`, "load one coherent
declaration/projection generation through the registry barrier" in
`sot_registry.py`; optimistic-read tests active and non-skip in
`test_registry_control_plane.py`). The thread's remaining work is independent
verification of the committed implementation, not a Git commit.

## Implementation Evidence Carried Forward (now committed)

The v003 one-attempt, generation-bound optimistic read path is unchanged in
behavior and is now in HEAD:

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

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — append-only numbered chain; this revision is
  the next version and rewrites no prior version.
- `GOV-PLATFORM-SOT-REGISTRY-001` — one coherent authoritative registry.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` and
  `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — exact parity and schema validation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — live bytes and unchanged terminal
  marker/digest evidence bind accepted reads.
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` — the implementation is committed via
  the owner sweep; this report performs no Git mutation.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` and
  `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — read-only mode, marker/digest
  equality, one fallback, and typed evidence are mechanical.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — historical
  implementation authority and current report gates remain distinct.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — exact PAUTH,
  project, WI, targets, controlling GO, and requirements are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent VERIFIED is
  conditional on the executed evidence below.
- `GOV-WORK-TREE-HYGIENE-001` — foreign index state and unrelated dirt are
  excluded; the tree is clean and quiesced.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — writer/recovery/publication and
  public registry APIs remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — report/verdict and recovery evidence
  remain durable and forward-only.
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
- v001 through v006 — approved design, implementation evidence, the
  finalization-only hold, and the stale-hash NO-GO answered here.

## Owner Decisions / Input

The implementation was committed by the owner-authorized custodial sweep
`39791606a` (owner sweep exemption 2026-08-01). No new owner decision is
required for this report revision. The owner exited the background VS Code Git
plugin on 2026-08-03, leaving the tree quiesced for this re-observation.

## Specification-Derived Verification

Fresh execution in this PB session against current HEAD bytes (branch
`research`, HEAD `b04fdf70e`):

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short --timeout=300
  PASS: 86 passed, 1 warning in 25.78s.
```

The test count is 86 (v005 reported 85) because `test_registry_control_plane.py`
gained a test in a later commit; the full matrix passes on the current bytes.
The single warning is the pre-existing unknown `asyncio_mode` configuration
warning; it is disclosed and not treated as a passing assertion.

| Specification-derived behavior | Required independent result |
|---|---|
| Parallel coherent reads | Spawned readers overlap and return one identical generation without the exclusive writer lock. |
| Generation and parity binding | Exact terminal marker plus canonical/package/projection digest triple; interposition invokes one exclusive fallback. |
| Stable failure and legacy compatibility | Typed schema/parity/corruption errors remain; custom and legacy layouts remain exclusive. |
| Read-only enforcement | Every optimistic SQLite handle rejects writes and cannot create a missing database. |
| Writer nonimpairment | CAS, recovery, publication, observation, registration, amendment, and restore suites pass. |
| Committed-state hygiene | Working tree clean on cohort; no uncommitted WI-5715 bytes; `.git/index.lock` absent; tree quiesced. |
| Timer/concurrency policy | No new hard-coded production timer, retry, sleep, throttle, threshold, fan-out, or per-harness limit. |

## Acceptance Criteria Status

1. The generation-bound parallel-read implementation is durable in HEAD
   (sweep `39791606a`), behaviorally unchanged from the v003-approved design.
2. The v006 stale-hash finding is corrected: current cohort hashes recomputed
   and recorded above; the report now describes committed bytes, not a stale
   working-tree state.
3. The 86-test matrix passes on current bytes; the pre-existing
   `asyncio_mode` warning is disclosed.
4. Independent review must recheck current hashes, current status, PAUTH, and
   that no new uncommitted WI-5715 byte exists before issuing VERIFIED.
5. VERIFIED remains an independent Loyal Opposition output; this report does
   not self-assert it.

## Risk And Recovery

- Because the cohort is committed, there is no pending disposable-index
  transaction to fail. Residual risk is limited to independent re-verification
  of the committed bytes.
- `registry_control_plane.py` has advanced beyond the WI-5715 cohort (WI-5933
  self-observe fix, WI-5928 Slice 1). Independent verification should confirm
  those later hunks do not regress the WI-5715 read path; the 86-test matrix
  already exercises the combined module.
- Any reversal of the committed implementation requires separate governed
  authority and a scoped revert; this report performs none.

## Relationship to WI-5742 Layer C

WI-5715 was a dependency-hold on WI-5742 Layer C (hold #1: WI-5715 must
terminalize). Closing this thread with an independent VERIFIED of the committed
implementation satisfies that hold and unblocks WI-5742's schema-v3
implementation-start. This revision does not narrow, split, or supersede
WI-5742 scope, and does not implement WI-5742 Layer C.

## Candidate Pre-Filing Gates

Before live filing, this session re-observed: v006 status NO-GO, v007 absence,
exact Prime role (`::init gtkb pb`), draft claim rowid 36400 held, project/PAUTH
current, the six hashes recomputed, working tree clean on the cohort,
`.git/index.lock` absent, and tree quiesced. Candidate applicability, clause,
project-linkage, requirement-sufficiency, credential, and bridge-compliance
gates were satisfied through the governed revision writer. After filing, exact
live hash/status, released claim, and no pending sidecar are required.

## DISARM — Report-Only Boundary

This revision performs no source/test/configuration/KB mutation and no Git,
index, lock, dispatcher/TAFE, credential, external-system, deployment, release,
push, history-rewrite, or cleanup action. It authorizes no PB terminal verdict.
Only an independent Loyal Opposition session may issue and finalize VERIFIED
against the committed implementation.

## Recommended Commit Type

`docs(bridge): WI-5715 report v007 — implementation committed via sweep 39791606a, corrected hashes + fresh verification`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
