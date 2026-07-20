REVISED
::init gtkb lo
::open build

# Corrected Revised Defect-Fix Proposal - Break the protected-commit terminalization cycle

bridge_kind: prime_proposal
Document: gtkb-wi5633-protected-commit-corrected-chain-evidence
Version: 005
Responds to: bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-004.md
Date: 2026-07-19 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; sandbox=danger-full-access
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5633

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Correction Of Version 003

Version 003 contained two `Intuitiveness / Non-Impairment Disposition`
objects. Its first object retained stale pre-v026 dependency text, while its
second object described the current v025/v026 evidence model. The duplicate
objects made v003 contradictory and nonoperative.

This version replaces v003 in full. It contains exactly one current structured
disposition object. No source scope, test scope, dependency hash, acceptance
predicate, or fail-closed control is expanded by this correction.

## Claim

Break the circular dependency between WI-5629 terminalization and
protected-commit authorization without weakening either control.

The checker will use the frozen WI-5629 public lifecycle resolver for committed
terminal history. During one atomic finalization transaction, it may
additionally consume exactly one fully validated staged VERIFIED candidate
whose declared same-transaction manifest equals the complete staged path set
and whose protected paths are covered by the finalized implementation-start
packet for the reviewed implementation.

WI-5629 need not already be terminal because this transaction-local route is
the prerequisite that makes its terminal commit possible. WI-5629 source and
test bytes remain frozen read-only dependencies throughout WI-5633.

## Canonical Cycle Evidence

The canonical evidence is now complete:

1. `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-025.md` reports the
   finished resolver/authorization implementation and its complete verification
   matrix.
2. `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md` independently
   substantiates that implementation evidence but records terminal `NO-GO`
   because the protected-commit checker denied the same-transaction path set.
3. A fresh read-only checker reproduction applied the current checker to the
   four frozen WI-5629 paths. It returned `status: fail` because
   `scripts/bridge_lifecycle_resolver.py` and
   `platform_tests/scripts/test_bridge_lifecycle_resolver.py` lacked a live GO
   packet or terminal VERIFIED bridge evidence. The two authorization paths
   cleared through existing terminal evidence.
4. Canonical claim status for WI-5629 and WI-5633 is `null`.

Reproduction:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\check_protected_commit_authorization.py --paths scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py --json
status: fail
scripts/bridge_lifecycle_resolver.py: protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence
platform_tests/scripts/test_bridge_lifecycle_resolver.py: protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence
```

## Frozen Resolver Readiness Gate

Implementation is prohibited until all of the following are true:

1. WI-5629 latest is v026 `NO-GO`, responding to v025.
2. WI-5629 and WI-5633 claim status is `null`.
3. Fresh independent review confirms the v025/v026 evidence pair and the
   public resolver contract.
4. These SHA-256 values match exactly:

   - `scripts/bridge_lifecycle_resolver.py`:
     `9f9aaf48a0712f93db778d0934e21cc344a00c433d690b07a9ac6981a768f1f1`
   - `scripts/implementation_authorization.py`:
     `a13b6cde9dea029996e8e8b724c20bb71168c074078835894733ba55ddf07371`
   - `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
     `247731d41a7d54641e38a57dd41a77af9b739993d8686902efcc63b0c3ce0c40`
   - `platform_tests/scripts/test_implementation_authorization.py`:
     `b60ab4529115ce9056d65f2397d6c5b2efc4021832d3cfda15612a3536c6f8f5`

5. WI-5633 has fresh independent GO, an exact two-path implementation claim,
   and a finalized schema-v3 implementation-start packet.
6. No other worker owns either WI-5633 target.

After WI-5633 is independently VERIFIED and committed, Prime Builder must
respond canonically to WI-5629 v026, revalidate the unchanged implementation,
and file the next governed report. Fresh independent Loyal Opposition must
then run the canonical atomic terminal finalizer. Any dependency-hash drift
stops the sequence and requires governed revision.

## Proposed Scope

1. Replace private committed-terminal history interpretation in
   `scripts/check_protected_commit_authorization.py` with consumption of the
   public WI-5629 lifecycle result.
2. Preserve strict VERIFIED status, implementation-report relationship,
   approved target scope, exact-thread enumeration, every WI-5629 fail-closed
   result, live-GO precedence, and protected-path classification.
3. Add one transaction-local evaluator used only when the complete staged set
   contains exactly one new numbered bridge artifact whose exact first status
   is VERIFIED.
4. Parse only that candidate's `Commit Finalization Evidence` path manifest.
   This is a commit-manifest parser, not a lifecycle-history parser.
5. Require normalized manifest equality with the complete normalized staged
   set. Missing or extra paths, duplicates, globs, directory shorthand, path
   escapes, `.git` paths, or multiple VERIFIED candidates deny the route.
6. Reuse existing bridge-compliance, evidence-anchor, author-provenance,
   review-independence, report-linkage, and source-freshness validators.
7. Require an internally consistent finalized schema-v3 implementation-start
   packet for the same bridge id. The packet must authorize every protected
   staged implementation path.
8. Clear only protected paths present in both the exact same-transaction
   manifest and packet target scope.
9. Preserve output schema and diagnostics while adding a distinct
   transaction-local evidence classification.
10. Add focused positive and negative TEST-11678 coverage, including the exact
    WI-5629-shaped finalization fixture.

## Mandatory Fail-Closed Conditions

- Candidate count is not exactly one.
- Manifest differs from the complete staged set.
- Manifest contains a duplicate, glob, directory shorthand, path escape, or
  `.git` path.
- Candidate status, document, version, author metadata, evidence hash,
  applicability, clause evidence, or `Responds to:` linkage is invalid.
- Reviewer and implementation-report author session contexts are not
  independent.
- The implementation-start packet is absent, corrupt, non-finalized,
  hash-mismatched, for another bridge, or does not cover every protected staged
  implementation path.
- A WI-5629 dependency hash differs from the frozen ledger.
- Any implementation would require a target outside the two WI-5633 paths.

## Out Of Scope

- Editing any WI-5629, WI-5636, or WI-5637 target.
- Changing the atomic finalizer, bridge writer, or bridge-compliance hook.
- Rewriting or normalizing historical bridge files.
- Accepting decorated historical metadata through this route.
- Dispatcher, TAFE, harness, role, eligibility, routing, lease, daemon,
  configuration, or runtime mutation.
- MemBase or `groundtruth.db` mutation.
- Git staging, commit, push, merge, history rewrite, deployment, release, or
  destructive cleanup during implementation.

## Requirement Sufficiency

Existing requirements are sufficient. This revision creates no new authority
source and changes no bridge lifecycle status semantics. Committed terminal
evidence remains derived from the public lifecycle resolver. Commit-in-progress
evidence remains one exact staged VERIFIED candidate bounded by existing
bridge-compliance, independent-review, implementation-report linkage,
implementation-start packet, protected-target, and exact-manifest controls.

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

- `DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE`
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-202666274`
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-008.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-025.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-001.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-002.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-003.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-004.md`

## Owner Decisions / Input

`DELIB-202666274` and
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` authorize
governed Tree Stabilization source, test, bridge, metadata, and governance
evidence work while preserving exact GO, claim, implementation-start,
independent verification, and Git-operation gates.

No new owner decision is required. The canonical v026 failure is evidence for
the already authorized WI-5633 defect, not a request to bypass protected-commit
control.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5633; TEST-11678; WI-5629 v025-v026; WI-5474 v008; DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE",
  "canonical_authority": "DCL-VERIFIED-BRIDGE-HISTORY-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "primary_route": "live GO packet or shared terminal lifecycle result; during one atomic commit, one fully validated staged VERIFIED manifest",
  "before_behavior": "The checker can authorize committed terminal evidence but cannot authorize the exact protected implementation paths through the fully reviewed VERIFIED candidate being staged in the same transaction.",
  "after_behavior": "Committed history uses the shared resolver. One exact staged VERIFIED candidate can clear only its equal staged manifest and packet-authorized protected paths after all existing validators pass.",
  "self_descriptive_naming": "committed lifecycle evidence and transaction-local candidate evidence remain separate named classifications",
  "obsolete_guidance_disposition": "The private history interpretation and impossible WI-5629-terminal-first dependency are removed; no bridge protocol or historical artifact is retired.",
  "history_preservation": "Every existing numbered bridge artifact remains byte-identical and append-only.",
  "baseline": {
    "historical_reader": "the checker privately interprets committed terminal history instead of consuming the WI-5629 public lifecycle result",
    "atomic_candidate": "a fully reviewed staged VERIFIED candidate cannot clear its own exact protected same-transaction paths",
    "canonical_reproduction": "WI-5629 v026 records terminal finalization denial, and a fresh checker run denies the resolver source and resolver test for lack of live GO or terminal VERIFIED evidence",
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
  "essential_context_preservation": "Preserve WI-5633 and TEST-11678, WI-5629 v025-v026, WI-5474 v008, the VERIFIED commit-finalization owner directive, protected-path classification, live-GO precedence, independent review, schema-v3 implementation-start authority, and the two-file boundary.",
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
    "No dispatcher, runtime, configuration, or Git state is mutated by implementation or tests."
  ],
  "fail_closed_conditions": [
    "The WI-5629 v025-v026 evidence pair, claim-null state, public resolver contract, or any frozen dependency hash does not match.",
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
| WI-5629 dependency freeze | SHA-256 ledger over the four WI-5629 paths before and after implementation | All four hashes remain exact. |
| Transaction-local positive path | WI-5474-shaped and WI-5629-shaped fixtures with one staged VERIFIED candidate, exact manifest, independent author, valid report link, and finalized packet | Every packet-scoped protected path clears with transaction-local evidence. |
| Exact staged-set equality | Missing, extra, duplicate, glob, directory, path-escape, `.git`, explicit-path-only, and second-candidate fixtures | Every mismatch denies all transaction-local clearance. |
| Candidate validity | Wrong status/document/version/link, missing metadata, self-review, failed applicability/clause/evidence anchor, or missing finalization section | Candidate denies before protected paths clear. |
| Packet-bound scope | Missing, corrupt, hash-mismatched, wrong-bridge, non-finalized, or out-of-scope packet | Candidate denies with stable evidence error. |
| Historical fail-closed behavior | Pending NO-ACTION, unlinked correction, duplicate, gap, unreadable, wrong-role, wrong-document, non-adjacent, and multiply malformed fixtures | No terminal authorization. |
| Live-GO precedence | Existing live-GO positive fixtures | Existing classification and behavior remain unchanged. |
| Focused checker suite | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0. |
| Resolver integration | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0 with frozen WI-5629 hashes. |
| Static quality | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Formatting | `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Syntax | `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Scoped diff | `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` plus exact before/after hashes | Only the two authorized targets change. |
| End-to-end cycle break | After WI-5633 VERIFIED, file the governed Prime response to WI-5629 v026 and run fresh independent atomic terminal verification | The next WI-5629 verdict commits atomically with its reviewed path set and no DB mutation. |

## Acceptance Criteria

- Fresh independent GO approves this exact dependency model.
- WI-5629 remains latest v026, claim-free, and frozen at all four hashes
  throughout WI-5633 implementation and verification.
- The checker uses the public WI-5629 resolver and contains no second numbered
  history parser.
- One fully validated staged VERIFIED candidate clears only the exact equal
  staged set intersected with finalized packet target scope.
- WI-5474-shaped and WI-5629-shaped atomic fixtures pass.
- Every negative fixture fails closed and clears no protected path.
- Live-GO precedence, protected-path classification, output schema, and
  diagnostics remain compatible.
- TEST-11678, focused and integration tests, Ruff, formatting, compile,
  hash-freeze, and diff checks pass.
- Independent Loyal Opposition verifies and atomically finalizes WI-5633.
- A governed Prime response to WI-5629 v026 and fresh independent terminal
  finalizer then succeed without a waiver, history rewrite, weakened control,
  or `groundtruth.db` mutation.

## Risks / Rollback

The primary risk is converting transaction-local evidence into a manual verdict
bypass. Exact staged-set equality, canonical candidate validation, independent
review, latest-report linkage, and finalized packet-bound scope are conjunctive.
Any missing input denies the entire route.

The secondary risk is dependency drift while WI-5629 is uncommitted. The four
hashes are hard preconditions and postconditions. Any drift stops work and
requires governed revision.

Before terminal verification, rollback is a hash-pinned reverse of only the two
WI-5633 target hunks. After VERIFIED, rollback requires a new governed
correction. Bridge history remains append-only.

## Applicability Preflight

- packet_hash: `sha256:9e0d1bfa7a90729a6d48b1c4d934ea704e40823065a4aa067b414f0436470e68`
- bridge_document_name: `gtkb-wi5633-protected-commit-corrected-chain-evidence`
- content_source: `pending revision bytes`
- declared_target_paths: `["platform_tests/scripts/test_check_protected_commit_authorization.py", "scripts/check_protected_commit_authorization.py"]`
- preflight_passed: `true`
- warnings.missing_parent_dirs: `[]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

- Bridge id: `gtkb-wi5633-protected-commit-corrected-chain-evidence`
- Operative candidate: proposed version 005 bytes
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory Slice 2 gate

## Files Expected To Change

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

## Recommended Commit Type

`fix`
