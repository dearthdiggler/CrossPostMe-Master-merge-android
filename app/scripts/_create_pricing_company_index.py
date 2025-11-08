import ftplib
import os
import sys

host = "82.180.138.1"
user = "u132063632.crosspostme.com"
passwd = "aPANDAGOD13!"
local_index = r"C:\Users\johnd\Desktop\marketwiz\app\frontend\build\index.html"
if not os.path.isfile(local_index):
    print("local index missing", local_index)
    sys.exit(2)
ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
for name in ["pricing", "company"]:
    remote_dir = f"public_html/{name}"
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
    except Exception as e:
        print("cwd failed", remote_dir, e)
    with open(local_index, "rb") as fh:
        print("Uploading index to", remote_dir + "/index.html")
        ftp.storbinary("STOR index.html", fh)
ftp.quit()
print("Done")
