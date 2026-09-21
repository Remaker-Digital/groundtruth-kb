# Getting started with GroundTruth

This walkthrough connects a selected application project to the host's native
authority, initializes its files, and records specifications and linked tests.
Canonical records live behind the native service. The application configuration
selects that service; an application-local database or an operational notepad is
not a substitute for it.

## Before you start

Use an installed GroundTruth distribution and an already configured GT-KB host
with a reachable native authority and its required reference-transaction hook.
This guide does not provision that service or cloud infrastructure. Git and a
supported Python environment must be available.

Replace `<host>`, `<PROJECT>`, `<ACTOR>` and `<OWNER>` with the selected host path,
execution project identifier, current context's attribution and owner name.
Commands below show a new application named `my-project`. Use the actual selected
application name consistently. Verify the installed CLI first:

```text
gt --version
```

## 1. Select the application and execution project

If the application is already registered and its execution project is already
bound, read that current project and continue to initialization. For a new,
owner-selected application, register its host slot and initialize its independent
Git repository:

```text
gt --config "<host>/groundtruth.toml" application register my-project --host-root "<host>" --json
git -C "<host>/applications/my-project" init --initial-branch=main
```

Registration creates the application marker; it does not initialize Git or
create a project. The native project writer validates the selected repository,
so create the independent repository before recording a new execution project.
Prepare `project.json` with the authored project fields:

```json
{
  "name": "My project",
  "repository_ref": "application:my-project"
}
```

Record that new project and read it back:

```text
gt --config "<host>/groundtruth.toml" projects record --id <PROJECT> --kind project --fields-file project.json --expected-version 0 --actor <ACTOR> --change-reason "Create the selected application project" --json
gt --config "<host>/groundtruth.toml" projects show <PROJECT> --json
```

Version zero asserts a new record. For an existing project, use its current
record and authorized scope instead of replaying creation or inventing a new ID.
The execution project's `repository_ref` must select the registered application.

## 2. Preview and initialize the application

The target must be uninitialized: only its matching registration marker and an
empty independent Git repository may already exist. Inspect the preview before
writing the selected application files:

```text
gt --config "<host>/groundtruth.toml" project init my-project --project-id <PROJECT> --host-root "<host>" --owner "<OWNER>" --profile local-only --dry-run --json
gt --config "<host>/groundtruth.toml" project init my-project --project-id <PROJECT> --host-root "<host>" --owner "<OWNER>" --profile local-only --json
```

The initializer writes the application configuration, instructions, managed
files and profile-tiered CI. It creates no local authority database and makes no
commit. Use the returned paths and readback to check the result.

Add `--harness <profile-name>` to both commands for each selected harness
configuration. These profiles select configuration, not an agent role. An
optional `--seed-example` creates `src/tasks.py` and `tests/test_tasks.py`; it does
not create an HTTP API. Use the same options in the preview and actual command.

## 3. Capture the owner's core requirements

Core intake derives twelve slots from current canonical specifications. Ask for
the next missing requirement explicitly, then record the owner's actual answer
using the slot and expected version returned by that fresh read:

```text
gt --config "<host>/applications/my-project/groundtruth.toml" core-specs next-question --project-id <PROJECT> --json
gt --config "<host>/applications/my-project/groundtruth.toml" core-specs answer --project-id <PROJECT> --slot <RETURNED_SLOT> --value "<EXPLICIT_OWNER_ANSWER>" --expected-version <RETURNED_VERSION> --actor <ACTOR> --reason "<REASON>" --json
gt --config "<host>/applications/my-project/groundtruth.toml" core-specs status --project-id <PROJECT> --no-fail --json
```

Re-read the next question before each answer. An explicit owner response that a
slot does not apply uses `--source not_applicable`. Answers go directly through
the specification writer and are read back; no session-progress store or
separate conversation archive is created. `status` without `--no-fail` returns
an unsuccessful exit while required intake remains incomplete.

The supported opt-outs are `--opt-out-core-spec-intake` during initialization,
`GTKB_CORE_SPEC_INTAKE_OPT_OUT=1`, or this table in the application configuration:

```toml
[core_spec_intake]
enabled = false
```

This guide makes no promise of automatic
session-start questions or prompts written to `MEMORY.md`.

## 4. Record a specification and its executable test

Use requirements actually selected for the project. The following demonstration
matches the optional task example from step 2. It records a specification for
`create_task` preserving its title and starting in the open state; recording it
does not establish that the implementation was reviewed or tested.

Prepare `spec-001.json`, replacing the project identifier and using the selected
application scope:

```json
{
  "title": "A new task preserves its title and starts open",
  "type": "requirement",
  "status": "active",
  "scope": "<PROJECT>",
  "application_scope": "application:my-project",
  "description": "create_task(title) returns the supplied title and status open."
}
```

Use the assigned specification ID; `SPEC-001` below is an example:

```text
gt --config "<host>/applications/my-project/groundtruth.toml" spec record --id SPEC-001 --fields-file spec-001.json --expected-version 0 --actor <ACTOR> --change-reason "Record the selected task requirement" --json
gt --config "<host>/applications/my-project/groundtruth.toml" spec show SPEC-001 --json
```

The optional example includes the following actual test selector. For a real
application, link its own implemented test and describe the required behavior in
`test-001.json`:

```json
{
  "title": "A new task preserves its title and starts open",
  "spec_id": "SPEC-001",
  "test_type": "unit",
  "test_file": "tests/test_tasks.py",
  "test_class": null,
  "test_function": "test_new_task_preserves_title_and_starts_open",
  "expected_outcome": "create_task returns the original title and status open",
  "application_scope": "application:my-project"
}
```

```text
gt --config "<host>/applications/my-project/groundtruth.toml" tests record --id TEST-001 --fields-file test-001.json --expected-version 0 --actor <ACTOR> --change-reason "Link the executable task requirement test" --json
```

Run the stated test in the application's test environment through the applicable
verification workflow. A recorded definition, generated example or static source
match is not an execution result or independent verification.

## 5. Add and evaluate a bounded assertion

An assertion evaluates its declared condition. For example, this
`spec-001-assertions.json` checks that the task function is present:

```json
{
  "assertions": [
    {
      "type": "grep",
      "file": "src/tasks.py",
      "pattern": "def create_task",
      "description": "The task function is declared in its application source"
    }
  ]
}
```

Read the specification's current version, then amend and evaluate it against the
selected application:

```text
gt --config "<host>/applications/my-project/groundtruth.toml" spec record --id SPEC-001 --fields-file spec-001-assertions.json --expected-version <CURRENT_VERSION> --actor <ACTOR> --change-reason "Add the function-presence assertion" --json
gt --config "<host>/applications/my-project/groundtruth.toml" assert --spec SPEC-001 --json
```

A successful grep establishes function presence only. The behavioral test checks
the returned title and status. Native assertions require a reachable authority;
inspect unsupported or unassessed conditions instead of treating them as passes.
Amendments preserve history and require current versions. Formal lifecycle
values are `active`, `superseded` and `retired`.

## 6. Refresh harness configuration from its authored sources

The initializer uses the host's supported projection path for requested harness
profiles. Do not manually copy or edit generated hook, rule or skill trees. For
an existing initialized application, upgrade requires the managed paths being
replaced or removed to be recoverable from Git history. A fresh scaffold is
uncommitted, so select its harness profiles during step 2 rather than using
upgrade to bypass that local-work check. Continue through the normal governed
review and commit process; this walkthrough adds no separate bootstrap commit.
For an application meeting the upgrade preconditions, preview its managed-file
changes, inspect them, then apply the selected scope:

```text
gt --config "<host>/groundtruth.toml" project upgrade my-project --project-id <PROJECT> --host-root "<host>" --harness <profile-name> --json
gt --config "<host>/groundtruth.toml" project upgrade my-project --project-id <PROJECT> --host-root "<host>" --harness <profile-name> --apply --json
```

For configuration belonging to the GT-KB host itself, select the host root that
contains the projector:

```text
gt --config "<host>/groundtruth.toml" harness project <profile-name> --dry-run
gt --config "<host>/groundtruth.toml" harness project <profile-name>
gt --config "<host>/groundtruth.toml" harness project <profile-name> --check
```

A newly scaffolded application does not contain that host projector. Use its
application initializer or upgrade route above.

For this shared-source layout, root `AGENTS.md` is authored once, skills live
in `.agents/skills`, and rules, hooks and routing live under
`.harness-baseline-configuration`. The projector derives the selected native
registration from those sources. See [Harness projection](reference/harness-projection.md).

In an actual host session, use the owner's exact init line and separately
supplied activity, then read the assigned current work and bridge item. Check
native instruction loading and hook execution in that host; generated files
alone do not establish those behaviors. The owner dispatches work until the
successor dispatcher is independently qualified and activated.

## 7. Inspect the generated CI for the chosen profile

Initialization includes CI by default; `--no-include-ci` omits it. The
`local-only` workflow runs Ruff. It does not execute pytest or native assertions.
Other profiles have their own generated steps and runtime requirements. Inspect
the actual workflow and supply the application's required tests and service
configuration through its governed development process. No undefined template
environment variable or manual harness-template copy is needed.

Continue with the [Method Overview](method/01-overview.md),
[Specifications guide](method/02-specifications.md),
[Adoption guide](method/09-adoption.md), and
[Product Architecture](architecture/product-split.md).
