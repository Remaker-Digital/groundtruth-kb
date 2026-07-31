# INSIGHTS 2026-07-17 — Worker-Facing Bridge/TAFE/Dispatcher Internals Exposure Audit

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb); audit produced in an ops activity envelope; captured via the LO-sanctioned CODEX-INSIGHT-DROPBOX path because the shared envelope projection resolved to loyal-opposition under a split-brain condition

Specs: DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001 (proposed), DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001 (proposed), ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001 (proposed)
WIs: WI-5269, WI-5270, WI-5271
Program: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Deliberations: DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE, -PHASED-HARDENING, -ACTIVITY-ENVELOPE-AUTHORITY, -ORDINARY-WORKER-DEFINITION, -DISPATCHER-WORKER-CONTEXT-PACKET, -SAFE-PACKET-CONTENT, -CAPABILITY-TOKEN-ENFORCEMENT, BRIDGE-FILES-PROTECTED-WORKER-SURFACE

## Provenance

Read-only exposure audit produced under Prime Builder intent (Claude, harness B,
`::init gtkb pb`) within an ops activity envelope, under explicit owner direction
(2026-07-17): "capture this audit as a governed input document to the black-box
program." Captured via the LO-sanctioned report path because the session's shared
envelope projection resolved to loyal-opposition during a split-brain condition
(concurrent sessions on harness B). Read-only; no artifact was modified during the
audit.

## Governing owner decisions (2026-07-15) and current directive

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` — strict operational black box: ordinary
  workers may use only worker-safe CLI/status summaries + their assigned packet;
  direct internals inspection prohibited unless assigned maintenance or case-by-case
  owner-authorized.
- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` — safe facade FIRST, hard
  enforcement LAST; explicitly rejected immediate hard boundary.
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY` — inspection only in
  explicit maintenance/admin (ops) activity envelopes.
- 2026-07-17 owner directive: workers must not reference bridge/TAFE/dispatcher
  configuration except when explicitly directed within an ops activity envelope; owner
  selected FULL PHASING (build facade, then gate) over immediate removal.

## Method and structural caveat

Grep/glob over tracked rules and skill locations plus reasoning from loaded rule
content and canonical skill descriptions.

Structural caveat (design-relevant): `.claude/skills/` is git-ignored (only
`.claude/rules/` is negated back into tracking), so a gitignore-respecting grep returns
zero for skills even though they exist. Canonical skill source is `.claude/skills/`;
generated adapters project to `.codex/`, `.cursor/`, `.agent/`, `.goose/`,
`.api-harness/`. Any gating/rewrite must land at the canonical source and regenerate
adapters (harness-parity gated), and is invisible to git unless the tracked
template/registry surfaces are also touched.

## Layer 1 — Instruction (rules that DIRECT workers to inspect internals)

96 references across 18 tracked rule files. Disposition: rewrite (phasing step 4) to
direct workers to the safe worker-context packet / mediated views. Heaviest:

| Rule file | Refs | Note |
| --- | --- | --- |
| canonical-terminology.md | 15 | mostly glossary definitions (likely stay — define, not direct) |
| bridge-essential.md | 13 | startup + operating directives to inspect TAFE/dispatcher state |
| codex-session-bootstrap.md | 13 | startup directives to check dispatcher/TAFE state |
| file-bridge-protocol.md | 13 | directs reading TAFE/dispatcher bridge state |
| operating-role.md | 8 | harness-registry / dispatcher role-set reads |
| codex-way-of-working.md | 5 | dispatcher/TAFE bridge state directives |
| prime-bridge-collaboration-protocol.md | 4 | dispatch automation references |
| prime-builder-role.md | 4 | dispatcher role read references |
| acting-prime-builder.md, codex-decision-ledger.md, codex-review-operating-contract.md, codex-standing-priorities.md, dispatcher-daemon-substrate-rollback-runbook.md | 3 each | mixed |
| codex-loyal-opposition-runbook.md | 2 | bridge-state directives |
| bridge-permanent-operations-runbook.md, codex-review-gate.md, operating-model.md, project-root-boundary.md | 1 each | incidental |

## Layer 2 — Tooling (skills/CLIs that LET workers inspect internals)

| Surface | Exposure | Disposition |
| --- | --- | --- |
| `dispatcher-control` skill | inspect health/status/report/selected-targets/live-workers/history AND mutate eligibility/ranking/caps/rules | ops-only (highest sensitivity — control surface) |
| `bridge-config` skill | inspect dispatch config, dispatchability, selected targets, rule eligibility, last dispatch state | ops-only |
| `bridge` skill | mixed — participation (file proposal, write verdict) PRESERVE; state inspection (state-report, routing) MEDIATE | split |
| CLI `gt bridge state-report` | raw bridge/queue state | gate outside ops |
| CLI `gt bridge dispatch config\|status\|health` | dispatcher config/state | gate outside ops |
| CLI `gt harness roles` | harness role/dispatch config | gate outside ops |

All three skills project to every harness (`.claude`, `.codex`, `.cursor`, `.agent`,
`.goose`, `.api-harness`) from the canonical source; changes must be made at the source
and re-projected.

## Layer 3 — Raw reads (protected internals to mediate/protect)

- Raw numbered `bridge/*.md` files (already owner-decided protected per
  `DELIB-20260715-BRIDGE-FILES-PROTECTED-WORKER-SURFACE`).
- `config/dispatcher/rules.toml` (dispatcher config).
- `harness-state/harness-registry.json` (role/dispatch config).
- Session-envelope documents (`.claude/session/`, `harness-state/*/session-envelopes/`).
- `.gtkb-state/bridge-poller/` (dispatch state).

## Participation path — PRESERVE (workers legitimately need)

- `bridge-propose` / `write_bridge.py` — file a proposal.
- `verify` / `write_verdict.py` — write a verdict.
- `bridge_claim_cli.py claim` and `implementation_authorization.py begin` — work-intent
  claim and implementation-start.
- The dispatched work packet (assigned content) itself.

## Design input for the facade / DCLs / gate

- WI-5270 worker-context packet must supply everything Layer-1 rules currently make
  workers fetch by inspection (assigned work + role + status), so the rewrites have a
  target. Maps to `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`.
- WI-5271 mediated view replaces Layer-3 raw reads plus the `bridge`-skill inspection
  half. Maps to `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`.
- WI-5269 gate denies Layer-2 CLIs plus Layer-3 raw reads outside ops. Maps to
  `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`.
- Scale: ~18 rule rewrites plus canonical-skill changes re-projected across 6 harnesses
  (parity-gated).

## Scope note

Non-live copies are OUT of scope for the gate: test fixtures under `.pytest-tmp/`,
`archive/worktrees/`, hygiene-reclaim trash under `.gtkb-state/hygiene-reclaim/`, and
venv `site-packages`. They explain grep noise but are not live worker surfaces.

## Recommended sequencing (owner-selected FULL PHASING)

1. Land spec-foundation VERIFIED + `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`,
   `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`,
   `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` canonically.
2. Implement WI-5270 (worker-context packet) + WI-5271 (mediated bridge views).
3. Rewrite the Layer-1 rules + canonical skills to consume the facade; re-project
   adapters (parity-gated).
4. Add audit + soft-deny.
5. Turn on WI-5269 hard gate (deny worker internals-reference outside ops) per
   protected surface, only after safe-facade parity.
