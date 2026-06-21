# GroundTruth-KB Platform Memory — Index

> MEMORY.md is the operational-notepad **INDEX**, not a content store or backlog
> authority. Canonical knowledge lives in MemBase (`groundtruth.db`); design
> reasoning lives in the Deliberation Archive (`gt deliberations`); per-session
> detail lives in git history (referenced commits) and `bridge/*-NNN.md`. The
> backlog authority is the MemBase `work_items` table via `gt backlog list`.
>
> Slice 8 of `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` (WI-4346/WI-4347) reduced
> this file from a ~109 KB session-state log to this index; the retired session
> ephemera remain recoverable in git history.

## Session Bootstrap
- Location: `E:\GT-KB`; key files: `CLAUDE.md`, this index.
- Role: resolved from `harness-state/harness-registry.json` (`gt harness roles`).
- Bridge: `gt bridge dispatch status` + status-bearing `bridge/*-NNN.md`.
- Backlog: `gt backlog list`. Recent-session detail: git history + `bridge/`.

## Quick Reference
- **Active branch:** `develop`
- **Virtual env:** `E:\GT-KB\groundtruth-kb\.venv`
- **Test runner:** `python -m pytest platform_tests/`
- **CI / CD:** `npx playwright test`
- **Live web UI:** `localhost:8090`
- **CLI prefix:** `gt` / `python -m groundtruth_kb`
- **Registry:** `config/registry/sot-artifacts.toml` (`gt registry validate` / `gt registry sync`)

## Protected Files (DO NOT MODIFY)
- `.claude/settings.json`
- `.codex/hooks.json`

## Recent Sessions
Per-session detail lives in git history (referenced commits) and `bridge/*-NNN.md`.
Pre-S398 history: [CLAUDE_ARCHIVE.md](CLAUDE_ARCHIVE.md).
- **S457** (2026-06-21, Claude B): drove **PROJECT-GTKB-ENV-INVENTORY-DRIFT-CONTROL-001 (+subproject) → retired**. Subproject `…-PROTECTED-ARTIFACTS` sole WI already VERIFIED (`gtkb-env-inventory-drift-control-001-010`) → `projects retire`. **Interrogative-default catch:** WI-3452 (toolchain `status`/`classification` drift, broken-tool envs) was marked open with "options a/b/c/d to evaluate" but its fix already landed+VERIFIED under **WI-3449** via `gtkb-inventory-regen-chore-commit-2026-05-31-010` (commits `7f859fef3`/`df7281efc`; refined option-a makes status/classification volatile but keeps `evidence` probe field gating, mitigating the S369 deferral) → resolved WI-3452 as reconciliation (not re-impl, owner AUQ "drive+retire") → retired parent. Filed **WI-4726** (consideration, `approval_state=unapproved`: fast-lane/regen bridge threads should cite the WI they close + doctor check for resolved-fix-but-open-WI drift; ~58% of threads carry WI metadata). 14/14 `test_check_dev_environment_inventory_drift.py` pass. Zero file edits; MemBase-only mutations (groundtruth.db); no git commit. Reusable: when asked to "drive a WI", grep code/`git log -S`/sibling regen threads first — the fix may already be landed (reconcile, don't re-implement).
- **S456** (2026-06-21, Claude B): drove **PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION → retired** (12/12 WIs VERIFIED). Slice 8 (51 ephemera deleted + MEMORY.md→index, WI-4346/4347), gap-closure (WI-4345 SoT-read clause + WI-4350 glossary), WI-4348 Phase-1 (3 rule-file role-state pointer-swaps), WI-4681 (scratchpad boundary, verify-by-reference under owner waiver `DELIB-20265510`) — all GO→impl→VERIFIED; reconciled 4 VERIFIED-but-open drift WIs (4340/4343/4347/4350); manual `gt projects retire` (WI-4384 auto-engine gap). Recovered 3 finalization-NO-GO classes: staged-foreign-file index contamination, CRLF/packet-hash mismatch (LF-normalize), empty-diff verify-by-reference.
- **S455** (2026-06-21, Antigravity C): post-crash resume; ran bridge trigger diagnostics, resolved launch block and forced dispatch of Codex LO; verified failover/cooldown logic (8 tests passed).
- **S454** (2026-06-21, Claude B): PROJECT-GTKB-BRIDGE-RECONCILIATION → all 7 WIs resolved. Resolved WI-4237 (bridge VERIFIED @ `gtkb-bridge-reconciliation-operator-skill-014`); WI-4711/4713 auto-resolved by the WI-4704 reconciler; captured WI-4719 (reconciler should treat WITHDRAWN sibling threads as non-blocking). Post-crash resume; read-only verification this turn.
- **S453** (2026-06-21, Claude B): drove PROJECT-GTKB-BRIDGE / WI-4468 to VERIFIED; GO/ADVISORY backlog reconciliation analysis.
- **S452** (2026-06-20/21, Claude B): dispatch repair — headless-Claude 401 churn fixed; WI-4682 / WI-4707 / WI-4703 resolved.
- **S450** (2026-06-20, Claude B): envelope-disposition + autonomous-dispatch program; bridge-dispatcher fabric deliberation.
- **S449** (2026-06-19, Claude B): GT-KB production-readiness assessment + drift-stabilization wave.
- **S448** (2026-06-18, Claude B): Agent Red Readiness Phase 1 execution begins.

## Standing Operating Decisions
Durable operating decisions are authoritative in the Deliberation Archive
(`gt deliberations search …`) and `.claude/rules/codex-decision-ledger.md`
(e.g. 2026-04-09 bridge ownership + asynchronous-protocol decisions). Consult
those rather than a copy here.

## Strategic Thesis & Plan-of-Record (pointers)
- [Pipeline vision](topics/project_vision_statement.md) · [Pipeline is the product](topics/project_strategic_thesis.md)
- [Production Readiness Plan-of-Record](topics/project_plan_of_record.md)
- [GT-KB non-disruptive upgrade priority](topics/project_gtkb_non_disruptive_upgrade_priority.md) · [GT-KB Azure SaaS Readiness](topics/project_gtkb_azure_saas_readiness_vision.md)

## Feedback Index
Owner behavioral-feedback corpus (durable; one file per lesson): [memory/feedback/](feedback/).
Root-level pointers: [canonical project URLs](feedback_groundtruth_kb_canonical_project_urls.md) ·
[peer-review weighting by reliability](feedback_peer_review_weighting_by_reliability.md) ·
[preflight before filing bridge proposals](feedback_preflight_before_filing_bridge_proposals.md) ·
[external resource registry](project_external_resource_registry.md).

## Memory Files (preserved topic notes)
- [agent-red-hibernation-runbook](agent-red-hibernation-runbook-2026-04-27.md) · [agent-red-hibernation-state](agent-red-hibernation-state-2026-04-27.md)
- [antigravity-integration-status](antigravity-integration-status.md)
- [testing-research](testing-research.md)
- [v1-0-release-plan-scope](v1-0-release-plan-scope.md) · [v1 release strategy (S347)](v1-release-strategy-deliberation-S347.md)
- Durable architecture / reference / decision topics: [memory/topics/](topics/)
- Open owner decisions: [pending-owner-decisions.md](pending-owner-decisions.md)
- Release-readiness state: [release-readiness.md](release-readiness.md)

## References
- [Sarah Scenario (UX anchor)](topics/reference_sarah_scenario.md)
- [UI Testing Tool Evaluation](topics/reference_ui_testing_tools.md)

## Project Knowledge (in MemBase)
- Cross-cutting lessons: `DOC-cross-cutting-lessons` · Owner preferences: `DOC-owner-preferences`.
- Protected behaviors: `PB-*` specs (machine-verifiable assertions checked at session start).
- [Production deploy approval](feedback/feedback_production_deploy_approval.md) — require explicit "deploy to production" confirmation.
