$ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
$hosts = @(
    'https://www.crosspostme.com',
    'https://crosspostme.com',
    'http://www.crosspostme.com',
    'http://crosspostme.com',
    'https://www.crosspostme.com/index.html',
    'https://www.crosspostme.com/frontendbuild1018645.zip'
)
foreach ($site in $hosts) {
    Write-Output "\n--- Checking: $site ---"
    try {
        $h = Invoke-WebRequest -Uri $site -Method Head -Headers @{ 'User-Agent' = $ua } -ErrorAction Stop -TimeoutSec 15
        Write-Output "HEAD: Status=$($h.StatusCode) | Content-Type=$($h.Headers['content-type'])"
    } catch {
        Write-Output "HEAD ERROR: $($_.Exception.Response.StatusCode.Value__ 2>$null)" 2>$null
        # fallback to GET to capture body or status
        try {
            $g = Invoke-WebRequest -Uri $site -Headers @{ 'User-Agent' = $ua } -UseBasicParsing -ErrorAction Stop -TimeoutSec 15
            Write-Output "GET: Status=$($g.StatusCode)"
            $snippet = if ($g.Content.Length -gt 500) { $g.Content.Substring(0,500) } else { $g.Content }
            Write-Output "BODY_SNIPPET: $snippet"
        } catch {
            # Try to extract status code from exception response if available
            $msg = $_.Exception.Message
            if ($_.Exception.Response -ne $null) {
                try { $code = $_.Exception.Response.StatusCode.Value__ } catch { $code = 'unknown' }
                Write-Output "GET ERROR: StatusCode=$code | Message=$msg"
            } else {
                Write-Output "GET ERROR: $msg"
            }
        }
    }
}
