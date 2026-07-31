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

# WI-5704 Transient Registry Index Recurrence Prevention Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5704-transient-index-recurrence-prevention
Version: 005
Responds to: bridge/gtkb-wi5704-transient-index-recurrence-prevention-004.md
Approved proposal: bridge/gtkb-wi5704-transient-index-recurrence-prevention-003.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5704-TRANSIENT-INDEX-REPAIR-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5704
target_paths: [".gitignore", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]
implementation_scope: defect_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

This implementation report performs no MemBase mutation or groundtruth.db write.

---

## Implementation Claim

WI-5704 is implemented within the five-path GO scope. Protected-commit Git
index snapshots now live under the validated `.gtkb-state` scratch root and
clean up after normal completion, exceptions, and interruption. A defensive
ignore rule prevents root transient recurrence. The protected-commit checker
rejects exact transient-index add, modify, copy, and rename states and grants a
deletion exception only for a pure deletion whose identity is absent from a
coherent canonical registry snapshot.

The operation-time classifier recognizes only the normalized, case-preserving
raw identity matching
`.gtkb-index-[a-z0-9_]{8}/index` with `re.fullmatch`. A backslash denotes the
same normalized identity and classifies positively; a doubled separator is
rejected. Uppercase, malformed, nested, directory, traversal, and unrelated
leaf forms do not gain `repository_metadata`; existing `.md`, `.json`, and
`.jsonl` classifications remain `governance_evidence`.

No tracked transient index was deleted, restored, staged, or committed. No
registry membership, declaration, packaged mirror, projection, journal,
MemBase semantic record, or `groundtruth.db` content was changed.

## First-Line Role Eligibility Check

PASS. Exact session `019f863a-acd3-7320-80c0-1831f0936cc0` is the Prime Builder
session that authored versions 001, 003, and this NEW implementation report.
The implementation used the live GO implementation claim for this thread and
the renewed exact-five-target packet
`sha256:e099b9b882cf86ce8117bb4954958c782532fd9e4c9750824048764c774bdca7`.
The packet's evaluator digest is
`2feeeab2c1996740c9ced1cf42bb1fa215d13ed39bd4104118ef31d7d957995d`.

## GO Precision Notes

1. Version 004 NI-1 is resolved by explicit semantics: path normalization
   makes a backslash the same identity, while a doubled separator remains a
   negative case.
2. Version 004 NI-2 is resolved with `re.fullmatch`, and alternate-leaf and
   nested-path regressions prove that suffix or prefix text cannot match.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-202667518` supplies the owner's exact authorization for WI-5704 and the
five-path PAUTH above. The owner authorized WI-5706 separately in
`DELIB-202667516`; that authorization is not consumed or widened here. The
owner also requires manual Loyal Opposition review, so this report requests an
independent review and does not spawn or substitute a reviewer.

## Prior Deliberations And Related Artifacts

- `DELIB-202667518` - exact WI-5704 authorization.
- `bridge/gtkb-wi5704-transient-index-recurrence-prevention-003.md` - approved
  revised implementation proposal.
- `bridge/gtkb-wi5704-transient-index-recurrence-prevention-004.md` -
  independent GO with two P3 precision notes and no implementation condition.
- `bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
  - originating advisory whose root-cause attribution the proposal corrected.
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md` - separate GO
  governing only the already-absent `hl705ij2` index.
- `WI-5722` / `TEST-11745` - separately unapproved work for deletion of the
  other nine tracked transient indexes after WI-5704 and WI-5706.

## Specification-Derived Verification

| Specification | Executed evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Canonical registry inspection and exact registered/unregistered deletion fixtures | PASS: coherent registry; membership remains authoritative and unchanged |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Registered pure-deletion and unregistered pure-deletion tests | PASS: registered deletion denied; only coherent no-membership grants the narrow exception |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Exact classifier positives, malformed negatives, alternate leaves, and generated-name tests | PASS: only exact normalized lowercase eight-character identity receives `repository_metadata` |
| `GOV-WORK-TREE-HYGIENE-001` | Snapshot success, exception, and `KeyboardInterrupt` cleanup tests plus root scan | PASS: no root or residual scratch transient remains |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Parameterized status matrix, path-shape matrix, and repeated generated-name samples | PASS: deterministic result across all tested states |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live claim, exact target/class packet, and explicit-path protected-commit audit | PASS: all five targets cleared by the live GO packet; no sixth target included |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict v001-v004 lifecycle resolution and NEW report helper plan | PASS: NEW -> NO-GO -> REVISED -> GO -> NEW, with no invalid transition |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Helper-carried 14-spec set and final-content applicability preflight | PASS: no linked specification omitted |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live PAUTH/project/WI binding used by claim and packet | PASS: exact PROJECT-GTKB-HOUSEKEEPING-HARDENING / WI-5704 triple |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This complete mapping plus 175-test focused execution | PASS pending independent Loyal Opposition re-execution |
| `GOV-STANDING-BACKLOG-001` | Live WI-5704, WI-5706, and WI-5722 dispositions | PASS: prevention and both cleanup cohorts remain separately visible |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Append-only proposal, verdict, report, and separate cleanup capture | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Five implementation postimages plus focused regression evidence | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Findings became revised proposal requirements and executable tests before mutation | PASS |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`
- `git diff --check -- .gitignore scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts/check_protected_commit_authorization.py --paths .gitignore scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py --json`
- `groundtruth-kb\.venv\Scripts\gt.exe registry inspect --json --no-census`
- `git ls-files -- .gtkb-index-*`

## Observed Results

- Focused tests: 175 passed, one pre-existing `PytestConfigWarning` for unknown
  `asyncio_mode`, in 89.48 seconds. The pre-change baseline was 159; all 16 new
  tests are included in the green result.
- Ruff check: PASS on all four Python targets.
- Ruff format check: PASS; all four Python targets already formatted.
- Git diff check: exit 0; only existing LF-to-CRLF future-touch warnings.
- Explicit-path protected-commit audit: PASS. All five paths were cleared by
  `live_go_packet`; seven audit gaps were recorded as nonblocking diagnostics.
- Live classifier spot-check: exact lowercase identity ->
  `repository_metadata`; uppercase -> `unclassified`; `.md` ->
  `governance_evidence`.
- Root transient inventory: ten tracked identities, nine present directories,
  and only the pre-existing WI-5706 identity absent. No new root transient and
  no `.gtkb-state` snapshot scratch remained.

## Registry Readback

- Coherent: true.
- Declaration and packaged digest:
  `sha256:8a45f90954cd0af9f026a1a7884ac2e499ec54a768080fc4d04ff84ad853fb44`.
- Projection digest:
  `sha256:ab996b43eb9e49618da127571155e3b7cae8c8ce87759f3a060173bc5932b787`.
- Generation digest:
  `sha256:1648ec387957a95bc236f0e1e2f22c3cd10e16e032ffe7a2360d808d7e1e9ed1`.
- Record count: 2348.
- No registry declaration, packaged mirror, projection, generation, or record
  count changed during WI-5704.

## Postimage Digests

- `.gitignore`: `2f5df6b9a0581dd91e4778fa0551773576eb95fd561b34ab9bdd2d187e0d9276`
- `scripts/check_protected_commit_authorization.py`: `2ccbb61798038cefaf214ba90bd6a5b2c2bbbe9095532ff6c52fba7a4aff41f4`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: `086471efccc4a165e45dba32a40061558afbf3ca62de93ec6b2455bde34cb04c`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`: `2feeeab2c1996740c9ced1cf42bb1fa215d13ed39bd4104118ef31d7d957995d`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`: `6faabe543e098efeaa908efe704ee3a9a7c89e72cabe2691c1d05e92716932fd6`

## Files Changed

- `.gitignore`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`

## Excluded Pre-Existing Worktree State

The tracked deletion `.gtkb-index-hl705ij2/index` predated WI-5704 and belongs
only to WI-5706. WI-5704 did not claim, packetize, restore, stage, modify, or
delete it. Fourteen other dirty paths reported by the canonical helper are also
outside WI-5704 and were not modified by this implementation.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: the change prevents recurrence of one proven
  transient-index defect without introducing a new policy or schema.

```text
5 files changed, 222 insertions(+), 6 deletions(-)
```

## Acceptance Criteria Status

1. PASS: snapshots use validated `.gtkb-state` scratch and clean up after
   success, exception, and `KeyboardInterrupt`; the real Git index is unchanged.
2. PASS: `.gitignore` contains exactly one `.gtkb-index-*/` rule.
3. PASS: add, modify, copy-source, copy-destination, rename-source, and
   rename-destination states are rejected; coherent unregistered pure deletion
   passes the transient rule.
4. PASS: missing or incoherent registry authority blocks the exception, and a
   matching registry record blocks deletion.
5. PASS: exact case-preserving `re.fullmatch` semantics and every required
   positive, fallback, and negative path shape are tested.
6. PASS: tests pin the private CPython alphabet, eight-character length, and
   128 generated names.
7. PASS: the 159-test baseline plus 16 regressions is 175/175; both focused Ruff
   gates pass.
8. PASS: registry declaration, mirror, projection, generation digest, and 2348
   record count are unchanged.
9. PASS: WI-5706's target classifies as `repository_metadata`; WI-5704 acquired
   no WI-5706 claim or packet and did not touch that path.
10. PASS: WI-5722 still owns the other nine deletions and remains separately
    unapproved.

## Risk And Rollback

Residual risk is the deliberate dependence on CPython's private temporary-name
contract. The runtime-contract test converts any future alphabet or length
change into an explicit review failure. Exact full matching and the status and
registry matrices bound over-classification and unauthorized deletion risk.

Before terminal verification, rollback is limited to restoring the five exact
target files and clearing only WI-5704 staging. After a terminal commit, repair
must be append-only and forward-only. No reset, amend, rebase, history rewrite,
push, release, or deployment is authorized by this report.

## Loyal Opposition Asks

1. Re-run the 175-test focused suite and both Ruff gates.
2. Independently inspect exact matcher, deletion exception, snapshot location,
   cleanup paths, and registry readback.
3. Confirm WI-5706's pre-existing deletion is outside the report include set.
4. Return VERIFIED only if implementation and finalization satisfy the approved
   scope; otherwise return NO-GO with the exact remaining finding.
