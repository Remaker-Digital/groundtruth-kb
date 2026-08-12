REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019feedf-9ae7-7f13-8819-5d6295655342
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder sub-agent; publication-completion lane; transcript-defined ::init gtkb pb
author_metadata_source: Codex runtime session metadata and delegated Prime Builder lane

bridge_kind: prime_proposal
Document: gtkb-wi5950-strict-terminal-recovery
Version: 009
Date: 2026-08-11 UTC
Responds to: bridge/gtkb-wi5950-strict-terminal-recovery-008.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project Authorization Version: 5
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5950
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "platform_tests/groundtruth_kb/project/test_publication_capability_recovery.py"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-5950 REVISED — fresh executable recovery cycle after W0P terminalization

## Revision Claim

This revision accepts every finding in Loyal Opposition NO-GO `-008` and
re-files the exact two-target WI-5950 recovery carrier after its declared
W0P-first sequencing condition became true. W0P/WI-5977 is independently
VERIFIED at `bridge/gtkb-w0p-finalization-machinery-repair-008.md` and committed
at `13c9f0f5032e1bcffb3cae60023e2ba20197e86d`. That commit contains the W0P
bridge chain, approved hunk patch, `registry_control_plane.py`, and focused
preimage-scoping test. The W0P claim now reads `null`.

Against the new HEAD baseline, the shared source has exactly the WI-5950
candidate delta declared before the temporary W0P overlap: `+218/-0`, entirely
the owner-gated `recover_missing_bridge_publication_capability` helper. The
focused WI-5950 test remains untracked and unchanged. Neither target is staged,
and no other live claim covers either target. The fresh GO requested here can
therefore bind a standard `go_implementation` claim and schema-v3 packet without
absorbing W0P or any unrelated worktree byte.

## Requirement Sufficiency

Existing requirements are sufficient. The original approved WI-5950 proposal,
active PAUTH v5, owner authorization, reports `-005`/`-007`, and NO-GO findings
`-006`/`-008` completely define the behavior, two-target cohort, and verification
boundary. This revision changes no product requirement and grants no waiver.

## Findings Addressed

### F1 (P0) — commingled W0P bytes made v007's exact-scope claim false

Resolved by sequencing, not by rewriting foreign work. W0P terminalized and its
exact source/test/bridge cohort entered commit `13c9f0f5`. Fresh readback now
shows:

- HEAD source blob: `d0ef9f186b36ba0bbef38e6600c5c602f104ab50`;
- real-index source blob: the same `d0ef9f186...`;
- source worktree delta versus HEAD: exactly `218 insertions, 0 deletions`;
- source postimage: 226,032 bytes, SHA-256
  `3f7a60311de62e312f3d627635788bc109b99f233664461f3c2c86953512105e`;
- focused test postimage: 9,148 bytes, SHA-256
  `7c69b7c16a414794a693ee0e0129f8a6aaba3ba0360345a3280ece2d7d50ccdc`;
- staged delta for both targets: empty.

The W0P `validated_transition_digest` / thread-scoped compensation change is now
part of HEAD, not part of the WI-5950 worktree delta. No W0P byte is attributed
to this proposal.

### F2 (P1) — live W0P `go_implementation` claim overlapped the source

Resolved. `python scripts/bridge_claim_cli.py status
gtkb-w0p-finalization-machinery-repair` returns `null`. W0P is terminal and
committed. The WI-5950 revision claim is held by this Prime Builder context only
for drafting; after a new independent GO, the ordinary begin path must replace
it with a fresh `go_implementation` claim and packet before target adoption.

### F3 (P2) — old report-resumption packet is diagnostic only

Preserved. The prior packet with `claim_kind: draft` is not reused. A new GO is
required so `implementation_authorization.py begin` can derive fresh authority
from this revision, the new verdict, the current PAUTH, and exactly two targets.

## Exact Current Candidate Evidence

The WI-5950 candidate adds `recover_missing_bridge_publication_capability`, an
owner-authorization-gated exact-byte recovery path for genuinely missing
publication receipts on existing pre-capability bridge files. It does not edit
bridge files, repair `recovery_required` rows, enable dispatch, or mutate the
legacy TAFE dispatcher. The later in-place poisoned-receipt operation remains
owned by the distinct WI-5953 carrier.

Current source delta is one additive hunk beginning at
`recover_missing_bridge_publication_capability`; `git diff --check` passes.
The focused module exercises authorization, exact-byte/lifecycle binding,
existing-receipt refusal, missing-target refusal, success, and idempotence/
single-use behavior.

## Scope And Implementation Sequence

1. Obtain an independent GO on this exact revision.
2. Acquire a fresh `go_implementation` claim and create a current schema-v3
   implementation-start packet for exactly the two declared targets.
3. Re-read HEAD, index, worktree hashes, target ownership, PAUTH, and foreign
   claims. Stop on drift; otherwise adopt the unchanged candidate bytes.
4. Run the focused module, adjacent registry-control-plane recovery regression
   coverage, Python compilation, Ruff lint, Ruff format check, exact diff review,
   applicability preflight, clause preflight, and pre-verdict executability.
5. File a fresh post-implementation report containing exact observed evidence.
6. Leave VERIFIED publication and atomic commit finalization to an independent
   Loyal Opposition context; its include set must be limited to the WI-5950
   numbered chain and exact two implementation targets.

No database operation, live bridge-receipt recovery, MemBase mutation,
dispatcher/TAFE mutation, configuration change, destructive cleanup, staging,
commit, push, history rewrite, credential action, deployment, or release is in
scope for Prime Builder implementation.

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

- `bridge/gtkb-wi5950-strict-terminal-recovery-001.md` — original approved behavior and target boundary.
- `bridge/gtkb-wi5950-strict-terminal-recovery-005.md` — accepted implementation evidence.
- `bridge/gtkb-wi5950-strict-terminal-recovery-006.md` — real-index precondition and report-resumption diagnosis.
- `bridge/gtkb-wi5950-strict-terminal-recovery-008.md` — W0P overlap/claim NO-GO addressed here.
- `bridge/gtkb-w0p-finalization-machinery-repair-008.md` — independent W0P VERIFIED terminal evidence.
- `DELIB-20260808-WI6073-PUBLICATION-CAPABILITY-RECOVERY-AUTHORIZATION` — publication-capability recovery authority.
- `DELIB-20260810-BRIDGE-VERSIONED-FILES-REGISTRY-REFRESH-AUTHORIZATION` — registry refresh/finalization authority.
- `DELIB-202667714` — owner decision underlying the current project-wide PAUTH.

## Owner Decisions / Input

No new owner decision is required. Existing decisions authorize the bounded
WI-5950 recovery capability and ordinary governed finalization. The owner also
requires the legacy TAFE dispatcher to remain disabled; this revision contains
no dispatcher or TAFE mutation.

## Specification-Derived Verification Plan

| Requirement | Executable evidence |
| --- | --- |
| Exact recovery semantics | Focused `test_publication_capability_recovery.py` module proves owner gate, exact bytes/lifecycle, missing/existing cases, success and single-use behavior. |
| Registry non-regression | Existing recovery/compensation tests in `groundtruth-kb/tests/test_registry_control_plane.py` and adjacent publication-capability modules. |
| Exact attribution and hygiene | HEAD/index blob equality, `+218/-0` source diff, untracked focused test hash, empty staged set, no foreign claim, `git diff --check`. |
| Project/bridge authority | Fresh independent GO, `go_implementation` claim, schema-v3 packet, PAUTH v5, applicability/clause/executability gates. |
| Python quality | `py_compile`, Ruff check, and Ruff format check on both exact Python targets. |
| Atomic terminal state | Independent VERIFIED helper finalizes exact chain plus two targets in one local commit. |
| Non-impairment | No database recovery, dispatcher/TAFE, config, external, credential, deployment, or release mutation; existing W0P tests remain green. |

## Acceptance Criteria

1. Independent GO approves this exact post-W0P two-target scope.
2. Fresh claim and packet both read `go_implementation` for the same Prime
   session and exactly these targets.
3. Candidate hashes, index cleanliness, and `+218/-0` attribution remain true at
   implementation start and report filing.
4. Focused, adjacent, compile, Ruff, diff, applicability, clause, and
   executability checks pass on exact final bytes.
5. Independent VERIFIED creates the atomic local commit without any unrelated
   worktree path.
6. The disabled legacy TAFE dispatcher remains disabled and untouched.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5950; gtkb-wi5950-strict-terminal-recovery-008; W0P VERIFIED 008; commit 13c9f0f5",
  "canonical_authority": "the current numbered bridge chain, active PAUTH v5, exact source/test bytes, and independent terminal finalization",
  "primary_route": "REVISED -> independent GO -> go_implementation claim/packet -> exact report -> atomic VERIFIED",
  "before_behavior": "WI-5950 could not be re-GOed while uncommitted W0P bytes and a live W0P claim overlapped registry_control_plane.py",
  "after_behavior": "W0P is committed and unclaimed; the remaining +218/-0 source delta and focused test are uniquely attributable to WI-5950",
  "self_descriptive_naming": "recover_missing_bridge_publication_capability names the missing-receipt-only operation and distinguishes it from WI-5953 poisoned-receipt recovery",
  "obsolete_guidance_disposition": "the v008 W0P-overlap warning is satisfied by terminal commit evidence but remains immutable history; the old draft-claim packet remains diagnostic-only",
  "history_preservation": "all bridge versions and W0P commit history remain append-only",
  "baseline": {
    "head_commit": "de467cbc9 with W0P predecessor commit 13c9f0f5",
    "source_delta": "+218/-0",
    "source_sha256": "3f7a60311de62e312f3d627635788bc109b99f233664461f3c2c86953512105e",
    "test_sha256": "7c69b7c16a414794a693ee0e0129f8a6aaba3ba0360345a3280ece2d7d50ccdc",
    "w0p_claim": "no active W0P work-intent claim; canonical status command returned JSON null"
  },
  "expected_result": {
    "missing_receipt_helper_present": true,
    "focused_and_adjacent_tests_green": true,
    "exact_two_target_atomic_finalization": true,
    "dispatcher_or_tafe_mutation": false
  },
  "rollback": {
    "instructions": "stop without mutation on drift; any later rollback removes only the WI-5950 additive hunk and focused test under separate authority",
    "verification": "repeat hashes, exact diff, focused and adjacent tests, claims, packet, and bridge lifecycle checks"
  },
  "hard_invariants": [
    "only the exact two WI-5950 targets are adopted",
    "the old draft-claim packet is never reused",
    "no live recovery or database mutation occurs in this implementation slice",
    "the legacy TAFE dispatcher remains disabled and untouched",
    "no VERIFIED survives without its same-transaction local commit"
  ],
  "fail_closed_conditions": [
    "any target hash, index, claim, PAUTH, proposal/GO, packet, or target-set drift",
    "any foreign work ownership or attribution ambiguity",
    "any mandatory test or gate failure",
    "any finalization set containing unrelated paths"
  ],
  "essential_context_preservation": "WI-5950 repairs genuinely missing pre-capability receipts only; WI-5953 separately repairs recovery_required receipts; W0P prevention is already terminal and committed"
}
```

## Pre-Filing Preflight Subsection

Candidate preflights were executed on these exact completed draft bytes:

- `python scripts/bridge_applicability_preflight.py --content-file
  .gtkb-state/bridge-revisions/drafts/gtkb-wi5950-strict-terminal-recovery-009.md
  --json` — exit 0; `preflight_passed: true`; `missing_required_specs: []`;
  `missing_advisory_specs: []`; PAUTH operation-time evaluation `allowed` for
  both exact targets.
- `python scripts/adr_dcl_clause_preflight.py --content-file
  .gtkb-state/bridge-revisions/drafts/gtkb-wi5950-strict-terminal-recovery-009.md`
  — exit 0; 3 `must_apply`, 2 `may_apply`, zero evidence gaps and zero blocking
  gaps.

The governed filing helper must rerun both checks and fail closed on any drift.

## Risk And Rollback

The recovery helper can create a consumed receipt only when supplied exact
owner authority and content, so misuse risk is material but bounded by strict
file/lifecycle binding and existing-receipt refusal. Any drift before report
filing stops without target mutation. A later source rollback is limited to the
exact WI-5950 additive hunk and focused test under separate authority; numbered
bridge history and W0P bytes are never deleted or rewritten.

## Recommended Commit Type

`feat:` — this adds the bounded owner-gated missing-publication-receipt recovery
capability.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
