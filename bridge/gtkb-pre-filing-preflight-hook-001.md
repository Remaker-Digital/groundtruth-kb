NEW

# Implementation Proposal — GTKB-PRE-FILING-PREFLIGHT-HOOK: Extend bridge-compliance-gate with applicability preflight at write-time

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** PreToolUse hook code update (extends `.claude/hooks/bridge-compliance-gate.py`)
**Companion:** `bridge/gtkb-pre-filing-preflight-rule-001.md` (rule that this hook mechanically enforces)
**Motivation:** S331 incident chain — two consecutive Codex NO-GOs on missing cross-cutting governance spec citations; the rule layer is necessary but voluntary; mechanical enforcement closes the gap.

---

## Background

The S331 incident chain (`bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F1 + `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1) demonstrated that voluntary compliance with the `Specification Links` mandate is unreliable when the cross-cutting governance specs are an *artifact-type axis* the proposer overlooks. The companion rule update bridge thread `bridge/gtkb-pre-filing-preflight-rule-001.md` adds rule-cited soft authority requiring pre-filing preflight; this proposal adds the mechanical enforcement so the rule is not bypassable.

The existing `.claude/hooks/bridge-compliance-gate.py` is a PreToolUse hook on Write+Edit tools. Its current content checks (lines 90–119 of the hook):

- `_has_concrete_spec_links(content)` — verifies a `Specification Links` heading is present + at least one spec-token (`SPEC|GOV|ADR|DCL|PB|REQ-...` or `.claude/rules/...` path) + no placeholder words (`tbd|todo|none|n/a|not applicable|no relevant`).
- `_has_spec_derived_verification(content)` — additionally checks for spec-to-test heading and command evidence (only enforced for `VERIFIED`-status writes).

These are coarse checks. They don't run the applicability matrix from `config/governance/spec-applicability.toml`; they only verify *some* spec is cited. Codex's review (which runs `bridge_applicability_preflight.py` as a separate step) is the only mechanical check that the *required* cross-cutting specs are cited.

This proposal extends the hook to call `scripts/bridge_applicability_preflight.py` at write-time (PreToolUse) and hard-block when `missing_required_specs != []`. The hook becomes the same gate Codex runs — preventing the proposal from being filed in a state Codex would NO-GO.

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives under `bridge/`; the hook implements bridge-time enforcement consistent with the live INDEX authority model.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this proposal IS the mechanical enforcement of this DCL at write-time; the new hook check directly operationalizes the DCL.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: the Specification-Derived Test Plan section below maps every spec clause to a concrete test command.

Topic-specific governance for this work:

- `.claude/hooks/bridge-compliance-gate.py` — The hook this proposal extends. Currently 287 lines; the extension adds approximately 30–40 lines (subprocess invocation of preflight + JSON parsing + decision emission).
- `scripts/bridge_applicability_preflight.py` — The script the hook will invoke as a subprocess. Existing CLI: `--bridge-id <id>` argument; outputs the applicability packet to stdout. The hook will parse stdout for `preflight_passed: <bool>` and `missing_required_specs: [...]`.
- `config/governance/spec-applicability.toml` — The trigger registry the script consults. Not modified by this proposal.
- `.claude/rules/file-bridge-protocol.md` — Will be extended by companion bridge thread `bridge/gtkb-pre-filing-preflight-rule-001.md`; this hook upgrade mechanically enforces that rule.
- `.claude/settings.json` — Hook registration entry; not modified by this proposal (existing PreToolUse registration covers the new check).
- `bridge/gtkb-pre-filing-preflight-rule-001.md` — Companion rule update bridge thread; should be filed and ideally GO'd before the hook upgrade lands so the rule is in place when the mechanical enforcement activates.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Owner directive: repetitive procedural work (citing cross-cutting specs by hand) is a defect; deterministic plumbing belongs in services, not in sessions. This proposal is a direct application.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — Triggered by mentions of `.claude/rules/file-bridge-protocol.md` + `Agent Red` references in the motivating-incident bridges. Compliance: this hook upgrade operates entirely within GT-KB platform hook corpus and does not move work into or out of `applications/Agent_Red/`. The hook applies uniformly to bridge proposals regardless of whether they originate from platform or adopter work.
- `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` — Motivating NO-GO F1 evidence.
- `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` — Motivating NO-GO F1 evidence.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Decisions preserved as durable artifacts. Compliance: the hook code itself is a durable artifact in the platform tree.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability. Compliance: this proposal cites the rule it enforces, the script it invokes, and the two motivating NO-GOs.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states. Compliance: the hook lifecycle is git-version-controlled; once GO'd and committed, it is active until owner-superseded.

Bridge bandwidth note: `DCL-CROSS-CUTTING-REQUIREMENTS-REGISTRY-001` (S330 spawn-queue companion) overlaps in spirit with this proposal — both move cross-cutting governance from voluntary to mechanical. They should evolve together; the registry handles arbitrary cross-cutting requirements registered as TOML entries, while this hook handles the bridge-proposal-specific applicability check that's already encoded in `spec-applicability.toml`. Future work may merge the two paths (e.g., the hook delegates to the registry's runtime); that's out of scope for this proposal.

The proposed tests in the Test Plan section derive from these linked specs as follows: `GOV-FILE-BRIDGE-AUTHORITY-001` → T-bridge-1; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` → T-spec-1 (preflight on this proposal); `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → T-spec-2; hook behavior → T-hook-1 (deliberately-incomplete fixture proposal blocked) + T-hook-2 (compliant proposal allowed) + T-hook-3 (preflight subprocess fails gracefully).

## Prior Deliberations

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | owner_conversation | informational | Justifies moving voluntary self-checks into mechanical services |
| `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` | owner_conversation | owner_decision | Source of the family of NO-GOs that motivated this hook upgrade |
| `DELIB-S330-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT` | owner_conversation | owner_decision | S330 owner decision establishing mechanical enforcement as the model for cross-cutting requirements; this hook upgrade is consistent with that model |
| Bridge thread DELIBs at `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` and `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` | bridge_thread | no_go | The two consecutive NO-GO incidents that motivated this hook upgrade |

No prior deliberation rejects mechanical enforcement of bridge applicability; the rule corpus assumes Codex review will catch defects, but Codex review is feedback after-the-fact.

## Goal

Extend `.claude/hooks/bridge-compliance-gate.py` to invoke `scripts/bridge_applicability_preflight.py` as a subprocess when a bridge file is being written, parse the result, and hard-block the write when `missing_required_specs != []`. The hook becomes the same gate Codex runs at review time — preventing self-defective proposals from reaching INDEX.

## Proposed Hook Behavior

Add a new function `_has_clean_applicability_preflight(file_path: str, bridge_id: str) -> tuple[bool, str]` to `.claude/hooks/bridge-compliance-gate.py`:

- Invokes `subprocess.run(["python", "scripts/bridge_applicability_preflight.py", "--bridge-id", bridge_id], capture_output=True)`.
- On exit code 0: parse stdout for `preflight_passed:` line. If `true` and `missing_required_specs: []`, return `(True, "")`. Otherwise return `(False, <missing-specs-string>)`.
- On exit code != 0 (preflight script error): return `(True, "")` (graceful degradation — don't block on hook bug; emit a stderr warning).
- Cache the result by file_path + content hash for the duration of the hook invocation (avoid re-running preflight on the same content).

Modify the existing main flow:

- After the existing `_has_concrete_spec_links(content)` check passes, additionally call `_has_clean_applicability_preflight(file_path, bridge_id)`.
- Extract `bridge_id` from `file_path`: strip `bridge/` prefix and `-NNN.md` suffix.
- If the new check fails, emit `deny` with reason: `"[Governance] Pre-filing applicability preflight failed: missing_required_specs=[{specs}]. Run python scripts/bridge_applicability_preflight.py --bridge-id {bridge_id} for full output. (Hard-block per DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 mechanical enforcement.)"`
- If the bridge file's INDEX entry doesn't yet exist (catch-22), the preflight script returns an `ERR_NO_INDEX_ENTRY:` error; treat this as a soft-pass (allow the write so the INDEX can be created), but emit a stderr warning prompting the next write to re-check.

Pseudo-diff (simplified):

```python
# After existing _has_concrete_spec_links check passes:

if _is_bridge_markdown_file(file_path) and content:
    bridge_id = _extract_bridge_id_from_path(file_path)
    preflight_ok, error_msg = _has_clean_applicability_preflight(file_path, bridge_id)
    if not preflight_ok:
        emit_deny(
            "PreToolUse",
            f"[Governance] Pre-filing applicability preflight failed: {error_msg}. "
            f"Run python scripts/bridge_applicability_preflight.py --bridge-id {bridge_id} "
            f"for full output. (Hard-block per DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 "
            f"mechanical enforcement.)",
        )
        sys.exit(0)
```

The exact code change will be in the post-impl REPORT phase; this proposal is the gate.

## Specification-Derived Test Plan

| Test ID | Spec coverage | Procedure | Expected result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-pre-filing-preflight-hook" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-pre-filing-preflight-hook` | `preflight_passed: true`, `missing_required_specs: []` |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | post-impl REPORT contains Specification Links + spec-to-test mapping + executed commands + observed results | Codex VERIFIED contingent |
| **T-hook-1** | hook negative test | Write a bridge file with missing required spec; expect hook hard-block | Hook emits `deny` with `[Governance] Pre-filing applicability preflight failed:` |
| **T-hook-2** | hook positive test | Write a bridge file with all required specs cited; expect hook allow | Hook emits empty `{}` (pass-through) |
| **T-hook-3** | hook graceful degradation | Simulate preflight script error (e.g., missing file); expect hook allow with stderr warning | Hook emits empty `{}`; stderr contains a warning string |
| **T-hook-4** | hook self-test passes | `python .claude/hooks/bridge-compliance-gate.py --self-test` | exit 0; output indicates new check is active |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, and `python .claude/hooks/...` invocations to satisfy the spec-derived-testing-mandatory regex.

## Acceptance Criteria

- [ ] Codex GO on this proposal
- [ ] Preflight passes (T-spec-1)
- [ ] Companion rule update bridge thread `bridge/gtkb-pre-filing-preflight-rule-001.md` reaches GO before this hook upgrade is implemented (so the rule is in place when the hook activates)

VERIFIED when:

- [ ] `.claude/hooks/bridge-compliance-gate.py` contains the new `_has_clean_applicability_preflight` function and is wired into the main flow
- [ ] Hook self-test passes (T-hook-4)
- [ ] All hook tests T-hook-1 through T-hook-3 pass
- [ ] Codex VERIFIED on the post-impl REPORT
- [ ] No regression in existing hook checks (compliance-gate, formal-artifact-approval-gate, etc.)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Preflight subprocess slow → hook latency for every bridge file write | Low | Medium | Preflight already runs in <1s; cache result by content hash |
| Preflight script unavailable / crashed → hook blocks all bridge writes | Low | High | Graceful-degradation path: on subprocess error, allow with stderr warning (T-hook-3) |
| Hook hard-blocks legitimate writes during refactor of `spec-applicability.toml` | Low | Medium | Owner override: temporarily disable hook by toggling its registration in `.claude/settings.json` |
| Rule update lands AFTER hook upgrade → mechanical enforcement without rule documentation | Low | Low | Sequencing: rule bridge thread reaches GO before this hook upgrade is implemented |
| Catch-22 case (INDEX entry doesn't yet exist) | Medium | Low | Soft-pass on `ERR_NO_INDEX_ENTRY:` (T-hook-3 covers) |

Rollback: `git revert` of the hook-file edit; existing checks (compliance-gate header presence, formal-artifact-approval-gate) remain operational.

## Open Questions

| ID | Question | Default if unanswered |
|----|----------|-----------------------|
| **OQ-1** | Should the hook also enforce *advisory* specs (i.e., block when `missing_advisory_specs != []`)? | Default: NO. Advisory specs are advisory; only required specs are blocking. Owner can override at GO time. |
| **OQ-2** | Should the hook cache preflight results across bridge writes within a session? | Default: NO. Each write is independent; caching introduces consistency risk. Re-run cost is <1s. |
| **OQ-3** | When the new check fails, should the hook emit `ask` (prompt owner to confirm override) or `deny` (hard-block, no override)? | Default: `deny` (hard-block). The whole point is mechanical enforcement; owner override should be an explicit hook-disable, not a per-write prompt. |

## Out of Scope

- Rule update (separate companion bridge thread).
- Memory record (already written in S331).
- Updates to `config/governance/spec-applicability.toml` (separate scope).
- Replacement of the existing `_has_concrete_spec_links` check (this proposal adds a new check; the existing one stays).
- Integration with `DCL-CROSS-CUTTING-REQUIREMENTS-REGISTRY-001` (S330 spawn-queue companion; out of scope here; future work may merge).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- Modifies `.claude/hooks/bridge-compliance-gate.py` (a platform hook file at GT-KB root).
- Does not touch `applications/Agent_Red/`.

## Provenance

| Source | Reference |
|--------|-----------|
| Owner direction | S331 AskUserQuestion: "All three: memory record + rule update + hook upgrade (Recommended)" |
| Motivating incidents | `bridge/gtkb-isolation-018-agent-red-file-migration-002.md` F1; `bridge/gtkb-isolation-018-pending-migration-waiver-002.md` F1 |
| Memory record | `memory/feedback_preflight_before_filing_bridge_proposals.md` |
| Companion bridge thread | `bridge/gtkb-pre-filing-preflight-rule-001.md` (rule update) |
| Spec-applicability config | `config/governance/spec-applicability.toml` |
| Preflight script | `scripts/bridge_applicability_preflight.py` |
| Existing hook | `.claude/hooks/bridge-compliance-gate.py` |
| Adjacent S330 work | `DELIB-S330-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT`; `DCL-CROSS-CUTTING-REQUIREMENTS-REGISTRY-001` (companion S330 thread; not blocking) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
