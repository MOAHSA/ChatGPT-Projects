import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, font, colorchooser
from datetime import datetime
from ttkthemes import ThemedTk
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist

class FontDialog:
    def __init__(self, parent, font_list, current_font):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Choose Font")
        dialog.geometry("300x400")
        
        # Font family
        ttk.Label(dialog, text="Font Family:").pack(pady=5)
        self.family_var = tk.StringVar(value=current_font[0])
        family_combo = ttk.Combobox(dialog, textvariable=self.family_var)
        family_combo['values'] = sorted(font_list)
        family_combo.pack(fill=tk.X, padx=5)
        
        # Font size
        ttk.Label(dialog, text="Size:").pack(pady=5)
        self.size_var = tk.IntVar(value=current_font[1])
        size_spin = ttk.Spinbox(
            dialog, 
            from_=6, 
            to=72, 
            textvariable=self.size_var,
            command=self.update_preview  # Add direct update on spin
        )
        size_spin.pack(fill=tk.X, padx=5)
        
        # Bold option
        self.bold_var = tk.BooleanVar(value=len(current_font) > 2 and 'bold' in current_font[2])
        ttk.Checkbutton(dialog, text="Bold", variable=self.bold_var).pack(pady=5)
        
        # Preview
        ttk.Label(dialog, text="Preview:").pack(pady=5)
        self.preview = tk.Text(dialog, height=3, width=30)
        self.preview.insert('1.0', "AaBbCcDd\n123456\nPreview Text")
        self.preview.pack(padx=5, pady=5)
        
        # Update preview on any change
        family_combo.bind('<<ComboboxSelected>>', self.update_preview)
        size_spin.bind('<KeyRelease>', self.update_preview)
        self.bold_var.trace('w', self.update_preview)
        
        # Initial preview
        self.update_preview()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=lambda: self.ok(dialog)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        dialog.transient(parent)
        dialog.grab_set()
        parent.wait_window(dialog)
        
    def update_preview(self, *args):
        """Update preview text with current font settings"""
        try:
            size = int(self.size_var.get())
        except:
            size = 10
            
        font_tuple = [self.family_var.get(), size]
        if self.bold_var.get():
            font_tuple.append('bold')
            
        self.preview.configure(font=tuple(font_tuple))
        
    def ok(self, dialog):
        font_tuple = [self.family_var.get(), self.size_var.get()]
        if self.bold_var.get():
            font_tuple.append('bold')
        self.result = tuple(font_tuple)
        dialog.destroy()

class ChatClient:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Chat Client")
        self.root.geometry("1000x700")
        
        # Configure colors and fonts
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#2196F3',
            'secondary': '#64B5F6',
            'success': '#4CAF50',
            'error': '#F44336',
            'warning': '#FFC107',
            'text': '#212121',
            'light_text': '#757575',
            'own_msg': '#E3F2FD',
            'other_msg': '#FFFFFF',
            'system_msg': '#F5F5F5'
        }
        
        
        self.fonts = {
            'header': ('Helvetica', 20, 'bold'),
            'subheader': ('Helvetica', 14),
            'normal': ('Helvetica', 11),
            'message': ('Helvetica', 11),
            'input': ('Helvetica', 12)
        }
        
        # Initialize client variables
        self.username = ""
        self.client_socket = None
        self.connected = False
        self.max_message_size = 1024  # Maximum message size in bytes
        
        # Default settings
        self.default_settings = {
            'theme': 'arc',
            'colors': {
                'bg': '#f0f0f0',
                'primary': '#2196F3',
                'secondary': '#64B5F6',
                'success': '#4CAF50',
                'error': '#F44336',
                'warning': '#FFC107',
                'text': '#212121',
                'light_text': '#757575',
                'own_msg': '#E3F2FD',
                'other_msg': '#FFFFFF',
                'system_msg': '#F5F5F5'
            },
            'fonts': {
                'header': ('Helvetica', 20, 'bold'),
                'subheader': ('Helvetica', 14),
                'normal': ('Helvetica', 11),
                'message': ('Helvetica', 11),
                'input': ('Helvetica', 12)
            },
            'show_timestamps': True
        }
        
        # Load saved settings or use defaults
        self.load_settings()
        
        # Apply loaded settings
        self.root.set_theme(self.settings.get('theme', self.default_settings['theme']))
        self.colors = self.settings.get('colors', self.default_settings['colors'])
        self.fonts = self.settings.get('fonts', self.default_settings['fonts'])
        
        self.create_login_frame()
        self.create_chat_frame()
        
        # Initially show only login frame
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure styles
        self.configure_styles()
        
        # Schedule initial server list refresh
        self.root.after(100, self.refresh_server_list)
        

        self.create_menu()
        
    def configure_styles(self):
        style = ttk.Style()
        
        # Configure button styles
        style.configure(
            'Primary.TButton',
            font=self.fonts['normal'],
            padding=10
        )
        
        style.configure(
            'Secondary.TButton',
            font=self.fonts['normal'],
            padding=8
        )
        
        # Configure entry styles
        style.configure(
            'Custom.TEntry',
            padding=8,
            font=self.fonts['input']
        )
        
    def create_login_frame(self):
        self.login_frame = ttk.Frame(self.root, padding="40")
        
        # Create header with logo/title
        header_frame = ttk.Frame(self.login_frame)
        header_frame.pack(pady=(0, 30))
        
        ttk.Label(
            header_frame, 
            text="Chat Client",
            font=self.fonts['header'],
            foreground=self.colors['primary']
        ).pack()
        
        # Create server browser
        server_browser = ttk.LabelFrame(self.login_frame, text="Available Servers", padding="10")
        server_browser.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Server tree view
        columns = ('name', 'host', 'port', 'status')
        self.server_tree = ttk.Treeview(server_browser, columns=columns, show='headings', height=6)
        
        # Define headings
        self.server_tree.heading('name', text='Server Name')
        self.server_tree.heading('host', text='Host')
        self.server_tree.heading('port', text='Port')
        self.server_tree.heading('status', text='Status')
        
        # Define columns
        self.server_tree.column('name', width=150)
        self.server_tree.column('host', width=120)
        self.server_tree.column('port', width=80)
        self.server_tree.column('status', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(server_browser, orient=tk.VERTICAL, command=self.server_tree.yview)
        self.server_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.server_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        ttk.Button(
            server_browser,
            text="↻ Refresh Servers",
            command=self.refresh_server_list,
            style='Secondary.TButton'
        ).pack(pady=(10, 0))
        
        # Bind double-click to connect
        self.server_tree.bind('<Double-1>', self.connect_to_selected_server)
        
        # Create manual connection frame
        connection_frame = ttk.LabelFrame(self.login_frame, text="Manual Connection", padding="10")
        connection_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server settings
        settings_frame = ttk.LabelFrame(
            connection_frame,
            text="Connection Settings",
            padding="20"
        )
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server connection options
        server_frame = ttk.LabelFrame(connection_frame, text="Server Connection", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server name/address toggle
        self.connect_mode = tk.StringVar(value="direct")
        ttk.Radiobutton(
            server_frame,
            text="Direct Connection",
            variable=self.connect_mode,
            value="direct",
            command=self.toggle_connection_mode
        ).pack(anchor=tk.W)
        
        # Add server name connection option
        ttk.Radiobutton(
            server_frame,
            text="Connect by Server Name",
            variable=self.connect_mode,
            value="name",
            command=self.toggle_connection_mode
        ).pack(anchor=tk.W)
        
        # Direct connection frame
        self.direct_frame = ttk.Frame(server_frame)
        ttk.Label(self.direct_frame, text="Server:").pack(side=tk.LEFT, padx=5)
        self.server_entry = ttk.Entry(self.direct_frame, width=30)
        self.server_entry.insert(0, "127.0.0.1")
        self.server_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.direct_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(self.direct_frame, width=6)
        self.port_entry.insert(0, "9998")
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        # Server name frame
        self.name_frame = ttk.Frame(server_frame)
        ttk.Label(self.name_frame, text="Server Name:").pack(side=tk.LEFT, padx=5)
        self.server_name_entry = ttk.Entry(self.name_frame, width=30)
        self.server_name_entry.pack(side=tk.LEFT, padx=5)
        
        # Initially show direct connection
        self.direct_frame.pack(fill=tk.X, pady=5)
        
        # Username entry
        username_frame = ttk.Frame(connection_frame)
        username_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(
            username_frame,
            text="Choose your username:",
            font=self.fonts['normal']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = ttk.Entry(
            username_frame,
            font=self.fonts['input'],
            style='Custom.TEntry'
        )
        self.username_entry.pack(fill=tk.X)
        
        # Connect button
        ttk.Button(
            connection_frame,
            text="Connect to Chat",
            command=self.connect_to_server,
            style='Primary.TButton',
            padding=(20, 10)
        ).pack(fill=tk.X)
        
    def toggle_connection_mode(self):
        if self.connect_mode.get() == "direct":
            self.name_frame.pack_forget()
            self.direct_frame.pack(fill=tk.X, pady=5)
        else:
            self.direct_frame.pack_forget()
            self.name_frame.pack(fill=tk.X, pady=5)

    def create_chat_frame(self):
        self.chat_frame = ttk.Frame(self.root, padding="10")
        
        # Header with user info and controls
        header_frame = ttk.Frame(self.chat_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User info
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.LEFT)
        
        self.user_label = ttk.Label(
            user_frame,
            font=self.fonts['subheader'],
            foreground=self.colors['primary']
        )
        self.user_label.pack(side=tk.LEFT)
        
        # Connection status
        self.status_label = ttk.Label(
            user_frame,
            text="• Connected",
            font=self.fonts['normal'],
            foreground=self.colors['success'],
            padding=(10, 0)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Disconnect button
        ttk.Button(
            header_frame,
            text="Disconnect",
            command=self.disconnect,
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT)
        
        # Add server info display
        self.server_info_label = ttk.Label(
            header_frame,
            font=self.fonts['normal'],
            foreground=self.colors['light_text'],
            padding=(10, 0)
        )
        self.server_info_label.pack(side=tk.RIGHT, padx=10)
        
        # Chat area
        chat_container = ttk.Frame(self.chat_frame)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Messages display
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=self.fonts['message'],
            background=self.colors['bg']
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure message tags with improved styling
        self.chat_display.tag_configure(
            'own_msg',
            background=self.colors['own_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20,
            spacing1=5,
            spacing3=5,
            justify='right'  # Right-align own messages
        )
        
        self.chat_display.tag_configure(
            'other_msg',
            background=self.colors['other_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20,
            spacing1=5,
            spacing3=5
        )
        
        self.chat_display.tag_configure(
            'system_msg',
            background=self.colors['system_msg'],
            foreground=self.colors['light_text'],
            justify='center',
            spacing1=8,
            spacing3=8,
            font=self.fonts['normal']
        )
        
        self.chat_display.tag_configure(
            'timestamp',
            foreground=self.colors['light_text'],
            font=('Helvetica', 9)  # Smaller font for timestamps
        )
        
        self.chat_display.tag_configure(
            'username',
            font=('Helvetica', 11, 'bold')  # Bold font for usernames
        )
        
        self.chat_display.tag_configure(
            'info_msg',
            background='#E3F2FD',
            foreground='#1976D2',
            justify='center',
            spacing1=5,
            spacing3=5
        )
        
        self.chat_display.tag_configure(
            'warning_msg',
            background='#FFF3E0',
            foreground='#F57C00',
            justify='center',
            spacing1=5,
            spacing3=5
        )
        
        self.chat_display.tag_configure(
            'success_msg',
            background='#E8F5E9',
            foreground='#388E3C',
            justify='center',
            spacing1=5,
            spacing3=5
        )
        
        self.chat_display.tag_configure(
            'error_msg',
            background='#FFEBEE',
            foreground='#D32F2F',
            justify='center',
            spacing1=5,
            spacing3=5
        )
        
        # Message input area
        input_frame = ttk.Frame(chat_container)
        input_frame.pack(fill=tk.X)
        
        self.message_entry = ttk.Entry(
            input_frame,
            font=self.fonts['input'],
            style='Custom.TEntry'
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
    def format_message(self, message, is_own=False, is_system=False):
        """Format and display message with improved styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] " if self.show_timestamps.get() else ""
        
        if is_system:
            # Handle system messages
            if "[Server Info:" in message:
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.chat_display.insert(tk.END, message + "\n", 'info_msg')
            elif "[Server Warning:" in message:
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.chat_display.insert(tk.END, message + "\n", 'warning_msg')
            elif "[Server Success:" in message:
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.chat_display.insert(tk.END, message + "\n", 'success_msg')
            elif "[Server Error:" in message:
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.chat_display.insert(tk.END, message + "\n", 'error_msg')
            else:
                # Remove any existing timestamp from system messages
                if message.startswith("[") and "]" in message:
                    _, message = message.split("]", 1)
                    message = message.strip()
                
                self.chat_display.insert(tk.END, "\n")
                self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                self.chat_display.insert(tk.END, message + "\n", 'system_msg')
        else:
            # Handle chat messages
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            
            tag = 'own_msg' if is_own else 'other_msg'
            
            if ":" in message:  # Split username and message content
                username, content = message.split(":", 1)
                self.chat_display.insert(tk.END, username + ":", 'username')
                self.chat_display.insert(tk.END, content + "\n", tag)
            else:
                self.chat_display.insert(tk.END, message + "\n", tag)
        
        self.chat_display.see(tk.END)

    def lookup_server(self, server_name):
        """Look up server details from registry"""
        registry_file = os.path.join(DATA_DIR, 'server_registry.json')
        try:
            with open(registry_file, "r") as f:
                registry = json.load(f)
                
            if server_name in registry:
                server_info = registry[server_name]
                if server_info.get("active", True):  # Default to True if not specified
                    return server_info["host"], server_info["port"]
                else:
                    raise ValueError(f"Server '{server_name}' is not active")
            
            raise ValueError(f"Server '{server_name}' not found")
        except FileNotFoundError:
            raise ValueError("No server registry found")
        except json.JSONDecodeError:
            raise ValueError("Invalid server registry format")
        except Exception as e:
            raise ValueError(f"Error looking up server: {str(e)}")

    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        try:
            if self.connect_mode.get() == "direct":
                host = self.server_entry.get().strip()
                port = int(self.port_entry.get().strip())
            else:
                server_name = self.server_name_entry.get().strip()
                if not server_name:
                    messagebox.showerror("Error", "Please enter a server name")
                    return
                try:
                    host, port = self.lookup_server(server_name)
                    self.server_name = server_name  # Store server name for display
                except ValueError as e:
                    messagebox.showerror("Server Lookup Error", str(e))
                    return
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)  # Add timeout
            
            try:
                self.client_socket.connect((host, port))
                self.client_socket.settimeout(None)  # Remove timeout after connection
            except ConnectionRefusedError:
                raise ValueError("Connection refused - server may be offline")
            except socket.timeout:
                raise ValueError("Connection timed out - server not responding")
            
            # Receive server info
            try:
                server_info = self.client_socket.recv(1024).decode()
                if server_info.startswith("SERVER_INFO:"):
                    info = json.loads(server_info[len("SERVER_INFO:"):])
                    self.server_name = info["name"]
                    # Update server info display and message size limit
                    max_users = info.get("max_users", "?")
                    current_users = info.get("current_users", "?")
                    self.max_message_size = info.get("max_message_size", 1024)  # Get limit from server
                    self.server_info_label.configure(
                        text=f"Users: {current_users}/{max_users} | Max Msg: {self.max_message_size}B"
                    )
            except:
                self.server_name = "Unknown Server"
                self.server_info_label.configure(text="Users: ?/? | Max Msg: ?B")
            
            # Send username
            self.client_socket.send(self.username.encode())
            
            # Check for immediate block/kick response
            try:
                self.client_socket.settimeout(2.0)
                response = self.client_socket.recv(1024).decode()
                self.client_socket.settimeout(None)
                
                if "You are blocked from this server" in response:
                    messagebox.showerror("Blocked", "You are blocked from joining this server")
                    self.disconnect()
                    return
            except socket.timeout:
                self.client_socket.settimeout(None)
            
            # Update UI
            self.login_frame.pack_forget()
            self.chat_frame.pack(fill=tk.BOTH, expand=True)
            self.user_label.configure(text=f"Connected to {self.server_name} as: {self.username}")
            
            # Start receiving messages
            self.connected = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {str(e)}")
            self.disconnect()

    def disconnect(self):
        """Handle client disconnection"""
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                self.connected = False
                self.client_socket.close()
            except:
                pass
            finally:
                self.client_socket = None
        
        # Reset UI regardless of connection state
        if hasattr(self, 'chat_frame'):
            self.chat_frame.pack_forget()
        if hasattr(self, 'login_frame'):
            self.login_frame.pack(fill=tk.BOTH, expand=True)
        if hasattr(self, 'chat_display'):
            self.chat_display.delete(1.0, tk.END)
        
        # Reset connection-related variables
        self.connected = False

    def send_message(self):
        if not self.connected or not self.client_socket:
            messagebox.showerror("Error", "Not connected to server")
            self.disconnect()
            return
        
        message = self.message_entry.get().strip()
        if message:
            # Check message size
            if len(message.encode()) > self.max_message_size:
                messagebox.showerror("Error", "Message exceeds maximum size limit")
                return
                
            try:
                self.client_socket.send(message.encode())
                self.format_message(f"You: {message}", is_own=True, is_system=False)
                self.message_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Error", "Could not send message")
                self.disconnect()

    def receive_messages(self):
        while self.connected and self.client_socket:
            try:
                message = self.client_socket.recv(1024).decode()
                if not message:
                    break
                
                # Handle user count updates
                if message.startswith("COUNT_UPDATE:"):
                    try:
                        count_info = json.loads(message[len("COUNT_UPDATE:"):])
                        if count_info["type"] == "user_count":
                            self.server_info_label.configure(
                                text=f"Users: {count_info['current']}/{count_info['max']}"
                            )
                        continue
                    except:
                        pass
                
                # Handle other messages
                if "Server is full" in message:
                    messagebox.showerror("Error", "Server is full, try again later")
                    self.root.after(0, self.disconnect)
                    break
                elif "You have been kicked from the server" in message:
                    self.format_message(message, is_system=True)
                    messagebox.showwarning("Kicked", "You have been kicked from the server")
                    self.root.after(0, self.disconnect)
                    break
                elif "has been blocked" in message:
                    self.format_message(message, is_system=True)
                    if f"[System: {self.username} has been blocked]" in message:
                        messagebox.showwarning("Blocked", "You have been blocked from the server")
                        self.message_entry.config(state='disabled')
                        self.message_entry.delete(0, tk.END)
                        self.message_entry.insert(0, "You are blocked from sending messages")
                        self.status_label.configure(text="• Blocked", foreground=self.colors['error'])
                elif "has been unblocked" in message:
                    self.format_message(message, is_system=True)
                    if f"[System: {self.username} has been unblocked]" in message:
                        self.message_entry.config(state='normal')
                        self.message_entry.delete(0, tk.END)
                        self.status_label.configure(text="• Connected", foreground=self.colors['success'])
                else:
                    self.format_message(message, is_own=False)
            except:
                break
        
        if self.connected:
            messagebox.showwarning("Disconnected", "Lost connection to server")
            self.root.after(0, self.disconnect)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to close the chat?"):
            self.save_settings()  # Save settings before closing
            self.disconnect()
            self.root.destroy()

    def refresh_server_list(self):
        """Refresh the server list from registry"""
        # Clear existing items
        for item in self.server_tree.get_children():
            self.server_tree.delete(item)
        
        try:
            with open(os.path.join(DATA_DIR,"server_registry.json"), "r") as f:
                registry = json.load(f)
            
            for server_name, info in registry.items():
                # Test connection to check if server is actually running
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.settimeout(1)
                    test_socket.connect((info['host'], info['port']))
                    test_socket.close()
                    status = 'Online'
                    tags = ('online',)
                except:
                    status = 'Offline'
                    tags = ('offline',)
                
                self.server_tree.insert(
                    '', 
                    'end', 
                    values=(server_name, info['host'], info['port'], status),
                    tags=tags
                )
        except:
            pass
        
        # Configure tag colors
        self.server_tree.tag_configure('online', foreground=self.colors['success'])
        self.server_tree.tag_configure('offline', foreground=self.colors['error'])

    def connect_to_selected_server(self, event):
        """Connect to the selected server from tree view"""
        selection = self.server_tree.selection()
        if not selection:
            return
        
        # Get selected server info
        server_info = self.server_tree.item(selection[0])
        if server_info['tags'][0] == 'offline':
            messagebox.showerror("Error", "Selected server is offline")
            return
        
        # Get server details
        server_name, host, port, _ = server_info['values']
        
        # Set connection details
        self.connect_mode.set("direct")
        self.server_entry.delete(0, tk.END)
        self.server_entry.insert(0, host)
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, port)
        
        # Connect if username is provided
        if self.username_entry.get().strip():
            self.connect_to_server()
        else:
            messagebox.showinfo("Info", "Please enter a username to connect")
            self.username_entry.focus()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Theme", menu=theme_menu)
        
        # Add available themes
        for theme in self.root.get_themes():
            theme_menu.add_command(
                label=theme,
                command=lambda t=theme: self.change_theme(t)
            )
        
        # Font submenu
        font_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Font", menu=font_menu)
        
        font_menu.add_command(label="Chat Font...", command=self.change_chat_font)
        font_menu.add_command(label="UI Font...", command=self.change_ui_font)
        
        # Colors submenu
        colors_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Colors", menu=colors_menu)
        
        colors_menu.add_command(label="Own Messages...", 
                              command=lambda: self.change_color('own_msg'))
        colors_menu.add_command(label="Other Messages...", 
                              command=lambda: self.change_color('other_msg'))
        colors_menu.add_command(label="System Messages...", 
                              command=lambda: self.change_color('system_msg'))
        colors_menu.add_command(label="Background...", 
                              command=lambda: self.change_color('bg'))
        colors_menu.add_command(label="Text...", 
                              command=lambda: self.change_color('text'))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        self.show_timestamps = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Show Timestamps", 
                                variable=self.show_timestamps)

    def change_theme(self, theme_name):
        try:
            self.root.set_theme(theme_name)
        except:
            messagebox.showerror("Error", f"Could not apply theme: {theme_name}")

    def change_chat_font(self):
        font_tuple = font.families()
        current_font = self.fonts['message']
        
        dialog = FontDialog(self.root, font_tuple, current_font)
        if dialog.result:
            self.fonts['message'] = dialog.result
            self.chat_display.configure(font=dialog.result)

    def change_ui_font(self):
        font_tuple = font.families()
        current_font = self.fonts['normal']
        
        dialog = FontDialog(self.root, font_tuple, current_font)
        if dialog.result:
            self.fonts['normal'] = dialog.result
            style = ttk.Style()
            style.configure('.', font=dialog.result)

    def change_color(self, color_type):
        color = colorchooser.askcolor(
            self.colors[color_type], 
            title=f"Choose {color_type} color"
        )[1]
        if color:
            self.colors[color_type] = color
            if color_type == 'bg':
                self.chat_display.configure(bg=color)
            elif color_type == 'text':
                self.chat_display.configure(fg=color)
            self.update_message_tags()
            self.save_settings()  # Save after color change

    def update_message_tags(self):
        """Update chat display message tags with current colors"""
        self.chat_display.tag_configure(
            'own_msg',
            background=self.colors['own_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20,
            spacing1=5,
            spacing3=5,
            justify='right'
        )
        
        self.chat_display.tag_configure(
            'other_msg',
            background=self.colors['other_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20,
            spacing1=5,
            spacing3=5
        )
        
        self.chat_display.tag_configure(
            'system_msg',
            background=self.colors['system_msg'],
            foreground=self.colors['light_text'],
            justify='center',
            spacing1=8,
            spacing3=8,
            font=self.fonts['normal']
        )

    def load_settings(self):
        """Load settings from file or use defaults"""
        settings_file = os.path.join(DATA_DIR, 'chat_settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
                    # Convert font tuples from lists
                    for key, value in self.settings.get('fonts', {}).items():
                        self.settings['fonts'][key] = tuple(value)
            else:
                self.settings = self.default_settings.copy()
        except:
            self.settings = self.default_settings.copy()
            
    def save_settings(self):
        """Save current settings to file"""
        settings_file = os.path.join(DATA_DIR, 'chat_settings.json')
        try:
            settings_to_save = {
                'theme': self.root.current_theme,
                'colors': self.colors,
                'fonts': {k: list(v) for k, v in self.fonts.items()},
                'show_timestamps': self.show_timestamps.get()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
        except:
            pass

if __name__ == "__main__":
    client = ChatClient()
    client.run()
