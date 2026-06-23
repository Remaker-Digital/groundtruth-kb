NEW

# gtkb-wi4714-gitattributes-lf-hardening - generated-artifact LF policy

bridge_kind: prime_proposal
Document: gtkb-wi4714-gitattributes-lf-hardening
Version: 001
Author: Prime Builder (Codex interactive session)
Date: 2026-06-23 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ef01a-73cf-7f82-ae71-a5acc321664f
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop interactive session; transcript role override ::init gtkb pb; bridge-propose + gtkb-propose skills

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4714

target_paths: [".gitattributes", "platform_tests/scripts/test_gitattributes_lf_policy.py"]

implementation_scope: scaffold_update | test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add a small `.gitattributes` policy that pins generated/text scaffold artifact classes to LF line endings, with a regression test that verifies representative bridge-tooling paths resolve to `eol=lf`. The immediate defect class comes from WI-4701: generated Codex skill adapter artifacts and nearby scaffold files can drift into CRLF-in-index state on Windows when no repo-local attribute policy constrains them.

This proposal is deliberately a policy hardening slice, not a broad repo renormalization sweep. It does not bulk rewrite existing bridge history, inventory, or every current CRLF-index outlier. It adds the guardrail that future generated/scaffold text writes and intentional future renormalization can rely on.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs this bridge-mediated implementation lifecycle and the append-only numbered bridge state used for review and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Allows the cited PAUTH to provide bounded owner authorization while preserving bridge GO, implementation-start, implementation report, and Loyal Opposition verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires concrete governing-spec linkage and mechanical preflight before implementation review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires project authorization, project, and work-item metadata plus live authorization/membership checks.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires the implementation report and Loyal Opposition verification to map linked specs to executed tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-4714 is the governed follow-up captured from WI-4701 instead of being bundled into that source/test-only bridge.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex adapter and hook parity surfaces are live harness-integration artifacts; generated Codex skill artifacts must be reproducible and line-ending stable across Windows harnesses.

## Prior Deliberations

- `DELIB-20265459` — Owner authorized the WI-4701 bridge-tooling reliability batch that surfaced this deferred line-ending hardening work.
- `DELIB-20265586` — Owner authorized bounded implementation for the 8 current open member WIs in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, including WI-4714, under the cited PAUTH.
- `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-003.md` — Revised WI-4701 scope explicitly deferred live-artifact LF convergence and `.gitattributes` hardening to WI-4714 rather than expanding the source/test-only generator fix.
- `bridge/gtkb-wi4701-codex-adapter-crlf-whitespace-fix-009.md` — Implementation evidence documented the deferred WI-4714 convergence signal and left generated live artifacts untouched under WI-4701.

## Owner Decisions / Input

No new owner decision is required before Loyal Opposition review. Owner decision `DELIB-20265586` authorizes bounded implementation for WI-4714 under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23`.

This proposal does not add new WIs, does not perform destructive cleanup, does not change credentials, does not deploy, and does not mutate GOV/SPEC/ADR/DCL/PB/REQ records. It also does not request a broad repository renormalization sweep.

## Requirement Sufficiency

Existing requirements sufficient — WI-4714’s work-item description, the WI-4701 bridge deferral, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, and the bridge/project governance requirements are enough to define the bounded policy/test implementation. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run bridge applicability and clause preflights before and after filing/reporting; preserve append-only bridge artifacts.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after GO, run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4714-gitattributes-lf-hardening` and confirm it resolves WI-4714, the project, the PAUTH, and only the scoped target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4714-gitattributes-lf-hardening` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4714-gitattributes-lf-hardening` must report no missing required specs and zero blocking gaps.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report will include spec-to-test mapping and executed command evidence.
- `GOV-STANDING-BACKLOG-001`: implementation evidence must keep WI-4714 separate from WI-4701 and avoid unapproved broad cleanup.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: representative `.codex/skills/**`, generated helper, JSON, TOML, and Markdown scaffold paths must resolve to LF via `.gitattributes`.

Focused commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gitattributes_lf_policy.py -q --tb=short
git check-attr text eol -- .codex/skills/bridge-propose/SKILL.md .codex/skills/bridge-propose/helpers/write_bridge.py .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml groundtruth-kb/templates/skills/bridge-propose/SKILL.md
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_gitattributes_lf_policy.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_gitattributes_lf_policy.py
```

## Risk / Rollback

Risk is mostly scope creep: a broad `git add --renormalize .` would touch historical bridge files and many unrelated artifacts. The implementation must keep the mutation to `.gitattributes` plus the focused test file unless a later GO explicitly broadens target paths. Existing CRLF-index files may remain until intentionally touched or separately normalized; that is acceptable for this policy slice.

Rollback is a single commit reverting `.gitattributes` and the focused test. No schema, DB, credential, or deployment state changes.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4714-gitattributes-lf-hardening`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

chore - adds repo-level generated-artifact LF policy plus a regression test.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
