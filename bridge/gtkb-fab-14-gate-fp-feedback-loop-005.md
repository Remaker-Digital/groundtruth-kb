REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-14-gate-fp-feedback-loop
Version: 005
Author: prime-builder (Claude Opus 4.8, harness B) — owner-present autonomous FABLE drive (/loop)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-14-gate-fp-feedback-loop-004.md (GO)

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4426
Project Authorization: PAUTH-FAB14-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: owner-present autonomous FABLE drive (/loop), ::init gtkb pb

---

# FAB-14 — Gate False-Positive Feedback Loop — REVISED (target_paths scope expansion)

This REVISED proposal supersedes the GO'd `-003`/`-004` ONLY to **expand `target_paths`**.
Implementation under the `-004` GO revealed that several of the four owner-decided areas require
lockstep edits to files the `-003` `target_paths` did not enumerate. The mechanical
implementation-start gate correctly refused to let Prime Builder exceed the authorized scope, so
those items are blocked pending this re-scope. No area's *intent* changes; only the authorized file
set grows. Owner decision to take the REVISE path: AskUserQuestion 2026-06-12 (this session) —
"REVISE fab-14 scope, then wait" (see Owner Decisions / Input).

## Revision Scope

`target_paths` adds four entries the original areas require:

1. **`.claude/settings.json`** — Area 2 (HYG-042) PowerShell coverage. The directive-enforcement hook
   is registered with matcher `"Write|Edit|MultiEdit|Bash|Delete|Move|Copy"` (no PowerShell), so
   adapter-code coverage alone never fires for PowerShell tool calls. The matcher must gain the
   PowerShell tool. `.claude/settings.json` is a protected-exact path absent from `-003` target_paths.
2. **`.codex/gtkb-hooks/**`** — Area 2 (HYG-042) Codex-side directive-enforcement coverage. The
   Codex PreToolUse surface fires on Bash/apply_patch and is wired through thin adapters under
   `.codex/gtkb-hooks/` (per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`); the `-003` set listed
   `.codex/hooks.json` (the registration) but not the adapter directory it must reference.
3. **`groundtruth-kb/templates/hooks/**`** — Area 4 (HYG-047) + Area 1 template parity. The tracked
   `.claude/hooks/*.py` gates are asserted byte-equivalent to their `groundtruth-kb/templates/hooks/`
   twins by `test_a_codex_template_parity_exists_and_matches`; any edit to a gate hook must move its
   template in lockstep or the parity test fails. (The narrative-gate template was already synced
   under `-004` because templates are not under the impl-start-gate's protected prefixes; this entry
   makes that lockstep obligation explicit and authorized for the remaining hook edits.)
4. **`.claude/hooks/scanner-safe-writer.py`** — Area 1 (HYG-040) denial telemetry. "Each blocking
   hook" includes the credential scanner-safe-writer, which denies but was not enumerated.

All other content (the four areas, owner constraints, verification plan) is unchanged from `-003`.

## Implementation Status (already done under the -004 GO; tested)

- **Area 2 — Bash parser (HYG-042 core):** `PATH_DELIMITER_RE` rewritten in
  `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py` with `_classify_path_token` (null-sink
  whitelist, URL skip, MSYS translation, rooted-driveless → project-relative). `config/governance/gate-fp-corpus.toml`
  + `platform_tests/scripts/test_gate_fp_corpus.py` (10 cases) green; the fix is live (Bash relative
  paths no longer false-blocked). **Remaining in Area 2:** PowerShell matcher + Codex adapter (this re-scope).
- **Area 3 — Requirement Sufficiency gate (HYG-046):** `SECTION_RE` widened to `^#{2,3}` (h2/h3);
  `REQUIREMENT_SUFFICIENCY_RE` / `REQUIREMENT_GAP_RE` bounded regexes replace the literal phrase list
  (with a `(?!\bnot\b)` guard); `requirement_sufficiency_state` splits `missing` vs `unrecognized`;
  caller emits distinct messages. `PATH_TOKEN_RE` de-duplicated into a single canonical source in
  `scripts/implementation_authorization.py` (imported by `bridge_applicability_preflight.py`; dead
  copy removed from `implementation_start_gate.py`). 99 + 158 existing tests + new tests green.
  (Discovered out-of-scope third copy in `scripts/adr_dcl_applicability_discovery.py` — tracked
  separately, not folded into FAB-14.)
- **Area 4 — narrative-gate packet auto-discovery (HYG-047):** `_autodiscover_packet` added to
  `.claude/hooks/narrative-artifact-approval-gate.py` (and its template twin) — a session-native
  Write to a protected narrative now succeeds from a matching on-disk packet (target_path + content
  sha256) without an env var. 18 tests green incl. template parity.

## Remaining Work (implement after this REVISE receives GO)

- Area 2: PowerShell matcher in `.claude/settings.json`; Codex directive adapter in
  `.codex/gtkb-hooks/` + registration in `.codex/hooks.json`; seed parser FP corpus with the 7
  commands (done) — extend with PowerShell/Codex cases.
- Area 4: formal-gate packet auto-discovery in `.claude/hooks/formal-artifact-approval-gate.py`
  (+ template); amend `DCL-ARTIFACT-APPROVAL-HOOK-001` via a formal-artifact-approval packet.
- Area 1: denial telemetry (gate, pattern-id, command-hash → `.gtkb-state/gate-denials.jsonl`) in
  each blocking hook (directive adapter, bridge-compliance, narrative, formal, impl-start,
  scanner-safe-writer) + templates; one-time GOV-15 reconciliation closing the ~20 fixed-but-open
  gate-FP WIs (owner-gated).

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — deterministic policy engine the gates implement (HYG-040).
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only classifiers (HYG-046, HYG-040).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — approval-packet hook contract amended by auto-discovery (HYG-047).
- `GOV-15` — owner-gated WI reconciliation (HYG-040).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — the Bash-parser fix adds Codex-harness + PowerShell coverage (HYG-042).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex adapter surface under `.codex/gtkb-hooks/` (Area 2 re-scope).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-14 changes are in-root.
- `GOV-STANDING-BACKLOG-001` — WI-4426 is the governed backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the WI reconciliation + DCL amend.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-040/042/046/047).
- `DELIB-FAB14-REMEDIATION-20260610` — the four owner dispositions (unchanged).
- `bridge/gtkb-fab-14-gate-fp-feedback-loop-003.md` / `-004.md` — the GO'd proposal this REVISE re-scopes.
- The `-004` implementation experience (this session) is the evidence that `target_paths` under-counted
  the lockstep file fan-out — the driver for this REVISE.

## Owner Decisions / Input

Collected via `AskUserQuestion` 2026-06-12 (this session): when implementation revealed fab-14's
`target_paths` was missing files its areas require (`.claude/settings.json`, `.codex/gtkb-hooks/`,
templates), the owner chose **"REVISE fab-14 scope, then wait"** — file this REVISED proposal
expanding `target_paths`, then pause fab-14 implementation until a fresh Codex GO, after which the
full expanded scope is implemented. The original four area dispositions remain
`DELIB-FAB14-REMEDIATION-20260610` (HYG-040 cheaper containment; HYG-042 Bash parser hotfix +
PowerShell/Codex coverage; HYG-046 three rigidities; HYG-047 auto-discovery in both gates).

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB14-REMEDIATION-20260610`
and unchanged. This REVISE is a pure `target_paths` scope correction so the already-decided work can
be implemented within authorized scope; it introduces no new requirement. The governing
specifications (`SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`,
`DCL-ARTIFACT-APPROVAL-HOOK-001`, `GOV-15`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`,
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`) already constrain every touched surface.

## target_paths

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*.json", "groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_applicability_preflight.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/narrative-artifact-approval-gate.py", ".claude/hooks/formal-artifact-approval-gate.py", ".claude/hooks/directive-enforcement-claude-adapter.py", ".claude/hooks/scanner-safe-writer.py", ".claude/settings.json", ".codex/hooks.json", ".codex/gtkb-hooks/**", "groundtruth-kb/templates/hooks/**", ".gtkb/directive-registry.json", ".gtkb-state/gate-denials.jsonl", "config/governance/gate-fp-corpus.toml", "platform_tests/scripts/**", "groundtruth-kb/tests/framework/**"]

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` (HYG-042) | the 7 everyday Bash commands PASS, genuine out-of-root DENIED (done, `test_gate_fp_corpus.py`); PowerShell tool calls now route through the directive check; the Codex adapter fires the directive |
| `SPEC-AUQ-POLICY-ENGINE-001` (HYG-046) | h2/h3 Requirement Sufficiency parsed; bounded sufficiency/gap accepted; absent vs unrecognized distinct (done, `test_fab14_requirement_sufficiency.py`); single PATH_TOKEN_RE source (done, `test_fab14_path_token_dedup.py`) |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (HYG-047) | a session-native Write/Bash with a matching on-disk packet PASSES without env var; mismatch BLOCKS — both gates (narrative done, `test_fab14_narrative_autodiscovery.py`; formal pending) |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` (HYG-040) | FP corpus required by LO gate-change review (done); each blocking gate appends a denial-telemetry record; GOV-15 reconciliation closes only WIs fixed-in-code |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/... groundtruth-kb/tests/framework/...` + `ruff check` AND `ruff format --check`; every touched `.claude/hooks/*.py` byte-parity with its template |

## Acceptance Criteria

Unchanged from `-003` (the four areas), plus: (5) every edited `.claude/hooks/*.py` stays byte-equivalent
to its `groundtruth-kb/templates/hooks/` twin; (6) PowerShell tool calls and the Codex harness both
route command execution through the directive root-boundary check.

## Recommended Commit Type

`fix:` — repairs four gate false-positive/evasion defects + the broken WI feedback loop, with
`feat:`-class additions (the FP regression corpus, denial telemetry, packet auto-discovery, and the
cross-harness/PowerShell directive coverage).
