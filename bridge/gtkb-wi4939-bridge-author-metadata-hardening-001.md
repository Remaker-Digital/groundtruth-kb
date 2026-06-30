NEW

# Defect-Fix Proposal — Slice 2: harden bridge_author_metadata contract

bridge_kind: prime_proposal
Document: gtkb-wi4939-bridge-author-metadata-hardening
Version: 001
Author: Prime Builder Cursor
Date: 2026-06-30T22:25:00Z

author_identity: Prime Builder Cursor
author_harness_id: E
author_session_context_id: cursor-pb-s522-metadata-compliance-wi4939
author_model: Composer
author_model_version: 2.5
author_model_configuration: Cursor interactive; session role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION
Project: PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE
Work Item: WI-4939

target_paths: ["scripts/bridge_author_metadata.py", "scripts/openrouter_harness.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_bridge_author_metadata.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Claim

Headless LO harnesses (F/D) and the metadata loader still emit static
`author_session_context_id` slugs (`openrouter-harness-f`, `ollama-harness-d`) while
`ensure_author_metadata()` preserves wrong-but-complete metadata. WI-4939 hardens the
loader and harness env injection so dispatch-run session ids win, static slugs are
rejected/overridden, and WI-4885 interactive defaults stop inventing wrong model identity.

## Defect / Reproduction

- `scripts/openrouter_harness.py` system prompt instructs `author_session_context_id: openrouter-harness-f` (~349–355); `set_author_metadata_env()` omits session id; guard fallback uses same slug (~658).
- `scripts/ollama_harness.py` mirrors with `ollama-harness-d`.
- `load_author_metadata()` does not map `GTKB_BRIDGE_POLLER_RUN_ID` to `author_session_context_id`.
- `ensure_author_metadata()` returns content unchanged when all six fields present even if session id is synthetic.
- `bridge_author_metadata.py` WI-4885 block generates fresh `uuid.uuid4()` per call and hardcodes inaccurate model strings.

## In-Root Placement Evidence

All targets under `E:\GT-KB` platform tree per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — credible per-session author metadata required.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governed bridge write path must not guess metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-20266647` — forward-prevention metadata compliance program.
- `bridge/gtkb-wi4522-author-metadata-per-harness-resolution-006.md` — prior resolution; static slug regression.
- `bridge/gtkb-wi4829-self-review-write-time-gate-005.md` — review independence depends on parseable session ids.

## Owner Decisions / Input

Authorized by `PAUTH-PROJECT-GTKB-BRIDGE-METADATA-COMPLIANCE-BRIDGE-AUTHOR-METADATA-COMPLIANCE-REMEDIATION-FORWARD-PREVENTION` / DELIB-20266647. No new owner decision.

## Requirement Sufficiency

Existing requirements sufficient (`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`, WI-4939 acceptance).

## Proposed Scope

1. Map `GTKB_BRIDGE_POLLER_RUN_ID` and `GTKB_INHERITED_SESSION_ID` into `author_session_context_id` resolution.
2. Add `is_synthetic_session_context_id()` helper; reject/override in `ensure_author_metadata()` when env carries dispatch id.
3. Fix F/D harness prompts and `set_author_metadata_env()` to inject dispatch session id; remove static slug instructions.
4. Fix WI-4885 interactive defaults: stable session from env, accurate model fields from runtime envelope.
5. Tests covering static slug rejection, dispatch id override, harness env injection.

Depends on WI-4938 scanner for regression reporting (can land after WI-4939 if GO order differs).

## Specification-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_author_metadata.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_author_metadata.py scripts/openrouter_harness.py scripts/ollama_harness.py
```

## Risks / Rollback

Medium — changes headless LO write path. Rollback single revert. Does not rewrite historical bridge files.

## Recommended Commit Type

fix — WI-4939 metadata loader and harness hardening.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
