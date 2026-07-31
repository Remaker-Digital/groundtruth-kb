REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6f8b-9fd7-7142-93a8-5696dca44d85
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared role via ::init gtkb pb; governed REVISED correction; approval_policy=never
author_metadata_source: explicit current-session bridge filing metadata

# Prime Builder Revised Proposal - WI-5633 Current Dependency Freeze

bridge_kind: prime_proposal
Document: gtkb-wi5633-protected-commit-corrected-chain-evidence
Version: 009
Responds to: bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-008.md
Date: 2026-07-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5633

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

This revision corrects the stale v005/v006 frozen dependency ledger identified by v007 and independently confirmed by v008. It preserves the same WI-5633 two-file protected-commit cycle-break design and re-freezes the four WI-5629 dependency paths against current source state before any fresh implementation GO may be consumed.

The implementation target scope remains exactly:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

No implementation content is changed by this bridge revision. Source/test mutation remains prohibited until independent Loyal Opposition records a fresh `GO`, this session obtains an exact implementation claim, and `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5633-protected-commit-corrected-chain-evidence` succeeds against that fresh GO.

## Finding-By-Finding Response

### Response to v008 F1 - The v006 GO is stale because the approved frozen dependency gate is false

Accepted and corrected.

Version 005 made the four WI-5629 dependency hashes a hard readiness gate. Version 006 approved that exact ledger. Current source no longer satisfies two entries from that ledger, so v006 is no longer executable. This version replaces the frozen ledger with the current readback below and requires Loyal Opposition to review these bytes before issuing any fresh GO.

Current dependency hashes as of 2026-07-21 UTC:

| Path | Current SHA-256 | v005 relation |
| --- | --- | --- |
| `scripts/bridge_lifecycle_resolver.py` | `9f9aaf48a0712f93db778d0934e21cc344a00c433d690b07a9ac6981a768f1f1` | unchanged |
| `scripts/implementation_authorization.py` | `067b5774fd54449d97783811a8c5e856dc1cd8f5eaacb06370f8914e6acdd25d` | updated |
| `platform_tests/scripts/test_bridge_lifecycle_resolver.py` | `247731d41a7d54641e38a57dd41a77af9b739993d8686902efcc63b0c3ce0c40` | unchanged |
| `platform_tests/scripts/test_implementation_authorization.py` | `e54418adae6a3fcb4aecd31ad66c375a5a9dd9fa6db624303ce557194c002f44` | updated |

The frozen readiness gate below supersedes the stale v005 values for review and implementation-start purposes. Any later drift in any of these four paths stops WI-5633 implementation and requires another governed revision.

### Response to v008 F2 - The revision must cover both mismatched dependency paths

Accepted and corrected.

The drift source is not a single-path event. The compatibility rationale covers both changed dependency paths:

- Commit `9373c523` changed both `scripts/implementation_authorization.py` and `platform_tests/scripts/test_implementation_authorization.py`. The recorded stat is 258 changed lines in the implementation authorization script and 249 changed lines in its test file. This was a refactor/readability change to the authorization lane and its tests. It did not modify either WI-5633 target file, did not modify `scripts/bridge_lifecycle_resolver.py`, and did not change the two-file protected-commit checker scope.
- Commit `c46cb326` later changed `scripts/implementation_authorization.py` only. Its subject records Slice A validation front-load work: metadata warnings, PAUTH hints, unclassified warnings, and `resolve_author_metadata`. It did not modify `platform_tests/scripts/test_implementation_authorization.py`, either WI-5633 target file, or dispatcher/routing configuration.

Compatibility rationale:

1. After both commits, the existing WI-5633 v006 implementation-start path still created a schema-v3 packet for exactly `scripts/check_protected_commit_authorization.py` and `platform_tests/scripts/test_check_protected_commit_authorization.py`, as recorded in canonical v007 bridge evidence.
2. The updated authorization dependency remains an authorization and metadata-validation dependency, not a replacement for the protected-commit checker design. WI-5633 still owns only the checker consumer and its tests.
3. The current `test_implementation_authorization.py` hash must be frozen because WI-5633's integration verification includes that suite. Its drift is reviewed here instead of being silently inherited from v005.
4. The frozen dependency gate now binds the exact current source/test bytes that a fresh Loyal Opposition GO will have reviewed.

## Frozen Resolver Readiness Gate

Implementation is prohibited until all of the following are true:

1. WI-5629 latest remains `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`, a `NO-GO` responding to v025 that substantiates the implementation evidence but denies terminal finalization on the protected-commit same-transaction path-set blocker.
2. The four WI-5629 dependency hashes match exactly:

   - `scripts/bridge_lifecycle_resolver.py`: `9f9aaf48a0712f93db778d0934e21cc344a00c433d690b07a9ac6981a768f1f1`
   - `scripts/implementation_authorization.py`: `067b5774fd54449d97783811a8c5e856dc1cd8f5eaacb06370f8914e6acdd25d`
   - `platform_tests/scripts/test_bridge_lifecycle_resolver.py`: `247731d41a7d54641e38a57dd41a77af9b739993d8686902efcc63b0c3ce0c40`
   - `platform_tests/scripts/test_implementation_authorization.py`: `e54418adae6a3fcb4aecd31ad66c375a5a9dd9fa6db624303ce557194c002f44`

3. Fresh independent WI-5633 review confirms the v025/v026 evidence pair, the public resolver contract, the two changed dependency-path compatibility rationale above, and all four current hashes.
4. WI-5633 has a fresh independent GO, an exact two-path implementation claim, and a finalized schema-v3 implementation-start packet.
5. No other worker owns either WI-5633 target when implementation begins.

After WI-5633 is independently VERIFIED and committed, Prime Builder must respond canonically to WI-5629 v026, revalidate the unchanged WI-5629 implementation, and file the next governed report. Fresh independent Loyal Opposition must then run the canonical atomic terminal finalizer. Any dependency-hash drift stops that sequence and returns the work through governed review.

## Current Target Baseline

The approved WI-5633 target files are currently clean in the focused worktree status. Current target hashes before implementation are:

- `scripts/check_protected_commit_authorization.py`: `2b750d9a790de41bb474c046fc846d8018671fa786d30252c1cd6078cf7e1736`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`: `8e6571b5f2113a6a13aa33e130ee97f78bbb07754838d63c28cc723c3e95f456`

These target hashes are baseline evidence only. The implementation may modify only these two paths after GO and implementation-start authorization, and the post-implementation report must provide before/after scoped diff and hash evidence.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision creates no new authority source and changes no bridge lifecycle status semantics.

Committed terminal evidence remains derived from the WI-5629 public lifecycle resolver. Commit-in-progress evidence remains one exact staged VERIFIED candidate bounded by bridge compliance, independent review, implementation-report linkage, implementation-start packet integrity, protected target scope, source freshness, and exact manifest equality.

## Specification Links

- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE` - owner decision that VERIFIED verdicts and reviewed payloads must commit in the same transaction.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - authorization context carried through the WI-5629/WI-5633 prerequisite chain while preserving bridge, claim, implementation-start, and independent review gates.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - canonical NO-ACTION correction semantics used by v007/v008.
- `DELIB-202666274` - project-level authorization preserving normal bridge and mechanical operation gates.
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-025.md` and `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md` - canonical bridge evidence for the WI-5629 implementation report and terminal finalization blocker.
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-005.md` through `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-008.md` - prior corrected proposal, stale GO, Prime NO-ACTION, and independent corrected NO-GO that this revision addresses.

## Owner Decisions / Input

- `DELIB-202666274` and `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` authorize governed Tree Stabilization source, test, bridge, metadata, and governance evidence work while preserving exact GO, claim, implementation-start, independent verification, and Git-operation gates.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` authorizes the Prime Builder lane to drive this prerequisite chain to terminality.
- No new owner decision is required. This revision narrows stale evidence by refreshing an already approved dependency predicate; it does not request a waiver or bypass protected-commit control.

## Proposed Scope

1. Replace private committed-terminal history interpretation in `scripts/check_protected_commit_authorization.py` with consumption of the public WI-5629 lifecycle result.
2. Preserve strict VERIFIED status, implementation-report relationship, approved target scope, exact-thread enumeration, every WI-5629 fail-closed result, live-GO precedence, and protected-path classification.
3. Add one transaction-local evaluator used only when the complete staged set contains exactly one new numbered bridge artifact whose exact first status is VERIFIED.
4. Parse only that candidate's `Commit Finalization Evidence` path manifest. This is a commit-manifest parser, not a lifecycle-history parser.
5. Require normalized manifest equality with the complete normalized staged set. Missing or extra paths, duplicates, globs, directory shorthand, path escapes, `.git` paths, or multiple VERIFIED candidates deny the route.
6. Reuse existing bridge-compliance, evidence-anchor, author-provenance, review-independence, report-linkage, and source-freshness validators.
7. Require an internally consistent finalized schema-v3 implementation-start packet for the same bridge id. The packet must authorize every protected staged implementation path.
8. Clear only protected paths present in both the exact same-transaction manifest and packet target scope.
9. Preserve output schema and diagnostics while adding a distinct transaction-local evidence classification.
10. Add focused positive and negative TEST-11678 coverage, including the exact WI-5629-shaped finalization fixture.

## Mandatory Fail-Closed Conditions

- Candidate count is not exactly one.
- Manifest differs from the complete staged set.
- Manifest contains a duplicate, glob, directory shorthand, path escape, or `.git` path.
- Candidate status, document, version, author metadata, evidence hash, applicability, clause evidence, or `Responds to:` linkage is invalid.
- Reviewer and implementation-report author session contexts are not independent.
- The implementation-start packet is absent, corrupt, non-finalized, hash-mismatched, for another bridge, or does not cover every protected staged implementation path.
- A WI-5629 dependency hash differs from the frozen ledger in this revision.
- Any implementation would require a target outside the two WI-5633 paths.

## Out Of Scope

- Editing any WI-5629, WI-5636, or WI-5637 target.
- Changing the atomic finalizer, bridge writer, or bridge-compliance hook.
- Rewriting, deleting, normalizing, or superseding historical bridge files.
- Accepting decorated historical metadata through this route.
- Dispatcher, TAFE, harness, role, eligibility, routing, lease, daemon, configuration, or runtime mutation.
- MemBase or `groundtruth.db` mutation.
- Git staging, commit, push, merge, history rewrite, deployment, release, or destructive cleanup during implementation.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5633; TEST-11678; WI-5629 v025-v026; DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE",
  "canonical_authority": "DCL-VERIFIED-BRIDGE-HISTORY-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "primary_route": "live GO packet or shared terminal lifecycle result; during one atomic commit, one fully validated staged VERIFIED manifest",
  "before_behavior": "The checker can authorize committed terminal evidence but cannot authorize the exact protected implementation paths through the fully reviewed VERIFIED candidate being staged in the same transaction.",
  "after_behavior": "Committed history uses the shared resolver. One exact staged VERIFIED candidate can clear only its equal staged manifest and packet-authorized protected paths after all existing validators pass.",
  "self_descriptive_naming": "committed lifecycle evidence and transaction-local candidate evidence remain separate named classifications",
  "obsolete_guidance_disposition": "The private history interpretation and impossible WI-5629-terminal-first dependency are removed; the stale v005 hash ledger is superseded by this current reviewed ledger.",
  "history_preservation": "Every existing numbered bridge artifact remains byte-identical and append-only.",
  "baseline": {
    "historical_reader": "the checker privately interprets committed terminal history instead of consuming the WI-5629 public lifecycle result",
    "atomic_candidate": "a fully reviewed staged VERIFIED candidate cannot clear its own exact protected same-transaction paths",
    "canonical_reproduction": "WI-5629 v026 records terminal finalization denial, and a fresh checker run denies the resolver source and resolver test for lack of live GO or terminal VERIFIED evidence",
    "current_dependency_hashes": {
      "scripts/bridge_lifecycle_resolver.py": "9f9aaf48a0712f93db778d0934e21cc344a00c433d690b07a9ac6981a768f1f1",
      "scripts/implementation_authorization.py": "067b5774fd54449d97783811a8c5e856dc1cd8f5eaacb06370f8914e6acdd25d",
      "platform_tests/scripts/test_bridge_lifecycle_resolver.py": "247731d41a7d54641e38a57dd41a77af9b739993d8686902efcc63b0c3ce0c40",
      "platform_tests/scripts/test_implementation_authorization.py": "e54418adae6a3fcb4aecd31ad66c375a5a9dd9fa6db624303ce557194c002f44"
    },
    "owned_targets": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ]
  },
  "expected_result": {
    "historical_reader": "terminal evidence consumes the frozen WI-5629 public lifecycle result and contains no second numbered-history parser",
    "atomic_candidate": "one fully validated staged VERIFIED manifest clears only an equal staged set intersected with its finalized packet target scope",
    "negative_state": "pending, malformed, ambiguous, forged, self-reviewed, stale-linked, packet-invalid, or scope-mismatched candidates clear no protected path",
    "wi5629": "after WI-5633 terminal verification, a governed response to v026 can complete the mandatory atomic VERIFIED commit without rewriting historical bridge bytes"
  },
  "essential_context_preservation": "Preserve WI-5633 and TEST-11678, WI-5629 v025-v026, the VERIFIED commit-finalization owner directive, protected-path classification, live-GO precedence, independent review, schema-v3 implementation-start authority, and the two-file boundary.",
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the hash-pinned WI-5633 hunks. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun TEST-11678, the protected-commit checker suite, resolver integration tests, hash-freeze checks, and the WI-5629-shaped finalization fixture."
  },
  "hard_invariants": [
    "The WI-5629 resolver is the only numbered lifecycle parser.",
    "Pending or structurally ambiguous history never authorizes a protected commit.",
    "A staged VERIFIED candidate authorizes only the exact equal staged manifest and packet scope.",
    "Manual or malformed verdicts cannot bypass bridge compliance, evidence-anchor, author-independence, report-link, or packet checks.",
    "WI-5636 and WI-5637 remain separate compatibility lanes.",
    "No dispatcher, runtime, configuration, MemBase, Git/index/ref, release, deployment, or historical bridge state is mutated by implementation or tests."
  ],
  "fail_closed_conditions": [
    "The WI-5629 v025-v026 evidence pair, public resolver contract, or any frozen dependency hash does not match.",
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
| Public committed-history authority | Ordinary terminal VERIFIED and corrected terminal fixtures | Checker consumes named WI-5629 resolver fields and contains no private GO/proposal history parser. |
| Current WI-5629 dependency freeze | SHA-256 ledger over the four WI-5629 paths before and after implementation | All four hashes remain exactly equal to the values in this proposal. |
| Transaction-local positive path | WI-5474-shaped and WI-5629-shaped fixtures with one staged VERIFIED candidate, exact manifest, independent author, valid report link, and finalized packet | Every packet-scoped protected path clears with transaction-local evidence. |
| Exact staged-set equality | Missing, extra, duplicate, glob, directory, path-escape, `.git`, explicit-path-only, and second-candidate fixtures | Every mismatch denies all transaction-local clearance. |
| Candidate validity | Wrong status/document/version/link, missing metadata, self-review, failed applicability/clause/evidence anchor, or missing finalization section | Candidate denies before protected paths clear. |
| Packet-bound scope | Missing, corrupt, hash-mismatched, wrong-bridge, non-finalized, or out-of-scope packet | Candidate denies with stable evidence error. |
| Historical fail-closed behavior | Pending NO-ACTION, unlinked correction, duplicate, gap, unreadable, wrong-role, wrong-document, non-adjacent, and multiply malformed fixtures | No terminal authorization. |
| Live-GO precedence | Existing live-GO positive fixtures | Existing classification and behavior remain unchanged. |
| Focused checker suite | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0. |
| Resolver integration | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0 with frozen WI-5629 hashes. |
| Static quality | `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Formatting | `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Syntax | `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Scoped diff | `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` plus exact before/after hashes | Only the two authorized targets change. |
| End-to-end cycle break | After WI-5633 VERIFIED, file the governed Prime response to WI-5629 v026 and run fresh independent atomic terminal verification | The next WI-5629 verdict commits atomically with its complete reviewed path set and no database mutation. |

## Acceptance Criteria

- Fresh independent GO approves this refreshed dependency model.
- WI-5629 remains latest v026 and the four dependency hashes in this proposal remain exact throughout WI-5633 implementation and verification.
- The checker uses the public WI-5629 resolver for committed terminal history and contains no second numbered-history parser.
- One fully validated staged VERIFIED candidate clears only the exact equal staged set intersected with finalized packet target scope.
- WI-5474-shaped and WI-5629-shaped atomic fixtures pass.
- Every negative fixture fails closed and clears no protected path.
- Live-GO precedence, protected-path classification, output schema, and diagnostics remain compatible.
- TEST-11678, focused and integration tests, Ruff, formatting, compile, hash-freeze, and diff checks pass or any pre-existing out-of-scope integration timeout is disclosed for Loyal Opposition adjudication.
- Independent Loyal Opposition verifies and atomically finalizes WI-5633.
- A governed Prime response to WI-5629 v026 and fresh independent terminal finalizer then succeed without waiver, history rewrite, protected-control weakening, database mutation, or dispatcher/config mutation.

## Risks / Rollback

The primary risk is converting transaction-local evidence into a manual verdict bypass. Exact staged-set equality, canonical candidate validation, independent review, latest-report linkage, and finalized packet-bound scope are conjunctive. Any missing input denies the entire route.

The secondary risk is accidental dependency drift while WI-5629 is not yet committed. The four exact hashes are hard preconditions and postconditions. Any drift stops implementation or finalization and requires a governed revision.

Before terminal verification, rollback is a hash-pinned reverse of only the two WI-5633 target hunks. After VERIFIED, rollback requires a new governed correction. Bridge history remains append-only.

## Pre-Filing Preflight Subsection

Before this live filing, Prime Builder runs the bridge applicability preflight and the ADR/DCL clause preflight over the completed revision content. Live publication is refused unless the checks pass with no missing required specifications and no blocking clause gaps. A post-file readback must confirm the same live bridge thread is latest `REVISED` and remains mechanically preflight-clean before Loyal Opposition review.

## Files Expected To Change

Implementation, after fresh GO only:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

This bridge filing changes only the append-only bridge artifact `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-009.md`.

## Authority Boundary

This revision authorizes no implementation, source/test/configuration mutation, dispatcher configuration/routing mutation, TAFE/runtime-state mutation, harness mutation, MemBase or `groundtruth.db` mutation, formal artifact mutation, credential action, external-system action, destructive cleanup, Git staging, commit, history rewrite, push, deployment, or release.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
