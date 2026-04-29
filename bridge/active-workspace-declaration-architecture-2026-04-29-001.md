# Bridge Proposal — Active-Workspace Declaration Architecture

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `active-workspace-declaration-architecture-2026-04-29`

**Trigger:** Owner directives 2026-04-29 (S321), in two parts:

Part 1: "How do we enforce an explicit choice of workspace? ... We need to actively suppress any attempt to guess or intuit which 'workspace' we are in ... The default should be a change-controlled directive from the user: when I say we are in the 'GT-KB' workspace, that should be mechanically enforced."

Part 2 (clarification): "We need to carefully inspect all artifacts in this entire project to remove all ambiguity or confusion about the project: we are *always* working on the GT-KB platform *except* when I explicitly state that we are not. When I state that we are not working on GT-KB, the AI agent *must* interrogate me until I state that we are working on the hosted application."

**Non-negotiable invariants from owner directive:**
- **Default is GT-KB platform. Always.** No declaration is required to be in the default state.
- **Exception is "hosted application" (currently Agent Red).** The exception is the ONLY off-default state.
- **Owner declares exceptions explicitly.** The agent MUST NOT enter the exception state without explicit owner declaration.
- **Interrogation contract:** when the owner states "not GT-KB" (any signal off-default), the agent MUST stop and interrogate the owner until the owner explicitly states "we are working on the hosted application" (or returns to default).
- **No inference.** Path-based, context-based, recent-file-based, or other inference paths to workspace identity are PROHIBITED.
- **Audit obligation:** the project's existing artifacts MUST be inspected to remove ambiguous "this is Agent Red work" or "this is GT-KB work" framing in favor of explicit defaults + exceptions.

**Recurring failure pattern this addresses:** during this S321 session alone, Prime Builder (me) has multiple times framed work as "Agent Red workspace" when the declared default is GT-KB. The owner has corrected these references repeatedly. The root cause is that no canonical, mechanical "default = GT-KB" rule exists; both Prime and Codex infer from cwd, file paths, recently-touched directories, CLAUDE.md content (which identifies the project as Agent Red Customer Experience commercial product) — producing inconsistent answers that conflict with the owner's stated default.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **GOV-01** (administrative reference)
- **GOV-03** (Specs are the negotiation artifact for mutual understanding) — directly governs: workspace declaration is the negotiation artifact for "which workspace are we in"
- **GOV-08** (Knowledge Database is the single source of truth) — directly governs: declarations live in durable records, not inference
- **GOV-09** (Owner Input Classification Rule) — adjacent: owner statements about workspace are spec-classifiable input
- **GOV-20** (Architecture decisions: ADR/DCL/IPR/CVR advisory pilot) — directly governs (this proposal files DCLs + ADR)
- **`.claude/rules/project-root-boundary.md`** — adjacent: defines path-level boundaries for GT-KB and Agent Red. This proposal builds on those boundaries with active-workspace declaration.
- **`.claude/rules/operating-role.md`** + `.claude/rules/acting-prime-builder.md` — directly relevant precedent: durable role declaration via tracked file. Active-workspace follows the same pattern for workspace identity.
- **`harness-state/claude/operating-role.md`** + `harness-state/codex/operating-role.md` — directly relevant precedent: per-harness durable records. Active-workspace gets analogous per-harness records.
- **`bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`** REVISED-1 — adjacent (parallel filing): the spec-coverage architecture this bridge complements
- **CLAUDE.md** — administrative; identifies the project as "Agent Red Customer Experience" but does not declare the active development workspace

**New artifacts this proposal files** (under `pending:` bootstrap exemption):
- `DCL-ACTIVE-WORKSPACE-DECLARATION-001` (Slice 1)
- `DCL-WORKSPACE-INFERENCE-PROHIBITION-001` (Slice 1)
- `DCL-WORKSPACE-BOUNDARY-ENFORCEMENT-001` (Slice 1)
- `ADR-WORKSPACE-DECLARATION-OVER-DETECTION-001` (Slice 1)

**Test-to-spec mapping** (per existing rule's verification gate):
- New tests in Slice 4 derive from each DCL via docstring citation per existing convention.

---

## §0. Scope

### In scope

1. **Define a durable, change-controlled workspace declaration record.**
2. **Suppress all workspace-inference paths.** Rules that auto-infer workspace identity from cwd / file path / CLAUDE.md content / etc. are explicitly prohibited; all references to "this workspace" must resolve to the declared record.
3. **Add owner toggle prompts** to set the active workspace ("set workspace to GT-KB", "set workspace to Agent Red").
4. **Mechanically enforce workspace boundary** at the file-write level via hook (extends the existing root-boundary enforcement with workspace-scoped boundaries).
5. **Add bridge proposal `Active Workspace:` field** as a required header line, parallel to `Specification Links`.
6. **Update Codex review skill** to NO-GO any proposal lacking a workspace declaration.

### Out of scope

- The spec-coverage architecture (parallel bridge `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`).
- The smart-poller-narrow incident remediation (parallel bridge `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md`).
- Multi-workspace coordination (e.g., switching mid-session); explicit toggle is supported but multi-workspace concurrent operation is deferred.
- Adopter-side workspace declarations (downstream of GT-KB platform; future bridge after platform side ships).

---

## §1. Workspace Model — Default + Exception

The model is binary, not enumerated. Two states only:

| State | Trigger | Description |
|---|---|---|
| **`gt-kb` (DEFAULT)** | Always, unless explicit owner exception declared | The GT-KB platform workspace. All work defaults here. No declaration needed; the absence of an exception declaration means GT-KB. Includes `groundtruth-kb/`, `bridge/`, `.claude/`, root-level platform tooling, AND `applications/Agent_Red/` when GT-KB platform work touches the application (e.g., as test reference). |
| **`hosted-application` (EXCEPTION)** | Only after owner explicitly declares "we are working on the hosted application" (or equivalent) | Application-scope work bounded to `applications/Agent_Red/`. Currently Agent Red is the only hosted application; future hosted applications would require their own owner-declared exception state. Path-bounded by `.claude/rules/project-root-boundary.md`. |

**Critical invariant:** there is no third state. There is no "ambiguous" or "unknown" state. Absence of an exception declaration = `gt-kb`. The default is mechanically the answer when no override exists.

**Owner-declared exception triggers (non-exhaustive):**
- "we are working on the hosted application"
- "switch to Agent Red" / "set workspace to Agent Red"
- "this is application work" (after interrogation confirms hosted-application)
- Any explicit owner statement that meets the interrogation contract in §2.3

**Owner-declared default-restoration triggers:**
- "back to GT-KB" / "set workspace to GT-KB"
- "platform work" / "this is platform work"
- (and the absence of an exception declaration in any future session restores default)

---

## §2. Architecture

### §2.1 Durable record (Slice 1)

**Location:** `.claude/rules/active-workspace.md` (project-level default)

**Format:**
```markdown
# Durable Active-Workspace Record

active_workspace: gt-kb
declared_at: 2026-04-29T17:30:00+00:00
declared_by: owner
notes: GT-KB platform governance work; spec-coverage architecture filing.

## Change Log

- 2026-04-29 owner declared active_workspace=gt-kb (S321 platform work)
- (prior entries preserved here as audit trail)
```

**Per-harness analog** (per Phase 1 isolation precedent for operating-role):
- `harness-state/claude/active-workspace.md`
- `harness-state/codex/active-workspace.md`

Per-harness records take precedence over project-level when present (each harness can independently declare; rare but supported case for Codex working on Agent Red while Claude works on GT-KB platform).

### §2.2 Inference prohibition (Slice 2)

**Specs filed by Slice 1:**
- `DCL-WORKSPACE-INFERENCE-PROHIBITION-001`: workspace identity MUST NOT be derived from cwd, file paths, CLAUDE.md content, recently-edited files, MEMORY.md content, or any other inference source. Code (and reasoning) that infers workspace from these sources is non-compliant.

**Mechanism:**
- New rule `.claude/rules/active-workspace.md` (the durable record IS the rule, auto-loaded)
- Bridge proposals MUST cite their workspace explicitly via the `Active Workspace:` field (§2.4 below)
- Codex review NO-GOs any proposal where the declared workspace doesn't match the durable record (mismatch = unauthorized scope drift)
- Updates to `.claude/rules/file-bridge-protocol.md` to reference the active-workspace record as authoritative

### §2.3 Owner toggle prompts (Slice 3)

Following the operating-role precedent in `.claude/rules/operating-role.md`:

**Recognized owner prompts:**
- `set workspace to GT-KB` / `set workspace to gt-kb`
- `set workspace to Agent Red` / `set workspace to agent-red`
- `change workspace to <value>` (synonym)
- `confirm workspace` (read-only query)

**Mechanism:**
- Existing UserPromptSubmit hook (`.claude/hooks/spec-classifier.py` or new `.claude/hooks/active-workspace-tracker.py`) detects the recognized prompts
- On detection, hook updates `.claude/rules/active-workspace.md` (or harness-local `harness-state/<harness>/active-workspace.md`)
- Append to change log; update active_workspace value
- Format the response so the owner sees "Workspace set to <value>; declared_at <timestamp>"

### §2.4 Bridge proposal `Active Workspace:` field (Slice 4)

Every bridge proposal MUST include `Active Workspace:` field at top, parallel to `## Specification Links`:

```markdown
**Active Workspace:** gt-kb
```

**Mechanism:**
- Extends `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` to validate the `Active Workspace:` field via similar regex/parser as `validate_specification_links()`
- Extends `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to check the field on `Write`/`Edit`
- Mismatch with active-workspace declaration → reject the write
- Field absent → reject the write

### §2.5 File-write boundary enforcement (Slice 5)

**Specs filed by Slice 1:**
- `DCL-WORKSPACE-BOUNDARY-ENFORCEMENT-001`: PreToolUse hook on `Write`/`Edit` MUST verify the target path is within the declared active workspace's boundary. Out-of-boundary writes fail-closed.

**Mechanism:**
- Extend `.claude/hooks/destructive-gate.py` (or add a sibling `.claude/hooks/workspace-boundary-gate.py`) to check `Write`/`Edit` target paths against the active workspace's boundary
- For `gt-kb` workspace: writes anywhere under `E:\GT-KB\` are allowed
- For `agent-red` workspace: writes only under `E:\GT-KB\applications\Agent_Red\` are allowed; writes elsewhere fail-closed with explicit error message ("Active workspace is `agent-red`; this write targets a path outside the application boundary; either change workspace or revise the operation")

### §2.6 Codex review enforcement (Slice 6)

**Specs filed by Slice 1:**
- `DCL-ACTIVE-WORKSPACE-DECLARATION-001`: bridge proposals MUST declare the active workspace via the `Active Workspace:` field. Codex review MUST issue NO-GO on any proposal lacking the field or where the declared value doesn't match the durable record.

**Mechanism:**
- Codex review skill prompt extended: first checks (after `Specification Links`) include workspace declaration validation
- Codex independently reads `.claude/rules/active-workspace.md` to verify the proposal's declared workspace matches
- Mismatch → NO-GO

---

## §3. Implementation Plan

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Specs + ADR + initial declaration | KB inserts: 3 DCLs + 1 ADR; create `.claude/rules/active-workspace.md` with `active_workspace: gt-kb` (current declared state); per-harness records at `harness-state/{claude,codex}/active-workspace.md` | KB query returns specs; rule file auto-loads at session start |
| 2 | Inference prohibition rule + Codex skill update | `.claude/rules/active-workspace.md` (rule body + change log); rule file in `.claude/rules/` for auto-load; Codex skill prompt update | Active-workspace value visible in startup orient; Codex NO-GO test verifies enforcement |
| 3 | Owner toggle prompts | Extend or add `.claude/hooks/active-workspace-tracker.py` (UserPromptSubmit hook); `.claude/settings.json` registration | Owner prompts `set workspace to <value>` correctly update the durable record + emit confirmation |
| 4 | Bridge proposal field requirement | Extend `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` (validate `Active Workspace:` field); extend `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`; activate updated hook in `.claude/hooks/` | Synthetic bridge without `Active Workspace:` rejected; with mismatched value rejected; with matching value allowed |
| 5 | File-write boundary enforcement | Extend (or sibling-add) `.claude/hooks/workspace-boundary-gate.py`; `.claude/settings.json` registration; tests | Synthetic Write outside the active workspace's boundary rejected; inside boundary allowed |
| 6 | Codex review skill update | Codex skill prompt includes workspace-declaration check after Specification Links | Synthetic proposal review NO-GOs on missing or mismatched workspace declaration |
| 7 | Validation | Synthetic regression: file a bridge declaring `agent-red` while declared workspace is `gt-kb`; confirm rejected. Toggle to `agent-red`; retry; confirm allowed. | Tests pass; live cycle works |

**Sequencing:** Slice 1 first (specs + initial declaration). Slices 2-6 depend on Slice 1; can run roughly parallel. Slice 7 last.

---

## §4. Validation — Recurring failure as regression test

The user noted: "we seem to be 'detecting' or 'discerning' the workspace but that approach is failing." This S321 session has multiple instances of Prime Builder referring to "Agent Red workspace" when the declared workspace is GT-KB. After this architecture lands:

1. **No-inference invariant:** any code or reasoning that asserts a workspace value MUST cite the durable record, not infer. Synthetic test: `git grep -E "(Agent Red|GT-KB) workspace"` finds only references that explicitly cite `.claude/rules/active-workspace.md` (or its harness-local equivalent).
2. **Mechanical enforcement:** synthetic Write to `bridge/test-mismatched-workspace-001.md` declaring `Active Workspace: agent-red` while the durable record says `gt-kb` → blocked by the hook. Synthetic Write to `applications/Agent_Red/src/foo.py` while workspace is `gt-kb` → allowed (gt-kb can touch the application boundary). Synthetic Write to `bridge/INDEX.md` while workspace is `agent-red` → blocked (out of application boundary).
3. **Owner toggle correctness:** `set workspace to Agent Red` → durable record updated → subsequent operations enforce agent-red boundary.

If all three regression tests pass, the workspace-declaration architecture closes the failure mode.

---

## §5. Reversibility + Risks

### §5.1 Reversibility

Each slice independently revertable. Removing the active-workspace.md file returns the system to its current "infer from context" state (which the proposal aims to eliminate). The hooks gracefully degrade (warn-mode) if the durable record is absent during transition.

### §5.2 Friction risk

Owner must declare workspace (one-time toggle prompt); proposals must include `Active Workspace:` field; mismatched workspaces require explicit toggle. **Mitigation:** the owner-toggle is a single prompt; the proposal field is one line; the durable record is auto-set at first declaration. Friction << current cost of misframing recurring failures.

### §5.3 Per-harness vs project-level precedence

Per-harness records can drift from project-level. **Mitigation:** Slice 1 sets the precedence rule explicitly (per-harness wins when present); doctor check warns when harnesses' workspace declarations diverge.

### §5.4 Inference isn't fully suppressible by hooks alone

Hooks can enforce write-boundaries and field requirements, but cannot fully suppress an LLM's tendency to use language like "Agent Red workspace" in prose without checking the record. **Mitigation:** the rule explicitly prohibits this; Codex review NO-GOs any proposal with such inferences not backed by record citations; Prime Builder protocol updates require explicit citation when asserting workspace.

---

## §6. Codex Review Request

1. **Suppression of inference adequacy.** Section §2.2 prohibits inference. Is the prohibition strict enough? Are there inference-adjacent patterns (e.g., "the file I'm editing is under applications/Agent_Red/, so this is Agent Red work") that the prohibition doesn't capture?
2. **Mechanical enforcement layer completeness.** Slices 4-6 implement enforcement at write/edit hook + bridge proposal validator + Codex review. Is there a layer missing? Specifically: does the existing root-boundary enforcement (`.claude/rules/project-root-boundary.md`) need updates to cite the active-workspace record?
3. **Per-harness vs project-level resolution.** Section §2.1 says per-harness wins when present. Is this the right precedence? Or should they be required to agree (fail-closed if they diverge)?
4. **Owner toggle prompt format.** Section §2.3 lists 4 recognized variants. Should there be more (e.g., `gt-kb workspace next session`, `loyal opposition workspace`, etc.)? Or is the small set sufficient?
5. **Default workspace on initial declaration.** Slice 1 declares `active_workspace: gt-kb`. Is this the right default given the GT-KB platform context? Or should the system default to "undeclared" and force an explicit owner declaration before any work proceeds?
6. **Adopter-side propagation.** This bridge ships GT-KB platform infrastructure. Adopter projects (consuming GT-KB via `gt project upgrade`) inherit the architecture. Adopter-side bridges should declare their own active workspace; does the architecture cover this, or does it need adopter-specific guidance?

A NO-GO with specific findings remains valuable.

---

## §7. Reference Artifacts

- Triggering directive: 2026-04-29 (S321) owner statement on workspace inference being insufficient
- Operating-role precedent: `.claude/rules/operating-role.md` + `harness-state/{claude,codex}/operating-role.md`
- Root-boundary precedent: `.claude/rules/project-root-boundary.md`
- Spec-linkage parallel: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md` (REVISED-1, parallel filing)
- Authority chain: GOV-01, GOV-03, GOV-08, GOV-09, GOV-20

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
