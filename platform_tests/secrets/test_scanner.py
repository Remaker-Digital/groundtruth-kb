from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.secrets import (
    PRODUCTION_PATTERNS,
    TEST_SYNTHETIC_PATTERNS,
    Allowlist,
    AllowlistEntry,
    AllowlistLoadError,
    scan_all_refs,
    scan_paths,
    scan_range,
    scan_staged,
)


def _synthetic_value(provider_class: str, suffix: str = "ABCDEFGH") -> str:
    return f"GTKB_TEST_{provider_class.upper()}_PATTERN_{suffix}"


def _production_samples() -> dict[str, str]:
    return {
        "stripe_test_secret_key": "sk" + "_test_" + "A" * 24,
        "stripe_live_secret_key": "sk" + "_live_" + "B" * 24,
        "stripe_webhook_secret": "wh" + "sec_" + "C" * 32,
        "shopify_access_token": "sh" + "pat_" + "a" * 32,
        "shopify_shared_secret": "sh" + "pss_" + "b" * 32,
        "mailchimp_api_key": "c" * 32 + "-us12",
        "github_oauth_token": "gh" + "o_" + "D" * 36,
        "azure_openai_key": "AZURE_OPENAI_KEY=" + "E" * 32,
        "azure_container_apps_fqdn": "agent-red-api" + ".eastus" + ".azurecontainerapps.io",
        "azure_redis_fqdn": "cache" + ".redis" + ".cache.windows.net",
        "azure_cosmos_fqdn": "account" + ".documents" + ".azure.com",
        "azure_keyvault_fqdn": "vault" + ".vault" + ".azure.net",
        "azure_connection_string": "DefaultEndpointsProtocol=https;AccountName=acct;AccountKey=" + "F" * 44,
        "azure_cache_redis_key": "REDIS_KEY=" + "G" * 43 + "=",
        "azure_communication_services_key": "endpoint=https://svc.communication.azure.com/;accesskey=" + "H" * 44,
        "azure_cosmos_db_key": "COSMOS_KEY=" + "I" * 86 + "==",
        "agent_red_ar_key": "ar" + "_user_" + "J" * 16,
    }


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(repo_root: Path) -> None:
    _git(repo_root, "init")
    _git(repo_root, "config", "user.email", "tester@example.invalid")
    _git(repo_root, "config", "user.name", "GTKB Test")


def test_production_provider_patterns_match_runtime_samples(tmp_path: Path) -> None:
    fixture = tmp_path / "runtime-samples.txt"
    samples = _production_samples()
    fixture.write_text("\n".join(samples.values()), encoding="utf-8")

    result = scan_paths([fixture], repo_root=tmp_path, patterns=PRODUCTION_PATTERNS)

    assert {finding.provider_class for finding in result.findings} == set(samples)


def test_provider_coverage_with_synthetic_patterns(tmp_path: Path) -> None:
    fixture = tmp_path / "tests" / "secrets" / "fixtures" / "providers.txt"
    fixture.parent.mkdir(parents=True)
    values = [_synthetic_value(entry.name, f"VALUE{index:03d}") for index, entry in enumerate(TEST_SYNTHETIC_PATTERNS)]
    fixture.write_text("\n".join(values), encoding="utf-8")

    result = scan_paths([fixture], repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS)

    assert {finding.provider_class for finding in result.findings} == {entry.name for entry in TEST_SYNTHETIC_PATTERNS}
    serialized = json.dumps(result.to_json_dict(), sort_keys=True)
    for value in values:
        assert value not in serialized
    assert "sha256:" in serialized


def test_exact_value_and_path_allowlist_allows_only_the_exact_fixture(tmp_path: Path) -> None:
    allowed_path = tmp_path / "tests" / "secrets" / "fixture.txt"
    allowed_path.parent.mkdir(parents=True)
    value = _synthetic_value(TEST_SYNTHETIC_PATTERNS[0].name)
    allowed_path.write_text(value, encoding="utf-8")
    allowlist = Allowlist(
        entries=(AllowlistEntry(value=value, path="tests/secrets/fixture.txt", justification="synthetic fixture"),)
    )

    allowed = scan_paths([allowed_path], repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS, allowlist=allowlist)
    assert allowed.findings == []

    near_miss_path = tmp_path / "tests" / "secrets" / "fixture-copy.txt"
    near_miss_path.write_text(value, encoding="utf-8")
    blocked = scan_paths([near_miss_path], repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS, allowlist=allowlist)
    assert len(blocked.findings) == 1


def test_production_path_allowlist_entry_is_rejected(tmp_path: Path) -> None:
    allowlist_path = tmp_path / "allowlist.toml"
    allowlist_path.write_text(
        "\n".join(
            [
                "[[entries]]",
                f'value = "{_synthetic_value(TEST_SYNTHETIC_PATTERNS[0].name)}"',
                'path = "src/config.py"',
                'justification = "not allowed"',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(AllowlistLoadError, match="production-path entries are prohibited"):
        Allowlist.load(allowlist_path)


def test_staged_scan_uses_index_content_and_redacted_findings(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    staged_file = tmp_path / "candidate.txt"
    value = _synthetic_value(TEST_SYNTHETIC_PATTERNS[1].name)
    staged_file.write_text(value, encoding="utf-8")
    subprocess.run(["git", "add", "candidate.txt"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = scan_staged(repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS)

    assert len(result.findings) == 1
    assert result.findings[0].path == "candidate.txt"
    serialized = json.dumps(result.to_json_dict(), sort_keys=True)
    assert value not in serialized
    assert "sha256:" in serialized


def test_clean_staged_scan_passes(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    staged_file = tmp_path / "clean.txt"
    staged_file.write_text("plain text\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = scan_staged(repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS)

    assert result.findings == []
    assert result.paths_scanned == 1


def test_range_scan_uses_head_side_blob_and_redacts_output(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    target = tmp_path / "candidate.txt"
    target.write_text("clean\n", encoding="utf-8")
    _git(tmp_path, "add", "candidate.txt")
    _git(tmp_path, "commit", "-m", "base")
    base_sha = _git(tmp_path, "rev-parse", "HEAD")

    value = _synthetic_value(TEST_SYNTHETIC_PATTERNS[2].name)
    target.write_text(value, encoding="utf-8")
    _git(tmp_path, "add", "candidate.txt")
    _git(tmp_path, "commit", "-m", "candidate")
    head_sha = _git(tmp_path, "rev-parse", "HEAD")

    result = scan_range(f"{base_sha}..{head_sha}", repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS)

    assert len(result.findings) == 1
    assert result.findings[0].path == "candidate.txt"
    serialized = json.dumps(result.to_json_dict(), sort_keys=True)
    assert value not in serialized
    assert "sha256:" in serialized


def test_all_refs_scan_inventory_is_redacted_and_carries_object_metadata(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    target = tmp_path / "history.txt"
    value = _synthetic_value(TEST_SYNTHETIC_PATTERNS[3].name)
    target.write_text(value, encoding="utf-8")
    _git(tmp_path, "add", "history.txt")
    _git(tmp_path, "commit", "-m", "history candidate")
    _git(tmp_path, "tag", "v-test")

    result = scan_all_refs(repo_root=tmp_path, patterns=TEST_SYNTHETIC_PATTERNS)

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.path == "history.txt"
    assert finding.ref and finding.ref.startswith("refs/")
    assert finding.object_id
    serialized = json.dumps(result.to_json_dict(), sort_keys=True)
    assert value not in serialized
    assert "sha256:" in serialized
