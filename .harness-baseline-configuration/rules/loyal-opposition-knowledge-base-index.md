# Loyal Opposition Knowledge Base Index - GroundTruth-KB

Purpose: index of Loyal Opposition rules maintained for the reviewing harness and Prime Builder handoff.

> **Activity envelope load policy (WI-4949 / SPEC-INTAKE-46594e):** This index is
> `explicit_query` — use it on demand when navigating Loyal Opposition surfaces. Do not
> load wholesale at base session startup.

## Active Rules under `{{HARNESS_RULES_DIR}}/`

- `session-bootstrap.md`
- `standing-priorities.md`
- `groundtruth-kb-vision.md`
- `role-way-of-working.md`
- `review-operating-contract.md`
- `loyal-opposition-runbook.md`
- `loyal-opposition-knowledge-base-index.md` (this file)
- Review-memory records (decision ledger; dead-ends/false-positives): MemBase governance records
- `loyal-opposition-review-checklists.md`
- `template-code-review.md`
- `template-decision-memo.md`

## Canonical Report And Review Stores

- Advisory Proposal bridge entries: Loyal Opposition reports that may create future Prime Builder work.
- Deliberation Archive records: process/review findings, owner decisions, rejected/deferred/monitored advisories, and rationale that needs durable searchability.
- MemBase `current_work_items` and project records: governed work, project risks, backlog items, and unresolved follow-up.
- `memory/MEMORY.md`: non-authoritative operational notes only.

## Global Baseline (session start)

- Project root `AGENTS.md` defines default Loyal Opposition operating contract.
- `{{HARNESS_RULES_DIR}}/canonical-terminology.md` — core primer subset only at startup;
  full corpus and activity-specific terms load on `::open <activity>`.
- `{{HARNESS_RULES_DIR}}/file-bridge-protocol.md` — bridge statuses, gates, claim/preflight.
- `config/agent-control/SESSION-STARTUP-INDEX.md` + role overlay — canonical load order.
- `session-bootstrap.md` — deterministic restart guide (Phase A global; Phase B
  defers activity-only surfaces).

## Activity-Envelope Loads (deferred until `::open <activity>`)

Per `config/agent-control/activity-envelope-sharding.toml` § `migration.wi4949`:

| Surface | Open with |
|---|---|
| `standing-priorities.md`, `groundtruth-kb-vision.md` | `::open project` |
| `role-way-of-working.md` | `::open deliberation` |
| `review-operating-contract.md`, `loyal-opposition-runbook.md` | `::open build` or `::open test` |
| `loyal-opposition-review-checklists.md`, `template-code-review.md`, `template-decision-memo.md` | `::open test` (substantial review work) |

`{{HARNESS_SKILLS_DIR}}/` adapters are generated from the canonical baseline skill source; no separate adapter
load is required at startup when the canonical skill source is unchanged.

## Legacy Startup-Loaded Rules note (retired 2026-07-01)

The former "Startup-Loaded Rules" block that listed every Loyal Opposition runbook at session
start is retired by WI-4949. Use the global-baseline and activity-envelope tables
above instead.

## Legacy Cursor Artifact Location

The former legacy Cursor artifact archive has been retired with the report-directory surface. Treat any surviving references to that archive as historical context only, not a live dependency or report destination.

## Update Convention

- Keep legacy files immutable unless owner explicitly requests edits.
- File new assessments as Advisory Proposal bridge entries or Deliberation Archive records, per content.
- Update this index when new Loyal Opposition-standard rules are introduced.
- Keep review memory rules focused on process memory, not canonical project facts already owned by the KB.
