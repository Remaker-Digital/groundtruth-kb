NEW

# Post-Impl REPORT - GTKB-PIP-INSTALL-ADOPTER-UX-001

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: `bridge/gtkb-pip-install-adopter-ux-001-003.md` REVISED-1; Loyal Opposition GO at `bridge/gtkb-pip-install-adopter-ux-001-004.md`
Requested bridge disposition: `VERIFIED`

## Claim

The minimal installed-wheel host-root fix is implemented.

- Source/editable checkout behavior remains strict: explicit `--gt-kb-root` must resolve to the active GT-KB host root.
- Installed distributions are detected by `site-packages` / `dist-packages` in `groundtruth_kb.project.scaffold.__file__`.
- Installed distributions accept an explicit adopter host root via `--gt-kb-root`.
- Installed distributions default host root to the current working directory when no explicit root is supplied.
- Application placement remains `<host_root>/applications/<project_name>/`.
- No `--here` or `--target` option was added.
- No release tag, PyPI publish, Agent Red migration, or broad scaffold redesign was performed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed in `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites required specs and release evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps install-smoke and isolation tests to cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 36 of `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the rc1 limitation and GA fix remain traceable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - editable installs preserve strict in-root applications boundary; installed wheels use adopter host-root placement.
- `.claude/rules/canonical-terminology.md` - GT-KB platform behavior remains separate from Agent Red application behavior.
- `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK` - owner accepted rc1 limitation and targeted this follow-on.
- `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-008.md` - Codex NO-GO that surfaced the install-UX defect.
- `bridge/gtkb-pip-install-adopter-ux-001-003.md` - approved revised proposal.
- `bridge/gtkb-pip-install-adopter-ux-001-004.md` - Loyal Opposition GO.

## Owner Decisions / Input

Owner decision: `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`.

- Rc1 limitation accepted: `v0.7.0-rc1` may ship with the known awkward installed-wheel command shape.
- GA follow-on scope: fix host-root resolution for installed wheels while preserving strict editable/source checkout behavior.
- Optional CLI shapes: `--here` and `--target` remain deferred and were not added.

This report does not authorize release publication.

## Implementation Details

Changed implementation:

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`
  - Added `_is_installed_wheel_context()`.
  - `_resolve_gt_kb_host_root(None)` returns `_GT_KB_HOST_ROOT` in source checkouts and `Path.cwd().resolve()` in installed distributions.
  - `_resolve_gt_kb_host_root(explicit)` preserves strict equality in source checkouts and accepts the explicit path in installed distributions.
- `groundtruth-kb/src/groundtruth_kb/cli.py`
  - Updated `--gt-kb-root` help text to describe source-checkout strictness and installed-wheel adopter host-root behavior.
- `groundtruth-kb/tests/test_scaffold_isolation.py`
  - Added helper tests for installed explicit-root and cwd-default behavior.
  - Added CLI tests proving installed-context `gt project init` creates under `<host_root>/applications/<name>`.

## Installed-Wheel Smoke

Command shape:

```text
python -m build --wheel --sdist
python -m venv E:\GT-KB\.tmp\pip-install-ux\run-cefce217\venv
<venv>\Scripts\python.exe -m pip install --quiet --upgrade pip
<venv>\Scripts\python.exe -m pip install --quiet <wheel>
<venv>\Scripts\gt.exe project init WheelExplicit --gt-kb-root E:\GT-KB\.tmp\pip-install-ux\run-cefce217\explicit-host --profile local-only --no-include-ci --no-seed-example
Push-Location E:\GT-KB\.tmp\pip-install-ux\run-cefce217\cwd-host
<venv>\Scripts\gt.exe project init WheelDefault --profile local-only --no-include-ci --no-seed-example
```

Observed result:

```text
Successfully built groundtruth_kb-0.7.0rc1-py3-none-any.whl and groundtruth_kb-0.7.0rc1.tar.gz
PASS explicit-root installed-wheel smoke: E:\GT-KB\.tmp\pip-install-ux\run-cefce217\explicit-host\applications\WheelExplicit\groundtruth.toml
PASS cwd-default installed-wheel smoke: E:\GT-KB\.tmp\pip-install-ux\run-cefce217\cwd-host\applications\WheelDefault\groundtruth.toml
Cleaned scratch: E:\GT-KB\.tmp\pip-install-ux\run-cefce217
```

The installed-wheel smoke proves adopters no longer need to discover virtual-environment internals.

## Specification-Derived Verification

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` updated so this file is latest `NEW` | PASS |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pip-install-adopter-ux-001` | PASS - `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect report for rc1 limitation, GA scope, and CLI-shape deferral | PASS |
| T-editable-root-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -m pytest tests/test_scaffold_isolation.py tests/test_scaffold_provider_templates.py tests/adopter/ tests/test_cli.py -q --tb=short` | PASS - 113 passed, 1 warning |
| T-installed-wheel-1 | GA UX follow-on | Installed-wheel smoke with explicit `--gt-kb-root <tmp-host>` | PASS |
| T-installed-wheel-2 | GA UX follow-on | Installed-wheel smoke with no explicit root from the desired host directory | PASS |
| T-lint-1 | Repo-native Python quality gate | `python -m ruff check src tests` from `groundtruth-kb` | PASS - all checks passed |
| T-format-touched-1 | Touched-file formatting | `python -m ruff format --check src/groundtruth_kb/project/scaffold.py src/groundtruth_kb/cli.py tests/test_scaffold_isolation.py` | PASS - 3 files already formatted |
| T-format-full-1 | Full package formatting | `python -m ruff format --check src tests` from `groundtruth-kb` | RESIDUAL - 22 pre-existing files would be reformatted; not part of this scoped UX fix |

`T-format-full-1` residual files:

```text
src/groundtruth_kb/bridge/notify.py
src/groundtruth_kb/project/doctor.py
src/groundtruth_kb/project/upgrade.py
tests/test_bridge_poller_runner.py
tests/test_bridge_propose_helper.py
tests/test_cli.py
tests/test_doctor_bridge_poller.py
tests/test_doctor_canonical_terminology.py
tests/test_full_tree_type_checks.py
tests/test_governance_hooks.py
tests/test_internal_helpers_type_checks.py
tests/test_managed_registry.py
tests/test_owner_decision_tracker_regex_tightening.py
tests/test_owner_decision_tracker_structural_guards.py
tests/test_owner_decisions_section_gate.py
tests/test_pending_owner_decisions_audit.py
tests/test_public_api_type_checks.py
tests/test_release_gate_metrics.py
tests/test_spec_classifier_canonical_triggers.py
tests/test_spec_event_surfacer.py
tests/test_term_disambiguation.py
tests/test_upgrade_isolation.py
```

## Changed Files

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_scaffold_isolation.py`
- `bridge/gtkb-pip-install-adopter-ux-001-005.md`
- `bridge/INDEX.md`
- `memory/work_list.md`

## Applicability Preflight

```text
packet_hash: sha256:aabae488475debcf43e8b2f5ff562f972721f41b5d38fa930068ebc6aab002a4
bridge_document_name: gtkb-pip-install-adopter-ux-001
operative_file: bridge/gtkb-pip-install-adopter-ux-001-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```
