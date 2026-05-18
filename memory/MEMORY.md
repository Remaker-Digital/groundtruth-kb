# Agent Red Memory

## Current Status

- **2026-05-18: Antigravity Integration completion drive started.**
  Owner directed prioritized completion of `PROJECT-ANTIGRAVITY-INTEGRATION`
  (add Google Antigravity as a 3rd AI coding harness; harness-registry refactor).
  Status reconciled across MemBase + `bridge/INDEX.md` + git: 7 WIs VERIFIED,
  2 GO (WI-3342 reader-migration, WI-3343 ADR extension), 6 TODO. Durable
  cross-session tracker created at `memory/antigravity-integration-status.md` --
  **future sessions tracking this project: start there.** Owner AUQ 2026-05-18
  authorized a MemBase status truth-up (work_items show `stage=backlogged`
  despite VERIFIED bridge threads). Open next: truth-up bridge proposal,
  WI-3342/WI-3343 implementation, WI-3345 spike + WI-3362 proposals.

- **S356 (2026-05-16): bridge-compliance-gate `SPEC_TEST_HEADING_RE` re.MULTILINE fix — VERIFIED + committed.**
  Branch `develop` @ `6d62ac1a`. Fixed the `SPEC_TEST_HEADING_RE` missing-`re.MULTILINE`
  defect that hard-blocked every Claude-authored VERIFIED bridge verdict
  (`_has_spec_derived_verification` never matched the mid-document `## Spec-to-Test Mapping`
  heading). Bridge thread `gtkb-bridge-compliance-gate-spec-test-heading-multiline-fix`:
  NEW→GO→NEW→NO-GO→REVISED→VERIFIED→VERIFIED (`-007` supersedes `-006`); `WI-3351`
  under `PROJECT-GTKB-RELIABILITY-FIXES` (reliability fast-lane). Committed `6d62ac1a` —
  11 files (re.MULTILINE in both `bridge-compliance-gate.py` copies + new regression test
  + 7 bridge files + INDEX); new test 10/10, existing bridge-compliance-gate suite 57/57,
  ruff clean. `develop` is 17 ahead of `origin/develop` — **not pushed** (push deferred to
  owner). Full handoff: `session_prompts` row S356. Open follow-ups: WI-3351
  `resolution_status` still `open` (stage→resolved deferred — WI not in a backlog snapshot);
  spawned task "Harden governance hooks for worktree sessions" awaits owner triage; sibling
  reliability threads `gtkb-bridge-compliance-gate-fenced-code-parser-fix` (WI-3336) and
  `gtkb-bridge-compliance-gate-wi-auto-regex-fix` (WI-3322) were GO but not implemented as
  of S356.

- **Fresh-session handoff (S353 wrap + addendum, 2026-05-15 PDT):**
  S353 was a Codex Loyal Opposition advisory/review session. Branch is
  `develop`; HEAD at wrap was `fd7bb43a`. The tree is dirty with active
  startup-relay implementation files, bridge files, skill adapter/manifest
  changes, and tests. No commit or push was attempted because the relay thread
  is latest `NO-GO` and the worktree includes mixed Prime-authored and
  LO-authored active artifacts.

  Addendum after the owner-decision tracker false-positive advisory: Codex wrote
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-15-07-owner-decision-tracker-startup-relay-false-positive.md`,
  recorded `WI-3332` ("Suppress already-known startup relay matches in
  owner-decision tracker") as an open P1 defect under
  `PROJECT-GTKB-RELIABILITY-FIXES`, linked the advisory report as project source
  evidence, and filed
  `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md`.
  Loyal Opposition review immediately returned `NO-GO` at
  `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-002.md`.
  The technical scope was accepted as directionally sound, but the operative
  bridge packet was authored by Codex while Codex was assigned Loyal Opposition;
  Prime Builder must refile the same technical scope as
  `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-003.md`
  with status `REVISED` and cite durable owner-routing evidence for `WI-3332`.
  Treat `WI-3323` only as related startup-relay context, not parent scope.

  Completed advisory #2: `gtkb-lo-opportunity-radar-skill` reached
  `VERIFIED` at `bridge/gtkb-lo-opportunity-radar-skill-004.md`.
  `SPEC-LO-OPPORTUNITY-RADAR-001` remains specified; the canonical
  `.claude/skills/lo-opportunity-radar/SKILL.md`, generated Codex adapter,
  manifest, registry entry, and `tests/skills/test_lo_opportunity_radar_skill.py`
  are present in the dirty tree. WI-3324 is resolved; project
  `PROJECT-GTKB-LO-OPPORTUNITY-RADAR` is active and intentionally kept open for
  future radar slices. Focused rerun during wrap: 6/6 opportunity-radar skill
  tests passed, adapter/parity tests 10/10 passed, bridge helper tests 34/34
  passed, and `scripts/check_harness_parity.py --all --markdown` reported
  PASS with 64 PASS / no parity issues.

  Advisory #1 remains open for Prime correction: the original
  `gtkb-startup-disclosure-relay-truncation-fix` thread was withdrawn at
  `bridge/gtkb-startup-disclosure-relay-truncation-fix-003.md`; the refile
  thread `gtkb-startup-relay-truncation-fix-refile` received GO at `-004`,
  Prime filed post-implementation report `-005`, and Codex returned
  `NO-GO` at `bridge/gtkb-startup-relay-truncation-fix-refile-006.md`.
  The blockers are: mandatory clause preflight reports a blocking
  `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` gap on the operative
  report, and the implementation still allows stale or non-disclosure cache
  content to satisfy the startup relay gate. WI-3323 remains open under
  `PROJECT-GTKB-RELIABILITY-FIXES`.

  Additional advisory produced:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  recommends a deterministic `skill_usage_router.py` / `gt skills
  suggest/check` first slice, followed by `gt bridge propose` hardening and
  `/verify` verdict-author/spec-to-test tooling. The report is under the
  gitignored CODEX insight dropbox and was not force-added.

  Live bridge scan after the addendum: `VERIFIED=162`, `NO-GO=65`, `GO=24`, `NEW=3`,
  `WITHDRAWN=28`, `ADVISORY=1`, `REVISED=0`. LO-actionable latest `NEW`
  entries are `gtkb-in-source-provenance-anchors-001-prop`,
  `gtkb-commit-scope-bundling-detection-001-prop`, and
  `gtkb-auto-push-investigation-001-prop`. Prime-actionable latest `GO` and
  `NO-GO` entries remain substantial; immediate Prime items include the
  startup-relay `NO-GO` revision and the owner-decision tracker `REVISED` refile.

  Wrap evidence is under `.groundtruth/session/snapshots/S353/`. Hygiene scan
  reported 38 ERROR / 2265 WARN, dominated by known
  `snapshots_non_manifest` historical outputs plus current dirty-tree warnings.
  Consistency scan reported 2 ERROR / 1903 WARN for the old missing
  `gtkb-isolation-018-slice-d-non-functional-content-{001,002}.md` INDEX
  citations and historical orphan bridge-file classes. DA harvest apply for
  S353 was blocked by `GOV-ARTIFACT-APPROVAL-001` because no native formal
  approval packet was supplied.

  Next session should start `::init gtkb pb`, re-read live `bridge/INDEX.md`,
  revise `gtkb-owner-decision-tracker-startup-relay-known-match-suppression`
  from Prime Builder as `REVISED`, then revise
  `gtkb-startup-relay-truncation-fix-refile` to close `-006` before committing.
  Do not assume the dirty tree is wholly owned by one thread; keep relay,
  opportunity-radar, bridge, memory, and advisory artifacts explicitly scoped.

- **Fresh-session handoff (S352 addendum, 2026-05-15 UTC):**
  Governance-chain mechanical enforcement closed. Live bridge shows the recent
  work threads verified: WI-3312/3313/3314/3315 were already verified and
  committed; WI-3317 `gtkb-impl-start-gate-format-spec-fix` is `VERIFIED` at
  `bridge/gtkb-impl-start-gate-format-spec-fix-008.md`; WI-3316
  `gtkb-project-verified-completion-auq-trigger` is `VERIFIED` at
  `bridge/gtkb-project-verified-completion-auq-trigger-008.md`; WI-3320
  `gtkb-bridge-compliance-audit-path-isolation` is `VERIFIED` at
  `bridge/gtkb-bridge-compliance-audit-path-isolation-006.md`; the chromadb
  hook-latency and reliability fast-lane threads also show `VERIFIED`.

  Owner approved project completion. Deliberation
  `DELIB-S352-GOVERNANCE-CHAIN-PROJECT-COMPLETION` was recorded, project
  authorization
  `PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN`
  is `completed`, and project `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001`
  / "GTKB Governance Chain Mechanical Enforcement" is `retired`.

  Current live bridge scan at wrap: `VERIFIED=160`, `NO-GO=63`, `GO=24`,
  `NEW=3`, `WITHDRAWN=27`, `ADVISORY=1`. Loyal Opposition-actionable latest
  `NEW` entries are `gtkb-in-source-provenance-anchors-001-prop`,
  `gtkb-commit-scope-bundling-detection-001-prop`, and
  `gtkb-auto-push-investigation-001-prop`. Prime Builder has 87 latest
  `GO`/`NO-GO` entries; `gtkb-gt-bridge-propose-deterministic-cli` remains
  `NO-GO` at `bridge/gtkb-gt-bridge-propose-deterministic-cli-002.md`.

  Focused verification rerun during wrap: project completion surface/lifecycle
  tests 25/25 passed; implementation-start-gate plus bridge-compliance
  audit-path tests 47/47 passed; targeted `ruff check` passed. Wrap evidence is
  under `.groundtruth/session/snapshots/S352-20260515/`; hygiene reported 35
  ERROR / 2238 WARN and consistency reported 2 ERROR / 1903 WARN, matching known
  snapshot report, old missing isolation-018 bridge-file citation, and
  historical orphan bridge-file classes. DA harvest apply is still blocked by
  `GOV-ARTIFACT-APPROVAL-001` without a native formal approval packet.

- **Fresh-session handoff (S352 wrap, 2026-05-14 UTC):**
  S352 was a Codex Loyal Opposition bridge-monitoring and wrap session. Branch
  is `develop`; HEAD at wrap was `d1448d43`. The branch is ahead 2 and the
  working tree remains broad and mixed across bridge, hook, skill, adapter,
  mode-switch, test, and memory files; no commit/push was attempted because
  this wrap did not own that full change set.

  Final live bridge scan from `bridge/INDEX.md` at `2026-05-14T20:49:11Z`:
  `VERIFIED=150`, `WITHDRAWN=24`, `GO=17`, `NO-GO=13`, `NEW=10`,
  `ADVISORY=1`. Loyal Opposition still has 10 latest `NEW` items. Prime
  Builder has 30 actionable latest `GO`/`NO-GO` entries. External Codex
  auto-dispatch workers produced additional NO-GO verdict files during wrap,
  including `gtkb-auto-push-investigation-slice-1-002`,
  `gtkb-commit-scope-bundling-detection-slice-1-002`,
  `gtkb-control-plane-placeholder-test-remediation-slice-1-revert-002`,
  `gtkb-gov-code-quality-baseline-formal-artifact-approval-002`,
  `gtkb-prime-worker-delivery-regression-slice-4-002`, and
  `gtkb-prime-worker-post-stop-dispatch-retry-slice-3-002`.

  Wrap artifacts are under `.groundtruth/session/snapshots/S352/`. Hygiene scan
  returned 33 ERROR / 2482 WARN; consistency returned 2 ERROR / 1904 WARN.
  `current_work_items` had 2072 rows at wrap with 126 `open`, 1 `in_progress`,
  1 `new`, 1774 `resolved`, 45 `verified`, 58 `retired`, 59 `wont_fix`, 7
  `not_a_defect`, and 1 `deferred`. `session_prompts` insertion succeeded for
  S352 version 1 at `2026-05-14T20:52:02+00:00`. Deliberation harvest apply was
  blocked by `GOV-ARTIFACT-APPROVAL-001` without a formal approval packet.

  Next session should start `::init gtkb pb`, re-scan the live bridge, process
  the large Prime-actionable queue in scoped batches, and avoid broad commits
  until the S349/S350/S351/S352 dirty-tree ownership is separated.

- **Fresh-session handoff (S351 wrap, 2026-05-14 UTC):**
  S351 was a Codex Loyal Opposition bridge-monitoring session. Branch is
  `develop`; HEAD at wrap was `b14786a0`. Live `bridge/INDEX.md` is the sole
  authoritative queue source and ended with 176 documents: 0 latest
  `NEW`/`REVISED`, 6 `GO`, 2 `NO-GO`, 143 `VERIFIED`, 24 `WITHDRAWN`, and 1
  `ADVISORY`.

  Main LO action: `gtkb-governed-spec-retirement` was reviewed and received
  NO-GO at `bridge/gtkb-governed-spec-retirement-004.md`; after Prime filed
  REVISED-2 at `-005`, Loyal Opposition approved GO at
  `bridge/gtkb-governed-spec-retirement-006.md`. The GO scope is
  `scripts/assertion_retirement_workflow.py` and
  `platform_tests/scripts/test_assertion_retirement_workflow.py`.

  Live Prime Builder-actionable queue at wrap:
  `gtkb-implementation-gate-friction-hygiene` NO-GO at `-002`,
  `gtkb-operating-mode-transaction-001` NO-GO at `-005`,
  `gtkb-governed-spec-retirement` GO at `-006`,
  `gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite` GO at `-010`,
  `gtkb-spec-lifecycle-schema-2026-04-29` GO at `-004`,
  `active-workspace-declaration-architecture-2026-04-29` GO at `-004`,
  `gtkb-gov-code-quality-baseline-slice1` GO at `-006`, and
  `gtkb-dora-001b-authoritative-deployment-source` GO at `-008`.

  Wrap artifacts: transcript manifest and scanner outputs are under
  `.groundtruth/session/snapshots/S351/`. Hygiene scan returned 31 ERROR /
  2339 WARN; consistency returned 2 ERROR / 1904 WARN, matching known
  snapshot/non-manifest, dirty-worktree, missing old slice-D files, and
  historical bridge-orphan classes. `session_prompts` handoff insertion
  succeeded for S351 v2 at `2026-05-14T04:34:37+00:00`. DA harvest apply was
  blocked by `GOV-ARTIFACT-APPROVAL-001` without a formal approval packet.
  Commit/push were skipped because the worktree is broad and mixed across
  S349/S350/S351 work; scope ownership before committing.

- **Fresh-session handoff (S350 wrap, 2026-05-14 UTC):**
  S350 had two threads of substantive work. Branch is `develop`; HEAD at start was `0419db0b`; many uncommitted parallel-session changes remain in the working tree (43 untracked + 28 added + 9 modified files).

  **Thread 1 — Operating-mode-transaction (NEW workstream).** Owner asked Prime to investigate the startup disclosure's `single_harness` topology report when two harnesses are installed with singleton role sets in `harness-state/role-assignments.json`. Root cause: `.claude/session/work-subject.json` stores `topology_mode` as canonical state; `scripts/session_self_initialization.py:4129` reads stored value rather than deriving from live role-map; 2026-05-13 role switch (recorded by `bridge/gtkb-owner-role-switch-codex-loyal-opposition-001.md` ADVISORY) updated `role-assignments.json` but not `work-subject.json` — exactly the ad-hoc-file-edit anti-pattern that `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` (approved 2026-05-13) was approved to prevent. Open P1 work item `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` was already on the books as an orphan in `gtkb-backlog-hygiene-bundle-s349` Finding 4.

  Filed `bridge/gtkb-operating-mode-transaction-001-001.md` (NEW) proposing a `gt mode set-role` deterministic transaction component + topology derivation in startup. Codex `NO-GO` at `-002` with two P1 findings: F1 hypothetical owner-waiver for deferred next-session-effectiveness (real waivers must cite real owner approval); F2 test paths under `tests/**` violating `pyproject.toml:9 testpaths = ["platform_tests", "applications/Agent_Red/tests"]`. Filed REVISED-1 at `-003` folding next-session-effectiveness into Slice 1 (new `groundtruth_kb.mode_switch.pending` module + SessionStart application of pending queue + 6 new spec-derived tests across `platform_tests/groundtruth_kb/` and `platform_tests/scripts/`) and relocating all test paths under `platform_tests/**`. Both preflights pass on `-003` (`preflight_passed: true`; 0 missing required; 0 blocking gaps; clause preflight 5 must_apply / 0 gaps). Awaiting Codex GO.

  **Thread 2 — Slice 4 (gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene).** Owner AUQ "Slice 4 hygiene first (Recommended)" routed Prime to the `-004` GO. Generated auth packet `sha256:1a45db1384a7...` (expires 2026-05-14T10:37:31Z). Audit revealed IP-1 (filename-vs-document parser hardening), IP-2 (named-packet cache + activate/list subcommands), IP-3 (configurable retention cap at `config/governance/assertion-runs-retention.toml`, default 50), and IP-5 (tracking `WI-3295` inserted at 02:42:48Z) were ALL already landed by a parallel S349 Prime session — `git diff --stat HEAD` at session start showed `scripts/implementation_authorization.py` +209 lines and `.claude/hooks/assertion-check.py` +97 lines. This session's only target-path edit was adding the missing test `test_gate_unchanged_reads_current_json_only` (~40 lines) to `platform_tests/scripts/test_implementation_start_gate.py`. **42/42 tests PASS** across `platform_tests/scripts/test_implementation_authorization.py`, `platform_tests/scripts/test_implementation_start_gate.py`, and `platform_tests/hooks/test_assertion_check_prune.py`. Filed post-impl `-005` with full per-IP accounting + transparent parallel-session-coordination disclosure. Both preflights pass on `-005`. Awaiting Codex VERIFIED.

  **Bridge state at wrap (updated mid-wrap as Codex dispatched against the new entries):**
  - `gtkb-operating-mode-transaction-001`: **GO at `-004`** (Codex approved REVISED-1 cleanly with no findings; cross-harness trigger fired during wrap-up). Next session: implement Slice 1 under a fresh `python scripts/implementation_authorization.py begin --bridge-id gtkb-operating-mode-transaction-001` packet; file post-impl at `-005`.
  - `gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`: **VERIFIED at `-007`** (Codex verified the implementation). Note: Codex verified the parallel-session-filed `-006` implementation report rather than this session's `-005`. Both are on disk per "never delete bridge files"; live INDEX has both listed as NEW. The `-006` report's "Supersedes-on-disk" wording called `-005` an "orphan" — Codex's verdict at `-007` corrected this to "superseded indexed report" since `-005` IS in INDEX. The verdict explicitly says the not-blocking distinction is wording-only.
  - `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage`: advanced from NO-GO `-012` to GO `-014` during this session (parallel-session action, not by S350 Prime).
  - 7 other GOs queued (Slice 1, Slice 2, spec-lifecycle-schema, active-workspace-declaration, gov-code-quality-baseline-slice1, dora-001b, etc.) plus 1 NO-GO (`gtkb-governed-spec-retirement`) per the bridge AXIS 2 surface.

  **Carry-forward defects + caveats:**
  - Implementation-start-gate fired 3 false-positives on read-only `python -c "...SELECT..."` Bash this session — same friction class flagged in S349 IP-3 follow-on candidates and Slice 4 `-005`'s § Sequenced Follow-Ons. Future Slice 5 or separate gate-friction-hygiene bridge needed.
  - INDEX has pre-existing defect `gtkb-single-harness-bridge-dispatcher-001.md` filename missing version suffix under its own `Document:` line; the parser-hardening fix at `scripts/implementation_authorization.py:108-178` correctly flags this. Should be addressed separately.
  - Many S349 parallel-session staged files (~70 files) remain uncommitted; this session's commit will scope strictly to S350-authored additions to avoid bundling.
  - DA harvest still blocked by `GOV-ARTIFACT-APPROVAL-001` packet requirement (carried from S347/S348/S349).
  - `session_prompts` insert blocked by same gate friction.
  - Wrap scanner output: 28 ERROR (`snapshots_non_manifest`, all pre-existing), 2316 WARN (`git_uncommitted_paths` mostly from S349 parallel state); consistency: 2 ERROR (pre-existing missing slice-d-non-functional-content files, same as S337+), 1904 WARN (orphaned bridge files mostly from agent-red prefix; pre-existing).

  **Wrap-time commit blocker (NOT resolved this session):** `git commit` was blocked by `GTKB-IMPLEMENTATION-START-GATE` with reason "Bridge latest status drifted to NEW; latest GO required". The slice-4 auth packet `sha256:1a45db13...` was issued when latest was GO at `-004`; live INDEX now has VERIFIED at `-007` (with intermediate NEW entries for `-005` and `-006`), so the packet's latest-status drift check fails closed. The gate is correctly preserving the "no further mutations to a VERIFIED slice" invariant, but `git commit` of already-done in-target-path work is arguably a snapshot-not-mutation operation. Documented as gate-friction-class follow-on in `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-005.md` § Sequenced Follow-Ons and acknowledged by Codex's `-007` VERIFIED. The next session's first action should be to either: (a) implement the topology fix under a fresh `gtkb-operating-mode-transaction-001` auth packet (its `GO` is live) and commit BOTH the carryover staged content + the new topology work under that packet, OR (b) file a dedicated gate-friction-hygiene bridge proposal that narrows the gate to source-file-mutation rather than commit-class operations.

  Next-session opening prompt: `::init gtkb pb` then check the staged-but-uncommitted state from S350 (75 staged files, +13616/-23 lines) and decide which approach to use to clear the working tree. The topology fix is the natural next implementation: it has fresh GO at `-004`, target_paths spanning the mode_switch module + `scripts/session_self_initialization.py` + `scripts/workstream_focus.py` + `scripts/single_harness_bridge_dispatcher.py`. Generate auth packet, implement Slice 1 covering all six acceptance criteria, file post-impl at `-005`.

- **Fresh-session handoff (S349 wrap, 2026-05-14 UTC):**
  S349 was the self-diagnostic investigation + leak-closure session. Owner
  asked Prime to probe agent behavior for "leaks, gaps and waste"; investigation
  produced quantitative findings on 5 leaks, then filed 3 implementation
  proposals as `GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE` umbrella (Slices 1-3). All
  three reached `GO` after 5 NO-GO rounds each (~10 hours of bridge wall-clock
  time, 30 bridge files). Slice 3 implementation began under GO at
  `bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md`;
  IPs 1, 2, 4a complete; IPs 3, 4b, 5, 6, 7 + impl report carry forward.

  Implemented in S349 (Slice 3 IP-1 + IP-2 + IP-4a):
  - `scripts/assertion_categorize.py` - read-only categorization
  - `scripts/assertion_retirement_workflow.py` - one-at-a-time owner-AUQ retirement
  - `platform_tests/scripts/test_assertion_categorize.py` - 10/10 PASS

  Live categorization output at `.gtkb-state/assertion-triage/20260514T003636Z/`:
  2576 assertions examined, 1636 currently failing decomposed into 34
  chronic_noise (owner-actionable retirement), 1595 flaky (test-quality
  repair), 0 genuine_drift, 947 healthy. The S347/S348 "1463 FAIL - known
  broad historical failure profile" is now mechanically actionable.

  Implementation-discovered constraints (S349 follow-on candidates):
  1. `assertion_runs` is pruned to 5 runs/spec by
     `.claude/hooks/assertion-check.py` line 489; SPEC's "50 consecutive"
     threshold defaulted to 5 per SPEC's "configurable" clause.
  2. `.gtkb-state/implementation-authorizations/current.json` is
     single-active-scope. Parallel slice work requires refresh-before-each-write;
     PostToolUse hooks thrash the packet between calls.
  3. `implementation-start-gate` INDEX-parsing appears to mis-attribute other
     documents' NO-GO to the active bridge id (blocked IP-3 even when Slice 3
     latest was GO at -008).

  Bridge GOs in flight (carry forward to next session):
  - Slice 1 advisory router: `GO` at -010 (implementation not started)
  - Slice 2 benchmark suite: `GO` at -010 (implementation not started)
  - Slice 3 assertion triage: `GO` at -008 (3/7 IPs done)

  Parallel work observed (not actioned by Prime in S349): Codex-filed
  `gtkb-backlog-hygiene-bundle-s349` covers 12 backlog hygiene findings
  including overlap with S349 LEAK 5 (implementation-start-gate over-blocking).
  Last seen at NO-GO -012 then advanced through -013 by Codex.

  DA harvest blocker (carried from S347/S348): `harvest_session_deliberations.py
  --session S349` dry-run shows 629 `bridge_thread` sources would-create;
  blocked by `GOV-ARTIFACT-APPROVAL-001` packet requirement. Harvest backlog
  continues to grow across sessions.

  Verification: `pytest platform_tests/scripts/test_assertion_categorize.py`
  10/10 PASS. `ruff check` on new scripts: 13 style errors (4 fixable with
  `--fix`, mostly import sorting), no test impact. Wrap scanners ran; outputs
  at `.groundtruth/session/snapshots/S349/wrap-scan-{hygiene,consistency}.md`
  (322KB / 293KB). Implementation-start packets active until 2026-05-14T08:43Z
  (Slice 1, 2) and 2026-05-14T08:45Z (Slice 3 refresh); will need fresh
  `begin` next session.

  Next-session opening prompt: `::init gtkb pb` then resume Slice 3
  implementation under live GO. First address the gate INDEX-parsing defect
  and auth-packet thrashing - they block parallel implementation. Then
  complete remaining Slice 3 IPs (IP-3 hook update, IP-4b retirement tests,
  IP-5 skill, IP-6 canonical-terminology + approval packet, IP-7 tracking
  WI), file the implementation report, and pursue VERIFIED. Then Slice 1
  and Slice 2 under their `GO`s at -010.

- **Fresh-session handoff (S348 wrap, 2026-05-13 UTC):**
  Final implementation commit on `develop` is `e946b349`
  (`docs(wrap): improve session knowledge collection`) and has been pushed
  to `origin/develop`. The wrap-up skill knowledge-collection upgrade
  completed a full bridge cycle:
  `gtkb-session-wrap-knowledge-collection` reached `VERIFIED` at
  `bridge/gtkb-session-wrap-knowledge-collection-004.md`. Implemented
  surfaces: canonical `.claude/skills/kb-session-wrap/SKILL.md`,
  handoff/audit reference templates, generated Codex skill adapter,
  `.codex/skills/MANIFEST.json`, harness capability registry entry, and
  `platform_tests/scripts/test_kb_session_wrap_skill.py`. Focused
  verification: wrap-skill regression tests passed 4/4; adapter/parity tests
  passed 10/10; Codex skill adapter check passed with 27 adapters current;
  bridge applicability and ADR/DCL clause preflights passed; `git diff
  --check` passed with only CRLF normalization warnings. Live bridge scan
  after the push: 167 documents, 0 latest `NEW`/`REVISED`, 4 latest `GO`,
  139 `VERIFIED`, 24 `WITHDRAWN`. S348 wrap scanners exited 2 on known
  structural classes: snapshot non-manifest report files (including the
  generated S348 wrap-scan report) and missing old
  `gtkb-isolation-018-slice-d-non-functional-content` bridge files cited by
  `bridge/INDEX.md`; warnings remain dominated by historical bridge files not
  referenced by the trimmed live index. Broad assertion check still reports
  `224/1687 PASS` and `1463 FAIL`, matching the known broad historical
  failure profile rather than this slice. Deliberation harvest was dry-run
  only for S348 (`609` bridge-thread sources would-create); no DA mutation was
  applied because formal approval evidence was not supplied for the broad
  harvest. Next-session handoff prompt was inserted into `session_prompts` for
  S348. No staging/production deployment was performed.
- **Fresh-session handoff (S347 wrap, 2026-05-13 UTC):**
  Final implementation commit on `develop` is `36f6c2d8`
  (`feat(governance): add project-scoped implementation authorization`) and
  has been pushed to `origin/develop`. Project-scoped implementation
  authorization completed a full bridge cycle:
  `gtkb-project-scoped-implementation-authorization` reached `VERIFIED` at
  `bridge/gtkb-project-scoped-implementation-authorization-010.md` after a
  Loyal Opposition `NO-GO` at `-006` found stale project-authorization packet
  revalidation. The corrective continuation at `-007`/`-008` added packet-load
  revalidation against stored `spec_links`; report `-009` was verified at
  `-010`. Implemented surfaces: MemBase `project_authorizations`, project
  authorization CLI commands, implementation-start metadata validation,
  automatic backlog creation/linkage for implementation-bearing specs,
  deterministic project attachment when explicit, rule/skill/glossary updates,
  formal approval packets, and focused regression tests. Focused verification:
  30 tests passed with 1 warning; bridge applicability and ADR/DCL clause
  preflights passed; Codex skill adapter check passed; narrative-artifact
  evidence passed. Broad assertion check still reports `224/1687 PASS` and
  `1463 FAIL`, matching the broad historical failure profile rather than this
  slice. Deliberation harvest was attempted and blocked by
  `GOV-ARTIFACT-APPROVAL-001` because no formal approval packet was supplied.
  Wrap scanners exited 2 on known structural classes: non-manifest snapshot
  report files and missing old `gtkb-isolation-018-slice-d-non-functional-content`
  bridge files cited by `bridge/INDEX.md`. No staging/production deployment was
  performed. Live bridge scan after the S347 push: 166 documents, 0 latest
  `NEW`/`REVISED`, 4 latest `GO`, 138 `VERIFIED`, 24 `WITHDRAWN`.
- **Fresh-session handoff (S340 Prime Builder wrap, 2026-05-11 UTC):**
  Final HEAD on `develop` is `9395b7cf`
  (`docs(bridge): Codex verdicts on S340 freshly-filed threads`). The
  branch is ahead of `origin/develop` by 40+ commits (no push during
  S340 wrap). S340 closed two major bridge threads VERIFIED and filed
  two more for Codex review:
    - **18.E.1 atomic code cluster move (1,423 files):** VERIFIED at
      `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-020.md`.
      Implementation across commits `c1021ab0` (Steps 3-6) + `58ac3ef5`
      (S339 Steps 0-2). 16 governance + 5 spec-derived rename tests
      passing.
    - **tests/ → platform_tests/ collision-resolution rename
      (116 files):** VERIFIED at
      `bridge/gtkb-tests-package-collision-resolution-008.md`.
      Implementation in commit `a641f622`. Criterion 5 owner-waived for
      `<=4` (pre-existing `test_host.suites` defect that was never on
      develop). Full collect: 12,329 tests / 4 errors, down from 17.
    - **GTKB-ARTIFACT-RECORDER-CLI scoping (S312 owner-approved):**
      filed at `bridge/gtkb-artifact-recorder-cli-001.md` (commit
      `8e7990c3`); Codex NO-GO at `-002` with two findings (F1 missing
      `GOV-STANDING-BACKLOG-001` citation; F2 stale coupled-thread state
      claims against live `bridge/INDEX.md`). Awaits REVISED-2 at `-003`
      per Codex's 4-point GO-able Revision Path.
    - **`gtkb-role-session-lifecycle-simplification` REVISED-1:** filed
      at `bridge/gtkb-role-session-lifecycle-simplification-003.md`
      (commit `afff91ab`); **Codex GO at `-004` authorizes
      implementation**. Three findings (F1 missing role-governance
      specs; F2 governance-adoption regression; F3 acting-prime
      compatibility contract) all addressed. 4 slices + 4 T-compat-*
      tests + 5 protected narrative-artifact writes (require formal-
      artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`).
  Wrap scanners pass clean (W0/W1/W2 exit 0; info/warn level only;
  long-standing MEMORY.md and DA citation drift unchanged). Deliberation
  harvest deferred (formal-artifact-approval-gate blocks
  `scripts/harvest_session_deliberations.py` without per-record approval
  packets — exact friction that GTKB-ARTIFACT-RECORDER-CLI is designed
  to address). Worktree intentionally has 2 untracked build-output
  paths (`applications/Agent_Red/widget/storybook-static/`,
  `platform_tests/results/`) and Codex's running log
  `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md`. **Next
  session prioritized actions** per S340 tranche selection: (1)
  implement role-session-lifecycle-simplification GO at `-004` (5
  protected narrative-artifact writes with approval packets + script
  edits + 4 new tests + post-impl report at `-005`); (2) revise
  ARTIFACT-RECORDER-CLI to `-003` REVISED-1 addressing the two findings;
  (3) CODEX-BRIDGE-COMPLIANCE-GATE-PARITY implementation per `-008` GO
  conditions (script extension + 3 regression tests; bounded scope); (4)
  continue Wave 2 NO-GO triage (4 actionable remaining); (5) MemBase
  Slice A scoping bridge (per `gtkb-membase-effective-use-recovery-2026-04-29-002`
  scoping GO). DECISION-0517 (false-positive class) was cleared during
  S340. Auto-memory updates: `feedback_bridge_compliance_gate_strict_heading.md`
  extended with `###` sub-heading rule (sub-headings inside
  `## Specification Links` break the detector); new project memory
  `project_role_session_lifecycle_implementation.md` captures
  implementation scope.
- **Fresh-session handoff (2026-05-10 23:21 PDT):** Final HEAD observed as
  `afff91ab` (`docs(bridge): role-session-lifecycle-simplification REVISED-1 at -003`)
  on `develop`, ahead of `origin/develop` by 37 commits. Live
  `bridge/INDEX.md` parse at wrap showed 127 docs, `GO=28`, `NO-GO=17`,
  `REVISED=1`, `VERIFIED=81`, latest `NEW`/`REVISED` = 1
  (`gtkb-role-session-lifecycle-simplification` at
  `bridge/gtkb-role-session-lifecycle-simplification-003.md`), and
  Prime-actionable latest `GO`/`NO-GO` = 45. Peer-solution advisory work is
  handed to Prime through
  `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md`; supporting
  report:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md`.
  Recommended next step is a Prime proposal, rebuttal, or explicit defer
  decision for the Peer Solution Advisory Loop and/or an Archon-derived
  GT-KB-native declarative workflow contract. `python .claude/hooks/assertion-check.py`
  failed during wrap with `224/1687 PASS, 1463 FAIL`; investigate before any
  release/deploy/quality-score claim. Worktree remains intentionally dirty with
  unrelated/concurrent changes including `memory/pending-owner-decisions.md`,
  untracked
  `bridge/gtkb-artifact-recorder-cli-002.md`, `platform_tests/results/`, and
  `applications/Agent_Red/widget/storybook-static/`. Wrap report:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SESSION-WRAP-CODEX-LOYAL-OPPOSITION-2026-05-10-23-21.md`.
- **Fresh-session handoff (2026-05-10 17:15 PDT):** Current HEAD is
  `58ac3ef5` (`wip(isolation): E.1 Steps 0-2 + platform-files (resume at Step
  3)`) on `develop`, ahead of `origin/develop` by 27 commits. Loyal Opposition
  bridge queue is empty from a live `bridge/INDEX.md` scan: 124 docs,
  `GO=29`, `NO-GO=13`, `VERIFIED=79`, `WITHDRAWN=3`, latest `NEW`/`REVISED` =
  0. Prime-actionable top item remains `gtkb-isolation-018-slice-e1-atomic-code-move`
  latest `GO` at `bridge/gtkb-isolation-018-slice-e1-atomic-code-move-016.md`.
  E.1 is intentionally mid-flight: Steps 0-2 plus platform files are committed;
  resume at Step 3 (atomic move, path edits, tests, post-move proof, final
  implementation commit, then post-impl bridge report). Startup-rollup change
  committed at `a11d27e1`; standard Loyal Opposition startup now includes the
  MemBase project-state rollup. Assertion check: `1653/1687 PASS`, quality
  `91.1/100`, 34 known failures. Focused startup tests and Ruff passed. Wrap
  report:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SESSION-WRAP-CODEX-LOYAL-OPPOSITION-2026-05-10-17-15.md`.
- **Fresh-session handoff (2026-05-09, end of S339 Codex LO wrap):** Live bridge state changed during wrap-up. Final scan at 11:04 PDT showed 1 latest `REVISED` LO-actionable entry: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001` at `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`. `gtkb-loyal-opposition-startup-symmetry-001` has an uncommitted `NO-GO` verdict at `bridge/gtkb-loyal-opposition-startup-symmetry-001-006.md` plus a modified `bridge/INDEX.md`; reconcile before push. Branch `develop` is 9 commits ahead of `origin/develop`; working tree remains dirty (`bridge/INDEX.md`, `memory/pending-owner-decisions.md`, untracked startup-symmetry `-006`). Assertion check remains `1654/1687 PASS`, quality `91.1/100`, with 33 known docs/runbook failures. Wrap scanners still fail on known historical bridge/snapshot hygiene plus current uncommitted bridge state. Session report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/SESSION-WRAP-CODEX-LOYAL-OPPOSITION-2026-05-09-S339.md`.
- **Fresh-session handoff (2026-05-09, end of S338 Codex wrap):** Loyal Opposition bridge queue is clear: live `bridge/INDEX.md` scan after wrap shows `LoyalOppositionActionable=0` and `PrimeActionable=32`. Codex processed 2 post-implementation bridge reports: cross-harness active-session suppression VERIFIED at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md`; DA Phase 3 glossary-expansion hook REVISED-1 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-010.md`. Targeted evidence: suppression tests `30 passed` plus legacy trigger suite `17 passed, 1 deselected`; glossary hook `20 passed`; targeted `ruff check` and `ruff format --check` passed. Assertion check from S338 wrap remains `1654/1687 PASS`, quality `91.1/100`, with 33 pre-existing/residual failures. Deliberation harvest remains deferred because the formal-artifact approval hook blocks `scripts/harvest_session_deliberations.py`; do not bypass without an approval packet. Worktree is intentionally mixed/dirty with Prime-owned implementation, archived smart-poller files, and Codex bridge verdicts; no broad commit/push was performed during Codex wrap.
- **Fresh-session handoff (2026-05-07, end of S335):** S335 wrap commit (pending push) records the lift-feature-freeze cycle — `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` inserted, S327 freeze + release-path framing fully lifted, 7 target WIs cleared of freeze/defer language, work_list.md rewritten with per-leverage priority bands (no freeze-derived sequencing). Bridge `gtkb-lift-feature-freeze` VERIFIED at `-012`. **Acceleration items now actionable:** Backlog DB Slices 2-7, `GTKB-ARTIFACT-RECORDER-CLI`, Term Primer Slices 2-5, Resource Disambiguation Slices 2-5. **Preserved release blockers:** `DELIB-S330` canonical Agent Red migration prerequisite + P0 secrets-purge override + in-flight Slice 8.5/8.6 — rc1 tag still NOT authorized. Live `bridge/INDEX.md`, not this summary, remains authoritative for queue status.
- **S335 session-numbering disclosure:** the lift-feature-freeze bridge artifacts and the DELIB use `S332` in content/IDs; the actual session is S335. Future references to this work cite the DELIB ID `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` and the bridge thread `gtkb-lift-feature-freeze`; the session is recorded as S335 in MEMORY.md.
- **Loyal Opposition bridge queue:** Live scan at S334 close showed 0 latest `NEW`/`REVISED` for Loyal Opposition; my two S334 filings (REVISED-3 and Slice-1 impl report) returned VERIFIED + GO during the same session.
- **Prime Builder next bridge actions:** Revise legacy `NO-GO` items still open from prior sessions: `gtkb-pre-filing-preflight-rule`, `gtkb-pre-filing-preflight-hook`, `gtkb-env-inventory-drift-control-001`, `gtkb-harness-parity-baseline`. Implement `GO`'d `gtkb-codex-bridge-compliance-gate-parity-008` (REVISED-3 implementation: parity-checker extension + `test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled` + negative fixture). Triage the 8 in-flight `gtkb-isolation-018-*` files left untracked since prior sessions.
- **Azure OpenAI key rotation:** confirmed rotated 2026-05-04. Fingerprint comparison (sha256:0..16): pre-reset leak `67bc4d57bc0a4762`; current `.env.local` `abff80a02123ad08`; both 84-char Azure-format. New value lives only in gitignored `.env.local`.
- **Secrets P0:** `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` is `VERIFIED` for approval-packet preparation only. No mirror rehearsal, live history rewrite, force-push, tag operation, credential action, release, or deployment is approved.
- **Harness roles / inventory:** Durable role map currently records Codex `A` as `loyal-opposition` and Claude `B` as `prime-builder`; dev-environment inventory was regenerated and drift check passed clean.
- **Prime-actionable CI blocker:** GitHub Actions `Release Candidate Gate` failed on `origin/develop` commit `6e04e60e`; current repair targets six stale/drifted Python-gate assertions.
- **Canonical repo aliases:** GT-KB aliases resolve to `https://github.com/Remaker-Digital/groundtruth-kb`; Agent Red resolves to `https://github.com/mike-remakerdigital/agent-red` only when explicitly scoped.
- **Release target:** v0.7.0-rc1 remains the GT-KB framework release target; irreversible Agent Red migration/cutover remains blocked until deployability preservation is verified or waived.
- **Production:** v1.98.92 hibernating since 2026-04-27. Resume runbook: `memory/agent-red-hibernation-runbook-2026-04-27.md`.
- **Smart poller:** S320 VERIFIED; Windows task `GTKB-SmartBridgePoller`, state under `.gtkb-state/bridge-poller/`.
- **Knowledge DB:** `groundtruth.db` at repo root is gitignored; ChromaDB retrieval aid at `.groundtruth-chroma/`.

## Feedback Index
- [Worktree drift pattern](feedback_worktree_drift_pattern.md) — Don't work from `.claude/worktrees/*` branches behind develop. S307.
- [No hardcoded paths](feedback_no_hardcoded_paths.md) — Use relative/discovered paths or env vars; 5-category triage. S307.
- [Pedagogical comments](feedback_pedagogical_comments_standard.md) — Module docstrings + why-comments + rationale links. S307.
- [Prime Builder default role](feedback_prime_builder_default_role.md) — Always start as Prime Builder. S305.
- [Canonical content in active surfaces](feedback_canonical_content_in_active_surfaces.md) — Canonical terms in CLAUDE.md/AGENTS.md/.claude/rules/. S305.
- [Bridge autonomy](feedback_bridge_autonomy.md) — Never ask owner to sweep/check/repair bridge.
- [Poller autonomy](feedback_poller_autonomy.md) — Leave working pollers alone.
- [Poller circular dependency](feedback_poller_circular_dependency.md) — Bridge protocol can't self-heal a broken poller. S291.
- [Codex poller not hung](feedback_codex_poller_not_hung.md) — codex exec buffers stdout; check stderr. S292.
- [Prioritization by dependencies](feedback_prioritization_by_dependencies.md) — Bridge correctness P0; everything else by dependency graph.
- [Session-start CronCreate poller](feedback_interactive_poller_monitor.md) — MANDATORY at session start. S292.
- [Post-impl report hygiene](feedback_postimpl_report_hygiene.md) — Class-qualified pytest IDs. S299.
- [Session-start ORIENT block](feedback_session_start_orient_block.md) — 7-item ORIENT block, fixed format.
- [Iterate fast on main](feedback_iterate_fast_on_main.md) — GT-KB pre-production; merge+push frequently.
- [Quality-first autonomy](feedback_quality_first_autonomy.md) — Default to max-quality option autonomously.
- [Don't re-elicit on agreement](feedback_dont_re_elicit_on_agreement.md) — Owner quoting recommendation = approval. S302.
- [AskUserQuestion for ALL decisions](feedback_use_askuserquestion_for_all_decisions.md) — Use AskUserQuestion for every owner decision. S302.
- [No deferrals ever](feedback_no_deferrals_ever.md) — Never defer; max quality+completeness always. S302.
- [Instrument before rule-making](feedback_instrument_before_rule_making.md) — Hypothesize → instrument → backlog → decide. S302.
- [Verify git diff before reporting](feedback_verify_git_diff_before_reporting.md) — Edit success ≠ committed. S302.
- [Read INDEX comments before GO execution](feedback_read_index_comments_before_executing_go.md) — Scan INDEX.md HTML comments. S302.
- [Bridge drift pattern](feedback_bridge_drift_pattern.md) — Surgical revert, not rewrite. S304.
- [No lossy compression of agent I/O](feedback_no_lossy_compression.md) — Quality > cost. S311.
- [MCP verification required](feedback_mcp_verification_required.md) — Verify MCP capabilities end-to-end before depending on them. S311.
- [Don't formalize implicit principles](feedback_dont_formalize_implicit_principles.md) — Ask before auto-DELIB. S312.
- [Verify source before parallel proposals](feedback_verify_source_before_parallel_proposals.md) — Each parallel bridge needs source-verification gate. S313.
- [Avoid quoting decision-tracker fragments](feedback_avoid_quoting_decision_tracker_fragments.md) — Quoting matched fragments re-fires the detector. S328.
- [Bare ? = status update](feedback_question_mark_means_status_update.md) — Single "?" = owner status request. S328.
- [Status updates probe live INDEX + sub-agent state](feedback_status_updates_load_index_and_subagent_state.md) — Multi-agent env moves between turns. S328.
- [GroundTruth-KB canonical project URLs](feedback_groundtruth_kb_canonical_project_urls.md) — "the GitHub", "repo", and related aliases resolve to the configured GT-KB GitHub URL, not local remote drift.
- [Run preflight before filing bridge proposals](feedback_preflight_before_filing_bridge_proposals.md) — Before drafting any bridge proposal, run `python scripts/bridge_applicability_preflight.py` against the intended bridge-id; cite cross-cutting governance specs of the artifact type, not just topic-specific specs. S331.
- [Project external resource registry](project_external_resource_registry.md) — Canonical URLs/identities for external resources and alias resolution.

## Strategic Thesis
- [Pipeline vision](project_vision_statement.md) — Software factory: owner delivers specs, pipeline produces deployable SaaS.
- [Pipeline is the product](project_strategic_thesis.md) — Agent Red validates the pipeline; groundtruth-kb is the core IP.
- [No attachment to implementations](feedback_no_attachment.md) — Adopt better alternatives without hesitation.
- [GT-KB non-disruptive upgrade priority](project_gtkb_non_disruptive_upgrade_priority.md) — CTO env upgrades non-disruptively. S298.
- [GT-KB Azure SaaS Readiness vision](project_gtkb_azure_saas_readiness_vision.md) — 15 deficiencies, 7 workstreams. S298.

## Plan-of-Record
- [Production Readiness v1.98.92](project_plan_of_record.md) — 16-step plan. Steps 1-13, 15 COMPLETE. Step 14 blocked on carrier. Step 16 PENDING.
- **Production OPERATIONAL** v1.98.92. 1 tenant: Remaker Digital. minReplicas=2 (currently hibernating per S314).
- **Step 14:** E2E phone OTP smoke, blocked on toll-free carrier (App 346df3eb).
- **Step 16:** Spec hygiene remediation: 118 untested specs + 10,440/11,066 orphan tests. Deferred until post-production.
- **WI-3156:** deploy.py scaling enforcement.
- **Bridge infrastructure (S295 permanent fix):** `.claude/hooks/`, `.claude/settings.json`, `.claude/rules/bridge-essential.md`, ps1/vbs scripts tracked via `!`-negation in `.gitignore`. Commit `94392a1b`.

## Standing Operating Decisions
- **2026-04-09 - Bridge ownership:** For bridge runtime/protocol/poller/worker/handshake work, Codex implements; Prime reviews.
- **2026-04-09 - Bridge protocol model:** Asynchronous message passing; not all messages require replies.
- **2026-04-09 - Bridge restart bias:** Don't restart healthy bridge for state cleanup; only for concrete reason.

## Recent Sessions
Detailed session content lives in git history (commits referenced) and `bridge/*-NNN.md`. Single-line hooks here. For deeper context use `git log --oneline --grep=S<NNN>` or read the cited bridge files.

- S352 addendum: **Governance-chain mechanical enforcement closed and project retired.** Recent bridge work now shows VERIFIED for WI-3316 (`gtkb-project-verified-completion-auq-trigger-008`), WI-3317 (`gtkb-impl-start-gate-format-spec-fix-008`), WI-3320 (`gtkb-bridge-compliance-audit-path-isolation-006`), the chromadb hook-latency thread, and the reliability fast-lane thread. Owner approved completion; `DELIB-S352-GOVERNANCE-CHAIN-PROJECT-COMPLETION` supports completing `PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN`, and `current_projects` now marks `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` retired. Live bridge count at wrap: `VERIFIED=160`, `NO-GO=63`, `GO=24`, `NEW=3`, `WITHDRAWN=27`, `ADVISORY=1`; LO queue has 3 NEW items, Prime queue has 87 GO/NO-GO items. Verification rerun: 25/25 project-completion tests, 47/47 implementation-start-gate + bridge-compliance tests, targeted ruff clean. Wrap evidence: `.groundtruth/session/snapshots/S352-20260515/`; DA harvest still blocked by `GOV-ARTIFACT-APPROVAL-001`.
- S352: **Bridge monitoring wrap with active parallel dispatch and large remaining queue.** Final live scan at `2026-05-14T20:49:11Z`: `VERIFIED=150`, `WITHDRAWN=24`, `GO=17`, `NO-GO=13`, `NEW=10`, `ADVISORY=1`; LO-actionable 10 latest NEW, Prime-actionable 30 latest GO/NO-GO. Concurrent Codex workers produced six observed NO-GO verdict files during wrap. Wrap scanners wrote `.groundtruth/session/snapshots/S352/` with hygiene 33 ERROR / 2482 WARN and consistency 2 ERROR / 1904 WARN. `session_prompts` insertion succeeded for S352 v1. DA harvest blocked by `GOV-ARTIFACT-APPROVAL-001`; commit/push skipped because `develop` is ahead 2 with a broad mixed dirty tree.
- S350: **Topology-misreport investigation + operating-mode-transaction proposal filed/REVISED-1 GO'd; Slice 4 implementation-gate-hygiene VERIFIED at -007 (parallel-session -006 superseded this session's -005, Codex verified -006).** Owner asked Prime to investigate the startup disclosure's `single_harness` topology report given two installed harnesses with singleton role sets. Root cause: `.claude/session/work-subject.json` stores `topology_mode` as canonical state; `scripts/session_self_initialization.py:4129` reads stored value rather than deriving from live role-map; 2026-05-13 role switch updated `role-assignments.json` but not `work-subject.json`. Discovered `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` (approved 2026-05-13) + open P1 orphan `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` already on the books. Filed `bridge/gtkb-operating-mode-transaction-001-001.md` (NEW), Codex `NO-GO` at `-002` (F1 hypothetical owner-waiver for deferred next-session-effectiveness; F2 test paths under `tests/**` violating `pyproject.toml:9 testpaths = ["platform_tests", "applications/Agent_Red/tests"]`); filed REVISED-1 at `-003` folding next-session-effectiveness into Slice 1 (new `groundtruth_kb.mode_switch.pending` module + SessionStart application + 6 new spec-derived tests) and relocating all test paths under `platform_tests/**`. Both preflights pass on `-003` (`preflight_passed: true`; 0 missing required; 0 blocking gaps). Picked up Slice 4 (`gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`) at the `-004` GO via owner AUQ; auth packet `sha256:1a45db13...`; audit revealed IP-1/IP-2/IP-3/IP-5 already landed by a parallel S349 Prime session (working-tree diff +209 lines in `scripts/implementation_authorization.py` + +97 lines in `.claude/hooks/assertion-check.py`, plus `config/governance/assertion-runs-retention.toml`, plus `WI-3295` inserted at 02:42:48Z by parallel session). Added one missing test `test_gate_unchanged_reads_current_json_only` to `platform_tests/scripts/test_implementation_start_gate.py`. **42/42 tests PASS.** Filed post-impl `-005` with full per-IP accounting + transparent parallel-session-coordination disclosure; both preflights pass. Wrap caveats: implementation-start gate fired false-positives on read-only `python -c "...SELECT..."` Bash three times (same friction class as S349 IP-3 follow-on candidates); INDEX has pre-existing defect `gtkb-single-harness-bridge-dispatcher-001.md` missing version suffix that surfaced via gate error; DA harvest/`session_prompts` writes not applied; many S349 parallel-session staged files remain uncommitted in working tree.
- S349: **Self-diagnostic leak-closure and backlog hygiene bridge cycle continued under active Prime/LO split; Codex LO cleared the live review queue during wrap.** Codex role resolved to Loyal Opposition (harness A), with Claude as Prime Builder (harness B). Bridge scans processed Slice 4 `gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`: NEW at `-001`, Codex NO-GO at `-002` because the proposed multi-active implementation authorization packet model changed the one-GO'd-proposal session-scope rule without updating the governing rule surface and did not define overlapping-target handling for shared paths such as `groundtruth.db`. During wrap, a fresh implementation report for `gtkb-backlog-hygiene-bundle-s349` appeared at `-015`; Codex verified it at `-016` after applicability and ADR/DCL clause preflights passed and live MemBase checks confirmed `WI-3282` through `WI-3293` latest `change_reason` values map to Findings 1-12 and cite `bridge/gtkb-backlog-hygiene-bundle-s349-013.md`. Final LO scan: no latest `NEW`/`REVISED`; latest counts 140 `VERIFIED`, 20 `GO`, 12 `NO-GO`, 1 `ADVISORY`. Wrap caveats: worktree remains dirty with many Prime-authored/staged S349 changes, scanner report writes and some read-only shell forms were blocked by the implementation-start gate after bridge status drifted, DA harvest/session_prompts writes were not applied, and git commit/push was skipped to avoid bundling unrelated active work.
- S348: **Session wrap knowledge collection upgraded, verified, and pushed.** Owner request to improve session-end knowledge collection produced bridge thread `gtkb-session-wrap-knowledge-collection`, completed through `VERIFIED` at `-004`. Commit `e946b349` pushed to `origin/develop`. The canonical wrap skill now centers a Knowledge Collection Matrix and explicitly accounts for MemBase, Deliberation Archive, `memory/MEMORY.md`, `bridge/INDEX.md`, `session_prompts`, verification evidence, wrap scanner output, ignored local evidence, formal-artifact blockers, and current-branch git sync. Handoff and audit reference templates are GT-KB-specific; Codex adapter/manifest/registry regenerated; `platform_tests/scripts/test_kb_session_wrap_skill.py` added. Verification: 4 wrap-skill tests passed, 10 adapter/parity tests passed, adapter check passed, bridge preflights passed. Wrap: branch clean at `e946b349`; live bridge latest statuses are 139 `VERIFIED`, 4 `GO`, 24 `WITHDRAWN`; assertion check remains broad red at 224/1687 PASS; wrap scanners exit 2 on known snapshot/non-manifest and missing old slice-D bridge-file classes; DA harvest dry-run only (609 would-create), no apply without formal approval evidence; `session_prompts` handoff inserted.
- S347: **Project-scoped implementation authorization implemented, corrected, verified, and pushed.** Owner-approved `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` was converted into governed specs, MemBase project authorization support, CLI lifecycle commands, implementation-start packet metadata validation, automatic backlog creation/linkage for implementation-bearing specs, deterministic project attachment, rule/skill/glossary updates, and formal approval packets. Bridge thread `gtkb-project-scoped-implementation-authorization` completed through `VERIFIED` at `-010`; Codex `NO-GO -006` found stale packet acceptance after current authorization scope narrowed, and the corrective `-007`/`-008` continuation fixed `load_packet()` to revalidate current exclusions against packet `spec_links`. Commit `36f6c2d8` pushed to `origin/develop`. Focused tests: 30 passed, 1 warning. Bridge applicability, ADR/DCL clause preflight, skill adapter check, and narrative-artifact evidence all passed. Wrap: assertion check remains broad red at 224/1687 PASS; deliberation harvest blocked by formal-artifact approval gate; wrap scanners exit 2 on known snapshot/report and missing old slice-D bridge-file classes; deployment skipped.
- S339: **Loyal Opposition bridge reviews continued; wrap stopped with one fresh REVISED open.** Startup loaded Loyal Opposition role. Codex processed `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md` and filed `NO-GO` at `-004` for two P1 blockers: boilerplate-heavy Jaccard correlation could still auto-resolve unrelated owner decisions, and DCL approval-packet recipe did not match `formal-artifact-approval-gate.py`. In parallel, Prime/bridge automation committed both REVISED-2 `-005` packets and an additional startup-symmetry `NO-GO -006` appeared during wrap-up. Final live queue: one latest `REVISED` remains (`owner-decision-tracker ... -005`); `startup-symmetry -006` and `bridge/INDEX.md` are uncommitted. Checks: assertion `1654/1687 PASS`, quality `91.1/100`; wrap scanners still fail on known historical snapshot/bridge hygiene plus current uncommitted state. No commit, push, deploy, KB mutation, or deliberation harvest was performed by Codex during wrap.
- S338: **Smart-poller token-cost regression mitigated; Slice 4 REVISED-7 filed; cross-harness active-session suppression mechanism implemented; DA Phase 3 hook F1+F2+F3 fixes filed.** Operational mitigation under owner AUQ "Mitigate now, then land Slice 4 (Recommended)": stopped PID 18616 (`bridge_poller_runner.py --interval 15 --quiet`, ~17.7h uptime, 20.5MB audit log) + disabled Windows scheduled task `GTKB-SmartBridgePoller`; verified zero new `PermissionError` in `dispatch-failures.jsonl` since the kill (was 69 historical from concurrent legacy + event-driven trigger contention on `dispatch-state.json.tmp`); lock released; dispatch-state continues updating contention-free via the cross-harness event-driven trigger alone. Slice 4 retirement REVISED-7 (`-015`): closed Codex `-014` F1 (`_BRIDGE_DISPATCH_DOC` retargeted from non-existent `bridge-event-driven-trigger.md` to existing `dual-agent-setup.md` + path-existence test) + F2 (test-rename allowlist alignment + explicit archive target `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`); both preflights clean; awaiting Codex `-016`. Cross-harness suppression GO at `-006` implemented per the GO'd proposal `-005`: new `scripts/active_session_heartbeat.py` (multi-mode session-start/tool-use/session-stop with REQUIRED `--state-dir` to make path coupling explicit at config time) + `scripts/cross_harness_bridge_trigger.py` state-machine refactor (split `last_dispatched_signature` + `last_suppressed_signature` preserving Slice 2 dedup invariant while enabling retry after counterpart exit; 120s sanity TTL matching owner-stated value; backward-compat fallback when reading pre-suppression state files) + 5 heartbeat hook steps registered on each harness side (Claude `.claude/settings.json` + Codex `.codex/hooks.json`) all using `--state-dir .gtkb-state/bridge-poller` matching the trigger; 30 tests pass (8 heartbeat + 14 suppression including F1-critical T-SUPPRESS-retry-after-counterpart-exits and F1-integration T-SUPPRESS-heartbeat-trigger-shared-lock-dir + 8 existing slice-3 hook validation); post-impl `-007` filed clean; awaiting Codex VERIFIED. DA Phase 3 glossary-expansion hook F1+F2+F3 fixes (`-009` REVISED post-impl after Codex `-008` NO-GO on parallel-Prime's `-007`): F1 token-budget contract repaired by computing wrapper overhead (~110 bytes for `<system-reminder>` + header) and subtracting from `TOKEN_BUDGET_BYTES` before fitting parts (final emitted body now bounded; reproduced Codex's exact case at budget=120); F2 deterministic priority repaired via `_tokenize_prompt` sort `(-len(p.split()), p)` producing "longer phrases first, alphabetical tiebreaker"; F3 ruff fixes (13 auto-resolved + 3 files reformatted); Codex parity hook mirrored byte-equivalent; 20 tests pass (was 18 + 2 new F1+F2 assertions); preflights clean; awaiting Codex VERIFIED. **Parallel-Prime pattern demonstrated mid-session and structurally fixed:** while drafting cross-harness REVISED-2, an auto-dispatched parallel Prime instance independently filed an equivalent (and slightly stronger F1) `-005`, Codex reviewed it, returned GO at `-006`; same pattern observed for DA Phase 3 with parallel Prime filing `-007` and Codex returning NO-GO at `-008` mid-session. The cross-harness suppression mechanism that's now active in hook configs is exactly the structural fix; from the next session the heartbeat lock prevents this duplicate-dispatch pattern. Quality 91.1/100; assertions 1654/1687 PASS with 33 pre-existing documentation/SPA spec FAILs (none S338-introduced). Wrap-scan exit-2 with all 14 W1 ERRORs (`snapshots_non_manifest`, scanner-self-recursion + leftover prior-session reports) and 2 W2 ERRORs (INDEX cites missing `gtkb-isolation-018-slice-d-non-functional-content-{001,002}.md`) pre-existing repo state, none S338-attributable. Phase 1.5 deliberation harvest deferred (formal-artifact-approval-gate blocked the harvest script as a deliberations-table mutation; same precedent as S333/S334/S335/S337; harvest is idempotent and safe to rerun). Pre-existing breakage noted (out-of-scope): `tests/scripts/test_cross_harness_bridge_trigger.py::test_signature_uses_selected_batch_not_full_list_with_max_items_2` imports `groundtruth-kb/scripts/bridge_poller_runner.py` which the parallel Slice 4 D1 archive has already removed; deselected via `--deselect` for the session's test sweep; Codex's Slice 4 `-016` verdict can decide whether to archive that test alongside the runtime or update it.
- S337: **canonical_terms backing registry seeded on production DB + doctor empty-table severity elevated.** Bridge `gtkb-canonical-terms-production-seed-and-doctor-elevation` 6-version cycle: -001 NEW → -002 GO → -003 NEW (impl report) → -004 NO-GO (worktree-vs-production-tree visibility split: edits made in worktree at `.claude/worktrees/zealous-ardinghelli-8da94a` were invisible to Codex's verification commands run from `E:\GT-KB`) → -005 REVISED (patch mirrored into production tree) → -006 VERIFIED. Defect statement: Phase 1 of `gtkb-canonical-terminology-system-context-model-001` (-008 VERIFIED) shipped the canonical_terms schema and CLI but the live seed claimed in the report was actually against a scratch DB; live S337 probe found `current_canonical_terms` empty in production `groundtruth.db`. Doctor's empty-table early-return classified the gap as `status="pass"`, masking the regression. Production DB now holds 27 active platform_core canonical terms at version=1 (idempotent re-apply confirmed `unchanged=27`); `_check_canonical_terms_registry()` empty-table early-return flipped to `status="warning"` with schema/seed-drift message; pre-existing `test_pass_when_table_empty` renamed `test_warning_when_table_empty_with_glossary` and assertion flipped to pin the fix. Commit `7855efeb` on develop, 8 files +927/-7, secret scan + inventory-drift hooks passed. Wrap-scan emitted 14 pre-existing structural ERRORs (12 snapshots_non_manifest from prior session wrap dirs; 2 INDEX cites of missing `gtkb-isolation-018-slice-d-non-functional-content-{001,002}.md`); none S337-attributable; owner override granted via AUQ. Quality 91.2/100; assertion check 1654/1688 PASS with 34 pre-existing documentation FAILs (no S337 regressions). Phase 1.5 deliberation harvest deferred (formal-artifact-approval-gate blocked the harvest script path; same precedent as S333/S334; harvest is idempotent and safe to rerun). Discovery for backlog: bridge protocol implicitly assumes a single working tree; future worktree-based Prime sessions should either mirror code patches into the production tree at evidence-capture time, or commit on the worktree branch and explicitly ask Codex to verify against that branch.
- S335: **S327 release-path freeze + release-path framing fully lifted via DELIB-S332.** Owner directive 2026-05-07: "remove all FREEZE or HOLD or DEFER states from all plans and work items. They are all stale." AUQ #1 scope `A + B + C + H`. AUQ #2 approve+extend `Approve, but also lift S327 release-path goal entirely`. Bridge `gtkb-lift-feature-freeze` cycle: NEW → 4 NO-GO/REVISED rounds (-002 brittle CLI/semantic-search → -003; -004 padding/case bugs/missing baseline/status_detail-reintroduces-freeze → -005 with one in-place self-fix; -006 Bash-only commands/missing approval-gate binding → -007) → GO at -008 → 2 self-detected mid-impl defects (Step 3 `fields=` kwarg no-op + U4 baseline overreach, both caught by tests) → post-impl -009 → NO-GO -010 (criterion 7 pending + count inconsistency) → REVISED -011 → VERIFIED at -012. Implementation: `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` v1 inserted with `GTKB_FORMAL_APPROVAL_PACKET` env binding; `memory/work_list.md` 4 sections rewritten (S327 RELEASE PATH header, freeze paragraph, Default idle work directive replaced with per-leverage priority bands, "Deferred during release path" section deleted, GTKB-GOV-007 PAUSED tag lifted); 7 target WIs updated to v3 with current-state-only `status_detail` (no freeze/defer/hold/paused/parked vocabulary); 7 no-op v2 versions remain in append-only history; all 12 acceptance + unchanged-surface tests PASS; criterion 7 pytest sanity-check WAIVED (pre-existing fallout from `687f4707` 18.C inventory move; follow-on WI candidate `GTKB-FIX-DEV-ENV-INVENTORY-DRIFT-TEST-FIXTURE`). Preserved: `DELIB-S330` canonical Agent Red migration prerequisite, P0 secrets-purge override, in-flight Slice 8.5/8.6 work — rc1 tag still NOT authorized. **Session-numbering disclosure:** all bridge artifacts and the inserted DELIB use "S332" in their content/IDs (the DELIB ID is `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` and `session_id=S332` field). This was a Prime-side numbering error; the actual session is S335 (next after S334). Artifact names + IDs are kept as filed; this entry is the authoritative MEMORY.md record. Pre-impl session work: prioritization analysis surfacing top acceleration items (Backlog DB Slices 2-7, `GTKB-ARTIFACT-RECORDER-CLI`, `GTKB-OPS-CURRENT-STATE-MONITORING-001`, pre-filing preflight hook/rule revisions, Term Primer + Disambiguation Slices 2-5). Quality 91.2/100. Assertion check: 1654/1688 PASS, 34 pre-existing FAIL (all documentation specs from prior sessions; no S335 regressions).
- S334: **Develop resync via owner-approved reset + S334 plan items 1-4 closed + Slice 1 framework live.** Discovered local develop was on the pre-S307-filter-repo lineage and still carried the Azure OpenAI key in `scripts/agent-container-template.yaml` working-tree (inherited from pre-rewrite baseline; no S334-or-later commit ever touched the file). Owner-approved AUQ path A: `git reset --hard claude/s333-audit-remediation` (run by owner; destructive-gate hook hard-blocked agent-side execution as designed). Today's work replayed on realigned baseline. AUQ-committed plan: (1) `gtkb-codex-backlog-cleanup-retroactive-review` Phase 1 implemented under GO at -004 (read-only inventory + review-packet generators + 6/6 tests; 119 work-items / 12 transitions / 54 consequential flags; VERIFIED at -006); (2) `gtkb-codex-bridge-compliance-gate-parity` REVISED-2 NO-GO at -006 → REVISED-3 at -007 added Change 7 parity-checker enforcement with SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1 named test → GO at -008; (3) NEW `gtkb-adr-dcl-clause-test-enforcement-001` (Slice 1 of GTKB-ADR-DCL-CLAUSE-TEST-ENFORCEMENT-001) → GO at -002 → implemented (5-fixture clause registry TOML + advisory-mode `scripts/adr_dcl_clause_preflight.py` CLI + 6/6 tests + `.claude/rules/file-bridge-protocol.md` advisory section) → VERIFIED at -004; (4) develop pushed FF (commits `fef42fe1` + `84e15a8c`). Azure OpenAI key rotation confirmed via sha256-prefix comparison (different fingerprints; both 84-char Azure format). Wrap-scan emitted 12 pre-existing structural ERRORs (10 recursive snapshot-rule violations + 2 INDEX cites of missing slice-d-non-functional-content files); none S334-introduced; owner explicit override granted to wrap. Quality 91.2/100. Deliberation harvest: skipped (formal-artifact-approval-gate blocked; same precedent as S333 where dry-run scoped to 949 broad records). Self-validation: running the new clause-preflight CLI against the freshly-VERIFIED Phase-1 report shows 5 must_apply / 0 evidence gaps — the framework's first real-world dogfood passes.
- S333: **Codex Loyal Opposition bridge queue cleared and governance batch committed.** Codex switched to Loyal Opposition, processed 7 live bridge items, and committed all staged work as `721f7c69 chore: record GT-KB governance bridge updates` after regenerating the dev-environment inventory baseline. Verdicts filed: `gtkb-claude-session-start-parity-002` GO; `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan-006` VERIFIED; `gtkb-auq-policy-gates-001-010` VERIFIED; `gtkb-pre-filing-preflight-rule-004` NO-GO; `gtkb-pre-filing-preflight-hook-006` NO-GO; `gtkb-env-inventory-drift-control-001-006` NO-GO; `gtkb-harness-parity-baseline-002` NO-GO. Wrap checks: assertion check `1687/1688 PASS` with expected `DCL-STANDING-BACKLOG-DB-SCHEMA-001` failure; harness parity PASS; inventory drift PASS clean; harvester dry-run broad at 949 would-create, not applied. Final live bridge scan: no LO-actionable `NEW`/`REVISED` entries.
- S331: ISOLATION-018 scoping unblocked. Pending-migration waiver bridge thread completed full cycle (NO-GO → REVISED → GO → owner-approved DELIB body via AskUserQuestion → packet → MemBase insert v1 → 7 tests PASS → REPORT VERIFIED). DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER v1 ACTIVE; in-flight Agent Red root-file work now covered by cited exception. Umbrella scoping bridge: NEW → NO-GO -002 (F1+F2+F3) → REVISED -003 → NO-GO -004 (F1: 18.B inconsistency) → REVISED -005 → GO -006. 12 sub-slices 18.A through 18.L confirmed for actual file migration. Process retrospective: "all three" corrective for the cross-cutting-spec citation gap — feedback memory `memory/feedback_preflight_before_filing_bridge_proposals.md`, rule update bridge GO'd at `bridge/gtkb-pre-filing-preflight-rule-002.md`, hook upgrade bridge NO-GO at `bridge/gtkb-pre-filing-preflight-hook-002.md` (F1 high-severity: preflight script needs content-aware mode for pending Write content). 0 commits this session (working tree carries all changes; commit-and-push deferred to next session).
- S330: Slice 8.6 CI-failure triage Phase 1+2 (43 rows). CI seed script + fixture + workflow step + groundtruth-kb pin fix + 5 rehearse skips + row-36/37/38 loosened + relative-parts SKIP_DIRS fix + pip<26 pin + Docker Scout 2-CVE SARIF waiver. See `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-*.md`.
- S329: ISOLATION-017 Slices 5/6/7 VERIFIED + 2 NO-GO bridges closed via supersession + Slice 8 REVISED-1 awaiting Codex. ~30 commits. See `bridge/gtkb-isolation-017-slice{5,6,7}-*-2026-05-03-*.md`.
- S328: ISOLATION-017 Slice 4 VERIFIED + Slice 5 GO + wrap-prep. 0 commits. Slice 4: 12-version cycle / 4 NO-GO/REVISED rounds. work_list rows 28-31. Stop-hook disabled via `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`.
- S327: 3 governance Slice 1s landed (Backlog DB / Term Primer / Term Disambiguation). Wrap commit `c73001b8`.
- S326: ISOLATION-017 Slices 1, 2, 2.5 VERIFIED. 16 commits. 8 Codex NO-GOs each catching real defects. New feedback: probe-live-state-before-quoting-counts. Slice 3 inherits 22-file deferred-registration obligation.
- S325: pre-S326 (see git history).
- S324: Priority elevation + dashboard-link cascade closed. ~50 commits. ISOLATION-016/017/018/019 sequence elevated.
- S323: pre-S324.
- S322: Triage + mojibake VERIFIED + Slice A spec-event-surfacer implemented (post-impl NO-GO concurrency). ~45 commits. AskUserQuestion adopted as primary primitive.
- S321: Governance foundation + hard-block hook LIVE + 25 KB specs + DA-backed. ~80 commits. Bridge-compliance-gate hook hard-blocks non-compliant Write/Edit.
- S320: Smart-poller activation + Phase 1 isolation TERMINALLY CLOSED. ~40 commits. Smart-poller VERIFIED at -012 (4 NO-GO/REVISED cycles).
- S319: Drift triage + DORA-001b Track 1. 11 commits. 3 bridge threads VERIFIED. Working tree fully clean.
- S318: Generator-hardening triad terminally closed. 19 commits. 5 threads VERIFIED. Lane achieves status:ok + violations:0.
- S317: Massive parallelization-driven cleanup. ~27 commits. 8 threads VERIFIED. ~80 carryover untracked files migrated into git. Telemetry-churn-policy.
- S316: 3 deletion-readiness manifests VERIFIED + application-isolation contract foundation (sub-slice 1 VERIFIED). E:\Claude-Playground archived. Lesson: explicit-destructive-action-authorization saved.
- S315: CRITICAL ROOT-ISOLATION REMEDIATION. `.claude/rules/project-root-boundary.md` filed. 104/104 auto-memory files migrated to `E:\GT-KB\memory\`. ~26 commits.
- S314: Wave 2 closure (10/11 VERIFIED + 1 NO-GO awaiting revision) + Agent Red 5-day hibernation executed. ~9 commits.
- S313: Wave 2 dense bridge cycle: 8 of 11 lanes shipped + 3 fix bridges VERIFIED. ~25 commits.
- S312: Wave 2 Stage B split-pattern cluster complete. Slices 4-5-6 VERIFIED. 2 new DELIBs (role-contract effectiveness + deterministic services principle). ~25 commits.
- S311: KB recovery (Drive-induced corruption) + Wave 2 foundation FULLY VERIFIED. `.driveignore` permanent fix. 2 new feedback memories. ~19 commits.
- S310: 5 threads VERIFIED. ADR-ISOLATION-APPLICATION-PLACEMENT-001. ~25 commits across develop + groundtruth-kb upstream.
- S309: 4 threads VERIFIED. GTKB-STARTUP-ENHANCEMENTS filed. P1 landed at `3caa034d`. 14 commits.
- S308: Bridge-poller halt directive. Filed three S309-carryover NO-GOs.
- S307: Worktree drift incident. No-hardcoded-paths + pedagogical-comments directives saved.
- S305-S306: ISOLATION Phase 3-7 baselines VERIFIED + Phase 8/9 plans VERIFIED. 4 new bridge threads + backlog hygiene. PROPOSAL-STANDARDS, DA-ENFORCEMENT, BACKLOG-DISCIPLINE programs scoped.
- S303-S304: Bridge restored. D3 azure-iac-skeleton VERIFIED. D4 azure-cicd-gates REVISED-2.
- S298-S300: v0.6.0 + v0.6.1 to PyPI. Tier A Phase A complete. Non-disruptive upgrade primitive.
- S294-S297: 4B mypy/coverage/docstrings to 39→0 / 70% / 85%. v0.5.0 Developer Preview.
- S288-S293: Phase 4 Spec Pipeline COMPLETE (8 features VERIFIED, 600 tests). Codex poller incident.
- S280-S287: Multiple PyPI releases, GT-KB docs Phases 0-8, deliberation archive C1-C6.
- S270-S279: v1.98.91-92 production deploy. ACS SMS. SonarCloud activation.
- S259-S269: ADR-004 canonical identity + bridge v3 + production incidents + P0 encryption incident. See `CLAUDE_ARCHIVE.md`.
- S258 and earlier: see `CLAUDE_ARCHIVE.md`.

## Protected Files (DO NOT MODIFY)
- `branding/logo/SVG/icon-master.svg`, `branding/logo/SVG/primary-logo-no-wordmark.svg`
- `branding/logo/PNG/icon-master.png`, `branding/logo/PNG/primary-logo-no-wordmark.png`

## Quick Reference
- **GroundTruth-KB GitHub URL:** https://github.com/Remaker-Digital/groundtruth-kb. Conversational aliases "the GitHub", "repo", "the repo", and "GitHub repo" resolve here unless explicitly scoped otherwise.
- **Resource aliases config:** `.claude/rules/project-resource-aliases.toml`; readable index `memory/project_external_resource_registry.md`.
- **Azure:** Subscription 4dce2122, ACR acragentredeastus.azurecr.io, Cosmos cosmos-agentred-eastus, KV kv-agentred-eastus, Redis redis-agentred-eastus (C1, TLS).
- **API Gateway:** agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
- **Docs site:** https://agentredcx.com (GHA from main). **Storefront:** https://blanco-9939.myshopify.com/
- **Brand color:** #ff3621. **Email:** Titan SMTP primary, ACS fallback.
- **Knowledge DB:** `groundtruth.db` at repo root (gitignored) — SQLite, web UI localhost:8090, Python API `tools/knowledge-db/db.py`.
- **GroundTruth KB:** in-repo `groundtruth-kb/` (editable install via `requirements-test.txt`). PyPI `v0.6.1` no longer used in CI.
- **Scripts:** `seed_tenant.py` (9-phase), `upgrade_verification.py` (35 assertions), `test_pipeline.py` (13 phases, canonical E2E runner), `membase_ci_seed.py` (CI fixture seed S330).
- **Admin SPAs:** standalone (port 3300), shopify, provider (port 3400). All have `dev:mock` mode.
- **SPEC-1673:** Provider MUST NOT hold raw tenant API keys.

## Memory Files
- [project_backlog018_plan.md](project_backlog018_plan.md) — BACKLOG-018 plan (6 phases, 55 specs). DEFAULT work priority.
- [feedback_codex_bridge_protocol.md](feedback_codex_bridge_protocol.md) — Codex role, $20/mo budget, prime-bridge notification discipline.
- [testing-research.md](testing-research.md) — S210 research; AI-generated code testing; 4-phase guardrail plan.
- [feedback_artifact_boundaries.md](feedback_artifact_boundaries.md) — KB for project artifacts; MEMORY.md for operational patterns. S218.
- [feedback_docs_release_gated.md](feedback_docs_release_gated.md) — Public docs release-gated with same rigor as code. S218.
- [feedback_deploy_gate_token.md](feedback_deploy_gate_token.md) — Production deploy gate = env token. S218.
- [project_architecture_specs.md](project_architecture_specs.md) — Lightweight architecture spec tagging (GOV-21 pending). S219.
- [feedback_taxonomy_simplicity.md](feedback_taxonomy_simplicity.md) — Collapse `architecture` type into ADR/DCL.
- [feedback_bridge_protocol.md](feedback_bridge_protocol.md) — Near-real-time autonomous bridge exchange. 60s ack. S223.
- [project_groundtruth_lineage.md](project_groundtruth_lineage.md) — GroundTruth = evolution of membase-4-claude. S237.
- [canonical_vocabulary.md](canonical_vocabulary.md) — Interim definitions for MemBase/DA/MEMORY.md/GT-KB/Prime/LO. S299.
- [project_s299_governance_lessons.md](project_s299_governance_lessons.md) — S299: 3 gaps; 5 owner decisions pending S300.
- [project_cto_trial_onboarding_docs.md](project_cto_trial_onboarding_docs.md) — Weekend CTO deadline; scope bridge GO'd.
- [feedback_canonical_terminology_governance.md](feedback_canonical_terminology_governance.md) — Pre-proposal DA search MANDATORY. S299.
- [feedback_agent_red_is_adopter_not_author.md](feedback_agent_red_is_adopter_not_author.md) — Historical note from S299; superseded by owner correction 2026-05-04: Agent Red is a separate project, not part of GT-KB.
- [feedback_complexity_fragility.md](feedback_complexity_fragility.md) — Evaluate every proposal element for coupling/testability/maintenance. S253.
- [project_widget_roadmap_decisions.md](project_widget_roadmap_decisions.md) — 4 owner decisions for widget roadmap. S253.
- [feedback_collaboration_protocol.md](feedback_collaboration_protocol.md) — MANDATORY dev lifecycle. S254.
- [feedback_environment_safety.md](feedback_environment_safety.md) — Never modify production without explicit confirmation. S254.
- [feedback_owner_questions.md](feedback_owner_questions.md) — Owner questions are reasoning tests. S256.
- [feedback_build_process.md](feedback_build_process.md) — All builds via GitHub Actions only. S254.
- [project_control_surface_closeout.md](project_control_surface_closeout.md) — 5-phase plan. S253-S254.
- [feedback_tests_before_implementation.md](feedback_tests_before_implementation.md) — Tests MUST be written BEFORE implementation code. S255.

## References
- [Sarah Scenario (GT-KB UX Anchor)](reference_sarah_scenario.md) — 7-phase user journey (DOC-SARAH-SCENARIO).
- [UI Testing Tool Evaluation](reference_ui_testing_tools.md) — Chromatic + axe-core first.
- [Codex automation failure](project_codex_automation_failure.md) — Desktop automations silently fail.

## Project Knowledge (in Knowledge Database)
- **Cross-cutting lessons (85+):** `DOC-cross-cutting-lessons` — Python, API, Cosmos, build, testing, frontend, infra patterns.
- **Owner preferences (6):** `DOC-owner-preferences` — quality, process, product directives.
- **Shopify production deployment guide:** `DOC-141`.
- **Docs site deployment:** KB procedure `docs-site-deploy`.
- **Roadmap planning wiki:** `wiki/Roadmap-planning.md` — P1 COMPLETE. P2-P7 pending.
- **Protected behaviors:** PB-* specs in KB — machine-verifiable assertions checked at session start.
- [Production deploy approval](feedback_production_deploy_approval.md) — Require explicit "deploy to production" confirmation.
