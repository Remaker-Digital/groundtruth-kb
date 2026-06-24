NEW

# gtkb-wi4614-kb-session-wrap-adapter-reference-coverage - Repair kb-session-wrap adapter reference coverage

bridge_kind: prime_proposal
Document: gtkb-wi4614-kb-session-wrap-adapter-reference-coverage
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-24T00:29:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; Windows PowerShell; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4614

target_paths: ["platform_tests/scripts/test_kb_session_wrap_skill.py", ".codex/skills/kb-session-wrap/references/audit-checklist.md", ".codex/skills/kb-session-wrap/references/handoff-template.md"]

implementation_scope: test_addition, scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4614 was opened because `.codex/skills/kb-session-wrap/SKILL.md` declared `references/audit-checklist.md` and `references/handoff-template.md`, but the Codex adapter package did not contain those reference files during the 2026-06-16 session-wrap invocation. The broader generator defect was later addressed by the verified `gtkb-codex-adapter-references-mirror` thread, and live inspection now shows the two `kb-session-wrap` Codex reference files are present, tracked, and byte-identical to their canonical `.claude` counterparts.

The remaining implementable defect for this WI is coverage drift. The focused test `platform_tests/scripts/test_kb_session_wrap_skill.py` still fails three assertions because it expects retired `bridge/INDEX.md` language even though the current bridge authority is TAFE-backed bridge state plus status-bearing numbered bridge files. The same test also does not directly assert that the Codex `kb-session-wrap` reference files exist and match the canonical reference payloads. This proposal repairs that coverage without changing formal artifacts, bridge governance records, or source behavior.

## Current Evidence

- `gt bridge threads --wi WI-4614` reports no existing bridge thread for this work item.
- `Get-ChildItem .codex/skills/kb-session-wrap/references, .claude/skills/kb-session-wrap/references` shows all four expected reference files present.
- `Get-FileHash -Algorithm SHA256` shows matching hashes for the Codex and Claude `audit-checklist.md` pair, and matching hashes for the Codex and Claude `handoff-template.md` pair.
- `git ls-files .codex/skills/kb-session-wrap .claude/skills/kb-session-wrap platform_tests/scripts/test_kb_session_wrap_skill.py` confirms the Codex reference files and the focused test are tracked.
- `python -m pytest platform_tests/scripts/test_kb_session_wrap_skill.py -q --tb=short` currently fails 3 tests solely on stale `bridge/INDEX.md` expectations.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH provides bounded owner authorization for this snapshot-member WI but does not bypass bridge GO, target-path scoping, implementation-start authorization, or verification.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - WI-4614's source spec; portable harness roles require Codex adapter packages to carry the operational skill material needed by the Codex harness.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - harness capability floors depend on complete, loadable harness-local skill packages and adapter resources.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal must use the file bridge, dispatcher/TAFE state, and numbered bridge files; implementation waits for Loyal Opposition GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the machine-readable `Project Authorization`, `Project`, and `Work Item` lines bind the proposal to the authorized project/WI scope.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward these specifications and show executed spec-derived tests.
- `GOV-STANDING-BACKLOG-001` - WI-4614 is the MemBase work item being advanced; no new WIs are added and newer project members outside the PAUTH snapshot remain out of scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - all target paths are in-root under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the change preserves the discovered defect, test mapping, prior deliberations, and verification evidence as durable artifacts instead of relying on session memory.

## Prior Deliberations

- `DELIB-20265586` - owner AUQ decision authorizing the drive-to-conclusion project sweep with snapshot-bound project authorizations. This proposal cites the specific PAUTH created from that decision and does not include newer May29 Hygiene project WIs outside the snapshot.
- `DELIB-20265308` and `bridge/gtkb-codex-adapter-references-mirror-001.md` through `-004.md` - prior verified Codex adapter reference mirroring work. That thread fixed the generator/materialization class and explicitly included `.codex/skills/kb-session-wrap/references/**`; this proposal builds on it by adding focused `kb-session-wrap` adapter-reference coverage and removing stale no-index-era test expectations.
- DA searches run before proposing:
  - `gt deliberations search "WI-4614 kb-session-wrap Codex adapter references audit-checklist handoff-template" --limit 5 --json`
  - `gt deliberations search "GOV-HARNESS-ROLE-PORTABILITY Codex skill adapter reference packaging parity" --limit 5 --json`
  - `gt deliberations search "DELIB-20265586 MAY29 HYGIENE bounded implementation authorization snapshot" --limit 5 --json`

## Owner Decisions / Input

No new owner decision is required for this proposal. Authority derives from `DELIB-20265586` and `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`; the PAUTH includes `WI-4614`, allows `test_addition` and `scaffold_update`, and does not authorize any work item added to the project after the snapshot.

## Requirement Sufficiency

Existing requirements sufficient - WI-4614 identifies the missing Codex adapter reference packaging defect, `GOV-HARNESS-ROLE-PORTABILITY-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001` govern harness adapter completeness, and the prior `gtkb-codex-adapter-references-mirror` thread supplies the adjacent generator precedent. No new or revised requirement is needed before implementing the focused coverage repair.

## Proposed Implementation

Update `platform_tests/scripts/test_kb_session_wrap_skill.py` so it reflects the current bridge contract and directly guards the `kb-session-wrap` Codex reference package:

1. Replace stale required-term assertions for `bridge/INDEX.md` with current bridge authority terms already used by the skill/reference content, such as dispatcher/TAFE-backed bridge state and status-bearing/versioned bridge files.
2. Add explicit constants for the two Codex `kb-session-wrap` reference files.
3. Add assertions that the two Codex reference files exist.
4. Add byte-for-byte or hash-based assertions that the Codex reference files match the canonical `.claude/skills/kb-session-wrap/references/` files.
5. Keep the repair scoped to the focused test and, only if live drift is found during implementation, the two Codex reference files named in `target_paths`.

No MemBase mutation, formal GOV/SPEC/ADR/DCL/PB/REQ mutation, bridge-state repair, generator rewrite, or project membership change is in scope.

## Spec-Derived Verification Plan

| Governing specification or artifact | Verification command / check | Expected result |
| --- | --- | --- |
| `GOV-HARNESS-ROLE-PORTABILITY-001` and `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `python -m pytest platform_tests/scripts/test_kb_session_wrap_skill.py -q --tb=short` | The focused test passes, proving the Codex adapter declares, contains, and preserves the `kb-session-wrap` reference package. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Same pytest command plus review of updated required terms | The test no longer asserts retired `bridge/INDEX.md` authority and instead reflects TAFE-backed bridge state plus numbered/versioned bridge files. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4614-kb-session-wrap-adapter-reference-coverage-001.md` | `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries forward this mapping and exact command results | Loyal Opposition can verify each linked specification against executed evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4614-kb-session-wrap-adapter-reference-coverage-001.md` | Exit 0 with zero blocking gaps. |
| Python code quality for touched test file | `ruff check platform_tests/scripts/test_kb_session_wrap_skill.py` and `ruff format --check platform_tests/scripts/test_kb_session_wrap_skill.py` | Both pass after implementation. |

## Pre-Filing Preflights

Prime Builder ran the mandatory preflights against the completed draft before helper-mediated live filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4614-kb-session-wrap-adapter-reference-coverage-001.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4614-kb-session-wrap-adapter-reference-coverage-001.md
```

Observed results before live filing:

- Applicability preflight exit 0; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause preflight exit 0; `Blocking gaps (gate-failing): 0`.

## Acceptance Criteria

- `platform_tests/scripts/test_kb_session_wrap_skill.py` no longer requires `bridge/INDEX.md`.
- The focused test asserts current bridge-state terminology for the `kb-session-wrap` skill/reference surfaces.
- The focused test asserts `.codex/skills/kb-session-wrap/references/audit-checklist.md` and `.codex/skills/kb-session-wrap/references/handoff-template.md` exist.
- The focused test asserts those Codex reference files match their canonical `.claude/skills/kb-session-wrap/references/` counterparts.
- Focused pytest, ruff lint, and ruff format checks pass on the touched test file.

## Risk / Rollback

Risk is low and localized. The expected implementation is test-only unless the live Codex reference files drift again before implementation. A single commit rollback restores the previous focused test behavior and any restored Codex reference files, without affecting MemBase, formal artifacts, project membership, or bridge history.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4614-kb-session-wrap-adapter-reference-coverage`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test:` - the expected durable change is focused regression coverage for existing adapter-reference behavior and stale bridge-terminology assertions. If implementation must restore one of the two Codex reference files because live drift recurs, the implementation report should justify whether `fix:` is more accurate.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
