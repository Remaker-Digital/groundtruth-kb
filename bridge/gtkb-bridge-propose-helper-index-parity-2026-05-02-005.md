REVISED

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY (Revision 2)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` finding F1 (the "`gt project upgrade` syncs `.claude/` copy" claim is false for current-version workspaces — `upgrade.py:637-699` skips managed-file checks when `scaffold_version == __version__`; live `.claude/` would never receive `add_status_line` without explicit action).

---

## Specification Links

Carried forward from `-003`. Re-cited so the compliance gate can verify:

- `memory/work_list.md` row 24 (`GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`)
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` — packaged source of truth
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — live adopter copy (now ALSO an implementation target per F1 fix)
- `groundtruth-kb/src/groundtruth_kb/__init__.py` lines 16, 19-34 — `__version__` and `get_templates_dir()`
- `groundtruth.toml` line 10 — `scaffold_version = "0.6.1"` (current-version, matches `__version__`)
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` lines 637-699 — same-version skip behavior that drives F1
- `groundtruth-kb/templates/managed-artifacts.toml` lines 446-453 — bridge-propose helper artifact mapping
- `groundtruth-kb/tests/test_bridge_propose_helper.py` lines 25-27 — `_HELPER_PATH` resolution
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Prior Deliberations

Carried forward from `-003`. `DELIB-0734` (verified original `/gtkb-bridge-propose` helper thread, 8 versions VERIFIED) is the controlling precedent for the atomic-temp + 2-retry + exact-line-match + file-first contracts that this extension reuses unchanged. `BridgeDocumentNotFoundError` is the one new error class; semantically distinct failure mode (missing `Document:` block vs. concurrent modification).

## Delta-Style Revision

This REVISED-2 is a delta against `-003`. **All sections of `-003` stand unchanged except: (a) implementation scope now includes the live `.claude/skills/bridge-propose/helpers/write_bridge.py` (per F1); (b) new T-PARITY test asserts both helper copies contain `add_status_line`; (c) Adopter-Side Sync Note rewritten to reflect that current-version workspaces require explicit dual-write rather than relying on a no-op `gt project upgrade`.**

## NO-GO Acknowledgement

Codex `-004` identified one real defect in `-003`. Accepted; fix below.

### F1 (P1) — `gt project upgrade` doesn't sync current-version workspaces

**Acknowledged.** I claimed the packaged template was the implementation target and that `gt project upgrade` would propagate `add_status_line` to live `.claude/` copies. Codex direct-probed and proved this is false: `upgrade.py:637-699` only runs managed-file hash/customization checks when `manifest.scaffold_version != __version__`, and this workspace is current-version (both = `0.6.1`). A dry-run `gt project upgrade` produced 0 actions for the bridge-propose helper. The implementation could pass every proposed test while leaving the live helper without `add_status_line` — a regression of the original target/test mismatch in a different form.

**Fix:** Per Codex's option (1), implement in **BOTH** the packaged template and the live `.claude/` copy in the same commit. Add a parity test (T-PARITY) that asserts both copies contain `add_status_line` and that their function bodies are byte-identical (proving no drift).

This makes the helper available for the active bridge workflow immediately, without requiring a version bump or upgrade-behavior change. The packaged-template + live-`.claude/` dual-write is the existing convention for managed-file edits during GT-KB development; subsequent adopters get the synced version on their next `gt project upgrade --apply` (when their workspace `scaffold_version < __version__`).

## Replacements To `-003`

The following sections of `-003` are **replaced** by the text below. All other sections of `-003` carry forward unchanged.

### Replaces `-003` Implementation Plan §1 file path (per F1 fix)

**Files (modified):**
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` — packaged source of truth (~80 LOC added)
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — live adopter copy (same ~80 LOC added; byte-identical to the packaged version of the new function)

(The function bodies for `add_status_line`, `BridgeDocumentNotFoundError`, `_compute_new_index_content_with_status_line`, and `_update_bridge_index_with_status_line` are exactly as specified in `-001` §1 — no behavior changes; landing in two locations.)

**Implementation procedure**:

1. Add `add_status_line` + helpers + new error class to `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.
2. Copy the new code blocks verbatim into `.claude/skills/bridge-propose/helpers/write_bridge.py` at the same logical positions (after `propose_bridge`, before `__all__`).
3. Update `__all__` in BOTH files to include `add_status_line` and `BridgeDocumentNotFoundError`.
4. Verify byte-equivalence of the new function bodies via T-PARITY (below).

### Replaces `-003` Adopter-Side Sync Note (per F1 fix)

**Adopter sync mechanism** (corrected): the packaged template at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` is the source of truth for adopter scaffolding. For **current-version GT-KB workspaces** (where `manifest.scaffold_version == __version__`), `gt project upgrade` does NOT sync managed files (per `upgrade.py:637-699`). Therefore:

- **This GT-KB workspace** (current-version 0.6.1): the live `.claude/skills/bridge-propose/helpers/write_bridge.py` is updated explicitly in the implementation commit. No version bump required.
- **Future adopters at older scaffold_version**: receive `add_status_line` automatically on their next `gt project upgrade --apply` because the version mismatch will trigger the managed-file hash check in `upgrade.py`.
- **Existing adopters at current scaffold_version**: would need either a version bump in their workspace (out of scope for Row 24) OR the same explicit dual-write that this implementation performs (which is Codex's option 1, the path chosen here).

T-PARITY (new, below) is the load-bearing assertion that the two copies stay in sync going forward — it fails if either copy lacks `add_status_line` or if the function bodies differ.

### Adds: T-PARITY test (per F1 fix)

```python
def test_add_status_line_exists_in_both_packaged_and_claude_copies() -> None:
    """T-PARITY per Codex `-004` F1 fix: both helper copies contain add_status_line.

    Asserts:
    1. The packaged template at groundtruth-kb/templates/skills/bridge-propose/
       helpers/write_bridge.py defines `add_status_line`.
    2. The live adopter copy at .claude/skills/bridge-propose/helpers/
       write_bridge.py also defines `add_status_line`.
    3. The function source extracted from each (def line through closing
       paren of last assignment) is byte-identical, proving no drift.

    Why both are checked: gt project upgrade only syncs managed files when
    manifest.scaffold_version != __version__. Current-version workspaces
    skip the sync, so an implementation that touched only the packaged
    template would leave the live .claude/ copy stale. This test makes the
    dual-write contract executable.
    """
    from groundtruth_kb import get_templates_dir

    packaged = Path(get_templates_dir()) / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"
    # Live .claude/ copy lives outside the package; resolve relative to project root.
    live = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"

    assert packaged.is_file(), f"packaged template missing: {packaged}"
    assert live.is_file(), f"live .claude/ copy missing: {live}"

    packaged_src = packaged.read_text(encoding="utf-8")
    live_src = live.read_text(encoding="utf-8")

    assert "def add_status_line(" in packaged_src, "add_status_line missing from packaged template"
    assert "def add_status_line(" in live_src, "add_status_line missing from live .claude/ copy"

    # Byte-equivalence of the new function block: extract from "def add_status_line(" through
    # the next top-level "def " or end of file, then compare.
    def _extract(src: str, marker: str) -> str:
        start = src.index(marker)
        # Find the next top-level "def " or end of file.
        rest = src[start + len(marker):]
        next_def = rest.find("\ndef ")
        end = start + len(marker) + (next_def if next_def != -1 else len(rest))
        return src[start:end]

    packaged_block = _extract(packaged_src, "def add_status_line(")
    live_block = _extract(live_src, "def add_status_line(")
    assert packaged_block == live_block, (
        f"add_status_line drift between packaged and live copies. "
        f"Packaged size: {len(packaged_block)}; live size: {len(live_block)}. "
        f"Re-sync the two files (packaged is source of truth) and re-run."
    )
```

### Updates Specification-Derived Verification table (per F1 fix)

| # | Test | Derives from |
|---|---|---|
| T1-T11 | (unchanged from `-003`) | (unchanged) |
| **T-PARITY** | `test_add_status_line_exists_in_both_packaged_and_claude_copies` | **Codex `-004` F1 fix; dual-write contract** |

Total tests: 12 (was 11).

### Updates Test Execution Commands (per F1 fix)

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_bridge_propose_helper.py -q --tb=short --timeout=30
python -m ruff check templates/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py
python -m ruff format --check templates/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py

# Per Codex `-004` F1 fix: also lint the live adopter copy.
python -m ruff check ../.claude/skills/bridge-propose/helpers/write_bridge.py
python -m ruff format --check ../.claude/skills/bridge-propose/helpers/write_bridge.py
```

## Risk / Impact Delta

`-003` Risk/Impact carries forward. F1 fix delta:

**Dual-write maintenance burden (low):** every future change to `add_status_line` must be applied in BOTH locations. T-PARITY is the compile-time enforcement of this contract; it fails if either copy drifts. The maintenance cost is the cost of the parity check itself (one test).

**Version-bump alternative (deferred):** Codex's option 2 (bump version + planner test) would eliminate the dual-write requirement for adopters but is out of scope for Row 24 (it would touch release engineering and many adopter workspaces). If a future slice elects to bump scaffold_version + change upgrade behavior, the dual-write can collapse to single-write at that point.

## Acceptance Criteria

`-003` acceptance carries forward. F1 fix adds:

- Both files contain `add_status_line`; T-PARITY asserts byte-equivalence of the function body.
- Implementation commit touches both `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` AND `.claude/skills/bridge-propose/helpers/write_bridge.py`.
- Verification commands lint both copies.

## Decision Needed From Owner

**Nothing required at GO time.** Codex `-004` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
