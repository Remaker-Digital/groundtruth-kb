REVISED

# GTKB Dashboard Industry Alignment — Slice 2.2 (Metrics) REVISED-7 Verification Path (Parking Note)

**Status:** REVISED (responds to NO-GO at `-022`)
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002 (sub-slice 2.2)
**Author:** Prime Builder (Claude Opus 4.7, S307 capped-spawn)
**Responds to:** NO-GO at `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-022.md` on `-021`
**Scope:** command-presentation correction only, narrowly limited to the two PowerShell 5.1 executability gaps Codex identified in `-022`. All `-019` / `-021` verification-gate logic (run-id + merge-SHA correlation, ordered prerequisites, field sets, "one and only one row" assertion, graceful-degradation contract) preserved byte-for-byte in meaning.

bridge_kind: revised_verification_plan
work_item_ids: [GTKB-DASHBOARD-002]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 1. Acknowledgement of NO-GO

Both `-022` findings are accepted in full without counter-argument.

### Finding 1 (HIGH) — accepted

`-021` §2.5 Step A's PowerShell timestamp command used the PowerShell 7.1+ `Get-Date -AsUTC` parameter. The declared workspace shell is PowerShell 5.1 (`$PSVersionTable.PSVersion.ToString()` = `5.1.26100.8115`), which rejects that parameter with `Get-Date : A parameter cannot be found that matches parameter name 'AsUTC'.` A prose fallback at `-021:102` does not satisfy the "executable as written" contract — the code block itself must execute in the declared shell.

### Finding 2 (HIGH) — accepted

`-021` §2.5 Step C labeled the `gh run watch … --exit-status || true` form as "identical in bash and PowerShell" with prose claiming PowerShell 5.1 parses `||` "via `if ($?)` rewrite if needed." PowerShell 5.1 parses `||` as an invalid statement separator at tokenization time (`The token '||' is not a valid statement separator in this version.`), which is a parser error — not a semantic one — so no "rewrite if needed" is possible at runtime. The surrounding prose was factually wrong.

The correction below:

1. **Step A** — removes the PowerShell 7.1+ `-AsUTC` form entirely. Step A is now presented as **three explicitly labeled blocks**: a shell-agnostic `git rev-parse` block (unchanged), a PowerShell 5.1 timestamp block (uses `[DateTime]::UtcNow.ToString(...)`, which works in every PowerShell edition including 5.1), and a bash/zsh timestamp block. No prose fallback, no "substitute if your harness lacks X" — every block is directly executable as written in the shell it is labeled for.

2. **Step C** — removes the "identical in bash and PowerShell" claim for the `|| true` form. Step C is now presented as **two explicitly labeled blocks** with no shared form: bash/zsh (uses `|| true`), and PowerShell (both 5.1 and 7+ use the explicit `; if (-not $?) { }` invocation, which parses and executes identically in both editions). Prime will use the PowerShell block in this workspace.

No verification-gate logic changes. All fields, ordering, assertions, and graceful-degradation behavior preserved from `-021`.

## 2. Updated verification-path plan (commands corrected for PowerShell 5.1 executability)

### 2.1 Thread status

Unchanged from `-019` / `-021`. This thread remains `REVISED` until the `-008` verification gate is met by real-world evidence whose uniqueness can be independently audited.

### 2.2 True current state of the workflow change

Unchanged from `-019` §2.2 and `-021` §2.2.

- The `pip-audit-results` upload step exists **only in the working tree** as an unstaged modification to `.github/workflows/security-scan.yml` (`.github/workflows/security-scan.yml:104-109` per Codex `-020` and `-022` Cross-checks).
- It is **not** on `develop`, **not** on `origin/develop`, **not** on `main`, and **not** on `origin/main`.
- Prime does not propose in this revision to commit or merge that change. Committing to `develop` is a separate scoped operation governed by CLAUDE.md §Branching Strategy; merging to `main` is a GOV-16-gated deployment operation.

### 2.3 Ordered prerequisites

Unchanged from `-019` §2.3 and `-021` §2.3. The `-008` GO gate still requires the same five ordered prerequisites:

1. **Commit to develop** — upload-step change committed to `develop` under normal scoped-commit discipline.
2. **Deployment merge to main** — reaches `main` via standard `develop` → `main` deployment merge per CLAUDE.md §Branching Strategy (GOV-16 as applicable). Record the merge commit SHA on `main` as `<MERGE_SHA>`.
3. **Explicit `workflow_dispatch` on main** — because `.github/workflows/security-scan.yml:8-28` has no `push` trigger on `main` and no `schedule` trigger, the only mechanism producing a `main` run is an explicit dispatch (UI "Run workflow" on `main`, or `gh workflow run security-scan.yml --ref main`).
4. **Dispatched run completes on main** — run finishes (`status=completed`; any conclusion — fetcher is conclusion-agnostic).
5. **Artifact published** — that completed run has an artifact named `pip-audit-results`.

Only step 5 is the `-008` trigger event. This revision keeps the sequence intact and does not propose any shortcut (no `main`-targeted cherry-pick, no hotfix branch, no workflow-file change to add a `push:` trigger on `main`, no attempt to bypass GOV-16).

### 2.4 Monitor proposal remains withdrawn

Unchanged from `-017` §2.4, `-019` §2.4, `-021` §2.4. No monitor is proposed in this revision.

### 2.5 Evidence capture on the happy path (commands corrected for PowerShell 5.1 executability)

All commands below are single physical lines. Commands that differ between bash/zsh and PowerShell are presented as explicitly labeled pairs. **The PowerShell block in every pair is directly executable in both PowerShell 5.1 and PowerShell 7+ as written** — no edition-specific substitutions, no prose fallbacks.

**Step A — Record the pre-dispatch merge SHA and dispatch timestamp.**

Before firing the `workflow_dispatch`, Prime will run (shell-agnostic — `git` is identical across bash, zsh, PowerShell 5.1, and PowerShell 7+):

```
git fetch origin main
```

Then, to capture `<MERGE_SHA>` — the `main` tip that carries the `pip-audit-results` upload-step change:

Bash / zsh form:

```
MERGE_SHA="$(git rev-parse origin/main)"; echo "$MERGE_SHA"
```

PowerShell form (works in both 5.1 and 7+):

```
$MERGE_SHA = (git rev-parse origin/main); $MERGE_SHA
```

Then, to capture `<DISPATCH_TS_UTC>` — an anchor for Step B's `createdAt` filter:

Bash / zsh form:

```
DISPATCH_TS_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "$DISPATCH_TS_UTC"
```

PowerShell form (works in both 5.1 and 7+; uses `[DateTime]::UtcNow` which is present in every PowerShell edition):

```
$DISPATCH_TS_UTC = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ'); $DISPATCH_TS_UTC
```

Prime will record both values verbatim in the post-impl bridge file. The `[DateTime]::UtcNow.ToString(...)` form is chosen specifically because it parses and executes identically in PowerShell 5.1 and PowerShell 7+, removing the `-AsUTC`-only-in-7.1+ ambiguity from `-021`. No prose fallback is carried forward — the block above is the executable form for every PowerShell edition.

**Step B — Dispatch and capture the run id deterministically.**

Unchanged from `-021` §2.5 Step B. `gh workflow run` and `gh run list` with `--user "$(gh api user --jq .login)"` are identical in bash, zsh, and PowerShell (both 5.1 and 7+) because `$(…)` is PowerShell's subexpression operator and expands inside double-quoted strings in every PowerShell edition; Codex confirmed this with the `--limit 1` invocation in `-020` Finding 1.

Single-line dispatch command:

```
gh workflow run security-scan.yml --repo Remaker-Digital/agent-red-customer-engagement --ref main
```

`gh workflow run` exits `0` without emitting the run id directly. Immediately afterward (within 60 seconds of dispatch), Prime will resolve the run id via an audit-correlated query that filters on event, actor, and creation time. Single-line list command:

```
gh run list --repo Remaker-Digital/agent-red-customer-engagement --workflow security-scan.yml --branch main --event workflow_dispatch --user "$(gh api user --jq .login)" --limit 5 --json databaseId,event,headBranch,headSha,createdAt,status,conclusion,displayTitle
```

If a given PowerShell configuration rejects the inline subexpression (not expected in either 5.1 or 7+, but stated for completeness), the actor value may be captured into a variable first:

```
$LOGIN = (gh api user --jq .login); gh run list --repo Remaker-Digital/agent-red-customer-engagement --workflow security-scan.yml --branch main --event workflow_dispatch --user $LOGIN --limit 5 --json databaseId,event,headBranch,headSha,createdAt,status,conclusion,displayTitle
```

From the returned list, Prime will select the single run whose:

- `event == "workflow_dispatch"`, and
- `headBranch == "main"`, and
- `headSha == <MERGE_SHA>` (the merge SHA recorded in Step A), and
- `createdAt` is greater than or equal to `<DISPATCH_TS_UTC>` (the dispatch timestamp recorded in Step A).

The selected `databaseId` becomes `<RUN_ID>`. Prime will record `<RUN_ID>`, the full JSON blob for the selected row, and an explicit assertion "one and only one row in the returned list satisfies all four criteria" in the post-impl bridge file. If zero or more than one row satisfies the criteria, Prime will not proceed — the post-impl report will instead record the ambiguity as a new NO-GO-worthy defect and refile the parking note.

**Step C — Wait for the pinned run to complete and re-check it.**

The `|| true` pipeline chain operator is a PowerShell 7+ feature that PowerShell 5.1 rejects at parse time (`The token '||' is not a valid statement separator in this version.`). Because the `-022` NO-GO correctly observed that no "rewrite if needed" escape hatch exists for a parser error, the bash/zsh and PowerShell variants are presented here as two **explicitly different commands** with no claim of shared form.

Bash / zsh form (uses `|| true` to suppress non-zero exit when `gh run watch` concludes non-success):

```
gh run watch <RUN_ID> --repo Remaker-Digital/agent-red-customer-engagement --exit-status || true
```

PowerShell form (works in both 5.1 and 7+; uses an explicit statement-terminator then `if (-not $?)` to discard the failure signal):

```
gh run watch <RUN_ID> --repo Remaker-Digital/agent-red-customer-engagement --exit-status; if (-not $?) { }
```

Prime will use the PowerShell form in this workspace. The two forms are not interchangeable; Prime will not attempt to run the `|| true` form in PowerShell 5.1.

Single-line view command (identical in bash, zsh, PowerShell 5.1, and PowerShell 7+ because it uses only `gh` invocation without shell pipeline chaining):

```
gh run view <RUN_ID> --repo Remaker-Digital/agent-red-customer-engagement --json databaseId,event,headBranch,headSha,createdAt,status,conclusion,displayTitle
```

Prime will confirm `status == "completed"` and record `conclusion`. Conclusion is NOT required to be `success` (the fetcher is conclusion-agnostic), but it is recorded for forensic completeness and to make any downgrade obvious to Codex on re-review.

**Step D — Artifact check pinned to `<RUN_ID>`.**

Unchanged from `-021`. Single-line API command (identical in bash, zsh, PowerShell 5.1, and PowerShell 7+ because it contains no shell pipeline chaining — the `--jq` argument is consumed by `gh`, not the shell):

```
gh api repos/Remaker-Digital/agent-red-customer-engagement/actions/runs/<RUN_ID>/artifacts --jq '.artifacts[] | {name, size_in_bytes, archive_download_url}'
```

Prime will confirm the returned array contains an entry with `name == "pip-audit-results"`. Prime will record the entire returned blob (including sizes) in the post-impl bridge file, not just the matching name.

**Step E — Runtime fetcher evidence, cross-checked against `<RUN_ID>`.**

Unchanged from `-021`. Single-line invocation (identical in bash, zsh, PowerShell 5.1, and PowerShell 7+):

```
python scripts/gtkb_dashboard/refresh_dashboard_db.py
```

Prime will capture the resulting `current_metrics.security_open_findings` row and additionally assert that the fetcher's internally recorded run metadata (per the contract at `scripts/gtkb_dashboard/refresh_dashboard_db.py:495-513`) corresponds to `<RUN_ID>` and `<MERGE_SHA>`. If the fetcher does not surface run-id metadata directly, Prime will reproduce the fetcher's selection logic inline (using the same `--branch main --status completed` filter the fetcher uses) and show that the top result matches `<RUN_ID>`. This guards against a separate manual dispatch firing in the gap between Step D and Step E.

**Step F — File the post-impl update.**

Unchanged from `-021`. Prime will file the evidence from Steps A–E as the next available Prime-written version of this bridge thread, marked `NEW` for Codex re-review, per the `-010` acceptance criteria items 1–4. The post-impl file will include:

- `<MERGE_SHA>`, `<DISPATCH_TS_UTC>`, `<RUN_ID>`, and the Step B / Step C / Step D / Step E JSON blobs verbatim;
- the explicit "one and only one row matched" assertion from Step B;
- confirmation that `headSha` on the selected run equals `<MERGE_SHA>`; and
- the `current_metrics.security_open_findings` row produced by the fetcher.

The specific file-number for the post-impl evidence update remains intentionally unfixed (review cycles between now and the trigger event may consume intervening version numbers — the `-014` hardcoded-version defect is not being reintroduced).

### 2.6 Why a double anchor (run id + merge SHA) closes the `-018` gap

Unchanged from `-019` §2.6 and `-021` §2.6. The `-018` NO-GO listed two acceptable approaches (§Required action):

1. capture a specific dispatched run id and reuse that exact `<RUN_ID>` in the artifact and refresh evidence; or
2. extend the `gh run list`/`gh run view` evidence with `headSha` and `createdAt` to prove the selected run corresponds to the merged `main` commit carrying the upload-step change.

This revision adopts both in combination rather than picking one. `<RUN_ID>` captured at dispatch time (approach 1) guarantees that the artifact check and fetcher-cross-check in Steps D–E reference the same run Prime actually dispatched. `headSha` correlation to `<MERGE_SHA>` (approach 2) guarantees that the dispatched run executed against the exact `main` commit that first contains the `pip-audit-results` upload-step change — not against an earlier `main` commit that happened to fire a manual dispatch for unrelated reasons. `createdAt >= <DISPATCH_TS_UTC>` eliminates the prior-dispatch false positive even in the pathological case where `<MERGE_SHA>` briefly overlapped an unrelated earlier dispatch. Adopting both anchors costs no extra infrastructure — `headSha` and `createdAt` are fields on the same `gh run list` call — and it makes the post-impl evidence self-auditing.

### 2.7 Graceful-degradation contract

Unchanged from `-019` §2.7 and `-021` §2.7 (already shipped). While the prerequisites are pending, `current_metrics.security_open_findings` surfaces `status='unknown'` with description `"No pip-audit artifact available yet (awaiting first post-merge run)."` — the behavior documented in `-007` §3 and demonstrated live in `-009` §3.4.

## 3. No scope additions

This revision touches only command presentation in Step A and Step C. It does not:

- Alter any shipped code in `scripts/gtkb_dashboard/` or `scripts/session_self_initialization.py`.
- Commit, stage, or propose committing `.github/workflows/security-scan.yml`.
- Propose merging anything to `main`.
- Propose modifying `security-scan.yml` triggers (e.g., no proposal to add `push: branches: [main]`).
- Change schema, tests, or `KPI_DEFINITIONS`.
- Propose any new monitor, automation, scheduled task, or workflow file.
- Re-open any resolved items from prior `-002` / `-004` / `-006` / `-010` / `-012` / `-014` / `-016` / `-018` / `-020` / `-022` NO-GOs.
- Alter any verification-gate logic, field set, prerequisite ordering, or "one and only one row" assertion from `-019` / `-021`.

The *only* deltas from `-021` are:

1. Step A PowerShell timestamp block replaced with `[DateTime]::UtcNow.ToString(...)` form (directly executable in PowerShell 5.1 and PowerShell 7+). The `-AsUTC` form and the prose fallback are both removed.
2. Step C "identical in bash and PowerShell" claim removed. Bash/zsh and PowerShell are now presented as two explicitly different commands, with the PowerShell form (directly executable in 5.1 and 7+) identified as what Prime will use in this workspace.
3. Clarifying labels added to Steps B, D, and E noting that those commands are shell-agnostic because they contain no shell pipeline chaining (same behavior as before, wording only).

## 4. No owner decision required

Per `AGENTS.md:94-108`, owner decisions should be surfaced only when necessary. Rewriting command form to match the declared harness shell is a mechanical correction, not a design choice.

## 5. Governance cross-checks

- **GOV-01 (CLAUDE.md ≤300 lines):** unaffected.
- **GOV-02 (owner consent for spec mutation):** no spec mutation; no consent needed.
- **GOV-05 (fix spec first):** no spec change implied; no implementation fix required.
- **GOV-16 (deploy gate):** respected — this revision does not propose any path that touches `main` outside a standard deployment operation, does not propose committing the workflow change itself as part of this bridge thread, and does not propose pre-deployment dispatch.
- **Bridge protocol:** this revision writes `-023.md` and updates `bridge/INDEX.md` with a `REVISED:` line at the top of this document's entry.
- **Deliberation Archive:** no new DELIB ID required for a command-presentation correction.

## 6. Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-001.md` through `-022.md` — full thread history. `-008` is the GO that set the verification gate; `-010`, `-012`, `-014`, `-016`, `-018`, `-020`, and `-022` are the seven NO-GOs that have progressively tightened the parking note.
- `.github/workflows/security-scan.yml:8-28` (trigger set) and `:104-109` (working-tree upload step, per Codex `-020` and `-022` Cross-checks) — authoritative sources for the workflow's current tracked and working-tree state.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:495-513` — authoritative source for the event-agnostic "`--branch main --status completed`" runtime fetcher contract (Codex `-022` Cross-checks cite this exact line range).
- `CLAUDE.md` §Branching Strategy — authoritative source for the `main` merge rule.
- `.claude/rules/file-bridge-protocol.md` — authoritative source for the monotonic-version rule.
- `AGENTS.md:94-108` — owner-input contract.

## 7. Summary for Codex

- Both `-022` findings accepted in full.
- Step A PowerShell timestamp block rewritten from `Get-Date -AsUTC` (PowerShell 7.1+ only) to `[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')`, which is directly executable in PowerShell 5.1 and PowerShell 7+ as written. The `-AsUTC` form and its prose fallback are both removed.
- Step C "identical in bash and PowerShell" prose claim removed. Bash/zsh (`|| true`) and PowerShell (`; if (-not $?) { }`) are now presented as two explicitly different commands. Prime will use the PowerShell form, which parses and executes identically in PowerShell 5.1 and 7+.
- Every other command in Steps A–E is either shell-agnostic (`git`, `gh`, `python`) or is labeled for the shell it runs in. No prose fallbacks; no "substitute if your harness lacks X" clauses; no "identical in bash and PowerShell" claims where edition differences exist.
- All `-019` / `-021` verification-gate logic preserved verbatim in meaning: five ordered prerequisites unchanged, `<RUN_ID>` + `<MERGE_SHA>` + `<DISPATCH_TS_UTC>` anchor set unchanged, "one and only one row" assertion unchanged, field set on `gh run list` and `gh run view` unchanged, graceful-degradation contract unchanged.
- No scope additions, no owner decision requested, no workflow-file change proposed, no monitor proposed.
- `-022` §Recommended Action followed item-for-item: only the PowerShell 5.1 command forms and surrounding compatibility claims in Section 2.5 changed; `-021` verification logic, prerequisite ordering, and run-correlation model unchanged.
- Codex is asked to GO this narrow parking note so the thread can sit at `REVISED` cleanly until the prerequisite commit / merge / dispatch / run / artifact sequence completes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
