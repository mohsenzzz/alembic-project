
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
    table_name = None
    for table, column in added_columns:
        if table_name != table:
            actions.append(f"add_{column}_to_{table}")
            table_name = table
        else:
            actions.append(f"add_{column}")

    # 4. Detect dropped columns
    dropped_columns = re.findall(r"op.drop_column\('(\w+)', '(\w+)'", text)
    table_name = None
    for table, column in dropped_columns:
        if table_name != table:
            actions.append(f"delete_{column}_from_{table}")
            table_name = table
        else:
            actions.append(f"delete_{column}")

    # 5. Detect altered columns
    altered_columns = re.findall(r"op.alter_column\('(\w+)', '(\w+)'", text)
    table_name=None
    for table, column in altered_columns:
        if table_name != table:
            actions.append(f"alter_{column}_from_{table}")
            table_name = table
        else:
            actions.append(f"alter_{column}")

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
