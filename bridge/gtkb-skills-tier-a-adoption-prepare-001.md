NEW

# GT-KB Tier A Adoption — Prepare Phase Implementation Bridge (E1 α+β+γ)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Authorizing chain:**
- `bridge/gtkb-skills-tier-a-adoption-002.md` (scope GO + 4 findings + 6 resolutions)
- `bridge/gtkb-skills-tier-a-adoption-001.md` (Prime scope proposal)

## Summary

This is the **Prepare** implementation bridge for E1 (Phases α+β+γ per
the scope). It carries forward all six open-question resolutions and
discharges all four findings from scope GO `-002`. It is **read-mostly**:
the only Agent Red write is a hand-written `groundtruth.toml` manifest;
everything else is enumeration, dry-run, and reconciliation classification.

**The Apply phase (δ+ε) will be a separate implementation bridge filed
after this one VERIFIED.** Phase ζ metrics is deferred per -002 item 6.

## Condition / Finding Compliance

| -002 reference | How this bridge addresses it |
|----------------|-------------------------------|
| Resolution 1 — profile `dual-agent` | §A.1 manifest template uses `profile = "dual-agent"`. |
| Resolution 2 — pin `0.6.1`, prove runtime | §B.1 first command is `python -m groundtruth_kb --version` expecting exactly `gt, version 0.6.1`. No `gt` console script assumed anywhere in this bridge. |
| Resolution 3 — clean-tree gate belongs to Apply | §D explicitly scopes clean-tree OUT of Prepare; no tree-mutating operations. |
| Resolution 4 — reconciliation rigor | §C.3 specifies the full column format and mandates a rendered table in the post-impl report. |
| Resolution 5 — phase split | This bridge is Prepare only; Apply gets its own bridge `gtkb-skills-tier-a-adoption-apply-001.md` after VERIFIED. |
| Resolution 6 — defer metrics | Phase ζ is not in this bridge or the follow-up Apply bridge per Codex recommendation. |
| Finding 1 — stale registry estimates | §B.2 regenerates the live `artifacts_for_upgrade("dual-agent")` output from the pinned `0.6.1` runtime and attaches it verbatim to the post-impl report. Proposal's counts are NOT used. |
| Finding 2 — scaffold rejects non-empty target | §A hand-writes `groundtruth.toml`; does not invoke `python -m groundtruth_kb project init` against Agent Red. |
| Finding 3 — explicit runtime invocation | All commands in §B use `python -m groundtruth_kb ...`. No `gt` usage. |
| Finding 4 — clean-tree applies to `--apply` only | Dry-run needs no clean tree. Prepare never calls `--apply`. Apply bridge will gate on B1 or a dedicated pre-apply cleanup bridge per -002 item 3. |

## A. Phase α — Retroactive Manifest

### A.1 Hand-written `groundtruth.toml` contents

Write the following to `groundtruth.toml` at Agent Red root:

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

Notes on each field:
- `profile = "dual-agent"` per -002 resolution 1 (Agent Red's webapp
  nature is adopter-specific; `-webapp` profile would over-scope).
- `cloud_provider = "azure"` recorded factually; does not trigger
  Terraform scaffold because `includes_docker=False` on `dual-agent`
  (reviewed in `profiles.py`).
- `scaffold_version = "0.6.1"` per -002 resolution 2 (PyPI-released
  version, not main HEAD).
- `created_at` — today's date. The manifest never existed before, so
  there is no prior creation time to preserve.
- `db_path = "groundtruth.db"` — matches the existing pre-manifest
  database file at Agent Red root (`E:\...\Agent Red Customer
  Engagement\groundtruth.db`).

### A.2 Validation after write

```
python -m groundtruth_kb project upgrade --dry-run --dir .
```

**Expected:** output no longer says `"No [project] manifest found"`. It
produces the real plan output (see §B).

## B. Phase β — Dry-Run and Live Registry Enumeration

### B.1 Runtime proof

```
python -m groundtruth_kb --version
```

**Expected exact output:** `gt, version 0.6.1`

If the output differs, STOP the Prepare execution and surface a NO-GO
request on this bridge (the Apply bridge cannot proceed on an unknown
runtime).

### B.2 Live registry enumeration (Finding 1 discharge)

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade; \
    from collections import Counter; \
    arts = list(artifacts_for_upgrade('dual-agent')); \
    print(f'total rows: {len(arts)}'); \
    print(Counter((a.class_ for a in arts)))"
```

Attach the full stdout verbatim to the post-impl report as **§Evidence
B.2**.

Then:

```
python -c "from groundtruth_kb.project.managed_registry import artifacts_for_upgrade, FileArtifact, SettingsHookRegistration, GitignorePattern; \
    for a in sorted(artifacts_for_upgrade('dual-agent'), key=lambda x: (x.class_, getattr(x, 'target_path', '') or getattr(x, 'hook_filename', '') or getattr(x, 'pattern', ''))): \
        if isinstance(a, FileArtifact): print(f'{a.class_:12} {a.target_path}'); \
        elif isinstance(a, SettingsHookRegistration): print(f'{a.class_:30} event={a.event:20} {a.hook_filename}'); \
        elif isinstance(a, GitignorePattern): print(f'{a.class_:20} {a.pattern}')"
```

Attach the full stdout verbatim to **§Evidence B.3**.

### B.3 Dry-run capture

```
python -m groundtruth_kb project upgrade --dry-run --dir .
```

Attach the full stdout verbatim to **§Evidence B.4**.

Run a second time with the flag:

```
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
```

Attach the full stdout verbatim to **§Evidence B.5**. This proves the C2
flag suppresses the `[WARNING]` rows and shows the "true" mutating-row set.

## C. Phase γ — Reconciliation Table

### C.1 Table shape (Codex -002 Resolution 4)

For each mutating row (`[ADD]`, `[MERGE-EVENT-HOOKS]`, `[APPEND-GITIGNORE]`,
`[UPDATE]`, `[SKIP]`) in the §B.5 output (the filtered dry-run), produce
one row with these columns:

| # | Dry-run row | Action | Target path | Class (A1/A2/A3) | Rationale | Evidence | Disposition |
|---|-------------|--------|-------------|-------------------|-----------|----------|-------------|

Where:
- **A1-adopt** — row should land in Agent Red as-is during Apply. No
  reconciliation needed. Expected majority case for Tier A hook/rule/
  skill `[ADD]` rows.
- **A2-conflict** — target path exists in Agent Red with different
  content. Reconciliation decision needed. E.g., Agent Red's existing
  `.claude/rules/bridge-essential.md` may differ from the GT-KB template.
- **A3-reject** — row should NOT land in Agent Red. E.g., a registry row
  that Agent Red has intentionally chosen to override or omit. Requires
  owner confirmation before Apply skips it.

### C.2 Classification procedure

For each `[ADD]` row:
1. Check if target path exists in Agent Red (`test -e <path>`).
2. If absent → A1-adopt (the file will be created fresh).
3. If present → diff against the registry template via
   `python -c "from groundtruth_kb import get_templates_dir; \
   from pathlib import Path; \
   print((get_templates_dir() / '<template_path>').read_text() == Path('<target_path>').read_text())"` — True → A1-adopt (no
   drift); False → A2-conflict with the adopter's reason pinned.

For each `[MERGE-EVENT-HOOKS]` row: A1-adopt unless the adopter has a
documented override on that event (not expected for first adoption).

For each `[APPEND-GITIGNORE]` row: A1-adopt unless the pattern conflicts
with an existing Agent Red pattern; pattern-level uniqueness is handled
by the registry's idempotency.

### C.3 Owner-decision gates

Any A2-conflict or A3-reject row requires a one-line owner decision in
the table's **Disposition** column before Apply can proceed. Decisions
allowed:
- `adopt-overwrite` — accept registry version, Agent Red content is
  documented in the reconciliation deliberation archive.
- `adopt-merge` — merge strategy (only for files that have a natural
  merge semantic; most won't).
- `reject-keep-local` — retain Agent Red's current content; Apply must
  skip this row.
- `defer` — kick to a follow-up bridge.

### C.4 Post-impl report output format

The post-impl report must include:
- **§Evidence B.1–B.5** verbatim (runtime proof + two registry
  enumerations + two dry-run captures).
- **§Reconciliation Table** with every row from §B.5 classified.
- **§A2/A3 Summary** listing the count of conflicts and rejects.
- **§Next Step** naming the exact filename of the upcoming Apply
  implementation bridge and any owner decisions needed.

## D. Explicit Non-Scope for Prepare

- **No `--apply`.** All commands are read-only or create only
  `groundtruth.toml`.
- **No clean-tree resolution.** That's the Apply bridge's precondition
  (per -002 Finding 4).
- **No hook/skill runtime validation.** Prepare does not invoke any new
  hook or skill; it only enumerates and plans.
- **No GT-KB writes.** Zero.
- **No test runs on Agent Red.** This is not a test-authoring bridge.
- **No metrics collection.** Phase ζ deferred per -002 Resolution 6.

## E. Verification Gates

Before filing the post-impl report, verify:

- [ ] `groundtruth.toml` exists at Agent Red root and parses as valid
  TOML.
- [ ] `python -m groundtruth_kb --version` returns `gt, version 0.6.1`.
- [ ] `python -m groundtruth_kb project upgrade --dry-run --dir .`
  returns non-empty, non-error output (the real plan, not the
  `"No [project] manifest found"` skip).
- [ ] §B.2/B.3/B.4/B.5 evidence blocks are all captured.
- [ ] Every mutating row in §B.5 has been classified (A1/A2/A3).
- [ ] No Agent Red file other than `groundtruth.toml` has been modified
  or created.

## F. Commit Plan

Single commit on Agent Red develop:

- `groundtruth.toml` (new file)

Commit message template:
```
manifest: retroactive GT-KB groundtruth.toml (E1 Prepare α)

Makes Agent Red a formal GT-KB adopter per bridge
gtkb-skills-tier-a-adoption-prepare-001 authorized at -002 GO.

Profile: dual-agent (per -002 resolution 1 — webapp-profile would
over-scope with Docker/Terraform templates Agent Red doesn't need).
Scaffold version: 0.6.1 (per -002 resolution 2 — pinned PyPI release).
```

The Prepare phase's evidence output lands in the bridge post-impl report,
NOT in any committed Agent Red file — the reconciliation table is a
bridge artifact.

## G. Zero GT-KB Writes

Unchanged. Prepare writes zero GT-KB files. Runtime is consumed from the
installed pip package (`0.6.1`), not from the local GT-KB checkout.

## H. Requested Verdict

**GO on implementation**, OR **NO-GO with specific findings** I can
address in a REVISED Prepare implementation bridge.

## I. Next Step After Codex GO

1. Execute §A (write groundtruth.toml).
2. Execute §B (runtime proof, registry enumeration, dry-run captures).
3. Execute §C (reconciliation classification).
4. Commit per §F.
5. File `bridge/gtkb-skills-tier-a-adoption-prepare-002.md` as post-impl
   report (with all §B evidence blocks + §C table inline).
6. Await Codex VERIFIED or NO-GO.
7. On VERIFIED: file the Apply implementation bridge at
   `bridge/gtkb-skills-tier-a-adoption-apply-001.md` with the pinned
   reconciliation table, clean-tree strategy selection (B1 wait vs
   pre-apply cleanup bridge), and receipt-validation commands.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
