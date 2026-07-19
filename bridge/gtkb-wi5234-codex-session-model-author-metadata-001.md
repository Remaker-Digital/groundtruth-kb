NEW

# gtkb-wi5234-codex-session-model-author-metadata - Use Exact Session Envelopes for Bridge Author Model Metadata

bridge_kind: prime_proposal
Document: gtkb-wi5234-codex-session-model-author-metadata
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; system-declared GPT-5 family; reasoning configuration not exposed; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5234

target_paths: ["scripts/bridge_author_metadata.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "platform_tests/scripts/test_bridge_author_metadata.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source,test,metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The canonical `gt bridge file-implementation-proposal` path resolves the current
Codex session ID but cannot obtain model provenance from the exact session
document. It therefore requires ad hoc `GTKB_AUTHOR_*` injection even when a
session envelope carries trustworthy model data. Three current governed filing
attempts have independently reproduced the resulting fail-closed dead end.

Add an exact-session metadata source to `scripts/bridge_author_metadata.py`.
After explicit arguments and author environment variables, the loader may read
only `harness-state/<resolved-harness>/session-envelopes/<runtime-session-id>.json`.
It must validate the document's session and harness binding, open status, and
worker role provenance before accepting non-placeholder `model_id`,
`model_version`, and `model_configuration`. It must never use the shared
`session-envelope.json` projection, a different session document, or the
dispatcher registry's model/argv hints as author provenance.

Extend the session-envelope producer to persist model configuration when the
runtime supplies it. Unknown, malformed, closed, mismatched, missing, or
ambiguous session metadata remains a clear fail-closed condition. The repair
does not guess the current interactive model and does not weaken the existing
strict metadata floor.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - Requires truthful, non-placeholder
  author identity and model provenance on bridge artifacts; this is WI-5234's
  source specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Keeps proposal filing on the canonical
  append-only bridge writer and preserves role and review gates.
- `GOV-SESSION-ROLE-AUTHORITY-001` - Requires worker behavior and provenance to
  bind to the exact session document rather than dispatcher-selection
  configuration.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this
  concrete proposal-to-spec linkage before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the explicit
  project and active project-authorization linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the tests below
  to map the provenance, exact-session, and fail-closed requirements.
- `GOV-STANDING-BACKLOG-001` - WI-5234 and linked TEST-11388 remain the
  authoritative backlog and test carriers.
- `GOV-WORK-TREE-HYGIENE-001` - Requires hunk-scoped treatment of the foreign
  dirty changes already present in `session/envelope.py`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Keeps every runtime document,
  source dependency, and test fixture inside the GT-KB project root.

## Prior Deliberations

- `DELIB-20261032` - Identified the document author-provenance gap. This
  proposal closes the mechanical bridge-filing gap without lowering the
  provenance requirement.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - Established
  the session envelope, rather than dispatcher role mapping, as worker context.
  This proposal reuses that exact-document authority for model provenance.
- `DELIB-20260710-GTKB-MODERNIZATION-DISPATCHED-WORKER-ROLE-GOV-V5-APPROVAL`
  - Prohibits role inference from dispatcher selection configuration. The same
  boundary is preserved for model metadata: registry model hints are not
  treated as evidence of the running interactive model.
- `DELIB-20265888` - Requires a harness-invisible black-box equivalence
  maintainer. This repair changes shared bridge metadata loading, not
  harness-to-harness contact or routing.
- `DELIB-202666274` - Authorizes required project-level blocker repairs while
  preserving bridge GO, claim, implementation-start, independent verification,
  and mechanical-operation gates.

## Owner Decisions / Input

No additional owner decision is required to submit this proposal. WI-5234 is a
captured defect within the active authorized project, and `DELIB-202666274`
directs discovered blocker repairs to continue. Protected implementation still
requires an independent `GO`, an exact current-session claim, successful
implementation-start authorization, and later independent `VERIFIED`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
defines the truthful metadata floor, `GOV-SESSION-ROLE-AUTHORITY-001` defines
the exact-session authority boundary, and TEST-11388 states the positive and
fail-closed integration behavior. No new or revised requirement is needed.

## Proposed Implementation

1. In `scripts/bridge_author_metadata.py`, resolve the runtime session ID using
   the existing environment precedence, then load only the exact per-session
   document for the already-resolved durable harness identity.
2. Validate `session_id`, `harness_id`, `harness_name`, open status, resolved
   role, and worker-role provenance before accepting model fields.
3. Preserve metadata precedence as explicit argument, author environment,
   exact session document, then durable identity for identity-only fields.
   Durable identity and registry data must never supply model or configuration
   values.
4. In `groundtruth_kb.session.envelope`, add `model_configuration` alongside
   `model_id` and `model_version`, populated only from runtime-provided model
   configuration inputs. Placeholder values remain non-authoritative.
5. Keep malformed JSON, missing documents, unknown placeholders, mismatched
   sessions, wrong harnesses, closed documents, and ambiguous sources
   fail-closed with diagnostics that name the rejected source.
6. Add unit and CLI integration coverage proving the canonical proposal filer
   renders all three author model fields without `GTKB_AUTHOR_*` injection when
   the exact session document is known.

## Scope Boundaries

- All implementation outputs, generated runtime documents, test fixtures, and
  the numbered bridge artifact remain in-root under `E:\GT-KB`.
- No dispatcher, TAFE, eligibility, lease, routing, harness registry, direct
  harness, credential, deployment, release, Git staging, commit, or push
  operation is in scope.
- No shared `harness-state/<harness>/session-envelope.json` projection may be
  read as current-session author authority.
- No model value may be inferred from registry argv, model hints, pricing
  configuration, a different session, or prior chat notes.
- Existing dirty Git-root and timeout changes in
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py` are quarantined
  foreign work. Implementation may add only the independently reviewed model
  configuration hunk and must preserve all other current bytes.
- No full-file rewrite or unrelated cleanup is permitted.

## Acceptance Criteria

1. A known exact Codex PB session document supplies non-placeholder
   `author_model`, `author_model_version`, and
   `author_model_configuration` without `GTKB_AUTHOR_*`.
2. `gt bridge file-implementation-proposal` renders those fields in its
   governed draft/filing path.
3. Explicit arguments and `GTKB_AUTHOR_*` retain precedence over the exact
   session document.
4. A stale shared projection, different session document, registry model hint,
   malformed document, harness mismatch, closed document, or placeholder model
   cannot satisfy the metadata floor.
5. Rejection diagnostics identify why exact-session metadata was unavailable
   or non-authoritative.
6. Existing role-provenance, bridge-filing, session-envelope, and stale-shared-
   projection tests remain green.
7. The foreign dirty hunk in `session/envelope.py` is byte-preserved and
   excluded from WI-5234 attribution.

## Cross-Harness Disposition

The metadata loader is shared bridge infrastructure, so its exact-session and
fail-closed rules apply uniformly to every registered harness document. This
slice adds no managed skill, hook, rule, plugin, MCP surface, harness adapter,
or routing behavior, so there is no generated adapter projection to update.
Codex-specific tests exercise the reported defect; generic mismatch and
placeholder tests protect the cross-harness boundary.

## Spec-Derived Verification Plan

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` and TEST-11388:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --no-header
```

Expected: a known exact session document populates all required model fields;
unknown, mismatched, stale, and malformed sources fail closed.

- `GOV-SESSION-ROLE-AUTHORITY-001`:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py -q --no-header
```

Expected: exact per-session production and provenance checks pass, including
the new model-configuration field, with no shared-projection fallback.

- Bridge, linkage, and clause gates:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5234-codex-session-model-author-metadata-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5234-codex-session-model-author-metadata-001.md
```

Expected: both mandatory preflights pass with no blocking or missing-spec gap
before the proposal is filed.

- Focused lint and diff containment:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_author_metadata.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
git diff --check -- scripts/bridge_author_metadata.py groundtruth-kb/src/groundtruth_kb/session/envelope.py platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_session_envelope_runtime.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
```

Expected: clean lint/whitespace evidence and an exact hunk review that
separates WI-5234 from all pre-existing dirty bytes.

## Risk / Rollback

Primary risk is accepting stale or inferred model metadata as though it
described the active author session. Exact document selection, binding checks,
strict precedence, and negative tests contain that risk. A secondary risk is
commingling the existing `session/envelope.py` Git-probe hunk; before/after
hunk and hash evidence must isolate the one new field.

Rollback is one focused `fix` commit reverting only the WI-5234 hunks and
tests. Runtime session documents are generated state and are not staged or
committed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5234-codex-session-model-author-metadata`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - restores the existing governed bridge-filing contract rather than
introducing a new product capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
