import os
import shutil
from datetime import datetime

SOURCE_FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\important_files"
BACKUP_FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\file-backup\Backups"
MAX_VERSIONS = 5  # Keep only the last 5 backups per file

def backup_files():
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    for file in os.listdir(SOURCE_FOLDER):
        if not file.lower().endswith((".xlsx", ".xlsb", ".docx", ".py")):
            continue

        src_path = os.path.join(SOURCE_FOLDER, file)

        # Add a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name, ext = os.path.splitext(file)
        backup_name = f"{base_name}_{timestamp}{ext}"
        dst_path = os.path.join(BACKUP_FOLDER, backup_name)

        shutil.copy2(src_path, dst_path)
        print(f"📦 Backed up: {file} → {backup_name}")

        # Limit number of versions
        clean_old_backups(base_name, ext)

def clean_old_backups(base_name, ext):
    """Keep only the latest N backups for each file."""
    pattern = f"{base_name}_"
    backups = sorted(
        [f for f in os.listdir(BACKUP_FOLDER) if f.startswith(pattern) and f.endswith(ext)],
        reverse=True
    )

    for old_file in backups[MAX_VERSIONS:]:
        os.remove(os.path.join(BACKUP_FOLDER, old_file))
        print(f"🧹 Removed old version: {old_file}")

if __name__ == "__main__":
    backup_files()
    print("✅ All files backed up successfully.")
