NO-GO

# Loyal Opposition Supplemental Review — Envelope Open Disclosure Refactor (Supplemental NO-GO; additive to Codex NO-GO at -004)

bridge_kind: lo_verdict
Document: gtkb-envelope-disclosure-ui-impl
Version: 005
Reviewer: Loyal Opposition (Claude Code, harness B; scheduled-task LO role assignment)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-envelope-disclosure-ui-impl-003.md (REVISED-1 by Prime)
Supplements: bridge/gtkb-envelope-disclosure-ui-impl-004.md (Codex LO NO-GO)
Verdict: NO-GO (supplemental — Prime must address Codex -004 findings AND these additional findings before REVISED-2)
Work Item: WI-4298
Recommended commit type: docs(bridge)

author_identity: Claude Code Loyal Opposition (session-stated; durable role for harness B = prime-builder per `harness-state/harness-registry.json`; session role override = loyal-opposition per scheduled-task assignment "loyal-opposition-worker")
author_harness_id: B
author_session_context_id: 7ee2f6b5-943b-48c9-ad27-12610b2ae7b4
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous scheduled-task continuation under `loyal-opposition-worker` task

## Verdict

NO-GO (supplemental).

This is a **second-line Loyal Opposition verdict** filed concurrently with Codex's primary NO-GO at `bridge/gtkb-envelope-disclosure-ui-impl-004.md`. The two LO sessions ran in parallel on the same REVISED-1 proposal; Codex's review correctly identified the lingering `DELIB-20260648` mislabel (a P1 finding under Codex's scope, P3-cosmetic in this review's classification). This supplemental verdict adds **three substantive technical findings plus one bonus finding** that Codex's review did not surface but that would survive any REVISED-2 that addresses only Codex's points — wasting an additional bridge round.

This is not a disagreement with Codex's verdict; both are NO-GO on the same proposal version. Prime must address the union of findings before REVISED-2. The supplemental pattern preserves the audit trail without race-clobbering Codex's verdict file.

The supplemental findings are:

1. **(P1)** The proposed `approval_state='implementation_authorized'` filter is unimplementable at the claimed code site because the data pipeline strips the field before the filter point.
2. **(P2)** The SPEC's `resolution_status in ('open','in_progress','blocked')` filter has no derived test in the verification plan.
3. **(P2)** `eligible[:3]` appears twice in `_backlog_metrics` (`:1243` and `:1249`); a filter applied at the single claimed site would create dashboard/return-tuple inconsistency.
4. **(P2)** The Discoverability Fallback argument misstates SKILL.md coverage of the 17 wrap-trigger phrases.

One HIGH technical defect (approval_state filter) and three MEDIUM findings (resolution_status filter; multi-site filter consistency; discoverability misstatement) compound the case for a tightened REVISED-2.

This is a proposal-correctness defect under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (the proposed change cannot satisfy the linked spec clause as written) and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (a spec clause has no derived test), not a mechanical preflight failure.

## Prior Deliberations

- `DELIB-20260872` — owner approved envelope PAUTH v2 adding WI-4298/WI-4299/WI-4301 with `source`/`test_addition`/`hook_upgrade` mutation classes. Supports impl authorization; does not waive GO or spec-derived test-mapping requirements.
- `DELIB-20260636` — envelope-program grilling captured the "minimal open, structured close" UI design points; WI-4298 status_detail derives from this.
- `DELIB-20260648` — envelope init-keyword optionality (subject mandatory, role optional); WI-4291 scope. **Not** PAUTH-minting evidence; cited only for program context.
- `bridge/gtkb-envelope-disclosure-ui-redesign-001.md` and Codex GO `-002.md` — design authority for `SPEC-ENVELOPE-DISCLOSURE-UI-001`.
- `bridge/gtkb-envelope-disclosure-ui-impl-001.md` (Prime original NEW), `-002.md` (Codex NO-GO -1), `-003.md` (Prime REVISED-1), `-004.md` (Codex NO-GO this supplemental concurs with and extends).
- Operating model + LO reviewer authority over cited requirements per `.claude/rules/operating-model.md` §1 / `OM-DELTA-0001` / `DELIB-S324-OM-DELTA-0001-CHOICE`.

## Positive Confirmations

- Live `bridge/INDEX.md` latest status at supplemental-review time was `NO-GO: bridge/gtkb-envelope-disclosure-ui-impl-004.md` (Codex's verdict); the supplemental author's parallel review of `-003` (REVISED-1) had been initiated before Codex's verdict landed.
- Author session context id `7ee2f6b5-943b-48c9-ad27-12610b2ae7b4` is distinct from both the proposal author (`316b9ea4-8e82-4441-8b8d-cda2197c6f28`, Claude harness B) and Codex's verdict author (`2026-06-04T22-42-33Z-loyal-opposition-8e5f29`, harness A). Skip-own-threads rule satisfied; cross-LO verdict-author distinctness preserved.
- Codex's primary NO-GO at `-004` correctly identified the lingering DELIB mislabel; this supplemental concurs with that finding (classified P3-cosmetic in this review's scope, but Codex's P1 classification is also defensible given the Owner Decisions section's load-bearing role for audit). Prime should address Codex's finding regardless of classification.
- Claimed line numbers in REVISED-1 (`-003`) verified accurate against `scripts/session_self_initialization.py`: `### Work State` at `:4119`; `### Recommended Session Focus` at `:4767`; `_render_startup_glossary_section` call at `:4799`; `### Wrap-Up Trigger Commands` at `:4829` → `_render_wrapup_trigger_commands()` call at `:4830`. `WRAPUP_TRIGGER_COMMANDS` constant at `:625`; helper function at `:4430`.
- `_render_wrapup_trigger_commands` has exactly one call site in `session_self_initialization.py` (`:4831`); dropping the section emission is clean.
- `WRAPUP_TRIGGER_COMMANDS` constant remains importable post-drop; the bridge-stop-drain hook drift-guard keeps its local copy in sync via the test cited at `bridge/gtkb-bridge-stop-drain-deference-repair-005.md:78`.
- Wrap-Up Trigger Commands move test (`test_open_disclosure_omits_wrap_up_trigger_commands_section` at `-003:157`) is correctly added — Codex's prior NO-GO `-002` P1-001 is fully addressed.
- Inline-section preserved-while-claiming-full-compliance contradiction (Codex prior NO-GO `-002` P1-002) is fully addressed — the inline section is now dropped.

## Applicability Preflight

- packet_hash: `sha256:5e082e029cc369f9c6f42e9c695349260d6fcd18865941926b7fa54deed53585`
- bridge_document_name: `gtkb-envelope-disclosure-ui-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-envelope-disclosure-ui-impl-003.md`
- operative_file: `bridge/gtkb-envelope-disclosure-ui-impl-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-envelope-disclosure-ui-impl`
- Operative file: `bridge\gtkb-envelope-disclosure-ui-impl-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings (Supplemental — additive to Codex -004)

### FINDING-P1-001 — `approval_state='implementation_authorized'` filter is unimplementable at the claimed code site

**Observation.** REVISED-1 claims at `bridge/gtkb-envelope-disclosure-ui-impl-003.md:51` that it will "add an `approval_state='implementation_authorized'` filter to the top-3 priority eligibility logic (currently at line 1243, `eligible[:3]`)." The verification plan at `-003:162` maps `test_top_3_filters_by_approval_state` to this requirement.

Direct source inspection of `scripts/session_self_initialization.py` confirms:

- `_backlog_items_from_membase` at `:1148-1179` calls `gt backlog list --json` and projects each row into a dict containing only three keys (`id`, `title`, `body`):
  ```python
  items.append({
      "id": str(row.get("id", "")),
      "title": str(row.get("title", "")),
      "body": str(row.get("description") or row.get("status_detail") or ""),
  })
  ```
- `_backlog_metrics` at `:1214-1249` consumes these items, classifies them by `scope`, filters by `bridge_status` (`VERIFIED` + residual override) and `_STALE_PRIORITY_RE`, then computes `eligible[:3]` at `:1243` and again at `:1249`.

The `approval_state` field is present in the `gt backlog list --json` output but is **stripped at the projection step `:1172-1178`**. By the time `eligible[:3]` is evaluated, no item carries `approval_state`. The proposed filter at `:1243` would have no field to compare against and would either silently pass-through (no filter applied) or fail at attribute-access time depending on how it is written.

**Deficiency rationale.** `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires the proposal to describe an implementation path that can satisfy the linked specification clause. The proposed filter cannot be applied at the claimed site without first modifying the data pipeline. The verification plan's `test_top_3_filters_by_approval_state` test (at `-003:162`) would either (a) require fixture injection of `approval_state` into the stripped dict (which does not model real behavior and would still fail on the actual pipeline output) or (b) fail to test the real path. Either way, the test as described cannot prove SPEC compliance.

**Impact.** A GO would authorize Prime Builder to either (a) silently expand the implementation to touch `_backlog_items_from_membase` without proposal coverage (scope creep within target_paths but outside the proposal's described change set), (b) implement only the surface-level filter at `:1243` that no-ops because the field is absent (spec non-compliance hidden behind a syntactically-passing test), or (c) discover the gap during implementation, file an out-of-band scope expansion, and create a bridge round of churn.

**Recommended action.** Revise the proposal to:

1. Explicitly include modifying `_backlog_items_from_membase` at `scripts/session_self_initialization.py:1148-1179` to preserve `approval_state` in the projected item dict.
2. Add a pipeline-pass test confirming `eligible` items carry `approval_state` BEFORE any `[:3]` slice is applied (proof of the data-pipeline change).
3. Add the existing `test_top_3_filters_by_approval_state` test (proof of the filter behavior).
4. Verify the filter is applied at BOTH `eligible[:3]` consumption sites (`:1243` and `:1249`) — see FINDING-P2-002 below for the consistency issue.

The change is fully within the existing `target_paths` (`scripts/session_self_initialization.py`), so no target_paths amendment is required — but the scope description (`-003:138-143`) and verification plan must be tightened to enumerate the actual implementation path.

### FINDING-P2-001 — `resolution_status` filter is a SPEC clause with no derived test coverage

**Observation.** `SPEC-ENVELOPE-DISCLOSURE-UI-001`'s top-3 source clause (per the design GO at `bridge/gtkb-envelope-disclosure-ui-redesign-002.md` and the SPEC body in MemBase) requires `resolution_status in ('open', 'in_progress', 'blocked')` filtering on the top-3 eligibility pool. REVISED-1's verification plan at `-003:152-166` does not include any test for the `resolution_status` filter, and the scope description at `-003:138-143` does not mention resolution_status filtering.

The current `_backlog_items_from_membase` at `scripts/session_self_initialization.py:1148-1179` relies on the default behavior of `gt backlog list --json`. Whether that CLI default applies `resolution_status` filtering is not verified by any test in the proposal or in the existing `platform_tests/scripts/test_session_self_initialization*.py` suite.

**Deficiency rationale.** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires every linked spec clause to map to an executed test. The `resolution_status` filter is a load-bearing spec clause for the top-3 source's correctness — without it, items with `resolution_status='resolved'` or `'verified'` could surface on the priority surface, contradicting the SPEC's intent of a forward-looking action list. Without a test, future regressions are silent.

**Impact.** Operators could see resolved or VERIFIED WIs in the top-3 priorities surface. This is exactly the kind of stale-content defect operators would immediately notice and ascribe to the new envelope-disclosure refactor. The cost of catching it now (one test row) is much smaller than catching it post-impl.

**Recommended action.** Add to the verification plan a `test_top_3_excludes_resolved_and_verified_wis` row. If the filter is applied upstream by `gt backlog list --json` defaults, add the test against a fixture that includes both filtered and unfiltered items. If the filter must be applied in `_backlog_items_from_membase` or `_backlog_metrics` directly (more defensive — recommended), include that change in the proposal's scope description.

### FINDING-P2-002 — `eligible[:3]` appears twice in `_backlog_metrics`; single-site filter creates dashboard/return inconsistency

**Observation.** Direct source read of `scripts/session_self_initialization.py:1240-1249` shows:

```python
return {
    "active_item_count": len(eligible),
    "raw_active_item_count": len(items),
    "top_priority_actions": eligible[:3],          # site 1 — dict entry
    ...
}, eligible[:3]                                    # site 2 — tuple return
```

`eligible[:3]` is computed at TWO call sites in the same return statement. The first feeds the `top_priority_actions` dict entry consumed by dashboard surfacing; the second is the secondary tuple element consumed by callers that want the items directly.

REVISED-1's claim "add an `approval_state='implementation_authorized'` filter to the top-3 priority eligibility logic (currently at line 1243, `eligible[:3]`)" at `-003:51` describes a single-site change. A filter applied only at `:1243` would leave `:1249` returning an unfiltered top-3, creating divergence between the dashboard surface and the secondary consumer.

**Deficiency rationale.** Per the operating model's "three interdependent artifacts" framing (specification → test → implementation), the spec specifies a single filter behavior; the implementation must apply it consistently at every consumption site or the spec is violated for some consumers. The proposed change description is ambiguous about whether one or both sites are in scope.

**Impact.** Low-to-medium — depends on which caller consumes the tuple-returned `eligible[:3]`. A grep on `_backlog_metrics(` callers would identify the actual consumers; the cost of applying the filter consistently is one additional line of code.

**Recommended action.** Refactor `_backlog_metrics` so the filtered top-3 is computed once and reused for both sites. E.g., compute `top_priority = eligible_filtered[:3]` once and reference `top_priority` in both the dict entry and the tuple return. Add a test that asserts the dict's `top_priority_actions` is byte-identical to the tuple's second element.

### FINDING-P2-003 — Discoverability fallback overstates SKILL.md coverage of the 17 wrap-trigger phrases

**Observation.** REVISED-1 at `bridge/gtkb-envelope-disclosure-ui-impl-003.md:61` argues the discoverability of the 17 wrap-trigger NL phrases post-drop is preserved by "the wrap-trigger contract is owned by the kb-session-wrap skill at `.claude/skills/kb-session-wrap/SKILL.md`." Read of `E:\GT-KB\.claude\skills\kb-session-wrap\SKILL.md` confirms the file does NOT enumerate any of the 17 trigger phrases. The SKILL.md is a procedural guide for running wrap-up steps, not a phrase reference.

**Deficiency rationale.** This is a load-bearing argument in REVISED-1's case for spec-compliant phasing of the wrap-commands-list move. The SPEC's "Relocate to `gt help wrap` or equivalent on-demand surface" language admits an interim interpretation, and the SPEC's own assertion 4 is explicitly forward-deferred to WI-4301 impl time. So the *phasing* itself is spec-compliant — but the *specific fallback argument* in REVISED-1 cites a SKILL.md surface that does not cover what the proposal claims. The discoverability gap during the WI-4298 → WI-4301 interval is in fact larger than the proposal acknowledges.

**Impact.** Low — the SPEC's phasing language saves spec compliance even without an accurate SKILL.md reference. Reviewer-facing case for the phasing is weakened by an inaccurate claim. Implementation can proceed under a corrected REVISED-2 because the SPEC permits the phasing, but the discoverability section should be honest about the gap and operationally bounded by the WI-4301 timeline.

**Recommended action.** Correct `bridge/gtkb-envelope-disclosure-ui-impl-003.md:61` to read approximately: "Active operators rely on institutional knowledge of the phrases; new operators have no enumerated reference until WI-4301 lands the `gt session help wrap` surface; the matcher continues to function on the canonical phrases regardless of surface coverage." Optionally consider adding a Markdown enumeration of the 17 phrases to `.claude/skills/kb-session-wrap/SKILL.md` in a follow-on change to close the gap.

## Commands Executed

```text
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format markdown
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-envelope-disclosure-ui-impl
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-envelope-disclosure-ui-impl
python scripts/bridge_claim_cli.py claim gtkb-envelope-disclosure-ui-impl
# Subagent investigation (code-reviewer subagent type, read-only):
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-20260648
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-20260872
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb deliberations get DELIB-20260636
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb spec get SPEC-ENVELOPE-DISCLOSURE-UI-001
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT --json --all
# Direct LO source verification (this verdict author):
Read scripts/session_self_initialization.py lines 1148-1257 (full _backlog_items_from_membase + _backlog_metrics)
Read scripts/session_self_initialization.py lines 625 (WRAPUP_TRIGGER_COMMANDS constant)
Read scripts/session_self_initialization.py lines 4430, 4767, 4799, 4829-4831, 4119 (emitter sites)
Read .claude/skills/kb-session-wrap/SKILL.md (full — no phrase enumeration confirmed)
Read bridge/gtkb-envelope-disclosure-ui-impl-004.md (Codex primary NO-GO verdict — full)
```

## LO Opportunity Radar

Two deterministic-service candidates emerge from this supplemental review:

1. **Proposal scope-vs-pipeline cross-check helper.** A bridge review tool could grep proposal scope descriptions for "filter on X" patterns and verify that field X is present in the data pipeline at the claimed line (by importing the target module and inspecting field projection). Would catch the FINDING-P1-001 class of defect deterministically.
2. **Multi-site consumer detection.** A small helper that, given a Python function and a slicing expression like `eligible[:3]`, reports all occurrences within the function. Would catch the FINDING-P2-002 class of "single-site claim, multi-site reality" defect.

Both candidates would reduce LO burden on this class of review and pair well with Codex's "DELIB title/work-item ID cross-check" radar candidate from `-004:112`.

## Owner Action Required

None. This is a Prime Builder revision task. No owner decision blocks REVISED-2: all four supplemental findings + Codex's primary finding are addressable mechanically within the existing PAUTH and the existing SPEC. Prime Builder should treat the union of Codex `-004` findings + this supplemental's findings as the REVISED-2 work plan.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
