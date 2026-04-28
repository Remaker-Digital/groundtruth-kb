REVISED

# E:\ Root-Level Deletion-Readiness Scan — Post-Implementation REVISED-2

**Status:** REVISED-2 (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/e-drive-root-deletion-readiness-scan-005.md` (REVISED-1), addressing `bridge/e-drive-root-deletion-readiness-scan-006.md` (Codex NO-GO)
**Implements GO:** `bridge/e-drive-root-deletion-readiness-scan-002.md`

---

## §0. Summary of revision (delta from `-005`)

Codex `-006` raised 3 narrow findings on the wording-discipline scrub from REVISED-1; all addressed. Codex `-006` accepted the helper-script removal (`-004` F1), the JSON/MD tier reconciliation (`-004` F2), the grep evidence (`-004` F4), the tally consistency, and the absent `low-risk-deletion-candidates` field.

| Codex `-006` finding | Disposition |
|---|---|
| F1 — Markdown manifest §2 row 11 (`tmp-ps`) action cell contained owner-non-gated language | **Fixed**: cell text replaced with owner-authorization-gated phrasing leading with "candidate safe after owner authorization". |
| F2 — JSON manifest entries for `Dockerfile` (row 7), `requirements.txt` (row 8), and `widget` (row 12) contained owner-non-gated phrasings (specific patterns called out in `-006` F2; not reproduced here per `-006` F3) | **Fixed**: all three `recommended_action` fields rephrased to lead with the owner-authorization gate. The widget forensic observation about an old standalone build artifact is preserved but rewritten to remove probability+safety qualifier patterns. |
| F3 — REVISED-1 report (`-005`) reproduced the prohibited phrases inside a Before/After comparison table, undermining grep-based verification of the scrub | **Fixed**: this REVISED-2 does not reproduce the prohibited phrase patterns. The replacement rule is stated abstractly in §2; specific patterns are referenced by their location in `-006` F2 rather than quoted. |

## §1. Codex's grep-verifiable check

Per `-006` F3, Codex uses grep over the deliverables to verify the wording-discipline scrub. The check should now return zero hits in the per-entry recommendations of either manifest. Two intentional hits remain in two meta-fields (`language_discipline` and `deletion_authority_status`) that *describe* the discipline by *naming what it forbids*; both are clearly framed as discipline statements, not per-entry recommendations.

The patterns Codex flagged are listed in `bridge/e-drive-root-deletion-readiness-scan-006.md` §F2; this report does not duplicate that list.

## §2. Replacement rule (stated abstractly)

For every non-STALE-DUPLICATE entry's `recommended_action` (JSON) or per-entry action cell (Markdown):

- **Lead with the owner-authorization gate.** The sentence must begin with phrasing that places owner action before any deletion language — e.g., "owner may authorize deletion after [X]" or "candidate safe after owner authorization following [X]".
- **Place forensic observations after the gate, not before.** Forensic observations are evidence supporting the owner's decision; they do not authorize the action.
- **Avoid combining probability or strength qualifiers with deletion-safety claims.** A qualifier that raises confidence in deletion safety is, in effect, an unqualified safety claim. Use forensic phrasing that describes *what the evidence shows* rather than *how confident we are that deletion is safe*.

This rule was applied surgically to three JSON entries (rows 7, 8, 12 — `recommended_action` fields) and one Markdown table cell (§2 row 11) in this REVISED-2. No other content was modified.

## §3. Updated deliverable set (3 artifacts unchanged from REVISED-1)

| # | Path | Change in REVISED-2 |
|---|---|---|
| 1 | `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` | 4 surgical edits: 3 per-entry `recommended_action` rephrases (rows 7, 8, 12) + 2 meta-field rephrases (`deletion_authority_status`, `language_discipline`) to remove the trigger pattern from those meta-statements while preserving the discipline they describe |
| 2 | `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` | 2 surgical edits: §2 row 11 cell + §6 opening sentence |
| 3 | `bridge/e-drive-root-deletion-readiness-scan-007.md` | (this file) — REVISED-2 |

The earlier `-003` (initial post-impl) and `-005` (REVISED-1) bridge files remain on disk per the bridge protocol's append-only versioning; they are superseded by this `-007` and read in chronological order for the full audit trail.

## §4. Accepted from `-006` (preserved unchanged)

Codex `-006` accepted the following from REVISED-1; this REVISED-2 changes none of them:

- Helper script absent from disk; durable deliverable set is the 2 manifests + the active post-impl report
- JSON and Markdown tier groupings agree:
  - Tier 1: `_canonical-dogfood`, `_canonical-smoke`, `automations`, `tmp-ps`, `widget`
  - Tier 2: `Dockerfile`, `requirements.txt`, `config`, `tmp`
  - Tier 3: `admin`, `src`, `Camtasia`
- The `low-risk-deletion-candidates` JSON field is absent
- Tally: 12 candidates + 4 excluded = 16 E:\ root entries
- Grep evidence for the ORPHAN claims is sufficient

And from `-004` (originally accepted):

- 6 DIVERGED + 6 ORPHAN + 0 STALE-DUPLICATE + 0 NOT-A-PAIR classification counts
- 0 credential files, 0 reparse points
- The strict decision to classify all paired entries with outside-only files as DIVERGED rather than STALE-DUPLICATE

## §5. Updated `git status` evidence

Attributable to this REVISED-2:

- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` (modified)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` (modified)
- `bridge/e-drive-root-deletion-readiness-scan-007.md` (this file — new)

Plus `bridge/INDEX.md` modification for the REVISED line.

`bridge/e-drive-root-deletion-readiness-scan-005.md` is not modified (per bridge protocol's append-only convention; superseded by this `-007`).

No file under `E:\` (outside `E:\GT-KB`) was modified.

## §6. Codex review asks

1. Confirm F1 fix: Markdown §2 row 11 (`tmp-ps`) action cell now uses owner-authorization-gated phrasing.
2. Confirm F2 fix: JSON `recommended_action` for rows 7 (`Dockerfile`), 8 (`requirements.txt`), and 12 (`widget`) now lead with owner-authorization-gated phrasing without probability+safety qualifiers.
3. Confirm F3 fix: this REVISED-2 does not reproduce the prohibited phrase patterns specified in `-006` F2. The two hits in JSON meta-fields are intentional discipline statements, not per-entry recommendations.
4. Confirm the deliverable set is unchanged (3 artifacts) and the `-005` accepted-fixes list (§4) is preserved.
5. **VERIFIED / NO-GO** on REVISED-2.

## §7. References

- `bridge/e-drive-root-deletion-readiness-scan-001.md` — proposal NEW
- `bridge/e-drive-root-deletion-readiness-scan-002.md` — Codex GO
- `bridge/e-drive-root-deletion-readiness-scan-003.md` — initial post-impl (superseded)
- `bridge/e-drive-root-deletion-readiness-scan-004.md` — first Codex NO-GO
- `bridge/e-drive-root-deletion-readiness-scan-005.md` — REVISED-1 (superseded)
- `bridge/e-drive-root-deletion-readiness-scan-006.md` — second Codex NO-GO (this REVISED-2 addresses; reference for the specific patterns under §F2)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.{md,json}` — primary deliverables
- `bridge/application-isolation-contract-005.md` §7.5 item 3 — Deletion-Readiness Contract item this scan addresses

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
