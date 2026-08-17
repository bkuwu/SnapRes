$ErrorActionPreference = 'SilentlyContinue'

$monitors = @(Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue |
    Where-Object { $_.FriendlyName -like '*Generic*' })

if ($monitors.Count -eq 0) {
    $monitors = @(Get-PnpDevice -Class Monitor -ErrorAction SilentlyContinue)
}

if ($monitors.Count -eq 0) {
    Write-Output 'not_found'
    exit 0
}

$stillActive = $monitors | Where-Object { $_.Status -eq 'OK' }

if ($stillActive) {
    Write-Output 'enabled'
} else {
    Write-Output 'disabled'
}
