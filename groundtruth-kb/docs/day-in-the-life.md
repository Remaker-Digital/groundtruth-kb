# A Day in the Life

A synthetic first week in the life of **Allison**, a solo developer building
a small appointment-booking API in Flask on her Windows laptop. Allison has
never used GroundTruth-KB before the first scene. By Friday she is writing
specs, running assertions, and reviewing Loyal Opposition feedback without
thinking about the tooling.

This is not a feature tour. It is what adoption actually looks like.

## Monday — Zero to First Commit

Allison clones an empty GitHub repo for `booking-api` and opens Claude Code
in the project folder. She is used to writing code first and documenting
second. Today she tries the other way around.

```powershell
pip install groundtruth-kb
gt project init booking-api --profile local-only --no-seed-example --no-include-ci
cd booking-api
gt project doctor
```

Doctor reports everything is installed. She opens the scaffold and sees
`groundtruth.toml`, a `bridge/` directory, `CLAUDE.md`, and a small
`src/tasks.py` stub. She is not ready for dual-agent mode yet, so she
sticks with `local-only`.

### Activity 1 — Add a Specification

She writes her first spec from the CLI:

```powershell
gt scaffold specs
```

The interactive flow asks for ID, title, status, and description. She
types `SPEC-001`, "Users can create a booking with a start time and a
duration in minutes," and picks `specified`. The CLI writes it to
`groundtruth.db` and confirms:

```
SPEC-001 inserted (version 1, status=specified).
```

She also writes one machine-checkable assertion: `grep` for the
`class Booking` definition in `src/booking.py`. The assertion is expected
to fail today, because `src/booking.py` does not exist yet. That is the
whole point — the spec is the commitment, the assertion is the proof.

## Tuesday — The Red-Green Rhythm

### Activity 2 — Add a Test

Allison writes a test file `tests/test_booking.py` with a single test:
`test_create_booking_returns_201`. Then she links the test to `SPEC-001`:

```powershell
gt tests add --id TEST-001 --spec SPEC-001 \
  --description "POST /bookings returns 201 for a valid payload"
```

She runs the test suite. It fails. She writes the minimum Flask handler
to make it pass. The test now passes. She runs `gt assert`:

```
PASSED: 1
FAILED: 0
```

Both the test and the spec assertion now hold. She promotes the spec to
`implemented`.

### Activity 3 — Push to Staging

Her `develop` branch now has a green test. She pushes:

```powershell
git push origin develop
```

GitHub Actions runs the CI template that `gt project init` scaffolded.
The workflow runs `pytest` and `gt assert`. Both pass. A staging deployment
job is gated by a manual approval — Allison clicks approve and watches the
app deploy to a free Azure App Service tier. She opens the staging URL,
creates a booking, sees it come back with a 201.

## Wednesday — Adding the Loyal Opposition

By Wednesday morning she has six specs, four tests, and one open work
item. She decides the single-agent feedback loop is too lonely. She
upgrades the scaffold to `dual-agent`:

```powershell
gt project upgrade --profile dual-agent
```

The upgrade adds `AGENTS.md`, a `bridge/INDEX.md`, and OS scheduler setup
instructions. She follows the
[Dual-Agent Setup](tutorials/dual-agent-setup.md) tutorial to wire up her
Codex-powered Loyal Opposition. Her first bridge proposal goes up at
10:47 AM. At 10:51 the Codex poller dispatches a review. At 10:58 she has
a NO-GO back citing a missing input-validation check.

She addresses the finding, writes a REVISED proposal, and gets a GO on
the next cycle.

## Thursday — Commit and Build

### Activity 4 — Commit and Build

With the Loyal Opposition in place, Allison's commit discipline shifts.
Each commit now references a spec and an approved bridge thread:

```
feat(booking): add cancellation endpoint [SPEC-004, bridge: cancel-flow-004 GO]
```

The CI template runs the full gate sequence on every commit:

```
pytest                → PASS (14 tests)
gt assert             → PASS (9 specs)
mkdocs build --strict → PASS
ruff check            → PASS
mypy --strict         → PASS
```

All green. She merges to `main` and the production deployment runs.

## Friday — Investigating and Learning

### Activity 5 — Investigate a Regression

A customer reports that cancelling a booking with a past start time
throws a 500 error. Allison opens Claude Code and describes the bug.
Claude reads the bridge protocol and proposes a fix as
`bridge/past-booking-cancel-500-001.md`. She lets the OS scheduler pick
it up.

The Loyal Opposition NO-GO's the first draft: Codex points out that the
proposed fix silently swallows the error instead of returning a 4xx.
Claude writes a REVISED proposal. Codex GO's. Claude implements, runs
tests, writes a post-implementation report. Codex VERIFIED.

The full cycle — report-to-fix-to-verified — took 72 minutes, 45 of which
Allison was away from her desk.

### Activity 6 — Retrieve Deliberations

Later that afternoon, Allison starts to code a rate-limiter and
remembers a similar decision came up two weeks ago. She searches the
Deliberation Archive:

```powershell
gt deliberations search "rate limit"
```

Three deliberations come back. The top hit is a Loyal Opposition review
that rejected a per-IP rate limit in favor of a per-token one. The
rejected alternative is spelled out. She does not have to re-litigate the
decision — it is already there, with the reasoning intact.

She cites the deliberation ID in the new proposal:

```
Building on DELIB-0042 (per-token rate limit, approved 2026-04-03)...
```

---

## What Allison Notices by Friday

**You are the decision maker.** The AI agents propose; she approves.
Nothing deploys, merges, or changes status without her explicit say-so.

**Nothing happens silently.** Every spec change has a version. Every
bridge cycle has a file. Every decision has a deliberation. If she forgot
what she did yesterday, `gt history` shows it.

**The cost is small.** Her API bill for the week — Claude Code tokens
plus Codex reviews — was under $20. The OS scheduler costs nothing and
only wakes the agents when there is bridge work to do.

**The AI agents work while she is away.** The bridge pollers run every
three minutes via Windows Task Scheduler, independent of whether Claude
Code is open. When she comes back from lunch, the queue is usually empty.

## What Allison Might Choose Differently

She would start with `dual-agent` mode on day one. The two days she spent
in `local-only` mode felt faster at the time, but in retrospect she shipped
at least one bug (empty duration field) that a Loyal Opposition review
would have caught in one pass.

She would write the bridge poller setup on day one too. It is documented
in [Bridge OS Scheduler](tutorials/bridge-os-scheduler.md) and takes
ten minutes to install.

## Can I Use Different Tools for the Loyal Opposition?

Yes. The Loyal Opposition role is defined by a protocol (the file
bridge), not by a specific tool. Any agent that can read markdown from
`bridge/`, analyze code, write a review, and update `bridge/INDEX.md`
can serve the role. The default setup uses Codex because it runs
autonomously via scheduled tasks and has been exercised across hundreds
of review cycles in the reference project.

## Getting Started

1. `pip install groundtruth-kb`
2. `gt project init my-project --profile dual-agent`
3. `cd my-project && gt project doctor`
4. Read [Your First Specification](tutorials/first-spec.md)
5. Read [Dual-Agent Setup](tutorials/dual-agent-setup.md)

Total time to a working project: about 15 minutes. Total time to
Allison's Friday: about a week.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
