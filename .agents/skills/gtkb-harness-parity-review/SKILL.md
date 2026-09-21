---
name: gtkb-harness-parity-review
description: Review an assigned harness configuration change against the shared baseline and native CLI, checking derivation, drift and real invocation without using peer-harness state.
---
# Review harness configuration

Use this skill for an explicitly assigned baseline, projector or harness
configuration work item. Read its current task context and formal requirements
through the native CLI. The role belongs to this session context; a model,
provider or installed harness does not carry a standing role assignment.

Inspect the shared baseline and the generator sources in the reviewed scope.
Use `gt harness project <harness> --validate` to check derivation without
changing installed output, `--dry-run` to inspect planned paths, and `--check`
to compare this harness's installed output with the current derivation.

All expected skills and hook registrations must come from the baseline and the
projector's declared profile. An old generated copy or a missing feature's old
proposal cannot satisfy that requirement. A profile needs an implemented
renderer for each capability it declares.

Report these outcomes separately:

- The reviewed sources can produce the required configuration.
- The selected installed configuration agrees with those sources.
- Real fresh-context execution invokes the required hooks and native CLI paths.

A clean render does not prove invocation, delivery or effect containment. Exercise
allowed operations and expected refusals through the installed entry points.
Compare results with the current native services and exact reviewed artifact
scope. Record failures and unavailable evidence directly.

Use `gt harness diagnostic --harness-id <ID> --json` to read current installation
metadata through the configured native service. Add `--native-context-id <ID>`
only for an explicitly selected context. Its immutable binding establishes that
context's role; it does not establish an association with the selected harness.
No context is selected from environment hints, registry roles or recent files.

The local report performs no provider request. A metadata fingerprint describes
only the canonical installation fields. Unknown runtime identity, metrics, hooks,
guard behavior and adapter health stay unavailable. A partial report with
unqualified parity is useful diagnostic evidence, never a passing host test.
The diagnostic contract is `SPEC-HARNESS-DIAGNOSTIC-MODE-001`; its remaining
measurement and actual-host requirements need separate executed evidence.

Harnesses are independent consumers. This session uses its own configuration
and runtime. Shared baseline and projector tests may verify declared output
contracts; do not inspect another harness's private directories, infer its role,
or coordinate directly with it.

Correct the canonical source and regenerate only the selected derived output.
Keep generated configuration out of the project work-product commit. Native
claim, independent review and project finalization requirements still apply.
