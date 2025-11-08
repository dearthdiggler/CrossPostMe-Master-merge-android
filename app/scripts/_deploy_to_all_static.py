"""Find all remote directories on the FTP under `public_html` that contain 'static' in their path
and upload local build/static/js and build/static/css contents to the corresponding remote paths.
Usage:
  python _deploy_to_all_static.py --host HOST --user USER --password PASS --local BUILD_DIR
"""

import argparse
import ftplib
import io
import os

p = argparse.ArgumentParser()
p.add_argument("--host", required=True)
p.add_argument("--user", required=True)
p.add_argument("--password", required=True)
p.add_argument("--local", required=True)
args = p.parse_args()

host = args.host
user = args.user
passwd = args.password
local_build = args.local

if not os.path.isdir(local_build):
    print("Local build dir not found:", local_build)
    raise SystemExit(2)

local_js_dir = os.path.join(local_build, "static", "js")
local_css_dir = os.path.join(local_build, "static", "css")

ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)

# BFS to find paths under public_html
queue = ["public_html"]
seen = set()
static_dirs = set()

while queue:
    cur = queue.pop(0)
    if cur in seen:
        continue
    seen.add(cur)
    try:
        entries = ftp.nlst(cur)
    except Exception:
        # can't list this path
        continue
    for ent in entries:
        # Normalize
        ent = ent.rstrip("/")
        if "/static" in ent and ent.endswith("static"):
            static_dirs.add(ent)
        # enqueue directories heuristically: entries without a dot in their last part are likely dirs
        name = ent.split("/")[-1]
        if name not in (".", "..") and "." not in name:
            queue.append(ent)

print("Found static dirs:", static_dirs)


# helper to ensure remote dir exists (creates nested dirs)
def ensure_remote(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


# upload files into each static dir's js and css subdirs
for sd in sorted(static_dirs):
    remote_js = sd.rstrip("/") + "/js"
    remote_css = sd.rstrip("/") + "/css"

    print("\nPreparing remote:", sd)
    ensure_remote(ftp, remote_js)
    ensure_remote(ftp, remote_css)

    try:
        ftp.cwd(remote_js)
    except Exception:
        pass
    # upload JS files
    if os.path.isdir(local_js_dir):
        for fname in os.listdir(local_js_dir):
            local_path = os.path.join(local_js_dir, fname)
            if os.path.isfile(local_path):
                print("Uploading JS", local_path, "->", remote_js + "/" + fname)
                with open(local_path, "rb") as fh:
                    ftp.storbinary("STOR " + fname, fh)

    # upload CSS files
    if os.path.isdir(local_css_dir):
        try:
            ftp.cwd(remote_css)
        except Exception:
            pass
        for fname in os.listdir(local_css_dir):
            local_path = os.path.join(local_css_dir, fname)
            if os.path.isfile(local_path):
                print("Uploading CSS", local_path, "->", remote_css + "/" + fname)
                with open(local_path, "rb") as fh:
                    ftp.storbinary("STOR " + fname, fh)

# also upload index.html and root assets into public_html (primary webroot)
print("\nUploading index and root assets to public_html")
ensure_remote(ftp, "public_html")
ftp.cwd("public_html")
for fname in ["index.html", "asset-manifest.json", "favicon.svg", "diagrams.html"]:
    local_path = os.path.join(local_build, fname)
    if os.path.isfile(local_path):
        print("Uploading root", local_path, "-> public_html/" + fname)
        with open(local_path, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)

# add simple .htaccess SPA fallback
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
try:
    ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
except Exception:
    try:
        # attempt to write into public_html/.htaccess explicitly
        ftp.cwd("public_html")
        import io

        ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
    except Exception as e:
        print("Could not upload .htaccess:", e)

ftp.quit()
print("\nDone")
