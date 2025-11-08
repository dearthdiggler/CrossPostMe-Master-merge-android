import ftplib
import io
import os
import sys

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_build = r"C:\Users\johnd\Desktop\marketwiz\app\frontend\build"
if not os.path.isdir(local_build):
    print("Local build not found", local_build)
    sys.exit(2)
index_path = os.path.join(local_build, "index.html")
if not os.path.isfile(index_path):
    print("index.html missing", index_path)
    sys.exit(2)

ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
# ensure public_html
try:
    ftp.cwd("public_html")
except Exception:
    try:
        ftp.mkd("public_html")
        ftp.cwd("public_html")
    except Exception as e:
        print("Could not ensure public_html", e)
        ftp.quit()
        sys.exit(1)

# upload index.html
with open(index_path, "rb") as fh:
    print("Uploading index.html to public_html")
    ftp.storbinary("STOR index.html", fh)

# upload .htaccess
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("Uploading .htaccess to public_html")
ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))

# verify presence of assets, upload if missing
local_js = os.path.join(local_build, "static", "js")
local_css = os.path.join(local_build, "static", "css")
for d, local_dir in [("static/js", local_js), ("static/css", local_css)]:
    remote_dir = d
    # ensure remote directory
    parts = [p for p in remote_dir.replace("\\", "/").split("/") if p]
    cur = ""
    for p in parts:
        cur = f"{cur}/{p}" if cur else p
        try:
            ftp.mkd(cur)
        except Exception:
            pass
    try:
        ftp.cwd(remote_dir)
    except Exception:
        pass
    # list remote files
    try:
        remote_files = ftp.nlst(remote_dir)
    except Exception:
        remote_files = []
    remote_basename = set([r.split("/")[-1] for r in remote_files])
    if os.path.isdir(local_dir):
        for fname in os.listdir(local_dir):
            if fname in remote_basename:
                continue
            local_path = os.path.join(local_dir, fname)
            if os.path.isfile(local_path):
                print("Uploading", fname, "to", remote_dir)
                with open(local_path, "rb") as fh:
                    ftp.storbinary("STOR " + fname, fh)

ftp.quit()
print("Done")
