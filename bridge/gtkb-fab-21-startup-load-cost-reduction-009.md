NEW

bridge_kind: implementation_report
Document: gtkb-fab-21-startup-load-cost-reduction
Version: 009
Responds-To: bridge/gtkb-fab-21-startup-load-cost-reduction-008.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4433
Project Authorization: PAUTH-FAB21-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 39746c1a-10a0-4914-a27c-dc4251c74b08
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/operating-model.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/bridge-essential.md", ".claude/rules/project-root-boundary.md"]

# FAB-21 — Startup Load-Cost Reduction — Post-Implementation Report (HYG-028: Always-Loaded Stale-Pointer Sweep)

## Slice Scope (this report vs the now-VERIFIED HYG-025 Slice 1)

This is a **new slice** on the same FAB-21 bridge thread, authorized by the same
`GO@-004` proposal. It is independent of the HYG-025 Slice 1 profiler baseline,
which was VERIFIED at `-008` (commit `522b7872`). This report (`-009`) covers
**HYG-028 only**: the always-loaded stale-pointer sweep across five protected
`.claude/rules/*.md` files. `Responds-To: -008` chains the thread; it does not
re-open the verified profiler slice.

## Implementation Summary

HYG-028 corrects **12 pure path-token references** to retired/moved locations in
the five always-loaded protected rule files (the startup DA read-surface that
FAB-21 measures). The corrections are textual only — no behavior, no harness
names, no live `scripts/ollama_harness.py` reference, no code, no schema changed.

Two correction families:

1. **`.ollama/` → `.api-harness/`** (8 references). The `.ollama/` directory is
   retired and contains zero files; the live routing/skills config tree is
   `.api-harness/` (39 files present). Distribution:
   - `canonical-terminology.md` ×6 (`routing.toml` definition + the ollama /
     routing.toml / task-to-model-routing implementation pointers).
   - `operating-model.md` ×2 (§3 Implemented + Intended-but-partial bullets:
     `.api-harness/routing.toml`, `.api-harness/skills/`).
2. **`tests/scripts/` → `platform_tests/scripts/`** (4 references). The test
   suite moved to `platform_tests/scripts/`; the corrected targets all resolve:
   - `canonical-terminology.md` ×1 — `test_cross_harness_bridge_trigger.py`.
   - `bridge-essential.md` ×1 — `test_cross_harness_bridge_trigger.py`.
   - `acting-prime-builder.md` ×1 — `test_codex_hook_parity.py`.
   - `project-root-boundary.md` ×1 — `test_rehearse_isolation.py`.

Harness names (`ollama`, the `ollama` harness term) and the live
`scripts/ollama_harness.py` source pointer were deliberately NOT touched; only
retired *path* tokens were corrected.

## Protected-Narrative Approval Evidence

The five files are protected narrative artifacts (`.claude/rules/*.md`), governed
by `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`. Each edit
carries a per-file owner-approval packet on disk under
`.groundtruth/formal-artifact-approvals/fab-21-<rule>-md.json`
(`approval_mode: approve`, `presented_to_user: true`, `transcript_captured: true`,
each `full_content_sha256` equal to the staged blob). The narrative-evidence
gate clears all five:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --staged
# PASS narrative-artifact evidence (5 cleared)
```

## Specification Links

Active/scoped specifications for this slice (each has an executed row in the
Spec-to-Test Mapping):

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the core HYG-028 spec: always-loaded rule
  files must not carry stale source-of-truth pointers. The sweep replaces retired
  `.ollama/` and moved `tests/scripts/` references with the live `.api-harness/`
  and `platform_tests/scripts/` locations.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — `canonical-terminology.md` is the
  always-loaded glossary / DA read surface; the corrections keep its
  implementation pointers accurate for the read path.
- `GOV-ARTIFACT-APPROVAL-001` — the five protected `.claude/rules/*.md` edits each
  carry an owner-approval packet; the narrative-artifact gate clears all five.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — the narrative-artifact approval gate
  mechanism that enforces the per-file packet evidence above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all five files are in-root under
  `.claude/rules/`; no `applications/` subtree touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage gated by
  the applicability preflight (below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a live INDEX entry;
  append-only thread.
- `GOV-08` — this slice writes no MemBase and no config; only the five rule files
  plus this bridge report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle governance
  for this bridge report (advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the complete spec-to-test
  mapping + deterministic verification evidence below.

Contextual (not an acceptance gate for this slice): `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`
— HYG-028 does not reduce the always-loaded payload (it is a freshness/accuracy
correction, not a size reduction); the token-budget payoff lands in the later
HYG-025 glossary-IA slice.

## Prior Deliberations

- `DELIB-FAB21-REMEDIATION-20260610` — the owner AUQ dispositions for the FAB-21
  program; HYG-028 is one batch within the sequenced remediation.
- `DELIB-FABLE-GRILL-20260610-Q1` — PROJECT-FABLE-INVESTIGATION chartering.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring fixed startup costs
  (including stale read-surface pointers) are defects to engineer out.
- `bridge/gtkb-fab-21-startup-load-cost-reduction-003.md` (REVISED) — the GO'd
  proposal this slice implements (HYG-028 line item).
- `bridge/gtkb-fab-21-startup-load-cost-reduction-004.md` (GO) — Loyal Opposition
  (Antigravity, harness C) approval of the FAB-21 program.
- `bridge/gtkb-fab-21-startup-load-cost-reduction-008.md` (VERIFIED) — the prior
  HYG-025 Slice 1 verification this thread chains from.

## Owner Decisions / Input

Authorized by:

- The bridge `GO` at `-004` (authorizes the FAB-21 proposal, including the
  HYG-028 stale-pointer line item).
- The owner `AskUserQuestion` on 2026-06-11, **"Approve all 12 corrections"** — an
  explicit owner approval of the full 12-token sweep across the five protected
  always-loaded rule files, recorded in each per-file narrative-approval packet's
  `explicit_change_request` field and tied to `DELIB-FAB21-REMEDIATION-20260610`.
- The five per-file formal narrative-approval packets at
  `.groundtruth/formal-artifact-approvals/fab-21-<rule>-md.json` (the per-protected-file
  owner-approval evidence required by `GOV-ARTIFACT-APPROVAL-001`).
- The owner standing directive (this session) to drive the Fable program to
  VERIFIED autonomously, AUQ only for decisions.

Owner Action Required: None.

## Spec-to-Test Mapping

| Specification | Verification command / evidence | Executed | Result |
|---|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale always-loaded pointers; corrected targets resolve) | `rg -n "\.ollama/\|\btests/scripts/"` over the 5 files → 0 matches; `.api-harness/` present (39 files); `.ollama/` absent; `platform_tests/scripts/{test_codex_hook_parity,test_cross_harness_bridge_trigger,test_rehearse_isolation}.py` all `Test-Path = True` | yes | PASS |
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (glossary read-surface pointers accurate) | `canonical-terminology.md` ollama/routing pointers now cite `.api-harness/`; 0 residual `.ollama/` in that file | yes | PASS |
| `GOV-ARTIFACT-APPROVAL-001` (per-file owner approval) | 5 packets present at `.groundtruth/formal-artifact-approvals/fab-21-*.json`, each `presented_to_user: true`, `approval_mode: approve`, sha256 == staged blob | yes | PASS |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (narrative gate clears) | `check_narrative_artifact_evidence.py --staged` → `PASS narrative-artifact evidence (5 cleared)` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | `git diff --cached --stat` → only `.claude/rules/{canonical-terminology,operating-model,acting-prime-builder,bridge-essential,project-root-boundary}.md`; no `applications/`; clause `CLAUSE-IN-ROOT` evidence=yes | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (all relevant specs linked) | `bridge_applicability_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction` → `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`; clause `CLAUSE-CONCRETE-LINKS` evidence=yes | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX canonical; append-only) | live `bridge/INDEX.md` `NEW@-009` entry; prior versions `-001..-008` retained; clause `CLAUSE-INDEX-IS-CANONICAL` evidence=yes | yes | PASS |
| `GOV-08` (no MemBase write) | `git diff --cached --stat` → no `groundtruth.db`, no `config/governance/*.toml`; only the 5 rule files (+ this report at commit time) | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) | implementation captured as durable bridge artifacts (`-003` proposal, `-009` report) linked to `WI-4433` | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) | the sweep is a tracked artifact under the bridge lifecycle; no transient-only change | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) | slice lifecycle tracked via bridge versioning (`NEW@-009` → awaiting `VERIFIED`) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (every linked spec has executed evidence) | this complete table; HYG-028 is doc-only, so spec-derived "tests" are deterministic verification commands, all executed and PASS | yes | PASS |

## Verification Commands and Results

### Residual / freshness evidence

```text
rg -n "\.ollama/|\btests/scripts/"  .claude/rules/canonical-terminology.md .claude/rules/operating-model.md .claude/rules/acting-prime-builder.md .claude/rules/bridge-essential.md .claude/rules/project-root-boundary.md
# (no matches — 0 residual stale pointers)

Test-Path .api-harness  -> True   (39 files)
Test-Path .ollama       -> False  (retired/zero-files)
Test-Path platform_tests\scripts\test_codex_hook_parity.py            -> True
Test-Path platform_tests\scripts\test_cross_harness_bridge_trigger.py -> True
Test-Path platform_tests\scripts\test_rehearse_isolation.py           -> True
```

### Narrative-evidence gate

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --staged
# PASS narrative-artifact evidence (5 cleared)
```

### Staged diff scope

```text
git diff --cached --stat
#  .claude/rules/acting-prime-builder.md  | 2 +-
#  .claude/rules/bridge-essential.md      | 2 +-
#  .claude/rules/canonical-terminology.md | 14 +++++++-------
#  .claude/rules/operating-model.md       | 4 ++--
#  .claude/rules/project-root-boundary.md | 2 +-
#  5 files changed, 12 insertions(+), 12 deletions(-)
```

### Applicability and clause preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction
# preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction
# blocking gaps 0; exit 0
```

(Both preflight outputs are reproduced verbatim in the commit-time evidence; this
report is filed only after both pass.)

## Recommended Commit Type

`docs:` — these are documentation/rule-text path-token corrections in protected
narrative files; no source, behavior, schema, or test logic changes. Per the
Conventional Commits Type Discipline, `docs:` is the correct type for
governance/rule-file-only edits. (The overall FAB-21 `perf:` cost-reduction lands
in the later glossary-IA slice; HYG-028 is freshness/accuracy, not size.)

## Isolation Placement Compliance

All five edited files are in-root under `E:\GT-KB\.claude\rules\`. No
`applications/` subtree touched; no out-of-root artifact. The corrected pointers
themselves reference in-root live locations (`.api-harness/`,
`platform_tests/scripts/`).

## Acceptance Criteria (this slice)

1. All 12 approved corrections applied; zero residual `.ollama/` and zero bare
   `tests/scripts/` in the 5 files — DONE (rg → 0 matches).
2. Corrected targets resolve (`.api-harness/` live; 3 `platform_tests/scripts/*.py`
   present) — DONE.
3. Per-file narrative-approval evidence clears (`--staged` PASS, 5 cleared) — DONE.
4. No MemBase write, no config change, no harness-name or source-pointer edit —
   CONFIRMED.

## Commit / Bridge State Note

The 5 rule files are staged with their narrative-approval packets on disk. This
`-009` report is committed together with the 5 rule files under an explicit
pathspec (`docs:`); staging this `bridge/*.md` alongside satisfies the
`role-and-governance-rules` `governance_review` route
(`.githooks/pre-commit --allow-review-evidence`). The `NEW@-009` line is added to
the live working-tree `bridge/INDEX.md` for Loyal Opposition to scan; the live
INDEX is the canonical queue per `GOV-FILE-BRIDGE-AUTHORITY-001`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
