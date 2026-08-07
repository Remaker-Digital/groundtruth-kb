NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e551d95-6728-46fd-b64d-181c9617a827
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_proposal
Document: gtkb-w0-worker-enablement-plumbing
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5839
related_work_items: ["WI-5812", "WI-5825", "WI-5742", "WI-5806", "WI-5849", "WI-5866", "WI-5368"]

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "scripts/harness_identity.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py", "platform_tests/scripts/test_session_envelope_cli_choice.py", "platform_tests/scripts/test_gtkb_session_id.py"]
implementation_scope: worker_enablement_plumbing_goose_binding_and_capability_ttl_wiring
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# W0.1 Thread B — Worker-Enablement Plumbing: Goose Session Binding, Capability-TTL Wiring, and Scratch-Tree Ignores

## Summary

Five small, evidence-verified plumbing defects block or degrade governed
worker sessions. Each is a bounded code or config-file fix with a
deterministic test:

(a) `gt session envelope open --harness-name goose` ignores a pre-set
`GOOSE_SESSION_ID`, so goose workers mint one session id at envelope-open and
resolve a DIFFERENT id at claim time, producing claim-denial id mismatches.
(b) `goose` is absent from `DEFAULT_HARNESS_IDS` even though the harness is
owner-registered as identity `G`.
(c) The WI-5839 publication-capability TTL raise never reached the mint: the
runtime still mints capabilities with an effective 120-second TTL against a
configured 800 seconds, because the mint default is a hard-coded 120 and the
production writer passes no TTL.
(d) The Loyal Opposition scratch directory `.tmp-lo-verdict-drafts/` is
untracked and unignored, polluting `git status` for every session.
(e) `.driveignore` is untracked, so its protections are not durable, and it
lacks the `.pytest-tmp/` churn-tree exclusion.

## Live Anchor Evidence (every anchor re-verified 2026-08-06)

1. `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:26` —
   `_HOST_SESSION_ID_ENV_BY_HARNESS` contains only `codex` and `cursor`
   entries; no `goose`. `_host_session_id` (line 65) therefore returns None
   for goose, and `envelope open` (line 144) never binds the caller's
   GOOSE_SESSION_ID. Asymmetry proof: the uniform session-id resolver
   `scripts/gtkb_session_id.py` DOES resolve `GOOSE_SESSION_ID` (lines 69, 88,
   97), and `groundtruth_kb/session/envelope.py:41` maps
   `"goose": ("GOOSE_SESSION_ID",)`. The claim path and the envelope-open CLI
   disagree, which is exactly the id-mismatch denial observed in sandbox
   reproduction.
2. `scripts/harness_identity.py:21` — `DEFAULT_HARNESS_IDS` covers
   codex/claude/antigravity/ollama/cursor/openrouter (A-F); `goose` is absent
   while `harness-state/harness-identities.json` records goose as identity
   `G` via owner-directed identity registration (assigned 2026-07-08).
3. `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` —
   `mint_bridge_publication_capability` (line 3342) declares
   `ttl_seconds: int = 120` at line 3356 (drift note: an earlier register
   cited approximately line 3347; live line is 3356) and enforces the
   1-800 second ceiling at lines 3364-3365. The module imports nothing from
   `groundtruth_kb.project.timer_config` (grep verified: only two comment
   mentions of the word timer). Meanwhile
   `config/governance/protected-commit-timers.toml:129` configures
   `bridge_publication_capability_ttl_seconds = 800` and the paired
   `evaluation_bound_seconds = 790` (line 115, raised 2026-08-06 under the
   WI-5839 lineage). Effective minted TTL is therefore 120s against a
   configured 800s.
4. `scripts/gtkb_bridge_writer.py:1232` — the single production mint call
   (`mint_bridge_publication_capability(...)`, lines 1232-1241) passes no
   ttl_seconds argument, so the 120-second default governs every real
   publication.
5. `.gitignore` — no `.tmp-lo-verdict-drafts/` entry (grep verified); the
   directory exists untracked in the worktree today.
6. `.driveignore` — untracked (`git status --porcelain` shows `??`), so the
   Drive-sync protections it declares are not durable in git. Drift note
   against the earlier register: the live untracked file ALREADY contains
   `.gtkb-state/` (line 57); only `.pytest-tmp/` is missing. `.pytest-tmp/`
   exists in the worktree as a live churn tree.

## Proposed Change

1. (a) Add `"goose": "GOOSE_SESSION_ID"` to `_HOST_SESSION_ID_ENV_BY_HARNESS`
   at `cli_session_handoff.py:26`, aligning the envelope-open CLI with
   `gtkb_session_id.py` and `session/envelope.py`.
2. (b) Add `"goose": "G"` to `DEFAULT_HARNESS_IDS` at
   `harness_identity.py:21`, matching the owner-registered identity.
3. (c) Wire the timer SoT into the mint path, keeping the 800-second ceiling
   unchanged: `mint_bridge_publication_capability` resolves its default TTL
   through `timer_config.resolve_protected_commit_timers` (the single
   resolution path: env override, then
   `config/governance/protected-commit-timers.toml`, then in-code fallback)
   when the caller passes no explicit value; an explicit caller value remains
   supported inside the existing 1-800 validation. `gtkb_bridge_writer.py`
   passes the resolved TTL at the single production mint call (line 1232) so
   the writer's publication window matches the configured pair. No change to
   `timer_config.py` or to `protected-commit-timers.toml`.
4. (d) Add `.tmp-lo-verdict-drafts/` to `.gitignore`.
5. (e) Bring `.driveignore` under version control (staged for the Loyal
   Opposition finalization commit) and add the missing `.pytest-tmp/` line;
   `.gtkb-state/` is already present at live line 57 and is not duplicated.
6. Tests: create `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py`
   (the module the WI-5839 chain declared and that is absent today) asserting:
   the mint default equals the resolver value (config-backed fixture); the
   800-second ceiling is still enforced for explicit values; and the writer's
   mint call carries the resolved TTL. Extend
   `platform_tests/scripts/test_session_envelope_cli_choice.py` with a goose
   envelope-open binding case (GOOSE_SESSION_ID pre-set binds that exact id,
   via CliRunner and monkeypatch per the module's existing pattern — this is
   the existing cli_session_handoff coverage module). Extend
   `platform_tests/scripts/test_gtkb_session_id.py` (which already asserts
   goose membership in the resolver orders) with a
   `DEFAULT_HARNESS_IDS` goose-equals-G assertion.

## Relationship to WI-5839 and Concurrent Threads (collision ledger)

- WI-5839 thread state (live 2026-08-06): 001 NEW, 002 GO, 003 NO-ACTION,
  004 NO-GO, 005 REVISED, 006 GO, 007 NEW (config-only bound-raise report),
  008 NO-GO (report's porcelain claim failed fresh read). The v005/v006 GO
  defines Slices A-D; the config surface (Slice B posture) landed in
  `protected-commit-timers.toml` (790/800 live), but Slice A's mint-side SoT
  resolution, the Slice C admission guard, and the Slice D test module remain
  unbuilt. This thread implements the BOUNDED mint-wiring subset: default
  resolution through the existing resolver plus writer TTL pass-through plus
  the missing test module. It does NOT implement Slice C mint-time
  transaction-cost admission, does NOT remove the in-code fallback constants
  in `timer_config.py` (full Slice A), and does NOT change the 800-second
  ceiling. Those remain with the WI-5839 thread, which also still owes a
  corrected REVISED report for its config-only change. This split is the
  owner-directed Wave 0 unblock: without the mint wiring, every publication
  today runs on a 120-second window that the 790-second gate bound legally
  exceeds, which is the structural stranding precondition the timer pair
  exists to prevent.
- Foreign dirty bytes (disclosed; sequencing precondition):
  `registry_control_plane.py` and `gtkb_bridge_writer.py` are dirty in the
  worktree today with WI-5825 receipt-backfill work (control-plane
  receipt_backfill evidence view plus a new function block after line 4360;
  writer `backfill_publication_receipt` appended after line 1510). Both
  foreign regions are hunk-disjoint from this thread's edit sites (mint
  signature at 3342-3412; mint call at 1229-1241). Implementation begins only
  after re-verifying target state at implementation-start; if the foreign
  hunks remain, edits stay strictly hunk-disjoint and the foreign bytes are
  neither staged, reverted, nor adopted. If the finalization commit cannot be
  scoped without capturing foreign bytes in these two files, implementation
  pauses and reports rather than committing mixed work.
- Explicit scope guard: this thread touches NEITHER
  `scripts/dispatcher_runtime.py` NOR `scripts/bridge_lifecycle_resolver.py`.
  Both are dirty with other threads' in-flight work (WI-5314 dispatcher
  envelope-rollback; WI-5827 resolver synonym-ordering) and are outside this
  thread's target_paths.
- WI-5812 (goose governed filing attestation, latest NO-GO) owns the goose
  wrapper build-out; this thread's goose items (a)-(b) are upstream session-id
  and identity plumbing that WI-5812's wrapper will rely on, not wrapper work.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - applicable because `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` sits under the project/ subtree named in the applicability matrix; every change stays within the GT-KB root and leaves the root/applications boundary untouched.

- WI-5839 thread `bridge/gtkb-wi5839-capability-ttl-sizing-001..008` (GO at
  002 and 006) — the governing capability-TTL sizing decision chain whose
  mint-wiring subset this thread implements.
- `DELIB-20260803084763` — owner decision authorizing the WI-5839 bound/TTL
  raise (700/800 pair; committed `10f0e2eea`); the configured pair this
  wiring makes effective at the mint.
- `GOV-ENV-LOCAL-AUTHORITY-001` — env-local layer of the timer resolution
  precedence; the wiring uses the existing resolver rather than introducing a
  second env read.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the publication capability protects the
  numbered-file bridge chain; TTL wiring changes lifetime sizing only, never
  the typed-authorization contract.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing links
  cited concretely here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/work-item
  linkage in the metadata block (WI-5839 has active membership in
  PROJECT-GTKB-HOUSEKEEPING-HARDENING; whole-project PAUTH cited).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in
  the verification plan below.
- `GOV-WORK-TREE-HYGIENE-001` — hunk-disjoint handling of the WI-5825 foreign
  dirty bytes; no concurrent thread's bytes are staged.
- WI-5849 / WI-5866 — context: commit-blocking lock contention and
  shared-helper dirty-state finalization blockage, the failure environment
  the ignore-file items (d)-(e) reduce.
- WI-5368 and the finalization-stranding evidence recorded in
  `config/governance/protected-commit-timers.toml` comments (WI-5368,
  WI-5758, WI-5759, WI-5824 and the cleanup-evidence incident directories) —
  the observed cost of an under-sized effective TTL.

## Prior Deliberations

Searches run 2026-08-06:
`gt deliberations search "publication capability ttl timer sizing" --limit 5`
and `gt deliberations search "goose session envelope claim" --limit 5`.

- `DELIB-20260803084763` — owner timer-sizing decision (bound/TTL raise) per
  the WI-5839 lineage; the controlling sizing authority for item (c).
- `DELIB-202667748` — standing owner directive: centralize timers, throttles,
  and thresholds in one source of truth, tuned from data; item (c) routes the
  mint default through that single SoT resolver.
- `DELIB-202667722` — relaxed-first timer governance with one resolution
  path; the resolver this wiring consumes implements it.
- `DELIB-202667739` — owner declined an interim TTL raise for the
  implementation-start PACKET expiry class; distinct timer class from the
  publication capability wired here, cited to show the distinction was
  checked.
- `DELIB-202667723` — expiry evidence must fail actionably rather than strand
  terminal work; motivating context for making the configured TTL effective.
- `DELIB-202667095` — Goose FSM amendment Phase 1 VERIFIED; goose is an
  operational governed harness whose session plumbing items (a)-(b) complete.
- `DELIB-202667098` and `DELIB-202668114` — Goose activation/role-parity and
  WI-5812 governed-filing NO-GO verdicts; boundary evidence that wrapper-side
  goose work remains with WI-5812 while this thread fixes only the upstream
  id plumbing.
- File refs: `bridge/gtkb-wi5839-capability-ttl-sizing-001..008` (thread
  state as inventoried in the collision ledger);
  `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-*`
  (the concurrent thread owning the foreign dirty bytes disclosed above).

## Owner Decisions / Input

- Owner AUQ, 2026-08-05 (four recorded answers): investigation method, plan
  scope, context budget, and review model for the friction-remediation
  program that produced this thread's work packet.
- Owner AUQ, 2026-08-06: "Expand Wave 0 now" — authorizes the Wave 0 scope
  expansion containing this worker-enablement thread.
- Owner AUQ, 2026-08-06: "Yes — file W0.1/W0.3/W0.4 now" — adopts split-phase
  execution and authorizes filing this proposal (W0.1 Thread B) immediately.
- `DELIB-20260803084763` — the recorded owner timer-sizing decision that item
  (c) makes effective at the mint; no new sizing decision is requested.
- Non-canonical context: `scratchpad/gtkb-friction-remediation-plan-2026-08-06.md`
  (owner-review draft; Wave 0 / W0.1 packet definition). Cited as context
  only; authority rests on the AUQ decisions, the WI-5839 GO chain, and the
  governing specs above.

## Requirement Sufficiency

Existing requirements sufficient. The WI-5839 GO chain plus
`DELIB-20260803084763` and `DELIB-202667748` define the capability-TTL
outcome and the single-SoT posture; `GOV-ENV-LOCAL-AUTHORITY-001` defines the
resolution precedence; the goose identity is already owner-registered in
`harness-state/harness-identities.json`. No new or revised requirement is
required before implementation.

## Specification-Derived Verification Plan

All commands are cmd.exe-safe and runnable from E:\GT-KB as written.

| Requirement | Test / command | Required observed behavior |
|---|---|---|
| WI-5839 mint default from SoT | new module `platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py`: mint-default-equals-resolver case | With a config-backed fixture, a mint with no explicit TTL produces a capability whose lifetime equals the resolver's bridge_publication_capability_ttl_seconds, not 120. |
| Ceiling unchanged | same module: explicit-values case | An explicit 801-second request is refused with the existing typed error; 800 is accepted; validation bounds are byte-equivalent to the pre-change 1-800 rule. |
| Writer passes resolved TTL | same module: writer call-shape case | The single production mint call in gtkb_bridge_writer.py carries the resolver-derived TTL. |
| Live effective-TTL probe | `python -c "from groundtruth_kb.project.timer_config import resolve_protected_commit_timers as r; print(r().bridge_publication_capability_ttl_seconds)"` | Prints 800 (the configured value the mint now inherits). |
| Goose envelope binding | extended `platform_tests/scripts/test_session_envelope_cli_choice.py` goose case | With GOOSE_SESSION_ID pre-set, `session envelope open --harness-name goose` binds exactly that id; codex/cursor behavior unchanged. |
| Goose default identity | extended `platform_tests/scripts/test_gtkb_session_id.py` assertion | DEFAULT_HARNESS_IDS resolves goose to G, matching harness-identities.json. |
| LO scratch dir ignored | `git check-ignore .tmp-lo-verdict-drafts/probe.md` | Exit code 0 (path ignored). |
| Drive-ignore completeness | `findstr /C:".pytest-tmp/" E:\GT-KB\.driveignore` and `findstr /C:".gtkb-state/" E:\GT-KB\.driveignore` | Both lines present; `.driveignore` is included in the finalization include-set so it becomes tracked. |
| Full regression on touched modules | `python -m pytest platform_tests/scripts/test_bridge_publication_capability_ttl_sizing.py platform_tests/scripts/test_session_envelope_cli_choice.py platform_tests/scripts/test_gtkb_session_id.py platform_tests/scripts/test_session_handoff_service.py -q` | All pass. |
| Code quality (both gates) | `ruff check` and `ruff format --check` on every touched .py file | Both pass; they are separate gates per the bridge protocol. |

## Acceptance Criteria

1. Only the nine declared target_paths change; `timer_config.py`,
   `protected-commit-timers.toml`, `dispatcher_runtime.py`, and
   `bridge_lifecycle_resolver.py` are untouched.
2. A no-argument mint resolves its TTL through the single timer SoT resolver;
   the 1-800 second validation is unchanged; the production writer passes the
   resolved TTL.
3. Goose envelope-open binds a pre-set GOOSE_SESSION_ID; goose resolves to
   identity G by default; existing codex/cursor behavior is regression-tested
   unchanged.
4. `.tmp-lo-verdict-drafts/` is ignored; `.driveignore` enters version
   control with `.pytest-tmp/` added and no duplicate `.gtkb-state/` line.
5. The WI-5825 foreign dirty regions in the two shared files are neither
   staged, reverted, nor adopted; if scoped finalization is impossible while
   they remain, implementation pauses and reports.
6. The new and extended test modules pass, and the verification-plan probe
   prints 800.
7. `ruff check` and `ruff format --check` both pass on every changed .py file.
8. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment,
   or external system is mutated; no commit is created by Prime Builder —
   finalization remains the Loyal Opposition atomic step.

## Risk and Rollback

Highest risk: widening the effective capability lifetime from 120s to the
configured 800s enlarges the window in which a minted capability outlives a
failed publication attempt; this is the owner-decided posture
(`DELIB-20260803084763`) and is bounded by the unchanged ceiling, the
unchanged coupled-invariant validation in the resolver, and the existing
single-use capability contract. Second risk: the shared-file overlap with
WI-5825's in-flight receipt-backfill work; bounded by hunk-disjoint edits,
implementation-start re-verification, and the pause-and-report rule in
acceptance criterion 5. Third risk: an operation-time authorization evaluator
could classify the repo-root ignore files or the two scripts as target
classes outside the cited PAUTH; if the implementation-start packet or
operation-time evaluation denies any class, implementation stops and reports
the exact denial rather than forcing. Rollback is a plain revert of the
source hunks, deletion of the new test module, and removal of the two ignore
lines; minted-capability behavior returns to the 120-second default with no
data migration.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "F-113/F-114 (friction register 2026-08-06, sandbox-reproduced claim-denial mechanism); WI-5839 thread (GO'd Slices A/C unbuilt); DELIB-20260803084763 owner timer-sizing decision; goose probe threads wi5808 dsv4pro r1-r3",
  "canonical_authority": "DELIB-20260803084763; WI-5839 bridge thread; GOV-ENV-LOCAL-AUTHORITY-001; harness identity registry (harness-state/harness-identities.json, goose=G)",
  "primary_route": "three bounded plumbing fixes: goose host-session-id binding in cli_session_handoff.py, goose in DEFAULT_HARNESS_IDS, publication-capability mint TTL wired to the timer_config resolver (bounded WI-5839 mint-wiring subset). Ignore-file hygiene (.tmp-lo-verdict-drafts gitignore line; .driveignore tracking + .pytest-tmp line) is DEFERRED out of this thread after PAUTH operation-time classification denied repository_metadata/unclassified targets under the cited authorization; it routes to the W0.2 custodial lane with owner decision evidence instead.",
  "before_behavior": "goose envelope-open generates a fresh session id while the claim CLI resolves GOOSE_SESSION_ID from env -> id mismatch -> go_implementation claims denied 'not prime-eligible' (reproduced); mint defaults ttl_seconds=120 ignoring the configured 800 (config raise decorative at runtime); LO scratch dir untracked and unignored; .driveignore untracked with .pytest-tmp unlisted",
  "after_behavior": "goose envelope-open binds GOOSE_SESSION_ID when set (parity with codex/cursor mapping); minted capabilities carry the resolver TTL under the existing 800 ceiling; scratch dir ignored; .driveignore tracked and covering both churn trees",
  "self_descriptive_naming": "no renames; one dict entry, one list entry, one default-source change, two ignore-file lines",
  "obsolete_guidance_disposition": "none removed; bridge_claim_cli docstring env-var list refresh is deferred to the goose-adoption lane (disclosed, out of scope here)",
  "history_preservation": "append-only surfaces untouched; consumed-capability rows unaffected (TTL bounds mint-to-consume only, per the code-of-record comment)",
  "baseline": {
    "host_session_id_map": "codex + cursor only (cli_session_handoff.py:26)",
    "default_harness_ids": "goose absent (harness_identity.py:21)",
    "mint_ttl_default": "120s at registry_control_plane.py:3356; no timer_config import; writer mint call at gtkb_bridge_writer.py:1232 passes no TTL",
    "config_pair": "evaluation_bound 700 / capability TTL 800 (resolver-verified)",
    "driveignore": "untracked; .gtkb-state/ already listed (line 57); .pytest-tmp/ missing"
  },
  "expected_result": {
    "goose_bootstrap": "envelope-open with GOOSE_SESSION_ID pre-set binds that id; claim succeeds without the manual copy-back step",
    "mint_ttl": "resolver value (800s) observed on freshly minted capabilities; ceiling honored; new test module green",
    "ignore_hygiene": "deferred to the W0.2 custodial lane (PAUTH class denial documented above); this thread makes no ignore-file change"
  },
  "rollback": "single revert; no data migration; previously minted capability rows are unaffected either way",
  "hard_invariants": "publication-capability consume-once semantics unchanged; 800s code ceiling unchanged; no dispatcher or lifecycle-resolver file touched (both carry other threads' dirty work - explicitly out of scope); claim eligibility rules unchanged beyond correct id binding",
  "fail_closed_conditions": "claim CLI continues to fail closed on id mismatch or missing envelope; mint continues to refuse existing targets; envelope-open continues to fail on unknown harness names",
  "essential_context_preservation": "the WI-5839 thread remains the authority for the unbuilt Slice C scope; this thread implements only the mint-wiring subset and says so, so the remaining scope stays visible"
}
```

## Cross-Harness Disposition

Per-harness parity declaration (per `ADR-CROSS-HARNESS-PARITY-001` Q8 /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`):

- **goose (G)**: primary beneficiary — gains the same host-session-id env binding codex and cursor
  already have (mechanism parity, not divergence).
- **codex (A) / cursor (E)**: existing map entries unchanged; behavior identical before and after.
- **claude (B) / antigravity (C) / ollama (D) / openrouter (F) / alibaba (H)**: unaffected by the
  map (their id resolution paths are untouched); mint TTL change applies uniformly to every
  harness that mints publication capabilities through the shared writer.
- No harness-surface hook/skill files in target_paths; no projections to regenerate; no typed
  waiver requested.

## Recommended Commit Type

`fix` — makes an owner-decided configured value effective at the runtime that
ignored it, repairs a session-id binding defect, and completes ignore-file
coverage; no new capability surface is added.

## DISARM — Implementation

This file requests review only. It grants no protected-edit, claim, start,
finalization, or cleanup authority. Implementation requires the Loyal
Opposition GO on this thread, a fresh work-intent claim, an
implementation-start authorization packet created from that GO, and clean or
demonstrably hunk-disjoint preimages on the two shared files before any
target path is touched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
