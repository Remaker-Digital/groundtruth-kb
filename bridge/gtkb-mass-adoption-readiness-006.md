# NO-GO: GT-KB Developer Preview Readiness Revision 2 Review

Verdict: NO-GO

Reviewed proposal: `bridge/gtkb-mass-adoption-readiness-005.md`
Prior review: `bridge/gtkb-mass-adoption-readiness-004.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `2a324c6`
Reviewer: Codex Loyal Opposition
Date: 2026-04-15

## Claim

Revision 2 is close to a GO-sized implementation packet. It resolves the previous blockers around `gt doctor`, `gt bridge status`, custom providers, and token persistence in the proposal text.

It is still not ready for GO because the revised acceptance path depends on `gt project doctor` as a bridge-readiness verifier while the proposal does not include the required doctor change and the current doctor still false-positives when `bridge/INDEX.md` is absent. Two smaller issues also need correction: the generated-output string scan is broader than the implementation scope, and provider role validation is not specified.

## Prior Deliberations

I searched the deliberation archive before review.

- Search command: `python -m groundtruth_kb deliberations search "GroundTruth-KB developer preview mass adoption bridge scaffold provider templates" --limit 10`
- Relevant results included `DELIB-0469`, `DELIB-0474`, `DELIB-0601`, and `DELIB-0633`.
- `DELIB-0469` frames the bootstrap gap as a layered product problem and says workstation doctor should verify expected folders, hooks, automation files, and local auth presence where possible.
- `DELIB-0474` supports a staged path with a reliable local scaffold, deterministic workstation doctor, reusable dual-agent webapp profile, and external validation.
- `DELIB-0601` is directly relevant to Layer 2 / Layer 3 completeness and the need for implemented `gt project init`, `gt project doctor`, and profile evidence rather than roadmap claims.
- `DELIB-0633` remains relevant to product posture: GroundTruth-KB is still alpha/developer-preview territory, not validated mass adoption.

## Evidence

- The revision keeps `gt init` as Layer 1 and `gt project init` as Layer 2: `bridge/gtkb-mass-adoption-readiness-005.md:24-30`.
- The revision says `gt project doctor` validates external CLI auth state: `bridge/gtkb-mass-adoption-readiness-005.md:30`.
- The verified baseline acknowledges that the current bridge file check passes when `bridge/INDEX.md` is absent: `bridge/gtkb-mass-adoption-readiness-005.md:55`.
- WI-MVP-2 instructs generated `bridge-essential.md` to tell developers to configure OS-level bridge scanning and run `gt project doctor` to verify bridge readiness: `bridge/gtkb-mass-adoption-readiness-005.md:124-127`.
- WI-MVP-4 only requires that `gt project doctor` "does not error" on the generated project structure: `bridge/gtkb-mass-adoption-readiness-005.md:168`.
- Success criteria require `gt project doctor` to report bridge configuration status accurately: `bridge/gtkb-mass-adoption-readiness-005.md:210`.
- The deferred-scope table defers `gt project doctor` expansion beyond bridge/auth status checks: `bridge/gtkb-mass-adoption-readiness-005.md:199`.
- Current CLI exposes `gt project init` and `gt project doctor`, with no top-level `bridge` command: `src/groundtruth_kb/cli.py:563-631`. Command result: `python -m groundtruth_kb bridge --help` exited 1 with `Error: No such command 'bridge'.`
- Current `gt project doctor` checks Claude Code only with `claude --version`: `src/groundtruth_kb/project/doctor.py:181-188`.
- Current doctor checks GitHub CLI auth, not Claude or Codex auth: `src/groundtruth_kb/project/doctor.py:201-214`.
- Current file-bridge doctor check returns pass when `BRIDGE-INVENTORY.md` and `bridge-os-poller-setup-prompt.md` exist but `bridge/INDEX.md` does not: `src/groundtruth_kb/project/doctor.py:469-500`.
- Current `run_doctor()` invokes the file-bridge check for bridge profiles: `src/groundtruth_kb/project/doctor.py:576-611`.
- Current scaffold copies dual-agent templates and rules but does not create `bridge/INDEX.md`: `src/groundtruth_kb/project/scaffold.py:75-94`, `src/groundtruth_kb/project/scaffold.py:163-188`.
- Current generated dual-agent-webapp smoke check produced:
  - `ABSENT bridge/INDEX.md`
  - `ABSENT .claude/rules/file-bridge-protocol.md`
  - `ABSENT .claude/rules/bridge-essential.md`
  - `ABSENT .claude/rules/deliberation-protocol.md`
  - `PRESENT .claude/rules/bridge-poller-canonical.md`
  - doctor output: `[OK] File bridge inventory and setup prompt present; create bridge/INDEX.md when enabling pollers`
- Current `templates/project/AGENTS.md` hardcodes Codex and Claude Code role language: `templates/project/AGENTS.md:3-5`, `templates/project/AGENTS.md:23-29`.
- Current generated dual-agent-webapp output still matches the proposed string scan across broad generated surfaces, including `Remaker Digital` in `templates/project/Dockerfile:4`, `templates/project/docker-compose.yml:8`, and `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md:62`.
- Targeted verification passed: `python -m pytest tests/test_scaffold_project.py tests/test_doctor.py tests/test_cli.py -q --tb=short` returned `63 passed, 1 warning in 6.27s`.
- Repository state: `git rev-parse --short HEAD` returned `2a324c6`; untracked local artifacts were present (`.coverage`, `.groundtruth-chroma/`, `_site_verify/`, `release-notes-0.4.0.md`) and were not modified.

## Findings

### P1 - `gt project doctor` is still not a reliable bridge-readiness verifier

The revision now routes adopters to `gt project doctor` instead of nonexistent `gt bridge` commands, which is the right command surface. But the proposal does not include the doctor behavior needed to make that instruction true.

Current doctor behavior is not accurate enough for the proposed developer-preview flow:

- It returns pass for file-bridge setup when `bridge/INDEX.md` is absent.
- It checks Claude Code availability with `claude --version`, not Claude auth state.
- It does not check Codex availability or auth despite `codex` being the built-in Loyal Opposition provider.
- WI-MVP-4 only asserts doctor "does not error", which would allow the current false-positive behavior to pass.

Risk / impact:

Generated `bridge-essential.md` would tell a new adopter to run a readiness check that cannot actually verify the bridge is ready. That recreates the false-readiness problem this proposal is supposed to close: generated files look operational while critical bridge prerequisites are still missing or unverified.

Required action:

Add an explicit MVP doctor work item, or remove doctor-readiness claims from the MVP. If doctor remains part of the flow, the next revision must require:

1. `gt project doctor` warns or fails for bridge profiles when `bridge/INDEX.md` is missing.
2. `gt project doctor` warns or fails when the three required bridge rule files are missing.
3. Doctor output distinguishes CLI availability from auth validation. If provider auth validation is claimed, implement safe built-in checks for the `claude-code` and `codex` providers, without token storage.
4. Smoke tests include negative cases: delete `bridge/INDEX.md` and one required rule file from a generated bridge profile and assert doctor no longer reports bridge readiness as pass.

### P1 - Generated-output neutrality is broader than the scoped implementation

WI-MVP-4 requires a case-insensitive search across every generated file for `"Agent Red"`, `"Remaker Digital"`, `"ACS"`, and `"azure-communication"`. Current generated output contains `Remaker Digital` in multiple generated files outside the specific WI-MVP-1 through WI-MVP-3 edit surfaces, including Docker, compose, and Codex bootstrap templates.

Risk / impact:

Prime can implement the named bridge-index, bridge-rule, and provider-template work and still fail the smoke test because unrelated generated templates retain vendor copyright text. The opposite failure mode is also risky: Prime may strip legal/vendor text across broad template surfaces without a reviewed ownership/copyright policy for generated adopter projects.

Required action:

Choose one explicit policy before GO:

1. Add a generated-template neutrality work item that lists every affected template category and defines how copyright/owner text should be rendered for adopter projects; or
2. Narrow the smoke-test scan to product-specific leakage only (`Agent Red`, `ACS`, `azure-communication`, hardcoded repo paths) and handle `Remaker Digital` through a separate legal/template ownership proposal.

Either path is acceptable. The current proposal mixes a broad global smoke assertion with a narrower implementation scope.

### P2 - Provider flags need role validation and CLI scope

The proposal defines two built-in providers with `bridge_role` values, then adds `--prime-provider` and `--lo-provider` flags. It says only `claude-code` and `codex` are valid in this MVP, and tests only the happy path plus `--prime-provider custom`.

That leaves an important invalid-but-individually-valid case unspecified: `--prime-provider codex` or `--lo-provider claude-code`.

Risk / impact:

If provider ids are validated only as a set of allowed strings, the scaffold can generate inverted or internally inconsistent operating contracts. Agent instructions are an operational control surface; role/provider mismatch should fail clearly rather than produce plausible-looking but wrong instructions.

Required action:

Revise WI-MVP-3 to require role validation:

- `--prime-provider` must resolve to a provider whose `bridge_role == "prime"`.
- `--lo-provider` must resolve to a provider whose `bridge_role == "loyal-opposition"`.
- `--prime-provider codex` and `--lo-provider claude-code` must fail with clear Click-facing errors.
- Add `src/groundtruth_kb/cli.py` to the WI-MVP-3 scope because new CLI options are required there.

## Non-Blocking Corrections

- `bridge/gtkb-mass-adoption-readiness-005.md:7` says current main is `cea14c4` per MEMORY.md, but the inspected checkout is currently `2a324c6`.
- The baseline row for `.claude/rules/` says generation is absent, but current scaffold does generate `.claude/rules/` with existing rule files. The accurate gap is that the three newly required rule files are absent.

## Required Conditions For GO

1. Add an explicit doctor-readiness work item and negative tests, or remove doctor-readiness claims/instructions from the MVP.
2. Resolve the generated-output string-scan policy so the implementation scope matches the smoke test.
3. Add provider role validation and tests for role/provider mismatch; include `src/groundtruth_kb/cli.py` in scope.
4. Correct the minor baseline inaccuracies noted above.

No owner decision is required if the next revision continues to avoid Layer 1 changes and provider-token persistence.
