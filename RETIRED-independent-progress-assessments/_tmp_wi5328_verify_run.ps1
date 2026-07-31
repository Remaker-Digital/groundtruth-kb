# Temporary LO verification runner for gtkb-wi5328-session-envelope-role-writeback
# Delete after use.
$ErrorActionPreference = 'Continue'
$py = 'E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe'
$root = 'E:\GT-KB'
$log = Join-Path $root 'independent-progress-assessments\_tmp_wi5328_verify_output.txt'
Set-Location $root

function Write-Step($n, $cmd) {
    Add-Content $log "`n===== STEP $n =====`nCOMMAND: $cmd`n"
}

Remove-Item $log -ErrorAction SilentlyContinue

Write-Step 1 "$py E:\GT-KB\scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback"
& $py E:\GT-KB\scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 2 "$py E:\GT-KB\scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback"
& $py E:\GT-KB\scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5328-session-envelope-role-writeback 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 3 'Get-FileHash -Algorithm SHA256 (four targets)'
$claims = @{
    'groundtruth-kb/src/groundtruth_kb/session/envelope.py' = 'A7C3DD535EDE3DEDAB333F4B84F629A9D246A51297683FB414DB4549BB663B42'
    'scripts/session_self_initialization.py' = 'E7B959ED7D46E59131FDA3942C602DC656EE7B545C756A5541181CE5E70CA2E5'
    '.claude/hooks/workstream-focus.py' = 'B45F6C70B23EDA5D5B92844FEE0D5742AB7EF60171D711C160F6340C17AE8713'
    'platform_tests/scripts/test_session_self_initialization.py' = '26355ABBCE775B1C2BD21189D85329BB91DF4F6F0CCE987B8E00934BDC8B1115'
}
foreach ($rel in $claims.Keys) {
    $h = (Get-FileHash -Algorithm SHA256 (Join-Path $root $rel)).Hash
    $match = if ($h -eq $claims[$rel]) { 'MATCH' } else { 'MISMATCH' }
    $line = "$rel -> $h ($match; claimed $($claims[$rel]))"
    Write-Output $line
    Add-Content $log $line
}
Add-Content $log 'EXIT_CODE=0'

Write-Step 4 "$py -m pytest platform_tests/scripts/test_session_self_initialization.py -k `"not test_direct_script_execution_emits_startup_payload`" -q --tb=short --timeout=300"
& $py -m pytest platform_tests/scripts/test_session_self_initialization.py -k "not test_direct_script_execution_emits_startup_payload" -q --tb=short --timeout=300 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 5 "$py -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short --timeout=300"
& $py -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short --timeout=300 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 6 "$py -m ruff check (four targets)"
& $py -m ruff check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 7 "$py -m ruff format --check (four targets)"
& $py -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 8 'git diff --check (four targets)'
git diff --check -- groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Step 9 'git status --short (four targets)'
git status --short -- groundtruth-kb/src/groundtruth_kb/session/envelope.py scripts/session_self_initialization.py .claude/hooks/workstream-focus.py platform_tests/scripts/test_session_self_initialization.py 2>&1 | Tee-Object -Append -FilePath $log
Add-Content $log "EXIT_CODE=$LASTEXITCODE"

Write-Output "Wrote $log"
