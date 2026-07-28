NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review
author_metadata_source: x-codex-turn-metadata

# WI-5706 Exact Repair-Forward Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5706-wi5441-finalization-scope-repair
Version: 003
Responds to: bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md
Approved proposal: bridge/gtkb-wi5706-wi5441-finalization-scope-repair-001.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5706-REPAIR-FORWARD-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5706
target_paths: [".gtkb-index-hl705ij2/index"]
implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: chore:

---

## Implementation Claim

WI-5706 is implemented to its one-path postimage. The unregistered transient
Git index `.gtkb-index-hl705ij2/index` is absent from the working tree and is
the sole staged repository path. The implementation adopts that pre-existing
absence after GO, proves the exact historical 12-versus-5 partition, and
preserves every byte of the 12 intended WI-5441 paths and four valid Loyal
Opposition advisories from commit `f9e85829e`.

No source, test, configuration, registry declaration, packaged registry,
registry projection, bridge predecessor, advisory, or unrelated dirty path was
modified by WI-5706. No history rewrite, push, dispatcher mutation, release,
deployment, credential operation, or external-system mutation occurred.
The valid-packet implementation performs no MemBase mutation and writes no
`groundtruth.db` change; its only implementation postimage is the declared
repository-metadata deletion.

## First-Line Role Eligibility Check

PASS. Exact session `019f863a-acd3-7320-80c0-1831f0936cc0` is the Prime Builder
session that authored version 001 and this NEW implementation report. The
implementation uses the live GO implementation claim and packet
`sha256:15cd8269e9d95e3521c67b620f0f80db6d35c20af74f82e3e3a0de9176b4846d`.
The packet records pre-start hash
`sha256:e68fa931271be5257b24bce11260ae57f545de4d480312ac0a51ad4d30ada56a`
and exact target classification `repository_metadata`.

## Sequence And Authorization Disclosure

The worktree deletion predated proposal 001 and GO 002; its original actor and
exact deletion time are not inferred. This report follows the GO's N1
instruction by recording that sequence explicitly. After GO, Prime Builder
acquired the exact claim, obtained a valid implementation-start packet, and
staged the already-absent postimage as the sole repository change.

The first packet attempt failed closed because PAUTH v1 named the exact target
but allowed only `metadata` and `bridge`, while terminal WI-5704 now correctly
classifies the target as `repository_metadata`. The canonical project service
appended PAUTH v2 with `repository_metadata` added. Owner decision, scope text,
included WI/specs, and every forbidden operation remained unchanged. The
second packet attempt passed and records authorization version 2. The PAUTH
append was a pre-implementation control-plane authorization correction, not an
implementation artifact or finalization path.

## Commit And Tree Identity

- Contaminating WI-5441 finalization commit: `f9e85829e`.
- Implementation baseline commit: `ec7e6b378329fdc6529a25311232235417ccda41`.
- Baseline tree: `90da3ca33f78d7df4d15c88a03ab70e79dd828da`.
- Prospective tree with only the transient deletion staged:
  `9fc795b2cd2c0979633cccd589796dfdb0f74836`.
- Terminal commit id: intentionally not yet available. Under the approved
  atomic finalization contract, the independent version 004 verdict and this
  report enter the same commit as the deletion. The commit id is therefore an
  output of verification, not information Prime Builder can place in this
  pre-verdict report without circularity.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

`DELIB-202667516` records the owner's exact authorization, "Authorize WI-5706
exactly as stated," and remains the owner evidence for the exact-path PAUTH.
PAUTH v2 reconciles the machine-readable mutation class to the already-approved
path after WI-5704's classifier became terminal; it does not widen the owner's
scope. The owner requires manual Loyal Opposition review, so this report asks
for independent review and does not spawn or substitute a reviewer.

## Prior Deliberations And Related Artifacts

- `DELIB-202667516` - exact WI-5706 authorization.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - registry
  authority and disposable-artifact distinction.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md` -
  terminal WI-5441 verdict whose commit contained the transient.
- `bridge/gtkb-wi5704-transient-index-recurrence-prevention-006.md` - terminal
  recurrence-prevention verification at commit `ec7e6b378`.
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-001.md` - exact repair
  proposal.
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md` - independent GO.

## Specification-Derived Verification

| Specification | Executed evidence | Result |
| --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolved all 17 historical paths and the target under `git rev-parse --show-toplevel` | PASS: every path is under `E:/GT-KB`; none is under `applications/` |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Cross-checked decision, WI, PAUTH, proposal, GO, report, target postimage, and retained hashes | PASS: every implementation input and output has a durable artifact edge |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Direct `resolve_bridge_lifecycle` calls for WI-5441 and WI-5706 | PASS: WI-5441 is terminal VERIFIED; WI-5706 is strict NEW -> GO before this NEW report; zero diagnostics |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verified owner decision, proposal chain, report, and separate WI-5704/WI-5722 records | PASS: no requirement or follow-on exists only in session prose |
| `GOV-WORK-TREE-HYGIENE-001` | Exact `f9e85829e` path-set partition, byte identity, staged-set enumeration, and excluded-path scan | PASS: 12 intended + 4 preserved advisories + 1 transient; only the transient deletion is staged |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `gt registry validate --json`, `gt registry reconcile --deep --json`, and canonical registry list | PASS: valid/coherent, 2348 records, zero invalid/unknown, zero unregistered load-bearing, target unregistered |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Pre/post declaration, packaged, projection, and generation digest comparison | PASS: all registry content and generation digests unchanged |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Claim plus implementation-start packet against PAUTH v2 and one target | PASS: exact path classified `repository_metadata`; requested operation allowed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | 95 focused lifecycle/project/registry tests plus strict live-chain resolution | PASS: 95/95 and zero live-chain diagnostics |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Helper-carried 13-spec set and final-content preflight | PASS: no linked specification omitted |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live PAUTH/project/WI triple used by the claim and packet | PASS: exact Housekeeping Hardening / WI-5706 binding |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This complete mapping, focused tests, deterministic scans, and command results | PASS pending independent Loyal Opposition re-execution |
| `GOV-STANDING-BACKLOG-001` | Live WI-5706 readback and separate WI-5704/WI-5722 ownership | PASS: repair and remaining transient cleanup remain separately traceable |

## Commands Run

- `git diff-tree --no-commit-id --name-only -r f9e85829e`
- Per retained path: `git rev-parse f9e85829e:<path>`, `git rev-parse
  HEAD:<path>`, `git hash-object -- <path>`, and PowerShell `Get-FileHash
  -Algorithm SHA256`.
- `gt registry validate --json`
- `gt registry reconcile --deep --json`
- `gt registry list --json` with exact `storage_path` filtering.
- Direct Python calls to `resolve_bridge_lifecycle` for WI-5441 and WI-5706.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest
  groundtruth-kb/tests/test_sot_registry.py
  groundtruth-kb/tests/test_artifact_membership_reconciliation.py
  platform_tests/scripts/test_project_authorization.py
  platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --no-header`
- `git add -u -- .gtkb-index-hl705ij2/index`
- `groundtruth-kb/.venv/Scripts/python.exe
  scripts/check_protected_commit_authorization.py --staged`
- `git write-tree`

## Observed Results

- Historical inventory: exactly 17 paths; expected partition equality true.
- Retained identity: all 16 retained paths have identical Git blob ids at
  `f9e85829e`, `HEAD`, and the working tree, and their SHA-256 values below are
  unchanged.
- Target: tracked at `HEAD`, absent from the working tree, unregistered, and
  staged as `D`.
- Focused tests: 95 passed in 17.07 seconds. Two warnings were emitted: the
  pre-existing unknown `asyncio_mode` configuration warning and one dependency
  deprecation warning.
- Protected-commit checker: PASS; the exact staged set contains no protected
  path.
- Deep reconciliation: exit 0, `release_eligible: true`, zero admission
  candidates, zero `invalid_unknown`, and zero `unregistered_load_bearing`.
  It reported 2,340,003 unregistered-disposable objects and very large JSON
  output; that performance/output-volume observation does not change the
  target's membership or this bounded repair.

## Retained Path Hashes

The first 12 rows are the intended WI-5441 cohort; the final four are the valid
advisories that commit `f9e85829e` also carried. Each SHA-256 is the live raw
file digest after Git blob equality was established across historical commit,
current HEAD, and working tree.

| Path | SHA-256 |
| --- | --- |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-014.md` | `c61a2385cfabd201add3045fe36ea1a213e9feee0ded58b4c74d51043fd4e045` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md` | `27dba59a5e20e06ca065cf4113efabfb04904fa9c6e811184275cf68f73cdfdf` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md` | `06584d56edcafefc4471e15cbf8d2468bd5a5cae87364ff76ee6fa08aac245f3` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md` | `08c3ba3314d232e7fcc2cd9d6408f919ac7b37457c70722f4f5fe5594b048847` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-018.md` | `7da5169eb3f1d7cb10a3c7c85efa0228333419d2ff2da0f07f9071a5f5ec3303` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-019.md` | `76c74807fb551892d5283ac9c5fd0a3d96a8afbbe42748d67f94b664fa37e803` |
| `bridge/gtkb-wi5441-global-registry-membership-reconciliation-020.md` | `99012f55122875e10e381dfe1c24d2aa4f94314d7a8218bd958c478ae4cbfdea` |
| `config/registry/sot-artifacts.toml` | `8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44` |
| `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` | `8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44` |
| `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py` | `367d3c5afa1401f815f0ba4b2f6efde4b9badaaad06b83ca8615813c8a728560` |
| `groundtruth-kb/tests/test_artifact_membership_reconciliation.py` | `839f371de9be39897178d3185176c821aaa21792b57611f2da077b04e447f6ea` |
| `platform_tests/scripts/test_implementation_start_gate.py` | `2d2d8dec605db7df0de6b22f246dd2e990e894e14272e27a39e54fa4057dcd40` |
| `bridge/gtkb-lo-advisory-verdict-filing-governed-cli-gap-001.md` | `102caef5f0f8d6a29dd2d7324040e810eec1c7564b8131206de9faeee6246d4f` |
| `bridge/gtkb-lo-bridge-state-report-unknown-status-silent-exclusion-advisory-001.md` | `67410a208c54e45b833bc82c0c86f7c7afa63253577646dc1cbaa151195fbb48` |
| `bridge/gtkb-lo-gov-file-bridge-authority-spec-body-path-orphaned-advisory-001.md` | `46b54441139c0fa577dc5db32e4d28ece3132a46ed0509d78aa57ce67630b6ed` |
| `bridge/gtkb-lo-owner-decision-capture-auq-binding-gap-advisory-001.md` | `aa3826561c38e5b67b8ac2af5eb82a9fe8f041955a76a9a96c938a0c3b4bbd31` |

## Registry Readback

- Coherent and valid: true.
- Record count: 2348.
- Declaration and packaged digest:
  `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`.
- Projection digest:
  `sha256:ab996b43eb9e49618da127571155e3b7cae8c8ce87759f3a060173bc5932b787`.
- Generation digest:
  `sha256:1648ec387957a95bc236f0e1e2f22c3cd10e16e032ffe7a2360d808d7e1e9ed1`.
- Membership counts from validation: 16,909 registered, 1,647
  unregistered-disposable, zero invalid/unknown, zero unregistered
  load-bearing.
- Exact registry lookup: no record has storage path
  `.gtkb-index-hl705ij2/index`; no `.gtkb-index-*` record exists.
- Registry declaration, packaged mirror, projection, generation digest, and
  record count did not change during WI-5706.

## Files Changed

- `.gtkb-index-hl705ij2/index`

## Finalization Include Contract

The terminal transaction must contain exactly the deletion above and the
append-only WI-5706 bridge chain:

- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-001.md`
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md`
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-003.md`
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-004.md`

No other path is admitted. Version 004 is reserved for the independently
authored terminal verdict and does not exist at report filing time.

## Excluded Pre-Existing Worktree State

The report helper observed 14 dirty paths outside the one implementation path.
Versions 001 and 002 above are audit-chain inputs reserved for terminal
finalization. The remaining 12 paths are unrelated and must remain unstaged:

- `bridge/gtkb-lo-bridge-lifecycle-semantics-gate-gap-advisory-001.md`
- `bridge/gtkb-lo-terminal-verdict-authoring-friction-advisory-001.md`
- `bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
- `bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-002.md`
- `bridge/gtkb-lo-verified-finalization-interrupted-transaction-recovery-advisory-001.md`
- `bridge/gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory-001.md`
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-001.md`
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-002.md`
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001.md`
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-002.md`
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-003.md`
- `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-004.md`

All 12 exist as untracked files and none is staged. In particular, the two
unrelated advisory paths explicitly named in proposal 001 remain present,
untracked, and unstaged.

## Recommended Commit Type

- Recommended commit type: `chore:`
- Diff-stat justification: the one-file binary deletion removes disposable
  repository metadata and changes no runtime behavior.

```text
.gtkb-index-hl705ij2/index | Bin 2510618 -> 0 bytes
1 file changed, 0 insertions(+), 0 deletions(-)
```

## Acceptance Criteria Status

1. PASS: commit `f9e85829e` contains exactly 17 paths partitioned as 12 intended
   plus four preserved advisories plus one transient.
2. PASS: all 16 retained paths are byte-identical across `f9e85829e`, current
   HEAD, and working tree; exact SHA-256 values are recorded above.
3. PASS: the transient is unregistered, absent from the working tree, and the
   sole staged repository path.
4. PASS: the two explicitly named unrelated advisories remain present,
   untracked, and unstaged; ten additional concurrent bridge paths are also
   enumerated and excluded.
5. PASS: focused tests are 95/95; protected-commit authorization passes; both
   live lifecycles resolve strictly with zero diagnostics.
6. PASS: registry content, projection, generation, and record count are
   unchanged; validation and deep reconciliation report no invalid/unknown or
   unregistered-load-bearing object.
7. READY FOR INDEPENDENT FINALIZATION: this report cannot truthfully provide a
   terminal commit id before the independently authored verdict exists. The
   exact five-path finalization contract above supplies the mechanical boundary
   for version 004 and the one authorized local commit.

## Risk And Rollback

Residual risk is finalization accidentally admitting an unrelated untracked
bridge artifact. The exact five-path include contract, one-path `Files Changed`
section, and pre-commit staged-set enumeration bound that risk. The deep census
also demonstrated a separate output-volume cost; no recovery or sweep action is
authorized by WI-5706.

Before terminal verification, rollback is restoring the transient from `HEAD`
and clearing only WI-5706 staging. After terminal commit, repair must be
append-only and forward-only. No reset, amend, rebase, history rewrite, push,
release, or deployment is authorized.

## Loyal Opposition Asks

1. Recompute the 17-path partition and retained byte identity independently.
2. Re-run the focused tests, registry checks, lifecycle checks, and staged-path
   authorization.
3. Confirm PAUTH v2 changes only the machine-readable mutation class needed by
   WI-5704's terminal taxonomy and does not widen owner scope.
4. Finalize only the target deletion and versions 001 through 004. Return
   VERIFIED only if the terminal commit can be created without admitting any
   excluded path; otherwise return NO-GO with the exact remaining finding.
