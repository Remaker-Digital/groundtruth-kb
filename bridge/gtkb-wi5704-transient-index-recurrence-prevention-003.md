REVISED
::init gtkb pb
::open build

# WI-5704 Transient Registry Index Recurrence Prevention - Review Corrections

bridge_kind: prime_proposal
Document: gtkb-wi5704-transient-index-recurrence-prevention
Version: 003
Author: Prime Builder (Codex)
Date: 2026-07-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop; Prime Builder; owner-driven manual Loyal Opposition review

Responds to: bridge/gtkb-wi5704-transient-index-recurrence-prevention-002.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5704-TRANSIENT-INDEX-REPAIR-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5704

target_paths: [".gitignore", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]

implementation_scope: defect_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This revision addresses both blocking findings and all four non-blocking
findings from version 002. It does not rederive or redesign the accepted root
cause, scratch relocation, ignore rule, staged recurrence guard, registry-bound
deletion exception, five-file PAUTH scope, or 159-test baseline.

The classifier contract is corrected to preserve existing classifications:
only the exact raw CPython-emitted transient shape becomes
`repository_metadata`; every negative stays outside that class, but alternate
`.md`, `.json`, and `.jsonl` leaves retain their existing
`governance_evidence` classification. The actual ten-file tracked population is
fully disclosed. WI-5706 remains bounded to the already-deleted `hl705ij2`
path; new WI-5722 owns separately reviewed removal of the other nine after
WI-5704 and WI-5706.

## Carried Forward Without Change

Version 002 independently verified these parts of version 001; they remain the
implementation contract and are not reworked here:

- The only root `.gtkb-index-*` creation site is
  `scripts/check_protected_commit_authorization.py:901`.
- `_scratch_root(root)` at
  `scripts/check_protected_commit_authorization.py:574-594` already supplies
  the required in-root, symlink, junction, reparse-point, and ancestor checks.
- `_index_snapshot` moves its temporary directory under that validated scratch
  root while retaining immutable index identity, permissions, sanitized
  `GIT_INDEX_FILE`, and before/after checks.
- `.gitignore` receives one defensive `.gtkb-index-*/` rule.
- The commit checker rejects exact transient add, modify, copy, and rename
  recurrence and permits deletion only when a coherent canonical registry
  snapshot proves no membership.
- The five exact target paths and all explicit PAUTH exclusions are unchanged.
- The focused pre-change baseline remains 159 passing tests.

## F1 Resolution - Exact Raw Shape, Existing Negative Classifications

The operation-time classifier will test the normalized but case-preserving raw
`path` value for this one exact shape before the module's generic extension
rules:

```text
\.gtkb-index-[a-z0-9_]{8}/index
```

This deliberate raw-path check is narrower than the module's later `lowered`
classification branches. It is justified because this rule identifies one
machine-emitted repository-metadata identity, not a user-facing case-insensitive
file family. CPython's current private `_RandomNameSequence` emits exactly eight
characters from `abcdefghijklmnopqrstuvwxyz0123456789_`; uppercase is not an
emitted identity. A case-variant therefore fails closed as `unclassified`
rather than being silently granted an operation class.

Negative expectations are now exact:

- `.gtkb-index-hl705ij2/index` -> `repository_metadata`.
- `.gtkb-index-HL705IJ2/index` -> `unclassified`.
- malformed suffix, directory-only, nested exact-looking path, separator, and
  traversal forms -> not `repository_metadata` and retain their existing
  classification.
- `.gtkb-index-hl705ij2/index.md`, `index.json`, and `index.jsonl` ->
  `governance_evidence`, exactly as today.
- every other alternate leaf retains the module's existing generic extension
  or fallback classification; none becomes `repository_metadata` through this
  rule.

Tests assert both the exact expected classes above and the stronger invariant
that no negative is classified as `repository_metadata`. No generic `.md`,
`.json`, `.jsonl`, or lowercase classification rule is changed.

The dependency on private CPython behavior is explicit. A focused test pins the
current eight-character alphabet/length contract and samples generated names.
A Python runtime upgrade that changes either property must fail that test and
trigger review of the matcher rather than silently widening classification.

## F2 Resolution - Ten Tracked Transients, Three Origins, Split Cleanup

Deterministic enumeration with `git ls-files -- ".gtkb-index-*"` returns ten
tracked paths:

```text
.gtkb-index-2ybwnnsa/index
.gtkb-index-3wupbb0i/index
.gtkb-index-cwv3hf3w/index
.gtkb-index-fhgo52kh/index
.gtkb-index-h_1cwotz/index
.gtkb-index-hef4mjw4/index
.gtkb-index-hl705ij2/index
.gtkb-index-ilk3djzq/index
.gtkb-index-jzitjv59/index
.gtkb-index-t7nsgbor/index
```

Origins are exact:

- `db07f9dcfe7e7de8addc850729209278472cb0fe` (`Synching backlog`) added
  `2ybwnnsa`, `3wupbb0i`, `cwv3hf3w`, `fhgo52kh`, `h_1cwotz`, `hef4mjw4`,
  `jzitjv59`, and `t7nsgbor`.
- `e1762fe29bddeed1da440edefc5782bf11443266` (`Create index`) added
  `ilk3djzq`.
- `f9e85829e0e0233adb98d275eccf9ab4569b4413` (`WI-5441`) added
  `hl705ij2`.

Nine directories remain present. Only `hl705ij2` is absent from the worktree
and recorded as a tracked deletion. A single coherent snapshot loaded through
the canonical registry control plane resolves all ten paths to no registry
record.

Disposition is intentionally split and mechanically visible:

- WI-5704 prevents recurrence and adds the exact classifier/commit-checker
  behavior. It deletes none of the ten paths.
- WI-5706 remains exactly as owner-authorized and repairs only the current
  `hl705ij2` tracked deletion from the contaminated WI-5441 finalization.
- WI-5722, `Remove nine legacy tracked transient Git indexes after recurrence
  prevention`, is open in PROJECT-GTKB-HOUSEKEEPING-HARDENING with linked
  TEST-11745. Its description enumerates the other nine paths, sequences their
  separately reviewed deletion after WI-5704 and WI-5706, requires coherent
  registry no-membership, and forbids registry mutation or history rewrite.

This reconciles the eight-file observation in
`bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md`: that
thread saw the eight `db07f9dcf` paths; the complete live population also
includes `ilk3djzq` and `hl705ij2`.

## Originating Advisory Correction

`bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
is the originating advisory. Its root-cause attribution to registry
reconciliation is incorrect. Repository-wide source search finds one root
creator: `_index_snapshot` in the protected-commit checker. Registry candidate
validation already creates differently named temporaries beneath
`.gtkb-state/bridge-candidate-validation`. Version 002's reviewer disclosed and
accepted this correction; WI-5704 implements the proven source fix.

## Requirement Sufficiency

Existing requirements sufficient. The owner decision, WI-5704, TEST-11722,
linked specifications, exact five-path PAUTH, and WI-5722 cleanup disposition
fully determine the work without a new specification or owner choice.

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

## Prior Deliberations And Related Artifacts

- `DELIB-202667518` - owner authorization for WI-5704's exact five-file scope.
- `DELIB-202667516` - separate owner authorization for WI-5706.
- `bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
  - originating advisory, with attribution corrected above.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md` -
  earlier eight-path observation reconciled above.
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md` - controlling GO
  for the separate one-path WI-5706 repair.
- `WI-5722` / `TEST-11745` - separate nine-path cleanup and linked integration
  test.

## Owner Decisions / Input

No additional owner decision is required. `DELIB-202667518` remains the exact
WI-5704 authority. WI-5722 is work capture, not implementation approval.

## Proposed Implementation

1. Route `_index_snapshot` through `_scratch_root(root)` and keep all immutable
   snapshot security behavior unchanged.
2. Add `.gtkb-index-*/` to `.gitignore` as a defensive backup control.
3. Add an exact root-transient matcher to the commit checker. Reject add,
   modify, copy, rename-source, and rename-destination recurrence. Permit only a
   pure deletion proven unregistered by a coherent canonical registry snapshot.
4. Add the exact case-preserving raw-path classifier described in F1. It grants
   `repository_metadata` only to `.gtkb-index-[a-z0-9_]{8}/index`.
5. Add focused classifier, staging, registry, cleanup, interruption,
   real-index, CPython-name-contract, and negative-shape tests.

## Explicit Exclusions

This proposal performs no KB mutation.

- No deletion, restoration, staging, or commit of any of the ten currently
  tracked transient-index paths.
- No WI-5706 or WI-5722 implementation.
- No registry declaration, packaged mirror, projection, journal, MemBase, or
  `groundtruth.db` mutation.
- No taxonomy TOML edit; `repository_metadata` already exists.
- No change to generic extension or case-normalized classifier rules.
- No bridge/advisory deletion, dispatcher activation, history rewrite, push,
  credential action, release, or deployment.

## Specification-Derived Verification Plan

| Specification | Verification | Required result |
|---|---|---|
| `GOV-PLATFORM-SOT-REGISTRY-001` | Load one coherent registry snapshot and resolve exact unregistered and registered transient fixtures | Only canonical no-membership can grant deletion exception; registry generation stays unchanged. |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Stage registered and unregistered exact transient deletions | Registered identity deletion is denied; exact unregistered deletion passes this transient rule. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Test exact raw positive; uppercase, malformed, directory, nested, traversal, alternate leaf, and unrelated dot negatives | Only exact lowercase eight-character `/index` is `repository_metadata`; uppercase and malformed fallback as specified; `.md`/`.json`/`.jsonl` retain `governance_evidence`; no negative becomes `repository_metadata`. |
| `GOV-WORK-TREE-HYGIENE-001` | Exercise `_index_snapshot` on normal exit, exception, and `KeyboardInterrupt`; scan root and `.gtkb-state` | No transient directory remains after each outcome and none is created at root. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Repeat focused snapshot and path-inventory tests | Every run and exit path reaches the same no-transient postcondition. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Applicability preflight, post-GO implementation start, and packet inspection | Active PAUTH and packet contain exactly five targets/classes; exclusions remain excluded. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict lifecycle and compliance audits | Valid append-only NEW -> NO-GO -> REVISED -> GO/NO-GO sequence and independent post-implementation verdict. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Final-content proposal/report audit | No missing required or advisory specification and no unmapped cited authority. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Live PAUTH/project/WI lookup | Exact triple resolves and WI-5704 appears once. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Report every row plus focused command results | Every linked requirement has fresh independent evidence. |
| `GOV-STANDING-BACKLOG-001` | Show WI-5704, WI-5706, WI-5722, TEST-11722, and TEST-11745 | Prevention and both cleanup cohorts remain separate and visible. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve advisory correction, revision chain, and terminal lifecycle evidence | No historical artifact is edited; WI-5704 resolves only after VERIFIED. |

Focused implementation and quality commands remain those declared in version
001. The post-implementation dry-run must show WI-5706's sole target classifies
as `repository_metadata` without acquiring its claim or creating its packet.

## Acceptance Criteria

1. `_index_snapshot` creates no root `.gtkb-index-*` directory and cleans its
   scratch directory after success, exception, and interruption.
2. `.gitignore` contains one effective `.gtkb-index-*/` defensive rule.
3. The commit checker rejects exact transient add, modify, copy, rename source,
   and rename destination; only pure canonical-registry-confirmed unregistered
   deletion receives the exception.
4. Missing/incoherent registry authority or any matching registry record cannot
   grant the deletion exception.
5. Only the exact case-preserving raw
   `.gtkb-index-[a-z0-9_]{8}/index` shape becomes `repository_metadata`.
   Uppercase and malformed shapes retain their specified fallback classes;
   alternate `.md`/`.json`/`.jsonl` leaves remain `governance_evidence`; no
   negative becomes `repository_metadata`.
6. A regression test pins the current private CPython temporary-name alphabet
   and length so a runtime change triggers explicit review.
7. The 159-test baseline remains green with new regressions, and focused Ruff
   check/format gates pass.
8. Registry declaration, mirror, projection, generation digest, and record count
   are unchanged.
9. WI-5706's exact target becomes mechanically describable, but WI-5704 does
   not claim, packetize, stage, or mutate it.
10. WI-5722 durably owns the other nine deletions and remains separately
    unapproved until its own governed review.

## Risk / Rollback

The principal risks remain over-broad classification and an identity-deletion
exception that bypasses registry authority. Case-preserving exact matching,
explicit fallback assertions, coherent registry resolution, and negative tests
bound those risks. Relocation tests preserve chmod, identity, sanitized
environment, real-index non-mutation, and reparse-point checks.

Before finalization, rollback restores only the five target files and clears
only WI-5704 staging. After terminal commit, defects require append-only
repair-forward; no reset, amend, rebase, history rewrite, or push is authorized.

## Files Expected To Change

- `.gitignore`
- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`

## Recommended Commit Type

`fix`
