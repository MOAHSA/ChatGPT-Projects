import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
from cryptography.fernet import Fernet
from ttkthemes import ThemedTk
import json

class ChatClient:
    def __init__(self):
        self.root = ThemedTk(theme="arc")
        self.root.title("Secure Chat")
        self.root.geometry("1000x700")
        
        # Configure colors and fonts
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#2196F3',
            'secondary': '#64B5F6',
            'success': '#4CAF50',
            'error': '#F44336',
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
        self.cipher_suite = None
        self.encryption_enabled = False  # Server's encryption status
        
        self.create_login_frame()
        self.create_chat_frame()
        
        # Initially show only login frame
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure styles
        self.configure_styles()
        
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
            text="Secure Chat",
            font=self.fonts['header'],
            foreground=self.colors['primary']
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Connect securely with end-to-end encryption",
            font=self.fonts['subheader'],
            foreground=self.colors['light_text']
        ).pack(pady=(5, 0))
        
        # Create login container
        login_container = ttk.Frame(self.login_frame, padding="20")
        login_container.pack(expand=True)
        
        # Server settings
        settings_frame = ttk.LabelFrame(
            login_container,
            text="Connection Settings",
            padding="20"
        )
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Server connection options
        server_frame = ttk.LabelFrame(login_container, text="Server Connection", padding="10")
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
        username_frame = ttk.Frame(login_container)
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
            login_container,
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
        
        # Configure message tags
        self.chat_display.tag_configure(
            'own_msg',
            background=self.colors['own_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20
        )
        
        self.chat_display.tag_configure(
            'other_msg',
            background=self.colors['other_msg'],
            lmargin1=20,
            lmargin2=20,
            rmargin=20
        )
        
        self.chat_display.tag_configure(
            'system_msg',
            background=self.colors['system_msg'],
            foreground=self.colors['light_text'],
            justify='center',
            spacing1=5,
            spacing3=5
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
        
        # Add encryption status indicator
        self.encryption_label = ttk.Label(
            user_frame,
            text="🔒 Encrypted",  # or 🔓 for unencrypted
            font=self.fonts['normal'],
            foreground=self.colors['success'],
            padding=(10, 0)
        )
        self.encryption_label.pack(side=tk.LEFT)

    def format_message(self, message, is_own=False, is_system=False):
        """Format and display message with appropriate styling and timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_system:
            # Check message type and add timestamp
            if "[Server Info:" in message:
                self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", 'info_msg')
            elif "[Server Warning:" in message:
                self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", 'warning_msg')
            elif "[Server Success:" in message:
                self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", 'success_msg')
            elif "[Server Error:" in message:
                self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", 'error_msg')
            else:
                self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", 'system_msg')
        else:
            tag = 'own_msg' if is_own else 'other_msg'
            self.chat_display.insert(tk.END, f"\n[{timestamp}] {message}\n", tag)
        self.chat_display.see(tk.END)
    def encrypt_message(self, message):
        """Encrypt message before sending"""
        try:
            if self.encryption_enabled and self.cipher_suite:
                encrypted = self.cipher_suite.encrypt(message.encode())
                return f"ENCRYPTED:{encrypted.decode()}"
            return f"PLAIN:{message}"
        except Exception as e:
            print(f"Encryption error: {e}")
            return f"PLAIN:{message}"

    def decrypt_message(self, message):
        """Decrypt received message"""
        try:
            if message.startswith("ENCRYPTED:"):
                if self.encryption_enabled and self.cipher_suite:
                    try:
                        encrypted = message[len("ENCRYPTED:"):].encode()
                        return self.cipher_suite.decrypt(encrypted).decode()
                    except Exception as e:
                        print(f"Decryption error: {e}")
                        return "[Encrypted message - Decryption failed]"
                return "[Encrypted message - Server encryption disabled]"
            elif message.startswith("PLAIN:"):
                return message[len("PLAIN:"):]
            return message
        except Exception as e:
            print(f"Message processing error: {e}")
            return f"[Message processing failed: {str(e)}]"

    def lookup_server(self, server_name):
        """Look up server details from registry"""
        try:
            with open("server_registry.json", "r") as f:
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
            
            # Receive server info and set encryption status
            try:
                server_info = self.client_socket.recv(1024).decode()
                if server_info.startswith("SERVER_INFO:"):
                    info = json.loads(server_info[len("SERVER_INFO:"):])
                    self.server_name = info["name"]
                    # Set initial encryption state from server
                    self.encryption_enabled = info.get("encryption", False)
                    self.update_encryption_status(self.encryption_enabled)
                    
                    # Handle initial encryption setup if enabled
                    if self.encryption_enabled:
                        try:
                            key_msg = self.client_socket.recv(1024).decode()
                            if key_msg.startswith("KEY:"):
                                key = key_msg[4:].encode()
                                self.cipher_suite = Fernet(key)
                                self.client_socket.send(b"ACK")
                            else:
                                raise ValueError("Invalid encryption key received")
                        except Exception as e:
                            print(f"Initial encryption setup error: {e}")
                            messagebox.showerror("Error", "Failed to setup encryption")
                            self.client_socket.close()
                            self.client_socket = None
                            return
            except:
                self.server_name = "Unknown Server"
                self.update_encryption_status(False)
            
            # Send username
            self.client_socket.send(self.encrypt_message(self.username).encode())
            
            # Update UI
            self.login_frame.pack_forget()
            self.chat_frame.pack(fill=tk.BOTH, expand=True)
            self.user_label.configure(text=f"Connected to {self.server_name} as: {self.username}")
            
            # Start receiving messages
            self.connected = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
        except socket.timeout:
            messagebox.showerror("Error", "Connection timed out")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Connection refused - server may be offline")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server: {str(e)}")
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
        
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
        self.cipher_suite = None

    def send_message(self):
        if not self.connected or not self.client_socket:
            messagebox.showerror("Error", "Not connected to server")
            self.disconnect()  # Ensure proper cleanup
            return
        
        message = self.message_entry.get().strip()
        if message:
            try:
                encrypted_message = self.encrypt_message(message)
                self.client_socket.send(encrypted_message.encode())
                self.format_message(f"You: {message}", is_own=True, is_system=False)
                self.message_entry.delete(0, tk.END)
            except:
                messagebox.showerror("Error", "Could not send message")
                self.disconnect()
                
    def receive_messages(self):
        while self.connected and self.client_socket:
            try:
                if not self.client_socket:
                    break
                
                encrypted_message = self.client_socket.recv(1024).decode()
                if not encrypted_message:
                    break
                
                message = self.decrypt_message(encrypted_message)
                
                # Handle encryption status changes first
                if "Server encryption has been" in message:
                    enabled = "enabled" in message.lower()
                    self.update_encryption_status(enabled)
                    self.format_message(message, is_system=True)
                    
                    if enabled and self.client_socket:
                        try:
                            key_msg = self.client_socket.recv(1024).decode()
                            if key_msg.startswith("KEY:") and self.client_socket:
                                key = key_msg[4:].encode()
                                self.cipher_suite = Fernet(key)
                                if self.client_socket:
                                    self.client_socket.send(b"ACK")
                        except:
                            print("Failed to setup new encryption key")
                    else:
                        self.cipher_suite = None
                    continue
                
                # Handle different message types
                if "[Server Info:" in message:
                    self.format_message(message, is_system=True)
                elif "[Server Warning:" in message:
                    self.format_message(message, is_system=True)
                elif "[Server Success:" in message:
                    self.format_message(message, is_system=True)
                elif "[Server Error:" in message:
                    self.format_message(message, is_system=True)
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
                # Normal message handling
                elif not message.endswith(f"{self.username}: {self.message_entry.get().strip()}"):
                    self.format_message(message, is_own=False)
            except:
                break
        
        # Handle disconnection outside the loop
        if self.connected:
            messagebox.showwarning("Disconnected", "Lost connection to server")
            self.root.after(0, self.disconnect)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to close the chat?"):
            self.disconnect()
            self.root.destroy()

    def update_encryption_status(self, enabled):
        """Update encryption status display and internal state"""
        self.encryption_enabled = enabled
        if enabled:
            self.encryption_label.configure(
                text="🔒 Encrypted",
                foreground=self.colors['success']
            )
        else:
            self.encryption_label.configure(
                text="🔓 Unencrypted",
                foreground=self.colors['error']
            )
            self.cipher_suite = None  # Clear encryption key when disabled

if __name__ == "__main__":
    client = ChatClient()
    client.run()
