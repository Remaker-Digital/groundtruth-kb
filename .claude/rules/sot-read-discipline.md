# SoT Read Discipline

This rule auto-loads via the `.claude/rules/` convention. It is the narrative authority for the SoT (source-of-truth) read-discipline enforcement layer landed in Slice 2A of `gtkb-platform-sot-consolidation-umbrella`.

## Authority

This rule cites and is governed by:

- `DCL-SOT-READ-HOOK-CONTRACT-001` v1 — the machine-checkable two-surface harness-specific hook contract.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 — the cross-cutting governance principle this rule operationalizes (clauses a–d of the Read-Discipline Extension).
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 — the `forbidden_substitutes` registry column the runtime hook consumes.
- `GOV-PLATFORM-SOT-REGISTRY-001` — the platform SoT artifact registry.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — the empirical foundation for the Codex hook surface (Bash/apply_patch, not Read/Grep/Glob).

## Runtime Behavior — Two-Surface Contract

The canonical hook at `.claude/hooks/sot-read-discipline.py` intercepts read intents at the PreToolUse boundary and blocks reads against any registered `forbidden_substitutes` path with canonical-path guidance. Because Claude Code and Codex CLI emit different PreToolUse tool-event sets, the contract is harness-specific:

### Claude side

PreToolUse fires on `tool_name ∈ {Read, Grep, Glob}`. The canonical hook is registered in `.claude/settings.json` with matcher `"Read|Grep|Glob"`. It extracts the target path from:

- `tool_input.file_path` for `Read`
- `tool_input.path` for `Grep`
- `tool_input.pattern` for `Glob` (treats the pattern's base directory as the target)

### Codex side

PreToolUse fires on `tool_name ∈ {Bash, apply_patch}`. The canonical hook does NOT register `Read/Grep/Glob` on the Codex side — that would be a non-intercepting (false-green) registration. Instead, a thin Codex adapter at `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` is registered in `.codex/hooks.json` with matcher `"Bash"`. The adapter pipes the PreToolUse payload via subprocess into the canonical hook with `GTKB_HARNESS_NAME=codex` env override.

The canonical hook's Codex branch parses the `tool_input.command` string for the following read/search verbs (initial set):

| Verb / form | Alias(es) | Path extraction |
|-------------|-----------|-----------------|
| `Get-Content <path>` | `gc <path>`, `cat <path>` | first positional arg after the verb |
| `Select-String -Path <path> [-Pattern X]` | `sls -Path <path>` | value of `-Path` flag |
| `Get-ChildItem -Path <path> [-Recurse] [-Filter X]` | `gci -Path <path>` | value of `-Path` flag |
| `Get-ChildItem <path>` (positional) | `gci <path>` | first positional arg |
| `rg [flags] <pattern> <path>` | — | last positional arg |
| `grep [flags] <pattern> <path>` | — | last positional arg |

Future verbs may be added in subsequent slices via a versioned update to `DCL-SOT-READ-HOOK-CONTRACT-001`. The doctor check stays at severity WARN initially to surface coverage gaps without blocking.

## Bypass Path — Owner-Authorized Only

The runtime hook block is mechanical and cannot be bypassed by agent self-discipline. The only sanctioned bypass is:

```text
GTKB_SOT_READ_DISCIPLINE_BYPASS=1 <command>
```

Set in the shell environment for a single command and document the rationale in session memory. The bypass is reserved for legitimate exceptional cases:

- Debugging the hook itself
- Archive recovery operations
- Owner-directed audit work that requires reading a forbidden substitute for historical inspection (not for current-state claims)

The bypass surface MUST NOT be used to subvert the discipline for routine work. Repeated bypass invocations within a single session are a smell that should prompt owner consultation rather than reflexive use. Sessions that use the bypass MUST record the use + rationale in their session-memory log.

## Historical Motivation

The discipline arose from two strands of evidence:

- `DELIB-20260673` — parallel-session fragmentation evidence: multiple AI sessions independently consulted different aliases of the same SoT (e.g., one read `harness-state/role-assignments.json` directly while another read the legacy mirror), producing divergent state claims that the operator had to reconcile by hand.
- `DELIB-20260670` — manual-triage survey identifying 8 forbidden-substitute candidates AND the always-loaded / shell-readable falsifying class of substitutes: paths that get loaded automatically at session start (where caching would be invisible) AND paths that are shell-readable via Bash/PowerShell verbs (where agent-side self-discipline fails because the read happens before any GT-KB-aware logic runs).

The two-surface harness-specific contract directly addresses the falsifying class: by intercepting at PreToolUse and parsing both Claude tool-events AND Codex Bash command verbs, the discipline catches the read at the earliest point any harness can be intercepted. The mechanical floor (the `forbidden_substitutes` registry column) ensures the discipline is owner-controlled and not relying on agent memory.

## Relationship to Other Rules

- `.claude/rules/file-bridge-protocol.md` — bridge protocol authority; this rule operationalizes one aspect of the broader source-of-truth discipline that protocol depends on.
- `.claude/rules/operating-model.md` — operating model framing; SoT read discipline is part of the platform's lifecycle-independence and audit-trail contract.
- `.claude/rules/loyal-opposition.md` — LO review obligations; reviewers should flag PRs that introduce reads of registered forbidden substitutes without bypass justification.
- `.claude/rules/prime-builder-role.md` — Prime Builder discipline; Prime SHOULD route reads through canonical readers per clause (a) of `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2.

## Doctor Check

The `_check_sot_read_discipline` doctor check (in `groundtruth_kb/project/doctor.py`) verifies effective hook coverage. See `DCL-SOT-READ-HOOK-CONTRACT-001` v1 for the 4-layer assertion contract. Initial severity is WARN; promotion to FAIL is a Slice 2B candidate after coverage audit.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
