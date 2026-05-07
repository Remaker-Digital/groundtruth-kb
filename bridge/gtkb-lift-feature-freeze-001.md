# Lift S327 release-path freeze + remove stale defer markers

**Document ID:** `gtkb-lift-feature-freeze`
**Version:** 001
**Status:** NEW
**Filed by:** Prime Builder (Claude Opus 4.7, harness B)
**Filed at:** 2026-05-07 (S332)

## Summary

Owner directive (this session): "Remove all FREEZE or HOLD or DEFER states
from all plans and work items. They are all stale." Owner AUQ scope answer
locked the action set to categories A + B + C + H per the inventory below.
Owner AUQ approval-and-extend answer authorized full supersession of
`DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (not just the
freeze clause), which means the "release path = clean-adopter
productization" framing is also dropped.

This proposal:

1. Inserts a new owner-decision Deliberation Archive entry,
   `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`, that fully
   supersedes `DELIB-S327`.
2. Edits `memory/work_list.md` to remove the "Feature freeze in effect"
   paragraph, the "Deferred during release path (capture only; do not
   advance)" section, the "Default idle work directive 2026-05-06"
   freeze-derived ordering, and the `GTKB-GOV-007 PAUSED` tag.
3. Appends new MemBase versions for 7 backlogged WIs whose
   `status_detail` carries stale "deferred under feature freeze" or
   equivalent text, clearing that text.
4. Leaves untouched: technical-dependency defers (D), `wont_fix` items
   (E), `GTKB-DASHBOARD-RETENTION` contingent flag (F), VERIFIED bridge
   thread scope language (G), and 5 H-category items where the defer
   language reflects genuine dependency / contingency / different
   decision class.

This proposal does NOT lift other release blockers:

- `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` (P0 security override)
  remains active. The S327 freeze is independent of the P0 override.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  remains in force; the `v0.7.0-rc1` tag is still NOT authorized until
  canonical Agent Red migration completes. That is a separate owner
  decision recorded in S330 and is not affected by lifting S327.

## Specification Links

This proposal is governed by the following specifications and rule files:

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` — superseded in
  full by this proposal's `DELIB-S332`.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` — owner
  decision authorizing this work; created by this proposal's
  implementation step 1. Owner authority for this DELIB is the
  AskUserQuestion answers cited in §"Owner Decisions / Input" below; the
  DELIB record itself is inserted post-GO.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — preserved (not affected by this supersession); rc1 tag remains
  blocked until canonical migration completes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governs this work.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact insertion (the new
  DELIB) requires owner-visible approval evidence.
- `GOV-STANDING-BACKLOG-001` — `memory/work_list.md` is the human-readable
  view of the standing backlog; mutations here must preserve backlog
  source-of-truth alignment with MemBase.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, backlog
  state, and deferral states are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserve traceability across
  decisions and bridge threads.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan
  in §"Tests / verification" below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — application/root placement
  authority. Cited because this proposal touches
  `.claude/rules/file-bridge-protocol.md` (rule file under the ADR's
  applicability scope) and references Agent Red repository state in the
  context of preserving `DELIB-S330`'s canonical-migration prerequisite.
  This proposal does not propose any application/root placement change;
  the rc1 tag remains gated by the existing canonical-migration prerequisite.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers
  (advisory). Cited because this proposal performs deliberate lifecycle
  transitions: DELIB-S327 marked superseded, 7 backlogged WIs lifted
  from deferred status, and the GTKB-GOV-007 PAUSED tag retired.
- `.claude/rules/operating-model.md` §1 — operating-model framing of
  backlog as the unified view of known work.
- `.claude/rules/operating-model.md` §3 — implemented-vs-intended surfaces
  (this work clarifies which deferrals reflect platform-state-as-implemented
  vs. owner-policy-as-decided).
- `.claude/rules/file-bridge-protocol.md` — bridge filing, owner-decisions
  section gate, applicability preflight.
- `.claude/rules/codex-review-gate.md` — no implementation without GO.
- `.claude/rules/prime-builder-role.md` — AskUserQuestion as the only
  valid owner-decision channel; interrogative default for owner factual
  claims.

How proposed tests derive from linked specifications: §"Tests /
verification" below maps each acceptance criterion back to a specific
governing spec or rule clause.

### Pre-filing applicability preflight evidence

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze`
ran clean against this proposal at filing time:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:0d536c046512b0a4d08c23ea88cefab392f27bca49bca26517ec01221ded0231`

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing
Preflight Subsection", this evidence demonstrates that all applicable
required and advisory cross-cutting specifications are cited.

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` (2026-05-02 S327)
  — established the freeze and the clean-adopter-productization release
  path framing. Cited as superseded.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  — established the canonical-Agent-Red migration prerequisite for rc1
  tag authorization. Cited as preserved (not affected by supersession).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — relevant: this
  proposal's DELIB-insertion ceremony is itself an example of the
  recurring AI-mediated plumbing the principle flags. Lifting the freeze
  unblocks `GTKB-ARTIFACT-RECORDER-CLI`, which would absorb this
  ceremony.
- `DELIB-GTKB-IDP-TERMINOLOGY` — backlog as unified view; informs the
  H-category dispositions below.

No prior deliberation rejected the lifting of the S327 freeze. Search
performed against `gt deliberations search` for "feature freeze" and
"S327" yielded only the establishment record.

## Owner Decisions / Input

This proposal depends on owner approval and is filed under the
AskUserQuestion-only owner-decision channel per
`.claude/rules/prime-builder-role.md` §"AskUserQuestion as the Only Valid
Owner-Decision Channel".

Owner directive (this session, 2026-05-07): "We need to prioritize the
work which will improve the reliability and utility of GT-KB, because
these will help us do subsequent work more effectively." Followed by:
"Let's remove all FREEZE or HOLD or DEFER states from all plans and work
items. They are all stale."

AskUserQuestion #1 — Scope: "Which categories of FREEZE/HOLD/DEFER state
should I lift?"
- Owner answer: **A + B + C + H**
- Excluded by owner: D (technical-dependency defers), E (wont_fix
  items), F (`GTKB-DASHBOARD-RETENTION` contingent), G (VERIFIED bridge
  thread scope language).

AskUserQuestion #2 — Approval and extension: "Approve DELIB-S332 as
drafted and authorize me to file the bridge proposal?"
- Owner answer: **"Approve, but also lift S327 release-path goal
  entirely"**
- Effect: DELIB-S332 supersedes the entire DELIB-S327 (not just the
  "feature freeze in effect" clause). The "release path = clean-adopter
  productization" framing is dropped; rc1 sequencing becomes open. This
  proposal is filed accordingly.

These two AUQ answers, captured in this session's transcript, are the
sole owner-decision authority for this work. No prose-decision-ask is
relied upon.

## Implementation scope

After Loyal Opposition GO, Prime Builder will perform the following
mutations in a single bridge-implementation cycle:

### Step 1 — Insert DELIB-S332

Insert `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` into
the Deliberation Archive (`groundtruth.db.deliberations`). Body matches
the draft in the Appendix below. `source_type=owner_conversation`,
`outcome=owner_decision`, `session_id=S332`,
`detected_via=ask_user_question`, `supersedes=DELIB-S327-...`.

Approval-packet evidence at
`.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`
with `artifact_id`, `artifact_type=deliberation`, `body_hash`,
`owner_authority` enumerating both AUQ answers, and pointer to this
bridge thread.

### Step 2 — Edit `memory/work_list.md`

Remove or rewrite, in this order:

a. The "TOP — S327 RELEASE PATH" header (line ~17) — replace with a
   neutral "TOP — Active workstreams" header that no longer asserts
   release-path framing as the controlling priority.
b. The "Owner directive 2026-05-02 (S327, end-of-session)" paragraph
   (line ~19) — delete; this is the freeze record being superseded.
c. The "Feature freeze in effect" paragraph (line ~21) — delete.
d. The "Default idle work directive 2026-05-06" paragraph (line ~27) —
   rewrite to drop freeze-derived sequencing and replace with priority
   ordering driven by per-item leverage analysis (the analysis I
   surfaced earlier this session covers the top 10 items; the rewrite
   reflects that ordering).
e. The "Deferred during release path (capture only; do not advance)"
   section (line ~78) — delete the section header and reclassify each
   row as either `live` or `kept-deferred-with-reason` per the H-category
   inventory.
f. The `GTKB-GOV-007 - PAUSED` tag (line ~1656) — replace with new
   disposition note: "Stale PAUSED tag lifted 2026-05-07 S332. New
   disposition required: revise underlying commercial-readiness NO-GO
   bridge threads, retire, or reclassify. Tracked as separate work
   item." File a follow-on inventory work item in MemBase for the
   new disposition decision.

The "Owner pre-approval" header (line 10) and "Backlog source-of-truth
status" header (line 3) are preserved unchanged.

### Step 3 — Append MemBase WI versions

For each of the following 7 WIs, append a new version with `change_reason="Lift stale S327 feature-freeze defer marker per DELIB-S332 / bridge gtkb-lift-feature-freeze-001"`, clearing freeze-related text from `status_detail`:

- `GTKB-BRIDGE-INDEX-ROLE-INTENT-SENTINEL`
- `GTKB-STARTUP-REFRACTOR-001`
- `GTKB-ROLE-ENHANCEMENT`
- `GTKB-ISOLATION-017-SLICE-5.5`
- `GTKB-PIP-INSTALL-ADOPTER-UX-001`
- `GTKB-CI-COVERAGE-FOR-PLATFORM-001`
- `GTKB-EVALUATION-MODULE-RESTORATION-001`

For the 4 already-active items (5.5, pip-install-UX, CI-coverage,
evaluation-module), the new `status_detail` reflects their actual bridge
state (e.g., "active in bridge -005 awaiting VERIFIED").

For the 3 newly-unblocked items (sentinel, startup-refactor, role-enhancement),
the new `status_detail` is "live; was deferred under S327 feature freeze;
unblocked by DELIB-S332 (2026-05-07)".

### Step 4 — NOT done in this proposal (out of scope)

- D items (technical-dependency defers): unchanged.
- E items (wont_fix): unchanged.
- F item (`GTKB-DASHBOARD-RETENTION` contingent): unchanged.
- G items (VERIFIED bridge .md scope language): unchanged. Per the
  bridge protocol §Guardrails, bridge files are append-only audit trail.
- 5 keep-as-is H items: unchanged. (`GTKB-MASS-001`,
  `GTKB-DASHBOARD-002-SLICE-2-2-METRICS`,
  `GTKB-DASHBOARD-RETENTION` (also F),
  `GTKB-GOV-008`,
  `WORKLIST-...-CLAUDE-DESIGN-GUI-EXPLORATION`.)
- `DELIB-S330` and the canonical-Agent-Red repo migration prerequisite
  for rc1: unchanged. The rc1 tag is still NOT authorized.
- `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` (P0 security override):
  unchanged. Remains in flight per its own slice schedule.

## Tests / verification

Each acceptance criterion below derives from a linked specification.

### Verification commands

```bash
# 1. work_list.md no longer contains freeze/PAUSED-2026-04-18 language
grep -c "Feature freeze in effect" memory/work_list.md  # expect 0
grep -c "Deferred during release path" memory/work_list.md  # expect 0
grep -c "GTKB-GOV-007 - PAUSED" memory/work_list.md  # expect 0

# 2. MemBase: 0 backlogged WIs still carry "deferred under feature freeze"
python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(); items=db.list_work_items(); latest={}; [latest.update({w['id']:w}) for w in items if w['id'] not in latest or w['version']>latest[w['id']]['version']]; matches=[w for w in latest.values() if 'deferred under feature freeze' in (w.get('status_detail') or '')]; print(f'remaining freeze-defer WIs: {len(matches)}')"
# expect: remaining freeze-defer WIs: 0

# 3. DELIB-S332 retrievable
gt deliberations search "DELIB-S332-LIFT-FEATURE-FREEZE"
# expect: 1 record returned

# 4. DELIB-S327 marked superseded (current-state lookup)
gt deliberations show DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION
# expect: superseded_by field references DELIB-S332

# 5. Approval packet exists
test -f .groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json
# expect: exit 0

# 6. Bridge applicability preflight passes on this proposal
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze
# expect: preflight_passed: true; missing_required_specs: []
```

### Spec-to-test mapping

| Test | Verifies | Linked spec |
|---|---|---|
| 1 | work_list.md cleanup of freeze markers | Implementation scope §2 a-f; `GOV-STANDING-BACKLOG-001` |
| 2 | MemBase WI status_detail cleanup | Implementation scope §3; `GOV-STANDING-BACKLOG-001` |
| 3 | DELIB-S332 inserted and retrievable | Implementation scope §1; `GOV-ARTIFACT-APPROVAL-001` |
| 4 | DELIB-S327 supersession recorded | Implementation scope §1; owner AUQ #2 |
| 5 | Formal-artifact-approval packet exists | `GOV-ARTIFACT-APPROVAL-001` |
| 6 | Cross-cutting spec citations complete | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `.claude/rules/file-bridge-protocol.md` "Mandatory Pre-Filing Preflight Subsection" |

## Risk / rollback

**Risks:**

- **Loss of release-path framing.** Lifting DELIB-S327 entirely removes
  the "release path = clean-adopter productization" goal as an active
  organizing principle. The "Default idle work directive 2026-05-06" no
  longer has freeze-derived ordering authority. Mitigation: rc1 tag
  remains gated by DELIB-S330 (canonical Agent Red migration), which is
  preserved. Other release blockers (P0 security override) preserved.
  Owner can re-establish a release-path framing in a future DELIB if
  this turns out to be misjudged.
- **Markdown drift from MemBase.** `memory/work_list.md` is currently a
  human-readable view; canonical backlog is MemBase. This proposal
  edits the markdown directly (not via `gt backlog regenerate`) because
  the regeneration tooling for the freeze-derived sections does not
  exist yet. The drift is bounded and visible. Mitigation: include a
  note in the rewritten "Default idle work directive" pointing to
  MemBase for canonical priority.
- **Stale references in other artifacts.** Other rule files or DELIBs
  may reference the S327 freeze. A grep across the repo identifies any
  such references; they get converted to historical references during
  implementation.
- **DELIB-S327 referenced by parked DELIBs or specs.** The supersession
  is one-way; downstream consumers reading `DELIB-S327` will see it
  superseded by `DELIB-S332` (per `superseded_by` field) and can chase
  the reference forward.

**Rollback procedure:**

1. Insert a new DELIB superseding `DELIB-S332` and re-establishing the
   freeze (or whatever subset was retracted).
2. Append new MemBase WI versions restoring prior `status_detail`.
3. Edit `memory/work_list.md` to restore the freeze paragraphs; cite
   the rollback DELIB.
4. VERIFIED bridge files: not touched in either direction; no rollback
   needed.

Rollback is reversible at the same granularity as the forward action.

## Acceptance criteria

1. `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` exists in
   the Deliberation Archive, supersedes `DELIB-S327`, and carries
   `source_type=owner_conversation`,
   `detected_via=ask_user_question`.
2. Formal-artifact-approval packet at
   `.groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json`
   exists, validates against the schema, and cites both AUQ answers.
3. `memory/work_list.md` no longer contains "Feature freeze in effect",
   "Deferred during release path (capture only; do not advance)", or
   "GTKB-GOV-007 - PAUSED" strings.
4. The 7 listed WIs no longer carry "deferred under feature freeze"
   text in their latest-version `status_detail`.
5. The 5 keep-as-is H items, all D/E/F/G items, `DELIB-S330`, and the
   `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` workstream are
   unchanged.
6. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lift-feature-freeze`
   reports `preflight_passed: true`.
7. `python -m pytest tests/scripts/ -k "bridge or backlog" -q` passes
   (sanity check that bridge/backlog tooling is not regressed).

## Recommended commit type

`chore:` — governance hygiene; lifts a stale governance state and clears
stale defer markers. No new capability surface; one DELIB insert, ~6
markdown sections rewritten, 7 MemBase WI versions appended.

(Per `.claude/rules/file-bridge-protocol.md` §"Conventional Commits Type
Discipline": this is true maintenance — the DELIB itself is governance
hygiene, the markdown edits remove stale text, and the MemBase WI
versions update field values without changing schemas, public APIs, or
behavior.)

## Appendix — DELIB-S332 draft body (for review during GO/NO-GO)

```
DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING

source_type:    owner_conversation
outcome:        owner_decision
session_id:     S332
detected_via:   ask_user_question
recorded_at:    2026-05-07
supersedes:     DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION (full)
preserves:      DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE
                DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE
                GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT (P0)

Decision:
  1. Lift the S327 release-path "Feature freeze in effect" governance
     state. Backlog DB Slices 2-7, Term Primer Slices 2-5, and Resource
     Disambiguation Slices 2-5 may now advance. GTKB-ARTIFACT-RECORDER-CLI
     is no longer freeze-blocked.
  2. Drop the S327 "release path = clean-adopter productization"
     framing. rc1 sequencing is open; the "Default idle work directive
     2026-05-06" is rewritten to reflect per-item leverage rather than
     freeze-derived ordering.
  3. Lift the GTKB-GOV-007 PAUSED tag (2026-04-18). Entry stale; new
     disposition required.
  4. Clear stale "deferred under feature freeze" / equivalent text from
     the status_detail field of 7 backlogged WIs. 5 H-category items
     stay (genuine dependency / contingency / different decision class).

Excluded from this decision (per owner AUQ):
  D. Technical-dependency defers - kept (real build-order)
  E. wont_fix items - different decision class
  F. Contingent items (GTKB-DASHBOARD-RETENTION) - kept
  G. VERIFIED bridge thread scope language - append-only audit trail

Preserved release blockers (NOT lifted by this decision):
  - P0 security override (GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT)
  - DELIB-S330 canonical Agent Red repo migration prerequisite for rc1
  - Slice 8.5 / 8.6 in-flight bridge work

Rationale:
  Owner directive 2026-05-07: these states are stale. The S327 freeze
  served its planning-sprint purpose during isolation-017 close-out
  but is no longer load-bearing on rc1 work. Acceleration items
  deferred under it (Backlog DB, Recorder CLI, Term Primer follow-on
  slices) have higher per-session leverage than the freeze's
  protective value. The release-path goal framing is also dropped
  because rc1 sequencing is governed by other DELIBs (S330 canonical
  migration prerequisite + P0 security override) which remain
  authoritative.

Authority:
  Two AskUserQuestion answers in S332 (Q1: "A + B + C + H"; Q2:
  "Approve, but also lift S327 release-path goal entirely"), captured
  in session transcript and approval-packet evidence at
  .groundtruth/formal-artifact-approvals/2026-05-07-DELIB-S332-LIFT-FEATURE-FREEZE.json.
```

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
