# 21 Sessions, 18 Days, 2,200 Tests: What I Learned Building Production Software with Claude Code

Over 18 calendar days and 21 working sessions, I built a commercial SaaS product with Claude Code as my primary engineering partner. Not a prototype. Not a demo. A production system deployed on Azure with a multi-tenant backend, a React admin dashboard, 11 successful production deployments, 43 tracked defects, and 2,200+ automated tests — all with zero test failures at close.

Along the way, I made every mistake worth making and discovered patterns that transformed how I work with AI. Most guides on AI-assisted development focus on prompting tricks. This isn't that. This is about the operational discipline, knowledge architecture, and communication patterns that determine whether your AI collaboration produces production-grade software or expensive technical debt.

Here's what I learned — with the numbers to back it up.

---

## 1. Your Project Instructions Are a Briefing, Not a Novel

Claude Code loads a `CLAUDE.md` file at the start of every session. Early on, mine was 609 lines long. It contained project identity, legal notices, architecture details, infrastructure specifics, pricing tables, and historical decisions. The AI read all of it every time, burning context window on information it rarely needed.

The fix was decomposition. I split it into tiers:

- **Core instructions (126 lines):** Always loaded. Project identity, working conventions, current priorities, and active procedures.
- **Reference data (262 lines):** Legal, pricing, infrastructure. Loaded on demand when the work requires it.
- **Architecture guide (162 lines):** Module inventory, project structure. Loaded when navigating unfamiliar code.
- **Historical archive:** Session logs and past decisions. Loaded only when investigating why something was built a certain way.

**The numbers:** This freed ~483 lines (~79%) of context window per session. The 12 sessions before decomposition averaged 1-2 features shipped per session. The 9 sessions after averaged 3-5 features per session. Correlation isn't causation — the team was also gaining familiarity — but the freed context budget allowed more working memory for complex multi-file changes.

The principle: **load what's needed for every session; link to everything else.** Your context window is finite and valuable. Every line of static reference material you force-load is a line of working memory you don't have for the actual task.

**Practical advice for your CLAUDE.md:**
- Lead with project identity, current status, and immediate priorities
- Define your preferred working style explicitly (I'll cover this below)
- List active procedures and their file locations
- Keep it under 150 lines. If it's longer, decompose.

---

## 2. Repeatable Procedures Changed Everything

This was the single most impactful discovery across 21 sessions.

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

**The numbers:** I executed 11 production deployments across 21 sessions. Before Repeatable Procedures, my deployment success rate was roughly 33% — 2 of the first 3 deploys required full-session rework due to stale build artifacts. After formalizing the procedure with 7 pre-flight safety checks (each added because something went wrong in a prior session), the success rate was 100% across the subsequent 8 deployments. The procedure grew from 12 steps to 28. It now documents 11 known failure modes. Every safeguard exists because it prevented a real failure from recurring.

---

## 3. Codify Specifications Before Writing Code

This lesson cost me two full sessions to learn.

I described exactly how I wanted a feature to behave. The AI acknowledged it, and immediately began implementing. Two hours later, the implementation was complete, tested, and deployed. It was also wrong. Not dramatically wrong — subtly wrong. Default values that should have been empty weren't. A status badge showed "Active" when it should have shown "Pending." Small things, but the kind of small things that erode user trust.

The root cause wasn't a coding error. It was a **specification management failure.** The spec existed only in our conversation. It was never written down as testable assertions. So there was no mechanism to verify correctness — no checklist to validate against, no regression test to catch drift.

The fix was a new rule: **the first deliverable for any behavioral specification is a test that validates it, not the code that implements it.**

**The numbers:** Before adopting this practice, approximately 8 defects were caused by uncodified specifications, costing 2 full sessions of rework. After adopting it, we built a test procedure with 123 testable assertions across 11 pages. Of the 43 total defects tracked during the project, the 7 found after adopting codify-first were all caught by existing procedure tests during the same review pass — zero required rework sessions, and zero defects recurred after being fixed. That's a 100% non-recurrence rate.

This pattern — codify, then code — eliminated an entire class of subtle-but-costly specification drift bugs.

---

## 4. Specificity Is the Currency of Collaboration

The quality of AI output is directly proportional to the precision of your language. This sounds obvious. In practice, it means rewriting habits that feel natural in human-to-human communication.

**Vague:** "Option A is simpler."
**Specific:** "Option A requires 3 files and 1 API endpoint. Option B requires 7 files, 2 endpoints, and a new database container, but eliminates the race condition in concurrent updates."

I codified this in my project instructions: *"Avoid vague generalizations ('simpler,' 'harder,' 'more complex'). State specifically what is gained or lost: which protocols, failure modes, components, test coverage implications."*

This applies in both directions. When I give instructions, I'm specific. When the AI presents options, I expect the same specificity back.

**The numbers:** Three separate defects were caused by imprecise field-naming conventions — the frontend used one naming convention (camelCase), the backend used another (snake_case), and nobody stated explicitly which was the source of truth. Each took 2-4 hours to diagnose and fix because data was silently dropped, not visibly broken. Total cost: roughly 8-12 hours of rework. After introducing an explicit mapping layer with documented naming conventions, zero field-name mismatches occurred in subsequent work.

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

- **MEMORY.md** — Index file. Session checkpoints, quick reference. Under 200 lines.
- **deployment.md** — Build procedures, safety checks, failure history
- **testing.md** — Mock patterns, coverage gates, known gotchas
- **cosmos-db.md** — Database patterns, schema evolution, query idioms
- **activation-model.md** — Core business logic lifecycle
- **ui-testing.md** — UI review procedure and defect tracking

**The numbers:** The memory system grew to 13 topic files containing ~1,200 lines of accumulated knowledge. Only the 188-line index is loaded every session; the remaining ~1,012 lines load on demand. The deployment topic file alone documents 11 known failure modes — without it, each would need to be rediscovered at a cost of roughly an hour each. That's an estimated 11 hours of avoided rework from a single topic file.

**Session checkpoints** follow a compression pattern: the current session gets full detail (every change, every decision), the prior session gets a paragraph, and older sessions get one line each. This keeps the most actionable information prominent while preserving enough historical context for traceability.

---

## 6. Cluster Related Work to Improve Accuracy

AI assistants make more errors when context-switching between unrelated tasks. They make fewer errors when working on a cluster of related items that share context.

**The numbers:** In session 18, we fixed 17 defects in a single batch. Two of them (D12 and D24) appeared to be unrelated — one on the configuration page, one on the widget page. But they shared a root cause: a service method was passing a raw dictionary where the database layer expected a typed model. Fixing them together revealed the shared root cause in about 30 minutes. Fixing them separately, across different sessions, would have cost an estimated 2 hours each — and would likely have produced two independent patches instead of one structural fix. Across the 17-defect batch, clustering reduced the actual code changes to roughly 12 structural fixes — about 30% fewer patches than treating each defect individually.

**The pattern:** Before starting work, group items by shared code paths, shared data models, or shared UI components. Fix them together. This gives the AI enough context to recognize systemic issues rather than treating each symptom individually.

The inverse is also true: **avoid mixing unrelated work in the same session.** A session that bounces between database optimization, CSS styling, and deployment scripting will produce lower-quality output in all three areas than three focused sessions.

---

## 7. Session Instructions Solve the Cold-Start Problem

Every new session starts cold. The AI has your `CLAUDE.md` and memory files, but it doesn't know what happened yesterday or what you want to accomplish today.

I use a standardized session-start template:

"Continue work on [project name]. Location: [path]. Key files: CLAUDE.md, memory/MEMORY.md. Current status: Production v1.30.3 HEALTHY. 2,217 tests (0 failures). Next: [specific task description]."

**The numbers:** Four lines. Across 15 sessions that used this template, estimated orientation time dropped from 5-10 minutes to under a minute — saving roughly 60-135 minutes total. The larger value is in avoiding wrong-context errors: at least 2 early sessions started without explicit status and began work against stale assumptions about system state, requiring correction mid-session.

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

**The numbers:** Six coaching categories were defined. At least one credential exposure incident was caught and flagged before it could become a security issue. The qualitative impact is visible in the transcripts themselves: early sessions show more back-and-forth clarification rounds before work begins; later sessions show single-message instructions that produce correct first-attempt implementations. By roughly session 15, the coaching had become internalized — I was naturally providing the specificity and structure that produced the best results.

---

## 9. Does Polite Language Make a Difference?

This is a question I get asked frequently. The honest answer: **it makes a difference to the process, not to the model.**

Claude doesn't perform better or worse based on please and thank you. It's not offended by terse instructions. The model processes your input the same way regardless of tone.

But here's what I've observed over 21 sessions: **polite, respectful language improves my own thinking.** When I take the time to frame a request courteously, I also take the time to frame it clearly. When I bark a one-word instruction, I tend to be vague. The correlation isn't between politeness and AI performance — it's between the care I put into communication and the quality of the output I get back.

There's also a practical consideration for teams. If your engineers are going to build habits around AI interaction, those habits will transfer to human interaction. A team that practices clear, respectful communication with AI tools is a team that communicates better in code reviews, architecture discussions, and incident response.

So: be polite. Not because the model cares. Because you should care about the clarity of your own thinking.

---

## 10. Anti-Patterns to Avoid

These are the most costly mistakes from 21 sessions of production development, with their measured cost:

**Acknowledging a spec without writing it down.** Cost: ~8 defects, 2 sessions of rework. Fix: Write testable assertions before writing code.

**One giant context document.** Cost: ~79% of context budget wasted per session. Fix: Decompose into a 126-line core with on-demand reference files.

**Silently working around procedure failures.** Cost: 3+ recurring failures across sessions. Fix: Classify the error type; fix the procedure document if it's a procedure defect.

**Vague option evaluations.** Cost: 3 field-name defects, ~8-12 hours rework. Fix: Quantify tradeoffs — files, endpoints, failure modes, test implications.

**Batching decisions for approval.** Cost: Missed constraints requiring mid-session correction. Fix: Present one item at a time with a recommendation.

**Mixing unrelated work in one session.** Cost: Lower quality across all tasks. Fix: Group related items by shared code paths or data models.

**Trusting CLI output on unfamiliar platforms.** Cost: 4+ silent failures on Windows/Azure CLI. Fix: Always have a secondary verification path.

**Assuming field names match across boundaries.** Cost: 3 defects with silent data loss. Fix: Explicit mapping layers with round-trip tests.

**Skipping post-deployment verification.** Cost: 2 stale-asset deploys shipped to production. Fix: Structured integrity audit with baseline comparison.

**Relying on conversation memory for specs.** Cost: Specs unretrievable after session ends. Fix: Persistent documents with numbered, verifiable assertions.

**Aggregate rework cost of these anti-patterns: approximately 5-6 full sessions out of 21** — nearly 25% of total project time spent on preventable rework.

---

## What Surprised Me Most

**The numbers, in total:** 21 sessions. 18 calendar days. 11 production deployments (100% success rate after adopting Repeatable Procedures). 43 defects tracked, 36 fixed, 7 deferred with documented reasons. 2,200+ tests with zero failures. 123 testable UI assertions. 13 memory topic files containing 1,200 lines of accumulated operational knowledge. Zero recurring defects after adopting codify-first.

The biggest surprise was how much of the value came from **process and structure**, not from prompting technique. I spent almost no time optimizing prompts. I spent significant time building:

- A knowledge architecture that scales across sessions
- Repeatable Procedures that accumulate operational wisdom
- Feedback loops that improve communication quality over time
- A specification management discipline that prevents drift

The AI is remarkably capable. What limits it isn't intelligence — it's context. Give it the right context, structured the right way, with clear expectations and verifiable success criteria, and it will build production software that you'd be comfortable deploying.

The skill isn't in talking to AI. It's in building the systems that make every conversation productive.

---

*I'm building Agent Red Customer Experience, a commercial SaaS product for AI-powered customer engagement. If you're working with Claude Code on production systems, I'd love to hear what patterns you've discovered. What's working? What isn't? Let's compare notes.*
