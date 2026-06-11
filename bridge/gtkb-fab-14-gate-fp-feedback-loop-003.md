REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-14-gate-fp-feedback-loop
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-14-gate-fp-feedback-loop-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4426
Project Authorization: PAUTH-FAB14-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*.json", "groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "scripts/bridge_applicability_preflight.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/narrative-artifact-approval-gate.py", ".claude/hooks/formal-artifact-approval-gate.py", ".claude/hooks/directive-enforcement-claude-adapter.py", ".codex/hooks.json", ".gtkb/directive-registry.json", ".gtkb-state/gate-denials.jsonl", "config/governance/gate-fp-corpus.toml", "platform_tests/scripts/**", "groundtruth-kb/tests/framework/**"]

KB mutation: YES. Two MemBase writes: (1) the one-time WI reconciliation resolving the fixed-but-open gate-FP work items (append-only, under GOV-15), and (2) the DCL-ARTIFACT-APPROVAL-HOOK-001 amendment (formal-artifact-approval packet at implementation time). `groundtruth.db` is therefore included in `target_paths`. No canonical specification rows are hard-deleted.

---

# FAB-14 — Gate False-Positive Feedback Loop + ~20-WI Consolidation

WI-4426 (FAB-14) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-040 (the gate FP treadmill + the open-WI
cluster), HYG-042 (root-boundary Bash parser defect), HYG-046 (Requirement Sufficiency gate rigidities),
HYG-047 (narrative approval gate packet-discovery defect). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md`.

Common root cause: every gate ships its own bespoke regex classifier of free-form text (shell commands,
markdown, prose), with no shared FP regression corpus and no denial telemetry — so FP discoveries become
WIs that stay open after fixes land, new FP classes ship through VERIFIED, and sessions route around gates
(PowerShell-for-git, Bash-mediated writes), silently nullifying enforcement.

## Revision Scope

REVISED-003 responds to the three NO-GO findings in
`bridge/gtkb-fab-14-gate-fp-feedback-loop-002.md`:

- **F1 (mandatory applicability preflight fails — ADR-ISOLATION not cited):** added
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to `## Specification Links`. The proposal already carries an
  `## Isolation Placement Compliance` section and references `applications/`, which makes the ADR
  must_apply; citing it in Specification Links is what the applicability preflight harvests, so the
  mandatory gate now passes.
- **F2 (formal amendment packet artifacts missing from target_paths):** added
  `.groundtruth/formal-artifact-approvals/*.json` so the formal-artifact-approval packet for the
  `DCL-ARTIFACT-APPROVAL-HOOK-001` amendment falls inside the GO'd path-scope.
- **F3 (denial telemetry output path not in target_paths):** added `.gtkb-state/gate-denials.jsonl` to
  `target_paths` (the concrete runtime denial-telemetry sink the blocking hooks append to).

No other substantive change; the four gate-FP fixes, the owner constraints (gates stay blocking; shared
classifier library deferred; no external Agent Red mutation), and the verification plan are unchanged from
-001.

## Summary

- **HYG-040 (treadmill):** ~20 open WIs document gate FP classes with a bidirectional lossy loop — ≥3
  defects are fixed-but-WI-still-open; others accrete per-incident patches (e.g. a hardcoded incident
  phrase at implementation_authorization.py:61). No FP corpus gates new parser changes; no denial
  telemetry exposes FP rates.
- **HYG-042 (Bash parser):** PATH_DELIMITER_RE treats any 'word/word' token as an out-of-root absolute,
  denying essentially every Bash command with a relative path, URL, or /dev/null. It went VERIFIED with a
  test suite whose one FP case ('python -m pytest tests/') has a trailing slash that dodges the bug; this
  session's Bash 'wc -l bridge/INDEX.md' was denied (this whole session runs on PowerShell as a result).
  Absorbed: the directive matches only the Claude Bash tool, not PowerShell or the Codex harness.
- **HYG-046 (Req-Suff gate):** implementation_authorization.py matches only h2 headings (so
  '### Requirement Sufficiency' is silently invisible — the S421 blocker), grows a per-incident literal
  phrase allowlist, and returns the same 'missing' verdict for absent-section and unrecognized-phrasing.
- **HYG-047 (narrative gate):** the approval-packet discovery can only be satisfied by an env var the
  agent cannot set mid-session or a tool_input key the Write schema doesn't expose, so a compliant
  owner-approved Write to a protected narrative is mechanically impossible and sessions bypass via
  Bash-mediated writes the Write-matched hook never sees.

## Specification Links

- `SPEC-AUQ-POLICY-ENGINE-001` — the deterministic policy engine the gates implement; the FP corpus +
  denial telemetry strengthen its precision (HYG-040).
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — deterministic-only classifiers; the bounded-regex Req-Suff fix and
  the shared FP corpus keep the gates deterministic (HYG-046, HYG-040).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — the narrative/formal approval-packet hook contract amended by the
  auto-discovery branch (HYG-047).
- `GOV-15` (Test fix gate) — the one-time WI reconciliation closes fixed-but-open WIs under GOV-15 owner
  gating (HYG-040).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — the Bash-parser fix adds the Codex-harness + PowerShell coverage
  the directive currently lacks (HYG-042 absorbed).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-14 changes are in-root; the proposal touches no
  `applications/` subtree and writes no out-of-root artifact (see Isolation Placement Compliance below).
- `GOV-STANDING-BACKLOG-001` — WI-4426 is the governed backlog authority; absorbs the ~20-WI cluster.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the WI reconciliation + DCL amend.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-040/042/046/047).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB14-REMEDIATION-20260610` — this cluster's four owner dispositions (below).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the bespoke-classifier-per-gate pattern is the
  repetitive-plumbing defect this cluster contains.
- _The freshly-VERIFIED directive-enforcement thread (gtkb-directive-enforcement-p1-p2-combined, -008) is
  the thread the HYG-042 hotfix amends as a defect fix._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB14-REMEDIATION-20260610`:

1. **HYG-040 = Cheaper containment.** Add a cross-gate FP regression corpus required by LO verification of
   any gate change; add denial telemetry (gate, pattern-id, command-hash → .gtkb-state/gate-denials.jsonl);
   one-time GOV-15 reconciliation closing the fixed-but-open WIs. Defer the shared classifier library to a
   follow-on sub-project. Gates stay blocking (warn-mode downgrade rejected).
2. **HYG-042 = Hotfix the Bash parser now.** Rewrite PATH_DELIMITER_RE to match only genuine absolutes,
   treat rooted-driveless '/foo' as project-root-relative, whitelist null sinks, skip '://' context; seed
   the FP corpus with the 7 commands proven blocked this session; add PowerShell + Codex coverage.
3. **HYG-046 = Fix all three rigidities.** Widen SECTION_RE to h2/h3; replace the phrase tuple with two
   bounded regexes (sufficient / gap); split the conflated 'missing' return; port to the GO-time detector.
4. **HYG-047 = Auto-discovery in both gates.** Scan .groundtruth/formal-artifact-approvals/*.json for the
   newest packet whose target_path == the write target and content sha256 matches; keep env var as
   override; amend DCL-ARTIFACT-APPROVAL-HOOK-001 via the standard packet workflow.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB14-REMEDIATION-20260610`; the
governing specifications (`SPEC-AUQ-POLICY-ENGINE-001`, `SPEC-AUQ-NO-LLM-CLASSIFIER-001`,
`DCL-ARTIFACT-APPROVAL-HOOK-001`, `GOV-15`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`) already constrain the
policy-engine, deterministic-classifier, approval-hook, test-fix, and cross-harness-enforcement surfaces.
No new requirement is needed. The DCL-ARTIFACT-APPROVAL-HOOK-001 amendment is a hook-contract extension
recorded via the formal-artifact-approval packet at implementation time.

## Scope and Boundaries

In scope: the four decisions + the absorbed sub-findings (Bash-parser tool-coverage asymmetry; the
SPEC_LINK_HEADING / PATH_TOKEN_RE magic-content + duplicate-constant drift). Out of scope and explicitly
excluded: the full shared-classifier-library refactor (follow-on sub-project); downgrading any gate to
warn-mode (rejected); deploy/push. This proposal absorbs the advisory's ~20-WI gate-FP cluster — the
3322/3334/3336/3351/3356/3357/3358/3384/3410/3448/3454/3463/3493/3496/3497/3499/4304/4354/4355/4368 set —
folding the reconciliation + structural fixes into WI-4426 and describing them here rather than re-filing.
The reconciliation closes only WIs verified fixed-in-code (e.g. the re.MULTILINE, WI-AUTO-* acceptance,
and fence-aware section-collection fixes already in bridge-compliance-gate.py).

## Proposed Implementation

**Area 1 — HYG-040 gate-quality program.** Add `config/governance/gate-fp-corpus.toml` + a pytest module
(`platform_tests/scripts/test_gate_fp_corpus.py`) seeded with each WI's reproducer + the commands proven
blocked this session; make the FP corpus a required check in the LO gate-change verification checklist.
Add a denial-log line (gate, pattern-id, command-hash) to each blocking hook → `.gtkb-state/gate-denials.jsonl`.
Run the one-time GOV-15 WI reconciliation closing the fixed-but-open WIs (append-only resolve).

**Area 2 — HYG-042 Bash parser hotfix.** Rewrite PATH_DELIMITER_RE (enforcement/__init__.py) to match only
genuine absolutes (drive-letter both slash forms, UNC, MSYS /x/ translated before checking), resolve
rooted-driveless tokens against the project root (not the drive root), whitelist null sinks, and skip
'://' URL context. Add PowerShell coverage to the Claude adapter matcher and a Codex-side
directive-enforcement registration in `.codex/hooks.json`. Seed the parser FP corpus with the 7 commands.

**Area 3 — HYG-046 Requirement Sufficiency gate.** Widen SECTION_RE to `^#{2,3}\s+`; replace
REQUIREMENT_SUFFICIENCY_PHRASES with two bounded regexes (sufficiency / gap); split the 834-842 return into
'missing' vs 'unrecognized-phrasing (found: …)'; port the same fix to the GO-time detector
(implementation_start_gate.py) so pre-impl review and begin-time gate agree. Also de-duplicate the drifted
PATH_TOKEN_RE constant (bridge_applicability_preflight.py vs implementation_start_gate.py) into one source.

**Area 4 — HYG-047 packet auto-discovery.** Add a deterministic discovery branch to
narrative-artifact-approval-gate.py AND formal-artifact-approval-gate.py: select the newest packet under
.groundtruth/formal-artifact-approvals/ whose `target_path` == the write rel-path and `full_content_sha256`
== sha256(proposed content); env var stays an explicit override. Amend DCL-ARTIFACT-APPROVAL-HOOK-001.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` + `SPEC-AUQ-POLICY-ENGINE-001` (HYG-040) | test: the FP corpus pytest passes (every reproducer is NOT falsely blocked); each blocking gate appends a denial-telemetry record; the reconciliation resolves only WIs whose fix is present in code |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` (HYG-042) | test: the 7 everyday Bash commands (relative paths, URL, /dev/null, MSYS /x/) PASS the parser; a genuinely out-of-root reference is still DENIED; PowerShell + Codex registrations fire the directive |
| `SPEC-AUQ-POLICY-ENGINE-001` (HYG-046) | test: '### Requirement Sufficiency' is parsed (h3 accepted); a bounded sufficiency/gap statement is accepted; absent vs unrecognized-phrasing return distinct messages; GO-time and begin-time detectors agree |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (HYG-047) | test: a session-native Write to a protected narrative with a matching on-disk packet (target_path + sha256) PASSES with no env var; a mismatched/absent packet still BLOCKS; same for the formal gate |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/... groundtruth-kb/tests/framework/...` + `ruff check` AND `ruff format --check` |

## Acceptance Criteria

1. **Area 1:** gate-fp-corpus.toml + pytest module exist and are required by the LO gate-change checklist;
   denial telemetry writes to .gtkb-state/gate-denials.jsonl; the fixed-but-open WIs are reconciled (closed).
2. **Area 2:** the 7 everyday Bash commands pass; out-of-root refs still denied; PowerShell + Codex coverage
   added; parser FP corpus green.
3. **Area 3:** h2/h3 headings + bounded phrasing accepted; absent vs unrecognized-phrasing distinguished;
   GO-time and begin-time detectors agree; the PATH_TOKEN_RE duplicate is de-drifted.
4. **Area 4:** a compliant on-disk packet satisfies both the narrative and formal Write gates with no env
   var; DCL-ARTIFACT-APPROVAL-HOOK-001 amended via packet under `.groundtruth/formal-artifact-approvals/`.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-14-gate-fp-feedback-loop-003.md` with a matching `REVISED` line inserted at the
top of this thread's entry in `bridge/INDEX.md`; append-only. The FP corpus + denial telemetry STRENGTHEN
the gate layer (and thus the bridge protocol's enforcement) rather than weakening it; gates stay blocking.
`GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal Opposition records `GO`.

## Backlog Visibility

FAB-14 is WI-4426 under `GOV-STANDING-BACKLOG-001`; the one-time WI reconciliation is a GOV-15-gated
append-only resolve described as an inventory in Scope and Boundaries (the ~20-WI set), not a silent bulk
close — each closure cites the in-code fix. The formal-artifact-approval packet evidence governs the DCL
amendment.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-14 changes are in-root. Every generated artifact stays
under `E:\GT-KB\` — the FP-corpus config at `config/governance/gate-fp-corpus.toml`, the FP-corpus + parser
tests under `platform_tests/` and `groundtruth-kb/tests/framework/`, the denial telemetry at
`.gtkb-state/gate-denials.jsonl`, the approval packets under `.groundtruth/formal-artifact-approvals/`, the
gate/hook/parser edits in their in-root homes, and this bridge file under `E:\GT-KB\bridge\`. The cluster
relocates no file, touches no `applications/` subtree, and writes no out-of-root artifact; the root-boundary
parser fix actually tightens correct in-root enforcement.

## Risk and Rollback

- **Risk — loosening a gate parser introduces a true-negative (lets a real violation through):** every
  loosening is paired with a test asserting genuine violations are still blocked (out-of-root ref, mismatched
  packet, absent section). **Rollback:** revert the parser edit; the FP corpus is additive.
- **Risk — WI reconciliation closes a WI whose fix isn't actually complete:** reconciliation closes only
  WIs whose fix is verified present in code (cited line numbers); GOV-15 owner gating applies. **Rollback:**
  re-open the WI (append-only).
- **Risk — packet auto-discovery picks a wrong packet:** match requires BOTH target_path AND
  full_content_sha256 of the exact proposed content; newest-wins only among exact matches. **Rollback:**
  revert the discovery branch; env-var path unchanged.
- **Risk — amending a freshly-VERIFIED directive thread:** filed as an explicit defect amendment with the
  FP reproductions as evidence; the original VERIFIED stays in the audit trail.

## Recommended Implementation Routing

**Opus/Codex-supervised** — these are load-bearing enforcement surfaces (boundary parser, approval gates,
impl-auth) where a loosening bug re-opens a security/governance hole; not cheap-model candidates. Coordinate
the bridge-compliance-gate denial-telemetry edit with FAB-10 (which also touches that hook). Sequence Area 2
(Bash parser) early — it unblocks Bash as a working tool for the rest of the campaign.

## Recommended Commit Type

`fix:` — repairs four gate false-positive/evasion defects and the broken WI feedback loop, with
`feat:`-class additions (the FP regression corpus, denial telemetry, and packet auto-discovery).
