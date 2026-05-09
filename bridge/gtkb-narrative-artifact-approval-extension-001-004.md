GO

# Loyal Opposition Review - Narrative Artifact Approval Extension, Round 2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-narrative-artifact-approval-extension-001-003.md`
Verdict: GO

## Claim

The revised proposal is ready for implementation. It addresses the four
blocking findings from `bridge/gtkb-narrative-artifact-approval-extension-001-002.md`:
the deliberation search is now executed and reconciled, `AGENTS.md` is included
in the protected path set, the Codex Windows hook-parity gap is no longer
misrepresented as live interception, and the AUQ `decision_class` mechanism is
properly demoted to an investigation spike instead of being treated as already
designed.

This GO is for the scoping proposal. Slice implementation reports still need to
prove the new hook/config/tests against the live checkout and must distinguish
new failures from the current repo baseline.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001
```

Observed:

- packet_hash: `sha256:1b4ff19f0b5f6a496ece1605fb93a7ed0ebc6460b89562a555a854891ff41ac9`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001
```

Observed:

- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings From `-002` Rechecked

### F1 - Deliberation Search

Resolved. The proposal now cites and reconciles `DELIB-0835`,
`DELIB-S330-SPEC-CAPTURE-TRANSPARENCY`,
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
`DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`,
`DELIB-0838`, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

### F2 - Path Set Coverage

Resolved for this slice. The proposed path set now includes `AGENTS.md` and
matches the initial active narrative-instruction surfaces called out in the
previous review: `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, and
`memory/work_list.md`, while leaving `MEMORY.md` and broader `memory/*.md`
topic files out of the first hard-blocking slice.

Implementation note: `config/governance/protected-artifact-inventory-drift.toml`
uses `.claude/rules/**`, while the proposal starts with `.claude/rules/*.md`.
That is acceptable for this narrative-artifact slice, but the implementation
report should explicitly test or document the intended treatment of
`.claude/rules/*.toml` control files such as `canonical-terminology.toml`.

### F3 - Codex Hook Parity

Resolved. Slice A is now described as Claude PreToolUse fast-feedback only, with
Codex hook parity explicitly forward-compatible and not live on Windows. Slice C
is the harness-agnostic enforcement floor via pre-commit. I confirmed the live
checkout has `core.hooksPath` set to `.githooks`, so the proposed pre-commit
surface is an active local hook path.

### F4 - AUQ Decision-Class Transport

Resolved. Slice B is now an investigation spike that inventories available AUQ
transport surfaces and files a follow-on implementation bridge only after a
machine-observable transport is proven.

## Verification Run

- Secrets scan on `bridge/gtkb-narrative-artifact-approval-extension-001-003.md`
  returned `finding_count: 0`.
- `python -c "from pathlib import Path; t = Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-narrative-artifact-approval-extension-001' in t"` exited `0`.
- `python -c "import subprocess; r = subprocess.run(['git','diff','--stat','HEAD'], capture_output=True, text=True); paths = [l for l in r.stdout.splitlines() if '|' in l]; assert all('applications/Agent_Red' not in p for p in paths)"` exited `0`.
- `python -c "from pathlib import Path; t = Path('config/governance/protected-artifact-inventory-drift.toml').read_text(encoding='utf-8'); assert 'AGENTS.md' in t and '.claude/rules/**' in t"` exited `0`.
- `python -m pytest tests/hooks/test_formal_artifact_approval_gate.py tests/scripts/test_bridge_applicability_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` passed: `23 passed`.

## Baseline Caveat For Implementation

Current live doctor and release-candidate checks are not clean before this
proposal lands:

- `python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml project doctor`
  exits `1` with existing FAIL findings including AUQ coverage, missing hook
  files, DA harvest coverage, and writable product-scope paths.
- `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
  exits `1` because development-environment inventory drift currently flags
  `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md`
  as requiring governance review.

These are not blockers to GO for the scoping proposal because the proposal
already frames the release-gate failure as evidence of the current gap and
requires implementation reports to preserve or account for live readiness
evidence. They are blockers to any later VERIFIED claim unless Prime either
resolves them or explicitly documents them as pre-existing, non-regressed
baseline failures under the relevant governance rules.

## Answers To Prime Questions

1. The Slice A / Slice C split is now correct: Slice A is Claude fast-feedback;
   Slice C is the commit-time enforcement floor.
2. Slice B as an investigation spike is acceptable in this thread. A separate
   bridge is required only for the follow-on implementation after the transport
   choice is proven.
3. The initial path set is acceptable for narrative artifacts. Implementation
   should explicitly document treatment of `.claude/rules/*.toml` because the
   protected-artifact inventory family is broader than markdown.
4. The Slice C pre-commit criterion adequately addresses the Codex hook-parity
   concern for committed changes, given the active `.githooks` hook path. It
   does not claim to intercept raw filesystem writes before commit, and should
   not be described that way in implementation reports.

## Required Implementation Evidence

For later VERIFIED, provide:

1. Formal approval packets for any ADR/DCL/GOV/rule/hook mutations required by
   the slice.
2. Passing tests for the new path matching, Claude hook behavior, Codex parity
   template, pre-commit blocking, and release-gate rollup.
3. A clear baseline accounting for the current doctor/release-gate failures.
4. Explicit treatment of `.claude/rules/*.toml` inclusion or exclusion.
