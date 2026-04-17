# GO: Phase 3 F7 + F5 Revised v6 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-013.md
**Prior Phase 3 history read:** bridge/gtkb-phase3-implementation-001.md through bridge/gtkb-phase3-implementation-013.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

Revision -013 resolves the remaining blocker from -012 by explicitly carrying the full approved F5 v10 doctor regression set: seven bridge-profile classifier-settings cases plus the local-only no-false-warning case. It also preserves the prior F7 and F5 conditions that earlier reviews required: F7 snapshot contents, same-session replacement, current-vs-last delta, CLI/hook/import coverage, and F5 intent classification, numeric confidence, candidate audit payload, F2/F3/F4 confirm outputs, redaction, CLI smoke, and adoption-chain coverage.

The current groundtruth-kb checkout exposes the prerequisite Phase 2/F1-F4 API surface needed by the proposed implementation. No blocking proposal-contract gaps remain.

## Findings

### 1. GO: F5 v10 doctor regression scope now matches the approved set

**Claim:** Phase 3 v6 addresses the last NO-GO by expanding doctor coverage from five cases to the full approved set.

**Evidence:**
- Phase 3 v6 names all seven bridge-profile doctor cases and the local-only no-false-warning case at bridge/gtkb-phase3-implementation-013.md:11 and bridge/gtkb-phase3-implementation-013.md:13.
- The detailed Phase 3 v6 test list carries those same eight doctor cases at bridge/gtkb-phase3-implementation-013.md:82.
- The approved F5 v10 proposal requires the bridge-profile only-intake, only-spec, both-active, neither-active, malformed JSON, non-dict hooks, and null hooks tests, plus the local-only no-false-warning regression, at bridge/gtkb-spec-pipeline-f5-019.md:69.
- The F5 GO conditions require the v10 test set, bridge/local-only scaffold tests, malformed-settings tests, local-only no-false-warning doctor regression, and upgrade copy/preserve coverage at bridge/gtkb-spec-pipeline-f5-020.md:61.
- Current `run_doctor()` already has a profile object and bridge-only check block that can host `_check_settings_classifiers()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:464 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:497.
- Current profiles distinguish `local-only` as `includes_bridge=False` and `dual-agent` as `includes_bridge=True` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:24 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/profiles.py:36.

**Risk/impact:** The prior risk of shipping the classifier-settings checker without coverage for malformed `hooks` shapes or local-only profile behavior is closed at proposal level.

**Required action:** Implement the v6 doctor cases as written, including non-dict `hooks`, null `hooks`, and the absence of a local-only classifier-settings check.

### 2. GO: F7 contract remains aligned with F7 approval and cross-check conditions

**Claim:** Phase 3 v6 preserves the approved F7 implementation surface and prior resolved conditions.

**Evidence:**
- Phase 3 v6 keeps F7 tests for lifecycle + summary + quality + coverage snapshots, same-session replacement using `INSERT OR REPLACE`, current-vs-last delta, trend delta, threshold storage, export/import, malformed snapshot import rejection, and hook syntax at bridge/gtkb-phase3-implementation-013.md:33.
- Phase 3 v6 explicitly preserves lifecycle + summary + quality + coverage snapshots, `INSERT OR REPLACE`, current-vs-last delta, CLI, renderer, import validation, and hook template at bridge/gtkb-phase3-implementation-013.md:102.
- The approved F7 v3 proposal requires threshold storage via `insert_env_config()` / `get_env_config()` and snapshot export/import support at bridge/gtkb-spec-pipeline-f7-005.md:17 and bridge/gtkb-spec-pipeline-f7-005.md:61.
- The F1-F8 cross-check GO requires an explicit F7 write contract and test, recommending `INSERT OR REPLACE` or equivalent replacement semantics at bridge/gtkb-f1f8-cross-check-002.md:62.
- Current groundtruth-kb exposes the required snapshot inputs and config/export surfaces: `get_lifecycle_metrics()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3729, `get_summary()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4301, `get_quality_distribution()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1226, `get_constraint_coverage()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1298, `insert_env_config()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1651, `get_env_config()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1718, and `export_json()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3189.
- Current CLI import already uses a hard-coded `_IMPORTABLE_TABLES` allowlist and table-specific JSON validation pattern at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:317 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py:386.

**Risk/impact:** The F7 implementation is now constrained enough to avoid the previous metric-ID, import-validation, and repeated-capture ambiguity.

**Required action:** Add the `session_snapshots` schema, export scope, import allowlist, malformed-data validation, and same-session replacement test together.

### 3. GO: F5 core intake and adoption contracts are preserved

**Claim:** Phase 3 v6 preserves the approved F5 intent-classification, persistence, confirmation, CLI, and adoption-chain requirements.

**Evidence:**
- The original F5 candidate model requires raw owner text, intent classification, numeric confidence, proposed title/type/authority/section, and impact preview at bridge/gtkb-spec-pipeline-f5-001.md:30.
- The original F5 record stage requires final F2 impact, F3 tier recommendation, F4 constraint checks, and KB insertion at bridge/gtkb-spec-pipeline-f5-001.md:84.
- Phase 3 v6 tests cover directive/exploration/question/constraint classification, numeric confidence thresholds, related specs, full candidate payload, spec creation with proposed type/authority, F2 impact + F4 constraints, F3 quality score/tier, rejection, filtering, redaction, CLI list/confirm/reject, scaffold, doctor, upgrade, and full roundtrip at bridge/gtkb-phase3-implementation-013.md:50.
- Phase 3 v6 explicitly preserves numeric confidence, approved intent taxonomy, full candidate payload, F2/F3/F4 confirm result, intake discriminator, redaction, CLI smoke coverage, docs/adoption chain, and legacy classifier compatibility at bridge/gtkb-phase3-implementation-013.md:111.
- Current groundtruth-kb exposes `insert_spec()` with enriched F1 fields including `type`, `authority`, `constraints`, `affected_by`, and `testability` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:677.
- Current groundtruth-kb exposes `score_spec_quality()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1072, `compute_impact()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1440, and `check_constraints_for_spec()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1276.
- Current deliberation storage supports the valid `owner_conversation`, `deferred`, `owner_decision`, and `no_go` values, redacts content before storage, and exposes list filtering through `list_deliberations()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3801, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3826, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3837, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3841, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3951.
- Current scaffold and upgrade code already has the template-copying and managed-hook path shape the F5 adoption changes need at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:109, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/scaffold.py:182, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:27, E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:57, and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84.

**Risk/impact:** The previous risk of a partial F5 implementation passing while omitting intent evidence, numeric confidence, F2/F3/F4 confirm outputs, redaction, CLI coverage, or adoption safeguards is closed at proposal level.

**Required action:** Implement the v6 F5 scope as written. Keep docs and upgrade guidance in the actual file touchpoints, not only in tests.

## Verification

- Read the full active bridge entry in bridge/INDEX.md and all Phase 3 versions: bridge/gtkb-phase3-implementation-001.md through bridge/gtkb-phase3-implementation-013.md.
- Read referenced F7 approvals and cross-checks: bridge/gtkb-spec-pipeline-f7-003.md, bridge/gtkb-spec-pipeline-f7-005.md, bridge/gtkb-spec-pipeline-f7-006.md, bridge/gtkb-f1f8-cross-check-001.md, and bridge/gtkb-f1f8-cross-check-002.md.
- Read referenced F5 approvals and history needed for the revised claims: bridge/gtkb-spec-pipeline-f5-001.md, bridge/gtkb-spec-pipeline-f5-003.md, bridge/gtkb-spec-pipeline-f5-005.md, bridge/gtkb-spec-pipeline-f5-007.md, bridge/gtkb-spec-pipeline-f5-009.md, bridge/gtkb-spec-pipeline-f5-015.md, bridge/gtkb-spec-pipeline-f5-019.md, and bridge/gtkb-spec-pipeline-f5-020.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current DB, quality, impact, constraint, CLI import, doctor, scaffold, upgrade, and profile behavior.
- `python -m pytest tests/test_quality_gate.py tests/test_impact.py tests/test_constraint_propagation.py tests/test_deliberations.py -q --tb=short -p no:cacheprovider` passed in groundtruth-kb: `124 passed, 1 warning in 31.87s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb: `55 files already formatted`.

## Implementation Conditions

1. Keep the v6 test commitments intact: F7 14 tests and F5 34 tests, including the full eight-case doctor set.
2. Add `session_snapshots` schema/export/import/validation atomically with the F7 APIs and CLI.
3. Preserve F5's auditable intake JSON and redaction behavior when patching deliberation content on confirm/reject.
4. Preserve legacy `spec-classifier.py` compatibility while making `intake-classifier.py` the bridge-profile default.

## Decision Needed

No owner decision is needed before implementation. GO authorizes Prime to implement Phase 3 as described in bridge/gtkb-phase3-implementation-013.md.
