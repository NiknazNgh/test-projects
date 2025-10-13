import os
import shutil
import pytesseract
from PIL import Image

# Path to the Tesseract engine
pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\NEGAHDN\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"

# Source and output directories
SOURCE_DIR = r"C:\\Users\\NEGAHDN\\OneDrive - City of Fort Worth\\Pictures\\Screenshots"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ocr_results")


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def extract_text_from_image(image_path: str, output_txt_path: str) -> None:
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"Reading image: {image_path}")
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved OCR text: {output_txt_path}")


def is_image_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def migrate_legacy_outputs_to_folder():
    """Move existing output_*.txt files in the project root into OUTPUT_DIR."""
    cwd = os.path.dirname(__file__)
    for name in os.listdir(cwd):
        if name.startswith("output_") and name.endswith(".txt"):
            src = os.path.join(cwd, name)
            dst = os.path.join(OUTPUT_DIR, name)
            # Do not overwrite if destination already exists
            if not os.path.exists(dst):
                try:
                    shutil.move(src, dst)
                except Exception as e:
                    print(f"Warning: could not move {src} -> {dst}: {e}")


if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    migrate_legacy_outputs_to_folder()

    processed = 0
    skipped = 0

    for img_file in os.listdir(SOURCE_DIR):
        if not is_image_file(img_file):
            continue

        # Output name matches previous runs for easy detection
        output_name = f"output_{img_file}.txt"
        output_path = os.path.join(OUTPUT_DIR, output_name)

        # Also check for legacy output in the project root to avoid reprocessing
        legacy_output_path = os.path.join(os.path.dirname(__file__), output_name)

        if os.path.exists(output_path) or os.path.exists(legacy_output_path):
            skipped += 1
            continue

        image_path = os.path.join(SOURCE_DIR, img_file)
        extract_text_from_image(image_path, output_path)
        processed += 1

    print(f"Done. Processed: {processed}, Skipped (already done): {skipped}. Results: {OUTPUT_DIR}")

