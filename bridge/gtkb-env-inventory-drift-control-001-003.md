NEW

# Post-Implementation Report - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001

Author: Prime Builder (Codex, harness A)
Date: 2026-05-06
Bridge thread: `gtkb-env-inventory-drift-control-001`
Prior GO: `bridge/gtkb-env-inventory-drift-control-001-002.md`

## Claim

Prime Builder implemented protected-artifact development-environment inventory
drift control as proposed. The implementation adds a deterministic protected
artifact registry, a normalized inventory drift checker, release-gate
integration, pre-commit integration, focused tests, and a refreshed public
inventory baseline.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/project-root-boundary.md`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `bridge/gtkb-env-inventory-001-001.md`
- `bridge/gtkb-env-inventory-001-003.md`
- `GTKB-ENV-INVENTORY-001`

## Owner Decisions / Input

No new owner decision is required for this implementation report. The owner
already directed the drift-control follow-on and the approved proposal recorded
that intent. This report does not request credential lifecycle action,
deployment, GitHub settings mutation, or formal GOV/ADR/DCL promotion.

## Implemented Changes

Added:

- `config/governance/protected-artifact-inventory-drift.toml`
- `scripts/check_dev_environment_inventory_drift.py`
- `tests/scripts/test_check_dev_environment_inventory_drift.py`

Updated:

- `scripts/release_candidate_gate.py`
- `.githooks/pre-commit`
- `tests/scripts/test_release_candidate_gate.py`
- `docs/release/dev-environment-inventory.json`
- `docs/release/dev-environment-inventory.md`

## Behavior

The protected artifact registry is deterministic TOML. It currently covers:

- harness identity and role state;
- role and governance rules;
- hook and action-gate behavior;
- release and CI gates;
- inventory collector and inventory baseline surfaces;
- package and project config.

The checker:

- regenerates a current public inventory through
  `scripts.collect_dev_environment_inventory.collect_inventory`;
- removes configured volatile inventory fields before comparison;
- compares the normalized current inventory to
  `docs/release/dev-environment-inventory.json`;
- inspects changed Git paths and intersects them with the protected registry;
- emits human-readable or JSON output;
- returns non-zero for material unclassified drift;
- allows the pre-commit hook to pass protected staged changes only when staged
  bridge review evidence is present;
- keeps the release gate stricter by default.

## Spec-To-Test Mapping

| Linked requirement | Coverage |
|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This section maps linked requirements to executed tests and commands. |
| `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` | Bridge thread and report preserve backlog-driven implementation continuity. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `tests/scripts/test_check_dev_environment_inventory_drift.py` covers deterministic registry loading, drift outcomes, accepted baseline updates, review-evidence outcome, and root-boundary rejection. |
| `.claude/rules/project-root-boundary.md`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `test_changed_path_must_stay_inside_project_root` rejects changed paths that escape the GT-KB root. |
| `bridge/gtkb-env-inventory-001-001.md`, `bridge/gtkb-env-inventory-001-003.md`, `GTKB-ENV-INVENTORY-001` | `tests/scripts/test_release_candidate_gate.py` covers release-gate invocation; collector command regenerated public inventory artifacts. |

## Verification Commands And Results

Passed:

```powershell
python -m ruff check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py
```

Result: `All checks passed!`

Passed:

```powershell
python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py -q --tb=short
```

Result: `35 passed`.

Passed:

```powershell
python scripts/collect_dev_environment_inventory.py --public-json docs/release/dev-environment-inventory.json --public-markdown docs/release/dev-environment-inventory.md --local-json .gtkb-state/dev-environment-inventory/local.json
```

Result: public JSON, public Markdown, and local JSON were written; redaction
status was `pass`.

Passed:

```powershell
python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence
```

Result: `PASS (review_evidence_present)`.

Expected strict-gate failure on the current dirty workspace:

```powershell
python scripts/check_dev_environment_inventory_drift.py
```

Result: `FAIL (release_blocker)` with 189 changed paths, 22 protected changes,
and `Material inventory drift: False`. This is expected because the current
working tree contains many pre-existing governance, hook, workflow, harness, and
release-gate changes that now require review evidence or cleanup before release.
The failure proves the new release-gate path detects protected drift instead of
silently ignoring it.

## Residual Risk

- The checker deliberately does not infer semantic approval from arbitrary
  protected file edits. Protected changes must be paired with bridge review
  evidence for pre-commit relief or cleaned up before strict release-gate use.
- Current workspace drift is broad. A clean release candidate still requires a
  scoped commit or explicit disposition of unrelated protected changes.

## Requested Loyal Opposition Review

Please verify the implementation and decide whether the focused tests and
strict dirty-tree failure satisfy the approved proposal, or whether the checker
needs stronger acceptance evidence before `VERIFIED`.

