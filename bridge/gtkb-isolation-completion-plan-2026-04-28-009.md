# Bridge Proposal — GT-KB Isolation Completion Plan: REVISED-4 Default-Occupied Semantics + Self-Completion Validation (2026-04-28)

**Status:** REVISED (version 009 — addresses Loyal Opposition NO-GO at -008)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S319 (2026-04-28)
**Document name:** `gtkb-isolation-completion-plan-2026-04-28`
**Builds on:**
- `bridge/gtkb-isolation-completion-plan-2026-04-28-001.md` (NEW; comprehensive scoping)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-002.md` (NEW; owner decisions addendum)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-004.md` (REVISED-1; -003 finding closures)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-005.md` (REVISED-2; lifecycle independence + cardinality contract)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-007.md` (REVISED-3; slot-occupancy cardinality)
- `bridge/gtkb-isolation-completion-plan-2026-04-28-008.md` (NO-GO; default-occupied semantics + self-completion validation findings)

This is a delta document. It supersedes specific subsections of `-007` (specifically `-007 §1.1, §1.2 step 4, §1.5`). All other content of `-001`, `-002`, `-004`, `-005`, and `-007` remains authoritative as written. The combined `-001 + -002 + -004 + -005 + -007 + -009` represents the proposed final state.

---

## 1. Three Finding Closures

### 1.1 Finding -008 P1 #1: Default-occupied semantics (supersedes -007 §1.1)

**Problem:** -007's marker list was finite ("counts only what we recognize"). Future or current partial slots containing real application content (`.env.local`, `.shopify/`, `pdf-tooling/`, `incident-response/`, paired package files, deploy assets) could be misclassified as unoccupied if the recognized markers happened to be absent.

**Resolution:** Invert the occupancy model. Default to occupied; require explicit allowlist evidence for unoccupied.

#### 1.1.1 Definition: occupied vs. unoccupied (REVISED)

A subdirectory `applications/<name>/` is **occupied** when ANY of the following is true:

- (a) The directory contains a **strong marker** from §1.1.2 below, OR
- (b) The directory contains any file or subdirectory NOT explicitly allowlisted by §1.1.3, OR
- (c) `applications/registry.toml` exists at platform root AND contains an entry naming `<name>`.

A subdirectory is **unoccupied** only when ALL of the following are true:

- The directory does not exist, OR
- The directory exists but is empty, OR
- The directory exists but contains only allowlisted leftovers per §1.1.3, AND
- No registry entry references `<name>`.

This is a fail-closed invariant: anything we don't recognize as harmless is treated as occupancy requiring positive resolution.

#### 1.1.2 Strong markers (always indicate occupancy)

| Marker | Type | Reason |
|---|---|---|
| `application.toml` | file | Application registration manifest |
| `.gtkb-app-isolation.json` | file | S316 application isolation contract |
| `harness-state/` | dir (any contents) | Per-app Claude/Codex operating-role state |
| `src/` | dir (any contents) | Application source code |
| `tests/` | dir (any contents) | Application test suite |
| Registry entry in `applications/registry.toml` for `<name>` | record | Explicit registration |

The strong-marker list is retained from -007 §1.1 as a **diagnostic aid**, not the only path to occupancy. Doctor uses it for clearer error messages ("`<name>` is occupied because `application.toml` exists"); the cardinality check itself does not depend on it being exhaustive.

#### 1.1.3 Allowlisted leftovers (do NOT indicate occupancy on their own)

The following files and patterns may exist in `applications/<name>/` without triggering occupancy:

| Pattern | Reason it's harmless |
|---|---|
| (empty directory) | Standard placeholder |
| `.gitkeep` | Standard "preserve empty dir in git" file |
| `README.md` containing only a documented cleanup placeholder header | The file's only purpose is to document the slot-cleanup state |
| `.DS_Store`, `Thumbs.db`, `desktop.ini` | OS-generated metadata files |

The README.md exception requires the file to begin with the literal header string `<!-- gtkb-application-slot-cleanup-marker -->` on its first line. Any other README.md content triggers occupancy. This narrow exception prevents accidental occupancy from automated tooling that creates README placeholders, while requiring an explicit marker that says "this slot is intentionally a cleanup remnant."

The allowlist may grow only via owner-approved bridge proposal. Tooling additions that create new file types under `applications/<name>/` MUST either be added as strong markers OR remain unallowlisted (and thus trigger occupancy).

#### 1.1.4 Doctor diagnostic enhancement

When doctor detects occupancy, it reports the trigger:

- "Strong marker present: `application.toml`" → recommend register/unregister.
- "Strong marker present: `.gtkb-app-isolation.json`" → recommend register completion.
- "Non-allowlisted content present: `.env.local`, `package.json`, `pdf-tooling/`" → list the unrecognized contents so the operator sees exactly what's there.
- "Registry entry exists but no application directory" → registry drift; recommend `gt application unregister <name>` to clean registry.

### 1.2 Finding -008 P1 #2: Self-completion validation gate (augments -007 §1.2 step 4)

**Problem:** -007 §1.2 step 4 said registration of `<name>` against a partial slot for `<name>` proceeds with self-completion. But the partial slot might contain markers that name a *different* application, malformed JSON/TOML, or otherwise corrupted state. Self-completion would silently bless the corruption.

**Resolution:** Add a preflight validation step before self-completion proceeds.

#### 1.2.1 Self-completion preflight (NEW; inserted before -007 §1.2 step 4 actions)

When `gt application register <name>` encounters partial occupancy of `applications/<name>/`, it MUST run the following preflight before completing the registration:

1. **Parse all structured markers present** in the slot:
   - `application.toml` (TOML parse)
   - `.gtkb-app-isolation.json` (JSON parse + schema validation)
   - `applications/registry.toml` entry for `<name>` (TOML parse if present)
2. **Validate name consistency.** For each parsed marker:
   - `application.toml` MUST have `name == "<name>"` (or be absent).
   - `.gtkb-app-isolation.json` MUST have `application == "<name>"` (or be absent).
   - Registry entry MUST name `<name>` (or be absent).
3. **Validate schema.** Each parsed marker MUST conform to its known schema (current + supported prior versions). Unknown future schema version → warn and continue (forward compatibility); incompatible content → abort.
4. **Abort conditions** (all non-zero exit, with clear remediation):
   - Any structured marker fails to parse → "Malformed marker at `<path>`: <parser error>. Manually inspect or restore from backup."
   - Any structured marker names a different application → "Slot `applications/<name>/` contains marker `<path>` naming application `<other>`. This is a slot-name mismatch. Run `gt application register <other>` to claim it for `<other>`, or manually archive the slot if it should be removed."
   - Required schema field missing or invalid type → "Marker at `<path>` is schema-incompatible: <field> = <value>. Run `gt application repair <name>` (Phase 3 design) or manually edit and retry."
5. **Proceed conditions:** All parsed markers either match `<name>` or are absent. Self-completion writes `application.toml` (creating it if absent), ensures `harness-state/` exists, and adds the registry entry.

#### 1.2.2 Doctor reporting for malformed self-slot

`gt platform doctor` adds a new verdict cell to the §1.4 matrix (replacing the original P1 partial-occupancy cell):

| Slot state | Verdict | Remediation |
|---|---|---|
| One properly-registered slot for `<name>`, all markers consistent | Green | None |
| One partial slot for `<name>`, markers consistent (no `application.toml` yet) | **P1** | "Run `gt application register <name>` to complete registration." |
| One slot containing markers that name a different application `<other>` | **P1** | "Slot at `applications/<name>/` contains markers naming `<other>`. Run `gt application register <other>` (if `<other>` is the intended occupant) or archive the slot." |
| One slot with malformed structured markers (parse failure / schema-incompatible) | **P1** | "Malformed marker at `<path>`. Manual repair required before registration can proceed." |
| Two or more occupied slots (any combination) | **P0** | "Platform supports only one developed application at a time. Run `gt application unregister <name>` to remove an application." |
| Registry entry exists for `<name>` but `applications/<name>/` does not exist | **P2** | "Registry drift: registry references `<name>` but no slot directory exists. Run `gt application unregister <name>` to clean registry." |
| One or more empty leftover subdirectories | **P2** | "Empty leftover slot detected at `applications/<name>/`. Run `rm -r applications/<name>` to clean up." |
| Zero occupied slots, no registry drift | Green (informational) | None |

### 1.3 Finding -008 P2: Test contract expansion (augments -007 §1.5)

The `tests/framework/test_application_register_cardinality.py` and companion test files add the following scenarios (numbering continues from -007 §1.5):

8. **Non-marker app content blocks foreign register.** `applications/foo/.env.local` exists; no other content; `applications/registry.toml` does not exist → `gt application register bar` fails with non-allowlisted-content cardinality error citing `foo` and listing `.env.local`.

9. **Non-marker app content blocks foreign install.** `applications/foo/package.json` exists; no recognized marker → Phase 5 application install for `bar` fails with the same error.

10. **Malformed JSON marker blocks self-completion.** `applications/foo/.gtkb-app-isolation.json` contains invalid JSON → `gt application register foo` fails with parse-error remediation message; doctor reports P1 malformed-slot for `foo`.

11. **Mismatched marker name blocks self-completion.** `applications/foo/.gtkb-app-isolation.json` parses successfully but contains `"application": "Agent_Red"` → `gt application register foo` fails with mismatch-message naming both `foo` (slot) and `Agent_Red` (marker).

12. **Mismatched marker name blocks foreign register.** Same fixture as #11 → `gt application register bar` fails with cardinality error; doctor reports P1 (mismatched-slot occupancy by `Agent_Red` per `.gtkb-app-isolation.json`).

13. **Registry-only conflict blocks foreign register.** `applications/registry.toml` contains entry for `foo`; `applications/foo/` does not exist; `applications/bar/` does not exist → `gt application register bar` fails with cardinality error, OR doctor reports the registry drift first and registration is blocked until drift is resolved (Phase 3 owner-decision-deferred — flag as design choice during Phase 3 implementation, default to "report drift first, block registration").

14. **Schema-version forward compatibility.** `applications/foo/.gtkb-app-isolation.json` has `schema_version: "2.0"` (future version) but valid JSON, name matches `foo` → register proceeds with a forward-compatibility warning ("schema version 2.0 newer than supported 1.0; proceeding under best-effort interpretation").

15. **Allowlisted README cleanup-marker.** `applications/foo/README.md` containing the literal first line `<!-- gtkb-application-slot-cleanup-marker -->` and no other content → `gt application register bar` succeeds; doctor reports P2 cleanup suggestion for `foo`.

16. **Non-allowlisted README blocks register.** `applications/foo/README.md` containing arbitrary documentation (no cleanup-marker header) → `gt application register bar` fails with non-allowlisted-content cardinality error.

The combined test list (-007 tests 1–7 + -009 tests 8–16) covers: clean install, self-completion happy path, foreign-slot cardinality refusal (registered + partial + non-marker + mismatched-marker + registry-only + non-allowlisted-README), idempotent re-register, schema validation (parse error + name mismatch + forward-compat warning), and doctor severity grading across all matrix cells.

## 2. What Stays Unchanged from -004 / -005 / -007

- **All -004 finding closures** (independent-progress-assessments disposition, Option A bridge centralization, doctor phase relocation, root-file inventory appendix). Codex confirmed in -006 + -008 Positive Findings.
- **-005 §1 lifecycle independence + single-application contract.** Codex confirmed in -006 + -008 Positive Findings.
- **-007 §1.2 (Phase 3 register check) and §1.3 (Phase 5 install precondition) framing.** Codex confirmed the directional shift to slot-occupancy was correct in -008. -009 only tightens the semantics of "what counts as occupied" and adds the validation gate.
- **-007 §1.4 doctor verdict matrix structure.** -009 §1.2.2 augments the matrix with three new rows (mismatched-marker, malformed-marker, registry-drift) but does not regress the existing rows.

## 3. Codex Re-Review Request

Please verify:

1. **Default-occupied invariant correctness.** Confirm §1.1.1's three occupancy conditions (strong marker / non-allowlisted content / registry entry) cover all paths to occupancy. Flag any path Codex's sampling found that this definition still misses.

2. **Allowlist completeness.** Confirm §1.1.3's allowlist (empty dir, `.gitkeep`, README.md with cleanup-marker header, OS metadata) is the right narrow set. Specifically: should the OS metadata exemption be split (allowed vs. flagged-with-warning)? Should cleanup-marker README require additional structure beyond the first-line header?

3. **Self-completion preflight soundness.** Confirm §1.2.1's preflight steps (parse, name-validate, schema-validate, abort/proceed) close the malformed-slot gap. Specifically: is forward-compat warning (vs. abort) the right call for unknown schema versions? Are there structured markers the preflight should parse that are not in the current list?

4. **Doctor matrix completeness.** Confirm §1.2.2's eight verdict cells cover all distinguishable slot states. Flag any state that should grade differently or any combination not covered.

5. **Test contract coverage.** Confirm §1.3's tests 8–16 close the test-coverage gaps Codex identified. Test 13 (registry-only conflict) leaves an explicit Phase 3 design choice flagged for owner decision-or-default — confirm this is appropriate or call for an immediate decision.

6. **No regression of prior closures.** Confirm -009 does not weaken any -004 / -005 / -007 closure that Codex previously confirmed.

A NO-GO with specific findings remains more valuable than a fast GO. Each iteration narrows the gap; getting the cardinality contract precisely right at proposal time is cheaper than discovering a gap during Phase 3 implementation.

## 4. Reversibility (No Change)

This addendum does not directly mutate any artifact. It records proposal revisions for the contract. Subsequent phase proposals execute the contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
