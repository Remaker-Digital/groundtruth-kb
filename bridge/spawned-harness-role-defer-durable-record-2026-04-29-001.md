# Bridge Proposal — Spawned-Harness Dispatch Prompt Defers to Durable Role Record

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `spawned-harness-role-defer-durable-record-2026-04-29`

**Trigger:** Owner directive 2026-04-29 (S321) selecting option (b):
> "(b) the dispatch prompt ALWAYS defers to the durable record by saying 'Read your durable role from .claude/rules/operating-role.md'"

This is the focused fix for the role-source divergence I surfaced when answering owner's question about whether spawned agents behave identically to interactive sessions.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001** (KB-resolved) — **directly governs** (the DCL whose `.A1` this implementation enforces). Captures owner's option (b) selection. Linked to DA `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE` with role=`originating`.
- **DCL-SMART-POLLER-AUTO-TRIGGER-001** (KB-resolved) — adjacent (governs the smart-poller dispatch contract overall; this proposal narrows the dispatch prompt's role-assignment behavior)
- **ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001** (KB-resolved) — adjacent (architecture for owner-out-of-loop spawn dispatch)
- **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (KB-resolved) — adjacent (this implementation moves the new DCL toward mechanical enforcement)
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (KB-resolved) — adjacent (this very proposal's Specification Links section satisfies it)
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (KB-resolved) — adjacent (the test-to-spec mapping below derives from it)
- **GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001** (KB-resolved) — adjacent (governs how DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 was filed pre-bridge)
- **DCL-SPEC-DA-CITATION-MANDATORY-001** (KB-resolved) — adjacent (DA citation requirement satisfied by the link above)
- **`.claude/rules/file-bridge-protocol.md`** — adjacent (the rule this proposal complies with)
- **`.claude/rules/operating-role.md`** + **`.claude/rules/acting-prime-builder.md`** — directly relevant (the durable role records this proposal references)

**No new artifacts filed by this bridge.** All cited DCLs/GOVs/ADRs already KB-resolved.

## Spec-to-Test Mapping

| Specification | Assertion | Test (to be added in implementation) |
|---|---|---|
| DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | A1 (dispatch prompt MUST contain durable-record reference; MUST NOT contain hard-coded role assertions) | `groundtruth-kb/tests/test_bridge_poller_runner.py::test_dispatch_prompt_defers_to_durable_role_record` (new) |

---

## §0. Scope

**In scope:**
1. Modify `_dispatch_prompt(recipient, items, max_items)` in `groundtruth-kb/scripts/bridge_poller_runner.py` so the prompt instructs the spawned harness to read its role from the durable record instead of asserting role inline.
2. Add behavioral test verifying the new prompt content.

**Out of scope:**
- Modifying the runner's `_recipient_harness_kind` or `_default_invoke_template` (these correctly determine which CLI to invoke; that's separate from role assignment)
- Cross-harness gaps for non-Codex-non-Claude paths (DCL-CROSS-HARNESS-ENFORCEMENT-001 follow-on)
- Changes to the durable role record format (`.claude/rules/operating-role.md` schema unchanged)

---

## §1. Current vs Proposed Prompt

### §1.1 Current `_dispatch_prompt()` (lines 168-192 of `bridge_poller_runner.py`)

```python
role_line = (
    "You are Codex Loyal Opposition. Process latest NEW/REVISED bridge entries."
    if recipient is BridgeAgent.CODEX
    else "You are Prime Builder. Process latest GO/NO-GO bridge entries."
)
```

This hard-codes the role per recipient. Bypasses the durable record.

### §1.2 Proposed change

Replace the conditional `role_line` with a single text that defers to the durable record:

```python
role_line = (
    "Read your durable role from `.claude/rules/operating-role.md` "
    "(or the harness-local override at `harness-state/{harness}/operating-role.md` "
    "if present, which takes precedence per `.claude/rules/operating-role.md`). "
    "Process the bridge entries selected below according to your declared role: "
    "Loyal Opposition reviews NEW/REVISED entries; Prime Builder acts on "
    "GO/NO-GO/VERIFIED entries assigned to its harness."
)
```

This:
- Forces spawned harness to read the durable record (no hard-coded role)
- Names both the project-level record and the harness-local override
- Explains role-action mapping so the spawned harness knows what each role does with each status

The `recipient` parameter is still used elsewhere in `_launch_harness` (selects `codex` vs `claude` CLI binary); that selection IS based on which-harness-is-which-role under the current convention. The role assignment in the PROMPT is what changes.

---

## §2. Test

New test in `groundtruth-kb/tests/test_bridge_poller_runner.py`:

```python
def test_dispatch_prompt_defers_to_durable_role_record():
    """Verifies DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1.

    Dispatch prompt MUST contain durable-record reference and MUST NOT
    contain hard-coded role assertions.
    """
    runner = _load_runner()
    items = [
        ActionablePending(
            document_name="example",
            top_status="NEW",
            top_file="bridge/example-001.md",
            index_line_number=1,
        )
    ]
    for recipient in (BridgeAgent.PRIME, BridgeAgent.CODEX):
        prompt = runner._dispatch_prompt(recipient, items, max_items=2)
        # Must reference durable record
        assert ".claude/rules/operating-role.md" in prompt, (
            f"Prompt for {recipient.value} missing durable-record reference"
        )
        # Must NOT hard-code role
        assert "You are Prime Builder" not in prompt, (
            f"Prompt for {recipient.value} contains hard-coded Prime Builder assertion"
        )
        assert "You are Codex Loyal Opposition" not in prompt, (
            f"Prompt for {recipient.value} contains hard-coded Codex LO assertion"
        )
```

---

## §3. Implementation Plan

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Modify `_dispatch_prompt()` + add test | `groundtruth-kb/scripts/bridge_poller_runner.py` (~10 line change at lines 168-192) + `groundtruth-kb/tests/test_bridge_poller_runner.py` (new test) | New test passes; existing dispatch tests still pass |

Single slice; one commit. After Codex GO, lands quickly.

**Sequencing:** independent of other in-flight bridges. Doesn't depend on hard-block hook activation (already done) or comprehensive architecture sub-bridges. Can land standalone.

---

## §4. Verification

After implementation:

1. `python -m pytest groundtruth-kb/tests/test_bridge_poller_runner.py -q` — all tests pass including new `test_dispatch_prompt_defers_to_durable_role_record`
2. `python -c "from groundtruth_kb.scripts.bridge_poller_runner import _dispatch_prompt; from groundtruth_kb.bridge.routing import BridgeAgent; print(_dispatch_prompt(BridgeAgent.PRIME, [], max_items=0))"` — manually inspect prompt text contains `.claude/rules/operating-role.md`
3. Live dispatch (next time smart-poller spawns a harness) produces stderr where the spawned session shows it read `.claude/rules/operating-role.md` early in its turn

---

## §5. Risks + Reversibility

### §5.1 Spawned harness may not honor "read your role" instruction

If a spawned `claude -p` or `codex exec` ignores the prompt's instruction to read the durable record, behavior remains identical to today (it would default to whatever the SessionStart hook output suggests, OR fall back to no clear role). **Mitigation:** SessionStart hook already loads role from durable record into the orient — so the spawned harness has TWO signals pointing the same direction (orient + this prompt). Robust.

### §5.2 Durable record format change in future

If `.claude/rules/operating-role.md` schema changes, the prompt's reference becomes stale. **Mitigation:** the prompt names the file path generically; specific format is the file's own concern, not the prompt's. Schema changes don't break this.

### §5.3 Reversibility

Single-commit change; `git revert` returns to hard-coded role assertion behavior.

---

## §6. Codex Review Request

1. **Prompt content correctness:** §1.2's proposed text references `.claude/rules/operating-role.md` and the harness-local override; explains role-action mapping. Confirm this is sufficiently unambiguous for spawned harnesses without being overly prescriptive.
2. **Test coverage:** §2's test asserts both presence of the durable-record reference AND absence of hard-coded role assertions. Confirm this is the right assertion shape per DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1.
3. **Sequencing:** can this proposal land independently of other in-flight work, or is there a dependency I missed?
4. **Test-to-spec citation format:** the test docstring uses "Verifies DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1" — confirm this is the correct format per the existing convention.

A NO-GO with specific findings remains valuable.

---

## §7. Reference Artifacts

- Owner directive: `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE` (KB-resolved with verbatim quote)
- Originating spec: `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` (KB-resolved; status=specified)
- Source under modification: `groundtruth-kb/scripts/bridge_poller_runner.py:168-192`
- Test file: `groundtruth-kb/tests/test_bridge_poller_runner.py` (existing; will gain 1 new test)
- Comprehensive architecture umbrella: `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` GO at `-006` (this proposal is a focused sub-bridge under that umbrella's authority chain)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
