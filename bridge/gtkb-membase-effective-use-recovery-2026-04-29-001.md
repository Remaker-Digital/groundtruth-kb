NEW

# GTKB MemBase Effective Use - Recovery (scoping)

**Status:** NEW
**Date:** 2026-04-29
**Work item:** GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY (added to work_list row 19, 2026-04-28 S319 per owner directive)
**Author:** Prime Builder (Claude, current session)
**Owner specs this bridge serves:**
- `SPEC-INTAKE-c9e997` - Extract specifications from conversation in-session
- `SPEC-INTAKE-2485e9` - Surface spec creation/update events in owner chat view
- `SPEC-INTAKE-3623f1` - Aggressive foundational-requirements intake for new user projects

bridge_kind: prime_proposal
work_item_ids: [GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY]
spec_ids: [SPEC-INTAKE-c9e997, SPEC-INTAKE-2485e9, SPEC-INTAKE-3623f1]
target_project: groundtruth-kb
target_paths: [
  "groundtruth-kb/templates/hooks/spec-event-surfacer.py (Slice A, new)",
  "groundtruth-kb/templates/hooks/spec-classifier.py (Slice B, modified - elevated to capturer)",
  "groundtruth-kb/src/groundtruth_kb/intake.py (Slices B/C/D, modified - capture_requirement / confirm_intake / reject_intake)",
  "groundtruth-kb/src/groundtruth_kb/foundational_requirements.py (Slice D, new)",
  "groundtruth-kb/templates/skills/gtkb-foundational-intake/** (Slice D, new)",
  ".claude/session/spec-events-seen.jsonl (Slice A, new state file - not implementation; per-session ledger)",
  "scripts/release_candidate_gate.py (Slices A-D, modified - test wiring)",
  "tests/** (Slices A-D, new)",
  "memory/work_list.md (this bridge, modified - update row 19 on GO)"
]
implementation_scope: governance
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate. Codex MUST NO-GO this proposal if any relevant specification is missing.

**Owner-stated requirement specs (primary):**
- `SPEC-INTAKE-c9e997` - Extract specifications from conversation in-session. Verified to exist in KB at proposal time.
- `SPEC-INTAKE-2485e9` - Surface spec creation/update events in owner chat view. Verified to exist in KB at proposal time.
- `SPEC-INTAKE-3623f1` - Aggressive foundational-requirements intake for new user projects. Verified to exist in KB at proposal time.

**Governance specs / records that constrain this work:**
- `GOV-ARTIFACT-APPROVAL-001` and `ADR-ARTIFACT-FORMALIZATION-GATE-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` - any DA/SPEC/GOV mutation introduced by this program must respect the formal-artifact-approval gate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (DELIB-0874 owner directive 2026-04-22) - artifact-oriented governance bias justifies elevating classifier from "nudge" to "capture candidate".
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - aligns with reducing AI-driven repetitive plumbing for capture/confirm/reject loops.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release-candidate gate must continue running effectiveness regression tests.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - upstream-routing of these capabilities is the GT-KB conformance path; Agent Red consumes via `gt project upgrade`.

**Loyal Opposition source document:**
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` (lo_review, informational) - the substance basis. Filed at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/MEMBASE-EFFECTIVE-USE-ASSESSMENT-2026-04-29.md`.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` - all artifacts must remain under `E:\GT-KB`; upstream changes route to `E:\GT-KB\groundtruth-kb\` (in-root).
- `.claude/rules/file-bridge-protocol.md` - this proposal complies with the Mandatory Root Boundary Gate, Mandatory Specification Linkage Gate, and (transitively, via per-slice implementation bridges) the Mandatory Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` - codifies the requirement Codex must NO-GO any unlinked proposal.
- `.claude/rules/deliberation-protocol.md` - dictates the prior-deliberation search performed for this proposal.
- `.claude/rules/bridge-essential.md` - bridge protocol audit-trail discipline that constrains how the phantom INDEX must be reconciled (no silent edits).

**Test derivation statement (per file-bridge-protocol Mandatory Specification-Derived Verification Gate):**
This is a SCOPING bridge; it proposes no tests itself. Each subsequent slice's implementation bridge will declare tests derived from the linked specs as follows:

| Slice | Driving spec | Test derivation summary |
|-------|--------------|-------------------------|
| A (event surfacer) | SPEC-INTAKE-2485e9 ("surface spec events in owner chat view") | A test asserts that creating a spec row produces exactly one chat-visible event line within the same session, and that repeated hook invocations do not duplicate the event. |
| B (auto-capture) | SPEC-INTAKE-c9e997 ("extract specifications from conversation in-session") | A test asserts that owner directive language ("must", "should", numbered criteria) creates a `deliberation` row at `outcome='deferred'` with `changed_by='classifier-auto-capture'`, and that questions/non-directive prose do not. |
| C (confirm/reject loop) | SPEC-INTAKE-c9e997 (closure path) | A test asserts that `confirm intake INTAKE-...` writes a spec row plus a confirmation deliberation; `reject intake INTAKE-... <reason>` writes a rejection deliberation with the reason; double-confirm is idempotent. |
| D (foundational intake) | SPEC-INTAKE-3623f1 ("aggressive foundational-requirements intake") | A test asserts the intake mechanism produces `type='requirement'` with `section='foundational/<category>'` rows for each of the 10 categories from a sample document, and that the in-session questionnaire yields equivalent rows from synthetic owner answers. |

Each slice's implementation bridge will detail the exact test files, fixtures, and assertions before that slice receives GO.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, deliberations searched before drafting:

- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** (lo_review, informational, S319) - the Codex Loyal Opposition assessment that drives this recovery program. Cited throughout as primary source.
- **`DELIB-1126`** (bridge_thread, go) - compressed-thread KB record for `gtkb-membase-effective-use-umbrella`. Records "1 version(s)" - **independent KB-side corroboration** of the phantom-INDEX claim in §1.
- **`DELIB-0874`** (owner_conversation, owner_decision, 2026-04-22) - artifact-oriented governance directive. Justifies elevating classifier behavior from advisory to capturing.
- **`bridge/gtkb-membase-effective-use-umbrella-001.md`** (NEW, 2026-04-24, S307) - the surviving prior scoping artifact. Treated as scoping evidence only; no implementation evidence is carried forward from phantom INDEX entries -002..-014.
- **Searched but NOT cited as evidence:** `DELIB-INTAKE-c971df2d`, `DELIB-INTAKE-9a936aee`, `DELIB-INTAKE-32cc09aa` (cited in prior umbrella as "owner requirements confirmed into specs on 2026-04-24") - **MISSING from current KB**. The three SPEC-INTAKE-* spec IDs above are the surviving authoritative artifacts. The disappearance of these deliberation IDs is itself a diagnostic signal that prior umbrella state was not durably preserved.
- **No prior deliberation reverses this approach.** The previous program stalled at -001 NEW with no Loyal Opposition GO/NO-GO ever applied. Codex review of this proposal is the first formal review for the program substance.

---

## 1. Phantom-INDEX Reconciliation (mandatory per work_list row 19)

Empirical phantom-INDEX evidence, gathered first-hand at proposal-drafting time:

- **`bridge/INDEX.md` lines 811-825** list the thread `gtkb-membase-effective-use-umbrella` with 14 entries: NEW -001 through VERIFIED -014.
- **Filesystem inspection** (`Glob bridge/gtkb-membase-effective-use-umbrella*.md`) returns exactly ONE file: `gtkb-membase-effective-use-umbrella-001.md`. Files -002 through -014 do not exist on disk.
- **KB-side compressed-thread record `DELIB-1126`** reports "1 version(s)" for this thread, independently corroborating the filesystem inspection at the KB layer.
- **`bridge/INDEX.md` line 810** already carries an HTML comment from S317 noting "S317 phantom-INDEX (per bridge\gtkb-bridge-index-phantom-verified-references-2026-04-27): -014 absent from disk + git history. Only -001 exists on disk."

Conclusion:

1. The apparent VERIFIED status of `gtkb-membase-effective-use-umbrella-014.md` is NOT implementation evidence and MUST NOT be relied upon by this recovery program.
2. The prior umbrella program stopped at `-001` NEW. No implementation slices were ever shipped. No tests were ever written.
3. `bridge/gtkb-membase-effective-use-umbrella-001.md` is treated as the surviving SCOPING artifact only, supplying problem-statement substance and sub-slice structure context. All implementation evidence is rebuilt from scratch in this recovery program.

Reconciliation action proposed:

1. **No silent INDEX edit.** Per `.claude/rules/bridge-essential.md` "Invariants" and `.claude/rules/file-bridge-protocol.md` "Guardrails", the bridge files must not be deleted (audit trail discipline) and INDEX state must not be silently edited. The phantom INDEX entries -002 through -014 stand as a permanent historical record of the integrity gap.
2. **New thread.** This proposal opens a new thread `gtkb-membase-effective-use-recovery-2026-04-29` that explicitly cites the phantom history, redoes the scoping, and rebuilds verification evidence on each slice.
3. **Filename deviation explained.** Work_list row 19 suggests filename `gtkb-membase-effective-use-recovery-2026-04-28-001.md` (row-creation date). The Codex assessment recommends `gtkb-membase-effective-use-recovery-2026-04-29` (assessment date). Bridge convention uses thread-opening date. Today is 2026-04-29; this bridge is filed today; therefore the filename uses 2026-04-29. The work_list row will be updated on GO to cite this exact bridge ID.
4. **Optional follow-up.** A future INDEX hygiene proposal MAY add a second HTML comment to the umbrella block in INDEX.md cross-referencing this recovery thread (similar to the existing line-810 annotation). This is OUT OF SCOPE for this scoping bridge; it would be a separate `bridge/index-hygiene-membase-cross-reference-NNN` proposal. Including it here would conflate scope and risk silent edits to canonical INDEX state.

---

## 2. Problem Statement (carried forward from -001 + S319 assessment)

MemBase is used heavily as a decision log (KB current row counts at proposal time per S319 assessment: `current_specifications=2,153`, `current_tests=11,142`, `current_work_items=1,928`, `current_deliberations=1,416`, `current_documents=182`) but is NOT used effectively for the three workflows the owner needs.

### 2.1 In-session extraction is advisory, not capturing

- `.claude/hooks/spec-classifier.py:7` reminds Claude to follow specification-first workflow.
- `.claude/hooks/spec-classifier.py:101` tells Claude not to skip to implementation.
- `.claude/hooks/spec-classifier.py:109-112` emits a `systemMessage` or `{}`. It does NOT call `capture_requirement()` or create MemBase rows.
- Empirical S307 evidence (carried forward from prior umbrella): 6+ bridge proposals filed with requirements language, 0 KB specs written until owner explicitly asked.

### 2.2 Spec/intake events are not visible in chat

- The classifier's `systemMessage` is Claude-only. The owner can inspect via `localhost:8090` dashboard UI or by querying the DB, but cannot observe events as they happen during a session.
- This violates the GT-KB vision filter (DELIB-0874): routine capture and reconciliation should be observable to the owner without manual inspection.

### 2.3 Foundational bootstrap for new projects has no first-class support

- A new project adopting GT-KB has no standardized foundational-requirements set, no dedicated KB section taxonomy, no intake procedure, no prepared-document template, and no in-session questionnaire.
- The owner's enumeration in SPEC-INTAKE-3623f1 names the categories (preferred technology choices, mobile UI, security posture, tenancy, external integrations, core features, deployment target, cost constraints, etc.). None currently have first-class records.

### 2.4 Phantom bridge state creates false confidence

- Documented in §1. The umbrella thread appears VERIFIED in INDEX.md but no verification artifact exists. This is the most concrete current risk: future sessions can mistake the apparent VERIFIED for implementation evidence.

### 2.5 Open MemBase WIs are not fully reconciled

- S319 assessment reports 51 open MemBase work items.
- `GTKB-GOV-004` (work-item harvest into standing backlog snapshots) and `GTKB-GOV-010` (standing-backlog harvest audit as release-gate input) are progress, but until reconciled, the dashboard "open WI count" is noisy.
- Without reconciliation, every Prime/Loyal Opposition session must rediscover whether a MemBase row is actionable.

---

## 3. Recovery Program Structure (Four Slices, A through D)

This bridge is a **scoping proposal**. On GO, four implementation bridges follow plus one parallel reconciliation track. Slices ordered by dependency.

### 3.1 Slice A - Spec/intake event surfacer (serves SPEC-INTAKE-2485e9)

**Thread name (proposed):** `gtkb-membase-effective-use-recovery-slice-a-event-surfacer-2026-04-29`

**Deliverable:** a Stop / PostToolUse hook that watches the KB for spec-row writes in the current session and emits a chat-visible summary line per event.

**Mechanism (refined in implementation bridge):**
- Hook path upstream: `groundtruth-kb/templates/hooks/spec-event-surfacer.py`. Adopters consume via `gt project upgrade`.
- Per-session seen ledger at `.claude/session/spec-events-seen.jsonl` records `(spec_id, version, seen_at)` tuples. Idempotency boundary.
- Detection: query `specifications` table for rows with `changed_at >= session_started_at` not in the ledger.
- Emission format: chat-visible systemMessage (same mechanism as existing bridge-essential block).

**Why first:** enables Slices B, C, D to be observable. Without it, captures fire silently.

**Does NOT deliver:** automatic capture (that is Slice B). Slice A observes only.

### 3.2 Slice B - Safe auto-capture from owner requirement language (serves SPEC-INTAKE-c9e997)

**Thread name (proposed):** `gtkb-membase-effective-use-recovery-slice-b-auto-capture-2026-04-29`

**Deliverable:** elevate `spec-classifier.py` from advisory to capturing. When triggers fire, invoke `capture_requirement()` directly with `changed_by='classifier-auto-capture'`. The owner sees the capture via Slice A's surfacer.

**Mechanism:**
- Conservative triggers: "must", "should", "shall", "required", numbered criteria, "I want", "I would like".
- Distinguishes informational description from statement-of-requirement to bound false positives.
- Auto-captured deliberations land at `outcome='deferred'` with attribution `changed_by='classifier-auto-capture'` so the audit trail distinguishes auto from skill-driven captures.
- **Formal-artifact-approval handling:** because Slice B mutates the Deliberation Archive automatically, the implementation bridge MUST include explicit approval evidence per `GOV-ARTIFACT-APPROVAL-001`. Two acceptable paths: (1) deferred-only captures bypass the formal gate by design (the gate fires on canonical promotion, not deferred candidates) and the `confirm intake` path in Slice C is the gate for canonical promotion; (2) a scoped auto-approval packet that names `classifier-auto-capture` as an audited actor for `outcome='deferred'` writes only. Path (1) is preferred because it keeps the formal gate at the canonical-promotion boundary unchanged.

**Why second:** depends on Slice A for owner observability of captures.

**Does NOT deliver:** retroactive capture of past conversations. Owner-language only, current session only.

### 3.3 Slice C - Confirm/reject owner command loop (serves SPEC-INTAKE-c9e997 closure)

**Thread name (proposed):** `gtkb-membase-effective-use-recovery-slice-c-confirm-reject-2026-04-29`

**Deliverable:** owner-facing low-friction commands `confirm intake INTAKE-xxxxxxxx` and `reject intake INTAKE-xxxxxxxx <reason>`. Confirm writes a spec row plus confirmation deliberation. Reject writes a rejection deliberation. Repeat-confirm is idempotent.

**Mechanism choice (open question - see §11):**
- Option C1: prompt-recognition hook (lower friction, less discoverable).
- Option C2: slash-skill `/confirm-intake INTAKE-...` and `/reject-intake INTAKE-... <reason>` (more discoverable, higher friction).
- Implementation bridge picks one after Codex review of the trade-off.

**Why third:** depends on Slice A for confirmation-event observability and Slice B for the candidate population.

**Does NOT deliver:** bulk confirm/reject. One INTAKE-id per command.

### 3.4 Slice D - Foundational requirements intake (serves SPEC-INTAKE-3623f1)

**Thread name (proposed):** `gtkb-membase-effective-use-recovery-slice-d-foundational-intake-2026-04-29`

**Deliverable:** standardized project bootstrap intake for foundational requirements.

**Type-vocabulary path (lower-risk per S319 Recommendation 2 Slice D):**
- Use existing `type='requirement'` with new `section='foundational/<category>'`.
- Avoid introducing `foundational_requirement` as a new `type` value until type vocabulary expansion is separately proposed and the dashboard/tests/queries are updated for it.
- Categories (10, carried forward from prior umbrella; subject to Codex acceptance per §11): `tech-stack`, `ui-targets`, `security-posture`, `tenancy`, `external-integrations`, `core-features`, `deployment-target`, `cost-constraints`, `operational-posture`, `compliance`.

**Two input modes:**
- Document upload: skill `gtkb-foundational-intake` parses prepared Markdown/YAML.
- In-session questionnaire: same skill, conversational walkthrough.

**Agent Red as seed corpus:** the skill ships with a reference foundational-requirements document extracted from Agent Red current state.

**Why fourth:** depends on Slices A + B + C; carries the largest content payload (Agent Red reference corpus).

**Does NOT deliver:** opinionated best-practices content layer. Captures what the owner says, not what the skill thinks is correct.

### 3.5 Parallel track - WI harvest reconciliation (Recommendation 3 from S319)

**Thread name (proposed):** `gtkb-membase-effective-use-recovery-wi-harvest-2026-04-29`

**Deliverable:** treat `GTKB-GOV-004` and `GTKB-GOV-010` as part of the same recovery program; classify every non-terminal MemBase WI into one of: active release blocker, standing backlog item, grouped backlog snapshot, obsolete/superseded, deferred/non-actionable with reason. Update dashboard to distinguish raw vs reconciled MemBase WI counts.

**Why parallel:** can run in parallel with Slice A (no shared files). On Slice D landing, the foundational-intake skill will produce additional WIs to be harvested by the same mechanism, so this track must land before or with Slice D.

---

## 4. Effectiveness Metrics (defined before implementation, per S319 Recommendation 4)

The implementation bridges will instrument these metrics. Each implementation bridge declares which metric it measures.

| # | Metric | Definition | Slice it measures |
|---|--------|------------|-------------------|
| 1 | Capture latency | Time from owner requirement statement to MemBase candidate row written | B |
| 2 | Visibility latency | Time from MemBase row creation to owner-visible chat event emission | A |
| 3 | Confirmation rate | % of captured candidates confirmed/rejected within session | C |
| 4 | Unreconciled WI count | Raw open MemBase WIs minus classified/reconciled WIs | parallel WI harvest |
| 5 | Bridge-to-MemBase drift | Bridge proposals containing requirements but no linked MemBase spec/intake row | B + cross-cutting |

The dashboard (`docs/gtkb-dashboard/`) updates to distinguish raw vs reconciled MemBase work as part of Slice A's implementation bridge.

---

## 5. Acceptance Criteria for Each Slice's Implementation Bridge (per work_list row 19)

The work_list specifies six acceptance criteria for "the future implementation proposal". Translated to per-slice acceptance criteria for each implementation bridge:

1. **Phantom-INDEX reconciliation statement.** Each implementation bridge cites this scoping bridge's §1 reconciliation by name, and adds any slice-specific phantom-state checks (e.g., whether a sub-thread already has phantom entries).
2. **Specific files per slice.** Each implementation bridge declares its exact file additions, modifications, and tests-touched list before requesting GO.
3. **Formal-artifact-approval handling for any DA/SPEC/GOV mutation automation.** Slice B auto-capture: deferred-only captures via Path 1 (formal gate fires at canonical promotion only); Slice C confirm: writes a canonical spec, fires the formal gate; Slice D: writes `type='requirement'` rows, fires the formal gate. Each implementation bridge declares which approval path it uses.
4. **Tests for event surfacing/capture/confirm-reject/false-positive-suppression.** Each implementation bridge declares its test files and assertions per the test-derivation table in the Specification Links section above.
5. **Dashboard metric updates distinguishing raw vs reconciled MemBase work.** Slice A's implementation bridge ships the dashboard delta. Subsequent slices add their own metric instrumentation but do not re-do the dashboard panel.
6. **Rollback plan that disables hooks without corrupting MemBase or DA state.** Each implementation bridge declares a rollback procedure: (a) disable the hook by removing its registration in `.claude/settings.json` (and matching `.codex/hooks.json` per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`); (b) leave the helper code in place (audit trail); (c) any DA/SPEC rows already written by the auto-capture path remain durable - rollback never deletes KB rows. The rollback is "stop creating new auto-captures", not "undo previously captured ones".

---

## 6. Sequencing and Concurrency

**Owner's standing-backlog row 19 statement:** "non-blocking parallel program; can ship in parallel with isolation Phases 2-6".

**Internal slice ordering:** A -> B -> C -> D. Each slice's implementation bridge waits for the previous slice to reach VERIFIED.

**Parallel tracks:**
- WI harvest reconciliation runs in parallel with Slice A (no shared files).
- Slice A and the active `GTKB-ISOLATION-016` Phase 8 rehearsal can run in parallel because they touch disjoint file sets.

**Gates:**
- Slice B does not start until Slice A is VERIFIED and the spec-events-seen.jsonl ledger format is stable.
- Slice C does not start until Slice B is VERIFIED.
- Slice D does not start until Slice C is VERIFIED, AND the WI harvest reconciliation track is at least at Slice 1 GO (so Slice D's added WIs flow into a working harvest pipeline).

**No bridge-protocol changes proposed.** This program uses the standard NEW -> GO -> implement -> NEW post-impl -> VERIFIED flow.

---

## 7. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:

- All new and modified files reside within `E:\GT-KB`.
- Upstream changes route to `E:\GT-KB\groundtruth-kb\` (in-root). No external `groundtruth-kb` checkout is used as a live dependency.
- Adopter applications (Agent Red) consume via `gt project upgrade` from in-root sources, NOT from external paths.
- This bridge does not introduce, propose, or rely on any path under `E:\Claude-Playground` or any home-directory mirror.

---

## 8. Files Touched (this bridge - scoping only)

**New:** none (this is a scoping/planning proposal).

**Modified:** `memory/work_list.md` row 19 - on GO, update with this bridge ID and the proposed slice thread names listed in §3.

**Not touched:** `src/**`, `scripts/**`, `templates/**`, `tests/**`, `docs/**` - all implementation defers to per-slice bridges.

---

## 9. Verification Matrix (this scoping bridge)

The Mandatory Specification-Derived Verification Gate at the scoping level verifies the **plan**, not the implementation. The four-row test-derivation table in the Specification Links section maps each slice to its driving spec and the assertion-class each test must satisfy.

For this scoping bridge, the verification owed at VERIFIED time is:

| Risk | Verification at scoping VERIFIED |
|------|-----------------------------------|
| Phantom-INDEX claim is wrong | Codex review re-runs the filesystem inspection (`Glob bridge/gtkb-membase-effective-use-umbrella*.md`) and the KB compressed-thread query (`get_deliberation('DELIB-1126')`) and confirms the 1-version count. |
| Slices don't cover all 3 SPEC-INTAKE-* specs | Codex review walks the §3 slice-to-spec map: A->2485e9, B->c9e997 (capture), C->c9e997 (closure), D->3623f1. |
| Slice ordering creates an unbuildable dependency chain | Codex review walks the §6 gate sequence and confirms each gate's prereq is achievable from prior-slice outputs alone. |
| Acceptance criteria #6 (rollback) creates a new corruption surface | Codex review confirms the rollback design ("disable hook registration; never delete KB rows") preserves audit-trail invariants. |
| Filename deviation from work_list (-2026-04-28 vs -2026-04-29) is a regression | §1 reconciliation explains the convention; Codex review confirms work_list will be updated on GO to cite the actual filename. |
| Effectiveness metrics are vapor | §4 names 5 metrics with definitions and assigned slices; Codex review confirms each implementation bridge can instrument its assigned metric without external dependencies. |

---

## 10. Out of Scope

These remain out of scope for the entire recovery program:

- Retroactive capture of past bridge proposals as specs (separate backfill WI if desired).
- Spec auto-promotion (`specified -> implemented -> verified`). Stays owner-gated via `/kb-promote` skill.
- Rejection-on-contradiction. The system captures; it does not refuse contradictory requirements. Conflict surfacing is downstream work.
- Non-English requirement handling. English classifier only.
- Multi-owner workflows. Single-owner assumption retained.
- Cross-project foundational-requirement inheritance. Each project gets its own foundational set.
- INDEX.md hygiene comment cross-referencing this recovery thread (see §1.4 - separate optional bridge).
- Type-vocabulary expansion to add `foundational_requirement` as a new `type` value (Slice D uses `type='requirement'` + `section='foundational/<category>'` instead).
- Agent Red production deployment. No `applications/Agent_Red/src/**` changes proposed in any slice. GOV-16 not triggered by this program.

---

## 11. Open Questions for Loyal Opposition Review

1. **Filename convention deviation.** §1.4 deviates from work_list row 19's literal filename suggestion (`-2026-04-28`) in favor of the bridge thread-opening date (`-2026-04-29`). Acceptable, or should the work_list literal win?

2. **Classifier false-positive bias (Slice B).** Tune toward false positives (capture liberally; owner reject overhead is low) or false negatives (capture conservatively; missed requirements get re-prompted)? Prior umbrella proposed false-positive bias; carrying that recommendation forward.

3. **Confirm/reject command surface (Slice C).** Prompt-recognition (option C1) vs slash-skill (option C2)? Prior umbrella defaulted to prompt-recognition; that bias is preserved here pending Codex preference.

4. **Foundational-category list size (Slice D).** 10 categories proposed (carried forward from prior umbrella). Too many => questionnaire fatigue; too few => missed context. Codex to accept the 10-category starter or propose a different cut.

5. **Slice C dependency on full Slice B VERIFIED.** Could Slice C land in parallel with Slice B's implementation bridge if the confirm/reject command operates on a stub `INTAKE-...` ID format independent of capture mechanism? Carries integration risk; default is sequential.

6. **WI harvest track scope.** Does the parallel WI harvest reconciliation track satisfy `GTKB-GOV-004` and `GTKB-GOV-010` outright, or should those remain as their own work-list rows with this track as a unifying program? Default: this track satisfies them; their work-list rows close on the parallel track's VERIFIED.

7. **Type-vocabulary expansion deferral (Slice D).** Section taxonomy `foundational/<category>` instead of new `type='foundational_requirement'`. Lower implementation risk but means future dashboard queries must know to filter on `type='requirement' AND section LIKE 'foundational/%'`. Acceptable, or is the dashboard-query risk material enough to warrant a parallel type-vocabulary expansion proposal first?

---

## 12. Decision Needed From Owner

Two decisions, neither blocking for this scoping bridge but blocking for the first implementation bridge:

1. **Upstream vs Agent Red-local routing** (carried forward from prior umbrella §9). Default: upstream `groundtruth-kb/` (in-root at `E:\GT-KB\groundtruth-kb\`), consistent with `gtkb-gov-proposal-standards` precedent and `GOV-AGENT-RED-GTKB-CONFORMANCE-001`. If owner prefers Agent-Red-local-first with later upstream promotion, narrow scope of all four implementation bridges accordingly.

2. **Slice C command surface** (per §11 question 3). Prompt-recognition (lower friction) vs slash-skill (more discoverable). Decision needed before Slice C implementation bridge files; not needed for this scoping bridge or for Slices A/B/D.

All other design choices surface in per-slice implementation bridges, not here.

---

## 13. Aligns With

- GT-KB vision filter (limit owner role to specs / clarifications / decisions).
- DELIB-0874 artifact-oriented governance.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (move repetitive plumbing behind services).
- SPEC-INTAKE-c9e997, SPEC-INTAKE-2485e9, SPEC-INTAKE-3623f1 (the three governing specs).
- GOV-AGENT-RED-GTKB-CONFORMANCE-001 (upstream-routing path).
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 (hook intent must mirror to `.codex/hooks.json` for non-Windows runtimes).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
