import tkinter as tk
from tkinter import ttk , messagebox, colorchooser, filedialog
from tkcalendar import Calendar, DateEntry
import sqlite3
import random

# --- Database Setup ---
DATABASE = "tasks.db"
conn = sqlite3.connect(DATABASE)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    priority TEXT,
    due_date TEXT,
    x INTEGER,
    y INTEGER,
    font_size INTEGER,
    font_style TEXT,
    fg_color TEXT,
    bg_color TEXT
)''')

# --- Color Palette ---
color_palette = {
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Yellow": "#FFFF00",
    "Cyan": "#00FFFF",
    "Magenta": "#FF00FF",
    "Black": "#000000",
    "White": "#FFFFFF",
    "LightGray": "#D3D3D3",
}

# --- Task Class ---


class Task:
    def __init__(self, canvas, task_data):
        self.canvas = canvas
        self.id = task_data[0]
        self.task = task_data[1]
        self.priority = task_data[2]
        self.due_date = task_data[3]
        self.x = task_data[4]
        self.y = task_data[5]
        self.font_size = task_data[6]
        self.font_style = task_data[7]
        self.fg_color = task_data[8]
        self.bg_color = task_data[9]

        try:
            self.font_size = int(self.font_size)
        except ValueError:
            self.font_size = 12

        self.font = (self.font_style, self.font_size)

        # Draw initial background rectangle
        self.bg_rect = self.canvas.create_rectangle(
            self.x, self.y, self.x + 200+self.font_size * 0.5, self.y + self.font_size * 2,
            fill=self.bg_color, outline=""
        )

        # Draw text on the canvas
        self.canvas_item = self.canvas.create_text(
            self.x + 5, self.y + 5,
            text=self.task,
            anchor=tk.NW,
            fill=self.fg_color,
            font=self.font,
            tags=f"task_{self.id}"
        )

        self.update_bg_rect()  # Update rectangle size based on text width

        self.canvas.tag_bind(f"task_{self.id}", "<Button-1>", self.start_move)
        self.canvas.tag_bind(f"task_{self.id}", "<B1-Motion>", self.move_task)
        self.canvas.tag_bind(
            f"task_{self.id}", "<ButtonRelease-1>", self.stop_move)
        self.canvas.tag_bind(f"task_{self.id}", "<Enter>", self.show_details)
        self.canvas.tag_bind(f"task_{self.id}", "<Leave>", self.hide_details)
        self.canvas.tag_bind(
            f"task_{self.id}", "<Button-3>", self.show_edit_menu)

        # Initial details window (hidden)
        self.details_window = tk.Toplevel(self.canvas)
        self.details_window.withdraw()  # Hide it initially
        self.details_window.wm_overrideredirect(True)  # Remove title bar
        self.details_label = tk.Label(
            self.details_window, text=self.get_details(), bg="white", wraplength=200
        )
        self.details_label.pack(pady=5)

    def update_bg_rect(self):
        # Calculate text width
        bbox = self.canvas.bbox(self.canvas_item)
        text_width = bbox[2] - bbox[0]

        # Update the background rectangle size
        self.canvas.coords(self.bg_rect, self.x, self.y,
                           self.x + text_width + 10+self.font_size * 0.5, self.y + self.font_size * 2)  # +10 for padding

    def start_move(self, event):
        self.x, self.y = self.canvas.coords(self.canvas_item)[:2]
        self.x_offset = event.x - self.x
        self.y_offset = event.y - self.y

    def move_task(self, event):
        self.x = event.x - self.x_offset
        self.y = event.y - self.y_offset
        self.canvas.coords(self.canvas_item, self.x + 5,
                           self.y + 5)  # Reposition task text
        self.update_bg_rect()  # Update background rectangle

        # Update database in real-time
        self.update_db()

    def stop_move(self, event):
        self.x = event.x - self.x_offset
        self.y = event.y - self.y_offset
        self.canvas.coords(self.canvas_item, self.x + 5,
                           self.y + 5)  # Final repositioning
        self.update_bg_rect()  # Final repositioning of background rectangle

    def show_details(self, event):
        self.details_window.deiconify()  # Show the details window
        self.details_label.config(text=self.get_details())
        self.details_window.geometry(
            f"+{event.x_root + 20}+{event.y_root + 20}")

    def hide_details(self, event):
        self.details_window.withdraw()

    def show_edit_menu(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Edit Task", command=lambda: self.edit_task())
        menu.add_separator()
        menu.add_command(label="Delete Task",
                         command=lambda: self.delete_task())
        menu.post(event.x_root, event.y_root)

    def edit_task(self):
        edit_window = tk.Toplevel(self.canvas)
        edit_window.title("Edit Task")
        edit_window.attributes("-topmost", True)

        # --- Create Edit Widgets ---
        # Task name
        tk.Label(edit_window, text="Task Name:").grid(
            row=0, column=0, padx=5, pady=5)
        task_name_entry = tk.Entry(edit_window)
        task_name_entry.insert(0, self.task)
        task_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Priority
        tk.Label(edit_window, text="Priority:").grid(
            row=1, column=0, padx=5, pady=5)
        priority_var = tk.StringVar(edit_window)
        priority_var.set(self.priority)
        priority_options = ["Low", "Medium", "High"]
        priority_dropdown = ttk.Combobox(
            edit_window, textvariable=priority_var, values=priority_options)
        priority_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # Due Date
        tk.Label(edit_window, text="Due Date:").grid(
            row=2, column=0, padx=5, pady=5)
        due_date_entry = DateEntry(
            edit_window, width=12, background="darkblue", foreground="white", borderwidth=2)
        due_date_entry.insert(0, self.due_date)
        due_date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Font Size
        tk.Label(edit_window, text="Font Size:").grid(
            row=3, column=0, padx=5, pady=5)
        font_size_entry = tk.Entry(edit_window, width=5)
        font_size_entry.insert(0, self.font_size)
        font_size_entry.grid(row=3, column=1, padx=5, pady=5)

        # Font Style
        tk.Label(edit_window, text="Font Style:").grid(
            row=4, column=0, padx=5, pady=5)
        font_style_var = tk.StringVar(edit_window)
        font_style_var.set(self.font_style)
        font_style_options = [
            "Arial", "Times New Roman", "Courier New", "Verdana"]
        font_style_dropdown = ttk.Combobox(
            edit_window, textvariable=font_style_var, values=font_style_options)
        font_style_dropdown.grid(row=4, column=1, padx=5, pady=5)

        # Foreground Color
        tk.Label(edit_window, text="Foreground Color:").grid(
            row=5, column=0, padx=5, pady=5)
        fg_color_var = tk.StringVar(edit_window)
        fg_color_var.set(self.fg_color)

        def choose_fg_color():
            color = colorchooser.askcolor(initialcolor=self.fg_color)[1]
            if color:
                fg_color_var.set(color)
        fg_color_button = tk.Button(
            edit_window, text="Choose", command=choose_fg_color)
        fg_color_button.grid(row=5, column=1, padx=5, pady=5)

        # Background Color
        tk.Label(edit_window, text="Background Color:").grid(
            row=6, column=0, padx=5, pady=5)
        bg_color_var = tk.StringVar(edit_window)
        bg_color_var.set(self.bg_color)

        def choose_bg_color():
            color = colorchooser.askcolor(initialcolor=self.bg_color)[1]
            if color:
                bg_color_var.set(color)
        bg_color_button = tk.Button(
            edit_window, text="Choose", command=choose_bg_color)
        bg_color_button.grid(row=6, column=1, padx=5, pady=5)

        def save_changes():
            self.task = task_name_entry.get()
            self.priority = priority_var.get()
            self.due_date = due_date_entry.get()
            self.font_size = int(font_size_entry.get())
            self.font_style = font_style_var.get()
            self.fg_color = fg_color_var.get()
            self.bg_color = bg_color_var.get()
            self.font = (self.font_style, self.font_size)

            self.canvas.itemconfig(
                self.canvas_item, text=self.task, font=self.font, fill=self.fg_color)
            self.canvas.itemconfig(self.bg_rect, fill=self.bg_color)
            self.update_bg_rect()
            self.update_db()
            edit_window.destroy()

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(
            row=7, columnspan=2, pady=10)

    def delete_task(self):
        self.canvas.delete(self.canvas_item)
        self.canvas.delete(self.bg_rect)
        self.details_window.destroy()

        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id=?", (self.id,))
            conn.commit()

    def get_details(self):
        return f"Task: {self.task}\nPriority: {self.priority}\nDue Date: {self.due_date}"

    def update_db(self):
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''UPDATE tasks
                         SET task=?, priority=?, due_date=?, x=?, y=?, font_size=?, font_style=?, fg_color=?, bg_color=?
                         WHERE id=?''', (self.task, self.priority, self.due_date, self.x, self.y, self.font_size, self.font_style, self.fg_color, self.bg_color, self.id))
            conn.commit()

# --- Task Manager Class ---


class TaskManager(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.tasks = []

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Tasks", command=self.save_tasks)
        file_menu.add_command(label="Load Tasks", command=self.load_tasks)
        menu_bar.add_cascade(label="File", menu=file_menu)

        add_task_frame = tk.Frame(self)
        add_task_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(add_task_frame, text="Task:").pack(
            side=tk.LEFT, padx=5, pady=5)
        self.task_entry = tk.Entry(add_task_frame)
        self.task_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(add_task_frame, text="Priority:").pack(
            side=tk.LEFT, padx=5, pady=5)
        self.priority_var = tk.StringVar(add_task_frame)
        self.priority_var.set("Medium")
        priority_options = ["Low", "Medium", "High"]
        self.priority_dropdown = ttk.Combobox(
            add_task_frame, textvariable=self.priority_var, values=priority_options)
        self.priority_dropdown.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(add_task_frame, text="Due Date:").pack(
            side=tk.LEFT, padx=5, pady=5)
        self.due_date_entry = DateEntry(
            add_task_frame, width=12, background="darkblue", foreground="white", borderwidth=2)
        self.due_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(add_task_frame, text="Add Task", command=self.add_task).pack(
            side=tk.LEFT, padx=5, pady=5)

    def add_task(self):
        task_text = self.task_entry.get()
        priority = self.priority_var.get()
        due_date = self.due_date_entry.get_date().strftime('%Y-%m-%d')

        task_data = (None, task_text, priority, due_date, random.randint(50, 500), random.randint(
            50, 300), 12, "Arial", "black", "white")
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO tasks (task, priority, due_date, x, y, font_size, font_style, fg_color, bg_color)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', task_data[1:])
            task_data = (c.lastrowid,) + task_data[1:]
            conn.commit()

        task = Task(self.canvas, task_data)
        self.tasks.append(task)

    def save_tasks(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db", filetypes=[("Database Files", "*.db")])
        if file_path:
            with sqlite3.connect(file_path) as dest_conn:
                with sqlite3.connect(DATABASE) as source_conn:
                    source_conn.backup(dest_conn)

    def load_tasks(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".db", filetypes=[("Database Files", "*.db")])
        if file_path:
            self.canvas.delete("all")
            self.tasks.clear()
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM tasks")
                conn.commit()

            with sqlite3.connect(file_path) as source_conn:
                with sqlite3.connect(DATABASE) as dest_conn:
                    source_conn.backup(dest_conn)

            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM tasks")
                for row in c.fetchall():
                    task = Task(self.canvas, row)
                    self.tasks.append(task)


# --- Main Application ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Task Manager")
    root.geometry("800x600")
    app = TaskManager(master=root)
    app.mainloop()
app.save_tasks()
