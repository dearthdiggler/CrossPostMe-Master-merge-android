$site='https://www.crosspostme.com'
try{
  $r = Invoke-WebRequest -Uri $site -UseBasicParsing -ErrorAction Stop -TimeoutSec 20
  Write-Output "STATUS=$($r.StatusCode)"
  $content = $r.Content
  $hasRoot = $content -match '<div id="root">' -or $content -match '<div id="app">'
  Write-Output "HAS_ROOT_ELEMENT=$hasRoot"
  $len = [math]::Min(1000, $content.Length)
  Write-Output "SNIPPET:\n$($content.Substring(0,$len))"
  # find /static/ occurrences
  $assets = @()
  $pos=0
  while($true){
    $idx = $content.IndexOf('/static/',$pos)
    if($idx -lt 0){break}
    # extract token until next quote or space
    $end = $content.IndexOfAny(@('"','''',' '),$idx)
    if($end -lt 0){ $end = $idx+200 }
    $token = $content.Substring($idx, $end-$idx)
    if(-not ($assets -contains $token)){$assets += $token}
    $pos = $idx + 8
    if($assets.Count -ge 5){break}
  }
  Write-Output "ASSETS_FOUND_COUNT=$($assets.Count)"
  $i=0
  foreach($a in $assets){ $i++; Write-Output "ASSET_$i=$a" }
}catch{ Write-Output "ERROR=$($_.Exception.Message)" }
