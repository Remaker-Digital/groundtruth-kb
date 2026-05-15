NO-GO

# Loyal Opposition Review - bridge-skill Protected-File Write Helper

bridge_kind: loyal_opposition_review
Document: gtkb-bridge-skill-protected-write-helper
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-15 UTC
Reviewed proposal: `bridge/gtkb-bridge-skill-protected-write-helper-001.md`
Verdict: NO-GO

## Claim

The proposed helper addresses a real friction point, and the batch-4 project authorization covers WI-3281. The proposal cannot receive GO as written because its core mechanism misunderstands the PreToolUse boundary: a Python helper that calls `Path.write_text` does not cause the harness `Write` / `Edit` PreToolUse hook to intercept the write.

## Prior Deliberations

Deliberation searches and lookups run:

```text
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "bridge skill protected write helper WI-3281 approval packet ergonomics" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "narrative artifact approval extension protected write packet gate target_path" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0835 --json
$env:PYTHONPATH='groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-1901 --json
```

Relevant results:

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` authorizes `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` and includes WI-3281.
- `DELIB-0835` is the owner decision requiring full native-format artifact presentation and approval evidence.
- `DELIB-1901` records the verified narrative-artifact approval extension, including the current two-layer design: Claude PreToolUse UX plus a universal pre-commit evidence floor.
- `DELIB-S350-CODEX-LO-FILE-SAFETY-VIOLATION` is relevant context for keeping Loyal Opposition review and Prime implementation boundaries clean, but it is not the basis for this NO-GO.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:194bc64b7c51194b06836d2ee6a4855a301381456653ffd18ef22d4acedfabdc`
- bridge_document_name: `gtkb-bridge-skill-protected-write-helper`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-skill-protected-write-helper-001.md`
- operative_file: `bridge/gtkb-bridge-skill-protected-write-helper-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-skill-protected-write-helper`
- Operative file: `bridge\gtkb-bridge-skill-protected-write-helper-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - P1 - `Path.write_text` does not trigger the narrative-artifact PreToolUse gate

Observation: The proposal's central claim is that the helper will set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` and perform the protected write "through a Python subprocess that the PreToolUse hook intercepts cleanly." The implementation plan then says the helper will write via `Path.write_text`.

Evidence:

- Proposal claim: "The helper sets the env var, validates the packet against the file's content-hash expectation, and performs the Write through a Python subprocess that the PreToolUse hook intercepts cleanly" (`bridge/gtkb-bridge-skill-protected-write-helper-001.md:22`).
- Proposal IP-1 says to set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` and then "Write the content to target via `Path.write_text`" (`bridge/gtkb-bridge-skill-protected-write-helper-001.md:68-69`).
- The live narrative-artifact hook is a Claude Code PreToolUse hook for `Write|Edit` tool calls (`.claude/hooks/narrative-artifact-approval-gate.py:3`, `:19`).
- The hook reads hook-event JSON and explicitly exits unless `tool_name` is `Write` or `Edit` (`.claude/hooks/narrative-artifact-approval-gate.py:232-233`).
- The narrative-artifact config states this layer is a Claude PreToolUse `Write|Edit` UX and that the universal harness-agnostic floor is `scripts/check_narrative_artifact_evidence.py` at pre-commit time (`config/governance/narrative-artifact-approval.toml:8-16`).

Deficiency rationale: A Python subprocess writing a file is a Bash command execution from the harness perspective, not a harness `Write` / `Edit` tool call with `tool_input.file_path` and `tool_input.content`. The PreToolUse hook therefore does not inspect the target write as proposed. At best, the helper would duplicate some validation in process and then write directly, which is materially different from "the hook intercepts cleanly."

Impact: The implementation could create a false sense that the real-time narrative-artifact gate fired when it did not. That is the exact audit problem WI-3281 is supposed to reduce: authors would still be writing protected files by script path and relying on secondary evidence rather than an intercepted tool write.

Required action: Revise the design to choose and name the actual enforcement path. Acceptable revision paths include:

1. A deterministic protected-writer helper that validates the narrative packet, writes with explicit LF/staged-blob semantics, and then runs `scripts/check_narrative_artifact_evidence.py --paths <target>` or the staged equivalent. Document this as the universal-floor path, not as a PreToolUse interception.
2. A non-writing helper that prepares the packet/env evidence and then instructs Prime to perform the actual harness `Write` / `Edit` call with an explicit packet reference so the PreToolUse hook sees `tool_name = Write|Edit`.

In either case, tests must assert the actual boundary. Do not include a test named `test_helper_env_var_propagates` as proof that the PreToolUse hook fired unless the test feeds a real hook JSON event into `.claude/hooks/narrative-artifact-approval-gate.py`.

### F2 - P2 - Skill adapter parity is outside the authorized scope

Observation: The proposal updates `.claude/skills/bridge/SKILL.md` but does not authorize or verify the generated Codex skill adapter.

Evidence:

- Proposal `target_paths` include `.claude/skills/bridge/SKILL.md` but not `.codex/skills/bridge/SKILL.md` or the adapter-generation command/test surface (`bridge/gtkb-bridge-skill-protected-write-helper-001.md:16`).
- The proposal says `.claude/skills/bridge/SKILL.md` will document the helper (`bridge/gtkb-bridge-skill-protected-write-helper-001.md:72-74`).
- The canonical bridge skill says the skill body is identical across Claude Code and Codex through `scripts/generate_codex_skill_adapters.py`, and that the Codex adapter at `.codex/skills/bridge/SKILL.md` should be regenerated from the canonical source (`.claude/skills/bridge/SKILL.md:206`).
- The Codex adapter itself says its canonical source is `.claude/skills/bridge/SKILL.md` and not to edit the adapter directly (`.codex/skills/bridge/SKILL.md:8-11`).

Deficiency rationale: The bridge skill is an explicitly cross-harness operating surface. Updating only the Claude canonical skill file without adapter regeneration creates a documented/available behavior split between Claude and Codex.

Impact: The helper may be documented for Prime Builder but not visible to Codex during bridge review/verification, or the adapter may drift from its canonical source until a later unrelated regeneration.

Required action: Revise the scope to include adapter regeneration and verification, or explicitly explain why this helper is Claude-only and should not appear in the Codex adapter. If cross-harness, add `.codex/skills/bridge/SKILL.md` to expected changed outputs or cite the exact regeneration command and test that proves adapter parity.

## Positive Confirmations

- The live bridge entry was latest `NEW` before review and had no show-thread drift.
- The batch-4 owner authorization exists as `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`.
- Live MemBase includes active project authorization `PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH` with `WI-3281` included, and active project membership `PWM-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-WI-3281`.
- Mandatory applicability and clause preflights have no missing required specs and no blocking clause gaps.

## Required Revision

Prime Builder should file `bridge/gtkb-bridge-skill-protected-write-helper-003.md` as `REVISED` after:

1. Correcting the enforcement model so it no longer claims a Python `Path.write_text` subprocess is intercepted as a harness `Write` / `Edit` call.
2. Adding tests against the actual hook JSON path and/or the universal `check_narrative_artifact_evidence.py` path.
3. Updating the skill adapter parity scope or explicitly scoping the helper as Claude-only.
4. Re-running and citing the mandatory preflights.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
