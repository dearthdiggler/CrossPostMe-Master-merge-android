$site = 'https://www.crosspostme.com'
try {
    $r = Invoke-WebRequest -Uri $site -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
    Write-Output "ROOT_STATUS=$($r.StatusCode)"
    $hasRoot = ($r.Content -match '<div id="root">' -or $r.Content -match '<div id="app">')
    Write-Output "ROOT_HAS_APP_ELEMENT=$hasRoot"

    $html = $r.Content
    $idx = $html.IndexOf('/static/')
    if ($idx -ge 0) {
        # find the nearest quote before idx
        $start = -1
        for ($i = $idx - 1; $i -ge 0; $i--) {
            if ($html[$i] -eq '"' -or $html[$i] -eq "'") { $start = $i; break }
        }
        # find the next quote after idx
        $end = -1
        for ($i = $idx; $i -lt $html.Length; $i++) {
            if ($html[$i] -eq '"' -or $html[$i] -eq "'") { $end = $i; break }
        }
        if ($start -ne -1 -and $end -ne -1 -and $end -gt $start) {
            $src = $html.Substring($start+1, $end - $start -1)
            Write-Output "FIRST_ASSET=$src"
            if ($src.StartsWith('/')) { $assetUrl = $site.TrimEnd('/') + $src } elseif ($src -match '^http') { $assetUrl = $src } else { $assetUrl = $site.TrimEnd('/') + '/' + $src }
            Write-Output "ASSET_URL=$assetUrl"
            try {
                $h = Invoke-WebRequest -Uri $assetUrl -Method Head -ErrorAction Stop -TimeoutSec 20
                Write-Output "ASSET_STATUS=$($h.StatusCode)"
                Write-Output "ASSET_CONTENT_TYPE=$($h.Headers['content-type'])"
            } catch { Write-Output "ASSET_HEAD_ERROR=$($_.Exception.Message)" }
        } else {
            Write-Output 'ASSET_PARSE_FAILED'
        }
    } else {
        Write-Output 'NO_STATIC_FOUND'
    }

    # SPA route test
    $routeUrl = $site.TrimEnd('/') + '/_test-client-route-xyz'
    try {
        $rr = Invoke-WebRequest -Uri $routeUrl -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
        Write-Output "ROUTE_STATUS=$($rr.StatusCode)"
        $routeHas = ($rr.Content -match '<div id="root">' -or $rr.Content -match '<div id="app">')
        Write-Output "ROUTE_RETURNS_INDEX=$routeHas"
    } catch { Write-Output "ROUTE_ERROR=$($_.Exception.Message)" }

    # API checks
    $apis = @('/api/status','/api/health','/api','/status')
    foreach ($a in $apis) {
        $u = $site.TrimEnd('/') + $a
        try {
            $res = Invoke-RestMethod -Uri $u -Method Get -ErrorAction Stop -TimeoutSec 10
            Write-Output "API_OK $a -> type:$($res.GetType().Name)"
        } catch { Write-Output "API_FAIL $a -> $($_.Exception.Message)" }
    }

    # TLS/port
    $uri = [uri]$site
    $host = $uri.Host
    if ($uri.Scheme -eq 'https') { $port = 443 } else { $port = 80 }
    $t = Test-NetConnection -ComputerName $host -Port $port -WarningAction SilentlyContinue
    Write-Output "TCP_PORT_$port_OPEN=$($t.TcpTestSucceeded)"
} catch { Write-Output "ROOT_ERROR=$($_.Exception.Message)" }
