# GT-KB Project Root Boundary

This rule is mandatory for all GT-KB work and for every application developed,
managed, scaffolded, upgraded, or governed by GT-KB.

## Directive

- All active files for the GT-KB project MUST be within `E:\GT-KB`.
- No GT-KB artifact may be created, read as a live dependency, updated, verified,
  or required from outside `E:\GT-KB`.
- GT-KB demo/application files MUST be within `E:\GT-KB\applications\`.
- **EXCEPTION:** `groundtruth-kb/examples/` (adopter fixtures) are exempt from the `applications/` mandate.
- Agent Red is the reference adopter application for GT-KB. Its application files
  live at `E:\GT-KB\applications\Agent_Red\` per the root harness instruction file section
  Mandatory Project Root Boundary, governed by the isolation contract at
  `applications/Agent_Red/.gtkb-app-isolation.json`. The hosted form deploys
  from a lifecycle-independent repository at
  `https://github.com/mike-remakerdigital/agent-red`. Unqualified GT-KB tooling references
  (CLI, CI workflows, GitHub Actions, release evidence) must not resolve
  silently to Agent Red repository or CI surfaces; Agent Red surfaces are addressed
  explicitly when in scope.
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
- Any live GT-KB artifact discovered under `E:\Claude-Playground` must be
  relocated to its correct in-root home before that archive is deleted. In-root
  Agent Red application artifacts belong under `E:\GT-KB\applications\Agent_Red\`;
  out-of-root Agent Red repository or CI artifacts are external surfaces that
  must be explicitly scoped when used as evidence.
- When a live path is unknown, fail closed and request or derive an in-root path.
- Any proposal, review, implementation, or test that depends on a path outside
  the allowed roots is a NO-GO until revised to be root-contained.
- Any migration of application code must move toward
  `E:\GT-KB\applications\<application-name>\`; new application files must not be
  added outside `E:\GT-KB\applications\`.

## Harness-Local Scratchpad Non-Authority Boundary

Harness-local scratchpads are non-authoritative. This includes per-harness planning/brain files,
automation memory, harness auto-memory, and the
`MEMORY.md` hierarchy, including `memory/MEMORY.md`, scaffolded root
`MEMORY.md`, and harness-created mirrors or cache files.

Formal GT-KB artifacts, implementation reports, verification verdicts, tests,
doctor checks, bridge evidence, governed decisions, release evidence, and
dependency closure must not read from or depend on harness-local scratchpads as
authority. Project-relevant information originating in a scratchpad must be
promoted into governed in-root artifacts such as MemBase, the Deliberation
Archive, specifications, ADR/DCL/GOV records, bridge files, source, tests, or
approved reports before it is cited, verified, or used as a dependency.

This boundary does not forbid harness scratchpads from existing as runtime
byproducts or operational notes. It forbids treating them as GT-KB authority.
The External Harness Executable Resolution Exception remains executable-only:
it authorizes invoking registry-enumerated harness executables, not reading, writing,
verifying, or requiring harness-local files, memory, planning documents, or
evidence outside `E:\GT-KB`.

The deterministic doctor check `_check_harness_local_scratchpad_boundary`
enforces this declaration by verifying the required rule surfaces carry the
non-authority language and by failing when those surfaces regress to granting
positive authority to harness-local scratchpads.

## Sandbox Output (retired exception)

The former Sandbox Output Exception (`DCL-PROJECT-ROOT-BOUNDARY-SANDBOX-OUTPUT-EXCEPTION-001`,
retired) allowed rehearsal-class operations to emit regenerable output outside
`E:\GT-KB` under an owner-approved rehearsal manifest and the executable
allowlist in `scripts/rehearse/_common.py`. The rehearsal wrapper, its manifest
and that allowlist are retired, so no operation can satisfy the exception and
it grants nothing. No rehearsal-class output exception remains; this section
is retained as history only and is not an authority carrier.

## SQLite Snapshot Output (retired exception)

The `gt db snapshot` command, its scheduled task and the doctor's snapshot
freshness and output-allowlist checks are retired (O-7 R22), and with them the
former DB-Snapshot Output Exception (`DCL-PROJECT-ROOT-BOUNDARY-DB-SNAPSHOT-OUTPUT-EXCEPTION-001`,
retired). A SQLite snapshot is neither a health criterion nor a production
fallback. The only remaining snapshot use is the explicit offline migration
input read by `gt db postgres export-current --sqlite-snapshot`; that file is
supplied by the operator and is not a project-root output. The PostgreSQL
authority is recovered from physical backups and WAL archives, which live
outside the project root under their own installation contract.

## External Harness Executable Resolution Exception

GT-KB cross-harness operations may resolve and invoke external AI coding harness
executables (registry-enumerated harness CLIs) that are installed outside E:\GT-KB by
their own toolchains (npm-global, user-install, system package managers) when ALL
of the following hold:

1. The executable belongs to a current canonical harness installation record,
   read through the native `gt harness show <id>` CLI or authority service,
   with an invocation_surfaces.*.argv entry. Only command names declared by
   those current records are eligible; generated files confer no eligibility.
2. Resolution uses one of: (a) ambient PATH resolution provided by the launching
   context (the mechanism by which registered harnesses are already dispatched), or (b) a
   location configured in the in-root platform env source-of-truth (.env.local)
   per GOV-ENV-LOCAL-AUTHORITY-001, which is the SoT for hard path prefixes and
   CLI configuration choices. No out-of-root absolute path is stored as a literal
   in source, specs, registry values, or state.
3. The dependency is limited to INVOKING the external harness executable. It does
   NOT extend to reading, writing, verifying, or requiring any other out-of-root
   project artifact (specs, tests, source, state, bridge, dashboard, knowledge
   base).
4. The deterministic doctor check _check_external_harness_exec_boundary enforces
   the bound: it confirms any out-of-root executable dependency in GT-KB
   cross-harness code resolves to a registry-enumerated harness command, and
   reports FAIL if non-harness project work is routed to an out-of-root path.

This exception is narrow and harness-specific. External AI coding harnesses are,
by their nature, installed outside the platform root by their own toolchains, and
the cross-harness dispatch substrate must invoke them. The exception does NOT
relax the core directive for project artifacts: all active GT-KB project files and
artifacts MUST remain within E:\GT-KB, and no GT-KB project artifact may be
created, read as a live dependency, updated, verified, or required from outside
that root.

Authority: `DCL-PROJECT-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXEC-EXCEPTION-001`.

Provenance: `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (owner S366 AUQ).
