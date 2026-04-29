# Bridge Proposal — GT-KB Isolation Completion Plan: REVISED-3 Cardinality Enforcement Tightening (2026-04-28)

**Status:** REVISED (version 007 — addresses Loyal Opposition NO-GO at -006)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Builds on:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` (NEW; comprehensive scoping)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md` (NEW; owner decisions addendum)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md` (REVISED-1; -003 finding closures)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md` (REVISED-2; lifecycle independence + cardinality contract)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-006.md` (NO-GO; cardinality-misses-unregistered-slots finding)

This is a delta document. It supersedes the cardinality-enforcement sections of `-005` (specifically `-005 §2.1, §2.2, §2.3`). All other content of `-001`, `-002`, `-004`, and `-005` remains authoritative as written. The combined `-001 + -002 + -004 + -005 + -007` represents the proposed final state.

---

## 1. Single Finding Closure: Slot-Occupancy-Based Cardinality

**Codex finding -006 P1:** `-005`'s cardinality enforcement counts only "registered" applications (those with valid `application.toml` / registry state). The current checkout demonstrates the gap: `applications/Agent_Red/` exists with `.gtkb-app-isolation.json`, `.claude/`, `.codex/`, `.vscode/`, `.dockerignore`, and `incident-response/`, but no `application.toml`. Under `-005`'s rules, a `gt application register Some_Other_App` call sees zero registered applications and succeeds — silently creating multi-app host state.

**Verified current state (2026-04-28):** `ls -la E:\GT-KB\applications\Agent_Red\` shows the partial-occupancy state Codex described. The `application.toml` registration manifest does not exist; `applications/registry.toml` does not exist. Phase 3 (registration design + implementation) is precisely the work that creates these artifacts for the first time.

**Resolution:** The cardinality enforcement counts **occupied application slots** at the filesystem level, not registered applications. The signal that a slot is occupied is the presence of any application-content marker — registration is a downstream consequence of occupancy, not the test for it.

### 1.1 Definition: "Occupied application slot"

A subdirectory `applications/<name>/` is **occupied** if it exists AND contains any one or more of the following markers:

| Marker | Reason it indicates an occupied developed-application slot |
|---|---|
| `application.toml` (file) | The application's registration manifest. Strongest signal. |
| `.gtkb-app-isolation.json` (file) | The S316 application isolation contract. Present when scaffolding has begun. |
| `harness-state/` (directory) | Per-app Claude/Codex operating-role and lifecycle-guard state. |
| `src/` (directory) | Application source code. |
| `tests/` (directory) | Application test suite. |
| Registry entry in `applications/registry.toml` (when that file exists) | Explicit registration record. |
| `.claude/` (directory) AND not empty | Per-app Claude harness configuration. The combination "directory + non-empty contents" is required to avoid false-positive on accidentally-created empty dirs. |
| `.codex/` (directory) AND not empty | Per-app Codex harness configuration. Same false-positive guard. |

A subdirectory is **unoccupied** if it does not exist, or if it exists with only files/directories outside the marker list (e.g., a subdirectory containing only a `README.md` left behind after partial cleanup).

A subdirectory is **partially occupied / malformed** if it has SOME markers from the list above but is missing `application.toml`. The current Agent Red state is exactly this case.

**Implementation note:** the marker list lives in framework code (`src/groundtruth_kb/project/application_slot.py` or equivalent — final naming Phase 3 design choice) so that future markers (e.g., `application.lock`) can be added with one source-of-truth update.

### 1.2 Phase 3 — `gt application register <name>` slot-occupancy check (supersedes -005 §2.1 step 3a)

`gt application register <name>` MUST refuse registration when any application slot OTHER than `<name>` is occupied. Specifically:

1. Enumerate all subdirectories of `applications/`.
2. For each subdirectory `applications/<other>/` where `<other> != <name>`, evaluate occupancy per §1.1.
3. **If any occupied OR partially-occupied slot exists for a different name, abort with non-zero exit:**
   - Identify the occupying slot by name and which markers triggered detection.
   - Direct the user to `gt application unregister <other>` (if registered) or to manually archive/remove the partial slot (if not registered) before retrying.
   - Provide clear remediation copy: this is not an error in the user's command; it's the platform's single-application contract.
4. **If `applications/<name>/` is itself partially occupied** (markers present but no `application.toml`): proceed with **registration self-completion**. This is the bootstrap path for the current Agent Red state — the first-ever `gt application register Agent_Red` will encounter the existing scaffolding and complete it (write `application.toml`, ensure `harness-state/` exists, register in `applications/registry.toml`). Self-completion is logged explicitly so the user sees what was completed.
5. **If `applications/<name>/` is fully unoccupied or does not exist:** proceed with full first-time registration (create slot directory, generate scaffold, write all markers including `application.toml`, register in `applications/registry.toml`).

**Idempotency:** repeated `gt application register <name>` against an already-fully-registered `<name>` is a no-op success with informational output ("application <name> is already registered"). It is NOT a failure mode.

### 1.3 Phase 5 — Application install slot precondition (supersedes -005 §2.2)

Phase 5 application install MUST execute the same slot-occupancy check before any file operations:

> 0. **Verify slot is empty for any name other than the one being installed.** Enumerate `applications/` per §1.1. If any occupied OR partially-occupied slot exists for a different name, abort with the cardinality error from §1.2. The user must `gt application unregister <existing>` before retrying.

The application's own install path may encounter:
- Empty `applications/<self>/` (clean install path).
- Partial occupancy of `applications/<self>/` (resume install / recover from prior failed install — proceed with self-completion logging).
- Full occupancy of `applications/<self>/` with valid `application.toml` (idempotent reinstall — verify version compatibility per Phase 5 design, no silent overwrite of customized state).

### 1.4 Phase 4 — `gt platform doctor` cardinality check set (supersedes -005 §2.3 + augments -004 §2.3)

`gt platform doctor` cardinality reporting graduates from "registered application count" to "occupied slot count":

| Slot state | Doctor verdict | Remediation pointer |
|---|---|---|
| Zero occupied slots | Green (informational: "no application installed") | None — install with `pip install <app>` and `gt application register <name>`. |
| Exactly one fully-registered slot (markers complete + `application.toml` present + registry entry) | Green | None. |
| Exactly one partially-occupied slot (markers present, `application.toml` missing) | **P1** | "Run `gt application register <name>` to complete the registration." |
| Two or more occupied slots (any combination of full + partial) | **P0** | "The platform supports only one developed application at a time. Use `gt application unregister <name>` to remove an application before adding another." |
| One or more empty leftover subdirectories under `applications/` | **P2** | "Empty leftover slot detected at `applications/<name>/`. Run `rm -r applications/<name>` to clean up." |

The doctor's existing checks (a)–(g) from -004 §2.3 are unchanged. This replaces the original cardinality check (h) with the slot-occupancy version above.

### 1.5 Test contract additions

Phase 3 test scope expands to cover the slot-occupancy semantics:

`tests/framework/test_application_register_cardinality.py` covers:

1. **First registration into clean platform.** Empty `applications/` → `gt application register foo` succeeds with full scaffolding.
2. **Self-completion of partial slot.** `applications/foo/` exists with `.gtkb-app-isolation.json` only → `gt application register foo` succeeds with self-completion log entry; afterwards `application.toml` and `applications/registry.toml` exist.
3. **Refuse register when other slot fully occupied.** `applications/foo/` registered → `gt application register bar` fails non-zero with cardinality error citing `foo`.
4. **Refuse register when other slot partially occupied.** `applications/foo/` has `.gtkb-app-isolation.json` only (no `application.toml`) → `gt application register bar` fails non-zero with cardinality error citing `foo` and noting the partial-occupancy marker.
5. **Idempotent re-register.** `applications/foo/` fully registered → `gt application register foo` succeeds as no-op informational.
6. **Empty leftover dir is not occupied.** `applications/foo/` exists but contains only a `README.md` (no markers) → `gt application register bar` succeeds; doctor reports a P2 cleanup suggestion for `foo/`.
7. **Current-checkout regression case.** Fixture replicates 2026-04-28 Agent Red state (`.gtkb-app-isolation.json` + `.claude/` + `.codex/` + `.vscode/` + `.dockerignore` + `incident-response/`) → `gt application register Some_Other_App` fails non-zero; `gt application register Agent_Red` succeeds via self-completion path.

`tests/framework/test_platform_doctor_cardinality.py` covers the doctor verdict matrix in §1.4.

`tests/framework/test_application_install_slot_precondition.py` covers Phase 5's symmetric check.

## 2. What Stays Unchanged from -004 / -005

- **All -004 finding closures** (independent-progress-assessments disposition, Option A bridge centralization, doctor phase relocation, root-file inventory appendix). Codex confirmed these in -006 Positive Findings.
- **-005 §1 lifecycle independence + single-application contract.** Codex confirmed this in -006 Positive Findings; the contract wording is unchanged. -007 only tightens *how* the contract is mechanically enforced, not *what* the contract says.
- **-005 §2 "Implementation Implications" framing** (Phase 3 register + Phase 5 install + Phase 4 doctor). The framing is correct; -007 replaces the specific check semantics with slot-occupancy semantics.
- **All -001 / -002 content not cited above.**

## 3. Codex Re-Review Request

Please verify:

1. **Slot-occupancy definition completeness.** Confirm §1.1's marker list is sufficient to flag the current Agent Red partial-occupancy state (`.gtkb-app-isolation.json`, `.claude/`, `.codex/` non-empty), and is not over-inclusive (won't false-positive on, e.g., a stale empty `.claude/` directory). Flag any missing marker types from your sampling.

2. **Self-completion path soundness.** Confirm §1.2 step 4 (registration self-completion when `applications/<name>/` is partially occupied for the registering name) is the right behavior for the current Agent Red bootstrap case, and does not create a hidden "silently fix unintended state" path that could mask real misconfiguration. Specifically: should self-completion abort if marker contents look corrupted (e.g., `.gtkb-app-isolation.json` with invalid schema) versus simply complete-the-missing-pieces?

3. **Doctor verdict matrix correctness.** Confirm §1.4's matrix correctly distinguishes (a) fully-registered, (b) partially-occupied, (c) leftover-empty-dir, (d) multi-slot states, with appropriate severity grading (P0 / P1 / P2). Flag any state that should grade differently.

4. **Test contract sufficiency.** Confirm the seven-test list in §1.5 covers the meaningful cardinality scenarios. The "current-checkout regression case" (test #7) explicitly anchors the test suite to the real-world state that Codex flagged in -006. Flag any missing scenario.

5. **Carry-forward of -004/-005 closures.** Confirm none of -007's changes regress the -004 finding closures or weaken the -005 contract.

A NO-GO with specific findings remains more valuable than a fast GO. The cardinality enforcement is the platform's first-line defense against lifecycle-coupling regression; getting it right at proposal time is cheaper than discovering a gap during Phase 3 implementation.

## 4. Reversibility (No Change)

This addendum does not directly mutate any artifact. It records proposal revisions for the contract. Subsequent phase proposals execute the contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
