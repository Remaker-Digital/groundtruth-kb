# WI-4395 uv cache command-surface disposition

Specs: GOV-STANDING-BACKLOG-001
WIs: WI-4395
Run time: 2026-06-13T08:44:23-07:00
Author: Loyal Opposition (Codex harness A)

## Claim

`WI-4395` no longer reproduces as an active default-uv-cache outage in the current Codex Loyal Opposition shell, but the work item should not be silently closed as "fixed." The durable gap is that GT-KB still lacks a canonical, tracked command surface that pins `UV_CACHE_DIR`, temp paths, and optional tool dependencies for automation and verification commands.

## Evidence

- Live role and queue selection: Codex harness `A` is `loyal-opposition`; live `bridge/INDEX.md` scan returned zero Loyal Opposition-actionable `NEW` or `REVISED` entries, so backlog fallback selection was appropriate.
- Live backlog: `uv run --project groundtruth-kb python -m groundtruth_kb.cli backlog list --id WI-4395 --json` succeeded and returned `WI-4395` as `priority=P1`, `stage=backlogged`, `resolution_status=open`, `approval_state=unapproved`.
- Current default uv cache: `uv cache dir` returned `C:\Users\micha\AppData\Local\uv\cache`.
- Current reproduction check: bare `uv run --project groundtruth-kb python -c "print('uv-default-ok')"` succeeded. The same command with `UV_CACHE_DIR=E:\GT-KB\.gtkb-state\uv-cache-lo-wi4395` also succeeded.
- Tool dependency checks: `uv run --project groundtruth-kb --with pytest python -m pytest --version` succeeded with `pytest 9.0.3`; `uv run --project groundtruth-kb --with ruff python -m ruff --version` succeeded with `ruff 0.15.12`. The in-root `UV_CACHE_DIR` variants also succeeded.
- Adjacent reproducibility evidence: `uv run --project groundtruth-kb python -m pytest --version` failed with `No module named pytest`, showing that successful test/lint surfaces still depend on exact `--with` or environment setup rather than project-local defaults.
- Existing drift indicators: `config/governance/runtime-evidence-retention.toml:16` treats `uv-cache` directories as runtime evidence; `config/governance/hygiene-baseline-registry.toml:668` records HYG-054, the 117 scratch-dir / 7.4GB ad hoc `--basetemp` and `uv-cache` sprawl; `scripts/cross_harness_bridge_trigger.py:1021` through `:1032` garbage-collects only stale pytest/uv-cache runtime directories under `.gtkb-state`.

## Finding

### P1-001 - The original cache failure is stale, but command reproducibility is still under-specified

Observation: The exact backlog symptom captured in `WI-4395` was "default uv cache fails; in-root `UV_CACHE_DIR` works." In the current shell, default uv-backed `gt backlog`, `pytest --version` with `--with pytest`, and `ruff --version` with `--with ruff` all run successfully against the default home-directory cache. That means the old error is not currently reproducible.

Deficiency rationale: The acceptance summary for `WI-4395` is stronger than "the current host happens to work." It asks that GT-KB automation and documented verification command surfaces avoid relying on `C:\Users\micha\AppData\Local\uv\cache` and prove a harness-writable cache location works when the default cache is denied or broken. The current repo still shows repeated ad hoc in-root cache names and no single tracked wrapper/config convention that future agents can use without rediscovering the right environment shape.

Impact: Without a canonical command surface, future bridge reports can again file evidence that works only in the author's shell, while Loyal Opposition reruns fail for cache, temp, or missing optional-tool reasons. That repeats the verification reproducibility failure recorded in `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-013.md`.

Recommended action: Prime Builder should convert `WI-4395` from "repair current uv outage" to a small command-surface hardening bridge. The proposal should define one supported wrapper or documented command prelude for GT-KB automation that sets `UV_CACHE_DIR`, `TMP`, `TEMP`, and optional tool flags under an approved in-root runtime-evidence location, plus regression coverage that simulates a bad default uv cache. It should also dedupe against HYG-054 / WI-4356 scratch-directory cleanup so the fix does not add another cache naming convention.

## Prime Builder context

| Element | Detail |
|---|---|
| Objective | Make uv-backed GT-KB commands reproducible across harnesses without relying on user-profile cache state. |
| Preconditions | File a normal implementation proposal; do not treat this LO report as implementation approval. |
| Evidence paths | `config/governance/runtime-evidence-retention.toml:16`; `config/governance/hygiene-baseline-registry.toml:668`; `scripts/cross_harness_bridge_trigger.py:1021`; `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-013.md`. |
| File touchpoints | Likely a command wrapper, docs/runbook surface, and tests; exact paths should be proposed by Prime Builder. |
| Implementation sequence | Define canonical env surface; add tests for denied default cache and missing optional tools; update docs/bridge evidence guidance; align cleanup/retention naming. |
| Verification steps | Run `uv` wrapper/default-cache failure simulation, a `gt backlog` command, `pytest --version` with tool provisioning, and `ruff --version` with tool provisioning. |
| Rollback notes | Revert wrapper/docs/tests; no MemBase or bridge history mutation should be needed. |
| Open decisions | None for Loyal Opposition. Prime may need owner approval if it wants to mutate governed command-surface docs or backlog state. |

## Decision needed from owner

None. This is an advisory disposition report. It does not close `WI-4395` in MemBase.

## Verification commands run

```text
uv --version
uv cache dir
uv run --project groundtruth-kb python -c "print('uv-default-ok')"
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-lo-wi4395'; uv run --project groundtruth-kb python -c "print('uv-inroot-ok')"
uv run --project groundtruth-kb python -m groundtruth_kb.cli backlog list --id WI-4395 --json
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-lo-wi4395'; uv run --project groundtruth-kb python -m groundtruth_kb.cli backlog list --id WI-4395 --json
uv run --project groundtruth-kb python -m pytest --version
uv run --project groundtruth-kb --with pytest python -m pytest --version
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-lo-wi4395'; uv run --project groundtruth-kb --with pytest python -m pytest --version
uv run --project groundtruth-kb --with ruff python -m ruff --version
$env:UV_CACHE_DIR='E:\GT-KB\.gtkb-state\uv-cache-lo-wi4395'; uv run --project groundtruth-kb --with ruff python -m ruff --version
rg -n "UV_CACHE_DIR|uv cache|uv-cache" .gitignore .claude .codex scripts config groundtruth.toml pyproject.toml -S
```
