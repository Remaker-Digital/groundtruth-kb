REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T15-02-41Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5658 by-reference bridge-audit materialization

bridge_kind: prime_proposal
Document: gtkb-wi5658-terminal-verdict-recovery
Version: 003
Responds to: bridge/gtkb-wi5658-terminal-verdict-recovery-002.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5658

target_paths: ["bridge/gtkb-wi5658-terminal-verdict-recovery-001.md", "bridge/gtkb-wi5658-terminal-verdict-recovery-002.md", "bridge/gtkb-wi5658-terminal-verdict-recovery-003.md", "bridge/gtkb-wi5658-terminal-verdict-recovery-004.md", "bridge/gtkb-wi5658-terminal-verdict-recovery-005.md", "bridge/gtkb-wi5658-terminal-verdict-recovery-006.md"]

implementation_scope: governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover WI-5658 through a fresh, append-only bridge-audit chain whose
terminal transaction is independently finalizable. The performance source/test
implementation is immutable at commit 93f7764662853b3f86a714d34555303a62c2321d
and is not a target of this recovery.

## Claim

Prime Builder proposes a bridge-artifact-only recovery. The untracked original
performance report and file-only verdict are quarantine evidence, never
completion evidence and never staging inputs. The new recovery chain records
the committed source identity, materializes only its own reviewed bridge
predecessors, and then permits an LO helper-mediated terminal transaction.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-202667183, sourced from
AUQ-2026-07-23-WI5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE, authorized the
bounded performance-only source/test work and its PAUTH. DELIB-20265762
requires a fail-closed recovery instead of a second file-only VERIFIED state.
No new source implementation or owner decision is requested.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Committed Implementation Identity

- Commit: 93f7764662853b3f86a714d34555303a62c2321d
- Authorized implementation paths: scripts/check_protected_commit_authorization.py
  and platform_tests/scripts/test_check_protected_commit_authorization.py
- Commit diff: 90 insertions and 18 deletions in the checker; 72 test
  insertions; predecessor bridge -001/-002 are already committed.
- Focused evidence observed now:
  - pytest -k wi5658: 3 passed, 110 deselected
  - Ruff check: pass
  - Ruff format --check: two files already formatted
  - git diff --check for the commit's two implementation paths: pass

## Quarantine And Non-Staging Disposition

- bridge/gtkb-wi5658-protected-commit-checker-performance-003.md and -004.md
  remain untracked false-terminal evidence. Do not stage, delete, amend,
  include, or cite them as terminal proof.
- No source/test file is staged, restaged, or changed in this recovery.
- The recovery chain's -001 and -002 are new, untracked, and will be
  materialized only as the fresh chain's own audit evidence after GO.

## Exact Recovery And Finalization Transaction

1. Independent LO reviews this version and, if satisfied, publishes recovery
   -004 GO.
2. With that GO and a fresh Prime implementation claim, create one
   non-terminal bridge-audit materialization commit containing exactly recovery
   -001 NEW, -002 NO-GO, -003 REVISED, and -004 GO. No source/test path and no
   original false-terminal path is allowed.
3. Prime Builder files recovery -005 as an implementation report. It records
   the immutable commit identity, the focused results above, the exact
   materialization-commit SHA/path set, and the by-reference waiver below.
   Commit recovery -005 alone as the report-audit predecessor.
4. Independent LO invokes the canonical finalizer to create recovery -006
   VERIFIED and its atomic local commit. It must verify that all recovery
   predecessors are committed, the final staged/committed set contains only
   -006 plus declared bridge-audit evidence, and Commit Finalization Evidence
   is present.
5. The original false terminal files remain quarantined after closure; the new
   recovery chain is the only completion authority.

## By-Reference Finalization Waiver

By-reference audit finalization is permitted for this recovery because
DELIB-202667183 authorizes the original performance-only implementation and
its immutable commit. The waiver is narrow: it never authorizes source/test
restaging, the original false terminal chain, unrelated dirty paths, or a
file-only terminal verdict. The independent LO helper remains mandatory.

## Specification-Derived Verification Plan

    git show --stat --oneline --no-renames 93f7764662853b3f86a714d34555303a62c2321d
    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -k wi5658 -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
    git diff --check 93f7764662853b3f86a714d34555303a62c2321d^ 93f7764662853b3f86a714d34555303a62c2321d -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
    python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5658-terminal-verdict-recovery
    python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5658-terminal-verdict-recovery

## Acceptance Criteria

- The committed two-path source/test implementation is identified and tested
  without restaging or rewriting it.
- The false original -003/-004 artifacts remain quarantined and excluded from
  every recovery commit.
- A non-terminal materialization commit and report-audit commit make the fresh
  recovery chain finalizer-eligible before LO terminal action.
- Only the canonical helper may issue VERIFIED, with complete finalization
  evidence and a committed terminal artifact.

## Cross-Harness Disposition

This is a bridge-audit recovery only. It changes no harness behavior, adapter,
hook, dispatcher, or protected checker semantics.

## Risks And Rollback

The risk is another file-only terminal state or an accidental source/test
restage. The two-step predecessor materialization and LO helper finalizer fail
closed. Rollback reverts only a later bridge-audit commit; neither the
immutable implementation nor quarantined evidence is deleted.

## Owner Decisions / Input

- DELIB-202667183 — AUQ-2026-07-23-WI5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE:
  owner authorized the bounded performance-only source/test implementation.
- PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI-5658-PROTECTED-COMMIT-CHECKER-PERFORMANCE-FIX
  carries that source boundary into the project lifecycle.
- DELIB-20265762 requires fail-closed terminal recovery.

## Recommended Commit Type

chore

