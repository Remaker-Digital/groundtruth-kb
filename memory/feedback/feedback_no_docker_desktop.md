---
name: No Docker Desktop
description: Never launch or use Docker Desktop — always use az acr build for container builds unless explicitly told otherwise
type: feedback
---

AVOID USING DOCKER DESKTOP UNLESS EXPLICITLY ASKED. Always use `az acr build` for container image builds — this runs on Azure's infrastructure and does not require Docker locally.
