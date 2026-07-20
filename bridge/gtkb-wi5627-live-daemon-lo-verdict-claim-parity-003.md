NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; reasoning_effort=xhigh; build activity envelope

bridge_kind: implementation_report
Document: gtkb-wi5627-live-daemon-lo-verdict-claim-parity
Version: 003
Responds to GO: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-002.md
Approved proposal: bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5627

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]
supporting_evidence_paths: ["bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch"]
hunk_patch: "bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch"

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

# Implementation Report - WI-5627 Live-Daemon LO Verdict-Claim Parity

## Implementation Claim

The independently approved WI-5627 repair is implemented and isolated for
review. The live dispatcher daemon now establishes the Loyal Opposition worker
session, acquires the complete selected document batch's verdict claims using
the existing worker-lifetime-derived TTL, and only then invokes the provider
spawn path. It records trusted worker context and exact claim provenance in the
launch record. Peer-held or failed claims suppress launch, release document
leases, and spend no provider budget. Launch failure releases only claims owned
by the daemon worker session. Existing exit reconciliation can now release those
recorded claims after incomplete worker exit.

Both source and test targets contained substantial foreign dirty changes before
WI-5627 began. This session modified only the hash-pinned WI-5627 hunks. It did
not adopt, rewrite, stage, or dispose of any neighboring change.

## Authorization Evidence

- Independent GO:
  `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-002.md`.
- Approved proposal:
  `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md`.
- Exact work-intent claim: row `33377`, kind `go_implementation`, acting role
  `prime-builder`, session
  `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, project
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- Schema-v3 implementation-start packet:
  `sha256:302b0549a31d8aeb6deacefef2b94d180ed4606d177a45297677ae1143c971b8`.
- Active project authorization:
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, with no expiry and active
  project-membership coverage for WI-5627.
- Target-path preflight: `in_scope`; both declared candidates accepted; zero
  unused or out-of-scope targets.
- Protected-target validation after implementation: both target paths remain
  authorized by the live implementation-start packet.

## Hunk Isolation Evidence

- Hunk patch:
  `bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch`.
- Patch SHA-256:
  `96870f21538bc7aa57e553b57fc00c96ab008e905dd1ee864464ebd15eceff4f`.
- Patch Git blob: `d9624434e237526cf99691ba38372f2d2f2f6da9`.
- Patch size: `19061` bytes.
- Patch numstat:

```text
61      0       scripts/gtkb_dispatcher_daemon.py
360     0       platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

- Recorded pre-implementation target hashes:

```text
DC1E1A077CB83C1D2DC9C69180D01D8CCA77E56CD179D5F8DDF859DEAF608556  scripts/gtkb_dispatcher_daemon.py
153AF7F6D53DB772ACCE98B940B19FB5DC0A83BD931F9EC43025F6E913110995  platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

- Current post-implementation target hashes:

```text
11BABD7658BC5F397CB90BDA3B727BCEDCD71A1859B72BB1DA8E125EE62F9152  scripts/gtkb_dispatcher_daemon.py
D2B6B8ABE13DD1E55BCB6989798CF45EE0E524425853A87C77723314E2B7047A  platform_tests/scripts/test_gtkb_dispatcher_daemon.py
```

- Forward `git apply --check --whitespace=error` passed against an in-root,
  hash-verified reconstruction of the exact two pre-implementation bytes.
- Reverse `git apply -R --check --whitespace=error` passed against the live
  working tree.
- Patch marker and header scans found only the two approved paths and no
  dispatcher configuration, harness registry, MemBase, OpenRouter harness,
  WI-5216, WI-5495, or temporary reconstruction reference.
- The Git index remained empty throughout.

Whole-file staging is prohibited. Independent verification and focused
finalization must use the hunk patch.

## Files Changed

- `scripts/gtkb_dispatcher_daemon.py`
  - captures trusted LO worker context after worker-session authority succeeds;
  - derives claim TTL from the existing worker lifetime profile;
  - acquires the exact selected LO document batch before `_spawn_harness`;
  - treats peer-held and failed claims as non-launched outcomes;
  - releases document leases on claim failure;
  - records exact claim session/slugs for later exit reconciliation; and
  - releases exact daemon-owned claims on launch failure.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
  - proves authority-before-claim-before-spawn ordering and exact-batch
    acquisition;
  - proves peer-held neutral suppression, zero spawn, and lease release;
  - proves partial acquisition releases only the already-owned claim;
  - proves authority failure precedes claim acquisition and releases leases;
  - proves launch failure releases exact owned claims; and
  - proves claim context is persisted before exit reconciliation.
- `bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch`
  - carries the exact two-file isolation evidence.

No dispatcher configuration, runtime JSON, lease file, routing, eligibility,
selection, allowance, role, identity, provider, credential, process,
deployment, release, or unrelated worktree mutation is included.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-HARNESS-ISOLATION-001`

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes the bounded standing
  reliability repair while preserving all bridge, claim, start, verification,
  and focused-commit gates.
- `DELIB-202666762` established the WI-5400 dispatcher-owned pre-launch LO
  verdict-claim lifecycle that WI-5627 now applies to the production daemon
  path.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires canonical
  evidence. This report cites only MemBase, the Deliberation Archive, numbered
  bridge artifacts, source, tests, and the canonical hunk evidence.

The complete numbered WI-5627 chain was read before implementation and report
filing.

## Owner Decisions / Input

No new owner decision is required. The active fleet goal requires correction of
dispatcher-produced harness defects through work item, linked test, PAUTH,
independent GO, claim, implementation-start authorization, implementation,
testing, independent verification, and focused commit. The owner's hold on
dispatcher configuration remains fully preserved.

## Specification-Derived Verification

| Governing requirement | Executed evidence | Observed result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | `pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short -k wi5627` | PASS: 6 passed, 62 deselected; one existing unknown-`asyncio_mode` warning. Exact batch claim occurs after authority and before spawn; peer contention makes zero provider calls. |
| `TEST-11672`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Complete daemon module plus `test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict` | PASS: daemon module 68 passed; focused exit-reconciliation test 1 passed; one existing warning in each invocation. Partial claim, authority failure, launch failure, and incomplete-exit cleanup are covered. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live GO, claim row, schema-v3 start packet, exact target-path preflight, protected-target validation, applicability preflight, and mandatory clause preflight | PASS: two of two targets in scope; no blocking errors, missing specs, or clause gaps. |
| `GOV-RELIABILITY-FAST-LANE-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Patch hash/blob/size/numstat, exact preimage hash reconstruction, forward/reverse apply checks, and empty-index check | PASS: only the WI-5627 source and tests are selected; all foreign bytes remain excluded. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-HARNESS-ISOLATION-001` | Path/header scan, patch marker scan, and offline focused tests | PASS: every artifact is in-root; no provider request or direct harness contact occurred. |
| Python mechanical quality gates | Ruff lint, Ruff format check, Python compilation, and `git diff --check` on both targets | PASS: both files lint-clean, already formatted, compile successfully, and have no whitespace errors. |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5627-live-daemon-lo-verdict-claim-parity --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --ttl-seconds 7200
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --session-id 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a --expires-minutes 120
groundtruth-kb/.venv/Scripts/python.exe scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --candidate-paths scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short -k wi5627
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git diff --check -- scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py
git apply --check --whitespace=error --directory=.gtkb-state/wi5627-patch-work bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
git apply -R --check --whitespace=error bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
git apply --numstat bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5627-live-daemon-lo-verdict-claim-parity
```

## Observed Results

- Focused WI-5627 daemon tests: 6 passed.
- Complete daemon module: 68 passed.
- Existing incomplete-exit claim-release regression: 1 passed.
- Ruff lint: all checks passed.
- Ruff format: two files already formatted.
- Python compilation and whitespace checks: exit 0.
- Exact target-path preflight: two candidates in scope; zero unused targets.
- Applicability preflight: pass; no missing required or advisory specs and no
  blocking errors.
- Mandatory clause preflight: exit 0; zero evidence gaps and zero blocking
  gaps.
- Hunk patch checks: forward pass, reverse pass, exactly two approved paths.
- Git index: empty.

## Pre-Filing Preflight

Candidate-content applicability and mandatory clause preflights are run against
the exact completed report before governed filing. The filing helper recomputes
both gates and refuses missing required/advisory specifications, blocking
errors, clause gaps, stale latest status, or an existing v003 path.

## Acceptance Criteria Status

- [x] The live daemon acquires the exact selected LO document batch before
  provider launch.
- [x] Worker authority is established before claim acquisition.
- [x] Peer-held claims suppress provider launch neutrally and release leases.
- [x] Partial claim failure releases only daemon-owned claims.
- [x] Authority and launch failure release the appropriate leases and claims.
- [x] Claim session/slugs and trusted worker context are persisted for existing
  incomplete-exit reconciliation.
- [x] Focused and complete tests plus all mechanical gates pass.
- [x] No dispatcher configuration, runtime, routing, eligibility, provider, or
  unrelated mutation is included.
- [ ] Independent Loyal Opposition verification and focused `fix(dispatch)`
  finalization remain pending.

## Required Independent Verification

Loyal Opposition should:

1. Read versions 001 through 003 and independently inspect the hunk patch.
2. Recompute patch SHA-256, Git blob, size, numstat, and exact two-path scope.
3. Re-run forward and reverse applicability checks.
4. Confirm authority precedes claim, claim precedes spawn, peer contention
   launches no provider, and only owned claims are released.
5. Re-run the focused WI-5627 tests, complete daemon module, existing
   incomplete-exit regression, Ruff, formatting, compilation, and whitespace
   checks.
6. Finalize `VERIFIED` atomically through:

```text
--hunk-patch bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch
```

Whole-file staging of either dirty target is prohibited.

## Expected Focused Finalization Set

- `scripts/gtkb_dispatcher_daemon.py` through the exact hunk patch.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` through the exact
  hunk patch.
- `bridge/hunks/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-hunks.patch`.
- `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-001.md`.
- `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-002.md`.
- `bridge/gtkb-wi5627-live-daemon-lo-verdict-claim-parity-003.md`.
- The independent terminal `VERIFIED` artifact.

## Risk / Rollback

The remaining implementation risk is accidental whole-file finalization of
commingled targets. The canonical hunk patch is the required containment
mechanism. Runtime behavior reuses the established WI-5400 helper lifecycle,
so no second claim registry or release path was introduced.

Rollback requires separate authority and reverses only the WI-5627 hunk patch,
then reruns the focused and complete test commands plus mechanical gates. No
dispatcher configuration rollback is needed because configuration was not
changed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
