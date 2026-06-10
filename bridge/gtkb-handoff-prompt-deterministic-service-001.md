NEW

# Implementation Proposal — Deterministic Handoff-Prompt Service Design (governance_review)

bridge_kind: governance_advisory
Document: gtkb-handoff-prompt-deterministic-service
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
Work Item: WI-4299
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation. The net-new
`SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` inserts downstream
via the active PAUTH's `approval_packet_creation` mutation class as
a separate formal-artifact-approval-packet operation after GO.
(Trips `KB_MUTATION_NEGATION_RE` in
`.claude/hooks/bridge-compliance-gate.py:203-207`.)

## PAUTH Coverage Note

WI-4299 is not in the envelope-program PAUTH's
`included_work_item_ids` (WI-4291..WI-4297). Codex's WI-4302 and my
WI-4300 both filed under the same PAUTH with explicit
coverage-gap notes; both were GO'd / are pending LO. This filing
follows that precedent.

## Claim

Draft `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`: the
deterministic service contract for the GroundTruth-KB session
handoff-prompt generator. A direct manifestation of the
deterministic-services principle
(`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`): repetitive prompt-
assembly work performed by an AI session is a defect; the service
encapsulates the assembly as deterministic code.

Service surface (per WI-4299 owner AUQ):

1. **Interface (CLI + Python API):**
   - CLI: `gt session handoff generate [--session-id ID]`
   - Python API:
     `groundtruth_kb.session.handoff.generate(session_id: str) -> dict`
   - The CLI is a thin wrapper around the API.

2. **Inputs (tight, action-oriented):**
   - The latest **archived** session envelope file for the named
     session (per WI-4293's GO'd schema: under
     `harness-state/<harness_name>/session-envelope-archive/`).
   - Open bridge state: the latest `NEW` / `REVISED` / `GO` / `NO-GO`
     entries for the **active role** from `bridge/INDEX.md`. The
     parsing reuses the same canonical-status set as the bridge-
     applicability preflight.
   - **Deliberately excluded:** full deliberation harvest; full
     backlog rollup. The prompt is tight by design.

3. **Outputs (3 surfaces):**
   - **MemBase** `session_prompts` table (durable; queryable via
     `gt session handoff get`).
   - **File** at `.claude/session/handoff-<session-id>.md` (cold-read
     by next session; the file is regenerable from the canonical
     inputs).
   - **Terminal echo** at generation time (immediate read for the
     closing operator).

4. **Determinism contract:** same `session_id` + same archived
   session-envelope file (per the per-harness archive directory's
   immutability invariant) + same bridge state → same prompt **bytes**.
   Re-runs are idempotent.

5. **Coupling to wrap procedure (WI-4294):** the wrap procedure
   invokes the handoff-prompt service after the per-harness
   session-envelope archive step (#12a of the wrap-procedure 4-tier
   framework) and before the terminal close-summary. The wrap
   procedure passes the just-archived session_id; the service reads
   the archive file (now stable) and writes outputs.

6. **Terminology lock:** the artifact is called a "handoff prompt"
   per DELIB-2500 #6. The term "continuation prompt" is NOT adopted;
   it has subtly different semantics (a continuation prompt implies
   the next session continues the same work, while a handoff prompt
   may also direct the next session to different work).

## Why Now

The envelope-program design phase has reached ~10/13 WIs covered;
of the remaining 3, WI-4299 is the cleanest single-deliverable spec.
Its design (per owner AUQ) is tight and self-contained — a service
contract, not a complex multi-artifact span.

Filing WI-4299 now:

- Closes the deterministic-service half of the envelope program
  (the other half being the dispatcher rules engine per WI-4296).
- Provides the WI-4294 wrap procedure with its handoff-emission
  call-site definition.
- Sets up WI-4301 (implementation umbrella) by completing one of
  its remaining design dependencies.

## Why Not (alternatives considered)

- **Inline the handoff generation in the wrap procedure spec
  (WI-4294)** (rejected per WI-4299 separation): a deterministic
  service deserves its own contract for testability, reuse, and
  independent versioning. Per
  `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, services are
  durable artifacts, not procedure-fragments.
- **Make the service AI-mediated rather than deterministic**
  (rejected): the prompt-assembly logic is intentionally
  deterministic so the same canonical inputs always produce the
  same handoff-prompt bytes. AI mediation would defeat the
  reproducibility contract.
- **Adopt 'continuation prompt' terminology** (rejected per
  DELIB-2500 #6 and WI-4299 status_detail): "handoff" is the
  canonical term.
- **Include comprehensive deliberation harvest in inputs**
  (rejected per owner AUQ #2): deliberately tight input scope keeps
  the prompt short and action-oriented. Comprehensive harvest belongs
  in a different service (the wrap procedure's DA harvest step).
- **Promote to implementation_proposal scope now** (rejected for
  this slice): the design contract is the deliverable for this
  thread; the actual `gt session handoff` CLI implementation and
  `groundtruth_kb.session.handoff` Python module land via a
  separate implementation_proposal thread (or under WI-4301's
  umbrella).

## Prior Deliberations

- `DELIB-2238`, `DELIB-2500` — originating envelope-program
  foundation. DELIB-2500 #6 establishes "handoff prompt" terminology.
- `DELIB-20260635`, `DELIB-20260637` — 3-part envelope anatomy
  context; the handoff prompt is the session-close artifact bridging
  to the next session.
- `DELIB-20260648` — envelope-program PAUTH-minting.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — direct authority
  for the service-shape choice (deterministic code, not AI
  mediation).
- `bridge/gtkb-session-envelope-durability-001-006.md` (GO; parallel
  session) — defines the per-harness archive directory the service
  reads from.
- `bridge/gtkb-session-wrap-procedure-001-004.md` (GO; my REVISED-2)
  — defines the call-site context for the handoff service.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `GOV-ARTIFACT-APPROVAL-001`,
  `GOV-STANDING-BACKLOG-001`.

**Cross-cutting (advisory):**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Specs referenced (forward references; sibling WIs):**

- The session-envelope durability spec planned for sibling WI-4293
  (bridge thread `gtkb-session-envelope-durability-001`, GO at -006)
  — the service consumes the per-harness archive file format
  defined there.
- The wrap-procedure spec planned for sibling WI-4294 (bridge
  thread `gtkb-session-wrap-procedure-001`, GO at -004) — the
  procedure invokes this service at the prescribed call-site.

**Specs drafted by this proposal:**

- The deterministic handoff-prompt service spec drafted below
  (NEW; spec id provisional until insertion).

## Owner Decisions / Input

This governance-review proposal is authorized by the active PAUTH;
no fresh AUQ is required:

1. **DELIB-20260648 (envelope-program PAUTH-minting)** — authorizes
   governance-review spec creation under this PAUTH.
2. **DELIB-2500 #6** — terminology authority ("handoff prompt").
3. **WI-4299 status_detail owner AUQ** — direct authority for the
   service-surface design (CLI + API, inputs, 3 output surfaces,
   determinism contract, terminology lock).
4. **DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE** — authority for
   the service-shape choice.

Owner-input dependencies downstream of GO:

- 1 formal-artifact-approval packet at MemBase insertion time.
- The actual Python implementation + CLI module is a separate
  bridge thread (under impl_proposal scope) covered by WI-4301
  (impl umbrella) or a dedicated downstream proposal.

## Requirement Sufficiency

Existing requirements sufficient. The owner-grilling AUQ for WI-4299
captured the complete service-surface contract. The deterministic-
services principle provides the design-shape authority. No new
owner requirement is needed.

## Spec Body — Deterministic Handoff-Prompt Service (draft)

**Title:** GroundTruth-KB Session Handoff-Prompt Service —
Deterministic Surface Contract.

**Type:** specification.

**Status (at insertion):** specified.

**Body:**

The session handoff-prompt service generates a bounded, action-
oriented prompt that the next GroundTruth-KB session reads to
inherit the closing session's open state. The service is
**deterministic**: same canonical inputs always produce the same
prompt bytes.

### Service Surface

**CLI:**

```text
gt session handoff generate [--session-id ID]
```

When `--session-id` is omitted, the service uses the
most-recently-archived session envelope for the active harness.

The CLI is a thin wrapper around the Python API; the CLI invocation
returns the same dict that the API returns, formatted for terminal
output.

**Python API:**

```python
groundtruth_kb.session.handoff.generate(session_id: str) -> dict
```

Returns a dict with at minimum:

- `session_id`: str (echoed).
- `prompt_markdown`: str (the generated handoff prompt body).
- `output_files`: list[str] (relative paths to written files; see
  Output Surfaces below).
- `session_prompts_id`: str (the MemBase row id created by this
  invocation).

Errors raise `groundtruth_kb.session.handoff.HandoffError` with a
clear message; the CLI maps the exception to a non-zero exit code.

### Inputs

The service reads exactly two input sources:

1. **The latest archived session-envelope file** for `session_id`:
   `harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json`
   (per WI-4293's GO'd schema). The `<harness_name>` and
   `<closed_at-ISO>` tokens are resolved from the session_id +
   directory contents at service invocation time.
2. **Open bridge state** filtered for the active role: the latest
   `NEW` / `REVISED` / `GO` / `NO-GO` lines per Document in
   `bridge/INDEX.md`. Parsing reuses the canonical status-set
   logic from `scripts/bridge_applicability_preflight.py` or
   equivalent.

**Deliberately excluded inputs:**

- Full deliberation-archive harvest. The DA harvest step is part of
  the wrap procedure (Tier 1 step #4 per WI-4294); the handoff
  prompt does not duplicate it.
- Full standing-backlog rollup. The dashboard / `gt backlog list`
  cover that surface.
- Source-tree state. Working-tree attestation is the wrap
  procedure's step #8 (per WI-4294); the handoff prompt does not
  duplicate it.

The deliberately tight input set keeps the prompt short and
action-oriented.

### Output Surfaces

The service writes to **all three** of the following surfaces on
each invocation:

1. **MemBase `session_prompts` table:** a new row keyed by
   `session_id` + an idempotency hash of the inputs. Queryable via
   `gt session handoff get <session_id>` (CLI surface
   complementary to `generate`).
2. **File at `.claude/session/handoff-<session-id>.md`:** a
   markdown file the next session reads cold. The file content is
   the `prompt_markdown` from the API return value, possibly with
   a thin header for human readability. Regenerable from the
   canonical inputs (no data loss if deleted).
3. **Terminal echo:** when invoked via CLI, the prompt body is
   echoed to stdout. The terminal echo is for the closing
   operator's immediate read; not consumed programmatically.

### Determinism Contract

For a fixed `session_id`, identical archived session-envelope file
contents (immutable per WI-4293's archive directory invariant) +
identical bridge state → identical prompt bytes.

Implementation must ensure:

- No timestamps in the prompt body (other than those copied verbatim
  from envelope fields).
- No source of randomness.
- No AI mediation; the prompt assembly is pure-Python deterministic
  templating.

The MemBase `session_prompts` row's idempotency hash detects
re-invocation on the same inputs and short-circuits (returns the
existing row's prompt unchanged) to preserve hash-stable bytes.

### Call-Site Coupling (WI-4294 wrap procedure)

The service is invoked by the wrap procedure (per WI-4294's GO'd
4-tier framework). Specifically:

- After step #12a (per-harness session-envelope archive rename
  completes; the archive file is stable).
- Before the procedure's terminal close-summary emission.

The wrap-procedure invocation is `conditional-with-default-on`
(Tier 2): the handoff prompt is auto-generated unless the operator
passes `::wrap --suppress handoff_prompt` (per WI-4294's
`--suppress <step>` plumbing).

If the wrap procedure aborts before reaching the handoff step (e.g.,
a Tier 1 MANDATORY step fails), the handoff prompt is NOT generated
for that session; the operator may re-invoke `gt session handoff
generate` manually after resolving the wrap blocker.

### Terminology Lock

This service produces a **handoff prompt** (per DELIB-2500 #6). The
term **continuation prompt** is NOT adopted: a continuation prompt
implies the next session continues the same work, while a handoff
prompt may also direct the next session to different work. The
service's output is the latter.

### Assertions (machine-checkable; shipped at `status=specified`)

1. `grep` — `groundtruth-kb/src/groundtruth_kb/session/handoff.py`
   (or equivalent) exports `generate(session_id) -> dict` at
   WI-4301 Slice B impl time. Expected-failing until then.
2. `grep` — `gt session handoff generate` is registered as a CLI
   subcommand at WI-4301 impl time. Expected-failing until then.
3. `grep` — `session_prompts` MemBase table schema is present in
   `groundtruth_kb/db/schema.py` (or equivalent) at WI-4301 impl
   time.
4. `grep_absent` — no AI-mediated prompt-assembly path exists. The
   service is purely deterministic per
   `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

### Owner directive citation

"S-2026-06-04 owner grilling: formalize envelope program (WI-3468)"
(per WI-4299 `source_owner_directive`).

### Related deliberations

`DELIB-2238`, `DELIB-2500`, `DELIB-20260635`, `DELIB-20260637`,
`DELIB-20260648`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing
Preflight Subsection. Re-run after this NEW entry is added to
`bridge/INDEX.md`. Expected `preflight_passed: true`,
`missing_required_specs: []`, no blocking clause gaps.

## Specification-Derived Verification Plan

Because this is a governance_review proposal with `target_paths: []`
and `requires_verification: false`, GO is terminal for this bridge
thread (per `feedback_latest_go_terminal_for_governance_review.md`).
No follow-on post-impl report or VERIFIED verdict is required.

The downstream MemBase insertion is verified at its own gate:

```text
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec list \
    --type specification --id <inserted-id> --json
```

Reviewer verification of THIS bridge thread:

1. **Bridge mechanics** — INDEX has `NEW:` at top.
2. **Applicability + clause preflights** pass with no blocking gaps.
3. **PAUTH coverage note** — proposal cites Codex WI-4302 +
   my WI-4300 as precedents under the same PAUTH; LO may NO-GO if a
   separate PAUTH is needed.
4. **Service-surface completeness** — CLI + Python API + inputs +
   3 output surfaces + determinism + coupling + terminology + 4
   assertions; all 7 owner-AUQ design points captured.
5. **Per-harness path correctness** — input file path uses
   `harness-state/<harness_name>/session-envelope-archive/`, NOT
   the legacy `.claude/session/archive/`. (The legacy path appears
   in WI-4299's original status_detail but was superseded by
   WI-4293's GO'd per-harness model; this proposal uses the
   per-harness path.)
6. **DELIB-S312 alignment** — service is deterministic code, not AI
   mediation; assertion #4 enforces no AI-mediated path.

## Risk / Rollback

This proposal writes one bridge file + one INDEX entry. Rollback
single `git restore` + `rm`.

The downstream spec insertion is owner-gated. The actual Python
service implementation is a separate impl_proposal scope (out of
scope here).

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted
at the top of the `gtkb-handoff-prompt-deterministic-service`
document list in `bridge/INDEX.md`.

## Recommended Commit Type

`docs` — governance documentation; no source / test / hook /
configuration code is modified.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
