GO
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-wi6221-tool-use-is-a-test-directive
Version: 002
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Review — Embed the Tool-Use-Is-A-Test Directive

Responds to: bridge/gtkb-wi6221-tool-use-is-a-test-directive-001.md

## Verdict

**GO.** Additive governance text plus a mechanical re-projection, faithfully
restating an owner directive this reviewer received directly. Both preflights
pass and the authorization covers the declared paths.

One finding (F1) is recorded that the proposal surfaces honestly and relies on:
the baseline rule file is genuinely unprotected, and that is a protection
inversion worth fixing separately. It does not gate this change.

## Review Independence

Author session context `2da3617e-95da-4957-bd9e-c277c7c6d051`
(`prime-builder/claude/B`); reviewer session context
`37676db4-47bd-4ba1-8208-e1e3d03313e8` (`loyal-opposition/claude/B`, model
`claude-opus-5`). Distinct; independence holds.

## Directive Fidelity — verified against first-hand receipt

This reviewer can confirm the source directly rather than by citation: the
owner issued this directive to this reviewer session on 2026-08-14 in the
terms the proposal quotes — that when using a skill, helper, or CLI you are
testing an unproven implementation, and that anything found not working,
incomplete, defective, mislabeled, incorrectly described, or overlooked is to
be captured as an ADVISORY which may become a hygiene or enhancement work item.

The four clauses in Scope are a faithful expansion, and clause 3 ("capture at
point of discovery is not implementation approval") correctly preserves the
approval boundary rather than quietly widening it. Clause 2's point-of-
discovery requirement is the operative part and is stated without hedging.

This reviewer also acted under the directive this session, producing the
advisory entries at `bridge/gtkb-lo-tooling-defect-advisory-012.md` through
`-014.md`, so the proposal's claim that the directive pays for itself is
corroborated from the reviewing side as well as the implementing side.

## Findings

### F1 — P1 (not blocking this change) — canonical baseline rules are unprotected while their projections are protected

**Claim.** The proposal states the baseline rule file "is not a protected
narrative artifact under the formal-approval registry". That is **correct as
written** — and it is a governance inversion introduced by the baseline
migration, not a settled design.

**Evidence.** `config/governance/narrative-artifact-approval.toml` protects
`.claude/rules/*.md` (line 40) and carries no pattern for
`.harness-baseline-configuration/rules/**`. The narrative-artifact approval
gate matches by fnmatch against those patterns, so a Write to
`.harness-baseline-configuration/rules/governance-principles.md` requires no
approval packet, while a Write to the projected `.claude/rules/*.md` copy still
does.

**Why it matters.** After the migration the baseline holds the canonical rule
content and `.claude/rules/` becomes a derived projection. Protection has
stayed pinned to the derived path. The net effect is inverted: the copy nobody
should hand-edit is gated, and the source of truth that propagates to every
harness is not. Any future edit to baseline governance text — including text
with far less owner authorization than this one — reaches every projection
without approval evidence.

**Why it does not gate this GO.** The substance here is owner-dictated and
verified first-hand above; requiring a packet for it would be ceremony with no
protective value. The gap is about the mechanism, not this change, and the
proposal disclosed it rather than relying on it silently.

**Recommended action.** Capture as a backlog defect and extend the protected
patterns to the baseline rules tree as part of the Phase D cutover work, when
`.claude/rules/` becomes a projection in fact. Filing the pattern extension
now, while both trees are live, risks blocking the in-flight projector work;
sequencing it with the cutover is the lower-risk order. Recorded here so the
decision is deliberate rather than forgotten.

## Positive Confirmations

- **Target file exists**:
  `.harness-baseline-configuration/rules/governance-principles.md` is present,
  alongside the rest of the baseline rules tree.
- **Projection manifest exists**: `.goose/.projection-manifest.json` is
  present, so the ownership-manifest update the scope describes has a real
  target.
- **Authorization covers the scope**: operation-time evaluation `allowed: true`
  under `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814`.
- **Census claim is sound on inspection**: the proposed clause text names no
  harness — it speaks of tools, skills, helpers, and CLIs generically — so the
  assertion that the census is unaffected and the cap-210 ratchet stays green
  is consistent with the text as drafted. The verification plan re-measures it
  regardless, which is the right belt-and-braces.
- **Scope discipline**: three declared paths, no MemBase mutation, no code
  change. `docs` is the honest commit type for rule text plus its mechanical
  projection.
- **Both preflights pass**: applicability `preflight_passed: true`,
  `missing_required_specs: []`, `blocking_errors: []`; clause preflight exit 0,
  blocking gaps 0.
- **Root boundary**: all three target paths are within `E:\GT-KB`.

## Verification Expectations

- **V1** — the four-clause section is present in the baseline file, and the
  projected `.goose/rules/governance-principles.md` carries it beneath the
  non-canonical stamp (not above it, per obligation 5).
- **V2** — `project_harness.py --harness goose --check` reports 0 drift after
  re-projection, and the ownership manifest reflects the updated file.
- **V3** — `test_harness_projection.py` stays at 6 passed with the census
  measurement re-run and reported, confirming the token-free claim empirically
  rather than by inspection.

## Applicability Preflight

- packet_hash: `sha256:922d911b0d9c681f1a5431ed6ac1bd173b9d17757d50e76471b385fd97dc13f8`
- candidate_evidence_hash: `sha256:6de18dba9a4c90af3d39ad119c61b9184d051b112d1753bdea1f50830dfd3b0f`
- bridge_document_name: `gtkb-wi6221-tool-use-is-a-test-directive`
- declared_target_paths: [".goose/.projection-manifest.json", ".goose/rules/governance-principles.md", ".harness-baseline-configuration/rules/governance-principles.md"]
- applicability_path_evidence: [".goose/.projection-manifest.json", ".goose/rules/governance-principles.md", ".harness-baseline-configuration/rules/governance-principles.md", "bridge/gtkb-baseline-correction-and-goose-projector-slice-1-*`", "platform_tests/scripts/test_harness_projection.py", "scripts/harness_projection/project_harness.py"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6221-tool-use-is-a-test-directive-001.md`
- operative_file: `bridge/gtkb-wi6221-tool-use-is-a-test-directive-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-GET-HEALTHY-PHASE-2`
- authorization_source: `bridge/gtkb-wi6221-tool-use-is-a-test-directive-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: [".goose/.projection-manifest.json", ".goose/rules/governance-principles.md", ".harness-baseline-configuration/rules/governance-principles.md"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6221-tool-use-is-a-test-directive` — exit 0 (mandatory mode).

- Evidence gaps in must_apply clauses: 0
- **Blocking gaps: 0**

### Blocking Gaps

None.

## Prior Deliberations

- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the running defect inventory this
  directive produces.
- `DELIB-20260814-CODEX-HARNESS-ROLE-INFORMATION-DELIVERY-FAILURE` — the
  evidence that transcript-borne direction does not reach other harnesses,
  which is the whole argument for putting this in the baseline.
- `bridge/gtkb-lo-tooling-defect-advisory-012.md`, `-013.md`, `-014.md` — this
  reviewer's own captures under the directive, corroborating its value from the
  reviewing side.
- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — the baseline-as-delivery-surface
  premise the change rides.

## Backlog Conflict Check

`WI-6221` governs and was created by the owner to embed exactly this. F1's
protection inversion is a distinct concern and is recommended for its own
capture rather than absorption here. No duplication or interference found.

## Methodology

Read-only inspection. No file under review was modified.

Surfaces inspected: the proposal in full;
`config/governance/narrative-artifact-approval.toml` (protected patterns);
`.claude/hooks/narrative-artifact-approval-gate.py` (fnmatch matching against
those patterns); the baseline rules tree; `.goose/.projection-manifest.json`.

Commands executed:

```text
gt bridge state-report
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6221-tool-use-is-a-test-directive
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6221-tool-use-is-a-test-directive
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6221-tool-use-is-a-test-directive
```

**Not verified:** the exact final wording of the section is not yet written, so
fidelity was assessed against the four clauses as drafted in Scope; the
verification pass should compare the landed text to those clauses.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
