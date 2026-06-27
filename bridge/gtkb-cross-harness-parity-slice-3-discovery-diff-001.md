NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 0eb73a79-4ad6-40c0-88e9-16f797f0ef2e
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4877

Document: gtkb-cross-harness-parity-slice-3-discovery-diff
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Recommended commit type: feat

target_paths: ["scripts/parity_discovery_diff.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_parity_discovery_diff.py"]

## Summary

Slice 3 of `PROJECT-GTKB-CROSS-HARNESS-PARITY` builds the **discovery-diff**
that the foundation `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` requires
(assertions PARITY-DIFF-EXISTS + PARITY-DIFF-WIRED). It is the enforcement
mechanism the ADR demotes the registry in favor of (Q5): the registry is no
longer the existence authority — the diff **discovers** actual harness surfaces
and uses the registry only as the canonical-purpose / per-harness surface map /
waiver store.

The slice delivers three on-disk artifacts:

1. `scripts/parity_discovery_diff.py` — enumerates actual hook surfaces from
   `.claude/settings.json` and `.codex/hooks.json`, maps each to a capability
   key, diffs the keys across the applicability-scoped active population, and
   FAILs (exit non-zero) on any **unwaived** asymmetry. Consumes the Slice-2
   reader accessors (`resolve_applicability`, `build_surface_map`,
   `load_parity_waivers`).
2. A new `gt project doctor` check `_check_parity_discovery_diff` wired at
   **WARN** (per Q6 ramp: WARN now, FAIL after the Slice-6 coverage audit).
3. `platform_tests/scripts/test_parity_discovery_diff.py` — derives tests from
   the linked DCL assertions, including the acceptance test that the diff
   **detects the `::open`/`::close` topic-envelope-routing asymmetry**
   (`session_wrapup_trigger_dispatch.py` on Codex `UserPromptSubmit`, absent
   from Claude's `UserPromptSubmit` chain) and a synthetic-unregistered-hook
   regression fixture.

A separate, owner-approval-gated formal step (NOT in `target_paths`; the
MemBase DB is gitignored) encodes the five `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
assertions as structured `assertions` JSON via
`gt spec update DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 --assertions-json`.
That step is presented to the owner via AskUserQuestion and executed through the
formal-artifact approval-packet dance during implementation; it is called out
here for review completeness.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — the bidirectional,
  applicability-scoped behavioral-parity invariant. This slice realizes the
  discovery-diff enforcement mechanism (Q5): the diff discovers existence and
  fails on unwaived asymmetry across the applicable population (Q4).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — directly satisfies
  assertion **PARITY-DIFF-EXISTS** (Slice 3: a discovery-diff module that
  enumerates actual harness surfaces and diffs them across the
  applicability-scoped population) and **PARITY-DIFF-WIRED** (Slices 3, 6: the
  diff runs as a doctor check at WARN — the FAIL ramp and CI gate are Slice 6).
  It contributes **PARITY-APPLICABILITY-RULE** (Slices 2-3: role-relative vs
  universal, active-only) by consuming the Slice-2 `resolve_applicability`.
- `GOV-20` (architecture decision governance) — the ADR/DCL workflow this
  program follows; Slice 3 implements two further DCL assertions derived from
  the ADR and (in the gated formal step) encodes the DCL's assertion set.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governing this
  proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Test Plan below
  derives tests from the linked DCL assertions (PARITY-DIFF-EXISTS,
  PARITY-DIFF-WIRED, PARITY-APPLICABILITY-RULE).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — path-triggered by the edit to
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. The change is a
  platform-internal doctor check that adds harness-agnostic parity tooling; it
  introduces no application/adopter code, respects the platform/application
  isolation boundary (the doctor module is platform lifecycle infrastructure),
  and adds no out-of-root dependency.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — this slice is delivered
  as durable artifacts (a tracked script, a doctor check, a test, and the gated
  DCL assertion encoding), consistent with artifact-oriented development.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the slice progresses the
  parity program's specified artifacts through their lifecycle (the DCL
  assertions move from description-only `specified` toward structured/verified);
  no artifact is silently deferred or retired.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the work is governed
  through the bridge protocol, the standing project/PAUTH, and the
  formal-artifact approval path for the DCL mutation.

The proposed tests derive from the linked specs: the enumeration + detection
tests map to PARITY-DIFF-EXISTS; the doctor-check test maps to PARITY-DIFF-WIRED;
the population-scoping test maps to PARITY-APPLICABILITY-RULE.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CROSS-HARNESS-PARITY-001` and
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` already specify the discovery-diff
mechanism (Q5 / PARITY-DIFF-EXISTS), the doctor WARN ramp (Q6 / PARITY-DIFF-WIRED),
and the applicability rule (Q4 / PARITY-APPLICABILITY-RULE). No new or revised
requirement is needed; this slice implements those existing constraints. The
DCL `--assertions-json` encoding is a structured re-expression of the DCL's
already-specified assertion set, not a new requirement.

## Cross-Harness Disposition

These `target_paths` are parity-infrastructure and platform files
(`scripts/parity_discovery_diff.py`,
`groundtruth-kb/src/groundtruth_kb/project/doctor.py`, the test file), not
per-harness runtime surfaces. The disposition is declared per the ADR Q8 / DCL
assertion PARITY-DISPOSITION-GATE contract (the mechanical gate itself lands in
Slice 4; declared proactively here).

- **Nature of change:** the discovery-diff script and doctor check are
  harness-agnostic platform tooling that *reads* every harness's surfaces; they
  introduce no per-harness runtime capability.
- **In-root artifact declaration (ADR-ISOLATION-APPLICATION-PLACEMENT-001 /
  CLAUSE-IN-ROOT):** all artifacts this slice generates — the new
  `scripts/parity_discovery_diff.py`, the edit to the platform doctor module,
  the new test file, and this bridge file under the `bridge/` directory — are
  written in-root under the GT-KB project root. The discovery-diff script emits
  its JSON/markdown to stdout (or an in-root `.gtkb-state/` path when a file is
  requested); no out-of-root, temp-directory, or user-home output is produced.
- **Per-harness behavioral parity:** no behavioral asymmetry is introduced. The
  tooling's applicability is **universal** — it runs identically wherever
  `gt project doctor` runs.
- **Scope note (deliberate, not a waiver):** the Slice-3 hook-surface
  enumerator compares only harnesses that declare a hook-config file
  (`.claude/settings.json` for claude, `.codex/hooks.json` for codex). The
  cloud-shim harnesses (ollama, cursor, openrouter) and the inactive
  antigravity harness declare no hook-config surface, so they are
  **surface-not-applicable** for the hook-surface axis (per the design's
  start-with-hook-arrays scope and the section 7 risk note) — they are excluded
  upstream by applicability, not suppressed by a waiver. Expanding the
  enumerator to other surface classes (commands, MCP, startup) is a Slice-6
  coverage-audit follow-on.
- **Waivers:** none added by this slice; no live `[[parity_waivers]]` record
  exists yet (the first real disposition is the Slice-5 `::open` conformance
  case, which resolves rather than waives).

## Design

### A. Discovery-diff script — `scripts/parity_discovery_diff.py` (new)

A standalone, importable module (stdlib + the Slice-2 reader accessors only):

1. **Surface enumeration.** For each harness with a hook-config file, parse the
   five event arrays (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`,
   `SessionStart`, `Stop`) and extract the referenced script path from each
   `command` string:
   - claude: `.claude/settings.json` — match `.claude/hooks/<name>.py`,
     `scripts/<name>.py`, and skill references.
   - codex: `.codex/hooks.json` — match `.codex/gtkb-hooks/<name>.{py,cmd}`,
     `.claude/hooks/<name>.py`, `scripts/<name>.py`, and `<name>.cmd` wrappers.
   The output is a per-harness map of `event -> set(discovered surface paths)`.
2. **Capability keying.** Map each discovered surface to a capability key:
   - **registered** surfaces resolve to their registry capability `id` by
     matching the discovered path against the per-harness `surface` in
     `build_surface_map(registry)` (basename-normalized, so a `.cmd` wrapper that
     fronts a canonical `.py` resolves to the same capability when the registry
     declares it).
   - **unregistered** surfaces key by a derived identity: the normalized script
     basename (so the same conceptual hook on two harnesses keys together, and
     an unregistered single-harness hook stands alone). This is what catches
     unregistered asymmetry — the registry is not the existence authority.
3. **Applicability + active-only population.** For each capability key, resolve
   the applicable population: registered capabilities via
   `resolve_applicability` (role-relative → active harnesses holding the
   required roles; universal → all active harnesses) read from the harness
   projection; unregistered hook surfaces default to **universal** across the
   hook-config-declaring active population (claude + codex for this slice).
   Inactive harnesses are excluded (active-only per Q4).
4. **Diff.** For each capability key present on at least one harness in its
   applicable population, every other applicable harness must either declare a
   surface for it or carry a matching `[[parity_waivers]]` record
   (`capability_id` + `harness`, validated by the Slice-2
   `validate_parity_waiver`). A missing, unwaived surface is an **asymmetry
   finding** (capability key, present-on harnesses, absent-on harnesses, waiver
   status).
5. **Output + exit.** Emit structured JSON and a markdown summary; expose
   `run_discovery_diff(project_root) -> DiffReport` for the doctor + tests; CLI
   `main()` exits non-zero when any unwaived asymmetry exists, 0 otherwise.

Because the current Claude and Codex `UserPromptSubmit` chains are genuinely
asymmetric (Codex runs `session_wrapup_trigger_dispatch.py`; Claude does not —
and Claude runs several hooks Codex does not), the Slice-3 diff will surface a
set of WARN findings, **including the `::open` asymmetry**. That is expected and
correct under the Q6 ramp: the diff lands at WARN so the coverage-audit window
(Slice 6) can resolve or waive each finding before WARN→FAIL promotion.

### B. Doctor wiring — `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

Add `_check_parity_discovery_diff(target) -> ToolCheck`, modeled on
`_check_registered_hooks_tracked` / `_check_cross_harness_trigger`. It imports
`run_discovery_diff` from `scripts/parity_discovery_diff.py` (guarded import,
mirroring the script's own `scripts.` / bare fallback), runs it against
`target`, and returns:

- `status="pass"` when no unwaived asymmetry exists;
- `status="warning"` (never `fail` at Slice 3) listing the asymmetric capability
  keys when unwaived asymmetries exist;
- `status="info"`/`warning` fail-soft when a hook-config file is missing or
  malformed.

Register the check in the doctor's assembled check list so it runs under
`gt project doctor`. WARN→FAIL promotion is explicitly deferred to Slice 6.

### C. DCL assertion encoding (owner-approval-gated; not in target_paths)

`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`'s five assertions are currently
description-only (the DB `assertions` column is None, noted in the Slice-1
verdict). This slice encodes them as structured `assertions` JSON via
`gt spec update DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 --assertions-json ...`.
This is a formal-artifact mutation: the assertion content is presented to the
owner via AskUserQuestion, approved, and written through the
`--dry-run`-writes-the-approval-packet dance under
`.groundtruth/formal-artifact-approvals/`. The MemBase DB is gitignored, so this
mutation does not appear in the slice commit; it is recorded in the
post-implementation report with the approval-packet reference.

### D. Tests — `platform_tests/scripts/test_parity_discovery_diff.py` (new)

Derived from the linked DCL assertions:

- **Enumeration (PARITY-DIFF-EXISTS):** the enumerator extracts the expected
  hook-script set from the live `.claude/settings.json` and `.codex/hooks.json`
  (e.g. asserts `session_wrapup_trigger_dispatch` is discovered on codex
  `UserPromptSubmit`).
- **Acceptance — `::open` detection (PARITY-DIFF-EXISTS):** `run_discovery_diff`
  against the live tree yields an asymmetry finding for the
  `session_wrapup_trigger_dispatch` capability key (present codex, absent
  claude, unwaived). This is the acceptance criterion that must be detectable
  pre-Slice-5 and become green only after Slice 5 wires it into Claude.
- **Regression — synthetic unregistered single-harness hook (PARITY-DIFF-EXISTS):**
  a tmp-path fixture with a codex-only unregistered hook produces an asymmetry
  finding; the symmetric counterpart produces none.
- **Waiver suppression (PARITY-APPLICABILITY-RULE / waiver store):** a synthetic
  registry with a matching `[[parity_waivers]]` record suppresses the
  corresponding finding; an expired/absent waiver does not.
- **Population scoping (PARITY-APPLICABILITY-RULE):** cloud-shim / inactive
  harnesses with no hook-config file are excluded from the hook-surface diff
  (surface-not-applicable), not reported as asymmetries.
- **Doctor wiring (PARITY-DIFF-WIRED):** `_check_parity_discovery_diff` returns
  `warning` when an unwaived asymmetry exists and `pass` on a symmetric fixture;
  never `fail` at Slice 3.

## Test Plan / Spec-Derived Verification

| Linked spec / assertion | Derived test | Command |
|---|---|---|
| DCL PARITY-DIFF-EXISTS | enumeration + `::open` detection + synthetic-hook regression + waiver suppression in `test_parity_discovery_diff.py` | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py -q` |
| DCL PARITY-DIFF-WIRED | `_check_parity_discovery_diff` returns warning on asymmetry, pass on symmetric fixture | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py -q` |
| DCL PARITY-APPLICABILITY-RULE | population-scoping (cloud-shim/inactive excluded) + role-relative/universal resolution | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py -q` |
| Behavior preservation | existing parity matrix + schema validator unchanged | `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_cross_harness_parity_schema.py -q` |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: all new tests pass; the live-tree `::open` asymmetry is detected;
the synthetic single-harness hook is caught; `gt project doctor` shows the new
check at WARN (not FAIL); existing parity/schema tests remain green.

## Owner Decisions / Input

Implementation authority flows from the existing owner authorization
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (active; owner decision
`DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), which authorizes bounded
implementation of the program covering slice work items by active project
membership. The program-home state (owner AUQ 2026-06-27, archived
`DELIB-20266265`) reactivated the project and elected membership-based PAUTH
coverage; **WI-4877** (this slice) is the active member that authorizes this
proposal.

One owner decision is required during implementation, not to file this proposal:

- **DCL assertion encoding (formal-artifact mutation):** encoding the five
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` assertions as structured
  `--assertions-json` is a formal-artifact mutation requiring an
  owner-approval packet. It will be presented via AskUserQuestion with the exact
  assertions JSON before the `gt spec update` is executed.

No other new owner decision is required to implement Slice 3.

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — the build-ready design; §5
  build sequence step 3 is this slice (discovery-diff → doctor WARN), and §6
  acceptance criteria 1-2 (detect the `::open` asymmetry; catch a synthetic
  unregistered single-harness hook) are realized by the tests here.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` — owner grill Q5-Q8
  resolving the discovery-diff mechanism, the WARN→FAIL ramp (Q6), and registry
  demotion.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — the owner authorization basis.
- `DELIB-20266265` — owner AUQ reactivating the program home and electing
  membership-based PAUTH coverage for the slice work items.
- `bridge/gtkb-cross-harness-parity-slice-2-registry-schema-004.md` — Slice-2
  VERIFIED verdict; this slice consumes its delivered accessors
  (`resolve_applicability`, `build_surface_map`, `load_parity_waivers`,
  `validate_parity_waiver`) and acts on its note that the DCL `assertions` DB
  column is still description-only (encoded here as a gated formal step).
- `bridge/gtkb-cross-harness-parity-slice-1-adr-dcl-004.md` — Slice-1 VERIFIED
  verdict establishing the ADR/DCL foundation and deferring `--assertions-json`
  encoding to Slice 3.

## Risk / Rollback

- **Risk:** the enumerator's surface inventory is incomplete (only hook arrays),
  so the diff could miss command/MCP/startup asymmetries. *Mitigation:* Q6 /
  the section 7 risk note explicitly scope Slice 3 to hook arrays (where the
  demonstrated gap lives); the doctor check is WARN, and Slice 6's coverage
  audit expands the inventory before WARN→FAIL.
- **Risk:** presence-not-correctness — the diff proves a surface exists, not that
  it behaves equivalently. *Mitigation:* accepted under Q1 (behavioral
  equivalence remains a review concern) and the layered ramp.
- **Risk:** the new doctor check could mis-key a `.cmd` wrapper vs its `.py`
  target and produce a spurious finding. *Mitigation:* basename-normalized
  keying plus the registry surface-map resolution; the symmetric-fixture test
  asserts no false positive on a matched pair.
- **Risk:** the additive doctor check could perturb the doctor run. *Mitigation:*
  the check is fail-soft (WARN/info only), isolated, and guarded on missing
  config files; existing doctor checks are untouched.
- **Rollback:** revert the three files and remove the check registration; the
  Slice-1/Slice-2 foundation is untouched. The DCL `--assertions-json` encoding,
  if already applied, is reverted by a new `gt spec update` version restoring the
  prior (description-only) assertion state, leaving append-only DB history intact.
