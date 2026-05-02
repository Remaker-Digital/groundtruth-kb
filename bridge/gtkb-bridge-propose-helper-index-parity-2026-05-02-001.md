NEW

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY: `add_status_line` extension to `write_bridge.py`

**Status:** NEW (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** Owner directive S324 captured in `memory/work_list.md` row 24; explicit pre-approval at program level: "This should be tracked and completed at the next opportunity."

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-bridge-propose-helper-index-parity-2026-05-02` entry

This commit does NOT modify `write_bridge.py`, `test_bridge_propose_helper.py`, or any caller. Those changes ship in the implementation commit after Codex GO.

## Specification Links

- `memory/work_list.md` row 24 (`GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`) — owner directive + scope
- `.claude/skills/bridge-propose/helpers/write_bridge.py` lines 235-362 — existing `_compute_new_index_content` + `_update_bridge_index` helpers (the atomic write + 2-retry pattern this proposal extends)
- `.claude/skills/bridge-propose/helpers/write_bridge.py` lines 365-448 — existing `propose_bridge` orchestrator (the Phase-3 INDEX-update model the new function reuses)
- `groundtruth-kb/tests/test_bridge_propose_helper.py` — 22 existing tests for `propose_bridge` / `_update_bridge_index` patterns; new tests follow the same shape
- `.claude/rules/file-bridge-protocol.md` lines 50-130 — INDEX entry format: `Document: <slug>` followed by status lines newest-first; status enum NEW / REVISED / GO / NO-GO / VERIFIED
- `.claude/rules/project-root-boundary.md` — change is under `E:\GT-KB`
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate
- `.claude/rules/codex-review-gate.md` — Codex GO required before implementation
- `GOV-09`, `GOV-20` — no owner decision; helper extension is mechanical hygiene; no GOV-20 IPR/CVR (this is not a Phase 9 isolation deliverable, it's tooling hygiene per work_list row 24)

## Owner Decisions

**None.** Owner pre-approved at program level; helper extension is mechanical.

## Problem Statement

`propose_bridge()` handles the initial `Document: <slug>` + `NEW: bridge/<slug>-001.md` insertion case using an atomic temp-file write + 2-attempt retry against concurrent modification. But Prime Builder also routinely needs to insert subsequent status lines into existing entries:

- `REVISED: bridge/<slug>-NNN.md` (after a NO-GO)
- `NEW: bridge/<slug>-NNN.md` (post-implementation report after a GO)
- Audit-trail landings of `GO`/`NO-GO`/`VERIFIED` lines from Codex output

Today these are done via direct `Edit` tool calls on `bridge/INDEX.md`. Each direct Edit races the smart-poller's atomic `os.replace`. Empirical evidence (S324, work_list row 24): at least 5 retroactive INDEX commits in one session due to lost races.

## Implementation Plan

Implementation commit (after Codex GO) lands:

### 1. New helper function `add_status_line`

**File:** `.claude/skills/bridge-propose/helpers/write_bridge.py` (~80 LOC added)

```python
class BridgeDocumentNotFoundError(RuntimeError):
    """Raised when ``Document: <topic_slug>`` is not present in INDEX.md.

    The caller asked to add a status line to an existing entry, but no
    matching ``Document:`` block exists. Either the topic is misspelled
    or ``propose_bridge()`` should be used instead (which creates the
    initial ``Document:`` + ``NEW:`` pair).
    """


_VALID_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "VERIFIED"}
)


def _compute_new_index_content_with_status_line(
    existing_lines: list[str],
    topic_slug: str,
    new_status_line: str,
) -> str:
    """Insert ``new_status_line`` immediately after the ``Document: <slug>`` line.

    Status lines within an entry are listed newest-first per the bridge
    protocol; therefore new status lines insert at the TOP of the
    entry's version list (immediately after ``Document:``).

    Raises:
        BridgeDocumentNotFoundError: when ``Document: <topic_slug>`` is
            absent from ``existing_lines``.
    """
    expected = f"Document: {topic_slug}"
    for idx, line in enumerate(existing_lines):
        if line.strip() == expected:
            entry = (
                new_status_line
                if new_status_line.endswith("\n")
                else new_status_line + "\n"
            )
            return (
                "".join(existing_lines[: idx + 1])
                + entry
                + "".join(existing_lines[idx + 1 :])
            )
    raise BridgeDocumentNotFoundError(
        f"INDEX.md has no entry for {expected!r}. "
        f"Use propose_bridge() to create the initial Document + NEW pair."
    )


def add_status_line(
    topic_slug: str,
    status: Literal["NEW", "REVISED", "GO", "NO-GO", "VERIFIED"],
    version: int,
    *,
    bridge_dir: Path | None = None,
    require_file_exists: bool = True,
) -> None:
    """Insert ``<status>: bridge/<topic_slug>-<NNN>.md`` into the existing Document entry.

    Mirrors the atomic + 2-retry pattern from ``propose_bridge()`` for
    incremental status-line additions to an existing INDEX entry. Use
    this for REVISED, post-implementation NEW, and audit-trail landings
    of Codex GO/NO-GO/VERIFIED lines.

    File-first contract: when ``require_file_exists=True`` (default),
    the function asserts ``bridge/<topic_slug>-<NNN>.md`` exists before
    touching INDEX. Set ``require_file_exists=False`` only for the
    audit-trail Codex-side landing case where the verdict file may have
    been written by Codex separately.

    Args:
        topic_slug: Existing slug; must already have a
            ``Document: <slug>`` entry in INDEX.
        status: One of ``NEW`` / ``REVISED`` / ``GO`` / ``NO-GO`` / ``VERIFIED``.
        version: Integer 1-999; formatted as ``-{NNN}`` (zero-padded).
        bridge_dir: Defaults to ``Path("bridge")``.
        require_file_exists: Default ``True`` (file-first contract).

    Raises:
        ValueError: ``status`` not in valid set, or ``version`` out of [1, 999].
        BridgeFileAlreadyExistsError: NEVER raised (this function does
            not write the bridge file; it expects it to exist if
            ``require_file_exists=True``).
        FileNotFoundError: ``require_file_exists=True`` and the bridge
            file is absent.
        BridgeDocumentNotFoundError: ``Document: <slug>`` is absent
            from INDEX.
        BridgeIndexConflictError: INDEX could not be updated after 2
            total attempts (1 initial + 1 retry), matching ``propose_bridge``.
    """
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Invalid status {status!r}; expected one of {sorted(_VALID_STATUSES)}"
        )
    if not 1 <= version <= 999:
        raise ValueError(f"version must be in [1, 999]; got {version}")

    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    version_str = f"{version:03d}"
    bridge_file = bridge_root / f"{topic_slug}-{version_str}.md"
    index_path = bridge_root / "INDEX.md"

    if require_file_exists and not bridge_file.exists():
        raise FileNotFoundError(
            f"Expected {bridge_file} to exist before INDEX update. "
            f"Either write the bridge file first, or pass "
            f"require_file_exists=False for audit-trail landing of "
            f"Codex-side verdict files."
        )

    new_status_line = f"{status}: bridge/{topic_slug}-{version_str}.md\n"

    last_error: BridgeIndexConflictError | None = None
    max_attempts = 2  # 2 total attempts — 1 initial + 1 retry (matches propose_bridge).
    for attempt in range(1, max_attempts + 1):
        try:
            _update_bridge_index_with_status_line(
                index_path, new_status_line, topic_slug=topic_slug
            )
            return
        except BridgeIndexConflictError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
    raise BridgeIndexConflictError(
        f"Status line {new_status_line.strip()!r} could not be added to "
        f"INDEX.md after 2 total attempts. The bridge file at {bridge_file} "
        f"is on disk; manually add the line or retry. Last error: {last_error}"
    )


def _update_bridge_index_with_status_line(
    index_path: Path,
    new_status_line: str,
    *,
    topic_slug: str,
) -> None:
    """Insert a status line atomically (mirrors _update_bridge_index)."""
    original_bytes = index_path.read_bytes()
    lines = original_bytes.decode("utf-8").splitlines(keepends=True)
    new_content = _compute_new_index_content_with_status_line(
        lines, topic_slug, new_status_line
    )
    temp_path = index_path.with_name(f"{index_path.name}.tmp.{os.getpid()}")
    temp_path.write_bytes(new_content.encode("utf-8"))
    try:
        current_bytes = index_path.read_bytes()
        if current_bytes != original_bytes:
            temp_path.unlink()
            raise BridgeIndexConflictError(
                "INDEX.md changed during update — concurrent modification detected."
            )
        os.replace(temp_path, index_path)
    except BridgeIndexConflictError:
        raise
    except Exception:
        if temp_path.exists():
            with contextlib.suppress(OSError):
                temp_path.unlink()
        raise
```

### 2. `__all__` update

Add `add_status_line` and `BridgeDocumentNotFoundError` to the module's `__all__` list.

### 3. Tests

**File:** `groundtruth-kb/tests/test_bridge_propose_helper.py` — extended with ~150 LOC of new tests:

```python
def test_add_status_line_inserts_after_document_line(tmp_path: Path) -> None:
    """Status line inserted immediately after the matching Document line."""

def test_add_status_line_preserves_other_entries(tmp_path: Path) -> None:
    """Other Document entries in INDEX are unchanged."""

def test_add_status_line_raises_when_document_absent(tmp_path: Path) -> None:
    """BridgeDocumentNotFoundError when Document:<slug> is missing."""

def test_add_status_line_raises_when_bridge_file_missing(tmp_path: Path) -> None:
    """FileNotFoundError when require_file_exists=True and file absent."""

def test_add_status_line_skips_file_check_when_disabled(tmp_path: Path) -> None:
    """require_file_exists=False allows audit-trail landing without file."""

def test_add_status_line_validates_status_enum(tmp_path: Path) -> None:
    """Invalid status raises ValueError before any IO."""

def test_add_status_line_validates_version_range(tmp_path: Path) -> None:
    """version outside [1, 999] raises ValueError before any IO."""

def test_add_status_line_atomic_via_os_replace(tmp_path, monkeypatch) -> None:
    """Atomicity test parallel to test_update_bridge_index_is_atomic_via_os_replace."""

def test_add_status_line_detects_concurrent_modification(tmp_path, monkeypatch) -> None:
    """Concurrent modification triggers retry; second failure raises BridgeIndexConflictError."""

def test_add_status_line_retry_budget_is_2_total(tmp_path, monkeypatch) -> None:
    """Retry budget exactly mirrors propose_bridge: 2 total attempts (1 initial + 1 retry)."""

def test_add_status_line_exact_line_match_for_document_lookup(tmp_path: Path) -> None:
    """Document lookup uses exact line match, not substring (parallels propose_bridge contract)."""
```

**Satisfies:** work_list row 24 acceptance ("Adding helper-mediated INDEX update for VERIFIED line additions").

## Output Layout

No runtime output. Pure helper extension to an existing skill module.

## Specification-Derived Verification

| # | Test | Derives from |
|---|---|---|
| T1 | `test_add_status_line_inserts_after_document_line` | Bridge protocol: status lines newest-first within entry (file-bridge-protocol.md) |
| T2 | `test_add_status_line_preserves_other_entries` | INDEX integrity: other Documents unchanged |
| T3 | `test_add_status_line_raises_when_document_absent` | New `BridgeDocumentNotFoundError` contract |
| T4 | `test_add_status_line_raises_when_bridge_file_missing` | File-first contract (require_file_exists default) |
| T5 | `test_add_status_line_skips_file_check_when_disabled` | Audit-trail landing escape hatch |
| T6 | `test_add_status_line_validates_status_enum` | Status enum gate |
| T7 | `test_add_status_line_validates_version_range` | Version range gate |
| T8 | `test_add_status_line_atomic_via_os_replace` | Atomicity (mirrors `propose_bridge`) |
| T9 | `test_add_status_line_detects_concurrent_modification` | Concurrency detection (mirrors `propose_bridge`) |
| T10 | `test_add_status_line_retry_budget_is_2_total` | 2-attempt retry parity with `propose_bridge` |
| T11 | `test_add_status_line_exact_line_match_for_document_lookup` | Exact-line match contract (slug-prefix safety, mirrors `propose_bridge`) |

Plus regression: existing 22 `test_bridge_propose_helper.py` tests must remain green.

**Test execution commands:**

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_bridge_propose_helper.py -q --tb=short --timeout=30
python -m ruff check ../.claude/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py
python -m ruff format --check ../.claude/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py
```

## Risk / Impact

**Trivial / additive (low):** pure additive helper; no change to `propose_bridge`, `_compute_new_index_content`, or `_update_bridge_index`. Existing tests remain green by construction.

**Concurrency parity (low):** new `_update_bridge_index_with_status_line` mirrors `_update_bridge_index` exactly (read original → compute new → write temp → re-read original → atomic rename → cleanup on error). Behavior equivalence is asserted by T8/T9/T10.

**Caller migration (deferred):** This proposal does NOT migrate Prime Builder's existing INDEX-edit call sites. That's a follow-on hygiene pass best done after the helper has soaked. Manual `Edit` calls remain valid until migrated.

**No GOV-20 IPR/CVR:** this is tooling hygiene per work_list row 24, not a Phase 9 isolation deliverable. The cosmetic-exemption pattern from Row 25 applies.

## Acceptance Criteria

GO-able when Codex confirms:

1. `add_status_line` signature matches the spec (topic_slug, status, version + kwargs).
2. Status enum is exactly `{NEW, REVISED, GO, NO-GO, VERIFIED}`.
3. File-first contract: `require_file_exists=True` (default) checks file existence before INDEX.
4. Insertion location: immediately after the matching `Document: <slug>` line.
5. Atomicity + 2-retry parity with `propose_bridge`.
6. Document-not-found is a distinct error class, not `BridgeIndexConflictError`.
7. Test plan covers all 11 contract assertions.
8. Specification Links cover all governing artifacts.
9. Scope of the proposal commit matches what will land (proposal + INDEX only).

## Decision Needed From Owner

Nothing required at GO time. Owner pre-approved at program level via work_list row 24.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
