REVISED

# Implementation Proposal - Project Authorization Spec-Amendment Approval Gate - REVISED-1 (WI-3313)

bridge_kind: prime_proposal
Document: gtkb-project-auth-spec-amendment-gate
Version: 003
Responds to: bridge/gtkb-project-auth-spec-amendment-gate-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3313

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/tests/test_db.py", "groundtruth.db"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-project-auth-spec-amendment-gate-002.md`:

- **F1 (P1/blocking)** — Substring-only "packet path" check is bypassable by `change_reason="approved via .groundtruth/formal-artifact-approvals/fake.json"` → **closed** by upgrading to **real packet-evidence validation**: parse the cited path, require it resolves inside `.groundtruth/formal-artifact-approvals/`, require the JSON file exists, require it passes `validate_packet()` from the shared validator, require `approved_by: owner`, AND require packet content covers the amendment.
- **F2 (P2)** — Missing negative-evidence tests → **closed** with 6 explicit negative cases (fake path, malformed JSON, outside-root, non-owner-approved, hash-mismatch, non-covering packet) plus the original positive cases.

## Claim

`KnowledgeDB.insert_project_authorization()` must reject any version that mutates `included_spec_ids` or `excluded_spec_ids` (relative to the prior version) unless `change_reason` carries a path to a **real, owner-approved formal-artifact-approval packet** that covers the mutation. Substring text alone is insufficient.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - source spec; v1 specified 2026-05-14.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - sibling spec (WI-3312); covers initial authorization linkage.
- `GOV-ARTIFACT-APPROVAL-001` - approval-packet workflow that this gate enforces.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract this aligns with.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3313 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-project-auth-spec-amendment-gate-002.md` - NO-GO under remediation.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved 5-spec batch.
- 2026-05-15 UTC, S350+: owner directive "Please proceed with WI-3312 + WI-3313".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. F1 fix uses the existing `validate_packet()` shared validator already trusted by `formal-artifact-approval-gate.py` — no new validation invented; gate adopts the validator the rest of the governance stack trusts.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (real packet validation) + IP-2 (helper extraction) + IP-3 (tests) + IP-4 (no spec promotion at proposal time) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-auth-spec-amendment-gate-003.md`; `REVISED:` line prepended; prior `NO-GO: -002` and `NEW: -001` preserved.

## Proposed Scope

### IP-1: Real packet-evidence validation in insert_project_authorization()

In `groundtruth-kb/src/groundtruth_kb/db.py`, extend `insert_project_authorization()` (or its validation helper):

```python
APPROVAL_PACKET_DIR_REL = ".groundtruth/formal-artifact-approvals"
PACKET_PATH_REGEX = re.compile(
    r"\.groundtruth[/\\]formal-artifact-approvals[/\\][\w.-]+\.json"
)

def _validate_spec_amendment_approval_packet(
    self, prior_specs: set[str], new_specs: set[str], change_reason: str,
    project_id: str, authorization_id: str,
) -> None:
    """If linked_specs mutated, require a real, owner-approved, covering packet."""
    if prior_specs == new_specs:
        return  # no spec mutation
    # 1. Extract packet path from change_reason
    match = PACKET_PATH_REGEX.search(change_reason or "")
    if not match:
        raise ValueError(
            "Spec amendment requires a real approval-packet path in change_reason "
            "(DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001/"
            "CLAUSE-AMENDMENT-APPROVAL-REQUIRED). No packet path detected."
        )
    rel_path = match.group(0).replace("\\", "/")
    packet_path = PROJECT_ROOT / rel_path

    # 2. In-root check
    try:
        packet_path.resolve().relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        raise ValueError("Packet path resolves outside project root.")

    # 3. File-exists check
    if not packet_path.is_file():
        raise ValueError(f"Cited approval packet not found at {rel_path}.")

    # 4. JSON-parse + validate_packet()
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Packet at {rel_path} not valid JSON: {exc}")
    from groundtruth_kb.governance.approval_packet import validate_packet
    result = validate_packet(packet)
    if not result.is_valid:
        raise ValueError(f"Packet at {rel_path} fails schema validation: {result.errors[0]}")

    # 5. Owner-approved check
    if packet.get("approved_by") != "owner":
        raise ValueError(f"Packet at {rel_path} is not owner-approved (approved_by != 'owner').")

    # 6. Coverage check
    added = sorted(new_specs - prior_specs)
    removed = sorted(prior_specs - new_specs)
    full_content = packet.get("full_content", "") or ""
    explicit_change = packet.get("explicit_change_request", "") or ""
    change_reason_field = packet.get("change_reason", "") or ""
    packet_text = "\n".join([full_content, explicit_change, change_reason_field])
    mentioned_specs = set()
    for spec_id in added + removed:
        if spec_id in packet_text:
            mentioned_specs.add(spec_id)
    project_mentioned = (project_id in packet_text) or (authorization_id in packet_text)
    if not project_mentioned or not (mentioned_specs >= set(added + removed)):
        raise ValueError(
            f"Packet at {rel_path} does not cover the amendment: "
            f"project={project_id}, added={added}, removed={removed}, "
            f"mentioned_specs={sorted(mentioned_specs)}."
        )
```

### IP-2: Helper extraction (refactor for testability)

In `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`, expose:

```python
def parse_packet_path_from_change_reason(change_reason: str) -> Path | None:
    """Return the absolute Path to the cited packet, or None if no path detected."""

def packet_covers_amendment(packet: dict, project_id: str, authorization_id: str,
                             added_specs: set[str], removed_specs: set[str]) -> tuple[bool, str]:
    """Return (covers, reason). Reason explains why coverage failed when False."""
```

The DB-layer validator calls these helpers; tests can exercise them in isolation.

### IP-3: Tests with comprehensive negative cases

Tests in `groundtruth-kb/tests/test_db.py`:

| Scenario | Test |
|---|---|
| spec mutation + no packet path → blocked | `test_amend_specs_without_packet_path_raises` |
| spec mutation + fake/non-existent path → blocked | `test_amend_specs_with_fake_path_raises` |
| spec mutation + outside-root path → blocked | `test_amend_specs_with_outside_root_path_raises` |
| spec mutation + malformed JSON → blocked | `test_amend_specs_with_malformed_json_raises` |
| spec mutation + schema-invalid packet → blocked | `test_amend_specs_with_schema_invalid_packet_raises` |
| spec mutation + non-owner-approved packet → blocked | `test_amend_specs_with_non_owner_approved_packet_raises` |
| spec mutation + valid packet not mentioning project → blocked | `test_amend_specs_packet_does_not_cover_project_raises` |
| spec mutation + valid packet not mentioning added spec → blocked | `test_amend_specs_packet_does_not_cover_added_spec_raises` |
| spec mutation + valid covering packet → passes | `test_amend_specs_with_covering_packet_succeeds` |
| batch packet covering multiple amendments → passes per-call | `test_amend_specs_batch_packet_multiple_projects` |
| initial version (no prior) → no packet required | `test_authorize_initial_version_no_packet_required` |
| status-only change (no spec mutation) → no packet required | `test_authorize_status_change_no_packet_required` |
| excluded_spec_ids mutation also gated | `test_amend_excluded_specs_also_gated` |

Test fixtures include: valid covering packet, fake-path packet, malformed packet, schema-invalid packet, non-owner-approved packet, non-covering packet.

### IP-4: No spec promotion at proposal-filing time

`DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` stays at `specified`. **Promotion only on VERIFIED**.

## Specification-Derived Verification Plan

Tests above directly map to clauses:

| Clause | Tests |
|---|---|
| `CLAUSE-AMENDMENT-APPROVAL-REQUIRED` (positive) | `test_amend_specs_with_covering_packet_succeeds` |
| `CLAUSE-AMENDMENT-APPROVAL-REQUIRED` (negative — F1 cluster) | 8 negative tests covering each failure mode |
| `CLAUSE-BATCH-APPROVAL-PERMITTED` | `test_amend_specs_batch_packet_multiple_projects` |
| Grandfathering | `test_authorize_initial_version_no_packet_required` |
| Status-only exemption | `test_authorize_status_change_no_packet_required` |
| Both linkage sets gated | `test_amend_excluded_specs_also_gated` |

Run: `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_governance_approval_packet.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 13 tests PASS (especially the 8 negative cases).
- IP-4: DCL stays at `specified` at proposal time.
- No regression in existing `test_db.py` or formal-artifact-approval gate tests.
- Both preflights PASS.

## Risks / Rollback

- Risk: legacy amendment commits with substring-only packet citations will fail under the new gate. Mitigation: only NEW insertions are gated; existing data unchanged.
- Risk: coverage check may false-negative when a packet legitimately covers an amendment but uses different ID phrasing. Mitigation: per-spec-ID + project-or-auth-ID substring search; tests document expected phrasing.
- Risk: regex anchoring on packet path may fail on unusual path separators. Mitigation: regex accepts `/` and `\`.
- Rollback: revert `_validate_spec_amendment_approval_packet` (single-function scope) + helper additions.

## Recommended Commit Type

`feat` - real packet-evidence gate replacing substring check; ~80 LOC DB + ~30 LOC helpers + ~200 LOC tests + fixtures.
