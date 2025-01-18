import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, colorchooser, font
from datetime import datetime
from ttkthemes import ThemedTk
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class ChatMonitor:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Chat Traffic Monitor")
        self.root.geometry("1000x600")
        
        # Theme and style settings
        self.colors = {
            'client': '#E3F2FD',
            'server': '#F3E5F5',
            'system': '#E8F5E9',
            'error': '#FFEBEE',
            'bg': '#FFFFFF',
            'text': '#212121'
        }
        
        self.fonts = {
            'log': ('Consolas', 10),
            'ui': ('Helvetica', 10),
            'title': ('Helvetica', 12, 'bold')
        }
        
        # Monitor settings
        self.proxy_port = 9998
        self.server_port = 9999
        self.is_running = False
        self.connections = {}
        self.usernames = {}
        
        self.create_gui()
        self.create_menu()
        
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
        
        font_menu.add_command(label="Log Font...", command=self.change_log_font)
        font_menu.add_command(label="UI Font...", command=self.change_ui_font)
        
        # Colors submenu
        colors_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Colors", menu=colors_menu)
        
        colors_menu.add_command(label="Client Messages...", 
                              command=lambda: self.change_color('client'))
        colors_menu.add_command(label="Server Messages...", 
                              command=lambda: self.change_color('server'))
        colors_menu.add_command(label="System Messages...", 
                              command=lambda: self.change_color('system'))
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
        
        self.show_directions = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Show Message Directions", 
                                variable=self.show_directions)
        
    def change_theme(self, theme_name):
        try:
            self.root.set_theme(theme_name)
        except:
            messagebox.showerror("Error", f"Could not apply theme: {theme_name}")
            
    def change_log_font(self):
        font_tuple = font.families()
        current_font = self.fonts['log']
        
        dialog = FontDialog(self.root, font_tuple, current_font)
        if dialog.result:
            self.fonts['log'] = dialog.result
            self.log.configure(font=dialog.result)
            
    def change_ui_font(self):
        font_tuple = font.families()
        current_font = self.fonts['ui']
        
        dialog = FontDialog(self.root, font_tuple, current_font)
        if dialog.result:
            self.fonts['ui'] = dialog.result
            # Update UI elements font
            style = ttk.Style()
            style.configure('.', font=dialog.result)
            
    def change_color(self, color_type):
        color = colorchooser.askcolor(self.colors[color_type], 
                                    title=f"Choose {color_type} color")[1]
        if color:
            self.colors[color_type] = color
            if color_type == 'bg':
                self.log.configure(bg=color)
            elif color_type == 'text':
                self.log.configure(fg=color)
            self.update_message_tags()
            
    def update_message_tags(self):
        self.log.tag_configure('client', background=self.colors['client'])
        self.log.tag_configure('server', background=self.colors['server'])
        self.log.tag_configure('system', background=self.colors['system'])
        self.log.tag_configure('error', background=self.colors['error'])
        
    def create_gui(self):
        # Main container
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        controls = ttk.LabelFrame(container, text="Monitor Controls", padding=5)
        controls.pack(fill=tk.X, pady=(0, 10))
        
        # Port settings
        port_frame = ttk.Frame(controls)
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(port_frame, text="Listen on port:").pack(side=tk.LEFT)
        self.proxy_port_entry = ttk.Entry(port_frame, width=6)
        self.proxy_port_entry.insert(0, "9998")
        self.proxy_port_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(port_frame, text="Forward to port:").pack(side=tk.LEFT, padx=10)
        self.server_port_entry = ttk.Entry(port_frame, width=6)
        self.server_port_entry.insert(0, "9999")
        self.server_port_entry.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        btn_frame = ttk.Frame(controls)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Monitoring", command=self.start_monitor)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop_monitor, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Traffic display
        self.log = scrolledtext.ScrolledText(container, height=20)
        self.log.pack(fill=tk.BOTH, expand=True)
        
        # Configure message tags
        self.update_message_tags()
        
        # Connected users
        users_frame = ttk.LabelFrame(container, text="Connected Users", padding=5)
        users_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.users_list = tk.Listbox(users_frame, height=5)
        self.users_list.pack(fill=tk.X)
        
    def log_message(self, message, direction=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = ""
        
        if self.show_timestamps.get():
            prefix += f"[{timestamp}] "
        if self.show_directions.get() and direction:
            prefix += f"{direction} "
            
        tag = {
            "→": "client",
            "←": "server",
            "!": "system",
            "X": "error"
        }.get(direction, "")
        
        self.log.insert(tk.END, prefix + message + "\n", tag)
        self.log.see(tk.END)
        
        # Save to log file
        try:
            log_file = os.path.join(DATA_DIR, 'proxy_log.txt')
            with open(log_file, "a") as f:
                json.dump({
                    "timestamp": timestamp,
                    "type": direction,
                    "message": message
                }, f)
                f.write("\n")
        except:
            pass
        
    def update_users(self):
        self.users_list.delete(0, tk.END)
        for username in self.usernames.values():
            self.users_list.insert(tk.END, username)
            
    def handle_client_traffic(self, client_socket, server_socket):
        while self.is_running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                message = data.decode()
                username = self.usernames.get(client_socket, "Unknown")
                self.log_message(f"{username} → Server: {message}", "→")
                
                server_socket.send(data)
            except:
                break
                
        self.close_connection(client_socket)
        
    def handle_server_traffic(self, client_socket, server_socket):
        while self.is_running:
            try:
                data = server_socket.recv(4096)
                if not data:
                    break
                    
                message = data.decode()
                username = self.usernames.get(client_socket, "Unknown")
                self.log_message(f"Server → {username}: {message}", "←")
                
                client_socket.send(data)
            except:
                break
                
        self.close_connection(client_socket)
        
    def handle_connection(self, client_socket):
        try:
            # Connect to real server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(('127.0.0.1', self.server_port))
            
            self.connections[client_socket] = server_socket
            
            # Forward initial server info
            server_info = server_socket.recv(4096)
            client_socket.send(server_info)
            
            # Get username
            username = client_socket.recv(4096).decode()
            self.usernames[client_socket] = username
            self.log_message(f"New connection: {username}", "!")
            self.root.after(0, self.update_users)
            
            # Forward username to server
            server_socket.send(username.encode())
            
            # Start traffic monitors
            threading.Thread(target=self.handle_client_traffic, 
                           args=(client_socket, server_socket),
                           daemon=True).start()
            threading.Thread(target=self.handle_server_traffic,
                           args=(client_socket, server_socket),
                           daemon=True).start()
            
        except Exception as e:
            self.log_message(f"Connection error: {e}", "X")
            self.close_connection(client_socket)
            
    def close_connection(self, client_socket):
        if client_socket in self.connections:
            server_socket = self.connections[client_socket]
            username = self.usernames.get(client_socket, "Unknown")
            
            self.log_message(f"Disconnected: {username}", "X")
            
            server_socket.close()
            client_socket.close()
            
            del self.connections[client_socket]
            if client_socket in self.usernames:
                del self.usernames[client_socket]
            
            self.root.after(0, self.update_users)
            
    def start_monitor(self):
        try:
            self.proxy_port = int(self.proxy_port_entry.get())
            self.server_port = int(self.server_port_entry.get())
            
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind(('127.0.0.1', self.proxy_port))
            self.proxy_socket.listen(5)
            
            self.is_running = True
            self.log_message(f"Monitoring started on port {self.proxy_port}", "!")
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitor: {e}")
            
    def stop_monitor(self):
        self.is_running = False
        
        for client_socket in list(self.connections.keys()):
            self.close_connection(client_socket)
            
        if hasattr(self, 'proxy_socket'):
            self.proxy_socket.close()
            
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("Monitoring stopped", "!")
        
    def accept_connections(self):
        while self.is_running:
            try:
                client_socket, _ = self.proxy_socket.accept()
                threading.Thread(target=self.handle_connection,
                              args=(client_socket,),
                              daemon=True).start()
            except:
                if self.is_running:
                    continue
                break
                
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Stop monitoring and exit?"):
            self.stop_monitor()
            self.root.destroy()

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
        size_spin = ttk.Spinbox(dialog, from_=6, to=72, textvariable=self.size_var)
        size_spin.pack(fill=tk.X, padx=5)
        
        # Bold option
        self.bold_var = tk.BooleanVar(value=len(current_font) > 2 and 'bold' in current_font[2])
        ttk.Checkbutton(dialog, text="Bold", variable=self.bold_var).pack(pady=5)
        
        # Preview
        ttk.Label(dialog, text="Preview:").pack(pady=5)
        self.preview = tk.Text(dialog, height=3, width=30)
        self.preview.insert('1.0', "AaBbCcDd\n123456")
        self.preview.pack(padx=5, pady=5)
        
        # Update preview on change
        def update_preview(*args):
            font_tuple = (self.family_var.get(), self.size_var.get())
            if self.bold_var.get():
                font_tuple += ('bold',)
            self.preview.configure(font=font_tuple)
            
        family_combo.bind('<<ComboboxSelected>>', update_preview)
        size_spin.bind('<Return>', update_preview)
        self.bold_var.trace('w', update_preview)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="OK", command=lambda: self.ok(dialog)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        dialog.transient(parent)
        dialog.grab_set()
        parent.wait_window(dialog)
        
    def ok(self, dialog):
        font_tuple = [self.family_var.get(), self.size_var.get()]
        if self.bold_var.get():
            font_tuple.append('bold')
        self.result = tuple(font_tuple)
        dialog.destroy()

if __name__ == "__main__":
    monitor = ChatMonitor()
    monitor.run()
