REVISED

# GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL — Scoping Proposal (REVISED-2)

Author: Prime Builder (Claude Code)
Date: 2026-05-02 (S327)
Status: REVISED (responding to Codex NO-GO at `-004.md`)

## Revision Rationale (REVISED-2)

Codex NO-GO at `-004.md` issued 1 P1 blocking finding (Prime-fixable). REVISED-1 (`-003.md`) resolved the prior 4 findings (path/schema, prior deliberations, sibling dependency, pinned defaults). The remaining issue:

- **F1** — Hard-blocking on `error` severity assigned to a PostToolUse hook, but PostToolUse runs AFTER the write completes. Existing blocking gates in this repo (e.g., `bridge-compliance-gate.py`) are PreToolUse and read `tool_input.content` BEFORE the write. Resolved by adopting Codex's recommended architecture: shared library + PreToolUse Write/Edit hook for deny-capable checks; PostToolUse only for warn-only audit; existing `bridge-compliance-gate.py` extension calls the same shared library.

**Material changes from `-003.md`:**

- §"Change 3" architecture rewritten: shared library `term_disambiguation.py` + PreToolUse hook (deny-capable) + PostToolUse hook (audit-only).
- Test plan T2/T4/T8/T9/T12/T17 updated to assert PreToolUse deny vs PostToolUse audit separately.
- `bridge-compliance-gate.py` extension architecture clarified: it calls the same shared library, not a parallel logic path.
- `[defaults]` retained from REVISED-1 (all 7 pinned values unchanged); their enforcement event is now PreToolUse for `error` severities.

All other sections unchanged from REVISED-1; carry forward.

## Origin

Owner directive 2026-05-02 (S327, fourth turn) — full verbatim text at `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md` §"Origin". Owner observed chronic vagueness in canonical-vs-common term use; requested structural mechanical fix that disambiguates specific artifact / class of artifact / procedure / general English. Candidate Deliberation Archive entry: `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

1. **`.claude/rules/operating-model.md` §2** — canonical terminology with allowed synonyms and forbidden uses. Constraint: this proposal mechanically enforces forbidden-use rules at PreToolUse.

2. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol mandatory linkage gate. Constraint: proposal compliance.

3. **`.claude/rules/project-root-boundary.md`** — all artifacts within `E:\GT-KB`. Constraint: policy file at `groundtruth-kb/templates/rules/canonical-terminology-policy.toml`; shared library at `groundtruth-kb/src/groundtruth_kb/term_disambiguation.py`.

4. **`.claude/rules/deliberation-protocol.md`** — owner-directive archival; deliberation-search obligation. Constraint: this proposal includes Prior Deliberations.

5. **`GOV-ARTIFACT-APPROVAL-001`** — formal-artifact approval contract. Constraint: new policy file is a managed-rule template; Slice 1 carries approval packet.

6. **`GOV-19-A1`** — outside-in testing. Constraint: tests exercise hook public surface (PreToolUse/PostToolUse events), not internal helpers.

7. **`GOV-20`** — architecture decisions; cross-cutting. Constraint: IPR/CVR per slice.

8. **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — repetitive AI plumbing is a defect. Constraint: this proposal converts term-disambiguation from prompt-time recall to deterministic gate.

9. **`groundtruth-kb/templates/rules/canonical-terminology.toml`** — existing profile-aware doctor config. Constraint: this proposal does NOT modify this file's schema; sibling policy file composes with it.

10. **`groundtruth-kb/templates/rules/canonical-terminology.md`** — existing managed-rule glossary. Constraint: term entries here are source-of-truth for which terms have policies.

11. **`bridge/gtkb-canonical-terminology-surface-implementation-012.md`** (VERIFIED) — prior architecture decision. Constraint: this proposal does not contradict; extends with sibling policy file using same managed-rule pattern.

12. **`groundtruth-kb/templates/managed-artifacts.toml`** — existing registry. Constraint: new policy file gets new registry row `rule.canonical-terminology-policy` following same pattern.

13. **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** *(per Codex F1 evidence at lines 3, 11, 219-233)* — existing PreToolUse Write/Edit hook that reads `tool_input.content` before write. Constraint per Codex F1: this proposal's deny-capable enforcement uses the same PreToolUse pattern; bridge-compliance-gate.py is extended to call the shared library for bridge-specific Tier B escalation.

14. **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** — smart-poller dispatch. Constraint: hook runs in dispatch-spawned headless sessions; T10 verifies.

15. **`bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`** (sibling REVISED-2) — primer proposal. Constraint: this proposal is **decoupled** per F3 of `-002.md` — defines minimum term set independent of primer state.

16. **`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-005.md`** (sibling REVISED-2; GO at `-006.md`) — backlog proposal where "backlog" is the running case study. Constraint: this proposal's lint applies to canonical "Backlog" usage in subsequent backlog-program proposals.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`. Relevant prior deliberations:

- **`DELIB-0722` / `DELIB-1180`** — prior canonical-terminology bridge thread. **Preserved + extended.** This proposal does not contradict verified Option B architecture; extends with sibling policy file.
- **`DELIB-1179`, `DELIB-1018`, `DELIB-1017`, `DELIB-0804`** — earlier canonical-terminology context. **Preserved.**
- **`DELIB-S324-OM-DELTA-0004-CHOICE`** — backlog ordering semantics. **Preserved.**
- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** — fragmentation finding. **Built on.**
- **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — supports deterministic-service conversion. **Built on.**
- **`DELIB-1404`** — candidate-vs-approved spec wording. **Preserved.**
- **`DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`** + **`DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`** + **`DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`** (this session, candidates) — coupled motivations.

**Differentiation:** No prior deliberation already establishes per-term disambiguation policy + PreToolUse-enforced hook architecture. This proposal introduces new mechanism; does NOT contradict verified canonical-terminology thread.

## Problem Statement (unchanged from -001.md, abridged)

§2 of `operating-model.md` defines forbidden uses with no mechanical enforcement. Three failure modes (specific artifact / class / procedure) plus general English. Empirical drift evidence in this S327 session (work_items/backlog_items conflation; wrong template paths cited despite existing VERIFIED architecture). Smart-poller spawns + bridge-protocol gap + forbidden-use violations all undetected.

## Proposed Direction (REVISED-2)

A 3-tier disambiguation policy declared in sibling `canonical-terminology-policy.toml`, enforced via shared library + PreToolUse hook + PostToolUse audit + `bridge-compliance-gate.py` extension. Self-contained: minimum term set defined here independently of primer state.

### Change 1 — Sibling policy file (unchanged from REVISED-1)

`groundtruth-kb/templates/rules/canonical-terminology-policy.toml` (new managed-rule template):

```toml
# Canonical-terminology disambiguation policy. Composes with canonical-terminology.toml.
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

[meta]
version = "1.0.0"
# Source-of-truth term list: canonical-terminology.md (sibling glossary).
# This file declares per-term enforcement metadata.

[defaults]
# Pinned per Codex `-002.md` F4 (carry forward from REVISED-1):
tier_b_severity_in_bridge_proposals = "error"     # block in bridge proposals (PreToolUse)
tier_b_severity_elsewhere = "warn"                 # warn in other writes (PostToolUse audit)
tier_c_strictness = "strict"                       # demonstrative + canonical word + no ID = flag
forbidden_uses_severity = "error"                  # always block (PreToolUse)
sentence_initial_capitalization = "ignore"         # ignore for Tier B detection
file_level_disable_marker = "<!-- term-disambiguation: off -->"
override_syntax = "{!common: <term>}"

[term."backlog"]
disambiguation_tier = "B"
specific_id_prefix = "BL"

[term."MemBase"]
disambiguation_tier = "A"
distinctive_form = "MemBase"

# ... per-term entries for each canonical term in canonical-terminology.md
```

### Change 2 — Self-contained minimum term set (unchanged from REVISED-1)

22 owner-required terms declared in policy file regardless of primer state. T17 verifies decoupling.

### Change 3 — Shared library + PreToolUse + PostToolUse + bridge-compliance-gate extension (REVISED-2 per Codex F1)

Architecture pivot. Three components:

**Component 3a — Shared library `groundtruth-kb/src/groundtruth_kb/term_disambiguation.py`** (new):

- Single Python module containing all policy logic.
- Public functions: `evaluate_content(content: str, *, file_path: Path, policy: PolicyConfig) -> List[Violation]`.
- Each `Violation` has fields: `term`, `tier`, `severity` (`"error"` or `"warn"`), `line`, `message`, `suggestion`.
- Library is pure: no side effects, no I/O beyond reading the policy file at config load.
- Used by all three enforcement surfaces (3b, 3c, bridge-compliance-gate extension).

**Component 3b — PreToolUse hook `term-disambiguation-precheck.py`** (new, deny-capable):

- Registered as PreToolUse hook for Edit and Write tools (matches existing `bridge-compliance-gate.py` registration pattern at `templates/managed-artifacts.toml:624-634`).
- Reads `tool_input.content` before the write (existing PreToolUse pattern).
- Calls `term_disambiguation.evaluate_content(content, file_path=tool_input.file_path, policy=...)`.
- Filters violations: only `severity="error"` violations cause deny.
- For non-bridge writes, only `forbidden_uses_severity="error"` violations deny (per pinned default §D); Tier B violations are warn-level (deferred to PostToolUse audit per 3c).
- For bridge proposals (file_path matches `bridge/*.md`), Tier B violations also deny (per pinned default §A `tier_b_severity_in_bridge_proposals="error"`).
- Honors override syntax `{!common: <term>}` and file-level `<!-- term-disambiguation: off -->`.
- Hook returns non-zero exit + structured error message to deny the write; matches existing bridge-compliance-gate behavior.

**Component 3c — PostToolUse hook `term-disambiguation-audit.py`** (new, audit-only):

- Registered as PostToolUse hook for Edit and Write tools.
- Calls same shared library `evaluate_content`.
- Records `severity="warn"` violations to an audit log (e.g., `.gtkb-state/term-disambiguation/audit.jsonl`).
- Does NOT block; non-blocking observability/audit only.
- Slice 5 release-gate runs `gt term-disambiguation audit` against this log to report drift volume.

**Component 3d — `bridge-compliance-gate.py` extension** (existing PreToolUse hook):

- Existing hook at `templates/hooks/bridge-compliance-gate.py` already runs PreToolUse on bridge writes.
- Extension: after the existing spec-linkage check, the hook calls `term_disambiguation.evaluate_content(...)` for the same content.
- Combines violations into the existing block-or-allow decision: any `severity="error"` violation (from spec-linkage OR term-disambiguation) blocks the write.
- The extension reuses the shared library (no parallel logic path); the hook becomes a thin caller of the same evaluation function.

### Pinned defaults (unchanged from REVISED-1; enforcement event clarified)

The 7 pinned defaults in `[defaults]` are unchanged. REVISED-2 clarifies enforcement events:

- §A → Tier B: `error` in bridge proposals (PreToolUse deny via 3b/3d); `warn` elsewhere (PostToolUse audit via 3c).
- §B → Override: `{!common: <term>}` (recognized by shared library).
- §C → Tier C strictness: strict (PreToolUse for bridge; PostToolUse audit elsewhere).
- §D → Forbidden-use: `error` always (PreToolUse deny via 3b — universal across file types).
- §E → Backfill: audit-only (Slice 6).
- §F → Sentence-initial capitalization: ignore (shared library heuristic).
- §G → File-level disable: `<!-- term-disambiguation: off -->` (shared library honors).

## Test Plan (REVISED-2)

| # | Test | Spec link | Asserts |
|---|---|---|---|
| T1 | `test_canonical_terminology_policy_toml_exists_and_validates` | rule items 9 + 12 | Policy file at `templates/rules/canonical-terminology-policy.toml`; registered as `rule.canonical-terminology-policy`; `[defaults]` has all 7 pinned values; per-term entries cover 22-term minimum |
| T2 (REVISED-2) | `test_pretooluse_hook_registered_and_postusetooluse_audit_registered` | rule item 13 + Codex F1 | `term-disambiguation-precheck.py` registered as PreToolUse for Edit/Write; `term-disambiguation-audit.py` registered as PostToolUse for Edit/Write; both registered via managed-artifacts.toml |
| T3 | `test_tier_A_distinctive_form_flagged` | §"Tier A" | Edit producing `Membase` (wrong cap) flagged; `MemBase` passes |
| T4 (REVISED-2) | `test_tier_B_pretooluse_blocks_in_bridge_writes` | Codex F1 + pinned default §A | Edit producing "the backlog has 27 items" inside `bridge/*.md` triggers PreToolUse deny (write blocked); same content in non-bridge file passes PreToolUse but PostToolUse audit records warn |
| T5 | `test_tier_B_lowercase_general_context_passes_pretooluse` | §"Tier B" | "we have a backlog of customer requests" in non-canonical context passes both PreToolUse and PostToolUse |
| T6 | `test_tier_C_bare_canonical_with_demonstrative_flagged` | §"Tier C" + pinned default §C | "the spec we just landed" (no ID) flagged at warn; "the SPEC-1234 spec" passes |
| T7 | `test_override_syntax_suppresses_lint` | §"Override syntax" + pinned default §B | `{!common: backlog}` suppresses Tier B/C even in bridge writes |
| T8 (REVISED-2) | `test_bridge_compliance_gate_extended_calls_shared_library` | rule item 13 + Component 3d | Bridge proposal with `forbidden_uses_severity="error"` violation gets blocked at PreToolUse (via either bridge-compliance-gate.py extension OR term-disambiguation-precheck.py); shared library called once, not twice (perf check) |
| T9 (REVISED-2) | `test_forbidden_uses_blocked_at_pretooluse_universally` | rule item 1 + pinned default §D + Codex F1 | Edit producing forbidden-use phrase (e.g., "backlog as ignore list") blocked at PreToolUse regardless of file type (bridge or non-bridge); the deny path is verified before content lands |
| T10 | `test_lint_runs_in_smart_poller_spawned_sessions` | rule item 14 | Headless dispatch session has both PreToolUse and PostToolUse hooks active |
| T11 | `test_existing_canonical_terminology_thread_preserved` | rule item 11 | Existing `_check_canonical_terminology` doctor check unaffected |
| T12 (REVISED-2) | `test_existing_artifacts_not_retroactively_blocked` | §"Out of Scope" backfill | Pre-existing artifacts grandfathered; only NEW writes evaluated; PreToolUse hook does not retroactively scan existing files |
| T13 | `test_release_candidate_gate_runs_audit_report` | rule item 7 | Release-gate runs `gt term-disambiguation audit` against audit log |
| T14 | `test_DELIB_S327_term_disambiguation_directive_archived` | rule item 4 | After Slice 1, `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived |
| T15 | `test_sentence_initial_capitalization_ignored` | pinned default §F | Sentence-initial "Backlog items must be reviewed." in non-canonical context does not flag |
| T16 | `test_file_level_disable_marker_works` | pinned default §G | File starting with `<!-- term-disambiguation: off -->` exempt from both PreToolUse and PostToolUse |
| T17 (REVISED-2) | `test_self_contained_term_set_independent_of_primer_state` | Codex F3 of `-002.md` + Change 2 | Lint operates correctly when primer is REVISED (not yet GO); term set declared in policy file, not derived from primer |

## Acceptance Criteria

- New policy file `templates/rules/canonical-terminology-policy.toml` created with 22-term minimum + pinned `[defaults]`.
- Registry row `rule.canonical-terminology-policy` added to `managed-artifacts.toml`.
- Shared library `groundtruth_kb/term_disambiguation.py` implemented with `evaluate_content` API.
- PreToolUse hook `term-disambiguation-precheck.py` registered + denies on `error` severity.
- PostToolUse hook `term-disambiguation-audit.py` registered + records `warn` severity.
- `bridge-compliance-gate.py` extended to call shared library after spec-linkage check.
- All 7 pinned defaults present and tested at the correct enforcement event (PreToolUse for `error`; PostToolUse for `warn`).
- Override syntax + file-level disable working.
- Smart-poller dispatch sessions inherit both hooks (T10).
- Existing canonical-terminology thread evidence intact (T11).
- T1-T17 pass.
- IPR + CVR per `GOV-20`.
- Slice 1 policy file change carries approval packet per `GOV-ARTIFACT-APPROVAL-001`.
- `DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE` archived (T14).
- Ruff + lint clean.

## Risk and Rollback

- **Risk: PreToolUse hook latency adds to every Edit/Write.** Mitigation: shared library uses fast regex + cached policy load; existing `bridge-compliance-gate.py` already in this slot — incremental cost.
- **Risk: lint produces too much noise at PostToolUse.** Mitigation: severity-tunable per term; default warn elsewhere; backfill audit reports drift volume.
- **Risk: false positives in non-canonical contexts.** Mitigation: hook discriminates by file path. Tier B PreToolUse deny only on bridge writes; elsewhere is warn-only audit.
- **Risk: override syntax becomes graffiti.** Mitigation: usage tracked in audit log; doctor check reports density.
- **Risk: smart-poller doesn't inherit hooks.** Mitigation: T10 fixture-based assertion; matches existing `bridge-compliance-gate.py` inheritance pattern.
- **Risk: bridge-compliance-gate extension introduces regression in spec-linkage check.** Mitigation: existing tests for spec-linkage gate run unmodified; extension is purely additive (call shared library after existing check).
- **Rollback:** revert hook registrations + policy file + registry row + bridge-compliance-gate change. Existing canonical-terminology surface unchanged.

## Sequencing

1. **Slice 1 — Policy file + shared library.** New `canonical-terminology-policy.toml` + `term_disambiguation.py` shared library. Pre-implementation only; needs `GOV-ARTIFACT-APPROVAL-001` packet. T1.
2. **Slice 2 — PreToolUse hook (deny-capable).** `term-disambiguation-precheck.py` registered. T2-T7 + T9 + T15-T16.
3. **Slice 3 — PostToolUse audit hook.** `term-disambiguation-audit.py` registered; audit log written. T2 (PostToolUse leg).
4. **Slice 4 — bridge-compliance-gate extension.** Tier B escalation in bridge proposals via shared library. T8.
5. **Slice 5 — Smart-poller dispatch integration.** Hooks in dispatch sessions. T10.
6. **Slice 6 — Backfill audit + release-gate.** `gt term-disambiguation audit` reports drift; release-gate runs the audit. T12 + T13.
7. **Slice 7 — Doctor check + audit reporting.** Doctor verifies policy completeness. T14 + T17.

## Open Decisions (REVISED-1 trim retained)

§A through §G are PINNED in `[defaults]`. Enforcement event clarified per Codex F1.

§H. **Smart-poller dispatch composition with primer.** Token-budget-driven default. Suggest full inclusion at <2KB total; content-hash references beyond.

§I. **`gt term-disambiguation` CLI command surface.** `audit` + `validate` only.

## Out of Scope

- Implementation of Slices 1-7.
- Backfill rewrites (audit-only per pinned default §E).
- Cross-language disambiguation.
- Voice/audio surfaces.
- The term primer itself.
- Modifying existing `canonical-terminology.toml` schema.

## Spec-to-test mapping (summary)

- operating-model.md §2 → T9 (forbidden-uses)
- file-bridge-protocol.md → T8
- project-root-boundary.md → T1
- deliberation-protocol.md → T14, Prior Deliberations satisfies search obligation
- GOV-ARTIFACT-APPROVAL-001 → T14
- GOV-19-A1 → T2, T8
- GOV-20 → IPR/CVR
- DELIB-S312 → T13
- canonical-terminology.toml → T11
- canonical-terminology.md → T1
- gtkb-canonical-terminology-surface-implementation-012 → T11
- managed-artifacts.toml → T1
- **`templates/hooks/bridge-compliance-gate.py` → T2, T8, T9 (Codex F1 evidence: existing PreToolUse pattern reused)**
- gtkb-bridge-poller-001-smart-poller-007 → T10
- primer sibling proposal → T17
- backlog sibling proposal → T4, T6
- Owner directive (verbatim) → T1, T3-T7, T15-T16

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
