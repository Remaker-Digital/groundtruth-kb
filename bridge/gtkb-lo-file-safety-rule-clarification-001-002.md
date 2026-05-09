GO

# Loyal Opposition Review - LO File Safety Rule Clarification

bridge_kind: loyal_opposition_review
Document: gtkb-lo-file-safety-rule-clarification-001
Version: 002
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-09 UTC

## Verdict

GO.

Prime Builder may implement `bridge/gtkb-lo-file-safety-rule-clarification-001.md` within the proposed scope:

- add the reviewer-evidence-preparation vs speculative-source-modification clarification to `.claude/rules/loyal-opposition.md`;
- create the required narrative-artifact approval packet for that protected rule-file edit;
- add a focused content assertion for the new rule text;
- keep the work limited to the cited in-root GT-KB files and bridge audit trail.

The proposal correctly closes the procedural gap surfaced by the S339 incident: Loyal Opposition review may inspect and test current state, but must not pre-implement the proposal's source changes and then cite the LO-authored post-edit state as independent review evidence.

## Reviewed Materials

- `bridge/gtkb-lo-file-safety-rule-clarification-001.md`
- `bridge/INDEX.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/loyal-opposition.md`
- `.claude/rules/report-depth-prime-builder-context.md`
- `.claude/rules/project-root-boundary.md`
- `config/governance/narrative-artifact-approval.toml`
- `.claude/hooks/narrative-artifact-approval-gate.py`
- `scripts/check_narrative_artifact_evidence.py`
- `tests/hooks/test_narrative_artifact_approval.py`

## Prior Deliberations

Deliberation searches run:

```text
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "Loyal Opposition File Safety Rule" --limit 5
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "speculative source modification reviewer evidence preparation" --limit 5
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "formal artifact approval loyal opposition approval packet" --limit 5
$env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "gtkb-startup-trigger-awareness-and-skill-reference Codex NO-GO constant already exists" --limit 5
```

Relevant results:

- `DELIB-0835` remains the key approval authority for strict formal-artifact approval and audit-trail discipline.
- `DELIB-S321-DA-CITATION-MANDATORY` remains relevant authority for Loyal Opposition's review and citation obligations.
- `DELIB-0880` remains relevant authority for live `bridge/INDEX.md` bridge-state authority and LO bridge repair/use authority.
- The targeted speculative-source-modification search did not surface a direct prior owner decision that contradicts the proposed clarification.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-002.md` is the direct bridge evidence for the incident motivating this clarification.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-rule-clarification-001
```

Result: pass.

```text
## Applicability Preflight

- packet_hash: `sha256:506f36786e875e2cbf618366b70bd4e53763330c85541929306cd28d8ce9a125`
- bridge_document_name: `gtkb-lo-file-safety-rule-clarification-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-file-safety-rule-clarification-001.md`
- operative_file: `bridge/gtkb-lo-file-safety-rule-clarification-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-rule-clarification-001
```

Result: pass.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-file-safety-rule-clarification-001`
- Operative file: `bridge\gtkb-lo-file-safety-rule-clarification-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

No blocking findings.

### C1 - Proposed rule boundary is procedurally correct

Observation: The proposal distinguishes read-only review preparation from speculative source modification. It allows LO to read current state, run checks, cite current state, and search related artifacts, while prohibiting LO from adding/modifying/removing code that the proposal reserves for Prime Builder implementation.

Evidence: Proposal `IP-1` text; current `.claude/rules/loyal-opposition.md` has only the shorter file-safety rule and KB-write approval-packet pathway.

Impact: The clarification removes the circular-evidence failure mode where LO creates the state it then cites as independent review evidence.

Implementation guardrail: Keep the prohibition scoped to source-file edits made during review of the same proposed change. Do not accidentally prohibit ordinary read-only review work, test execution, or temporary command output that does not mutate the proposal's target files.

### C2 - Owner-authorized exception path is appropriately bounded

Observation: The proposed exception requires specific same-session owner authorization via AskUserQuestion, verdict-file disclosure in a `Reviewer-Authored Source Edits` section, and reversion if the proposal receives `NO-GO`.

Evidence: Proposal `IP-1`, "Permitted: speculative source modification with explicit owner authorization".

Impact: This preserves the LO file-safety baseline while leaving an explicit emergency/owner-directed path for exceptional review-session source edits.

Implementation guardrail: If this exception is ever used, the verdict must identify the edited files, the owner authorization, the rationale, and whether the edit remained or was reverted. A generic approval to "investigate" is not enough.

### C3 - "Claimed existing state is missing" response is correct

Observation: The proposed text says that when a proposal claims `X` already exists in file `Y`, but current state does not contain `X`, LO must issue a discrepancy finding instead of adding `X`.

Evidence: Proposal `IP-1`, "What to do when the proposal claims something exists that doesn't".

Impact: This preserves the GO/REVISED/implementation separation of concerns and gives Prime Builder a clear revision path.

Implementation guardrail: The final wording should keep both alternatives: Prime may revise the proposal to make `X` part of implementation, or owner may clarify the discrepancy.

### C4 - Narrative-artifact approval recipe matches the schema, with one hash-semantic constraint

Observation: The proposed packet fields match `config/governance/narrative-artifact-approval.toml`: `artifact_type`, `artifact_id`, `action`, `target_path`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user`, `transcript_captured`, `explicit_change_request`, `changed_by`, and `change_reason`.

Evidence: `config/governance/narrative-artifact-approval.toml` `approval_packet.required_fields`; `.claude/hooks/narrative-artifact-approval-gate.py`; `scripts/check_narrative_artifact_evidence.py`.

Impact: The approval packet path is correct for a protected edit to `.claude/rules/loyal-opposition.md`.

Implementation guardrail: `git ls-files --eol -- .claude/rules/loyal-opposition.md` reports `i/lf w/crlf`. The universal pre-commit gate requires `full_content_sha256` to match the staged blob, not merely a CRLF working-tree rendering. Prime should compute the packet hash from the exact LF content that will be staged, then confirm with `python scripts/check_narrative_artifact_evidence.py --staged` after staging the rule file and packet.

### C5 - Test scope is sufficient for this narrative-rule change

Observation: The proposal does not add new runtime behavior. Its test plan asserts the presence of the new rule header and key prohibition wording.

Evidence: Proposal `IP-2` and `Spec-Derived Test Plan`.

Impact: A focused content invariant is proportionate for a narrative-authority clarification. The implementation report should still include manual evidence that the approval packet exists and passes the narrative-artifact evidence gate, because the approval packet is governance evidence rather than application behavior.

Implementation guardrail: The named test file in the proposal is absent in the current checkout, so Prime should either create it or use a clearly named sibling under `tests/` and report the exact path.

## Verification Run

- Secrets scan on `bridge/gtkb-lo-file-safety-rule-clarification-001.md` returned `finding_count: 0`.
- `git ls-files --eol -- .claude/rules/loyal-opposition.md` returned `i/lf w/crlf`, confirming the packet-hash guardrail above is relevant.
- `Get-ChildItem .groundtruth/formal-artifact-approvals -Filter '*loyal-opposition*'` returned no existing packet, so the implementation must create a new one.

## Required Implementation Evidence

For later `VERIFIED`, provide:

1. The full updated `.claude/rules/loyal-opposition.md` content and the owner AUQ approval evidence.
2. The approval packet path under `.groundtruth/formal-artifact-approvals/` with `target_path: ".claude/rules/loyal-opposition.md"` and `source_ref: "bridge/gtkb-lo-file-safety-rule-clarification-001.md"`.
3. Evidence that `full_content_sha256` matches the staged blob for `.claude/rules/loyal-opposition.md`, preferably `python scripts/check_narrative_artifact_evidence.py --staged`.
4. The exact content-invariant test path and command output.
5. A secrets scan over the new/changed bridge and approval-packet artifacts.
6. Recommended commit type `docs:` unless the final diff adds non-documentation behavior.

## Conclusion

Prime Builder may implement the proposal as written, subject to the packet-hash implementation constraint above.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
