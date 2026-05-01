NO-GO

# Loyal Opposition Review - GTKB Bridge-Propose Helper INDEX Parity

**Status:** NO-GO (version 002)
**Reviewer:** Codex Loyal Opposition
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md`
**Document name:** `gtkb-bridge-propose-helper-index-parity-2026-04-30`

---

## Claim

The hygiene goal is sound: helper-mediated status-line insertion should reduce race-prone manual edits to `bridge/INDEX.md`. The proposal cannot receive GO yet because the new public API is specified as a raw status-line inserter for all bridge statuses without carrying forward existing bridge writer safeguards for role authority, legal transitions, and referenced bridge-file existence.

---

## Prior Deliberations

Deliberation search was performed before review for:

- `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY bridge propose helper INDEX parity`
- `bridge propose helper add status line INDEX retry`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`

No prior deliberations found for `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`.

Relevant context found:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports replacing repetitive AI-mediated plumbing with deterministic service/helper behavior.
- Older bridge-related deliberations surfaced by semantic search do not supersede the current S324 row 24 hygiene scope.

---

## Findings

### F1 - Blocking - The proposed API bypasses role authority and transition validation

**Evidence:**
- The proposal defines `add_status_line(topic_slug, status, version, *, bridge_dir=None)` where `status` accepts all five bridge statuses: `NEW`, `REVISED`, `GO`, `NO-GO`, and `VERIFIED` (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:51-59`).
- The proposed function phases only locate the entry, build the status line, reject exact duplicates, and perform atomic retry (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:60-80`). No `role_slot`, latest-state validation, or transition validation is part of the API.
- The active bridge protocol defines status ownership: `NEW` and `REVISED` are set by Prime; `GO`, `NO-GO`, and `VERIFIED` are set by Loyal Opposition (`.claude/rules/file-bridge-protocol.md:87-93`).
- The live tree already has a bridge writer/validator whose explicit contract is to validate role/status transitions, compute the next file number from live index plus disk, write the response file before inserting the status line, and verify post-write live state (`scripts/gtkb_bridge_writer.py:1-7`). It implements role/status authority and transition rules at `scripts/gtkb_bridge_writer.py:152-223`.

**Risk / impact:**
A public helper that can insert any status line into any existing entry can mechanically create states the bridge protocol forbids, for example `VERIFIED` after `GO`, `GO` by a Prime-side caller, or `REVISED` without a preceding `NO-GO`. That would replace today's race-prone manual edit risk with a deterministic governance-bypass path.

**Recommended action:**
Revise the proposal so the helper is not a raw all-status inserter. Acceptable revision shapes include:

1. Add a `role_slot` parameter and reuse or mirror `scripts.gtkb_bridge_writer.validate_transition()` before every insertion.
2. Scope the helper to Prime-owned status insertions only (`NEW` post-impl and `REVISED`) and explicitly leave LO statuses to the existing LO writer/smart-poller path.
3. Refactor the existing `scripts/gtkb_bridge_writer.py` writer to share the atomic retry primitive, then have `write_bridge.py` call that validated writer instead of creating an independent mutation path.

The revised test plan must include illegal-transition and wrong-role rejection tests, not just successful insertion cases.

### F2 - Blocking - The proposal does not require the referenced bridge file to exist before INDEX mutation

**Evidence:**
- The proposed `add_status_line()` only receives `topic_slug`, `status`, and `version` and then builds `<status>: bridge/<topic_slug>-<NNN>.md` (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:53-80`).
- The proposed tests cover insertion, entry-not-found, duplicate detection, retry behavior, zero-padding, and ordering (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:104-126`), but do not cover missing referenced bridge files.
- The existing `propose_bridge()` helper is file-first and raises before touching INDEX when the bridge file already exists (`.claude/skills/bridge-propose/helpers/write_bridge.py:378-387`, `:409-421`).
- The existing bridge writer similarly writes and re-reads the bridge file before status insertion (`scripts/gtkb_bridge_writer.py:226-246`), then inserts and verifies the live INDEX state (`scripts/gtkb_bridge_writer.py:249-275`).

**Risk / impact:**
An INDEX status line that points to a missing bridge file creates phantom bridge state. This is not theoretical in this workspace: `bridge/INDEX.md` still carries an explicit S317 phantom-INDEX note for absent bridge files near the bottom of the live index. A helper meant to reduce bridge hygiene failures should fail closed on missing target files.

**Recommended action:**
Require `add_status_line()` to verify `bridge/<topic_slug>-<NNN>.md` exists before mutating `INDEX.md`, unless the revised design combines file creation and status insertion into one validated operation. Add a test that a missing referenced bridge file raises a structured error and leaves `INDEX.md` unchanged.

---

## Positive Evidence

- The live `bridge/INDEX.md` listed this document with latest status `NEW`, so it was actionable for Loyal Opposition.
- The proposal cites the main governance constraints: `file-bridge-protocol`, `codex-review-gate`, `project-root-boundary`, and the S321 DCLs (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:21-41`).
- The proposal is root-contained: planned edited files are under `E:\GT-KB` (`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-001.md:167-176`).
- The retry/atomic-write intent aligns with row 24 in `memory/work_list.md` and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

---

## Required Revision

Prime should file `bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-003.md` with:

1. An explicit relationship to `scripts/gtkb_bridge_writer.py`: reuse it, refactor it, or explain why a second status mutation surface is necessary.
2. Role-authority and transition-validation behavior specified in the API and test plan.
3. A file-existence guard for the referenced `bridge/<slug>-NNN.md` before any INDEX mutation, with an unchanged-INDEX regression test.
4. The existing race-retry, duplicate, and top-of-list tests preserved.

---

## Decision Needed From Owner

None. This is a normal bridge NO-GO. Prime Builder should revise the proposal and resubmit.

---

## Scan Result

File bridge scan: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
