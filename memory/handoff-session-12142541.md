# Session Handoff — 12142541 (Prime Builder, harness B)

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 12142541-773d-4560-8095-1fcc131101ff
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope

Date: 2026-08-08. Non-authoritative operational note. Canonical authority is
MemBase, the Deliberation Archive, and the numbered bridge chain.

## Start here

1. `gt bridge state-report` — live queue.
2. `DELIB-20260807012015` — registry/junk doctrine D1–D7. **Read before any deletion work.**
3. `DELIB-20260807011978` — earlier session decisions (dispatcher exclusion, wi6024 consolidation, enforcement Option B, E1 scope exception).
4. `bridge/gtkb-adbr-t0-mechanism-repair-004.md` — the live T0 GO.

## Live threads

| Thread | State | Next actor |
|---|---|---|
| `gtkb-adbr-t0-mechanism-repair` | `-004 GO` | Prime Builder — partially implemented |
| `gtkb-wi6065-projects-skill-path-rename-fallout` | `-003 REVISED` | Loyal Opposition |

## T0 — completed and verified

| Item | Evidence |
|---|---|
| **E2** AC-15 verifier repaired | `check_project_dependency_ordering.py:168` repointed to `gtkb-projects`; `PROJECT-DEP-A1..A5` PASS, exit 0. Confirmed the asserted string exists at `.claude/skills/gtkb-projects/SKILL.md:161` first, so the fix did not clear the crash while leaving the assertion false |
| **W1 items 1–5** back-ported | 5/5 ordered-hash equal. `gtkb-prime-builder.md` = `8903abf36b990a1b`, matching the `wi5984` approval packet. `gtkb-file-bridge-protocol.md` = `dd36b7ace7f40592`, 541 lines, 0 diff hunks |
| **E1** false Generator Inventory purged | 4 false "No generator" rows replaced with derived truth + `Source` column; second defect fixed — regenerate list named 3 of 5 generators |
| **E3** Pre-GO gate script tracked | `scripts/pre_verdict_executability_check.py` staged (`?? → A`) |
| Dead paths in canonical | **0** |

Two controls that existed only in generated files are now safe in canonical: the
purge-before-probative directive (`DELIB-20260806011917`) and the Mandatory
Pre-GO Executability Gate.

## T0 — remaining

- **W1b hygiene deletions.** Do not use the raw `unregistered_disposable` set as a path list — see D4/D5.
- **W0 coverage manifest.** Ruleset designed, not yet written to `config/registry/coverage-manifest.toml`. Constraints: first-match-wins ordering, the **inverse** of `gtkb_file_reference_migration.py:717` (higher-priority-wins) — do not copy priority numbers across; brace globs `{a,b}` match **nothing** in every Python matcher and must be expanded; `.claude/worktrees/**` (59,215 files) must be pruned before descent or it resurrects 38 pre-rename skill directories as canonical.
- **W1 item 6** — `project-root-boundary.md` forward-port question, for the owner.
- **P5 / P6** — outstanding owner prerequisites: `repository_metadata` for `.gitattributes`; a `.githooks/**` taxonomy rule. Neither blocks the GO.

## Registry work — current focus

Doctrine: `DELIB-20260807012015`. Sequencing is strict — **verify and perfect the
registry, then delete.** Nothing has been deleted.

Measured (`gt registry reconcile --json`, 22,687 entries): `registered` 20,788 ·
`unregistered_load_bearing` 71 · `unregistered_disposable` 1,821 ·
`invalid_unknown` 7 · `membership_complete: false` · `sweep_eligible: false`.

| Thread | WI | Scope |
|---|---|---|
| 1 | **WI-6075** | Admit the 71 load-bearing (batch pre-computed); resolve the 7 `invalid_unknown` |
| 2 | **WI-6074** (P0) | D4 directory inheritance + D5 exempt directories |

Both need bridge proposals. `gt registry register` requires `--bridge-id`,
`--pauth-id`, `--start-packet-hash` — admission is a governed mutation.

**D7 — write-time enforcement is in scope**, but the owner's answer restated both
options without eliminating one. Confirm before treating as settled.

**D5 open:** `applications/` is exempt; the owner noted there may be other such
directories. The exempt set is owner-determined and must not be inferred.

## Defects captured

| WI | Sev | Summary |
|---|---|---|
| WI-6056 | P1 | Concurrent verdict permanently destroys a bridge thread — `bridge_lifecycle_resolver.py:458` requires `responds_to == version-1`; append-only means it can never be repaired. Killed the first T0 thread |
| WI-6057 | P1 | Pre-GO Gate A false positive — `pre_verdict_executability_check.py:95` omits `mutation_class_families()` |
| WI-6065 | P1 | Stale `projects` path in `test_projects_skill_adapter.py` (filed, `-003 REVISED`) |
| WI-6066 | P2 | Fast-lane spec says membership suffices; the check requires explicit `included_work_item_ids` |
| WI-6074 | **P0** | Registry sweep-safety: hosted application root marked disposable; directory disposability ignores registered descendants |
| WI-6075 | P1 | The 71 admission + 7 `invalid_unknown` |

## Owner decisions outstanding

1. Which `wi5984-004` is authoritative — the published original (`consumed` twice) or the re-authored file in `HEAD`. Both preserved; differ ~40%.
2. The recovery-file commit — two originals recovered byte-exact from unreachable git objects, still prunable.
3. `wi6024` — decided NO-GO but never filed; still live at `-003 NEW`, can still collide with T0-W1.
4. Whether publication-loss (145 undone attempts) gates T0 — raised, never ruled, T0 proceeded.

## Cautions

- **Packet churn.** The implementation packet is session-global and was superseded four times by other sessions. Re-validate `.gtkb-state/implementation-authorizations/current.json` before every protected mutation; `authorized: true` can be coincidental overlap with another thread's paths.
- **Stale hook warnings.** T0 edits emit `NO-GO status ... gtkb-adbr-t0-mechanism-repair-and-discovery` — the chain-dead thread, not live authority.
- **Three hook false positives:** a scratchpad write blocked as controlled-artifact mutation; a `Select-String` loop blocked as harness-to-harness launch; an explicit-interpreter call blocked as direct helper execution. All legitimate read-only work.
- **Verify scope, not just measurement.** Two of this session's errors were correct measurements attributed to the wrong subject: a two-file pytest count reported as one file's, and `storage_path` string counting reported as registry coverage (4.6% vs the true 91.6%).

## Scratch to clean

`bridge/_adbr_t0_body.md`, `_adbr_t0_body_004.md`, `_adbr_t0_refile_body.md`,
`_adbr_t0_rev003.md`, `_wi6065_body.md`, `_wi6065_rev003.md`;
`.gtkb-state/spec-intake/*.md` (3 files consumed by `gt spec record` /
`gt deliberations record`). All in the disposable set.
