NEW

# Implementation Proposal — Session-Context Review Independence Startup Rationale

bridge_kind: prime_proposal
Document: gtkb-session-context-review-independence-startup-rationale
Version: 001
Author: Prime Builder (Cursor harness E)
Date: 2026-06-24 UTC

author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: cursor-interactive-pb-s466-rationale-proposal
author_model: composer
author_model_version: 2.5
author_model_configuration: Cursor IDE interactive session; owner-requested bridge proposal; workspace E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4779

target_paths: ["config/agent-control/SESSION-STARTUP-INDEX.md", "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md", "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md", ".cursor/rules/gtkb-loyal-opposition.mdc", "scripts/session_self_initialization.py", ".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", ".claude/rules/codex-review-gate.md", "platform_tests/scripts/test_session_startup_review_independence_rationale.py", "bridge/gtkb-session-context-review-independence-startup-rationale-*.md"]

implementation_scope: governance_rule_surface_clarification, startup_disclosure, test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4597 (VERIFIED at `bridge/gtkb-session-context-self-review-rule-surfaces-004.md`) corrected durable rule surfaces to state that bridge review independence is **session-context based**. Agents still chronically misapply the rule because startup and harness-specific instructions:

1. Lead with **defensive negations** ("same harness ID is not a blocker") instead of the **normative prohibition and rationale**.
2. Conflate **review independence** with **harness ID**, **durable registry role**, or **bridge status-token authorship**.
3. Omit the **why**: a session context that authored/implemented work must not formally review that work because verification would inherit the same assumptions and errors.

This proposal implements **WI-4779**: add a **rationale-first canonical startup block** to the startup index and role overlays, emit it through `scripts/session_self_initialization.py` startup disclosure, align `.cursor/rules/gtkb-loyal-opposition.mdc` so Cursor agents stop inferring "durable LO = cannot propose/implement," and add focused tests. **No dispatcher or hook behavior changes** — mechanical enforcement remains in `cross_harness_bridge_trigger.py`.

## Problem Evidence

- Owner correction (2026-06-24): the actual prohibition is **no model session-context may formally review its own past authorship/implementation**; harness ID simplification is incorrect and causes chronic inefficiency.
- Prior agent misbehavior: conflated durable registry LO on harness E with inability to file `NEW` proposals during `::init gtkb pb` sessions.
- WI-4597 updated nine rule/root surfaces but **did not** add rationale-first language to generated startup disclosure (`session_self_initialization.py` grep: no review-independence strings).
- `config/agent-control/SESSION-STARTUP-INDEX.md` still uses defensive wording ("same harness ID alone is not a blocker") without stating cognitive contamination rationale.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge workflow authority; numbered file chain unchanged.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal metadata and inline JSON `target_paths`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing spec citations before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in implementation report.
- `GOV-STANDING-BACKLOG-001` — **WI-4779** / **TEST-11238** (created 2026-06-24; member of `PROJECT-GTKB-MAY29-HYGIENE`).
- `GOV-SESSION-SELF-INITIALIZATION-001` — startup disclosure is a first-class agent orientation surface.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable role vs interactive session role; must not conflate with review independence.
- `DCL-SESSION-ROLE-RESOLUTION-001` — interactive session role resolution for PB/LO posture.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` — `author_session_context_id` metadata contract (unchanged).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable wording over transient handoff notes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-2195` — owner decision: formal review requires unrelated session context from author; same harness allowed across different session contexts.
- `DELIB-2196` — interactive sessions bound to owner-declared role; distinct from headless dispatch routing.
- `bridge/gtkb-session-context-self-review-rule-surfaces-001.md` through `-004.md` (WI-4597, VERIFIED) — procedural clarification; this proposal adds **startup rationale** follow-on.
- Owner conversation 2026-06-24 — cognitive rationale for session-context prohibition; expunge harness-ID oversimplification from agent behavior.

## Owner Decisions / Input

- **Pre-implementation gate:** bounded PAUTH covering **WI-4779** (placeholder until owner approves scope expansion on May29 Hygiene snapshot PAUTH).
- **No new formal GOV/SPEC/ADR/DCL mutation** — wording and startup disclosure only.
- **Explicit non-goals:** no changes to `cross_harness_bridge_trigger.py` selection/refusal logic (already correct); no `lo-file-safety-gate.py` Cursor session-marker repair (recommend separate WI if still failing under `::init gtkb pb`).

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-2195`, WI-4597 VERIFIED behavior, and `GOV-SESSION-SELF-INITIALIZATION-001` supply acceptance criteria. This slice closes the **startup/orientation gap** that WI-4597 left open.

## Proposed Implementation

### Canonical block (single source of truth)

Add a shared markdown fragment (constant or small helper in `session_self_initialization.py`, referenced by startup index/overlays) titled **Session-Context Review Independence**:

```markdown
### Session-context review independence (normative)

Formal bridge review (GO / NO-GO / VERIFIED) must come from a **different model
session context** than the one that authored or implemented the artifact under
review. Shared session context means the verifier likely inherits the same
assumptions and errors as the author — same-session formal review is prohibited
and must fail closed.

- **Blocker:** reviewer session context equals artifact `author_session_context_id`
- **Fail closed:** missing or unreadable `author_session_context_id`
- **Not the boundary:** harness ID, vendor, or durable registry role (routing labels only)

Interactive `::init gtkb pb` grants Prime Builder authority in this session
regardless of durable registry role. It does **not** permit this same session
context to later issue GO/VERIFIED on work it authored or implemented here.
```

### Slice 1 — Startup index and overlays

- Insert canonical block into `config/agent-control/SESSION-STARTUP-INDEX.md` step 4 (file bridge / review independence).
- Add compact summaries to `LOYAL-OPPOSITION-STARTUP-OVERLAY.md` and `PRIME-BUILDER-STARTUP-OVERLAY.md` (link to full block; PB overlay includes the `::init gtkb pb` clarification line).
- **Reduce** repeated defensive "same harness ID is not a blocker" sentences in startup surfaces to one cross-reference: "See Session-Context Review Independence in SESSION-STARTUP-INDEX."

### Slice 2 — Generated startup disclosure

- Update `scripts/session_self_initialization.py` to include the canonical block (or equivalent rendered bullets) in role-appropriate startup disclosure output for both PB and LO.
- Preserve GOV-01 token budget: use compact bullets in generated report; full block remains in index file.

### Slice 3 — Cursor harness rule

- Update `.cursor/rules/gtkb-loyal-opposition.mdc`:
  - Separate **durable registry role** (dispatch routing) from **interactive session role** (`::init gtkb pb|lo`).
  - Include review-independence rationale (short form).
  - Explicitly retract the misinterpretation: durable LO on harness E does **not** prohibit PB `NEW` proposals when session role is Prime Builder.

### Slice 4 — Rule cross-links (minimal)

- Add one rationale sentence to `.claude/rules/file-bridge-protocol.md` § Review Independence Boundary pointing to startup index canonical block.
- Add matching one-line rationale cross-reference in `loyal-opposition.md` and `codex-review-gate.md` § Review Independence Gate (no duplicate negation paragraphs).

### Slice 5 — Tests

- Add `platform_tests/scripts/test_session_startup_review_independence_rationale.py`:
  - Assert SESSION-STARTUP-INDEX contains rationale keywords (`inherits`, `session context`, `author_session_context_id` or equivalent).
  - Assert generated startup disclosure helper includes review-independence section when invoked with fixture root.
  - Assert startup index does **not** lead with harness-ID negation as the primary explanation (heuristic: rationale section appears before "same harness ID" if latter retained once).
- Run existing dispatch regression unchanged: `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q -k "same_harness_author_different_session or self_review"`.

## Spec-Derived Verification Plan

| Spec / WI | Verification |
|-----------|--------------|
| `GOV-SESSION-SELF-INITIALIZATION-001` / WI-4779 / TEST-11238 | New pytest module passes; manual spot-check of generated `session-startup-report.md` includes review-independence rationale |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-session-context-review-independence-startup-rationale` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-session-context-review-independence-startup-rationale` |
| WI-4597 regression | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q -k "same_harness_author_different_session or self_review"` — no behavior change expected |
| Scope | `git diff --name-only` limited to `target_paths` |
| Lint | `ruff check` / `ruff format --check` on edited Python only |

## Acceptance Criteria

- [ ] Startup index and both role overlays state rationale-first session-context review independence.
- [ ] Generated startup disclosure includes the rationale (compact form acceptable).
- [ ] Cursor rule distinguishes durable registry role vs interactive session role and does not imply durable LO forbids PB proposals.
- [ ] Defensive "same harness ID is not a blocker" is demoted to single cross-reference, not primary startup teaching.
- [ ] No dispatcher/source logic changes.
- [ ] Focused tests pass; existing self-review regression tests pass.

## Risk / Rollback

| Risk | Mitigation |
|------|------------|
| Wording implies same-harness review always valid | Rationale states same-**session** prohibition only; keep DELIB-2195 citation |
| Startup token bloat | Compact bullets in generated report; full block in index |
| CLAUDE.md line budget | Do not edit CLAUDE.md in this slice unless net-neutral swap approved separately |

Rollback: revert wording/test commits; no runtime behavior to unwind.

## Bridge Filing

- Proposal: `bridge/gtkb-session-context-review-independence-startup-rationale-001.md` (this file)
- Implementation report: `-002` (REVISED post-GO)
- LO verdict: `-003` (GO/NO-GO)
- Verification: `-004` (VERIFIED/NO-GO)

## Recommended Commit Type

```
docs: session-context review independence startup rationale (WI-4779)
```
