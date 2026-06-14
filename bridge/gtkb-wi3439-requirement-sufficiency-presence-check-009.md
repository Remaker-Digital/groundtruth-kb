REVISED

bridge_kind: implementation_report
Document: gtkb-wi3439-requirement-sufficiency-presence-check
Version: 009
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T18-51-40Z-prime-builder-B-7d693a
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3439
target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py"]
implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-3439 Implementation Report (REVISED): bridge-compliance-gate `## Requirement Sufficiency` — exactly-one operative-state enforcement

## Revision Scope

This REVISED report addresses the sole blocking finding (F1) of the verification NO-GO at `-008`. No owner action is required (the NO-GO itself recorded "Owner Action Required: None — within the existing PAUTH and corrected target-path envelope"); the change is fully within `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` and the corrected three-path `target_paths` carried forward from `-005`/`-007`.

## Remediation of `-008` Finding F1 (the sole blocking finding)

`-008` F1 (P1/blocking): the gate accepted a `## Requirement Sufficiency` section containing **both** mutually exclusive operative states at once. The governing contract (`.claude/rules/file-bridge-protocol.md` § "Mandatory Implementation-Start Authorization Metadata") requires **exactly one** operative state. The prior helper used the combined `REQUIREMENT_SUFFICIENCY_OPERATIVE_RE.search(...)` which only proved presence-of-either, so a dual-state section was wrongly accepted. Codex's behavioral probe showed `_requirement_sufficiency_section_gap(<both states>)` returning `None` (valid).

Resolution (both hook copies, byte-identical):

1. **Two state-specific regexes** replace the presence-of-either test as the operative-state oracle: `REQUIREMENT_SUFFICIENCY_STATE_SUFFICIENT_RE` and `REQUIREMENT_SUFFICIENCY_STATE_NEW_REQUIRED_RE`, collected in `REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES`.
2. **`_requirement_sufficiency_section_gap` now counts distinct operative states present** (`states_present = sum(1 for state_re in REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES if state_re.search(joined))`) and returns a gap descriptor when the count is `0` ("no operative state") **or `> 1`** ("multiple operative states (exactly one required: ... XOR ...)"). Only `states_present == 1` returns `None` (valid).
3. The pre-existing `REQUIREMENT_SUFFICIENCY_OPERATIVE_RE` combined regex is retained for backward-compatible call sites; the gap helper no longer depends on it for the accept/deny decision.

This is genuine behavior change since `-007` (SHA moved from `2adb6772…` to `7b5d734a…`); the dual-state section is now **denied** at Write-time.

### `-008` Required Revisions — disposition

| `-008` required revision | Status |
|---|---|
| 1. File next bridge version as REVISED | This report (`-009`, status REVISED) |
| 2. Helper counts operative-state matches; rejects 0 or >1 distinct states | Done (both hook copies; `states_present` count, `> 1` → gap) |
| 3. Add focused dual-state tests against both hook copies (incl. `_requirement_sufficiency_section_gap` and full deny path) | Done — `test_dual_state_requirement_sufficiency_denied` (full deny path, x2 live/template) + extended `test_requirement_sufficiency_gap_helper` (asserts "multiple operative states") + new `_DUAL_STATE` fixture |
| 4. Preserve corrected three-path `target_paths` | Done — unchanged from `-007`/`-005` |
| 5. Re-run pytest, ruff check, ruff format check, SHA parity, applicability, clause, citation-freshness preflights | Done (evidence below) |

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-3439 backlog authority (P2 bridge-compliance improvement). Single-WI scope; `CLAUSE-VISIBILITY-BULK-OPS` not_applicable.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeded under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`).
- **`.claude/rules/file-bridge-protocol.md`** § "Mandatory Implementation-Start Authorization Metadata" — the exactly-one-operative-state contract this revision now enforces correctly at Write-time.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the gate protects bridge artifact integrity; this fix strengthens enforcement without altering INDEX or workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — project/WI/target-path metadata and governing specs concretely linked; `target_paths` enumerates all three authorized files.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all three `target_paths` are in-root under `E:\GT-KB`.

## Spec-to-Test Mapping

| Acceptance criterion (spec/clause) | Test | Result |
|---|---|---|
| **Dual-state section DENIED — exactly one operative state required (`-008` F1)** | **`test_dual_state_requirement_sufficiency_denied`** | **PASS (x2 live/template)** |
| **Gap helper returns "multiple operative states" for both-states input (`-008` F1)** | **`test_requirement_sufficiency_gap_helper` (extended)** | **PASS (x2)** |
| Implementation proposal lacking `## Requirement Sufficiency` DENIED | `test_missing_requirement_sufficiency_denied` | PASS (x2) |
| Placeholder-only section DENIED | `test_placeholder_requirement_sufficiency_denied` | PASS (x2) |
| Section without operative-state phrase DENIED | `test_requirement_sufficiency_without_operative_state_denied` | PASS (x2) |
| Substantive section (state 1) ALLOWED | `test_substantive_requirement_sufficiency_allowed` | PASS (x2) |
| Second operative state (state 2) ALLOWED (GO constraint 3) | `test_second_operative_state_allowed` | PASS (x2) |
| REVISED status also gated — shared status trigger (GO constraint 5) | `test_revised_status_also_gated` | PASS (x2) |
| implementation_report NOT gated (GO constraint 2) | `test_implementation_report_with_target_paths_not_gated` | PASS (x2) |
| Non-implementation proposal (no target_paths) NOT gated | `test_non_implementation_proposal_not_gated` | PASS (x2) |
| Verdict files exempt | `test_verdict_files_exempt` | PASS (x2) |
| Predicate covers both proposal tokens, excludes reports (GO constraint 1) | `test_bridge_kind_predicate_covers_both_proposal_tokens` | PASS (x2) |
| Shared status/predicate constants (GO constraint 5) | `test_shared_status_trigger_constant` | PASS (x2) |
| Template ↔ .claude byte-identity (GO constraint 6) | `test_template_and_active_hook_byte_identical` | PASS (x1) |

## Verification Evidence (exact commands + fresh results, this session 2026-06-14T18:5xZ)

- Focused WI-3439 suite (was 25; now 27 — the dual-state deny test adds 2 parametrized instances):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q --tb=short
27 passed, 1 warning in 9.98s
```

- Ruff lint (all three `target_paths`):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py
All checks passed!
```

- Ruff format gate (separate from lint):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check ...
3 files already formatted
```

- Byte-identity (GO constraint 6) — new SHA after the behavioral fix:

```text
sha256  .claude/hooks/bridge-compliance-gate.py                    7b5d734a512e00fcb4ca83a858b7092a4fe6e01f8c4f3f8a4262577ff5b5bf94
sha256  groundtruth-kb/templates/hooks/bridge-compliance-gate.py   7b5d734a512e00fcb4ca83a858b7092a4fe6e01f8c4f3f8a4262577ff5b5bf94
identical: True
```

- Applicability preflight:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: [ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001]  (advisory-only)
packet_hash: sha256:87cec0fd8336e321ebd8d21c4a82306ee33172e04cf2ae6dcf62bf6ef0a9a9db
```

- Clause preflight:

```text
Clauses evaluated: 5
must_apply: 2, may_apply: 3, not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
exit: 0
```

- Citation freshness:

```text
No stale cross-thread citations detected.
```

### Pre-existing/environmental failures (NOT caused by this change)

As documented in `-003`/`-007` and acknowledged non-blocking in `-004`: a combined subprocess run of older bridge-compliance / implementation-authorization tests reports failures whose deny-reason is the work-intent claim gate or the WI-4534 claim-role-eligibility guard, both firing in `main()`/`acquire()` BEFORE `_deny_reason_for_content`. Zero failures reference `WI-3439` or `Requirement Sufficiency`.

## Risk / Rollback

- **Risk: low.** The change tightens an existing Write-time gate (rejects an additional invalid shape: dual operative state). No previously-valid single-state proposal becomes denied — `test_substantive_requirement_sufficiency_allowed` and `test_second_operative_state_allowed` confirm both single states still pass.
- **Rollback:** revert the two state regexes + `REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES` + the `states_present` counting in `_requirement_sufficiency_section_gap` (both copies); remove `_DUAL_STATE`, `test_dual_state_requirement_sufficiency_denied`, and the gap-helper dual-state assertion. No migration, schema change, or KB mutation.

## Recommended Commit Type

`feat:` — strengthens the bridge-compliance-gate enforcement capability (rejects a previously-accepted invalid shape) plus a net-new negative test. Net-new helper logic in the gate (both copies) + new test coverage; no restructure-only or pure-repair change.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new AskUserQuestion required to file or verify.

- **`DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION`** — owner AUQ (2026-06-14) authorizing WI-3439 under `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001` (allows `source`, `test_addition`, `hook_upgrade`, `config`; forbids formal-artifact + narrative-artifact mutation). The dual-state-rejection fix and its test are `source` + `test_addition` work squarely inside this scope; no formal-artifact, narrative-artifact, or KB mutation.
- The `-008` NO-GO explicitly recorded "Owner Action Required: None — within the existing PAUTH and corrected target-path envelope."

## Prior Deliberations

- **NO-GO verdict `-008`** (Codex, harness A) — the verification NO-GO whose sole blocking finding (F1, dual operative state accepted) this report remediates with state-counting enforcement + dual-state tests.
- **Implementation report `-007`** (Prime Builder, harness B) — the prior re-submission (corrected `target_paths`); behavior was byte-identical to `-003` and is now superseded by the state-counting fix.
- **GO verdict `-006`** (Loyal Opposition, Ollama harness D) — re-GO of REVISED proposal `-005`.
- **REVISED proposal `-005`** (Prime Builder, harness B) — the target-path metadata correction carried forward.
- **GO verdict `-002`** (Codex, harness A) — the six mandatory implementation constraints, all still honored (the state-counting fix does not alter scoping, report-exemption, shared-status-trigger, or deployment-parity behavior).
- _Live semantic deliberation search not run during authoring; prior-decision context gathered from the live bridge thread (`-001`…`-008`), the live gate source, and the file-bridge-protocol exactly-one-operative-state contract._

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
