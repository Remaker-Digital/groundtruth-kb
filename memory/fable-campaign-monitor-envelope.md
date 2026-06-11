author_identity: prime-builder
author_harness_id: B
author_session_context_id: 4490dc1a-faa5-401f-968c-670bf2c915b5
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

# PROJECT-FABLE-INVESTIGATION — Cross-Session Monitor Envelope

Operational notepad (not canonical). Canonical state = `bridge/INDEX.md` + MemBase.
Companion: `memory/fable-investigation-campaign.md` (filing playbook, cheap-draft recipe,
per-cluster status, the consolidated gate lessons) and
`bridge/gtkb-fable-investigation-advisory-001.md` (charter, Q1-Q7, per-FAB WI/findings table).

## Owner Directive (2026-06-11, interactive owner session, harness B)

"Monitor the progress of this program and take on new PB-addressable work from the bridge
as soon as it becomes available. Continue this thread (envelope) across multiple sessions
so you can follow the progress to its conclusion."

I (Prime Builder, harness B) am the **standing PB monitor** for the FABLE campaign until
it concludes.

## Standing Scope (AUQ 2026-06-11, `detected_via: ask_user_question`)

- **FULL CONCLUSION.** Act on every Codex `GO` (implement) / `NO-GO` (revise) as verdicts
  land, AND finish filing the 4 remaining proposals (FAB-20..23). Shepherd all 23 clusters
  to filed → reviewed → implemented → VERIFIED.
- FAB-22 is owner-heavy → grill-me-for-clarification AUQ batch when reached.

## Resume Keyword (paste to resume in a fresh session)

```
::init gtkb pb

Resume the PROJECT-FABLE-INVESTIGATION standing monitor. READ FIRST:
memory/fable-campaign-monitor-envelope.md (this file — the monitor arrangement + live status),
memory/fable-investigation-campaign.md (filing playbook + gate lessons),
bridge/gtkb-fable-investigation-advisory-001.md (charter), bridge/INDEX.md (live queue).
Standing scope = FULL CONCLUSION (act on Codex GO/NO-GO + finish FAB-20..23). Take on
PB-addressable work (latest GO/NO-GO in the FAB threads) as it appears; pause only for
genuine owner-gated AUQ batches.
```

## Per-Session / Per-Tick Monitor Procedure

1. Read live `bridge/INDEX.md` (cheap: scan the FAB-* and campaign entries' top status lines).
2. Identify PB-addressable entries = latest status `GO` or `NO-GO` on a FAB-* or campaign thread.
   (Do NOT act on NEW/REVISED/VERIFIED/ADVISORY as Prime.)
3. For each, check the work-intent claim (`.gtkb-state/work-intent/<slug>.json`) and the
   impl-start state to avoid collision with a dispatched/concurrent worker. If unclaimed/stale,
   take it; if actively held by another session, skip and note.
4. On `GO`: `python scripts/implementation_authorization.py begin --bridge-id <slug>` →
   implement within target_paths + PAUTH bounds → verify (tests/ruff/guard) → file post-impl
   report (NEW) → INDEX prepend. On `NO-GO`: read findings → revise → file REVISED → INDEX prepend.
5. When no FAB verdict work is available, advance FAB-20..23 filing (owner-gated; AUQ batch first).
6. When everything currently available is drained, go idle: ScheduleWakeup (~20-25 min) to
   re-check for the next Codex verdict. Work continuously while work exists; sleep only when idle.
   (Avoid the retired-poller anti-pattern: each wake must do real triage, not blind re-scan.)

## Collision Protocol

- Dispatch substrate (FAB-01) is itself still unimplemented → cross-harness headless Prime
  dispatch is likely degraded, so headless workers are NOT reliably grabbing GOs. That makes
  acting on landed GOs primarily this session's job — but still claim before drafting and
  check claims/impl-state before implementing.
- The campaign already hit one two-session collision (2026-06-11 ~00:41Z, owner chose a driver).
  If a concurrent Prime session is active, coordinate via claims; surface to owner if ambiguous.

## Live Status Snapshot (2026-06-11 ~03:35Z, session 4490dc1a)

- **Investigation thread `gtkb-architecture-governance-hygiene-investigation`: WITHDRAWN**
  (this session, `-005`; resolved Codex `NO-GO@-004`; owner-closure AUQ recorded). Terminal.
- **FAB-02 (secrets-remediation): IMPLEMENTED + report filed `NEW@-003` this session; awaiting
  Codex VERIFIED.** All gates green (guard 10/10, pytest 9-passed, ruff lint+format clean).
  doctor.py wiring deferred to FAB-19 per the proposal's escape clause (documented in `-003`).
- **PB-ADDRESSABLE VERDICT QUEUE (landed while implementing FAB-02; act per standing directive):**
  - `gtkb-fab-01-dispatch-substrate-revival` **GO@-002** → implement (this fixes dispatch itself).
  - `gtkb-cheap-draft-linter` **GO@-002** → implement.
  - `gtkb-fab-03-membase-backup` **NO-GO@-002** → revise.
  - `gtkb-fab-05-rule-file-retirement` **NO-GO@-002** → revise.
- **Filed NEW, awaiting Codex review:** FAB-04, FAB-06..FAB-19 (the rest of the NEW queue).
- **Remaining to file:** FAB-20 (hygiene-investigation skill), FAB-21 (startup load-cost),
  FAB-22 (architecture — owner-heavy/grill-me), FAB-23 (demoted near-miss batch).
- **NEW WORKSTREAM (owner-directed 2026-06-11 AUQ): bridge INDEX prune.** INDEX is ~1,880 lines
  (~9× the ~200-line `file-bridge-protocol.md` §Index Maintenance guidance). Owner authorized a
  **deterministic prune tool + archive via bridge**: move terminal-status threads (latest =
  VERIFIED/WITHDRAWN) into `bridge/INDEX-ARCHIVE.md`; keep actionable (NEW/REVISED/GO/NO-GO/
  ADVISORY/DEFERRED) live; never touch bridge `*.md` files on disk; repeatable. Governing spec
  `GOV-FILE-BRIDGE-AUTHORITY-001`. To file as a prime_proposal → needs Project/WI/PAUTH.
- **Codex (Loyal Opposition, harness A) is ACTIVE** and churning the NEW queue fast (a wave of
  GO/NO-GO verdicts landed within one FAB-02 implementation window).

## Gate Lessons (pointer)

Reuse the consolidated gate lessons in `memory/fable-investigation-campaign.md` (Specification
Links + Isolation Placement Compliance two-gate rule; groundtruth.db-in-target_paths for KB
mutation; bare-WI collision warnings; claim survives failed Write; transcript-UUID for claims;
WITHDRAWN files still need `## Specification Links` + `## Owner Decisions / Input` + the 6
author-provenance fields per the governed-markdown provenance gate, learned filing the
investigation WITHDRAWN this session).
