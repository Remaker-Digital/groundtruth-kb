NEW

bridge_kind: implementation_report
Document: gtkb-fab-21-startup-load-cost-reduction
Version: 011
Responds-To: bridge/gtkb-fab-21-startup-load-cost-reduction-010.md
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

target_paths: [".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md"]

# FAB-21 — Startup Load-Cost Reduction — Post-Implementation Report (HYG-025: Glossary Core/Detail Information-Architecture)

## Slice Scope (this report vs the prior VERIFIED slices)

This is the third slice on the FAB-21 bridge thread, authorized by the same
`GO@-004` proposal and the owner sequencing decision in
`DELIB-FAB21-REMEDIATION-20260610` ("HYG-025 = Full program, sequenced: profiler
baseline first, THEN glossary information-architecture"). Prior slices:
HYG-025 Slice 1 profiler baseline VERIFIED at `-008` (commit `522b7872`); HYG-028
stale-pointer sweep VERIFIED at `-010` (commit `bfddafbab` + verdict `8516fecd7`).
This report (`-011`) covers the **HYG-025 glossary core/detail
information-architecture** — the sequenced glossary restructure. `Responds-To: -010`
chains the thread; it does not re-open the verified slices.

## Implementation Summary

`canonical-terminology.md` is the largest always-loaded protected rule file —
82,747 bytes, ~25% of the 334KB `.claude/rules/*.md` startup payload, paid by
every Claude AND Codex session before any work. HYG-025 splits it into an
always-loaded **core** plus an on-demand **detail reference**, per the owner's
chosen "balanced stub-in-core" strategy.

Deterministic, self-asserting builder (`.gtkb-state/_build_fab21_hyg025.py`):

- The **23 doctor-required primer terms** stay **FULL** in the always-loaded core.
- The **58 non-required term entries** compress to: `### heading` + (`**Canonical
  alias:**` if present) + `**Definition:**` + a one-line pointer to the detail
  reference. Their verbose fields (`**Not to be confused with:**`, `**Source:**`,
  `**Implementation pointer:**`, extended discussion) move VERBATIM to the detail.
- All 84 `###` headings remain in core (every term still discoverable by
  name + definition — the DA read surface stays complete-by-name).
- The preamble, section intros, the `## Alias / Canonical Disposition` table, the
  `## Expected Glossary Artifact Terms` (MEMBASE-4) tables, and the
  `## Doctor Contract` are unchanged.

New non-auto-loaded reference: `groundtruth-kb/docs/reference/canonical-terminology-detail.md`
(60,765 bytes) holds the 58 full entries.

**Always-loaded reduction: 82,747 → 61,545 bytes (−21,202, −25.6%).**

### Honest correction to the strategy AUQ estimate

The strategy AUQ presented an estimated ~45-55% reduction for the balanced
option; the verified actual is **25.6%**. The gap is because "balanced
stub-in-core" keeps every term's full Definition always-loaded by design, and
Definitions are a larger share of each entry than estimated. The owner was shown
the corrected byte numbers and a sample compressed stub and approved applying the
balanced split as-built ("Approve & apply balanced", AskUserQuestion 2026-06-11).
The benefit the owner selected — the DA read surface stays complete-by-name — is
fully delivered.

## Protected-Narrative Approval Evidence

`canonical-terminology.md` is a protected narrative artifact
(`GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`). The edit carries
a per-file owner-approval packet at
`.groundtruth/formal-artifact-approvals/fab-21-hyg025-canonical-terminology-md.json`
(`approval_mode: approve`, `presented_to_user: true`, `transcript_captured: true`,
`full_content_sha256: a8b1e123c8e681956b63ac4dfe88950668e6f0e0fc3fa98da38a09247c8da0f3`
== the staged-blob sha256). The detail reference is not a protected path and
needs no packet. The narrative-evidence gate clears:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --staged
# PASS narrative-artifact evidence (1 cleared)
```

## Specification Links

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — the glossary is the always-loaded DA
  read surface; the balanced split preserves its completeness-by-name (every term
  keeps heading + definition in core) while moving verbose detail on-demand.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — the startup token budget the rules
  payload exceeds; HYG-025 removes 21KB from the always-loaded surface.
- `GOV-SESSION-SELF-INITIALIZATION-001` — requires startup token-reduction options
  (progressive disclosure / on-demand detail); the core/detail split realizes one.
- `GOV-ARTIFACT-APPROVAL-001` — the protected-narrative edit carries its per-file
  owner-approval packet.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — the narrative-artifact approval gate
  mechanism that validates the packet against the staged blob.
- `GOV-08` — no MemBase write; the `canonical-terminology.toml` required-terms
  matrix stays green (doctor `_check_canonical_terminology` = pass).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changes in-root; the detail
  reference is in-root under `groundtruth-kb/docs/reference/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage gated by
  the applicability preflight below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a live INDEX entry;
  append-only.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
  / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the
  glossary restructure + the new detail artifact (advisory).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the complete spec-to-test
  mapping + deterministic verification evidence below.

## Prior Deliberations

- `DELIB-FAB21-REMEDIATION-20260610` — owner sequencing: profiler baseline first,
  THEN glossary IA; this slice is the glossary IA step.
- `DELIB-FABLE-GRILL-20260610-Q1` — PROJECT-FABLE-INVESTIGATION chartering.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring fixed startup token
  costs are a defect to engineer out; the always-loaded glossary is one such cost.
- `bridge/gtkb-fab-21-startup-load-cost-reduction-003.md` (REVISED) — the GO'd
  proposal this slice implements (HYG-025 line item; names the detail artifact in
  target_paths).
- `bridge/gtkb-fab-21-startup-load-cost-reduction-008.md` (VERIFIED) — profiler
  baseline; `bridge/gtkb-fab-21-startup-load-cost-reduction-010.md` (VERIFIED) —
  HYG-028 sweep; this thread chains from `-010`.
- The S331 DA-read-surface / placement / bias-vs-salience deliberations
  (`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`,
  `ADR-DA-READ-SURFACE-PLACEMENT-001`) — the salience principle that motivated the
  balanced (read-surface-preserving) strategy over the aggressive option.

## Owner Decisions / Input

Authorized by:

- The bridge `GO` at `-004` (authorizes the FAB-21 proposal, including the HYG-025
  glossary-IA line item, which names the detail artifact in target_paths).
- The owner sequencing decision `DELIB-FAB21-REMEDIATION-20260610` ("HYG-025 = Full
  program, sequenced").
- **Two `AskUserQuestion` decisions on 2026-06-11:** (1) strategy = **"Balanced
  stub-in-core"** (every term keeps name + definition always-loaded; 23 required
  full; verbose detail for non-required moves out); (2) after the verified-byte
  correction was disclosed (actual 25.6% vs the ~45-55% estimate, with a sample
  stub shown), apply = **"Approve & apply balanced"** — the protected-narrative
  content approval for the `canonical-terminology.md` edit.
- The per-file narrative-approval packet at
  `.groundtruth/formal-artifact-approvals/fab-21-hyg025-canonical-terminology-md.json`.
- The owner standing directive (this session) to drive the Fable program to
  VERIFIED autonomously, AUQ only for decisions.

Owner Action Required: None.

## Spec-to-Test Mapping

| Specification | Verification command / evidence | Executed | Result |
|---|---|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (read surface complete-by-name) | builder assertion: all 84 `### ` term headings present in core; `Select-String '^### '` core = 84, detail = 58 | yes | PASS |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (always-loaded payload reduced) | builder report: core 82,747 → 61,545 bytes (−21,202, −25.6%); detail 60,765 bytes NOT auto-loaded | yes | PASS |
| `GOV-SESSION-SELF-INITIALIZATION-001` (on-demand detail realizes progressive disclosure) | new non-auto-loaded `groundtruth-kb/docs/reference/canonical-terminology-detail.md` holds 58 full entries; core stubs point to it | yes | PASS |
| `GOV-ARTIFACT-APPROVAL-001` (per-file owner approval) | packet present, `presented_to_user: true`, `approval_mode: approve`, sha256 `a8b1e123…` == staged blob | yes | PASS |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (narrative gate clears) | `check_narrative_artifact_evidence.py --staged` → `PASS narrative-artifact evidence (1 cleared)` | yes | PASS |
| `GOV-08` (no MemBase write; doctor terms green) | `_check_canonical_terminology(., dual-agent)` → `status='pass'`; `git diff --cached --stat` → no `groundtruth.db`, no `.toml` | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | both paths in-root (`.claude/rules/`, `groundtruth-kb/docs/reference/`); no `applications/`; clause `CLAUSE-IN-ROOT` evidence=yes | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (all relevant specs linked) | `bridge_applicability_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction` → `preflight_passed: true`, `missing_required_specs: []`; clause `CLAUSE-CONCRETE-LINKS` evidence=yes | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX canonical; append-only) | live `bridge/INDEX.md` `NEW@-011`; prior versions retained; clause `CLAUSE-INDEX-IS-CANONICAL` evidence=yes | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) | restructure captured as durable bridge artifacts linked to `WI-4433`; detail artifact is a tracked durable reference | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (every linked spec has executed evidence) | this complete table; HYG-025 is doc/rule-restructure, so spec-derived "tests" are deterministic verification commands, all executed and PASS | yes | PASS |

## Verification Commands and Results

### Builder (deterministic split + self-assertions)

```text
groundtruth-kb\.venv\Scripts\python.exe .gtkb-state\_build_fab21_hyg025.py --apply
# term entries: 81 (required full: 23, non-required stub: 58)
# source 82,747 -> core 61,545 (-21,202 = 25.6%); detail 60,765
# required terms all present in core: True; all assertions PASS
```

### Doctor canonical-terminology check (required-terms green)

```text
_check_canonical_terminology(Path('.'), 'dual-agent')
# status: 'pass'
# 'Canonical-terminology surface OK — 5 required terms present in 4 required files (profile: dual-agent)'
# (overall pass also requires the 23 required_primer_terms present in canonical-terminology.md)
```

### Narrative-evidence gate + staged scope

```text
check_narrative_artifact_evidence.py --staged  ->  PASS narrative-artifact evidence (1 cleared)
git diff --cached --stat  ->  .claude/rules/canonical-terminology.md (modified),
                              groundtruth-kb/docs/reference/canonical-terminology-detail.md (new)
```

### Applicability + clause preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction
# preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-21-startup-load-cost-reduction
# blocking gaps 0; exit 0
```

(Both preflight outputs are reproduced in the commit-time evidence; this report is
filed only after both pass.)

## Recommended Commit Type

`docs:` — this slice restructures a protected rule/glossary document and adds a
documentation reference; no source, schema, or test logic changes. Per the
Conventional Commits Type Discipline, `docs:` is correct for governance/rule-file
restructures (consistent with the HYG-028 `-009` slice). The perf MOTIVATION
(always-loaded token reduction) is real, but the DIFF is documentation-only.

## Isolation Placement Compliance

Both edited/created paths are in-root under `E:\GT-KB\`:
`.claude/rules/canonical-terminology.md` and
`groundtruth-kb/docs/reference/canonical-terminology-detail.md`. No `applications/`
subtree touched; no out-of-root artifact.

## Acceptance Criteria (this slice)

1. `canonical-terminology.md` split into an always-loaded core + the on-demand
   detail artifact; doctor required-terms check green — DONE (status='pass').
2. The 23 required primer terms remain full in core; all 84 term headings remain
   discoverable in core — DONE (builder assertions; core ### = 84).
3. Per-file narrative-approval packet exists and clears the gate — DONE
   (`--staged` PASS, 1 cleared).
4. No MemBase write, no config change — CONFIRMED (`git diff --cached --stat`).

The dedup + era-file archival sub-step and the HYG-008 measure-first item remain
out of this slice (subsequent FAB-21 work).

## Commit / Bridge State Note

`canonical-terminology.md` (modified) + `canonical-terminology-detail.md` (new) are
committed together with this `-011` report under an explicit pathspec (`docs:`);
staging this `bridge/*.md` alongside satisfies the `role-and-governance-rules`
`governance_review` route (`.githooks/pre-commit --allow-review-evidence`). The
`NEW@-011` line is added to the live working-tree `bridge/INDEX.md`; the live INDEX
is the canonical queue per `GOV-FILE-BRIDGE-AUTHORITY-001`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
