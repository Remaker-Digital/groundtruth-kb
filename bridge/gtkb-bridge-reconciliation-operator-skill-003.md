REVISED

# gtkb-bridge-reconciliation-operator-skill — Bridge Reconciliation Operator Skill + Runbook (no-index, re-scoped WI-4237) — REVISED after NO-GO -002

bridge_kind: prime_proposal
Document: gtkb-bridge-reconciliation-operator-skill
Version: 003
Responds to NO-GO: bridge/gtkb-bridge-reconciliation-operator-skill-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-06-20 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 34407a42-8900-4908-a72a-3ed27a0df984
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: claude-code

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4237

target_paths: [".claude/skills/bridge-reconciliation/SKILL.md", ".codex/skills/bridge-reconciliation/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/bridge-reconciliation/SKILL.md", ".agent/skills/MANIFEST.json", ".api-harness/skills/bridge-reconciliation/SKILL.md", ".api-harness/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "scripts/wrap_scan_reconciliation.py", "scripts/bridge_backlog_terminal_reconciliation.py", "platform_tests/scripts/test_bridge_reconciliation_skill.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Response to NO-GO -002 (FINDING-P1-001)

The NO-GO correctly found that the `-001` verification plan required the whole-repository `platform_tests/scripts/test_api_skill_adapters.py` to pass, but that test fails on **pre-existing** `.api-harness` adapter drift in files outside this bridge's `target_paths` (`.api-harness/skills/bridge/SKILL.md`, `kb-session-wrap/SKILL.md`, `proposal-review/SKILL.md`, and `MANIFEST.json` — "would update 4 files"). This revision takes Codex's **Path 2 (keep WI-4237 narrow)**:

1. **Verification narrowed.** The whole-repo SHA-parity gate `test_api_skill_adapters.py` is removed from the WI-4237 verification plan. API generator behavior for the new adapter is instead proven by `platform_tests/scripts/test_generate_api_skill_adapters.py` (generator-unit coverage) plus the new cross-harness discoverability test. The new `bridge-reconciliation` adapter is still generated and registered; only the verification *instrument* changed.
2. **Pre-existing drift deferred.** The unrelated `.api-harness` adapter drift is deferred to a separate standing backlog item, **WI-4711** ("Repair pre-existing .api-harness skill adapter drift"), captured 2026-06-20, citing this thread. WI-4237 does not repair it and does not add the drifted files to `target_paths`.
3. **No scope creep.** `target_paths` is unchanged from `-001`: only the new `bridge-reconciliation` SKILL.md per harness, the shared `MANIFEST.json` registrations, the capability registry, the cleanup targets, and the new test. The drifted adapter files remain out of scope.

The implementation generates only the new adapter; it must not regenerate or "repair" the three drifted adapters (that is WI-4711's job). If the API generator cannot register the new adapter without touching drifted files, the implementation will register the new adapter's manifest entry without rewriting the drifted SKILL.md bodies, and the post-implementation report will state exactly which `.api-harness` files it wrote.

### Standing-backlog bulk-operation visibility (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS)

This proposal performs no bulk backlog transition itself; it documents one. For visibility of the bulk reconciliation correction the skill wraps (`bridge_verified_backlog_reconciler.py --apply`): the skill mandates that the operator first run the read-only `--dry-run --json` to produce an **inventory** of candidate resolutions (the operator **review packet**), then present exactly one owner-approval `AskUserQuestion` (the owner-approval packet, subject to the `formal-artifact-approval` gate) before any bulk state transition, under a live project-authorization envelope + implementation-start packet. Out-of-scope findings are recorded as deferred-decision markers (**DECISION DEFERRED**), e.g. the deferred `.api-harness` drift captured as WI-4711. The skill forbids silent/unattended bulk backlog mutation; one-class-at-a-time correction is the default.

## Summary

Re-scoped WI-4237 per owner AskUserQuestion decision `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` (Option A of three). WI-4237 originally called for an operator skill/runbook wrapping the `gt bridge reconcile audit | index-chain | packet` commands. Those commands no longer exist: the governed 2026-06-16 "no-index bridge closeout" (commit `0f96c4e6e`; thread `gtkb-retired-bridge-artifact-runtime-source-cleanout`) deleted the INDEX-centric reconciliation tooling after `bridge/INDEX.md` was retired in the 2026-06-15 TAFE/dispatcher cutover. This proposal re-scopes WI-4237 to a no-index-era operator skill that documents and wraps the **surviving** reconciliation surface, and folds in cleanup of the broken leftover from that closeout.

The deliverable is a canonical operator skill `.claude/skills/bridge-reconciliation/SKILL.md` (which doubles as the runbook) guiding an agent through: (1) read-only assessment, (2) finding classification, (3) one-class-at-a-time correction, (4) presenting exactly one owner `AskUserQuestion` before any mutation, and (5) preserving the bridge / project-authorization / implementation-start gates (no-bulk-mutation), citing command names. The three adapter generators mirror the canonical skill to `.codex/`, `.agent/`, and `.api-harness/` (registering it in their `MANIFEST.json` and `config/agent-control/harness-capability-registry.toml`). Cleanup removes the broken `scripts/bridge_backlog_terminal_reconciliation.py` (its line 15 `import`s the deleted `bridge_reconciliation_audit` module, raising `ModuleNotFoundError`) and corrects the stale `gt bridge reconcile audit` doc reference in `scripts/wrap_scan_reconciliation.py`. A focused discoverability test proves the skill is present across all harness skill surfaces.

The surviving no-index reconciliation surface the skill wraps (all read-only unless an apply flag is passed):

- `gt bridge dispatch health` / `gt bridge dispatch status` — bridge dispatch eligibility/health.
- `python scripts/wrap_scan_reconciliation.py --json` — report-only session-wrap reconciliation scan (no-index adapted; WI-4238).
- `python scripts/bridge_verified_backlog_reconciler.py --dry-run | --apply | --repair-overbroad [--json]` — resolves open work items whose linked bridge threads are all latest VERIFIED with explicit parent evidence (`DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`), now including the WI-4704 umbrella auto-closure and canonical parent-evidence relaxation paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the skill operates on the bridge protocol surface and must read the no-index canonical bridge state (dispatcher/TAFE + status-bearing versioned files), never aggregate queue artifacts.
- `GOV-STANDING-BACKLOG-001` — the reconciliation resolves open work items against their VERIFIED bridge threads; the MemBase `work_items` backlog is the governed authority the skill defers to.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the skill mandates fresh reads from canonical surfaces, not cached startup reports or derived counts.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — corrective (mutating) steps documented by the skill proceed only under a live project authorization; the skill preserves this gate.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — the skill's no-bulk-mutation policy requires a live authorization envelope before any `--apply` correction.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the skill is a durable governed artifact (operator runbook) wrapping the reconciliation tooling rather than transient chat guidance.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the development project is a network of durable artifacts; this skill converts the reconciliation operator workflow into a durable, discoverable artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — bridge/backlog reconciliation drift is an artifact-lifecycle signal the skill surfaces and routes to one-class-at-a-time correction.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every governing spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below maps each linked spec to executed tests/commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries `Project` / `Work Item` / `Project Authorization` metadata.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the skill is mirrored across harnesses (Claude/Codex/Antigravity/API) for parity via the adapter generators.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — the operator skill must be available to all capable harnesses that can hold Prime Builder / Loyal Opposition roles.

## Prior Deliberations

- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` — the owner decision authorizing this re-scope (Option A). This proposal implements it directly.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — owner authorization of `PROJECT-GTKB-BRIDGE-RECONCILIATION` and WI-4234..4238; `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` derives from it and explicitly authorizes "bridge reconciliation operator skill/runbook updates".
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — authority for the surviving `bridge_verified_backlog_reconciler.py` that the skill wraps.
- `DELIB-20261048` — Bridge/Backlog Reconciliation Drift Advisory; the origin advisory for the whole project, defining the drift the skill helps an operator correct.
- `DELIB-20263291` — WI-4238 wrap-scan VERIFIED; the adapted no-index `wrap_scan_reconciliation.py` the skill also wraps.
- Bridge thread `gtkb-retired-bridge-artifact-runtime-source-cleanout` — the governed no-index closeout that deleted the original INDEX-centric tooling; this re-scope reconciles that supersession into WI-4237.

## Owner Decisions / Input

- `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL` — owner `AskUserQuestion`, 2026-06-20. Owner selected **Option A "Re-scope to no-index"** over Option B "Retire as superseded" and Option C "Restore full deleted tooling". This authorizes the re-scope direction and the filing of this proposal. It does **not** waive Loyal Opposition review, bridge `GO`, the implementation-start packet, or post-implementation verification.
- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` — owner authorization of `PROJECT-GTKB-BRIDGE-RECONCILIATION` and WI-4234..4238, the basis of the active `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` (which names "bridge reconciliation operator skill/runbook updates" within scope).

## Requirement Sufficiency

Existing requirements sufficient. Governing requirements: (a) WI-4237's acceptance summary — "a skill/runbook exists for bridge reconciliation; it invokes the reusable CLI/check, documents one-class-at-a-time correction packets, requires owner/bridge gates for mutation, and includes tests or manifest checks proving the skill is discoverable"; (b) owner re-scope decision `DELIB-2026-06-20-WI4237-RESCOPE-NO-INDEX-OPERATOR-SKILL`; and (c) `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION`, which authorizes operator-skill/runbook updates for WI-4234..4238. The acceptance summary maps cleanly onto the surviving no-index tooling; no new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Linked specification(s) | Verification (test / command + expected result) |
| --- | --- |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | New `platform_tests/scripts/test_bridge_reconciliation_skill.py` asserts the `bridge-reconciliation` skill exists and is discoverable in `.claude/`, `.codex/`, `.agent/`, `.api-harness/` skill surfaces; the Codex + Antigravity adapter-parity tests pass; the **API generator-unit** test `test_generate_api_skill_adapters.py` passes for the new adapter. The whole-repo SHA-parity gate `test_api_skill_adapters.py` is intentionally NOT required here — its current failure is unrelated pre-existing drift deferred to WI-4711. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The new test asserts the SKILL.md positively cites the surviving no-index fresh-read surfaces (`gt bridge dispatch health/status`, `wrap_scan_reconciliation.py`, `bridge_verified_backlog_reconciler.py --dry-run`) and does not instruct use of the retired `gt bridge reconcile` commands or `bridge/INDEX.md` as live state. |
| `GOV-STANDING-BACKLOG-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verification runs `bridge_verified_backlog_reconciler.py --dry-run --json` and confirms exit 0 / `errors: []`, demonstrating the documented assessment step works against live state. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The new test asserts the SKILL.md contains the no-bulk-mutation + gate-preservation language (live PAUTH + implementation-start packet + exactly-one `AskUserQuestion` before any `--apply`). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `pytest` of the new + Codex/Antigravity/API generator + wrap-scan tests passes; `ruff check` and `ruff format --check` pass on changed Python; this proposal carries full spec/project linkage (verified by the applicability + clause preflights). |
| Cleanup (broken leftover + stale doc ref) | `grep` confirms no module imports the removed `bridge_backlog_terminal_reconciliation`; `test_wrap_scan_reconciliation.py` still passes after the doc-ref fix. |

Commands (repo venv interpreter for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_reconciliation_skill.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py platform_tests/scripts/test_wrap_scan_reconciliation.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/wrap_scan_reconciliation.py platform_tests/scripts/test_bridge_reconciliation_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/wrap_scan_reconciliation.py platform_tests/scripts/test_bridge_reconciliation_skill.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_verified_backlog_reconciler.py --dry-run --json
```

## Risk / Rollback

Risk is low. The deliverable is operator documentation (skill/runbook) plus generated harness mirrors, a focused discoverability test, removal of an already-broken script, and a one-line doc-reference fix. No runtime or protocol behavior changes; the wrapped reconciliation tooling is unchanged. The removed `scripts/bridge_backlog_terminal_reconciliation.py` is already non-functional (it imports a module deleted in commit `0f96c4e6e`), so deleting it cannot regress a working surface. The `wrap_scan_reconciliation.py` change is a comment/doc-string reference only and is covered by its existing test. **Deferred drift:** the unrelated pre-existing `.api-harness` adapter drift (WI-4711) is explicitly out of scope and is neither repaired nor worsened by this change; the implementation writes only the new adapter's files. Rollback: a single revert of the implementation commit restores the prior tree. No data/KB rollback is required (`kb_mutation_in_scope: false`); resolving WI-4237 itself is a separate post-VERIFIED step.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-bridge-reconciliation-operator-skill`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` — the dominant change is a net-new operator skill + runbook + discoverability test (a new capability surface), with incidental chore-class cleanup (broken-script removal, doc-ref fix) folded in.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
