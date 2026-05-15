# Implementation Proposal REVISED-1 - Governed Spec Retirement

bridge_kind: implementation_proposal
Document: gtkb-governed-spec-retirement
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
Addresses: NO-GO at `bridge/gtkb-governed-spec-retirement-002.md` (F1 placeholder/non-implementable, F2 nonexistent API, F3 invalid artifact_type)
target_paths: ["scripts/assertion_retirement_workflow.py", "platform_tests/scripts/test_assertion_retirement_workflow.py", "groundtruth.db"]

## Claim

REVISED-1 replaces the placeholder filing at `-001` with a concrete implementable plan that addresses all three Codex `-002` findings:

- **F1 fix:** every "refined at REVISED-1" placeholder is replaced with explicit IP scope, exact API signature, exact packet field set, and full spec-to-test mapping (below). The proposal is now implementable as written.
- **F2 fix:** the implementation calls `KnowledgeDB.update_spec(id, changed_by, change_reason, *, status='retired')` (the live API at `groundtruth-kb/src/groundtruth_kb/db.py:1245-1253`), NOT the non-existent `db.update_specification()`. The carry-forward semantics (all unchanged fields preserved; new version inserted; assertions re-validated by default) are documented in the live docstring.
- **F3 fix:** the formal-artifact approval packet's `artifact_type` is **derived from the spec being retired**, NOT a new `spec_status_mutation` type. The implementation looks up `db.get_spec(spec_id)['type']` and uses that value (which is already constrained to one of `governance`, `protected_behavior`, `architecture_decision`, `design_constraint`, `requirement` per the live `VALID_ARTIFACT_TYPES` set in `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25-32`). No schema extension required.

The deferred-retire behavior from Slice 3 (the `apply_decision --decision retire` SystemExit) is REPLACED in this slice by a governed retirement path that requires BOTH the existing AUQ packet (for owner-decision evidence) AND a new formal-artifact-approval packet (for the canonical spec-mutation gate). The follow-on retirement message named in Slice 3 (`gtkb-governed-spec-retirement-001`) is satisfied by this REVISED-1 implementation; the slug carries forward unchanged.

## Why Now

Codex's `-002` NO-GO was correct: the `-001` filing was a tracking placeholder, not an implementable plan. With Slice 3 REVISED-5 GO'd at `-014` and its implementation report filed at `-015`, the deferred-retire refusal path is in production. Restoring governed retirement is the natural next step — assertion-triage workflows now have chronic-noise candidates surfaced via `review-candidates`, but `retire` decisions cannot complete until this thread lands.

## Specification Links

Carried forward from `-001` plus `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (Codex flagged as missing-advisory in `-002`).

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this REVISED-1 follows the standard lifecycle. `bridge/INDEX.md` will be updated with the `REVISED: bridge/gtkb-governed-spec-retirement-003.md` entry at the top of the document's version list.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text; no "refined later" deferrals.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each linked spec to a concrete test.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - this thread restores the `retire` decision path for chronic-noise assertions identified under SPEC-1662.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic-noise assertions require owner AUQ AND formal-artifact-approval packet; this thread preserves the gate while implementing governance-compliant execution.
- GOV-ARTIFACT-APPROVAL-001 - the governed-retirement path requires a formal-artifact-approval packet matching the spec's artifact_type; the implementation validates the packet via `groundtruth_kb.governance.approval_packet.validate_packet`.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - reuses the same formal-artifact-approval packet schema; no schema extension proposed.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - retirement is a spec lifecycle transition; this thread implements the trigger via `db.update_spec(..., status='retired')`.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - retirement decisions and their evidence (AUQ packet + formal-artifact-approval packet + new spec row at `status='retired'`) are durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - retirement-decision artifacts (packets, spec row, decision record) preserve traceability across the implementation lineage.
- GOV-STANDING-BACKLOG-001 - this thread creates one tracking WI for its own implementation.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the retirement service is deterministic given the two packets; the AUQ + formal-artifact split keeps owner-decision substance at the AUQ boundary while moving canonical mutation behind a governed API.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - the Slice 3 GO under which deferral scope was established.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-014.md - the Slice 3 REVISED-5 GO confirming the deferral; this REVISED-1 picks up the deferred work.
- bridge/gtkb-governed-spec-retirement-002.md - Codex NO-GO addressed by this REVISED-1.
- `groundtruth-kb/src/groundtruth_kb/db.py:1245-1253` - the live `KnowledgeDB.update_spec` API used in IP-1.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:25-32` - the live `VALID_ARTIFACT_TYPES` constraint used for F3.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` - the bridge gate this thread's tests will satisfy.
- `.claude/rules/file-bridge-protocol.md` - the proposal protocol followed.
- `.groundtruth/formal-artifact-approvals/` - the directory where governed-retirement approval packets will live at execution time.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable item should I pick up next?" answered "Revise governed-spec-retirement (Recommended)" - authorizes this REVISED-1 filing.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" Answer: "Defer retire to follow-on bridge (Recommended)" - the upstream deferral decision that motivates this thread.
- DELIB-1580 - Loyal Opposition verification of the backlog work-list retirement directive; relevant to retirement discipline.
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- bridge/gtkb-governed-spec-retirement-002.md - Codex NO-GO addressed here.
- bridge/gtkb-governed-spec-retirement-001.md - original placeholder filing.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-015.md - Slice 3 implementation report (current refusal path in production).

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable item should I pick up next?" answer "Revise governed-spec-retirement (Recommended)" - authorizes filing this REVISED-1.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "How should REVISED-1 of Slice 3 handle the `retire` mutation path (Codex F1)?" answer "Defer retire to follow-on bridge (Recommended)" - upstream authorization for this thread's scope.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

REVISED-1 implements governed retirement under the same SPEC-1662 + GOV-15 + GOV-ARTIFACT-APPROVAL-001 constraints already in force. No new requirements proposed.

## Clause Scope Clarification (Not a Bulk Operation)

This thread is not a bulk operation. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662') at IP-D, identical in shape to tracking WIs from prior slices. No formal-artifact-approval packet is required for the proposal/report files themselves; the governed-retirement code path that this thread implements produces ITS OWN formal-artifact-approval packets at execution time (one per spec retired).

## Proposed Scope

### IP-A: Reintroduce governed `_retire_spec` using `KnowledgeDB.update_spec`

Reintroduce the `_retire_spec` function in `scripts/assertion_retirement_workflow.py`, this time using the governed DB API:

```python
def _retire_spec(project_root: Path, spec_id: str, assertion_id: str,
                 auq_packet: dict[str, Any], formal_packet: dict[str, Any]) -> dict[str, Any]:
    """Retire a spec via the governed KnowledgeDB.update_spec path.

    Requires BOTH packets:
    - auq_packet: AskUserQuestion decision evidence (existing -007 schema).
    - formal_packet: formal-artifact-approval packet (validated against
      groundtruth_kb.governance.approval_packet.validate_packet); its
      artifact_type MUST equal the spec's current type (looked up live).
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
        # F3: artifact_type derived from spec's current type
        expected_artifact_type = current["type"]
        if formal_packet.get("artifact_type") != expected_artifact_type:
            raise SystemExit(
                f"Formal-artifact packet artifact_type mismatch: "
                f"packet says {formal_packet.get('artifact_type')!r} but spec {spec_id} "
                f"is type {expected_artifact_type!r}"
            )
        new_row = db.update_spec(
            id=spec_id,
            changed_by="assertion-retirement-workflow@2.0",
            change_reason=(
                f"Retired via assertion_retirement_workflow.py for assertion {assertion_id} "
                f"(chronic_noise category, owner AUQ approved {auq_packet.get('approved_at', '?')}, "
                f"formal-artifact approval packet sha256:{formal_packet.get('full_content_sha256', '?')[:12]}"
                f"... at {formal_packet.get('source_ref', '?')})"
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

### IP-B: Update `apply_decision` to validate both packets for retire

Modify `apply_decision()` in `scripts/assertion_retirement_workflow.py`:

```python
def apply_decision(project_root: Path, triage_dir: Path, assertion_id: str,
                   decision: str, auq_packet_path: Path,
                   formal_packet_path: Path | None = None) -> dict[str, Any]:
    if decision not in VALID_DECISIONS:
        raise SystemExit(f"Invalid decision: {decision!r}")
    auq_packet = _validate_packet(auq_packet_path)  # existing AUQ validation
    if auq_packet["assertion_id"] != assertion_id:
        raise SystemExit(f"AUQ packet assertion_id mismatch: ...")
    if auq_packet["decision"] != decision:
        raise SystemExit(f"AUQ packet decision mismatch: ...")
    records = _load_categories(triage_dir)
    target = next((r for r in records if r["assertion_id"] == assertion_id), None)
    if target is None:
        raise SystemExit(f"assertion_id not found: {assertion_id}")

    decisions_dir = triage_dir / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    decision_path = decisions_dir / f"{assertion_id}.json"
    spec_update_result = None
    formal_packet = None
    if decision == "retire":
        if formal_packet_path is None:
            raise SystemExit(
                "retire decision requires --formal-approval-packet pointing at a formal-artifact "
                "approval packet matching the spec's artifact_type"
            )
        formal_packet = _validate_formal_packet(formal_packet_path)  # new
        spec_update_result = _retire_spec(
            project_root, target["spec_id"], assertion_id, auq_packet, formal_packet
        )

    decision_record = {
        "assertion_id": assertion_id,
        "spec_id": target["spec_id"],
        "decision": decision,
        "auq_packet_path": str(auq_packet_path),
        "formal_packet_path": str(formal_packet_path) if formal_packet_path else None,
        "applied_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "category_at_decision": target.get("category"),
        "description": target["description"],
        "spec_update_result": spec_update_result,
    }
    decision_path.write_text(json.dumps(decision_record, indent=2, sort_keys=True), encoding="utf-8")
    return {"decision_path": str(decision_path), "decision": decision,
            "assertion_id": assertion_id, "spec_update_result": spec_update_result}
```

Plus a new `_validate_formal_packet(path) -> dict[str, Any]` helper:

```python
def _validate_formal_packet(packet_path: Path) -> dict[str, Any]:
    """Validate a formal-artifact approval packet using the shared schema validator."""
    if not packet_path.is_file():
        raise SystemExit(f"Formal-approval packet file not found: {packet_path}")
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Formal-approval packet is not valid JSON: {e}") from e
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "groundtruth-kb" / "src"))
    from groundtruth_kb.governance.approval_packet import validate_packet
    result = validate_packet(packet)
    if not result.is_valid:
        raise SystemExit("Formal-approval packet invalid: " + "; ".join(result.errors))
    if packet.get("presented_to_user") is not True:
        raise SystemExit("Formal-approval packet requires presented_to_user=true")
    if packet.get("transcript_captured") is not True:
        raise SystemExit("Formal-approval packet requires transcript_captured=true")
    return packet
```

CLI surface change (in `main()`):

```python
sub_apply.add_argument("--formal-approval-packet", help="Path to formal-artifact approval packet; required for retire")
```

### IP-C: Tests for the governed retirement path

Add to `platform_tests/scripts/test_assertion_retirement_workflow.py`:

1. `test_apply_decision_retire_requires_formal_packet`: assert `SystemExit` when `--formal-approval-packet` is None and decision is retire.
2. `test_apply_decision_retire_rejects_missing_formal_packet_file`: invalid path.
3. `test_apply_decision_retire_rejects_invalid_formal_packet_json`: malformed JSON.
4. `test_apply_decision_retire_rejects_formal_packet_missing_fields`: missing one of the REQUIRED_PACKET_FIELDS.
5. `test_apply_decision_retire_rejects_wrong_artifact_type`: packet `artifact_type='design_constraint'` but spec type is `'governance'`.
6. `test_apply_decision_retire_rejects_packet_presented_to_user_false`: packet has `presented_to_user=false`.
7. `test_apply_decision_retire_rejects_packet_transcript_captured_false`: packet has `transcript_captured=false`.
8. `test_apply_decision_retire_rejects_packet_invalid_approval_mode`: packet has `approval_mode='custom'`.
9. `test_apply_decision_retire_promotes_spec_to_retired_via_governed_api`: positive path. Fixture spec with type='governance' + valid AUQ + valid formal packet. Assert: new spec row written with `status='retired'`, `version=2`, `changed_by='assertion-retirement-workflow@2.0'`. Decision record has `spec_update_result` populated with the expected fields.
10. `test_apply_decision_retire_refuses_already_retired_spec`: spec already at `status='retired'`. Assert `SystemExit`.
11. `test_apply_decision_retire_uses_canonical_db_update_spec_api`: monkeypatch `KnowledgeDB.update_spec` to capture invocation; assert it was called with the expected kwargs (`status='retired'`, `changed_by` and `change_reason` matching documented format).

Plus update the existing `test_apply_decision_retire_refuses_pending_governed_path` test: since this slice REPLACES the deferral path, this test should be removed or refactored. Decision per Codex's verification preference: keep the refusal path enabled when no formal packet is supplied (which is the case in the existing test, since the existing test doesn't pass a formal packet). The existing test passes unchanged because IP-B says "retire decision requires --formal-approval-packet pointing at a formal-artifact approval packet matching the spec's artifact_type" — the existing test provides no formal packet, so retire still refuses (with a different message that names the missing flag rather than the gtkb-governed-spec-retirement-001 bridge). The existing test's assertion `"refusing retire"` will fail; this test is updated to assert the new error message `"retire decision requires --formal-approval-packet"`.

### IP-D: Tracking work_item

Insert one `work_items` row via `db.insert_work_item()`:

- id: `WI-NNNN` (next available; resolved at insert time)
- `origin='hygiene'`
- `source_spec_id='SPEC-1662'`
- `title='Governed spec retirement (deferred follow-on from Slice 3)'`
- `related_bridge_threads='gtkb-governed-spec-retirement'`
- `changed_by='prime-builder/claude/B'`
- `change_reason='S349 self-diagnostic LEAK 3 closure - governed retirement substrate; replaces deferred-refuse path with KnowledgeDB.update_spec + formal-artifact approval packet validation'`

## Tests

Per § IP-C above. Total: 11 new/updated tests covering:
- Negative paths (8): missing packet, missing file, invalid JSON, missing fields, wrong artifact_type, presented_to_user false, transcript_captured false, invalid approval_mode.
- Positive path (1): retire succeeds via governed API with valid packets.
- Edge case (1): already-retired spec.
- API contract (1): monkeypatch confirms `KnowledgeDB.update_spec` invocation shape.

## Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_assertion_retirement_workflow.py -v` - all existing 15 tests + 11 new tests PASS (26 total).
2. Source inspection:
   - `_retire_spec` exists in `scripts/assertion_retirement_workflow.py` and calls `KnowledgeDB.update_spec(..., status='retired')`.
   - `_validate_formal_packet` exists and uses `groundtruth_kb.governance.approval_packet.validate_packet`.
   - `apply_decision` requires both packets for retire.
   - CLI accepts `--formal-approval-packet`.
3. End-to-end smoke test (post-implementation): create a fixture spec at `status='specified'`; build a valid AUQ packet + valid formal packet; run `apply-decision <assertion_id> --decision retire --packet <auq> --formal-approval-packet <formal>`. Verify a new spec row exists at `version=2`, `status='retired'`.
4. Targeted Ruff on touched files clean.
5. Both mandatory bridge preflights pass with no missing required specs and zero blocking gaps.
6. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` - PASS (carried forward; no new glossary entries in this slice).

## Risks and Rollback

- **Risk:** `KnowledgeDB.update_spec` may raise on assertion validation if the retired spec has assertions. Mitigation: tests confirm a fixture spec with assertions retires cleanly; if not, pass `validate_assertions=False` (which the API supports via the `validate_assertions` keyword).
- **Risk:** the formal-artifact approval packet must be generated by the harness before `apply-decision` runs. The harness path for this is described in `GOV-ARTIFACT-APPROVAL-001`; this thread does not propose a new generation path; reusing the existing path is in scope.
- **Risk:** AUQ packet + formal packet require coordinated owner approval. Mitigation: this is a feature, not a bug; the two packets are different governance evidence axes (owner-decision vs canonical-mutation-approval).
- **Rollback:** revert `_retire_spec`, `_validate_formal_packet`, and the CLI flag; the deferred-refuse path from Slice 3 returns as the safe default.

## Sequenced Dependencies

This thread is sequenced AFTER Slice 4 lands (which it has, VERIFIED at `-007`). The named-packet cache + activate substrate is now in place; this thread's implementation proceeds without the prior packet-thrashing risk.

## Recommended Commit Type

`feat:` - reintroduces the governed retirement capability (replacing the Slice 3 refuse-path). Net-new test coverage (11 tests); net-new helper (`_validate_formal_packet`); reintroduced function (`_retire_spec` with governed API); new CLI flag.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with flat bullets; no `###` sub-headings inside; no parenthetical heading.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the two AskUserQuestion exchanges.
- `target_paths` consistent with all planned writes; no protected narrative artifacts touched.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type` present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` added to Specification Links (closes Codex's advisory-spec gap from `-002`).
- All paths under `E:\GT-KB`.
- No `refined at REVISED-1` or `placeholder` posture anywhere (closes Codex F1).
- API named is the live `KnowledgeDB.update_spec` (closes Codex F2).
- artifact_type derived from live spec's `type` field; uses existing VALID_ARTIFACT_TYPES set (closes Codex F3).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
