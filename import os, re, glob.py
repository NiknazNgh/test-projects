import os, re, glob
import pandas as pd
from PIL import Image, ImageFilter, ImageOps
import pytesseract

# --- 1) TESSERACT PATH (edit to match your machine) ---
# Common installs:
# r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# r"C:\Users\<you>\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\NEGAHDN\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# --- 2) INPUTS: put your two parts (folders) here ---
INPUTS = [
    r"C:\Users\NEGAHDN\Downloads\New folder (2)",   # folder with PNG/JPG screenshots (batch 2)
]

# If you want, you can list individual files instead:
# INPUTS = [r"C:\path\to\img1.png", r"C:\path\to\img2.png", ...]

# --- 3) TAGS OF INTEREST ---
TAGS = {"RH-OG2PSU-RT", "RH-OG3PSU-RT", "RH-OG4PSU-RT"}

# --- OCR helper ---
def ocr_image(path: str) -> str:
    img = Image.open(path)
    gray = ImageOps.grayscale(img)
    sharp = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
    # psm 6: assume a block of text; good for tables
    return pytesseract.image_to_string(sharp, config="--psm 6")

# --- Collect image files from folders or list ---
def collect_images(inputs):
    files = []
    for p in inputs:
        if os.path.isdir(p):
            files.extend(glob.glob(os.path.join(p, "*.png")))
            files.extend(glob.glob(os.path.join(p, "*.jpg")))
            files.extend(glob.glob(os.path.join(p, "*.jpeg")))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"⚠️ Not found: {p}")
    # sort for stable order
    return sorted(set(files), key=lambda x: (os.path.dirname(x), os.path.basename(x)))

# --- Parse all OCR text into rows ---
def parse_rows(text: str):
    rows = []
    current_tag = None
    current_unit = None

    # Pattern 1: header line with tag after DATE TIME
    header_pat = re.compile(r"DATE\s+TIME\s+([A-Z0-9\-]+)", re.I)

    # Pattern 2: tag-only line (enforce hyphenated to avoid words like Interrupt/LO/HI)
    tag_only_pat = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+){1,}$")

    # Units can vary; accept common uppercase tokens (let’s keep it optional)
    unit_pat = re.compile(r"^\s*([A-Z%/\-\u00B0]{2,})\s*$")

    # Data line like: 1-OCT-2024  0:00:00  32.55  (ignore trailing tokens)
    data_pat = re.compile(
        r"(\d{1,2}-[A-Z]{3}-\d{4})\s+(\d{1,2}:\d{2}:\d{2})\s+(-?\d+(?:\.\d+)?)",
        re.I
    )

    for raw in text.splitlines():
        line = raw.strip().replace("—", "-").replace("–", "-")
        if not line:
            continue

        # Header with tag
        hm = header_pat.search(line)
        if hm:
            current_tag = hm.group(1).upper()
            current_unit = None
            continue

        # Tag-only line (fallback)
        if tag_only_pat.match(line):
            # Only accept if it looks like one of our hyphenated tags
            current_tag = line.upper()
            current_unit = None
            continue

        # A simple "unit" line right after header sometimes appears (optional)
        um = unit_pat.match(line)
        if um and current_tag:
            # Avoid common alarm tokens that OCR might read as caps too
            if um.group(1) not in {"LO", "HI", "HIHI", "LOW", "HIGH", "INTERRUPT"}:
                current_unit = um.group(1)
            continue

        # Data row
        dm = data_pat.match(line)
        if dm and current_tag:
            date, time, val = dm.groups()
            try:
                value = float(val)
            except ValueError:
                continue
            rows.append({
                "TAG": current_tag,
                "UNIT": current_unit or "",
                "DATE": date,
                "TIME": time,
                "VALUE": value
            })

    return rows

def main():
    files = collect_images(INPUTS)
    if not files:
        raise SystemExit("No images found. Update INPUTS.")

    print(f"OCR on {len(files)} file(s)...")
    all_text = []
    for f in files:
        print(f" • {f}")
        try:
            all_text.append(ocr_image(f))
        except Exception as e:
            print(f"   ⚠️ OCR failed: {e}")

    combined = "\n".join(all_text)
    rows = parse_rows(combined)
    if not rows:
        raise SystemExit("No rows parsed. Check Tesseract path and screenshots.")

    df = pd.DataFrame(rows)
    # Filter only the three requested tags
    df = df[df["TAG"].isin(TAGS)].copy()
    if df.empty:
        raise SystemExit("No data for requested tags. Verify the screenshots show RH-OG2PSU-RT/3/4.")

    # Build a proper datetime for sorting/aligning
    df["DATETIME"] = pd.to_datetime(
        df["DATE"] + " " + df["TIME"],
        format="%d-%b-%Y %H:%M:%S",
        errors="coerce"
    )
    df = df.dropna(subset=["DATETIME"]).sort_values(["DATETIME", "TAG"])

    # --- WIDE (All 3 Points): index = DATETIME, columns = TAG ---
    wide = df.pivot_table(index="DATETIME", columns="TAG", values="VALUE", aggfunc="first")
    wide = wide.reset_index()

    # Output
    out_xlsx = os.path.join(os.path.dirname(__file__), "RH_PSU_RT_from_screenshots.xlsx")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as xw:
        # Wide sheet with all three points aligned by timestamp
        wide.to_excel(xw, sheet_name="All 3 Points", index=False)

        # Individual sheets
        for tag, sub in df.groupby("TAG"):
            sub = sub.sort_values("DATETIME")
            sub = sub[["DATE", "TIME", "VALUE", "UNIT"]]
            sub.to_excel(xw, sheet_name=tag[:31], index=False)

    print(f"✅ Saved: {out_xlsx}")

if __name__ == "__main__":
    main()
