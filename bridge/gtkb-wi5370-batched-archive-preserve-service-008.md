NO-GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5370-batched-archive-preserve-service
Version: 008
Responds to: bridge/gtkb-wi5370-batched-archive-preserve-service-007.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Review Verdict - NO-GO - WI-5370 Batched Archive Preserve Service v007

## Verdict

NO-GO. v007 is actionable, but it is not verification-ready and the current target bytes still preserve the prior blockers. The bridge entry is a `REVISED` `prime_proposal` that says a refreshed implementation report "will" make corrections, while `scripts/batch_archive_terminal_verdicts.py` and its focused test still conflict with the governing terminal-status taxonomy and the cleanup acceptance criteria.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `NO-GO`, a Loyal Opposition review status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Reviewed artifact author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

- packet_hash: `sha256:0d62cc2611889ad0a1c7ef465fec5979a9d445061310f5276545eab98e2e8e23`
- bridge_document_name: `gtkb-wi5370-batched-archive-preserve-service`
- content_file: `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md`
- operative_file: `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:b96d66ac4436e47b366f87cc10cc6c827fbfc16a28e49a3848f571698f3477a0`

## Clause Applicability

- Bridge id: `gtkb-wi5370-batched-archive-preserve-service`
- Operative file: `bridge\gtkb-wi5370-batched-archive-preserve-service-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory mode exit: 0

## Prior Deliberations

- `DELIB-202666766` - owner AUQ deciding archive-preserve disposition for legacy terminal bridge verdicts.
- `bridge/gtkb-wi5370-batched-archive-preserve-service-004.md` - prior GO for implementation.
- `bridge/gtkb-wi5370-batched-archive-preserve-service-006.md` - prior NO-GO with the terminal taxonomy and cleanup blockers.
- `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md` - revised proposal under this review.

## Specification Links

- `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Blocking Findings

### F1 - Terminal taxonomy still conflicts with the governing DCL

The governing DCL says an archive-preserve candidate terminal token is exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`, or `ADVISORY`. The current source still defines `TERMINAL_STATUSES` as `{"VERIFIED", "DEFERRED", "WITHDRAWN", "RETIRED", "SUPERSEDED"}` at `scripts/batch_archive_terminal_verdicts.py:44`, and candidate discovery filters through that set at `scripts/batch_archive_terminal_verdicts.py:161` and `scripts/batch_archive_terminal_verdicts.py:165`.

This means `ADVISORY` is still wrongly excluded, while `RETIRED` and `SUPERSEDED` remain wrongly eligible. v007 itself states the required correction at `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md:80`, but the target bytes have not made that correction.

### F2 - Commit-failure cleanup still strands same-attempt archive copies

The implementation still copies archives before commit, then returns after commit failure without removing same-attempt archive copies: `scripts/batch_archive_terminal_verdicts.py:296` through `scripts/batch_archive_terminal_verdicts.py:302`. Discovery then skips existing archive targets at `scripts/batch_archive_terminal_verdicts.py:175`, so a failed attempt can make a retry non-clean.

The focused test still encodes the wrong acceptance behavior. `platform_tests/scripts/test_batch_archive_terminal_verdicts.py:189` through `platform_tests/scripts/test_batch_archive_terminal_verdicts.py:198` creates `.git/index.lock`, expects an error, expects the source to remain, and also asserts that the archive copy exists. v007 requires the opposite for same-invocation archive copies: source present, archive copy absent, no archive path staged, and retry possible without manual cleanup.

### F3 - v007 is structurally not an implementation report

The latest bridge entry is `REVISED` and declares `bridge_kind: prime_proposal` at `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md:1` and `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md:15`. Its wording repeatedly promises what a refreshed implementation report will do, including at `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md:76` and `bridge/gtkb-wi5370-batched-archive-preserve-service-007.md:88`.

That is acceptable as a proposal shape only if it is reviewed as a proposal. It is not sufficient for implementation verification, and the live target bytes still fail the substantive requirements above.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` | `groundtruth-kb\.venv\Scripts\gt.exe spec show DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` plus source review | yes | FAIL: source taxonomy still excludes `ADVISORY` and includes `RETIRED`/`SUPERSEDED`. |
| `DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001` | Focused cleanup-path source and test review | yes | FAIL: commit failure returns with same-attempt archive copies still present, and the test asserts that stale copy exists. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --dry-run --json` | yes | FAIL: dry run exits 0 but reports `verified_overall: false`; multiple cited specs have no derived tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge` and applicability preflight | yes | PASS: latest actionable file is v007 `REVISED`, prior NO-GO v006 is visible, and drift is empty. |

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5370-batched-archive-preserve-service --format json --preview-lines 8
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --content-file bridge/gtkb-wi5370-batched-archive-preserve-service-007.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --content-file bridge/gtkb-wi5370-batched-archive-preserve-service-007.md
groundtruth-kb\.venv\Scripts\gt.exe spec show DCL-ARCHIVE-PRESERVE-TERMINAL-VERDICT-DISPOSITION-001
python scripts/run_spec_derived_tests.py --bridge-id gtkb-wi5370-batched-archive-preserve-service --dry-run --json
rg -n "TERMINAL_STATUSES|existing archive target|commit failed|return BatchResult|archive target|archive_path|git commit" scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py bridge/gtkb-wi5370-batched-archive-preserve-service-007.md
git status --short -- scripts/batch_archive_terminal_verdicts.py platform_tests/scripts/test_batch_archive_terminal_verdicts.py bridge/gtkb-wi5370-batched-archive-preserve-service-007.md
```

## Required Corrections

1. Replace terminal candidate taxonomy with exactly `VERIFIED`, `WITHDRAWN`, `DEFERRED`, and `ADVISORY`.
2. Add tests that accept `ADVISORY` and reject `RETIRED` plus `SUPERSEDED` unless a future governed DCL changes that set.
3. On commit failure, remove only same-invocation archive copies whose recorded size and SHA-256 still match, and prove no archive path remains staged.
4. File a true implementation report with executed evidence after source and tests are corrected.

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, gtkb-verify
