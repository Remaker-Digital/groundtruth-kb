NEW

# Umbrella Closeout Report - GTKB-GOV AskUserQuestion Enforcement Stack

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: Loyal Opposition GO at
`bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-004.md`
Requested bridge disposition: `VERIFIED`

## Claim

The AskUserQuestion enforcement-stack umbrella is complete enough for Loyal
Opposition umbrella verification. Sub-slices A through F are all latest
`VERIFIED` in `bridge/INDEX.md`, and the umbrella end-state release governance
metrics pass in the current checkout.

This closeout also fixed one end-state metric false positive discovered during
the umbrella check: the shared bridge-compliance helper treated any Owner
Decisions section containing the word `none` as placeholder-only, even when the
section also contained concrete owner-decision evidence. The helper now rejects
only placeholder-only Owner Decisions sections.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this closeout is filed in `bridge/` and
  registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report
  carries forward the umbrella GO and sub-slice verification artifacts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - umbrella verification
  maps to sub-slice VERIFIED status plus executed end-state tests below.
- `GOV-OWNER-DECISION-SURFACING-001`,
  `GOV-REQUIREMENTS-COLLECTION-HOOK-001`, and
  `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` - the sub-slices implement
  AUQ-only surfacing, evidence, bridge review, requirements collection, and
  release metrics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the enforcement program is preserved
  as durable bridge, hook, rule, metric, and test artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - this umbrella did not introduce
  new `applications/` content and did not treat Agent Red as live GT-KB state.

## Sub-Slice Status Evidence

| Umbrella slice | Latest bridge status |
|---|---|
| Sub-slice A - hook re-enable + regex tightening | `VERIFIED: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` |
| Sub-slice B - Prime Builder AUQ-only rule | `VERIFIED: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md` |
| Sub-slice C - bridge review gate | `VERIFIED: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-006.md` |
| Sub-slice D - durable evidence audit | `VERIFIED: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-d-evidence-audit-008.md` |
| Sub-slice E - requirements collector | `VERIFIED: bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-010.md` |
| Sub-slice F - release metrics + gate promotion | `VERIFIED: bridge/gtkb-gov-auq-enforcement-stack-slice-f-release-metrics-2026-05-04-006.md` |

## End-State Finding And Fix

During closeout, `python scripts/release_governance_metrics.py` initially
failed `_check_uncited_owner_input_bridges` on two compliant VERIFIED bridge
thread files whose Owner Decisions sections contained concrete evidence plus
phrases such as "Current owner input needed: none."

Fix applied:

- `.claude/hooks/bridge-compliance-gate.py`: added
  `OWNER_DECISIONS_PLACEHOLDER_LINE_RE` and changed
  `_has_concrete_owner_decisions_section()` so placeholder rejection applies
  only when every nonblank line in the section is placeholder-only.
- `groundtruth-kb/tests/test_owner_decisions_section_gate.py`: added hook
  regression coverage for a substantive Owner Decisions section that also says
  no current owner input is needed.
- `groundtruth-kb/tests/test_release_gate_metrics.py`: added release-metric
  regression coverage for a VERIFIED thread with the same section shape.

## Specification-Derived Verification

| Test ID | Umbrella requirement | Procedure | Result |
|---|---|---|---|
| T-sub-slices | All A-F sub-slices VERIFIED | Direct read of `bridge/INDEX.md` for the six sub-slice document entries | PASS - all latest `VERIFIED` |
| T-end-state-1 | Release metrics PASS and gate enforcement active | `python scripts/release_governance_metrics.py` | PASS - all 3 release governance metrics clean |
| T-out-of-applications | Umbrella did not create `applications/` content | `git diff --name-only -- applications/` | PASS - empty output |
| T-block-emission-env | Hook block emission default active | `python -c "import os; print(os.environ.get('GTKB_BLOCK_ON_PROSE_DECISION_ASK', '1'))"` | PASS - `1` |
| T-owner-section-helper | Owner Decisions helper handles substantive section with `none` status | `python -m pytest groundtruth-kb/tests/test_owner_decisions_section_gate.py groundtruth-kb/tests/test_release_gate_metrics.py -q --tb=short` | PASS - 19 passed, 1 warning |
| T-style | Changed helper/tests style | `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/tests/test_owner_decisions_section_gate.py groundtruth-kb/tests/test_release_gate_metrics.py` | PASS |
| T-format | Changed helper/tests formatting | `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/tests/test_owner_decisions_section_gate.py groundtruth-kb/tests/test_release_gate_metrics.py` | PASS - 3 files already formatted |

The warning is the existing upstream ChromaDB deprecation warning.

## Changed Files

- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/tests/test_owner_decisions_section_gate.py`
- `groundtruth-kb/tests/test_release_gate_metrics.py`
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-005.md`
- `bridge/INDEX.md`

## Residual Risk

This closeout did not rerun the full release-candidate gate. The focused
end-state command that Sub-slice F promotes is now clean, and the targeted
regressions cover the false-positive class found during closeout.

## Decision Needed From Owner

None.

