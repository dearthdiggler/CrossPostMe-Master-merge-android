$site = 'https://www.crosspostme.com'
try {
    $r = Invoke-WebRequest -Uri $site -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
    Write-Output "ROOT_STATUS=$($r.StatusCode)"
    $hasRoot = ($r.Content -match '<div id="root">' -or $r.Content -match '<div id="app">')
    Write-Output "ROOT_HAS_APP_ELEMENT=$hasRoot"

    $re = [regex] '<script[^>]+src=["'"'](?<src>[^"'"']+)["'"']'
    $matches = $re.Matches($r.Content)
    $assets = @()
    foreach ($m in $matches) { $assets += $m.Groups['src'].Value }
    Write-Output "ASSET_COUNT=$($assets.Count)"
    if ($assets.Count -gt 0) {
        $first = $assets[0]
        Write-Output "FIRST_ASSET=$first"
        if ($first.StartsWith('/')) { $assetUrl = $site.TrimEnd('/') + $first } elseif ($first -match '^http') { $assetUrl = $first } else { $assetUrl = $site.TrimEnd('/') + '/' + $first }
        Write-Output "ASSET_URL=$assetUrl"
        try {
            $h = Invoke-WebRequest -Uri $assetUrl -Method Head -ErrorAction Stop -TimeoutSec 20
            Write-Output "ASSET_STATUS=$($h.StatusCode)"
            Write-Output "ASSET_CONTENT_TYPE=$($h.Headers['content-type'])"
        } catch { Write-Output "ASSET_HEAD_ERROR=$($_.Exception.Message)" }
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
    $port = ($uri.Scheme -eq 'https') ? 443 : 80
    $t = Test-NetConnection -ComputerName $host -Port $port -WarningAction SilentlyContinue
    Write-Output "TCP_PORT_$port_OPEN=$($t.TcpTestSucceeded)"
} catch { Write-Output "ROOT_ERROR=$($_.Exception.Message)" }
