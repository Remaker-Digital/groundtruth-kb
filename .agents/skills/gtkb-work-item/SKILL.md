---
name: gtkb-work-item
description: Create a work item with an executable linked test and current test-plan phase, using native governed writers.
argument-hint: "[title] [--spec SPEC-ID] [--origin regression|defect|new|hygiene]"
allowed-tools: Bash, Read, Grep
compatibility:
  - claude-code >= 1.0
metadata:
  project: groundtruth-kb
  category: knowledge-management
  governance: GOV-12, GOV-13
  references:
    - references/taxonomy.md
  license: "Proprietary - (c) 2026 Remaker Digital"
  activity-envelope: build, ops, project, deliberation, spec
---
# Create a work item with executable evidence

Use the current explicitly opened activity and immutable session attribution.
This skill grants no role, project authorization or implementation approval.
The work item belongs to the selected execution project; no agent owns the
whole work item. Ask for a missing owner selection instead of choosing work
from a queue.

## Read the selected scope

Read the current specification, project, proposed existing work/test records,
and applicable test plan and phase through the native CLI. Follow bounded
pagination when a listing is needed. Use `gt <domain> --help` to inspect current
options. Do not inspect a legacy database or another context's scratch space.

Use explicitly selected identifiers. Do not infer the next identifier from a
listing's numerical maximum. Creation asserts `--expected-version 0`; an
existing identifier produces a CAS refusal. Re-read that record and reconcile
the selection instead of overwriting or silently creating another identity.

Classify the intended work using [the taxonomy](references/taxonomy.md).
Select an existing phase in the active plan appropriate to this application
and scope. `PLAN-001` is the Agent Red GA plan, not the platform-wide default.
Do not create a new plan or phase merely to avoid selecting the correct scope.

## Record the executable test first

GOV-12 requires an active specification and an executable test before work-item
creation. GOV-03 requires an unambiguous result, GOV-18 meaningful assertions,
and GOV-10 coverage through the actual interface. Choose the suitable declared
test type; naming a file is not evidence that it passed.

Prepare a UTF-8 JSON object such as:

```json
{
  "title": "Verify the specified behavior",
  "spec_id": "SPEC-SELECTED",
  "test_type": "integration",
  "test_file": "platform_tests/groundtruth_kb/test_selected_behavior.py",
  "test_function": "test_selected_behavior",
  "expected_outcome": "The specified effect occurs and an invalid request leaves current state and history unchanged."
}
```

```text
gt tests record --id TEST-SELECTED --fields-file test.json --expected-version 0 --actor "<current-context>" --change-reason "<specific evidence purpose>" --json
gt tests show TEST-SELECTED --json
```

Use the actual application scope, file, callable and expected behavior. For an
existing TEST, re-read its definition and version before an amendment; do not
present historical execution metadata as evidence for a changed definition.

## Assign the test to the selected current phase

Read the selected plan and phase:

```text
gt test-plans show PLAN-SELECTED --json
gt test-phases show PHASE-SELECTED --json
```

Require the plan to be active. Preserve the phase's current `test_ids` order and
members, appending the selected test once if absent. Write that complete array
in `phase-fields.json` and use the version just read:

```text
gt test-phases record --id PHASE-SELECTED --fields-file phase-fields.json --expected-version <current-version> --actor "<current-context>" --change-reason "Assign the selected executable test under GOV-13" --json
gt test-phases show PHASE-SELECTED --json
```

Test creation and phase amendment are separate native CAS operations. Complete
and read back both before creating work or claiming coverage; do not claim an
atomic combined transaction. On conflict, re-read and preserve intervening
members. An unphased test cannot satisfy the current work-evidence rule.

## Create the work item in the selected project

Prepare the authored fields in `wi.json`:

```json
{
  "title": "Implement the specified behavior",
  "origin": "new",
  "component": "maintenance_tool",
  "description": "The bounded implementation and its expected effects.",
  "source_spec_id": "SPEC-SELECTED",
  "source_test_id": "TEST-SELECTED",
  "priority": "P2"
}
```

```text
gt backlog record --id WI-SELECTED --project-id PROJECT-SELECTED --fields-file wi.json --expected-version 0 --actor "<current-context>" --change-reason "<specific owner-selected intake purpose>" --json
gt backlog show WI-SELECTED --json
```

`resolution_status` is not an authored creation field; the new item opens as
`open`. Priority is `P0`–`P3`. Current native writers refuse missing or inactive
specification links, non-executable test links and tests outside active plan
phases. Work creation is not implementation start or a bridge proposal.

## Report the verified readback

Report the WI, project membership, specification, executable TEST, current
plan/phase membership, origin, component and priority. Distinguish current
definitions from actual test results and identify any refused or incomplete
step. Apply durable corrections only through their existing canonical writers;
do not retain a separate decision or session-progress archive.
