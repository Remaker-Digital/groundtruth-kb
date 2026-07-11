NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ea0-6326-78a1-a2f4-775fd98d66ce
author_model: gpt-5.5
author_model_version: desktop
author_model_configuration: reasoning=xhigh; approval_policy=never; interactive Prime Builder session
author_metadata_source: live Codex session envelope plus bridge state-report

bridge_kind: governance_advisory
Document: gtkb-wi5186-lo-startup-gate-dcl-reconciliation
Version: 001
Date: 2026-07-11 UTC
Author: Prime Builder (Codex, harness A)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5186
target_paths: []

# Governance Review: Reconcile the Fresh LO Relay With the Startup-Input Gate

## Summary

This non-implementation governance review resolves the contradictory startup
contracts behind WI-5186. A fresh `::init gtkb lo` relay currently instructs
the Loyal Opposition (LO) to verify live bridge state and, in default mode,
process actionable `NEW`/`REVISED` entries in the init turn. The co-resident
startup-input gate nonetheless holds `startup_response_pending` until another
owner message and therefore blocks the required `gt` reads and governed verdict
writer.

The owner selected Option C in `DELIB-20260711-LO-FRESH-INIT-GATE-CLEAR`: after
a successful LO startup-disclosure relay, clear the pending gate for the LO path
only. The owner then selected amendment of the existing startup-gate DCL in
`DELIB-20260711-LO-FRESH-INIT-GATE-DCL-AMENDMENT`.

This proposal requests Loyal Opposition review of the exact DCL amendments
below. It does not mutate MemBase, source, tests, hooks, configuration, or
bridge dispatch state beyond the ordinary filing of this review request. After
GO and formal-artifact approval of the exact content, a separate implementation
proposal will request the protected code and test changes.

## Evidence and Non-Duplication

- `scripts/session_self_initialization.py` renders the default-LO instruction to
  verify live bridge state and auto-process actionable entries in the init turn.
- `scripts/workstream_focus.py` records `startup_response_pending=True` when an
  init keyword matches, and `guard_tool_use` blocks all tool use except the
  exact disclosure-cache read.
- A live in-memory guard reproduction on 2026-07-11 blocked both
  `gt bridge state-report --markdown` and a governed verdict-writer-shaped tool
  call while pending, while allowing only the exact cache read.
- `WI-4440` corrected the relay-stop behavior but did not add a gate release.
  `WI-5083` covers continuation re-arm, `WI-5118` covers AUQ/mid-session
  clearing, and `WI-4827` covers relay-failure TOCTOU; none covers this fresh
  LO relay conflict.

## Specification Links

- `DCL-STARTUP-GATE-FRESH-START-ONLY-001` - the current fresh-start gate
  constraint to be amended with the explicit LO relay release.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - the current universal
  relay-stop wording that must be reconciled with LO continuation.
- `GOV-SESSION-SELF-INITIALIZATION-001` - required startup actions must be
  executed against live bridge state rather than merely displayed.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - disclosure remains visible
  before the operational startup action.
- `ADR-LOYAL-OPPOSITION-STARTUP-AUTO-PROCESS-DEFAULT-001` - current default-LO
  auto-process authority, preserved in the active startup overlay and bridge
  lineage; it is not currently returned by `gt spec show`.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the
  shared hook behavior must remain semantically equivalent for Claude and Codex.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, and
  `DCL-ARTIFACT-APPROVAL-HOOK-001` - exact DCL mutations require formal-artifact
  packets and validation after review.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the owner decisions, DCLs, work
  item, and bridge review are durable governed artifacts rather than session
  memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the detected contradiction triggers
  bounded formal-artifact reconciliation rather than an undocumented runtime
  workaround.
- `GOV-STANDING-BACKLOG-001` - WI-5186 remains the visible reliability work
  authority through the requirement and implementation slices.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this bridge review is the prerequisite for
  the governed follow-on work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the later implementation
  proposal and its verification must retain complete spec-to-test linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5186 is an active
  member of the cited standing-authorized project.

## Prior Deliberations

- `DELIB-20260711-LO-FRESH-INIT-GATE-CLEAR` - owner selected the LO-only relay
  gate-clear contract over tool-specific exemption or relay-stop alternatives.
- `DELIB-20260711-LO-FRESH-INIT-GATE-DCL-AMENDMENT` - owner selected amendment
  of the existing startup-gate DCL rather than a new DCL.
- `WI-4440` bridge chain, culminating in
  `bridge/gtkb-lo-init-startup-relay-harness-action-004.md` - current same-turn
  LO startup instruction that the gate must no longer contradict.
- `bridge/gtkb-startup-relay-pretooluse-read-exemption-005.md` - the existing
  cache-read-only exemption is deliberately narrower than the selected Option C.
- `bridge/gtkb-wi5083-startup-input-gate-rearm-fix-005.md` and
  `bridge/gtkb-wi5118-startup-gate-fresh-start-only-002.md` - nearby re-arm and
  AUQ-clear repairs that remain distinct.


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 39120 and this is thread id 33004.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- `DELIB-20260711-LO-FRESH-INIT-GATE-CLEAR`: owner selected Option C, clearing
  `startup_response_pending` in the successful LO relay path so the same-turn
  required action can run.
- `DELIB-20260711-LO-FRESH-INIT-GATE-DCL-AMENDMENT`: owner selected amendment
  of `DCL-STARTUP-GATE-FRESH-START-ONLY-001` as the formal carrier.
- The interactive environment did not expose AskUserQuestion; both selections
  were captured immediately as append-only owner-decision deliberations. They
  authorize this review request, not mutation of the exact formal content.

## Requirement Sufficiency

New or revised requirement required before implementation. The current DCLs
require both a post-disclosure stop and a fresh-session wait for the next owner
message, so they cannot truthfully authorize the selected LO same-turn behavior.
This bridge proposes the bounded requirement correction first. The follow-on
implementation proposal may declare existing requirements sufficient only after
these exact amendments have received LO review, owner formal-artifact approval,
and MemBase insertion.

## Proposed DCL Amendments

### DCL-STARTUP-GATE-FRESH-START-ONLY-001: proposed replacement description

```markdown
## Purpose

Ensure the startup-input gate applies only to genuinely fresh interactive
sessions, cannot re-arm after it has been satisfied within the same session
context, and does not prevent a successfully relayed Loyal Opposition startup
action that the session contract requires in the same init turn.

## Constraint

1. The startup-input gate may arm only for a canonical, genuinely fresh
   `SessionStart`.
2. Resume, compaction, continuation, AUQ completion, repeated AUQ, role
   changes, and mid-session init-keyword processing must not re-arm a satisfied
   gate.
3. Once owner input satisfies or clears the gate, satisfaction is monotonic for
   that interactive session context.
4. An AskUserQuestion answer counts as owner input. It must clear a pending
   gate, or otherwise prevent that gate from blocking subsequent non-exempt
   tool use.
5. A genuinely fresh Prime Builder or non-LO session context must still arm the
   gate and wait for the next owner message. A genuinely fresh LO init-keyword
   relay may clear `startup_response_pending` only after it has rendered the
   complete owner-visible startup disclosure successfully. The clear must be
   auditable with reason `lo_startup_relay` and must never occur on relay
   failure.
6. After that LO-only relay clear, default LO startup may verify live bridge
   state, report the live scan, and process actionable `NEW`/`REVISED` entries
   oldest-to-newest in the same init turn. Advisory LO startup may verify and
   report live bridge state in the same init turn, but it must not auto-process
   entries or write a verdict until the owner explicitly switches from advisory
   mode.
7. Stale, mismatched, or continuation-originated pending state must fail closed
   by clearing with an auditable lifecycle reason, without weakening fresh
   session disclosure requirements.
8. Applicable Prime Builder and Loyal Opposition paths must exhibit equivalent
   behavior across supported interactive harnesses.

## Required behavior and acceptance criteria

- Fresh-session init displays the required disclosure before any LO startup
  action or ordinary task work.
- A successful fresh LO relay records `lo_startup_relay` and permits the
  mandatory same-turn bridge-state reads and governed writer path in default
  mode.
- A successful fresh LO advisory relay permits only the live scan/report
  workflow; advisory mode remains opt-in for auto-processing and verdict
  writing.
- Fresh PB and non-LO startup remains pending and blocks non-exempt tools until
  normal owner input.
- A normal follow-up owner message clears the pending gate.
- An AUQ answer clears the pending gate.
- Repeated AUQ round trips do not re-arm the gate.
- Compaction or resume after satisfaction preserves the satisfied state.
- Mid-session role or init-keyword changes do not re-arm the gate.
- A distinct fresh session re-arms the gate.
- Regression coverage exercises default LO relay clearing, LO advisory
  opt-in, PB blocking, AUQ, repeated AUQ, compaction/resume, fresh-session
  reset, and applicable PB/LO harness paths.
- Audit state may identify lifecycle events and clear reasons but must not
  retain owner prompt or AUQ-answer content.

## Evidence

- WI-5118 PB reproduction, session `fea7dd14`, 2026-07-09.
- WI-5118 LO/harness-B reproduction, session `be4929b6`, 2026-07-10.
- WI-5186 fresh LO default-init reproduction, 2026-07-11: the relay-directed
  `gt` bridge read and governed verdict writer were blocked while the cache read
  alone remained exempt.
- WI-5083 VERIFIED bridge chain, which corrected continuation re-arming and
  identified this constraint as follow-on work.

## Related specifications

`GOV-SESSION-SELF-INITIALIZATION-001`,
`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001`,
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`,
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-CROSS-HARNESS-PARITY-001`, and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`.

## Out of scope

This constraint does not remove startup disclosure, weaken Prime Builder focus
gating, make advisory processing implicit, bypass PAUTH, or authorize
implementation.
```

### DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001: proposed replacement description

```markdown
## Purpose

Ensure that a matched GT-KB init keyword produces the owner-visible startup
disclosure in the assistant response, not merely hook state that claims the
disclosure was emitted, while allowing the specified Loyal Opposition startup
action to continue in the same init turn.

This constraint covers the interactive startup path in which a first owner
message such as `::init gtkb lo`, `::init gtkb pb`, or a supported owner-facing
init phrase activates the startup disclosure relay.

## Constraint

When the first owner prompt in a fresh interactive GT-KB session matches the
init-keyword contract, the harness response for that turn MUST render the
cached user-visible startup disclosure to the owner before any startup action.

For Prime Builder and non-LO relay paths, the response then stops and waits for
the next owner message. For a successful LO relay, the relay clears
`startup_response_pending` with the auditable `lo_startup_relay` reason and
continues with the role-specific harness-only startup action in that turn:

- default LO verifies live bridge state, reports the scan, and processes
  actionable `NEW`/`REVISED` entries oldest-to-newest by default;
- advisory LO verifies and reports the live scan, then asks the owner whether
  to switch to auto-process, without processing entries or writing a verdict
  before that explicit switch.

The relay path MUST NOT satisfy the startup contract by emitting only hook
metadata, by setting lifecycle guard state, by returning a short acknowledgement
that the disclosure was emitted, or by attempting the LO action before the
disclosure is visible in the chat.

The cached startup disclosure used for interactive init-keyword relay MUST be
isolated from bridge auto-dispatch SessionStart payloads. A bridge auto-dispatch
SessionStart context MUST NOT overwrite, shadow, or replace the cache used by
the interactive startup-disclosure relay.

If the cached disclosure is unavailable, malformed, or displaced by a
non-disclosure payload, the harness MUST fail visibly with an actionable
startup-relay diagnostic. A relay failure MUST NOT clear
`startup_response_pending` or claim that disclosure was emitted.

## Required Behavior

1. A matching init keyword activates the disclosure-relay path.
2. The assistant-visible response includes the complete
   `## User-Visible Startup Message` content or its extracted user-visible
   startup disclosure.
3. A PB or non-LO relay response stops after the disclosure and waits for the
   next owner message. A successful LO relay proceeds only with the bounded
   role-specific startup action described above.
4. The LO relay clear occurs only after owner-visible disclosure success; it
   must be recorded as `lo_startup_relay`. Relay failure retains the normal
   pending protection.
5. Advisory LO must remain opt-in for auto-processing and verdict writing even
   though its live scan is allowed in the relay turn.
6. Interactive startup-disclosure cache files and bridge auto-dispatch cache
   files are separate, or otherwise protected by payload-type validation that
   rejects non-disclosure payloads for interactive relay.
7. Tests cover the failed-regression shape where hook state says disclosure was
   emitted but the visible assistant response contains only a short
   acknowledgement, the LO same-turn release, PB blocking, and advisory
   opt-in.

## Related Specifications

- GOV-SESSION-SELF-INITIALIZATION-001
- PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001
- DCL-STARTUP-GATE-FRESH-START-ONLY-001
- SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001
- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001

## Evidence

On 2026-05-14, owner prompt `::init gtkb lo` matched the init-keyword path and
the lifecycle guard recorded startup-disclosure pending state, but the visible
assistant response was only a short acknowledgement: "Startup disclosure has
been emitted." The generated SessionStart payload contained the full startup
disclosure, proving generation succeeded while owner-visible relay failed.

On 2026-07-11, the repaired owner-visible relay instructed default LO to
continue with its mandatory startup action, but the still-pending input gate
blocked the action's `gt` bridge read and governed verdict writer until an
extra owner message. This amendment makes the selected in-turn LO behavior
explicit while preserving PB waiting and advisory opt-in.

The same investigation found that `.codex/gtkb-hooks/last-session-start.json`
can contain bridge auto-dispatch SessionStart context, creating a cache-collision
risk for the interactive relay path when the relay reads that shared file as its
startup disclosure source.

## Test Expectations

Implementation work for this constraint should add or update tests equivalent
to:

- UserPromptSubmit init-keyword integration returns additional context
  containing the extracted user-visible startup disclosure.
- Assistant-facing startup relay instructions require rendering the disclosure
  and prohibit replacing it with a status acknowledgement.
- A successful default LO relay clears its pending gate with
  `lo_startup_relay` and permits live bridge-state and governed writer calls in
  the same turn.
- A PB relay retains the pending gate until owner input.
- An advisory LO relay allows the live scan but does not direct or perform
  auto-processing or verdict writing without a later owner switch.
- Bridge auto-dispatch SessionStart payloads do not populate the interactive
  startup-disclosure cache.
- If an interactive relay cache contains a non-disclosure SessionStart payload,
  the relay fails visibly and does not set satisfied startup-response state.

## Out Of Scope

This constraint does not redefine the canonical init-keyword syntax, durable
role assignment, bridge dispatch role-selection algorithm, or the general
startup-disclosure requirement. Those remain governed by the related
specifications listed above.
```

## Cross-Harness Disposition

The changed behavior belongs in the shared `scripts/workstream_focus.py`
module. Claude's `.claude/hooks/workstream-focus.py` and Codex's
`.codex/gtkb-hooks/workstream-focus.cmd` both delegate to that module, so no
wrapper or hook-registration change is proposed. The follow-on implementation
must run `python scripts/check_codex_hook_parity.py` and prove the same LO/PB
state transitions through the shared handler. No harness receives a behavior
waiver.

## Spec-Derived Verification Plan

| Specification | Review or future verification | Expected result |
| --- | --- | --- |
| `DCL-STARTUP-GATE-FRESH-START-ONLY-001` | Inspect the proposed text for an LO-only successful-relay release, PB wait, advisory opt-in, and auditable reason. | The current universal fresh-session wait is replaced by the bounded LO exception. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Inspect the proposed text for visible-disclosure-first ordering, PB stop, default-LO continuation, advisory scan-only behavior, and relay-failure retention. | No remaining universal relay-stop contradiction. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Inspect the default-LO action requirement and the planned live bridge-state verification. | The action is executed, not merely relayed. |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` | Inspect order and PB behavior. | Disclosure remains first; PB remains focus-gated. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Follow-on proposal runs `python scripts/check_codex_hook_parity.py`. | Shared handler behavior is parity-checked without wrapper drift. |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | Per-DCL formal-artifact packet validation after GO and before MemBase update. | Each exact DCL content hash validates against the live formal gate. |

## Acceptance Criteria

1. Loyal Opposition confirms the current DCLs conflict with the selected
   same-turn LO contract and that both proposed amendments resolve the conflict.
2. Loyal Opposition confirms that default LO can complete its mandated
   same-turn action without requiring a second owner message.
3. Loyal Opposition confirms PB stays focus-gated and advisory LO remains
   opt-in for processing and verdict writing.
4. No formal DCL mutation occurs until the exact content above has a valid
   formal-artifact approval packet and explicit owner approval.
5. The follow-on implementation proposal contains concrete `target_paths`, a
   fresh GO, an implementation-start packet, spec-derived tests, ruff gates,
   the startup/session suites, and `scripts/check_codex_hook_parity.py`.

## Risk / Rollback

Risk: clearing the LO pending state is broader than a read-only exemption and
therefore permits the LO harness to execute the specified startup sequence in
turn. Mitigation: the release is restricted to a successful fresh LO relay,
records `lo_startup_relay`, preserves PB pending state, and leaves advisory
auto-processing/writing subject to the already-rendered opt-in instructions.

Risk: the formal wording could weaken relay failure handling. Mitigation: both
amendments state that failure never clears the pending gate.

Rollback: this review itself is non-mutating. Before source implementation,
the formal DCL updates can be withheld. After any later implementation, rollback
restores the prior DCL versions and removes the LO-only clear branch through a
new reviewed bridge change.

## Bridge Filing

Before filing, run:

```powershell
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5186-lo-startup-gate-dcl-reconciliation-001.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5186-lo-startup-gate-dcl-reconciliation-001.md
```

## Recommended Commit Type

`docs:` for the later formal-spec-only amendment. The follow-on runtime repair
will recommend `fix:`.
