import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from tkinter.scrolledtext import ScrolledText
import json
from tkinter import colorchooser
import ttkthemes
from functools import partial, lru_cache
import threading
from queue import Queue
import time
from collections import defaultdict
import weakref

class Task:
    def __init__(self, title, description, due_date=None, status="Pending"):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status
        self.created_at = datetime.now()
        self.category = "General"
        self.priority = "Medium"
        self.progress = 0
        self.notes = ""
        self.color = None

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'category': self.category,
            'priority': self.priority,
            'progress': self.progress,
            'notes': self.notes,
            'color': self.color
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(data['title'], data['description'], data['due_date'], data['status'])
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.category = data.get('category', 'General')
        task.priority = data.get('priority', 'Medium')
        task.progress = data.get('progress', 0)
        task.notes = data.get('notes', '')
        task.color = data.get('color', None)
        return task

class TaskCache:
    def __init__(self):
        self.tasks_by_title = {}
        self.tasks_by_status = defaultdict(list)
        self.tasks_by_category = defaultdict(list)
        self._observers = weakref.WeakSet()

    def add_task(self, task):
        self.tasks_by_title[task.title] = task
        self.tasks_by_status[task.status].append(task)
        self.tasks_by_category[task.category].append(task)
        self._notify_observers()

    def remove_task(self, task):
        if task.title in self.tasks_by_title:
            del self.tasks_by_title[task.title]
            self.tasks_by_status[task.status].remove(task)
            self.tasks_by_category[task.category].remove(task)
            self._notify_observers()

    def update_task(self, task, old_status=None, old_category=None):
        if old_status and old_status != task.status:
            self.tasks_by_status[old_status].remove(task)
            self.tasks_by_status[task.status].append(task)
        if old_category and old_category != task.category:
            self.tasks_by_category[old_category].remove(task)
            self.tasks_by_category[task.category].append(task)
        self.tasks_by_title[task.title] = task
        self._notify_observers()

    def add_observer(self, callback):
        self._observers.add(callback)

    def _notify_observers(self):
        for callback in self._observers:
            callback()

class TaskManager:
    def __init__(self):
        self._tasks = []
        self._categories = ["General", "Work", "Personal", "Shopping", "Health", "Education"]
        self._cache = TaskCache()
        self._search_index = {}  # Add search index
        self.load_tasks()
        self._build_search_index()  # Build initial index

    @property
    def tasks(self):
        return self._tasks

    @property
    def categories(self):
        return self._categories

    def add_task(self, task):
        self._tasks.append(task)
        self._cache.add_task(task)
        # Update search index
        for text in [task.title, task.description, task.category, task.priority]:
            words = text.lower().split()
            for word in words:
                self._search_index[word].append(task)
        self._save_tasks_async()

    def remove_task(self, task):
        self._tasks.remove(task)
        self._cache.remove_task(task)
        self._save_tasks_async()

    def update_task(self, task, old_status=None, old_category=None):
        self._cache.update_task(task, old_status, old_category)
        self._save_tasks_async()

    def _save_tasks_async(self):
        def save_worker():
            with open('tasks.json', 'w') as f:
                json.dump([task.to_dict() for task in self._tasks], f)
            
        thread = threading.Thread(target=save_worker)
        thread.daemon = True
        thread.start()

    def _build_search_index(self):
        """Build search index for faster searching"""
        self._search_index = defaultdict(list)
        for task in self._tasks:
            # Index words from title, description, category, and priority
            for text in [task.title, task.description, task.category, task.priority]:
                words = text.lower().split()
                for word in words:
                    self._search_index[word].append(task)

    def filter_tasks(self, search_term, status_filter):
        """Optimized task filtering using index-based search"""
        if not self._tasks:
            return []

        # First filter by status as it's typically more restrictive
        if status_filter != "All":
            filtered_tasks = set(task for task in self._tasks if task.status == status_filter)
        else:
            filtered_tasks = set(self._tasks)

        if not search_term:
            return list(filtered_tasks)

        # Use the search index for text search
        search_words = search_term.lower().split()
        matching_tasks = set()
        
        for word in search_words:
            matching_tasks.update(self._search_index.get(word, []))
        
        # Intersect status-filtered tasks with search results
        return list(filtered_tasks.intersection(matching_tasks))

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                data = json.load(f)
                self._tasks = [Task.from_dict(task_data) for task_data in data]
                for task in self._tasks:
                    self._cache.add_task(task)
        except FileNotFoundError:
            self._tasks = []

class TaskManagerGUI:
    def __init__(self):
        self.task_manager = TaskManager()
        self.root = tk.Tk()
        self.root.title("Enhanced Task Manager")
        self.root.geometry("1200x800")
        
        # Performance optimizations
        self.update_queue = Queue()
        self.last_search = ""
        self.search_after_id = None
        self.last_refresh = 0
        self.refresh_delay = 1  # Reduced delay for better responsiveness
        self.batch_size = 50  # Number of items to update in one batch
        
        # Configure the root window for better performance
        self.root.update_idletasks()
        self.root.after(1, self.root.attributes, '-alpha', 0.0)
        self.root.after(1, self.setup_gui)
        self.root.after(1, lambda: self.root.attributes('-alpha', 1.0))

    def setup_gui(self):
        # Apply theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        # Configure styles
        self.configure_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self.root, style="Custom.TFrame", padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI elements
        self.create_menu()
        self.create_header()
        self.create_input_panel()
        self.create_task_list_panel()
        self.create_status_bar()
        
        # Start update thread
        self.start_update_thread()
        
        # Initialize
        self.task_manager._cache.add_observer(self.schedule_refresh)
        self.update_task_counter()
        self.schedule_refresh()

    def configure_styles(self):
        self.style.configure("Custom.TFrame", background="#f5f6f7")
        self.style.configure("TaskTree.Treeview", rowheight=30, padding=5)
        self.style.configure("Accent.TButton", padding=10)
        self.style.configure("Action.TButton", padding=10)
        self.style.configure("Status.TLabel", padding=5)

    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.LEFT)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.schedule_refresh())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        # Filters
        filter_frame = ttk.Frame(header_frame)
        filter_frame.pack(side=tk.RIGHT)
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                  values=["All", "Pending", "In Progress", "Completed"],
                                  width=15, state="readonly")
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.schedule_refresh())

    def create_input_panel(self):
        input_frame = ttk.LabelFrame(self.content_frame, text="Add New Task", padding="10")
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Task input fields
        ttk.Label(input_frame, text="Title:").pack(anchor=tk.W, pady=(5, 0))
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Description:").pack(anchor=tk.W)
        self.desc_entry = ScrolledText(input_frame, width=35, height=4)
        self.desc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Category selection
        ttk.Label(input_frame, text="Category:").pack(anchor=tk.W)
        self.category_var = tk.StringVar(value="General")
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var,
                                         values=self.task_manager.categories, state="readonly")
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Due date
        ttk.Label(input_frame, text="Due Date:").pack(anchor=tk.W)
        self.due_date_entry = DateEntry(input_frame, width=38, background='darkblue',
                                      foreground='white', borderwidth=2)
        self.due_date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Priority
        ttk.Label(input_frame, text="Priority:").pack(anchor=tk.W)
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = ttk.Frame(input_frame)
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        for priority in ["Low", "Medium", "High"]:
            ttk.Radiobutton(priority_frame, text=priority, value=priority,
                          variable=self.priority_var).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        ttk.Label(input_frame, text="Progress:").pack(anchor=tk.W)
        self.progress_var = tk.IntVar(value=0)
        progress_frame = ttk.Frame(input_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        progress_scale = ttk.Scale(progress_frame, from_=0, to=100, variable=self.progress_var,
                                orient=tk.HORIZONTAL, command=lambda x: self.progress_var.set(int(float(x))))
        progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        progress_label.pack(side=tk.LEFT, padx=5)
        
        # Color picker
        ttk.Button(input_frame, text="Choose Color", 
                  command=self.choose_color).pack(fill=tk.X, pady=(0, 10))
        
        # Add button
        ttk.Button(input_frame, text="Add Task", style="Accent.TButton",
                  command=self.add_task).pack(fill=tk.X, pady=(10, 0))

    def create_task_list_panel(self):
        list_frame = ttk.LabelFrame(self.content_frame, text="Tasks", padding="10")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create tree view with columns
        columns = ("Title", "Category", "Priority", "Progress", "Due Date", "Status")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings",
                                    style="TaskTree.Treeview", selectmode="extended")
        
        # Configure columns
        column_widths = {
            "Title": 200, "Category": 100, "Priority": 80,
            "Progress": 100, "Due Date": 100, "Status": 100
        }
        for col, width in column_widths.items():
            self.task_tree.heading(col, text=col, 
                                 command=partial(self.sort_tasks, col))
            self.task_tree.column(col, width=width)
        
        # Add scrollbars with smooth scrolling
        y_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                               command=self.task_tree.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL,
                               command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=self.smooth_scroll(y_scroll.set),
                               xscrollcommand=self.smooth_scroll(x_scroll.set))
        
        # Pack everything
        self.task_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add action buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Complete button
        complete_btn = ttk.Button(btn_frame, text=" Complete", 
                                command=self.mark_complete,
                                style="Action.TButton")
        complete_btn.pack(side=tk.LEFT, padx=5)
        
        # Edit button
        edit_btn = ttk.Button(btn_frame, text="Edit",
                            command=self.edit_task,
                            style="Action.TButton")
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = ttk.Button(btn_frame, text="Delete",
                              command=self.delete_task,
                              style="Action.TButton")
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind events with debouncing
        self.task_tree.bind('<Double-1>', lambda e: self.debounce(self.edit_task))
        self.task_tree.bind('<Delete>', lambda e: self.debounce(self.delete_task))

    def smooth_scroll(self, callback):
        """Implement smooth scrolling"""
        def smooth(*args):
            callback(*args)
            self.root.update_idletasks()
        return smooth

    def debounce(self, func, *args, delay=200):
        """Debounce function calls"""
        if hasattr(self, '_debounce_timer'):
            self.root.after_cancel(self._debounce_timer)
        self._debounce_timer = self.root.after(delay, lambda: func(*args))

    def refresh_task_list(self):
        """Highly optimized task list refresh"""
        if hasattr(self, 'search_after_id') and self.search_after_id:
            try:
                self.root.after_cancel(self.search_after_id)
            except ValueError:
                pass
        self.search_after_id = None

        def update_batch(items_to_process, start_idx=0):
            if start_idx >= len(items_to_process):
                self.task_tree.configure(selectmode='extended')
                self.update_task_counter()
                return

            end_idx = min(start_idx + self.batch_size, len(items_to_process))
            batch = items_to_process[start_idx:end_idx]

            for task in batch:
                item_values = (
                    task.title, task.category, task.priority,
                    f"{task.progress}%", task.due_date, task.status
                )
                
                if task.title in existing_items:
                    item_id = existing_items[task.title]
                    self.task_tree.item(item_id, values=item_values, tags=(task.color,) if task.color else ())
                    del existing_items[task.title]
                else:
                    item_id = self.task_tree.insert("", tk.END, values=item_values, tags=(task.color,) if task.color else ())
                
                if task.color:
                    self.task_tree.tag_configure(task.color, background=task.color)

            self.root.after(1, lambda: update_batch(items_to_process, end_idx))

        # Prepare for batch update
        self.task_tree.configure(selectmode='none')
        existing_items = {self.task_tree.item(item)['values'][0]: item 
                         for item in self.task_tree.get_children()}

        # Get filtered tasks
        filtered_tasks = self.task_manager.filter_tasks(
            self.search_var.get().lower(),
            self.filter_var.get()
        )

        # Start batch update
        update_batch(filtered_tasks)

        # Remove remaining items
        for item_id in existing_items.values():
            self.task_tree.delete(item_id)

    def add_task(self):
        if not self.validate_input():
            return
            
        task = Task(
            title=self.title_entry.get().strip(),
            description=self.desc_entry.get("1.0", tk.END).strip(),
            due_date=self.due_date_entry.get_date().strftime("%Y-%m-%d")
        )
        task.category = self.category_var.get()
        task.priority = self.priority_var.get()
        task.progress = self.progress_var.get()
        task.color = getattr(self, 'current_color', None)
        
        def add_task_worker():
            self.task_manager.add_task(task)
            self.update_queue.put(lambda: self.after_task_added())
            
        thread = threading.Thread(target=add_task_worker)
        thread.daemon = True
        thread.start()

    def after_task_added(self):
        self.clear_entries()
        self.schedule_refresh()
        self.show_status("Task added successfully!")

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Tasks", command=self.task_manager._save_tasks_async)
        file_menu.add_command(label="Export as CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
        
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        for theme in self.style.get_themes():
            theme_menu.add_command(label=theme.capitalize(), 
                                 command=lambda t=theme: self.style.set_theme(t))

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Separator(status_frame).pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.task_counter_label = ttk.Label(status_frame, style="Status.TLabel")
        self.task_counter_label.pack(side=tk.RIGHT, padx=5, pady=2)

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Task Color")[1]
        if color:
            self.current_color = color
            
    def edit_task(self):
        """Open dialog to edit selected task"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return
    
        # Get the task index from the tree item ID
        task_id = selection[0]
        task = self.task_tree.item(task_id)['values']
        if not task:
            messagebox.showerror("Error", "Could not find the selected task.")
            return

        # Find the task in the task manager by title
        task_title = task[0]  # Assuming title is the first column
        task_to_edit = next((t for t in self.task_manager.tasks if t.title == task_title), None)
        
        if not task_to_edit:
            messagebox.showerror("Error", "Task not found in task manager.")
            return
    
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("500x700")  # Made taller to accommodate buttons
        edit_window.transient(self.root)
        edit_window.grab_set()
    
        # Create main frame with padding
        main_frame = ttk.Frame(edit_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Title
        ttk.Label(main_frame, text="Title:").pack(anchor=tk.W)
        title_entry = ttk.Entry(main_frame, width=50)
        title_entry.insert(0, task_to_edit.title)
        title_entry.pack(fill=tk.X, pady=(0, 10))
    
        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor=tk.W)
        desc_text = tk.Text(main_frame, height=4, width=50)
        desc_text.insert("1.0", task_to_edit.description)
        desc_text.pack(fill=tk.X, pady=(0, 10))
    
        # Category
        ttk.Label(main_frame, text="Category:").pack(anchor=tk.W)
        category_var = tk.StringVar(value=task_to_edit.category)
        category_combo = ttk.Combobox(main_frame, textvariable=category_var)
        category_combo['values'] = list(set([t.category for t in self.task_manager.tasks] + ["General"]))
        category_combo.pack(fill=tk.X, pady=(0, 10))
    
        # Priority
        ttk.Label(main_frame, text="Priority:").pack(anchor=tk.W)
        priority_var = tk.StringVar(value=task_to_edit.priority)
        priority_frame = ttk.Frame(main_frame)
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        for priority in ["Low", "Medium", "High"]:
            ttk.Radiobutton(priority_frame, text=priority, variable=priority_var, 
                          value=priority).pack(side=tk.LEFT, padx=5)
    
        # Due Date
        ttk.Label(main_frame, text="Due Date:").pack(anchor=tk.W)
        due_date = DateEntry(main_frame, width=30, background='darkblue',
                           foreground='white', borderwidth=2)
        if task_to_edit.due_date:
            due_date.set_date(datetime.strptime(task_to_edit.due_date, "%Y-%m-%d").date())
        due_date.pack(fill=tk.X, pady=(0, 10))
    
        # Progress
        progress_var = tk.IntVar(value=int(task_to_edit.progress))
        progress_label = ttk.Label(main_frame, text=f"Progress: {progress_var.get()}%")
        progress_label.pack(anchor=tk.W)
        progress_scale = ttk.Scale(main_frame, from_=0, to=100, 
                                variable=progress_var, orient=tk.HORIZONTAL,
                                command=lambda x: progress_var.set(int(float(x))))
        progress_scale.pack(fill=tk.X, pady=(0, 10))

        # Update progress label when scale changes
        def update_progress_label(*args):
            progress_label.config(text=f"Progress: {int(progress_var.get())}%")
        progress_var.trace_add("write", update_progress_label)
        # Update progress label when scale changes
    
        # Status
        ttk.Label(main_frame, text="Status:").pack(anchor=tk.W)
        status_var = tk.StringVar(value=task_to_edit.status)
        status_combo = ttk.Combobox(main_frame, textvariable=status_var)
        status_combo['values'] = ["Not Started", "In Progress", "Completed"]
        status_combo.pack(fill=tk.X, pady=(0, 10))
    
        # Color
        color_frame = ttk.Frame(main_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        color_btn = ttk.Button(color_frame, text="Choose Color",
                             command=self.choose_color)
        if hasattr(task_to_edit, 'color') and task_to_edit.color:
            color_btn.configure(style=f'Color.TButton')
            self.current_color = task_to_edit.color
        color_btn.pack(side=tk.LEFT, padx=5)
    
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
    
        def save_changes():
            if not title_entry.get().strip():
                messagebox.showerror("Error", "Title is required!")
                return

            try:
                # Update task attributes
                task_to_edit.title = title_entry.get().strip()
                task_to_edit.description = desc_text.get("1.0", tk.END).strip()
                task_to_edit.category = category_var.get()
                task_to_edit.priority = priority_var.get()
                task_to_edit.progress = progress_var.get()
                task_to_edit.due_date = due_date.get_date().strftime("%Y-%m-%d")
                task_to_edit.status = status_var.get()
                task_to_edit.color = getattr(self, 'current_color', None)

                # Update tree item
                values = (
                    task_to_edit.title,
                    task_to_edit.category,
                    task_to_edit.priority,
                    task_to_edit.due_date,
                    f"{task_to_edit.progress}%",
                    task_to_edit.status
                )
                self.task_tree.item(task_id, values=values)
                
                # Save changes
                self.task_manager._save_tasks_async()
                self.update_task_counter()
                self.show_status("Task updated successfully!")
                edit_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update task: {str(e)}")

    
        def cancel():
            edit_window.destroy()
    
        # Save button
        save_btn = ttk.Button(button_frame, text="Save", command=save_changes)
        save_btn.pack(side=tk.LEFT, padx=5)
    
        # Cancel button
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')



    def delete_task(self):
        """Delete the selected task after confirmation"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return

        task_id = selection[0]
        task = self.task_tree.item(task_id)['values']
        if not task:
            messagebox.showerror("Error", "Could not find the selected task.")
            return

        # Find the task in the task manager by title
        task_title = task[0]  # Assuming title is the first column
        task_to_delete = next((t for t in self.task_manager.tasks if t.title == task_title), None)
        
        if not task_to_delete:
            messagebox.showerror("Error", "Task not found in task manager.")
            return
    
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            try:
                # Remove from task manager
                self.task_manager.remove_task(task_to_delete)
                # Remove from tree
                self.task_tree.delete(task_id)
                # Update task counter and save
                self.update_task_counter()
                self.task_manager._save_tasks_async()
                self.show_status("Task deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task: {str(e)}")

    def mark_complete(self):
        """Mark the selected task as complete"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to mark as complete.")
            return

        # Get the task index from the tree item ID
        task_id = selection[0]
        task = self.task_tree.item(task_id)['values']
        if not task:
            messagebox.showerror("Error", "Could not find the selected task.")
            return

        # Find the task in the task manager by title
        task_title = task[0]  # Assuming title is the first column
        task_to_mark = next((t for t in self.task_manager.tasks if t.title == task_title), None)
        
        if not task_to_mark:
            messagebox.showerror("Error", "Task not found in task manager.")
            return
    
        try:
            # Update task status and progress
            task_to_mark.status = "Completed"
            task_to_mark.progress = 100
            
            # Update the tree item
            values = list(self.task_tree.item(task_id)['values'])
            values[-3] = "100%"  # Update progress
            values[-1] = "Completed"  # Update status
            self.task_tree.item(task_id, values=values)
            
            # Save changes and update UI
            self.task_manager._save_tasks_async()
            self.update_task_counter()
            self.show_status("Task marked as complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark task as complete: {str(e)}")

    def start_update_thread(self):
        def update_worker():
            while True:
                try:
                    callback = self.update_queue.get()
                    if callback:
                        self.root.after(0, callback)
                except Exception as e:
                    print(f"Error in update thread: {e}")
                time.sleep(0.01)  # Prevent CPU overuse

        thread = threading.Thread(target=update_worker)
        thread.daemon = True
        thread.start()

    def schedule_refresh(self):
        current_time = time.time() * 1000
        if current_time - self.last_refresh < self.refresh_delay:
            if hasattr(self, 'search_after_id') and self.search_after_id:
                self.root.after_cancel(self.search_after_id)
            self.search_after_id = self.root.after(
                self.refresh_delay, self.refresh_task_list)
        else:
            self.refresh_task_list()
            self.last_refresh = current_time

    def validate_input(self):
        if not self.title_entry.get().strip():
            messagebox.showerror("Error", "Title is required!")
            return False
        return True

    def show_status(self, message):
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text=""))

    def show_statistics(self):
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Task Statistics")
        stats_window.geometry("400x300")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Add padding
        main_frame = ttk.Frame(stats_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Calculate statistics
        total_tasks = len(self.task_manager.tasks)
        completed = sum(1 for task in self.task_manager.tasks if task.status == "Completed")
        pending = sum(1 for task in self.task_manager.tasks if task.status == "Pending")
        in_progress = sum(1 for task in self.task_manager.tasks if task.status == "In Progress")
        
        # Create statistics display
        ttk.Label(main_frame, text="Task Statistics", 
                 font=('Helvetica', 14, 'bold')).pack(pady=(0, 20))
        
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Task counts
        counts_frame = ttk.LabelFrame(stats_frame, text="Task Counts", padding="10")
        counts_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(counts_frame, text=f"Total Tasks: {total_tasks}").pack(anchor=tk.W)
        ttk.Label(counts_frame, text=f"Completed: {completed}").pack(anchor=tk.W)
        ttk.Label(counts_frame, text=f"In Progress: {in_progress}").pack(anchor=tk.W)
        ttk.Label(counts_frame, text=f"Pending: {pending}").pack(anchor=tk.W)
        
        # Progress
        progress_frame = ttk.LabelFrame(stats_frame, text="Overall Progress", padding="10")
        progress_frame.pack(fill=tk.X)
        
        progress = int(completed/total_tasks*100) if total_tasks else 0
        ttk.Label(progress_frame, text=f"Completion Rate: {progress}%").pack(anchor=tk.W)
        
        progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        progress_bar['value'] = progress
        progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Close button
        ttk.Button(main_frame, text="Close", 
                  command=stats_window.destroy,
                  style="Accent.TButton").pack(pady=(20, 0))

    def export_csv(self):
        try:
            with open('tasks.csv', 'w', newline='', encoding='utf-8') as f:
                # Write header
                headers = ["Title", "Description", "Category", "Priority", 
                          "Progress", "Due Date", "Status", "Color"]
                f.write(','.join(headers) + '\n')
                
                # Write tasks
                for task in self.task_manager.tasks:
                    row = [
                        task.title.replace(',', ';'),
                        task.description.replace(',', ';').replace('\n', ' '),
                        task.category,
                        task.priority,
                        str(task.progress),
                        task.due_date,
                        task.status,
                        task.color or ''
                    ]
                    f.write(','.join(row) + '\n')
                    
            self.show_status("Tasks exported successfully to tasks.csv!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")

    def sort_tasks(self, column):
        """Sort tasks by the specified column"""
        reverse = False
        if hasattr(self, '_last_sort') and self._last_sort[0] == column:
            reverse = not self._last_sort[1]
        
        self.task_manager.tasks.sort(
            key=lambda x: (getattr(x, column.lower(), '') or '').lower(),
            reverse=reverse
        )
        
        self._last_sort = (column, reverse)
        self.schedule_refresh()

    def update_task_counter(self):
        """Update the task counter in the status bar"""
        total = len(self.task_manager.tasks)
        completed = sum(1 for task in self.task_manager.tasks if task.status == "Completed")
        in_progress = sum(1 for task in self.task_manager.tasks if task.status == "In Progress")
        
        # Calculate overall progress
        progress = int(completed/total*100) if total else 0
        
        # Update counter label with detailed statistics
        self.task_counter_label.config(
            text=f"Total: {total} | Completed: {completed} | "
                 f"In Progress: {in_progress} | "
                 f"Progress: {progress}%"
        )

    def clear_entries(self):
        """Clear all input fields"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete("1.0", tk.END)
        self.category_var.set("General")
        self.priority_var.set("Medium")
        self.progress_var.set(0)
        self.due_date_entry.set_date(datetime.now())
        if hasattr(self, 'current_color'):
            del self.current_color

    def run(self):
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskManagerGUI()
    app.run()
