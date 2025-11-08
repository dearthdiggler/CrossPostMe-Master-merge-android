import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[2]  # repo root (app/..)
print("Repo root:", root)
snapshot_dir = root / "master_snapshot"
if snapshot_dir.exists():
    print("Removing existing snapshot at", snapshot_dir)
    shutil.rmtree(snapshot_dir)

exclude = {".git", "master_snapshot"}


def should_exclude(path: Path):
    # exclude .git and the snapshot directory itself
    for part in path.relative_to(root).parts:
        if part in exclude:
            return True
    return False


print("Creating snapshot at", snapshot_dir)

for item in root.iterdir():
    name = item.name
    if name in exclude:
        print("Skipping", name)
        continue
    dest = snapshot_dir / name
    if item.is_dir():
        print("Copying dir", item, "->", dest)
        shutil.copytree(item, dest)
    else:
        print("Copying file", item, "->", dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)

print("Snapshot created successfully at", snapshot_dir)
