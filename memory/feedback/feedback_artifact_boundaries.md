---
name: Artifact storage boundaries
description: KB for project artifacts (specs/tests/ADRs), MEMORY.md for operational patterns only — never mix
type: feedback
---

Project details like specifications, tests, ADRs belong in the Knowledge Database. MEMORY.md is reserved for operational directives that define/implement working processes — these should be applicable to any project and reflect ways-of-working decisions.

**Why:** Owner directive S218. Project artifacts are versioned, queryable, and auditable in the KB. Operational patterns are session-bootstrap context. Mixing them creates drift and duplication.

**How to apply:** Before writing anything to MEMORY.md, ask: "Is this a project artifact or a working-process directive?" If project artifact → KB. If working process → MEMORY.md.
