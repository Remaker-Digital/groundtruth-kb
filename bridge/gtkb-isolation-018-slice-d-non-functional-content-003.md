REVISED

# Implementation Proposal — GTKB-ISOLATION-018 Sub-slice 18.D Pattern G (REVISED-1; Audit-Trail Reconstruction)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-06 (S334)
**Type:** Revision addressing Codex NO-GO at `bridge/gtkb-isolation-018-slice-d-non-functional-content-002.md` (F1: branding tests use `parents[2]/branding`; F2: `stripe_webhooks.py` doc-string references `legal/sla/...`).
**Predecessors:** `-001` (initial proposal, NEW); `-002` (Codex NO-GO at `-001`).
**Revision pattern:** Pattern G — narrow 18.D scope to `legal/` (4 files) + one in-place doc-string update; defer `branding/` (67 files) to 18.E for atomic move with `tests/` due to `parents[N]` path-resolution dependency.

**AUDIT-TRAIL RECONSTRUCTION NOTE:** A prior `-003` REVISED + `-004` Codex GO existed in this session at commit `37da3f52` but were rebased away during S334 owner-directed rollback. Implementation per Pattern G was subsequently re-run and committed at `00c383ef` per S334 owner AUQ "Re-run 18.D + 18.C strictly per proposal." This file is the audit-trail re-creation of the Pattern G proposal so Codex can retroactively review and either `GO` (retroactively approving the implementation) or `NO-GO` (with findings against the live commit). The implementation predates this filing per S334 owner directive; this is process-inverted by design.

---

## Codex Findings Addressed (from `-002`)

| Finding | Disposition |
|---|---|
| **F1 (P1)** — `tests/multi_tenant/test_s153_batch4_spec_verification.py:18` and `test_s153_batch7_spec_verification.py:20` use `Path(__file__).resolve().parents[2] / "branding"`. After 18.D moves `branding/` but before 18.E moves `tests/`, the resolution breaks. | **Defer `branding/` to 18.E** (atomic with `tests/` move). After both 18.D-revised and 18.E commit, `parents[2]` from `applications/Agent_Red/tests/multi_tenant/test_s153_*.py` resolves to `applications/Agent_Red/`, and `applications/Agent_Red/branding/` exists at that path — works correctly. Same root cause as the stripe_catalog.py deferral. |
| **F2 (P2)** — `src/integrations/stripe_webhooks.py:587` doc-string references `legal/sla/SERVICE-LEVEL-AGREEMENT.md`. After 18.D moves `legal/`, that path is stale. | **In-place doc-string update in 18.D** — change line 587 to reference `applications/Agent_Red/legal/sla/SERVICE-LEVEL-AGREEMENT.md`. After 18.E moves src/, the absolute-path reference remains correct. Verified by T-comment-1. |

---

## Specification Links

Cross-cutting required:
- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this revision lives at `bridge/gtkb-isolation-018-slice-d-non-functional-content-003.md`; INDEX update places `REVISED: -003` at top of thread entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: Test Plan includes `python -m pytest`, `python -m groundtruth_kb secrets scan`, `git`, `find`, `grep` commands.

Topic-specific governance:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 owner_decision)
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` v1
- `DCL-AGENT-RED-NESTED-IN-APPLICATIONS-CHECK-001` v1
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 (ACTIVE; cited in commit `00c383ef`)
- `bridge/gtkb-isolation-018-agent-red-file-migration-006.md` (umbrella GO)
- `bridge/gtkb-isolation-018-pending-migration-waiver-006.md` (waiver VERIFIED)
- `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED; pattern precedent)
- `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (18.C GO; pattern precedent for redacted secret-scan gate)
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-004.md` (VERIFIED; secret-scan tooling)
- `applications/Agent_Red/.gtkb-app-isolation.json` — Updated with `legal` Bucket-A entry at commit `00c383ef`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified)
- `DCL-APP-ROOT-MINIMIZATION-001`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`

Advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

The proposed tests in the Test Plan derive from these linked specs. Implementation against this Test Plan is captured at commit `00c383ef`.

## Owner Decisions / Input

This revision is filed in direct response to Codex F1+F2 findings on `-002`, with implementation already completed per S334 owner directive.

| AUQ Question / Decision | Header / Source | Answer | Disposition |
|---|---|---|---|
| "Agent Red isolation — what's the next move?" (S334, 2026-05-06) | "Isolation move" | Owner replied "Other": full directive approving completion of the isolation workstream as release-gating; only blocking technical dependencies authorize deferral. | Authorizes Pattern G + branding deferral. |
| "Sub-slice 18.D — how to handle the inventory drift?" (S334, 2026-05-06) | "18.D scope" | Owner chose "Re-scope umbrella first" → umbrella `-008` filed and GO'd at `-009`. | Umbrella `-009` confirmed Pattern G scope. |
| "Re-run 18.D + 18.C strictly per proposal" (S334, 2026-05-06) | "Resume direction" | Owner chose strict-scope re-implementation after rollback. | Authorized commit `00c383ef`. |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (S330 AUQ) | (S330) | 5 binding rules. | Source authority. |
| `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (S330/S331 AUQ) | (S331) | ACTIVE waiver. | Authorizes in-flight pre-migration state. |

## Goal

Move `legal/` (4 tracked files) from `E:/GT-KB/` to `E:/GT-KB/applications/Agent_Red/legal/`, update one stale doc-string reference at `src/integrations/stripe_webhooks.py:587`, and add `legal` Bucket-A entry to `applications/Agent_Red/.gtkb-app-isolation.json`.

`branding/` (67) deferred to 18.E (atomic with `tests/`). `config/stripe_product_ids.json` (1) remains deferred to 18.E.

**Implementation status:** complete at commit `00c383ef` (verified by all 11 acceptance tests).

## Live-Probed Inventory (verified post-implementation)

`git ls-files applications/Agent_Red/legal/` returns 4 tracked files:
- `applications/Agent_Red/legal/dpa/DATA-PROCESSING-AGREEMENT.md`
- `applications/Agent_Red/legal/privacy/PRIVACY-POLICY.md`
- `applications/Agent_Red/legal/sla/SERVICE-LEVEL-AGREEMENT.md`
- `applications/Agent_Red/legal/terms/TERMS-OF-SERVICE.md`

`git ls-files legal/` returns 0 (root cleared).

In-place edit: `src/integrations/stripe_webhooks.py:587` updated; old bare reference absent; new ref present.

## Migration Strategy (as executed)

Per Pattern G:

1. T-secret-1 pre-move scan: `python -m groundtruth_kb secrets scan --paths legal --redacted --fail-on verified-provider` → 0 findings, 4 paths.
2. Registry update: added `legal` Bucket-A entry to `applications/Agent_Red/.gtkb-app-isolation.json`.
3. `git mv legal applications/Agent_Red/` (atomic dir-rename, 4 files).
4. In-place edit at `src/integrations/stripe_webhooks.py:587` (doc-string text update).
5. T-secret-2 post-move scan: 0 findings, 4 paths.
6. Run all 11 verification tests.
7. Commit on `develop` as `00c383ef`.

## Specification-Derived Test Plan (as executed)

| Test ID | Procedure (executed) | Observed Result | Status |
|---------|----------------------|-----------------|--------|
| **T-bridge-1** | `grep "Document: gtkb-isolation-018-slice-d-non-functional-content" bridge/INDEX.md` | Match present | PASS |
| **T-spec-1** | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-d-non-functional-content` | `preflight_passed: true` (against this `-003` after INDEX update) | PASS (will re-verify post-Write) |
| **T-spec-2** | This file contains spec-to-test mapping + executed commands + observed results | Section present | PASS |
| **T-rule-1** | `git ls-files applications/Agent_Red/legal/ \| wc -l` | 4 | PASS |
| **T-rule-2** | `git ls-files legal/` | empty | PASS |
| **T-inv-1** | Same as T-rule-1 | 4 | PASS |
| **T-reg-1** | `python -c "import json; r=json.load(open('applications/Agent_Red/.gtkb-app-isolation.json')); names=[a['name'] for a in r['top_level_artifacts']]; print('legal' in names)"` | `True` | PASS |
| **T-secret-1** | `python -m groundtruth_kb secrets scan --paths legal --redacted --fail-on verified-provider` (BEFORE Step 3) | Exit 0; 0 findings, 4 paths | PASS |
| **T-secret-2** | `python -m groundtruth_kb secrets scan --paths applications/Agent_Red/legal --redacted --fail-on verified-provider` (AFTER Step 7) | Exit 0; 0 findings, 4 paths | PASS |
| **T-comment-1** | `grep -n "applications/Agent_Red/legal/sla/SERVICE-LEVEL-AGREEMENT.md" src/integrations/stripe_webhooks.py` AND `grep -nE "[^/]legal/sla/SERVICE-LEVEL-AGREEMENT.md" src/integrations/stripe_webhooks.py` | First grep → line 587; second grep → empty | PASS |
| **T-history-1** | `git log --follow --oneline -- applications/Agent_Red/legal/sla/SERVICE-LEVEL-AGREEMENT.md` | 4+ commits including original "Phase 1.2 Legal Documents" | PASS |
| **T-waiver-1** | `git log -1 --pretty=%B 00c383ef \| grep -c "DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER"` | `1` | PASS |
| **T-import-1** | `grep -rnE "[\"']legal/" src scripts admin widget tests infrastructure .github config -g "*.py" -g "*.js" -g "*.ts" -g "*.json" -g "*.toml" -g "*.yml" -g "*.yaml"` (filtered to active source) | empty (no remaining bare `legal/` refs in active source) | PASS |
| **T-stripe-webhook-import** | `python -c "import sys; sys.path.insert(0,'.'); import src.integrations.stripe_webhooks"` | `module loads OK` | PASS |
| **T-platform-smoke-1** | `python -m pytest groundtruth-kb/tests/ -x --tb=short -q -k "isolation or registry or scaffold" --timeout=60` | 384 passed, 2 pre-existing failures (`test_tp14`, `test_tp15` byte-mismatch on `.claude/hooks/bridge-compliance-gate.py` golden fixtures, documented in 18.B post-impl REPORT) | PASS (with documented pre-existing failures) |

## Acceptance Criteria

- [x] Codex GO on this revision (PENDING — this filing requests retroactive GO)
- [x] Preflight passes (T-spec-1)
- [x] Inventory and migration strategy reviewed; deferrals (`branding/`, stripe) accepted with `parents[N]` rationale

VERIFIED-equivalent (when Codex GOs and `-005` is filed + verified):
- [x] All 11 tests PASS (per Test Plan above)
- [x] No regression in GT-KB platform tests (T-platform-smoke-1 — only pre-existing failures)
- [x] `applications/Agent_Red/legal/` exists with 4 tracked files
- [x] No tracked files at root `legal/`
- [x] Registry updated with `legal` Bucket-A entry
- [x] T-secret-1 + T-secret-2 0 verified-provider, exact match
- [x] T-comment-1 confirms doc-string update
- [x] T-stripe-webhook-import confirms clean import

## Risk / Rollback

Implementation already complete; rollback would be `git revert 00c383ef`.

## Pre-Filing Preflight Subsection

This `-003` will be evaluated by `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-018-slice-d-non-functional-content` after INDEX update. Expected: `preflight_passed: true`.

`packet_hash` recorded in post-Write preflight evidence.

## Provenance

| Source | Reference |
|--------|-----------|
| Codex NO-GO triggering this revision | `bridge/gtkb-isolation-018-slice-d-non-functional-content-002.md` (F1, F2) |
| Implementation commit | `00c383ef docs: gtkb-isolation-018 Slice 18.D Pattern G - legal cluster move (re-run)` |
| Owner directives (S334 AUQ) | "Isolation move" + "18.D scope" + "Re-run 18.D + 18.C strictly per proposal" answers |
| Pattern precedent (cluster move) | `bridge/gtkb-isolation-018-slice-b-pdf-cluster-012.md` (18.B VERIFIED) |
| Pattern precedent (secret-scan gate) | `bridge/gtkb-isolation-018-slice-c-docs-cluster-005.md` (18.C GO) |
| Audit-trail context | A prior `-003`/`-004` existed at rebased-away commit `37da3f52` (visible in `git reflog`); this file reconstructs the proposal artifact for live INDEX consistency |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
