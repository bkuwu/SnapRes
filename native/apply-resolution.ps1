param(
    [Parameter(Mandatory = $true)][int]$Width,
    [Parameter(Mandatory = $true)][int]$Height
)

$ErrorActionPreference = 'Stop'

$src = @"
using System;
using System.Runtime.InteropServices;

public class SnapResDisplay
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct DEVMODE
    {
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmDeviceName;
        public short dmSpecVersion;
        public short dmDriverVersion;
        public short dmSize;
        public short dmDriverExtra;
        public int dmFields;
        public int dmPositionX;
        public int dmPositionY;
        public int dmDisplayOrientation;
        public int dmDisplayFixedOutput;
        public short dmColor;
        public short dmDuplex;
        public short dmYResolution;
        public short dmTTOption;
        public short dmCollate;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)]
        public string dmFormName;
        public short dmLogPixels;
        public int dmBitsPerPel;
        public int dmPelsWidth;
        public int dmPelsHeight;
        public int dmDisplayFlags;
        public int dmDisplayFrequency;
    }

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int ChangeDisplaySettingsW(ref DEVMODE devMode, int flags);

    public const int DM_PELSWIDTH  = 0x80000;
    public const int DM_PELSHEIGHT = 0x100000;

    public static int Apply(int width, int height)
    {
        DEVMODE dm = new DEVMODE();
        dm.dmSize = (short)Marshal.SizeOf(typeof(DEVMODE));
        dm.dmPelsWidth = width;
        dm.dmPelsHeight = height;
        dm.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT;
        return ChangeDisplaySettingsW(ref dm, 0);
    }
}
"@

$cacheDir = Join-Path $env:ProgramData 'SnapRes'
$dllPath = Join-Path $cacheDir 'SnapResDisplay.dll'

try {
    if (Test-Path $dllPath) {
        Add-Type -Path $dllPath -ErrorAction Stop
    } else {
        if (-not (Test-Path $cacheDir)) {
            New-Item -Path $cacheDir -ItemType Directory -Force | Out-Null
        }
        Add-Type -TypeDefinition $src -Language CSharp -OutputAssembly $dllPath -OutputType Library -ErrorAction Stop
    }
} catch {
    Add-Type -TypeDefinition $src -Language CSharp -ErrorAction Stop
}

$result = [SnapResDisplay]::Apply($Width, $Height)
Write-Output $result
