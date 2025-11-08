#!/usr/bin/env python3
"""Upload build assets to all 'static' directories found under public_html.
Usage: python _deploy_ftp_recursive.py --host HOST --user USER --password PASS --local-build PATH
"""
import argparse
import ftplib
import os


def is_dir(ftp, path):
    cur = ftp.pwd()
    try:
        ftp.cwd(path)
        ftp.cwd(cur)
        return True
    except Exception:
        return False


def walk(ftp, root):
    # return list of all directories under root (including root)
    dirs = []
    stack = [root]
    seen = set()
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        dirs.append(p)
        try:
            entries = ftp.nlst(p)
        except Exception:
            continue
        for e in entries:
            # ftp.nlst returns paths like 'public_html/dir' sometimes; normalize
            # We'll attempt to treat e as a directory if cwd succeeds
            # Try full path
            candidate = e
            try:
                ftp.cwd(candidate)
                # if cwd works, then it's a directory; add and then return to previous cwd
                ftp.cwd("/")
                stack.append(candidate)
            except Exception:
                # try joining
                joined = p.rstrip("/") + "/" + os.path.basename(e)
                try:
                    ftp.cwd(joined)
                    ftp.cwd("/")
                    stack.append(joined)
                except Exception:
                    # not a directory
                    pass
    return dirs


def ensure_remote_dir(ftp, path):
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass


def upload_file(ftp, local_path, remote_dir):
    fname = os.path.basename(local_path)
    try:
        ensure_remote_dir(ftp, remote_dir)
        try:
            ftp.cwd(remote_dir)
        except Exception:
            pass
        with open(local_path, "rb") as fh:
            print(f"Uploading {local_path} -> {remote_dir}/{fname}")
            ftp.storbinary("STOR " + fname, fh)
    except Exception as e:
        print("ERROR uploading", local_path, "->", remote_dir, e)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--local-build", required=True)
    args = p.parse_args()

    build = os.path.abspath(args.local_build)
    if not os.path.isdir(build):
        print("Local build path not found", build)
        return

    ftp = ftplib.FTP()
    print("Connecting", args.host)
    ftp.connect(args.host, 21, timeout=30)
    ftp.login(args.user, args.password)
    ftp.set_pasv(True)

    root = "public_html"
    print("Walking FTP tree under", root)
    dirs = walk(ftp, root)
    print("Found", len(dirs), "directories (sample 50):", dirs[:50])

    # upload index.html to every public_html-like dir
    index_local = os.path.join(build, "index.html")
    for d in dirs:
        # if dir endswith public_html or contains /public_html/
        if d.endswith("public_html") or "/public_html/" in d:
            upload_file(ftp, index_local, d)

    # upload static assets where appropriate
    local_js_dir = os.path.join(build, "static", "js")
    local_css_dir = os.path.join(build, "static", "css")
    # for each dir in ftp dirs, if it endswith static/js or static/css or contains /static/js or /static/css, upload
    for d in dirs:
        low = d.lower()
        if low.endswith("/static/js") or "/static/js" in low:
            # upload all js files
            if os.path.isdir(local_js_dir):
                for f in os.listdir(local_js_dir):
                    upload_file(ftp, os.path.join(local_js_dir, f), d)
        if low.endswith("/static/css") or "/static/css" in low:
            if os.path.isdir(local_css_dir):
                for f in os.listdir(local_css_dir):
                    upload_file(ftp, os.path.join(local_css_dir, f), d)

    # Also ensure top-level files are uploaded to root public_html
    top_files = ["asset-manifest.json", "favicon.svg", "index.html", "diagrams.html"]
    for tf in top_files:
        local_tf = os.path.join(build, tf)
        if os.path.exists(local_tf):
            upload_file(ftp, local_tf, root)

    # upload .htaccess to root to enable SPA fallback
    ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
    try:
        ftp.cwd(root)
        from io import BytesIO

        ftp.storbinary("STOR .htaccess", BytesIO(ht.encode("utf-8")))
        print("Wrote .htaccess to", root)
    except Exception as e:
        print("Failed to write .htaccess", e)

    ftp.quit()
    print("Done")


if __name__ == "__main__":
    main()
