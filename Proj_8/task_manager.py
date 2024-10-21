import pygame
import random
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import colorchooser, ttk, messagebox, filedialog
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar
import json

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600  # Increased width for task details
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Task Manager")

clock = pygame.time.Clock()
DATABASE = "tasks.db"

class Task:
    def __init__(self, x, y, name, description, due_date=None, font_size=20, font_color=(255, 255, 255), bg_color=(0, 0, 0), font_type='Arial'):
        self.name = name
        self.description = description
        self.due_date = due_date if due_date else datetime.now().strftime("%Y-%m-%d")  # Default to today's date
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.font_type = font_type
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.text = self.font.render(self.name, True, self.font_color)
        self.rect = self.text.get_rect(center=(x, y))
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect.inflate(10, 10))
        screen.blit(self.text, self.rect)


    def update(self):
        """Update the task's text and rectangle based on current attributes."""
        self.font = pygame.font.SysFont(self.font_type, self.font_size)  # Update font with new size and type
        self.text = self.font.render(self.name, True, self.font_color)
        self.rect = self.text.get_rect(topleft=(self.rect.topleft))  # Update the rectangle based on the new text

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'due_date': self.due_date,
            'font_size': self.font_size,
            'font_color': list(self.font_color),  # Store as a list
            'bg_color': list(self.bg_color),      # Store as a list
            'font_type': self.font_type,
            'center': {'x': self.rect.centerx, 'y': self.rect.centery}  # Store top-left position
        }

class TaskEditor:
    def __init__(self, task, task_manager):
        self.task = task
        self.task_manager = task_manager  # Store the reference to TaskManager
        self.input_fields = {
            "name": task.name,
            "description": task.description,
            "due_date": task.due_date,
            "font_size": str(task.font_size),
        }
        self.active_field = None
        self.fonts = list(pygame.font.get_fonts())
        self.selected_font_color = task.font_color
        self.selected_bg_color = task.bg_color

        # Create a new Tkinter window
        self.root = tk.Tk()
        self.root.title("Task Editor")
        self.root.geometry("300x500")  # Increased height for the editor
        self.root.resizable(False, False)  # Make the window non-resizable
        self.root.configure(bg="#2E2E2E")

        # Create UI elements
        self.create_widgets()

        # Bind the close event to the on_close method
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.is_closed = False  # Flag to indicate if the window is closed

    def create_widgets(self):
        # Create labels and entry fields
        for field, value in self.input_fields.items():
            label = tk.Label(self.root, text=field.capitalize(), bg="#2E2E2E", fg="white")
            label.pack(pady=5)

            if field == "description":
                # Use a Text widget for the description
                self.description_text = tk.Text(self.root, height=4, width=30)  # Larger input
                self.description_text.insert(tk.END, value)
                self.description_text.pack(pady=5)
            elif field == "due_date":
                # Use DateEntry for the due date
                self.due_date_entry = DateEntry(self.root, width=27, background='darkblue', foreground='white', borderwidth=2)
                self.due_date_entry.set_date(datetime.strptime(value, "%Y-%m-%d"))  # Set the current date
                self.due_date_entry.pack(pady=5)
            else:
                entry = tk.Entry(self.root)
                entry.insert(0, value)
                entry.pack(pady=5)
                self.input_fields[field] = entry  # Replace with Entry widget

        # Font type selection
        self.font_type_label = tk.Label(self.root, text="Font Type", bg="#2E2E2E", fg="white")
        self.font_type_label.pack(pady=5)
        self.font_type_combobox = ttk.Combobox(self.root, values=self.fonts)
        self.font_type_combobox.set(self.task.font_type)  # Set the current font type
        self.font_type_combobox.pack(pady=5)

        # Create color buttons
        self.font_color_button = tk.Button(self.root, text="Pick Font Color", command=self.pick_font_color, bg="#4CAF50", fg="white")
        self.font_color_button.pack(pady=5)

        self.bg_color_button = tk.Button(self.root, text="Pick Background Color", command=self.pick_bg_color, bg="#4CAF50", fg="white")
        self.bg_color_button.pack(pady=5)

    def pick_font_color(self):
        color = colorchooser.askcolor()[0]  # Returns a tuple (R, G, B)
        if color:
            self.selected_font_color = tuple(int(c) for c in color)

    def pick_bg_color(self):
        color = colorchooser.askcolor()[0]  # Returns a tuple (R, G, B)
        if color:
            self.selected_bg_color = tuple(int(c) for c in color)

    def on_close(self):
        # Update task attributes from input fields
        self.task.name = self.input_fields["name"].get()
        self.task.description = self.description_text.get("1.0", tk.END).strip()  # Get text from Text widget
        self.task.due_date = self.due_date_entry.get()  # Get date from DateEntry
        
        # Convert the date to the correct format before saving
        try:
            self.task.due_date = datetime.strptime(self.task.due_date, "%m/%d/%y").strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Setting to today's date.")
            self.task.due_date = datetime.now().strftime("%Y-%m-%d")  # Fallback to today's date if parsing fails
        
        # Handle font size conversion
        try:
            self.task.font_size = int(self.input_fields["font_size"].get().strip('` '))  # Remove backticks and whitespace
        except ValueError:
            print("Invalid font size. Setting to default (20).")
            self.task.font_size = 20  # Default value if conversion fails

        # Set the task colors from the selected values
        self.task.font_color = self.selected_font_color
        self.task.bg_color = self.selected_bg_color
        
        # Get font type from combobox
        self.task.font_type = self.font_type_combobox.get()

        # Update the task display
        self.task.update()  # Update the task's text and rect based on new attributes
        
        # Save tasks in the task manager
        self.task_manager.save_tasks()  # Auto-save after changes
        
        # Clear the database after closing the editor
        self.task_manager.clear_tasks()  # Clear the tasks from the database
        
        self.is_closed = True  # Set the flag to indicate the window is closed
        self.root.destroy()  # Close the Tkinter window

    def run(self):
        while not self.is_closed:
            try:
                self.root.update()  # Keep the Tkinter window responsive
            except tk.TclError:
                break  # Break the loop if the window is destroyed

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.selected_task = None
        self.create_table()
        self.editor_open = False  # Flag to track if the editor is open

    def create_table(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                          (id INTEGER PRIMARY KEY,
                           name TEXT,
                           description TEXT,
                           due_date TEXT,
                           x INTEGER,
                           y INTEGER,
                           font_size INTEGER,
                           font_color TEXT,
                           bg_color TEXT,
                           font_type TEXT)''')
        conn.commit()
        conn.close()

    def load_tasks(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        for row in rows:
            # Ensure the due date is valid
            due_date = row[3] if row[3] and row[3] != 'Due Date' else datetime.now().strftime("%Y-%m-%d")
            task = Task(row[4], row[5], row[1], row[2], due_date, row[6], eval(row[7]), eval(row[8]), row[9])
            self.tasks.append(task)
        conn.close()

    def save_tasks(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        for task in self.tasks:
            cursor.execute('''INSERT INTO tasks 
                              (name, description, due_date, x, y, font_size, font_color, bg_color, font_type)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (task.name, task.description, task.due_date, 
                            task.rect.centerx, task.rect.centery, 
                            task.font_size, str(task.font_color), str(task.bg_color), task.font_type))
        conn.commit()
        conn.close()

    def add_task(self, x, y):
        due_date = datetime.now().strftime("%Y-%m-%d")
        task = Task(x, y, "New Task", "Description", due_date)
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task):
        self.tasks.remove(task)
        self.save_tasks()

    def open_task_editor(self, task):
        if not self.editor_open:  # Check if the editor is already open
            self.editor_open = True
            editor = TaskEditor(task, self)  # Pass the TaskManager instance to TaskEditor
            editor.run()  # Run the Tkinter editor
            self.editor_open = False  # Reset the flag when the editor is closed

    def handle_events(self, event):
        detail_panel_rect = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)  # Define the details bar area

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for task in self.tasks:
                    if task.rect.collidepoint(event.pos):
                        # Check if dragging the task would cause it to collide with the details bar
                        if not task.rect.colliderect(detail_panel_rect):
                            self.selected_task = task
                            task.dragging = True
                            # Calculate the offset between the mouse position and the task's rectangle
                            task.offset_x = event.pos[0] - task.rect.x
                            task.offset_y = event.pos[1] - task.rect.y
                        break
                else:
                    self.selected_task = None
            elif event.button == 3:  # Right click
                if not self.selected_task:
                    self.add_task(*event.pos)
                else:
                    self.open_task_editor(self.selected_task)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selected_task:
                self.selected_task.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.selected_task and self.selected_task.dragging:
                # Update the task's position based on the mouse position and the offset
                new_x = event.pos[0] - self.selected_task.offset_x
                new_y = event.pos[1] - self.selected_task.offset_y
                # Check if the new position would collide with the details bar
                if not self.selected_task.rect.move(new_x - self.selected_task.rect.x, new_y - self.selected_task.rect.y).colliderect(detail_panel_rect):
                    self.selected_task.rect.topleft = (new_x, new_y)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE and self.selected_task:
                self.delete_task(self.selected_task)
                self.selected_task = None
            elif event.key == pygame.K_s:  # Press 'S' to save tasks to a file
                self.save_to_file()
            elif event.key == pygame.K_l:  # Press 'L' to load tasks from a file
                self.load_from_file()

    def draw(self, screen):
        for task in self.tasks:
            task.draw(screen)
        if self.selected_task:
            pygame.draw.rect(screen, (255, 0, 0), self.selected_task.rect, 2)

    def save_to_file(self):
        """Save tasks to a JSON file using a file dialog."""
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                                  filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            with open(filename, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f)

    def load_from_file(self):
        """Load tasks from a JSON file using a file dialog."""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    tasks_data = json.load(f)
                    self.tasks = []
                    for task_data in tasks_data:
                        task = Task(
                            task_data['center']['x'],  # Use the center position for x
                            task_data['center']['y'],  # Use the center position for y
                            task_data['name'],
                            task_data['description'],
                            task_data['due_date'],
                            task_data['font_size'],
                            tuple(task_data['font_color']),  # Convert list back to tuple
                            tuple(task_data['bg_color']),     # Convert list back to tuple
                            task_data['font_type']
                        )
                        self.tasks.append(task)
                    self.save_tasks()  # Save to the database after loading
            except json.JSONDecodeError as e:
                print(f"Error loading tasks: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    def clear_tasks(self):
        """Clear all tasks from the database."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")  # Clear the tasks table
        conn.commit()
        conn.close()

class TaskManagerApp:
    def __init__(self):
        self.task_manager = TaskManager()
        self.task_manager.load_tasks()
        self.selected_task = None  # Track the selected task

        # Create a Tkinter window for buttons
        self.root = tk.Tk()
        self.root.title("Task Manager Controls")
        self.root.geometry("200x100")  # Size of the control window
        self.root.configure(bg="#2E2E2E")

        # Create Save and Load buttons
        self.save_button = tk.Button(self.root, text="Save Tasks", command=self.save_tasks, bg="#4CAF50", fg="white")
        self.save_button.pack(pady=5)

        self.load_button = tk.Button(self.root, text="Load Tasks", command=self.load_tasks, bg="#4CAF50", fg="white")
        self.load_button.pack(pady=5)

        self.root.withdraw()  # Hide the control window initially

    def save_tasks(self):
        self.task_manager.save_to_file()  # Call the save method from TaskManager

    def load_tasks(self):
        self.task_manager.load_from_file()  # Call the load method from TaskManager

    def draw_task_details(self, screen):
        detail_panel_rect = pygame.Rect(0, SCREEN_HEIGHT-50, SCREEN_WIDTH, 50)  # Panel on the bottom side
        pygame.draw.rect(screen, (50, 50, 50), detail_panel_rect)  # Dark gray background
        if self.selected_task:
            # Draw task details
            font = pygame.font.SysFont('Arial', 20)
            title_surface = font.render(f"Task: {self.selected_task.name}", True, (255, 255, 255))
            description_surface = font.render(f"Description: {self.selected_task.description}", True, (255, 255, 255))
            due_date_surface = font.render(f"Due Date: {self.selected_task.due_date}", True, (255, 255, 255))

            screen.blit(title_surface, (0, SCREEN_HEIGHT-40))
            screen.blit(description_surface, (400, SCREEN_HEIGHT-40))
            screen.blit(due_date_surface, (200, SCREEN_HEIGHT-40))

        # Draw buttons in the bottom right corner
        self.save_button.place(x=SCREEN_WIDTH - 100, y=SCREEN_HEIGHT - 40)  # Adjust position as needed
        self.load_button.place(x=SCREEN_WIDTH - 100, y=SCREEN_HEIGHT - 70)  # Adjust position as needed

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.task_manager.clear_tasks()
                self.task_manager.handle_events(event)

            screen.fill((30, 30, 30))
            for task in self.task_manager.tasks:  # Draw all tasks
                task.draw(screen)  # Draw the task
                if task.rect.collidepoint(pygame.mouse.get_pos()):  # Check if the mouse is over the task
                    self.selected_task = task  # Set the selected task to the one being hovered over

            self.draw_task_details(screen)  # Draw the task details panel

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        self.root.destroy()  # Close the Tkinter window when done

if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()

