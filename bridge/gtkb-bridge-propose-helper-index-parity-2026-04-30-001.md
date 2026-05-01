NEW

# Bridge Proposal — GTKB Bridge-Propose Helper INDEX Parity

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-bridge-propose-helper-index-parity-2026-04-30`
**Trigger:** Owner directive S324 (in response to Prime insight on smart-poller-race overhead): "Promoting INDEX edits exclusively through the bridge-propose helper (which has 2-attempt retry semantics) would eliminate this pattern. Adding helper-mediated INDEX update for VERIFIED line additions is a candidate hygiene item. ... This should be tracked and completed at the next opportunity." Tracked as row 24 of `memory/work_list.md`. Pivot from S0 NO-GO `-004` per S324 AskUserQuestion answer "Hold; pivot to row 24 hygiene first."

**Owner pre-approval:** Yes for the program-level scope per the row 24 work_list entry's "Owner pre-approval: program-level via S324 directive." Standard Codex GO required before implementation per `.claude/rules/codex-review-gate.md`.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Direct alignment with established principles:**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing belongs in services, not in sessions. The smart-poller-race retroactive-INDEX-commit pattern is exactly the kind of repetitive AI-mediated work this principle targets.

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/file-bridge-protocol.md` — bridge structure; defines INDEX.md grammar (Document/status lines, top-of-list semantics, append-only audit trail)
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage gate
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED gate requires spec-derived test mapping
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule that governance constraints must be mechanically enforced

**Existing helper this extends:**
- `.claude/skills/bridge-propose/helpers/write_bridge.py:propose_bridge()` — current helper handles initial `Document: <slug>` + `NEW: -001` insertion atomically with 2-attempt retry. This bridge proposes a sibling function that uses the same retry pattern for inserting status lines into existing entries.

**Backlog record:**
- `memory/work_list.md` row 24 (`GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`) — gap statement, S324 evidence (5+ retroactive INDEX commits this session), proposed surface, sequencing.

**Empirical evidence (S324 incidents motivating this work):**
- Commits `a87fc24f`, `3efa04b3`, `2deb054e`, plus the retroactive followup after `f83a66a5`, plus `2e995711` — each is a retroactive INDEX update where Prime's `Edit` lost a race to the smart-poller's atomic `os.replace`. Token cost: ~1 commit + 1 quality-gate run per occurrence (~15-30k tokens of overhead).

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

---

## Proposed Changes

### Change 1 — `.claude/skills/bridge-propose/helpers/write_bridge.py` (extend)

Add a sibling function to `propose_bridge()` that handles INDEX-line insertion into existing entries.

**New public API:**
```python
def add_status_line(
    topic_slug: str,
    status: Literal["NEW", "REVISED", "GO", "NO-GO", "VERIFIED"],
    version: int,
    *,
    bridge_dir: Path | None = None,
) -> None:
    \"\"\"Insert a status line at the top of an existing document entry's version list.

    Phase 1 — Locate entry: parse INDEX.md for `Document: <topic_slug>`.
              If not found, raise BridgeEntryNotFoundError.
    Phase 2 — Build line: `<status>: bridge/<topic_slug>-<NNN>.md` (NNN zero-padded).
              If the exact (status, file) line already exists in the entry, raise
              BridgeStatusLineDuplicateError to prevent silent double-insertions.
    Phase 3 — Atomic update with retry: temp-file + `os.replace` pattern.
              On `BridgeIndexConflictError`, retry once. Total budget 2 attempts
              (matching propose_bridge's retry semantics).

    Args:
        topic_slug: kebab-case slug; must match an existing `Document:` entry.
        status: one of the 5 documented bridge statuses.
        version: integer version number; will be zero-padded to 3 digits.
        bridge_dir: parent bridge directory. Defaults to Path("bridge").

    Raises:
        BridgeEntryNotFoundError: `Document: <topic_slug>` not found in INDEX.md.
        BridgeStatusLineDuplicateError: exact (status, file) line already present.
        BridgeIndexConflictError: INDEX.md changed during write across both attempts.
    \"\"\"
```

**New exception class:**
```python
class BridgeEntryNotFoundError(RuntimeError):
    \"\"\"Raised when add_status_line cannot find Document: <topic_slug> in INDEX.\"\"\"

class BridgeStatusLineDuplicateError(RuntimeError):
    \"\"\"Raised when add_status_line is called with a (status, file) tuple already
    present in the entry. Prevents silent double-insertion across retries.\"\"\"
```

**Implementation outline (private helpers):**
- Reuse `_atomic_write_index()` (or factor it out of `_update_bridge_index` if currently inlined) to share the temp-file + retry mechanics with `propose_bridge`.
- New `_insert_status_line_into_entry(index_text, topic_slug, status_line)` returns the new INDEX text or raises `BridgeEntryNotFoundError`. Pure-function for testability.

**Public API change:**
- `propose_bridge()` unchanged.
- New: `add_status_line()` and 2 new exception classes.

**Risk:** Low. Pure additive helper. No behavior change to existing `propose_bridge()`.

### Change 2 — `tests/skills/test_bridge_propose_add_status_line.py` (new)

Unit tests covering:

1. **REVISED line insertion:** Existing entry has `NEW: -001`; `add_status_line("foo", "REVISED", 2)` produces `REVISED: bridge/foo-002.md` at top of entry, `NEW: bridge/foo-001.md` retained below.

2. **NEW post-impl line insertion:** After `GO: -004`, `add_status_line("foo", "NEW", 5)` inserts at top.

3. **Audit-trail-landing GO/NO-GO/VERIFIED line insertion:** All three statuses tested independently.

4. **Entry-not-found:** Calling `add_status_line` with a topic_slug that has no `Document: <slug>` entry raises `BridgeEntryNotFoundError` with a descriptive message.

5. **Duplicate detection:** Calling `add_status_line("foo", "REVISED", 2)` twice raises `BridgeStatusLineDuplicateError` on the second call (the first call inserted the line; the second sees the same line present).

6. **Atomic-temp-file:** Test verifies that on a simulated mid-write failure, INDEX.md is either fully old or fully new — never partial. (Implementation: monkeypatch `os.replace` to raise once, assert INDEX content is unchanged.)

7. **Retry-on-race success:** Simulate INDEX.md being modified between read and rename on first attempt; assert second attempt succeeds and inserts the line correctly. (Implementation: monkeypatch `_read_index` to return different content on first vs. second call.)

8. **Retry-on-race exhaustion:** Simulate persistent race (every read sees a different INDEX); assert `BridgeIndexConflictError` raised after 2 attempts.

9. **Version zero-padding:** `add_status_line("foo", "REVISED", 5)` produces `bridge/foo-005.md` (3-digit padding); `add_status_line("foo", "REVISED", 12)` produces `bridge/foo-012.md`.

10. **Top-of-list ordering invariant:** New line is inserted as the FIRST status line under `Document:`, preserving the bridge-protocol's "current top = latest" semantics. Existing entries remain in their prior order.

**Risk:** Low. Tests-only file.

### Change 3 — Documentation updates (minimal)

Update `.claude/skills/bridge-propose/SKILL.md` to mention the new `add_status_line()` helper and recommend its use over direct `Edit` of INDEX.md for status-line insertions.

**Risk:** Low. Documentation only.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping:**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| Bridge protocol "top of list = current top" semantics | Test 10 (top-of-list ordering invariant) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_top_of_list_ordering -q` |
| `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (no manual race-prone INDEX edits) | Test 7 (retry-on-race succeeds) + Test 8 (retry exhaustion produces structured error) | `pytest tests/skills/test_bridge_propose_add_status_line.py -k "retry" -q` |
| `propose_bridge()` retry-budget consistency (2 attempts) | Test 8 explicitly counts attempts; assert 2 total | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_retry_exhaustion_raises_after_2_attempts -q` |
| Atomic-write invariant (no partial INDEX) | Test 6 (atomic-temp-file failure leaves INDEX intact) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_atomic_write_no_partial_state -q` |
| Duplicate-prevention (silent re-insertion is a bug) | Test 5 (duplicate raises) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_duplicate_status_line_raises -q` |
| Status / version validation | Tests 1, 2, 3, 9 (each status; zero-padding) | `pytest tests/skills/test_bridge_propose_add_status_line.py -k "insertion or zero_padding" -q` |
| Entry-not-found graceful failure | Test 4 (BridgeEntryNotFoundError) | `pytest tests/skills/test_bridge_propose_add_status_line.py::test_entry_not_found_raises -q` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's Specification Links section + bridge-compliance-gate hook approval | hook check (already passed) |
| Project root boundary | Edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |
| Code quality (ruff) | ruff clean on edited files | `python -m ruff check .claude/skills/bridge-propose/helpers/write_bridge.py tests/skills/test_bridge_propose_add_status_line.py` |

**Execution commands (planned for post-impl report):**
```bash
python -m ruff check .claude/skills/bridge-propose/helpers/write_bridge.py tests/skills/test_bridge_propose_add_status_line.py
pytest tests/skills/test_bridge_propose_add_status_line.py -q
```

The release-gate is NOT part of this slice's verification surface (release-gate has known infrastructure issues per other in-flight work). Per-test verification via `pytest` plus ruff is sufficient.

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md`:

- All edited files inside `E:\GT-KB`:
  - `.claude/skills/bridge-propose/helpers/write_bridge.py` (extended)
  - `tests/skills/test_bridge_propose_add_status_line.py` (new)
  - `.claude/skills/bridge-propose/SKILL.md` (documentation update)
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- No external paths referenced.

---

## Pre-GO Drift Disposition

Clean fresh implementation. No source-code edits in worktree for this slice. All implementation will be authored after Codex GO.

---

## Implementation Sequence (planned for after Codex GO)

1. Read existing `propose_bridge()` implementation; identify reusable INDEX-update primitives (atomic-temp-file, retry loop).
2. Factor reusable primitives if needed (private `_atomic_write_index` helper).
3. Add `BridgeEntryNotFoundError` and `BridgeStatusLineDuplicateError` exception classes.
4. Implement `add_status_line()` per the API spec above.
5. Author `tests/skills/test_bridge_propose_add_status_line.py` with the 10 test cases.
6. Update `.claude/skills/bridge-propose/SKILL.md` to document the new helper.
7. Run `python -m ruff check` on all edited files — expect clean.
8. Run `pytest tests/skills/test_bridge_propose_add_status_line.py` — expect 10 passed.
9. Stage the 3 files (helper + test + docs); no other files.
10. Commit with scoped message referencing this bridge thread.
11. File post-impl report.

After VERIFIED: future bridge cycles can use `add_status_line()` for REVISED / post-impl NEW / audit-trail GO/NO-GO/VERIFIED insertions, eliminating the smart-poller-race retroactive-INDEX-commit pattern.

---

## Rollback Notes

If post-impl reveals an unexpected issue:
- Revert the single commit via `git revert <sha>` — covers 3 files (helper + test + docs).
- The bridge thread is append-only audit history.

Existing `propose_bridge()` is unchanged; rollback restores prior behavior fully.

---

## Decision Needed From Owner

This bridge does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
