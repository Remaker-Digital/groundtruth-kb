# Implementation Bridge: DA Governance Completeness (REVISED-5, focused delta vs -009)

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7, 1M context)
**Date:** 2026-04-17
**Target repo:** `groundtruth-kb`

**Revision basis:** addresses the two findings in Codex NO-GO
`bridge/gtkb-da-governance-completeness-implementation-010.md`:

1. **High** — Upgrade/doctor registration enforcement is still
   underspecified for non-`PreToolUse` events. The current
   `_plan_settings_registration` filters to `PreToolUse` only
   (`upgrade.py:252-258`) and `_execute_register_hook` is hardcoded to
   append into `hooks["PreToolUse"]` (`upgrade.py:432-450`). REVISED-4 did
   not specify the event-aware action contract, the per-event apply
   semantics, or the lifecycle profile values for the four new
   `settings-hook-registration` records. **Resolved in §A and §B below.**
2. **Medium** — Bypass `content` format mismatch: REVISED-4 §5.5.1 calls
   it "JSON-in-markdown block" but the tests in §5.5.3 call
   `json.loads(content)` directly. **Resolved in §C below.**

**Supersedes `-009`.** Preserves all content accepted by `-008` and
`-010`'s non-blocking notes:

- Phase 0 DELIB-0819 sequencing (`-009` §3) — unchanged.
- Transcript queue as pre-insert dry-run artifact (`-009` §5.6) — unchanged.
- Canonical `owner_conversation` source_ref grammar (`-009` §5.5.1) — unchanged.
- A3 HYBRID branch + A5 CI-result deterministic file (`-009` §5.9) — unchanged.
- Bypass DELIB stored without a `metadata` column; discriminators carried
  by `change_reason` + `title` + structured payload in `content` (`-009`
  §5.5.1) — **§C clarifies the storage shape of `content`; the
  discriminator contract is unchanged.**
- 5 file records + 4 settings-hook-registration records (`-009` §5.11);
  registry placement table — unchanged.
- 8 specs in MemBase (`-009` §5.1), test inventory (`-009` §6), post-impl
  report contract (`-009` §7), rollback (`-009` §8).

This bridge rewrites only:

- §5.5.1 sub-bullet on `content` shape and §5.5.3 test wording (per §C).
- §5.11 — adds **§A** (lifecycle profile values for the 4 new
  settings-hook-registration records) and **§B** (event-aware upgrade plan
  + apply contract + tests + doctor contract + tests).
- §6 — test counts updated to reflect §B.
- §7 — post-impl evidence updated to include event-aware plan/apply
  output and event-aware doctor output.

All other §-numbered content from `-009` is preserved verbatim.

**Scope-bridge references:**
- `bridge/gtkb-da-governance-completeness-003.md` (REVISED scope proposal)
- `bridge/gtkb-da-governance-completeness-004.md` (Codex scope GO with 7 conditions)

**Authorization chain:** Scope GO at `-004` authorizes filing this
implementation bridge. Per `.claude/rules/codex-review-gate.md`, no GT-KB
source, doc, hook, template, script, DB, or managed-artifact mutation
may begin until Codex GOs this `-011`.

---

## 1. Summary of Revisions vs `-009`

| Origin | Finding | Where discharged in `-011` |
|--------|---------|---------------------------|
| `-010` #1 (High) — non-PreToolUse upgrade/doctor enforcement underspecified | Lifecycle profile values for 4 new settings-hook-registration records were missing | §A — explicit `initial_profiles` / `managed_profiles` / `doctor_required_profiles` triples for all 4 records, matching the C1-scoped enforcement intent (managed by upgrade; surfaced by doctor) |
| `-010` #1 (High) — non-PreToolUse upgrade/doctor enforcement underspecified | Event-aware upgrade plan/apply contract missing | §B.1 — `register-hook` action gets a new `event` field (back-compatible default `PreToolUse`); `_plan_settings_registration` removes the `event != "PreToolUse"` skip and emits one action per (event, hook_filename) pair filtered by `managed_profiles`; `_execute_register_hook` inserts into `hooks[action.event]`, preserving every existing entry. |
| `-010` #1 (High) — non-PreToolUse upgrade/doctor enforcement underspecified | Per-event tests missing | §B.2 — 9 new test cases in `tests/test_upgrade.py` covering planning + apply per event (UserPromptSubmit, PostToolUse, PreToolUse), idempotence, ordering preservation, malformed-shape defense |
| `-010` #1 (High) — non-PreToolUse upgrade/doctor enforcement underspecified | Doctor contract for non-PreToolUse missing | §B.3 — generalizes the scanner-safe-writer composite-check pattern to any registry-`doctor_required_profiles`-included settings-hook-registration record (no event hardcoding). +5 doctor test cases. |
| `-010` #2 (Medium) — bypass `content` raw-JSON vs JSON-in-Markdown mismatch | Format ambiguity | §C — pin `content` as **raw JSON** (one canonical shape). `-009` §5.5.1 phrase "JSON-in-markdown block" is corrected to "raw JSON document". `-009` §5.5.3 tests' `json.loads(content)` calls become correct by construction. No new helper required. |
| `-010` non-blocking — `-008` metadata blocker resolved | accepted | unchanged |
| `-010` non-blocking — transcript queue as pre-insert dry-run artifact | accepted | unchanged |
| `-010` non-blocking — 4 named settings-hook-registration records + relative placement | accepted directionally | preserved verbatim from `-009` §5.11 placement table; §A adds the lifecycle profile axes that were missing |

All previously accepted content is retained verbatim unless noted.

---

## 2. Discharge of 7 Required Implementation Conditions (from scope `-004`)

*(Unchanged from `-009` §2 — all 7 conditions still discharged in the
same locations. §B and §A strengthen condition #4 — the upgrade/doctor
enforcement extension promised there now has an executable contract.)*

---

## 3. Phase 0 — Owner Decision Gate (satisfied)

*(Unchanged from `-009` §3.)* DELIB-0819 already in place.

---

## 4. Hard Sequencing Gates

*(Unchanged from `-009` §4.)*

---

## 5. Per-Phase Execution Plan

### 5.1 Phase 1 — Spec recording

*(Unchanged from `-009` §5.1.)*

### 5.2 Phase 2 — Redaction routing invariant + residual re-scan

*(Unchanged from `-009` §5.2.)*

### 5.3 Phase 3 — Source-ref validation (warn-only v1)

*(Unchanged from `-009` §5.3.)*

### 5.4 Phase 4 — LO-report coverage closure + retroactive backfill

*(Unchanged from `-009` §5.4.)*

### 5.5 Phase 5 — Preflight hook infrastructure (Q3 = env var + content marker)

#### 5.5.1 Q3 contract — bypass DELIB storage

*(Unchanged from `-009` §5.5.1 except for the single sub-bullet on `content` storage.)*

**Bypass logging — `content` storage shape (REVISED per `-010` #2):**

The `content` column stores a **raw JSON document** (UTF-8 string,
parseable by a single `json.loads(content)` call) with this exact key
set:

```json
{
  "reason": "<reason string as supplied by env value or marker capture group>",
  "tier": "env" | "marker",
  "file_path": "<absolute or repo-relative target path from the tool input>",
  "session_id": "<session id>",
  "turn_id": "<turn id>",
  "timestamp": "<UTC ISO-8601 timestamp matching the source_ref minute prefix>"
}
```

Rationale for **raw JSON over JSON-in-markdown**: (a) zero ambiguity;
(b) zero new helper code path (no fenced-block extractor needed); (c)
matches the test contract in §5.5.3 (`json.loads(content)`); (d)
deliberation `content` is opaque text in the schema — no
producer/consumer in the codebase parses it as Markdown today;
(e) human readability is preserved (JSON pretty-prints); (f) round-trips
losslessly through ChromaDB indexing because the chunker treats `content`
as text either way.

**Backwards-compat note:** if at some future point we want a Markdown
wrapper for human-friendly DA viewers, that would be an additive
producer-side change with a fenced-block extractor on the consumer side
— out of scope for this bridge.

All other content of `-009` §5.5.1 is preserved unchanged: the column
list (`id`, `source_type`, `source_ref`, `title`, `summary`, `content`,
`session_id`, `outcome`, `changed_by`, `change_reason`), the canonical
`source_ref` grammar, the discriminator-layering table, the
stale/abuse protections, the failure behavior.

#### 5.5.2 `delib-preflight-gate.py` logic

*(Unchanged from `-009` §5.5.2.)*

#### 5.5.3 Tests (`tests/test_delib_preflight_gate.py`) — 23 total

*(Unchanged from `-009` §5.5.3 in count and structure.)*

**Wording correction per `-010` #2:** the bullets in cases 8 and 11 that
read `json.loads(content)["tier"] == "..."` are now correct by
construction because §5.5.1 (above) pins `content` as a raw JSON
document. No fenced-block extraction helper is invoked. Tests literally
call `json.loads(content)["tier"]` and `json.loads(content)["reason"]`.

**Explicit NON-assertion (preserved):** none of these tests reference a
`metadata` column, `metadata` kwarg, or `metadata->>` JSON extraction
operator.

### 5.6 Phase 6 — Transcript extractor (Q1 = HYBRID)

*(Unchanged from `-009` §5.6.)*

### 5.7 Phase 7 — Owner-decision capture hook + GOV-09 capture

*(Unchanged from `-009` §5.7.)*

### 5.8 Phase 8 — Backfill framework generalization

*(Unchanged from `-009` §5.8.)*

### 5.9 Phase 9 — Session wrap gate

*(Unchanged from `-009` §5.9 including A2 `change_reason` query shape.)*

### 5.10 Phase 10 — Dogfooding

*(Unchanged from `-009` §5.10.)*

### 5.11 Consolidated final hook / scaffold / managed-artifact surface

The **scaffold path**, **two-class registration requirement** (`hook` +
`settings-hook-registration`), the **5 file records** (with their
profile triples already concrete in `-009`), and the **registry
placement** of the 4 new settings-hook-registration records relative to
existing rows are all unchanged from `-009` §5.11.

What changes here is two-fold:

- **§A** specifies the missing `initial_profiles`, `managed_profiles`,
  `doctor_required_profiles` triples for the 4 new
  `settings-hook-registration` records.
- **§B** specifies the event-aware upgrade plan + apply contract and
  the doctor contract that consume those triples.

#### §A — Lifecycle profile values for the 4 new settings-hook-registration records

Each new `settings-hook-registration` record carries these axes (in
addition to `class`, `id`, `event`, `hook_filename`,
`target_settings_path`, `ownership`, `upgrade_policy`,
`adopter_divergence_policy` shown in `-009` §5.11):

| Record id | event | hook_filename | initial_profiles | managed_profiles | doctor_required_profiles |
|-----------|-------|---------------|-------------------|-------------------|----------------------------|
| `settings.hook.turn-marker.userpromptsubmit` | UserPromptSubmit | `turn-marker.py` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` |
| `settings.hook.gov09-capture.userpromptsubmit` | UserPromptSubmit | `gov09-capture.py` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` |
| `settings.hook.owner-decision-capture.posttooluse` | PostToolUse | `owner-decision-capture.py` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` |
| `settings.hook.delib-preflight-gate.pretooluse` | PreToolUse | `delib-preflight-gate.py` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` | `["dual-agent", "dual-agent-webapp"]` |

**Other axes (constant across all 4):**
- `target_settings_path = ".claude/settings.json"`
- `ownership = "gt-kb-managed"`
- `upgrade_policy = "structured-merge"`
- `adopter_divergence_policy = "warn"`

**Cross-reference against existing rows:** these triples deliberately
**diverge from the existing 11 settings-hook-registration records** —
all 11 of which (verified against `templates/managed-artifacts.toml`
lines 374-503) have `managed_profiles = []` and
`doctor_required_profiles = []`, except `scanner-safe-writer.pretooluse`
which has `managed_profiles = ["dual-agent", "dual-agent-webapp"]` and
`doctor_required_profiles = []`. The 4 new records are the **first
settings-hook-registration rows that opt in to both upgrade enforcement
and doctor enforcement**, which is the point of the §B contract — the
existing 11 rows remain scaffold-only and are unaffected by the upgrade
generalization, because `_plan_settings_registration` filters by the
record's own `managed_profiles` axis (§B.1).

**Why `managed_profiles ≠ []` AND `doctor_required_profiles ≠ []`:**
DELIB-0720 governance-completeness scope explicitly requires that
existing adopter projects retrofit into the final event matrix — not
just fresh scaffolds. `managed_profiles` populates the upgrade plan;
`doctor_required_profiles` lights up the doctor warning when the
registration is absent on disk; both together close the gap that `-010`
identified.

#### §B — Event-aware upgrade plan + apply + doctor contract

##### §B.1 Plan/apply contract — code-level changes

**File: `src/groundtruth_kb/project/upgrade.py`**

Add an optional `event` field to `UpgradeAction` payloads, defaulting
to `"PreToolUse"` for backward compatibility with any caller that does
not set it. Concrete shape:

```python
@dataclass
class UpgradeAction:
    file: str
    action: str
    reason: str
    payload: str | None = None
    event: str = "PreToolUse"  # NEW — defaults preserve back-compat for
                                # the (currently sole) PreToolUse caller.
```

Modify `_plan_settings_registration(target, profile_name)` (currently
`upgrade.py:191-270`):

1. **Remove** the `if registration.event != "PreToolUse": continue`
   guard (currently `upgrade.py:252-258`).
2. **Replace** the `registered_commands: set[str]` accumulator that
   reads only `hooks["PreToolUse"]` (currently `upgrade.py:233-248`)
   with a per-event registered-commands map:
   ```python
   registered_by_event: dict[str, set[str]] = {}
   for event_name, raw_event_list in hooks_dict.items():
       if not isinstance(raw_event_list, list):
           continue
       cmds: set[str] = set()
       for entry in raw_event_list:
           if not isinstance(entry, dict):
               continue
           entry_hooks = entry.get("hooks", [])
           if not isinstance(entry_hooks, list):
               continue
           for h in entry_hooks:
               if not isinstance(h, dict):
                   continue
               cmd = h.get("command", "")
               if isinstance(cmd, str):
                   cmds.add(cmd)
       registered_by_event[event_name] = cmds
   ```
3. **Replace** the action-emit loop with one that filters per-record by
   the record's own `managed_profiles` axis (already enforced by the
   call to `_managed_settings_registrations(profile_name)`, which uses
   `artifacts_for_upgrade(profile_name)` — `managed_registry.py:394-403`)
   and emits an `event`-tagged action only when the marker is missing
   from `hooks[registration.event]`:
   ```python
   for registration in _managed_settings_registrations(profile_name):
       marker = f"python .claude/hooks/{registration.hook_filename}"
       existing = registered_by_event.get(registration.event, set())
       if any(marker in cmd for cmd in existing):
           continue
       actions.append(
           UpgradeAction(
               file=".claude/settings.json",
               action="register-hook",
               reason=f"Register {registration.hook_filename} as {registration.event} hook",
               payload=registration.hook_filename,
               event=registration.event,
           )
       )
   ```

Modify `_execute_register_hook(target, action)` (currently
`upgrade.py:403-455`):

1. **Replace** the hardcoded `"PreToolUse"` reads/writes (currently
   `upgrade.py:432-450`) with `action.event`:
   ```python
   raw_event_list = hooks_dict.get(action.event)
   if not isinstance(raw_event_list, list):
       hooks_dict[action.event] = []
   event_list = hooks_dict[action.event]

   marker = f"python .claude/hooks/{action.payload}"
   for entry in event_list:
       if not isinstance(entry, dict):
           continue
       entry_hooks = entry.get("hooks", [])
       if not isinstance(entry_hooks, list):
           continue
       for h in entry_hooks:
           if isinstance(h, dict):
               cmd = h.get("command", "")
               if isinstance(cmd, str) and marker in cmd:
                   return f"SKIPPED {action.file} — {action.payload} already registered ({action.event})"

   event_list.append({"hooks": [{"type": "command", "command": marker}]})
   ```
2. **Status string:** include the event name in the success and skip
   messages so dry-run output is unambiguous:
   `REGISTERED {action.payload} in {action.file} ({action.event})` /
   `SKIPPED ... already registered ({action.event})`.
3. **Preservation guarantee:** existing entries in
   `hooks[action.event]` are not mutated. Existing entries in **other
   events** (the events not targeted by this action) are not read or
   touched — the function only reads the targeted event's list.
4. **Order semantics within an event:** when multiple `register-hook`
   actions for the same event are applied in the same `execute_upgrade`
   pass, they are appended in **plan order**, which is registry order
   (because `_managed_settings_registrations` returns
   `artifacts_for_upgrade` order, which is TOML row order). This means
   the rendered registration order on a fully retrofit upgrade matches
   the rendered scaffold order from `_write_settings_json()`, satisfying
   the `-009` §5.11 ordering contract for both surfaces.
5. **Idempotence:** re-running upgrade after a successful register-hook
   apply produces zero new actions for that record because the marker
   is now in `registered_by_event[event]` on the next plan pass.

**No change to:** `_managed_settings_registrations`, `plan_upgrade`
control flow, gitignore plan/apply, or managed-file copy plan/apply.

##### §B.2 Tests (`tests/test_upgrade.py`) — 9 new cases (was ~4 in -009)

| # | Case | Asserts |
|---|------|---------|
| 1 | Plan: missing `turn-marker.py` under empty `UserPromptSubmit` | One `register-hook` action with `event="UserPromptSubmit"`, `payload="turn-marker.py"` |
| 2 | Plan: missing `gov09-capture.py` under `UserPromptSubmit` that already has `delib-search-gate.py` | One action for gov09 with event UserPromptSubmit; existing delib-search-gate untouched in plan |
| 3 | Plan: missing `owner-decision-capture.py` under absent `PostToolUse` key | One action with `event="PostToolUse"`; plan does not crash on missing key |
| 4 | Plan: missing `delib-preflight-gate.py` under `PreToolUse` that has 6 existing entries | One action with `event="PreToolUse"`; existing PreToolUse list size unchanged in plan |
| 5 | Apply: case 1 action against an empty settings.json — produces `hooks["UserPromptSubmit"] = [{"hooks": [{"type": "command", "command": "python .claude/hooks/turn-marker.py"}]}]`; existing `hooks["PreToolUse"]` (if any) unchanged byte-for-byte |
| 6 | Apply: case 3 action against settings with `hooks={"PreToolUse": [...]}` (no PostToolUse key) — creates `hooks["PostToolUse"]` with one entry; existing PreToolUse list preserved byte-for-byte |
| 7 | Apply: case 4 action against settings with 6-entry PreToolUse — appends to tail; the first 6 entries are preserved in their original order; `delib-preflight-gate.py` is the 7th entry |
| 8 | Idempotence: apply case 5 then re-plan — re-plan returns zero `register-hook` actions for the now-registered record |
| 9 | Defense: malformed root (e.g., `{"hooks": "not-a-dict"}`) — plan returns `[]` for non-dict hooks (or empty per existing `_plan_settings_registration` contract); apply on a non-dict root returns the existing SKIPPED status without crashing |

**Back-compat assertion (one additional case):** an `UpgradeAction`
constructed without `event=` (the back-compat default) routes through
the existing apply path with `event="PreToolUse"` — verifies no
behavioral regression for any caller that does not yet set the field.

**Total Phase 5/7 `tests/test_upgrade.py` deltas: 9 new + 1 back-compat
= 10 new (was ~4 in `-009`).**

##### §B.3 Doctor contract — generalized composite check

**File: `src/groundtruth_kb/project/doctor.py`**

Generalize the scanner-safe-writer composite check pattern (currently
`doctor.py:510-617`) to **every settings-hook-registration record whose
`doctor_required_profiles` includes the active profile**. Two
implementation paths are acceptable; the bridge prescribes one:

**Prescribed path: factory-function generalization.**

Replace the single `_check_scanner_safe_writer_drift(target,
profile_name)` function with a generic
`_check_settings_hook_registration_drift(target, profile_name,
registration)` helper, where `registration` is a
`SettingsHookRegistration` returned from `artifacts_for_doctor(profile,
class_="settings-hook-registration")` (consistent with `_check_hooks`
already using `artifacts_for_doctor(profile, class_="hook")` —
`doctor.py:328-332`). The helper performs the same liveness logic as
the existing scanner-safe-writer check but reads `hooks[registration.event]`
instead of hardcoding `PreToolUse`. The check name in the report is
`f"settings:{registration.id}"` for unambiguous output.

`run_doctor` then calls this helper inside the existing
`if p.includes_bridge:` branch (after the existing skill-presence
checks) by iterating over the doctor-required settings-hook-registration
records:

```python
if p.includes_bridge:
    ...
    for registration in artifacts_for_doctor(profile, class_="settings-hook-registration"):
        if isinstance(registration, SettingsHookRegistration):
            checks.append(
                _check_settings_hook_registration_drift(target, profile, registration)
            )
```

**Backward-compat preservation:** the existing
`_check_scanner_safe_writer_drift` is **retained** in the source for
one release cycle as a thin wrapper that delegates to the generic
helper with the scanner-safe-writer record looked up by id. This keeps
the existing test names green and avoids a check-name regression in
adopter scripts. Removing the wrapper is a follow-up bridge once
adopters have been notified. (If Codex prefers immediate rename, this
can be flipped — flagged as the only Open Question in §11.)

**Status semantics (unchanged from scanner-safe-writer pattern):**

- `pass` (`required=False`): the active profile is not bridge-enabled,
  or the record's `doctor_required_profiles` does not include the
  active profile.
- `fail`: the corresponding hook **file** is missing (i.e. the
  `hook.<short>` companion FileArtifact's target_path is absent on
  disk). Cross-class ID convention: a settings-hook-registration record's
  paired hook FileArtifact is found by stripping the `settings.` prefix
  and the trailing `.<event-lowercase>` suffix from the registration id
  — e.g. `settings.hook.turn-marker.userpromptsubmit` →
  `hook.turn-marker`. The lookup uses
  `find_artifact_by_id(paired_id)`; missing paired records ALARM at
  startup (registry-integrity failure) rather than degrade to a doctor
  warning.
- `warning`: the hook file is present but the `.claude/settings.json`
  registration for `registration.event` is missing.
- `pass`: hook file present, registration present in
  `hooks[registration.event]`.

**File-level integrity:** the doctor check defends against malformed
settings.json shape exactly as the scanner-safe-writer check does
(`doctor.py:558-586`) — non-dict root, non-dict `hooks`, non-list event
list, non-dict entry are all treated as "not registered" rather than
crashing the doctor pass.

##### §B.4 Doctor tests (`tests/test_doctor.py`) — 5 new cases (was ~4 in -009)

| # | Case | Asserts |
|---|------|---------|
| 1 | Bridge profile, `turn-marker.py` file missing | `settings:settings.hook.turn-marker.userpromptsubmit` returns `fail` |
| 2 | Bridge profile, `turn-marker.py` present, `hooks["UserPromptSubmit"]` empty | `settings:settings.hook.turn-marker.userpromptsubmit` returns `warning` |
| 3 | Bridge profile, `owner-decision-capture.py` present + registered in `hooks["PostToolUse"]` | `settings:settings.hook.owner-decision-capture.posttooluse` returns `pass` |
| 4 | Bridge profile, registration accidentally placed in `hooks["PreToolUse"]` instead of `hooks["UserPromptSubmit"]` for `turn-marker` | `settings:settings.hook.turn-marker.userpromptsubmit` returns `warning` (event-correct location is what's checked) |
| 5 | Base profile (non-bridge) | None of the 4 new `settings:` checks appear in the report (gated by `p.includes_bridge` AND by `doctor_required_profiles` filter) |

**Back-compat assertion (one additional case):** the existing
`scanner-safe-writer` doctor check name is still present in the report
output for `dual-agent` / `dual-agent-webapp` profiles (because
scanner-safe-writer's `doctor_required_profiles = []`, the wrapper
preserves the prior behavior — the wrapper is what runs the existing
check; the registry-iteration loop skips records with empty
`doctor_required_profiles`).

**Total `tests/test_doctor.py` deltas: 5 new + 1 back-compat = 6 new
(was ~4 in `-009`).**

#### Scaffold tests — unchanged from -009

`-009` §5.11 added 3 registry-order test cases asserting the rendered
`.claude/settings.json` per-event order matches the target. Those 3
cases are unchanged. The §B changes do not affect scaffold-rendered
ordering — they affect upgrade-time retrofit ordering, which is
covered by §B.2 cases 5/6/7.

### 5.12 Phase 11 — Post-implementation report + Codex VERIFIED

Contract in §7 (revised below).

---

## 6. Test Inventory Summary (REVISED counts)

| Phase | Test file | New tests in `-011` | Δ vs `-009` |
|-------|-----------|---------------------|-------------|
| 2 | `tests/test_da_db_routing_invariant.py` | ~8 | — |
| 2 | `tests/test_da_residual_rescan.py` | ~4 | — |
| 3 | `tests/test_source_ref_validation.py` | ~13 | — |
| 3 | `tests/test_cli_deliberations.py` | 0 new | — |
| 4 | `tests/test_lo_report_backfill.py` | 5 | — |
| 5 | `tests/test_delib_preflight_gate.py` | 23 | — |
| 5+7 | `tests/test_scaffold_settings.py` | +3 registry-order cases | — |
| 5+7 | `tests/test_upgrade.py` | **10** (9 event-aware + 1 back-compat) | **+6** |
| 5+7 | `tests/test_doctor.py` | **6** (5 generalized-check + 1 back-compat) | **+2** |
| 6 | `tests/test_transcript_extract.py` | 13 | — |
| 7 | `tests/test_owner_decision_capture.py` | 8 | — |
| 8 | `tests/test_backfill_framework.py` | 6 | — |
| 9 | `tests/test_wrap_gate.py` | 16 | — |
| **Total** | | **~115 new** (was ~107 in `-009`) | **+8** |

All new tests ASCII-only. All new modules mypy --strict clean, ruff
check + format clean. Baseline 1161 stays green. Expected post-bridge
suite size: ~1276.

---

## 7. Post-Impl Report Contract (REVISED to add §B evidence)

Post-implementation report filed to this thread as the next version
(NEW). Contents — items 1-12 from `-009` §7 are unchanged except for
items 9 and 12 which are extended:

1-8. *(Unchanged from `-009` §7.)*

9. **Rendered scaffold-settings evidence** (unchanged from `-009`)
   **PLUS event-aware upgrade plan/apply evidence (new per `-010` #1):**
   - Output of `gt project upgrade --dry-run` against an Agent-Red-like
     fixture project that is missing all 4 new registrations — must
     show 4 `register-hook` actions, one per record, each carrying the
     correct `event` field in the action description.
   - Output of `gt project upgrade --apply` against the same fixture —
     must show 4 `REGISTERED ... ({event})` lines and produce a
     settings.json whose `hooks["UserPromptSubmit"]`,
     `hooks["PostToolUse"]`, and `hooks["PreToolUse"]` lists each match
     the §B.1 ordering contract.
   - Output of `gt project upgrade --dry-run` immediately after — must
     show zero `register-hook` actions (idempotence proof).
10. **Dogfood evidence** (unchanged from `-009`).
11. **Rollback instructions** (unchanged from `-009`).
12. **Delta summary** — commit-local line counts + range line counts
    per `feedback_postimpl_report_hygiene.md`. **PLUS event-aware
    doctor evidence (new per `-010` #1):** output of `gt project
    doctor --profile dual-agent` against the same fixture in three
    states (all four hook files missing, files present + registrations
    missing, files + registrations present) showing the correct
    `fail` / `warning` / `pass` transitions for each of the four new
    `settings:` checks.

---

## 8. Rollback / Containment

*(Unchanged from `-009` §8.)* All §A and §B changes reversible via
`git revert` on `groundtruth-kb` main. The optional `event` field
defaults to `"PreToolUse"` so any in-flight callers that haven't been
updated continue to function under revert.

---

## 9. Prior Deliberations

Required DA search performed; directly relevant rows (unchanged from
`-009`):

- `DELIB-0715` — MemBase canonical definition.
- `DELIB-0716` / `-0717` / `-0718` — bridge-thread compression examples.
- `DELIB-0719` — S299 owner-decision round.
- `DELIB-0720` / `DELIB-0818` — prior DA rows on this thread.
- `DELIB-0721` / `DELIB-0805` — harvest-coverage bridge-thread rows.
- `DELIB-0817` — S299-continuation meta-summary.
- **`DELIB-0819`** — Phase-0 Q1/Q2/Q3 owner-decision DELIB
  (authoritative for §3).

No prior deliberation rejected the event-aware upgrade approach; the
prior decisions in DELIB-0720 explicitly require existing-adopter
retrofit, which §B operationalizes.

REVISED-5 `-011` differs from `-009` only in:
- §5.5.1 (one sub-bullet: `content` shape pinned to raw JSON).
- §5.5.3 (wording correction; counts and structure unchanged).
- §5.11 — new §A (lifecycle profiles for 4 new records) + §B (event-aware
  upgrade + doctor contracts and tests).
- §6 (test counts: +6 upgrade, +2 doctor; total +8).
- §7 item 9 (extended with upgrade plan/apply evidence) and item 12
  (extended with doctor evidence).

All other content preserved verbatim from `-009`.

---

## 10. Required Next Steps After Codex GO on This REVISED-5 Bridge

Same as `-009` §10 with one strengthening: Phase 7's "owner-decision
capture + GOV-09 capture + upgrade/doctor enforcement extension" now
expands to:

3. After Phase 1, in parallel:
   - Phase 7 — owner-decision capture + GOV-09 capture + **§B.1 upgrade
     plan/apply generalization (`upgrade.py` edits)** + **§B.3 doctor
     generalization (`doctor.py` edits)** + §A profile-axis
     additions in `templates/managed-artifacts.toml` for the 4 new
     settings-hook-registration records.

All other phasing and exit-gates unchanged from `-009` §10.

---

## 11. Open Questions for Codex

One narrow Codex preference question — implementation is unblocked
either way:

1. **Doctor wrapper retention horizon.** §B.3 retains
   `_check_scanner_safe_writer_drift` as a thin wrapper around the
   generalized helper for one release cycle to preserve the existing
   check name. **Default: keep the wrapper for one release.** If
   Codex prefers immediate rename to `settings:settings.hook.scanner-safe-writer.pretooluse`
   — set `scanner-safe-writer.pretooluse` `doctor_required_profiles = ["dual-agent", "dual-agent-webapp"]` and delete the wrapper — flag in the GO and the bridge will discharge the rename in the same commit. (This is the only judgment call; either path produces the same operational behavior on disk.)

Both `-010` blockers are resolved:
- **Lifecycle profile values for the 4 new settings-hook-registration
  records** are concrete in §A.
- **Event-aware upgrade plan/apply contract** is concrete in §B.1 with
  the `UpgradeAction.event` field, the `_plan_settings_registration`
  per-event pass, and the `_execute_register_hook` event-targeted
  insert that preserves existing entries.
- **Per-event tests** for plan, apply, idempotence, ordering, and
  malformed-shape defense are enumerated in §B.2.
- **Doctor tests** for the generalized check across all three event
  classes are enumerated in §B.4.
- **Bypass `content` raw-JSON contract** is pinned in §C (folded into
  §5.5.1 above) — no JSON-in-Markdown wrapper, tests' direct
  `json.loads(content)` is now the canonical contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
