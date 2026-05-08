NEW

# Proposal — Canonical Terms Production-DB Seed and Doctor Severity Elevation

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-07 (S337)
**Bridge thread:** `gtkb-canonical-terms-production-seed-and-doctor-elevation`
**Successor of:** `bridge/gtkb-canonical-terminology-system-context-model-001-008.md` (VERIFIED — Phase 1 of the parent umbrella)
**Scope class:** Defect remediation (test-fixture vs. production-DB drift) + doctor-check severity correction

## Defect Statement

Phase 1 of `GTKB-CANONICAL-TERMINOLOGY-SYSTEM-CONTEXT-MODEL-001` was VERIFIED at `-008` on the basis of "Live seed against `.claude/rules/canonical-terminology.md` populates 27 platform_core terms" (`-007` line 20). A live probe in S337 against `E:\GT-KB\groundtruth.db` finds the seed never reached the production database:

```text
canonical_terms table:        present
current_canonical_terms view: present
canonical_terms row count:           0
current_canonical_terms row count:   0
```

Re-reading `-008`'s evidence section confirms the verification was reproduced against a "Scratch seed/idempotency flow" (`-008` line 71), not the production DB. The Phase 1 schema and CLI shipped correctly; only the data load was missed.

The defect's persistence has a second contributing cause. The doctor surface `_check_canonical_terms_registry()` at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1697-1704` already detects the exact condition (`canonical_terms` table present but no rows) — but classifies it as `status="pass"`:

```python
terms = _ct.list_terms(conn, include_retired=False)
if not terms:
    return ToolCheck(
        name="canonical terms registry",
        required=False,
        found=True,
        status="pass",  # ← silent
        message=("canonical_terms table present but empty — run gt canonical-terms seed --apply"),
    )
```

Because the early-return classifies an empty table as PASS, `gt project doctor` produces no warning visible in the aggregate health summary. A future Phase 1-class regression (schema present, seed not run) would remain invisible the same way.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is delivered through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposals must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification requires spec-derived tests executed against the implementation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — touched paths are platform-internal (`groundtruth-kb/src/...`, `tests/scripts/...`); no `applications/` or Agent Red surface is affected.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — append-only versioning preserved (the seed uses `insert_term` per `groundtruth-kb/src/groundtruth_kb/canonical_terms.py:215-244`).
- `.claude/rules/project-root-boundary.md` — all touched paths are within `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol contract.
- `.claude/rules/codex-review-gate.md` — KB mutations (canonical_terms inserts) require GO before execution; this proposal is filed before any seed run.
- `.claude/rules/canonical-terminology.md` — Phase-1-authoritative source the seed parses; **no content changes** in this proposal.
- `bridge/gtkb-canonical-terminology-system-context-model-001-005.md` (Phase 1 design), `-006.md` (GO), `-007.md` (impl report), `-008.md` (VERIFIED) — predecessor thread.

## Prior Deliberations

`db.search_deliberations("canonical_terms backing registry seed", limit=3)` returned `DELIB-1017` (bridge_thread, GO) and `DELIB-1018` (bridge_thread, NO-GO) on the parent umbrella. No prior deliberation specifically rejects the production-seed approach; this proposal is a continuation, not a re-litigation. No prior deliberation flagged the doctor-severity question — that finding originates with this S337 review.

## Proposed Changes

### Change 1 — Run the seed against the production database

Execute, from `E:\GT-KB`:

```text
python -m groundtruth_kb canonical-terms seed --dry-run    # plan
python -m groundtruth_kb canonical-terms seed --apply      # apply
python -m groundtruth_kb canonical-terms seed --apply      # idempotency check
```

Expected post-`--apply` state:

- `SELECT COUNT(*) FROM current_canonical_terms` → 27.
- Second `--apply` → all 27 operations are `unchanged`.
- `gt canonical-terms list --authority-level platform_core --json` returns 27 rows.

The seed is mediated entirely by `groundtruth_kb.canonical_terms.seed_from_markdown()` (already shipped, idempotent, append-only). No code change is required for Change 1; it is a pure data-load step gated by Codex GO per `codex-review-gate.md`.

### Change 2 — Elevate doctor empty-table severity from `pass` to `warning`

Edit `groundtruth-kb/src/groundtruth_kb/project/doctor.py` lines 1697–1704:

```python
# BEFORE
terms = _ct.list_terms(conn, include_retired=False)
if not terms:
    return ToolCheck(
        name="canonical terms registry",
        required=False,
        found=True,
        status="pass",
        message=("canonical_terms table present but empty — run gt canonical-terms seed --apply"),
    )
```

```python
# AFTER
terms = _ct.list_terms(conn, include_retired=False)
if not terms:
    return ToolCheck(
        name="canonical terms registry",
        required=False,
        found=True,
        status="warning",
        message=(
            "canonical_terms table present but empty while .claude/rules/canonical-terminology.md "
            "defines platform_core terms — schema/seed drift; run `gt canonical-terms seed --apply`"
        ),
    )
```

Rationale: classifying an empty backing registry as `status="pass"` (when the markdown source defines 27+ platform_core terms) is inconsistent with the same surface's `parity_warnings` path at `doctor.py:1740` (which uses `status="warning"` for content drift between markdown and table). Empty-table is the strongest possible parity gap; it must not be quieter than per-term drift. `required=False` is preserved to maintain the soft-doctor compatibility contract (the same compatibility logic the existing `parity_warnings` path uses).

### Change 3 — Regression test for the elevated severity

Add a new test method to `tests/scripts/test_check_canonical_terminology_doctor_integration.py` (or co-located test file): when the `canonical_terms` table exists, the markdown defines ≥1 platform_core term, and the table is empty, `_check_canonical_terms_registry()` returns `status="warning"` (not `"pass"`).

This test pins the severity flip so a future refactor cannot silently re-introduce `status="pass"` on the empty-table path.

### Out of Scope

- No change to `.claude/rules/canonical-terminology.md` content (Phase 1 markdown authority preserved).
- No change to `canonical_terms` schema, the `current_canonical_terms` view, or the seed implementation (`seed_from_markdown`).
- No change to the existing parity-error / collision-error paths in the doctor check.
- No new umbrella spec — this is a defect remediation under the existing Phase 1 umbrella.
- Phase 2/3/4 of the parent umbrella remain out of scope.

## Test Plan and Spec-to-Test Mapping

| ID | Spec basis | Test |
|----|-----------|------|
| T-seed-1 | Phase 1 idempotency contract (`-005` design) | `python -m groundtruth_kb canonical-terms seed --dry-run` against production DB → plan summary shows `insert=27`. |
| T-seed-2 | Append-only versioning (`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) | `--apply` run → `SELECT COUNT(*) FROM canonical_terms` = 27, all rows at `version=1`, `lifecycle_status='active'`, `authority_level='platform_core'`. |
| T-seed-3 | Idempotency contract | Second `--apply` → plan summary shows `unchanged=27`; row count remains 27 (no version-2 rows). |
| T-seed-4 | Markdown is authority (Phase 1 contract) | `git diff --stat .claude/rules/canonical-terminology.md` is empty. |
| T-doctor-1 | Change 2 (severity correction) | New regression test: stub a DB with empty `canonical_terms` + present markdown → `_check_canonical_terms_registry().status == "warning"`. |
| T-doctor-2 | No regression in Phase 1 doctor scope | `python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py -q` passes (9 existing tests + 1 new). |
| T-doctor-3 | Post-seed doctor health | After Change 1, `gt project doctor --json` reports `canonical terms registry` as `status="pass"` with `27 active terms, parity clean, no collisions`. |
| T-mod-1 | Module unit tests unchanged | `python -m pytest groundtruth-kb/tests/test_canonical_terms_*.py -q` still passes (31 existing tests). |
| T-lint | Project lint contract | `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py` clean; ruff format check clean. |

## Acceptance Criteria

1. `current_canonical_terms` view returns 27 rows on `E:\GT-KB\groundtruth.db` after the implementation report is filed.
2. `gt canonical-terms seed --apply` is idempotent on a second invocation (all-unchanged).
3. `_check_canonical_terms_registry()` returns `status="warning"` (not `"pass"`) when the table is empty but the markdown defines platform_core terms.
4. The regression test added in Change 3 passes.
5. All existing tests in T-mod-1 and T-doctor-2 still pass.
6. No content change to `.claude/rules/canonical-terminology.md`.

## Risk Analysis

- **Seed risk:** low. The seed is append-only (`insert_term` ratchets `version`), idempotent (second run produces unchanged operations), and acts only on `platform_core` rows under `scope='platform'`. No existing rows are mutated; `parity_check`'s `missing_in_markdown` ERROR path can fire on next run if a markdown term is later removed, which is the intended parity-error semantics.
- **Doctor severity risk:** low. The severity change is a one-line flip with a tightened message. `required=False` is preserved (consistent with the adjacent `parity_warnings` branch at `doctor.py:1740`), so the change does not turn an existing PASS doctor run into a hard failure on systems that have not yet seeded.
- **Backwards compatibility:** Adopter projects that have not yet run the schema upgrade still hit the earlier `if cur.fetchone() is None` branch at `doctor.py:1687-1694` and remain at `status="pass"`. The severity change applies only to the post-schema, pre-seed window.

## Rollback

- **Change 1 rollback:** the seeded `canonical_terms` rows are correct platform_core data; if a rollback is needed (e.g., to validate a different seed source), retire the rows via a follow-on `seed --apply` against an alternative markdown — the rows persist as `lifecycle_status='retired'`. No DELETE is required (and would violate `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`).
- **Change 2 rollback:** revert the one-line severity change in `doctor.py`. The change is purely additive in observability terms.
- **Change 3 rollback:** delete the new test method.

## Owner Decisions / Input

This proposal does not introduce new owner-decision scope beyond the directive given in the S337 owner prompt (verbatim: "Run `python -m groundtruth_kb canonical-terms seed --apply`... and verify... Also propose a doctor-check addition... File a small bridge proposal"). The directive constitutes owner authorization to:

1. File this proposal through the bridge.
2. Execute the seed (Change 1) and doctor edits (Changes 2 and 3) **after Codex GO**.

Per `.claude/rules/acting-prime-builder.md` "AskUserQuestion as the Only Valid Owner-Decision Channel," no new AUQ-ask is required because (a) the work is owner-directed at the prompt level and (b) it is a bounded defect remediation under the existing VERIFIED Phase 1 umbrella. No requirement-disambiguation question is open.

If Codex review identifies a scope question that requires owner adjudication (e.g., whether the doctor severity should escalate to `fail` rather than `warning`), Prime Builder will route that question through `AskUserQuestion` before Implementation.

## Files to Touch

- `groundtruth.db` — data only via `gt canonical-terms seed --apply` (no schema change).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — one-line severity change + message tighten in `_check_canonical_terms_registry()`.
- `tests/scripts/test_check_canonical_terminology_doctor_integration.py` — one new regression test (or co-located equivalent).

## Implementation Sequence (post-GO)

1. Apply Change 2 (doctor.py severity flip).
2. Apply Change 3 (regression test).
3. Run `python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py groundtruth-kb/tests/test_canonical_terms_*.py -q` → expect all green (40 tests: 31 + 9 + 1 new).
4. Run `python -m groundtruth_kb canonical-terms seed --dry-run` → confirm `insert=27`.
5. Run `python -m groundtruth_kb canonical-terms seed --apply` → confirm `insert=27` summary.
6. Run `python -m groundtruth_kb canonical-terms seed --apply` → confirm `unchanged=27` (idempotency).
7. Run `python -m groundtruth_kb canonical-terms list --authority-level platform_core --json` → confirm 27 rows.
8. Run `python -m groundtruth_kb project doctor --json` → confirm `canonical terms registry` is `pass` with the OK message.
9. Run `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py` → clean.
10. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` → expect `preflight_passed: true`.
11. File the implementation report as `-002.md`, append `NEW: bridge/...-002.md` to the index entry.

## Recommended Commit Type

`fix:` — repair to a verified-but-incomplete deployment of Phase 1 (production seed missed) plus a tightening of the doctor-check severity that masked the same regression class. This is a defect remediation, not a new feature surface.

## Pre-Filing Preflight Evidence

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` (run 2026-05-07, S337):

- `packet_hash`: `sha256:16507ffa3dd2c5f2d1ab299854fdcc99f223ee1a7fc62fd964c7de32db6eacb0`
- `preflight_passed`: `true`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `[]`
- All 4 blocking + 3 advisory cross-cutting specs are cited.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
