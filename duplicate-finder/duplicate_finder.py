import os
import hashlib

FOLDER = r"C:\Users\NEGAHDN\Downloads\test projects\important_files"  # change this path

def file_hash(path):
    """Generate a SHA256 hash of a file."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def find_duplicates(folder):
    seen = {}
    duplicates = []

    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            try:
                hash_val = file_hash(path)
            except Exception as e:
                print(f"⚠️ Skipped {file}: {e}")
                continue

            if hash_val in seen:
                duplicates.append((path, seen[hash_val]))
            else:
                seen[hash_val] = path

    if duplicates:
        print("\n🧩 Found duplicates:")
        for dup, original in duplicates:
            print(f"→ {dup}\n   ↳ same as: {original}\n")
    else:
        print("✅ No duplicates found.")

    return duplicates

def delete_duplicates(duplicates):
    for dup, _ in duplicates:
        try:
            os.remove(dup)
            print(f"🗑️ Deleted: {dup}")
        except Exception as e:
            print(f"❌ Could not delete {dup}: {e}")

if __name__ == "__main__":
    dups = find_duplicates(FOLDER)
    if dups:
        confirm = input("Do you want to delete duplicates? (y/n): ").strip().lower()
        if confirm == "y":
            delete_duplicates(dups)
            print("✅ Cleanup complete.")
