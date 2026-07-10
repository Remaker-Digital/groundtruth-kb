GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T17-22-11Z-loyal-opposition-B-335e14
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge-dispatch worker; resolved role loyal-opposition; auto-dispatch

# Loyal Opposition Verdict — GO — gtkb-wi5135-codex-shell-no-window-dispatch

bridge_kind: lo_verdict
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 008
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md (REVISED, prime-builder/codex, harness A)
Date: 2026-07-10 UTC

## Verdict

GO. The `-007` REVISED resolves the single blocking Finding from the `-006` NO-GO
— a `source`-scoped proposal citing a filing-only PAUTH — by creating and citing a
live, active, implementation-scoped WI-5135 project authorization. I verified that
authorization against canonical state (the `gt projects` reader, not the proposal's
self-assertion): `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710`
is `status: active`, unexpired, scoped to `WI-5135`, backed by owner-decision
`DELIB-202666064`, and grants `allowed_mutation_classes` of `source`, `tests`,
`bridge`, and `governance_evidence`. That is exactly the two-stage
filing-then-implementation authorization the `-006` corrected path required. The
`-004`-approved efficacy-gated technical scope is preserved verbatim in `-007` and
is NOT reopened by this review. Both mandatory preflights pass on the operative
`-007` file. No new blocking defect is introduced. Implementation may proceed
within the declared ten-path target scope, gated (per the proposal's own
commitment) on a successful `implementation_authorization.py begin` packet that
agrees with this GO, the cited implementation-scoped PAUTH, and the target paths
before any protected mutation.

## Sole `-006` Finding — disposition

### Finding 1 — [P1, blocking] Source-scoped proposal cited a filing-only PAUTH → CLEARED

The `-006` NO-GO required (1) a live implementation-scoped WI-5135 PAUTH backed by
`DELIB-202666064`, (2) the operative proposal re-filed as REVISED citing that PAUTH,
(3) the `-004` technical scope preserved verbatim, and (4) both pre-filing preflights
re-run. All four are satisfied:

- **Implementation-scoped PAUTH is live (canonical-state verified).**
  `gt projects show-authorization PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710 --json`
  returns rowid `566`, `status: active`, `expires_at: null`,
  `project_id: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION`,
  `included_work_item_ids: ["WI-5135"]`,
  `owner_decision_deliberation_id: DELIB-202666064`, and
  `allowed_mutation_classes: ["source", "tests", "bridge", "governance_evidence"]`.
  Its `scope_summary` bounds the WI-5135 Codex Windows shell no-window containment
  slice, and its `forbidden_operations` encode the technical guards (Codex-A stays
  quiesced; no sweep-commit bundling; no groundtruth.db / harness-state staging).
  This directly matches the `created: true, rowid: 566` result the proposal reports,
  so the proposal's self-report and canonical state agree.
- **Operative proposal cites it.** The `-007` `Project Authorization:` metadata line
  — the line `implementation_authorization.py begin` actually reads — now names the
  `...-SOURCE-TEST-20260710` PAUTH, not the `...-IMPLEMENTATION-PROPOSAL-FILING` PAUTH.
- **Technical scope preserved.** The `-007` Preserved Technical Scope, Proposed Scope,
  and Acceptance Criteria sections carry the `-003`/`-004` design unchanged
  (efficacy-gated acceptance tied to zero visible pwsh windows; the four-step decision
  rule with `windows.sandbox_private_desktop` demoted to one candidate plus named
  fallbacks and an honest fail path; schema-v2 multi-command smoke; fail-closed
  readiness; bounded dispatcher-path proof; Codex-A dispatch stays disabled). The
  ten-entry `target_paths` set is byte-identical to `-003` (five source + five test).
- **Preflights re-run independently.** I re-ran both mandatory preflights on the
  operative `-007` file, not trusting the proposal's Pre-Filing self-assertion:
  applicability `preflight_passed: true`, empty missing-spec lists; clause preflight
  exit 0, 0 blocking gaps.

### `-006` Finding 2 — [P1, root cause] `-004` over-relied on the `begin` packet → dispositioned

The `-006` root-cause finding (that `implementation_authorization.py begin` and
`implementation_start_gate.py` do not validate `allowed_mutation_classes` against
`implementation_scope`) is addressed at the review level exactly as `-006`
prescribed: the corrected condition is not a passing `begin` packet but the operative
proposal citing an implementation-scoped PAUTH, verified by LO. Because `begin` reads
the proposal's `Project Authorization:` line to select the PAUTH (confirmed by the
`-005` evidence, where the `-003` filing PAUTH produced a `['bridge', 'metadata']`
packet), `-007` citing the source/test PAUTH now yields a correctly-scoped begin
packet. The scope-blind gate is compensated by this LO verification of the cited
authorization; it is not silently relied upon.

## Preserved strengths (from `-002`/`-004`; do not rework)

The root-cause premise (grandchild pwsh consoles uncovered because
`CREATE_NO_WINDOW` in `scripts/windows_subprocess.py` applies to the direct child
only), the sequencing (WI-5105/5112/5132 resolved before this slice), the
non-duplication finding (WI-5052 fixed parent-level no-window only), the genuine
owner authorization (`DELIB-202666064`), and the defensive posture (Codex-A
`can_receive_dispatch` stays false until a separate governed enablement step) all
remain intact in `-007`.

## Non-blocking observations (implementation-phase notes; not GO conditions)

1. **[P3 — carried from `-004`] The bounded dispatcher-path proof must not re-arm
   persistent dispatch.** Acceptance Criterion #5 runs real Codex shell activity
   through the wrapped-command path; on any visible window the implementation must
   capture that as the decision-rule step-4 failure class and stop, and must not
   refresh the no-window verification artifact in a way that re-enables Codex-A
   dispatch (the WI-5080 verification-refresh re-trigger hazard). The proposal already
   carries the right guards; this is guidance.
2. **[P3 — carried from `-006`] Mutation-class enforcement gap remains open.** The
   `-006` NO-GO recommended (not as a condition) a follow-on work item to add
   mutation-class-versus-scope validation to the `implementation_authorization.py` /
   `implementation_start_gate.py` chain, since that discipline held here only because
   Prime conscientiously filed a NO-ACTION rather than proceed on the scope-blind
   `begin` packet. That recommendation is unaffected by this GO and remains a
   Prime-Builder backlog-capture item (check the backlog for an existing item first).
   It is not a condition of this verdict.
3. **[P3] Recommended commit type.** `-007` recommends `fix`. The slice remediates
   the window-storm defect, so `fix` is a defensible declared type even though it adds
   `scripts/codex_shell_no_window_wrapper.py`; the implementation report should confirm
   the final type matches the diff stat per the Conventional Commits discipline.

## Applicability Preflight

Command: `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch`.
Operative file resolved: `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md` (REVISED). Result summary:

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: `sha256:5d2186e37d210c3ad16d90daa2309235595e203a503d212c6b359e3fd8d978c5`

## Clause Applicability

Command: `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch` (mandatory mode; exit 0).

- Clauses evaluated: 5 (must_apply: 3, may_apply: 2, not_applicable: 0).
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps (gate-failing): 0.

No blocking gaps; no owner-waiver line required.

## Prior Deliberations

- `DELIB-202666064` — owner decision (AUQ): fix WI-5135 for the headless Prime path;
  authorizes the work direction and the implementation-scoped WI-5135 PAUTH.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — owner directive governing the objective
  (no visible console windows) and the safe quiesced status quo.
- `DELIB-202665909` — VERIFIED for the parent-level dispatcher no-window containment
  (WI-5052) that this grandchild-shell follow-on supersedes.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — governs the `-005` NO-ACTION / `-006` NO-GO
  lifecycle correction that this GO closes.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-004.md` — the prior GO whose
  efficacy-gated technical scope this GO preserves unchanged.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-006.md` — the LO NO-GO whose
  single authorization-scope Finding this GO clears.

## Methodology trail

- Read the full thread chain (`-001` NEW, `-002` NO-GO, `-003` REVISED, `-004` GO,
  `-005` NO-ACTION, `-006` NO-GO, `-007` REVISED) before verdict.
- Canonical bridge state: `gt bridge show gtkb-wi5135-codex-shell-no-window-dispatch
  --json --compact` reported latest `REVISED` at `-007` with version_count 7.
- Review independence: reviewer session `2026-07-10T17-22-11Z-loyal-opposition-B-335e14`
  (harness B, loyal-opposition) differs from the `-007` author session
  `019f4ace-e667-7030-b632-1cf002c1a0f7` (harness A, Codex), and from my prior
  `-002`/`-004`/`-006` sessions — not a same-session self-review.
- Load-bearing authorization check: `gt projects show-authorization
  PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710 --json`
  confirmed active status, source/tests mutation classes, WI-5135 membership,
  `DELIB-202666064` backing, and null expiry; cross-checked against `gt projects
  authorizations PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json`.
- Role: `gt harness roles` confirmed harness B = claude = loyal-opposition (active).
- Both mandatory preflights re-run independently on the operative `-007` file:
  applicability passed with empty missing-spec lists; clause preflight exited 0 with
  0 blocking gaps across 5 clauses.

## Summary

The revision does exactly what the `-006` NO-GO asked: it creates a live
implementation-scoped WI-5135 PAUTH (source + tests, `DELIB-202666064`-backed) and
cites it in the operative `Project Authorization:` line, resolving the
authorization-scope contradiction while preserving the `-004`-approved efficacy-gated
technical scope verbatim. Canonical-state verification confirms the PAUTH; both gates
are green; review independence is confirmed; no new blocking defect is introduced. GO
— with the three P3 implementation-phase notes carried into the implementation report,
and the standing recommendation to capture the mutation-class enforcement gap as a
follow-on work item.
