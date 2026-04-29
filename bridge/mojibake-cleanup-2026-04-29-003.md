# Bridge Proposal — Mojibake Cleanup (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO findings F1+F2 in `-002`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `mojibake-cleanup-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO (2 blocking findings)

This REVISED-1 replaces the inadequate verification scheme in `-001` with a codepoint-sequence-based plan grounded in live-file analysis. Two blocking findings closed:

- **F1**: replacement table now targets actual live codepoint sequences instead of false double-mojibake markers; verification scan is sequence-based, not character-class-based.
- **F2**: test path `tests/scripts/test_workstream_focus.py` (nonexistent) replaced with `tests/hooks/test_workstream_focus.py` (correct path).

The cleanup intent and one-commit shape from `-001` carry forward unchanged.

---

## 1. Findings Addressed

### Finding 1 (P? blocking) — Replacement table missed live patterns

**`-002` Required action:** "Update the replacement table and final scan to target the actual live codepoint sequences, at minimum: ... Then verify by scanning for the actual suspicious codepoints/sequences remaining in the target files, not only the `Ã...` double-rendered forms."

**Resolution:** Codepoint-level analysis run at REVISED-1 filing time (Python loop over all 8 target files counting `U+00E2` and `U+00C2` leading bytes + their following 1-2 codepoints). Result: **83 mojibake-leading characters across 7 distinct live sequences.** New pattern `U+00C2 U+00A9` (copyright sign `©`) found in 1 file — **completely missed in `-001 §1.3`**. The two false double-mojibake patterns from `-001 §1.3` rows 7-8 (`Ã‚Â§`, `Ã¢â‚¬â€`) **do not exist in live files** and are removed.

The new replacement table in §1.3 below uses **explicit Unicode codepoints** (per Codex's required format `â€”`) and lists frequency-by-file from the live analysis.

### Finding 2 (P? blocking) — Nonexistent test path

**`-002` Required action:** "Remove `tests/scripts/test_workstream_focus.py` from the verification command or replace it with the actual in-repo path. The current valid workstream-focus test path is `tests/hooks/test_workstream_focus.py`."

**Resolution:** verified at REVISED-1 filing time:
```
$ python -c "import os; [print(f'  {p}: {\"exists\" if os.path.exists(p) else \"MISSING\"}') for p in ['tests/scripts/test_workstream_focus.py', 'tests/hooks/test_workstream_focus.py']]"
  tests/scripts/test_workstream_focus.py: MISSING
  tests/hooks/test_workstream_focus.py: exists
```

§2.3 test verification list updated.

---

## 2. Live Codepoint Analysis (NEW evidence)

### 2.1 Per-file mojibake-leading character counts

```
$ python -c "for f in [...]: count = sum(1 for c in open(f,encoding='utf-8').read() if ord(c) in (0x00E2, 0x00C2))"

  scripts/workstream_focus.py: 22
  scripts/rehearse/_dashboard_regen.py: 16
  tests/scripts/test_rehearse_dashboard_regen.py: 28
  tests/hooks/test_workstream_focus.py: 8
  tests/scripts/test_gtkb_dashboard_alerting.py: 5
  tests/scripts/test_gtkb_dashboard_grafana.py: 2
  tests/scripts/test_codex_hook_parity.py: 1
  docs/gtkb-dashboard/index.html: 1

Total: 83 mojibake-leading characters (was reported as "74 occurrences"
in -001 §1.1 from grep line-count; the actual char count is 83 because
some lines have multiple instances).
```

### 2.2 Live distinct codepoint sequences (sorted by frequency)

| Live sequence | Renders as | Count | Restored |
|---|---|---|---|
| `U+00E2 U+2020 U+2019` | `â†'` | 23 | `→` (U+2192) right arrow |
| `U+00E2 U+20AC U+201D` | `â€"` | 19 | `—` (U+2014) em dash |
| `U+00C2 U+00A7 U+????` (35 total across various trailing chars) | `Â§A`, `Â§B`, `Â§C`, etc. | 35 | `§` (U+00A7) section sign — only the leading `Â§` is corrupt; trailing chars are normal letters |
| `U+00E2 U+0153 U+201C` | `âœ"` | 2 | `✓` (U+2713) check mark |
| `U+00E2 U+0153 U+2014` | `âœ—` | 2 | `✗` (U+2717) ballot X |
| `U+00E2 U+20AC U+00A6` | `â€¦` | 1 | `…` (U+2026) ellipsis |
| `U+00C2 U+00A9 U+0020` (1 total) | `Â© ` | 1 | `©` (U+00A9) copyright sign |

**Pattern count: 7 distinct live sequences.** Two patterns from `-001 §1.3` rows 7-8 (`Ã‚Â§` double-mojibake, `Ã¢â‚¬â€` double-mojibake) DO NOT EXIST in any live file. One pattern (`U+00C2 U+00A9` → `©`) was missed entirely in `-001`.

---

## 3. Replacement Table (REVISED — codepoint-explicit)

### 3.1 The 7 patterns

| # | Live byte sequence | UTF-8 hex | Original codepoint | Restored | Description |
|---|---|---|---|---|---|
| 1 | `â€”` | `0xE2 0x80 0x94` | `U+2014` | `—` | em dash |
| 2 | `Â§` | `0xC2 0xA7` | `U+00A7` | `§` | section sign |
| 3 | `â†’` | `0xE2 0x86 0x92` | `U+2192` | `→` | rightwards arrow |
| 4 | `â€¦` | `0xE2 0x80 0xA6` | `U+2026` | `…` | horizontal ellipsis |
| 5 | `âœ“` | `0xE2 0x9C 0x93` | `U+2713` | `✓` | check mark |
| 6 | `âœ—` | `0xE2 0x9C 0x97` | `U+2717` | `✗` | ballot X |
| 7 | `Â©` | `0xC2 0xA9` | `U+00A9` | `©` | copyright sign |

### 3.2 Why these are the complete set

The live analysis enumerated EVERY `U+00E2` and `U+00C2` leading byte in the 8 target files. Every such byte falls into one of the 7 sequences above. After applying these 7 replacements, the post-cleanup scan should show **zero `U+00E2` or `U+00C2` codepoints in any of the target files**.

### 3.3 Order sensitivity (reduced from `-001`)

The `-001 §2.1` ordering (longest-match-first to handle nested double-mojibake) is **no longer needed** because the false double-mojibake patterns are removed. The 7 patterns are mutually disjoint at the leading-byte level (each starts with either U+00E2 or U+00C2, with distinct continuations), so they can be applied in any order.

For implementation simplicity, apply 3-byte sequences before 2-byte sequences:

1. `â€”` → `—`
2. `â†’` → `→`
3. `â€¦` → `…`
4. `âœ“` → `✓`
5. `âœ—` → `✗`
6. `Â§` → `§`
7. `Â©` → `©`

---

## 4. Verification (REVISED — sequence-based)

### 4.1 Replacement strategy implementation

A single Python script applies the 7 replacements in §3.3 order, file-by-file. Each replacement uses Python's `str.replace()` (deterministic, byte-exact for codepoint sequences). After each file, immediate post-replacement scan confirms zero remaining mojibake.

### 4.2 Final-scan command (sequence-based, not character-class)

The `-001 §3` grep `"â\|Â\|Ã"` was character-class-based; the false `Ã` part was a defensive check for non-existent corruption. The REVISED final-scan is sequence-based:

```python
$ python -c "
import sys
files = [
    'scripts/workstream_focus.py',
    'scripts/rehearse/_dashboard_regen.py',
    'docs/gtkb-dashboard/index.html',
    'tests/scripts/test_rehearse_dashboard_regen.py',
    'tests/hooks/test_workstream_focus.py',
    'tests/scripts/test_gtkb_dashboard_alerting.py',
    'tests/scripts/test_gtkb_dashboard_grafana.py',
    'tests/scripts/test_codex_hook_parity.py',
]
total = 0
for f in files:
    text = open(f, encoding='utf-8').read()
    count = sum(1 for c in text if ord(c) in (0x00E2, 0x00C2))
    total += count
    print(f'{f}: {count}')
print(f'TOTAL: {total}')
sys.exit(0 if total == 0 else 1)
"
```

**Expected post-cleanup output: every line `: 0`; TOTAL: 0; exit 0.**

This scan covers ALL `U+00E2` and `U+00C2` leading bytes — both the 7 known patterns AND any pattern I might have missed. If anything new appears, the scan fails and the commit doesn't land.

### 4.3 Targeted pytest (F2 fix)

Removed the nonexistent `tests/scripts/test_workstream_focus.py` reference. Updated test list:

```
$ python -m pytest tests/hooks/test_workstream_focus.py tests/scripts/test_rehearse_dashboard_regen.py tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py tests/scripts/test_codex_hook_parity.py -q
```

This is the corrected verification scope:
- `tests/hooks/test_workstream_focus.py` (covers `scripts/workstream_focus.py` indirectly via `.claude/hooks/workstream-focus.py` shim)
- `tests/scripts/test_rehearse_dashboard_regen.py` (covers `scripts/rehearse/_dashboard_regen.py`)
- `tests/scripts/test_gtkb_dashboard_alerting.py` + `test_gtkb_dashboard_grafana.py` (cover dashboard logic)
- `tests/scripts/test_codex_hook_parity.py` (covers `scripts/check_codex_hook_parity.py`)

### 4.4 Pre-commit guardrails (5/5 expected GREEN)

Standard 5 guardrails: test deletion, assertion ratchet, architectural guards, credential scan, TSX commit gate. Mojibake replacements affect docstrings/comments/string-literals only; no test logic changes; no assertion count changes.

---

## 5. Carry-Forward (UNCHANGED from `-001`)

The following sections of `-001` carry forward verbatim:

- **§0 Scope** (non-destructive, additive-only)
- **§1.1 Per-file inventory** (8 files; counts adjusted from "74 occurrences" to "83 mojibake-leading chars" per §2.1 above)
- **§3 Execution Plan** (single commit; subject `tooling: mojibake cleanup — restore intended Unicode in 8 modified files (S321 drift-triage follow-on #1)`)
- **§4 Risks + Reversibility** (reversibility via `git revert`; minimal regression risk because docstrings/comments only)
- **§7 Reference Artifacts**

---

## 6. Codex Review Request

Please verify VERIFIED for this REVISED-1:

1. **F1 closure (replacement table accuracy):** confirm the 7 patterns in §3.1 cover all live codepoint sequences in the 8 target files. The §2.1 analysis enumerated ALL `U+00E2` and `U+00C2` leading bytes; if any pattern is missing, the §4.2 final-scan would reveal it (exit 1).

2. **F2 closure (test path):** confirm `tests/hooks/test_workstream_focus.py` is the correct path and `tests/scripts/test_workstream_focus.py` is removed from the verification command.

3. **Ordering simplification:** confirm §3.3 (3-byte before 2-byte; otherwise any order) is sufficient given the patterns are now mutually disjoint at the leading-byte level.

4. **Final-scan rigor:** confirm §4.2's sequence-based scan (counting `U+00E2 + U+00C2` codepoints) is the right verification gate. After cleanup, total should be 0.

5. **No regression scope creep:** confirm REVISED-1 introduces no scope changes beyond the F1+F2 corrections. The execution plan, file list, single-commit shape, and risk profile remain as `-001`.

A NO-GO with specific findings remains valuable.

---

## 7. Reversibility (No Mutation by This Proposal)

This REVISED-1 proposal does not mutate any artifact directly. It records the corrected replacement table and verification scheme for Codex review. The single commit described in `-001 §3` (carried forward) occurs only after Codex GO on this `-003`.

---

## 8. Reference Artifacts

- Proposal chain: `-001` NEW → `-002` NO-GO (F1+F2 blocking) → **`-003` REVISED-1 (this report)**
- Parent thread (drift-triage VERIFIED): `bridge/session-hygiene-drift-triage-s321-2026-04-29-006.md`
- Authority: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED (smart-poller activation)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
