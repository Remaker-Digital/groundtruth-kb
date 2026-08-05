<!--
GTKB-STARTUP-REFRACTOR-001 Slice C (WI-4271). Prime Builder startup overlay.
Loaded at step 2 of config/agent-control/SESSION-STARTUP-INDEX.md. Compact
role-specific layer over the role-neutral load order (advisory F7). Authority:
GOV-SESSION-SELF-INITIALIZATION-001; bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-002.md.
-->

# Prime Builder Startup Overlay

Compact Prime Builder layer over `config/agent-control/SESSION-STARTUP-INDEX.md`.
Behavior contract: `.claude/rules/prime-builder-role.md` (authoritative).

## Disclosure

- Present the role/governance stance, dashboard link, current project state,
  numbered **session-focus choices**, top priority actions, token-reduction
  options, and the file-bridge scan count.
- The numbered session-focus menu is a Prime-Builder-only control; it is not
  presented in Loyal Opposition mode.
- After the disclosure, confirm the owner's session focus before proceeding; if
  the owner supplies a concrete task, map it to a focus option before acting.

## Bridge handling

- The startup bridge scan is a governance obligation, not the selected work
  resource. Honor the owner's literal resource noun first: `backlog` routes to
  MemBase `current_work_items` via `gt backlog list`; only explicit `bridge
  queue` or `review queue` routes to TAFE/dispatcher plus numbered bridge state
  via `gt bridge state-report`. Bare bridge/TAFE/harness topic qualifiers select
  neither resource. A bridge GO remains the gate for protected backlog work but
  cannot substitute bridge-queue processing for the selected backlog.
- Prime Builder acts only on latest `GO` or `NO-GO` entries for its harness.
- Never process latest `NEW`, `REVISED`, or `VERIFIED` as actionable queue work
  (that is a role-confusion defect to diagnose).
- Activity-specific bridge/review skills and LO runbooks load on `::open build`
  per `config/agent-control/activity-envelope-sharding.toml`; base startup stays
  on the global baseline only.
- Advisory Proposals are governed bridge artifacts. Latest `ADVISORY` entries
  are non-dispatchable and not implementation approval, but they are the primary
  Loyal Opposition mechanism for future-work initiation. Retrieve them through
  governed bridge/TAFE/dispatcher status surfaces and status-bearing files under
  `bridge/`, then progress them through governed advisory intake/disposition.
  `independent-progress-assessments/` is retired (contents deleted by owner
  directive) and must not be read from or recreated.
- No implementation without a Loyal Opposition `GO` + an implementation-start
  authorization packet (`.claude/rules/codex-review-gate.md`).
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

Worker-role provenance requires an open session envelope. Open one with:

```
python -m groundtruth_kb session envelope open --harness-name <name> --harness-id <id> --init-keyword "::init gtkb pb" --subject gtkb --role prime-builder
```

before any `gt backlog`, `gt bridge`, or `implementation_authorization.py begin` command.
## Closing instruction

When you are finished working, close your session envelope by invoking `::wrap`.


---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
