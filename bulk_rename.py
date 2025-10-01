import os
import re
import argparse
from datetime import datetime
from pathlib import Path

def slugify(name: str) -> str:
    # keep letters, numbers, dashes, underscores; replace spaces with _
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]", "-", name)
    # collapse multiple separators
    name = re.sub(r"-{2,}", "-", name)
    name = re.sub(r"_{2,}", "_", name)
    return name

def build_new_name(path: Path, prefix: str, suffix: str, lower: bool, upper: bool,
                   dateprefix: bool, index: int | None) -> str:
    stem = path.stem
    ext = path.suffix

    # normalize
    stem = slugify(stem)
    if lower:
        stem = stem.lower()
    if upper:
        stem = stem.upper()

    parts = []
    if dateprefix:
        parts.append(datetime.now().strftime("%Y%m%d"))
    if prefix:
        parts.append(prefix)
    parts.append(stem)
    if suffix:
        parts.append(suffix)

    new_stem = "_".join([p for p in parts if p])

    if index is not None:
        new_stem = f"{new_stem}_{index:03d}"

    return new_stem + ext

def is_ignorable(path: Path) -> bool:
    # skip hidden & system-ish clutter
    hidden = path.name.startswith(".")
    onedrive_noise = path.name.startswith(".849C") or path.name.endswith(".tmp")
    return hidden or onedrive_noise

def main():
    p = argparse.ArgumentParser(description="Bulk rename files with preview & dry-run.")
    p.add_argument("folder", help="Folder containing files to rename")
    p.add_argument("--prefix", default="", help="Add prefix (before filename)")
    p.add_argument("--suffix", default="", help="Add suffix (after filename, before extension)")
    p.add_argument("--lower", action="store_true", help="Force lowercase")
    p.add_argument("--upper", action="store_true", help="Force UPPERCASE (overrides --lower)")
    p.add_argument("--dateprefix", action="store_true", help="Add YYYYMMDD at start")
    p.add_argument("--ext", default="", help="Filter by extension (e.g. .jpg)")
    p.add_argument("--start", type=int, default=1, help="Start index for numbering (optional)")
    p.add_argument("--number", action="store_true", help="Append _### sequence")
    p.add_argument("--dry", action="store_true", help="Dry-run (preview only)")
    args = p.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"Folder not found: {folder}")
        return

    files = [p for p in folder.iterdir() if p.is_file()]
    if args.ext:
        files = [f for f in files if f.suffix.lower() == args.ext.lower()]

    # deterministic order
    files.sort(key=lambda p: p.name.lower())

    if not files:
        print("No files found (check path or --ext filter).")
        return

    print(f"Found {len(files)} file(s) in: {folder}")
    idx = args.start if args.number else None
    planned = []

    for i, f in enumerate(files, start=args.start):
        if is_ignorable(f):
            continue
        new_name = build_new_name(
            f,
            prefix=args.prefix,
            suffix=args.suffix,
            lower=(args.lower and not args.upper),
            upper=args.upper,
            dateprefix=args.dateprefix,
            index=(i if args.number else None),
        )
        dst = f.with_name(new_name)

        # avoid accidental overwrite
        if dst.exists() and dst != f:
            # add a unique tail
            base = dst.stem
            ext = dst.suffix
            k = 1
            while dst.exists():
                dst = f.with_name(f"{base}__{k}{ext}")
                k += 1

        planned.append((f, dst))

    # preview
    print("\nPreview:")
    for src, dst in planned:
        if src != dst:
            print(f"{src.name}  ->  {dst.name}")
        else:
            print(f"{src.name}  (no change)")

    if args.dry:
        print("\nDRY-RUN: No changes made.")
        return

    # apply
    changes = 0
    for src, dst in planned:
        if src == dst:
            continue
        try:
            src.rename(dst)
            changes += 1
        except PermissionError:
            print(f"⚠ Skipped locked file: {src.name}")
        except Exception as e:
            print(f"⚠ Error renaming {src.name}: {e}")

    print(f"\nDone. Renamed {changes} file(s).")

if __name__ == "__main__":
    main()
