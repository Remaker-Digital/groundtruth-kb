REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 58f826b2-6551-47df-8edf-ceba6461be29
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1M context window; explanatory output style; interrogative-default Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-SLICE-3-KB-WORK-ITEM-MIGRATION
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3455

# Skill Modernization Slice 3 — kb-work-item Migration — REVISED Reduced-Scope Proposal (verb only)

bridge_kind: prime_proposal

Document: gtkb-skill-modernization-slice-3-kb-work-item-migration
Version: 009 (REVISED — reduced scope)
Date: 2026-05-29 UTC
Supersedes: the full-scope -005 (GO at -006) after the -008 NO-GO on the -007 scope-reduced post-impl report.
Recommended commit type: feat

## Revision Claim

This REVISED proposal re-routes the owner-authorized scope reduction through the bridge protocol, per the -008 NO-GO Required Revisions (F1: "re-route the scope reduction through a fresh/revised bridge proposal that receives LO GO before terminal verification"; F2: "present a bridge-scoped waiver ... or resubmit ... after completing the consumer migration").

It narrows this slice's scope to **Half A only**: the `gt backlog add-work-item` deterministic GOV-12/13 CLI service + its spec-derived tests. **Half B** — the canonical skill rewrite, Codex/Antigravity adapter regeneration, registry source-hash refresh, Slice 0 skill-health regression, and harness-parity PASS — is **removed from this slice** and re-homed to the already-captured follow-on work item under PROJECT-GTKB-SKILL-MODERNIZATION (depends-on WI-3455).

The reduction is owner-authorized (AUQ S364: "Verb-only post-impl now; defer skill rewrite to clean tree", recorded in `memory/pending-owner-decisions.md`) and was forced by a tree-state blocker: the working tree carries 2+ parallel-session uncommitted skill edits, and the all-skills `--update-registry` generators cannot produce a cleanly-scoped, parity-passing Half-B commit until the S373 triage umbrella clears that parallel work. The verb (Half A) is independently valuable and verifiable: it is the deterministic service; any caller can now perform the GOV-12/13 chain without inline `db.insert_*`.

## Bridge INDEX Update (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This REVISED proposal is filed under `bridge/` and inserts a `REVISED` line at the top of this thread's entry in `bridge/INDEX.md` (the canonical workflow state), above the prior `NO-GO: -008` / `NEW: -007` lines. All prior versions are preserved; no bridge file is deleted or rewritten (append-only).

## target_paths (Half A only)

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_add_work_item.py` — the GOV-12/13 work-item-create verb (work item + linked test + required fail-closed phase).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — register `add-work-item` under the `backlog` command group.
- `platform_tests/scripts/test_cli_backlog_add_work_item.py` — spec-derived tests.

Explicitly OUT of scope for this slice (re-homed to the follow-on WI under PROJECT-GTKB-SKILL-MODERNIZATION): `.claude/skills/kb-work-item/SKILL.md`, both kb-work-item adapters + manifests, and `config/agent-control/harness-capability-registry.toml`.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the verb makes the WI+test+phase chain a deterministic CLI artifact. Primary; in PAUTH.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-first; in PAUTH.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — motivates the verb (the deterministic service). The *consumer migration* (rewriting the skill to call the verb) is explicitly out of this reduced scope and is the follow-on WI; this slice does not claim the skill-rewrite regression.
- GOV-12 — the verb creates a linked test in the same invocation.
- GOV-13 — the verb requires + fail-closed-validates a test-plan phase before any mutation; no orphan-test path.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — fail-closed attribution + dry-run no-mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the verb is application-agnostic (phase id is a required caller-supplied parameter); all artifacts in-root.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — metadata triple present; PAUTH active, includes WI-3455.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — every linked spec in THIS reduced scope has executed test coverage (mapping below); no deferred linked spec remains in scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — canonical bridge protocol; INDEX authoritative.

## Requirement Sufficiency

Existing requirements sufficient. The umbrella scoping (GO at -004) authorizes the kb-* CLI verb. GOV-12/GOV-13 are existing specs, fully covered by the verb's tests. No new requirement is needed for the reduced scope.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — motivating principle.
- `DELIB-S364-KB-WORK-ITEM-MIGRATION-SLICE-PAUTH` and `DELIB-S364-KB-WORK-ITEM-MIGRATION-PAUTH-REGISTRY-AMENDMENT` — owner authorizations for the slice + PAUTH v2.
- `bridge/gtkb-skill-modernization-slice-3-kb-work-item-migration-008.md` (Codex NO-GO) — required this re-scope through the bridge before verification; this REVISED proposal is the response.
- The owner AUQ "Verb-only post-impl now; defer skill rewrite to clean tree" (recorded in `memory/pending-owner-decisions.md`) authorizes the reduction; the deferred Half B is tracked as the follow-on WI under PROJECT-GTKB-SKILL-MODERNIZATION.
- No prior deliberation rejected the reduced-scope approach.

## Implementation Plan

Half A is already implemented (the verb + tests exist and pass); this REVISED proposal formalizes the reduced bridge scope so the subsequent post-impl report can verify it. No further Half-A code change is proposed beyond what exists. The verb composes `add_backlog_item` (work item + fail-closed attribution), `db.insert_test` (GOV-12 linked test), and an append-only `test_plan_phases.test_ids` update (GOV-13), with `--test-plan-phase` required and pre-validated for non-dry-run creation.

## Spec-to-Test Mapping (reduced scope — all executed)

Command (reproducible temp base per -008 F3): `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cli_backlog_add_work_item.py -v --basetemp E:\GT-KB\.pytest-tmp` → **7 passed**.

| Linked Spec | Test | Result |
|---|---|---|
| GOV-12 | `test_creates_work_item_test_and_phase_assignment` | PASS |
| GOV-12 | `test_test_links_to_source_spec_by_default` | PASS |
| GOV-13 | `test_missing_phase_fails_closed` | PASS |
| GOV-13 | `test_invalid_phase_fails_closed` | PASS |
| GOV-13 | `test_phase_assignment_appends_test_id_append_only` | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_dry_run_writes_nothing` | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_fail_closed_attribution` | PASS |

Every linked specification in this reduced scope has executed coverage. `DELIB-S312`'s consumer-migration regression is NOT in this scope (it belongs to the follow-on WI); the verb itself satisfies the deterministic-service principle.

## Acceptance Criteria (reduced scope)

- [ ] `gt backlog add-work-item` enforces GOV-12 + GOV-13 (required, fail-closed, pre-validated phase); no orphan-test path.
- [ ] Verb reuses `add_backlog_item`; fail-closed attribution; phase id parameterized (no PLAN-001 hardcoding).
- [ ] 7/7 tests pass (with the reproducible `--basetemp` command); ruff clean on the new module + test.
- [ ] Implementation confined to the three Half-A target_paths; applicability + clause preflights pass.
- [ ] Half B confirmed out of this slice's scope and tracked as the follow-on WI.

## Risk / Rollback

- **Risk:** LOW for the reduced scope — additive CLI verb + tests; no skill/adapter/registry mutation in this slice; `gt backlog add` and existing skill behavior unaffected. The deferred Half B leaves the kb-work-item skill's inline-db bypass in place until the follow-on; that residual governance risk is owner-accepted (verb-only AUQ) and tracked.
- **Rollback:** `git checkout` the three Half-A files. MemBase writes are append-only.

## Owner Decisions / Input

- **Scope the migration slice** (AskUserQuestion, S364): owner authorized the verb; PAUTH v1.
- **PAUTH amendment** (AskUserQuestion, S364): owner amended PAUTH to v2 (config_registry_edit).
- **Contamination disposition** (AskUserQuestion, S364): owner chose "Verb-only post-impl now; defer skill rewrite to clean tree" — the authority for this reduced scope. Half B is the follow-on WI under PROJECT-GTKB-SKILL-MODERNIZATION.
- No new owner decision is required to review this reduced-scope REVISED proposal.

## Notes for Loyal Opposition

- This addresses -008 F1 by routing the scope reduction through a REVISED proposal for a fresh GO before any verification request. On GO, the post-impl report will verify Half A only (the 7 tests + ruff with the reproducible `--basetemp` command per -008 F3).
- This addresses -008 F2 by removing `DELIB-S312`'s consumer-migration regression from this slice's linked-and-must-verify set; no deferred linked spec remains in the reduced scope. The consumer migration is the follow-on WI.
- AXIS-1 dispatchable review; no owner-AUQ-mid-stream needed for the verdict.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
