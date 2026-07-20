author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d38aabe5-2a10-40dc-a682-00a2992717be
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Loyal Opposition Advisory — NO-ACTION status is being misused for advisory dispositions

- Date: 2026-07-08T22:31Z
- Author: Loyal Opposition (Claude, harness B, interactive)
- Session role source: `::init gtkb lo` (session-stated override of durable Prime Builder registry role)
- HEAD at analysis: `3468e178`
- Work Items referenced: WI-5034, WI-5035, WI-5036, WI-5037, WI-5039 (advisory threads); WI-5068 (scan-helper parser, open P1)
- Specs / rules referenced: `.claude/rules/file-bridge-protocol.md`; `.claude/rules/canonical-terminology.md`; `advisory-disposition` skill
- Severity: **P1 (governance drift)** — bridge status-semantics confusion causing mis-routing; not active misdirection (no wrong implementation shipped), so not P0.
- Trigger: owner correction of NO-ACTION semantics during interactive LO bridge-queue auto-processing.

## Owner Correction (canonical NO-ACTION semantics)

The owner stated the canonical meaning of the `NO-ACTION` bridge status:

1. **NO-ACTION is a Prime Builder response to an LO GO or NO-GO verdict.**
2. **NO-ACTION is a rejection of the LO verdict**, usually because the verdict
   does not comply with appropriate governance. **The NO-ACTION reason must
   describe what the LO needs to do in order to correct the verdict.**

Implication: a well-formed `NO-ACTION` sits on top of a prior LO `GO`/`NO-GO`
in the same thread, and routes back to LO so the LO can re-issue a corrected,
GOV-compliant verdict. NO-ACTION is *not* a Prime disposition of an advisory.

## Claim

Five bridge threads currently surface in the Loyal-Opposition-actionable queue
as latest-status `NO-ACTION`, but they are a **status misuse**: each is a Prime
Builder *advisory disposition* written as `NO-ACTION`, with **no prior LO
`GO`/`NO-GO` verdict** for Prime to reject. Under the canonical semantics there
is no verdict for LO to correct, so none of the three LO verdicts (GO / NO-GO /
VERIFIED) is an honest response, and the entries are permanently non-terminal in
the interactive LO scan.

## Evidence

### Code confirms the owner's semantics

- `groundtruth-kb/src/groundtruth_kb/bridge/routing.py:24-26` —
  `_PRIME_STATUSES = frozenset({"NEW", "REVISED", "NO-ACTION"})` with the comment
  "NEW / REVISED / NO-ACTION are Prime Builder authoring acts." → **Prime authors
  NO-ACTION.**
- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py:126-127` — NO-ACTION
  maps to reason `lo_no_action_review_required`, action `review_no_action`. →
  **routes to LO to review/correct.**
- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py:132-133` — ADVISORY
  maps to reason `prime_advisory_disposition`, action `owner_disposition`. →
  **advisory dispositions are Prime's job and stay under ADVISORY.**
- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py:29` — NO-ACTION is in
  `LOYAL_OPPOSITION_ACTIONABLE_STATUSES`, so a NO-ACTION thread is routed to LO.

The code keeps ADVISORY (Prime-actionable disposition) and NO-ACTION (LO-actionable
verdict-correction) as distinct concerns. That matches the owner's definition.

### The five queue entries misuse NO-ACTION

Each chain is `001 ADVISORY → 002 NO-ACTION`; the `-002` entries were authored by
`prime-builder/codex` with `bridge_kind: operational_state_change` and body text
"Prime Advisory Disposition … Disposition: NO-ACTION on this advisory thread."
There is **no prior LO `GO`/`NO-GO`** in any of the five chains.

| Advisory thread | Underlying WI state (verified) | Disposition claim | Correct? |
|---|---|---|---|
| `gtkb-wi5034-f-agentic-turn-budget-advisory` | WI-5034 retired/resolved (DELIB-20260707-WI5034-RETIRE-SUPERSEDE) | retired/superseded | disposition rationale sound |
| `gtkb-wi5035-no-verdict-retry-backoff-advisory` | impl thread `gtkb-wi5035-no-verdict-retry-backoff` VERIFIED (-004) | adopted into proposal | sound |
| `gtkb-wi5036-stale-lease-reaping-advisory` | WI-5036 open/backlogged, owner-gated/unapproved | owner-gated, no proposal | sound |
| `gtkb-wi5037-invoke-ban-false-positive-advisory` | impl thread `gtkb-wi5037-invoke-ban-false-positive` VERIFIED (-004) | adopted+implemented+VERIFIED | sound |
| `gtkb-wi5039-watchdog-heartbeat-stale-advisory` | remediation thread `gtkb-wi5039-watchdog-heartbeat-remediation` VERIFIED (-006) | adopted+VERIFIED | sound |

The *dispositions themselves are factually correct* — the defect is the **status
chosen to record them** (`NO-ACTION` rather than leaving the thread `ADVISORY`
or moving it to a terminal status). Writing `NO-ACTION` flipped each thread from
Prime-actionable ADVISORY (`owner_disposition`) into LO-actionable NO-ACTION
(`review_no_action`), mis-routing five threads into the LO queue as
verdict-corrections that have no verdict to correct.

### Not a live token drain (but a persistent scan-clutter)

- `.gtkb-state/bridge-poller/dispatch-state.json` — only
  `gtkb-wi5039-watchdog-heartbeat-stale-advisory` carries a signature record
  (already suppressed); the other four advisory slugs are absent. Headless
  dispatch is quiesced, so this is not actively spawning workers. The entries
  persist in the *interactive* LO scan.

## Deficiency Rationale

- The `advisory-disposition` skill (`.claude/skills/advisory-disposition/SKILL.md`)
  routes an advisory no-op close (decision-tree item 1) into a disposition, but
  the observed Codex practice records that close as a `NO-ACTION`
  `operational_state_change` entry. That conflicts with the canonical NO-ACTION
  meaning (PB rejecting an LO verdict). The skill body itself does not name a
  bridge status for the no-op close, so the drift is in the writing practice /
  the status vocabulary the practice reaches for.
- `NO-ACTION` is **undocumented in governance surfaces**: it is absent from the
  status table in `.claude/rules/file-bridge-protocol.md` and from the glossary
  in `.claude/rules/canonical-terminology.md`. The owner's two statements above
  are the canonical definition and are not recorded anywhere yet. The absence of
  a documented definition is the root enabler of the misuse.

## WI-5068 premise concern (open P1, currently Prime-actionable)

`WI-5068` ("Bridge scan helpers omit NO-ACTION status parsing", P1,
PROJECT-GTKB-RELIABILITY-FIXES) is premised on making the scan helpers
*recognize* "latest NO-ACTION advisory-disposition files." Under the canonical
semantics, that is **accommodating the misuse** (advisory-disposition ≠
NO-ACTION) rather than fixing the root cause. Its thread
`gtkb-wi5068-no-action-scan-helper-parser` is at latest `NO-GO` (`-007`,
Prime-actionable, in revision) — a live window to reconsider the premise before
it hardens the misuse into the scanner contract. This is a flag for the next
Prime reviser of WI-5068, not an LO verdict (the thread is not LO-actionable).

## Recommended Prime Actions

1. **Document NO-ACTION canonically** in `.claude/rules/file-bridge-protocol.md`
   (status table + directional rules) and in the `.claude/rules/canonical-terminology.md`
   glossary, using the owner's definition: PB response to an LO GO/NO-GO verdict;
   a rejection of the verdict for GOV non-compliance; the reason must state what
   the LO must fix; routes back to LO to re-issue a corrected verdict.
2. **Fix the advisory no-op close path** so advisory dispositions never write
   `NO-ACTION`. Options for the eventual proposal to weigh: keep the thread
   `ADVISORY` with a recorded Prime disposition note, or move it to a terminal
   status (WITHDRAWN precedent: DELIB-20260703-DASHBOARD-…-WITHDRAWN,
   DELIB-20260704-WITHDRAW-…). Include a test asserting an advisory no-op close
   does not produce an LO-actionable NO-ACTION entry.
3. **Remediate the five existing misused threads** (WI-5034/5035/5036/5037/5039
   advisory) via the governed terminalization path chosen in (2). These are not
   LO-correctable; terminalizing them is a Prime/owner action.
4. **Reconsider WI-5068's premise** during its open revision so the scanner is
   not taught to treat advisory-disposition NO-ACTION files as legitimate.

## LO Disposition

No LO bridge verdict filed on any of the five threads: GO is nonsensical (no
proposal), NO-GO is dishonest (dispositions are factually correct) and loop-fuel,
and VERIFIED is both dishonest and mechanically refused by
`.claude/skills/verify/helpers/write_verdict.py::_assert_verification_ready`
(requires a prior GO in the chain — none exists). The honest LO outcome is this
advisory plus governed capture of the canonical definition and the remediation
work items.

## Captured Artifacts

- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` — owner-conversation / owner_decision: the canonical NO-ACTION definition + the AUQ "Full" decision + finding summary.
- `DELIB-20260708-NO-ACTION-SPEC-CANDIDATE` — owner-conversation / deferred: spec-intake requirement-candidate for the formal NO-ACTION spec (awaits governed confirmation into a canonical GOV/SPEC).
- `WI-5081` (P2, PROJECT-GTKB-RELIABILITY-FIXES) — Document canonical NO-ACTION semantics in file-bridge-protocol + glossary.
- `WI-5082` (P2, PROJECT-GTKB-RELIABILITY-FIXES) — Advisory no-op close must not write NO-ACTION; remediate the 5 misused threads. Depends on WI-5081.
- WI-5068 premise flag: recorded in this advisory + the anchor deliberation; surfaced for the next Prime reviser of `gtkb-wi5068-no-action-scan-helper-parser` (latest NO-GO `-007`, Prime-actionable).

No LO bridge verdict was filed on any of the 5 threads (see LO Disposition above).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
