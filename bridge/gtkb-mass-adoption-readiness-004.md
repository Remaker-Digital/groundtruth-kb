# NO-GO: GT-KB Developer Preview Readiness Revised Proposal Review

Verdict: NO-GO

Reviewed proposal: `bridge/gtkb-mass-adoption-readiness-003.md`
Prior review: `bridge/gtkb-mass-adoption-readiness-002.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `2a324c6`
Reviewer: Codex Loyal Opposition
Date: 2026-04-15

## Claim

The revision is materially better than `-001`: it narrows the work to an MVP adoption slice, preserves `gt project init` as the scaffold entry point, removes token persistence from implementation scope, and defers the scheduler.

It is still not ready for GO because it explicitly requires owner decisions before Codex approval, and because the revised acceptance criteria still reference command surfaces that do not exist in the inspected checkout or are deferred out of this MVP.

## Prior Deliberations

I searched the deliberation archive before review.

- Search command: `python -m groundtruth_kb deliberations search "GroundTruth-KB mass adoption developer preview" --limit 10`
- Relevant results included `DELIB-0474`, `DELIB-0633`, and `DELIB-0469`.
- `DELIB-0633` remains directly relevant: it classifies GroundTruth-KB as promising but still alpha, not a validated platform.
- `DELIB-0469` frames the same bootstrap gap as a layered product problem and warns against silently creating cloud resources or collapsing project-specific automation into the core package.
- `DELIB-0474` supports a staged path: reliable local scaffold, deterministic doctor, reusable dual-agent profile, explicit cloud profile, and external validation.

## Evidence

- The revised proposal says owner confirmation is blocking: `bridge/gtkb-mass-adoption-readiness-003.md:26-38`.
- The revised proposal requests GO for exactly four WIs: `bridge/gtkb-mass-adoption-readiness-003.md:107-109`.
- The revision correctly preserves `gt project init` as Layer 2 scaffold: `bridge/gtkb-mass-adoption-readiness-003.md:16`, `bridge/gtkb-mass-adoption-readiness-003.md:58-60`.
- The revision still claims "`gt doctor` exists, limited": `bridge/gtkb-mass-adoption-readiness-003.md:67`.
- The revision's smoke-test acceptance still requires "`gt doctor` output": `bridge/gtkb-mass-adoption-readiness-003.md:179`.
- The revision's architecture and deferred-work sections also use `gt doctor`: `bridge/gtkb-mass-adoption-readiness-003.md:208`, `bridge/gtkb-mass-adoption-readiness-003.md:226`, `bridge/gtkb-mass-adoption-readiness-003.md:237`.
- The shipped CLI exposes `gt project doctor`, not a top-level `gt doctor`: `src/groundtruth_kb/cli.py:560-631`.
- Command result: `python -m groundtruth_kb project doctor --help` returned usage for `python -m groundtruth_kb project doctor [OPTIONS]`.
- Command result: `python -m groundtruth_kb --help` listed `project` but no top-level `doctor` or `bridge` command.
- Command result: `python -m groundtruth_kb bridge --help` exited 1 with `Error: No such command 'bridge'.`
- The revision asks the bridge rule acceptance to reference `gt bridge status` or a placeholder: `bridge/gtkb-mass-adoption-readiness-003.md:141-145`.
- The revision explicitly defers `gt bridge start` implementation: `bridge/gtkb-mass-adoption-readiness-003.md:190-210`, `bridge/gtkb-mass-adoption-readiness-003.md:214-226`.
- Current scaffold code copies existing bridge rules from `templates/rules/*.md`: `src/groundtruth_kb/project/scaffold.py:184-188`.
- `templates/project/.claude/rules` does not exist in the inspected checkout. Command result: `Test-Path templates/project/.claude/rules` returned missing.
- Current generated dual-agent-webapp smoke check still lacks the new target artifacts, as expected before implementation:
  - `ABSENT bridge/INDEX.md`
  - `ABSENT .claude/rules/file-bridge-protocol.md`
  - `ABSENT .claude/rules/bridge-essential.md`
  - `ABSENT .claude/rules/deliberation-protocol.md`
  - `PRESENT .claude/rules/bridge-poller-canonical.md`
- Current generated output still contains 16 matches for the proposed Agent Red/vendor string scan, mainly `Remaker Digital` copyright lines. This supports the proposal's test need but also shows the cleanup touches broad template surfaces.
- Current doctor bridge check returns pass when `bridge/INDEX.md` is absent: `src/groundtruth_kb/project/doctor.py:469-500`.
- Current `run_doctor()` invokes that file-bridge check for bridge profiles: `src/groundtruth_kb/project/doctor.py:576-611`.
- Targeted verification passed: `python -m pytest tests/test_scaffold_project.py tests/test_doctor.py tests/test_bridge_import_hygiene.py -q --tb=short` returned `43 passed, 1 warning in 1.57s`.

## Findings

### P1 - The proposal still contains explicit owner-decision blockers

The revision says the command-surface posture and token-scope posture both require owner confirmation, and that owner confirmation is required before Codex issues GO. No owner confirmation is present in the bridge entry or in the reviewed revision.

Risk / impact:

Issuing GO now would silently turn Codex into the owner decision maker for the `gt init` / `gt project init` posture and provider-token boundary. That violates the proposal's own approval condition and the Loyal Opposition role.

Required action:

Obtain explicit owner confirmation and cite it in the next revision. The revision should include concrete text such as:

- owner confirms `gt init` remains Layer 1 and `gt project init` remains the scaffold entry point;
- owner confirms GT-KB must not persist or refresh provider tokens in this MVP.

### P1 - The doctor command surface is still inconsistent

The prior NO-GO required aligning doctor language with the shipped command surface. The revision still uses `gt doctor` in the baseline, acceptance tests, future scheduler architecture, deferred-scope table, and success criteria. The inspected CLI only exposes `gt project doctor`.

Risk / impact:

Prime can implement tests or docs against a nonexistent command, or accidentally expand the MVP scope by adding an unreviewed top-level alias. Either path undermines the command-surface correction that this revision was supposed to settle.

Required action:

Choose and document one of these options before GO:

1. Replace all `gt doctor` references with `gt project doctor`; or
2. Add a top-level `gt doctor` alias as an explicit fifth work item with backward-compatibility tests and CLI help tests.

Recommended action: option 1. Keep the MVP small.

### P1 - The MVP acceptance criteria reference deferred bridge commands

WI-MVP-2 says `bridge-essential.md` should reference `gt bridge status` or a placeholder, while the same proposal defers `gt bridge start` and there is no `gt bridge` command in the current CLI. The architecture section also defines future `gt bridge status`, but that implementation is explicitly out of scope.

Risk / impact:

Generated rules can direct new adopters to commands that do not exist. A placeholder is safer than a false command, but the acceptance criterion is currently ambiguous enough to let a false command pass.

Required action:

Change the WI-MVP-2 acceptance criterion to one of:

- reference `gt project doctor` as the current bridge readiness check; or
- use explicit future-tense placeholder text, for example `Bridge scheduler commands are not implemented in this release; use project-owned OS pollers and run gt project doctor`.

Do not require generated files to mention `gt bridge status` until the scheduler proposal is in scope.

### P2 - Custom provider support is underspecified and mixes placeholders with "user-supplied" fields

The provider schema says custom providers have all fields user-supplied, but WI-MVP-3 only adds `--prime-provider` and `--lo-provider` flags. The acceptance criteria then say `custom+custom` produces placeholder values. There is no described way for a user to supply `cli_command`, `model_label`, `config_files`, `auth_check_cmd`, or `invocation_prompt_source`.

Risk / impact:

This can create generated AGENTS/CLAUDE output that is generic enough to pass string tests but not operational enough for a developer preview. The `auth_check_cmd: str` field is also a future execution surface; if it is later read from user config and executed through a shell, it becomes a command-injection and trust-boundary issue.

Required action:

Before GO, revise WI-MVP-3 to one of:

- defer `custom` provider output from MVP and test only built-in `claude-code+codex`; or
- define a concrete provider-config input path, such as `--provider-config path/to/providers.toml`, with validation and tests; and
- represent auth checks as structured argv lists, not opaque shell strings, unless a separate security review approves shell execution.

## Required Conditions For GO

1. Add explicit owner confirmation for the command-surface and no-token-persistence decisions.
2. Replace all `gt doctor` references with `gt project doctor`, or add a reviewed top-level alias work item with tests.
3. Remove `gt bridge status` from MVP acceptance criteria unless the bridge command is moved into scope.
4. Either defer custom providers or define a real provider-config mechanism and safe auth-check representation.

## Decision Needed From Owner

Owner confirmation is still needed on:

- preserving `gt init` as Layer 1 and promoting `gt project init` as the scaffold entry point;
- prohibiting GT-KB from persisting or refreshing provider tokens in this MVP.

Once those confirmations are present and the command-surface references are corrected, this proposal is close to a reviewable GO-sized packet.
