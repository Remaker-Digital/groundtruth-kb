NEW

# ISOLATION-017 Slices 4-8 + bridge-propose-helper Citation Backfill Implementation Proposal

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-06 (S333)
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking) — proposals must cite governing specs by ID, not only by rule-file path. The very gap this proposal remediates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking) — touches `bridge/` files under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol governing this work.
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## Claim

The S333 audit found 7 bridge threads reached `VERIFIED` with operative
files that fail the applicability preflight because they do not cite
required cross-cutting specifications by spec ID — only by rule-file
path. The bridge-compliance-gate hook landed mid-stream (commit
`639b981c` 2026-05-04), AFTER these threads were filed, so the gate did
not block them at Write time.

Affected threads (from `02-preflight-sweep.txt`):

1. `gtkb-isolation-017-slice4-upgrade-2026-05-02` (VERIFIED at `-012`)
2. `gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03` (VERIFIED at `-006`)
3. `gtkb-isolation-017-slice6-docs-2026-05-03` (VERIFIED at `-004`)
4. `gtkb-isolation-017-slice7-examples-2026-05-03` (VERIFIED at `-004`)
5. `gtkb-isolation-017-slice8-release-ops-2026-05-03` (VERIFIED at `-012`)
6. `gtkb-bridge-propose-helper-caller-migration-2026-05-02`
7. `gtkb-bridge-propose-helper-index-parity-2026-05-02`

Missing citations on items 1-5: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`.

Missing citations on items 6-7: same three plus `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

This proposal remediates the gap via citation backfill — each thread
gets a REVISED version that adds an explicit `## Specification Links`
section listing the missing spec IDs. Owner directive S333 ("Do not defer
anything") rules out the alternative path (DELIB-S333 waiver).

## Proposed Changes

For each of the 7 affected threads, file a REVISED version of the
**operative file** (the file the preflight currently identifies) that:

1. Preserves all existing content verbatim.
2. Adds an explicit `## Specification Links` section listing the
   required spec IDs (and any advisories).
3. Adds a brief "Citation backfill rationale" subsection explaining why
   this REVISED was filed: "Backfilled per `gtkb-isolation-017-citation-backfill-001`
   GO; original `-NNN` predated the bridge-compliance-gate hook landing.
   Backfilled citations carry the same governance authority as if filed
   originally; no implementation/verification scope changes."
4. Carries the next available `-NNN` version number per per-thread
   monotonic numbering.
5. Is added to `bridge/INDEX.md` with status `REVISED` per file-bridge protocol.

The REVISED files do NOT change any implementation, test results, or
verification claims. They are documentation-completeness backfills only.

This proposal also files a single companion DELIB
`DELIB-S333-ISOLATION-017-CITATION-BACKFILL` documenting:

- The historical gap and root cause (gate hook landed mid-stream).
- The backfill execution per-thread.
- The relationship to `gtkb-codex-bridge-compliance-gate-parity-001`
  (which prevents recurrence of this class on the Codex side).

## Specification-Derived Verification

Spec-to-test mapping per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Test |
|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | After REVISED files land, `python scripts/bridge_applicability_preflight.py --bridge-id <each>` returns `preflight_passed: true` for all 7 threads |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Each REVISED preserves all prior content; only additive citation block + rationale |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The mapping table in this proposal IS the spec-to-test mapping; the verification is the post-impl preflight pass |
| Append-only protocol | Old `-NNN` files preserved; new `-NNN+k` files filed as REVISED, not edits |

## Acceptance Criteria

1. 7 REVISED files filed under their respective threads (next-available `-NNN` per thread).
2. INDEX entries updated with `REVISED:` lines at the top of each thread block.
3. `python scripts/bridge_applicability_preflight.py --bridge-id <each-of-7>` returns `preflight_passed: true` for all 7 threads.
4. `DELIB-S333-ISOLATION-017-CITATION-BACKFILL` inserted with `source_type='audit_finding'`, `outcome='resolved'`, citing the audit report and this bridge thread.
5. No previous version files deleted; append-only discipline preserved.

## Risk And Rollback

- Risk: Backfill could be misread as restating past VERIFIED claims. Mitigation: each REVISED carries a "Citation backfill rationale" subsection explicitly clarifying scope.
- Risk: Per-thread numbering collision if a parallel session files something else. Mitigation: read each thread's INDEX block before filing; use the next available number.
- Rollback: each REVISED is isolated; `git revert` of the implementation commit removes them; per-thread state returns to pre-backfill VERIFIED.

## Owner Decisions / Input

- Owner directive S333: "I believe these are all acceptable. Do not defer anything." — explicitly chooses the backfill path over the waiver path the audit report offered as alternative.
- Owner directive S333: "I give you pre-approval to make changes wherever required" — authorizes filing.
- Owner directive S333 design-goals: "maximum quality (elegant simplicity, reliability, sustainability) and fit-for-purpose, not cost." — backfill is more rigorous; waiver was the cost-saving option that was declined.
- No additional owner approval requested by this proposal beyond standard Loyal Opposition `GO`/`NO-GO`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`:

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited above.
2. KB-search — no prior deliberation specifically rejects citation backfill; this is the first time the issue surfaces at audit scale.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX entry filed.
5. `packet_hash` recorded after preflight.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
