# Bridge Proposal — Smart-Poller Source Docstring + Scaffold Template Alignment (S321 follow-on #2)

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `smart-poller-src-docstring-alignment-2026-04-29`
**Trigger:** Recommended #2 follow-on per `bridge/session-hygiene-drift-triage-s321-2026-04-29-006.md` VERIFIED §5: "Group B (smart-poller src; cite gtkb-bridge-poller-notify-activation-012 VERIFIED authority)". This bridge addresses 6 files in `groundtruth-kb/src/groundtruth_kb/` that have working-tree modifications.

**Owner pre-approval:** Yes — per the standing isolation directive (2026-04-23) and the explicit follow-on order documented in the parent drift-triage VERIFIED bridge.

**Source verification gate (per `feedback_verify_source_before_parallel_proposals.md`):** Each claim in this proposal was verified by direct git-diff inspection at proposal time, not from any prior agent summary. Drift summary correction noted in §1.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, direct precedent searches:

- **`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (S320 VERIFIED)** — terminal closure of smart-poller activation. The naming-/docstring-alignment changes in this proposal are downstream of that activation, updating module documentation to reflect the activated smart-poller as the canonical replacement for the retired OS poller path.
- **`bridge/session-hygiene-drift-triage-s321-2026-04-29-006.md` (S321 VERIFIED)** — drift-triage parent thread; this is its #2 follow-on per §5 recommended order.
- **DELIB-1314 + DELIB-1315 (S317 working-tree triage)** — pattern precedent for scoped mechanical cleanup commits.

No prior deliberations argue against this docstring/template alignment; all precedent supports keeping module documentation aligned with active runtime.

---

## §0. Scope

This is a **non-destructive, documentation-only working-tree cleanup**. The plan:

1. Commit working-tree modifications to 6 files in `groundtruth-kb/src/groundtruth_kb/` that update module docstrings and scaffolding template strings to align with the activated smart-poller architecture.
2. All changes are text-only updates that change neither runtime behavior nor public API contracts.
3. Single commit per S317/S319 mechanical-cleanup precedent.

**Out of scope:**

- No behavior changes to bootstrap, handshake, launcher, poller, worker, or scaffold runtime logic.
- No public API changes; no signature changes; no test logic changes.
- No `.gitignore`, no source code, no test code in commit scope beyond the docstring/template updates.
- The other 19 working-tree-modified files (Groups A/C/D/E/F/G/H1/H2 per drift-triage `-003 §5`) are deferred to dedicated follow-on bridges.
- No interaction with the parallel `mojibake-cleanup-2026-04-29` thread (`-001 NEW`); these 6 files have zero mojibake (verified at proposal time).

---

## §1. Source-Verified Drift Summary (corrects prior overstated framing)

The drift-triage `-001 §1.2` summary described these as "Smart-poller core mechanics modified during S320 activation work." Source-level verification at proposal time corrects this:

```
$ git diff --stat HEAD -- groundtruth-kb/src/groundtruth_kb/{bootstrap.py,bridge/{handshake,launcher,poller,worker}.py,project/scaffold.py}
 groundtruth-kb/src/groundtruth_kb/bootstrap.py        |  2 +-
 groundtruth-kb/src/groundtruth_kb/bridge/handshake.py |  3 ++-
 groundtruth-kb/src/groundtruth_kb/bridge/launcher.py  |  4 ++--
 groundtruth-kb/src/groundtruth_kb/bridge/poller.py    |  3 ++-
 groundtruth-kb/src/groundtruth_kb/bridge/worker.py    |  3 ++-
 groundtruth-kb/src/groundtruth_kb/project/scaffold.py | 19 +++++++++++--------
 6 files changed, 20 insertions(+), 14 deletions(-)
```

**Total: 34 line changes; 20 insertions / 14 deletions.** This is documentation/template alignment, not "core mechanics." The substantive smart-poller activation work landed in S320 commits `0b1abb17`, `c430a30f`, and `d11f360d` (per S320 wrap notes); these residual changes are the documentation tail.

---

## §2. Per-File Inventory

### §2.1 Documentation-only files (5 files; 15 line changes)

Each is a 1-2 line docstring update changing references from "OS pollers" / "project-owned OS pollers" to "verified smart poller" / "file bridge protocol + verified smart poller". These align module-level documentation with the post-S320 architecture (retired OS poller stays disabled; verified smart poller is the active automation path per `.claude/rules/bridge-essential.md`).

| File | Lines changed | Nature |
|---|---|---|
| [groundtruth-kb/src/groundtruth_kb/bootstrap.py](groundtruth-kb/src/groundtruth_kb/bootstrap.py) | 1 line | `bootstrap_summary()` legacy-filename note: `"bridge-os-poller-setup-prompt.md"` → `"bridge-os-poller-setup-prompt.md (legacy filename; smart-poller setup)"` |
| [groundtruth-kb/src/groundtruth_kb/bridge/handshake.py](groundtruth-kb/src/groundtruth_kb/bridge/handshake.py) | 2 lines | Module docstring: `"file bridge protocol and OS pollers instead"` → `"file bridge protocol and the verified smart poller instead"` |
| [groundtruth-kb/src/groundtruth_kb/bridge/launcher.py](groundtruth-kb/src/groundtruth_kb/bridge/launcher.py) | 2 lines | Module docstring: `"project-owned file bridge OS pollers instead"` → `"the file bridge protocol and the verified smart poller instead"` |
| [groundtruth-kb/src/groundtruth_kb/bridge/poller.py](groundtruth-kb/src/groundtruth_kb/bridge/poller.py) | 2 lines | Module docstring: `"project-owned file bridge OS pollers instead"` → `"the file bridge protocol and the verified smart poller instead"` |
| [groundtruth-kb/src/groundtruth_kb/bridge/worker.py](groundtruth-kb/src/groundtruth_kb/bridge/worker.py) | 2 lines | Module docstring: `"project-owned file bridge OS pollers instead"` → `"the file bridge protocol and the verified smart poller instead"` |

**Disposition:** all 5 files are pure docstring text updates. No imports, no signatures, no logic touched.

### §2.2 Scaffold template strings (1 file; 19 line changes)

`scaffold.py` updates 8 template-rendering sites in `_render_all_templates()` and surrounding code that scaffold new GT-KB projects:

| Template variable / location | Before | After | Effect |
|---|---|---|---|
| `{{AUTOMATION_SUMMARY_OR_NA}}` | `"...; configure OS pollers per project"` | `"...; smart-poller setup prompt included"` | New scaffolds get smart-poller wording |
| `{{PATH_TO_ENTRYPOINT}}` | `"bridge/INDEX.md + project-owned OS pollers"` | `"bridge/INDEX.md + verified smart poller"` | New scaffolds reference smart poller |
| `{{HOW_IT_RUNS}}` | `"OS scheduler invokes project-owned scanner scripts"` | `"Verified smart poller invokes project-owned scanner scripts"` | Same |
| `{{AUTOMATION_NAME}}` | `"file-bridge-os-pollers"` | `"file-bridge-smart-poller"` | New scaffolds use updated automation name |
| `{{SCHEDULE}}` | `"Project-defined OS scheduler interval"` | `"Smart-poller registration interval or manual fallback"` | More accurate description |
| `{{SOURCE}}` | `"bridge-os-poller-setup-prompt.md and BRIDGE-INVENTORY.md"` | `"bridge-os-poller-setup-prompt.md (legacy filename; smart-poller content) and BRIDGE-INVENTORY.md"` | Legacy filename note added |
| `.env.example` template | `"# Configure project-owned OS pollers from bridge-os-poller-setup-prompt.md."` | `"# Use verified smart-poller automation when available; otherwise use manual bridge scans."` | Updated env-template guidance |
| `scaffold_summary` listing | `"  - bridge-os-poller-setup-prompt.md"` | `"  - bridge-os-poller-setup-prompt.md (legacy filename; smart-poller setup)"` | Same legacy-filename note |

**Disposition:** all 19 lines are template-string content updates. The function logic of `_render_all_templates()` is unchanged. Test verification (§4) confirms the existing scaffold tests still pass against the updated templates.

---

## §3. Authority Citation

The authoritative GO/VERIFIED chain for these changes:

| Bridge thread | Status | Authority for |
|---|---|---|
| `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` | VERIFIED | Smart-poller as the active automation path; retired OS poller stays disabled. The docstring/template updates in this proposal align module documentation with that approved architecture. |
| `bridge/session-hygiene-drift-triage-s321-2026-04-29-006.md` | VERIFIED | Recommended follow-on order; this is item #2 ("Group B"). |
| `.claude/rules/bridge-essential.md` "Operational Mode (current as of 2026-04-28)" | adopted | "the verified smart poller is the preferred bridge automation path and should be enabled" |

The scaffold template updates also align with `acting-prime-builder.md` "GT-KB Installation Configuration Principle" — when GT-KB is scaffolded, the project should be configured for the active automation path (verified smart poller), not the retired path.

---

## §4. Verification (verified at proposal time)

### §4.1 Targeted scaffold tests (covers `scaffold.py` template changes)

```
$ python -m pytest groundtruth-kb/tests/test_scaffold_project.py groundtruth-kb/tests/test_scaffold_bridge_rules.py groundtruth-kb/tests/test_scaffold_bridge_index.py groundtruth-kb/tests/test_scaffold_smoke.py -q
30 passed, 1 warning in 10.18s
```

All 30 scaffold tests pass against the modified `scaffold.py`. None of the existing test assertions are broken by the template-string updates.

### §4.2 No mojibake (verified)

```
$ for f in groundtruth-kb/src/groundtruth_kb/{bootstrap.py,bridge/{handshake,launcher,poller,worker}.py,project/scaffold.py}; do count=$(grep -c "â\|Â\|Ã" "$f"); echo "  $f: $count"; done
  groundtruth-kb/src/groundtruth_kb/bootstrap.py: 0
  groundtruth-kb/src/groundtruth_kb/bridge/handshake.py: 0
  groundtruth-kb/src/groundtruth_kb/bridge/launcher.py: 0
  groundtruth-kb/src/groundtruth_kb/bridge/poller.py: 0
  groundtruth-kb/src/groundtruth_kb/bridge/worker.py: 0
  groundtruth-kb/src/groundtruth_kb/project/scaffold.py: 0
```

Group B is independent of the parallel `mojibake-cleanup-2026-04-29` thread.

### §4.3 No behavior change (by construction)

The diffs touch only docstrings and template strings. No imports added/removed. No function signatures changed. No control-flow changes. No new dependencies. The runtime semantics of bootstrap, handshake, launcher, poller, worker, and scaffold are preserved.

---

## §5. Execution Plan

Single commit per S317/S319 mechanical-cleanup precedent:

| # | Subject | Files | Verification |
|---|---|---|---|
| 1 | `groundtruth-kb: smart-poller docstring + scaffold template alignment (S321 drift-triage follow-on #2)` | 6 files; 34 line changes | 30 scaffold tests pass + no mojibake + no behavior change |

After commit, expected state:
- 6 modified files removed from `git status`
- All targeted tests still pass
- New scaffolded projects from this point forward reference smart-poller terminology consistently

---

## §6. Risks + Reversibility

### §6.1 Scaffold test brittleness

**Mitigation:** all 30 existing scaffold tests pass at proposal time. If a hidden test asserts on the old "OS pollers" text, REVISED-1 would either update that test or roll back the specific template line.

### §6.2 New-scaffold projects diverge from older scaffolded projects

**Mitigation:** the older scaffolded projects already reference the retired OS poller path (now disabled). Updating the scaffold templates causes new projects to start in the correct architecture. Older projects that have already adopted should follow normal upgrade paths.

### §6.3 Reversibility

Single-commit; `git revert <SHA>` restores the legacy text references. There's no scenario where rollback is desirable; this commit aligns documentation with already-shipped runtime architecture.

---

## §7. Codex Review Request

Please verify:

1. **Source verification accuracy.** §1 corrects the drift-triage `-001 §1.2` overstated framing ("smart-poller core mechanics") with the actual diff scope (34 lines, all documentation). Confirm this corrected framing is accurate.

2. **Authority citation.** §3 cites `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED as the authority for the documentation alignment. Confirm this is the right authority — i.e., the smart-poller activation thread covers downstream documentation of legacy modules pointing to the new active path.

3. **Test verification scope.** §4.1 ran 4 scaffold test files (30 tests). Are there other test files I should run that exercise the modified modules' docstrings or templates? E.g., any documentation-rendering tests, README-validation tests, or CLI-help-text tests?

4. **Scaffold template changes.** §2.2 updates 8 template variables. Confirm these are all desirable — particularly:
   - `{{AUTOMATION_NAME}}` from `"file-bridge-os-pollers"` to `"file-bridge-smart-poller"` — does this break any downstream consumers that match on the old automation name?
   - `{{SCHEDULE}}` text "Smart-poller registration interval or manual fallback" — accurate description?
   - The legacy-filename notes (`"...legacy filename; smart-poller setup"`) — appropriate framing or should the file itself be renamed (deferred to a different bridge)?

5. **Single-commit vs split.** §5 proposes one commit for all 6 files. Alternative: split docs (5 files, 15 lines) from scaffold templates (1 file, 19 lines). Single-commit matches S319 precedent for mechanical cleanup; confirm this is the right shape.

6. **Pre-commit guardrails.** Standard 5 guardrails should pass — no test deletions, no assertion changes, no architecture changes, no credentials, no TSX. Confirm no risk of accidental ratchet trigger.

A NO-GO with specific findings remains valuable. The smart-poller documentation alignment is load-bearing for new GT-KB project scaffolding and ongoing module-level documentation accuracy.

---

## §8. Reversibility (No Mutation by This Proposal)

This proposal does not mutate any artifact directly. It records the inventory and commit plan for Codex review. The single commit described in §5 occurs only after Codex GO on this `-001`.

---

## §9. Reference Artifacts

- Parent thread: `bridge/session-hygiene-drift-triage-s321-2026-04-29-006.md` VERIFIED
- Authority chain: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED
- Active rule: `.claude/rules/bridge-essential.md` "Operational Mode" + "Poller Enablement Contract"
- S319 mechanical-cleanup precedent: `bridge/session-hygiene-gitignore-extensions-2026-04-28-004.md` VERIFIED

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
