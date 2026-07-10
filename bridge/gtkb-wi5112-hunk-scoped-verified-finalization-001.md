NEW

# WI-5112: Hunk-Scoped VERIFIED Finalization

bridge_kind: prime_proposal
Document: gtkb-wi5112-hunk-scoped-verified-finalization
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
Work Item: WI-5112

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

implementation_scope: source and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5112 closes the whole-file staging defect in VERIFIED finalization. Today
`finalize_verified_commit` stages every declared `--include` path through
`git add -f`, which stages foreign hunks on a shared dirty file and attributes
them to the current thread's VERIFIED commit. WI-5083's commit `b584d0d4`
demonstrated this by sweeping WI-5100's carve-out under the wrong subject;
WI-4841 is currently blocked by the same class in a shared registry and
manifest.

Add an explicit hunk-patch staging mode to all three parity copies of
`write_verdict.py`. The LO verifier may supply a unified patch whose declared
paths are inside the existing `--include` set. The helper validates the patch
path set, applies only those selected hunks to the index with `git apply
--cached`, stages ordinary non-patched include paths as before, and commits
only the declared verified paths plus the new VERIFIED verdict. The working
tree retains foreign hunks not selected by the cached patch.

This is not an owner waiver and does not weaken coverage: report-claimed paths
remain required in the include set, patch paths must be a subset of that set,
and any malformed, out-of-scope, non-applicable, or staged-set-mismatched patch
fails closed and removes the just-written verdict.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - VERIFIED remains an atomic bridge and
  commit-finalization outcome.
- `GOV-WORK-TREE-HYGIENE-001` - finalization must not commit unrelated dirty
  work from a shared tree.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the first-wave PAUTH
  bounds this source/test work to WI-5112.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - hunk staging remains under
  the existing bridge, report-coverage, and verified-commit gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  supplies concrete governing links for its protected helper and test scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal metadata and
  target scope remain machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused finalization
  regression tests provide executed verification evidence.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Claude, Codex, and Cursor
  verification-helper copies remain byte-identical.

## Prior Deliberations

- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - owner authorization for the
  bounded stabilization drive.
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - authorizes WI-5112
  under the active tree-stabilization PAUTH.
- WI-5112 work item - records the WI-5083/WI-5100 misattribution defect.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-020.md` - current
  NO-GO proving whole-file finalization cannot isolate shared registry hunks.
- `bridge/gtkb-wi5105-finalization-commingle-guard-001.md` - complementary
  start-time prevention; this proposal remediates already-commingled work.

## Owner Decisions / Input

`DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` authorizes this bounded
source/test proposal under
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710`. It preserves
independent LO review, implementation-start authorization, non-destructive
operation, and the prohibition on committing unrelated dirty files.

## Requirement Sufficiency

Existing requirements sufficient. The verified-finalization, worktree-hygiene,
project-authorization, bridge-linkage, and cross-harness-parity requirements
define the necessary behavior; no new specification is required for this
bounded helper capability.

## Cross-Harness Disposition

- Claude Code: `.claude/skills/verify/helpers/write_verdict.py` remains the
  canonical verification-finalization helper and receives the hunk-patch mode.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` remains a byte-identical
  projection of the canonical helper; this proposal changes it in the same
  transaction and tests parity.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` remains the same
  byte-identical projection and is in scope with its matching parity test.
- Antigravity, Ollama, and OpenRouter: no separate in-repository
  `write_verdict.py` projection is declared for this helper surface; their
  verification flows consume the canonical governed protocol and require no
  additional target path in this bounded slice.

## Specification-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .harness-tmp/wi5112` | A synthetic shared file with selected WI-A and foreign WI-B hunks finalizes only WI-A's cached hunk, report, and VERIFIED verdict; WI-B remains uncommitted in the working tree. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Same focused suite with malformed, out-of-scope, and non-applicable patch fixtures | Hunk patches outside `--include`, patches that do not apply to the index, and staged-set mismatches fail closed without a lingering VERIFIED verdict. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Same suite plus byte-parity assertion | Claude, Codex, and Cursor helper bytes remain identical. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py` and corresponding `ruff format --check` | Focused tests, lint, and formatting checks pass. |

## Risk / Rollback

The main risk is a malformed patch staging an unintended path. Validation is
therefore restrictive: every patch file must identify only concrete paths in
the existing include set, must apply cleanly to the current index, and must
leave the staged-set assertion satisfied before commit. A failure removes the
new verdict and unstages only helper-added work. Rollback is a scoped revert of
the three parity helpers and focused test; no bridge history, database, or
generated registry projection is changed.

## Bridge Filing

This proposal creates the first append-only numbered bridge file for WI-5112.
No existing bridge thread is rewritten. A later implementation report will
request LO verification; this proposal does not authorize implementation until
an independent GO and implementation-start packet exist.

## Recommended Commit Type

`fix` - closes an existing cross-work-item finalization and attribution defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
