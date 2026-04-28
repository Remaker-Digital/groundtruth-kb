---
name: Complexity and fragility awareness during proposals
description: Every proposal element must be evaluated for maintenance burden, coupling, and testability — not just functionality added
type: feedback
---

Consider overall system complexity and fragility when working through each element of each proposal. The system is complex and must be maintained and modernized as new components and capabilities become available. Do not let the system become brittle, and do not let subsystems become overly entangled or un-testable.

**Why:** The system has grown substantially (2,092 specs, 20 agents, 39 API endpoints, 18 integration specs, etc.). Each addition creates maintenance surface. Owner wants explicit complexity/coupling/testability assessment alongside functional value.

**How to apply:** For every proposal element, evaluate: (1) does this increase coupling between subsystems? (2) can this be tested in isolation? (3) what is the maintenance burden if upstream dependencies change? (4) is there a simpler approach that achieves the same outcome? Prefer removing or simplifying over adding. Flag elements that increase entanglement.
