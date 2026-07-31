NEW
::init gtkb lo
::open build

# Defect-Fix Proposal - Make protected-commit terminal evidence consume corrected bridge lifecycle resolution

bridge_kind: prime_proposal
Document: gtkb-wi5633-protected-commit-corrected-chain-evidence
Version: 001
Date: 2026-07-19 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5633

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Make the protected-commit checker consume the terminal state and implementation
pair exposed by the public WI-5629 exact-thread lifecycle resolver instead of
reparsing numbered bridge history through a second consumer-specific algorithm.

Also close the atomic-finalization gap that precedes terminal history: during
one commit-in-progress, the checker may derive candidate evidence from exactly
one staged helper-shaped VERIFIED artifact only when its declared
same-transaction path set equals the complete staged path set and every existing
bridge-compliance, author-independence, report-linkage, implementation-packet,
and target-scope check succeeds. This transaction-local route must not classify
or normalize malformed historical bridge files and must never become a stale
fallback for ordinary implementation.

## Hard Dependency

Implementation is prohibited until all of the following are true:

1. WI-5629 is latest terminal VERIFIED.
2. The WI-5629 implementation claim has been released.
3. The public resolver contract is available from
   `scripts/bridge_lifecycle_resolver.py`.
4. WI-5633 has independent Loyal Opposition GO, an exact matching Prime
   Builder claim, and a finalized implementation-start packet for only the two
   declared targets.

The proposal may be reviewed before WI-5629 completes. No WI-5633 source or
test mutation may begin before the dependency gates above are satisfied.

## Defect / Reproduction

WI-5474's source and test implementation passed independent verification, but
the mandatory atomic VERIFIED helper could not commit the protected
`groundtruth-kb/src/groundtruth_kb/git_lifecycle/*` paths. The durable
independent verdict at
`bridge/gtkb-wi5474-exact-path-tracked-file-restore-008.md` records the
finalization-only NO-GO.

The direct protected-path check reproduces the defect:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\check_protected_commit_authorization.py --paths groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/repository.py groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py --json
```

Observed result:

```text
status: fail
live_go_packets_scanned: 451
live_go_packets_valid: 2
terminal_verified_packets_scanned: 451
terminal_verified_threads_loaded: 4
gtkb-wi5474-exact-path-tracked-file-restore:
Version metadata '002 (GO; independent Loyal Opposition review)' does not match 002:
bridge/gtkb-wi5474-exact-path-tracked-file-restore-002.md
```

The checker currently calls `implementation_authorization.bridge_entry()` for
every packet-backed terminal candidate and then independently searches
`entry.versions` for a GO-approved proposal. Once WI-5629 makes
`bridge_entry()` consume the strict shared resolver, the checker still needs to
consume the resolver's named terminal fields directly. More importantly, the
pre-commit invocation occurs before the new VERIFIED artifact is committed, so
there is no terminal historical result yet. The staged VERIFIED artifact
already carries a helper-generated exact same-transaction path set, but the
checker currently validates only that the section exists; it does not use a
fully validated candidate to clear the protected paths in that exact
transaction.

## Requirement Sufficiency

Existing requirements are sufficient. This work changes no bridge status
semantics and creates no new authority source. It connects two existing
governed evidence paths:

1. committed terminal evidence comes from the WI-5629 public lifecycle result;
2. commit-in-progress evidence comes from one exact staged VERIFIED candidate,
   bounded by the canonical bridge-compliance and implementation-authorization
   controls already required by the atomic finalizer.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

WI-5629's resolver, implementation-authorization consumer, and their tests are
dependencies only. They are not WI-5633 mutation targets.

## Specification Links

- `DCL-VERIFIED-BRIDGE-HISTORY-001` - terminal protected-path evidence must
  derive from a valid VERIFIED lifecycle rather than an ad hoc status scan.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct numbered bridge
  authority, exact links, independent review, and fail-closed malformed state.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - pending or uncorrected NO-ACTION state
  remains non-authorizing.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - a transaction-local VERIFIED candidate
  must remain independently authored relative to the implementation report.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - commit authorization is derived from the
  current exact thread, staged set, and current governed packet state.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5629 must be terminal before this
  resolver consumer is implemented.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - protected commit evidence is evaluated
  against the current repository and exact staged transaction.
- `GOV-WORK-TREE-HYGIENE-001` - the checker must inspect only the supplied or
  staged path set and must not mutate or absorb unrelated worktree bytes.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - no dispatcher, runtime, route,
  lease, harness, deployment, or release behavior changes in this slice.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation still requires
  exact GO, claim, target scope, and finalized implementation-start authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time
  PAUTH and exact target checks remain mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links
  the requirements that define its implementation and verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent VERIFIED
  requires executed tests mapped to the specifications above.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal declares
  its project, PAUTH, work item, and exact target paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the repository pre-commit checker is a
  harness-neutral enforcement backstop.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - this is GT-KB platform governance
  tooling, not adopter application code.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the discovered finalization blocker
  is preserved as WI-5633 and TEST-11678 before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - proposal, implementation report,
  test evidence, and independent verdict remain durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the NO-GO finding flows through a
  governed defect-fix lifecycle rather than an inline workaround.
- `GOV-STANDING-BACKLOG-001` - WI-5633 remains tracked until independently
  VERIFIED.

## Prior Deliberations

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - owner decision
  that VERIFIED and its reviewed payload must commit in one transaction.
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-005.md` through
  `bridge/gtkb-wi5474-exact-path-tracked-file-restore-008.md` - approved
  implementation, report, and independent finalization-only NO-GO evidence.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md` and
  `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-012.md` - accepted
  exact-thread resolver contract and independent GO.
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-006.md` - dependent
  consumer requirement that readers use the shared resolver contract.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md` - malformed
  status quarantine precedent; malformed bytes never become valid status.
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md` - finalized
  schema-v3 implementation-start packet contract.

## Owner Decisions / Input

- `DELIB-202666274` and active
  `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` authorize
  governed Tree Stabilization source, test, bridge, metadata, and governance
  evidence work while preserving exact GO, claim, implementation-start,
  independent verification, and separate Git-operation gates.
- The active owner-directed fleet and Tree Stabilization objective requires
  every discovered blocker to be corrected through governed work and
  independent verification.
- No additional owner decision is required for proposal review. This proposal
  does not authorize implementation before its hard dependency and normal
  bridge gates clear.

## Proposed Scope

1. After WI-5629 is terminal and unclaimed, replace the checker's historical
   terminal-evidence use of `bridge_entry()` plus
   `_approved_proposal_after_go()` with the WI-5629 public lifecycle resolver.
2. For committed terminal evidence, require a resolver result whose latest
   strict state is VERIFIED, whose terminal implementation/report relationship
   is valid, and whose approved Prime artifact supplies concrete target paths.
3. Preserve exact-thread enumeration. Do not add a local numbered-file parser,
   decorated-token normalizer, prefix scan, legacy no-suffix fallback, or
   malformed-history skip.
4. Preserve all WI-5629 fail-closed outcomes. Pending correction, missing
   implementation pair, unresolved blocking diagnostics, duplicate or skipped
   versions, unreadable files, wrong role/document/link, non-adjacency,
   cross-thread state, multiple malformed files, and ambiguous quarantine
   provide no terminal evidence.
5. Keep live-GO packet evidence first in precedence and preserve existing
   protected-path classification.
6. Add one transaction-local candidate evaluator used only when the selected
   path set contains exactly one staged numbered bridge file whose exact first
   status is VERIFIED.
7. Parse only that VERIFIED artifact's `Commit Finalization Evidence`
   same-transaction path manifest. This is a commit manifest parser, not a
   lifecycle parser.
8. Require the normalized manifest set to equal the complete normalized staged
   path set. Missing paths, extra paths, duplicates, globs, directory
   shorthand, path escape, `.git` paths, or a second VERIFIED candidate fail
   closed.
9. Reuse existing governed validators to require a clean bridge-compliance
   audit, valid evidence anchors, concrete author metadata, exact
   Document/Version/Responds-to linkage to the latest Prime implementation
   report, and session-context review independence.
10. Require an existing internally consistent finalized schema-v3
    implementation-authorization packet for the same bridge id. Its
    packet-bound target scope must authorize every protected staged path, and
    its proposal/GO identity must remain internally consistent. A missing,
    corrupt, hash-mismatched, wrong-bridge, non-finalized, or out-of-scope
    packet fails closed.
11. The transaction-local candidate may clear only protected paths present in
    both the exact manifest and packet target scope. It cannot authorize
    additional implementation, mutation, staging, or a later transaction.
12. Preserve the existing terminal VERIFIED file requirement for Commit
    Finalization Evidence and preserve all existing output keys and human/JSON
    diagnostics. Add a distinct evidence classification for a cleared
    transaction-local candidate.
13. Add focused positive and negative tests under TEST-11678 without modifying
    WI-5629's four owned targets.

## Out Of Scope

- Editing any WI-5629 target.
- Changing the atomic finalizer or bridge-compliance hook.
- Rewriting, deleting, normalizing, or superseding historical bridge bytes.
- Treating decorated historical metadata as valid lifecycle state.
- Dispatcher, TAFE, harness, eligibility, route, lease, daemon, or runtime
  mutation.
- MemBase or `groundtruth.db` mutation.
- Git staging, commit, push, history rewrite, merge, deployment, release, or
  destructive cleanup.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5633; TEST-11678; WI-5474 v008; WI-5629 v011-v012; DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE",
  "canonical_authority": "DCL-VERIFIED-BRIDGE-HISTORY-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "primary_route": "live GO packet or shared terminal lifecycle result; during the one atomic commit, one fully validated staged VERIFIED manifest",
  "before_behavior": "The checker reparses packet-backed terminal threads and rejects WI-5474 before its helper-generated staged VERIFIED candidate can authorize the protected paths in the same transaction.",
  "after_behavior": "Committed history uses the shared resolver. One exact staged VERIFIED candidate can clear only its equal staged manifest and packet-authorized protected paths after all existing validators pass.",
  "self_descriptive_naming": "historical resolver evidence and transaction-local candidate evidence remain separate named classifications",
  "obsolete_guidance_disposition": "The checker's private terminal-history GO/proposal search is removed; no bridge protocol or historical artifact is retired.",
  "history_preservation": "Every existing numbered bridge artifact remains byte-identical and append-only.",
  "baseline": {
    "historical_reader": "check_protected_commit_authorization calls implementation_authorization.bridge_entry and then privately searches entry.versions for GO-approved proposal state",
    "atomic_candidate": "the staged VERIFIED finalization section is checked for presence but cannot clear its own protected same-transaction paths",
    "live_reproduction": "WI-5474 finalization loads only 4 of 451 packet-backed terminal threads and fails on decorated v002 Version metadata",
    "owned_targets": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ]
  },
  "expected_result": {
    "historical_reader": "terminal evidence consumes the WI-5629 public lifecycle result and contains no second numbered-history parser",
    "atomic_candidate": "one fully validated staged VERIFIED manifest clears only an equal staged set intersected with its finalized packet target scope",
    "negative_state": "pending, malformed, ambiguous, forged, self-reviewed, stale-linked, packet-invalid, or scope-mismatched candidates clear no protected path",
    "wi5474": "the WI-5474-shaped fixture can complete the mandatory atomic VERIFIED commit without rewriting or normalizing historical bridge bytes"
  },
  "essential_context_preservation": "Preserve WI-5633 and TEST-11678, WI-5474 v005-v008, WI-5629 v011-v012 and its terminal dependency, the VERIFIED commit-finalization owner directive, exact protected-path classification, live-GO precedence, independent review, schema-v3 implementation-start authority, and the two-file ownership boundary.",
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the hash-pinned WI-5633 hunks. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun TEST-11678, the full protected-commit checker suite, resolver integration tests, and the WI-5474-shaped finalization fixture."
  },
  "hard_invariants": [
    "The WI-5629 resolver is the only numbered lifecycle parser.",
    "Pending or structurally ambiguous history never authorizes a protected commit.",
    "A staged VERIFIED candidate authorizes only the exact equal staged manifest and packet scope.",
    "Manual or malformed verdicts cannot bypass bridge compliance, evidence-anchor, author-independence, report-link, or packet checks.",
    "No dispatcher or Git state is mutated by implementation or tests."
  ],
  "fail_closed_conditions": [
    "WI-5629 is not terminal VERIFIED or still claimed.",
    "Resolver result is structural error, pending correction, nonterminal, or lacks the required artifact relationship.",
    "Candidate count is not exactly one or its manifest differs from the staged set.",
    "Candidate validation, author independence, report linkage, packet integrity, or protected target scope fails.",
    "Any target outside the two declared WI-5633 files would need modification."
  ]
}
```

## Specification-Derived Verification Plan

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Shared historical lifecycle authority | Unit fixtures using ordinary terminal VERIFIED and WI-5629 corrected terminal VERIFIED results | Checker consumes named resolver fields and loads target evidence without a private GO/proposal history search. |
| Pending and malformed denial | Pending NO-ACTION, unlinked correction, duplicate, gap, unreadable, wrong-role, wrong-document, non-adjacent, and multiply malformed fixtures | No terminal evidence; stable fail-closed diagnostic. |
| Transaction-local positive path | WI-5474-shaped fixture with one staged helper-shaped VERIFIED candidate, exact manifest, independent author, valid report link, and finalized schema-v3 packet | Every packet-scoped protected path clears with transaction-local evidence and no historical metadata normalization. |
| Exact manifest equality | Missing, extra, duplicate, glob, directory, path-escape, `.git`, explicit-path-only, and second-candidate fixtures | Candidate route denies every mismatch. |
| Candidate validity | Invalid status, stale Responds-to, wrong Document/Version, missing metadata, self-review, failed applicability, bad evidence anchor, or missing finalization section | Candidate route denies before protected paths clear. |
| Packet-bound scope | Missing/corrupt/hash-mismatched/wrong-bridge/non-finalized packet and protected path outside packet targets | Candidate route denies with stable evidence error. |
| Live GO precedence | Existing live-GO positive fixtures | Existing evidence classification and behavior remain unchanged. |
| Terminal bridge file gate | Existing VERIFIED-without-finalization-evidence fixtures | Missing Commit Finalization Evidence remains a blocking finding. |
| Existing checker regression | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0. |
| Resolver integration | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0 without changing WI-5629 bytes. |
| Static quality | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Formatting | `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Syntax | `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Nonimpairment | Before/after scoped hashes, `git diff --check`, dispatcher health read only | Only the two authorized targets change; no runtime, configuration, index, or dispatcher mutation. |

## Acceptance Criteria

- WI-5629 is terminal VERIFIED and unclaimed before implementation starts.
- The checker uses the public WI-5629 resolver for committed terminal
  lifecycle evidence and contains no second numbered-history parser.
- One helper-shaped staged VERIFIED candidate can clear the exact
  WI-5474-shaped atomic commit fixture without treating its decorated
  historical metadata as valid state.
- Transaction-local authorization requires exact staged-manifest equality,
  clean canonical candidate validation, independent author context, exact
  latest-report linkage, and finalized packet-bound target scope.
- Every negative fixture fails closed and clears no protected path.
- Live-GO precedence, protected-path classification, terminal finalization
  evidence checks, JSON schema, and human diagnostics remain compatible.
- TEST-11678, focused regressions, Ruff, formatting, compile, and diff checks
  pass.
- Independent Loyal Opposition verifies the implementation before any focused
  commit.

## Risks / Rollback

The primary risk is accidentally turning the transaction-local route into a
manual verdict bypass. Exact manifest equality, canonical candidate validation,
review independence, latest-report linkage, and packet-bound target scope are
therefore conjunctive requirements; any missing input denies the entire route.

The secondary risk is duplicating WI-5629 lifecycle semantics. The
implementation must import and consume its public result for historical state
and may parse only the staged commit manifest. If implementation requires a
second numbered-history parser or a WI-5629 target change, stop and revise this
proposal through independent review.

Before terminal verification, rollback is a hash-pinned reverse of only the
WI-5633 hunks. After VERIFIED, rollback requires a new governed correction.
Bridge artifacts remain append-only and are never deleted as rollback.

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`fix`
