# A Day in the Life: Development with GroundTruth-KB

This document describes what a typical development day looks like when using
GroundTruth-KB to manage a software project. It is written for a senior
technologist evaluating whether GroundTruth-KB is a good fit for their team.

---

## What GroundTruth-KB Is

GroundTruth-KB is a **specification-first development system**. Instead of
writing code and hoping it matches requirements, you write requirements first
(as "specifications"), then write code to satisfy them, then verify that the
code actually does what the specifications say. The system tracks this entire
lifecycle in a local SQLite database — no cloud service required.

The system also coordinates two AI agents — a **Prime Builder** (who writes
code) and a **Loyal Opposition** (who reviews it) — through an asynchronous
file-based "bridge" protocol. The Loyal Opposition's job is to find problems
before they reach production.

**You are the decision maker.** The AI agents propose; you approve. Nothing
deploys, merges, or changes status without your explicit say-so.

---

## What a "Requirement Specification" Is

A specification is a short, verifiable statement about what your system must do:

> "Users can create tasks with a title and priority."

That's it. It's not a design document, not a user story with acceptance
criteria, not a Jira ticket. It's a **decision log entry** — a record that
you and the system agree on what "done" looks like for this behavior.

Each specification has:
- An **ID** (e.g., `SPEC-100`)
- A **status** (`specified` → `implemented` → `verified`)
- **Assertions** — machine-checkable rules that test whether the spec is true
- A **change history** — who changed it, when, and why (append-only, never deleted)

When you run `gt assert`, the system checks every assertion against the actual
codebase. If something fails, you know exactly which specification is broken
and who last changed it.

---

## Morning: Start Your Session

```bash
cd my-project
gt project doctor        # Check workstation health
```

Doctor verifies: Python version, Git, Claude Code, bridge health, database
integrity, file structure. If anything is wrong, it tells you what to fix.

Open Claude Code (your Prime Builder). It loads `CLAUDE.md` (project rules)
and `memory/MEMORY.md` (session state) automatically. It knows where you left
off yesterday.

If you're using dual-agent mode, the bridge poller is already running in the
background (set up once via OS scheduler). The Loyal Opposition (Codex) picks
up review work automatically every 3 minutes.

---

## Mid-Morning: Define What You're Building

Before writing code, write a specification:

```python
from groundtruth_kb import KnowledgeDB

db = KnowledgeDB()
db.insert_spec(
    "SPEC-201",
    "API returns 401 for requests without a valid token",
    status="specified",
    changed_by="mike-s1",
    change_reason="Security requirement from architecture review",
    description="Any endpoint that requires authentication must return HTTP 401 "
                "when the Authorization header is missing or contains an invalid token.",
)
```

Or use the CLI:

```bash
gt scaffold specs        # Interactive guided spec creation
```

Now tell Claude Code: "Implement SPEC-201." Claude reads the specification
from the database, writes the code, and creates tests. When it's done, it
updates the spec status to `implemented`.

---

## Afternoon: Review and Verify

If you're using dual-agent mode, the Loyal Opposition has been reviewing
Prime's work through the bridge. You'll see the review status in
`bridge/INDEX.md`:

```
Document: auth-middleware
GO: bridge/auth-middleware-004.md       ← Approved after 2 revisions
REVISED: bridge/auth-middleware-003.md
NO-GO: bridge/auth-middleware-002.md    ← LO found a problem
NEW: bridge/auth-middleware-001.md      ← Prime's original proposal
```

Each NO-GO includes specific evidence: what was wrong, what file and line,
what needs to change. This is not vague feedback — it's auditable.

Run assertions to verify everything:

```bash
gt assert
```

Output tells you exactly which specifications pass and which don't.

---

## End of Day: Check Your Position

```bash
gt project doctor        # Everything still healthy?
gt assert                # All specs passing?
```

Review the Knowledge Database through the web UI:

```bash
gt web                   # Opens localhost:8090
```

The dashboard shows: spec counts by status, recent changes, test coverage,
deliberation archive. You can see at a glance how much of your project is
specified, implemented, and verified.

---

## What About Cost?

GroundTruth-KB itself is free and open-source. The costs come from the AI
providers you choose to use with it:

**Claude Code (Prime Builder):**
- Uses your existing Anthropic subscription or API key
- Token usage scales with how much code you ask it to write
- A typical day of active development uses the equivalent of a few dollars
  in API tokens — not hundreds
- The bridge poller only dispatches work when there's something to do (it
  reads `bridge/INDEX.md` every 3 minutes and does nothing if the queue is
  empty), so idle time costs zero tokens

**Codex (Loyal Opposition):**
- Uses your OpenAI/Codex subscription
- Only runs when Prime posts a proposal to the bridge — it does not burn
  tokens continuously
- A typical review cycle (one proposal → one review) uses a few thousand
  tokens
- Budget control: you can set `maxItemsPerSpawn=1` in the poller
  configuration to limit how many items are processed per cycle

**If nobody is writing proposals, nobody is burning tokens.** The system is
event-driven, not polling-driven. The 3-minute poller checks for new work
but doesn't invoke the AI unless it finds something.

---

## Can I Use Different Tools for the Loyal Opposition?

Yes. The Loyal Opposition role is defined by a protocol (the file bridge),
not by a specific tool. Any AI agent that can:

1. Read markdown files from a `bridge/` directory
2. Analyze code and write a review
3. Write its review as a new markdown file
4. Update `bridge/INDEX.md` with the review status

...can serve as the Loyal Opposition. The default setup uses Codex because
it runs autonomously via scheduled tasks, but you could use:

- **Another Claude Code instance** (with a different session/config)
- **A custom script** that calls any LLM API
- **A human reviewer** who reads proposals and writes GO/NO-GO files manually

The bridge protocol is tool-agnostic. The file format is documented in
`.claude/rules/file-bridge-protocol.md` in any scaffolded project.

We recommend starting with Codex because it's battle-tested (hundreds of
review cycles in production use) and the automation is already built.

---

## Installable Components

Everything installs from a single package:

```bash
pip install groundtruth-kb
```

This gives you:

| Component | What it does | CLI command |
|-----------|-------------|-------------|
| Knowledge Database | SQLite store for specs, tests, work items, deliberations | `gt init`, `gt assert`, `gt web` |
| Project Scaffold | Generates project structure with all config files | `gt project init --profile ...` |
| Workstation Doctor | Validates your dev environment | `gt project doctor` |
| Specification Engine | Create, query, score, impact-analyze specs | `gt scaffold specs` |
| Deliberation Archive | Decision history with semantic search | `gt deliberations search "..."` |
| Bridge Protocol | File-based dual-agent coordination | Files in `bridge/` directory |
| CI Templates | GitHub Actions workflows (3 tiers) | Generated by `gt project init` |

**Additional setup (one-time, per workstation):**

- **Claude Code** — install from [claude.ai](https://claude.ai); this is your Prime Builder
- **Codex** — available through OpenAI; this is your Loyal Opposition (optional but recommended)
- **OS scheduler** — Windows Task Scheduler or macOS/Linux cron; runs the bridge pollers (documented in the tutorials)

---

## Getting Started

1. `pip install groundtruth-kb`
2. `gt project init my-project --profile dual-agent`
3. `cd my-project && gt project doctor`
4. Read [Your First Specification](tutorials/first-spec.md)
5. Read [Dual-Agent Setup](tutorials/dual-agent-setup.md)

Total time to a working project: **~15 minutes.**
