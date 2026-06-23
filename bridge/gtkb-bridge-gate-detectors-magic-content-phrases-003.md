REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef010-de34-73d0-9baa-d0e50b18fae4
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop Prime Builder bridge revision

# Defect-Fix Proposal Revision - Bridge gate detectors require magic content phrases, surfacing failures late

bridge_kind: prime_proposal
Document: gtkb-bridge-gate-detectors-magic-content-phrases
Version: 003
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-bridge-gate-detectors-magic-content-phrases-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3463

target_paths: ["scripts/adr_dcl_clause_preflight.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py", "platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py"]

This REVISED proposal is filed as `bridge/gtkb-bridge-gate-detectors-magic-content-phrases-003.md`. The numbered bridge files remain append-only; this revision supersedes only the proposed implementation scope from `bridge/gtkb-bridge-gate-detectors-magic-content-phrases-001.md` and preserves the earlier NO-GO record unchanged.

## Claim

WI-3463 is not adequately fixed by enriching only `scripts/adr_dcl_clause_preflight.py`, because authors still encounter the same "magic phrase" failure class at the Write-time bridge-compliance gate. This revision keeps the offline preflight diagnostic enrichment, but expands the implementation scope to the actual write-time gate path: `.claude/hooks/bridge-compliance-gate.py` and the distributed template copy at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.

The intended fix is diagnostic-only. It must make missing evidence phrasing actionable at Write time by surfacing the relevant clause `evidence_pattern` and, when applicable, the refuting `failure_pattern`, without weakening clause applicability, owner-waiver handling, status-token validation, target-path enforcement, or exit/deny behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the write-time bridge-compliance gate is the first-line bridge authority guard, so missing-phrase guidance must appear where the write is blocked, not only in a later offline preflight report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves registry-backed governance clauses while reducing author friction that otherwise causes well-formed artifacts to fail on prose token phrasing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal compliance remains spec-linked and concrete; the change must not bypass the spec-linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove both the offline diagnostic and the write-time denial surface carry actionable evidence-pattern guidance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries Project Authorization, Project, and Work Item linkage lines for the active backlog item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the active hook and template copy must remain behaviorally aligned so Codex/Claude hook parity does not drift.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the gate verdict remains artifact-backed through the clause registry; the change exposes the registry evidence pattern instead of inventing a second authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - source and test changes are explicitly mapped in `target_paths`; no generated queue artifact or dashboard summary becomes authority.
- `GOV-STANDING-BACKLOG-001` - WI-3463 remains an open backlog item under `PROJECT-GTKB-RELIABILITY-FIXES`.

## Prior Deliberations

- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch; WI-3463 is in that batch scope.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction for bounded defect fixes under the reliability project.
- `DELIB-20263745` - prior Loyal Opposition review for bridge compliance gate detector correction; relevant precedent for correcting gate-detector friction.
- `DELIB-2660` - verdict context for one of the bridge artifacts that had to add prose phrasing to satisfy the numbered-file-chain clause.
- `DELIB-20261139` - directive enforcement registry precedent for keeping enforcement registry-backed while improving author-facing behavior.
- `DELIB-20265396` - bridge compliance gate template parity precedent; relevant because this revision deliberately includes both active and template hook paths.
- `DELIB-20263734` - audit-path isolation bridge-compliance gate review precedent; relevant to keeping write-time hook changes narrow and testable.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorize bounded reliability defect proposals under the active reliability project.
- `DELIB-20265457` authorized authoring proposals for open reliability work items, including WI-3463.
- No new owner decision is requested by this revision. The NO-GO required scope correction, not a change in owner intent.

## Requirement Sufficiency

Existing requirements are sufficient. The linked WI already describes the author-facing defect as bridge artifacts failing on required phrasing, and the NO-GO clarified that the acceptance point must include Write time. This revision therefore does not narrow the work item and does not add a new requirement; it corrects target scope so implementation reaches the actual bridge-compliance write chokepoint.

## NO-GO Findings Addressed

### FINDING-P1-001: Proposal only improves an offline preflight, not the Write-time gate

Addressed. The revised `target_paths` include `.claude/hooks/bridge-compliance-gate.py`, `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, and a hook-focused regression test file. The implementation scope now requires the Write-time bridge-compliance denial to surface missing `evidence_pattern` guidance. The offline preflight remains in scope only as the shared diagnostic source and regression surface.

## Proposed Scope

1. In `scripts/adr_dcl_clause_preflight.py`, enrich missing-evidence diagnostics so each blocking/advisory gap can surface the satisfying `evidence_pattern` and any relevant `failure_pattern` in a reusable structured or rendered form.
2. In `.claude/hooks/bridge-compliance-gate.py`, route bridge-file Write-time compliance denials that stem from missing clause evidence through the same diagnostic information, so the hook denial tells the author what pattern or phrase class would satisfy the clause.
3. Mirror the active hook change into `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to preserve scaffold/template parity.
4. Add or update `platform_tests/scripts/test_adr_dcl_clause_preflight.py` to prove offline preflight gap output includes evidence-pattern guidance without changing pass/fail semantics.
5. Add `platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py` to simulate a bridge-file Write-time denial for missing clause evidence and assert the denial includes actionable `evidence_pattern` guidance.

Out of scope:

- Relaxing registry detectors into structural-only checks.
- Changing `config/governance/adr-dcl-clauses.toml`.
- Adding owner-waiver behavior or changing owner-waiver semantics.
- Changing status-token, project-linkage, implementation authorization, or target-path enforcement.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py -q --tb=short` | A simulated Write-time bridge-compliance denial for a bridge artifact with missing clause evidence includes the relevant satisfying `evidence_pattern` or equivalent pattern guidance in the denial text. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | The offline clause preflight still exits with the blocking-gap status when evidence is missing, and the rendered gap includes the clause `evidence_pattern`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Same two focused pytest commands | Tests cover both enforcement surfaces named by the NO-GO: offline preflight and Write-time hook denial. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py -q --tb=short` | Active and template hook copies are loaded and expected to produce equivalent actionable guidance. |

Additional verification commands:

- `python -m ruff check scripts/adr_dcl_clause_preflight.py .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py`
- `python -m ruff format --check scripts/adr_dcl_clause_preflight.py .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py`

## Acceptance Criteria

1. A bridge-file Write-time denial caused by missing clause evidence surfaces actionable guidance tied to the clause `evidence_pattern`, not only a generic prose requirement.
2. The offline `adr_dcl_clause_preflight.py` report also surfaces the same evidence-pattern guidance for missing evidence.
3. Existing gate semantics are unchanged: applicability, evidence matching, failure matching, owner-waiver handling, and blocking/allow behavior remain the same.
4. Active and template bridge-compliance hook copies remain aligned for the changed behavior.
5. Focused pytest and ruff commands listed above pass.

## Risks / Rollback

- Risk: exposing regex text could be noisy in hook denial messages. Mitigation: include it as actionable diagnostic detail next to the existing prose requirement, and keep matching semantics unchanged.
- Risk: active/template hook drift. Mitigation: include both paths in target scope and load both copies in the hook-focused regression test.
- Risk: scope creep into detector semantics. Mitigation: this proposal forbids registry and structural-detector changes; it only enriches denial diagnostics.
- Rollback: revert the five target paths listed in this revision. No migration, database mutation, or governed-record mutation is required.

## Files Expected To Change

- `scripts/adr_dcl_clause_preflight.py`
- `.claude/hooks/bridge-compliance-gate.py`
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`
- `platform_tests/hooks/test_bridge_compliance_gate_magic_content_guidance.py`

## Recommended Commit Type

`fix`
