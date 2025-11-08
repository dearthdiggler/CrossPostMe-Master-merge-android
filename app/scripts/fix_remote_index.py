#!/usr/bin/env python3
"""Fix remote nested index.html files by uploading local build/index.html to every index.html
found under the remote `public_html` tree. Also upload a .htaccess SPA fallback to each
directory visited.

Usage:
  python fix_remote_index.py --host HOST --user USER --password PASS --local-index PATH

This script is designed to be run from the repo's virtualenv but has no external deps.
"""
import argparse
import ftplib
import io
import os


def list_recursive(ftp, start):
    # BFS traversal returning all file paths under start
    seen = set()
    queue = [start]
    files = []
    while queue:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        try:
            entries = ftp.nlst(cur)
        except Exception:
            # cur might be a file rather than a directory
            files.append(cur)
            continue
        for e in entries:
            # Normalize some FTP servers return '.'/'..' and full path names
            if e.endswith("/.") or e.endswith("/.."):
                continue
            # If entry looks like a directory (endswith '/'), try to descend
            try:
                # Attempt to cwd into it to determine if directory
                ftp.cwd(e)
                # It's a directory
                queue.append(e)
                # Move back up
                ftp.cwd("/")
            except Exception:
                # It's a file path
                files.append(e)
    return files


def ensure_remote_dir(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


def upload_to_remote(ftp, local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    remote_name = os.path.basename(remote_path)
    ensure_remote_dir(ftp, remote_dir)
    try:
        ftp.cwd(remote_dir)
    except Exception:
        ensure_remote_dir(ftp, remote_dir)
        ftp.cwd(remote_dir)
    with open(local_path, "rb") as fh:
        print(f"Uploading {local_path} -> {remote_dir}/{remote_name}")
        ftp.storbinary(f"STOR {remote_name}", fh)


def upload_htaccess_into(ftp, remote_dir):
    # Basic Apache rewrite to serve index.html for SPA routes
    ht = (
        "RewriteEngine On\n"
        "RewriteBase /\n\n"
        "# Serve index.html for all requests (single-page app)\n"
        "RewriteCond %{REQUEST_FILENAME} !-f\n"
        "RewriteCond %{REQUEST_FILENAME} !-d\n"
        "RewriteRule ^ index.html [L,QSA]\n"
    )
    try:
        ensure_remote_dir(ftp, remote_dir)
        ftp.cwd(remote_dir)
        ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
        print("Uploaded .htaccess to", remote_dir)
    except Exception as e:
        print("Failed to upload .htaccess to", remote_dir, e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--local-index", required=True)
    p.add_argument("--remote-root", default="public_html")
    args = p.parse_args()

    if not os.path.isfile(args.local_index):
        print("Local index.html not found:", args.local_index)
        return

    ftp = ftplib.FTP()
    print("Connecting to", args.host)
    ftp.connect(args.host, 21, timeout=60)
    ftp.login(args.user, args.password)
    ftp.set_pasv(True)

    # List files recursively
    print("Listing remote tree under", args.remote_root)
    files = list_recursive(ftp, args.remote_root)
    index_paths = [f for f in files if f.lower().endswith("index.html")]
    print("Found index.html paths:", len(index_paths))
    for path in index_paths:
        try:
            # Overwrite the remote index.html
            upload_to_remote(ftp, args.local_index, path)
        except Exception as e:
            print("Failed to upload to", path, e)
    # Also upload .htaccess at top-level and to remote_root
    upload_htaccess_into(ftp, args.remote_root)
    # attempt uploading .htaccess into any nested public_html directories we discovered
    for pth in set([os.path.dirname(x) for x in index_paths]):
        upload_htaccess_into(ftp, pth)

    try:
        ftp.quit()
    except Exception:
        pass


if __name__ == "__main__":
    main()
