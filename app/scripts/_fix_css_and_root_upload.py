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
    print("Local build missing", local_build)
    sys.exit(2)
local_css = os.path.join(local_build, "static", "css")
ftp = ftplib.FTP()
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


# ensure static/css at root
ensure("static")
ensure("static/css")
try:
    ftp.cwd("static/css")
except Exception:
    ftp.cwd("/")
    ftp.cwd("static/css")
# upload css files
if os.path.isdir(local_css):
    for fname in os.listdir(local_css):
        src = os.path.join(local_css, fname)
        if os.path.isfile(src):
            print("Uploading CSS", fname)
            with open(src, "rb") as fh:
                ftp.storbinary("STOR " + fname, fh)
# upload root assets to ftp root
ftp.cwd("/")
for fname in ["index.html", "asset-manifest.json", "favicon.svg", "diagrams.html"]:
    src = os.path.join(local_build, fname)
    if os.path.isfile(src):
        print("Uploading root", fname)
        with open(src, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)
# upload .htaccess at root
ht = "RewriteEngine On\nRewriteBase /\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("Uploading .htaccess to root")
ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
ftp.quit()
print("Done")
