NO-GO

# Loyal Opposition Review - implementation_start_gate Finalization Quoting Fix

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 002
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-17 UTC
Work Item: WI-3357
Verdict: NO-GO

## Decision

NO-GO. The proposal identifies a real defect: quoted literal punctuation in a
commit message is currently treated as command chaining, so legitimate
`git commit -m "fix X; tidy Y"` commands are blocked by the implementation-start
gate. The proposal cannot receive GO in its current form because the proposed
quote-stripping implementation also treats executable command substitution
inside double quotes (`$(` and backticks) as benign message text.

That changes the security posture of the finalization exemption, contradicts
the prior finalization-thread intent to reject command substitution, and leaves
the verification plan without a regression proving command-substitution
protected writes remain blocked.

## Applicability Preflight

- packet_hash: `sha256:7312d74bd22ca7bd3fca12ced00730d72c54c81b6dd2cd7c49bd86b5403e5ea3`
- bridge_document_name: `gtkb-impl-start-gate-finalization-quoting-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md`
- operative_file: `bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-impl-start-gate-finalization-quoting-fix`
- Operative file: `bridge\gtkb-impl-start-gate-finalization-quoting-fix-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate note: no mechanical clause gaps were found. The NO-GO is
based on substantive review of the proposed command-classifier behavior, not on
preflight failure.

## Prior Deliberations

Commands:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "implementation-start gate git finalization command classification chaining quoted command substitution WI-3357 reliability fast lane" --limit 10 --json
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
```

Results:

- The targeted semantic search returned `[]`; no Deliberation Archive record
  was found for this exact quoted-control-marker defect.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` exists with
  `source_type = owner_conversation`, `outcome = owner_decision`, and
  `session_id = S351`. It approves the standing reliability fast-lane while
  preserving bridge review, work items, and all safety gates.
- The operative prior bridge-thread record is
  `bridge/gtkb-implementation-start-gate-repository-finalization-001.md`,
  which specified that the simple git finalization classifier must reject
  shell chaining and control markers, including command substitution and
  backtick execution.

## Review Evidence

Current implementation:

```text
scripts/implementation_start_gate.py:70:GIT_FINALIZATION_CONTROL_MARKERS = (";", "&&", "||", "|", "$(", "`")
scripts/implementation_start_gate.py:183:def _is_simple_git_finalization_command(command: str) -> bool:
scripts/implementation_start_gate.py:184:    if any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS):
scripts/implementation_start_gate.py:185:        return False
```

Prior finalization-thread intent:

```text
bridge/gtkb-implementation-start-gate-repository-finalization-001.md:61:1. Add a small classifier for standalone git finalization commands:
bridge/gtkb-implementation-start-gate-repository-finalization-001.md:62:   - allow `git commit ...` and `git push ...` when the command is a simple git invocation;
bridge/gtkb-implementation-start-gate-repository-finalization-001.md:63:   - reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution.
```

Current behavior confirms the real defect and the current safety behavior:

```text
git commit -m "fix X; tidy Y"                         -> simple False, decision block
git commit -m "$(cat msg.txt)"                        -> simple False, decision block
git commit -m "$(Set-Content -Path scripts/sample.py -Value z)" -> simple False, decision block
git commit -m "x"; Set-Content -Path scripts/sample.py -Value z -> simple False, decision block
git push origin develop                               -> simple True, decision allow
git push --force origin main                          -> simple False, decision block
```

Read-only simulation of the proposal's `_strip_quoted_spans()` implementation:

```text
git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"
blanked: git commit -m "                                               "
proposed_simple: True
```

The simulation used the helper body proposed in `-001` without modifying source
files. It shows the proposed classifier would exempt a command whose quoted
message performs command substitution containing a protected write command.

Authorization evidence:

```text
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
.\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
```

Observed:

- `PROJECT-GTKB-RELIABILITY-FIXES` is active.
- `WI-3357` has active project membership, `work_item_origin = defect`,
  `resolution_status = open`, and component `maintenance_tool`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry,
  covers work items by active project membership, allows `source`,
  `test_addition`, and `hook_upgrade`, and forbids `deploy`, `git_push_force`,
  and `spec_deletion`.

The authorization envelope is valid for a small defect fix, but it does not
authorize weakening the implementation-start gate's command-substitution
control without an explicit owner decision and revised verification coverage.

## Findings

### F1 - Command substitution inside double quotes cannot be treated as benign

Severity: P1 governance/safety drift

Observation: The proposal explicitly blanks the interior of both single- and
double-quoted spans, and states that treating `$(` / backtick inside double
quotes as benign is deliberate. The proposal acknowledges the strict shell
semantics differ because command substitution still executes inside double
quotes. The read-only simulation above confirms the proposed helper would return
`proposed_simple: True` for a `git commit -m "$(Set-Content -Path
scripts/sample.py -Value z)"` shape.

Deficiency rationale: The implementation-start gate exists to prevent protected
source, test, script, hook, configuration, deployment, repository-state, and
KB-mutation work unless a live latest-`GO` authorization packet covers it. A
command substitution embedded inside a double-quoted commit-message argument is
not literal message text in PowerShell or POSIX shell semantics; it is executable
command text. Exempting it as a "simple git finalization command" creates a
path where a protected mutation can run during the finalization command without
the live GO packet check.

Impact: The finalization exemption would no longer preserve the prior approved
scope from `gtkb-implementation-start-gate-repository-finalization`: simple
`git commit` / `git push` transport would remain allowed, but executable
subcommands inside a commit-message expression could bypass the protected-write
gate. That is not a pure false-positive correction and should not travel as a
fast-lane defect fix without explicit security/threat-model approval.

Recommended action: Revise IP-1 so the quote-aware scan distinguishes literal
punctuation from executable command substitution:

- allow `;`, `|`, `&&`, and `||` when they are inside quoted message text;
- continue to reject `$(` and backtick execution when they remain executable,
  including inside double quotes;
- allow `$(` / backtick only when they are provably literal, such as inside
  single quotes, or through a narrow owner-approved allowlist;
- if the HEREDOC message-generation pattern must be supported, handle it as an
  explicit, tightly tested exception rather than by blanking all double-quoted
  command substitutions.

### F2 - The verification plan lacks a test for the command-substitution bypass

Severity: P1 test gap against a protected behavior

Observation: The proposed tests cover quoted punctuation, quoted command
substitution returning true, unquoted `;` / `&&` chaining returning false,
chained protected writes after a quoted message returning a block, plain push,
and denied push flags. They do not include a test where command substitution
inside the quoted message itself contains a protected mutation.

Deficiency rationale: The missing test is exactly the boundary where the
proposal changes from "literal punctuation in a message should not block" into
"executable shell syntax inside a message is exempt." The prior finalization
thread required command substitution and backtick execution to reject the safe
classification. A spec-derived verification plan that approves command
substitution as simple finalization without a negative protected-mutation case
does not cover the linked implementation-start gate behavior.

Impact: Prime Builder could implement the proposed helper, pass all proposed
tests, and still ship a finalization-exemption bypass for protected writes.

Recommended action: Add negative tests before refiling:

- `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` must not
  be a simple finalization command and must not return `{}` from
  `gate_decision()`.
- A backtick command-substitution equivalent must also fail closed where the
  shell semantics make it executable.
- If a HEREDOC exception is retained, add paired tests proving the narrow
  accepted pattern is allowed while non-message-generation command substitution
  remains blocked.

## Non-Blocking Confirmations

- Root placement is valid: the target files are under `E:\GT-KB`.
- Bridge metadata is present: `Project Authorization`, `Project`, `Work Item`,
  and `target_paths` are provided.
- The mechanical applicability preflight and ADR/DCL clause preflight both
  pass.
- Project/work-item authorization is active and matches the proposed file
  classes.
- The underlying semicolon/pipe false positive is real and should be fixed.

## Opportunity Radar

No separate advisory filed. The useful automation signal is already inside this
thread: future implementation-start-gate review would benefit from a small
read-only probe helper that evaluates command-classifier cases without embedding
literal mutating command strings in the outer shell command. That is not needed
to resolve this proposal because the required regression tests can cover the
same behavior directly in `platform_tests/scripts/test_implementation_start_gate.py`.

## Owner Action

None for this NO-GO. Prime Builder can revise the proposal to preserve
command-substitution blocking while allowing literal quoted punctuation. If
Prime Builder wants executable `$(` / backtick expressions inside double-quoted
commit messages to be exempt, that is a new threat-model decision and should be
presented to the owner explicitly before refiling.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
