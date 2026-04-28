---
name: Prioritization is by dependency only; everything must ship before GA
description: Do not ask the owner to pick priority for feature/hygiene work; bridge correctness is P0, everything else is ordered strictly by dependency graph
type: feedback
originSessionId: 12953966-5fb1-486d-abf4-94fa82fdb93a
---
All work in Agent Red Customer Experience must be complete before GA release.
Priority is determined by one rule only: dependencies. There is no other basis for
ranking work. Do not ask the owner "should this be P0?" or "should we do X first or
Y first?" — those are not priority decisions the owner wants to make.

**Why:** S292 owner directive. When I surfaced two "pending priority decisions"
(Stream 2 elevation, Stream 3 schema constraint) at session end, the owner clarified
that priority questions should not come to them — dependency analysis is the answer.
The GA deadline makes this a solved question: everything gets done, the only open
question is order, and order is fixed by what must complete before what else can
start.

**How to apply:**

1. **Bridge correctness is always P0.** If the bridge is malfunctioning or any bridge
   infrastructure is compromised, drop everything else and fix it. No other work
   proceeds while the bridge is sick.

2. **For all other work, rank by dependency graph.** If work item A blocks work item
   B (B reads data A produces, B uses an interface A provides, B cannot be tested
   until A lands), then A comes first. If A and B are independent, either order is
   fine — pick the one with shorter expected completion or the one that unblocks
   more downstream work.

3. **Do not ask about priority.** Proposals and plans should lead with a dependency
   argument, not a P0/P1/P2 label. If a dependency can be proven either direction,
   state that and pick one.

4. **"Should we do X before GA?" is never a real question — yes, because everything
   ships before GA.** If the owner asks "do we need X for GA?" that's asking about
   *scope*, not priority; treat it as a scope question and answer on technical
   grounds.

5. **Technical "withdraw vs implement" calls are not priority decisions.** If a
   proposed work item has a technical reason not to proceed (breaks a legitimate
   existing workflow, duplicates a better alternative, contradicts an ADR), make
   the WITHDRAW call autonomously on those grounds. Do not escalate it as a priority
   question.

**What this changes in day-to-day work:**

- Session start: read the in-flight bridge state and the pre-GA backlog; pick the
  next unblocked item by dependency, not by subjective importance.
- Proposals: include a "Dependencies" section that says what must be done first and
  what this unblocks. Skip any "Priority: P0/P1/P2" framing.
- Blockers: escalate to the owner only when (a) the bridge is broken or (b) you
  genuinely cannot determine a dependency ordering from available evidence.
- Technical merit calls: make them autonomously. The S292 Stream 3 WITHDRAW
  recommendation was the correct autonomous action; escalating it as a "decision"
  was unnecessary noise.
