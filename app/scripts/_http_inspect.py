import urllib.error
import urllib.request

paths = [
    "/pricing",
    "/pricing/",
    "/pricing/index.html",
    "/company",
    "/company/",
    "/company/index.html",
]
for p in paths:
    url = "https://www.crosspostme.com" + p
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print("\n===", p, "STATUS", r.status)
            for k, v in r.getheaders():
                if k.lower() in (
                    "server",
                    "content-type",
                    "cache-control",
                    "x-cache",
                    "x-litespeed",
                    "location",
                ):
                    print(k + ":", v)
            body = r.read(2000).decode("utf-8", errors="replace")
            print("BODY PREVIEW:\n", body[:1000])
    except urllib.error.HTTPError as e:
        print("\n===", p, "HTTPERROR", e.code)
        try:
            body = e.read(2000).decode("utf-8", errors="replace")
            print("BODY PREVIEW:\n", body[:1000])
        except Exception:
            print("No body")
    except Exception as ex:
        print("\n===", p, "ERROR", ex)
