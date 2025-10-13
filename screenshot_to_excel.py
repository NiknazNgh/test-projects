import os
import pytesseract
from pytesseract import Output
from PIL import Image, ImageEnhance, ImageOps
from openpyxl import Workbook
from datetime import datetime

# === Tesseract Path ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\NEGAHDN\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# === Config ===
SOURCE_DIR = r"C:\Users\NEGAHDN\Downloads\New folder (2)"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ocr_results_xlsx")

# Tesseract configuration for structured table-like OCR
TESS_CONFIG = (
    r"--oem 3 --psm 6 "
    r"-c preserve_interword_spaces=1 "
    r"-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-:/%.?"
)

# === Helper functions ===
def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def preprocess(img_path):
    """Enhance contrast and sharpen the image for better OCR on blue-background SCADA screens."""
    img = Image.open(img_path)
    img = ImageOps.grayscale(img)
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = img.point(lambda p: 255 if p > 180 else 0)
    return img

def extract_table(img):
    """Use image_to_data to get positional OCR data and rebuild rows by vertical proximity."""
    data = pytesseract.image_to_data(img, config=TESS_CONFIG, output_type=Output.DICT)

    rows = []
    current_line = []
    last_top = None

    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if not word:
            continue
        top = data['top'][i]
        # If new line detected (top coordinate jump)
        if last_top is not None and abs(top - last_top) > 12:
            rows.append(" ".join(current_line))
            current_line = []
        current_line.append(word)
        last_top = top

    if current_line:
        rows.append(" ".join(current_line))

    # Filter out garbage and headers
    clean_rows = []
    for r in rows:
        if any(month in r for month in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]):
            clean_rows.append(r)
    return clean_rows

def save_to_excel(image_name, rows):
    """Save the extracted rows to Excel with proper formatting."""
    wb = Workbook()
    ws = wb.active
    ws.title = "OCR Data"
    ws.append(["DATE", "TIME", "TAG", "VALUE"])

    for line in rows:
        parts = line.split()
        if len(parts) >= 4:
            date = parts[0]
            time = parts[1]
            tag = parts[2]
            value = parts[-1]
            ws.append([date, time, tag, value])
        elif len(parts) >= 2:
            ws.append(parts)

    for col in ['A', 'B', 'C', 'D']:
        ws.column_dimensions[col].width = 18

    output_path = os.path.join(OUTPUT_DIR, os.path.splitext(image_name)[0] + ".xlsx")
    wb.save(output_path)
    print(f"✅ Saved {os.path.basename(output_path)} ({len(rows)} rows)")

def main():
    ensure_dir(OUTPUT_DIR)
    print(f"📂 Reading from: {SOURCE_DIR}")
    images = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]

    if not images:
        print("⚠️ No screenshots found in folder.")
        return

    for img_name in images:
        try:
            img_path = os.path.join(SOURCE_DIR, img_name)
            print(f"🖼️ Processing: {img_name}")
            processed = preprocess(img_path)
            rows = extract_table(processed)
            save_to_excel(img_name, rows)
        except Exception as e:
            print(f"⚠️ Error with {img_name}: {e}")

    print("\n🎯 Done! Excel files saved to:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
