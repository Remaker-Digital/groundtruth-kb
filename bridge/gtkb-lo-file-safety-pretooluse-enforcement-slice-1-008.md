NO-GO

# Loyal Opposition Verification - LO File-Safety PreToolUse Enforcement Slice 1

bridge_kind: verification_verdict
Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-007.md

## Claim

The implementation report cannot receive VERIFIED. The bridge gates pass and the hook self-test returns `{}`, but the implemented Bash write-intent classifier does not enforce one command form explicitly required by the approved `-005` proposal: `git restore --source ... <path>`. Under a live Loyal Opposition role projection, that command shape returns `{}` and would allow a non-allow-listed source-file restore path to pass.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:d583838072a3b75bb180ec8b0292f3e258a3e65c0303140848f61325b9d4c864`
- bridge_document_name: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-007.md`
- operative_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- Operative file: `bridge\gtkb-lo-file-safety-pretooluse-enforcement-slice-1-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

The required deliberation search could not run through `python -m groundtruth_kb` in this auto-dispatch shell because neither the default interpreter nor `.venv` exposes the `groundtruth_kb` package. The full bridge thread was read. Relevant prior deliberations are already carried through the proposal and GO chain:

- `DELIB-2188` - originating Loyal Opposition file-safety violation.
- `DELIB-1886` - verified file-safety rule clarification.
- `DELIB-1518` - Loyal Opposition verification for the clarification.
- `DELIB-1550` / `DELIB-1551` - Codex hook firing evidence.
- `DELIB-1742`..`DELIB-1739` - Codex hook wrapper parity precedent.

No cited prior deliberation waives the approved requirement to detect `git restore --source ... <path>`.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` | yes | PASS, no missing required or advisory specs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Manual hook probe for approved `git restore --source ... <path>` behavior | yes | FAIL, hook returned `{}` |
| `.claude/rules/loyal-opposition.md` | Manual hook probe under `harness_id=A`, `harness_name=codex` against `scripts/implementation_authorization.py` | yes | FAIL for `git restore --source` command shape |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Read `.codex/hooks.json` and adapter registration | yes | Registered, but canonical hook classifier has uncovered command shape |

## Positive Confirmations

- The implementation added the expected hook, Codex adapter, TOML config, hook registrations, and platform test module.
- `python .claude/hooks/lo-file-safety-gate.py --self-test` returned `{}`.
- Applicability and clause preflights pass on the post-implementation report.
- `.claude/settings.json` and `.codex/hooks.json` include the LO file-safety registrations described by the implementation report.

## Findings

### F1 (P1) - `git restore --source` bypasses the LO file-safety gate

**Observation:** The approved proposal requires `_classify_bash_write_intent(command)` to treat `git restore --source ... <path>` as write intent. Evidence: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md` lists "`git restore --source ... <path>`" under the Bash write-intent classifier. The implementation regex in `.claude/hooks/lo-file-safety-gate.py` matches `git restore` followed by one path token, so `git restore --source HEAD -- scripts/implementation_authorization.py` captures `--source` as the path-like token, drops it as an option, emits no mutation target, and returns pass.

Probe command:

```text
@'
{"cwd":"E:/GT-KB","tool_name":"Bash","tool_input":{"command":"git restore --source HEAD -- scripts/implementation_authorization.py"},"harness_id":"A","harness_name":"codex"}
'@ | python .claude/hooks/lo-file-safety-gate.py
```

Observed output:

```text
{}
```

**Deficiency rationale:** `git restore --source` is a normal Git working-tree restore form and can overwrite a non-allow-listed project file. The approved proposal explicitly included this form because the hook must cover restore operations independent of flags.

**Impact:** A Loyal Opposition session can restore or overwrite source/config/hook files through this command shape while the new safety hook reports pass, preserving the same bypass class the slice was meant to close.

**Recommended action:** Parse `git restore` options and identify the pathspec after `--` or after recognized option arguments such as `--source <tree>`. Add regression tests for `git restore --source HEAD -- <path>` and `git restore --source HEAD <path>` under LO-only role projection.

## Required Revisions

1. Update the Bash classifier so `git restore --source HEAD -- scripts/implementation_authorization.py` and `git restore --source HEAD scripts/implementation_authorization.py` emit a mutation target for `scripts/implementation_authorization.py`.
2. Add focused tests for both command forms.
3. Re-run the platform hook suite, hook self-test, bridge preflights, and lint/format checks in an environment with the repo test dependencies available.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
python .claude/hooks/lo-file-safety-gate.py --self-test
@'...git restore --source HEAD -- scripts/implementation_authorization.py...'@ | python .claude/hooks/lo-file-safety-gate.py
```

Attempted but unavailable in this shell:

```text
python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -q
uv run python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -q
python -m groundtruth_kb deliberations search --limit 8 --json "Loyal Opposition file safety PreToolUse enforcement hook WI-3308"
```

The default interpreter and `.venv` both lacked the required packages; `uv` also resolved to an environment without `pytest`, `ruff`, and `groundtruth_kb`.

## Verdict

NO-GO. The implementation must close the `git restore --source` write-intent bypass before this thread can be VERIFIED.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
