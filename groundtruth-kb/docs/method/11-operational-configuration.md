# 11. Operational Configuration Capture

GroundTruth projects often depend on operational control surfaces that live
outside application code: bridges, hooks, rule files, scheduled jobs,
pollers, automation definitions, and markdown directives that shape
agent behavior. If those surfaces are not captured, a project can preserve
specifications and tests while still losing the actual operating model.

This document defines the minimum capture contract for those control surfaces.
For the concrete durable file-bridge polling pattern, see
[File Bridge Automation](12-file-bridge-automation.md).

## Capture rule

If a file, schedule, role description, script, or runtime process can change
how agents coordinate, how automation runs, or how work is executed, it must
be discoverable from the project.

The goal is not to move every operational detail into MemBase.
The goal is to make the full configuration traceable: where it lives, what it
does, who owns it, and how it is reviewed.

## What must be captured

At minimum, capture the following categories when they exist:

### 1. Runtime code artifacts

- Bridge entrypoints, workers, pollers, supervisors, and helper scripts
- Message stores, spool files, or runtime databases
- Hook scripts that trigger bridge or automation behavior
- Health-check or recovery scripts
- Prompt files or inline prompts used by scheduled agent runs

### 2. Directive and instruction surfaces

- `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, or equivalent control files
- Rule files under agent-specific config directories
- Prompt templates, session bootstrap files, and runbooks
- Markdown files that define role boundaries, review procedure, or protocol rules
- Plugin, MCP server, and skill dependencies that change what an agent can do

### 3. Scheduled tasks and automations

- OS schedulers (cron, Task Scheduler, launchd, systemd timers)
- App-native automations and recurring tasks
- GitHub Actions schedules or other CI-driven recurring jobs
- Resident loops that act as de facto schedulers

### 4. Roles and ownership

- Which agent or process implements the bridge
- Which agent reviews or verifies bridge changes
- Standing exceptions to the default relationship
- Owner-only decisions and escalation points

### 5. Protocol and recovery rules

- Message model (for example, async event stream vs transactional request/reply)
- Reply expectations and retry rules
- Startup health checks and handshake behavior
- Failure handling, restart policy, and closure rules

## Where to capture it

Use a layered approach:

1. **Project-owned inventory file**
   Keep a bridge or operations inventory file such as `BRIDGE-INVENTORY.md`
   that lists the relevant artifacts, schedules, directives, and ownership.

2. **Rules file**
   Put behavioral mandates in `CLAUDE.md`, `AGENTS.md`, or equivalent
   startup-loaded rule files.

3. **State file**
   Put current status, live health notes, and recent operational observations
   in `MEMORY.md` or the project's state file.

The knowledge database layer below is what ADR-0001: Three-Tier Memory Architecture calls MemBase.

4. **MemBase (the knowledge database)**
   Record canonical project decisions and procedures in MemBase:
   - `environment_config` for config values and integration surfaces
   - `operation_procedure` for startup, recovery, and deployment procedures
   - `document` records for bridge design notes, inventories, and audits

MemBase is the canonical project history. MEMORY.md can coordinate work, but it cannot make anything true — the markdown files are the discoverable control surface that agents load and operate from.

## Minimum inventory fields

A usable bridge inventory should answer:

- What processes or scripts make the bridge run?
- Where are the code artifacts and config files?
- Which markdown files define behavior or role boundaries?
- Which scheduled tasks or automations exist, and where are they defined?
- Which prompts, plugins, MCP servers, and skills are required?
- Who owns implementation, who reviews, and what exceptions apply?
- What protocol model does the bridge use?
- What is the startup health check and retry behavior?

If a reviewer cannot answer those questions quickly, the configuration capture
is incomplete.

## Update discipline

Update the capture surfaces in the same session whenever you change:

- Bridge runtime code or entrypoints
- Scheduled jobs or automation definitions
- Role descriptions or ownership boundaries
- Reply, retry, handshake, or restart behavior
- Startup or recovery procedures

Do not rely on "everybody knows where that lives." If the answer depends on
tribal memory, the project is already drifting.

## Review checklist

When reviewing bridge or automation changes, verify:

1. The runtime code changes are reflected in the inventory.
2. The role descriptions match the actual operating relationship.
3. The protocol description matches the live behavior.
4. The scheduled tasks and automations are explicitly listed.
5. The state file captures any live operational facts that future sessions need.

## Relationship to project scaffolding

`groundtruth-kb` provides the method, templates, capture contract, and
project scaffolding commands (`gt project init`, `gt project doctor`,
`gt project upgrade`).  The scaffold generates initial configuration files,
but the requirement to keep that configuration accurate and up to date
remains part of the GroundTruth method.
