#!/usr/bin/env python3
"""Find the remote served static dir and upload current build assets to it.
Usage: python fix_and_upload_assets.py --host HOST --user USER --password PASS --local-build PATH
"""
import argparse
import fnmatch
import ftplib
import os
import sys

p = argparse.ArgumentParser()
p.add_argument("--host", required=True)
p.add_argument("--user", required=True)
p.add_argument("--password", required=True)
p.add_argument("--local-build", required=True)
args = p.parse_args()

host = args.host
user = args.user
passwd = args.password
local_build = os.path.abspath(args.local_build)

if not os.path.isdir(local_build):
    print("Local build not found:", local_build)
    sys.exit(2)

print("Connecting to FTP", host)
ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)

# Search remote tree for any main.*.js files and list their directories
candidates = set()
try:
    entries = ftp.nlst("public_html")
except Exception:
    entries = ftp.nlst()

# We'll walk recursively using NLST where possible
from collections import deque

queue = deque(["public_html"])
from collections import deque

queue = deque(["public_html"])
visited = set()
while queue:
    path = queue.popleft()
    if path in visited:
        continue
    visited.add(path)
    try:
        items = ftp.nlst(path)
    except Exception:
        continue
    for it in items:
        # items can be returned as 'public_html/file' or 'file'
        name = it
        if name.endswith("/"):
            name = name[:-1]
        # If it's a directory, schedule deeper; heuristic: if it appears to be a directory name (no dot) or path contains path separators
        try:
            ftp.cwd(it)
            # it's a directory
            queue.append(it)
            ftp.cwd("/")
        except Exception:
            # file-like
            basename = os.path.basename(it)
            if fnmatch.fnmatch(basename, "main.*.js"):
                dirpath = os.path.dirname(it)
                if not dirpath:
                    dirpath = "public_html"
                candidates.add(dirpath)

print("Candidate directories containing main.*.js:", candidates)

# Heuristic: prefer 'public_html/static/js' if present, else any candidate
preferred = None
for c in candidates:
    if (
        c.endswith("public_html/static/js")
        or c.endswith("public_html/static/js".lstrip("/"))
        or c.endswith("static/js")
    ):
        preferred = c
        break
if not preferred and candidates:
    preferred = sorted(candidates)[0]

if not preferred:
    # fallback: ensure public_html/static/js exists and use that
    preferred = "public_html/static/js"

print("Using remote JS dir:", preferred)
# ensure corresponding css dir
if preferred.endswith("/js"):
    css_remote_dir = preferred[:-3] + "css"
else:
    css_remote_dir = preferred + "/../css"


# helper to ensure remote dir exists
def ensure_remote_dir(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


# upload files from local static/js to preferred
local_js_dir = os.path.join(local_build, "static", "js")
local_css_dir = os.path.join(local_build, "static", "css")
print("Local JS dir:", local_js_dir)
print("Local CSS dir:", local_css_dir)

# Ensure remote dirs
ensure_remote_dir(ftp, preferred)
ensure_remote_dir(ftp, css_remote_dir)

# Change to remote js dir and upload files
try:
    ftp.cwd(preferred)
except Exception:
    ensure_remote_dir(ftp, preferred)
    ftp.cwd(preferred)

for fname in os.listdir(local_js_dir):
    local_path = os.path.join(local_js_dir, fname)
    if os.path.isfile(local_path):
        print("Uploading js", local_path, "->", preferred + "/" + fname)
        with open(local_path, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# Upload css
try:
    ftp.cwd(css_remote_dir)
except Exception:
    ensure_remote_dir(ftp, css_remote_dir)
    ftp.cwd(css_remote_dir)
for fname in os.listdir(local_css_dir):
    local_path = os.path.join(local_css_dir, fname)
    if os.path.isfile(local_path):
        print("Uploading css", local_path, "->", css_remote_dir + "/" + fname)
        with open(local_path, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# Upload index.html to public_html root
with open(os.path.join(local_build, "index.html"), "rb") as fh:
    print("Uploading index.html to public_html/index.html")
    try:
        ftp.cwd("public_html")
    except Exception:
        ensure_remote_dir(ftp, "public_html")
        ftp.cwd("public_html")
    ftp.storbinary("STOR index.html", fh)

# Upload .htaccess SPA fallback
ht = b"RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("Uploading .htaccess to public_html/.htaccess")
import io

if isinstance(ht, bytes):
    fp = io.BytesIO(ht)
else:
    fp = io.BytesIO(str(ht).encode("utf-8"))
ftp.storbinary("STOR .htaccess", fp)

ftp.quit()
print("Upload complete")
