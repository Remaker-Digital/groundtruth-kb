NEW

# Post-Implementation Report — GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 (Slice A.1)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-narrative-artifact-approval-extension-001`
**Prior GO:** `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (on `-003` REVISED-1)
**Implementation status:** Slice A.1 (operational layer) complete; Slice A.2 (governance metadata) explicitly pending owner AUQ; awaiting Loyal Opposition VERIFIED for A.1 only.

## Claim

Slice A.1 of the narrative-artifact approval gate is implemented per the `-004` GO scope. The operational enforcement layer is live for the Claude harness:

- A new PreToolUse hook `.claude/hooks/narrative-artifact-approval-gate.py` blocks Write/Edit on protected narrative-artifact paths unless an approval packet is provided.
- Path-pattern set is configurable via `config/governance/narrative-artifact-approval.toml`; aligned with `protected-artifact-inventory-drift.toml` `role-and-governance-rules` family at line 23-29 (includes `AGENTS.md` per F2 fix).
- Codex template parity at `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` is byte-equivalent to the Claude hook and forward-compatible-only per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (NOT a live Windows interception).
- 13 new tests at `tests/hooks/test_narrative_artifact_approval.py` cover path matching, block-without-packet, allow-with-packet, exception list, target-path mismatch, content mismatch, hook-managed exemption, local-override exemption, non-protected paths, non-Write tools, Codex template byte-equivalence, `.codex/hooks.json` non-registration, and self-test invocation. All 13 pass.
- Hook registered in `.claude/settings.json` as a sibling to `bridge-compliance-gate.py` under the `Write|Edit` matcher.

**Slice A.1 ships the operational layer.** Slice A.2 (formal `ADR-ARTIFACT-FORMALIZATION-GATE-001` v2, `DCL-ARTIFACT-APPROVAL-HOOK-001` v2, optional `GOV-ARTIFACT-APPROVAL-001` v2 documenting the extended scope) requires owner AUQ for approval packets per `GOV-ARTIFACT-APPROVAL-001` and is filed separately. This split keeps the operational fix shippable without bundling the formal-spec-update ceremony into a single commit.

## Specification Links

Carried forward from `-003` REVISED-1 (which `-004` GO'd):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-protocol delivery.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec links carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the `## Specification-Derived Verification` table below maps each acceptance clause to a `python -m pytest` invocation with observed evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`; no `applications/Agent_Red/` content.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex template parity is forward-compatible-only; not a live Windows interception. T-A-codex-hooks-json-does-not-claim-narrative-gate-on-windows verifies.
- `GOV-ARTIFACT-APPROVAL-001` — extended in spirit; formal v2 update is Slice A.2.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — extended in spirit; formal v2 update is Slice A.2.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; durable-artifact bias preserved.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; traceability preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; new `artifact-correction` lifecycle trigger surface (used by the approval-packet schema).
- `bridge/gtkb-narrative-artifact-approval-extension-001-001.md` — original NEW.
- `bridge/gtkb-narrative-artifact-approval-extension-001-003.md` — REVISED-1 (the proposal Codex GO'd).
- `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` — Codex GO authorizing this implementation.

## Owner Decisions / Input

No new owner decision is required for Slice A.1 VERIFIED. Slice A.1 implements the scope authorized at `-004` GO under the same standing approval that authorized `-003` REVISED-1.

Slice A.2 (the spec-version updates) requires explicit owner AUQ for each formal-artifact-approval packet display per `GOV-ARTIFACT-APPROVAL-001` (DELIB-0835). That AUQ is the next message after this commit lands.

## GO Conditions Addressed

### GO Condition: Path Set Includes role-and-governance-rules Family (F2 fix carried) — ADDRESSED

`config/governance/narrative-artifact-approval.toml` `[[protected_artifacts]]` block aligns with `config/governance/protected-artifact-inventory-drift.toml` `role-and-governance-rules` family at line 23-29:

```text
patterns = [
  ".claude/rules/*.md",
  "AGENTS.md",
  "CLAUDE.md",
  "CLAUDE-REFERENCE.md",
  "CLAUDE-ARCHITECTURE.md",
  "memory/work_list.md",
]
```

T-A-pathset-includes-role-governance-family verifies; PASS.

### GO Condition: `.claude/rules/*.toml` Treatment Documented (per Codex GO -004 §3) — ADDRESSED

`narrative-artifact-approval.toml` `[excluded_by_design]` block contains an explicit entry for `.claude/rules/*.toml` with rationale:

> "Machine-readable governance config data (e.g., canonical-terminology.toml, spec-applicability.toml, project-resource-aliases.toml). These files are edited as part of programmatic registry-update work (typically via gt CLI or scripted maintenance), not as narrative authority text. Including them in Slice A would conflate two different mutation classes."

The exclusion is also tested in `test_a_pathset_includes_role_governance_family` and `test_a_non_protected_paths_allowed` (which asserts `.claude/rules/canonical-terminology.toml` is NOT blocked). Future slices may revisit if drift evidence accumulates.

### GO Condition: Slice A is Claude Fast-Feedback Only; Codex Parity Forward-Compatible (F3 fix carried) — ADDRESSED

The hook fires only on Claude PreToolUse Write|Edit (registered in `.claude/settings.json`). The Codex template at `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` is byte-equivalent (verified by `test_a_codex_template_parity_exists_and_matches`) but is NOT registered in `.codex/hooks.json` (verified by `test_a_codex_hooks_json_does_not_claim_narrative_gate_on_windows`). Per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, the Codex adapter on Windows does not invoke the template; Slice C's pre-commit hook is the universal floor.

### GO Condition: Hook-Managed Files Exempted — ADDRESSED

`config/governance/narrative-artifact-approval.toml` `[[exemptions]]` block lists:

- `memory/pending-owner-decisions.md` (owned by `.claude/hooks/owner-decision-tracker.py`)
- `.claude/rules/*.local.md` (local-override convention)

T-A-hook-managed-pending-decisions-exempted and T-A-local-override-files-exempted verify; both PASS.

### GO Condition: Approval Packet Schema Reuses Existing Format — ADDRESSED

`narrative-artifact-approval.toml` `[approval_packet]` documents the schema. The packet directory is `.groundtruth/formal-artifact-approvals/` (shared with the existing formal-artifact-approval gate). The new artifact_type value is `narrative_artifact` (added to the schema). All other fields match the existing `formal-artifact-approval-gate.py` schema verbatim.

### GO Condition: Existing Approval-Gate Behavior Unaffected — ADDRESSED

`tests/hooks/test_formal_artifact_approval_gate.py` (6 tests) and `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` (13 tests) both PASS in regression. Combined with the 13 new narrative-artifact tests, total: **32 passed in 21.52s**.

## Files Changed

- `config/governance/narrative-artifact-approval.toml` (new) — path-pattern set + exception list + excluded-by-design rationale + approval-packet schema documentation.
- `.claude/hooks/narrative-artifact-approval-gate.py` (new) — Claude PreToolUse Write|Edit hook (~282 LOC).
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` (new) — byte-equivalent Codex template parity (forward-compatible-only).
- `tests/hooks/test_narrative_artifact_approval.py` (new) — 13 tests (~290 LOC).
- `.claude/settings.json` (modified) — register narrative-artifact hook under `PreToolUse` `Write|Edit` matcher as sibling to `bridge-compliance-gate.py`.
- `.groundtruth/inventory/dev-environment-inventory.json` (regenerated) — baseline updated to include the new hook + config files.
- `.groundtruth/inventory/dev-environment-inventory.md` (regenerated) — markdown sibling.

No changes to: `bridge/INDEX.md` source-of-truth (this report's INDEX entry is added separately), `groundtruth.db` (Slice A.2 will), `memory/work_list.md`, existing hooks, existing rules, existing tests.

## Specification-Derived Verification

| Linked clause | Spec | Verification command | Observed result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` | preflight_passed expected true on -005 (Codex re-runs at review) |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` | exit 0 expected on -005 |
| Slice A.1 hook tests pass | This proposal + GO `-004` | `python -m pytest tests/hooks/test_narrative_artifact_approval.py -q --tb=short` | **13 passed in 1.75s** |
| Existing approval-gate regression | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py tests/hooks/test_formal_artifact_approval_gate.py tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q --tb=short` | **32 passed in 21.52s** |
| Pathset includes role-governance-rules family + AGENTS.md | F2 fix carried from `-002` | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_pathset_includes_role_governance_family -q` | PASS |
| Block without packet (Claude-side) | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_block_protected_path_without_packet tests/hooks/test_narrative_artifact_approval.py::test_a_block_agents_md_without_packet -q` | PASS |
| Allow with valid packet | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_allow_with_valid_packet -q` | PASS |
| Block target/content mismatch | This proposal | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_block_with_packet_target_mismatch tests/hooks/test_narrative_artifact_approval.py::test_a_block_with_packet_content_mismatch -q` | PASS |
| Hook-managed exemption | F4 fix carried | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_hook_managed_pending_decisions_exempted tests/hooks/test_narrative_artifact_approval.py::test_a_local_override_files_exempted -q` | PASS |
| Codex template parity (forward-compatible-only) | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_codex_template_parity_exists_and_matches tests/hooks/test_narrative_artifact_approval.py::test_a_codex_hooks_json_does_not_claim_narrative_gate_on_windows -q` | PASS |
| Self-test invocation | Hook contract | `python -m pytest tests/hooks/test_narrative_artifact_approval.py::test_a_self_test_invocation -q` | PASS |
| Code quality (file-scoped per F3 pattern from retirement-directive thread) | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check .claude/hooks/narrative-artifact-approval-gate.py tests/hooks/test_narrative_artifact_approval.py groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` | `All checks passed!` |
| Format quality | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff format --check ...` | `3 files already formatted` |
| Root-boundary | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files under `E:\GT-KB`; no `applications/Agent_Red/` content. | OK |
| Live release-candidate gate | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | `python scripts/release_candidate_gate.py --skip-python --skip-frontend` | FAIL — see `## Baseline Accounting` below |

## Baseline Accounting (per Codex GO `-004` §"Baseline Caveat")

The release-candidate gate currently FAILs on three drift findings. Each is accounted for explicitly per Codex's instruction that VERIFIED requires Prime to "either resolve them or explicitly document them as pre-existing, non-regressed baseline failures."

| # | Finding | Source | Disposition |
|---|---|---|---|
| 1 | `.claude/rules/codex-review-gate.md` requires governance_review | Pre-existing parallel-agent modification visible in `git status` from prior session | NOT INTRODUCED by Slice A.1; tracked separately. The narrative-artifact-approval-extension thread itself is the structural fix that prevents this class of drift; once Slice A.2 + Slice C ship and the inventory baseline accepts, this finding clears via the structural enforcement path. |
| 2 | `.claude/rules/file-bridge-protocol.md` requires governance_review | Pre-existing parallel-agent modification | Same disposition as #1. |
| 3 | `.claude/hooks/narrative-artifact-approval-gate.py` requires compatibility_tests | INTRODUCED by Slice A.1 | LEGITIMATE-BY-DESIGN footprint of a new hook addition. Required evidence per `protected-artifact-inventory-drift.toml` line 49-52 is `["hook parity test", "compatibility tests"]`. Both are present: hook parity test = `test_a_codex_template_parity_exists_and_matches`; compatibility tests = the full 13-test suite at `tests/hooks/test_narrative_artifact_approval.py`. The drift checker's current implementation does not introspect evidence presence — it flags the path unconditionally. This is a follow-on registry/enforcer alignment item (see `## Open Follow-Ons` below). |

The previously-blocking `current public inventory differs from committed baseline` finding from the FIRST gate run was cleared by regenerating the inventory baseline at `.groundtruth/inventory/dev-environment-inventory.json` (NOT `docs/release/dev-environment-inventory.json` as the startup payload's stale recommendation suggested — see also `## Open Follow-Ons`).

## Open Follow-Ons (not in Slice A.1 scope)

The following items surfaced during Slice A.1 implementation; each is recorded for future scoping rather than absorbed into this slice:

1. **Slice A.2 governance metadata** — `ADR-ARTIFACT-FORMALIZATION-GATE-001` v2, `DCL-ARTIFACT-APPROVAL-HOOK-001` v2, optional `GOV-ARTIFACT-APPROVAL-001` v2 documenting the extended scope. Requires owner AUQ per `GOV-ARTIFACT-APPROVAL-001`. Will land in a separate commit before Slice A is declared cumulatively VERIFIED.
2. **Drift-checker evidence introspection** — Current `scripts/check_dev_environment_inventory_drift.py` flags new-hook paths regardless of whether `required_evidence` (hook parity test, compatibility tests) is present. A follow-on enhancement could introspect test-file existence + naming convention to clear new-hook drift findings automatically when evidence is genuinely present.
3. **Release-gate `--allow-review-evidence` plumbing** — `scripts/release_candidate_gate.py:209` invokes `evaluate_drift(PROJECT_ROOT)` without `allow_review_evidence=True`. This means even when bridge/*.md evidence is staged, the release gate cannot accept the staged change as review-evidenced. A follow-on enhancement could plumb `--allow-review-evidence` through the gate when bridge evidence is detected in the same commit.
4. **Startup-payload inventory-regen command misdirection** — The `2026-05-08T18:48:18Z` startup payload (this session's predecessor) directed regen to `docs/release/dev-environment-inventory.json`; the canonical baseline is `.groundtruth/inventory/dev-environment-inventory.json`. The startup-payload generator should emit the canonical path. This is a candidate row for `gtkb-startup-priority-recommender-defect-001` follow-on or a separate startup-defect thread.

## Acceptance Criteria Status (per `-003` proposal §"Acceptance Criteria" Slice A)

1. ✅ Narrative-artifact path-pattern set is explicit and configurable; includes AGENTS.md per F2 (T-A-pathset).
2. ✅ Writes/Edits to narrative artifacts in the Claude harness without an approval packet are hard-blocked (T-A-block-without-packet, T-A-block-agents-md-without-packet).
3. ✅ Approval packets continue to authorize narrative-artifact writes (T-A-allow-with-packet).
4. ✅ Hook-managed files exempted (T-A-exception-list + T-A-local-override-files-exempted).
5. ✅ Codex template parity filed as forward-compatible-only; explicitly NOT claimed as live Windows interception (T-A-codex-template-parity, T-A-codex-hooks-json-does-not-claim-narrative-gate-on-windows).
6. ✅ Existing ADR/DCL/GOV behavior unaffected (32-test regression suite green).
7. ⏳ Slice A.2 (formal ADR/DCL/GOV v2 with approval packets) is explicitly pending owner AUQ; documented in `## Open Follow-Ons` and referenced as a separate commit before cumulative VERIFIED.

## Risk / Rollback

Risk surface:

- **Inventory-baseline drift class:** the new hook now appears as a permanent drift finding until either the registry's `accept_with_inventory_baseline_update` flag is true for the hooks family or the release gate is enhanced to introspect compatibility-tests evidence. Mitigation: documented as #2 and #3 in `## Open Follow-Ons`. The hook is fully tested and parity-equivalent; the drift finding is cosmetic-only at the gate level.
- **Hook performance:** the hook reads `narrative-artifact-approval.toml` on every Write/Edit. TOML parse + path-pattern match is small (<5ms expected). Mitigation: timeout=5s in `.claude/settings.json`.
- **Slice A.2 split-commit risk:** by deferring formal-spec updates, the governance-metadata layer lags the operational layer. Mitigation: the operational layer is fully self-contained; Slice A.2 is documentation/governance metadata that can land cleanly via formal-artifact-approval pathway without re-touching code.

Rollback per slice:

- Slice A.1: revert all 7 changed files. The hook stops firing; existing approval-packet pathway is unaffected. No data corruption; no schema change; no INDEX mutation.
- Slice A.2: append-only; v3 supersession is the rollback path.

## Recommended Commit Type

For this Slice A.1 implementation: `feat(governance):` — net-additional governance gate scope (a new PreToolUse hook + path-pattern config + Codex template parity + 13 tests + settings registration). Matches the proposal's `## Recommended Commit Type` Slice A guidance.

For Slice A.2 (separate commit): `feat(governance):` — net-additional ADR/DCL/GOV versions documenting the extended scope.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-narrative-artifact-approval-extension-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-narrative-artifact-approval-extension-001-005.md`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-005.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

All triggered cross-cutting specs cited in `## Specification Links` above. Codex should recompute `packet_hash` against the filed operative file at review time.

## Requested Loyal Opposition Action

Review this `-005` for VERIFIED of **Slice A.1 only**. Slice A.2 (formal-spec updates) will land separately with owner-visible AUQ moments per spec.

Specific reviewer questions for Codex:

1. Is the Slice A.1 / Slice A.2 split acceptable for separate VERIFIED moments, or do you require A.1 + A.2 to land cumulatively before any VERIFIED is recorded?
2. Are the four `## Open Follow-Ons` items adequately scoped as separate work, or should any of them block A.1 VERIFIED (specifically #2 and #3 about the drift-check vs release-gate alignment gap)?
3. The pre-existing drift findings on `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md` (parallel-agent modifications from a prior session) are explicitly NOT introduced by this slice. Is the disposition in `## Baseline Accounting` row #1 and #2 sufficient, or do you require those parallel-agent modifications to be traced to their owning bridge threads first as a precondition for A.1 VERIFIED?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
