NO-GO

# Loyal Opposition Review - GT-KB `grill-me-for-clarification` Skill Proposal

**Thread:** gtkb-grill-me-for-clarification-skill
**Reviewed proposal:** bridge/gtkb-grill-me-for-clarification-skill-001.md
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-15
**Verdict:** NO-GO

## Summary

The proposed skill is directionally aligned with the owner clarification workflow, and the mechanical applicability and clause preflights pass. It cannot receive GO because the proposal is not currently implementable through the protected implementation-start gate: it lacks the required machine-readable project-linkage metadata, it requests a MemBase spec-assertion mutation outside `target_paths`, and its first implementation command uses a bridge id that does not exist in `bridge/INDEX.md`.

## Prior Deliberations

Deliberation Archive searches performed:

- `owner clarification interview skill grill me for clarification decision tree`
- `SPEC-INTAKE-1262c1 INTAKE-45c006c4 grill-me-for-clarification`
- `Prime Builder interrogative default owner factual claims clarification decision`

Relevant results:

- `INTAKE-45c006c4` v2 - owner-confirmed requirement candidate; confirms `SPEC-INTAKE-1262c1` and contains the substantive raw requirement text for this skill.
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` - owner directive establishing the Prime Builder interrogative default that this skill operationalizes.
- `DELIB-0710` - related spec-quality history emphasizing clarity of intent and completeness at the right development stage.

No prior deliberation found that conflicts with a reusable, scope-required clarification interview skill.

## Findings

### F1 - P1 - Missing project-linkage metadata blocks an implementation proposal

**Observation:** The proposal is an implementation-targeting NEW entry, but its header only includes bold prose fields for `Governing spec`, `Work item`, and `target_paths`; it does not include the required machine-readable `Project Authorization:`, `Project:`, and `Work Item:` lines. Evidence: `bridge/gtkb-grill-me-for-clarification-skill-001.md:1-10`.

**Deficiency rationale:** The bridge skill contract requires every implementation-targeting NEW/REVISED proposal to include those three machine-readable lines, unless the document declares a non-implementation `bridge_kind` exemption. Evidence: `.claude/skills/bridge/SKILL.md:46-55`. The hook code treats absence of those lines as a hard block under `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT`. Evidence: `.claude/hooks/bridge-compliance-gate.py:583-594`.

**Impact:** Prime Builder cannot demonstrate that this work item is tied to an active project authorization and active project membership before implementation. GO would weaken the current project/WI authorization chain.

**Recommended action:** Revise the proposal to add a compliant metadata block near the top:

```text
Project Authorization: PAUTH-...
Project: PROJECT-...
Work Item: ...
```

If this auto-created WI is not yet attached to an active project authorization, perform that governed attachment first or revise the work item/project surface so the bridge metadata resolves cleanly through the live membership check.

### F2 - P1 - The proposed spec-assertion mutation is outside `target_paths`

**Observation:** The proposal's `target_paths` list includes only two skill files and one test file. Evidence: `bridge/gtkb-grill-me-for-clarification-skill-001.md:10`. Later, the proposal says `SPEC-INTAKE-1262c1` will gain grep assertions and includes that as implementation step 5. Evidence: `bridge/gtkb-grill-me-for-clarification-skill-001.md:173-174` and `bridge/gtkb-grill-me-for-clarification-skill-001.md:192-200`.

**Deficiency rationale:** KB mutations are implementation work, and protected implementation must be denied when it is outside the GO'd proposal's `target_paths`. Evidence: `.claude/rules/codex-review-gate.md:48-63`. The file bridge protocol requires proposals that request KB-mutation work to include `target_paths` metadata listing the concrete files or globs authorized for implementation. Evidence: `.claude/rules/file-bridge-protocol.md:39-48`.

**Impact:** The post-GO implementation would need to mutate `groundtruth.db` by updating the spec's assertions, but the authorization packet derived from this proposal would not cover that mutation. This creates either a failed implementation-start gate or an out-of-scope MemBase write.

**Recommended action:** Revise `target_paths` to include `groundtruth.db` and spell out the exact MemBase mutation being authorized: target spec id, assertion JSON/shape, change reason, changed_by attribution, and read-back verification. Include a test/read-back step that confirms the new `SPEC-INTAKE-1262c1` assertion version exists and executes.

### F3 - P2 - Requirement sufficiency overclaims the current spec record

**Observation:** The proposal states that `SPEC-INTAKE-1262c1` governs the implementation completely and contains the five-phase behavior, persistence routing, and non-goals. Evidence: `bridge/gtkb-grill-me-for-clarification-skill-001.md:102-108`. Live MemBase read-back found `SPEC-INTAKE-1262c1` at version 1 with `description: null`, `assertions: null`, and no linked tests; the substantive requirement text is in `INTAKE-45c006c4` v2, not in the spec row.

Command evidence:

```text
python - <<'PY'
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
cfg = GTConfig.load()
db = KnowledgeDB(cfg.db_path)
spec = db.get_spec('SPEC-INTAKE-1262c1')
print({k: spec.get(k) for k in ['id','version','title','status','description','assertions']})
print(db.get_tests_for_spec('SPEC-INTAKE-1262c1'))
PY
```

Observed result:

```text
{'id': 'SPEC-INTAKE-1262c1', 'version': 1, 'title': 'grill-me-for-clarification owner clarification interview skill', 'status': 'specified', 'description': None, 'assertions': None}
[]
```

**Deficiency rationale:** A proposal may carry the missing detail in its own body, but the `Requirement Sufficiency` claim specifically says the formal spec record governs the implementation completely. That is not true against live MemBase. The raw intake is valuable evidence, but it is a deliberation/intake record, not the populated spec body.

**Impact:** Verification would risk proving the implementation against proposal prose rather than against a durable, sufficiently populated specification record. This undermines the spec-derived verification gate for a new skill that is itself meant to improve requirement clarity.

**Recommended action:** Either amend `SPEC-INTAKE-1262c1` through the governed path so the formal spec carries the substantive behavior clauses, or revise the proposal to explicitly cite `INTAKE-45c006c4` as the operative owner-confirmed requirement source and explain why the empty spec-row body is acceptable for this slice. If the spec is amended, include the MemBase mutation in `target_paths` and verification evidence per F2.

### F4 - P2 - The implementation authorization command uses the wrong bridge id

**Observation:** The implementation sequence starts with `python scripts/implementation_authorization.py begin --bridge-id gtkb-grill-me-for-clarification-skill-001`. Evidence: `bridge/gtkb-grill-me-for-clarification-skill-001.md:192-194`.

**Deficiency rationale:** `implementation_authorization.py begin --bridge-id` expects the document name from `bridge/INDEX.md`, not the versioned file stem. The live document name is `gtkb-grill-me-for-clarification-skill`; running the proposed command returns:

```text
{
  "authorized": false,
  "error": "Bridge document not found in INDEX: gtkb-grill-me-for-clarification-skill-001"
}
```

**Impact:** Even after GO, Prime Builder's first protected implementation step would fail before creating the required authorization packet.

**Recommended action:** Revise the command to:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-grill-me-for-clarification-skill
```

## Applicability Preflight

- packet_hash: `sha256:7ba15e2262f34ca59108953101b105575ad7698601f17d9617dcaf6611dda118`
- bridge_document_name: `gtkb-grill-me-for-clarification-skill`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-grill-me-for-clarification-skill-001.md`
- operative_file: `bridge/gtkb-grill-me-for-clarification-skill-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-grill-me-for-clarification-skill`
- Operative file: `bridge\gtkb-grill-me-for-clarification-skill-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no owner-waiver line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Verification Commands

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-grill-me-for-clarification-skill --format json --preview-lines 400
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-grill-me-for-clarification-skill
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations search "SPEC-INTAKE-1262c1 INTAKE-45c006c4 grill-me-for-clarification" --limit 10
python scripts/implementation_authorization.py begin --bridge-id gtkb-grill-me-for-clarification-skill-001
```

## Required Revision

File a REVISED proposal that:

1. Adds compliant project authorization metadata or resolves the missing project authorization/membership first.
2. Includes `groundtruth.db` and the exact spec-assertion mutation in implementation scope, or removes the KB mutation from this slice.
3. Corrects the implementation authorization command to use the document id, not the versioned file stem.
4. Resolves the requirement-sufficiency overclaim by either populating the formal spec body/assertions through governance or explicitly carrying `INTAKE-45c006c4` as operative requirement evidence with an explanation.

After those changes, the structural/parity skill test plan is likely an appropriate baseline for this LLM-procedure skill, provided the revised proposal keeps the `allowed-tools` set constrained to the stated no-code/no-bridge-writing behavior.
