"""
Cleanup script for CAMAT corpus folders.

Rules applied to each target folder:
  - Delete everything except files whose stem ends in _facs_zones
  - Also delete the img/ subfolder entirely

Usage:
  python cleanup.py                  # dry run on all numbered folders in repo root
  python cleanup.py --run            # actually delete
  python cleanup.py path/to/folder   # dry run on a specific folder
  python cleanup.py path/to/folder --run
"""

import sys
import shutil
from pathlib import Path


def collect_deletions(folder: Path) -> list[Path]:
    to_delete = []

    for f in folder.iterdir():
        if f.is_dir() and f.name.lower() == "img":
            to_delete.append(f)
            continue

        if not f.is_file():
            continue

        if not f.stem.endswith("_facs_zones"):
            to_delete.append(f)

    return to_delete


def main():
    args = sys.argv[1:]
    dry_run = "--run" not in args
    paths = [a for a in args if a != "--run"]

    repo_root = Path(__file__).parent

    if paths:
        folders = [Path(p) for p in paths]
    else:
        folders = sorted(d for d in repo_root.iterdir() if d.is_dir() and d.name[0].isdigit())

    if not folders:
        print("No folders found.")
        return

    all_deletions: list[tuple[Path, Path]] = []  # (folder, item)
    for folder in folders:
        if not folder.exists():
            print(f"Folder not found: {folder}")
            continue
        items = collect_deletions(folder)
        for item in items:
            all_deletions.append((folder, item))

    if not all_deletions:
        print("Nothing to delete.")
        return

    print(f"{'DRY RUN — ' if dry_run else ''}Files/folders to delete:\n")
    current_folder = None
    for folder, item in all_deletions:
        if folder != current_folder:
            print(f"  [{folder.name}]")
            current_folder = folder
        label = "(dir) " if item.is_dir() else ""
        print(f"    {label}{item.name}")

    total = len(all_deletions)
    print(f"\nTotal: {total} item(s)")

    if dry_run:
        print("\nRun with --run to actually delete.")
        return

    confirm = input("\nProceed with deletion? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    deleted = 0
    for folder, item in all_deletions:
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            deleted += 1
        except Exception as e:
            print(f"Error deleting {item}: {e}")

    print(f"Deleted {deleted}/{total} item(s).")


if __name__ == "__main__":
    main()
