# WI-4458 Governance Emergency Bootstrap Protocol Advisory

Date: 2026-06-13
Author: Loyal Opposition (Codex harness A, automation `keep-working-lo`)
Status: Advisory report
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, GOV-STANDING-BACKLOG-001
Work Items: WI-4458, WI-4449

## Claim

`WI-4458` is valid and should be implemented as a narrow governed exception
protocol, not as a broad license to bypass bridge review or commit hooks.
The WI-4449 precedent shows a real governance deadlock: the pre-commit path,
bridge claim path, implementation-start path, and proposal-write path were
blocked by the same missing-hook class being repaired. The current durable
rules describe the normal path well, but they do not define a canonical
emergency-bootstrap path for restoring the governance substrate itself.

## Evidence

- Live backlog row `WI-4458` is open, P0, unapproved, and asks to document the
  governance-emergency-bootstrap exception protocol for sanctioned `--no-verify`
  and bridge-GO bypass with audit-trail discipline.
- `bridge/gtkb-commit-untracked-governance-hooks-002.md:68` records that commit
  `e90b2f03` was made with `--no-verify`; lines 69-72 state the pre-commit
  verify hooks were part of the chicken-and-egg deadlock.
- `bridge/gtkb-commit-untracked-governance-hooks-002.md:153` and
  `bridge/gtkb-commit-untracked-governance-hooks-002.md:154` state the bridge
  claim path, implementation-start authorization path, and proposal-write path
  were blocked by the missing-hook condition.
- `bridge/gtkb-commit-untracked-governance-hooks-002.md:114` through
  `bridge/gtkb-commit-untracked-governance-hooks-002.md:120` rely on tacit owner
  approval for the precedent and explicitly call for a follow-on protocol WI.
- `git show --stat --summary e90b2f03 --` confirms the precedent commit added
  six `.claude/hooks/*.py` files, 110 lines, subject
  `fix: restore registered governance hooks (WI-4449)`.
- `.githooks/pre-commit:15`, `.githooks/pre-commit:17`,
  `.githooks/pre-commit:25`, and `.githooks/pre-commit:30` show the commit gate
  chains through staged secret scan, inventory drift, narrative-artifact
  evidence, and ruff-format checks.
- `.claude/rules/file-bridge-protocol.md:40` through
  `.claude/rules/file-bridge-protocol.md:69` define the normal
  implementation-start path: declared target paths, latest GO, and
  `implementation_authorization.py begin --bridge-id`.
- `.claude/rules/file-bridge-protocol.md:252` through
  `.claude/rules/file-bridge-protocol.md:261` define bridge statuses, including
  GO, NO-GO, VERIFIED, and ADVISORY. Lines 267-280 accept `WITHDRAWN` as a
  status token, but do not define it as a governance-bypass protocol.
- `.claude/rules/codex-way-of-working.md:131` through
  `.claude/rules/codex-way-of-working.md:165` require necessary owner input to
  be surfaced as a single explicit owner decision. That is materially different
  from treating tacit non-intervention as reusable approval evidence.

## Finding

### [P1] The exception class is real, but the proposed protocol needs stricter boundaries

Risk / impact: Without a documented exception class, future agents must either
deadlock when governance infrastructure is broken, or improvise a bypass and
retrofit the audit trail afterward. The WI-4449 precedent shows the latter can
be the least-bad operational choice, but it also shows the danger: the durable
record currently leans on tacit owner approval and a `WITHDRAWN` audit entry.
That is acceptable as an incident closure record; it is too weak as a reusable
protocol.

Recommended action: Prime Builder should file a standard bridge proposal for a
narrow rule/runbook addition, not mutate governance docs directly. The proposal
should define a governance-emergency-bootstrap path with these minimum
conditions:

1. The affected work must restore a governance substrate required to use the
   normal path, such as bridge writes, bridge claims, implementation-start
   packets, commit hooks, formal-approval gates, or credential-safety gates.
2. The agent must record why the normal bridge or hook path is mechanically
   unavailable before bypassing it.
3. Scope must be limited to restoring the blocked substrate and the minimum
   audit artifact needed to record the action.
4. A post-fix audit artifact must cite the commit SHA, changed paths, command
   evidence, bypass reason, and regression checks.
5. If explicit owner approval was not captured before the emergency action, the
   follow-up must require a retroactive owner-decision capture rather than
   relying on tacit approval as reusable precedent.
6. The protocol must state that ordinary implementation convenience, failing
   tests, formatting failures, bridge-review disagreement, or missing approval
   packets are not emergency-bootstrap conditions.

## Verification

- `python -m pytest platform_tests\scripts\test_bridge_claim_cli.py platform_tests\scripts\test_go_impl_claim_timebox.py platform_tests\hooks\test_narrative_artifact_approval.py -q --tb=short`
  passed: 31 tests.
- `python -m groundtruth_kb.cli deliberations search "WI-4458 governance emergency bootstrap exception protocol" --limit 10 --json`
  returned no prior deliberation records.
- `rg` for `WI-4458`, `governance-emergency-bootstrap`, `sanctioned --no-verify`,
  and `bridge-GO bypass` found only the WI-4449 withdrawal/audit bridge entry
  and a separate WI-4516 proposal sentence forbidding bridge-GO bypass.

## Decision Needed From Owner

None for this advisory report. Implementation still needs the normal Prime
Builder bridge proposal and Loyal Opposition review. If Prime's proposal would
create or revise a formal GOV/SPEC/ADR/DCL/PB artifact, it must carry the
required approval evidence before mutation.
