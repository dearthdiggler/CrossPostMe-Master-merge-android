import ftplib
import io
import os

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
# Portable path logic
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
default_css = os.path.join(project_root, "app", "frontend", "build", "static", "css")
local_css = os.environ.get("LOCAL_CSS_PATH", default_css)
if not os.path.isdir(local_css):
    print("local css dir missing", local_css)
    raise SystemExit(2)
ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
# ensure static/css
try:
    ftp.mkd("static")
except Exception:
    pass
try:
    ftp.mkd("static/css")
except Exception:
    pass
# upload css files
try:
    ftp.cwd("static/css")
except Exception:
    ftp.cwd("/")
for fname in os.listdir(local_css):
    src = os.path.join(local_css, fname)
    if os.path.isfile(src):
        print("upload", fname)
        with open(src, "rb") as fh:
            ftp.storbinary("STOR " + fname, fh)
# upload .htaccess to root
ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
print("uploading .htaccess to root")
ftp.cwd("/")
ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
ftp.quit()
print("done")
