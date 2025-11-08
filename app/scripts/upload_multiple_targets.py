#!/usr/bin/env python3
import ftplib
import os

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_base = r"c:\Users\johnd\Desktop\marketwiz\app\frontend\build"

targets = [
    "public_html",
    "public_html/public_html",
    "public_html/public_html/public_html",
]

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


# upload helper
def upload_to_target(target):
    print("\nUploading to target:", target)
    # ensure target
    ensure(ftp, target)
    # index
    try:
        ftp.cwd(target)
    except Exception as e:
        print("cwd failed", target, e)
        return
    # upload index
    idx = os.path.join(local_base, "index.html")
    if os.path.isfile(idx):
        with open(idx, "rb") as fh:
            print("Uploading index.html ->", target + "/index.html")
            ftp.storbinary("STOR index.html", fh)
    # upload static dirs
    for sub in ["static/css", "static/js"]:
        local_dir = os.path.join(local_base, *sub.split("/"))
        remote_dir = target + "/" + sub
        ensure(ftp, remote_dir)
        try:
            ftp.cwd(remote_dir)
        except Exception:
            print("could not cwd to", remote_dir)
            continue
        for fname in os.listdir(local_dir):
            local_path = os.path.join(local_dir, fname)
            if os.path.isfile(local_path):
                print("Uploading", local_path, "->", remote_dir + "/" + fname)
                with open(local_path, "rb") as fh:
                    ftp.storbinary("STOR " + fname, fh)
    # upload root files
    for fname in ["asset-manifest.json", "favicon.svg"]:
        local_path = os.path.join(local_base, fname)
        if os.path.isfile(local_path):
            try:
                ftp.cwd(target)
            except Exception:
                pass
            print("Uploading", local_path, "->", target + "/" + fname)
            with open(local_path, "rb") as fh:
                ftp.storbinary("STOR " + fname, fh)
    # upload .htaccess
    ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
    from io import BytesIO

    try:
        ftp.cwd(target)
        print("Uploading .htaccess to", target)
        ftp.storbinary("STOR .htaccess", BytesIO(ht.encode("utf-8")))
    except Exception as e:
        print("failed to upload .htaccess to", target, e)


for t in targets:
    upload_to_target(t)

ftp.quit()
print("\nAll targets processed")
