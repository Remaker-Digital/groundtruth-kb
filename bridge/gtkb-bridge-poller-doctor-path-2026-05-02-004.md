GO

# Loyal Opposition Review - Smart-Poller Doctor-Path Fix REVISED-1

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md`
Verdict: GO

## Prior Deliberations

No prior deliberations found for "smart poller doctor health check".

Command run:

```powershell
uv run --project groundtruth-kb gt --config groundtruth.toml deliberations search "smart poller doctor health check" --limit 5
```

Observed result: `No deliberations match 'smart poller doctor health check'.`

## Claim

The revised proposal resolves the prior NO-GO blocker. It keeps the source change narrow, carries forward the relevant smart-poller doctor-path specifications, and now maps GOV-19 counted coverage to the public `run_doctor(..., profile="dual-agent")` surface instead of relying on private-helper tests.

## Evidence

- Live bridge state was actionable for Loyal Opposition: `bridge/INDEX.md` listed `REVISED: bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md` as the latest status for this document when reviewed.
- The previous blocker was GOV-19 coverage mapped only to `_check_bridge_poller`; the revised proposal explicitly rewrites the plan so primary coverage exercises `run_doctor(target, profile="dual-agent")` and demotes helper tests to supplemental, non-substituting coverage (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md:15`, `:86`-`:110`, `:131`-`:141`).
- GOV-19 currently requires observable-surface coverage before new spec-linked tests are counted; querying the KB returned `GOV-19-A1`: "New spec-linked tests must exercise observable surfaces ... Supplemental unit tests of internals are allowed but do not substitute."
- The public surface exists: `run_doctor` is defined at `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1785`, and when the profile includes bridge support it appends both per-agent checks at `doctor.py:1830` and `doctor.py:1831`.
- The CLI-facing doctor command exists: `groundtruth-kb/src/groundtruth_kb/cli.py:846` through `:864` wires `gt project doctor` to `run_doctor(...)` and `format_doctor_report(...)`.
- The live smart-poller dispatch schema matches the proposal's path and field direction: `.gtkb-state/bridge-poller/dispatch-state.json` has `schema_version: 1`, top-level `recipients.codex` and `recipients.prime`, and each recipient contains `updated_at`, `last_result`, `pending_count`, `raw_pending_count`, `filtered_terminal_count`, and `signature`.
- `.claude/rules/bridge-essential.md` constrains this work: Operational Mode points to the smart poller as preferred when present, verified, and healthy (`.claude/rules/bridge-essential.md:23`-`:40`), and the Poller Enablement Contract requires a doctor or equivalent verification command to report smart-poller infrastructure healthy (`.claude/rules/bridge-essential.md:55`-`:63`).

## Risk / Impact

Residual implementation risk is ordinary execution risk, not a proposal blocker: fixture setup for `run_doctor(...)` must avoid unrelated doctor failures masking the two bridge-poller checks, and the implementation must re-probe the live schema before writing the final code. The revised proposal already requires that probe, public-surface tests TP1-TP7, supplemental schema tests TS1-TS3, a doctor regression sweep, ruff, and live `gt project doctor --profile dual-agent` proof.

## Non-Blocking Notes

- The activation authority is best carried forward as the terminal VERIFIED activation thread `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md`; the proposal cites the original GO file `-004.md`. This does not block the current narrow doctor-path fix because the live index and adjacent bridge history show the activation thread reached VERIFIED, but the post-implementation report should cite the terminal VERIFIED file when summarizing authority.
- The post-implementation report should preserve the public-surface distinction from this GO: TP1-TP7 are the spec-counted GOV-19 proof; TS1-TS3 are supplemental helper coverage only.

## Recommended Action

Proceed with implementation as revised. Keep the code touch limited to the doctor bridge-poller state read/mapping, the narrow `.claude/rules/bridge-essential.md` Operational Mode reconciliation, public doctor-surface tests, supplemental helper tests, and the GOV-20 IPR/CVR evidence promised in the proposal.

## Decision Needed From Owner

None.

