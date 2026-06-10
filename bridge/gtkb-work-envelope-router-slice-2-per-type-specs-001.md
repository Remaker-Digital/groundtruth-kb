NEW

# Implementation Proposal — Topic-Envelope Router Slice 2: 5 Per-Type SPECs (governance_review)

bridge_kind: governance_advisory
Document: gtkb-work-envelope-router-slice-2-per-type-specs
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
Work Item: WI-4295
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation. The 5 net-new per-type
SPECs proposed here insert downstream via the active PAUTH's
`approval_packet_creation` mutation class as separate
formal-artifact-approval-packet operations after GO. (Trips
`KB_MUTATION_NEGATION_RE` in
`.claude/hooks/bridge-compliance-gate.py:203-207`.)

## Claim

Slice 2 of WI-4295 completes the 7-artifact target of the
topic-envelope router by drafting the 5 per-type SPECs. Slice 1
(umbrella SPEC + routing DCL) GO'd at
`bridge/gtkb-work-envelope-router-slice-1-001-004.md` (LO Antigravity
harness C); the per-type bodies depend on Slice 1's umbrella for the
closed 5-vocabulary `{spec, build, test, deliberation, project}` and
the activity-type-to-service routing constraint.

Five SPECs drafted, one per type token:

1. **SPEC-TOPIC-SPEC-001** — `::open spec` topic envelope: preload
   sources, routing to the spec-intake service, per-topic harness
   routing override semantics.
2. **SPEC-TOPIC-BUILD-001** — `::open build` topic envelope:
   build/scaffold/packaging dispatch.
3. **SPEC-TOPIC-TEST-001** — `::open test` topic envelope: test
   execution + assertion-run dispatch.
4. **SPEC-TOPIC-DELIBERATION-001** — `::open deliberation` topic
   envelope: Deliberation Archive write-path dispatch.
5. **SPEC-TOPIC-PROJECT-001** — `::open project` topic envelope:
   project-lifecycle dispatch.

Each per-type SPEC includes: type name (verbatim from closed
vocabulary), preload sources (what state the topic loads on `::open
<type>` invocation), routing target (the existing GT-KB service per
Slice 1's DCL), per-type harness routing override (per WI-4296
DELIB-20260648 amendment), and a brief description of MEDIUM
auto-close behavior at `::close <type>` time.

**Scope unchanged from Slice 1:** governance_review with
`target_paths: []`, `requires_verification: false`,
`kb_mutation_in_scope: false`. GO is terminal for the spec-body
approval step (per Slice 1's pattern). Downstream insertion is the
formal-artifact-approval-packet path under PAUTH.

## Why Now

Slice 1's umbrella + DCL are GO'd. Slice 2 completes the WI-4295
7-artifact target. The per-type SPECs are needed for:

- WI-4301 implementation umbrella's topic-router Slice C
  (substrate integration needs per-type dispatch tables).
- WI-4296 dispatch-envelope element's per-topic routing override
  (each per-type SPEC documents its override surface).
- Downstream owner-evidence for the 5 spec insertions (each per-type
  SPEC body becomes the explicit_change_request basis for its
  approval packet).

Filing Slice 2 alongside Slice 1's GO completes WI-4295's
governance-only deliverable.

## Why Not (alternatives considered)

- **Defer Slice 2 until Slice 1 VERIFIED** (rejected): Slice 1 is
  governance_review with GO-terminal pattern; there is no VERIFIED
  step. Slice 2 can ship as soon as Slice 1's GO lands.
- **Inline Slice 2 into Slice 1** (rejected during Slice 1 planning):
  would have produced a single 7-artifact proposal that's harder to
  review and revise. Slicing umbrella-first allowed Slice 1 to land
  cleanly; Slice 2 inherits the umbrella's GO.
- **Per-type SPEC as 5 independent bridge threads** (rejected): per-type
  SPECs are tightly coupled (same routing model, same override
  semantic, same MEDIUM auto-close). One thread for all 5 keeps
  audit-trail coherent.

## Prior Deliberations

- `DELIB-2238`, `DELIB-2500` — originating envelope-program foundation.
- `DELIB-20260635`, `DELIB-20260636` — v1.0 release-content + AUQ
  context.
- `DELIB-20260637` — 3-part envelope anatomy; topic-envelope renaming
  (the per-type SPECs are topic envelopes per this decision).
- `DELIB-20260638` — reduced closed vocabulary from 8 to 5 elements;
  defines the 5 type tokens this slice covers.
- `DELIB-20260648` — PAUTH-minting; authorizes governance-review
  spec creation. Also: per-topic harness routing override authority
  for each per-type SPEC.
- `bridge/gtkb-work-envelope-router-slice-1-001-004.md` (GO; LO
  Antigravity harness C) — Slice 1's GO; this slice continues under
  the same umbrella.
- `bridge/gtkb-envelope-dispatch-element-001-002.md` (GO; LO Codex
  harness A) — WI-4296 dispatch-envelope element; per-topic routing
  override defined there is consumed by each per-type SPEC.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-004.md` (GO; LO
  Antigravity harness C) — WI-4292 wrap-keyword; topic auto-close at
  session-wrap iterates through the per-type topics defined here.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`,
  `GOV-STANDING-BACKLOG-001`,
  `GOV-SESSION-ROLE-AUTHORITY-001` (preserved by per-topic routing
  override design).

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs referenced (Slice 1 dependency):**

- The Slice 1 umbrella SPEC and routing DCL (drafted in the
  `gtkb-work-envelope-router-slice-1-001` GO'd thread; spec ids
  provisional until insertion). Each per-type SPEC in Slice 2 cites
  the Slice 1 umbrella as the canonical command-surface authority
  and the routing DCL as the dispatch-map authority.

**Specs drafted by this proposal:**

- SPEC-TOPIC-SPEC-001 (NEW; body drafted below).
- SPEC-TOPIC-BUILD-001 (NEW; body drafted below).
- SPEC-TOPIC-TEST-001 (NEW; body drafted below).
- SPEC-TOPIC-DELIBERATION-001 (NEW; body drafted below).
- SPEC-TOPIC-PROJECT-001 (NEW; body drafted below).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH;
no fresh AUQ is required:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — authorizes
   governance-review spec creation under this PAUTH for WI-4291..
   WI-4297.
2. **DELIB-20260638** — 5-element closed type vocabulary establishes
   exactly the 5 per-type SPECs drafted here.
3. **DELIB-2500 #2/#3/#7** — MEDIUM auto-close behavior (carried
   forward from Slice 1's DCL).
4. **DELIB-20260648 amendment** — per-topic harness routing override
   semantic that each per-type SPEC accommodates.

Owner-input dependencies downstream of GO:

- 5 formal-artifact-approval packets at MemBase insertion time, one
  per per-type SPEC. Each packet requires owner-evidence per
  GOV-ARTIFACT-APPROVAL-001 (autonomous /loop cannot supply this).

## Requirement Sufficiency

Existing requirements sufficient. Slice 1's umbrella SPEC + routing
DCL (GO'd at `-004`) provide the substrate. The 5 per-type SPECs are
mechanical fill-in: each type token from the closed vocabulary gets
a SPEC documenting its preload + routing details. No new owner
requirement is needed.

## Common Spec Structure (shared across all 5 per-type SPECs)

Each per-type SPEC carries this common structure:

- **Title:** `Topic-Envelope Type: <type>` (with `<type>` substituted).
- **Type:** specification.
- **Status (at insertion):** specified.
- **Body sections:**
  1. **Type token:** the closed-vocab token (e.g., `spec`).
  2. **Trigger surface:** carries forward Slice 1's umbrella SPEC
     parse rule (`^::open <type>$` and `^::close <type>$`).
  3. **Preload sources:** the per-type state the topic loads on
     `::open <type>` invocation.
  4. **Routing target:** the existing GT-KB service the topic
     dispatches to on `::close <type>` (per Slice 1's DCL).
  5. **Per-type harness routing override (per WI-4296):** the
     `routing_override` field semantic for this topic type.
  6. **One-topic-per-type invariant:** preserved from Slice 1's
     umbrella.
  7. **MEDIUM auto-close:** dispatch auto-executes at close time per
     DELIB-2500 #2/#3/#7.
- **Assertions:**
  1. `grep` — at WI-4301 impl time, the per-type dispatch table
     references the type token verbatim.
  2. `grep` — the routing target's existing service reference is
     coherent with the per-type SPEC.
- **Related deliberations:** `DELIB-2238`, `DELIB-2500`,
  `DELIB-20260637`, `DELIB-20260638`, `DELIB-20260648`.

## Spec Body — SPEC-TOPIC-SPEC-001

**Type token:** `spec`.

**Preload sources:**

- The `gt spec list` view filtered by the owner's intended target
  (passed as a payload field on `::open spec`).
- The `gt intake` queue for any pending requirement-candidate records
  the owner may want to promote during the topic.
- Any deliberation-archive records cited by the target spec(s)
  (read-only).

**Routing target:**

The spec-intake pipeline. On `::close spec`, the topic dispatches to
`gt intake` to promote any owner-touched requirement-candidate
records to formal specs, OR to the formal-artifact-approval-packet
path if the topic produced spec-text revisions.

**Per-type harness routing override:**

A `::open spec` topic MAY carry `routing_override.harness=<id>` to
direct the dispatch to a specific harness (e.g., to keep spec-intake
work on a particular harness with that capability). The override is
per-topic; durable role authority is unchanged.

## Spec Body — SPEC-TOPIC-BUILD-001

**Type token:** `build`.

**Preload sources:**

- The `gt project doctor` summary for the current project (read-only).
- Any in-flight build/scaffold WIs from the standing backlog.
- The current package version from `pyproject.toml` and the
  `groundtruth-kb` package state.

**Routing target:**

The build / packaging / scaffold service. On `::close build`, the
topic dispatches to the build pipeline (TBD by WI-4301 Slice C; this
SPEC promises the dispatch surface, not the build pipeline's
internals).

**Per-type harness routing override:**

A `::open build` topic MAY carry `routing_override.harness=<id>` to
target a harness with build capability (e.g., one with Docker /
container runtimes available). Override is per-topic.

## Spec Body — SPEC-TOPIC-TEST-001

**Type token:** `test`.

**Preload sources:**

- The `gt assert` assertion-run history for the current project.
- Any failing assertions per the most recent run.
- The `tests/` directory inventory (read-only file list).

**Routing target:**

The test execution + assertion-run service. On `::close test`, the
topic dispatches to `gt assert` (or equivalent test orchestrator) to
run the topic's targeted test set.

**Per-type harness routing override:**

A `::open test` topic MAY carry `routing_override.harness=<id>` to
direct test execution to a harness with the required Python
interpreter / pytest configuration. Override is per-topic.

## Spec Body — SPEC-TOPIC-DELIBERATION-001

**Type token:** `deliberation`.

**Preload sources:**

- The Deliberation Archive search results for the topic's target
  subject (via `gt deliberations search`).
- Any related owner_conversation records from the most recent
  session.

**Routing target:**

The Deliberation Archive write-path (`gt deliberations record`). On
`::close deliberation`, the topic dispatches to record the
deliberation outcome with appropriate metadata
(`source_type=owner_conversation` or `source_type=lo_advisory` as
applicable).

**Per-type harness routing override:**

A `::open deliberation` topic MAY carry `routing_override.harness=<id>`,
though deliberation work is harness-agnostic and override is
typically unused. Override is per-topic when present.

## Spec Body — SPEC-TOPIC-PROJECT-001

**Type token:** `project`.

**Preload sources:**

- The `gt projects list` summary including the topic's target
  project's lifecycle state.
- The `current_project_authorizations` view for the target project.
- Any open WIs under the target project (via the standing backlog
  view).

**Routing target:**

The project lifecycle service (`gt projects` family). On
`::close project`, the topic dispatches to the appropriate project
lifecycle CLI based on the topic's intent (create, authorize,
retire, etc.).

**Per-type harness routing override:**

A `::open project` topic MAY carry `routing_override.harness=<id>` to
target a harness with project-lifecycle authority. Override is
per-topic; durable role authority is preserved.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`, no
blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread (per `feedback_latest_go_terminal_for_governance_review.md`).
No follow-on post-impl report or VERIFIED verdict is required.

The downstream MemBase insertions are verified at their own gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id SPEC-TOPIC-SPEC-001 --json
# Same shape for SPEC-TOPIC-BUILD-001, SPEC-TOPIC-TEST-001,
# SPEC-TOPIC-DELIBERATION-001, SPEC-TOPIC-PROJECT-001.
```

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at
   the top of the
   `gtkb-work-envelope-router-slice-2-per-type-specs` document
   entry; the file exists on disk; first line is the canonical `NEW`
   status token.
2. **Applicability + clause preflights** pass with no blocking gaps.
3. **Slice 1 dependency:** Slice 1 thread is at GO at `-004`
   (terminal); per-type SPECs may proceed.
4. **Project linkage** unchanged from Slice 1.
5. **Phantom-spec sweep:** every cited SPEC / GOV / ADR / DCL id
   exists in the live `specifications` table, except the 5
   self-references being created here.
6. **Vocabulary closure:** the 5 per-type SPECs match the
   DELIB-20260638 closed vocabulary `{spec, build, test,
   deliberation, project}` exactly.
7. **Common-structure consistency:** each per-type SPEC follows the
   "Common Spec Structure" section above (7 body sections, 2
   assertions, common DELIB citations).

## Risk / Rollback

This proposal writes one file
(`bridge/gtkb-work-envelope-router-slice-2-per-type-specs-001.md`)
and inserts one entry pair in `bridge/INDEX.md`. Rollback is a single
`git restore` + `rm`. The 5 downstream spec insertions are separate,
gated operations under `GOV-ARTIFACT-APPROVAL-001`; each is owner-
gated independently.

If LO surfaces per-type concerns (e.g., a preload source is wrong),
a Slice 2 REVISED can address them without affecting Slice 1's GO.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the
`gtkb-work-envelope-router-slice-2-per-type-specs` document list in
`bridge/INDEX.md`. `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
