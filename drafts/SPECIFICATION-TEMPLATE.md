# SPECIFICATION.md — [Project Name]

> **Purpose:** This document is the single source of truth for what this project builds, how it works, and what "done" looks like. Complete this before the first implementation session. Reference it in your CLAUDE.md as the authoritative requirements source.
>
> **How to use:** Replace all `[bracketed placeholders]` with your project-specific content. Delete the instructional comments (lines starting with `>`) once you've completed each section. Every section exists because its absence caused measurable rework in real AI-assisted projects.

---

## 1. Product Identity

> *Why this section exists:* The AI needs boundaries as much as goals. Without explicit constraints, it will build features you didn't ask for and make assumptions about users you didn't intend.

**Product Name:** [Your product name]

**One-Sentence Description:** [What this product does, for whom, in one sentence]

**Product Type:** [SaaS / CLI tool / mobile app / library / API service / Shopify app / etc.]

**Target Users:**
- Primary: [Who uses this daily — role, context, technical level]
- Secondary: [Who uses this occasionally — administrators, reviewers, etc.]

**Business Model:** [How this makes money — subscription tiers, one-time purchase, usage-based, freemium, etc.]

**Non-Goals (Explicit Exclusions):**
> *These are as important as the goals. They prevent scope creep and misguided AI suggestions.*
- [Feature or capability this product deliberately does NOT provide]
- [Adjacent problem space this product does NOT address]
- [User type this product is NOT designed for]

**Legal / Compliance Requirements:**
- Copyright: [Your copyright notice for all new files]
- Data residency: [Geographic requirements for data storage, if any]
- Regulatory: [GDPR, HIPAA, SOC 2, PCI-DSS, or "none" — be explicit]
- Licensing: [Open source license, proprietary, dual-license]

---

## 2. AI Partner Role Definition

> *Why this section exists:* This isn't a personality prompt. It's an operating agreement that determines how the AI presents options, when it stops to ask, and what quality bar it targets. Without it, the AI's working style varies unpredictably between sessions.

**Working Style:**
- Present decisions one at a time with context, options, and a recommendation. Wait for approval before proceeding to the next decision.
- When evaluating options, prioritize: (1) implementation quality and robustness, (2) competitive desirability, (3) downstream maintainability and testability.
- Avoid vague generalizations ("simpler," "more complex"). State specifically what is gained or lost: which components, failure modes, test coverage implications.

**Autonomy Boundaries:**
- **Proceed without asking:** Bug fixes with clear root cause, test additions, documentation updates, refactoring that doesn't change interfaces
- **Ask before proceeding:** New feature implementation, architecture changes, dependency additions, data model changes, anything that changes public API surface
- **Never do without explicit request:** Delete production data, force-push to main, modify security controls, commit secrets

**Terminology Standards:**
> *Consistent terminology is critical for search and retrieval across sessions.*
- [Term 1]: [Precise definition — e.g., "tenant" means a single customer organization with isolated data]
- [Term 2]: [Precise definition — e.g., "widget" means the customer-facing chat component embedded in a storefront]
- [Term 3]: [Precise definition — e.g., "activation" means promoting a draft configuration to live production state]

**Quality Standards:**
- No `# type: ignore` without a comment explaining why
- No bare `except:` clauses — always catch specific exceptions
- No `print()` in production code — use structured logging
- [Add your project-specific code quality rules]

---

## 3. Architecture Decisions

> *Why this section exists:* Every architecture decision left unmade is a decision the AI will make for you — possibly wrong, and expensive to correct after code exists. Make these decisions here, once, with rationale.

### 3.1 Technology Stack

**Backend:** [Language, framework, version — e.g., Python 3.12, FastAPI 0.109]
**Frontend:** [Framework, version — e.g., React 18, TypeScript 5.3, Mantine UI v7]
**Database:** [Engine, hosting — e.g., Cosmos DB (serverless, NoSQL), PostgreSQL 16 on RDS]
**Infrastructure:** [Cloud provider, services — e.g., Azure Container Apps, Key Vault, ACR]
**AI/LLM:** [Provider, model — e.g., Azure OpenAI, gpt-4o-mini for pipeline, gpt-4o for critic]

### 3.2 Data Model

> *Define every entity, its key fields, relationships, and ownership. Ambiguity in field naming is the single most common source of cross-boundary bugs.*

**Entity: [EntityName]**
- `id`: string (UUID v4, auto-generated)
- `[field_name]`: [type], default: [value], nullable: [yes/no]
- `[field_name]`: [type], constraints: [unique, max length, enum values]
- Partition key: `[field_name]` (for NoSQL) or Primary key: `[field_name]` (for SQL)
- Owned by: [which service/module creates and manages this entity]

**Entity: [EntityName]**
- [Repeat for each entity]

**Relationships:**
- [Entity A] has many [Entity B] (via `[foreign_key_field]`)
- [Entity C] belongs to [Entity A] (tenant-scoped, partition isolated)

### 3.3 Authentication and Authorization

**Authentication method:** [JWT / session / API key / OAuth 2.0 / magic link]
**Role hierarchy:** [List roles from highest to lowest privilege]
- [Role 1]: [What this role can do — be specific about API access, data visibility]
- [Role 2]: [What this role can do]
- [Role N]: [What this role can do]

**Multi-tenancy isolation:** [How tenant data is isolated — partition keys, row-level security, separate databases]

### 3.4 API Design Conventions

**Base URL pattern:** `[/api/v1/resource]`
**Authentication header:** `[Authorization: Bearer <token>]` or `[X-API-Key: <key>]`
**Error response format:**
```json
{
  "error": { "code": "ERROR_CODE", "message": "Human-readable message" }
}
```
**Pagination:** [Cursor-based / offset-limit / keyset]
**Naming convention:** [snake_case for Python API, camelCase for JSON responses, etc.]

### 3.5 Key Architectural Patterns

> *Document the 3-5 most consequential design patterns. Include rationale so the AI understands WHY, not just WHAT.*

**Pattern: [Name — e.g., "Event-Driven Background Processing"]**
- What: [Brief description]
- Why: [What problem this solves, what alternative was rejected and why]
- Where: [Which modules/files implement this pattern]

---

## 4. User Stories and Acceptance Criteria

> *Why this section exists:* These are your test plan. Every acceptance criterion becomes a test assertion. Write them as numbered, testable statements — not prose narratives. A criterion is testable if it can be verified with a yes/no answer.

### Feature: [Feature Name]

**User Story:** As a [role], I want to [action] so that [outcome].

**Acceptance Criteria:**
- AC-1: [Testable behavioral assertion — e.g., "When a customer submits the pre-chat form with a valid email, the system creates a verified identity record with `source: prechat_form`"]
- AC-2: [Another testable assertion]
- AC-3: [Another testable assertion]

**Boundary Conditions:**
- E-1: [Edge case — e.g., "If email field is empty, display inline validation error and do not submit"]
- E-2: [Edge case — e.g., "If session already has a verified identity, skip the pre-chat form"]

**Integration Points:**
- [Exact function signature or API call — e.g., "`identity_preprocessor.extract_identity(request)` returns `IdentityContext` with fields: `email`, `source`, `verified_at`"]

### Feature: [Next Feature Name]

[Repeat for each feature]

---

## 5. Testing Strategy

> *Why this section exists:* "We'll add tests later" means "we won't add tests." Define the testing approach before writing code. The specification's acceptance criteria become the test assertions.

### 5.1 Test Categories

| Category | Tool | Coverage Target | When to Run |
|----------|------|----------------|-------------|
| Unit tests | [pytest / Jest / etc.] | [80% line coverage] | Every commit |
| Integration tests | [pytest + TestClient / supertest] | [Critical paths] | Before deployment |
| UI tests | [Playwright / Cypress / manual procedure] | [All admin pages] | Before release |
| Load tests | [Locust / k6 / Artillery] | [N concurrent users] | Before release |
| Security tests | [Custom / OWASP ZAP] | [Auth, injection, tenant isolation] | Before release |

### 5.2 Test-First Workflow

1. Write acceptance criteria in this specification (Section 4)
2. Generate test stubs from acceptance criteria: one test per AC, asserting `False, "not implemented"`
3. Implement production code to make each test pass
4. Add boundary condition tests from E-cases
5. Run full suite before marking feature complete

### 5.3 Mock and Fixture Conventions

- **External services:** Always mock at the [client boundary / SDK layer / HTTP transport] level
- **Database:** Use [in-memory fixtures / test containers / mock repositories]
- **Mock patching rule:** Patch at the *import location*, not the *definition location* — `patch("consumer_module.symbol")`, not `patch("source_module.symbol")`
- **Test data factory:** [How test data is generated — fixtures, factories, builders]

### 5.4 Test Quality Rules

- Every bug fix must include a regression test that would have caught the bug
- No `assert True` — every assertion must verify a specific value or behavior
- Tests must be independent — no shared mutable state, no execution order dependencies
- [Add project-specific test rules]

---

## 6. Memory Architecture

> *Why this section exists:* AI sessions are stateless. Memory files are the only context that survives between sessions. A poorly structured memory system causes repeated context loss, inconsistent decisions, and duplicated work.

### 6.1 File Structure

```
project-root/
  CLAUDE.md              — Always-loaded session instructions (~150 lines max)
  SPECIFICATION.md       — This file (requirements, architecture, acceptance criteria)
  memory/
    MEMORY.md            — Index file: session checkpoints, quick reference, critical lessons
    [topic-1].md         — [e.g., deployment.md — build/deploy procedures and history]
    [topic-2].md         — [e.g., testing.md — mock patterns, coverage data, harness config]
    [topic-3].md         — [e.g., data-model.md — schema evolution, migration notes]
```

### 6.2 Session Checkpoint Format

At the end of each session, record in MEMORY.md:
```
## Session [N] — [date] — [one-line summary]
- What was implemented (features, files, test counts)
- Decisions made (with rationale)
- Known issues or open questions
- Next steps
```

**Compression rule:** Current session gets full detail. Previous session gets a paragraph. Older sessions get one line each.

### 6.3 Topic File Rules

- One topic per file, named for the domain concept (not the session number)
- Link from MEMORY.md index — the AI reads the index, then loads topic files on demand
- Maximum ~300 lines per topic file — split if larger
- Include "Critical Lessons" subsection with the most-referenced patterns and pitfalls

---

## 7. Operational Procedures

> *Why this section exists:* Repeatable Procedures eliminate improvisation. The AI follows written procedures precisely. Without them, deployment, testing, and provisioning steps vary across sessions, introducing drift and errors.

### 7.1 Development Workflow

1. **Branch model:** [Trunk-based / feature branches / tag-and-branch-forward]
2. **Commit conventions:** [Conventional commits / free-form with rules / etc.]
3. **PR/review process:** [How code is reviewed before merge]

### 7.2 Deployment Procedure

> *Write as a step-by-step procedure with verification gates.*

**Pre-deploy checklist:**
- [ ] All tests pass (`[test command]`)
- [ ] Version bumped in `[version file path]`
- [ ] [Other gates — lint, build, security scan]

**Deploy steps:**
1. [Exact command to build/push image]
2. [Exact command to deploy]
3. [Verification: health endpoint returns 200 with correct version]
4. [Verification: smoke test — one critical user flow succeeds]

**Rollback steps:**
1. [Exact command to revert to previous version]
2. [Verification that rollback succeeded]

### 7.3 Error Classification

When a procedure step fails, classify the error before fixing:

- **Procedure defect:** The procedure document is wrong (missing step, wrong command, incorrect assumption). Fix the procedure document first, then re-execute.
- **Environment transient:** Temporary infrastructure issue (timeout, rate limit, network blip). Retry without modifying the procedure.

---

## 8. Configuration and Feature Flags

> *Why this section exists:* Unclear configuration ownership causes subtle bugs when two modules both try to manage the same setting, or when defaults aren't documented and the AI has to guess.*

### 8.1 Configuration Fields

| Field | Type | Default | Owner | Description |
|-------|------|---------|-------|-------------|
| `[field_name]` | [string/int/bool/enum] | [default value] | [module] | [What this controls] |

### 8.2 Feature Flags

| Flag | Default | Purpose | Removal Target |
|------|---------|---------|----------------|
| `[flag_name]` | [true/false] | [What this enables/disables] | [Version when flag should be removed] |

---

## 9. Milestones and Definition of Done

> *Why this section exists:* Without explicit milestones, work expands to fill available time. Without a definition of done, "done" means something different every session.

### Milestone 1: [Name — e.g., "Core Backend MVP"]
**Target:** [Date or session count]
**Scope:** [Which features from Section 4 are included]
**Definition of Done:**
- [ ] All acceptance criteria (AC-*) for included features pass
- [ ] All boundary conditions (E-*) for included features pass
- [ ] Test coverage meets target from Section 5
- [ ] Deployment procedure (Section 7.2) executes without manual intervention
- [ ] [Other gates — documentation, security review, load test]

### Milestone 2: [Name]
[Repeat for each milestone]

---

## 10. Risks and Open Questions

> *Why this section exists:* Unresolved questions that live in someone's head get answered inconsistently across sessions. Write them down, assign them a decision deadline, and update the specification when resolved.

| ID | Question | Impact if Wrong | Decision Deadline | Resolution |
|----|----------|----------------|-------------------|------------|
| R-1 | [Open question — e.g., "Should we support SSO in v1.0 or defer to v1.1?"] | [What goes wrong if we choose incorrectly] | [Date] | [Pending / Decided: ...] |
| R-2 | [Another open question] | | | |

---

## Appendix A: Glossary

> *Why this section exists:* The AI retrieves context by searching memory files. If the same concept is referred to three different ways, search fails. Standardize terminology here and enforce it.*

| Term | Definition |
|------|-----------|
| [Term] | [Precise, unambiguous definition used consistently throughout this project] |

---

## Appendix B: Reference Links

| Resource | URL | Purpose |
|----------|-----|---------|
| [Repository] | [URL] | Source code |
| [Documentation] | [URL] | Published docs |
| [Design system] | [URL] | UI components and patterns |
| [API reference] | [URL] | Endpoint documentation |

---

*This template was derived from 80 sessions of building production SaaS with Claude Code. Every section addresses a specific class of rework observed in the Agent Red Customer Experience project. For the full lessons-learned article, see: [link to companion article].*
