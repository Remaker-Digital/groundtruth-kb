REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5657 audit-only terminal-finalization recovery

bridge_kind: prime_proposal
Document: gtkb-wi5657-terminal-finalization-audit-recovery
Version: 005
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657
Responds to: bridge/gtkb-wi5657-terminal-finalization-audit-recovery-004.md

target_paths: ["bridge/gtkb-wi5657-terminal-finalization-audit-recovery-007.md"]

implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover WI-5657 through an audit-only, append-only terminal-finalization chain.
The implementation is immutable in commit
`7b838d9e7606a8b1f8be75ade78881f63beda170`; this proposal neither modifies nor
re-stages its source/test paths. The only prospective PB artifact is recovery
report `bridge/gtkb-wi5657-terminal-finalization-audit-recovery-007.md`.

## Fresh-Carrier Disposition

Version 001 is immutable, committed provenance evidence, but its bare
`author_identity: codex` cannot resolve to Prime Builder. Version 002 therefore
cannot supply executable GO authority. Versions 003 and 004 correctly record
the packet denial and require this append-only retry; none authorizes source,
test, staging, or terminal mutation.

This version is the fresh provenance-valid implementation proposal. After an
independent version 006 GO, the only prospective Prime Builder implementation
artifact is version 007. The exact-session claim and implementation-start
packet must bind to this version-005 carrier. Failure at PAUTH classification,
waiver lookup, author provenance, or any other start gate produces another
nonterminal stop report; it never licenses a manual report, file-only VERIFIED,
or retrospective adoption of the invalid version-001 GO.

The already-committed version 001 remains read-only. Any eventual terminal
transaction must stage only the then-untracked recovery chain versions 002
through 007 plus the helper-generated version 008 verdict, and must leave the
immutable implementation commit and its source/test paths untouched.

## Claim

After a fresh independent GO, Prime Builder will revalidate the committed
implementation evidence and file only the named recovery report. An independent
LO finalizer may create a terminal verdict only if a helper-recognized,
owner-authorized by-reference waiver permits finalization of the already
committed implementation. If no valid waiver exists, the finalizer must fail
closed and return NO-GO identifying the exact waiver requirement; no file-only
VERIFIED verdict is permitted.

## Requirement Sufficiency

Existing requirements sufficient for the audit-only recovery. `DELIB-202667182`
authorizes the bounded original source/test fix; it does not by itself waive
same-transaction finalization. The recovery expressly preserves that distinction.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667182` — owner AUQ for the bounded superseded-predecessor checker
  fix, linked to the exact WI-5657 PAUTH.
- `DELIB-20265762` — terminal-finalization precedent requiring fail-closed
  recovery rather than a file-only VERIFIED artifact.
- `bridge/gtkb-wi5657-protected-commit-superseded-verified-004.md` — committed
  source/test evidence and failed finalizer history.

## Owner Decisions / Input

- `DELIB-202667182` authorizes only the two committed implementation paths and
  their behavior boundary.
- No by-reference waiver is inferred. If finalization requires one, the
  finalizer must request/cite an explicit governing record before terminal state.

## Immutable Evidence And Exact Finalization Contract

Read-only evidence:

- commit `7b838d9e7606a8b1f8be75ade78881f63beda170`;
- `scripts/check_protected_commit_authorization.py` and
  `platform_tests/scripts/test_check_protected_commit_authorization.py` from
  that commit;
- committed historical bridge files
  `gtkb-wi5657-protected-commit-superseded-verified-001.md` through `-004.md`.

The recovery report must record the committed diff, the focused test/lint/format
results, the by-reference waiver lookup/result, and the exact finalization
candidate. A successful LO terminal transaction is limited to recovery
`-001`, `-002`, `-003`, and its newly generated `-004` verdict; it must use
`--finalize-verified` and commit those recovery artifacts atomically. It must
not alter or re-stage the already committed source/test paths.

## Verification Plan

1. Recheck that the immutable commit contains only the expected two source/test
   paths plus its committed historical audit chain.
2. Re-run the committed implementation’s focused test module plus Ruff check,
   Ruff format check, and `git diff --check` against its two paths.
3. Run recovery applicability and mandatory clause preflights.
4. Query the finalizer for a valid owner-authorized by-reference waiver. A
   missing or invalid waiver is a nonterminal NO-GO outcome.
5. With a valid waiver only, LO uses the canonical `--finalize-verified` helper
   and the four-artifact recovery include set; the helper must create the commit
   or remove its partial verdict and fail closed.

## Pre-Filing Preflight

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/wi5657-audit-recovery-001.md` passed with packet hash `sha256:d7c39d5eb0a6ef4663f0f1c846892e034d1e334e6b3bb91266148d13017504b9`, no missing required/advisory specifications, and no blocking errors.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/wi5657-audit-recovery-001.md` passed: three must-apply clauses, zero evidence gaps, and zero blocking gaps.

## Specification-Derived Verification Mapping

| Requirement | Evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Recovery chain is independently reviewed; terminal verdict is helper-finalized in one commit or absent. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Recovery preflights and explicit project/PAUTH/WI metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused protected-commit test module, Ruff check/format, diff check, and recorded finalizer outcome. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Immutable source evidence and append-only recovery artifacts remain separately identifiable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No terminal state before a valid waiver and commit-finalization evidence exist. |

## Acceptance Criteria

- No source/test target is claimed or changed by this recovery.
- The report records the exact immutable commit, test/quality evidence, waiver
  result, and recovery finalization candidate.
- Any terminal verdict is helper-finalized in an atomic commit; otherwise this
  recovery remains nonterminal.

## Risks And Rollback

The main risk is using audit-only bridge work to mask an absent finalization
waiver. The waiver lookup is mandatory and fail-closed. Rollback can only be a
separate governed revert of a future recovery-artifact commit; immutable source
and historical bridge evidence are never rewritten.

## Recommended Commit Type

chore
