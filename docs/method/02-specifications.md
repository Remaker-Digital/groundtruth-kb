# 2. Specifications

Specifications are the foundation of the GroundTruth method. They describe what the system must do, serving as a **decision log** — a record of what was agreed and why — rather than a build specification that dictates implementation details.

## What makes a good specification

A specification should be **as stable as the business need it captures**. If the business need changes rarely, the specification should change rarely. If a specification needs constant revision, it may be describing implementation rather than intent.

Good specifications:

- **State the requirement**, not the solution. "Users must be able to reset their password via email" — not "Add a POST /api/reset-password endpoint that sends a Mailgun email."
- **Are testable.** Someone must be able to determine, unambiguously, whether the specification is satisfied. "The system should be fast" is not testable. "API responses must return within 500ms at the 95th percentile" is.
- **Carry context.** Why does this requirement exist? What business problem does it solve? This context prevents future contributors from removing or weakening the requirement without understanding its purpose.
- **Are independent of the implementation.** A specification should survive a complete rewrite of the system. If rewriting the backend from Python to Go would invalidate the spec, it's too implementation-specific.

## Specification lifecycle

Every specification moves through a defined lifecycle:

```
specified → implemented → verified → retired
```

**Specified**: The requirement has been agreed upon and recorded. No implementation exists yet, or the implementation does not yet satisfy the spec.

**Implemented**: The code or configuration that satisfies this specification has been written. The team believes the requirement is met, but it has not been independently verified.

**Verified**: Tests linked to this specification pass, and the implementation has been reviewed. This is the highest confidence state — the spec is satisfied and proven.

**Retired**: The specification is no longer relevant. The business need has changed, or the feature has been removed. Retired specs are preserved in the database (append-only) but excluded from active dashboards and assertion checks.

### Promotion rules

Promotion is always forward: `specified → implemented → verified`. You cannot skip steps. Each promotion is a claim:

- "specified → implemented" claims: *the code now satisfies this requirement*
- "implemented → verified" claims: *tests prove the code satisfies this requirement*

Governance gates can enforce additional conditions at each transition. For example, architecture decision specs may require non-empty assertions before reaching "implemented" status.

## Specification types

GroundTruth recognizes five specification types:

| Type | ID prefix | Purpose |
|------|-----------|---------|
| `requirement` | `SPEC-*` | Standard business or technical requirement |
| `governance` | `GOV-*` | Rules about the method itself (meta-specifications) |
| `protected_behavior` | `PB-*` | Critical behaviors with machine-verifiable assertions |
| `architecture_decision` | `ADR-*` | Cross-cutting technical decisions with rationale |
| `design_constraint` | `DCL-*` | Machine-checkable rules derived from architecture decisions |

Types are auto-detected from the ID prefix. A specification with ID `GOV-15` is automatically classified as type `governance`.

### Requirements (`SPEC-*`)

The most common type. Requirements describe what the system must do for its users, operators, or other systems. Examples:

- `SPEC-001: Users can create tasks with a title and description`
- `SPEC-002: Tasks transition through created → in_progress → done`
- `SPEC-003: API rate limits enforce 300 requests per minute per tenant`

### Governance (`GOV-*`)

Governance specifications define the rules of the engineering process itself. They are the method's self-description — how specifications, tests, and work items interact. Governance specs carry assertions that can be automatically checked.

### Protected behaviors (`PB-*`)

Protected behaviors mark critical system invariants that must never regress. They carry machine-verifiable assertions (grep patterns, glob checks) that run before every build. If a protected behavior assertion fails, the build is blocked.

Use protected behaviors for safety-critical constraints: "API keys must never appear in client-side bundles", "Authentication middleware must be present on all admin routes", "The rate limiter must be configured before the request handler."

### Architecture decisions (`ADR-*`) and design constraints (`DCL-*`)

Architecture Decision Records capture cross-cutting technical choices: why a particular database was chosen, why a specific communication pattern was adopted, what alternatives were considered and rejected. They include a `consequences` section documenting known trade-offs.

Design Constraints are machine-checkable rules derived from ADRs. Where an ADR says "we chose SQLite for the knowledge database because of single-file portability", the corresponding DCL says "the knowledge database must use SQLite" and carries assertions to verify it.

For details, see the [Architecture Decisions guide](08-architecture.md).

## The spec-first workflow

The most important discipline in GroundTruth is **spec-first**: when the owner describes what the system must do, record or verify specifications *before* writing any code.

This applies whenever you encounter specification language — words like "must", "should", "must include", numbered criteria, or acceptance conditions. The workflow:

1. **Recognize** the input as specification language
2. **Record** the specification in the knowledge database (or verify an existing spec covers it)
3. **Identify** any implementation gaps → create work items
4. **Add** work items to the backlog for prioritization
5. **Wait** for prioritization approval before implementing

This discipline prevents the common failure mode where code is written first and specifications are retrofitted to match — which defeats the purpose of specifications entirely.

## Spec hierarchies

Specifications can be organized hierarchically using dot notation:

```
SPEC-245          (parent: top-level requirement)
SPEC-245.1        (child: first sub-requirement)
SPEC-245.1.1      (grandchild: detail of sub-requirement)
SPEC-245.2        (child: second sub-requirement)
```

Hierarchies express decomposition: a high-level requirement broken into verifiable sub-requirements. The parent spec describes the intent; child specs describe the testable pieces.

Utility functions `get_depth()` and `get_parent_id()` help navigate hierarchies:

- `get_depth("SPEC-245.1.3")` → `2`
- `get_parent_id("SPEC-245.1")` → `"SPEC-245"`

## Tags and scope

Specifications carry optional `tags` (a list of strings) and a `scope` field for organization:

- **Tags**: categorize by subsystem, phase, or concern. Example: `["auth", "api", "phase-2"]`
- **Scope**: a single string describing the spec's domain. Example: `"billing"`, `"widget"`, `"infrastructure"`
- **Section**: group specs into logical document sections. Example: `"3.2 Authentication"`

Use tags for cross-cutting concerns (a spec might be tagged both `["api", "security"]`) and scope for primary ownership.

## Common anti-patterns

**Over-specifying implementation.** "The login endpoint must use bcrypt with cost factor 12 and return a JWT with RS256 signing." This binds the spec to specific libraries and algorithms. Better: "User credentials must be stored using a one-way hash. Authentication tokens must be cryptographically signed and expire within 24 hours."

**Under-specifying acceptance.** "The system should handle errors gracefully." This cannot be tested. Better: "When an API call fails, the response must include an error code, a human-readable message, and a correlation ID for debugging."

**Spec drift.** Specifications written early and never revisited as the system evolves. Assertions catch some drift automatically, but teams should review spec coverage at phase boundaries (see the [Governance guide](05-governance.md)).

**Retrofitting specs to code.** Writing code first, then creating specifications that describe what was built. This produces specifications that are implementation descriptions, not requirements — defeating the decision-log purpose.

**Phantom specifications.** Specifications that exist in the database but have no linked tests. These create a false sense of coverage. The governance rule GOV-12 requires that work item creation triggers test creation, preventing orphaned specs from accumulating.
