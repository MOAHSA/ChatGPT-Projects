import tkinter as tk
from tkinter import ttk, scrolledtext, font, colorchooser
import os
from pathlib import Path
import pyperclip
from bidi.algorithm import get_display
import arabic_reshaper
import json

class PromptGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مولد وتعزيز النصوص")
        self.root.geometry("1200x800")
        
        # Settings file path
        self.settings_file = "settings.json"
        
        # Define color schemes
        self.light_colors = {
            "background": "#f0f0f0",
            "text": "#333333",
            "button": "#e0e0e0",
            "entry": "#ffffff",
            "entry_text": "#000000",
            "highlight": "#e6f3ff"
        }
        
        self.dark_colors = {
            "background": "#2d2d2d",
            "text": "#ffffff",
            "button": "#404040",
            "entry": "#404040",
            "entry_text": "#ffffff",
            "highlight": "#1a1a1a"
        }
        
        # Load settings or use defaults
        self.load_settings()
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create top bar for language and theme switching
        self.create_top_bar()
        
        # Create left panel for prompts
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create right panel for preview and main message
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Initialize variables
        self.prompts = {}
        self.selected_prompts = {}
        self.prompt_vars = {}
        
        # Create UI elements
        self.create_prompt_list()
        self.create_preview_section()
        self.create_main_message_section()
        self.create_help_section()
        
        # Load prompts
        self.load_prompts()
        
        # Apply RTL for Arabic
        self.apply_rtl()
    
    def load_settings(self):
        default_settings = {
            "language": "ar",
            "dark_mode": False,
            "font": {
                "family": "Arial",
                "size": 10,
                "style": "normal"
            },
            "colors": {
                "background": "#f0f0f0",
                "text": "#333333",
                "button": "#e0e0e0",
                "entry": "#ffffff",
                "entry_text": "#000000",
                "highlight": "#e6f3ff"
            }
        }
        
        if self.settings_file:
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_language = settings.get("language", default_settings["language"])
                    self.is_dark_mode = settings.get("dark_mode", default_settings["dark_mode"])
                    self.current_font = settings.get("font", default_settings["font"])
                    self.colors = settings.get("colors", default_settings["colors"])
            except:
                self.current_language = default_settings["language"]
                self.is_dark_mode = default_settings["dark_mode"]
                self.current_font = default_settings["font"]
                self.colors = default_settings["colors"]
        else:
            self.current_language = default_settings["language"]
            self.is_dark_mode = default_settings["dark_mode"]
            self.current_font = default_settings["font"]
            self.colors = default_settings["colors"]
        
        # Update colors based on theme
        if self.is_dark_mode:
            self.colors = {
                "background": "#2d2d2d",
                "text": "#ffffff",
                "button": "#404040",
                "entry": "#404040",
                "entry_text": "#ffffff",
                "highlight": "#1a1a1a"
            }
    
    def save_settings(self):
        settings = {
            "language": self.current_language,
            "dark_mode": self.is_dark_mode,
            "font": self.current_font,
            "colors": self.colors
        }
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    
    def apply_rtl(self):
        if self.current_language == "ar":
            self.root.tk_setPalette(background=self.colors["background"])
            for widget in self.root.winfo_children():
                if isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
                    widget.pack_configure(side=tk.RIGHT if widget == self.left_panel else tk.LEFT)
                
                # Apply RTL to text widgets
                if isinstance(widget, (scrolledtext.ScrolledText, tk.Text)):
                    widget.tag_configure("rtl", justify="right")
                    widget.tag_add("rtl", "1.0", "end")
                    
                    # Set text direction
                    if hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            if isinstance(child, (tk.Canvas, tk.Frame)):
                                child.pack_configure(side=tk.RIGHT)
    
    def create_top_bar(self):
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X, padx=20, pady=5)
        

        
   

    
    def toggle_language(self):
        self.current_language = "en" if self.current_language == "ar" else "ar"
        self.update_ui_text()
        self.apply_rtl()
        
        # Update text direction for input fields
        if self.current_language == "ar":
            self.main_message.tag_configure("rtl", justify="right")
            self.main_message.tag_add("rtl", "1.0", "end")
            self.preview_text.tag_configure("rtl", justify="right")
            self.preview_text.tag_add("rtl", "1.0", "end")
        else:
            self.main_message.tag_configure("ltr", justify="left")
            self.main_message.tag_add("ltr", "1.0", "end")
            self.preview_text.tag_configure("ltr", justify="left")
            self.preview_text.tag_add("ltr", "1.0", "end")
    
    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.colors = {
                "background": "#2d2d2d",
                "text": "#ffffff",
                "button": "#404040",
                "entry": "#404040",
                "entry_text": "#ffffff",
                "highlight": "#1a1a1a"
            }
        else:
            self.colors = {
                "background": "#f0f0f0",
                "text": "#333333",
                "button": "#e0e0e0",
                "entry": "#ffffff",
                "entry_text": "#000000",
                "highlight": "#e6f3ff"
            }
        self.apply_theme()
        self.save_settings()
    
    def apply_theme(self):
        self.root.configure(bg=self.colors["background"])
        self.style.configure("TFrame", background=self.colors["background"])
        self.style.configure("TLabel", background=self.colors["background"], foreground=self.colors["text"])
        self.style.configure("TButton", background=self.colors["button"], foreground=self.colors["text"])
        self.style.configure("TLabelframe", background=self.colors["background"], foreground=self.colors["text"])
        self.style.configure("TLabelframe.Label", background=self.colors["background"], foreground=self.colors["text"])
    
    def update_ui_text(self):
        # Update all UI text based on current language
        texts = {
            "ar": {
                "title": "مولد وتعزيز النصوص",
                "prompts": "النصوص المتاحة",
                "preview": "معاينة النص",
                "main_message": "الرسالة الرئيسية",
                "generate": "إنشاء النص النهائي",
                "copy": "نسخ إلى الحافظة",
                "help": "المساعدة"
            },
            "en": {
                "title": "Prompt Generator and Enhancer",
                "prompts": "Available Prompts",
                "preview": "Prompt Preview",
                "main_message": "Main Message",
                "generate": "Generate Final Prompt",
                "copy": "Copy to Clipboard",
                "help": "Help"
            }
        }
        
        current_texts = texts[self.current_language]
        self.root.title(current_texts["title"])
        
        # Update all labels and buttons with new text
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                if "prompts" in str(widget):
                    widget.configure(text=current_texts["prompts"])
                elif "preview" in str(widget):
                    widget.configure(text=current_texts["preview"])
                elif "main_message" in str(widget):
                    widget.configure(text=current_texts["main_message"])
    
    def create_prompt_list(self):
        prompt_frame = ttk.LabelFrame(
            self.left_panel,
            text="النصوص المتاحة" if self.current_language == "ar" else "Available Prompts"
        )
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(prompt_frame, bg=self.colors["background"])
        scrollbar = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_preview_section(self):
        preview_frame = ttk.LabelFrame(
            self.right_panel,
            text="معاينة النص" if self.current_language == "ar" else "Prompt Preview"
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            width=40,
            height=10,
            font=(self.current_font["family"], self.current_font["size"]),
            bg=self.colors["entry"],
            fg=self.colors["entry_text"]
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text.configure(state='disabled')
        
        # Add right-click context menu for preview
        self.preview_menu = tk.Menu(self.preview_text, tearoff=0)
        if self.current_language == "ar":
            self.preview_menu.add_command(label="نسخ الكل", command=self.copy_to_clipboard)
        else:
            self.preview_menu.add_command(label="Copy All", command=self.copy_to_clipboard)
        self.preview_text.bind("<Button-3>", self.show_preview_menu)
        self.preview_text.bind("<Button-2>", self.show_preview_menu)  # For Mac
        
        # Set text direction based on language
        if self.current_language == "ar":
            self.preview_text.tag_configure("rtl", justify="right")
            self.preview_text.tag_add("rtl", "1.0", "end")
    
    def create_main_message_section(self):
        message_frame = ttk.LabelFrame(
            self.right_panel,
            text="الرسالة الرئيسية" if self.current_language == "ar" else "Main Message"
        )
        message_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create toolbar for main message
        toolbar = ttk.Frame(message_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Select All button
        select_all_btn = ttk.Button(
            toolbar,
            text="تحديد الكل" if self.current_language == "ar" else "Select All",
            command=lambda: self.main_message.tag_add(tk.SEL, "1.0", tk.END)
        )
        select_all_btn.pack(side=tk.LEFT, padx=2)
        
        # Copy button
        copy_btn = ttk.Button(
            toolbar,
            text="نسخ" if self.current_language == "ar" else "Copy",
            command=lambda: self.main_message.event_generate("<<Copy>>")
        )
        copy_btn.pack(side=tk.LEFT, padx=2)
        
        # Cut button
        cut_btn = ttk.Button(
            toolbar,
            text="قص" if self.current_language == "ar" else "Cut",
            command=lambda: self.main_message.event_generate("<<Cut>>")
        )
        cut_btn.pack(side=tk.LEFT, padx=2)
        
        # Paste button
        paste_btn = ttk.Button(
            toolbar,
            text="لصق" if self.current_language == "ar" else "Paste",
            command=lambda: self.main_message.event_generate("<<Paste>>")
        )
        paste_btn.pack(side=tk.LEFT, padx=2)
        
        # Clear button
        clear_btn = ttk.Button(
            toolbar,
            text="مسح" if self.current_language == "ar" else "Clear",
            command=lambda: self.main_message.delete("1.0", tk.END)
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Create main message text widget with line numbers
        text_frame = ttk.Frame(message_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(
            text_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background=self.colors["entry"],
            foreground=self.colors["entry_text"],
            state='disabled'
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Main message text widget
        self.main_message = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=40,
            height=5,
            font=(self.current_font["family"], self.current_font["size"]),
            bg=self.colors["entry"],
            fg=self.colors["entry_text"],
            undo=True  # Enable undo/redo
        )
        self.main_message.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add right-click context menu for main message
        self.main_message_menu = tk.Menu(self.main_message, tearoff=0)
        if self.current_language == "ar":
            self.main_message_menu.add_command(label="نسخ", command=lambda: self.main_message.event_generate("<<Copy>>"))
            self.main_message_menu.add_command(label="قص", command=lambda: self.main_message.event_generate("<<Cut>>"))
            self.main_message_menu.add_command(label="لصق", command=lambda: self.main_message.event_generate("<<Paste>>"))
            self.main_message_menu.add_command(label="تحديد الكل", command=lambda: self.main_message.tag_add(tk.SEL, "1.0", tk.END))
            self.main_message_menu.add_command(label="مسح", command=lambda: self.main_message.delete("1.0", tk.END))
        else:
            self.main_message_menu.add_command(label="Copy", command=lambda: self.main_message.event_generate("<<Copy>>"))
            self.main_message_menu.add_command(label="Cut", command=lambda: self.main_message.event_generate("<<Cut>>"))
            self.main_message_menu.add_command(label="Paste", command=lambda: self.main_message.event_generate("<<Paste>>"))
            self.main_message_menu.add_command(label="Select All", command=lambda: self.main_message.tag_add(tk.SEL, "1.0", tk.END))
            self.main_message_menu.add_command(label="Clear", command=lambda: self.main_message.delete("1.0", tk.END))
        self.main_message.bind("<Button-3>", self.show_main_message_menu)
        self.main_message.bind("<Button-2>", self.show_main_message_menu)  # For Mac
        
        # Bind events for line numbers
        self.main_message.bind('<<Modified>>', self.update_line_numbers)
        self.main_message.bind('<Key>', self.update_line_numbers)
        self.main_message.bind('<MouseWheel>', self.update_line_numbers)
        
        # Add keyboard shortcuts
        self.main_message.bind('<Control-a>', lambda e: self.main_message.tag_add(tk.SEL, "1.0", tk.END))
        self.main_message.bind('<Control-c>', lambda e: self.main_message.event_generate("<<Copy>>"))
        self.main_message.bind('<Control-x>', lambda e: self.main_message.event_generate("<<Cut>>"))
        self.main_message.bind('<Control-v>', lambda e: self.main_message.event_generate("<<Paste>>"))
        self.main_message.bind('<Control-z>', lambda e: self.main_message.edit_undo())
        self.main_message.bind('<Control-y>', lambda e: self.main_message.edit_redo())
        
        # Add status bar
        status_frame = ttk.Frame(message_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.status_label = ttk.Label(
            status_frame,
            text="0 حرف" if self.current_language == "ar" else "0 characters"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Add action buttons frame
        action_frame = ttk.Frame(message_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Generate button
        generate_btn = ttk.Button(
            action_frame,
            text="إنشاء النص النهائي" if self.current_language == "ar" else "Generate Final Prompt",
            command=self.generate_final_prompt
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy to clipboard button
        copy_clipboard_btn = ttk.Button(
            action_frame,
            text="نسخ إلى الحافظة" if self.current_language == "ar" else "Copy to Clipboard",
            command=self.copy_to_clipboard
        )
        copy_clipboard_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind event for character count
        self.main_message.bind('<KeyRelease>', self.update_character_count)
        
        # Initial line numbers update
        self.update_line_numbers()
    
    def handle_arabic_input(self, event):
        if self.current_language == "ar":
            # Get the current text
            current_text = self.main_message.get("1.0", tk.END)
            
            # Process Arabic text
            reshaped_text = arabic_reshaper.reshape(current_text)
            bidi_text = get_display(reshaped_text)
            if isinstance(bidi_text, bytes):
                bidi_text = bidi_text.decode("utf-8")
            elif isinstance(bidi_text, (bytearray, memoryview)):
                bidi_text = str(bidi_text)
            
            # Update text widget
            self.main_message.delete("1.0", tk.END)
            self.main_message.insert("1.0", bidi_text)
            
            # Apply RTL formatting
            self.main_message.tag_configure("rtl", justify="right")
            self.main_message.tag_add("rtl", "1.0", "end")
            
            # Update character count
            self.update_character_count()
            
            # Update line numbers
            self.update_line_numbers()
    
    def update_line_numbers(self, event=None):
        # Update line numbers
        line_count = self.main_message.get('1.0', tk.END).count('\n')
        line_numbers_text = '\n'.join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
        
        # Reset modified flag
        self.main_message.edit_modified(False)
    
    def update_character_count(self, event=None):
        # Update character count
        text = self.main_message.get('1.0', tk.END)
        char_count = len(text.strip())
        self.status_label.config(
            text=f"{char_count} حرف" if self.current_language == "ar" else f"{char_count} characters"
        )
    
    def create_help_section(self):
        help_btn = ttk.Button(
            self.right_panel,
            text="المساعدة" if self.current_language == "ar" else "Help",
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT, pady=10, padx=5)
        
        # Add settings button
        settings_btn = ttk.Button(
            self.right_panel,
            text="⚙️ الإعدادات" if self.current_language == "ar" else "⚙️ Settings",
            command=self.show_settings
        )
        settings_btn.pack(side=tk.LEFT, pady=10, padx=5)
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("الإعدادات" if self.current_language == "ar" else "Settings")
        settings_window.geometry("600x500")
        
        # Apply RTL to settings window
        if self.current_language == "ar":
            settings_window.tk_setPalette(background=self.colors["background"])
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Font settings tab
        font_frame = ttk.Frame(notebook)
        notebook.add(font_frame, text="الخط" if self.current_language == "ar" else "Font")
        
        # Font family
        font_family_frame = ttk.LabelFrame(font_frame, text="نوع الخط" if self.current_language == "ar" else "Font Family")
        font_family_frame.pack(fill=tk.X, padx=5, pady=5)
        
        font_families = sorted(font.families())
        self.font_family_var = tk.StringVar(value=self.current_font["family"])
        font_family_dropdown = ttk.Combobox(
            font_family_frame,
            textvariable=self.font_family_var,
            values=font_families,
            width=30,
            state="readonly"
        )
        font_family_dropdown.pack(padx=5, pady=5)
        font_family_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_font_settings(settings_window))
        
        # Font size
        font_size_frame = ttk.LabelFrame(font_frame, text="حجم الخط" if self.current_language == "ar" else "Font Size")
        font_size_frame.pack(fill=tk.X, padx=5, pady=5)
        
        font_sizes = [str(size) for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]]
        self.font_size_var = tk.StringVar(value=str(self.current_font["size"]))
        font_size_dropdown = ttk.Combobox(
            font_size_frame,
            textvariable=self.font_size_var,
            values=font_sizes,
            width=10,
            state="readonly"
        )
        font_size_dropdown.pack(padx=5, pady=5)
        font_size_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_font_settings(settings_window))
        
        # Font style
        style_frame = ttk.LabelFrame(font_frame, text="نمط الخط" if self.current_language == "ar" else "Font Style")
        style_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.bold_var = tk.BooleanVar(value="bold" in self.current_font["style"])
        self.italic_var = tk.BooleanVar(value="italic" in self.current_font["style"])
        
        bold_cb = ttk.Checkbutton(
            style_frame,
            text="غامق" if self.current_language == "ar" else "Bold",
            variable=self.bold_var,
            command=lambda: self.update_font_settings(settings_window)
        )
        bold_cb.pack(padx=5, pady=2)
        
        italic_cb = ttk.Checkbutton(
            style_frame,
            text="مائل" if self.current_language == "ar" else "Italic",
            variable=self.italic_var,
            command=lambda: self.update_font_settings(settings_window)
        )
        italic_cb.pack(padx=5, pady=2)
        
        # Colors tab
        colors_frame = ttk.Frame(notebook)
        notebook.add(colors_frame, text="الألوان" if self.current_language == "ar" else "Colors")
        
        # Text color
        text_color_frame = ttk.LabelFrame(colors_frame, text="لون النص" if self.current_language == "ar" else "Text Color")
        text_color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        text_color_btn = ttk.Button(
            text_color_frame,
            text="اختر لون النص" if self.current_language == "en" else "اختر لون النص",
            command=lambda: self.choose_text_color(settings_window)
        )
        text_color_btn.pack(padx=5, pady=5)
        
        # Background color
        bg_color_frame = ttk.LabelFrame(colors_frame, text="لون الخلفية" if self.current_language == "ar" else "Background Color")
        bg_color_frame.pack(fill=tk.X, padx=5, pady=5)
        
        bg_color_btn = ttk.Button(
            bg_color_frame,
            text="اختر لون الخلفية" if self.current_language == "en" else "اختر لون الخلفية",
            command=lambda: self.choose_bg_color(settings_window)
        )
        bg_color_btn.pack(padx=5, pady=5)
        
        # Theme tab
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="المظهر" if self.current_language == "ar" else "Theme")
        
        # Dark mode toggle
        dark_mode_frame = ttk.LabelFrame(theme_frame, text="الوضع المظلم" if self.current_language == "ar" else "Dark Mode")
        dark_mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        dark_mode_var = tk.BooleanVar(value=self.is_dark_mode)
        dark_mode_cb = ttk.Checkbutton(
            dark_mode_frame,
            text="تفعيل الوضع المظلم" if self.current_language == "ar" else "Enable Dark Mode",
            variable=dark_mode_var,
            command=lambda: self.toggle_theme_and_update(settings_window)
        )
        dark_mode_cb.pack(padx=5, pady=5)
        
        # Preview section
        preview_frame = ttk.LabelFrame(settings_window, text="معاينة" if self.current_language == "ar" else "Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.settings_preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            width=40,
            height=5,
            font=(self.current_font["family"], self.current_font["size"]),
            bg=self.colors["background"],
            fg=self.colors["text"]
        )
        self.settings_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add sample text based on language
        sample_text = "نص تجريبي للعربية" if self.current_language == "ar" else "Sample Text"
        if isinstance(sample_text, bytes):
            sample_text = sample_text.decode('utf-8')
        elif isinstance(sample_text, bytearray):
            sample_text = sample_text.decode('utf-8')
        elif isinstance(sample_text, memoryview):
            sample_text = sample_text.tobytes().decode('utf-8')
        self.settings_preview_text.insert(tk.END, sample_text)
        if self.current_language == "ar":
            self.settings_preview_text.tag_configure("rtl", justify="right")
            self.settings_preview_text.tag_add("rtl", "1.0", "end")
        self.settings_preview_text.configure(state='disabled')

    def update_font_settings(self, settings_window=None):
        self.current_font["family"] = self.font_family_var.get()
        self.current_font["size"] = int(self.font_size_var.get())
        style = []
        if self.bold_var.get():
            style.append("bold")
        if self.italic_var.get():
            style.append("italic")
        self.current_font["style"] = " ".join(style)
        self.apply_font_to_text_widgets()
        self.save_settings()
        self.update_settings_preview()

    def choose_text_color(self, settings_window=None):
        color = colorchooser.askcolor(title="Choose Text Color" if self.current_language == "en" else "اختر لون النص")
        if color[1]:
            self.colors["text"] = color[1]
            self.main_message.configure(fg=color[1])
            self.preview_text.configure(fg=color[1])
            self.save_settings()
            self.update_settings_preview()

    def choose_bg_color(self, settings_window=None):
        color = colorchooser.askcolor(title="Choose Background Color" if self.current_language == "en" else "اختر لون الخلفية")
        if color[1]:
            self.colors["background"] = color[1]
            self.main_message.configure(bg=color[1])
            self.preview_text.configure(bg=color[1])
            self.save_settings()
            self.update_settings_preview()

    def update_settings_preview(self):
        # Update the preview in the settings window
        self.settings_preview_text.configure(state='normal')
        self.settings_preview_text.delete('1.0', tk.END)
        sample_text = "نص تجريبي للعربية" if self.current_language == "ar" else "Sample Text"
        if isinstance(sample_text, bytes):
            sample_text = sample_text.decode('utf-8')
        elif isinstance(sample_text, bytearray):
            sample_text = sample_text.decode('utf-8')
        elif isinstance(sample_text, memoryview):
            sample_text = sample_text.tobytes().decode('utf-8')
        self.settings_preview_text.insert(tk.END, sample_text)
        self.settings_preview_text.configure(font=(self.current_font["family"], self.current_font["size"]),
                                            bg=self.colors["background"], fg=self.colors["text"])
        if self.current_language == "ar":
            self.settings_preview_text.tag_configure("rtl", justify="right")
            self.settings_preview_text.tag_add("rtl", "1.0", "end")
        self.settings_preview_text.configure(state='disabled')

    def toggle_theme_and_update(self, settings_window=None):
        self.toggle_theme()
        self.save_settings()
        self.update_settings_preview()
        self.apply_font_to_text_widgets()

    def load_prompts(self):
        data_dir = Path("Data")
        for folder in data_dir.iterdir():
            if folder.is_dir():
                folder_name = folder.name
                folder_frame = ttk.LabelFrame(self.scrollable_frame, text=folder_name)
                folder_frame.pack(fill=tk.X, padx=5, pady=5)
                
                max_columns = 4  # عدد الأعمدة
                row = 0
                col = 0
                for file in folder.glob("*.md"):
                    var = tk.BooleanVar()
                    self.prompt_vars[file.name] = var
                    
                    cb = ttk.Checkbutton(
                        folder_frame,
                        text=file.name,
                        variable=var,
                        command=lambda f=file: self.update_preview(f)
                    )
                    cb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
                    
                    # Read and store prompt content
                    with open(file, 'r', encoding='utf-8') as f:
                        self.prompts[file.name] = f.read()
                    
                    col += 1
                    if col >= max_columns:
                        col = 0
                        row += 1
    
    def update_preview(self, file):
        if file.name in self.prompts:
            self.preview_text.configure(state='normal')
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, self.prompts[file.name])
            self.preview_text.configure(state='disabled')
    
    def generate_final_prompt(self):
        final_prompt = ""
        
        # Add clear instructions and emphasis
        if self.current_language == "ar":
            final_prompt += "=" * 80 + "\n"
            final_prompt += "تعليمات هامة:\n"
            final_prompt += "1. الرسالة الرئيسية أدناه هي محور تركيزك الأساسي ومهمتك الأولى\n"
            final_prompt += "2. استخدم السياق الإضافي فقط لتعزيز فهمك\n"
            final_prompt += "3. لا تدع السياق الإضافي يشتتك عن المهمة الأساسية\n"
            final_prompt += "4. أعطِ الأولوية دائمًا لمتطلبات الرسالة الرئيسية\n"
            final_prompt += "=" * 80 + "\n\n"
        else:
            final_prompt += "=" * 80 + "\n"
            final_prompt += "CRITICAL INSTRUCTION:\n"
            final_prompt += "1. The MAIN MESSAGE below is your PRIMARY focus and task\n"
            final_prompt += "2. The supplementary context should ONLY be used to enhance your understanding\n"
            final_prompt += "3. Do not let the supplementary context distract from the main task\n"
            final_prompt += "4. Always prioritize the requirements in the main message\n"
            final_prompt += "=" * 80 + "\n\n"
        
        # Add main message with strong emphasis
        main_message = self.main_message.get(1.0, tk.END).strip()
        if main_message:
            if self.current_language == "ar":
                main_message = arabic_reshaper.reshape(main_message)
                main_message = get_display(main_message)
                if isinstance(main_message, bytes):
                    main_message = main_message.decode("utf-8")
                elif isinstance(main_message, (bytearray, memoryview)):
                    main_message = str(main_message)
                final_prompt += "🔴 الرسالة الرئيسية (المهمة الأساسية) 🔴\n"
                final_prompt += "-" * 50 + "\n"
                final_prompt += main_message + "\n"
                final_prompt += "-" * 50 + "\n\n"
                # Add transition to supplementary context
                final_prompt += "📚 السياق الإضافي (معلومات داعمة فقط) 📚\n"
                final_prompt += "ملاحظة: استخدم هذه النصوص فقط لتعزيز فهمك للمهمة الرئيسية أعلاه.\n"
                final_prompt += "=" * 80 + "\n\n"
            else:
                final_prompt += "🔴 MAIN MESSAGE (PRIMARY TASK) 🔴\n"
                final_prompt += "-" * 50 + "\n"
                final_prompt += main_message + "\n"
                final_prompt += "-" * 50 + "\n\n"
                # Add transition to supplementary context
                final_prompt += "📚 SUPPLEMENTARY CONTEXT (Supporting Information Only) 📚\n"
                final_prompt += "Note: Use these prompts only to enhance your understanding of the main task above.\n"
                final_prompt += "=" * 80 + "\n\n"
        
        # Add selected prompts with clear separation
        prompt_count = 0
        for file_name, var in self.prompt_vars.items():
            if var.get():
                prompt_count += 1
                final_prompt += f"Supplementary Prompt #{prompt_count}:\n"
                final_prompt += "-" * 40 + "\n"
                final_prompt += self.prompts[file_name] + "\n"
                final_prompt += "-" * 40 + "\n\n"
        
        # Add final reminder
        if prompt_count > 0:
            final_prompt += "=" * 80 + "\n"
            final_prompt += "REMINDER: Return to the MAIN MESSAGE above and ensure your response primarily addresses those requirements.\n"
            final_prompt += "=" * 80 + "\n"
        
        # Show result in preview
        self.preview_text.configure(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, final_prompt)
        self.preview_text.configure(state='disabled')
        
        # Apply RTL if Arabic
        if self.current_language == "ar":
            self.preview_text.tag_configure("rtl", justify="right")
            self.preview_text.tag_add("rtl", "1.0", "end")
    
    def copy_to_clipboard(self):
        text = self.preview_text.get(1.0, tk.END).strip()
        pyperclip.copy(text)
    
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("المساعدة" if self.current_language == "ar" else "Help")
        help_window.geometry("600x400")
        
        help_text_ar = """
كيفية استخدام مولد النصوص:

1. اختيار النصوص:
   - تصفح النصوص المتاحة في اللوحة اليسرى
   - حدد مربعات الاختيار بجانب النصوص التي تريد تضمينها
   - انقر على أي نص لمعاينة محتواه

2. إضافة رسالتك:
   - اكتب رسالتك الرئيسية في مربع "الرسالة الرئيسية"
   - يمكنك كتابة عدة أسطر

3. إنشاء النص النهائي:
   - انقر على زر "إنشاء النص النهائي" لدمج النصوص المحددة مع رسالتك
   - ستظهر النتيجة في قسم المعاينة

4. نسخ النتيجة:
   - انقر على "نسخ إلى الحافظة" لنسخ النص النهائي
   - يمكنك لصقه حيث تحتاج

نصائح:
- يمكنك اختيار عدة نصوص من فئات مختلفة
- قسم المعاينة يعرض محتوى النص المحدد
- النص النهائي يجمع جميع النصوص المحددة مع رسالتك
        """
        
        help_text_en = """
How to Use the Prompt Generator:

1. Select Prompts:
   - Browse through the available prompts in the left panel
   - Check the boxes next to the prompts you want to include
   - Click on any prompt to preview its content

2. Add Your Message:
   - Type your main message in the "Main Message" text box
   - You can write multiple lines

3. Generate Final Prompt:
   - Click the "Generate Final Prompt" button to combine selected prompts with your message
   - The result will appear in the preview section

4. Copy Result:
   - Click "Copy to Clipboard" to copy the generated prompt
   - You can then paste it wherever you need

Tips:
- You can select multiple prompts from different categories
- The preview section shows the content of the selected prompt
- The final prompt combines all selected prompts with your message
        """
        
        help_text = help_text_ar if self.current_language == "ar" else help_text_en
        
        help_label = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 10),
            bg=self.colors["entry"],
            fg=self.colors["entry_text"]
        )
        help_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        help_label.insert(tk.END, help_text)
        
        # Set text direction based on language
        if self.current_language == "ar":
            help_label.tag_configure("rtl", justify="right")
            help_label.tag_add("rtl", "1.0", "end")
        
        help_label.configure(state='disabled')

    def apply_font_to_text_widgets(self):
        font_config = (self.current_font["family"], self.current_font["size"])
        if "bold" in self.current_font["style"]:
            font_config = (self.current_font["family"], self.current_font["size"], "bold")
        if "italic" in self.current_font["style"]:
            font_config = (self.current_font["family"], self.current_font["size"], "italic")
        
        self.main_message.configure(font=font_config)
        self.preview_text.configure(font=font_config)
    
    def show_main_message_menu(self, event):
        try:
            self.main_message_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.main_message_menu.grab_release()

    def show_preview_menu(self, event):
        try:
            self.preview_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.preview_menu.grab_release()

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptGeneratorApp(root)
    root.mainloop() 