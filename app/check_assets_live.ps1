$site = 'https://www.crosspostme.com'
$indexPath = 'C:\Users\johnd\Desktop\marketwiz\app\frontend\build\index.html'
if (-not (Test-Path $indexPath)) { Write-Output "Index not found: $indexPath"; exit 1 }
$html = Get-Content $indexPath -Raw
$assets = @()
$pos = 0
while ($true) {
    $idx = $html.IndexOf('/static/',$pos)
    if ($idx -lt 0) { break }
    # find previous quote
    $start = $html.LastIndexOf('"', $idx)
    if ($start -lt 0) { $start = $html.LastIndexOf("'", $idx) }
    # find next quote
    $end = $html.IndexOf('"', $idx)
    if ($end -lt 0) { $end = $html.IndexOf("'", $idx) }
    if ($start -ge 0 -and $end -gt $start) {
        $src = $html.Substring($start+1, $end - $start -1)
        $assets += $src
        $pos = $end + 1
    } else {
        $pos = $idx + 8
    }
}
$assets = $assets | Select-Object -Unique
if ($assets.Count -eq 0) { Write-Output 'No /static/ assets found in index.html'; exit 0 }
Write-Output "Found $($assets.Count) unique assets in index.html"
foreach ($a in $assets) {
    $url = if ($a.StartsWith('/')) { $site.TrimEnd('/') + $a } elseif ($a -match '^https?://') { $a } else { $site.TrimEnd('/') + '/' + $a }
    try {
        $h = Invoke-WebRequest -Uri $url -Method Head -ErrorAction Stop -TimeoutSec 15
        $ct = $h.Headers['content-type'] -or ''
        Write-Output "OK     $a -> $($h.StatusCode) | $ct"
    } catch {
        Write-Output "FAIL   $a -> $($_.Exception.Message)"
    }
}
