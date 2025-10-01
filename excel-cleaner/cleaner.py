import pandas as pd

def clean_excel(input_file, output_file):
    df = pd.read_excel(input_file)

    # Drop empty rows
    df.dropna(how="all", inplace=True)

    # Drop duplicate rows
    df.drop_duplicates(inplace=True)

    # Strip whitespace in all string columns
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.strip()

    # Reset index
    df.reset_index(drop=True, inplace=True)

    df.to_excel(output_file, index=False)
    print(f"✅ Cleaned data saved to {output_file}")

if __name__ == "__main__":
    clean_excel("messy_data.xlsx", "cleaned_data.xlsx")
