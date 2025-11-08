#!/usr/bin/env python3
"""Force-publish the current frontend build to every index.html found under public_html.
This walks the FTP public_html tree, finds directories containing index.html and uploads
the local build/index.html and static assets (js/css) into each of those directories.
"""
import ftplib
import os
from io import BytesIO

HOST = "82.180.138.1"
USER = "u132063632.crosspostme.com"
PASS = "aPANDAGOD13!"
LOCAL_BUILD = r"c:\Users\johnd\Desktop\marketwiz\app\frontend\build"


def ftp_connect():
    ftp = ftplib.FTP()
    ftp.connect(HOST, 21, timeout=30)
    ftp.login(USER, PASS)
    ftp.set_pasv(True)
    return ftp


def walk(ftp, path):
    # Return list of file paths under path using nlst
    try:
        items = ftp.nlst(path)
    except Exception:
        return []
    results = []
    for it in items:
        if it in (".", ".."):
            continue
        results.append(it)
        # try to descend
        try:
            ftp.cwd(it)
            # it's a dir
            results += walk(ftp, it)
            ftp.cwd("/")
        except Exception:
            # file, ignore
            pass
    return results


def ensure(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


def upload_to_dir(ftp, remote_dir):
    # upload index, static js/css, asset-manifest.json, favicon.svg, and .htaccess
    print("Publishing to", remote_dir)
    try:
        ensure(ftp, remote_dir)
        ftp.cwd(remote_dir)
    except Exception as e:
        print("Could not cwd to", remote_dir, e)
        return

    # index.html
    local_index = os.path.join(LOCAL_BUILD, "index.html")
    if os.path.isfile(local_index):
        with open(local_index, "rb") as fh:
            ftp.storbinary("STOR index.html", fh)

    # static dirs
    for sub in ("static/js", "static/css"):
        local_dir = os.path.join(LOCAL_BUILD, *sub.split("/"))
        remote_subdir = remote_dir.rstrip("/") + "/" + sub
        ensure(ftp, remote_subdir)
        try:
            ftp.cwd(remote_subdir)
        except Exception:
            print("could not cwd to", remote_subdir)
            continue
        if os.path.isdir(local_dir):
            for fname in os.listdir(local_dir):
                local_path = os.path.join(local_dir, fname)
                if os.path.isfile(local_path):
                    with open(local_path, "rb") as fh:
                        print(
                            "Uploading", local_path, "->", remote_subdir + "/" + fname
                        )
                        ftp.storbinary("STOR " + fname, fh)

    # root files
    for fname in ("asset-manifest.json", "favicon.svg"):
        local_path = os.path.join(LOCAL_BUILD, fname)
        if os.path.isfile(local_path):
            try:
                ftp.cwd(remote_dir)
            except Exception:
                pass
            with open(local_path, "rb") as fh:
                ftp.storbinary("STOR " + fname, fh)

    # .htaccess for SPA fallback
    ht = (
        "RewriteEngine On\nRewriteBase /\n\n"
        "# Serve index.html for all requests (single-page app)\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteCond %{REQUEST_FILENAME} !-d\n"
        "RewriteRule ^ index.html [L,QSA]\n"
    )
    try:
        ftp.cwd(remote_dir)
        ftp.storbinary("STOR .htaccess", BytesIO(ht.encode("utf-8")))
    except Exception as e:
        print("Failed to write .htaccess to", remote_dir, e)


def main():
    ftp = ftp_connect()
    print("Connected, scanning public_html...")
    all_paths = walk(ftp, "public_html")
    # find directories which contain index.html
    dirs = set()
    for p in all_paths:
        if p.lower().endswith("index.html"):
            # remove trailing file to get directory
            dirpath = os.path.dirname(p)
            if not dirpath:
                dirpath = "public_html"
            dirs.add(dirpath)
    # also include plain public_html
    dirs.add("public_html")
    print("Found index.html in dirs:", dirs)
    for d in sorted(dirs):
        upload_to_dir(ftp, d)

    ftp.quit()
    print("Done")


if __name__ == "__main__":
    main()
