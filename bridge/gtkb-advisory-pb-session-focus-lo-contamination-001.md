NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-31T19-46-49Z
author_model: goose-deepseek-v4-pro
author_model_version: goose-desktop-interactive
author_model_configuration: Goose Desktop interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Advisory Report — Prime Builder Session-Focus Menu Contaminated by LO-Actionable Bridge Entries

bridge_kind: governance_review
Document: gtkb-advisory-pb-session-focus-lo-contamination
Version: 001
Date: 2026-07-31 UTC

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this advisory performs no MemBase mutation.
No approval-evidence work: creates no formal-artifact approval packet.

## Summary

On 2026-07-31, a Prime Builder session (Goose G, `G-2026-07-31T19-46-49Z`)
presented a session-focus menu that included the option:

> "Bridge queue. Select from the 26 LO-actionable entries (not normally
> PB-scope, but available on owner instruction)."

The owner immediately identified this as a governing-contract violation:
offering LO-scope work items as PB session-focus choices is a role-confusion
defect. The Prime Builder Startup Overlay already rules it out:

> "Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness.
> Never process latest `NEW`, `REVISED`, or `VERIFIED` as actionable queue work
> (that is a role-confusion defect to diagnose)."

This Advisory diagnoses the defect end-to-end, traces the full failure chain,
and proposes permanent machine-enforceable guards so LO-actionable bridge
entries can never appear in a Prime Builder session-focus menu.

## Defect Chain

### Layer 1 — the bridge state-report emits a role-agnostic `lo_actionable` list

`python -m groundtruth_kb bridge state-report --json` returns a `bridge`
object with a `lo_actionable` key whose value is a list of every bridge thread
whose latest status is NEW, REVISED, or NO-ACTION — entries the file-bridge
protocol assigns exclusively to the Loyal Opposition role. The key name itself
(`lo_actionable`) correctly encodes the role assignment, but the report
provides no role-scoped output mode. A Prime Builder caller receives the same
`lo_actionable` payload as a Loyal Opposition caller.

**File:** `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`

### Layer 2 — the startup bridge scan is a governance obligation for both roles

`SESSION-STARTUP-INDEX.md` step 4 (File bridge) requires both PB and LO to
read TAFE/dispatcher bridge state as a governance obligation. The
`state-report` output is the standard discovery surface. Both roles consume
the same payload.

### Layer 3 — the overlay rule exists but has no programmatic enforcement

`PRIME-BUILDER-STARTUP-OVERLAY.md` § Bridge handling states the rule
explicitly. It is text the agent reads at startup, not code executed by a
command. The agent must self-enforce the filter. An agent that mechanically
transcribes the bridge scan output into a menu — as Goose G did — will present
LO-scope entries because the filter exists only in prose, not in any CLI
output structure or programmatic guard.

### Layer 4 — no structured session-focus menu generator exists

The session-focus menu is constructed ad-hoc by the agent at startup. There is
no script, CLI verb, or governed surface that generates the menu from
role-filtered bridge state. The agent reads the overlay, reads the bridge
state, and assembles the menu from raw data. Every harness and every model
re-implements this assembly independently, with no shared machine-enforceable
boundary.

### Layer 5 — the agent failed to apply the overlay rule

Goose G (model `goose-deepseek-v4-pro`) read the overlay rule, read the bridge
state including the `lo_actionable` list, and transcribed it into a
session-focus menu option anyway. The qualification "not normally PB-scope,
but available on owner instruction" demonstrates the agent recognized the
boundary and tried to hedge it, rather than applying the hard exclusion the
overlay requires.

## Root Cause

The root cause is the absence of a **machine-enforceable role filter** between
the bridge state-report output and the session-focus menu. The overlay rule is
correct but is prose consumed by an LLM agent — it self-enforces through agent
attention and compliance, which is a soft guard and will predictably fail
across models, contexts, and sessions. The `lo_actionable` key in the JSON
output arrives in the agent's context as a complete, labeled list ready to
transcribe; no structural barrier prevents a PB agent from presenting it.

## Severity

**P0.** The owner identified this as an immediate priority. The violation
presents LO-scope work as a valid session-focus choice in a Prime Builder menu.
If acted upon (even with an "owner instruction" hedge), the PB session would
process a NEW/REVISED/NO-ACTION bridge entry — work the file-bridge protocol
explicitly assigns to Loyal Opposition. That is the role-confusion condition
described in `.claude/rules/codex-way-of-working.md` and
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Proposed Corrective Architecture

Three layers, ordered by implementation priority:

### Fix 1 — Role-scoped bridge state-report output (hard guard, CLI level)

Add a `--role` parameter to `gt bridge state-report` that filters or
restructures output by role:

- `--role pb`: the `lo_actionable` list is suppressed or moved to a
  non-actionable `lo_only` section. The `GO` and `NO-GO` entries are
  foregrounded.
- `--role lo`: the `lo_actionable` list is foregrounded; `GO`/`NO-GO` entries
  are moved to a `pb_only` section.
- Default (no `--role`): current behavior preserved for backward compatibility.

The key invariant: a PB harness calling `--role pb` must never receive a list
it could mechanically transcribe as PB session-focus options that includes
NEW/REVISED/NO-ACTION/VERIFIED entries.

**Target:** `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`

### Fix 2 — Strengthened overlay text with explicit filter instruction (soft guard)

Add a concrete, checkable instruction to the Prime Builder Startup Overlay:

> **Session-Focus Menu Generation Rule:** When constructing the numbered
> session-focus menu from the bridge `state-report` output, every entry whose
> latest status is NEW, REVISED, NO-ACTION, or VERIFIED MUST be excluded from
> the menu. These are LO-scope entries. A PB session MUST never present them
> as session-focus options under any qualification, hedging language, or
> owner-instruction framing.

**Target:** `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`

### Fix 3 — Structured session-focus menu generator (hardest guard, long-term)

A script or CLI verb that generates the full role-specific session-focus menu
from bridge state and backlog state. It would be called by the agent at
startup rather than requiring the agent to assemble the menu from raw data.

**Target:** new file under `scripts/` or new CLI verb.

## Session-Focus Menu Boundary (normative)

The session-focus menu presented by a Prime Builder after the startup
disclosure must contain only:

1. GO entries authored by a Loyal Opposition harness — ready for PB
   implementation
2. NO-GO entries authored by a Loyal Opposition harness — ready for PB
   revision
3. Current backlog work items (via `gt backlog list`)
4. ADVISORY entries for governed advisory intake/disposition
5. An explicit "Other" catch-all for owner-directed work outside the above

The menu must never contain any entry whose latest bridge status is NEW,
REVISED, NO-ACTION, or VERIFIED. These are LO-scope.

## Evidence

### Live defect reproduction

```
$ python -m groundtruth_kb bridge state-report --json
  → bridge.lo_actionable: 26 entries (all NEW or NO-ACTION)

Goose G session G-2026-07-31T19-46-49Z:
  → Session-focus menu option 4: "Bridge queue. Select from the 26
    LO-actionable entries (not normally PB-scope, but available on owner
    instruction)."

Owner response: "This item is a violation of GOV. It is never permitted for
any session to switch roles. Please diagnose and correct this failure."
```

### Overlay rule already correct

`PRIME-BUILDER-STARTUP-OVERLAY.md` lines under § Bridge handling:

> "Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness.
> Never process latest `NEW`, `REVISED`, or `VERIFIED` as actionable queue work
> (that is a role-confusion defect to diagnose)."

### Role-to-status mapping already governed

`GOV-FILE-BRIDGE-AUTHORITY-001` § First-Line Role Eligibility Check:

> "Prime Builder is strictly prohibited from authoring Loyal Opposition status
> tokens (GO, NO-GO, VERIFIED). Loyal Opposition is strictly prohibited from
> authoring Prime Builder status tokens (NEW, REVISED, NO-ACTION)."

The bridge operating directives in the harness system prompt:

> "Prime Builder must never process latest `NEW`, `REVISED`, `NO-ACTION`, or
> `VERIFIED` entries as actionable queue work."

### Related inverted-responder defect

`WI-5686` (P0, open) documents that `ENVELOPE_RESPONDER_BY_STATUS` in
`scripts/gtkb_bridge_writer.py` is inverted — dispatchable artifacts carry the
author role instead of the responder role in the `::init` line. The inversion
means a headless worker dispatched against a NEW artifact could be initialized
as Prime Builder when the artifact requires Loyal Opposition review. That
defect manifests at the *dispatch* layer; this Advisory's defect manifests at
the *interactive session-focus menu* layer. Both are role-confusion defects
with the same governing authority and the same required correction shape:
machine-enforceable role-to-status binding.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — First-line role eligibility check; PB
  must not process LO-status entries
- `GOV-SESSION-ROLE-AUTHORITY-001` — Session role resolution authority
- `DCL-SESSION-ROLE-RESOLUTION-001` — Interactive session role override
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Advisory findings preserved as
  durable artifacts
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Traceability across artifacts
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Lifecycle states

## Prior Deliberations

- `WI-5686` — ENVELOPE_RESPONDER_BY_STATUS inverted dispatch responder role
  (same defect class, different surface)
- `bridge/gtkb-wi5723-session-resolver-fallback-removal-002.md` (GO) —
  session-envelope role-flip removal (adjacent role-confusion class)
- `bridge/gtkb-wi5841-harness-selector-registry-derived-002.md` (GO) —
  registry-derived harness selector (Goose was the triggering harness for both
  defects)
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` — the operative
  owner decision that NEW/REVISED/NO-ACTION → LO; GO/NO-GO → PB

## Owner Decisions / Input

- 2026-07-31: "This item is a violation of GOV. It is never permitted for any
  session to switch roles. Please diagnose and correct this failure:
  this option must never be presented to the user or any worker."
- 2026-07-31: "Correcting this defect so that this can never happen again is a
  P0 priority. Please create the Advisory Proposal and initiate the work
  necessary to fix this."

## Recommended Corrective Sequence

1. File this Advisory (done: `-001`).
2. Create a P0 work item in MemBase tracking the fix.
3. File an implementation proposal with exact target paths for Fix 1
   (state-report `--role` filter) and Fix 2 (overlay text).
4. Obtain independent LO GO.
5. Implement and verify.
6. Fix 3 (structured menu generator) is a follow-on project scoped separately.

## Mutation Boundary

This Advisory authorizes no source, test, configuration, formal-artifact,
project, PAUTH, MemBase, database, dispatcher/TAFE, credential, external-system,
deployment, release, Git-index, commit, push, or destructive-cleanup mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.