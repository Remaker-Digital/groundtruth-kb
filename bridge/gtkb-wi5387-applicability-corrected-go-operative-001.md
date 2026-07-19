NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; ::open build; reasoning=xhigh; approval_policy=never
author_metadata_source: explicit_current_codex_thread_metadata

# WI-5387: Make Applicability Preflight Honor Corrected Verdict Operative Content

bridge_kind: prime_proposal
Document: gtkb-wi5387-applicability-corrected-go-operative
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5387-APPLICABILITY-CORRECTED-GO-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5387

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/bridge_applicability_preflight.py` currently chooses operative content with a fixed status precedence: latest `NEW`/`REVISED`/`NO-ACTION` first, then latest `VERIFIED`/`WITHDRAWN`/`GO`/`NO-GO`. That rule fails on corrected-verdict chains. A Loyal Opposition corrected `GO` issued after a Prime `NO-ACTION` can be shadowed by the older `NO-ACTION`, and later the applicability and clause preflights can select different operative files for the same bridge thread.

WI-5387 proposes a narrow resolver repair: applicability preflight must resolve operative content from the latest numbered chain and explicit `Responds to`, `Approved proposal`, `Reviewed`, or `Verified` metadata when a verdict corrects a prior `NO-ACTION`. The repair must preserve standalone latest `NO-ACTION` semantics, terminal `WITHDRAWN`, packet hashing, spec-link harvesting, and in-root bridge authority.

## Current Evidence

Live read-only reproduction on `gtkb-wi5299-reissued-finalizer-failure-repair`:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5299-reissued-finalizer-failure-repair --json` exits nonzero and selects `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-006.md` (`NO-ACTION`) as `operative_version`, reporting missing mandatory proposal/verification specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5299-reissued-finalizer-failure-repair` exits nonzero and selects `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` (`VERIFIED`) as operative, reporting a different blocking gap.
- WI-5387 was created from earlier live evidence on the same thread where corrected `GO` version 005 explicitly approved proposal version 001 after Prime version 003 `NO-ACTION`, but applicability preflight selected the older `NO-ACTION` instead.

The core defect is not that WI-5299 should be allowed to implement now. It should not. The defect is that mandatory preflight tools disagree about what file is being evaluated and that applicability can shadow a corrected verdict with an older `NO-ACTION`.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5387` and keeps owner authorization, PAUTH, bridge review, work-intent, implementation-start, report, independent verification, and focused finalization gates intact.

## Requirement Sufficiency

Existing requirements sufficient.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; DCL-NO-ACTION-STATUS-SEMANTICS-001; WI-5387; live WI-5299 corrected-verdict/preflight contradiction",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, and DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.",
  "primary_route": "Fresh Loyal Opposition GO, exact go_implementation claim, implementation-start packet, focused resolver tests, implementation report, and independent VERIFIED.",
  "before_behavior": "Applicability preflight can select an older NO-ACTION over a later corrected GO or disagree with the mandatory clause preflight about the operative numbered file.",
  "after_behavior": "Applicability preflight uses corrected-verdict metadata and the latest numbered chain to identify the intended operative file deterministically while preserving true latest NO-ACTION holds and terminal WITHDRAWN behavior.",
  "self_descriptive_naming": "The bridge slug, PAUTH id, WI id, target list, and test plan all name corrected-GO operative resolution directly.",
  "obsolete_guidance_disposition": "The repair must not revive bridge/INDEX.md, retired aggregate queues, stale status caches, or free-form prose status inference.",
  "history_preservation": "Prior WI-5299 evidence, corrected verdicts, NO-ACTION entries, and existing bridge files remain append-only. The repair changes only resolver behavior and tests after GO.",
  "baseline": {
    "work_item_state": "WI-5387 is open/backlogged with no prior bridge thread.",
    "project_authorization": "PAUTH-DISPATCHER-BLACK-BOX-WI5387-APPLICABILITY-CORRECTED-GO-20260716 is active and includes WI-5387.",
    "current_code_state": "choose_operative_version gives NO-ACTION precedence over later GO/VERIFIED/NO-GO statuses except latest WITHDRAWN."
  },
  "expected_result": {
    "corrected_go_after_no_action": "Applicability preflight does not shadow the corrected GO with the older NO-ACTION and resolves the operative file using explicit correction metadata.",
    "standalone_no_action": "A genuinely latest NO-ACTION with no later corrected verdict remains operative and LO-actionable.",
    "terminal_withdrawn": "Latest WITHDRAWN remains terminal operative content.",
    "tool_coherence": "Applicability and clause preflights agree on the numbered operative file or report the same explicit non-applicability reason."
  },
  "rollback": {
    "instructions": "If the resolver change broadens implementation authority or misroutes standalone NO-ACTION, revert the exact WI-5387 hunks and keep the work item open.",
    "verification": "Rerun focused applicability tests, candidate/live preflights, and representative corrected-verdict fixture checks."
  },
  "hard_invariants": [
    "No protected mutation occurs from this NEW entry alone.",
    "No source or test edit is authorized without fresh GO, matching claim, and implementation-start authorization.",
    "No dispatcher, TAFE, runtime, lease, credential, Git history, push, deployment, release, or unrelated file mutation is authorized.",
    "NO-ACTION remains a Prime-authored routing rejection of a prior LO GO or NO-GO, never an advisory close or terminal no-op."
  ]
}
```

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/bridge_applicability_preflight.py` and `platform_tests/scripts/test_bridge_applicability_preflight.py`.

## Specification Links

- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - defines NO-ACTION as a Prime-authored correction route back to Loyal Opposition, not terminal closure.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the numbered bridge chain and live bridge state to determine workflow authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - defines PAUTH as bounded owner evidence that does not replace bridge GO, target scoping, start packet, report, or verification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires current PAUTH and target bounds at proposal, claim, packet, and start gates.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - forbids using this PAUTH as an implementation bypass.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the machine-readable PAUTH, project, work-item, and target-path metadata above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links and preflight evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation verification to map executed tests to these linked requirements.
- `GOV-WORK-TREE-HYGIENE-001` - requires preserving foreign hunks and avoiding unrelated source/test adoption.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all proposal, source, test, and evidence paths inside the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the defect, PAUTH, proposal, tests, report, and verdict to remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports the artifact-first flow from defect evidence through verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps WI-5387 open until the resolver behavior is implemented and verified.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded PAUTH carriers and governed proposals for newly discovered fleet/bridge/TAFE/harness defects while preserving every downstream gate.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - owner correction anchoring canonical NO-ACTION semantics.
- WI-5387 work item evidence - records the corrected-GO/NO-ACTION operative-selection contradiction on `gtkb-wi5299-reissued-finalizer-failure-repair`.

## Owner Decisions / Input

No new owner decision is required. `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this bounded carrier and proposal. `PAUTH-DISPATCHER-BLACK-BOX-WI5387-APPLICABILITY-CORRECTED-GO-20260716` permits only bridge, metadata, governance evidence, source, and focused test work after every later bridge and implementation-start gate passes.

## Proposed Scope

- Replace or extend `choose_operative_version` so corrected verdicts after `NO-ACTION` are not shadowed by the older `NO-ACTION`.
- Use explicit metadata such as `Responds to:`, `Corrects:`, `Approved proposal:`, `Reviewed:`, and `Verified:` when present to identify the intended operative content.
- Preserve latest `WITHDRAWN` as terminal operative content.
- Preserve standalone latest `NO-ACTION` as operative when no later corrected LO verdict exists.
- Add focused tests for corrected GO after NO-ACTION, later VERIFIED-on-NO-ACTION coherence, standalone NO-ACTION, terminal WITHDRAWN, and packet-hash stability.
- Keep all parsing deterministic; do not infer authority from summaries, retired aggregate queue files, or status prose outside numbered bridge files.

## Out Of Scope

- Dispatcher, TAFE, runtime, lease, worker, or eligibility mutation.
- Changing bridge lifecycle semantics beyond applicability-preflight operative selection.
- Changing the clause preflight unless a later bridge explicitly approves a shared resolver extraction.
- Marking WI-5299, WI-5370, or any failed-finalization repair complete.
- Credential lifecycle, external-system mutation, destructive cleanup, git history rewrite, git push, deployment, release, or unrelated source/test/config edits.
- Whole-file adoption of foreign hunks in shared test/source files.

## Specification-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused tests in `platform_tests/scripts/test_bridge_applicability_preflight.py` covering corrected GO after NO-ACTION, standalone NO-ACTION, terminal WITHDRAWN, and later VERIFIED-on-NO-ACTION coherence | Corrected verdict metadata is honored; real NO-ACTION holds and WITHDRAWN terminality remain intact. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live applicability preflight on this WI-5387 proposal plus resolver fixture tests | Proposal has no missing required/advisory specs; resolver tests prove concrete spec links are harvested from the intended operative file. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must carry forward this mapping and executed test results | Loyal Opposition can verify every linked requirement against concrete tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | After GO, exact work-intent claim plus implementation-start packet for the two target paths | Protected mutation occurs only under current PAUTH, latest GO, target path, and start-packet authority. |
| `GOV-WORK-TREE-HYGIENE-001` | `git diff --check -- scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py` and implementation-report hunk attribution | No whitespace errors or foreign hunk adoption. |
| Source quality | `ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py` and `ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py` | No lint or format regressions on exact targets. |

## Acceptance Criteria

- Applicability preflight no longer selects an older `NO-ACTION` when a later corrected `GO` explicitly responds to or corrects that `NO-ACTION` and identifies the approved proposal.
- Applicability preflight and clause preflight no longer silently disagree about the operative numbered file for corrected-verdict chains; any remaining difference is explicit and justified by documented status semantics.
- Latest standalone `NO-ACTION` remains operative and LO-actionable when no corrected verdict exists.
- Latest `WITHDRAWN` remains terminal operative content.
- Packet hash output is stable for identical fixture content after the resolver repair.
- Implementation report includes exact commands, observed results, and hunk-level attribution.

## Risks / Rollback

Risk is moderate because applicability preflight is a mandatory gate for bridge review and verification. The implementation must be fixture-driven, status-aware, and conservative around `NO-ACTION` so it does not accidentally convert dependency holds into implementation authority.

Rollback is a focused revert of the WI-5387 source and test hunks after normal bridge authorization. Bridge files, PAUTH records, and evidence remain append-only audit history and are not deleted by rollback.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight Subsection

Pre-filing candidate checks are run against this exact completed content file before live filing:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5387-applicability-corrected-go-operative --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5387-applicability-corrected-go-operative-001.completed.md --json`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5387-applicability-corrected-go-operative --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5387-applicability-corrected-go-operative-001.completed.md`

The live filed proposal must be rechecked after the helper writes `bridge/gtkb-wi5387-applicability-corrected-go-operative-001.md`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
