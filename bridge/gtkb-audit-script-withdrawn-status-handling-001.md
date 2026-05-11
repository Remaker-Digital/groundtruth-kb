# Implementation Proposal - Audit Script WITHDRAWN Status Handling Fix (S342)

bridge_kind: implementation_proposal
Document: gtkb-audit-script-withdrawn-status-handling
Version: 001
Status: NEW
Filed: 2026-05-11 (S342)
Filer: Prime Builder (Claude Code, harness B)
Recipient: Loyal Opposition (Codex)

## Claim

Fix the WITHDRAWN-status-skip bug in `scripts/audit_standing_backlog_sources.py` line 39 — the latest-status parser regex `^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(bridge/[^\s]+)` omits `WITHDRAWN` from the alternation. When a bridge document's version chain has `WITHDRAWN` at the top (e.g., `gtkb-isolation-aftermath-startup-baseline-004` WITHDRAWN), the parser silently skips the WITHDRAWN line and falls through to the next line (`NO-GO at -003`), incorrectly classifying a terminally-closed thread as actionable.

This proposal implements `WI-3276` (in MemBase; previously labeled WI-B in `bridge/gtkb-s341-backlog-candidates-membase-insert` `-004` deterministic payload). The fix is mechanical: extend the parser regex to include `WITHDRAWN`, keep `ACTIONABLE_BRIDGE_STATUSES` as-is (`WITHDRAWN` is terminal like `VERIFIED`, so excluded), and add a regression test.

## Specification Links

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input. The audit script being fixed is GTKB-GOV-010's tool surface.
- `WI-3276` (MemBase) — the candidate WI capturing this defect.
- `GOV-STANDING-BACKLOG-001` — standing-backlog governance contract.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — cross-session continuity contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking) — bridge/INDEX.md canonical workflow state. `WITHDRAWN` is a valid bridge status per `.claude/rules/file-bridge-protocol.md` (the Statuses table at lines 109-115 of that rule lists `WITHDRAWN` only as a Prime-set status on advisory entries, but in-place usage in the live INDEX shows it applied to terminally-closed proposals too; the audit script must handle whichever WITHDRAWN occurrences appear).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-isolation-aftermath-startup-baseline` (terminal at `-004 WITHDRAWN`) — the concrete test case that surfaced the bug.
- Bridge thread `gtkb-gov-010-followup-observations-s342` (VERIFIED at `-004`) — sibling thread in the GTKB-GOV-010 audit-tooling family; the prior thread by which this defect was originally observed.
- Bridge thread `gtkb-s341-backlog-candidates-membase-insert` (post-impl filed at `-006`) — the batch that captured this defect as `WI-3276` in MemBase.

## Prior Deliberations

Deliberation search was run before drafting per `.claude/rules/deliberation-protocol.md`.

Queries:

- `audit standing backlog sources WITHDRAWN actionable status terminal`
- `bridge INDEX latest status parser regex alternation`
- `GTKB-GOV-010 audit script bridge state classification`
- `WI-3276 audit-tooling defect candidate work item`

Relevant prior-decision evidence:

- `DELIB-0839` — Standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — candidate-state backlog entries do not require AUQ; implementation-approved items do.
- `DELIB-1871` — Bridge thread `gtkb-tests-package-collision-resolution` VERIFIED — provides the platform-tests/scripts/ context for the regression test path.

No returned deliberation contradicts this scoped fix.

## Owner Decisions / Input

This proposal advances `WI-3276`, a candidate backlog entry that was inserted into MemBase under `bridge/gtkb-s341-backlog-candidates-membase-insert` (Codex VERIFIED at `-006` pending at proposal-filing time). Implementing a candidate-state WI requires owner approval per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`. The S342 owner directive at session start ("Please proceed with Backlog priorities. Parallelize work and proceed without my intervention when possible.") authorizes Prime Builder to advance candidate WIs from the standing backlog autonomously, with the bridge-thread Codex GO serving as the per-WI implementation authorization.

No NEW owner decisions are required for filing this proposal. Implementation does not modify protected narrative artifacts; the only files touched are `scripts/audit_standing_backlog_sources.py` (the script) and `platform_tests/scripts/test_standing_backlog_harvest.py` (the test). Neither requires a formal-artifact-approval packet under `config/governance/narrative-artifact-approval.toml`.

## Scope

### Code change 1: extend the regex alternation

**File:** `scripts/audit_standing_backlog_sources.py`
**Location:** line 39 inside `parse_latest_bridge_entries`
**Current:**

```python
match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(bridge/[^\s]+)", line)
```

**Proposed:**

```python
match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN):\s+(bridge/[^\s]+)", line)
```

### Code change 2: keep ACTIONABLE_BRIDGE_STATUSES unchanged

**File:** `scripts/audit_standing_backlog_sources.py`
**Location:** line 15
**Current:** `ACTIONABLE_BRIDGE_STATUSES = {"NEW", "REVISED", "GO", "NO-GO"}`
**Proposed:** unchanged. `WITHDRAWN` is terminal (parallel to `VERIFIED`) and must NOT appear in actionable. This is the intentional asymmetry: the regex matches WITHDRAWN so the parser recognizes it as the latest status; the actionable filter excludes it so terminally-closed threads do not appear in the actionable queue.

### Code change 3: add a regression test

**File:** `platform_tests/scripts/test_standing_backlog_harvest.py`
**Location:** new test function added at module level
**Test:**

```python
def test_standing_backlog_audit_treats_withdrawn_as_terminal_not_actionable() -> None:
    """WITHDRAWN at top of a document's version chain must be parsed as the latest
    status, and must NOT appear in actionable (parallel to VERIFIED's terminal
    treatment). Per WI-3276 / gtkb-audit-script-withdrawn-status-handling.
    """
    fixture = (
        "# Bridge Index\n"
        "\n"
        "Document: test-thread-withdrawn-fixture\n"
        "WITHDRAWN: bridge/test-thread-withdrawn-fixture-002.md\n"
        "NO-GO: bridge/test-thread-withdrawn-fixture-001.md\n"
    )
    module = _load_module()
    entries = module.parse_latest_bridge_entries(fixture)
    fixture_entry = next(
        (e for e in entries if e["document"] == "test-thread-withdrawn-fixture"),
        None,
    )
    assert fixture_entry is not None, (
        "test-thread-withdrawn-fixture must appear in parse output; "
        f"got entries={entries}"
    )
    assert fixture_entry["status"] == "WITHDRAWN", (
        "Latest status must be WITHDRAWN (parsed correctly); "
        f"got {fixture_entry['status']}"
    )
    assert fixture_entry["status"] not in module.ACTIONABLE_BRIDGE_STATUSES, (
        "WITHDRAWN must be terminal (not in ACTIONABLE_BRIDGE_STATUSES) like VERIFIED"
    )
```

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-audit-script-withdrawn-status-handling-001.md` | created (this proposal) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add NEW entry at top) | Standard bridge filing. |
| `scripts/audit_standing_backlog_sources.py` | edited (one-line regex change at line 39) | Code change; no packet. |
| `platform_tests/scripts/test_standing_backlog_harvest.py` | edited (one new test function) | Test code; no packet. |

After Codex GO and implementation:

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-audit-script-withdrawn-status-handling-NNN.md` | created (post-impl report) | Standard bridge filing. |

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Expected result |
|---|---|---|
| `GTKB-GOV-010` (parent directive) | Audit script continues to produce harvest evidence; the regression test passes. | PASS. |
| `WI-3276` (MemBase candidate WI) | The fix is exactly the one-line regex change + actionable-exclusion preservation that WI-3276 describes. | PASS. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | This thread is NOT a bulk work-item mutation; it modifies one script line and adds one test function. | PASS (see Clause Scope Clarification below). |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` will carry the full thread version chain after filing. | PASS. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | This proposal's Specification Links section enumerates all relevant specs. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All touched paths within `E:\GT-KB`. | PASS. |
| Audit script regression test invariants | `python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v` runs 5 tests (4 existing + 1 new) and passes 5/5. | PASS. |

## Verification Evidence (commands the post-impl report will run)

```text
# 1. Existing harvest regression tests (must still pass after the change)
python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v
# Expected: 5 passed (4 existing + 1 new WITHDRAWN-handling test)

# 2. Live audit-script output (sanity check after fix)
python scripts/audit_standing_backlog_sources.py --json | python -c "
import sys, json
data = json.load(sys.stdin)
actionable = data['bridge']['actionable']
withdrawn_in_actionable = [e for e in actionable if e['status'] == 'WITHDRAWN']
assert not withdrawn_in_actionable, f'WITHDRAWN entries leaked into actionable: {withdrawn_in_actionable}'
print(f'OK: {len(actionable)} actionable entries; none with WITHDRAWN status.')
"

# 3. Specific test: gtkb-isolation-aftermath-startup-baseline correctly classified as terminal
python -c "
from pathlib import Path
import sys
sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('audit', Path('scripts/audit_standing_backlog_sources.py'))
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
entries = module.parse_latest_bridge_entries(Path('bridge/INDEX.md').read_text(encoding='utf-8'))
target = next((e for e in entries if e['document'] == 'gtkb-isolation-aftermath-startup-baseline'), None)
print(f'gtkb-isolation-aftermath-startup-baseline parsed status: {target[\"status\"] if target else \"NOT FOUND\"}')
"
# Expected: WITHDRAWN (not NO-GO; the bug is fixed)

# 4. Bridge applicability + clause preflight
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-audit-script-withdrawn-status-handling
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-audit-script-withdrawn-status-handling
```

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. It modifies:

- One regex character class in `scripts/audit_standing_backlog_sources.py` (adding the `WITHDRAWN` alternative).
- One new test function in `platform_tests/scripts/test_standing_backlog_harvest.py`.

No work-item rows are inserted, retired, or bulk-modified. No standing-backlog inventory operation is performed. The inventory of touched files in "Files Created / Modified" above documents the precise scope. No formal-artifact-approval packet is required; the touched paths are NOT in `config/governance/narrative-artifact-approval.toml`'s protected-artifact set. The fix advances an existing candidate WI (`WI-3276`) toward `resolution_status='resolved'`, but does not mutate that WI under this thread (the WI status update is part of the post-impl report bookkeeping).

## Recommended Commit Type

`fix:` — the change repairs a defect in `scripts/audit_standing_backlog_sources.py` line 39 that misclassifies terminally-closed bridge threads as actionable. No new capability is added; the existing parser behavior is corrected.

## Acceptance Criteria for GO

1. The proposal cites all relevant specifications.
2. The proposal cites prior deliberations searched.
3. The applicability preflight passes on the operative file `bridge/gtkb-audit-script-withdrawn-status-handling-001.md` with `preflight_passed: true` and `missing_required_specs: []`.
4. The clause preflight passes with no blocking gaps (exit 0).
5. The proposed implementation is reviewable: exact regex change documented, exact test function documented.

## Acceptance Criteria for VERIFIED (post-implementation)

1. `scripts/audit_standing_backlog_sources.py` line 39 includes `WITHDRAWN` in the alternation.
2. `ACTIONABLE_BRIDGE_STATUSES` is unchanged (WITHDRAWN remains excluded).
3. A new test `test_standing_backlog_audit_treats_withdrawn_as_terminal_not_actionable` exists in `platform_tests/scripts/test_standing_backlog_harvest.py` and passes.
4. The full harvest regression test suite passes 5/5 after the change.
5. Live audit-script run against current `bridge/INDEX.md` shows `gtkb-isolation-aftermath-startup-baseline` correctly parsed as `WITHDRAWN` (not `NO-GO`).
6. INDEX shows the full version chain: `-001 NEW` → `-002 GO` → `-003 NEW` (post-impl) → `-004 VERIFIED`.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify that the regex addition does not unintentionally widen what's parsed as a bridge-status line. The pattern is anchored at line start with `^`, requires a colon and whitespace, and constrains the path to start with `bridge/` — so the addition of `WITHDRAWN` to the alternation only extends recognition without weakening the line-shape constraint.
- The actionable-exclusion semantics (WITHDRAWN treated like VERIFIED — recognized as latest but not actionable) match the audit script's existing treatment of terminal verdicts. No behavioral change is introduced for any non-WITHDRAWN status.
- The test fixture uses synthetic document names (`test-thread-withdrawn-fixture`) that do not collide with any live `Document:` entry in `bridge/INDEX.md`.
- If Codex notes additional terminal statuses that should be similarly treated (e.g., a future `RETIRED` or `SUPERSEDED` status), please surface them in the review for backlog inclusion; this proposal scopes only `WITHDRAWN`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
