import tkinter as tk
from tkinter import colorchooser, messagebox

palette = []

def pick_color():
    color_code = colorchooser.askcolor(title="Choose a color")
    if color_code[1]:  # hex value
        palette.append(color_code[1])
        update_palette()

def update_palette():
    palette_box.delete(0, tk.END)
    for c in palette:
        palette_box.insert(tk.END, c)

def copy_color():
    try:
        selected = palette_box.get(palette_box.curselection())
        root.clipboard_clear()
        root.clipboard_append(selected)
        messagebox.showinfo("Copied", f"{selected} copied to clipboard!")
    except:
        messagebox.showwarning("No selection", "Please select a color first.")

root = tk.Tk()
root.title("🎨 Color Picker")
root.geometry("300x300")

btn_pick = tk.Button(root, text="Pick a Color", command=pick_color)
btn_pick.pack(pady=10)

palette_box = tk.Listbox(root, height=10)
palette_box.pack(fill="both", expand=True, padx=10)

btn_copy = tk.Button(root, text="Copy Selected Color", command=copy_color)
btn_copy.pack(pady=10)

root.mainloop()
