NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder
author_metadata_source: codex-system-runtime

# GT-KB Bridge Implementation Report - WI-5424 auto-finalization import repair v2

bridge_kind: implementation_report
Document: gtkb-wi5424-auto-finalization-import-repair-v2
Version: 003
Date: 2026-07-26 UTC
Responds to: bridge/gtkb-wi5424-auto-finalization-import-repair-v2-002.md
Approved proposal: bridge/gtkb-wi5424-auto-finalization-import-repair-v2-001.md

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5424

target_paths: ["scripts/auto_finalize_sweep.py", "platform_tests/hooks/test_auto_finalize_verified_verdicts.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Implementation Claim

The bounded repair is complete. The auto-finalization service now adds the live
`.claude/skills/gtkb-verify/helpers` directory to its import path instead of
the retired `.claude/skills/verify/helpers` directory. A focused regression
test binds the production constant and the imported `write_verdict.py` module
to that exact live directory.

The repair restores canonical VERIFIED-body validation and the downstream
protected-commit authorization check. It does not run the sweep, finalize a
verdict, stage or commit a file, change a hook registration, or modify a third
implementation path.

## Before And After Behavior

Before this repair, `_VERIFY_HELPERS` resolved to a directory that does not
exist. `_canonical_verdict_skip_reason` caught the resulting
`ModuleNotFoundError` and returned `canonical finalizer validation
unavailable`, so every otherwise eligible terminal verdict was skipped. The
focused baseline was 7 failed and 6 passed.

After this repair, `write_verdict` resolves from the live canonical helper
directory. The validator runs before the protected-commit authorization
checker, invalid verdicts still fail closed, and all 14 focused tests pass. The
sweep's fail-soft outer control flow and bounded Git subprocess behavior are
unchanged.

## GO Condition Disposition

| Condition | Disposition |
| --- | --- |
| F1: correct the false green baseline | Satisfied. The report records the observed pre-repair `7 failed, 6 passed` baseline and the post-repair `14 passed` result. The six previously passing tests remain green. |
| F2: correct before/after behavior | Satisfied in the preceding section. The before state names the failed import and blanket skip; the after state names restored validation without changing fail-soft or bounded-Git controls. |
| F3: prune over-linking or provide real evidence | Satisfied. Three unrelated links are removed with one-line rationales below, and every retained link has concrete executed evidence. |

## Specification Links

- `DCL-VERIFIED-BRIDGE-HISTORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Removed Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001`: removed because the two-file repair requests
  no owner choice and changes no AUQ surface.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: removed because the repair changes a
  shared service and focused test, not Codex or Claude hook registration.
- `GOV-STANDING-BACKLOG-001`: removed because this is not a bulk operation,
  creates no bulk inventory or review packet, and remains traceable through the
  existing WI-5424 record.

## Owner Decisions / Input

No new owner choice is needed. Existing authority is the active
`PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE`, whose owner
decision is `DELIB-202666274`. The GO, matching Prime claim, and
implementation-start packet authorize only the two declared targets.

## Prior Deliberations

- `DELIB-20266278` authorized the durability-treadmill drain program that
  established the auto-finalization service.
- `DELIB-202666599` established the invalid-body guard whose canonical
  validator import this repair restores.
- `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-001.md` is the
  approved proposal.
- `bridge/gtkb-wi5424-auto-finalization-import-repair-v2-002.md` is the
  independent GO with the three carried conditions addressed above.

No searched deliberation rejected this bounded import-root repair.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-VERIFIED-BRIDGE-HISTORY-001` | The 14-test focused module exercises eligible, invalid, checker-rejected, idempotent, audit, and import-origin paths; all pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show` returned latest `GO`; claim kind is `go_implementation`; packet hash is `sha256:6eaf29b7b9fc317636344dd5cae682ff76de1483856755dd2e3e6d7413b7507b`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5424, the numbered bridge chain, and this implementation report preserve the defect, authorization, implementation, and review lifecycle. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The exact report candidate was run through the mandatory applicability preflight with no missing required or advisory links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Every retained link is mapped in this table to executed evidence; the focused source-derived test module reports 14 passed. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The report carries PAUTH, project, WI, approved proposal, GO, and exact target metadata; packet operation-time evaluation allowed both targets. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed files and all report evidence are under `E:/GT-KB`; the packet classified only those in-root paths. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The report helper plan resolved v003 from the current GO chain and detected exactly the two approved-scope dirty files. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The lifecycle remains proposal NEW, independent GO, bounded implementation, report NEW, and pending independent verification. |
| `GOV-WORK-TREE-HYGIENE-001` | Windows Git shows exactly one production-line replacement and ten added test lines; Ruff check and format check both pass. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/hooks/test_auto_finalize_verified_verdicts.py -q --tb=short` before editing.
- The same focused pytest command after editing.
- `groundtruth-kb\.venv\Scripts\ruff.exe check scripts/auto_finalize_sweep.py platform_tests/hooks/test_auto_finalize_verified_verdicts.py`.
- `groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/auto_finalize_sweep.py platform_tests/hooks/test_auto_finalize_verified_verdicts.py`.
- `C:\Program Files\Git\cmd\git.exe diff -- scripts/auto_finalize_sweep.py platform_tests/hooks/test_auto_finalize_verified_verdicts.py`.
- `gt bridge show gtkb-wi5424-auto-finalization-import-repair-v2 --json --compact`.
- `python scripts/bridge_applicability_preflight.py --content-file <candidate-report>`.
- `python scripts/adr_dcl_clause_preflight.py --content-file <candidate-report>` in mandatory mode.

The production sweep command was deliberately not run, as required by the GO.

## Observed Results

- Pre-repair baseline: exit 1, 7 failed, 6 passed, 1 pre-existing
  `asyncio_mode` configuration warning. Every failure carried the stale-import
  signature or a downstream assertion caused by that signature.
- Post-repair focused suite: exit 0, 14 passed, 1 unchanged configuration
  warning.
- Ruff check: exit 0, all checks passed.
- Ruff format check: exit 0, both files already formatted.
- Windows Git diff: 11 insertions and 1 deletion across exactly two paths.
- Live module-origin assertion: `write_verdict.py` resolves from the canonical
  `gtkb-verify/helpers` directory and exposes callable
  `validate_verified_body`.
- Candidate applicability preflight: exit 0, no missing required specs, no
  missing advisory specs, no unclassified target paths, and no blocking errors.
- Candidate clause preflight: exit 0, no must-apply evidence gaps and no
  blocking gaps.

## Files Changed

- `platform_tests/hooks/test_auto_finalize_verified_verdicts.py`
- `scripts/auto_finalize_sweep.py`

## Scope Exclusions

This WI-5424 implementation performs no KB mutation, no MemBase write, and no
`groundtruth.db` change.

The helper reported one pre-existing out-of-scope dirty path: the already-filed
GO verdict. It was not modified. The implementation did not change the stale
rule reference owned by WI-5664, hook settings, bridge history, dispatcher or
harness state, `groundtruth.db`, release, or deployment surfaces.

Unrelated canonical backlog evidence updates to WI-5106 and WI-5541 occurred
under standing backlog authority during this session. They are not WI-5424
implementation changes, are absent from the Git diff, and are not claimed by
this report.

## Recommended Commit Type

- Recommended commit type: `fix`.
- Reason: one stale production import root is corrected and protected by one
  exact-origin regression test.
- No commit is authorized or attempted under this GO.

## Acceptance Criteria Status

- [x] The canonical validator imports from the live helper directory in
  production code.
- [x] The added exact-origin regression would fail on the old
  `.claude/skills/verify/helpers` constant and passes on the repaired
  `.claude/skills/gtkb-verify/helpers` constant.
- [x] GO-corrected criterion 3: the true baseline was 7 failed and 6 passed;
  after repair all 14 tests pass, the six pre-existing passes remain green, and
  no third implementation path changed.
- [x] The sweep itself was not run and no verdict was finalized.

The proposal's original statement that all existing focused tests were green is
superseded by the GO's F1 condition and the measured baseline above.

## Risk And Rollback

Residual risk is narrow: the import remains a path-based coupling to the
canonical skill helper, so a future skill rename must update this service and
its exact-origin test atomically. The restored validator can now reject malformed
legacy verdicts that the broken import previously skipped wholesale; that is
the intended fail-closed behavior.

Rollback requires separate authority to revert only the source and test changes,
followed by the focused pytest and Ruff commands. The numbered bridge chain
remains append-only. Rollback must not run the sweep or delete audit evidence.

## Applicability Preflight

The exact pending v003 candidate was run through
`bridge_applicability_preflight.py` before governed publication.

- preflight passed: true
- missing required specifications: none
- missing advisory specifications: none
- unclassified target paths: none
- blocking errors: none
- author metadata warnings: none

The governed writer will rerun its candidate checks before the bridge file
reaches disk.

## Clause Applicability (Slice 2; Mandatory Gate)

The exact pending v003 candidate was run in mandatory mode before governed
publication.

- clauses evaluated: 5
- must apply: 5
- evidence gaps in must-apply clauses: 0
- blocking gaps: 0
- mandatory-mode exit: 0

## Loyal Opposition Asks

1. Reproduce the 14-test focused result and exact helper-module origin.
2. Confirm all three v002 GO conditions are satisfied and only the two declared
   targets changed.
3. Return VERIFIED only for this bounded repair; otherwise return NO-GO with
   exact findings.
