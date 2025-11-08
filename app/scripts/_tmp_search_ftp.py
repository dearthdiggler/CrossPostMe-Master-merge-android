import argparse
import ftplib

p = argparse.ArgumentParser()
p.add_argument("--host", required=True)
p.add_argument("--user", required=True)
p.add_argument("--password", required=True)
p.add_argument("--start", default="public_html")
p.add_argument("--name", required=True)
args = p.parse_args()

host = args.host
user = args.user
passwd = args.password
start = args.start
target = args.name

seen = set()
matches = []

ftp = ftplib.FTP()
ftp.connect(host, 21, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)


def safe_nlst(path):
    try:
        return ftp.nlst(path)
    except Exception:
        return []


# BFS over directories to avoid deep recursion
queue = [start]
while queue:
    cur = queue.pop(0)
    if cur in seen:
        continue
    seen.add(cur)
    # try to list entries under cur
    try:
        entries = ftp.nlst(cur)
    except Exception:
        entries = []
    for ent in entries:
        # normalize
        name = ent.split("/")[-1]
        if name == target:
            matches.append(ent)
        # heuristic: if entry looks like a dir (endswith '/' or no dot?) attempt to enqueue
        if not name or name in (".", ".."):
            continue
        # if entry looks like a directory path (contains cur + '/'), enqueue
        # also avoid enqueuing files (has a dot and not end with '/')
        if ent.endswith("/") or "." not in name:
            queue.append(ent)

print("Matches for", target)
for m in matches:
    print(m)

ftp.quit()
