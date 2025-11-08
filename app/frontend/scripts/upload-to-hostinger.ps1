<#
Uploads the contents of app/frontend/build to Hostinger via FTP.

Usage:
  ./scripts/upload-to-hostinger.ps1 -Host ftp.example.com -User username -Password secret -RemotePath public

This script prefers WinSCP (if installed). If WinSCP is not available it falls back to a simple .NET FTP upload (less efficient).
#>

param(
    [Parameter(Mandatory=$true)][string]$Host,
    [Parameter(Mandatory=$true)][string]$User,
    [Parameter(Mandatory=$true)][string]$Password,
    [string]$RemotePath = 'public',
    [string]$LocalPath = 'app/frontend/build'
)

function Upload-WithWinSCP {
    $winscpPath = "C:\\Program Files (x86)\\WinSCP\\WinSCP.exe"
    if (-not (Test-Path $winscpPath)) { return $false }

    $script = "open ftp://$User:`$Password@$Host/ -passive=on`noption batch abort`noption confirm off`nmirror -delete `"$LocalPath`" `"$RemotePath`"`nclose`nexit"
    $temp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $temp -Value $script -Encoding ASCII

    & "$winscpPath" "/script=$temp"
    $code = $LASTEXITCODE
    Remove-Item $temp -ErrorAction SilentlyContinue
    return ($code -eq 0)
}

function Upload-FtpFallback {
    Write-Host "WinSCP not found — using basic FTP fallback. This may be slower and doesn't support mirror deletes." -ForegroundColor Yellow

    $files = Get-ChildItem -Path $LocalPath -Recurse -File
    foreach ($file in $files) {
        $relative = $file.FullName.Substring((Get-Item $LocalPath).FullName.Length).TrimStart('\') -replace '\\','/'
        $uri = "ftp://$Host/$RemotePath/$relative"

        $dir = [System.IO.Path]::GetDirectoryName($relative)
        # create remote dirs is not trivial in FtpWebRequest; skip for simplicity and assume they exist

        try {
            $req = [System.Net.FtpWebRequest]::Create($uri)
            $req.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
            $req.Credentials = New-Object System.Net.NetworkCredential($User,$Password)
            $req.UseBinary = $true
            $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
            $req.ContentLength = $bytes.Length
            $req.GetRequestStream().Write($bytes,0,$bytes.Length)
            $resp = $req.GetResponse()
            $resp.Close()
            Write-Host "Uploaded: $relative"
        } catch {
            Write-Warning "Failed: $relative -> $_"
        }
    }
}

Push-Location
Set-Location -Path (Resolve-Path .)

if (-not (Test-Path $LocalPath)) {
    Write-Error "Local path '$LocalPath' not found. Run 'yarn build' in app/frontend first."
    exit 2
}

if (Upload-WithWinSCP) {
    Write-Host "Upload completed with WinSCP." -ForegroundColor Green
} else {
    Upload-FtpFallback
    Write-Host "Upload finished (fallback)." -ForegroundColor Green
}

Pop-Location
