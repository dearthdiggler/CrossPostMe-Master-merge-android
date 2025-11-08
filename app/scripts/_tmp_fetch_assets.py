import re
import urllib.request

u = "https://www.crosspostme.com/"
req = urllib.request.Request(u, headers={"User-Agent": "python-urllib/3"})
with urllib.request.urlopen(req, timeout=20) as r:
    html = r.read().decode("utf-8")
print("LEN", len(html))
js = re.search(r'src=["\'](/static/js/(main\.[^"\']+\.js))["\']', html)
css = re.search(r'href=["\'](/static/css/(main\.[^"\']+\.css))["\']', html)
print("JS", js.group(1) if js else None)
print("CSS", css.group(1) if css else None)
