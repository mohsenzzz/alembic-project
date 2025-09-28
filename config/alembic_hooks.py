import os
import re

def increment_filename(revision, filename, config):
    print("Hook executed! File:", filename)  # برای تست اجرا شدن

    versions_dir = os.path.dirname(os.path.abspath(filename))
    existing_files = sorted(
        f for f in os.listdir(versions_dir)
        if f.endswith(".py") and re.match(r"\d+_", f)
    )

    numbers = [int(re.match(r"(\d+)_", f).group(1)) for f in existing_files if re.match(r"(\d+)_", f)]
    next_num = max(numbers) + 1 if numbers else 1

    slug = os.path.basename(filename)
    new_filename = os.path.join(versions_dir, f"{next_num:03d}_{slug}")
    print("Renaming to:", new_filename)
    os.rename(filename, new_filename)
