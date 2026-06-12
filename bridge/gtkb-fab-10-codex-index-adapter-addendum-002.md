GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-10-codex-index-adapter-addendum
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md

# Loyal Opposition Review - FAB-10 Codex INDEX Adapter Addendum

## Verdict

GO.

The addendum is a narrow target-scope correction for the already-approved
FAB-10 HYG-039 work. It authorizes the missing Codex apply_patch adapter path
that must forward `bridge/INDEX.md` edits to the canonical bridge-compliance
gate. The proposal does not expand helper-only CAS writes, does not weaken
`bridge/INDEX.md` as canonical workflow state, and does not restore the retired
pollers.

## Same-Session Guard

The proposal under review was authored by Codex Prime Builder harness A in
session `019ebc0a-181f-7791-a64b-482f97486014`. This Loyal Opposition review is
in a different session context and did not create the proposal.

## Dependency And Precedence Check

- `WI-4422` remains open/backlogged and has no parsed `depends_on_work_items` or
  `blocks_work_items`.
- The coupled FAB-01 dispatch-substrate thread is latest `VERIFIED` with
  bridge drift `[]`, so the FAB-10 adapter addendum is no longer blocked by the
  launchability/event-source prerequisite.
- The original FAB-10 thread is latest `GO` and explicitly kept helper-only
  INDEX writes out of scope for a follow-on slice; this addendum preserves that
  constraint.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-10-codex-index-adapter-addendum --content-file bridge\gtkb-fab-10-codex-index-adapter-addendum-001.md
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:b4076ace7189057defc19b6f64df012b1e5d491f6cc73c0f0425fa2cd42bdaac`
- bridge_document_name: `gtkb-fab-10-codex-index-adapter-addendum`
- content_source: `pending_content`
- content_file: `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md`
- operative_file: `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The advisory omissions do not block GO.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-10-codex-index-adapter-addendum --content-file bridge\gtkb-fab-10-codex-index-adapter-addendum-001.md
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-10-codex-index-adapter-addendum`
- Operative file: `bridge\gtkb-fab-10-codex-index-adapter-addendum-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

- `DELIB-FAB10-REMEDIATION-20260610` - owner selected INDEX
  well-formedness lint now and helper-only INDEX writes later.
- `DELIB-20261697` - harvested Loyal Opposition GO for the original FAB-10
  proposal, including constraints against retired poller restoration and
  weakening `bridge/INDEX.md`.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` and `-002.md`
  - original FAB-10 proposal and GO verdict.

## Scope Evidence

The proposed addendum fixes a real target-path omission:

```text
python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-fab-10-dispatch-telemetry-claim-contract --candidate-paths .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py --json
```

Observed result:

```text
verdict: out_of_scope_drift
out_of_scope: [".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py"]
approved target_paths: ["scripts/cross_harness_bridge_trigger.py", ".claude/hooks/bridge-compliance-gate.py", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**"]
```

Live source inspection also supports the proposal's claim: the current adapter
predicate only matches versioned bridge files through
`BRIDGE_VERSIONED_FILE_RE = re.compile(r"^bridge/.+-\d{3}\.md$")`, so
`bridge/INDEX.md` apply_patch edits are not forwarded to the canonical gate.
`.codex/hooks.json` already registers
`.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd` for
`apply_patch`, so no hook-registration change is required unless implementation
finds drift.

## Implementation Constraints

- Implementation scope is limited to
  `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` and focused
  tests under `platform_tests/scripts/**`.
- Keep the adapter a thin dispatcher to `.claude/hooks/bridge-compliance-gate.py`;
  do not duplicate bridge INDEX parsing policy in the Codex adapter.
- Do not change helper-only CAS-protected INDEX writes; that remains follow-on
  work per the owner decision.
- Do not restore the retired OS poller or retired smart poller.
- Do not weaken `bridge/INDEX.md` as canonical workflow state.
- Do not mutate `groundtruth.db`.

## Findings

No blocking findings.

## Opportunity Radar

No separate advisory is needed from this review. The deterministic-service
opportunity is already the subject of this addendum: route Codex apply_patch
INDEX writes through the same canonical bridge gate rather than relying on
manual review to catch malformed INDEX edits.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
