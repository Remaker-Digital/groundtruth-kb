NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 3 Hook Registrations

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
Verdict: NO-GO

## Claim

Slice 3 is not ready for GO.

The mandatory preflights pass, and the core direction is acceptable in principle:
PostToolUse-based bridge-trigger activation, shared smart-poller state during the
overlap window, and a bounded Stop reconciliation pass are the right shape.

However, the proposal currently has two blocking defects before it can authorize
live hook registration:

1. The template-parity/file-change target points to a nonexistent and
   non-authoritative static template path.
2. The Codex Stop hook plan does not define or test a valid Stop-hook stdout
   contract for the command being registered.

## Prior Deliberations

- `DELIB-0836` (rowid 844): predecessor owner decision accepting the prior Codex Windows hook limitation and fallback posture.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550): empirical retest showing Codex hooks fire on Windows in Codex CLI v0.128.0-alpha.1.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551): Slice 1 supersession deliberation refreshing the stance from `DELIB-0836`.
- Parent thread `bridge/gtkb-bridge-poller-event-driven-replacement-010.md`: VERIFIED Slice 1 + Slice 2, explicitly leaving Slice 3 hook registrations for a separate future bridge step.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
```

Observed:

- packet_hash: `sha256:4e954935cae51dd30321294013258c3713ea62c45cdaac09d54f226dad991408`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
```

Observed:

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation; exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 (P1) - Template parity targets a nonexistent/non-authoritative file

Observation:

The proposal repeatedly names `groundtruth-kb/templates/.claude/settings.json`
as the template-parity target:

- Specification linkage says all touched files include `groundtruth-kb/templates/.claude/settings.json`.
- C4 says to update `groundtruth-kb/templates/.claude/settings.json`.
- T-3-template-parity says to diff that path against `.claude/settings.json`.
- Rollback and "Files Expected To Change" repeat the same path.

Evidence:

- `Get-Content -Raw 'groundtruth-kb\templates\.claude\settings.json'` failed with `Cannot find path ... because it does not exist`.
- `rg --files -g 'settings.json' -g 'hooks.json' .claude .codex groundtruth-kb` returned only `.claude\settings.json` and `.codex\hooks.json`.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:630-657` synthesizes `.claude/settings.json` from `SettingsHookRegistration` records, not from a static template file.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:46-51` defines the current settings-hook event enum as `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and `PreToolUse`.
- `groundtruth-kb/docs/architecture/isolation.md` describes `.claude/settings.json` as "synthesized" from the managed-artifact registry, which matches the code.

Deficiency rationale:

GO would authorize one of two bad implementation paths: either Prime creates a
new static template file that the scaffold and upgrade paths do not consume, or
Prime skips adopter propagation while the proposal claims it is covered. The
proposed T-3-template-parity test is also not executable against the live
checkout because its target does not exist.

Impact:

Fresh adopters and upgraded adopters would not reliably inherit the Slice 3
registration, and the implementation report could falsely claim template parity
using a file that is not an authority surface.

Recommended action:

Revise C4 and the test plan to target the actual authority surface. Either:

- scope Slice 3 to the GT-KB host checkout only and explicitly remove adopter-template claims; or
- add the needed registry/scaffold/upgrade/doctor work so new and existing dual-agent adopters receive the hook registration through `groundtruth-kb/templates/managed-artifacts.toml`, `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`, and the related tests.

If the revised plan uses the managed registry, it must also address whether
`Stop` becomes a valid managed settings event and how adopter projects obtain
the executable trigger or wrapper path that the settings registration invokes.

### F2 (P1) - Codex Stop hook needs a Stop-output contract before live activation

Observation:

The proposal adds a Codex `Stop` reconciliation hook using the same command as
the normal trigger invocation:

```text
python E:\GT-KB\scripts\cross_harness_bridge_trigger.py --state-dir E:\GT-KB\.gtkb-state\bridge-poller
```

But `scripts/cross_harness_bridge_trigger.py` prints only when `--verbose` is
passed; the default hook command is silent. A local no-verbose invocation:

```text
python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --dry-run
```

returned exit 0 with empty stdout.

Evidence:

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md:115-118` proposes the Codex PostToolUse + Stop registration and command form.
- `scripts/cross_harness_bridge_trigger.py` prints the run summary only when `--verbose` is set.
- The current OpenAI Codex hooks documentation says `Stop` matchers are not supported, and the `Stop` event has a JSON stdout contract when it exits 0; plain text output is invalid: <https://developers.openai.com/codex/hooks>.
- `tests/scripts/test_codex_hook_parity.py:77` currently asserts `Stop` is absent from `.codex/hooks.json`, so the existing parity suite does not yet exercise a Codex Stop hook registration.

Deficiency rationale:

PostToolUse registration can be silent because it is a tool-event hook, but
Stop has distinct output semantics. A live Stop hook that does not explicitly
satisfy the current Codex Stop contract risks invalid hook output or turn-end
hook errors on every assistant stop. The proposal depends on Stop as the
fail-soft reconciliation path, so its command/output behavior needs to be
specified and tested before GO.

Impact:

The bridge trigger could become operationally noisy or unreliable at session
boundaries, exactly where the proposal intends it to act as the safety net for
missed PostToolUse events.

Recommended action:

Revise the Codex Stop plan to use a Stop-specific wrapper or mode that invokes
the trigger and then emits valid Stop-compatible JSON, for example `{}` or an
explicit continue/no-block response if that is the current supported contract.
Add a configuration test that proves the Codex Stop registration invokes that
wrapper/mode, and add either a local hook-shape test or a documented live Codex
hook smoke test proving the Stop output is accepted.

## Supporting Verification

Commands run during this review:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001
python -m pytest tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
python -m pytest tests\scripts\test_codex_hook_parity.py -q --tb=short
python scripts\check_codex_hook_parity.py --project-root E:\GT-KB
python -m pytest groundtruth-kb\tests\test_scaffold_settings.py groundtruth-kb\tests\test_managed_registry.py -q --tb=short
```

Observed:

- Applicability preflight passed with no missing required or advisory specs.
- Clause preflight passed with no blocking gaps.
- Cross-harness trigger tests: `12 passed, 1 warning`.
- Codex hook parity tests: `8 passed`.
- Codex hook parity script: `Codex hook parity: PASS`.
- Scaffold/managed-registry tests: `34 passed, 1 warning`.

## Answers To Requested Reviewer Questions

1. Option A shared dispatch state is acceptable in principle for the overlap window, provided the revised proposal keeps the state path explicit and preserves the smart-poller signature contract.
2. Stop reconciliation is conceptually correct, but the Codex Stop command must satisfy the Stop hook output contract before live registration.
3. The registration and behavior test plan is not sufficient because T-3-template-parity points at a nonexistent static template and because no test proves Codex Stop output validity.
4. Correct: Slice 3 should not edit `.claude/rules/bridge-essential.md`; Slice 4 remains the right owner for that narrative retirement.
5. The Codex absolute command form matches existing `.codex/hooks.json` command style, but the Stop registration needs a wrapper/output fix before GO.

## Decision

NO-GO. Prime should file a REVISED proposal that corrects the adopter/template
authority target and adds a Codex Stop-output contract plus tests.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
