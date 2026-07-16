# Codex Knowledge Base Index - GroundTruth-KB

Purpose: index of Loyal Opposition rules maintained for Codex and Prime Builder handoff.

> **Activity envelope load policy (WI-4949 / SPEC-INTAKE-46594e):** This index is
> `explicit_query` — use it on demand when navigating Codex LO surfaces. Do not
> load wholesale at base session startup.

## Active Rules under `.claude/rules/`

- `codex-session-bootstrap.md`
- `codex-standing-priorities.md`
- `groundtruth-kb-vision.md`
- `codex-way-of-working.md`
- `codex-review-operating-contract.md`
- `codex-loyal-opposition-runbook.md`
- `codex-knowledge-base-index.md` (this file)
- `codex-decision-ledger.md`
- `codex-dead-ends-and-false-positives.md`
- `codex-review-checklists.md`
- `template-code-review.md`
- `template-decision-memo.md`

## Active Logs and Dropbox under `independent-progress-assessments/`

- `CODEX-INSIGHT-DROPBOX/` (active report dropbox)
- `loyal-opposition-log.md` (existing running log)
- `KNOWLEDGE-PROJECT.md` (existing recurring project risks and decisions)
- `KNOWLEDGE-MIKE.md` (existing owner preference context)

## Global Baseline (session start)

- Project root `AGENTS.md` defines default Loyal Opposition operating contract.
- `.claude/rules/canonical-terminology.md` — core primer subset only at startup;
  full corpus and activity-specific terms load on `::open <activity>`.
- `.claude/rules/file-bridge-protocol.md` — bridge statuses, gates, claim/preflight.
- `config/agent-control/SESSION-STARTUP-INDEX.md` + role overlay — canonical load order.
- `codex-session-bootstrap.md` — deterministic restart guide (Phase A global; Phase B
  defers activity-only surfaces).

## Activity-Envelope Loads (deferred until `::open <activity>`)

Per `config/agent-control/activity-envelope-sharding.toml` § `migration.wi4949`:

| Surface | Open with |
|---|---|
| `codex-standing-priorities.md`, `groundtruth-kb-vision.md` | `::open project` |
| `codex-way-of-working.md` | `::open deliberation` |
| `codex-review-operating-contract.md`, `codex-loyal-opposition-runbook.md` | `::open build` or `::open test` |
| `codex-review-checklists.md`, `template-code-review.md`, `template-decision-memo.md` | `::open test` (substantial review work) |

`.codex/skills/` adapters are generated from `.claude/skills/`; no separate adapter
load is required at startup when the canonical skill source is unchanged.

## Legacy Startup-Loaded Rules note (retired 2026-07-01)

The former "Startup-Loaded Rules" block that listed every Codex runbook at session
start is retired by WI-4949. Use the global-baseline and activity-envelope tables
above instead.

## Legacy Cursor Artifact Location

Legacy Cursor artifacts were moved (not deleted) to:

- `independent-progress-assessments/archive/cursor-legacy/CURSOR-KNOWLEDGE-BASE-INDEX.md`
- `independent-progress-assessments/archive/cursor-legacy/CURSOR-LOYAL-OPPOSITION-ROLE.md`
- `independent-progress-assessments/archive/cursor-legacy/CURSOR-WAY-OF-WORKING.md`
- `independent-progress-assessments/archive/cursor-legacy/CURSOR-INSIGHT-DROPBOX/`

## Update Convention

- Keep legacy files immutable unless owner explicitly requests edits.
- Create new assessments in `CODEX-INSIGHT-DROPBOX/`.
- Update this index when new Codex-standard rules are introduced.
- Keep review memory rules focused on process memory, not canonical project facts already owned by the KB.
