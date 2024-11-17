import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

class Task:
    def __init__(self, text, state="To-Do"):
        self.text = text
        self.state = state

    def to_dict(self):
        return {"text": self.text, "state": self.state}

    @staticmethod
    def from_dict(data):
        return Task(data["text"], data["state"])

class TaskManager:
    FILE_PATH = "tasks.json"

    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def add_task(self, text):
        task = Task(text)
        self.tasks.append(task)
        self.save_tasks()

    def remove_task(self, task):
        self.tasks.remove(task)
        self.save_tasks()

    def save_tasks(self):
        with open(self.FILE_PATH, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f)

    def load_tasks(self):
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as f:
                self.tasks = [Task.from_dict(data) for data in json.load(f)]

class KanbanApp:
    def __init__(self, root):
        self.root = root
        self.task_manager = TaskManager()
        self.root.title("Kanban Task Manager")
        self.center_window()
        self.create_widgets()
        self.populate_tasks()

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.75)
        height = int(screen_height * 0.75)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        self.frames = {}
        for state in ["To-Do", "Doing", "Done"]:
            # Create a frame for each state with a border
            frame = tk.Frame(
                self.root,
                bg="lightblue",  # Set a background color for clarity
                padx=5, pady=5,
                relief="solid",  # Add a solid border
                bd=2  # Border thickness
            )
            frame.pack(side="left", fill="both", expand=True)

            # Add a label for the state title
            label = tk.Label(
                frame,
                text=state,
                bg="gray",
                fg="white",
                font=("Arial", 14, "bold")
            )
            label.pack(fill="x")
            self.frames[state] = frame

        # Add button to add tasks
        self.add_button = tk.Button(
            self.root,
            text="Add Task",
            command=self.add_task,
            font=("Arial", 12),
            bg="green",
            fg="white"
        )
        self.add_button.pack(side="bottom", fill="x")

    def populate_tasks(self):
        for frame in self.frames.values():
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text") not in ["To-Do", "Doing", "Done"]:
                    widget.destroy()

        for task in self.task_manager.tasks:
            self.create_task_widget(task)

    def create_task_widget(self, task):
        frame = self.frames[task.state]
        task_label = tk.Label(frame, text=task.text, bg="white", relief="raised", pady=5)
        task_label.pack(fill="x", pady=2)

        task_label.bind("<Button-1>", lambda e: self.start_drag(e, task, task_label))

    def start_drag(self, event, task, widget):
        # Store drag-related data
        self.drag_data = {
            "task": task,
            "widget": widget,
            "start_x": event.x,
            "start_y": event.y,
            "orig_x": widget.winfo_x(),
            "orig_y": widget.winfo_y(),
            "width": widget.winfo_width(),
            "height": widget.winfo_height(),
        }

        # Place the widget above others and maintain its size
        widget.lift()
        widget.place(
            x=self.drag_data["orig_x"],
            y=self.drag_data["orig_y"],
            width=self.drag_data["width"],
            height=self.drag_data["height"]
        )

        # Bind mouse motion and release events
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.end_drag)

    def on_drag(self, event):
        widget = self.drag_data["widget"]

        # Calculate new widget position based on mouse movement
        x = widget.winfo_x() + (event.x - self.drag_data["start_x"])
        y = widget.winfo_y() + (event.y - self.drag_data["start_y"])

        # Move the widget with the mouse and maintain its size
        widget.place(
            x=x,
            y=y,
            width=self.drag_data["width"],
            height=self.drag_data["height"]
        )

    def end_drag(self, event):
        widget = self.drag_data["widget"]
        task = self.drag_data["task"]

        # Determine which frame the task is dropped into
        for state, frame in self.frames.items():
            frame_x1 = frame.winfo_rootx()
            frame_y1 = frame.winfo_rooty()
            frame_x2 = frame_x1 + frame.winfo_width()
            frame_y2 = frame_y1 + frame.winfo_height()

            if frame_x1 <= event.x_root <= frame_x2 and frame_y1 <= event.y_root <= frame_y2:
                task.state = state
                self.task_manager.save_tasks()
                break

        # Refresh the UI to update task positions
        self.populate_tasks()

        # Unbind drag events
        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")

    def add_task(self):
        text = simpledialog.askstring("New Task", "Enter task description:")
        if text:
            self.task_manager.add_task(text)
            self.populate_tasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = KanbanApp(root)
    root.mainloop()
