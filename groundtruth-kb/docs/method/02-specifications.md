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

The native specification lifecycle describes whether a formal record is
current: `active`, `superseded` or `retired`.

- **Active:** the record states a current requirement or rule.
- **Superseded:** a replacement formal record carries the current requirement.
- **Retired:** the requirement no longer applies.

Amendments use the current record version and preserve history. Read the
current fields and history with `gt spec show <ID> --history --json`.

Implementation and verification evidence are separate from this lifecycle.
An active specification can describe work that is still unfinished. Its linked
tests, current results and independently reviewed work establish whether the
implementation satisfies it. The `implementation_verified_at` marker, when
applicable, is stamped by the service when an amendment asserts
`implementation_verified_at: true`; it is not a specification status or a
substitute for the underlying evidence. See the [CLI reference](../reference/cli.md).

Do not promote a specification through `specified`, `implemented` or
`verified`: these are not accepted values of the native `status` field.

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

Design Constraints are machine-checkable rules derived from ADRs. For example, an ADR can select PostgreSQL behind the native domain service; a corresponding DCL can require callers to use that service and carry executable assertions for the boundary.

For details, see the [Architecture Decisions guide](08-architecture.md).

## The spec-first workflow

The most important discipline in GroundTruth is **spec-first**: when the owner describes what the system must do, record or verify specifications *before* writing any code.

This applies whenever you encounter specification language — words like "must", "should", "must include", numbered criteria, or acceptance conditions. The workflow:

1. **Recognize** the input as specification language
2. **Record** the specification in MemBase (or verify an existing spec covers it)
3. **Identify** any implementation gaps → create work items
4. **Add** work items to the backlog for prioritization
5. **Wait** for prioritization approval before implementing

This discipline prevents the common failure mode where code is written first and specifications are retrofitted to match — which defeats the purpose of specifications entirely.

### Core specification intake

At project start, read the current project and its linked formal records to
identify missing requirements. The specification-intake skill classifies the
owner's text into a temporary candidate, then confirms it into the applicable
canonical specification or discards it. An inferred candidate does not record
an owner answer. Re-query the canonical record before proceeding.

Capturing a specification does not create implementation work or approve a
proposal. Create any required work item in its execution project with a linked
executable test and an active test-plan phase. The project-initialization
intake options and supported scaffold profiles are documented in the
[CLI reference](../reference/cli.md#requirement-intake).

## Spec hierarchies

Specifications can be organized hierarchically using dot notation:

```
SPEC-245          (parent: top-level requirement)
SPEC-245.1        (child: first sub-requirement)
SPEC-245.1.1      (grandchild: detail of sub-requirement)
SPEC-245.2        (child: second sub-requirement)
```

Hierarchies express decomposition: a high-level requirement broken into verifiable sub-requirements. The parent spec describes the intent; child specs describe the testable pieces.

The dot notation is a naming convention; the relationship itself is the explicit `parent` field of the child's record, which `gt spec show <ID> --json` reads back:

- `SPEC-245.1.3` → depth `2` (two dot-separated segments below the top-level ID)
- `SPEC-245.1` → `"parent": "SPEC-245"`

## Tags and scope

Specifications carry optional `tags` (a list of strings) and a `scope` field for organization:

- **Tags**: categorize by subsystem, phase, or concern. Example: `["auth", "api", "phase-2"]`
- **Scope**: a single string describing the spec's domain. Example: `"billing"`, `"widget"`, `"infrastructure"`
- **Section**: group specs into logical document sections. Example: `"3.2 Authentication"`

Use tags for cross-cutting concerns (a spec might be tagged both `["api", "security"]`) and scope for its domain. Scope does not assign a work item to an agent.

## Common anti-patterns

**Over-specifying implementation.** "The login endpoint must use bcrypt with cost factor 12 and return a JWT with RS256 signing." This binds the spec to specific libraries and algorithms. Better: "User credentials must be stored using a one-way hash. Authentication tokens must be cryptographically signed and expire within 24 hours."

**Under-specifying acceptance.** "The system should handle errors gracefully." This cannot be tested. Better: "When an API call fails, the response must include an error code, a human-readable message, and a correlation ID for debugging."

**Spec drift.** Specifications written early and never revisited as the system evolves. Assertions catch some drift automatically, but teams should review spec coverage at phase boundaries (see the [Governance guide](05-governance.md)).

**Retrofitting specs to code.** Writing code first, then creating specifications that describe what was built. This produces specifications that are implementation descriptions, not requirements — defeating the decision-log purpose.

**Phantom specifications.** Specifications that exist in the database but have no linked tests. These create a false sense of coverage. The governance rule GOV-12 requires that work item creation triggers test creation, preventing orphaned specs from accumulating.
