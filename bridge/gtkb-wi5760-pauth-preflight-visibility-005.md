REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher deliberately disabled

bridge_kind: prime_proposal
Document: gtkb-wi5760-pauth-preflight-visibility
Version: 005
Date: 2026-07-30 UTC
Responds to: bridge/gtkb-wi5760-pauth-preflight-visibility-004.md

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5760

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/pauth_finalization_exposure_sweep.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_pauth_finalization_exposure_sweep.py"]

# WI-5760 — Narrowed PAUTH Operation-Time Preflight Visibility

## Revision Summary

This revision accepts NO-GO-004 and narrows the executable cohort to the source/test/bridge classes already covered by the cited active program PAUTH v3. It keeps Slices A, C, and D; removes protected Slice B; carries the closed owner decisions exactly; and introduces no dependency on the pending v2 supersession of `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`.

The revision removes `scripts/pauth_cohort_preflight.py` and its test because `DELIB-202667681` selected integration into `scripts/bridge_applicability_preflight.py`. It removes `scripts/implementation_authorization.py` and its test because this slice reuses the canonical operation-time evaluator and existing PAUTH decode surface without changing the post-GO gate. It also removes the verify skill, review rule, formal-approval glob, generated adapter, and registry claims because Slice B is explicitly deferred.

## Problem

The mandatory applicability preflight does not expose the canonical project-authorization operation-time decision before `GO` or before terminal verification. Reviewers can therefore approve a target cohort that the implementation-start or finalization gate must later deny. WI-5741 demonstrated the terminal form: implementation targets were green, but the numbered bridge chain added a `bridge` mutation class that the cited PAUTH did not authorize.

The canonical evaluator already exists at `groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`. This revision surfaces that same decision through an existing mandatory review command and adds a read-only exposure sweep; it does not create a second authority implementation.

## Current Project Authority

- `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` is active.
- WI-5760 is an active member through `PWM-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI-5760`, active version 2, order 4.
- `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` is active v3, has `included_work_item_ids: null` and `excluded_work_item_ids: null`, and allows `source`, `test_addition`, `governance_evidence`, and `bridge`.
- Under current formal v1 semantics, a null/empty included-WI list falls back to active project membership; this exact narrowed cohort is therefore executable now. The owner's project-only rule in `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` is consistent with that result, but this revision does not claim that the pending DCL v2 already exists.
- `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-WI5760-SLICEB-20260729` is historical evidence only and is neither cited nor used.

## Recorded PAUTH Operation-Time Evaluation

A refreshed read-only evaluation on 2026-07-30 used program PAUTH v3, evaluator v1, and taxonomy v1.

| Envelope | Operations | Cohort | Result |
| --- | --- | --- | --- |
| proposal | `implementation_packet_create`, `implementation_start` | the four declared target paths | `allowed=true`, `reason_code=allowed` for both operations |
| finalization | `git_commit`, `protected_mutation` | the four target paths plus `bridge/gtkb-wi5760-pauth-preflight-visibility-001.md` through proposed `-005.md` | `allowed=true`, `reason_code=allowed` for both operations |

The two scripts classify as `source`; the two test modules classify as `test` and are authorized by `test_addition`; the numbered chain classifies as `bridge`. No configuration or metadata path is present.

## Proposed Change

### Slice A — Fold PAUTH cohort evaluation into the existing applicability preflight

Extend `scripts/bridge_applicability_preflight.py` so its normal review-time execution also resolves the operative proposal's cited PAUTH and evaluates the exact phase-appropriate cohort through the canonical evaluator:

- proposal review: declared implementation `target_paths` evaluated for `implementation_packet_create` and `implementation_start`;
- implementation/finalization review: operative implementation/report targets union the complete numbered bridge chain, including the next verdict version, evaluated for `git_commit` and `protected_mutation`.

The existing bridge kind and lifecycle state select the envelope automatically, so the mandatory preflight cannot silently omit the check. JSON and Markdown output include `allowed`, `reason_code`, requested operations, per-target classifications, and evaluator/taxonomy identity. Any denial is blocking with exit 5; evaluator, taxonomy, PAUTH-load, or malformed-envelope failures fail closed with a distinct non-zero result. Enforcement is review-time only: no filing-time hook, PreToolUse behavior, dispatcher behavior, or TAFE surface changes.

The implementation imports the canonical evaluator and reuses existing decode behavior. It does not modify `scripts/implementation_authorization.py` and does not change post-GO `begin` semantics.

### Slice C — Add the finalization exposure sweep

Add `scripts/pauth_finalization_exposure_sweep.py`, a read-only CLI that scans status-bearing numbered bridge files for non-terminal threads, projects each terminal cohort (operative implementation/report targets union numbered chain), resolves the cited PAUTH, and evaluates `git_commit` plus `protected_mutation` through the canonical evaluator.

Markdown and JSON output distinguish mutation-class denial, missing PAUTH, PAUTH-load/evaluator failure, and authorized threads. Regenerable output may be written only under `.gtkb-state/pauth-exposure/`; no MemBase, bridge, dispatcher, or TAFE state is mutated.

### Slice D — Tests

Add fixture-rooted behavioral coverage to `platform_tests/scripts/test_bridge_applicability_preflight.py` and new `platform_tests/scripts/test_pauth_finalization_exposure_sweep.py`. Tests may not read or mutate the live MemBase or live bridge.

## Explicit Slice B Deferral

This revision does not edit `.claude/rules/codex-review-gate.md`, `.claude/skills/gtkb-verify/SKILL.md`, any generated Codex adapter or registry, or `.groundtruth/formal-artifact-approvals/**`. It makes no managed-skill regeneration promise and requires no narrative/formal approval packet.

The protected review-surface documentation remainder stays deferred project work. It requires its own reviewed bridge after WI-5781's project-only DCL v2 is formalized and a governed whole-project PAUTH for `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` covers `configuration` and `metadata`. A WI-5760-only supplemental PAUTH is not an executable remedy under the owner's project-only direction.

## Closed Owner Decisions / Input

- `DELIB-202667681` — fold into `scripts/bridge_applicability_preflight.py`; no standalone CLI.
- `DELIB-202667682` — mandatory review-time-only enforcement; no filing-time PreToolUse block.
- `DELIB-202667683` — proposal operations are `implementation_packet_create` and `implementation_start`; finalization operations are `git_commit` and `protected_mutation`.
- `DELIB-202667684` — bridge-protocol PAUTHs must explicitly authorize the `bridge` class; no append-only writer exemption.
- `DELIB-202667685` — SF-1 repaired with registered token `dispatcher_mutation`; active program PAUTH v3 reflects the repair.
- `DELIB-202667686` — prior WI-only Slice B authorization is historical and is not used by this narrowed revision.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level implementation approval direction; WI-5781 owns formal supersession.

No owner question remains for this narrowed cohort.

## Requirement Sufficiency

Existing requirements are sufficient for this narrowed scope. No new or revised requirement is required before implementation. The pending DCL v2 changes the general project/WI model but is not a precondition here because the cited PAUTH has a null included-WI list and WI-5760 is an active member of its active project under the current v1 fallback semantics.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active project authorization is the implementation envelope.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the one cited program PAUTH covers every selected class.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the canonical decision surfaced by both tools.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — current v1 semantics cited accurately; v2 remains pending.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — neither GO nor historical supplemental authority bypasses the selected envelope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — finalization cohorts include the numbered bridge chain and require explicit bridge authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the existing applicability preflight is the integration surface.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — terminal review evaluates the exact commit cohort before verdict filing.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — review-time and post-GO gates share one canonical authority.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` and `SPEC-1830` — deterministic commands replace ad-hoc reviewer inference.
- `GOV-10`, `GOV-12`, and `SPEC-1662` — production-interface, work-item-derived, behavioral tests.
- `GOV-17` — reviewed automation-script modification.
- `GOV-WORK-TREE-HYGIENE-001` — target ownership and sequencing are checked immediately before implementation.

## Prior Deliberations

- `DELIB-202667531`, `DELIB-202667533`, and `DELIB-202667534` — advisory-correction project, program PAUTH, and WI-5760 consolidation authority.
- `DELIB-202667529` — WI-5741 terminal-authorization incident precedent; evidence for the defect class, not authority for this revision.
- `DELIB-202667681` through `DELIB-202667686` — complete closed WI-5760 decision register.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-only direction and WI-5781 pull-forward.
- Source advisories: `bridge/gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory-001.md` and `-002.md`.
- Review chain: `bridge/gtkb-wi5760-pauth-preflight-visibility-002.md` through `-004.md`; NO-GO-004 expressly permits this narrowed-authorized-cohort disposition.

## Spec-Derived Test Plan

| Requirement | Test | Expected result |
| --- | --- | --- |
| Project authorization / two-envelope behavior | `test_pauth_proposal_allowed_finalization_denied_when_bridge_class_missing` | Proposal operations pass while finalization operations deny with `target_mutation_class_not_allowed` naming numbered bridge paths; preflight exits 5. |
| Authorized exact cohort | `test_pauth_phase_cohort_allowed_and_reported` | Both phase-selected operation sets return `allowed`, with evaluator/taxonomy identity and per-target classes in JSON/Markdown. |
| Fail-closed authority loading | `test_pauth_unknown_forbidden_operation_fails_closed` | Unregistered forbidden token, missing PAUTH, malformed PAUTH, or unavailable evaluator never produces an allowed result and returns distinct blocking evidence. |
| Canonical-authority parity | `test_pauth_preflight_matches_canonical_evaluator` | For identical fixture PAUTH, targets, and operations, the preflight result exactly matches `evaluate_envelope`; no local policy reimplementation exists. |
| Exposure inventory | `test_sweep_enumerates_only_exposed_nonterminal_threads` | Authorized, class-denied, missing-PAUTH, evaluator-failure, and terminal fixtures are classified correctly; terminal threads are omitted from exposure rows. |
| Root/output safety | `test_sweep_is_fixture_rooted_and_idempotent` | Output is stable across reruns and written only under the fixture `.gtkb-state/pauth-exposure/`; no live DB or bridge mutation. |

Verification commands:

`python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_pauth_finalization_exposure_sweep.py -q --tb=short`

`python -m ruff check scripts/bridge_applicability_preflight.py scripts/pauth_finalization_exposure_sweep.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_pauth_finalization_exposure_sweep.py`

`python -m ruff format --check scripts/bridge_applicability_preflight.py scripts/pauth_finalization_exposure_sweep.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_pauth_finalization_exposure_sweep.py`

Also run both mandatory bridge preflights against the implementation report and a read-only operation-time evaluation of the exact finalization cohort.

## Acceptance Criteria

1. The mandatory applicability preflight evaluates and reports the exact phase-appropriate PAUTH envelope through the canonical evaluator.
2. A denial or authority-load failure blocks review; no filing-time hook is added.
3. The finalization cohort includes all implementation/report targets and the complete numbered chain including the next verdict version.
4. The exposure sweep deterministically inventories every non-terminal exposed thread and writes only regenerable fixture/root-local output.
5. The four declared files are the only implementation targets; Slice B and all configuration/metadata work remain deferred.
6. Targeted pytest, ruff check, ruff format check, applicability preflight, clause preflight, and exact finalization-cohort evaluation pass.

## Target Ownership and Implementation Start

At refreshed drafting time, `scripts/bridge_applicability_preflight.py` and `platform_tests/scripts/test_bridge_applicability_preflight.py` exist and are clean; `scripts/pauth_finalization_exposure_sweep.py` and `platform_tests/scripts/test_pauth_finalization_exposure_sweep.py` are absent and have no Git-status entry. WI-5760 has no work-intent claim.

Historical/live GO threads overlap the existing applicability-preflight source/test pair, including WI-5408, WI-5460/WI-5465, WI-5554, and WI-5648; all four claim readbacks remain `null`. Clean bytes and null claims do not waive fresh sequencing checks.

After an independent fresh `GO`, Prime Builder must recheck target cleanliness and current claims, acquire an exact work-intent claim for these four paths, and create a fresh implementation-start packet. Stop on any collision or dirty foreign change. The dispatcher and TAFE remain disabled and are outside scope.

## Risk and Rollback

Risk is low-to-medium: one existing mandatory read-only preflight gains a fail-closed authority check, and one new read-only inventory command is added. The principal compatibility risk is incorrect phase/cohort resolution; fixture tests cover proposal/finalization divergence, next-verdict inclusion, and malformed authority data.

Rollback is file-scoped: revert the applicability-preflight change and its additive tests, then delete the new sweep and its test. No schema, canonical record, hook, dispatcher, TAFE, credential, deployment, or external-system state is migrated.

Recommended commit type: feat

## Verification Questions for Loyal Opposition

1. Does automatic phase selection make the existing mandatory applicability preflight enforce the closed OD-B review-time-only decision without protected workflow-document edits?
2. Does the finalization projection match the terminal commit cohort, including the next verdict version?
3. Does the narrowed target set remain wholly allowed under the one cited program PAUTH and avoid every configuration/metadata dependency identified in NO-GO-004?

## Pre-Filing Checks

Before publication, run the credential scan, bridge compliance audit-only check, applicability preflight, mandatory clause preflight, phantom-spec existence check, and inline-JSON `target_paths` parse check against the candidate. File only if all blocking checks pass. Do not activate the dispatcher or TAFE.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
