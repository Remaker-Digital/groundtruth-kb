NEW
::init gtkb pb
::open build

# WI-5509 Strict Recovery: Complete Narrative Edit Autodiscovery Evidence

bridge_kind: prime_proposal
Document: gtkb-wi5509-narrative-edit-autodiscovery-test-completion-strict-recovery
Version: 001
Date: 2026-08-01 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5509
Related Work Items: WI-5574, WI-5593

target_paths: ["platform_tests/scripts/test_fab14_narrative_autodiscovery.py", "platform_tests/hooks/test_wi5509_edit_autodiscovery.py"]

implementation_scope: test_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
approval_evidence_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
selected_remediation: strict_recovery_and_unowned_test_completion

## Strict-Recovery Claim

The historical `gtkb-narrative-gate-edit-autodiscovery-fix` chain cannot carry
a lawful implementation start. Its immutable v003 declares
`Version: 003 (REVISED after NO-GO 002)`, while the strict lifecycle resolver
requires exact three-digit metadata. A fresh resolution on 2026-08-01 failed
closed with `WRONG_BRIDGE_VERSION_METADATA` at
`bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md`.

This document starts an independent parse-clean lifecycle without rewriting,
deleting, or treating the historical chain as current implementation authority.
Version 001 intentionally has no `Responds to` field. Historical v003
(`sha256:2A710C00B9C3B0A5417EC95F66D996A5EE6E34FCDE52F51EF5514C8C41E392F6`)
and the latest v006 NO-GO
(`sha256:460102DD2A5EC5A313291894AF4C68063B3C158CADECD40AF430F9DEED5BE9FE`)
remain immutable evidence. No historical GO, claim, packet, implementation
report, or finalization authority is imported into this recovery.

## Current-State Reconciliation

The intended Edit reconstruction behavior is already present in the clean
current tree: `_reconstruct_edit_content()` reads the current target, applies
the requested unique or `replace_all` substitution, and feeds the reconstructed
content into the existing packet autodiscovery path. The active hook and the
Codex projection have equal Git object identity even though their raw working
tree hashes differ because of line-ending normalization.

That current behavior is a pre-existing baseline, not an implementation credit
claimed by this proposal. The promised focused Edit tests are still absent.
This proposal completes only that presently unowned verification remainder and
does not modify either runtime copy.

The existing direct-test target was clean at re-observation, with raw SHA-256
`6E7740FB926951E89A2C22C4AACB047FEAA86FE81797D4D1671AC3AB2410661F`.
The new hook-level test target did not exist. These are evidence baselines, not
implementation-start preimages. After an independent GO, Prime Builder must
re-read authorization, claims, lifecycle, and both target preimages before
acquiring a fresh claim and minting the implementation-start packet.

## Requirement Sufficiency

Existing requirements sufficient

The governing approval-hook and bridge requirements already define the desired
fail-closed behavior, project authority, independent review, and
specification-derived verification. No new or amended requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`

## Owner Decisions / Input

- `DELIB-202666772` records the owner's specific decision to fix the hook
  itself first, including the bounded Edit reconstruction and narrative
  `--content-file` behavior, rather than use a one-time exception or defer.
- `DELIB-202667718` is the owner decision behind active list-free
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WHOLE-PROJECT-20260730` v2.
  WI-5509 is an active member of active
  `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`; project-inherited approval covers
  source and test additions without a WI allowlist.
- No new owner decision is required for this bounded proposal. The existing
  PAUTH still forbids dispatcher mutation, external-system mutation,
  credential lifecycle, push, history rewrite, deployment, release, and
  destructive cleanup.

## Ownership and Sequencing Boundaries

- `WI-5574` has its own strict-valid GO chain and exclusively owns
  `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py`,
  `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`,
  and `groundtruth-kb/tests/test_cli_approval_packet.py`. This proposal does
  not touch, duplicate, finalize, or claim those paths.
- `WI-5593` has its own GO chain and exclusively owns the
  `groundtruth-kb/src/groundtruth_kb/cli.py` help-text reconciliation. This
  proposal does not touch or claim that path.
- The existing behavioral bytes in both runtime copies are a read-only current
  baseline. If focused tests expose a defect, Prime Builder must stop and file
  a new REVISED proposal that names the necessary runtime targets; this GO
  request cannot authorize a behavioral correction.
- No implementation may begin if any declared target becomes foreign-dirty.
  The PB must release any claim and return for reconciliation rather than
  overwrite or absorb foreign work.

## Proposed Scope

1. Add direct unit coverage for `_reconstruct_edit_content()` in
   `platform_tests/scripts/test_fab14_narrative_autodiscovery.py`:
   unique replacement, `replace_all`, absent old text, ambiguous repeated old
   text without `replace_all`, missing or non-string operands, and unreadable
   or missing target. The failure cases must return `None` and preserve the
   existing fail-closed downstream path.
2. Add isolated hook-level Edit payload coverage in the new
   `platform_tests/hooks/test_wi5509_edit_autodiscovery.py` module. Prove that
   a governed packet matching the reconstructed post-edit content allows,
   while mismatched content and ambiguous edits both block. Fixtures must use
   a temporary project root and must not write packet records into the live
   repository.

## Out of Scope

- Any runtime, template, documentation, configuration, or CLI mutation.
- Any path owned by WI-5574 or WI-5593.
- Protected-artifact registry unification under WI-5441.
- Changes to packet schemas, artifact-approval policy, protected path
  classification, or the universal pre-commit enforcement floor.
- Any MemBase, formal GOV/ADR/DCL/SPEC, dispatcher, TAFE, deployment,
  credential, release, Git history, stage, commit, push, or cleanup operation.

This proposal performs no KB mutation and no MemBase write.
This proposal performs no approval-evidence work and creates, updates, or
deletes no live packet record. Temporary packet fixtures exist only inside
isolated test roots and are discarded by the test runner.

All durable outputs are in-root under `E:/GT-KB`; the governed proposal is
filed only under `E:/GT-KB/bridge/`, and the two implementation targets remain
under `E:/GT-KB/platform_tests/`.

## Specification-Derived Verification Plan

| Requirement | Required evidence |
| --- | --- |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `python -m pytest platform_tests/scripts/test_fab14_narrative_autodiscovery.py platform_tests/hooks/test_wi5509_edit_autodiscovery.py -q --tb=short` demonstrates deterministic reconstruction, allow, mismatch-block, and ambiguity-block behavior. |
| `GOV-ARTIFACT-APPROVAL-001` | The same focused suite proves only a packet whose path and full-content hash match the reconstructed post-edit state can authorize the Edit. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest platform_tests/hooks/test_narrative_artifact_approval.py -q --tb=short` preserves the existing cross-harness parity and hook regression assertions without modifying runtime surfaces. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Operation-time applicability preflight permits exactly the two declared test targets under the active v2 project PAUTH; the implementation-start packet is minted only after a fresh GO, claim, clean preimages, and exact target-path preflight. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The PB implementation report maps each acceptance criterion below to command output and an independently reproducible artifact/hash. |

Additional regression commands:

- `python -m pytest groundtruth-kb/tests/test_cli_approval_packet.py -q --tb=short`
- `python -m ruff check platform_tests/scripts/test_fab14_narrative_autodiscovery.py platform_tests/hooks/test_wi5509_edit_autodiscovery.py`
- `python -m ruff format --check platform_tests/scripts/test_fab14_narrative_autodiscovery.py platform_tests/hooks/test_wi5509_edit_autodiscovery.py`

## Acceptance Criteria

- Unit tests cover deterministic unique replacement and `replace_all` output.
- Missing, malformed, ambiguous, nonexistent, or unreadable Edit inputs return
  `None`; no test weakens the existing block behavior.
- A hook-level Edit with an owner-approved packet for the exact reconstructed
  post-edit content allows without an environment-variable packet reference.
- A mismatched packet and an ambiguous Edit both block with the existing
  approval-gate decision shape.
- Hook-level fixtures use a temporary project root and leave the live approval
  directory unchanged.
- Runtime and template files remain byte-for-byte outside the implementation
  diff; the existing parity regression stays green.
- Existing Write behavior, explicit packet-reference priority, protected path
  set, packet fields, and CLI packet behavior are unchanged.
- No WI-5574 or WI-5593 target is modified or represented as this WI's work.
- No hard-coded timeout, retry count, sleep, throttle, threshold, fan-out, or
  concurrency literal is introduced. Any later need for such policy must use
  the canonical centralized configuration surface rather than a local literal.
- Focused pytest and Ruff commands pass, and the implementation report records
  exact commands, results, changed-path hashes, and isolation evidence.

## Cross-Harness Disposition

- **Claude**: the live PreToolUse behavior is exercised read-only by direct and
  isolated hook-level Edit tests.
- **Codex**: its forward-compatible projection is not modified; existing parity
  coverage remains the regression boundary under
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- **Cursor, Antigravity, Goose, and other harnesses**: no runtime surface is
  changed. Their universal enforcement floor and governed packet contract are
  preserved.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "cross_cutting_harness_approval_surface",
  "provenance": "WI-5509; DELIB-202666772; historical gtkb-narrative-gate-edit-autodiscovery-fix v003-v006; current clean hook baseline",
  "canonical_authority": "GOV-ARTIFACT-APPROVAL-001 and DCL-ARTIFACT-APPROVAL-HOOK-001",
  "primary_route": "Claude PreToolUse Edit payload -> deterministic full-content reconstruction -> existing governed-packet resolution and validation",
  "before_behavior": "The current implementation reconstructs Edit content, but focused proof is absent.",
  "after_behavior": "The same fail-closed behavior is covered by direct and hook-level tests without adding a trust path or changing runtime bytes.",
  "self_descriptive_naming": "Existing names _reconstruct_edit_content and _autodiscover_packet remain unchanged and describe their responsibilities.",
  "obsolete_guidance_disposition": "No guidance mutation is in scope; preserve historical bridge evidence append-only.",
  "history_preservation": "Do not rewrite or delete the strict-invalid historical chain or attribute already-landed behavior to this recovery.",
  "baseline": "One clean existing test target at the recorded preimage hash, one absent new test target, and unchanged runtime behavior.",
  "expected_result": "Exact reconstructed Edit content can be independently shown to allow only with its matching approved packet; malformed, ambiguous, or mismatched cases block.",
  "rollback": "Revert only the eventual two-target test implementation; the prior behavioral baseline and historical bridge chain remain intact.",
  "hard_invariants": [
    "no new packet trust source",
    "no weakening of protected-path or packet validation",
    "explicit references remain higher priority than autodiscovery",
    "no runtime or template mutation",
    "no WI-5574 or WI-5593 path mutation",
    "no dispatcher or TAFE mutation"
  ],
  "fail_closed_conditions": [
    "missing or non-string Edit operands",
    "old text absent",
    "ambiguous repeated old text without replace_all",
    "missing or unreadable target",
    "packet path or content hash mismatch",
    "foreign-dirty declared target",
    "missing fresh GO, claim, or implementation-start packet"
  ],
  "essential_context_preservation": "Tests retain both allowed and denied behavior, use isolated project roots, and keep existing Write and explicit-reference regressions in the executed suite."
}
```

## Risk and Rollback

Risk is low but governance-sensitive: test construction could accidentally
exercise the live packet directory or mistake a failing test for authority to
edit runtime code. Temporary-root fixtures, explicit live-directory isolation,
and an exact two-target authorization close those risks. Rollback is a forward
revert of only the eventual two-target test implementation; it must not alter
the immutable bridge audit trail.

## Implementation-Start Boundary

This NEW file is a request for independent review, not implementation
authority. Prime Builder must wait for a strict-valid independent GO, then
re-read the active project PAUTH, lifecycle, target ownership, current claims,
and exact preimages; acquire a fresh GO-implementation claim; mint and validate
the named implementation-start packet; and only then modify the two declared
targets. No claim or packet is created by filing this proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
