REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe34a-283e-77c1-b7b5-3e94242873e9
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; build envelope; owner-driven manual bridge routing
author_metadata_source: transcript init keyword and Codex runtime system metadata

# Revised Implementation Proposal - WI-5950 fresh executable finalization cycle after index reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi5950-strict-terminal-recovery
Version: 007
Date: 2026-08-10 UTC
Responds to: bridge/gtkb-wi5950-strict-terminal-recovery-006.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
Latest Bridge Status: NO-GO
Reviewed Proposal Version: 7

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
KB mutation declaration: This proposal performs no MemBase mutation or write.

## Summary

Request one fresh, independently reviewed implementation cycle for the already
implemented WI-5950 strict-terminal recovery helper. Loyal Opposition `-006`
accepted the two-target implementation substance and found one finalization
precondition: the source hunk was already staged in the real Git index. Prime
Builder has now performed the exact prescribed index-only reconciliation. The
source hunk remains byte-identical in the worktree, the real index is back at
HEAD, the focused test remains untracked, and the focused verification remains
green.

A second mechanical constraint means another report under the report-NO-GO
resumption packet would still be unexecutable. The supported resumption path
finalizes a packet containing a `draft` claim, while the protected-commit gate
requires the embedded claim to be `go_implementation`. This REVISED proposal
therefore requests a new GO so the ordinary claim and implementation-start
packet are bound to a genuinely executable fresh cycle.

## Claim

The approved WI-5950 design remains correct and the current two candidate files
remain within the exact original scope. No source or test byte is changed by
filing this proposal. After an independent GO, Prime Builder will acquire a
fresh `go_implementation` claim, mint and finalize a schema-v3 packet bound to
this proposal and that GO, validate both exact targets, re-adopt or make only
strictly bounded corrections to the current candidate bytes, execute the full
specified verification set, and file a fresh post-GO implementation report for
independent atomic VERIFIED finalization.

## Requirement Sufficiency

Existing requirements are sufficient. The original approved proposal, active
project authorization, owner decisions, v005 implementation report, and v006
verification verdict fully determine the behavior, target cohort, and
verification boundary. This revision introduces no new requirement and grants
no waiver or bypass. It only replaces an unexecutable report-resumption route
with the ordinary fresh-GO lifecycle required by the protected-commit gate.

## Findings Addressed

### F1 - Real-index staged overlap is reconciled

The exact remediation directed by `-006` has been performed under a live
true-session claim and schema-v3 packet:

```text
git restore --staged -- groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py
```

Post-remediation evidence:

- `git status --short` reports ` M` for the source, not `M `.
- `git diff --cached --numstat` for the two targets is empty.
- source index blob equals HEAD blob:
  `03cb0a5d51e885fa2ed5906a37ecf5d61805f7c8`.
- source worktree delta remains exactly `+218/-0`.
- source full-file SHA-256 remains
  `62ABC576187CCC1AB5DD31B0B85FD0CFAFD25EBBF9B770021DBF769944F995DD`
  at 221,972 bytes.
- focused test remains untracked with SHA-256
  `7C69B7C16A414794A693EE0E0129F8A6AABA3BA0360345A3280ECE2D7D50CCDC`
  at 9,148 bytes.

The operation changed only index metadata. It did not alter source, test, HEAD,
refs, worktree bytes, MemBase, project state, PAUTH state, dispatcher state, or
TAFE state.

### F2 - Report-NO-GO draft claim cannot authorize atomic finalization

The current diagnostic packet is schema v3, packet
`sha256:e368c0a8cb10f2db8828483ee836310843aaaf2c1cb1a379d3a672fb0d06f444`,
with pre-start hash
`sha256:aa9731bd88ec453742bcb7c89878c54578150b83d9133eb5219dbfcfbc26fc05`.
It correctly records `resumption_authority.state = resumable_report_no_go`, but
its embedded work-intent claim is `draft`.

`scripts/implementation_authorization.py` permits that draft claim solely for
fresh report-level NO-GO resumption. The protected finalization authority in
`scripts/check_protected_commit_authorization.py` and the governed Git
lifecycle service fail closed unless both the live and embedded claims are
`go_implementation`.

The packet also fails the protected checker's pre-start reconstruction. Its
declared pre-start hash is
`sha256:aa9731bd88ec453742bcb7c89878c54578150b83d9133eb5219dbfcfbc26fc05`,
but reconstruction with the finalized top-level `resumption_authority` yields
`sha256:8c643c1c7067a4815d30db5459e055ee2ee2d1a0269fad1be6d07d199fdba0ee`.
Removing that post-hash resumption augmentation reproduces the declared hash,
confirming a deterministic report-resumption mismatch rather than target-byte
drift. A standard fresh-GO packet has no report-resumption augmentation and is
the supported route around both failures.

The diagnostic packet is therefore evidence of the problem, not finalization
authority. It must not be reused after this proposal is filed.

## Exact Current Candidate Evidence

The implementation behavior accepted by `-006` remains unchanged:

- `recover_missing_bridge_publication_capability` is owner-decision-gated,
  exact-targeted, byte-bound before and inside the registry lock, strict-
  lifecycle checked, idempotent, single-use, and records recovery provenance.
- It back-fills one consumed publication-capability receipt for an existing
  pre-fix bridge file without creating or modifying the bridge file.
- It does not perform the later WI-5953 recovery-required in-place transition;
  that remains a separate carrier.

Fresh post-remediation checks already completed:

| Check | Result |
| --- | --- |
| `python -m pytest platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py -q --tb=short` | 6 passed, 1 warning |
| `python -m py_compile` on the exact source and test | pass |
| `python -m ruff check` on the exact source and test | pass |
| `python -m ruff format --check` on the exact source and test | 2 files already formatted |
| `git diff --check` on the source worktree delta | pass |

These results are readiness evidence only. The post-GO implementation report
must rerun and record the actual final evidence under the new
`go_implementation` claim and packet.

## Proposed Scope And Sequence

1. Loyal Opposition independently reviews this exact proposal and returns GO
   only if the two-target fresh cycle is executable and requirement-complete.
2. Prime Builder acquires an ordinary claim after GO and requires readback
   `claim_kind = go_implementation` for the true session
   `019fe34a-283e-77c1-b7b5-3e94242873e9`.
3. Prime Builder runs `implementation_authorization.py begin` for this bridge
   and requires a current schema-v3 packet bound to this v007 proposal, the new
   GO, the active PAUTH, and exactly the two declared targets.
4. Prime Builder revalidates exact candidate hashes, index cleanliness, target
   authorization, and foreign-work isolation. If state drift makes attribution
   ambiguous, stop without mutation. Otherwise adopt the existing bytes or make
   only bounded corrections within the exact two targets.
5. Rerun the focused recovery suite, the adjacent registry-control-plane
   regression suite, Python compilation, Ruff check and format check, exact diff
   review, bridge applicability, mandatory clause, and pre-verdict gates.
6. File a fresh post-GO implementation report with exact packet, claim,
   postimage, test, and index evidence.
7. Independent Loyal Opposition performs the governed atomic VERIFIED
   finalization, staging only the numbered bridge chain and the exact two
   implementation targets. No unrelated worktree content may be included.

No live recovery operation against an existing bridge receipt is in scope for
this WI. No dispatcher/TAFE, configuration, credential, deployment, release,
push, history rewrite, project graph, PAUTH, or unrelated worktree mutation is
authorized.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5950; bridge/gtkb-wi5950-strict-terminal-recovery-006.md; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal/finalization services",
  "primary_route": "fresh REVISED proposal -> independent GO -> go_implementation claim -> schema-v3 packet -> report -> atomic VERIFIED",
  "before_behavior": "The report-level NO-GO resumption packet embeds a draft claim and a non-reconstructable pre-start hash; the protected finalizer rejects it. The real-index staged overlap identified by v006 has already been removed without changing worktree bytes.",
  "after_behavior": "A new independent GO binds a standard go_implementation claim and fresh packet to the same exact two-target implementation, enabling revalidation and ordinary atomic finalization without a waiver or bypass.",
  "self_descriptive_naming": "The document, work item, target paths, claim-kind correction, and finalization sequence name the proposed effect directly.",
  "obsolete_guidance_disposition": "The v006 substantive findings remain valid history; only its implied direct report-resumption route is superseded by this fresh executable cycle.",
  "history_preservation": "All numbered bridge versions remain append-only. Before current/named authorization pointers are replaced, prior exact named-packet bytes are preserved in append-only packet history; no prior bridge audit file is rewritten or deleted.",
  "baseline": {
    "work_item": "WI-5950",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE",
    "project_authorization": "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py",
      "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"
    ],
    "candidate_source_sha256": "62ABC576187CCC1AB5DD31B0B85FD0CFAFD25EBBF9B770021DBF769944F995DD",
    "candidate_test_sha256": "7C69B7C16A414794A693EE0E0129F8A6AABA3BA0360345A3280ECE2D7D50CCDC"
  },
  "expected_result": {
    "summary": "Reauthorize the unchanged two-target WI-5950 implementation through a fresh executable GO/claim/packet cycle.",
    "scope": [
      "Preserve the index-only remediation and require index-equals-HEAD readback before finalization.",
      "Require live and embedded go_implementation claims from the same true Prime session.",
      "Require a fresh schema-v3 packet bound to this proposal, its new independent GO, the active PAUTH, and exactly two targets.",
      "Revalidate candidate bytes and rerun focused, adjacent, compile, Ruff, applicability, clause, and pre-verdict checks.",
      "Atomically finalize only the new bridge chain and exact two implementation targets; preserve all unrelated work."
    ],
    "acceptance_criteria": [
      "Fresh independent GO is current and executable.",
      "Claim and embedded packet claim are both go_implementation.",
      "Exact source/test scope and PAUTH validation pass at start and finalization.",
      "Specified verification passes on final exact bytes.",
      "Independent VERIFIED and its local commit are atomic and contain no unrelated path."
    ]
  },
  "rollback": {
    "instructions": "Stop without mutation on drift or ambiguity. Any later code rollback reverts only the two approved targets under separate authority; bridge history remains append-only.",
    "verification": "Re-run the same spec-derived tests, exact hashes, index checks, and bridge preflights after any authorized rollback."
  },
  "hard_invariants": [
    "No implementation authority exists until independent GO and a matching go_implementation claim/packet are current.",
    "Only the two declared in-root paths are attributable to this proposal.",
    "No dispatcher, TAFE, credential, deployment, release, push, history-rewrite, project-graph, PAUTH, or unrelated work mutation is authorized.",
    "No terminal VERIFIED may survive without the matching atomic local commit."
  ],
  "fail_closed_conditions": [
    "The proposal/GO pair, claim, packet, session, PAUTH, target set, or target hashes are missing, stale, conflicting, or mismatched.",
    "Either implementation target is already staged or foreign ownership/attribution is ambiguous.",
    "Any mandatory test, applicability, clause, executability, protected-commit, or publication-capability check fails.",
    "Atomic finalization would include an unrelated path or require a bypass."
  ],
  "essential_context_preservation": "The proposal retains the original behavior contract, owner decisions, PAUTH, exact target cohort, index remediation, claim/hash diagnosis, verification matrix, risks, rollback, and append-only bridge history."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5950-strict-terminal-recovery-001.md` - original approved
  implementation proposal and exact design boundary.
- `bridge/gtkb-wi5950-strict-terminal-recovery-002.md` - historical GO for the
  original cycle; it is not reused as authority for this fresh cycle.
- `bridge/gtkb-wi5950-strict-terminal-recovery-005.md` - implementation report
  whose source/test substance remains current.
- `bridge/gtkb-wi5950-strict-terminal-recovery-006.md` - independent NO-GO that
  accepted the implementation substance and prescribed real-index
  reconciliation.
- `DELIB-20260810-BRIDGE-VERSIONED-FILES-REGISTRY-REFRESH-AUTHORIZATION` - owner
  authority for governed bridge-versioned-files registry recovery and terminal
  finalization reconciliation.
- `DELIB-20260808-WI6073-PUBLICATION-CAPABILITY-RECOVERY-AUTHORIZATION` - owner
  authority for the publication-capability recovery control plane.
- `DELIB-202667714` - owner decision underlying the active project-wide PAUTH
  and governed atomic local-commit route.

## Owner Decisions / Input

No new owner decision is required. Existing owner decisions authorize the
bounded WI-5950 recovery capability and its governed finalization. This proposal
does not expand behavior, target paths, project scope, PAUTH, or commit scope;
it restores the ordinary independent GO and `go_implementation` lifecycle that
the mandatory finalizer requires.

## Specification-Derived Verification Plan

| Specification | Required executable evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Strict numbered lifecycle; independent GO; true-session claim; current schema-v3 packet; independent atomic VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflights must harvest every governing specification with no blocking omission. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Read back exact PAUTH, project, WI, and two target paths from the proposal and packet. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Require live and embedded `go_implementation` claims from the same true Prime session before implementation/finalization. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Validate both target classes at start and finalization; forbidden operations remain denied. |
| `GOV-WORK-TREE-HYGIENE-001` | Prove the real index starts clean for both targets, source/test attribution is exact, and unrelated staged/unstaged/untracked work is preserved. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Rerun focused and adjacent tests plus compile/Ruff gates; map results and exact hashes in report and verdict. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Applicability, mandatory clause, and pre-verdict executability gates all exit 0 on exact proposal/report/verdict bytes. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Re-read bridge, claim, PAUTH, index, target bytes, and packet immediately before every protected action. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All effects remain inside `E:\GT-KB`; no adopter application path is touched. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Valid receipt behavior, unrelated registry state, dispatcher/TAFE state, and foreign work remain unchanged. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve v001-v006 append-only; treat the current draft-claim packet only as historical diagnostic evidence after v007. |

## Acceptance Criteria

- Independent GO approves this exact v007 proposal and its exact two-target
  scope.
- Fresh claim and finalized packet both read back `go_implementation`, the true
  Prime session, the new proposal/GO pair, the active PAUTH, and exactly the two
  target paths.
- Source/test hashes and attribution are revalidated after GO; any drift fails
  closed.
- The recovery helper continues to satisfy the behavior accepted by v006.
- Focused and adjacent tests, compilation, Ruff, applicability, clause, and
  pre-verdict gates pass on exact final bytes.
- Atomic VERIFIED commits only the new bridge chain and exact two targets while
  preserving all unrelated work and leaving no false terminal artifact.

## Risk And Rollback

Risk is bounded but material because the helper can mint and consume recovery
receipts when supplied exact owner authority and content. Strict lifecycle,
byte binding, owner-decision input, single-use refusal, and exact target scope
mitigate misuse. The fresh-cycle requirement prevents a draft claim from being
misrepresented as commit authority.

If post-GO validation finds drift or ambiguity, stop without staging or
mutation. Any later implementation rollback reverts only the exact two approved
targets under separate governed authority. Numbered bridge files and audit
records remain append-only.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
- `platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py`

The candidate bytes already exist in the worktree, but they remain expected
implementation targets because the fresh cycle must explicitly adopt,
revalidate, stage, and atomically finalize them.

## Recommended Commit Type

Recommended commit type: `feat:` - the bounded change adds the owner-gated
publication-capability recovery service and its focused tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
