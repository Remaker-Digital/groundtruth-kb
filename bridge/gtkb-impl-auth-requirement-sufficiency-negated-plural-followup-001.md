NEW

# Requirement-Sufficiency negated-plural follow-up

bridge_kind: prime_proposal
Document: gtkb-impl-auth-requirement-sufficiency-negated-plural-followup
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-24 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-prime-interactive-implauth-negation-followup-20260623
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive session; Prime Builder role; approval policy never; danger-full-access workspace

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4671

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_fab14_requirement_sufficiency.py"]

implementation_scope: source, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The prior WI-4671 repair fixed the implementation-authorization Requirement
Sufficiency classifier for future-scoped gap mentions and for the narrow negated
form "No new or revised requirement is needed". The classifier still false-flags
the equally natural plural subject form "New or revised requirements are not
needed before implementing this slice" as a requirement gap.

This residual bug is now blocking the GO'd benchmarking proposal
`bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-001.md`, whose operative
state says "Existing requirements sufficient" but whose explanatory sentence uses
that negated-plural form. The implementation-start packet correctly refuses to
proceed when the classifier returns `gap`; the repair must therefore go through
its own bridge proposal, GO review, implementation-start packet, implementation
report, and LO verification before the benchmarking work resumes.

The proposed implementation is a minimal classifier/test follow-up: make
`requirement_sufficiency_state()` treat negated gap-context sentences as
non-gap context when an operative sufficiency declaration is present, including
both "No new..." and "New or revised requirements are not..." forms. Preserve
the existing behavior that present-tense, non-negated declarations such as
"new or revised requirement required before implementation" remain `gap`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge-mediated authorization and
  preserves the implementation-start gate; this proposal repairs that gate
  without bypassing it.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active bounded PAUTH
  listed above includes `WI-4671` and allows source/test changes only after GO.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  Project Authorization, Project, and Work Item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  explicitly cites the governing specifications for the repair.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is derived
  from the classifier's required accept/reject behavior.
- `GOV-STANDING-BACKLOG-001` - `WI-4671` is the standing-backlog defect record
  for Requirement-Sufficiency classifier false positives.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the residual defect is preserved and
  remediated through durable project, WI, bridge, and report artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - favors this reviewable proposal and
  bridge lifecycle over an ad hoc direct repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation-start false
  positive crossed the threshold from transient observation to tracked repair.
- `.claude/rules/file-bridge-protocol.md` - defines the bridge proposal,
  work-intent, implementation-start, report, and LO verification lifecycle that
  this repair follows.

## Requirement Sufficiency

Existing requirements are sufficient. The listed bridge, project-authorization,
proposal-linkage, and spec-derived-verification requirements fully constrain
this source/test classifier follow-up.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` / file-bridge protocol: obtain LO `GO`, acquire
  the implementation-start packet for this bridge slug, and do not mutate
  protected source/test paths before that packet succeeds.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: implementation-start must
  validate the PAUTH metadata for
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` / `WI-4671` before edits.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: add regression coverage in
  `platform_tests/scripts/test_fab14_requirement_sufficiency.py` for:
  - sufficiency plus "New or revised requirements are not needed..." returns
    `sufficient`;
  - sufficiency plus "New or revised requirements are not required..." returns
    `sufficient`;
  - the existing non-negated present-tense gap cases still return `gap`.
- Run focused regression tests:
  `python -m pytest platform_tests/scripts/test_fab14_requirement_sufficiency.py -q --tb=short`
- Run repo-native quality checks on touched files:
  `python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_fab14_requirement_sufficiency.py`
  and
  `python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_fab14_requirement_sufficiency.py`
- After the repair, re-check the previously blocked benchmarking proposal by
  confirming `requirement_sufficiency_state()` classifies
  `bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-001.md` as `sufficient`.

## Prior Deliberations

- `DELIB-20265586` - owner mass project authorization on 2026-06-23; its active
  bridge-protocol-reliability PAUTH snapshot includes `WI-4671` and allows
  source/test implementation.
- `DELIB-20265284` - original WI-4671 owner decision to park the prior poison-pill
  dispatch thread and repair the Requirement-Sufficiency parser.
- DELIB-20260623-WI4587-REQ-SUFFICIENCY - owner decision confirming the
  benchmarking bridge proposal has no requirement gap; this exposed the residual
  classifier false positive but does not waive the implementation-start gate.
- `bridge/gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix-001.md`
  through `-004.md` - prior VERIFIED WI-4671 repair; this follow-up preserves its
  intent and adds the missed negated-plural form.
- `bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-001.md` - blocked
  downstream GO'd proposal whose Requirement Sufficiency section demonstrates
  the residual false positive.

## Owner Decisions / Input

No additional owner input is required. The owner has explicitly directed this
repair to be proposed and driven through bridge verification before resuming the
benchmarking project, and the active PAUTH above covers `WI-4671` source/test
changes. The owner decision for the downstream benchmarking proposal is cited as
evidence of the false positive, not as a bypass of this repair's bridge gate.

## Risk / Rollback

Risk is limited to the implementation-start Requirement-Sufficiency classifier.
The repair must not weaken genuine gap detection; tests will retain positive gap
coverage. Rollback is a single revert of the classifier/test diff if LO finds
authorization behavior broadened beyond negated explanatory context.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
bridge file for `gtkb-impl-auth-requirement-sufficiency-negated-plural-followup`.
No prior version is deleted or rewritten. Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - corrects a false-positive authorization classifier defect and adds focused
regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
