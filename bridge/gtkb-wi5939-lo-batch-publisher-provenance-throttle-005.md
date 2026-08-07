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
Version: 005
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-004.md
Approved proposal: bridge/gtkb-wi5939-lo-batch-publisher-provenance-throttle-001.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5939

target_paths: ["scripts/lo_batch_publish.py", "platform_tests/scripts/test_lo_batch_publish.py"]

# WI-5939 REVISED Implementation Report - re-request VERIFIED

REVISED response to the `-004` NO-GO. **No product code changed.** The `-004`
verdict states its own basis plainly: "Substantive evidence is green, but atomic
VERIFIED finalization failed closed," and "No product-code rework indicated from
the focused suite." The implementation bytes are byte-identical to those reviewed
at `-003`.

This revision does two things: it supplies the finalization evidence in the exact
shape the finalization helper requires, and it corrects the recorded root cause.

## Response to Finding 1 (P1) - atomic VERIFIED finalization failed closed

**Agreed that finalization failed. The recorded cause is incorrect, with
evidence.**

The `-004` recommended action attributes the failure to "governed publication
capability for untracked bridge predecessors." The traceback quoted in that same
finding attributes it elsewhere, and the code of record confirms the traceback:

`.claude/skills/gtkb-verify/helpers/write_verdict.py` `validate_verified_body()`
raises before any publication capability is requested. The gate at that function
requires the **VERIFIED verdict body** to contain a `## Spec-to-Test Mapping`
section with at least one table row whose third cell is literally `yes`:

```
mapping = _section_body(body, "Spec-to-Test Mapping")
if not re.search(r"\|\s*[^|\n]+\s*\|\s*[^|\n]+\s*\|\s*yes\s*\|\s*[^|\n]+\s*\|", mapping, re.IGNORECASE):
    raise VerifiedFinalizationError(
        "VERIFIED verdict body must include at least one executed Spec-to-Test Mapping row with Executed=yes."
    )
```

Three consequences follow:

1. The blocker is a **verdict-body format requirement**, evaluated on the
   reviewer's own VERIFIED body, before publication is attempted. It is not a
   publication-capability condition and not a property of the untracked
   predecessor script.
2. Nothing in the implementation under review can clear it. The `-003` report's
   mapping table used an `Executed`-less `| clause | test | result |` shape, so a
   reviewer lifting it into a verdict body would not satisfy the third-cell
   `yes` predicate.
3. The remedy is to supply the mapping in the required shape. That is done below,
   in a form that can be lifted verbatim into the VERIFIED body.

This friction class is already tracked and is **not** re-captured here: `WI-4674`
(enforce verification verdict structure and commit-type checks), `WI-4773`
(prevent invalid VERIFIED verdict finalization), `WI-5417` (reject helper-invalid
VERIFIED bodies in per-thread finalization repair), and `WI-5446` (LO harness
emitting governance-non-compliant verdicts). This report adds no duplicate
backlog row.

## Specification Links

Carried forward from the approved proposal `-001.md` and unchanged:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary
- `config/agent-control/SESSION-STARTUP-INDEX.md` section Session-context review independence (normative)
- `.claude/rules/codex-review-gate.md` section Review Independence Gate
- `.claude/rules/deliberation-protocol.md`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/codex-decision-ledger.md` (2026-04-29 tracked-surface bias)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; cited at `-004`)
- `DELIB-202667721`

## Spec-to-Test Mapping

Every row below was executed in this session against the implementation bytes
under review. This table is in the shape `validate_verified_body()` requires and
may be lifted verbatim into the VERIFIED verdict body.

| Specification clause | Test | Executed | Result |
| --- | --- | --- | --- |
| file-bridge-protocol Review Independence Boundary (self-review refusal) | test_t1_self_review_is_refused | yes | PASS |
| file-bridge-protocol Review Independence Boundary (independent predecessor accepted) | test_t1_distinct_sessions_are_accepted | yes | PASS |
| file-bridge-protocol fail-closed clause; codex-review-gate Review Independence Gate (missing metadata) | test_t2_missing_author_session_fails_closed | yes | PASS |
| file-bridge-protocol fail-closed clause (unreadable predecessor) | test_t2_unreadable_artifact_fails_closed | yes | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (no embedded session literal) | test_t3_no_hardcoded_uuid_literal_in_module | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (truthful session provenance in body) | test_t3_body_carries_runtime_session | yes | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (fail closed on unresolvable provenance) | test_t3_provenance_fails_closed_without_session | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (no embedded date literal) | test_t4_no_hardcoded_iso_date_literal_in_module | yes | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (runtime publication date) | test_t4_body_uses_supplied_runtime_date | yes | PASS |
| deliberation-protocol (no false search claim) | test_t5_absent_deliberations_disclose_rather_than_claim | yes | PASS |
| deliberation-protocol (supplied citations rendered) | test_t5_supplied_deliberations_are_rendered | yes | PASS |
| bridge-essential; DELIB-202667526 (bounded inter-publication interval) | test_t6_batch_publication_is_throttled | yes | PASS |
| bridge-essential (no artificial leading delay) | test_t6_no_delay_before_first_publication | yes | PASS |
| bridge-essential; DELIB-202667526 (contention backoff) | test_t6_contention_is_retried_with_exponential_backoff | yes | PASS |
| bridge-essential (fail fast on deterministic error) | test_t6_non_contention_failure_is_not_retried | yes | PASS |
| file-bridge-protocol actionable-predecessor rule | test_t6_non_actionable_predecessor_is_refused | yes | PASS |
| codex-decision-ledger tracked-surface bias (tracked path) | test_t7_module_lives_on_the_tracked_surface | yes | PASS |
| codex-decision-ledger tracked-surface bias (no runtime-state dependency) | test_t7_module_does_not_depend_on_runtime_state_paths | yes | PASS |

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_batch_publish.py -q
  -> 18 passed, 1 warning

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> 2 files already formatted

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_publication_finalization_atomicity.py platform_tests/scripts/test_bridge_work_intent_registry.py -q
  run 1 -> 1 failed, 57 passed, 2 skipped
  run 2 -> 58 passed, 2 skipped (identical command)

git status --porcelain scripts/lo_batch_publish.py platform_tests/scripts/test_lo_batch_publish.py
  -> ?? platform_tests/scripts/test_lo_batch_publish.py
  -> ?? scripts/lo_batch_publish.py
```

## Changes Since `-003`

| Area | Change |
|---|---|
| `scripts/lo_batch_publish.py` | none - byte-identical to the bytes reviewed at `-003` |
| `platform_tests/scripts/test_lo_batch_publish.py` | none - byte-identical |
| Report body | Spec-to-Test Mapping restated in the finalization-helper-required shape; `## Commands Executed` heading normalized to the exact required form; root cause of the `-004` finalization failure corrected with the code of record |

## Disclosure carried forward: intermittent regression flake

`test_release_commit_wait_cannot_outlive_total_deadline` failed on the first
combined regression run and passed on an identical re-run and in isolation. It is
a pre-existing wall-clock flake, independently captured as **WI-5941**, and not a
WI-5939 regression: the failing module does not import `lo_batch_publish`,
`scripts/bridge_work_intent_registry.py` is unmodified by this change, and the two
new files were not collected in that invocation. This is disclosed rather than
presented as green.

## Acceptance Criteria Check

| # | Criterion | Status |
|---|---|---|
| 1 | Module exists at the tracked path; no runtime-state path required | MET |
| 2 | No hardcoded session-id or date literal | MET |
| 3 | Independence computed; fails closed on equality or missing/unreadable metadata | MET |
| 4 | Body never asserts an unperformed deliberation search | MET |
| 5 | Multi-item publication serialized with bounded delay/backoff | MET |
| 6 | T1-T7 pass; ruff check and ruff format --check pass | MET |
| 7 | Existing publication regression suites pass | MET with the disclosed flake above (WI-5941) |

## Owner Decisions / Input

- **AUQ 2026-08-05 (next lane):** owner selected "P0: close the rogue-publish hole".
- **AUQ 2026-08-05 (verdict provenance):** owner selected "Genuine review; metadata
  is the bug" - no re-review of the already-published verdicts; correction deferred
  to WI-5940.
- **AUQ 2026-08-05 (script disposition):** owner initially selected "Fix provenance
  + throttle in place".
- **AUQ 2026-08-05 (target surface, superseding the preceding item):** after the
  PAUTH gate refused governed mutation of the runtime-state path, owner selected
  "Promote to tracked source" - the authority for the declared target paths.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization.

## Recommended commit type

`feat:` - introduces a net-new tracked governed capability surface
(`scripts/lo_batch_publish.py`) plus its test module. Confirmed at `-002`
(Positive Confirmation 5).

## Requested Next Step

Re-request VERIFIED. If the finalization helper rejects the verdict body again,
the rejection text and the failing predicate are the actionable evidence - please
quote them rather than restating the publication-capability hypothesis, since the
code of record shows `validate_verified_body()` runs before any capability is
requested.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
