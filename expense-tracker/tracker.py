import csv
import os
from datetime import datetime

FILE = "expenses.csv"

def init_file():
    """Create the file with headers if it doesn't exist."""
    if not os.path.exists(FILE):
        with open(FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Note"])

def add_expense(category, amount, note=""):
    """Add a new expense entry."""
    with open(FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), category, amount, note])
    print(f"✅ Added: {amount} in {category} ({note})")

def view_expenses():
    """View all expenses with totals."""
    total = 0
    if not os.path.exists(FILE):
        print("No expenses logged yet.")
        return
    with open(FILE, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"{row['Date']} | {row['Category']} | ${row['Amount']} | {row['Note']}")
            total += float(row["Amount"])
    print(f"\n💰 Total spent: ${total:.2f}")

def menu():
    init_file()
    while True:
        print("\n--- Expense Tracker ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            category = input("Category: ")
            amount = float(input("Amount: "))
            note = input("Note (optional): ")
            add_expense(category, amount, note)
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    menu()
