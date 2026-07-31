NO-GO
::init gtkb pb
::open test

bridge_kind: lo_verdict
Document: gtkb-wi5602-ipa-governance-gate-cleanup
Version: 004
Responds to: bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md
Date: 2026-07-19 UTC
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata via nodeRepl.requestMeta plus current owner transcript role assignment

# Loyal Opposition Proposal Review - NO-GO - WI-5602 Retired Assessment-Surface Governance Gate Cleanup

## Verdict

NO-GO. Version 003 corrects the prior Project Authorization mismatch with an active WI-5602-scoped PAUTH, and the narrowed target set is directionally better than version 001. The remaining blocker is technical: the proposal says the implementation will remove `independent-progress-assessments/` from the controlled-artifact allowlist and path recognizer, but that removal by itself does not stop ungated writes to the retired path. Unknown paths currently fall through as `not_protected`, so the proposed removal-only shape leaves the core defect alive.

## First-Line Role Eligibility Check

- Role authority for this interactive session: Loyal Opposition by Mike's direct current-chat assignment.
- Verdict status: `NO-GO`, a Loyal Opposition proposal-review status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Reviewer session context: `019f7815-a565-78d3-a599-dec8388086ff`.
- Proposal author session context: `019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`.
- The author and reviewer session contexts are present and distinct; review independence passes.

## Applicability Preflight

- packet_hash: `sha256:e601bc514a4fb53f04b7ae767c3aaa2d70059c48c1cd11b7bb67cd20bdbcf6ce`
- bridge_document_name: `gtkb-wi5602-ipa-governance-gate-cleanup`
- content_file: `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md`
- operative_file: `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:bf49677fe98f4d32fdff052f4e09b9767fca51f2086f300d5a7e62423e07c245`

## Clause Applicability

- Bridge id: `gtkb-wi5602-ipa-governance-gate-cleanup`
- Operative file: `bridge\gtkb-wi5602-ipa-governance-gate-cleanup-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory mode exit: 0

## Positive Confirmations

- Latest thread state before this verdict is `REVISED` v003 with no bridge-chain drift.
- The prior PAUTH mismatch called out in `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-002.md` is resolved. `gt projects show-authorization PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5602-GOVERNANCE-GATE-CLEANUP-2026-07-19 --json` shows `status: active`, `project_id: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`, `included_work_item_ids: ["WI-5602"]`, and `owner_decision_deliberation_id: DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`.
- `gt backlog show WI-5602 --json` confirms WI-5602 is open, P1, and specifically describes the retired `independent-progress-assessments/` write-allowance defect.
- Applicability and ADR/DCL clause preflights against v003 both pass with zero blocking gaps.
- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` was read directly from MemBase and is on point: the retired directory must not be read from, cited, recreated, or depended on.

## Findings

### P1 - Removing the allowlist entry alone leaves retired-path writes ungated

**Evidence.** The live guard logic classifies a path as protected only when it matches direct controlled artifacts, runtime authority state, exact protected paths, protected prefixes, or diagnostic/direct-block rules in `scripts/controlled_artifact_paths.py`. If none match, `classify_controlled_artifact()` returns `ControlledArtifactClassification(..., is_controlled=False, reason_code="not_protected", ...)` at the final fallthrough. `scripts/protected_mutation_guard.py` then allows the mutation when `protected_targets` is empty.

Version 003 says the implementation will "remove the retired assessment-surface prefix from the live controlled-artifact allowlist and implementation-authorization path recognizer" and its verification table says to assert the retired prefix is "not accepted as an unprotected write target." Those two statements do not line up with the current code. A read-only monkey-patch probe that removes the `independent-progress-assessments/` allowlist entry while leaving the rest of the target code shape intact still returns `allowed=True`:

```text
python -c "from pathlib import Path; from scripts import controlled_artifact_paths as c; from scripts.protected_mutation_guard import evaluate_mutation; c.ALLOWED_WRITE_PREFIXES=('bridge/',); r=c.classify_controlled_artifact('independent-progress-assessments/report.md'); print(r); g=evaluate_mutation(Path('.').resolve(), ['independent-progress-assessments/report.md'], harness_id='A', session_id='probe'); print(g)"

ControlledArtifactClassification(normalized_path='independent-progress-assessments/report.md', is_controlled=False, direct_write_blocked=False, reason_code='not_protected', classification='independent-progress-assessments/report.md')
GuardResult(allowed=True, reason_code='not_protected', details='No protected paths modified')
```

For comparison, a read-only monkey-patch that removes the allowlist entry and adds the retired prefix to protected-prefix classification does cause the guard to block without a claim:

```text
python -c "from pathlib import Path; from scripts import controlled_artifact_paths as c; from scripts.protected_mutation_guard import evaluate_mutation; c.ALLOWED_WRITE_PREFIXES=('bridge/',); c.PROTECTED_PREFIXES=c.PROTECTED_PREFIXES+('independent-progress-assessments/',); r=c.classify_controlled_artifact('independent-progress-assessments/report.md'); print(r); g=evaluate_mutation(Path('.').resolve(), ['independent-progress-assessments/report.md'], harness_id='A', session_id='probe'); print(g)"

ControlledArtifactClassification(normalized_path='independent-progress-assessments/report.md', is_controlled=True, direct_write_blocked=False, reason_code='protected_path', classification='independent-progress-assessments/')
GuardResult(allowed=False, reason_code='missing_or_stale_claim', details='No active work-intent claim found for session ID probe')
```

**Risk/impact.** Approving v003 as written would likely let Prime Builder remove two stale string references and update tests while still allowing the exact prohibited behavior WI-5602 exists to stop: a direct write to `independent-progress-assessments/report.md` can remain `not_protected` and therefore bypass bridge GO, work-intent claim, and implementation-start authorization. That contradicts the owner decision not to recreate or depend on the retired surface.

**Required revision.** The revised proposal must explicitly authorize the behavior change that makes the retired path non-open. Acceptable shapes include adding `independent-progress-assessments/` to a protected or direct-retired classification path in `scripts/controlled_artifact_paths.py`, or an equivalent fail-closed guard inside the existing approved target set. The focused tests must assert the retired path is no longer `not_protected`, and `platform_tests/scripts/test_protected_mutation_guard.py` must prove a write to `independent-progress-assessments/report.md` is denied without a valid GO/claim/packet or direct-retired reason.

### P2 - PAUTH scope still mentions archive-name protection that v003 removes from proposal scope

**Evidence.** The active WI-5602 PAUTH scope summary says it covers removing live allowances for the retired surface, protecting the two retired/barred archive names, and updating focused tests. Version 003 removes `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py` from `target_paths` and explicitly says it does not protect or preserve the noncanonical archive residue.

**Risk/impact.** This is not the basis for the NO-GO because proposal `target_paths` remain the narrower implementation boundary. It is still a traceability mismatch that can confuse the next implementer or reviewer about whether archive-name protection is part of WI-5602.

**Recommended cleanup.** Either revise the PAUTH scope text/version to match the narrowed four-path plan, or carry an explicit note in the revised proposal that the PAUTH over-includes archive-name protection but the approved implementation excludes it and no `hygiene/reclaim.py` mutation is authorized.

## Required Revisions

1. Refile with an explicit fail-closed classification plan for `independent-progress-assessments/`, not just removal from `ALLOWED_WRITE_PREFIXES` and `PATH_TOKEN_RE`.
2. Update the verification plan so the focused tests prove the retired path is denied by the guard when no governed GO/claim/packet exists, or is directly blocked with a stable retired-surface reason.
3. Clarify the PAUTH/proposal mismatch around archive-name protection so the next implementation cannot treat `groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py` or noncanonical residue as silently in scope.

## Prior Deliberations

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` - directly read from MemBase; owner decision records that the directory is retired, contents deleted, and the surface must not be read from, cited, recreated, or depended on.
- `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-001.md` - original proposal.
- `bridge/gtkb-wi5602-ipa-governance-gate-cleanup-002.md` - prior independent NO-GO for mismatched PAUTH, now resolved by v003.
- Deliberation searches were run for `independent-progress-assessments retired write guard allowlist`, `WI-5602 governance gates allow independent-progress-assessments writes`, and `canonical artifacts may not reference noncanonical archive residue`. They surfaced the IPA retirement decision and the WI-5492/obsolete-reference-purge precedent chain; no record was found that makes removal-only classification sufficient.

## Commands Executed

```text
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi5602-ipa-governance-gate-cleanup --format json --preview-lines 6
Get-Content -Raw bridge/gtkb-wi5602-ipa-governance-gate-cleanup-002.md
Get-Content -Raw bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5602-ipa-governance-gate-cleanup --content-file bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5602-ipa-governance-gate-cleanup --content-file bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md
gt projects show-authorization PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5602-GOVERNANCE-GATE-CLEANUP-2026-07-19 --json
gt backlog show WI-5602 --json
gt deliberations search "independent-progress-assessments retired write guard allowlist" --limit 5 --json
gt deliberations search "WI-5602 governance gates allow independent-progress-assessments writes" --limit 5 --json
gt deliberations search "canonical artifacts may not reference noncanonical archive residue" --limit 5 --json
python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('groundtruth-kb/src').resolve())); from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB(Path('groundtruth.db')); d=db.get_deliberation('DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT'); print(d)"
rg -n "independent-progress-assessments|BARRED - DO NOT USE|RETIRED-independent-progress-assessments|ALLOWED_WRITE_PREFIXES|PATH_TOKEN_RE|_PROTECTED_PREFIXES" scripts/controlled_artifact_paths.py scripts/implementation_authorization.py groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_protected_mutation_guard.py bridge/gtkb-wi5602-ipa-governance-gate-cleanup-003.md
rg -n "classify_controlled_artifact|is_protected_path|ALLOWED_WRITE_PREFIXES|not_protected|direct_write_blocked|evaluate_mutation|PATH_TOKEN_RE" scripts/protected_mutation_guard.py scripts/controlled_artifact_paths.py scripts/implementation_authorization.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_protected_mutation_guard.py
python -c "from pathlib import Path; from scripts import controlled_artifact_paths as c; from scripts.protected_mutation_guard import evaluate_mutation; c.ALLOWED_WRITE_PREFIXES=('bridge/',); r=c.classify_controlled_artifact('independent-progress-assessments/report.md'); print(r); g=evaluate_mutation(Path('.').resolve(), ['independent-progress-assessments/report.md'], harness_id='A', session_id='probe'); print(g)"
python -c "from pathlib import Path; from scripts import controlled_artifact_paths as c; from scripts.protected_mutation_guard import evaluate_mutation; c.ALLOWED_WRITE_PREFIXES=('bridge/',); c.PROTECTED_PREFIXES=c.PROTECTED_PREFIXES+('independent-progress-assessments/',); r=c.classify_controlled_artifact('independent-progress-assessments/report.md'); print(r); g=evaluate_mutation(Path('.').resolve(), ['independent-progress-assessments/report.md'], harness_id='A', session_id='probe'); print(g)"
```

## Owner Action Required

None.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

Skills applied: gtkb-bridge, proposal-review
