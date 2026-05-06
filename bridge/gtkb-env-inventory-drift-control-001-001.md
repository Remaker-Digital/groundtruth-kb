NEW

# Implementation Proposal - GTKB-ENV-INVENTORY-DRIFT-CONTROL-001: Inventory Baseline Drift Control for Protected Artifacts

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-06
**Type:** Governance/release-gate/checkin enforcement proposal
**Risk tier:** Medium (checkin and release-gate enforcement; no production deployment)
**Backlog item:** `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 - Inventory baseline drift control for protected artifacts`

target_paths: ["config/governance/protected-artifact-inventory-drift.toml", "scripts/check_dev_environment_inventory_drift.py", "scripts/collect_dev_environment_inventory.py", "scripts/release_candidate_gate.py", ".githooks/pre-commit", ".github/workflows/**", "docs/release/dev-environment-inventory.json", "tests/scripts/test_check_dev_environment_inventory_drift.py", "tests/scripts/test_release_candidate_gate.py"]

---

## Background

`GTKB-ENV-INVENTORY-001` establishes the baseline harness and development
environment inventory: a release-safe public artifact, a private local artifact,
redaction checks, and release-gate freshness enforcement. That is necessary but
not sufficient for change control. A current inventory can still be a passive
snapshot if protected artifacts change without an inventory-baseline update or a
reviewable drift classification.

The owner clarified the intended use on 2026-05-06: use the inventory to
identify drift by verifying inventory, then evaluate and confirm changes or
flag them for further implementation work, documentation review, or application
compatibility tests. This proposal turns that intent into a mechanical
checkin/release control.

This proposal intentionally separates two control layers:

- **Hard gate:** normalized inventory diff enforcement at checkin, CI, and
  release-candidate-gate time.
- **Best-effort early warning:** optional per-command or per-hook warnings when
  a protected artifact mutation flows through known GT-KB tooling.

Per-CRUD enforcement is useful where GT-KB owns the mutation path, but it should
not be the source of truth. Manual edits, generated output, Git operations, and
external tools do not share one reliable CRUD interception point.

## Current Evidence Snapshot

| Evidence | Source | Relevance |
|---|---|---|
| Inventory implementation proposal exists | `bridge/gtkb-env-inventory-001-001.md` | Defines the baseline inventory artifact, redaction model, and release-gate integration this item extends |
| Inventory implementation report is filed | `bridge/gtkb-env-inventory-001-003.md` | Records the implemented public/private inventory split and release-candidate-gate freshness check |
| Backlog follow-on is recorded | `memory/work_list.md` row `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001` | Preserves the owner-directed change-control follow-on as standing backlog work |
| Public inventory artifact exists | `docs/release/dev-environment-inventory.json` | Provides the committed baseline a normalized drift check can compare against |
| Release gate already validates inventory freshness | `scripts/release_candidate_gate.py` | Natural integration point for a material-drift hard gate |
| Inventory collector already produces public and local views | `scripts/collect_dev_environment_inventory.py` | Natural source for regenerating a temporary current inventory during diff checks |

## Specification Links

Cross-cutting bridge requirements:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) - `bridge/INDEX.md` is the live
  authority for this proposal. Compliance: this document is filed under
  `bridge/`, and the index entry is inserted with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) -
  implementation proposals must cite relevant governing specifications.
  Compliance: this section links bridge, backlog, artifact-governance,
  root-boundary, isolation, and testing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) - a later
  implementation report must carry these links forward and map executed tests
  to linked requirements. Compliance: this proposal includes a
  specification-derived verification plan.

Standing-backlog authority:

- `GOV-STANDING-BACKLOG-001` v2 (verified) - the standing backlog is durable
  cross-session work authority. Compliance: `memory/work_list.md` now records
  this owner-directed follow-on item.
- `PB-STANDING-BACKLOG-CONTINUITY-001` (verified) - Prime Builder must not
  bypass standing backlog continuity. Compliance: this proposal preserves the
  owner-stated change-control purpose and routes it through the bridge.
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` (verified) - backlog items are
  selectable work authority. Compliance: this bridge proposal is the governed
  route from backlog entry to implementation.

Artifact-oriented governance:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) - concrete requirements,
  risks, procedures, and future work should be preserved as durable artifacts.
  Compliance: protected-artifact policy, drift classifications, and baseline
  changes become inspectable artifacts instead of chat-only judgments.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) - project memory is a
  traceable artifact graph. Compliance: drift findings link protected paths,
  inventory deltas, classification, and required follow-on action.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) - artifact lifecycle states
  must be explicit. Compliance: drift outcomes are explicit states such as
  accepted baseline update, documentation review, compatibility test, further
  work, local-only notice, and release blocker.

Role, bridge, and root-boundary rules:

- `.claude/rules/file-bridge-protocol.md` - governs proposal filing, `GO`,
  implementation reports, and `VERIFIED`.
- `.claude/rules/codex-review-gate.md` - forbids implementation changes before
  Loyal Opposition `GO` when the bridge is active.
- `.claude/rules/deliberation-protocol.md` - requires deliberation search and
  citation before proposal filing.
- `.claude/rules/canonical-terminology.md` - defines GT-KB, Internal Developer
  Platform, application, work item, bridge, MemBase, Prime Builder, and Loyal
  Opposition terminology used here.
- `.claude/rules/operating-model.md` - defines platform/application isolation,
  backlog, work item, specification, implementation proposal, implementation
  report, verification, and release.
- `.claude/rules/project-root-boundary.md` - all active GT-KB files must remain
  under `E:\GT-KB`; GT-KB application files must remain under
  `E:\GT-KB\applications\`. Compliance: all target paths remain inside the
  GT-KB root.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) - application/root
  placement and platform/application isolation must be respected. Compliance:
  this proposal protects GT-KB platform artifacts and treats application
  compatibility tests as downstream verification, not as permission to write
  live application files outside the GT-KB boundary.

Related inventory authority:

- `bridge/gtkb-env-inventory-001-001.md` - source proposal for the baseline
  development-environment inventory.
- `bridge/gtkb-env-inventory-001-003.md` - implementation report for inventory
  collector, public/private artifacts, and release-gate freshness checks.
- `GTKB-ENV-INVENTORY-001` - parent backlog item; this proposal is a follow-on
  drift-control layer rather than a replacement.

The proposed tests derive from these linked specs as follows: bridge authority
drives index/preflight checks; standing backlog specs drive evidence that this
item is recorded before implementation; artifact-governance specs drive durable
registry and drift-classification tests; root-boundary/isolation specs drive
path containment and application-boundary tests; verified-spec testing drives
the implementation report's spec-to-test mapping.

## Prior Deliberations

Searches performed per `.claude/rules/deliberation-protocol.md`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "development environment inventory drift protected artifacts checkin change control" --limit 10
python -m groundtruth_kb deliberations search "GTKB-ENV-INVENTORY-001 baseline inventory release gate protected artifact drift" --limit 10
python -m groundtruth_kb deliberations search "pre commit inventory drift CI baseline protected artifact" --limit 10
```

Relevant results and adjacent evidence:

| Record | Relevance |
|---|---|
| `DELIB-0108` | Earlier Loyal Opposition/Prime Builder pattern refinement; relevant to bridge-mediated review discipline |
| `DELIB-1369` | Isolation review context; relevant to protected platform/application boundaries |
| `DELIB-1336` | Application-boundary audit context; relevant to avoiding cross-boundary enforcement mistakes |
| `DELIB-0563` | Non-disruptive upgrade certification context; relevant to compatibility-test routing for material drift |
| `DELIB-0639` | Appeared in baseline/pre-commit searches; adjacent evidence for pre-commit/checkin enforcement concerns |
| `DELIB-0877` | Appeared in pre-commit drift search; adjacent evidence for checkin-path governance |
| `DELIB-1390` | Appeared in pre-commit drift search; adjacent evidence for recent governance/checkin enforcement |
| `DELIB-1042`, `DELIB-1045` | Appeared in baseline inventory searches; adjacent evidence for release/baseline governance context |

No search result found an owner decision rejecting inventory drift control. The
searches did surface related isolation, pre-commit, and release-baseline
concerns; this proposal uses them as cautionary context, not as a substitute for
the owner directive in this session.

## Owner Decisions And Input

No new owner decision is needed to file this proposal. The owner explicitly
asked on 2026-05-06 to add the drift/change-control concept to the backlog and
create an implementation proposal.

Owner intent captured for implementation:

- Inventory should help identify drift by verifying the current inventory
  against a baseline.
- Confirmed changes can be accepted and documented.
- Unconfirmed or risky changes should be flagged for further work,
  documentation review, or application compatibility tests.
- Mechanical checkin diff enforcement is feasible and worthwhile.
- Per-CRUD enforcement may be useful, but it is not reliable enough to be the
  only control.

## Proposed Implementation

### Slice 1 - Protected Artifact Registry

Create `config/governance/protected-artifact-inventory-drift.toml` with
registry entries for protected surfaces whose changes can alter GT-KB's
operating environment or governance behavior. Initial classes:

| Class | Example paths | Default drift route |
|---|---|---|
| Harness identity and role state | `harness-state/harness-identities.json`, `harness-state/role-assignments.json` | governance review |
| Role and governance rules | `.claude/rules/**`, `AGENTS.md`, `CLAUDE.md` | governance review |
| Hook and action-gate behavior | `.claude/hooks/**`, `.codex/gtkb-hooks/**`, `.githooks/**` | compatibility tests plus governance review |
| Release and CI gates | `scripts/release_candidate_gate.py`, `.github/workflows/**` | release blocker until accepted |
| Inventory collector and baseline | `scripts/collect_dev_environment_inventory.py`, `docs/release/dev-environment-inventory.json` | accepted baseline update or drift review |
| Package/config surfaces | `groundtruth.toml`, `groundtruth-kb/pyproject.toml` | documentation review plus compatibility tests |

The registry should be deterministic TOML, not an LLM classifier. Each entry
should include path pattern, owner/review route, severity, required evidence,
and whether an inventory-baseline update is mandatory.

### Slice 2 - Normalized Inventory Drift Checker

Add `scripts/check_dev_environment_inventory_drift.py`.

Responsibilities:

- Regenerate a temporary current public inventory using
  `scripts/collect_dev_environment_inventory.py`.
- Normalize volatile fields before comparison, including generation timestamp,
  elapsed age, local absolute cache/output paths, and any field explicitly
  marked volatile by the inventory schema.
- Compare normalized current inventory with
  `docs/release/dev-environment-inventory.json`.
- Inspect Git changed paths, when available, and intersect them with protected
  artifact registry patterns.
- Emit machine-readable JSON and a concise human-readable summary.
- Return non-zero when material protected drift is unclassified or when a
  protected artifact changed without an accepted inventory-baseline update.

The checker should distinguish these outcomes:

| Outcome | Meaning | Gate behavior |
|---|---|---|
| `clean` | No material normalized drift and no protected path mismatch | pass |
| `accepted_baseline_update` | Inventory baseline changed with a matching protected change and acceptable classification | pass |
| `docs_review` | Change requires documentation review before release | fail release until resolved unless explicitly waived |
| `compatibility_tests` | Change requires application compatibility tests | fail release until tests run or waiver is recorded |
| `further_work` | Change requires implementation follow-up | fail |
| `local_only_notice` | Private/local-only state changed without public release impact | warn |
| `release_blocker` | Material drift with no acceptable route | fail |

### Slice 3 - Checkin And Release-Gate Integration

Integrate the checker with:

- `.githooks/pre-commit` or the repo's current checkin hook path, so local
  checkin fails on protected drift unless the inventory baseline and
  classification are updated.
- `scripts/release_candidate_gate.py`, so release packaging cannot proceed with
  unclassified material drift.
- CI workflow checks where GT-KB already runs release-candidate-gate validation.

This slice should not rely on GitHub branch-protection settings or production
deployment approvals; those are out of scope for this proposal.

### Slice 4 - Optional Early Warnings

Add optional early warnings only where GT-KB already owns the mutation path.
Examples: a `gt` command that updates a protected artifact can print or return
the expected inventory-drift follow-up. These warnings are additive. The hard
control remains checkin/CI/release-gate enforcement.

### Slice 5 - Tests And Documentation

Add focused tests under `tests/scripts/`:

- protected-registry loading and path classification;
- normalization excludes volatile fields;
- material drift is detected;
- protected path change without inventory update fails;
- inventory baseline update with acceptable classification passes;
- private/local redaction boundaries remain intact;
- optional unknown/unsupported tool states remain non-fatal unless marked
  blocking;
- release-candidate-gate invokes the drift checker by default;
- `--skip-dev-inventory` or equivalent skip behavior does not silently skip the
  new drift checker unless explicitly documented and tested.

Documentation should be compact and operational: explain how to update the
inventory baseline, how to classify drift, and what evidence is needed for
docs review or compatibility tests.

## Acceptance Criteria

- `memory/work_list.md` records
  `GTKB-ENV-INVENTORY-DRIFT-CONTROL-001`.
- `bridge/INDEX.md` records this proposal as latest `NEW`.
- A protected-artifact registry exists and is covered by tests.
- A normalized inventory drift checker exists and returns stable machine-readable
  output.
- Checkin/release-gate paths fail on unclassified material drift.
- Volatile inventory fields do not cause false-positive drift.
- Public/private redaction boundaries from `GTKB-ENV-INVENTORY-001` remain
  intact.
- Implementation report maps each linked specification to executed tests.

## Out Of Scope

- Credential rotation or secret lifecycle changes.
- Production or staging deployment.
- GitHub repository settings, branch-protection mutation, or required-review
  configuration.
- Treating per-CRUD hooks as the sole enforcement mechanism.
- Formal GOV/ADR/DCL promotion beyond the proposal's implementation artifacts.
- Blocking every file change in the repository; scope is protected artifacts
  whose changes can materially affect inventory, harness behavior, governance,
  hooks, CI/release gates, or application compatibility.

## Specification-Derived Verification Plan

| Test ID | Linked requirement | Verification |
|---|---|---|
| T-preflight | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-env-inventory-drift-control-001` reports no missing required specs |
| T-backlog | `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` | `rg "GTKB-ENV-INVENTORY-DRIFT-CONTROL-001" memory/work_list.md bridge/INDEX.md bridge/gtkb-env-inventory-drift-control-001-001.md` finds all governing locations |
| T-registry | `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Unit tests prove protected-path classes and drift outcome states are deterministic |
| T-normalized-diff | `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Unit tests prove volatile fields are ignored and material fields are detected |
| T-root-boundary | `.claude/rules/project-root-boundary.md`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests and path assertions prove the checker stays within `E:\GT-KB` and does not treat external Agent Red files as live GT-KB artifacts |
| T-release-gate | `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` exercises the drift gate after implementation |

## Recommended Verdict

`GO`, with the expected Loyal Opposition review focus on:

- whether the proposed protected-artifact registry is too broad or too narrow;
- whether the drift classifications are deterministic enough for a gate;
- whether pre-commit/release-gate integration is sufficient before adding
  optional per-command warnings;
- whether the implementation must be sliced further to keep the first patch
  reviewable.
