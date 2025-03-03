import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font, PhotoImage, TclError, BooleanVar, StringVar, Text, Scrollbar, Canvas, Frame
import subprocess
import threading
import queue
import os
import platform
import time
import ipaddress
import re
import json
from datetime import datetime
from ttkthemes import ThemedTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import ttkthemes
from functools import lru_cache
import concurrent.futures
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

class NmapScannerApp:
    def __init__(self, root):
        """Initialize the application"""
        # Initialize root window
        self.root = root
        self.root.title("Advanced Nmap Scanner")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Create menubar first
        self.create_menubar()
        
        # Initialize core variables
        self._init_core_variables()
        
        # Initialize style
        self._init_style()
        
        # Initialize loading screen
        self._init_loading_screen()
        
        # Schedule main initialization
        self.root.after(100, self._init_main)

    def create_menubar(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Load Configuration", command=self.load_configs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        
        # Available themes
        self.theme_var = tk.StringVar(value="plastik")
        self.available_themes = [
            "plastik",  # Default
            "arc",
            "clearlooks",
            "radiance",
            "ubuntu",
            "breeze",
            "equilux",
            "black",
            "blue",
            "aquativo",
            "kroc",
            "winxpblue",
            "keramik",
        ]
        
        for theme in self.available_themes:
            theme_menu.add_radiobutton(
                label=theme.capitalize(),
                value=theme,
                variable=self.theme_var,
                command=self.change_theme
            )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_info)

    def _init_core_variables(self):
        """Initialize core state variables"""
        # Core state variables
        self.is_updating = False
        self.scan_running = False
        self.current_process = None
        self.output_queue = queue.Queue()
        self.output_buffer = []
        self.update_interval = 100
        
        # Initialize caches
        self._command_cache = {}
        self._last_command_hash = None
        self._target_cache = {}
        
        # Initialize thread pool
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.result_cache = {}

    def _init_style(self):
        """Initialize application style"""
        self.style = ttk.Style()
        
        # Load saved theme preference
        self.load_theme_preference()
        
        # Apply theme (will use default if no saved preference)
        try:
            self.style.theme_use(self.theme_var.get())
        except:
            self.style.theme_use('plastik')  # Fallback to default
            self.theme_var.set('plastik')
        
        # Setup theme colors
        self.setup_theme_colors()
        self.configure_styles()

    def _init_loading_screen(self):
        """Initialize loading screen"""
        self.loading_var = tk.StringVar(value="Loading...")
        self.loading_label = ttk.Label(
            self.root, 
            textvariable=self.loading_var,
            style='Loading.TLabel'
        )
        self.loading_label.place(relx=0.5, rely=0.5, anchor='center')

    def _init_main(self):
        """Main initialization sequence"""
        try:
            # Initialize all variables first
            self.initialize_variables()
            
            # Create main container
            self.main_container = ttk.Frame(self.root, style='Main.TFrame')
            self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create GUI elements in order
            self._create_gui_elements()
            
            # Start output processing
            self.process_output()
            
            # Remove loading screen
            self.loading_label.destroy()
            
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {str(e)}")
            self.root.destroy()

    def _create_gui_elements(self):
        """Create GUI elements in correct order"""
        # Create header
        self.create_header()
        
        # Create notebook and pack it
        self.notebook = ttk.Notebook(self.main_container, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs after notebook is packed
        self.create_tabs()
        
        # Create footer last
        self.create_footer()

    def initialize_sections(self):
        """Initialize all sections of the application"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create frames for each tab
        target_frame = ttk.Frame(self.notebook)
        scan_type_frame = ttk.Frame(self.notebook)
        port_options_frame = ttk.Frame(self.notebook)
        timing_frame = ttk.Frame(self.notebook)
        script_frame = ttk.Frame(self.notebook)
        evasion_frame = ttk.Frame(self.notebook)
        expert_frame = ttk.Frame(self.notebook)
        output_frame = ttk.Frame(self.notebook)
        analysis_frame = ttk.Frame(self.notebook)
        history_frame = ttk.Frame(self.notebook)
        
        # Add frames to notebook
        self.notebook.add(target_frame, text='Target')
        self.notebook.add(scan_type_frame, text='Scan Type')
        self.notebook.add(port_options_frame, text='Port Options')
        self.notebook.add(timing_frame, text='Timing')
        self.notebook.add(script_frame, text='Scripts')
        self.notebook.add(evasion_frame, text='Evasion')
        self.notebook.add(expert_frame, text='Expert')
        self.notebook.add(output_frame, text='Output')
        self.notebook.add(analysis_frame, text='Analysis')
        self.notebook.add(history_frame, text='History')
        
        # Create tab contents
        self.create_target_tab(target_frame)
        self.create_scan_type_tab(scan_type_frame)
        self.create_port_options_tab(port_options_frame)
        self.create_timing_tab(timing_frame)
        self.create_script_tab(script_frame)
        self.create_evasion_tab(evasion_frame)
        self.create_expert_commands_tab(expert_frame)
        self.create_output_tab(output_frame)
        self.create_analysis_tab(analysis_frame)
        self.create_history_tab(history_frame)

    def setup_theme_colors(self):
        """Setup theme colors"""
        # Modern color scheme optimized for plastik theme
        self.bg_color = "#e8e8e8"  # Light gray background
        self.fg_color = "#2c2c2c"  # Dark text
        self.accent_color = "#2b5797"  # Metro blue
        self.alt_color = "#ffffff"  # White
        self.success_color = "#1e7145"  # Metro green
        self.warning_color = "#fa6800"  # Metro orange
        self.error_color = "#ce352c"  # Metro red
        self.border_color = "#c0c0c0"  # Light border
        self.hover_color = "#3670b9"  # Lighter blue for hover

    def initialize_variables(self):
        """Initialize all variables"""
        # Initialize all your variables here
        self.source_ip_var = tk.StringVar()
        self.interface_var = tk.StringVar()
        self.proxy_var = tk.StringVar()
        self.hex_data_var = tk.StringVar()
        self.ascii_data_var = tk.StringVar()
        self.data_length_var = tk.StringVar()
        self.badsum_var = tk.BooleanVar()
        self.mtu_var = tk.StringVar()
        self.fragment_var = tk.BooleanVar()
        self.decoy_var = tk.StringVar()
        self.spoof_mac_var = tk.StringVar()
        self.ttl_var = tk.StringVar()

        # Initialize variables for output options
        self.normal_output_var = tk.BooleanVar()
        self.normal_file_var = tk.StringVar()
        self.xml_output_var = tk.BooleanVar()
        self.xml_file_var = tk.StringVar()
        self.script_output_var = tk.BooleanVar()
        self.script_file_var = tk.StringVar()
        self.grep_output_var = tk.BooleanVar()
        self.grep_file_var = tk.StringVar()
        self.all_output_var = tk.BooleanVar()
        self.all_file_var = tk.StringVar()

        # Initialize variables for additional options
        self.reason_var = tk.BooleanVar()
        self.open_var = tk.BooleanVar()
        self.packet_trace_var = tk.BooleanVar()
        self.iflist_var = tk.BooleanVar()
        self.append_var = tk.BooleanVar()
        self.noninteractive_var = tk.BooleanVar()

        # Initialize verbosity and debug levels
        self.verbosity_var = tk.IntVar(value=0)
        self.debug_var = tk.IntVar(value=0)

        # Initialize other required variables
        self.scan_running = False
        self.current_process = None
        self.output_queue = queue.Queue()
        
        # Initialize history list
        self.history_list = None  # Will be created in create_history_tab
        
        # Initialize thread pool and queue
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.scan_thread = None
        
        # Add result cache
        self.result_cache = {}
        
        # Reduce GUI updates
        self.update_interval = 100  # ms
        self.output_buffer = []
        self.is_updating = False
        
        # Add command caching
        self._command_cache = {}
        self._last_command_hash = None
        
        # Add target validation cache
        self._target_cache = {}

        # Add missing variables for port states
        self.port_open_var = tk.BooleanVar(value=True)
        self.port_closed_var = tk.BooleanVar()

        # Add missing variables for scan history
        self.current_command = None

        # Add missing variables for timing options
        self.host_timeout_var = tk.StringVar()
        self.min_rtt_var = tk.StringVar()
        self.max_rtt_var = tk.StringVar()
        self.max_retries_var = tk.StringVar()

        # Add missing port-related variables
        self.port_type_var = tk.StringVar(value="default")
        self.target_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.target_file_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.exclude_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.random_count_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.dns_resolution_var = tk.StringVar(value="default")
        self.dns_server_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.scan_type_var = tk.StringVar(value="normal")
        self.custom_scan_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.discovery_type_var = tk.StringVar(value="default")
        self.custom_discovery_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.port_specific_entry = ttk.Entry(self.root)  # Will be properly placed later
        self.service_detection_var = tk.BooleanVar()
        self.intensity_var = tk.StringVar()
        self.os_detection_var = tk.BooleanVar()
        self.aggressive_os_var = tk.BooleanVar()
        self.random_targets_var = tk.BooleanVar()

        # Initialize results tab widgets
        self.stop_button = ttk.Button(self.root, text="Stop Scan", command=self.stop_scan, state=tk.DISABLED)
        self.progress_bar = ttk.Progressbar(self.root, mode='indeterminate')
        self.output_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg=self.alt_color,
            fg=self.fg_color,
            font=('Consolas', 10)
        )

        # Output format variables
        self.stylesheet_var = tk.StringVar()
        self.webxml_var = tk.BooleanVar()
        self.no_stylesheet_var = tk.BooleanVar()
        
        # Verbosity and debug
        self.verbosity_var = tk.IntVar(value=0)
        self.debug_var = tk.IntVar(value=0)
        
        # Additional options
        self.reason_var = tk.BooleanVar()
        self.open_var = tk.BooleanVar()
        self.packet_trace_var = tk.BooleanVar()
        self.iflist_var = tk.BooleanVar()
        self.append_var = tk.BooleanVar()
        self.noninteractive_var = tk.BooleanVar()
        self.resume_var = tk.StringVar()

        # Add animation variables
        self.animation_chars = ["◜", "◠", "◝", "◞", "◡", "◟"]  # Simpler animation chars
        self.animation_index = 0
        self.animation_after_id = None
        self.animation_running = False

    def configure_styles(self):
        """Configure styles with reduced updates"""
        if hasattr(self, '_styles_configured'):
            return
        
        # Update colors for a more modern look
        self.bg_color = "#2b2b2b"  # Dark background
        self.fg_color = "#ffffff"  # Crisp white text
        self.accent_color = "#3584e4"  # Modern blue
        self.alt_color = "#333333"  # Slightly lighter background
        self.success_color = "#26a269"  # Green
        self.warning_color = "#cd9309"  # Orange
        self.error_color = "#c01c28"  # Red
        self.border_color = "#1b1b1b"  # Darker border
        self.hover_color = "#4a86e8"  # Lighter blue for hover
        
        # Configure modern styles with theme integration
        self.style.configure('Main.TFrame',
            background=self.bg_color
        )
        
        self.style.configure('Header.TLabel',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 12, 'bold')
        )
        
        self.style.configure('TButton',
            font=('Segoe UI', 9),
            padding=(12, 6),
            background=self.accent_color,
            relief="flat"
        )
        self.style.map('TButton',
            background=[('active', self.hover_color), ('pressed', self.accent_color)],
            relief=[('pressed', 'sunken')]
        )
        
        # Special style for execute button
        self.style.configure('Execute.TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8),
            background=self.success_color
        )
        self.style.map('Execute.TButton',
            background=[('active', '#2ec27e'), ('pressed', '#26a269')]
        )
        
        self.style.configure('TNotebook',
            background=self.bg_color,
            tabmargins=[2, 5, 2, 0]
        )
        self.style.configure('TNotebook.Tab',
            padding=[15, 5],
            font=('Segoe UI', 9),
            background=self.alt_color
        )
        self.style.map('TNotebook.Tab',
            background=[('selected', self.accent_color)],
            foreground=[('selected', '#ffffff'), ('!selected', '#cccccc')]
        )
        
        self.style.configure('TLabelframe',
            background=self.bg_color,
            foreground=self.fg_color,
            bordercolor=self.border_color,
            relief="solid",
            borderwidth=1
        )
        self.style.configure('TLabelframe.Label',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 9, 'bold')
        )
        
        self.style.configure('TCheckbutton',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 9)
        )
        self.style.map('TCheckbutton',
            background=[('active', self.bg_color)],
            foreground=[('active', self.fg_color)]
        )
        
        self.style.configure('TEntry',
            fieldbackground=self.alt_color,
            foreground=self.fg_color,
            padding=8,
            relief="flat",
            borderwidth=1,
            insertcolor=self.fg_color  # Cursor color
        )
        
        self.style.configure('TSpinbox',
            fieldbackground=self.alt_color,
            foreground=self.fg_color,
            padding=5,
            relief="flat",
            borderwidth=1,
            arrowcolor=self.fg_color
        )
        
        # Configure Listbox style
        self.root.option_add('*TListbox*Background', self.alt_color)
        self.root.option_add('*TListbox*Foreground', self.fg_color)
        self.root.option_add('*TListbox*selectBackground', self.accent_color)
        self.root.option_add('*TListbox*selectForeground', self.fg_color)
        
        # Configure Text widget style
        self.root.option_add('*Text*Background', self.alt_color)
        self.root.option_add('*Text*Foreground', self.fg_color)
        self.root.option_add('*Text*selectBackground', self.accent_color)
        self.root.option_add('*Text*selectForeground', self.fg_color)
        self.root.option_add('*Text*insertBackground', self.fg_color)
        
        self._styles_configured = True

    def create_header(self):
        """Create the header with the app title and info"""
        header_frame = ttk.Frame(self.main_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = ttk.Label(header_frame, text="ADVANCED NMAP SCANNER", style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Add information button
        info_button = ttk.Button(header_frame, text="About", command=self.show_info)
        info_button.pack(side=tk.RIGHT, padx=5)
        
        # Add help button
        help_button = ttk.Button(header_frame, text="Help", command=self.show_help)
        help_button.pack(side=tk.RIGHT, padx=5)
        
        # Add a separator
        separator = ttk.Separator(self.main_container, orient='horizontal')
        separator.pack(fill=tk.X, padx=5, pady=5)
    
    def create_footer(self):
        """Create the footer with command preview and run button"""
        footer_frame = ttk.Frame(self.main_container, style='Footer.TFrame')
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Command preview
        preview_label = ttk.Label(footer_frame, text="Command Preview:", style='Footer.TLabel')
        preview_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.command_preview = tk.Text(footer_frame, height=3, width=80, bg=self.alt_color, fg=self.fg_color, wrap=tk.WORD)
        self.command_preview.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # Add copy button
        copy_button = ttk.Button(footer_frame, text="Copy", command=self.copy_command)
        copy_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add save config button
        save_button = ttk.Button(footer_frame, text="Save Config", command=self.save_config)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Add execute button
        execute_button = ttk.Button(footer_frame, text="EXECUTE SCAN", style='Execute.TButton', command=self.run_scan)
        execute_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Add a separator above the footer
        separator = ttk.Separator(self.main_container, orient='horizontal')
        separator.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
    
    def create_tabs(self):
        """Create tabs with lazy loading"""
        # Create all tab frames first
        self.tab_frames = {}
        
        # Define tab order
        self.tab_order = [
            "Targets", "Scan Type", "Port Options", "Timing",
            "Scripts", "Evasion", "Output", "Results", "Analysis",
            "History", "Expert Commands"
        ]
        
        # Create frames in order
        for title in self.tab_order:
            frame = ttk.Frame(self.notebook, style='Tab.TFrame')
            self.notebook.add(frame, text=title)
            self.tab_frames[title] = frame
        
        # Store creator functions
        self.tab_creators = {
            "Targets": self.create_target_tab,
            "Scan Type": self.create_scan_type_tab,
            "Port Options": self.create_port_options_tab,
            "Timing": self.create_timing_tab,
            "Scripts": self.create_script_tab,
            "Evasion": self.create_evasion_tab,
            "Output": self.create_output_tab,
            "Results": self.create_results_tab,
            "Analysis": self.create_analysis_tab,
            "History": self.create_history_tab,
            "Expert Commands": self.create_expert_commands_tab
        }
        
        # Initialize first two tabs
        for title in ["Targets", "Scan Type"]:
            self.tab_creators[title](self.tab_frames[title])
        
        # Setup lazy loading
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        """Lazy load tabs when selected"""
        current_tab = self.notebook.select()
        tab_text = self.notebook.tab(current_tab, "text")
        
        # Check if tab needs to be created
        if tab_text in self.tab_creators:
            frame = self.tab_frames[tab_text]
            if not frame.winfo_children():
                self.tab_creators[tab_text](frame)

    def create_target_tab(self, frame):
        """Create the target specification tab"""
        # Target Input section
        target_input_frame = ttk.LabelFrame(frame, text="Target Specification", style='TLabelframe')
        target_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Single target
        single_target_label = ttk.Label(target_input_frame, text="Target (IP, hostname, CIDR):")
        single_target_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.target_entry = ttk.Entry(target_input_frame, width=40)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Configure column weights
        target_input_frame.columnconfigure(1, weight=1)
        
        # Target file frame
        target_file_frame = ttk.Frame(target_input_frame)
        target_file_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        target_file_frame.columnconfigure(0, weight=1)
        
        target_file_label = ttk.Label(target_input_frame, text="Or target list file:")
        target_file_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.target_file_entry = ttk.Entry(target_file_frame)
        self.target_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(target_file_frame, text="Browse", command=lambda: self.browse_file(self.target_file_entry))
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Target validation
        validate_button = ttk.Button(target_input_frame, text="Validate Targets", command=self.validate_targets)
        validate_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Exclude targets
        exclude_label = ttk.Label(target_input_frame, text="Exclude targets:")
        exclude_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.exclude_entry = ttk.Entry(target_input_frame, width=40)
        self.exclude_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Target options
        target_options_frame = ttk.LabelFrame(target_input_frame, text="Target Options", style='TLabelframe')
        target_options_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        target_options_frame.columnconfigure(1, weight=1)
        
        # Random targets option
        self.random_targets_var = tk.BooleanVar()
        random_targets_check = ttk.Checkbutton(target_options_frame, text="Scan targets in random order", variable=self.random_targets_var, command=self.update_command_preview)
        random_targets_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Number of random targets
        random_count_label = ttk.Label(target_options_frame, text="Number of random hosts:")
        random_count_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.random_count_entry = ttk.Entry(target_options_frame, width=10)
        self.random_count_entry.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # DNS Resolution options
        dns_frame = ttk.LabelFrame(target_input_frame, text="DNS Resolution", style='TLabelframe')
        dns_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)
        dns_frame.columnconfigure(1, weight=1)
        
        self.dns_resolution_var = tk.StringVar(value="default")
        dns_default = ttk.Radiobutton(dns_frame, text="Default DNS resolution", variable=self.dns_resolution_var, value="default", command=self.update_command_preview)
        dns_default.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        dns_always = ttk.Radiobutton(dns_frame, text="Always do DNS resolution (-n never)", variable=self.dns_resolution_var, value="always", command=self.update_command_preview)
        dns_always.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        dns_never = ttk.Radiobutton(dns_frame, text="Never do DNS resolution (-n)", variable=self.dns_resolution_var, value="never", command=self.update_command_preview)
        dns_never.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # DNS Servers
        dns_server_label = ttk.Label(dns_frame, text="Specify DNS server(s):")
        dns_server_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.dns_server_entry = ttk.Entry(dns_frame, width=30)
        self.dns_server_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Update preview on any change
        self.target_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        self.target_file_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        self.exclude_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        self.random_count_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        self.dns_server_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
    
    def create_scan_type_tab(self, frame):
        """Create the scan type tab"""
        # Scan techniques section
        techniques_frame = ttk.LabelFrame(frame, text="Scan Techniques", style='TLabelframe')
        techniques_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scan techniques
        self.scan_type_var = tk.StringVar(value="normal")
        
        scan_normal = ttk.Radiobutton(techniques_frame, text="Normal Scan (default)", variable=self.scan_type_var, value="normal", command=self.update_command_preview)
        scan_normal.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_syn = ttk.Radiobutton(techniques_frame, text="SYN Scan (-sS)", variable=self.scan_type_var, value="syn", command=self.update_command_preview)
        scan_syn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_connect = ttk.Radiobutton(techniques_frame, text="Connect Scan (-sT)", variable=self.scan_type_var, value="connect", command=self.update_command_preview)
        scan_connect.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_ack = ttk.Radiobutton(techniques_frame, text="ACK Scan (-sA)", variable=self.scan_type_var, value="ack", command=self.update_command_preview)
        scan_ack.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_window = ttk.Radiobutton(techniques_frame, text="Window Scan (-sW)", variable=self.scan_type_var, value="window", command=self.update_command_preview)
        scan_window.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_maimon = ttk.Radiobutton(techniques_frame, text="Maimon Scan (-sM)", variable=self.scan_type_var, value="maimon", command=self.update_command_preview)
        scan_maimon.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_null = ttk.Radiobutton(techniques_frame, text="NULL Scan (-sN)", variable=self.scan_type_var, value="null", command=self.update_command_preview)
        scan_null.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_fin = ttk.Radiobutton(techniques_frame, text="FIN Scan (-sF)", variable=self.scan_type_var, value="fin", command=self.update_command_preview)
        scan_fin.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_xmas = ttk.Radiobutton(techniques_frame, text="Xmas Scan (-sX)", variable=self.scan_type_var, value="xmas", command=self.update_command_preview)
        scan_xmas.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_udp = ttk.Radiobutton(techniques_frame, text="UDP Scan (-sU)", variable=self.scan_type_var, value="udp", command=self.update_command_preview)
        scan_udp.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_sctp_init = ttk.Radiobutton(techniques_frame, text="SCTP INIT Scan (-sY)", variable=self.scan_type_var, value="sctp_init", command=self.update_command_preview)
        scan_sctp_init.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        
        scan_sctp_cookie = ttk.Radiobutton(techniques_frame, text="SCTP COOKIE ECHO Scan (-sZ)", variable=self.scan_type_var, value="sctp_cookie", command=self.update_command_preview)
        scan_sctp_cookie.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        scan_custom = ttk.Radiobutton(techniques_frame, text="Custom Scan Type:", variable=self.scan_type_var, value="custom", command=self.update_command_preview)
        scan_custom.grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.custom_scan_entry = ttk.Entry(techniques_frame, width=20)
        self.custom_scan_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        self.custom_scan_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        
        # Discovery options
        discovery_frame = ttk.LabelFrame(frame, text="Host Discovery", style='TLabelframe')
        discovery_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.discovery_type_var = tk.StringVar(value="default")
        discovery_default = ttk.Radiobutton(discovery_frame, text="Default Discovery", variable=self.discovery_type_var, value="default", command=self.update_command_preview)
        discovery_default.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        discovery_skip = ttk.Radiobutton(discovery_frame, text="Skip Discovery (-Pn)", variable=self.discovery_type_var, value="skip", command=self.update_command_preview)
        discovery_skip.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        discovery_ping = ttk.Radiobutton(discovery_frame, text="Ping Scan Only (-sn)", variable=self.discovery_type_var, value="ping", command=self.update_command_preview)
        discovery_ping.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        discovery_tcp_syn = ttk.Radiobutton(discovery_frame, text="TCP SYN Discovery (-PS)", variable=self.discovery_type_var, value="tcp_syn", command=self.update_command_preview)
        discovery_tcp_syn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        discovery_tcp_ack = ttk.Radiobutton(discovery_frame, text="TCP ACK Discovery (-PA)", variable=self.discovery_type_var, value="tcp_ack", command=self.update_command_preview)
        discovery_tcp_ack.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        discovery_udp = ttk.Radiobutton(discovery_frame, text="UDP Discovery (-PU)", variable=self.discovery_type_var, value="udp", command=self.update_command_preview)
        discovery_udp.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        discovery_sctp = ttk.Radiobutton(discovery_frame, text="SCTP Discovery (-PY)", variable=self.discovery_type_var, value="sctp", command=self.update_command_preview)
        discovery_sctp.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        
        discovery_icmp_echo = ttk.Radiobutton(discovery_frame, text="ICMP Echo Discovery (-PE)", variable=self.discovery_type_var, value="icmp_echo", command=self.update_command_preview)
        discovery_icmp_echo.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        discovery_icmp_timestamp = ttk.Radiobutton(discovery_frame, text="ICMP Timestamp Discovery (-PP)", variable=self.discovery_type_var, value="icmp_timestamp", command=self.update_command_preview)
        discovery_icmp_timestamp.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        
        discovery_icmp_netmask = ttk.Radiobutton(discovery_frame, text="ICMP Netmask Discovery (-PM)", variable=self.discovery_type_var, value="icmp_netmask", command=self.update_command_preview)
        discovery_icmp_netmask.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        
        discovery_custom = ttk.Radiobutton(discovery_frame, text="Custom Discovery:", variable=self.discovery_type_var, value="custom", command=self.update_command_preview)
        discovery_custom.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.custom_discovery_entry = ttk.Entry(discovery_frame, width=20)
        self.custom_discovery_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        self.custom_discovery_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        
        # Service/Version detection
        service_frame = ttk.LabelFrame(frame, text="Service/Version Detection", style='TLabelframe')
        service_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.service_detection_var = tk.BooleanVar()
        service_check = ttk.Checkbutton(service_frame, text="Enable Service Version Detection (-sV)", variable=self.service_detection_var, command=self.update_command_preview)
        service_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # Version intensity
        intensity_label = ttk.Label(service_frame, text="Version Detection Intensity (0-9):")
        intensity_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.intensity_var = tk.StringVar()
        intensity_combo = ttk.Combobox(service_frame, textvariable=self.intensity_var, width=5, values=[str(i) for i in range(10)])
        intensity_combo.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        intensity_combo.bind("<<ComboboxSelected>>", lambda e: self.update_command_preview())
        
        # OS detection
        self.os_detection_var = tk.BooleanVar()
        os_check = ttk.Checkbutton(service_frame, text="Enable OS Detection (-O)", variable=self.os_detection_var, command=self.update_command_preview)
        os_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # More aggressive OS detection
        self.aggressive_os_var = tk.BooleanVar()
        aggressive_os_check = ttk.Checkbutton(service_frame, text="More Aggressive OS Detection (--osscan-guess)", variable=self.aggressive_os_var, command=self.update_command_preview)
        aggressive_os_check.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
    
    def create_port_options_tab(self, frame):
        """Create the port options tab"""
        # Port specification
        port_spec_frame = ttk.LabelFrame(frame, text="Port Specification", style='TLabelframe')
        port_spec_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Port selection options
        self.port_type_var = tk.StringVar(value="default")
        port_default = ttk.Radiobutton(port_spec_frame, text="Default Ports", variable=self.port_type_var, value="default", command=self.update_command_preview)
        port_default.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        port_all = ttk.Radiobutton(port_spec_frame, text="All Ports (-p-)", variable=self.port_type_var, value="all", command=self.update_command_preview)
        port_all.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        port_fast = ttk.Radiobutton(port_spec_frame, text="Fast Scan (top 100 ports)", variable=self.port_type_var, value="fast", command=self.update_command_preview)
        port_fast.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        port_specific = ttk.Radiobutton(port_spec_frame, text="Specific Ports:", variable=self.port_type_var, value="specific", command=self.update_command_preview)
        port_specific.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.port_specific_entry = ttk.Entry(port_spec_frame, width=40)
        self.port_specific_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W+tk.E)
        self.port_specific_entry.bind("<KeyRelease>", lambda e: self.update_command_preview())
        
        # Common ports
        common_ports_frame = ttk.LabelFrame(port_spec_frame, text="Common Port Groups", style='TLabelframe')
        common_ports_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        
        common_web = ttk.Button(common_ports_frame, text="Web (80,443,8080,8443)", command=lambda: self.set_ports("80,443,8080,8443"))
        common_web.grid(row=0, column=0, padx=5, pady=5)
        
        common_mail = ttk.Button(common_ports_frame, text="Mail (25,110,143,465,587,993,995)", command=lambda: self.set_ports("25,110,143,465,587,993,995"))
        common_mail.grid(row=0, column=1, padx=5, pady=5)
        
        common_db = ttk.Button(common_ports_frame, text="Database (1433,1521,3306,5432,27017)", command=lambda: self.set_ports("1433,1521,3306,5432,27017"))
        common_db.grid(row=0, column=2, padx=5, pady=5)
        
        common_ftp = ttk.Button(common_ports_frame, text="FTP (20,21)", command=lambda: self.set_ports("20,21"))
        common_ftp.grid(row=1, column=0, padx=5, pady=5)
        
        common_ssh = ttk.Button(common_ports_frame, text="SSH (22)", command=lambda: self.set_ports("22"))
        common_ssh.grid(row=1, column=1, padx=5, pady=5)
        
        common_rdp = ttk.Button(common_ports_frame, text="RDP (3389)", command=lambda: self.set_ports("3389"))
        common_rdp.grid(row=1, column=2, padx=5, pady=5)
        
        # Port state options
        port_state_frame = ttk.LabelFrame(frame, text="Port State Options", style='TLabelframe')
        port_state_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Checkboxes for port states
        self.port_open_var = tk.BooleanVar(value=True)
        port_open_check = ttk.Checkbutton(port_state_frame, text="Open", variable=self.port_open_var, command=self.update_command_preview)
        port_open_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.port_closed_var = tk.BooleanVar()
        port_closed_check = ttk.Checkbutton(port_state_frame, text="Closed", variable=self.port_closed_var, command=self.update_command_preview)
        port_closed_check.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    
    def create_results_tab(self, frame):
        """Create the results/output tab"""
        # Create output display
        output_frame = ttk.LabelFrame(frame, text="Scan Output", style='TLabelframe')
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create output text widget
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            bg=self.alt_color,
            fg=self.fg_color,
            font=('Consolas', 10)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create status frame
        status_frame = ttk.Frame(output_frame)
        status_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Create status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create progress bar
        self.progress_bar = ttk.Progressbar(
            output_frame,
            mode='indeterminate',
            style='TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Create control buttons frame
        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create stop button
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Scan",
            command=self.stop_scan,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Create clear button
        clear_button = ttk.Button(
            button_frame,
            text="Clear Output",
            command=self.clear_output
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Create save button
        save_button = ttk.Button(
            button_frame,
            text="Save Output",
            command=self.save_output
        )
        save_button.pack(side=tk.LEFT, padx=5)

    def create_timing_tab(self, frame):
        """Create the timing and performance tab"""
        # Timing templates
        timing_template_frame = ttk.LabelFrame(frame, text="Timing Template", style='TLabelframe')
        timing_template_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.timing_var = tk.StringVar(value="normal")
        timings = [
            ("Paranoid (0)", "0"),
            ("Sneaky (1)", "1"),
            ("Polite (2)", "2"),
            ("Normal (3)", "3"),
            ("Aggressive (4)", "4"),
            ("Insane (5)", "5")
        ]
        
        for text, value in timings:
            ttk.Radiobutton(
                timing_template_frame,
                text=text,
                value=value,
                variable=self.timing_var,
                command=self.update_command_preview
            ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Advanced timing options
        advanced_timing_frame = ttk.LabelFrame(frame, text="Advanced Timing", style='TLabelframe')
        advanced_timing_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Host timeout
        host_timeout_frame = ttk.Frame(advanced_timing_frame)
        host_timeout_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(host_timeout_frame, text="Host Timeout (ms):").pack(side=tk.LEFT)
        self.host_timeout_var = tk.StringVar()
        ttk.Entry(host_timeout_frame, textvariable=self.host_timeout_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Min/Max RTT timeout
        rtt_frame = ttk.Frame(advanced_timing_frame)
        rtt_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(rtt_frame, text="Min RTT (ms):").pack(side=tk.LEFT)
        self.min_rtt_var = tk.StringVar()
        ttk.Entry(rtt_frame, textvariable=self.min_rtt_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(rtt_frame, text="Max RTT (ms):").pack(side=tk.LEFT, padx=5)
        self.max_rtt_var = tk.StringVar()
        ttk.Entry(rtt_frame, textvariable=self.max_rtt_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Max retries
        retries_frame = ttk.Frame(advanced_timing_frame)
        retries_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(retries_frame, text="Max Retries:").pack(side=tk.LEFT)
        self.max_retries_var = tk.StringVar()
        ttk.Entry(retries_frame, textvariable=self.max_retries_var, width=10).pack(side=tk.LEFT, padx=5)

    def create_script_tab(self, frame):
        """Create the NSE scripts tab"""
        # Script categories
        categories_frame = ttk.LabelFrame(frame, text="Script Categories", style='TLabelframe')
        categories_frame.pack(fill=tk.X, padx=10, pady=5)
        
        script_categories = [
            ("auth", "Authentication"),
            ("broadcast", "Broadcast"),
            ("brute", "Brute Force"),
            ("default", "Default"),
            ("discovery", "Discovery"),
            ("dos", "DOS"),
            ("exploit", "Exploit"),
            ("external", "External"),
            ("fuzzer", "Fuzzer"),
            ("intrusive", "Intrusive"),
            ("malware", "Malware"),
            ("safe", "Safe"),
            ("version", "Version"),
            ("vuln", "Vulnerability")
        ]
        
        self.script_vars = {}
        for category, display_name in script_categories:
            var = tk.BooleanVar()
            self.script_vars[category] = var
            ttk.Checkbutton(
                categories_frame,
                text=display_name,
                variable=var,
                command=self.update_script_selection
            ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Custom script selection
        custom_script_frame = ttk.LabelFrame(frame, text="Custom Scripts", style='TLabelframe')
        custom_script_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.script_var = tk.StringVar()
        ttk.Entry(custom_script_frame, textvariable=self.script_var, width=50).pack(padx=5, pady=5)
        ttk.Label(custom_script_frame, text="Example: http-title,ssh-auth-methods").pack(padx=5)

    def update_script_selection(self):
        """Update script selection based on category checkboxes"""
        selected_categories = []
        for category, var in self.script_vars.items():
            if var.get():
                selected_categories.append(category)
        
        if selected_categories:
            self.script_var.set(','.join(selected_categories))
        else:
            self.script_var.set('')
        
        self.update_command_preview()

    def create_evasion_tab(self, frame):
        """Create the evasion options tab"""
        # Fragmentation and decoys
        frag_frame = ttk.LabelFrame(frame, text="Fragmentation and Decoys", style='TLabelframe')
        frag_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.fragment_var = tk.BooleanVar()
        ttk.Checkbutton(
            frag_frame,
            text="Fragment Packets (-f)",
            variable=self.fragment_var,
            command=self.update_command_preview
        ).pack(anchor=tk.W, padx=5, pady=2)
        
        decoy_frame = ttk.Frame(frag_frame)
        decoy_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(decoy_frame, text="Decoy Addresses:").pack(side=tk.LEFT)
        self.decoy_var = tk.StringVar()
        ttk.Entry(decoy_frame, textvariable=self.decoy_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Data length and source port
        data_frame = ttk.LabelFrame(frame, text="Data Options", style='TLabelframe')
        data_frame.pack(fill=tk.X, padx=10, pady=5)
        
        length_frame = ttk.Frame(data_frame)
        length_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(length_frame, text="Data Length:").pack(side=tk.LEFT)
        self.data_length_var = tk.StringVar()
        ttk.Entry(length_frame, textvariable=self.data_length_var, width=10).pack(side=tk.LEFT, padx=5)
        
        port_frame = ttk.Frame(data_frame)
        port_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(port_frame, text="Source Port:").pack(side=tk.LEFT)
        self.source_port_var = tk.StringVar()
        ttk.Entry(port_frame, textvariable=self.source_port_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # IP options
        ip_frame = ttk.LabelFrame(frame, text="IP Options", style='TLabelframe')
        ip_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.spoof_mac_var = tk.StringVar()
        mac_frame = ttk.Frame(ip_frame)
        mac_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(mac_frame, text="Spoof MAC:").pack(side=tk.LEFT)
        ttk.Entry(mac_frame, textvariable=self.spoof_mac_var, width=20).pack(side=tk.LEFT, padx=5)
        
        self.ttl_var = tk.StringVar()
        ttl_frame = ttk.Frame(ip_frame)
        ttl_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(ttl_frame, text="TTL:").pack(side=tk.LEFT)
        ttk.Entry(ttl_frame, textvariable=self.ttl_var, width=10).pack(side=tk.LEFT, padx=5)

    def create_expert_commands_tab(self, frame):
        """Create the expert commands tab with organized command groups"""
        # Create main frame with grid layout
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create left panel for commands (70% width)
        commands_frame = ttk.Frame(main_frame)
        commands_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        # Create right panel for preview (30% width)
        preview_frame = ttk.LabelFrame(main_frame, text="Command Preview", style='TLabelframe')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5,0))
        
        # Add command preview text widget
        self.expert_command_preview = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            width=40,
            height=10,
            font=('Consolas', 10),
            bg=self.alt_color,
            fg=self.fg_color
        )
        self.expert_command_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add buttons under preview
        preview_buttons_frame = ttk.Frame(preview_frame)
        preview_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_preview_btn = ttk.Button(
            preview_buttons_frame,
            text="Load to Main",
            command=self.load_preview_to_main
        )
        load_preview_btn.pack(side=tk.LEFT, padx=2)
        
        copy_preview_btn = ttk.Button(
            preview_buttons_frame,
            text="Copy",
            command=lambda: self.copy_to_clipboard(self.expert_command_preview.get(1.0, tk.END).strip())
        )
        copy_preview_btn.pack(side=tk.LEFT, padx=2)
        
        clear_preview_btn = ttk.Button(
            preview_buttons_frame,
            text="Clear",
            command=lambda: self.expert_command_preview.delete(1.0, tk.END)
        )
        clear_preview_btn.pack(side=tk.LEFT, padx=2)

        # Create canvas for scrollable commands
        canvas = tk.Canvas(commands_frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(commands_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Define command groups
        scan_commands = {
            "Basic Scans": [
                ("Quick Scan", "nmap -T4 -F {target}"),
                ("Intense Scan", "nmap -T4 -A -v {target}"),
                ("Full Port Scan", "nmap -p- {target}"),
                ("UDP Scan", "nmap -sU {target}"),
                ("Version Detection", "nmap -sV {target}"),
            ],
            "Stealth Scans": [
                ("SYN Stealth", "nmap -sS {target}"),
                ("ACK Scan", "nmap -sA {target}"),
                ("Window Scan", "nmap -sW {target}"),
                ("Maimon Scan", "nmap -sM {target}"),
                ("FIN Scan", "nmap -sF {target}"),
            ],
            "Advanced Scans": [
                ("OS Detection", "nmap -O {target}"),
                ("Aggressive Scan", "nmap -A {target}"),
                ("Timing Template 5", "nmap -T5 {target}"),
                ("IPv6 Scan", "nmap -6 {target}"),
                ("Idle Scan", "nmap -sI zombie_host {target}"),
            ],
            "Script Scans": [
                ("Default Scripts", "nmap -sC {target}"),
                ("Vuln Scripts", "nmap --script vuln {target}"),
                ("Safe Scripts", "nmap --script safe {target}"),
                ("Auth Scripts", "nmap --script auth {target}"),
                ("All Scripts", "nmap --script all {target}"),
            ],
            "Special Scans": [
                ("Service Detection", "nmap -sV --version-intensity 5 {target}"),
                ("Fast Scan", "nmap -F -T4 {target}"),
                ("Ping Scan", "nmap -sn {target}"),
                ("Skip DNS", "nmap -n {target}"),
                ("Trace Route", "nmap --traceroute {target}"),
            ],
            "Advanced Options": [
                ("Max Retries", "nmap --max-retries 2 {target}"),
                ("Min Rate", "nmap --min-rate 300 {target}"),
                ("Max Rate", "nmap --max-rate 500 {target}"),
                ("Fragment", "nmap -f {target}"),
                ("Decoy Scan", "nmap -D RND:5 {target}"),
            ]
            ,
            "Custom Scans": [
                ("Custom Scan 1", "nmap -sS -sV -p- --min-rate 1000 {target}"),
                ("Custom Scan 2", "nmap -sV -sC --version-intensity 9 {target}"),
                ("Custom Scan 3", "nmap -sV --script vuln {target}"),
                ("Custom Scan 4", "nmap -sn -PE -PP -PS21,22,23,25,80,443,3306,3389 -PA80,443,3389 --traceroute {target}"),
                ("Custom Scan 5", "nmap -A --script ssl-enum-ciphers,auth,vuln {target}"),
                ("Custom Scan 6", "nmap -sS -sV --script=vulscan/vulscan.nse {target}"),
                ("Custom Scan 7", "nmap -sO -sV --script=unusual-port,auth {target}"),
                ("Custom Scan 8", "nmap -sV --version-intensity 9 --script=version,vulners {target}"),
            ]
            ,
            "Analysis Scans": [
                ("Port Distribution & Risk", "nmap -sS -sV -p- --min-rate 1000 {target}"),
                ("Service Vulnerability Map", "nmap -sV -sC --version-intensity 9 {target}"),
                ("CVE Risk Analysis", "nmap -sV --script vuln {target}"),
                ("Network Attack Surface", "nmap -sn -PE -PP -PS21,22,23,25,80,443,3306,3389 -PA80,443,3389 --traceroute {target}"),
                ("Security Posture Assessment", "nmap -A --script ssl-enum-ciphers,auth,vuln {target}"),
                ("Temporal Analysis", "nmap -sS -sV --script=vulscan/vulscan.nse {target}"),
                ("Protocol Security", "nmap -sO -sV --script=unusual-port,auth {target}"),
                ("Service Version Risk", "nmap -sV --version-intensity 9 --script=version,vulners {target}"),
            ]
            ,
        }

        # Create frames for each group
        row = 0
        col = 0
        for group_name, commands in scan_commands.items():
            group_frame = ttk.LabelFrame(scrollable_frame, text=group_name, style='Group.TLabelframe')
            group_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Add commands to group
            for i, (name, cmd) in enumerate(commands):
                btn = ttk.Button(
                    group_frame,
                    text=name,
                    command=lambda c=cmd: self.load_expert_command(c),
                    style='Command.TButton'
                )
                btn.pack(fill=tk.X, padx=5, pady=2)
                self.create_tooltip(btn, f"Load command: {cmd}")
            
            # Update grid position
            col += 1
            if col > 4:  # 3 columns layout
                col = 0
                row += 1

        # Add custom command entry at the bottom
        custom_frame = ttk.LabelFrame(scrollable_frame, text="Custom Command", style='Group.TLabelframe')
        custom_frame.grid(row=row+1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        
        self.custom_command = ttk.Entry(custom_frame, style='Command.TEntry')
        self.custom_command.pack(fill=tk.X, padx=5, pady=5, expand=True, side=tk.LEFT)
        
        load_btn = ttk.Button(
            custom_frame,
            text="Load Custom",
            command=lambda: self.load_expert_command(self.custom_command.get()),
            style='Command.TButton'
        )
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Configure styles
        style = ttk.Style()
        style.configure('Group.TLabelframe', padding=5)
        style.configure('Command.TButton', padding=3)
        style.configure('Command.TEntry', padding=3)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas scrolling
        canvas.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units")))
        canvas.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))

    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(
                tooltip,
                text=text,
                background=self.alt_color,
                foreground=self.fg_color,
                padding=5
            )
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
        
        widget.bind('<Enter>', show_tooltip)

    def load_expert_command(self, command):
        """Load expert command into preview"""
        if not command:
            return
            
        # Get current target and target file
        target = self.target_entry.get().strip()
        target_file = self.target_file_entry.get().strip()
        
        # Check if either target or target file is specified
        if not target and not target_file:
            messagebox.showwarning("Warning", "Please specify either a target or a target file")
            return
            
        # Replace target placeholder with appropriate value
        if target:
            command = command.replace("{target}", target)
        elif target_file:
            command = command.replace("{target}", f"-iL {target_file}")
        
        # Update expert command preview
        if hasattr(self, 'expert_command_preview'):
            self.expert_command_preview.delete(1.0, tk.END)
            self.expert_command_preview.insert(tk.END, command)
        elif hasattr(self, 'command_preview'):
            # Fallback to main command preview if expert preview doesn't exist
            self.command_preview.delete(1.0, tk.END)
            self.command_preview.insert(tk.END, command)

    def _run_scan_thread(self):
        """Run the scan in a separate thread with improved error handling"""
        try:
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            else:
                startupinfo = None
            
            if not self.current_command:
                self.output_queue.put("Error: No command specified\n")
                self._handle_scan_completion()
                return
            
            # Split command properly handling quotes
            cmd_parts = []
            current_part = []
            in_quotes = False
            for char in self.current_command:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part.append(char)
                elif char == ' ' and not in_quotes:
                    if current_part:
                        cmd_parts.append(''.join(current_part))
                        current_part = []
                else:
                    current_part.append(char)
            if current_part:
                cmd_parts.append(''.join(current_part))
            
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                startupinfo=startupinfo,
                text=True
            )
            
            self.current_process = process
            
            # Read output continuously
            while self.scan_running and process.poll() is None:
                if process.stdout:
                    # Read output line by line
                    line = process.stdout.readline()
                    if line:
                        self.output_queue.put(line)
                        # Small sleep to prevent CPU overuse
                        time.sleep(0.01)
            
            # Handle process termination
            if not self.scan_running:
                process.terminate()
                try:
                    process.wait(timeout=5)  # Wait up to 5 seconds for process to terminate
                except subprocess.TimeoutExpired:
                    process.kill()  # Force kill if not terminated
                self.output_queue.put("\nScan terminated by user.\n")
            else:
                return_code = process.wait()
                if return_code == 0:
                    self.output_queue.put("\nScan completed successfully.\n")
                else:
                    self.output_queue.put(f"\nScan failed with return code {return_code}\n")
            
            # Ensure cleanup happens
            self._handle_scan_completion()
            
        except Exception as e:
            self.output_queue.put(f"\nError during scan: {str(e)}\n")
            self._handle_scan_error(str(e))
        finally:
            # Ensure process is terminated if it still exists
            if hasattr(self, 'current_process') and self.current_process:
                try:
                    self.current_process.terminate()
                except:
                    pass
                self.current_process = None
            
            # Cancel animation timer
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                self.root.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            
            # Update UI
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=tk.DISABLED)
            if hasattr(self, 'progress_bar'):
                self.progress_bar.stop()
            
            # Clear queue
            if hasattr(self, 'output_queue'):
                while not self.output_queue.empty():
                    self.output_queue.get()
            
            # Update status and output
            self.update_scan_status("Scan stopped by user")
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, "\nScan stopped by user.\n")
                self.output_text.see(tk.END)
            
        

    def clear_output(self):
        """Clear the output text"""
        self.output_text.delete(1.0, tk.END)

    def save_output(self):
        """Save the output text to a file"""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.output_text.get(1.0, tk.END))

    def get_command(self):
        """Optimized command generation with caching"""
        # Validate targets first
        if not self.validate_targets():
            return None
        
        # Generate command
        command = ["nmap"]
        
        # Add target specification
        targets = []
        if self.target_entry.get().strip():
            targets.append(self.target_entry.get().strip())
        if self.target_file_entry.get().strip():
            targets.append(f"-iL {self.target_file_entry.get().strip()}")
        
        # Add exclude targets
        if self.exclude_entry.get():
            command.append(f"--exclude {self.exclude_entry.get()}")
        
        # Add random targets options
        if self.random_targets_var.get():
            command.append("--randomize-hosts")
            if self.random_count_entry.get():
                command.append(f"--max-hostgroup {self.random_count_entry.get()}")
        
        # Add DNS options
        dns_resolution = self.dns_resolution_var.get()
        if dns_resolution == "never":
            command.append("-n")
        elif dns_resolution == "always":
            command.append("-n never")
        if self.dns_server_entry.get():
            command.append(f"--dns-servers {self.dns_server_entry.get()}")
        
        # Add scan type
        scan_type = self.scan_type_var.get()
        scan_type_mapping = {
            "syn": "-sS",
            "connect": "-sT",
            "ack": "-sA",
            "window": "-sW",
            "maimon": "-sM",
            "null": "-sN",
            "fin": "-sF",
            "xmas": "-sX",
            "udp": "-sU",
            "sctp_init": "-sY",
            "sctp_cookie": "-sZ",
            "custom": self.custom_scan_entry.get()
        }
        if scan_type in scan_type_mapping and scan_type != "normal":
            command.append(scan_type_mapping[scan_type])
        
        # Add discovery options
        discovery_type = self.discovery_type_var.get()
        discovery_mapping = {
            "skip": "-Pn",
            "ping": "-sn",
            "tcp_syn": "-PS",
            "tcp_ack": "-PA",
            "udp": "-PU",
            "sctp": "-PY",
            "icmp_echo": "-PE",
            "icmp_timestamp": "-PP",
            "icmp_netmask": "-PM",
            "custom": self.custom_discovery_entry.get()
        }
        if discovery_type in discovery_mapping and discovery_type != "default":
            command.append(discovery_mapping[discovery_type])
        
        # Add port options
        port_type = self.port_type_var.get()
        if port_type == "all":
            command.append("-p-")
        elif port_type == "fast":
            command.append("--top-ports 100")
        elif port_type == "specific" and self.port_specific_entry.get():
            command.append(f"-p{self.port_specific_entry.get()}")
        
        # Add service/version detection
        if self.service_detection_var.get():
            command.append("-sV")
            if self.intensity_var.get():
                command.append(f"--version-intensity {self.intensity_var.get()}")
        
        # Add OS detection
        if self.os_detection_var.get():
            command.append("-O")
            if self.aggressive_os_var.get():
                command.append("--osscan-guess")
        
        # Add timing options if defined
        if hasattr(self, 'timing_var') and self.timing_var.get() != "normal":
            command.append(f"-T{self.timing_var.get()}")
        
        # Add script options if defined
        if hasattr(self, 'script_var') and self.script_var.get():
            command.append(f"--script={self.script_var.get()}")
        
        # Add evasion options
        if self.fragment_var.get():
            if self.mtu_var.get():
                command.append(f"--mtu {self.mtu_var.get()}")
            else:
                command.append("-f")
        
        if self.decoy_var.get():
            command.append(f"-D {self.decoy_var.get()}")
        
        if self.source_ip_var.get():
            command.append(f"-S {self.source_ip_var.get()}")
        
        if self.interface_var.get():
            command.append(f"-e {self.interface_var.get()}")
        
        if self.proxy_var.get():
            command.append(f"--proxies {self.proxy_var.get()}")
        
        if self.hex_data_var.get():
            command.append(f"--data {self.hex_data_var.get()}")
        
        if self.ascii_data_var.get():
            command.append(f"--data-string {self.ascii_data_var.get()}")
        
        if self.data_length_var.get():
            command.append(f"--data-length {self.data_length_var.get()}")
        
        if self.badsum_var.get():
            command.append("--badsum")
        
        # Add output options
        if self.normal_output_var.get() and self.normal_file_var.get():
            command.append(f"-oN {self.normal_file_var.get()}")
        
        if self.xml_output_var.get() and self.xml_file_var.get():
            command.append(f"-oX {self.xml_file_var.get()}")
        
        if self.script_output_var.get() and self.script_file_var.get():
            command.append(f"-oS {self.script_file_var.get()}")
        
        if self.grep_output_var.get() and self.grep_file_var.get():
            command.append(f"-oG {self.grep_file_var.get()}")
        
        if self.all_output_var.get() and self.all_file_var.get():
            command.append(f"-oA {self.all_file_var.get()}")
        
        # Add verbosity and debug levels
        if self.verbosity_var.get() > 0:
            command.append("-" + "v" * self.verbosity_var.get())
        
        if self.debug_var.get() > 0:
            command.append("-" + "d" * self.debug_var.get())
        
        # Add additional options
        if self.reason_var.get():
            command.append("--reason")
        
        if self.open_var.get():
            command.append("--open")
        
        if self.packet_trace_var.get():
            command.append("--packet-trace")
        
        if self.iflist_var.get():
            command.append("--iflist")
        
        if self.append_var.get():
            command.append("--append-output")
        
        if self.noninteractive_var.get():
            command.append("--noninteractive")
        
        # Add targets at the end
        if targets:
            command.extend(targets)
        
        return " ".join(command)

    def validate_targets(self):
        """Optimized target validation with caching"""
        targets = self.target_entry.get().strip()
        target_file = self.target_file_entry.get().strip()
        
        # Check if either target or target file is specified
        if not targets and not target_file:
            messagebox.showerror("Error", "Please specify either a target or a target file")
            return False
        
        # If target file is specified, validate it exists
        if target_file:
            if not os.path.exists(target_file):
                messagebox.showerror("Error", f"Target file not found: {target_file}")
                return False
            return True
        
        # Validate individual targets
        target_list = [t.strip() for t in targets.split(',') if t.strip()]
        if not target_list:
            messagebox.showerror("Error", "No valid targets specified")
            return False
        
        # Use cached results if available
        if not hasattr(self, '_target_cache'):
            self._target_cache = {}
        
        # Clean old cache entries
        if len(self._target_cache) > 1000:
            self._target_cache.clear()
        
        # Validate each target
        invalid_targets = []
        for target in target_list:
            if target in self._target_cache:
                if not self._target_cache[target]:
                    invalid_targets.append(target)
                continue
                
            is_valid = self._validate_single_target(target)
            self._target_cache[target] = is_valid
            if not is_valid:
                invalid_targets.append(target)
        
        if invalid_targets:
            messagebox.showerror("Error", f"Invalid targets found: {', '.join(invalid_targets)}")
            return False
        
        return True

    def _validate_single_target(self, target):
        """Helper for parallel target validation"""
        target = target.strip()
        try:
            ipaddress.ip_address(target)
            return True
        except ValueError:
            try:
                ipaddress.ip_network(target, strict=False)
                return True
            except ValueError:
                return bool(re.match(r'^[a-zA-Z0-9.-]+$', target))

    def set_ports(self, ports):
        """Set the port specification"""
        self.port_type_var.set("specific")
        self.port_specific_entry.delete(0, tk.END)
        self.port_specific_entry.insert(0, ports)
        self.update_command_preview()

    def update_command_preview(self, event=None):
        """Update the command preview"""
        command = self.get_command()
        if command:
            self.command_preview.delete(1.0, tk.END)
            self.command_preview.insert(tk.END, command)

    def show_info(self):
        """Show comprehensive information about the application"""
        info_text = """Advanced Nmap Scanner GUI

Version: 1.0
Author: MAS
License: MIT
Website: https://github.com/MOAHSA/ChatGPT-Projects/tree/main/project_14

Description:
This application provides a comprehensive graphical interface for the Nmap Security Scanner,
making it easier to perform network discovery and security auditing. It is designed for both
beginners and advanced users, offering a full range of Nmap's powerful features through an
intuitive interface.

Key Features:
• Multiple scan types (SYN, TCP, UDP, etc.)
• Comprehensive port scanning options
• Service and OS detection
• NSE (Nmap Scripting Engine) integration
• Advanced timing and performance controls
• Multiple output formats
• Scan history and configuration management
• Expert mode with pre-configured commands
• Modern and customizable interface

System Requirements:
• Nmap 7.80 or later
• Python 3.6+
• tkinter and ttk
• Operating System: Windows/Linux/macOS

Privacy & Security:
This application is designed with security in mind. It:
• Runs all scans locally
• Doesn't collect or transmit any data
• Saves configurations only on user request
• Follows Nmap's security best practices

Credits:
• Nmap: https://nmap.org
• Icons: Material Design Icons
• Special thanks to the Nmap development team

For bug reports and feature requests, please visit:
https://github.com/MOAHSA/ChatGPT-Projects/tree/main/project_14"""

        # Create a custom dialog for better presentation
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title("About Advanced Nmap Scanner")
        info_dialog.geometry("600x500")
        
        # Create a scrolled text widget
        info_text_widget = scrolledtext.ScrolledText(
            info_dialog,
            wrap=tk.WORD,
            width=60,
            height=25,
            bg=self.alt_color,
            fg=self.fg_color,
            font=('Consolas', 10)
        )
        info_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert the info text
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.configure(state='disabled')  # Make it read-only
        
        # Add a close button
        close_button = ttk.Button(info_dialog, text="Close", command=info_dialog.destroy)
        close_button.pack(pady=5)
        
        # Center the dialog on screen
        info_dialog.transient(self.root)
        info_dialog.grab_set()
        info_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - info_dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - info_dialog.winfo_height()) // 2
        info_dialog.geometry(f"+{x}+{y}")

    def show_help(self):
        """Show comprehensive help information in a structured format"""
        help_text = """Advanced Nmap Scanner GUI - Comprehensive Help Guide

1. Target Specification:
   - Single IP (e.g., 192.168.1.1)
   - Hostname (e.g., example.com)
   - IP Range (e.g., 192.168.1.1-10)
   - CIDR Notation (e.g., 192.168.1.0/24)
   - Target List File (-iL option)
   - Exclude specific targets (--exclude option)

2. Scan Types:
   - SYN Scan (-sS): Stealthy, default scan
   - Connect Scan (-sT): Full TCP connection
   - ACK Scan (-sA): Firewall rule detection
   - Window Scan (-sW): Exploit TCP window size
   - UDP Scan (-sU): Scan UDP ports
   - NULL, FIN, Xmas Scans: Advanced stealth scans
   - Custom scan options available

3. Port Options:
   - All Ports (-p-): Scan all 65535 ports
   - Fast Scan: Top 100 common ports
   - Specific Ports: Custom port ranges
   - Port States: Open, closed, filtered
   - Service Version Detection (-sV)
   - OS Detection (-O)

4. Timing and Performance:
   - Templates (T0-T5):
     * T0 (Paranoid): Very slow, evasive
     * T1 (Sneaky): Slow scan
     * T2 (Polite): Slows down to consume less bandwidth
     * T3 (Normal): Default timing
     * T4 (Aggressive): Faster scan
     * T5 (Insane): Very aggressive, potentially unreliable
   - Custom timing options available

5. NSE Scripts:
   - Default Scripts (-sC)
   - Vulnerability Scripts (--script vuln)
   - Authentication Scripts
   - Discovery Scripts
   - Safe Scripts
   - Custom Script Selection

6. Output Options:
   - Normal Output (-oN): Human readable
   - XML Output (-oX): Structured format
   - Grepable Output (-oG): Easy to parse
   - Script Output (-oS): Script kiddie format
   - All Formats (-oA): Save in all formats
   - Verbosity Levels (-v): Control output detail

7. Evasion Techniques:
   - Fragmentation (-f)
   - MTU Specification (--mtu)
   - Decoy Scans (-D)
   - Source IP Spoofing (-S)
   - MAC Address Spoofing
   - Custom Data Payloads

8. Expert Mode:
   - Pre-configured expert commands
   - Custom command construction
   - Command history and saving
   - Load/Save configurations

Tips:
- Use higher verbosity (-v) for detailed scan information
- Save configurations for repeated scans
- Check target validity before scanning
- Monitor scan progress in real-time
- Export results for documentation

For detailed Nmap documentation: https://nmap.org/book/man.html
For script documentation: https://nmap.org/nsedoc/
For security guidelines: https://nmap.org/book/legal-issues.html"""

        # Create a custom dialog for better presentation
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Advanced Nmap Scanner Help")
        help_dialog.geometry("800x600")
        
        # Create a scrolled text widget
        help_text_widget = scrolledtext.ScrolledText(
            help_dialog,
            wrap=tk.WORD,
            width=80,
            height=30,
            bg=self.alt_color,
            fg=self.fg_color,
            font=('Consolas', 10)
        )
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert the help text
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.configure(state='disabled')  # Make it read-only
        
        # Add a close button
        close_button = ttk.Button(help_dialog, text="Close", command=help_dialog.destroy)
        close_button.pack(pady=5)
        
        # Center the dialog on screen
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        help_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - help_dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - help_dialog.winfo_height()) // 2
        help_dialog.geometry(f"+{x}+{y}")

    def copy_command(self):
        """Copy the current command to clipboard"""
        command = self.command_preview.get(1.0, tk.END).strip()
        if command:
            self.root.clipboard_clear()
            self.root.clipboard_append(command)
            messagebox.showinfo("Success", "Command copied to clipboard")

    def save_config(self):
        """Save the current configuration"""
        config = {
            'target': self.target_entry.get(),
            'target_file': self.target_file_entry.get(),
            'exclude': self.exclude_entry.get(),
            'random_targets': self.random_targets_var.get(),
            'random_count': self.random_count_entry.get(),
            'dns_resolution': self.dns_resolution_var.get(),
            'dns_servers': self.dns_server_entry.get(),
            'scan_type': self.scan_type_var.get(),
            'custom_scan': self.custom_scan_entry.get(),
            'discovery_type': self.discovery_type_var.get(),
            'custom_discovery': self.custom_discovery_entry.get(),
            'port_type': self.port_type_var.get(),
            'specific_ports': self.port_specific_entry.get(),
            'service_detection': self.service_detection_var.get(),
            'version_intensity': self.intensity_var.get(),
            'os_detection': self.os_detection_var.get(),
            'aggressive_os': self.aggressive_os_var.get()
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Configuration"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=4)
                messagebox.showinfo("Success", "Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_configs(self):
        """Load saved configuration"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")],
                title="Load Configuration"
            )
            
            if not file_path:  # User cancelled file selection
                return
            
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Apply loaded configuration
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, config.get('target', ''))
            
            self.target_file_entry.delete(0, tk.END)
            self.target_file_entry.insert(0, config.get('target_file', ''))
            
            self.exclude_entry.delete(0, tk.END)
            self.exclude_entry.insert(0, config.get('exclude', ''))
            
            self.random_targets_var.set(config.get('random_targets', False))
            
            self.random_count_entry.delete(0, tk.END)
            self.random_count_entry.insert(0, config.get('random_count', ''))
            
            self.dns_resolution_var.set(config.get('dns_resolution', 'default'))
            
            self.dns_server_entry.delete(0, tk.END)
            self.dns_server_entry.insert(0, config.get('dns_servers', ''))
            
            self.scan_type_var.set(config.get('scan_type', 'normal'))
            
            self.custom_scan_entry.delete(0, tk.END)
            self.custom_scan_entry.insert(0, config.get('custom_scan', ''))
            
            self.discovery_type_var.set(config.get('discovery_type', 'default'))
            
            self.custom_discovery_entry.delete(0, tk.END)
            self.custom_discovery_entry.insert(0, config.get('custom_discovery', ''))
            
            self.port_type_var.set(config.get('port_type', 'default'))
            
            self.port_specific_entry.delete(0, tk.END)
            self.port_specific_entry.insert(0, config.get('specific_ports', ''))
            
            self.service_detection_var.set(config.get('service_detection', False))
            self.intensity_var.set(config.get('version_intensity', ''))
            self.os_detection_var.set(config.get('os_detection', False))
            self.aggressive_os_var.set(config.get('aggressive_os', False))
            
            self.update_command_preview()
            messagebox.showinfo("Success", "Configuration loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def create_output_tab(self, frame):
        """Create the output tab with all Nmap output options"""
        # Create main scrollable frame
        canvas = tk.Canvas(frame, bg=self.bg_color)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Output format options
        format_frame = ttk.LabelFrame(scrollable_frame, text="Output Format", style='TLabelframe')
        format_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Basic output formats with file selection
        basic_formats = [
            ("Normal Output (-oN)", self.normal_output_var, self.normal_file_var),
            ("XML Output (-oX)", self.xml_output_var, self.xml_file_var),
            ("Script Kiddie (-oS)", self.script_output_var, self.script_file_var),
            ("Grepable Output (-oG)", self.grep_output_var, self.grep_file_var),
            ("All Formats (-oA)", self.all_output_var, self.all_file_var)
        ]
        
        for text, check_var, file_var in basic_formats:
            frame = ttk.Frame(format_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            check = ttk.Checkbutton(frame, text=text, variable=check_var, command=self.update_command_preview)
            check.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame, textvariable=file_var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            entry.bind('<KeyRelease>', lambda e: self.update_command_preview())
            
            browse_btn = ttk.Button(frame, text="Browse", 
                                  command=lambda v=file_var: self.browse_output_file(v))
            browse_btn.pack(side=tk.RIGHT)
        
        # Verbosity and Debug options
        level_frame = ttk.LabelFrame(scrollable_frame, text="Verbosity and Debug Level", style='TLabelframe')
        level_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Verbosity control
        verbosity_frame = ttk.Frame(level_frame)
        verbosity_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(verbosity_frame, text="Verbosity Level (-v):").pack(side=tk.LEFT)
        verbosity_spin = ttk.Spinbox(verbosity_frame, from_=0, to=4, width=5, 
                                    textvariable=self.verbosity_var, command=self.update_command_preview)
        verbosity_spin.pack(side=tk.LEFT, padx=5)
        
        # Debug control
        debug_frame = ttk.Frame(level_frame)
        debug_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(debug_frame, text="Debug Level (-d):").pack(side=tk.LEFT)
        debug_spin = ttk.Spinbox(debug_frame, from_=0, to=4, width=5, 
                                textvariable=self.debug_var, command=self.update_command_preview)
        debug_spin.pack(side=tk.LEFT, padx=5)
        
        # Additional options frame
        options_frame = ttk.LabelFrame(scrollable_frame, text="Additional Options", style='TLabelframe')
        options_frame.pack(fill=tk.X, padx=8, pady=4)
        
        # Additional options with tooltips
        options = [
            ("Show reason for port states (--reason)", self.reason_var),
            ("Only show open ports (--open)", self.open_var),
            ("Show all packets (--packet-trace)", self.packet_trace_var),
            ("Print interfaces and routes (--iflist)", self.iflist_var),
            ("Append to output files (--append-output)", self.append_var),
            ("Non-interactive mode (--noninteractive)", self.noninteractive_var)
        ]
        
        for text, var in options:
            check = ttk.Checkbutton(options_frame, text=text, variable=var, 
                                   command=self.update_command_preview)
            check.pack(anchor=tk.W, padx=5, pady=2)
            self.create_tooltip(check, text.split('(')[1].rstrip(')'))

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

    def browse_output_file(self, var):
        """Browse for output file location"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("XML files", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            var.set(file_path)

    def create_history_tab(self, frame):
        """Create the scan history tab"""
        # Create history list first
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_list = tk.Listbox(
            list_frame,
            bg=self.alt_color,
            fg=self.fg_color,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 9),
            relief="flat",
            borderwidth=0,
            selectbackground=self.accent_color,
            selectforeground=self.fg_color,
            activestyle='none'
        )
        self.history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_list.yview)
        
        # Bind double-click to load scan
        self.history_list.bind('<Double-Button-1>', self.load_scan_from_history)
        
        # Create toolbar after history list
        toolbar = ttk.Frame(frame, style='Header.TFrame')
        toolbar.pack(fill=tk.X, padx=8, pady=4)
        
        ttk.Button(
            toolbar,
            text="Clear History",
            command=self.clear_history
        ).pack(side=tk.LEFT, padx=4)
        
        ttk.Button(
            toolbar,
            text="Export History",
            command=self.export_history
        ).pack(side=tk.LEFT, padx=4)

    def clear_history(self):
        """Clear the scan history"""
        if self.history_list:
            self.history_list.delete(0, tk.END)

    def export_history(self):
        """Export scan history to file"""
        if not self.history_list:
            messagebox.showerror("Error", "No history to export")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, 'w') as f:
                for i in range(self.history_list.size()):
                    f.write(self.history_list.get(i) + '\n')

    def load_scan_from_history(self, event):
        """Load selected scan from history"""
        if not self.history_list:
            return
        
        selection = self.history_list.curselection()
        if selection:
            scan = self.history_list.get(selection[0])
            self.command_preview.delete(1.0, tk.END)
            self.command_preview.insert(tk.END, scan)

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)

    def change_theme(self):
        """Change the application theme"""
        try:
            # Get selected theme
            new_theme = self.theme_var.get()
            
            # Apply the theme
            self.style.theme_use(new_theme)
            
            # Update theme colors based on theme
            if new_theme in ['equilux', 'black']:
                # Dark theme colors
                self.bg_color = "#2d2d2d"
                self.fg_color = "#ffffff"
                self.accent_color = "#007acc"
                self.alt_color = "#363636"
            elif new_theme in ['breeze', 'arc']:
                # Modern light theme colors
                self.bg_color = "#f5f5f5"
                self.fg_color = "#2c2c2c"
                self.accent_color = "#3daee9"
                self.alt_color = "#ffffff"
            else:
                # Default theme colors
                self.bg_color = "#e8e8e8"
                self.fg_color = "#2c2c2c"
                self.accent_color = "#2b5797"
                self.alt_color = "#ffffff"
            
            # Common colors
            self.success_color = "#1e7145"
            self.warning_color = "#fa6800"
            self.error_color = "#ce352c"
            self.border_color = "#c0c0c0"
            self.hover_color = "#3670b9"
            
            # Reconfigure styles with new colors
            self.configure_styles()
            
            # Update existing widgets
            self.update_widget_colors()
            
            # Save theme preference
            self.save_theme_preference()
            
        except Exception as e:
            messagebox.showerror("Theme Error", f"Failed to change theme: {str(e)}")
            # Revert to default theme
            self.theme_var.set("plastik")
            self.style.theme_use("plastik")

    def update_widget_colors(self):
        """Update colors of existing widgets"""
        # Update text widgets
        if hasattr(self, 'output_text'):
            self.output_text.configure(
                bg=self.alt_color,
                fg=self.fg_color
            )
        
        # Update listbox
        if hasattr(self, 'history_list') and self.history_list:
            self.history_list.config(
                bg=self.alt_color,
                fg=self.fg_color,
                selectbackground=self.accent_color
            )
        
        # Update command preview
        if hasattr(self, 'command_preview'):
            self.command_preview.configure(
                bg=self.alt_color,
                fg=self.fg_color
            )

    def save_theme_preference(self):
        """Save theme preference to config file"""
        try:
            config = {
                'theme': self.theme_var.get()
            }
            with open('theme_config.json', 'w') as f:
                json.dump(config, f)
        except:
            pass  # Silently fail if can't save theme preference

    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            with open('theme_config.json', 'r') as f:
                config = json.load(f)
                if 'theme' in config:
                    self.theme_var.set(config['theme'])
                    self.change_theme()
        except:
            pass  # Use default theme if can't load preference

    def browse_file(self, entry):
        """Open a file dialog to select a target file"""
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def update_scan_status(self, status):
        """Update the scan status label with enhanced animation"""
        if not hasattr(self, 'status_label'):
            return
        
        # Always update the status text first
        self.status_label.config(text=status)
        
        # Handle animation
        if self.scan_running and hasattr(self, 'animation_running') and self.animation_running:
            # Start progress bar if not already started
            if hasattr(self, 'progress_bar'):
                try:
                    self.progress_bar.start(10)
                except:
                    pass
                
            # Update animation with more visible characters
            chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]  # Braille pattern animation
            char = chars[self.animation_index % len(chars)]
            self.animation_index = (self.animation_index + 1) % len(chars)
            
            # Format status with animation and elapsed time
            elapsed = time.time() - self.scan_start_time if hasattr(self, 'scan_start_time') else 0
            elapsed_str = f"{int(elapsed)}s"
            status_text = f"{char} {status} ({elapsed_str})"
            
            self.status_label.config(text=status_text)
            
            # Schedule next animation frame
            if hasattr(self, 'root'):
                if self.animation_after_id:
                    try:
                        self.root.after_cancel(self.animation_after_id)
                    except:
                        pass
                self.animation_after_id = self.root.after(100, 
                    lambda: self.update_scan_status(status))
        else:
            # Stop animation and progress bar
            if hasattr(self, 'progress_bar'):
                try:
                    self.progress_bar.stop()
                except:
                    pass
                
            # Cancel any pending animation
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                if hasattr(self, 'root'):
                    try:
                        self.root.after_cancel(self.animation_after_id)
                    except:
                        pass
                self.animation_after_id = None
            
            # Update stop button state
            if hasattr(self, 'stop_button'):
                try:
                    self.stop_button.config(state=tk.DISABLED)
                except:
                    pass

    def run_scan(self):
        """Start a new scan with proper status handling"""
        if self.scan_running:
            messagebox.showwarning("Scan in Progress", "A scan is already running")
            return
            
        command = self.get_command()
        if not command:
            return
    
        try:
            # Initialize scan state
            self.scan_running = True
            self.scan_completed = False
            self.scan_error = False
            self.current_command = command
            self.scan_start_time = time.time()
            
            # Initialize output queue if not exists
            if not hasattr(self, 'output_queue'):
                self.output_queue = queue.Queue()
            
            # Switch to results tab
            self.notebook.select(self.notebook.index('end') - 4)
            
            # Clear previous output
            self.clear_output()
            self.output_text.insert(tk.END, f"Starting scan...\n\nCommand: {command}\n\n")
            self.output_text.see(tk.END)
            
            # Initialize animation state
            self.animation_index = 0
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                try:
                    self.root.after_cancel(self.animation_after_id)
                except:
                    pass
            self.animation_after_id = None
            self.animation_running = True
            
            # Update UI state
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=tk.NORMAL)
            if hasattr(self, 'progress_bar'):
                try:
                    self.progress_bar.stop()  # Stop any existing animation
                except:
                    pass
                try:
                    self.progress_bar.start(10)
                except:
                    pass
            
            # Update status and start animation
            self.update_scan_status("Initializing scan...")
            
            # Add to history
            if hasattr(self, 'history_list') and self.history_list is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.history_list.insert(0, f"[{timestamp}] {command}")
            
            # Start scan thread
            self.scan_thread = threading.Thread(target=self._run_scan_thread)
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            # Start output processing
            self.process_output()
            
        except Exception as e:
            self._handle_scan_error(f"Failed to start scan: {str(e)}")

    def _handle_scan_error(self, error_msg):
        """Handle scan errors with proper cleanup"""
        self.scan_running = False
        self.animation_running = False
        self.scan_error = True
        
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state=tk.DISABLED)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
            
        self.update_scan_status("Scan failed")
        
        if hasattr(self, 'output_text'):
            self.output_text.insert(tk.END, f"\nError: {error_msg}\n")
            self.output_text.see(tk.END)
            
        messagebox.showerror("Error", error_msg)

    def _handle_scan_completion(self):
        """Handle scan completion with proper cleanup"""
        self.scan_running = False
        self.animation_running = False
        self.scan_completed = True
        
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state=tk.DISABLED)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
            
        # Calculate scan duration
        duration = time.time() - self.scan_start_time
        duration_str = f"{int(duration)} seconds"
        
        # Update status
        if not self.scan_error:
            self.update_scan_status(f"Scan completed in {duration_str}")
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, f"\nScan completed in {duration_str}\n")
                self.output_text.see(tk.END)

    def load_preview_to_main(self):
        """Load the expert command preview into the main command preview"""
        if not hasattr(self, 'expert_command_preview') or not hasattr(self, 'command_preview'):
            return
            
        command = self.expert_command_preview.get(1.0, tk.END).strip()
        if not command:
            messagebox.showwarning("Warning", "No command to load")
            return
            
        # Update main command preview
        self.command_preview.delete(1.0, tk.END)
        self.command_preview.insert(tk.END, command)
        

    def copy_to_clipboard(self, text):
        """Copy text to clipboard with feedback"""
        if not text:
            messagebox.showwarning("Warning", "No text to copy")
            return
            
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Success", "Command copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

    def process_output(self):
        """Process scan output with batching and animation"""
        if hasattr(self, 'is_updating') and self.is_updating:
            return
            
        self.is_updating = True
        try:
            # Process output in batches
            batch_size = 50
            lines = []
            
            for _ in range(batch_size):
                try:
                    line = self.output_queue.get_nowait()
                    if line:
                        lines.append(line)
                except queue.Empty:
                    break
            
            if lines:
                # Update output text
                if hasattr(self, 'output_text'):
                    self.output_text.insert(tk.END, ''.join(lines))
                    self.output_text.see(tk.END)
                
                # Update status if progress info is found
                for line in lines:
                    if "Progress:" in line or "Timing:" in line:
                        self.update_scan_status(line.strip())
                        break
            
        finally:
            self.is_updating = False
            if self.scan_running and hasattr(self, 'root'):
                self.root.after(100, self.process_output)

    def stop_scan(self):
        """Stop the current scan with proper cleanup"""
        if not self.scan_running:
            return
            
        try:
            # Reset scan state
            self.scan_running = False
            self.scan_completed = False
            self.scan_error = False
            self.animation_running = False
            
            # Stop current process
            if hasattr(self, 'current_process') and self.current_process:
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=1)
                except:
                    try:
                        self.current_process.kill()
                    except:
                        pass
            
            # Update UI
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state=tk.DISABLED)
            if hasattr(self, 'progress_bar'):
                self.progress_bar.stop()
            
            self.update_scan_status("Scan stopped")
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, "\nScan stopped by user\n")
                self.output_text.see(tk.END)
            
        except Exception as e:
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, f"\nError stopping scan: {str(e)}\n")
                self.output_text.see(tk.END)

    def create_analysis_tab(self, frame):
        """Create the analysis tab with enhanced security visualizations"""
        # Create main analysis frame with proper packing
        analysis_frame = ttk.Frame(frame)
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5,45))  # Add bottom padding for footer
        
        # Create left panel for controls with enhanced options
        control_frame = ttk.LabelFrame(analysis_frame, text="Security Analysis Controls", style='TLabelframe')
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Add analysis type selector with enhanced options
        ttk.Label(control_frame, text="Analysis Type:").pack(anchor=tk.W, padx=5, pady=2)
        self.analysis_type = tk.StringVar(value="port_distribution")
        analysis_types = [
            ("Port Distribution & Risk", "port_distribution"),
            ("Service Vulnerability Map", "service_map"),
            ("CVE Risk Analysis", "vuln_overview"),
            ("Network Attack Surface", "network_topology"),
            ("Security Posture Assessment", "risk_assessment"),
            ("Temporal Analysis", "temporal_analysis"),
            ("Protocol Security", "protocol_security"),
            ("Service Version Risk", "version_risk")
        ]
        
        for text, value in analysis_types:
            ttk.Radiobutton(
                control_frame,
                text=text,
                value=value,
                variable=self.analysis_type,
                command=self.update_analysis
            ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Add filtering options
        filter_frame = ttk.LabelFrame(control_frame, text="Analysis Filters", style='TLabelframe')
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Risk level filter
        ttk.Label(filter_frame, text="Risk Level:").pack(anchor=tk.W, padx=5, pady=2)
        self.risk_level = tk.StringVar(value="all")
        for level in ["All", "Critical", "High", "Medium", "Low"]:
            ttk.Radiobutton(
                filter_frame,
                text=level,
                value=level.lower(),
                variable=self.risk_level,
                command=self.update_analysis
            ).pack(anchor=tk.W, padx=15, pady=1)
        
        # Protocol filter
        ttk.Label(filter_frame, text="Protocol:").pack(anchor=tk.W, padx=5, pady=2)
        self.protocol_filter = tk.StringVar(value="all")
        for proto in ["All", "TCP", "UDP", "ICMP"]:
            ttk.Radiobutton(
                filter_frame,
                text=proto,
                value=proto.lower(),
                variable=self.protocol_filter,
                command=self.update_analysis
            ).pack(anchor=tk.W, padx=15, pady=1)
        
        # Create right panel for visualizations
        viz_frame = ttk.LabelFrame(analysis_frame, text="Security Analysis Dashboard", style='TLabelframe')
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create top stats panel
        stats_frame = ttk.Frame(viz_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add key statistics
        self.stats_labels = {}
        stats = ["Total Hosts", "Open Ports", "Critical Vulnerabilities", "Security Score"]
        for i, stat in enumerate(stats):
            frame = ttk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, expand=True, padx=5)
            ttk.Label(frame, text=stat, style='Bold.TLabel').pack()
            self.stats_labels[stat] = ttk.Label(frame, text="0", style='Stats.TLabel')
            self.stats_labels[stat].pack()
        
        # Create matplotlib canvas with adjusted size for footer
        self.fig = Figure(figsize=(10, 5), dpi=100)  # Reduced height to accommodate footer
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create enhanced summary text widget with reduced height
        summary_frame = ttk.LabelFrame(viz_frame, text="Security Analysis Summary", style='TLabelframe')
        summary_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.analysis_summary = scrolledtext.ScrolledText(
            summary_frame,
            wrap=tk.WORD,
            height=4,  # Reduced height
            bg=self.alt_color,
            fg=self.fg_color,
            font=('Consolas', 10)
        )
        self.analysis_summary.pack(fill=tk.X, padx=5, pady=5)
        
        # Add export button
        export_frame = ttk.Frame(viz_frame)
        export_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(
            export_frame,
            text="Export Analysis Report",
            command=self._export_analysis_report
        ).pack(side=tk.RIGHT)
        
        # Find and lift the footer if it exists
        for child in self.root.winfo_children():
            if str(child).endswith('footer'):
                child.lift()
        
        # Update the analysis immediately
        self.update_analysis()

    def _export_analysis_report(self):
        """Export the current analysis as a detailed security report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                title="Export Security Analysis Report"
            )
            if not filename:
                return
                
            # Generate report content
            report = self._generate_html_report()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
                
            messagebox.showinfo("Success", "Analysis report exported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def _get_expert_scan_command(self, analysis_type):
        """Get expert scan command based on analysis type"""
        base_target = "${target}"  # Will be replaced with actual target
        commands = {
            "port_distribution": {
                "command": f"nmap -sS -sV -p- --min-rate 1000 {base_target}",
                "description": "Full TCP port scan with service version detection"
            },
            "service_map": {
                "command": f"nmap -sV -sC --version-intensity 9 {base_target}",
                "description": "Intensive service version and script scanning"
            },
            "vuln_overview": {
                "command": f"nmap -sV --script vuln {base_target}",
                "description": "Vulnerability detection scan using NSE scripts"
            },
            "network_topology": {
                "command": f"nmap -sn -PE -PP -PS21,22,23,25,80,443,3306,3389 -PA80,443,3389 --traceroute {base_target}",
                "description": "Network topology mapping with traceroute"
            },
            "risk_assessment": {
                "command": f"nmap -A --script ssl-enum-ciphers,auth,vuln {base_target}",
                "description": "Aggressive scan with authentication and vulnerability checks"
            },
            "temporal_analysis": {
                "command": f"nmap -sS -sV --script=vulscan/vulscan.nse {base_target}",
                "description": "Temporal vulnerability scanning with version detection"
            },
            "protocol_security": {
                "command": f"nmap -sO -sV --script=unusual-port,auth {base_target}",
                "description": "Protocol-level security analysis"
            },
            "version_risk": {
                "command": f"nmap -sV --version-intensity 9 --script=version,vulners {base_target}",
                "description": "Deep version scanning with vulnerability correlation"
            }
        }
        return commands.get(analysis_type, {"command": "", "description": "No specific scan available"})

    def _update_analysis_summary(self, analysis_type):
        """Update the analysis summary text with expert recommendations"""
        if not hasattr(self, 'analysis_summary'):
            return
            
        # Clear previous summary
        self.analysis_summary.delete(1.0, tk.END)
        
        # Get expert scan recommendation
        expert_scan = self._get_expert_scan_command(analysis_type)
        
        # Initialize summary text
        summary = "No analysis summary available"
        
        if analysis_type == "port_distribution":
            summary = "Port Distribution Analysis:\n"
            summary += "• Shows distribution of open ports across the network\n"
            summary += "• Color-coded by risk level (red=high, yellow=standard, blue=low)\n"
            summary += "• Services running on each port are displayed\n"
            summary += "• High-risk ports (21,23,445,3389,5900) require immediate attention\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Consider using --reason flag for port state reasoning"
            
        elif analysis_type == "service_map":
            summary = "Service Vulnerability Map:\n"
            summary += "• Maps services to their potential vulnerabilities\n"
            summary += "• Size indicates frequency of service occurrence\n"
            summary += "• Color intensity represents vulnerability severity\n"
            summary += "• Focus on red/large nodes for priority remediation\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Use --script-args=safe=1 for non-intrusive scans"
            
        elif analysis_type == "vuln_overview":
            summary = "Vulnerability Overview:\n"
            summary += "• Summarizes detected vulnerabilities\n"
            summary += "• Categorizes by severity and type\n"
            summary += "• Highlights critical security issues\n"
            summary += "• Provides remediation priorities\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Add --script-args vulns.showall for complete results"
            
        elif analysis_type == "network_topology":
            summary = "Network Attack Surface:\n"
            summary += "• Visualizes network connectivity and exposure\n"
            summary += "• Node size indicates number of open ports\n"
            summary += "• Edge thickness shows connection strength\n"
            summary += "• Identifies potential attack vectors\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Use --max-retries 2 for faster topology mapping"
            
        elif analysis_type == "risk_assessment":
            summary = "Security Risk Assessment:\n"
            summary += "• Comprehensive security posture evaluation\n"
            summary += "• Risk scoring based on multiple factors\n"
            summary += "• Identifies critical security gaps\n"
            summary += "• Helps prioritize security measures\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Add --script-args=unsafe=1 for thorough testing"
            
        elif analysis_type == "temporal_analysis":
            summary = "Temporal Security Analysis:\n"
            summary += "• Shows security event timeline\n"
            summary += "• Tracks changes in system state\n"
            summary += "• Helps identify patterns and anomalies\n"
            summary += "• Useful for threat hunting and monitoring\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Schedule regular scans with cron/task scheduler"
            
        elif analysis_type == "protocol_security":
            summary = "Protocol Security Analysis:\n"
            summary += "• Analyzes security by protocol type\n"
            summary += "• Shows distribution of port states\n"
            summary += "• Highlights protocol-specific risks\n"
            summary += "• Helps identify protocol vulnerabilities\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Use -sU for UDP protocol analysis"
            
        elif analysis_type == "version_risk":
            summary = "Service Version Risk Analysis:\n"
            summary += "• Evaluates risks from service versions\n"
            summary += "• Identifies outdated/vulnerable services\n"
            summary += "• Bubble size indicates usage frequency\n"
            summary += "• Color intensity shows risk level\n\n"
            summary += "Expert Scan Recommendation:\n"
            summary += f"• {expert_scan['description']}\n"
            summary += f"• Command: {expert_scan['command']}\n"
            summary += "• Additional: Use --allports for complete version detection"
        
        self.analysis_summary.insert(tk.END, summary)

    def _generate_html_report(self):
        """Generate a detailed HTML security report with expert recommendations"""
        analysis_type = self.analysis_type.get()
        expert_scan = self._get_expert_scan_command(analysis_type)
        
        # Get current figure as base64 image
        import io
        import base64
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', dpi=100)
        img_data = base64.b64encode(buf.getvalue()).decode()
        
        # Generate HTML report
        report = f"""
        <html>
        <head>
            <title>Security Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1, h2 {{ color: #2c3e50; }}
                .stats {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .stat-box {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .visualization {{ margin: 20px 0; }}
                .summary {{ 
                    background: #f8f9fa; 
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .expert-scan {{
                    background: #e8f5e9;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #2ecc71;
                }}
                .risk-high {{ color: #e74c3c; }}
                .risk-medium {{ color: #f39c12; }}
                .risk-low {{ color: #27ae60; }}
                .command {{ 
                    background: #2c3e50; 
                    color: #fff; 
                    padding: 10px; 
                    border-radius: 3px; 
                    font-family: monospace;
                }}
            </style>
        </head>
        <body>
            <h1>Security Analysis Report</h1>
            <div class="stats">
        """
        
        # Add statistics
        for stat, label in self.stats_labels.items():
            report += f"""
                <div class="stat-box">
                    <h3>{stat}</h3>
                    <p>{label.cget("text")}</p>
                </div>
            """
        
        # Add visualization
        report += f"""
            </div>
            <div class="visualization">
                <h2>Analysis Visualization</h2>
                <img src="data:image/png;base64,{img_data}" style="max-width: 100%;">
            </div>
            <div class="summary">
                <h2>Analysis Summary</h2>
                <pre>{self.analysis_summary.get(1.0, tk.END)}</pre>
            </div>
            <div class="expert-scan">
                <h2>Expert Scan Recommendation</h2>
                <p><strong>Purpose:</strong> {expert_scan['description']}</p>
                <p><strong>Command:</strong></p>
                <div class="command">{expert_scan['command']}</div>
            </div>
            <div class="details">
                <h2>Detailed Findings</h2>
                {self._generate_detailed_findings()}
            </div>
            <div class="footer">
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return report

    def _generate_detailed_findings(self):
        """Generate detailed security findings based on the analysis"""
        if not hasattr(self, 'output_text'):
            return "<p>No scan data available</p>"
            
        output = self.output_text.get(1.0, tk.END)
        findings = []
        
        # Analyze open ports
        open_ports = []
        for line in output.split('\n'):
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'open':
                    port = parts[0]
                    service = parts[2] if len(parts) > 2 else 'unknown'
                    open_ports.append((port, service))
        
        if open_ports:
            findings.append("<h3>Open Ports and Services</h3>")
            findings.append("<ul>")
            for port, service in open_ports:
                risk_class = 'risk-high' if port.split('/')[0] in {'21', '23', '445', '3389'} else 'risk-low'
                findings.append(f'<li class="{risk_class}">{port} - {service}</li>')
            findings.append("</ul>")
        
        # Analyze vulnerabilities
        vulns = []
        current_vuln = None
        for line in output.split('\n'):
            if '|' in line and 'VULNERABLE' in line.upper():
                current_vuln = line.strip()
            elif current_vuln and line.strip().startswith('|'):
                vulns.append((current_vuln, line.strip()))
                current_vuln = None
        
        if vulns:
            findings.append("<h3>Identified Vulnerabilities</h3>")
            findings.append("<ul>")
            for vuln, details in vulns:
                findings.append(f'<li class="risk-high">{vuln}<br><small>{details}</small></li>')
            findings.append("</ul>")
        
        # Add recommendations
        findings.append("<h3>Security Recommendations</h3>")
        findings.append("<ul>")
        if any(p[0].split('/')[0] in {'21', '23', '445', '3389'} for p in open_ports):
            findings.append('<li>High-risk ports detected - Consider restricting access or using secure alternatives</li>')
        if vulns:
            findings.append('<li>Critical vulnerabilities found - Immediate patching recommended</li>')
        findings.append('<li>Regular security assessments recommended</li>')
        findings.append('<li>Implement network segmentation and access controls</li>')
        findings.append("</ul>")
        
        return '\n'.join(findings)

    def _plot_temporal_analysis(self, ax):
        """Plot temporal analysis of scan data"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No temporal data available', ha='center', va='center')
            return
            
        # Parse timestamps and events from scan output
        events = []
        current_time = None
        for line in self.output_text.get(1.0, tk.END).split('\n'):
            if 'Initiating' in line and 'at' in line:
                try:
                    current_time = datetime.strptime(line.split('at')[1].strip(), '%Y-%m-%d %H:%M %Z')
                    events.append((current_time, 'scan_start'))
                except:
                    pass
            elif current_time and ('open' in line or 'filtered' in line):
                events.append((current_time, 'port_discovery'))
        
        if events:
            # Create timeline plot
            times, event_types = zip(*events)
            y_pos = range(len(times))
            
            ax.scatter(times, y_pos, c=['#2ecc71' if e == 'scan_start' else '#3498db' for e in event_types])
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f"Event {i+1}" for i in range(len(times))])
            ax.set_title('Temporal Security Analysis')
            plt.setp(ax.get_xticklabels(), rotation=45)
        else:
            ax.text(0.5, 0.5, 'No temporal data available', ha='center', va='center')

    def _plot_protocol_security(self, ax):
        """Plot protocol security analysis"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No protocol data available', ha='center', va='center')
            return
            
        # Analyze protocols and their security implications
        protocols = {}
        for proto in ['TCP', 'UDP']:
            protocols[proto] = {
                'open': 0,
                'filtered': 0,
                'closed': 0,
                'open|filtered': 0,  # Add combined state
                'risk_score': 0
            }
        
        for line in self.output_text.get(1.0, tk.END).split('\n'):
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 2:
                    proto = 'TCP' if '/tcp' in parts[0] else 'UDP'
                    state = parts[1]
                    port = parts[0].split('/')[0]
                    
                    # Handle the state
                    if state in protocols[proto]:
                        protocols[proto][state] += 1
                    
                    # Calculate risk score based on port number and state
                    if 'open' in state:  # This covers both 'open' and 'open|filtered'
                        if port in {'21', '23', '445', '3389', '5900'}:
                            protocols[proto]['risk_score'] += 3  # High risk
                        elif port in {'80', '443', '22', '53'}:
                            protocols[proto]['risk_score'] += 1  # Standard risk
                        else:
                            protocols[proto]['risk_score'] += 2  # Medium risk
        
        if protocols:
            # Create protocol security matrix
            labels = list(protocols.keys())
            x = np.arange(len(labels))
            width = 0.15
            
            # Plot bars for each state
            ax.bar(x - width*2, [p['open'] for p in protocols.values()], width, label='Open', color='#e74c3c')
            ax.bar(x - width, [p['filtered'] for p in protocols.values()], width, label='Filtered', color='#f1c40f')
            ax.bar(x, [p['closed'] for p in protocols.values()], width, label='Closed', color='#2ecc71')
            ax.bar(x + width, [p['open|filtered'] for p in protocols.values()], width, label='Open|Filtered', color='#e67e22')
            ax.bar(x + width*2, [p['risk_score'] for p in protocols.values()], width, label='Risk Score', color='#9b59b6')
            
            ax.set_ylabel('Count')
            ax.set_title('Protocol Security Analysis')
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Add risk annotations
            for i, proto in enumerate(protocols.keys()):
                risk_score = protocols[proto]['risk_score']
                if risk_score > 5:
                    ax.annotate('High Risk', xy=(i, risk_score), xytext=(0, 10),
                               textcoords='offset points', ha='center', va='bottom',
                               bbox=dict(boxstyle='round,pad=0.5', fc='#e74c3c', alpha=0.3),
                               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        else:
            ax.text(0.5, 0.5, 'No protocol data available', ha='center', va='center')

    def _plot_version_risk(self, ax):
        """Plot service version risk analysis"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No version data available', ha='center', va='center')
            return
            
        # Analyze service versions and their risks
        services = {}
        
        for line in self.output_text.get(1.0, tk.END).split('\n'):
            if '/tcp' in line or '/udp' in line:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == 'open':
                    service = parts[2]
                    version = 'Unknown'
                    risk_level = 1
                    
                    # Extract version information
                    if len(parts) > 3:
                        version_info = ' '.join(parts[3:])
                        if 'version' in version_info.lower():
                            version = version_info
                            # Calculate risk based on version age/known vulnerabilities
                            if any(x in version_info.lower() for x in ['outdated', 'old', 'vulnerable']):
                                risk_level = 3
                            elif any(x in version_info.lower() for x in ['current', 'latest']):
                                risk_level = 1
                            else:
                                risk_level = 2
                    
                    if service not in services:
                        services[service] = {'versions': {}, 'risk_level': 0}
                    if version not in services[service]['versions']:
                        services[service]['versions'][version] = 0
                    services[service]['versions'][version] += 1
                    services[service]['risk_level'] = max(services[service]['risk_level'], risk_level)
        
        if services:
            # Create service version risk matrix
            service_names = list(services.keys())
            risk_levels = [services[s]['risk_level'] for s in service_names]
            version_counts = [len(services[s]['versions']) for s in service_names]
            
            # Calculate sizes based on total instances of each service
            sizes = [sum(services[s]['versions'].values()) * 100 for s in service_names]
            
            # Create bubble chart
            scatter = ax.scatter(risk_levels, version_counts, s=sizes, c=risk_levels, cmap='RdYlGn_r', alpha=0.6)
            
            ax.set_xlabel('Risk Level (1-3)')
            ax.set_ylabel('Number of Versions')
            ax.set_title('Service Version Risk Analysis')
            
            # Add service labels
            for i, service in enumerate(service_names):
                ax.annotate(service, (risk_levels[i], version_counts[i]))
            
            plt.colorbar(scatter, label='Risk Level')
        else:
            ax.text(0.5, 0.5, 'No version data available', ha='center', va='center')

    def update_analysis(self, event=None):
        """Update the analysis visualization based on selected type"""
        if not hasattr(self, 'output_text'):
            return
            
        try:
            # Clear previous plot and set up figure with proper sizing
            self.fig.clear()
            self.fig.set_size_inches(8, 6)  # Set consistent figure size
            
            # Add subplot with proper spacing
            self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            ax = self.fig.add_subplot(111)
            
            # Get current analysis type and filters
            analysis_type = self.analysis_type.get()
            risk_level = self.risk_level.get()
            protocol = self.protocol_filter.get()
            
            # Update statistics first
            self._update_statistics()
            
            # Dictionary mapping analysis types to their plotting functions
            plot_functions = {
                "port_distribution": self._plot_port_distribution,
                "service_map": self._plot_service_map,
                "vuln_overview": self._plot_vulnerability_overview,
                "network_topology": self._plot_network_topology,
                "risk_assessment": self._plot_risk_assessment,
                "temporal_analysis": self._plot_temporal_analysis,
                "protocol_security": self._plot_protocol_security,
                "version_risk": self._plot_version_risk
            }
            
            # Get the appropriate plotting function
            plot_func = plot_functions.get(analysis_type)
            if plot_func:
                # Call the plotting function
                plot_func(ax)
                
                # Handle layout based on plot type
                if analysis_type in ["network_topology", "service_map"]:
                    # These plots need more space for labels
                    self.fig.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.05)
                elif analysis_type in ["risk_assessment"]:
                    # Radar plot needs square aspect ratio
                    self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                    ax.set_aspect('equal')
                elif analysis_type in ["vuln_overview"]:
                    # Pie chart needs square aspect ratio and legend space
                    self.fig.subplots_adjust(left=0.1, right=0.75, top=0.9, bottom=0.1)
                    ax.set_aspect('equal')
                else:
                    # Standard plots
                    self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
                
                # Force redraw
                self.canvas.draw_idle()
                self.canvas.flush_events()
            else:
                # Handle unknown analysis type
                ax.text(0.5, 0.5, 'Unknown analysis type', ha='center', va='center', color='red')
                self.canvas.draw()
            
            # Update summary text
            self._update_analysis_summary(analysis_type)
            
        except Exception as e:
            # Clear the plot in case of error
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            error_msg = f'Error generating analysis:\n{str(e)}'
            ax.text(0.5, 0.5, error_msg, ha='center', va='center', color='red')
            self.canvas.draw()
            
            # Log the error
            if hasattr(self, 'output_text'):
                self.output_text.insert(tk.END, f"\nAnalysis Error: {str(e)}\n")
                self.output_text.see(tk.END)

    def _update_statistics(self):
        """Update the statistics panel with current scan data"""
        if not hasattr(self, 'output_text'):
            return
            
        output = self.output_text.get(1.0, tk.END)
        
        # Count total hosts
        host_count = len([line for line in output.split('\n') if 'Nmap scan report for' in line])
        self.stats_labels["Total Hosts"].config(text=str(host_count))
        
        # Count open ports
        open_ports = len([line for line in output.split('\n') 
                         if ('/tcp' in line or '/udp' in line) and 'open' in line])
        self.stats_labels["Open Ports"].config(text=str(open_ports))
        
        # Count critical vulnerabilities
        vuln_count = len([line for line in output.split('\n') 
                         if '|' in line and 'VULNERABLE' in line.upper()])
        self.stats_labels["Critical Vulnerabilities"].config(text=str(vuln_count))
        
        # Calculate security score (0-100)
        max_score = 100
        deductions = 0
        
        # Deduct for open high-risk ports
        high_risk_ports = {'21', '23', '445', '3389', '5900'}
        for line in output.split('\n'):
            if any(f"{port}/" in line for port in high_risk_ports) and 'open' in line:
                deductions += 10
                
        # Deduct for vulnerabilities
        deductions += vuln_count * 15
        
        # Deduct for excessive open ports
        if open_ports > 10:
            deductions += (open_ports - 10) * 2
            
        # Calculate final score
        security_score = max(0, max_score - deductions)
        self.stats_labels["Security Score"].config(
            text=f"{security_score}",
            foreground='#27ae60' if security_score >= 80 
            else '#f39c12' if security_score >= 50 
            else '#e74c3c'
        )

    def _plot_port_distribution(self, ax):
        """Plot port distribution analysis"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No port data available', ha='center', va='center')
            return
            
        try:
            output = self.output_text.get(1.0, tk.END)
            ports = {}
            
            # Parse port information
            for line in output.split('\n'):
                if '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 2 and 'open' in parts[1]:
                        port_num = parts[0].split('/')[0]
                        protocol = 'TCP' if '/tcp' in parts[0] else 'UDP'
                        service = parts[2] if len(parts) > 2 else 'unknown'
                        
                        port_key = f"{port_num}/{protocol}"
                        if port_key not in ports:
                            ports[port_key] = {'count': 0, 'services': set()}
                        ports[port_key]['count'] += 1
                        ports[port_key]['services'].add(service)
            
            if ports:
                # Sort ports by count
                sorted_ports = sorted(ports.items(), key=lambda x: x[1]['count'], reverse=True)
                
                # Prepare data for plotting
                port_names = [p[0] for p in sorted_ports]
                counts = [p[1]['count'] for p in sorted_ports]
                
                # Create color map based on risk
                colors = []
                for port in port_names:
                    port_num = port.split('/')[0]
                    if port_num in {'21', '23', '445', '3389', '5900'}:
                        colors.append('#e74c3c')  # High risk - red
                    elif port_num in {'80', '443', '22', '53'}:
                        colors.append('#f1c40f')  # Standard - yellow
                    else:
                        colors.append('#3498db')  # Low risk - blue
                
                # Create bar plot
                bars = ax.bar(range(len(port_names)), counts, color=colors)
                
                # Customize plot
                ax.set_xticks(range(len(port_names)))
                ax.set_xticklabels(port_names, rotation=45, ha='right')
                ax.set_xlabel('Ports')
                ax.set_ylabel('Count')
                ax.set_title('Port Distribution Analysis')
                
                # Add service labels on top of bars
                for i, bar in enumerate(bars):
                    services = list(ports[port_names[i]]['services'])
                    service_text = services[0] if services else 'unknown'
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                           service_text, ha='center', va='bottom', rotation=0,
                           fontsize=8)
                
                # Add risk level legend
                from matplotlib.patches import Rectangle
                legend_elements = [
                    Rectangle((0,0),1,1, facecolor='#e74c3c', label='High Risk'),
                    Rectangle((0,0),1,1, facecolor='#f1c40f', label='Standard'),
                    Rectangle((0,0),1,1, facecolor='#3498db', label='Low Risk')
                ]
                ax.legend(handles=legend_elements, loc='upper right')
                
                # Ensure all elements are visible
                ax.margins(y=0.2)
                
            else:
                ax.text(0.5, 0.5, 'No open ports found', ha='center', va='center')
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error plotting port distribution:\n{str(e)}', 
                    ha='center', va='center', color='red')

    def _plot_service_map(self, ax):
        """Plot service relationship map"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No service data available', ha='center', va='center')
            return
            
        try:
            G = nx.Graph()
            services = {}
            
            output = self.output_text.get(1.0, tk.END)
            for line in output.split('\n'):
                if '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == 'open':
                        port = parts[0].split('/')[0]
                        service = parts[2]
                        if service not in services:
                            services[service] = []
                        services[service].append(port)
                        G.add_node(service, type='service')
                        G.add_node(port, type='port')
                        G.add_edge(service, port)
            
            if G.nodes():
                pos = nx.spring_layout(G, k=1, iterations=50)
                
                # Draw service nodes
                service_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'service']
                nx.draw_networkx_nodes(G, pos, nodelist=service_nodes, node_color='#3498db', 
                                     node_size=2000, ax=ax, alpha=0.7)
                
                # Draw port nodes
                port_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'port']
                nx.draw_networkx_nodes(G, pos, nodelist=port_nodes, node_color='#e74c3c', 
                                     node_size=1500, ax=ax, alpha=0.7)
                
                # Draw edges
                nx.draw_networkx_edges(G, pos, edge_color='#95a5a6', ax=ax, alpha=0.5)
                
                # Add labels with better visibility
                labels = nx.get_node_attributes(G, 'type')
                nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, 
                                      font_weight='bold', font_color='black')
                
                ax.set_title('Service-Port Relationship Map')
                
                # Remove axis for better visualization
                ax.set_axis_off()
                
            else:
                ax.text(0.5, 0.5, 'No service data available', ha='center', va='center')
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error plotting service map:\n{str(e)}', 
                    ha='center', va='center', color='red')

    def _plot_vulnerability_overview(self, ax):
        """Plot vulnerability analysis overview"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No vulnerability data available', ha='center', va='center')
            return
            
        try:
            output = self.output_text.get(1.0, tk.END)
            vuln_levels = {'Critical': 0, 'Warning': 0, 'Info': 0}
            
            for line in output.split('\n'):
                if 'VULNERABLE' in line.upper():
                    vuln_levels['Critical'] += 1
                elif 'WARNING' in line.upper():
                    vuln_levels['Warning'] += 1
                elif 'INFO' in line.upper():
                    vuln_levels['Info'] += 1
            
            if any(vuln_levels.values()):
                # Create pie chart with better styling
                colors = ['#e74c3c', '#f1c40f', '#3498db']
                explode = (0.1, 0.05, 0)  # Explode critical vulnerabilities
                
                wedges, texts, autotexts = ax.pie(vuln_levels.values(), 
                                                 explode=explode,
                                                 labels=vuln_levels.keys(), 
                                                 colors=colors, 
                                                 autopct='%1.1f%%',
                                                 shadow=True,
                                                 startangle=90)
                
                # Enhance text visibility
                plt.setp(autotexts, size=8, weight="bold")
                plt.setp(texts, size=10)
                
                ax.set_title('Vulnerability Distribution')
                
                # Add legend with counts
                legend_labels = [f"{k} ({v})" for k, v in vuln_levels.items()]
                ax.legend(wedges, legend_labels, title="Vulnerability Levels",
                         loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            else:
                ax.text(0.5, 0.5, 'No vulnerability data available', ha='center', va='center')
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error plotting vulnerability overview:\n{str(e)}', 
                    ha='center', va='center', color='red')

    def _plot_network_topology(self, ax):
        """Plot network topology visualization"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No topology data available', ha='center', va='center')
            return
            
        try:
            from matplotlib.lines import Line2D
            import numpy as np
            
            G = nx.Graph()
            hosts = set()
            connections = {}
            
            output = self.output_text.get(1.0, tk.END)
            current_host = None
            
            for line in output.split('\n'):
                if 'Nmap scan report for' in line:
                    current_host = line.split()[-1].strip('()')
                    hosts.add(current_host)
                    G.add_node(current_host, type='host')
                    connections[current_host] = []
                elif current_host and ('/tcp' in line or '/udp' in line) and 'open' in line:
                    port = line.split()[0].split('/')[0]
                    connections[current_host].append(port)
            
            if G.nodes():
                # Add port nodes and connections
                for host in connections:
                    for port in connections[host]:
                        port_node = f"{host}:{port}"
                        G.add_node(port_node, type='port')
                        G.add_edge(host, port_node)
                
                # Use better layout with more iterations
                pos = nx.spring_layout(G, k=2, iterations=50)
                
                # Draw host nodes with size based on number of open ports
                host_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'host']
                host_sizes = np.array([len(connections[node])*500 + 2000 for node in host_nodes])
                nx.draw_networkx_nodes(G, pos, nodelist=host_nodes, 
                                     node_color='#2ecc71', 
                                     node_size=host_sizes.tolist(), 
                                     ax=ax, alpha=0.7)
                
                # Draw port nodes with size and color based on risk
                port_nodes = [node for node, attr in G.nodes(data=True) if attr['type'] == 'port']
                port_colors = []
                port_sizes = []
                
                # Define color map for risk levels
                risk_colors = {
                    'high': '#e74c3c',
                    'standard': '#f1c40f',
                    'low': '#3498db'
                }
                
                for node in port_nodes:
                    port = node.split(':')[1]
                    if port in {'21', '23', '445', '3389', '5900'}:
                        port_colors.append(risk_colors['high'])
                        port_sizes.append(1500)
                    elif port in {'80', '443', '22', '53'}:
                        port_colors.append(risk_colors['standard'])
                        port_sizes.append(1200)
                    else:
                        port_colors.append(risk_colors['low'])
                        port_sizes.append(1000)
                
                port_sizes = np.array(port_sizes)
                port_colors = np.array(port_colors)
                
                nx.draw_networkx_nodes(G, pos, nodelist=port_nodes, 
                                     node_color=port_colors.tolist(), 
                                     node_size=port_sizes.tolist(), 
                                     ax=ax, alpha=0.7)
                
                # Draw edges with better styling
                nx.draw_networkx_edges(G, pos, edge_color='#95a5a6', 
                                     width=2, alpha=0.5, ax=ax)
                
                # Add labels with better visibility
                host_labels = {node: node for node in host_nodes}
                port_labels = {node: node.split(':')[1] for node in port_nodes}
                labels = {**host_labels, **port_labels}
                
                nx.draw_networkx_labels(G, pos, labels=labels,
                                      font_size=8, font_weight='bold',
                                      font_color='black')
                
                # Add legend
                legend_elements = [
                    Line2D([0], [0], marker='o', color='w', 
                          markerfacecolor='#2ecc71', markersize=15,
                          label='Hosts'),
                    Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=risk_colors['high'], markersize=15,
                          label='High Risk Ports'),
                    Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=risk_colors['standard'], markersize=15,
                          label='Standard Ports'),
                    Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=risk_colors['low'], markersize=15,
                          label='Low Risk Ports')
                ]
                ax.legend(handles=legend_elements, loc='upper left', 
                         bbox_to_anchor=(1, 1))
                
                ax.set_title('Network Topology Map')
                ax.set_axis_off()
            else:
                ax.text(0.5, 0.5, 'No topology data available', ha='center', va='center')
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error plotting network topology:\n{str(e)}', 
                    ha='center', va='center', color='red')

    def _plot_risk_assessment(self, ax):
        """Plot security risk assessment"""
        if not hasattr(self, 'output_text'):
            ax.text(0.5, 0.5, 'No risk assessment data available', ha='center', va='center')
            return
            
        try:
            output = self.output_text.get(1.0, tk.END)
            risk_factors = {
                'Open High-Risk Ports': 0,
                'Vulnerable Services': 0,
                'Weak Configurations': 0,
                'Missing Updates': 0,
                'Authentication Issues': 0
            }
            
            # Analyze high-risk ports
            high_risk_ports = {'21', '23', '445', '3389', '5900'}
            for line in output.split('\n'):
                if '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == 'open':
                        port = parts[0].split('/')[0]
                        if port in high_risk_ports:
                            risk_factors['Open High-Risk Ports'] += 1
            
                # Check for various security issues
                if 'VULNERABLE' in line.upper():
                    risk_factors['Vulnerable Services'] += 1
                elif 'WEAK' in line.upper() or 'DEFAULT' in line.upper():
                    risk_factors['Weak Configurations'] += 1
                elif 'OUT OF DATE' in line.upper() or 'OUTDATED' in line.upper():
                    risk_factors['Missing Updates'] += 1
                elif 'AUTH' in line.upper() or 'PASSWORD' in line.upper():
                    risk_factors['Authentication Issues'] += 1
            
            if any(risk_factors.values()):
                # Create radar chart
                categories = list(risk_factors.keys())
                values = list(risk_factors.values())
                
                # Compute angle for each axis
                angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
                angles += angles[:1]
                
                # Initialize the spider plot
                ax.clear()  # Clear any existing plot
                ax.set_theta_offset(np.pi / 2)  # Rotate to start from top
                ax.set_theta_direction(-1)  # Clock-wise
                
                # Plot data
                values += values[:1]
                ax.plot(angles, values, 'o-', linewidth=2, label='Risk Factors', color='#e74c3c')
                ax.fill(angles, values, alpha=0.25, color='#e74c3c')
                
                # Set chart properties
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, size=8)
                
                # Add value labels
                for angle, value in zip(angles[:-1], values[:-1]):
                    if value > 0:
                        ax.text(angle, value, str(value), 
                               ha='center', va='bottom')
                
                ax.set_title('Security Risk Assessment', pad=20)
                
                # Add legend
                ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            else:
                ax.text(0.5, 0.5, 'No risk assessment data available', ha='center', va='center')
                
        except Exception as e:
            ax.text(0.5, 0.5, f'Error plotting risk assessment:\n{str(e)}', 
                    ha='center', va='center', color='red')

def main():
    root = ThemedTk(theme="plastik")  # Using plastik theme
    root.title("Advanced Nmap Scanner")
    app = NmapScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    main()
