REVISED

bridge_kind: governance_review
Document: gtkb-session-envelope-durability-001
Version: 003
Author: Prime Builder (Codex, harness A; acting Prime Builder per automation prompt)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-session-envelope-durability-001-002.md

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-04
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Keep Working PB

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297
Project: PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT
Work Item: WI-4293
Recommended commit type: docs

target_paths: []

implementation_scope: governance_review_spec_drafting
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Revision Claim

This revision corrects the session-envelope durability model after the NO-GO at
`bridge/gtkb-session-envelope-durability-001-002.md`. The authoritative session
envelope is no longer a shared `.claude/session/envelope.json` file. The
authoritative current-state surface is per harness:

- `harness-state/codex/session-envelope.json`
- `harness-state/claude/session-envelope.json`
- `harness-state/antigravity/session-envelope.json`

More generally, writers resolve the harness name from
`harness-state/harness-identities.json` and
`harness-state/harness-registry.json`, then write
`harness-state/<harness_name>/session-envelope.json`.

The shared `.claude/session/envelope.json` surface, if generated, is a
non-authoritative projection for dashboards, startup disclosure, or human
inspection. It must never be treated as the write target for active session
state and must never be the source of truth for concurrent harness lifecycle
decisions.

This remains a governance-review proposal only. It performs no MemBase mutation
and executes no KB writes. The actual `DCL-SESSION-ENVELOPE-DURABILITY-001`
insertion is a downstream formal-artifact approval operation under the active
PAUTH's `approval_packet_creation` mutation class.

## Revised DCL Body

`DCL-SESSION-ENVELOPE-DURABILITY-001` v1 shall specify the following durability
contract.

### Authoritative State

The active session-envelope state is authoritative only in the per-harness file
under `harness-state/<harness_name>/session-envelope.json`.

The `<harness_name>` segment is the host-local harness key, currently
`codex`, `claude`, or `antigravity`, resolved from the durable harness identity
and registry records:

- `harness-state/harness-identities.json`
- `harness-state/harness-registry.json`

Each harness writes only its own per-harness state file. A Codex session writes
`harness-state/codex/session-envelope.json`; a Claude Code session writes
`harness-state/claude/session-envelope.json`; an Antigravity session writes
`harness-state/antigravity/session-envelope.json`.

### Non-Authoritative Projection

`.claude/session/envelope.json` MAY exist only as a generated projection. If it
exists, it is a read-mostly summary assembled from the authoritative
per-harness files. It must be labeled non-authoritative in documentation and
must not be used as the mutation target for startup, wrap, topic close, or
dispatch lifecycle writes.

The projection may be omitted entirely. Omission of the projection must not
affect session-envelope correctness, because correctness is defined by
`harness-state/<harness_name>/session-envelope.json`.

### Schema

The per-harness session-envelope JSON object contains:

- `envelope_schema_version`: integer schema version. v1 is the initial schema.
- `harness_id`: durable installation ID from `harness-identities.json`.
- `harness_name`: host-local harness key such as `codex`, `claude`, or
  `antigravity`.
- `subject`: resolved session subject, such as `gtkb` or `application`.
- `role`: resolved operating role for the session; nullable when an accepted
  init keyword omits a role token.
- `init_keyword`: raw owner or dispatch prompt that opened the session
  envelope.
- `opened_at`: UTC timestamp for the session-envelope open event.
- `closed_at`: UTC timestamp for the close event, or null while open.
- `wrap_outcome`: wrap outcome, or null while open.
- `status`: `open`, `closed`, or `error`.
- `topics`: array of topic-envelope records.
- `last_error`: nullable diagnostic object for malformed input, write failure,
  or recovery state.

Each topic-envelope record contains:

- `type`: closed topic type from the governed `::open <type>` vocabulary.
- `opened_at`: UTC timestamp for the topic open event.
- `closed_at`: UTC timestamp for the topic close event, or null while open.
- `close_outcome`: explicit close outcome; open topics closed by session wrap
  record `auto_closed_by_session_wrap`.
- `preload_state`: topic preload or context state.
- `route_target`: routing target used by dispatch or topic handoff, if any.

Writers always emit the latest schema version. Readers normalize older archived
versions on load without rewriting the archive unless an explicit migration is
approved.

### Lifecycle

On accepted `::init`, the active harness opens or refreshes only its
per-harness `session-envelope.json`. Opening a new envelope while a prior
envelope remains open requires deterministic recovery behavior: either close
the prior envelope with a documented recovery outcome or refuse the new open
with an owner-visible diagnostic, according to the implementation proposal for
the writer.

On `::wrap`, the active harness:

1. Reads only its own `harness-state/<harness_name>/session-envelope.json`.
2. Sets `closed_at` and `wrap_outcome`.
3. For every open topic in `topics`, sets `closed_at` and
   `close_outcome=auto_closed_by_session_wrap`.
4. Archives the closed envelope under
   `harness-state/<harness_name>/session-envelope-archive/<closed_at-ISO>-session-envelope.json`.
5. Clears or replaces the current per-harness state so the next accepted
   `::init` opens a fresh envelope.
6. Optionally regenerates the non-authoritative `.claude/session/envelope.json`
   projection.

The archive trail is append-only at the per-harness archive location. A schema
version bump requires a new DCL version.

### Write Safety

Per-harness writes use atomic replacement: write a complete temporary file in
the same directory, flush it, and rename it over the current
`session-envelope.json`. The per-harness layout is the primary concurrency
control; atomic replacement protects each individual file from partial writes.

No implementation may rely on a shared `.claude/session` directory being unique
per harness. Current GT-KB precedent keeps shared work-subject state under
`.claude/session/` and per-harness lifecycle guards under `harness-state/`.
This DCL follows the per-harness lifecycle-guard precedent.

## Specification Links

**Cross-cutting blocking specs:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) - governs append-only bridge
  versioning and INDEX-canonical state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) -
  this Specification Links section satisfies the linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) -
  `Project:` and `Project Authorization:` metadata cite the active PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - governs
  the verification mapping below.
- `GOV-STANDING-BACKLOG-001` v5 (verified) - WI-4293 is the governing backlog
  item and is covered by the active PAUTH.
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) - governs the downstream
  formal-artifact approval packet for inserting
  `DCL-SESSION-ENVELOPE-DURABILITY-001`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) and
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` v1 (specified) - govern the PAUTH
  envelope cited in this proposal.

**Cross-cutting advisory specs:**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposed DCL is a governed
  artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - cited explicitly because the
  applicability preflight on `-001` reported it as missing advisory coverage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - net-new DCL creation is a lifecycle
  event covered by the PAUTH's allowed mutation classes.

**Coupled specs and surfaces not modified by this proposal:**

- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 (specified) - provides the
  accepted init-keyword values recorded by the envelope.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 (specified) - provides the
  current keyword syntax driving `init_keyword`.
- `bridge/gtkb-canonical-wrap-keyword-syntax-001-001.md` - sibling WI-4292
  proposal; depends on this DCL for open-topic auto-close semantics.

**Spec drafted by this proposal:**

- `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 - revised body in this proposal.

## Prior Deliberations

- `DELIB-20260636` - envelope-program grilling and project-home authority.
- `DELIB-20260637` - envelope meta-model and topic-envelope shape.
- `DELIB-20260648` - envelope-program PAUTH authorization and
  subject-mandatory / role-optional clarification.
- `DELIB-2238` - originating session-envelope fields:
  `opened_at`, `init_keyword`, `subject`, `role`, `closed_at`,
  `wrap_outcome`.
- `DELIB-2500` - originating envelope convention; this revision preserves the
  convention while correcting the storage authority to avoid shared-file
  contention.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-29-07-12-delib-2500-envelope-convention-advisory.md`
  - prior Loyal Opposition advisory recommending authoritative
  `harness-state/<harness>/session-envelope.json` plus optional
  non-authoritative `.claude/session/envelope.json` projection.

## Owner Decisions / Input

No new owner decision is required for this revision. The revision preserves the
owner-grilled envelope fields, lifecycle, schema-evolution rule, and
`::wrap` topic auto-close behavior from WI-4293, DELIB-20260636,
DELIB-20260637, DELIB-20260648, DELIB-2238, and DELIB-2500. It changes only the
state authority model to satisfy the Loyal Opposition NO-GO finding by aligning
the DCL with existing per-harness lifecycle-guard precedent.

## Findings Addressed

### F1 - P1 - Shared `.claude/session/envelope.json` authority

Resolution: replaced shared-file authority with per-harness authority under
`harness-state/<harness_name>/session-envelope.json`. The revised DCL states
that each harness writes only its own file and that `.claude/session/envelope.json`
is optional, generated, and non-authoritative.

### Missing advisory `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`

Resolution: added `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` to the advisory
Specification Links set and cited the prior artifact-oriented advisory report
as supporting evidence.

## Scope Changes

The governance-review scope remains unchanged:

- no source-code mutation;
- no hook mutation;
- no test mutation;
- no MemBase mutation in this bridge revision;
- downstream insertion remains a formal-artifact approval operation under the
  active PAUTH.

The substantive DCL-body change is the storage authority correction:
authoritative current state and archive are per harness under `harness-state/`;
shared `.claude/session/envelope.json` is non-authoritative projection only.

## Bridge Filing And INDEX Update

This revision is filed as
`bridge/gtkb-session-envelope-durability-001-003.md`. The bridge helper inserts
`REVISED: bridge/gtkb-session-envelope-durability-001-003.md` at the top of the
`Document: gtkb-session-envelope-durability-001` entry in `bridge/INDEX.md`.
No prior bridge version is deleted or rewritten; the bridge/INDEX.md entry is
the canonical workflow state.

## Pre-Filing Preflight Subsection

This completed revision is filed through
`.claude/skills/bridge/helpers/revise_bridge.py file`, which runs both
candidate-content gates before writing the live `REVISED` file:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-envelope-durability-001 --content-file <candidate> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-envelope-durability-001 --content-file <candidate>
```

The revision must not be filed unless both gates pass.

## Specification-Derived Verification Plan

Because this is a `governance_review` bridge thread with
`requires_verification: false`, GO is terminal for review of the DCL body. The
downstream formal-artifact approval packet verifies insertion of
`DCL-SESSION-ENVELOPE-DURABILITY-001` v1.

No `python -m pytest`, `pytest`, or `ruff` command is required for this bridge
revision because it changes no source code, hook code, test file, or MemBase
row. The executed verification for this revision is the bridge applicability
preflight and ADR/DCL clause preflight against the completed candidate content.

Expected downstream evidence:

| Linked Spec | Verification Evidence Expected |
|---|---|
| `DCL-SESSION-ENVELOPE-DURABILITY-001` v1 | Live MemBase row exists after formal-artifact approval; description includes per-harness authoritative state, non-authoritative projection, schema, lifecycle, archive, and atomic-replace write safety. |
| `GOV-ARTIFACT-APPROVAL-001` v3 | Formal-artifact approval packet exists and its body hash matches the inserted DCL body. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v2 and `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v2 | Remain unchanged by this thread. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and project-linkage specs | This bridge revision, the INDEX entry, PAUTH metadata, and Specification Links section provide evidence. |

## Risk And Rollback

Risk is low because this is a governance-review revision and does not mutate
source code, hooks, tests, or MemBase rows. The main risk is terminology drift
between the original owner phrase "single envelope.json" and the revised
per-harness authority. This is mitigated by preserving the single-envelope
shape per harness and allowing an optional aggregate projection for human
inspection.

Rollback is append-only. If Loyal Opposition still finds the DCL body
insufficient, Prime Builder files a later `REVISED` version addressing the
remaining finding. Because no MemBase mutation occurs in this bridge revision,
there is no database rollback.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
