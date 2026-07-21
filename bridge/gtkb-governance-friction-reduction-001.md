Status: NEW
Bridge-Id: gtkb-governance-friction-reduction
Bridge-Kind: advisory_proposal
Author: goose (G) loyal-opposition
author_identity: loyal-opposition/goose
author_session_context_id: G-2026-07-21T05-49-33Z
Created: 2026-07-21
Responds to: owner request (post-rollout session retrospective)
Work Item: (none yet — new WI(s) to be created at implementation proposal time)

# Advisory: Governance & startup friction reduction — front-load enforcement, auto-stamp mechanical metadata, surface hidden knowledge

## Summary
This advisory captures a transcript-level retrospective of the extended interactive session that
executed the gtkb- canonical skill-rename rollout (WI-5640) plus the two follow-on parity-gap
work items (WI-5641 goose manifest, WI-5642 cursor-fallback DEFERRED reporting). All
implementation for that program is complete and committed (head `e0554bd8`; parity **WARN**,
PASS 353 / MISSING 0). The dominant cost of the session was **not** any single defect — it was
*staggered, reactive discovery of rules and knowledge that all live in one place but are
enforced in three and surfaced in none*. This advisory organizes those findings into an
actionable program for a Prime Builder.

The session burned an estimated 60+ tool calls on avoidable search, retry, and one-error-at-a-time
validation loops. Every finding below is claim → evidence → recommendation, scoped to what a
builder (GLM-5.2) needs to start cold.

**Core thesis (do not lose this):** the bridge protocol and the GOV gates are *correct and
working*. The friction is that the *same* checks are enforced at *different* times by *different*
surfaces, and the knowledge needed to pass them is discoverable only by failing first. The fix is
to **front-load** enforcement to filing time, **auto-derive** mechanical metadata, and **surface**
the knowledge at the point of need — not to weaken any control.

---

## Category 1 — Knowledge that should have been loaded (role def / envelope action / skill)

These are cases where I spent many tool calls locating a fact that was one page away, or that no
page held at all. The fix is surfacing, not new documentation volume.

### 1.1 Session-envelope worker-role provenance (highest severity)
- **What I searched for:** how to satisfy worker-role provenance. I inspected
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `_kb_attribution.py`, harness state,
  handoff logic, and env vars — instead of simply *opening an envelope*.
- **Evidence:** `bridge_claim_cli.py claim` → `claim_exit: 3` "not prime-eligible";
  `implementation_authorization.py begin` → `begin_exit: 2`. Resolved only when the envelope was
  opened (`python -m groundtruth_kb session envelope open`).
- **Fix (role definition):** add a one-line pre-flight to the Prime Builder overlay
  (`config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`) and `SESSION-STARTUP-INDEX.md`:
  *"Worker-role provenance requires an open session envelope; open one with
  `python -m groundtruth_kb session envelope open` before any KB-write or bridge claim."*
  This is a startup/envelope-action change, not a knowledge-base addition.

### 1.2 Bridge metadata required by `begin` (discovered one failure at a time)
- **What I searched for:** the full required-metadata set for `implementation_authorization begin`:
  `author_identity`, the `Responds to` chain, `target_paths` with concrete paths,
  `author_session_context_id` (for non-self-review), and a PAUTH reference.
- **Evidence:** **six** consecutive `begin` failures, each naming a new field (see Category 2.1).
- **Fix (skill):** these belong as a filing checklist in the frontmatter/body of
  `gtkb-bridge` / `gtkb-bridge-propose`. `scripts/bridge_applicability_preflight.py` already parses
  `target_paths` (line 64) and `Responds to` (line 70) — it is *most* of a validator; it simply is
  not run as the filing gate (see 2.1).

### 1.3 `backlog add-work-item` required argument set
- **What I searched for:** the full flag set (`--origin`, `--component`, `--priority`,
  `--project-name`, `--test-plan-phase`, `--test-type`, `--test-expected-outcome`,
  `--change-reason`, `--test-title`, `--source-spec-id`).
- **Evidence:** ten-plus failed invocations, each surfacing one missing flag.
- **Fix (skill / auto-load):** `gtkb-work-item` already exists and its `argument-hint` (line 4)
  lists these — but I had not loaded it. The work-item flow's activity envelope should auto-load
  `gtkb-work-item`. (Note the skill name itself was just renamed from `kb-work-item` →
  `gtkb-work-item`; verify any auto-load bundle references the new name.)

### 1.4 Valid `test-plan-phase` values
- **What I searched for:** valid phase IDs. Burned calls on `projects list`, help output, and a
  direct sqlite query before discovering `PHASE-001`…`PHASE-016`.
- **Evidence:** `test-plan-phase 'integration'` → GOV-13 failure; sqlite discovery of valid rows.
- **Fix (CLI + skill):** expose a `--list-phases` (or `groundtruth_kb backlog list-phases`)
  command; have `gtkb-work-item` cite valid phase IDs. Data-derived values must not require a DB
  dump.

### 1.5 `normalized_inventory_drift` remediation path
- **What I searched for:** how to regenerate the inventory baseline after the pre-commit hook
  blocked a commit.
- **Evidence:** `release_blocker` commit failure, then a search for
  `scripts/collect_dev_environment_inventory.py`.
- **Fix (hook output):** `scripts/check_dev_environment_inventory_drift.py` already imports the
  collector (line 152) — the fix path is known in-code. The FAIL message should print
  *"run `python scripts/collect_dev_environment_inventory.py`"*. (See 2.5.)

### 1.6 Per-harness skill-adapter generators (which exist, which don't)
- **What I searched for:** the generators for each projection surface, and the fact that cursor and
  goose had *none*.
- **Evidence:** Slice-3 "generators failed, hardcoded old path" cluster; eventual parity gaps that
  became WI-5641/5642.
- **Fix (skill):** `gtkb-harness-parity-review` should enumerate per-harness generator scripts and
  flag harnesses that declare capabilities but have no generator. (See 4.4.)

### 1.7 Terminology: session id ≠ worker-role provenance
- **What I conflated:** I set an ad-hoc `GTKB_SESSION_ID` and assumed it satisfied provenance. It
  does not — provenance is a property of an *open session envelope*, not an env var.
- **Evidence:** the provenance-rejection loop (1.1). The error message ("Worker role provenance
  session id does not match the current session") nudged me toward comparing ids rather than toward
  opening an envelope.
- **Fix (terminology + error text):** `canonical-terminology.md` defines *session envelope* (§901)
  and *activity envelope* (§258) separately, but has no entry binding "worker-role provenance" to
  "the thing an open session envelope provides." Add one; and/or make the error name the envelope.
  (See 3.1.)

---

## Category 2 — GOV overhead that can be safely mitigated (front-load, don't weaken)

None of these change *what* is enforced — only *when* and *by whom*. This is the safe-mitigation
category.

### 2.1 Unify preflight and `begin` validation into one filing gate (highest leverage)
- **Problem:** `bridge_applicability_preflight.py` parses `target_paths` and `Responds to`, but
  `implementation_authorization.py begin` *separately re-validates* those **plus**
  `author_identity`, the `Responds to` chain, `author_session_context_id`, and PAUTH. I hit each as
  a separate `begin` failure — **six** round-trips after GO.
- **Evidence (transcript):** the `begin` failure sequence:
  missing `author_identity` (001/003) → missing `author_identity` (002) → missing `Responds to`
  (002) → `Responds to` pointed at NO-GO (003) → self-review check (002) → missing `target_paths`
  (003) → missing PAUTH.
- **Recommendation:** run the full validator set at *filing* time (NEW/REVISED), so a proposal is
  rejected once, completely, *before* any review cycle — not after GO. **Safe because the rules do
  not change; only when they are checked does.**

### 2.2 Auto-stamp mechanical bridge metadata
- **Problem:** `author_identity`, `Responds to`, and `author_session_context_id` are derivable from
  the resolved session role and the responding-to file, yet I edited them by hand into 001–004.
- **Recommendation:** a filing helper (extend `bridge_claim_cli` or a new filing-time writer)
  stamps them at write time. **Safe because they are mechanical facts, not judgments.**
- **Existing assets:** `scripts/bridge_author_metadata.py`, `scripts/bridge_metadata_audit.py` —
  inspect before building; much of this likely exists.

### 2.3 Auto-resolve the PAUTH reference
- **Problem:** when `target_paths` classify into a protected class and an active PAUTH already
  covers it, `begin` fails with "Project Authorization is required." I had to run
  `projects authorizations <id>` and read the envelope to find the right PAUTH.
- **Recommendation:** `begin` (or preflight) surfaces the matching PAUTH id(s). **Safe because it
  is lookup, not grant.**

### 2.4 The `target_paths` classification footgun
- **Problem:** `groundtruth-kb/templates/skills/**` → `unclassified`, but
  `.../**/*.md` → `governance_evidence`. I only passed `begin` by refining the glob.
- **Recommendation:** the classifier warns at preflight that a path is unclassified, or
  auto-suggests the most-specific classifiable sub-pattern. **Safe because it removes a
  trial-and-error loop, not a control.**

### 2.5 Make the drift hook self-remediating
- (See 1.5.) `check_dev_environment_inventory_drift.py` should print its own remediation command
  in the FAIL message. **Safe because the collector already exists and is imported.**

### 2.6 Atomic WI creation + project linkage
- **Problem:** `add-work-item` then `projects add-item` is two commands with two failure surfaces
  (I failed the first on missing `--change-reason`, then `begin` failed because the WI was not a
  project member).
- **Recommendation:** a `--project` flag on `add-work-item` (or a wrapper) makes WI creation
  atomic. **Safe because it is the same two DB writes, just ordered.**
- **Caution:** `gt backlog` already has `authorize-implementation` and `repair-work-item-test-link`
  subcommands — confirm the seam before adding a flag.

---

## Category 3 — Terminology / role / procedure confusion

### 3.1 Session id ≠ worker-role provenance
- (See 1.7.) The central procedural error of the session. Fix via a glossary entry in
  `canonical-terminology.md` and/or an error message that names the envelope, not the id.

### 3.2 `unclassified` mutation class
- Not in the working vocabulary; I read `classify_target` to learn it exists. Either add it to the
  operating-model glossary or make `begin` explain it (see 2.4).

### 3.3 Bridge `Responds to` chain semantics
- I wrote `Responds to: ... (NO-GO)` and `begin` rejected it because a NO-GO cannot be
  responded-to as if it were a GO. The rule is correct (a REVISED responds to the NO-GO; the chain
  must point at a GO for `begin`), but the prose in the bridge files did not encode it.
- **Fix:** a one-line note in `gtkb-bridge`: *"`Responds to` for `begin` must resolve to the GO
  document."*

---

## Category 4 — Other opportunities (CLI / skill / context / generator)

1. **CLI:** `gtkb-work-item --list-phases` (or `gt backlog list-phases`) — see 1.4.
2. **CLI:** `gt projects authorizations <id> --covers-path <path>` — answer "which PAUTH covers this
   target" directly (see 2.3).
3. **Skill:** author a `gtkb-skill-rollout` (or extend `gtkb-managed-skill-adoption-review`)
   capturing the rename playbook: rename canonical → update rename-map → fix
   `canonical_source`/`surface` paths → fix frontmatter → regenerate adapters → clear stale
   on-disk dirs → run parity. The stale-`surface`-path (21) and stale-on-disk-dir (46 deletions)
   bugs were both "the rename didn't cascade"; a checklist makes it repeatable.
4. **Skill:** `gtkb-harness-parity-review` should list per-harness generator scripts and flag
   harnesses with declared capabilities but no generator (cursor/goose) — see 1.6.
5. **Generator hygiene:** the rename surfaced 21 stale `surface` paths and 46 stale on-disk dirs
   that parity only flagged as `EXTRA`/`MISSING` *after* the fact. A `check_harness_parity
   --strict-on-rename` (or a pre-commit coupling of rename-map → parity) catches the cascade at
   commit time.
6. **Context/startup:** the PB overlay should carry the "open a session envelope" pre-flight line,
   and the work-item flow should auto-load `gtkb-work-item`. Both are envelope-action changes, not
   new docs — see 1.1, 1.3.

---

## Recommended program structure (for the implementing PB)

Group into independent, separately-GO-able slices so no single proposal is umbrella-large:

- **Slice A (validation front-load):** 2.1 (filing-gate validator) + 2.2 (auto-stamp) +
  2.3 (PAUTH resolve) + 2.4 (unclassified warn). Highest leverage; touches
  `bridge_applicability_preflight.py`, `implementation_authorization.py`, `bridge_claim_cli.py`.
- **Slice B (startup & knowledge surfacing):** 1.1 (envelope line) + 1.3/1.6 (auto-load
  `gtkb-work-item`) + 3.1/3.2/3.3 (terminology). Cheap, high ROI.
- **Slice C (CLI affordances):** 1.4 (list-phases) + 4.2 (covers-path) + 2.6 (atomic WI+project).
- **Slice D (drift & generator hygiene):** 2.5 (hook remediation text) + 4.3 (skill-rollout
  playbook) + 4.4 (parity skill generator map) + 4.5 (strict-on-rename).

Each slice is independently reviewable; recommend one implementation proposal per slice (or per
two adjacent slices) rather than one umbrella proposal, to avoid the multi-round GO friction this
very session exhibited.

## Existing assets to inspect before building (avoid duplicate effort)
- `scripts/bridge_applicability_preflight.py` — already parses `target_paths` (L64), `Responds to`
  (L70); emits a packet hash. Closest existing filing-gate candidate.
- `scripts/implementation_authorization.py` — the `begin` validator (arg defs ~L2829-2861).
- `scripts/bridge_author_metadata.py`, `scripts/bridge_metadata_audit.py`,
  `scripts/bridge_review_independence.py` — metadata and independence helpers; likely reusable for
  2.2.
- `scripts/check_dev_environment_inventory_drift.py` — imports collector (L152); add remediation
  text.
- `scripts/check_harness_parity.py` — parity states; add strict-on-rename / generator-map output.
- `scripts/collect_dev_environment_inventory.py` — the regeneration entry point.
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` — envelope open/show/packet.
- `gtkb-work-item`, `gtkb-bridge`, `gtkb-harness-parity-review`,
  `gtkb-managed-skill-adoption-review` skills — auto-load and checklist targets.

## Relevant governance records to consult
- `GOV-FILE-BRIDGE-AUTHORITY-001` (who may author which status tokens).
- `GOV-12` / `GOV-13` (work-item test-spec and test-plan-phase requirements).
- `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`,
  `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
  (session-role / provenance model underlying 1.1 / 1.7).
- `canonical-terminology.md` §258 (activity envelope), §901 (session envelope) for 3.1.

## Backlog cross-check (avoid duplication)
A `gt backlog list` scan surfaced no existing WI that front-loads bridge validation, auto-stamps
bridge metadata, surfaces the session-envelope open step, lists test-plan phases, or adds PAUTH
path lookup. Nearest-adjacent (do **not** duplicate, cite as related):
- WI-4726 (fast-lane bridge threads cite WI + doctor check) — bridge-metadata hygiene, adjacent.
- WI-5010 (gt CLI changed_by attribution vs session-stated role) — touches the same attribution /
  provenance seam as 1.1/1.7.
- WI-5177 (bridge state-report classifier fallback) — bridge classification, adjacent.
- WI-5533 (session-envelope active_work_item_id defaults) — session-envelope surface, adjacent.
- WI-4832 (bridge thread→WI linkage reconciliation) — linkage, adjacent to 2.6.
No conflict detected; these should be cross-referenced in any implementation proposal.

## target_paths
(read-only advisory; no mutation targets. Implementation proposals under Slices A–D will declare
their own target_paths, expected to touch: `scripts/bridge_applicability_preflight.py`,
`scripts/implementation_authorization.py`, `scripts/bridge_claim_cli.py`,
`scripts/check_dev_environment_inventory_drift.py`, `scripts/check_harness_parity.py`,
`config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, `config/agent-control/SESSION-STARTUP-INDEX.md`,
`.claude/rules/canonical-terminology.md`, and the listed `gtkb-*` skill directories.)
