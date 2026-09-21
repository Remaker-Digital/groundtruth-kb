# Templates and managed sources

Project templates create application-specific files under the supported native
initializer. They do not establish a second harness baseline. The selected
application/project, registered host root, current authority and overwrite scope
are validated by the native initializer; inspect its dry-run before application.

## Shared harness material

Root `AGENTS.md` is authored once. `.agents/skills` holds the shared skills;
`.harness-baseline-configuration/rules`, `hooks` and `routing.toml` hold the
focused rules, hook implementations and API routing. Host settings and pointer
stubs are derived by the declared projection profile. See
[Harness projection](harness-projection.md) for source paths and output classes.

Do not copy rules or hook scripts into a host directory, generate another
`AGENTS.md` from a duplicate baseline file, or create an application-local skill
body. A hosted application's skill pointer resolves to the shared host tree.
Root `CLAUDE.md` and `.goosehints` are concise pointers, not independent guidance.

## Application files and upgrades

The selected initializer may author application configuration, starter source,
specification inputs and optional CI files. Inspect the current native command,
selected profile and managed-artifact registry for its exact inventory; an old
template count is not an upgrade contract. Application source belongs to that
application's governed work product. Template existence alone does not make a
file managed or grant permission to replace an existing file.

Use the native project doctor/upgrade routes for their declared checks and
repairs. Use `gt harness project <profile>` for shared-source derivation. A clean
doctor or projection result does not prove an actual host session loaded its
instructions, discovered a skill or executed a hook.

## Current work process

The owner selects the exact task and supplies literal init/activity inputs.
Each fresh context uses native binding and reads current project/work/bridge
state through the CLI. Independent contexts author proposals, implementations,
reports and verdicts according to the current bridge phase. Dispatcher does not
author lifecycle content, and owner dispatch remains in place until the successor
dispatcher is independently qualified and activated.

Session logs and temporary bridge payloads are not durable authority. Do not
create a memory or deliberation archive to stand in for current formal, project
or work-item records. See [Dual-Agent Setup](../tutorials/dual-agent-setup.md).

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
