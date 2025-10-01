import os
import shutil

DOWNLOADS = r"C:\Users\NEGAHDN\OneDrive - City of Fort Worth"

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Music": [".mp3", ".wav"],
    "Videos": [".mp4", ".mkv", ".mov"],
    "Archives": [".zip", ".rar", ".7z"],
}

def organize_folder():
    for filename in os.listdir(DOWNLOADS):
        file_path = os.path.join(DOWNLOADS, filename)

        # Skip folders
        if os.path.isdir(file_path):
            continue

        # Skip hidden/system files (those starting with ".")
        if filename.startswith("."):
            continue

        _, ext = os.path.splitext(filename)

        moved = False
        for category, extensions in FILE_TYPES.items():
            if ext.lower() in extensions:
                category_folder = os.path.join(DOWNLOADS, category)
                os.makedirs(category_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(category_folder, filename))
                print(f"Moved: {filename} → {category}/")
                moved = True
                break

        if not moved:
            other_folder = os.path.join(DOWNLOADS, "Others")
            os.makedirs(other_folder, exist_ok=True)
            try:
                shutil.move(file_path, os.path.join(other_folder, filename))
                print(f"Moved: {filename} → Others/")
            except PermissionError:
                print(f"⚠ Skipped locked file: {filename}")

if __name__ == "__main__":
    organize_folder()
