REVISED

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` findings F1 (implementation target ↔ test target mismatch — `.claude/skills/...` vs packaged `groundtruth-kb/templates/skills/...`) and F2 (missing prior-deliberation linkage to `DELIB-0734`).

---

## Specification Links

Carried forward from `-001`, with added pointers per F1 + F2:

- `memory/work_list.md` row 24 (`GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`) — owner directive + scope
- **`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`** — the packaged source of truth (per F1 fix; this is the implementation target)
- `groundtruth-kb/src/groundtruth_kb/__init__.py` lines 19-34 — `get_templates_dir()` resolution that the test harness uses
- `.claude/skills/bridge-propose/helpers/write_bridge.py` — adopter-side copy synchronized via `gt project upgrade` (per F1 fix; NOT the implementation target)
- `groundtruth-kb/tests/test_bridge_propose_helper.py` lines 25-27 — `_HELPER_PATH` resolves to the packaged template, confirming the test target alignment
- `.claude/rules/file-bridge-protocol.md` lines 50-130 — INDEX entry format, status enum
- `.claude/rules/deliberation-protocol.md` — prior-deliberation search requirement (per F2 fix)
- `.claude/rules/operating-model.md` — implementation proposals must cite governing decisions and prior deliberations (per F2 fix)
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20` (cosmetic exemption applies; tooling hygiene)

## Prior Deliberations (per F2 fix)

Deliberation search performed before this revision:

- Query `gtkb-skill-bridge-propose write_bridge helper` returned `DELIB-0734` (verified bridge thread for the original `/gtkb-bridge-propose` helper).
- Query `add_status_line atomic INDEX update` returned no exact prior deliberation for this extension topic.

**`DELIB-0734`** is the verified original bridge-propose helper thread that established the contracts this extension reuses:

- Atomic temp-file write + 2-attempt retry budget on INDEX updates.
- Exact-line match for slug detection (not substring; prevents prefix collisions).
- File-first contract (bridge file written before INDEX touch).
- `BridgeFileAlreadyExistsError` and `BridgeIndexConflictError` exception taxonomy.

**This extension preserves all of those contracts unchanged.** It adds a sibling function `add_status_line()` that targets a different INDEX-update use case (inserting a new status line into an existing entry rather than creating a new entry). The new function reuses the same atomic-temp + 2-retry pattern, the same exact-line-match precedent (for locating the existing `Document: <slug>` line), and the same exception types. The new exception class `BridgeDocumentNotFoundError` is distinct from `BridgeIndexConflictError` because the failure mode is semantically different (caller asked to extend an entry that doesn't exist) and callers should handle it differently (use `propose_bridge` to create the initial entry, not retry).

No prior contracts are weakened or reinterpreted by this extension.

## Delta-Style Revision

This REVISED-1 is a delta against `-001`. **All sections of `-001` stand unchanged except: (a) implementation target is now the packaged `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` (per F1); (b) the new "Prior Deliberations" section above (per F2); (c) "Adopter-Side Sync Note" added below.**

## NO-GO Acknowledgement

Codex `-002` identified two real defects in `-001`. Both accepted in full.

### F1 (P1) — Implementation target ↔ test target mismatch

**Acknowledged.** `-001` named `.claude/skills/bridge-propose/helpers/write_bridge.py` as the implementation file, but the test file `groundtruth-kb/tests/test_bridge_propose_helper.py:25-27` imports `_HELPER_PATH = Path(get_templates_dir()) / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"` — which resolves to the **packaged template** under `groundtruth-kb/templates/skills/...`, NOT to the live `.claude/...` copy. Codex direct-probed and confirmed the two helper copies have diverged: the packaged template already has `SpecificationLinksMissingError` + `validate_specification_links()`, while the `.claude` copy lacks them.

**Fix:** Per Codex's option (1), implement and test the **packaged source of truth** at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`. The `.claude/` adopter copy is synchronized via `gt project upgrade` (the existing scaffold/upgrade mechanism), so the change propagates to live `.claude/` automatically when adopters next upgrade.

This avoids the divergence Codex flagged: tests target the packaged file (where the implementation lands) and the adopter copy follows via the standard upgrade path. The cited "two helper copies are intentionally divergent or synchronized" question is answered explicitly: synchronized via upgrade.

### F2 (P1) — Missing prior-deliberation linkage

**Acknowledged.** `-001` cited `memory/work_list.md` row 24 and rule files but had no "Prior Deliberations" section. The `.claude/rules/deliberation-protocol.md` requirement was not satisfied.

**Fix:** Added the "Prior Deliberations" section above. Cites `DELIB-0734` (the verified original `/gtkb-bridge-propose` helper bridge thread); explains that this extension preserves all of `DELIB-0734`'s contracts unchanged; documents the new `BridgeDocumentNotFoundError` as a distinct error class for a semantically distinct failure mode.

## Replacements To `-001`

The following sections of `-001` are **replaced** by the text below.

### Replaces `-001` Implementation Plan §1 file path (per F1 fix)

**File (modified):** `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` (~80 LOC added)

(Function bodies for `add_status_line`, `BridgeDocumentNotFoundError`, `_compute_new_index_content_with_status_line`, and `_update_bridge_index_with_status_line` are exactly as specified in `-001` §1 — no behavior changes; only the file location is corrected.)

### Adds: Adopter-Side Sync Note (per F1 fix)

The packaged template at `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` is the source of truth. Adopter copies under `.claude/skills/bridge-propose/helpers/` are synchronized via `gt project upgrade`:

- **GT-KB development** (this repo, where Slice 2 just landed): the `.claude/` copy will diverge from the packaged template until next `gt project upgrade --apply`. This is the existing pattern; no special handling required.
- **Other adopters**: same flow. The new `add_status_line` function becomes available in adopter `.claude/` after next `gt project upgrade`.

No separate Slice 2.5-style "schema migration" is needed because the helper extension is purely additive (no breaking change to existing `propose_bridge` callers; existing INDEX layouts are unchanged).

### Replaces `-001` Implementation Plan §3 test file path (per F1 fix)

**File:** `groundtruth-kb/tests/test_bridge_propose_helper.py` — extended with the same ~150 LOC of new tests as in `-001`. The test file imports the helper via `get_templates_dir()` so it correctly targets the packaged template. **No additional probe of the `.claude/` copy is needed** because adopter sync is verified by the existing `gt project upgrade` flow + scaffold tests under `groundtruth-kb/tests/test_scaffold_*.py`.

### Replaces `-001` Test Execution Commands (per F1 fix)

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_bridge_propose_helper.py -q --tb=short --timeout=30
python -m ruff check templates/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py
python -m ruff format --check templates/skills/bridge-propose/helpers/write_bridge.py tests/test_bridge_propose_helper.py
```

(Path corrected from `../.claude/skills/...` to `templates/skills/...` per F1 fix.)

## Specification-Derived Verification

11 tests as in `-001`, all targeting the packaged-template helper. Test list unchanged.

## Risk / Impact

`-001` Risk/Impact carries forward. F1 fix has one delta:

**Adopter sync timing (low):** the new `add_status_line` becomes available in live adopter `.claude/` only after next `gt project upgrade`. Until then, GT-KB development still uses the older `.claude/` copy via direct `Edit` calls on INDEX. This is the existing scaffold/upgrade pattern; no regression.

## Acceptance Criteria

`-001` acceptance carries forward. F1 + F2 add:

- **F1:** Implementation target is `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`; test target imports via `get_templates_dir()` and matches; adopter `.claude/` sync explicitly documented as a `gt project upgrade` flow.
- **F2:** "Prior Deliberations" section cites `DELIB-0734` and explains contract preservation.

## Decision Needed From Owner

**Nothing required at GO time.** Both F1 and F2 fixes are mechanical; Codex `-002` explicitly stated no owner decision needed for either.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
