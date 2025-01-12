import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from datetime import datetime
from cryptography.fernet import Fernet
import base64
import hashlib
from ttkthemes import ThemedTk
import json

class ChatServerGUI:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Secure Chat Server")
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
        
        # Encryption toggle
        encryption_frame = ttk.Frame(controls_frame)
        encryption_frame.pack(side=tk.RIGHT, padx=5)
        
        self.encryption_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            encryption_frame,
            text="Enable Encryption",
            variable=self.encryption_var,
            command=self.toggle_encryption
        ).pack()
        
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
        
        self.user_listbox = tk.Listbox(
            connected_frame,
            font=self.fonts['normal'],
            selectmode=tk.SINGLE
        )
        self.user_listbox.pack(fill=tk.BOTH, expand=True)
        
        # User controls
        user_controls = ttk.Frame(connected_frame)
        user_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            user_controls,
            text="Block User",
            command=self.block_selected_user,
            style='Warning.TButton'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            user_controls,
            text="Kick User",
            command=self.kick_selected_user,
            style='Danger.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
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
        """Kick selected user from the server"""
        selection = self.user_listbox.curselection()
        if selection and self.server:
            username = self.user_listbox.get(selection[0])
            if messagebox.askyesno("Confirm Kick", f"Kick user {username}?"):
                # Find and close user's connection
                for sock, name in list(self.server.clients.items()):
                    if name == username:
                        try:
                            # Send kick message to user
                            kick_msg = self.server.encrypt_message("[System: You have been kicked from the server]", sock)
                            sock.send(kick_msg.encode())
                            # Close socket
                            sock.close()
                            # Remove from clients
                            del self.server.clients[sock]
                            if sock in self.server.client_keys:
                                del self.server.client_keys[sock]
                            # Log kick
                            self.log_message(f"Kicked user: {username}", 'warning')
                            # Notify other users
                            self.server.broadcast(f"[System: {username} has been kicked from the server]")
                        except:
                            pass
                        break

    def log_message(self, message, level='info'):
        """Log message with timestamp and level-based formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.log_display.insert(tk.END, f"{message}\n", level)
        self.log_display.see(tk.END)

    def update_user_lists(self):
        if self.server:
            # Update connected users
            self.user_listbox.delete(0, tk.END)
            for username in self.server.clients.values():
                self.user_listbox.insert(tk.END, username)
            
            # Update blocked users
            self.blocked_listbox.delete(0, tk.END)
            for username in self.server.blocked_users:
                self.blocked_listbox.insert(tk.END, username)
        
        # Schedule next update
        self.root.after(1000, self.update_user_lists)

    def block_selected_user(self):
        selection = self.user_listbox.curselection()
        if selection and self.server:
            username = self.user_listbox.get(selection[0])
            if self.server.block_user(username):
                self.log_message(f"Blocked user: {username}")

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
            
            self.server = ChatServer(host=host, port=port, gui=self, server_name=server_name)
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

    def toggle_encryption(self):
        """Toggle encryption and notify all clients"""
        if self.server:
            new_state = self.encryption_var.get()
            status = "enabled" if new_state else "disabled"
            self.log_message(f"Encryption {status}")
            
            # Notify clients before changing encryption state
            self.server.broadcast(f"[System: Server encryption has been {status}]")
            
            # Update server encryption state
            self.server.encryption_enabled = new_state
            
            if new_state:
                # Generate new server key
                self.server.cipher_suite = Fernet(Fernet.generate_key())
                # Send new keys to all connected clients
                for client in self.server.clients:
                    try:
                        client_key = Fernet.generate_key()
                        self.server.client_keys[client] = Fernet(client_key)
                        client.send(f"KEY:{client_key.decode()}".encode())
                        # Wait for acknowledgment
                        try:
                            client.settimeout(2.0)  # Set timeout for acknowledgment
                            client.recv(1024)
                            client.settimeout(None)  # Remove timeout
                        except:
                            self.log_message(f"Failed to get acknowledgment from {self.server.clients[client]}", 'warning')
                    except:
                        self.log_message(f"Failed to send key to {self.server.clients[client]}", 'error')
            else:
                # Clear encryption state
                self.server.client_keys.clear()
                self.server.cipher_suite = Fernet(Fernet.generate_key())  # Keep a valid key but don't use it

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
        
        # Broadcast to clients with encryption
        if self.server.encryption_enabled:
            for client in self.server.clients:
                try:
                    encrypted_msg = self.server.encrypt_message(formatted_msg, client)
                    client.send(encrypted_msg.encode())
                except:
                    continue
        else:
            self.server.broadcast(formatted_msg)

class ChatServer:
    def __init__(self, host='127.0.0.1', port=9999, gui=None, server_name="Main Server"):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_socket: username}
        self.client_keys = {}  # {client_socket: cipher_suite}
        self.blocked_users = set()
        self.is_running = False
        self.gui = gui
        self.encryption_enabled = True
        self.cipher_suite = Fernet(Fernet.generate_key())

    def encrypt_message(self, message, client_socket=None):
        """Encrypt message for sending"""
        try:
            if self.encryption_enabled:
                if client_socket and client_socket in self.client_keys:
                    # Use client's key if available
                    cipher = self.client_keys[client_socket]
                    encrypted = cipher.encrypt(message.encode())
                    return f"ENCRYPTED:{encrypted.decode()}"
                elif self.cipher_suite:
                    # Use server's key as fallback
                    encrypted = self.cipher_suite.encrypt(message.encode())
                    return f"ENCRYPTED:{encrypted.decode()}"
            return f"PLAIN:{message}"
        except Exception as e:
            print(f"Encryption error: {e}")  # For debugging
            return f"PLAIN:{message}"

    def decrypt_message(self, message, client_socket=None):
        """Decrypt received message"""
        try:
            if message.startswith("ENCRYPTED:"):
                if self.encryption_enabled:
                    try:
                        encrypted = message[len("ENCRYPTED:"):].encode()
                        if client_socket and client_socket in self.client_keys:
                            # Use client's key if available
                            cipher = self.client_keys[client_socket]
                            return cipher.decrypt(encrypted).decode()
                        elif self.cipher_suite:
                            # Use server's key as fallback
                            return self.cipher_suite.decrypt(encrypted).decode()
                    except Exception as e:
                        print(f"Decryption error: {e}")  # For debugging
                        return "[Encrypted message - Decryption failed]"
                return "[Encrypted message - Encryption disabled]"
            elif message.startswith("PLAIN:"):
                return message[len("PLAIN:"):]
            return message
        except Exception as e:
            print(f"Message processing error: {e}")  # For debugging
            return f"[Message processing failed: {str(e)}]"

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

    def broadcast(self, message, exclude_client=None):
        """Send message to all clients except the sender"""
        for client in self.clients:
            if client != exclude_client and self.clients[client] not in self.blocked_users:
                try:
                    encrypted_message = self.encrypt_message(message, client)
                    client.send(encrypted_message.encode())
                except:
                    self.remove_client(client)

    def handle_client(self, client_socket):
        try:
            # Send server info with encryption status
            server_info = {
                "name": self.server_name,
                "host": self.host,
                "port": self.port,
                "encryption": self.encryption_enabled
            }
            client_socket.send(f"SERVER_INFO:{json.dumps(server_info)}".encode())
            
            # Setup encryption if enabled
            if self.encryption_enabled:
                try:
                    client_key = Fernet.generate_key()
                    self.client_keys[client_socket] = Fernet(client_key)
                    client_socket.send(f"KEY:{client_key.decode()}".encode())
                    client_socket.recv(1024)  # Wait for acknowledgment
                except Exception as e:
                    print(f"Encryption setup error: {e}")
                    if self.gui:
                        self.gui.log_message("Failed to establish encrypted connection", 'error')
                    return
            
            # Get username
            encrypted_username = client_socket.recv(1024).decode()
            username = self.decrypt_message(encrypted_username, client_socket)
            
            self.clients[client_socket] = username
            
            if self.gui:
                self.gui.log_message(f"{username} joined the chat!", 'success')
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.broadcast(f"[{timestamp}] {username} joined the chat!")
            
            while self.is_running:
                try:
                    encrypted_message = client_socket.recv(1024).decode()
                    if not encrypted_message:
                        break
                    
                    message = self.decrypt_message(encrypted_message, client_socket)
                    
                    if username not in self.blocked_users:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        broadcast_message = f"[{timestamp}] {username}: {message}"
                        self.broadcast(broadcast_message, client_socket)
                        if self.gui:
                            self.gui.log_message(f"{username}: {message}", 'info')
                except:
                    break
        except:
            pass
        finally:
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.broadcast(f"[{timestamp}] {username} left the chat!")
            if self.gui:
                self.gui.log_message(f"{username} left the chat!")

    def block_user(self, username):
        if username in [name for name in self.clients.values()]:
            self.blocked_users.add(username)
            timestamp = datetime.now().strftime("%H:%M:%S")
            # Find user's socket to send direct message
            for sock, name in self.clients.items():
                if name == username:
                    try:
                        block_msg = self.encrypt_message(f"[System: {username} has been blocked]", sock)
                        sock.send(block_msg.encode())
                    except:
                        pass
                    break
            # Notify others
            self.broadcast(f"[System: {username} has been blocked]")
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
                        unblock_msg = self.encrypt_message(f"[System: {username} has been unblocked]", sock)
                        sock.send(unblock_msg.encode())
                    except:
                        pass
                    break
            # Notify others
            self.broadcast(f"[System: {username} has been unblocked]")
            return True
        return False

    def register_server(self):
        """Register server in the registry file"""
        try:
            registry = {}
            try:
                with open("server_registry.json", "r") as f:
                    registry = json.load(f)
            except:
                pass
            
            registry[self.server_name] = {
                "host": self.host,
                "port": self.port,
                "active": True
            }
            
            with open("server_registry.json", "w") as f:
                json.dump(registry, f)
            
            if self.gui:
                self.gui.log_message(f"Server '{self.server_name}' registered", 'info')
        except:
            if self.gui:
                self.gui.log_message("Failed to register server", 'error')

    def unregister_server(self):
        """Remove server from registry"""
        try:
            with open("server_registry.json", "r") as f:
                registry = json.load(f)
            
            if self.server_name in registry:
                del registry[self.server_name]
            
            with open("server_registry.json", "w") as f:
                json.dump(registry, f)
        except:
            pass

if __name__ == "__main__":
    server_gui = ChatServerGUI()
    server_gui.run()
