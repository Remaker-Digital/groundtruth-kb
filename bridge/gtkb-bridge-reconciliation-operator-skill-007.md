REVISED

# gtkb-bridge-reconciliation-operator-skill — Bridge Reconciliation Operator Skill + Runbook — REVISED (Option B: all harnesses)

bridge_kind: prime_proposal
Document: gtkb-bridge-reconciliation-operator-skill
Version: 007
Responds to NO-GO: bridge/gtkb-bridge-reconciliation-operator-skill-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-06-21 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 34407a42-8900-4908-a72a-3ed27a0df984
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4237

target_paths: [".claude/skills/bridge-reconciliation/SKILL.md", ".codex/skills/**", ".agent/skills/**", ".api-harness/skills/**", "config/agent-control/harness-capability-registry.toml", "scripts/wrap_scan_reconciliation.py", "platform_tests/scripts/test_bridge_reconciliation_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Re-scope WI-4237 to **Option B (deliver all harnesses now)** per owner AskUserQuestion 2026-06-21 (`DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES`), in response to the `-006` verification NO-GO. The bridge-reconciliation operator skill (delivered Claude-native at `-005`) is mirrored to `.codex`, `.agent`, and `.api-harness` via the registry-driven adapter generators, registered in `config/agent-control/harness-capability-registry.toml`, and the cross-harness discoverability test is extended to assert all four surfaces.

Because the adapter generators (`generate_codex/antigravity/api_skill_adapters.py`) are whole-repo / all-or-nothing, generating the new mirror in `.agent` and `.api-harness` also regenerates the pre-existing/concurrent drifted adapters there (`bridge`, `kb-session-wrap`, `proposal-review`). The owner's Option B decision **explicitly authorizes that in-thread drift repair, overriding GO Condition 2 of `-004`**, and **folds WI-4711 (.api-harness drift) and WI-4713 (cross-harness mirroring + .agent drift) into this work** — on VERIFIED, both are superseded/resolved as completed-by-WI-4237. `target_paths` is broadened to glob the three harness skill directories accordingly.

## Response to NO-GO -006

- **F1 (cross-harness scope):** Resolved by Option B — this proposal delivers the `.codex`/`.agent`/`.api-harness` mirrors + registry rather than narrowing. Owner approval recorded (`DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES`).
- **F2 (CRLF/whitespace churn in `scripts/wrap_scan_reconciliation.py`):** Already fixed — line endings normalized to LF across the session-touched files; `git diff --check` exits 0 (clean). The implementation step re-verifies this after generator runs.
- **F3 (live reconciler dry-run reproducibility):** The command completes locally with exit 0, `errors: []` (observed `candidate_count: 76`, `would_resolve_ids: []`). Codex's `-006` failure was a 300-second headless timeout under DB load on the 1.37 GB MemBase, not a code defect. The implementation report will include a compact observed-exit-0 summary; Loyal Opposition may need a longer timeout or a lower-load window to reproduce.

## Specification Links

- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — the operator skill must be available to all capable harnesses (the core of Option B).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — cross-harness adapter parity via the generators.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the skill operates on the no-index canonical bridge surface.
- `GOV-STANDING-BACKLOG-001` — the wrapped reconciler resolves backlog work items against VERIFIED threads.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the skill mandates fresh reads, not cached state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — work proceeds under `PAUTH-...-DETECTION-CORRECTION` + the owner Option B decision.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the broadened `target_paths` envelope; no-bulk-mutation discipline preserved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable governed operator artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — bridge/backlog reconciliation drift is the lifecycle signal the skill routes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — linkage + spec-derived verification.

## Prior Deliberations

- `DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES` — owner decision authorizing this broadened scope (Option B), the GO Condition 2 override, and folding in WI-4711/WI-4713. This proposal implements it.
- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` — owner re-scope of WI-4237 to the no-index operator skill.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — project authorization.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — authority for the reconciler the skill wraps.
- `bridge/gtkb-bridge-reconciliation-operator-skill-004.md` — GO with Condition 2 (drift deferral) now overridden by owner Option B.
- `bridge/gtkb-bridge-reconciliation-operator-skill-006.md` — the verification NO-GO this revision answers (F1/F2/F3).

## Owner Decisions / Input

- `DELIB-2026-06-21-WI4237-OPTION-B-DELIVER-ALL-HARNESSES` — owner AskUserQuestion (2026-06-21) selected **Option B "Deliver all harnesses now"** over A ("approve Claude-native, defer rest") and C ("keep open, verify later"). This authorizes: delivering all harness mirrors + registry in WI-4237; repairing the `.agent`/`.api-harness` adapter drift in-thread (overriding `-004` GO Condition 2); and superseding WI-4711 + WI-4713.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — project authorization basis.

## Requirement Sufficiency

Existing requirements sufficient. Governing: WI-4237 acceptance ("Codex/Claude-accessible skill/runbook ... discoverable"), the Option B owner decision, and `PAUTH-...-DETECTION-CORRECTION`. Option B makes the multi-harness delivery the accepted completion boundary; no new requirement is needed.

## Spec-Derived Verification Plan

| Linked specification(s) | Verification (test / command + expected result) |
| --- | --- |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_bridge_reconciliation_skill.py` (extended) asserts the `bridge-reconciliation` skill is present + discoverable in `.claude/`, `.codex/`, `.agent/`, `.api-harness/`; the whole-repo adapter parity tests `test_generate_codex_skill_adapters.py`, `test_generate_antigravity_skill_adapters.py`, `test_generate_api_skill_adapters.py`, and `test_api_skill_adapters.py` all pass (the latter now green because the drift is repaired). |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The test asserts the canonical SKILL.md cites the surviving no-index surfaces and never presents `gt bridge reconcile` or `bridge/INDEX.md` as live state; generated mirrors are compact pointers to the canonical source. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `bridge_verified_backlog_reconciler.py --dry-run --json` exits 0 / `errors: []` (compact evidence; runtime caveat per F3). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The test asserts the SKILL.md carries the no-bulk-mutation + gate-preservation contract. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + linkage DCLs | Full suite `pytest` passes; `ruff check` + `ruff format --check` clean; `git diff --check` exits 0 across all changed files; this proposal carries full spec/project linkage. |

Commands (repo venv interpreter):

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --update-registry
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_antigravity_skill_adapters.py --update-registry
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_api_skill_adapters.py --update-registry
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_reconciliation_skill.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py platform_tests/scripts/test_api_skill_adapters.py platform_tests/scripts/test_wrap_scan_reconciliation.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/wrap_scan_reconciliation.py platform_tests/scripts/test_bridge_reconciliation_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/wrap_scan_reconciliation.py platform_tests/scripts/test_bridge_reconciliation_skill.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_verified_backlog_reconciler.py --dry-run --json
```

## Risk / Rollback

The dominant change is generated adapter mirrors + a discoverability test + the registry entry. The in-thread drift repair (owner-approved) brings `.agent`/`.api-harness` adapters back into parity with their canonical sources — a net hygiene improvement, made deterministically by the canonical generators. Risk: the all-or-nothing generators could touch a concurrently-edited adapter; mitigated by re-running the whole-repo parity tests + `git diff --check` before reporting, and by the glob `target_paths` authorizing exactly the harness skill directories. Rollback: revert the implementation commit (removes the mirrors + registry entry, restores prior adapter state). No data/KB rollback (`kb_mutation_in_scope: false`); WI-4237 resolution + WI-4711/WI-4713 supersession are post-VERIFIED steps.

## Bridge Filing

Filed as the next status-bearing numbered bridge file for `gtkb-bridge-reconciliation-operator-skill`; append-only. Dispatcher/TAFE state + the numbered chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` — net-new cross-harness operator-skill mirrors + registry + discoverability test, with deterministic adapter-parity repair folded in.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
