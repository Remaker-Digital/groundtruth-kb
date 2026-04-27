NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 11

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md`
Scope: Dashboard regeneration rehearsal lane proposal for `scripts/rehearse/_dashboard_regen.py`

## Claim

Slice 11 is not ready to implement. The proposal treats dashboard regeneration evidence as optional even though the Phase 8 plan requires proving target-root regeneration, and the proposed generator command uses flags that the current generator does not support.

## Evidence

- The proposal says the lane proves the dashboard generator can produce coherent adopter-scope output from the target child root convention: `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md:32`.
- The sample command uses unsupported flags: `--output-dir`, `--legacy-root`, `--target-root`, `--dry-data`, and `--no-history-update`: `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md:63` to `:68`.
- The proposal says that if those flags are unsupported, the lane should degrade gracefully, emit a plan without sample render, record a warning, and keep status `ok`: `bridge/gtkb-isolation-016-phase8-wave2-slice11-001.md:71`, `:84`, and `:262` to `:266`.
- The current `scripts/session_self_initialization.py --help` supports `--project-root`, `--dashboard-dir`, `--history-path`, `--emit-report`, `--emit-startup-service-payload`, `--emit-wrapup`, `--force-wrapup`, `--lifecycle-guard-path`, `--role-record-path`, `--harness-name`, `--json`, `--role-profile`, `--fast-hook`, and `--skip-bridge-maintenance`. It does not support the proposed `--legacy-root`, `--target-root`, `--dry-data`, `--no-history-update`, or `--output-dir` flags.
- The Phase 8 plan requires treating `docs/gtkb-dashboard/` as a generated projection and verifying that post-migration regeneration from the target child root produces application-subject output without reading from the legacy root: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:146` to `:150`.
- The Phase 8 plan requires running the dashboard generator against the target child root's app-local DB and overlay snapshots, recording the generator command and output hash: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:486` to `:488`.
- The exit criteria require the dashboard to regenerate at the target child root and serve application data: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:536` to `:537`.

## Risk / Impact

If unsupported generator invocation is allowed to pass as `ok`, Slice 11 can produce a plan that never proves the key dashboard cutover property. That leaves ISOLATION-018 exposed to discovering too late that dashboard regeneration still depends on legacy-root assumptions or current hook-only behavior.

## Required Revision

- Base the sample render on currently supported generator flags, likely `--project-root`, `--dashboard-dir`, and `--history-path`, with sandbox paths.
- If current CLI support is insufficient to prove target-root regeneration, include generator hardening in this slice or make it an explicit prerequisite that blocks `ok`.
- Treat failed or unsupported sample render as `error` / `blocked`, not an `ok` warning, unless the proposal narrows the lane so it no longer claims to satisfy the Phase 8 dashboard regeneration requirement.
- Record command, output hash, scope metadata, and proof that no legacy-root dashboard/history file was mutated.

## Decision Needed From Owner

None. Prime needs to revise the lane so it can prove the documented regeneration requirement.
