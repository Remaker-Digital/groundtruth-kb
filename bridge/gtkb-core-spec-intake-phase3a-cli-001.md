NEW

# GT-KB Core Specification Intake Phase 3A Read-Only CLI Proposal

target_paths: ["E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/cli.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_cli_core_specs.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_core_specs.py"]

## Status

NEW - Loyal Opposition review requested before implementation.

## Requested Verdict

GO to implement the Phase 3A read-only CLI slice, or NO-GO with required
revisions.

This proposal intentionally does not request approval for owner-answer
mutation, project-init prompting, doctor integration, session-start integration,
dashboard integration, release, packaging, or any formal artifact mutation.

## Claim

Prime Builder should add the first CLI surface for GT-KB core application
specification intake after the Phase 1/2 catalog and evaluator are implemented
and verified.

The CLI should expose deterministic, read-only commands:

1. `gt core-specs status`
2. `gt core-specs status --json`
3. `gt core-specs next-question`
4. `gt core-specs next-question --json`

The mutating `gt core-specs answer` path should remain out of scope for this
slice and receive its own bridge proposal because it intersects owner answers,
Deliberation Archive capture, specification creation/update, and formal
artifact approval rules.

## Preconditions

Do not implement this Phase 3A slice until the current Phase 1/2 bridge thread
has been implemented and submitted for post-implementation verification.

Current related bridge state:

- `bridge/gtkb-core-spec-intake-001.md` received GO in
  `bridge/gtkb-core-spec-intake-002.md`.
- `bridge/gtkb-core-spec-intake-phase1-001.md` received GO in
  `bridge/gtkb-core-spec-intake-phase1-002.md`.
- The target checkout currently has an uncommitted Phase 1/2 draft:
  - `src/groundtruth_kb/core_specs.py`
  - `tests/test_core_specs.py`

This proposal may be reviewed before Phase 1/2 verification, but implementation
must not expand or rely on unverified Phase 1/2 behavior beyond the reviewed
public API.

## Prior Deliberations

Deliberation search was run before this proposal.

Relevant records:

- `DELIB-0875`: owner approval for GT-KB core specification intake Phase 0.
- `DELIB-0732`: VERIFIED `/gtkb-spec-intake` bridge thread, relevant to the
  later mutating answer path.
- `DELIB-0708`: GT-KB should function as a structured interview system with
  deliberate specification sequencing.
- `DELIB-0835`: strict approval and audit handling for DA, GOV, SPEC, PB, ADR,
  and DCL mutations.

## Governing Evidence

- `memory/work_list.md` defines `GTKB-CORE-001` and its Phase 3 plan:
  deterministic `gt core-specs status`, `gt core-specs next-question`, and an
  answer/intake flow suitable for tests and hooks.
- `bridge/gtkb-core-spec-intake-002.md` gave GO for the Phase 0 workstream
  shape and required non-interactive and machine-readable command paths to be
  no-prompt paths.
- `bridge/gtkb-core-spec-intake-phase1-002.md` gave GO for the narrow Phase
  1/2 package-module slice and explicitly excluded CLI behavior from that GO.
- The current upstream `tests/test_cli.py` uses `click.testing.CliRunner` and
  establishes existing CLI test style.

## Scope In

1. Add a `core-specs` CLI command group.
2. Add read-only `status` command:
   - reads `evaluate_core_spec_slots(db)`;
   - prints completion count, total count, completion percentage, and one row
     per slot;
   - returns exit code `0` when complete;
   - returns exit code `2` when incomplete unless `--no-fail` is supplied.
3. Add read-only `status --json` command:
   - emits stable JSON with `complete`, `completed_count`, `total_count`,
     `next_handle`, and `slots`;
   - emits no decorative prose.
4. Add read-only `next-question` command:
   - prints exactly one next missing/unclear/inferred question;
   - includes handle, title, question, why-it-matters, expected reply shape,
     and not-applicable guidance;
   - prints a completion message when no question remains.
5. Add read-only `next-question --json` command:
   - emits stable JSON for the next incomplete slot or a complete payload when
     no question remains.
6. Add focused CLI tests in `tests/test_cli_core_specs.py`.
7. Preserve existing scaffold and CLI behavior outside the new command group.

## Scope Out

1. No `gt core-specs answer` implementation in this slice.
2. No spec insertion, spec update, Deliberation Archive insertion, or work-item
   mutation.
3. No `gt project init` integration.
4. No `gt project doctor` integration.
5. No session-start hook, dashboard, startup report, or wrap-up integration.
6. No package release or Agent Red adoption apply.
7. No changes to the existing `minimal` or `full` scaffold outputs.

## Proposed CLI Behavior

### `gt core-specs status`

Human output should be compact and deterministic:

```text
Core specifications: 1/12 complete
Next question: core-app-type - Application Type

missing         core-app-type        Application Type
inferred        core-tenancy         Tenancy And Provider Administration
stated          core-identity        Product Identity
not_applicable  core-ai              AI Usage
```

Ordering must follow `CORE_SPEC_SLOT_HANDLES`.

### `gt core-specs status --json`

Suggested JSON shape:

```json
{
  "complete": false,
  "completed_count": 1,
  "total_count": 12,
  "next_handle": "core-app-type",
  "slots": [
    {
      "handle": "core-identity",
      "title": "Product Identity",
      "state": "stated",
      "complete": true,
      "evidence_id": "SPEC-CORE-IDENTITY",
      "reason": "Owner-stated spec evidence exists for this slot."
    }
  ]
}
```

### `gt core-specs next-question`

Human output should be one question only:

```text
core-app-type - Application Type
Question: What type of application is this: SaaS, internal tool, API service, CLI, mobile app, library, marketplace app, or something else?
Why it matters: The delivery surface determines default architecture, test, deployment, and UX assumptions.
Expected reply:
- Application type: ...
- Delivery surface: ...
- Notes: ...
Not applicable: Mark not applicable only for non-software knowledge-base projects.
```

When complete:

```text
Core specifications are complete.
```

### `gt core-specs next-question --json`

Suggested JSON shape when incomplete:

```json
{
  "complete": false,
  "slot": {
    "handle": "core-app-type",
    "title": "Application Type",
    "question": "...",
    "why_it_matters": "...",
    "reply_shape": ["Application type: ...", "Delivery surface: ..."],
    "not_applicable_guidance": "..."
  }
}
```

Suggested JSON shape when complete:

```json
{
  "complete": true,
  "slot": null
}
```

## Exit Code Policy

Recommended initial policy:

- `status`: exit `0` if complete, exit `2` if incomplete.
- `status --no-fail`: always exit `0` unless command execution fails.
- `status --json`: same exit policy as `status`.
- `next-question`: exit `0` whether it prints a question or completion message.
- `next-question --json`: exit `0` whether incomplete or complete.
- invalid config/database errors: existing Click error behavior.

Rationale: `status` is suitable for gates and automation, while
`next-question` is a read-only prompt selector and should not fail merely
because work remains.

## Tests

Add `tests/test_cli_core_specs.py` with focused coverage:

1. fresh database `status` reports `0/12`, `core-identity`, and exits `2`;
2. `status --no-fail` reports incomplete state and exits `0`;
3. `status --json` emits valid JSON with stable keys and slot order;
4. owner-stated evidence changes `core-identity` state to `stated`;
5. not-applicable deliberation changes the relevant slot to `not_applicable`;
6. `next-question` prints exactly the first incomplete slot;
7. `next-question --json` emits only JSON and no decorative prose;
8. all-complete state prints completion and JSON `slot: null`;
9. existing CLI tests still pass.

If Phase 1/2 post-verification adds tag-only and handle-only tests, preserve
those; otherwise add them before or with this slice if still missing.

## Verification Commands

Run in `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

```powershell
python -m pytest tests/test_cli_core_specs.py tests/test_core_specs.py tests/test_cli.py -q --tb=short
python -m pytest tests/test_spec_scaffold.py tests/test_scaffold_project.py -q --tb=short
python -m ruff check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py tests/test_core_specs.py
python -m ruff format --check src/groundtruth_kb/cli.py src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py tests/test_core_specs.py
python -m mypy --strict src/groundtruth_kb/core_specs.py tests/test_cli_core_specs.py
```

Do not claim the broader GT-KB suite is clean unless it is run separately.

## Risks And Controls

### Risk: CLI output becomes too chatty for hooks

Control: require JSON modes to emit only machine-readable JSON and require
`next-question` to print one question only.

### Risk: incomplete state fails automation unexpectedly

Control: add `--no-fail` for `status`; keep `next-question` exit `0` in both
incomplete and complete states.

### Risk: answer mutation sneaks into this slice

Control: leave `gt core-specs answer` unimplemented or show a clear "not yet
implemented" message. Mutating answer behavior needs a separate bridge proposal
because it intersects formal artifact approval and Deliberation Archive capture.

### Risk: Phase 3A relies on unverified Phase 1/2 draft behavior

Control: implementation waits for Phase 1/2 post-implementation report and
Loyal Opposition verification, or explicitly carries any Phase 1/2 verification
conditions into the implementation report.

## Review Questions

1. Is splitting read-only `status` and `next-question` from mutating `answer`
   acceptable for Phase 3, or should the entire CLI surface wait for a larger
   answer-flow proposal?
2. Should incomplete `status` exit `2`, or should it always exit `0` and leave
   gating to a later `gt core-specs gate` command?
3. Is the proposed JSON shape sufficient for later session-start and dashboard
   integration?
4. Should `next-question` include not-applicable guidance in human output by
   default, or only in JSON/details mode?

## Decision Needed From Owner

None at proposal time.

Implementation is blocked on Loyal Opposition `GO`. A later owner decision may
be needed for the mutating `answer` command, especially whether direct owner
answers create formal specs immediately or first create confirmation-needed
candidate records.
