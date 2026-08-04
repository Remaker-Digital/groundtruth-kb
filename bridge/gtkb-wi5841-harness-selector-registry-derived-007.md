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
Document: gtkb-wi5841-harness-selector-registry-derived
Version: 007 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5841-harness-selector-registry-derived-006.md
Approved proposal: bridge/gtkb-wi5841-harness-selector-registry-derived-005.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5841
target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_implementation_authorization_harness_selector.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This report performs no MemBase or `groundtruth.db` write or mutation.

Recommended commit type: feat:

# GT-KB Bridge Implementation Report - gtkb-wi5841-harness-selector-registry-derived - 007

## Implementation Claim

Implemented the approved registry-derived durable-ID harness selector (S1/S2/S3)
under independent GO v006, per proposal v005.

- **S1 — one registry-derived selector contract.** `_worker_harness_selector`
  in `scripts/bridge_work_intent_registry.py` now:
  1. honors a nonblank `GTKB_HARNESS_NAME` (highest precedence);
  2. returns `None` under `GTKB_BRIDGE_POLLER_RUN_ID` so dispatched work cannot
     inherit the parent harness identity;
  3. maps `GTKB_HARNESS_ID` or `GTKB_AUTHOR_HARNESS_ID` through the canonical
     `groundtruth_kb.harness_projection.read_identity()` reader to the
     registered harness name — failing closed (`ValueError`) on conflicting,
     unknown, non-unique, unavailable, or malformed identity data rather than
     guessing by registration order;
  4. retains the legacy live markers (`CLAUDE_CODE_SESSION_ID`/`CLAUDECODE` →
     claude; `CODEX_THREAD_ID` → codex); and
  5. never treats `CODEX_HOME` as a live session signal.
  All eight canonical harness identities resolve through both generic-ID routes.
- **S2 — delegation, no second copy.** `scripts/implementation_authorization.py`
  `_worker_harness_selector` now delegates to the registry implementation,
  removing the duplicate behavioral copy so the two operational consumers
  cannot drift.
- **S3 — full-registry and two-consumer regression coverage.** Added focused
  tests to both declared test targets covering all-eight-identity resolution,
  conflict/unknown fail-closed, explicit-name and poller precedence, legacy
  markers, and CODEX_HOME non-selection.
- No source file outside the four declared targets was changed; no dispatcher,
  TAFE, MemBase, credential, Git, or external-system mutation.

## Implementation Start Evidence

- Exact work-intent claim: row `36428`, session
  `G-2026-08-03T15-24-47Z`, acquired `2026-08-03T17:59:xxZ`,
  `claim_kind=go_implementation`, `latest_bridge_status=GO`.
- Fresh schema-v3 packet:
  `sha256:7e11fa30daf22406cf85ebaeec7557c03fb58f5ee22ec77e5141c6872f6604e7`.
- `implementation_packet_create=allowed`; finalized
  `implementation_start=allowed`.
- Project authorization:
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2.
- Target classification: 2 source (`bridge_work_intent_registry.py`,
  `implementation_authorization.py`) + 2 test.
- Controlling GO: `bridge/gtkb-wi5841-harness-selector-registry-derived-006.md`.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
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
The registry-derived design is expressly approved by proposal v005 and GO v006.
No AUQ is requested.

## Prior Deliberations

- `bridge/gtkb-wi5841-harness-selector-registry-derived-005.md` - approved
  implementation proposal carried forward.
- `bridge/gtkb-wi5841-harness-selector-registry-derived-006.md` - Loyal
  Opposition GO verdict authorizing implementation.
- `DELIB-202667719`, `DELIB-202667724`, `DELIB-202667732` - project-authority
  and exact re-observation provenance.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | All eight durable IDs resolve to canonical names via both generic-ID routes |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Identity SoT read via canonical `read_identity`; no direct JSON read |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Registry-derived mapping; adding a harness needs no new selector branch |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Envelope provenance remains the only role authority |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Selector only narrows document lookup; never supplies role |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Identity SoT read fresh via canonical reader |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Fresh packet PAUTH allowed for both operations |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No bridge/GO/claim/start bypass |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Active PAUTH + project + member WI + exact targets recorded |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only chain v005 proposal → v006 GO → this v007 report |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal v005 carries Specification Links; carried forward |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Executed focused pytest + ruff evidence recorded below |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Change scoped to four declared targets |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | No hard-coded timer / no dispatcher mutation |
| `GOV-WORK-TREE-HYGIENE-001` | Only four declared targets changed |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Legacy markers + CODEX_THREAD_ID + GTKB_HARNESS_NAME behavior preserved |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Defect, correction, tests, report durable |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All targets inside mandatory GT-KB root |

## Commands Run

- `python -m pytest platform_tests/scripts/test_implementation_authorization_harness_selector.py -q --tb=line`
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=line`
- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=line`
- `python -m ruff check scripts/bridge_work_intent_registry.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization_harness_selector.py`
- `python -m ruff format --check <four targets>`
- `git --no-optional-locks status --short <four targets>`

## Observed Results

- `test_implementation_authorization_harness_selector.py`: **11 passed** (6
  existing + 5 new WI-5841 tests).
- `test_bridge_work_intent_registry.py`: **48 passed** (44 existing + 4 new
  WI-5841 tests). One timing-sensitive deadline test
  (`test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim`)
  is flaky under full-suite load but passes in isolation; it is unrelated to
  this change.
- `test_implementation_authorization.py`: **163 passed**.
- `ruff check`: **All checks passed!**
- `ruff format --check`: **4 files already formatted**.
- `git diff --stat`: only the four declared targets changed
  (218 insertions / 17 deletions); no whole-file line-ending noise.

## Files Changed

- `scripts/bridge_work_intent_registry.py` (S1 registry-derived selector +
  durable-id mapper)
- `scripts/implementation_authorization.py` (S2 delegation; removed unused
  `os` import)
- `platform_tests/scripts/test_bridge_work_intent_registry.py` (S3: 4 new tests)
- `platform_tests/scripts/test_implementation_authorization_harness_selector.py`
  (S3: 5 new tests)

Excluded out-of-scope dirty paths: 155.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: adds registry-derived harness selection across both
  operational consumers and their focused regression coverage.

```text
 scripts/bridge_work_intent_registry.py                      |  63 +++
 scripts/implementation_authorization.py                     |  25 +-
 platform_tests/scripts/test_bridge_work_intent_registry.py  |  86 +++
 platform_tests/scripts/test_implementation_authorization_harness_selector.py | 61 +++
```

## Acceptance Criteria Status

- [x] S1: registry-derived selector with explicit-name, poller, durable-id
      mapping, legacy-marker, and no-signal precedence; fail-closed on
      conflict/unknown/non-unique/unavailable/malformed.
- [x] S2: implementation-authorization consumer delegates to the single
      registry selector; no second behavioral copy.
- [x] S3: full-registry (all eight) and two-consumer regression coverage.
- [x] CODEX_HOME alone selects no harness; CODEX_THREAD_ID still selects Codex.
- [x] Session-envelope provenance remains the only role authority; no
      dispatcher/TAFE/foreign/quarantined rewrite.

## Risk And Rollback

Rollback is a focused revert of the four-path cohort. The delegation unifies
selector behavior, so both consumers cannot drift; existing legacy-marker and
explicit-name behavior is preserved (non-impairment verified by the 222-test
combined run). Residual risk is the pre-existing timing-flaky deadline tests,
unrelated to this change. Bridge history remains append-only; no governance or
TAFE state is rewritten.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed
   command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved
   proposal, otherwise return NO-GO with findings.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
