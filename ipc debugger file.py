import tkinter as tk
from tkinter import messagebox
import time
from queue import Queue

# -------------------------
# DATA MODELS
# -------------------------

class Process:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y


class MessageQueue:
    def __init__(self, size):
        self.q = Queue(maxsize=size)

    def send(self, msg):
        try:
            self.q.put(msg, block=False)
            return True
        except:
            return False

    def receive(self):
        try:
            return self.q.get(block=False)
        except:
            return None


# -------------------------
# DEBUG ENGINE
# -------------------------

class DebugEngine:
    def detect_deadlock(self, logs):
        block_count = sum("BLOCKED" in log for log in logs)
        return block_count >= 1   # Simple deadlock detection


# -------------------------
# IPC DEBUGGER GUI
# -------------------------

class IPCDebugger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced IPC Debugger Simulator")
        self.root.geometry("1100x650")

        self.processes = []
        self.links = []
        self.logs = []

        self.msg_queue = MessageQueue(2)
        self.debug_engine = DebugEngine()

        self.setup_ui()
        self.root.mainloop()

    # -------------------------
    # UI SETUP
    # -------------------------
    def setup_ui(self):
        # Main Layout
        left_frame = tk.Frame(self.root, width=750, height=600)
        right_frame = tk.Frame(self.root, width=350, height=600)
        left_frame.pack(side="left", fill="both")
        right_frame.pack(side="right", fill="both")

        # Canvas for Visualization
        self.canvas = tk.Canvas(left_frame, bg="white", width=750, height=600)
        self.canvas.pack(fill="both", expand=True)

        # Log Box
        tk.Label(right_frame, text="Debugger Logs", font=("Arial", 14)).pack()
        self.log_box = tk.Text(right_frame, height=25, width=40)
        self.log_box.pack()

        # Input field for messages
        tk.Label(right_frame, text="Enter Message:", font=("Arial", 12)).pack(pady=5)
        self.msg_entry = tk.Entry(right_frame, width=30, font=("Arial", 12))
        self.msg_entry.pack(pady=5)

        # Control Buttons
        tk.Button(right_frame, text="Add Process", command=self.add_process).pack(pady=10)
        tk.Button(right_frame, text="Create Queue Link", command=self.create_link).pack(pady=10)
        tk.Button(right_frame, text="Send Message", command=self.send_message).pack(pady=10)
        tk.Button(right_frame, text="Run Demo Simulation", command=self.demo_simulation).pack(pady=10)

    # -------------------------
    # LOGGING FUNCTION
    # -------------------------
    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.logs.append(message)
        self.log_box.insert(tk.END, timestamp + message + "\n")
        self.log_box.see(tk.END)

    # -------------------------
    # ADD PROCESS NODE
    # -------------------------
    def add_process(self):
        name = f"P{len(self.processes) + 1}"
        x, y = 100 + len(self.processes) * 150, 100
        process = Process(name, x, y)
        self.processes.append(process)

        self.draw_process(process)
        self.log(f"Process {name} added.")

    def draw_process(self, p):
        radius = 30
        self.canvas.create_oval(
            p.x - radius, p.y - radius,
            p.x + radius, p.y + radius,
            fill="lightblue", outline="black", width=2, tags=p.name
        )
        self.canvas.create_text(p.x, p.y, text=p.name, tags=p.name)

    # -------------------------
    # CREATE IPC LINK
    # -------------------------
    def create_link(self):
        if len(self.processes) < 2:
            messagebox.showwarning("Error", "Need at least 2 processes.")
            return

        p1 = self.processes[-2]
        p2 = self.processes[-1]

        self.links.append((p1, p2))
        self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, width=3, arrow=tk.LAST)
        self.log(f"Queue link created between {p1.name} and {p2.name}")

    # -------------------------
    # SEND MESSAGE WITH ANIMATION
    # -------------------------
    def send_message(self):
        if not self.links:
            messagebox.showwarning("Error", "No IPC link exists.")
            return

        user_msg = self.msg_entry.get().strip()

        if user_msg == "":
            messagebox.showwarning("Input Error", "Please enter a message to send.")
            return

        p1, p2 = self.links[-1]

        if self.msg_queue.send(user_msg):
            self.log(f"{p1.name} → {p2.name}: Sent '{user_msg}'")
            self.animate_message(p1, p2, user_msg)
            self.msg_entry.delete(0, tk.END)
        else:
            self.log(f"{p1.name} BLOCKED while sending '{user_msg}'")
            self.canvas.create_text(350, 300, text="DEADLOCK!", font=("Arial", 30), fill="red")
            messagebox.showerror("Deadlock Detected", "Queue overflow! Deadlock detected.")

    # -------------------------
    # MESSAGE ANIMATION
    # -------------------------
    def animate_message(self, p1, p2, msg):
        x, y = p1.x, p1.y
        dx = (p2.x - p1.x) / 40
        dy = (p2.y - p1.y) / 40

        msg_obj = self.canvas.create_text(x, y, text=msg, font=("Arial", 12), fill="green")

        def move_step(step=0):
            if step < 40:
                self.canvas.move(msg_obj, dx, dy)
                self.root.after(30, move_step, step + 1)
            else:
                self.canvas.delete(msg_obj)
                self.log(f"{p2.name} received '{msg}'")

        move_step()

    # -------------------------
    # DEMO SIMULATION
    # -------------------------
    def demo_simulation(self):
        self.add_process()
        self.add_process()
        self.create_link()
        self.msg_entry.insert(0, "Hello")
        self.send_message()
        self.msg_entry.insert(0, "Data2")
        self.send_message()
        self.msg_entry.insert(0, "Data3")  # Should overflow and deadlock
        self.send_message()


# Start simulator
IPCDebugger()

