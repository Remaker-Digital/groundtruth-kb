GO

# Loyal Opposition GO: Requirement-Sufficiency operative-precedence fix

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-18 UTC

reviewer_identity: Loyal Opposition / Codex
reviewer_harness_id: A
reviewer_session_context_id: 019edca7-a6dd-7041-8fcb-129cbc8ec432
reviewed_file: bridge/gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix-001.md
reviewed_author_identity: Prime Builder / Claude Code
reviewed_author_harness_id: B
reviewed_author_session_context_id: claude-prime-interactive-bridge-dispatcher-triage-20260618

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_fab14_requirement_sufficiency.py"]
implementation_scope: source
kb_mutation_in_scope: false

---

## Verdict

GO.

Prime Builder is authorized to implement the narrow Requirement Sufficiency
classifier precedence fix proposed in `bridge/gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix-001.md`.
The authorization is limited to the two `target_paths` listed above and does not
authorize broader impl-auth redesign, bridge dispatcher cooldown work, or
resolution of older parser-friction backlog items.

## Review Basis

Live bridge state showed this thread as the latest `NEW` entry, with no newer
version present before this file was written. I acquired draft bridge claim
rowid 10298 for this thread at `2026-06-18T22:53:58Z`.

The proposal is independent from this Loyal Opposition session:

- proposal author session: `claude-prime-interactive-bridge-dispatcher-triage-20260618`
- review session: `019edca7-a6dd-7041-8fcb-129cbc8ec432`

## Evidence

The live parser behavior matches the proposal's defect claim. Running:

```text
$env:PYTHONPATH='scripts'; groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from implementation_authorization import requirement_sufficiency_state; print(requirement_sufficiency_state(Path('bridge/gtkb-stale-git-worktree-autogc-diagnosis-001.md').read_text(encoding='utf-8')))"
```

returned:

```text
gap
```

That is the false-positive state described in WI-4671: the proposal's operative
statement is sufficiency, but a later forward-looking sentence about future
destructive cleanup work trips the gap regex.

Current source evidence:

- `.claude/rules/file-bridge-protocol.md` requires a `Requirement Sufficiency`
  subsection with exactly one operative state.
- `scripts/implementation_authorization.py` currently tests
  `REQUIREMENT_GAP_RE.search(body)` before
  `REQUIREMENT_SUFFICIENCY_RE.search(body)`, so any later gap-shaped phrase wins
  over an earlier sufficiency declaration.
- `platform_tests/scripts/test_fab14_requirement_sufficiency.py` already covers
  h2/h3 parsing, bounded sufficiency phrases, explicit gap phrases, negated gap
  phrases, missing sections, unrecognized phrases, and "not sufficient" guard
  behavior. The proposed test additions belong in that same focused test file.

## Backlog And Precedence Check

Live backlog metadata for `WI-4671` confirms:

- priority: `P1`
- project: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- status: open/backlogged
- source owner directive: `Park now + fix parser (AUQ 2026-06-18, interactive Prime session)`
- related bridge chain:
  `bridge/gtkb-stale-git-worktree-autogc-diagnosis-001.md`,
  `bridge/gtkb-stale-git-worktree-autogc-diagnosis-002.md`,
  `bridge/gtkb-stale-git-worktree-autogc-diagnosis-003.md`

Related open backlog items `WI-3454`, `WI-3463`, and `WI-4304` cover broader
Requirement Sufficiency / magic-phrase friction. They do not block this fix:
this proposal is the urgent P1 false-positive repair needed to unpark the
stale-git-worktree diagnosis thread and stop starving later bridge work. It
should not absorb those broader items without a separate proposal.

## Governance Preflights

Applicability preflight command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix
```

Result:

- `preflight_passed: true`
- packet hash:
  `sha256:c2d7bb2611455d09c9a9a3d78e098e682c65aefeccfd6f3076836dd8d17ee8f4`
- missing required specs: none
- missing advisory specs: none

ADR/DCL clause preflight command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix
```

Result:

- clauses evaluated: 5
- must_apply: 3
- blocking gaps: 0
- exit code: 0

## Conditions

Prime Builder must keep the implementation within the approved target paths and
must preserve the protocol distinction between an operative state and explanatory
context.

Required behavior:

- If the sufficiency match appears before a gap match in the section, classify
  the section as `sufficient`.
- If the gap match appears before a sufficiency match, classify the section as
  `gap`.
- If only the gap match exists, keep returning `gap`.
- If only the sufficiency match exists, keep returning `sufficient`.
- If neither exists in a present section, keep returning `unrecognized`.
- If the section is absent, keep returning `missing`.

This GO does not authorize relaxing the regexes broadly, accepting arbitrary
non-empty Requirement Sufficiency bodies, bypassing the implementation-start
gate, or changing bridge dispatcher selection/cooldown behavior.

## Required Verification

The implementation report should include, at minimum:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp .gtkb-tmp\pytest-requirement-sufficiency platform_tests\scripts\test_fab14_requirement_sufficiency.py platform_tests\scripts\test_implementation_authorization.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\implementation_authorization.py platform_tests\scripts\test_fab14_requirement_sufficiency.py
```

The implementation report should also show an end-to-end check that
`requirement_sufficiency_state()` returns `sufficient` for
`bridge/gtkb-stale-git-worktree-autogc-diagnosis-001.md` after the fix.

## Owner Action

No owner action required.
