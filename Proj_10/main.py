import tkinter as tk
from typing import Dict, List, Optional, Set, Tuple
import math
import json
from tkinter import messagebox ,filedialog

class Node:
    def __init__(self, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.previous_node: Optional[Node] = None
        self.weight = float('inf')
        self.edges: Dict[Node, float] = {}  # {connected_node: distance}

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'edges': {connected_node.name: distance 
                     for connected_node, distance in self.edges.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        node = cls(data['name'], data['x'], data['y'])
        # Edges will be connected later
        return node

class Dijkstra:
    def __init__(self, root):
        self.nodes: Dict[str, Node] = {}
        self.root = root
        self.next_node_id = 0  # Add counter for node IDs

    def add_node(self, x: int, y: int) -> None:
        # Find the next available node number
        while f"N{self.next_node_id}" in self.nodes:
            self.next_node_id += 1
            
        name = f"N{self.next_node_id}"
        self.nodes[name] = Node(name, x, y)
        self.next_node_id += 1
    def remove_node(self, name: str) -> None:
        if name in self.nodes:
            # Remove all edges connected to this node
            node = self.nodes[name]
            for connected_node in list(node.edges.keys()):
                self.remove_edge(name, connected_node.name)
            del self.nodes[name]
            self.next_node_id -= 1

    def add_edge(self, node1_name: str, node2_name: str) -> bool:
        # Validate nodes exist and aren't the same
        if (node1_name not in self.nodes or 
            node2_name not in self.nodes or 
            node1_name == node2_name):
            return False

        node1 = self.nodes[node1_name]
        node2 = self.nodes[node2_name]

        # Check if edge already exists
        if node2 in node1.edges:
            return False

        # Get distance from user
        dialog = ModernDialog(self.root)
        self.root.wait_window(dialog)
        
        if dialog.result is not None:
            node1.edges[node2] = dialog.result
            node2.edges[node1] = dialog.result
            return True
        return False

    def remove_edge(self, node1_name: str, node2_name: str) -> None:
        if node1_name in self.nodes and node2_name in self.nodes:
            node1 = self.nodes[node1_name]
            node2 = self.nodes[node2_name]
            if node2 in node1.edges:
                del node1.edges[node2]
            if node1 in node2.edges:
                del node2.edges[node1]

    def find_path(self, start_name: str, end_name: str) -> List[Node]:
        if start_name not in self.nodes or end_name not in self.nodes:
            return []

        # Reset all nodes before finding new path
        for node in self.nodes.values():
            node.weight = float('inf')
            node.previous_node = None

        # Initialize
        unvisited: Set[Node] = set(self.nodes.values())
        current = self.nodes[start_name]
        current.weight = 0

        while unvisited and current.name != end_name:
            for neighbor, distance in current.edges.items():
                if neighbor in unvisited:
                    new_weight = current.weight + distance
                    if new_weight < neighbor.weight:
                        neighbor.weight = new_weight
                        neighbor.previous_node = current

            unvisited.remove(current)
            if not unvisited:
                break

            # Find next node with minimum weight
            current = min(unvisited, key=lambda x: x.weight)

        # Reconstruct path
        path = []
        current = self.nodes[end_name]
        while current:
            path.append(current)
            current = current.previous_node
        return list(reversed(path))

    def clear(self):
        self.nodes.clear()
        self.next_node_id = 0  # Reset the counter when clearing

    def save_to_file(self, filename: str) -> None:
        data = {
            'nodes': {name: node.to_dict() for name, node in self.nodes.items()},
            'next_node_id': self.next_node_id
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing nodes
        self.nodes.clear()
        
        # Create nodes first
        for name, node_data in data['nodes'].items():
            node = Node.from_dict(node_data)
            self.nodes[name] = node
        
        # Connect edges
        for name, node_data in data['nodes'].items():
            node = self.nodes[name]
            for connected_name, distance in node_data['edges'].items():
                node.edges[self.nodes[connected_name]] = distance
        
        self.next_node_id = data['next_node_id']

class ModernDialog(tk.Toplevel):
    def __init__(self, parent, title="Enter Distance"):
        super().__init__(parent)
        self.result = None
        
        # Window setup
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Style
        self.configure(bg='#f0f0f0')
        self.resizable(False, False)
        
        # Create main frame
        main_frame = tk.Frame(self, bg='#f0f0f0', padx=20, pady=15)
        main_frame.pack(expand=True, fill='both')
        
        # Title label
        title_label = tk.Label(
            main_frame,
            text="Enter the distance:",
            font=('Helvetica', 12),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 10))
        
        # Entry field
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(
            main_frame,
            textvariable=self.entry_var,
            font=('Helvetica', 11),
            width=20,
            bd=0,
            relief='solid',
            bg='white'
        )
        self.entry.pack(pady=(0, 15), ipady=8)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x')
        
        # Buttons
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=self.ok_pressed,
            width=10,
            bg='#007bff',
            fg='white',
            font=('Helvetica', 10),
            bd=0,
            relief='solid',
            activebackground='#0056b3',
            activeforeground='white'
        )
        ok_button.pack(side='right', padx=5)
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_pressed,
            width=10,
            bg='#6c757d',
            fg='white',
            font=('Helvetica', 10),
            bd=0,
            relief='solid',
            activebackground='#545b62',
            activeforeground='white'
        )
        cancel_button.pack(side='right', padx=5)
        
        # Bindings
        self.entry.bind('<Return>', lambda e: self.ok_pressed())
        self.entry.bind('<Escape>', lambda e: self.cancel_pressed())
        
        # Center dialog
        self.center_dialog()
        
        # Set focus
        self.entry.focus_set()
    
    def center_dialog(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.master.winfo_rootx() + (self.master.winfo_width() // 2) - (width // 2))
        y = (self.master.winfo_rooty() + (self.master.winfo_height() // 2) - (height // 2))
        self.geometry(f'+{x}+{y}')
    
    def ok_pressed(self):
        try:
            value = float(self.entry_var.get())
            if value <= 0:
                self.show_error("Distance must be positive")
                return
            self.result = value
            self.destroy()
        except ValueError:
            self.show_error("Please enter a valid number")
    
    def cancel_pressed(self):
        self.result = None
        self.destroy()
    
    def show_error(self, message):
        messagebox.showerror(
            "Invalid Input",
            message,
            parent=self
        )

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra Algorithm Visualization")
        
        # Add color constants first
        self.COLORS = {
            'primary': '#2196F3',    # Material Blue
            'secondary': '#757575',   # Gray
            'accent': '#FF4081',      # Pink
            'background': '#FAFAFA',  # Light Gray
            'surface': '#FFFFFF',     # White
            'text': '#212121',        # Dark Gray
            'node': {
                'default': '#2196F3',
                'selected': '#FFC107', # Amber
                'path': '#4CAF50'      # Green
            }
        }
        
        # Create mode variable
        self.mode_var = tk.StringVar(value="add")
        
        # Update root window style
        self.root.configure(bg=self.COLORS['background'])
        
        # Create main frame first
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both')
        self.main_frame.configure(bg=self.COLORS['background'])
        
        # Create toolbar
        self.create_toolbar()
        
        # Create canvas
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600)
        self.canvas.pack(expand=True, fill='both')
        
        # Configure canvas style
        self.canvas.configure(
            bg=self.COLORS['surface'],
            highlightthickness=0,
            relief='ridge',
            bd=1
        )
        
        self.dijkstra = Dijkstra(root)
        self.selected_node = None
        self.node_radius = 20
        self.mode = "add"  # Modes: "add", "remove", "connect"
        
        self.setup_events()

    def create_toolbar(self):
        toolbar = tk.Frame(self.main_frame, bg=self.COLORS['background'])
        toolbar.pack(side='top', fill='x', padx=10, pady=10)
        
        # Create style for buttons
        button_style = {
            'font': ('Helvetica', 10),
            'bd': 0,
            'relief': 'flat',
            'padx': 15,
            'pady': 8,
            'bg': self.COLORS['primary'],
            'fg': 'white',
            'activebackground': '#1976D2',  # Darker blue
            'activeforeground': 'white'
        }
        
        # Create style for radio buttons
        radio_style = {
            'font': ('Helvetica', 10),
            'bg': self.COLORS['background'],
            'activebackground': self.COLORS['background'],
            'selectcolor': self.COLORS['primary']
        }
        
        # Mode buttons with updated style
        tk.Radiobutton(
            toolbar, text="Add Nodes", variable=self.mode_var, value="add",
            command=lambda: self.change_mode("add"),
            **radio_style
        ).pack(side='left', padx=5)
        
        tk.Radiobutton(
            toolbar, text="Connect Nodes", variable=self.mode_var, value="connect",
            command=lambda: self.change_mode("connect"),
            **radio_style
        ).pack(side='left', padx=5)
        
        tk.Radiobutton(
            toolbar, text="Remove", variable=self.mode_var, value="remove",
            command=lambda: self.change_mode("remove"),
            **radio_style
        ).pack(side='left', padx=5)
        
        # Action buttons with updated style
        tk.Button(toolbar, text="Clear All", command=self.clear_canvas, **button_style).pack(side='right', padx=5)
        tk.Button(toolbar, text="Find Path", command=self.find_path_gui, **button_style).pack(side='right', padx=5)
        
        # Add Save/Load buttons
        tk.Button(
            toolbar,
            text="Save",
            command=self.save_graph,
            **button_style
        ).pack(side='right', padx=5)
        
        tk.Button(
            toolbar,
            text="Load",
            command=self.load_graph,
            **button_style
        ).pack(side='right', padx=5)

    def change_mode(self, mode):
        self.mode = mode
        self.selected_node = None
        self.draw_background()

    def setup_events(self):
        self.canvas.bind('<Button-1>', self.handle_click)
        self.canvas.bind('<B1-Motion>', self.move_node)
        self.canvas.bind('<Escape>', lambda e: self.cancel_selection())

    def handle_click(self, event):
        clicked_node = self.find_node_at_position(event.x, event.y)
        
        if self.mode == "add":
            if not clicked_node:  # Only add if not clicking existing node
                self.dijkstra.add_node(event.x, event.y)  # Remove name parameter
                self.draw_background()
                
        elif self.mode == "remove":
            if clicked_node:
                self.dijkstra.remove_node(clicked_node.name)
                if self.selected_node == clicked_node:
                    self.selected_node = None
                self.draw_background()
                
        elif self.mode == "connect":
            if clicked_node:
                if self.selected_node is None:
                    self.selected_node = clicked_node
                    self.draw_node(clicked_node, color='yellow')  # Highlight selected node
                else:
                    if self.dijkstra.add_edge(self.selected_node.name, clicked_node.name):
                        self.draw_background()
                    self.selected_node = None

    def cancel_selection(self):
        self.selected_node = None
        self.draw_background()

    def draw_background(self):
        self.canvas.delete('all')
        self.draw_all_edges()
        self.draw_all_nodes()

    def draw_node(self, node: Node, color=None):
        x, y = node.x, node.y
        color = color or self.COLORS['node']['default']
        
        # Add shadow effect
        self.canvas.create_oval(
            x - self.node_radius + 2, y - self.node_radius + 2,
            x + self.node_radius + 2, y + self.node_radius + 2,
            fill='#000022', tags='shadow'
        )
        
        # Draw node with border
        self.canvas.create_oval(
            x - self.node_radius, y - self.node_radius,
            x + self.node_radius, y + self.node_radius,
            fill=color,
            outline='white',
            width=2,
            tags='node'
        )
        
        # Draw node label
        self.canvas.create_text(
            x, y,
            text=node.name,
            fill='white',
            font=('Helvetica', 11, 'bold'),
            tags='node'
        )

    def draw_edge(self, node1: Node, node2: Node, color='#757575'):
        # Draw the line with transparency
        self.canvas.create_line(
            node1.x, node1.y, node2.x, node2.y,
            fill=color,
            width=2,
            tags='edge'
        )
        
        # Calculate midpoint and draw distance
        mid_x = (node1.x + node2.x) / 2
        mid_y = (node1.y + node2.y) / 2
        
        # Add a semi-transparent background for the distance label
        distance = node1.edges[node2]
        text = f"{distance:.1f}"
        self.canvas.create_oval(
            mid_x - 20, mid_y - 12,
            mid_x + 20, mid_y + 12,
            fill='#FFFF99',
            outline='#FFFFFF',
            tags='edge'
        )
        self.canvas.create_text(
            mid_x, mid_y,
            text=text,
            font=('Helvetica', 9),
            fill=self.COLORS['text'],
            tags='edge'
        )

    def draw_all_nodes(self):
        for node in self.dijkstra.nodes.values():
            self.draw_node(node)

    def draw_all_edges(self):
        drawn_edges = set()
        for node in self.dijkstra.nodes.values():
            for connected_node in node.edges:
                edge = tuple(sorted([node.name, connected_node.name]))
                if edge not in drawn_edges:
                    self.draw_edge(node, connected_node)
                    drawn_edges.add(edge)

    def draw_path(self, path: List[Node]):
        for i in range(len(path) - 1):
            self.draw_edge(path[i], path[i + 1], color='red')
        self.draw_all_nodes()
        for node in path:
            self.draw_node(node, color='yellow')

    def find_node_at_position(self, x: int, y: int) -> Optional[Node]:
        for node in self.dijkstra.nodes.values():
            if math.sqrt((node.x - x)**2 + (node.y - y)**2) <= self.node_radius:
                return node
        return None

    def move_node(self, event):
        node = self.find_node_at_position(event.x, event.y)
        if node:
            node.x = event.x
            node.y = event.y
            self.draw_background()

    def clear_canvas(self):
        self.dijkstra = Dijkstra(self.root)  # This will reset the counter
        self.selected_node = None
        self.draw_background()

    def find_path_gui(self):
        if len(self.dijkstra.nodes) < 2:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Find Path")
        dialog.resizable(False,False)

        dialog.configure(bg=self.COLORS['background'])
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        main_frame = tk.Frame(dialog, bg=self.COLORS['background'], padx=20, pady=15)
        main_frame.pack(expand=True, fill='both')
        
        # Title label
        tk.Label(
            main_frame,
            text="Select Start and End Nodes",
            font=('Helvetica', 12, 'bold'),
            bg=self.COLORS['background'],
            fg=self.COLORS['text']
        ).pack(pady=(0, 15))
        
        # Variables
        start_var = tk.StringVar(dialog)
        end_var = tk.StringVar(dialog)
        
        node_names = list(self.dijkstra.nodes.keys())
        start_var.set(node_names[0])
        end_var.set(node_names[-1])
        
        def update_path(*args):
            # Reset and redraw everything when selection changes
            self.draw_background()
            path = self.dijkstra.find_path(start_var.get(), end_var.get())
            if path:
                self.draw_path(path)
        
        # Bind the update function to variable changes
        start_var.trace('w', update_path)
        end_var.trace('w', update_path)
        
        # Dropdown style
        dropdown_style = {
            'bg': 'white',
            'activebackground': self.COLORS['primary'],
            'activeforeground': 'white',
            'relief': 'solid',
            'bd': 1,
            'highlightthickness': 0,
        }
        
        # Start node selection
        start_frame = tk.Frame(main_frame, bg=self.COLORS['background'])
        start_frame.pack(fill='x', pady=5)
        
        tk.Label(
            start_frame,
            text="Start node:",
            font=('Helvetica', 10),
            bg=self.COLORS['background'],
            fg=self.COLORS['text']
        ).pack(side='left')
        
        start_menu = tk.OptionMenu(start_frame, start_var, *node_names)
        start_menu.configure(**dropdown_style)
        start_menu.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # End node selection
        end_frame = tk.Frame(main_frame, bg=self.COLORS['background'])
        end_frame.pack(fill='x', pady=5)
        
        tk.Label(
            end_frame,
            text="End node:",
            font=('Helvetica', 10),
            bg=self.COLORS['background'],
            fg=self.COLORS['text']
        ).pack(side='left')
        
        end_menu = tk.OptionMenu(end_frame, end_var, *node_names)
        end_menu.configure(**dropdown_style)
        end_menu.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=self.COLORS['background'])
        button_frame.pack(fill='x', pady=(15, 0))
        
        def find():
            path = self.dijkstra.find_path(start_var.get(), end_var.get())
            self.draw_background()
            if path:
                self.draw_path(path)
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        # Buttons
        button_style = {
            'font': ('Helvetica', 10),
            'bd': 0,
            'relief': 'flat',
            'padx': 15,
            'pady': 8,
        }
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=cancel,
            bg=self.COLORS['secondary'],
            fg='white',
            activebackground='#616161',
            activeforeground='white',
            **button_style
        )
        cancel_btn.pack(side='right', padx=5)
        
        find_btn = tk.Button(
            button_frame,
            text="Find Path",
            command=find,
            bg=self.COLORS['primary'],
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            **button_style
        )
        find_btn.pack(side='right', padx=5)
        
        # Center dialog on parent window
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Key bindings
        dialog.bind('<Return>', lambda e: find())
        dialog.bind('<Escape>', lambda e: cancel())
        
        # Wait for dialog
        dialog.wait_window()

    def save_graph(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Graph"
        )
        if filename:
            try:
                self.dijkstra.save_to_file(filename)
                messagebox.showinfo(
                    "Success",
                    "Graph saved successfully!",
                    parent=self.root
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to save graph: {str(e)}",
                    parent=self.root
                )
    
    def load_graph(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Graph"
        )
        if filename:
            try:
                self.dijkstra.load_from_file(filename)
                self.selected_node = None
                self.draw_background()
                messagebox.showinfo(
                    "Success",
                    "Graph loaded successfully!",
                    parent=self.root
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to load graph: {str(e)}",
                    parent=self.root
                )

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
