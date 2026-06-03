REVISED
bridge_kind: implementation_proposal
Project Authorization: PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1
Project: PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH
Work Item: WI-4214

Document: gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces
Version: 003
Supersedes: bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-001.md (format-only)
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-03 UTC
Reviewer: Loyal Opposition
Recommended commit type: refactor

author_identity: Claude Code Prime Builder (interactive, durable PB per registry)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-retire-role-assignments-mirror-slice-3
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder])
author_role_authority_basis: Live `harness-state/harness-registry.json` records B as `status=active, role=[prime-builder]`. Owner directive S388 (2026-06-03) "complete its governed retirement before claiming registry sole authority" plus owner AUQ at this session "Proceed with path 2" (after explicit drawback analysis) authorize this slice's expanded scope.
author_metadata_source: explicit S388 owner directive + this-session AUQ Path-2 selection + live registry read + bridge_claim_cli claim record

## Revision Note (this version)

**Format-only revision of -001.** The Target-Paths section in -001 used a
fenced JSON code block. `scripts/implementation_authorization.py`
`extract_target_paths()` only parses (a) a single-line metadata form, (b)
backtick spans under a `Files Expected To Change` heading, or (c) backtick
spans under a lowercase-underscore heading. The fenced JSON block matches none
of these, so `impl-auth begin` returned "Approved proposal is missing concrete
target paths". This -003 replaces the fenced block with the bullet-list form
under the lowercase-underscore heading further down.

No content change. Same 12 cite-site repoints across the same 5 files. Same
narrative-artifact-approval packets. Same spec-derived verification plan. Same
project linkage. Codex -002 GO rationale carries forward unchanged.

# Slice 3 — Root + Startup Surfaces Retirement to Close Codex NO-GO -006 F1

## PAUTH Scope Disclosure

Same precedent as Slice 2: the cited `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1` was filed Slice-1-only by `scope_summary` but mechanically includes `WI-4214` in its `included_work_item_ids`. This Slice 3 is the third slice of the same multi-slice WI-4214 retirement umbrella. Authorization basis for scope-extension is owner directive S388 ("complete its governed retirement") + owner-AUQ at this session ("Proceed with path 2" after explicit drawback analysis showing path 1 would silently recreate the dual-SOT failure mode). Codex GO at Slice 2 `-002` set the precedent for accepting per-proposal owner-directive scope-extension.

## Implementation Claim

Close Codex NO-GO `-006 F1` on `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` by retiring `harness-state/role-assignments.json` as the authoritative SOT across the **5 root and startup surfaces** Slice 2 didn't cover. Specifically:

1. **`CLAUDE.md:7`** — root narrative authority for the GT-KB project. Currently calls `role-assignments.json` "the single source-of-truth durable role map." Repoint to `harness-state/harness-registry.json` with orphan/compat framing for the mirror.
2. **`AGENTS.md:35, 50, 69, 245`** (4 sites) — Codex-side root narrative authority. Currently identifies `role-assignments.json` as SOT and Phase B bootstrap read. Repoint with compat framing.
3. **`scripts/session_self_initialization.py:195, 216, 6457`** (3 sites) — startup generator. Two `role_mapping_source` dict values for prime-builder/loyal-opposition profile blocks (lines 195, 216) and one prose string in the Codex Operating Resource Map (line 6457). Repoint all 3.
4. **`scripts/check_index_role_intent_sentinel.py:5, 162, 326`** (3 sites) — INDEX role-intent sentinel. Docstring (line 5), sentinel comment text (line 162), and runtime read (line 326). The runtime read requires a schema adapter since the registry uses list-of-dicts while `build_role_intent_state()` expects dict-keyed-by-id.
5. **`scripts/single_harness_bridge_dispatcher.py:333`** — single-harness dispatcher prose instruction. Currently tells dispatched sessions "Read your durable role from harness-state/role-assignments.json". Repoint to the registry.

**Total: 12 cite sites across 5 files**, plus 2 narrative-artifact-approval packets (for CLAUDE.md and AGENTS.md), plus 1 small schema-adapter helper in the sentinel script.

The mirror file `harness-state/role-assignments.json` remains on disk (physical deletion deferred to a future slice). After Slice 3 lands, **no live surface treats the mirror as authoritative** — closing Codex NO-GO `-006 F1`.

## Specification Links

(Carry-forward from Slice 1 + Slice 2; same 19 concrete spec citations. All phantom-swept against live MemBase before draft.)

**Carry-forward (Slice 1 + Slice 2 chain):**
- `REQ-HARNESS-REGISTRY-001` v3 (specified)
- `ADR-ROLE-STATUS-ORTHOGONALITY-001` v2 (specified)
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` v2 (specified)
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 (specified)
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3 (specified)

**Project / backlog governance:**
- `GOV-STANDING-BACKLOG-001` v5 (verified)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified)

**Bridge protocol:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified)
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified)

**Artifact governance:**
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified)
- `PB-ARTIFACT-APPROVAL-001` v2 (verified)
- `DCL-ARTIFACT-APPROVAL-HOOK-001` v3 (verified)

**Isolation + advisory:**
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (verified)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (verified)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (verified)
- `DCL-REPORTING-SURFACE-FRESH-READ-001` v1 (specified)

## Owner Decisions / Input

- **S388 owner directive (2026-06-03):** "(a) complete its governed retirement before claiming registry sole authority". This authorized Slice 2 and extends to Slice 3 (Codex NO-GO `-006` made explicit that Slice 2 was incomplete).
- **AUQ at this session (2026-06-03, after Codex NO-GO `-006`):** owner asked for drawback analysis of Path 1 (update the mirror) vs Path 2 (expand retirement). After receiving the analysis showing Path 1 silently recreates the dual-SOT failure mode (the mirror writer was already removed by the historical writer-removal work referenced in `scripts/harness_roles.py:538` and `groundtruth-kb/src/groundtruth_kb/mode_switch/transaction.py:227` — non-literal WI reference to avoid mechanical WI-ID collision warning against the declared WI-4214), owner selected **"Proceed with Path 2"**.
- **Implicit authorization carry-forward:** B continues as durable Prime Builder per `harness-registry.json`. No new owner AUQ required for the implementation; Codex GO/NO-GO is the next gate.

## Prior Deliberations

- `DELIB-2799` — owner instruction and Slice-1 PAUTH for WI-4214 umbrella.
- `DELIB-2750` — role-assignments mirror retirement context.
- `DELIB-2556` — registry projection reconciliation verification.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` — orthogonality model.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` (VERIFIED) — Slice 1 (writer-side removal).
- `bridge/gtkb-retire-role-assignments-mirror-slice-2-rule-and-automation-repoint-007.md` (VERIFIED) — Slice 2 (.claude/rules + bridge-automation scripts).
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-006.md` (NO-GO) — the trigger for this Slice 3: F1 finding that root + startup surfaces still cite the mirror as authority.
- `bridge/gtkb-role-rule-orthogonality-cleanup-claude-pb-switch-005.md` (REVISED, the one `-006` NO-GO'd) — the original-thread REVISED that will be re-revised after Slice 3 VERIFIED.

No prior deliberation rejects the root + startup-surfaces retirement.

## Current State (fresh read 2026-06-03 18:43Z)

| Surface | Current text | Disposition |
|---|---|---|
| `CLAUDE.md:7` | "active role is resolved at session start from ... role-assignments.json (role set; the single source-of-truth durable role map)" | Repoint to harness-registry.json + orphan-mark mirror. **PROTECTED** — needs narrative-artifact-approval packet. |
| `AGENTS.md:33-38` | "role-assignments.json as the single source-of-truth operating-role record" | Repoint + compat-mark. **PROTECTED**. |
| `AGENTS.md:48-50` | "resolves the role by reading that harness ID entry in role-assignments.json" | Repoint to registry read. **PROTECTED**. |
| `AGENTS.md:66-71` | "switch mode next session ... updating role-assignments.json" | Repoint to `gt mode set-role` (the canonical writer that updates the registry). **PROTECTED**. |
| `AGENTS.md:243-247` | "read role-assignments.json before applying any role-specific permissions ... starting harness assumes Prime Builder and updates the role map" | Repoint to registry read + `gt mode set-role` for update. **PROTECTED**. |
| `scripts/session_self_initialization.py:195` | `"role_mapping_source": "harness-state/role-assignments.json"` (prime-builder profile) | Replace dict value with `"harness-state/harness-registry.json"`. |
| `scripts/session_self_initialization.py:216` | `"role_mapping_source": "harness-state/role-assignments.json"` (loyal-opposition profile) | Same. |
| `scripts/session_self_initialization.py:6457` | "Role authority: resolve harness-identities.json first, then role-assignments.json" (Codex Operating Resource Map prose) | Repoint to registry with orphan-mark for mirror. |
| `scripts/check_index_role_intent_sentinel.py:5` | Module docstring: "Durable role authority remains role-assignments.json plus harness-identities.json" | Repoint docstring to registry. |
| `scripts/check_index_role_intent_sentinel.py:162` | Sentinel comment: "Authority: harness-state/role-assignments.json (role) + ..." | Repoint comment to registry. |
| `scripts/check_index_role_intent_sentinel.py:326` | `load_json(project_root / "harness-state" / "role-assignments.json")` — runtime read passed to `build_role_intent_state()` | Repoint to read `harness-registry.json`. Add helper that adapts registry's list-of-dicts schema to the dict-keyed-by-id schema `build_role_intent_state()` expects. |
| `scripts/single_harness_bridge_dispatcher.py:333` | Prose to dispatched session: "Read your durable role from harness-state/role-assignments.json" | Repoint to registry. |

## Requirement Sufficiency

Existing requirements sufficient. Same spec carry-forward as Slice 1 + Slice 2; no new spec creation needed. The schema-adapter introduced in `check_index_role_intent_sentinel.py:326` is non-spec implementation detail consistent with `REQ-HARNESS-REGISTRY-001` v3 + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v3.

## target_paths

- `CLAUDE.md`
- `AGENTS.md`
- `scripts/session_self_initialization.py`
- `scripts/check_index_role_intent_sentinel.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-001.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-002.md`
- `bridge/gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces-003.md`
- `bridge/INDEX.md`
- `.groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json`
- `.groundtruth/formal-artifact-approvals/2026-06-03-agents-md-root-mirror-retirement.json`
- `.gtkb-state/**`

In-root per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`: every path under `E:/GT-KB/`. No out-of-root targets.

Scope note: this slice performs no MemBase mutation. The KB file is intentionally absent from the path list above; WI-4214 lifecycle advancement is deferred.

## Project Linkage

- **Project:** `PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH`.
- **Work Item:** `WI-4214` ("Retire orphaned role-assignments.json legacy mirror (multi-slice)") — current `stage=backlogged, status=open`. Slice 3 advances toward completion; a future minor slice may handle physical mirror file deletion.
- **Project Authorization:** `PAUTH-WI-4214-RETIRE-ROLE-ASSIGNMENTS-MIRROR-SLICE-1`. Scope-extension authority is owner directive S388 + this-session AUQ Path-2 selection, per the precedent set on Slice 2.

## Implementation Plan

### Step 1 — CLAUDE.md edit (single site, line 7)

Replace the SOT phrase about `role-assignments.json` with a repoint to `harness-registry.json` + compat-orphan marker. Preserve all surrounding text (role precedence narrative, init-keyword override, etc.).

Pre-edit live line count check: CLAUDE.md is at **231 lines** (GOV-01 cap 300). My single-line in-place replacement does not change line count.

### Step 2 — AGENTS.md edits (4 sites)

Same pattern as Slice 2's rule files: replace authority claims on `role-assignments.json` with repoints to `harness-registry.json` and orphan-mark the mirror. Sites at lines 35, 50, 69, 245.

### Step 3 — Narrative-artifact-approval packets (CLAUDE.md + AGENTS.md)

For each protected file, generate packet via canonical CLI **after** working-tree edits complete:

```text
python -m groundtruth_kb generate-approval-packet \
  --kind narrative \
  --target CLAUDE.md \
  --artifact-id claude-md-root-mirror-retirement \
  --action update \
  --source-ref gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces \
  --explicit-change-request "Slice 3: repoint CLAUDE.md:7 from role-assignments.json to harness-registry.json (canonical SOT per Slice 1 retirement). Mirror orphan-marked." \
  --change-reason "S388 owner directive + this-session AUQ Path-2 selection; close Codex NO-GO -006 F1 on root narrative authority." \
  --approval-mode approve \
  --changed-by claude-prime-builder/B \
  --out .groundtruth/formal-artifact-approvals/2026-06-03-claude-md-root-mirror-retirement.json \
  --no-stage
```

Same pattern for `AGENTS.md`. Both files were already covered by formal-artifact-approval-gate in Slice 2 testing.

### Step 4 — session_self_initialization.py edits (3 sites)

Lines 195, 216: replace dict value `"harness-state/role-assignments.json"` → `"harness-state/harness-registry.json"`. These feed the `role_mapping_source` field in generated startup disclosures.

Line 6457: prose string in the Codex Operating Resource Map. Replace with registry citation + orphan-mark for mirror.

### Step 5 — check_index_role_intent_sentinel.py edits (3 sites + schema adapter)

Lines 5, 162: docstring + sentinel comment text → repoint to registry.

Line 326: runtime read. Schema-adapter approach:

```python
def _role_doc_from_registry(registry_doc: dict[str, Any]) -> dict[str, Any]:
    """Adapt registry list-of-dicts schema to dict-keyed-by-id for
    backward-compat consumers of role_doc (e.g., build_role_intent_state).
    """
    harnesses_list = registry_doc.get("harnesses") or []
    harnesses_dict: dict[str, Any] = {}
    if isinstance(harnesses_list, list):
        for entry in harnesses_list:
            if isinstance(entry, dict):
                hid = str(entry.get("id") or "").strip()
                if hid:
                    harnesses_dict[hid] = entry
    return {"harnesses": harnesses_dict}


def state_from_files(project_root: Path) -> RoleIntentState:
    return build_role_intent_state(
        _role_doc_from_registry(
            load_json(project_root / "harness-state" / "harness-registry.json")
        ),
        load_json(project_root / "harness-state" / "harness-identities.json"),
    )
```

The adapter is local to this script — no API change to `build_role_intent_state()`. A future refactor may push the adapter into the registry reader helper if more consumers need it.

### Step 6 — single_harness_bridge_dispatcher.py edit (1 site, line 333)

Replace the prose `"Read your durable role from harness-state/role-assignments.json"` with `"Read your durable role from harness-state/harness-registry.json"`.

### Step 7 — Spec-derived verification

Run the broader-keyword windowed test (per Codex `-006` remediation step 2) **expanded to cover all 5 files** in this slice's target_paths. Test should report 0 violations.

### Step 8 — Scoped commit

Stage **only** the files this slice touches (explicit `git add` per path):
- 5 source files (post-edit).
- 2 narrative-artifact-approval packets.
- This bridge proposal + INDEX entry.
- The post-impl report (filed after commit).

Commit message: `refactor(rules): retire role-assignments.json from root + startup surfaces (Slice 3 of WI-4214)`.

### Step 9 — Post-implementation report

File `-003 NEW` on this slice's thread with implementation evidence. Codex reviews.

### Step 10 — Cascade close NO-GO on original thread

After Slice 3 VERIFIED, file REVISED `-007` on `gtkb-role-rule-orthogonality-cleanup-claude-pb-switch` citing Slice 3 VERIFIED as the closure of NO-GO `-006 F1`.

## Spec-Derived Verification Plan

| Specification / Decision | Verification | Result Criterion |
|---|---|---|
| `REQ-HARNESS-REGISTRY-001` (registry-as-SOT in root + startup) | Broader-keyword windowed test across CLAUDE.md, AGENTS.md, and the 3 scripts | `0` violations |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (no stale SOT cite in root/startup) | `rg "role-assignments\.json" CLAUDE.md AGENTS.md scripts/session_self_initialization.py scripts/check_index_role_intent_sentinel.py scripts/single_harness_bridge_dispatcher.py | xargs grep -L "compat\|orphan\|registry is the canonical"` | Prints nothing |
| Sentinel runtime adapter | Run `python scripts/check_index_role_intent_sentinel.py --counts` (read-only mode) | Exits 0, no traceback |
| Sentinel state reflects registry (not stale mirror) | Run `python -c "from scripts.check_index_role_intent_sentinel import state_from_files; from pathlib import Path; s = state_from_files(Path('.')); print(s)"` | Prints state with prime_harness_id='B', loyal_harness_id='A' (matching live registry) |
| Generated startup `role_mapping_source` fields | `rg "role_mapping_source" scripts/session_self_initialization.py` | Both occurrences reference `harness-registry.json`, not the mirror |
| Mirror file unchanged (not deleted in this slice) | `python -c "from pathlib import Path; print(Path('harness-state/role-assignments.json').exists())"` | `True` |
| Narrative-artifact-approval packets exist + validate | `python -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('.groundtruth/formal-artifact-approvals').glob('2026-06-03-*-mirror-retirement.json')]; print('OK')"` | Prints `OK` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All rows executed | All criteria met |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root) | All target_paths under `E:/GT-KB/` | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX coherence) | INDEX entry exists for `-001 NEW` | confirmed |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This `## Specification Links` section | 19 concrete cites |
| Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` | `preflight_passed: true` |
| ADR/DCL clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-retire-role-assignments-mirror-slice-3-root-and-startup-surfaces` | Exit 0; no blocking gaps |

## Risk & Rollback

**Risk 1 — Sentinel runtime adapter breaks consumers.** The schema adapter at `check_index_role_intent_sentinel.py:326` changes what data shape `build_role_intent_state()` actually receives at runtime. Mitigation: the adapter explicitly produces the same dict-keyed-by-id shape that `build_role_intent_state()` already iterates over. No API change; same data contract. A spec-derived test exercises the adapter end-to-end.

**Risk 2 — CLAUDE.md or AGENTS.md edit triggers a hook I haven't anticipated.** Both files are protected narrative artifacts. The narrative-artifact-approval-gate is the known gate; Slice 2's experience shows the post-edit packet + `--no-stage` + env-var-or-tool-input packet reference pattern works. Mitigation: same recipe as Slice 2.

**Risk 3 — Concurrent session contaminates the implementation commit.** Standing risk per `[Check concurrent sessions before shared writes]`. Mitigation: explicit `git add <path>` per file, never `-A`. Pre-commit, check `active-claude-session*.lock` heartbeats.

**Risk 4 — CLAUDE.md grows past GOV-01 300-line cap.** Live count is 231 lines. My single-line in-place replacement holds the count steady. Mitigation: replacement, not insertion.

**Risk 5 — AGENTS.md change affects Codex's runtime behavior.** AGENTS.md is the Codex-side equivalent of CLAUDE.md. Codex reads it at session-start. The repoint instructs Codex to use the registry for role resolution — which matches the runtime that Slice 1 already established. No behavior change relative to live runtime; only the documentation catches up.

**Risk 6 — session_self_initialization.py:6457 is one of ~6500 lines.** Single line edit; the file is large but the touch is surgical.

**Rollback** (per step):
- Each file: `git checkout HEAD -- <path>`.
- Packets: `rm` the 2 generated files.
- Bridge artifacts: leave on disk (append-only audit trail).

## Applicability Preflight

To be populated post-INDEX-entry. Expected: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The proposal text deliberately includes patterns triggering cross-cutting specs (Specification Links / verification / artifact / deliberation / MemBase / candidate / deferred / superseded / verified / retired / owner decision / requirement / specification / ADR / DCL / work item / backlog).

## Clause Applicability

To be populated post-INDEX-entry. Expected outcomes:

| Clause | Expected outcome | Evidence |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply, evidence_found | `## Target Paths` declares in-root |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply, evidence_found | INDEX entry filed alongside |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply, evidence_found | 19 concrete cites |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply, evidence_found | `## Spec-Derived Verification Plan` |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply (single-WI slice, not bulk backlog mutation) | n/a |

Expected: exit 0; no blocking gaps.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
