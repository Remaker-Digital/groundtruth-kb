author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T10-24-02Z-loyal-opposition-B-511eb3
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition

# LO advisory — WI-4841 is verification-quality; hunk-scoped finalization is not executable by a headless LO worker

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, GOV-WORK-TREE-HYGIENE-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
WIs: WI-4841, WI-5112, WI-5095, WI-5105
Bridge: gtkb-wi4841-managed-skill-adoption-review-scaffold (latest -021 REVISED, left actionable)

## Disposition (headless auto-dispatch, dispatch id 2026-07-10T10-24-02Z-loyal-opposition-B-511eb3)

**Record-and-stop. No bridge verdict filed. `-021` REVISED is intentionally left
as the latest actionable entry so an INTERACTIVE Loyal Opposition session can
finalize it.** This advisory is the ready-to-execute recipe.

I did NOT file a NO-GO because the implementation is verification-quality and a
finalization-only NO-GO (as `-020` already recorded) only re-triggers the
propose→revise treadmill. I did NOT VERIFIED-finalize because the `-021`
hunk-scoped path is not executable by a headless LO worker (see Blocker below).

## Verification result — the WI-4841 implementation IS verification-quality

Re-verified this session against live state:

- Focused + catalog tests: `pytest platform_tests/skills/test_managed_skill_adoption_review_skill.py platform_tests/skills/test_skill_catalog_contract.py` → **13 passed**, 1 benign warning (`asyncio_mode`).
- Applicability preflight (operative `-021`): `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:1636a2e49ad8ed5c04ea46dd795c9031310c1b19e7ff34911e10a1f503d941e5`.
- Clause preflight: exit 0, must_apply 2/2 satisfied, 0 blocking gaps.
- Byte/adapter parity: canonical source SHA `b9c8a7e0f81a893ef98de6b7e28b9b9057d5bb79a3d8b4025d70b1a8998614e9` recorded consistently in `.codex` MANIFEST, `.agent` MANIFEST, and `registry.toml` WI-4841 block.
- `-020` (Claude-B interactive) already found the implementation verification-quality; the sole blocker was finalization commit-isolability.

The `-021` revision correctly answers `-020` by invoking the now-committed
WI-5112 hunk-scoped finalization path (commit `9ce84c60`; further hardened by
WI-5132 at `062b5147`, VERIFIED earlier this same dispatch). The design is sound.

## Blocker — headless LO cannot author the `--hunk-patch` files

`write_verdict.py --finalize-verified --hunk-patch <file>` requires patch files
on disk. Authoring them is blocked for a headless LO worker:

- `GTKB-LO-FILE-SAFETY` PreToolUse Write gate refuses LO writes to non-allow-listed
  paths (e.g. a `.harness-tmp/*.py` generator) with: *"No LO file-safety approval
  packet was found. Reference a valid packet with GTKB_LO_FILE_SAFETY_APPROVAL_PACKET."*
  That packet requires OWNER approval, which a headless auto-dispatch worker cannot
  obtain (it "cannot interactively ask the owner for input").
- The LO Bash mutation gate similarly refuses script/redirect-based generation.

This matches the standing guidance that LO must not hand-roll a commingled-shared-file
VERIFIED finalization; the sanctioned resolution is an interactive LO session (owner
can approve the LO-file-safety packet for the patch files) OR waiting for the foreign
registry/manifest churn to land under its owning WIs. The foreign churn is the
WI-5095-deferred Antigravity registry SHA reconciliation and will not clear imminently.

## Ready-to-execute finalization recipe (for an interactive LO session)

Preconditions re-confirmed live this session:
- WI-5112 hunk-scoped helper is in HEAD; WI-5132 gap-tolerance is in HEAD (`062b5147`).
- `.codex/skills/MANIFEST.json` is **WI-4841-only** (the `formal-artifact-packet-helper` entry above the WI-4841 entry is pre-existing HEAD context, not an addition) → whole-file include is clean.
- Only TWO files carry foreign hunks and need hunk-isolation: `config/agent-control/harness-capability-registry.toml` and `.agent/skills/MANIFEST.json`.

Hunk isolation:
- `registry.toml`: the WI-4841 `[[capabilities]] id = "skill.managed-skill-adoption-review"` block is a clean standalone hunk (git `@@ -2097,3 +2097,40 @@`, a pure EOF append). The ONLY foreign hunk is the `skill.decision-capture` Codex `source_sha256` refresh at `@@ -413,7 +413,7 @@` (`8544a4d4…` → `e2084661…`). Keep the header + the @2097 hunk, drop the @413 hunk (whole-hunk drop preserves counts — no manual recount).
- `.agent/skills/MANIFEST.json`: the WI-4841 `managed-skill-adoption-review` adapter entry (source_sha256 `b9c8a7e0…`) is the LAST array element, added after `skill.verify` (verify source_sha256 `cb2ee93b…` is the anchor). It is commingled in ONE git hunk with a foreign `formal-artifact-packet-helper` addition, plus 8 foreign SHA refreshes (bridge, lo-opportunity-radar, codex-report, decision-capture, harness-parity-review, projects, gtkb-benchmarks, loyal-opposition-hygiene-assessment) and 3 other foreign new adapters (skill-governance-lifecycle, advisory-disposition/-proposal/-intake). Build the WI-4841-only patch mechanically: base = `git show HEAD:.agent/skills/MANIFEST.json`; target = base with ONLY the managed entry appended as the last adapters-array element (anchor on the verify `cb2ee93b…` entry close + array close `  ]`); `git diff --no-index base target`; rewrite `--- `/`+++ ` headers to `a/.agent/skills/MANIFEST.json` / `b/.agent/skills/MANIFEST.json`; validate with `git apply --cached --check` against a `read-tree HEAD` temp index. (git apply is strict → fail-closed on any error.)

Finalization command shape:
```
.claude/skills/verify/helpers/write_verdict.py --slug gtkb-wi4841-managed-skill-adoption-review-scaffold --finalize-verified --no-prepopulate --no-semantic-search --body-file <verdict-body> --commit-message "feat(skill): WI-4841 managed-skill-adoption-review scaffold + Antigravity adapter (hunk-scoped) VERIFIED"
```
--include (whole-file): `.claude/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/managed-skill-adoption-review/SKILL.md`, `.codex/skills/MANIFEST.json`, `.agent/skills/managed-skill-adoption-review/SKILL.md`, `platform_tests/skills/test_managed_skill_adoption_review_skill.py`, `config/agent-control/harness-capability-registry.toml`, `.agent/skills/MANIFEST.json`
--include (untracked predecessor chain — required by `_assert_predecessor_chain_committed`; `-001..-014` and `-016` are already committed, `-015` and `-017..-021` are untracked): `bridge/…-015.md`, `bridge/…-017.md`, `bridge/…-018.md`, `bridge/…-019.md`, `bridge/…-020.md`, `bridge/…-021.md`
--hunk-patch (×2): the registry.toml @2097-only patch and the .agent MANIFEST managed-entry-only patch (registry.toml and .agent MANIFEST are in the --include set but hunk-patched instead of whole-file staged).

Verdict body must satisfy the VERIFIED gates (learned live): first token `VERIFIED`; `bridge_kind: lo_verdict`; full 6-field author block; `Responds to: bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-021.md`; literal `Recommended commit type:`; `## Spec-to-Test Mapping` with a row whose 3rd column is `yes`; `## Commands Executed`; an Applicability Preflight block whose `missing_required_specs:` value is exactly `[]` and which never writes the token `missing_required_specs:` inline in prose; relative paths only in evidence sections.

## Recommendation

Route `-021` to an interactive Loyal Opposition session. That session obtains the
owner-approved `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET` (or the owner authorizes the
hunk-scoped commit by reference), generates the two patches per the recipe above,
and runs the finalization. Expected result: a scoped VERIFIED commit of the seven
WI-4841 implementation paths (registry.toml and .agent MANIFEST hunk-limited) + the
untracked bridge chain + the new `-022` VERIFIED verdict, with zero foreign registry/
manifest hunks committed.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
