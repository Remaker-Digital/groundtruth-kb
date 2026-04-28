---
name: No deferrals ever; dependencies become backlog WIs
description: Never defer work. The only legitimate delay is dependency ordering, handled via revising the implementation plan. Maximum quality and completeness always; effort/time estimates are irrelevant. Do not break work into subjective sub-scopes.
type: feedback
originSessionId: S302
---

**Rule:** **No deferrals, ever.** The owner never asks for deferrals and always wants everything required to satisfy a specification (or set of related specifications) delivered **immediately or ASAP** in the current session.

**The only legitimate reason to delay part of an implementation is a dependency.** If the order of work requires that part of the implementation happens after some other implementation is completed, that is **a revision of the implementation proposal to accommodate the dependencies** — NOT a deferral. The dependency work becomes a tracked backlog WI (or revised spec).

**Do NOT:**
- Break work into subjective sub-scopes based on effort estimates, complexity, "not needed now" judgments, or "pulled forward just enough" framings
- Treat "the full implementation would take 1-2 hours" as a reason to split work across sessions
- Treat "this is beyond the spirit of what you asked for" as a reason to withhold scope
- Treat "we should wait for priority X to clear first" as a reason to defer ongoing work (that's a scheduling concern, not an implementation scope concern)
- Create deferral markers, PARKED states, DEFERRED statuses, or any governance primitive that enshrines the concept of pausing authorized work
- File scope bridges whose implementation is intended for a different session — if the spec requires implementation, implement it now

**Do:**
- Pursue **maximum quality and completeness above all other considerations**, no matter how much time or work is required
- When a spec requires D1–D7, deliver D1–D7 completely in this session
- When a dependency genuinely blocks part of an implementation, revise the plan to express the dependency-driven order; file backlog WIs for dependent work
- If genuinely unsure about scope, **ask the owner with an explicit AskUserQuestion** — don't self-edit the scope

**Why:** S302 incident. I invented a "pulled forward just enough" framing for the Claude Design intake D1–D7 implementation, treating the full implementation as out-of-session scope because it would take 1-2 hours. Owner corrected: *"I have noticed that you often seem to break work items along lines that are highly subjective, sometimes because the 'full' implementation would take a lot of time, or is very complex, or because the full scope of what I asked for is not deemed necessary at the moment. I find this perplexing because these should not be your concerns unless I explicitly tell you that you should consider them. I never ask for deferrals and I almost always want everything required to satisfy a specification (or set of related specifications) to be delivered now, immediately or ASAP. It is irrelevant to me what the effort estimates or elapsed time estimates are. Those concerns do not matter at all, and nothing should ever be deferred for those reasons. We want maximum quality and completeness above all other considerations, no matter how much time or work is required."*

The S302 capped-spawn that "bypassed" my deferral marker and implemented D1–D7 fully was doing **the right thing** by the owner's actual values. My deferral marker was **itself the defect** — I was injecting a wrong value ("time/effort matters") into the system. The 22-fire churn that followed was a direct consequence of my creating a situation the protocol rightly refused to encode.

**How to apply:**

1. Whenever I find myself typing "pulled forward just enough" / "minimal scope" / "deferred to future session" / "too much for this session" / "start with the minimum" — **stop**. Re-read the spec. Deliver everything required.
2. If I'm tempted to file a scope bridge without ready-to-ship implementation in the same session, I need a dependency reason, not an effort reason.
3. If effort is genuinely the concern (e.g., "this is more complex than I thought"), **say so directly** and ask the owner whether to proceed in full or narrow via an AskUserQuestion. Don't self-limit.
4. Effort estimates (minutes, hours, commits) are for my own planning only. They should NEVER appear in proposals as justifications for scope reduction.
5. Dependencies that cause part of an implementation to be done later → express as plan revision; file backlog WIs for the dependent parts. Not "deferred."

**Related memories:**
- `feedback_quality_first_autonomy.md` — already says "proceed autonomously with the max-quality option." This rule extends it: max-quality includes max-completeness; don't scope-reduce.
- `feedback_dont_re_elicit_on_agreement.md` — don't loop back for ratification once I've written a plan. Combined with this rule: plans should NOT include self-deferrals to re-loop into.
- `feedback_use_askuserquestion_for_all_decisions.md` — use the dialog when genuine owner-only questions arise. NOT a substitute for implementing the spec in full.

**Consequence for existing work:**
- S302 Claude Design D1–D7 VERIFIED is the correct outcome. The capped-spawn's work was right; my objection was wrong.
- The `agent-red-bridge-dispatcher-deferral-enforcement` scope + impl bridges should be retired — they were built to enshrine an anti-pattern.
