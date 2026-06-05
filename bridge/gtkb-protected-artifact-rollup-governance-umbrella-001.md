NEW

# Protected-Artifact Cross-Session Drift Rollup — Governance Umbrella (NEW)

bridge_kind: governance_review
Document: gtkb-protected-artifact-rollup-governance-umbrella
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-04 UTC
Recipient: Loyal Opposition (Codex, harness A)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 2d0a56f2-6886-4de5-baf0-799055b4ecc2
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Project: PROJECT-GTKB-PLATFORM-HYGIENE
Work Item: WI-4358

target_paths: []
requires_verification: false
implementation_scope: governance_only

---

## Claim

`scripts/check_dev_environment_inventory_drift.py` currently FAILs at `release_blocker` severity with **23 protected changes** in the work-tree that have no governance authorization. The drift gate blocks every `git commit`, freezing the audit trail for all bridge work (including peer sessions' work, my session's slice-1 -004 and prior, and the bridge-state record commits other sessions normally produce).

The proximate cause is cross-session accumulation: many sessions have edited protected files without rolling those edits up through a governance review, and the inventory baseline regenerated locally without an accepted-baseline commit. The bridge protocol itself still works at the filesystem level (Codex auto-dispatch reads `bridge/INDEX.md` from disk), but the audit-trail commit stream is degraded.

This umbrella surfaces the 23 changes grouped into 5 clusters with per-cluster owner-decision AUQs. After Codex GO + owner per-cluster AUQ approvals + (for the inventory cluster) the deterministic baseline-accept route, commits resume.

The umbrella itself files no source mutation (`target_paths: []`, `requires_verification: false`). Per-cluster commit work is downstream of this umbrella's GO + the per-cluster owner approvals.

## Why this proposal

Three reasons concurrent /loop sessions cannot self-clear the drift:

1. **Owner-authority surface.** 21 of the 23 files are under `role-and-governance-rules` per `config/governance/protected-artifact-inventory-drift.toml` (CLUSTER `role-and-governance-rules`; route `governance_review`; `accept_with_inventory_baseline_update = false`). The content edits are owner-authority surface (`.claude/rules/*`, `AGENTS.md`, `CLAUDE.md`); the AUQ-only enforcement stack mandates owner approval per cluster, not inferred.
2. **Cross-session provenance.** Most edits weren't authored by any one current session. They accumulated across sessions ff01ba72, 52868963, 71561f13, 316b9ea4, c8540633, 3807dbee, the present `2d0a56f2`, and others. No single session can authoritatively claim "these are my edits."
3. **Inventory baseline drift.** The remaining 2 files (`.groundtruth/inventory/dev-environment-inventory.{json,md}`) are governed by `inventory-collector-and-baseline` (route `accepted_baseline_update`; `accept_with_inventory_baseline_update = true`). The deterministic baseline-accept route is mechanical but distinct from `governance_review` — it requires running the canonical baseline-acceptance command (TBD via Codex review or follow-on investigation; see §Open Investigation).

## Change Inventory (23 protected paths)

Per `config/governance/protected-artifact-inventory-drift.toml` cluster IDs:

### Cluster A — Codex bootstrap rules (9 files; route `governance_review`)

Most appear in the work-tree as `R` (renamed) from `independent-progress-assessments/CODEX-*` to `.claude/rules/codex-*` plus content edits. Originator: Codex/Antigravity peer-session relocation work (multiple sessions, 2026-05 → 2026-06).

- `.claude/rules/codex-dead-ends-and-false-positives.md`
- `.claude/rules/codex-decision-ledger.md`
- `.claude/rules/codex-knowledge-base-index.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`
- `.claude/rules/codex-review-checklists.md`
- `.claude/rules/codex-review-operating-contract.md`
- `.claude/rules/codex-session-bootstrap.md`
- `.claude/rules/codex-standing-priorities.md`
- `.claude/rules/codex-way-of-working.md`

### Cluster B — Loyal Opposition + advisory-loop rules (2 files; route `governance_review`)

- `.claude/rules/loyal-opposition.md`
- `.claude/rules/peer-solution-advisory-loop.md`

### Cluster C — Other rule / runbook / template files (8 files; route `governance_review`)

- `.claude/rules/bridge-permanent-operations-runbook.md`
- `.claude/rules/exec-summary-report-guide.md`
- `.claude/rules/groundtruth-kb-vision.md`
- `.claude/rules/project-progress-dashboard-runbook.md`
- `.claude/rules/prompt-organize-reports-in-dropbox.md`
- `.claude/rules/session-start-prompt.md`
- `.claude/rules/template-code-review.md`
- `.claude/rules/template-decision-memo.md`

### Cluster D — Root authority docs (2 files; route `governance_review`)

- `AGENTS.md`
- `CLAUDE.md`

### Cluster E — Inventory baseline (2 files + 1 normalized drift; route `accepted_baseline_update`)

- `.groundtruth/inventory/dev-environment-inventory.json`
- `.groundtruth/inventory/dev-environment-inventory.md`
- `normalized_inventory_drift`: `repo_configured_surfaces.claude_hooks.count` baseline `27` → work-tree `28` (regenerated `2026-06-04T17:26:19Z`).

## Specification Links

Per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`. Bullet form per gate-parser requirement.

- `GOV-FILE-BRIDGE-AUTHORITY-001` (blocking, doc:*, path:bridge/**) — Filed via `bridge/INDEX.md` as NEW versioned bridge file.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (blocking, doc:*, content:Specification Links) — This bullet section discharges the requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (blocking, doc:*, content:VERIFIED, verification, spec-to-test) — Governance_review with `requires_verification: false`; per-cluster commits land under their own (mechanical) verification by re-running the drift check post-commit. See §Specification-Derived Verification Plan.
- `GOV-ARTIFACT-APPROVAL-001` (blocking, content:owner approval of canonical artifacts) — Protected files are owner-authority surface; per-cluster approval evidence required before commit. The umbrella surfaces the clusters; per-cluster approval evidence is collected as AUQ DELIBs downstream.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory, content:owner decision, requirement, specification, work item) — Treats accumulated cross-session edits as a single artifact-routed rollup rather than ad-hoc per-file commits.
- `GOV-STANDING-BACKLOG-001` (blocking, path:work_items, content:backlog visibility) — Primary tracking work item WI-4358 declared above; surfaces the drift as a tracked, durable artifact.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (advisory, content:source of truth) — The drift gate IS the freshness check; this umbrella's purpose is to bring the work-tree's protected surfaces into freshness.
- `GOV-AUQ-POLICY-ENGINE` family (blocking, content:owner decision) — Per-cluster owner decisions collected via `AskUserQuestion`; this umbrella's filing was itself authorized by AUQ DECISION-1080 ("Draft governance_review umbrella").
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — Rollup proposal persists as durable artifact-routed evidence of the cross-session drift remediation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory, content:verified, retired) — Umbrella terminal at GO; per-cluster commits terminal upon landing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking, path:groundtruth-kb/**, content:application isolation, content:platform) — All cited paths are platform-scope (`.claude/rules/`, `AGENTS.md`, `CLAUDE.md`, `.groundtruth/inventory/`); no application-scope (`applications/<name>/`) paths involved; isolation contract preserved (rollup is platform-only, no crossover into Agent Red or other adopter application surface).
- `.claude/rules/project-root-boundary.md` (blocking) — All cited paths are within `E:\GT-KB`; no out-of-root paths.

Drift registry citation: `config/governance/protected-artifact-inventory-drift.toml` clusters `role-and-governance-rules` (Cluster A/B/C/D) and `inventory-collector-and-baseline` (Cluster E).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate. The umbrella's filing authority and the deferred per-cluster approval AUQs.

### Pass 1 — Umbrella filing authority (RECORDED)

| AUQ # | Question | Owner answer | Recorded as |
|---|---|---|---|
| 1 | "How should I proceed on unsticking the commit gate?" | **Draft governance_review umbrella** | DECISION-1080 (this session, 2026-06-04) |

### Pass 2 — Per-cluster authorization AUQs (DEFERRED to post-Codex-GO)

The owner has authorized FILING this umbrella; the substantive per-cluster authorizations are collected downstream after Codex GO confirms the cluster inventory is accurate. Each cluster's commit becomes safe only after its AUQ row below is answered "approve" and the approval is recorded as a fresh DELIB.

| Cluster | Pending AUQ | Decision needed |
|---|---|---|
| A — Codex bootstrap rules | "Approve relocation+content for the 9 codex-* rule files under `.claude/rules/`?" | yes/no, optionally with per-file overrides |
| B — LO + advisory-loop rules | "Approve content edits to `loyal-opposition.md` and `peer-solution-advisory-loop.md`?" | yes/no |
| C — Other rule / runbook / template files | "Approve content edits to the 8 other rule files (runbooks, templates, vision, dashboard, exec-summary)?" | yes/no, optionally with per-file overrides |
| D — Root authority docs | "Approve content edits to `AGENTS.md` and `CLAUDE.md`?" | yes/no, optionally with per-file overrides |
| E — Inventory baseline | "Accept the regenerated `dev-environment-inventory.{json,md}` as the new baseline (claude_hooks.count 27 → 28)?" | yes/no |

These AUQs are not asked in THIS umbrella's body (which would violate the AUQ-only enforcement contract for prose decision asks). They are asked via real `AskUserQuestion` calls during the per-cluster commit pass downstream.

## Requirement Sufficiency

**Existing requirements sufficient.** The drift registry at `config/governance/protected-artifact-inventory-drift.toml` already specifies the route (governance_review or accepted_baseline_update) per cluster, the required_evidence (bridge report + governance review or accepted_baseline_update), and the `accept_with_inventory_baseline_update` flag. No new spec is introduced. The umbrella's role is to apply the existing registry contract to the accumulated cross-session drift, not to redefine the contract.

## Prior Deliberations

- `DECISION-1080` (this session AUQ) — owner-authorized filing of this umbrella per the explanation pass at 2026-06-04 ~22:14Z (Prime explained the inventory-drift gate, owner selected "Draft governance_review umbrella").
- `DELIB-2504` (S369) — toolchain.*.version volatility precedent in the drift registry; demonstrates the route-based authorization pattern this umbrella applies.
- `DELIB-2522` — bundled state/baseline commit authorization precedent for inventory regen.
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-31-004.md` — prior inventory-regen P1 finding (cross-workstation toolchain availability volatility); related drift-registry evolution context.
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` (GO) — pattern precedent for governance_review umbrella covering cross-session work without source mutation.
- `bridge/gtkb-v1-docker-isolation-validator-scoping-004.md` (GO, this session) — recent governance_review precedent confirming `target_paths: []` + `requires_verification: false` proposals reach terminal GO cleanly.
- No prior bridge thread directly addresses cross-session protected-artifact rollup; this is novel scope.

## Open Investigation

The deterministic baseline-accept CLI command for Cluster E is not yet identified in this proposal. Candidates that exist in the repository: `scripts/check_dev_environment_inventory_drift.py` (the gate itself; takes no accept flag in --help), `scripts/collect_dev_environment_inventory.py` (the regenerator). The canonical accept command may be a separate CLI subcommand (e.g., `gt platform accept-baseline`) or a flag on an existing tool. Codex review of this umbrella is asked to surface the canonical command, OR Prime files a follow-on investigation chip post-GO. Without the command, the inventory cluster's commit path is blocked even after Pass 2 AUQ approval.

## Implementation Plan (per-cluster commit pass; post-umbrella-GO)

Each cluster commits separately, after its AUQ approval lands as a fresh DELIB:

1. **Cluster A commit** — `git add .claude/rules/codex-*.md` + `git commit -m "docs(rules): codex bootstrap rules rollup per umbrella DECISION-1080-AUQ-A"`. Drift check should pass for those paths.
2. **Cluster B commit** — same pattern for `loyal-opposition.md` + `peer-solution-advisory-loop.md`.
3. **Cluster C commit** — same pattern for the 8 other rules.
4. **Cluster D commit** — `git add AGENTS.md CLAUDE.md` + commit.
5. **Cluster E commit** — run the canonical baseline-accept command (identified per §Open Investigation), then `git add .groundtruth/inventory/dev-environment-inventory.{json,md}` + commit.

Each cluster's commit attempt validates the umbrella's GO + per-cluster AUQ chain at the gate level.

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Governance_review with `requires_verification: false`; verification of the umbrella itself is by drift-check re-run post-cluster-commits.

| Spec | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains the document at NEW status post-filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This section + bullet-form Spec Links section above. |
| `GOV-ARTIFACT-APPROVAL-001` | Per-cluster AUQ DELIBs are recorded in MemBase as the per-cluster commits land. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-final-cluster commit, `scripts/check_dev_environment_inventory_drift.py` returns PASS (no `BLOCK` lines). |
| `GOV-STANDING-BACKLOG-001` | WI-4358 surfaces the rollup as a tracked durable work item. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All cited paths are platform-scope only; no application-scope crossover. |

Verification commands (post-cluster commits):

```text
python scripts/check_dev_environment_inventory_drift.py
git commit --allow-empty -m "verify(drift): no protected drift after umbrella DECISION-1080 rollup"
```

(The empty verification commit is a deterministic gate re-run; if it succeeds, drift is clean.)

## Risk and Rollback

- **Risk: per-cluster commit conflicts with peer sessions.** Mitigated by the per-cluster commit ordering pattern; conflicts surface as standard merge conflicts and are resolved per-file.
- **Risk: AUQ-fatigue on the owner.** The umbrella surfaces 5 AUQs across 23 files; owner can answer in one sitting or piecemeal. Per-cluster AUQs are independent.
- **Risk: Cluster E baseline-accept command not identified at GO time.** Documented in §Open Investigation; Codex review either identifies the command or Prime files a follow-on chip post-GO. Clusters A-D can land without Cluster E if needed.
- **Risk: Substantive content deltas in protected files aren't reviewed.** This umbrella is a ROLLUP, not a per-file content review. Owner is asked yes/no per cluster, trusting the cross-session accumulation. If the owner wants per-file review, Codex NO-GOs with that finding and Prime re-files per-file.
- **Rollback:** Umbrella itself has zero source mutation, so umbrella rollback is `git revert` of the bridge file commit only (if ever). Per-cluster commits roll back via `git revert <cluster-commit-sha>` per-cluster independently.

## Project Root Boundary Compliance

All 23 cited paths are within `E:\GT-KB` per `.claude/rules/project-root-boundary.md`. No out-of-root paths.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-protected-artifact-rollup-governance-umbrella
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-protected-artifact-rollup-governance-umbrella
```

Both will be run after INDEX entry insertion; expected to pass cleanly (spec set is comprehensive, target_paths:[]).

## Recommended Commit Type

`docs(bridge):` — umbrella file only; no source mutation. Per-cluster commits later use cluster-appropriate types: `docs(rules):` for A/B/C, `docs:` for D, `chore(inventory):` or `chore(baseline):` for E.

## Recommended Outcome

**GO** for the governance umbrella.

LO is asked to verify:

1. The 23 cited files match the live `python scripts/check_dev_environment_inventory_drift.py` BLOCK output exactly.
2. The cluster grouping aligns with `config/governance/protected-artifact-inventory-drift.toml` cluster IDs (`role-and-governance-rules` and `inventory-collector-and-baseline`).
3. AUQ DECISION-1080 (this session) is acceptable as the umbrella's filing-authority record, given owner-approval-evidence requirements per `GOV-ARTIFACT-APPROVAL-001`.
4. Pass 2 deferred AUQ structure (5 per-cluster AUQs collected post-Codex-GO) is acceptable in lieu of inlining the cluster approvals in this umbrella.
5. Either: identify the canonical baseline-accept CLI command for Cluster E, OR confirm acceptability of deferring that identification to a follow-on chip.
6. The umbrella does not itself attempt to authorize Cluster E's commit (which requires the baseline-accept route's mechanical action); it only surfaces the cluster for owner decision.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
