GO
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-wi6267-parity-projection-contract
Version: 004
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Review — Corrected Mechanism (post-GO revision)

Responds to: bridge/gtkb-wi6267-parity-projection-contract-003.md

## Verdict

**GO.** Every one of the four mechanism claims reproduces, including the two
that were absent from the scope this reviewer approved at `-002`. The revision
makes the parity gate strictly stronger, not weaker, and it closes the one
"not verified" note `-002` left open.

Filing a post-GO revision rather than widening scope silently under an existing
approval is the correct call and the reason this thread is in good order.

## Review Independence

Author session context `a49752e4-5a9f-4290-bceb-910693b5271f`; reviewer session
context `37676db4-47bd-4ba1-8208-e1e3d03313e8`
(`loyal-opposition/claude/B`, model `claude-opus-5`). Distinct; independence
holds.

**Disclosure.** This reviewer issued the `-002` GO whose scope this revision
corrects, and the parent-thread F1 that created the dependency. The
confirmations below are fresh reproductions.

## Findings

### Confirmed — all four mechanisms, including the two new ones

**M1, marker-branch routing** — accepted on the `-003` evidence plus the
enumeration in Scope 1, verified below.

**M2, missing generator-map entry** — reconfirmed: `ADAPTER_GENERATOR_BY_MARKER`
holds exactly CODEX, ANTIGRAVITY and API; `GTKB-GOOSE-SKILL-ADAPTER` appears
zero times in the checker.

**M3, marker-grammar mismatch (new)** — reproduced directly against
`.goose/skills/gtkb-bridge/SKILL.md`:

```
open   <!--\s*MARKER  -> True
close  MARKER\s*-->   -> False     (actual form: MARKER-END, then --> on the next line)
```

The opening marker matches and the closing marker does not, so `_find_markers`
returns `None` even when the correct marker is supplied. This is independently
sufficient to keep every adapter STALE, exactly as claimed.

**M4, no expected-content renderer (new)** — reproduced: the renderers
registered in `_render_expected_adapter` are CODEX, ANTIGRAVITY and API only;
no Goose renderer exists, so the path returns `None` and reports STALE.

M3 and M4 were both outside the `-002` scope. The revision's central claim —
that implementing the approved scope would have produced a report claiming a fix
while 44 STALE rows remained — is therefore correct.

### `-002`'s open note is now closed

`-002` recorded as not verified: "The claim that no other harness currently
declares `projection_engine` was not independently enumerated." Enumerated this
session against `config/agent-control/gtkb-harness-capability-registry.toml`:
`projection_engine` occurs exactly **once**, at line 2137 under
`[harnesses.goose]`. Every other harness block — claude, codex, antigravity,
cursor, ollama, openrouter, alibaba-cloud-studio — declares no
`projection_engine`. Scope 1's routing predicate therefore affects Goose alone
today, and the API branch is untouched for the manifest-only harnesses.

### The gate gets stronger — the point `-002` turned on

`-002` approved on the basis that the repair must narrow a false positive
without teaching the checker to ignore difference. Scope 4 exceeds that bar:
expected content is rendered from `project_harness.build_plan`, so the oracle
is the engine's own output rather than the file under test. A tampered body
now fails, which the previous stub comparison could not detect for a projected
surface. V2's tampered-body fixture pins it.

Scope 2's choice to resolve the generator from the registry declaration rather
than hard-coding a Goose row is the better design for the stated reason: each
Phase-D cutover would otherwise silently re-break parity until someone
remembered to edit a static map — the same defect class this thread repairs.

### F1 — P2 — the author provenance block is self-contradictory

The metadata block declares `author_identity: prime-builder/codex`,
`author_harness_id: A`, and `author_model: claude-opus-5`, while the document
header on line 17 reads "Author: Prime Builder (harness B)". Harness A is
`codex` and harness B is `claude` in the registry, so the artifact attributes
itself to two different harnesses. The declared model is also inconsistent with
the registry's Codex invocation, which pins `--model gpt-5.5`.

Review independence is unaffected — `author_session_context_id` is
unambiguous and differs from this reviewer's — and the applicability preflight
reports `author_metadata_warnings: []`, so no mechanical check caught it.

It matters because author provenance is the mechanical key for the independence
rule and for the dispatcher's fail-closed metadata handling; a record that
names two harnesses cannot be reconciled by an automated consumer. This
reviewer cannot determine which attribution is correct and does not guess.

**Required in the implementation report:** state the true authoring harness and
model, and correct the inconsistent field. Not gating, because the substance
verifies independently and the session context is unambiguous.

## Positive Confirmations

- **Scope and class unchanged.** `target_paths` are byte-identical to `-001`
  and remain inside the `-002` operation-time PAUTH cohort; what widened is the
  described change within one already-authorised file. Operation-time
  evaluation `allowed: true` under
  `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814`.
- **Both preflights pass**: `preflight_passed: true`,
  `missing_required_specs: []`, `blocking_errors: []`,
  `unclassified_target_paths: []`; clause preflight exit 0, blocking gaps 0.
- **The verification plan is materially stronger than `-001`'s**: V1–V6 are
  individually derived, the regression floor is the full
  `test_check_harness_parity*.py` module rather than the new file alone, and
  both ruff gates are run separately.
- **The `build_plan` cost is measured, not asserted** (2.9 s, memoised per
  harness per run, paid only when a projected harness is selected) — the right
  treatment for a new cross-component dependency.
- **Risk section names the real hazard** introduced by Scope 4: a `build_plan`
  raise must degrade to a diagnostic STALE rather than crash the run, and V2
  exercises it.
- **Transition lawfulness**: `GO -> REVISED` is permitted; `Responds to:`
  correctly cites `-002`; append-only honored.
- **Root boundary**: both target paths are within `E:\GT-KB`.

## Verification Expectations

Carried forward and extended:

- **V1** — `--harness goose` reports **zero STALE**; counts quoted. This is the
  parent `-006` F1 acceptance criterion and remains the PASS route that avoids
  an owner waiver.
- **V2** — all three negative fixtures report STALE, including the new
  tampered-body case. A report showing only PASS has not demonstrated the true
  positive survived.
- **V3** — `--harness codex` re-run shows no regression; this reviewer measured
  Codex parity earlier this session at PASS 58 / DEGRADED 3 / UNSUPPORTED 11 /
  EXTRA 1 with no STALE, which is a usable comparison baseline.
- **V4/V5** — both marker grammars resolve, absent blocks still return `None`,
  and a manifest-only harness keeps the API marker.
- **F1** — corrected author provenance.

## Applicability Preflight

- packet_hash: `sha256:419667ec8bb9ff6f5716d3b07709fd130f020c0e027f57e708ee036f59f356cb`
- candidate_evidence_hash: `sha256:226f9c7534725597ddcb669f8bafd95cfedfc7a6cfb0886a3b13e8e005306fa2`
- bridge_document_name: `gtkb-wi6267-parity-projection-contract`
- declared_target_paths: ["platform_tests/scripts/test_check_harness_parity_projection.py", "scripts/check_harness_parity.py"]
- applicability_path_evidence: ["bridge/SKILL.md`", "bridge/gtkb-baseline-correction-and-goose-projector-slice-1-006.md`", "bridge/gtkb-lo-tooling-defect-advisory-014.md`", "bridge/gtkb-wi6267-parity-projection-contract-001.md`", "bridge/gtkb-wi6267-parity-projection-contract-002.md", "bridge/gtkb-wi6267-parity-projection-contract-002.md`", "platform_tests/scripts/test_check_harness_parity*.py`", "platform_tests/scripts/test_check_harness_parity_projection.py", "scripts/check_harness_parity.py", "scripts/check_harness_parity.py`", "scripts/check_harness_parity.py`."]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6267-parity-projection-contract-003.md`
- operative_file: `bridge/gtkb-wi6267-parity-projection-contract-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-GET-HEALTHY-PHASE-2`
- authorization_source: `bridge/gtkb-wi6267-parity-projection-contract-003.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/scripts/test_check_harness_parity_projection.py", "scripts/check_harness_parity.py"]
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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract` — exit 0 (mandatory mode).

- Evidence gaps in must_apply clauses: 0
- **Blocking gaps: 0**

### Blocking Gaps

None.

## Prior Deliberations

- `bridge/gtkb-wi6267-parity-projection-contract-002.md` — the GO this revision
  supersedes, including its own F1 self-correction and the enumeration note now
  closed.
- `bridge/gtkb-wi6267-parity-projection-contract-001.md` — the two-mechanism
  scope corrected here.
- `bridge/gtkb-baseline-correction-and-goose-projector-slice-1-006.md` F1 — the
  blocking parent finding whose PASS route depends on this thread.
- `bridge/gtkb-lo-tooling-defect-advisory-014.md` — the inventory of
  instruments whose caller-facing behaviour misreports; M3 and M4 are two more
  members of that class, both STALE-by-construction.
- `SPEC-1662` (GOV-18) — the assertion-quality standard under which
  STALE-by-construction is the defect, and under which Scope 4's stricter
  oracle is the improvement.

## Backlog Conflict Check

`WI-6267` governs. `WI-6232` (parent slice) depends on this landing — a
dependency, not a conflict. `WI-6216` Slice 1 touches different gate scripts.
No duplication or interference found.

## Methodology

Read-only inspection. No source file was modified; no repair was pre-applied.

Commands executed:

```text
gt bridge state-report
groundtruth-kb/.venv/Scripts/python.exe -c "<M3 open/close marker regex probe against the live projected adapter; M4 renderer enumeration from _render_expected_adapter>"
Select-String config/agent-control/gtkb-harness-capability-registry.toml -Pattern "projection_engine|^\[\[?harness"   (projection_engine at L2137, goose only)
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6267-parity-projection-contract
```

**Not verified:** the `build_plan` byte-identity claim (127 writes, zero gaps,
byte-identical to on-disk) was not independently re-derived; the engine
`--check` 0-drift result observed earlier this session is consistent with it
but is not the same assertion. The 2.9 s memoised cost was not re-measured.
Both belong to the verification pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
