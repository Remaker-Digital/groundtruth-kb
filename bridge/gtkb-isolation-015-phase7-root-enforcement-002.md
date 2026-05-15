NO-GO

# Loyal Opposition Review - Isolation Phase 7 Work-Subject/Root Enforcement

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-isolation-015-phase7-root-enforcement-001.md`
Verdict: NO-GO

## Claim

The isolation/work-subject objective is valid, but this proposal is not ready
for GO. It appears to re-propose behavior that already has verified bridge
history and live implementation, while also omitting required target paths for
its own hook-registration scope and pointing verification at a non-existent
test location.

## Prior Deliberations

Command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "GTKB-ISOLATION-015 work subject root enforcement applications hook" --limit 8
```

Relevant results:

- `DELIB-2061` / `DELIB-1142` - bridge thread
  `gtkb-work-subject-root-enforcement-implementation`, including VERIFIED
  closure at `bridge/gtkb-work-subject-root-enforcement-implementation-020.md`.
- `DELIB-2029` / `DELIB-1135` - bridge thread
  `gtkb-isolation-015-phase7-full-integration`, including VERIFIED closure at
  `bridge/gtkb-isolation-015-phase7-full-integration-016.md`.

The reviewed proposal cites `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`
and `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`, but it does not cite
or distinguish these directly relevant prior verified work-subject/root
enforcement threads.

No prior deliberation found that waives target-path completeness, Codex parity,
or the need to avoid duplicating already verified enforcement surfaces.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-015-phase7-root-enforcement
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:a0631b26825f2291ca47819c79febef29e9fbf9fa64b24835b4d19d1df6371a8`
- bridge_document_name: `gtkb-isolation-015-phase7-root-enforcement`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-isolation-015-phase7-root-enforcement-001.md`
- operative_file: `bridge/gtkb-isolation-015-phase7-root-enforcement-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The missing advisory specs are not independently blocking. Required
applicability coverage passes.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-isolation-015-phase7-root-enforcement
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-isolation-015-phase7-root-enforcement`
- Operative file: `bridge\gtkb-isolation-015-phase7-root-enforcement-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

No blocking clause gaps were reported.

## Findings

### F1 - The proposal duplicates or conflicts with already verified work-subject/root enforcement

Severity: P1

Evidence:

- The proposal claims `.claude/session/work-subject.json` is currently
  advisory and proposes a new PreToolUse Write/Edit gate at
  `bridge/gtkb-isolation-015-phase7-root-enforcement-001.md:64-76`.
- Prior thread `bridge/gtkb-work-subject-root-enforcement-implementation-020.md`
  is VERIFIED and states the narrowed work-subject/root-enforcement request is
  satisfied.
- Prior thread `bridge/gtkb-isolation-015-phase7-full-integration-016.md` is
  VERIFIED for `GTKB-ISOLATION-015` Slice 1 and cites live
  work-subject/root-guard behavior.
- Live code already contains the root classifier and guard in
  `scripts/workstream_focus.py:1262` and `scripts/workstream_focus.py:1355`.
- Live regression tests already cover application/GT-KB subject blocking in
  `platform_tests/hooks/test_workstream_focus.py:639` and
  `platform_tests/hooks/test_workstream_focus.py:688`.
- `.claude/settings.json:164` and `.codex/hooks.json:63` already register the
  existing workstream/work-subject hook path.

Impact:

Approving a second, parallel hook (`work-subject-write-gate.py`) would create
two competing enforcement surfaces for the same invariant and would obscure
which verified bridge thread owns the behavior.

Recommended action:

Revise the proposal to start from the verified existing surface. If a real gap
remains, define the delta against `scripts/workstream_focus.py`,
`.claude/hooks/workstream-focus.py`, `.codex/gtkb-hooks/workstream-focus.cmd`,
`.claude/settings.json`, `.codex/hooks.json`, and
`platform_tests/hooks/test_workstream_focus.py` as applicable. If no gap
remains, withdraw or convert this thread into a closure/disposition proposal.

### F2 - Target paths do not authorize the proposal's stated hook registration and Codex parity work

Severity: P1

Evidence:

- The proposal's `target_paths` are only
  `.claude/hooks/work-subject-write-gate.py`,
  `.claude/session/work-subject.json`, `scripts/work_subject_enforce.py`, and
  `tests/scripts/test_work_subject_enforce.py`
  (`bridge/gtkb-isolation-015-phase7-root-enforcement-001.md:16`).
- The proposed scope explicitly says to register the hook in
  `.claude/settings.json`, mirror it at
  `.codex/gtkb-hooks/work-subject-write-gate.py`, and update `.codex/hooks.json`
  (`bridge/gtkb-isolation-015-phase7-root-enforcement-001.md:74-76`).
- Those three registration/parity paths are absent from `target_paths`.

Impact:

The implementation-start gate cannot authorize the implementation as written.
Prime Builder would either be blocked by the approved scope or would need to
mutate hook registration/parity files outside the approved bridge envelope.

Recommended action:

Either remove IP-2 from this proposal or add every concrete registration and
Codex parity path to `target_paths`. If the existing `workstream-focus` hook
remains the intended surface, target that existing hook and wrapper rather than
creating a new parallel hook name.

### F3 - The verification plan points to a non-existent test surface and misses the live regression suite

Severity: P2

Evidence:

- The proposal requires `python -m pytest tests/scripts/test_work_subject_enforce.py -v`
  (`bridge/gtkb-isolation-015-phase7-root-enforcement-001.md:94`).
- Live checkout inspection found `tests/scripts/test_work_subject_enforce.py`
  does not exist.
- The current work-subject/root-enforcement tests live at
  `platform_tests/hooks/test_workstream_focus.py`.

Impact:

The proposal cannot produce reliable spec-derived verification as written, and
it risks bypassing the regression suite that actually protects the existing
work-subject hook behavior.

Recommended action:

Move the proposed test scope to the live `platform_tests/hooks` surface, or
explicitly justify a new test file under an existing test root and include the
current workstream/work-subject regression suite in the required verification
command.

### F4 - Proposed path semantics would regress the verified bridge/governance exception

Severity: P1

Evidence:

- The proposal says application scope should allow only paths under
  `applications/<app-name>/`
  (`bridge/gtkb-isolation-015-phase7-root-enforcement-001.md:69-72`).
- The verified live guard deliberately treats current-repo bridge/governance
  surfaces as a separate category allowed in both work subjects:
  `scripts/workstream_focus.py:1363-1368`.
- Regression coverage explicitly asserts that application subject allows
  current-repo bridge/governance writes at
  `platform_tests/hooks/test_workstream_focus.py:661`.

Impact:

The proposal would make routine bridge/governance maintenance fail while the
session is in application subject, contradicting the verified Phase 7 behavior
and creating operational deadlock for the bridge itself.

Recommended action:

Preserve the existing four-category taxonomy:
`application_product`, `current_repo_bridge_or_governance`, `gtkb_product`, and
`neutral`. Any new enforcement must keep bridge/governance paths available in
both work subjects unless a new owner-approved rule explicitly changes that
contract.

## Positive Evidence

- The bridge applicability preflight has no missing required specs.
- The mandatory clause preflight reports zero blocking gaps.
- The requested paths are in-root.
- The owner authorization cited by the proposal may support a properly scoped
  closeout delta, but it does not cure the target-path, duplicate-surface, or
  verification-plan defects above.

## Required Revision

File a revised proposal that:

1. Distinguishes the requested delta from the already VERIFIED
   `gtkb-work-subject-root-enforcement-implementation` and
   `gtkb-isolation-015-phase7-full-integration` threads.
2. Uses the existing workstream/work-subject enforcement surfaces unless the
   revision proves a new hook is necessary.
3. Lists every concrete hook-registration, Codex parity, source, state, and
   test path in `target_paths`.
4. Replaces the non-existent `tests/scripts/test_work_subject_enforce.py`
   verification path with the live regression suite, or clearly creates and
   justifies a new platform test surface.
5. Preserves the verified bridge/governance exception for both work subjects.

## Decision Needed From Owner

None.

File bridge scan: 1 entry processed.
