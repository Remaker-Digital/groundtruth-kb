NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 0eb73a79-4ad6-40c0-88e9-16f797f0ef2e
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4883

Document: gtkb-cross-harness-parity-slice-4-disposition-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Recommended commit type: feat

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_compliance_gate_disposition.py"]

## Summary

Slice 4 of `PROJECT-GTKB-CROSS-HARNESS-PARITY` realizes the authoring-time
disposition gate (ADR Q8 / DCL assertion **PARITY-DISPOSITION-GATE**, currently
behavioral). It extends the bridge-compliance gate
(`.claude/hooks/bridge-compliance-gate.py`) so that a bridge proposal whose
`target_paths` touch a **harness-surface file** MUST include a non-empty
`## Cross-Harness Disposition` section; the Write is hard-blocked otherwise, and
Loyal Opposition issues NO-GO at review time as the second-line backstop.

The change is purely additive — a new heading regex, a harness-surface path
predicate, a concrete-section check, and one wiring call in the central deny
path — mirroring the gate's existing section gates (Owner Decisions / Input,
Requirement Sufficiency). Codex parity is automatic: the Codex
`bridge-compliance-gate.cmd` wrapper invokes the canonical Python hook through
`bridge-compliance-gate-bash-adapter.py`, so logic added to the Python hook
flows to Codex with no separate change. The active hook and its activation
template (`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`) are kept
byte-identical per the template-drift contract.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — the authoring-time disposition
  gate is the ADR's Q8 enforcement point: a harness-surface proposal must
  declare, per applicable harness, parity or a typed waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — directly satisfies
  assertion **PARITY-DISPOSITION-GATE** (Slice 4): the bridge-compliance gate
  requires a `## Cross-Harness Disposition` section for proposals whose
  target_paths touch a harness-surface file. This slice promotes that assertion
  from behavioral to mechanically enforced.
- `GOV-20` (architecture decision governance) — the ADR/DCL workflow this
  program follows.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; the
  bridge-compliance gate is a bridge-protocol enforcement surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Test Plan derives
  tests from the PARITY-DISPOSITION-GATE assertion.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the slice is delivered as
  durable artifacts (hook + template + test) and progresses the DCL assertion
  PARITY-DISPOSITION-GATE from behavioral to mechanically enforced through the
  bridge protocol.

The proposed tests derive from the linked spec: each test maps to a clause of
PARITY-DISPOSITION-GATE (trigger on harness-surface target_paths; pass when the
section is present; do not trigger off-surface; exclude verdict files).

## Requirement Sufficiency

Existing requirements sufficient. `ADR-CROSS-HARNESS-PARITY-001` (Q8) and
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (assertion PARITY-DISPOSITION-GATE)
already specify the disposition-section requirement and the LO NO-GO contract.
No new or revised requirement is introduced; this slice mechanizes the existing
constraint.

## Cross-Harness Disposition

This proposal's `target_paths` touch a harness-surface file
(`.claude/hooks/bridge-compliance-gate.py`), so the disposition is declared per
the ADR Q8 / DCL PARITY-DISPOSITION-GATE contract — and this very section is the
artifact the slice will enforce (self-referential).

- **Nature of change:** the bridge-compliance gate is a shared governance hook.
  The change adds one section-presence gate that applies identically to every
  harness because Codex consumes the same canonical Python hook via the
  bash-adapter. Applicability is **universal**.
- **Per-harness behavioral parity:** the new gate behaves identically on Claude
  (PreToolUse Write|Edit) and Codex (PreToolUse Bash/apply_patch via the
  adapter). No per-harness divergence is introduced; the active hook and its
  template are kept byte-identical.
- **In-root:** all artifacts (the hook, the template, the new test, this bridge
  file) are written in-root under the GT-KB project root; no out-of-root or
  temp-directory output is produced.
- **Waivers:** none required; no harness lacks the surface.

## Design

### A. Harness-surface predicate — `.claude/hooks/bridge-compliance-gate.py`

Add a module-level set of harness-surface path markers and a predicate:

- `HARNESS_SURFACE_PATH_MARKERS` (prefixes / exact paths): `.claude/settings.json`,
  `.codex/hooks.json`, `.claude/hooks/`, `.codex/gtkb-hooks/`, `.claude/skills/`,
  `.codex/skills/`. (Scoped to the demonstrated behavioral-surface set; the
  registry-driven expansion is a Slice-6 follow-on.)
- `_target_paths_touch_harness_surface(content) -> bool`: reuse the existing
  `_target_path_set_from_content(content)` parser; return True when any
  normalized target path equals or is prefixed by a harness-surface marker.

### B. Disposition-section check

- `CROSS_HARNESS_DISPOSITION_HEADING_RE`: matches `## Cross-Harness Disposition`
  (1–6 hashes, case-insensitive), mirroring `OWNER_DECISIONS_HEADING_RE`.
- `_has_concrete_cross_harness_disposition_section(content) -> bool`: heading
  present AND section body non-empty AND not placeholder-only (reuse
  `_collect_section_lines` + the existing placeholder-line regex), mirroring
  `_has_concrete_owner_decisions_section`.

### C. Wiring into the deny path

In the central `_deny_reason_for_content` path, for a versioned bridge file whose
first non-blank line is a `NEW`/`REVISED` status token (verdict files —
`GO`/`NO-GO`/`VERIFIED` first line — are excluded, consistent with the other
section gates): when `_target_paths_touch_harness_surface(content)` is True and
`_has_concrete_cross_harness_disposition_section(content)` is False, return a
deny reason citing PARITY-DISPOSITION-GATE with remediation guidance ("add a
`## Cross-Harness Disposition` section declaring, per applicable harness, parity
or a typed waiver"). A `_record_gate_denial` audit entry is emitted with a new
`pattern_id` (e.g. `cross-harness-disposition-missing`), consistent with the
gate's existing denial-audit pattern.

### D. Template sync + Codex parity

Copy the edited active hook to
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so the two remain
byte-identical (the template-drift doctor check enforces this). No Codex-side
file changes: `.codex/gtkb-hooks/bridge-compliance-gate.cmd` →
`bridge-compliance-gate-bash-adapter.py` already invokes the canonical hook.

### E. Tests — `platform_tests/scripts/test_bridge_compliance_gate_disposition.py` (new)

Import the hook module and exercise the predicate + deny path with synthetic
proposal content (the established hook-test idiom):

- a NEW proposal with harness-surface `target_paths` and NO disposition section
  → deny (the central deny reason mentions Cross-Harness Disposition);
- the same proposal WITH a concrete disposition section → no deny;
- a NEW proposal whose `target_paths` are off-surface (e.g. `scripts/foo.py`)
  and no disposition section → no deny (gate not triggered);
- a placeholder-only disposition section (`n/a`) on a harness-surface proposal
  → deny;
- a verdict file (`GO`/`VERIFIED` first line) touching a harness surface →
  no deny (verdict files excluded);
- the active hook and template are byte-identical (drift guard).

## Test Plan / Spec-Derived Verification

| Linked assertion clause | Derived test | Command |
|---|---|---|
| PARITY-DISPOSITION-GATE: trigger on harness-surface target_paths, require section | deny-without-section + pass-with-section + off-surface-no-trigger + placeholder-deny in `test_bridge_compliance_gate_disposition.py` | `python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q` |
| Verdict-file exclusion | verdict-first-line no-deny test | `python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q` |
| Template parity (byte-identical) | drift-guard test + (manual) `Get-FileHash` equality | `python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q` |
| Regression (no false-block of existing proposals) | existing bridge-compliance-gate test suite | `python -m pytest platform_tests/scripts/ -k bridge_compliance -q` |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: the gate blocks a harness-surface proposal lacking the disposition
section (advisory §6 criterion 3) and passes one that includes it; off-surface
proposals are unaffected; verdict files are excluded; the active hook and
template stay byte-identical; the existing bridge-compliance suite stays green.

## Owner Decisions / Input

Implementation authority flows from the existing owner authorization
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (active; owner decision
`DELIB-S20260626-PARITY-IMPL-AUTHORIZATION`), covering slice work items by active
project membership; **WI-4883** (this slice) is the active member that authorizes
this proposal. No new owner decision is required to implement Slice 4 (the change
creates no GOV/ADR/DCL/SPEC artifact and edits no protected narrative-authority
file — the bridge-compliance hook is platform code, not a `.claude/rules/*.md`
narrative artifact).

## Prior Deliberations

- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §5 build sequence step 4 is
  this slice (bridge-compliance-gate disposition section + LO NO-GO contract);
  §6 acceptance criterion 3 (a harness-surface proposal lacking the section is
  NO-GO'd) is realized by the deny path + tests here.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` — owner grill Q8
  resolving the disposition-section requirement and the LO NO-GO contract.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` — the owner authorization basis.
- `DELIB-20266265` — owner AUQ reactivating the program home and electing
  membership-based PAUTH coverage for the slice work items.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — Slice-3
  VERIFIED; the discovery-diff (the diagnostic counterpart) is now live at WARN,
  and this slice adds the authoring-time prevention gate.

## Risk / Rollback

- **Risk:** the gate could false-block a legitimate harness-surface proposal
  that genuinely needs no disposition (e.g. a pure formatting touch).
  *Mitigation:* the disposition section is cheap to add and the design's intent
  is that every harness-surface change reason about parity; the deny message
  gives exact remediation. The trigger is narrow (target_paths prefix match on
  the demonstrated surface set).
- **Risk:** template drift between the active hook and the activation template.
  *Mitigation:* the byte-identical copy + the drift-guard test + the existing
  template-drift doctor check.
- **Risk:** the new gate perturbs the central deny path ordering. *Mitigation:*
  the check is appended as an independent clause scoped to NEW/REVISED +
  harness-surface target_paths; the existing bridge-compliance suite is re-run
  as a regression gate.
- **Rollback:** revert the hook + template + test; no governance artifact or
  protected narrative file is touched, so rollback returns to the post-Slice-3
  state with no residue.
