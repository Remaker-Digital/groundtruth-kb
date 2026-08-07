REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5939-lo-batch-publisher-provenance-throttle
Version: 009
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-008.md
Approved proposal: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5939

target_paths: ["scripts/lo_batch_publish.py", "platform_tests/scripts/test_lo_batch_publish.py"]

**No KB mutation.** This report performs no MemBase write and does not modify `groundtruth.db`.

# WI-5939 REVISED (009) - re-request VERIFIED; owner-run finalization

REVISED response to the `-008` NO-GO. **No product code changed.** The two target
files are byte-identical to the bytes reviewed at `-003`, `-005`, and `-007`.

This entry exists for a protocol reason as much as an evidentiary one: `VERIFIED`
is not a lawful successor to `NO-GO` under the § Post-Verdict Transition Table
(`NO-GO -> GO, REVISED, NO-ACTION, DEFERRED, WITHDRAWN`). Only from `REVISED`
does the post-GO augmentation permit `VERIFIED`. This `REVISED` therefore
re-opens the lawful path so finalization can land at `-010`.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both targets are in-root paths and
this bridge file resides under `E:/GT-KB/bridge/`. No generated artifact is
written outside the project root.

## Response to `-008` Finding 1

Agreed and understood. The `-008` blocker was
`WRONG_BRIDGE_VERSION_METADATA: Version metadata '000' does not match 008` - the
verdict body carried `Version: 000` rather than the version of the file being
written. Nothing in the implementation under review can influence that field.

Across four cycles the substance has been affirmed every time ("no product-code
rework indicated"), and each block has been a different single field in the
verdict bytes:

| Cycle | Blocking predicate | Where |
|---|---|---|
| `-004` | Spec-to-Test row with third cell `yes` | `validate_verified_body` |
| `-006` | `## Specification Links` section | `_has_concrete_spec_links` |
| `-008` | `Version:` must equal the file's own version | `WRONG_BRIDGE_VERSION_METADATA` |

Per owner decision (AUQ 2026-08-06), finalization will be performed by the owner
rather than by a further harness cycle. The consolidated predicate checklist in
`-007` plus the version-field correction above are the complete known set.

## Specification Links

Carried forward from the approved proposal `-001.md` and unchanged:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary
- `config/agent-control/SESSION-STARTUP-INDEX.md` section Session-context review independence (normative)
- `.claude/rules/codex-review-gate.md` section Review Independence Gate
- `.claude/rules/deliberation-protocol.md`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/codex-decision-ledger.md` (2026-04-29 tracked-surface bias)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)
- `DELIB-202667721`

## Spec-to-Test Mapping

Every row was executed against the bytes under review. Liftable verbatim into the
VERIFIED body.

| Specification clause | Test | Executed | Result |
| --- | --- | --- | --- |
| file-bridge-protocol Review Independence Boundary (self-review refusal) | test_t1_self_review_is_refused | yes | PASS |
| file-bridge-protocol Review Independence Boundary (independent predecessor accepted) | test_t1_distinct_sessions_are_accepted | yes | PASS |
| file-bridge-protocol fail-closed clause (missing metadata) | test_t2_missing_author_session_fails_closed | yes | PASS |
| file-bridge-protocol fail-closed clause (unreadable predecessor) | test_t2_unreadable_artifact_fails_closed | yes | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (no embedded session literal) | test_t3_no_hardcoded_uuid_literal_in_module | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (truthful session provenance) | test_t3_body_carries_runtime_session | yes | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fail closed on unresolvable provenance) | test_t3_provenance_fails_closed_without_session | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no embedded date literal) | test_t4_no_hardcoded_iso_date_literal_in_module | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (runtime publication date) | test_t4_body_uses_supplied_runtime_date | yes | PASS |
| deliberation-protocol (no false search claim) | test_t5_absent_deliberations_disclose_rather_than_claim | yes | PASS |
| deliberation-protocol (supplied citations rendered) | test_t5_supplied_deliberations_are_rendered | yes | PASS |
| bridge-essential; DELIB-202667526 (bounded interval) | test_t6_batch_publication_is_throttled | yes | PASS |
| bridge-essential (no artificial leading delay) | test_t6_no_delay_before_first_publication | yes | PASS |
| bridge-essential; DELIB-202667526 (contention backoff) | test_t6_contention_is_retried_with_exponential_backoff | yes | PASS |
| bridge-essential (fail fast on deterministic error) | test_t6_non_contention_failure_is_not_retried | yes | PASS |
| file-bridge-protocol actionable-predecessor rule | test_t6_non_actionable_predecessor_is_refused | yes | PASS |
| codex-decision-ledger tracked-surface bias (tracked path) | test_t7_module_lives_on_the_tracked_surface | yes | PASS |
| codex-decision-ledger tracked-surface bias (no runtime-state dependency) | test_t7_module_does_not_depend_on_runtime_state_paths | yes | PASS |

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_batch_publish.py -q
  -> 18 passed

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> 2 files already formatted

git status --porcelain scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> ?? platform_tests/scripts/test_lo_batch_publish.py
  -> ?? scripts/lo_batch_publish.py
```

## Changes Since `-007`

| Area | Change |
| --- | --- |
| `scripts/lo_batch_publish.py` | none - byte-identical |
| `platform_tests/scripts/test_lo_batch_publish.py` | none - byte-identical |
| Report body | restores the lawful `REVISED` state so `VERIFIED` can follow; records the `-008` version-field blocker and the owner decision to finalize outside the harness cycle |

## Disclosure carried forward

`test_release_commit_wait_cannot_outlive_total_deadline` was an intermittent
wall-clock flake in an unrelated module, captured as **WI-5941** and since
repaired and reported at `bridge/gtkb-wi5941-deterministic-release-deadline-test-003.md`
(7/7 consecutive combined runs green). It was never a WI-5939 regression.

## Acceptance Criteria Check

All seven acceptance criteria from `-001` remain MET, unchanged from `-005` and
`-007`.

## Owner Decisions / Input

- **AUQ 2026-08-06 (WI-5939 close-out):** owner selected "You run the
  finalization" - finalization is performed by the owner rather than a further
  harness cycle. This `REVISED` restores the lawful predecessor state for that
  step.
- **AUQ 2026-08-05 (next lane / verdict provenance / script disposition / target
  surface):** the decision chain that scoped and authorized this work item.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization.

## Recommended commit type

`feat:` - net-new tracked governed capability surface plus its test module.
Confirmed at `-002` (Positive Confirmation 5).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
