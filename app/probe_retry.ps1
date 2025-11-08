$sites = @('https://www.crosspostme.com','http://www.crosspostme.com')
$uas = @(
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/119.0',
  'curl/7.85.0',
  'Googlebot/2.1 (+http://www.google.com/bot.html)'
)
foreach ($site in $sites) {
  Write-Output "\n=== SITE: $site ==="
  foreach ($ua in $uas) {
    Write-Output "-- UA: $ua"
    $hdr = @{ 'User-Agent' = $ua }
    try {
      $r = Invoke-WebRequest -Uri $site -Headers $hdr -UseBasicParsing -ErrorAction Stop -TimeoutSec 15
      Write-Output "GET => $($r.StatusCode)"
      if ($r.StatusCode -lt 400) {
        $snippet = $r.Content.Substring(0,[math]::Min(400,$r.Content.Length)) -replace "`r`n"," `n"
        Write-Output "BODY_SNIPPET: $snippet"
      } else { Write-Output "BODY NOT FETCHED (status $($r.StatusCode))" }
      if ($r.Headers) { Write-Output "Headers: `n$($r.Headers | Out-String)" }
    } catch {
      Write-Output "GET_ERROR: $($_.Exception.Message)"
      if ($_.Exception.Response -and $_.Exception.Response.Headers) {
        Write-Output "Error Response Headers: $($_.Exception.Response.Headers)"
      }
    }
    # HEAD
    try {
      $h = Invoke-WebRequest -Uri $site -Method Head -Headers $hdr -ErrorAction Stop -TimeoutSec 10
      Write-Output "HEAD => $($h.StatusCode)"
      if ($h.Headers) { Write-Output "HEAD Headers: `n$($h.Headers | Out-String)" }
    } catch {
      Write-Output "HEAD_ERROR: $($_.Exception.Message)"
    }
  }
}
# TCP checks
Write-Output "\n=== TCP CHECKS ==="
foreach ($s in @('www.crosspostme.com')) {
  try {
    $t443 = Test-NetConnection -ComputerName $s -Port 443 -WarningAction SilentlyContinue
    Write-Output "$s:443 -> $($t443.TcpTestSucceeded)"
  } catch {
    Write-Output "TCP443_ERROR: $($_.Exception.Message)"
  }
  try {
    $t80 = Test-NetConnection -ComputerName $s -Port 80 -WarningAction SilentlyContinue
    Write-Output "$s:80 -> $($t80.TcpTestSucceeded)"
  } catch {
    Write-Output "TCP80_ERROR: $($_.Exception.Message)"
  }
}
