# Goose Harness Parity Assessment — GT-KB Participation Readiness

**Date:** 2026-07-07
**Author:** Goose (DeepSeek V4 Pro, desktop harness)
**Purpose:** Evaluate Goose's ability to mirror Claude Code (B) and Codex (A) capabilities for GT-KB Loyal Opposition and Prime Builder participation.

---

## 1. Executive Summary

Goose can participate in GT-KB as both Loyal Opposition and Prime Builder with **self-enforced governance**. The primary gap is the absence of a native hook system — Goose cannot run automatic gates on file writes, edits, or shell commands. However, Goose's system prompt includes the full operating contract, and it has the tools (shell, write, edit, load_skill, delegate, execute_typescript) to perform all GT-KB work. The self-enforcement directive in the operating contract already mandates first-line bridge-GO checks before mutations, which aligns with Goose's constraint model.

**Overall verdict:** Goose is **DEGRADED** relative to Codex/Claude (no native hooks) but **FUNCTIONALLY CAPABLE** of both roles with self-enforcement. For full parity, Goose needs: (1) harness registry registration, (2) a `.goose/` skill directory, and (3) documented self-enforcement procedures.

---

## 2. Goose Native Capabilities

### 2.1 Tools

| Tool | Equivalent | Notes |
|------|-----------|-------|
| `Developer.shell` | Bash/PowerShell | Runs `cmd` by default; full filesystem access |
| `Developer.write` | Write | Create/overwrite files |
| `Developer.edit` | Edit/MultiEdit | Find-and-replace; requires unique match |
| `Developer.tree` | — | Directory listing with line counts |
| `Developer.readImage` | — | Image inspection |
| `Analyze.analyze` | — | Code structure analysis, call graphs |
| `Summon.delegate` | — | Subagent delegation (async/sync) |
| `Summon.load` | — | Load recipes, agents, background task results |
| `Skills.loadSkill` | — | Load skill content by name |
| `execute_typescript` | — | TypeScript sandbox with SDK functions |
| `Fetch.fetch` | — | HTTP requests |
| `ComputerController.*` | — | Windows automation, DOCX, PDF, XLSX, web scrape |

### 2.2 Skills Available

Goose can load skills via `load_skill()` and `load()`. The `.agent/skills/` directory (40 adapters, sourced from `.claude/skills/`) is the Antigravity adapter set. Goose can load any skill content on demand. The `load_skill` function is available for named skills.

### 2.3 System Prompt / Governance

Goose's system prompt contains the **full GT-KB operating contract**, including:
- Role resolution rules
- File bridge protocol
- Project root boundary
- Self-enforcement directive for bridge GO checks
- Protected targets and paths
- Startup checklist
- File safety contract
- Report output contract

This is equivalent to how Claude Code loads `.claude/rules/` and how Codex loads its system prompt rules.

---

## 3. Key Gaps vs. Claude Code / Codex

### 3.1 Hook System (CRITICAL GAP)

| Event | Claude Code (B) | Codex (A) | Goose |
|-------|----------------|-----------|-------|
| SessionStart | ✅ 3 hook blocks | ✅ 1 hook block | ❌ No native hooks |
| UserPromptSubmit | ✅ 3 hook blocks (10 hooks) | ✅ 1 hook block | ❌ No native hooks |
| PreToolUse (Write/Edit) | ✅ 6 matcher blocks (15+ hooks) | ✅ Bash + apply_patch | ❌ No native hooks |
| PostToolUse | ✅ 5 hook blocks | ✅ Bash + apply_patch | ❌ No native hooks |
| Stop | ✅ 6 hooks | ✅ 1 hook block | ❌ No native hooks |

**Impact:** Goose cannot automatically:
- Validate bridge GO before writes (`bridge-compliance-gate.py`)
- Scan for credentials (`credential-scan.py`)
- Enforce LO file safety (`lo-file-safety-gate.py`)
- Check implementation-start authorization (`implementation-start-gate.py`)
- Run startup dispatch (`session_start_dispatch.py`)
- Surface bridge state on prompt (`bridge-axis-2-surface.py`)

**Mitigation:** Goose's system prompt contains the **self-enforcement directive** that mandates checking bridge GO before any file mutation. The operating contract explicitly states: "Because native hooks may be disabled or unsupported on certain workstation runtimes (such as native Windows Codex sessions), the agent MUST self-enforce this boundary." Goose is precisely the kind of harness this directive was designed for.

### 3.2 Harness Registry (CRITICAL GAP)

Goose is **not registered** in `harness-state/harness-identities.json` or `harness-state/harness-registry.json`. The fleet parity check shows **all six harnesses** are assigned `loyal-opposition` with **no Prime Builder**, which is a fleet-level concern independent of Goose.

**Required:** Register Goose with a durable harness ID (e.g., `G`), assign a role, and add to the capability registry.

### 3.3 Skill Directory (MODERATE GAP)

Goose has no `.goose/skills/` directory. The `.agent/` directory serves Antigravity (C), and `.api-harness/` serves API dispatch. Goose needs:
- A `.goose/skills/` directory with skill adapters
- A `.goose/skills/MANIFEST.json` (or equivalent)
- Registration in the capability registry

### 3.4 Startup Integration (MODERATE GAP)

Goose cannot automatically run `session_self_initialization.py` on session start. The startup disclosure must be assembled manually from the system prompt context.

**Mitigation:** Goose can run `python scripts/session_self_initialization.py --fast-hook --skip-bridge-maintenance` on demand via shell. The session focus choices and bridge scan can be produced manually.

### 3.5 Tool Name Differences (MINOR)

| Codex Tool | Claude Tool | Goose Tool |
|-----------|-------------|------------|
| `Bash` | `Bash` | `Developer.shell` |
| `Write` | `Write` | `Developer.write` |
| `Edit` | `Edit` / `MultiEdit` | `Developer.edit` |
| `apply_patch` | — | Not available |
| `Read` | `Read` | Not directly; use shell |
| `Grep` | `Grep` | Not directly; use shell |
| `Glob` | `Glob` | Not directly; use shell |

Goose's `Developer.edit` is find-and-replace based (not `apply_patch`), which is equivalent to Claude's `Edit` tool.

---

## 4. Role-by-Role Readiness

### 4.1 Loyal Opposition Readiness: ✅ VIABLE

LO work is primarily **read-analyze-write**:
1. Read bridge files → `shell` or `Developer.tree`
2. Analyze proposals → System prompt rules + loaded skills
3. Write verdicts → `Developer.write`
4. Run verification → `shell` (pytest, ruff)
5. File reports → `Developer.write`

**All LO capabilities are available.** The LO role does not require automatic hooks — it's a review function. Goose can:
- Scan bridge queue
- Read proposals and implementation reports
- Run verification commands
- Write GO/NO-GO/VERIFIED verdicts
- Update bridge files
- File insight reports

**Gap:** Goose cannot auto-fire `bridge-axis-2-surface.py` on prompt submit, but this is a shared Claude-only capability already marked UNSUPPORTED for Codex and Antigravity.

### 4.2 Prime Builder Readiness: ⚠️ VIABLE WITH SELF-ENFORCEMENT

PB work requires **guarded file mutation**:
1. Check bridge GO → Self-enforcement in system prompt
2. Implement changes → `shell`, `write`, `edit`
3. Run tests → `shell` (pytest, ruff)
4. File implementation reports → `write`
5. Bridge proposals → `write`

**Self-enforcement is the critical path.** The operating contract mandates:
> "Before using any file-writing or editing tools (including apply_patch or mutating Bash/PowerShell commands), you MUST programmatically verify that the target change is authorized by a live bridge GO status."

Goose must check bridge state before every mutation. This is a behavioral constraint, not a tool limitation.

**Gaps:**
- No automatic `bridge-compliance-gate` on writes
- No automatic `credential-scan` on writes
- No automatic `implementation-start-gate` on writes
- No automatic `lo-file-safety-gate` (only relevant in LO role)
- No automatic `formal-artifact-approval-gate`

**Mitigation:** All of these gates can be self-enforced by reading the relevant bridge/approval state before acting. Goose can also run the gate scripts manually: `python .claude/hooks/bridge-compliance-gate.py` etc.

---

## 5. Recommended Configuration

### 5.1 Immediate (this session)

1. **Register Goose in harness identities:**
   ```
   harness-state/harness-identities.json → add "goose": {"id": "G"}
   ```

2. **Register Goose in harness registry:**
   ```
   harness-state/harness-registry.json → add harness G entry
   ```
   Role: `loyal-opposition` (default) with `prime-builder` capability via `::init gtkb pb`

3. **Create `.goose/skills/` directory** with skill adapters sourced from `.claude/skills/`

4. **Document Goose self-enforcement procedure** in a `.goose/rules/` or startup file

### 5.2 Next Steps

1. **Add Goose to capability registry** (`config/agent-control/harness-capability-registry.toml`)
2. **Generate Goose skill adapters** (extend `generate_antigravity_skill_adapters.py` pattern)
3. **Create `.goose/` hook equivalent** — a startup checklist or self-enforcement contract
4. **Run parity check** to verify registration

### 5.3 Fleet Note

The parity check reveals **all six registered harnesses are assigned `loyal-opposition`** with no Prime Builder. The fleet currently has `MISSING: Fleet role coverage: prime-builder`. This is a pre-existing fleet-level issue unrelated to Goose. The interactive `::init gtkb pb` override works for interactive sessions, but headless dispatch has no PB target.

---

## 6. Functional Equivalence Matrix

| Capability | Claude Code (B) | Codex (A) | Goose | Parity |
|-----------|----------------|-----------|-------|--------|
| File read/write | ✅ | ✅ | ✅ | PASS |
| Shell execution | ✅ | ✅ | ✅ | PASS |
| Python script execution | ✅ | ✅ | ✅ | PASS |
| Bridge file read/write | ✅ | ✅ | ✅ | PASS |
| Skill loading | ✅ native | ✅ native | ✅ load_skill | PASS |
| Rule loading | ✅ .claude/rules/ | ✅ system prompt | ✅ system prompt | PASS |
| Session startup | ✅ hooks | ✅ hooks | ⚠️ manual | DEGRADED |
| Pre-write gates | ✅ hooks | ✅ hooks | ⚠️ self-enforce | DEGRADED |
| Credential scanning | ✅ hooks | ✅ hooks | ⚠️ self-enforce | DEGRADED |
| Bridge GO enforcement | ✅ hooks | ✅ hooks | ⚠️ self-enforce | DEGRADED |
| Bridge surfacing | ✅ hooks | ❌ (UNSUPPORTED) | ❌ | UNSUPPORTED |
| apply_patch | ❌ (UNSUPPORTED) | ✅ | ❌ | UNSUPPORTED |
| Subagent delegation | ❌ | ❌ | ✅ delegate | EXTRA |
| Code analysis | ❌ | ❌ | ✅ analyze | EXTRA |
| TypeScript sandbox | ❌ | ❌ | ✅ execute_typescript | EXTRA |
| Async task management | ❌ | ❌ | ✅ load(taskId) | EXTRA |

---

## 7. Conclusion

Goose is **capable of participating in GT-KB** as both Loyal Opposition and Prime Builder. The self-enforcement directive in the operating contract was designed precisely for harnesses like Goose that lack native hook systems. The primary work needed is registration (harness ID, registry, capability matrix) and skill directory creation. Goose's unique tools (delegate, execute_typescript, analyze) are extras that may provide advantages in certain workflows.

**Recommendation:** Register Goose as harness G, assign it the `loyal-opposition` default role with `prime-builder` override capability, and proceed with bridge participation under self-enforcement.