$site = 'https://www.crosspostme.com'
$headers = @{
    'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
Write-Output "Using UA: $($headers['User-Agent'])"
try {
    $r = Invoke-WebRequest -Uri $site -Headers $headers -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
    Write-Output "ROOT_STATUS=$($r.StatusCode)"
    $len = [math]::Min(800, $r.Content.Length)
    Write-Output "BODY_SNIPPET:`n$($r.Content.Substring(0,$len))"

    $idx = $r.Content.IndexOf('/static/')
    if ($idx -ge 0) {
        $start = $r.Content.LastIndexOf('"', $idx)
        if ($start -lt 0) { $start = $r.Content.LastIndexOf("'", $idx) }
        $end = $r.Content.IndexOf('"', $idx)
        if ($end -lt 0) { $end = $r.Content.IndexOf("'", $idx) }
        if ($start -ge 0 -and $end -gt $start) {
            $src = $r.Content.Substring($start+1, $end - $start -1)
            Write-Output "FIRST_ASSET=$src"
            if ($src.StartsWith('/')) { $assetUrl = $site.TrimEnd('/') + $src } elseif ($src -match '^http') { $assetUrl = $src } else { $assetUrl = $site.TrimEnd('/') + '/' + $src }
            Write-Output "ASSET_URL=$assetUrl"
            try {
                $h = Invoke-WebRequest -Uri $assetUrl -Method Head -Headers $headers -ErrorAction Stop -TimeoutSec 20
                Write-Output "ASSET_STATUS=$($h.StatusCode)"
                Write-Output "ASSET_CONTENT_TYPE=$($h.Headers['content-type'])"
            } catch { Write-Output "ASSET_HEAD_ERROR=$($_.Exception.Message)" }
        } else {
            Write-Output 'ASSET_PARSE_FAILED'
        }
    } else {
        Write-Output 'NO_STATIC_FOUND'
    }
} catch {
    Write-Output "ROOT_ERROR=$($_.Exception.Message)"
}
try {
    $uri = [uri]$site
    $host = $uri.Host
    $t = Test-NetConnection -ComputerName $host -Port 443 -WarningAction SilentlyContinue
    Write-Output "TCP_PORT_443_OPEN=$($t.TcpTestSucceeded)"
} catch { Write-Output "TCP_CHECK_ERROR=$($_.Exception.Message)" }
