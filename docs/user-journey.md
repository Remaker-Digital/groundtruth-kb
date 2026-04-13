# The User Journey

What does it actually look like to build a product with GroundTruth and
Claude Code? This walkthrough follows Sarah — a product owner with a vision
but no programming experience — from first install to production.

---

## The Scenario

Sarah has a product idea: a multi-tenant customer engagement platform. She has:

- A 3-page written description of what she wants to build
- Screenshots from competitor products
- Mockups of her envisioned UI
- A budget, a timeline, and a target market

She doesn't write code. Claude Code does that. GroundTruth makes sure the
code matches what Sarah actually asked for.

---

## Phase 0: Setup and Installation

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Command line | Basic | Navigate directories, run commands. No scripting. |
| Git | Basic | `git init`, `git commit`. Conceptual version control. |
| Python | None | Runs `pip install` but doesn't write Python. |
| Editor | Basic | Open files, read markdown. |
| Claude Code | Awareness | It's her builder interface — natural language in, working code out. |

### The experience

```bash
pip install groundtruth-kb
mkdir my-engagement-platform && cd my-engagement-platform
git init
gt project init
```

GroundTruth asks a few questions:

- **Project name:** Engage
- **Profile:** `local-only` (solo developer, no reviewer agent yet)

The scaffold creates: `groundtruth.db`, `.claude/hooks/`, `CLAUDE.md`, `MEMORY.md`.

With the scaffold generator, Sarah also gets seed specifications:

```bash
gt scaffold specs --platform cloud --tenancy multi-tenant --auth mixed --frontend spa
```

This generates ~30 seed specifications covering governance rules,
infrastructure, security baselines, and frontend patterns. All are
`authority='inferred'` — templates Sarah will review, confirm, or discard.

### What Sarah does NOT need to know

How SQLite works, what the spec schema looks like, Python programming,
containers, or deployment.

---

## Phase 1: Requirement Capture

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Writing requirements | Moderate | Be clear: "The widget MUST support real-time messaging" beats "make it good." |
| Product thinking | Strong | Her market, her users, her differentiators. No tool replaces this. |
| AI interaction | Basic-moderate | Directives vs. exploration. "Specify that tenant isolation must prevent data leakage" is a directive. |

### The experience

```
Sarah: Here's my product description: [pastes 3 pages]
       I also have these mockups: [provides paths]
       
       The platform MUST support real-time messaging, AI-powered 
       response suggestions, and customer sentiment analysis.
       Authentication MUST use magic links for end-users and API 
       keys for tenant administrators.
```

The intake pipeline detects specification language ("MUST support",
"MUST use") and begins structured capture:

```
Claude: I've identified 4 requirement candidates:

1. "Multi-tenant platform with embedded widget"
   → Classification: directive (high confidence)
   → Proposed section: Architecture / Multi-tenancy

2. "Real-time messaging support"
   → Classification: directive (high confidence)
   → Proposed section: Features / Messaging

3. "AI-powered response suggestions"
   → Classification: directive (moderate confidence)
   → Proposed section: Features / AI Components

4. "Magic link auth for end-users, API keys for admins"
   → Classification: directive (high confidence)
   → Proposed section: Security / Authentication

Would you like me to create specifications for these?
```

For mockups and screenshots, Claude extracts UI patterns and proposes specs:

```
Claude: From your mockup "chat-widget-v1.png", I can see:
- Floating button trigger in the bottom-right corner
- Chat panel with message bubbles, typing indicators, agent avatars
- Header bar with tenant branding (logo + color)

Shall I create UI specifications for these elements?
```

### What Sarah IS doing (irreplaceable contributions)

- **Product decisions:** "Real-time messaging yes, video calls no — out of scope for v1."
- **Priority calls:** "Authentication is highest priority. Without it, nothing else matters."
- **Creative direction:** "The widget should feel premium, not generic."
- **Market knowledge:** "Competitors charge per-seat. We should charge per-conversation."

---

## Phase 2: Specification Refinement

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Quality reports | Basic | Gold tier = ready to build. Needs-work = needs more detail. |
| Decision-making | Strong | Claude asks questions. Sarah's answers ARE the specifications. |
| Trade-off awareness | Moderate | "WebSockets cost 30% more than polling. Proceed?" Sarah decides. |

### The experience

Claude runs quality scoring across all specs:

```
Claude: Quality assessment for your 34 specifications:

Gold (ready to build):     8 specs
Silver (mostly ready):    12 specs
Bronze (needs detail):     9 specs
Needs work:                5 specs

The 5 lowest-scoring specs need your input:
1. "Sentiment Analysis" — I need to know: what model? Real-time or batch?
2. "Horizontal Scaling" — what's your expected load? 100 tenants? 10,000?
```

Sarah answers. Each answer is captured as an owner decision. Claude tracks
provenance — which specs came from Sarah directly (`authority='stated'`),
which were derived by AI (`authority='inferred'`), and which are temporary
implementation choices (`authority='provisional'`).

### What Sarah IS doing

- Answering questions to fill gaps
- Confirming or rejecting inferred specs
- Making trade-off decisions
- Setting provisional deadlines ("Decide on the database by week 3")

---

## Phase 3: Architecture and Constraints

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Architecture concepts | Basic | "ADR = a decision about how the system is built." |
| Cloud concepts | Basic-moderate | High-level understanding: compute, database, cache. |
| Security concepts | Awareness | "Tenant isolation = one customer never sees another's data." |

### The experience

```
Claude: I'm proposing 6 architecture decisions:

ADR-001: Multi-tenant isolation via partition keys
  → Affects 14 specs across data access and API layers

ADR-002: WebSocket transport for real-time messaging
  → Affects 8 specs in the messaging feature

ADR-003: Widget deployed as embedded iframe with postMessage API
  → Strongest isolation, but slightly more complex for customers

Shall I proceed, or discuss alternatives?
```

Sarah reviews, asks questions, approves. Constraint propagation then links
each ADR to affected specs automatically. Machine-checkable constraints
(DCLs) are derived from each ADR.

### What Sarah IS doing

- Reviewing architecture decisions at a business level
- Understanding trade-offs: "Iframe is safer but harder to install — OK for our market?"
- Setting priorities: "Tenant isolation is non-negotiable."

---

## Phase 4: Implementation

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Claude Code interaction | Moderate | "Implement the auth system per specs." Review summaries, not code. |
| Testing concepts | Basic | "Tests verify code does what specs say." PASS or FAIL. |
| Git | Basic | Commit work, push to GitHub. Claude handles mechanics. |
| Running commands | Basic | `gt doctor`, `gt intake list`, commands Claude provides. |

### The experience

```
Sarah: Implement the authentication system. Start with magic links.

Claude: Working through auth specs in priority order...

SPEC-023 implementation complete.
- Created: src/auth/magic_link.py
- Created: tests/auth/test_magic_link.py (8 tests)
- Test results: 8/8 PASS

The magic link expires after 15 minutes and can only be used once.
Moving to SPEC-024...
```

Session health dashboard at end of each session:

```
Specs implemented this session: 4
Tests added: 32
Tests passing: 32/32
Assertion coverage: 67% → 74%
No alerts.
```

When Sarah changes requirements mid-build, impact analysis shows the blast
radius:

```
Sarah: Change magic link expiry to 5 minutes.

Claude: Impact analysis:
- 3 specs affected
- SPEC-024 has a test asserting 15-minute window
- SPEC-089 email template references "15 minutes"
- No constraint conflicts

Shall I update all three?
```

### What Sarah does NOT need to know

Programming in any language, database queries, API design, test frameworks,
containers, CI/CD pipeline configuration.

### What Sarah IS doing

- Directing priority: "Auth first, then messaging, then analytics"
- Reviewing results: "8/8 pass — good, move on"
- Making mid-course changes: "Change expiry to 5 minutes"
- Answering questions: "Rate-limit failed attempts? How many before lockout?"

---

## Honest Gaps

**Environment setup:** Sarah needs cloud credentials, API keys, connection
strings. Claude guides her, but she needs to create accounts, set up billing,
and navigate cloud portals. This requires moderate cloud knowledge or a
tutorial walkthrough.

**Local development:** Running the app locally requires commands Claude
provides, but error messages can be confusing. Basic comfort with terminal
output helps.

**Debugging production issues:** Claude diagnoses from logs, but Sarah needs
to understand "the API is returning 500 errors" at a basic level.

**Third-party integrations:** Shopify, Stripe, email providers — each has its
own dashboard. Sarah navigates these GUIs; Claude handles code integration.

**Visual design:** Claude implements UI from mockups, but can't replace a
designer's eye. Sarah needs mockups as inputs, or uses component libraries.

---

## Phase 5: Testing and Quality

### The experience

```
Sarah: How are we looking overall?

Claude: gt doctor output:
  Database schema: up to date
  Hooks: all present
  Assertion coverage: 81%

  Reconciliation found:
  - 2 orphaned specs (file targets deleted during refactor)
  - 1 near-duplicate pair (92% overlap)
  - 1 expired provisional (database decision was due week 3)

  The expired provisional needs your decision: promote to
  stated, or evaluate alternatives?
```

Sarah: "Promote. Merge the duplicates. Fix the orphans."

---

## Phase 6: Deployment and Release

### What Sarah needs to know

| Skill | Level | Details |
|-------|-------|---------|
| Cloud basics | Moderate | Needs a cloud account. Understands "compute" vs "database" vs "secrets." |
| CI/CD concepts | Basic | "Push triggers build." Claude configures the pipelines. |
| DNS / domains | Basic | Buy a domain, point it at the deployment. |
| Staging vs production | Important | "Staging = test. Production = customers. Never skip staging." |

### The experience

```
Claude: Pre-deployment checklist:
  247/247 tests passing
  Security scan: no critical findings
  Quality: 89% gold tier

  Before we deploy, you need:
  1. A cloud subscription (I'll guide you through setup)
  2. A domain name
  3. Staging environment provisioned
```

After staging verification:

```
Sarah: Deploy to production.

Claude: Governance requires your explicit approval.
  Type "deploy to production" to confirm.

Sarah: Deploy to production.
```

---

## Phase 7: Ongoing Operation

| Skill | When | Level |
|-------|------|-------|
| Monitoring | Daily | Basic — read dashboards. Claude interprets alerts. |
| Customer feedback | Ongoing | Strong — feed requests back through the intake pipeline. |
| Scaling decisions | As load grows | Moderate — Claude proposes, Sarah approves. |
| Security updates | Monthly | Basic — Claude runs Dependabot, Sarah approves. |
| Feature iteration | Ongoing | Same as Phase 1 — describe what you want, Claude builds it. |

---

## Summary

### Must have (non-negotiable)

- **Product vision and domain knowledge** — no AI replaces this
- **Decision-making ability** — every "should we..." question needs Sarah
- **Basic command line** — running commands Claude provides
- **Basic git** — committing and pushing code
- **Cloud account setup** — subscription, billing, portal navigation
- **Budget awareness** — infrastructure costs money

### Not required (Claude + GroundTruth handle these)

- Programming in any language
- Database design and queries
- API design and implementation
- Test writing
- Container orchestration
- CI/CD pipeline authoring
- Security implementation
- Performance optimization
- Dependency management
- Code review (Loyal Opposition handles this in dual-agent mode)

---

## How GroundTruth Features Map to Sarah's Journey

| ID | Feature | Role | Phase |
|----|---------|------|-------|
| F1 | Schema Enrichment | Tracks authority, testability, stability on every spec | 2 |
| F2 | Change Impact Analysis | Shows blast radius when requirements change | 3, 4 |
| F3 | Quality Gate | Scores spec quality, flags gaps to fill | 2, 5 |
| F4 | Constraint Propagation | Links architecture decisions to affected specs | 3 |
| F5 | Requirement Intake | Classifies natural language input as requirements | 1 |
| F6 | Scaffold Generator | Generates seed specs and project structure | 0 |
| F7 | Session Health Dashboard | Shows progress metrics at session boundaries | 4, 5 |
| F8 | Provenance Reconciliation | Catches orphans, duplicates, authority conflicts | 5 |

---

Ready to start? Follow the [Start Here](start-here.md) guide to install
GroundTruth and create your first project.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
