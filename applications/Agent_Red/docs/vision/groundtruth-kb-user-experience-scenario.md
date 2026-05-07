# GroundTruth-KB User Experience Scenario

**Status:** Anchor reference document for all GT-KB documentation  
**Created:** 2026-04-13 (S287)  
**Author:** Mike (Owner) + Claude (Prime Builder)  
**Audience:** Product documentation, onboarding guides, marketing, investor materials  

> This document describes the complete user journey for a non-developer product
> owner building a SaaS product using GroundTruth-KB and Claude Code. It is the
> single most useful artifact for any potential user and should anchor all other
> documentation.

---

## The Scenario

**The user:** Sarah. She has a product idea — a multi-tenant customer engagement
platform (like Agent Red). She has:

- A 3-page written description of what she wants to build
- 6 screenshots from competitor products (Intercom, Drift, Zendesk)
- 4 Figma mockups of her envisioned UI
- A budget, a timeline, and a target market

---

## Phase 0: Setup and Installation

### What happens

Sarah needs to set up her development environment and install GroundTruth-KB.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Command line | Basic | Navigate directories, run commands (`pip install`, `git init`, `cd`). Doesn't need scripting — just execution. |
| Git | Basic | `git init`, `git commit`, `git push`. Conceptual understanding of version control. GT-KB manages the database; git manages the code. |
| Python | None yet | GT-KB installs as a pip package. Sarah runs `pip install groundtruth-kb` but doesn't write Python. |
| VS Code / editor | Basic | Open files, read markdown. Claude Code runs in terminal alongside the editor. |
| Claude Code | Awareness | Sarah needs to know that Claude Code is her primary builder interface — she talks to it in natural language and it writes code. She should understand it's an AI assistant, not a search engine. |
| Cloud / Azure | None yet | Not relevant at this stage. |

### The experience

```
Sarah: pip install groundtruth-kb
Sarah: mkdir my-engagement-platform && cd my-engagement-platform
Sarah: git init
Sarah: gt project init
```

GT-KB asks her a few questions:

- **Project name:** Engage (Sarah's product name)
- **Profile:** `local-only` (she's working solo for now, no Codex reviewer yet)

The scaffold creates her project structure: `groundtruth.db`, `.claude/hooks/`,
`CLAUDE.md`, `MEMORY.md`.

With F6 (Scaffold Generator), she also gets:

```
Sarah: gt scaffold specs --platform azure --tenancy multi-tenant --auth mixed --frontend spa --data-store cosmos
```

This generates ~30 seed specifications covering:

- Governance rules (GOV-01 through GOV-20 adapted for her project)
- Infrastructure specs for Azure + Cosmos + multi-tenant
- Security baseline specs for mixed auth
- Frontend SPA specs

These are all `authority='inferred'` — AI-generated templates, not Sarah's
requirements yet. They're a starting point she'll review and either confirm or
discard.

### What Sarah does NOT need to know

- How SQLite works internally
- What the spec schema looks like
- Python programming
- Docker, Kubernetes, or deployment
- How Claude Code works under the hood

---

## Phase 0.5: Daily Startup and Project Dashboard

### What happens

After the project exists, Sarah no longer starts each session from a blank prompt. GT-KB builds a current dashboard model and turns it into directly actionable choices in the AI/user chat stream.

The dashboard remains a reference surface; the chat stream is where Sarah chooses the new session's focus.

![Session startup focus choices](../assets/gtkb-dashboard/session-focus-options.png)

### The experience

Sarah starts a new Claude Code session and sees focus choices such as:

- Resolve release blockers
- Repair testing/tool integrations
- Remediate known risks
- Clear the stage/test release path
- Continue from the last session
- Clean for internal review
- Choose work from the standing backlog
- Use a custom focus

The labels, order, and prompt text are derived from the dashboard's current view of the project. If GitHub Actions is failing, tool repair rises. If production is blocked, release blockers rise. If the previous session ended midstream, continuation is available with the supporting evidence already summarized.

### Project dashboard

Sarah can open the dashboard when she wants a full visual overview. It shows Agent Red as the product/project and treats GT-KB as pre-existing implementation infrastructure used to build it.

![Agent Red project dashboard top section](../assets/gtkb-dashboard/dashboard-top.png)

The delivery timeline sits immediately below the heading block. Events run oldest to latest, left to right, with calendar dates visible so clustering and gaps are obvious.

![Delivery timeline](../assets/gtkb-dashboard/delivery-timeline.png)

### Corrective-action shortcuts

The dashboard also surfaces health, next actions, and failing tool integrations with suggested remediation.

![Dashboard action center](../assets/gtkb-dashboard/action-center.png)

![Testing service and tool integrations](../assets/gtkb-dashboard/testing-integrations.png)

### What Sarah does NOT need to know

- How the dashboard harvests commit/build/deployment evidence
- How GT-KB computes the ordering of startup focus choices
- How PDF export is generated
- How integration health probes are implemented

### What Sarah IS doing

- Choosing the next session focus from evidence-backed options
- Reviewing the dashboard when she wants full context
- Deciding whether a blocker, risk, integration failure, or backlog item should be addressed next
- Exporting a stakeholder PDF when she needs a distributable project-state report

---

## Phase 1: Requirement Capture

### What happens

Sarah feeds her written description, screenshots, and Figma mockups to Claude
Code. F5 (Requirement Intake Pipeline) classifies her input and captures
requirement candidates.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Writing requirements | Moderate | Sarah doesn't need to write formal specs, but she needs to be clear about what she wants. "The widget MUST support real-time messaging" is better than "make it good." |
| Product thinking | Strong | This is Sarah's primary contribution. She knows her market, her users, her differentiators. No tool replaces this. |
| AI interaction | Basic-moderate | Sarah needs to learn that Claude Code responds to direction, not just questions. "Specify that tenant isolation must prevent any data leakage between customers" is a directive. "What do you think about security?" is exploration. The intake classifier distinguishes these. |
| Image literacy | Basic | She needs to be able to point at her screenshots and mockups and explain what she wants: "This chat interface from Intercom — I want something like this, but with our branding and a different message threading model." |

### The experience

Sarah starts a Claude Code session:

```
Sarah: Continue work on Engage. 
       Here's my product description: [pastes 3 pages]
       I also have these mockups: [provides Figma export paths]
       
       The core idea: a multi-tenant customer engagement platform that 
       embeds as a widget on our customers' websites. Each customer (tenant) 
       gets their own branded chat experience. The platform MUST support 
       real-time messaging, AI-powered response suggestions, and customer 
       sentiment analysis. Authentication MUST use magic links for end-users 
       and API keys for tenant administrators.
```

F5's intake classifier detects specification language ("MUST support", "MUST
use") and begins structured capture:

```
Claude: I've identified 4 requirement candidates from your description:

1. "Multi-tenant customer engagement platform with embedded widget" 
   -> Classification: directive (high confidence)
   -> Proposed section: Architecture / Multi-tenancy
   
2. "Real-time messaging support"
   -> Classification: directive (high confidence)
   -> Proposed section: Features / Messaging

3. "AI-powered response suggestions"
   -> Classification: directive (moderate confidence)
   -> Proposed section: Features / AI Components

4. "Magic link auth for end-users, API keys for tenant admins"
   -> Classification: directive (high confidence)
   -> Proposed section: Security / Authentication

Would you like me to create specifications for these? I can also 
review the scaffold-generated specs against your description to 
identify overlaps and gaps.
```

Sarah confirms, and Claude creates specs. Each captured requirement becomes a
deliberation first (`outcome='deferred'`), then gets promoted to a spec on
confirmation (`outcome='owner_decision'`).

For the mockups and screenshots, Claude Code reads the images, extracts UI
patterns, and proposes specs:

```
Claude: From your Figma mockup "chat-widget-v1.png", I can see:
- A floating button trigger in the bottom-right corner
- A chat panel with message bubbles, typing indicators, and agent avatars
- A header bar with tenant branding (logo + color)

Shall I create UI specifications for these elements? They would 
include visual assertions that can be checked against the actual 
implementation later.
```

### What Sarah does NOT need to know

- SQL, Python, or any programming language
- How the deliberation storage works
- What `source_type='owner_conversation'` means
- How assertions work (yet)
- Anything about deployment or infrastructure

### What Sarah IS doing (her irreplaceable contributions)

- **Product decisions:** "Yes, real-time messaging, but NOT video calls — that's out of scope for v1."
- **Priority calls:** "Authentication is the highest priority. Without it, nothing else matters."
- **Creative direction:** "The widget should feel premium, not like a generic chat box. Think Apple-level polish."
- **Market knowledge:** "Our competitors all charge per-seat. We should charge per-active-conversation instead."

---

## Phase 2: Specification Refinement

### What happens

The initial specs are rough. Now Claude Code and Sarah iterate to make them
precise, testable, and complete. F1 (Schema Enrichment) and F3 (Quality Gate)
drive this process.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Reading spec quality reports | Basic | F3 produces scores. Sarah needs to understand "gold tier = ready to build, needs-work = needs more detail." She doesn't need to understand the 5 dimensions. |
| Decision-making | Strong | Claude will ask clarifying questions. Sarah must answer them: "Should tenant admins be able to customize the widget colors, or just the logo?" These decisions ARE the specifications. |
| Trade-off awareness | Moderate | Claude will surface trade-offs: "Real-time messaging requires WebSockets, which increases infrastructure cost by ~30% vs. polling. Proceed?" Sarah needs to make the call. |
| User stories | Helpful but not required | If Sarah can articulate "As a tenant admin, I want to see conversation analytics so I can measure team performance" — that's ideal. But Claude can derive user stories from her descriptions. |

### The experience

Claude runs F3 quality scoring across all specs:

```
Claude: Quality assessment for your 34 specifications:

Gold (ready to build):     8 specs  (governance, auth basics)
Silver (mostly ready):    12 specs  (messaging, widget core)
Bronze (needs detail):     9 specs  (analytics, AI features)
Needs work:                5 specs  (scaling, compliance)

The 5 lowest-scoring specs need your input:
1. SPEC-045 "Sentiment Analysis" - NO_ASSERTIONS flag. 
   I need to know: what sentiment model? Real-time or batch? 
   What accuracy threshold is acceptable?
   
2. SPEC-051 "Horizontal Scaling" - missing testability classification.
   I need to know: what's your expected load? 100 concurrent tenants? 
   10,000? This drives the entire architecture.
```

Sarah answers these questions, and Claude updates the specs. Each answer is
captured as an owner decision (archived as a deliberation via F5).

F1's authority field tracks provenance:

```
Claude: I've marked 12 specs as authority='stated' (your direct requirements),
18 as authority='inferred' (derived from your description + scaffold), 
and 4 as authority='provisional' (temporary implementation decisions 
that you'll revisit when we have more data).

For example: SPEC-062 "Use Cosmos DB for conversation storage" is 
provisional until we validate that Cosmos handles your expected 
message volume within budget. If not, we'll switch to Postgres.
```

### What Sarah does NOT need to know

- How F1 schema columns work
- What `_normalize_provisional()` does
- How quality scoring dimensions are weighted
- Any programming concepts

### What Sarah IS doing

- Answering questions to fill gaps
- Confirming or rejecting inferred specs
- Making trade-off decisions
- Setting provisional deadlines ("Let's decide on the database by week 3")

---

## Phase 3: Architecture and Constraints

### What happens

Before implementation begins, Claude proposes Architecture Decision Records
(ADRs) and Design Constraint Lists (DCLs). F4 (Constraint Propagation)
automatically links these to the specs they affect. F2 (Change Impact Analysis)
helps evaluate the blast radius of proposed changes.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Architecture concepts | Basic | Sarah needs to understand "ADR = a decision about how the system is built" and "DCL = a rule that all code must follow." She doesn't need to make these decisions — Claude proposes, Sarah approves. |
| Cloud concepts | Basic-moderate | Sarah should understand at a high level: "Azure Container Apps = where the code runs", "Cosmos DB = where data is stored", "Redis = fast temporary storage." She doesn't need to configure these. |
| Security concepts | Awareness | "Multi-tenant isolation means one customer can never see another customer's data." Sarah approves this as a constraint; Claude implements it. |

### The experience

```
Claude: Based on your specifications, I'm proposing 6 architecture decisions:

ADR-001: Multi-tenant isolation via partition keys (Cosmos DB)
  -> Affects 14 specs across data access and API layers
  -> Trade-off: simpler than database-per-tenant, but requires 
    careful query scoping at every data access point
    
ADR-002: WebSocket transport for real-time messaging
  -> Affects 8 specs in the messaging feature
  -> Trade-off: lower latency than polling, but requires sticky 
    sessions or a message broker for horizontal scaling

ADR-003: Widget deployed as embedded iframe with postMessage API
  -> Affects 11 specs in the widget and security domains
  -> Trade-off: strongest isolation (no CSS/JS leakage), but 
    slightly more complex integration for customers

Shall I proceed with these, or do you want to discuss alternatives?
```

Sarah reviews, asks questions ("What's the alternative to iframe?"), and
approves. F4 then runs:

```
Claude: Constraint propagation complete. ADR-001 (tenant isolation) 
has been linked to 14 specs. Each now carries affected_by=["ADR-001"] 
so we can trace which code must respect this constraint.

DCL-001: "All database queries MUST include tenant_id in the 
WHERE clause" - this is a machine-checkable constraint derived 
from ADR-001. It has a grep assertion that will FAIL if any 
query file doesn't filter by tenant_id.
```

### What Sarah does NOT need to know

- How `propagate_constraint()` works internally
- What `affected_by` JSON arrays look like
- How grep assertions match patterns
- Azure Container Apps configuration
- Cosmos DB partition key mechanics (Claude handles this)

### What Sarah IS doing

- Reviewing and approving architecture decisions
- Understanding trade-offs at a business level ("iframe is safer but slightly harder for customers to install — is that okay for our market?")
- Setting priorities ("Tenant isolation is non-negotiable. Performance optimization can come later.")

---

## Phase 4: Implementation

### What happens

Now Claude Code begins building. This is where the most transformation happens
relative to traditional development. Sarah is NOT coding — she's directing.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Claude Code interaction | Moderate | Sarah directs work sessions: "Implement the authentication system per the specs." She reviews what Claude produces. She doesn't write code, but she reads summaries of what was built. |
| Testing concepts | Basic | Sarah needs to understand "tests verify that the code does what the specs say." She doesn't write tests — Claude does (GOV-12: work item creation triggers test creation). She reviews test results: PASS or FAIL. |
| Git / version control | Basic | Sarah commits work, pushes to GitHub. Claude Code handles the mechanics, but Sarah approves commits. |
| Running commands | Basic | `gt doctor` (check project health), `gt intake list` (see pending requirements), basic npm/python commands that Claude tells her to run. |

### The experience

Sarah's workflow becomes cyclical:

```
Sarah: Let's implement the authentication system. Start with magic link 
       generation and verification.

Claude: I'll work through the auth specs in priority order:
        
        SPEC-023: Magic link generation endpoint
        SPEC-024: Magic link verification and session creation  
        SPEC-025: API key issuance for tenant admins
        SPEC-026: Session token refresh mechanism
        
        Starting with SPEC-023...
```

Claude writes code, creates tests, runs them. Sarah sees:

```
Claude: SPEC-023 implementation complete.
        - Created: src/auth/magic_link.py (generation logic)
        - Created: src/auth/routes.py (API endpoint)
        - Created: tests/auth/test_magic_link.py (8 tests)
        - Test results: 8/8 PASS
        
        The implementation sends a magic link via email using Azure 
        Communication Services. The link expires after 15 minutes 
        and can only be used once.
        
        Moving to SPEC-024...
```

F7 (Session Health Dashboard) runs at the end of each session:

```
Claude: Session health report:
        +----------------------------------+
        | Specs implemented this session: 4 |
        | Tests added: 32                   |
        | Tests passing: 32/32              |
        | Assertion coverage: 67% -> 74%    |
        | Quality: 12 gold, 15 silver       |
        | No alerts.                        |
        +----------------------------------+
```

F2 (Change Impact Analysis) surfaces when Sarah asks for changes mid-build:

```
Sarah: Actually, I want magic links to expire after 5 minutes, not 15.

Claude: Impact analysis for SPEC-023 change:
        - Blast radius: contained (3 specs affected)
        - SPEC-024 (verification) has a test asserting 15-minute window
        - SPEC-089 (email template) references "15 minutes" in copy
        - No constraint conflicts
        
        Shall I update all three?
```

### What Sarah does NOT need to know

- Python, JavaScript, TypeScript, or any language
- How Azure Communication Services APIs work
- Database query syntax
- Test framework mechanics (pytest, etc.)
- Docker, container orchestration
- CI/CD pipeline configuration

### What Sarah IS doing

- Directing priority: "Auth first, then messaging, then analytics"
- Reviewing results: "8/8 tests pass — good, move on"
- Making mid-course changes: "Actually, change the expiry to 5 minutes"
- Answering questions Claude asks: "Should failed magic link attempts be rate-limited? How many attempts before lockout?"

---

## Honest Gaps

### Where Sarah might need help

**Environment setup:** Sarah needs Azure credentials, API keys, database
connection strings. Claude can guide her, but she needs to create Azure
accounts, set up billing, and navigate the Azure portal. This requires moderate
cloud knowledge or a tutorial walkthrough.

**Local development:** Running the application locally requires `docker compose
up` or similar. Claude tells her the commands, but error messages can be
confusing. Sarah benefits from basic comfort with terminal output.

**Debugging production issues:** When something breaks in staging, Claude can
diagnose from logs, but Sarah needs to understand "the API is returning 500
errors" at a basic level to provide context.

**Third-party integrations:** Setting up Shopify apps, Stripe payments, email
providers — each has its own dashboard and configuration. Sarah navigates these
GUIs; Claude handles the code integration.

---

## Phase 5: Testing and Quality

### What happens

As implementation progresses, the test suite grows. F3 (Quality Gate) ensures
specs stay testable. F8 (Provenance Reconciliation) catches drift.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Test results | Basic | Green = good, red = broken. Sarah reads summaries, not stack traces. |
| Quality tiers | Basic | Gold/silver/bronze/needs-work. Sarah focuses on getting "needs-work" specs to at least bronze. |
| Acceptance criteria | Moderate | Sarah defines "done": "The chat widget must load in under 2 seconds on a 3G connection." Claude converts this to a testable spec. |

### The experience

```
Sarah: How are we looking overall?

Claude: gt doctor output:
        > Database schema: up to date
        > Hooks: all present
        > Assertion coverage: 81%
        
        Quality distribution:
        ##################-- 71% gold
        ####---------------- 18% silver  
        ##------------------ 8% bronze
        -------------------- 3% needs-work

        F8 reconciliation found:
        - 2 orphaned specs (file targets deleted during refactor)
        - 1 near-duplicate pair (SPEC-067 and SPEC-071 - 92% overlap)
        - 0 authority conflicts
        - 1 expired provisional (SPEC-062 - database decision was due week 3)
        
        The expired provisional needs your decision: Cosmos DB has 
        performed well in testing. Promote to stated, or evaluate 
        alternatives?
```

Sarah: "Promote Cosmos to stated. Merge the duplicate specs. Fix the orphans."

---

## Phase 6: Deployment and Release

### What happens

Code moves from local -> staging -> production. This is where Sarah needs the
most operational knowledge, though Claude handles most mechanics.

### What Sarah needs to know

| Skill area | Required level | What specifically |
|------------|---------------|-------------------|
| Cloud basics | Moderate | Sarah needs an Azure account with a subscription. She follows Claude's instructions to create resources, but understanding "container app" vs "database" vs "key vault" helps her make cost decisions. |
| CI/CD concepts | Basic | "GitHub Actions automatically builds and tests the code when I push." Sarah doesn't configure pipelines — Claude does — but she needs to understand that pushing code triggers automated checks. |
| DNS / domains | Basic | Sarah needs to buy a domain and point it at her deployment. Claude provides the steps. |
| Staging vs production | Important | Sarah must understand: "Staging is where we test. Production is where customers see it. Never skip staging." This is a governance rule (GOV-16). |

### The experience

```
Sarah: I think we're ready for our first deployment.

Claude: Pre-deployment checklist:
        > 247/247 tests passing
        > Security scan: no critical findings
        > Lint: clean
        > Quality: 89% gold tier
        x SPEC-062 (database) still provisional - resolved? 
        x No staging environment configured yet
        
        Before we deploy, you need:
        1. An Azure subscription (I'll guide you through setup)
        2. A domain name for your API and widget
        3. Staging environment provisioned
        
        Shall I walk you through Azure setup?
```

Claude guides Sarah through Azure portal setup, generates
infrastructure-as-code (Terraform or Bicep), and deploys to staging. Sarah tests
manually ("Visit staging.engage.app and try the widget"). Claude runs automated
tests against staging.

Once staging is verified:

```
Sarah: Deploy to production.

Claude: GOV-16 requires your explicit approval for production deployment.
        
        Production deployment will:
        - Deploy 8 containers to Azure Container Apps
        - Configure Cosmos DB with production throughput
        - Enable Redis caching
        - Set up the custom domain
        
        Estimated monthly cost: ~$180 at current scale.
        
        Type "deploy to production" to confirm.
        
Sarah: Deploy to production.
```

---

## Phase 7: Ongoing Operation

### What Sarah needs to know long-term

| Skill area | When it matters | Required level |
|------------|----------------|----------------|
| Monitoring | Daily | Basic — read dashboards. Claude interprets alerts. |
| Customer feedback | Ongoing | Strong — Sarah's core job. Feed customer requests back through F5 intake. |
| Scaling decisions | As load grows | Moderate — Claude proposes, Sarah approves. "Your database is at 80% capacity. Scale up ($50/mo more) or optimize queries first?" |
| Security updates | Monthly | Basic — Claude runs Dependabot, proposes updates, Sarah approves. |
| Feature iteration | Ongoing | Same as Phase 1 — Sarah describes what she wants, Claude builds it. |

---

## Summary: What Sarah Actually Needs

### Must have (non-negotiable)

- **Product vision and domain knowledge** — No AI replaces this
- **Decision-making ability** — Every "should we..." question needs Sarah's answer
- **Basic command line comfort** — Running commands Claude tells her to run
- **Basic git understanding** — Committing and pushing code
- **Cloud account setup** — Azure subscription, billing, basic portal navigation
- **Budget awareness** — Infrastructure costs money; Sarah makes cost trade-offs

### Helpful but learnable on the job

- Reading test output — Green/red, pass/fail
- Architecture trade-off intuition — Develops over time through Claude's explanations
- CI/CD awareness — "Push triggers build" mental model
- Staging/production discipline — Governance rules enforce this

### Not required (Claude handles these)

- Programming in any language
- Database design and queries
- API design and implementation
- Test writing
- Docker/Kubernetes configuration
- CI/CD pipeline authoring
- Security implementation
- Performance optimization
- Dependency management
- Code review (Codex handles this in dual-agent mode)

---

## The Honest Assessment

The 8 features we've designed make the "owner as spec provider" model
significantly more practical. F5 (intake) captures requirements from natural
language. F1 (schema enrichment) tracks authority and provenance. F3 (quality
gate) tells Sarah when specs need more detail. F6 (scaffold) gives her a running
start. F7 (health dashboard) shows progress. F8 (reconciliation) catches drift.

**The remaining gap is the operational layer** — Azure setup, DNS, SSL
certificates, environment variables, credential management. These are currently
guided-but-manual. A future phase could template this further (infrastructure
scaffold analogous to F6's spec scaffold), but today Sarah needs moderate cloud
literacy or a DevOps-savvy collaborator for the deployment phases.

**The other honest gap: visual design.** Claude Code can implement UI from
mockups, but it can't replace a designer's eye. Sarah's Figma mockups are
inputs, not outputs. If she doesn't have design skills, she needs a designer — or
she uses component libraries and accepts "good enough" aesthetics.

---

## GT-KB Features Referenced

| Feature | Role in Sarah's Journey | Phase |
|---------|------------------------|-------|
| F1: Schema Enrichment | Tracks `authority`, `testability`, `stability` on every spec | 2 |
| F2: Change Impact Analysis | Shows blast radius when Sarah changes requirements mid-build | 3, 4 |
| F3: Quality Gate | Scores spec quality, flags gaps Sarah needs to fill | 2, 5 |
| F4: Constraint Propagation | Links ADRs/DCLs to affected specs automatically | 3 |
| F5: Requirement Intake | Classifies Sarah's natural language input as requirements | 1 |
| F6: Scaffold Generator | Generates seed specs and project structure | 0 |
| F7: Session Health Dashboard | Shows progress metrics at session boundaries | 4, 5 |
| F8: Provenance Reconciliation | Catches orphaned specs, duplicates, authority conflicts | 5 |

---

*This document is the anchor reference for all GroundTruth-KB user documentation.*

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
