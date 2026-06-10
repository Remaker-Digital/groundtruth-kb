REVISED

# Active-Workspace Declaration Architecture — REVISED-1

**Status:** REVISED (REVISED-1; supersedes -001 NO-GO at -002)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex Loyal Opposition NO-GO at `bridge/active-workspace-declaration-architecture-2026-04-29-002.md` identifying six blocking findings (F1: canonical state values inconsistent; F2: missing-record behavior conflicts with default; F3: per-harness precedence allows unauthorized divergence; F4: hosted-app boundary deadlocks bridge/governance writes; F5: enforcement coverage Claude-centric; F6: prompt handling doesn't fully encode interrogation contract). Plus spec-to-test mapping requirement.

This REVISED-1 addresses each blocking finding with surgical changes plus a complete spec-to-test mapping. The owner invariants from -001 §1 (default GT-KB; only hosted-application exception; no inference; interrogation; audit obligation) are preserved unchanged.

bridge_kind: prime_proposal
work_item_ids: [GTKB-ACTIVE-WORKSPACE-DECLARATION]
target_project: groundtruth-kb (with adopter-side propagation)
implementation_scope: governance + enforcement
requires_review: true
requires_verification: true

---

## Specification Links

(Mostly unchanged from -001 §Specification Links.) Additionally:
- **`.claude/rules/file-bridge-protocol.md`** — bridge protocol authority that F4 fix carve-out (control-plane allowlist) must preserve.
- **`.claude/rules/operating-role.md` lines 19-25** — explicitly cited per F3: distinguishes role/harness separation from workspace-identity authority.
- **`bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md`** (REVISED-1) — sister bridge defining the `parent` attribute on specs; vocabulary alignment intentional (both use `gt-kb` / `hosted-application` (or `application`) / `all`).

## Prior Deliberations

(Unchanged from -001.) Plus:
- **`bridge/active-workspace-declaration-architecture-2026-04-29-002.md`** (Codex NO-GO; recovered in commit `b693ba92`) — substance basis for this REVISED-1.

---

## Change Log Vs -001

| Change | Driving finding | Section |
|--------|-----------------|---------|
| Canonical states reduced to ONLY `gt-kb` and `hosted-application`; `hosted_application_id` added as separate field for app name | F1 | §1.1, §2.1 |
| Resolver redefined as fail-closed state machine; no inference fallback; missing/invalid → `gt-kb` (default) or block hosted-app op with diagnostic | F2 | §2.1, §2.7 |
| Per-harness records require owner-confirmation evidence; divergence surfaced at startup; fail-closed for enforcement | F3 | §2.1, §2.7 |
| Work-subject boundary separated from control-plane/audit boundary; explicit allowlist for `bridge/`, `harness-state/`, `.claude/rules/`, governance artifacts | F4 | §2.5 |
| Enforcement scope explicitly bounded to Claude Code in first impl; Codex protocol-only via review-gate; repo-native validator added for shell/script writes | F5 | §2.5, §2.6, §3 |
| Prompt handling: `gt-kb` is ONLY non-interactive transition; off-default prompts → single owner-question checkpoint; record updates only on canonical confirmation | F6 | §2.3 |
| Complete spec-to-test mapping added for each DCL/ADR + each edge case from Codex required revision | spec-test gate | §4 |

Sections 5, 6, 7 mostly unchanged from -001; substantive changes concentrated in §1, §2, §3, §4.

---

## §1. Workspace Model — Default + Exception (REVISED per F1)

### §1.1 Canonical State Vocabulary (per F1 fix)

**Two canonical states only.** Future hosted applications MUST NOT introduce new state values; their identity goes in the separate `hosted_application_id` field.

| State | Trigger | Description |
|---|---|---|
| **`gt-kb` (DEFAULT)** | Always, unless valid hosted-application exception declared | The GT-KB platform workspace. All work defaults here. |
| **`hosted-application` (EXCEPTION)** | Only after owner explicitly declares hosted-application work AND the durable record carries a valid `hosted_application_id` | Application-scope work. Path-bounded by §2.5 work-subject boundary; control-plane/audit writes still permitted per allowlist. |

**Removed:** any reference to `agent-red`, `Agent Red`, or other hosted-application names AS workspace values. Those are `hosted_application_id` values, never `active_workspace` values.

**Critical invariants (unchanged):**
- No third state. No "ambiguous" / "unknown" / "inferred" state.
- Absence of a valid hosted-application exception = `gt-kb`.
- The default is mechanically the answer when no valid override exists.

**Owner-declared exception triggers (per F6 fix; tightened):** the ONLY recognized canonical-confirmation prompt is exact-match against the question/answer flow defined in §2.3. Loose prompts like "set workspace to Agent Red" are rejected by the prompt handler with an interrogation question.

---

## §2. Architecture (REVISED)

### §2.1 Durable Record (Slice 1; REVISED per F1, F2, F3)

**Project-level record location:** `.claude/rules/active-workspace.md`

**Format (revised per F1):**
```markdown
# Durable Active-Workspace Record

active_workspace: gt-kb
hosted_application_id:    # empty unless active_workspace=hosted-application
declared_at: 2026-04-29T17:30:00+00:00
declared_by: owner
owner_confirmation_evidence:    # required when active_workspace=hosted-application; cite owner approval packet path
notes: GT-KB platform governance work.

## Change Log

- 2026-04-29 owner declared active_workspace=gt-kb (S321 platform work)
```

**`hosted_application_id` semantics (per F1 fix):**
- Empty string when `active_workspace=gt-kb`.
- Required non-empty value when `active_workspace=hosted-application` (e.g., `Agent_Red`).
- The resolver fails closed if `active_workspace=hosted-application` AND `hosted_application_id` is empty/missing.

**`owner_confirmation_evidence` semantics (per F2, F3 fixes):**
- Empty when `active_workspace=gt-kb` (no confirmation needed for default).
- Required non-empty value when `active_workspace=hosted-application` (cite owner approval packet path, e.g., `.groundtruth/formal-artifact-approvals/2026-04-29-hosted-app-toggle.json`).
- The resolver fails closed if `active_workspace=hosted-application` AND `owner_confirmation_evidence` is empty/missing.

**Per-harness records (per F3 fix):**
- Location: `harness-state/claude/active-workspace.md`, `harness-state/codex/active-workspace.md`.
- Per-harness records are EXPLICIT owner-declared session exceptions, NOT silent precedence overrides.
- Schema is identical to project-level, but `owner_confirmation_evidence` is REQUIRED if the per-harness record's `active_workspace` differs from project-level.
- Resolver behavior on harness/project divergence: see §2.7.

### §2.2 Inference Prohibition (Slice 2; unchanged from -001)

(Unchanged from -001 §2.2.) DCL prohibits inference; bridge proposals cite their workspace explicitly; Codex NO-GOs mismatched proposals.

### §2.3 Owner Toggle Prompts — Interrogation Contract (Slice 3; REVISED per F6)

**`gt-kb` is the ONLY non-interactive transition.**

**Recognized owner prompts:**

| Prompt pattern | Behavior |
|---|---|
| `set workspace to GT-KB` / `back to GT-KB` / `gt-kb workspace` | **Non-interactive.** Update durable record to `active_workspace=gt-kb`; clear `hosted_application_id` and `owner_confirmation_evidence`. Append change log entry. Confirm to owner. |
| Any other prompt suggesting off-default work (e.g., mentions of an app name, paths under `applications/`, `set workspace to <anything>`) | **Interrogation question.** Hook produces a single owner-question checkpoint via AskUserQuestion: "You signaled potential hosted-application work. Confirm by stating: 'we are working on the hosted application <id>' (where <id> is the application identifier, e.g., Agent_Red). Or restate 'set workspace to GT-KB' to remain in default." Hook does NOT update the durable record until the canonical confirmation is received. |
| Exact match: `we are working on the hosted application <id>` (where `<id>` is non-empty) | **Canonical confirmation.** Hook prompts owner for `owner_confirmation_evidence` path (or auto-creates one and cites it). Update durable record: `active_workspace=hosted-application`, `hosted_application_id=<id>`, `owner_confirmation_evidence=<path>`. Append change log. Confirm to owner. |

**Mechanism:**
- `.claude/hooks/active-workspace-tracker.py` (new UserPromptSubmit hook) handles all three patterns.
- Update is atomic (write new content + change log entry in one operation).
- All updates also write a deliberation row to KB capturing the owner statement.

### §2.4 Bridge Proposal `Active Workspace:` Field (Slice 4; mostly unchanged from -001)

(Mostly unchanged from -001 §2.4.) Bridge proposals must include `**Active Workspace:** gt-kb` (or `hosted-application` with the `hosted_application_id`). Codex NO-GOs proposals where the declared workspace doesn't match the durable record.

### §2.5 File-Write Boundary Enforcement — Two Boundaries (Slice 5; REVISED per F4, F5)

**Per F4 fix: separate work-subject boundary from control-plane/audit boundary.**

**Two boundaries enforced by the boundary-gate hook:**

**Boundary A — Work-subject boundary** (application source code):
- When `active_workspace=hosted-application` AND `hosted_application_id=Agent_Red`: writes to `applications/Agent_Red/src/**`, `applications/Agent_Red/tests/**`, `applications/Agent_Red/docs/**`, `applications/Agent_Red/scripts/**` are allowed.
- Writes to `applications/Agent_Red/**` outside those subdirs require explicit allowlist entry (see Boundary B).
- When `active_workspace=gt-kb`: all paths under `E:\GT-KB\` are allowed (gt-kb is the broadest workspace).

**Boundary B — Control-plane / audit-trail allowlist** (always allowed regardless of workspace):
- `bridge/**` — bridge protocol artifacts (audit trail; CANNOT be blocked per `.claude/rules/file-bridge-protocol.md` and `GOV-FILE-BRIDGE-AUTHORITY-001`).
- `harness-state/**` — harness-state durable records (including this active-workspace per-harness records).
- `.claude/rules/**` — rule files (including this active-workspace.md itself).
- `.claude/settings.json` and `.claude/hooks/**` — hook registration and code.
- `.codex/**` — Codex hook intent and parity (per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).
- `memory/MEMORY.md` and `memory/work_list.md` — operational memory and standing backlog.
- `memory/pending-owner-decisions.md` — owner-decision-tracker hook output.
- `independent-progress-assessments/**` — Loyal Opposition reports.
- `.groundtruth/formal-artifact-approvals/**` — formal artifact approval packets.
- `groundtruth.db` — KB write authority (already gated by formal-artifact-approval hook).

**Test for F4 fix:** synthetic Write to `bridge/test-during-hosted-app-001.md` while `active_workspace=hosted-application` MUST be allowed (bridge artifacts are control-plane). Synthetic Write to `applications/Agent_Red/src/foo.py` while `active_workspace=gt-kb` MUST be allowed (gt-kb broadest). Synthetic Write to `applications/Agent_Red/src/foo.py` while `active_workspace=hosted-application, hosted_application_id=Agent_Red` MUST be allowed. Synthetic Write to `groundtruth-kb/src/foo.py` while `active_workspace=hosted-application` MUST be blocked (work-subject boundary).

**Per F5 fix: enforcement scope bounded to Claude Code; Codex protocol-only; repo-native validator for shell/script.**

- **Claude Code coverage:** PreToolUse hook on `Write`/`Edit` enforces both boundaries via `.claude/hooks/workspace-boundary-gate.py`.
- **Codex coverage:** Codex review skill (NO-GO any proposal targeting paths outside the declared workspace's boundaries) — protocol-level enforcement, not interception.
- **Shell/script coverage:** new `scripts/check_workspace_boundary.py` runs as a pre-commit hook (or Slice 1 setup adds it); rejects commits that include writes outside the declared workspace's boundaries (other than control-plane allowlist). Test fixture verifies the validator catches synthetic violations.

This first implementation EXPLICITLY DOES NOT cover all possible write paths (bare `python -c` exec, native subprocess writes, etc.). Slice 5 implementation bridge will document the residual coverage gap and the regression-test surface that bounds it.

### §2.6 Codex Review Enforcement (Slice 6; REVISED per F5)

(Mostly unchanged from -001 §2.6.) Codex review checks `Active Workspace:` field; NO-GOs mismatch with durable record.

**Per F5 fix:** Codex review skill ALSO checks the proposal's target paths against the declared workspace's boundaries. If declared `gt-kb` but proposal targets only `applications/Agent_Red/src/**`, NO-GO with workspace-mismatch finding. If declared `hosted-application` but proposal targets only `groundtruth-kb/src/**`, NO-GO. The check is intent-level (read the proposal's `target_paths` metadata or §"Files Touched" section), not write-time interception.

### §2.7 Resolver Behavior — Fail-Closed State Machine (NEW per F2, F3)

The resolver runs at session start and on every PreToolUse `Write`/`Edit`. It produces an `(active_workspace, hosted_application_id)` tuple OR a fail-closed diagnostic.

**Resolution algorithm:**

```
1. Read project-level .claude/rules/active-workspace.md.
   - If file missing OR malformed (e.g., missing required field, invalid YAML-ish header) → return ('gt-kb', '') with audit-log entry "project-level record absent/invalid; defaulting to gt-kb".
   - If valid AND active_workspace='gt-kb' → continue with project-level value.
   - If valid AND active_workspace='hosted-application' AND hosted_application_id non-empty AND owner_confirmation_evidence non-empty → continue with project-level value.
   - If valid BUT active_workspace='hosted-application' AND (hosted_application_id empty OR owner_confirmation_evidence empty) → BLOCK with diagnostic "project-level hosted-application record is incomplete; required fields hosted_application_id and owner_confirmation_evidence are empty; either complete the record or restore gt-kb default".

2. Read harness-local harness-state/<harness>/active-workspace.md (where <harness> from $HARNESS_NAME env or default 'claude').
   - If absent → use project-level value from step 1.
   - If present AND value matches project-level → use that value.
   - If present AND value differs from project-level:
     a. If harness-local's active_workspace='gt-kb' → use that (more restrictive than potentially-broader project-level).
     b. If harness-local's active_workspace='hosted-application':
        - Verify harness-local has its own owner_confirmation_evidence non-empty AND its own hosted_application_id non-empty AND that hosted_application_id matches project-level OR has separate documented owner override.
        - If verification fails → BLOCK with diagnostic "harness-local hosted-application record diverges from project-level without sufficient owner-confirmation evidence; resolve at startup".
        - If verification passes → use harness-local value WITH a startup-emitted divergence notification (visible in the session orient, not just a doctor warning).

3. Return resolved (active_workspace, hosted_application_id).
```

**Critical:** the resolver NEVER returns "infer from context" or "warn-mode degradation". The resolver returns either a definite tuple OR a fail-closed block. Per F2: missing/invalid records resolve to `gt-kb` OR block; never to inference.

**Divergence surfacing:** when harness-local diverges from project-level (per step 2.b verification-passes branch), the session-startup orient emits a visible notification block (not just a log line). This makes "agent A is in hosted-application while agent B is in gt-kb" mechanically visible at session start.

---

## §3. Implementation Plan (REVISED)

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Specs + ADR + initial declaration + resolver + repo-native validator | KB inserts: 4 DCLs + 1 ADR; create `.claude/rules/active-workspace.md` with `active_workspace: gt-kb`; per-harness records at `harness-state/{claude,codex}/active-workspace.md`; `groundtruth-kb/src/groundtruth_kb/active_workspace.py` (resolver per §2.7); `scripts/check_workspace_boundary.py` (repo-native validator per F5) | KB query returns specs; rule file auto-loads at session start; resolver returns `(gt-kb, '')` for valid project-level + no harness-local; resolver blocks on incomplete hosted-application record; repo-native validator catches synthetic violations |
| 2 | Inference prohibition rule + Codex skill update | `.claude/rules/active-workspace.md` body + change log; Codex skill prompt updates | Active-workspace value visible in startup orient; Codex NO-GO test verifies enforcement |
| 3 | Owner toggle prompts (interrogation contract per F6) | `.claude/hooks/active-workspace-tracker.py` (new UserPromptSubmit hook); `.claude/settings.json` registration | `set workspace to GT-KB` non-interactive update; off-default prompts produce interrogation question; canonical confirmation `we are working on the hosted application Agent_Red` updates record with owner_confirmation_evidence |
| 4 | Bridge proposal field requirement | Extend `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` to validate `Active Workspace:` field; extend `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | Synthetic bridge without field rejected; with mismatched value rejected; with matching value allowed |
| 5 | File-write boundary enforcement (two boundaries per F4) | `.claude/hooks/workspace-boundary-gate.py` (new); `.claude/settings.json` registration; tests for both Boundary A and Boundary B per §2.5 | Synthetic Writes per §2.5 test cases pass; control-plane allowlist works during hosted-application state |
| 6 | Codex review skill update | Codex skill prompt extended with workspace-declaration check + workspace-target-paths check (per F5) | Synthetic proposal review NO-GOs on missing/mismatched workspace OR on target_paths/workspace mismatch |
| 7 | Validation regression suite | All §2.5 + §2.7 + §4 spec-test mapping fixtures | Tests pass; live cycle works |

**Sequencing:** Slice 1 first (specs + initial declaration + resolver + validator). Slices 2-6 depend on Slice 1; can run roughly parallel. Slice 7 last.

**Per F5 explicit scope statement:** Slice 5's hook covers Claude Code `Write`/`Edit` only. Slice 1's repo-native validator covers shell/script via pre-commit. Codex coverage is protocol-only (review-gate per Slice 6). The architecture explicitly does NOT claim coverage for bare `python -c` exec, native subprocess writes inside running tools, or other pathways outside these three layers — this gap is documented and bounded by the regression-test surface.

---

## §4. Spec-to-Test Mapping (NEW per Codex required revision)

Each DCL/ADR maps to specific tests at the slice listed:

| DCL/ADR | Slice | Test |
|---------|-------|------|
| `DCL-ACTIVE-WORKSPACE-DECLARATION-001` (bridge proposals MUST declare workspace) | 4 + 6 | Synthetic bridge without field → bridge-compliance-gate rejects (Slice 4 test); Codex review NO-GOs (Slice 6 test). |
| `DCL-WORKSPACE-INFERENCE-PROHIBITION-001` (no inference from cwd/path/etc) | 2 + 7 | Resolver returns same value when called from different cwds (Slice 2 test); regression test grep for inference patterns in code (Slice 7 test). |
| `DCL-WORKSPACE-BOUNDARY-ENFORCEMENT-001` (hook enforces boundaries) | 5 | Boundary A + Boundary B test cases per §2.5 (Slice 5 test). |
| `DCL-RESOLVER-FAIL-CLOSED-001` (NEW; resolver fails closed on invalid records per F2/F3) | 1 + 7 | Resolver test fixtures for: missing project file → defaults to gt-kb; malformed file → defaults to gt-kb with audit log; hosted-application with empty hosted_application_id → blocks with diagnostic; harness-local divergence without confirmation evidence → blocks (Slice 1 + Slice 7 tests). |
| `ADR-WORKSPACE-DECLARATION-OVER-DETECTION-001` (architecture rationale) | 1 | KB record exists; cited by other DCLs (Slice 1 test). |

**Edge cases (per Codex required revision):**

| Edge case | Slice | Test |
|-----------|-------|------|
| Missing project record | 1 | Resolver returns `('gt-kb', '')` + audit log (per §2.7 step 1). |
| Malformed exception record (e.g., active_workspace='hosted-application' but hosted_application_id empty) | 1 | Resolver BLOCKS with diagnostic per §2.7 step 1. |
| Per-harness vs project divergence (harness=hosted-application, project=gt-kb) | 1 | Resolver runs §2.7 step 2.b verification; without owner-confirmation evidence → blocks; with evidence → uses harness-local AND emits startup divergence notification. |
| Canonical value rejection for `agent-red` as `active_workspace` | 1 | Resolver fails-closed (only `gt-kb` and `hosted-application` are valid `active_workspace` values per §1.1; `agent-red` rejected). |
| Hosted-application confirmation checkpoint | 3 | Owner prompt `set workspace to Agent Red` → produces interrogation question; only canonical `we are working on the hosted application Agent_Red` updates the record. |
| Bridge / control-plane allowlist during hosted-application work | 5 | Per §2.5 Boundary B test cases. |
| Codex / non-Claude write-path limitations | 5 + 6 | Slice 5 documents the residual coverage gap; Slice 6 Codex review-gate enforces protocol-level workspace check; pre-commit validator catches shell/script writes. |
| Bridge proposal `Active Workspace:` parsing and mismatch | 4 + 6 | Slice 4 hook test; Slice 6 Codex review test. |

---

## §5. Validation — Recurring Failure as Regression Test

(Mostly unchanged from -001 §4.) Plus per F1 fix:

4. **Canonical-state-only invariant:** `git grep -E 'active_workspace.*agent-red'` returns zero matches (after migration). The string `agent-red` only appears as `hosted_application_id` value, never as `active_workspace` value.

---

## §6. Reversibility + Risks (REVISED per F2)

### §6.1 Reversibility

(Mostly unchanged from -001 §5.1.) **Per F2 fix:** removing the `.claude/rules/active-workspace.md` file does NOT return the system to "infer from context". The resolver per §2.7 returns `('gt-kb', '')` when the file is missing — the default is the safe fallback, not inference. This makes deletion of the file equivalent to "restore default workspace".

### §6.2 Friction risk

(Unchanged from -001 §5.2.)

### §6.3 Per-harness vs project-level precedence (per F3 fix)

(Replaces -001 §5.3.) Per-harness records require explicit owner-confirmation evidence; precedence is documented in §2.7; divergence is surfaced at startup (visible orient block, not just a doctor warning). Resolver fails closed when divergence lacks evidence.

### §6.4 Inference suppression (mostly unchanged from -001 §5.4)

(Mostly unchanged.) Per F5 + F6: hook + repo-native validator + Codex protocol enforcement together cover Claude / shell / Codex; LLM prose tendencies still require explicit citation discipline (Codex review-gate enforces).

---

## §7. Codex Review Request

Per the prior NO-GO findings F1-F6 + spec-test mapping, this REVISED-1 should be evaluable on:

1. Does the F1 fix (canonical states `gt-kb` + `hosted-application`; `hosted_application_id` separate) eliminate the third-state ambiguity?
2. Does the F2 fix (fail-closed resolver per §2.7) eliminate the inference-fallback risk?
3. Does the F3 fix (per-harness records require owner-confirmation evidence + startup divergence surfacing) eliminate silent unauthorized divergence?
4. Does the F4 fix (Boundary A vs Boundary B per §2.5; control-plane allowlist) preserve bridge/governance audit-trail writability during hosted-application work?
5. Does the F5 fix (Claude Code first impl + repo-native validator + Codex protocol-only) provide adequate enforcement coverage with documented gaps?
6. Does the F6 fix (interrogation contract per §2.3; canonical-only confirmation for hosted-application) prevent off-default prompts from updating the record without explicit confirmation?
7. Does §4 spec-to-test mapping cover all required edge cases?

Plus the original §6 questions from -001 (suppression of inference adequacy, mechanical enforcement layer completeness, owner toggle prompt format adequacy, default workspace, adopter-side propagation).

---

## §8. Decision Needed From Owner

None for this REVISED-1; all changes are within the owner-stated invariants from -001 plus address Codex's evidence-based blocking findings. If owner wants a different vocabulary for `hosted_application_id` (per F1 fix), that's a separate request.

---

## §9. Reference Artifacts

(Unchanged from -001 §7.) Plus:
- Codex NO-GO at -002 (commit `b693ba92`) — substance basis for this revision.
- Sister bridge `gtkb-spec-lifecycle-schema-2026-04-29-003` (REVISED-1) — `parent` attribute vocabulary alignment.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
