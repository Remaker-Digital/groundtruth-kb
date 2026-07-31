GO

# Loyal Opposition Verdict — WI-4978 Helper Compliance Audit Chokepoint

bridge_kind: lo_verdict
Document: gtkb-wi4978-helper-compliance-audit-chokepoint
Version: 002
Responds to: bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-001.md (NEW; bridge_kind prime_proposal)
Reviewer: Loyal Opposition (Claude, harness B)
Date: 2026-07-05 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-05T21-49-48Z-loyal-opposition-B-137d84
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; loyal-opposition; explanatory output style

---

## Verdict

GO. The proposal identifies a real defense-in-depth defect, its factual premise is
confirmed against live runtime, the remedy (a shared bridge-compliance audit at the
`scripts/gtkb_bridge_writer.write_bridge_file()` chokepoint) is architecturally sound,
all mandatory proposal sections are present, and both mechanical preflights pass with
zero gaps. The findings below are implementation guidance and verification conditions,
not blocking defects; they must be honored during implementation and reflected in the
post-implementation report.

## Review Independence

Author session context `019f3170-d706-77d3-b3e1-be39d47f3eda` (prime-builder/codex, harness A);
reviewer session context `2026-07-05T21-49-48Z-loyal-opposition-B-137d84` (loyal-opposition/claude,
harness B). Contexts are unrelated; independence gate satisfied (not same-session self-review).

## Prior Deliberations

Searched the Deliberation Archive for this topic:
`gt deliberations search "bridge compliance gate helper chokepoint requirement sufficiency bypass"`,
`"write_bridge_file audit before disk write helper bypass Write hook"`, and
`"WI-4977 headless dispatch stability requirement sufficiency missing"`. No prior deliberations
matched. The proposal's cited lineage was cross-checked and is consistent: the WI-4977
`-003`/`-004` incident (missing `## Requirement Sufficiency` persisted through a helper path,
caught only at LO review) is the motivating evidence, and `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`
with `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI4978-BATCH-A2-20260705` authorize the Batch A2 scope.
No previously rejected approach is being revisited.

## Defect Premise — Verified Against Live Runtime

The proposal's claims were verified by reading the live code, not by trusting the proposal text:

1. `scripts/gtkb_bridge_writer.write_bridge_file()` (lines 101–145) runs version/existence checks,
   a git-history conflict guard (WI-4520), verdict evidence-anchor validation (WI-4520,
   `validate_verdict_evidence_anchors`, line 127), author-metadata validation (line 134), and
   synthetic-session rejection (line 139). It does NOT invoke `bridge-compliance-gate.py --audit-only`.
   CONFIRMED: the writer never checks structural mandatory elements.

2. `.claude/hooks/bridge-compliance-gate.py` DOES enforce `## Requirement Sufficiency`
   (WI-3439 gate `_requirement_sufficiency_section_gap`, line 1163; fires for
   `bridge_kind ∈ {prime_proposal, implementation_proposal, prime_implementation_proposal}`),
   plus project-linkage metadata, concrete Specification Links, the Owner Decisions / Input
   section, Cross-Harness Disposition, the body status-token rule, the Prior-Deliberations
   placeholder check, and target_paths KB-mutation / approval-evidence completeness. CONFIRMED:
   these live only in the gate, not in the writer.

3. `revise_bridge.file_revision()` routes through `write_bridge_file()` (line 357) and runs the
   applicability + clause preflights, but NOT the compliance gate — so a malformed REVISED
   `prime_proposal` missing `## Requirement Sufficiency` persists. This is precisely the WI-4977
   incident. `impl_report_bridge.file_report()` routes through `write_bridge_file()` (line 447)
   and runs neither the compliance gate nor the applicability/clause preflights. CONFIRMED: both
   sibling helper paths bypass the gate.

4. `propose_bridge_codex_non_bypass()` (`.../bridge-propose/helpers/write_bridge.py` line 550) does
   run `_run_bridge_compliance_audit()`. The live NEW-proposal filing path
   (`groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:486`) calls that audited variant.
   CONFIRMED: the production propose path is already protected; the live gap is the
   revise/impl-report/verdict writer chokepoint the proposal targets.

Conclusion: the defect is real and correctly scoped, and routing `write_bridge_file()` through a
shared audit closes the revise/report/verdict gap at a single chokepoint.

## Applicability Preflight

- packet_hash: `sha256:c4fadc3c07f20ca8b599184daffea1fd687146ebbf4f0470b94caed4ada4b7c5`
- bridge_document_name: `gtkb-wi4978-helper-compliance-audit-chokepoint`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-001.md`
- operative_file: `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: harvested
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, requirement, specification, ADR, DCL, work item, backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 0 = pass.

| Clause | Applicability | Evidence found | Severity |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | may_apply | — | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — | blocking |

Both mandatory preflights pass on the operative NEW proposal file. Root-boundary check: every
`target_paths` entry is in-root under `E:\GT-KB` (scripts/, .claude/, .codex/, groundtruth-kb/templates/,
platform_tests/); no out-of-root dependency. Mandatory sections present: Specification Links (concrete),
Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency (single operative state
"Existing requirements sufficient"), project-linkage metadata (PAUTH/Project/Work Item), inline-JSON
target_paths, Cross-Harness Disposition (no waiver requested), Spec-Derived Verification Plan, and
Recommended Commit Type (`fix:`).

## Findings / Implementation Guidance (non-blocking; honor during implementation)

### [P1] Regression MUST prove the VERIFIED-finalization path still writes through the audited chokepoint

Observation: LO verdict finalization (`.claude/skills/verify/helpers/write_verdict.py --finalize-verified`)
and every GO/NO-GO/VERIFIED verdict write flow through the same `write_bridge_file()` chokepoint being
modified. Adding the compliance audit there makes it run — for the first time — on terminal verdict
finalization.

Deficiency risk: if the shared audit ever denies a well-formed GO/NO-GO/VERIFIED verdict, Loyal
Opposition can never finalize a thread and the entire bridge deadlocks. This is the single most severe
failure mode of the change. The gate's verdict-exemption logic (first-line GO/NO-GO/VERIFIED excluded
from `_ask_reason_for_content`, and the Requirement-Sufficiency / project-metadata / owner-decisions
gates scoped to NEW/REVISED or implementation-proposal `bridge_kind`) SHOULD make the audit a no-op for
verdicts — but "should" must be proven, not assumed. The proposal's acceptance criterion "valid …
verdict … helper writes still succeed" is correct in intent but the verification-plan table lists no
explicit VERIFIED-finalization test.

Action: add explicit regressions asserting that (a) a valid VERIFIED verdict via `write_verdict.py
--finalize-verified`, and (b) valid GO and NO-GO verdicts, still write successfully through the audited
`write_bridge_file()`. Include at least one verdict fixture that intentionally omits proposal-only
sections (e.g., no `## Requirement Sufficiency`) to prove the audit does NOT gate verdicts.

### [P2] Run the audit on the FINAL author-metadata-injected content, immediately before the write

Observation: `write_bridge_file()` computes `content_to_write = ensure_author_metadata(content, …)`
(lines 134–138), rejects synthetic session ids (line 139), then writes (lines 140–141). The reference
propose path audits `body_to_write` AFTER `ensure_author_metadata` (propose helper lines 538–554).

Deficiency rationale: to match both the PreToolUse hook (which sees the exact bytes written) and the
propose path, the shared audit must run on `content_to_write` (post-injection) and BEFORE
`target.write_text` — i.e., inserted between line 139 and the mkdir/write at 140–141. Auditing the
pre-injection `content` would check different bytes than land on disk and could diverge from the
Write-tool hook result.

Action: sequence the shared audit after `ensure_author_metadata` / `_reject_synthetic_session_context_id`
and before the file is written.

### [P3] Single-source the shared audit primitive; document propose_bridge() and .cursor coverage

Observation: (a) proposal step 1 says "add or expose a shared audit function" — to preserve parity by
construction, the primitive should live in ONE shared module (e.g., `scripts/gtkb_bridge_writer.py` or a
`scripts/` helper) that all harness copies import, not be duplicated into each `.claude`/`.codex`/
`.cursor`/template `write_bridge.py`. (b) The default `propose_bridge()` (propose helper line 408) writes
via `write_bytes` without the audit and does not use `write_bridge_file`, so the chokepoint does not
cover it; it is currently TEST-ONLY (live NEW filing uses the audited `propose_bridge_codex_non_bypass`),
so this is latent, not a live hole. (c) `.cursor/skills/bridge-propose/helpers/write_bridge.py` exists
but is not in `target_paths`; `.cursor` revise/impl-report helpers inherit the fix only if they import
`scripts.gtkb_bridge_writer`.

Action: per proposal step 2 ("update that caller or document why it is already protected"), the impl
report should explicitly disposition (b) — confirm `propose_bridge()` is test-only and the live propose
path already audits, or add the shared audit to it for symmetry — and (c) — confirm `.cursor` helpers
inherit the shared-writer chokepoint or are out of scope. Given PROJECT-GTKB-CROSS-HARNESS-PARITY, the
`.cursor` disposition should be stated, not left implicit.

## Verification Methodology (reproducible)

Files inspected: `bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-001.md`;
`scripts/gtkb_bridge_writer.py`; `.codex/skills/bridge-propose/helpers/write_bridge.py`;
`.claude/skills/bridge/helpers/revise_bridge.py`; `.claude/skills/bridge/helpers/impl_report_bridge.py`;
`.claude/hooks/bridge-compliance-gate.py` (lines 1–1238); `scripts/bridge_author_metadata.py`.
Commands run: `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` (both clean,
above); `gt deliberations search` (3 queries, no matches); a caller grep for
`propose_bridge` / `propose_bridge_codex_non_bypass` (live filing path confirmed as the audited
variant); Glob confirming the four named test files exist. No source files were modified during review.

## Conditions on GO

1. Implementation stays within the declared `target_paths` envelope (WI-4978 helper/writer/test scope).
2. The shared audit is a no-op for verdict/terminal statuses — proven by the [P1] regressions.
3. Existing evidence-anchor (WI-4520), author-metadata, credential-scan, and conflict/latest-status
   gates remain in force and their tests stay green.
4. `ruff check` AND `ruff format --check` are both run on all changed files and reported in the impl
   report (format is a separate gate from lint).
5. The post-implementation report carries forward these Specification Links and provides a spec-to-test
   mapping with executed command output per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
