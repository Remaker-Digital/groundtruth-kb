NEW

# Retire orphaned `role-assignments.json` — Slice 1: repoint the fresh-install seed

- bridge_kind: implementation_proposal
- Project: GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
- Work Item: WI-4214
- Author: prime-builder/claude (harness B), S385, 2026-06-01
- Recommended commit type: `refactor:` (repoint a bootstrap input source + harden status handling; no new capability surface)

## Summary

`harness-state/role-assignments.json` is an **orphaned legacy mirror**. As of WI-3342 (Registry Projection Reconciliation, VERIFIED — DELIB-2556), every role / dispatch / attribution **reader** was migrated to the DB-backed projection `harness-state/harness-registry.json`, and the **writer** `scripts/harness_roles.py:write_role_assignments` has **zero callers**. The file is frozen at its last hand-edit (2026-05-31, showing `C=["prime-builder"]`) and now diverges from the DB source of truth (`C role=[], status="registered"`), with no supported reconciliation path. Owner AUQ (S385) selected **retire**.

The **only remaining functional reader** is `scripts/seed_harness_registry.py:94`, which reads `role-assignments.json` (joined with `harness-identities.json`) as the fresh-install DB seed source. `groundtruth.db` is gitignored, so a fresh clone has no DB and must seed; the three `harness-state/*.json` files are tracked.

**Slice 1 (this proposal)** cuts that last functional dependency by repointing the seed to read the already-tracked, strictly-more-complete `harness-registry.json` projection. This removes role-assignments.json's last reader and, as a correctness bonus, lets the seed **preserve each record's real status** instead of forcing `status="active"` for everything — the behavior that originally seeded antigravity (C) as active and contributed to the `[B,C]` multi-active-prime dispatch failures in S381/S383.

This proposal touches **no owner-directive narrative** (that is Slice 2) and does **not** delete the file (that is Slice 3).

## Specification Links

- **ADR-ROLE-STATUS-ORTHOGONALITY-001** (architecture_decision) — role membership and dispatch eligibility (`status`) are orthogonal axes; dispatch is gated on `status=="active"`. Seeding everything `active` violates the spirit of this ADR; Slice 1 makes the seed status-faithful.
- **DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001** (design_constraint) — only the single ACTIVE harness per role is the dispatch target; an inactive role-holder must not be a candidate. Preserving `registered` status on seed keeps C out of the active set.
- **REQ-HARNESS-REGISTRY-001** (requirement) — FR1: the `harnesses` table is seeded from harness-state; FR5: the generated projection (`harness-registry.json`) is the hot-path surface. Slice 1 changes the FR1 seed **source** from `role-assignments.json` to the FR5 projection (both tracked); FR5 regeneration after seed is unchanged.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** (governance) — prefer fresh reads over divergent cached copies. Seeding from the DB-derived projection rather than a hand-edited orphan removes a stale-copy read path.
- **GOV-STANDING-BACKLOG-001** (governance) — WI-4214 backlog authority for this work.
- **`.claude/rules/file-bridge-protocol.md`** + **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — bridge proposal governance (spec linkage, preflight, owner-decisions section).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — live bridge index authority; this proposal is filed and tracked under the file-bridge protocol with `bridge/INDEX.md` as canonical state.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — post-implementation VERIFIED requires a spec-to-test mapping; the Spec-Derived Verification Plan below maps each linked spec to an executed test and reports the exact commands.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — artifact-oriented governance baseline; this work is tracked as a WI + bridge thread + spec-linked proposal rather than ad-hoc edits.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — artifact-oriented development decision context for governed cleanup work.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — artifact lifecycle triggers; retiring an orphaned artifact is a lifecycle event tracked via WI-4214 and sequenced across the 3-slice plan.

**Test derivation:** the spec-derived tests below derive from REQ-HARNESS-REGISTRY-001 FR1/FR5 (seed populates the table + regenerates the projection), and from ADR-ROLE-STATUS-ORTHOGONALITY-001 / DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 (seed preserves a `registered` record's status rather than forcing `active`). A regression test asserts the seed no longer reads `role-assignments.json`.

## Prior Deliberations

- **DELIB-2556** (Loyal Opposition Verification — Registry Projection Reconciliation, **VERIFIED**) — the WI-3342 reader migration to `harness-registry.json` that orphaned `role-assignments.json`. Slice 1 completes the consequence of that migration on the seed side.
- **DELIB-2507** (S371 Interactive Session Role Override Owner Directive) — establishes the durable-role authority model; relevant context, not contradicted here.
- **DELIB-1466** (Role And Session Lifecycle Review) — background on role/session lifecycle.
- **DELIB-2671** (LO Review — GT-KB CLAUDE.md Scope Clarification Slice 2, NO-GO) — relevant to the **Slice 2** narrative reword (not this slice); flagged so the owner-directive reword is handled with care later.

_No prior deliberation directly decided retiring `role-assignments.json`; the seed-bootstrap repoint is novel ground (DA query "seed harness registry fresh install bootstrap" returned no matches)._

## Requirement Sufficiency

**Existing requirements sufficient.** REQ-HARNESS-REGISTRY-001, ADR-ROLE-STATUS-ORTHOGONALITY-001, DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001, and GOV-SOURCE-OF-TRUTH-FRESHNESS-001 fully govern this change. No new or revised requirement is needed for Slice 1. (Slice 2 will require an owner re-direction decision, not a new requirement.)

## Retirement Program Context (3 slices; only Slice 1 is authorized by this proposal)

- **Slice 1 (this proposal):** repoint `seed_harness_registry.py` from `role-assignments.json` (+`harness-identities.json`) to `harness-registry.json`; preserve per-record `status`; update seed tests. Outcome: role-assignments.json has **zero functional readers**.
- **Slice 2 (future bridge thread):** reword the protected owner-directive narrative that still names `role-assignments.json` the single source of truth — `CLAUDE.md`, `AGENTS.md`, `.claude/rules/operating-role.md`, `.claude/rules/prime-builder-role.md`, `.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md`, `SECURITY.md` — to cite `harness-registry.json`. Requires **owner re-direction (AUQ)** for the three owner-directed files plus formal/narrative-artifact approval packets. Also removes the orphaned `write_role_assignments` and dead `ROLE_ASSIGNMENTS_*` constants/params.
- **Slice 3 (future bridge thread):** delete `harness-state/role-assignments.json`; update `test_harness_registry_reader_migration.py::_reconcile_registry_to_role_assignments`; finalize tracking removal.

## Slice 1 Scope (concrete changes)

1. `scripts/seed_harness_registry.py`:
   - Replace `read_legacy_harnesses()` (which reads `role-assignments.json` + `harness-identities.json`) with a reader of `harness-state/harness-registry.json` (the tracked projection list). Each projection record already carries `id`, `harness_name`, `harness_type`, `role`, `status`, `invocation_surfaces` — no identity/role join is needed, and richer `invocation_surfaces` (e.g. C's interactive surface) are carried verbatim.
   - Stop forcing `SEED_STATUS="active"`. Seed each harness at its **projection `status`** (default to `"registered"` — the conservative fail-closed value — when a record omits status). Idempotence is unchanged (skip ids already present).
   - Keep FR5 projection regeneration after seeding (unchanged).
2. `platform_tests/scripts/test_seed_harness_registry.py`:
   - Update the `_project()` fixture to write `harness-registry.json` (projection list form, including a `status` per record) instead of `role-assignments.json` + `harness-identities.json`.
   - Add a test that a `status="registered"` projection record seeds as `registered` (not coerced to `active`) — ADR-ROLE-STATUS-ORTHOGONALITY-001 / DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 derivation.
   - Add a regression test that the seed ignores `role-assignments.json` (presence of a stale role there does not affect seeded roles) — GOV-SOURCE-OF-TRUTH-FRESHNESS-001 derivation.

## Spec-Derived Verification Plan

| Spec | Derived check | Command |
|------|---------------|---------|
| REQ-HARNESS-REGISTRY-001 FR1/FR5 | Seed populates the table from `harness-registry.json` and regenerates the projection | `uv run --directory E:\GT-KB\groundtruth-kb pytest E:\GT-KB\platform_tests\scripts\test_seed_harness_registry.py -v` |
| ADR-ROLE-STATUS-ORTHOGONALITY-001 / DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001 | A `registered` record seeds as `registered`, not `active` | same suite (new test) |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | Seed does not read `role-assignments.json` | same suite (regression test) |
| Code quality (both files) | lint + format | `uv run --directory E:\GT-KB\groundtruth-kb ruff check E:\GT-KB\scripts\seed_harness_registry.py E:\GT-KB\platform_tests\scripts\test_seed_harness_registry.py` and `uv run --directory E:\GT-KB\groundtruth-kb ruff format --check E:\GT-KB\scripts\seed_harness_registry.py E:\GT-KB\platform_tests\scripts\test_seed_harness_registry.py` |

## Target Paths

```json
["scripts/seed_harness_registry.py", "platform_tests/scripts/test_seed_harness_registry.py"]
```

## Owner Decisions / Input

- **Owner AUQ (S385, this session):** chose **"Retire the orphaned mirror"** over "regenerate from DB" and "reconcile-now/defer," and over the originally-proposed option (b) (relax the `set-role` active gate), which was shown not to fix the symptom (its write path targets the DB/projection, not `role-assignments.json`). This proposal implements the first slice of that retire decision.
- **Owner directive (S383-wrap):** flagged the role-assignments.json divergence as the residual reconciliation gap under PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH and asked to file a WI (WI-4214, filed) and follow the bridge protocol.
- **Deferred to Slice 2 (no owner decision sought here):** rewording the owner-directed narrative (CLAUDE.md / AGENTS.md / operating-role.md) that names role-assignments.json the SoT will require a separate owner AUQ at that time.

## Risks / Rollback

- **Risk:** the tracked `harness-registry.json` is itself a generated snapshot; seeding the DB from it then regenerating it is idempotent (same records written back). On this install A/B/C already exist in the DB, so the seed is a no-op here; the change is exercised by fresh-clone seeding and by the test fixtures.
- **Risk:** behavior change (status no longer forced `active`). Mitigation: a fresh-clone seed now reflects the committed projection's true status, which is the intended, more-correct behavior; covered by the new `registered`-preservation test.
- **Rollback:** revert the two files; `role-assignments.json` is untouched and still present, so the prior seed path is fully restorable.
- **Scope guard:** this proposal does **not** delete `role-assignments.json`, remove `write_role_assignments`, or touch any `.md` narrative — those are Slices 2/3 with their own reviews.
