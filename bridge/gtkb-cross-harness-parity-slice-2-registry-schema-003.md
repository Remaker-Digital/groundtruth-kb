NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 9630d0f9-6179-4700-ad6b-c32bb630c128
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4875

Document: gtkb-cross-harness-parity-slice-2-registry-schema
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-cross-harness-parity-slice-2-registry-schema-002.md
Recommended commit type: feat

target_paths: ["config/agent-control/harness-capability-registry.toml", "scripts/check_harness_parity.py", "platform_tests/scripts/test_cross_harness_parity_schema.py", "platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py"]

## Summary

Implemented Slice 2 per the GO (`-002`). Additive cross-harness-parity schema:
per-capability **applicability** (role-relative / universal), a formalized
**per-harness surface map** accessor, and a typed **waiver schema** (reason-class
+ rationale + owner-approval ref + review-trigger/expiry), plus a
`--validate-schema` CLI and tests. Closes Slice-1 GO finding **F1** (committed
foundation test asserting the ADR + DCL exist with required fields). The change
is behavior-preserving for the existing parity matrix.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` — realizes the registry-as-waiver-store
  demotion (Q5) and the applicability rule (Q4).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — satisfies assertion
  **PARITY-WAIVER-SCHEMA** (Slice 2) and contributes **PARITY-APPLICABILITY-RULE**
  (Slices 2-3).
- `GOV-20`, `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governance + bridge +
  spec-linkage + spec-derived-testing authority, carried forward from `-001`.

## Requirement Sufficiency

Existing requirements sufficient. The ADR + DCL already specify the waiver
schema and applicability rule; this slice implements them with no new or
revised requirement.

## Files Changed

- `config/agent-control/harness-capability-registry.toml` — added
  `parity_schema_version = 1` + a documented schema header (applicability
  vocabulary + `[[parity_waivers]]` convention); added explicit
  `applicability = "universal"` to `hook.advisory-router-scan`; bumped
  `last_updated`. No live waiver records (no declared asymmetry yet).
- `scripts/check_harness_parity.py` — additive: `PARITY_SCHEMA_VERSION`,
  `VALID_APPLICABILITY`, `WAIVER_REASON_CLASSES`, `WAIVER_REQUIRED_FIELDS`;
  `resolve_applicability`, `build_surface_map`, `load_parity_waivers`,
  `validate_parity_waiver`, `validate_parity_schema`; and a `--validate-schema`
  CLI flag. Existing `check_harness_parity()` matrix logic untouched.
- `platform_tests/scripts/test_cross_harness_parity_schema.py` — NEW (16 tests).
- `platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py` — NEW
  (F1; 2 tests, live-DB-or-skip idiom).

## Recommended Commit Type

`feat` — net-new schema surface, reader accessors/validators, a new CLI flag,
and two new test modules.

## Spec-to-Test Mapping + Verification Evidence

| Linked spec / requirement | Derived test(s) | Command | Result |
|---|---|---|---|
| DCL `PARITY-WAIVER-SCHEMA` | waiver accept/reject (well-formed, bad reason_class, missing field, missing trigger+expiry) + live-registry schema validity + synthetic schema failure modes | `python -m pytest platform_tests/scripts/test_cross_harness_parity_schema.py -q` | PASS (16) |
| DCL `PARITY-APPLICABILITY-RULE` | `resolve_applicability` default role-relative / default universal / explicit-universal override / live shared-hook universal | (same module) | PASS |
| F1 (ADR + DCL exist with required fields) | foundation existence/structure assertions vs live MemBase | `python -m pytest platform_tests/groundtruth_kb/test_cross_harness_parity_foundation.py -q` | PASS (2; ran, not skipped — live DB present) |
| Behavior preservation | existing parity matrix unchanged | `python -m pytest platform_tests/scripts/test_check_harness_parity.py -q` | PASS (12) |
| Schema validator (CLI) | `--validate-schema` exits 0 on live registry | `python scripts/check_harness_parity.py --validate-schema` | `parity schema OK` (exit 0) |
| Lint | changed `.py` files | `ruff check <changed>` | All checks passed |
| Format | changed `.py` files | `ruff format --check <changed>` | 3 files already formatted |

Aggregate: 30 passed in 1.00s.

## Acceptance Criteria Check

- Registry carries a validated waiver schema + per-capability applicability —
  satisfied; `validate_parity_schema` green on the live registry.
- Reader exposes schema / applicability / waiver / surface-map accessors with
  backward-compatible defaults — satisfied; additive, existing matrix test green.
- Schema-validation test passes — satisfied (16 tests).
- F1 foundation test committed and passing — satisfied (2 tests; ran against
  live MemBase).

## Owner Decisions / Input

Implementation authority flows from the active owner authorization
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (owner decision
`DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`). Program-home state for this slice
was established by owner AUQ on 2026-06-27 (archived `DELIB-20266265`):
reactivate the project + keep-open guard, and reconcile the PAUTH to
membership-based coverage. A subsequent owner AUQ on 2026-06-27 elected
interactive implementation for this program (headless Prime-B dispatch quiesced;
the idle dispatched worker on this thread was stopped and its stale lease
cleared under that authorization). No new owner decision is required to verify
this slice; this slice creates no formal GOV/ADR/DCL/SPEC artifact.

## Prior Deliberations

- `bridge/gtkb-cross-harness-parity-slice-2-registry-schema-002.md` — the GO
  (non-blocking residual: foundation test skips when DB absent; addressed by the
  live-DB-or-skip idiom).
- `bridge/gtkb-cross-harness-parity-slice-1-adr-dcl-004.md` — Slice-1 VERIFIED;
  this slice folds in its deferred F1 finding.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` §5 step 2 (this slice);
  `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` (Q5-Q8 waiver typing);
  `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`; `DELIB-20266265`.

## Risk / Rollback

- Behavior-preservation risk mitigated: the existing
  `test_check_harness_parity.py` is green; the new reader functions are pure and
  separate from `_status_for_surface` / `_role_applies`.
- Rollback: revert the four files; the Slice-1 foundation ADR/DCL are untouched,
  so rollback returns cleanly to the post-Slice-1 state.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
