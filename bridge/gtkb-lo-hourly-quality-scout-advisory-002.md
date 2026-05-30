ADVISORY

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: automation/scout/2026-05-30T04:19:41Z
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop automation

bridge_kind: loyal_opposition_advisory
Document: gtkb-lo-hourly-quality-scout-advisory
Version: 002
Author: Codex Loyal Opposition
Date: 2026-05-30T04:19:41Z

# Hourly Quality Scout Advisory - State Surface and Bridge Automation Reliability

## Source

Harness-level scheduled Scout automation `scout`, first recorded run for this automation memory.

## Inspected Surfaces

- `bridge/INDEX.md`
- `bridge/gtkb-lo-hourly-quality-scout-advisory-001.md`
- `docs/gtkb-dashboard/session-startup-report.md`
- `docs/gtkb-dashboard/startup-service-payload.json`
- `docs/gtkb-dashboard/dashboard-data.json`
- `groundtruth.db` read-only MemBase queries against `current_work_items`
- `memory/work_list.md`
- `memory/release-readiness.md`
- `.codex/hooks.json`
- `.claude/hooks/lo-file-safety-gate.py`
- `.claude/hooks/advisory-router-scan.py`
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`
- `scripts/advisory_backlog_router.py`
- `config/governance/lo-file-safety.toml`
- Git status and read-only verification command attempts

## Summary Of Findings

1. P1 - Startup/dashboard state surfaces materially underreport live work, drift, and bridge pressure.
2. P1 - The Loyal Opposition file-safety hook blocks harmless read-only searches containing comparison operators.
3. P1 - The advisory-to-backlog router is not runnable from the documented CLI shape and the Stop hook silently swallows the same likely import failure.

## Finding 1: Startup And Dashboard State Surfaces Underreport Live Work

Severity: P1

Claim: The owner-facing startup/dashboard state summary presents small queue and drift numbers that conflict with live MemBase, bridge, and git evidence.

Evidence:

- `docs/gtkb-dashboard/session-startup-report.md:54-57` reports 4 active backlog items, 26 open MemBase work items, 4 dashboard-scoped bridge/contention entries, and 3 drift changed paths.
- The same startup report at `docs/gtkb-dashboard/session-startup-report.md:68-69` reports 2248 current work items, 269 non-terminal work items, and 266 open work items.
- A read-only MemBase query of `groundtruth.db.current_work_items` found `open=266`, `in_progress=1`, `new=1`, `deferred=1`, for 269 non-terminal rows across 49 active project groups.
- A fresh parse of `bridge/INDEX.md` found 165 latest document states: 34 latest `GO`, 24 latest `NO-GO`, 65 latest `VERIFIED`, 40 latest `WITHDRAWN`, and 2 latest `ADVISORY`; that is 58 Prime-actionable bridge entries and 0 Loyal Opposition-actionable entries.
- `python scripts/audit_standing_backlog_sources.py` independently reported the same bridge latest status counts: `ADVISORY=2`, `GO=34`, `NO-GO=24`, `VERIFIED=65`, `WITHDRAWN=40`.
- `git status --porcelain=v1` reported 744 dirty paths: 54 modified, 6 deleted, and 684 untracked. The same status command emitted permission warnings for `C:\Users\micha/.config/git/ignore` and multiple `GT-KB.pytest-tmp*` directories. A root directory listing found 36 pytest scratch/cache directories under `E:\GT-KB`.
- `docs/gtkb-dashboard/session-startup-report.md:42-43` reports the Grafana health endpoint and GT-KB dashboard URL as unavailable, which means the human-visible dashboard path is down while the text summary is already inconsistent.

Risk/impact:

The owner and Prime Builder can believe the system has a small active queue and low drift while the live bridge, MemBase, and git state indicate a much larger operational load. This increases the chance of wrong sequencing decisions, missed Prime-actionable work, and release/readiness claims based on an incomplete state picture.

Recommended action:

Prime Builder should convert this to an implementation proposal that makes startup/dashboard state counters source-explicit and reconciliation-safe:

- Show separate counters for dashboard-scoped items, full MemBase non-terminal rows, full bridge latest-status counts, Prime-actionable bridge entries, Loyal Opposition-actionable bridge entries, and git dirty path counts.
- Treat inaccessible git-status paths and unavailable dashboard probes as warning-level state, not as invisible background noise.
- Add a regression that compares the rendered startup report against direct `current_work_items`, `bridge/INDEX.md`, and `git status --porcelain` collectors.

Owner decision needed: No.

Recommended Prime Builder disposition: Convert to implementation proposal.

## Finding 2: LO File-Safety Hook Blocks Read-Only Inspection Commands

Severity: P1

Claim: The Loyal Opposition file-safety gate misclassifies a harmless read-only `rg` command as a shell mutation when the search pattern contains a comparison operator.

Evidence:

- During this Scout run, the read-only command `rg -n "dev = \[|pytest>=|ruff>=|\[tool.pytest|\[tool.ruff" groundtruth-kb/pyproject.toml` was blocked before execution with: `BLOCKED (GTKB-LO-FILE-SAFETY): Loyal Opposition shell mutation to '=' is outside the allow-list`.
- `.codex/hooks.json:164-179` registers `lo-file-safety-gate.cmd` for both `Bash` and `apply_patch` PreToolUse enforcement.
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` delegates to `.claude/hooks/lo-file-safety-gate.py`.
- `.claude/hooks/lo-file-safety-gate.py` uses shell text heuristics for write detection. The redirection regex checks the character before `>`, so `pytest>=` can be parsed as `>` redirection with `=` as the target.
- `config/governance/lo-file-safety.toml` only lists write allow patterns; it does not define a read-command allowlist that would exempt `rg`, `Select-String`, `Get-Content`, or similar inspection commands before redirection heuristics fire.

Risk/impact:

Loyal Opposition review and Scout automation lose the ability to inspect normal source text containing comparison operators, version constraints, TOML assignments, or shell fragments. The failure is especially harmful because the gate is meant to protect mutations, not block read-only evidence gathering.

Recommended action:

Prime Builder should convert this to a narrow hook-fix proposal:

- Parse known read-only commands before mutation heuristics and allow `rg`, `Select-String`, `Get-Content`, `git status`, `git diff --name-only`, and equivalent read-only probes when no shell redirection or write cmdlet is present outside quoted strings.
- Replace the raw redirection regex with a quote-aware tokenizer or command AST helper.
- Add regression coverage for `rg` patterns containing `>=`, `<=`, `=>`, `=`, and TOML assignment text.

Owner decision needed: No.

Recommended Prime Builder disposition: Convert to implementation proposal.

## Finding 3: Advisory Backlog Router Is Likely Silent-Failing

Severity: P1

Claim: The bridge `ADVISORY` workflow depends on an advisory-to-backlog router, but the documented router command fails to import `groundtruth_kb`, and the registered Stop hook suppresses the same class of failure.

Evidence:

- `scripts/advisory_backlog_router.py:6-17` documents the CLI as `python scripts/advisory_backlog_router.py [--dry-run] [--source dropbox|bridge|both] [--since YYYY-MM-DD]`.
- Running `python scripts/advisory_backlog_router.py --dry-run --source bridge` from `E:\GT-KB` failed with `ModuleNotFoundError: No module named 'groundtruth_kb'`.
- `scripts/advisory_backlog_router.py:388` imports `KnowledgeDB` from `groundtruth_kb.db` inside `run()`.
- `.claude/hooks/advisory-router-scan.py:97-103` calls `module.run(...)`, then catches broad `Exception` and emits pass output. It does not add `groundtruth-kb/src` to `sys.path`, invoke the package through an installed environment, or report router failures.
- `.codex/hooks.json:285` registers `.claude/hooks/advisory-router-scan.py` as the Codex Stop-hook advisory router.
- `bridge/INDEX.md:51-52` already contains the Scout advisory thread as latest `ADVISORY`, so this automation depends on the router or Prime's direct bridge scan to avoid advisory loss.

Risk/impact:

New `ADVISORY` entries can be written correctly but never become MemBase backlog work items, and the Stop hook may hide that failure from the operator. This undermines the strategic self-improvement loop: important Loyal Opposition findings can appear durable in the bridge while being absent from the work authority Prime actually sequences.

Recommended action:

Prime Builder should convert this to an implementation proposal that makes the router fail-visible and environment-independent:

- Add deterministic import path setup in the wrapper and CLI, or provide a package entry point that runs in the `groundtruth-kb` environment.
- Make the Stop hook write router errors to `.gtkb-state/advisory-router/last-scan.json` or a bounded error log while still not blocking the turn.
- Add regression coverage for direct CLI dry-run from repo root and Stop-wrapper invocation against a temporary MemBase fixture.

Owner decision needed: No.

Recommended Prime Builder disposition: Convert to implementation proposal.

## Owner-Grilling Gate

Does this advisory imply future implementation work? Yes. All three findings recommend Prime Builder conversion proposals or scoped backlog work.

Has owner approval been obtained for implementation? No separate implementation approval is claimed. This Scout run is authorized to file an advisory only. Prime Builder must use the normal bridge proposal, GO, implementation, report, and verification workflow before changing source, hooks, dashboard code, or MemBase behavior.

Why this should not be dismissed as already tracked: prior work tracks dashboard, LO safety, and advisory-router themes broadly, but this run adds fresh live evidence: contradictory startup counts generated on 2026-05-30, a current false-positive LO hook block on a read-only `rg`, and a current router import failure on the documented CLI.

Expected reply shape if owner input is later requested: choose `convert`, `defer`, or `reject` per finding. No owner input is needed to let Prime Builder file normal proposals.

## Recommended Prime Builder Disposition

Convert Findings 1, 2, and 3 into normal implementation proposals. Treat Finding 2 and Finding 3 as the most urgent process-correctness repairs because they directly affect Loyal Opposition inspection and advisory durability. Finding 1 should follow as a dashboard/startup reconciliation proposal unless Prime Builder is already actively editing that surface.

