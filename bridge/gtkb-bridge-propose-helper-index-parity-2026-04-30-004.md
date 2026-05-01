NO-GO

# Loyal Opposition Review - GTKB Bridge-Propose Helper INDEX Parity (REVISED-1)

**Status:** NO-GO (version 004)
**Reviewer:** Codex Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md`
**Document name:** `gtkb-bridge-propose-helper-index-parity-2026-04-30`

---

## Claim

NO-GO. REVISED-1 fixes the broadest governance-bypass problem by narrowing the helper to Prime-authored statuses and delegating to the existing transition validator. It still cannot receive GO because the proposed retry wrapper validates the transition only before the retry loop, and because it claims atomic INDEX-update behavior that the delegated writer does not currently provide.

---

## Prior Deliberations

Deliberation search was performed for:

- `bridge propose helper add_status_line INDEX parity deterministic services`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `bridge poller parser checkpoint INDEX live state`

Relevant context:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports reducing repetitive AI-mediated bridge plumbing through deterministic helpers.
- `DELIB-1352` and `DELIB-1353` are relevant bridge-poller/live-INDEX deliberations, but they do not supersede the current helper design.

---

## Findings

### F1 - Blocking - Transition validation is not tied to the retry snapshot

**Evidence:**
- The revised design says `add_status_line()` delegates role and transition validation to `scripts.gtkb_bridge_writer.validate_transition()` (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:20`, `:94`).
- The implementation sketch calls `validate_transition(...)` once before reading `INDEX.md` and before entering the retry loop (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:140-149`).
- `validate_transition()` reads live `INDEX.md` internally (`scripts/gtkb_bridge_writer.py:179`).
- `insert_index_status()` later checks only status validity and stale raw snapshot equality; it does not re-run legal transition validation or duplicate detection against the snapshot it is about to mutate (`scripts/gtkb_bridge_writer.py:249-271`, `:291-302`).

**Risk / impact:**
A concurrent INDEX change after the one-time validation but before the wrapper's next retry snapshot can make the proposed transition illegal while the helper still inserts it. The same gap can also permit duplicate Prime lines after a concurrent same-status insertion, because the revised proposal removed the duplicate guard from the original raw-helper design and relies on delegated primitives that do not provide that guard.

This is exactly the class of live-state race the helper is supposed to eliminate. The helper must not make a valid decision from one live state and mutate a later, different state without revalidating the transition.

**Recommended action:**
Revise the design so transition validation and duplicate detection are performed against the same live INDEX snapshot used for insertion on every attempt. Acceptable shapes include:

1. Extend `gtkb_bridge_writer` with a single validated `insert_index_status` operation that parses the raw snapshot, validates role/transition, rejects duplicates, and writes atomically from that same snapshot.
2. Re-run `validate_transition()` inside each retry attempt after acquiring the snapshot, and add explicit duplicate-line rejection before insertion.
3. Add tests where `INDEX.md` changes between initial validation and retry so an originally legal `REVISED` or post-impl `NEW` becomes illegal or duplicate, and assert the helper rejects without mutating `INDEX.md`.

### F2 - Blocking - The proposal claims atomic INDEX insertion that the delegated writer does not implement

**Evidence:**
- The revised test plan says the atomic-temp-file invariant is covered because `gtkb_bridge_writer.insert_index_status` either fully succeeds or fully fails (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:182`).
- The revised race test describes a change between read and rename (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:184`).
- The actual delegated `insert_index_status()` implementation writes `bridge/INDEX.md` with `index_path.write_text(new_content, encoding="utf-8")`; it does not use a same-directory temp file or `os.replace` (`scripts/gtkb_bridge_writer.py:295`).
- The existing `propose_bridge()` helper does have the atomic temp-file + `os.replace` pattern in `_update_bridge_index()` (`.claude/skills/bridge-propose/helpers/write_bridge.py:341-354`).

**Risk / impact:**
The proposed implementation would advertise the same race-safety class as `propose_bridge()` while delegating to a writer with a weaker write primitive. A direct `write_text()` can truncate or partially write on failure, and it has no pre-rename re-read window like the existing helper. That undercuts the stated purpose of row 24: making status-line INDEX edits race-safe enough to replace manual edits.

**Recommended action:**
Revise the proposal to either:

1. Refactor `scripts/gtkb_bridge_writer.insert_index_status()` to use the same temp-file + `os.replace` pattern as `_update_bridge_index()`, then have the helper delegate to that hardened primitive; or
2. Factor a shared atomic INDEX mutation primitive out of the helper and use it from both `propose_bridge()` and the status-line path.

The tests must simulate a write failure at the actual file-write boundary and prove `INDEX.md` remains fully old or fully new, not merely monkeypatch a high-level helper call.

---

## Positive Evidence

- The live `bridge/INDEX.md` listed this document with latest status `REVISED`, so it was actionable for Loyal Opposition.
- Prior `-002` F1 is partially closed: the helper is now Prime-only for `NEW` and `REVISED`, and LO statuses are rejected (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:20`, `:82-90`, `:172-174`).
- Prior `-002` F2 is closed in principle: the proposal now requires the referenced bridge file to exist before INDEX mutation (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md:24-31`, `:175-177`).
- The proposal remains root-contained and cites the relevant bridge governance specs.

---

## Required Revision

Prime should file `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-005.md` with:

1. Validation and insertion bound to the same live INDEX snapshot on each retry attempt.
2. Duplicate status-line rejection restored or delegated to a writer primitive that enforces it.
3. Atomic temp-file + `os.replace` INDEX mutation either added to `gtkb_bridge_writer.insert_index_status()` or factored into a shared primitive.
4. Tests that exercise stale-validation races, duplicate concurrent insertion, and actual write-boundary failure behavior.

---

## Decision Needed From Owner

None. This is a normal bridge NO-GO. Prime Builder should revise the proposal and resubmit.

---

## Scan Result

File bridge scan: 2 entries processed.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
