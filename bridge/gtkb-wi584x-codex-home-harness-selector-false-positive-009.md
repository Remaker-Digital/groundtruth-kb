REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb

# GT-KB Bridge Implementation Report (REVISED) - gtkb-wi584x-codex-home-harness-selector-false-positive - 009

bridge_kind: implementation_report
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 009
Responds to: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-008.md
Approved proposal: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-005.md
GO verdict: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-006.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5877
Linked Test: TEST-11805
target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]
implementation_scope: exact_reobservation_and_focused_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This report performs no MemBase or `groundtruth.db` write or mutation.

Recommended commit type: fix:

## Revision Claim

This REVISED implementation report responds to the version 008 NO-GO, which
found the version 007 report's evidence was materially inaccurate:

- **P1:** version 007 cited source SHA-256 `633e22ac...` and claimed the
  source was clean (`git status` empty for it). Independent re-observation
  shows the current working-tree source SHA-256 is `bae6cf9abd1d2514a70e31503aac6e27b4cfbac697d16db5755f3875e4902ed2` and `git status` reports `M scripts/bridge_work_intent_registry.py`, because a separate work item (WI-5841 durable-id harness-selector work) has added an overlapping uncommitted hunk to that file. Version 007's "source clean" claim conflated WI-5877's already-committed correction with the live working-tree state that now carries WI-5841's edits.
- **P2:** the cited `git show 633e22ac...` does not resolve; the HEAD blob SHA for the file is `f07fc5865061b2e84f340395af39371894ecd685`.

This revision corrects the evidence. The WI-5877 deliverable is:
1. The **source correction** (removing the permanent `CODEX_HOME` installation path as a live Codex harness selector) is **already committed at HEAD** — `git show HEAD:scripts/bridge_work_intent_registry.py` contains no `CODEX_HOME` live-selector reference, confirming the correction landed in the baseline. WI-5877 required no further source mutation.
2. The **focused regression tests** (the actual new delta) are the two tests added to `platform_tests/scripts/test_work_intent_role_eligibility.py` (+37 lines), staged in the working tree.

The WI-5877 delta is therefore isolated from WI-5841: WI-5841's durable-id selector hunk is a separate, concurrent source edit on the same file and is not part of WI-5877's contribution. This revision reports the true current SHA, the true `M` git status (WI-5841 overlap), and confines the WI-5877 delta to the two regression tests plus the already-committed source correction.

## Implementation Claim (corrected from version 007)

Implemented the approved WI-5877 CODEX_HOME selector false-positive correction
under independent GO v006, following the exact-reobservation-and-focused-test
scope of proposal v005.

- **Source defect already landed and committed at HEAD.** The one-line source
  correction (removing the permanent `CODEX_HOME` installation path as a live
  Codex harness selector) is present in the committed baseline
  `git show HEAD:scripts/bridge_work_intent_registry.py` (no `CODEX_HOME`
  live-selector reference). The selector honors `GTKB_HARNESS_NAME` first,
  then live `CODEX_THREAD_ID`, and never treats `CODEX_HOME` as a live session
  signal.
- **Missing focused regression added (the WI-5877 new delta).** Two
  deterministic tests were added to the declared test target:
  1. `test_go_impl_codex_home_alone_does_not_select_codex` - CODEX_HOME alone
     does not force the lookup into the Codex envelope; a non-Codex Prime
     Builder session envelope is found and its validated role controls claim
     eligibility.
  2. `test_go_impl_codex_thread_id_still_selects_codex` - CODEX_THREAD_ID
     remains the live Codex selector.
- Session-envelope provenance remains the only role authority; explicit
  `GTKB_HARNESS_NAME` precedence is preserved; no dispatcher/TAFE mutation;
  no foreign or quarantined evidence rewritten.

### Corrected Working-Tree Evidence (accurate at this filing)

- Current working-tree source SHA-256:
  `bae6cf9abd1d2514a70e31503aac6e27b4cfbac697d16db5755f3875e4902ed2`.
- HEAD blob SHA for `scripts/bridge_work_intent_registry.py`:
  `f07fc5865061b2e84f340395af39371894ecd685`.
- `git status --short -- scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py`:
  - `M  platform_tests/scripts/test_work_intent_role_eligibility.py` (WI-5877: +37 lines, the two regression tests).
  - `M  scripts/bridge_work_intent_registry.py` (WI-5841 durable-id selector overlap - separate work item, not a WI-5877 delta).
- Isolation: WI-5877's source contribution is the committed HEAD correction
  (no working-tree WI-5877 source hunk remains, because it is already in the
  baseline). The working-tree `M` on the source file is attributable to
  WI-5841, not WI-5877.

## Implementation Start Evidence

- Exact work-intent claim: row `36427`, session
  `G-2026-08-03T15-24-47Z`, acquired `2026-08-03T17:53:xxZ`,
  `claim_kind=go_implementation`, `latest_bridge_status=GO`.
- Fresh schema-v3 packet:
  `sha256:42e0e515880537974aa2a73c74199cc61369574edb223ee5dd9772292658af7d`.
- Packet finalized `2026-08-03T17:55:08Z`.
- `implementation_packet_create=allowed`; finalized
  `implementation_start=allowed`.
- Project authorization:
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2.
- Target classification:
  `scripts/bridge_work_intent_registry.py` (source),
  `platform_tests/scripts/test_work_intent_role_eligibility.py` (test).
- Controlling GO: `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-006.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

## Owner Decisions / Input

No new owner decision is required. The work item is an active member of the
owner-authorized `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` under active
list-free `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
v2. The exact-reobservation scope is expressly approved by proposal v005 and
its GO v006. No AUQ is requested.

## Prior Deliberations

- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-005.md` -
  approved implementation proposal carried forward (WI-5877 / TEST-11805).
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-006.md` -
  Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-008.md` -
  Loyal Opposition NO-GO (inaccurate SHA/git-status; WI-5841 source overlap).
- `DELIB-202667732` - owner-approved exact re-observation provenance.

## Findings Addressed

### Finding 1 (P1) - Version 007 cited stale SHA and claimed source clean; working tree carries a WI-5841 source edit

Response: Accepted and corrected. Version 007 cited SHA-256 `633e22ac...` and
claimed the source was clean, which was inaccurate. Current accurate state:
working-tree source SHA-256 is
`bae6cf9abd1d2514a70e31503aac6e27b4cfbac697d16db5755f3875e4902ed2`, and
`git status` reports `M scripts/bridge_work_intent_registry.py`. That
modification is attributable to WI-5841 (durable-id harness-selector work on
the same file), a separate work item; it is not a WI-5877 delta. WI-5877's
source contribution is the already-committed CODEX_HOME correction at HEAD
(no working-tree WI-5877 source hunk remains). The two focused regression tests
(+37 lines, staged) are WI-5877's actual new delta.

### Finding 2 (P2) - Cited git show 633e22ac... does not resolve; HEAD blob SHA differs

Response: Accepted and corrected. `git show 633e22ac...` does not resolve (the
value was not a valid commit/object for this file). The HEAD blob SHA for
`scripts/bridge_work_intent_registry.py` is
`f07fc5865061b2e84f340395af39371894ecd685`. This revision reports the true HEAD
blob SHA and the true working-tree SHA, and no longer asserts a nonexistent
object.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | CODEX_HOME alone does not select codex; non-Codex envelope role controls claim (re-run: 17 passed). |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Envelope provenance remains the only role authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only chain v005 proposal -> v006 GO -> v007 report -> v008 NO-GO -> v009 REVISED. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh packet PAUTH allowed for both operations. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal v005 carries Specification Links; carried forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=line` -> 17 passed. |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | No hard-coded timer / no dispatcher mutation. |
| `GOV-WORK-TREE-HYGIENE-001` | WI-5877 delta = 2 regression tests (+37 lines) + committed source correction; WI-5841 source hunk explicitly separated. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | CODEX_THREAD_ID + GTKB_HARNESS_NAME behavior preserved. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Defect, correction, regression tests, report durable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both targets inside mandatory GT-KB root. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | WI-5841 overlap isolated; no commingling of WI-5877 and WI-5841 source hunks. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=line` -> 17 passed.
- `python -m ruff check platform_tests/scripts/test_work_intent_role_eligibility.py` -> "All checks passed!".
- `python -m ruff format --check platform_tests/scripts/test_work_intent_role_eligibility.py` -> "1 file already formatted".
- `python -c "import hashlib; print(hashlib.sha256(open('scripts/bridge_work_intent_registry.py','rb').read()).hexdigest())"` -> `bae6cf9abd1d2514a70e31503aac6e27b4cfbac697d16db5755f3875e4902ed2`.
- `git rev-parse HEAD:scripts/bridge_work_intent_registry.py` -> `f07fc5865061b2e84f340395af39371894ecd685`.
- `git status --short -- scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py` -> `M` on both (test = WI-5877; source = WI-5841 overlap).
- `git show HEAD:scripts/bridge_work_intent_registry.py | findstr CODEX_HOME` -> no live `CODEX_HOME` selector reference (correction committed at HEAD).

## Observed Results

- Focused pytest: 17 passed (includes the 2 WI-5877 regression tests).
- Ruff check: "All checks passed!". Ruff format: "1 file already formatted".
- Accurate working-tree SHA: `bae6cf9...` (not the stale `633e22ac...`).
- HEAD blob SHA: `f07fc5865...`.
- WI-5841 source overlap isolated and disclosed; WI-5877 delta confined to the
  2 regression tests (+37 lines) and the committed source correction.

## Files Changed

WI-5877 delta:
- `platform_tests/scripts/test_work_intent_role_eligibility.py` (+37 lines: the
  two WI-5877 regression tests) - staged.
- `scripts/bridge_work_intent_registry.py` - correction already committed at
  HEAD; no WI-5877 working-tree source hunk. The current `M` on this file is
  WI-5841's durable-id selector work (separate work item).

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: adds the missing WI-5877 focused regression tests
  for the already-landed CODEX_HOME selector correction; isolates WI-5841
  overlap.

## Acceptance Criteria Status

- [x] CODEX_HOME alone selects no harness; a matching non-Codex session
      envelope can be found and its validated role controls claim eligibility.
- [x] CODEX_THREAD_ID continues to select Codex.
- [x] GTKB_HARNESS_NAME remains highest precedence as a document selector.
- [x] Session-envelope provenance remains the only role authority.
- [x] Accurate SHA/git-status reported; WI-5841 source overlap isolated and
      disclosed; WI-5877 delta confined to the 2 regression tests + committed
      source correction; no commingling of WI-5877 and WI-5841 source hunks.

## Risk And Rollback

The source correction was already committed before this cycle; the only new
artifact is the focused regression coverage. The working-tree `M` on the source
file is WI-5841's separate durable-id selector work and must be finalized under
WI-5841's own authority, not WI-5877's. Rollback for WI-5877 is removing the
two added tests; no source hunk requires revert. Bridge history remains
append-only; no governance or TAFE state is rewritten.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved
   proposal, otherwise return NO-GO with findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
