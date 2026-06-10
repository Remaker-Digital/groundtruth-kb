NEW

# Implementation Proposal — Dispatch-Envelope Element Spec + DCL (governance_review)

bridge_kind: governance_advisory
Document: gtkb-envelope-dispatch-element-001
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 35ed98f8-ae1c-4a5f-bf3f-219c579f144e
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous /loop dynamic mode

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4296
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. The
two net-new artifacts (`SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
`DCL-DISPATCH-ENVELOPE-RULES-001`) are inserted downstream via the
active PAUTH's `approval_packet_creation` mutation class as separate
formal-artifact-approval-packet operations after GO. (Trips
`KB_MUTATION_NEGATION_RE` in `.claude/hooks/bridge-compliance-gate.py:203-207`,
short-circuiting `_declares_kb_mutation` to False.)

## Claim

Define the **dispatch-envelope** element as a qualified, always-named
construct (never bare "envelope") in GroundTruth-KB's three-part envelope
anatomy (dispatch / session / topic, per WI-4302 meta-model ADR). A
dispatch envelope routes recurring ops, review, or audit work to a
chosen harness, role, topic, or arbitrary prompt on a cadence or
event subscription, **always** activity-gated (idempotent self-check
before spawn) per the S308 blind-automation lesson.

The proposal drafts two artifacts:

1. **`SPEC-DISPATCH-ENVELOPE-ELEMENT-001`** — the schema and behavior
   contract for a dispatch envelope: target dimensions (harness, role,
   topic, prompt), trigger kinds (cadence cron, event subscription),
   activity-gate predicate, payload template, persistence opt-in flag.
   Reuses `harness-registry.json`'s `invocation_surfaces.*.argv`,
   the canonical `::init <subject> <role>` keyword family (per
   `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` VERIFIED), and the existing
   cross-harness dispatch substrate.
2. **`DCL-DISPATCH-ENVELOPE-RULES-001`** — the design constraint that
   `config/dispatcher/rules.toml` is the declarative rule registry,
   with hot-reload semantics, one entry per rule, and a hybrid
   activity-gate API (DSL for common predicates + dotted-path escape
   hatch for complex cases).

## Why Now

Per the 2026-06-04 owner grilling (envelope-program AUQ over WI-3468),
the envelope program formalizes a 3-part anatomy
(work / dispatch / session-topic, per DELIB-20260637 amended by
DELIB-20260648). The dispatch-envelope element is the foundational
"how recurring work gets routed" construct that:

- Carries the recurring ops/review/audit cadence that the v1.0
  major-release content goal depends on (per the standing release-goal
  DELIB referenced by WI-4296).
- Activity-gates spawns so we never repeat the S308 blind-automation
  incident (~12.5 M tokens/day of background spawns doing work without
  information; the defect was repeating work whether or not anything
  needed doing).
- Reuses the existing cross-harness dispatch substrate
  (`scripts/cross_harness_bridge_trigger.py` + registered hooks) rather
  than inventing a parallel automation surface.
- Lets topic envelopes (per WI-4295 `::open <type>`) optionally
  override the default per-role harness routing via per-topic
  routing — preserving the durable-role-vs-session-state authority split
  per `GOV-SESSION-ROLE-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001`.

Today GroundTruth-KB has the cross-harness event-driven trigger (which
dispatches on Stop / PostToolUse), but no declarative rule registry
for recurring or scheduled work, no canonical schema for what a
"dispatch envelope" carries, and no formal activity-gate API. This
proposal fills those gaps.

## Why Not (alternatives considered)

- **Cron-only / cadence-only triggers** (rejected): would re-create the
  retired OS-poller class (`AgentRedFileBridgeIndexScan-*`) that fired
  on a fixed interval regardless of bridge activity. The S308 incident
  established that activity-independent automation is the defect.
- **Pure event-driven triggers (no cadence)**: cannot handle
  release-readiness audits, drift sweeps, or other "every Monday at
  09:00" work that is intrinsically cadence-coupled. Both trigger
  kinds are needed; the dispatcher unifies them.
- **Pure code-defined rules (no TOML registry)** (rejected): would
  embed every rule in source, requiring a code release to add or
  modify routing. Owner-edit-friendliness is the goal: TOML +
  hot-reload + a DSL for common predicates.
- **Pure DSL activity-gate (no escape hatch)** (rejected): expressive
  enough for 80 % of rules but blocks the long tail. Hybrid: DSL grows
  incrementally, path-based predicate is the unlimited escape.
- **Always-persist dispatch events to MemBase** (rejected): would
  flood `work_items` siblings with low-information rows. Opt-in
  `persist=true` flag per rule; default ephemeral logging to
  `.gtkb-state/dispatcher/log.jsonl`.
- **Bare "envelope" terminology**: rejected per WI-4302 meta-model
  ADR and DELIB-20260637; envelope is always qualified
  (dispatch / session / topic) to avoid ambiguity.

## Prior Deliberations

- `DELIB-20260635` — originating owner directive citing dispatch
  envelopes as the v1.0 major-release headline content. Establishes
  the activity-gated mandate referencing S308.
- `DELIB-20260637` — refined the 3-part envelope anatomy
  (work / dispatch / session-topic). Originally framed dispatch as the
  mandatory outer container; amended by DELIB-20260648.
- `DELIB-20260638` — refined the closed-vocabulary set for `::open`
  activity types (WI-4295 sibling). Bears on the per-topic dispatch
  routing override.
- `DELIB-20260648` — PAUTH-minting deliberation for the envelope-program
  spec WI batch (WI-4291..WI-4297). Authorizes governance-review spec
  amendments + net-new spec/DCL creation via approval-packet path.
  Refines DELIB-20260637 #1: containment chain is dispatch ⊃ session ⊃
  topic, with the dispatch tier OPTIONAL (interactive sessions skip it;
  session is the outer wrapper).
- `bridge/gtkb-canonical-init-keyword-syntax-001.md` chain (VERIFIED at
  `-012`) — establishes the `::init <subject> <role>` keyword that
  the dispatch envelope reuses for harness invocation.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` (NEW, this
  session) — sibling spec for the wrap-keyword; coupled via the
  envelope-program PAUTH.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*`
  (VERIFIED) and `bridge-essential.md` § Operational Mode — the
  established cross-harness event-driven trigger is the substrate the
  dispatch envelope's event-subscription triggers extend.
- S308 incident in `bridge-essential.md` § Incident History — the
  blind-automation lesson that motivates the mandatory activity-gate.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains canonical
  workflow state; this proposal is filed under the file-bridge protocol
  and does not modify bridge mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this
  Specification Links section satisfies the linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project:` and
  `Project Authorization:` metadata cite the active PAUTH covering
  WI-4296.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal
  declares `requires_verification: false` because it is a
  `bridge_kind: governance_review` with `target_paths: []`; GO is
  terminal for the spec-body approval step per
  `feedback_latest_go_terminal_for_governance_review.md`. The
  Specification-Derived Verification Plan section below enumerates the
  reviewer-side gates that ARE performed in this thread; downstream
  spec-insertion verification runs at the formal-artifact-approval-packet
  gate (a separate operation under `GOV-ARTIFACT-APPROVAL-001`).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files (this
  proposal and future approval packets) remain under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` — the two downstream artifacts
  (`SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
  `DCL-DISPATCH-ENVELOPE-RULES-001`) each require a
  formal-artifact-approval packet; those packets are **not** filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4296 is the governing backlog item
  and is in `approval_state=implementation_authorized` covered by the
  active PAUTH.
- `GOV-SESSION-ROLE-AUTHORITY-001` — preserved by the per-topic
  routing override: override is a per-message routing choice, not a
  durable role assignment.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — proposed spec/DCL are
  governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — informs the
  artifact-oriented framing: dispatch envelopes are durable MemBase
  artifacts (rules) not transient code-embedded automation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new spec + DCL creation
  are lifecycle events covered by the PAUTH's
  `allowed_mutation_classes`.

**Specs referenced (not modified by this proposal):**

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (VERIFIED at -012) — the
  init-keyword that the dispatch envelope reuses for harness invocation.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — paired init-keyword
  contract; dispatch envelopes emit the canonical keyword derived from
  the target's durable role (or per-topic override).
- `DCL-SESSION-ROLE-RESOLUTION-001` — the resolution table for
  session-stated vs durable role; dispatch envelopes use durable role
  for routing unless the topic envelope explicitly overrides.

**Specs drafted by this proposal (downstream insert via approval packets):**

- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` (NEW; body drafted below).
- `DCL-DISPATCH-ENVELOPE-RULES-001` (NEW; body drafted below).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no
fresh AUQ is required at proposal-filing time. The PAUTH cites the
operative owner decisions:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner
   approved the envelope-program spec-WI batch (WI-4291..WI-4297)
   under `bridge_kind=governance_review`, with new-spec creation
   authorized via the formal-artifact-approval-packet path. This
   proposal operates under that scope.
2. **DELIB-20260635** — originating dispatch-envelope directive;
   activity-gate mandate; v1.0 release-content framing.
3. **DELIB-20260637 + DELIB-20260648** — 3-part envelope anatomy with
   dispatch tier optional; dispatch envelope is the transport wrapper
   when present.
4. **DELIB-20260638** — informs the topic-envelope coupling that
   makes the per-topic harness routing override valid.

Owner-input dependencies downstream of GO:

- 2 formal-artifact-approval packets at MemBase insertion time, one
  for each net-new artifact.
- No source / hook / test mutation requested in this thread; the
  dispatcher implementation lands in WI-4301 (envelope-program
  implementation umbrella), which is a separate WI under its own
  authorization.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4296
captured the complete schema design (target dimensions, trigger kinds,
activity-gate API hybrid, persistence opt-in, rules.toml hot-reload,
per-topic routing override); the PAUTH covers spec+DCL creation; the
sibling `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and the established
cross-harness dispatch substrate establish the reuse surface. No new
owner requirement is needed to draft and approve the spec/DCL bodies
proposed below.

## Spec Body — SPEC-DISPATCH-ENVELOPE-ELEMENT-001 (draft)

**Title:** Dispatch-Envelope Element Schema and Behavior Contract.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

A **dispatch envelope** is the routing element in the GroundTruth-KB
three-part envelope anatomy. It carries the metadata required to spawn
a unit of work to a target on a trigger, always activity-gated. The
term is always qualified — never bare "envelope".

**Target dimensions** (a dispatch envelope targets exactly one):

1. **harness** — a specific installed harness by `harness_id`
   (e.g., `B` for Claude Code, `A` for Codex). Routes via
   `harness-registry.json` `invocation_surfaces.<harness>.argv`.
2. **role** — a durable role (`prime-builder` or `loyal-opposition`).
   Routes to the harness currently holding that role per the
   durable role registry, unless overridden by a topic-envelope's
   `routing_override`.
3. **topic** — a topic envelope (`::open <type>`) record. The topic's
   `routing_override` (if any) supersedes the role default.
4. **prompt** — an arbitrary user prompt string. Spawns a session
   with the prompt as the first message (`::init` keyword optional;
   if omitted, the spawned session starts in its default role mode).

**Trigger kinds:**

1. `cadence_cron` — a cron expression (`* * * * *` syntax). The
   dispatcher polls cron rules on a 1-minute heartbeat; a rule
   matching the current minute fires after passing its activity gate.
2. `event_subscription` — a named event subscription (e.g.,
   `bridge_actionable_changed`, `working_tree_drifted`, `index_pruned`).
   The dispatcher consumes events from the existing cross-harness
   substrate event bus.

**Activity gate** (REQUIRED on every dispatch envelope):

The activity-gate is an idempotent predicate that the dispatcher
evaluates immediately before spawn. If the predicate returns false,
the spawn is skipped (logged at level `gate_skip`); if true, the
spawn proceeds. This is the S308 protection: no automation fires
without verifying that work exists.

Two predicate forms (hybrid API, per DCL-DISPATCH-ENVELOPE-RULES-001):

- **DSL form** — a closed vocabulary of common predicates
  (`bridge_actionable_count > 0`, `time_since_last_spawn > 5m`,
  `working_tree_dirty`, etc.). DSL grows incrementally as new patterns
  emerge.
- **Path form** — a fully-qualified Python dotted path
  (e.g., `groundtruth_kb.predicates.bridge_has_actionable_for(role)`).
  The dispatcher imports + calls; the predicate returns a boolean.
  This is the unlimited escape hatch for predicates that don't fit the
  DSL.

**Payload template:**

A dispatch envelope carries a payload that becomes the spawned
session's first prompt. Standard payload forms:

1. `::init <subject> <role>` (per `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`).
2. Free-form prompt text (when target = prompt).
3. Templated prompts referencing rule-context variables (e.g.,
   `"::init gtkb pb\\n\\nReview the actionable bridge entries for ${role}."`).

**Persistence:**

Default ephemeral: each dispatch is logged as one line to
`.gtkb-state/dispatcher/log.jsonl` (timestamp, rule_id, target,
gate_result, spawn_outcome) and otherwise leaves no MemBase footprint.

Opt-in per-rule `persist=true`: emits a row to the new MemBase
`dispatch_events` table (schema in DCL-DISPATCH-ENVELOPE-RULES-001).
Used when the dispatch is itself an auditable artifact (e.g., a
project-completion drive per WI-4297).

**Per-topic routing override (per DELIB-20260648):**

A topic envelope (`::open <type>`, per WI-4295) MAY carry a
`routing_override` field that names a specific `harness_id`. When a
dispatch envelope targets that topic, the override supersedes the
role-default routing for that one spawn. The override is a
per-message routing choice; it does NOT durably reassign roles, and
the durable role registry is unchanged (preserves
`GOV-SESSION-ROLE-AUTHORITY-001`'s authority split).

**Activity-gate state file:**

`.gtkb-state/dispatcher/state.json` is the per-rule state record
consulted by DSL predicates (e.g., `time_since_last_spawn`).
Updated atomically after each spawn outcome.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `config/dispatcher/rules.toml` exists at envelope-program
   implementation time (WI-4301). Until then the assertion is
   expected-failing at status `specified`.
2. `grep_absent` — no automation script other than the canonical
   dispatcher SHALL maintain a parallel set of dispatch rules.
   (Cross-checks against `archive/smart-poller-2026-05-09/` to ensure
   retired substrates stay archived.)

## Spec Body — DCL-DISPATCH-ENVELOPE-RULES-001 (draft)

**Title:** Dispatcher Rule Registry, Hot-Reload, and Activity-Gate API
Hybrid.

**Type:** design_constraint.

**Status (at insertion):** specified.

**Body:**

The dispatch envelope ecosystem MUST conform to the following design
constraints:

1. **Rule registry location:** `config/dispatcher/rules.toml` is the
   sole declarative registry of dispatch envelopes. No dispatch
   envelope may be defined in source code, in MemBase work_items, or
   in any other file. (Implementation note: a future migration of
   release-readiness rules from per-script ad-hoc cron entries into
   this registry is an envelope-program implementation concern, not a
   constraint violation, provided the migration lands the registry
   entries.)

2. **Rule schema:** each TOML entry has the keys
   `id`, `trigger`, `target`, `activity_gate`, `payload`, and
   `persist` (default `false`). `id` MUST be unique. Schema validation
   happens at dispatcher start AND on file change (hot-reload).

3. **Hot-reload:** the dispatcher MUST detect changes to
   `config/dispatcher/rules.toml` and reload the rule set without
   restart. A rule whose `id` is removed terminates its scheduled
   spawns at the next reload tick.

4. **Activity-gate API (hybrid):**
   - DSL form: closed vocabulary of common predicates. New DSL
     predicates require a separate spec amendment.
   - Path form: a fully-qualified Python dotted path resolving to a
     callable returning `bool`. The dispatcher MUST import + call the
     path in a sandboxed subprocess to prevent dispatcher hang on a
     bad predicate; timeout 5 seconds, treated as `gate_skip` on
     failure.

5. **Persistence semantics:**
   - Default ephemeral: `.gtkb-state/dispatcher/log.jsonl` is the
     authoritative log. JSONL one line per dispatch attempt
     (gate_skip OR spawn_outcome).
   - Opt-in persistent: when `persist=true`, the dispatcher MUST emit
     a row to MemBase `dispatch_events` table after each spawn. The
     table schema:
     ```
     dispatch_events:
       id, version, rule_id, target_kind, target_value,
       trigger_at, gate_result, payload_template_id,
       spawn_outcome, spawn_pid, spawn_exit_status,
       changed_by, changed_at, change_reason
     ```
   - Append-only versioning (consistent with other MemBase tables).

6. **Activity-gate is mandatory:** the dispatcher MUST reject a rule
   at registry load time if `activity_gate` is absent or empty. There
   is no default-to-always-fire path. This is the S308 incident's
   structural protection.

7. **No bare "envelope":** all rule-context references to envelopes
   MUST be qualified (dispatch / session / topic). Bare "envelope"
   identifiers in rule names, comments, or payload templates trigger a
   load-time validation warning (advisory; not blocking).

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `config/dispatcher/rules.toml` exists; loadable by the
   dispatcher validator. Expected-failing until WI-4301 implementation.
2. `grep` — `dispatch_events` MemBase table schema is present in
   `groundtruth_kb/db/schema.py` (or equivalent). Expected-failing
   until WI-4301 Slice C (dispatch-envelope substrate integration).

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4296 `source_owner_directive`).

**Related deliberations:** `DELIB-20260635`, `DELIB-20260637`,
`DELIB-20260638`, `DELIB-20260648`.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no blocking
clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread (per `feedback_latest_go_terminal_for_governance_review.md`).
No follow-on post-impl report or VERIFIED verdict is required for the
spec/DCL-body approval step.

The downstream MemBase insertions are verified at their own gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id SPEC-DISPATCH-ENVELOPE-ELEMENT-001 --json

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type design_constraint --id DCL-DISPATCH-ENVELOPE-RULES-001 --json
```

Each MUST return one row at version 1 with body fingerprints matching
the respective formal-artifact-approval packets. The verification runs
at *spec-insertion* time, not at this bridge thread's review time.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at the
   top of the `gtkb-envelope-dispatch-element-001` document entry; the
   file exists on disk; first line is the canonical `NEW` status
   token.
2. **Applicability preflight:** `python scripts/bridge_applicability_preflight.py
   --bridge-id gtkb-envelope-dispatch-element-001` returns
   `preflight_passed: true`, `missing_required_specs: []`.
3. **Clause preflight:** `python scripts/adr_dcl_clause_preflight.py
   --bridge-id gtkb-envelope-dispatch-element-001` returns
   `Blocking gaps: 0`.
4. **Project linkage:** `Project Authorization`, `Project`, and
   `Work Item` metadata point at the active PAUTH and the live work
   item; the WI is in the PAUTH's `included_work_item_ids`.
5. **Phantom-spec sweep:** every cited SPEC / GOV / ADR / DCL / PB id
   exists in the live `specifications` table (the two net-new artifact
   ids `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
   `DCL-DISPATCH-ENVELOPE-RULES-001` are forward-references to the
   downstream approval-packet insertions; not cited as existing).
6. **Spec/DCL body completeness:** both spec-body sections contain
   schema, behavior contract, assertions, and DELIB citations
   sufficient for downstream approval packets to fingerprint without
   further editing.
7. **Activity-gate mandate:** the spec body MUST encode the
   activity-gate as a load-time mandatory field; reviewer confirms
   the DCL section #6 ("Activity-gate is mandatory") is present and
   unambiguous.
8. **No KB mutation in scope:** `kb_mutation_in_scope: false`; no
   `groundtruth.db` write is performed by this thread.

## Risk / Rollback

This proposal writes one file
(`bridge/gtkb-envelope-dispatch-element-001-001.md`) and inserts one
entry pair (`Document:` + `NEW:`) in `bridge/INDEX.md`. Rollback is a
single `git restore` of `bridge/INDEX.md` and `rm` of the versioned
file (or a WITHDRAWN follow-on). The downstream spec/DCL insertions
(under the approval-packet path) are separate, gated operations
governed by `GOV-ARTIFACT-APPROVAL-001` and are not part of this
thread's blast radius.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at
the top of the `gtkb-envelope-dispatch-element-001` document list in
`bridge/INDEX.md`; no prior version is deleted or rewritten
(append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this bridge proposal is governance documentation; no source /
test / hook / configuration code is modified by this thread. The
downstream spec/DCL insertions (under the approval-packet path) will
record their own commit type when filed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
