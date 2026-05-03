NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 3 Init Defaults

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice3-init-defaults-2026-05-02`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-001.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the proposal against `.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, the Phase 9 plan, the Slice 3 scoping
GO, and the current scaffold/CLI implementation.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `gt project init scaffold isolation`
- `GTKB-ISOLATION-017 Slice 3`
- `ADR-ISOLATION-APPLICATION-PLACEMENT gt project init`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. Active prior review context is the bridge
thread itself, especially `bridge/gtkb-isolation-017-scoping-003.md` and
`bridge/gtkb-isolation-017-scoping-004.md`.

## Findings

### F1 - P1 - `gt project init` CLI default path is out of scope, so the proposal does not implement the Phase 9 command behavior

Claim: The proposal plans helper-level validation but leaves the actual `gt project init`
entrypoint/default target behavior unscoped and explicitly unprobed.

Evidence:

- Phase 9 requires `gt project init` to mechanically create
  `<gt-kb-root>/applications/<name>/` and refuse to land outside:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:106-108`.
- The current CLI default is still `Path.cwd() / project_name`, and the
  `ScaffoldOptions` construction does not pass any GT-KB root:
  `groundtruth-kb/src/groundtruth_kb/cli.py:826-841`.
- The proposal's modified-file list excludes `groundtruth-kb/src/groundtruth_kb/cli.py`
  and says the CLI entrypoint location is still pending probe:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-001.md:33-38`
  and `:127-129`.

Risk / impact: A helper-level refusal can make the default CLI path fail instead
of creating the required adopter application under `applications/`. That misses
the user-facing Phase 9 requirement and would leave `gt project init my-app`
behavior incorrect even if `scaffold_project()` unit tests pass.

Recommended action: Revise the proposal to include `groundtruth-kb/src/groundtruth_kb/cli.py`.
Specify how the CLI resolves the GT-KB host root and how the default target
becomes `<gt-kb-root>/applications/<project_name>`. Add CLI-level tests for the
default path and explicit `--dir` refusal/acceptance behavior.

Decision needed from owner: None.

### F2 - P1 - Spec-derived tests do not cover the full Phase 9 scaffold enumeration

Claim: The test plan covers the new service endpoint, README, release-readiness,
Codex hook intent, approval `.gitkeep`, and golden fixtures, but it does not
explicitly map tests to several Phase 9 Section 1 scaffold obligations.

Evidence:

- Phase 9 Section 1 enumerates required scaffold artifacts and exclusions:
  `groundtruth.toml`, `groundtruth.db`, `bridge/INDEX.md` plus README bridge
  header, `memory/work_list.md`, `memory/release-readiness.md`, `.claude/rules/`,
  `.claude/hooks/`, `.claude/settings.json`, `.codex/hooks.json`,
  `.groundtruth/formal-artifact-approvals/`, no pre-populated dashboard,
  segregated `.gitignore`, and no product source/tests/raw credentials/secrets:
  `...GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:114-139`.
- Slice 3 scoping carried the same "scaffold all artifacts enumerated" requirement:
  `bridge/gtkb-isolation-017-scoping-003.md:93-115`.
- The proposal's T1-T13 mapping does not name tests for at least:
  `groundtruth.db` initialized with app-scope tables only, `bridge/INDEX.md` and
  bridge-essential README header, `memory/work_list.md`, `.claude` wrappers with
  no embedded enforcement logic, non-prepopulation of `docs/gtkb-dashboard/`,
  segregated `.gitignore`, and absence of forbidden product artifacts/secrets:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-001.md:82-96`.
- The bridge protocol requires LO to reject proposals when relevant specifications
  are missing from the test mapping or proposed tests do not map back to the
  linked specifications: `.claude/rules/file-bridge-protocol.md:27-35`.

Risk / impact: Slice 3 could pass the proposed suite while still omitting or
mis-shaping required scaffold artifacts. That would create a false GO against
Phase 9 and push incomplete adopter defaults into later slices.

Recommended action: Revise the test matrix so every Phase 9 Section 1 bullet is
covered by either a named behavior test, a golden-fixture assertion explicitly
tied to that bullet, or a documented waiver. The verification commands should
also run the bridge/index/rule, smoke, and leakage tests that are being relied on.

Decision needed from owner: None.

### F3 - P2 - The proposal cites non-existent live paths for implementation and ADR evidence

Claim: Several cited paths are not present in the current checkout, so the
proposal is not yet mechanically actionable as written.

Evidence:

- The proposal lists
  `groundtruth-kb/src/groundtruth_kb/templates/managed-artifacts.toml`, but the
  live registry is `groundtruth-kb/templates/managed-artifacts.toml`.
  `rg --files -g 'managed-artifacts.toml' groundtruth-kb` found only the latter.
- The proposal cites the authoritative ADR file at
  `groundtruth-kb/docs/architecture/adrs/ADR-ISOLATION-APPLICATION-PLACEMENT-001.md`,
  but that file is absent in this checkout; `groundtruth-kb/docs/architecture/`
  currently contains only `product-split.md`.
- The same absence applies to the file-form
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001.md`; current live evidence appears to be
  bridge/KB/test references, not a local ADR markdown file.

Risk / impact: Prime Builder may edit the wrong path, fail to register new
artifacts, or cite non-live authority that LO cannot verify under the root-boundary
and live-authority rules.

Recommended action: Correct the registry path and cite the live authority for
each ADR, such as the relevant MemBase record, bridge thread, or an actual
in-root file if one is added. Keep all references within `E:\GT-KB`.

Decision needed from owner: None.

## Verdict

NO-GO until the proposal is revised to include the CLI entrypoint/default-target
behavior, complete the Phase 9 Section 1 spec-to-test mapping, and correct the
non-existent live paths.

File bridge scan: 1 entry processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
