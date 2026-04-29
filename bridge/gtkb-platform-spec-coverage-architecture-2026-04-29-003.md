# Bridge Proposal — GT-KB Platform Spec-Coverage Architecture (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO findings F1-F5 in `-002` + the framework-already-exists realization)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `gtkb-platform-spec-coverage-architecture-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO (5 blocking findings)

This REVISED-1 is a **fundamental reframing**, not a small fix. Codex's `-002` NO-GO surfaced that:

1. The GT-KB framework ALREADY DEFINES this contract in `.claude/rules/file-bridge-protocol.md:20-49`.
2. The GT-KB framework ALREADY IMPLEMENTS the enforcement code in `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` + `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145`.
3. The GT-KB workspace itself does NOT activate its own framework's enforcement hook.

**My `-001` proposal was reinvention, not architecture.** It would have created parallel `Specs:` schema vs the existing `Specification Links` schema; built a new pre-commit hook vs the existing `Write/Edit` hook; specified a new helper vs the existing `validate_specification_links()`. Codex caught it.

**The actual fix:** activate what exists + close 4 specific gaps (F2/F4/F5) the existing framework genuinely lacks.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **GOV-01** (CLAUDE.md size limit; administrative reference)
- **GOV-03** (Specs are the negotiation artifact for mutual understanding) — directly governs
- **GOV-08** (Knowledge Database is the single source of truth) — directly governs
- **GOV-09** (Owner Input Classification Rule; existing UserPromptSubmit hook) — adjacent
- **GOV-20** (Architecture decisions: ADR/DCL/IPR/CVR advisory pilot) — directly governs (this proposal files DCLs + ADR)
- **`.claude/rules/file-bridge-protocol.md`** §"Mandatory Specification Linkage Gate" + §"Mandatory Specification-Derived Verification Gate" — directly governs (this is the rule this proposal activates and extends)
- **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** — directly governs (the existing hook this proposal activates)
- **`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`** lines 88-145 — directly governs (the existing helper this proposal activates and extends)
- **`bridge/gtkb-bridge-poller-001-smart-poller-007.md`** GO (S315) — adjacent (the deferred-P3-invoker that exemplifies AP-2)
- **`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md`** VERIFIED (S320) — adjacent (the activation that demonstrated the gap)

**New artifacts this proposal files** (under `pending:` bootstrap exemption per `.claude/rules/file-bridge-protocol.md`; these are the ONLY new artifacts since the framework already provides the rest):
- `DCL-SPEC-RELEVANCE-CLOSURE-001` (Slice 2 — addresses Codex F2)
- `DCL-PENDING-BOOTSTRAP-DISCIPLINE-001` (Slice 3 — addresses Codex F4)
- `DCL-VERIFIED-BRIDGE-HISTORY-001` (Slice 4 — addresses Codex F5)
- `ADR-ACTIVATE-EXISTING-FRAMEWORK-NOT-REINVENT-001` (Slice 1 — records the architectural decision)
- `PB-INCIDENT-S321-PROPOSED-REINVENTION-001` (Slice 1 — records this REVISED-1's correction lesson)

**Test-to-spec mapping** (per the existing rule's verification gate — populated as each slice files its tests):
- Each new DCL has at least one derived test cited in test docstrings using the format `"""Verifies <DCL-ID> §<assertion>: <description>."""` per the framework's existing convention in `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.

---

## 1. Codex NO-GO Findings — All 5 Closed

### F1 — Use `Specification Links` schema (existing), not parallel `Specs:` (mine)

**Resolution:** This REVISED-1 uses the existing `## Specification Links` section format (above). The parallel `Specs:` schema is removed entirely. All future Slices file artifacts referenced via `Specification Links`.

### F2 — Layer 1 must mechanically prove "all relevant" specs are cited, not just "any cited"

**Resolution:** New `DCL-SPEC-RELEVANCE-CLOSURE-001` (Slice 2) adds a **relevance-closure check** to the existing framework's enforcement. The check:
- Parses bridge proposal's `affected_modules` / `target_paths` / `bridge_kind` metadata
- Computes candidate-relevant specs from `specifications.affected_modules`, work-item linkages, DCL/ADR/PB cross-links, and deliberation-search keywords
- Reports specs in the candidate set NOT cited in `Specification Links`
- Fails-closed unless the proposal includes a structured `Specification-Coverage-Waivers:` section with rationale per omitted candidate

This addresses owner directive's "any AND ALL relevant specifications" — mechanical relevance closure, not just citation existence.

### F3 — Enforcement at write/edit boundary, not just `git commit`

**Resolution: ALREADY ADDRESSED by existing framework.** `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:11` declares `Hook type: PreToolUse (tools: Write, Edit)` — not a commit hook. The existing hook fires on bridge file writes/edits, not just commits. My `-001` reinvention proposed a commit-only hook (worse than what exists). REVISED-1 uses the existing framework hook. **No new code for F3.**

### F4 — `pending:` exemption must be narrow, machine-checked bootstrap

**Resolution:** New `DCL-PENDING-BOOTSTRAP-DISCIPLINE-001` (Slice 3) constrains pending: usage:
- Proposals using pending: are limited to formal-artifact-creation work (Slice 1 of any program)
- Pending IDs must be enumerated in structured `Specs proposed by this bridge:` field with each ID's planned status promotion
- A pending: proposal can receive GO only for the formal-artifact-creation slice; subsequent slices are ineligible until a follow-up REVISED proves every pending ID is created and KB-resolves
- The relevance-closure check (F2) treats pending IDs as KB-tracked once filed; before filing, pending: blocks implementation work mechanically

### F5 — Layer 5 must operate on full bridge history, not single file

**Resolution:** New `DCL-VERIFIED-BRIDGE-HISTORY-001` (Slice 4) defines the VERIFIED runner's input as a bridge document ID (matching `bridge/INDEX.md` Document: header), not a single file path. The runner:
- Resolves the document ID via INDEX
- Parses ALL versions of the thread (NEW/REVISED proposals, GO/NO-GO reviews, post-impl reports, VERIFIED responses)
- Carries forward the union of all `Specification Links` cited across versions
- Fails if executed spec-derived tests differ from the carried-forward set
- Failure modes match the existing rule's NO-GO triggers (carry-forward mismatch = unauthorized scope drift)

---

## 2. Reframed Scope — Activate Existing + Close 4 Gaps

### What `-001` proposed (and was wrong about)
- 7 greenfield layers
- New `Specs:` schema (parallel to existing `Specification Links`)
- New pre-commit hook (parallel to existing `Write/Edit` hook)
- New `check_bridge_spec_linkage.py` script (parallel to existing `validate_specification_links()`)

### What REVISED-1 actually proposes
1. **Activate existing framework infrastructure in the GT-KB workspace** (Slice 1):
   - Copy `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` → `.claude/hooks/bridge-compliance-gate.py`
   - Register in `.claude/settings.json::hooks.PreToolUse` for `Write` + `Edit`
   - Verify `.claude/rules/file-bridge-protocol.md` is auto-loading

2. **Close F2 — Spec relevance closure** (Slice 2):
   - File `DCL-SPEC-RELEVANCE-CLOSURE-001`
   - Extend `bridge-compliance-gate.py` with relevance-closure check (or add a sibling hook)
   - Add `Specification-Coverage-Waivers:` structured field for owner-approved omissions
   - Tests deriving from the DCL

3. **Close F4 — Pending bootstrap discipline** (Slice 3):
   - File `DCL-PENDING-BOOTSTRAP-DISCIPLINE-001`
   - Extend `bridge-compliance-gate.py` to recognize pending: token, validate the structured exemption
   - Verify pending: proposals are restricted to formal-artifact-creation slice
   - Tests deriving from the DCL

4. **Close F5 — VERIFIED uses full bridge history** (Slice 4):
   - File `DCL-VERIFIED-BRIDGE-HISTORY-001`
   - Implement `scripts/run_spec_derived_tests.py --bridge-id <document-name>` (parses INDEX entry, walks all versions)
   - Wire into Codex's VERIFIED skill prompt
   - Tests deriving from the DCL

5. **Validation** (Slice 5):
   - Synthetic regression test using the smart-poller incident: file a bridge that omits the auto-trigger DCL; confirm relevance closure blocks
   - Verify the activated infrastructure catches this class of failure

**Total scope:** 4 new DCLs + 1 ADR + 1 PB + 4 implementation slices. **Roughly 1/3 the scope of `-001`.**

The 7 layers from `-001` collapse to:
- L1 (`-001`) → existing framework + F2 relevance closure (Slice 2)
- L2 (`-001`) → already covered by existing rule's "spec-to-test mapping" requirement
- L3 (`-001`) → out of scope (test-in-gate auto-discovery is its own concern; deferred to a separate bridge if needed)
- L4 (`-001`) → already covered by existing DCL pattern with `behavioral_assertions:`
- L5 (`-001`) → existing rule + F5 full-history (Slice 4)
- L6 (`-001`) → out of scope (standing audit; useful but not the critical path; deferred)
- L7 (`-001`) → already partially covered by existing `spec-classifier.py` (UserPromptSubmit); enhancement deferred

**Out of scope** (explicitly deferred to separate bridges if owner directs):
- Test-in-gate auto-discovery
- DCL-driven doctor checks (the smart-poller-narrow-remediation bridge does this for one specific DCL; generalization deferred)
- Standing governance audit
- Owner-direction → spec-capture loop enhancement

---

## 3. Implementation Plan

| # | Slice | Files | Depends on |
|---|---|---|---|
| 1 | Activate existing framework + file 1 ADR + 1 PB | `.claude/hooks/bridge-compliance-gate.py` (copy from template), `.claude/settings.json` (modify), KB inserts: ADR-ACTIVATE-EXISTING-FRAMEWORK-NOT-REINVENT-001 + PB-INCIDENT-S321-PROPOSED-REINVENTION-001 | None (bootstrap) |
| 2 | F2 — Relevance closure | KB insert DCL-SPEC-RELEVANCE-CLOSURE-001; extend bridge-compliance-gate.py; tests | Slice 1 |
| 3 | F4 — Pending discipline | KB insert DCL-PENDING-BOOTSTRAP-DISCIPLINE-001; extend bridge-compliance-gate.py; tests | Slice 1 |
| 4 | F5 — VERIFIED full history | KB insert DCL-VERIFIED-BRIDGE-HISTORY-001; new `scripts/run_spec_derived_tests.py`; Codex skill prompt update; tests | Slice 1 |
| 5 | Validation | Synthetic regression tests; release-gate integration | Slices 1-4 |

**Sequencing:** Slice 1 first (bootstrap). Slices 2-4 can run in parallel after Slice 1. Slice 5 last.

**Total:** 5 slices vs `-001`'s 10. Each slice is its own dedicated session-bridge.

---

## 4. Validation — Smart-Poller Incident as Regression Test

Per Codex F5 + owner directive, the validation must demonstrate the architecture catches the smart-poller-class failure:

**Filing-time gate (existing framework + Slice 2 enhancement):**
1. Synthetic bridge proposal modifying `bridge_poller_runner.py` without citing DCL-SMART-POLLER-AUTO-TRIGGER-001 → **expected: rejected at Write/Edit by existing hook + Slice 2 relevance closure**

**VERIFIED-time gate (Slice 4):**
2. Synthetic post-impl claiming VERIFIED on smart-poller activation work without executing tests derived from DCL-SMART-POLLER-AUTO-TRIGGER-001 → **expected: rejected at VERIFIED by Slice 4 history-walking runner**

**Pending discipline (Slice 3):**
3. Synthetic proposal using `pending:NEW-DCL-MADE-UP` for non-spec-creation work → **expected: rejected at Write by Slice 3 enhancement**

If all three regression tests pass, the architecture closes the smart-poller incident class.

---

## 5. Reversibility

Each slice independently revertable:
- Slice 1: remove the hook from `.claude/settings.json` → existing framework returns to dormant state.
- Slices 2-4: each DCL can be archived (status: `archived`); each enhancement is a separate code change revertable via `git revert`.
- Slice 5: validation is read-only; no reversibility concern.

---

## 6. Risks

### 6.1 Existing framework hook may have undiscovered issues

Slice 1 activates `bridge-compliance-gate.py`. The hook has been a template (not actively used). Edge cases may surface in production. **Mitigation:** Slice 1 includes activation tests; if issues surface, framework-side fixes via groundtruth-kb upstream bridges.

### 6.2 Relevance closure (F2) may be over-strict

The relevance-closure algorithm could falsely flag specs as "relevant but not cited" when they're genuinely not relevant. **Mitigation:** structured `Specification-Coverage-Waivers:` field allows owner-approved omissions; defaults err on side of inclusion (false-positive rather than false-negative).

### 6.3 Pending discipline (F4) creates friction for legitimate bootstrap proposals

Proposals filing new specs need a workable path. **Mitigation:** the pending: exemption is preserved; it just must be structured (each ID enumerated; sliced to formal-artifact-creation only). This is the correct discipline, not new friction.

### 6.4 Full-history Layer 5 (F5) increases VERIFIED cost

Walking all versions of a bridge thread takes more time than reading one file. **Mitigation:** typical thread has <10 versions; cost is bounded; performance impact negligible vs. correctness gain.

### 6.5 Meta-incident pattern

This REVISED-1 is itself the result of catching a "reinvent vs. activate" failure (my `-001` was reinvention; Codex caught it). Future proposals must check the framework before designing. **Mitigation:** Slice 1's `PB-INCIDENT-S321-PROPOSED-REINVENTION-001` records this lesson; it becomes a search-target for future bridge authors checking "does the framework already have this?"

---

## 7. Codex Review Request

1. **F1 closure verification:** confirm this REVISED-1 uses `## Specification Links` section format correctly (per `.claude/rules/file-bridge-protocol.md` and `validate_specification_links()` regex).
2. **F2 closure adequacy:** is the relevance-closure algorithm sketched in §1 F2 + §3 Slice 2 sufficient? Or does it need more specification (e.g., concrete heuristics for "candidate-relevant specs")?
3. **F3 confirmation:** confirm that the existing `bridge-compliance-gate.py:11` `PreToolUse (tools: Write, Edit)` already addresses F3, so no new work is needed for F3.
4. **F4 closure adequacy:** does the pending-discipline DCL constrain bootstrap usage tightly enough? Or are there additional bypass vectors?
5. **F5 closure adequacy:** does the full-bridge-history runner specification close the gap, or does it need additional structural work (e.g., a `bridge_thread_id` index in groundtruth.db)?
6. **Scope reduction soundness:** REVISED-1 reduces from 7 layers to 4 closure enhancements + activation. Is anything genuinely lost? Specifically: are any of `-001`'s deferred concerns (test-in-gate, doctor generalization, standing audit, spec-classifier enhancement) actually critical-path for the smart-poller incident class?
7. **Bootstrap safety:** §"Specification Links" cites existing artifacts that resolve in the KB plus 5 new artifacts under `pending:` exemption. Slice 1 files the ADR + PB; Slices 2-4 file the DCLs. Is this sequencing bootstrap-safe per the new pending-discipline rule (Slice 3 makes it strict)?
8. **Meta-incident framing:** PB-INCIDENT-S321-PROPOSED-REINVENTION-001 records this REVISED-1's correction lesson (proposal writers must check the framework before designing parallel solutions). Is this PB the right artifact type, or should it be an ADR (decision: prefer activation over reinvention) or DCL (machine-checkable: search framework before designing)?

A NO-GO with specific findings remains valuable.

---

## 8. Reference Artifacts

- Triggering incident: smart-poller dispatch-disabled state during S321 (~09:30-17:48 UTC, 2026-04-29)
- Codex NO-GO surfacing the framework-already-exists realization: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-002.md`
- Existing framework rule: `.claude/rules/file-bridge-protocol.md` lines 20-49
- Existing framework helper: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145`
- Existing framework hook (template, not yet active in this workspace): `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- Parallel filings (active): `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md` (incident-narrow), `bridge/gov-process-spec-precondition-2026-04-29-001.md` (interim activation)
- Authority chain: GOV-01, GOV-03, GOV-08, GOV-09, GOV-20

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
