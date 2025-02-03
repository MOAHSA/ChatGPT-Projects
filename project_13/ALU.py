import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class ALUSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("4-bit ALU Simulator")
        self.root.configure(bg='#1a1a2e')  # Darker background
        
        # Initialize variables first
        self.show_decimal = tk.BooleanVar(value=False)
        self.bit_format = "0b{}"
        
        # Variables for inputs
        self.a_vars = [tk.StringVar(value='0') for _ in range(4)]
        self.b_vars = [tk.StringVar(value='0') for _ in range(4)]
        self.s_vars = [tk.StringVar(value='0') for _ in range(4)]
        self.m_var = tk.StringVar(value='Arithmetic (0)')
        self.cn_var = tk.StringVar(value='0')
        
        # Variables for outputs
        self.f_vars = [tk.StringVar(value='0') for _ in range(4)]
        self.cn4_var = tk.StringVar(value='0')
        self.g_var = tk.StringVar(value='0')
        self.p_var = tk.StringVar(value='0')
        self.equals_var = tk.StringVar(value='0')
        
        # Add decimal sum display variable
        self.decimal_sum = tk.StringVar(value="A:0 B:0 F:0")
        
        # Initialize variables with display values
        self.m_var.set('Arithmetic (0)')
        
        # Configure enhanced styles
        self.configure_styles()
        
        # Add menubar with styling
        self.create_menubar()
        
        self.create_gui()
        
    def configure_styles(self):
        style = ttk.Style()
        
        # Frame styles
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabelframe', 
                       background='#1a1a2e',
                       foreground='#16213e',
                       borderwidth=2,
                       relief='solid')
        style.configure('TLabelframe.Label', 
                       font=('Roboto', 12, 'bold'), 
                       foreground='#00fff5',  # Cyan for headers
                       background='#1a1a2e',
                       padding=(10, 5))
        
        # Label styles
        style.configure('TLabel', 
                       font=('Roboto', 10),
                       foreground='#e94560',  # Bright accent color
                       background='#1a1a2e',
                       padding=2)
        style.configure('Header.TLabel',
                       font=('Roboto', 11, 'bold'),
                       foreground='#00fff5',
                       background='#1a1a2e',
                       padding=3)
        style.configure('Output.TLabel', 
                       font=('Roboto Mono', 16, 'bold'),
                       foreground='#7fff00',  # Bright green for outputs
                       background='#1a1a2e',
                       padding=5)
        
        # Button styles
        style.configure('Bit.TButton',
                       font=('Roboto Mono', 12, 'bold'),
                       padding=8,
                       width=4,
                       borderwidth=2)
        style.map('Bit.TButton',
                 background=[('active', '#e94560'), ('pressed', '#c73e54')],
                 foreground=[('active', 'white'), ('pressed', 'white')],
                 relief=[('pressed', 'sunken')])
        
        # Control button style
        style.configure('Control.TButton',
                       font=('Roboto', 10, 'bold'),
                       padding=8,
                       borderwidth=2)
        style.map('Control.TButton',
                 background=[('active', '#00fff5'), ('pressed', '#00e6dc')],
                 foreground=[('active', '#1a1a2e'), ('pressed', '#1a1a2e')],
                 relief=[('pressed', 'sunken')])
        
        # Status label style
        style.configure('Status.TLabel',
                       font=('Roboto', 10),
                       foreground='#ffd700',  # Gold for status
                       background='#1a1a2e',
                       padding=2)
        
    def create_gui(self):
        # Create main container with padding
        container = ttk.Frame(self.root, padding="25")
        container.grid(row=0, column=0, sticky="nsew")
        
        # Add gradient effect background
        canvas = tk.Canvas(container, 
                          bg='#1a1a2e',
                          highlightthickness=0,
                          width=800,
                          height=600)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create main frames with enhanced styling
        input_frame = ttk.LabelFrame(container, text="INPUTS", padding=20)
        input_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        
        output_frame = ttk.LabelFrame(container, text="OUTPUTS", padding=20)
        output_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")
        
        # Add decorative separator
        ttk.Separator(container, orient='vertical').grid(row=0, column=2, sticky='ns', padx=10)
        
        # Input A with enhanced layout
        ttk.Label(input_frame, text="A3 A2 A1 A0", style='Header.TLabel'
                ).grid(row=0, column=0, columnspan=4, pady=(0,5))
        
        # Create bit frames with enhanced styling and buttons
        for section, vars, row_start in [
            ("A", self.a_vars, 1),
            ("B", self.b_vars, 4),
            ("S", self.s_vars, 7)
        ]:
            bit_frame = ttk.Frame(input_frame)
            bit_frame.grid(row=row_start, column=0, columnspan=4, pady=5)
            
            for i in range(4):
                bit_container = ttk.Frame(bit_frame, padding=3)
                bit_container.grid(row=0, column=i, padx=8)
                
                # Initialize with binary format
                vars[i].set(self.bit_format.format(0))
                
                # Create toggle button with binary display
                btn = ttk.Button(bit_container, 
                               textvariable=vars[i],
                               command=lambda v=vars[i]: self.toggle_bit(v),
                               style='Bit.TButton')
                btn.grid(row=0, column=0, pady=2)
                
                # Add bit position label (MSB to LSB)
                ttk.Label(bit_container, 
                         text=f"{3-i}",  # This is correct as is
                         style='Header.TLabel',
                         font=('Helvetica', 8)
                         ).grid(row=1, column=0)
            
            if section != "A":
                ttk.Label(input_frame, text=f"{section}3 {section}2 {section}1 {section}0",
                         style='Header.TLabel'
                         ).grid(row=row_start-1, column=0, columnspan=4, pady=(10,5))
        
        # Enhanced control frame
        control_frame = ttk.LabelFrame(input_frame, text="CONTROL", padding=15)
        control_frame.grid(row=10, column=0, columnspan=4, pady=(15,5), sticky="ew")
        
        # Mode controls with button
        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(mode_frame, text="Mode (M):", style='Header.TLabel'
                ).grid(row=0, column=0, padx=5)
        
        mode_btn = ttk.Button(mode_frame, 
                             textvariable=self.m_var,
                             command=lambda: self.toggle_bit(self.m_var, values=['Logic (1)', 'Arithmetic (0)']),
                             width=12,
                             style='Control.TButton')
        mode_btn.grid(row=0, column=1, padx=5)
        
        # Carry controls with button
        carry_frame = ttk.Frame(control_frame)
        carry_frame.grid(row=1, column=0, padx=10, pady=5)
        ttk.Label(carry_frame, text="Carry In:", style='Header.TLabel'
                ).grid(row=0, column=0, padx=5)
        
        carry_btn = ttk.Button(carry_frame, 
                              textvariable=self.cn_var,
                              command=lambda: self.toggle_bit(self.cn_var),
                              width=3,
                              style='Control.TButton')
        carry_btn.grid(row=0, column=1, padx=5)
        
        # Enhanced output display
        result_frame = ttk.LabelFrame(output_frame, text="RESULT", padding=15)
        result_frame.grid(row=0, column=0, pady=5, sticky="ew")
        
        ttk.Label(result_frame, text="F3 F2 F1 F0", style='Header.TLabel'
                ).grid(row=0, column=0, columnspan=4, pady=10)
        
        output_display = ttk.Frame(result_frame)
        output_display.grid(row=1, column=0, columnspan=4, pady=5)
        
        for i in range(4):
            label = ttk.Label(output_display, 
                             textvariable=self.f_vars[i],
                             style='Output.TLabel',
                             width=12 if self.show_decimal.get() else 6)
            label.grid(row=0, column=i, padx=15)
        
        # Add decimal sum display after result frame
        sum_frame = ttk.LabelFrame(output_frame, text="DECIMAL", padding=15)
        sum_frame.grid(row=2, column=0, pady=(15,0), sticky="ew")
        
        ttk.Label(sum_frame, 
                 textvariable=self.decimal_sum,
                 style='Output.TLabel',
                 font=('Roboto Mono', 12, 'bold')
                 ).pack(fill="x", expand=True, padx=5, pady=5)
        
        # Enhanced status display
        status_frame = ttk.LabelFrame(output_frame, text="STATUS", padding=15)
        status_frame.grid(row=1, column=0, pady=(15,0), sticky="ew")
        
        status_items = [
            ("Carry Out (Cn+4)", self.cn4_var),
            ("Generate (G)", self.g_var),
            ("Propagate (P)", self.p_var),
            ("Equals (A=B)", self.equals_var)
        ]
        
        for i, (text, var) in enumerate(status_items):
            ttk.Label(status_frame, 
                     text=text, 
                     style='Header.TLabel'
                     ).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            ttk.Label(status_frame, 
                     textvariable=var,
                     style='Output.TLabel',
                     width=12 if self.show_decimal.get() else 6
                     ).grid(row=i, column=1, padx=10, pady=5, sticky="w")
    
    def toggle_bit(self, var, values=None):
        """Toggle between binary values with enhanced visual feedback."""
        if values is None:
            current = var.get().replace('0b', '')
            new_value = '1' if current == '0' else '0'
            var.set(self.bit_format.format(int(new_value)))
            
            # Flash effect for the button (can be implemented with after())
            self.root.after(100, lambda: self.calculate())
        else:
            current = var.get()
            var.set(values[0] if current == values[1] else values[1])
            self.calculate()
    
    def calculate(self):
        # Get input values with proper binary handling (MSB to LSB)
        a = int(''.join(var.get().replace('0b', '') for var in self.a_vars), 2)
        b = int(''.join(var.get().replace('0b', '') for var in self.b_vars), 2)
        s = int(''.join(var.get().replace('0b', '') for var in self.s_vars), 2)
        m = 1 if self.m_var.get() == 'Logic (1)' else 0
        cn = int(self.cn_var.get().replace('0b', ''))
        
        # Perform ALU operations
        if m == 1:  # Logic mode
            result = self.logic_operation(a, b, s)
            carry = 0  # Logic operations don't generate carry
        else:  # Arithmetic mode
            result, carry = self.arithmetic_operation(a, b, s, cn)  # Get both result and carry
        
        # Update outputs with binary/decimal format
        result_bin = format(result & 0xF, '04b')
        for i, bit in enumerate(result_bin):
            self.f_vars[i].set(self.format_value(format(int(bit), 'b')))
        
        # Update status outputs with format
        self.cn4_var.set(self.format_value(format(carry, 'b')))
        self.g_var.set(self.format_value(format(1 if (a & b) != 0 else 0, 'b')))
        self.p_var.set(self.format_value(format(1 if (a | b) == 0xF else 0, 'b')))
        self.equals_var.set(self.format_value(format(1 if a == b else 0, 'b')))
        
        # Update decimal sum display
        result_dec = int(result_bin, 2)
        self.decimal_sum.set(f"A:{a} B:{b} F:{result_dec}")
    
    def logic_operation(self, a, b, s):
        operations = {
            0b0000: lambda a, b: ~(a | b) & 0xF,        # NOT (A OR B)
            0b0001: lambda a, b: ~(a & b) & 0xF,        # NOT (A AND B)
            0b0010: lambda a, b: a ^ b,                 # A XOR B
            0b0011: lambda a, b: a | b,                 # A OR B
            0b0100: lambda a, b: a & b,                 # A AND B
            0b0101: lambda a, b: ~a & 0xF,              # NOT A
            0b0110: lambda a, b: ~b & 0xF,              # NOT B
            0b0111: lambda a, b: a & ~b & 0xF,          # A AND (NOT B)
            0b1000: lambda a, b: ~a & b & 0xF,          # (NOT A) AND B
            0b1001: lambda a, b: ~(a ^ b) & 0xF,        # NOT (A XOR B)
            0b1010: lambda a, b: b,                     # B
            0b1011: lambda a, b: a | ~b & 0xF,          # A OR (NOT B)
            0b1100: lambda a, b: a,                     # A
            0b1101: lambda a, b: ~a | b & 0xF,          # (NOT A) OR B
            0b1110: lambda a, b: a | b,                 # A OR B
            0b1111: lambda a, b: 0xF                    # 1's (HIGH)
        }
        return operations.get(s, lambda a, b: 0)(a, b)
    
    def arithmetic_operation(self, a, b, s, cn):
        def add_with_carry(a, b, cin):
            result = a + b + cin
            return result & 0xF, 1 if result > 0xF else 0

        def sub_with_borrow(a, b, cin):
            result = a - b - cin
            return result & 0xF, 0 if result >= 0 else 1

        operations = {
            0b0000: lambda a, b, cn: add_with_carry(a, b, cn),           # A PLUS B
            0b0001: lambda a, b, cn: sub_with_borrow(b, a, cn),          # B MINUS A
            0b0010: lambda a, b, cn: add_with_carry(a, ~b & 0xF, cn),    # A PLUS NOT B
            0b0011: lambda a, b, cn: sub_with_borrow(~b & 0xF, a, cn),   # NOT B MINUS A
            0b0100: lambda a, b, cn: add_with_carry(a, a, cn),           # A PLUS A
            0b0101: lambda a, b, cn: sub_with_borrow(a, ~a & 0xF, cn),   # A MINUS NOT A
            0b0110: lambda a, b, cn: add_with_carry(a, 1, cn),           # A PLUS 1
            0b0111: lambda a, b, cn: sub_with_borrow(a, 1, cn),          # A MINUS 1
            0b1000: lambda a, b, cn: add_with_carry(a | b, a & b, cn),   # A OR B PLUS A AND B
            0b1001: lambda a, b, cn: add_with_carry(0, a, cn),           # A
            0b1010: lambda a, b, cn: add_with_carry(a & b, ~b & 0xF, cn),# (A AND B) PLUS NOT B
            0b1011: lambda a, b, cn: sub_with_borrow(a & b, b, cn),      # (A AND B) MINUS B
            0b1100: lambda a, b, cn: add_with_carry(a, 0xF, cn),         # A PLUS ALL 1's
            0b1101: lambda a, b, cn: sub_with_borrow(a, b, cn),          # A MINUS B
            0b1110: lambda a, b, cn: add_with_carry(a, ~a & 0xF, cn),    # A PLUS NOT A
            0b1111: lambda a, b, cn: add_with_carry(a, 0, cn)            # A
        }
        
        result, carry = operations.get(s, lambda a, b, cn: (0, 0))(a, b, cn)
        
        # Update carry out
        self.cn4_var.set(self.format_value(format(carry, 'b')))
        
        # Update generate and propagate
        self.g_var.set(self.format_value(format(1 if (a & b) != 0 else 0, 'b')))
        self.p_var.set(self.format_value(format(1 if (a | b) == 0xF else 0, 'b')))
        
        return result, carry

    def create_menubar(self):
        menubar = tk.Menu(self.root, bg='#34495e', fg='white')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='white',
                          activebackground='#3498db', activeforeground='white')
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reset All", command=self.reset_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='white',
                          activebackground='#3498db', activeforeground='white')
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear A", command=lambda: self.clear_inputs('A'))
        edit_menu.add_command(label="Clear B", command=lambda: self.clear_inputs('B'))
        edit_menu.add_command(label="Clear S", command=lambda: self.clear_inputs('S'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Set A to Max", command=lambda: self.set_max('A'))
        edit_menu.add_command(label="Set B to Max", command=lambda: self.set_max('B'))
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='white',
                          activebackground='#3498db', activeforeground='white')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Decimal Values", 
                                variable=self.show_decimal,
                                command=self.update_display)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#34495e', fg='white',
                          activebackground='#3498db', activeforeground='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Datasheet", command=self.show_datasheet)
        help_menu.add_command(label="About", command=self.show_about)
    
    def reset_all(self):
        """Reset all inputs to default values"""
        for vars in [self.a_vars, self.b_vars, self.s_vars]:
            for var in vars:
                var.set(self.bit_format.format(0))
        self.m_var.set('Arithmetic (0)')
        self.cn_var.set(self.bit_format.format(0))
        self.calculate()

    def clear_inputs(self, input_type):
        """Clear specific input group"""
        vars_dict = {'A': self.a_vars, 'B': self.b_vars, 'S': self.s_vars}
        for var in vars_dict[input_type]:
            var.set(self.bit_format.format(0))
        self.calculate()

    def set_max(self, input_type):
        """Set specific input group to maximum value (1111)"""
        vars_dict = {'A': self.a_vars, 'B': self.b_vars}
        for var in vars_dict[input_type]:
            var.set(self.bit_format.format(1))
        self.calculate()

    def show_about(self):
        """Show about dialog"""
        about_text = """ALU Simulator
Version 1.0

A simulation of the  4-bit ALU
Features:
• 16 Logic Operations
• 16 Arithmetic Operations
• Real-time Calculation
• Binary/Decimal Display
• Interactive Operation Selection

Created with Python and Tkinter"""
        
        messagebox.showinfo("About ALU Simulator", about_text)

    def show_datasheet(self):
        datasheet = tk.Toplevel(self.root)
        datasheet.title("ALU Datasheet")
        datasheet.geometry("800x600")
        datasheet.configure(bg='#2c3e50')
        
        # Create a frame with scrollbar
        main_frame = ttk.Frame(datasheet, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Style the canvas
        canvas = tk.Canvas(main_frame, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def apply_operation(m, s):
            """Apply the selected operation to the current inputs"""
            # Set mode
            self.m_var.set('Logic (1)' if m == 1 else 'Arithmetic (0)')
            
            # Set S inputs
            s_bits = format(s, '04b')
            for i, bit in enumerate(s_bits):
                self.s_vars[i].set(self.bit_format.format(int(bit)))
            
            self.calculate()
            
            # Flash feedback
            datasheet.focus_set()
        
        # Modified sections list with operation tables that include apply buttons
        sections = [
            ("Description", 
             "The ALU Simulator is a 4-bit Arithmetic Logic Unit (ALU) that performs arithmetic "
             "and logic operations on two 4-bit binary words. It can perform 16 logic "
             "operations and 16 arithmetic operations based on the mode selection and "
             "function inputs. The device was widely used in early computer systems "
             "and serves as a fundamental building block for arithmetic processing units."),
            
            ("Inputs",
             "• A3-A0: First 4-bit operand (A3 is MSB)\n"
             "• B3-B0: Second 4-bit operand (B3 is MSB)\n"
             "• S3-S0: Function select inputs (determine operation)\n"
             "• M: Mode control (0=Arithmetic, 1=Logic)\n"
             "• Cn: Carry input (used in arithmetic operations)"),
            
            ("Outputs",
             "• F3-F0: 4-bit result (F3 is MSB)\n"
             "• Cn+4: Carry output for arithmetic operations\n"
             "• G: Generate signal (indicates if a carry is generated)\n"
             "• P: Propagate signal (indicates if a carry will propagate)\n"
             "• A=B: Equality indicator (high when A equals B)"),
            
            ("Logic Operations (M=1)",
             "╔═══════════════╦══════════════════════╦═══════╗\n"
             "║ S3 S2 S1 S0   ║      Operation       ║ Apply ║\n"
             "╠═══════════════╬══════════════════════╬═══════╣",
             [(0b0000, "NOT (A OR B)      "),
              (0b0001, "NOT (A AND B)     "),
              (0b0010, "A XOR B           "),
              (0b0011, "A OR B            "),
              (0b0100, "A AND B           "),
              (0b0101, "NOT A             "),
              (0b0110, "NOT B             "),
              (0b0111, "A AND (NOT B)     "),
              (0b1000, "(NOT A) AND B     "),
              (0b1001, "NOT (A XOR B)     "),
              (0b1010, "B                 "),
              (0b1011, "A OR (NOT B)      "),
              (0b1100, "A                 "),
              (0b1101, "(NOT A) OR B      "),
              (0b1110, "A OR B            "),
              (0b1111, "1                 ")]),
            
            ("Arithmetic Operations (M=0)",
             "╔═══════════════╦══════════════════════╦═══════╗\n"
             "║ S3 S2 S1 S0   ║      Operation       ║ Apply ║\n"
             "╠═══════════════╬══════════════════════╬═══════╣",
             [(0b0000, "A PLUS B          "),
              (0b0001, "B MINUS A         "),
              (0b0010, "A PLUS NOT B      "),
              (0b0011, "NOT B MINUS A     "),
              (0b0100, "A PLUS A          "),
              (0b0101, "A MINUS NOT A     "),
              (0b0110, "A PLUS 1          "),
              (0b0111, "A MINUS 1         "),
              (0b1000, "A OR B PLUS A AND B"),
              (0b1001, "A                 "),
              (0b1010, "(A AND B) PLUS NOT B"),
              (0b1011, "(A AND B) MINUS B "),
              (0b1100, "A PLUS ALL 1's    "),
              (0b1101, "A MINUS B         "),
              (0b1110, "A PLUS NOT A      "),
              (0b1111, "A                 ")]),
            
            ("Signal Details",
             "• Generate (G):\n"
             "  - Indicates when a carry is generated from the most significant bit\n"
             "  - Used in look-ahead carry generation\n\n"
             "• Propagate (P):\n"
             "  - Indicates when a carry will propagate through all bits\n"
             "  - Used with Generate for fast carry prediction\n\n"
             "• Carry Out (Cn+4):\n"
             "  - Represents overflow in arithmetic operations\n"
             "  - Used for cascading multiple ALUs\n\n"
             "• Equals (A=B):\n"
             "  - High when all bits of A match corresponding bits of B\n"
             "  - Used for comparison operations"),
            
            ("Usage Tips",
             "1. For addition operations, set M=0 and S=0000\n"
             "2. For subtraction (A-B), set M=0 and S=1101\n"
             "3. For basic logic operations:\n"
             "   - AND: M=1, S=0100\n"
             "   - OR:  M=1, S=0011\n"
             "   - XOR: M=1, S=0010\n"
             "4. Carry input (Cn) affects arithmetic operations\n"
             "5. All operations are performed on 4-bit words\n"
             "6. Results are available on F outputs immediately")
        ]
        
        # Add small button style with better positioning
        style = ttk.Style()
        style.configure('Small.TButton',
                       font=('Roboto', 8, 'bold'),
                       padding=2)
        style.map('Small.TButton',
                 background=[('active', '#00fff5'), ('pressed', '#00e6dc')],
                 foreground=[('active', '#1a1a2e'), ('pressed', '#1a1a2e')])
        
        # Modified table formatting
        table_width = 65  # Total width of the table
        
        for title, *content in sections:
            section_frame = ttk.LabelFrame(scrollable_frame, text=title, padding="15")
            section_frame.pack(fill="x", expand=True, padx=10, pady=5)
            
            if "Operations" in title:
                # Create operations table with apply buttons
                header, operations = content
                
                # Add header
                ttk.Label(section_frame, 
                         text=header,
                         font=('Courier New', 10, 'bold'),
                         justify="left").pack(fill="x", expand=True)
                
                # Create table container
                table_frame = ttk.Frame(section_frame)
                table_frame.pack(fill="x", expand=True, padx=5)
                
                # Add operations with buttons
                for s_val, op_text in operations:
                    row_frame = ttk.Frame(table_frame)
                    row_frame.pack(fill="x", expand=True, pady=1)
                    
                    # Operation text
                    s_bits = format(s_val, '04b')
                    # Pad the operation text to align buttons (reduced padding)
                    op_text_padded = op_text.ljust(18)  # Reduced from 20
                    row_text = f"║ {s_bits[0]}  {s_bits[1]}  {s_bits[2]}  {s_bits[3]}    ║ {op_text_padded}"
                    
                    # Create label container for proper alignment
                    label_frame = ttk.Frame(row_frame)
                    label_frame.pack(side="left")
                    
                    ttk.Label(label_frame,
                             text=row_text,
                             font=('Courier New', 10, 'bold'),
                             justify="left").pack(side="left")
                    
                    # Apply button with closer positioning
                    m_val = 1 if "Logic Operations" in title else 0
                    btn_frame = ttk.Frame(row_frame)
                    btn_frame.pack(side="left")  # Changed from right to left
                    
                    ttk.Button(btn_frame,
                              text="Apply",
                              style='Small.TButton',
                              width=6,
                              command=lambda m=m_val, s=s_val: apply_operation(m, s)
                              ).pack(side="left", padx=(30, 7))  # Reduced padding
                    
                    # Closing border
                    ttk.Label(btn_frame,
                             text="║",
                             font=('Courier New', 10, 'bold'),
                             justify="left").pack(side="left")
                
                # Modify the header to match the new layout
                header = header.replace("╦═══════╗", "╗")
                
                # Modify the bottom border to match the new layout
                bottom_border = "╚═══════════════╩═══════════════════════════════╝"
                
                # Add bottom border
                ttk.Label(section_frame,
                         text=bottom_border,
                         font=('Courier New', 10, 'bold'),
                         justify="left").pack(fill="x", expand=True)
                
                # Add separator after table
                ttk.Separator(section_frame, orient='horizontal'
                            ).pack(fill="x", expand=True, pady=10)
            else:
                # Regular content
                ttk.Label(section_frame,
                         text=content[0],
                         wraplength=700,
                         justify="left",
                         font=('Helvetica', 10)
                         ).pack(fill="x", expand=True, padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Make the window resizable
        datasheet.grid_rowconfigure(0, weight=1)
        datasheet.grid_columnconfigure(0, weight=1)
        
        # Center the window
        datasheet.update_idletasks()
        width = datasheet.winfo_width()
        height = datasheet.winfo_height()
        x = (datasheet.winfo_screenwidth() // 2) - (width // 2)
        y = (datasheet.winfo_screenheight() // 2) - (height // 2)
        datasheet.geometry(f'{width}x{height}+{x}+{y}')
        
        # Make the window modal
        datasheet.transient(self.root)
        datasheet.grab_set()

    def create_bit_display(self, parent, value, size=14):
        """Create an enhanced bit display frame"""
        frame = ttk.Frame(parent)
        
        # Add LED-like indicator
        led = tk.Canvas(frame, 
                       width=size, 
                       height=size, 
                       bg='#1a1a2e',
                       highlightthickness=0)
        led.create_oval(2, 2, size-2, size-2, 
                       fill='#7fff00' if value == '1' else '#333333',
                       outline='#444444')
        led.pack(side='left', padx=2)
        
        # Add value label
        ttk.Label(frame, 
                  text=value,
                  style='Output.TLabel').pack(side='left')
        
        return frame

    def flash_output(self, label, duration=100):
        """Create a flash effect for output changes"""
        original_fg = label.cget('foreground')
        label.configure(foreground='#ffffff')
        self.root.after(duration, lambda: label.configure(foreground=original_fg))

    def update_display(self):
        """Update all displays with current format"""
        self.calculate()  # This will trigger the display update

    def format_value(self, binary_str):
        """Format value according to current display settings"""
        value = int(binary_str.replace('0b', ''), 2)
        if self.show_decimal.get():
            return f"{self.bit_format.format(int(binary_str.replace('0b', '')))} ({value})"
        return self.bit_format.format(int(binary_str.replace('0b', '')))

def main():
    root = tk.Tk()
    app = ALUSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
