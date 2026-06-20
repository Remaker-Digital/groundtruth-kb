from __future__ import annotations

from scripts import ollama_harness as oh


def test_build_system_prompt_uses_verdict_first_language() -> None:
    route = oh.ModelRoute(
        key="fixture-route",
        model_id="fixture-model:latest",
        model_version="latest",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
    )
    prompt = oh.build_system_prompt("bridge-review", route)
    assert prompt is not None
    assert "advisory context" in prompt
    assert "rejection criterion" in prompt
    assert "exit 5 from the ADR/DCL" not in prompt
    assert "explicit owner waiver" not in prompt


def test_build_system_prompt_enforces_claim_first() -> None:
    route = oh.ModelRoute(
        key="fixture-route",
        model_id="fixture-model:latest",
        model_version="latest",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
    )
    prompt = oh.build_system_prompt("bridge-review", route)
    assert prompt is not None
    claim_index = prompt.index("python scripts\\bridge_claim_cli.py claim <document-slug>")
    helper_index = prompt.index("python .claude/skills/verify/helpers/write_verdict.py")
    bridge_workflow_index = prompt.index("Use the GT-KB file bridge")
    assert claim_index < helper_index < bridge_workflow_index


def test_build_system_prompt_seeds_prior_deliberations_before_verdict_write() -> None:
    route = oh.ModelRoute(
        key="fixture-route",
        model_id="fixture-model:latest",
        model_version="latest",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
    )
    prompt = oh.build_system_prompt("bridge-review", route)
    assert prompt is not None
    assert (
        "python .claude/skills/verify/helpers/write_verdict.py --slug <document-slug> --body-file <draft-body-file>"
    ) in prompt
    assert "Review and prune the helper-seeded Prior Deliberations" in prompt
    assert "preserve its failure\noutput in the verdict evidence" in prompt
    assert "silently omitting Prior Deliberations" in prompt


def test_build_system_prompt_retains_preflight_commands() -> None:
    route = oh.ModelRoute(
        key="fixture-route",
        model_id="fixture-model:latest",
        model_version="latest",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
    )
    prompt = oh.build_system_prompt("bridge-review", route)
    assert prompt is not None
    assert "bridge_applicability_preflight.py" in prompt
    assert "adr_dcl_clause_preflight.py" in prompt


def test_build_system_prompt_uses_no_index_bridge_instructions() -> None:
    route = oh.ModelRoute(
        key="fixture-route",
        model_id="fixture-model:latest",
        model_version="latest",
        tool_calling_supported=True,
        allowed_tools=("Read", "Write", "Edit", "Grep", "Glob", "Bash"),
    )
    prompt = oh.build_system_prompt("bridge-review", route)
    assert prompt is not None
    assert "bridge/INDEX.md" not in prompt
    assert "full\nversioned bridge-file chain" in prompt
    assert "gt bridge dispatch config" in prompt
    assert "gt bridge dispatch status" in prompt
    assert "gt bridge dispatch\nhealth" in prompt
