REVISED

# Phase-1 Mirror-Retirement REVISED-2 — bundle DCL-HARNESS-STATE-SOT-ASSERTION-001 v2 correction (owner-authorized) + 5-surface deletion; verification mapped to the corrected live assertions

bridge_kind: implementation_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-004.md (NO-GO)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-010.md
Prereq (VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-010.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4336
work_item_ids: [WI-4336, WI-4327]

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 5719749f-e6b7-48bd-a999-90fb527c5c37
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session, /loop dynamic-pacing

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-06-05-DCL-HARNESS-STATE-SOT-ASSERTION-001-v2.json", "harness-state/role-assignments.json", "config/governance/protected-artifact-inventory-drift.toml", "scripts/collect_dev_environment_inventory.py", ".groundtruth/inventory/dev-environment-inventory.json", "platform_tests/scripts/test_mirror_retirement_role_assignments.py"]

# groundtruth.db is in target_paths for the DCL-HARNESS-STATE-SOT-ASSERTION-001 v2
# membase_spec_insert ONLY (formal-artifact-approval packet). NO WI-lifecycle
# resolution is in scope (deferred to project-completion reconciliation per
# rule-files -002 F1). PAUTH rowid 134 v2 covers membase_spec_insert,
# file_deletion, config_file, source_file, test_file.

requires_verification: true
implementation_scope: implementation

## Revision Claim

REVISED-2 resolves the NO-GO at `-004` per the **owner AskUserQuestion decision this session (2026-06-05): "Amend the DCL (recommended)"**. The -004 NO-GO was correct on every point: a backlog item (WI-4372) cannot waive a blocking spec, and the -003 "no live reads" narrowing did not match the live `DCL-HARNESS-STATE-SOT-ASSERTION-001` v1 text ("grep 'role-assignments' returns 0 matches"). Rather than narrow the verification without governance (rejected) or scrub ~67 legitimate references (rejected), this REVISED amends the **defective spec itself** to its intended scope, then deletes against the corrected, consistent assertions.

| Codex -004 finding | Resolution in this REVISED-2 |
|---|---|
| **F1 (P1)** — verification under-proves the live blocking retired-path specs; narrowing to "no live reads" without an owner waiver / governed amendment / sufficient implementation | **Codex path 2 (governed spec amendment), owner-authorized.** This proposal amends `DCL-HARNESS-STATE-SOT-ASSERTION-001` to v2, narrowing assertion #1 from "0 string matches" to "no LIVE retired-path reads outside whitelisted bridge/audit/packet/provenance contexts" — aligning it with `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` assertion (b) AND with the DCL's own original WI-4327 intent ("all readers go through canonical entrypoint"). Verification then maps to the corrected live assertions (§Specification-Derived Verification Plan). |
| **F2 (P2)** — empty `assertions` column does not weaken the normative DCL text | **Accepted; mapped to executable tests (Codex's second option in F2).** v2 keeps the descriptive assertions normative and maps the mirror-specific ones (#1 amended, #4) to `test_mirror_retirement_role_assignments.py`. No claim that the empty machine column lowers the bar. |
| **F3 (P4)** — inventory baseline reference count stale (4 matches, not 3) | **Corrected and made line-count-free.** Acceptance now requires a post-regeneration **zero-match** grep of the inventory for `role-assignments`, not a fixed line count. |
| **Revision Required #3** — fate of compatibility writer-path code in `scripts/harness_roles.py` | **Clarified (verified):** `write_role_assignments()` has **no live caller** (grep-verified); `_mirror_role_assignments_to_registry()` is the authoritative role write. The dead writer does NOT recreate the deleted mirror at runtime. It is a retained NON-READING reference explicitly permitted by amended assertion #1; its eventual removal is WI-4372 hygiene. |

## DCL-HARNESS-STATE-SOT-ASSERTION-001 v2 — proposed amended text

The implementation will insert v2 via a formal-artifact-approval packet (owner presents/approves the exact content at implementation time per `GOV-ARTIFACT-APPROVAL-001`). Proposed v2 description (only assertion #1 + the Enforcement/rationale notes change; assertions #2–#5 unchanged):

```
DCL-HARNESS-STATE-SOT-ASSERTION-001 v2 - Machine-checkable consistency assertions.

Constraint: 5 assertions MUST evaluate against the live repo state and MUST PASS:
1. No LIVE retired-path reads: no active code performs a runtime read of
   harness-state/role-assignments.json (json.load / json.loads / read_text /
   open(...,'r') / tomllib.load resolving that path) outside whitelisted
   bridge/audit/packet contexts. The sole role-state read path is the canonical
   reader entrypoint groundtruth_kb.harness_projection (readers resolve role
   state from harness-state/harness-registry.json). Retained NON-READING
   references are explicitly permitted: the path-constant definition and
   signature-compat path resolver (ROLE_ASSIGNMENTS_RELATIVE_PATH,
   role_assignments_path), the uncalled compatibility writer
   (write_role_assignments), migration docstrings/comments,
   formal-artifact-approval packet-builder content (scripts/_build_*_packet.py),
   the doctor predicate's own retired-path token literal, SoT-registry records,
   and narrative provenance - these document the retirement and do not read the
   mirror.
2. No out-of-entrypoint direct reads: grep for json.load.*harness-state/ and
   tomllib.load.*harness-capability-registry.toml outside
   groundtruth_kb.harness_projection returns 0 matches.
3. Canonical entrypoint exists and exports read_roles/read_identity/read_capabilities.
4. Retired paths are physically absent post-WI-4336.
5. 3 SoT files parse + pass schema validation.

Enforcement: Assertions evaluated against live repo state; the mirror-specific
assertions (#1 amended, #4) are proven by
platform_tests/scripts/test_mirror_retirement_role_assignments.py. The doctor
predicate _check_harness_state_sot_consistency rolls up SoT consistency at WARN
severity; refinement of that predicate to match this amended assertion #1
(live-read distinction vs token-mention) is tracked under WI-4372. Severity:
blocking. Affected by: GOV-HARNESS-STATE-SOT-CONSOLIDATION-001.

v2 amendment rationale (owner AUQ 2026-06-05): v1 assertion #1 ("grep
'role-assignments' returns 0 matches" across scripts/, groundtruth-kb/src/,
config/, .claude/rules/, CLAUDE.md, AGENTS.md) was self-contradictory and
unsatisfiable - the doctor predicate that enforces it must itself contain the
token to grep for it, and the assertion flagged legitimate retained references
(packet-builder content, migration docstrings, provenance). v2 narrows
assertion #1 to the original WI-4327 intent ("all readers go through canonical
entrypoint" = no LIVE reads of the mirror), aligning it with
RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 assertion (b). The substantive
SoT guarantee (no live read of the retired mirror; canonical entrypoint sole
read path) is preserved; this is a correction-to-intent, not a weakening.

Owner AUQ approval captured 2026-06-05 (amend-DCL decision); prior Phase-1 batch
AUQ 3 of 4 (v1).
```

## PAUTH Forbidden-Operation Analysis (`weaken_existing_role_assertions`)

PAUTH rowid 134 v2 lists `weaken_existing_role_assertions` among `forbidden_operations`. This amendment is **not** such a violation:

1. **Target is project-created, not a pre-existing role assertion.** `DCL-HARNESS-STATE-SOT-ASSERTION-001` was authored BY this project (WI-4327) and is **not** in the PAUTH `included_spec_ids` (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-ARTIFACT-APPROVAL-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`). The forbidden-op protects pre-existing role-**STATE** assertions (e.g., `GOV-HARNESS-ROLE-PORTABILITY-001`, role-set invariants), which are untouched here.
2. **Substantive guarantee preserved.** The SoT protection (no live read of the retired mirror; `groundtruth_kb.harness_projection` is the sole role-state read path) is unchanged. Only the over-broad, self-contradictory **wording** is corrected to its intended scope.
3. **Correction of a defect, not a relaxation.** v1 assertion #1 can NEVER pass as written (the enforcement predicate's own token guarantees a match), so it is not a functioning protection being weakened — it is a defect being repaired toward the WI-4327 intent.
4. **Owner-authorized.** Owner chose "Amend the DCL" via AskUserQuestion this session, with full knowledge of the exact narrowing.

If Loyal Opposition nonetheless reads this as `weaken_existing_role_assertions`, Prime will **escalate to the owner for an explicit PAUTH amendment** before implementing, rather than proceed. No unilateral PAUTH mutation is performed by this proposal.

## Scope — DCL v2 amendment + deletion + 3 coupled surfaces + test

| # | Path | Action |
|---|------|--------|
| 1 | `groundtruth.db` | **INSERT** `DCL-HARNESS-STATE-SOT-ASSERTION-001` v2 (membase_spec_insert) via formal-artifact-approval packet. Append-only new version; no other rows touched; NO WI-lifecycle resolution. |
| 2 | `.groundtruth/formal-artifact-approvals/2026-06-05-DCL-HARNESS-STATE-SOT-ASSERTION-001-v2.json` | **CREATE** the owner-approval packet (presented_to_user=true, transcript_captured=true, full_content + sha256, approved_by=owner). |
| 3 | `harness-state/role-assignments.json` | **DELETE** (legacy mirror; orphan; zero live reads/writes verified). |
| 4 | `config/governance/protected-artifact-inventory-drift.toml` | **EDIT** — remove the `"harness-state/role-assignments.json",` pattern from `[[protected_artifacts]] id="harness-identity-and-role-state"`, leaving `harness-identities.json`. Block route=`governance_review`, `accept_with_inventory_baseline_update=false`, `required_evidence=["bridge report"]` — this child IS that report. |
| 5 | `scripts/collect_dev_environment_inventory.py` | **EDIT** — repoint `role_record_resolution` capability evidence (~L497) from `role-assignments.json` → `harness-registry.json`. |
| 6 | `.groundtruth/inventory/dev-environment-inventory.json` | **REGENERATE** — so the inventory-drift gate passes (governance_review route + bridge report) and no `role-assignments.json` reference remains. |
| 7 | `platform_tests/scripts/test_mirror_retirement_role_assignments.py` | **CREATE** — assert (a) file absent; (b) no live-code READS of the retired path; (c) drift-registry no longer lists it; (d) the DCL v2 row is live with the amended assertion #1. |

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as REVISED versioned file; INDEX entry at top; no prior-version deletion/rewrite. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan maps the corrected live assertions → executable test. |
| `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` | blocking | content:retire, deletion | Operative deletion authorization; assertions (a)+(b) become the test; the DCL v2 wording is aligned to (b). |
| `DCL-HARNESS-STATE-SOT-ASSERTION-001` | blocking | content:assertions | **Amended to v2** (this proposal); deletion verified against the corrected assertion #1 + #4. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:formal artifact (DCL) change | DCL v2 insert gated by a formal-artifact-approval packet (owner presents/approves content). Drift-registry block requires a bridge report (governance_review) — this child IS it. No protected NARRATIVE edited (toml/py/json are config/source; DCL v2 is a MemBase spec row, not a `.md` narrative file). |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces, retired paths | Retired path removed; registry sole roles SoT; DCL assertion corrected to the SoT-read intent. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Eliminates the stale mirror; assertion now correctly forbids LIVE reads of it. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Orphan deletion; **no role-set VALUE changes**; no role-state assertion weakened (see §PAUTH Forbidden-Operation Analysis). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH 134 v2; classes `membase_spec_insert`+`file_deletion`+`config_file`+`source_file`+`test_file` all covered; WI-4336+WI-4327 included. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites framing specs + harness-state SoT specs. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4336 (deletion) + WI-4327 (DCL artifact) primary; WI lifecycle resolution deferred (no groundtruth.db WI mutation). WI-4372 follow-on tracks doctor refinement + remaining L2 readers. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 1 new platform test (deletion + DCL-live assertions). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | content:E:\GT-KB | All target_paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry SoT canonical; mirror removed; DCL row is the canonical assertion text. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item | DCL amendment + deletion + cleanup as governed artifacts; owner decision archived. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Governed amendment + deletion; deliberation evidence cited. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:retired | RETIRE-SPEC terminal action; mirror lifecycle → deleted; DCL lifecycle → v2. |

## Requirement Sufficiency

**Existing requirements sufficient (with this owner-authorized spec amendment).** `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` is operative for the deletion. The DCL v1 assertion #1 was a defective requirement; the owner authorized its correction via AskUserQuestion this session. No NEW requirement is introduced — the amendment narrows an existing assertion to its documented WI-4327 intent. Evidence: owner AUQ 2026-06-05 (amend-DCL); DELIB-20260668 (AUQ#3 clean-delete); DELIB-20260669 (drift); DELIB-20260880 (PAUTH v2).

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-{foundation-012,scripts-source-010,rule-files-010}.md` — VERIFIED prerequisites.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-002.md` / `-004.md` — Codex NO-GOs that drove this revision. -004 F1 (under-proves live specs), F2 (empty assertions column), F3 (stale inventory count) — all addressed.
- `RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001` / `DCL-HARNESS-STATE-SOT-ASSERTION-001` — operative authorization + amended spec.
- `DELIB-20260668` (AUQ#3 clean delete) / `DELIB-20260669` (drift) / `DELIB-20260880` (PAUTH v2).
- `DELIB-20260763` / `DELIB-2750` — prior mirror-repoint review context (surfaced by Codex search at -004).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor (VERIFIED).
- Owner AUQ this session (2026-06-05, "Amend the DCL"); DA archival DELIB recorded with implementation (impl-start-gate quiescence on an unrelated parallel report currently blocks the pre-proposal `groundtruth.db` decision insert; the AUQ tool-use is the canonical owner-decision evidence per the AUQ-only enforcement stack).

No previously rejected approach is being revisited; the rejected full-scrub (A) and waiver-only (C) paths are documented in §Revision Claim.

## Owner Decisions / Input

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Resolve the mirror-retirement DCL-assertion blocker by **amending the DCL** (vs full scrub vs waiver+defer) | AskUserQuestion (this session, 2026-06-05) | Owner AUQ — recommended option chosen | This entire REVISED-2 approach |
| Clean-delete the mirror (no preservation) | AskUserQuestion | DELIB-20260668 AUQ#3 | The deletion |
| Phase-1 deletion batch approval | AskUserQuestion | RETIRE-SPEC "Phase-1 batch AUQ 4 of 4" | Authorizes WI-4336 |
| PAUTH v2 (WI-4336+WI-4214) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |
| DCL v2 **content** approval (exact text) | AskUserQuestion + formal-artifact-approval packet | Owner — captured at implementation time | The DCL v2 insert |

The DCL v2 *direction* is owner-approved (AUQ this session). The DCL v2 *exact content* will be presented to the owner for the formal-artifact-approval packet at implementation time per `GOV-ARTIFACT-APPROVAL-001` before the `membase_spec_insert`.

## Acceptance Criteria

1. `DCL-HARNESS-STATE-SOT-ASSERTION-001` v2 inserted (latest version) with the amended assertion #1, via a matching formal-artifact-approval packet (presented_to_user=true, content hash matches).
2. `harness-state/role-assignments.json` deleted (absent).
3. `protected-artifact-inventory-drift.toml` no longer lists the path; block retains `harness-identities.json`.
4. `collect_dev_environment_inventory.py` `role_record_resolution` evidence cites `harness-registry.json`.
5. `.groundtruth/inventory/dev-environment-inventory.json` regenerated; **post-regeneration grep of the inventory for `role-assignments` returns 0 matches** (line-count-free); inventory-drift pre-commit gate passes.
6. New test asserts file-absent + no-live-code-reads + drift-registry-absent + DCL-v2-row-live; GREEN. **This is the spec-derived proof of RETIRE-SPEC (a)+(b) and DCL v2 assertion #1 + #4.**
7. `ruff check` + `ruff format --check` GREEN on the changed `.py`.
8. Commit lands cleanly via explicit-path `git commit -- <targets>` (inventory-drift gate satisfied via governance_review + regenerated baseline); never `git add -A`.
9. No project-root-boundary violation.
10. **Explicitly NOT claimed:** doctor `_check_harness_state_sot_consistency` fully clean (WARN-only; refinement tracked in WI-4372).

## Phased Implementation Plan

1. **Pre-grep**: re-confirm 0 live READS of the retired path (record evidence); confirm `write_role_assignments` has no live caller.
2. **Present DCL v2 content to owner** (AskUserQuestion) → generate the formal-artifact-approval packet → **insert** `DCL-HARNESS-STATE-SOT-ASSERTION-001` v2.
3. **Repoint generator**: `collect_dev_environment_inventory.py` `role_record_resolution` → `harness-registry.json`.
4. **Remove drift-registry entry**: `protected-artifact-inventory-drift.toml`.
5. **Delete** `harness-state/role-assignments.json`.
6. **Regenerate** `.groundtruth/inventory/dev-environment-inventory.json`; confirm 0 `role-assignments` matches.
7. **Write** `test_mirror_retirement_role_assignments.py` (4 assertions; (b) targets live READ patterns, not all mentions; (d) reads the live DCL v2 row).
8. **Verify**: run the new test; `ruff check` + `ruff format --check` on the `.py`.
9. **Capture** the owner-decision DELIB (DA archival) now that a packet covers `groundtruth.db`.
10. **File** `-006.md` post-impl report (NEW) with spec-to-test mapping + executed results + applicability+clause preflights + explicit bridge-index audit-trail evidence (`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`) + Recommended Commit Type.

## Specification-Derived Verification Plan

| Spec / requirement | Test / check (executable in scope) | Acceptance |
|---|---|---|
| RETIRE-SPEC assertion (a) file-absent | `test_mirror_retirement_role_assignments.py::test_file_absent` | `harness-state/role-assignments.json` does not exist |
| RETIRE-SPEC assertion (b) + DCL v2 assertion #1 (no live reads) | `test_mirror_retirement_role_assignments.py::test_no_live_reads` | no `json.load`/`json.loads`/`read_text`/`open(...,'r')`/`tomllib.load` of the path in `scripts/`+`groundtruth-kb/src/` outside whitelist |
| DCL v2 assertion #4 (physically absent) | `test_file_absent` (same) | retired path absent post-WI-4336 |
| DCL v2 row live | `test_mirror_retirement_role_assignments.py::test_dcl_v2_live` | latest `DCL-HARNESS-STATE-SOT-ASSERTION-001` version is v2 with amended assertion #1 |
| drift-registry consistency | `test_mirror_retirement_role_assignments.py::test_drift_registry_absent` | `protected-artifact-inventory-drift.toml` no longer lists the path |
| inventory regeneration | post-regen grep (line-count-free) | regenerated baseline has 0 `role-assignments` matches; inventory-drift gate passes |
| DCL v2 amendment approval | formal-artifact-approval packet hash match | packet `presented_to_user=true`, content sha256 matches inserted row |

## Recommended Commit Type

`refactor(harness-state)` — completes the SoT consolidation by removing the orphaned legacy mirror and correcting the SoT-consistency assertion to its intended scope. No runtime behavior change (zero live reads/writes of the mirror; canonical entrypoint already the sole read path). The DCL v2 amendment is a governance correction bundled with the structural cleanup. (Not `feat` — no new capability; not `chore` — touches a governed spec + removes a load-bearing-by-history file.)

## Risk and Rollback

**Risk 1 — inventory-drift gate blocks the commit.** Mitigation: governance_review route + bridge report + regenerated baseline; explicit-path `git commit -- <targets>`; if still blocked, follow the hook's governance_review acceptance path (cite this bridge id), never `git add -A`.

**Risk 2 — a retained reference breaks at runtime.** Mitigation: grep-verified 0 live reads/writes; `write_role_assignments` has no live caller; `load_role_assignments` reads the registry projection (WI-3342 IP-3) and discards the path arg. Non-reading references (resolver, dead writer, packet-builders, docstrings, provenance) are explicitly permitted by amended assertion #1.

**Risk 3 — Codex reads the DCL amendment as `weaken_existing_role_assertions`.** Mitigation: §PAUTH Forbidden-Operation Analysis; if Codex disagrees, Prime escalates to the owner for an explicit PAUTH amendment before implementing — no unilateral PAUTH mutation here.

**Rollback:** DCL v2 insert is append-only (revert by inserting a v3 restoring prior text, owner-gated); `file_deletion` reversible via `git restore`; config/source/json edits file-level reversible; new test removable. No protected narrative edited; no WI mutation. If Codex NO-GO: nothing implemented (impl post-GO); superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight exit 0, 0 blocking gaps.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
