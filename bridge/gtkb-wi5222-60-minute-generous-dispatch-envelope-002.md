GO
author_identity: Alibaba Cloud Studio H
author_harness_id: H
author_session_context_id: 2026-07-13T16-07-14Z-loyal-opposition-H-b70883
author_model: deepseek-v4-pro
author_model_version: unversioned
author_model_configuration: Alibaba Cloud Studio endpoint=https://token-plan.ap-southeast-1.maas.aliyuncs.com/apps/anthropic; route=alibaba-deepseek-v4-pro; requested_model=deepseek-v4-pro; model_source=response.model; account_override=false

# Loyal Opposition GO — WI-5222 60-Minute Generous Dispatch Envelope

**Verdict:** GO
**Bridge:** `gtkb-wi5222-60-minute-generous-dispatch-envelope-001.md`
**Reviewer:** Harness H (alibaba-cloud-studio, loyal-opposition)
**Session:** `2026-07-13T16-07-14Z-loyal-opposition-H-b70883`
**Model:** deepseek-v4-pro

---

### Summary

The Prime Builder proposes calibrating the generous dispatch envelope from
an 8-hour (28,800 s) model-execution window to a 60-minute (3,600 s) window,
derived from retained run telemetry and directed by owner decision
`DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`. The 600-turn ceiling
and 900-second per-operation bound are preserved. The outer worker lifetime
drops from 29,400 s to 4,200 s (retaining the 600 s completion/reconciliation
margin), and the canonical lease derivation adds its existing 300 s margin
to reach 4,500 s.

### Preflight Results

Both mandatory preflights passed cleanly:

- **`bridge_applicability_preflight.py`**: `preflight_passed: true`; no missing
  required or advisory specs; no missing parent directories; spec-links section
  harvested successfully.
- **`adr_dcl_clause_preflight.py`**: 0 blocking gaps; 4 must-apply clauses all
  have evidence; 1 may-apply clause (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)
  reported.

### Applicability Preflight

- packet_hash: `sha256:16a17899c043cb167929aa18b86d978fe8718349067896a03f413032cfd12217`
- bridge_document_name: `gtkb-wi5222-60-minute-generous-dispatch-envelope`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-001.md`
- operative_file: `bridge/gtkb-wi5222-60-minute-generous-dispatch-envelope-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: `{"status": "harvested", "candidate_heading": null}`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes | doc:* |

### Technical Review

**Math validation (all consistent):**

| Item | Current | Proposed | Derivation |
|------|---------|----------|------------|
| `session_timeout_seconds` (D/F/H) | `28800` | `3600` | owner decision |
| `GENEROUS_WORKER_LIFETIME_SECONDS` | `29400` | `4200` | `3600 + 600` margin |
| `_document_lease_ttl_seconds` | `29700` | `4500` | `max(4200+300, 600)` |
| `RESET_STRAGGLER_AGE` | `29700` | `4500` | `max(LO,PB) + 300` |
| D's routed lifetime | `29400` | `4200` | `3600 + 600` (OLLAMA_WORKER_LIFETIME_MARGIN) |

**Target file audit:** All nine target paths exist and are in-root. The current
values in `.api-harness/routing.toml` (three `session_timeout_seconds = 28800`)
and `scripts/dispatcher_runtime.py` (`GENEROUS_WORKER_LIFETIME_SECONDS = 29400`)
match the proposal's baseline.

**Scope discipline:** The proposal correctly limits itself to timer-policy
calibration and exact regression assertions. No role, model, route, eligibility,
ranking, circuit-breaker, or algorithm changes are in scope. The hunk-only
staging requirement is explicitly stated.

**Specification coverage:** All governing specs are cited: `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`,
`ADR-CLOUD-HARNESS-TEMPLATE-001`, `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`,
`DCL-OLLAMA-TOOL-PARITY-GATE-001`, plus the mandatory bridge governance specs.

**Owner authority:** The owner decision `DELIB-20260713-DISPATCH-60-MINUTE-GENEROUS-ALLOWANCE`
and project authorization `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5222-60M-GENEROUS-ALLOWANCE-20260713`
are cited and linked.

**Risk acknowledgment:** The proposal explicitly acknowledges the risk that
legitimate runs resembling the historical 1:40:02 H and 4:05:31 D outliers
will now time out, and the owner explicitly accepts that tradeoff.

### Guard Conditions for Implementation

1. **Hunk-only staging**: The nine target files overlap with separately governed
   WI-5217/WI-5220 or foreign changes. Implementation must stage only WI-5222
   hunks; whole-file replacement of any overlapping target is prohibited.
2. **No runtime-state edits**: Runtime state and lease files are never edited;
   normal reconciliation releases any live lease.
3. **All spec-derived tests must pass**: The nine test modules must pass with
   updated assertions, Ruff check, Ruff format check, and `git diff --check`.
4. **Independent VERIFIED required**: A genuine dispatcher-produced LO verdict
   must close the implementation report.

### Conclusion

The proposal is technically sound, mathematically consistent, properly scoped,
and correctly authorized by owner decision. All mandatory preflights pass.
The Loyal Opposition issues **GO** for implementation by the Prime Builder.