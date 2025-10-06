import pytesseract
from PIL import Image
import os

# Path to the Tesseract engine
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\NEGAHDN\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path, output_txt):
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}")
        return

    print(f"🖼️ Reading image: {image_path}")
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Text extracted and saved to: {output_txt}")

if __name__ == "__main__":
    extract_text_from_image(
        r"C:\Users\NEGAHDN\OneDrive - City of Fort Worth\Pictures\Screenshots\Screenshot 2025-10-03 155718.png",
        "output.txt"
    )
