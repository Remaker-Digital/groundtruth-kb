# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.governance.mutation module."""

from groundtruth_kb.governance.mutation import classify_bash_command, is_source_path


def test_redirect_detected():
    result = classify_bash_command("echo x > src/foo.py")
    assert "shell output redirection (>)" in result


def test_append_detected():
    result = classify_bash_command("echo x >> src/foo.py")
    assert "shell append redirection (>>)" in result


def test_tee_detected():
    result = classify_bash_command("cat x | tee src/foo.py")
    assert "tee command" in result


def test_cp_detected():
    result = classify_bash_command("cp /tmp/foo src/foo.py")
    assert "cp command" in result


def test_mv_detected():
    result = classify_bash_command("mv /tmp/foo src/foo.py")
    assert "mv command" in result


def test_sed_i_detected():
    result = classify_bash_command("sed -i 's/a/b/' src/foo.py")
    assert "sed -i (in-place edit)" in result


def test_awk_i_detected():
    result = classify_bash_command("awk -i inplace '{print}' src/foo.py")
    assert "awk -i (in-place edit)" in result


def test_powershell_set_content():
    result = classify_bash_command("Set-Content -Path src/foo.py -Value x")
    assert "PowerShell Set-Content" in result


def test_powershell_add_content():
    result = classify_bash_command("Add-Content src/foo.py x")
    assert "PowerShell Add-Content" in result


def test_powershell_out_file():
    result = classify_bash_command("Get-X | Out-File src/foo.py")
    assert "PowerShell Out-File" in result


def test_python_oneliner_open():
    result = classify_bash_command("python -c \"open('src/foo.py','w').write('x')\"")
    assert any("Python one-liner" in r for r in result)


def test_node_oneliner_writefile():
    result = classify_bash_command("node -e \"fs.writeFileSync('src/foo.py','x')\"")
    assert any("Node.js" in r for r in result)


def test_perl_i_detected():
    result = classify_bash_command("perl -i -pe 's/a/b/' src/foo.py")
    assert "perl -i (in-place edit)" in result


def test_ruby_i_detected():
    result = classify_bash_command("ruby -i -pe 'gsub(/a/,\"b\")' src/foo.py")
    assert "ruby -i (in-place edit)" in result


def test_clean_command_no_mutations():
    result = classify_bash_command("ls -la src/")
    assert result == []


def test_is_source_path_true():
    assert is_source_path("src/groundtruth_kb/db.py") is True


def test_is_source_path_false():
    assert is_source_path("docs/guide.md") is False
