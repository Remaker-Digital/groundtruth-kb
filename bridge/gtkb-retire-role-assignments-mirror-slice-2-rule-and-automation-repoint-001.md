NEW
bridge_kind: prime_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint
Version: 001
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition (Codex, harness A, durable role per registry: `[loyal-opposition]`)
Recommended commit type: refactor

author_identity: Claude Code Prime Builder (interactive, durable PB per registry)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-retire-role-assignments-mirror-slice-2
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder])
author_role_authority_basis: Live `harness-state/harness-registry.json` records B as `status=active, role=[prime-builder]` (registry is the canonical SOT per Slice 1 -008 VERIFIED). Owner directive 2026-06-03 (interactive prompt): "complete its governed retirement before claiming registry sole authority" — explicit authorization for this slice's scope.
author_metadata_source: explicit S388 owner directive + live registry read + bridge_claim_cli claim record at .gtkb-state/work-intent/

# Slice 2 — Rule + Automation Repoint to Retire `role-assignments.json` Mirror

## PAUTH Scope Disclosure (Pre-Filing Transparency)

The cited `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` was filed scoped to "Slice 1 only" per its `scope_summary`. Its `included_work_item_ids` contains WI-4214 (mechanically satisfying `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-METADATA-PRESENT`). This proposal is Slice 2 of the same WI-4214 multi-slice umbrella and is **not within the Slice-1 PAUTH's nominal scope**. The owner directive of 2026-06-03 ("complete its governed retirement before claiming registry sole authority") is the per-proposal authorization basis carrying scope-extension authority.

Loyal Opposition has three valid responses to this scope question:

1. **GO accepting the owner directive as scope-extension authority** (precedent: `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002` GO at -002 accepted an owner-directive-only basis for that proposal's scope without a stored PAUTH).
2. **NO-GO requiring a Slice-2 PAUTH** to be created first. Owner is responsive in this session and can run `gt projects authorize` for `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-2` upon AUQ.
3. **NO-GO requiring the proposal to be re-filed with `bridge_kind: governance_review`**, gaining the metadata-exemption per `CLAUSE-NON-IMPLEMENTATION-EXEMPT`. This is mechanically valid since Slice 2 is primarily aligning rule text with the Slice-1-established reality; the PowerShell script edits are read-path repoints that consume the same registry surface the rules describe.

Author preference is path (1) for fastest forward progress, but any of the three is acceptable.

## Implementation Claim

Complete the governed retirement of `harness-state/role-assignments.json` as a load-bearing role-authority surface by:

1. **Repointing 5 rule files** (17 citation sites) from `harness-state/role-assignments.json` to `harness-state/harness-registry.json` as the durable role SOT. The rule text becomes consistent with the live runtime behavior, where the registry has been the canonical SOT since `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008` VERIFIED (2026-06-02).
2. **Repointing 5 bridge-automation PowerShell scripts** (9 citation sites under `independent-progress-assessments/bridge-automation/`) to read role from the registry. These scripts currently instruct LO sessions to "re-read `role-assignments.json` before writing any review" — under live registry SOT, that read returns stale data.
3. **Leaving the mirror file `harness-state/role-assignments.json` on disk** but no longer treated as authoritative. The mirror writer was already removed by the historical writer-removal work referenced in `scripts/harness_roles.py:538` and `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:227`; the file is orphaned. A future slice may stamp it with a deprecation header or physically delete it; this slice scopes to the read-side cleanup only.

The slice is **observation-equivalent** with the Slice 1 VERIFIED claim that the registry is canonical. Slice 1 made the writer-side canonical; this slice makes the reader-side (rule + automation surface) consistent. After this slice lands, no active surface treats `role-assignments.json` as authoritative.

**Work-item-of-record:** WI-4214 only. The historical writer-removal references above are context, not WI-of-record citations; they are intentionally written without the `WI-NNNN` literal pattern to avoid mechanical WI-ID collision warnings against the declared WI-4214.

## Specification Links

Concrete citations to governing artifacts (all 19 citations phantom-swept against live MemBase at session start; all present):

**Carry-forward from Slice 1 -008 (this slice continues the same umbrella scope):**
- `REQ-HARNESS-REGISTRY-001` v3 (specified) — registry as the role-authority SOT.
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` v2 (specified) — role/status orthogonality model.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v2 (specified) — single-active-per-role invariant.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 (specified) — fresh-read principle: this slice eliminates the rule-text/runtime drift detected by Codex NO-GO on the original thread.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (specified) — orthogonality model formalized; this slice makes rule text consistent with v3.

**Project / backlog governance:**
- `GOV-STANDING-BACKLOG-001` v5 (verified) — backlog/work-item authority covering WI-4214.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) — project authorization envelope spec; cited PAUTH is `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` with the scope disclosure above.

**Bridge protocol:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) — governs this proposal's INDEX routing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) — this `## Specification Links` section is its evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) — see `## Spec-Derived Verification Plan` below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) — three project-linkage header lines at the top of this file.

**Artifact governance (narrative-artifact gates fire on each rule edit):**
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) — formal-artifact-approval discipline.
- `PB-ARTIFACT-APPROVAL-001` v2 (verified) — Prime Builder protected-artifact write contract.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v3 (verified) — narrative-artifact-approval-gate hook gates rule edits on packet presence.

**Isolation + advisory:**
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) — all touched files are under `E:/GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (verified) — durable-artifact preservation: each rule edit goes through a packet + bridge audit trail.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (verified) — advisory: this slice routes the retirement-completion through durable governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (verified) — advisory: the mirror file transitions to `orphaned-readers-removed` lifecycle state in this slice; physical deletion deferred.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` v1 (specified) — `## Current State` table below is a fresh read of the live filesystem + MemBase.

## Owner Decisions / Input

- **S388 owner directive (interactive prompt, 2026-06-03):** in response to Codex NO-GO `-004` on `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch`, owner selected: "(a) complete its governed retirement before claiming registry sole authority" and "(b) do an audit-trail repair commit". Path (a) authorizes this slice; path (b) is addressed by this slice's scoped commit + the future REVISED `-005` post-impl on the original thread.
- **Authority basis for this slice:** owner directive (above) + live registry read confirming B holds `role=[prime-builder]` per the canonical SOT. PAUTH cited for mechanical-gate satisfaction with the scope-disclosure note at top.
- **Implicit owner direction (carry-forward from S385/S386):** B continues to hold Prime Builder authority. This slice is downstream of `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002` GO + the original Slice 1 retirement umbrella.

## Prior Deliberations

- `DELIB-2799` — owner instruction and PAUTH for the WI-4214 multi-slice umbrella Slice 1 (cited as ancestor; the PAUTH it backs is the one cited in this proposal's header).
- `DELIB-2750` — role-assignments mirror retirement context.
- `DELIB-2556` — registry projection reconciliation verification.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — owner decision adopting role/status orthogonality; this slice removes rule-text inconsistencies with that decision.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` (VERIFIED) — Slice 1 made the writer-side canonical; this slice does the reader-side.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-004.md` (NO-GO) — F1 finding that motivated this slice: 5 rule files + 3 PowerShell scripts still cite mirror as authoritative.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-002.md` (GO) — original-thread GO that established Claude=PB; this slice completes the remediation chain.
- `bridge/gtkb-role-status-orthogonality-dispatch-slice-1-adr-dcl-009.md` (VERIFIED at -010) — landed ADR-SINGLE-HARNESS-OPERATING-MODE-001 v3 which the cleaned-up rule text aligns with.

No prior deliberation rejects the read-side-cleanup approach.

## Current State (fresh read 2026-06-03 14:49Z)

| Surface | Authoritative claim | Reality |
|---|---|---|
| `harness-state/harness-registry.json` (mtime 2026-06-03 06:41) | Registry IS the SOT (`source_of_truth: "MemBase harnesses table (groundtruth.db)"`) | A=`active, [LO]`; B=`active, [PB]`; C=`registered, [PB]` |
| `harness-state/role-assignments.json` (mtime 2026-06-01 23:26) | Mirror, used to be SOT pre-Slice-1 | A=`[LO, PB]`; B=`[]`; C=`[]` — STALE |
| `.claude/rules/operating-role.md` (6 cites) | Names role-assignments.json as SOT | Disagrees with Slice 1 VERIFIED; this slice removes the SOT claim |
| `.claude/rules/canonical-terminology.md` (7 cites) | Implementation pointer = role-assignments.json | Same as above |
| `.claude/rules/bridge-essential.md` (1 cite) | Doctor reads role-assignments.json | Same as above |
| `.claude/rules/prime-builder-role.md` (2 cites) | Role record at role-assignments.json | Same as above |
| `.claude/rules/acting-prime-builder.md` (1 cite) | READ-accepts existing values | Compatibility/provenance — KEEP as compatibility statement, not as authority |
| `independent-progress-assessments/bridge-automation/*.ps1` (9 cites across 5 files) | Read role-assignments.json before writing review | Returns stale data; instructs LO under wrong authority |

Writer side: `scripts/harness_roles.py:538` and `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:227` confirm the mirror writer was removed by the historical context noted in `## Implementation Claim` above. No active writer emits to `role-assignments.json`.

## Requirement Sufficiency

Existing requirements sufficient. The retirement direction is established by `REQ-HARNESS-REGISTRY-001`, `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3, `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`, and the Slice 1 VERIFIED implementation report. This slice carries the retirement forward; no new specification creation required.

## Target Paths

```json
[
  ".claude/rules/operating-role.md",
  ".claude/rules/canonical-terminology.md",
  ".claude/rules/bridge-essential.md",
  ".claude/rules/prime-builder-role.md",
  ".claude/rules/acting-prime-builder.md",
  "independent-progress-assessments/bridge-automation/bridge-scan-common.ps1",
  "independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1",
  "independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1",
  "independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1",
  "independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1",
  "bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-001.md",
  "bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-002.md",
  "bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-003.md",
  "bridge/INDEX.md",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-operating-role-md-mirror-retirement.json",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-canonical-terminology-md-mirror-retirement.json",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-bridge-essential-md-mirror-retirement.json",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-prime-builder-role-md-mirror-retirement.json",
  ".groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-acting-prime-builder-md-mirror-retirement.json",
  ".gtkb-state/**"
]
```

In-root declaration per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: every path above is under `E:/GT-KB/`. No out-of-root targets.

**No KB / MemBase mutation in this slice.** `groundtruth.db` is intentionally **not** in `target_paths`. Slice 2 edits markdown rule files, PowerShell scripts, narrative-artifact-approval JSON packet files, and bridge files; it does not insert/update/version any row in `specifications`, `work_items`, `projects`, `deliberations`, or any other MemBase table. WI-4214 status advancement (currently `backlogged`) is deferred to a later admin step or auto-retire scanner — not performed by this slice's implementation.

## Project Linkage

- **Project:** `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`. Authorized active project; carries the WI-4214 multi-slice umbrella retirement work.
- **Work Item:** `WI-4214` ("Retire orphaned role-assignments.json legacy mirror (multi-slice)") — current `stage=backlogged, status=open`. This slice advances WI-4214 toward completion; Slice 1 closed the writer-side, this slice closes the reader-side. A future slice may close the WI fully (physical mirror deletion).
- **Project Authorization:** `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1`. The `## PAUTH Scope Disclosure` section above explicitly flags the scope-extension question. Mechanical metadata gate satisfied; substantive scope-authority is Codex's call per the three valid paths enumerated there.

## Implementation Plan

### Step 1 — Rule edits (5 files)

Each edit removes the load-bearing "SOT" / "single source of truth" claim attached to `harness-state/role-assignments.json` and repoints to `harness-state/harness-registry.json`. The edits are minimal-surface; they preserve all surrounding text including legacy compatibility statements (`acting-prime-builder.md` line 25 is preserved as a READ-accepted compatibility statement, not removed).

For each rule file:

1. Identify each citation site (grep `role-assignments` → 17 hits across 5 files; see `## Current State` table for distribution).
2. For citations that claim authority/SOT, rewrite to point at `harness-state/harness-registry.json` (the live SOT) with an inline note that the mirror persists as orphan compatibility evidence until a future slice retires it.
3. For citations that describe the legacy file as compatibility-only (e.g. acting-prime-builder.md line 25), preserve them unchanged or strengthen the compatibility framing.
4. Verify final state: zero "authoritative" / "SOT" / "source of truth" claims on `role-assignments.json` across the 5 files.

### Step 2 — PowerShell script edits (5 files)

For each script citing `role-assignments.json`:

1. Replace the read-path from `role-assignments.json` to `harness-registry.json` and adjust the field-extraction code to match the registry schema (`harnesses` is a list with `id` + `role` fields, not a dict keyed by harness ID).
2. Update the inline guidance comments that name the file (e.g. "Role map source: …") to reference the registry.
3. Update the `Before writing any review result, re-read …` guidance to point at the registry.
4. The two `*-noconsole.generated.ps1` files are generated artifacts; the canonical generator is `independent-progress-assessments/bridge-automation/build-noconsole.ps1` or similar. This slice updates both the source `.ps1` and the generated `.generated.ps1` to ensure the next regen does not undo the cleanup; a follow-on micro-slice may update the generator if it embeds the literal.

### Step 3 — Narrative-artifact-approval packets

For each of the 5 rule files, generate a packet via the canonical CLI **after** the working-tree edit completes (the packet captures the post-edit blob sha256):

```text
python -m groundtruth_kb generate-approval-packet \
  --kind narrative \
  --target <.claude/rules/...> \
  --artifact-id claude-rules-<basename>-md-mirror-retirement \
  --action update \
  --source-ref gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint \
  --explicit-change-request "Slice 2: repoint rule citations from harness-state/role-assignments.json to harness-state/harness-registry.json (registry is the canonical SOT per Slice 1 VERIFIED). Compatibility statements preserved." \
  --change-reason "S388 owner directive: complete governed retirement of role-assignments.json as load-bearing surface. Slice 2 closes the reader-side; Slice 1 closed the writer-side." \
  --approval-mode approve \
  --changed-by claude-prime-builder/B \
  --out .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-<basename>-md-mirror-retirement.json \
  --stage
```

Per the feedback note from prior session memory, packet generation must happen post-edit (otherwise the captured sha differs from the post-edit blob).

### Step 4 — Spec-derived verification

Run the spec-to-test mapping from `## Spec-Derived Verification Plan` below. All checks must pass before commit.

### Step 5 — Scoped commit (the (b) audit-trail repair)

Stage **only** the files this slice touches (use exact `git add <path>`, never `-A`, per feedback note `[Check concurrent sessions before shared writes]`):
- The 5 rule files (post-edit).
- The 5 PowerShell scripts (post-edit).
- 5 narrative-artifact-approval packets.
- This bridge proposal + its INDEX entry.
- The post-implementation report bridge file (`-003 NEW` to be filed after commit).

Commit message: `refactor(rules): retire role-assignments.json reader-side cite; repoint to harness-registry.json (Slice 2 of WI-4214)`.

This scoped commit IS the audit-trail repair for (b). The prior contaminating commit `e31bbef5` is documented in the `-005 REVISED` post-impl report on the original thread (separately filed after this slice VERIFIED).

### Step 6 — Post-implementation report

File `-003 NEW` on this slice's thread with implementation evidence + spec-to-test results. Codex reviews and (expected) VERIFIES.

## Spec-Derived Verification Plan

| Specification / Decision | Verification | Result Criterion |
|---|---|---|
| `REQ-HARNESS-REGISTRY-001` (registry-as-SOT) | `python -c "import pathlib; total = sum(1 for p in pathlib.Path('.claude/rules').glob('*.md') for line in p.read_text(encoding='utf-8').splitlines() if 'role-assignments.json' in line and ('source of truth' in line.lower() or 'sot' in line.lower() or 'single role artifact' in line.lower() or 'role map' in line.lower())); print(total)"` | Prints `0` (no remaining SOT claims). |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale SOT cite) | `rg -l "harness-state/role-assignments.json" .claude/rules/ | xargs grep -L "compatibility\|orphaned\|retired\|registry is the canonical"` | Prints nothing (every remaining mention is in a compatibility/historical context). |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (rule text aligns with ADR) | Inspection: `.claude/rules/operating-role.md` and `.claude/rules/canonical-terminology.md` describe the registry as SOT consistent with `source_of_truth: "MemBase harnesses table (groundtruth.db)"` in the live registry. | Manual inspection passes. |
| PowerShell scripts repointed | `rg "harness-state.role-assignments.json" independent-progress-assessments/bridge-automation/` | Prints nothing. |
| PowerShell scripts read registry | `rg "harness-state.harness-registry.json" independent-progress-assessments/bridge-automation/` | Prints at least 5 hits (one per file). |
| Mirror file unchanged (not deleted in this slice) | `python -c "from pathlib import Path; print(Path('harness-state/role-assignments.json').exists())"` | Prints `True`. |
| Narrative-artifact-approval packets exist + validate | `python -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('.groundtruth/formal-artifact-approvals').glob('2026-06-03-claude-rules-*-mirror-retirement.json')]; print('OK')"` | Prints `OK` (5 packets parse cleanly). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All rows in this table executed | All criteria met. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | `python -c "from pathlib import Path; root = Path('.').resolve(); paths = ['.claude/rules/operating-role.md','independent-progress-assessments/bridge-automation/bridge-scan-common.ps1']; [Path(p).resolve().relative_to(root) for p in paths]; print('all in-root')"` | Prints `all in-root`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX coherence) | `python -c "import pathlib; t = pathlib.Path('bridge/INDEX.md').read_text(encoding='utf-8'); assert 'gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint' in t; print('OK')"` | Prints `OK`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (this `## Specification Links` section) | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint` | `preflight_passed: true`, `missing_required_specs: []`. |
| ADR/DCL clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint` | Exit 0; no blocking gaps. |

## Risk & Rollback

**Risk 1 — Generated PowerShell scripts regenerate from a source that re-introduces the mirror citation.** The two `*-noconsole.generated.ps1` files are generated artifacts; if the canonical generator embeds the mirror path literal, future regen undoes this slice. Mitigation: this slice updates both source and generated. A follow-on micro-slice can update the generator if it embeds the literal. The post-impl report will document the generator state explicitly.

**Risk 2 — Codex NO-GO on PAUTH scope (Slice-1 PAUTH cited for Slice-2 work).** Already disclosed in `## PAUTH Scope Disclosure` at top. If NO-GO arrives on this basis, the next move is owner AUQ to create `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-2` and refile as REVISED.

**Risk 3 — Narrative-artifact-approval-gate blocks rule edits.** Each rule file is a protected narrative artifact; Write/Edit requires a packet. Mitigation: Step 3 generates packets per file before Write; env var `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` is set per write. Order: edit working-tree first (gate fires; expected block), generate packet (captures post-edit sha), then re-write (this time with packet env var set, gate passes). This per-file order is documented in `feedback_s378_narrative_artifact_packet_recipe.md`.

**Risk 4 — Concurrent session contaminates the implementation commit (repeat of F2 root cause).** Mitigation: this proposal's commit uses exact `git add <path>` per file, never `git add -A` or `git add .`. Pre-commit, check `active-claude-session*.lock` heartbeats and recent bridge writes to detect mid-commit peers. Auto-memory feedback `[Check concurrent sessions before shared writes]` is the authority.

**Risk 5 — Mirror file still exists, future drift possible.** The mirror file persists on disk. Future readers that ignore this slice's repoint could re-introduce the contradiction. Mitigation: documentation in rule text labels the file as `orphan / no live writer / awaiting physical retirement in a future slice`. A future slice (Slice 3?) can physically delete the file with owner AUQ.

**Rollback (per step):**
- Rule edits: `git checkout HEAD -- .claude/rules/<file>.md` for each.
- PowerShell script edits: same, per file.
- Narrative-artifact-approval packets: `rm .groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-*-mirror-retirement.json`.
- Bridge files: `git rm --cached` if staged, otherwise leave on disk (append-only audit trail).
- INDEX entry: if added before commit, revert via `git checkout HEAD -- bridge/INDEX.md`; if committed, file a separate REVISED.

## Applicability Preflight

To be populated post-INDEX-entry. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The proposal text deliberately includes the canonical content patterns that trigger the cross-cutting specs registered in `config/governance/spec-applicability.toml`.

If the preflight reports missing required specs, this proposal is REVISED before the INDEX entry stays NEW. Author will paste the actual `## Applicability Preflight` output here as a final pre-filing self-check.

## Clause Applicability

To be populated post-INDEX-entry. Expected outcomes for each clause registered in `config/governance/adr-dcl-clauses.toml`:

| Clause | Expected outcome | Evidence in this proposal |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply, evidence_found | `## Target Paths` declares in-root; `## Current State` table refers to in-root files only. |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply, evidence_found | INDEX entry filed alongside this proposal; append-only respected. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply, evidence_found | `## Specification Links` is concrete (19 IDs cited with versions + statuses; no TBD/TODO). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply, evidence_found | `## Spec-Derived Verification Plan` table maps each spec to a verification step. |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply (not bulk backlog mutation; the WI-4214 work this advances is a single multi-slice WI, not bulk transition) | n/a |

Expected: exit 0; no blocking gaps.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
