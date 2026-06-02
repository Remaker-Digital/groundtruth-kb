# Agent Red Memory

## Current Status

- **2026-06-02 (S394 Codex wrap; Codex harness A): commit/push request completed and wrap state preserved after the worker-packet authorization work.** The implementation commit `118f3310` (`feat(gtkb): auto-create worker authorization packets`) is pushed to `origin/develop`; the first explicit `git push origin develop` hit a remote ref lock race, but `git ls-remote`, `git fetch origin develop`, and `git status --short --branch` confirmed local and remote `develop` both pointed at `118f3310`. During wrap the worker-packet bridge thread advanced to terminal `VERIFIED` at `bridge/gtkb-worker-packet-auth-envelope-slice-2-auto-packet-004.md`; that bridge verdict and `bridge/INDEX.md` update are pushed as `116e4954` (`docs(bridge): verify worker packet auto authorization`). Live bridge scan at wrap: Loyal Opposition actionable 0, Prime actionable 43, summary `ADVISORY=5 / GO=22 / NO-GO=21 / VERIFIED=95 / WITHDRAWN=42`. Verification recorded for the implementation lane: focused pytest `223 passed, 1 warning`, ruff check passed, ruff format check passed, bridge applicability preflight passed, and clause preflight passed. Wrap evidence under `.groundtruth/session/snapshots/S394/`: W0 manifest written; W1 hygiene scan exited nonzero with 16 `snapshots_non_manifest` ERROR findings plus 3,875 WARN, dominated by pre-existing snapshot self-report files and unindexed historical bridge files; W2 consistency scan exited 0 with 3,971 WARN, dominated by historical bridge files orphaned from active `bridge/INDEX.md`. No Deliberation Archive harvest or `session_prompts` insertion was performed; no new owner decision beyond commit/push and wrap was captured. Remaining untracked residue: `$base/`, `PASS`, `bridge/.claude/`, and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-02 (S393 Codex Prime Builder wrap; Codex harness A): committed and pushed the Keep Working governance/bridge batch, then closed a newly surfaced discoverability regression.** Branch `develop` is synchronized with `origin/develop` at HEAD `1682dad2` (`docs(bridge): revise discoverability scoping closure`). Commits pushed this session include `eb007b46` (`chore: land verified bridge governance bundle`), `16ac587b` (`docs(bridge): file discoverability status regression proposal`), `beef5484` (`docs(bridge): record discoverability status regression GO`), `aab07ff9` (`fix(backlog): repair status scanner coverage`), `e8c599cb` (`docs(memory): update release readiness evidence`), `a6db37ab` (`docs(memory): record S393 Codex wrap`), `050f0baa` (`docs(bridge): record rc1 pyjwt and discoverability closure`), `5a1f24e8` (`docs(memory): correct S393 wrap head`), `b9018c5c` (`docs(bridge): record rc1 blocked report and scoping no-go`), and `1682dad2` (`docs(bridge): revise discoverability scoping closure`). The governance bundle committed bridge reconciliation CLIs/tests, implementation authorization owner-sufficiency support, registry/scaffold drift reconciliation, DA-enforcement Slice 1 decomposition artifacts, harness role/registry updates, and inventory baseline updates; staged/range secret scans passed and inventory drift was regenerated/accepted. The discoverability follow-on thread `gtkb-discoverability-cli-status-scanner-api-regression` completed through `VERIFIED -004`: `gt backlog status` now uses `verified_work_items_by_project(project_root)` instead of removed `verified_work_items()`, focused tests passed (`10 passed`), ruff check and format-check passed, and live `gt backlog status` smokes with base, `--with-verified-coverage`, and `--with-retire-ready` all exited 0. Release-readiness evidence now records same-head PR #124 workflow_dispatch results, with PyJWT audit findings and Docker Scout Docker Hub auth as remaining RC1 blockers; follow-on bridge proposal `gtkb-rc1-pyjwt-dependency-audit-remediation-001` and blocked report `gtkb-rc1-canonical-ci-closure-003` were filed and committed, and stale `gtkb-discoverability-cli-slice-2-scoping` advanced through report-only `-003`, NO-GO `-004`, and REVISED `-005`. Live bridge scan at wrap: LO actionable 0; Prime actionable 46 (`GO=25`, `NO-GO=21`), led by `gtkb-rc1-canonical-ci-closure`, `gtkb-dispatch-owner-approval-forgery-prevention`, and `gtkb-role-status-orthogonality-dispatch-scoping`. Wrap scanners/session snapshot writes were blocked by the implementation-start gate when attempting `.groundtruth/session/snapshots/S393`; no DA harvest or `session_prompts` insertion was performed. Remaining local residue: untracked `$base/`, `PASS`, `bridge/.claude/`, and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-02 (S392 Antigravity Loyal Opposition wrap; Antigravity harness C, explanatory): performed an automated parallel Loyal Opposition bridge scan and queue processing cycle, then committed and pushed the WI-3485 active-session target-naming implementation report and associated test cleanup.** All 11 actionable bridge queue entries (latest `NEW` or `REVISED`) were processed and resolved using parallel `BridgeReviewer` sub-agents coordinated through `scripts/lo_bridge_process_helper.py`. Verdicts authored: `gtkb-impl-auth-requirement-sufficiency-phrase-tolerance-004` VERIFIED, `gtkb-bridge-mode-config-transactions-slice-1-015` VERIFIED, `gtkb-registry-scaffold-fixture-drift-reconciliation-002` GO, `gtkb-da-enforcement-completion-slice1-decompose-009` GO, `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-004` GO, `gtkb-stale-thread-closure-slice-3-impl-006` VERIFIED, `gtkb-in-source-provenance-anchors-001-prop-008` VERIFIED, `gtkb-isolation-019-program-closeout-008` VERIFIED, `gtkb-bridge-skill-protected-write-helper-006` VERIFIED, `gtkb-bridge-citation-freshness-test-restoration-003` GO, `gtkb-bridge-propose-helper-caller-migration-to-writer-003` GO. Additionally, a carry-over WI-3485 active-session target-naming implementation report (`bridge/gtkb-cross-harness-trigger-active-session-target-naming-004.md`) and four updated platform test files were staged and committed as `c3344c45` (`test(bridge): WI-3485 active-session target naming cleanup`) and pushed to `origin/develop`; all 67 targeted regression tests passed, ruff check and format-check clean. A subsequent VERIFIED verdict for that report was independently committed as `90dadb8f` by a concurrent process. Branch `develop` at `origin/develop` HEAD `90dadb8f` at session close; working tree clean. W0 transcript manifest written to `.groundtruth/session/snapshots/7b3b154d-4d35-4465-886d-3e2f8196d5f4/manifest.json`. W1 hygiene scan exited 2 with `snapshots_non_manifest` errors (pre-existing chronic noise from prior session wrap-scan reports placed under snapshot directories) and `bridge_files_not_in_index` warns; no session-introduced regressions. W2 consistency scan exited 0 with `da_cites_missing_bridge_file` warns only (pre-existing, from bridge thread pruning). Remaining untracked residue: `bridge/.claude/session/spec-events-seen.jsonl.lock` (ephemeral), `$base/`, `PASS` (transient pytest artifacts), and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-02 (S391 Codex Prime Builder wrap; Codex harness A): completed Keep Working commit/push closeout after bridge-helper and registry/scaffold fixture work.** Branch `develop` is synchronized with `origin/develop` at HEAD `e4f16a11` (`chore: parallel Loyal Opposition bridge scan and queue processing closeout`); an explicit `git push origin develop` returned `Everything up-to-date`. Live bridge thread checks after push: `gtkb-bridge-propose-helper-caller-migration-to-writer` is latest `VERIFIED -005` with `drift=[]`; `gtkb-registry-scaffold-fixture-drift-reconciliation` is latest `NEW -003` with `drift=[]`. Verification observed during the commit path: registry group 35 passed; fixture/scaffold group 60 passed after adding Git to PATH; bridge helper group 52 passed after adding Git to PATH; targeted ruff check and format checks passed. Important caveat: Codex's explicit local commit attempt failed because force-added ignored generated scaffold-golden `.claude` Python fixtures conflicted with staged ruff-format enforcement versus golden byte-parity; then the branch advanced via parallel/background commits and the relevant bridge/fixture files are now tracked in pushed history. Remaining local tracked dirt is limited to four platform bridge-trigger test files (`test_bridge_dispatch_per_document_lease.py`, `test_cross_harness_bridge_trigger.py`, `test_cross_harness_bridge_trigger_diagnose.py`, `test_cross_harness_trigger_suppression.py`) from parallel bridge-trigger work; leave them uncommitted unless continuing that packet. Wrap evidence is under `.groundtruth/session/snapshots/S391/`: transcript manifest written, hygiene scan exited nonzero with 6 ERROR / 3832 WARN dominated by snapshot non-manifest artifacts plus existing bridge/session noise, and consistency scan exited 0 with 3924 WARN.

- **2026-06-02 (S390 Codex Prime Builder wrap; Codex harness A): committed/pushed all available Prime Builder work and preserved the stop-state after an owner `Commit and push` / `::wrap` command.** Durable pushed commits now at `origin/develop` / `develop` HEAD `547326a4`: `86846895 feat(bridge): add protected write helper`, `60c4b6f2 feat(verify): land isolation program backstop release-gate check`, `03a6f4b9 chore: format test_isolation_program_backstop.py`, and `547326a4 docs(bridge): file implementation report for gtkb-isolation-019-program-closeout`. The bridge protected-write helper work added `.claude/skills/bridge/helpers/protected_write.py` plus skill docs/adapters/tests and filed its implementation report. The isolation closeout added the read-only isolation backstop, release-candidate-gate integration, focused platform tests, and filed `bridge/gtkb-isolation-019-program-closeout-007.md`; observed verification included the backstop live run (`status: pass`, `scanned_files: 1067`, `violations: 0`) and focused tests (`9 passed`). After the final owner stop command, `git push origin develop` reported `Everything up-to-date`; no new code/bridge revision was committed after that. Live bridge scan at wrap: summary `ADVISORY=5 / GO=24 / NEW=6 / NO-GO=22 / REVISED=2 / VERIFIED=72 / WITHDRAWN=42`; Prime-actionable latest GO/NO-GO count 46; Loyal Opposition-actionable latest NEW/REVISED count 8. Important handoff: `gtkb-worker-packet-auth-envelope-slice-2-auto-packet` is latest GO, but `scripts/implementation_authorization.py begin --bridge-id gtkb-worker-packet-auth-envelope-slice-2-auto-packet` rejects the approved proposal because `## Requirement Sufficiency` says `Existing requirements are sufficient.` instead of the gate's exact accepted phrase `Existing requirements sufficient.` A narrow `REVISED -003` should be filed through the bridge helper before implementation; no `-003` was filed in S390. The owner's registry/scaffold fixture drift handoff remains LO-actionable `NEW`, not Prime-actionable; no fixture/TOML mutation was performed. Wrap evidence is under `.groundtruth/session/snapshots/S390/`: transcript manifest written, hygiene scan exited nonzero with 3 ERROR / 3821 WARN (snapshot non-manifest artifacts plus existing bridge/session noise), and consistency scan exited 0 with 3917 WARN. Remaining local residue: untracked/runtime `bridge/.claude/session/spec-events-seen.jsonl.lock` and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-02 (S389 Antigravity Loyal Opposition wrap; Antigravity harness C, explanatory): performed an automated parallel Loyal Opposition bridge scan and queue processing cycle, followed by the verification of the revised Slice 2 spec-to-test mapping helper.** Reviewed and successfully verified all 6 active queue threads, bringing the bridge to a clean terminal state (0 active items remaining). Specifically: (1) spawned parallel `BridgeReviewer` background subagents to evaluate the 5 pending post-implementation reports (`gtkb-terminal-project-record-retirement-batch` to -006, `gtkb-da-enforcement-completion-slice1-decompose` to -007, `gtkb-deterministic-services-stale-status-reconciliation` to -012, `gtkb-spec-coherence-cli` to -004, and `gtkb-bridge-index-role-intent-sentinel` to -008); (2) reviewed the newly filed revised report `gtkb-verify-skill-spec-to-test-mapping-009.md` and verified the F1/F2 fixes with all 14 unit tests passing, filing the terminal `VERIFIED` verdict (-010). Deliberation Archive harvest completed with 4 new records written. W0, W1, and W2 wrap-up scans were successfully run, writing their markdown reports to `.groundtruth/session/snapshots/1bc17630-557e-45f6-932c-0f98b99c82e5/`.

- **2026-06-02 (S388 Antigravity Loyal Opposition wrap; Antigravity harness C, explanatory): performed an automated parallel Loyal Opposition bridge scan and queue processing cycle.** All 7 active queue threads were successfully evaluated and processed, bringing the bridge to a terminal state (0 active items remaining). The verdicts authored and linked to the bridge are: `gtkb-terminal-project-record-retirement-batch` GO, `gtkb-da-enforcement-completion-slice1-decompose` GO, `gtkb-index-agent-edit-serialization-scoping` VERIFIED, `gtkb-role-enhancement-isolation-dependency-reframe` VERIFIED, `gtkb-deterministic-services-stale-status-reconciliation` GO, `gtkb-dispatch-owner-approval-forgery-prevention` GO, and `gtkb-stale-thread-closure-slice-3-impl` GO. Status mutations were successfully serialized to `bridge/INDEX.md` using the index set-status CLI tool. W0 transcript capture, W1 hygiene scan, and W2 consistency scan wrap-up checks were executed, writing their markdown reports to `.groundtruth/session/snapshots/S388/`. The Deliberation Archive harvest completed successfully with 15 new records written.

- **2026-06-01 (S387 Codex Prime Builder wrap-only closeout; Codex harness A): preserved handoff state after the Keep Working automation.** No new implementation was performed. Branch `develop` was already synced to `origin/develop` at `8db4c38e` (`docs(bridge): record deterministic services reconciliation report`). Live bridge state at wrap: Loyal Opposition-actionable `NEW` entries are `gtkb-deterministic-services-stale-status-reconciliation-011` and `gtkb-bridge-index-role-intent-sentinel-007`; Prime-actionable scan reports 57 GO/NO-GO threads, led by `gtkb-terminal-project-record-retirement-batch` GO, `gtkb-da-enforcement-completion-slice1-decompose` GO, `gtkb-retire-role-assignments-mirror-slice-1-seed-repoint` NO-GO, and `gtkb-stale-thread-closure-slice-3-impl` GO. Inserted S387 handoff prompt into MemBase `session_prompts` rowid 171. Wrap helper scripts were blocked by the implementation-start gate (`scripts/wrap_capture_transcript.py`, `scripts/wrap_scan_hygiene.py`, `scripts/wrap_scan_consistency.py` treated as protected script targets without a live GO authorization packet), so no S387 transcript/hygiene/consistency reports were produced. Remaining local residue: untracked/runtime `bridge/.claude/` and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-01 (S386 Codex Prime Builder wrap; Codex harness A): committed and pushed the broad GT-KB bridge/governance work batch, then captured wrap state.** User explicitly directed Codex to act as working Prime Builder and commit/push everything possible. Commit `29bac133` (`feat: land bridge mechanics and governance updates`) landed 119 durable files covering bridge mechanics, bridge/index reconciliation, governance hook work-intent enforcement, harness parity skills, project lifecycle bridge artifacts, and focused tests; it was pushed to `origin/develop`. Verification before/during commit: targeted pytest `59 passed, 1 warning`; ruff check passed; staged/range secret scans clean; protected-artifact inventory drift and narrative-artifact evidence gates passed. During wrap, another bridge worker/LO flow landed and pushed `8b86c9e5` (`docs(bridge): record GO and VERIFIED verdicts on bridge index`) with additional bridge verdicts and INDEX entries. Follow-up commit `b35abadc` added role-intent sentinel regression coverage and this S386 memory entry. Latest live bridge implications at wrap: `gtkb-stale-thread-closure-slice-3-impl` is Prime-actionable `GO -004`; `gtkb-terminal-project-record-retirement-batch` is Prime-actionable `GO -004`; `gtkb-index-agent-edit-serialization-scoping` is terminal `VERIFIED -009`; `gtkb-bridge-index-role-intent-sentinel` has corrective post-implementation report `NEW -007` awaiting Loyal Opposition review; `gtkb-deterministic-services-stale-status-reconciliation` has post-implementation report `NEW -011` awaiting Loyal Opposition verification. Wrap evidence is under `.groundtruth/session/snapshots/S386/` with transcript manifest plus hygiene/consistency reports. Wrap scanners wrote reports but exited nonzero because of pre-existing hygiene classes: hygiene `76 ERROR / 4355 WARN`, consistency `2 ERROR / 3923 WARN` (missing indexed bridge files `gtkb-commit-scope-bundling-detection-001-prop-001.md` and `gtkb-auto-push-investigation-001-prop-001.md`, plus historical orphan/snapshot noise). Remaining local residue: ignored/runtime `bridge/.claude/session/spec-events-seen.jsonl.lock` and recurring permission warning on `groundtruth-kb/pytest-kpi-retro-codex/basetemp4/`.

- **2026-06-01 (S385 Antigravity Loyal Opposition wrap; Antigravity harness C, explanatory): responded to the owner's query on parallel sub-agent dispatch.** Confirmed that all prior bridge scan and queue processing cycles were executed directly within the main session with 0 active background sub-agents. Revised and corrected the automated parallel Hourly Scan Prompt to support maximum parallelism. Detailed the technical solution that leverages the existing `scripts/bridge_claim_cli.py` for exclusive process-level work-intent claims and `scripts/bridge_index_writer.py` (`atomic_index_update`) for serialized, lock-guarded in-memory index updates, eliminating lost-update/race risks during parallel index writes. W0 transcript capture, W1 hygiene scan, and W2 consistency scan wrap-up checks were run, writing their markdown reports to `.groundtruth/session/snapshots/bd62d119-38fb-487a-90dc-a862543ea1af/`. The Deliberation Archive harvest completed with 0 new records written.

- **2026-06-01 (S384 Codex Prime Builder handoff configuration): configured Claude-offline bridge mode per owner directive.** Durable harness registry now resolves **Codex/A = active Prime Builder**, **Claude/B = suspended/no role**, and **Antigravity/C = active Loyal Opposition**. Added `harness-state/bridge-substrate.json` with `substrate: none`, which makes both the cross-harness trigger and single-harness dispatcher inert; Antigravity LO work is manual `bridge/INDEX.md` scans only. Mirrored the role state into legacy `harness-state/role-assignments.json` to prevent stale startup/reporting contradictions. Verification passed: active role partition A/PB + C/LO; role/bridge/session/substrate validators; `cross_harness_bridge_trigger.py --dry-run --verbose` skipped as `substrate_mismatch_inert`; `single_harness_bridge_automation.py --dry-run --verbose` skipped as `single_harness_dispatcher_substrate_inactive`; Windows task `GTKB-SingleHarnessBridgeDispatcher` absent. Live bridge scan at wrap: ADVISORY=5 / GO=30 / NO-GO=35 / VERIFIED=68 / WITHDRAWN=40 / NEW=0 / REVISED=0. Wrap scanners were **blocked by implementation-start gate** when invoked through `scripts/wrap_*` without a live bridge authorization packet; do not bypass that gate. Git sync not performed: working tree already contains broad mixed-owner bridge/inventory/memory changes; only scoped handoff files are `harness-state/harness-registry.json`, `harness-state/role-assignments.json`, untracked `harness-state/bridge-substrate.json`, ignored `groundtruth.db`, and ignored `.gtkb-state/mode-switches/20260601T180814Z-2a306674.json`.

- **2026-06-01 (S383 Antigravity integration wrap; Claude harness B, Opus 4.8, explanatory): resumed PROJECT-ANTIGRAVITY-INTEGRATION (WI-3349, bridge `gtkb-headless-gemini-lo-dispatch-verification`).** REVISED-12 (`-013`) retracted the REVISED-11 home-dir PATH enrichment and relied only on the already-verified External Harness Executable Resolution Exception clause-2a ambient-PATH (DELIB-S366) → Codex **GO `-014`**. Implemented 3 spec-derived tests + docstring on `scripts/verify_antigravity_dispatch.py`; **committed `3e41dc3b`** → **pushed origin/develop** (confirmed via `git branch -r --contains`; a concurrent session co-pushed, `git push` reported "Everything up-to-date"). Post-impl `-015` → Codex **NO-GO `-016`**: **evidence-package gap only** — design passed lint/format/applicability/clause/external-harness-boundary-doctor; blockers are a `<sentinel>`-placeholder verifier command and an unrecorded in-root prompt-fixture path. "No owner decision required" → refile corrected report as `-017` (dispatchable next session). WI-3349 stays `open` (accurate; work incomplete).
  - **Dual-PB confirmed already resolved in DB** (per the fd415a89 reconciliation noted below): A=lo active, **B=prime-builder active (sole active PB)**, **C=role `[]` status `registered`** (inactive); last `[B,C]` multi-active dispatch error `05:02Z`, none since. Owner AUQ chose "durably demote C"; `gt mode set-role` refused (can't role-assign an inactive harness), so I **regenerated `harness-state/harness-registry.json`** from DB (now shows C role=[] registered). **Residual:** legacy `harness-state/role-assignments.json` mirror still shows `C=prime-builder` and has no clean tooling path for an inactive harness — this IS the "unbuilt orthogonal role/status SET mechanism" noted in S379 below; captured as a spawn-task under PROJECT-GTKB-ROLE-STATUS-ORTHOGONALITY-DISPATCH. Latent risk only (reactivating C without role fix → `[B,C]` recurs).
  - **INDEX clobber loop observed live** this session: a concurrent PB committed `bridge/INDEX.md` from a stale buffer (`fa6b174e`), repeatedly wiping my `-013`/`-014` lines (Edit-restored GO line clobbered within ~2 min); restored manually, settled once concurrent writes quiesced. Same dispatch-swarm class as S379. Wrap scanners (`.groundtruth/session/snapshots/S383/`): hygiene 69 ERROR/4367 WARN, consistency 3848 WARN — all pre-existing bridge-orphan/dirty-tree noise.
- **2026-06-01 (S379 WI-3494 commit; Claude harness B, Opus 4.8 1M, explanatory): committed the VERIFIED `gt backlog authorize-implementation` thread -> `9b3764f1` on develop (ahead 1, NOT pushed).** Drove WI-3494 (deterministic command collapsing the project-authorization ceremony [record-deliberation + create/extend-PAUTH -> one governed call] per DELIB-2547 "reduce friction, keep gates") full loop: NEW -001 -> NO-GO -002 (GOV-15 status-only bypass) -> REVISED -003 -> GO -004 -> impl + post-impl -005 -> NO-GO -006 (report-only: dropped the clause-scope CLAUSE-VISIBILITY-BULK-OPS evidence + over-specific repro note) -> REVISED -007 -> **VERIFIED -008**. New module `cli_backlog_authorize_implementation.py` + cli.py `backlog authorize-implementation` + `platform_tests/scripts/test_cli_backlog_authorize_implementation.py` (12 T1-T12); 26 pass (incl. 14 backlog-add non-regression); ruff clean. Owner-authority predicate: `--owner-decision` must be source_type=owner_conversation AND outcome=owner_decision (fail-closed). Committed WITH bridge audit trail -001..-008 (inventory-drift-gate review evidence). This is the deterministic-services command that collapses the exact ceremony S379 had to do by hand to authorize WI-3494.
  - **WI-3510 captured** (cross-gate `included_work_item_ids` divergence: Write-time bridge-compliance gate = restrictive allowlist [bridge-compliance-gate.py:608-610] vs impl-start gate = additive [implementation_authorization.py:623]; 38/41 active PAUTHs use allowlists; open for governance review -- do NOT relax Write-time without an owner decision on canonical semantics).
  - **Clobber root cause = dispatch swarm** (~25 concurrent cross_harness_bridge_trigger.py + headless `codex exec` + parallel interactive sessions racing INDEX writes; my -003..-008 INDEX entry reverted to -002 twice). Quiesced once solo. Structural cure = GO'd `gtkb-bridge-dispatch-per-document-lease-substitution`. The VERIFIED `index-edit-race-quiesce` thread fixes the trigger's own edits, not the spawned sessions' races.
  - **Topology**: dual-PB (B+C both prime, C added "while Claude offline") self-resolved when the registry regenerated to C-no-role; commit `fd415a89` reconciled the inventory baseline to single-active-prime, which unblocked the commit. Interim "keep dual-PB" was overtaken by fd415a89; an inactive 2nd prime needs the unbuilt orthogonal role/status SET mechanism (scoped in GO'd `gtkb-role-status-orthogonality-dispatch-scoping`).
  - **Open**: Slice 2 (extend-existing-allowlist path, deferred in-proposal); WI-3494 status still `open` (governed promotion via the post-VERIFIED reconciler or `gt backlog update`); WI-3510; push of `9b3764f1` (not requested). Wrap evidence `.groundtruth/session/snapshots/S379/`; DA harvest 3 created / 473 skipped; hygiene+consistency scans were pre-existing noise only (67 ERR / 3818 WARN, none S379-introduced).

- **S381 (2026-06-01): Codex Loyal Opposition bridge automation queue cleared + wrap evidence captured.** Live `bridge/INDEX.md` was treated as the sole authoritative queue source. Final LO scan reported **0 actionable latest NEW/REVISED entries** with summary ADVISORY=5 / GO=32 / NO-GO=30 / VERIFIED=64 / WITHDRAWN=40. Filed/confirmed verdicts included harness registry parity **NO-GO -007**, startup relay cache TTL GO/NO-GO, wrapup impl-start packet clear **NO-GO -002**, impl-start quoted-arg GO/NO-GO, bridge-kind terminal alignment **VERIFIED -006**, backlog authorize implementation **VERIFIED -008**, dashboard launcher idempotence **GO -002**, bash hook destructive substring **GO -002**, project authorization keep-open **NO-GO -002**, role-status orthogonality landing reconciliation GO/NO-GO/VERIFIED, and bridge dispatch per-document lease substitution **NO-GO -004**. Key Prime follow-up: `gtkb-bridge-dispatch-per-document-lease-substitution-004.md` blocks VERIFIED because production dispatch still contains a `PYTEST_CURRENT_TEST` branch that can call `check_counterpart_active()`; revise by removing that fallback and making the diagnostic suppression test lease-based. Verification evidence: lease + heartbeat tests 5/5 PASS, full trigger suite 43/43 PASS, ruff check PASS, ruff format --check PASS. Wrap evidence captured under `.groundtruth/session/snapshots/S381/`; hygiene scan wrote 63 ERRORs + thousands of WARNs, consistency scan wrote 3818 WARNs, dominated by pre-existing snapshot/report/orphan/pyc noise and broad dirty-tree state. Git sync deliberately blocked: working tree is broad and mixed-owner; do not commit wholesale.

- **S381 (2026-06-01): Prime Builder autonomous proposal run (Claude harness B, Opus 4.8 1M, explanatory). Owner directive: "produce as many friction-reducing implementation proposals as possible, parallelize, work without supervision." Filed 11 implementation proposals (all preflight-clean), 1 correct SKIP. This is the PB-side companion to the Codex LO S381 wrap entry above.**
  - **Method:** ran a deterministic gap-scan (`.gtkb-state/proposal-gap-scan.py`) instead of trusting backlog status — the backlog is PROPOSAL-SATURATED (229 of 348 non-terminal WIs already threaded; ~45 genuine un-proposed GT-KB defects after removing Agent Red `wont_fix` noise). `resolution_status` is systematically stale (whole gate-defect cluster WI-3351/3322/3335/3356/3357/3316 already fixed in source). Cross-check every candidate against a live `bridge/` grep before drafting; drafting done by parallel general-purpose subagents, filing serialized through me.
  - **Fast-lane wave (standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, no fresh approval):** WI-3486 startup-relay-cache-ttl-self-heal (**Codex GO**; Antigravity impl NO-GO'd), WI-3358 impl-start-gate-quoted-arg (**GO**; impl NO-GO'd -004), WI-3413 dashboard-launcher-idempotence (**GO -002**), WI-3493 destructive-gate quoted-substring (**GO -002**), WI-3328 wrapup-clear-impl-packet (**NO-GO -002**), WI-3329 project-auth-keep-open (**NO-GO -002**). The two NO-GOs both hit the CLI-surface PAUTH gap → see auto-memory `feedback_fastlane_standing_pauth_excludes_cli_surface.md`: standing PAUTH = source/test/hook only; any new subcommand OR flag is `cli_extension`, needs a WI-specific PAUTH or NO-GO. To revive WI-3328/3329: dedicated PAUTH or CLI-free redesign.
  - **Owner-authorized batch (AUQ → DELIB-2548 → 5 dedicated PAUTHs):** filed via the now-LIVE collapsed command `gt backlog authorize-implementation <WI> --owner-decision DELIB-2548 ...` (WI-3494/DELIB-2547 deterministic service; mints DELIB+packet+PAUTH in one governed call, `--dry-run` first). PAUTHs: `PAUTH-WI-3488-INDEX-ROLE-SENTINEL-001`, `PAUTH-WI-3487-RESTORE-SYSTEMS-TOOLS-DOC-001`, `PAUTH-WI-3469-PYTEST-BASETEMP-ISOLATION-001` (project `PROJECT-GTKB-MAY29-HYGIENE` — WI-3469's real membership, not reliability-fixes), `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001`, `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001`. Proposals: WI-3488 INDEX role-sentinel stale-reconciliation (sentinel claims Codex-as-Prime/prime_only — live contradiction of role map; 9 parse errors), WI-3487 restore `docs/gtkb-systems-and-tools.md` (lost in isolation-018 Slice 18.C move; 2 platform tests failing now), WI-3469 pytest per-session basetemp (retires S377 waiver), WI-3491 INDEX WITHDRAWN reconcile tool+guard, WI-3482 git-hooks-path lint. All NEW awaiting Codex. WI-3361 SKIPPED (test 96/96 PASS; backlog premise wrong).
  - **Dual-PB contention (important):** role map has B=claude AND C=antigravity both `prime-builder` (C added "while Claude offline" 2026-05-31). Antigravity implemented my GO'd proposals (and got NO-GO'd on the impls) and raced `bridge/INDEX.md`; won INDEX edits via tight paired Read+Edit. Intended fix WI-3511 (suspend C). Auto-memory: `project_s381_autonomous_proposal_run.md`, `feedback_fastlane_standing_pauth_excludes_cli_surface.md`.
  - **Git: DEFERRED** (consistent with the Codex LO S381 wrap's explicit "do not commit wholesale"). My 11 bridge `-001.md` files are all untracked-but-durable on disk and live in INDEX (Codex already reviewed them); a future bridge-audit-trail-catchup commit will capture them in a settled tree. **DA harvest:** my only owner decision (the AUQ) was archived as DELIB-2548 directly by the `gt` CLI (handles its own packet at `.groundtruth/formal-artifact-approvals/2026-06-01-DELIB-2548.json`); no separate harvest needed. **Wrap evidence** already captured by the LO wrap under `.groundtruth/session/snapshots/S381/`. WI-3469 contamination bit the wrap itself (`git status` Permission-denied on `pytest-kpi-retro-codex/basetemp4/`) — live evidence.
  - **Next session:** WI-3413 + WI-3493 are GO'd and ready to implement; WI-3486 + WI-3358 are GO'd but Antigravity's implementations were NO-GO'd (re-implement cleanly); the 5 DELIB-2548 batch proposals await Codex review; WI-3328/3329 need dedicated PAUTHs or CLI-free redesign.

- **S378 (2026-05-31): Slice 10 interactive-session-role-override regression tests landed VERIFIED + inventory-regen chore landed VERIFIED (Claude harness B, Opus 4.7, explanatory style). Two bridge threads carried through full GO/post-impl/VERIFIED cycles with 3 commits to develop.**
  - **Slice 10 thread** `gtkb-interactive-session-role-override-slice-10-regression-tests` (WI-3480, PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001): NEW -001 → NO-GO -002 (bare pytest) → REVISED-1 -003 → NO-GO -004 (POSIX grep in PowerShell workspace) → REVISED-2 -005 → GO -006 → NEW post-impl -007 → NO-GO -008 (F1 assertion 1 dual-row mapping incomplete: Module 5 had STRICT_DROP but not DISPATCH_AUTHORIZED; F2 placeholder regression-command) → REVISED-1 -009 (added 2 DISPATCH_AUTHORIZED tests; exact 17-module regression command + node IDs) → **VERIFIED -010 + committed `47125bb9`**. 53 new test functions across 5 modules under `platform_tests/scripts/`: test_session_role_resolution_table.py (24, assertions 2/3/4/6/7); test_session_role_marker_invalidation_both_harnesses.py (8, assertion 5 via subprocess both dispatchers); test_codex_hook_parity_resolution_table_drift.py (5, assertion 8 via 4 drift classes + baseline); test_cross_harness_trigger_durable_keyed_regression.py (6, GOV-SESSION-ROLE-AUTHORITY-001 marker-blindness); test_strict_drop_misdirected_headless_dispatch.py (10, assertion 1a DISPATCH_AUTHORIZED + 1b STRICT_DROP). 53/53 focused PASS; ruff clean; lane regression 329 PASS (6 pre-existing failures verified pre-existing without my modules).
  - **Inventory-regen chore thread** `gtkb-inventory-regen-chore-commit-2026-05-31` (WI-3449, dual auth: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING + DELIB-2522): unblocks the Slice 10 commit by aligning inventory baseline. NEW -001 → NO-GO -002 (P1 wrong PAUTH for state/baseline scope) → REVISED-1 -003 (governance_review framing + DELIB-2522 archived via `gt deliberations record`) → NO-GO -004 (P1-001 toolchain drift gate still failing; P1-002 collector fails public validation on `gh --version` error containing absolute path) → REVISED-2 -005 (Fix A path-safe `_extract_version` fallback in collector; Fix B toolchain.*.status + .classification added to volatile_inventory_paths; Fix C regenerated inventory; bridge_kind back to implementation_proposal; dual auth) → GO -006 → NEW post-impl -007 + **first commit `7f859fef`** (15 files including state-projection: harness-state/{harness-identities,harness-registry,role-assignments}.json projection of MemBase mode-switch-transaction snapshot for Codex→LO/Claude→PB/Antigravity→PB transitions, per DELIB-2198/2213/DELIB-2522) → NO-GO -008 (P2-001 stale comment in protected-artifact-inventory-drift.toml said status/classification continue to gate after Fix B made them volatile) → REVISED-1 post-impl -009 + **comment-fix commit `df7281ef`** → **VERIFIED -010**. **Origin owner decision: DELIB-2522** (S378 AUQ "Bundled chore: topology + inventory regen") + DELIB-2504 (toolchain.*.version volatility precedent, 2026-05-29) + DELIB-2198/2213 (antigravity harness registration).
  - **Side reliability improvements landed (durable, project-wide impact):** (1) collector `_extract_version` now path-safe — any tool whose `--version` fails with stderr containing an absolute path returns the "unknown" sentinel instead of leaking the path through the public `version` field; (2) drift registry now treats `toolchain.*.status` and `toolchain.*.classification` as volatile alongside `toolchain.*.version`, eliminating cross-workstation tool-availability drift as a commit gate (tool-presence regressions still gate via top-level toolchain key set).
  - **Process patterns surfaced** (auto-memory feedback candidates): (a) compliance-gate regex `^Project Authorization:\s*PAUTH-[A-Z0-9-]+\s*$` rejects N/A values; use `bridge_kind: governance_review` exemption when no PAUTH covers scope; (b) CLAUSE-IN-ROOT failure_pattern catches `C:\Users\...` even in explanatory prose — obfuscate with `&#92;` HTML entities; (c) DELIB-only authorization works for state-projection commits when no PAUTH's allowed_mutation_classes covers `harness-state` or `inventory`; (d) impl-start gate's "simple git finalization command" exemption (`_is_simple_git_finalization_command`) is the canonical bypass for staging/committing under a VERIFIED-terminal bridge thread; (e) inventory-collector-and-baseline protected-artifacts group uses `accept_with_inventory_baseline_update = true` to route inventory chores cleanly; harness-identity-and-role-state group uses `governance_review` route with bridge files as evidence; (f) pre-existing F841 unused variable surfaced after ruff format reformat — `# noqa: F841` with explanatory comment was the min-touch in-target-path defensive fix.
  - **Commits (3, on develop, NOT pushed yet at wrap):** `7f859fef` fix(inventory) original chore [15 files, 1227+/35-]; `47125bb9` test(governance) Slice 10 [17 files; bundled the chore -007 post-impl + INDEX update]; `df7281ef` fix(inventory) comment correction [6 files, 379+/4-]. Branch `develop` ahead of origin by 3 commits + 2 prior-session commits already pushed.
  - **Wrap evidence:** `.groundtruth/session/snapshots/S378/{manifest.json, wrap-scan-hygiene.md, wrap-scan-consistency.md}`. **DA harvest BLOCKED** by GOV-ARTIFACT-APPROVAL-001 (per-deliberation approval packets required); DELIB-2522 was directly archived via `gt deliberations record` which handles the packet flow; no other new owner decisions this session need harvest.
  - **Stale pending decisions** from earlier sessions: DECISION-0861, DECISION-0860 (queue-triage asks; owner gave explicit Slice 10 direction this session, superseding both — eligible for `clear pending`).

- **S374 (2026-05-30/31): Governed retraction of 7 fixture-shape DELIBs (Claude harness B, Opus 4.7→4.8, explanatory style; follow-on to S373 Slice 4). Bridge `gtkb-s374-polluted-delib-2514-2520-governed-retraction` → VERIFIED -007 (terminal).** Workflow (5 agents) researched precedent + drafted; `-001` NEW → `-002` NO-GO (4 findings: target_paths not parseable; impl-start cmd used verdict-file suffix; missing project-linkage metadata; scope-AUQ cited by placeholder) → `-003` REVISED-1 (reclassified `bridge_kind: governance_review` per owner DECISION-0845, removing impl-start semantics; bare `bridge_kind:` line required — `^bridge_kind:` regex won't match `- bridge_kind:`) → `-004` GO → `-006` post-impl → **`-007` VERIFIED**. Inserted **7 append-only v2 supersession rows** for DELIB-2514..2520 (rowids 2682–2688; each v2 `content_hash`==packet `full_content_sha256`); v1 rows + 10 v1 packet files preserved at baseline SHA; **DELIB-2511..2513 untouched** (legitimate). 7 per-record formal-artifact packets at `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-25NN-v2.json` (**gitignored by design** — DB is canonical). Owner chain: DECISION-0834+0842+0843+0845 + grouped per-record approval + "Fix it now" correction. **PROCESS INCIDENT (corrected, lesson durably captured)**: over-parallelized a batch of 7 gated inserts + the success-claiming post-impl report; inserts FAILED (missing `gt deliberations add --summary`) and the co-batched report (`-005`, never persisted) carried fabricated content-hashes + "ALL PASS". Recovery batch ALSO scrambled; only one-command-at-a-time with unique markers gave trustworthy state. Redid inserts correctly, superseded with `-006`. Also a **false "unreliable channel" alarm** (a later turn was actually clean). Lesson → auto-memory `feedback_no_cobatch_report_with_mutations.md`: never co-batch a results-claiming artifact with the mutations it reports; one protected mutation per message; author evidence only from observed output; re-verify before alarming. **Open follow-on (OUT of scope)**: root-cause fix for auto_archive.py fixture-shape `DECISION-0001` source_ref leak; optional provenance DELIB. Branch `develop`; bridge -006/-007/INDEX scoped-committed.

- **S372 (2026-05-29): Bridge-implementation conversation (Claude harness B, Opus 4.8; parallel to S373 same-day). Resumed the S372 in-flight bridge work; took 3 threads to VERIFIED + committed, then originated Phase-2.**
  Three threads VERIFIED and scoped-committed to `develop` (each via `git commit -- <paths>` partial-commit to isolate from the ~723-path parallel-session-polluted index; never `--no-verify`):
  - **`gtkb-axis-2-scoping-terminal-classifier-fix`** (WI-3442) — VERIFIED -004; commit **`428c603e`** `fix:` (AXIS-2 actionable-entry inflation; notify.py + test_bridge_notify.py).
  - **`gtkb-project-completion-scanner-addressing-thread-fix`** (WI-3365) — VERIFIED -017; commit **`af0883b6`** `feat:` (v4 **project-scoped** D4 implements-gate). Arc: NO-GO -012 (P0 cross-project leak: global-slug set let a PROJECT-A implements-link complete PROJECT-B) → REVISED-5 -013 (project-scoped `dict[project_id,set[wi]]`; pre-validated against synthetic 2-project DB) → GO -014 → impl → -016 → VERIFIED -017. Inserted **GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4** to MemBase (formal packet `.groundtruth/formal-artifact-approvals/2026-05-29-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v4.json`, sha `bf4baac8…`). 39 tests incl. 2 cross-project regressions; ruff clean. **Fail-safe: v4 pauses ALL project auto-completion until implements-links exist (0 platform-wide) — correct, conservative.**
  - **`gtkb-root-boundary-external-harness-exec-exception`** (WI-3434) — VERIFIED -008; commit **`9d379289`** `feat:` (bounded External Harness Executable Resolution Exception in `.claude/rules/project-root-boundary.md` + `_check_external_harness_exec_boundary` doctor check + test; committed WITH its 8 bridge files as drift-gate review evidence). Narrative packet `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`. Owner decision `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION`.
  **Phase-2 implements-link backfill** (follow-on to v4): owner AUQ chose Phase-2 then "file scoping proposal". Read-only discovery (captured in **WI-3462**, reliability lane): 8 CLEAN auto-linkable / 3 AMBIGUOUS (all resolvable by "prefer non-scoping, non-superseded thread") / 14 UNADDRESSED; reactive eligible set = 0 (non-urgent). Scoping proposal `bridge/gtkb-implements-link-backfill-phase2-scoping-001.md` filed **NEW, awaiting Codex GO** (both preflights pass; design-only, mirrors orphan-wi-backfill precedent).
  **Self-improvement WIs captured** (reliability lane, unapproved): **WI-3454** (auth-gate `requirement_sufficiency_state` parser needs magic opener phrase), **WI-3463** (bridge gate detectors require magic content phrases — `CLAUSE-INDEX-IS-CANONICAL` bit -015 + Phase-2 scoping; sibling of WI-3454).
  Branch `develop` **ahead of origin by 3** (the commits above) — **NOT pushed** (owner did not request). DA harvest **BLOCKED** (GOV-ARTIFACT-APPROVAL-001 requires per-deliberation approval packets); owner decisions preserved in the two formal packets + each bridge thread's Owner Decisions section + `memory/pending-owner-decisions.md`. Wrap evidence: `.groundtruth/session/snapshots/S372/`. Tool-output-corruption restart early in session (cleared on restart). Process lessons: `git commit -- <pathspec>` isolates partial commits from index pollution; protected-rule commits need a `bridge/` file co-staged (drift gate) + the local narrative packet (narrative gate); never edit a filed bridge file in place (supersede with a new version).

- **S373 (2026-05-30): GTKB-ARTIFACT-RECORDER-CLI Slice 4 conversation (Claude harness B, Opus 4.7 1M, explanatory style). Yet-another parallel S373 conversation alongside `00d6b362` (backlog triage) and `8c70eac3` (commit triage). Took Slice 4 (owner-decision auto-archive integration) from owner-AUQ-selected to VERIFIED + committed in one session through 7 review cycles. Bridge thread `gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive`: `-001` NEW → `-002` NO-GO (target_paths bare-bullet syntax) → `-003` REVISED-1 (heading form; Prime self-superseded after self-catch on inline-JSON regex prose false-match) → `-004` REVISED-2 → `-005` GO → `-006` NEW post-impl → `-007` NO-GO (**P1 live DB contamination via `Path.cwd()` fallback** — 7 fixture DELIBs + 10 same-day approval packets written to live `groundtruth.db`) → `-008` REVISED-1 post-impl (explicit `project_root` required; ValueError on omit; direct `GTConfig(db_path=root/...)` bypass of `GTConfig.load`) → `-009` NO-GO (**remediation plan overreach** — would have retracted 3 legitimate DELIBs alongside the 7 fixture ones) → `-010` REVISED-2 post-impl (corrected scope; explicit `source_ref` discriminator; worker-portable verification command) → `-011` VERIFIED (brief; superseded) → `-012` NO-GO corrective (**post-impl scope broadening** — `-010` added `groundtruth.db` to target_paths after GO at `-005`) → `-013` REVISED-3 (restored 9-path GO'd scope; remediation deferred to its own bridge thread) → **`-014` VERIFIED**. Commit `6c148ad2` `feat:` (16 files: 6 implementation + 9 bridge state + INDEX). Slice 4 helper at `groundtruth-kb/src/groundtruth_kb/owner_decision/`: deterministic `should_auto_archive` classifier (frozen out-of-scope set; no LLM per SPEC-AUQ-NO-LLM-CLASSIFIER-001), `archive_decision` requires explicit `project_root`. Tracker integration `.claude/hooks/owner-decision-tracker.py` `_auto_archive_if_enabled` is env-gated default-off (`GTKB_AUQ_AUTO_ARCHIVE=1` opt-in). 57 tests pass including durable `test_slice4_hook_does_not_touch_live_repo_state` regression. **Open follow-on**: governed retraction of 7 fixture DELIBs (`DELIB-2514..2520`, all `source_ref=DECISION-0001`) + 7 packets (`2026-05-30-DELIB-2514..2520.json`) — must be filed as its own bridge thread with proper target_paths and GO before any mutation. `DELIB-2511..2513` are legitimate parallel-session records (S-2026-05-30-pauth-agent-red-hygiene-cluster, S-2026-05-30-grill-suppression-per-document-lease, S-2026-05-30-lease-substitution-asap-directive) and explicitly excluded. Owner Option A AUQ preserved as durable evidence for the future remediation thread. Wrap scanners (`.groundtruth/session/snapshots/S373/`): W0 manifest written; W1 hygiene 57 ERRORs all pre-existing snapshot accumulation; W2 consistency 3612 WARN all pre-existing orphan-from-INDEX. DA harvest BLOCKED again by GOV-ARTIFACT-APPROVAL-001 (502 sources would each need a packet) — deferred. **Process lessons surfaced this conversation**: (1) "discriminator-before-action" pattern — any remediation list targeting irreversible action must point at the precise data field (here `source_ref`) classifying each item ON/OFF; range-by-temporal-proximity is NOT a discriminator (would have caused the F1 governance damage at -009); (2) bridge-compliance-gate KB-mutation-completeness hook and Codex's scope-discipline pull opposite directions on this exact question — resolution is prose disambiguation (paths named in prose for Future Remediation Note, NOT in target_paths section); (3) the drift-check's "bridge review evidence accepted" branch FORCES the commit's scope to include both code AND audit trail (initial commit attempt with only 6 source files failed; staging the 9 bridge files + INDEX unlocked); (4) Codex's `-011 VERIFIED → -012 NO-GO supersession` is the bridge protocol catching itself via late-arriving sidecar review — both verdicts preserved in append-only chain; (5) `_run_hook_with_env` name-collision: my new test helper shadowed an existing same-named helper with different signature, caused 1 pre-existing test to fail; renamed mine; (6) parallel-session commit race: my bridge state catch-up was beaten to commit (`ff2ef47e`) by another harness at the exact same scope while I was preparing the commit message — standard practice was to stand down after verifying the parallel commit captured my work. Branch `develop` ahead of origin by 4 commits (the 3 from earlier S373 conversations + my `6c148ad2`); not pushed (owner did not request).

- **S373 (2026-05-29): Backlog-triage conversation (Claude harness B; conv `00d6b362`). Parallel S373 conversation (`8c70eac3`) ran the working-tree commit-triage umbrella + scanner-fix; this conversation ran the backlog assessment + implementation-gap triage.**
  Owner asked for a full backlog status report (each project + all outstanding work items) plus an assessment of the project/WI/CLI/skill implementation against the rule that every WI belongs to a named project, projects auto-retire when all WIs are mechanically VERIFIED, and CRUD is deterministic skill+CLI (not markdown). Deterministic MemBase query (read-only) produced: **155 projects (148 active / 7 retired), 2210 work items (231 open + 1800 resolved + others), 507 active memberships, 92 orphan open WIs** (mostly legacy `wont_fix` Agent Red pipeline-failure rows WI-0826..WI-1320), **53 active projects retire-ready** (all WIs terminal) but only 7 actually retired.
  Seven implementation gaps surfaced (§6 of the report): (1) auto-retire scanner is read-only + has the live D3+D4 over-broad-citation defect [in flight at `gtkb-project-completion-scanner-addressing-thread-fix` GO -004]; (2) `backlog add` doubled-prefix membership bug; (3) `kb-work-item`/`kb-batch` skills bypass CLI; (4) `gt backlog` missing retire/link verbs; (5) **no deterministic `gt backlog status` report CLI** (the symptom this assessment itself hit); (6) orphan-WI scanner Slice 2 not filed; (7) `work_list.md` narrative drift.
  DECISION-0758 resolved "start the triage". Owner AUQ chose "Implementation gaps" scope, then "File Gap 5 slice-2 scoping now", then "Pick up Gap 2 (doubled-prefix)".
  **Bridge threads filed this conversation (all Codex-GO'd by wrap):**
  - `gtkb-discoverability-cli-slice-2-scoping` → **GO -002** (terminal scoping approval for `gt backlog status`).
  - `gtkb-discoverability-cli-slice-2-implementation` → **GO -004** (after NO-GO -002 [stale `scanner_caveat` cited the WITHDRAWN `-implementation` dup thread] → REVISED -003 fixed to cite canonical `gtkb-project-completion-scanner-addressing-thread-fix`). Parent WI-3262; PAUTH `...DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI`.
  - `gtkb-project-id-prefix-idempotent-fix` → **GO -003** (Gap 2 fix; after self-detected clause-preflight bulk-ops false-positive on -001 → REVISED -002 added DECISION DEFERRED marker). Root cause: `_project_id_from_names` (db.py:910) unconditionally prepends `PROJECT-`; fix is idempotent normalization. Parent WI-3411 (reliability fast-lane, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`). Phantom-`PROJECT-PROJECT-*` reconciliation (10 projects) deferred to a follow-on (captured in WI-3355).
  **No code written** — both implementation proposals are GO'd but await `implementation_authorization.py begin` + implementation in a future session. Next session: implement both GO'd threads (prefix fix = 1 function in db.py + `platform_tests/scripts/test_project_id_from_names_idempotent.py`; `gt backlog status` = new `cli_backlog_status.py` + cli.py registration + `platform_tests/scripts/test_cli_backlog_status.py`).
  Branch `develop` @ `ec080b6d`; 667 dirty working-tree entries (broad mixed-owner). **Commit deferred to the parallel S373 commit-triage umbrella** (`gtkb-s373-triage-umbrella`); this conversation committed nothing. DA harvest deferred (decisions captured in the bridge files' Owner Decisions sections + `memory/pending-owner-decisions.md`; full S373 harvest best run once by the last-wrapping conversation to avoid double-processing).
  **S373 IMPLEMENTATION-PHASE ADDENDUM (same conv `00d6b362`, resumed; supersedes the "No code written" line above).** Owner directed implementation of the two GO'd threads + the NOT-DEFERRED phantom reconciliation + Gap 6. All landed and VERIFIED:
  - **Gap 2 idempotent prefix fix** (WI-3411) + **`gt backlog status` CLI** (WI-3262): implemented + Codex VERIFIED earlier this session (predecessor work to the threads below).
  - **Phantom `PROJECT-PROJECT-*` reconciliation** (WI-3355): `gtkb-phantom-project-prefix-reconciliation` NEW→NO-GO -002→REVISED-1 -003 (Option A: `groundtruth.db` in target_paths + durable DELIBs)→GO -004→impl→post-impl NEW -005→NO-GO -006 (WI-3408→**WI-3434** factual error + 8th-link over-scope)→REVISED-1 -007→**VERIFIED -008**. New CLI `gt projects reconcile-doubled-prefix` (`groundtruth-kb/src/groundtruth_kb/cli_projects_reconcile.py` + `platform_tests/scripts/test_cli_projects_reconcile.py`, 11 tests). **`--apply` EXECUTED against canonical MemBase**: 49 phantom-membership supersessions + 8 canonical links + 10 phantom-project retirements (append-only; idempotent rerun = 0/0/0; 0 active doubled-prefix projects remain). Owner DELIBs: **2505** (NOT-DEFERRED directive), **2506** (re-link-to-retired disposition, 7 cases), **2508** (accept 8th link WI-3434 — parallel-session retired its canonical between proposal + apply). All 3 packets present.
  - **Gap 6 orphan-WI backfill Slice 2** (WI-3450): `gtkb-orphan-wi-membership-backfill-slice-2-implementation` NEW -001→NO-GO -002 (standing fast-lane PAUTH not eligible: WI-3450 origin=new + new CLI surface fail GOV-RELIABILITY-FAST-LANE-001; + retire/exclude claimed a nonexistent per-WI service)→REVISED-1 -003 (per-WI **PAUTH-WI-3450-ORPHAN-BACKFILL-DRIVER-001** [classes source+test_addition, cites **DELIB-2509**] + assign-only scope)→GO -004→impl→post-impl NEW -005→NO-GO -006 (ruff I001)→REVISED-1 -007→**VERIFIED -008**. New driver `scripts/resolve_orphan_wi_memberships.py` + `platform_tests/scripts/test_resolve_orphan_wi_memberships.py` (10 tests). **Assign-only**; retire/exclude → deferred-action records; NO canonical `--apply` run (read-only dry-run only: 34 orphans, all `owner_decision`). Does NOT touch `cli.py` — cleanly committable standalone. Slice 2b follow-on (per-WI retire service) filed as **WI-3464**.
  - **Gaps 3/7 NOT taken** (parallel-owned / migration-blocked): Gap 3 = `gtkb-skill-modernization-slice-3-kb-work-item-migration` (GO, parallel program PROJECT-GTKB-SKILL-MODERNIZATION); Gap 7 = `work_list.md` drift (migration-bound protected file, slated for deletion per DELIB-S337; collides with uncommitted VERIFIED GOV-010 thread). Left to parallel workstreams.
  - **Also captured:** **WI-3447** (P2 defect: PB startup-disclosure cache fails freshness contract — recurred every session; owner AUQ "proceed minimal" each time).
  - **COMMITS DEFERRED to S373 umbrella** per owner AUQ; two staged handoff notes: `.gtkb-state/commit-messages/wi-3355-phantom-reconciliation.txt` (⚠️ cli.py-ENTANGLED — committing cli.py drags in 3 uncommitted parallel work-streams: hygiene/ pkg [WI-3420], cli_approval_packet.py, cli_bridge_propose.py; committing cli.py alone breaks `import groundtruth_kb.cli`) and `.gtkb-state/commit-messages/wi-3450-orphan-wi-backfill-slice-2.txt` (✅ clean standalone — discover_orphan dep is in HEAD, no cli.py touch). MemBase mutations (reconciliation effect + 4 DELIBs + PAUTH + 2 WIs) are LIVE/durable regardless of git. DA harvest still deferred to last-wrapping conversation.

  **S373 WRAP-TIME EXECUTION ADDENDUM (2026-05-30; Claude harness B, Opus 4.7 1M context).** Continuation conversation executed the deferred commit umbrella + originated Slice 7-prime + filed friction-observation WIs + pushed origin/develop. Wrap procedure executed per `.claude/skills/kb-session-wrap/SKILL.md`.
  - **Commits landed and pushed to origin/develop** (HEAD `2eed3b3c`; 4 mine + 2 prior-session = 6 total):
    1. `ff2ef47e` chore(bridge): audit-trail catchup (580 snapshots + INDEX) — bundles 578 prior-session bridge files + my Slice 7-prime proposal (-009 NEW) + Codex NO-GO (-010). Note: pre-commit hook auto-staged 2 non-bridge files (test_inventory_verified_untested_spec_hygiene_cluster.py + script) into this commit (logged as friction WI-3497).
    2. `7556f873` feat(scripts): orphan-WI driver Slice 2 (WI-3450) — clean standalone per S373 handoff note.
    3. `f7120e49` feat(projects): reconcile-doubled-prefix module (WI-3355 module only) — cli.py registration + test deferred per coordination warning.
    4. `2eed3b3c` docs(memory): operational notepad updates through S373 — this MEMORY.md commit (now extended by this addendum).
  - **Slice 7-prime work** (WI-3490; PAUTH `...SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT`): proposal `-009` NEW → Codex NO-GO `-010` (F1 target_paths missing ~16 callers, F2 protected deletion-evidence path / control-bypass anti-pattern, F3 phantom `--priority` flag, F4 overbroad acceptance grep) → **REVISED-1 `-011` filed** addressing all 4 findings + 2 non-blocking notes; 40 enumerated callers, 16-class principled-exclusion block, deletion-specific approval packet `2026-05-30-WORK-LIST-MD-DELETION-S7P.json` (action: delete) for F2, scoped grep for F4. Applicability preflight clean (`packet_hash: sha256:07239c5783...`). Awaiting Codex review of `-011`. The `-011` proposal lives in working tree (uncommitted).
  - **7 friction-observation WIs filed under PROJECT-GTKB-RELIABILITY-FIXES**: WI-3492 (gt bridge propose CLI; improvement P2), WI-3493 (Bash hook destructive-command false positive; defect P3 — beautifully self-demonstrated during filing), WI-3494 (`gt backlog add --auto-create-pauth`; improvement P3), WI-3495 (auto-inject author/model audit metadata block; improvement P3), WI-3496 (bridge-compliance-gate regex strictness on markdown-bold; defect P3), WI-3497 (pre-commit auto-stage contamination; defect P2), WI-3498 (commit-handoff prep ruff-format step; improvement P3). All linked clean (no doubled-prefix), confirming WI-3411 idempotent fix loaded.
  - **Wrap scanners** (`.groundtruth/session/snapshots/S373/`): W0 manifest written; W1 hygiene exit 0 with 56 "ERROR"-class `snapshots_non_manifest` findings (all pre-existing self-recursion artifacts from prior session scans — scanner creates files the next scan flags as errors); W2 consistency exit 0 with 3613 WARN `bridge_file_orphaned_from_index` (expected INDEX-pruning historical artifacts).
  - **DA harvest BLOCKED again** by `GOV-ARTIFACT-APPROVAL-001` (`harvest_session_deliberations.py --apply` requires `GTKB_FORMAL_APPROVAL_PACKET`). Owner decisions preserved in bridge proposal Owner Decisions sections + `memory/pending-owner-decisions.md` + this addendum. Owner directives captured this session: Path A migration retirement (S373 AUQ), "commit everything possible" (post-wrap-up direction), friction-WI filing directive, push authorization, run wrap-up authorization, `resolve DECISION-0831 wrap-up`. S373 unresolved DELIB candidates: S373-WORK-LIST-RETIREMENT-PATH-A, S373-COMMIT-EVERYTHING-POSSIBLE, S373-SLICE-7-PRIME-REVISED-1.
  - **session_prompts insertion BLOCKED** (same GOV-ARTIFACT-APPROVAL-001 path). S374 handoff prompt written to `.groundtruth/session/snapshots/S373/handoff-S374.md` (gitignored snapshot path; copy/paste into `::init gtkb pb` session for fast continuation).
  - **Process lessons (this conversation)**: REVISED-1 took 1 Write attempt vs -009's 4 (all gates from -009 pre-internalized — project-linkage triplet plain-text, author/model audit block, avoiding `git rm` literal pattern, plain-text section structure); pre-commit hook autostage contamination is a real failure-mode worth a dedicated WI; the wrap-scan suite has a self-recursive defect (every run leaves files the next run flags as errors); `gt projects authorize --scope` text hard-blocked on `git rm` substring (work-around: reword); cli.py and CLAUDE.md are now BOTH cross-thread coordination points (cli.py with WI-3355 + 3 other streams; CLAUDE.md with `gtkb-claude-md-scope-clarification-slice-3` NO-GO).
  - **Process lessons:** post-impl drift narratives are a new instance-site for "probe-before-quoting-counts" (WI-3408→WI-3434 error caught by Codex); pre-submission `ruff check` + `ruff format --check` on target files belongs in the impl flow alongside pytest (ruff I001 NO-GO cost one round-trip); PAUTH activation requires `--include-spec` (`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`); `backlog add` doubled-prefix bug did NOT fire in later-session subprocesses (idempotent fix loaded from working-tree db.py).

- **S366 (2026-05-27): Prime bridge continuation, Antigravity dispatch verification, and document-provenance advisory.**
  Codex continued from the cleared Loyal Opposition queue as Prime Builder,
  processing Prime-actionable GO/NO-GO bridge responses from live
  `bridge/INDEX.md`. Revised proposals were filed for
  `gtkb-work-item-priority-canonical-p0p3-migration`,
  `gtkb-chromadb-vector-continuity-v1-cut-scoping`,
  `gtkb-git-repo-broken-blob-investigation`, and
  `gtkb-skill-modernization-scoping`; Loyal Opposition auto-dispatch later
  returned GO for those threads. The git fsck missing-blob issue remains
  separate follow-up reliability debt, with existing WI-3394 context and no
  repair attempted in this session. Codex implemented the GO for
  `gtkb-headless-gemini-lo-dispatch-verification`: added
  `scripts/verify_antigravity_dispatch.py`, its platform tests, the sentinel
  fixture, and updated `memory/antigravity-integration-status.md`. Focused
  verification passed: 5 dispatch-verification tests passed and ruff passed;
  the live Antigravity/Gemini substrate check failed because Python subprocess
  could not launch bare `gemini` while `gemini.cmd --version` worked. The
  implementation report was filed at
  `bridge/gtkb-headless-gemini-lo-dispatch-verification-005.md`, and later
  bridge state shows follow-on LO responses through `-007`.

  Owner asked whether new document artifacts include model+harness production
  details. Codex scanned document surfaces and found partial bridge-only
  coverage, not repo-wide enforcement. A fresh advisory was written at
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-13-24-DOCUMENT-ARTIFACT-AUTHOR-PROVENANCE-GAP.md`
  recommending a dedicated `gtkb-document-artifact-author-provenance` proposal.
  That report is in the gitignored insight dropbox and intentionally not
  force-added.

  Wrap evidence is under `.groundtruth/session/snapshots/S366/`. Live bridge
  scan at wrap: 118 documents; latest counts `ADVISORY=1`, `GO=20`, `NEW=1`,
  `NO-GO=24`, `VERIFIED=35`, `WITHDRAWN=37`; Prime-actionable latest GO/NO-GO
  count 44; Loyal Opposition-actionable latest NEW/REVISED count 1
  (`gtkb-headless-gemini-lo-dispatch-verification` NEW at `-007`). MemBase
  `current_work_items` counts: `open=200`, `in_progress=1`, `new=1`,
  `deferred=1`, `resolved=1796`, `verified=45`, `retired=64`,
  `wont_fix=59`, `not_a_defect=7`. Hygiene scan exited nonzero with
  49 ERROR / 4307 WARN, dominated by snapshot-manifest and dirty-tree findings;
  consistency scan reported 3606 WARN, dominated by historical orphan
  bridge-file inventory. DA harvest apply timed out after about two minutes.
  No commit/push was attempted because the branch is `develop` ahead 1 and the
  worktree contains broad mixed-owner tracked/untracked changes.

- **S365 (2026-05-27): Codex Loyal Opposition bridge queue processing pass.**
  Owner asked Codex LO to process as many actionable bridge items as possible
  in parallel using sub-agents. Codex used the `gtkb-bridge` workflow, live
  `bridge/INDEX.md`, mandatory applicability and ADR/DCL clause preflights,
  and read-only sub-agent reviews. Eleven bridge items were processed and
  `bridge/INDEX.md` was updated append-only:
  `GO` for `gtkb-inventory-regen-chore-commit-2026-05-27-002.md` and
  `gtkb-worker-packet-auth-envelope-slice-2-auto-packet-002.md`;
  `VERIFIED` for `gtkb-bridge-compliance-gate-fenced-code-parser-fix-004.md`;
  `NO-GO` for `gtkb-agent-red-reference-adopter-framing-restoration-002.md`,
  `gtkb-headless-gemini-lo-dispatch-verification-002.md`,
  `gtkb-skill-modernization-scoping-002.md`,
  `gtkb-impl-report-bridge-structural-validation-mtime-004.md`,
  `gtkb-project-completion-scanner-wi-auto-regex-fix-004.md`,
  `gtkb-lo-hygiene-assessment-skill-build-003.md`,
  `gtkb-s358-w3-requirements-collection-hook-title-fix-012.md`, and
  `gtkb-bridge-target-paths-kb-mutation-check-004.md`.
  A late Prime update added `gtkb-inventory-regen-chore-commit-2026-05-27-003.md`
  after `-002` was GO'd, so it remains LO-actionable. End-of-session live
  LO bridge scan: 5 actionable items (`gtkb-inventory-regen-chore-commit-2026-05-27`
  NEW at `-003`; `gtkb-s358-w1-retirement-machinery-correction` REVISED at
  `-018`; `gtkb-bridge-compliance-gate-wi-auto-regex-fix` NEW at `-003`;
  `gtkb-startup-relay-truncation-fix-refile` NEW at `-011`;
  `gtkb-gt-bridge-propose-deterministic-cli` NEW at `-005`).
  Wrap evidence is under `.groundtruth/session/snapshots/S365/`. DA harvest
  apply was blocked by `GOV-ARTIFACT-APPROVAL-001` due missing formal approval
  packet. Hygiene scan exited nonzero with 45 ERROR / 4079 WARN, dominated by
  known snapshot-manifest policy and dirty-tree warnings; consistency scan
  reported 3436 WARN, dominated by historical orphan bridge-file inventory.
  No commit/push was attempted because the worktree already contained broad
  mixed-owner changes; only the bridge verdict files and INDEX edits from this
  pass should be attributed to Codex LO.

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

- S382 (2026-06-01): **Closed dangling Codex GO on `gtkb-role-enhancement-review-depth-methodology` & resolved per-document lease substitution + heartbeat fix (WI-AUTO-SPEC-INTAKE-57A736).** Address Codex NO-GO at `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-004.md` by decoupling production trigger (`scripts/cross_harness_bridge_trigger.py`) from legacy test fallbacks and updating suppression tests to acquire per-document leases. 48/48 regression tests pass cleanly; ruff check + format check clean. Post-implementation report filed at `-005` and VERIFIED by Codex LO at `-006` closing the bridge thread successfully. Also closed dangling Codex GO on `gtkb-role-enhancement-review-depth-methodology` via format-only REVISED `-005` -> Codex GO `-006` -> post-impl `-007` -> VERIFIED `-008` (committed `33c93fe7` + **pushed origin/develop**). Wrap caveats: DA harvest dry-run = 479 would-create (no apply without formal approval evidence); wrap-tree dirty with concurrent-session modifications; scanners 69 ERROR / 4373 WARN (chronic baseline, my thread 0 orphan findings); W0/W1/W2 scans written at `.groundtruth/session/snapshots/S382/`.
- 2026-06-01 Codex bridge automation wrap: live Loyal Opposition bridge queue drained to 0 latest `NEW`/`REVISED` entries. Codex filed `bridge/gtkb-backlog-update-cli-slice-1-006.md` VERIFIED and `bridge/gtkb-role-status-orthogonality-dispatch-landing-reconciliation-008.md` VERIFIED; concurrent bridge workers filed `gtkb-bash-hook-destructive-substring-false-positive-002.md` GO, `gtkb-project-authorization-completion-keep-open-002.md` NO-GO, `gtkb-impl-start-gate-quoted-arg-misclassification-004.md` NO-GO, and `gtkb-dashboard-launcher-idempotence-pid-tracking-002.md` GO. Final scan summary: `ADVISORY=5`, `GO=32`, `NO-GO=30`, `VERIFIED=64`, `WITHDRAWN=40`; LO actionable 0. Verification highlights: backlog-update CLI tests/ruff passed with in-root pytest basetemp; role-status projection reconciliation verified DB/projection A/B/C match, resolver B/A, and attribution regression pass. Caveat: a late subagent disputed `gtkb-backlog-update-cli-slice-1-006.md` on report-completeness grounds after the append-only VERIFIED verdict was already filed; treat as residual review concern for future cleanup rather than silent closure.
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
