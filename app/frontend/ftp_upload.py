import os
from ftplib import FTP

FTP_HOST = "ftp.crosspostme.com"
FTP_USER = "u132063632.crosspostme"
FTP_PASS = input("Enter FTP password: ")
LOCAL_DIR = "build"
REMOTE_DIR = "/public_html"


def upload_dir(ftp, local_dir, remote_dir):
    for root, dirs, files in os.walk(local_dir):
        rel_path = os.path.relpath(root, local_dir)
        ftp_path = (
            remote_dir
            if rel_path == "."
            else f"{remote_dir}/{rel_path.replace('\\', '/')}"
        )
        try:
            ftp.mkd(ftp_path)
        except Exception:
            pass  # Directory may already exist
        ftp.cwd(ftp_path)
        for fname in files:
            local_file = os.path.join(root, fname)
            with open(local_file, "rb") as f:
                ftp.storbinary(f"STOR {fname}", f)
        ftp.cwd("..")


def main():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    upload_dir(ftp, LOCAL_DIR, REMOTE_DIR)
    ftp.quit()
    print("Upload complete.")


if __name__ == "__main__":
    main()
