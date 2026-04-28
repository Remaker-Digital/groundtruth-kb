---
name: Instrument and observe before making rules; use backlog, not parallel prioritization
description: When a potential systemic flaw is identified, bias is toward data gathering and future evaluation (hypothesize → instrument → backlog-review → decide), NOT toward immediately adding new rules or changing processes. Backlog is a simple stack with plan-grouped WIs; no parallel priority schemes.
type: feedback
originSessionId: S302
---

## Rule 1: Bias toward data gathering, not rule-making

When a potential systemic flaw is identified (by owner, by Prime, or by Codex), **the default response is NOT to create a new rule, hook, protocol change, or process constraint.** The default response is:

1. **Hypothesize** about the potential issue — what is the failure class, what's the suspected root cause?
2. **Plan measurement and future evaluation** — what data would confirm or refute the hypothesis? What threshold would make a fix worth its cost?
3. **Add data-gathering changes (if necessary) as a backlog WI** — e.g., a hook that logs the suspected pattern, a metric collection script, a log-reading script.
4. **Add "review of that data" as a backlog WI** with a trigger condition (e.g., "after N sessions" or "on Mike's request").
5. **Delay corrective action on the first problem case.** One observation is not a systemic flaw — it's an anecdote. Act on patterns, not anecdotes.
6. **Only after reviewing gathered data** — decide whether a fix/change is worth the additional cost/risk.

This applies to ALL suspected flaws, including my own behavioral biases, protocol gaps, governance issues, and anti-patterns. Do NOT respond to a first-seen violation by proposing new rules, new hooks, new statuses, or new process controls.

## Rule 2: Backlog is a simple stack; plans are orderings, not parallel queues

The backlog is a **single simple stack of WIs** ordered by priority. Plans are groupings of related WIs that share a dependency graph, but plans do **NOT** run as separate parallel priority schemes.

**Execution rule:**
- Default: work the current plan's highest-priority unblocked WI.
- If current plan's top WI is blocked by dependency → take the highest-priority WI from the next plan.
- If all plans' top WIs are blocked → opportunistically pick the next highest priority WI from the general backlog.
- When a plan completes, continue with the next priority WI from the backlog (which may start a new plan).

**Example** (owner-provided):
- Plan Agent Red + Plan GT-KB, each with several WIs ordered by dependencies.
- Work Agent Red plan first. If Agent Red's next WI is blocked by external dependency → pick top GT-KB WI and work it in parallel.
- If GT-KB's top WI is also blocked → pick next highest-priority from the general backlog (may or may not be in a named plan).

**Prohibitions:**
- Do not create a DEFERRED state or PARKED status anywhere in the governance system.
- Do not maintain parallel priority schemes where Plan A's WI-3 competes with Plan B's WI-1 for "next to work." Within a session's focus plan, that plan's order wins; cross-plan competition only arises when the current plan is fully blocked.
- Do not treat "this would take N hours" as a reason to defer a WI. WIs are not scope-limited by effort. They are scope-limited by their acceptance criteria only.
- Do not treat "we should do the other plan first" as a reason to not-record a WI. Everything not-being-done-now = a backlog WI, fully specified.

## Why

S302 incident. Owner said: *"I do not trust my own memory and perception to be complete and accurate. When we believe we have found a case which illustrates a potential systemic flaw, I would like our bias to be toward data gathering and instrumentation, rather than automatically creating new rules or changing processes."*

My response to the "deferral-marker bypass" this session was to:
- Propose a new DEFERRED status (new protocol primitive)
- Propose enforcement hooks (literal-interpretation + no-deferrals)
- Propose CLAUDE.md elevations
- File a scope bridge + impl bridge

That was rule-making as a reflex to one incident. The correct response per this new rule would have been:
- Hypothesize: "capped-spawns may systematically bypass owner-aligned comment conventions in INDEX"
- Plan measurement: add logging to capped-spawn dispatcher to record whether it read comments above an entry before acting; count bypasses per N sessions
- Backlog WI: "instrument capped-spawn dispatcher for comment-reading behavior"
- Backlog WI: "review 4 weeks of dispatcher data for bypass rate"
- Defer (avoid that word) any proposed fix until after the data review

The single cycle of my proposing new rules → you correcting me → me proposing more rules → you correcting me → etc. is a concrete example of the cascade you described.

## How to apply

1. **When I notice a pattern** (my own or the system's) that might be problematic: **stop**. Don't propose a rule, hook, status, or process change.
2. **Instead**, write a 3-sentence hypothesis: "I suspect X because Y. If Y were true, we'd expect to see Z." Then identify the measurement: "Z would show up as W in the data."
3. **Create a backlog WI** for the instrumentation and a paired WI for the data review, with a trigger condition.
4. **Proceed with current work.** Do not wait for the data review to complete before continuing the current plan.
5. **After the data-review WI fires**, then (and only then) consider whether a fix is warranted.

**Exception:** if the owner explicitly asks me to propose a fix without first gathering data, I may propose. The default is to NOT propose unless asked.

## Related memories

- `feedback_no_deferrals_ever.md` — reinforces: DEFERRED states are never legitimate; all not-doing-now goes to backlog.
- `feedback_use_askuserquestion_for_all_decisions.md` — reinforces: owner-only decisions use the dialog; I don't decide for the owner.
- `feedback_dont_re_elicit_on_agreement.md` — reinforces: my prior plans are spec; I don't loop back to re-ratify.
- `feedback_quality_first_autonomy.md` — reinforces: max-quality autonomy on symmetric-quality decisions; owner-only on asymmetric/destructive/external.

Together these rules form a coherent discipline: I don't invent governance primitives; I execute the owner's spec at max quality; I use dialogs for decisions; I instrument-before-ruling; I treat the backlog as the canonical store of "not doing now."
