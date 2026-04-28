---
name: Build process — GitHub Actions only
description: Never build Docker locally or via ACR Tasks. All builds go through GitHub Actions workflows.
type: feedback
---

NEVER build Docker images locally or via `az acr build`. All container image builds go through GitHub Actions workflows.

**Why:** Local Docker builds were abandoned ~200 sessions ago. The build process uses GitHub Actions for reproducibility, CI checks, and proper artifact management. Building locally bypasses CI guardrails and can produce inconsistent images.

**How to apply:**
- To build the API gateway image: trigger the GitHub Actions build workflow (push to the appropriate branch or use `gh workflow run`)
- To build the test host: same — GitHub Actions only (documented in MEMORY.md)
- Never run `docker build`, `az acr build`, or any local container build command
- If Docker Desktop isn't running, that's expected — it's not needed
