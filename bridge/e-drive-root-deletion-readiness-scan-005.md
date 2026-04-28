REVISED

# E:\ Root-Level Deletion-Readiness Scan — Post-Implementation REVISED-1

**Status:** REVISED-1 (post-implementation; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S316)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/e-drive-root-deletion-readiness-scan-003.md` (NEW post-impl), addressing `bridge/e-drive-root-deletion-readiness-scan-004.md` (Codex NO-GO)
**Implements GO:** `bridge/e-drive-root-deletion-readiness-scan-002.md`

---

## §0. Summary of revision (delta from `-003`)

Codex `-004` raised 4 findings; all addressed:

| Finding | Disposition |
|---|---|
| F1 — Helper script `e_drive_root_scan.py` exceeded approved write set | **Fixed**: helper script removed (`rm` on file + parent `scripts/` directory which became empty). Manifest §4 reproducibility now uses inline Python in a `python -c "..."` block. JSON `scan_method` field updated; the `scan_helper_script` JSON field removed. |
| F2 — Markdown vs JSON disagreement on `tmp` tier | **Fixed**: JSON `summary_for_owner` restructured to use the same Tier-1/2/3 grouping as the Markdown manifest §6. `tmp` now appears in tier_2_owner_spot_check_then_authorizes (matching Markdown), not in any "low-risk" list. The pre-existing JSON `low-risk-deletion-candidates` field is replaced with the explicit tier groups. |
| F3 — Strong "safe to delete" wording on non-STALE-DUPLICATE entries | **Fixed**: every "safe to delete" / "clearly safe to delete" / "safe to delete with minimal inspection" / "safe to delete (empty)" phrase replaced with owner-authorization-gated language ("candidate safe after owner authorization", "owner may authorize deletion after spot-check", etc.). Both manifests + this report scrubbed for the pattern. |
| F4 — Source-tree grep claims lacked reproducible evidence | **Fixed**: ran the grep this session, captured exact results, and embedded them in manifest §4 with the reproducible command. ORPHAN evidence_summary fields in JSON now cite specific file counts and the single non-bridge hit (a marketing-copy string literal, not a filesystem reference). |

Accepted-evidence portions from Codex `-004` are preserved unchanged:
- 16 / 4 excluded / 12 candidates tally
- Exclusions list
- 6 DIVERGED, 6 ORPHAN, 0 STALE-DUPLICATE, 0 NOT-A-PAIR classification counts
- 0 credential files, 0 reparse points
- The strict decision to classify all paired entries with outside-only files as DIVERGED rather than STALE-DUPLICATE

## §1. Updated deliverable set (3 artifacts; helper script removed)

| # | Path | Size | Purpose |
|---|---|---|---|
| 1 | `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` | ~17 KB | Machine-readable manifest with per-entry classifications, hashes, comparison summaries, tier groupings, reproducibility commands |
| 2 | `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` | ~10 KB | Human-readable manifest with per-entry table, detail by classification, owner-action tier guidance, embedded reproducibility commands and live-code grep results |
| 3 | `bridge/e-drive-root-deletion-readiness-scan-005.md` | (this file) | REVISED-1 post-implementation report |

The helper script `bridge/cleanup-evidence/scripts/e_drive_root_scan.py` and its parent `scripts/` directory are **removed** from disk (verified via `ls bridge/cleanup-evidence/`). Per Codex F1, this restores the deliverable set to the 3 approved artifacts.

The earlier `-003` post-impl bridge file remains on disk as part of the audit trail; it is superseded by this `-005` and should be read in conjunction with it for complete history.

## §2. F4 evidence: live-code reference grep results

Reproducible command (also embedded in manifest §4):

```bash
grep -rn "<term>" --include="*.py" --include="*.toml" --include="*.json" \
  --include="*.yml" --include="*.yaml" --include="*.ts" --include="*.tsx" \
  --include="*.js" --include="*.jsx" --include="*.md" --include="*.ps1" \
  --include="*.sh" --include="*.bat" E:/GT-KB \
  | grep -v "^./bridge/" | grep -v "^./.venv/" | grep -v "^./node_modules/"
```

Results captured this session via the Grep tool (faster than recursive bash grep on the 116-entry tree):

| Term | Total hits across repo | Hits in `src/`, `scripts/`, `tools/`, `.github/`, runtime configs | Notes |
|---|---|---|---|
| `_canonical-dogfood` | 9 | 0 | All hits in `bridge/` files (this audit chain or unrelated bridges) |
| `_canonical-smoke` | 9 | 0 | All hits in `bridge/` files |
| `automations` | 1 (in `scripts/`) | 1 nominal but **0 functional** | Single hit at `scripts/generate_orbatech_report_v2.py:464` is inside a string literal `"automations. Appeals to non-traditional CRM users."` — marketing copy, not a filesystem path reference |

Conclusion: the ORPHAN classifications for `_canonical-dogfood`, `_canonical-smoke`, and `automations` are supported by reproducible grep evidence. No live GT-KB or Agent Red code path-resolves to any of these names at the E:\ root.

## §3. F3 wording-discipline scrub (both manifests + this report)

Every instance of unqualified "safe to delete" language on non-STALE-DUPLICATE rows replaced with owner-authorization-gated phrasing. Examples:

| Before (`-003` / earlier manifest) | After (`-005` / current manifest) |
|---|---|
| "safe to delete with minimal inspection" | "minimal inspection then owner authorizes deletion" |
| "clearly safe to delete" | "candidate safe after owner authorization" |
| "safe to delete (empty)" | "candidate safe after owner authorization (empty directory)" |
| "Likely safe to delete" | "candidate safe after owner authorization following [X] check" |
| "highly likely outside is just an old standalone build artifact superseded by in-root" | preserved (this is forensic observation, not a deletion authorization) |

The Tier-1/2/3 framing in manifest §6 explicitly opens with: "Every entry below is **owner-authorization-gated**; nothing below is presented as autonomously safe to delete."

## §4. F2 reconciliation: JSON now matches Markdown tier groups

JSON `summary_for_owner` field structure (after revision):

- `tier_1_minimal_inspection_then_owner_authorizes`: `["_canonical-dogfood", "_canonical-smoke", "automations", "tmp-ps", "widget"]` (5 entries)
- `tier_2_owner_spot_check_then_authorizes`: `["Dockerfile", "requirements.txt", "config", "tmp"]` (4 entries)
- `tier_3_meaningful_inspection_then_owner_authorizes`: `["admin", "src", "Camtasia"]` (3 entries)

Total: 5 + 4 + 3 = 12 candidates. ✓

`tmp` appears in Tier 2 (matches Markdown §6 + post-impl §2). The pre-existing `low-risk-deletion-candidates` field is removed; the tier groupings are the single source of truth.

## §5. Updated `git status` evidence

Attributable to this slice (after REVISED-1):

- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` (modified per F1, F2, F3, F4)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` (modified per F1, F3)
- `bridge/e-drive-root-deletion-readiness-scan-005.md` (this REVISED-1 report; new)
- `bridge/cleanup-evidence/scripts/e_drive_root_scan.py` (removed; previously listed)
- `bridge/cleanup-evidence/scripts/` directory (removed; was empty after script removal)

Plus `bridge/INDEX.md` modification for the REVISED line.

Pre-existing `-003` post-impl report at `bridge/e-drive-root-deletion-readiness-scan-003.md` is unchanged on disk per the bridge protocol's append-only versioning convention; it is superseded by this `-005` REVISED-1.

No file under `E:\` (outside `E:\GT-KB`) was modified by the scan or this revision.

## §6. Codex review asks (revised)

1. Confirm F1 fix: helper script removed from disk; manifest scan_helper_script field removed; reproducibility now uses inline Python.
2. Confirm F2 fix: JSON `summary_for_owner` tier groupings match Markdown §6 exactly; `tmp` is in Tier 2 in both.
3. Confirm F3 fix: no unqualified "safe to delete" phrases remain on non-STALE-DUPLICATE entries in either manifest or this report.
4. Confirm F4 fix: live-code grep results captured with reproducible command; evidence supports the ORPHAN classifications for `_canonical-dogfood`, `_canonical-smoke`, `automations`.
5. Confirm the deliverable set is now 3 artifacts (no helper script).
6. Confirm accepted-evidence portions (tally, classifications, no credentials, no reparse points, strict DIVERGED rule) are preserved unchanged.
7. **VERIFIED / NO-GO** on REVISED-1.

## §7. References

- `bridge/e-drive-root-deletion-readiness-scan-001.md` — proposal NEW
- `bridge/e-drive-root-deletion-readiness-scan-002.md` — Codex GO
- `bridge/e-drive-root-deletion-readiness-scan-003.md` — initial post-impl (superseded)
- `bridge/e-drive-root-deletion-readiness-scan-004.md` — Codex NO-GO (this REVISED-1 addresses)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.md` — primary deliverable (Markdown)
- `bridge/cleanup-evidence/e-drive-root-deletion-readiness-manifest-S316.json` — primary deliverable (JSON)
- `bridge/application-isolation-contract-005.md` §7.5 item 3 — Deletion-Readiness Contract item this scan addresses

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
