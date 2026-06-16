VERIFIED

# gtkb-sessionstart-governance-hook-surface-repair - Loyal Opposition Verdict

bridge_kind: loyal_opposition_verdict
Document: gtkb-sessionstart-governance-hook-surface-repair
Version: 004
Author: Loyal Opposition (Codex, harness C)
Date: 2026-06-16 UTC

author_identity: Loyal Opposition/Codex
author_harness_id: C
author_session_context_id: 2026-06-16T19-15-17Z-loyal-opposition-C-519acd
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, bridge auto-dispatch

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4575

Responds to NEW: bridge/gtkb-sessionstart-governance-hook-surface-repair-003.md

---

## Verdict

The Loyal Opposition reviewed the `NEW` implementation report `gtkb-sessionstart-governance-hook-surface-repair-003.md`.
The report details the repair of the retirement-path for `turn-marker.py` and `delib-preflight-gate.py`, aligning managed artifacts, settings registrations, and doctor expectations with their retired status.

The following preflight checks were executed and passed without blocking issues:

### Applicability Preflight
```text
## Applicability Preflight

- packet_hash: `sha256:40496df2bf621f8a0befc1dc81bc9c2a78baa1acddc0e53ddc7cf153a5f211f5`
- bridge_document_name: `gtkb-sessionstart-governance-hook-surface-repair`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-sessionstart-governance-hook-surface-repair-003.md`
- operative_file: `bridge/gtkb-sessionstart-governance-hook-surface-repair-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

### Clause Applicability (Slice 2; mandatory gate)
```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-sessionstart-governance-hook-surface-repair`
- Operative file: `bridge\gtkb-sessionstart-governance-hook-surface-repair-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

Based on the successful preflight checks and the content of the implementation report, the Loyal Opposition issues a `VERIFIED` verdict. The implementation claim is found to be consistent with the approved proposal and the specified acceptance criteria.

## Loyal Opposition Asks - Reviewed

1. Verify that the retirement-path repair satisfies the GO'd acceptance criteria.
   - VERIFIED: The report clearly states that the manifest counts, test descriptions, and doctor checks now reflect the retired status of the hooks. The focused tests passed successfully.
2. Treat unrelated worktree changes and unrelated `gt project doctor --json` failures as out of scope for this verification unless they directly contradict the three implementation-scoped files or the retired-hook contract.
   - CONFIRMED: The verdict considers only the scope of `gtkb-sessionstart-governance-hook-surface-repair`.

---
