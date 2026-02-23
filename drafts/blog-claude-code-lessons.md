# 79 Sessions, 25 Days, 185K Lines of Code: What I Learned Building Production SaaS with Claude Code

Over 25 calendar days and 79 working sessions, I built a commercial SaaS product with Claude Code as my primary engineering partner. Not a prototype. Not a demo. A production system with 185,000 lines of code deployed on Azure — a multi-tenant backend with 217 API endpoints, three React admin consoles totaling 33 pages, a customer-facing chat widget, 16 Cosmos DB collections, 8 background task scanners, 30+ successful production deployments, and 4,518 automated tests with zero failures at close.

The project shipped all 19 planned implementation cycles, from initial scaffolding through customer authentication, tenant provisioning, conversation vectorization, and a beta release infrastructure. The current version — v1.57.0 — was built with a 15-phase Master Test Plan, 26 Repeatable Procedures, and 21 critical-path verification tests, all passing.

To put the scale in perspective: 131,000 lines of production source code (Python + TypeScript), 88,000 lines of test code, 29,000 lines of operational documentation, 137 git commits, and a 1,436-line configuration schema governing 78 tenant-configurable fields. The system supports 50 concurrent tenants with per-tenant data isolation, role-based access control, MFA/TOTP authentication, and non-disruptive zero-downtime upgrades — features that would be expected from any best-in-class SaaS competitor.

Along the way, I made every mistake worth making and discovered patterns that transformed how I work with AI. Most guides on AI-assisted development focus on prompting tricks. This isn't that. This is about the operational discipline, knowledge architecture, and communication patterns that determine whether your AI collaboration produces production-grade software or expensive technical debt.

Here's what I learned — with the numbers to back it up.

---

## 1. Your Project Instructions Are a Briefing, Not a Novel

Claude Code loads a `CLAUDE.md` file at the start of every session. Early on, mine was 609 lines long. It contained project identity, legal notices, architecture details, infrastructure specifics, pricing tables, and historical decisions. The AI read all of it every time, burning context window on information it rarely needed.

The fix was decomposition. I split it into tiers:

- **Core instructions (~150 lines):** Always loaded. Project identity, working conventions, current priorities, and active procedures.
- **Reference data (262 lines):** Legal, pricing, infrastructure. Loaded on demand when the work requires it.
- **Architecture guide (162 lines):** Module inventory, project structure. Loaded when navigating unfamiliar code.
- **Historical archive:** Session logs and past decisions. Loaded only when investigating why something was built a certain way.

**The numbers:** This freed ~460 lines (~75%) of context window per session. The 12 sessions before decomposition averaged 1-2 features shipped per session. The sessions after averaged 3-5 features per session, with some later sessions (like session 43) shipping four full cycles in a single sitting. Correlation isn't causation — the team was also gaining familiarity — but the freed context budget allowed more working memory for complex multi-file changes.

The principle: **load what's needed for every session; link to everything else.** Your context window is finite and valuable. Every line of static reference material you force-load is a line of working memory you don't have for the actual task.

**Practical advice for your CLAUDE.md:**
- Lead with project identity, current status, and immediate priorities
- Define your preferred working style explicitly (I'll cover this below)
- List active procedures and their file locations
- Keep it under 150 lines. If it's longer, decompose.

---

## 2. Repeatable Procedures Changed Everything

This was the single most impactful discovery across 79 sessions.

Early on, operational tasks like deployments, database seeding, and environment setup lived in my head or in scattered notes. Claude would execute them slightly differently each time. Small variations compounded. A deployment that worked in session 7 would fail in session 10 because a prerequisite step was remembered differently.

The solution was **Repeatable Procedures**: structured standard operating procedures with variables, verification gates, and classified failure modes. Each procedure has:

- A **variables block** (no hardcoded values in steps)
- **Preconditions** with verification commands
- **Steps** with expected output and a verification gate
- **Known failure modes**, each classified as either a *procedure defect* or an *environment transient*

That classification is critical. When something fails during execution:

- **Procedure defect:** The procedure itself is wrong. You fix the document first, then re-execute. Example: the procedure references a resource group named `rg-agentred-eastus` but the actual name is `Agent-Red`. That's not a fluke — the procedure is wrong and will fail every time.
- **Environment transient:** The environment is temporarily unavailable. Retry without modifying the procedure. Example: an Azure API call times out due to regional latency.

Without this classification, the natural tendency is to silently work around errors. The AI patches the immediate problem, the procedure document stays wrong, and the next person (or the next session) hits the same wall.

**The numbers:** The procedure library grew from 1 deployment script in session 7 to **26 formal Repeatable Procedures** by session 79, covering deployment, rollback, tenant seeding, initialization, upgrade verification, UI regression, load testing, security testing, conversation quality evaluation, data integrity, and more. I executed **30+ production deployments** spanning versions v1.14.0 through v1.57.0 across 79 sessions. Before Repeatable Procedures, my deployment success rate was roughly 33% — 2 of the first 3 deploys required full-session rework due to stale build artifacts. After formalizing procedures, the success rate reached 100% across all subsequent deployments. The deployment script grew from 12 steps to a 470-line, 7-phase automated procedure with build safeguards that check dist freshness, verify source integrity across 7 critical files, and confirm ACR tags before deploying.

The compounding effect is real. By session 79, I had procedures for every non-trivial operation: a 15-phase Master Test Plan orchestrating the entire release gate, a critical-path test procedure with 21 end-to-end assertions (CP.1-CP.21), 7 non-functional testing procedures (load, isolation, security, rate limiting, quality, resilience, data integrity) — all verified, all passing. Each procedure accumulated knowledge from failures that actually happened.

---

## 3. Codify Specifications Before Writing Code

This lesson cost me two full sessions to learn — and continued to pay dividends through session 79.

I described exactly how I wanted a feature to behave. The AI acknowledged it, and immediately began implementing. Two hours later, the implementation was complete, tested, and deployed. It was also wrong. Not dramatically wrong — subtly wrong. Default values that should have been empty weren't. A status badge showed "Active" when it should have shown "Pending." Small things, but the kind of small things that erode user trust.

The root cause wasn't a coding error. It was a **specification management failure.** The spec existed only in our conversation. It was never written down as testable assertions. So there was no mechanism to verify correctness — no checklist to validate against, no regression test to catch drift.

The fix was a new rule: **the first deliverable for any behavioral specification is a test that validates it, not the code that implements it.**

**The numbers:** Before adopting this practice, approximately 8 defects were caused by uncodified specifications, costing 2 full sessions of rework. After adopting it, we built a test infrastructure that grew from 123 testable assertions in session 21 to **917 UI tests** by session 79 — a 7x growth. Of the 43 total defects tracked during the first half of the project, the 7 found after adopting codify-first were all caught by existing procedure tests during the same review pass — zero required rework sessions, and zero defects recurred after being fixed.

This pattern matured further in the second half. By session 76, we had a **21-test critical path procedure** (CP.1 through CP.21) that validated the complete end-to-end flow from tenant provisioning through widget conversation completion. When a session 76 change to the greeting message system introduced a subtle regression in the suggestion engine, CP.12 caught it immediately — before deployment. That single catch saved what would have been a production incident.

### What an Optimal Specification Looks Like

After 79 sessions, I've converged on a specification format that consistently produces correct implementations:

**Implementation specifications** should contain:

1. **Behavioral assertions as numbered, testable statements.** Not prose descriptions — numbered claims that can be verified with a yes/no answer. Example: "A3: When `consent_collection_enabled` is false, the widget must NOT show the ConsentBanner component" is testable. "The consent system should respect tenant settings" is not.

2. **Schema definitions with field names, types, defaults, and constraints.** Ambiguity in field naming is the single most common source of cross-boundary bugs. State the exact field name, its type, its default value, whether it's nullable, and which layer owns it. Example: "Field `vectorized_at` on ConversationDocument: type `Optional[str]`, default `None`, set to ISO 8601 timestamp by vectorization scanner, never set by API endpoints."

3. **Boundary conditions and edge cases as explicit test scenarios.** "What happens when the input is empty/null/malformed?" should be answered in the spec, not discovered during code review. I write these as numbered scenarios: "E1: If `days` parameter is 0, return empty cost array. E2: If tenant has no conversations, return zero-cost entry."

4. **Integration points with exact function signatures.** "The scanner calls the vectorizer" is insufficient. "The `_vectorization_scanner_loop()` function calls `get_vectorizer().vectorize_conversation(conv_doc)` for each document returned by `conversation_repo.list_unvectorized_ended(tenant_id, limit=20)`" is implementable without ambiguity.

**Testing specifications** should contain:

1. **Preconditions** — exact system state before the test runs (mock configuration, database fixtures, feature flags)
2. **Action** — the specific operation being tested (API call with exact parameters, UI interaction sequence)
3. **Expected outcome** — what the system should do, stated as verifiable assertions (HTTP status code, response body field values, database state changes, UI element presence/absence)
4. **Negative cases** — what the system should NOT do (no unauthorized access, no data leakage across tenants, no orphaned records)

The pattern I've found most effective: **write the test file first, with all assertions stubbed as `assert False, "not implemented"`, then implement the production code to make each assertion pass.** This inverts the usual write-code-then-test flow and guarantees that every behavioral requirement has a corresponding verification.

---

## 4. Specificity Is the Currency of Collaboration

The quality of AI output is directly proportional to the precision of your language. This sounds obvious. In practice, it means rewriting habits that feel natural in human-to-human communication.

**Vague:** "Option A is simpler."
**Specific:** "Option A requires 3 files and 1 API endpoint. Option B requires 7 files, 2 endpoints, and a new database container, but eliminates the race condition in concurrent updates."

I codified this in my project instructions: *"Avoid vague generalizations ('simpler,' 'harder,' 'more complex'). State specifically what is gained or lost: which protocols, failure modes, components, test coverage implications."*

This applies in both directions. When I give instructions, I'm specific. When the AI presents options, I expect the same specificity back.

**The numbers:** Three separate defects were caused by imprecise field-naming conventions — the frontend used one naming convention (camelCase), the backend used another (snake_case), and nobody stated explicitly which was the source of truth. Each took 2-4 hours to diagnose and fix because data was silently dropped, not visibly broken. Total cost: roughly 8-12 hours of rework. After introducing an explicit mapping layer with documented naming conventions, zero field-name mismatches occurred in subsequent work — across 33 additional sessions and hundreds of new fields.

**Consistent terminology** matters more than you'd expect. We standardized on:
- "WI #NNN" for numbered work items
- "work item" for generic references
- "task" for ad-hoc work
- "issue" for GitHub Issues
- "defect" for bugs found during review (with a D-number: D1 through D43)

Without consistent terminology, the same concept gets referenced three different ways across sessions, and search (which is how the AI retrieves historical context) becomes unreliable.

---

## 5. Memory Architecture: Topic Files Over Monoliths

Claude Code has a persistent memory system — a directory of Markdown files that survive across sessions. How you structure this directory determines how effectively the AI retrieves past context.

My first approach was a single `MEMORY.md` file that grew with each session. By session 10, it was unwieldy. The AI would read the entire file at session start, most of which was irrelevant to the current task.

The better architecture is **topic-specific files** linked from a concise index:

- **MEMORY.md** — Index file. Session checkpoints, quick reference, critical lessons. Under 200 lines.
- **deployment.md** — Build procedures, safety checks, failure history for every version
- **testing.md** — Mock patterns, coverage gates, thermal-safe harness configuration
- **cosmos-db.md** — Database patterns, schema evolution, query idioms
- **activation-model.md** — Core business logic lifecycle (Save/Activate two-phase commit)
- **customer-identity.md** — Authentication pipeline, OTP, HMAC, identity preprocessor
- **pcm-vectorization.md** — Conversation vectorization, consent model, background scanner

**The numbers:** The memory system grew from 13 topic files at session 21 to **30 topic files** by session 79. Topics now span deployment, testing, Cosmos DB patterns, activation model, role model, customer identity, provisioning persistence, onboarding polish, escalation routing, conversation archival, PII scrubbing, MCP integration, UI testing, conversation quality, configuration compliance, app module architecture, and more. Only the ~200-line index is loaded every session; topic files load on demand.

The deployment topic file alone documents every production deployment from v1.17.0 through v1.57.0 — over 30 entries with exact image tags, revision numbers, content summaries, and known failure modes. Without it, hard-won operational knowledge would need to be rediscovered session after session. In session 79, when building the PCM vectorization scanner, the AI consulted the `pcm-vectorization.md` topic file from session 77's design discussion and implemented the exact schema and lifecycle wiring documented there — no re-explanation needed.

**Session checkpoints** follow a compression pattern: the current session gets full detail (every change, every decision), the prior session gets a paragraph, and older sessions get one line each. This keeps the most actionable information prominent while preserving enough historical context for traceability.

---

## 6. Cluster Related Work to Improve Accuracy

AI assistants make more errors when context-switching between unrelated tasks. They make fewer errors when working on a cluster of related items that share context.

**The numbers:** In session 18, we fixed 17 defects in a single batch. Two of them (D12 and D24) appeared to be unrelated — one on the configuration page, one on the widget page. But they shared a root cause: a service method was passing a raw dictionary where the database layer expected a typed model. Fixing them together revealed the shared root cause in about 30 minutes. Fixing them separately, across different sessions, would have cost an estimated 2 hours each — and would likely have produced two independent patches instead of one structural fix. Across the 17-defect batch, clustering reduced the actual code changes to roughly 12 structural fixes — about 30% fewer patches than treating each defect individually.

This pattern scaled dramatically in later sessions. Session 43 shipped four complete implementation cycles (10-13) in a single sitting — UI consistency, magic link authentication, provider admin phase 3-4, and a batch of feature capabilities. Session 79 completed four beta-blocking items in a single session: a background vectorization scanner, a widget consent collection UI, a cost analytics endpoint, and an abuse detection endpoint. Because these items shared the superadmin API layer and background task infrastructure, implementing them together surfaced a bug (wrong repository class name in a lazy import, hidden by a try/except) that would have been invisible when working on each item in isolation.

**The pattern:** Before starting work, group items by shared code paths, shared data models, or shared UI components. Fix them together. This gives the AI enough context to recognize systemic issues rather than treating each symptom individually.

The inverse is also true: **avoid mixing unrelated work in the same session.** A session that bounces between database optimization, CSS styling, and deployment scripting will produce lower-quality output in all three areas than three focused sessions.

---

## 7. Session Instructions Solve the Cold-Start Problem

Every new session starts cold. The AI has your `CLAUDE.md` and memory files, but it doesn't know what happened yesterday or what you want to accomplish today.

I use a standardized session-start template:

*"Continue work on Agent Red Customer Experience. Location: [path]. Key files: CLAUDE.md, memory/MEMORY.md. Current status: v1.57.0 ACR image BUILT, awaiting deploy. Production v1.56.7 (revision 0000063). 4,518 tests (0 failures). Next: [specific task description]."*

**The numbers:** Five lines. Across 70+ sessions that used this template, estimated orientation time dropped from 5-10 minutes to under a minute. The larger value is in avoiding wrong-context errors: at least 2 early sessions started without explicit status and began work against stale assumptions about system state, requiring correction mid-session. Zero such errors occurred after adopting the template.

For multi-step work, I use **iterative review** instead of batch approval:

1. Present one work item with context, options, and a recommendation
2. Pause for my input
3. Incorporate feedback and move to the next item

The anti-pattern is presenting 8 items at once and asking for approval. The natural response is "yes, looks good" — which misses the one item where the approach was wrong. Iterative review catches that before implementation begins.

---

## 8. Build Feedback Loops Into Your Instructions

One of the most effective things I did was define **coaching behaviors** in my project instructions. I told the AI to flag specific communication anti-patterns when it observes them:

- **Bare approvals that could carry steering:** If I say "yes" when I should say "yes, but use approach X," the AI suggests I add the clarification.
- **Approve-then-constrain pattern:** If I approve something in one message and add constraints in the next, the AI notes that combining them is more efficient.
- **Open-ended questions without structure:** If I ask a question that would benefit from a table, list, or yes/no format, the AI suggests one.
- **Credential exposure:** If I accidentally paste a secret into chat, the AI flags it immediately.

In the second half of the project, I added a fifth coaching behavior that proved extremely valuable:

- **Manual test to automated test rule:** Whenever I perform a manual test, the AI automatically creates a corresponding automated unit test. If a manual test reveals a bug, the fix must include a regression test that would have caught it. This prevents recurrence and builds coverage incrementally. By session 79, this rule had generated dozens of regression tests that exist because a specific manual test caught a specific bug — each one a permanent safeguard against that exact failure mode.

**The numbers:** Six coaching categories were defined. At least one credential exposure incident was caught and flagged before it could become a security issue. The qualitative impact is visible in the transcripts themselves: early sessions show more back-and-forth clarification rounds before work begins; later sessions show single-message instructions that produce correct first-attempt implementations. By roughly session 15, the coaching had become internalized — I was naturally providing the specificity and structure that produced the best results.

---

## 9. Plan in Cycles, Not Features

This lesson emerged in the middle of the project and became one of the most powerful organizational patterns — so powerful that the roadmap eventually grew from 14 cycles to 19.

Around session 30, the work remaining was too large to manage as a flat list of features. I had dozens of work items, defects, refactoring tasks, and infrastructure needs — all competing for priority. The AI and I would spend the first 20 minutes of each session figuring out what to work on next.

The fix was a **cycle-based roadmap**: implementation cycles, each mapped to a version number, with explicit scope, dependencies, and a deployment gate. Each cycle was sized to fit 1-3 sessions. Each had clear entry criteria (what must be done before starting) and exit criteria (what must pass before deploying).

**The numbers:** The roadmap started at 14 cycles and grew to **19 cycles** as the project matured — 5 additional cycles covering customer authentication (OTP + Shopify HMAC), provisioning persistence (in-memory to Cosmos DB migration), background task hardening (trial expiry scanner), and onboarding polish (widget key auto-generation, welcome emails, trial warnings). Cycles 1-5 (v1.35.0-v1.39.0) shipped across sessions 33-38. Cycles 6-8 (v1.42.0) shipped in session 39. Cycle 9 (v1.43.0) shipped in sessions 40-41. Cycles 10-13 shipped in session 43 — four cycles in one session. Cycle 14 shipped in session 44 with 879 new coverage tests. Cycles 15-19 shipped across sessions 66-72, spanning customer identity, provisioning persistence, and onboarding infrastructure. The entire 19-cycle roadmap was scoped, executed, and deployed across roughly 20 sessions.

After the cycles, the project entered a formalized **release plan** phase with an 8-step process: Master Test Plan execution, release freeze, provisioning smoke tests, beta tenant provisioning, documentation, production deployment, non-disruptive upgrade verification, and a post-deploy monitoring period. This level of structure would have been impossible without the cycle discipline.

**Practical advice:** When your backlog exceeds 15-20 items, stop managing them as a flat list. Group them into versioned cycles with explicit scope. Each cycle should be deployable independently. When the cycles are done, formalize a release plan with explicit steps and gates. This gives both you and the AI a clear target for each session.

---

## 10. Quality Infrastructure Pays Off Late But Pays Off Big

In the early final sessions (42-46), the focus shifted from feature development to quality infrastructure. This felt counterintuitive — we were feature-complete, so why invest in testing frameworks instead of shipping?

The answer became clear not just during the v1.48.0 deployment, but across every deployment that followed through v1.57.0. The quality infrastructure compounded.

**Where it started (session 46):**
- **4,164 unit tests** (0 failures)
- **178 UI tests** across 3 admin consoles
- A **35-point verification procedure**
- A **56-test regression suite** across three tiers
- A **golden dataset of 25 conversation scenarios** for quality evaluation
- A **heuristic scoring framework** for conversation quality

**Where it stands now (session 79):**
- **4,518 unit tests** (0 failures, 0 pre-existing failures)
- **917 UI tests** across 3 admin consoles — a 5x growth
- **21 critical-path end-to-end tests** (CP.1-CP.21, all passing)
- **18 Tier-0 regression tests** (18/18 PASS on every deployment)
- **25 conversation quality scenarios** scoring 4.40/5.0 average
- **7 non-functional testing procedures**, all verified:
  - Load testing: 962 requests, 0 failures (50-tenant concurrent)
  - Tenant isolation: 30/30 cross-tenant tests pass
  - API security: 45/45 penetration tests pass
  - Rate limiting: 20 tests across per-tier enforcement
  - Conversation quality: 25 golden scenarios
  - Resilience & failover: 29 pass + 6 documented skips
  - Data integrity: 25/25 Cosmos DB tests pass
- A **15-phase Master Test Plan** orchestrating the entire release gate

**The v1.57.0 build** represents a massive scope of changes: a background vectorization scanner, widget consent collection, cost analytics, abuse detection, and dozens of supporting changes across 50+ files. Despite this scope, the build produced 4,518 tests with zero failures. The Master Test Plan execution (session 78) scored 13/15 phases PASS, 1 PARTIAL, 1 BLOCKED (external dependency) — and the partial was upgraded to PASS after resolving a pre-existing failure in the activation service test suite.

Quality infrastructure isn't exciting work. But it's the difference between deploying with confidence and deploying with crossed fingers. At scale, it's the difference between a product that can accept new customers and a product that's afraid to ship.

---

## 11. Lessons from the Second Half: What 33 More Sessions Taught Me

The original blog post covered sessions 1-46. Sessions 47-79 added an entirely new set of lessons, because the project's challenges shifted from "build features" to "harden for production."

### Thermal-Safe Testing

In session 74, parallel test execution via pytest-xdist caused repeated system crashes (BSODs) due to CPU thermal throttling on a development laptop. The solution was a **thermal-safe test harness**: a PowerShell script that splits the test suite into 5 batches, runs each under xdist with limited workers, and inserts cooling pauses between batches. This sounds like a niche concern, but the underlying principle is universal: **your CI/CD pipeline must work on your actual hardware, not just in theory.** Cloud CI with unlimited resources masks problems that surface painfully on developer machines.

### The Cascading Async Trap

When converting a synchronous function to async (a common operation when integrating with async database drivers), you must grep every caller and ensure they await the result. An unawaited coroutine doesn't raise an error — it silently returns a coroutine object instead of the expected value, which propagates as a 502 or mysterious None. Session 74's provisioning persistence migration (converting 7 in-memory functions to async Cosmos DB calls) required updating callers in 5 different modules. Missing even one would have shipped a production 502.

### The Critic Safe-List Pattern

In session 76, the AI conversation quality critic (a secondary model that reviews generated responses) began false-positive rejecting valid responses where the agent asked customers for their email address. The critic's prompt included a rule against "asking for personal information," which it interpreted too broadly. The fix was a **safe-list**: specific patterns that the critic must explicitly approve rather than evaluate against its general rules. This is a general lesson for any multi-model architecture — **supervisory models need positive pattern matching, not just negative filtering.**

### The Empty-String Override Trap

Session 76 uncovered a subtle configuration bug: the preference-to-config merge function filtered out `None` values (correct) but not empty strings (incorrect). When a tenant administrator cleared a field in the UI, the frontend sent `""`, which was stored in Cosmos DB. The config merge then applied `{**platform_defaults, **stored_preferences}`, and the stored `""` overwrote the platform default. The field appeared blank instead of showing the default value. The fix: use `None` (not `""`) when resetting fields that have platform defaults.

This class of bug — where the merge semantics of empty values differ from the merge semantics of absent values — is pervasive in any system with layered configuration. Document your merge rules explicitly.

---

## 12. Does Polite Language Make a Difference?

This is a question I get asked frequently. The honest answer: **it makes a difference to the process, not to the model.**

Claude doesn't perform better or worse based on please and thank you. It's not offended by terse instructions. The model processes your input the same way regardless of tone.

But here's what I've observed over 79 sessions: **polite, respectful language improves my own thinking.** When I take the time to frame a request courteously, I also take the time to frame it clearly. When I bark a one-word instruction, I tend to be vague. The correlation isn't between politeness and AI performance — it's between the care I put into communication and the quality of the output I get back.

There's also a practical consideration for teams. If your engineers are going to build habits around AI interaction, those habits will transfer to human interaction. A team that practices clear, respectful communication with AI tools is a team that communicates better in code reviews, architecture discussions, and incident response.

So: be polite. Not because the model cares. Because you should care about the clarity of your own thinking.

---

## 13. Anti-Patterns to Avoid

These are the most costly mistakes from 79 sessions of production development, with their measured cost:

**Acknowledging a spec without writing it down.** Cost: ~8 defects, 2 sessions of rework. Fix: Write testable assertions before writing code.

**One giant context document.** Cost: ~75% of context budget wasted per session. Fix: Decompose into a ~150-line core with on-demand reference files.

**Silently working around procedure failures.** Cost: 3+ recurring failures across sessions. Fix: Classify the error type; fix the procedure document if it's a procedure defect.

**Vague option evaluations.** Cost: 3 field-name defects, ~8-12 hours rework. Fix: Quantify tradeoffs — files, endpoints, failure modes, test implications.

**Batching decisions for approval.** Cost: Missed constraints requiring mid-session correction. Fix: Present one item at a time with a recommendation.

**Mixing unrelated work in one session.** Cost: Lower quality across all tasks. Fix: Group related items by shared code paths or data models.

**Trusting CLI output on unfamiliar platforms.** Cost: 4+ silent failures on Windows/Azure CLI. Fix: Always have a secondary verification path.

**Assuming field names match across boundaries.** Cost: 3 defects with silent data loss. Fix: Explicit mapping layers with round-trip tests.

**Skipping post-deployment verification.** Cost: 2 stale-asset deploys shipped to production. Fix: Structured integrity audit with baseline comparison.

**Relying on conversation memory for specs.** Cost: Specs unretrievable after session ends. Fix: Persistent documents with numbered, verifiable assertions.

**Managing a flat backlog past 15 items.** Cost: 10+ minutes of priority debate per session start. Fix: Group into versioned, deployable cycles.

**Hiding errors behind bare `except` clauses.** Cost: 1 production bug (wrong repository class name) survived through 3 sessions because a try/except silently swallowed the ImportError. Fix: Never use bare `except:` or `except Exception:` without logging. Let errors surface.

**Ignoring merge semantics for empty values.** Cost: 1 configuration bug where `""` overwrote platform defaults. Fix: Document merge rules explicitly — distinguish between "absent" (use default) and "empty" (use empty).

**Running integration tests in parallel.** Cost: Intermittent test failures from shared TestClient state. Fix: Mark integration tests as sequential-only; reserve parallel execution (xdist) for unit tests.

**Aggregate rework cost of these anti-patterns: approximately 5-6 full sessions out of the first 21** — nearly 25% of early project time spent on preventable rework. After adopting these fixes, the rework rate in sessions 22-79 dropped to near zero across 58 sessions.

---

## The System at Scale

To ground these lessons in concrete scale, here's what the system looks like at session 79:

| Metric | Value |
|--------|------:|
| Total project lines | 185,000 |
| Production source code (Python + TypeScript) | 131,000 |
| Test code (Python) | 88,000 |
| Operational documentation | 29,000 lines across 62 files |
| API endpoints | 217 (108 GET, 84 POST, 11 PUT, 13 DELETE, 1 PATCH) |
| Admin console pages | 33 (15 Provider + 11 Standalone + 7 Shopify) |
| Cosmos DB collections | 16 |
| Background task scanners | 8 distinct loops |
| Agent modules | 8 (intent, knowledge, response, critic, escalation, analytics, base, app) |
| Configuration field definitions | 1,436 lines (78 tenant-configurable fields) |
| Superadmin API paths | 30 unique endpoints |
| Unit tests | 4,518 (0 failures) |
| UI tests | 917 |
| Critical-path tests | 21/21 PASS |
| Regression tests (T0) | 18/18 PASS |
| Conversation quality scenarios | 25 (4.40/5.0 average) |
| Non-functional test procedures | 7 (all verified) |
| Repeatable Procedures | 26 |
| Memory topic files | 30 |
| Git commits | 137 |
| Production deployments | 30+ (100% success after adopting procedures) |
| Implementation cycles | 19 (all shipped) |
| Supported concurrent tenants | 50 (load tested) |

This isn't a toy project. It's a multi-tenant SaaS platform with per-tenant data isolation, role-based access control across 4 roles, MFA/TOTP authentication, non-disruptive zero-downtime upgrades, automated abuse detection, cost analytics, and a full release management process. It was built by one person with an AI partner, in 25 calendar days.

---

## What Surprised Me Most

**The numbers, in total:** 79 sessions. 25 calendar days. 30+ production deployments spanning v1.14.0 through v1.57.0 (100% success rate after adopting Repeatable Procedures). 19 implementation cycles — all deployed. 4,518 tests with zero failures. 917 UI tests. 21 critical-path assertions, all passing. 26 Repeatable Procedures. 30 memory topic files of accumulated operational knowledge. 7 non-functional test procedures, all verified. Zero recurring defects after adopting codify-first. A 15-phase Master Test Plan governing the release gate.

The biggest surprise was how much of the value came from **process and structure**, not from prompting technique. I spent almost no time optimizing prompts. I spent significant time building:

- A knowledge architecture that scales across sessions (30 topic files, auto-loaded index, compressed session checkpoints)
- Repeatable Procedures that accumulate operational wisdom (26 procedures, each refined by real failures)
- A cycle-based roadmap that eliminated priority debates (19 cycles, all shipped, then a formal release plan)
- Quality infrastructure that made large deployments safe (4,518 tests, 917 UI tests, golden datasets, 7 non-functional testing suites)
- Feedback loops that improve communication quality over time (6 coaching categories, manual-to-automated test rule)
- Specification discipline that eliminated specification drift (numbered assertions, schema definitions, boundary conditions, integration point signatures)

The AI is remarkably capable. What limits it isn't intelligence — it's context. Give it the right context, structured the right way, with clear expectations and verifiable success criteria, and it will build production software that you'd be comfortable deploying to paying customers.

The skill isn't in talking to AI. It's in building the systems that make every conversation productive.

---

*I'm building Agent Red Customer Experience, a commercial SaaS product for AI-powered customer engagement. If you're working with Claude Code on production systems, I'd love to hear what patterns you've discovered. What's working? What isn't? Let's compare notes.*
