NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-30T03-55-00Z-prime-builder-E-s515
author_model: Cursor Agent
author_model_version: composer
author_model_configuration: Cursor interactive Prime Builder session S515; owner approved bridge filing for WI-4928 + WI-4930

# gtkb-wi4928-wi4930-harness-parity-role-readiness — Correct and integrate harness parity role-readiness gates

bridge_kind: prime_proposal
Document: gtkb-wi4928-wi4930-harness-parity-role-readiness
Version: 001
Author: Prime Builder (Cursor, harness E)
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4928
Related Work Items: WI-4930

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity.py", "config/agent-control/harness-capability-registry.toml", ".claude/skills/harness-parity-review/SKILL.md", "scripts/session_self_initialization.py", "scripts/harness_parity_phase2.py", "scripts/parity_discovery_diff.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

implementation_scope: source,test_addition,config,skill
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Umbrella bridge proposal for the **role-readiness false-positive remediation program** captured in MemBase as **WI-4928** (phase-1 checker correctness) and **WI-4930** (post-fix orchestration/integration). Cursor E and Codex A audits found that `scripts/check_harness_parity.py` and the `harness-parity-review` skill are useful **static catalog drift** controls but are **not** valid end-to-end verifiers of whether harnesses can fill Prime Builder or Loyal Opposition roles.

**Slice A (WI-4928)** repairs false positives and role-scoping defects inside the phase-1 checker and refreshes skill inputs. **Slice B (WI-4930)** depends on Slice A and wires corrected semantics into startup disclosure, fleet role-coverage, phase-2/discovery-diff workflow, and operator-facing terminology so PASS/WARN cannot be misread as operational role fitness.

Project note: `PROJECT-GTKB-CROSS-HARNESS-PARITY` shows `status=retired` after the six-slice program completed, but **WI-4928** and **WI-4930** remain active project members under standing backlog authority and **PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION** (`status=active`). This proposal does not reopen the retired program umbrella; it implements two new defect-class work items already filed in MemBase.

## Bulk-Operation Inventory and Review Packet

Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`, this umbrella
touches multiple harness surfaces and registry rows. Inventory at filing time:

| Class | Population | Slice |
|---|---|---|
| Phase-1 checker | `scripts/check_harness_parity.py`, `platform_tests/scripts/test_check_harness_parity.py` | A (WI-4928) |
| Capability registry | `config/agent-control/harness-capability-registry.toml` shared-hook rows + `[[parity_waivers]]` | A |
| Skill + adapters | `.claude/skills/harness-parity-review/SKILL.md` and generated `.codex`/`.cursor`/`.agent` adapters | A + B |
| Startup integration | `scripts/session_self_initialization.py` (`_harness_parity_status`) | B (WI-4930) |
| Operational evaluator | `scripts/harness_parity_phase2.py` (workflow integration only) | B |
| Discovery diff | `scripts/parity_discovery_diff.py` (workflow citation; expansion optional) | B |
| Harness fleet | `codex`, `claude`, `cursor` (PB); `antigravity`, `ollama`, `openrouter` (LO) per `harness-state/harness-registry.json` | A + B |

**Review packet:** Cursor E + Codex A independent audits (2026-06-30) documented
false-PASS on ollama/openrouter hook rows, missing assigned-role scoping, unused
waivers, stale skill authority path, and startup `harness=all` collapse. MemBase
authority: WI-4928 (checker) + WI-4930 (orchestration, `depends_on_work_items=["WI-4928"]`).
No Phase/Path deferral — both slices are in-scope for this GO request; discovery-diff
population expansion is the only optional deferral called out in Risks.

## Defect Evidence (2026-06-30)

| Finding | Live symptom |
|---|---|
| Manifest hook synthesis | `ollama --role loyal-opposition --show-pass` reports PASS on `.claude/hooks/*.py` and `.codex/gtkb-hooks/*.cmd` via `check_harness_parity.py:327-334` although API harness wrappers do not invoke those surfaces |
| Assigned-role scoping | `--role prime-builder` evaluates **all** active harnesses, not only PB-assigned harnesses from `harness-state/harness-registry.json` |
| Native semantics | `status=native` + file exists → PASS; no hook registration / invocation / enforcement proof |
| Waivers unused | `[[parity_waivers]]` validated by `--validate-schema` but not applied during evaluation; Claude shows three `MISSING` shared-hook rows despite owner-approved waivers |
| Stale skill | `harness-parity-review` still references absent `harness-state/role-assignments.json` |
| Startup noise | `session_self_initialization._harness_parity_status` collapses cursor/antigravity/ollama/openrouter to `harness=all`, inflating startup WARN |
| Repo test failure | `test_repository_registry_has_no_unclassified_missing_rows` fails on live registry |
| Phase-2 orphan | `scripts/harness_parity_phase2.py` is closer to operational readiness but not on the skill's required command path |

Verification commands used during diagnosis:

```text
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness ollama --role loyal-opposition --show-pass
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
python scripts/harness_parity_phase2.py --project-root . --format markdown
```

## Specification Links

- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity schema, applicability rule, waiver store, discovery-diff wiring expectations.
- `ADR-CROSS-HARNESS-PARITY-001` — semantic capability equivalence across harnesses; registry is not sole existence authority for hooks.
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` — governed harness parity surfaces and enforcement posture.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected edits require bridge GO + implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH / project / work item / target paths in proposal header.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-to-verification mapping in report and verdict.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — focused pytest + command evidence for each slice.
- `GOV-STANDING-BACKLOG-001` — WI-4928 and WI-4930 are durable backlog authority for this remediation.

## Prior Deliberations

- Owner directive 2026-06-30 — create WI-4928 after Codex role-readiness audit; companion WI-4930 filed S515 for integration gaps.
- `bridge/gtkb-harness-parity-baseline-001.md` — original phase-1 checker intent (catalog parity, not runtime readiness).
- `bridge/gtkb-harness-parity-phase-2-baseline-evaluator-001.md` — phase-2 operational evaluator (WI-4900); complementary to this work.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — hook discovery-diff; currently Claude/Codex hook-config scoped.
- `bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-003.md` — recent parity discovery-diff false-positive remediation precedent.

## Owner Decisions / Input

Owner approved filing this bridge proposal linking WI-4928 and WI-4930 (2026-06-30, S515). No new AUQ is required for proposal filing. Implementation remains subject to LO GO and implementation-start authorization per standard bridge protocol.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped implementation. Cross-harness parity ADR/DCL and the MemBase WI descriptions cover the defects; this proposal decomposes already-captured gaps into two bounded implementation slices without reopening net-new product requirements.

## Proposed Implementation

### Slice A — WI-4928: Phase-1 checker correctness

1. **Remove manifest hook false-PASS synthesis** (`check_harness_parity.py:327-334`):
   - Do **not** synthesize `status=native` for `kind=hook` from `canonical_source` when only a skill adapter manifest exists.
   - For API/provider harnesses (ollama, openrouter) and any harness without a registered hook wiring surface, emit `UNSUPPORTED`, `OWNER_ACTION_REQUIRED`, or explicit registry `unsupported` rows — not PASS on Claude/Codex canonical paths.

2. **Assigned-role harness scoping**:
   - When `--role` is provided, intersect selected harnesses with `harness-state/harness-registry.json` role sets (READ vocabulary includes `acting-prime-builder` normalization per `scripts/harness_roles.py`).
   - Preserve `--all` / `--harness` explicit overrides for diagnostic runs.
   - Add tests proving antigravity is excluded from `--role prime-builder` default scoping and vice versa.

3. **Apply typed waivers during evaluation**:
   - Consult `load_parity_waivers()` when classifying harness×capability results; map approved waivers to non-failing states (document chosen mapping in code/tests).
   - Restore green `test_repository_registry_has_no_unclassified_missing_rows` or update test contract deliberately with spec citation if intentional behavior changes.

4. **Harness-parity-review skill refresh**:
   - Replace `role-assignments.json` with `harness-state/harness-registry.json`.
   - Document all six harness surfaces and the distinction between phase-1 checker vs phase-2 evaluator commands.
   - Regenerate Codex/Cursor/Antigravity adapters after canonical skill edit.

5. **Registry hygiene (minimal)**:
   - Where waivers are insufficient, add explicit per-harness `unsupported` registry rows instead of leaving `MISSING` unclassified rows (e.g. Claude vs Codex-only hook adapters).

### Slice B — WI-4930: Orchestration and role-readiness integration (depends on Slice A)

1. **Startup harness scoping** (`session_self_initialization._harness_parity_status`):
   - Stop collapsing cursor/antigravity/ollama/openrouter to `harness=all`.
   - Run parity against the resolved interactive harness name + role profile; disclose scope in compact startup text.

2. **Fleet role-coverage gate**:
   - Add checker mode (e.g. `--role-coverage` or dedicated function) proving each operating role (`prime-builder`, `loyal-opposition`) is fillable by **at least one** active harness for all `parity_class=required` capabilities after Slice A semantics.
   - Reuse or extend `platform_tests/scripts/test_cross_harness_protocol_parity.py` rather than duplicating topology logic.

3. **Consume `resolve_applicability()` in harness population selection**:
   - `role-relative` capabilities check only harnesses holding matching assigned roles; `universal` capabilities check the applicable active population per DCL applicability rule.

4. **Integrate phase-2 + discovery-diff into review workflow**:
   - Update `harness-parity-review` required commands to include `harness_parity_phase2.py` and, where hook-config exists, `parity_discovery_diff.py`.
   - Document API/provider harness hook evidence model (wrapper argv / governed helper references), not canonical-source aliasing.
   - Optionally expand discovery-diff population beyond Claude/Codex when harness hook-config files exist — or document explicit waiver/deferral if out of slice budget.

5. **Operator disclosure split**:
   - Startup report / skill report format must label phase-1 result as **catalog parity** and phase-2 result as **operational readiness** so WARN on degraded adapters is not read as role unfitness.

### Slice sequencing and commits

- Implement and verify **Slice A** first; file implementation report `-002` (or slice-specific report) and obtain LO VERIFIED before Slice B protected edits unless LO GO explicitly authorizes combined landing (default: sequential).
- Prefer two focused commits: `fix: WI-4928 harness parity checker role scoping` then `feat: WI-4930 harness parity role-readiness orchestration`.

## Cross-Harness Disposition

| Surface | Slice A | Slice B |
|---|---|---|
| `scripts/check_harness_parity.py` | **Yes** | **Yes** (role-coverage / applicability) |
| `platform_tests/scripts/test_check_harness_parity.py` | **Yes** | **Yes** |
| `config/agent-control/harness-capability-registry.toml` | **Yes** (explicit unsupported rows as needed) | No unless orchestration needs registry labels |
| `.claude/skills/harness-parity-review/SKILL.md` + adapters | **Yes** | **Yes** |
| `scripts/session_self_initialization.py` | No | **Yes** |
| `scripts/harness_parity_phase2.py` | No | **Yes** (workflow integration only; no semantic rewrite) |
| `scripts/parity_discovery_diff.py` | No | **Maybe** (expand population or document deferral) |
| Claude/Codex/Cursor hook configs | No direct edits in Slice A | No unless discovery-diff expansion requires registry-unify follow-up |

## Spec-Derived Verification Plan

| Spec / surface | Verification |
|---|---|
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Waiver application + applicability-aware populations; `python scripts/check_harness_parity.py --validate-schema` → OK |
| `ADR-CROSS-HARNESS-PARITY-001` | API harnesses no longer PASS on unwired canonical hook paths; discovery-diff or documented equivalent remains honest |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation-start packet before protected edits; cite hash in reports |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4928-wi4930-harness-parity-role-readiness` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Slice A/B pytest + command matrix below |

Concrete commands after implementation:

```text
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short
python -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short
python scripts/check_harness_parity.py --harness ollama --role loyal-opposition --json
python scripts/check_harness_parity.py --harness cursor --role prime-builder --json
python scripts/check_harness_parity.py --all --markdown
python scripts/harness_parity_phase2.py --project-root . --format markdown
python scripts/session_self_initialization.py --harness-name cursor --emit-report
```

Slice A acceptance highlights:

- `ollama` / `openrouter` no longer PASS unwired Claude/Codex hook files under LO role scope.
- `test_repository_registry_has_no_unclassified_missing_rows` passes.
- Assigned-role scoping tests pass.

Slice B acceptance highlights:

- Cursor startup parity uses `harness=cursor`, not `all`.
- Role-coverage gate passes on live registry for both operating roles.
- Skill documents three-command path: phase-1 checker, phase-2 evaluator, optional discovery-diff.

## Risks / Rollback

- **Risk:** Tightening checker semantics may surface new WARN/FAIL across harnesses previously false-PASS. **Mitigation:** typed waivers + explicit `unsupported` registry rows; sequential Slice A before startup integration.
- **Risk:** Slice B discovery-diff expansion could broaden scope into hook-config rewrites. **Mitigation:** default to workflow/documentation integration; defer hook-population expansion to follow-on WI if LO judges it too large for WI-4930.
- **Rollback:** Revert Slice B then Slice A commits; registry TOML changes revert with Slice A.

## Out of Scope

- Runtime dispatch/auth smoke automation beyond existing `verify_*_dispatch.py` scripts (may be cited as manual supplemental evidence only).
- Rewriting `PROJECT-HARNESS-PARITY-PHASE-2` evaluator dimensions (WI-4900 family).
- Reactivating retired `PROJECT-GTKB-CROSS-HARNESS-PARITY` program status in MemBase (not required for these WIs).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
