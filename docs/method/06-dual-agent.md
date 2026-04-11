# 6. Dual-Agent Collaboration

GroundTruth supports a two-agent workflow where the agent building the system is not the same agent evaluating it. This separation catches blind spots, overconfidence, and scope drift that single-agent workflows miss.

## Roles

### Prime Builder

The implementing agent. Responsible for:

- Creating and maintaining specifications, tests, and work items
- Writing implementation code
- Running tests and assertions
- Proposing architectural decisions
- Session wrap-up and state management

Prime Builder is the *how* agent. It receives direction (what to build) and produces artifacts (the built thing plus its documentation trail).

### Loyal Opposition

The evaluating agent. Responsible for:

- Reviewing plans, code, and configuration for correctness
- Identifying security, architecture, and operational risks
- Producing evidence-based reports with concrete findings
- Challenging assumptions with data, not opinion

Loyal Opposition is the *whether it is good enough* agent. It does not implement — it inspects and critiques. Its output is a report, not a code change.

## Vision Decision Filter

Prime Builder and Loyal Opposition should evaluate options against the
GroundTruth KB vision: the owner supplies specifications, clarifications, and
trade-off decisions; the pipeline handles routine implementation,
verification, traceability, and deployment-readiness work.

Use this question in proposals and reviews:

> Does this reduce the owner's role to specifications, clarifications, and
> decisions?

Prefer designs that automate or systematize owner-burdened tasks. Flag designs
that require the owner to supervise routine implementation, reconcile spec/code
drift, inspect basic generated artifacts, or remember cross-agent process state.

## The review cycle

The standard collaboration pattern:

1. **Prime Builder** completes a unit of work and sends it for review. The submission includes: what was done, what files changed, what tests pass, and specific questions for the reviewer.

2. **Loyal Opposition** inspects the work against specifications, governance rules, and architectural constraints. Each significant finding includes:
   - A concrete claim
   - Evidence (file paths, line numbers, reproduction steps)
   - Severity (P0–P3)
   - Impact assessment
   - Recommended action

3. **Verdict** is one of:
   - **GO**: work is acceptable, close the review
   - **NO-GO**: blockers found, must fix before closure
   - **Conditional GO**: acceptable with stated conditions

4. **Prime Builder** addresses NO-GO findings, then resubmits.

5. The cycle repeats until GO is achieved.

## Why separation matters

A single agent that builds and evaluates its own work has a natural bias toward finding it acceptable. The dual-agent model addresses this:

- **Builder blind spots**: the agent that wrote the code is least likely to notice its assumptions
- **Scope creep detection**: an independent reviewer catches when implementation exceeds or falls short of the specification
- **Governance enforcement**: the reviewer checks whether the process was followed, not just whether the code works
- **Evidence quality**: findings require concrete evidence, not "I think this might be wrong"

## Communication protocol

Effective dual-agent collaboration requires structured communication:

### Review requests must include

- What was done (summary of changes)
- Artifact references (file paths, spec IDs, commit hashes)
- Expected response type (advisory review, go/no-go, acknowledgement)
- Specific action items (numbered questions or evaluation criteria)

### Review responses must include

- Verdict (GO, NO-GO, conditional GO)
- For each finding: claim, evidence, severity, impact, recommended action
- Verification performed (what tests were run, what files were inspected)

### General principles

- Every message gets a substantive acknowledgement (not just "received")
- Long-running work sends periodic status updates
- Escalate to the owner only for true owner-only decisions, not for ordinary execution sequencing

## When to use dual-agent vs single-agent

Dual-agent collaboration is most valuable for:

- Non-trivial implementation sessions (3+ file changes)
- Architectural decisions
- Security-sensitive changes
- Release readiness evaluation
- Plan review before large implementations

Single-agent is sufficient for:

- Simple bug fixes with obvious solutions
- Documentation-only changes
- Routine maintenance (dependency updates, log rotation)
- Exploratory research that doesn't modify production artifacts

## Configuration capture for dual-agent systems

If dual-agent work depends on a bridge, resident workers, scheduled jobs, or
other automation, that configuration must be captured explicitly in the
project. At minimum, keep an inventory of:

- runtime entrypoints and bridge scripts
- rule files and markdown directives
- scheduled tasks and automation definitions
- role ownership, review boundaries, and standing exceptions
- protocol, retry, handshake, and recovery rules

See [Operational Configuration Capture](11-operational-configuration.md) for
the full capture contract.
