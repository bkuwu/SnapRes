param(
    [Parameter(Mandatory = $true)][ValidateSet('Enable', 'Disable')]
    [string]$Action,
    [string]$ResultFile
)

$ErrorActionPreference = 'Stop'

$sharedDir = Join-Path $env:ProgramData 'SnapRes'
$logPath = Join-Path $sharedDir 'driver-debug.log'

function Write-Log {
    param([string]$Message)
    try {
        if (-not (Test-Path $sharedDir)) {
            New-Item -Path $sharedDir -ItemType Directory -Force | Out-Null
        }
        $line = "[{0}] [{1}] {2}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $PID, $Message
        Add-Content -Path $logPath -Value $line -Encoding UTF8 -ErrorAction SilentlyContinue
        $existing = Get-Content -Path $logPath -ErrorAction SilentlyContinue
        if ($existing -and $existing.Count -gt 400) {
            Set-Content -Path $logPath -Value ($existing | Select-Object -Last 400) -Encoding UTF8 -ErrorAction SilentlyContinue
        }
    } catch {
    }
}

function Test-IsAdmin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-TargetMonitors {
    $monitors = @(Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue |
        Where-Object { $_.FriendlyName -like '*Generic*' })

    if ($monitors.Count -gt 0) {
        return $monitors
    }

    return @(Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue)
}

if ($ResultFile) {
    Write-Log "Elevated branch start. Action=$Action ResultFile=$ResultFile"

    function Write-Result {
        param([string]$Value)
        try {
            Set-Content -Path $ResultFile -Value $Value -Encoding ASCII -ErrorAction Stop
            Write-Log "Wrote result '$Value' to $ResultFile"
        } catch {
            Write-Log "FAILED to write result '$Value' to $ResultFile : $($_.Exception.Message)"
        }
    }

    try {
        $monitors = Get-TargetMonitors

        if (-not $monitors -or $monitors.Count -eq 0) {
            Write-Log 'No Class=Monitor devices found on this system.'
            Write-Result 'not_found'
            exit 0
        }

        Write-Log ("Targeting {0} device(s): {1}" -f $monitors.Count, (($monitors | ForEach-Object { $_.FriendlyName }) -join ', '))

        $failures = @()
        foreach ($m in $monitors) {
            try {
                if ($Action -eq 'Disable') {
                    Disable-PnpDevice -InstanceId $m.InstanceId -Confirm:$false -ErrorAction Stop
                } else {
                    Enable-PnpDevice -InstanceId $m.InstanceId -Confirm:$false -ErrorAction Stop
                }
            } catch {
                $failures += "$($m.FriendlyName): $($_.Exception.Message)"
                Write-Log "FAILED on '$($m.FriendlyName)': $($_.Exception.Message)"
            }
        }

        if ($failures.Count -eq $monitors.Count) {
            Write-Log ("All devices failed: " + ($failures -join ' | '))
            Write-Result 'error'
        } elseif ($Action -eq 'Disable') {
            Write-Result 'disabled'
        } else {
            Write-Result 'enabled'
        }
    } catch {
        Write-Log "Unhandled error in elevated branch: $($_.Exception.Message)"
        Write-Result 'error'
    }
    exit 0
}

try {
    if (-not (Test-Path $sharedDir)) {
        New-Item -Path $sharedDir -ItemType Directory -Force | Out-Null
    }
} catch {
    $sharedDir = $env:TEMP
}

$resultPath = Join-Path $sharedDir ("driver-result_{0}.txt" -f ([guid]::NewGuid().ToString('N')))
if (Test-Path $resultPath) { Remove-Item $resultPath -Force -ErrorAction SilentlyContinue }

Write-Log "Launcher start. Action=$Action IsAdmin=$(Test-IsAdmin) ResultPath=$resultPath"

if (Test-IsAdmin) {
    Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -Wait -ArgumentList @(
        '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
        '-File', "`"$PSCommandPath`"",
        '-Action', $Action,
        '-ResultFile', "`"$resultPath`""
    ) | Out-Null
} else {
    try {
        Start-Process -FilePath 'powershell.exe' -Verb RunAs -WindowStyle Hidden -Wait -ArgumentList @(
            '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
            '-File', "`"$PSCommandPath`"",
            '-Action', $Action,
            '-ResultFile', "`"$resultPath`""
        ) | Out-Null
    } catch {
        $msg = $_.Exception.Message
        Write-Log "Start-Process -Verb RunAs threw: $msg"
        if ($msg -match 'cancel' -or $_.Exception.HResult -eq -2147023673) {
            Write-Output 'denied'
        } else {
            Write-Output 'error'
        }
        exit 0
    }
}

if (Test-Path $resultPath) {
    $result = (Get-Content -Path $resultPath -Raw).Trim()
    Write-Log "Launcher read result: '$result'"
    Remove-Item -Path $resultPath -Force -ErrorAction SilentlyContinue
    Write-Output $result
} else {
    Write-Log 'Launcher found no result file after elevated process exited, treating as denied.'
    Write-Output 'denied'
}
