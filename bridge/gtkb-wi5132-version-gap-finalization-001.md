NEW

# WI-5132: Tolerate Genuine Version Gaps in VERIFIED Finalization

bridge_kind: prime_proposal
Document: gtkb-wi5132-version-gap-finalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5132

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

implementation_scope: source and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`_assert_predecessor_chain_committed` currently loops every numeric version
between one and the new VERIFIED verdict and fails whenever a corresponding
`bridge/<slug>-NNN.md` is absent. This treats a genuine historical numbering
gap as tampering and prevents finalization of otherwise valid threads such as
the dashboard Slice 2A chain, whose versions jump from 003 to 007 because
004-006 belong to separate sibling slugs.

Extend the predecessor check to distinguish a genuine gap from a missing
historical artifact. For an absent on-disk predecessor, query Git history for
that exact path: allow only when no history record exists; fail closed when the
path existed in history or history inspection itself fails. Existing checks for
present untracked or dirty predecessor files remain unchanged.

The implementation is sequenced behind any active WI-5112 implementation
claim because both WIs share the three parity helper copies and atomicity test.
This proposal itself does not mutate those currently foreign-dirty paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protects the append-only bridge audit
  without fabricating missing predecessor files.
- `GOV-WORK-TREE-HYGIENE-001` - preserves fail-closed treatment of present
  uncommitted predecessor artifacts.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - first-wave PAUTH bounds
  this source/test work to WI-5132.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - finalization remains
  subject to the existing verified-commit, bridge, and coverage gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the protected
  helper and test changes carry concrete governing links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item,
  and target paths are explicit and machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused tests prove
  genuine-gap allowance and historical-artifact rejection.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - all three helper projections
  stay byte-identical.

## Prior Deliberations

- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - owner authorization for the
  bounded stabilization drive.
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - authorizes WI-5132
  under the active tree-stabilization PAUTH.
- WI-5132 work item - captures the dashboard Slice 2A finalization block and
  forbids fabricating absent append-only bridge files.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-001.md` - adjacent
  shared-helper finalization proposal; implementation claims must serialize.

## Owner Decisions / Input

`DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` authorizes this bounded
source/test proposal under
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710`. It preserves
independent LO review, implementation-start authorization, non-destructive
operation, and the prohibition on fabricating bridge history or committing
unrelated dirty files.

## Requirement Sufficiency

Existing requirements sufficient. The bridge-audit, worktree-hygiene,
project-authorization, verified-testing, and cross-harness parity requirements
already specify the relevant integrity constraints for this bounded repair.

## Cross-Harness Disposition

- Claude Code: `.claude/skills/verify/helpers/write_verdict.py` remains the
  canonical finalization helper and receives the history-aware gap check.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` remains a byte-identical
  projection of the canonical helper; it changes in the same transaction and
  is covered by parity tests.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` remains a
  byte-identical projection and is included with matching parity coverage.
- Antigravity, Ollama, and OpenRouter: no separate in-repository projection is
  declared for this helper surface, so no additional target path is needed.

## Specification-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .harness-tmp/wi5132` | A synthetic valid thread with missing numeric versions that never existed in Git finalizes without fabricated files. |
| `GOV-WORK-TREE-HYGIENE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Same focused suite with a predecessor path present in Git history but now absent, plus present dirty/untracked predecessors | Historical absence and current uncommitted predecessors still fail closed; only a proven never-existed gap is allowed. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Same focused suite's byte-parity assertion | Claude, Codex, and Cursor helper bytes are identical. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ruff check and Ruff format check on the three helpers and atomicity test | Focused tests, lint, and formatting checks pass. |

## Risk / Rollback

The risk is accepting a deletion as a genuine gap. The design prevents that by
checking the exact path across Git history and failing closed on either a
positive historical record or an inspection error. Existing present-file
tracking and dirtiness checks remain untouched. Rollback is a scoped revert of
the three parity helpers and focused test; no bridge file is fabricated, no
database state changes, and no generated registry projection is included.

## Bridge Filing

This proposal creates the first append-only numbered bridge file for WI-5132.
No existing bridge thread is rewritten. Implementation remains prohibited until
independent LO GO and implementation-start authorization; it will not start
while WI-5112 owns the overlapping helper paths.

## Recommended Commit Type

`fix` - restores VERIFIED finalization for valid gapped bridge threads without
weakening historical-artifact integrity.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
