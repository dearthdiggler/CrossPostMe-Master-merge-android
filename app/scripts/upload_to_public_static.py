#!/usr/bin/env python3
import ftplib
import os

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_base = r"c:\Users\johnd\Desktop\marketwiz\app\frontend\build"
ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)


def ensure(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


# upload index
with open(os.path.join(local_base, "index.html"), "rb") as fh:
    ensure(ftp, "public_html")
    ftp.cwd("public_html")
    print("Uploading index.html")
    ftp.storbinary("STOR index.html", fh)

# upload css/js
for sub in ["static/css", "static/js"]:
    local_dir = os.path.join(local_base, *sub.split("/"))
    remote_dir = "public_html/" + sub
    ensure(ftp, remote_dir)
    try:
        ftp.cwd(remote_dir)
    except Exception:
        ftp.mkd(remote_dir)
        ftp.cwd(remote_dir)
    for fname in os.listdir(local_dir):
        local_path = os.path.join(local_dir, fname)
        if os.path.isfile(local_path):
            print("Uploading", local_path, "->", remote_dir + "/" + fname)
            with open(local_path, "rb") as fh:
                ftp.storbinary("STOR " + fname, fh)

# upload other root files
for fname in ["asset-manifest.json", "favicon.svg"]:
    local_path = os.path.join(local_base, fname)
    if os.path.isfile(local_path):
        print("Uploading", local_path, "-> public_html/" + fname)
        with open(local_path, "rb") as fh:
            ftp.cwd("public_html")
            ftp.storbinary("STOR " + fname, fh)

# upload .htaccess SPA fallback
from io import BytesIO

ftp.cwd("public_html")
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"

ftp.cwd("public_html")
print("Uploading .htaccess")
ftp.storbinary("STOR .htaccess", BytesIO(ht.encode("utf-8")))

ftp.quit()
print("Done")
