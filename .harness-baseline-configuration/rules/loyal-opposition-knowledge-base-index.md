# Loyal Opposition Knowledge Base Index - GroundTruth-KB

Purpose: index of Loyal Opposition rules maintained for the reviewing harness and Prime Builder handoff.

> **Activity envelope load policy (WI-4949 / SPEC-INTAKE-46594e):** This index is
> `explicit_query` — use it on demand when navigating Loyal Opposition surfaces. Do not
> load wholesale at base session startup.

## Active Rules under `.harness-baseline-configuration/rules/`

- `session-bootstrap.md`
- `standing-priorities.md`
- `groundtruth-kb-vision.md`
- `way-of-working.md`
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
- `.harness-baseline-configuration/rules/canonical-terminology.md` — core primer subset only at startup;
  full corpus and activity-specific terms load on `::open <activity>`.
- `.harness-baseline-configuration/rules/file-bridge-protocol.md` — bridge statuses, gates, claim/preflight.
- `session-bootstrap.md` — deterministic restart guide (Phase A global; Phase B
  defers activity-only surfaces).

## Activity-Envelope Loads (deferred until `::open <activity>`)

Activity-specific surfaces load on demand from the baseline rules directory:

| Surface | Open with |
|---|---|
| `standing-priorities.md`, `groundtruth-kb-vision.md` | `::open project` |
| `way-of-working.md` | `::open deliberation` |
| `review-operating-contract.md`, `loyal-opposition-runbook.md` | `::open build` or `::open test` |
| `loyal-opposition-review-checklists.md`, `template-code-review.md`, `template-decision-memo.md` | `::open test` (substantial review work) |

Skills are authored once under `.agents/skills/` and read there. Hosts that need
registrations receive frontmatter-preserving pointer stubs; load the authored skill
body and its helpers on demand, never a copied provider-specific skill body.

## Legacy Startup-Loaded Rules note (retired 2026-07-01)

The former "Startup-Loaded Rules" block that listed every Loyal Opposition runbook at session
start is retired by WI-4949. Use the global-baseline and activity-envelope tables
above instead.


## Update Convention

- Keep legacy files immutable unless owner explicitly requests edits.
- File new assessments as Advisory Proposal bridge entries or Deliberation Archive records, per content.
- Update this index when new Loyal Opposition-standard rules are introduced.
- Keep review memory rules focused on process memory, not canonical project facts already owned by the KB.
