import os
import shutil

# Pick the folder you want to clean
DOWNLOADS = r"C:\Users\NEGAHDN\OneDrive - City of Fort Worth\Documents"

# File type categories
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

        # Get extension
        _, ext = os.path.splitext(filename)

        # Find matching category
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
            # Put everything else in "Others"
            other_folder = os.path.join(DOWNLOADS, "Others")
            os.makedirs(other_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(other_folder, filename))
            print(f"Moved: {filename} → Others/")

if __name__ == "__main__":
    organize_folder()
