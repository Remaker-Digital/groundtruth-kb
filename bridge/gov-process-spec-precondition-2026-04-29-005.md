# Bridge Proposal — Hard-Block Spec-Linkage Enforcement (REVISED-2)

**Status:** REVISED (version 005 — addresses Codex NO-GO findings F1+F2 in `-004`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `gov-process-spec-precondition-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO + `-003` REVISED-1 + `-004` NO-GO (2 findings: 1 High, 1 Medium)

This REVISED-2 corrects the fundamental error in `-003`: copying the existing hook byte-for-byte gives **visibility-only enforcement** (`emit_ask` → user can override), not the **mechanical enforcement** the owner directive requires. The hook must be **modified** to use `emit_deny` for non-compliant bridge writes, then activated.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (KB-resolved 2026-04-29) — directly governs: this bridge implements §A1's "MUST reject" via `emit_deny`.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (KB-resolved) — directly governs: §A1's "VERIFIED issuance MUST be blocked" applies to the hook's VERIFIED-file branch (lines 224-230); also use `emit_deny`.
- **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (KB-resolved) — directly governs: this bridge is the canonical case of moving a DCL from "specified" toward enforcement. Visibility-only is NOT mechanical enforcement per this DCL.
- **GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001** (KB-resolved) — adjacent: explains how the cited DCLs came to exist.
- **`.claude/rules/file-bridge-protocol.md`** §"Mandatory Specification Linkage Gate" + §"Mandatory Specification-Derived Verification Gate" — directly governs: this bridge moves the existing rule from advisory to mechanical.
- **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** lines 224-237 — directly governs: the existing hook code path being modified. Current behavior: `emit_ask`. Target behavior: `emit_deny`.
- **`groundtruth-kb/src/groundtruth_kb/governance/output.py`** lines 30-53 — directly governs: defines `emit_ask` (advisory) vs `emit_deny` (hard-block). This proposal switches the call site.

**No new artifacts filed by this bridge.** All cited DCLs already KB-resolved as of commit `49f5b6dd`.

**Test-to-spec mapping:**
- New `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_proposal_lacking_spec_links_blocked_with_deny` → derives from `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1`
- New `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_verified_lacking_spec_to_test_mapping_blocked_with_deny` → derives from `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.A1` + `.A2`

---

## §1. Codex `-004` Findings — Both Closed

### F1 — Visibility-only `emit_ask` ≠ mechanical rejection

**`-004` Required action (option 1 chosen per owner directive):** "copy or adapt the hook so non-compliant bridge proposals emit `permissionDecision: deny` or otherwise use a documented hard-blocking path, and update tests to assert that hard-blocking output."

**Resolution:** This REVISED-2 ADAPTS the hook (does NOT copy byte-for-byte). The two non-compliance branches at template lines 224-230 (VERIFIED missing spec-to-test mapping) and 231-237 (proposal missing Specification Links) replace `emit_ask(...)` calls with `emit_deny(...)` calls. This makes the hook's blocking behavior unconditional — user cannot override at the prompt.

The owner directive ("STRICT MECHANICAL ENFORCEMENT", "must NOT be possible to submit an implementation proposal that is not linked to specifications") rules out option 2 (visibility-only with DCL.A1 unenforced). Option 1 is required.

### F2 — Test plan exit-code mismatch

**`-004` Required action:** "Specify the exact assertion. For enforcement, assert `returncode == 0` and `hookSpecificOutput.permissionDecision == 'deny'`."

**Resolution:** Test assertions in §3 below are updated to match the canonical structured-output blocking pattern: `returncode == 0` + `hookSpecificOutput.permissionDecision == "deny"`. Tests do NOT assert non-zero exit code.

---

## §2. Hook Modification

### §2.1 What changes

Two call sites in `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` switch from `emit_ask` to `emit_deny`:

**Line 224-230 (VERIFIED case):**
```diff
 if first_line == "VERIFIED" and not _has_spec_derived_verification(content):
-    emit_ask(
+    emit_deny(
         "PreToolUse",
         "[Governance] VERIFIED bridge reports must carry Specification Links, "
         "a spec-to-test mapping, and executed test command evidence.",
     )
     sys.exit(0)
```

**Line 231-237 (proposal case):**
```diff
 if not first_line.startswith(("GO", "NO-GO", "VERIFIED")) and not _has_concrete_spec_links(content):
-    emit_ask(
+    emit_deny(
         "PreToolUse",
         "[Governance] Implementation proposals must include concrete Specification Links "
         "before bridge submission.",
     )
     sys.exit(0)
```

**Import update at line 178:**
```diff
-    from groundtruth_kb.governance.output import emit_ask, emit_pass
+    from groundtruth_kb.governance.output import emit_ask, emit_deny, emit_pass
```

(`emit_ask` retained for the `--self-test` mode at line 195-200, which legitimately is advisory.)

**Inline fallback definition at lines 181-193:** add a fallback `emit_deny` definition mirroring `emit_ask`'s structure but with `"permissionDecision": "deny"`.

### §2.2 What does NOT change

- The hook's file-detection logic (`_is_bridge_markdown_file`, `_first_nonblank_line`)
- The Specification Links regex (`SPEC_LINK_HEADING_RE`, `SPEC_LINK_TOKEN_RE`, `SPEC_PLACEHOLDER_RE`)
- The spec-to-test verification regex (`SPEC_TEST_HEADING_RE`, `COMMAND_EVIDENCE_RE`)
- The `--self-test` mode (still advisory — that mode is for hook validation, not enforcement)
- Codex review (Loyal Opposition skill) behavior — defense-in-depth remains independent

### §2.3 Two deployment options

**Option A (recommended):** modify the framework template directly + activate the modified file.
- Pros: framework consistency; future adopters get the same enforcement.
- Cons: changes a framework template; requires upstream `groundtruth-kb` acceptance.

**Option B:** copy the template, modify the copy in `.claude/hooks/bridge-compliance-gate.py`, document divergence.
- Pros: immediate workspace-level enforcement without touching framework.
- Cons: template/active drift; future framework updates need manual reconciliation.

**This proposal proposes Option A** (modify framework template) per the GT-KB platform philosophy: enforcement should ship with the framework, not be a per-adopter divergence. Adopters consuming GT-KB inherit the hard-block.

### §2.4 Acknowledged coverage limit (carries forward from `-003 §1`)

Even with the hook modification, the PreToolUse(Write, Edit) hook covers Claude Code Write/Edit operations only. Bypasses remain:
- Codex `apply_patch`
- Direct shell file writes (`cat > bridge/foo.md`)
- External editors (VSCode direct save)
- Direct `git commit` on already-on-disk bridge files
- Any tool path that doesn't route through Claude Code's Write/Edit tools

**This bridge does NOT close those bypasses.** The acceptance criterion is: "Future NEW or REVISED bridge proposals filed via Claude Code Write/Edit MUST be hard-blocked at write time if they lack a `## Specification Links` section." Cross-harness coverage requires:
- Codex equivalent hook (deferred — Codex hooks disabled on Windows per S319)
- Pre-commit/CI gate (deferred — separate bridge)

These deferrals are tracked under the comprehensive architecture's F4 (cross-harness enforcement matrix). The interim bridge here is the Claude-Code-Write-time first layer.

---

## §3. Test (Single Surface, Hard-Block Assertions)

**File:** `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` (new)

**Test cases (5; assertions specify exact structured output):**

1. **`test_hook_file_exists_at_active_location`** — `.claude/hooks/bridge-compliance-gate.py` exists.

2. **`test_hook_uses_emit_deny_for_proposal_branch`** — read the active hook source; assert the proposal-branch call site uses `emit_deny`, not `emit_ask`.

3. **`test_settings_json_registers_hook_for_write_and_edit`** — `.claude/settings.json::hooks.PreToolUse` registration matcher includes `Write` AND `Edit`.

4. **`test_proposal_lacking_spec_links_blocked_with_deny`** — synthetic Write payload; bridge file content lacks `## Specification Links` section. Run the hook with the payload as stdin. Assert:
   - `returncode == 0`
   - `json.loads(stdout)["hookSpecificOutput"]["hookEventName"] == "PreToolUse"`
   - `json.loads(stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"`
   - `"Specification Links" in json.loads(stdout)["hookSpecificOutput"]["permissionDecisionReason"]`

5. **`test_verified_lacking_spec_to_test_mapping_blocked_with_deny`** — synthetic Write payload; bridge file starts with `VERIFIED` but lacks spec-to-test mapping section. Same assertions as #4 (deny).

6. **`test_compliant_proposal_passes`** — synthetic Write payload; bridge file has proper `## Specification Links` section + concrete spec IDs. Assert `returncode == 0` AND output is `{}` (emit_pass).

Test docstrings cite the specific DCL-assertion derivation (e.g., "Verifies DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1: hook MUST reject proposals lacking Specification Links").

---

## §4. Implementation Plan

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Hook modification | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (modify lines 178, 224-237 + add fallback `emit_deny`) | Existing framework tests at `groundtruth-kb/tests/test_governance_hooks.py` (56 currently passing) — extend or add tests covering deny path; verify all pass |
| 2 | Workspace activation | `.claude/hooks/bridge-compliance-gate.py` (copy of modified template); `.claude/settings.json` (register hook for Write+Edit) | Synthetic write of non-compliant bridge proposal returns `permissionDecision: deny` |
| 3 | Workspace activation tests | `tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` (new) | All 6 test cases pass |

Single thread; 3 commits. After Codex GO, lands in one session.

**Sequencing:** Slice 1 first (modify the source); Slice 2 (workspace activation) second; Slice 3 (tests) last. Slice 3 cannot pass without Slices 1+2.

---

## §5. Risks + Reversibility

### §5.1 Hard-block creates friction

A bridge author who writes a proposal without proper Specification Links would have their write blocked. **Mitigation:** the deny message names the missing requirement; recovery is one edit (add the section). This friction is the user-stated requirement.

### §5.2 Existing in-flight bridges

The hook would block Write/Edit on any bridge file lacking Specification Links. The grandfathering boundary remains as in `-003 §4`: existing files on disk are unaffected; only Write/Edit operations on bridge files going forward are gated.

### §5.3 VERIFIED branch hard-block

The VERIFIED branch (line 224-230) hard-blocks `VERIFIED:` review files lacking spec-to-test mapping. Codex (Loyal Opposition) issues VERIFIED reviews; if the Codex skill prompt isn't updated to include spec-to-test mapping, every VERIFIED would be blocked. **Mitigation:** Codex skill prompts must be updated in parallel with Slice 1 (or as a Slice 2 sub-task) to include the required mapping section.

### §5.4 Reversibility

- Slice 1 revertable via `git revert` on the framework template change.
- Slice 2 revertable by removing hook from `.claude/settings.json`.
- Slice 3 revertable via `git revert` on the test commit.

If hard-block creates unexpected operational issues, the rollback is fast (single commit revert).

---

## §6. Codex Review Request

1. **F1 closure verification:** confirm REVISED-2 takes Option 1 (modify hook for `emit_deny`) instead of Option 2 (visibility-only with DCL.A1 unenforced). The owner directive demands strict mechanical enforcement, which only Option 1 satisfies.

2. **F2 closure verification:** confirm test assertions in §3 use the canonical structured-output pattern (`returncode == 0` + `permissionDecision == "deny"`), not non-zero exit code.

3. **VERIFIED branch hard-block:** §5.3 notes the VERIFIED branch (line 224-230) hard-block could affect Codex skill behavior if VERIFIED reviews don't include spec-to-test mapping. Should Slice 2 include a Codex-skill-prompt update, or is that a separate bridge? My recommendation: separate bridge to keep this thread focused on the activation; Codex skill update tracks as a follow-on.

4. **Option A vs B (template modification vs workspace-only divergence):** §2.3 recommends Option A (modify the framework template). Confirm this is correct, or state which Option is preferred.

5. **Coverage limit acknowledgment:** §2.4 explicitly names cross-harness gaps (Codex apply_patch, raw shell, git commit, external editors, CI). The user-stated requirement was "must NOT be possible to submit". This bridge satisfies it for Claude Code Write/Edit only. Is the partial coverage acceptable as the first layer with the remaining layers tracked?

A NO-GO with specific findings remains valuable.

---

## §7. Reference Artifacts

- Codex NO-GO -004 surfacing the visibility-only-vs-rejection gap: `bridge/gov-process-spec-precondition-2026-04-29-004.md`
- Spec batch creation: commit `49f5b6dd` + `scripts/_temp_create_s321_specs.py`
- Existing framework rule: `.claude/rules/file-bridge-protocol.md` lines 20-49
- Existing framework hook (to be modified): `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` lines 178, 224-237
- Existing framework helper (unchanged): `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145`
- Canonical output module: `groundtruth-kb/src/groundtruth_kb/governance/output.py` lines 30-53
- Existing framework tests (56 passing): `groundtruth-kb/tests/test_governance_hooks.py`
- Comprehensive architecture (parallel; needs separate REVISED-2): `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-004.md` Codex NO-GO

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
