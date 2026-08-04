NEW
::init gtkb pb
::open build

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-03T15-24-47Z
author_model: DeepSeek V4 Flash 0731
author_model_version: DeepSeek V4 Flash 0731
author_model_configuration: Goose desktop interactive Prime Builder; transcript-resolved ::init gtkb pb
author_metadata_source: explicit current-session metadata

bridge_kind: implementation_report
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-006.md
Approved proposal: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-005.md
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

# GT-KB Bridge Implementation Report - gtkb-wi584x-codex-home-harness-selector-false-positive - 007

## Implementation Claim

Implemented the approved WI-5877 CODEX_HOME selector false-positive correction
under independent GO v006, following the exact-reobservation-and-focused-test
scope of proposal v005.

- **Source defect already landed.** The one-line source correction (removing
  the permanent `CODEX_HOME` installation path as a live Codex harness
  selector) is already present and committed in
  `scripts/bridge_work_intent_registry.py`. Current source SHA-256
  `633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3` matches
  the proposal v005 `source_current_sha256` exactly. The selector now honors
  `GTKB_HARNESS_NAME` first, then live `CODEX_THREAD_ID`, and never treats
  `CODEX_HOME` as a live session signal.
- **Missing focused regression added.** I added two deterministic tests to the
  declared test target:
  1. `test_go_impl_codex_home_alone_does_not_select_codex` — CODEX_HOME alone
     does not force the lookup into the Codex envelope; a non-Codex Prime
     Builder session envelope is found and its validated role controls claim
     eligibility.
  2. `test_go_impl_codex_thread_id_still_selects_codex` — CODEX_THREAD_ID
     remains the live Codex selector.
- Session-envelope provenance remains the only role authority; explicit
  `GTKB_HARNESS_NAME` precedence is preserved; no dispatcher/TAFE mutation;
  no foreign or quarantined evidence rewritten.

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

## Owner Decisions / Input

No new owner decision is required by this implementation report. The work item
is an active member of the owner-authorized `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
under active list-free
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2.
The exact-reobservation scope is expressly approved by proposal v005 and its
GO v006. No AUQ is requested.

## Prior Deliberations

- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-005.md` -
  approved implementation proposal carried forward (WI-5877 / TEST-11805).
- `bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-006.md` -
  Loyal Opposition GO verdict authorizing implementation.
- `DELIB-202667732` - owner-approved exact re-observation provenance.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001` | CODEX_HOME alone does not select codex; non-Codex envelope role controls claim |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Envelope provenance remains the only role authority |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only chain v005 proposal → v006 GO → this v007 report |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh packet PAUTH allowed for both operations |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal v005 carries Specification Links; carried forward |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Executed focused pytest + ruff evidence recorded below |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | No hard-coded timer / no dispatcher mutation |
| `GOV-WORK-TREE-HYGIENE-001` | Only declared test target modified; source clean and byte-exact |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | CODEX_THREAD_ID + GTKB_HARNESS_NAME behavior preserved |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Defect, correction, regression tests, report durable |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both targets inside mandatory GT-KB root |

## Commands Run

- `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=line`
- `python -m ruff check platform_tests/scripts/test_work_intent_role_eligibility.py`
- `python -m ruff format --check platform_tests/scripts/test_work_intent_role_eligibility.py`
- `sha256sum scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py`
- `git --no-optional-locks status --short scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py`

## Observed Results

- Focused pytest: **17 passed** (includes the 2 new WI-5877 regression tests).
- New regression tests:
  - `test_go_impl_codex_home_alone_does_not_select_codex`: **passed**.
  - `test_go_impl_codex_thread_id_still_selects_codex`: **passed**.
- `ruff check`: **All checks passed!**
- `ruff format --check`: **1 file already formatted**.
- Source SHA-256 `633e22ac...` matches proposal v005 `source_current_sha256`
  exactly (source defect already committed; no source mutation this cycle).
- `git status`: only the declared test target modified (+37 lines); source clean.

## Files Changed

- `platform_tests/scripts/test_work_intent_role_eligibility.py` (+37 lines)

Source `scripts/bridge_work_intent_registry.py` was already at the corrected
byte-identity; no source mutation was required or made.

Excluded out-of-scope dirty paths: 149.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: adds the missing WI-5877 focused regression tests
  for the already-landed CODEX_HOME selector correction.

```text
 platform_tests/scripts/test_work_intent_role_eligibility.py | 37 ++++++++++++++++++++++
```

## Acceptance Criteria Status

- [x] CODEX_HOME alone selects no harness; a matching non-Codex session
      envelope can be found and its validated role controls claim eligibility.
- [x] CODEX_THREAD_ID continues to select Codex.
- [x] GTKB_HARNESS_NAME remains highest precedence as a document selector.
- [x] Session-envelope provenance remains the only role authority.
- [x] Only the declared test target changed; source is clean and byte-exact to
      the reviewed hunk; no dispatcher/TAFE/foreign/quarantined rewrite.

## Risk And Rollback

The source correction was already committed before this cycle; the only new
artifact is the focused regression coverage. Rollback is removing the two added
tests if they are ever found to over-constrain selector behavior; no source
hunk requires revert. Bridge history remains append-only; no governance or TAFE
state is rewritten.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved
   proposal, otherwise return NO-GO with findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
