import tkinter as tk
from tkinter import filedialog, messagebox

def new_note():
    text.delete("1.0", tk.END)

def save_note():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", tk.END))
        messagebox.showinfo("Saved", f"Note saved to {file_path}")

def open_note():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        text.delete("1.0", tk.END)
        text.insert(tk.END, content)

root = tk.Tk()
root.title("📝 Notes App")
root.geometry("400x400")

# Buttons
frame = tk.Frame(root)
frame.pack(pady=10)

btn_new = tk.Button(frame, text="New", command=new_note)
btn_new.pack(side=tk.LEFT, padx=5)

btn_open = tk.Button(frame, text="Open", command=open_note)
btn_open.pack(side=tk.LEFT, padx=5)

btn_save = tk.Button(frame, text="Save", command=save_note)
btn_save.pack(side=tk.LEFT, padx=5)

# Text area
text = tk.Text(root, wrap="word")
text.pack(expand=True, fill="both")

root.mainloop()
