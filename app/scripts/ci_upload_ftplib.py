#!/usr/bin/env python3
"""CI FTP uploader used by GitHub Actions.
Reads args and uploads a directory recursively to the remote FTP path.
"""
import argparse
import ftplib
import os
import sys


def ensure_remote_dir(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


def upload_dir(ftp, local_dir, remote_dir):
    local_dir = os.path.abspath(local_dir)
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir)
        if rel == ".":
            remote_path = remote_dir
        else:
            remote_path = remote_dir.rstrip("/") + "/" + rel.replace("\\", "/")
        ensure_remote_dir(ftp, remote_path)
        try:
            ftp.cwd(remote_path)
        except Exception:
            ensure_remote_dir(ftp, remote_path)
            ftp.cwd(remote_path)
        for f in files:
            local_path = os.path.join(root, f)
            with open(local_path, "rb") as fh:
                print(f"Uploading {local_path} -> {remote_path}/{f}")
                ftp.storbinary(f"STOR {f}", fh)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--local", required=True)
    p.add_argument("--remote", required=True)
    args = p.parse_args()

    if not os.path.isdir(args.local):
        print("Local path not found:", args.local)
        sys.exit(2)

    print("Connecting to", args.host)
    ftp = ftplib.FTP()
    ftp.connect(args.host, 21, timeout=60)
    ftp.login(args.user, args.password)
    ftp.set_pasv(True)
    try:
        upload_dir(ftp, args.local, args.remote)
    finally:
        try:
            ftp.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
