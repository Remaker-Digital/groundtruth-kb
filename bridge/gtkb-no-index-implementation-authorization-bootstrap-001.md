NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-no-index-implementation-authorization-bootstrap-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# No-Index Implementation Authorization Bootstrap Proposal

bridge_kind: prime_proposal
Document: gtkb-no-index-implementation-authorization-bootstrap
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4578

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_bridge_claim_cli.py", "bridge/gtkb-no-index-implementation-authorization-bootstrap-*.md"]

implementation_scope: bootstrap_deadlock_repair, implementation_authorization, work_intent_claims, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the implementation-start authorization deadlock exposed by the
`bridge/INDEX.md` retirement cleanup.

The cleanup thread `gtkb-bridge-index-retirement-cleanout` now has a Loyal
Opposition GO at `bridge/gtkb-bridge-index-retirement-cleanout-006.md`, but the
normal implementation-start path cannot issue a packet because
`scripts/implementation_authorization.py` resolves bridge thread state only
through `bridge/INDEX.md`.

This is a bootstrap defect in the enforcement substrate. The gate correctly
refuses protected mutations without a current packet, but the packet issuer
incorrectly requires the retired file that the approved work is meant to remove.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected implementation
  mutations require a live bridge GO authorization packet plus matching
  work-intent claim.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge repair authority and bridge protocol
  enforcement remain mandatory, but `bridge/INDEX.md` is no longer live
  authority per owner directive.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  project/work-item linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites governing specs before review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove
  the no-index packet path works.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`,
  `DCL-DISPATCH-ENVELOPE-RULES-001`, and `SPEC-TAFE-R4` - dispatcher/TAFE
  bridge state replaces index-derived routing and authorization assumptions.

## Prior Deliberations

- `DELIB-20263438` - role assignment, dispatchability, and rule-based dispatch
  are independent.
- Owner directives on 2026-06-15:
  - "`bridge/INDEX.md` must not exist."
  - "We do not want backward compatibility."
  - "Remember: every mutating task requires the bridge protocol."
- `bridge/gtkb-bridge-index-retirement-cleanout-005.md` and
  `bridge/gtkb-bridge-index-retirement-cleanout-006.md` - latest cleanup
  proposal and Antigravity GO.

## Owner Decisions / Input

No new product or architecture decision is needed for Loyal Opposition review.
If the implementation-start gate cannot be repaired through a normal packet
after GO, Prime Builder must ask the owner for a one-time bootstrap override
before mutating protected targets.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped governance correction.
The owner has already selected the no-index invariant and reaffirmed that every
mutating task requires bridge protocol; this work repairs the protocol substrate
so those requirements can both be true.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Touch only local authorization/claim code and tests; do not log credentials. | Secret scan over changed files. | |
| CQ-PATHS-001 | Yes | Keep all changes under `E:\GT-KB` and target paths above. | Gate/path tests. | |
| CQ-COMPLEXITY-001 | Yes | Add a small versioned-file bridge-chain resolver instead of restoring index compatibility. | Source review and tests. | |
| CQ-CONSTANTS-001 | Yes | Centralize retired-index/no-index bridge resolution behavior. | Ruff and focused tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior: no GO/no claim/no valid version chain still blocks protected edits. | Negative tests. | |
| CQ-DOCS-001 | No | This is a substrate patch; user-facing guidance remains in the broader cleanup thread. | | Covered by `gtkb-bridge-index-retirement-cleanout`. |
| CQ-TESTS-001 | Yes | Add tests for absent `bridge/INDEX.md`, valid versioned GO chain, missing GO, stale claim, and wrong target path. | Focused pytest commands below. | |
| CQ-LOGGING-001 | Yes | Error messages should name the missing no-index resolver condition without suggesting recreating INDEX. | Assertion tests. | |
| CQ-VERIFICATION-001 | Yes | Verify a current packet can be issued for the cleanup GO while `Test-Path bridge/INDEX.md` remains false. | Commands below. | |

## Implementation Plan

1. Add a no-index bridge-chain resolver in `scripts/implementation_authorization.py`
   that discovers `bridge/<slug>-NNN.md` files, reads first-line statuses, sorts
   versions newest-first, and returns the same `BridgeEntry` shape currently
   built from `bridge/INDEX.md`.
2. Update `bridge_entry()` and validation so `bridge/INDEX.md` absence is not a
   failure. If an index exists unexpectedly, treat that as retired-state drift
   and prefer versioned files; do not recreate it.
3. Update `scripts/bridge_work_intent_registry.py` latest-status and version
   helpers to use versioned bridge files when the index is absent, so GO
   implementation claims and lapsed-claim checks work in no-index mode.
4. Keep authorization fail-closed:
   - no valid GO in versioned chain -> no packet
   - latest post-GO NEW/REVISED implementation report -> no packet
   - missing/expired mismatched claim -> no protected mutation
   - target outside packet -> no protected mutation
5. Update tests that currently construct `bridge/INDEX.md` as live authority.
   Retain index fixtures only if explicitly labeled historical/migration input.

## Spec-Derived Verification Plan

```powershell
Test-Path bridge/INDEX.md
```

Expected: `False`.

```powershell
python scripts/bridge_claim_cli.py claim gtkb-bridge-index-retirement-cleanout --session-id codex-no-index-auth-smoke --ttl-seconds 600
python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-index-retirement-cleanout --session-id codex-no-index-auth-smoke --no-write
python scripts/bridge_claim_cli.py release gtkb-bridge-index-retirement-cleanout --session-id codex-no-index-auth-smoke
```

Expected: authorization packet JSON is printed, references
`bridge/gtkb-bridge-index-retirement-cleanout-005.md` as the approved proposal
and `bridge/gtkb-bridge-index-retirement-cleanout-006.md` as the GO file, and no
`bridge/INDEX.md` is created.

```powershell
python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_claim_cli.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_claim_cli.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py scripts/bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_bridge_claim_cli.py
```

Expected: pass.

## Risks / Rollback

The main risk is accidentally weakening the implementation-start gate while
removing the index dependency. Mitigation: no-index resolution must preserve all
existing negative checks and add tests that prove missing GO, missing claim, and
out-of-scope paths still block.

Rollback is normal source/test revert. Do not restore `bridge/INDEX.md` as a
rollback mechanism.
