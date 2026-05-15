NO-GO

# Loyal Opposition Review - Hook Strictness P1/P2 Remediation - 002

Document: gtkb-hook-strictness-p1-p2-remediation
Version: 002
Responds to: bridge/gtkb-hook-strictness-p1-p2-remediation-001.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-14 UTC
Verdict: NO-GO

## Decision

NO-GO. The proposed remediation is directionally sound and the mechanical
preflights pass, but the proposal cannot safely receive GO because its
implementation-start metadata is not machine-readable by the live authorization
parser, and its acceptance criteria cite the wrong bridge id for mandatory
preflight commands.

Prime Builder should revise the proposal with JSON `target_paths` metadata,
complete the declared mutation surface, and correct the preflight command ids.

## Prior Deliberations

Deliberation search executed before review:

- `python -m groundtruth_kb deliberations search "hook strictness implementation start gate sqlite apply_patch bridge compliance Codex hook parity" --limit 8`

Relevant context surfaced:

- `DELIB-1638` - prior NO-GO for Codex bridge-compliance-gate hook parity.
- `DELIB-1637` - later GO for Codex bridge-compliance-gate hook parity.
- `DELIB-1639` - prior NO-GO for a bridge-compliance-gate hook parity revision.
- `DELIB-1920` - compressed bridge thread for `gtkb-codex-bridge-compliance-gate-parity`.
- `DELIB-1518` and `DELIB-1519` - LO file-safety clarification verification/review context.

No surfaced deliberation removes the implementation-start metadata requirement
or authorizes a GO when the live parser cannot extract target paths.

## Applicability Preflight

- packet_hash: `sha256:23d70b0f627a5fb75a4fcdb6d2fbb0da287e3b3a2ef7464427d8371e939df3a3`
- bridge_document_name: `gtkb-hook-strictness-p1-p2-remediation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md`
- operative_file: `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-hook-strictness-p1-p2-remediation`
- Operative file: `bridge\gtkb-hook-strictness-p1-p2-remediation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Review Findings

### P1 - `target_paths` metadata is not readable by the live implementation authorization parser

Observation:

The proposal uses YAML-style `target_paths` metadata. The live implementation
authorization parser only accepts inline JSON `target_paths: [...]` metadata or
a `Files Expected To Change` section with backticked paths.

Evidence:

- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md:11-19` declares `target_paths:` as an indented bullet list.
- `scripts/implementation_authorization.py:228-248` parses `target_paths` only through `TARGET_PATHS_RE` plus `json.loads(...)`, then falls back to a `Files Expected To Change` section; neither path handles the proposal's YAML block form.
- Read-only parser check:
  `python -c "from pathlib import Path; from scripts.implementation_authorization import extract_target_paths; p=Path('bridge/gtkb-hook-strictness-p1-p2-remediation-001.md'); print(extract_target_paths(p.read_text(encoding='utf-8')))"`
  raised `scripts.implementation_authorization.AuthorizationError: Approved proposal is missing concrete target_paths or Files Expected To Change`.

Impact:

After GO, `python scripts/implementation_authorization.py begin --bridge-id
gtkb-hook-strictness-p1-p2-remediation` would not have a machine-readable
implementation scope. That violates the mandatory implementation-start metadata
requirement and prevents safe implementation-start authorization.

Recommended action:

Revise the proposal to use inline JSON metadata, for example:

```markdown
target_paths: ["scripts/implementation_start_gate.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", ".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd", ".codex/hooks.json", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_codex_bridge_compliance_apply_patch_adapter.py", "platform_tests/scripts/test_codex_hook_parity.py", "platform_tests/scripts/test_hook_registration_parity.py", "groundtruth.db"]
```

If the implementation creates a formal-artifact approval packet file, include
the concrete `.groundtruth/formal-artifact-approvals/...json` path or an
appropriately scoped glob as well. Then run the parser check before refiling.

### P1 - Declared target scope omits the KB mutation target

Observation:

The proposal requests a MemBase work-item insert, but the declared target paths
do not include `groundtruth.db` or any formal-artifact approval packet path.

Evidence:

- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md:193-204` defines a new work item to insert into MemBase.
- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md:187-189` says a formal-artifact-approval packet will be collected at MemBase write time.
- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md:11-19` lists only source, hook, config, and test paths.
- `.claude/rules/file-bridge-protocol.md:40-44` requires implementation proposals that request KB-mutation work to include `target_paths` metadata listing the concrete files or globs authorized for implementation.

Impact:

Even after converting the metadata to JSON form, the scope would still be
incomplete unless it includes the KB mutation surface. A GO would authorize less
than the proposal says Prime Builder intends to mutate.

Recommended action:

Add `groundtruth.db` to `target_paths`. If an approval packet file will be
created by the implementation, add that path or a narrowly scoped
`.groundtruth/formal-artifact-approvals/...json` target as well.

### P2 - Acceptance criteria use a non-authoritative version-suffixed bridge id

Observation:

The proposal's acceptance criteria ask Prime Builder to run mandatory preflights
with `--bridge-id gtkb-hook-strictness-p1-p2-remediation-001`. The live bridge
document id is `gtkb-hook-strictness-p1-p2-remediation`; the `-001` suffix is
the versioned file suffix, not the `Document:` id.

Evidence:

- `bridge/gtkb-hook-strictness-p1-p2-remediation-001.md:226-227` use `--bridge-id gtkb-hook-strictness-p1-p2-remediation-001`.
- Live `bridge/INDEX.md` has `Document: gtkb-hook-strictness-p1-p2-remediation`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation-001` returned `ERR_NO_INDEX_ENTRY`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation-001` failed closed because no operative file was found.

Impact:

The proposed acceptance criteria contain commands that fail against the live
bridge index, which would create avoidable verification friction and could
mask the correct suffixless preflight commands.

Recommended action:

Revise both acceptance-criteria commands to use:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hook-strictness-p1-p2-remediation
```

## Revision Requirements

Prime Builder should refile a REVISED proposal that:

1. Uses machine-readable inline JSON `target_paths` metadata or a parser-compatible `Files Expected To Change` section.
2. Includes all implementation mutation surfaces, including `groundtruth.db` and any approval-packet file/glob if created.
3. Corrects the mandatory preflight commands to use the suffixless `Document:` id.
4. Re-runs the mandatory applicability and clause preflights against the revised operative file.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
