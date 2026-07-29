NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - WI-5714 registry write linearizability

bridge_kind: implementation_report
Document: gtkb-wi5714-registry-write-linearizability
Version: 009
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-wi5714-registry-write-linearizability-008.md
Approved proposal: bridge/gtkb-wi5714-registry-write-linearizability-007.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5714-REGISTRY-LINEARIZABILITY-20260729
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5714
Recommended commit type: fix

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/tests/test_registry_control_plane.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This implementation report performs no KB or MemBase mutation.

## Implementation Claim

Implemented the approved amend-only generation-CAS repair. `RegistryGenerationConflict`
is a strict `RegistryAuthorizationError` subtype. An amend commit compares its bound
snapshot generation before request-digest idempotency lookup; a stale generation fails
before journal or registry mutation. `amend_artifact` rebuilds only the caller's declared
field delta from a fresh coherent snapshot and retries only that typed conflict, with
eight total attempts and visible failure on the eighth.

Registration and legacy bootstrap writers were not changed; their residual generation
binding remains WI-5736 / TEST-11748. No production registry content, MemBase data,
dispatcher state, external system, Git history, deployment, release, credential, or
adopter application was mutated.

All implementation and bridge outputs remain in-root under `E:/GT-KB`; no
generated artifact or live dependency is outside the mandatory project root.

## Durable Operation-Time Authorization Evidence

- Exact-session GO implementation claim row `34632` was acquired at
  `2026-07-29T08:23:01Z` by session
  `019f9329-a174-7763-8f7e-29679f39e6bd`, role `prime-builder`, project
  `PROJECT-GTKB-HOUSEKEEPING-HARDENING`; it was live at protected mutation.
- The claim was extended once before report filing. Its implementation deadline is
  `2026-07-29T09:23:01Z` and grace/TTL expiry is `2026-07-29T09:33:01Z`.
- Implementation-start packet
  `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5714-registry-write-linearizability.json`
  was created at `2026-07-29T08:23:30Z`, finalized at `2026-07-29T08:23:31Z`,
  and expires at `2026-07-29T10:23:30Z`.
- Packet hash: `sha256:f9a0653f9602297744f59d24a188ec9103999483708f30a3f537fc309880d2ea`.
  Pre-start packet hash:
  `sha256:d25013b84db0786b1b4eb435da49761ca772c56ead51df3a35f45980deef3d4c`.
- The packet binds proposal v007, independent GO v008, the exact session claim,
  owner decision `DELIB-202667522`, PAUTH v1, and exactly the two declared targets.
  Both target validations returned `authorized: true` before mutation.
- Operation-time PAUTH decision was `allowed`, reason code `allowed`, evaluator v1,
  normalized envelope hash
  `7D671627329C3DEEC65BE6CFB82AE5212F07C633D3B5728311A43A75CE38A912`.
- Fresh report-time reads found the project active v1, WI-5714 P0/open/backlogged,
  the exact PAUTH active/unexpired/unsuperseded, and bridge latest GO v008.

These identifiers and timestamps are durable evidence that the claim and packet were
live when protected mutation began. Terminal review should validate this captured
operation-time proof and freshly rerun the still-live state and test checks; it should
not require the GO-derived packet or claim to remain live after this NEW report changes
the bridge lifecycle.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

- `DELIB-202667522` records the owner's exact two-file WI-5714 authorization,
  including the typed conflict, eight-attempt fresh-snapshot retry, and deterministic
  Windows-spawn coverage.
- `DELIB-202667517` records the no-lost-update concurrency requirement.
- No new owner decision is required for this implementation report.

## Prior Deliberations And Chain

- The complete numbered v001-v008 chain was reread before implementation.
- v007 is the operative REVISED proposal and v008 is its independent GO.
- A fresh exact Deliberation Archive read confirmed `DELIB-202667522` v1,
  work item WI-5714, outcome `owner_decision`, content hash
  `c681f8773bd897af24be29527ebdaf57cf9f40e97ecb818e1951678a2f7b3c93`.
- WI-5715 and WI-5736 remain separately sequenced after WI-5714; neither was
  absorbed into this diff.

## Specification-Derived Verification

| Spec / governing surface | Executed evidence and observed result |
| --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `test_amend_spawned_disjoint_writers_preserve_every_accepted_delta` forced four spawned writers through one first-read barrier; all four returned success and every accepted delta survived in the final authoritative snapshot. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Each retry calls the real coherent `load_registry_snapshot`; the interposition test observed two attempts and preserved the intervening accepted amendment. Fresh CLI/packet/claim reads were repeated before this report. |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` / `GIT-REQ-A11` | Spawn and deterministic interposition regressions prove accepted disjoint updates are preserved; no writer reports false success. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Spawn, mismatch, interposition, and exhaustion tests load a coherent snapshot after execution; declaration/package bytes and declaration/package/projection generation digests remain equal to the required success or preimage state. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Exact stale-generation test raises exact `RegistryGenerationConflict` before the idempotency lookup can return an old receipt and asserts unchanged files plus unchanged journal row count. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact PAUTH v1 is active, singleton WI-5714, source/test only, and names exactly the two changed targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Named packet finalized successfully and `validate --target` returned `authorized: true` for both paths before mutation; durable claim/packet evidence is recorded above. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Exact chain is v001-v008 GO followed by this v009 NEW report; author and reviewer session contexts differ; exact claim and start packet were used. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | All v007 linked specifications are carried into this report and candidate/filed applicability checks are required below. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Complete focused module collected 38 tests and passed all 38 after final formatting; the five new regression groups map to the approved acceptance criteria. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed paths are within `E:/GT-KB/groundtruth-kb`; no adopter or external repository path changed. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact two-path status shows only those two approved paths modified; `git diff --check -- <two targets>` exits 0; unrelated WI-5458 and bridge work remains untouched. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | WI-5714, TEST-11732, v007/v008, these two implementation paths, and this report remain linked; residual writers stay in WI-5736 / TEST-11748. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Mutation began only after GO, exact claim, and finalized start packet; this report requests independent VERIFIED and does not claim terminal completion. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The implementation is limited to approved amend behavior; WI-5736 remains the durable residual for registration/bootstrap generation binding. |

## Commands Run And Observed Results

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5714-registry-write-linearizability
  PASS; named packet created/finalized with allowed PAUTH decision.

groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py --target groundtruth-kb/tests/test_registry_control_plane.py
  PASS; authorized=true for both targets.

groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short
  PASS; 38 passed in 14.66s after final formatting (29-test pre-change baseline also passed).

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS; All checks passed.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS; 2 files already formatted.

git diff --check -- groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py groundtruth-kb/tests/test_registry_control_plane.py
  PASS; exit 0. Git emitted only its existing LF-to-CRLF working-copy advisory.
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  - SHA-256 `276D4479F824F4240D9FB39E0580056D0EE3CCB4CAEAFDEC2D2D963B2A8DFEC6`
- `groundtruth-kb/tests/test_registry_control_plane.py`
  - SHA-256 `66EDFEFDD3FCB66958F9EB2C530E2841D713970490F618809F2238944EFCA6DE`

Exact diff stat: 2 files changed, 305 insertions, 35 deletions. Thirty unrelated
dirty/untracked paths observed by the report helper were excluded and preserved.

## Acceptance Criteria Status

- [x] Stale amend generation raises exact `RegistryGenerationConflict` before mutation.
- [x] Four Windows-spawn workers preserve all four accepted disjoint deltas.
- [x] Deterministic interposed commit forces a conflict, fresh rebase, and preservation of both changes.
- [x] Ordinary authorization, in-progress, recovery, coverage, and unexpected failures propagate after one attempt.
- [x] Eight forced conflicts fail on attempt eight with unchanged declaration/package/projection digests and journal count.
- [x] Final reads are coherent and the existing fault-phase suite remains green.
- [x] Complete focused pytest plus Ruff lint/format and exact diff check pass.
- [x] `register_artifacts` and `bootstrap_legacy_registry` are unchanged and remain WI-5736.
- [x] Durable claim/start evidence proves live authorization at mutation/report time.

## Pre-Filing Preflight

Candidate commands executed against this completed report:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5714-registry-write-linearizability-009.md
  PASS; packet_hash sha256:218a9dbc950935e6a611339a38c58c2617b50f767b1cc4edc1f304b0f86cc043;
  preflight_passed=true; missing_required_specs=[]; missing_advisory_specs=[];
  blocking_errors=[]; unclassified_target_paths=[].

groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-impl-reports/drafts/gtkb-wi5714-registry-write-linearizability-009.md
  PASS; 5 clauses evaluated; must_apply=4; may_apply=1;
  must-apply evidence gaps=0; blocking gaps=0; mandatory exit 0.
```

The governed filing helper must repeat its content gates, and both preflight
commands must be rerun against the filed bridge ID before claim release.

## Risk And Rollback

Residual risk is bounded to contention beyond eight consecutive amend conflicts;
that condition now fails visibly rather than losing an accepted update. The
transaction lock, recovery, parity, and non-amend idempotency paths remain intact.
Rollback requires separate governed authority to revert only the two approved
paths and rerun the complete focused module and both Ruff gates. Numbered bridge
history, WI-5736, TEST-11748, owner decisions, report, and verdict are append-only.

## Recommended Commit Type

`fix`

## Loyal Opposition Asks

1. Independently rerun the named concurrency, mismatch, retry, exhaustion, full-module,
   Ruff, exact-diff, bridge/PAUTH, and durable operation-time evidence checks.
2. Return VERIFIED only if every linked specification and acceptance row passes;
   otherwise return NO-GO with concrete findings.
