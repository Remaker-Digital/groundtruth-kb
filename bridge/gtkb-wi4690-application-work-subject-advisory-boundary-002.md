GO

# Loyal Opposition Review - Application work-subject advisory boundary - WI-4690

Reviewed file: `bridge/gtkb-wi4690-application-work-subject-advisory-boundary-001.md`
Bridge document: `gtkb-wi4690-application-work-subject-advisory-boundary`
Reviewer: Antigravity Loyal Opposition (harness C)
Date: 2026-06-23 UTC

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 956c4758-0f28-4a93-a5f1-6b8edd5b35c4
author_model: Gemini 3.5 Flash (High)
author_model_version: gemini-3.5-flash-high
author_model_configuration: Antigravity interactive session; resolved_role=loyal-opposition

## Verdict

GO for implementation under:
- Project Authorization: `PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23`
- Project: `PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH`
- Work Item: `WI-4690`
- Target paths: `scripts/workstream_focus.py`, `.claude/hooks/workstream-focus.py`, `.codex/gtkb-hooks/workstream-focus.cmd`, `platform_tests/hooks/test_workstream_focus.py`, `platform_tests/scripts/test_workstream_focus_hook_parity.py`, `platform_tests/scripts/test_advisory_backlog_router.py`, `scripts/advisory_backlog_router.py`

No blocking findings. The proposed change to isolate application work-subject tool writes is well-specified, links the correct design decisions and constraints, and restricts application writes to the cross-scope advisory channel (ADVISORY files and staging config).

## First-Line Role Eligibility Check

Resolved session role: Loyal Opposition. Latest bridge status reviewed: NEW. Status authored here: GO. Loyal Opposition is authorized to issue GO verdicts for NEW implementation proposals.

## Review Evidence

- Checked live bridge files. The latest status for this document `gtkb-wi4690-application-work-subject-advisory-boundary` was `NEW` in version `001`, authored by Prime Builder (harness A).
- Verified the design:
  1. The proposal restricts the `application` work-subject to read-only tool access for most GT-KB platform targets (rules, hooks, source, etc.), preventing direct changes in application mode.
  2. The proposal preserves the `ADVISORY` bridge output as the only permitted write destination for cross-scope concerns, allowing application sessions to suggest platform enhancements without bypassing governance.
  3. Spec-derived verification plan covers all needed regression tests and parity hooks.

## Prior Deliberations

- `DELIB-20265586` - owner selection for the snapshot-bound project implementation authorization.
- `DELIB-20265287` - owner decision set for the envelope disposition and autonomous dispatch program.
- `DELIB-20260621` - activity disposition profile framing.

## Specification-Linkage Review

The proposal links:
- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001`
- `DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001`
- `DCL-ADVISORY-ROUTING-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-CODE-QUALITY-BASELINE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

All linked specifications are applicable, and the spec-to-test mapping covers the isolation constraints.

## Applicability Preflight

```json
{
  "applicable_specs": {
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001": {
      "exists_in_membase": true,
      "matched_by": [
        "content:artifact",
        "content:traceability",
        "content:deliberation",
        "content:MemBase"
      ],
      "rationale": "Development changes should preserve traceability across artifacts, tests, reports, and decisions.",
      "severity": "advisory",
      "spec_id": "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "status": "verified",
      "title": "Model project memory as a durable artifact graph",
      "type": "architecture_decision"
    },
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001": {
      "exists_in_membase": true,
      "matched_by": [
        "content:Agent Red"
      ],
      "rationale": "Application/root placement work must honor the GT-KB root and applications/ boundary.",
      "severity": "blocking",
      "spec_id": "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "status": "specified",
      "title": "Adopter applications live at <gt-kb-root>/applications/<name>/",
      "type": "architecture_decision"
    },
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001": {
      "exists_in_membase": true,
      "matched_by": [
        "content:candidate",
        "content:blocked",
        "content:verified"
      ],
      "rationale": "Artifact lifecycle transitions should expose candidate, active, deferred, blocked, superseded, verified, complete, rejected, and retired states.",
      "severity": "advisory",
      "spec_id": "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "status": "verified",
      "title": "Artifact lifecycle triggers require thresholds, states, and confirmation flows",
      "type": "design_constraint"
    },
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001": {
      "exists_in_membase": true,
      "matched_by": [
        "doc:*",
        "content:Specification Links",
        "content:implementation proposal",
        "content:bridge proposal"
      ],
      "rationale": "Implementation proposals must cite every relevant governing specification.",
      "severity": "blocking",
      "spec_id": "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "status": "specified",
      "title": "Implementation proposals must be linked to all relevant specifications",
      "type": "design_constraint"
    },
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001": {
      "exists_in_membase": true,
      "matched_by": [
        "doc:*",
        "content:VERIFIED",
        "content:verification"
      ],
      "rationale": "Verification must be derived from linked specifications and executed against the implementation.",
      "severity": "blocking",
      "spec_id": "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "status": "specified",
      "title": "VERIFIED is conditional on test creation + execution derived from linked specs",
      "type": "design_constraint"
    },
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001": {
      "exists_in_membase": true,
      "matched_by": [
        "content:owner decision",
        "content:requirement",
        "content:specification",
        "content:ADR",
        "content:DCL",
        "content:work item",
        "content:backlog"
      ],
      "rationale": "Concrete requirements, decisions, risks, procedures, and future work should be preserved as durable artifacts.",
      "severity": "advisory",
      "spec_id": "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "status": "verified",
      "title": "Artifact-oriented governance is the default project interpretation stance",
      "type": "governance"
    },
    "GOV-FILE-BRIDGE-AUTHORITY-001": {
      "exists_in_membase": true,
      "matched_by": [
        "doc:*",
        "path:bridge/**"
      ],
      "rationale": "All bridge-mediated implementation and verification work must honor the file bridge authority model.",
      "severity": "blocking",
      "spec_id": "GOV-FILE-BRIDGE-AUTHORITY-001",
      "status": "verified",
      "title": "Live bridge index authority and permanent bridge repair authority",
      "type": "governance"
    }
  },
  "bridge_document_name": "gtkb-wi4690-application-work-subject-advisory-boundary",
  "cited_specs": [
    "ADR-APPLICATION-ISOLATION-CONTRACT-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "ADR-DEFAULT-GT-KB-EXCEPTION-HOSTED-APP-001",
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
    "DCL-ACTIVITY-DISPOSITION-PROFILE-001",
    "DCL-ADVISORY-ROUTING-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-PLATFORM-APPLICATION-NON-SPECIFICITY-001",
    "DCL-TOPIC-ENVELOPE-ROUTING-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "DELIB-20265586",
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
    "GOV-CODE-QUALITY-BASELINE-001",
    "GOV-FILE-BRIDGE-AUTHORITY-001"
  ],
  "content_source": {
    "mode": "bridge_file_operative",
    "path": "bridge/gtkb-wi4690-application-work-subject-advisory-boundary-001.md"
  },
  "missing_advisory_specs": [],
  "missing_required_specs": [],
  "operative_version": {
    "path": "bridge/gtkb-wi4690-application-work-subject-advisory-boundary-001.md",
    "status": "NEW",
    "version_number": 1
  },
  "packet_hash": "sha256:c216f5f18e7069e846224a7a6f7bcd9d600e44e6d4beb599084d6c9480f57b9d",
  "preflight_passed": true,
  "target_paths": [
    ".claude/hooks/**`,",
    ".claude/hooks/workstream-focus.py",
    ".codex/gtkb-hooks/workstream-focus.cmd",
    "bridge/**`,",
    "bridge/*.md`",
    "bridge/<slug>-001.md`",
    "bridge/agent-disposition-wi4589-external-mutation-gate-slice1-006.md`",
    "bridge/governance",
    "bridge/gtkb-envelope-disposition-autonomous-dispatch-advisory-001.md`",
    "bridge/gtkb-work-subject-root-enforcement-implementation-020.md`",
    "config/governance/spec-applicability.toml`",
    "memory/**`,",
    "platform_tests/hooks/test_workstream_focus.py",
    "platform_tests/hooks/test_workstream_focus.py::test_application_subject_allows_current_repo_bridge_or_governance_write`",
    "platform_tests/hooks/test_workstream_focus.py`",
    "platform_tests/scripts/test_advisory_backlog_router.py",
    "platform_tests/scripts/test_advisory_backlog_router.py`",
    "platform_tests/scripts/test_workstream_focus_hook_parity.py",
    "platform_tests/scripts/test_workstream_focus_hook_parity.py`",
    "scripts/advisory_backlog_router.py",
    "scripts/advisory_backlog_router.py`",
    "scripts/bridge_claim_cli.py",
    "scripts/workstream_focus.py",
    "scripts/workstream_focus.py`"
  ],
  "warnings": {
    "missing_parent_dirs": [],
    "spec_links_section": {
      "candidate_heading": null,
      "status": "harvested"
    }
  },
  "work_items": [
    "GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH",
    "GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23",
    "WI-4690"
  ]
}
```

## Clause Preflight

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4690-application-work-subject-advisory-boundary`
- Operative file: `bridge\gtkb-wi4690-application-work-subject-advisory-boundary-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
