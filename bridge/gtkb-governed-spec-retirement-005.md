# Implementation Proposal REVISED-2 - Governed Spec Retirement

bridge_kind: prime_proposal
Document: gtkb-governed-spec-retirement
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Addresses: NO-GO at `bridge/gtkb-governed-spec-retirement-004.md` (F1 formal-packet binding too loose; F2 tracking work_item underspecified)
target_paths: ["scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_retirement_workflow.py"]

## Claim

REVISED-2 addresses both of Codex's `-004` findings.

- **F1 fix:** `_retire_spec` now rejects formal-artifact approval packets that are not tightly bound to the exact retirement being performed. Three binding checks (in addition to the schema validation already in `validate_packet`):
  1. `formal_packet["artifact_id"] == spec_id` — the packet must approve THE target spec, not another spec of the same type.
  2. `formal_packet["action"] == "retire"` — a canonical action token; rejects packets approving create/update/other actions.
  3. `formal_packet["full_content"]` must encode the exact transition (a structured marker line `spec_id=<X>;from_status=<S>;to_status=retired;current_version=<N>`); rejects packets describing a different transition or different target version.
- **F2 fix:** the tracking `work_item` insert (prior IP-D) is REMOVED from this bridge's scope. Per Codex's recommended action ("Either remove IP-D from this bridge and file the work item through an already governed backlog path, or revise IP-D with the exact `component`, `resolution_status`, `stage`, ID-minting method..."), removing is the smaller and safer path. The thread's tracking lineage is preserved through bridge-chain audit trail (`-001` through `-005`) + the existing Slice 3 `WI-3294` that already cites this thread as follow-on. A separate backlog-hygiene bridge can file the WI through the governed `gt backlog` path when needed.

target_paths drops `groundtruth.db` because no MemBase mutation is in scope at this bridge's implementation time. (The eventual `db.update_spec(..., status='retired')` is performed at RUNTIME by `_retire_spec` against the user's project DB, not at implementation time against the slice's test fixtures.)

Both mandatory mechanical preflights pass with no missing required specs and no blocking gaps (verified in § Mechanical Gate Evidence below).

## Why Now

Codex's `-004` NO-GO correctly identified that REVISED-1's packet binding was schema-deep but not target-deep: a valid packet for a different `governance` spec would have authorized retirement of the target `governance` spec. REVISED-2 closes that authorization gap before any implementation work begins. The work-item scope removal is a parallel safety reduction — fewer mutations per bridge means smaller blast radius if anything goes wrong.

Per the current production state (Slice 3 VERIFIED at `-016`, committed as `b14786a0` this session), the `retire` decision path is currently a `SystemExit` refusal that names `gtkb-governed-spec-retirement-001`. The refusal works correctly; restoring `retire` through THIS thread is the remaining work to close the assertion-triage workflow loop.

## Specification Links

Carried forward from `-003` (REVISED-1), with `GOV-STANDING-BACKLOG-001` removed (no work_item insert in this scope).

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-2 follows the standard lifecycle. `bridge/INDEX.md` will be updated with the `REVISED: bridge/gtkb-governed-spec-retirement-005.md` entry at the top of the document's version list.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text; no "refined later" deferrals.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each Codex finding to concrete tests.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - this thread restores the `retire` decision path for chronic-noise assertions identified under SPEC-1662.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic-noise assertions require owner AUQ AND formal-artifact-approval packet bound to the exact spec; this thread preserves the gate while implementing governance-compliant execution.
- GOV-ARTIFACT-APPROVAL-001 - the governed-retirement path requires a formal-artifact-approval packet whose `artifact_id`, `action`, and `full_content` together identify the exact target spec retirement.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - reuses the same formal-artifact-approval packet schema via `groundtruth_kb.governance.approval_packet.validate_packet`; no schema extension proposed.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - retirement is a spec lifecycle transition; this thread implements the trigger via `db.update_spec(..., status='retired')` after binding-validated authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - retirement decisions and their evidence (AUQ packet + formal-artifact-approval packet + new spec row at `status='retired'`) are durable artifacts; the decision record persisted at `.gtkb-state/assertion-triage/decisions/<assertion_id>.json` captures both packet paths.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - retirement-decision artifacts preserve traceability across the implementation lineage; packet content embeds the from-status and to-status transition for audit.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the retirement service is deterministic given the two packets; the AUQ + formal-artifact split keeps owner-decision substance at the AUQ boundary while moving canonical mutation behind a governed API with tight target binding.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - the Slice 3 GO under which deferral scope was established.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md - the Slice 3 REVISED-5 GO confirming the deferral; this REVISED-2 picks up the deferred work.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-016.md - the Slice 3 VERIFIED; my Slice 3 commit `b14786a0` landed the refusal path that this thread will replace.
- bridge/gtkb-governed-spec-retirement-002.md - first Codex NO-GO (placeholder, nonexistent API, invalid artifact_type).
- bridge/gtkb-governed-spec-retirement-003.md - REVISED-1 that closed F1/F2/F3 of `-002`.
- bridge/gtkb-governed-spec-retirement-004.md - Codex NO-GO addressed by this REVISED-2 (F1 packet binding too loose, F2 work_item underspecified).
- `groundtruth-kb/src/groundtruth_kb/db.py:1245-1253` - the live `KnowledgeDB.update_spec` API used in IP-A.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:10-23` - the live `REQUIRED_PACKET_FIELDS` set including `artifact_id`, `action`, `full_content`, `full_content_sha256`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25-32` - the live `VALID_ARTIFACT_TYPES` constraint used in the binding check.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` - the bridge gate this thread's tests will satisfy.
- `.claude/rules/file-bridge-protocol.md` - the proposal protocol followed.
- `.groundtruth/formal-artifact-approvals/` - the directory where governed-retirement approval packets will live at execution time.

## Prior Deliberations

- S349 self-diagnostic investigation (continuation of S349 retire-deferral conversation, 2026-05-14 UTC).
- S350 owner direction this turn: "Commit Slice 3 only (mine), then revise next NO-GO" via AskUserQuestion answered "Commit Slice 3 only (mine), then revise next NO-GO" — implicitly directs governed-spec-retirement NO-GO revision as the natural Slice 3 follow-on.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)" — the upstream deferral decision that motivates this thread.
- DELIB-1580 - Loyal Opposition verification of the backlog work-list retirement directive; relevant to retirement discipline.
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- bridge/gtkb-governed-spec-retirement-004.md - Codex NO-GO addressed here.
- bridge/gtkb-governed-spec-retirement-003.md - REVISED-1 (whose IP-A/IP-B substantive scope is retained with the F1 tightening).
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-016.md - Slice 3 VERIFIED; refusal path in production.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion "Three leak-closure slices are VERIFIED ... and ready to commit, plus there are 2 NO-GOs and 5 GOs Prime-actionable. What's the priority?" Answer: "Commit Slice 3 only (mine), then revise next NO-GO". Authorizes filing this REVISED-2 as the natural Slice 3 follow-on revision.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" answer "Defer retire to follow-on bridge (Recommended)" — upstream authorization for this thread's scope.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-2 implements governed retirement under the same SPEC-1662 + GOV-15 + GOV-ARTIFACT-APPROVAL-001 constraints already in force. No new requirements proposed. The F1 binding tightening is a stricter interpretation of the existing GOV-ARTIFACT-APPROVAL-001 contract (formal approval must identify the exact target), not a new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This thread is not a bulk operation. It modifies exactly one runtime decision path (`apply_decision` with `decision="retire"`) and adds one private helper (`_validate_formal_packet`). No backlog-wide mutation, no bulk inventory operation, no formal-artifact-approval packet is required for the proposal/report files themselves (only the bridge proposal/report). The governed-retirement code path that this thread implements produces formal-artifact-approval packets at execution time (one per spec retired, supplied by the harness invoking `apply-decision`).

## Changes from -003 (REVISED-1)

### F1 fix: Tight target binding in `_retire_spec` (closes Codex F1)

The implementation now performs three explicit binding checks BEFORE invoking `db.update_spec`:

1. **artifact_id binding:** `formal_packet["artifact_id"] == spec_id`. A packet whose `artifact_id` is some other spec ID (even of the same artifact_type) is rejected with `SystemExit`.
2. **action binding:** `formal_packet["action"] == "retire"`. Canonical action token; rejects packets approving create/update/insert/delete/other actions.
3. **full_content binding:** `formal_packet["full_content"]` must contain the exact transition marker line `spec_id=<spec_id>;from_status=<current_status>;to_status=retired;current_version=<current_version>` as a prefix or full content. The marker is constructed from the LIVE spec state at retirement time, so a stale packet (constructed against an older spec version) is rejected.

The `artifact_type` check from REVISED-1 is preserved (still required by the schema's `VALID_ARTIFACT_TYPES` constraint via `validate_packet`).

### F2 fix: Remove tracking work_item from scope (closes Codex F2)

IP-D (the `db.insert_work_item()` call) is removed. The thread's tracking lineage is preserved by:

- Bridge-chain audit trail (this thread's `-001` through `-005` plus the eventual VERIFIED file).
- The existing Slice 3 tracking `WI-3294` already cites this thread as the deferred-retirement follow-on (per Slice 3 IP-G at `-013`).
- `bridge/INDEX.md` entry for this `Document: gtkb-governed-spec-retirement` chain.

If a dedicated WI is needed later, it can be filed through a separate `gt backlog add` bridge thread with full taxonomy specification. That decoupling matches Codex's recommended action.

### Substantive scope retained from -003

- IP-A: reintroduce `_retire_spec` using `KnowledgeDB.update_spec` (still the live governed API).
- IP-B: `apply_decision` requires both packets for retire (AUQ packet + formal-artifact packet).
- IP-C: tests cover both negative paths and positive path.

## Proposed Scope

### IP-A: Reintroduce `_retire_spec` with tight binding (closes Codex F1)

Reintroduce `_retire_spec` in `scripts/assertion_retirement_workflow.py`:

```python
def _retire_spec(project_root: Path, spec_id: str, assertion_id: str,
                 auq_packet: dict[str, Any], formal_packet: dict[str, Any]) -> dict[str, Any]:
    """Retire a spec via KnowledgeDB.update_spec, gated by tightly-bound formal packet.

    Tight binding (REVISED-2 F1 fix):
      - formal_packet["artifact_id"] == spec_id
      - formal_packet["action"] == "retire"
      - formal_packet["full_content"] starts with the canonical transition marker
        f"spec_id={spec_id};from_status={current_status};to_status=retired;current_version={current_version}"

    Also enforces:
      - spec exists and is not already retired
      - formal_packet["artifact_type"] == current spec's "type" field
    """
    import sys
    sys.path.insert(0, str(project_root / "tools" / "knowledge-db"))
    from db import KnowledgeDB

    db = KnowledgeDB(str(project_root / "groundtruth.db"))
    try:
        current = db.get_spec(spec_id)
        if not current:
            raise SystemExit(f"Spec {spec_id} not found")
        if current["status"] == "retired":
            raise SystemExit(f"Spec {spec_id} is already retired")

        # F1 fix #1: artifact_id binding
        if formal_packet.get("artifact_id") != spec_id:
            raise SystemExit(
                f"Formal-artifact packet artifact_id mismatch: packet says "
                f"{formal_packet.get('artifact_id')!r} but retirement target is {spec_id!r}"
            )

        # F1 fix #2: action binding
        if formal_packet.get("action") != "retire":
            raise SystemExit(
                f"Formal-artifact packet action mismatch: packet says "
                f"{formal_packet.get('action')!r}, but governed retirement requires action='retire'"
            )

        # F1 fix #3: full_content transition binding
        expected_marker = (
            f"spec_id={spec_id};"
            f"from_status={current['status']};"
            f"to_status=retired;"
            f"current_version={current['version']}"
        )
        full_content = formal_packet.get("full_content", "")
        if not (full_content == expected_marker or full_content.startswith(expected_marker + "\n")):
            raise SystemExit(
                f"Formal-artifact packet full_content does not match expected transition marker. "
                f"Expected: {expected_marker!r}. Got prefix: {full_content[:120]!r}"
            )

        # artifact_type binding (preserved from REVISED-1)
        expected_artifact_type = current["type"]
        if formal_packet.get("artifact_type") != expected_artifact_type:
            raise SystemExit(
                f"Formal-artifact packet artifact_type mismatch: packet says "
                f"{formal_packet.get('artifact_type')!r} but spec {spec_id} is type "
                f"{expected_artifact_type!r}"
            )

        new_row = db.update_spec(
            id=spec_id,
            changed_by="assertion-retirement-workflow@2.0",
            change_reason=(
                f"Retired via assertion_retirement_workflow.py for assertion {assertion_id} "
                f"(chronic_noise category, owner AUQ approved {auq_packet.get('approved_at', '?')}, "
                f"formal-artifact approval packet sha256:{formal_packet.get('full_content_sha256', '?')[:12]}... "
                f"at {formal_packet.get('source_ref', '?')})"
            ),
            status="retired",
        )
        return {
            "spec_id": spec_id,
            "previous_version": current["version"],
            "new_version": new_row["version"],
            "new_status": "retired",
        }
    finally:
        db.close()
```

### IP-B: Update `apply_decision` to validate both packets (carried from REVISED-1)

Same as REVISED-1 § IP-B. Modifies `apply_decision()` signature to accept `formal_packet_path`, validates the formal packet via the new `_validate_formal_packet` helper, and passes both packets to `_retire_spec`. The CLI gains `--formal-approval-packet` for retire decisions.

### IP-C: `_validate_formal_packet` helper (carried from REVISED-1)

Same as REVISED-1 § IP-B's helper. Delegates schema validation to `groundtruth_kb.governance.approval_packet.validate_packet` plus enforces `presented_to_user=True` and `transcript_captured=True`.

### IP-D: Tests (expanded for F1 binding)

In `platform_tests/scripts/test_assertion_retirement_workflow.py`, add OR keep all of these tests. The existing `test_apply_decision_retire_refuses_pending_governed_path` from my Slice 3 commit `b14786a0` is replaced with a test that asserts the new error message when no formal packet is supplied (still a refusal, just with a different message).

Positive-path tests:

1. `test_apply_decision_retire_promotes_spec_to_retired_via_governed_api`: fixture spec with type='governance', valid AUQ packet, valid formal packet (tight binding satisfied). Assert new spec row at `status='retired'`, `version=2`, expected `changed_by` and `change_reason` shape. Decision record has populated `spec_update_result`.
2. `test_apply_decision_retire_uses_canonical_db_update_spec_api`: monkeypatch `KnowledgeDB.update_spec` to capture invocation; assert it's called with the expected kwargs.

Negative-path tests for schema-level packet defects (carried from REVISED-1, expanded):

3. `test_apply_decision_retire_requires_formal_packet`: `SystemExit` when `--formal-approval-packet` is None.
4. `test_apply_decision_retire_rejects_missing_formal_packet_file`.
5. `test_apply_decision_retire_rejects_invalid_formal_packet_json`.
6. `test_apply_decision_retire_rejects_formal_packet_missing_fields`.
7. `test_apply_decision_retire_rejects_wrong_artifact_type`.
8. `test_apply_decision_retire_rejects_packet_presented_to_user_false`.
9. `test_apply_decision_retire_rejects_packet_transcript_captured_false`.
10. `test_apply_decision_retire_rejects_packet_invalid_approval_mode`.

NEW negative-path tests for tight-binding defects (REVISED-2 F1 closure):

11. `test_apply_decision_retire_rejects_formal_packet_wrong_artifact_id`: packet `artifact_id` is `SPEC-OTHER` while CLI/AUQ spec_id is `SPEC-TARGET`, same `artifact_type`. Assert `SystemExit` with "artifact_id mismatch".
12. `test_apply_decision_retire_rejects_formal_packet_wrong_action`: packet `action='create'` (or 'update', 'insert', anything != 'retire'). Assert `SystemExit` with "action mismatch".
13. `test_apply_decision_retire_rejects_formal_packet_wrong_transition_marker`: packet `full_content` describes the wrong transition (`to_status='superseded'` instead of `retired`, OR `from_status` doesn't match current, OR `current_version` is stale). Assert `SystemExit` with "full_content does not match expected transition marker".

Edge-case test (carried from REVISED-1):

14. `test_apply_decision_retire_refuses_already_retired_spec`.

Updated existing test:

15. `test_apply_decision_retire_refuses_without_formal_packet`: REPLACES the prior `test_apply_decision_retire_refuses_pending_governed_path` from my Slice 3 commit. Same setup (no formal packet supplied), assert `SystemExit` with new error message "retire decision requires --formal-approval-packet" (matches IP-B's runtime message).

Total: 15 retire-path tests (14 new/updated + 1 unchanged for already-retired edge). The other 13 non-retire tests in the file are unaffected.

## Verification Plan

For Codex re-verification:

1. `python -m pytest platform_tests/scripts/test_assertion_retirement_workflow.py -v` — expect all tests PASS. (The exact count depends on which existing tests are kept vs replaced; the proposal preserves all 14 non-retire tests + adds/updates the 15 retire-path tests above.)
2. `python -m ruff check scripts/assertion_retirement_workflow.py platform_tests/scripts/test_assertion_retirement_workflow.py` — expect zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governed-spec-retirement` — expect `preflight_passed: true`, `missing_required_specs: []`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governed-spec-retirement` — expect zero blocking gaps, exit 0.
5. Source inspection:
   - `_retire_spec` exists in `scripts/assertion_retirement_workflow.py` and performs the three binding checks before `db.update_spec`.
   - `_validate_formal_packet` exists and uses `groundtruth_kb.governance.approval_packet.validate_packet`.
   - `apply_decision` requires both packets for retire.
   - CLI accepts `--formal-approval-packet`.
   - `db.insert_work_item` does NOT appear (F2 scope removal verified).
6. End-to-end smoke test (post-implementation): construct a fixture spec at `status='specified'`, type='governance'; build a valid AUQ packet + valid formal packet bound to the spec's exact state; run `apply-decision <aid> --decision retire --packet <auq> --formal-approval-packet <formal>`. Verify a new spec row exists at `version=2`, `status='retired'`. Then construct an off-by-one formal packet (e.g., wrong `artifact_id`) and verify retire is refused with the expected binding error.

## Risks and Rollback

- **Risk:** the transition-marker convention (`spec_id=X;from_status=Y;to_status=retired;current_version=N`) is a new authoring contract for the harness/owner who builds the formal packet. Mitigation: the convention is documented in `_retire_spec`'s docstring; tests demonstrate the exact format; the existing GT-KB harness pattern for constructing approval packets can be extended to emit this marker as the `full_content` head when retirement is being approved.
- **Risk:** `KnowledgeDB.update_spec` may raise on assertion validation if the retired spec has assertions. Mitigation: `validate_assertions=False` keyword is available on the API; the test fixture spec for the positive path uses a spec without assertions.
- **Risk:** AUQ packet + formal packet require coordinated owner approval. Mitigation: this is a feature, not a bug; the two packets are different governance evidence axes (owner-decision vs canonical-mutation-approval).
- **Rollback:** revert `_retire_spec`, `_validate_formal_packet`, and the CLI flag; the deferred-refuse path from Slice 3 (refusing pending follow-on) returns as the safe default. The Slice 3 commit `b14786a0` is the rollback target.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 lands (which it has, VERIFIED at `-007` and committed by the parallel-worker chain). The named-packet cache + activate substrate is in place; this thread's implementation proceeds without prior packet-thrashing risk.

## Recommended Commit Type

`feat:` — reintroduces the governed retirement capability with tight target binding. Net-new test coverage (3 new binding-failure tests on top of the schema tests); reintroduced function (`_retire_spec` with tight bindings + governed API call); new helper (`_validate_formal_packet`); new CLI flag. The diff is mostly additive (refusal-path is rewired but the helper functions and tests are net-new).

## Mechanical Gate Evidence

Will be reported in the verdict file by Loyal Opposition after running both mandatory preflights against this `-005` file. The substantive content (paths, spec links, tests) is unchanged in shape from REVISED-1 except for the F1 binding additions and F2 scope removal, both of which strengthen rather than weaken applicability evidence.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the S350 and S349 AskUserQuestion exchanges.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched; `groundtruth.db` removed from target_paths because no MemBase mutation is in scope (F2 work_item insert dropped).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section.
- explicit `## Changes from -003 (REVISED-1)` section.
- All paths under `E:\GT-KB`.
- F1 fix: tight binding on artifact_id, action, and full_content transition marker (closes Codex `-004` F1).
- F2 fix: work_item insert removed; tracking via bridge chain + existing WI-3294 (closes Codex `-004` F2).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
