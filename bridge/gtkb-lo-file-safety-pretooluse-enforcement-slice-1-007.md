NEW
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Post-Implementation Report - LO File-Safety PreToolUse Enforcement Slice 1

bridge_kind: prime_builder_post_implementation_report
Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1
Version: 007
Author: Prime Builder (Codex harness A)
Date: 2026-05-20 UTC
Implements: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-006.md`

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: WI-3308

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation followed the live latest `GO` bridge state and this report advances the bridge lifecycle through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps the approved behavior and prior NO-GO findings to executed tests.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity is implemented through `.codex/hooks.json`, a `.cmd` wrapper, and the Python adapter.
- `GOV-ARTIFACT-APPROVAL-001` - the exceptional LO write path uses an owner approval packet with content-exact hash validation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all slice-scoped changed files are under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the rule-to-hook implementation, config, tests, and bridge report preserve traceability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the implementation converts a text-only LO safety rule into a durable mechanical control.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the hook lifecycle is now created, registered, and regression-tested.
- `GOV-STANDING-BACKLOG-001` - the work is a single WI-3308 implementation, not a bulk backlog operation.
- `.claude/rules/loyal-opposition.md` - the implemented behavior mechanizes the Loyal Opposition file-safety rule and its approval-packet exception.
- `.claude/rules/file-bridge-protocol.md` - the bridge exception preserves append-only verdict filing and canonical `bridge/INDEX.md` state.
- `.claude/rules/codex-review-gate.md` - implementation-start authorization was obtained before the protected implementation edits.
- `.claude/rules/project-root-boundary.md` - all live GT-KB artifacts remain within the project root.

## Claim

Slice 1 is implemented. The new `lo-file-safety-gate.py` resolves the active harness role through `scripts.harness_roles`, fails open when role projection is absent, passes Prime Builder sessions, and enforces only for a resolved Loyal Opposition harness without Prime authority.

For LO-only sessions, the gate allows the approved additive/reporting surfaces, blocks non-allow-listed writes, accepts exceptional `Write|Edit|MultiEdit` changes only when `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET` points to a valid `lo_file_safety_authorization` packet whose `full_content` exactly matches the proposed post-edit content, and rejects approval-packet bypass for Bash writes.

The bridge carve-outs are narrowed to the approved operations: creating a new versioned bridge verdict/report file whose first line is `GO`, `NO-GO`, `VERIFIED`, or `ADVISORY`, and editing `bridge/INDEX.md` only when the reconstructed candidate inserts exactly one matching LO status line at the top of the relevant document entry. Existing bridge files, full `bridge/INDEX.md` writes, deletions, reorders, Prime status insertions, unrelated-entry edits, and multi-line insertions block.

The Codex parity wrapper is registered for both `Bash` and `apply_patch`. The canonical hook also understands Codex `apply_patch` payloads directly so the adapter can pass the original payload through while setting the Codex harness identity.

## Slice-Scoped Changed Files

- `.claude/hooks/lo-file-safety-gate.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `config/governance/lo-file-safety.toml`
- `.claude/settings.json`
- `.codex/hooks.json`
- `platform_tests/scripts/test_lo_file_safety_gate.py`

Scope note: `.claude/settings.json` and `.codex/hooks.json` already contained unrelated dirty hunks before this slice. This implementation only adds the LO file-safety registration groups and leaves the pre-existing hunks intact.

## Implementation Notes

- Added a canonical Claude hook with importable `gate_decision(payload)` plus `--self-test`.
- Added TOML-driven allow-list patterns for:
  - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**`
  - `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md`
  - `independent-progress-assessments/KNOWLEDGE-PROJECT.md`
  - `memory/MEMORY.md`
- Added post-edit reconstruction for `Edit`, `MultiEdit`, and simple `apply_patch` operations.
- Added the Bash write-intent classifier for shell redirects, heredoc writes, PowerShell write/delete/move/copy commands, POSIX copy/move/delete commands, `git restore`, `git checkout --`, and risky opaque command substitutions.
- Added the append-only `bridge/INDEX.md` classifier required by the `-004` NO-GO.
- Registered Claude `Write|Edit|MultiEdit|Bash` and Codex `Bash|apply_patch` PreToolUse hooks.
- Added exactly 44 focused platform tests covering role resolution, allow-list behavior, approval packets, shell classifiers, bridge exceptions, Codex adapter behavior, and hook registration.

## Specification-Derived Verification

| Spec / requirement | Verification evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge state governs implementation | `python scripts\implementation_authorization.py begin --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` succeeded from latest `GO`; packet hash `sha256:5b4ec70c42b7b42434f35a826fa8bdbff2e1ec741d65dacf7867fb0a9fe00cd0`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation/report carry linked specs | This report carries forward the approved proposal's governing specs and includes project metadata for WI-3308. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived tests executed | `platform_tests/scripts/test_lo_file_safety_gate.py` collected and passed exactly 44 tests, including cases mapped to both prior NO-GO findings. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex parity | Tests assert `.codex/hooks.json` registers `lo-file-safety-gate.cmd` for both `Bash` and `apply_patch`, and subprocess-test the adapter blocking a Codex Bash source write under LO-only role projection. |
| `GOV-ARTIFACT-APPROVAL-001` - owner approval packet exception | Tests validate correct packet acceptance and block mismatched content, target, artifact type, missing fields, and Bash packet bypass attempts. |
| `.claude/rules/loyal-opposition.md` - LO file-safety rule | LO-only tests block source writes, deletes, moves, copies, redirects, restore/checkout operations, and unresolved substitution writes outside the allow-list. Prime Builder and missing-role fail-open cases pass. |
| `.claude/rules/file-bridge-protocol.md` - append-only bridge safety | Tests allow only new LO verdict/report bridge file creation and one exact LO status-line insertion into `bridge/INDEX.md`; tests block full INDEX writes, deletion, two-line insertion, wrong-document insertion, existing bridge overwrite, and existing bridge edit. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement | All slice-scoped target files are in-root under `E:\GT-KB`; `git diff --check` over the target files exited 0. |
| `GOV-STANDING-BACKLOG-001` - no bulk backlog operation | No backlog or MemBase mutation was performed by this implementation. |

## Verification Commands

Authorization:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed: latest bridge status `GO`; project authorization active; packet hash `sha256:5b4ec70c42b7b42434f35a826fa8bdbff2e1ec741d65dacf7867fb0a9fe00cd0`.

Focused acceptance tests:

```text
python -m pytest platform_tests\scripts\test_lo_file_safety_gate.py -v
```

Observed: `44 passed in 0.77s`.

Hook self-test:

```text
python .claude\hooks\lo-file-safety-gate.py --self-test
```

Observed stdout: `{}`.

Ruff check:

```text
python -m ruff check .claude\hooks\lo-file-safety-gate.py .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py platform_tests\scripts\test_lo_file_safety_gate.py
```

Observed: `All checks passed!`. Ruff emitted a non-blocking cache warning about a different package root.

Ruff format:

```text
python -m ruff format --check .claude\hooks\lo-file-safety-gate.py .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py platform_tests\scripts\test_lo_file_safety_gate.py
```

Observed: `3 files already formatted`. Ruff emitted the same non-blocking cache warning.

JSON syntax:

```text
python -m json.tool .claude\settings.json > $null
python -m json.tool .codex\hooks.json > $null
```

Observed: both JSON files parse successfully (`json-ok`).

Diff whitespace:

```text
git diff --check -- .claude\hooks\lo-file-safety-gate.py .codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py .codex\gtkb-hooks\lo-file-safety-gate.cmd config\governance\lo-file-safety.toml .claude\settings.json .codex\hooks.json platform_tests\scripts\test_lo_file_safety_gate.py
```

Observed: exit 0; Git emitted only LF-to-CRLF working-copy warnings for `.claude/settings.json` and `.codex/hooks.json`.

Bridge preflights:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1 --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed: applicability `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:da89eaf1a96217cf668f9ccfcc21512c58dc88f645a363af727f56db3aa0da1e`; clause preflight exited 0 with zero blocking gaps.

Additional hook parity sweep:

```text
python -m pytest platform_tests\scripts\test_hook_registration_parity.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_codex_bridge_compliance_gate.py -q
```

Observed: `19 passed`, `1 failed`. The failure is pre-existing and out of scope for WI-3308: `platform_tests/scripts/test_hook_registration_parity.py::test_claude_registers_implementation_start_gate_on_mutation_surfaces` expects a Claude `implementation-start-gate.py` PreToolUse registration that is absent from the current baseline. The LO file-safety registration tests in the new suite pass.

## Residual Risk

The Bash write-intent classifier is intentionally conservative but still heuristic. The approved slice covers common and previously missed mutation forms; future false negatives should add classifier cases and focused tests rather than widening LO write authority.

The hook currently passes any harness record with Prime Builder authority before enforcing LO-only restrictions. That preserves the current single-harness Prime Builder workflow where Codex carries both durable roles, and the tests cover LO-only enforcement with synthetic role projection.

Existing unrelated dirty hunks remain in `.claude/settings.json` and `.codex/hooks.json`. They were not introduced or reverted by this implementation.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
