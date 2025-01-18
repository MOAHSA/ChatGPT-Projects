import socket
import threading
from datetime import datetime
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ttkthemes import ThemedTk

class ProxyGUI:
    def __init__(self):
        self.root = ThemedTk(theme="arc")  # Using themed tk for better visuals
        self.root.title("Chat Proxy Monitor")
        self.root.geometry("900x600")
        
        # Configure colors and fonts
        self.colors = {
            'bg': '#f0f0f0',
            'text': '#212121',
            'client': '#E3F2FD',
            'server': '#F3E5F5',
            'connection': '#E8F5E9',
            'disconnection': '#FFEBEE'
        }
        
        self.fonts = {
            'header': ('Helvetica', 12, 'bold'),
            'normal': ('Helvetica', 10),
            'message': ('Helvetica', 10),
        }
        
        # Default server settings
        self.proxy_host = '127.0.0.1'
        self.server_host = '127.0.0.1'
        
        self.create_widgets()
        self.configure_tags()
        
    def configure_tags(self):
        """Configure text tags for different message types"""
        self.message_display.tag_configure('timestamp', foreground='#666666')
        self.message_display.tag_configure('client_msg', background=self.colors['client'])
        self.message_display.tag_configure('server_msg', background=self.colors['server'])
        self.message_display.tag_configure('connection', background=self.colors['connection'])
        self.message_display.tag_configure('disconnection', background=self.colors['disconnection'])
        
    def create_widgets(self):
        # Control Frame
        control_frame = ttk.Frame(self.root, padding="5")
        control_frame.pack(fill=tk.X)
        
        # Server settings
        settings_frame = ttk.LabelFrame(control_frame, text="Settings", padding="5")
        settings_frame.pack(side=tk.LEFT, padx=5)
        
        # Proxy settings
        proxy_frame = ttk.Frame(settings_frame)
        proxy_frame.pack(fill=tk.X, pady=2)
        ttk.Label(proxy_frame, text="Proxy:").pack(side=tk.LEFT, padx=5)
        self.proxy_host_entry = ttk.Entry(proxy_frame, width=15)
        self.proxy_host_entry.insert(0, "127.0.0.1")
        self.proxy_host_entry.pack(side=tk.LEFT, padx=5)
        self.proxy_port_entry = ttk.Entry(proxy_frame, width=6)
        self.proxy_port_entry.insert(0, "9998")
        self.proxy_port_entry.pack(side=tk.LEFT)
        
        # Target server settings
        server_frame = ttk.Frame(settings_frame)
        server_frame.pack(fill=tk.X, pady=2)
        ttk.Label(server_frame, text="Server:").pack(side=tk.LEFT, padx=5)
        self.server_host_entry = ttk.Entry(server_frame, width=15)
        self.server_host_entry.insert(0, "127.0.0.1")
        self.server_host_entry.pack(side=tk.LEFT, padx=5)
        self.server_port_entry = ttk.Entry(server_frame, width=6)
        self.server_port_entry.insert(0, "9999")
        self.server_port_entry.pack(side=tk.LEFT)
        
        # Control buttons frame
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(side=tk.LEFT, padx=20)
        
        # Start/Stop buttons
        self.start_button = ttk.Button(
            buttons_frame, 
            text="Start Proxy",
            command=self.start_proxy,
            style='Accent.TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            buttons_frame,
            text="Stop Proxy",
            command=self.stop_proxy,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            buttons_frame,
            text="Clear Log",
            command=self.clear_log
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame,
            text="Status: Stopped",
            foreground="red",
            font=self.fonts['header']
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Main content area with paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - Message display
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=3)
        
        # Message display with custom font
        self.message_display = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            font=self.fonts['message'],
            height=20
        )
        self.message_display.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Users and controls
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Connected users frame
        users_frame = ttk.LabelFrame(right_frame, text="Connected Users", padding="5")
        users_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.users_listbox = tk.Listbox(
            users_frame,
            font=self.fonts['normal'],
            selectmode=tk.SINGLE
        )
        self.users_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Save button
        ttk.Button(
            right_frame,
            text="Save Logs",
            command=self.save_logs,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=5)
        
    def clear_log(self):
        """Clear the message display"""
        if messagebox.askyesno("Clear Log", "Clear all logged messages?"):
            self.message_display.delete(1.0, tk.END)
            
    def log_message(self, message, direction=None):
        """Display message in GUI with formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Insert timestamp
        self.message_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Determine message tag based on direction
        if direction == "CLIENT_TO_SERVER":
            tag = 'client_msg'
        elif direction == "SERVER_TO_CLIENT":
            tag = 'server_msg'
        elif direction == "CONNECTION":
            tag = 'connection'
        elif direction == "DISCONNECTION":
            tag = 'disconnection'
        else:
            tag = ''  # For system messages
        
        # Insert message with tag
        self.message_display.insert(tk.END, f"{message}\n", tag)
        self.message_display.see(tk.END)
        
        # Save to file if it's a message
        if direction:
            log_entry = {
                "timestamp": timestamp,
                "direction": direction,
                "message": message
            }
            try:
                with open("captured_data.txt", "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except:
                pass

    def update_users(self):
        """Update the users listbox"""
        if hasattr(self, 'proxy') and self.proxy:
            self.users_listbox.delete(0, tk.END)
            for username in self.proxy.usernames.values():
                self.users_listbox.insert(tk.END, username)

    def start_proxy(self):
        """Start the proxy server with configured settings"""
        try:
            proxy_host = self.proxy_host_entry.get().strip()
            proxy_port = int(self.proxy_port_entry.get().strip())
            server_host = self.server_host_entry.get().strip()
            server_port = int(self.server_port_entry.get().strip())
            
            self.proxy = ChatProxy(
                gui=self,
                proxy_host=proxy_host,
                proxy_port=proxy_port,
                server_host=server_host,
                server_port=server_port
            )
            
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", foreground="green")
            
            # Disable settings while running
            self.proxy_host_entry.config(state='disabled')
            self.proxy_port_entry.config(state='disabled')
            self.server_host_entry.config(state='disabled')
            self.server_port_entry.config(state='disabled')
            
            # Start proxy in separate thread
            proxy_thread = threading.Thread(target=self.proxy.start)
            proxy_thread.daemon = True
            proxy_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start proxy: {str(e)}")
    
    def stop_proxy(self):
        """Stop the proxy server"""
        if messagebox.askyesno("Confirm", "Stop proxy server?"):
            self.proxy.stop()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Stopped", foreground="red")
            
            # Re-enable settings
            self.proxy_host_entry.config(state='normal')
            self.proxy_port_entry.config(state='normal')
            self.server_host_entry.config(state='normal')
            self.server_port_entry.config(state='normal')

    def save_logs(self):
        """Save message display contents to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proxy_logs_{timestamp}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(self.message_display.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Logs saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
            
    def run(self):
        """Start the GUI main loop"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window close"""
        if hasattr(self, 'proxy') and self.proxy.is_running:
            if messagebox.askyesno("Quit", "Stop proxy and exit?"):
                self.proxy.stop()
                self.root.destroy()
        else:
            self.root.destroy()

    def log_system_message(self, message):
        """Log system messages without direction"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.message_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.message_display.see(tk.END)

class ChatProxy:
    def __init__(self, gui=None, proxy_host='127.0.0.1', proxy_port=9998, 
                 server_host='127.0.0.1', server_port=9999):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.server_host = server_host 
        self.server_port = server_port
        
        self.proxy_socket = None
        self.connections = {}  # {client_socket: server_socket}
        self.usernames = {}   # {client_socket: username}
        self.is_running = False
        self.gui = gui
        
    def log_message(self, message, direction=None):
        """Log message through GUI"""
        if self.gui:
            self.gui.log_message(message, direction)

    def handle_client_to_server(self, client_socket, server_socket):
        """Forward messages from client to server while logging"""
        try:
            while self.is_running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                        
                    message = data.decode()
                    username = self.usernames.get(client_socket, "Unknown")
                    if self.gui:
                        self.gui.log_message(f"{username} -> Server: {message}", "CLIENT_TO_SERVER")
                    
                    server_socket.send(data)
                except:
                    break
                    
        except Exception as e:
            if self.gui:
                self.gui.log_message(f"Client to server error: {e}")
        finally:
            self.close_connection(client_socket)

    def handle_server_to_client(self, client_socket, server_socket):
        """Forward messages from server to client while logging"""
        try:
            while self.is_running:
                try:
                    data = server_socket.recv(1024)
                    if not data:
                        break
                        
                    message = data.decode()
                    username = self.usernames.get(client_socket, "Unknown")
                    self.log_message(f"Server -> {username}: {message}", "SERVER_TO_CLIENT")
                    
                    client_socket.send(data)
                except:
                    break
                    
        except Exception as e:
            if self.gui:
                self.gui.log_message(f"Server to client error: {e}")
        finally:
            self.close_connection(client_socket)

    def handle_client(self, client_socket):
        """Set up connection forwarding for a new client"""
        try:
            # Connect to real server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((self.server_host, self.server_port))
            
            # Store connection pair
            self.connections[client_socket] = server_socket
            
            # Get username from first message
            username = client_socket.recv(1024).decode()
            self.usernames[client_socket] = username
            self.log_message(f"New connection from: {username}", "CONNECTION")
            
            if self.gui:
                self.gui.update_users()
            
            # Forward username to server
            server_socket.send(username.encode())
            
            # Start forwarding threads
            client_thread = threading.Thread(
                target=self.handle_client_to_server,
                args=(client_socket, server_socket)
            )
            server_thread = threading.Thread(
                target=self.handle_server_to_client,
                args=(client_socket, server_socket)
            )
            
            client_thread.daemon = True
            server_thread.daemon = True
            
            client_thread.start()
            server_thread.start()
            
        except Exception as e:
            if self.gui:
                self.gui.log_message(f"Connection handler error: {e}")
            self.close_connection(client_socket)

    def close_connection(self, client_socket):
        """Clean up a closed connection"""
        if client_socket in self.connections:
            try:
                server_socket = self.connections[client_socket]
                username = self.usernames.get(client_socket, "Unknown")
                
                self.log_message(f"Connection closed: {username}", "DISCONNECTION")
                
                server_socket.close()
                client_socket.close()
                
                del self.connections[client_socket]
                if client_socket in self.usernames:
                    del self.usernames[client_socket]
                    
                if self.gui:
                    self.gui.update_users()
            except:
                pass

    def start(self):
        """Start the proxy server"""
        try:
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind((self.proxy_host, self.proxy_port))
            self.proxy_socket.listen(5)
            self.is_running = True
            
            if self.gui:
                self.gui.log_system_message(f"Proxy running on {self.proxy_host}:{self.proxy_port}")
                self.gui.log_system_message(f"Forwarding to {self.server_host}:{self.server_port}")
            
            while self.is_running:
                try:
                    client_socket, _ = self.proxy_socket.accept()
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    thread.daemon = True
                    thread.start()
                except:
                    if self.is_running:
                        continue
                    break
                    
        except Exception as e:
            if self.gui:
                self.gui.log_system_message(f"Proxy error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the proxy server and clean up"""
        self.is_running = False
        
        # Close all connections
        for client_socket in list(self.connections.keys()):
            self.close_connection(client_socket)
            
        if self.proxy_socket:
            try:
                self.proxy_socket.close()
            except:
                pass
            self.proxy_socket = None
            
        if self.gui:
            self.gui.log_system_message("Proxy stopped")

if __name__ == "__main__":
    # Configure ttk styles
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Helvetica', 10))
    
    gui = ProxyGUI()
    gui.run()
