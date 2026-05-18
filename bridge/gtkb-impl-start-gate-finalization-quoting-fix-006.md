NO-GO

# Loyal Opposition Review - implementation_start_gate Finalization Quoting Fix REVISED-2

bridge_kind: loyal_opposition_verdict
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 006
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-17 UTC
Work Item: WI-3357
Verdict: NO-GO

## Decision

NO-GO. REVISED-2 fixes the prior first-delimiter blocker from `-004`: the proposed parser now searches for the first heredoc delimiter line and requires the substitution close after that delimiter.

One safety blocker remains. The new opener parser matches only through the quoted delimiter in the opener, then searches forward for the delimiter line. It does not require the rest of the opener line, after the quoted delimiter and before the heredoc body newline, to be whitespace-only. Shell syntax can place output redirection, a separator, or a pipeline on that same opener line. The proposed neutralizer would blank that same-line executable/redirection tail together with the safe-looking heredoc span, hiding it from the control-marker and path scans.

## Applicability Preflight

- packet_hash: `sha256:635c839b7912570abdb2b2fd9d4288e71abcb258d2b07618125540bc1e6822fe`
- bridge_document_name: `gtkb-impl-start-gate-finalization-quoting-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md`
- operative_file: `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-finalization-quoting-fix`
- Operative file: `bridge\gtkb-impl-start-gate-finalization-quoting-fix-005.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Commands:

```text
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "implementation-start gate git finalization command classification chaining quoted command substitution HEREDOC WI-3357 Option B" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
```

Results:

- The targeted Deliberation Archive search returned `[]`; no direct WI-3357 deliberation record was found beyond this bridge thread and the standing fast-lane decision.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` exists with `source_type = owner_conversation`, `outcome = owner_decision`, and `session_id = S351`. It approves the standing reliability fast-lane while preserving bridge review, work items, and safety gates.
- `PROJECT-GTKB-RELIABILITY-FIXES` is active. `WI-3357` has active membership, `work_item_origin = defect`, `resolution_status = open`, and component `maintenance_tool`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry, covers work items by active project membership, allows `source`, `test_addition`, and `hook_upgrade`, and forbids `deploy`, `git_push_force`, and `spec_deletion`.

Operative prior bridge-thread records:

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-004.md` - prior NO-GO requiring a parser that recognizes the first delimiter line and fails closed when executable text appears after that delimiter.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md` - prior NO-GO requiring executable command substitution and backticks inside double quotes to remain disqualifying.
- `bridge/gtkb-implementation-start-gate-repository-finalization-001.md:61-63` - prior accepted intent: allow simple standalone git finalization, but reject the safe classification when shell chaining, command substitution, or backtick execution is present.

## Review Evidence

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md:197-200` defines `_HEREDOC_OPENER_RE` to match the fixed opener only through `$(cat <<['"]DELIM['"]`.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md:221-240` searches for the first delimiter line and accepts the span when text after that delimiter line strips to a leading close parenthesis.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md:244-262` blanks every accepted span from `opener.start()` through the computed close parenthesis.
- No proposed step checks the slice between `opener.end()` and the next newline. If that slice contains an output redirect, a command separator, a pipeline, or another shell operator, it is inside the span that gets blanked.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md:314-322` argues that a recognized span runs only read-only `cat` over literal text and permits no file write. That claim is not established unless the parser also proves the opener line has no same-line executable/redirection tail after the quoted delimiter.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md:332-350` lists the revised verification cases. They include the first-delimiter negatives from `-004`, but they do not include opener-line redirection or opener-line separator/pipeline negatives.

## Findings

### F1 - The HEREDOC parser does not validate the opener-line tail

Severity: P1 governance/safety drift

Observation: The proposed `_HEREDOC_OPENER_RE` stops immediately after the quoted delimiter, and `_find_heredoc_message_substitution_spans()` then searches forward for the first delimiter line. There is no validation that the rest of the opener line is whitespace-only before the heredoc body begins.

Deficiency rationale: Quoted heredoc semantics protect only the heredoc body. They do not make same-line shell syntax after the heredoc redirection harmless. A command can place an output redirection, command separator, or pipeline after the quoted delimiter on the opener line and before the body newline. Under the proposed neutralizer, that same-line tail is part of the accepted span and is replaced with spaces before `_has_disqualifying_control_marker()` and path classification run. The parser therefore proves the first delimiter boundary but not the equally necessary opener-line boundary.

Impact: A protected write or chained command can be hidden inside a command substitution that is classified as simple git finalization. That weakens the implementation-start gate and violates the repository-finalization intent to reject shell chaining/control markers rather than merely correcting a false block for literal commit-message text.

Recommended action: Revise the parser so that, after `_HEREDOC_OPENER_RE` matches, it locates the next line break and requires `command[opener.end():line_break]` to be whitespace-only. The delimiter-line search should then start after that line break. Any non-whitespace opener-line tail must fail closed and leave the `$(` visible to the execution-marker scan.

### F2 - The verification plan lacks opener-line tail negatives

Severity: P1 test gap against a protected behavior

Observation: The revised test matrix covers literal quoted punctuation, ordinary executable substitution, backtick execution, non-HEREDOC substitution, unquoted delimiter, non-`cat`, first-delimiter command-after-body cases, plain push, and denied push flags. It does not test same-line syntax after the quoted heredoc delimiter on the opener line.

Deficiency rationale: The HEREDOC allowlist's safety depends on proving that the neutralized span contains only read-only `cat` over literal text. That proof requires both boundaries: the first delimiter line and a clean opener line. Tests 16 and 17 cover the first-delimiter boundary but not opener-line redirection, separator, or pipeline forms.

Impact: Prime Builder could implement the proposed parser, satisfy every listed test, and still ship the opener-line bypass described in F1.

Recommended action: Add mandatory negative unit and `gate_decision()` tests for opener-line tails before refiling:

- an output-redirection tail after the quoted heredoc delimiter and before the body newline;
- a command-separator tail after the quoted heredoc delimiter and before the body newline;
- optionally a pipeline tail, because it exercises the same missing boundary.

Expected result for each: `_find_heredoc_message_substitution_spans()` returns no span, `_is_simple_git_finalization_command()` returns `False`, and `gate_decision()` blocks without an authorization packet.

## Non-Blocking Confirmations

- Root placement is valid: target paths are under `E:\GT-KB`.
- Bridge metadata is present: `Project Authorization`, `Project`, `Work Item`, and `target_paths`.
- The mandatory bridge applicability preflight and ADR/DCL clause preflight both pass mechanically.
- The standing fast-lane authorization envelope is valid for a small source / hook / test defect fix.
- REVISED-2 resolves the `-004` first-delimiter issue; the remaining blocker is a separate opener-line boundary.
- The underlying literal-punctuation defect remains real and should be fixed.

## Opportunity Radar

No separate advisory filed. The deterministic opportunity stays in this thread: the HEREDOC recognizer should be unit-tested as a pure parser against adversarial shell-shape cases, including both first-delimiter and opener-line-tail boundaries.

## Owner Action

None. Prime Builder can revise the proposal by adding opener-line tail validation and the missing negative tests. No additional owner decision is needed because this is implementation safety inside the already-selected Option B scope.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
