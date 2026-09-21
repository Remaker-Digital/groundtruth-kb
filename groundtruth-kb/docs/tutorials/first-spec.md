# Your First Specification

<!-- © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. -->

This walkthrough records a requirement and its executable test through the native
authority in your configured project. The example requirement is: “Creating a
task returns its title and the initial status `open`.”

## 1. Read the current project and applicable requirements

Use the configured CLI in your project directory. Confirm the doctor can reach
the native authority, then read the selected project and its linked formal
records. Use the project's current application scope when recording new rows.

```bash
gt doctor
gt projects show <PROJECT_ID> --json
gt spec show <SPEC_ID> --history --json
```

Choose the existing requirement when it already expresses the intended behavior.
A new specification uses an unused ID; an amendment uses the current version
returned by the service. A missing record and an unavailable service are different
conditions and must not be treated as interchangeable.

## 2. Record the required behavior

For a new requirement, prepare a UTF-8 JSON fields file such as
`spec-fields.json`:

```json
{
  "title": "Creating a task returns its initial state",
  "description": "Creating a task with a nonempty title returns that title and status open. Invalid empty titles are rejected.",
  "status": "active"
}
```

Record it with expected version `0` only when the ID is new. Supply your actual
attribution and the reason for the change:

```bash
gt spec record --id <SPEC_ID> --fields-file spec-fields.json --expected-version 0 --actor <ACTOR> --change-reason "Record the required task creation behavior" --json
gt spec show <SPEC_ID> --history --json
```

Confirm the canonical readback has the exact intended fields. An active formal
record states a current requirement; it does not establish implemented or
verified behavior. See [Specifications](../method/02-specifications.md).

## 3. Define an executable test

In your application's actual test suite, test both the required result and its
failure boundary. For example, when the selected implementation exposes
`create_task` from `tasks`, the test can express:

```python
import pytest
from tasks import create_task


def test_task_initial_state():
    task = create_task("Buy milk")
    assert task["title"] == "Buy milk"
    assert task["status"] == "open"
    with pytest.raises(ValueError):
        create_task("")
```

The import and selector must name real code and a real test in your application.
Run that test in the application's configured environment. Before implementation,
a measured failure can establish the missing behavior; a test description alone
does not supply executable coverage.

## 4. Record the test binding and plan membership

Prepare `test-fields.json` with the actual selector and the specification ID:

```json
{
  "title": "Task creation preserves title and validates empty input",
  "spec_id": "<SPEC_ID>",
  "test_type": "unit",
  "test_file": "tests/test_tasks.py",
  "test_function": "test_task_initial_state",
  "expected_outcome": "A valid title is returned with status open; an empty title is rejected."
}
```

```bash
gt tests record --id <TEST_ID> --fields-file test-fields.json --expected-version 0 --actor <ACTOR> --change-reason "Bind the executable requirement test" --json
gt tests show <TEST_ID> --history --json
gt test-phases show <PHASE_ID> --history --json
```

Add the TEST to the appropriate active test-plan phase through its version-checked
native amendment, preserving its existing members. Do not put an invented PASS
or execution timestamp in the fields file. Keep the observed execution evidence
and the test's current definition together.

## 5. Progress the selected implementation work

The implementation work item belongs to one execution project and links the
applicable specification and executable test. Follow the current independent
proposal, implementation and verification process for that work. Reading or
creating a specification does not itself grant an implementation verdict.

After implementation, rerun the actual test, inspect the result and review the
smallest affected requirement closure. A selected passing test is evidence for
its measured duty; complete independent verification remains a separate step.

The [CLI reference](../reference/cli.md#canonical-record-commands) describes current
record fields and version-checked commands. The [adopter fixtures](../examples/task-tracker.md)
show the small layouts used by the platform's scaffold smoke checks.
