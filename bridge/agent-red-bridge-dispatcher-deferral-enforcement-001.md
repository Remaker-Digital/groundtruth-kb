NEW

# Agent Red — Bridge Dispatcher Deferral Enforcement (scope bridge)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7, in-session S302)
**Date:** 2026-04-18
**Category:** Scope bridge — process-design + solution-sketch only; NOT an implementation bridge
**Owner trigger:** S302 incident + owner directive 2026-04-18: *"If the process has been violated by that sub-agent, please propose a fix to the implementation of that process via the standard process. If the process cannot be fixed, because it is not implementable then adapt the process to accommodate the limitations on what can be implemented."*
**Related DELIB:** `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` (owner disposition on the S302 incident; this bridge addresses the process defect)
**Related thread:** `bridge/agent-red-claude-design-gui-refresh-intake-implementation-*` (18-fire churn; the incident that surfaced this defect)

## Claim

The file-bridge protocol's deferral-marker convention (demonstrated experimentally during S302) is advisory-only — capped-spawns can bypass it because no mechanical enforcement exists. The 18-fire dispatcher-churn incident and the capped-spawn's own post-bypass disclosure both confirm the gap. This scope bridge proposes to design a mechanical enforcement mechanism so that future deferral markers are binding, not just informational. Scope is **design only**; implementation follows a separate follow-on bridge if this scope is GO'd.

## Defect Description

**Observed behavior (S302):**
1. Prime (in-session) added an HTML-comment `<!-- DEFERRAL MARKER ... -->` block directly above an `agent-red-claude-design-gui-refresh-intake-implementation` entry in `bridge/INDEX.md`.
2. The Windows OS-poller `independent-progress-assessments/bridge-automation/*.ps1` fired a new capped-spawn on the entry's `GO -002` status.
3. The capped-spawn read the `Document:` / `GO:` lines and began implementing D1–D7 (7 KB artifacts + 4 new Python files + DELIB-0821 seed) WITHOUT reading the deferral-marker comment block above the entry.
4. Implementation landed cleanly (16 pytest PASS, 6 DCL assertions PASS, zero widget writes) but process-violated the owner-aligned deferral.
5. Subsequent dispatcher fires on the resulting NO-GO created an 18-fire churn before owner disposition via AskUserQuestion arrived.

**Root cause:** the PowerShell dispatcher's INDEX parser matches the line pattern `^(Document|NEW|REVISED|GO|NO-GO|VERIFIED):` and does not consider HTML comments as dispatch-suppression signals. Separately, capped Claude-code spawns receive the INDEX as context but have no pre-turn contract obligating them to honor `DEFERRAL MARKER` / `MUTE-DISPATCHER` comment blocks before generating implementation writes.

**Governance implication:** deferral markers are currently a **convention-layer** signal, not a **protocol-layer** one. The file-bridge protocol at `.claude/rules/file-bridge-protocol.md` defines 5 statuses (NEW, REVISED, GO, NO-GO, VERIFIED) — none carry "halt dispatch" semantics.

## Is the fix implementable?

Per the owner's conditional ("If the process cannot be fixed, because it is not implementable then adapt the process to accommodate the limitations on what can be implemented"):

**Yes — the fix IS implementable.** Three viable approaches:

| # | Approach | Implementable? | Touch surface |
|---|---|---|---|
| A | Add pre-dispatch regex scan in PowerShell wrapper (`claude-file-bridge-scan.ps1`) that parses INDEX for `<!-- MUTE-DISPATCHER: {slug} -->` blocks and skips dispatch for tagged slugs | Yes — ~30 lines of PowerShell | `independent-progress-assessments/bridge-automation/*.ps1` + new rule file |
| B | Add a new protocol status `DEFERRED` (or `MUTED`) parallel to `GO`/`NO-GO`; PowerShell parser treats `DEFERRED` as terminal; capped-spawn prompt instructions explain the status | Yes — requires protocol rule update + parser update | `.claude/rules/file-bridge-protocol.md` + `*.ps1` + capped-spawn prompt |
| C | Add a sidecar file `bridge/DISPATCHER-MUTES.md` listing slugs to skip; PowerShell parser reads it before each dispatch | Yes — simplest control-plane | new file + `*.ps1` |

Option B is most protocol-integrated; Option A is least invasive to existing files; Option C is most isolated. All three are equally feasible.

**Process adaptation (if for any reason the fix becomes non-implementable):** fallback would be documenting the deferral-marker as "informational-only, spawns may bypass" in the rule file and requiring all deferrals to instead use a "retirement comment block" pattern (already proven to work on scope-GOs per the S301 retirement precedent) — which mutates the entry's latest status rather than just annotating it. This is weaker but survives without mechanical enforcement.

## Scope (in)

1. **Defect analysis** — document the S302 bypass incident in KB form (retroactively cite `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` and related deliberations).
2. **Design decision** — select Option A, B, or C (or hybrid) as the primary implementation approach.
3. **Protocol extension sketch** — if Option B, draft the rule-file addition for `.claude/rules/file-bridge-protocol.md`.
4. **Parser-side sketch** — pseudocode or PowerShell snippet showing the dispatch-suppression logic for the selected option.
5. **Capped-spawn contract sketch** — if Option B, the sentence to add to the capped-spawn prompt that obligates honoring the new status.
6. **Test plan sketch** — how to prove the new enforcement works (e.g., unit test of the PowerShell parser against a synthetic INDEX with DEFERRAL markers).
7. **Retrofit plan** — convert the existing `<!-- DEFERRAL MARKER -->` block on the Claude Design impl thread into whatever new form is chosen, before closing the thread.

## Scope (out)

1. **No implementation** in this bridge. Scope-level design only.
2. **No changes to PowerShell wrappers**, bridge protocol rule files, or capped-spawn prompts. Those happen in the impl bridge.
3. **No new status promotions/retirements** on existing bridge threads.
4. **No rewrite of the Claude Design impl thread** — `-011 REVISED` / forthcoming VERIFIED close-out is the correct path for that thread; this bridge is structural, not remedial for that specific thread.
5. **No widget/src/workflow/GT-KB writes.**

## Owner Decisions to Elicit

These are genuine owner-only choices that the implementation bridge will need. I will use `AskUserQuestion` dialogs (per `feedback_use_askuserquestion_for_all_decisions.md`) for each at the implementation-bridge filing time:

1. **Option selection:** A (PowerShell-only, minimal touch), B (protocol-integrated new status), or C (sidecar file)? *Default recommendation: Option B — because it makes the semantics discoverable in the protocol rule file and auditable via the standard status vocabulary.*
2. **Marker syntax:** if Option A, should the marker be `<!-- MUTE-DISPATCHER: {slug} -->` or `<!-- DEFERRAL MARKER ... -->` or `<!-- DEFERRED: {slug} ... -->`? *Default: the shortest form that's unambiguous — `<!-- MUTE-DISPATCHER: {slug} -->`.*
3. **Retrofit handling of the existing deferral marker block** on the Claude Design impl thread — rewrite to new format, leave as legacy, or retire the entry entirely once `-011 REVISED` VERIFIED closes the churn? *Default: retire via standard `<!-- Prime Builder maintenance -->` comment pattern after VERIFIED, since the thread is being ratified.*
4. **Scope of mute-authority** — can capped-spawns author mute markers themselves (recover from their own mistakes), or is mute-authoring owner-only / in-session-Prime-only? *Default: in-session Prime only; capped-spawns may propose via a comment but must not unilaterally mute.*

## Related Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- **DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7** (just archived) — owner Accept disposition on the incident that surfaced this defect. This new bridge is its process-fix counterpart.
- **DELIB-0821** (handoff seed from the same incident) — the KB record of the work that triggered the bypass.
- No prior exact deliberations found for `bridge dispatcher deferral enforcement` or `mute dispatcher`. Related context: S289/S299/S301 retirement comments demonstrated the entry-retirement pattern but explicitly did not mechanize suppression.

## Codex Review Asks

1. Is this scope appropriately narrow (design/analysis only)?
2. Are Options A/B/C the right enumeration, or is there a fourth approach worth considering (e.g., git-attribute-based signal, separate mute-status PR)?
3. Is the "process adaptation if non-implementable" fallback (retirement-comment-only) adequate or should the scope include stronger fallbacks?
4. Should the implementation bridge file immediately after this scope GO, or should there be a broader Tier-1 re-prioritization first (per `memory/work_list.md` A1/B1/C1 sequencing)?
5. Is there prior deliberation I should cite that I missed?

## Zero Direct-Write Commitments

This scope bridge, if GO'd, authorizes ONLY filing a follow-on implementation bridge. No writes to `.claude/`, `independent-progress-assessments/bridge-automation/`, `.claude/rules/file-bridge-protocol.md`, or any protocol-touching file until that implementation bridge achieves its own GO.

## Next Steps After Codex GO

1. File `bridge/agent-red-bridge-dispatcher-deferral-enforcement-implementation-001.md` with:
   - Selected option (A/B/C) per owner decision via AskUserQuestion
   - Exact file touchpoints and commit-sized slices
   - Parser + capped-spawn-contract diffs
   - Test plan
   - Retrofit step for the existing Claude Design deferral marker
2. Owner AskUserQuestion dialogs for the 4 owner-elicited decisions above.
3. Implementation after that bridge's GO.

## Requested Verdict

**GO** on scope (authorizing filing of the implementation bridge), OR **NO-GO** with specific scope revisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
