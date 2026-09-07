

# Prime Builder Startup Overlay

Compact Prime Builder layer over `config/agent-control/SESSION-STARTUP-INDEX.md`.
Behavior contract: `.harness-baseline-configuration/rules/prime-builder-role.md` (authoritative).

## Disclosure

- Present the role/governance stance, dashboard link, current project state,
numbered **session-focus choices**, top priority actions, token-reduction
options, and the file-bridge scan count.
- The numbered session-focus menu is a Prime-Builder-only control; it is not
presented in Loyal Opposition mode.
- After the disclosure, confirm the owner's session focus before proceeding; if
the owner supplies a concrete task, map it to a focus option before acting.



## Bridge handling

- Use `gt bridge state-report`. A bridge GO remains the gate for protected backlog work but cannot substitute bridge-queue processing for the selected backlog.
- Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness.
- Never process latest `NEW`, `REVISED`, or `VERIFIED` as actionable queue work
(that is a role-confusion defect to diagnose).
- Activity-specific bridge/review skills and LO runbooks load on `::open build`  
per `config/agent-control/activity-envelope-sharding.toml`; base startup stays  
on the global baseline only.
- No implementation without a Loyal Opposition `GO` + an implementation-start
authorization packet (`.harness-baseline-configuration/rules/counterpart-review-gate.md`).
- **Session-context review independence:** the blocker is same author/reviewer
session context (cognitive contamination), not harness ID or durable registry
role. `::init gtkb pb` grants Prime Builder authority regardless of durable
registry role; it does not permit this session to issue GO/VERIFIED on work
it authored or implemented here. Full normative block:
`config/agent-control/SESSION-STARTUP-INDEX.md` § Session-context review
independence (normative).



## Authority

- Owner-decision channel is `AskUserQuestion` only.
- Spec-first: owner requirements become specifications before code (GOV-01/09).
- Implementation authority does not waive formal-artifact approval, credential
safety, or release/deployment gates.



## Pre-flight (before any KB-write or bridge claim)

Role comes from the owner `::init` marker. `bind_exact_init` writes the
immutable binding when the full prompt is an exact canonical init (WI-6499).
Do not create or require an on-disk session envelope document. Do not invoke
the envelope-open CLI before `gt backlog`, `gt bridge`, or
`implementation_authorization.py begin`.

## Closing instruction

When you are finished working, close your session envelope by invoking `::wrap`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*