REVISED
::init gtkb lo
::open build

# Slice 1 REVISED — Scope-Glob Correction Only (design unchanged)

bridge_kind: prime_proposal
Document: gtkb-session-role-attestation-service-slice-1
Version: 003
Author: Prime Builder (harness B)
Date: 2026-08-14 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 2da3617e-95da-4957-bd9e-c277c7c6d051
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword. Same authoring transcript as -001 (runtime session id changed at an owner model switch; pre-switch id c78a4e67-7799-4284-b540-72ede994027f).

Responds to: bridge/gtkb-session-role-attestation-service-slice-1-002.md

Work Item: WI-6213
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/*.py", "groundtruth-kb/src/groundtruth_kb/session/**/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/*.py", "groundtruth-kb/src/groundtruth_kb/bridge/**/*.py", "scripts/_kb_attribution.py", "scripts/session_self_initialization.py", "platform_tests/**/*.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## What changed relative to the GO'd `-001` (and only this)

The `target_paths` array gains two direct-child patterns:
`groundtruth-kb/src/groundtruth_kb/session/*.py` and
`groundtruth-kb/src/groundtruth_kb/bridge/*.py`. Nothing else changes: the
design, scope items 1–6, slice ordering, verification plan, specification
links and out-of-scope list of `-001` stand exactly as approved by `-002`.

**Why.** The approved globs use the `dir/**/*.py` form, and under the
gate's fnmatch semantics `**/` requires at least one subdirectory level —
so the globs EXCLUDE direct children of `session/` and `bridge/`. The
consumers scope item 4 names are direct children:
`groundtruth-kb/src/groundtruth_kb/bridge/verdict_filing.py` is exactly
where the verdict-filing repoint must land, and the implementation-start
gate correctly denied the edit as outside packet scope ("Target path
outside implementation authorization scope"). The proposal's own globs
therefore structurally excluded the work the proposal ordered.

**Evidence.** Live gate denial this session on the `verdict_filing.py`
edit under packet `2026-08-14T04:59:57Z`; the same pitfall independently
forced the attestation module into a `session/attestation/` subpackage
(direct-child placement did not match) — which incidentally is the better
design, and is retained.

## Progress already landed under the `-002` GO (within the approved scope)

- `e36f5d804` — attestation core: `groundtruth_kb/session/attestation/`
  (immutable exact-init binding + append-only role attestations + the one
  canonical resolver with no fallback authority), 19 spec-derived tests
  green (`platform_tests/scripts/test_session_role_attestation.py`).
- `02998ea2f` — `scripts/_kb_attribution.py` repointed attestation-first
  with the typed `no_session_binding` migration fallthrough.

Remaining after re-GO: verdict-filing repoint (draft prepared),
`session_self_initialization` init-wiring (`bind_exact_init` beside the
role-marker write), consumer tests, the GOV-20 ADR under its own
per-artifact approval packet, and the implementation report.

## Specification Links

Unchanged from `-001`, carried forward in full:
`DCL-SESSION-ROLE-RESOLUTION-001` v8; `DCL-INIT-BOUND-SESSION-IDENTITY-001`
v1; `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v4;
`GOV-FILE-BRIDGE-AUTHORITY-001` v4;
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1;
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5; `GOV-20` v2;
`GOV-ARTIFACT-APPROVAL-001` v4; `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
v1; `GOV-STANDING-BACKLOG-001` v5; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`;
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`.

## Requirement Sufficiency

Existing requirements sufficient (unchanged from `-001`): the slice
implements `DCL-SESSION-ROLE-RESOLUTION-001` v8 and
`DCL-INIT-BOUND-SESSION-IDENTITY-001` as specified; no new or revised
requirement is needed for the glob correction, which is packet-scope
metadata, not behavior.

## Spec-Derived Verification Plan

Unchanged from `-001`. Already partially discharged:
`test_session_role_attestation.py` covers the exact-init transaction
clauses 1–6 (four valid forms create; eight invalid forms create nothing;
repeat init is a typed rejection with no second ID), resolver typed
failures and at-time semantics, and append-only chained role change.
Consumer-repoint tests land with the repoints.

## Owner Decisions / Input

Unchanged from `-001` (the LO-advisory grilling-gate AUQ evidence carried
there). No new owner decision is required for this glob correction; the
GOV-20 ADR retains its own future per-artifact approval packet
requirement.

## Prior Deliberations

Unchanged from `-001`, plus: the live gate denial recorded in commit
`02998ea2f`'s message; the same-pitfall occurrences in
`bridge/gtkb-baseline-correction-and-goose-projector-slice-1-005.md`
(observations) — three independent reproductions of the `**/`
direct-child exclusion this session, supporting a future lint on
`target_paths` glob forms (candidate backlog item, not this slice).

## Risk / Rollback

The correction widens packet scope to files the proposal always named in
prose; it grants nothing new in kind. Rollback: the two added patterns
simply lapse with the packet; landed commits are unaffected.

## Recommended Commit Type

Unchanged: `feat` for the remaining increments.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
