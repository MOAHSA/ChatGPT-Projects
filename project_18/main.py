# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import keyboard
import pyperclip
import time
from threading import Thread
import json
import os
from pathlib import Path
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import winreg

# Comprehensive mapping between English QWERTY and Arabic keyboard layout
eng_to_ar = {
    # Lowercase letters
    "a": "ش", "b": "لا", "c": "ؤ", "d": "ي", "e": "ث",
    "f": "ب", "g": "ل", "h": "ا", "i": "ه", "j": "ت",
    "k": "ن", "l": "م", "m": "ة", "n": "ى", "o": "خ",
    "p": "ح", "q": "ض", "r": "ق", "s": "س", "t": "ف",
    "u": "ع", "v": "ر", "w": "ص", "x": "ء", "y": "غ",
    "z": "ئ",
    
    # Uppercase letters
    "A": "َ", "B": "لآ", "C": "}", "D": "ٍ", "E": "ُ",
    "F": "ِ", "G": "لأ", "H": "أ", "I": "÷", "J": "ـ",
    "K": "،", "L": "/", "M": "'", "N": "آ", "O": "×",
    "P": "؛", "Q": "ّ", "R": "ٌ", "S": "ٍ", "T": "لإ",
    "U": "ˇ", "V": "{", "W": "ً", "X": "ْ", "Y": "إ",
    "Z": "~",
    
    # Numbers
    "1": "٢", "2": "٢", "3": "٣", "4": "٤", "5": "٥",
    "6": "٦", "7": "٧", "8": "٨", "9": "٩", "0": "٠",
    
    # Special characters
    "`": "ذ", "~": "ّ", "!": "!", "@": "@", "#": "#",
    "$": "$", "%": "%", "^": "^", "&": "&", "*": "*",
    "(": ")", ")": "(", "-": "-", "_": "ـ", "=": "=",
    "+": "+", "[": "ج", "]": "د", "{": "<", "}": ">",
    "\\": "\\", "|": "|", ";": "ك", ":": ":", "'": "ط",
    "\"": "\"", ",": "و", ".": "ز", "/": "ظ", "?": "؟",
    "<": ",", ">": "."
}

# Reverse dictionary Arabic → English
ar_to_eng = {v: k for k, v in eng_to_ar.items()}

# Configuration file path
CONFIG_FILE = Path.home() / ".keyboard_flipper_config.json"

def detect_language(text):
    """Detect if text is primarily English or Arabic"""
    arabic_chars = sum(1 for ch in text if ch in ar_to_eng)
    english_chars = sum(1 for ch in text if ch in eng_to_ar and ch.isalpha())
    
    if arabic_chars > english_chars:
        return "Arabic"
    return "English"

def flip_text_auto(text):
    """Automatically detect and convert text"""
    lang = detect_language(text)
    result = []
    
    if lang == "English":
        for ch in text:
            result.append(eng_to_ar.get(ch, ch))
    else:
        for ch in text:
            result.append(ar_to_eng.get(ch, ch))
    
    return "".join(result)

def flip_text_manual(text, from_lang, to_lang):
    """Manually convert text between specified languages"""
    result = []
    if from_lang == "English" and to_lang == "Arabic":
        for ch in text:
            result.append(eng_to_ar.get(ch, ch))
    elif from_lang == "Arabic" and to_lang == "English":
        for ch in text:
            result.append(ar_to_eng.get(ch, ch))
    else:
        result = list(text)
    return "".join(result)

class LayoutFlipperApp:
    def __init__(self, root):
        self.root = root
        self.is_running = True
        self.hotkey_enabled = True
        self.conversion_count = 0
        self.history = []
        self.max_history = 50
        self.tray_icon = None
        self.is_hidden = False
        
        # Load configuration
        self.load_config()
        
        # Set startup if enabled in config
        if self.config["run_on_startup"]:
            self.set_startup(True)
        
        self.setup_gui()
        self.setup_hotkey()
        self.setup_tray_icon()
        
        # Check if should start minimized
        if len(sys.argv) > 1 and sys.argv[1] == "--minimized":
            self.root.after(100, self.hide_to_tray)
    
    def load_config(self):
        """Load configuration from file"""
        self.config = {
            "hotkey_enabled": True,
            "run_on_startup": False,
            "start_minimized": False,
            "theme": "dark",
            "show_notifications": True,
            "history_enabled": True,
            "hotkey": "ctrl+shift"  # Add default hotkey to config
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except:
                pass
        
        self.hotkey_enabled = self.config["hotkey_enabled"]
        self.hotkey = self.config["hotkey"]  # Load hotkey from config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print("Error saving config: {}".format(e))
    
    def setup_gui(self):
        """Setup the GUI"""
        self.root.title("Keyboard Layout Flipper Pro v2.1")
        self.root.geometry("850x700")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(True, True)
        
        # Configure ttk style with custom colors
        style = ttk.Style(self.root)
        style.theme_use("clam")
        
        # Custom color scheme
        style.configure("TFrame", background="#1a1a1a")
        style.configure("TLabel", background="#1a1a1a", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#61dafb")
        style.configure("TButton", 
                       font=("Segoe UI", 10), 
                       padding=8,
                       background="#2d2d30",
                       foreground="#e0e0e0")
        style.map("TButton",
                  background=[("active", "#61dafb"), ("!disabled", "#2d2d30")],
                  foreground=[("active", "#000"), ("!disabled", "#e0e0e0")])
        style.configure("Accent.TButton", 
                       font=("Segoe UI", 11, "bold"),
                       background="#61dafb")
        
        style.configure("TCombobox", 
                       fieldbackground="#3c3f41",
                       background="#61dafb",
                       foreground="#ffffff")
        style.map("TCombobox",
                 fieldbackground=[("readonly", "#3c3f41")])
        
        style.configure("TCheckbutton", 
                       background="#1a1a1a", 
                       foreground="#e0e0e0",
                       font=("Segoe UI", 10))
        
        # Create menu bar
        self.create_menu_bar()
        
        # Main container
        main_canvas = tk.Canvas(self.root, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_frame = ttk.Frame(main_canvas, padding=20)
        
        main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        
        title_label = ttk.Label(header_frame, text="⌨️ Keyboard Layout Flipper Pro", 
                                style="Header.TLabel", font=("Segoe UI", 18, "bold"))
        title_label.pack(side="left")
        
        # Header buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="⚙", width=3, command=self.show_settings).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="📊", width=3, command=self.show_statistics).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="?", width=3, command=self.show_shortcuts).pack(side="left", padx=2)
        
        # Hotkey status card
        status_card = tk.Frame(main_frame, bg="#2d2d30", relief="flat", borderwidth=0)
        status_card.pack(fill="x", pady=(0, 15))
        
        status_inner = ttk.Frame(status_card, padding=15)
        status_inner.pack(fill="x")
        
        status_header = ttk.Frame(status_inner)
        status_header.pack(fill="x", pady=(0, 10))
        
        ttk.Label(status_header, text="🔥 System-Wide Hotkey", 
                  font=("Segoe UI", 14, "bold"), foreground="#ff6b6b").pack(side="left")
        
        self.hotkey_badge = tk.Label(status_header, text="ACTIVE", 
                                     bg="#4CAF50", fg="white", 
                                     font=("Segoe UI", 8, "bold"),
                                     padx=8, pady=2)
        self.hotkey_badge.pack(side="right")
        
        self.hotkey_status_label = ttk.Label(status_inner, 
                                             text="✓ Press Ctrl+Shift to convert selected text anywhere!",
                                             foreground="#4CAF50", font=("Segoe UI", 11))
        self.hotkey_status_label.pack(anchor="w", pady=(5, 10))
        
        # Statistics row
        stats_frame = ttk.Frame(status_inner)
        stats_frame.pack(fill="x")
        
        self.conversion_label = ttk.Label(stats_frame, text="Conversions: 0", 
                                         foreground="#61dafb", font=("Segoe UI", 10, "bold"))
        self.conversion_label.pack(side="left", padx=(0, 20))
        
        self.last_conversion_label = ttk.Label(stats_frame, text="Last: Never", 
                                               foreground="#888", font=("Segoe UI", 9))
        self.last_conversion_label.pack(side="left")
        
        # Toggle controls
        toggle_frame = ttk.Frame(status_inner)
        toggle_frame.pack(anchor="w", pady=(10, 0))
        
        # Update the label to show the current hotkey
        self.hotkey_toggle = ttk.Checkbutton(toggle_frame, 
                                            text="Enable System-Wide Hotkey ({})".format(self.config['hotkey'].upper()),
                                            command=self.toggle_hotkey)
        if self.hotkey_enabled:
            self.hotkey_toggle.state(['selected'])
        self.hotkey_toggle.pack(side="left")
        
        # Quick Actions Panel
        quick_actions = tk.Frame(main_frame, bg="#2d2d30", relief="flat")
        quick_actions.pack(fill="x", pady=(0, 15))
        
        qa_inner = ttk.Frame(quick_actions, padding=10)
        qa_inner.pack(fill="x")
        
        ttk.Label(qa_inner, text="⚡ Quick Actions", 
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        qa_buttons = ttk.Frame(qa_inner)
        qa_buttons.pack(fill="x")
        
        ttk.Button(qa_buttons, text="📋 Convert Clipboard", 
                  command=self.convert_clipboard).pack(side="left", padx=(0, 5))
        ttk.Button(qa_buttons, text="📝 Open History", 
                  command=self.show_history).pack(side="left", padx=5)
        ttk.Button(qa_buttons, text="🗑️ Clear History", 
                  command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(qa_buttons, text="💾 Export Text", 
                  command=self.export_text).pack(side="left", padx=5)
        
        # Separator
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=15)
        
        # Manual conversion section
        ttk.Label(main_frame, text="📝 Manual Conversion", 
                  font=("Segoe UI", 14, "bold"), foreground="#61dafb").pack(anchor="w", pady=(0, 10))
        
        # Language selection frame
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill="x", pady=(0, 15))
        
        langs = ["English", "Arabic"]
        
        # From language
        from_container = ttk.Frame(lang_frame)
        from_container.grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Label(from_container, text="From:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.from_combo = ttk.Combobox(from_container, values=langs, state="readonly", width=18,
                                       font=("Segoe UI", 11))
        self.from_combo.set("English")
        self.from_combo.pack()
        
        # Swap button
        swap_btn = ttk.Button(lang_frame, text="⇄", width=4, command=self.swap_languages,
                             style="Accent.TButton")
        swap_btn.grid(row=0, column=1, padx=15)
        
        # To language
        to_container = ttk.Frame(lang_frame)
        to_container.grid(row=0, column=2, sticky="w", padx=(0, 10))
        ttk.Label(to_container, text="To:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.to_combo = ttk.Combobox(to_container, values=langs, state="readonly", width=18,
                                     font=("Segoe UI", 11))
        self.to_combo.set("Arabic")
        self.to_combo.pack()
        
        # Auto-detect checkbox
        self.auto_detect_var = tk.BooleanVar(value=False)
        auto_detect_cb = ttk.Checkbutton(lang_frame, text="Auto-detect language",
                                         variable=self.auto_detect_var)
        auto_detect_cb.grid(row=0, column=3, padx=(20, 0))
        
        # Input section
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        input_header = ttk.Frame(input_frame)
        input_header.pack(fill="x", pady=(0, 5))
        ttk.Label(input_header, text="Input Text:", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        self.input_char_count = ttk.Label(input_header, text="0 characters", 
                                     foreground="#888", font=("Segoe UI", 9))
        self.input_char_count.pack(side="right")
        
        self.input_box = tk.Text(input_frame, height=8, font=("Consolas", 11),
                            bg="#2d2d30", fg="#e0e0e0", insertbackground="#61dafb",
                            relief="flat", padx=15, pady=15, wrap="word",
                            borderwidth=2, highlightthickness=1, 
                            highlightbackground="#3c3f41", highlightcolor="#61dafb")
        self.input_box.pack(fill="both", expand=True)
        
        # Update character count on input
        def update_char_count(event=None):
            text = self.input_box.get("1.0", tk.END).strip()
            self.input_char_count.config(text="{} characters".format(len(text)))
        self.input_box.bind("<KeyRelease>", update_char_count)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=15)
        
        ttk.Button(buttons_frame, text="🔄 Convert", 
                  style="Accent.TButton", command=self.convert_manual).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="📋 Copy Output", command=self.copy_output).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="📥 Paste", command=self.paste_input).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="🗑️ Clear", command=self.clear_all).pack(side="left", padx=5)
        
        # Output section
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        output_header = ttk.Frame(output_frame)
        output_header.pack(fill="x", pady=(0, 5))
        ttk.Label(output_header, text="Output Text:", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        self.output_char_count = ttk.Label(output_header, text="0 characters", 
                                          foreground="#888", font=("Segoe UI", 9))
        self.output_char_count.pack(side="right")
        
        self.output_box = tk.Text(output_frame, height=8, font=("Consolas", 11),
                             bg="#3c3f41", fg="#ffffff", relief="flat", padx=15, pady=15,
                             wrap="word", state='disabled',
                             borderwidth=2, highlightthickness=1,
                             highlightbackground="#3c3f41", highlightcolor="#61dafb")
        self.output_box.pack(fill="both", expand=True)
        
        # Status bar
        status_bar = tk.Frame(main_frame, bg="#2d2d30", height=30)
        status_bar.pack(fill="x", pady=(10, 0))
        
        status_inner_bar = ttk.Frame(status_bar, padding=5)
        status_inner_bar.pack(fill="both", expand=True)
        
        self.status_label = ttk.Label(status_inner_bar, text="Ready", 
                                      foreground="#4CAF50", font=("Segoe UI", 9, "bold"))
        self.status_label.pack(side="left")
        
        version_label = ttk.Label(status_inner_bar, text="v2.1", 
                                  foreground="#666", font=("Segoe UI", 8))
        version_label.pack(side="right")
        
        # Keyboard shortcuts
        self.root.bind("<Control-Return>", lambda e: self.convert_manual())
        self.root.bind("<Control-c>", lambda e: self.copy_output())
        self.root.bind("<Control-v>", lambda e: self.paste_input())
        self.root.bind("<Control-l>", lambda e: self.clear_all())
        self.root.bind("<Control-h>", lambda e: self.show_shortcuts())
        self.root.bind("<Escape>", lambda e: self.hide_to_tray())
        
        self.input_box.focus_set()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root, bg="#2d2d30", fg="#e0e0e0")
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Text...", command=self.export_text)
        file_menu.add_command(label="Import Text...", command=self.import_text)
        file_menu.add_separator()
        file_menu.add_command(label="Hide to Tray", command=self.hide_to_tray, accelerator="Esc")
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy Output", command=self.copy_output, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste Input", command=self.paste_input, accelerator="Ctrl+V")
        edit_menu.add_command(label="Clear All", command=self.clear_all, accelerator="Ctrl+L")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="History", command=self.show_history)
        view_menu.add_command(label="Statistics", command=self.show_statistics)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Convert Clipboard", command=self.convert_clipboard)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#2d2d30", fg="#e0e0e0")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts, accelerator="Ctrl+H")
        help_menu.add_command(label="Remove from Startup", command=self.remove_from_startup)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_hotkey(self):
        """Setup system-wide hotkey listener"""
        def hotkey_callback():
            if not self.hotkey_enabled:
                return
            
            try:
                time.sleep(0.05)
                keyboard.send('ctrl+c')
                time.sleep(0.1)
                
                selected_text = pyperclip.paste()
                
                if selected_text and selected_text.strip():
                    converted_text = flip_text_auto(selected_text)
                    pyperclip.copy(converted_text)
                    
                    time.sleep(0.05)
                    keyboard.send('ctrl+v')
                    
                    # Update statistics
                    self.conversion_count += 1
                    if self.config["history_enabled"]:
                        self.history.append({
                            "original": selected_text,
                            "converted": converted_text,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        if len(self.history) > self.max_history:
                            self.history.pop(0)
                    
                    self.root.after(0, self.update_conversion_count)
                    self.root.after(0, self.flash_status, "✓ Text converted!")
                    
            except Exception as e:
                print("Error in hotkey callback: {}".format(e))
        
        def register_hotkey():
            try:
                # Use the configurable hotkey instead of hardcoded 'ctrl+shift'
                keyboard.add_hotkey(self.config["hotkey"], hotkey_callback, suppress=True)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Hotkey Error", 
                    "Failed to register hotkey. Try running as administrator.\n\nError: {}".format(e)))
        
        Thread(target=register_hotkey, daemon=True).start()
    
    def setup_tray_icon(self):
        """Setup system tray icon"""
        def create_icon_image():
            img = Image.new('RGB', (64, 64), color='#61dafb')
            draw = ImageDraw.Draw(img)
            draw.rectangle([10, 10, 54, 54], fill='#1a1a1a')
            draw.text((20, 22), "KB", fill='#61dafb')
            return img
        
        def on_show(icon, item):
            self.show_from_tray()
        
        def on_quit(icon, item):
            icon.stop()
            self.on_closing()
        
        menu = Menu(
            MenuItem('Show', on_show, default=True),
            MenuItem('Convert Clipboard', lambda: self.convert_clipboard()),
            MenuItem('Enable/Disable Hotkey', lambda: self.toggle_hotkey()),
            MenuItem('Remove from Startup', lambda: self.remove_from_startup()),
            MenuItem('Quit', on_quit)
        )
        
        self.tray_icon = Icon("KeyboardFlipper", create_icon_image(), 
                              "Keyboard Layout Flipper Pro v2.1", menu)
        
        Thread(target=self.tray_icon.run, daemon=True).start()
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.root.withdraw()
        self.is_hidden = True
    
    def show_from_tray(self):
        """Show window from system tray"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_hidden = False
    
    def toggle_hotkey(self):
        """Toggle the hotkey on/off"""
        self.hotkey_enabled = not self.hotkey_enabled
        self.config["hotkey_enabled"] = self.hotkey_enabled
        self.save_config()
        
        # Update the toggle button text
        self.hotkey_toggle.config(text="Enable System-Wide Hotkey ({})".format(self.config['hotkey'].upper()))
        
        if self.hotkey_enabled:
            self.hotkey_status_label.config(
                text="✓ Press {} to convert selected text anywhere!".format(self.config['hotkey'].upper()),
                foreground="#4CAF50")
            self.hotkey_badge.config(text="ACTIVE", bg="#4CAF50")
            self.flash_status("Hotkey enabled")
        else:
            self.hotkey_status_label.config(
                text="✗ Hotkey is disabled",
                foreground="#ff6b6b")
            self.hotkey_badge.config(text="DISABLED", bg="#ff6b6b")
            self.flash_status("Hotkey disabled")
    
    def update_conversion_count(self):
        """Update the conversion counter"""
        self.conversion_label.config(text="Conversions: {}".format(self.conversion_count))
        self.last_conversion_label.config(text="Last: {}".format(time.strftime('%H:%M:%S')))
    
    def flash_status(self, message):
        """Flash a status message"""
        self.status_label.config(text=message, foreground="#4CAF50")
        self.root.after(3000, lambda: self.status_label.config(text="Ready", foreground="#888"))
    
    def convert_manual(self):
        """Manual conversion in the GUI"""
        text = self.input_box.get("1.0", tk.END).strip()
        
        if not text:
            messagebox.showwarning("Empty Input", "Please enter some text to convert.")
            return
        
        if self.auto_detect_var.get():
            converted = flip_text_auto(text)
        else:
            from_lang = self.from_combo.get()
            to_lang = self.to_combo.get()
            converted = flip_text_manual(text, from_lang, to_lang)
        
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, converted)
        self.output_box.config(state='disabled')
        
        self.output_char_count.config(text="{} characters".format(len(converted)))
        self.flash_status("Text converted")
        
        if self.config["history_enabled"]:
            self.history.append({
                "original": text,
                "converted": converted,
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            if len(self.history) > self.max_history:
                self.history.pop(0)
    
    def swap_languages(self):
        """Swap source and target languages"""
        from_val = self.from_combo.get()
        to_val = self.to_combo.get()
        self.from_combo.set(to_val)
        self.to_combo.set(from_val)
        if self.input_box.get("1.0", tk.END).strip():
            self.convert_manual()
    
    def clear_all(self):
        """Clear both input and output boxes"""
        self.input_box.delete("1.0", tk.END)
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state='disabled')
        self.output_char_count.config(text="0 characters")
        self.input_char_count.config(text="0 characters")
        self.input_box.focus_set()
    
    def copy_output(self):
        """Copy output to clipboard"""
        text = self.output_box.get("1.0", tk.END).strip()
        if text:
            pyperclip.copy(text)
            self.flash_status("✓ Copied to clipboard!")
        else:
            messagebox.showinfo("Empty Output", "Nothing to copy!")
    
    def paste_input(self):
        """Paste from clipboard to input"""
        try:
            text = pyperclip.paste()
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert("1.0", text)
        except Exception as e:
            print("Paste error: {}".format(e))
    
    def convert_clipboard(self):
        """Convert text from clipboard and put it back"""
        try:
            text = pyperclip.paste()
            if text and text.strip():
                converted = flip_text_auto(text)
                pyperclip.copy(converted)
                self.conversion_count += 1
                self.update_conversion_count()
                self.flash_status("✓ Clipboard converted!")
                messagebox.showinfo("Success", "Clipboard text converted!\n\nOriginal: {}...\nConverted: {}...".format(text[:50], converted[:50]))
            else:
                messagebox.showwarning("Empty Clipboard", "Clipboard is empty!")
        except Exception as e:
            messagebox.showerror("Error", "Failed to convert clipboard: {}".format(e))
    
    def show_history(self):
        """Show conversion history"""
        if not self.history:
            messagebox.showinfo("History", "No conversion history yet!")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Conversion History")
        history_window.geometry("700x500")
        history_window.configure(bg="#1a1a1a")
        
        frame = ttk.Frame(history_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="📜 Conversion History", 
                  font=("Segoe UI", 14, "bold"), foreground="#61dafb").pack(pady=(0, 10))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        history_text = tk.Text(text_frame, font=("Consolas", 10), 
                              bg="#2d2d30", fg="#e0e0e0",
                              yscrollcommand=scrollbar.set, wrap="word")
        history_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=history_text.yview)
        
        for i, entry in enumerate(reversed(self.history), 1):
            history_text.insert("end", "━━━ Entry {} ━━━ {} ━━━\n".format(i, entry['time']), "header")
            history_text.insert("end", "Original:  {}\n".format(entry['original']), "original")
            history_text.insert("end", "Converted: {}\n\n".format(entry['converted']), "converted")
        
        history_text.tag_config("header", foreground="#61dafb", font=("Segoe UI", 10, "bold"))
        history_text.tag_config("original", foreground="#ff6b6b")
        history_text.tag_config("converted", foreground="#4CAF50")
        history_text.config(state="disabled")
    
    def clear_history(self):
        """Clear conversion history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all conversion history?"):
            self.history = []
            self.flash_status("History cleared")
    
    def show_statistics(self):
        """Show usage statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("500x400")
        stats_window.configure(bg="#1a1a1a")
        
        frame = ttk.Frame(stats_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="📊 Usage Statistics", 
                  font=("Segoe UI", 14, "bold"), foreground="#61dafb").pack(pady=(0, 20))
        
        stats = [
            ("Total Conversions", self.conversion_count),
            ("History Entries", len(self.history)),
            ("Hotkey Status", "Enabled" if self.hotkey_enabled else "Disabled"),
            ("Run on Startup", "Yes" if self.config["run_on_startup"] else "No")
        ]
        
        for label, value in stats:
            stat_frame = ttk.Frame(frame)
            stat_frame.pack(fill="x", pady=5)
            ttk.Label(stat_frame, text="{}:".format(label), 
                     font=("Segoe UI", 11, "bold")).pack(side="left")
            ttk.Label(stat_frame, text=str(value), 
                     font=("Segoe UI", 11), foreground="#61dafb").pack(side="right")
    
    def show_settings(self):
        """Show settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("550x500")  # Increased height to accommodate new settings
        settings_window.configure(bg="#1a1a1a")
        
        frame = ttk.Frame(settings_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="⚙️ Settings", 
                  font=("Segoe UI", 14, "bold"), foreground="#61dafb").pack(pady=(0, 20))
        
        # Hotkey customization
        ttk.Label(frame, text="Hotkey Settings:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        
        hotkey_frame = ttk.Frame(frame)
        hotkey_frame.pack(fill="x", pady=5)
        
        ttk.Label(hotkey_frame, text="Current hotkey:").pack(side="left")
        self.hotkey_var = tk.StringVar(value=self.config["hotkey"])
        hotkey_entry = ttk.Entry(hotkey_frame, textvariable=self.hotkey_var, width=20)
        hotkey_entry.pack(side="left", padx=10)
        ttk.Label(hotkey_frame, text="e.g., ctrl+shift, alt+z, ctrl+alt+t").pack(side="left")
        
        # Run on startup
        startup_var = tk.BooleanVar(value=self.config["run_on_startup"])
        def on_startup_toggle():
            enable = startup_var.get()
            self.set_startup(enable)
            # Also save to config immediately
            self.config["run_on_startup"] = enable
            self.save_config()
        startup_cb = ttk.Checkbutton(frame, text="Run on Windows startup",
                                     variable=startup_var,
                                     command=on_startup_toggle)
        startup_cb.pack(anchor="w", pady=5)
        
        # Add button to remove from startup
        ttk.Button(frame, text="Remove from Startup", command=self.remove_from_startup).pack(anchor="w", pady=5)
        
        # Start minimized
        minimized_var = tk.BooleanVar(value=self.config["start_minimized"])
        minimized_cb = ttk.Checkbutton(frame, text="Start minimized to tray",
                                       variable=minimized_var)
        minimized_cb.pack(anchor="w", pady=5)
        
        # Show notifications
        notif_var = tk.BooleanVar(value=self.config["show_notifications"])
        notif_cb = ttk.Checkbutton(frame, text="Show notifications",
                                   variable=notif_var)
        notif_cb.pack(anchor="w", pady=5)
        
        # Enable history
        history_var = tk.BooleanVar(value=self.config["history_enabled"])
        history_cb = ttk.Checkbutton(frame, text="Enable conversion history",
                                     variable=history_var)
        history_cb.pack(anchor="w", pady=5)
        
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=20)
        
        # Save button
        def save_settings():
            # Update hotkey in config
            self.config["hotkey"] = self.hotkey_var.get().lower()
            self.config["start_minimized"] = minimized_var.get()
            self.config["show_notifications"] = notif_var.get()
            self.config["history_enabled"] = history_var.get()
            # Note: run_on_startup is handled by the checkbox callback
            self.save_config()
            
            # Update the toggle button text
            self.hotkey_toggle.config(text="Enable System-Wide Hotkey ({})".format(self.config['hotkey'].upper()))
            
            # Update hotkey status label
            if self.hotkey_enabled:
                self.hotkey_status_label.config(
                    text="✓ Press {} to convert selected text anywhere!".format(self.config['hotkey'].upper()))
            
            self.flash_status("Settings saved")
            settings_window.destroy()
            
            # Show message about restarting for hotkey changes
            messagebox.showinfo("Hotkey Change", "Restart the application for hotkey changes to take effect.")
        
        ttk.Button(frame, text="Save Settings", command=save_settings,
                  style="Accent.TButton").pack(pady=10)
    
    def set_startup(self, enable):
        """Set or remove startup registry entry"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            if enable:
                exe_path = sys.executable
                if exe_path.endswith("python.exe"):
                    script_path = os.path.abspath(__file__)
                    value = f'"{exe_path}" "{script_path}" --minimized'
                else:
                    value = f'"{exe_path}" --minimized'
                
                winreg.SetValueEx(key, "KeyboardFlipperPro", 0, winreg.REG_SZ, value)
                # Only flash status if GUI is initialized
                if hasattr(self, 'status_label'):
                    self.flash_status("✓ Added to startup")
            else:
                try:
                    winreg.DeleteValue(key, "KeyboardFlipperPro")
                    # Only flash status if GUI is initialized
                    if hasattr(self, 'status_label'):
                        self.flash_status("✓ Removed from startup")
                except FileNotFoundError:
                    # Only flash status if GUI is initialized
                    if hasattr(self, 'status_label'):
                        self.flash_status("Already removed from startup")
            
            winreg.CloseKey(key)
            self.config["run_on_startup"] = enable
            self.save_config()
            
        except Exception as e:
            messagebox.showerror("Startup Error", "Failed to modify startup settings:\n{}".format(e))
    
    def remove_from_startup(self):
        """Remove the application from Windows startup"""
        self.set_startup(False)
        messagebox.showinfo("Success", "Application removed from Windows startup.")
    
    def export_text(self):
        """Export output text to file"""
        text = self.output_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No Content", "Output is empty!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.flash_status("✓ Exported to {}".format(os.path.basename(filename)))
            except Exception as e:
                messagebox.showerror("Export Error", "Failed to export: {}".format(e))
    
    def import_text(self):
        """Import text from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.input_box.delete("1.0", tk.END)
                self.input_box.insert("1.0", text)
                self.flash_status("✓ Imported from {}".format(os.path.basename(filename)))
            except Exception as e:
                messagebox.showerror("Import Error", "Failed to import: {}".format(e))
    
    def show_shortcuts(self):
        """Display keyboard shortcuts help"""
        shortcuts = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    KEYBOARD SHORTCUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 SYSTEM-WIDE HOTKEY:
    {}        Auto-convert selected text anywhere!

📝 MANUAL CONVERSION:
    Ctrl + Enter        Convert text
    Ctrl + C            Copy output
    Ctrl + V            Paste to input
    Ctrl + L            Clear all
    Ctrl + H            Show shortcuts

🪟 WINDOW CONTROLS:
    Esc                 Hide to system tray

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HOW TO USE SYSTEM-WIDE HOTKEY:

1. Select any text anywhere (browser, Word, etc.)
2. Press {} together
3. Text automatically converts and replaces!

The app auto-detects if text is Arabic or English.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """.format(self.config['hotkey'].upper(), self.config['hotkey'].upper())
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Keyboard Layout Flipper Pro v2.1

A powerful tool to convert text between 
English and Arabic keyboard layouts.

Features:
• System-wide hotkey (customizable)
• Auto language detection
• Conversion history
• System tray integration
• Run on startup
• Export/Import functionality
• Settings panel

Enhanced with customizable hotkeys and improved startup functionality.

Created with ❤️ for productivity
        """
        messagebox.showinfo("About", about_text)
    
    def on_closing(self):
        """Cleanup on exit"""
        self.is_running = False
        try:
            keyboard.unhook_all()
        except:
            pass
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        self.root.destroy()
        sys.exit(0)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = LayoutFlipperApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
