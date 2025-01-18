import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from datetime import datetime
from ttkthemes import ThemedTk
import json
import os 

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True) 

class ChatServerGUI:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Chat Server")
        self.root.geometry("1100x700")
        
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
            'log_bg': '#FFFFFF'
        }
        
        self.fonts = {
            'header': ('Helvetica', 16, 'bold'),
            'subheader': ('Helvetica', 12),
            'normal': ('Helvetica', 11),
            'log': ('Consolas', 10),
            'status': ('Helvetica', 10)
        }
        
        self.server = None
        self.max_users = 10  # Default max users
        self.create_widgets()
        self.configure_tags()
        
    def configure_tags(self):
        """Configure text tags for different log types"""
        self.log_display.tag_configure('timestamp', foreground='#666666')
        self.log_display.tag_configure('info', foreground=self.colors['primary'])
        self.log_display.tag_configure('success', foreground=self.colors['success'])
        self.log_display.tag_configure('error', foreground=self.colors['error'])
        self.log_display.tag_configure('warning', foreground=self.colors['warning'])
        
    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header Frame
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server controls
        controls_frame = ttk.LabelFrame(header_frame, text="Server Controls", padding="5")
        controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Start/Stop buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(
            button_frame,
            text="Start Server",
            command=self.start_server,
            style='Success.TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Stop Server",
            command=self.stop_server,
            state=tk.DISABLED,
            style='Danger.TButton'
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Server status
        self.status_label = ttk.Label(
            controls_frame,
            text="Server Status: Stopped",
            foreground=self.colors['error'],
            font=self.fonts['status'],
            padding=(20, 0)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Add server configuration to controls_frame
        config_frame = ttk.Frame(controls_frame)
        config_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(config_frame, text="Server Name:").pack(side=tk.LEFT, padx=5)
        self.server_name_entry = ttk.Entry(config_frame, width=15)
        self.server_name_entry.insert(0, "Main Server")
        self.server_name_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(config_frame, text="IP:").pack(side=tk.LEFT, padx=5)
        self.host_entry = ttk.Entry(config_frame, width=15)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(config_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(config_frame, width=6)
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        # Add max users configuration to config_frame
        ttk.Label(config_frame, text="Max Users:").pack(side=tk.LEFT, padx=5)
        self.max_users_entry = ttk.Entry(config_frame, width=4)
        self.max_users_entry.insert(0, "10")
        self.max_users_entry.pack(side=tk.LEFT, padx=5)
        
        # Add message size limit configuration
        ttk.Label(config_frame, text="Max Message Size (bytes):").pack(side=tk.LEFT, padx=5)
        self.max_message_size_entry = ttk.Entry(config_frame, width=6)
        self.max_message_size_entry.insert(0, "1024")
        self.max_message_size_entry.pack(side=tk.LEFT, padx=5)
        
        # Content area with paned window
        content = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Log display
        log_frame = ttk.Frame(content)
        content.add(log_frame, weight=3)
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(
            log_controls,
            text="Server Log",
            font=self.fonts['subheader']
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            log_controls,
            text="Clear Log",
            command=self.clear_log,
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT)
        
        ttk.Button(
            log_controls,
            text="Save Log",
            command=self.save_log,
            style='Secondary.TButton'
        ).pack(side=tk.RIGHT, padx=5)
        
        # Log display
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=self.fonts['log'],
            background=self.colors['log_bg']
        )
        self.log_display.pack(fill=tk.BOTH, expand=True)
        
        # Right side - User management
        user_frame = ttk.Frame(content)
        content.add(user_frame, weight=1)
        
        # Connected users
        connected_frame = ttk.LabelFrame(user_frame, text="Connected Users", padding="5")
        connected_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add search/filter for connected users
        self.user_filter = ttk.Entry(connected_frame)
        self.user_filter.pack(fill=tk.X, pady=(0, 5))
        self.user_filter.bind('<KeyRelease>', self.filter_users)
        
        # User listbox with scrollbar
        user_list_frame = ttk.Frame(connected_frame)
        user_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.user_listbox = tk.Listbox(
            user_list_frame,
            font=self.fonts['normal'],
            selectmode=tk.SINGLE
        )
        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        user_scrollbar = ttk.Scrollbar(user_list_frame, orient=tk.VERTICAL, command=self.user_listbox.yview)
        user_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.user_listbox.configure(yscrollcommand=user_scrollbar.set)
        
        # User controls with manual input
        user_controls = ttk.Frame(connected_frame)
        user_controls.pack(fill=tk.X, pady=(5, 0))
        
        # Manual username input
        ttk.Label(user_controls, text="Username:").pack(side=tk.LEFT, padx=(0, 5))
        self.username_entry = ttk.Entry(user_controls, width=15)
        self.username_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Action buttons frame
        action_buttons = ttk.Frame(user_controls)
        action_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            action_buttons,
            text="Block User",
            command=self.block_user,
            style='Warning.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            action_buttons,
            text="Kick User",
            command=self.kick_user,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        # Add right-click context menu
        self.user_menu = tk.Menu(self.root, tearoff=0)
        self.user_menu.add_command(label="Kick User", command=self.kick_selected_user)
        self.user_menu.add_command(label="Block User", command=self.block_selected_user)
        self.user_listbox.bind("<Button-3>", self.show_user_menu)
        
        # Blocked users
        blocked_frame = ttk.LabelFrame(user_frame, text="Blocked Users", padding="5")
        blocked_frame.pack(fill=tk.BOTH, expand=True)
        
        self.blocked_listbox = tk.Listbox(
            blocked_frame,
            font=self.fonts['normal'],
            selectmode=tk.SINGLE
        )
        self.blocked_listbox.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(
            blocked_frame,
            text="Unblock User",
            command=self.unblock_selected_user,
            style='Success.TButton'
        ).pack(pady=(5, 0))
        
        # Add user count display to connected_frame header
        self.user_count_label = ttk.Label(
            connected_frame,
            text="Users: 0/10",
            font=self.fonts['normal']
        )
        self.user_count_label.pack(anchor=tk.E, pady=(0, 5))
        
        # Add server message controls
        message_frame = ttk.LabelFrame(user_frame, text="Server Messages", padding="5")
        message_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.server_message = ttk.Entry(message_frame, width=30)
        self.server_message.pack(fill=tk.X, padx=5, pady=5)
        
        msg_buttons = ttk.Frame(message_frame)
        msg_buttons.pack(fill=tk.X, padx=5)
        
        ttk.Button(
            msg_buttons,
            text="Info",
            command=lambda: self.send_server_message('info'),
            style='Info.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            msg_buttons,
            text="Warning",
            command=lambda: self.send_server_message('warning'),
            style='Warning.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            msg_buttons,
            text="Success",
            command=lambda: self.send_server_message('success'),
            style='Success.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            msg_buttons,
            text="Error",
            command=lambda: self.send_server_message('error'),
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
    def clear_log(self):
        """Clear the log display"""
        if messagebox.askyesno("Clear Log", "Clear all log messages?"):
            self.log_display.delete(1.0, tk.END)
            
    def save_log(self):
        """Save log contents to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"server_log_{timestamp}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(self.log_display.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
            
    def kick_selected_user(self):
        """Kick currently selected user (for context menu)"""
        selection = self.user_listbox.curselection()
        if selection:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, self.user_listbox.get(selection[0]))
            self.kick_user()

    def block_selected_user(self):
        """Block currently selected user (for context menu)"""
        selection = self.user_listbox.curselection()
        if selection:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, self.user_listbox.get(selection[0]))
            self.block_user()

    def show_user_menu(self, event):
        """Show context menu on right-click"""
        if self.user_listbox.curselection():
            self.user_menu.post(event.x_root, event.y_root)

    def filter_users(self, event=None):
        """Filter users in listbox based on search text"""
        search_text = self.user_filter.get().lower()
        selected_user = None
        
        # Store currently selected user before clearing
        if self.user_listbox.curselection():
            selected_user = self.user_listbox.get(self.user_listbox.curselection())
        
        self.user_listbox.delete(0, tk.END)
        if self.server:
            for username in self.server.clients.values():
                if search_text in username.lower():
                    self.user_listbox.insert(tk.END, username)
                    # Reselect user if it's still in filtered list
                    if username == selected_user:
                        self.user_listbox.selection_set(tk.END)
                        self.username_entry.delete(0, tk.END)
                        self.username_entry.insert(0, username)

    def kick_user(self):
        """Kick user by name or selection"""
        if not self.server:
            messagebox.showerror("Error", "Server not running")
            return
            
        # Get username from entry or selection
        username = self.username_entry.get().strip()
        if not username:
            selection = self.user_listbox.curselection()
            if selection:
                username = self.user_listbox.get(selection[0])
            else:
                messagebox.showerror("Error", "Please enter a username or select a user")
                return
        
        if username in self.server.clients.values():
            if messagebox.askyesno("Confirm Kick", f"Kick user {username}?"):
                # Find and close user's connection
                for sock, name in list(self.server.clients.items()):
                    if name == username:
                        try:
                            sock.send("[System: You have been kicked from the server]".encode())
                            sock.close()
                            del self.server.clients[sock]
                            self.log_message(f"Kicked user: {username}", 'warning')
                            self.server.broadcast(f"[System: {username} has been kicked from the server]")
                        except:
                            pass
                        break
                self.username_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"User '{username}' not found")

    def block_user(self):
        """Block user by name or selection"""
        if not self.server:
            messagebox.showerror("Error", "Server not running")
            return
            
        # Get username from entry or selection
        username = self.username_entry.get().strip()
        if not username:
            selection = self.user_listbox.curselection()
            if selection:
                username = self.user_listbox.get(selection[0])
            else:
                messagebox.showerror("Error", "Please enter a username or select a user")
                return
        
        if self.server.block_user(username):
            self.log_message(f"Blocked user: {username}", 'warning')
            self.username_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"User '{username}' not found")

    def unblock_selected_user(self):
        selection = self.blocked_listbox.curselection()
        if selection and self.server:
            username = self.blocked_listbox.get(selection[0])
            if self.server.unblock_user(username):
                self.log_message(f"Unblocked user: {username}")

    def start_server(self):
        try:
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            server_name = self.server_name_entry.get().strip()
            max_users = int(self.max_users_entry.get().strip())
            max_message_size = int(self.max_message_size_entry.get().strip())
            
            if max_users < 1:
                raise ValueError("Maximum users must be at least 1")
            if max_message_size < 1:
                raise ValueError("Maximum message size must be at least 1")
            
            self.server = ChatServer(
                host=host, 
                port=port, 
                gui=self, 
                server_name=server_name,
                max_users=max_users,
                max_message_size=max_message_size
            )
            self.server.start_server()
            
            # Disable configuration while running
            self.host_entry.config(state='disabled')
            self.port_entry.config(state='disabled')
            self.server_name_entry.config(state='disabled')
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.configure(text="Server Status: Running", foreground=self.colors['success'])
            self.update_user_lists()
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")

    def stop_server(self):
        if self.server:
            self.server.stop_server()
            self.server = None
            
            # Re-enable configuration
            self.host_entry.config(state='normal')
            self.port_entry.config(state='normal')
            self.server_name_entry.config(state='normal')
            
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.configure(text="Server Status: Stopped", foreground=self.colors['error'])

    def run(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Success.TButton', font=self.fonts['normal'])
        style.configure('Danger.TButton', font=self.fonts['normal'])
        style.configure('Warning.TButton', font=self.fonts['normal'])
        style.configure('Secondary.TButton', font=self.fonts['normal'])
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to close the server?"):
            self.stop_server()
            self.root.destroy()

    def send_server_message(self, level):
        """Send a colored system message to all clients"""
        if not self.server:
            messagebox.showerror("Error", "Server not running")
            return
        
        message = self.server_message.get().strip()
        if not message:
            return
        
        # Clear the entry
        self.server_message.delete(0, tk.END)
        
        # Format message based on level
        formatted_msg = f"[Server {level.title()}: {message}]"
        self.log_message(formatted_msg, level)
        
        # Broadcast to clients
        self.server.broadcast(formatted_msg)

    def update_user_lists(self):
        if self.server:
            # Store current filter and selection
            search_text = self.user_filter.get().lower()
            selected_user = None
            if self.user_listbox.curselection():
                selected_user = self.user_listbox.get(self.user_listbox.curselection())
            
            # Update connected users with filter
            self.user_listbox.delete(0, tk.END)
            for username in self.server.clients.values():
                if search_text in username.lower():
                    self.user_listbox.insert(tk.END, username)
                    # Restore selection if user still exists
                    if username == selected_user:
                        self.user_listbox.selection_set(tk.END)
                        self.username_entry.delete(0, tk.END)
                        self.username_entry.insert(0, username)
            
            # Update blocked users
            self.blocked_listbox.delete(0, tk.END)
            for username in self.server.blocked_users:
                self.blocked_listbox.insert(tk.END, username)
            
            # Update user count
            current_users = len(self.server.clients)
            self.user_count_label.configure(
                text=f"Users: {current_users}/{self.server.max_users}",
                foreground=self.colors['error'] if current_users >= self.server.max_users else self.colors['text']
            )
        
        # Schedule next update
        self.root.after(1000, self.update_user_lists)

    def log_message(self, message, level='info'):
        """Log message with timestamp and level-based formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.log_display.insert(tk.END, f"{message}\n", level)
        self.log_display.see(tk.END)

class ChatServer:
    def __init__(self, host='127.0.0.1', port=9999, gui=None, server_name="Main Server", 
                 max_users=10, max_message_size=1024):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.blocked_users = set()
        self.is_running = False
        self.gui = gui
        self.max_users = max_users
        self.max_message_size = max_message_size

    def broadcast(self, message, exclude_client=None, update_count=True):
        """Send message to all clients except the sender"""
        # Send the message
        for client in self.clients:
            if client != exclude_client and self.clients[client] not in self.blocked_users:
                try:
                    client.send(message.encode())
                except:
                    self.remove_client(client)
        
        # Send updated user count if requested
        if update_count:
            count_info = {
                "type": "user_count",
                "current": len(self.clients),
                "max": self.max_users
            }
            count_msg = f"COUNT_UPDATE:{json.dumps(count_info)}"
            for client in self.clients:
                try:
                    client.send(count_msg.encode())
                except:
                    continue

    def handle_client(self, client_socket):
        try:
            # Check if server is full before accepting new client
            if len(self.clients) >= self.max_users:
                client_socket.send("[System: Server is full, try again later]".encode())
                client_socket.close()
                return
                
            # Send server info with max users and message size limit
            server_info = {
                "name": self.server_name,
                "host": self.host,
                "port": self.port,
                "max_users": self.max_users,
                "current_users": len(self.clients),
                "max_message_size": self.max_message_size  # Add message size limit
            }
            client_socket.send(f"SERVER_INFO:{json.dumps(server_info)}".encode())
            
            # Get username
            username = client_socket.recv(1024).decode()
            
            # Check if username is blocked
            if username in self.blocked_users:
                client_socket.send("[System: You are blocked from this server]".encode())
                client_socket.close()
                return
                
            self.clients[client_socket] = username
            
            if self.gui:
                self.gui.log_message(f"{username} joined the chat!", 'success')
            
            # Broadcast join message and update counts
            self.broadcast(f"{username} joined the chat!")
            
            while self.is_running:
                try:
                    message = client_socket.recv(self.max_message_size).decode()
                    if not message:
                        break
                    
                    if len(message.encode()) > self.max_message_size:
                        client_socket.send("[System: Message exceeds maximum size limit]".encode())
                        continue
                        
                    if username not in self.blocked_users:
                        broadcast_message = f"{username}: {message}"
                        self.broadcast(broadcast_message, client_socket)
                        if self.gui:
                            self.gui.log_message(f"{username}: {message}", 'info')
                except:
                    break
        except:
            pass
        finally:
            self.remove_client(client_socket)

    def block_user(self, username):
        if username in [name for name in self.clients.values()]:
            self.blocked_users.add(username)
            # Find user's socket to send direct message
            for sock, name in list(self.clients.items()):
                if name == username:
                    try:
                        sock.send("[System: You have been blocked]".encode())
                        sock.close()
                        del self.clients[sock]
                        # Update counts after removing blocked user
                        self.broadcast(f"[System: {username} has been blocked]")
                    except:
                        pass
                    break
            return True
        return False

    def unblock_user(self, username):
        if username in self.blocked_users:
            self.blocked_users.remove(username)
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Find user's socket to send direct message
            for sock, name in self.clients.items():
                if name == username:
                    try:
                        sock.send(f"[System: {username} has been unblocked]".encode())
                    except:
                        pass
                    break
            # Notify others
            self.broadcast(f"[System: {username} has been unblocked]")
            return True
        return False

    def start_server(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            self.register_server()
            if self.gui:
                self.gui.log_message(f"Server started on {self.host}:{self.port}")
            
            # Start accepting clients in a separate thread
            accept_thread = threading.Thread(target=self.accept_clients)
            accept_thread.daemon = True
            accept_thread.start()
        except Exception as e:
            if self.gui:
                self.gui.log_message(f"Error starting server: {e}")

    def stop_server(self):
        self.is_running = False
        self.unregister_server()
        # Disconnect all clients
        for client in list(self.clients.keys()):
            client.close()
        self.clients.clear()
        self.server_socket.close()
        if self.gui:
            self.gui.log_message("Server stopped")

    def accept_clients(self):
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.daemon = True
                thread.start()
            except:
                break

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            # Broadcast leave message and update counts
            self.broadcast(f"{username} left the chat!")
            if self.gui:
                self.gui.log_message(f"{username} left the chat!")

    def register_server(self):
        """Register server in the registry file"""
        try:
            registry = {}
            try:
                with open(os.path.join(DATA_DIR,"server_registry.json"), "r") as f:
                    registry = json.load(f)
            except:
                pass
            
            registry[self.server_name] = {
                "host": self.host,
                "port": self.port,
                "active": True
            }
            
            with open(os.path.join(DATA_DIR,"server_registry.json"), "w") as f:
                json.dump(registry, f)
            
            if self.gui:
                self.gui.log_message(f"Server '{self.server_name}' registered", 'info')
        except:
            if self.gui:
                self.gui.log_message("Failed to register server", 'error')

    def unregister_server(self):
        """Remove server from registry"""
        try:
            with open(os.path.join(DATA_DIR,"server_registry.json"), "r") as f:
                registry = json.load(f)
            
            if self.server_name in registry:
                del registry[self.server_name]
            
            with open(os.path.join(DATA_DIR,"server_registry.json"), "w") as f:
                json.dump(registry, f)
        except:
            pass

if __name__ == "__main__":
    server_gui = ChatServerGUI()
    server_gui.run()
