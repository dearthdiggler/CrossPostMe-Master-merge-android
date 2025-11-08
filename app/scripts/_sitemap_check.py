#!/usr/bin/env python3
"""Crawl the homepage and report where every anchor/button navigates.
Classify links as: public (200), redirect-to-login (302->/login), protected (401), missing (404), or non-navigating (javascript, #).
"""
import ssl
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

BASE = "https://www.crosspostme.com"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.buttons = []
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            href = attrs.get("href")
            if href:
                self.links.append(href)
        if tag == "button":
            # check onclick
            onclick = attrs.get("onclick")
            if onclick:
                self.buttons.append(onclick)
            # sometimes button inside form with formaction
            fa = attrs.get("formaction")
            if fa:
                self.buttons.append(fa)
        if tag == "form":
            action = attrs.get("action")
            method = attrs.get("method")
            if method is not None:
                method = method.upper()
            else:
                method = "GET"
            self.forms.append((action, method))


# fetch homepage
ctx = ssl.create_default_context()
req = urllib.request.Request(BASE + "/", headers={"User-Agent": "python-urllib/3"})
html = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode("utf-8")
parser = LinkParser()
parser.feed(html)

raw_links = parser.links
raw_buttons = parser.buttons
raw_forms = parser.forms


# normalize links
def normalize(href):
    if not href:
        return None
    href = href.strip()
    if href.lower().startswith("javascript:"):
        return None
    if href.startswith("#"):
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    # relative
    return urllib.parse.urljoin(BASE + "/", href)


candidates = set()
for h in raw_links:
    n = normalize(h)
    if n:
        candidates.add(n)
for b in raw_buttons:
    # attempt to extract quoted URL inside onclick patterns like location.href='/x' or window.location='/x'
    import re

    m = re.search(
        r"(?:location|window.location|location.href)\s*[:=]\s*['\"]([^'\"]+)['\"]", b
    )
    if m:
        n = normalize(m.group(1))
        if n:
            candidates.add(n)
    else:
        # if it's a full url in button/formaction
        if b.startswith("/") or b.startswith("http"):
            n = normalize(b)
            if n:
                candidates.add(n)
for action, method in raw_forms:
    if action:
        n = normalize(action)
        if n:
            candidates.add(n)

# remove duplicates and home
candidates = sorted(candidates)
print("Found", len(candidates), "navigable targets")

# function to check URL
import urllib.error


def check_url(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "python-urllib/3"})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        code = getattr(resp, "status", None) or resp.getcode()
        final = resp.geturl()
        return code, final
    except urllib.error.HTTPError as e:
        return e.code, getattr(e, "url", u)
    except Exception as e:
        return None, str(e)


results = []
for u in candidates:
    code, final = check_url(u)
    note = ""
    if code in (301, 302, 303, 307, 308):
        note = "redirect"
    elif code == 200:
        note = "ok"
    elif code == 404:
        note = "missing"
    elif code == 401:
        note = "auth required"
    elif code is None:
        note = final
    results.append((u, code, final, note))

# print nicely
for u, code, final, note in results:
    print(u, code, "->", final, note)

# also print non-navigating anchors
non_nav = [h for h in raw_links if not normalize(h)]
if non_nav:
    print("\nNon-navigating hrefs (javascript/#):")
    for h in non_nav[:50]:
        print(" ", h)

print("\nForms:")
for a, m in raw_forms:
    print(" ", a, m)

print("\nButtons with onclick (raw):")
for b in raw_buttons:
    print(" ", b)
