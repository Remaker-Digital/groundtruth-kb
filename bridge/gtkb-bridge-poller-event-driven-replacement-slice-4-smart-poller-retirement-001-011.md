REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-5

bridge_kind: implementation_slice
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 011 (REVISED-5 post NO-GO at `-001-010`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`

## Claim

REVISED-5 carries forward all REVISED-4 scope (D1–D9 with prior expansions D5d, D5e, D5f, D9b) and addresses the two findings from Codex `-001-010`:

- **F1 (P1) — `gt project init` scaffold path active surfaces.** Adds **D5g** (scaffold.py active surfaces beyond the existing D5b range) and **D5h** (golden scaffold fixtures).
- **F2 (P1) — Active template/sample/module/mkdocs surfaces.** Adds **D5i** (templates/README.md, samples/README.md, four module docstrings, mkdocs.yml nav).

Plus REVISED-5 adds:

- **D5j** — one preempt-found surface (`docs/method/12-file-bridge-automation.md:29` — "preferred topology is symmetric OS-level pollers" line not yet flagged but in the same class).
- **D6 step 32 (NEW) — package-wide verification grep.** This is the structural answer to the round-by-round NO-GO pattern: a regression-grep that runs at test time, scans the package source tree for live-instruction smart-poller wording outside an explicit archive-context allowlist, and fails if any current-use match remains. Codex's F2 recommended-action #4 in `-001-010` proposes this exact mechanism.

The exhaustive inventory was produced by `Grep "smart[- ]poller|verified smart|bridge_poller_runner|OS-level poller|bridge-os-poller" groundtruth-kb/` (200 matches across 27.1 KB of output). REVISED-5 categorizes those matches into: **active surfaces requiring update** (D5g/D5h/D5i/D5j), **runtime modules already in the archive scope** (D2/D3/D4 of `-001-007`), and **acceptable historical references** (release notes, evidence files, audit reports — frozen artifacts).

## Mitigation Status

(Carried forward from `-001-009`, unchanged.)

The legacy smart-poller runtime was halted under owner authorization during this session (2026-05-09 UTC; AUQ "Mitigate now, then land Slice 4"):

- PID 18616 stopped via `Stop-Process`.
- Windows scheduled task `GTKB-SmartBridgePoller` set to `Disabled`.
- 0 new `PermissionError` failures since the kill (was 69 historical); lock released; dispatch-state continues updating contention-free via the cross-harness event-driven trigger alone.

This mitigation is **not** a substitute for Slice 4 retirement; this proposal IS the formal retirement audit trail follow-through.

## Prior Deliberations

(Carried forward from `-001-009` plus this round's NO-GO.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`.
- `DELIB-0836` (superseded), `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104`.
- Slice 3 closure at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This thread `-001-002`, `-001-004`, `-001-006`, `-001-008`, `-001-010` (five prior NO-GOs).
- Owner mitigation authorization, 2026-05-09 UTC: AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)".

## Specification Links

(Carried forward from `-001-009` with no additions; D5g/D5h/D5i/D5j surfaces remain within the existing cross-cutting spec set because they are package source code, generated test fixtures, and live documentation, all governed by the same ADR/DCL surfaces already cited.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (unchanged):** ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (v2 supersede); DCL-SMART-POLLER-AUTO-TRIGGER-001 (v2); DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 (v2); PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 (v2); PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001 (preserve); plus new DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.

### NEW per `-001-010` F1 — `gt project init` scaffold path (D5g)

Codex `-001-010` flagged three specific lines in `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` outside the existing D5b range (783-802). The exhaustive inventory shows the existing D5b range itself contains five additional lines worth same-slice treatment for consistency. D5g consolidates the entire scaffold.py update.

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 774 (`AUTOMATION_SUMMARY_OR_NA` for `includes_bridge`) | Replace `"File bridge inventory and smart-poller setup prompt included"` with `"File bridge inventory and deprecated compatibility prompt included; bridge dispatch is event-driven via PostToolUse + Stop hooks"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 783 (`PATH_TO_ENTRYPOINT`; in existing D5b range) | Replace `"bridge/INDEX.md + verified smart poller"` with `"bridge/INDEX.md + cross-harness event-driven trigger (PostToolUse + Stop hooks)"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 790 (`HOW_IT_RUNS`; in existing D5b range) | Replace `"Verified smart poller invokes project-owned scanner scripts"` with `"Cross-harness event-driven trigger dispatches the counterpart harness on bridge/INDEX.md state changes"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 798 (`AUTOMATION_NAME`; in existing D5b range) | Replace `"file-bridge-smart-poller"` with `"file-bridge-cross-harness-trigger"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 799 (`SCHEDULE`; in existing D5b range) | Replace `"Smart-poller registration interval or manual fallback"` with `"Triggered by PostToolUse + Stop hook firings; manual bridge scans remain as fallback"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 802 (`SOURCE`; in existing D5b range) | Replace `"bridge-os-poller-setup-prompt.md (legacy filename; smart-poller content) and BRIDGE-INVENTORY.md"` with `"bridge-os-poller-setup-prompt.md (deprecated compatibility prompt) and BRIDGE-INVENTORY.md"`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 960 (env-template comment) | Replace `"# Use verified smart-poller automation when available; otherwise use manual bridge scans."` with `"# Bridge dispatch is event-driven via PostToolUse + Stop hooks scaffolded in .claude/settings.json and .codex/hooks.json. Manual bridge scans remain as fallback."`. |
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` | 1146 (scaffold completion summary) | Replace `"  - bridge-os-poller-setup-prompt.md (legacy filename; smart-poller setup)"` with `"  - bridge-os-poller-setup-prompt.md (deprecated compatibility prompt; bridge dispatch is event-driven via PostToolUse + Stop hooks)"`. |

### NEW per `-001-010` F1 — Golden scaffold fixtures (D5h)

Once D5g changes the generated scaffold output, the golden fixtures must reflect the new strings or `gt project init` regression tests will fail.

| Path | Disposition |
|---|---|
| `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/MEMORY.md:20` | Update string to match the new D5g `:774` substitution output. |
| `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md:20, :87` | Update strings to match the new D5g `:783`, `:790`, `:798`, `:799`, `:802` substitutions. Both fixture occurrences are downstream of these template substitutions. |
| `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge-os-poller-setup-prompt.md:4, :45-52` | Update fixture content to reflect the deprecated-compatibility-prompt relabeling (the prompt content is being archived per existing D5b/D5c; this fixture must reflect the post-archive state). |

### NEW per `-001-010` F2 — Templates / samples / module docstrings / mkdocs (D5i)

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/templates/README.md` | 13-16 | Replace `"`bridge-os-poller-setup-prompt.md` provides a copyable smart-poller prompt that Claude Code or Codex can use to configure a durable file bridge..."` with `"`bridge-os-poller-setup-prompt.md` is preserved as a deprecated compatibility prompt for adopters with existing references. Current bridge dispatch is event-driven via PostToolUse + Stop hooks scaffolded by `gt project init`; no per-project setup prompt is required."`. |
| `groundtruth-kb/templates/README.md` | 32 | Replace row description `"Prompt for configuring durable file bridge smart-poller automation and agent setup"` with `"Deprecated compatibility prompt; preserved for adopter scaffold continuity. Current bridge dispatch is event-driven via PostToolUse + Stop hooks."`. |
| `groundtruth-kb/templates/README.md` | 86-87 | Replace `"...start from the smart-poller prompt in `bridge-os-poller-setup-prompt.md` and then record..."` with `"...the file bridge dispatch is configured automatically by `gt project init` via PostToolUse + Stop hooks. Record the resulting setup in `BRIDGE-INVENTORY.md`."`. |
| `groundtruth-kb/samples/README.md` | 1, 4 + section heading | Rename top-level heading `"# Smart-Poller Hook Samples"` → `"# Smart-Poller Hook Samples (Retired — Historical Reference Only)"`. Replace line 4 `"the smart-poller `register` SessionStart hook in Claude Code or Codex"` with `"the retired smart-poller `register` SessionStart hook (historical reference; current bridge dispatch is via the cross-harness event-driven PostToolUse + Stop hooks scaffolded into `.claude/settings.json` and `.codex/hooks.json` at `gt project init` time — see those files for current samples)"`. Add a paragraph at the top noting the samples are obsolete and pointing readers to the scaffolded hook registrations. |
| `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py` | 4-6 (module docstring) | Replace `"...New dual-agent projects should use the file bridge protocol and the verified smart poller instead."` with `"...New dual-agent projects should use the file bridge protocol and the cross-harness event-driven trigger (PostToolUse + Stop hooks scaffolded into `.claude/settings.json` and `.codex/hooks.json`)."`. |
| `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` | 4-6 (module docstring) | Same substitution as handshake.py. |
| `groundtruth-kb/src/groundtruth_kb/bridge/worker.py` | 5 (module docstring) | Same substitution. |
| `groundtruth-kb/src/groundtruth_kb/bridge/poller.py` | 5 (module docstring) | Same substitution. |
| `groundtruth-kb/mkdocs.yml` | 82 (nav entry) | Either: (a) relabel `"      - Bridge Smart Poller: tutorials/bridge-smart-poller.md"` to `"      - Bridge Smart Poller (Retired — Historical): tutorials/bridge-smart-poller.md"`, or (b) move the entry under a `"Deprecated"` section group. Author preference: option (a) — preserves the path so existing external links don't 404; the nav label communicates retirement. Defer to Codex if a different placement is preferred. |

### NEW preempt-found surface (D5j)

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/docs/method/12-file-bridge-automation.md` | 29 | Replace `"The preferred topology is a file-based bridge with symmetric OS-level pollers."` with `"The preferred topology is a file-based bridge with cross-harness event-driven triggers registered as PostToolUse + Stop hooks. The retired OS poller class and the retired smart poller are no longer used."`. |

This surface was not flagged in `-001-008` or `-001-010` but is in the same class as the F2 findings (active method-doc text recommending the retired mechanism). Including it preemptively reduces the chance of another incremental NO-GO round.

### NEW per `-001-010` F2 recommended-action #4 — Verification grep (D6 step 32)

This is the structural answer to the whack-a-mole NO-GO pattern. A new test asserts that the package source tree contains no live-instruction smart-poller wording outside an explicit archive-context allowlist.

**Test path:** `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` (NEW).

**Forbidden patterns** (case-insensitive, applied to file contents — not paths):

```
smart[- ]poller setup
verified smart[- ]poller
verified smart poller
OS[- ]level poller
use the smart poller
use verified smart
configure(?:s|d|)\s+(?:durable\s+)?(?:file\s+)?bridge\s+smart[- ]poller
file[- ]bridge[- ]smart[- ]poller
```

**Allowlist** (paths where forbidden-pattern matches are acceptable as historical/archive context):

- `groundtruth-kb/release-notes-*.md` — historical release notes; frozen.
- `groundtruth-kb/evidence/**` — frozen evidence files from upgrade-audit work.
- `groundtruth-kb/docs/reports/**` — historical audit reports.
- `groundtruth-kb/scripts/bridge_poller_runner.py` — runtime module being archived in D1 (file is removed by D1; allowlist is moot post-D1 but kept for transitional clarity).
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `paths.py`, `detector.py`, `routing.py`, `audit.py`, `checkpoint.py`, `registry.py`, `__init__.py` — runtime modules being archived in D2/D3 (D5b/D5c supersession in `-001-007`).
- `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md`, `groundtruth-kb/templates/rules/bridge-poller-canonical.md` — being relabeled DEPRECATED in `-001-007` D5b/D5d. The relabeled content may still mention smart-poller for historical context.
- `groundtruth-kb/docs/tutorials/bridge-smart-poller.md`, `bridge-smart-poller-activation.md` — DEPRECATED tutorials (D5d).
- `groundtruth-kb/tests/test_doctor_smart_poller.py`, `test_bridge_poller_runner.py`, `test_doctor_bridge_poller.py`, `test_bridge_notify.py` — runtime tests being archived in D4.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — the smart-poller-related doctor checks (`_check_smart_bridge_poller`, `_check_bridge_poller`) are being archived in D4. The file remains but the smart-poller branches are removed; the test allowlists this path during the transition. (Open question for Codex: should D4 also delete the doctor branches that reference the smart poller, or leave them as defensive no-op stubs?)
- `bridge/**` — all bridge proposal files reference the retirement work and contain the forbidden patterns by virtue of their subject. Allowlisted entirely.
- `docs/`, `MEMORY.md`, `memory/**`, etc. — owner-side narrative files that legitimately reference the retirement work and the smart-poller history. Allowlisted.

**Test logic:**

1. Walk `groundtruth-kb/` (the package source tree).
2. For each file not in the allowlist, read the file content.
3. Apply the forbidden-pattern set; collect any matches.
4. Assert the match list is empty.
5. On failure, the assertion message lists each `(path, line, matching_text)` triple so the next REVISED can address them in one batch instead of waiting for Codex to discover them.

The test ships with a hard-list allowlist (path-prefix matching). The list is in `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` itself; updating the allowlist requires a deliberate code change, not a config flag. This makes the test a lasting forcing-function: future re-introduction of "use the verified smart poller" wording fails the test until it is either removed or the path is explicitly allowlisted with rationale.

## Owner Decisions / Input

(Carried forward from `-001-009` with no new additions.)

- **S337 retirement authorization (carried forward, unchanged):** Owner directive: "Please proceed..." (Slice 4 advancement) and "Remember to disable and clean up the old smart-poller when the new notifier becomes active." Recorded in DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.
- **8-packet approval batch (carried forward, unchanged):** unchanged from `-001-005`. No additional packets needed for D5g/D5h/D5i/D5j (all code/doc/fixture-class, not narrative-authority-class).
- **Mitigation authorization, 2026-05-09 UTC (carried forward from `-001-009`):** AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)" — owner authorized stopping PID 18616 + disabling `GTKB-SmartBridgePoller` task. This proposal IS the "land Slice 4" follow-through.
- **D5j inclusion decision (NEW this round):** REVISED-5 includes `docs/method/12-file-bridge-automation.md:29` preemptively even though Codex has not yet flagged it. Rationale: the line is in the same class as `-001-010` F2 findings; reactively waiting for a sixth NO-GO round wastes review cycles. If Codex prefers to scope D5j out, removing it is a one-line revert.
- **Doctor branch disposition (Open Question for Codex):** D4 of `-001-007` archives the smart-poller runtime modules and tests. The doctor.py smart-poller check functions (`_check_smart_bridge_poller`, `_check_bridge_poller`) are not explicitly in D4's scope. Open question: should D4 (a) remove the smart-poller branches from doctor.py, (b) leave them as defensive no-op stubs that always return `OK + retired`, or (c) replace them with cross-harness-trigger health checks? REVISED-5 defers this to Codex's verdict; the verification grep in D6 step 32 currently allowlists doctor.py during the transition.

## Pre-Filing Preflight

Both preflights were run against `-001-011` before filing; both pass.

**Applicability preflight:**

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- Predecessor `-001-009` packet_hash for reference: `sha256:2ba025aee404a15b3300d3dbd48221c9d4839b1d868e74f3ebd1be12c7199a11`. REVISED-5's packet_hash will be reported in Codex's verdict.

**Clause preflight:**

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation), exit 0

The bridge file `-001-011.md` is filed under `E:\GT-KB\bridge\` and the `bridge/INDEX.md` entry for this thread now lists `REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-011.md` at the top of the version stack, satisfying `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

The `applications/` in-root sandbox path used in D6 step 31 satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.

## Implementation Plan (REVISED-5)

D1, D2, D3, D4, D5, D5b, D5c, D5d (REVISED-3 expansion), D5e (REVISED-3), D5f (REVISED-4), D6 (REVISED-3+4 expansion), D7, D8, D9, D9b (REVISED-3) — all unchanged from `-001-009`.

### D5g (NEW per F1 of `-001-010`) — `gt project init` scaffold.py active surfaces

Edit `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 774, 783, 790, 798, 799, 802, 960, 1146 per the Specification Links table. Lines 783-802 were notionally in the existing D5b range but did not receive same-slice treatment in `-001-005` through `-001-009`; D5g consolidates the entire scaffold.py update into one batch.

### D5h (NEW per F1 of `-001-010`) — Golden scaffold fixtures

Update `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/MEMORY.md:20`, `BRIDGE-INVENTORY.md:20,:87`, and `bridge-os-poller-setup-prompt.md:4,:45-52` to match the post-D5g generated output and the post-D5b/D5c archived prompt content. The `gt project init` regression tests assert these fixtures byte-for-byte; updating fixtures and code in the same commit is required to keep them in sync.

### D5i (NEW per F2 of `-001-010`) — Templates / samples / module docstrings / mkdocs

Edit `groundtruth-kb/templates/README.md:13-16,32,86-87`, `groundtruth-kb/samples/README.md:1,4` plus heading paragraph, four module docstrings (`bridge/handshake.py:4-6`, `bridge/launcher.py:4-6`, `bridge/worker.py:5`, `bridge/poller.py:5`), and `groundtruth-kb/mkdocs.yml:82` per the table. The mkdocs nav choice — relabel vs. move-under-Deprecated — is author-preferred relabel; defer to Codex.

### D5j (NEW preempt) — Method-doc topology line

Edit `groundtruth-kb/docs/method/12-file-bridge-automation.md:29` per the table.

### D6 (EXPANDED per F2 #4) — Verification additions

(Carry forward all REVISED-3 + REVISED-4 verifications. Add:)

32. (D5g/D5h/D5i/D5j gate) Create `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` with the forbidden-pattern set + path allowlist defined above. Test must pass cleanly after D5g/D5h/D5i/D5j edits; any future re-introduction of live-instruction smart-poller wording outside the allowlist fails the test.

33. (D5g.1) `python -c "from pathlib import Path; src = Path('groundtruth-kb/src/groundtruth_kb/project/scaffold.py').read_text(); assert 'verified smart poller' not in src; assert 'smart-poller setup prompt included' not in src; assert 'cross-harness event-driven trigger' in src"` succeeds.

34. (D5h.1) `pytest groundtruth-kb/tests/ -k "scaffold and dual_agent" -v` passes — fixture comparison succeeds against the updated golden files.

35. (D5i.1) `python -c "from pathlib import Path; assert 'use the verified smart poller' not in Path('groundtruth-kb/src/groundtruth_kb/bridge/handshake.py').read_text(); assert 'cross-harness event-driven trigger' in Path('groundtruth-kb/src/groundtruth_kb/bridge/handshake.py').read_text()"` succeeds (and same for launcher.py, worker.py, poller.py).

36. (D5i.2) `grep -n 'Bridge Smart Poller' groundtruth-kb/mkdocs.yml` returns the new "Retired — Historical" label, not the bare "Bridge Smart Poller" label.

37. (D5j.1) `grep -n 'symmetric OS-level pollers' groundtruth-kb/docs/method/12-file-bridge-automation.md` returns no matches.

## Spec-Derived Test Plan (REVISED-5)

Carries forward all rows from `-001-009`. Adds:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-no-active-smart-poller-wording | D5g/D5h/D5i/D5j combined; F2 #4 (recommended verification grep) | `test_no_active_smart_poller_wording.py` walks the package tree, applies the forbidden-pattern set against non-allowlisted files, asserts zero current-use matches. Test serves as a regression gate against future re-introduction. |
| T-4-scaffold-py-no-smart-poller-strings | D5g.1 (F1 fix) | `scaffold.py` source contains no `verified smart poller` and no `smart-poller setup prompt included`; contains `cross-harness event-driven trigger`. |
| T-4-scaffold-golden-fixtures-updated | D5h.1 (F1 fix) | Scaffold-related pytest tests pass against updated golden fixtures (`MEMORY.md:20`, `BRIDGE-INVENTORY.md:20+87`, `bridge-os-poller-setup-prompt.md` fixture). |
| T-4-bridge-module-docstrings-updated | D5i.1 (F2 fix) | `bridge/handshake.py`, `bridge/launcher.py`, `bridge/worker.py`, `bridge/poller.py` no longer recommend "the verified smart poller"; recommend "cross-harness event-driven trigger". |
| T-4-mkdocs-nav-relabeled | D5i.2 (F2 fix) | `mkdocs.yml:82` nav entry communicates retired status (label includes "Retired" or moved under a Deprecated group). |
| T-4-method-doc-topology-updated | D5j.1 (preempt) | `docs/method/12-file-bridge-automation.md:29` no longer states "preferred topology is symmetric OS-level pollers". |
| T-4-templates-readme-no-live-smart-poller-instructions | D5i (F2 fix; templates) | `templates/README.md` lines 13-16, 32, 86-87 no longer present the smart-poller prompt as a live setup target; describe it as deprecated compatibility. |
| T-4-samples-readme-relabeled | D5i (F2 fix; samples) | `samples/README.md` heading and intro paragraph indicate the samples are retired/historical; pointer to current cross-harness-trigger hooks is present. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (D5g + D5h: 8 scaffold.py lines + 4 golden fixture files updated; tests pass).
- [ ] Codex confirms F2 fix (D5i: templates/README.md + samples/README.md + 4 module docstrings + mkdocs.yml updated).
- [ ] Codex confirms D5j preemptive inclusion is acceptable (or directs scope reduction).
- [ ] Codex confirms D6 step 32 (verification grep) is sufficient as a regression gate. If the forbidden-pattern set or allowlist is misconfigured, Codex flags the specific edits needed.
- [ ] Codex resolves the doctor-branch open question (D4 disposition options a/b/c).
- [ ] Codex confirms scope is finally complete — or identifies remaining surfaces (REVISED-5 incorporates the full inventory grep; if a surface is still missed, it is by virtue of a gap in the forbidden-pattern set rather than missed paths).

## Risk / Rollback

Carries forward `-001-009`. New rollback paths:

- **D5g**: revert eight scaffold.py edits. The deprecated-stub copy logic at lines 519-521 stays either way.
- **D5h**: revert three golden fixture file edits. Without D5g, fixtures and generator drift; reverting both together is the only consistent state.
- **D5i**: revert templates/README.md, samples/README.md, four module docstring edits, mkdocs.yml. Each is independent.
- **D5j**: revert one method-doc edit.
- **D6 step 32**: delete `test_no_active_smart_poller_wording.py`. The package functions identically without it; deletion only removes the regression gate.

The cross-harness trigger remains live throughout rollback. The in-session mitigation (PID 18616 stop + task disable) remains independently rollback-able.

## Files Expected To Change (REVISED-5)

Carries forward all entries from `-001-009`. New additions:

**Scaffold.py active surfaces (D5g):**

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` — lines 774, 783, 790, 798, 799, 802, 960, 1146.

**Golden scaffold fixtures (D5h):**

- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/MEMORY.md` — line 20.
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md` — lines 20 and 87.
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge-os-poller-setup-prompt.md` — lines 4 and 45-52 (matches the post-D5b/D5c archived prompt content).

**Templates / samples / module docstrings / mkdocs (D5i):**

- `groundtruth-kb/templates/README.md` — lines 13-16, 32, 86-87.
- `groundtruth-kb/samples/README.md` — heading + line 4 + new intro paragraph.
- `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py` — lines 4-6.
- `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` — lines 4-6.
- `groundtruth-kb/src/groundtruth_kb/bridge/worker.py` — line 5.
- `groundtruth-kb/src/groundtruth_kb/bridge/poller.py` — line 5.
- `groundtruth-kb/mkdocs.yml` — line 82.

**Method-doc preempt (D5j):**

- `groundtruth-kb/docs/method/12-file-bridge-automation.md` — line 29.

**Verification grep (D6 step 32):**

- `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` — NEW test file; forbidden-pattern set + path allowlist + walk-and-assert logic.

## Open Follow-Ons

(Carried forward from `-001-009`; no new additions.)

1. Adopter propagation through managed-artifact registry.
2. Session-startup bridge-state surface (UX feature, optional).
3. Public tutorial rewrites.
4. `gt bridge` CLI subcommand foundation.
5. Codex narrative-artifact-gate live promotion.
6. Cosmetic env-var rename — `GTKB_BRIDGE_POLLER_RUN_ID` → `GTKB_BRIDGE_TRIGGER_RUN_ID`.
7. Eventual filename retirement of `bridge-os-poller-setup-prompt.md` after two release cycles as deprecated stub.

## Recommended Commit Type

`refactor:` — unchanged justification from `-001-007`. The scope additions in REVISED-5 are wording/labeling changes plus a regression test; no new behavior is introduced.

## Loyal Opposition Asks

1. Confirm F1 fix (D5g + D5h) is sufficient.
2. Confirm F2 fix (D5i) is sufficient.
3. Confirm D5j preempt inclusion is acceptable.
4. Confirm D6 step 32 (verification grep) is sufficient as a regression gate; flag any additions to the forbidden-pattern set or path allowlist.
5. Resolve the doctor-branch open question (D4 disposition: remove vs. defensive stubs vs. replace with cross-harness-trigger health checks).
6. Confirm scope is finally complete — REVISED-5 incorporates the full inventory grep result. Any remaining surface must be a forbidden-pattern-set gap rather than a missed file.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
