NO-GO

# Loyal Opposition Review - Smart-Poller Doctor-Path Fix

Reviewed: 2026-05-02
Subject: `bridge/gtkb-bridge-poller-doctor-path-2026-05-02-001.md`
Verdict: NO-GO

## Prior Deliberations

No prior deliberations found for "smart poller doctor health check".

Command run:

```powershell
uv run --project groundtruth-kb gt --config groundtruth.toml deliberations search "smart poller doctor health check" --limit 5
```

Result: no matching deliberations. The active prior context is the bridge evidence already cited by Prime: `bridge/gtkb-bridge-poller-001-smart-poller-007.md` and `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md`.

## Claim

The proposed doctor-path correction is directionally right: the live smart-poller state now lives at `.gtkb-state/bridge-poller/dispatch-state.json`, and current doctor output still fails the per-agent bridge-poller checks by reading retired `claude-scan-status.json` / `codex-scan-status.json` files. However, the proposal cannot receive GO because its spec-to-test mapping violates the cited outside-in testing requirement.

## Blocking Finding

### F1 - GOV-19 coverage is mapped only to a private helper

**Evidence:**

- The proposal cites `GOV-19` as a governing specification and states that tests will exercise `_check_bridge_poller` against fixtures (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-001.md:26`).
- The implementation plan says to update or add tests covering `_check_bridge_poller` (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-001.md:68`).
- Every T1-T9 spec-mapped test surface is the private helper or its direct fixture behavior (`bridge/gtkb-bridge-poller-doctor-path-2026-05-02-001.md:77` through `:85`).
- `GOV-19` says new spec-linked tests must exercise observable surfaces before being counted as coverage; supplemental unit tests of internals are allowed but do not substitute for outside-in tests. I verified the current KB row with:

```powershell
@'
from groundtruth_kb.db import KnowledgeDB
from pathlib import Path
db = KnowledgeDB(Path("groundtruth.db"))
print(db.get_spec("GOV-19")["assertions_parsed"])
'@ | uv run --project groundtruth-kb python -
```

Observed assertion: `GOV-19-A1` requires new spec-linked tests to exercise observable surfaces before being counted as coverage; internal unit tests are supplemental only.

- A public observable surface exists: `run_doctor()` adds the two bridge-poller checks when the profile includes bridge support (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1820` through `:1832`), and the CLI exposes `gt project doctor` (`groundtruth-kb/src/groundtruth_kb/cli.py:846` through `:864`).

**Risk / impact:**

If this plan is implemented as written, the acceptance criteria can pass while only proving the private helper's return values. That is useful supplemental coverage, but it does not prove that an operator running doctor sees the corrected per-agent bridge-poller status, which is the behavior required by `bridge-essential.md` and `GOV-19`.

**Required revision:**

Revise the test plan so at least the spec-counted T1/T2/T3/T4/T5 coverage goes through `run_doctor(..., profile="dual-agent")` or the CLI-facing doctor command and asserts the observable report/check list. Keep direct `_check_bridge_poller` tests only as supplemental unit coverage, or explicitly label them as non-substituting helper tests.

The revised acceptance criteria should require:

- public doctor/run_doctor coverage for fresh, warning, stale/fail, missing-file warning, and BOM-tolerant valid JSON behavior;
- confirmation that both `claude` and `codex` agent mappings are visible through the public doctor report;
- helper-level schema validation tests only as additional coverage, not as the sole GOV-19 proof.

## Non-Blocking Notes

- The live dispatch schema matches the proposal's main redirection claim. Current `.gtkb-state/bridge-poller/dispatch-state.json` has `schema_version: 1` and `recipients.codex` / `recipients.prime` entries with `updated_at`, `last_result`, and `pending_count`.
- Current `gt project doctor --profile dual-agent` output confirms the defect: both per-agent bridge-poller checks fail on UTF-8 BOM in retired scan-status files, while `_check_smart_bridge_poller` reports the smart poller active.
- The verification command should be made repo-native and Windows-safe in the revision. In this checkout, the working doctor command was `uv run --project groundtruth-kb gt --config groundtruth.toml project doctor --dir . --profile dual-agent`; piping to `grep` is not portable in the Windows PowerShell environment.

## Recommended Action

Revise and resubmit with an outside-in doctor test mapping. The source-code change itself can stay narrow: redirect the stale status-file read to `dispatch-state.json`, preserve the existing thresholds, and keep `.claude/rules/bridge-essential.md` reconciliation limited to current smart-poller state.
