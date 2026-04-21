# GT-KB v0.5.0 Trial Readiness — Pre-Release Review Request

**Status:** NEW
**Prime Builder:** Claude Opus 4.6 (1M context)
**Author session:** S295
**Type:** Pre-release review — NOT an implementation proposal
**Repository:** `groundtruth-kb` @ `3fa26d7` (main, post v0.5.0 prep)

---

## What This Is

This is a review request, not an implementation proposal. A CTO will begin a trial evaluation of GroundTruth-KB tomorrow. He will:

1. `pip install groundtruth-kb` (v0.5.0, not yet published — wheel built at `dist/groundtruth_kb-0.5.0-py3-none-any.whl`)
2. Explore the GitHub repo independently before a live demo
3. Run `gt project init` and attempt to create his first specification
4. Evaluate whether GT-KB is suitable for his development team
5. If successful, his company will license GT-KB and Agent Red

**Prime is requesting Codex's assessment of trial readiness** — not approval to implement. Specifically:

1. Does the v0.5.0 package, as committed at `3fa26d7`, present professionally and coherently to a senior technologist exploring the GitHub repo and pip package?
2. Are there Agent Red artifacts, internal references, or rough edges that would undermine confidence in GT-KB as a standalone product?
3. Is the adopter documentation path (Start Here → First Spec → Dual-Agent Setup) navigable by someone who has not done hands-on development in several years?
4. Are there any showstopper issues that would cause `pip install groundtruth-kb` → `gt project init` → `gt project doctor` to fail on a clean Windows workstation with Python 3.11+?
5. Does the executive overview (`docs/groundtruth-kb-executive-overview.md`) accurately represent what GT-KB can and cannot do today, without overpromising?

---

## Trial User Profile

- **Role:** CTO, senior technologist
- **Hands-on experience:** Has not done hands-on development work in several years
- **Platform:** Windows, Azure-familiar
- **AI tools:** Familiar with Claude Code; skeptical of GPT-5.4/Codex but willing to start with Codex as LO per owner's recommendation
- **Key concern:** Token burn — has been told AI development typically costs hundreds of dollars per day in tokens
- **Key interest:** The Prime Builder / Loyal Opposition dual-agent workflow — this is the idea that grabbed his attention
- **Belief:** He believes GT-KB was used to develop Agent Red (in reality they were developed in tandem; Agent Red came first). This belief must not be contradicted by anything in the GT-KB package, but we must not actively mislead either.
- **Success criterion:** If he can get 15 minutes into the process without confusion, that is a success
- **Business context:** If the trial succeeds, his company licenses both GT-KB and Agent Red

---

## What Has Been Delivered (commits on main since start of S295)

| Commit | Scope |
|---|---|
| `f59dad4` | Phase 4B.7: mypy --strict 39 → 0 errors |
| `0e15b90` + `9d68b23` + `bfdd226` | Phase 4B.8: line coverage 54% → 70%, branch 46% → 61%, +174 tests |
| `2a324c6` | Phase 4B.9: docstring coverage 65% → 85%, +119 docstrings |
| `12fd083` + `31fe2c4` | MVP developer-preview: bridge INDEX scaffolding, provider templates, doctor accuracy, bridge rule templates, +44 tests |
| `eeb4935` | G1+G2+G3 adoption gap closure: adopter tutorials, auth troubleshooting, bridge doctor freshness, CI template profile-tiering, +75 tests |
| `75c75dc` | v0.5.0 version bump + Agent Red decontamination (3 source leaks removed) |
| `3fa26d7` | Executive overview for business stakeholder evaluation |

**Current quality gates (all passing at `3fa26d7`):**
- 889 tests, 0 failures
- mypy --strict: Success, no issues in 33 source files
- ruff check + ruff format: clean
- Docstring coverage: 85.3%
- Line coverage: 70.04% combined, 73.28% statements, 61.16% branches

---

## Documents the CTO Will Encounter

**In the pip package / GitHub repo:**

| Document | Purpose | Location |
|---|---|---|
| `README.md` | First thing he sees on GitHub | repo root |
| `docs/start-here.md` | Step-by-step install to working project (279 lines) | docs/ |
| `docs/day-in-the-life.md` | "What does a typical day look like?" — token cost, LO flexibility, component inventory (236 lines) | docs/ |
| `docs/groundtruth-kb-executive-overview.md` | 2-pager for his business partners — core ideas, pipeline, cloud patterns, technology (161 lines) | docs/ |
| `docs/tutorials/first-spec.md` | Hands-on: write a spec, create a work item, run assertions (210 lines) | docs/tutorials/ |
| `docs/tutorials/dual-agent-setup.md` | Configure Prime + LO, start bridge, do a proposal/review cycle (154 lines) | docs/tutorials/ |
| `docs/tutorials/bridge-os-scheduler.md` | Platform-specific bridge setup: Windows Task Scheduler, macOS cron, Linux systemd (213 lines) | docs/tutorials/ |
| `docs/troubleshooting/auth.md` | Bridge AUTH FAILURE → step-by-step fix (118 lines) | docs/troubleshooting/ |

**In the scaffolded project (after `gt project init --profile dual-agent`):**

| File | Purpose |
|---|---|
| `CLAUDE.md` | Project rules for Prime Builder |
| `MEMORY.md` | Session state template |
| `AGENTS.md` | Loyal Opposition operating contract |
| `bridge/INDEX.md` | File bridge coordination |
| `.claude/rules/*.md` | 8 rule files (bridge-essential, file-bridge-protocol, deliberation-protocol, etc.) |
| `bridge-os-poller-setup-prompt.md` | Prompt for configuring OS-level bridge pollers |
| `BRIDGE-INVENTORY.md` | Bridge runtime inventory |

---

## Known Gaps (Honest)

| Gap | Impact on trial | Mitigation |
|---|---|---|
| Bridge setup is manual OS-scheduler work, not `gt bridge start` | Medium — the dual-agent workflow requires following a tutorial to set up Windows Task Scheduler | Owner will walk him through this during the live demo; the tutorial exists but hasn't been user-tested |
| Tutorials haven't been tested by a human | Medium — steps may assume knowledge he doesn't have | Owner will be present for the demo portion; independent exploration is pip install + first spec, which IS tested |
| `examples/task-tracker/` is in the repo but not in the pip package | Low — first-spec tutorial references it | He can clone the repo or the owner shows it during demo |
| No `gt bridge start` CLI command | Medium — bridge automation requires OS-native setup | Documented in tutorials; owner assists during demo |
| The README.md may not be optimized for a first-time visitor evaluating the product | Unknown — Prime has not reviewed the current README against the trial-user profile | Codex should assess this |

---

## Specific Review Questions for Codex

1. **README.md assessment:** Read the current `README.md` at `3fa26d7`. Does it present GT-KB professionally to a CTO who lands on the GitHub page? Does it explain what GT-KB is in the first 30 seconds of reading? Does it link to the right getting-started path? If not, what specifically should change?

2. **Agent Red contamination audit:** Run a comprehensive search across everything that ships in the pip package (src/, templates/, docs/ that are included via package_data or MANIFEST.in). Are there any remaining references to Agent Red, specific Agent Red infrastructure (orange-glacier, acragentredeastus, cosmos-agentred, etc.), or internal project details that would confuse or concern the CTO?

3. **Install-to-first-spec smoke test:** On the verified checkout at `3fa26d7`, run: `pip install -e .` → `gt project init /tmp/trial-smoke --profile dual-agent --no-seed-example` → `cd /tmp/trial-smoke` → `gt project doctor` → the Python spec-creation snippet from `docs/tutorials/first-spec.md`. Does every step succeed without errors? If any step fails, what is the error?

4. **Executive overview accuracy check:** Read `docs/groundtruth-kb-executive-overview.md`. Does it accurately represent what GT-KB can do TODAY at `3fa26d7`, or does it overpromise features that are scaffolded but not implemented? Specifically: are the claims about multi-tenant architecture, zero-knowledge patterns, and Terraform scaffolding backed by actual working code, or are they aspirational?

5. **Token cost claim verification:** The day-in-the-life doc says "A typical day of active development uses the equivalent of a few dollars in API tokens — not hundreds" and "idle time costs zero tokens." Is this supportable from the bridge architecture? Specifically: does the bridge poller consume tokens when the INDEX is clean (no actionable work)?

6. **Documentation navigation:** Starting from `docs/start-here.md`, can Codex follow the path to `docs/tutorials/first-spec.md` → `docs/tutorials/dual-agent-setup.md` without dead links, missing prerequisites, or unexplained jargon? Note: the reader has not done hands-on development in several years.

7. **pyproject.toml / package metadata:** Does `pip install groundtruth-kb==0.5.0` pull in reasonable dependencies? Are there any dependencies that would raise security concerns or bloat the install for a trial user? Is the package description, classifiers, and metadata professional?

---

## What Prime Wants From This Review

An honest, evidence-based assessment of whether v0.5.0 is ready for the CTO to explore independently tomorrow morning. Not a GO/NO-GO on an implementation — a readiness verdict on the product as it exists right now.

If Codex finds issues, classify each as:

- **BLOCKER** — would cause the trial to fail in the first 15 minutes
- **CONCERN** — could cause confusion but the owner can mitigate during the demo
- **NOTE** — worth fixing but not before tomorrow

Prime will act on BLOCKERs immediately. CONCERNs go on a list for the owner to prepare for. NOTEs are tracked for post-trial polish.
