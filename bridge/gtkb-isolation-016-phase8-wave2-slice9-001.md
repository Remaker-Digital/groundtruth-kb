NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9 — `_production_effects.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md` (Slice 6 VERIFIED; release-gate framework-vs-adopter classification pattern)

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_production_effects.py + tests; driver dispatch already wired (table entry index 9: `("production", "rehearse._production_effects", "run")`)

**Filed in parallel with:** Slices 7 (`_ci_inventory`) and 8 (`_membase_export`) per owner direction 2026-04-27. All three Stage B lanes are independent at the implementation level (umbrella -004: "Lanes 2-11 must consume the validated runtime manifest" with no inter-lane ordering).

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.emit_result()` for the standard sub-script result envelope. Does NOT use ID-prefix classification — production-effect surfaces are filesystem artifacts (not KB records) and classify by filename + filesystem location + Phase 8 plan §4 explicit policy rules.
- Phase 8 plan §4 ("Explicit List Of Artifacts That Must Not Move") establishes the canonical do-not-move list — the highest-priority classification rule for this slice.

## 1. Scope

Single Stage B leaf lane: `scripts/rehearse/_production_effects.py`. Produces the **production-effects map** required by Phase 8 plan §2 ("Zero-Destructive Dry-Run Output"), specifically `production-effects-map.md` plus a machine-readable companion JSON. The map enumerates every production-affecting filesystem surface in the legacy mixed root and assigns one of four dispositions:

- **MOVE** — adopter-owned production artifact; relocates to `applications/Agent_Red/<path>` at cutover.
- **KEEP** — framework production artifact; stays at GT-KB root post-cutover.
- **DO_NOT_MOVE** — explicitly listed in Phase 8 plan §4 as immovable (groundtruth.db, .env.local, secrets, ACS carrier artifacts, GT-KB rule files, etc.).
- **OWNER_DECISION_REQUIRED** — content-ambiguous; Wave 3 verification matrix or owner resolves.

Strictly additive: no driver changes (dispatch already registers `production`), no manifest changes, no changes to `_common.py` or any earlier lane.

**Critical safety property:** this lane MUST NOT read sensitive content. `.env.local`, `.env`, secrets directory contents, approval-packet credential fields — only **presence + path + size** is recorded. Content reads are reserved for explicitly classified non-secret surfaces (e.g., `docker-compose.yml` may be content-scanned because it's in git; `.env.local` may NOT be content-scanned because it's secret material).

## 2. Authoritative Source Set

Production-affecting surfaces probed at known root-relative locations. Per Phase 8 plan §4 ("Explicit List Of Artifacts That Must Not Move") + filesystem inventory verified 2026-04-27:

### 2.1 Secret material surfaces (presence-only; never content-read)

| Path | Disposition | Signal |
|---|---|---|
| `.env.local` | DO_NOT_MOVE | `secret_material_per_phase8_plan_section_4` |
| `.env` (if exists) | DO_NOT_MOVE | `secret_material_per_phase8_plan_section_4` |
| `secrets/` | DO_NOT_MOVE | `secret_material_per_phase8_plan_section_4` |
| `groundtruth-artifacts/secrets/` | DO_NOT_MOVE | `secret_material_per_phase8_plan_section_4` |

### 2.2 Template files (content-readable)

| Path | Disposition | Signal |
|---|---|---|
| `.env.example` | MOVE | `adopter_environment_template` |
| `.env.integration.example` | MOVE | `adopter_environment_template` |

### 2.3 Container orchestration

| Path | Disposition | Signal |
|---|---|---|
| `docker-compose.yml` | MOVE | `adopter_container_orchestration` |

(Content scan: confirms it composes Agent Red services, not GT-KB framework services. Override to OWNER_DECISION_REQUIRED if framework references found.)

### 2.4 Shopify deployment

| Path | Disposition | Signal |
|---|---|---|
| `.shopify/deploy-bundle` | MOVE | `adopter_shopify_deployment_artifact` |
| `.shopify/deploy-bundle.br` | MOVE | `adopter_shopify_deployment_artifact_compressed` |

### 2.5 Deployment logs

| Path glob | Disposition | Signal |
|---|---|---|
| `logs/deploy-*.log` | MOVE (or owner-decision: archive vs move) | `adopter_deployment_history` |

(Recommendation embedded in preview: archive the historical logs at legacy root, do not carry to applications root. Final disposition: OWNER_DECISION_REQUIRED with recommendation.)

### 2.6 Formal artifact approvals (`.groundtruth/formal-artifact-approvals/*.json`)

Probed but classified per-file by approval **subject** (not just filename):

- Approval packets whose `approved_records[*].id` starts with `GTKB-` → KEEP (framework approval evidence)
- Approval packets whose subject mentions Agent Red / commercial readiness / production-readiness → MOVE
- Mixed (e.g., `2026-04-20-session-formalization-audit-batch.json` covers both subjects) → OWNER_DECISION_REQUIRED with signal `mixed_scope_approval_packet`

The lane reads packet **structure** (top-level keys, ID prefixes of approved records) — never credential or token fields. Per Slice 5 lesson: classify by content signals, not just filename.

### 2.7 POR (Production Operations Records) snapshots

| Path | Disposition | Signal |
|---|---|---|
| `.groundtruth/por-16d-phase1-snapshot.json` | MOVE | `adopter_production_operations_record` |
| `.groundtruth/por-16d-phase2-classification.json` | MOVE | `adopter_production_operations_record` |
| `.groundtruth/por-16d-phase2-snapshot.json` | MOVE | `adopter_production_operations_record` |

### 2.8 Wrap-scan + session evidence

| Path glob | Disposition | Signal |
|---|---|---|
| `.groundtruth/wrap-scan/*` | OWNER_DECISION_REQUIRED | `mixed_scope_session_evidence` |
| `.groundtruth/session/*` | OWNER_DECISION_REQUIRED | `per_session_state_not_per_scope` |

(Session state is per-session, not per-scope. Owner must decide: archive at legacy root, or migrate per-session-evidence policy.)

### 2.9 Configuration files at known locations

| Path | Disposition | Signal |
|---|---|---|
| `groundtruth.toml` (root) | KEEP | `framework_config_per_classify_tree` |
| `tools/knowledge-db/groundtruth.toml` | KEEP | `framework_config_per_classify_tree` |

(Cross-reference Slice 4's `path_rewrite/classification.json` if available — same logic as Slice 7.)

### 2.10 Authoritative DB

| Path | Disposition | Signal |
|---|---|---|
| `groundtruth.db` | DO_NOT_MOVE | `phase_8_plan_section_4_explicit_immovable` |
| `groundtruth.db-shm` | DO_NOT_MOVE | `sqlite_wal_companion` |
| `groundtruth.db-wal` | DO_NOT_MOVE | `sqlite_wal_companion` |

(Phase 8 plan §4: "groundtruth.db (authoritative file stays with whichever subject owns it post-split; the file itself is not moved as a whole unit)." The membase export from Slice 8 is the road map for selective extraction; the file itself is immovable as a whole.)

### 2.11 GT-KB framework rule files (do not move per §4)

| Path | Disposition | Signal |
|---|---|---|
| `CLAUDE.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md` | KEEP | `framework_root_directive_file` |
| `AGENTS.md` | KEEP | `framework_root_directive_file` |
| `.claude/rules/*.md` | KEEP | `framework_rule_file` |

### 2.12 ACS carrier artifacts (do not touch)

| Path glob | Disposition | Signal |
|---|---|---|
| Any file matching `*acs*toll*free*`, `*carrier-app-*`, `*sms-verification-app-*` | DO_NOT_MOVE | `acs_carrier_verification_artifact_per_phase8_plan_section_4` |

(The plan explicitly forbids touching carrier verification artifacts; treat them as untouchable.)

## 3. Classification Algorithm

For each known-path probe (§2.1-§2.12) and each glob match:

1. **Probe** filesystem for path existence (`Path.exists()` + `Path.is_file()` / `Path.is_dir()`). Record `exists` flag.
2. If path is in §2.1 (secret material) or §2.10 (live DB): record `path + exists + size_bytes` only. **Skip content read entirely.** Disposition: DO_NOT_MOVE.
3. If path is content-readable: optionally read content for signal extraction (only when filename rule is ambiguous and content scan is needed).
4. Apply per-section disposition rule. If §2.6 (approval packets), parse top-level keys + approved_records IDs (no body content read).
5. Cross-reference Slice 4's `path_rewrite/classification.json` if present (same optional cross-validation as Slice 7).
6. Emit row to inventory.

**Failure modes:** broken symlink, permission denied, file replaced mid-walk → record as `exists=false` warning; do not crash.

## 4. Output Layout

```
{output_dir}/production_effects/
├── production-effects-map.md  # main artifact (per Phase 8 plan §2)
├── production_effects.json    # machine-readable companion (schema in §5)
└── result.json                # standard sub-script result per Wave 2 -003 §4.2
```

## 5. Schemas

### 5.1 `production-effects-map.md` shape

```markdown
# Production Effects Map

Generated: <ISO timestamp>
Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_production_effects.py` (Slice 9).

## Summary

- Total surfaces probed: <N>
- MOVE: <count>
- KEEP: <count>
- DO_NOT_MOVE: <count>
- OWNER_DECISION_REQUIRED: <count>

## DO_NOT_MOVE (Phase 8 plan §4 explicit immovables)

- `.env.local` — signal: `secret_material_per_phase8_plan_section_4`
- `groundtruth.db` — signal: `phase_8_plan_section_4_explicit_immovable`
- ...

## MOVE (relocate to applications/Agent_Red/<path>)

- `.env.example` → `applications/Agent_Red/.env.example` — signal: `adopter_environment_template`
- `docker-compose.yml` → `applications/Agent_Red/docker-compose.yml` — signal: `adopter_container_orchestration`
- ...

## KEEP (stays at GT-KB root post-cutover)

- `CLAUDE.md` — signal: `framework_root_directive_file`
- `groundtruth.toml` — signal: `framework_config_per_classify_tree`
- ...

## OWNER_DECISION_REQUIRED

### `.groundtruth/wrap-scan/`

Per-session evidence; owner must decide policy: archive in place, or migrate.

### `logs/deploy-*.log`

Historical deployment logs. Recommendation: archive at legacy root. Final disposition: owner.

### `.groundtruth/formal-artifact-approvals/2026-04-20-session-formalization-audit-batch.json`

Approval packet covers both GTKB-* and AR-* records. Owner must decide partition policy.

...
```

### 5.2 `production_effects.json` schema

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "summary": {
    "total_surfaces": ...,
    "move_count": ...,
    "keep_count": ...,
    "do_not_move_count": ...,
    "owner_decision_required_count": ...
  },
  "surfaces": [
    {
      "path": ".env.local",
      "exists": true,
      "size_bytes": 12345,
      "disposition": "DO_NOT_MOVE",
      "signal": "secret_material_per_phase8_plan_section_4",
      "content_read": false,
      "category": "secret_material"
    },
    ...
  ],
  "absent_probed_paths": [...],
  "warnings": []
}
```

## 6. Common Contract Compliance

Per Wave 2 -003 §4 + Slice 4/5/6 lessons:

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, project_root=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/production_effects/`; includes `result.json` from start (Slice 4 -006 F2) — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT: only probes paths + reads non-sensitive content; never reads §2.1 secret-material content — ✓
- §4.5 driver dispatch: already wired (table index 9) — ✓
- §4.6 manifest validation precondition: lane assumes validated manifest; consumes `excluded_paths` for compatibility — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

`project_root=` parameter follows Slice 5/6/7 fixture-root pattern.

## 7. Test Plan

`tests/scripts/test_rehearse_production_effects.py` (new; ~16-20 tests).

Mocking strategy:
- `project_root=` parameter overrides `LEGACY_ROOT` for fixture trees
- Tests construct synthetic file trees under `tmp_path` matching the §2 surface inventory
- Critical safety test: `.env.local` content NEVER read (no `read_text` / `read_bytes` call against secret-material paths)

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_classifies_env_local_as_do_not_move` | §2.1 — presence-only, no content read |
| 3 | `test_run_does_not_read_env_local_content` | **Safety regression guard:** monkeypatch `Path.read_text`/`read_bytes` to raise; assert §2.1 paths still classified correctly. |
| 4 | `test_run_classifies_env_example_as_move` | §2.2 — adopter template |
| 5 | `test_run_classifies_docker_compose_as_move` | §2.3 |
| 6 | `test_run_overrides_docker_compose_to_owner_decision_when_framework_content` | §2.3 content scan override |
| 7 | `test_run_classifies_shopify_deploy_bundle_as_move` | §2.4 |
| 8 | `test_run_classifies_deploy_logs_as_owner_decision_with_archive_recommendation` | §2.5 |
| 9 | `test_run_classifies_approval_packet_by_subject` | §2.6 — GTKB-only → KEEP, AR-only → MOVE |
| 10 | `test_run_classifies_mixed_scope_approval_packet_as_owner_decision` | §2.6 mixed-scope |
| 11 | `test_run_does_not_read_credential_fields_in_approval_packets` | **Safety:** assert structure-only parse |
| 12 | `test_run_classifies_por_snapshots_as_move` | §2.7 |
| 13 | `test_run_classifies_wrap_scan_as_owner_decision` | §2.8 |
| 14 | `test_run_classifies_groundtruth_db_as_do_not_move` | §2.10 |
| 15 | `test_run_classifies_claude_md_as_keep` | §2.11 |
| 16 | `test_run_classifies_acs_carrier_artifact_as_do_not_move` | §2.12 |
| 17 | `test_run_writes_production_effects_map_with_four_sections` | §5.1 |
| 18 | `test_run_writes_production_effects_json` | §5.2 |
| 19 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 |
| 20 | `test_run_writes_result_json_on_error_path` | Error path forensics |
| 21 | `test_run_handles_absent_probed_paths` | Missing files recorded with exists=false |

Plus 1 driver integration test: advance the missing-lane fixture per Stage B GO ordering.

## 8. Files Changed (this slice's commit)

### 8.1 NEW
- `scripts/rehearse/_production_effects.py` — ~250 LOC (§2 path inventory + content-safe probes + classifier + 2 emitters)
- `tests/scripts/test_rehearse_production_effects.py` — ~480 LOC (~21 tests + safety-regression guard)
- `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md` (this file)

### 8.2 MODIFIED
- `bridge/INDEX.md` — new slice9 entry at top
- `tests/scripts/test_rehearse_isolation.py` — fixture advances per Stage B GO ordering

### 8.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`
- All other Slice 1-6 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `.env.local`, `.env`, `secrets/` (read-only presence probe; never content-read)

## 9. Out of Scope

- Stage B sibling lanes: `_ci_inventory.py` (Slice 7), `_membase_export.py` (Slice 8) — separate parallel slices.
- Stage C: `_chromadb_regen.py`, `_dashboard_regen.py` — separate slices.
- Stage D: `_rollback.py` — separate slice.
- Resolving `OWNER_DECISION_REQUIRED` rows — surfaced in preview markdown; resolution belongs to Wave 3 verification matrix or explicit owner workflow.
- Modifying any production surface — strictly read-only.
- Live Azure resource enumeration (Container Apps revisions, Cosmos containers, Key Vault contents) — not in repo, requires `az` CLI; out of scope for this rehearsal lane.
- Decryption of any secret material — explicitly forbidden.
- Selective approval-packet partition at cutover — that's ISOLATION-018 work; this slice produces the inventory that drives it.

## 10. Codex Review Asks

1. Confirm the §2 surface inventory (12 sub-sections) is complete vs. missing production-effect surfaces. Specifically: are there CI-secret env files, Azure CLI cache, or Shopify token files I should add?
2. Confirm the **safety property** in §1 ("MUST NOT read sensitive content") + Test 3 + Test 11 are sufficient to prevent regression where a future change accidentally content-reads `.env.local` or credential fields.
3. Confirm the four-disposition vocabulary (MOVE / KEEP / DO_NOT_MOVE / OWNER_DECISION_REQUIRED) maps cleanly to ISOLATION-018 cutover script. Alternative: add a fifth disposition (ARCHIVE_AT_LEGACY) for `logs/deploy-*.log`-style cases.
4. Confirm §2.6 approval-packet classification by subject (parsing top-level keys + approved_records ID prefixes) is the right depth — vs. classifying every approval packet as DO_NOT_MOVE for safety, vs. content-scanning the full body.
5. Confirm §2.8 classification of `.groundtruth/wrap-scan/` and `.groundtruth/session/` as OWNER_DECISION_REQUIRED is right — vs. defaulting them to MOVE (per-session state belongs with adopter app) or DO_NOT_MOVE.
6. Confirm Test 11 (`test_run_does_not_read_credential_fields_in_approval_packets`) regression-guards the structure-only parse correctly.
7. **GO / NO-GO** on Slice 9.

## 11. Decision Needed From Owner

None.

(The §2 surface inventory + classification rules collectively encode several Phase 8 plan §4 owner decisions already; if Codex flags any unresolved owner decision in this slice's classification rules, that becomes a §11 entry in the REVISED proposal.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
