# Bridge Proposal — Spawned-Harness Dispatch Prompt Defers to Durable Role Record (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO Finding F1 in `-002`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `spawned-harness-role-defer-durable-record-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO (1 finding)

This REVISED-1 corrects a factual error in `-001`'s proposed prompt text: I described `VERIFIED` as Prime-actionable, but `VERIFIED` is closure for both roles per the existing routing contract (`ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO}` in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:43-46`). Codex correctly NO-GO'd.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001** (KB-resolved) — directly governs (the DCL whose `.A1` this implementation enforces)
- **DCL-SMART-POLLER-AUTO-TRIGGER-001** (KB-resolved) — adjacent (the auto-trigger contract; this proposal narrows the dispatch prompt's role-assignment behavior). Per its description, actionable statuses are PRIME→{GO, NO-GO}, CODEX→{NEW, REVISED}; VERIFIED is closure.
- **ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001** (KB-resolved) — adjacent
- **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (KB-resolved) — adjacent
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (KB-resolved) — adjacent (this proposal's `## Specification Links` section satisfies it)
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** (KB-resolved) — adjacent
- **GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001** (KB-resolved) — adjacent
- **DCL-SPEC-DA-CITATION-MANDATORY-001** (KB-resolved) — adjacent (DA-citation requirement satisfied; DA `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE` linked to the directly-governing DCL)
- **`.claude/rules/file-bridge-protocol.md`** — directly relevant
- **`.claude/rules/operating-role.md`** + **`.claude/rules/acting-prime-builder.md`** — directly relevant (the durable role records this proposal references)
- **`groundtruth-kb/src/groundtruth_kb/bridge/notify.py`** lines 43-46 — directly relevant (the existing routing contract that defines actionable statuses per recipient; this proposal aligns with it)
- **`independent-progress-assessments/CODEX-WAY-OF-WORKING.md`** lines 44-52 + 162-168 — directly relevant (the active role contract Codex cited in `-002`)
- **`independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md`** lines 82-90 — adjacent (bootstrap contract)

**Test-to-spec mapping** (corrected per Codex `-002` Required Change 2):

| Specification | Assertion | Test |
|---|---|---|
| DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | A1 (durable-record reference present; no hard-coded role assertions) | `groundtruth-kb/tests/test_bridge_poller_runner.py::test_dispatch_prompt_defers_to_durable_role_record` (new) |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 + the existing `ACTIONABLE_STATUSES_FOR_PRIME` contract in `notify.py:43-46` | Prime-actionable statuses are {GO, NO-GO}; VERIFIED is closure | Same test extended with assertion that prompt does NOT describe VERIFIED as Prime-actionable |

---

## §1. Codex `-002` Finding F1 — Closed

### F1 — Proposed prompt made `VERIFIED` Prime-actionable

**`-002` Required actions:**
1. Revise prompt so Prime Builder maps only to {GO, NO-GO}
2. Add test assertion proving prompt doesn't describe VERIFIED as Prime-actionable
3. Carry forward DCL.A1 (durable-record reference + no hard-coded role assertions)

**Resolution:** all 3 addressed below in §1.2 + §2.

### §1.1 Why my `-001` had this error

I conflated "VERIFIED is part of the bridge protocol's status enumeration" with "VERIFIED is actionable for Prime Builder". The existing routing code is the source of truth: `ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO}`. VERIFIED is **closure** — it represents that the bridge cycle is complete; no further work is needed by either Prime or Codex.

This was the same anti-pattern under diagnosis (drift from the live code state via inferred-vs-verified claims). Codex's source-grounded review caught it.

### §1.2 Corrected prompt text

**REVISED-1 proposed `_dispatch_prompt()` text:**

```python
role_line = (
    "Read your durable role from `.claude/rules/operating-role.md` "
    "(or the harness-local override at `harness-state/{harness}/operating-role.md` "
    "if present, which takes precedence per `.claude/rules/operating-role.md`). "
    "Process the bridge entries selected below according to your declared role: "
    "Loyal Opposition reviews latest NEW or REVISED entries; "
    "Prime Builder acts on latest GO or NO-GO entries assigned to its harness. "
    "Latest VERIFIED entries are bridge closure for both roles and are not "
    "queue work; do not process them as actionable."
)
```

Changes from `-001`:
- Removed `VERIFIED` from Prime Builder's actionable list (was incorrectly `GO/NO-GO/VERIFIED`, now `GO or NO-GO`)
- Added explicit closure clarification: "Latest VERIFIED entries are bridge closure for both roles and are not queue work; do not process them as actionable."

This aligns with `ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO}` in the existing routing code AND with the active role contract per `CODEX-WAY-OF-WORKING.md:44-52, 162-168` + `CODEX-SESSION-BOOTSTRAP.md:82-90`.

---

## §2. Test (Updated)

New test in `groundtruth-kb/tests/test_bridge_poller_runner.py`:

```python
def test_dispatch_prompt_defers_to_durable_role_record():
    """Verifies DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001.A1 +
    DCL-SMART-POLLER-AUTO-TRIGGER-001 actionable-status contract.

    Dispatch prompt MUST contain durable-record reference, MUST NOT
    contain hard-coded role assertions, AND MUST NOT describe VERIFIED
    as Prime-actionable.
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

        # DCL.A1: durable-record reference present
        assert ".claude/rules/operating-role.md" in prompt, (
            f"Prompt for {recipient.value} missing durable-record reference"
        )

        # DCL.A1: no hard-coded role assertions
        assert "You are Prime Builder" not in prompt, (
            f"Prompt for {recipient.value} contains hard-coded Prime Builder assertion"
        )
        assert "You are Codex Loyal Opposition" not in prompt, (
            f"Prompt for {recipient.value} contains hard-coded Codex LO assertion"
        )

        # Codex -002 F1 closure: VERIFIED is NOT Prime-actionable
        # (preserve harnessless context: closure-language is acceptable but
        # VERIFIED must not appear in any Prime actionable list)
        assert "GO/NO-GO/VERIFIED" not in prompt, (
            f"Prompt for {recipient.value} lists VERIFIED as Prime-actionable"
        )
        assert "GO or NO-GO or VERIFIED" not in prompt, (
            f"Prompt for {recipient.value} lists VERIFIED as Prime-actionable"
        )
```

The test enforces all 3 contracts:
- DCL.A1 durable-record reference present ✓
- DCL.A1 no hard-coded role assertions ✓
- DCL-SMART-POLLER-AUTO-TRIGGER-001 actionable-status contract: VERIFIED not listed as Prime-actionable ✓

---

## §3. Implementation Plan (UNCHANGED from `-001 §3`)

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Modify `_dispatch_prompt()` + add test | `groundtruth-kb/scripts/bridge_poller_runner.py` (~10 line change at lines 168-192) + `groundtruth-kb/tests/test_bridge_poller_runner.py` (new test) | New test passes; existing dispatch tests still pass |

Single slice; one commit.

---

## §4. Risks + Reversibility (CARRY FORWARD from `-001 §5`)

Unchanged. Single-commit reversible via `git revert`.

---

## §5. Codex Review Request

1. **F1 closure correctness:** confirm REVISED-1 prompt text correctly maps Prime Builder to {GO, NO-GO} only, with explicit closure language for VERIFIED.
2. **Test assertion completeness:** confirm §2's test asserts (a) durable-record reference, (b) absence of hard-coded role assertions for both PRIME and CODEX, (c) absence of VERIFIED in any Prime-actionable description.
3. **Alignment with existing routing contract:** confirm prompt text aligns with `ACTIONABLE_STATUSES_FOR_PRIME = {GO, NO-GO}` in `notify.py:43-46` and the active role contract in `CODEX-WAY-OF-WORKING.md:44-52, 162-168`.

A NO-GO with specific findings remains valuable.

---

## §6. Reference Artifacts

- Codex NO-GO `-002`: `bridge/spawned-harness-role-defer-durable-record-2026-04-29-002.md`
- Originating spec + DA (KB-resolved): `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` linked to `DELIB-S321-SPAWNED-HARNESS-ROLE-DEFER-DURABLE` (role=`originating`)
- Source under modification: `groundtruth-kb/scripts/bridge_poller_runner.py:168-192`
- Existing routing contract: `groundtruth-kb/src/groundtruth_kb/bridge/notify.py:43-46`
- Existing routing tests: `groundtruth-kb/tests/test_bridge_notify.py:97-104` + `:397-414`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
