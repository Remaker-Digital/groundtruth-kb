REVISED

# Bridge Proposal — GTKB Bridge-Propose Helper INDEX Parity (REVISED-1)

**Status:** REVISED (version 003)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-bridge-propose-helper-index-parity-2026-04-30`
**Reviewed prior version:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-002.md` (Codex NO-GO with F1, F2 — both architecturally substantive).

**REVISED-1 summary:** Substantive redesign per Codex's recommended option 1 (reuse existing `scripts/gtkb_bridge_writer.py`) merged with option 2 (scope helper to Prime-only statuses). The new design is a **thin convenience wrapper that composes existing validated primitives** plus retry-on-stale-snapshot semantics — not a parallel mutation path. Closes -002 F1 (role + transition validation) by delegating to `gtkb_bridge_writer.validate_transition()`. Closes -002 F2 (file-existence guard) by checking on-disk bridge file presence as a precondition.

---

## Closure of NO-GO Findings (-002)

### F1 Closure — Role Authority + Transition Validation Delegated to Existing Validated Writer

**Original finding:** REVISED-1 candidate proposed an all-status raw inserter that would let any caller insert any status line into any entry, mechanically permitting governance-forbidden states (Prime-side GO insertion, VERIFIED out of sequence, etc.). The bridge protocol defines status ownership: NEW/REVISED → Prime; GO/NO-GO/VERIFIED → LO. Plus transition rules (REVISED requires preceding NO-GO; VERIFIED requires preceding NEW post-impl).

**Closure:** The redesigned `add_status_line()` is **scoped to Prime-only statuses** (NEW + REVISED). LO status writes (GO/NO-GO/VERIFIED) go through the smart-poller's existing dispatch path (`groundtruth-kb/scripts/bridge_poller_runner.py`), not this helper. Within the Prime-only scope, the helper delegates role + transition validation to the existing `scripts/gtkb_bridge_writer.validate_transition(document_name, proposed_status, role_slot=PRIME_ROLE_SLOT, project_root)` which already implements all the rules at `scripts/gtkb_bridge_writer.py:152-223`.

This eliminates the parallel-mutation-path concern Codex flagged: there is exactly one validated writer (`gtkb_bridge_writer.py`); this helper composes over it.

### F2 Closure — File-Existence Guard as Precondition

**Original finding:** The previous helper proposal would let callers insert an INDEX line pointing at a non-existent bridge file, creating phantom INDEX state.

**Closure:** `add_status_line()` checks on-disk bridge file presence as a Phase-2 precondition. If `bridge/<topic_slug>-<version:03d>.md` does not exist when the helper is called, a `BridgeFileNotFoundError` is raised before any INDEX read or write.

The helper does NOT create bridge files — that is Prime's responsibility (via Write tool when authoring proposals/post-impls). The helper only inserts the INDEX line corresponding to an existing on-disk file. This separation matches the existing protocol's "write file, then update INDEX" pattern.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Direct alignment with established principles:**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing belongs in services. The smart-poller-race retroactive-INDEX-commit pattern is exactly this. **REVISED-1 delivers the principle better than `-001` did**: by reusing `gtkb_bridge_writer.py` instead of duplicating it.

**Existing infrastructure this composes over:**
- `scripts/gtkb_bridge_writer.py:152-223` (`validate_transition`) — full role + transition validation. **REVISED-1 delegates to this.**
- `scripts/gtkb_bridge_writer.py:226-246` (`write_bridge_file`) — file-first with post-write verification. NOT used by `add_status_line` (which assumes file already exists; that is Prime's responsibility).
- `scripts/gtkb_bridge_writer.py:249-` (`insert_index_status`) — fresh-read INDEX + optimistic-concurrency check via `expected_index_raw`. **REVISED-1 delegates to this; adds retry-on-stale-snapshot wrapper.**
- `scripts/gtkb_bridge_writer.py` exception classes: `BridgeTransitionError`, `BridgeConflictError`. Re-exported from `write_bridge.py` for caller convenience.

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/file-bridge-protocol.md` — bridge structure
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule
- `bridge-essential.md` — bridge integrity is top-priority

**Backlog record:**
- `memory/work_list.md` row 24 (`GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`) — gap statement, S324 evidence, proposed surface, sequencing.

**Empirical evidence (S324 incidents motivating this work):**
- Commits `a87fc24f`, `3efa04b3`, `2deb054e`, `f83a66a5`-followup, `2e995711`, post-`060dd373` — each is a retroactive INDEX update where Prime's `Edit` lost a race. Token cost: ~1 commit + 1 quality-gate run per occurrence.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

---

## Proposed Changes (REVISED-1 design)

### Change 1 — `.claude/skills/bridge-propose/helpers/write_bridge.py` (extend)

Add a Prime-scoped convenience wrapper that composes existing `gtkb_bridge_writer.py` primitives with retry-on-stale-snapshot semantics.

**New public API (REVISED — Prime-only scope):**
```python
PRIME_AUTHORED_STATUSES: Final[frozenset[str]] = frozenset({"NEW", "REVISED"})

def add_status_line(
    topic_slug: str,
    status: str,  # validated against PRIME_AUTHORED_STATUSES
    version: int,
    *,
    project_root: Path | None = None,
    role_slot: str = "prime-builder",
    max_attempts: int = 2,
) -> None:
    """Insert a Prime-authored status line at the top of an existing entry.

    Phase 1: Validate status is Prime-authored (NEW or REVISED).
             LO statuses (GO, NO-GO, VERIFIED) raise BridgeStatusNotPrimeAuthoredError.
    Phase 2: Verify bridge/<topic_slug>-<NNN>.md exists on disk.
             If not, raise BridgeFileNotFoundError. (F2 closure)
    Phase 3: Delegate to gtkb_bridge_writer.validate_transition() with role_slot.
             Catches BridgeTransitionError; re-raises with context. (F1 closure)
    Phase 4: Retry-loop wrapper around gtkb_bridge_writer.insert_index_status():
             - Read INDEX into snapshot
             - Call insert_index_status(expected_index_raw=snapshot)
             - On BridgeConflictError, retry; max_attempts total
             - On exhaustion, raise BridgeIndexConflictError
    """
```

**New exception classes (re-exported from gtkb_bridge_writer where applicable):**
```python
class BridgeStatusNotPrimeAuthoredError(ValueError):
    \"\"\"Raised when add_status_line is called with a non-Prime status.\"\"\"

class BridgeFileNotFoundError(FileNotFoundError):
    \"\"\"Raised when add_status_line cannot find the on-disk bridge file.\"\"\"

class BridgeIndexConflictError(RuntimeError):
    \"\"\"Raised when add_status_line exhausts retry attempts due to INDEX changes.\"\"\"

# Re-exports for caller convenience:
# BridgeTransitionError (from gtkb_bridge_writer)
# BridgeConflictError (from gtkb_bridge_writer)
```

**Implementation sketch:**
```python
from scripts.gtkb_bridge_writer import (
    PRIME_ROLE_SLOT,
    BridgeConflictError,
    BridgeTransitionError,
    insert_index_status,
    validate_transition,
)

def add_status_line(topic_slug, status, version, *, project_root=None,
                     role_slot=PRIME_ROLE_SLOT, max_attempts=2):
    if status not in PRIME_AUTHORED_STATUSES:
        raise BridgeStatusNotPrimeAuthoredError(
            f"add_status_line is Prime-only; status {status!r} requires LO writer path"
        )
    project_root = project_root or _resolve_project_root()
    bridge_file = project_root / "bridge" / f"{topic_slug}-{version:03d}.md"
    if not bridge_file.is_file():
        raise BridgeFileNotFoundError(f"Bridge file does not exist: {bridge_file}")
    validate_transition(topic_slug, status, role_slot, project_root)  # raises BridgeTransitionError
    index_path = project_root / "bridge" / "INDEX.md"
    for attempt in range(max_attempts):
        snapshot = index_path.read_text(encoding="utf-8")
        try:
            insert_index_status(topic_slug, version, status, project_root,
                                expected_index_raw=snapshot)
            return
        except BridgeConflictError:
            if attempt == max_attempts - 1:
                raise BridgeIndexConflictError(
                    f"INDEX.md changed during {max_attempts} write attempts for "
                    f"{topic_slug} {status} v{version}"
                )
            continue
```

**Public API change:**
- `propose_bridge()` UNCHANGED.
- New: `add_status_line()` + 3 new exception classes + 2 re-exports.
- No parallel mutation path; `add_status_line` strictly composes over `gtkb_bridge_writer.py`.

**Risk:** Low. Pure additive helper; `propose_bridge()` unchanged.

### Change 2 — `tests/skills/test_bridge_propose_add_status_line.py` (new)

11 unit tests (UPDATED in REVISED-1 to cover the new validation surface):

1. **REVISED line insertion success:** Existing entry has `NEW: -001` → `NO-GO: -002`; `add_status_line("foo", "REVISED", 3)` succeeds (legal NO-GO → REVISED transition).

2. **NEW post-impl line insertion success:** Existing entry has `NEW: -001` → `NO-GO: -002` → `REVISED: -003` → `GO: -004`; `add_status_line("foo", "NEW", 5)` succeeds (legal GO → NEW post-impl transition).

3. **LO status REJECTION (REVISED-1 F1 closure):** `add_status_line("foo", "GO", 2)`, `add_status_line("foo", "NO-GO", 2)`, `add_status_line("foo", "VERIFIED", 2)` each raise `BridgeStatusNotPrimeAuthoredError`. (Three sub-cases.)

4. **Wrong-role REJECTION (REVISED-1 F1 closure):** `add_status_line("foo", "REVISED", 2, role_slot="loyal-opposition")` raises `BridgeTransitionError` from delegated `validate_transition()` (LO can't write REVISED).

5. **Illegal-transition REJECTION (REVISED-1 F1 closure):** Existing entry has `NEW: -001` (no NO-GO yet); `add_status_line("foo", "REVISED", 2)` raises `BridgeTransitionError` (REVISED requires preceding NO-GO).

6. **Missing on-disk file REJECTION (REVISED-1 F2 closure):** `add_status_line("foo", "REVISED", 2)` when `bridge/foo-002.md` does NOT exist on disk raises `BridgeFileNotFoundError`. INDEX is unchanged after the failed call.

7. **Entry-not-found REJECTION:** Calling `add_status_line` with a topic_slug whose `Document:` entry is absent from INDEX raises an error from delegated `validate_transition()` (which calls `get_block` → returns None → falls through).

8. **Atomic-temp-file invariant:** Test verifies that on a simulated `insert_index_status` failure, INDEX.md is unchanged (the atomic write inside `gtkb_bridge_writer.insert_index_status` either fully succeeds or fully fails).

9. **Retry-on-race success:** Simulate INDEX modified between read and rename on first attempt; assert second attempt succeeds.

10. **Retry-exhaustion error:** Simulate persistent race; assert `BridgeIndexConflictError` raised after `max_attempts=2` attempts.

11. **Version zero-padding:** `add_status_line("foo", "REVISED", 5)` produces `bridge/foo-005.md`; `add_status_line("foo", "REVISED", 12)` → `bridge/foo-012.md` (3-digit pad consistent with `gtkb_bridge_writer.write_bridge_file`).

**Risk:** Low. Tests-only file.

### Change 3 — `.claude/skills/bridge-propose/SKILL.md` (documentation update)

Document the new `add_status_line()` helper and recommend its use over direct `Edit` of INDEX.md for status-line insertions during Prime authoring. Note that LO status writes go through the smart-poller's path, not this helper.

**Risk:** Low. Documentation only.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md`:

**Spec-to-test mapping (REVISED-1; expanded for new validation surface):**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| Bridge protocol Prime-only role authority for NEW/REVISED | Test 3 (3 sub-cases reject LO statuses) + Test 4 (LO role_slot reject) | `pytest tests/skills/test_bridge_propose_add_status_line.py -k "lo_status or wrong_role" -q` |
| Bridge protocol legal transitions (REVISED after NO-GO; NEW post-impl after GO) | Test 5 (REVISED-without-NO-GO rejects) + Test 1 + Test 2 (legal paths succeed) | `pytest tests/skills/test_bridge_propose_add_status_line.py -k "transition or insertion" -q` |
| `gtkb_bridge_writer.validate_transition` is the single source of authority | Test 4 + Test 5 + Test 7 all rely on `validate_transition` raising `BridgeTransitionError` | covered by tests above |
| F2 file-existence guard (no phantom INDEX state) | Test 6 (missing-file reject) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_missing_on_disk_file_rejects -q` |
| `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (eliminate race-prone manual edits) | Tests 9, 10 (retry success + exhaustion) | `pytest tests/skills/test_bridge_propose_add_status_line.py -k "retry" -q` |
| `propose_bridge()` retry-budget consistency (2 attempts default) | Test 10 (`max_attempts=2` default) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_retry_exhaustion_after_2_attempts -q` |
| Atomic-write invariant (no partial INDEX) | Test 8 | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_atomic_write_no_partial_state -q` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's Specification Links section + bridge-compliance-gate hook approval | hook check (passed) |
| Project root boundary | Edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |
| Code quality (ruff) | ruff clean on edited files | `python -m ruff check .claude/skills/bridge-propose/helpers/write_bridge.py tests/skills/test_bridge_propose_add_status_line.py` |
| `propose_bridge()` unchanged | Existing propose_bridge tests still pass | `pytest tests/skills/ -q` (full skill tests) |

**Execution commands (planned for post-impl report):**
```bash
python -m ruff check .claude/skills/bridge-propose/helpers/write_bridge.py tests/skills/test_bridge_propose_add_status_line.py
pytest tests/skills/test_bridge_propose_add_status_line.py -q
pytest tests/skills/ -q
```

The release-gate is NOT part of this slice's verification surface (release-gate has known infrastructure issues per other in-flight work).

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md`:

- All edited files inside `E:\GT-KB`:
  - `.claude/skills/bridge-propose/helpers/write_bridge.py` (extended)
  - `tests/skills/test_bridge_propose_add_status_line.py` (new)
  - `.claude/skills/bridge-propose/SKILL.md` (documentation update)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- All planned post-impl verification commands operate inside `E:\GT-KB`.
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean fresh implementation. No source-code edits in worktree for this slice. All implementation will be authored after Codex GO.

---

## Implementation Sequence (planned for after Codex GO)

1. Read existing `propose_bridge()` and confirm reusable primitives in `scripts/gtkb_bridge_writer.py` (validate_transition, insert_index_status, exception classes).
2. Implement `add_status_line()` per the API spec; delegate role + transition + insert to `gtkb_bridge_writer`; add the retry wrapper.
3. Add the 3 new exception classes + 2 re-exports.
4. Author the 11 test cases in `tests/skills/test_bridge_propose_add_status_line.py`.
5. Update `.claude/skills/bridge-propose/SKILL.md` documentation.
6. Run `python -m ruff check` on edited files — expect clean.
7. Run `pytest tests/skills/test_bridge_propose_add_status_line.py` — expect 11 passed (including the 3 sub-cases of Test 3, the test count is reported as 13 by pytest if sub-cases parametrize; the bridge-thread "11 tests" is the logical-test count).
8. Run `pytest tests/skills/ -q` — expect existing skill tests still pass (regression check).
9. Stage the 3 files. No other files.
10. Commit.
11. File post-impl report.

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — covers 3 files.
- Existing `propose_bridge()` is unchanged; rollback fully restores prior behavior.
- `gtkb_bridge_writer.py` is NOT modified by this slice (composition-only); no rollback needed there.

---

## Decision Needed From Owner

This bridge does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
