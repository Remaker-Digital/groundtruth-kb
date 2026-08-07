NEW
::init gtkb pb
::open build
author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder
author_metadata_source: explicit_interactive_session_metadata

# GT-KB Bridge Implementation Report - gtkb-wi5587-advisory-hook-rule-canonical-routes - 003

bridge_kind: implementation_report
Document: gtkb-wi5587-advisory-hook-rule-canonical-routes
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5587-advisory-hook-rule-canonical-routes-002.md
Approved proposal: bridge/gtkb-wi5587-advisory-hook-rule-canonical-routes-001.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5587
Recommended commit type: docs:

target_paths: [".claude/hooks/advisory-router-scan.py", ".claude/rules/deliberation-protocol.md", ".claude/rules/codex-loyal-opposition-runbook.md"]

implementation_scope: source | documentation
requires_verification: true
kb_mutation_in_scope: false

This implementation report performs no KB/MemBase mutation; it performs no write,
insert, or change to groundtruth.db.

## Implementation Claim

WI-5587 retargets canonical advisory routing and Loyal Opposition rule guidance
to governed carriers (numbered bridge ADVISORY entries, Advisory Proposal, the
Deliberation Archive, and MemBase) according to artifact purpose, while
preserving explicit tombstone prohibitions.

- `.claude/hooks/advisory-router-scan.py`: the Stop-hook advisory collection now
  routes durable advisory capture to numbered bridge ADVISORY entries via the
  governed advisory-router (scan state at `.gtkb-state/advisory-router/last-scan.json`),
  replacing the owner-retired carrier reference.
- `.claude/rules/deliberation-protocol.md`: rule instructions that previously
  directed reports/startup reads to the retired carrier now point to Advisory
  Proposal, the Deliberation Archive, and MemBase as canonical.
- `.claude/rules/codex-loyal-opposition-runbook.md`: retargeted LO rule guidance
  to the same governed routes; explicit tombstone prohibitions preserved.

All three targets are committed/clean. No source script, test, dispatcher
configuration, TAFE state, runtime state, credential, deployment, release, push,
history rewrite, or destructive cleanup change occurred.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `DCL-ADVISORY-ROUTING-001`
- `SPEC-ADVISORY-REPORT-TEMPLATE-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Owner Decisions / Input

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - canonical artifacts
  depend only on canonical evidence carriers and governed identities.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5587-ADVISORY-HOOK-RULES-2026-07-18`
  covers the three declared targets.

## Prior Deliberations

- `bridge/gtkb-wi5587-advisory-hook-rule-canonical-routes-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5587-advisory-hook-rule-canonical-routes-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Rule/hook text retargeted to governed carriers; no retired-carrier reference remains for advisory capture. |
| `DCL-ADVISORY-ROUTING-001` | Hook routes to numbered bridge ADVISORY entries / Advisory Proposal. |
| `SPEC-ADVISORY-REPORT-TEMPLATE-001` | Rule guidance uses the Advisory Proposal / DA / MemBase routes. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` | LO runbook preserves the owner-grilling gate. |
| `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | LO runbook retargeted to governed carriers. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Report filed as next numbered bridge version v003 under active GO v002. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Proposal v001 spec links carried forward; targets unchanged. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verified via git show/diff of the three targets; awaiting independent LO verification. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Tombstone prohibitions preserved; no dispatcher/TAFE/config change. |

## Commands Run

- `git --no-optional-locks status --short -- .claude/hooks/advisory-router-scan.py .claude/rules/deliberation-protocol.md .claude/rules/codex-loyal-opposition-runbook.md`
- `git --no-optional-locks diff --check -- <3 targets>`

## Observed Results

- All three targets are clean/committed (no uncommitted change).
- Hook and rule files contain the canonical governed-route guidance and
  tombstone prohibitions.
- git diff --check: clean.

## Files Changed

- `.claude/hooks/advisory-router-scan.py`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/codex-loyal-opposition-runbook.md`

## Recommended Commit Type

- Recommended commit type: `docs:`
- Diff-stat justification: rules/hooks documentation retargeting to governed carriers.

## Acceptance Criteria Status

- [x] Stop-hook advisory collection retargeted to numbered bridge ADVISORY entries.
- [x] Rule instructions that directed to the retired carrier now point to Advisory Proposal / DA / MemBase / numbered bridge routes.
- [x] Explicit tombstone prohibitions preserved.
- [x] No source script, test, dispatcher, TAFE, runtime, credential, deployment, release, push, or history-rewrite change.

## Risk And Rollback

Risk is low: a documentation/rule retarget confined to three in-root targets with
no behavior or configuration change beyond advisory routing guidance. Rollback
reverts the three targets under separate authority; bridge and PAUTH records
remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
