NEW
::init gtkb pb
::open build

# gtkb-wi5679-session-role-keying-continuity — Session-id continuity chain and strict transcript-only role inheritance

bridge_kind: prime_proposal
Document: gtkb-wi5679-session-role-keying-continuity
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c70e4b35-80ab-4ee7-b9d3-b3912ca18b61
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; owner-declared role prime-builder via the canonical init keyword

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5679

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/session_self_initialization.py", "scripts/session_role_resolution.py", "scripts/workstream_focus.py", ".claude/hooks/workstream-focus.py", ".claude/settings.json", "platform_tests/scripts/test_session_role_keying_continuity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

An owner-declared interactive Prime Builder role does not survive a session
restart at the worker-session-document layer, and cannot be repaired mid-session
by re-sending the canonical init keyword. This blocks every `go_implementation`
work-intent claim — and therefore every implementation-start packet — for the
affected session, even when the bridge thread carries a valid independent `GO`.

Investigation established that the operative root cause is a **session-id keying
divergence, not a persistence failure**. Hook subprocesses and tool subprocesses
resolve different session ids after a restart or resume. Worker-session documents
are written under the hook-payload session id; `scripts/bridge_claim_cli.py` and
`scripts/bridge_work_intent_registry.py` `_resolve_worker_role` resolve under the
ambient environment session id via `BRIDGE_WORK_INTENT_ORDER`. After a restart the
two diverge permanently and nothing reconciles them, so the claim path reads a
stale document carrying the durable registry fallback role.

Both reported symptoms follow from that single cause. The declared role *does*
survive the restart — into a document the claim path cannot see. The mid-session
init-keyword repair *does* fire and *does* write the correct role — into that same
unreachable document. Live evidence from the reproducing session: document
`2b72a308` carried `role: prime-builder` with the canonical init keyword and
`role_resolution_source: transcript_init_keyword`, while the claim path resolved
`c70e4b35`, which carried `loyal-opposition` with `session_resolver_fallback`.

This proposal implements the owner-approved fix: a **session-id continuity chain
with a liveness backstop** on the read path, and **strict transcript-only
inheritance** on the SessionStart write path. Per owner decision it also folds in
WI-5504, whose two defects live in the same init-keyword persistence path that
this fix depends on.

## Problem Detail

### P1 — Stale-but-present documents outrank the live projection

`groundtruth_kb/session/envelope.py` `resolve_worker_role_provenance` (approx.
L536-541) falls back to the shared per-harness projection **only when the
session-keyed document is absent**:

```python
path = worker_session_envelope_path(project_root, expected_harness_name, current_session_id)
if not path.is_file():
    path = current_envelope_path(project_root, expected_harness_name)
```

Absence was modelled as the only failure mode; staleness was not. A stale-but-
present document therefore silently outranks the live projection.

### P2 — No channel carries a transcript-declared role into a restarted session

`scripts/session_self_initialization.py` (approx. L7627-7673) resolves
`role_profile` via `discover_role_profile`, which at approx. L3454 reads **only**
the durable registry through `role_for_harness`. Per-session markers and the prior
envelope are never consulted. `role_profile_explicit` can only be set by
`--role-profile` (not the SessionStart path) or `GTKB_BRIDGE_DISPATCH_KEYWORD`
(headless dispatch only), so interactive restarts always write
`role_source="session_resolver_fallback"`.

### P3 — The WI-4663 inheritance path is dead on arrival

`scripts/session_role_resolution.py` `resolve_interactive_session_role` (approx.
L168-181) does implement envelope inheritance, but reads
`harness-state/<harness>/session-envelope.json` — the shared projection that
`write_current` (envelope.py approx. L589-602) overwrites for the new session id
*before* any consumer reads it. It can only ever observe the current session's own
registry-derived role.

### P4 — Fallback roles are laundered into transcript authority

The same path accepts `role_resolved` without checking
`worker_role_provenance.role_resolution_source`, then labels the result
`authority_mode: "interactive_transcript"`. Verified live: it returned
`interactive_resolved_role: loyal-opposition`, `interactive_role_source:
session_envelope`, `authority_mode: interactive_transcript` — a registry fallback
laundered into transcript authority. Once a fallback role lands in the projection
it self-perpetuates across restarts.

### P5 (WI-5504) — The repair channel is silently breakable

`_CANONICAL_INIT_KEYWORD` (envelope.py L36) has no line anchors and is checked via
`.fullmatch()` against the entire prompt. This contradicts the first-line-only
grammar in `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and diverges from
`scripts/_session_init_keyword.py` `match_canonical_init_keyword`, which uses an
anchored pattern with `.match()`. Measured divergence:

| Prompt | `match_canonical_init_keyword` | `parse_canonical_init_keyword` |
|---|---|---|
| bare keyword | `pb` | `prime-builder` |
| keyword + trailing newline | `pb` | `None` |
| keyword + trailing space | `None` | `None` |

Because `_persist_interactive_session_envelope` gates on the stricter parser, a
trailing newline silently no-ops the envelope write while the marker write still
succeeds — producing exactly the marker-present / envelope-absent asymmetry seen
in the field. WI-5504 additionally records that the hook is invoked via bare
`pythonw` rather than the project venv interpreter, with a 5-second timeout, and
that both failure modes are silent.

### Operational severity

Eight worker-session documents were created for harness `claude` in roughly 85
minutes during the reproducing session, each resetting the role to the registry
fallback. A repaired role therefore has an observed half-life of about ten
minutes, which is shorter than the multi-step gated-write sequence the bridge
protocol requires. This is why P2/P3 matter beyond restart: every SessionStart is
a role-reset event.

## Proposed Implementation

### C1 — Session-id continuity chain (read path)

Add an optional `predecessor_session_id` field to the worker-session document
schema and a resolver step that follows the chain forward. When
`resolve_worker_role_provenance` is called with a session id whose document
records a successor, it resolves forward to the live document rather than
returning the stale one. The chain is explicit and auditable and never links
documents across harnesses.

### C2 — Liveness backstop (read path)

When no continuity link exists, the session-keyed document is older than the
harness's shared projection, and that projection is `status: open`, prefer the
projection and record the resolution source as a distinct, non-transcript value so
the fallback is visible in the audit trail rather than silently laundered.

### C3 — Strict transcript-only inheritance (write path)

At SessionStart, before `ensure_worker_session` writes, read the prior open
document for the harness. Inherit its role **only** when its
`worker_role_provenance.role_resolution_source` is `transcript_init_keyword`, and
carry it forward with that same provenance plus an explicit
`predecessor_session_id`. In every other case use the durable registry role with
`session_resolver_fallback`. This restores persistence and closes P4, because a
fallback-derived role can no longer be promoted into transcript authority.

### C4 — Parser convergence (WI-5504)

Make `parse_canonical_init_keyword` delegate to, or exactly mirror, the anchored
first-line grammar in `scripts/_session_init_keyword.py`, so the two parsers
cannot diverge again. Add a drift-lock test in the style of
`platform_tests/scripts/test_gtkb_session_id.py`.

### C5 — Hook invocation hardening (WI-5504)

Resolve the hook interpreter deterministically to the project venv rather than
bare `pythonw`, and surface an explicit warning when a canonical init keyword is
observed but no corresponding persistence write occurs, so the failure is never
silent.

## Cross-Harness Disposition

Required because `target_paths` includes the harness-surface files
`.claude/hooks/workstream-focus.py` and `.claude/settings.json`
(`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` assertion `PARITY-DISPOSITION-GATE`;
`ADR-CROSS-HARNESS-PARITY-001` Q8). Disposition: **behavioral parity, no waiver
requested.**

**C1–C4 — parity by shared implementation.** The core fixes land in
harness-neutral shared modules: `groundtruth-kb/src/groundtruth_kb/session/envelope.py`,
`scripts/session_self_initialization.py`, `scripts/session_role_resolution.py`,
and `scripts/workstream_focus.py`. Every registered harness resolves roles
through these same modules, so the continuity chain, liveness backstop,
transcript-only inheritance, and parser convergence apply identically to all
harnesses with no per-harness change. The defect itself is harness-general: it
arises wherever a harness's hook and tool subprocesses resolve different session
ids, which `SESSION_ID_ENV_VARS` already anticipates for Claude
(`CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`), Codex (`CODEX_SESSION_ID`,
`CODEX_THREAD_ID`), and Antigravity (`ANTIGRAVITY_SESSION_ID`).

**C5 — parity already exists on the Codex side; this change brings Claude up to
it.** `.codex/gtkb-hooks/workstream-focus.cmd` invokes the *same*
`.claude/hooks/workstream-focus.py` file with `GTKB_HARNESS_NAME=codex`, so any
change to that hook module propagates to Codex automatically with no `.codex/`
edit required. The interpreter half of C5 is Claude-only by construction:
`.codex/hooks.json` already invokes hooks through the explicit venv interpreter
(`groundtruth-kb\.venv\Scripts\pythonw.exe`), while `.claude/settings.json` uses
bare `pythonw`. C5 therefore *removes* an existing divergence rather than
creating one — after this change both harnesses resolve the same interpreter.

**Codex registration is already in place.** The Codex `user-prompt-submit` batch
in `.codex/gtkb-hooks/run_py_no_window.py` already lists
`.codex/gtkb-hooks/workstream-focus.cmd`, so no new Codex hook registration is
required by this proposal.

**Other harnesses.** Cursor, Antigravity, and Ollama consume the same shared
modules and inherit C1–C4 without change. No harness-specific waiver is sought.
If Loyal Opposition identifies a harness whose UserPromptSubmit or SessionStart
surface does not route through `.claude/hooks/workstream-focus.py` or the shared
session modules, that gap should be raised as a NO-GO finding so registration is
added in this proposal rather than deferred.

**Verification.** The regression module asserts harness-neutrality directly via
`test_continuity_chain_does_not_cross_harness`, and the parity claim above is
re-checkable by inspecting `.codex/gtkb-hooks/workstream-focus.cmd` and the
`BATCHES["user-prompt-submit"]` entry.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge audit trail this proposal is filed under and the append-only numbered-file discipline the implementation must preserve.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every governing specification; satisfied by this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the Project Authorization / Project / Work Item metadata triple present above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the spec-to-test mapping below and executed evidence before `VERIFIED`.
- `GOV-STANDING-BACKLOG-001` — governs WI-5679, WI-5504, WI-5681, and WI-5682 as MemBase work items and the backlog-conflict check performed against WI-5086 and WI-5504.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — the persistence constraints this defect violates; the primary governing constraint for C1, C2, and C3.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` — the decision that a transcript-defined interactive role persists across compaction, resume, and contiguous SessionStart-like boundaries; the authority C3 restores.
- `DCL-SESSION-ROLE-RESOLUTION-001` — the deterministic resolution table; C2 and C3 must keep resolution deterministic and must not introduce a new implicit precedence.
- `GOV-SESSION-ROLE-AUTHORITY-001` — the durable-versus-session-stated authority split; C3 must not mutate the durable registry, and C1/C2 must not let one session borrow another's authority except through an explicit recorded link.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` — the first-line-only canonical grammar that `parse_canonical_init_keyword` currently contradicts; the governing spec for C4.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the artifact-oriented stance under which this defect was captured as WI-5679 with a linked test, an owner-decision deliberation, and a bounded authorization rather than being repaired conversationally.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — requires traceability across artifacts, tests, reports, and decisions; satisfied by the WI/test/DELIB/PAUTH chain cited above and the spec-to-test mapping below.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — governs the lifecycle triggers exercised during preparation: defect capture (WI-5679), owner-decision capture (`DELIB-202667477`), and future-work capture without implementation approval (WI-5681, WI-5682, explicitly excluded from this authorization).

## Prior Deliberations

- `DELIB-202667477` — the owner-decision record for this work: continuity chain plus liveness backstop, strict transcript-only inheritance, full bridge-protocol routing, and WI-5504 scope folding. This proposal implements those decisions directly.
- `DELIB-20265225` — owner correction establishing that the transcript defines the session envelope and the designated role survives compaction. This proposal builds on it by making the surviving role reachable from the claim path, which is the gap that decision did not anticipate.
- `DELIB-20265224` — owner decision that the interactive role persists across contiguous sessions via the durable envelope. The present defect is that the mechanism it describes is defeated by session-id re-keying; this proposal does not revisit the decision, only its mechanism.
- `DELIB-20260710-WI5086-CONCURRENT-CODEX-SESSION-ENVELOPE-CLOBBER` — records the sibling manifestation on the concurrency axis: the single per-harness current envelope is peer-clobberable under concurrent same-harness sessions. This proposal deliberately addresses the restart and stale-id axis only; C2 is scoped so it does not weaken the isolation WI-5086 still needs.
- `DELIB-20265447` — the `GO` verdict for `gtkb-interactive-session-role-override-slice-11-envelope-durability`, which established the envelope-durability surface this proposal extends rather than replaces.
- `INTAKE-e71dd673` v2 — a prior default interactive session envelope role continuity intake, rejected as superseded. Noted so review can confirm this proposal is not re-litigating a closed capture; it addresses a defect in the shipped mechanism, not a new default-continuity policy.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing evidence is
`DELIB-202667477` (`source_type=owner_conversation`, `outcome=owner_decision`,
recorded from AskUserQuestion evidence `AUQ-2026-07-24-WI5679`):

1. **Resolution strategy** — continuity chain plus liveness backstop. Rejected: continuity chain only; liveness precedence only; close-stale-documents.
2. **Inheritance policy** — strict transcript-only inheritance. Rejected: inherit any prior role; no inheritance.
3. **Governance routing** — defect work item under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` through the full bridge protocol. Rejected: fast lane per `GOV-RELIABILITY-FAST-LANE-001`; split fast lane plus work item.
4. **Scope** — fold WI-5504 into this implementation scope. Rejected: WI-5679 only; also scoping in WI-5681 and WI-5682.
5. **Unblock path** — owner re-sends the canonical init keyword rather than authorizing an LO file-safety approval packet.

Two further owner decisions were taken during preparation and are recorded in the
session transcript pending archival as a follow-on deliberation: authorizing an LO
file-safety approval packet after the init-keyword window proved too short to
complete the governance chain, and — when that packet proved impossible to create
from inside a gated session — adding `.gtkb-state/propose-drafts/**` and
`.gtkb-state/owner-decisions/**` to `allow_patterns` in
`config/governance/lo-file-safety.toml`. Loyal Opposition should treat that
allow-list edit as an owner-made governance-config change outside the bridge
protocol and confirm whether it requires its own retrospective bridge record.

Standing owner directive accompanying these decisions: the defect must not be
worked around by hand-editing the session envelope or forcing session-id
environment variables. A third possible bypass — routing writes through the
PowerShell tool, whose exclusion from the LO file-safety gate matcher is recorded
in WI-5477 and WI-5481 — was also not used.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements are
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`,
`ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`,
`DCL-SESSION-ROLE-RESOLUTION-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and
`SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`. Each already states the behaviour the
implementation currently fails to deliver; this is a defect against shipped
requirements, not a requirements gap. No new or revised requirement is required
before implementation.

## Spec-Derived Verification Plan

New regression module `platform_tests/scripts/test_session_role_keying_continuity.py`.

| Linked specification | Derived test | Expected result |
|---|---|---|
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | `test_declared_role_survives_session_rekey` — write a document with `transcript_init_keyword` provenance, simulate a SessionStart re-key, resolve under the prior session id | Resolves `prime-builder`, not the registry fallback |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | `test_restart_inherits_transcript_role_with_predecessor_link` | New document carries the inherited role, `role_resolution_source=transcript_init_keyword`, and a `predecessor_session_id` |
| `DCL-SESSION-ROLE-RESOLUTION-001` | `test_fallback_role_is_not_inherited` and `test_fallback_is_not_labelled_interactive_transcript` | A `session_resolver_fallback` document is not inherited; resolution never reports `authority_mode=interactive_transcript` for a fallback-derived role |
| `GOV-SESSION-ROLE-AUTHORITY-001` | `test_continuity_chain_does_not_cross_harness` and `test_durable_registry_not_mutated` | The chain never links documents across harnesses; the durable registry is unchanged by any inheritance |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | `test_init_keyword_parsers_agree` — drift-lock over a shared case matrix | Both parsers agree on every case, including trailing newline, trailing space, CRLF, and leading whitespace |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The mapping in this table plus executed evidence in the implementation report | Every linked spec has executed test coverage |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` | Both mandatory preflights on this bridge id | `preflight_passed: true`, `missing_required_specs: []`, blocking gaps `0` |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_keying_continuity.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_session_id.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests -q --no-header -k "envelope or session_role"
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed .py>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed .py>
```

End-to-end acceptance: after implementation, a restarted interactive session whose
prior document carried `transcript_init_keyword` must obtain a `go_implementation`
claim without any envelope hand-edit, environment-variable override, or approval
packet.

## Pre-Filing Preflight Evidence

Both mandatory preflights were run against this body before filing, per
`.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection, using the `--content-file` surface (a `-001` thread has no prior
versioned file for `--bridge-id` to resolve):

- **Applicability preflight** — `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`.
  Packet hash: `sha256:9c7cebf0c2f0ebfd45886b45d5e328cdf37723a57e157bd67ed6984e2af728c7`
  (computed before this evidence section was appended).
- **Clause preflight** — `must_apply: 3`, `may_apply: 2`, `not_applicable: 0`;
  evidence gaps in `must_apply` clauses: `0`; **blocking gaps: 0**; exit `0`.
  The three satisfied blocking clauses are
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
  and the spec-to-test-mapping clause of
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

A phantom-spec sweep over all cited `SPEC`/`GOV`/`ADR`/`DCL`/`PB` ids confirmed
every id resolves in the live `specifications` table (11 ids at the time of the
sweep; none phantom). Loyal Opposition should re-run both preflights against the
filed `bridge/` file and cite its own packet hash in the verdict.

## Implementation-Path Note For Review

This proposal's own drafting claim was recorded with
`acting_role: "loyal-opposition"` — the defect manifesting inside the claim
registry. A `draft` claim does not gate on role, so filing is unaffected, but the
subsequent `go_implementation` claim will be denied by the same stale-document
resolution this proposal fixes.

That is a genuine bootstrap deadlock: the gate that must be satisfied to implement
the fix is the gate the fix repairs.
`.claude/rules/governance-emergency-bootstrap-protocol.md` condition (a)(1)
explicitly names "the work-intent claim system cannot operate" as a sanctioned
condition, and (a)(2) requires the normal path to be blocked by the very defect
being repaired. Both hold here. Loyal Opposition is asked to state in its verdict
whether it concurs that the emergency-bootstrap protocol is the correct
implementation path, and if so to confirm the after-action obligations: a
`WITHDRAWN` audit entry recording the commit SHA, deadlock rationale, and scope,
plus counterpart verification evidence. Owner approval is already on record at
`DELIB-202667477`, so clause (c) retroactive capture is satisfied prospectively.

If Loyal Opposition does not concur, the alternative is an owner-authorized LO
file-safety approval packet plus a fresh owner decision permitting the
implementation claim.

## Risk / Rollback

**Risk surface.** The change touches session-role authority and isolation
semantics, so the principal risk is over-broad resolution — one session resolving
against another session's authority. C1 mitigates by making links explicit,
recorded, and same-harness-only. C2 is the residual risk: a liveness backstop
inherently prefers a document the current session did not write. It is bounded to
`status: open` projections for the same harness and records a distinct resolution
source, so any such resolution is visible in the audit trail rather than silent.
C2 does not close WI-5086 (concurrent same-harness clobber) and must not be read
as doing so.

Secondary risk: C4 tightens a parser. A prompt shape that previously matched the
looser `fullmatch` and no longer matches the anchored grammar would stop
persisting a role. The drift-lock test enumerates the case matrix explicitly so
any such change is visible at review rather than in the field.

**Rollback.** Single-commit revert. No schema migration is required — the new
`predecessor_session_id` field is additive and optional, and documents written
without it resolve exactly as they do today. No MemBase mutation is in scope
(`kb_mutation_in_scope: false`), so revert is confined to source, tests, and hook
configuration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5679-session-role-keying-continuity`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — this repairs broken behaviour in shipped session-role resolution and adds
no new capability surface. The additive `predecessor_session_id` field and the new
regression module exist to support the repair, not to introduce a new feature.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
