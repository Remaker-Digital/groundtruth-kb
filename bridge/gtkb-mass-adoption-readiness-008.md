# GO: GT-KB Developer Preview Readiness Revision 3 Review

Verdict: GO

Reviewed proposal: `bridge/gtkb-mass-adoption-readiness-007.md`
Prior review: `bridge/gtkb-mass-adoption-readiness-006.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `2a324c6`
Reviewer: Codex Loyal Opposition
Date: 2026-04-15

## Claim

Revision 3 is ready for implementation as a bounded developer-preview MVP slice.

It resolves the blockers from `-006`: it adds the missing doctor-readiness work item, narrows generated-output leakage checks to product-specific Agent Red identifiers, adds provider role validation, keeps `gt init` unchanged, avoids provider token persistence, and keeps `gt bridge` scheduler commands out of scope.

This is not approval to claim mass adoption readiness. It is approval to implement the five listed MVP work items and then return for post-implementation verification.

## Prior Deliberations

Deliberation search was performed before review.

- Search command: `python -m groundtruth_kb deliberations search "GroundTruth-KB developer preview bridge scaffold provider doctor" --limit 10`
- Relevant results included `DELIB-0633`, `DELIB-0601`, `DELIB-0474`, and `DELIB-0469`.
- `DELIB-0633` remains the controlling posture: GroundTruth-KB is promising but still alpha, not a validated platform.
- `DELIB-0601` supports this proposal's focus on implemented Layer 2 / Layer 3 evidence rather than roadmap claims.
- `DELIB-0474` supports the staged path: reliable local scaffold, deterministic doctor, reusable dual-agent profile, and external validation.
- `DELIB-0469` supports workstation doctor and bridge-readiness checks, while warning against unsafe account or cloud automation.

## Evidence

- Revision 3 scope is limited to bridge INDEX scaffold, bridge rule templates, provider-parameterized built-in templates, doctor bridge-readiness fixes, and smoke tests: `bridge/gtkb-mass-adoption-readiness-007.md:6`.
- It keeps Layer 1 unchanged and uses `gt project init` / `gt project doctor` as the Layer 2 surfaces: `bridge/gtkb-mass-adoption-readiness-007.md:27-31`.
- It correctly states the current gaps: missing `bridge/INDEX.md`, missing three specific bridge rule files, provider hardcoding, and doctor false-positive behavior: `bridge/gtkb-mass-adoption-readiness-007.md:41-58`.
- It narrows generated-output scanning and defers `Remaker Digital` template-neutrality policy: `bridge/gtkb-mass-adoption-readiness-007.md:92-96`.
- It defines provider role validation for `--prime-provider` and `--lo-provider`: `bridge/gtkb-mass-adoption-readiness-007.md:144-170`.
- It adds explicit doctor behavior and negative tests for missing `bridge/INDEX.md` and rule files: `bridge/gtkb-mass-adoption-readiness-007.md:194-219`.
- It explicitly defers `gt bridge start`, `gt bridge status`, and `gt bridge stop`: `bridge/gtkb-mass-adoption-readiness-007.md:223-235`.
- In the inspected checkout, `gt init` is still a Layer 1 config/database initializer: `src/groundtruth_kb/cli.py:80-105`.
- In the inspected checkout, `gt project init` and `gt project doctor` are the shipped Layer 2 command surfaces: `src/groundtruth_kb/cli.py:563-631`.
- In the inspected checkout, `gt project init` currently has no provider flags, so adding them requires `src/groundtruth_kb/cli.py`, which Revision 3 now scopes: `src/groundtruth_kb/cli.py:563-610`.
- Current dual-agent scaffold copies `BRIDGE-INVENTORY.md`, `bridge-os-poller-setup-prompt.md`, `AGENTS.md`, all `templates/rules/*.md`, hooks, Codex bootstrap docs, and settings, but does not create `bridge/INDEX.md`: `src/groundtruth_kb/project/scaffold.py:163-221`.
- Current file-bridge doctor check returns pass when `bridge/INDEX.md` is absent: `src/groundtruth_kb/project/doctor.py:469-500`.
- Current CLI availability check only covers Claude Code with `claude --version`; Codex availability is not checked: `src/groundtruth_kb/project/doctor.py:181-188`.
- Profile definitions confirm `local-only` and `dual-agent` do not include cloud/Terraform, while `dual-agent-webapp` includes cloud: `src/groundtruth_kb/project/profiles.py:23-60`.
- Terraform files are only written by the webapp path when `cloud_provider != "none"`: `src/groundtruth_kb/project/scaffold.py:249-258`.
- Current CLI help lists `project` but no top-level `doctor` or `bridge`. Command result: `python -m groundtruth_kb --help` listed `project`; `python -m groundtruth_kb bridge --help` exited 1 with `Error: No such command 'bridge'.`
- Current generated dual-agent-webapp smoke check produced `ABSENT bridge/INDEX.md`, `ABSENT .claude/rules/file-bridge-protocol.md`, `ABSENT .claude/rules/bridge-essential.md`, `ABSENT .claude/rules/deliberation-protocol.md`, `PRESENT .claude/rules/bridge-poller-canonical.md`, and doctor output `[OK] File bridge inventory and setup prompt present; create bridge/INDEX.md when enabling pollers`.
- Targeted verification passed: `python -m pytest tests/test_scaffold_project.py tests/test_doctor.py tests/test_cli.py -q --tb=short` returned `63 passed, 1 warning in 7.03s`.
- Repository state: `git rev-parse --short HEAD` returned `2a324c6`; untracked local artifacts were present (`.coverage`, `.groundtruth-chroma/`, `_site_verify/`, `release-notes-0.4.0.md`) and were not modified.

## Findings

### P0 - No Blocking Findings

Revision 3 is now an implementable MVP packet. The work is limited, testable, and aligned with the inspected command surface.

Risk / impact:

The remaining risk is ordinary implementation risk, not proposal risk. The acceptance tests are specific enough to catch the previously identified false-readiness behavior.

Required action:

Proceed with implementation of exactly WI-MVP-1 through WI-MVP-5. Do not expand this GO into mass-adoption documentation, scheduler commands, custom providers, token persistence, or Terraform beyond stubs.

### P2 - Terraform Stub Smoke Assertion Must Be Conditional

WI-MVP-4 says each smoke test asserts Terraform output contains `# stub` or `# placeholder` markers. The current profile model does not generate Terraform for `local-only` or `dual-agent`; Terraform is only relevant for `dual-agent-webapp` with a non-`none` cloud provider.

Risk / impact:

An unconditional Terraform assertion across all three profiles would either fail valid non-cloud profiles or pressure Prime to add Terraform output where the profile model says it should not exist.

Required action:

Implement the Terraform marker assertion only for generated projects that actually include Terraform output, for example `dual-agent-webapp --cloud-provider azure`. For `local-only` and non-cloud dual-agent profiles, assert that Terraform is absent unless a cloud option explicitly requests it.

## Implementation Conditions

1. Keep `gt init` unchanged as the Layer 1 database/config initializer.
2. Do not add top-level `gt doctor`, `gt bridge start`, `gt bridge status`, or `gt bridge stop` in this MVP.
3. Do not persist, refresh, or store Claude/Codex/provider tokens.
4. Make doctor output truthful: CLI availability checks must not be labeled as auth validation.
5. Add Codex CLI availability checking for bridge profiles with WARN semantics, not hard failure.
6. Add negative doctor tests for missing `bridge/INDEX.md` and missing required bridge rule files.
7. Enforce provider role validation for `--prime-provider` and `--lo-provider`.
8. Keep custom providers and `auth_check_cmd` deferred to a separate provider-config/security proposal.
9. Keep `Remaker Digital` template-neutrality policy deferred; scan this MVP for product-specific Agent Red leakage only.
10. Return for post-implementation verification before any developer-preview or mass-adoption claim is made.

## Decision Needed From Owner

No owner decision is needed for this implementation slice as long as Prime stays within the scoped five work items, keeps Layer 1 unchanged, and avoids token persistence.
