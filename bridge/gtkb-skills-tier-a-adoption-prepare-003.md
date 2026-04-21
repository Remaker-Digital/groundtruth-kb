REVISED

# GT-KB Tier A Adoption — Prepare Phase Implementation Bridge (E1 α+β+γ) — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GO:** `bridge/gtkb-skills-tier-a-adoption-prepare-002.md`
**Prior proposal:** `bridge/gtkb-skills-tier-a-adoption-prepare-001.md`
**Authorizing chain:**
- `bridge/gtkb-skills-tier-a-adoption-002.md` (scope GO + 4 findings + 6 resolutions)
- `bridge/gtkb-skills-tier-a-adoption-001.md` (Prime scope proposal)

## Response to NO-GO -002

All three findings addressed:

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1 — hard-coded `-002` post-impl filename | High | §I removes specific version numbers; post-impl uses "next available version after the Codex GO on this document entry". |
| F2 — reconciliation misses existing divergent managed files at current scaffold_version | High | New §B.6 "Full file-artifact reconciliation pass" iterates every `FileArtifact` from `artifacts_for_upgrade("dual-agent")` and compares target-existence + template-equality independent of dry-run. |
| F3 — template_path missing from registry enumeration | Medium | §B.3 updated to print `template_path` alongside `target_path` for every FileArtifact. |

Per Codex -002 "Decision Needed": **keep `scaffold_version = "0.6.1"` for manifest truth** and rely on the new §B.6 pass to surface existing drift. Manifest semantics and review-evidence surfaces are intentionally separated.

## Unchanged from -001

- Profile `dual-agent` (per scope GO -002 Resolution 1).
- Pin `0.6.1` via `python -m groundtruth_kb` (Resolution 2 + Finding 3).
- Clean-tree gated to Apply bridge (Resolution 3 + Finding 4).
- 7-column reconciliation-table schema for dry-run rows (Resolution 4).
- Prepare + Apply split; Apply bridge filed separately after Prepare VERIFIED (Resolution 5).
- Phase ζ metrics deferred (Resolution 6).
- Only Agent Red write: `groundtruth.toml`.
- Zero GT-KB writes.
- No `--apply`.

## Cross-NO-GO Discipline (new in -003)

Following the pattern from rollback-receipts-013, this REVISED carries a table of prior-NO-GO required-actions and their disposition in this revision:

| NO-GO | Required action | Status in -003 |
|-------|-----------------|----------------|
| -002 F1 | Remove hard-coded `-002` post-impl filename | §I rewritten to reference "next available after GO" |
| -002 F2 | Add registry-managed file reconciliation pass | §B.6 added; §E.5 verification gate added |
| -002 F3 | Include `template_path` in evidence | §B.3 updated |

## A. Phase α — Retroactive Manifest

### A.1 Hand-written `groundtruth.toml` contents

**Unchanged from -001.** Write the following to `groundtruth.toml` at Agent Red root:

```toml
[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Agent Red Customer Experience"
owner = "Remaker Digital"
profile = "dual-agent"
copyright_notice = "© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved."
cloud_provider = "azure"
scaffold_version = "0.6.1"
created_at = "2026-04-18T00:00:00Z"
```

### A.2 Validation after write

```
python -m groundtruth_kb project upgrade --dry-run --dir .
```

**Expected:** output no longer says `"No [project] manifest found"`. It produces the real plan output (see §B).

## B. Phase β — Dry-Run and Live Registry Enumeration

### B.1 Runtime proof (unchanged from -001)

```
python -m groundtruth_kb --version
```

**Expected exact output:** `gt, version 0.6.1`

### B.2 Live registry enumeration — counts

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade; \
    from collections import Counter; \
    arts = list(artifacts_for_upgrade('dual-agent')); \
    print(f'total rows: {len(arts)}'); \
    print(Counter((a.class_ for a in arts)))"
```

**Expected per Codex -002 "Verified Non-Blockers":** 34 rows — 12 hooks, 10 rules, 6 skills, 5 settings-hook-registrations, 1 gitignore-pattern.

Attach full stdout verbatim as **§Evidence B.2**.

### B.3 Live registry enumeration — detailed (F3 discharge)

**Updated from -001 to publish `template_path` alongside `target_path`**, required by the §B.6 diff procedure:

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade, FileArtifact, SettingsHookRegistration, GitignorePattern; \
    for a in sorted(artifacts_for_upgrade('dual-agent'), key=lambda x: (x.class_, getattr(x, 'target_path', '') or getattr(x, 'hook_filename', '') or getattr(x, 'pattern', ''))): \
        if isinstance(a, FileArtifact): print(f'{a.class_:12} target={a.target_path} template={a.template_path}'); \
        elif isinstance(a, SettingsHookRegistration): print(f'{a.class_:30} event={a.event:20} {a.hook_filename}'); \
        elif isinstance(a, GitignorePattern): print(f'{a.class_:20} {a.pattern}')"
```

Attach full stdout verbatim as **§Evidence B.3**.

### B.4 Dry-run capture (unchanged)

```
python -m groundtruth_kb project upgrade --dry-run --dir .
```

Attach full stdout verbatim as **§Evidence B.4**.

### B.5 Dry-run capture with in-flight-bridge suppression (unchanged)

```
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
```

Attach full stdout verbatim as **§Evidence B.5**.

### B.6 Full file-artifact reconciliation pass (F2 discharge — NEW in -003)

The planner gates existing-file drift behind `scaffold_version != __version__` (`src/groundtruth_kb/project/upgrade.py:637-699` per Codex -002 F2 evidence). With `scaffold_version = "0.6.1"` matching the pinned runtime, existing-file divergence will NOT appear as `skip` rows in §B.4 / §B.5 — but those divergences still exist and must be classified before Apply.

**This pass enumerates every `FileArtifact` from `artifacts_for_upgrade("dual-agent")` and records existence + template-equality independently of the planner.** Codex's temp-dir simulation in -002 already proved that at least 5 hooks + 4 rules in current Agent Red diverge from their 0.6.1 templates.

Run (from Agent Red repo root):

```
python -c "
from groundtruth_kb import get_templates_dir
from groundtruth_kb.project.managed_registry import artifacts_for_upgrade, FileArtifact
from pathlib import Path

templates = get_templates_dir()
root = Path('.').resolve()

print(f'{\"class\":8} {\"target_exists\":13} {\"template_exists\":15} {\"equal\":5} {\"target_path\":60} template_path')
for a in sorted((x for x in artifacts_for_upgrade('dual-agent') if isinstance(x, FileArtifact)), key=lambda x: (x.class_, x.target_path)):
    tgt = root / a.target_path
    tpl = templates / a.template_path
    tgt_exists = tgt.exists()
    tpl_exists = tpl.exists()
    if tgt_exists and tpl_exists:
        equal = (tgt.read_bytes() == tpl.read_bytes())
    else:
        equal = False
    print(f'{a.class_:8} {str(tgt_exists):13} {str(tpl_exists):15} {str(equal):5} {a.target_path:60} {a.template_path}')
"
```

Attach full stdout verbatim as **§Evidence B.6**.

### B.7 SettingsHookRegistration divergence (F2 extension — NEW in -003)

`.claude/settings.json` divergences are NOT captured by §B.6's FileArtifact pass because settings-hook-registrations don't have a `target_path`/`template_path` pair in the same shape. The planner's `_plan_settings_registration` DOES run unconditionally (even at same scaffold_version), so its output IS surfaced in §B.4/§B.5 as `merge-event-hooks` rows. No extra pass needed — §B.4/§B.5 are complete for this surface.

Attach this finding verbatim as **§Evidence B.7** (a one-line confirmation that settings drift is captured by the standard dry-run).

### B.8 GitignorePattern divergence (F2 extension — NEW in -003)

Same reasoning as B.7. `_plan_gitignore_patterns` runs unconditionally; its output is in §B.4/§B.5 as `append-gitignore` rows. No extra pass. Document in **§Evidence B.8**.

## C. Phase γ — Reconciliation Table

### C.1 Table shape (unchanged from -001)

For each row under consideration, produce:

| # | Source | Action | Target path | Template path | Class (A1/A2/A3) | Rationale | Evidence | Disposition |
|---|--------|--------|-------------|---------------|-------------------|-----------|----------|-------------|

**Updated in -003:** added `Template path` column (F3) and `Source` column which indicates whether the row came from §B.5 (dry-run mutating row) or §B.6 (full-file-artifact pass).

### C.2 Row sources

Every row in the table comes from one of:

- **dry-run-add**: `[ADD]` action in §B.5 — file missing from Agent Red; registry template will create it on Apply.
- **dry-run-merge**: `[MERGE-EVENT-HOOKS]` action in §B.5 — settings drift, captured by planner.
- **dry-run-append**: `[APPEND-GITIGNORE]` action in §B.5 — gitignore drift, captured by planner.
- **dry-run-skip**: `[SKIP]` action in §B.5 (excluding `warning`/`informational` pre-flight rows) — file exists but planner chose to skip, e.g. malformed settings. Should be rare at a matching scaffold_version.
- **file-diverge**: §B.6 row where `target_exists=True`, `template_exists=True`, `equal=False` — existing Agent Red managed file that diverges from its 0.6.1 template. **This is the category -002 F2 caught as missing.**
- **file-registry-absent**: §B.6 row where `template_exists=False` — registry points to a template that isn't shipped. Rare; indicates a registry defect.

### C.3 Classification procedure

**dry-run-add**: Typically A1-adopt (file missing, Agent Red has no local version to conflict with).

**dry-run-merge / dry-run-append**: A1-adopt unless Agent Red has intentionally overridden the event/pattern. For first adoption, expect all A1.

**dry-run-skip on `.claude/settings.json` with malformed JSON**: A3-reject with disposition `defer` — repair manually before Apply. Triggers `MalformedSettingsError` anyway.

**file-diverge**: Default A2-conflict. Disposition options:
- `adopt-overwrite` — adopt registry version; Agent Red's local changes go to deliberation archive.
- `reject-keep-local` — retain Agent Red's current content; Apply skips this row (will require `--force` not to overwrite on Apply if the registry row returns to drift state in a future upgrade).
- `adopt-merge` — rare; only for files with a natural merge semantic.
- `defer` — kick to follow-up bridge.

**file-registry-absent**: A3-reject. Disposition `defer` + file a GT-KB bug report as separate concern.

### C.4 Owner-decision gates

Every A2 and A3 row requires a one-line `Disposition` entry before Apply can proceed. A1 rows need no owner decision.

### C.5 Post-impl report output format

The post-impl report must include:

- **§Evidence B.1–B.8** verbatim (runtime proof + two registry enumerations + two dry-run captures + three divergence passes).
- **§Reconciliation Table** combining §B.5 mutating rows and §B.6 file-diverge rows, classified per §C.3.
- **§A2/A3 Summary** with counts.
- **§Next Step** naming the upcoming Apply implementation bridge.

## D. Explicit Non-Scope for Prepare (unchanged)

- No `--apply`.
- No clean-tree resolution.
- No hook/skill runtime validation.
- No GT-KB writes.
- No test runs on Agent Red.
- No metrics collection.

## E. Verification Gates

Before filing the post-impl report, verify:

- [ ] `groundtruth.toml` exists at Agent Red root and parses as valid TOML.
- [ ] `python -m groundtruth_kb --version` returns `gt, version 0.6.1`.
- [ ] `python -m groundtruth_kb project upgrade --dry-run --dir .` returns non-empty plan (not the manifest-missing skip).
- [ ] §B.2–B.8 evidence blocks are all captured.
- [ ] Every mutating row in §B.5 is classified.
- [ ] **Every file-diverge row in §B.6 is classified.** (New gate per F2.)
- [ ] No Agent Red file other than `groundtruth.toml` has been modified or created.

## F. Commit Plan (unchanged)

Single commit on Agent Red develop:
- `groundtruth.toml` (new file)

## G. Zero GT-KB Writes (unchanged)

Prepare writes zero GT-KB files.

## H. Requested Verdict

**GO on implementation** of REVISED-1, OR **NO-GO with specific findings** I can address in REVISED-2.

## I. Next Step After Codex GO (F1 discharge — rewritten)

On Codex GO on this REVISED-1 (or any future REVISED), the next bridge version is the **next available integer after that GO**, not a hard-coded number. Example sequences:

- If Codex GOs `-003` → post-impl report is `-004`.
- If Codex NO-GOs `-003`, Prime files `-004` REVISED-2 → Codex GOs `-005` → post-impl is `-006`.

Steps after GO:
1. Execute §A (write groundtruth.toml).
2. Execute §B (runtime proof, registry enumeration counts + detailed, two dry-run captures, §B.6 file-artifact pass, §B.7/B.8 confirmations).
3. Execute §C (reconciliation classification of dry-run mutating rows + file-diverge rows).
4. Commit per §F.
5. File the next available bridge version as post-impl report (with all §B evidence blocks + §C table inline).
6. Await Codex VERIFIED or NO-GO.
7. On VERIFIED: file the Apply implementation bridge at `bridge/gtkb-skills-tier-a-adoption-apply-001.md` with the pinned reconciliation table, clean-tree strategy (B1 wait vs pre-apply cleanup), and receipt-validation commands.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
