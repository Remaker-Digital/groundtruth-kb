# GT-KB Project Root Boundary

This rule is mandatory for all GT-KB work and for every application developed,
managed, scaffolded, upgraded, or governed by GT-KB.

## Directive

- All active files for the GT-KB project MUST be within `E:\GT-KB`.
- No GT-KB artifact may be created, read as a live dependency, updated, verified,
  or required from outside `E:\GT-KB`.
- GT-KB demo/application files MUST be within `E:\GT-KB\applications\`.
- Agent Red is the reference adopter application for GT-KB. Its application files
  live at `E:\GT-KB\applications\Agent_Red\` per `CLAUDE.md` section
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

## Sandbox Output Exception

GT-KB rehearsal-class operations may emit runtime output to a path outside `E:\GT-KB` when ALL of the following hold:

1. The path is declared in an owner-approved manifest field (currently `output_dir` in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`).
2. The path matches a sandbox-allowlist pattern enforced by Rule M2 in `scripts/rehearse/_common.py`. Current allowlist (per `_OUTPUT_DIR_ALLOWLIST_DESC` source constant): "C:/temp/agent-red-rehearsal* or /tmp/agent-red-rehearsal* (extend _OUTPUT_DIR_ALLOWLIST_PATTERNS for additional sandbox paths)".
3. The output is regenerable evidence (preview artifacts, classification manifests, dry-run DBs), not canonical project state.
4. The output is documented in the bridge proposal that authorizes the operation, and the bridge passes Codex review with the path explicit.

Source: `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` and the manifest §3.3 owner decision recorded at S311 (commit `12538b97` context). Rationale: rehearsal output must avoid cloud-sync corruption (Google Drive currently syncs `E:`); the in-root `.driveignore` mechanism per commit `12538b97` adds a per-path enumeration burden that does not scale with rehearsal cardinality.

Outputs covered by this exception remain outside the scope of GT-KB canonical state, audit history, release evidence, regression tests (except as preview-evidence inputs), and dependency closure.

Owner approval is per-manifest, not per-run; adding new sandbox paths requires:

1. A code change to `_OUTPUT_DIR_ALLOWLIST_PATTERNS` in `scripts/rehearse/_common.py` (which extends the executable allowlist).
2. An owner-approved manifest update through the bridge protocol (which exercises the new pattern under owner review).
3. Synchronized update of this rule's allowlist citation to keep rule text and source code aligned (verified by tests/scripts/test_rehearse_isolation.py asserting `_OUTPUT_DIR_ALLOWLIST_DESC` equals the rule-text quotation).

## External Harness Executable Resolution Exception

GT-KB cross-harness operations may resolve and invoke external AI coding harness
executables (e.g., codex, claude, gemini) that are installed outside E:\GT-KB by
their own toolchains (npm-global, user-install, system package managers) when ALL
of the following hold:

1. The executable is an AI coding harness enumerated in the harness registry
   (harness-state/harness-registry.json) via an invocation_surfaces.*.argv entry.
   Only registry-enumerated harness command names are eligible.
2. Resolution uses one of: (a) ambient PATH resolution provided by the launching
   context (the mechanism by which codex/claude are already dispatched), or (b) a
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

Source: DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION (owner S366 AUQ).
