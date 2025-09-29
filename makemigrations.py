# import subprocess
# import os
# import re
# from pathlib import Path
#
# VERSIONS_DIR = Path("alembic/versions")
#
# def next_revision_number():
#     existing = [f.name for f in VERSIONS_DIR.glob("*.py")]
#     nums = []
#     for f in existing:
#         m = re.match(r"(\d+)_", f)
#         if m:
#             nums.append(int(m.group(1)))
#     return max(nums) + 1 if nums else 1
#
# def main(message):
#     # run alembic revision
#     subprocess.run([sys.executable, "-m","alembic", "revision", "--autogenerate", "-m", message])
#
#     # find latest file
#     latest = max(VERSIONS_DIR.glob("*.py"), key=lambda f: f.stat().st_mtime)
#
#     # build new name with numeric prefix
#     rev = f"{next_revision_number():03d}"
#     new_name = VERSIONS_DIR / f"{rev}_{latest.name.split('_',1)[1]}"
#     latest.rename(new_name)
#
#     # patch inside file too
#     text = new_name.read_text()
#     text = re.sub(r"revision = .+?", f"revision = '{rev}'", text)
#     text = re.sub(r"down_revision = .+?", f"down_revision = '{rev.zfill(3 - 1)}'", text)
#     new_name.write_text(text)
#
#     print(f"Renamed migration to {new_name}")
#
# if __name__ == "__main__":
#     import sys
#     main(" ".join(sys.argv[1:]))
#
#
# alembic/script.py
import subprocess
import re
from pathlib import Path
import sys

VERSIONS_DIR = Path("alembic/versions")

def next_revision_number():
    existing = [f.name for f in VERSIONS_DIR.glob("*.py")]
    nums = []
    for f in existing:
        m = re.match(r"(\d+)_", f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) + 1 if nums else 1

def detect_action_from_text(text):
    # Simple examples; extend for other operations
    """Inspect Alembic autogen migration text and return descriptive action name."""
    actions = []

    # 1. Detect created tables
    created_tables = re.findall(r"op.create_table\('(\w+)'", text)
    for table in created_tables:
        actions.append(f"create_{table}")

    # 2. Detect dropped tables
    dropped_tables = re.findall(r"op.drop_table\('(\w+)'", text)
    for table in dropped_tables:
        actions.append(f"delete_{table}")

    # 3. Detect added columns
    added_columns = re.findall(r"op.add_column\('(\w+)', Column\('(\w+)'", text)
    for table, column in added_columns:
        actions.append(f"add_{column}_to_{table}")

    # 4. Detect dropped columns
    dropped_columns = re.findall(r"op.drop_column\('(\w+)', '(\w+)'", text)
    for table, column in dropped_columns:
        actions.append(f"delete_{column}_from_{table}")

    # 5. Detect altered columns
    altered_columns = re.findall(r"op.alter_column\('(\w+)', '(\w+)'", text)
    table_name=None
    for table, column in altered_columns:
        if table_name != table:
            actions.append(f"alter_{column}_from_{table}")
            table_name = table

    # 6. Fallback
    if not actions:
        actions.append("update_schema")

    return "_and_".join(actions)


def extract_upgrade_only(file_path: Path) -> str:
    lines = file_path.read_text().splitlines()
    upgrade_lines = []
    inside_upgrade = False
    indent_level = None

    for line in lines:
        # شروع متد upgrade
        if line.strip().startswith("def upgrade("):
            inside_upgrade = True
            indent_level = len(line) - len(line.lstrip())
            continue

        if inside_upgrade:
            # اگر به خطی رسیدیم که indent کمتر دارد و تابع جدید است، خروج
            current_indent = len(line) - len(line.lstrip())
            if line.strip().startswith("def ") and current_indent <= indent_level:
                break
            upgrade_lines.append(line)

    return "\n".join(upgrade_lines).strip()

def main():
    before = set(VERSIONS_DIR.glob("*.py"))

    # Run alembic autogenerate
    subprocess.run([sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "temp"], check=True)

    after = set(VERSIONS_DIR.glob("*.py"))
    new_files = list(after - before)
    if not new_files:
        print("No new migration generated")
        return

    latest = new_files[0]
    upgrade_text=extract_upgrade_only(latest)


    action_name = detect_action_from_text(upgrade_text)

    rev_num = f"{next_revision_number():03d}"
    new_name = VERSIONS_DIR / f"{rev_num}_{action_name}.py"
    latest.rename(new_name)
    print(f"Renamed migration to {new_name}")

if __name__ == "__main__":
    main()
