NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 9630d0f9-6179-4700-ad6b-c32bb630c128
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4875

Document: gtkb-cross-harness-parity-slice-2-registry-schema
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Recommended commit type: feat

target_paths: ["config/agent-control/harness-capability-registry.toml", "scripts/check_harness_parity.py", "platform_tests/scripts/test_cross_harness_parity_schema.py", "platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py"]

## Summary

Slice 2 of `PROJECT-GTKB-CROSS-HARNESS-PARITY` extends the harness capability
registry and its reader with the cross-harness-parity schema that the
foundation `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` requires: per-capability
**applicability** (role-relative / universal), a formalized **per-harness
surface map** accessor, and a typed **waiver schema** (reason-class +
rationale + owner-approval ref + review-trigger/expiry). It adds reader
accessors and a schema validator that later slices consume, plus a
schema-validation test and the deferred Slice-1 F1 foundation test.

This slice is additive and behavior-preserving for the existing parity matrix:
the new fields and functions do not alter `check_harness_parity()`'s existing
per-capability per-harness state evaluation. The discovery-diff that *consumes*
the waiver store and applicability rule lands in Slice 3.

This closes Slice-1 GO finding **F1** (the deferred committed test file
`platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py`
asserting the ADR + DCL exist with required fields).

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — the bidirectional,
  applicability-scoped behavioral-parity invariant. This slice realizes the
  registry-as-waiver-store demotion (Q5) and the applicability rule (Q4):
  registry carries `canonical_purpose` + per-harness surface map + waiver
  store.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — directly satisfies
  assertion **PARITY-WAIVER-SCHEMA** (Slice 2: typed reason-class
  hard-limitation / harness-surface-difference / deliberate-deferral +
  rationale + owner-approval ref + review-trigger/expiry) and contributes
  **PARITY-APPLICABILITY-RULE** (Slices 2-3: role-relative for role-specific
  capabilities, universal for session/governance capabilities, active-only).
- `GOV-20` (architecture decision governance) — the ADR/DCL workflow this
  program follows; Slice 2 implements two DCL assertions derived from the ADR.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governing this
  proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Test Plan below
  derives tests from the linked DCL assertions and the F1 foundation
  requirement.

The proposed tests derive from the linked specs: the schema-validation test
maps to DCL assertions PARITY-WAIVER-SCHEMA and PARITY-APPLICABILITY-RULE; the
foundation test maps to the F1 requirement (ADR + DCL exist with required
fields).

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CROSS-HARNESS-PARITY-001` and
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` already specify the waiver schema
(Q7 / assertion PARITY-WAIVER-SCHEMA) and the applicability rule (Q4 /
assertion PARITY-APPLICABILITY-RULE). No new or revised requirement is needed;
this slice implements those existing constraints.

## Cross-Harness Disposition

These `target_paths` touch parity-infrastructure surfaces
(`config/agent-control/harness-capability-registry.toml`,
`scripts/check_harness_parity.py`), so the disposition is declared per the
ADR Q8 / DCL assertion PARITY-DISPOSITION-GATE contract (the mechanical gate
itself lands in Slice 4; this section is declared proactively).

- **Nature of change:** the registry TOML and its Python reader are
  harness-agnostic platform files consumed identically by every harness's
  parity tooling. This slice adds schema fields, reader accessors, and tests.
- **Per-harness behavioral parity:** the change introduces no per-harness
  runtime capability and no behavioral asymmetry. All applicable harnesses
  (claude, codex, antigravity, ollama, cursor, openrouter) consume the same
  registry and reader. Applicability for this infrastructure is **universal**.
- **Waivers:** none required; no harness lacks a surface introduced here.

## Design

### A. Registry schema extension — `config/agent-control/harness-capability-registry.toml`

1. Add a top-level `parity_schema_version = 1` declaration (after
   `last_updated`) plus a documented schema-header comment block describing the
   applicability vocabulary and the waiver-record shape.
2. Add an explicit `applicability = "universal"` field to the
   `hook.advisory-router-scan` capability (a session/governance Stop hook that
   runs on all harnesses) to exercise the explicit-override path. All
   role-specific skills keep the reader's default resolution (no per-capability
   churn).
3. Document the `[[parity_waivers]]` array-of-tables convention (the typed
   waiver store). No live waiver records are added in this slice — no declared
   asymmetry exists yet (the first real disposition is the Slice-5 `::open`
   conformance case). The reader validates any records that are present.
4. Bump `last_updated`.

### B. Reader extension — `scripts/check_harness_parity.py` (additive only)

New module constants and pure functions; existing functions and the
`check_harness_parity()` matrix logic are untouched:

- Constants: `PARITY_SCHEMA_VERSION = 1`,
  `VALID_APPLICABILITY = frozenset({"role-relative", "universal"})`,
  `WAIVER_REASON_CLASSES = frozenset({"hard-limitation",
  "harness-surface-difference", "deliberate-deferral"})`,
  `WAIVER_REQUIRED_FIELDS = ("capability_id", "harness", "reason_class",
  "rationale", "owner_approval_ref")`.
- `resolve_applicability(capability) -> str`: returns an explicit valid
  `applicability` field if present; otherwise the default — `"role-relative"`
  when `required_for_roles` is non-empty, else `"universal"`.
- `build_surface_map(registry) -> dict`: per-capability `id` -> `{harness:
  {surface, status}}` from the existing per-harness subtables (the formalized
  per-harness surface map accessor).
- `load_parity_waivers(registry) -> list[dict]`: returns the
  `[[parity_waivers]]` records (empty list when absent).
- `validate_parity_waiver(waiver) -> list[str]`: required fields present;
  `reason_class` in `WAIVER_REASON_CLASSES`; at least one of `review_trigger`
  / `expiry` present. Returns error strings (empty = valid).
- `validate_parity_schema(registry) -> list[str]`: `parity_schema_version`
  present and equal to `PARITY_SCHEMA_VERSION`; every capability's resolved
  applicability is valid; every waiver validates and references a known
  capability id and a known harness. Returns error strings (empty = valid).
- A `--validate-schema` CLI flag on `main()` that runs `validate_parity_schema`
  against the live registry, prints results, and exits non-zero on errors —
  making the schema independently checkable now (Slice 3's discovery-diff and
  Slice 6's CI gate build on it).

### C. Schema-validation test — `platform_tests/scripts/test_cross_harness_parity_schema.py`

Derived from DCL assertions PARITY-WAIVER-SCHEMA + PARITY-APPLICABILITY-RULE:

- live registry passes `validate_parity_schema` (returns empty);
- `parity_schema_version == 1`;
- `resolve_applicability` defaults a role-specific capability to
  `role-relative` and honors the explicit `universal` on
  `hook.advisory-router-scan`;
- `build_surface_map` contains a known capability with its claude + codex
  surfaces;
- waiver validation: a well-formed synthetic waiver passes; a bad
  `reason_class` fails; a missing required field fails; a waiver with neither
  `review_trigger` nor `expiry` fails.

### D. F1 foundation test — `platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py`

Follows the established live-DB-or-skip idiom
(`platform_tests/scripts/test_check_obsolete_reference_purge.py`): resolve
`_PROJECT_ROOT / "groundtruth.db"`, `pytest.skip` when the gitignored MemBase
is absent (fresh CI checkout), else open `KnowledgeDB` read-only and assert:

- `ADR-CROSS-HARNESS-PARITY-001` exists, `type=architecture_decision`,
  `status=accepted`, body contains the required sections (`## Decision`,
  `## Context`, `## Rejected alternatives`, `## Consequences`, `## Rationale`);
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` exists,
  `type=design_constraint`, `status=specified`, body names the five assertion
  ids (PARITY-DIFF-EXISTS, PARITY-WAIVER-SCHEMA, PARITY-DISPOSITION-GATE,
  PARITY-APPLICABILITY-RULE, PARITY-DIFF-WIRED).

This enforces wherever the canonical DB exists (dev + the Slice-6 release/CI
gate, which runs against the live MemBase) without duplicating canonical
content or false-failing a DB-less checkout.

## Test Plan / Spec-Derived Verification

| Linked spec / assertion | Derived test | Command |
|---|---|---|
| DCL PARITY-WAIVER-SCHEMA | waiver schema accept/reject cases + live-registry schema validity in `test_cross_harness_parity_schema.py` | `python -m pytest platform_tests/scripts/test_cross_harness_parity_schema.py -q` |
| DCL PARITY-APPLICABILITY-RULE | `resolve_applicability` default + explicit-override cases | `python -m pytest platform_tests/scripts/test_cross_harness_parity_schema.py -q` |
| F1 (ADR + DCL exist w/ required fields) | foundation existence/structure assertions | `python -m pytest platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py -q` |
| Behavior preservation | existing parity matrix unchanged | `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: all new tests pass; existing `test_check_harness_parity.py`
remains green (additive change); `gt project doctor` parity surface unchanged;
`scripts/check_harness_parity.py --validate-schema` exits 0 against the live
registry.

## Owner Decisions / Input

Implementation authority flows from the existing owner authorization
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (active; owner decision
`DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), which authorizes bounded
implementation of the program covering slice work items by active project
membership. Two owner AUQ decisions on 2026-06-27 (archived
`DELIB-20266265`) established the program-home state for this slice:

- **Reactivate + guard:** reactivate `PROJECT-GTKB-CROSS-HARNESS-PARITY`
  (auto-retired after Slice 1) and keep it open via an active non-terminal
  slice WI (WI-4875) — the project member that authorizes this proposal.
- **Membership-based PAUTH coverage:** reconcile the PAUTH
  `included_work_item_ids` to empty so coverage matches its scope_summary's
  membership model, covering WI-4875 and future slice WIs.

No new owner decision is required to implement Slice 2; formal-artifact
approvals are not needed (this slice creates no GOV/ADR/DCL/SPEC artifact —
the foundation ADR/DCL already exist).

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — the build-ready design;
  §5 build sequence step 2 is this slice (registry schema extension).
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` — owner grill Q5-Q8
  resolving the waiver typing and registry demotion.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — the owner authorization basis.
- `DELIB-20266265` — owner AUQ reactivating the program home and electing
  membership-based PAUTH coverage for the slice work items.
- `bridge/gtkb-cross-harness-parity-slice-1-adr-dcl-004.md` — Slice-1 VERIFIED
  verdict; this slice folds in its deferred F1 finding and its note that the
  DCL `assertions` DB column is description-only (structured `--assertions-json`
  encoding remains deferred to Slice 3 per the verdict).

## Risk / Rollback

- **Risk:** the additive reader functions could inadvertently change existing
  parity-matrix behavior. *Mitigation:* the existing
  `test_check_harness_parity.py` is re-run as a behavior-preservation gate; new
  functions are pure and separate from `_status_for_surface` / `_role_applies`.
- **Risk:** a new top-level TOML key or per-capability field could break the
  reader's `tomllib` load or existing key reads. *Mitigation:* the new keys are
  ignored by existing code paths; the schema test loads the live registry.
- **Rollback:** revert the four files; the foundation ADR/DCL (Slice 1) are
  untouched, so rollback returns to the post-Slice-1 state with no governance
  residue.
