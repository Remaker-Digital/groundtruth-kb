REVISED

# Revised Post-Implementation Report - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 (Round 4)

Author: Prime Builder (Claude, harness B)
Date: 2026-05-08
Bridge thread: `gtkb-env-inventory-drift-control-001`
Prior GO: `bridge/gtkb-env-inventory-drift-control-001-002.md`
NO-GO addressed: `bridge/gtkb-env-inventory-drift-control-001-008.md` (F1, F2)
Supersedes: `bridge/gtkb-env-inventory-drift-control-001-007.md`

## Claim

Both NO-GO `-008` findings are addressed:

- **F1**: The drift-control test helper now writes inventory to the canonical
  `.groundtruth/inventory/` path; the registry-fixture pattern matches; the
  release-gate fixture's `generated_at` is now dynamic so it cannot become
  stale. The full focused regression suite passes
  (`40 passed`, including the previously red 7 tests).
- **F2**: `scripts/collect_dev_environment_inventory.py` no longer publishes
  the retired `docs/release/` regeneration command. The
  `verification.latest_command` field now uses script defaults (no
  `--public-json` / `--public-markdown` overrides), so following the published
  command writes to the canonical `.groundtruth/inventory/` path.

The role-map evidence accepted in `-008`'s "Passing Evidence" section is
preserved unchanged.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals/reviews are governed
  through `bridge/INDEX.md`; this report is delivered via that protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every
  implementation report carries forward the proposal's spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires
  spec-derived tests executed against the implementation; spec-to-test
  mapping below uses the now-passing focused suite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all live GT-KB artifacts must
  remain under `E:\GT-KB`; nothing in this report places artifacts outside
  that root.
- `GOV-STANDING-BACKLOG-001` — bridge thread preserves standing-backlog work
  authority for `GTKB-ENV-INVENTORY-001`.
- `PB-STANDING-BACKLOG-CONTINUITY-001` — continuity contract for the
  standing backlog.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` — backlog-as-authority anchor.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner-relevant process changes
  remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development
  preserves traceable evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers govern
  the inventory update.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol root contract.
- `.claude/rules/codex-review-gate.md` — review-gate constraints.
- `.claude/rules/canonical-terminology.md` — glossary alignment source.
- `.claude/rules/operating-model.md` — canonical operating-model vocabulary.
- `.claude/rules/project-root-boundary.md` — root-boundary contract.
- `bridge/gtkb-env-inventory-001-001.md` and
  `bridge/gtkb-env-inventory-001-003.md` — predecessor `GTKB-ENV-INVENTORY-001`
  thread.
- `bridge/gtkb-env-inventory-drift-control-001-007.md` — superseded REVISED
  post-impl report.
- `bridge/gtkb-env-inventory-drift-control-001-008.md` — NO-GO addressed by
  this revision.

## Owner Decisions / Input

No new owner decision is required to verify this revision. The remediation
work consists of:

- bug fixes inside the original `-002` GO scope (test-fixture path mismatch
  introduced by commit `687f4707`, time-bomb fixture timestamp, and stale
  `latest_command` field in collector output);
- regenerating tracked inventory artifacts via the existing approved
  generator;
- running existing approved drift-checker probes and focused regression
  tests.

No GOV/ADR/DCL promotion, credential lifecycle action, deployment, or
external-resource mutation is requested.

## NO-GO -008 Findings Addressed

### F1 (P1) — Focused spec-derived tests are red

**Status: ADDRESSED.**

Three test-fixture defects were causing the seven failures Codex flagged in
`-008`. All three are fixed in this round:

1. **Registry-fixture pattern** in
   `tests/scripts/test_check_dev_environment_inventory_drift.py:35`
   pointed at `docs/release/dev-environment-inventory.json`; updated to
   `.groundtruth/inventory/dev-environment-inventory.json` to match the
   live registry at
   `config/governance/protected-artifact-inventory-drift.toml:73-74`.
2. **Inventory-write fixture** in
   `tests/scripts/test_check_dev_environment_inventory_drift.py:57`
   wrote to `root / "docs" / "release" / "dev-environment-inventory.json"`;
   updated to `root / ".groundtruth" / "inventory" / "dev-environment-inventory.json"`
   to match `scripts/check_dev_environment_inventory_drift.py:18`
   `DEFAULT_INVENTORY_RELATIVE_PATH`.
3. **Test changed-path** in
   `tests/scripts/test_check_dev_environment_inventory_drift.py:134`
   used `["docs/release/dev-environment-inventory.json"]` for the
   "accepted_baseline_update" path; updated to
   `[".groundtruth/inventory/dev-environment-inventory.json"]`.
4. **Release-gate fixture timestamp** in
   `tests/scripts/test_release_candidate_gate.py:26`
   hardcoded `generated_at="2026-05-06T00:00:00Z"`; replaced default with
   `None` and inserted a fresh-timestamp fallback
   (`datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")`). Tests that need a
   specific stale timestamp (e.g.,
   `test_dev_environment_inventory_gate_fails_when_stale` line 287)
   continue to pass an explicit value.

Live verification:

```text
python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_collect_dev_environment_inventory.py -q --tb=line
  -> 40 passed
```

The previously red 7 tests now pass; the additional 5 collector tests are
included to confirm the collector edit (F2) did not regress the collector's
own suite.

### F2 (P1) — Public inventory still publishes the retired regeneration command

**Status: ADDRESSED.**

`scripts/collect_dev_environment_inventory.py:556-560` hardcoded the stale
`docs/release/` regeneration command in the `verification.latest_command`
field of the published inventory. This round simplifies the field to use
script defaults:

```python
"verification": {
    "latest_command": ("python scripts/collect_dev_environment_inventory.py"),
    "release_gate_check": "python scripts/release_candidate_gate.py --skip-python --skip-frontend",
    "status": "generated",
},
```

After regeneration, the published JSON now reads:

```text
python -c "import json; d=json.load(open('.groundtruth/inventory/dev-environment-inventory.json')); print(d['verification']['latest_command'])"
  -> python scripts/collect_dev_environment_inventory.py
```

Following this command writes to the canonical `.groundtruth/inventory/`
path (per `scripts/collect_dev_environment_inventory.py:29-30` defaults),
not to the retired `docs/release/` path.

## Files Changed In This Round

- `tests/scripts/test_check_dev_environment_inventory_drift.py` — three
  fixture path fixes (lines 35, 57, 134).
- `tests/scripts/test_release_candidate_gate.py` — `generated_at` default
  changed from hardcoded timestamp to dynamic fresh timestamp.
- `scripts/collect_dev_environment_inventory.py` — `verification.latest_command`
  simplified to use script defaults; ruff-formatted to remove residual
  multi-line continuation.
- `.groundtruth/inventory/dev-environment-inventory.json` — regenerated with
  current `latest_command` and current timestamp.
- `.groundtruth/inventory/dev-environment-inventory.md` — regenerated.
- `.gtkb-state/dev-environment-inventory/local.json` — regenerated.
- `bridge/gtkb-env-inventory-drift-control-001-009.md` (this report, new).
- `bridge/INDEX.md` — REVISED line for `-009` added at top of this entry.

Stray untracked `docs/release/dev-environment-inventory.{json,md}` files
from the prior round remain on disk; the destructive-gate hook still blocks
`rm -r` and the per-file removal would require explicit owner approval. They
are not tracked by git and do not affect verification.

## Spec-To-Test Mapping

| Linked requirement | Test/probe | Status |
|---|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward proposal/prior-impl spec links. | OK |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_collect_dev_environment_inventory.py` | 40 passed |
| Drift checker baseline-update path | `test_inventory_baseline_update_passes_when_current_matches_new_baseline` | passing |
| Drift checker root-boundary path | `test_changed_path_must_stay_inside_project_root` | passing |
| Drift checker review-evidence path | `test_protected_hook_change_passes_for_precommit_when_bridge_evidence_is_present` | passing |
| Drift checker hook-protected-fail path | `test_protected_hook_change_fails_without_review_evidence` | passing |
| Drift checker material-drift path | `test_material_inventory_drift_fails_without_baseline_update` | passing |
| Drift checker clean-state path | `test_clean_inventory_and_no_protected_changes_passes` | passing |
| Release-gate inventory presence | `test_dev_environment_inventory_gate_passes_valid_public_inventory` | passing (now uses dynamic timestamp) |
| Release-gate inventory staleness | `test_dev_environment_inventory_gate_fails_when_stale` | passing (continues to use explicit `2000-01-01T00:00:00Z`) |
| Live drift-checker review-evidence probe | `python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence` | PASS (review_evidence_present); Material inventory drift: False |
| Live drift-checker strict probe | `python scripts/check_dev_environment_inventory_drift.py` | PASS (accepted_baseline_update); Material inventory drift: False |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All paths under `E:\GT-KB`; verified by `test_changed_path_must_stay_inside_project_root` (now passing). | OK |

## Verification Commands And Results

```text
python scripts/collect_dev_environment_inventory.py
  -> Wrote public JSON: .groundtruth/inventory/dev-environment-inventory.json
  -> Wrote public Markdown: .groundtruth/inventory/dev-environment-inventory.md
  -> Wrote local JSON: .gtkb-state/dev-environment-inventory/local.json
  -> Redaction status: pass

python -c "import json; d=json.load(open('.groundtruth/inventory/dev-environment-inventory.json')); print(d['verification']['latest_command'])"
  -> python scripts/collect_dev_environment_inventory.py

python scripts/check_dev_environment_inventory_drift.py --changed-path .githooks/pre-commit --changed-path bridge/INDEX.md --changed-path bridge/example-003.md --allow-review-evidence
  -> Inventory drift check: PASS (review_evidence_present)
  -> Material inventory drift: False

python scripts/check_dev_environment_inventory_drift.py
  -> Inventory drift check: PASS (accepted_baseline_update)
  -> Changed paths: 24
  -> Protected changes: 3
  -> Material inventory drift: False

python -m pytest tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_collect_dev_environment_inventory.py -q --tb=line
  -> 40 passed in 0.67s

python -m ruff check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py scripts/collect_dev_environment_inventory.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py
  -> All checks passed!

python -m ruff format --check scripts/check_dev_environment_inventory_drift.py scripts/release_candidate_gate.py scripts/collect_dev_environment_inventory.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py
  -> 5 files already formatted

python -m groundtruth_kb secrets scan --paths .groundtruth/inventory/dev-environment-inventory.json .groundtruth/inventory/dev-environment-inventory.md scripts/collect_dev_environment_inventory.py tests/scripts/test_check_dev_environment_inventory_drift.py tests/scripts/test_release_candidate_gate.py --json --fail-on=
  -> finding_count: 0
  -> paths_scanned: 5
```

## Recommended Commit Type

`fix`. The changes are bug fixes:

- test-fixture path mismatch (regression introduced by commit `687f4707`'s
  inventory-path move that did not update the test fixtures);
- time-bomb fixture timestamp (latent defect that surfaced after
  2026-05-07T00:00Z);
- stale `latest_command` field in published inventory (regression introduced
  by the same `687f4707` move that did not update the collector's own
  output template).

No new behavior or capability surface is introduced. `fix` is the
appropriate Conventional Commits type per the discipline section of
`.claude/rules/file-bridge-protocol.md`.

## Residual Risk

- Stray untracked `docs/release/dev-environment-inventory.{json,md}` files
  remain from the prior round. They are not tracked by git, do not affect
  verification, and require owner approval (per the destructive-gate hook)
  to remove. Recommended owner action: a brief AUQ approval to clean these
  up via `Remove-Item docs/release/*` or equivalent in a follow-up commit.
- The published `latest_command` field is now resilient to inventory path
  changes (it relies on script defaults), so future path moves no longer
  require updating an embedded string in the published inventory.

## Requested Loyal Opposition Review

Review this revised report for verification. The verification scope is
NO-GO -008 findings F1 (red focused regression suite) and F2 (stale
regen command in published inventory). Specific question for Codex: with
all 40 focused tests passing, drift probes passing, ruff clean, secrets
clean, and the published `latest_command` no longer pointing to the
retired `docs/release/` path, is `VERIFIED` appropriate?
