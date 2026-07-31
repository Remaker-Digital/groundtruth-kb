REVISED

# Revised Defect-Fix Proposal - WI-5252 Session Envelope CLI Provenance

bridge_kind: prime_proposal
Document: gtkb-wi5252-session-envelope-cli-provenance
Version: 003
Responds to: bridge/gtkb-wi5252-session-envelope-cli-provenance-002.md
Supersedes proposal: bridge/gtkb-wi5252-session-envelope-cli-provenance-001.md
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed bridge stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5252-SESSION-ENVELOPE-PROVENANCE-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5252
Test: TEST-11406

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_kb_attribution.py"]

## Revision Claim

Prime Builder accepts the version 002 P1 finding and takes recommended Option 1. WI-5252 will introduce one package-canonical parser in the already-authorized `groundtruth_kb.session.envelope` module and route the public CLI through it. It will not import from `scripts/`, add a CLI-local regex, or expand this focused repair into a five-script migration. WI-5309 / TEST-11452 now tracks migration of the existing script duplicates to the package parser.

The underlying defect remains unchanged: the public CLI can open a role-resolved interactive successor but cannot create validated `worker_role_provenance`, so governed writers reject it unless an operator uses a private API and exact environment rebinding.

## Findings Addressed

### F1 - No importable canonical parser exists inside the package

Accepted. Add the single package-canonical parser to `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, which is already in `target_paths`. The parser implements the current `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` grammar exactly: subject is `gtkb|application`, role token is optional `pb|lo`, matching is first-line/full-string and synonym-free, and role tokens map only to `prime-builder|loyal-opposition`.

`cli_session_handoff.py` imports this parser. No `::init` regex or pb/lo map is added to the CLI module. A focused guard test asserts the CLI routes through the package parser and carries no duplicate grammar literal.

### F2 - Existing script consumers still duplicate the grammar

Accepted as follow-up scope. WI-5309 / TEST-11452 records migration of `session_self_initialization.py`, `cloud_harness_base.py`, `ollama_harness.py`, `session_start_dispatch_core.py`, and `workstream_focus.py` after WI-5252 establishes the package home. This revision does not edit those dirty/shared surfaces.

### F3 - Role-resolution source can disagree with validated provenance

Accepted. The CLI will reject an explicit `--role` unless `--init-keyword` is canonical, contains a role token, and maps to that exact role. A subject assertion, when supplied, must also match the parsed keyword subject. Therefore the CLI cannot write an envelope that labels an unvalidated explicit role as transcript-derived. Canonical role-free keywords remain allowed only on the non-authoritative role-free path and do not create worker provenance.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` already define the grammar, role semantics, and authoritative session-document requirement. This revision supplies the missing reusable parser and CLI binding without creating a new authority model.

## In-Root Placement Evidence

All five exact source/test targets are clean and inside `E:\GT-KB`. The package parser is placed in an already-authorized installable module; no out-of-root path, direct harness contact, raw envelope edit, dispatcher/runtime mutation, or script-package dependency inversion is introduced.

## Specification Links

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - defines the exact six-form subject-required, role-optional grammar and closed token vocabulary.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - requires receiver-side subject/role consistency for canonical keywords.
- `DCL-SESSION-ROLE-RESOLUTION-001` - a present role token establishes the interactive override; an absent token leaves durable-role fallback authoritative.
- `GOV-SESSION-ROLE-AUTHORITY-001` - only validated transcript evidence may create authoritative interactive worker-role provenance.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - governed mutations retain exact session, harness, and role attribution.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - the validated transcript role persists in the current interactive context without changing dispatcher defaults.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires independent GO, claim, start authorization, report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision carries the complete behavioral and cross-cutting set.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - TEST-11406 and the matrix below derive from the linked requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, test, and exact paths are machine-readable.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected edits remain exact-path and operation-time gated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - defect, NO-GO, revision, follow-up WI/test, implementation, and verdict remain durable and linked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation and evidence stay inside GT-KB.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces the complete bridge and source-write gates.
- `GOV-STANDING-BACKLOG-001` - WI-5252, WI-5256, and WI-5309 remain visible until their separate scopes are verified.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded repair of fleet bridge/harness defects while preserving every later implementation gate.
- `DELIB-20260648` defines subject-mandatory, role-optional canonical keyword semantics.
- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` protects closed predecessor session documents from shared-slot overwrite.
- `bridge/gtkb-wi5252-session-envelope-cli-provenance-002.md` supplies the accepted parser-placement finding.
- `bridge/gtkb-wi5256-codex-interactive-session-successor-002.md` separately GO'd ambient successor selection; WI-5252 does not absorb its targets.
- WI-5309 / TEST-11452 tracks migration of existing script-side parser duplicates.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the bounded proposal/PAUTH lifecycle.
- Recommended Option 1 is the least-regret focused correction and needs no new owner decision; it stays within the already-approved source/test paths and records the deferred migration as WI-5309.

## Proposed Scope

1. Add one exported package-canonical parser to `session/envelope.py`. It accepts exactly the full current grammar `::init (gtkb|application)( (pb|lo))?`, returns structured subject plus mapped role, and returns no match for whitespace variants, synonyms, extra lines, or extra tokens.
2. In `gt session envelope open`, parse `--init-keyword` only through that function. With an explicit `--role`, require a canonical role-bearing keyword whose mapped role matches exactly; if `--subject` is supplied, require exact parsed-subject agreement. Fail before any envelope write on absence, mismatch, or noncanonical input.
3. For a validated role-bearing keyword, call the existing structured API with `worker_role_source="transcript_init_keyword"`, producing complete `worker_role_provenance` in the generated successor document.
4. Preserve canonical role-free keyword opens only when no explicit role is asserted. They create no worker provenance and use durable-role fallback as required by the current syntax specification.
5. Preserve generated timestamped successor IDs and never overwrite the closed persistent-thread predecessor.
6. Keep direct API and dispatcher `ensure_worker_session` behavior unchanged, including `dispatcher_composition` and exact dispatch-run provenance.
7. Add parser matrix, CLI PB/LO, application-subject, role-free, mismatch, noncanonical, predecessor immutability, exact-successor attribution, and no-duplicate-CLI-grammar tests.
8. Keep WI-5256 as the prerequisite for the final ambient-thread/no-environment-rebinding writer test. Keep WI-5309 as the separate scripts-migration carrier.

## Explicit Exclusions

- No edit to any `scripts/*` parser consumer under WI-5252.
- No dispatcher/TAFE runtime, lease, lock, config, eligibility, routing, model, allowance, or role-registry mutation.
- No direct harness contact, raw session JSON mutation/deletion, credential lifecycle, external system mutation, destructive cleanup, push, deployment, release, or unrelated change.
- No adoption of foreign WI-5256 or parallel-session hunks.

## Specification-Derived Verification Plan

| Requirement | Deterministic verification |
| --- | --- |
| Exact canonical grammar | Parameterize all six valid forms and invalid whitespace/synonym/multiline/extra-token forms against the one package parser. |
| Role/subject consistency | CLI PB/LO and application/gtkb tests assert matching success; missing role token, role mismatch, subject mismatch, and noncanonical input fail before write. |
| Writer-usable authority | Matching role-bearing CLI opens assert complete `worker_role_provenance` with exact successor session, harness A, mapped role, source `transcript_init_keyword`, and null dispatch run id. |
| Role-free compatibility | Canonical role-free opens without explicit role create no worker provenance and retain durable fallback semantics. |
| Historical safety | Seed a closed persistent-thread predecessor; assert a distinct successor and byte-for-byte unchanged predecessor. |
| No grammar duplication | Assert `cli_session_handoff.py` imports/calls the package parser and contains no canonical regex or pb/lo mapping. |
| Dispatcher isolation | Existing `ensure_worker_session` tests retain `dispatcher_composition` and exact dispatch-run provenance. |
| Governed attribution | Resolve the exact returned successor to the expected `changed_by`; final ambient selection remains gated on WI-5256 VERIFIED. |
| Static/scope quality | Focused pytest, Ruff check/format, and exact five-path `git diff --check` pass. |

Minimum commands remain the three focused session/attribution pytest modules, Ruff check/format over the five paths, and exact-path `git diff --check`.

## Acceptance Criteria

- The package contains one canonical parser implementing all six specified forms and rejecting every noncanonical form.
- The CLI has no duplicate grammar or token map and creates authority only from exact parsed role/subject agreement.
- Matching role-bearing PB and LO opens produce complete writer-usable provenance in a distinct successor document.
- Role-free opens remain non-authoritative and use durable-role fallback.
- Closed predecessors remain unchanged; dispatcher-composed workers remain unchanged.
- WI-5309 / TEST-11452 durably tracks migration of the existing scripts-side duplicates.
- Focused tests, Ruff, exact-path diff checks, independent verification, and a focused commit pass before closure.

## Pre-Filing Preflight Subsection

Run applicability and mandatory clause preflights against this exact revision. File only with no missing required/advisory specifications, no blocking errors, and zero mandatory clause gaps.

## Risk And Rollback

The main risk is treating an unvalidated CLI role assertion as transcript authority. Exact package parsing, role/subject agreement, and pre-write failure contain it. A secondary risk is accidentally changing role-free or dispatcher semantics; dedicated compatibility tests keep both paths stable. Rollback is a focused revert of the package parser, CLI integration, and focused tests; WI-5309 and all bridge/session history remain durable.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_kb_attribution.py`

## Recommended Commit Type

`fix`
