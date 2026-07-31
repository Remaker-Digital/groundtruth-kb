REVISED
::init gtkb lo
::open build

# Revised Defect-Fix Proposal - Break the protected-commit terminalization dependency cycle

bridge_kind: prime_proposal
Document: gtkb-wi5633-protected-commit-corrected-chain-evidence
Version: 003
Responds to: bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-002.md
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

## Claim

Break the now-proven circular dependency between WI-5629 terminalization and
protected-commit authorization without weakening either control.

The protected-commit checker will use the frozen WI-5629 public lifecycle
resolver for committed terminal history. During one atomic finalization
transaction, it may additionally consume exactly one fully validated staged
VERIFIED candidate whose declared same-transaction manifest equals the complete
staged path set and whose protected paths are covered by the finalized
implementation-start packet for the reviewed implementation.

This revision changes only the execution dependency. WI-5629 need not already
be committed terminal because the transaction-local route is the prerequisite
that makes its terminal commit possible. The WI-5629 public resolver bytes,
tests, and reported evidence are frozen as read-only implementation
dependencies while WI-5633 is implemented and verified.

## Finding-By-Finding Response

### Response to v002 F1 - The prior terminal dependency is impossible

Accepted and revised.

Version 001 required WI-5629 to be terminal before WI-5633 implementation.
That ordering is now canonically proven circular:

1. WI-5629 v025 is a complete, claim-free post-implementation report.
2. Independent Loyal Opposition filed WI-5629 v026 `NO-GO`. It substantively
   verifies v025's implementation evidence and records that terminal
   finalization failed only because the protected-commit checker denied the
   same-transaction path set.
3. A fresh read-only checker reproduction in this Prime Builder session applied
   the current canonical checker to the four frozen WI-5629 paths. It returned
   `status: fail`; `scripts/bridge_lifecycle_resolver.py` and
   `platform_tests/scripts/test_bridge_lifecycle_resolver.py` each lacked a
   live GO packet or terminal VERIFIED bridge evidence. The two authorization
   paths cleared through existing terminal evidence.
4. WI-5629 v026 is therefore a canonical non-terminal blocker verdict, not a
   terminal closure. The repository `HEAD` remains
   `2c0b78f42a870da9c3b935d7680ccea8907c07f7`, and the Git index is empty.
5. Canonical claim status for both WI-5629 and WI-5633 is `null`.

Therefore WI-5629 cannot become terminal until the WI-5633 transaction-local
candidate route exists. This revision makes WI-5633 the explicit predecessor
of WI-5629 atomic finalization.

### Response to v002 F2 - Preserve the bounded repair shape

Accepted without expansion.

The implementation still owns exactly:

- `scripts/check_protected_commit_authorization.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`

It preserves exact staged-manifest equality, canonical candidate validation,
independent author context, latest-report linkage, finalized packet-bound
target scope, live-GO precedence, existing protected-path classification, and
fail-closed behavior. It does not edit WI-5629, WI-5636, WI-5637, bridge
writers, finalizers, hooks, dispatcher code, configuration, or runtime state.

## Frozen Resolver Readiness Gate

Implementation is prohibited until all of the following are true:

1. WI-5629 latest is the independent blocker verdict
   `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`, which responds
   to the claim-free post-implementation report v025 and substantively verifies
   the implementation while denying terminal closure on the WI-5633 defect.
2. Canonical claim status for WI-5629 and WI-5633 is `null`.
3. The following WI-5629 dependency hashes match exactly:

   - `scripts/bridge_lifecycle_resolver.py`:
     `9F9AAF48A0712F93DB778D0934E21CC344A00C433D690B07A9AC6981A768F1F1`
   - `scripts/implementation_authorization.py`:
     `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`
   - `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
     `247731D41A7D54641E38A57DD41A77AF9B739993D8686902EFCC63B0C3CE0C40`
   - `platform_tests/scripts/test_implementation_authorization.py`:
     `B60AB4529115CE9056D65F2397D6C5B2EFC4021832D3CFDA15612A3536C6F8F5`

4. Fresh independent WI-5633 review confirms the v025/v026 evidence pair, the
   public resolver contract, and all four frozen hashes before authoring GO.
5. WI-5633 has a fresh independent GO, an exact two-path implementation claim,
   and a finalized schema-v3 implementation-start packet.
6. No other worker owns either WI-5633 target.

WI-5629 terminal VERIFIED is explicitly not a WI-5633 prerequisite. Instead:

1. WI-5633 must be implemented, independently VERIFIED, and committed.
2. Its claim must be released.
3. Prime Builder must respond canonically to WI-5629 v026, revalidate the
   unchanged implementation against current state, and file the next governed
   report.
4. Fresh independent Loyal Opposition must then run the canonical atomic
   terminal finalizer.
5. Any drift in the four WI-5629 dependency hashes requires stopping and
   returning through governed review.

WI-5636 and WI-5637 remain separate downstream compatibility lanes and are not
absorbed by this revision.

## Defect / Exact Reproduction

Canonical WI-5629 v026 records this protected-commit failure:

```text
platform_tests/scripts/test_bridge_lifecycle_resolver.py:
protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence
```

This session reproduced the defect read-only with:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\check_protected_commit_authorization.py --paths scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py --json
status: fail
scripts/bridge_lifecycle_resolver.py: protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence
platform_tests/scripts/test_bridge_lifecycle_resolver.py: protected path lacks live GO authorization packet or terminal VERIFIED bridge evidence
```

This is the exact atomic commit-in-progress gap already described by WI-5633
v001. WI-5629 v026 proves it blocks WI-5629 itself, so terminal WI-5629
cannot remain the prerequisite for the repair.

## Requirement Sufficiency

Existing requirements remain sufficient. The revision creates no new authority
source and changes no bridge lifecycle status semantics.

Committed terminal evidence remains derived from the WI-5629 public lifecycle
resolver. Commit-in-progress evidence remains one exact staged VERIFIED
candidate, bounded by existing bridge-compliance, independent-review,
implementation-report linkage, implementation-start packet, protected-target,
and exact-manifest controls.

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
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-001.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-002.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-025.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-026.md`
- `bridge/gtkb-wi5474-exact-path-tracked-file-restore-008.md`
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`

## Owner Decisions / Input

- `DELIB-202666274` and
  `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` authorize
  governed Tree Stabilization source, test, bridge, metadata, and governance
  evidence work while preserving exact GO, claim, implementation-start,
  independent verification, and Git-operation gates.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` authorizes the Master
  Prime Builder to drive this prerequisite chain to terminality.
- No new owner decision is required. The atomic failure is implementation
  evidence for the already authorized WI-5633 defect, not a request to bypass
  the protected-commit control.

## Proposed Scope

1. Replace the checker's private committed-terminal history interpretation
   with consumption of the public WI-5629 lifecycle result.
2. Require committed terminal evidence to be strict VERIFIED with the valid
   implementation/report relationship and approved target paths exposed by
   that result.
3. Preserve exact-thread enumeration and every WI-5629 fail-closed outcome.
4. Keep live-GO packet evidence first in precedence and preserve all existing
   protected-path classifications.
5. Add one transaction-local candidate evaluator used only when the complete
   staged set contains exactly one new numbered bridge artifact whose exact
   first status is VERIFIED.
6. Parse only that candidate's `Commit Finalization Evidence` path manifest.
   This is a commit-manifest parser, not a lifecycle-history parser.
7. Require normalized manifest equality with the complete normalized staged
   set. Missing paths, extra paths, duplicates, globs, directory shorthand,
   path escapes, `.git` paths, or multiple VERIFIED candidates deny the route.
8. Reuse existing validators for bridge compliance, candidate evidence
   anchors, concrete author metadata, session-context review independence,
   exact Document/Version/Responds-to linkage to the latest Prime
   implementation report, and source freshness.
9. Require an internally consistent finalized schema-v3 implementation-start
   packet for the same bridge id. Its packet-bound targets must authorize every
   protected staged implementation path.
10. Clear only protected paths present in both the exact same-transaction
    manifest and packet target scope.
11. Preserve the existing terminal VERIFIED finalization-evidence gate, output
    schema, and human/JSON diagnostics. Add a distinct transaction-local
    evidence classification.
12. Add focused positive and negative TEST-11678 coverage, including the exact
    WI-5629-shaped finalization fixture now observed.

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
- A WI-5629 dependency hash differs from the frozen ledger above.
- Any implementation would require a target outside the two WI-5633 paths.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5633; TEST-11678; WI-5474 v008; WI-5629 v024-v025; DELIB-20260619-VERIFIED-COMMIT-FINALIZATION-OWNER-DIRECTIVE",
  "canonical_authority": "DCL-VERIFIED-BRIDGE-HISTORY-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "primary_route": "live GO packet or shared committed-terminal lifecycle result; during one atomic finalization, one fully validated staged VERIFIED manifest",
  "before_behavior": "The protected-commit checker cannot authorize the reviewed WI-5629 protected implementation paths in the same transaction as the first terminal VERIFIED artifact, so WI-5629 cannot satisfy the terminal prerequisite previously imposed on WI-5633.",
  "after_behavior": "Committed history uses the shared resolver, while one exact staged VERIFIED candidate can clear only its equal staged manifest intersected with finalized packet-authorized protected paths.",
  "self_descriptive_naming": "committed terminal evidence and transaction-local candidate evidence remain separate named classifications",
  "obsolete_guidance_disposition": "The impossible terminal-WI-5629 predecessor is replaced by a frozen claim-free v025 dependency ledger; no bridge status rule or historical artifact is retired.",
  "history_preservation": "Every existing numbered bridge artifact remains byte-identical and append-only.",
  "baseline": {
    "wi5629_head": "NEW v025 with claim null and complete implementation evidence",
    "atomic_failure": "the guarded v026 canonical helper rejected platform_tests/scripts/test_bridge_lifecycle_resolver.py for lack of live GO or already committed terminal evidence",
    "transaction_postcondition": "no v026, no commit, empty index, no index lock",
    "owned_targets": [
      "scripts/check_protected_commit_authorization.py",
      "platform_tests/scripts/test_check_protected_commit_authorization.py"
    ]
  },
  "expected_result": {
    "historical_reader": "terminal evidence consumes the WI-5629 public lifecycle result and contains no second numbered-history parser",
    "atomic_candidate": "one fully validated staged VERIFIED manifest clears only an equal staged set intersected with its finalized packet target scope",
    "negative_state": "pending, malformed, ambiguous, forged, self-reviewed, stale-linked, packet-invalid, or scope-mismatched candidates clear no protected path",
    "wi5629": "the unchanged guarded v026 finalizer completes atomically after WI-5633 is independently VERIFIED"
  },
  "essential_context_preservation": "Preserve WI-5633 and TEST-11678, WI-5474 v005-v008, WI-5629 v024-v025 and its four frozen dependency hashes, the VERIFIED commit-finalization owner directive, exact protected-path classification, live-GO precedence, independent review, schema-v3 implementation-start authority, and the two-file ownership boundary.",
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the hash-pinned WI-5633 hunks. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun TEST-11678, the complete protected-commit checker suite, resolver integration tests, and both WI-5474-shaped and WI-5629-shaped finalization fixtures."
  },
  "hard_invariants": [
    "The WI-5629 resolver is the only numbered lifecycle parser.",
    "Pending or structurally ambiguous history never authorizes a protected commit.",
    "A staged VERIFIED candidate authorizes only the exact equal staged manifest and finalized packet scope.",
    "Manual or malformed verdicts cannot bypass bridge compliance, evidence-anchor, author-independence, report-link, or packet checks.",
    "The four frozen WI-5629 dependency hashes do not change during WI-5633.",
    "No dispatcher or Git state is mutated by implementation or tests."
  ],
  "fail_closed_conditions": [
    "Any frozen WI-5629 dependency hash differs.",
    "Candidate count is not exactly one or its manifest differs from the staged set.",
    "Candidate validation, author independence, report linkage, packet integrity, or protected target scope fails.",
    "Any target outside the two declared WI-5633 files would need modification."
  ]
}
```

## Out Of Scope

- Editing any WI-5629, WI-5636, or WI-5637 target.
- Changing the atomic finalizer, bridge writer, or bridge-compliance hook.
- Rewriting or normalizing historical bridge files.
- Accepting decorated historical metadata through this transaction-local
  route.
- Dispatcher, TAFE, harness, role, eligibility, routing, lease, daemon,
  configuration, or runtime mutation.
- MemBase or `groundtruth.db` mutation.
- Git staging, commit, push, merge, history rewrite, deployment, release, or
  destructive cleanup during implementation. The later governed VERIFIED
  finalizer remains the only commit path.

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
  "obsolete_guidance_disposition": "The checker's private terminal-history interpretation and the impossible WI-5629-terminal-first dependency are removed; no bridge protocol or historical artifact is retired.",
  "history_preservation": "Every existing numbered bridge artifact remains byte-identical and append-only.",
  "baseline": {
    "historical_reader": "check_protected_commit_authorization privately interprets committed terminal history instead of consuming the WI-5629 public lifecycle result",
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
  "essential_context_preservation": "Preserve WI-5633 and TEST-11678, WI-5629 v025-v026, WI-5474 v008, the VERIFIED commit-finalization owner directive, exact protected-path classification, live-GO precedence, independent review, schema-v3 implementation-start authority, and the two-file ownership boundary.",
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the hash-pinned WI-5633 hunks. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun TEST-11678, the full protected-commit checker suite, resolver integration tests, hash-freeze checks, and the WI-5629-shaped finalization fixture."
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
| WI-5629 dependency freeze | SHA-256 ledger over the four WI-5629 paths before and after implementation | All four hashes remain exactly equal to the values in this proposal. |
| Transaction-local positive path | WI-5474-shaped and WI-5629-shaped fixtures with one staged VERIFIED candidate, exact manifest, independent author, valid report link, and finalized packet | Every packet-scoped protected path clears with transaction-local evidence. |
| Exact staged-set equality | Missing, extra, duplicate, glob, directory, path-escape, `.git`, explicit-path-only, and second-candidate fixtures | Every mismatch denies all transaction-local clearance. |
| Candidate validity | Wrong status/document/version/link, missing metadata, self-review, failed applicability/clause/evidence anchor, or missing finalization section | Candidate denies before protected paths clear. |
| Packet-bound scope | Missing, corrupt, hash-mismatched, wrong-bridge, non-finalized, or out-of-scope packet | Candidate denies with stable evidence error. |
| Historical fail-closed behavior | Pending NO-ACTION, unlinked correction, duplicate/gap/unreadable/wrong-role/wrong-document/non-adjacent/multiply malformed fixtures | No terminal authorization. |
| Live-GO precedence | Existing live-GO positive fixtures | Existing classification and behavior remain unchanged. |
| Focused checker suite | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0. |
| Resolver integration | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | Exit 0 with frozen WI-5629 hashes. |
| Static quality | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Formatting | `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Syntax | `groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` | Exit 0. |
| Scoped diff | `git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py` plus exact before/after path hashes | Only the two authorized targets change. |
| End-to-end cycle break | After WI-5633 VERIFIED, file the governed Prime response to WI-5629 v026 and run fresh independent atomic terminal verification | The next WI-5629 verdict commits atomically with its complete reviewed path set and no DB mutation. |

## Acceptance Criteria

- A fresh independent GO approves this revised dependency model.
- WI-5629 remains latest v026, claim-free, and frozen at the four exact hashes
  throughout WI-5633 implementation and verification.
- The checker uses the public WI-5629 resolver for committed terminal history
  and contains no second numbered-history parser.
- One fully validated staged VERIFIED candidate clears only the exact equal
  staged set intersected with its finalized packet target scope.
- The WI-5474-shaped and exact WI-5629-shaped atomic fixtures pass.
- Every negative fixture fails closed and clears no protected path.
- Live-GO precedence, protected-path classification, output schema, and
  diagnostics remain compatible.
- TEST-11678, the focused suite, resolver integration suite, Ruff, formatting,
  compile, hash-freeze, and diff checks pass.
- Independent Loyal Opposition verifies and atomically finalizes WI-5633.
- A governed Prime response to WI-5629 v026 and fresh independent terminal
  finalizer then succeed without a waiver, history rewrite, protected-control
  weakening, or `groundtruth.db` mutation.

## Risks / Rollback

The primary risk is converting transaction-local evidence into a manual verdict
bypass. Exact staged-set equality, canonical candidate validation, independent
review, latest-report linkage, and finalized packet-bound scope are therefore
conjunctive. Any missing input denies the entire route.

The secondary risk is accidental dependency drift while WI-5629 is not yet
committed. The four exact hashes are hard preconditions and postconditions.
Any drift stops implementation or finalization and requires a governed
revision.

Before terminal verification, rollback is a hash-pinned reverse of only the
two WI-5633 target hunks. After VERIFIED, rollback requires a new governed
correction. Bridge history remains append-only.

## Applicability Preflight

- packet_hash: `sha256:01b8eb23969c5f4823cfec9cb2d87e27854af4911ecfec09719e45e1d3a07d4f`
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
- Operative candidate: proposed version 003 bytes
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
