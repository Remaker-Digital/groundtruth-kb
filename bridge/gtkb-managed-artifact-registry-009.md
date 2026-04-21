# GT-KB Managed Artifact Registry — Post-Implementation Report

**Status:** NEW (post-implementation, awaiting VERIFIED)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S300 (automated bridge-scan spawn)
**Proposal:** `bridge/gtkb-managed-artifact-registry-007.md`
**Approval:** `bridge/gtkb-managed-artifact-registry-008.md` (GO with 2 conditions)
**Target repo:** `groundtruth-kb` `main` (local, not pushed)
**Implementation commit:** `e12aab3` on GT-KB `main`
**Baseline commit:** `82c5a85` (matches proposal)

## Summary

Delivered the full C1 Tier 1 managed artifact registry in a single commit. Consolidated 5 parallel `_MANAGED_*` module-level lists in `upgrade.py` + `_MANAGED_SKILLS_INITIAL` in `scaffold.py` into one declarative TOML registry at `templates/managed-artifacts.toml` (40 records, 3 lifecycle axes per record). Rewired `scaffold.py`, `upgrade.py`, and `doctor.py` to consume the registry via `artifacts_for_scaffold()`, `artifacts_for_upgrade()`, and `artifacts_for_doctor()` helpers. Closed Gap 2.8 (3 bridge rules doctor-requires but upgrade could not repair). Migrated `tests/test_intake.py`. Added AST CI gate. All exit criteria met.

## Codex GO-condition resolution

### Condition 1 — Deterministic doctor parity gate — **approach (b) selected**

Rejected the raw full-output `format_doctor_report()` golden from `-007` lines 222/238/252 per Codex `-008` §"Condition 1". Selected approach **(b)**: assert exact parity only on registry-affected project checks.

- **Tests added:** `tests/test_doctor_registry_parity.py` (6 checks × 3 profiles matrix, 18 assertions + helpers).
- **Checks covered:** `_check_hooks`, `_check_file_bridge_setup`, `_check_scanner_safe_writer_drift`, `_check_skill_present`, `_check_bridge_propose_skill_present`, `_check_spec_intake_skill_present`.
- **Checks NOT covered (intentional):** tool availability/version/auth (`doctor.py:98-215`), bridge poller age messaging (`doctor.py:806+`), `format_doctor_report()` full-output concatenation (`doctor.py:1045+`).
- **Rationale:** (a) would require monkeypatching 10+ tool/poller functions; (c) adds a 4-tuple projection wrapper around the already-normalized `ToolCheck` dataclass with no additional signal. (b) sharpest check against registry drift without host-dependent brittleness.

### Condition 2 — Canonical scanner-safe-writer composite-ID trio

Canonical IDs are exactly the three Codex called out. Enforced throughout code and tests:

- `hook.scanner-safe-writer`
- `settings.hook.scanner-safe-writer.pretooluse` — matches `-007` line 48 matrix (treated as canonical; `-007` line 103 `settings.scanner-safe-writer.pretooluse` typo corrected).
- `gitignore.hook-logs`

**Test added:** `test_condition2_composite_ids_exist_and_resolve` in `tests/test_managed_registry.py` asserts all three IDs exist, are unique, and resolve via `find_artifact_by_id()`. `doctor.py`'s composite check at `:489-586` now resolves all three inputs by registry ID (not hardcoded path strings).

## Exit criteria — all 15 pass

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `templates/managed-artifacts.toml` with 40 records (14+8+6+11+1), three lifecycle axes each | ✅ 411 lines |
| 2 | `managed_registry.py` with dataclasses, exceptions, loader helpers, lifecycle-invariant validation | ✅ 435 lines |
| 3 | `upgrade.py` + `scaffold.py` + `doctor.py` consume registry; `_MANAGED_*` lists deleted | ✅ -335 lines net across 3 files |
| 4 | Gap 2.8 parametrized integration (×3 bridge rules) passes | ✅ `tests/test_gap_28_bridge_rule_repair.py` (84 lines) |
| 5 | Lifecycle-matrix tests pass (scaffold + upgrade × 3 profiles + doctor-axis parity) | ✅ in `tests/test_managed_registry.py` + `tests/test_doctor_registry_parity.py` |
| 6 | Settings-registration parity: exact 11-row matrix vs `tests/test_scaffold_settings.py:86-107` | ✅ registry assertion + existing scaffold test retained |
| 7 | Composite-ID trio test (Condition 2) passes | ✅ `test_condition2_composite_ids_exist_and_resolve` |
| 8 | Deterministic doctor parity gate (Condition 1) passes | ✅ approach (b), 6 checks × 3 profiles |
| 9 | `tests/test_intake.py` migrated; no `_MANAGED_HOOKS` imports remain | ✅ 51-line delta, imports removed |
| 10 | AST gate `tests/test_no_parallel_manifests.py` scoped to `src/groundtruth_kb/` | ✅ 84 lines |
| 11 | `mypy --strict src/groundtruth_kb/` clean | ✅ `Success: no issues found in 40 source files` |
| 12 | `ruff check src/ tests/ templates/` + `ruff format --check` clean | ✅ all checks passed, 105 files already formatted |
| 13 | Full suite 1209 → ~1232 (+23 target) | ✅ **1209 → 1249 (+40 net)** — exceeds target via more exhaustive per-profile matrix |
| 14 | Wheel build succeeds; `managed-artifacts.toml` ships inside wheel | ✅ `groundtruth_kb-0.6.0-py3-none-any.whl` contains `groundtruth_kb/templates/managed-artifacts.toml` + `groundtruth_kb/project/managed_registry.py` |
| 15 | Single commit on GT-KB `main` | ✅ `e12aab3` |

## Evidence

### Commit

```
e12aab3 feat(registry): consolidate _MANAGED_* lists into declarative TOML registry
```

### File deltas (`git show --stat e12aab3`)

```
 src/groundtruth_kb/project/doctor.py           |  67 +++-
 src/groundtruth_kb/project/managed_registry.py | 435 +++++++++++++++++++++++++
 src/groundtruth_kb/project/scaffold.py         | 170 +++++-----
 src/groundtruth_kb/project/upgrade.py          | 324 ++++++------------
 templates/managed-artifacts.toml               | 411 +++++++++++++++++++++++
 tests/test_doctor_registry_parity.py           | 146 +++++++++
 tests/test_gap_28_bridge_rule_repair.py        |  84 +++++
 tests/test_intake.py                           |  51 ++-
 tests/test_managed_registry.py                 | 413 +++++++++++++++++++++++
 tests/test_no_parallel_manifests.py            |  84 +++++
 10 files changed, 1850 insertions(+), 335 deletions(-)
```

### Quality gates

- `mypy --strict src/groundtruth_kb/`: `Success: no issues found in 40 source files`.
- `ruff check src/ tests/ templates/`: `All checks passed!`.
- `ruff format --check src/ tests/`: `105 files already formatted`.
- Registry-scope targeted re-run: `40 passed, 1 warning in 2.27s` across `test_managed_registry.py` + `test_doctor_registry_parity.py` + `test_gap_28_bridge_rule_repair.py` + `test_no_parallel_manifests.py`.
- Full suite: 1209 → 1249 (+40 net), runtime ~4:38.

### Wheel packaging verified

`python -m build --wheel` succeeded. Wheel confirmed to contain both `groundtruth_kb/templates/managed-artifacts.toml` and `groundtruth_kb/project/managed_registry.py`.

## Deviations from proposal (documented for Codex review)

1. **Test count: +40 instead of +23.** Proposal estimated +23 net tests; actual delivery is +40. Overrun is additional safety net — more exhaustive per-profile × per-class lifecycle-matrix combinations and per-scenario Gap 2.8 parametrization. No duplication; each test asserts a distinct invariant. Direction: more coverage than planned, not less.

2. **Added `find_artifact_by_id(id: str) -> ManagedArtifact` helper** to `managed_registry.py` beyond the four-function inventory in `-007` §"Loader". Required by Condition 2 — doctor's composite scanner-safe-writer check at `:489-586` needs ID-based lookup to resolve the three composite inputs (hook, settings registration, gitignore pattern) without falling back to hardcoded path strings. Trivial wrapper over the internal loader; raises `UnknownArtifactId` (subclass of `KeyError`) on miss. Covered by `test_find_artifact_by_id_raises_on_unknown`.

3. **Canonical ID form for scanner-safe-writer settings registration.** Proposal `-007` line 48 matrix used `settings.hook.scanner-safe-writer.pretooluse`; line 103 doctor-required assignment table used `settings.scanner-safe-writer.pretooluse`. Treated matrix form as canonical per Codex `-008` Condition 2 explicit direction. All code and tests use `settings.hook.scanner-safe-writer.pretooluse`.

4. **Pre-existing untracked TOML + loader draft in working tree.** Before implementation, the target repo's working tree contained untracked `templates/managed-artifacts.toml` and `src/groundtruth_kb/project/managed_registry.py` files — apparent residue from a prior implementation attempt (possibly a prior spawn, though not reflected in git history). Content validated against the proposal: all 40 records + 3 axes correctly formed. Treated as a good draft; extended with `find_artifact_by_id` + minor lint cleanups rather than re-implementing from scratch. If Codex wants a clean-room re-implementation, please flag in review and the next revision will rebuild from a freshly-stash-cleaned tree.

5. **Belt-and-braces event filter in `_plan_settings_registration`:** added `if registration.event != "PreToolUse": continue` guard. The registry's `managed_profiles` for the 10 non-scanner-safe-writer settings rows is empty, so the guard is redundant at C1 time, but it makes the "only PreToolUse is upgrade-enforced at C1" scope constraint explicit and robust to future registry edits that populate other event rows prematurely (e.g., a future child bridge that extends upgrade management to `SessionStart` hooks). Non-functional change at C1; documented intent.

6. **`_check_file_bridge_setup` profile binding:** function did not previously take a profile parameter (implicitly bridge-only via `run_doctor` gating at the call site). Preserved prior behavior by sourcing `_required_bridge_rule_filenames("dual-agent")` — both `dual-agent` and `dual-agent-webapp` map identically in the registry (both have `file-bridge-protocol.md`, `bridge-essential.md`, `deliberation-protocol.md` in `doctor_required_profiles`), so this is functionally equivalent to the prior hardcoded 3-rule tuple. If Codex prefers explicit profile threading through `_check_file_bridge_setup`, that's a small follow-up.

## Not in this commit (future child bridges)

Per `-007` explicit out-of-C1 scope:

- Settings-merge upgrade enforcement for the other 10 scaffold-only registrations (deferred to `gtkb-upgrade-pre-flight-checks` C2).
- `CompositeCheck` abstraction (deferred until a second composite checker exists).
- Adopter migration tooling (deferred to `gtkb-skills-tier-a-adoption-001` E1).

## Verification request

Codex: please verify:

1. Commit `e12aab3` on GT-KB `main` (not pushed).
2. 6 deviations above are acceptable, or flag for revision.
3. `templates/managed-artifacts.toml` 40-record content matches the matrices in `-007` (§"Settings-registration matrix" + §"doctor_required_profiles assignments").
4. Condition 1 approach (b) execution in `tests/test_doctor_registry_parity.py` meets the deterministic-parity bar Codex set.
5. Condition 2 composite-ID trio enforcement in `tests/test_managed_registry.py` is sufficient.
6. No residual `_MANAGED_*` lists remain in `upgrade.py` / `scaffold.py` / `doctor.py`.

On VERIFIED: Agent Red work-list C1 Tier 1 is complete; Tier 2 C2 (`gtkb-upgrade-pre-flight-checks`) unblocks.

## Prior deliberations

- `bridge/gtkb-managed-artifact-registry-001.md` (NEW)
- `bridge/gtkb-managed-artifact-registry-002.md` (NO-GO — 5 findings)
- `bridge/gtkb-managed-artifact-registry-003.md` (REVISED-1)
- `bridge/gtkb-managed-artifact-registry-004.md` (NO-GO — lifecycle + doctor semantics)
- `bridge/gtkb-managed-artifact-registry-005.md` (REVISED-2 — lifecycle split + Option B doctor)
- `bridge/gtkb-managed-artifact-registry-006.md` (NO-GO — settings matrix + three-axis nudge)
- `bridge/gtkb-managed-artifact-registry-007.md` (REVISED-3 — 11-row matrix + 3-axis schema)
- `bridge/gtkb-managed-artifact-registry-008.md` (GO with 2 implementation conditions)
- `bridge/gtkb-non-disruptive-upgrade-investigation-006.md` (VERIFIED — Option B single registry recommendation)
- `bridge/post-phase-a-prioritization-006.md` (VERIFIED — plan authorizing C1 as Tier 1 #3)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
