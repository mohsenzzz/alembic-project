import subprocess
import os
import re
from pathlib import Path

VERSIONS_DIR = Path("alembic/versions")

def next_revision_number():
    existing = [f.name for f in VERSIONS_DIR.glob("*.py")]
    nums = []
    for f in existing:
        m = re.match(r"(\d+)_", f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1

def main(message):
    # run alembic revision
    subprocess.run([sys.executable, "-m","alembic", "revision", "--autogenerate", "-m", message])

    # find latest file
    latest = max(VERSIONS_DIR.glob("*.py"), key=lambda f: f.stat().st_mtime)

    # build new name with numeric prefix
    rev = f"{next_revision_number():03d}"
    new_name = VERSIONS_DIR / f"{rev}_{latest.name.split('_',1)[1]}"
    latest.rename(new_name)

    # patch inside file too
    text = new_name.read_text()
    text = re.sub(r"revision = .+?", f"revision = '{rev}'", text)
    text = re.sub(r"down_revision = .+?", f"down_revision = '{rev.zfill(3 - 1)}'", text)
    new_name.write_text(text)

    print(f"Renamed migration to {new_name}")

if __name__ == "__main__":
    import sys
    main(" ".join(sys.argv[1:]))


