NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive; Prime Builder; build activity
author_metadata_source: open session envelope and current transcript

# GT-KB Bridge Implementation Report — WI-5715 Registry Read Scalability

bridge_kind: implementation_report
Document: gtkb-wi5715-registry-read-scalability
Version: 003
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5715-registry-read-scalability-002.md
Approved proposal: bridge/gtkb-wi5715-registry-read-scalability-001.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project Authorization Version: 2
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5715
Related Work Items: WI-5675, WI-5717, WI-5783, WI-5825
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This implementation report performs no MemBase mutation. It also performs no
project, PAUTH, dispatcher, external-system, credential, deployment, release,
or Git-history mutation.

## Implementation Claim

Implemented the approved one-attempt generation-bound read fast path for the
authoritative SoT registry:

- A read-only SQLite marker snapshot rejects optimistic eligibility when any
  nonterminal journal row exists. The latest terminal row binds committed state
  to its `new_*` digest triple and aborted state to its `old_*` triple.
- Canonical TOML is parsed from the exact byte payload that is hashed. The
  canonical, packaged, and logical projection digests must match one unchanged
  terminal marker before an optimistic result is accepted.
- Optimistic SQLite handles use URI `mode=ro`, `uri=True`, and mechanically
  verified `PRAGMA query_only=ON`; they cannot create a missing database or
  perform DDL/DML.
- The marker is reread after successful and exceptional bodies. An unchanged
  marker preserves the original typed exception by bare re-raise. A changed,
  nonterminal, missing, incomplete, or unreadable post-state emits one internal
  conflict signal.
- `load_registry_snapshot`, `load_toml`, and `load_projection` catch that
  signal at their bounded boundary and invoke the existing exclusive reader
  exactly once. No loop, cache, sleep, retry counter, production timeout,
  throttle, daemon, or configuration surface was added.
- Only the root's exact canonical/package/database layout is eligible for the
  optimistic path. Custom and standalone TOML/projection inputs preserve their
  prior exclusive compatibility behavior.
- Writer, recovery, observation, bridge-publication, CAS, registration,
  amendment, and projection-write paths remain exclusively locked and were not
  changed.

No production registry content or live MemBase row was migrated by this
implementation. All implementation paths remain inside `E:/GT-KB`.

## Corrective Finding During Implementation

The initial focused 76-test cohort passed, and an independent technical review
found no P0/P1 issue on those bytes. A broader unchanged-consumer matrix then
found a genuine compatibility defect: custom TOML loaders located outside the
canonical three-path layout could see the live root journal and compare their
custom bytes against the live packaged mirror.

The implementation was reopened rather than overstated. It now gates optimistic
eligibility on the exact canonical root layout. The six failing standalone
loader tests and the legacy projection test all pass after that correction.
The final target hashes below supersede the first technical-review hashes. A
fresh independent technical rereview of that exact replacement cohort found no
P0 or P1 issue.

## Durable Operation-Time Authorization Evidence

- Exact-session GO implementation claim row `36004` was acquired at
  `2026-08-01T10:29:02Z` by Prime Builder session
  `019f9b59-52a0-75b2-9973-bd5601f98e9f` for
  `PROJECT-GTKB-HOUSEKEEPING-HARDENING`.
- The governed self-service extension was used twice because the default
  30-minute implementation deadline was shorter than the Windows-spawn and
  broad nonimpairment work. The resulting implementation deadline is
  `2026-08-01T11:59:02Z`; grace/TTL expires
  `2026-08-01T12:09:02Z`.
- The first finalized schema-v3 start packet was created at
  `2026-08-01T10:31:18Z`. After claim extension, a fresh packet was finalized
  at `2026-08-01T10:51:43Z` and expires at
  `2026-08-01T12:01:43Z`.
- Final packet hash:
  `sha256:bddb3ac66064e4c36df0f4a738b4aa9e96b005d2f74709b41500a60c23041e89`.
  Pre-start packet hash:
  `sha256:6d89bfe475cb4e1b4073385f6a4ca9ea04272df9292f0218559f1da6a9e700d9`.
- The packet binds proposal v001, independent GO v002, the exact root session
  and claim, PAUTH v2, project/WI, and exactly the three declared targets.
  Its implementation-start operation-time decision is `allowed`.
- Proposal SHA-256:
  `aa9c2e8126babf9750f0aff06a1fee2f9e052153dba28e73de7e3a14ddf03197`.
  GO SHA-256:
  `4d36192cedd48fe96a5ef457c29e683cf7c4fc8e91d38e988322b555599f65da`.
- `implementation_authorization.py validate` returned
  `authorized: true` for the exact three-target cohort before mutation and
  after the claim extension.

These identifiers preserve operation-time authority. Independent terminal
review must validate the captured proof and current implementation report; it
must not require the GO claim or start packet to remain live after filing this
`NEW` report changes the bridge lifecycle.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- `DELIB-202667517` and
  `DELIB-20260730-DISPATCHER-NEXT-PARALLEL-SOT-CONCURRENCY-REQUIREMENT`
  reject global single-leader serialization as the steady state.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` requires
  generous bounded waits and canonical readback rather than aggressive retry.
- `DELIB-202667721` authorizes normal work under the active list-free
  Housekeeping Hardening PAUTH.
- No new owner decision is required for this implementation report.

## Prior Deliberations And Chain

- `bridge/gtkb-wi5715-registry-read-scalability-001.md` is the exact
  approved implementation proposal.
- `bridge/gtkb-wi5715-registry-read-scalability-002.md` is the independent
  Loyal Opposition GO.
- WI-5675/WI-5717 retain the wider MemBase concurrency, timer-policy, and
  replacement-store frontier; this read-path implementation does not claim
  system-wide concurrency closure.
- WI-5825 overlaps two targets and must rebase after WI-5715 terminalization;
  it was not absorbed or modified here.

## Specification-Derived Verification

| Spec / governing surface | Executed evidence and observed result |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Four Windows-spawn readers synchronized inside the optimistic path and completed while the parent held the writer lock; all returned the same generation digest and record count with two marker reads. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Committed/aborted marker tests bind new/old triples; controlled writer interposition returns the complete new generation after exactly one exclusive fallback; existing parity/fault/recovery tests pass. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Stable TOML and projection schema errors remain typed; the untouched forbidden-substitutes and legacy restore-action suites pass. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Exact canonical bytes supply both parser and digest; no digest-keyed cache exists; stable and interposed generations are read live. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | Reader overlap is structural, writer interposition is deterministic, accepted writes remain complete, and no false-success path was added. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Tests prove `mode=ro`, `query_only=1`, rejected writes, missing-database no-create behavior, exact two-marker success, and exactly one fallback. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | One optimistic attempt plus one existing exclusive fallback; no new retry service, timer, worker, cache, or manual choreography. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / operation-time DCL | Claim row 36004 and the refreshed schema-v3 packet bind PAUTH v2, GO v002, root session, and exact targets. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Numbered chain remains v001 proposal, v002 GO, then this v003 NEW report; PB authors no terminal verdict. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Final focused plus unchanged compatibility matrix collected and passed 85 tests; independent final-hash technical rereview found no P0/P1 issue. Formal terminal review remains independent. |
| `GOV-WORK-TREE-HYGIENE-001` | Only the exact three approved targets changed. The helper excluded 1,177 other dirty paths, all preserved as foreign. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Writer, recovery, publication, observation, CAS, registration, amendment, public loader, forbidden-substitutes, and legacy restore tests remain green. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every changed or verification path is under `E:/GT-KB`; no adopter or external repository was touched. |

## Commands Run And Observed Results

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py groundtruth-kb/tests/test_sot_registry.py groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short --timeout=300
  PASS: 85 passed, 1 warning in 66.38s.

groundtruth-kb\.venv\Scripts\ruff.exe check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS: All checks passed.

groundtruth-kb\.venv\Scripts\ruff.exe format --check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS: 3 files already formatted.

groundtruth-kb\.venv\Scripts\python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS.

git --no-optional-locks diff --check -- groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS; Git emitted only its existing LF-to-CRLF working-copy advisory.
```

### Broad discovery matrix

A 580-test registry-consumer selection was initially stopped by the repository's
global 30-second pytest timeout while an implementation-start test scanned the
high-contention bridge tree. It was not reported as a WI-5715 test failure.

A narrowed rerun with `--timeout=300` collected 400 tests:

- 388 passed.
- Six standalone/custom-loader failures were attributable to WI-5715 and were
  fixed by exact canonical-layout eligibility; all nine affected loader/legacy
  module tests then passed.
- Six failures remain outside this diff:
  - the already-known schema-v2 checker fixture expects stale packet hash
    `sha256:0ab1e409...` (routed to WI-5783);
  - inventory path-class expectation drift (`generated` versus
    `opaque_container`);
  - four work-intent denial tests expect removed/changed authorization APIs.

This report does not claim those six unrelated tests are green or that WI-5715
closes their governed work.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  - SHA-256 `a063e0cb057facfc86d077360b02eb9805a1eb516c7ce16cced0b472d06c3006`
- `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`
  - SHA-256 `a37c5738094802367de4760638f7df450b5f78085dc3f3e86cac82a02b71437b`
- `groundtruth-kb/tests/test_registry_control_plane.py`
  - SHA-256 `fda19aed075d4d397bf7a97556cb4395d6ea97324012da08a8e39be327349073`

Verification-only paths were not edited:

- `groundtruth-kb/tests/test_sot_registry.py`
  - SHA-256 `c6fcba97dc582cafd8a830cbc94bd4f90a997ca9f62d7490afa9088bd87a19f8`
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py`
  - SHA-256 `55a029cd431c346d052076b99c1a514af9be51160ee7d073eefd15f34a412780`
- `platform_tests/scripts/test_gtkb_service_sot_restore_registry.py`
  - SHA-256 `ad29b90abad02b8f16874a7327e40509af82b01bcb9a8e1403acd444373da20a`

Exact diff stat at draft time: 3 files changed, 829 insertions, 53
deletions. The report helper excluded 1,177 out-of-scope dirty paths.

## Acceptance Criteria Status

1. [x] Stable terminal readers overlap without acquiring the writer lock and
   return one identical coherent generation.
2. [x] No optimistic reader accepts mixed canonical, packaged, or projection
   generations.
3. [x] Changed/nonterminal/missing/incomplete/unreadable evidence invokes
   exactly one exclusive fallback; no retry loop exists.
4. [x] Stable body failures preserve the exact original exception object and
   traceback; typed corruption/schema/parity errors remain visible.
5. [x] Every optimistic SQLite handle is read-only/query-only and rejects
   writes; missing databases are not created.
6. [x] Registry content is read live from exact bytes; no cache exists.
7. [x] Writers, recovery, observation, publication, CAS, registration, and
   amendment remain exclusively locked and behaviorally unchanged.
8. [x] Context-manager conflict is caught only at the bounded public wrappers,
   which replay their exclusive body once.
9. [x] Focused and untouched public/compatibility suites pass.
10. [x] No production timer, sleep, retry count, throttle, daemon, cache, or
    configuration surface was added.
11. [x] Only the three declared targets changed; foreign work remains excluded.
12. [x] No dispatcher, credential, external-system, push, history rewrite,
    deployment, release, or destructive cleanup occurred.

## Pre-Filing Preflight

Independent technical rereview covered the exact final hashes listed above and
reported no P0/P1 findings. The reviewer reran the expanded matrix (85 passed),
Ruff check/format, and `git diff --check`; directly probed canonical-layout
eligibility for live defaults, custom TOML, custom packaged mirror, custom
database, and normalized canonical spelling; and measured one live optimistic
snapshot at 2,348 records in 0.301 seconds. The reviewer lacked Windows symlink
creation privilege (`WinError 1314`), so symlink alias behavior was inspected
from resolved-path implementation rather than claimed as live fixture evidence.
Exact digest binding and the unchanged post-marker proof remain the acceptance
authority, not path spelling.

Final candidate preflights against this report produced:

- Applicability: `preflight_passed: true`, no blocking errors, no missing
  required specs, and no missing advisory specs. The final packet hash is
  preserved in the publication evidence rather than embedded self-referentially
  in the candidate bytes.
- Clause gate: five clauses evaluated; four `must_apply`, one `may_apply`, no
  evidence gap, and no blocking gap.
- Target coverage: advisory gaps only for the three unchanged verification
  paths listed under **Files Changed**. They were executed as compatibility
  evidence, are byte-hashed above, and are intentionally excluded from
  mutation authority because they were not edited.
- Duplicate live-thread guard: clean; no other live thread cites WI-5715.
- Related-work collision check: the four cited foreign WIs are explicitly
  declared as related work; no unrelated WI collision remains.
- Pattern lint in strict mode: zero findings.

The governed report helper must repeat its credential, currentness, transition,
capability, and physical-publication checks.

## Risk And Rollback

The complete journal head currently includes about 1.52 MB of `payload_json`;
marker equality hashes that row twice per successful optimistic read. Three
live 2,348-record snapshots on the pre-correction bytes took 0.474–0.497
seconds and returned one digest. The cost is bounded and currently acceptable,
but should be monitored as the registry grows; this report does not claim
constant-time marker reads.

Rollback requires separate governed authority to restore the prior exclusive
public reader in exactly the three declared targets, preserve the append-only
proposal/report/verdict chain, and rerun the 85-test final matrix plus static
checks. No data migration or registry-content rollback is required.

## Recommended Commit Type

`feat(registry): add generation-bound parallel reads`

## Loyal Opposition Asks

1. Independently verify the exact final hashes, claim/start history, canonical
   layout eligibility, marker semantics, one-fallback behavior, exact-byte
   binding, SQLite read-only enforcement, spawned overlap, writer
   interposition, standalone compatibility, and all executed evidence.
2. Re-run the final 85-test matrix and static checks with a short unique pytest
   temp root if Windows path length requires it.
3. Return `VERIFIED` only if every linked specification and acceptance row
   passes; otherwise return `NO-GO` with concrete findings.
