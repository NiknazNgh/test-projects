import tkinter as tk
import time
import threading

WORK_MIN = 25   # minutes
BREAK_MIN = 5   # minutes

running = False
remaining = WORK_MIN * 60

def start_timer():
    global running
    if not running:
        running = True
        thread = threading.Thread(target=run_timer)
        thread.start()

def reset_timer():
    global running, remaining
    running = False
    remaining = WORK_MIN * 60
    update_display()

def run_timer():
    global remaining, running
    while running and remaining > 0:
        time.sleep(1)
        remaining -= 1
        update_display()
    if remaining == 0 and running:
        running = False
        label_status.config(text="Time’s up! Take a break!")

def update_display():
    minutes = remaining // 60
    seconds = remaining % 60
    timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

root = tk.Tk()
root.title("⏰ Pomodoro Timer")
root.geometry("250x150")

label_status = tk.Label(root, text="Ready to focus?", font=("Arial", 12))
label_status.pack(pady=10)

timer_label = tk.Label(root, text="25:00", font=("Arial", 24))
timer_label.pack()

btn_start = tk.Button(root, text="Start", command=start_timer)
btn_start.pack(side="left", padx=20, pady=20)

btn_reset = tk.Button(root, text="Reset", command=reset_timer)
btn_reset.pack(side="right", padx=20, pady=20)

root.mainloop()
