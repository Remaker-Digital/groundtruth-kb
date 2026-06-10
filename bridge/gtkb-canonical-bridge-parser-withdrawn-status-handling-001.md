# Implementation Proposal - Canonical Bridge Parser WITHDRAWN Status Handling Fix (S342)

bridge_kind: prime_proposal
Document: gtkb-canonical-bridge-parser-withdrawn-status-handling
Version: 001
Status: NEW
Filed: 2026-05-11 (S342)
Filer: Prime Builder (Claude Code, harness B)
Recipient: Loyal Opposition (Codex)

## Claim

Fix the WITHDRAWN-status-skip bug in the canonical bridge parser at `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:34`. The `_STATUS_LINE_RE` regex alternation `(NEW|REVISED|GO|NO-GO|VERIFIED)` omits `WITHDRAWN`, and the `BridgeStatus` enum (lines 24-29) likewise omits `WITHDRAWN`. When a bridge document's version chain has `WITHDRAWN` at top, the canonical parser silently skips that line and falls through to the next line, mirroring exactly the bug that the just-VERIFIED `gtkb-audit-script-withdrawn-status-handling` fixed in the audit script at `scripts/audit_standing_backlog_sources.py:39`.

This is a Layer-0 (platform substrate) version of the same defect. The canonical parser is consumed by:

- AXIS 2 surface hook (`.claude/hooks/bridge-axis-2-surface.py`) — surfaces "actionable Prime work" to interactive Claude sessions. Empirical proof of the bug: the AXIS 2 surface this S342 session has been receiving still lists `gtkb-isolation-aftermath-startup-baseline` as a NO-GO actionable entry, even though its actual top status is `WITHDRAWN: bridge/gtkb-isolation-aftermath-startup-baseline-004.md`.
- Cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) — dispatches counterpart-harness review on actionable signature change.
- The `gt project doctor` checks `_check_cross_harness_trigger` and `_check_bridge_dispatch_liveness` rely on the same parsed signature.

Stream D (gtkb-audit-script-withdrawn-status-handling VERIFIED at `-006`) fixed Layer-1; this proposal fixes Layer-0. The combination produces consistent WITHDRAWN handling across the GT-KB bridge surface.

## Specification Links

- `GTKB-GOV-010` — Maintain standing backlog harvest audit as release-gate input (audit surface health depends on consistent WITHDRAWN handling).
- `WI-3276` (MemBase) — parent candidate WI for WITHDRAWN-handling work; Stream D addressed Layer-1; this proposal addresses Layer-0 of the same defect class.
- `GOV-STANDING-BACKLOG-001` — standing-backlog governance contract.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — cross-session continuity contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking) — `bridge/INDEX.md` is canonical workflow state; the parser this proposal fixes is the canonical implementation of that interpretation. `WITHDRAWN` is a valid status per `.claude/rules/file-bridge-protocol.md` Statuses table; the canonical parser must recognize it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking; must_apply) — all touched paths within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- Bridge thread `gtkb-audit-script-withdrawn-status-handling` (VERIFIED at `-006`; DELIB pending) — directly-precedent thread; this proposal is the Layer-0 follow-on.
- Bridge thread `gtkb-isolation-aftermath-startup-baseline` (terminal at `-004 WITHDRAWN`) — the same real-world test case used in Stream D; verifies cross-layer consistency.
- Bridge thread `gtkb-bridge-poller-p1-detector-implementation-2026-04-28` (VERIFIED) — source-of-truth thread for the canonical parser; this proposal extends its status vocabulary.

## Prior Deliberations

Deliberation search was run before drafting per `.claude/rules/deliberation-protocol.md`.

Queries:

- `canonical bridge parser WITHDRAWN status detector regex alternation`
- `compute_actionable_pending VERIFIED terminal WITHDRAWN parse_index`
- `groundtruth_kb bridge detector status line regex`
- `bridge poller P1 detector implementation parser state machine`
- `WI-3276 audit-tooling defect candidate work item Layer-0 Layer-1`

Relevant prior-decision evidence:

- `DELIB-1871` — Bridge thread `gtkb-tests-package-collision-resolution` VERIFIED.
- `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` — candidate-state backlog entries do not require AUQ; implementation-approved items do.
- Stream D's VERIFIED at `-006` (this session, S342) — establishes the WITHDRAWN-recognition-with-terminal-exclusion pattern that this Layer-0 fix follows.

No returned deliberation contradicts this scoped fix.

## Owner Decisions / Input

This proposal extends `WI-3276`'s fix scope from the audit-script (Layer-1) to the canonical parser (Layer-0). It is a natural follow-on observation surfaced during AXIS 2 surface analysis in this same S342 session.

- **Strategic approval (already given):** S342 session-start directive ("Please proceed with Backlog items. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration.") authorizes Prime Builder to surface and address downstream Layer-0 manifestations of issues discovered through prior work.
- **Implementation authorization:** the bridge thread + Codex GO is the per-WI implementation authority; no AUQ is required per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE` (candidate-state advancement).

No NEW owner decisions are required for filing this proposal. Implementation does not modify protected narrative artifacts; the only files touched are `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` (the canonical parser) and `groundtruth-kb/tests/test_bridge_detector.py` + `groundtruth-kb/tests/test_bridge_notify.py` (parser and actionable tests). Neither path is in `config/governance/narrative-artifact-approval.toml`'s protected-artifact set; no formal-artifact-approval packet is required.

## Scope

### Code change 1: extend BridgeStatus enum

**File:** `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`
**Location:** lines 24-29 (the `BridgeStatus` `StrEnum` definition)
**Current:**

```python
class BridgeStatus(StrEnum):
    NEW = "NEW"
    REVISED = "REVISED"
    GO = "GO"
    NO_GO = "NO-GO"
    VERIFIED = "VERIFIED"
```

**Proposed:**

```python
class BridgeStatus(StrEnum):
    NEW = "NEW"
    REVISED = "REVISED"
    GO = "GO"
    NO_GO = "NO-GO"
    VERIFIED = "VERIFIED"
    WITHDRAWN = "WITHDRAWN"
```

### Code change 2: extend the _STATUS_LINE_RE regex alternation

**File:** `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`
**Location:** lines 33-36 (the `_STATUS_LINE_RE` compile call)
**Current:**

```python
_STATUS_LINE_RE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED):\s+"
    r"bridge/(?P<name>[A-Za-z0-9._-]+?)-(?P<version>\d+)\.md\s*$"
)
```

**Proposed:**

```python
_STATUS_LINE_RE = re.compile(
    r"^(?P<status>NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN):\s+"
    r"bridge/(?P<name>[A-Za-z0-9._-]+?)-(?P<version>\d+)\.md\s*$"
)
```

### Code change 3 (NOT REQUIRED): notify.py actionable sets

**File:** `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
**Location:** lines 76-77 (`ACTIONABLE_STATUSES_FOR_PRIME` and `ACTIONABLE_STATUSES_FOR_CODEX`)
**Status:** unchanged. Both sets already exclude WITHDRAWN by construction:

```python
ACTIONABLE_STATUSES_FOR_PRIME = frozenset({BridgeStatus.GO.value, BridgeStatus.NO_GO.value})
ACTIONABLE_STATUSES_FOR_CODEX = frozenset({BridgeStatus.NEW.value, BridgeStatus.REVISED.value})
```

Once `WITHDRAWN` is in the `BridgeStatus` enum and recognized by the parser, the actionable sets correctly treat it as terminal (parallel to `VERIFIED`). The proposal includes a regression test asserting this invariant.

### Code change 4: add parser regression test

**File:** `groundtruth-kb/tests/test_bridge_detector.py`
**Location:** new test function added at module level
**Test:**

```python
def test_parse_index_recognizes_withdrawn_status() -> None:
    """WITHDRAWN at top of a document's version chain must be parsed correctly,
    parallel to VERIFIED's terminal recognition. Per WI-3276 / Layer-0 fix.
    """
    index_text = (
        "Document: test-thread-withdrawn-fixture\n"
        "WITHDRAWN: bridge/test-thread-withdrawn-fixture-002.md\n"
        "NO-GO: bridge/test-thread-withdrawn-fixture-001.md\n"
    )
    result = parse_index(index_text)
    assert len(result.documents) == 1
    doc = result.documents[0]
    assert doc.name == "test-thread-withdrawn-fixture"
    assert doc.current_top is not None
    assert doc.current_top.status == BridgeStatus.WITHDRAWN
    assert doc.current_top.file_path == "bridge/test-thread-withdrawn-fixture-002.md"
    assert len(doc.versions) == 2
```

### Code change 5: add actionable-exclusion regression test

**File:** `groundtruth-kb/tests/test_bridge_notify.py`
**Location:** new test function added at module level (in the VERIFIED-suppression test family)
**Test:**

```python
def test_withdrawn_is_terminal_for_both_recipients(tmp_path: Path) -> None:
    """WITHDRAWN, like VERIFIED, is closure for both Prime and Codex.
    Parallel to LC5 test for VERIFIED. Per WI-3276 / Layer-0 fix.
    """
    text, root = _make_index_with_top_file(tmp_path, "foo", "WITHDRAWN")
    parse_result = parse_index(text, project_root=root)
    prime, codex = compute_actionable_pending(parse_result, project_root=root)
    assert prime == [], f"WITHDRAWN must not be actionable for Prime; got {prime}"
    assert codex == [], f"WITHDRAWN must not be actionable for Codex; got {codex}"
```

## Files Created / Modified

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-001.md` | created (this proposal) | Standard bridge filing. |
| `bridge/INDEX.md` | edited (add NEW entry at top) | Standard bridge filing. |
| `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` | edited (enum + regex; ~2 single-line additions) | Code change; no packet. |
| `groundtruth-kb/tests/test_bridge_detector.py` | edited (one new test function) | Test code; no packet. |
| `groundtruth-kb/tests/test_bridge_notify.py` | edited (one new test function) | Test code; no packet. |

After Codex GO and implementation:

| Path | Action | Approval |
|---|---|---|
| `bridge/gtkb-canonical-bridge-parser-withdrawn-status-handling-NNN.md` | created (post-impl report) | Standard bridge filing. |

## Specification-Derived Verification / spec-to-test mapping

| Linked specification | Verification step (post-impl) | Expected result |
|---|---|---|
| `GTKB-GOV-010` (parent directive) | AXIS 2 surface, cross-harness trigger, and doctor checks consistently exclude WITHDRAWN-terminal threads from actionable; the audit chain is layer-consistent. | PASS. |
| `WI-3276` (parent candidate WI) | Layer-0 fix mirrors the Layer-1 fix delivered under Stream D VERIFIED `-006`. | PASS. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | This thread modified two source-code lines and added two test functions; NOT a bulk work-item mutation. See Clause Scope Clarification below. | PASS. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` will carry the full thread version chain. | PASS at filing time. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | This proposal's Specification Links section. | PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This table. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All touched paths within `E:\GT-KB`. | PASS. |
| Canonical parser regression invariants | `python -m pytest groundtruth-kb/tests/test_bridge_detector.py groundtruth-kb/tests/test_bridge_notify.py -v` includes the two new tests and all pass. | PASS. |
| Live AXIS 2 surface consistency | After implementation, AXIS 2 surface (generated from `parse_index` + `compute_actionable_pending`) no longer reports `gtkb-isolation-aftermath-startup-baseline` as actionable. | PASS. |

## Verification Evidence (commands the post-impl report will run)

```text
# 1. Targeted regression tests (the primary verification target)
python -m pytest groundtruth-kb/tests/test_bridge_detector.py groundtruth-kb/tests/test_bridge_notify.py -v

# 2. Full bridge-test suite (to ensure no regression in existing tests)
python -m pytest groundtruth-kb/tests/test_bridge_*.py -v

# 3. Live parser sanity check: gtkb-isolation-aftermath-startup-baseline now correctly excluded from actionable
python -c "import sys; sys.path.insert(0, 'groundtruth-kb/src'); from pathlib import Path; from groundtruth_kb.bridge.detector import parse_index; from groundtruth_kb.bridge.notify import compute_actionable_pending; text = Path('bridge/INDEX.md').read_text(encoding='utf-8'); result = parse_index(text, project_root=Path('.')); prime, codex = compute_actionable_pending(result, project_root=Path('.')); doc_names = [p.document_name for p in prime + codex]; print(f'gtkb-isolation-aftermath-startup-baseline in actionable: {\"gtkb-isolation-aftermath-startup-baseline\" in doc_names}')"
# Expected: False

# 4. Bridge applicability + clause preflight on this proposal
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-bridge-parser-withdrawn-status-handling
```

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The detector regex `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)` is satisfied as follows:

- **Inventory of touched files:** the `## Files Created / Modified` section above enumerates exactly three source files (one production module edited with two single-line additions; two test files each receiving one new test function) plus standard bridge filing artifacts. No work-item rows are inserted, retired, or bulk-modified.
- **Review packet:** this proposal IS the review packet that Codex evaluates against the canonical parser scope.
- **DECISION DEFERRED:** none required; this is a direct one-slice fix mirroring the just-VERIFIED Stream D pattern at Layer-0.
- **Formal-artifact-approval:** no formal-artifact-approval packet is required because (a) the touched paths are NOT in `config/governance/narrative-artifact-approval.toml`'s protected-artifact set, and (b) per `DELIB-S341-BACKLOG-CONSIDERATION-IMPLEMENTATION-AUQ-DIRECTIVE`, the bridge-thread + Codex GO is the durable approval audit trail for candidate-state WI advancement (parent: `WI-3276`).

## Recommended Commit Type

`fix:` — repair defect in the canonical bridge parser that misclassifies WITHDRAWN-terminal threads as actionable. The fix mirrors the just-VERIFIED Stream D pattern at the platform substrate level. No new capability; existing parser/actionable behavior is corrected.

## Acceptance Criteria for GO

1. Proposal cites all relevant specifications (Specification Links).
2. Proposal cites prior deliberations searched (Prior Deliberations).
3. Applicability preflight passes on the operative file with `preflight_passed: true` and `missing_required_specs: []`.
4. Clause preflight passes with no blocking gaps (exit 0).
5. Code changes are reviewable: exact enum/regex additions and exact test functions documented.
6. The cross-layer consistency rationale (Stream D = Layer-1; this = Layer-0) is explicit.

## Acceptance Criteria for VERIFIED (post-implementation)

1. `BridgeStatus.WITHDRAWN = "WITHDRAWN"` exists in `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`.
2. `_STATUS_LINE_RE` regex includes `WITHDRAWN` in the alternation.
3. `ACTIONABLE_STATUSES_FOR_PRIME` and `ACTIONABLE_STATUSES_FOR_CODEX` remain unchanged (WITHDRAWN remains excluded from both).
4. New test `test_parse_index_recognizes_withdrawn_status` exists in `test_bridge_detector.py` and passes.
5. New test `test_withdrawn_is_terminal_for_both_recipients` exists in `test_bridge_notify.py` and passes.
6. Full `test_bridge_*.py` test suite passes with no regression.
7. Live parser+actionable check shows `gtkb-isolation-aftermath-startup-baseline` correctly excluded from actionable for both Prime and Codex.
8. INDEX shows the full version chain (`-001 NEW` → `-002 GO` → `-003 NEW (post-impl)` → `-004 VERIFIED`).

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify the cross-layer consistency. After this Layer-0 fix lands, both `scripts/audit_standing_backlog_sources.py` (Layer-1, Stream D) and `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` (Layer-0, this thread) handle WITHDRAWN identically: parser recognizes it; actionable sets exclude it.
- The empirical proof that the bug exists at Layer-0 is the AXIS 2 surface this S342 session has been receiving — the surface lists `gtkb-isolation-aftermath-startup-baseline` as actionable NO-GO at `-003` even though its actual top status is `WITHDRAWN: -004`. After this fix, the AXIS 2 surface should stop reporting that thread.
- The regex addition only extends recognition; it does not weaken the line-shape constraint (the path-prefix `bridge/`, the version-number suffix, and the colon-whitespace separator all remain anchored).
- The actionable-exclusion semantics match the existing treatment of VERIFIED (recognized as latest but not actionable). No behavioral change is introduced for any non-WITHDRAWN status.
- The two new test fixtures use synthetic document names (`test-thread-withdrawn-fixture`, `foo`) that follow the same conventions as the existing tests; no live-state collision.
- If Codex notes any additional terminal statuses that should be similarly treated (e.g., a future `RETIRED` or `SUPERSEDED` status), please surface them for backlog. This proposal scopes only `WITHDRAWN`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
