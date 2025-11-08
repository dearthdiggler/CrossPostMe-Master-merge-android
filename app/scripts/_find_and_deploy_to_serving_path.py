#!/usr/bin/env python3
"""Find existing served static asset path (older build) and deploy our new build files into the same path.
This avoids uploading into nested/duplicate public_html copies.
"""
import ftplib
import io
import os
import sys

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_build = r"C:\Users\johnd\Desktop\marketwiz\app\frontend\build"

if not os.path.isdir(local_build):
    print("Local build missing:", local_build)
    sys.exit(2)

target_filename = "main.d59929a8.js"  # older asset we saw being served

ftp = ftplib.FTP()
print("Connecting", host)
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)

# BFS search under public_html and root
from collections import deque

queue = deque(["public_html", "."])
from collections import deque

queue = deque(["public_html", "."])
seen = set()
found = None
max_entries = 2000
entries_checked = 0

while queue and entries_checked < max_entries and not found:
    cur = queue.popleft()
    if cur in seen:
        continue
    seen.add(cur)
    try:
        items = ftp.nlst(cur)
    except Exception:
        continue
    for it in items:
        entries_checked += 1
        # normalize
        name = it.split("/")[-1]
        if name == target_filename:
            found = it
            break
        # enqueue directories heuristically
        if name not in (".", "..") and "." not in name:
            queue.append(it)

if not found:
    print("Did not find", target_filename, "within", entries_checked, "entries")
    ftp.quit()
    sys.exit(1)

print("Found served asset at", found)
# compute asset_dir and webroot
asset_dir = found.rsplit("/", 1)[0]
# webroot = up to /static
if "/static" in asset_dir:
    webroot = asset_dir.split("/static", 1)[0]
else:
    webroot = asset_dir
if webroot.startswith("./"):
    webroot = webroot[2:]
print("Asset dir:", asset_dir)
print("Webroot:", webroot)

# Prepare remote dirs
try:
    ftp.cwd(asset_dir)
except Exception:
    # try to create
    parts = [p for p in asset_dir.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass
    ftp.cwd(asset_dir)

# upload js files into asset_dir
local_js = os.path.join(local_build, "static", "js")
for fname in os.listdir(local_js):
    src = os.path.join(local_js, fname)
    if os.path.isfile(src):
        print("Uploading JS", fname, "->", asset_dir)
        with open(src, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# css remote path: webroot + /static/css
remote_css = webroot.rstrip("/") + "/static/css"
# ensure remote css dir
parts = [p for p in remote_css.replace("\\", "/").split("/") if p]
cur = ""
for p in parts:
    cur = f"{cur}/{p}" if cur else p
    try:
        ftp.mkd(cur)
    except Exception:
        pass
# upload css
local_css = os.path.join(local_build, "static", "css")
try:
    ftp.cwd(remote_css)
except Exception:
    ftp.cwd(webroot)
for fname in os.listdir(local_css):
    src = os.path.join(local_css, fname)
    if os.path.isfile(src):
        print("Uploading CSS", fname, "->", remote_css)
        with open(src, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# upload root files to webroot
parts = [p for p in webroot.replace("\\", "/").split("/") if p]
cur = ""
for p in parts:
    cur = f"{cur}/{p}" if cur else p
try:
    ftp.cwd(cur)
except Exception:
    # create
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass
    ftp.cwd(cur)
for fname in ["index.html", "asset-manifest.json", "favicon.svg", "diagrams.html"]:
    src = os.path.join(local_build, fname)
    if os.path.isfile(src):
        print("Uploading root file", fname, "->", cur)
        with open(src, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# write .htaccess
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("Uploading .htaccess to", cur)
ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))

ftp.quit()
print("Done")
