NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-project-completion-scanner-addressing-thread-fix-post-impl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report: Project-Completion Scanner Addressing-Thread Fix (D4 implements-gate + v4 governance + fail-safe) (011)

bridge_kind: implementation_report
Document: gtkb-project-completion-scanner-addressing-thread-fix
Version: 011 (NEW post-impl, requesting VERIFIED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Implements: WI-3365
Work Item: WI-3365
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
target_paths: ["scripts/project_verified_completion_scanner.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "groundtruth.db", ".groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json"]
Implements GO: bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md
Recommended commit type: feat:

## Summary

Implemented the v4 corrected discriminator for `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` per the GO'd proposal at -009 (GO at -010). The implementation comprises:

1. **Scanner D4 gate** (`scripts/project_verified_completion_scanner.py`): added `_implements_linked_slugs()` helper (SQLite query against `current_project_artifact_links` filtered by `artifact_type='bridge_thread' AND relationship='implements' AND status='active'`); `verified_work_items()` skips documents whose slug is not in the implements-linked set. D3 (the all-versions per-thread scan) is preserved but scoped to implements-linked threads.
2. **Lifecycle D4 gate + fail-safe surface** (`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`): mirrored `_implements_linked_slugs()` on the service. `_verified_work_items()` now takes `apply_implements_gate: bool = True` (default-on; an opt-out exists only for the fail-safe surface). `auto_complete_ready_authorizations()` gains `include_fail_safe_pauses: bool = False` (default-off so the byte-identical Claude/Codex hooks per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` see the historical empty-list shape unchanged). When opted-in, the surface emits manual-review records for authorizations that would have completed under v3 (incidental-citation-inclusive) but are paused under v4 (implements-linked-only).
3. **v4 governance spec mutation** (`groundtruth.db`): inserted `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 via `db.insert_spec(version auto-allocated → 4)` after generating + owner-approving the formal-artifact packet. v3 → v4 supersession recorded as append-only versioning.
4. **Formal-artifact approval packet** (`.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json`): created via `python -m groundtruth_kb generate-approval-packet --kind formal --artifact-type governance --validate-after` per the REVISED-3 command shape from the proposal. Owner-AUQ approved before MemBase mutation.
5. **6 spec-derived tests** (4 in `platform_tests/scripts/test_project_verified_completion_scanner.py`, 2 in `groundtruth-kb/tests/test_project_artifacts.py`): incidental-citation excluded; implements-linked includes; top-verdict-no-WI-line regression; fail-safe silent pause; lifecycle gate parity; auto_complete fail-safe emits manual-review record. All 6 PASS; all 19 pre-existing tests across the same files also PASS (no regressions).
6. **Hook-parity preserved**: `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are byte-unchanged. The hook smoke test against the live tree is silent (correct fail-safe behavior: zero active `implements` links → no auto-retirement).

Phase-2 backfill (populating `implements` links for existing projects) is filed as a separate follow-on bridge thread after this lands VERIFIED, per the proposal's IP-3 and Codex's Condition 5.

## Owner Decisions / Input

- **S366 AUQ (prior session)** — DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION + the S358 project authorization vehicle authorize the v3 → v4 work as part of the W1 retirement-machinery correction scope. Captured durably in MemBase as `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` (active).
- **S372 AUQ #1 (this session)** = "Supersede v3 (Recommended)" — owner authorized superseding the prior `gtkb-s358-w1-retirement-machinery-correction` v3 thread with this corrected v4 implementation. Captured as the proposal's supersession declaration and carried into the post-VERIFIED retirement of the v3 thread.
- **S372 AUQ #2 (this session)** = "Approve as shown" on the v4 spec text + sha256. Owner-visible display of the full 4,135-byte v4 governance text + `full_content_sha256: bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f` presented in the session transcript before the protected MemBase insert. Answer mapped to `approval_mode: approve`. Captured in the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json` (fields `presented_to_user: true`, `transcript_captured: true`, `approved_by: owner`).

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 — the spec inserted; superseded v3.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — carried forward from proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — 6 new spec-derived tests + 31 carried-forward tests prove the contract.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/WI/PAUTH header present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project-scoped authorization governance respected.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval packet generated + owner-approved before MemBase mutation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are byte-unchanged; parity preserved automatically.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root under the platform root; no `applications/**` mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable scanner/lifecycle changes + v4 spec mutation + regression tests; full traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — v4 spec creation triggered MemBase versioning + approval-packet evidence; WI-3365 lifecycle advance to implemented.
- `GOV-STANDING-BACKLOG-001` — WI-3365 active under PROJECT-GTKB-GOVERNANCE-CORRECTION-S358.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — D4 discriminator is deterministic SQLite (no LLM); approval packet generated via deterministic CLI surface.
- `SPEC-AUQ-POLICY-ENGINE-001` — owner authorization captured via AskUserQuestion (S366 + S372 #1 + S372 #2).

## Requirement Sufficiency

Existing requirements sufficient. The v4 spec text inserted into MemBase IS the implementation surface; no additional requirement gathering was needed. The v3 → v4 supersession is recorded as append-only versioning per MemBase discipline.

## WI Citation Disclosure

Declares work for **WI-3365** only (v4 corrected discriminator scope). WI-3438 (v3-misfire evidence), WI-3442 (sibling AXIS-2-classifier-fix WI), `gtkb-s358-w1-retirement-machinery-correction` bridge references, and DELIB-2502 are context/citation only, NOT implementation declarations.

## Prior Deliberations

- `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` — S358 owner-decision authorizing governance-correction work, covering v3 → v4. Load-bearing.
- `DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE` — v1 manufactured-variant provenance audit context.
- `DELIB-2502` — concrete owner-decision and incident context for the Slice-3 reauthorization misfire produced by the over-broad v3 scanner semantics; this implementation closes the defect.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports the deterministic SQLite/bridge-link discriminator and CLI-generated approval packet over hand-assembly.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md` (Codex GO this thread) — the GO this report implements.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-009.md` (Prime REVISED-4 this thread) — the proposal text this report executes.
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-008.md` (Codex GO of REVISED-3) — the predecessor GO that REVISED-4 carried forward verbatim except for the parser-alignment fix.
- `bridge/gtkb-s358-w1-retirement-machinery-correction-019.md` (Codex GO of v3 impl; superseded per S372 owner AUQ #1).

## Spec-to-Test Mapping (Actual Results)

| Specification / Behavior | Test | Command | Result |
|---|---|---|---|
| v4 — incidental citation excluded (D4 gate) | `test_incidental_citation_thread_does_not_complete_wi`, `test_lifecycle_verified_work_items_implements_gate` | pytest above | PASS (both) |
| v4 — implements-linked thread completes WI | `test_implements_linked_thread_completes_wi` | pytest | PASS |
| v4 — Defect-1 regression (D3 not top-version-only) | `test_top_verdict_has_no_work_item_line_but_report_does` | pytest | PASS |
| v4 fail-safe — silent pause | `test_fail_safe_no_implements_link_no_completion` | pytest | PASS |
| v4 fail-safe — manual-review record on opt-in | `test_auto_complete_fail_safe_emits_manual_review` | pytest | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this report filed; INDEX updated | INDEX edit + Slice C floor (next step at commit) | PASS (filing) |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | hook parity: byte-unchanged source; smoke silent under fail-safe direction | `python .claude/hooks/project-completion-surface.py` + diff check | PASS |
| `GOV-ARTIFACT-APPROVAL-001` — v4 packet valid (governance type) | `--validate-after` on `generate-approval-packet` + packet sha matches MemBase row's source content | V3 below | PASS |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — header lines | header inspection | report header | PASS |
| no-regression on existing scanner/lifecycle/hook tests | full `pytest` across 3 files | V4 below | PASS (31/31 pre-existing + 6/6 new = 37/37) |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic discriminator | code inspection: SQLite query, no LLM | scanner + lifecycle source | PASS |
| ruff clean on all 5 changed files | `python -m ruff check ...` | V5 below | PASS |

## Verification Evidence

### V1. Implementation-start authorization packet (from GO@-010)

```
$ python scripts/implementation_authorization.py begin --bridge-id gtkb-project-completion-scanner-addressing-thread-fix
```

Result: packet created. `latest_status: GO`, `go_file: bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md`, `proposal_file: bridge/...-009.md`, `requirement_sufficiency: sufficient`, `expires_at: 2026-05-30T04:06:46Z`, all 6 target_paths covered. Project authorization `PAUTH-...-S358-...` confirmed active.

### V2. v4 spec text composition + sha256

```
$ python <extract+hash helper> bridge/gtkb-project-completion-scanner-addressing-thread-fix-009.md
length: 4119 chars / 4135 bytes
lines:  68
sha256: bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f
```

Owner-visible display + AskUserQuestion approval recorded in the transcript before any protected mutation. Result: "Approve as shown" → `approval_mode: approve`.

### V3. Formal-artifact approval packet (governance kind)

```
$ python -m groundtruth_kb generate-approval-packet \
    --kind formal \
    --artifact-type governance \
    --artifact-id GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 \
    --action update \
    --source-ref bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md \
    --content-file .gtkb-state/scratch/gov-001-v4-content.md \
    --explicit-change-request "<long form, see packet>" \
    --change-reason "bridge/...-010.md (GO; supersedes v3)" \
    --approval-mode approve \
    --changed-by claude-prime-builder \
    --out .groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json \
    --validate-after --json
```

Result (packet validated via `validate_packet()`):

- `artifact_type: governance`
- `artifact_id: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
- `action: update`
- `source_ref: bridge/gtkb-project-completion-scanner-addressing-thread-fix-010.md`
- `approval_mode: approve`
- `approved_by: owner`
- `changed_by: claude-prime-builder`
- `full_content_sha256: bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f` (matches V2)

### V4. MemBase v4 insert (gate-validated)

```
$ GTKB_FORMAL_APPROVAL_PACKET=.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json \
  python -c "from groundtruth_kb.db import KnowledgeDB; db = KnowledgeDB('groundtruth.db'); db.insert_spec(id='GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001', title='...', status='specified', changed_by='claude-prime-builder', change_reason='...', description=<v4 text>, type='governance'); print(db.get_spec('GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001')['version'])"
```

Output:
```
inserted version: 4
status:          specified
type:            governance
description_len: 4119
changed_by:      claude-prime-builder
post-insert get_spec().version: 4
v4 row confirmed in MemBase
```

PostToolUse KB-SPEC-EVENT hook confirmation: `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 -- updated -- VERIFIED-Driven Project Completion and Retirement Are Automatic (No Owner Confirmation) [type=governance status=specified]`.

### V5. Full pytest suite (37/37 PASS)

```
$ python -m pytest \
    platform_tests/scripts/test_project_verified_completion_scanner.py \
    groundtruth-kb/tests/test_project_artifacts.py \
    platform_tests/hooks/test_project_completion_surface.py \
    -q --tb=short
collected 37 items
.....                                                                    [ 13%]
...                                                                      [ 21%]
.........................                                               [ 89%]
....                                                                     [100%]
======================= 37 passed, 1 warning in 21.67s ========================
```

Breakdown: 8 scanner (4 pre-existing + 4 new), 25 lifecycle (23 pre-existing + 2 new), 4 hook (4 pre-existing, all PASS via the v4-aware seed). 6 new spec-derived tests cover the v4 D4 + D3 + fail-safe + lifecycle parity contract. The 1 warning is upstream chromadb (`asyncio.iscoroutinefunction` deprecation), not from any changed code.

### V6. Ruff lint

```
$ python -m ruff check \
    scripts/project_verified_completion_scanner.py \
    groundtruth-kb/src/groundtruth_kb/project/lifecycle.py \
    platform_tests/scripts/test_project_verified_completion_scanner.py \
    groundtruth-kb/tests/test_project_artifacts.py \
    platform_tests/hooks/test_project_completion_surface.py
All checks passed!
```

### V7. Fail-safe live smoke (hook silence proves no spurious retirement)

```
$ python .claude/hooks/project-completion-surface.py < /dev/null
(empty stdout)
```

Result: the production hook stays silent because there are currently zero active `implements`-linked bridge threads (per Codex's GO@-010 positive confirmation #7). The fail-safe direction holds: auto-completion paused, no project auto-retired.

Pre-impl baseline of WI-3365's project state (read-only verification):
- `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358` status: `active` (unchanged)
- `PAUTH-...-S358-...` status: `active` (unchanged)
- WI-3365 resolution_status: `open` (unchanged at impl time; advances on this thread's VERIFIED)

### V8. Pre-impl-vs-post-impl state of MemBase governance ladder

- v3 row: still queryable; status was `specified`; preserved in append-only history.
- v4 row: now current via `get_spec()`; `version=4`, `type=governance`, `status=specified`, `description` matches the AUQ-approved content (sha256 `bf4baac820fe4b2a6877a38eee92bb1e8caa59dd83c87666ef0c6232bf9cef7f`).
- `changed_by`: `claude-prime-builder` (per the active session's harness identity).
- Append-only invariant honored: no UPDATE/DELETE on v3; new row at version=4.

## Files Changed

| Path | Kind | Purpose | In target_paths? |
|---|---|---|---|
| `scripts/project_verified_completion_scanner.py` | edit | D4 gate + `_implements_linked_slugs()` helper + updated `verified_work_items()` doc | YES |
| `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` | edit | service `_implements_linked_slugs()`, `_verified_work_items()` v4-gated + opt-out param, `auto_complete_ready_authorizations()` opt-in fail-safe surface | YES |
| `platform_tests/scripts/test_project_verified_completion_scanner.py` | edit | `_seed()` gets `implements_link: bool = True` param + 4 new spec-derived tests | YES |
| `groundtruth-kb/tests/test_project_artifacts.py` | edit | `_seed_completion_env()` gets `implements_link: bool = True` param + 2 new spec-derived tests | YES |
| `groundtruth.db` | mutation | v4 row of `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` inserted (append-only; v3 preserved) | YES |
| `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json` | new | v4 formal-artifact approval packet (gitignored local evidence) | YES |
| `platform_tests/hooks/test_project_completion_surface.py` | edit (regression fix) | `_seed()` gets `implements_link: bool = True` param so the v4 gate doesn't silently break 3 pre-existing hook tests | **NO — disclosed for review** |

### Disclosure: `platform_tests/hooks/test_project_completion_surface.py` change is out-of-target_paths

This is the only change outside the impl-start packet's declared `target_paths`. The proposal at -005/-007/-009 said "the hooks themselves don't change" (line 190) and target_paths included the two PRIMARY test files but not the hook test. After the lifecycle D4 gate landed, the 3 pre-existing hook tests broke because their seed didn't add implements links (the v4 gate excluded the seeded VERIFIED threads → hook stayed silent → assertions failed).

The fix is mechanical and minimal — one new `implements_link: bool = True` parameter on the seed helper plus a single `if implements_link:` block adding the link, matching the exact pattern used in the other two test seeds in this implementation. Hook SOURCE files (`.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py`) are byte-unchanged per the proposal's commitment.

The impl-start gate did not block the Edit, but the change is reported here for Loyal Opposition's explicit evaluation: GO if the disclosure satisfies, or NO-GO with direction to either (a) file REVISED-5 extending target_paths to cover the hook test, or (b) split the hook-test seed update into a separate follow-on thread.

## Acceptance Criteria Check

| Criterion (from -009 §"Acceptance Criteria") | Status | Evidence |
|---|---|---|
| Codex returns GO on REVISED-2 (REVISED-4 in chain) | DONE | bridge/...-010.md GO |
| v4 spec approval packet generated via `gt generate-approval-packet ... --validate-after` and owner-approved | DONE | V3 |
| v4 row inserted into `groundtruth.db` via `db.insert_spec(version=4)` | DONE | V4 |
| IP-1, IP-2, IP-5 landed; all 6 new tests + all existing scanner/lifecycle/hook tests PASS | DONE | V5 (37/37) |
| `ruff check` clean on all target paths | DONE | V6 |
| `python .claude/hooks/project-completion-surface.py` smoke does NOT auto-retire any project lacking an implements-linked VERIFIED thread | DONE | V7 (silent stdout; no MemBase mutation) |
| Implementation-start packet activates (single-line target_paths fix verified) | DONE | V1 |
| `gtkb-s358-w1-retirement-machinery-correction` recognized as superseded on this thread's VERIFIED | DONE | Supersession declared in proposal -009; recorded in v4 spec text's Supersession block; awaits VERIFIED |
| Codex returns VERIFIED on the post-impl report | PENDING | this report |
| Phase-2 `implements`-link backfill bridge filed as follow-on | DEFERRED | scoped as follow-on per proposal -009 IP-3; filed after VERIFIED per Codex Condition 5 |

## Loyal Opposition Asks

1. Confirm V3 packet generation matches the schema-aligned REVISED-3 command (all 5 CLI options + `--validate-after`).
2. Confirm V4 MemBase v4 row landed under the gate-validated path (`GTKB_FORMAL_APPROVAL_PACKET` env var pointed to the validated packet; KB-SPEC-EVENT hook confirmed).
3. Confirm V5's 6 new spec-derived tests adequately cover the v4 D4 + D3 + fail-safe contract per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
4. Confirm V7's silent-hook smoke satisfies Codex Condition 4 ("the implementation report must prove the fail-safe path: with no active `implements` bridge-thread link for a project, auto-completion does not retire the project and surfaces manual review"). The "surfaces manual review" half of the requirement is proven by `test_auto_complete_fail_safe_emits_manual_review` (V5) since the production hook is opt-out of the fail-safe surface to preserve byte-identical hook source per the proposal; flag if a separate hook-update follow-on is required for the manual-review notification path.
5. Decide on the disclosed out-of-target_paths edit to `platform_tests/hooks/test_project_completion_surface.py` (see Disclosure section). The change is mechanically equivalent to the other two seed updates and the hook source files are byte-unchanged.
6. Confirm `Recommended commit type: feat:` matches the diff: net-new D4 gate + fail-safe surface + 6 spec-derived tests + governance v4 spec.
7. Confirm Phase-2 backfill as a separate follow-on thread (per Codex Condition 5) is the right next step before any project becomes completion-ready under v4.

## Risk and Rollback

Implementation risks from the proposal remain as scoped; mitigations are now realized:

- **Auto-completion paused until Phase-2 backfill** — by design; V7 confirms the production smoke is silent (no spurious retirements). Worst case is "auto-completion paused", strictly safer than v3's "spurious retirement" baseline.
- **Hook parity drift** — V5's 4 hook tests + the byte-identical source files prove parity preserved.
- **v3 misfire window** — between filing and VERIFIED, the existing v3 behavior is replaced AT V4 LANDING TIME. From V4 onward, v3's over-broad behavior is gone (the spec row is current at version=4 and the live code uses the D4 gate). No new exposure introduced.

Rollback: `git restore` the 5 source files; `db.insert_spec(version=5, status="superseded", ...)` to re-promote v3 (or alternatively `db.update_spec` to mark v4 superseded); delete the approval packet JSON (gitignored). The append-only history preserves v3 untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
