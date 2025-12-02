import time
import threading
from queue import Queue
import tkinter as tk
from tkinter import messagebox

# ------------------------------
# Process Class
# ------------------------------
class Process:
    def __init__(self, name):
        self.name = name

# ------------------------------
# IPC Mechanisms
# ------------------------------

class Pipe:
    def __init__(self):
        self.buffer = []

    def send(self, msg):
        self.buffer.append(msg)
        return True

    def receive(self):
        if self.buffer:
            return self.buffer.pop(0)
        return None


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


class SharedMemory:
    def __init__(self):
        self.memory = None

    def write(self, data):
        self.memory = data

    def read(self):
        return self.memory


# ------------------------------
# Debugging Engine
# ------------------------------
class DebugEngine:
    def detect_deadlock(self, log_data):
        wait_events = [x for x in log_data if "BLOCKED" in x]
        if len(wait_events) >= 2:
            return True
        return False


# ------------------------------
# GUI and Simulator
# ------------------------------
class IPCDebuggerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("IPC Debugger Simulator")
        self.root.geometry("900x600")

        # Logs
        self.log_box = tk.Text(self.root, height=20, width=100)
        self.log_box.pack()

        # Buttons
        tk.Button(self.root, text="Run Simulation", command=self.simulate).pack()

        self.debug_engine = DebugEngine()
        self.logs = []

        self.root.mainloop()

    # Add logs to window and memory
    def log(self, msg):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.logs.append(msg)
        self.log_box.insert(tk.END, timestamp + msg + "\n")

    # Simulation function
    def simulate(self):
        self.log("Starting Simulation...")

        # Create message queue
        mq = MessageQueue(2)

        # Send messages
        self.log("Sending message 1: " + str(mq.send("MSG1")))
        self.log("Sending message 2: " + str(mq.send("MSG2")))
        self.log("Sending message 3 (queue full): " + str(mq.send("MSG3 BLOCKED")))

        # Detect deadlock
        if self.debug_engine.detect_deadlock(self.logs):
            self.log("DEADLOCK DETECTED!")
            messagebox.showwarning("Warning", "Deadlock Detected in IPC Simulation")

        # Receive messages
        self.log("Receiving: " + str(mq.receive()))
        self.log("Receiving: " + str(mq.receive()))
        self.log("Simulation Completed.")


# Run GUI
IPCDebuggerGUI()
