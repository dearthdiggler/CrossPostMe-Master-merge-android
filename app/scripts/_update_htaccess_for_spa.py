import ftplib
import io
import sys

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"

content = """Options -MultiViews
DirectoryIndex index.html

RewriteEngine On
RewriteBase /

# Serve index.html for all requests (single-page app)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^ index.html [L,QSA]
"""

ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
try:
    ftp.cwd("public_html")
except Exception as e:
    print("Could not cwd into public_html", e)
    ftp.quit()
    sys.exit(1)
print("Uploading updated .htaccess to public_html")
ftp.storbinary("STOR .htaccess", io.BytesIO(content.encode("utf-8")))
ftp.quit()
print("Done")
