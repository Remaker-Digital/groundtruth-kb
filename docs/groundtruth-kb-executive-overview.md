# GroundTruth-KB: Specification-Driven Development for AI-Powered SaaS

**A system for building reliable, auditable software with AI — where every decision is recorded, every change is verified, and every deployment is earned.**

---

## The Problem

AI-assisted development is fast. It is also reckless. Today's AI coding tools can produce thousands of lines of code per day, but they produce them without memory, without verification, and without accountability. The result is software that works until it doesn't — and when it doesn't, nobody can explain why it was built that way in the first place.

Development teams using AI tools face a paradox: the more productive the tool, the more dangerous the output, because speed without structure compounds errors instead of eliminating them.

## The GroundTruth Approach

GroundTruth-KB is a development system — not just a tool — that solves this by making **specifications** the unit of work, not code. Every feature, every bugfix, every architectural decision starts as a verifiable specification: a recorded agreement about what the system must do. Code is written to satisfy specifications. Tests verify that the code matches. Nothing deploys until the specifications say it's ready.

This is not new in principle. What is new is that GroundTruth-KB makes it **practical with AI agents** — automating the tedious parts of specification tracking, test verification, and change auditing while keeping humans in control of every decision that matters.

---

## Core Ideas

### 1. MemBase: Persistent Project Memory

AI agents forget everything between sessions. GroundTruth-KB solves this with MemBase — a structured memory system that gives every session full context about what has been decided, what has been built, and what needs to happen next. This structure is codified in ADR-0001: Three-Tier Memory Architecture.

- **MemBase (knowledge database)** — SQLite-backed store of specifications, tests, work items, and deliberations, per ADR-0001: Three-Tier Memory Architecture. Every entry is append-only and versioned: you can see who changed what, when, and why.
- **Session Memory** — structured handoff files that tell the AI agent exactly where the project stands, what the current priorities are, and what lessons have been learned from previous sessions.
- **Deliberation Archive (DA)** — a searchable record of every significant design discussion, rejected alternative, and owner decision. When someone asks "why did we build it this way?", the answer is in the archive — not in someone's head.

### 2. Spec-First Development

The foundational rule: **before you write a line of code, write a specification.** A specification is not a design document or a Jira ticket. It is a short, verifiable statement about what the system must do:

> "API returns 401 for requests without a valid token."

Specifications have machine-checkable assertions. When you run `gt assert`, the system tests every assertion against the actual codebase and reports which specifications are satisfied and which are not. This transforms "does it work?" from a subjective question into a binary, auditable answer.

### 3. Test-Then-Implement

GroundTruth inverts the traditional development sequence. Instead of writing code and then writing tests to verify it, the system creates test expectations from specifications *before* implementation begins. The AI agent writes code to make the tests pass — not the other way around.

This matters because AI agents are excellent at generating code that satisfies well-defined constraints but poor at generating constraints from vague intentions. By front-loading the constraints (specifications + test expectations), GroundTruth channels the AI's productivity toward verified correctness.

### 4. Deterministic Procedures, Creative Analysis

Most software development work falls into two categories: **repeatable procedures** (build, test, deploy, format, lint, scan) and **creative work** (architecture, design, debugging, user experience). AI token costs become expensive when creative work is wasted on repeatable procedures.

GroundTruth makes every repeatable procedure deterministic and executable:

- **Governance gates** enforce rules mechanically (no deployment without tests passing, no spec promotion without owner approval)
- **Assertion checks** run on every session start — failing specifications are surfaced immediately, not discovered later
- **CI workflow templates** are generated from project profiles, running ruff and pytest by default; coverage, type-checking, and docstring gates are available in higher-tier templates and enabled when the project is ready
- **Bridge protocol** automates proposal/review cycles between agents on a 3-minute cadence

The result: AI tokens are concentrated on creative, insightful, and analytical work — the work that actually moves the project forward.

### 5. Dual-Agent Quality Assurance

GroundTruth-KB coordinates two AI agents with distinct roles:

- **Prime Builder** — writes code, creates specifications, implements features, proposes changes
- **Loyal Opposition** — reviews every proposal, checks evidence, finds problems before they reach production

They communicate through an asynchronous file-based bridge protocol. Prime proposes; the Loyal Opposition reviews and returns GO (approved), NO-GO (requires changes), or VERIFIED (post-implementation confirmed). Nothing proceeds without the Opposition's sign-off.

This is not a rubber stamp. In practice, proposals go through 2-5 revision cycles before approval. Each NO-GO includes specific evidence: what was wrong, which file, which line, what needs to change. The result is code that has been adversarially reviewed before any human sees it.

### 6. Deliberation Archive (DA): Organizational Memory

Every significant decision — accepted proposals, rejected alternatives, owner directives, design trade-offs — is automatically harvested into a searchable archive with semantic search capability. Before any agent proposes a change, it searches the archive for prior decisions on the same topic.

This prevents the most expensive failure in AI-assisted development: **re-debating settled questions.** When a new team member (human or AI) joins the project, the archive provides full context without requiring anyone to explain the project's history from scratch.

---

## Development Pipeline

GroundTruth-KB provides a structured pipeline from idea to production:

```
Specification → Work Item → Test Expectation → Implementation →
Assertion Check → Dual-Agent Review → CI Verification →
Staging Deploy → Production Deploy
```

Each stage has explicit entry and exit criteria. The system tracks which specifications are in which stage and reports progress through a web dashboard and CLI.

**CI templates are included in the project scaffolding:**

- Three template tiers (minimal, standard, full) generate GitHub Actions workflows running ruff and pytest by default
- The full-tier template includes optional configuration for `mypy`, per-file coverage thresholds, and docstring gates (off by default — enabled when the project's codebase is ready)
- Security scanning, accessibility testing, and visual regression (e.g., Semgrep, Bandit, axe-core, Playwright, Chromatic) are added by the team per their stack and requirements
- Architecture compliance assertions (`gt assert`) run on every session start via the included session hook

---

## Cloud Deployment Patterns

When a cloud provider is selected during project initialization, GroundTruth-KB generates Docker and Terraform starter stubs. These provide a version-controlled starting point — not a production-ready deployment configuration.

- **Docker** — a starter Dockerfile and Compose file are included; production configuration (secrets, health checks, multi-stage builds) is the team's responsibility
- **Terraform** — a provider stub with minimal variable and output scaffolding; resource configuration, secrets management, networking, and scaling are implemented by the team for their specific environment
- **Governance gate** — production deploys require explicit owner approval recorded in the specification system

Multi-tenant data isolation and zero-knowledge security are architectural patterns that teams implement for their use case — they are not pre-built features of the current v0.5.0 package.

---

## Technology Foundation

GroundTruth-KB is built on current-generation, industry-standard technology:

| Layer | Technology | Why |
|-------|-----------|-----|
| MemBase (knowledge database) | SQLite | Zero-infrastructure, portable, append-only versioning |
| AI Agents | Claude Code (Anthropic), Codex (OpenAI) | Best-of-breed for code generation and code review |
| Type Safety | Python 3.11+ with `mypy --strict` | Full static type coverage, zero errors |
| CI/CD | GitHub Actions | Industry standard, matrix testing across platforms |
| Cloud | Azure (starter scaffolding) | Docker templates and minimal Terraform provider stubs; teams add cloud resources for their environment |
| Web UI | FastAPI + Jinja2 | Built-in `gt serve` dashboard for spec tracking, assertions, and work items |
| Security | Credential detection built-in; CI placeholders for OWASP scanning tools | Teams configure Semgrep, Bandit, and accessibility tools per project |
| Search | ChromaDB (optional) | Semantic search over Deliberation Archive (DA) |

The entire system is open-source (AGPL-3.0), installable from PyPI (`pip install groundtruth-kb`), and designed for inspection by lead developers familiar with modern AI-assisted development practices.

---

## What Makes This Different

Most AI coding tools optimize for **speed of code generation.** GroundTruth-KB optimizes for **reliability of the finished product.** The distinction matters because:

- Speed without verification produces technical debt faster than it produces features
- AI agents without memory repeat mistakes across sessions
- Code without specifications cannot be audited, cannot be tested against requirements, and cannot survive team turnover
- Deployment without governance gates is one bad commit away from a production incident

GroundTruth-KB accepts a deliberate trade-off: development is slightly slower per-line than unstructured AI coding, but the output is **verified, auditable, and deployable with confidence.** For SaaS applications where reliability, security, and compliance matter, this trade-off pays for itself on the first avoided production incident.

---

## Getting Started

```bash
pip install groundtruth-kb
gt project init my-project --profile dual-agent-webapp --cloud-provider azure
cd my-project
gt project doctor
```

Four commands. Fifteen minutes to a working project with specifications, tests, dual-agent review, CI pipeline, and cloud deployment scaffolding.

---

*GroundTruth-KB is developed by Remaker Digital.*
*Available at [github.com/Remaker-Digital/groundtruth-kb](https://github.com/Remaker-Digital/groundtruth-kb)*
