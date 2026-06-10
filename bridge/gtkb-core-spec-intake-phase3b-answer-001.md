NEW

# GT-KB Core Specification Intake Phase 3B Answer Command Proposal

target_paths: ["E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/intake.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_cli_core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_intake.py"]
bridge_kind: prime_proposal
implementation_scope: protocol
target_project: GroundTruth-KB upstream CLI
work_item_ids: ["GTKB-CORE-001"]
affected_spec_ids: ["SPEC-CORE-INTAKE-001", "SPEC-CORE-INTAKE-002", "ADR-CORE-INTAKE-001", "DCL-CORE-INTAKE-001"]
requires_verification: true

## Status

NEW - Loyal Opposition review requested before implementation.

## Requested Verdict

GO to implement Phase 3B mutating answer capture for core application
specification intake, or NO-GO with required revisions.

This proposal does not request approval for project-init prompting, doctor
integration, session-start integration, dashboard integration, release,
packaging, or Agent Red application behavior.

## Claim

After the Phase 3A read-only CLI is verified, GT-KB should add a governed
answer command that lets an owner provide one core-spec answer at a time and
persist it with explicit provenance.

The command should be portable GT-KB infrastructure for all applications, not
Agent Red-specific implementation.

## Preconditions

Implementation must wait until
`bridge/gtkb-core-spec-intake-phase3a-cli-003.md` is Loyal Opposition
VERIFIED, or must carry any unresolved Phase 3A verification findings forward
explicitly.

The existing Phase 1/2 evaluator verification is already satisfied by
`bridge/gtkb-core-spec-intake-phase1-004.md`.

## Prior Evidence

- `GTKB-CORE-001` requires a persisted core application specification intake
  loop that asks one missing question at a time, captures owner-stated
  provenance, continues across sessions, and stops once every required slot is
  owner-stated or explicitly not applicable.
- `bridge/gtkb-core-spec-intake-002.md` gave GO for the overall Phase 0
  workstream and required non-interactive no-prompt behavior.
- `bridge/gtkb-core-spec-intake-phase1-004.md` VERIFIED the slot catalog and
  read-only evaluator.
- `bridge/gtkb-core-spec-intake-phase3a-cli-002.md` gave GO for read-only
  `status` and `next-question` only, and explicitly reserved the mutating
  answer path for a separate proposal.
- `src/groundtruth_kb/intake.py` already provides confirm-before-mutate
  requirement intake primitives, but the current confirm path does not preserve
  core-slot handle, tag, description, or not-applicable semantics.

## Scope In

1. Add a governed `gt core-specs answer` command.
2. Require a stable slot handle argument that must exist in the core slot
   catalog.
3. Support an explicit owner-stated answer text path, for example:

   ```powershell
   gt core-specs answer core-identity --text "Name: ...`nDescription: ..."
   ```

4. Persist owner-stated answers as current specs with:
   - stable slot handle;
   - slot tag;
   - owner-stated authority;
   - title/description evidence sufficient for the current evaluator;
   - changed-by and change-reason evidence identifying core-spec intake.
5. Support explicit not-applicable capture for applicable slots, for example:

   ```powershell
   gt core-specs answer core-ai --not-applicable --reason "AI is out of scope."
   ```

   This should persist the canonical not-applicable deliberation evidence used
   by `core_spec_not_applicable_source_ref(handle)`.
6. Reject invalid combinations such as `--text` plus `--not-applicable`.
7. Reject not-applicable for always-applicable slots unless the catalog marks
   that slot as eligible, or provide a deliberate `--force-not-applicable`
   escape with a clear audit reason.
8. Add `--dry-run` to show the proposed mutation without writing.
9. Add `--json` for automation-safe output.
10. Reuse the Phase 3A evaluator after writes to report the updated slot state
    and next handle.
11. Add focused tests for stated answer capture, not-applicable capture,
    invalid handles, invalid option combinations, dry-run no-write behavior,
    JSON output, and existing read-only command compatibility.

## Scope Out

1. No automatic prompting during `gt project init`.
2. No session-start, dashboard, or doctor integration.
3. No multi-question wizard.
4. No Agent Red application source changes.
5. No package release, push, merge, or deployment.
6. No bulk import of Agent Red specs.
7. No automatic mutation when `status` or `next-question` runs.

## Proposed Behavior

### Owner-Stated Answer

`gt core-specs answer core-identity --text "..."`

Expected result:

- creates or updates the current spec evidence for `core-identity`;
- preserves `handle="core-identity"` and `tags=["core-identity"]`;
- sets `authority="stated"`;
- prints the completed slot and next incomplete slot;
- exits `0`.

### Not Applicable

`gt core-specs answer core-ai --not-applicable --reason "..."`

Expected result:

- creates an owner-decision deliberation with
  `source_ref=core-spec:core-ai:not-applicable`;
- does not create a fake requirement spec;
- marks `core-ai` complete through the existing evaluator;
- prints the completed slot and next incomplete slot;
- exits `0`.

### Dry Run

`gt core-specs answer core-users --text "..." --dry-run --json`

Expected result:

- emits the planned mutation as JSON;
- performs no database write;
- exits `0`.

## Verification Commands

Run in `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

```powershell
python -m pytest tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py -q --tb=short
python -m pytest tests/test_cli.py tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py src/groundtruth_kb/intake.py tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_intake.py
python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py
```

Run the broader GT-KB suite only if implementation touches shared intake logic
outside the command path.

## Risks And Controls

### Risk: answer capture bypasses formal approval governance

Control: require the owner to invoke an explicit mutating command; preserve
changed-by/change-reason/source evidence; keep automatic read-only commands
non-mutating.

### Risk: not-applicable is represented as a fake completed requirement

Control: persist not-applicable as deliberation evidence using the existing
canonical source-ref, and keep the evaluator responsible for completion state.

### Risk: free-form answer text is too weak for later structured specs

Control: this phase stores enough owner-stated evidence to stop repeated
prompting, while later Phase 4/5 documentation can improve guided reply
format. Do not block the intake loop on a full schema wizard in this slice.

## Decision Needed From Owner

None at proposal time.

Implementation is blocked on Loyal Opposition GO and Phase 3A verification.
