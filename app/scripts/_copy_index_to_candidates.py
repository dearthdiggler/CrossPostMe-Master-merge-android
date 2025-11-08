import ftplib
import io
import os

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_index = r"C:\Users\johnd\Desktop\marketwiz\app\frontend\build\index.html"
if not os.path.isfile(local_index):
    print("local index missing", local_index)
    raise SystemExit(2)

ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
# candidate paths (from earlier search results)
candidates = [
    "public_html/index.html",
    "public_html/public_html/index.html",
    "public_html/static/index.html",
    "public_html/public_html/public_html/index.html",
    "public_html/public_html/static/index.html",
    "public_html/static/js/index.html",
]
# upload index.html into each candidate's parent directory
for c in candidates:
    try:
        parent = "/".join(c.split("/")[:-1]) or "."
        parts = [p for p in parent.replace("\\", "/").split("/") if p]
        # ensure parent exists
        cur = ""
        for p in parts:
            cur = f"{cur}/{p}" if cur else p
            try:
                ftp.mkd(cur)
            except Exception:
                pass
        # change cwd
        try:
            ftp.cwd(parent)
        except Exception:
            pass
        print("Uploading index to", parent)
        with open(local_index, "rb") as fh:
            ftp.storbinary("STOR index.html", fh)
        # upload .htaccess as well
        ht = "RewriteEngine On\nRewriteBase /\n\n# Serve index.html for all requests (single-page app)\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule ^ index.html [L,QSA]\n"
        ftp.storbinary("STOR .htaccess", io.BytesIO(ht.encode("utf-8")))
    except Exception as e:
        print("Error uploading to", c, e)

ftp.quit()
print("done")
