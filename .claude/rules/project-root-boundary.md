# GT-KB Project Root Boundary

This rule is mandatory for all GT-KB work and for every application developed,
managed, scaffolded, upgraded, or governed by GT-KB.

## Directive

- All active files for the GT-KB project MUST be within `E:\GT-KB`.
- No GT-KB artifact may be created, read as a live dependency, updated, verified,
  or required from outside `E:\GT-KB`.
- GT-KB application files MUST be within `E:\GT-KB\applications\`.
- Agent Red application files MUST be within `E:\GT-KB\applications\Agent_Red\`.
- `E:\Claude-Playground` is an archive only. It is not a live GT-KB,
  Agent Red, harness-state, bridge, dashboard, memory, source, verification, or
  dependency location.
- There are no exceptions.

## Operational Consequences

- Do not route GT-KB implementation, verification, bridge, dashboard, harness,
  hook, skill, plugin-cache, role-record, lifecycle-guard, or knowledge-base work
  to home-directory paths, temp-directory paths, sibling checkouts, or legacy
  project locations.
- Historical references to obsolete external paths may remain only as historical
  evidence. They must not be used as current instructions, defaults, examples,
  verification paths, or live dependencies.
- Any live GT-KB or Agent Red artifact discovered under `E:\Claude-Playground`
  must be relocated to its correct in-root home before that archive is deleted.
- When a live path is unknown, fail closed and request or derive an in-root path.
- Any proposal, review, implementation, or test that depends on a path outside
  the allowed roots is a NO-GO until revised to be root-contained.
- Any migration of application code must move toward
  `E:\GT-KB\applications\<application-name>\`; new application files must not be
  added outside `E:\GT-KB\applications\`.
