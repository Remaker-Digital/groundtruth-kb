NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 8cd56f34-2ccb-41c3-86e3-e099620f487d
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: 1m

# Git pre-commit gate: block protected-surface commits without GO-auth or VERIFIED evidence (WI-4613 Slice A)

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4613

target_paths: ["scripts/check_protected_commit_authorization.py", ".githooks/pre-commit", "platform_tests/scripts/test_check_protected_commit_authorization.py"]

## Summary

WI-4613 (P2): no mutating GT-KB change should be committed (by any harness)
without a live GO-authorization packet covering it or a VERIFIED verdict citing
it. Owner decision (AskUserQuestion 2026-06-17): **"Hard git gate, protected
surfaces"** — a git-level pre-commit gate (uniform across all harnesses, since
git invokes `.githooks/pre-commit` regardless of which harness staged the
change) that BLOCKS a commit when staged changes touch protected surfaces
without GO-auth/VERIFIED evidence, while ALLOWING routine docs/memory/scratch.
This is **Slice A** — the deterministic code gate only. The AGENTS.md/`.claude/rules`
directive formalization is **Slice B** (protected narrative; needs
formal-artifact-approval packets) and is explicitly out of scope here.

## Problem

GT-KB's implementation-start gate is **write-time** (PreToolUse): it blocks
*writing* protected mutations without a GO-auth packet. There is no **commit-time**
check that staged changes carry GO-auth or VERIFIED evidence, so a change written
under one authorization (or by a harness lacking the PreToolUse gate, cf. WI-4543)
can be committed without any bridge evidence. `.githooks/pre-commit` is the one
enforcement point every harness shares (git invokes it via `core.hooksPath` on
every commit), making it the correct uniform gate.

## Proposed fix

Add `scripts/check_protected_commit_authorization.py` — a stdlib-import-only,
read-only detector with an `evaluate(root, *, paths=None)` pure function, a
`main()` with `--staged|--paths|--json|--project-root`, and a 0/1/2 exit-code
contract (mirroring the architectural twin `scripts/check_narrative_artifact_evidence.py`).
Wire it into `.githooks/pre-commit` after the existing ruff-format gate in the
established `"$PYTHON_BIN" scripts/<gate>.py --staged || exit $?` style.

### Protected-surface classification (dotfile-correct)

Import the constant DATA from `scripts/implementation_start_gate.py`
(`PROTECTED_EXACT`, `PROTECTED_PREFIXES`, `ALLOWED_WRITE_PREFIXES`,
`DIAGNOSTIC_WRITE_PREFIXES`) as the single source — but perform matching with a
**correct** normalization. The reused predicate `is_protected_path`
(`implementation_start_gate.py:211`) uses `relative_path.lstrip("./")`, which
strips leading dots as a CHARACTER SET, so `.claude/hooks/h.py` →
`claude/hooks/h.py` and silently fails to match `.claude/hooks/`. Empirically
confirmed: `is_protected_path` returns False for `.claude/hooks/`,
`.codex/gtkb-hooks/`, `.github/`, `.claude/settings.json`, `.codex/hooks.json`.
This gate therefore uses `removeprefix("./")` (prefix strip, not char-set
strip) so dot-prefixed protected surfaces classify correctly. (The shared
`is_protected_path`/`protected_mutation_guard` lstrip bug is captured separately
as WI-4642; this gate is correct independently of that fix.)

The Slice A protected set = correctly-matched set B
(`scripts/`, `groundtruth-kb/src/`, `groundtruth-kb/tests/`, `platform_tests/`,
`tests/`, `.claude/hooks/`, `.claude/rules/`, `.codex/gtkb-hooks/`, `config/`,
`.github/`, plus the exacts `.claude/settings.json`, `.codex/hooks.json`,
`pyproject.toml`, `groundtruth.toml`) **plus** `groundtruth.db` (the owner's
"KB" surface) **plus** `.githooks/` (self-protection so the gate's own wiring
cannot be edited without authorization), **minus** the narrative `.md` surfaces
(`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, `applications/*/CLAUDE*.md`)
which are already gated at commit time by `check_narrative_artifact_evidence.py`
(no double-gating). Intentionally excluded (ALLOW routine): `bridge/`,
`independent-progress-assessments/`, `.groundtruth/session/snapshots/`,
`.gtkb-state/`, `memory/*.md`, `MEMORY.md`, `docs/`, and anything outside the set.

### Evidence check (GO-auth OR VERIFIED; bounded)

Enumerate staged files via `git diff --cached --name-only --diff-filter=ACM`
(deletions excluded — no committed content to authorize). For each staged file:

1. Not protected → ALLOW.
2. **GO-auth path** → ALLOW iff some `list_named_packets(root)` row has
   `valid == True` (live `_validate_packet`: GO-still-GO, no newer GO,
   not awaiting-review/terminal/deferred, not expired) AND
   `path_authorized({"target_path_globs": row["target_path_globs"]}, rel)`.
   The GO-authorized-in-flight allowance falls out for free (an active
   `begin`-minted packet whose GO is still live passes).
3. **VERIFIED path** (no TTL — durable terminal evidence), **bounded to the
   by-bridge packet set** (NOT a scan of all `bridge/*.md`): for each by-bridge
   named packet, read its thread via `bridge_entry(root, packet["bridge_id"])`;
   if the thread's latest status is terminal `VERIFIED` and the GO the chain
   rests on approved a proposal whose `extract_target_paths()` covers `rel`,
   ALLOW. The proposal is found by mirroring `approved_files_for_go`'s exact
   traversal (`entry.versions` is newest-first; the GO's first older
   `NEW`/`REVISED` is the approved proposal). Do NOT call `approved_files_for_go`
   directly — it raises on terminal-VERIFIED threads
   (`implementation_authorization.py:399-403`). Bounding to the by-bridge packet
   set keeps the per-commit cost small (the packet cache, not ~7,000 bridge
   files).
4. Else → BLOCK.

### Fail-closed contract

Exit 0 = clean; exit 1 = block-with-findings (a protected staged file lacking
BOTH evidence paths, OR an evidence-resolution error — corrupt packet JSON,
unreadable bridge file, MemBase DB-read failure during `_validate_packet` — while
evaluating a protected file, treated as no-evidence → block); exit 2 = the
gate's own error. A `git diff --cached` failure means the staged set is unknown,
so the gate cannot prove the commit is routine → **exit 2** (abort under
`set -e`), never exit 0. The fail-closed behavior cannot block routine commits:
when zero staged files are protected the gate short-circuits to exit 0 (after the
staged set is read) before touching any packet/bridge/DB machinery, so an
evidence-subsystem error is unreachable for a pure docs/memory/scratch commit.
Note: `_validate_packet` may open `groundtruth.db` (sqlite3, stdlib) for packets
carrying `project_authorization` metadata; a DB-read failure yields
`valid == False` → block (fail-closed) for a protected staged file.

### gtkb-sweep-commit interaction (operational analysis)

`gtkb-sweep-commit` bulk-stages protected source/test/config files and commits
through `.githooks/pre-commit` (not `--no-verify`), so this gate fires on every
sweep-commit. Files covered by a live GO packet (step 2) or a terminal-VERIFIED
thread (step 3) pass. Files implemented-but-not-yet-VERIFIED whose GO packet has
since expired (packet TTL ≤ `DEFAULT_EXPIRY_MINUTES` = 120 min) would be BLOCKED.
This is the intended steady state of the owner's chosen hard gate
("VERIFIED-before-commit"), with a documented remedy: re-run
`python scripts/implementation_authorization.py begin --bridge-id <slug>` to
re-mint a live packet before sweeping, or commit only VERIFIED work. The
post-implementation report itself lives under `bridge/` (an ALLOWED surface), so
filing it is never blocked.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge authority; the gate enforces the
  bridge GO/VERIFIED model at commit time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Slice A is itself a
  VERIFIED-gating mechanism; spec-derived tests are required.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the no-bridge-bypass
  protected-behavior the commit gate reinforces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the detector + hook line are
  in-root (`scripts/`, `.githooks/`); no out-of-root path.
- `GOV-RELIABILITY-FAST-LANE-001` — the ALLOW-routine docs/memory/scratch
  exemption.
- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate —
  the authorization-packet model this gate reuses.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start
  Authorization Metadata — the `target_paths` / GO-packet authority.
- (advisory) `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `GOV-ARTIFACT-APPROVAL-001` — cited for the **Slice B** narrative
  formalization follow-on (out of scope here; needs formal-approval packets).

## Prior Deliberations

- `DELIB-20264209` (GO — Implementation Start Authorization Gate): the
  session-local authorization-packet model this gate consumes rather than
  duplicates.
- `DELIB-1656` (GO — secrets-purge-and-commit-enforcement Slice 2): precedent
  for a harness-agnostic `.githooks/pre-commit` deterministic check
  (`scan_secrets.py --staged`); the established pattern Slice A follows.
- `DELIB-2452` (NO-GO — Commit-Scope Bundling Detection Slice 1): prior
  commit-time git-hook detector deliberation; informs failure modes.
- `PROJECT-GTKB-PUSH-GATE` (`bridge/gtkb-push-gate-design-governance-review-001.md`):
  the push-time CI gate; Slice A is the complementary commit-time check.
- A grep for WI-4613 across `bridge/` returns zero matches; keyword scans
  surfaced only adjacent/distinct threads (push-gate, commit-scope bundling,
  secrets-purge) — Slice A is unproposed.
- This proposal is filed as a versioned bridge file in the append-only numbered
  chain (`bridge/gtkb-protected-commit-authorization-gate-001.md`); the
  post-implementation report follows as the next numbered bridge file with no
  deletion or rewrite of prior versions.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20262192` — seed=search; bridge_thread; Bridge thread: gtkb-implementation-start-authorization-gate (10 versions, ORPHAN
- DA: `DELIB-2131` — seed=search; bridge_thread; Bridge thread: gtkb-implementation-start-authorization-gate (10 versions, VERIFI
- DA: `DELIB-20264627` — seed=search; bridge_thread; Loyal Opposition Verification - Project Authorization Spec-Amendment Gate
- DA: `DELIB-20262386` — seed=search; bridge_thread; Bridge thread: gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush (4 ve
- DA: `DELIB-2109` — seed=search; bridge_thread; Bridge thread: gtkb-project-auth-spec-amendment-gate (8 versions, VERIFIED)

## Requirement Sufficiency

Existing requirements are sufficient. The owner AUQ of 2026-06-17 ("Hard git
gate, protected surfaces") fully bounds Slice A, and the implementation-start
gate / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` model establishes the
GO-auth/VERIFIED evidence contract this gate reuses. No new or revised
requirement is needed before implementation.

## Spec-Derived Verification Plan

Spec-to-test mapping — tests in
`platform_tests/scripts/test_check_protected_commit_authorization.py`, mostly via
the git-free `evaluate(root, *, paths=[...])` pure function plus a few tmp-git
integration cases:

- Block without evidence (`PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`):
  protected `scripts/foo.py` with no covering valid packet and no covering
  VERIFIED thread → exit 1; finding names the file + protected class.
- **Dotfile protection (the lstrip-class fix — critical)**:
  protected `.claude/hooks/x.py` and `.codex/gtkb-hooks/y.py` with no evidence →
  exit 1 (block). Without this the suite would be false-green on the exact
  surfaces the gate must protect.
- GO-auth allow: inject a by-bridge packet `valid == True` whose
  `target_path_globs` covers the staged file → exit 0.
- VERIFIED allow (no live packet): fixture a thread at terminal VERIFIED whose
  GO-approved proposal `target_paths` covers the file, with the packet
  TTL-expired → exit 0 (proves the no-TTL VERIFIED path via the `bridge_entry`
  walk, not `approved_files_for_go`).
- Routine ALLOW + short-circuit: stage `memory/MEMORY.md`, `docs/x.md`,
  `bridge/y-001.md`, `.gtkb-state/z.json`,
  `independent-progress-assessments/r.md` → exit 0; assert no packet/bridge read
  attempted.
- Fail-closed-without-blocking-routine: corrupt packet JSON while ONLY
  non-protected files staged → exit 0; same corruption WITH a protected file and
  no other evidence → exit 1.
- git-failure → exit 2 (staged set unknown; abort), not a traceback.
- path-mismatch: packet covers a different path than staged → exit 1.
- expired/superseded packet (`valid == False`) alone → exit 1 unless a VERIFIED
  thread also covers.
- KB extension: stage `groundtruth.db` → classified protected (requires
  evidence).
- `--json` shape + 0/1/2 exit-code contract regression.

Commands (resolved against the GT-KB venv interpreter, which carries ruff):

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py

Expected: all tests pass (incl. the dotfile-protection and VERIFIED-path tests);
ruff check and ruff format --check clean on the changed source and test.

## Acceptance Criteria

1. Committing a staged protected-surface change with no live GO-auth packet
   covering it and no citing VERIFIED thread is BLOCKED (exit 1).
2. A live GO-auth packet OR a terminal-VERIFIED thread covering the file ALLOWS
   the commit.
3. Dot-prefixed protected surfaces (`.claude/hooks/`, `.codex/gtkb-hooks/`,
   `.github/`, `.claude/settings.json`, `.codex/hooks.json`) are correctly
   classified protected (dotfile-correct matching), and `.githooks/` is
   self-protected.
4. Routine docs/memory/bridge/scratch commits are never blocked, and the gate
   short-circuits before touching evidence machinery for them.
5. git-failure → exit 2 (abort), not a crash; the VERIFIED scan is bounded to
   the by-bridge packet set.
6. No double-gating of narrative `.md` surfaces (left to
   `check_narrative_artifact_evidence.py`).
7. ruff check and ruff format --check clean on the changed source and test.

## Risk and Rollback

- Risk: MEDIUM. A commit-time gate changes the commit path. Mitigations: it ALLOWS
  routine commits (short-circuit) and reuses VERIFIED packet/path machinery; the
  dotfile-correct matching + the bounded VERIFIED scan + git-failure→exit-2 are
  the adversarial-review fixes baked in. The sweep-commit interaction is analyzed
  above with a documented remedy.
- Blast radius: one new detector + one `.githooks/pre-commit` line + one test. It
  does NOT modify the shared `is_protected_path` (the WI-4642 lstrip fix is
  separate), `cross_harness_bridge_trigger.py` (WI-4600; it does not import
  `is_protected_path`), `.claude/skills/bridge/helpers/scan_bridge.py` (WI-4618;
  a skill helper, not a commit surface), or `generate_codex_skill_adapters.py`
  (WI-4598) — no conflict with in-flight work.
- Rollback: remove the `.githooks/pre-commit` line and delete the two new files;
  the prior (no commit-time gate) behavior returns. No state/schema change.

## Owner Decisions / Input

Authorized by the owner AskUserQuestion of 2026-06-17 ("Hard git gate, protected
surfaces"), under the active project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` (owner
decision `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`). Two items are
surfaced for owner awareness (no further AUQ required to proceed with Slice A):
(1) the gtkb-sweep-commit interaction above (not-yet-VERIFIED expired-packet
files require a re-minted packet to commit — the intended hard-gate steady
state); (2) a minor design choice — Slice A adopts set B's narrower
PROTECTED_EXACT plus `groundtruth.db` + `.githooks/` rather than
`protected_mutation_guard`'s broader env/Docker exacts; this can be confirmed
during normal Loyal Opposition review. Slice B (the AGENTS.md/`.claude/rules`
directive formalization) is deferred to a separate owner-approved thread with
formal-artifact-approval packets.

## Recommended Commit Type

`feat:` — adds a new commit-time governance gate (a net-new detector + hook
wiring + test).
