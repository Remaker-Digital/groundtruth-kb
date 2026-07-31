# WI-4782 Session Role Authority Audit

Generated: 2026-06-30T15:13:00Z
Bridge: `gtkb-wi4782-session-role-authority-audit`
Work item: `WI-4782`
Project authorization: `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`

## Claim

The scanned implementation surfaces mostly support the current authority split: durable registry role is dispatch/fallback authority, while a transcript-defined interactive session role governs in-session surfaces when present. The remaining actionable drift is wording debt, not a runtime marker-propagation failure.

## Scope

- Files scanned: 1165
- Candidate lines matched: 1388
- Scan roots: `CLAUDE.md, AGENTS.md, .claude/rules, .cursor, .codex, .agent, .api-harness, config/agent-control, groundtruth-kb/templates, .claude/hooks, .codex/gtkb-hooks, scripts, .claude/skills, .codex/skills`
- Machine-readable ledger: `.gtkb-state/role-authority-audit/wi4782-session-role-authority-audit.json`

## Candidate Summary

| Class | Meaning | CONTRADICTS | REVIEW | SUPPORTS | HISTORICAL |
| --- | --- | ---: | ---: | ---: | ---: |
| V1 | Registry leak into non-dispatcher gates. | 2 | 433 | 27 | 18 |
| V2 | Init-keyword marker propagation and session-marker continuity. | 8 | 168 | 20 | 13 |
| V3 | Durable-role terminology drift. | 1 | 155 | 82 | 7 |
| V4 | Backwards framing where session authority is described as overriding or bypassing durable role authority. | 13 | 378 | 54 | 9 |

## Findings

| ID | Severity | Class | Status | Finding | Evidence | Recommended action |
| --- | --- | --- | --- | --- | --- | --- |
| WI4782-F1 | P2 | V4 | CONTRADICTS | Startup disclosure still says session Prime authority is granted regardless of durable registry role | `config/agent-control/SESSION-STARTUP-INDEX.md:58` CONTRADICTS; `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md:32` CONTRADICTS; `scripts/session_self_initialization.py:5080` CONTRADICTS; `.codex/gtkb-hooks/last-user-visible-startup-pb.md:23` CONTRADICTS; `.cursor/gtkb-hooks/last-user-visible-startup-pb.md:36` CONTRADICTS | File a cleanup slice to replace the phrase with: session transcript role governs interactive in-session surfaces when declared; durable registry remains headless-dispatch routing and fallback authority. |
| WI4782-F2 | P2 | V3/V4 | CONTRADICTS | Core terminology still says interactive roles override durable roles | `AGENTS.md:100` CONTRADICTS; `CLAUDE.md:7` CONTRADICTS; `.claude/rules/canonical-terminology.md:806` CONTRADICTS; `.claude/rules/operating-role.md:154` CONTRADICTS; `scripts/_kb_attribution.py:244` CONTRADICTS | Normalize wording to session-stated role governs scoped interactive surfaces, while durable registry authority remains unchanged for durable assignment and headless dispatch. |
| WI4782-F3 | P3 | V1/V3 | REVIEW | Assigned-operating-role preambles can be read as durable-only unless session-resolved cross-reference is nearby | `AGENTS.md:92` REVIEW; `AGENTS.md:104` REVIEW; `.claude/rules/prime-builder-role.md:16` REVIEW; `.claude/rules/prime-builder-role.md:85` SUPPORTS | When touching these files for F1/F2, add local cross-reference text that assigned role means resolved session role for interactive surfaces, not durable role alone. |
| WI4782-C1 | Info | V2 | SUPPORTS | Init keyword propagation writes per-session markers | `scripts/session_self_initialization.py:7501` SUPPORTS; `scripts/session_self_initialization.py:7545` SUPPORTS; `scripts/workstream_focus.py:1302` SUPPORTS; `scripts/workstream_focus.py:1331` SUPPORTS | Do not reopen marker propagation unless a new failing runtime case appears. |
| WI4782-C2 | Info | V1 | SUPPORTS | Work-intent claim gate separates dispatch durable authority from interactive marker authority | `scripts/bridge_work_intent_registry.py:499` SUPPORTS; `scripts/bridge_work_intent_registry.py:467` SUPPORTS; `scripts/session_role_resolution.py:17` SUPPORTS; `scripts/session_role_resolution.py:240` SUPPORTS | Preserve this split while cleaning wording debt. |

## Notes

- V2 marker propagation is not the blocker. `scripts/session_self_initialization.py` handles `GTKB_BRIDGE_DISPATCH_KEYWORD` and writes per-session role markers; `scripts/workstream_focus.py` provides the per-session marker writer; `scripts/session_role_resolution.py` resolves per-session marker/envelope before durable fallback.
- The strongest cleanup candidate is the repeated phrase `::init gtkb pb grants Prime Builder authority regardless of durable registry role`. It appears in source startup rendering and generated cache files. The behavior is mostly right; the wording is backwards for the current authority model.
- Generated startup cache files are evidence, not the preferred edit target. Fix `scripts/session_self_initialization.py`, `config/agent-control/SESSION-STARTUP-INDEX.md`, and `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`, then regenerate caches through normal startup flow.

## Risk / Impact

Leaving the wording debt in place can cause future agents to treat durable registry role as something an interactive session bypasses, rather than as a separate authority used for durable assignment, headless dispatch, and fallback. That risks repeated bridge/claim/session-role confusion even though the runtime marker and claim code now fail closed correctly.

## Decision Needed

No owner decision is needed for this audit artifact. Follow-on cleanup should be filed as a normal bridge-governed implementation slice before mutating source, rules, config, or generated caches.
