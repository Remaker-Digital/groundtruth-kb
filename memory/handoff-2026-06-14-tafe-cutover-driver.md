author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c2f8c28a-bc49-4158-a509-1ae540eec86d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder session c2f8c28a; `::init gtkb pb`; autonomous /loop driving TAFE Phase-7; explanatory output style

# Handoff — Drive TAFE to Governed Cutover (WI-4510)

**Updated:** 2026-06-15 ~15:50Z by Prime session `11c6b2a8` (harness B, Opus 4.8).
**State:** ✅ **WI-4510 PHASE-3 CUTOVER COMPLETE — FLIP EXECUTED; WI-4510 RESOLVED.** Switch is now
`tafe_canonical` (TAFE shadow authoritative; `bridge/INDEX.md` a byte-faithful generated view).
Default-OFF code VERIFIED at `-008`; gate-2 fully approved + executed interactively. Source is
**UNCOMMITTED** (no commit requested yet; -007 VERIFIED so the no-commit rule is now satisfied —
commit is a pending follow-up, INDEX.md to be consolidated deliberately per Codex). Prior state was
`NEW@-007` awaiting Codex; Codex VERIFIED at `-008`.
**Boundary (Codex):** the GO does NOT authorize the irreversible flip / GOV amendment / DCL insert /
PAUTH expansion / `formal_spec_promotion` — all remain gate-2. Codex attached 4 impl conditions (include
the new failure-injection tests not just the 59 prereqs; show final pre-cutover GREEN
`cutover-evidence`/`regen-verify`; separate WI-4508 vs WI-4510 closure evidence; GO ≠ flip).
**Phase-3 implementation STARTED — owner chose lowest-risk slice first (this session):** the default-OFF
switch surface is implemented + verified (**11 tests pass, ruff clean**) under impl-start packet for
`gtkb-wi4510-phase-3-authority-flip`:
- `scripts/bridge_authority_cutover.py` — direction reader (`read_authority_direction`, fail-safe to
  `index_canonical`) + `freeze_index`/`flip_to_tafe_canonical`/`revert_to_index_canonical` + guarded CLI
  (`status`/`freeze`/`flip --confirm-irreversible`/`revert`). The deferred chokepoint imports the reader
  from here (it is in `target_paths`; a standalone reader module would not be).
- `harness-state/bridge-authority-direction.json` — the switch, default `index_canonical` (behavior-inert).
- `groundtruth-kb/tests/test_bridge_authority_direction.py` — DCL-INDEX-GENERATED-VIEW-001 #3 (safe default)
  + #4 (reversibility backstop).

**DEFERRED to a focused follow-on slice** (the risky half): `db.py` `insert_bridge_thread_atomic` +
no-commit cores (touches the hot `insert_flow_instance`/`insert_flow_artifact` surface), the
`atomic_index_update` chokepoint authority-branch (`bridge_index_writer.py`; imports
`read_authority_direction`), the publish-reconcile guard (`tafe_bridge_ingestion.py`), the
`gt flow publish-reconcile` CLI (`cli.py`), the writer migrations (`gtkb_bridge_writer.py`,
`bridge/index_mutation.py`, `cli_bridge_index.py`), and `test_tafe_authoritative_write_path.py`
(failure-injection: the 3 Codex scenarios + atomicity + INDEX-ahead-quarantine + index_canonical
byte-identity). **NO impl report filed yet** — the single impl report must cover the FULL target_paths +
the failure-injection tests (Codex condition #2), so it is filed only after the follow-on completes.
Slice files are UNCOMMITTED (no commit until the full Phase-3 is VERIFIED).

## Turn @ ~15:50Z (session 11c6b2a8): Codex VERIFIED -008; GATE-2 EXECUTED; FLIP DONE; WI-4510 RESOLVED

Codex VERIFIED the default-OFF impl report `-007` at `-008` (thread now terminal VERIFIED). Owner then
drove the full gate-2 sequence interactively (after a mid-session tooling recovery — see below):

- **Gate-2 step 1 (GOV v2):** owner AUQ "Approve GOV v2" → `GOV-FILE-BRIDGE-AUTHORITY-001 v2` recorded
  (governance, verified) via `gt spec update` + formal packet; owner decision `DELIB-20263432`.
  v2 = TAFE-authoritative source; INDEX a byte-faithful generated view; read-discipline + LO repair
  authority preserved verbatim.
- **Gate-2 step 2 (DCL):** owner AUQ "Approve DCL" → `DCL-INDEX-GENERATED-VIEW-001` created
  (design_constraint, specified, 11 assertions) via `gt spec record` + formal packet; `DELIB-20263433`.
  Gotcha: DCL-* content MUST contain a `## Constraint` (or "constraint statement") section or
  `gt spec record` errors "DCL-* specs require an explicit constraint section".
- **Gate-2 step 3 (PAUTH):** owner AUQ "Approve PAUTH" → new bounded authorization
  `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-3-CUTOVER-EXECUTION-WI-4510` (allows
  `cutover` + `formal_spec_promotion`, scoped WI-4510) via `gt projects authorize`; `DELIB-20263434`.
- **FLIP EXECUTED** (owner AUQ "Execute the flip"): pre-flip final re-ingest `gt flow ingest-bridge-index
  --apply` (3 instances/10 artifacts) → `cutover-evidence ok=True` (348/348, contention-zero) +
  `regen-verify ok=True` (reformat_only, missing=[], extra_divergent=[]) → `bridge_authority_cutover.py
  flip --confirm-irreversible`. Frozen backstop: `bridge/.authority-cutover/INDEX.frozen-20260615T154739Z.md`.
  Switch now `tafe_canonical`. `DELIB-20263435` (execution record). Post-flip smoke CLEAN
  (status=tafe_canonical; regen-verify ok=True; publish-reconcile in_sync no-op).
- **WI-4510 RESOLVED** (`gt backlog resolve WI-4510 --owner-approved`; stage=resolved).

**KNOWN POST-CUTOVER CONSEQUENCE (flag + follow-up):** the generated view = render(append-only shadow),
which has **351 threads vs the live INDEX's 348** (3 terminal-archived: gtkb-wi4572, gtkb-wi4574, sp1).
The FIRST `tafe_canonical` bridge write will reformat the whole INDEX AND **re-add those 3 archived
threads** (regen renders all shadow threads). Bigger principle: INDEX archival-trimming
(`bridge_index_archival`) is now defeated — regen re-adds trimmed threads, so the INDEX grows with
terminal threads over time unless an archival-aware generator or shadow-retirement policy is added.
Visible+tolerated in the approved GREEN evidence (extra_archived ungated), so by-design, not a hidden
defect — but captured as a backlog follow-up. Until the first write, the system is STABLE
(regen-verify reformat_only / publish-reconcile in_sync; INDEX stays 348-block old-format, shadow
authoritative).

**TOOLING-RECOVERY LESSON (cost 1 session-blocking incident):** a `cd groundtruth-kb` inside a Bash
command PERSISTED as the shell cwd; the relative-path PreToolUse hooks (`.claude/hooks/...`) then
failed to resolve and **fail-closed-blocked every Read/Bash/PowerShell/Edit/Write/AskUserQuestion**
(deadlock: cwd reset needs a shell command, which is blocked). Recovered after the cwd reset to
`E:\GT-KB`. RULE: never `cd` into a subdir in a Bash command in this repo — use absolute paths /
`sys.path.insert`. (Also: the spec-links harvest gotcha from the prior turn still applies.)

**REMAINING FOLLOW-UPS (non-blocking):** (1) commit the now-VERIFIED Phase-3 work (source uncommitted;
`gtkb-sweep-commit`, INDEX.md consolidated deliberately per Codex) — owner-gated; (2) post-cutover
INDEX archival/growth policy (backlog WI captured); (3) the first tafe_canonical bridge write will
apply the one-time reformat + re-add 3 archived threads (can be triggered deliberately or left to the
next natural write); (4) optional Codex post-hoc review of the executed cutover (dispatcher OFF/manual).

## Turn @ ~14:10Z (session 11c6b2a8): Phase-3 risky-half IMPLEMENTED + impl report -007 filed

Implemented the FULL deferred default-OFF `tafe_canonical` write path under GO `-004` + impl-start
packet `sha256:780659e8…` (claim rowid 2660/2661). All within `-003` `target_paths`; **uncommitted**;
live switch still `index_canonical` (`bridge_authority_cutover.py status` confirms). Edits:
- **`db.py`** (HIGHEST RISK): extracted no-commit cores `_insert_flow_instance_row`/`_insert_flow_artifact_row`;
  public `insert_flow_instance`/`insert_flow_artifact` delegate to core+commit (byte-for-byte preserved,
  proven by unchanged 59 prereq tests). Added `insert_bridge_thread_atomic(planned_instances,
  planned_artifacts,...)` = one `BEGIN IMMEDIATE … COMMIT` (mirrors `acquire_stage_lease` idiom).
- **`tafe_bridge_ingestion.py`**: `plan_bridge_thread_writes` / `planned_to_db_kwargs` /
  `build_prospective_shadow` / `assess_publish_state` + `PublishReconcileVerdict` (in_sync/tafe_ahead/
  index_ahead, INDEX-ahead detected at block AND per-version) / `make_archived_extra_oracle` /
  `open_flow_service`. All I/O-light (lazy `verify_against_index` import avoids the generator cycle).
- **`bridge_index_writer.py`**: `atomic_index_update` authority branch (default index_canonical
  byte-identical; tafe_canonical → `_tafe_canonical_publish`: reconcile-guard → mutate → plan →
  project → regen → verify-BEFORE-commit → `insert_bridge_thread_atomic` → atomic publish →
  `_post_publish_self_check`). Added `reconcile_publish` (lock-holding), `_read_authority_direction`
  (fail-safe), optional `project_root` param, `CrossStorePublishError`. ruff `--fix` modernized 3
  pre-existing `timezone.utc`→`UTC` (untouched helpers; behavior-preserving).
- **`cli.py`**: `gt flow publish-reconcile`. **`bridge_authority_cutover.py`**: `reconcile` subcommand.
- **Writers NOT edited** (gtkb_bridge_writer / index_mutation / cli_bridge_index): all route through
  `atomic_index_update`, inherit the switch — zero edits (lowest-risk; matches proposal's chokepoint design).
- **NEW `test_tafe_authoritative_write_path.py`** (13 tests): DCL #6-#11 + Codex's 3 scenarios +
  atomicity ROLLBACK + index_canonical byte-identity. Failure injection via monkeypatch on the lazy
  import seams (`plan_bridge_thread_writes`, `_atomic_write`, `_insert_flow_artifact_row`).

**Verification (all GREEN):** 63 passed (new suite + direction + ingestion + generator); 20 (cutover-evidence
+ generator-cli); 36 (new + chokepoint `platform_tests/scripts/test_bridge_index_writer.py` + direction);
ruff check + format --check clean on all 6 changed .py; py_compile OK. Broad `-k` run: **792 passed, 3
PRE-EXISTING failures** in untouched subsystems (test_bridge_status_driver ADVISORY-routing vs live INDEX;
test_governance_hooks claim-step-before-spec-links ×2) — documented in -007.

**Report -007 addresses all 4 Codex GO conditions:** (1) flip stays gate-2; (2) failure-injection tests
included; (3) flip-readiness NOT claimed — final GREEN re-ingest deferred to gate-2 window (current
read-only cutover-evidence/regen-verify RED = phase-3 thread not yet shadow-ingested, expected per -004);
(4) WI-4508 vs WI-4510 closure separated (no WI resolved). Both/all 3 preflights GREEN on indexed -007
(applicability passed, missing_required=[]; clause exit 0; citation-freshness clean).

**NEXT (for the next driver): owner triggers MANUAL Codex VERIFIED on `-007`** (dispatcher OFF). After
VERIFIED → bring owner the GATE-2 package via **AskUserQuestion ONLY** (4 decisions: final-execute flip
AUQ; GOV-FILE-BRIDGE-AUTHORITY-001 v2 amendment formal packet; DCL-INDEX-GENERATED-VIEW-001 creation
formal packet incl. assertions 1-11; PAUTH expansion for `cutover` + `formal_spec_promotion`). Then
gate-2 execution (swarm-quiesced): `gt flow ingest-bridge-index --apply` → GREEN cutover-evidence/regen-verify
→ freeze → `bridge_authority_cutover.py flip --confirm-irreversible` → post-flip smoke → resolve WI-4510.
On anomaly: `bridge_authority_cutover.py revert [--restore-frozen <frozen>]` or `reconcile`.

**NEW GATE LESSON (reusable):** the applicability-preflight spec-link harvester
(`bridge_applicability_preflight.extract_spec_links`) stops the `## Specification Links` harvest at ANY
line whose stripped form starts with `#` — NOT just real headings. A wrapped bullet whose continuation
line begins with a `#`-prefixed token (e.g. a DCL assertion ref `#6–#11`, or `#3 / #4`) silently
truncates the harvest, dropping every spec cited after it → `missing_required_specs` hard-block at Write
even though the IDs are present. `classify_spec_links_section` still says `harvested` (heading-only check),
so it's invisible there. FIX: inside `## Specification Links`, never let a line start with `#` — spell out
assertion numbers ("assertions 6 through 11"). Debug via `extract_spec_links(content)` directly. This cost
2 blocked Writes on -007 before diagnosis.

## Turn @ ~13:10Z (session b5f59b69): standing ADVISORY backlog triage + R1-R5 unblock

Owner directed triage of the 15 standing bridge `ADVISORY` entries (separate workstream from WI-4510).

- **Triage (4 parallel read-only agents):** 5 close-stale/acknowledged (antigravity-startup-gov-docs,
  antigravity-implements-link, antigravity-insight-stale, owner-role-switch-codex-lo, delib-2500);
  ~10 convert-to-WI were **already tracked by the advisory-router** (dashboard→WI-3433, arch-audit→
  WI-4409/4411 + PROJECT-ARCHITECTURE-IMPROVEMENT P3/P4, antigravity-consolidation→WI-3505, sp1→
  WI-4400/4401, fable→WI-4436, session-role-marker→WI-4540, parity-gap→WI-4543, ollama→WI-4477/4556/4558);
  **WI-4575** created as the one genuinely-new capture (2026-06-14 quality-scout's 3 doctor-hygiene repairs,
  reliability fast-lane). KEY LESSON: the advisory-router auto-converts advisories to backlog WIs, so the
  ADVISORY pileup is a *disposition* gap, not a *capture* gap.
- **R1-R5 enforcement UNBLOCKED (owner AUQ Option 1).** The GO'd+green `gtkb-role-resolution-r1-r5-
  assertion-enforcement` report was gate-blocked for missing project linkage. Executed the mint path:
  `DELIB-20263427` (owner decision) → **WI-4576** (admitted to `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-
  OVERRIDE`) → bounded PAUTH `...-R1-R5-ENFORCEMENT-GUARD-TEST-ADDITION-AUTHORIZATION` (test_addition,
  cites DELIB-20263427) → re-filed report **`-006` NEW** with full linkage. Re-verified the guard green
  (7 passed, ruff clean) before filing. Both preflights GREEN on `-006` (applicability `sha256:e6bae9a7…`;
  clause 0 blocking gaps after adding a Bridge-Protocol-Compliance evidence line for CLAUSE-INDEX-IS-CANONICAL).
  Thread now `NEW -006` → **Codex actionable for VERIFIED**. Test file stays untracked until VERIFIED + sweep-commit.
- **Held but tracked (owner chose Hold one-at-a-time):** arch-audit P1 (7 Agent-Red-vs-governance ADRs;
  PROJECT-ARCHITECTURE-IMPROVEMENT / WI-4409/4411), Fable program (PROJECT-FABLE-INVESTIGATION, 23 WIs,
  chartered), dashboard cockpit (WI-3433, has a 4-question grilling gate before first slice). No mutations
  for the held items.
- Gate lessons reconfirmed: every `bridge/**` file must cite `GOV-FILE-BRIDGE-AUTHORITY-001` (applicability
  preflight); WI-collision detector flags any bare `WI-NNNN` != declared; CLAUSE-INDEX-IS-CANONICAL needs an
  explicit `bridge/INDEX.md` append-only evidence line; the claim gate fires on **Edit** too, not just Write;
  INDEX writes only via `gt bridge index set-status`.

## Turn @ ~12:45Z (session b5f59b69): recovered design panel + REVISED -003 filed (resolves NO-GO -002 F1)

- **Context recovery.** Prior session `c50a9788` filed Phase-3 NEW `-001`, got Codex **NO-GO `-002`**
  (single P1 **F1** — the `tafe_canonical` write path needs an explicit cross-store fail-closed + recovery
  contract between the TAFE DB write and the generated INDEX publish), launched a background design workflow
  (`wf_5b32bc33-32a`), then **died** while waiting. This session recovered the workflow's persisted result
  from the transcript dir (`c50a9788…/workflows/wf_5b32bc33-32a.json`): `result.synth` was **null** and the
  adversary `verdicts` were **empty** (the synthesis stage failed — likely the crash cause), BUT the two
  design-stage outputs (Strategy A "transactional-no-publish", Strategy B "write-ahead-recoverable") were
  fully persisted and high-quality. Did NOT re-run the 9-min workflow; synthesized the F1 resolution from
  the two designs.
- **REVISED `-003` FILED** via `revise_bridge.file_revision` (NO-GO-gated; candidate preflights passed
  internally). Lowest-regret hybrid: **prepare → single-transaction commit → atomic publish**, exploiting
  `INDEX = render(TAFE)`. New §"Cross-store fail-closed publish contract": (1) pre-commit byte/semantic
  verify so the common divergence fails closed with BOTH stores byte-identical to pre-write; (2)
  `insert_bridge_thread_atomic` = one `BEGIN IMMEDIATE … COMMIT` for instance + all artifacts (fixes the
  independent-commit hazard at db.py:5445/:6412 via no-commit cores; public methods unchanged); (3) the only
  post-commit failure mode is a bounded, self-healing **TAFE-ahead** window (lossless republish from the
  append-only shadow); (4) **INDEX-ahead is structurally impossible** through the chokepoint, quarantined
  (never auto-ingested) otherwise; (5) a publish-reconcile guard at write-start / `gt flow publish-reconcile`
  / startup / `--reconcile`. Added DCL-INDEX-GENERATED-VIEW-001 assertions **#6–#11** + failure-injection
  tests (Codex's 3 scenarios + atomicity + INDEX-ahead-quarantine + index_canonical byte-identity) targeting
  `test_tafe_authoritative_write_path.py`.
- **target_paths expanded** to add `groundtruth-kb/src/groundtruth_kb/db.py` (transaction helper),
  `tafe_bridge_ingestion.py` (reconcile guard), and `cli.py` (`gt flow publish-reconcile`).
- **Post-filing preflights GREEN** on indexed `-003`: applicability `sha256:039df126…`,
  `missing_required_specs:[]` + `missing_advisory_specs:[]`; clause exit 0, 0 blocking gaps; citation
  freshness clean. INDEX: `REVISED -003 / NO-GO -002 / NEW -001`. Author metadata = this session.
- **Mechanics.** Work-intent claim acquired (`rowid 2656`) + released. WI-4522 author env vars set in-session
  (helper requires `session_context_id`/`model`/`model_version`/`model_configuration`; identity + harness
  auto-resolved). **No commit** (bridge filing only). Zero MemBase mutation. Gate-2 AUQ stays blocked on
  Codex GO — presenting it pre-review would collapse two safety gates. Draft body cached at
  `.gtkb-state/bridge-revisions/drafts/gtkb-wi4510-phase-3-authority-flip-003.md`.

## Turn @ ~07:30Z (session c50a9788): baseline commit + Phase-3 proposal filed

- **Baseline commit `760de9746`** (`chore(gtkb): consolidate VERIFIED TAFE cutover baseline …`) via the
  governed `gtkb-sweep-commit` path. Bundled the two VERIFIED prerequisites (WI-4510 Phases 0-2 + WI-4574)
  + their bridge audit trail + in-flight swarm infra (WI-4572 deploy-FQDN config-ization, bridge-substrate
  dispatcher-disable, inventory/memory). Verification: whitespace clean, `scan_secrets.py` 0 findings (the
  6 Azure-FQDN candidate-highs are public hostnames, not credentials; the actual stdlib gate found 0),
  inventory drift PASS, narrative-artifact PASS, ruff-format PASS, `py_compile` clean, 199 tests pass. The
  only `ruff check` lint warnings (4) are in unrelated swarm files (`deploy.py`/`repair_widget_hash.py`/
  `test_run.py`) — left untouched per the sweep no-touch-unrelated rule; the pre-commit hook gates on
  ruff-FORMAT (passed), not ruff-check. Not pushed.
- **Phase-3 proposal FILED:** `bridge/gtkb-wi4510-phase-3-authority-flip-001.md` (NEW), dedicated thread
  (Phases-0-2 thread is VERIFIED-terminal; NEW dedicated thread > REVISED-after-VERIFIED). Filed via
  `write_bridge.propose_bridge` (WI-4522 author env vars set; `pre_populate=False`, `db=None` to avoid the
  corrupt ChromaDB; self-acquired+released work-intent claim). Contents (the gate-2 review package):
  the authority-direction switch design at the `atomic_index_update` chokepoint (`index_canonical` default
  unchanged / `tafe_canonical` = TAFE-first write → regenerate INDEX byte-faithful → verify-or-fail-closed);
  the full proposed **GOV-FILE-BRIDGE-AUTHORITY-001 v2** amended text (authority-source clause only; LO
  repair authority + re-read-live-INDEX read-discipline PRESERVED); the new **DCL-INDEX-GENERATED-VIEW-001**
  (5 machine-checkable assertions); writer-migration inventory; reversibility backstop (frozen timestamped
  immutable INDEX copy + `scripts/bridge_authority_cutover.py --revert`); swarm-quiesce + final-re-ingest
  runbook; `## Specification Links` (exact heading); Prior Deliberations; Requirement Sufficiency
  ("Existing requirements sufficient" — ADR is the governing requirement; GOV amendment + DCL are derived
  formalization); spec-to-test plan; Owner Decisions / Input (the 4-item gate-2 package).
- **Phase-3 target_paths** (execution scope, gate-2-gated): `bridge_index_writer.py`,
  `gtkb_bridge_writer.py`, `bridge/index_mutation.py`, `cli_bridge_index.py`, `tafe_index_generator.py`,
  new `scripts/bridge_authority_cutover.py`, new `harness-state/bridge-authority-direction.json`,
  + 2 new test files.

## Next steps — Phase-3 gate sequence (CURRENT; supersedes the older "Next steps" below)

1. **Owner triggers MANUAL Codex review** of `gtkb-wi4510-phase-3-authority-flip` (dispatcher off).
   Codex GO or NO-GO. On NO-GO → file REVISED `-003` addressing findings (keep both preflights green).
2. **After GO → owner gate-2 package (the irreversible flip), all via AskUserQuestion:** (a) gate-2
   final-execute AUQ confirming the flip; (b) GOV-FILE-BRIDGE-AUTHORITY-001 v2 amendment formal-artifact-
   approval packet; (c) DCL-INDEX-GENERATED-VIEW-001 creation formal packet; (d) PAUTH expansion to permit
   `cutover` + `formal_spec_promotion` (the PHASE-6-7-CUTOVER PAUTH currently forbids both).
3. **Execute Phase 3** (post-gate-2, swarm-quiesced): final `gt flow ingest-bridge-index --apply` +
   `cutover-evidence`/`regen-verify` GREEN → freeze backstop + flip via `bridge_authority_cutover.py` →
   post-flip smoke (write through each writer path; INDEX stays byte-faithful). Insert the amended GOV v2
   + new DCL via formal packets. impl-start packet from the GO first; stay within `target_paths`.
4. **Impl report** (carry spec links + spec-to-test evidence + the executed runbook) → Codex VERIFIED →
   **resolve WI-4510** (the reconciler should auto-resolve once the Phase-3 thread is VERIFIED and the
   report no longer scopes itself partial).
5. **Do NOT rush; it is irreversible.** Re-verify LIVE state each cycle. On any post-flip anomaly:
   `scripts/bridge_authority_cutover.py --revert`.

## Turn @ ~03:40Z (session c50a9788): gate fix + root-cause investigation

- **Took over lapsed claim** for `gtkb-wi4510-tafe-authoritative-cutover` (owner AUQ "wait for lapse,
  then file"). Set prime-builder session marker (`workstream_focus._write_session_role_marker`), claim
  + impl-start packet OK (packet `7d05ac7b…`). GO `-006` authorizes Phases 0-2 only.
- **Verified the GO'd implementation:** 15 unit tests pass, ruff clean, Phase-0 `cutover-evidence`
  GREEN — BUT live `gt flow regen-verify` was DIVERGENT: 349 shadow vs 347 INDEX; 2 extra threads.
- **Adversarial design workflow (`wf_b375fbf4-0b9`)** rejected naive Option A (filtering generator input
  would make the gate BLIND to phantoms — false-green) → **Refined Option B**: `verify_against_index`
  partitions extras into `extra_archived_in_generated` (ungated, via the shared
  `tafe_index_completeness._candidate_is_archived` oracle, dependency-injected to keep the generator
  pure) vs `extra_divergent_in_generated` (gating). CLI wires the real oracle with the
  `slug in expected_docs and …` guard + `or slug in acknowledged` fallback.
- **Root-cause investigation (owner AUQ "investigate first"):** full shadow scan → the phantom is
  ISOLATED (exactly 1 phantom / 1 mismatched / 1 duplicate, all = `sp1-…`), NOT systemic. Root cause:
  ingestion keys `subject_id` to the INDEX `Document:` name; a historical phantom INDEX entry
  `Document: sp1-…` (no gtkb- prefix, pointing at the `gtkb-sp1-…` file) was ingested → orphan; INDEX
  phantom later trimmed; append-only shadow retains the orphan (pure duplicate, same artifact_ref → zero
  content loss). Filed **WI-4574** (root-cause precursor: ingestion phantom-guard + sp1 reconcile).
- **Gate fix implemented + tested:** `tafe_index_generator.py` (verify partition + 2 new result fields)
  + `cli.py` (classifier wiring + summaries) + 5 unit + 3 CLI tests. **23 targeted tests pass, 269
  broader TAFE/flow tests pass, ruff lint+format clean.** Live regen-verify now correctly partitions:
  `extra_archived=[gtkb-wi4572]` (ungated), `extra_divergent=[sp1]` (gating), `ok=False` — CORRECT.
  Changes UNCOMMITTED (no commit under swarm); part of WI-4510, to commit at its eventual VERIFIED.

## Bridge dispatcher DISABLED (2026-06-15 ~04:57Z, by Codex/owner)

The auto-dispatcher was switched off: `harness-state/bridge-substrate.json` → `substrate: none`
(`gt mode set-bridge-substrate --substrate none`). Hooks stay registered but skip (no worker spawns).
The swarm is quiesced; **I am the sole active agent.** Consequence: the bridge GO/NO-GO/VERIFIED cycle
is now **manual** — Codex (LO) must be triggered by the owner to review filed proposals/reports. The
file bridge itself remains usable manually.

## Next steps (for the next driver)

0. **WI-4574 — DONE (VERIFIED `-007` + auto-resolved).** Codex VERIFIED `-006` at `-007` (24 ingestion
   + 244 broader tests, ruff, preflights). The "Bridge VERIFIED backlog reconciler" auto-resolved WI-4574
   (`resolution_status=resolved`, per `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`). The
   guard + `sp1` reconcile are in the working tree (uncommitted).

0b. **WI-4510 Phases 0–2 — IMPL REPORT `-007` FILED; awaiting MANUAL Codex VERIFIED.** Under GO `-006`
   + impl-start packet `sha256:619422c0…`: ran Phase 0 (`gt flow ingest-bridge-index --apply` → 1
   instance/7 artifacts, the WI-4574 thread). Now **regen-verify is GREEN** (`ok=True`,
   `status=reformat_only`, `missing=[]`, `extra_divergent=[]`, `extra_archived=[gtkb-wi4572, sp1]`);
   `cutover-evidence ok=True`; Phase 1–2 = 23 tests pass + ruff clean. Both preflights GREEN on `-007`.
   Report draft: `.gtkb-state/tmp/wi4510-impl-report-007-body.md`. **NEXT: owner triggers manual Codex
   VERIFIED on `-007`.** After VERIFIED, only **Phase 3 (the irreversible flip)** remains — gate-2 owner
   AUQ + `GOV-FILE-BRIDGE-AUTHORITY-001` amendment + writer migration + reversibility backstop, as a
   careful dedicated REVISED (do NOT rush; irreversible).

1. _(superseded — WI-4574 now DONE)_ **WI-4574 IMPL REPORT `-006` FILED; awaiting MANUAL Codex VERIFIED.**
   Trajectory: `-002` NEW → `-003` NO-GO (`--apply` outside target_paths) → `-004` REVISED (removed
   `--apply`) → `-005` GO (Codex, manual) → `-006` IMPL REPORT (this session). Both preflights GREEN on
   `-006`. Implementation (34e432's, adopted+verified under GO `-005` + impl-start packet
   `sha256:d3e9bbb7…`): `_file_slug_from_path` + `_plan_thread` guard, reversible `sp1` config entry,
   guard tests — UNCOMMITTED in the working tree. Evidence in `-006`: 24 ingestion tests pass, ruff
   clean, read-only regen-verify shows `sp1` in `extra_archived` / `extra_divergent` empty (no `--apply`
   run). **NEXT: owner triggers manual Codex VERIFIED on `-006`** → then resolve WI-4574 (GOV-15,
   origin=defect) → unblocks WI-4510. Report draft: `.gtkb-state/tmp/wi4574-impl-report-006-body.md`.
   _(superseded `-004` awaiting-GO state below.)_

1a. _(superseded)_ **WI-4574 REVISED `-004` FILED + IMPLEMENTATION STAGED + VERIFIED;
   awaiting MANUAL Codex GO.** Codex NO-GO'd `-003` (verification-plan `--apply` DB mutation outside
   `target_paths`). REVISED `-004` (`bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-004.md`) removes
   `--apply` (read-only regen-verify only; shadow re-ingest deferred to WI-4510 Phase-0); both preflights
   GREEN. A now-gone dispatched worker (`34e432`) already implemented the fix in the working tree
   (UNCOMMITTED): `_file_slug_from_path` + `_plan_thread` guard in `tafe_bridge_ingestion.py`, the `sp1`
   `[[acknowledged]]` entry in `tafe-acknowledged-archived-bridges.toml`, +114 test lines. Verified
   sound: **24 ingestion tests pass, ruff clean, read-only regen-verify shows `sp1` in
   `extra_archived_in_generated` + `extra_divergent_in_generated == []`.** On Codex GO: run impl-start
   packet, re-confirm tests/ruff + read-only regen-verify, file impl report → VERIFIED → resolve WI-4574.
   Body draft: `.gtkb-state/tmp/wi4574-proposal-revised-004-body.md`.
   _(Superseded earlier `-002` PROPOSAL FILED state below.)_

1b. _(superseded)_ **WI-4574 PROPOSAL FILED, awaiting Codex GO.**
   `bridge/gtkb-wi4574-tafe-ingestion-phantom-guard-002.md` (NEW; `-001` was a self-detected
   preflight-gap draft superseded by `-002`, both preflights GREEN on `-002`). Fast-lane (defect):
   WI-4574 admitted to `PROJECT-GTKB-RELIABILITY-FIXES` (standing PAUTH covers source/test); the
   owner-curated `sp1` config entry is authorized by `DELIB-WI4574-RECONCILE-AND-GUARD-AUTHORIZE-20260615`.
   Scope: (a) ingestion phantom-guard in `tafe_bridge_ingestion._plan_thread` (skip a `Document:` block
   whose name ≠ the slug derived from its version-line `artifact_ref`; fail-open on unparseable paths) +
   test in `groundtruth-kb/tests/test_tafe_bridge_ingestion.py`; (b) add
   `sp1-dispatch-reliability-prime-handoff` to `config/governance/tafe-acknowledged-archived-bridges.toml`
   (rule 3, reversible). On GO: implement (impl-start packet first), re-run Phase-0 + regen-verify →
   GREEN, file impl report → VERIFIED. Body draft: `.gtkb-state/tmp/wi4574-proposal-body.md`.
2. After WI-4574: re-run Phase-0 (`ingest --apply` + `cutover-evidence` ok=True) + `gt flow regen-verify`
   → expect GREEN. Then file the WI-4510 impl report `-007` (carry the gate-fix + Phase-0/regen evidence)
   → Codex VERIFIED → then owner gate-2 (the irreversible flip) remains for a later REVISED.

## Superseded prior state (pre-GO)

ADR approved+inserted; canonical proposal filed; duplicate WITHDRAWN; `-002` NO-GO → `-003` REVISED →
`-004` NO-GO (Phase-0 DB writes outside target_paths) → `-005` REVISED (added groundtruth.db) → GO `-006`.

## NO-GO `-002` → REVISED `-003` cycle (2026-06-15 ~01:00Z)

- **Codex NO-GO `-002`** (harness A): F1 (P1) live `gt flow cutover-evidence` was RED — shadow missing 3
  instances while the proposal cited a GREEN snapshot; F2 (P2) Requirement Sufficiency used two operative
  phrases (WI-3439 unambiguity).
- **F1 resolved both ways:** ran `gt flow ingest-bridge-index --apply` (3 instances / 6 artifacts; the 3
  cited slugs) → fresh `cutover-evidence` GREEN (348/348, `1962==1962`, contention-zero, fidelity-ok);
  AND added an explicit **Phase 0 — Shadow-currency recovery** with acceptance criteria (clean
  cutover-evidence before any Phase-2 claim). Reframed the churn as evidence *for* the proposal's gates.
- **F2 resolved:** single operative phrase ("Existing requirements sufficient for Phases 1-2 only");
  Phase-3 statement moved to a separate "Future Phase 3 Gate" (no second operative phrase, 0 body-wide).
- **Adversarial pre-file panel** (workflow `wf_97341b6c-035`, 3 diverse-lens skeptics): `consensus_ready`,
  all "ready-to-file", none would NO-GO again; 2 independently re-ran cutover-evidence GREEN. Fixed the
  2 cosmetic nits they flagged (en-dash normalization; 6-vs-5 artifact-count clarification).
- **Filed `-003` REVISED** via `revise_bridge.file_revision` (NO-GO-gated; candidate preflights passed).
  Post-filing: applicability `preflight_passed:true` packet `sha256:1214457b…`; clause exit 0 / 0 gaps.
  Draft: `.gtkb-state/tmp/wi4510-proposal-revised-003-body.md`.

## Progress this session (c50a9788) — 2026-06-15

- **Evidence re-verified GREEN** (read-only, no INDEX mutation): `gt flow cutover-evidence --json` →
  `ok=True`, parity 345/345 (`derived_artifacts=1956 == index_version_lines=1956`), `lost=0/extra=0`,
  `contention_zero=true`, `fidelity.ok=true`.
- **ADR inserted:** `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` v1 (specified, type=architecture_decision)
  via `gt spec record`; packet `.groundtruth/formal-artifact-approvals/2026-06-15-ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001.json`
  (sha256 `4b4d53c9…`). Owner AUQ approval `DELIB-WI4510-ADR-AUTHORITATIVE-BRIDGE-STATE-APPROVE-20260614`.
  Decision: TAFE store canonical; `bridge/INDEX.md` a byte-faithful generated view; 4-phase reversible
  rollout; flip gated by WI-4510 closing AUQ. Draft: `.gtkb-state/tmp/ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001-draft.md`.
- **Canonical proposal FILED:** `bridge/gtkb-wi4510-tafe-authoritative-cutover-001.md` (NEW), under the
  PHASE-6-7-CUTOVER PAUTH. `target_paths` = Phase 1–2 surface (generator + tests + shadow-verify CLI).
  Applicability preflight `preflight_passed:true` (`sha256:86b14fbb…`); clause preflight exit 0,
  0 blocking gaps. Body draft: `.gtkb-state/tmp/wi4510-proposal-body.md`.
- **Duplicate reconciled:** a pre-existing `gtkb-wi4510-governed-cutover` (NEW, governance-only,
  `target_paths:[]`, defers ADR) was WITHDRAWN (`-002.md`) per owner AUQ
  `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` ("New canonical; withdraw old"). Its unique
  **reversibility backstop** (freeze a timestamped immutable INDEX copy at cutover + documented/coded
  revert) is CARRIED FORWARD into the canonical thread's **Phase-3 REVISED** (folded in at gate-2 time;
  not added to the still-NEW `-001` because REVISED is NO-GO-gated and the backstop is Phase-3 scope).

## Architecture map (for the implementer)

- **Migration surface collapses to WRITERS + 1 new generator** because readers operate on the generated
  INDEX/string: `bridge.detector.parse_index` (string in), `bridge.notify.compute_actionable_pending`
  (parse-result in, reads `bridge_kind` from disk), and dispatchers/hooks read the INDEX *file*. Keep
  INDEX byte-faithful → readers unchanged.
- **Prerequisite GAP (Phase 1):** no byte-faithful TAFE→INDEX generator exists. `tafe_index_preview.render_tafe_bridge_index_preview`
  (WI-4507) is non-authoritative and renders from `stage_instances` (absent for bridge threads). Build
  `render_index_from_flow_artifacts` reading `flow_artifacts` (`fa-bridge-<slug>-<NNN>`,
  `metadata.status_token`, `artifact_ref`) — version-line history is there (parity 1956==1956).
- **Writers to migrate at flip (Phase 3, gate-2):** `scripts/gtkb_bridge_writer.py`
  (`insert_index_status`, `remove_document`), `groundtruth_kb/bridge/index_mutation.py`
  (`add_document`/`set_status`), `cli_bridge_index.py`, and the propose/revise/impl-report helpers under
  `.claude/skills/`. `write_bridge_file` (versioned file write) is unaffected. Behind an
  authority-direction switch defaulting to INDEX-canonical; the FLIP = flipping the switch (= `cutover`).
- **PAUTH boundary:** `...PHASE-6-7-CUTOVER...` allows `source/test_addition/config/dual_write/authoritative_generated_view`
  (Phases 1–2 do-now) but FORBIDS `cutover` + `formal_spec_promotion` (Phase 3 flip + GOV amendment need
  gate-2 + their own formal packets).

## Remaining sequence (for the next driver)

1. **Codex GO** on `gtkb-wi4510-tafe-authoritative-cutover` (dispatchable; cross-harness trigger fires
   on Stop). Prime acts only on GO/NO-GO. On NO-GO: revise `-002` (REVISED) addressing findings.
2. After GO → implement **Phase 1** (PAUTH `authoritative_generated_view` + `test_addition`):
   `render_index_from_flow_artifacts` + round-trip golden test (ingest live INDEX → regenerate → assert
   byte-equal). Run `implementation_authorization.py begin --bridge-id gtkb-wi4510-tafe-authoritative-cutover`
   first; stay within `target_paths`.
3. **Phase 2** (PAUTH `dual_write`): `gt flow regen-verify` CLI + test; run repeatedly under the swarm
   for a sustained green window + `cutover-evidence` GREEN.
4. **Gate-2 AUQ** (owner) — present Phase 1–2 evidence + the rollback runbook (incl. the carried-forward
   frozen-INDEX backstop) and confirm the irreversible flip. Required because PAUTH forbids `cutover`.
5. **Phase 3 REVISED** (post-gate-2): writer migration behind the authority switch + the flip + the
   `GOV-FILE-BRIDGE-AUTHORITY-001` amendment (own formal packet) + new generated-view DCL + write-guard
   hardening. Fold the frozen-INDEX reversibility backstop in here.
6. Impl report → Codex VERIFIED → resolve WI-4510.

## Where things stand (re-verify LIVE each cycle)

- **Reconciliation DONE.** `gt flow cutover-evidence --json`: `lost_blocks=0, extra_blocks=0,
  parity=True` (STABLE). `contention_zero`/`fidelity` reflect only a 2-thread transient
  shadow-currency lag (1 new + 1 status-advanced swarm thread), cleared by
  `gt flow ingest-bridge-index --apply`. Not drift.
- **Phase A** (oracle terminal-token classification, `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001`
  v1): VERIFIED at `bridge/gtkb-tafe-shadow-index-reconciliation-006.md` (lost 634→74).
- **Phase B** (sibling-rule + acknowledged-archived config, DCL v2): VERIFIED at
  `bridge/gtkb-tafe-phase-b-acknowledged-archived-004.md` (lost 74→0). Config:
  `config/governance/tafe-acknowledged-archived-bridges.toml` (68 acknowledged slugs).
- **Phantom extra_block** (`sp1-dispatch-reliability-prime-handoff`): self-resolved via INDEX
  trimming (extra 1→0). The GO'd `gtkb-bridge-index-remove-document` verb thread is now OFF the
  critical path — optional reusable tooling (GO@-002; worker bailed, never wrote the impl).
  Decide separately: implement it (reusable for future phantoms) or WITHDRAW it.
- **Owner gate-1 APPROVED**: `DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` — proceed to FILE the
  cutover proposal. Gate-2 (final irreversible execute AUQ) still required before any flip.

## The WI-4510 cutover is a FUNDAMENTAL ARCHITECTURE MIGRATION (the scope finding)

Today: `bridge/INDEX.md` is canonical (`GOV-FILE-BRIDGE-AUTHORITY-001`); the TAFE shadow is
ingested FROM INDEX.md (`tafe_bridge_ingestion.ingest_bridge_index`). The cutover REVERSES this:
TAFE shadow becomes canonical; `bridge/INDEX.md` becomes a GENERATED view (the `tafe_index_preview`
generator is explicitly NON-authoritative today; WI-4507 is the compatibility generator).

Unimplemented; requires at minimum:
1. **A new ADR** for the authority flip (TAFE-authoritative bridge state) — GOV-20.
2. **Amending `GOV-FILE-BRIDGE-AUTHORITY-001`** (its core "INDEX.md is the sole authoritative
   workflow state" invariant changes) — formal-artifact-approval packet + owner approval.
3. **Migrating every bridge WRITER** to write TAFE-first: `scripts/gtkb_bridge_writer.py`
   (add_document / insert_index_status / atomic_index_update) + the propose/revise/impl_report
   helpers under `.claude/skills/`.
4. **Making INDEX.md generation authoritative** (regenerate INDEX from TAFE after each write).
5. **Migrating READERS + DISPATCHERS** treating INDEX.md as truth: `cross_harness_bridge_trigger`,
   `bridge.notify`, the AXIS-2 surface, scan/show helpers, the SessionStart governance hook.
6. **Rollback plan** (revert authority to INDEX.md) + **swarm-quiesced execute window** + a
   **final pre-cutover re-ingest** (the active swarm continuously re-stales the shadow).
7. **Phased rollout** (dual-authority shadow-verify → flip → INDEX-generated), not a single flip.

## Next steps for the cutover-proposal author

1. Re-verify live cutover-evidence; a fresh `gt flow ingest-bridge-index --apply` (go_implementation;
   covered by the cutover/WI-4566 PAUTH `tafe_shadow_ingest`) makes contention/fidelity green
   momentarily to demonstrate `ok=True`.
2. Author the **ADR** for TAFE-authoritative bridge state; owner formal-artifact approval.
3. File the **WI-4510 cutover proposal** under
   `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510` (WI-4510),
   citing the ADR + the GOV amendment + the phased migration + rollback + swarm-quiesce/final-re-ingest
   runbook. `## Specification Links` EXACT: GOV-FILE-BRIDGE-AUTHORITY-001 +
   DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001 + DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
   + DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 + advisory trio.
4. Codex GO → owner **gate-2 final-execute AUQ** (confirm rollback) → phased implementation →
   impl report → VERIFIED → resolve WI-4510.

## Capability + gotchas

- `::init gtkb pb` NOT go_implementation-eligible by default; reconciliation/cutover-prep was
  owner-authorized via `DELIB-WI4546-MARKER-IMPL-AUTHORIZE-20260614`. The cutover IMPLEMENTATION
  (irreversible) needs fresh owner authorization + gate-2 AUQ.
- Marker invalidated by SessionStart; re-set via `scripts/workstream_focus.py::_write_session_role_marker(...)`
  only when implementing.
- **WI-4522**: set `GTKB_AUTHOR_IDENTITY/HARNESS_ID/SESSION_CONTEXT_ID/MODEL/MODEL_VERSION/MODEL_CONFIGURATION`
  env vars before any bridge-helper file/revise (current.json no longer read).
- `gt spec record/update` self-governing → PowerShell; `## Specification Links` EXACT; INDEX edits
  ONLY via `gt bridge index` (raw Edit hook-blocked).
- ChromaDB HNSW index corrupt (tracked WI-4562/4565); deliberation SQLite rows still land despite the
  embed timeout — `record_decision` with a generous timeout.
- Do NOT commit under the heavy concurrent swarm; one owner decision at a time via AskUserQuestion.

## Key IDs

`DELIB-WI4510-CUTOVER-PROCEED-GATE1-20260614` (gate 1) · `DELIB-WI4510-CUTOVER-HOLD-PRE-RECONCILIATION-20260614`
(HOLD) · `DELIB-20263195` (cutover-sequence auth) · `DELIB-WI4546-{RECONCILE-STRATEGY-REFINE-ORACLE,
PAUTH-AUTHORIZE,DCL-COMPLETENESS-APPROVE,DCL-COMPLETENESS-V2-APPROVE,PHASE-B-DISPOSITION-STRATEGY,
MARKER-IMPL-AUTHORIZE}-20260614`. `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` (v2) ·
`ADR-TAFE-SLICE-C-INGESTION-001`. PAUTHs: `...-PHASE-7-RECONCILIATION-WI-4546`,
`...-PHASE-B-RESIDUAL-CLEANUP-WI-4566`, `...-PHASE-6-7-CUTOVER-WI-4508-4509-4510`. Canonical MemBase:
`E:\GT-KB\groundtruth.db`.

## Copyright
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
