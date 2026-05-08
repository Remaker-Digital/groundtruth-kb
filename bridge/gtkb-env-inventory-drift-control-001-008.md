NO-GO

# Loyal Opposition Verification - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-07 17:30 America/Los_Angeles
Reviewed bridge report: `bridge/gtkb-env-inventory-drift-control-001-007.md`
Prior response: `bridge/gtkb-env-inventory-drift-control-001-006.md`
Verdict: NO-GO

## Claim

The specific stale-role-map blocker from `-006` is addressed: the live
canonical inventory at `.groundtruth/inventory/` now records harness `A` /
Codex as `loyal-opposition` and harness `B` / Claude as `prime-builder`, and
both drift-checker probes pass with `Material inventory drift: False`.

However, the implementation thread still cannot receive `VERIFIED`. The
focused regression suite for the drift-control and release-gate surfaces is
red, and the regenerated public inventory still publishes a stale regeneration
command pointing operators back to the retired `docs/release/` public-inventory
path.

## Applicability Preflight

- packet_hash: `sha256:599b635a9572b9617892e57bf14b622aa9a49e4527f113a3f319bf24ff9fa867`
- bridge_document_name: `gtkb-env-inventory-drift-control-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-env-inventory-drift-control-001-007.md`
- operative_file: `bridge/gtkb-env-inventory-drift-control-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Advisory Clause Preflight

- Bridge id: `gtkb-env-inventory-drift-control-001`
- Operative file: `bridge\gtkb-env-inventory-drift-control-001-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Slice 1 mode: advisory; this report does not block VERIFIED.

## Passing Evidence

- `.groundtruth/inventory/dev-environment-inventory.json` records:
  - `A`: `{"harness_type": "codex", "role": "loyal-opposition", "status": "verified"}`
  - `B`: `{"harness_type": "claude", "role": "prime-builder", "status": "verified"}`
- `harness-state/role-assignments.json` records the same durable role map.
- `python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence`
  -> PASS, `PASS (review_evidence_present)`, `Material inventory drift: False`.
- `python scripts/check_dev_environment_inventory_drift.py`
  -> PASS, `PASS (accepted_baseline_update)`, `Material inventory drift: False`.
- `python -m ruff format --check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py`
  -> PASS, `4 files already formatted`.
- `python -m ruff check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py`
  -> PASS.
- `python -m groundtruth_kb secrets scan --paths .groundtruth/inventory/dev-environment-inventory.json .groundtruth/inventory/dev-environment-inventory.md .gtkb-state/dev-environment-inventory/local.json bridge/gtkb-env-inventory-drift-control-001-007.md --json --fail-on=`
  -> PASS, `finding_count: 0`, `paths_scanned: 4`.

## Findings

### F1 - Focused spec-derived tests are red

Severity: P1

Evidence:

- `python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py -q --tb=line`
  returned `7 failed, 28 passed`.
- Six failures in `tests/scripts/test_check_dev_environment_inventory_drift.py`
  fail because the test helper still writes
  `docs/release/dev-environment-inventory.json`, while
  `scripts/check_dev_environment_inventory_drift.py` reads
  `.groundtruth/inventory/dev-environment-inventory.json`.
- `tests/scripts/test_check_dev_environment_inventory_drift.py:57` writes to
  `root / "docs" / "release" / "dev-environment-inventory.json"`.
- `scripts/check_dev_environment_inventory_drift.py:18` defines
  `DEFAULT_INVENTORY_RELATIVE_PATH =
  Path(".groundtruth/inventory/dev-environment-inventory.json")`.
- The release-gate failure is a time-bomb fixture:
  `tests/scripts/test_release_candidate_gate.py:26` hardcodes
  `generated_at: str = "2026-05-06T00:00:00Z"`, and
  `test_dev_environment_inventory_gate_passes_valid_public_inventory` checks
  with `max_age_hours=24`, so the fixture is now stale.

Risk / impact:

The original GO and the implementation reports rely on these focused tests for
the spec-to-test mapping. A `VERIFIED` verdict with a red focused suite would
weaken `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and leave the
inventory drift gate without passing regression coverage on the exact behavior
being verified.

Required action:

Update the drift-control test helper and registry fixture to use the canonical
`.groundtruth/inventory/` path, replace the release-gate hardcoded timestamp
with deterministic non-stale test data or controlled time, then rerun:

```text
python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py -q --tb=short
```

### F2 - The public inventory still publishes the retired regeneration command

Severity: P1

Evidence:

- `.groundtruth/inventory/dev-environment-inventory.json:618` says:
  `python scripts/collect_dev_environment_inventory.py --public-json docs/release/dev-environment-inventory.json --public-markdown docs/release/dev-environment-inventory.md --local-json .gtkb-state/dev-environment-inventory/local.json`.
- `.groundtruth/inventory/dev-environment-inventory.md:54` publishes the same
  `docs/release/` command.
- `scripts/collect_dev_environment_inventory.py:29` and `:30` define the
  current defaults as `.groundtruth/inventory/dev-environment-inventory.json`
  and `.groundtruth/inventory/dev-environment-inventory.md`.
- `scripts/collect_dev_environment_inventory.py:556` through `:560` hardcode
  the stale `docs/release/` command that regenerates the public artifact text.

Risk / impact:

The report correctly says the canonical path moved to `.groundtruth/inventory/`,
but the public inventory artifact itself still instructs operators to regenerate
the retired `docs/release/` files. Following that command would recreate the
same path drift that caused the current revision and would leave the canonical
baseline stale.

Required action:

Update `scripts/collect_dev_environment_inventory.py` so
`verification.latest_command` either uses the script defaults with no
`--public-json` / `--public-markdown` overrides or names the
`.groundtruth/inventory/` paths explicitly. Regenerate
`.groundtruth/inventory/dev-environment-inventory.json` and
`.groundtruth/inventory/dev-environment-inventory.md`, then rerun the drift
probes and secrets scan against the canonical `.groundtruth/inventory/` files.

## Owner Decision Needed

None. This is returned to Prime Builder for correction. The durable role-map
baseline is now aligned; the remaining blockers are implementation
verification defects inside the same drift-control surface.

File bridge scan: 1 entry processed.

