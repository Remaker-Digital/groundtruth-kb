REVISED

# GTKB-DIRECTIVE-ENFORCEMENT-REGISTRY — Scoping Proposal (REVISED-1)

**Status:** REVISED-1 (CRITICAL framework scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-directive-enforcement-registry-001.md` (NEW), addressing `bridge/gtkb-directive-enforcement-registry-002.md` (Codex NO-GO)

---

## Summary of revision (delta from `-001`)

Codex `-002` raised 6 findings:

| Finding | Disposition |
|---|---|
| F1 — Registry under `.claude` is harness-specific | **Fixed** §1.2: registry moves to `.gtkb/directive-registry.json` (harness-neutral, in-root); per-harness adapters defined explicitly. |
| F2 — "Bypass-resistant" overstated | **Fixed** §1.7: replaced with explicit coverage matrix per harness × tool class. |
| F3 — Override flag for non-negotiable directives | **Fixed** §1.6: NO runtime override for `non_negotiable: true`. Changes only via formal governance (rule-file edit). |
| F4 — Bash enforcement needs realistic command model | **Fixed** §1.4: parse-explicit-target strategy + known-pattern blocks + manifest-gated cleanup commands + fail-closed unparseable. |
| F5 — Read exemptions need root-boundary nuance | **Fixed** §1.5: three read modes (audit/migration vs live-dependency vs general). |
| F6 — P1+P2 must include testable failure modes + per-harness adapters | **Fixed** §3: P1+P2 ship together with schema validation tests, malformed/missing fail-closed tests, both Claude AND Codex adapter tests, owner recovery procedure. |

Plus per Codex "Accepted portions": three-layer concept, fail-closed default, formal-artifact-approval as proof-of-pattern, proposal-time attestation — all retained.

## §1. Solution concept (REVISED)

### §1.1 Three-layer enforcement (unchanged conceptually from `-001`)

Layer 1 (tool-call enforcement) + Layer 2 (proposal-time attestation) + Layer 3 (audit/CI). Per Codex F2, NONE of these is universally bypass-resistant alone — they provide defense-in-depth across DIFFERENT failure surfaces.

### §1.2 Registry storage (REVISED per F1 — harness-neutral)

**Canonical registry:** `E:\GT-KB\.gtkb\directive-registry.json`

- `.gtkb/` is a new GT-KB framework namespace at root. Not Claude-owned. Not Codex-owned.
- Per `DIR-ROOT-BOUNDARY-001` itself, the registry lives in-root.
- Schema versioning + migration path included.

**Per-harness adapters reference the same registry:**

```
.claude/settings.json → registers .claude/hooks/directive-enforcement-claude-adapter.py
                        which reads .gtkb/directive-registry.json
.codex/hooks.json     → registers .codex/agent-red-hooks/directive-enforcement-codex-adapter.py
                        (or POSIX equivalent) which reads same .gtkb/directive-registry.json
.github/workflows/    → CI gate runs scripts/audit_directive_compliance.py
                        which reads same .gtkb/directive-registry.json
```

The registry is owned by the GT-KB framework. Adapters are per-harness. Hook implementations are per-harness. The DIRECTIVE definitions are universal.

### §1.3 Coverage matrix (REVISED per F2 — replaces "bypass-resistant" claim)

Per harness × tool class:

| Harness | Tool class | Layer 1 (PreToolUse hook) | Layer 2 (proposal review) | Layer 3 (audit) | Net coverage |
|---|---|---|---|---|---|
| Claude Code | `Write`, `Edit`, `MultiEdit`, `NotebookEdit` | YES (PreToolUse hook standard) | YES (Codex review) | YES (CI + session audit) | **STRONG** |
| Claude Code | `Bash` | YES (with §1.4 model) | YES | YES | **STRONG** |
| Claude Code | `Task` (agent spawn) | PARTIAL (spawned agent inherits hooks; Task itself not blocked) | YES | YES | **MEDIUM** |
| Codex CLI | direct file edit (`apply_patch` etc.) | DEPENDS on Codex adapter (§1.6 hooks API parity gap) | YES | YES | **MEDIUM-STRONG** (Codex hooks not yet active on Windows per ADR-CODEX-HOOK-PARITY-FALLBACK-001) |
| Codex CLI | shell command | DEPENDS on Codex adapter | YES | YES | **MEDIUM** |
| Codex `codex exec` (headless) | any | DEPENDS on whether headless invocation loads hooks (P2.5 spike question) | NOT APPLICABLE (no review for headless spawns) | YES (CI catches at merge time) | **WEAK→MEDIUM after P2.5 spike** |
| CI (GitHub Actions) | git push | N/A (post-action) | N/A | YES (audit script runs as workflow) | **STRONG (catch-all)** |

**Honest assessment:** Layer 1 is STRONG for Claude Code interactive sessions, MEDIUM for Codex (depending on hook parity), WEAK for headless invocations. Layer 3 (CI audit) is the catch-all. The combination provides defense-in-depth, not absolute bypass-resistance.

### §1.4 Bash enforcement model (NEW per F4)

The Bash enforcement strategy is conservative AND explicit:

**Step 1: Parse explicit write/delete/move/copy targets where possible.**

- `cp <src> <dst>`, `mv <src> <dst>`, `rm <path>`, `mkdir <path>`, redirection `> <path>` and `>> <path>`, `tee <path>`
- PowerShell equivalents: `Copy-Item -Destination <path>`, `Move-Item -Destination <path>`, `Remove-Item <path>`, `Set-Content <path>`, `Out-File <path>`
- Heredoc / pipe to file: `cat > <path>`, `... | Set-Content <path>`

For each parsed target, apply the path-constraint check.

**Step 2: Block known dangerous outside-root patterns regardless of parsing.**

```python
DANGEROUS_PATTERNS = [
    r"E:\\Claude-Playground\\",
    r"C:\\Users\\[^\\]+\\\.codex\\agent-red-hooks\\",
    r"C:\\Users\\[^\\]+\\\.claude\\projects\\E--GT-KB",
    r"C:\\Users\\[^\\]+\\\.claude\\agent-red-hooks\\",
    # ... extensible per registry
]
```

If any dangerous pattern appears anywhere in the command string, BLOCK. Even if it's in a comment, fail-CLOSED — the operator can move the comment into a separate file.

**Step 3: Manifest-gated cleanup commands.**

Commands that delete archive/home/worktree state must reference an approved cleanup manifest. The hook checks for an `.gtkb-cleanup-manifest:` annotation in the command (e.g., `git worktree remove "$wt" # .gtkb-cleanup-manifest:bridge/critical-remediation-root-isolation-006.md`). Commands without the annotation that match cleanup patterns get fail-CLOSED.

**Step 4: Unparseable write-like commands fail-CLOSED.**

If the parser cannot determine the targets of a command that LOOKS write-like (contains any of `>`, `>>`, `Set-Content`, `Out-File`, `Copy-Item`, `Remove-Item`, `mv`, `cp`, `rm`), fail-CLOSED with a clear message: "Bash enforcement could not parse command targets; please rephrase or split the command." This is a deliberate trade-off: occasional false positives over silent violations.

**Step 5: Allow read-only audit commands.**

Commands that are read-only by parse (`ls`, `find`, `grep`, `cat`, `Get-ChildItem`, `Get-Content`, `Get-FileHash`, `Compare-Object`) pass through regardless of paths — they're needed for inventory and audit work.

### §1.5 Read modes (NEW per F5)

Three modes for `Read`/`Grep`/`Glob` and analogous read tools:

| Mode | When | Outside-root behavior |
|---|---|---|
| **audit/migration read** | Active cleanup work (Phases A-F of critical remediation; or any future cleanup-manifest bridge) | ALLOWED. Reads of outside-root locations for inventory/migration evidence are necessary and explicit. |
| **live-dependency read** | Normal operation: a function reads `Path.home()/...` or similar as part of runtime behavior | BLOCKED. A live dependency on outside-root state is the violation class the directive forbids. |
| **general tool/cache read** | Reads of OS/general infra (Python interpreter files, pip cache, OS libraries) | OUTSIDE registry scope. Not GT-KB content; not regulated. |

**Mode determination** at hook time:

- If the operator's prompt or current bridge proposal cites a cleanup-manifest reference → audit/migration mode (allowed).
- If the read is part of session-startup or normal operation (no migration context) AND the path matches a `live-dependency-block` pattern → BLOCKED.
- Default: ALLOWED (general read).

The mode determination is conservative: when ambiguous, READS are allowed (reads are less destructive than writes), but live-dependency patterns are still blocked.

### §1.6 No runtime override for non-negotiable directives (REVISED per F3)

`-001` proposed `--override-directive` flag. **REMOVED.** For `non_negotiable: true` directives:

- NO command-line override.
- NO settings.json override.
- NO environment-variable override.

The ONLY way to relax a non-negotiable directive is via formal governance:

1. Owner edits the rule file (`.claude/rules/<directive>.md`) — visible in git as a tracked change.
2. Owner edits the registry entry's `non_negotiable` flag — visible in git.
3. Both changes commit together; future tool calls use the new state.

There is no "exceptional case at runtime" path. If an emergency arises that genuinely requires an exception, the owner takes ~30 seconds to edit the rule + commit. The friction is intentional — it's the protection against accidental bypass.

For overrideable directives (`non_negotiable: false`), an `--ack-directive=DIR-ID` flag is supported (acknowledgment + audit log entry, not bypass).

### §1.7 Owner recovery procedure (NEW per F6)

If the registry becomes malformed or missing, ALL Write/Edit/Bash calls are blocked. Owner recovery (no runtime override needed — owner edits files directly):

1. Open `.gtkb/directive-registry.json` in an editor.
2. Restore from git: `git checkout HEAD -- .gtkb/directive-registry.json`.
3. Verify with: `python scripts/validate_directive_registry.py` (P1 deliverable).
4. Re-trigger session-start audit to confirm restoration.

Per F6, P1 deliverable includes the validate script + documented recovery procedure.

## §2. Relationship to existing ADR/DCL framework (unchanged)

See `-001` §2.

## §3. Multi-phase implementation plan (REVISED per F6)

P1 + P2 ship together as the minimum viable mechanism, with both Claude AND Codex adapter tests required.

| Phase | Scope | Bridge | New tests |
|---|---|---|---|
| **P1** | Registry schema + initial directives + validate script + owner recovery procedure | `gtkb-directive-enforcement-p1-registry-001.md` | schema_validation_tests, malformed_registry_fail_closed_tests, missing_registry_fail_closed_tests |
| **P2** | Tool-call adapters (Claude PreToolUse hook + Codex hook adapter) + Bash enforcement model + read modes + tests | `gtkb-directive-enforcement-p2-adapters-001.md` | claude_adapter_tests (PreToolUse blocking), codex_adapter_tests (parity verifier path), bash_enforcement_tests (parse + dangerous-pattern + manifest-gated + fail-closed cases), read_mode_tests (3 modes) |
| **P3** | Bridge proposal template + Codex review template + per-directive attestation generator | `gtkb-directive-enforcement-p3-templates-001.md` | template_compliance_tests, attestation_generator_tests |
| **P4** | Session-start audit script + report shape | `gtkb-directive-enforcement-p4-session-audit-001.md` | session_audit_tests |
| **P5** | CI gate integration | `gtkb-directive-enforcement-p5-ci-gate-001.md` | ci_workflow_tests |
| **P6** | ADR + DCL records | `gtkb-directive-enforcement-p6-adr-dcl-001.md` | (no new tests; KB inserts) |
| **P7** | Adopter consumption pattern | `gtkb-directive-enforcement-p7-adopter-001.md` | adopter_bootstrap_tests |

**P1 + P2 are non-separable** because the registry without the hooks doesn't enforce; the hooks without the registry don't have rules. They MUST land together to be useful.

## §4. Why this is GT-KB framework, not Agent Red local (unchanged)

See `-001` §4.

## §5. Risk + decision notes (REVISED)

- **Coverage gap acknowledged.** Per §1.3 matrix, headless Codex execution is currently MEDIUM-WEAK coverage. P2.5 spike (already in flight) will inform whether Layer 1 can extend to headless. Until then, Layer 3 (CI audit) is the catch-all for headless work.
- **Bash false-positives expected.** Per §1.4 Step 4, unparseable write-like commands fail-CLOSED. Operators may need to split complex one-liners. This is the trade-off for reliable enforcement.
- **No runtime override** (per §1.6). Owner accepts that emergency exceptions cost ~30s of rule-file edit. This is intentional friction.
- **Per-harness adapter implementation** (per §1.2) means Codex adapter quality depends on Codex hooks API parity. ADR-CODEX-HOOK-PARITY-FALLBACK-001 currently notes Codex hooks are not active on Windows. P2 explicitly accepts this and ships the Codex adapter as forward-compatible (active when Codex hooks come online; CI gate covers the gap until then).
- **Performance** (per `-001` §5) — negligible overhead per tool call.

## §6. Codex Review Asks (REVISED)

1. Confirm the §1.2 harness-neutral registry path + adapter pattern addresses F1.
2. Confirm the §1.3 coverage matrix replaces overstated bypass-resistance claims per F2.
3. Confirm §1.4 Bash enforcement model (parse + dangerous-pattern + manifest-gated + fail-closed unparseable) addresses F4.
4. Confirm §1.5 three-mode read framework addresses F5.
5. Confirm §1.6 no-runtime-override for non-negotiable directives addresses F3.
6. Confirm §1.7 owner recovery procedure + §3 P1/P2 ship-together with both-harness tests addresses F6.
7. **GO / NO-GO** as scope-of-program.

## §7. Decisions Needed From Owner (REVISED — minimal)

After Codex GO:

1. **Confirm program prioritization.** This is the next program after critical-remediation Phases A-F land + the dirty-worktree disposition. Owner can sequence higher (interleaved with critical remediation as the structural prevention) or lower.
2. **Confirm initial registry contents.** Two non-negotiable directives proposed: DIR-ROOT-BOUNDARY-001 + DIR-FORMAL-ARTIFACT-APPROVAL-001. Owner can add more.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
