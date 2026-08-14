# SoT Read Discipline

This rule auto-loads via the `{{HARNESS_RULES_DIR}}/` convention. It is the narrative authority for the SoT (source-of-truth) read-discipline enforcement layer landed in Slice 2A of `gtkb-platform-sot-consolidation-umbrella`.

## Authority

This rule cites and is governed by:

- `DCL-SOT-READ-HOOK-CONTRACT-001` v1 — the machine-checkable two-surface harness-specific hook contract.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 — the cross-cutting governance principle this rule operationalizes (clauses a–d of the Read-Discipline Extension).
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 — the `forbidden_substitutes` registry column the runtime hook consumes.
- `GOV-PLATFORM-SOT-REGISTRY-001` — the platform SoT artifact registry.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — the empirical foundation for the shell-command hook surface (governance record; retains its historical identifier).

## Runtime Behavior — Two-Surface Contract

The canonical hook at `{{HARNESS_HOOKS_DIR}}/sot-read-discipline.py` intercepts read intents at the pre-tool-use boundary and blocks reads against any registered `forbidden_substitutes` path with canonical-path guidance. Because different harnesses emit different pre-tool-use tool-event sets, the contract has two surface classes; each harness's projection registers the surface matching its native event model (registration rendered from `hooks/manifest.toml`, intent `read_access` plus `shell_exec`).

### Native-tool surface

For harnesses whose pre-tool-use events report read tools directly (`Read`, `Grep`, `Glob` or equivalents), the hook extracts the target path from the tool input:

- the file path field for direct reads
- the search path field for content searches
- the pattern's base directory for glob matching

### Shell-command surface

For harnesses whose pre-tool-use events report shell commands rather than read tools, a thin per-harness adapter (a projector output; see the harness-adapter record `DOC-SOT-READ-DISCIPLINE-HARNESS-ADAPTERS-001` in MemBase) pipes the payload into the canonical hook with the harness name in the environment. The hook's shell branch parses the command string for the following read/search verbs (initial set):

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

- `DELIB-20260673` — parallel-session fragmentation evidence: multiple AI sessions independently consulted different aliases of the same SoT, including a retired role mirror and another legacy alias, producing divergent state claims that the operator had to reconcile by hand.
- `DELIB-20260670` — manual-triage survey identifying 8 forbidden-substitute candidates AND the always-loaded / shell-readable falsifying class of substitutes: paths that get loaded automatically at session start (where caching would be invisible) AND paths that are shell-readable via Bash/PowerShell verbs (where agent-side self-discipline fails because the read happens before any GT-KB-aware logic runs).

The two-surface contract directly addresses the falsifying class: by intercepting at the pre-tool-use boundary on both the native-tool surface and the shell-command surface, the discipline catches the read at the earliest point any harness can be intercepted. The mechanical floor (the `forbidden_substitutes` registry column) ensures the discipline is owner-controlled and not relying on agent memory.

## Relationship to Other Rules

- `{{HARNESS_RULES_DIR}}/file-bridge-protocol.md` — bridge protocol authority; this rule operationalizes one aspect of the broader source-of-truth discipline that protocol depends on.
- `{{HARNESS_RULES_DIR}}/operating-model.md` — operating model framing; SoT read discipline is part of the platform's lifecycle-independence and audit-trail contract.
- `{{HARNESS_RULES_DIR}}/loyal-opposition.md` — LO review obligations; reviewers should flag PRs that introduce reads of registered forbidden substitutes without bypass justification.
- `{{HARNESS_RULES_DIR}}/prime-builder-role.md` — Prime Builder discipline; Prime SHOULD route reads through canonical readers per clause (a) of `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2.

## Doctor Check

The `_check_sot_read_discipline` doctor check (in `groundtruth_kb/project/doctor.py`) verifies effective hook coverage. See `DCL-SOT-READ-HOOK-CONTRACT-001` v1 for the 4-layer assertion contract. Initial severity is WARN; promotion to FAIL is a Slice 2B candidate after coverage audit.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
