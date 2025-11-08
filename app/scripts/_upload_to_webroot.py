#!/usr/bin/env python3
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

ftp = ftplib.FTP()
print("Connecting", host)
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)


def ensure(path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


# targets
root = "public_html"
js_remote = f"{root}/static/js"
css_remote = f"{root}/static/css"

ensure(root)
ensure(f"{root}/static")
ensure(js_remote)
ensure(css_remote)

# upload root files
for fname in ["index.html", "asset-manifest.json", "favicon.svg", "diagrams.html"]:
    src = os.path.join(local_build, fname)
    if os.path.isfile(src):
        print("Upload root", fname)
        with open(src, "rb") as fh:
            ftp.storbinary(f"STOR {root}/{fname}", fh)

# upload js
local_js = os.path.join(local_build, "static", "js")
if os.path.isdir(local_js):
    for fname in os.listdir(local_js):
        src = os.path.join(local_js, fname)
        if os.path.isfile(src):
            print("Upload JS", fname)
            # store into remote path
            with open(src, "rb") as fh:
                # change to remote dir and store
                try:
                    ftp.cwd(js_remote)
                except Exception:
                    ensure(js_remote)
                    ftp.cwd(js_remote)
                ftp.storbinary(f"STOR {fname}", fh)

# upload css
local_css = os.path.join(local_build, "static", "css")
if os.path.isdir(local_css):
    for fname in os.listdir(local_css):
        src = os.path.join(local_css, fname)
        if os.path.isfile(src):
            print("Upload CSS", fname)
            try:
                ftp.cwd(css_remote)
            except Exception:
                ensure(css_remote)
                ftp.cwd(css_remote)
            with open(src, "rb") as fh:
                ftp.storbinary(f"STOR {fname}", fh)

# upload .htaccess to root
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("Upload .htaccess")
ftp.cwd(root)
ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))

ftp.quit()
print("Upload finished")
