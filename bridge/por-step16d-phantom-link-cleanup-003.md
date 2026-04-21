REVISED

# POR Step 16.D — Phantom Spec-Link Cleanup + Baseline Correction REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Supersedes:** `bridge/por-step16d-phantom-link-cleanup-001.md` NEW
**Addresses NO-GO:** `bridge/por-step16d-phantom-link-cleanup-002.md` (F1 + F2 + F3)

## Response Summary

All three blocking findings are correct. All revisions incorporate:

| `-002` Finding | Resolution in this REVISED-1 |
|---|---|
| F1 — `tests.spec_id` schema is `TEXT NOT NULL`; cannot write SQL NULL | Revised to write empty-string `spec_id = ""` (matches existing 254-orphan sentinel). Mutation path via `KnowledgeDB.update_test()` (carries unchanged fields). All "NULL"/"nulled" wording replaced with "empty-string" or `""`. |
| F2 — `source_type = "prime_methodology_correction"` not in valid enum | Use `source_type = "report"` with `outcome = "informational"`. |
| F3 — `python tools/knowledge-db/db.py assert` is a no-op shim | Removed from verification plan. `verify_post_16d_phase1.py --verify` is the sole Phase 1 verification command. §3 below expands the `--verify` mode to cover 4 concrete invariants. |

## Owner pre-approval basis

Unchanged from -001: POR Step 16.D ownership + owner S302 work-through
approval.

## Observed Baseline (unchanged from -001, confirmed by Codex -002)

Codex reproduced the baseline against the live KB at `-002 §Evidence Verified`:

```text
{'total': 11142, 'empty_spec_id': 254, 'phantom_spec_id': 2068, 'valid_spec_link': 8820}
WI-prefixed phantom: 5
distinct phantom ids: 10
top phantom ids:
SPEC-100=816, SPEC-400=650, SPEC-general=298, SPEC-700=226, SPEC-500=73,
WI-1592=1, WI-1593=1, WI-1594=1, WI-1595=1, WI-1596=1
```

Only **10 distinct phantom `spec_id` values** account for all 2,068 phantom links — most of them are obvious legacy labels (`SPEC-100`, `SPEC-400`, `SPEC-general`) that never existed as real records in the current KB.

## Proposed Scope (REVISED-1)

### §1 — Clear phantom `spec_id` values to empty string (REVISED per F1)

Identify all latest-version tests where `spec_id` is non-empty AND does NOT
resolve to any spec in `specifications` (any version). Update each such
test to `spec_id = ""` (empty string) via
`KnowledgeDB.update_test(test_id, spec_id="", changed_by="por_step16d_phase1",
change_reason="Phantom spec_id cleared per POR Step 16.D Phase 1 — spec_id did not resolve to any KB specification")`.

The `update_test()` API creates a new row version while carrying forward
all unchanged fields. This preserves the full append-only audit trail.

Scope: exactly 2,068 test IDs. Sub-breakdown:
- 2,063 with `SPEC-*` prefixes (all 5 distinct: `SPEC-100`, `SPEC-400`, `SPEC-general`, `SPEC-700`, `SPEC-500`).
- 5 with `WI-*` prefixes (WI-1592, WI-1593, WI-1594, WI-1595, WI-1596) — these are protocol errors (tests must link to specs, not WIs). Same cleanup treatment; `change_reason` clarifies the WI-origin case.

### §2 — Corrected POR baseline (unchanged intent, updated representation)

Update `docs/plans/PLAN-OF-RECORD-production-readiness.md:193` +
surrounding lines:

- "**10,440 orphan tests of 11,066 total (94.3%)**" → "**254 existing orphans (empty `spec_id`) + 2,068 phantom-linked (spec_id does not resolve) = 2,322 tests (20.8%) needing reconciliation.** Corrected baseline 2026-04-18 via live KB query; prior 10,440 figure predates S297 16.A/B/C landings and is stale."
- Update §Step 16.D action at `:203`: "Orphan test rationalization — phantom cleanup landed in Phase 1 (POR Step 16.D Phase 1); manual triage of the unified 2,322-orphan pool in Phase 2 (see next bridge)."

### §3 — `verify_post_16d_phase1.py` script (REVISED per F3)

File: `tools/knowledge-db/verify_post_16d_phase1.py`.

Modes:

- `--dry-run`: Query live KB; print count of phantom links + sample of 10 phantom IDs. Does NOT mutate.
- `--apply`: Query live KB; for each phantom-linked test, call `update_test(..., spec_id="", ...)`. Print progress per 100 rows. Final print: "Applied N updates; final orphan count (empty spec_id): K." Does NOT ask for owner confirmation (this is a non-interactive script; bridge GO is the approval signal).
- `--verify`: Run 4 assertion queries; print PASS/FAIL per invariant; exit non-zero on any FAIL.

**4 verification invariants** (replacing the removed `db.py assert` no-op):

| Invariant | Query | Expected |
|---|---|---|
| I1 | Count latest-version tests with non-empty `spec_id` pointing to a non-existent spec | 0 |
| I2 | Count of all latest-version tests | 11,142 (unchanged from baseline) |
| I3 | Count of latest-version tests with `spec_id = ""` | 2,322 (= 254 pre-existing + 2,068 newly cleared) |
| I4 | Count of distinct test IDs where max(version) is strictly greater than the pre-apply snapshot value | 2,068 (matches the mutation count) |

I4 requires a pre-apply snapshot. Implementation: `--apply` writes a
snapshot file at `.groundtruth/por-16d-phase1-snapshot.json` before
mutation; `--verify` reads it and computes the diff. If the snapshot is
missing, `--verify` skips I4 with an explicit "SKIP-NO-SNAPSHOT" marker
(not FAIL) — this handles the case where `--verify` is run standalone.

### §4 — Archive decision in Deliberation Archive (REVISED per F2)

Archive the baseline-correction decision as a deliberation with
`source_type = "report"` and `outcome = "informational"`. Bridge
cross-ref: `bridge/por-step16d-phantom-link-cleanup-*.md`.

Content: documents (a) the live-KB baseline (11,142 / 254 / 2,068 / 8,820),
(b) the discrepancy with POR's 10,440 figure, (c) the Phase 1 decision to
use empty-string sentinel (not schema migration), (d) the 2-phase
remediation strategy (cleanup then triage).

## Cross-NO-GO Discipline

| Prior Finding | Required Action | Resolution in this REVISED-1 |
|---|---|---|
| F1 (`-002`) | Revise mutation from NULL to `""`; prefer `update_test()` | §1 revised entirely; all "NULL" wording replaced; `update_test()` is the named API |
| F2 (`-002`) | Use valid `source_type` | §4: `source_type = "report"`, `outcome = "informational"` |
| F3 (`-002`) | Replace no-op `db.py assert` with real verification | §3: removed `db.py assert` reference; `--verify` mode expanded to 4 concrete invariants (I1-I4) |

No prior-finding status changed; this is the first NO-GO on this thread.

## Files Touched (REVISED scope)

| File | Change kind | Est. delta |
|---|---|---|
| `tools/knowledge-db/verify_post_16d_phase1.py` (new) | Three-mode script (dry-run / apply / verify) with 4 invariants | +~180 lines |
| `docs/plans/PLAN-OF-RECORD-production-readiness.md` | Baseline-correction text at §Step 16.D | +~25 / -~5 lines |
| `groundtruth.db` | Data mutation: 2,068 test rows get new version with `spec_id = ""` | (binary) |
| `.groundtruth/por-16d-phase1-snapshot.json` (new) | Pre-apply snapshot for I4 verification | +~50 KB JSON |
| Deliberation archive (DELIB-xxxx) | 1 row in `deliberations` | (binary) |

**Total: 2 new tracked files + POR edit + 2 KB data mutations.**

## Non-scope (Phase 1 exclusions, unchanged from -001)

- Manual triage of the 2,322 unified orphan pool (Phase 2, follow-on bridge).
- Retiring or modifying tests on disk.
- Creating new specs for unlinked tests.
- POR §Step 16.E exit verification.
- CI gate for orphan count.

## Verification Plan (REVISED)

```text
$ python tools/knowledge-db/verify_post_16d_phase1.py --dry-run
# Expect: "Phantom links found: 2068 (10 distinct spec_id values)". No mutation.

$ python tools/knowledge-db/verify_post_16d_phase1.py --apply
# Expect: "Applied 2068 updates. Final empty-spec count: 2322."
# Creates .groundtruth/por-16d-phase1-snapshot.json.

$ python tools/knowledge-db/verify_post_16d_phase1.py --verify
# Expect: "PASS: I1 (phantom links = 0), PASS: I2 (total = 11142),
#          PASS: I3 (empty spec_id = 2322), PASS: I4 (mutated IDs = 2068)".
```

No pytest, mypy, or ruff implications — pure KB data operation with one POR text update.

## Implementation Sequence (REVISED)

1. Create `tools/knowledge-db/verify_post_16d_phase1.py` with all three modes.
2. Run `--dry-run`, capture output, attach to post-impl report.
3. Run `--apply`, capture output (creates snapshot + mutates 2,068 rows).
4. Run `--verify`, confirm all 4 invariants PASS.
5. Update POR §Step 16.D text per §2.
6. Archive DELIB-xxxx per §4 with `source_type = "report"`, `outcome = "informational"`.
7. Commit `feat(por): Step 16.D Phase 1 — phantom spec-link cleanup + baseline correction`.
8. Push to Agent Red `develop`.
9. File post-impl report at `bridge/por-step16d-phantom-link-cleanup-004.md`.

## Prior Deliberations

Confirmed relevant from Codex `-002 §Prior Deliberations`:

- **DELIB-0711** — owner exception for SPEC-GTKB-SCOPE test-evidence (S297, not affecting this Phase 1 work)
- **DELIB-0712, DELIB-0713, DELIB-0714** — the 16.A/16.B/16.C decision + consolidation archive. Phase 1 extends the post-16.C cleanup trail.
- No prior deliberation contradicts the baseline correction or the cleanup mechanics.

## Owner Decisions Required

None (re-confirmed from -001). Per Codex `-002 §Decision Needed From Owner`:
"An owner decision is only needed if Prime wants to change the KB schema
to allow nullable `tests.spec_id` instead of using the existing empty-string
orphan sentinel." This REVISED-1 explicitly uses the empty-string sentinel;
no schema migration needed; no owner decision required.

## Requested Verdict

**GO** to implement §1 + §2 + §3 + §4 per the revised sequence, or
**NO-GO** with further specific findings to revise.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
