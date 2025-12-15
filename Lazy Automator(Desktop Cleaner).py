import os
import shutil
from pathlib import Path

# --- CONFIGURATION ---
# change this to the folder you want to clean!
# For Windows, it usually looks like: r"C:\Users\YourName\Downloads"
DIRECTORY_TO_CLEAN = r"C:\Users\NEGAHDN\Downloads"

# Define where files should go based on their extension
EXTENSION_MAP = {
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets",
    ".exe": "Installers",
    ".msi": "Installers",
    ".zip": "Archives",
    ".mp4": "Videos",
    ".mp3": "Audio",
}


def organize_folder():
    target_dir = Path(DIRECTORY_TO_CLEAN)

    # Check if directory exists
    if not target_dir.exists():
        print(f"Error: The directory '{target_dir}' does not exist.")
        return

    print(f"Scanning {target_dir}...")

    # Iterate over all files in the directory
    for file_path in target_dir.iterdir():
        # Skip directories, only move files
        if file_path.is_dir():
            continue

        # Get the file extension (lowercase)
        file_extension = file_path.suffix.lower()

        # Check if we have a folder mapped for this extension
        if file_extension in EXTENSION_MAP:
            folder_name = EXTENSION_MAP[file_extension]

            # Create the destination sub-folder path
            destination_folder = target_dir / folder_name

            # Create the sub-folder if it doesn't exist
            destination_folder.mkdir(exist_ok=True)

            # Define the new path for the file
            destination_path = destination_folder / file_path.name

            # Move the file
            try:
                shutil.move(str(file_path), str(destination_path))
                print(f"Moved: {file_path.name} -> {folder_name}/")
            except Exception as e:
                print(f"Error moving {file_path.name}: {e}")

    print("\nDone! Your folder is organized.")


if __name__ == "__main__":
    organize_folder()
