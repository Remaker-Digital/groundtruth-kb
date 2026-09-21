"""The root instruction file and its declared pointers (M15 stage 1).

Owner ruling D15 as amended by R3 (D34, 2026-09-19; M15 rulings R1, R4, R13): the
baseline instruction file moved to the tracked root ``AGENTS.md`` (option B - no
render surface, no derivability check), ``CLAUDE.md`` and ``.goosehints`` are
tracked pointer files whose exact bytes are declared once in
``profiles.toml [root_pointers]`` and pinned by the acceptance checker
(``declared_pointer_drift``, both modes), never by the commit hook. This module is
the one acceptance test on the landed root file (rev2 finding 7): harness-neutral
(ADR-RULE-PROJECTION-FLOW-INVERSION-001 paragraph 5, GOV-HARNESS-NEUTRAL-BASELINE-001
paragraph 3 - no vendor directory enumerated, the neutral derived-output sentence
kept), no embedded checkout path, no neutral token, ``.agents`` not described as
generated, rules read on demand from the baseline and skills from ``.agents/skills``.
Content reconciliation of the former 62 KB root text is task 15.9; the sentences
asserted here are the ones stage 1 landed.
"""

from __future__ import annotations

import re
import stat
import subprocess
import tomllib
from pathlib import Path

import pytest

from scripts import check_harness_parity as parity

ROOT = Path(__file__).resolve().parents[2]
PROFILES = ROOT / "scripts/harness_projection/profiles.toml"
INSTRUCTIONS = "AGENTS.md"
BASELINE = ".harness-baseline-configuration"
SKILLS_ROOT = ".agents/skills"
# R1 option B (D34): the exact pointer bytes. profiles.toml [root_pointers] declares
# the same bytes so the checker and this test share one declaration, and a profile
# edit cannot silently redefine the ruling.
ROOT_POINTERS = {
    "CLAUDE.md": "@AGENTS.md\n",
    ".goosehints": (
        "Follow ./AGENTS.md (GT-KB session instructions). This file is only a pointer; do not add guidance here.\n"
    ),
}
ROOT_CARRIERS = (INSTRUCTIONS, *ROOT_POINTERS)
NEUTRAL_SENTENCE = "named harness configuration directories are derived output"
RULES_SENTENCE = "Read applicable rules on demand from `.harness-baseline-configuration/rules`."
SKILLS_SENTENCE = "Use the role-appropriate bridge skill in `.agents/skills`:"
VENDOR_ROOTS = (".claude", ".codex", ".cursor", ".goose", ".agent", ".api-harness")
DRIVE_LETTER = re.compile(r"\b[A-Za-z]:[\\/]")
NEUTRAL_TOKEN = re.compile(r"\{\{[A-Z_]+\}\}")


def _profiles() -> dict:
    return tomllib.loads(PROFILES.read_text(encoding="utf-8"))


def _instructions() -> str:
    return (ROOT / INSTRUCTIONS).read_text(encoding="utf-8")


def _tracked(*paths: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z", "--", *paths], capture_output=True, text=True, encoding="utf-8"
    )
    assert result.returncode == 0, result.stderr
    return {path for path in result.stdout.split("\0") if path}


def _issues(report: dict, code: str) -> list[dict]:
    return [issue for issue in report["issues"] if issue["code"] == code] + [
        issue for target in report["harnesses"].values() for issue in target["issues"] if issue["code"] == code
    ]


def test_root_carriers_are_tracked_regular_lf_files() -> None:
    assert _tracked(*ROOT_CARRIERS) == set(ROOT_CARRIERS)
    for name in ROOT_CARRIERS:
        path = ROOT / name
        metadata = path.lstat()
        reparse = getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        assert stat.S_ISREG(metadata.st_mode) and not reparse and path.resolve() == path, name
        raw = path.read_bytes()
        assert b"\r" not in raw and raw.endswith(b"\n") and not raw.startswith(b"\xef\xbb\xbf"), name


def test_root_agents_md_has_no_drive_letter() -> None:
    hits = [line for line in _instructions().splitlines() if DRIVE_LETTER.search(line)]
    assert hits == [], "the instruction file embeds a checkout path; it must read the same in every clone"


def test_root_agents_md_has_no_neutral_tokens() -> None:
    assert NEUTRAL_TOKEN.findall(_instructions()) == [], "the root file is read in place; nothing substitutes tokens"


def test_root_agents_md_does_not_name_agents_as_generated() -> None:
    text = _instructions()
    assert not [line for line in text.splitlines() if re.fullmatch(r"- `\.agents`\s*", line)]
    assert "`.agents`" not in text, ".agents holds the one skills source (D15); it is authored, not derived"


def test_root_agents_md_keeps_the_neutral_derived_output_sentence() -> None:
    assert NEUTRAL_SENTENCE in _instructions()


@pytest.mark.parametrize("vendor", VENDOR_ROOTS)
def test_root_agents_md_enumerates_no_vendor_directory(vendor: str) -> None:
    """R13: the neutral sentence stands in for the config_dir list (ADR paragraph 5, GOV paragraph 3)."""
    text = _instructions()
    assert f"`{vendor}`" not in text
    assert not [line for line in text.splitlines() if line.strip().startswith(f"- `{vendor}`")]
    assert not re.search(r"(?<![\w.])" + re.escape(vendor) + r"(?=[/\s`'\"])", text), vendor


def test_profiles_config_dirs_are_the_vendor_roots_this_test_refuses() -> None:
    roots = {profile["config_dir"].split("/")[0] for profile in _profiles()["harnesses"].values()}
    assert roots == set(VENDOR_ROOTS), sorted(roots)


def test_root_agents_md_names_the_rules_and_skills_sources() -> None:
    text = _instructions()
    assert RULES_SENTENCE in text
    assert SKILLS_SENTENCE in text
    assert "baseline's skills directory" not in text, "the pre-move wording names a directory that holds no skills"
    assert f"{BASELINE}/skills" not in text


def test_root_pointers_carry_exactly_the_declared_bytes() -> None:
    declared = _profiles()["root_pointers"]
    assert declared == ROOT_POINTERS, "profiles.toml [root_pointers] must carry the R1 option B bytes"
    for name, value in ROOT_POINTERS.items():
        assert (ROOT / name).read_bytes() == value.encode("utf-8"), name


def test_no_second_instruction_carrier() -> None:
    for name in (f"{BASELINE}/AGENTS.md", f"{BASELINE}/skills", "GEMINI.md", ".cursorrules"):
        assert not (ROOT / name).exists(), name


def test_live_tree_root_pointers_pass_the_checker() -> None:
    """The checker reads [root_pointers] itself; the live tree must satisfy it in derivation mode."""
    report = parity.check_harness_parity(ROOT, harness="claude", installed=False)
    assert "claude" in report["harnesses"], report["issues"]
    assert _issues(report, "declared_pointer_drift") == []
    assert _issues(report, "unavailable_projector") == []


def test_declared_pointer_drift_through_the_checker(generated_harness_root: Path) -> None:
    """A pointer that grows back into a canon carrier fails the checker; the target itself stays green."""
    root = generated_harness_root
    clean = parity.check_harness_parity(root, harness="claude", installed=True)
    assert clean["status"] == "pass", clean
    pointer = root / "CLAUDE.md"
    original = pointer.read_bytes()
    assert original == ROOT_POINTERS["CLAUDE.md"].encode("utf-8")
    try:
        pointer.write_bytes(original + b"\n# local guidance grew back\n")
        drifted = parity.check_harness_parity(root, harness="claude", installed=True)
    finally:
        pointer.write_bytes(original)
    assert drifted["status"] == "fail"
    assert [issue["code"] for issue in drifted["issues"]] == ["declared_pointer_drift"]
    assert drifted["harnesses"]["claude"]["status"] == "pass"
    assert parity.check_harness_parity(root, harness="claude", installed=True)["status"] == "pass"
