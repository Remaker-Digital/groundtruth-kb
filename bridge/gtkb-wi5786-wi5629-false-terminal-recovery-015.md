REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe1fd-61a9-7742-a7bf-5e44e1ec9de4
author_model: OpenAI GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; harness A; resolved role prime-builder via ::init gtkb pb; evidence-only SHA-remap correction
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5786-wi5629-false-terminal-recovery
Version: 015
Author: Prime Builder (Codex, harness A)
Date: 2026-08-09 UTC
Responds to: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-014.md
Controlling GO: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-012.md
Approved proposal: bridge/gtkb-wi5786-wi5629-false-terminal-recovery-011.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5786-BY-REFERENCE-TERMINAL-RECOVERY-20260808
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5786

target_paths: ["bridge/gtkb-wi5786-wi5629-false-terminal-recovery-013.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: chore

No KB mutation, MemBase mutation, source/test mutation, branch switch, merge,
graft, history rewrite, dispatcher mutation, or TAFE operation is performed.

# WI-5786 v015 — corrected by-reference evidence using canonical SHA remaps

## Revision Claim

This revision accepts `-014` F1 as a current-state finding and corrects the two
stale post-reset commit identifiers in `-013`. The implementation and historical
commits were not lost from canonical `develop`; they were deterministically
remapped when `develop` was reset to the rewritten `origin/develop` lineage on
2026-08-09. The remapped commits have byte-identical trees and identical stable
patch IDs to the old commits and are ancestors of current `develop`.

No merge or branch switch is required. The current target branch is the checked
out canonical `develop` branch at `b7271afd61b79b9a59ec75241f11a24fbdb645b1`,
also `origin/develop`. This report corrects evidence only and preserves all
foreign worktree changes.

## Current Implementation Authority

- Resumable head: `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-014.md`
  (`NO-GO`).
- Controlling GO: `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-012.md`.
- Approved proposal: `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-011.md`.
- Exact work-intent claim: row `37565`, session
  `019fe1fd-61a9-7742-a7bf-5e44e1ec9de4`, acquired
  `2026-08-09T23:12:07Z`.
- Fresh schema-v3 implementation-start packet:
  `sha256:52917a6a992456b073255c25cb3cbefd30a56bba146d0e3fb72108a3cc92850f`,
  created `2026-08-09T23:13:29Z`, expires `2026-08-09T23:58:29Z`.
- Singleton PAUTH v1 operation-time evaluation: `allowed: true`; target remains
  the approved factual v013 report path, mutation class `bridge`.

## Response To `-014` F1

### Canonical SHA remap

| Evidence role | Pre-reset SHA retained as historical alias | Canonical `develop` SHA | Equivalence proof | Current ancestry |
| --- | --- | --- | --- | --- |
| immutable WI-5629 implementation | `1aa2182bbe9ab1d8fd0338bc737a1e33b54531b4` | `4fa46ce33aff9dd62622f86a048818ce61151c83` | same tree `a4a2ad7c2835498232d7626ff3fd5adcecba5f45`; same stable patch ID `5b7175bb07e529df449e9ebc4f1527f333c5441b`; same subject and commit timestamp | ancestor of current `HEAD` (exit 0) |
| historical false-terminal chain | `db07f9dcfe7e7de8addc850729209278472cb0fe` | `4cff5b9c8f3fb2a71e2bda63c12031a14fe2e7fe` | same tree `78cfe5c79cd540337af6c925e54ca28bdbea794c`; same stable patch ID `1daa3b8f804850c3b92dd53a071b97747127d32b`; same subject and commit timestamp | ancestor of current `HEAD` (exit 0) |

The old commit IDs remain reachable only from `research` and correctly return
exit 1 when tested against current `develop`; they are retained solely as
historical aliases. The owner handoff for the rewritten lineage explicitly
requires post-2026-06-29 SHA references to be remapped. The new commit IDs above
are the canonical references used for current ancestry and finalization.

### Why `-013` and `-014` observed different results

The ancestor statements in `-011`, `-012`, and `-013` were reproducible against
the then-current `develop` lineage: both old IDs are ancestors of
`132e95ebf2005689594d427e9c5aaa931afdb238` and of later local develop tip
`2f1a169ec5b180fe46dea1ec6fb05d7ee05e301f` (exit 0). The local reflog then
records `develop@{2026-08-09 11:32:50 -0700}: reset: moving to origin/develop`,
after which the old IDs no longer occur in the canonical ancestry.

`-014` was therefore correct to fail the old identifiers against current
`develop`. The required correction is identifier remapping, not a merge of
already-equivalent content and not selection of `research` as the finalization
branch.

## Corrected By-Reference Evidence

1. `4fa46ce33aff9dd62622f86a048818ce61151c83` is an ancestor of current
   `develop` and contains exactly:
   - `platform_tests/scripts/test_implementation_authorization.py`
   - `scripts/implementation_authorization.py`
2. `4cff5b9c8f3fb2a71e2bda63c12031a14fe2e7fe` is an ancestor of current
   `develop` and retains the 532-path historical classification.
3. Each remapped commit is tree-identical and stable-patch-identical to the
   corresponding historical alias, so the evidence meaning is preserved.
4. No source or test byte is changed or staged by this revision.
5. The `-014` reviewer independently reran the focused suite and accepted
   `163 passed`; that accepted result is carried forward unchanged.

## Prospective Terminal Cohort

The earlier four-file expectation expanded lawfully because v014 was NO-GO.
The prospective terminal cohort is now exactly v011 through the future
independent v016 verdict: v011, v012, v013, v014, v015, and v016. Versions
v001-v010 and every source/test subject remain outside this recovery
finalization cohort. A terminal verdict must use the canonical atomic finalizer
and the remapped `develop` evidence above; any failure leaves the chain
non-terminal.

## Requirement Sufficiency

Existing requirements remain sufficient. This report is the factual
identifier-remapping correction required by `-014`; it changes no product or
runtime behavior and does not widen the owner-waived recovery scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260808-WI5786-BY-REFERENCE-TERMINAL-RECOVERY-WAIVER` — exact owner
  waiver for immutable-commit verification and fresh-cohort recovery.
- `DELIB-20260801-WI5786-FALSE-TERMINAL-RECOVERY-APPROVAL` — prior bounded
  recovery approval.
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-011.md` — approved
  evidence-only proposal.
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-012.md` — controlling GO.
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-014.md` — current
  lineage finding corrected here.

## Owner Decisions / Input

The durable waiver remains
`DELIB-20260808-WI5786-BY-REFERENCE-TERMINAL-RECOVERY-WAIVER`. The current owner
handoff additionally directs that post-2026-06-29 SHA references be remapped
after the rewritten canonical lineage. No new owner decision is required and no
scope is widened.

## Executed Evidence

| Requirement | Command / check | Result |
| --- | --- | --- |
| Implementation remap tree identity | `git rev-parse <old>^{tree} <new>^{tree}`; `git diff --quiet <old>^{tree} <new>^{tree}` | both tree IDs `a4a2ad7c...`; exit 0 |
| Implementation remap patch identity | `git show --pretty=format: <sha> | git patch-id --stable` for both IDs | both `5b7175bb...` |
| Historical remap tree identity | same tree commands for old/new historical IDs | both tree IDs `78cfe5c7...`; exit 0 |
| Historical remap patch identity | stable patch ID for both historical IDs | both `1daa3b8f...` |
| Canonical ancestry | `git merge-base --is-ancestor <remapped> HEAD` for both new IDs | exit 0 for both |
| Implementation inventory | `git diff-tree --no-commit-id --name-only -r 4fa46ce3...` | exactly two approved paths |
| Historical classification | path count for `4cff5b9c...` | 532 paths |
| Regression | `-014` independent review rerun | 163 passed; accepted |

No dispatcher or TAFE runtime state was inspected, invoked, or used as
authority.

## Specification-Derived Verification

| Specification / authority | Executed evidence | Result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | direct numbered v011-v014 chain plus exact v015 response | lawful NO-GO to REVISED continuation |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | exact claim and fresh schema-v3 resumption packet | allowed under singleton PAUTH v1 |
| `REQ-GTKB-GOVERNED-GIT-LIFECYCLE-001` | tree, stable patch, inventory, reflog, and current ancestry checks | remapped evidence is reproducible on canonical `develop` |
| `GOV-WORK-TREE-HYGIENE-001` | no branch switch, merge, source/test edit, stage, commit, push, or rewrite | foreign work preserved |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | accepted independent 163-test result plus remap-equivalence checks | pass |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all live artifacts remain under `E:/GT-KB` | pass |

## Acceptance Status

1. `-014` F1 is corrected with exact canonical remapped IDs.
2. Both remapped commits are ancestors of current `develop`.
3. Tree and stable patch identity prove the remapped commits preserve the old
   immutable evidence exactly.
4. The two-path and 532-path classifications reproduce under the new IDs.
5. The independent 163-test result remains accepted.
6. No branch, source, test, configuration, registry, database, dispatcher,
   TAFE, external, release, deployment, credential, or history mutation occurs.

## Risks And Rollback

The remaining risk is future citation of the historical aliases as though they
were canonical `develop` ancestors. This report explicitly maps old to new and
requires the remapped IDs for current verification. If further lineage drift
occurs, the chain remains non-terminal and must be corrected append-only again.
Rollback is not applicable to source or runtime state because this revision is
evidence-only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
