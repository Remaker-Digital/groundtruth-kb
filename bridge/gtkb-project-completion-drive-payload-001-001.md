NEW

# Implementation Proposal — Project-Completion Drive Payload + Bridge NO-GO AUQ-Class Marker (governance_review)

bridge_kind: governance_review
Document: gtkb-project-completion-drive-payload-001
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
Work Item: WI-4297
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes.
The two net-new artifacts (`SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001`
and `DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001`) are inserted downstream
via the active PAUTH's `approval_packet_creation` mutation class as
separate formal-artifact-approval-packet operations after GO. (Trips
`KB_MUTATION_NEGATION_RE` in `.claude/hooks/bridge-compliance-gate.py:203-207`.)

## Claim

Define two artifacts that together formalize the **autonomous
drive-to-VERIFIED** payload carried by dispatch envelopes (per WI-4296
sibling, just filed at `bridge/gtkb-envelope-dispatch-element-001-001.md`):

1. **`SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001`** — the payload shape
   for `target=auto-drive-project` dispatch envelopes. Carries
   `candidate_projects` (ordered priority list), `max_concurrent_proposals`,
   and `defer_classes` (the AUQ-category vocabulary that pauses the
   drive). Project-completion is a **payload/intent** carried by the
   existing dispatch envelope — NOT a separate dispatch-envelope type
   (re-framed per DELIB-20260637).
2. **`DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001`** — the cross-harness
   contract that Loyal Opposition bridge NO-GO verdicts MUST carry an
   `auq_class:` header field when the NO-GO blocks on an
   owner-AUQ-required decision. Vocabulary closed to eight categories:
   `{approval, waiver, priority, formal_artifact, requirement,
   destructive, deployment, blocking}`.

Together: the dispatcher's auto-drive loop reads NO-GO verdicts on
project-completion target threads; an `auq_class:` marker triggers
DEFERRED parking and owner-surfacing instead of bridge re-entry. This
preserves the deterministic auto-drive while honoring the AUQ-only
enforcement stack.

## Why Now

Per the 2026-06-04 owner grilling (envelope-program AUQ over WI-3468),
the project-completion drive is the headline content of the v1.0
major-release goal (per DELIB-20260635 #4). Without a canonical payload
schema:

- The dispatcher (WI-4296 / WI-4301) has no contract for what a
  project-completion drive's rule template carries.
- The auto-drive loop cannot distinguish AUQ-required NO-GOs (must park)
  from drift NO-GOs (can re-enter with REVISED). Today's NO-GO files
  describe AUQ-required status in free prose; the dispatcher can't
  parse free prose reliably.
- Single-project and multi-project drives need a uniform schema so
  rule templates compose.

The 2-artifact bundle is filed under one bridge thread because the
two artifacts are mutually-load-bearing: the payload spec depends on
the auq_class marker to define `defer_classes`, and the auq_class
marker has no consumer without the drive payload that observes it.

## Why Not (alternatives considered)

- **Define a separate "project-completion dispatch-envelope type"**
  (rejected per DELIB-20260637 re-framing): would fragment the
  envelope-anatomy by adding a third type beyond
  dispatch / session / topic. Owner clarified that
  project-completion is a payload/intent, not a structural element.
- **Implicit AUQ detection from NO-GO prose** (e.g., regex over the
  verdict body) (rejected): brittle, untestable, would re-create the
  prose-pattern detection problem the AUQ-only enforcement stack
  retired. Explicit machine-readable marker is the correct path.
- **Free-form `auq_class:` vocabulary** (rejected): would let
  reviewers invent categories ad-hoc. Closed vocabulary preserves
  rule-template safety.
- **Separate bridge threads for the two artifacts**: would double the
  review surface for two artifacts that have no independent consumer.
  One thread covers both.

## Prior Deliberations

- `DELIB-2238` — establishes wrap-on-exit + envelope-program
  foundation referenced by all WI-4292..WI-4297 siblings.
- `DELIB-2500` — owner directive: keyword shape is bare; outcome
  captured by procedure not keyword; coupling to AUQ-channel.
- `DELIB-20260635` — originating v1.0 release-content directive;
  project-completion drive is the headline content (#4).
- `DELIB-20260637` — re-framed project-completion: it is a payload
  carried by the (optional) dispatch envelope, not a new structural
  element. Direct re-framing authority for this proposal.
- `DELIB-20260648` — envelope-program PAUTH-minting; authorizes
  governance-review spec/DCL creation via approval-packet path.
- `bridge/gtkb-envelope-dispatch-element-001-001.md` (NEW, this
  session) — the sibling proposal that defines the dispatch-envelope
  schema. The payload spec drafted here is the
  `target=auto-drive-project` payload that fills the dispatch
  envelope's `payload` slot for project-completion drives.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` (NEW, this
  session) — sibling envelope-program spec; coupled via the
  envelope-program PAUTH.
- `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the
  Only Valid Owner-Decision Channel" — the owner-AUQ-only enforcement
  rule that the `auq_class:` marker formalizes for the cross-harness
  bridge verdict surface.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the project
  auto-retirement rule that terminates the drive when all WIs reach
  VERIFIED.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains
  canonical workflow state; the auq_class marker extends bridge
  verdict file shape, not bridge protocol mechanics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied
  by this Specification Links section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` —
  `Project Authorization`, `Project`, and `Work Item` metadata cite
  the active PAUTH covering WI-4297.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this proposal
  declares `requires_verification: false` because it is a
  `bridge_kind: governance_review` with `target_paths: []`; GO is
  terminal for the spec-body approval step per
  `feedback_latest_go_terminal_for_governance_review.md`. The
  Specification-Derived Verification Plan section below enumerates
  reviewer-side gates; downstream spec-insertion verification runs
  at the formal-artifact-approval-packet gate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files
  remain under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` — the two downstream artifacts each
  require a formal-artifact-approval packet; those packets are
  **not** filed here.
- `GOV-STANDING-BACKLOG-001` — WI-4297 is the governing backlog item
  in `approval_state=implementation_authorized` covered by the active
  PAUTH.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — defines the
  retirement event that terminates the drive.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — both proposed artifacts are
  governed records.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — informs artifact-oriented
  framing.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — net-new spec + DCL creation
  are lifecycle events covered by the PAUTH's
  `allowed_mutation_classes`.

**Specs referenced (not modified by this proposal):**

- `SPEC-AUQ-POLICY-ENGINE-001` — the deterministic AUQ-only policy
  engine that the auq_class marker integrates with. Bridge NO-GOs
  carrying `auq_class:` feed back into the engine's owner-surfacing
  path.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — the marker is a deterministic
  reviewer-set field; no LLM classification is required.

**Specs drafted by this proposal (downstream insert via approval packets):**

- `SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001` (NEW; body drafted
  below).
- `DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001` (NEW; body drafted below).

**Sibling artifacts (forward references; not yet inserted):**

The sibling `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
`DCL-DISPATCH-ENVELOPE-RULES-001` are the dispatch-envelope substrate
that this payload integrates with. Their bodies are drafted in
`bridge/gtkb-envelope-dispatch-element-001-001.md` (NEW, this session,
awaiting LO review). Both ids are forward-references at the time of
this filing.

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH; no
fresh AUQ is required at proposal-filing time:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — owner
   approved the envelope-program spec-WI batch (WI-4291..WI-4297)
   under `bridge_kind=governance_review`, new-spec creation via
   approval-packet path. This proposal operates under that scope.
2. **DELIB-20260635 #4** — project-completion drive is the v1.0
   release headline content.
3. **DELIB-20260637 re-framing** — project-completion is a
   payload/intent (not a separate dispatch-envelope type). Direct
   authority for the SPEC's payload framing.

Owner-input dependencies downstream of GO:

- 2 formal-artifact-approval packets at MemBase insertion time.
- LO/Codex cross-harness process change: LO bridge-verdict authors
  MUST adopt the `auq_class:` header field when filing AUQ-class
  NO-GOs. This is a documentation change (rule + bridge templates),
  filed as a sibling implementation proposal under WI-4301
  (envelope-program implementation umbrella) or a dedicated
  follow-on, NOT in this thread.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4297
captured the complete payload design (candidate_projects ordering,
max_concurrent_proposals bound, defer_classes vocabulary, AUQ-class
marker schema, event-driven re-entry no-background-watch); the PAUTH
covers spec+DCL creation; the dispatcher substrate (WI-4296 sibling)
provides the consuming surface. No new owner requirement is needed to
draft and approve the spec/DCL bodies proposed below.

## Spec Body — SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001 (draft)

**Title:** Project-Completion Drive Payload Schema for Dispatch
Envelopes.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

A **project-completion drive** is a dispatch envelope whose
`target=auto-drive-project` and whose payload conforms to this
specification. The drive autonomously advances one or more
owner-authorized projects toward VERIFIED-complete state by
file-bridge-protocol-compliant proposals.

**Payload schema:**

```toml
[payload]
candidate_projects = ["PROJECT-A", "PROJECT-B", ...]   # ordered priority
max_concurrent_proposals = 2                            # bounded by single-LO throughput
defer_classes = [                                       # AUQ categories that DEFER
    "approval", "waiver", "priority",
    "formal_artifact", "requirement",
    "destructive", "deployment", "blocking",
]
```

- `candidate_projects` — ordered list of `PROJECT-*` ids. The drive
  picks the **highest-priority unblocked** candidate at each event-driven
  re-entry. Single-project case is a 1-element list.
- `max_concurrent_proposals` — integer upper bound on simultaneous
  open NEW/REVISED bridge proposals for the active project. Bounded
  by single-LO throughput + serialized INDEX writes per the file-bridge
  protocol's atomic-update invariant.
- `defer_classes` — closed-vocabulary list of AUQ categories that, when
  observed on a NO-GO verdict's `auq_class:` marker (per
  `DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001`), cause the drive to park
  the project as DEFERRED and surface to owner.

**Project-selection algorithm** (per event-driven re-entry tick):

1. Filter `candidate_projects` for unblocked projects:
   - Has an active PAUTH covering at least one open WI in the project.
   - Has at least one open WI (not all retired/VERIFIED).
   - No currently-DEFERRED bridge thread under the project tagged with
     a `defer_class` in this drive's `defer_classes`.
2. Pick the first unblocked project from the ordered list.
3. If none unblocked, the drive is idle until the next event.

**Concurrency bound** (per pick):

1. Count open NEW/REVISED bridge threads under the picked project.
2. If count < `max_concurrent_proposals`, spawn one new
   proposal-authoring session (per dispatch-envelope substrate).
3. If count >= bound, the drive is idle for this project until a
   verdict reduces the open count.

**Event-driven re-entry (no background watch):**

The drive re-spins ONLY on bridge `INDEX.md` changes affecting its
target projects (reuses the WI-4296 dispatcher event-driven
substrate). There is no cadence-cron or background polling. This is
the S308 protection: no spawn fires without a real INDEX-state change.

**AUQ-class detection:**

When a NO-GO verdict file is added to `bridge/INDEX.md` under one of
the drive's target projects, the dispatcher reads the verdict file
and checks for an `auq_class:` header line. If present AND the value
is in this drive's `defer_classes`, the drive marks the project as
DEFERRED (via a `DEFERRED` bridge entry per
`.claude/rules/file-bridge-protocol.md` § DEFERRED Status) and
surfaces the project + the auq_class category to owner via the
standard AUQ-surfacing path.

**Termination + retirement:**

Per `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`, a project
auto-retires when all its open WIs reach `resolution_status=verified`.
The drive observes the retirement event (a MemBase
`project_lifecycle_events` row, or equivalent) and removes the
project from `candidate_projects` at the next tick (or stops if the
list becomes empty).

**Termination idempotency:**

The drive's tick is idempotent: re-running the same tick on the same
INDEX state produces no new spawns (the project-selection +
concurrency-bound logic already account for in-flight proposals).
This is required for the dispatcher's at-least-once event delivery
semantics.

**Single-LO-throughput invariant:**

`max_concurrent_proposals` MUST be tuned to honor LO's effective
verdict-authoring rate. A naive cap of 10+ would queue verdicts past
LO's response window and accumulate stale NEW threads in INDEX.
Default sane value: 2. Owner may tune per-rule via the rule TOML.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `config/dispatcher/rules.toml` contains at least one rule
   with `target = "auto-drive-project"` once WI-4301 implementation
   lands. Expected-failing until then.
2. `grep_absent` — no other automation script duplicates the
   project-completion drive logic. (Cross-checks against
   `archive/smart-poller-2026-05-09/` and any other archived
   auto-drive substrates.)

## Spec Body — DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001 (draft)

**Title:** Bridge-Verdict AUQ-Class Marker Contract.

**Type:** design_constraint.

**Status (at insertion):** specified.

**Body:**

Bridge NO-GO verdict files MUST carry an `auq_class:` header field
when the NO-GO blocks on an owner-AUQ-required decision. The marker
is consumed by the project-completion drive (per
`SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001`) and by future
AUQ-surfacing automation.

**Marker placement:**

The `auq_class:` line appears in the bridge file's metadata block
(the upper portion before `## Verdict` or equivalent prose), in the
same region as `bridge_kind:`, `Document:`, `Version:`, etc.

**Closed vocabulary (8 categories):**

| Category | Triggered when the NO-GO requires owner |
|----------|-----------------------------------------|
| `approval` | grant of explicit approval for the proposed change |
| `waiver` | acknowledgement that a normally-required gate is being skipped |
| `priority` | choice between mutually-exclusive priorities |
| `formal_artifact` | formal-artifact-approval packet creation/signature |
| `requirement` | clarification or revision of a cited requirement |
| `destructive` | confirmation for a destructive operation (delete, force-push, drop) |
| `deployment` | confirmation for a deployment step (stage, production, smoke) |
| `blocking` | a blocking decision that doesn't fit the other 7 categories |

The vocabulary is closed: new categories require a separate DCL
amendment. The dispatcher MUST reject unknown values at parse time.

**Format:**

```text
auq_class: <one of the 8 values>
```

Single line; no quotes; lowercase. Exactly one `auq_class:` line per
NO-GO file when applicable. NO-GO verdicts that DO NOT require owner
AUQ omit the field entirely (absence is the "not AUQ-class" signal).

**Cross-harness applicability:**

The marker is a verdict-author obligation that applies to BOTH Claude
Code Loyal Opposition and Codex Loyal Opposition. Both harnesses MUST
include the marker on AUQ-class NO-GOs. The cross-harness rule update
lands as an implementation step under WI-4301 (envelope-program
implementation umbrella) — specifically:

1. Update `templates/bridge/no-go-verdict.md` to include an
   `auq_class:` slot with vocabulary comment.
2. Update `.claude/rules/loyal-opposition.md` and `AGENTS.md` (Codex)
   with the marker obligation.
3. Update the bridge-compliance-gate hook to validate the marker
   value when present (closed vocabulary).
4. Provide a deterministic auq_class-detection helper (read NO-GO
   metadata, return value or None).

**Compatibility with existing NO-GO verdicts:**

Existing NO-GO verdicts in `bridge/` (pre-`DCL-...-001` insertion)
DO NOT carry the marker. The dispatcher MUST treat absent marker as
"not AUQ-class" (the safe default that does NOT trigger DEFERRED
parking; instead the project-completion drive treats the project as
unblocked at re-entry, which lets normal REVISED re-entry proceed).
No retroactive update of legacy NO-GO files is required.

**Assertions** (machine-checkable; shipped at `status=specified`):

1. `grep` — `templates/bridge/no-go-verdict.md` includes an
   `auq_class:` slot once WI-4301 implementation lands. Expected-
   failing until then.
2. `grep` — `.claude/hooks/bridge-compliance-gate.py` references
   `auq_class` validation logic once WI-4301 implementation lands.

**Owner directive citation:** "S-2026-06-04 owner grilling: formalize
envelope program (WI-3468)" (per WI-4297 `source_owner_directive`).

**Related deliberations:** `DELIB-20260635`, `DELIB-20260637`,
`DELIB-20260648`, `DELIB-2238`, `DELIB-2500`.

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
No follow-on post-impl report or VERIFIED verdict is required for
the spec/DCL-body approval step.

The downstream MemBase insertions are verified at their own gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001 --json

groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type design_constraint --id DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001 --json
```

Each MUST return one row at version 1 with body fingerprints matching
the respective formal-artifact-approval packets. The verification
runs at *spec-insertion* time, not at this bridge thread's review
time.

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics:** `bridge/INDEX.md` has `NEW: ...-001.md` at
   the top of the `gtkb-project-completion-drive-payload-001`
   document entry; the file exists on disk; first line is the
   canonical `NEW` status token.
2. **Applicability preflight:** `python scripts/bridge_applicability_preflight.py
   --bridge-id gtkb-project-completion-drive-payload-001` returns
   `preflight_passed: true`, `missing_required_specs: []`.
3. **Clause preflight:** `python scripts/adr_dcl_clause_preflight.py
   --bridge-id gtkb-project-completion-drive-payload-001` returns
   `Blocking gaps: 0`.
4. **Project linkage:** `Project Authorization`, `Project`, and
   `Work Item` metadata point at the active PAUTH and the live work
   item; the WI is in the PAUTH's `included_work_item_ids`.
5. **Dependency closure:** WI-4297 depends on WI-4296 (per the
   `depends_on_work_items` field). WI-4296's sibling proposal
   (`bridge/gtkb-envelope-dispatch-element-001-001.md`, NEW, this
   session) carries the dispatch-envelope schema this payload spec
   integrates with. Reviewer confirms the forward references to
   `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` and
   `DCL-DISPATCH-ENVELOPE-RULES-001` are coherent.
6. **Phantom-spec sweep:** every cited SPEC / GOV / ADR / DCL / PB id
   in this proposal exists in the live `specifications` table, except
   the two artifacts being created here and the two sibling
   forward-references.
7. **AUQ vocabulary closure:** the 8 closed categories are
   exhaustive of in-scope-decision-class types per
   `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the
   Only Valid Owner-Decision Channel". Reviewer confirms each
   category maps to a documented AUQ trigger.
8. **No KB mutation in scope:** `kb_mutation_in_scope: false`; no
   `groundtruth.db` write is performed by this thread.

## Risk / Rollback

This proposal writes one file
(`bridge/gtkb-project-completion-drive-payload-001-001.md`) and
inserts one entry pair (`Document:` + `NEW:`) in `bridge/INDEX.md`.
Rollback is a single `git restore` of `bridge/INDEX.md` and `rm` of
the versioned file (or a WITHDRAWN follow-on). The downstream
spec/DCL insertions (under the approval-packet path) are separate,
gated operations governed by `GOV-ARTIFACT-APPROVAL-001`.

The DCL imposes a forward obligation on LO verdict authors (include
`auq_class:` on AUQ-class NO-GOs). Until WI-4301 lands the rule and
template updates, LO authors will not yet uniformly include the
marker — the dispatcher's compatibility clause (treat absent marker
as "not AUQ-class") preserves correctness during the transition.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the `gtkb-project-completion-drive-payload-001`
document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical
workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — this bridge proposal is governance documentation; no
source / test / hook / configuration code is modified by this
thread.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
