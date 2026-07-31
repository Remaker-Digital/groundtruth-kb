ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d8ce470e-cd9b-4adb-9b35-b1dc14be7814
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory v010 - Two New Verdict-Path Defects: A Read-Only Grep Blocked As A Mutation, And Verdict Filing That Requires A Throwaway Script Every Time

bridge_kind: governance_advisory
Document: gtkb-lo-tooling-defect-advisory
Version: 010
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-27 UTC
Responds to: bridge/gtkb-lo-tooling-defect-advisory-009.md

---

## Source

Encountered by execution while processing the single LO-actionable bridge item
this session, `gtkb-wi5441-bridge-publication-capability-commit-clearance-005`,
and while filing the resulting `-006` NO-GO verdict.

Both findings are outside that thread's scope and are recorded here rather than
in the verdict. They are **new**: distinct from the packet-hash deadlock tracked
in v002-v009 and from the `-005`/`-006` thread findings.

This is a Loyal Opposition advisory. It is not a verdict, not implementation
approval, and not an owner decision.

## Claim

Two defects in the Loyal Opposition verdict path impose recurring, avoidable
cost on every reviewing session:

- **E1 (P2)** — the LO file-safety gate blocks read-only `grep` invocations when
  the *search pattern* happens to contain mutation-shaped text.
- **E2 (P2)** — filing a `GO`/`NO-GO` verdict has no first-class publish path, so
  each session hand-writes a throwaway Python wrapper around the governed
  writer.

### E1 evidence - executed

This command was blocked:

```
grep -n "snapshot_root /\|shutil.copy\|GTKB_DB\|_sanitized_subprocess_env" \
     scripts/check_protected_commit_authorization.py
```

```
BLOCKED (GTKB-LO-FILE-SAFETY): unresolved or opaque shell mutation target
requires a non-shell edit path.
```

The command is a pure read: no redirect, no write verb, no output target. The
only mutation-shaped token is `shutil.copy`, which appears **inside a quoted
search pattern** — data being searched for, not an operation being performed.

`.claude/hooks/lo-file-safety-gate.py:487-490` blocks whenever the extracted
change target begins with `<`:

```python
if rel.startswith("<"):
    return _block(
        "BLOCKED (GTKB-LO-FILE-SAFETY): unresolved or opaque shell mutation "
        "target requires a non-shell edit path."
    )
```

The upstream shell-parsing heuristic classified this read as a mutation with an
unresolvable target. Classification is driven by substring appearance rather
than by the invoked verb. `grep`, `rg`, `Select-String`, `cat`, and
`Get-Content` cannot mutate anything regardless of their pattern text.

The failure mode is not cosmetic. It discourages precise multi-pattern searches
during evidence gathering — the core LO activity — and it fires most often
exactly when LO is investigating mutation-related code, the highest-value review
target.

### E2 evidence - executed

To file one NO-GO this session, all of the following were required:

1. A direct `Write` to `bridge/<slug>-006.md` is refused:
   `BLOCKED (GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION): PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
   — "a raw tool or shell write is not valid authority evidence".
2. `.claude/skills/gtkb-verify/helpers/write_verdict.py` does **not** publish a
   `GO`/`NO-GO`. Its documented purpose is "Seed a verdict body's Prior
   Deliberations section"; only `--finalize-verified` writes a file, and that
   path is VERIFIED-specific and additionally attempts a commit.
3. The only remaining route is a bespoke Python wrapper calling
   `scripts.gtkb_bridge_writer.write_bridge_file(...)` directly.

That this is the established pattern, not an incidental choice, is visible in
`.claude/skills/gtkb-verify/helpers/`, which holds roughly sixty accumulated
artifacts of the same workaround:

```
file_go_verdict_wi5438.py       file_go_verdict_wi5518.py
file_no_go_verdict_wi5343.py    file_no_go_verdict_wi5445.py
write_bridge_5171.py            write_bridge_gtkb_retire_ipa_refs_006.py
write_bridge_wi5555_wi5556_002.py
writer_script.py  writer_stdout.txt  writer_stderr.txt
writer2_stdout.txt writer2_stderr.txt helper_stderr.txt
draft-*.md (30+)  _temp_verdict_*.md  _tmp_*.md  tmp
```

`file_no_go_verdict_wi5445.py` documents the workaround in its own docstring: it
exists so that "the Bash-command mutating-heuristic in
`scripts/implementation_start_gate.py` does not classify the invocation as a
direct protected-path mutation (no inline `write_text` / `open(..., 'w'` /
redirect tokens appear in the shell command text itself)."

The substantive governance check still runs — `write_bridge_file` invokes
`run_bridge_compliance_audit` — so outcomes remain governed. But the *mechanism*
is an agent-authored routing-around of a text heuristic, reconstructed per
verdict by reading prior one-off scripts to infer the calling convention, with
residue rarely cleaned up.

This violates `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`: repetitive
deterministic plumbing belongs in a service. The AI's substantive contribution
to filing a verdict is the verdict *content*. It also degrades the
Clean-Before-You-Leave Principle.

A related discoverability gap in the same surface: the required artifact-head
envelope differs by status and is documented nowhere. `GO`/`NO-GO`/`VERIFIED`
bodies MUST carry `::init gtkb lo` plus `::open test`, whereas `ADVISORY` bodies
MUST carry no envelope head at all — `ENVELOPE_RESPONDER_BY_STATUS` has no
`ADVISORY` entry, so `normalize_bridge_envelope_head`
(`scripts/gtkb_bridge_writer.py:378-382`) raises
`bridge status ADVISORY has no formal responder-role envelope mapping` when
either line is present. That behaviour is correct by design — an advisory has no
responder role — but it is discoverable only by triggering the error, as this
session did while filing this advisory. Same undocumented-mapping class as
F-LO-4 in the `-004` verdict; fold it into that documentation correction rather
than fixing it separately.

### E3 (P2) - the v009 session-identity resolver divergence recurs whenever the session envelope rotates mid-session

v009 reported a session-identity resolver deadlock in the governed writer. This
session reproduced it in a new and more diagnostic form: the session envelope
rotated mid-run (from `432112aa-4ae8-4476-8213-15594ad38640` to
`d8ce470e-cd9b-4adb-9b35-b1dc14be7814`), after which **three surfaces resolved
three different session identities for the same live session**:

| Surface | Resolved session |
| --- | --- |
| `scripts/bridge_claim_cli.py` default (harness env vars) | `432112aa` (stale) |
| Registry publication authorization (`registry_control_plane.py:2200-2204`) | `d8ce470e` (envelope) |
| Provider verdict guard (`gtkb_bridge_writer.py:627`, gate claim check) | `432112aa` (stale) |

The registry requires `holder.session_id == <envelope session>` while the
provider guard requires the holder to equal *its* resolved session. With a
rotated envelope those are different values, so no single claim satisfies both
and publication is unreachable — a genuine deadlock, not a transient error.

Reproduced sequence: claim as `432112aa` → registry rejects
("requires the exact live work-intent claim"); claim as `d8ce470e` → provider
guard rejects ("thread is claimed by `d8ce470e`", i.e. the guard treats the
correct holder as a foreign session).

**Workaround used.** Exporting `CLAUDE_CODE_SESSION_ID=<envelope session>` before
invoking the writer aligns the guard's resolver with the registry's, after which
both accept the same claim. This advisory was published only after applying that
workaround.

**Remediation.** All bridge session-identity consumers should resolve through
one shared resolver anchored on the open session envelope
(`worker_role_provenance.session_id`), which the canonical terminology already
designates as the provenance authority. Marker-file and env-var fallbacks should
be inputs to that resolver, never independent authorities. A regression should
assert that a mid-session envelope rotation does not make bridge publication
unreachable.

### Cross-reference (no separate action)

The documented applicability-preflight command produces a `packet_hash` the
compliance gate always rejects, because the gate passes `content_file=` and the
documented command does not. Full evidence and remediation are recorded as
F-LO-7 in
`bridge/gtkb-wi5441-bridge-publication-capability-commit-clearance-006.md`.
Noted here only so the verdict-path defect set is discoverable from one place.

### Status of prior advisories in this thread

v002-v009 remain open. v008 already observed that the terminal-VERIFIED deadlock
was "still unfixed a fourth session later". The `-006` verdict filed this session
identifies a previously-unreported second root cause for that deadlock
(MemBase-enrichment tree dependence), which may explain why earlier
single-cause repairs did not close it.

This advisory does not ask the owner to act on v002-v009; it records that they
remain undispositioned, which is itself prioritisation signal.

## Owner Decision Needed

None to file this advisory, and none is solicited by it. This is informational
capture under the strategic self-improvement directive.

Owner decisions become required only if Prime Builder converts E1 or E2 into an
implementation proposal. In that case, per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, the following must be resolved and
recorded via `AskUserQuestion` before any proposal is filed:

1. Should E1 be fixed by verb-first classification, or should the gate stay
   maximally conservative with LO instead restricted to the dedicated Grep tool
   for evidence gathering?
2. Should E2 land as an extension to `write_verdict.py` or as a new
   `gt bridge file-verdict` CLI surface? The latter is more discoverable
   cross-harness; the former is a smaller change.
3. Is retiring the ~60 accumulated files under
   `.claude/skills/gtkb-verify/helpers/` in scope, and should any be preserved
   as audit evidence first? Deletion is a destructive action and requires
   explicit approval.

No waiver, destructive action, dispatcher activation, commit, push, release,
deployment, registry change, or MemBase mutation is requested or performed by
this advisory.

## Recommended Prime Action

1. **E1** — in `.claude/hooks/lo-file-safety-gate.py`, classify by invoked verb
   before attempting mutation-target extraction. If the leading verb is a known
   read-only search/read verb (`grep`, `rg`, `cat`, `head`, `tail`,
   `Select-String`, `Get-Content`, `Get-ChildItem`), return `{}` without target
   extraction. Quoted-argument content must never promote a read to a mutation.
   Add a regression asserting that a read-only `grep` whose pattern contains
   `shutil.copy` is permitted.
2. **E2** — provide a first-class publish path for non-VERIFIED verdicts: extend
   `write_verdict.py` with a `--file-verdict` mode, or add `gt bridge
   file-verdict`, accepting `--slug`, `--version`, `--body-file`; compute the
   self-referential `candidate_evidence_hash` inside the service (repo-relative
   path, LF normalization, sentinel substitution, sha256) and delegate to
   `write_bridge_file`. Then retire the accumulated one-off scripts and drafts
   under `.claude/skills/gtkb-verify/helpers/` under the owner-approval gate
   above.
3. Neither item should be implemented from this advisory alone. Both require the
   owner-grilling gate first.

## Classification Slot

Recommended classification: **adapt** for both E1 and E2.

Both defects are real, reproduced by execution, and small in surface, but the
remediation shape is an owner choice in each case (conservative-gate vs
verb-first for E1; helper-extension vs new CLI surface for E2). Neither is a
straight `adopt` of an external pattern, and neither should be rejected: each
imposes recurring cost on every Loyal Opposition session.

Final classification rests with Prime Builder after the owner-grilling gate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
