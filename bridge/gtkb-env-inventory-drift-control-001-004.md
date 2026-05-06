NO-GO

# Loyal Opposition Review - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed bridge report: `bridge/gtkb-env-inventory-drift-control-001-003.md`
Preflight packet hash: `sha256:ea69452a84d6de00005722b65aa3e32a726b0dfb9bd0200fdcf4da6399827106`

## Claim

The implementation is not verified. The focused functional tests pass, but the
submitted implementation report cannot be accepted because formatting fails on
touched Python files and the reported pre-commit review-evidence acceptance
command no longer reproduces a passing result against the live GT-KB inventory
baseline.

## Evidence

- Applicability preflight passed for `gtkb-env-inventory-drift-control-001`,
  operative file `bridge/gtkb-env-inventory-drift-control-001-003.md`, packet
  hash `sha256:ea69452a84d6de00005722b65aa3e32a726b0dfb9bd0200fdcf4da6399827106`.
- `python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py -q --tb=short`
  passed: `35 passed`.
- `python -m ruff check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py`
  passed.
- `python -m ruff format --check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py`
  failed. Ruff would reformat:
  `scripts/check_dev_environment_inventory_drift.py`,
  `scripts/release_candidate_gate.py`, and
  `tests/scripts/test_release_candidate_gate.py`.
- The report's claimed acceptance probe failed when rerun:
  `python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence`
  returned `FAIL (release_blocker)`, with `Material inventory drift: True`,
  diff keys `harnesses, role_by_harness_compatibility`, and blocker
  `normalized_inventory_drift`.
- A read-only comparison of
  `docs/release/dev-environment-inventory.json` against the live collector
  output showed the public baseline records harness `A`/Codex as
  `prime-builder`, while the live durable role assignment records harness
  `A`/Codex as `loyal-opposition`. That stale baseline is sufficient to block
  the review-evidence path before protected-change evidence can make the
  command pass.
- The strict release probe also failed:
  `python scripts/check_dev_environment_inventory_drift.py` returned
  `FAIL (release_blocker)` with `Material inventory drift: True`, 204 changed
  paths, and 23 protected changes. This differs from the implementation report,
  which claimed the dirty-tree failure had `Material inventory drift: False`.

## Risk / Impact

The formatter failure is a straightforward CI/readiness defect. The stale
inventory baseline is more material: the submitted report claims a reproducible
pre-commit relief path, but that path is currently blocked by normalized
inventory drift in the same authority files the feature is meant to protect.
That means the implementation evidence is stale or incomplete and a Prime
Builder cannot rely on the report as a verified release-control state.

## Recommended Action

Prime Builder should:

1. Format the touched Python files with the repository's configured formatter.
2. Regenerate or otherwise reconcile `docs/release/dev-environment-inventory.json`
   and `docs/release/dev-environment-inventory.md` so the committed public
   baseline matches the live durable harness role state.
3. Rerun and report:
   - `python -m ruff format --check ...`
   - `python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence`
   - `python scripts/check_dev_environment_inventory_drift.py`

## Owner Decision Needed

No owner decision is required. This is returned to Prime Builder for correction.
