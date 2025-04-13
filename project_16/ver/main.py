import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from PIL import Image, ImageTk
import ttkthemes
import threading
import time

# Create a class for the Recipe Manager application
class RecipeManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Culinary Studio 2025")
        self.geometry("1200x700")
        
        # Use a modern theme
        self.style = ttkthemes.ThemedStyle(self)
        self.style.set_theme("arc")  # Modern looking theme
        
        # Configure colors - Enhanced dark mode color scheme
        self.primary_color = "#e8e7e3"       # Vibrant purple
        self.secondary_color = "#4f46e5"     # Deep indigo
        self.bg_color = "#0f172a"            # Dark blue-gray background
        self.text_color = "#f8fafc"          # Crisp white text
        self.accent_color = "#f472b6"        # Soft pink accent
        self.card_bg = "#1e293b"             # Slate card background
        self.highlight_color = "#38bdf8"     # Sky blue highlights
        self.category_header_bg = "#334155"  # Medium slate header
        self.success_color = "#10b981"       # Emerald green
        self.card_border = "#475569"         # Medium slate border
        self.muted_text = "#94a3b8"          # Muted light text
        self.hover_bg = "#334155"            # Slightly lighter on hover
        self.card_shadow = "#0f172a"         # Shadow color
        
        self.configure(bg=self.bg_color)
        
        # Configure styles for widgets with enhanced modern look
        self.style.configure("TFrame", background=self.bg_color)
        
        # Button styling with rounded corners effect
        self.style.configure("TButton", 
                             font=("Segoe UI Semibold", 10),
                             borderwidth=0,
                             padding=10)
        
        # Success button
        self.style.configure("Success.TButton",
                             font=("Segoe UI Semibold", 10),
                             padding=10)
        
        # Accent button  
        self.style.configure("Accent.TButton",
                             font=("Segoe UI Semibold", 10),
                             padding=10)
                             
        # Explicitly set the colors
        self.style.map("TButton", 
                       background=[("active", self.secondary_color), ("!active", self.primary_color)],
                       foreground=[("active", "white"), ("!active", "white")])
        
        self.style.map("Success.TButton",
                       background=[("active", "#059669"), ("!active", self.success_color)],
                       foreground=[("active", "white"), ("!active", "white")])
        
        self.style.map("Accent.TButton",
                       background=[("active", "#d61f69"), ("!active", self.accent_color)],
                       foreground=[("active", "white"), ("!active", "white")])
        
        # Label styling with modern fonts
        self.style.configure("Title.TLabel", 
                             font=("Montserrat", 18, "bold"), 
                             background=self.bg_color, 
                             foreground=self.primary_color)
        self.style.configure("TLabel", 
                             background=self.bg_color, 
                             foreground=self.text_color,
                             font=("Segoe UI", 10))
        self.style.configure("Category.TLabel",
                             font=("Montserrat", 11, "bold"),
                             foreground=self.secondary_color,
                             background=self.bg_color)
        self.style.configure("Subtitle.TLabel",
                             font=("Montserrat", 14, "bold"),
                             foreground=self.text_color,
                             background=self.bg_color)
        self.style.configure("Muted.TLabel",
                             font=("Segoe UI", 10),
                             foreground=self.muted_text,
                             background=self.bg_color)
        
        # Card styling with modern shadows effect
        self.style.configure("Card.TFrame", 
                             background=self.card_bg,
                             relief="ridge",
                             borderwidth=1,
                             bordercolor=self.card_border)
        self.style.configure("Header.TFrame",
                             background=self.category_header_bg,
                             relief="flat",
                             borderwidth=0)
        
        # Entry styling                     
        self.style.configure("Search.TEntry",
                             font=("Segoe UI", 11),
                             fieldbackground=self.card_bg,
                             foreground=self.text_color,
                             bordercolor=self.highlight_color)
        
        # Loading spinner styling
        self.style.configure("Loading.TLabel",
                             font=("Segoe UI", 12, "bold"),
                             foreground=self.highlight_color,
                             background=self.bg_color)
                             
        # Create a loading indicator
        self.loading_var = tk.StringVar()
        self.loading_indicator = ttk.Label(self, textvariable=self.loading_var, style="Loading.TLabel")
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_indicator.place_forget()  # Hide initially
        
        # Thread lock for recipe data
        self.data_lock = threading.Lock()
        
        # Start loading data in background thread
        self.loading_var.set("Loading recipes...")
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor="center")
        self.after(100, self.start_loading_data)
    
    def start_loading_data(self):
        """Start loading data in a background thread"""
        threading.Thread(target=self.load_data_thread, daemon=True).start()
    
    def load_data_thread(self):
        """Load data in a background thread"""
        data = self.load_data()
        
        # Update recipe_data and UI in the main thread
        self.after(0, lambda: self.finish_loading_data(data))
    
    def finish_loading_data(self, data):
        """Update UI with loaded data"""
        with self.data_lock:
            self.recipe_data = data
        
        # Hide loading indicator
        self.loading_indicator.place_forget()
        
        # Initialize the UI
        self.create_ui()
        
        # Keep track of the selected category and recipe
        self.selected_category = None
        self.selected_recipe = None
    
    def load_data(self):
        """Load data from JSON file if it exists, otherwise return empty data structure"""
        # Simulate longer loading to demonstrate threading
        time.sleep(0.5)  # Only for demonstration
        
        if os.path.exists("recipes.json"):
            try:
                with open("recipes.json", "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save data to JSON file"""
        # Show loading indicator
        self.loading_var.set("Saving...")
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start saving in background thread
        threading.Thread(target=self.save_data_thread, daemon=True).start()
    
    def save_data_thread(self):
        """Save data in a background thread"""
        # Make a copy of the data for thread safety
        with self.data_lock:
            data_copy = self.recipe_data.copy()
        
        # Save the data
        with open("recipes.json", "w") as f:
            json.dump(data_copy, f, indent=4)
            
        # Hide loading indicator in main thread
        self.after(0, lambda: self.loading_indicator.place_forget())
        
        # Show success message briefly
        self.after(0, lambda: self.show_toast_message("Changes saved successfully"))
    
    def show_toast_message(self, message, duration=1500):
        """Show a toast message that automatically disappears"""
        try:
            toast = tk.Label(self, text=message, 
                            font=("Segoe UI", 11),
                            fg="white", 
                            bg=self.success_color,
                            padx=15, pady=8)
            toast.place(relx=0.5, rely=0.9, anchor="center")
            
            # Make it rounded
            toast.update_idletasks()
            
            # Schedule removal instead of direct animation which can cause issues
            self.after(duration, lambda: self.fade_out_toast(toast))
        except Exception as e:
            print(f"Error showing toast: {e}")
    
    def fade_out_toast(self, toast):
        """Fade out the toast message"""
        try:
            # Simply destroy the toast without animation to avoid alpha issues
            toast.destroy()
        except Exception as e:
            print(f"Error fading toast: {e}")
    
    def create_ui(self):
        """Create the main UI with three columns"""
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure columns
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.columnconfigure(2, weight=3)
        main_container.rowconfigure(0, weight=1)
        
        # Main menu bar
        menu_bar = tk.Menu(self, bg=self.card_bg, fg=self.text_color, 
                          activebackground=self.primary_color, 
                          activeforeground="white", relief="flat", borderwidth=1)
        self.config(menu=menu_bar)
        
        # File menu with enhanced styling
        file_menu = tk.Menu(menu_bar, tearoff=0, bg=self.card_bg, fg=self.text_color,
                           activebackground=self.primary_color, 
                           activeforeground="white", relief="flat", borderwidth=1)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Generate Test Data", command=self.generate_test_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # First column - Categories
        self.create_category_section(main_container)
        
        # Second column - Recipe List
        self.create_recipe_list_section(main_container)
        
        # Third column - Recipe Details
        self.create_recipe_details_section(main_container)
        
        # Initialize search_results_frame (to prevent AttributeError)
        self.search_results_frame = ttk.Frame(self)
        self.search_results_container = ttk.Frame(self.search_results_frame)
        self.search_results_container.pack(fill=tk.BOTH, expand=True)
    
    def create_category_section(self, parent):
        """Create the first column with categories"""
        category_frame = ttk.Frame(parent)
        category_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=10)
        
        # Header frame with rounded corners effect
        header_frame = ttk.Frame(category_frame, style="Header.TFrame")
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        
        # Title label with enhanced styling
        title_label = ttk.Label(header_frame, text="Collections", style="Title.TLabel")
        title_label.pack(side=tk.TOP, pady=15, padx=15, anchor="w")
        
        # Search frame with elevated appearance
        search_frame = ttk.Frame(category_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=8)
        
        # Search input with modern styling
        self.category_search_var = tk.StringVar()
        self.category_search_var.trace("w", self.filter_categories)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.category_search_var, style="Search.TEntry")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        search_entry.insert(0, "Search collections...")
        search_entry.bind("<FocusIn>", lambda e: self.on_search_focus_in(e, "Search collections..."))
        search_entry.bind("<FocusOut>", lambda e: self.on_search_focus_out(e, "Search collections..."))
        
        # Buttons frame with modern spacing
        btn_frame = ttk.Frame(category_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=15)
        
        # Custom styling for these specific buttons with pill shape
        add_btn = tk.Button(btn_frame, text="+ New Collection", 
                          command=self.add_category,
                          bg=self.success_color,
                          fg="white",
                          font=("Montserrat", 10, "bold"),
                          relief=tk.FLAT,
                          padx=12, pady=6,
                          activebackground="#059669",
                          activeforeground="white",
                          cursor="hand2",
                          borderwidth=0)
        add_btn.pack(side=tk.LEFT, padx=2)
        
        # Make buttons round
        self.make_rounded(add_btn)
        
        edit_btn = tk.Button(btn_frame, text="Edit", 
                           command=self.edit_category,
                           bg=self.primary_color,
                           fg="white",
                           font=("Montserrat", 10, "bold"),
                           relief=tk.FLAT,
                           padx=12, pady=6,
                           activebackground=self.secondary_color,
                           activeforeground="white",
                           cursor="hand2",
                           borderwidth=0)
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Make buttons round
        delete_btn = tk.Button(btn_frame, text="Delete", 
                           command=self.delete_category,
                           bg=self.accent_color,
                           fg="white",
                           font=("Montserrat", 10, "bold"),
                           relief=tk.FLAT,
                           padx=12, pady=6,
                           activebackground="#d61f69",
                           activeforeground="white",
                           cursor="hand2",
                           borderwidth=0)
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Make buttons round
        self.make_rounded(delete_btn)
        
        # Category listbox with modern styling
        category_container = ttk.Frame(category_frame, style="Card.TFrame")
        category_container.pack(fill=tk.BOTH, expand=True, pady=10, padx=2)
        
        self.category_listbox = tk.Listbox(category_container, 
                                          bg=self.card_bg, 
                                          fg=self.text_color, 
                                          selectbackground=self.primary_color,
                                          selectforeground="white",
                                          font=("Segoe UI", 12),
                                          relief=tk.FLAT,
                                          highlightthickness=0,
                                          bd=0,
                                          activestyle="none",
                                          borderwidth=0)
        self.category_listbox.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)
        
        # Populate categories
        self.populate_categories()
    
    def make_rounded(self, widget):
        """Apply rounded corners to a widget"""
        # This simulates rounded corners by setting specific options
        widget.config(borderwidth=0, highlightthickness=0)
        radius = 20  # Define radius for rounded corners
        
        # Apply a modern shape style to the button
        widget.config(pady=8, padx=12)
    
    def create_recipe_list_section(self, parent):
        """Create the second column with recipe list"""
        recipe_list_frame = ttk.Frame(parent)
        recipe_list_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        
        # Header frame
        header_frame = ttk.Frame(recipe_list_frame, style="Header.TFrame")
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Title label
        self.recipe_list_title = ttk.Label(header_frame, text="Recipes", style="Title.TLabel")
        self.recipe_list_title.pack(side=tk.TOP, pady=12, padx=10, anchor="w")
        
        # Search frame
        search_frame = ttk.Frame(recipe_list_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Search input
        self.recipe_search_var = tk.StringVar()
        self.recipe_search_var.trace("w", self.filter_recipes)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.recipe_search_var, style="Search.TEntry")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        search_entry.insert(0, "Search recipes...")
        search_entry.bind("<FocusIn>", lambda e: self.on_search_focus_in(e, "Search recipes..."))
        search_entry.bind("<FocusOut>", lambda e: self.on_search_focus_out(e, "Search recipes..."))
        
        # Buttons frame
        btn_frame = ttk.Frame(recipe_list_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        # Add button - using tk.Button instead of ttk.Button for better color control
        add_btn = tk.Button(btn_frame, text="Add Recipe", 
                          command=self.add_recipe,
                          bg=self.success_color,
                          fg="white",
                          font=("Segoe UI Semibold", 10),
                          relief=tk.FLAT,
                          padx=6, pady=4,
                          activebackground="#2f855a",
                          activeforeground="white",
                          cursor="hand2")
        add_btn.pack(side=tk.LEFT, padx=2)
        
        # Edit button
        edit_btn = tk.Button(btn_frame, text="Edit", 
                           command=self.edit_recipe,
                           bg=self.primary_color,
                           fg="white",
                           font=("Segoe UI Semibold", 10),
                           relief=tk.FLAT,
                           padx=6, pady=4,
                           activebackground=self.secondary_color,
                           activeforeground="white",
                           cursor="hand2")
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        delete_btn = tk.Button(btn_frame, text="Delete", 
                             command=self.delete_recipe,
                             bg=self.accent_color,
                             fg="white",
                             font=("Segoe UI Semibold", 10),
                             relief=tk.FLAT,
                             padx=6, pady=4,
                             activebackground="#c53030",
                             activeforeground="white",
                             cursor="hand2")
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Recipe cards container (scrollable canvas)
        self.canvas_frame = ttk.Frame(recipe_list_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.card_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_recipe_details_section(self, parent):
        """Create the third column with recipe details"""
        recipe_details_frame = ttk.Frame(parent)
        recipe_details_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=5)
        
        # Header frame
        header_frame = ttk.Frame(recipe_details_frame, style="Header.TFrame")
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Title label
        self.recipe_details_title = ttk.Label(header_frame, text="Recipe Details", style="Title.TLabel")
        self.recipe_details_title.pack(side=tk.TOP, pady=12, padx=10, anchor="w")
        
        # Search frame for content search
        search_frame = ttk.Frame(recipe_details_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Search input
        self.content_search_var = tk.StringVar()
        self.content_search_var.trace("w", self.search_all_recipes)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.content_search_var, style="Search.TEntry")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        search_entry.insert(0, "Search in all recipes...")
        search_entry.bind("<FocusIn>", lambda e: self.on_search_focus_in(e, "Search in all recipes..."))
        search_entry.bind("<FocusOut>", lambda e: self.on_search_focus_out(e, "Search in all recipes..."))
        
        # Content container - This will hold either details or search results
        self.content_container = ttk.Frame(recipe_details_frame)
        self.content_container.pack(fill=tk.BOTH, expand=True)
        
        # Recipe details container
        self.details_frame = ttk.Frame(self.content_container)
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recipe title
        self.recipe_title_label = ttk.Label(self.details_frame, text="Select a recipe to view details", 
                                         style="Subtitle.TLabel",
                                         font=("Segoe UI", 16, "bold"))
        self.recipe_title_label.pack(pady=20)
        
        # Recipe description
        self.recipe_description_text = tk.Text(self.details_frame, wrap=tk.WORD, height=15, 
                                             font=("Segoe UI", 11), bg=self.card_bg, fg=self.text_color, bd=0,
                                             relief=tk.FLAT, padx=15, pady=15,
                                             highlightthickness=1,
                                             highlightcolor=self.highlight_color)
        self.recipe_description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 15))
        self.recipe_description_text.insert(tk.END, "Select a recipe to view details")
        self.recipe_description_text.config(state=tk.DISABLED)
        
        # Search results container (initially not visible)
        self.search_results_frame = ttk.Frame(self.content_container)
        self.search_results_container = ttk.Frame(self.search_results_frame)
        self.search_results_container.pack(fill=tk.BOTH, expand=True)
    
    def on_search_focus_in(self, event, placeholder):
        """Handle focus in event for search entries"""
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
    
    def on_search_focus_out(self, event, placeholder):
        """Handle focus out event for search entries"""
        if not event.widget.get():
            event.widget.insert(0, placeholder)
    
    def filter_categories(self, *args):
        """Filter categories based on search text"""
        search_text = self.category_search_var.get().lower()
        if search_text == "search collections...":
            search_text = ""
            
        # Start filtering in a background thread
        threading.Thread(target=self.filter_categories_thread, 
                      args=(search_text,), 
                      daemon=True).start()
    
    def filter_categories_thread(self, search_text):
        """Filter categories in a background thread"""
        with self.data_lock:
            # Get filtered categories
            filtered_categories = []
            for category in self.recipe_data.keys():
                if search_text == "" or search_text in category.lower():
                    filtered_categories.append(category)
        
        # Update UI in main thread
        self.after(0, lambda: self.update_category_listbox(filtered_categories))
    
    def update_category_listbox(self, filtered_categories):
        """Update the category listbox with filtered results"""
        self.category_listbox.delete(0, tk.END)
        for category in filtered_categories:
            self.category_listbox.insert(tk.END, category)
    
    def filter_recipes(self, *args):
        """Filter recipes based on search text"""
        if not self.selected_category:
            return
            
        search_text = self.recipe_search_var.get().lower()
        if search_text == "search recipes...":
            search_text = ""
        
        # Start filtering in a background thread    
        threading.Thread(target=self.filter_recipes_thread, 
                      args=(search_text,), 
                      daemon=True).start()
    
    def filter_recipes_thread(self, search_text):
        """Filter recipes in a background thread"""
        with self.data_lock:
            # Get filtered recipes
            filtered_recipes = []
            if self.selected_category in self.recipe_data:
                for recipe_name, recipe_info in self.recipe_data[self.selected_category].items():
                    if search_text == "" or search_text in recipe_name.lower():
                        filtered_recipes.append((recipe_name, recipe_info))
        
        # Update UI in main thread
        self.after(0, lambda: self.update_recipe_grid(filtered_recipes))
    
    def update_recipe_grid(self, filtered_recipes):
        """Update the recipe grid with filtered results"""
        # Clear previous grid
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Update title
        self.recipe_list_title.config(text=f"Recipes in {self.selected_category}")
        
        # Create 3-column grid layout
        for i, (recipe_name, recipe_info) in enumerate(filtered_recipes):
            row = i // 3  # Integer division for row number
            col = i % 3   # Remainder for column (0, 1, or 2)
            
            card = self.create_recipe_card(recipe_name, recipe_info)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Add animation effect for each card
            self.animate_card_entry(card, i)
            
            # Configure grid weights to make columns equal width
            self.scrollable_frame.columnconfigure(0, weight=1)
            self.scrollable_frame.columnconfigure(1, weight=1)
            self.scrollable_frame.columnconfigure(2, weight=1)
    
    def animate_card_entry(self, card, index):
        """Animate the entry of a card with slight delay based on index"""
        # Use place_forget() instead of lower() which doesn't work with ttk frames
        card_info = {'card': card, 'original_bg': card.cget('background')}
        
        # Hide the card initially
        card.grid_remove()
        
        # Show it with a slight delay based on index
        delay = 50 + (index * 30)  # Staggered delay
        self.after(delay, lambda: self.show_card_with_animation(card_info))
    
    def show_card_with_animation(self, card_info):
        """Show a card with a fade-in animation"""
        card = card_info['card']
        original_bg = card_info['original_bg']
        
        # Make the card visible again
        card.grid()
        
        # Add a brief highlighting effect - use configure to set a style instead
        try:
            card.configure(style="Highlight.Card.TFrame")
            self.style.configure("Highlight.Card.TFrame", 
                             background=self.highlight_color,
                             relief="raised")
            
            # Reset to normal style after brief highlight
            self.after(150, lambda: card.configure(style="Card.TFrame"))
        except tk.TclError:
            # Fall back if styling fails
            pass

    def search_all_recipes(self, *args):
        """Search across all recipes with modern card design"""
        search_text = self.content_search_var.get().lower()
        
        if search_text == "search in all recipes..." or not search_text:
            # Hide search results and show details frame
            self.search_results_frame.pack_forget()
            self.details_frame.pack(fill=tk.BOTH, expand=True)
            return
            
        # Show search results frame and hide details frame
        self.details_frame.pack_forget()
        self.search_results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show loading indicator in search results
        loading_label = ttk.Label(self.search_results_container, 
                               text=f"Searching for '{search_text}'...", 
                               style="Loading.TLabel")
        for widget in self.search_results_container.winfo_children():
            widget.destroy()
        loading_label.pack(pady=50)
        self.update_idletasks()
        
        # Start search in background thread
        threading.Thread(target=self.search_all_recipes_thread, 
                      args=(search_text,), 
                      daemon=True).start()
    
    def search_all_recipes_thread(self, search_text):
        """Search for recipes in a background thread"""
        with self.data_lock:
            # Find matches in all recipes
            result_items = []
            
            # First collect all matching recipes
            for category, recipes in self.recipe_data.items():
                for recipe_name, recipe_info in recipes.items():
                    # Check in recipe name
                    name_match = search_text in recipe_name.lower()
                    
                    # Check in recipe description
                    description = recipe_info.get("description", "").lower()
                    desc_match = search_text in description
                    
                    # Check in ingredients
                    ingredients_match = False
                    if "ingredients" in recipe_info:
                        for ingredient in recipe_info["ingredients"]:
                            if search_text in ingredient.lower():
                                ingredients_match = True
                                break
                    
                    # Check in instructions
                    instructions_match = False
                    if "instructions" in recipe_info:
                        for instruction in recipe_info["instructions"]:
                            if search_text in instruction.lower():
                                instructions_match = True
                                break
                    
                    if name_match or desc_match or ingredients_match or instructions_match:
                        match_info = []
                        if name_match:
                            match_info.append("name")
                        if desc_match:
                            match_info.append("description")
                        if ingredients_match:
                            match_info.append("ingredients")
                        if instructions_match:
                            match_info.append("instructions")
                        
                        # Add to results
                        result_items.append({
                            "category": category,
                            "recipe_name": recipe_name,
                            "recipe_info": recipe_info,
                            "match_info": match_info,
                            "description": description,
                            "desc_match": desc_match
                        })
        
        # Update UI in main thread
        self.after(0, lambda: self.display_search_results(search_text, result_items))
    
    def display_search_results(self, search_text, result_items):
        """Display search results in the UI"""
        # Clear previous results
        for widget in self.search_results_container.winfo_children():
            widget.destroy()
        
        # Add title for search results with modern design
        results_title = ttk.Label(self.search_results_container, 
                                text=f"Search results for: '{search_text}'", 
                                style="Title.TLabel")
        results_title.pack(pady=(5, 15), anchor="w")
        
        # Create a frame to hold all results
        results_frame = ttk.Frame(self.search_results_container)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable container
        results_canvas = tk.Canvas(results_frame, bg=self.bg_color, highlightthickness=0)
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_canvas.yview)
        
        # Place scrollbar on right side
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the canvas
        results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_canvas.configure(yscrollcommand=results_scrollbar.set)
        
        # Create a frame inside the canvas to hold the search results
        results_scrollable = ttk.Frame(results_canvas, style="TFrame")
        
        # Configure the canvas to resize with the window
        def on_canvas_configure(event):
            # Update the scrollregion to encompass the inner frame
            results_canvas.configure(scrollregion=results_canvas.bbox("all"))
            # Resize the inner frame to fit the canvas width
            results_canvas.itemconfig("results_window", width=event.width)
            
        results_canvas.bind("<Configure>", on_canvas_configure)
        
        # Make the results frame expandable
        results_scrollable.bind("<Configure>", 
                             lambda e: results_canvas.configure(scrollregion=results_canvas.bbox("all")))
        
        # Create a window in the canvas to hold the results frame
        canvas_window = results_canvas.create_window((0, 0), window=results_scrollable, 
                                                 anchor="nw", tags="results_window")
        
        if result_items:
            # Display results with staggered animations
            for i, item in enumerate(result_items):
                # Create result card
                result_card = ttk.Frame(results_scrollable, style="Card.TFrame")
                result_card.pack(fill=tk.X, padx=10, pady=8, ipadx=8, ipady=8)
                
                # Initially hide the card for animation
                result_card.lower()
                
                # Card header with brand color
                header_frame = ttk.Frame(result_card, style="Card.TFrame")
                header_frame.pack(fill=tk.X, padx=12, pady=6)
                
                recipe_title = ttk.Label(header_frame, text=item["recipe_name"], 
                                      font=("Montserrat", 14, "bold"), 
                                      foreground=self.primary_color,
                                      background=self.card_bg)
                recipe_title.pack(side=tk.LEFT)
                
                category_label = ttk.Label(header_frame, text=f"in {item['category']}", 
                                        font=("Segoe UI", 10, "italic"), 
                                        foreground=self.secondary_color,
                                        background=self.card_bg)
                category_label.pack(side=tk.RIGHT)
                
                # Match information with label styling
                match_frame = ttk.Frame(result_card, style="Card.TFrame")
                match_frame.pack(fill=tk.X, padx=12, pady=2)
                
                match_label = ttk.Label(match_frame, 
                                     text=f"Matches in: {', '.join(item['match_info'])}", 
                                     font=("Segoe UI", 10, "italic"),
                                     foreground=self.muted_text,
                                     background=self.card_bg)
                match_label.pack(fill=tk.X)
                
                # Preview of matching content if there's a description match
                if item["desc_match"]:
                    # Find the position of the match
                    match_pos = item["description"].find(search_text)
                    
                    # Extract a snippet around the match
                    start = max(0, match_pos - 50)
                    end = min(len(item["description"]), match_pos + len(search_text) + 50)
                    
                    # Create the snippet
                    if start > 0:
                        snippet = "..." + item["description"][start:end] + "..."
                    else:
                        snippet = item["description"][start:end] + "..."
                    
                    preview_frame = ttk.Frame(result_card, style="Card.TFrame")
                    preview_frame.pack(fill=tk.X, padx=12, pady=5)
                    
                    preview = ttk.Label(preview_frame, text=snippet, wraplength=450, 
                                     font=("Segoe UI", 10),
                                     foreground=self.text_color,
                                     background=self.card_bg)
                    preview.pack(fill=tk.X)
                
                # Actions frame with modern button
                actions_frame = ttk.Frame(result_card, style="Card.TFrame")
                actions_frame.pack(fill=tk.X, padx=12, pady=8)
                
                # View button with pill shape
                view_btn = tk.Button(actions_frame, text="View Recipe →", 
                                  command=lambda c=item["category"], r=item["recipe_name"]: 
                                      self.show_search_result(c, r),
                                  bg=self.primary_color,
                                  fg="white",
                                  font=("Montserrat", 9, "bold"),
                                  relief=tk.FLAT,
                                  padx=12, pady=6,
                                  activebackground=self.secondary_color,
                                  activeforeground="white",
                                  cursor="hand2",
                                  borderwidth=0)
                view_btn.pack(side=tk.RIGHT)
                
                # Make button rounded
                self.make_rounded(view_btn)
                
                # Add right-click context menu
                self.add_context_menu(result_card, item["recipe_name"], item["category"])
                self.add_context_menu(recipe_title, item["recipe_name"], item["category"])
                self.add_context_menu(category_label, item["recipe_name"], item["category"])
                
                # Make the entire card clickable for view action
                result_card.bind("<Button-1>", lambda e, c=item["category"], r=item["recipe_name"]: 
                              self.show_search_result(c, r))
                recipe_title.bind("<Button-1>", lambda e, c=item["category"], r=item["recipe_name"]: 
                               self.show_search_result(c, r))
                category_label.bind("<Button-1>", lambda e, c=item["category"], r=item["recipe_name"]: 
                                 self.show_search_result(c, r))
                
                # Add hover effect
                result_card.bind("<Enter>", lambda e, card=result_card: card.configure(relief="raised"))
                result_card.bind("<Leave>", lambda e, card=result_card: card.configure(relief="flat"))
                
                # Schedule animation with staggered delay
                delay = 50 + (i * 30)  # Staggered delay
                self.after(delay, lambda card=result_card: self.animate_search_result(card))
        else:
            # No results message with modern styling
            no_results_frame = ttk.Frame(results_scrollable, style="Card.TFrame")
            no_results_frame.pack(fill=tk.X, padx=20, pady=30, ipadx=20, ipady=30)
            
            no_results = ttk.Label(no_results_frame, text="No matching recipes found", 
                                font=("Montserrat", 14),
                                foreground=self.muted_text,
                                background=self.card_bg)
            no_results.pack(pady=20)
            
            suggestion = ttk.Label(no_results_frame, 
                                text="Try different keywords or browse collections", 
                                font=("Segoe UI", 11),
                                foreground=self.muted_text,
                                background=self.card_bg)
            suggestion.pack()
    
    def animate_search_result(self, card):
        """Animate a search result card entry"""
        try:
            # Make the card visible instead of trying to pack it again
            card.update_idletasks()
            
            # Add a brief highlighting effect with try-except
            try:
                # Store background
                current_relief = card.cget("relief")
                
                # Briefly change appearance
                card.configure(relief="raised")
                
                # Reset to normal style after a brief highlight
                self.after(150, lambda: card.configure(relief=current_relief))
            except tk.TclError:
                # Fall back if styling fails
                pass
        except Exception as e:
            print(f"Error in animation: {e}")

    def generate_test_data(self):
        """Generate random testing data to populate the recipe manager"""
        # Show loading indicator
        self.loading_var.set("Generating test data...")
        self.loading_indicator.place(relx=0.5, rely=0.5, anchor="center")
        
        # Start generation in background thread
        threading.Thread(target=self.generate_test_data_thread, daemon=True).start()
    
    def generate_test_data_thread(self):
        """Generate test data in a background thread"""
        try:
            import random
            
            # Sample categories
            categories = [
                "Breakfast",
                "Lunch",
                "Dinner",
                "Desserts",
                "Salads",
                "Soups",
                "Quick Meals",
                "Vegetarian",
                "Italian",
                "Mexican"
            ]
            
            # Create sample data
            test_data = {}
            
            # Generate 5-7 categories
            selected_categories = random.sample(categories, random.randint(5, 7))
            
            for category in selected_categories:
                test_data[category] = {}
                
                # Generate 3-8 recipes per category
                for _ in range(random.randint(3, 8)):
                    # Select random template and create deep copies of lists
                    template = random.choice([
                        {
                            "name_prefix": "Homemade",
                            "name_suffix": ["Pasta", "Pizza", "Soup", "Salad", "Casserole", "Stew", "Tacos", "Sandwich", "Curry"],
                            "description": "A delicious homemade recipe that's perfect for any occasion. This dish combines fresh ingredients with amazing flavors.",
                            "ingredients": [
                                "2 tablespoons olive oil",
                                "1 onion, diced",
                                "2 cloves garlic, minced",
                                "1 bell pepper, sliced",
                                "2 cups vegetables, chopped",
                                "1 can tomatoes",
                                "Salt and pepper to taste",
                                "Fresh herbs for garnish"
                            ],
                            "instructions": [
                                "Prepare all ingredients by washing and chopping as needed.",
                                "Heat oil in a large pan over medium heat.",
                                "Add onions and garlic, sauté until fragrant.",
                                "Add remaining vegetables and cook for 5-7 minutes.",
                                "Pour in tomatoes and simmer for 15 minutes.",
                                "Season with salt, pepper, and herbs.",
                                "Serve hot and enjoy!"
                            ]
                        },
                        {
                            "name_prefix": "Quick",
                            "name_suffix": ["Breakfast", "Lunch", "Dinner", "Snack", "Appetizer", "Dessert"],
                            "description": "A quick and easy recipe that takes minimal time to prepare. Perfect for busy weeknights!",
                            "ingredients": [
                                "1 package pre-made dough",
                                "1/2 cup sauce",
                                "1 cup cheese, shredded",
                                "Your favorite toppings",
                                "1 tablespoon herbs"
                            ],
                            "instructions": [
                                "Preheat oven to 400°F (200°C).",
                                "Roll out the dough on a floured surface.",
                                "Spread sauce evenly over the dough.",
                                "Sprinkle cheese and add toppings.",
                                "Bake for 10-15 minutes until golden.",
                                "Allow to cool slightly before serving."
                            ]
                        },
                        {
                            "name_prefix": "Traditional",
                            "name_suffix": ["Stew", "Roast", "Pie", "Bread", "Cake", "Cookie", "Pudding"],
                            "description": "A traditional family recipe passed down through generations. Rich in flavor and tradition.",
                            "ingredients": [
                                "2 pounds meat, cubed",
                                "3 carrots, peeled and chopped",
                                "2 potatoes, diced",
                                "1 onion, finely diced",
                                "2 stalks celery, chopped",
                                "4 cups broth",
                                "2 bay leaves",
                                "Salt and pepper"
                            ],
                            "instructions": [
                                "Season meat with salt and pepper.",
                                "Brown meat in a large pot over medium-high heat.",
                                "Add vegetables and cook for 5 minutes.",
                                "Pour in broth and add bay leaves.",
                                "Bring to a boil, then reduce heat and simmer for 1.5 hours.",
                                "Check seasoning and adjust if needed.",
                                "Serve hot with crusty bread."
                            ]
                        }
                    ])
                    
                    # Generate recipe name
                    name_suffix = random.choice(template["name_suffix"])
                    recipe_name = f"{template['name_prefix']} {name_suffix}"
                    
                    # Add a number if needed to make sure names are unique
                    if recipe_name in test_data[category]:
                        recipe_name = f"{recipe_name} {random.randint(1, 99)}"
                    
                    # Create recipe data with deep copies to avoid reference issues
                    recipe_data = {
                        "description": template["description"],
                        "ingredients": list(template["ingredients"]),  # Use list() instead of .copy() for compatibility
                        "instructions": list(template["instructions"])  # Use list() instead of .copy() for compatibility
                    }
                    
                    # Add recipe to test data
                    test_data[category][recipe_name] = recipe_data
            
            # Update recipe data in main thread
            self.after(0, lambda: self.finish_test_data_generation(test_data))
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error generating test data: {e}")
            self.after(0, lambda: self.loading_indicator.place_forget())

    def finish_test_data_generation(self, test_data):
        """Finalize test data generation in main thread"""
        with self.data_lock:
            self.recipe_data = test_data
        
        # Hide loading indicator
        self.loading_indicator.place_forget()
        
        # Save the data and refresh UI
        self.save_data()
        self.populate_categories()
        
        # Show success message
        self.after(0, lambda: self.show_toast_message("Test data has been generated successfully!"))

    def populate_categories(self):
        """Populate the category listbox with data"""
        self.category_listbox.delete(0, tk.END)
        for category in self.recipe_data.keys():
            self.category_listbox.insert(tk.END, category)

    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.category_listbox.curselection()
        if selection:
            category_name = self.category_listbox.get(selection[0])
            self.selected_category = category_name
            self.selected_recipe = None
            self.populate_recipes(category_name)
            
            # Clear recipe details
            self.recipe_title_label.config(text="Select a recipe to view details", foreground=self.text_color)
            self.recipe_description_text.config(state=tk.NORMAL)
            self.recipe_description_text.delete(1.0, tk.END)
            self.recipe_description_text.config(state=tk.DISABLED)
            
            # Clear the recipe search field if it's not empty and not the placeholder
            if self.recipe_search_var.get() and self.recipe_search_var.get() != "Search recipes...":
                self.recipe_search_var.set("")

    def populate_recipes(self, category):
        """Populate the recipe cards for a selected category"""
        # Clear previous grid
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not category or category not in self.recipe_data:
            return
        
        # Update title
        self.recipe_list_title.config(text=f"Recipes in {category}")
        
        # Create 3-column grid layout
        recipes = list(self.recipe_data[category].items())
        for i, (recipe_name, recipe_info) in enumerate(recipes):
            row = i // 3  # Integer division for row number
            col = i % 3   # Remainder for column (0, 1, or 2)
            
            card = self.create_recipe_card(recipe_name, recipe_info)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configure grid weights to make columns equal width
            self.scrollable_frame.columnconfigure(0, weight=1)
            self.scrollable_frame.columnconfigure(1, weight=1)
            self.scrollable_frame.columnconfigure(2, weight=1)

    def create_recipe_card(self, recipe_name, recipe_info):
        """Create a recipe card for the recipe list with a modern design"""
        # Return the created card to be placed in a grid
        card = ttk.Frame(self.scrollable_frame, style="Card.TFrame")
        
        # Add shadow and rounded effect with padding
        card.configure(padding=12)
        
        # Highlight if this is the selected recipe
        if recipe_name == self.selected_recipe:
            try:
                card.configure(style="Selected.Card.TFrame")
                self.style.configure("Selected.Card.TFrame", 
                                  background=self.card_bg,
                                  relief="raised",
                                  borderwidth=2)
            except tk.TclError:
                # Fallback if style configuration fails
                card.configure(relief="raised", borderwidth=2)
        
        # Recipe title with enhanced icon - modern layout
        title_frame = ttk.Frame(card, style="Card.TFrame")
        title_frame.pack(fill=tk.X, pady=(5, 8), padx=5)
        
        # Use a more visually appealing emoji or symbol
        recipe_icon = ttk.Label(title_frame, text="🍳", font=("Segoe UI Emoji", 18))
        recipe_icon.pack(side=tk.LEFT, padx=(5, 8))
        
        recipe_title = ttk.Label(title_frame, text=recipe_name, 
                              font=("Montserrat", 12, "bold"), 
                              foreground=self.primary_color,
                              wraplength=120,
                              background=self.card_bg)
        recipe_title.pack(side=tk.LEFT, pady=3, expand=True)
        
        # Add right-click context menu to the card
        self.add_context_menu(card, recipe_name)
        self.add_context_menu(recipe_title, recipe_name)
        self.add_context_menu(recipe_icon, recipe_name)
        
        # Make the card clickable for view action with hover effect
        card.bind("<Button-1>", lambda e, c=self.selected_category, r=recipe_name: self.show_recipe_details(c, r))
        
        # Use try-except for hover effects which might not work on all platforms
        try:
            card.bind("<Enter>", lambda e: card.configure(relief="raised"))
            card.bind("<Leave>", lambda e: card.configure(relief="flat"))
        except tk.TclError:
            pass
        
        recipe_title.bind("<Button-1>", lambda e, c=self.selected_category, r=recipe_name: self.show_recipe_details(c, r))
        recipe_icon.bind("<Button-1>", lambda e, c=self.selected_category, r=recipe_name: self.show_recipe_details(c, r))
        
        return card

    def add_context_menu(self, widget, recipe_name, category=None):
        """Add right-click context menu to a widget with modern styling"""
        if category is None:
            category = self.selected_category
            
        menu = tk.Menu(widget, tearoff=0, bg=self.card_bg, fg=self.text_color, 
                      activebackground=self.primary_color, activeforeground="white",
                      relief="flat", bd=1, borderwidth=8)
        
        menu.add_command(label="     View     ", 
                      command=lambda: self.show_recipe_details(category, recipe_name),
                      font=("Segoe UI", 10))
        menu.add_command(label="     Edit     ", 
                      command=lambda: self.edit_specific_recipe(recipe_name, category),
                      font=("Segoe UI", 10))
        menu.add_separator()
        menu.add_command(label="    Delete    ", 
                      command=lambda: self.delete_specific_recipe(recipe_name, category),
                      font=("Segoe UI", 10, "bold"),
                      foreground=self.accent_color)
        
        # Use a try-except since some widgets might not support binding
        try:
            widget.bind("<Button-3>", lambda e: self.show_context_menu(e, menu))
        except tk.TclError:
            pass

    def show_context_menu(self, event, menu):
        """Show context menu at mouse position"""
        menu.tk_popup(event.x_root, event.y_root)

    def show_recipe_details(self, category, recipe_name):
        """Display recipe details in the third column with enhanced formatting"""
        self.selected_category = category
        self.selected_recipe = recipe_name
        
        if category in self.recipe_data and recipe_name in self.recipe_data[category]:
            recipe_info = self.recipe_data[category][recipe_name]
            
            # Clear previous content
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            
            # Make sure we're showing details frame and not search results
            self.search_results_frame.pack_forget()
            self.details_frame.pack(fill=tk.BOTH, expand=True)
            
            # Recipe title with enhanced styling
            title_frame = ttk.Frame(self.details_frame, style="Header.TFrame")
            title_frame.pack(fill=tk.X, pady=(0, 15))
            
            recipe_title = ttk.Label(title_frame, text=recipe_name, 
                                  style="Title.TLabel",
                                  font=("Segoe UI", 18, "bold"))
            recipe_title.pack(pady=10, padx=15, anchor="w")
            
            # Create scrollable content frame
            content_canvas = tk.Canvas(self.details_frame, bg=self.bg_color, highlightthickness=0)
            content_scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=content_canvas.yview)
            scrollable_content = ttk.Frame(content_canvas, style="TFrame")
            
            scrollable_content.bind(
                "<Configure>",
                lambda e: content_canvas.configure(
                    scrollregion=content_canvas.bbox("all")
                )
            )
            
            content_canvas.create_window((0, 0), window=scrollable_content, anchor="nw", width=content_canvas.winfo_reqwidth())
            content_canvas.configure(yscrollcommand=content_scrollbar.set)
            
            content_canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
            content_scrollbar.pack(side="right", fill="y")
            
            # Description section
            if "description" in recipe_info:
                desc_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
                desc_frame.pack(fill=tk.X, padx=10, pady=10)
                
                desc_title = ttk.Label(desc_frame, text="Description", 
                                    font=("Segoe UI", 14, "bold"),
                                    foreground=self.primary_color)
                desc_title.pack(anchor="w", padx=10, pady=(10, 5))
                
                desc_divider = ttk.Separator(desc_frame, orient="horizontal")
                desc_divider.pack(fill=tk.X, padx=10, pady=(0, 10))
                
                desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=8, 
                                  font=("Segoe UI", 11), bg=self.card_bg, fg=self.text_color, bd=0,
                                  relief=tk.FLAT, padx=15, pady=15,
                                  highlightthickness=1,
                                  highlightcolor=self.highlight_color)
                desc_text.pack(fill=tk.X, padx=10, pady=(0, 10))
                desc_text.insert(tk.END, recipe_info["description"])
                desc_text.config(state=tk.DISABLED)
            
            # Ingredients section
            if "ingredients" in recipe_info:
                ing_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
                ing_frame.pack(fill=tk.X, padx=10, pady=10)
                
                ing_title = ttk.Label(ing_frame, text="Ingredients", 
                                   font=("Segoe UI", 14, "bold"),
                                   foreground=self.primary_color)
                ing_title.pack(anchor="w", padx=10, pady=(10, 5))
                
                ing_divider = ttk.Separator(ing_frame, orient="horizontal")
                ing_divider.pack(fill=tk.X, padx=10, pady=(0, 10))
                
                for ingredient in recipe_info["ingredients"]:
                    ing_item = ttk.Label(ing_frame, text=f"• {ingredient}", 
                                      font=("Segoe UI", 11),
                                      wraplength=450)
                    ing_item.pack(anchor="w", padx=15, pady=2)
            
            # Instructions section
            if "instructions" in recipe_info:
                inst_frame = ttk.Frame(scrollable_content, style="Card.TFrame")
                inst_frame.pack(fill=tk.X, padx=10, pady=10)
                
                inst_title = ttk.Label(inst_frame, text="Instructions", 
                                    font=("Segoe UI", 14, "bold"),
                                    foreground=self.primary_color)
                inst_title.pack(anchor="w", padx=10, pady=(10, 5))
                
                inst_divider = ttk.Separator(inst_frame, orient="horizontal")
                inst_divider.pack(fill=tk.X, padx=10, pady=(0, 10))
                
                for i, step in enumerate(recipe_info["instructions"]):
                    step_frame = ttk.Frame(inst_frame)
                    step_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    step_num = ttk.Label(step_frame, text=f"{i+1}.", 
                                      font=("Segoe UI Semibold", 11),
                                      foreground=self.primary_color,
                                      width=3)
                    step_num.pack(side=tk.LEFT, anchor="n")
                    
                    step_text = ttk.Label(step_frame, text=step, 
                                       font=("Segoe UI", 11),
                                       wraplength=450)
                    step_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Refresh recipe list to show the selected recipe highlighted
            self.populate_recipes(category)

    def show_search_result(self, category, recipe_name):
        """Show a recipe from search results"""
        # Update selected category and recipe
        self.selected_category = category
        self.selected_recipe = recipe_name
        
        # Update category listbox selection
        self.category_listbox.selection_clear(0, tk.END)
        for i in range(self.category_listbox.size()):
            if self.category_listbox.get(i) == category:
                self.category_listbox.selection_set(i)
                break
        
        # Populate recipes for the category
        self.populate_recipes(category)
        
        # Show recipe details
        self.show_recipe_details(category, recipe_name)
        
        # Hide search results and show details
        self.search_results_frame.pack_forget()
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Clear search text
        self.content_search_var.set("Search in all recipes...")

    def add_category(self):
        """Add a new category"""
        self.manage_category()

    def edit_category(self):
        """Edit selected category name"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a category to edit.")
            return
        
        old_name = self.category_listbox.get(selection[0])
        self.manage_category(old_name)

    def delete_category(self):
        """Delete selected category"""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a category to delete.")
            return
        
        category_name = self.category_listbox.get(selection[0])
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{category_name}' and all its recipes?")
        
        if confirm:
            del self.recipe_data[category_name]
            self.save_data()
            self.populate_categories()
            
            # Clear recipe list and details if the deleted category was selected
            if self.selected_category == category_name:
                self.selected_category = None
                self.selected_recipe = None
                self.recipe_list_title.config(text="Recipes")
                for widget in self.scrollable_frame.winfo_children():
                    widget.destroy()
                self.recipe_title_label.config(text="Select a recipe to view details", foreground=self.text_color)
                self.recipe_description_text.config(state=tk.NORMAL)
                self.recipe_description_text.delete(1.0, tk.END)
                self.recipe_description_text.config(state=tk.DISABLED)

    def manage_category(self, old_name=None):
        """Combined method to add or edit a category"""
        title = "Edit Category" if old_name else "Add Category"
        initial_value = old_name if old_name else ""
        
        new_name = simpledialog.askstring(title, "Enter category name:", initialvalue=initial_value)
        if not new_name:
            return
        
        # Check if name already exists and it's not the same as the old name
        if new_name in self.recipe_data and new_name != old_name:
            messagebox.showerror("Error", "Category already exists!")
            return
        
        if old_name:  # Edit mode
            # Copy recipes to new category name
            self.recipe_data[new_name] = self.recipe_data[old_name]
            # Delete old category
            del self.recipe_data[old_name]
            
            # Update currently selected category if it was renamed
            if self.selected_category == old_name:
                self.selected_category = new_name
        else:  # Add mode
            self.recipe_data[new_name] = {}
        
        self.save_data()
        self.populate_categories()
        
        # Select the new/edited category in the listbox
        for i in range(self.category_listbox.size()):
            if self.category_listbox.get(i) == new_name:
                self.category_listbox.selection_set(i)
                break
        
        # Update UI for the selected category
        if old_name:
            self.populate_recipes(new_name)
        else:
            self.on_category_select(None)  # Simulate selection event

    def add_recipe(self):
        """Add a new recipe to the selected category"""
        if not self.selected_category:
            messagebox.showinfo("Info", "Please select a category first.")
            return
        
        self.manage_recipe()

    def edit_recipe(self):
        """Edit selected recipe"""
        if not self.selected_recipe or not self.selected_category:
            messagebox.showinfo("Info", "Please select a recipe to edit.")
            return
        
        self.manage_recipe(self.selected_recipe)

    def delete_recipe(self):
        """Delete selected recipe"""
        if not self.selected_recipe or not self.selected_category:
            messagebox.showinfo("Info", "Please select a recipe to delete.")
            return
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{self.selected_recipe}'?")
        
        if confirm:
            del self.recipe_data[self.selected_category][self.selected_recipe]
            self.save_data()
            self.populate_recipes(self.selected_category)
            
            # Clear recipe details
            self.selected_recipe = None
            self.recipe_title_label.config(text="Select a recipe to view details", foreground=self.text_color)
            self.recipe_description_text.config(state=tk.NORMAL)
            self.recipe_description_text.delete(1.0, tk.END)
            self.recipe_description_text.config(state=tk.DISABLED)

    def edit_specific_recipe(self, recipe_name, category=None):
        """Edit a specific recipe by name"""
        if category is None:
            category = self.selected_category
        
        self.selected_category = category
        self.selected_recipe = recipe_name
        self.manage_recipe(recipe_name)

    def delete_specific_recipe(self, recipe_name, category=None):
        """Delete a specific recipe by name"""
        if category is None:
            category = self.selected_category
        
        if not category:
            return
        
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete '{recipe_name}'?")
        
        if confirm:
            del self.recipe_data[category][recipe_name]
            self.save_data()
            
            # If we're in the same category view, update it
            if self.selected_category == category:
                self.populate_recipes(category)
            
            # Clear recipe details if the deleted recipe was selected
            if self.selected_recipe == recipe_name:
                self.selected_recipe = None
                self.recipe_title_label.config(text="Select a recipe to view details", foreground=self.text_color)
                self.recipe_description_text.config(state=tk.NORMAL)
                self.recipe_description_text.delete(1.0, tk.END)
                self.recipe_description_text.config(state=tk.DISABLED)

    def manage_recipe(self, old_name=None):
        """Combined method to add or edit a recipe"""
        title = "Edit Recipe" if old_name else "Add Recipe"
        
        # Get current recipe details if editing
        current_details = {}
        if old_name:
            current_details = self.recipe_data[self.selected_category][old_name]
        
        # Open the details dialog with integrated name field
        recipe_dialog = RecipeDetailsDialog(self, title, initial_data=current_details, initial_name=old_name)
        result = recipe_dialog.result
        
        if not result:  # User canceled
            return
        
        # Extract name and details
        new_name = result["name"]
        recipe_details = {
            "description": result["description"],
            "ingredients": result["ingredients"],
            "instructions": result["instructions"]
        }
        
        # Check if name already exists and it's not the same as the old name
        if new_name in self.recipe_data[self.selected_category] and new_name != old_name:
            messagebox.showerror("Error", "Recipe already exists in this category!")
            return
        
        # Update recipe data
        if old_name and new_name != old_name:
            # Create with new name and delete old
            self.recipe_data[self.selected_category][new_name] = recipe_details
            del self.recipe_data[self.selected_category][old_name]
        else:
            # Just update the recipe
            self.recipe_data[self.selected_category][new_name] = recipe_details
        
        # Save and update UI
        self.save_data()
        self.selected_recipe = new_name
        self.populate_recipes(self.selected_category)
        self.show_recipe_details(self.selected_category, new_name)


class RecipeDetailsDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_data=None, initial_name=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("650x600")
        self.result = None
        
        # Set default initial data if none provided
        if initial_data is None:
            initial_data = {
                "description": "",
                "ingredients": [],
                "instructions": []
            }
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Apply visual styling to match the enhanced modern theme
        self.configure(bg=parent.bg_color)
        
        # Title
        title_frame = tk.Frame(self, bg=parent.category_header_bg)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(title_frame, text=title, 
                               font=("Segoe UI", 14, "bold"),
                               bg=parent.category_header_bg,
                               fg=parent.primary_color)
        title_label.pack(pady=12, padx=15, anchor="w")
        
        # Recipe name field
        name_frame = tk.Frame(self, bg=parent.bg_color)
        name_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        name_label = tk.Label(name_frame, text="Recipe Name:", 
                           font=("Segoe UI Semibold", 11),
                           bg=parent.bg_color,
                           fg=parent.text_color)
        name_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.name_entry = tk.Entry(name_frame, font=("Segoe UI", 11), 
                                width=40,
                                bg=parent.card_bg,
                                fg=parent.text_color,
                                insertbackground=parent.text_color,
                                highlightthickness=1,
                                highlightcolor=parent.highlight_color)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Set initial name if provided
        if initial_name:
            self.name_entry.insert(0, initial_name)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Basic info tab
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Description")
        
        # Description field
        ttk.Label(basic_frame, text="Recipe Description:", 
                  font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.description_text = tk.Text(basic_frame, wrap=tk.WORD, height=15, 
                                      font=("Segoe UI", 11), bg=parent.card_bg, fg=parent.text_color, bd=0,
                                      relief=tk.FLAT, padx=10, pady=10,
                                      highlightthickness=1,
                                      highlightcolor=parent.highlight_color)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))
        self.description_text.insert(tk.END, initial_data.get("description", ""))
        
        # Ingredients tab
        ingredients_frame = ttk.Frame(self.notebook)
        self.notebook.add(ingredients_frame, text="Ingredients")
        
        # Ingredients list
        ttk.Label(ingredients_frame, text="Ingredients (one per line):", 
                  font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.ingredients_text = tk.Text(ingredients_frame, wrap=tk.WORD, height=15, 
                                      font=("Segoe UI", 11), bg=parent.card_bg, fg=parent.text_color, bd=0,
                                      relief=tk.FLAT, padx=10, pady=10,
                                      highlightthickness=1,
                                      highlightcolor=parent.highlight_color)
        self.ingredients_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))
        
        # Fill ingredients text
        if "ingredients" in initial_data:
            ingredients_text = "\n".join(initial_data["ingredients"])
            self.ingredients_text.insert(tk.END, ingredients_text)
        
        # Instructions tab
        instructions_frame = ttk.Frame(self.notebook)
        self.notebook.add(instructions_frame, text="Instructions")
        
        # Instructions list
        ttk.Label(instructions_frame, text="Instructions (one step per line):", 
                  font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.instructions_text = tk.Text(instructions_frame, wrap=tk.WORD, height=15, 
                                      font=("Segoe UI", 11), bg=parent.card_bg, fg=parent.text_color, bd=0,
                                      relief=tk.FLAT, padx=10, pady=10,
                                      highlightthickness=1,
                                      highlightcolor=parent.highlight_color)
        self.instructions_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 15))
        
        # Fill instructions text
        if "instructions" in initial_data:
            instructions_text = "\n".join(initial_data["instructions"])
            self.instructions_text.insert(tk.END, instructions_text)
        
        # Buttons with enhanced styling - using tk.Button for consistent styling
        btn_frame = tk.Frame(self, bg=parent.bg_color)
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Create custom buttons with direct styling
        save_btn = tk.Button(btn_frame, text="Save", 
                           command=self.save,
                           bg=parent.success_color,
                           fg="white",
                           font=("Segoe UI Semibold", 10),
                           relief=tk.FLAT,
                           padx=10, pady=5,
                           activebackground="#2f855a",
                           activeforeground="white",
                           cursor="hand2")
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", 
                             command=self.cancel,
                             bg=parent.primary_color,
                             fg="white",
                             font=("Segoe UI Semibold", 10),
                             relief=tk.FLAT,
                             padx=10, pady=5,
                             activebackground=parent.secondary_color,
                             activeforeground="white",
                             cursor="hand2")
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Wait for window to be closed
        self.wait_window(self)
    
    def save(self):
        # Get recipe name
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Recipe name cannot be empty!")
            return
            
        # Get description
        description = self.description_text.get(1.0, tk.END).strip()
        
        # Get ingredients (split by lines and remove empty ones)
        ingredients_text = self.ingredients_text.get(1.0, tk.END)
        ingredients = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
        
        # Get instructions (split by lines and remove empty ones)
        instructions_text = self.instructions_text.get(1.0, tk.END)
        instructions = [line.strip() for line in instructions_text.split('\n') if line.strip()]
        
        # Prepare result
        self.result = {
            "name": name,
            "description": description,
            "ingredients": ingredients,
            "instructions": instructions
        }
        
        self.destroy()
    
    def cancel(self):
        self.destroy()


if __name__ == "__main__":
    app = RecipeManager()
    app.mainloop()
