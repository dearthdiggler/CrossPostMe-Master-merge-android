param(
    [Parameter(Mandatory=$true)][string]$Host,
    [Parameter(Mandatory=$true)][string]$User,
    [Parameter(Mandatory=$true)][string]$Password,
    [string]$RemotePath = 'public',
    [string]$LocalPath = 'app/frontend/build'
)

function Test-WinSCP {
    $winscp = "C:\\Program Files (x86)\\WinSCP\\WinSCP.exe"
    return (Test-Path $winscp)
}

if (-not (Test-Path $LocalPath)) {
    Write-Error "Local path '$LocalPath' not found. Run 'yarn build' in app/frontend first."
    exit 2
}

if (Test-WinSCP) {
    $winscp = "C:\\Program Files (x86)\\WinSCP\\WinSCP.exe"
    $script = @"
open ftp://$User:`$Password@$Host/ -passive=on
option batch abort
option confirm off
mirror -delete `"$LocalPath`" `"$RemotePath`"
close
exit
"@
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -Path $tmp -Value $script -Encoding ASCII
    & "$winscp" "/script=$tmp"
    $rc = $LASTEXITCODE
    Remove-Item $tmp -ErrorAction SilentlyContinue
    if ($rc -ne 0) { Write-Error "WinSCP mirror failed (exit $rc)"; exit $rc }
    Write-Host "Upload completed with WinSCP." -ForegroundColor Green
    exit 0
}

Write-Host "WinSCP not found — using FTP fallback. Ensure remote directories exist." -ForegroundColor Yellow
Get-ChildItem -Path $LocalPath -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring((Get-Item $LocalPath).FullName.Length).TrimStart('\') -replace '\\','/'
    $uri = "ftp://$Host/$RemotePath/$relative"
    try {
        $req = [System.Net.FtpWebRequest]::Create($uri)
        $req.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $req.Credentials = New-Object System.Net.NetworkCredential($User,$Password)
        $req.UseBinary = $true
        $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
        $req.ContentLength = $bytes.Length
        $stream = $req.GetRequestStream()
        $stream.Write($bytes,0,$bytes.Length)
        $stream.Close()
        $resp = $req.GetResponse()
        $resp.Close()
        Write-Host "Uploaded: $relative"
    } catch {
        Write-Warning "Failed to upload $relative - $_"
    }
}
